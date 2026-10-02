"""One run: `poller.py` beside an in-process mirror of `bench.latency`'s own scenarios.

Lives outside the `spur`/`bench` packages (D-03 -- SC1 forbids a `bench/` change for the
investigation), so it needs the `sys.path.insert` dance before it can `from bench.latency
import ...` -- 02's own approach, confirmed in planning as the only way to reuse the
harness's sampling functions unmodified without a `bench/` edit.

Every sampling function below (`_sample_for`, `_sample_while_building`, `_build`,
`_collect`, `_p95`) is imported from `bench.latency`, never reimplemented -- the rule
02's own write-up states and this phase's CONTEXT.md repeats explicitly (D-04 "Claude's
Discretion", Flagged Assumption A2). `concurrent_run`/`single_run` below are line-for-line
copies of `scenario_concurrent`/`scenario_single`'s *bodies* (bench/latency.py:135-146,
123-132) with three `time.monotonic()` stamps added for the poller/in-process
segmentation (E2) -- the copy exists only because `scenario_concurrent` hardcodes
`range(190, 200)` and Pair B needs `range(180, 190)`, which cannot be expressed without
either a `bench/` change or this mirror (A2).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import httpx

# This file sits at <repo>/.planning/phases/13-latency-bar/investigation/run_experiment.py
# -- four directories below the repository root.
REPO_ROOT = Path(__file__).resolve().parents[4]
POLLER_PATH = Path(__file__).resolve().parent / "poller.py"

sys.path.insert(0, str(REPO_ROOT))

from bench import machine_facts  # noqa: E402
from bench.latency import (  # noqa: E402
    MIN_SAMPLES,
    SETTLE_SECONDS,
    ComposedRun,
    ScenarioResult,
    _build,
    _collect,
    _composed_markdown,
    _p95,
    _report_markdown,
    _sample_for,
    _sample_while_building,
    run_composed,
)

_KNOWN_SCENARIOS = ("concurrent", "single", "composed")


def concurrent_run(base_url: str, teeth_start: int) -> tuple[ScenarioResult, float, float, float]:
    """Line-for-line copy of `scenario_concurrent`'s body (bench/latency.py:135-146),
    `range(teeth_start, teeth_start + 10)` in place of the hardcoded `range(190, 200)`
    (A2 -- Pair B's teeth 180-189 cannot fire through the real `scenario_concurrent`
    without a `bench/` change), plus three `time.monotonic()` stamps for E2's
    idle/under-load segmentation of the poller's independently-timestamped samples.
    """
    with httpx.Client() as client:
        t_start = time.monotonic()
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        t_builds_start = time.monotonic()
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(_build, base_url, client, teeth, "fine")
                       for teeth in range(teeth_start, teeth_start + 10)]
            under_load = _sample_while_building(base_url, client, futures)
        t_builds_done = time.monotonic()
        slowest, attempted, refused = _collect(futures)
    result = ScenarioResult("concurrent", idle, under_load, slowest, attempted, refused)
    return result, t_start, t_builds_start, t_builds_done


def single_run(base_url: str) -> tuple[ScenarioResult, float, float, float]:
    """Line-for-line copy of `scenario_single`'s body (bench/latency.py:123-132), plus
    the same three `time.monotonic()` stamps `concurrent_run` adds."""
    with httpx.Client() as client:
        t_start = time.monotonic()
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        t_builds_start = time.monotonic()
        with ThreadPoolExecutor(max_workers=1) as pool:
            futures = [pool.submit(_build, base_url, client, 200, "fine")]
            under_load = _sample_while_building(base_url, client, futures)
        t_builds_done = time.monotonic()
        slowest, attempted, refused = _collect(futures)
    result = ScenarioResult("single", idle, under_load, slowest, attempted, refused)
    return result, t_start, t_builds_start, t_builds_done


def composed_run(base_url: str) -> tuple[ScenarioResult, float, float, float, ComposedRun]:
    """Calls `bench.latency.run_composed` unmodified -- unlike `concurrent_run`/
    `single_run` (A2), there is no hardcoded teeth range to work around here, so this is
    a call, not a copy. `t_start` is stamped immediately before the call; `run_composed`
    already stamps every one of its ten requests (`RequestOutcome.sent`/`.done`), so
    `t_builds_start`/`t_builds_done` are the earliest `sent` and latest `done` among
    them -- the composed scenario's own equivalent of the other two legs' three manual
    `time.monotonic()` calls.
    """
    t_start = time.monotonic()
    run = run_composed(base_url)
    t_builds_start = min(r.sent for r in run.requests)
    t_builds_done = max(r.done for r in run.requests)
    return run.result, t_start, t_builds_start, t_builds_done, run


def series_stats(samples: list[float]) -> dict[str, object]:
    """One series' full stats, recomputed from raw samples, never from a print format
    (D-02). `p95_s` is null below `MIN_SAMPLES` (L08 -- a percentile over fewer samples
    than `statistics.quantiles`' own bucket count is a guess); `p94_s`/`p96_s` are null
    below 100 samples, the same rule applied to a 100-bucket call (E1). `min_gap_s` and
    `ties` feed the floor analysis (D-02, E2 -- ties are counted, never de-duplicated).
    """
    n = len(samples)
    stats: dict[str, object] = {"n": n}

    if n < MIN_SAMPLES:
        stats["p95_s"] = None
        stats["refused_reason"] = (
            f"only {n} /api/health samples (need >= {MIN_SAMPLES}); "
            f"refusing to report a p95")
    else:
        stats["p95_s"] = _p95(samples)
        stats["refused_reason"] = None

    if n < 100:
        stats["p94_s"] = None
        stats["p96_s"] = None
    else:
        quantiles = statistics.quantiles(samples, n=100)
        p95_recompute = quantiles[94]
        # The n=20 and n=100 statistics.quantiles() calls round differently -- isclose,
        # not ==, proves the 100-bucket call is the same percentile method, not a second
        # one that happens to agree (E1).
        assert math.isclose(p95_recompute, stats["p95_s"], rel_tol=1e-12)
        stats["p94_s"] = quantiles[93]
        stats["p96_s"] = quantiles[95]

    distinct = sorted(set(samples))
    if len(distinct) < 2:
        stats["min_gap_s"] = None
    else:
        stats["min_gap_s"] = min(b - a for a, b in pairwise(distinct))
    stats["ties"] = n - len(distinct)
    return stats


def ratio_block(idle: dict[str, object], under_load: dict[str, object]) -> dict[str, object]:
    """The verdict and its four one-percentile alternatives, all decided on raw floats
    (E6, D-02): `bench.latency._report_markdown` prints p95 at `:.1f` ms but computes its
    ratio on the raw float -- this is the one place that print-format floor is checked
    against the data instead of assumed. `flips` is true when any alternative lands on
    the other side of 2.0 from `ratio` -- the floor-analysis question, not a verdict.
    """

    def ratio_of(num: object, den: object) -> float | None:
        if num is None or den is None:
            return None
        return float(num) / float(den)  # type: ignore[arg-type]

    ratio = ratio_of(under_load["p95_s"], idle["p95_s"])
    alternatives = {
        "u94_i95": ratio_of(under_load["p94_s"], idle["p95_s"]),
        "u96_i95": ratio_of(under_load["p96_s"], idle["p95_s"]),
        "u95_i94": ratio_of(under_load["p95_s"], idle["p94_s"]),
        "u95_i96": ratio_of(under_load["p95_s"], idle["p96_s"]),
    }
    verdict = None if ratio is None else ("pass" if ratio <= 2.0 else "miss")
    alt_values = [v for v in alternatives.values() if v is not None]
    if ratio is None or not alt_values:
        flips = None
    else:
        pass_side = ratio <= 2.0
        flips = any((v <= 2.0) != pass_side for v in alt_values)
    return {"ratio": ratio, "verdict": verdict, "alternatives": alternatives, "flips": flips}


def _label(text: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9-]+", text):
        raise argparse.ArgumentTypeError(
            f"--label must be letters, digits and hyphens only (got {text!r})")
    return text


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_experiment",
        description="One run: poller.py beside bench.latency's own sampling functions, "
                     "imported unmodified (D-04).")
    parser.add_argument("--label", required=True, type=_label)
    parser.add_argument(
        "--base-url", required=True,
        help="No default -- the port-8001 trap (RESEARCH.md Pitfall 1) must never "
             "recur silently.")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--order", default="concurrent,single",
        help="Comma-separated scenario names, run order. Default matches "
             "bench.latency.main()'s own sorted() order with no scenario argument (A1).")
    parser.add_argument("--teeth-start", type=int, default=190)
    return parser


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True,
        text=True, check=True).stdout.strip()


def _wait_for_poller(poller_jsonl: Path, timeout_s: float = 10.0) -> bool:
    """Bounded wait for the poller's first flushed line, so a poller that never starts
    sampling cannot silently run the rest of the experiment unmeasured."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if poller_jsonl.exists() and poller_jsonl.stat().st_size > 0:
            return True
        time.sleep(0.1)
    return False


def _print_report_or_refusal(name: str, idle_stats: dict[str, object],
                              under_stats: dict[str, object], result: ScenarioResult) -> None:
    """Print `_report_markdown`'s own format exactly as `bench.latency._run_scenario`
    would, or -- when a series is under `MIN_SAMPLES` -- the harness's refusal warning
    (L08: a refused series never gets a printed number)."""
    if idle_stats["p95_s"] is not None and under_stats["p95_s"] is not None:
        print(_report_markdown(
            name, idle_stats["p95_s"], idle_stats["n"], under_stats["p95_s"],
            under_stats["n"], result.slowest_build, result.attempted, result.refused))
        return
    if idle_stats["p95_s"] is None:
        print(f"warning: {name}/idle {idle_stats['refused_reason']}", file=sys.stderr)
    if under_stats["p95_s"] is None:
        print(f"warning: {name}/under_load {under_stats['refused_reason']}", file=sys.stderr)


def _segment_poller_samples(poller_samples: list[dict[str, float]], order: list[str],
                             scenarios: dict[str, dict[str, object]]) -> int:
    """Segment the poller's own JSONL by each scenario's monotonic window (E2): idle is
    `t_start <= t < t_builds_start`, under-load is `t_builds_start <= t <= t_builds_done`.
    Samples outside every scenario's window are unassigned, never guessed into a bucket.
    """
    assigned = 0
    for name in order:
        sdata = scenarios[name]
        t_start = sdata["t_start"]
        t_builds_start = sdata["t_builds_start"]
        t_builds_done = sdata["t_builds_done"]
        idle = [s["latency_s"] for s in poller_samples if t_start <= s["t"] < t_builds_start]
        under = [s["latency_s"] for s in poller_samples
                 if t_builds_start <= s["t"] <= t_builds_done]
        assigned += len(idle) + len(under)
        idle_stats = series_stats(idle)
        under_stats = series_stats(under)
        sdata["poller"] = {"idle": idle_stats, "under_load": under_stats,
                            **ratio_block(idle_stats, under_stats)}
    return len(poller_samples) - assigned


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    order = [name.strip() for name in args.order.split(",") if name.strip()]
    unknown = [name for name in order if name not in _KNOWN_SCENARIOS]
    if unknown:
        print(f"error: --order names unknown scenarios: {unknown}", file=sys.stderr)
        return 2

    out_dir: Path = args.out_dir
    poller_jsonl = out_dir / f"{args.label}.poller.jsonl"
    inproc_jsonl = out_dir / f"{args.label}.inproc.jsonl"
    summary_json = out_dir / f"{args.label}.summary.json"
    stop_file = out_dir / f"{args.label}.stop"
    existing = [p for p in (poller_jsonl, inproc_jsonl, summary_json) if p.exists()]
    if existing:
        print(f"error: refusing to overwrite existing output: {existing}", file=sys.stderr)
        return 2

    started_utc = datetime.now(UTC).isoformat()
    head = _git_head()
    machine = machine_facts()

    poller_proc = subprocess.Popen(
        [sys.executable, str(POLLER_PATH), "--base-url", args.base_url,
         "--out", str(poller_jsonl), "--stop-file", str(stop_file)])
    if not _wait_for_poller(poller_jsonl):
        poller_proc.terminate()
        poller_proc.wait(timeout=5)
        print("error: poller produced no samples within 10s", file=sys.stderr)
        return 1

    scenarios: dict[str, dict[str, object]] = {}
    inproc_lines: list[dict[str, object]] = []
    try:
        for name in order:
            composed: ComposedRun | None = None
            if name == "concurrent":
                result, t_start, t_builds_start, t_builds_done = concurrent_run(
                    args.base_url, args.teeth_start)
                teeth: list[int] | None = [args.teeth_start, args.teeth_start + 9]
            elif name == "composed":
                result, t_start, t_builds_start, t_builds_done, composed = composed_run(
                    args.base_url)
                teeth = None
                # `scenario_composed` prints `_composed_markdown` before `_run_scenario`
                # prints `_report_markdown` below -- the same order a real
                # `python -m bench.latency composed` run produces.
                print(_composed_markdown(composed))
            else:
                result, t_start, t_builds_start, t_builds_done = single_run(args.base_url)
                teeth = None
            idle_stats = series_stats(result.idle)
            under_stats = series_stats(result.under_load)
            _print_report_or_refusal(name, idle_stats, under_stats, result)
            inproc_lines.append({"scenario": name, "series": "idle", "latency_s": result.idle})
            inproc_lines.append(
                {"scenario": name, "series": "under_load", "latency_s": result.under_load})
            scenario_entry: dict[str, object] = {
                "t_start": t_start,
                "t_builds_start": t_builds_start,
                "t_builds_done": t_builds_done,
                "slowest_build_s": result.slowest_build,
                "attempted": result.attempted,
                "refused": result.refused,
                "teeth": teeth,
                "inproc": {"idle": idle_stats, "under_load": under_stats,
                           **ratio_block(idle_stats, under_stats)},
            }
            if composed is not None:
                scenario_entry["requests"] = [
                    {"params": r.params, "status": r.status, "wall_s": r.wall_s}
                    for r in composed.requests
                ]
                scenario_entry["workers_replaced"] = {
                    "before": composed.workers_replaced_before,
                    "after": composed.workers_replaced_after,
                }
            scenarios[name] = scenario_entry
    finally:
        # The stop-file-then-wait-then-kill shape is 02's own try/finally lesson: the
        # poller must be stopped even when a scenario above raises.
        stop_file.touch()
        try:
            poller_proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            poller_proc.kill()
            poller_proc.wait()
        stop_file.unlink(missing_ok=True)

    if poller_proc.returncode != 0:
        print(f"error: poller exited {poller_proc.returncode}", file=sys.stderr)
        return 1

    poller_samples = [json.loads(line) for line in poller_jsonl.read_text().splitlines()]
    unassigned = _segment_poller_samples(poller_samples, order, scenarios)

    with inproc_jsonl.open("w") as f:
        for line in inproc_lines:
            f.write(json.dumps(line) + "\n")

    summary = {
        "label": args.label,
        "started_utc": started_utc,
        "finished_utc": datetime.now(UTC).isoformat(),
        "head": head,
        "machine": machine,
        "base_url": args.base_url,
        "order": order,
        "teeth_start": args.teeth_start,
        "clock_resolution_s": time.get_clock_info("perf_counter").resolution,
        "poller": {
            "n": len(poller_samples),
            "returncode": poller_proc.returncode,
            "unassigned": unassigned,
        },
        "scenarios": scenarios,
    }
    summary_json.write_text(json.dumps(summary, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
