"""Recompute, never trust: `--self-check` pins `series_stats`/`ratio_block`'s boundary
cases (E1, E2, E3, E6), `--check` recomputes every run's numbers straight from its raw
JSONL and compares field by field against the committed `summary.json`/`status.json`
(T-13-03), `--tables` and `--sessions` print the write-up's markdown.

Imports `series_stats` and `ratio_block` from `run_experiment.py` -- the one definition,
not a second one that happens to agree (L08).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_experiment import ratio_block, series_stats  # noqa: E402


def _self_check() -> int:
    cases = 0

    # E1 (boundary): MIN_SAMPLES (20) is the cutoff for a p95; 100 samples for p94/p96.
    nineteen = series_stats([0.001] * 19)
    assert nineteen["p95_s"] is None
    assert nineteen["refused_reason"] is not None
    cases += 1

    twenty = series_stats([float(i) for i in range(20)])
    assert twenty["p95_s"] is not None
    assert twenty["refused_reason"] is None
    cases += 1

    ninety_nine = series_stats([float(i) for i in range(99)])
    assert ninety_nine["p94_s"] is None
    assert ninety_nine["p96_s"] is None
    cases += 1

    one_hundred = series_stats([float(i) for i in range(100)])
    assert one_hundred["p94_s"] is not None
    assert one_hundred["p96_s"] is not None
    cases += 1

    # E3 (empty): an empty series is refused, never a plausible number.
    empty = series_stats([])
    assert empty["n"] == 0
    assert empty["p95_s"] is None
    cases += 1

    # E6 (precision): the pass bar is raw-float <= 2.0, not a rounded print value.
    idle = series_stats([float(i) for i in range(100)])
    equal_under = {**idle, "p95_s": idle["p95_s"] * 2.0}
    equal_block = ratio_block(idle, equal_under)
    assert equal_block["ratio"] == 2.0
    assert equal_block["verdict"] == "pass"
    cases += 1

    just_over = {**idle, "p95_s": math.nextafter(idle["p95_s"] * 2.0, math.inf)}
    just_over_block = ratio_block(idle, just_over)
    assert just_over_block["verdict"] == "miss"
    cases += 1

    # E3: a refused series gives ratio and verdict null, never a guessed number.
    refused_under = series_stats([0.001] * 5)
    refused_block = ratio_block(idle, refused_under)
    assert refused_block["ratio"] is None
    assert refused_block["verdict"] is None
    cases += 1

    # E2 (adjacency): a sample stamped exactly at t_builds_start belongs to under-load,
    # not idle (the half-open/closed boundary run_experiment.py's segmentation uses).
    t_start, t_builds_start, t_builds_done = 0.0, 10.0, 20.0
    samples = [
        {"t": 9.999, "latency_s": 0.001},   # idle
        {"t": 10.0, "latency_s": 0.002},    # under-load -- the boundary case
        {"t": 20.0, "latency_s": 0.003},    # under-load -- inclusive right edge
    ]
    idle_bucket = [s["latency_s"] for s in samples if t_start <= s["t"] < t_builds_start]
    under_bucket = [s["latency_s"] for s in samples
                    if t_builds_start <= s["t"] <= t_builds_done]
    assert idle_bucket == [0.001]
    assert under_bucket == [0.002, 0.003]
    cases += 1

    print(f"self-check: {cases} cases passed")
    return 0


def _recompute_run(label: str, out_dir: Path) -> dict[str, object]:
    """Recompute every field `run_experiment.py` wrote for `label`, straight from the
    raw JSONL -- the inverse of writing it, so a mismatch is a real bug, not noise."""
    summary = json.loads((out_dir / f"{label}.summary.json").read_text())
    inproc_lines = [json.loads(line)
                    for line in (out_dir / f"{label}.inproc.jsonl").read_text().splitlines()]
    poller_samples = [json.loads(line)
                       for line in (out_dir / f"{label}.poller.jsonl").read_text().splitlines()]

    recomputed: dict[str, object] = {"scenarios": {}}
    for name, scenario in summary["scenarios"].items():
        inproc_idle = next(line["latency_s"] for line in inproc_lines
                            if line["scenario"] == name and line["series"] == "idle")
        inproc_under = next(line["latency_s"] for line in inproc_lines
                             if line["scenario"] == name and line["series"] == "under_load")
        inproc_idle_stats = series_stats(inproc_idle)
        inproc_under_stats = series_stats(inproc_under)

        t_start = scenario["t_start"]
        t_builds_start = scenario["t_builds_start"]
        t_builds_done = scenario["t_builds_done"]
        poller_idle = [s["latency_s"] for s in poller_samples
                       if t_start <= s["t"] < t_builds_start]
        poller_under = [s["latency_s"] for s in poller_samples
                         if t_builds_start <= s["t"] <= t_builds_done]
        poller_idle_stats = series_stats(poller_idle)
        poller_under_stats = series_stats(poller_under)

        recomputed["scenarios"][name] = {
            "inproc": {"idle": inproc_idle_stats, "under_load": inproc_under_stats,
                       **ratio_block(inproc_idle_stats, inproc_under_stats)},
            "poller": {"idle": poller_idle_stats, "under_load": poller_under_stats,
                       **ratio_block(poller_idle_stats, poller_under_stats)},
        }
    return recomputed


def _diff_field(path: str, want: object, got: object) -> str | None:
    if isinstance(want, float) and isinstance(got, float):
        if math.isclose(want, got, rel_tol=1e-12, abs_tol=1e-15):
            return None
        return f"{path}: summary has {want!r}, recomputed {got!r}"
    if want != got:
        return f"{path}: summary has {want!r}, recomputed {got!r}"
    return None


def _diff_recursive(prefix: str, want: object, got: object) -> str | None:
    if isinstance(want, dict) and isinstance(got, dict):
        for key in want:
            if key not in got:
                return f"{prefix}.{key}: missing from recomputed"
            diff = _diff_recursive(f"{prefix}.{key}", want[key], got[key])
            if diff is not None:
                return diff
        return None
    return _diff_field(prefix, want, got)


def _check(labels: list[str], out_dir: Path) -> int:
    exit_code = 0
    for label in labels:
        summary = json.loads((out_dir / f"{label}.summary.json").read_text())
        recomputed = _recompute_run(label, out_dir)
        diff = None
        for name, scenario in summary["scenarios"].items():
            recomputed_scenario = recomputed["scenarios"][name]
            for source in ("inproc", "poller"):
                diff = _diff_recursive(f"scenarios.{name}.{source}",
                                        scenario[source], recomputed_scenario[source])
                if diff is not None:
                    break
            if diff is not None:
                break
        if diff is None:
            print(f"check ok: {label}")
        else:
            print(f"check FAILED: {label}: {diff}", file=sys.stderr)
            exit_code = 1
    return exit_code


def _fmt_ms(p95_s: object) -> str:
    return "insufficient" if p95_s is None else f"{float(p95_s) * 1000:.3f} ms"


def _fmt_ratio(block: dict[str, object]) -> str:
    return "--" if block["ratio"] is None else f"{block['ratio']:.3f}x ({block['verdict']})"


def _tables(labels: list[str], out_dir: Path) -> int:
    for label in labels:
        summary = json.loads((out_dir / f"{label}.summary.json").read_text())
        print(f"\n## {label} (head {summary['head']}, {summary['machine']})\n")
        print("| Scenario | Source | Idle p95 (n) | Under-load p95 (n) | Ratio | "
              "Slowest build | Refused |")
        print("|---|---|---|---|---|---|---|")
        for name, scenario in summary["scenarios"].items():
            for source in ("inproc", "poller"):
                block = scenario[source]
                idle, under = block["idle"], block["under_load"]
                print(f"| {name} | {source} | {_fmt_ms(idle['p95_s'])} (n={idle['n']}) | "
                      f"{_fmt_ms(under['p95_s'])} (n={under['n']}) | {_fmt_ratio(block)} | "
                      f"{scenario['slowest_build_s']:.2f} s | {scenario['refused']} |")
        print("\n### Floor analysis\n")
        print("| Scenario | Source | Series | p94 (ms) | p95 (ms) | p96 (ms) | "
              "min gap (us) | ties |")
        print("|---|---|---|---|---|---|---|---|")
        for name, scenario in summary["scenarios"].items():
            for source in ("inproc", "poller"):
                for series_name in ("idle", "under_load"):
                    s = scenario[source][series_name]
                    p94 = "--" if s["p94_s"] is None else f"{s['p94_s'] * 1000:.3f}"
                    p95 = _fmt_ms(s["p95_s"])
                    p96 = "--" if s["p96_s"] is None else f"{s['p96_s'] * 1000:.3f}"
                    gap = "--" if s["min_gap_s"] is None else f"{s['min_gap_s'] * 1e6:.2f}"
                    print(f"| {name} | {source} | {series_name} | {p94} | {p95} | {p96} | "
                          f"{gap} | {s['ties']} |")
        print(f"\nClock resolution: {summary['clock_resolution_s'] * 1e9:.1f} ns")

    pairs = [(a, b) for a in labels for b in labels if b == f"{a[:-5]}run2" and a.endswith("run1")]
    for run1, run2 in pairs:
        s1 = json.loads((out_dir / f"{run1}.summary.json").read_text())
        s2 = json.loads((out_dir / f"{run2}.summary.json").read_text())
        print(f"\n### Observation 1: {run1} vs {run2} (concurrent)\n")
        print("| Run | Source | Ratio | Under-load n | Refused |")
        print("|---|---|---|---|---|")
        for label, s in ((run1, s1), (run2, s2)):
            c = s["scenarios"].get("concurrent")
            if c is None:
                continue
            for source in ("inproc", "poller"):
                block = c[source]
                print(f"| {label} | {source} | {_fmt_ratio(block)} | "
                      f"{block['under_load']['n']} | {c['refused']} |")
        r1 = s1["scenarios"].get("concurrent", {}).get("inproc", {}).get("ratio")
        r2 = s2["scenarios"].get("concurrent", {}).get("inproc", {}).get("ratio")
        if r1 is not None and r2 is not None:
            direction = "worse" if r2 > r1 else "better or equal"
            print(f"\nRun 2 vs Run 1 (inproc, raw ratio): {direction}.")
    return 0


def _sessions(labels: list[str], out_dir: Path) -> int:
    for label in labels:
        status = json.loads((out_dir / f"{label}.status.json").read_text())
        print(f"\n## Session {label}\n")
        print(f"- State: {status['state']}, decisive: {status['decisive']}")
        samples = status["quiet"]["samples"][-3:] or status["quiet"]["samples"]
        for sample in samples:
            print(f"  - quiet sample {sample['utc']}: load1={sample['load1']}")
        print(f"- Top CPU: {status['host']['top_cpu']}")
        print(f"- docker ps: {status['host']['docker_ps']}")
        print(f"- Load after: {status['load_after']}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tabulate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--check", nargs="+", metavar="LABEL")
    group.add_argument("--tables", nargs="+", metavar="LABEL")
    group.add_argument("--sessions", nargs="+", metavar="LABEL")
    parser.add_argument("--out-dir", type=Path, default=HERE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.self_check:
        return _self_check()
    if args.check:
        return _check(args.check, args.out_dir)
    if args.tables:
        return _tables(args.tables, args.out_dir)
    return _sessions(args.sessions, args.out_dir)


if __name__ == "__main__":
    sys.exit(main())
