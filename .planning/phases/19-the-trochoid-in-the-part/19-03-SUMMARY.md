---
phase: 19-the-trochoid-in-the-part
plan: 03
subsystem: testing
tags: [resource-tracker, xdist, coverage, multiprocessing, flake, tech-debt, isolation, gate]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-01's gate-baseline run 2 and its kept whole log (investigation/19-01-gate-flake.log)
provides:
  - "investigation/19-03-isolation.md: the 60 isolation loops (20 each at -n 8 --cov, -n 8 --no-cov, -n0 --cov), every loop's exit, count, load and wall time"
  - "the must-severity resource-tracker debt re-deferred with the isolation counts, the orchestrator-verified crash-report observation and a new named trigger"
affects: [19-09, 20, next-milestone-planning]

# Actuals (#2632): chars/4 over the added lines of the three files (19-03-isolation.md, the debt file, INDEX.md), f2f4f47 and 0f7c375 against plan_head_before; this SUMMARY and the STATE/ROADMAP edits are not counted. The plan's estimate was 45000; most of the plan's cost was 39 minutes of wall time in the loops, not tokens.
actuals:
  tokens: 3310
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "an isolation run that finds nothing is recorded as counts with its upper bound, and does not become a fix or a filter (L08, the debt's own Next step)"

key-files:
  created:
    - .planning/phases/19-the-trochoid-in-the-part/investigation/19-03-isolation.md
  modified:
    - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "debt-redefer (human: 'take the recommendations'; id mapped by the orchestrator from the executor's stated recommendation): no shutdown(wait=True), no filterwarnings entry; Severity must and Status active stay"
  - "New trigger: the next make verify failure with its whole log kept so the test and worker localise the fix; or, if none by Phase 20 planning or the next milestone's start, whole-suite loops of make test at -n 8 --cov and -n 8 --no-cov"

patterns-established:
  - "Isolation loops for a gate flake run the whole suite when every recorded occurrence came from a whole-suite run: the two-file loops sampled a different population"

requirements-completed: []  # REQ-trochoid-composes-and-is-priced is declared by this plan and by sibling plans with no SUMMARY yet: requirements.ready-ids returned 0/1 ready (#2388 shared-ID gate); this plan satisfies its part (the debt trigger honoured); nothing marked

coverage:
  - id: D1
    description: "The isolation the debt names was run before any course was chosen: 60 loops of tests/test_pool.py and tests/test_api.py, 20 each at -n 8 --cov, -n 8 --no-cov and -n0 --cov, each with exit status, ReentrantCallError count, load and wall time; 0 of 60 failed, none contained the chain"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: other
        ref: ".planning/phases/19-the-trochoid-in-the-part/investigation/19-03-isolation.md (Task 1's automated check printed 'isolation record present' at f2f4f47)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The disposition is the human's, made with the isolation in front of them: debt-redefer, recorded verbatim with its date and the orchestrator's mapping, with the isolation counts and a named trigger in the debt file and the INDEX row"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: other
        ref: "Task 3's automated check over docs/tech_debt (prints 'debt ledger consistent' at 0f7c375): the file is in active/ only, carries 19-03, Status: active, and the INDEX row agrees"
        status: pass
    human_judgment: true
    rationale: "Whether to re-defer rather than fix or filter is a human choice made on counts that did not reproduce the flake; automation can check that the ledger is consistent, not that the choice is right"
  - id: D3
    description: "Nothing a shared link produces moved and the gate was not silenced: no file under src/, tests/ or pyproject.toml changed (git diff af53e4f..HEAD over src, tests/regression, pyproject.toml, tests/test_pool.py is empty); no filterwarnings entry and no shutdown(wait=True) call was added"
    verification:
      - kind: other
        ref: "make verify at 0f7c375: 1034 passed in 65.97s, coverage 97.68 % (floor 96), 0 ReentrantCallError in the log"
        status: pass
    human_judgment: false

duration: "about 50 min of executor time"
completed: 2026-10-09
status: complete
plan_head_before: af53e4fe50ac0c8dbd588f57b156d3b266d3aa03
plan_head_after: 0f7c3752f3a4664db50a1522d854ab72b57aca8d
# MEASURED from the ledger: git rev-list --count plan_head_before..HEAD reads 5 because 19-02's d8abb23, b6907eb and eac8908 landed on the same branch while this plan waited at its checkpoint; the 2 below are the commits titled (19-03), counted with --grep, as 19-02 did. The docs commit that carries this SUMMARY is not in the count (19-02's convention).
commits: 2
---

# Phase 19 Plan 03: The resource-tracker isolation Summary

**60 isolation loops over the two process-spawning test files did not reproduce the resource-tracker flake in any configuration (0 of 60), so the must-severity debt was re-deferred with its counts, the human's words and a trigger that localises the failure from a whole log or, failing that, from whole-suite loops.**

## Performance

- **Duration:** about 50 min of executor time: the first executor's 60 loops ran 2026-10-08T18:11Z to 18:49Z (38 min 48 s) plus its reading and record; this continuation about 10 min (ledger edits, one `make verify` of 66.6 s). The wait at the checkpoint is not counted. The start time was not captured, so the figure is approximate.
- **Tasks:** 3 (one auto, one blocking-human decision, one auto)
- **Files modified:** 3 (`investigation/19-03-isolation.md` +145, the debt file +34, `docs/tech_debt/INDEX.md` 1 line)

## The human's answer (Task 2, 2026-10-09)

The reply, verbatim: **`take the recommendations`**. The human named no option id. The orchestrator mapped those words to `debt-redefer`, the course the first executor stated as its own recommendation at the checkpoint; the mapping is the orchestrator's, from the executor's stated recommendation, and is recorded as such. The trigger recorded is the one the first executor proposed, verbatim:

> the next `make verify` failure, with its whole log kept (as 19-01 did) so the test and worker localise the fix; or, if none by Phase 20 planning or the next milestone's start, whole-suite loops of `make test` at `-n 8 --cov` and `-n 8 --no-cov`.

## The isolation (Task 1, `f2f4f47`)

Loops interleaved A, B, C round by round (20 rounds) so the host's load drift (8.4 to 24.0 on the 1-minute average) lands on all three alike; `[tool.pytest.ini_options] filterwarnings = ["error", ...]` as committed, so a reentrant-call warning would have failed a loop exactly as it fails the gate.

| Config | Loops | Failed | Logs with `ReentrantCallError` | Load range | Loop wall s (mean / max) |
|---|---|---|---|---|---|
| A `-n 8 --cov` | 20 | 0 | 0 | 8.43 - 22.57 | 38.35 / 39 |
| B `-n 8 --no-cov` | 20 | 0 | 0 | 8.43 - 24.02 | 38.20 / 39 |
| C `-n0 --cov` | 20 | 0 | 0 | 8.84 - 24.02 | 38.35 / 39 |

All 60 read `74 passed`. The fourth line read in beside them is 19-01's gate-baseline run 2 (`make verify`, whole suite, `-n 8 --cov`, `1 failed, 1022 passed in 53.61s`): `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` on `gw0`, the same five-exception chain; whole log at `investigation/19-01-gate-flake.log`.

What the counts do and do not say: the isolation did not separate xdist from coverage's `multiprocessing` concurrency, because none of the three configurations reproduced the flake. At 0 of 20 the 95 % upper bound on a per-loop rate is about 14 % per configuration (about 5 % pooled over 60; about 3 % over 100 with 17-04's 40 silent two-file loops). All four recorded occurrences came from a whole-suite run and none from the two files alone; the local whole-suite rate is 2 in 12 (17-04 1 in 3, Phase 18 0 in 4, 19-01 1 in 5), so the two-file loops probably sample a different population from the gate.

**ASSUMPTION, not measured (flagged by the first executor, kept open):** what the whole suite adds is other test files on the same worker (`tests/test_model.py` builds with the CAD kernel, the largest share of the gate) before or around the pool tests, and the longer life of the run. The loops varied neither, so which of these matters, if either, is unknown. That is why the new trigger names whole-suite loops, not two-file ones.

## Task Commits

1. **Task 1: The 60 isolation loops, recorded** - `f2f4f47` (docs), by the first executor
2. **Task 2: The human's answer** - no commit of its own; recorded above and in the debt file's dated paragraph
3. **Task 3: Apply the answer in the debt ledger** - `0f7c375` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md and ROADMAP.md (hash in the STATE.md session line).

`commits: 2` is measured from the ledger and counts the commits titled `(19-03)`. The raw `git rev-list --count af53e4f..HEAD` reads 5 because 19-02's `d8abb23`, `b6907eb` and `eac8908` landed on the branch while this plan waited at its checkpoint; they are not this plan's and were built on, not reverted.

## Files Created/Modified

- `.planning/phases/19-the-trochoid-in-the-part/investigation/19-03-isolation.md` - the 60 loops: host, the three command lines verbatim, counts, every loop, the reading against the debt's question (created by the first executor)
- `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` - dated paragraph: the 19-01 occurrence, the isolation counts and bounds, the whole-suite observation, the orchestrator's crash-report observation, the human's words with the mapping, the new trigger; `Severity: must`, `Status: active` unchanged
- `docs/tech_debt/INDEX.md` - the row's trigger column carries the new trigger and the date

## Decisions Made

- `debt-redefer` and the trigger above (the human's, by `take the recommendations`; id mapped by the orchestrator).
- The file stays in `active/`: nothing was fixed, so nothing moves to `resolved/` (CLAUDE.md: move on fixing only).
- Orchestrator observation, verified 2026-10-09 by the orchestrator and cited, not re-measured: 12 macOS crash reports since 2026-10-08 16:46 show a pytest-xdist worker dying at interpreter exit in `BRepAlgoAPI_BuilderAlgo::~BRepAlgoAPI_BuilderAlgo()` under `Py_FinalizeEx`, after its tests had reported, so it cannot fail a test. No mechanical link to the `ReentrantCallError` chain is established; the only shared trait is that both appear in whole-suite runs only. One sentence of it is in the debt file; the orchestrator files the crash itself separately.

## Deviations from Plan

### Plan-literal items that did not apply as written

**1. The loops were interleaved A, B, C round by round, not 20 of A then 20 of B then 20 of C.** Same 20 loops per configuration; interleaving puts the host's load drift (8 to 24) on all three alike. Recorded in `19-03-isolation.md`. `f2f4f47`.

**2. Task 3's `debt-filter` and `debt-shutdown` branches, and the plan's `files_modified` entries for `pyproject.toml`, `tests/test_pool.py`, `src/spur/pool.py` and `docs/tech_debt/resolved/...`, were skipped.** They apply only to the two rejected courses. No `filterwarnings` entry and no `shutdown(wait=True)` call was added, and nothing was `git mv`d. The plan's check "after a code change `make verify` exits 0" had no code change to follow; one `make verify` was run anyway at the end (below).

**3. The INDEX row was updated, as the plan says for `debt-redefer`, and its trigger column is longer than its neighbours'.** It carries the new trigger and the re-deferral's reason in the same shape the previous re-deferral used. `0f7c375`.

**4. No `19-03-occurrence-<config>-<i>.log` files exist.** No loop contained the chain, so there is nothing to copy; `19-03-isolation.md` says so. 19-01's whole log is read in by path.

**5. The "Phase 19 planning" trigger was read at the execution of this plan, not only at planning.** The trigger fired on 19-01's baseline run 2 (a `make verify` failure) and on Phase 19 planning; both are named in the debt's dated paragraph.

---

**Total deviations:** 0 auto-fixed; 5 plan-literal items (loop order; the two rejected courses skipped; INDEX row length; no occurrence logs; trigger reading).
**Impact on plan:** none on the honesty of the counts. The debt stays open, as the human chose.

## Issues Encountered

- The isolation did not reproduce the flake, so it localised nothing: no test, no worker, no pool left to a finalizer. The debt remains `must`; CI can still turn red on its own. That is the cost of the course the human took, recorded in the debt file's "Why it matters" lineage.
- The host was not idle during the loops (1-minute load 8.4 to 24.0, other applications; 19-02 paused). None of the figures here is a timing the phase decides from.
- `make verify` at `0f7c375`: exit 0, **`1034 passed in 65.97s`**, coverage 97.68 % (floor 96), 0 `ReentrantCallError` in the log, `make verify  ... 1:06.56 total`; the 1-minute load at the end read 20.38. It did not hit the flake, so the trigger did not fire again. The log is at the session scratchpad only; it is not kept in the repo because nothing failed. This run is not added to the "2 in 12" tally above, which was counted before it.

## Known Stubs

None. No code was written.

## Threat Flags

None. A record and a debt ledger only: no network, auth, file-access or trust-boundary surface. T-19-05 (a blanket `filterwarnings` ignore hiding a real unraisable exception) is mitigated by not adding any filter; the re-deferral carries the isolation counts it rests on.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The must-severity debt's Phase 19 trigger has been honoured and re-deferred with a named trigger; it is not Phase 19's blocker. 19-09 prices the gate with the flake unfixed: if its `make verify` runs hit the chain, keep each whole log under `investigation/` (that is the new trigger firing) and do not retry silently.
- Nothing a shared link produces moved: no file under `src/`, `tests/regression/` or `pyproject.toml` changed in this plan.
- No debt or idea item was filed by this plan beyond updating the existing flake item. The orchestrator files the interpreter-exit crash separately.

## Self-Check: PASSED

- Files: `.planning/phases/19-the-trochoid-in-the-part/investigation/19-03-isolation.md`, `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` and `docs/tech_debt/INDEX.md` exist; this SUMMARY is at `.planning/phases/19-the-trochoid-in-the-part/19-03-SUMMARY.md`.
- Commits `f2f4f47` and `0f7c375` are ancestors of HEAD; `git rev-list --count --grep='(19-03)' af53e4f..HEAD` reads 2.
- The human's words, the mapped id and the date are recorded here and in the debt file's dated paragraph; the debt file is in exactly one of `active/` and `resolved/` (active), `Severity: must`, `Status: active`; `grep` of `pyproject.toml` for `reentrant|ReentrantCallError|ResourceTracker` prints nothing (no filter added).

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
