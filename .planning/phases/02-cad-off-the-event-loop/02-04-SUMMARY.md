---
phase: 02-cad-off-the-event-loop
plan: 04
subsystem: infra
tags: [docker, compose, bench, mypy, multiprocessing, asgi-lifespan]

# Dependency graph
requires:
  - phase: 02-cad-off-the-event-loop
    provides: "02-01's pool topology (BuildPool, SPUR_BUILD_WORKERS, affinity routing),
      02-02's committed bench/ harness (deliberately not yet exercised for real), and
      02-03's timeout/failure-mapping/health-pool-fields -- this plan runs the harness
      against that real topology for the first time and sets four knobs from the result."
provides:
  - "bench/RESULTS.md: the committed, re-runnable measurement record -- machine facts,
    both of the debt file's load scenarios (run twice each), and the N=1,2,4 memory
    sweep plus a confirm run, over the real multi-process topology."
  - "SPUR_BUILD_TIMEOUT's shipped default (30s) set from the worst build actually
    observed (7.39s), replacing Plan 02-03's provisional placeholder."
  - "compose.yaml's mem_limit (4g) set from a real, uncapped sweep of the N=2 shipping
    default's peak (2878.5 MiB) x a named 1.3 headroom, confirmed with zero failures
    over the same 40-gear corpus L07's 2g was earned against."
  - "compose.yaml's SPUR_WORKERS: \"1\" / SPUR_BUILD_WORKERS: \"2\" (D-01, D-19) --  one
    server process, a fixed two-worker build pool sized from the per-N table, not
    os.cpu_count()."
  - "max_tasks_per_child left off (src/spur/pool.py), with the drift evidence and its
    corpus-ordering caveat recorded in the comment (D-11)."
  - "README.md and docs/architecture/packaging.md brought current for the new topology."
  - "A working docker build/compose flow for this topology: two pre-existing bugs in
    docker/smoke.py (lifespan never run; unguarded spawn recursion) fixed, both of which
    would have broken the first real image rebuild or CI run of this code, not just this
    plan's own memory sweep."
affects: [02-05]

# Actuals (#2632)
actuals:
  tokens: 8672     # chars/4 over b0ac042..HEAD, .planning excluded
  tasks: 3          # Task 1 was the resolved environment checkpoint (no code); Tasks 2-4 committed
  commits: 3
  plan_head_before: b0ac042

# Tech tracking
tech-stack:
  added: []   # stdlib + existing deps only
  patterns:
    - "Docker build-time smoke tests that exercise an ASGI app with a real lifespan
      (worker pools, DB pools, etc.) must drive `app.router.lifespan_context(app)`
      explicitly -- a bare `await app(scope, receive, send)` never runs FastAPI/Starlette
      lifespan handlers on its own."
    - "A script that may trigger `multiprocessing` spawn (directly or via a library)
      must guard its own entry point with `if __name__ == \"__main__\":` -- spawn
      re-imports the __main__ module in the child, and an unguarded module-level call
      recurses."
    - "A memory sweep must run with the resource limit it exists to set relaxed or
      removed, never the pre-existing (soon-to-be-superseded) limit -- otherwise the
      sweep measures the old ceiling capping the new topology, not the new topology's
      real footprint."
    - "A repeated (not single-shot) measurement, reported transparently with its
      run-to-run variance, is more honest than a single sample presented as definitive
      -- especially near a pass/fail boundary on noise-sensitive (sub-millisecond)
      absolute figures."

key-files:
  created:
    - bench/RESULTS.md
  modified:
    - bench/latency.py
    - bench/memory.py
    - src/spur/app.py
    - src/spur/pool.py
    - compose.yaml
    - docker/smoke.py
    - README.md
    - docs/architecture/packaging.md

key-decisions:
  - "SPUR_BUILD_TIMEOUT default: 30s, ~4x the worst build actually observed (7.39s,
    concurrent scenario), for margin on hardware slower than the measurement machine
    (the debt file's own stated concern)."
  - "mem_limit: 4g, from the N=2 shipping default's measured, uncapped peak (2878.5 MiB)
    x a named 1.3 (30%) headroom, rounded up, confirmed at zero failures over the
    40-gear corpus."
  - "max_tasks_per_child stays off: the sweep's early/late split shows growth at N=2/N=4,
    but bench/corpus.py's corpus is strictly ascending tooth count, so the growth is
    explained by the bounded 4-entry solid cache holding progressively larger solids as
    the corpus advances, not by an unflattened leak. No run showed unbounded growth, a
    rising failure rate, or a rising elapsed time."
  - "The concurrent latency scenario's pass bar (under-load p95 <= 2x idle p95) is NOT
    demonstrated met on this measurement session (2.02x, then 2.45x on a repeat run) --
    recorded as a finding, not tuned into a pass, per the plan's own instruction. See
    'Issues Encountered' below; this is the most consequential outcome of this plan."

requirements-completed: [REQ-cad-off-event-loop, REQ-measured-memory-ceiling]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Both of the debt file's load scenarios (single, concurrent) re-run
      against the real topology, with idle/under-load p95, ratio, sample counts and the
      slowest build recorded in bench/RESULTS.md."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "make bench.latency (bench/latency.py) against a host `spur serve`, run
          twice this session; output captured verbatim in bench/RESULTS.md's Latency
          section"
        status: fail
    human_judgment: true
    rationale: "The `single` scenario clears the 2x pass bar comfortably on both runs
      (1.12x, 1.18x). The `concurrent` scenario does not (2.02x, then 2.45x) -- status
      is `fail` for the scenario as a whole rather than a partial pass, and a human must
      decide whether the caveated environment (host not fully idle) sufficiently
      explains it or whether a clean re-run on a genuinely idle host is required before
      REQ-cad-off-event-loop's acceptance clause can be considered met."
  - id: D2
    description: "SPUR_BUILD_TIMEOUT's shipped default is set above the worst build
      actually observed, with the observation and margin named in the comment."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "src/spur/app.py's int_env(\"SPUR_BUILD_TIMEOUT\", 30) comment; worst
          observed build (7.39s) recorded in bench/RESULTS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "The N=1,2,4 memory ceiling is measured (not derived from L07's
      per-process figures) over the real topology, uncapped by any pre-existing limit,
      with early/late peaks recorded for the D-11 drift question."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.memory sweep, this session, against a freshly
          rebuilt image; bench/RESULTS.md's Memory section (three sweep attempts
          documented, including the two blocking issues found and fixed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "mem_limit (4g) is confirmed by re-running the full 40-gear corpus at
      that value with zero failures -- the same bar 2g cleared and 1g did not."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.memory confirm 4g, this session: 0 of 40
          requests failed; bench/RESULTS.md's confirm section"
        status: pass
    human_judgment: false
  - id: D5
    description: "compose.yaml ships the measured knobs (SPUR_WORKERS: \"1\",
      SPUR_BUILD_WORKERS: \"2\", mem_limit: 4g) and docker compose config renders them."
    requirement: "REQ-measured-memory-ceiling"
    verification:
      - kind: other
        ref: "docker compose config, this session: renders SPUR_WORKERS=1,
          SPUR_BUILD_WORKERS=2, mem_limit=4294967296 (4g)"
        status: pass
    human_judgment: false
  - id: D6
    description: "README.md and docs/architecture/packaging.md describe the shipped
      service (worker-process builds, timeout+503 behaviour, the new memory formula),
      not the one this phase replaced."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: other
        ref: "grep -nE 'SPUR_BUILD_WORKERS|SPUR_BUILD_TIMEOUT' README.md (2+ hits);
          grep -n bench docs/architecture/packaging.md; both this session"
        status: pass
      - kind: manual_procedural
        ref: "Read both documents end-to-end this session; no sentence still promises
          the retired single-process stall behaviour"
        status: pass
    human_judgment: false

duration: ~2h (continuation session; Task 1's checkpoint was answered by the human
  before this continuation started)
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 4: Measure, Then Set the Knobs Summary

Both of the debt file's load scenarios and a real, uncapped N=1/2/4 memory sweep now run
against the actual multi-process topology, producing `bench/RESULTS.md` and four
measured knobs (`SPUR_BUILD_TIMEOUT=30s`, `mem_limit=4g`, `SPUR_BUILD_WORKERS=2`,
`max_tasks_per_child` off) -- but the concurrent latency scenario's pass bar was not
demonstrated met on this session's host (2.02x, then 2.45x against a <=2.00x bar),
recorded as a finding rather than tuned into a pass.

## Performance

- **Duration:** ~2h active work this continuation (host latency runs, two failed sweep
  attempts diagnosed and fixed, three full memory sweeps, one confirm run, docs)
- **Tasks:** 3 completed this continuation (Task 1, the environment checkpoint, was
  already resolved by the human before this session started)
- **Files changed:** 9 (1 created, 8 modified)

## Accomplishments

- `bench/RESULTS.md` is now the committed, re-runnable evidence for both of Phase 2's
  success criteria: machine facts, the `single`/`concurrent` latency scenarios (each run
  twice), and the N=1,2,4 memory sweep with an early/late drift split, plus a `4g`
  confirm run at zero failures.
- `SPUR_BUILD_TIMEOUT` (30s) and `mem_limit` (4g) are both set from real observations,
  with the observation and margin named in the comment above each -- replacing Plan
  02-03's provisional placeholder and the old, now-superseded `2g`.
- `compose.yaml` ships the real topology: one server process (`SPUR_WORKERS: "1"`), a
  fixed two-worker build pool (`SPUR_BUILD_WORKERS: "2"`, justified by the per-N table
  rather than `cpu_count`, D-19), and the measured `mem_limit`.
- `max_tasks_per_child` stays off, with the sweep's early/late numbers and the
  corpus-ordering reasoning that explains them (rather than assuming a leak) recorded in
  `src/spur/pool.py`'s comment.
- README.md and `docs/architecture/packaging.md` describe the service that actually
  shipped: worker-process builds, a per-build timeout with `503`+`Retry-After`, the new
  memory formula, and `make bench` as a sibling of the gate.
- Two real bugs found and fixed along the way (see "Deviations"): `bench/latency.py`
  crashed on an expected admission-control refusal; `docker/smoke.py` couldn't build the
  image at all against the new pool topology (two separate, layered bugs).

## Task Commits

1. **Task 1: Establish the measurement environment before any number exists** -
   resolved by the human (`quiet`) before this continuation session began; no commit
   (checkpoint:human-action).
2. **Task 2: Re-run both load scenarios, and set the timeout above what was observed** -
   `d98fc62` (feat)
3. **Task 3: Sweep the real topology's memory, and earn mem_limit the way 2g was
   earned** - `c20f51c` (feat)
4. **Task 4: Make the user-facing runtime documentation true again** - `a01e3e4` (docs)

**Plan metadata:** commit follows this summary.

## Files Created/Modified

- `bench/RESULTS.md` (new) - the committed measurement record: `## Machine`,
  `## Latency` (both scenarios, both runs, the environment caveat), `## Memory` (sweep
  table, drift analysis, formula discussion, confirm run, the two blocking issues found
  and fixed).
- `bench/latency.py` - `_build()` now treats a `503` admission-control refusal as
  expected (returns `None`) instead of crashing the scenario; `ScenarioResult` gained
  `attempted`/`refused` fields, surfaced in the report.
- `bench/memory.py` - `SweepRow`/`_sweep_table_markdown` gained an early/late peak split
  per N (D-11 drift check), which the harness as committed by Plan 02-02 didn't capture.
- `src/spur/app.py` - `SPUR_BUILD_TIMEOUT`'s provisional comment (Plan 02-03) replaced
  with the measured default and its observation.
- `src/spur/pool.py` - comment on `BuildPool.__init__` recording the `max_tasks_per_child`
  decision and the drift numbers/reasoning behind it.
- `compose.yaml` - `SPUR_WORKERS: "1"`, new `SPUR_BUILD_WORKERS: "2"`, `mem_limit: 4g`,
  with the comment above `mem_limit` fully rewritten (no superseded claims survive).
- `docker/smoke.py` - drives `app.router.lifespan_context(app)` explicitly so the build
  pool actually starts before the smoke test's requests; `anyio.run(main)` now guarded
  by `if __name__ == "__main__":` to avoid a `spawn`-multiprocessing recursion.
- `README.md` - environment table gains `SPUR_BUILD_WORKERS`/`SPUR_BUILD_TIMEOUT`,
  corrects four existing rows' descriptions for the new topology, rewrites the
  memory-ceiling and behaviour-under-load paragraphs.
- `docs/architecture/packaging.md` - documents the two `docker/smoke.py` fixes, the new
  `compose.yaml` shape, `make bench` as a gate sibling (D-16), and the per-build-worker
  scope of the `malloc_trim` known gap.

## Decisions Made

See `key-decisions` in the frontmatter. The most consequential: the concurrent latency
scenario's pass bar was not met on this session, and that finding is recorded rather
than resolved -- see "Issues Encountered" below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `bench/latency.py`'s concurrent scenario crashed on an expected
admission-control refusal**
- **Found during:** Task 2, first `make bench.latency` run against the host service.
- **Issue:** `_build()` called `response.raise_for_status()` unconditionally.
  `MAX_QUEUED_BUILDS` is 4 at the shipping default and the concurrent scenario
  deliberately fires 10 requests at once, so several are expected to be refused with
  `503` -- exactly the pre-existing admission-control behaviour
  `docs/plan-2026-09-21.md`'s own outcome table already documents ("6 of 10 refused").
  The unhandled `HTTPStatusError` crashed the whole scenario on the first refusal.
- **Fix:** `_build()` now returns `None` for a `503` instead of raising; callers filter
  refused builds out of the "slowest build" computation and report the refused count
  explicitly in the markdown report.
- **Files modified:** `bench/latency.py`
- **Verification:** `make verify` green; ran the fixed harness against a live host
  service, confirmed sensible output on both scenarios.
- **Committed in:** `d98fc62`

**2. [Rule 3 - Blocking issue] The pre-existing `mem_limit: 2g` was capping the sweep it
was supposed to be replaced by**
- **Found during:** Task 3, first full `bench.memory sweep` run.
- **Issue:** N=2 and N=4 both landed on exactly `2048.0 MiB` (the old `2g` limit itself,
  not a real footprint), with N=4 additionally failing 2 of 40 requests to OOM pressure
  at that cap. A sweep constrained by the value it exists to replace cannot produce an
  honest measurement of that value.
- **Fix:** `mem_limit` temporarily raised to `8g` for the sweep (documented in-line in
  the compose file at the time, replaced with the real value once data was in hand); the
  sweep re-run twice more (once to get uncapped data, once more after the harness fix
  below) for a clean, consistent dataset.
- **Files modified:** `compose.yaml` (temporary, then final value)
- **Verification:** re-run sweep showed zero failures and no round-number capping at any
  N; `bench/RESULTS.md` documents both the capped and uncapped attempts for the record.
- **Committed in:** `c20f51c`

**3. [Rule 3 - Blocking issue] `docker compose build` failed entirely against the new
pool topology (two layered bugs)**
- **Found during:** Task 3, rebuilding the (45-hour-stale) image before the sweep.
- **Issue:** `docker/smoke.py` calls the ASGI app directly
  (`await app(scope, receive, send)`), which never runs `app.py`'s `lifespan` -- so
  `app.state.pool` was never set and `build_backend()` hard-failed by design
  (02-01-SUMMARY.md). Fixing that (driving the lifespan explicitly) surfaced a second,
  previously-masked bug: the script's unguarded module-level `anyio.run(main)` recursed
  once a build actually tried to spawn a worker process, because `spawn` re-imports the
  calling module as `__main__` in the child.
- **Fix:** `docker/smoke.py` now enters `async with app.router.lifespan_context(app):`
  around its requests, and its `anyio.run(main)` call is guarded by
  `if __name__ == "__main__":`.
- **Files modified:** `docker/smoke.py`
- **Verification:** `.venv/bin/python docker/smoke.py` passes locally; `docker compose
  build` succeeds end to end (smoke test runs inside the build); `make verify` green.
- **Committed in:** `c20f51c`

**4. [Rule 2 - Missing critical functionality] `bench/memory.py`'s sweep couldn't answer
the D-11 drift question**
- **Found during:** Task 3, while writing the `## Memory` section -- the plan's
  acceptance criteria require recording whether resident memory drifted upward across
  the corpus at any N, but the harness as committed by Plan 02-02 only ever tracked a
  single overall peak per N, with no way to distinguish "climbed once early and stayed
  there" from "kept climbing".
- **Fix:** `SweepRow` and the markdown table gained an early-half/late-half peak split.
- **Files modified:** `bench/memory.py`
- **Verification:** `make verify` green (mypy --strict, ruff); re-ran the full sweep to
  populate the new columns, then used them to write the drift analysis in
  `bench/RESULTS.md`.
- **Committed in:** `c20f51c`

---

**Total deviations:** 4 auto-fixed (1 Rule 1, 2 Rule 3, 1 Rule 2). **Impact:** all four
are necessary corrections to the measurement path itself, discovered exactly because
this was the harness's first real run against a live service and a live Docker daemon
(as Plan 02-02's own SUMMARY anticipated). None represent scope creep -- each was a
precondition for producing an honest number this plan's own acceptance criteria require.

## Issues Encountered

**The concurrent latency scenario's pass bar (under-load p95 <= 2x idle p95) is not
demonstrated met on this measurement session.** Two runs gave 2.02x and 2.45x
(deteriorating, not improving, on the repeat). The `single` scenario -- the debt file's
own headline numbers (0.22s -> 0.76s -> 2.00s) -- clears the bar comfortably on both runs
(1.12x, 1.18x). Both absolute figures involved are sub-millisecond (0.6ms idle, 1.2-1.5ms
under load), and the host was documented at Task 1 re-check as not fully idle (load
average 2.3-2.7 on this 12-core machine, above the >1.5 threshold the plan itself names,
with this session's own `claude` process among the contributors). Per the plan's explicit
instruction ("do not adjust the bar and do not adjust the corpus... record the numbers as
measured, state that the criterion was not met"), this is recorded as a finding in
`bench/RESULTS.md` rather than resolved. **This plan does not claim
`REQ-cad-off-event-loop`'s latency acceptance clause is fully demonstrated met** --
see "Next Phase Readiness" below.

All other verification passed cleanly: `make verify` green after every task; `docker
compose config` renders the correct knobs; the memory confirm run cleared zero failures
on the first attempt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`REQ-measured-memory-ceiling`'s acceptance is fully satisfied by this plan's evidence:
the ceiling is measured (not derived from L07's per-process figures), confirmed at zero
failures over the same corpus, and every number in `compose.yaml` carries its
measurement.

`REQ-cad-off-event-loop`'s acceptance is **partially** satisfied: `SPUR_BUILD_TIMEOUT` is
measured and set, and the `single` scenario clears its pass bar -- but the `concurrent`
scenario does not, on this session's host. Both `REQ-cad-off-event-loop` and
`REQ-measured-memory-ceiling` are structurally blocked from being marked `Complete` in
`.planning/REQUIREMENTS.md` regardless of this finding: `requirements.ready-ids` reports
`0/2 ready`, because Plan 02-05 (wave 4, `depends_on: ["02-04"]`) also declares both IDs
in its own frontmatter and has not yet produced a summary. **Before Plan 02-05 (or
whoever closes out `REQ-cad-off-event-loop`) marks it complete, the concurrent latency
finding above needs a decision**: re-run `bench.latency concurrent` on a genuinely idle
host to see if the ratio clears 2.00x cleanly, or make an explicit, documented judgment
call that the caveated result is acceptable evidence given the environment. This is
flagged in `STATE.md`'s Blockers/Concerns for visibility.

No other blockers. `docker compose up -d --build` was re-run at the end of this session
so the pre-existing `spur-spur-1` deployment (present before this session started) is
left running on the final, measured topology rather than down.

## Self-Check: PASSED

- All 9 files listed under `key-files` confirmed present on disk (`bench/RESULTS.md`,
  `bench/latency.py`, `bench/memory.py`, `src/spur/app.py`, `src/spur/pool.py`,
  `compose.yaml`, `docker/smoke.py`, `README.md`, `docs/architecture/packaging.md`).
- Commits `d98fc62`, `c20f51c`, `a01e3e4` all confirmed present in
  `git log --oneline --all`.
- `git rev-list --count b0ac042..HEAD` = 3, matching `actuals.commits` above
  (`plan_head_before: b0ac042`, the last commit of Plan 02-03).

---
*Phase: 02-cad-off-the-event-loop*
*Completed: 2026-09-23*
