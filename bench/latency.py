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
import json
import statistics
import sys
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

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


def _sample_while_building[T](base_url: str, client: httpx.Client,
                               futures: list[Future[T]]) -> list[float]:
    """Keep sampling `/api/health` for as long as at least one build is in flight.

    A do-while shape (sample first, check after) guarantees at least one sample even
    for a build that finishes before the first check would otherwise run.

    A PEP 695 type parameter, not a fixed `Future[float | None]`: `Future` is invariant,
    so the composed scenario's `Future[RequestOutcome]` list cannot satisfy a signature
    typed for `Future[float | None]` even though this body never reads a future's
    result -- only `scenario_single`/`scenario_concurrent`'s `Future[float | None]` and
    `run_composed`'s `Future[RequestOutcome]` instantiate `T` differently; the body
    below is unchanged either way.
    """
    samples: list[float] = []
    while True:
        t0 = time.perf_counter()
        client.get(f"{base_url}/api/health", timeout=30.0)
        samples.append(time.perf_counter() - t0)
        if all(future.done() for future in futures):
            return samples


# bench/sweeps/composed.json (Phase 12, D-01): 18 rows stacking each body-cutout
# pattern's own heaviest bore with the tip chamfer at its cap, plus six single-feature
# baselines. SC3 fires ten of them concurrently (D-13).
COMPOSED_SWEEP = Path(__file__).parent / "sweeps" / "composed.json"

# The ten rows SC3 fires, 0-based into COMPOSED_SWEEP (1-based 4, 2, 3, 1, 9, 6, 10, 12,
# 11, 5) -- the worst row first, then the next nine heaviest by "Build + slower export"
# (bench/RESULTS.md "### Re-run after the gate (lower-le: spoke_count 32)"): 29.42,
# 28.92, 28.87, 28.61, 27.27, 24.91, 24.06, 22.26, 22.09, 16.80 s of SPUR_BUILD_TIMEOUT's
# 30 s shipping default. Ten distinct keys so admission control (MAX_QUEUED_BUILDS, 4)
# takes exactly four of them and `hash(p) % workers` (D-07 affinity) spreads the four
# admitted builds over both workers, stacking kernel work on the host rather than
# queuing every admitted build behind a single worker (D-13).
COMPOSED_ROWS = (3, 1, 2, 0, 8, 5, 9, 11, 10, 4)


def _composed_rows() -> list[dict[str, int | float | str]]:
    """The ten `COMPOSED_ROWS` rows of `COMPOSED_SWEEP`, read directly as JSON.

    Not validated here, and not read through `bench.build_time.load_sweep`: that module
    imports `spur.model`, and through it cadquery, which would pull the CAD kernel into
    this harness's own measuring client -- the server validates every request on its
    own. `tests/test_bench.py` pins every row against `load_sweep`'s own output, so the
    two readings are checked to agree. Typed `int | float | str` (never the wider
    `object`), not from the JSON spec in general but from this one sweep file's actual
    field values -- the type `_fetch` needs to pass every row straight through as
    `httpx` query params.
    """
    rows: list[dict[str, int | float | str]] = json.loads(COMPOSED_SWEEP.read_text())
    return [rows[i] for i in COMPOSED_ROWS]


@dataclass(frozen=True)
class RequestOutcome:
    params: str  # the `k=v` label `load_sweep` uses, from the row's own raw JSON dict
    status: str  # "200", "503 " + the server's own `detail[0]["type"]`, or "500"
    wall_s: float
    sent: float  # time.monotonic() -- comparable across this process only
    done: float


@dataclass(frozen=True)
class ComposedRun:
    result: ScenarioResult
    requests: tuple[RequestOutcome, ...]  # in firing order: worst row first
    workers_replaced_before: int
    workers_replaced_after: int


def _fetch(base_url: str, client: httpx.Client, row: dict[str, int | float | str],
           record_500: bool = False) -> RequestOutcome:
    """One `/api/model.stl` request for a composed row, at `quality=fine` like `_build`
    (timeout 120.0, same as `_build`): `"200"` on success; `"503 " + detail[0]["type"]`
    (`"busy"` | `"timeout"` | `"pool_broken"` -- `src/spur/app.py`'s own three 503
    `type` values) on refusal, read from the documented body; any other status still
    raises (`_build`'s own rule) -- and a 503 without that documented field raises
    naming the body, never a guessed reason (L08).

    A 500 is not one of the service's three documented refusals. The scenario that
    exists to observe one (the same-slot timeout race,
    REQ-same-slot-timeout-race-reproduced) passes `record_500=True`, so the run
    finishes and the 500 lands in its table; every other caller still raises on it
    (SC3's rule, pinned in `tests/test_bench.py`)."""
    label = " ".join(f"{k}={v}" for k, v in row.items())
    sent = time.monotonic()
    response = client.get(f"{base_url}/api/model.stl",
                           params={**row, "quality": "fine"}, timeout=120.0)
    if response.status_code == 503:
        try:
            reason = response.json()["detail"][0]["type"]
        except (ValueError, KeyError, IndexError) as exc:
            raise ValueError(
                f"503 response body missing detail[0].type: {response.text!r}") from exc
        status = f"503 {reason}"
    elif record_500 and response.status_code == 500:
        status = "500"
    else:
        response.raise_for_status()
        status = "200"
    done = time.monotonic()
    return RequestOutcome(label, status, done - sent, sent, done)


def _pool_state(base_url: str, client: httpx.Client) -> tuple[int, int]:
    """`(queue_available, workers_replaced)` from `/api/health`'s `pool` key; raises if
    `pool` is null -- SC3 needs a server whose lifespan actually started, not a
    `TestClient(app)` run without `with` (`src/spur/app.py`'s `health()` docstring)."""
    response = client.get(f"{base_url}/api/health", timeout=30.0)
    response.raise_for_status()
    pool = response.json()["pool"]
    if pool is None:
        raise ValueError(f"/api/health reports a null pool: {response.text!r}")
    return pool["queue_available"], pool["workers_replaced"]


def run_composed(base_url: str, rows: list[dict[str, int | float | str]] | None = None,
                 label: str = "composed", record_500: bool = False) -> ComposedRun:
    """SC3 (D-13, D-16): the composed sweep's worst row fired alone first, confirmed
    (via `/api/health`) to be holding a build slot before the other nine heaviest rows
    fire beside it -- ten concurrent builds total, admission control (`MAX_QUEUED_BUILDS`
    4) taking four. Never run on a server a bar session also used: a request this
    scenario times out gets its worker replaced (D-10/D-12, `src/spur/pool.py`), and
    that replacement would pollute a bar reading taken afterwards on the same server.
    The admission-wait `/api/health` reads below are not samples -- they do not enter
    `idle` or `under_load`.

    `rows` (default: the ten composed rows) and `label` (the result's name) let the
    `identical` scenario reuse this firing rule; `record_500` is passed to every
    `_fetch` (see there). The defaults reproduce SC3's composed run exactly.
    """
    rows = _composed_rows() if rows is None else rows
    with httpx.Client() as client:
        queue_available_before, workers_replaced_before = _pool_state(base_url, client)
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        with ThreadPoolExecutor(max_workers=10) as pool:
            worst_future = pool.submit(_fetch, base_url, client, rows[0], record_500)
            deadline = time.monotonic() + 10.0
            held = False
            while True:
                if worst_future.done():
                    raise RuntimeError(
                        "the worst composed row was served without holding a build "
                        "slot -- a cache hit? SC3 needs a fresh server")
                queue_available, _ = _pool_state(base_url, client)
                if queue_available < queue_available_before:
                    held = True
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
            if not held:
                raise RuntimeError(
                    "the worst composed row never held a build slot within 10s -- "
                    "SC3 needs a fresh server")
            rest_futures = [pool.submit(_fetch, base_url, client, row, record_500)
                            for row in rows[1:]]
            futures = [worst_future, *rest_futures]
            under_load = _sample_while_building(base_url, client, futures)
        requests = tuple(future.result() for future in futures)
        _, workers_replaced_after = _pool_state(base_url, client)
    # "refused by admission control" (the harness's existing report line) means 503
    # busy only -- a timeout or pool_broken is a different server behaviour, counted in
    # the per-request table instead (A3).
    slowest = max((r.wall_s for r in requests if r.status == "200"), default=0.0)
    refused = sum(1 for r in requests if r.status == "503 busy")
    result = ScenarioResult(label, idle, under_load, slowest, 10, refused)
    return ComposedRun(result, requests, workers_replaced_before, workers_replaced_after)


def _composed_markdown(run: ComposedRun) -> str:
    """The per-request table and health delta SC3's write-up copies verbatim (E10). No
    `SPUR_BUILD_TIMEOUT` value is printed here: this client cannot know the server's
    setting -- `bench/RESULTS.md` names it from the server's own recorded environment."""
    lines = [f"### Per-request outcomes ({run.result.name})", "",
             "| # | Parameters | Outcome | Wall time (s) |", "|---|---|---|---|"]
    for i, r in enumerate(run.requests, start=1):
        lines.append(f"| {i} | {r.params} | {r.status} | {r.wall_s:.2f} |")
    counts: dict[str, int] = {}
    for r in run.requests:
        counts[r.status] = counts.get(r.status, 0) + 1
    lines.append("")
    lines.append(", ".join(f"{status}: {count}" for status, count in counts.items()))
    lines.append(f"- /api/health workers_replaced: {run.workers_replaced_before} -> "
                 f"{run.workers_replaced_after}")
    return "\n".join(lines) + "\n"


def scenario_composed(base_url: str) -> ScenarioResult:
    """SC3 (D-13, D-16): the composed worst row under ten concurrent builds. Never run
    on a server a bar session will use -- a timed-out request here gets its worker
    replaced, and that replacement would pollute a bar reading taken afterwards on the
    same server."""
    run = run_composed(base_url)
    print(_composed_markdown(run))
    return run.result


def _identical_rows() -> list[dict[str, int | float | str]]:
    """Ten copies of the composed worst row. 29.42 s alone (composed.json row 4), they
    are one cache key, so D-07's hash affinity routes every admitted copy to one worker
    slot -- `MAX_QUEUED_BUILDS` (4) admits four: one building, three queued behind it.
    That is the same-slot double timeout SC3 hit by affinity luck, isolated from
    cross-slot contention (13-CONTEXT `<deferred>`; the race debt's Next step)."""
    return [_composed_rows()[0]] * 10


def scenario_identical(base_url: str) -> ScenarioResult:
    """Phase 17, REQ-same-slot-timeout-race-reproduced: the worst composed row ten
    times, recording a 500 instead of raising on it. Never on a server a bar session
    will use -- it times out and replaces workers by design."""
    run = run_composed(base_url, _identical_rows(), "identical", record_500=True)
    print(_composed_markdown(run))
    return run.result


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
    "composed": scenario_composed,
    "identical": scenario_identical,
}

# A fourth registered scenario changes nothing here: the no-argument run reads this
# tuple, never `sorted(_SCENARIOS)` (which would put `composed` first), and neither
# `composed` nor `identical` -- both time out and replace a worker (D-10/D-12) -- may
# enter it, or that replacement would pollute the bar (D-16). The tuple pins the order
# the no-argument run has always had (D-07, D-15).
DEFAULT_SCENARIOS: tuple[str, ...] = ("concurrent", "single")


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
    # RECORDED_BASELINE is the debt file's single/concurrent numbers (D-17) -- printing
    # it under a "composed" or "identical" heading would invite a reader to compare that
    # ratio against numbers measured for a different scenario entirely. Omit it there.
    has_bar = name not in ("composed", "identical")
    baseline_line = (
        f"- Recorded baseline (different machine, ratio-only comparison per D-17): "
        f"{RECORDED_BASELINE}\n" if has_bar else ""
    )
    # The 2.00x bar is the single/concurrent scenarios' criterion; RESULTS.md reads
    # neither composed nor identical against it, so printing it beside their ratio
    # would invite exactly that reading.
    bar = " -- pass bar is <= 2.00x" if has_bar else ""
    return (
        f"## Latency: {name}\n\n"
        f"- Machine: {machine_facts()}\n"
        f"- Idle p95: {idle_p95 * 1000:.1f} ms (n={idle_n})\n"
        f"- Under-load p95: {load_p95 * 1000:.1f} ms (n={load_n})\n"
        f"- Ratio (under-load / idle): {ratio:.2f}x{bar}\n"
        f"- Slowest single build observed: {slowest_build:.2f} s\n"
        f"- Build requests: {attempted} attempted, {refused} refused by admission "
        f"control (`503`, D-09 -- expected once concurrency exceeds MAX_QUEUED_BUILDS, "
        f"not a harness failure)\n"
        f"{baseline_line}"
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
        help="Which load scenario to run. Omit to run the two bar scenarios, "
             "concurrent then single -- the shape `make bench.latency` uses.")
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"The running host service (`make serve`). Default: {DEFAULT_BASE_URL}.")
    args = parser.parse_args(argv)

    names = [args.scenario] if args.scenario else list(DEFAULT_SCENARIOS)
    # Run every scenario before deciding the exit code -- a generator inside all() would
    # short-circuit on the first failure and silently skip the rest.
    results = [_run_scenario(name, args.base_url) for name in names]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
