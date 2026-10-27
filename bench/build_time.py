"""Per-parameter-set build, fine-STL and STEP export time, against `SPUR_BUILD_TIMEOUT`.

Measures, per set, build wall time with the solid cache cleared, fine-STL export time and
STEP export time, in-process, through the same `spur.model` code a worker runs. Not part
of `make verify`: a sweep at 200 teeth takes about a minute and a half, and a timing
assertion on shared hardware would flap (the bench package's D-16 stance,
`bench/latency.py`'s docstring). Run it with `make bench.build`, or `make bench.build
SWEEP=bench/sweeps/<name>.json`. Phases 9-12 add their own sweep file and run this script
unchanged (08-CONTEXT.md D-12). Phase 12 (D-16) adds two columns: every row's fine-STL
byte count and triangle count, so "the heaviest v0.2 face topology" 12-04 re-measures L19
and L24 on is chosen by a number, not by inspection. The columns print for every sweep
file from here on; earlier `bench/RESULTS.md` sections are not back-filled.

Phase 32 adds shaft rows and `--fresh`. A row carrying `"part": "shaft"` is a `ShaftParams`
(a row without `part` stays a `GearParams`, so every earlier sweep file loads unchanged),
and `--fresh` times each row in its own child process, one at a time in file order, so the
row's peak RSS is its own: in one process `ru_maxrss` is the peak of every row so far, and a
per-row figure read from it would be a plausible wrong number (L08).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import TypedDict

from pydantic import ValidationError

from bench import machine_facts, maxrss_bytes
from spur import int_env, model
from spur.params import GearParams
from spur.parts import Part
from spur.shaft_params import ShaftParams

DEFAULT_SWEEP = Path(__file__).parent / "sweeps" / "hex_bore.json"


@dataclass(frozen=True)
class Timing:
    label: str
    build: float
    stl: float
    step: float
    stl_bytes: int
    stl_triangles: int
    # No defaults on the two fields above: a default 0 would be a plausible-looking
    # fake STL size for a row nobody actually measured (L08).
    # None is "not measured": in one process ru_maxrss is the peak of every row so far,
    # and printing it per row would be a plausible wrong number (L08). Only a `--fresh`
    # child fills them; resident is None on a host with no /proc/self/status (macOS).
    peak_rss_bytes: int | None = None
    resident_bytes: int | None = None

    @property
    def worst_request(self) -> float:
        """The number `SPUR_BUILD_TIMEOUT` must fit.

        `SPUR_BUILD_TIMEOUT` wraps one worker call (`spur.pool.build_export`), and a
        cold request builds once and then exports once -- so build plus the slower of
        the two exports is what a real request pays, not build plus both exports.
        """
        return self.build + max(self.stl, self.step)

    def inside(self, timeout: float) -> bool:
        return self.worst_request <= timeout


def load_sweep(path: Path) -> list[tuple[str, Part]]:
    """Read a JSON list of shareable-link parameter sets, each validated into a part. The
    label is the set's own `key=value` pairs, in file order, `part` included.

    A row without `part` validates as a `GearParams`, `"part": "shaft"` as a `ShaftParams`
    on its other keys; any other value is refused. A set that fails validation (including
    `check()`'s refusals, run by each model's own `_feasible` validator) cannot be timed and
    must not be silently skipped -- raise instead, naming the set and the file.
    """
    raw: list[dict[str, object]] = json.loads(path.read_text())
    sets: list[tuple[str, Part]] = []
    for i, obj in enumerate(raw):
        label = " ".join(f"{k}={v}" for k, v in obj.items())
        fields = {k: v for k, v in obj.items() if k != "part"}
        kind = obj.get("part", "gear")
        p: Part
        try:
            if kind == "gear" and "part" not in obj:
                p = GearParams.model_validate(fields)
            elif kind == "shaft":
                p = ShaftParams.model_validate(fields)
            else:
                raise ValueError(
                    f"{path} set {i} ({label}) names an unknown part {kind!r}; "
                    "a row has no `part` (a gear) or \"part\": \"shaft\"")
        except ValidationError as exc:
            what = "shaft" if kind == "shaft" else "gear"
            raise ValueError(
                f"{path} set {i} ({label}) is not a buildable {what}: {exc}") from exc
        sets.append((label, p))
    return sets


def stl_size(data: bytes) -> tuple[int, int]:
    """(byte count, triangle count) of a binary STL -- the triangle count read straight
    from the header's own 4-byte little-endian uint32 at bytes 80-84 (O(1); RESEARCH.md
    "Don't Hand-Roll": the count is already in the header, walking every facet with
    `test_model.py`'s `_stl_triangles` is for content proofs, not counting).

    Raises when the length disagrees with `84 + 50 * n`: a truncated file, or an ASCII
    STL that happens to carry 80 header-like bytes, would otherwise hand back a
    plausible-looking but wrong count (L08) -- exactly the failure a slicer needs a
    watertight, correctly-sized mesh to avoid.
    """
    n = int.from_bytes(data[80:84], "little")
    expected = 84 + 50 * n
    if len(data) != expected:
        raise ValueError(
            f"STL is {len(data)} bytes but its header's triangle count ({n}) implies "
            f"{expected} bytes -- truncated file or not a binary STL, refusing to "
            "report a triangle count that would be a plausible wrong number")
    return len(data), n


def time_set(p: Part) -> tuple[float, float, float, int, int]:
    """Build wall time (cold solid cache), fine-STL export time, STEP export time, and
    the fine STL's byte count and triangle count (D-16). The size is read from the
    already-exported bytes after `stl_s` is taken, so it does not inflate the timed
    export region."""
    model._build_cached.cache_clear()
    t0 = time.perf_counter()
    model.build(p)
    build_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    data = model.export(p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model.export(p, "step")
    step_s = time.perf_counter() - t0
    stl_bytes, stl_triangles = stl_size(data)
    return build_s, stl_s, step_s, stl_bytes, stl_triangles


class _ChildPayload(TypedDict):
    """The one JSON line a `--child-row` process prints: the wire shape between
    `_time_fresh` and `_run_child`, typed so the parent reads it without an `Any`."""

    build: float
    stl: float
    step: float
    stl_bytes: int
    stl_triangles: int
    peak_rss_bytes: int
    resident_bytes: int | None


def _vmrss_bytes(status: str) -> int | None:
    """The `VmRSS:` line of /proc/self/status in bytes (the file counts kB), None without
    one -- "not measured", never a zero."""
    for line in status.splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) * 1024
    return None


def _run_child(sweep: Path, index: int) -> int:
    """`--child-row i`: time row `i` of `sweep` in this fresh process, then print one JSON
    line holding the times, the STL size, this process's own peak RSS and, where Linux
    offers it, the resident memory at the end (after the build and both exports, the solid
    still cached). Nothing else goes to stdout."""
    _, p = load_sweep(sweep)[index]
    build_s, stl_s, step_s, stl_bytes, stl_triangles = time_set(p)
    peak = maxrss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        platform.system())
    status = Path("/proc/self/status")
    resident = _vmrss_bytes(status.read_text()) if status.exists() else None
    payload: _ChildPayload = {
        "build": build_s, "stl": stl_s, "step": step_s, "stl_bytes": stl_bytes,
        "stl_triangles": stl_triangles, "peak_rss_bytes": peak,
        "resident_bytes": resident,
    }
    print(json.dumps(payload))
    return 0


def _time_fresh(sweep: Path, labels: list[str]) -> list[Timing]:
    """Every row in its own process, one at a time in file order (a concurrent child
    would share the CPUs and the memory bus the next row is timed on)."""
    timings: list[Timing] = []
    for i, label in enumerate(labels):
        out = subprocess.run(
            [sys.executable, "-m", "bench.build_time", str(sweep), "--child-row", str(i)],
            capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()[-1]
        child: _ChildPayload = json.loads(out)
        timings.append(Timing(label, child["build"], child["stl"], child["step"],
                              child["stl_bytes"], child["stl_triangles"],
                              child["peak_rss_bytes"], child["resident_bytes"]))
    return timings


def report(path: Path, timings: list[Timing], timeout: int,
           load: tuple[float, float, float]) -> str:
    if not timings:
        raise ValueError(
            f"{path} produced no timings -- an empty sweep must be refused loudly, "
            "never printed as an empty table that reads as a pass")
    versions = ", ".join(f"{dist} {metadata.version(dist)}"
                          for dist in ("cadquery", "cadquery-ocp"))
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    # `load` is read by the caller before the first row builds (12-03 fix): a sweep at
    # 200 teeth runs 6-7 minutes, and a reading taken here -- after every row already
    # built -- made the "at start" label false (bench/RESULTS.md "Composed build and
    # export time (Phase 12)" intro; 12-02-SUMMARY.md documented the mismeasurement).
    load1, load5, load15 = load
    with_memory = [t.peak_rss_bytes is not None for t in timings]
    if any(with_memory) and not all(with_memory):
        raise ValueError(
            f"{path}: some rows have a peak RSS and some do not -- a report mixes rows "
            "from one process with rows from their own, and the first group's peaks are "
            "cumulative, not theirs (L08)")
    fresh = all(with_memory)
    lines = [
        f"- Machine: {machine_facts()}",
        f"- Python: {platform.python_version()}",
        f"- Kernel: {versions}",
        f"- HEAD: `{head}`",
        f"- Sweep: `{path}`",
        f"- Load averages at start: {load1:.2f}, {load5:.2f}, {load15:.2f}",
        f"- SPUR_BUILD_TIMEOUT: {timeout} s, a cold request is one build plus one export",
        "",
        "| Parameter set | Build (s) | Fine STL (s) | STEP (s) | "
        f"Build + slower export (s) | Inside {timeout} s | Fine STL (bytes) | Triangles |"
        + (" Peak RSS (MiB) | Resident after build (MiB) |" if fresh else ""),
        "|---|---|---|---|---|---|---|---|" + ("---|---|" if fresh else ""),
    ]
    for t in timings:
        verdict = "yes" if t.inside(timeout) else "**NO**"
        row = (f"| {t.label} | {t.build:.2f} | {t.stl:.2f} | {t.step:.2f} | "
               f"{t.worst_request:.2f} | {verdict} | {t.stl_bytes} | "
               f"{t.stl_triangles} |")
        if fresh:
            assert t.peak_rss_bytes is not None
            resident = "-" if t.resident_bytes is None else f"{t.resident_bytes / 1048576:.0f}"
            row += f" {t.peak_rss_bytes / 1048576:.0f} | {resident} |"
        lines.append(row)
    heaviest = max(timings, key=lambda t: t.worst_request)
    lines.append("")
    lines.append(f"**Heaviest:** {heaviest.label} -- {heaviest.worst_request:.2f} s "
                 f"of {timeout} s.")
    largest = max(timings, key=lambda t: t.stl_bytes)
    lines.append(f"**Largest fine STL:** {largest.label} -- {largest.stl_bytes} bytes, "
                 f"{largest.stl_triangles} triangles.")
    if fresh:
        # file order breaks a tie, as max() does for the two lines above
        top = max(timings, key=lambda t: t.peak_rss_bytes or 0)
        assert top.peak_rss_bytes is not None
        lines.append(f"**Highest peak RSS:** {top.label} -- "
                     f"{top.peak_rss_bytes / 1048576:.0f} MiB.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bench.build_time",
        description="Time build, fine-STL and STEP export per parameter set, against "
                     "SPUR_BUILD_TIMEOUT.",
    )
    parser.add_argument(
        "sweep", nargs="?", type=Path, default=DEFAULT_SWEEP,
        help=f"JSON sweep file of shareable-link parameter sets. Default: {DEFAULT_SWEEP}.")
    parser.add_argument(
        "--timeout", type=int, default=int_env("SPUR_BUILD_TIMEOUT", 30),
        help="Seconds a build plus its slower export must fit -- the same knob and "
             "default app.py's lifespan passes to BuildPool.")
    parser.add_argument(
        "--fresh", action="store_true",
        help="Each row in its own process, so its peak RSS is its own.")
    parser.add_argument("--child-row", type=int, default=None,
                        help=argparse.SUPPRESS)  # internal: see _time_fresh
    args = parser.parse_args(argv)

    if args.child_row is not None:
        return _run_child(args.sweep, args.child_row)

    sets = load_sweep(args.sweep)  # fails before any build if a set is not buildable

    # Read before the first row builds, not after the sweep finishes (12-03 fix): a
    # sweep at 200 teeth runs 6-7 minutes, so a reading taken after the loop was really
    # an end-of-run figure printed under an "at start" label.
    load = os.getloadavg()

    # Time every set before deciding the exit code -- a short-circuiting generator
    # would silently skip the rest (bench/latency.py's own rule).
    if args.fresh:
        timings = _time_fresh(args.sweep, [label for label, _ in sets])
    else:
        timings = [Timing(label, *time_set(p)) for label, p in sets]

    print(report(args.sweep, timings, args.timeout, load))

    over_budget = [t for t in timings if not t.inside(args.timeout)]
    for t in over_budget:
        print(f"warning: {t.label} is over budget: {t.worst_request:.2f} s of "
              f"{args.timeout} s", file=sys.stderr)
    return 1 if over_budget else 0


if __name__ == "__main__":
    sys.exit(main())
