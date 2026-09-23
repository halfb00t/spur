---
phase: 02-cad-off-the-event-loop
reviewed: 2026-09-23T15:00:00Z
depth: standard
files_reviewed: 27
files_reviewed_list:
  - bench/__init__.py
  - bench/corpus.py
  - bench/latency.py
  - bench/memory.py
  - bench/README.md
  - bench/RESULTS.md
  - compose.yaml
  - docker/smoke.py
  - Dockerfile
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/architecture/overview.md
  - docs/architecture/packaging.md
  - docs/ideas/2026-09-22-measure-or-soften-the-pi5-claim.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md
  - Makefile
  - pyproject.toml
  - README.md
  - src/spur/app.py
  - src/spur/build_errors.py
  - src/spur/cli.py
  - src/spur/model.py
  - src/spur/pool.py
  - tests/test_api.py
  - tests/test_pool.py
findings:
  critical: 2
  warning: 2
  info: 0
  total: 4
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-09-23T15:00:00Z
**Depth:** standard
**Files Reviewed:** 27
**Status:** issues_found

## Summary

Reviewed the process-pool split (`pool.py`), the admission-control/gzip-cache seam in
`app.py`, packaging (`Dockerfile`, `compose.yaml`), and the bench harness
(`bench/latency.py`, `bench/memory.py`), against the docs and decision log that describe
what they're supposed to guarantee.

The pool's timeout/replacement path (D-10, D-12) was traced against the one usage pattern
`pool.py`'s own docstring calls out as normal: several requests for the same gear (preview
STL, fine STL, STEP) landing on the same single-worker executor by parameter-hash affinity
(D-07). Under that pattern, a wedged build that times out cancels a second, still-queued
request on the same worker via `ProcessPoolExecutor.shutdown(cancel_futures=True)` — and
that cancellation surfaces as an unhandled `asyncio.CancelledError`, which is a
`BaseException`, not an `Exception`, so it is not caught by `_run_with_timeout`'s own
handlers, by `model()`'s `except BuildError/BuildTimeout/BrokenProcessPool`, or by
Starlette's `ServerErrorMiddleware` (confirmed against the installed Starlette:
`middleware/errors.py` catches `except Exception`, not `BaseException`). This turns a
"gear that's fine, worker's wedged" case into a dropped/broken response instead of the
project's own documented, closed set of `422`/`503` outcomes. No test in `tests/test_pool.py`
exercises two requests on the same hash slot with one timing out, so this path is untested.

`bench/memory.py`'s `sweep()` re-runs the exact class of bug `bench/RESULTS.md` records
as already found and hand-fixed once: `sweep()` starts the container via plain
`docker compose run ... spur`, inheriting `compose.yaml`'s shipped `mem_limit: 4g` — but
the N=4 row `sweep()` itself is supposed to produce peaked at 4731.9 MiB, *above* that 4g
cap. Unlike `confirm()` (which builds a `mem_limit` override file), `sweep()` has no
mechanism to relax the cap before measuring, so any future `make bench.memory` (the exact
command the README and the `compose.yaml` mem_limit comment tell an operator to re-run
after raising `SPUR_BUILD_WORKERS`) will silently reproduce "the pre-existing `mem_limit`
was capping the sweep it was supposed to be replaced by" — the exact failure mode
`bench/RESULTS.md`'s own "Two blocking issues found and fixed" section describes as
already hit once and worked around by hand.

Two further issues degrade quality without being outright incorrect: a Dockerfile comment
misstates the latency evidence it cites (the claimed 0.7-1.3 ms range only holds for the
four post-L19-fix runs, not "all eight" runs `bench/RESULTS.md` records), and a second,
independent concurrent failure on the same hash slot (two requests, same worker, worker
dies) causes `BuildPool.recreate_for` to run twice for one incident, discarding a freshly
spawned, still-warming replacement worker and double-counting `workers_replaced`.

## Critical Issues

### CR-01: A second same-worker request is killed by `CancelledError`, not a handled `BuildTimeout`, when its sibling request times out

**File:** `src/spur/pool.py:94-100, 120-158`
**Issue:**

`BuildPool` routes every request for one `GearParams` to the same single-worker
`ProcessPoolExecutor` by parameter-hash affinity (D-07) — the module's own docstring
names exactly this as the normal case: "the UI's preview STL, fine STL and STEP requests
for one gear ... keeping them on the same worker". Because each executor has
`max_workers=1`, a second concurrent request for the same gear queues inside that
executor rather than running.

If the first (running) request wedges and hits the per-build timeout
(`_run_with_timeout`, lines 121-149), the `except asyncio.TimeoutError` branch does:

```python
for proc in executor._processes.values():
    proc.terminate()
self.recreate_for(p)
```

`recreate_for` (lines 94-100) then calls:

```python
self._executors[i].shutdown(wait=False, cancel_futures=True)
```

`ProcessPoolExecutor.shutdown(cancel_futures=True)` cancels every pending-but-not-started
future on that executor synchronously, inside the call. The second request's future — the
one still queued behind the wedged build on the *same* executor — is exactly such a
future. Cancelling the underlying `concurrent.futures.Future` propagates to the
`asyncio.Future` `loop.run_in_executor` wrapped it in, so the coroutine awaiting it at
`await asyncio.wait_for(future, timeout=self.timeout)` (line 122) raises
`asyncio.CancelledError` — not `asyncio.TimeoutError`, not `BrokenProcessPool`.

`asyncio.CancelledError` is a `BaseException` subclass (since Python 3.8), not an
`Exception` subclass. It is not caught by:
- `_run_with_timeout`'s own `except asyncio.TimeoutError` / `except BrokenProcessPool`
  (neither matches).
- `app.py`'s `model()`, whose `try`/`except` only names `BuildError`, `BuildTimeout`,
  `BrokenProcessPool`.
- Starlette's `ServerErrorMiddleware`, which catches `except Exception` (confirmed against
  the installed package: `starlette/middleware/errors.py:165`), so it does not intercept a
  `BaseException`.

The result: the second request's coroutine raises out of the ASGI app entirely instead of
returning any of the four documented `detail[0].type` values
(`docs/architecture/http-api.md` calls these "pairwise distinct" and "a closed set the UI
can switch on"). In practice this means an uncaught exception escaping into uvicorn's
request handling — a dropped/broken response instead of a `503 timeout`, for a request
whose only fault was sharing a worker with one that wedged. `tests/test_pool.py`'s
`test_a_wedged_build_is_terminated_and_its_worker_replaced` only exercises one build per
worker at a time; no test drives two concurrent requests to the same hash slot with one
timing out, so this path is not covered.

**Fix:**
Treat cancellation of a queued sibling as itself a timeout, since from that request's
point of view it is exactly that ("your worker died while you were waiting behind
another build"):

```python
future = loop.run_in_executor(executor, func, *args)
try:
    return await asyncio.wait_for(future, timeout=self.timeout)
except asyncio.CancelledError:
    # A sibling request on the same hash slot (D-07) timed out first and its
    # recreate_for() cancelled this still-queued future via
    # ProcessPoolExecutor.shutdown(cancel_futures=True). From this request's
    # side that is indistinguishable from its own timeout -- report it as one,
    # rather than letting a BaseException escape past every except clause in
    # this module, app.py's model(), and Starlette's ServerErrorMiddleware
    # (which only catches Exception, not BaseException).
    raise BuildTimeout(
        f"Build exceeded the {self.timeout}s per-build timeout. Try a coarser "
        "quality or fewer teeth."
    ) from None
except asyncio.TimeoutError:
    ...
```
Add a `tests/test_pool.py` case that submits two tasks to the same executor (one long
sleep, one short), lets the first hit `pool.timeout`, and asserts the second raises
`BuildTimeout` (or otherwise resolves cleanly) rather than `CancelledError`.

### CR-02: `bench.memory sweep` re-caps itself at the shipped `mem_limit`, silently reproducing an already-fixed measurement bug

**File:** `bench/memory.py:133-167, 195-203`; `compose.yaml:25`
**Issue:**

`bench/RESULTS.md`'s own "Two blocking issues found and fixed before this data could be
trusted" section records that the sweep was first run against `compose.yaml`'s
pre-existing `mem_limit: 2g`, which silently capped N=2 and N=4 at exactly `2048.0 MiB`
(the limit itself, not a real footprint) rather than the true peak, and had to be
"temporarily raised to `8g` for the sweep so the measurement could not be capped by the
value it exists to determine".

`_sweep_one` (lines 133-167) starts the container for each N with:

```python
subprocess.run(
    ["docker", "compose", "run", "--rm", "-d", "--name", container,
     "--service-ports", "-e", f"SPUR_BUILD_WORKERS={n}", "spur"],
    check=True, capture_output=True,
)
```

This passes no compose override file, so it uses `compose.yaml` as committed — currently
`mem_limit: 4g` (line 25 of `compose.yaml`, set from this very sweep's own result). But
the N=4 row this same sweep produced peaked at **4731.9 MiB**, which is *above* the
shipped 4g (4096 MiB) cap. Unlike `confirm()` (lines 216-251), which builds a one-line
`mem_limit` override via `_write_mem_limit_override` before running, `sweep()` has no
equivalent — it never relaxes the cap.

Concretely: the next time anyone runs `make bench.memory` (or `.venv/bin/python -m
bench.memory sweep`) — which is exactly the re-measurement step `compose.yaml`'s own
`mem_limit` comment and `README.md` tell an operator to run after raising
`SPUR_BUILD_WORKERS` or the cache settings — the N=4 row (and any N whose true peak
exceeds 4g) will be OOM-capped by the container's own `mem_limit`, producing either a
falsely low "peak" (again capped at ~4096 MiB, not the real footprint) or outright request
failures, and giving no signal that the number is invalid. This is the identical failure
mode `bench/RESULTS.md` already found once and worked around by hand; the harness itself
was never fixed to stop reproducing it. `bench/README.md`'s stated purpose — "a committed,
rerunnable harness so the numbers stay falsifiable by whoever doubts them later" — does
not hold for `sweep()` as shipped: the very act of "doubting them later" by rerunning it
against the current `compose.yaml` produces a self-capped, misleading number instead of a
fresh measurement.

**Fix:**
Give `sweep()` the same override mechanism `confirm()` already has — write a temporary
`mem_limit` override well above any plausible peak (e.g. reuse
`_write_mem_limit_override` with a generous fixed ceiling, or accept a `--mem-limit-cap`
flag) and pass it via `-f compose.yaml -f override.yaml` the same way `confirm()` does,
so `sweep()` can never be capped by the value it exists to determine:

```python
def _sweep_one(n: int, base_url: str) -> SweepRow:
    container = f"spur-bench-n{n}"
    _teardown(container)
    override_path = _write_mem_limit_override(SWEEP_UNCAPPED_MEM_LIMIT)  # e.g. "16g"
    try:
        subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "-f", override_path, "run",
             "--rm", "-d", "--name", container, "--service-ports",
             "-e", f"SPUR_BUILD_WORKERS={n}", "spur"],
            check=True, capture_output=True,
        )
        ...
    finally:
        Path(override_path).unlink(missing_ok=True)
```

## Warnings

### WR-01: Two same-slot failures on one incident double-recreate the worker and double-count `workers_replaced`

**File:** `src/spur/pool.py:94-100, 143-158`
**Issue:**

D-07's affinity routing means two concurrent requests for the same gear can both be
in-flight against the same single-worker executor (one running, one queued, or — for
`BrokenProcessPool` — both already dispatched when the worker dies, since a dead worker
fails every pending/running future on its executor with `BrokenProcessPool` rather than
cancelling them). When that happens, **both** coroutines independently reach their own
`except BrokenProcessPool` (or, per CR-01, one reaches `except asyncio.TimeoutError` and
the other now — after CR-01's fix — reaches the proposed `except asyncio.CancelledError`)
and each calls `self.recreate_for(p)` for the same hash slot index `i`.

The first call replaces `self._executors[i]` with a fresh, still-warming executor and
increments `self.replaced`. The second call then shuts down that *fresh* executor (which
never ran anything) and replaces it again, incrementing `self.replaced` a second time for
what is really one underlying incident. Consequences: `/api/health`'s
`pool.workers_replaced` (D-13) over-counts replacements relative to actual worker deaths,
and a brand-new worker's warm-up (`_warm()` importing `spur.model`/`cadquery`, D-04) is
discarded and repeated for no reason, adding avoidable startup latency to whichever
request lands on that slot next.

**Fix:** Guard `recreate_for` so a slot already recreated for the same incident isn't
recreated twice — e.g. track a generation counter per slot and only shut down/replace if
the caller's captured executor is still the one currently installed:

```python
def recreate_for(self, p: GearParams, stale: ProcessPoolExecutor) -> None:
    i = hash(p) % self.workers
    if self._executors[i] is not stale:
        return  # another coroutine already replaced this slot for the same incident
    self._executors[i].shutdown(wait=False, cancel_futures=True)
    self._executors[i] = ProcessPoolExecutor(
        max_workers=1, mp_context=_SPAWN, initializer=_warm)
    self.replaced += 1
```
and pass the `executor` already captured in `_run_with_timeout` as `stale`.

### WR-02: Dockerfile `HEALTHCHECK` comment overstates the latency evidence it cites

**File:** `Dockerfile:41-48`
**Issue:**

The comment above `HEALTHCHECK` states: "its measured under-load p95 is 0.7-1.3 ms across
all eight bench/RESULTS.md latency runs (worst: 1.3 ms, concurrent Runs 6 and 8)". Checked
against `bench/RESULTS.md`'s own `concurrent` scenario table, the eight recorded
under-load p95 values are: Run 1 1.2 ms, **Run 2 1.5 ms**, **Run 3 2.3 ms**, **Run 4 2.1
ms**, Run 5 0.8 ms, Run 6 1.3 ms, Run 7 1.2 ms, Run 8 1.3 ms. Three of the eight runs (2,
3, 4) fall outside the claimed 0.7-1.3 ms range, and Run 3's 2.3 ms is nearly double the
comment's stated "worst: 1.3 ms". The 0.7-1.3 ms range the comment describes only holds
for the four *post-L19-fix* runs (5-8); Runs 1-4 predate that fix and are excluded from
the claim without saying so.

This doesn't change the `HEALTHCHECK`'s practical safety — even 2.3 ms is negligible
against the 2 s timeout the comment is justifying — but it is a comment stating a
measurement more favorably than the cited source supports, in a codebase whose own
standing rule is "a number the tool prints is a number someone will cut metal to" and
whose comments are called out (`AGENTS.md`) as carrying "the measurement or the constraint
that forced the choice." A reader taking this comment at face value would believe all
eight runs, not four, cleared 1.3 ms.

**Fix:** Either scope the claim to the runs it actually describes, or state the true
range:

```
# /api/health no longer touches the CAD kernel or waits on a build worker (Phase 2,
# D-13): its measured under-load p95 is 0.6-2.3 ms across all eight bench/RESULTS.md
# latency runs (worst: 2.3 ms, concurrent Run 3) -- three orders of magnitude below the
# old 10 s. Post-fix (L19, Runs 5-8) it tightens to 0.7-1.3 ms. ...
```

---

_Reviewed: 2026-09-23T15:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
