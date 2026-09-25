---
phase: quick/260924-bv5
plan: 01
subsystem: api
tags: [process-pool, concurrent.futures, fastapi, docker-compose, memory-ceiling]

requires:
  - phase: 02-cad-off-the-event-loop
    provides: BuildPool (src/spur/pool.py), the D-07 hash-slot affinity, bench.memory sweep
provides:
  - "recreate_for(p, executor): a once-per-incident replacement guard on BuildPool's hash slots"
  - "A queued same-slot sibling now reliably surfaces as BrokenProcessPool -> 503 pool_broken, never a raw asyncio.CancelledError"
  - "bench.memory sweep's own 8g ceiling (_SWEEP_MEM_LIMIT_BYTES), applied via the existing _write_mem_limit_override mechanism, independent of compose.yaml's mem_limit"
  - "_is_capped: a pure predicate that refuses a sweep row whose peak reached the sweep's own ceiling instead of reporting it as a real measurement"
affects: [02-cad-off-the-event-loop, 02-REVIEW.md]

actuals:
  tokens: 6814
  tasks: 2
  commits: 4
plan_head_before: 1760eb94eb054d2053f39fbf26a5f3a39bb107a6

tech-stack:
  added: []
  patterns:
    - "Identity-guarded replace-once: recreate_for compares the caller's already-captured executor against the slot's live one before touching state, so N siblings observing one incident cause exactly one replacement"

key-files:
  created:
    - tests/test_bench.py
  modified:
    - src/spur/pool.py
    - src/spur/app.py
    - tests/test_pool.py
    - docs/architecture/http-api.md
    - bench/memory.py
    - bench/README.md
    - compose.yaml

key-decisions:
  - "CR-01's queued-sibling test took the primary route, not the fallback: the pre-fix exception the queued sibling actually raised, in every one of six observed two-request runs, was BrokenProcessPool -- never asyncio.CancelledError. No new error class or fifth detail[0].type value was added; the closed set of four stays exactly as it was."
  - "The real, reliably-reproduced bug behind CR-01/WR-01 was recreate_for running twice for one incident (pool.replaced going to 2, not 1) -- fixed with an identity guard, not a cancellation-catching handler."
  - "Coordinator follow-up 1: extended the queued-sibling test to THREE same-slot requests (concurrent/futures/process.py's call queue is max_workers + EXTRA_QUEUED_CALLS == 2 deep, so a second sibling is already RUNNING/uncancellable the moment it's submitted -- a third was the candidate for a genuinely-PENDING, cancellable sibling). Empirically, with cancel_futures=True temporarily restored, the THIRD sibling also raised BrokenProcessPool, never CancelledError, across 5 runs -- reported per instruction rather than tuned further. recreate_for's comment stated this observation and the call-queue mechanism (with process.py line numbers) instead of the prior comment's untested CancelledError claim."
  - "Coordinator follow-up 2: extended to FOUR same-slot requests. With request 1 already dequeued into the busy worker, the 2-deep call queue exactly swallows requests 2 and 3 (both RUNNING); the FOURTH is the first request that can still be genuinely PENDING in work_ids_queue -- and reachable in production, since MAX_QUEUED_BUILDS admits 4 builds and D-07 affinity can route all four to one hash slot. Empirically, with cancel_futures=True temporarily restored, the fourth request raised asyncio.CancelledError in every one of 5 runs (second and third stayed BrokenProcessPool). Test renamed to test_four_same_slot_requests_all_refuse_without_cancellation; recreate_for's comment and the test's docstring now carry this observation with the same process.py line references."
  - "The sweep's ceiling (8g) reuses the exact value a prior session already hand-applied and confirmed sufficient for this same corpus (bench/RESULTS.md's Memory section), rather than picking a new number."
  - "The capping tolerance (1%) is justified from the two capped rows already on record, which read the cap exactly (2048.0 MiB at a 2g limit) -- a small fraction absorbs docker stats' own one-decimal-MiB rounding without risking a false positive on a real peak."

requirements-completed: []

coverage:
  - id: D1
    description: "Every same-slot request queued behind a timed-out sibling is refused with a documented 503 (pool_broken), never an escaped BaseException -- proven with FOUR same-slot siblings (the minimum that reaches a genuinely-PENDING, cancellable future in CPython's 2-deep call queue), per the coordinator's two call-queue-depth follow-ups"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_four_same_slot_requests_all_refuse_without_cancellation"
        status: pass
    human_judgment: false
  - id: D2
    description: "One worker-death incident observed by two same-slot requests replaces the worker exactly once (pool.replaced +1, not +2)"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_two_same_slot_deaths_from_one_incident_replace_the_worker_once"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench.memory sweep runs each N under its own ceiling, independent of compose.yaml's mem_limit, and a row hitting that ceiling is refused rather than reported as a peak"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_a_peak_equal_to_the_ceiling_is_capped"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_a_peak_well_below_the_ceiling_is_not_capped"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_tolerance_boundary_is_pinned_from_both_sides"
        status: pass
      - kind: other
        ref: "docker inspect --format '{{.HostConfig.Memory}}' on a container started via the new override -- observed 8589934592 (this session, before commit)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-09-24
status: complete
---

# Phase quick/260924-bv5 Plan 01: Close CR-01/WR-01/CR-02 Summary

**One worker incident now replaces one worker exactly once and a queued sibling reaches the client as a documented 503; `bench.memory sweep` measures under a ceiling of its own instead of the one it exists to determine.**

## Performance

- **Duration:** ~95 min (including the coordinator's two follow-ups)
- **Tasks:** 2 (plus two coordinator-requested follow-up commits)
- **Files modified:** 8 total (6 modified across the two tasks + 1 created, plus 2 of those files touched again by both follow-ups: `src/spur/pool.py`, `tests/test_pool.py`)

## Accomplishments

- `BuildPool.recreate_for` now takes the executor the failing request actually used and no-ops when the hash slot has already moved on -- a same-slot incident observed by N requests (D-07 affinity) now replaces the worker exactly once, not N times.
- The discarded executor is shut down without `cancel_futures=True`; a queued sibling's future is left pending so CPython's own `_ExecutorManagerThread._terminate_broken` fails it with `BrokenProcessPool` -- the exception `app.py` already maps to a 503 `pool_broken` -- instead of an `asyncio.CancelledError` no handler between there and the client catches.
- `bench.memory sweep` now applies its own 8g ceiling through the same override mechanism `confirm()` already used, and refuses (rather than reports) a row whose sampled peak reaches it.
- Follow-up 1 (coordinator-requested): the queued-sibling test extended to THREE same-slot requests, and `recreate_for`'s comment stated the actual CPython call-queue mechanism and this session's empirical observation, in place of an earlier, untested claim about which exception a cancelled sibling would raise.
- Follow-up 2 (coordinator-requested): extended again to FOUR same-slot requests -- the minimum needed to actually reach a genuinely-PENDING future in CPython's 2-deep call queue and observe `asyncio.CancelledError` pre-fix. `recreate_for`'s comment and the test (renamed `test_four_same_slot_requests_all_refuse_without_cancellation`) now carry that confirmed observation.

## Task Commits

Each task was committed atomically:

1. **Task 1: one worker incident, one replacement, one documented 503 (CR-01 + WR-01)** - `17048c9` (fix)
2. **Task 2: the memory sweep measures under its own ceiling, and refuses a row that hits it (CR-02)** - `d334049` (fix)
3. **Follow-up 1: prove the cancelled-sibling path with a third same-slot request** - `08697f0` (fix)
4. **Follow-up 2: observe the cancelled fourth same-slot request pre-fix** - `15fa5cd` (fix)

## Files Created/Modified

- `src/spur/pool.py` - `recreate_for(p, executor)` gains an identity guard and drops `cancel_futures=True`; both call sites in `_run_with_timeout` pass their already-held `executor`. Follow-ups: the comment on the `cancel_futures=True` removal was rewritten twice, ending with the call-queue mechanism (process.py line numbers) and the confirmed fourth-request `asyncio.CancelledError` observation, not the original comment's untested prediction.
- `src/spur/app.py` - the `pool_broken` `HTTPException` message widened to cover a worker terminated by this service, not only one that died on its own.
- `tests/test_pool.py` - two new tests: a same-slot request queued behind a timed-out sibling, and two same-slot requests that both lose their worker to a hard process death. Follow-ups: the queued-sibling test extended from two to three to four same-slot requests, and renamed to `test_four_same_slot_requests_all_refuse_without_cancellation`.
- `docs/architecture/http-api.md` - the `pool_broken` bullet widened to match `app.py`'s new wording, and notes the once-per-incident replacement fix.
- `bench/memory.py` - `_SWEEP_MEM_LIMIT_BYTES` (8g), `_CAP_TOLERANCE_FRACTION` (1%) and `_is_capped()`; `_sweep_one` now starts each N under the ceiling via `_write_mem_limit_override` and returns a capped row (no peak) when a sample reaches it.
- `tests/test_bench.py` (new) - pins `_is_capped` at the cap, well under it (real N=1/N=2 numbers from `bench/RESULTS.md`), and on both sides of the tolerance boundary.
- `bench/README.md` - one sentence: `sweep` runs under its own ceiling, independent of `compose.yaml`'s `mem_limit`, and a capped row reports no peak.
- `compose.yaml` - the `mem_limit` comment's re-measurement clause now says the sweep runs under its own ceiling, not this one.

## Decisions Made

**CR-01 route: primary, not fallback.** Per the plan's instruction, the queued-sibling test (`tests/test_pool.py::test_a_queued_sibling_is_refused_not_cancelled`) was written and run against the *unmodified* `src/spur/pool.py` first, six times (once during initial authoring, five more as a determinism check). Every run produced the identical result: both `isinstance(second_result, BrokenProcessPool)` and `not isinstance(second_result, asyncio.CancelledError)` held true even pre-fix -- the queued sibling never actually escaped as a raw cancellation in this environment. What failed, every time, was `pool.replaced == replaced_before + 1` (actual: `2`). This is WR-01's double-recreate bug, reliably reproduced; CR-01's specific cancellation-escape did not reproduce on this machine/kernel (hard_fact_1's own framing already anticipated this could go either way, as a race between the process-pool manager thread's own broken-worker detection and `shutdown(cancel_futures=True)`'s cancellation). Because cancellation was never observed reaching the caller, the plan's fallback (a new error class, a fifth `detail[0].type`) was not needed and was not added. `detail[0].type`'s closed set stays exactly `build_error`/`timeout`/`pool_broken`/`busy` -- unchanged, confirmed by the two existing closed-set tests still passing.

**Same fix serves both findings.** The identity guard in `recreate_for` is what actually fixes WR-01 (verified: `pool.replaced` now rises by exactly 1 in both new tests), and removing `cancel_futures=True` is what makes the queued-sibling path deterministically `BrokenProcessPool` going forward rather than depending on the same race that happened to favor `BrokenProcessPool` in every observed pre-fix run -- it removes the alternate (cancellation) outcome as a possibility rather than merely never having hit it yet.

**Sweep ceiling value: reused, not re-derived.** `_SWEEP_MEM_LIMIT_BYTES = 8 * 1024**3` (8g) is the exact value `bench/RESULTS.md`'s Memory section already records a prior session hand-applying and confirming sufficient for the same 40-gear corpus (0 of 120 requests failed across N=1/2/4, all three peaks landing well under it). No new measurement was taken; this task wires that already-proven value into the harness itself so it no longer needs to be applied by hand.

**Capping tolerance: 1%, justified from the record.** The two rows on file that actually hit a cap (`bench/RESULTS.md`'s first sweep attempt, before the fix) read the limit exactly -- `2048.0 MiB` against a then-shipped `mem_limit: 2g`. A 1% tolerance is small enough to reject any of the honest peaks already on record (N=1 2052.1 MiB, N=2 2878.5 MiB, N=4 4731.9 MiB, all far below 1% of 8g's ~85.9 MiB band) while absorbing `docker stats`' own one-decimal-MiB display rounding.

**Follow-up 1: CR-01's queued-sibling test needed three requests, not two, and the pre-fix comment overstated what was observed.** The coordinator identified, from reading CPython's `concurrent/futures/process.py` (3.12.13) directly, that a single-worker executor's call queue is `max_workers + EXTRA_QUEUED_CALLS == 2` items deep (line 118), and `add_call_item_to_queue` marks each item it pulls into that queue RUNNING (line 404, `future.set_running_or_notify_cancel()`) *before* any worker has touched it -- meaning a *second* same-slot sibling is already uncancellable the instant it's submitted, so the original two-request test could never actually exercise `cancel_futures=True`'s cancellation path at all. A third same-slot sibling was the candidate for a genuinely PENDING, cancellable future. Verified this session: even with `cancel_futures=True` temporarily restored, the third sibling *also* raised `BrokenProcessPool`, never `asyncio.CancelledError`, across 5 runs -- because both extra siblings in this test's design are created back-to-back in one asyncio tick (no `await` between them), so the manager thread's single, uninterrupted fill loop drains *both* into the 2-deep call queue as RUNNING before `recreate_for`'s `shutdown()` call ever executes. Per the coordinator's explicit instruction, this was reported rather than used as a reason to add a fourth sibling or otherwise tune the test until `CancelledError` appeared.

**Follow-up 2: a fourth same-slot request is where the genuinely-PENDING future actually lives, and it confirmed the prediction.** The coordinator's own math closed the loop: request 1 sits in the (single, busy) worker, having already been dequeued from the call queue; the 2-deep call queue is then exactly big enough to also swallow requests 2 and 3, both RUNNING; request 4 is the first one that can still be sitting in `work_ids_queue`, genuinely PENDING, when the incident is handled -- and this is reachable in production, not just a test artifact, since `MAX_QUEUED_BUILDS` admits 4 builds and D-07 affinity can route all four to one hash slot. The test was extended to four same-slot requests (second, third and fourth all created back-to-back after the one 0.5s gap, no extra `await asyncio.sleep(0)` needed or added). Verified this session, 5 runs with `cancel_futures=True` temporarily restored, `git diff` confirmed clean afterward: the second and third requests again raised `BrokenProcessPool` in every run (matching Follow-up 1's finding), but the **fourth raised `asyncio.CancelledError` in every one of 5 runs** -- `asyncio.gather(..., return_exceptions=True)` returns the `CancelledError` instance directly in the results list rather than raising it out of `gather` itself, so the test's `isinstance` assertions observe it the same way as any other exception type. Post-fix (no `cancel_futures=True`, the actual shipped code), all four runs of the four-request probe gave the same deterministic result as the three-request version: second, third and fourth all `BrokenProcessPool`, `pool.replaced == +1`. The test was renamed `test_four_same_slot_requests_all_refuse_without_cancellation` since "queued sibling" (singular) no longer described what it drives, and `recreate_for`'s comment was rewritten a second time to state this fully-confirmed mechanism and observation, replacing Follow-up 1's comment (which had correctly described the call-queue depth but had left open whether a genuinely-PENDING sibling would actually raise `CancelledError`). The fix itself (dropping `cancel_futures=True` unconditionally) is, again, unchanged by this round -- only the test's coverage and the comment's evidentiary basis are now complete.

## Deviations from Plan

None - plan executed exactly as written, including the primary (non-fallback) CR-01 route the pre-fix tests' own evidence pointed to.

## Issues Encountered

None.

## Verification Evidence

- **CR-01 pre-fix observation (original, two-request test):** `tests/test_pool.py::test_a_queued_sibling_is_refused_not_cancelled`, run against unmodified `src/spur/pool.py`, six times: all six runs failed on `assert pool.replaced == replaced_before + 1` (`2 == (0 + 1)`); the exception-type assertions (`isinstance(second_result, BrokenProcessPool)`, `not isinstance(second_result, asyncio.CancelledError)`) passed in every run. Post-fix: all pass, `pool.replaced` rises by exactly 1.
- **WR-01 pre-fix observation:** `tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`, run against unmodified `src/spur/pool.py`: failed identically, `2 == (0 + 1)`. Post-fix: passes.
- **`docker inspect` observation (CR-02):** a throwaway container (`spur-bench-inspect`, no `--service-ports`, port 8000 left held by `spur-spur-1`) started via `docker compose -f compose.yaml -f <override>` with the override's `mem_limit: 8589934592b` read back via `docker inspect --format '{{.HostConfig.Memory}}'` as **`8589934592`** -- exactly `_SWEEP_MEM_LIMIT_BYTES`, and distinct from `compose.yaml`'s shipped **`4294967296`** (4g). Container removed immediately after (`docker rm -f`); `bench/RESULTS.md` untouched; the 40-gear sweep itself was not re-run.
- **Follow-up 1: third-request observation (both pre- and post-fix).** A standalone throwaway probe script (three same-slot `_sleep_past_timeout` requests through `pool._run_with_timeout`, matching the eventual test) was run 5 times against the post-fix `recreate_for` (no `cancel_futures=True`, identity guard active): every run gave `first=BuildTimeout`, `second=BrokenProcessPool`, `third=BrokenProcessPool`, `pool.replaced == 1`. `recreate_for`'s `shutdown()` call was then temporarily edited back to `shutdown(wait=False, cancel_futures=True)` (identity guard left in place) and the same probe run 5 more times: **identical result every time** -- `second=BrokenProcessPool`, `third=BrokenProcessPool`, neither ever `asyncio.CancelledError`, `pool.replaced == 1`. The line was restored immediately after (`git diff src/spur/pool.py` confirmed empty before proceeding). **Pre-fix exception type observed for the third request: `BrokenProcessPool`, never `asyncio.CancelledError`, in every one of 5 runs with `cancel_futures=True` restored.**
- **Follow-up 2: fourth-request observation (both pre- and post-fix).** A second standalone throwaway probe script, identical to Follow-up 1's but with a fourth same-slot request added (created back-to-back with second and third, same asyncio tick, no extra `sleep(0)`), was run 3 times against the post-fix code: every run gave `first=BuildTimeout`, `second=BrokenProcessPool`, `third=BrokenProcessPool`, `fourth=BrokenProcessPool`, `pool.replaced == 1`. `recreate_for`'s `shutdown()` call was again temporarily edited to `cancel_futures=True` and the probe run 5 more times: **`second=BrokenProcessPool`, `third=BrokenProcessPool`, `fourth=CancelledError`, every single run.** The line was restored immediately after (`git diff src/spur/pool.py` confirmed empty). **Pre-fix exception type observed for the fourth request: `asyncio.CancelledError`, in every one of 5 runs with `cancel_futures=True` restored** -- the first request in this whole investigation to actually demonstrate CR-01's originally-predicted escape path. The committed test (`tests/test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation`) was then run 3 times against the final, committed (post-fix) code: all 3 passed, confirming all four requests deterministically surface `BrokenProcessPool` with no `cancel_futures=True` in play.
- `make verify` at all four commits: green (`17048c9`: 74 tests; `d334049`: 76 tests; `08697f0`: 76 tests, one test extended; `15fa5cd`: 76 tests, same test extended again and renamed -- ruff, mypy `--strict`, the four import-linter contracts, `no-fake-done`, pytest, all passing under the pre-commit hook with no bypass).
- Final run this session: `.venv/bin/python -m pytest tests/test_pool.py tests/test_bench.py -q` -> **19 passed**. `make verify` (final, at `15fa5cd`) -> ruff clean, mypy `Success: no issues found in 20 source files`, 4/4 import contracts kept, pytest **76 passed in 29.11s**.
- `git status --short bench/RESULTS.md .planning/`: no modification to `bench/RESULTS.md`, no staged `.planning` files (session's untracked `.planning/quick/...`, `.planning/config.json`, `.planning/milestone.lock`, `.planning/state.json` and `.gsd/` left untouched, per the execution constraints). Both follow-up commits touched only `src/spur/pool.py` and `tests/test_pool.py` -- no bench files, no `.planning/` beyond this SUMMARY.
- No throwaway Docker containers left behind (`docker ps -a --filter name=spur-bench` empty); `spur-spur-1` left running, `127.0.0.1:8000` untouched. Both follow-ups' throwaway probe scripts used no Docker.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `02-REVIEW.md`'s three open findings (CR-01, CR-02, WR-01) are all closed by this task's four commits, with CR-01's originally-predicted cancellation-escape now fully confirmed (fourth same-slot request, pre-fix) rather than merely inferred from source. No further action needed to fix them; `02-REVIEW.md` itself was not modified (out of scope per the execution constraints) -- whoever owns Phase 2's verification status can now mark these findings resolved against `17048c9`/`d334049`/`08697f0`/`15fa5cd`.
- No new tech debt was filed: every step of both tasks was completed as specified, nothing deferred. Both coordinator follow-ups strengthened evidence and comments rather than uncovering new deferred work, and the second follow-up closed the one open question the first left behind (what a genuinely-PENDING same-slot future actually raises under `cancel_futures=True`).

---
*Phase: quick/260924-bv5*
*Completed: 2026-09-24*

## Self-Check: PASSED

All 8 modified/created source files present on disk; all four commits (`17048c9`,
`d334049`, `08697f0`, `15fa5cd`) present in `git log`.
