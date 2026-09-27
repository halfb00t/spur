"""Per-parameter-set build, fine-STL and STEP export time, against `SPUR_BUILD_TIMEOUT`.

Measures, per set, build wall time with the solid cache cleared, fine-STL export time and
STEP export time, in-process, through the same `spur.model` code a worker runs. Not part
of `make verify`: a sweep at 200 teeth takes about a minute and a half, and a timing
assertion on shared hardware would flap (the bench package's D-16 stance,
`bench/latency.py`'s docstring). Run it with `make bench.build`, or `make bench.build
SWEEP=bench/sweeps/<name>.json`. Phases 9-12 add their own sweep file and run this script
unchanged (08-CONTEXT.md D-12).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from pydantic import ValidationError

from bench import machine_facts
from spur import int_env, model
from spur.params import GearParams

DEFAULT_SWEEP = Path(__file__).parent / "sweeps" / "hex_bore.json"


@dataclass(frozen=True)
class Timing:
    label: str
    build: float
    stl: float
    step: float

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


def load_sweep(path: Path) -> list[tuple[str, GearParams]]:
    """Read a JSON list of shareable-link parameter sets, each validated into a
    `GearParams`. Label is the set's own `key=value` pairs, in file order.

    A set that fails validation (including `check()`'s refusals, run by `GearParams`'s
    own `_feasible` validator) cannot be timed and must not be silently skipped -- raise
    instead, naming the set and the file.
    """
    raw: list[dict[str, object]] = json.loads(path.read_text())
    sets: list[tuple[str, GearParams]] = []
    for i, obj in enumerate(raw):
        label = " ".join(f"{k}={v}" for k, v in obj.items())
        try:
            p = GearParams.model_validate(obj)
        except ValidationError as exc:
            raise ValueError(
                f"{path} set {i} ({label}) is not a buildable gear: {exc}") from exc
        sets.append((label, p))
    return sets


def time_set(p: GearParams) -> tuple[float, float, float]:
    """Build wall time (cold solid cache), fine-STL export time, STEP export time."""
    model._build_cached.cache_clear()
    t0 = time.perf_counter()
    model.build(p)
    build_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model.export(p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model.export(p, "step")
    step_s = time.perf_counter() - t0
    return build_s, stl_s, step_s


def report(path: Path, timings: list[Timing], timeout: int) -> str:
    versions = ", ".join(f"{dist} {metadata.version(dist)}"
                          for dist in ("cadquery", "cadquery-ocp"))
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    load1, load5, load15 = os.getloadavg()
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
        f"Build + slower export (s) | Inside {timeout} s |",
        "|---|---|---|---|---|---|",
    ]
    for t in timings:
        verdict = "yes" if t.inside(timeout) else "**NO**"
        lines.append(f"| {t.label} | {t.build:.2f} | {t.stl:.2f} | {t.step:.2f} | "
                      f"{t.worst_request:.2f} | {verdict} |")
    heaviest = max(timings, key=lambda t: t.worst_request)
    lines.append("")
    lines.append(f"**Heaviest:** {heaviest.label} -- {heaviest.worst_request:.2f} s "
                 f"of {timeout} s.")
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
    args = parser.parse_args(argv)

    sets = load_sweep(args.sweep)  # fails before any build if a set is not buildable

    # Time every set before deciding the exit code -- a short-circuiting generator
    # would silently skip the rest (bench/latency.py's own rule).
    timings = [Timing(label, *time_set(p)) for label, p in sets]

    print(report(args.sweep, timings, args.timeout))

    over_budget = [t for t in timings if not t.inside(args.timeout)]
    for t in over_budget:
        print(f"warning: {t.label} is over budget: {t.worst_request:.2f} s of "
              f"{args.timeout} s", file=sys.stderr)
    return 1 if over_budget else 0


if __name__ == "__main__":
    sys.exit(main())
