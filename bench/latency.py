"""Does `/api/health` stay fast while a build is in flight?

Reproduces the debt file's own two load scenarios
(`docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md`) against a
running **host** service (`make serve`), because D-17 requires the latency half to be
measured the way the recorded baseline was -- container overhead would make the new
numbers incomparable to the old ones.

Not part of `make verify` (D-16): it needs a running service and minutes, and a latency
assertion on shared hardware would flap until someone stopped believing it. Run it with
`make bench.latency` after `make serve` is up.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

import httpx

from bench import machine_facts

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# The debt file's own recorded numbers (12-core machine). Printed verbatim beside every
# new run so nobody reads a cross-machine absolute as a target -- the acceptance
# criterion is the *ratio* (under-load p95 within 2x of idle p95), not the seconds
# (D-17, 02-RESEARCH.md Pitfall 4).
RECORDED_BASELINE = (
    "single: 0.22s -> 0.76s -> 2.00s under one 200-tooth fine build; "
    "concurrent: repeatedly over 5s under ten concurrent builds "
    "(12-core machine, docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md)"
)

# statistics.quantiles(samples, n=20)'s own bucket count. Fewer samples than buckets
# makes the 95th-percentile cut point a guess about data that was never collected, not
# a measurement -- refuse instead of printing one (L08).
MIN_SAMPLES = 20

SETTLE_SECONDS = 2.0  # idle sampling window before load starts


def _p95(samples: list[float]) -> float:
    """The one named stdlib method used for every p95 in this harness.

    `statistics.quantiles(samples, n=20)[-1]` is the last of 20 cut points: the 95th
    percentile. Hand-rolling a percentile (e.g. `sorted(samples)[int(0.95 * len)]`) is
    exactly the plausible-but-off-by-one number L08 forbids for a figure that is this
    project's own acceptance criterion.
    """
    return statistics.quantiles(samples, n=20)[-1]


def _sample_for(base_url: str, client: httpx.Client, duration: float) -> list[float]:
    """Sample `/api/health` as fast as the server answers, for `duration` seconds."""
    samples: list[float] = []
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        t0 = time.perf_counter()
        client.get(f"{base_url}/api/health", timeout=30.0)
        samples.append(time.perf_counter() - t0)
    return samples


def _sample_while_building(base_url: str, client: httpx.Client,
                            futures: list[Future[float | None]]) -> list[float]:
    """Keep sampling `/api/health` for as long as at least one build is in flight.

    A do-while shape (sample first, check after) guarantees at least one sample even
    for a build that finishes before the first check would otherwise run.
    """
    samples: list[float] = []
    while True:
        t0 = time.perf_counter()
        client.get(f"{base_url}/api/health", timeout=30.0)
        samples.append(time.perf_counter() - t0)
        if all(future.done() for future in futures):
            return samples


def _build(base_url: str, client: httpx.Client, teeth: int, quality: str) -> float | None:
    """One `/api/model.stl` download; returns how long it took, in seconds, or `None`
    if admission control refused it (`503`) rather than building.

    A refusal here is not a harness failure: `MAX_QUEUED_BUILDS` (D-09, `app.py`) is 4
    at the shipping default, and the concurrent scenario below deliberately fires 10
    requests at once -- `docs/plan-2026-09-21.md`'s own outcome table records exactly
    this admission-control behaviour pre-dating this phase ("6 of 10 refused"). Any
    other non-2xx status is a real failure and still raises.
    """
    t0 = time.perf_counter()
    response = client.get(f"{base_url}/api/model.stl",
                           params={"teeth": teeth, "quality": quality}, timeout=120.0)
    if response.status_code == 503:
        return None
    response.raise_for_status()
    return time.perf_counter() - t0


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    idle: list[float]
    under_load: list[float]
    slowest_build: float
    attempted: int
    refused: int


def _collect(futures: list[Future[float | None]]) -> tuple[float, int, int]:
    """Slowest completed build, attempted count, refused (503) count."""
    results = [future.result() for future in futures]
    completed = [r for r in results if r is not None]
    refused = len(results) - len(completed)
    return (max(completed) if completed else 0.0), len(results), refused


def scenario_single(base_url: str) -> ScenarioResult:
    """Idle p95, then one 200-tooth fine build in flight -- the scenario that produced
    the recorded 0.22s -> 0.76s -> 2.00s progression."""
    with httpx.Client() as client:
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        with ThreadPoolExecutor(max_workers=1) as pool:
            futures = [pool.submit(_build, base_url, client, 200, "fine")]
            under_load = _sample_while_building(base_url, client, futures)
        slowest, attempted, refused = _collect(futures)
    return ScenarioResult("single", idle, under_load, slowest, attempted, refused)


def scenario_concurrent(base_url: str) -> ScenarioResult:
    """Idle p95, then ten concurrent fine builds -- the scenario that repeatedly
    exceeded 5s. Admission control (MAX_QUEUED_BUILDS, D-09) refuses whatever doesn't
    fit the queue; see `_build`'s docstring."""
    with httpx.Client() as client:
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(_build, base_url, client, teeth, "fine")
                       for teeth in range(190, 200)]
            under_load = _sample_while_building(base_url, client, futures)
        slowest, attempted, refused = _collect(futures)
    return ScenarioResult("concurrent", idle, under_load, slowest, attempted, refused)


_SCENARIOS: dict[str, Callable[[str], ScenarioResult]] = {
    "single": scenario_single,
    "concurrent": scenario_concurrent,
}


def _p95_or_warn(samples: list[float], label: str) -> tuple[float, int] | None:
    """The one place a p95 is computed, or refused (L08).

    A p95 over fewer samples than `statistics.quantiles`' own bucket count is a
    plausible number, not a measured one -- warn and refuse rather than print it.
    """
    if len(samples) < MIN_SAMPLES:
        print(f"warning: {label} has only {len(samples)} /api/health samples "
              f"(need >= {MIN_SAMPLES}); refusing to report a p95", file=sys.stderr)
        return None
    return _p95(samples), len(samples)


def _report_markdown(name: str, idle_p95: float, idle_n: int, load_p95: float,
                      load_n: int, slowest_build: float, attempted: int,
                      refused: int) -> str:
    ratio = load_p95 / idle_p95 if idle_p95 > 0 else float("inf")
    return (
        f"## Latency: {name}\n\n"
        f"- Machine: {machine_facts()}\n"
        f"- Idle p95: {idle_p95 * 1000:.1f} ms (n={idle_n})\n"
        f"- Under-load p95: {load_p95 * 1000:.1f} ms (n={load_n})\n"
        f"- Ratio (under-load / idle): {ratio:.2f}x -- pass bar is <= 2.00x\n"
        f"- Slowest single build observed: {slowest_build:.2f} s\n"
        f"- Build requests: {attempted} attempted, {refused} refused by admission "
        f"control (`503`, D-09 -- expected once concurrency exceeds MAX_QUEUED_BUILDS, "
        f"not a harness failure)\n"
        f"- Recorded baseline (different machine, ratio-only comparison per D-17): "
        f"{RECORDED_BASELINE}\n"
    )


def _run_scenario(name: str, base_url: str) -> bool:
    result = _SCENARIOS[name](base_url)
    idle = _p95_or_warn(result.idle, f"{name}/idle")
    under_load = _p95_or_warn(result.under_load, f"{name}/under-load")
    if idle is None or under_load is None:
        return False
    idle_p95, idle_n = idle
    load_p95, load_n = under_load
    print(_report_markdown(name, idle_p95, idle_n, load_p95, load_n, result.slowest_build,
                            result.attempted, result.refused))
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bench.latency",
        description="Reproduce the debt file's two load scenarios against a running "
                     "host service: does /api/health stay fast while a build runs?",
    )
    parser.add_argument(
        "scenario", nargs="?", choices=sorted(_SCENARIOS), default=None,
        help="Which load scenario to run. Omit to run both, in order -- the shape "
             "`make bench.latency` uses.")
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"The running host service (`make serve`). Default: {DEFAULT_BASE_URL}.")
    args = parser.parse_args(argv)

    names = [args.scenario] if args.scenario else sorted(_SCENARIOS)
    # Run every scenario before deciding the exit code -- a generator inside all() would
    # short-circuit on the first failure and silently skip the rest.
    results = [_run_scenario(name, args.base_url) for name in names]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
