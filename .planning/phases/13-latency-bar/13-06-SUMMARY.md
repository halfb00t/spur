---
phase: 13-latency-bar
plan: 06
subsystem: testing
tags: [latency, benchmark, sc3, composed, concurrency, tech-debt]

requires:
  - phase: 13-latency-bar plan 04
    provides: "Outcome (a): the bar demonstrated on the unmodified harness (13-04's bar-3 decisive session) -- the precondition for running SC3 on a server a bar session never used (D-16)"
provides:
  - "A third, rerunnable bench/latency.py scenario (scenario_composed/run_composed/_fetch/_pool_state/RequestOutcome/ComposedRun/_composed_markdown, COMPOSED_ROWS) registered in _SCENARIOS, with its own tests; scenario_single/scenario_concurrent and the no-argument run (DEFAULT_SCENARIOS) are byte-identical to 9f26052 (D-13, D-15)"
  - "SC3's one permitted reading, recorded in bench/RESULTS.md whatever it reads (D-14, D-16): the composed worst row did not complete under ten concurrent builds in the shipped configuration -- 0 of 10 served, 6 of 10 refused, 4 of 10 admitted and all four exceeded SPUR_BUILD_TIMEOUT, two of those four via an undocumented 500"
  - "The server behaviour SC3 exposed filed as must-severity debt (D-17): docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md"
affects: [13-07]

actuals:
  tokens: 511000
  tasks: 3
  commits: 5
  plan_head_before: 420f200
  plan_head_after: PENDING

tech-stack:
  added: []
  patterns:
    - "A client-observed per-request latency table is only as good as the client surviving the run: run_composed's ThreadPoolExecutor `with` block waits for every future before the caller reads any .result(), so a single crashed request (an unhandled 500) aborts the whole tuple(...) comprehension and the harness never gets to print or persist anything -- the server's own structured records (records.py) are the fallback source of truth when the client-side one does not exist, and a SUMMARY must say so rather than compute a substitute figure from a differently-chosen boundary (L08)."
    - "D-07's hash-affinity slot assignment is not controllable from the client; a ten-distinct-key composed scenario can still land two heavy requests on the same slot by chance, and when both time out in the same incident the second caller's _run_with_timeout still holds a reference to the executor object the first caller's recreate_for already shut down -- a race the plan's own flagged ASSUMPTION predicted and SC3 measured directly."

key-files:
  created:
    - .planning/phases/13-latency-bar/investigation/sc3.status.json (+ sc3.session.log, sc3.server1.records.jsonl, sc3-run1.poller.jsonl, sc3-run1.stdout.txt (0 bytes), sc3-run1.stderr.txt)
    - docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md
  modified:
    - bench/latency.py (Task 1, prior session: scenario_composed and its support code)
    - tests/test_bench.py (Task 1, prior session)
    - .planning/phases/13-latency-bar/investigation/run_experiment.py, session.py (Task 2 harness half, prior session)
    - bench/RESULTS.md ("### Composed worst row under ten concurrent builds (Phase 13)", append-only)
    - docs/tech_debt/INDEX.md (one Active row added)

key-decisions:
  - "Human's decision at the Task 2 checkpoint, verbatim: option 1, 'record it' -- SC3's one permitted reading is recorded as it stands (aborted after every request was sent), the defect filed as debt, no retry, no src/ change. D-16 ('whatever it reads') governs; the run was not relaunched."
  - "bench/RESULTS.md's per-request accounting is sourced from sc3.server1.records.jsonl only, never fabricated into the client-side latency table the plan's template describes -- run_composed's requests tuple was never built (the generator expression raised on the second future's .result()), so no client wall-time exists for any of the ten rows; the server's build.started/queue.refused/build.failed/worker.replaced records are the only committed evidence and are what the section reports."
  - "In-process and split-poller idle/under-load p95 are reported as absent, not estimated, for this run. Both are computed from run_composed's own return value (ComposedRun) or from run_experiment.py's sent/done timestamps, neither of which exists because the function raised before returning; sc3-run1.poller.jsonl's 32,037 raw samples are committed in full, but computing a ratio against a differently-chosen boundary (e.g. server build.started/build.failed timestamps) would be a plausible-looking number not produced by the harness's own tested method -- exactly what L08 forbids."
  - "The debt file is filed as one item, not two: the undocumented-500 crash (the main finding) and the worst row's own margin disappearing under contention (a related, secondary finding from the same measurement) share Context in the same file rather than splitting into a second file, per the plan's own 'the same file or a second one' option and CLAUDE.md's 'simplest solution that actually works.'"
  - "REQUIREMENTS.md's REQ-latency-bar-demonstrated-or-superseded stays Pending: it is shared across 13-04/13-05/13-06/13-07 and completes only once 13-07 lands L32, the Dockerfile sentence and the debt retirement (or re-trigger) -- marking it complete from this plan would be premature, matching 13-04/13-05's own stated reasoning."

patterns-established:
  - "D-16's 'recorded whatever it reads' extends to an aborted run: when the harness itself crashes before producing a result, the record is built entirely from independently-committed server-side evidence (records.py's structured log), with every missing harness-computed figure stated as absent and why, never backfilled by a different computation."

requirements-completed: []

coverage:
  - id: D1
    description: "bench/latency.py gains scenario_composed (COMPOSED_ROWS, _composed_rows, RequestOutcome, ComposedRun, _fetch, _pool_state, run_composed, _composed_markdown), registered in _SCENARIOS; DEFAULT_SCENARIOS keeps the no-argument run at (concurrent, single); scenario_single/scenario_concurrent byte-identical to 9f26052 (Task 1, prior session, 47613fd)"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: automated
        ref: "make test PYTEST_ARGS=\"tests/test_bench.py -k 'composed_latency or no_argument_latency or reason_the_server_gave' -q\"; make lint typecheck lint-imports; the OLD/NEW scenario-body byte-identity script; git diff --quiet 9f26052 -- src tests/regression/pre_v0_2.json"
        status: pass
    human_judgment: false
  - id: D2
    description: "The investigation harness taught the composed scenario (run_experiment.py --order composed, session.py --mode composed), committed alone (Task 2 harness half, prior session, bfa54b7); SC3 measured once on a fresh server behind the D-05 quiet gate (900 s cap, 31 samples, never released -- non-decisive), recorded regardless per D-16"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: automated
        ref: "ruff check investigation/; sc3.status.json: state aborted, mode composed, server_env {\"SPUR_PORT\": \"8001\"}, decisive false, reason 'sc3-run1 exited 1'; no listener left on 8001; git diff --quiet 9f26052 -- src"
        status: pass
      - kind: human_judgment
        ref: "Checkpoint: the run aborted after requests were sent (not before); the human's decision (option 1, 'record it') authorized recording it as-is rather than relaunching"
        status: pass
    human_judgment: true
  - id: D3
    description: "bench/RESULTS.md's SC3 section records the composition's outcome honestly from the committed server records: 0/10 served, 6/10 refused (503 busy), 4/10 admitted and all 4 over SPUR_BUILD_TIMEOUT (2 via the documented BuildTimeout path, 2 via an undocumented 500), workers_replaced 0->2, idle/under-load ratios reported absent with reason; the undocumented-500 behaviour and the worst row's own margin loss filed as must-severity debt with INDEX.md's row, naming _run_with_timeout's second-handler TimeoutError branch (not recreate_for) as the site"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: automated
        ref: "git diff --numstat 9f26052 -- bench/RESULTS.md prints '... 0' (0 deletions, append-only); git diff --quiet 9f26052 -- src; grep -c <debt-file> docs/tech_debt/INDEX.md prints 1; Severity: must and a Revisit when line present"
        status: pass
      - kind: automated
        ref: "The plan's own literal verify script (comparing RESULTS.md's copied rows against sc3-run1.stdout.txt) fails as written: stdout.txt is 0 bytes because the harness crashed before printing -- expected and documented below, not worked around by fabricating rows"
        status: fail
    human_judgment: false

duration: ~69min total across two sessions (420f200 to this plan's final commit); this continuation (Task 2 close-out through Task 3, SUMMARY and state bookkeeping) ~45min
completed: 2026-10-02
status: complete
---

# Phase 13 Plan 06: SC3 -- The Composed Worst Row Under Ten Concurrent Builds Summary

**The composed scenario shipped as a tested, rerunnable third bench/latency.py scenario that changes nothing about the bar's no-argument run; its one permitted SC3 reading shows the composed worst row cannot complete under ten concurrent builds in the shipped configuration -- 0 of 10 served, all 4 admitted builds timed out, and 2 of those crashed the client with an undocumented 500 from a same-slot timeout cleanup race now filed as must-severity debt.**

## Performance

- **Duration:** ~69 min total (420f200 -> this plan's final commit), split across a prior session (Task 1 + Task 2's harness half) and this continuation (Task 2's measurement close-out + Task 3 + bookkeeping, ~45 min)
- **Started:** 2026-10-02T13:38:53+06:00 (plan start, 420f200)
- **Completed:** 2026-10-02 (this continuation's final commit)
- **Tasks:** 3 of 3
- **Files modified:** 13 total across the plan (bench/latency.py, tests/test_bench.py, run_experiment.py, session.py, six sc3* raw captures, bench/RESULTS.md, docs/tech_debt/INDEX.md, one new debt file)

## Accomplishments

- Task 1 (prior session, `47613fd`): added `scenario_composed` and its support code to `bench/latency.py`, with three pinned tests in `tests/test_bench.py`; `scenario_single`/`scenario_concurrent` and the no-argument run verified byte-identical to `9f26052`.
- Task 2 harness half (prior session, `bfa54b7`): taught `run_experiment.py`/`session.py` the `composed` order/mode.
- Task 2 measurement (prior session, uncommitted until this continuation): ran `session.py --mode composed --label sc3` once on a fresh server. The D-05 quiet gate never released (900 s cap, 31 samples, non-decisive). The run itself aborted (exit 1) after every one of the ten requests had been sent: two of the four admitted requests shared a hash slot with another admitted request, and the second one to time out on each slot crashed with an undocumented 500 (`pool.py`'s `_run_with_timeout`, reading an already-shut-down executor's `_processes`), which propagated through `httpx.HTTPStatusError` and aborted `run_experiment.py` before any stdout, markdown or summary file was produced.
- **This continuation:** verified the prior session's state (`git log`, the six `sc3*` files present and untracked, `src/` unchanged since `9f26052`), committed the six raw captures unmodified (`960866f`), wrote and verified `bench/RESULTS.md`'s SC3 section entirely from the committed server records (no client-side per-request table exists, so none was fabricated), filed the crash mechanism as must-severity debt with the worst row's own disappearing margin as a related finding in the same file, added the INDEX.md row, and committed both together (`a04a7e8`).
- Applied the human's checkpoint decision verbatim: option 1 ("record it") — SC3's one permitted reading stands as measured; no retry; no `src/` change (D-17).

## Task Commits

1. **Task 1 (prior session): the composed scenario and its tests** - `47613fd` (feat)
2. **Task 2 (prior session): the harness taught the composed scenario** - `bfa54b7` (chore)
3. **Task 2 (this continuation): the six raw SC3 captures, committed unmodified** - `960866f` (docs)
4. **Task 3 (this continuation): bench/RESULTS.md's SC3 section + the debt file + INDEX.md** - `a04a7e8` (docs)
5. **Plan metadata (this continuation): SUMMARY, STATE, ROADMAP** - `PENDING` (docs: complete plan; sha fixed in a follow-up commit per the chicken-and-egg precedent, `420f200`)

## Files Created/Modified

- `bench/latency.py`, `tests/test_bench.py` - the composed scenario and its tests (Task 1)
- `.planning/phases/13-latency-bar/investigation/run_experiment.py`, `session.py` - the composed order/mode (Task 2 harness half)
- `.planning/phases/13-latency-bar/investigation/sc3.status.json`, `sc3.session.log`, `sc3.server1.records.jsonl`, `sc3-run1.poller.jsonl`, `sc3-run1.stdout.txt` (0 bytes), `sc3-run1.stderr.txt` - the one permitted SC3 run's raw evidence
- `bench/RESULTS.md` - `### Composed worst row under ten concurrent builds (Phase 13)` appended before `### SPUR_BUILD_TIMEOUT`, append-only
- `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`, `docs/tech_debt/INDEX.md` - the filed defect

## Decisions Made

- The human's decision at the Task 2 checkpoint, verbatim: `1.` — option 1, "record it": SC3's reading is recorded as it stands; the defect is filed as debt; no retry; no `src/` change.
- `bench/RESULTS.md`'s per-request accounting is sourced only from `sc3.server1.records.jsonl` (server-observed `build.started`/`queue.refused`/`build.failed`/`worker.replaced` events), never from a client-side latency table — the harness never built one (the `requests` tuple comprehension raised on its second `future.result()` and `run_composed` never returned).
- In-process and split-poller idle/under-load p95 ratios are reported as absent for this run, with the reason stated, rather than computed from a differently-chosen boundary over the raw poller samples — the harness's own boundary (`run.requests[].sent`/`.done`) does not exist, and a substitute boundary would produce a plausible-but-unmeasured number (L08).
- One debt file, not two: the undocumented-500 crash and the worst row's own margin loss under contention are both measured facts from the same run and share one file's Context, per the plan's "the same file or a second one" option.
- `requirements-completed` stays empty: `REQ-latency-bar-demonstrated-or-superseded` is shared across 13-04/13-05/13-06/13-07 and is marked complete only when 13-07 lands the phase's full record.

## Deviations from Plan

**1. [Expected outcome, not a Rule 1-4 deviation] The plan's own Task 3 automated verify script cannot pass for this run's outcome.** The plan's `<verify>` for Task 3 compares `bench/RESULTS.md`'s copied per-request rows against lines matching `| N |` in `sc3-run1.stdout.txt`. That file is 0 bytes (the harness crashed before printing anything), so the script's own `assert len(rows)==10` fails by construction — there is no stdout capture to copy rows from. This is not a bug to fix: the orchestrator's resume instructions for this continuation explicitly superseded the plan's literal verify for the aborted-run case ("Do NOT fabricate a per-request latency table — the harness never printed one. Where the plan's section template asks for a figure that does not exist for this run, write that it does not exist and why — never a plausible value"), consistent with D-16 ("recorded whatever it reads"). The two verify checks that do apply regardless of outcome (append-only `bench/RESULTS.md`, `git diff --quiet 9f26052 -- src`) both pass.
- **Found during:** Task 3, writing the SC3 section.
- **Resolution:** Built the per-request accounting from `sc3.server1.records.jsonl` instead (server-side truth, independently committed); stated plainly in the RESULTS.md section and here that no client-side table exists.
- **Files affected:** `bench/RESULTS.md`.
- **Commit:** `a04a7e8`.

No Rule 1-4 auto-fixes were needed; no `src/` change was made (D-17).

## Issues Encountered

None beyond the one documented above. `make verify` passed on both commits (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest); plain `git commit` was used for both (the pre-commit hook outruns `gsd_run query commit`'s 30 s timeout, per `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC3 is answered: the composed worst row does not complete under ten concurrent builds in the shipped configuration, recorded in `bench/RESULTS.md` whatever it read (D-16), and the server behaviour it exposed is filed as must-severity debt with a named trigger (D-17).
- 13-07 (L32, the Dockerfile `HEALTHCHECK` comment, the `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` retirement, `fleet-user` restored) can proceed. 13-07 should cite this plan's SC3 finding directly from `bench/RESULTS.md`'s new section and from the new debt file, and should decide whether the 2026-09-23 debt file's own retirement is still correct given SC3's finding that the composed worst row's margin disappears under load (a question that file's own trigger list did not anticipate in those terms).
- No blockers. The new debt file (`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`) stays active; its own "Revisit when" names the deferred ten-identical-worst-row scenario as the next step, not this phase's.

---
*Phase: 13-latency-bar*
*Completed: 2026-10-02*

## Self-Check: PASSED

All claimed files found on disk (`bench/latency.py`, `tests/test_bench.py`,
`run_experiment.py`, `session.py`, all six `sc3*` files, `bench/RESULTS.md`, the new debt
file, `docs/tech_debt/INDEX.md`, this SUMMARY). All claimed commits found in git history
(`47613fd`, `bfa54b7`, `960866f`, `a04a7e8`).
