"""Own-process `/api/health` poller (D-01).

Runs as a genuinely separate OS process, not a thread inside `run_experiment.py`,
because the question this investigation re-checks (H1, `02-LATENCY-INVESTIGATION.md`
"## Method": does the health poller sharing a process and a GIL with the build threads
explain the under-load p95 ratio?) can only be answered by a poller that has its own
interpreter and its own GIL. A thread would reintroduce exactly the confound H1 tests.

Every sample is stamped with `time.monotonic()`, not `time.perf_counter()`: on this host
both read `mach_absolute_time()` at the same declared resolution (confirmed in planning
via `time.get_clock_info`), but `monotonic()` is the clock 02's own investigation used to
compare timestamps across two independent processes with no clock-sync step --
`perf_counter()`'s cross-process comparability is not guaranteed by its own
documentation, only observed to agree here.

Every sample is written to `--out` and flushed as it is taken (line-buffered), never
batched to the end: an orphaned poller -- 02's own try/finally lesson, a crashed parent
that never writes `--stop-file` -- still leaves honest, readable partial data instead of
nothing or a half-written line.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="poller",
        description="Sample /api/health in its own OS process until --stop-file appears.")
    parser.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:8001")
    parser.add_argument("--out", required=True, type=Path, help="JSONL output path")
    parser.add_argument("--stop-file", required=True, type=Path,
                         help="Checked after every sample; the loop exits once it exists")
    args = parser.parse_args(argv)

    if args.out.exists():
        print(f"error: --out {args.out} already exists -- refusing to append to or "
              f"overwrite a stale path (02's corrupted-JSONL lesson: two processes "
              f"writing the same file corrupts it)", file=sys.stderr)
        return 2

    # `with` on both the client and the file gives the same always-closed guarantee as
    # an explicit try/finally, including when client.get() raises on a connection error
    # (it is never caught here -- a dead server is a real failure, not a sample, D-01).
    with httpx.Client() as client, args.out.open("w", buffering=1) as out:
        while True:  # do-while: the first sample happens before the first stop check
            t = time.monotonic()
            t0 = time.perf_counter()
            client.get(f"{args.base_url}/api/health", timeout=30.0)
            latency_s = time.perf_counter() - t0
            out.write(json.dumps({"t": t, "latency_s": latency_s}) + "\n")
            if args.stop_file.exists():
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
