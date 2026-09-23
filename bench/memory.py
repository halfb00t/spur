"""The container memory ceiling, earned the way `2g` was earned.

Drives `docker compose` itself, because `mem_limit` is a container setting and must be
measured under the container's own accounting (D-17) -- on Linux/glibc, where
`malloc_trim(0)` actually does something (`_release_arenas`, `src/spur/model.py`).

`sweep` brings the service up at each of N = 1, 2, 4 build workers, drives L07's own
40-gear corpus (`bench/corpus.py`) through it, and records the peak. `confirm` re-runs
that same corpus at a candidate `mem_limit` and reports the failure count -- the bar
`2g` cleared and `1g` did not (D-18).

Not part of `make verify` (D-16): it needs a running Docker daemon and minutes. Run it
with `make bench.memory`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from bench import machine_facts
from bench.corpus import corpus

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# D-19: a fixed default, not os.cpu_count() -- a machine-dependent worker count would
# make the measured mem_limit untrue somewhere, the same reasoning L05 protects for
# parameter defaults. This is what compose.yaml ships once Plan 02-04 sets it.
SHIPPING_DEFAULT_WORKERS = 2

# docker stats' MEM USAGE column, longest suffix first -- "MiB" itself ends in "B", so
# checking "B" before "KiB"/"MiB"/"GiB" would misparse every non-byte value.
_MEM_UNITS: list[tuple[str, int]] = [
    ("GiB", 1024**3), ("MiB", 1024**2), ("KiB", 1024), ("B", 1),
]

POLL_INTERVAL = 0.5  # seconds between docker stats samples


def _parse_mem(text: str) -> int:
    """Parse a `docker stats` size like "612.3MiB" into bytes."""
    for suffix, factor in _MEM_UNITS:
        if text.endswith(suffix):
            return int(float(text[: -len(suffix)]) * factor)
    raise ValueError(f"unrecognised docker stats memory size: {text!r}")


def _wait_healthy(container: str, timeout: float = 120.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", container],
            capture_output=True, text=True, check=False,
        )
        if result.stdout.strip() == "healthy":
            return
        time.sleep(2)
    raise RuntimeError(f"{container} never reported healthy within {timeout:.0f}s")


def _poll_peak_mem(container: str, stop: threading.Event, samples: list[int]) -> None:
    """Sampled peak container memory, in bytes, appended to `samples` in place.

    Read from `docker stats --no-stream`'s MEM USAGE field, polled every
    `POLL_INTERVAL` seconds for the whole run -- this is a *sampled* peak, not the
    cgroup accounting's exact one; a spike narrower than the polling interval is
    missed, and that limitation is stated here and in `bench/README.md`. `docker stats`
    was chosen over `docker exec ... cat /sys/fs/cgroup/memory.peak` because it needs no
    shell inside the image (which runs as a non-root, `nologin` user) and its output
    format is stable across the cgroup v1/v2 split -- see 02-02-PLAN.md's flagged
    assumption 1 on container memory provenance.
    """
    while not stop.is_set():
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", container],
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            used = result.stdout.split("/")[0].strip()
            samples.append(_parse_mem(used))
        stop.wait(POLL_INTERVAL)


def _teardown(container: str) -> None:
    subprocess.run(["docker", "rm", "-f", container], capture_output=True, check=False)


def _drive_corpus(base_url: str) -> tuple[int, int]:
    """Run the full 40-gear corpus through `/api/model.stl?quality=fine`.

    Returns (request count, failure count).
    """
    requests = 0
    failures = 0
    with httpx.Client(timeout=120.0) as client:
        for gear in corpus():
            requests += 1
            # corpus() is typed `dict[str, object]` (bench/corpus.py); stringify every
            # value rather than trust its runtime type, since a query string is text
            # either way and httpx's params type only accepts known primitives.
            params = {k: str(v) for k, v in gear.items()} | {"quality": "fine"}
            try:
                response = client.get(f"{base_url}/api/model.stl", params=params)
                response.raise_for_status()
            except httpx.HTTPError:
                failures += 1
    return requests, failures


@dataclass(frozen=True)
class SweepRow:
    n: int
    peak_bytes: int | None
    requests: int
    failures: int
    elapsed_s: float
    early_peak_bytes: int | None = None  # D-11: max of the first half of samples --
    late_peak_bytes: int | None = None   # ...vs the second half. Answers "did resident
    # memory keep climbing across the corpus, or plateau" -- the question that decides
    # whether max_tasks_per_child is worth enabling. A single overall peak can't
    # distinguish "climbed once early and stayed there" from "kept climbing".
    note: str = ""


def _sweep_one(n: int, base_url: str) -> SweepRow:
    """Cold-start the service at SPUR_BUILD_WORKERS=n, drive the corpus, tear down."""
    container = f"spur-bench-n{n}"
    _teardown(container)  # a stray container from an earlier, aborted run
    try:
        subprocess.run(
            ["docker", "compose", "run", "--rm", "-d", "--name", container,
             "--service-ports", "-e", f"SPUR_BUILD_WORKERS={n}", "spur"],
            check=True, capture_output=True,
        )
        _wait_healthy(container)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"warning: N={n} never came up: {exc}", file=sys.stderr)
        _teardown(container)
        return SweepRow(n, None, 0, 0, 0.0, note=str(exc))

    stop = threading.Event()
    samples: list[int] = []
    poller = threading.Thread(target=_poll_peak_mem, args=(container, stop, samples))
    poller.start()
    t0 = time.monotonic()
    requests, failures = _drive_corpus(base_url)
    elapsed = time.monotonic() - t0
    stop.set()
    poller.join()
    _teardown(container)

    if not samples:
        print(f"warning: N={n} produced no memory samples", file=sys.stderr)
        return SweepRow(n, None, requests, failures, elapsed, note="no memory samples")
    mid = len(samples) // 2 or 1  # `or 1` guards a 1-sample run: both halves non-empty
    early_peak = max(samples[:mid])
    late_peak = max(samples[mid:]) if samples[mid:] else early_peak
    return SweepRow(n, max(samples), requests, failures, elapsed,
                     early_peak_bytes=early_peak, late_peak_bytes=late_peak)


def _sweep_table_markdown(rows: list[SweepRow]) -> str:
    lines = [
        "## Memory sweep\n",
        f"- Machine: {machine_facts()}",
        "- Peak read from: `docker stats --no-stream` MEM USAGE, polled every "
        f"{POLL_INTERVAL}s (sampled peak, not the cgroup's exact accounting)",
        "- Early/late peak: max of the first half vs second half of the corpus run's "
        "samples (D-11 drift check)",
        "",
        "| N (SPUR_BUILD_WORKERS) | Peak | Early peak | Late peak | Requests | Failures "
        "| Elapsed |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        peak = f"{row.peak_bytes / (1024**2):.1f} MiB" if row.peak_bytes is not None \
            else f"(none -- {row.note})"
        early = f"{row.early_peak_bytes / (1024**2):.1f} MiB" \
            if row.early_peak_bytes is not None else "--"
        late = f"{row.late_peak_bytes / (1024**2):.1f} MiB" \
            if row.late_peak_bytes is not None else "--"
        lines.append(f"| {row.n} | {peak} | {early} | {late} | {row.requests} "
                     f"| {row.failures} | {row.elapsed_s:.1f}s |")
    return "\n".join(lines) + "\n"


def sweep(base_url: str = DEFAULT_BASE_URL) -> bool:
    """N = 1, 2, 4: peak container memory over the 40-gear corpus, one row per N (D-18).

    Returns False if any row is incomplete (no samples, or docker never came up) -- a
    partial sweep must never be mistaken for a finished one (L08).
    """
    rows = [_sweep_one(n, base_url) for n in (1, 2, 4)]
    print(_sweep_table_markdown(rows))
    return all(row.peak_bytes is not None for row in rows)


def _write_mem_limit_override(mem_limit: str) -> str:
    """A one-line compose override file: the only way to set `mem_limit` per invocation,
    since `docker compose run` has no `--memory` flag (unlike plain `docker run`)."""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".yaml", delete=False, prefix="spur-bench-mem-limit-",
    ) as handle:
        handle.write(f"services:\n  spur:\n    mem_limit: {mem_limit}\n")
        return handle.name


def confirm(mem_limit: str, base_url: str = DEFAULT_BASE_URL,
            workers: int = SHIPPING_DEFAULT_WORKERS) -> bool:
    """Re-run the 40-gear corpus at a candidate `mem_limit`; report the failure count.

    Zero failures is the bar `2g` cleared and `1g` did not (docs/plan-2026-09-21.md) --
    this mode exists so the chosen number is confirmed rather than asserted (D-18).
    """
    container = "spur-bench-confirm"
    _teardown(container)
    override_path = _write_mem_limit_override(mem_limit)
    try:
        try:
            subprocess.run(
                ["docker", "compose", "-f", "compose.yaml", "-f", override_path, "run",
                 "--rm", "-d", "--name", container, "--service-ports",
                 "-e", f"SPUR_BUILD_WORKERS={workers}", "spur"],
                check=True, capture_output=True,
            )
        finally:
            Path(override_path).unlink(missing_ok=True)
        _wait_healthy(container)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"warning: confirm at mem_limit={mem_limit} never came up: {exc}",
              file=sys.stderr)
        _teardown(container)
        return False

    requests, failures = _drive_corpus(base_url)
    _teardown(container)
    print(f"## Memory confirm: mem_limit={mem_limit}, SPUR_BUILD_WORKERS={workers}\n\n"
          f"- Machine: {machine_facts()}\n"
          f"- Requests: {requests}, failures: {failures}\n")
    if failures:
        print(f"warning: {failures} of {requests} requests failed at "
              f"mem_limit={mem_limit}", file=sys.stderr)
    return failures == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bench.memory",
        description="Container memory sweep over L07's own 40-gear corpus (D-17, "
                     "D-18): drives docker compose itself, because mem_limit is a "
                     "container setting and must be measured under the container's "
                     "own accounting.",
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    sweep_parser = subparsers.add_parser(
        "sweep", help="N = 1, 2, 4: peak container memory over the 40-gear corpus")
    sweep_parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                               help=f"Default: {DEFAULT_BASE_URL}")

    confirm_parser = subparsers.add_parser(
        "confirm", help="Re-run the corpus at a candidate mem_limit; report failures")
    confirm_parser.add_argument("mem_limit", help="Candidate mem_limit, e.g. 2g")
    confirm_parser.add_argument("--workers", type=int, default=SHIPPING_DEFAULT_WORKERS,
                                 help=f"SPUR_BUILD_WORKERS. Default: "
                                      f"{SHIPPING_DEFAULT_WORKERS}")
    confirm_parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                                 help=f"Default: {DEFAULT_BASE_URL}")

    args = parser.parse_args(argv)
    if args.mode == "sweep":
        return 0 if sweep(args.base_url) else 1
    return 0 if confirm(args.mem_limit, args.base_url, args.workers) else 1


if __name__ == "__main__":
    sys.exit(main())
