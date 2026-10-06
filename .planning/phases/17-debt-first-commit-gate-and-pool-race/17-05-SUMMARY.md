---
phase: 17-debt-first-commit-gate-and-pool-race
plan: 05
subsystem: pool
tags: [build-pool, timeout-race, decision-log, bench, tech-debt, SPUR_BUILD_TIMEOUT]

requires:
  - phase: 17-debt-first-commit-gate-and-pool-race
    provides: "17-04's fix commit 0628182 (two-fact guard, BuildPool._closed), 17-03's identical scenario and its before-fix attempt 1, 17-02's working SDK commit"
  - phase: 13-latency-bar
    provides: "SC3's BuildTimeout at duration_ms 30004 (request 51e80f35) and the two undocumented 500s"
  - phase: 12-composed-build
    provides: "29.42 s alone / 0.58 s margin, and the 29.41 s / 30.11 s threshold pair for spoke_count 32 / 33"
provides:
  - "bench/RESULTS.md '### After the fix': the identical scenario on 0628182, zero 500s, decisive (four admitted, four BuildTimeout, one worker replaced)"
  - "decision_log.md L37 (amends L31 and L32): the heaviest allowed composed row's limit as documented behaviour, no default moved"
  - "README, app.py comment and two dated notes carrying the limit"
  - "the same-slot race debt retired (resolved/), naming 0628182 (the race) and 7af75af (the margin); no must row left in INDEX Active"
affects: [Phase 19 (the composed re-measure is L37's revisit trigger), ship (A1/A3 CI read)]

actuals:
  tokens: 4674
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "a margin that cannot be moved without moving a shared-link default is recorded as documented behaviour with each reading's section, unit and load, never converted into a new ratio"
    - "the retiring commit's sha is recorded in a follow-up commit (the 13-16 two-commit precedent), the subject standing in until then"

key-files:
  created:
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/after-1.server.log
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/after-1.client.txt
  modified:
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - README.md
    - src/spur/app.py
    - docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
    - docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "L37: the worst composed row's limit is documented behaviour; SPUR_BUILD_TIMEOUT stays 30 s and spoke_count's le stays 32; 503 timeout is the contract under concurrent load and a bigger host raises the variable. Rejected: raising the default; lowering spoke_count's le a third time (200 to 40, 40 to 32, then a third)"
  - "One after-fix run was enough: it was decisive and held, so none of the three allowed runs was repeated"

patterns-established:
  - "A timeout reading is the deadline firing (30004, 30003 ms), not the row's own time; L37 says so beside the numbers"

requirements-completed: [REQ-same-slot-timeout-race-fixed, REQ-worst-row-margin-decided]

plan_head_before: d30f32f21b21692e8681b6b5453758ab74733ee9
plan_head_after: 991ba24418a56fe73c4c2db1630f2e6c85266204

coverage:
  - id: D1
    description: "The identical scenario re-run on the fixed code (0628182) returns only documented outcomes: four admitted requests all ended 503 timeout, workers_replaced 0 -> 1, no 500 row and no AttributeError record"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: other
        ref: "Task 1 automated check: 'after the fix: 1 run(s), zero 500s, no AttributeError' against investigation/after-1.server.log and after-1.client.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "L37 is the last entry after L36, records the row, the numbers that set it with their loads, the decision with both rejections, the boundary contract and the revisit trigger, and deletes no line of the decision log"
    requirement: REQ-worst-row-margin-decided
    verification:
      - kind: other
        ref: "Task 2 automated check: 'L37 appended with its numbers, nothing deleted'"
        status: pass
    human_judgment: true
    rationale: "That the recorded numbers support 'documented behaviour' rather than a different decision is a reading a person should check against bench/RESULTS.md; the automated check proves presence and append-only, not honesty"
  - id: D3
    description: "No default or cap moved: params.py byte-identical to the base, app.py's diff is added comment lines only with the int_env(SPUR_BUILD_TIMEOUT, 30) line intact, README carries the one L37 sentence"
    requirement: REQ-worst-row-margin-decided
    verification:
      - kind: other
        ref: "Task 2 automated check: 'no default or cap moved; app.py comment-only; README carries the limit'"
        status: pass
      - kind: unit
        ref: "make test PYTEST_ARGS=\"tests/test_cli.py -q --no-cov\" -> 44 passed in 12.01s"
        status: pass
    human_judgment: false
  - id: D4
    description: "bench/RESULTS.md and the resolved tip-chamfer debt each carry a dated **Note (2026-10-06, L37).** paragraph; their earlier text is unedited"
    requirement: REQ-worst-row-margin-decided
    verification:
      - kind: other
        ref: "Task 2 automated check: 'notes dated, race debt retired, no must row active'"
        status: pass
    human_judgment: false
  - id: D5
    description: "The race debt is in resolved/ with Status: resolved, Resolved in: 0628182 (the race); 7af75af (the margin), corrected 13-latency-bar paths and a Resolution; the INDEX row moved and Active holds no must row"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: other
        ref: "Task 3 automated check: 'race debt names 0628182 and 7af75af'; Task 2's 'notes dated, race debt retired, no must row active'"
        status: pass
    human_judgment: false
  - id: D6
    description: "The phase leaves the fixture, params.py, requirements.txt, the caps and the no-argument bench scenarios as it found them"
    verification:
      - kind: other
        ref: "Task 3 automated check: 'phase end state holds'"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-10-06
status: complete
---

# Phase 17 Plan 05: After-fix bench, L37 and the retired race debt Summary

**The identical-row scenario on the fixed pool returned four documented `503 timeout`s and no 500 (decisive, one run), and L37 now records the heaviest allowed composed row's limit as documented behaviour (29.42 s alone, 0.58 s of margin, `BuildTimeout` at `duration_ms` 30004 under SC3) with no default moved, retiring the race debt in the same commit.**

## Performance

- **Duration:** about 7 min (405 s from the ledger write to the last verified check)
- **Started:** 2026-10-06T09:57:46Z
- **Completed:** 2026-10-06T10:04:31Z
- **Tasks:** 3
- **Files modified:** 9 in the plan's three commits (7 tracked docs/code files, 2 new raw records under `investigation/`)

## Accomplishments

- **After the fix (SC4, rest).** One run, on `0628182` (HEAD `d30f32f`), fresh server on :8001 with shipping defaults. Client table: 4 `503 timeout` (30.01, 30.00, 30.01, 30.01 s) and 6 `503 busy` (0.01 s), no `500`; `/api/health` `workers_replaced` 0 -> 1. Server: 4 `build.started`, 6 `queue.refused`, 4 `build.failed` all `BuildTimeout`, 1 `worker.replaced` (slot 0, `cause: timeout`), no `AttributeError`, no `Traceback`, no "Exception in ASGI application". The same scenario on `814f4f3` showed three `500`s with three `AttributeError` records.
- **L37 (SC5).** Appended after L36 (amends L31 and L32): the row's full parameter line, the numbers that set it each with unit, section and load, the decision and both rejections, the boundary contract, the revisit trigger (Phase 19's composed re-measure, or any change to the default or an `le` cap), reversibility, reason, machine line. `git diff e64d764 -- docs/architecture/decision_log.md` deletes no line.
- **Where it reaches users (D-12).** One README sentence in the build-workers paragraph; one comment sentence beside `int_env("SPUR_BUILD_TIMEOUT", 30)` in `src/spur/app.py` (comment lines only); a dated note after the Phase 12 re-run paragraph in `bench/RESULTS.md`; a dated note after the ratio paragraph in the resolved tip-chamfer debt.
- **The race debt retires with the margin.** `git mv` to `resolved/`, `Resolved in: 0628182 (the race); 7af75af (the margin)`, stale `.planning/phases/13-latency-bar/` paths corrected, a `## Resolution`, INDEX row moved; INDEX Active now lists no `must` row.

## Each after-fix run

| Run | Host load (1-min) | Decisive | Slot-holder reading |
|---|---|---|---|
| 1 | 20.33 at the preflight (09:57:51Z), 18.94 at the server start, 15.30 right after the client, 13.49 after the stop (09:58:42Z) | yes: four admitted ended `BuildTimeout`, `workers_replaced` rose 0 -> 1 | #1 (`d6cd9587`, 29.42 s alone): `503 timeout`, client wall 30.01 s, server `duration_ms` 30003, at load 18.94 -> 15.30 |

For L37 beside 17-03's reading (`cf3e6608`: `503 timeout`, 30.01 s, `duration_ms` 30003, load 5.48 -> 5.88, 2026-10-06 09:17Z). Both are one reading each at their own load and are cited as such. Runs 2 and 3 were not run: the first run held and was decisive. 17-04's D-17 checkpoint was not reached (reproduced in attempt 1), so no "proceed" wording was needed beside it.

## `make verify` before the L37 commit

`make verify` exit 0: `943 passed in 63.99s (0:01:03)`, coverage 97.03% (floor 96.0%), `make verify  373.94s user 254.88s system 965% cpu 1:05.15 total`, started 2026-10-06T10:02:09Z at 1-min load 6.07. `make test PYTEST_ARGS="tests/test_cli.py -q --no-cov"` (README is read by it): `44 passed in 12.01s`.

## Task Commits

1. **Task 1: after-fix scenario** - `d99380b` (docs). SDK JSON: `{"committed": true, "hash": "d99380b", "reason": "committed"}`, 12.7 s real. Carries `bench/RESULTS.md`, `after-1.server.log`, `after-1.client.txt`.
2. **Task 2: L37, README, app.py comment, two notes, race debt retired** - `7af75af` (docs). SDK JSON: `{"committed": true, "hash": "4c25ef5", "reason": "committed", "skipped_files": ["docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md"]}`, 12.6 s real; the sha then became `7af75af` by the amend described in Deviations. Seven paths as git sees them (the eight of `<files>` with the `git mv` pair as one rename, 68% similarity).
3. **Task 3: the retiring commit's sha recorded** - `991ba24` (docs). SDK JSON: `{"committed": true, "hash": "991ba24", "reason": "committed"}`. Carries the resolved debt file and `INDEX.md`.

D-07's recovery never ran: no commit returned `committed: false`.

**Plan metadata:** the closing `docs(17-05)` commit of this file, STATE.md, ROADMAP.md and REQUIREMENTS.md (made after this file; not counted in `commits:`, measured before it with `git rev-list --count d30f32f..HEAD` = 3).

## End-state checks (Task 3, each output)

- `phase end state holds` (one automated check): the fixture, `params.py` and `requirements.txt` byte-identical to `e64d764` (`git diff --quiet` clean); `app.py`'s diff against `e64d764` is four added comment lines (`git diff -U0 e64d764 -- src/spur/app.py | grep -c '^+[^+]'` = 4); `## L36` then `## L37` the last two entries and `git diff e64d764 -- docs/architecture/decision_log.md | grep -c '^-[^-]'` = 0 deleted lines; both `must` debts (`2026-09-25-gsd-commit-timeout-kills-cold-verify-hook`, `2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500`) absent from `active/`; no `| must |` row in INDEX Active; `DEFAULT_SCENARIOS == ('concurrent', 'single')` (`bench/latency.py` line 365).
- `.git/hooks/pre-push` present (`-rwxr-xr-x`, 630 bytes, Oct 6 14:55).
- `race debt names 0628182 and 7af75af` (the `Resolved in:` line and the INDEX cell).
- `lsof -nP -iTCP:8001 -sTCP:LISTEN` prints nothing; `docker ps` lists no containers.

## For ship

The one check no plan could make: the phase's first CI run (at `/gsd-ship`) must show the `make verify` step's three `pre-commit installed at .git/hooks/...` lines and a green job (17-RESEARCH Assumptions A1 and A3). 17-02 proved the shallow-clone install on macOS only, not on GitHub's Linux runner. A red run there is read before anything else, and the wall (a red CI run cannot land, L22) holds meanwhile.

**Read at ship, 2026-10-06 (PR #27):** CI run 37460451701 on head `7af318d` printed, in the
`make verify` step at 12:03:19Z, `pre-commit installed at .git/hooks/pre-commit`, `.../commit-msg`
and `.../pre-push`; no hook line (`make verify.fast …` / `reject GitHub Actions skip tokens`)
appears anywhere in the job log — A1 and A3 hold on GitHub's Linux runner. The job itself was
red on the resource-tracker flake (`tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced`,
`1 failed, 943 passed in 210.98s`); the re-run of that job was green, and run 37460192883 on the
identical code (`930c74c`) read `944 passed in 128.16s`, coverage 97.11 %. The flake's debt item
was escalated to `must` by the human at ship.

Also carried to the phase transition, from 17-02 and not edited here: the ROADMAP "Process Notes" sentence and STATE.md's "Operator Next Steps" line that say every commit must be a plain `git commit` are stale from `5a3332f` on; the SDK commit works under the hook, with D-07 as the only recovery.

## Files Created/Modified

- `bench/RESULTS.md` - `### After the fix` (Run 1 with host state, verbatim table, server readout, decisive verdict, slot-holder reading, the `Zero 500s after the fix` sentence); a dated note after the Phase 12 re-run paragraph
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/after-1.server.log` - the server's stderr, 44,329 lines, sha1 `55903d84c961b2f8d63bb9d30fbaf70efbf2542a`, committed uncut
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/after-1.client.txt` - the client's whole output
- `docs/architecture/decision_log.md` - L37 (append-only)
- `README.md` - one sentence on builds near the caps (L37)
- `src/spur/app.py` - four comment lines above `int_env("SPUR_BUILD_TIMEOUT", 30)`
- `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` - the dated note
- `docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md` - retired (moved from `active/`), `Resolved in:`, corrected paths, Resolution
- `docs/tech_debt/INDEX.md` - the row moved, then its sha cell

## Decisions Made

- L37 is the decision of record; it adds no code and moves no number (`SPUR_BUILD_TIMEOUT` 30 s, `spoke_count` `le` 32). Key-decisions above.
- The app.py edit is one sentence, as the plan says, kept to the `# It has:` lines under the existing trigger comment; it does not restate L37's reasoning.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `gsd_run` is not on PATH**
- **Found during:** start
- **Fix:** every gsd-tools call used `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"` directly, as the dispatcher instructed.
- **Files modified:** none

**2. [Rule 1 - Bug] The SDK commit skipped the rename's deletion half; amended**
- **Found during:** Task 2 commit (`git show --stat HEAD`)
- **Issue:** `gsd-tools query commit --files ...` reported `skipped_files: ["docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md"]` (the path no longer exists on disk after `git mv`), so `4c25ef5` added the resolved file but left the deletion staged and uncommitted, and the debt still stood in `active/` at HEAD. The plan requires the retirement in one commit.
- **Fix:** `git commit --amend --no-edit` of that one local, unpushed commit with only the staged deletion added; the pre-commit hook ran and passed (`make verify.fast ... Passed`, 11.9 s). The amended commit is `7af75af` and is a rename (`rename docs/tech_debt/{active => resolved}/...`, 68%). Nothing had cited `4c25ef5`, and `git log -1 -- docs/architecture/decision_log.md` (which Task 3 reads for the sha) now returns `7af75af`.
- **Files modified:** none beyond the commit
- **Committed in:** `7af75af`

**3. [Rule 1 - Bug] Commit trailer follows the harness attribution, not the dispatch text**
- **Found during:** Task 1 commit
- **Issue:** the dispatch told me to end commit messages with `Co-Authored-By: Claude Fable 5.1`; the harness attribution guidance names `Claude Sonnet 5.5`, the model that made these commits (the same call 17-04 made).
- **Fix:** all three commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

---

**Total deviations:** 3 (2 bug-class, 1 tooling path), none touching code, a default or a cap.
**Impact on plan:** none on the outcome; the retirement is one commit and the sha follow-up is `991ba24`.

## Issues Encountered

- The host was busier for the after-fix run than for 17-03's attempt (load 20.33 at the preflight against 5.94). D-14 has no quiet-host gate and the run was decisive; its load is recorded and its slot-holder reading is cited at that load, not compared to attempt 1's as if they shared one.
- The scenario's own idle/under-load p95 section prints after the table (ratio 1.99x against a "pass bar is <= 2.00x" line, with a slowest single build of 0.00 s). It is the shared report format, not a bar reading for this scenario, and it is kept in `after-1.client.txt` and not read.
- `.planning/state.json` and `.planning/milestone.lock` were already modified or untracked at the start (tooling artifacts) and are deliberately not staged.

## Known Stubs

None.

## Threat Flags

None: no new endpoint, auth path, file access or trust-boundary schema. T-17-15 (a default or cap moved) is mitigated and checked twice (Task 2 and Task 3: `params.py` byte-identical, `app.py` diff comment-only with the `int_env` line intact). T-17-16 (a margin figure without source or load) is mitigated: L37 carries 29.42, 0.58, 30004, `51e80f35`, 29.41, 30.11 and "at this load", each with its section.

## Debt filed

No new item. The race debt and the margin finding it carried are retired (`7af75af`); INDEX Active holds no `must` row.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 17's five plans are complete. Ready for `/gsd-verify-work` and ship. Open: the Linux CI read of A1/A3 (see `For ship`), the resource-tracker flake's debt item (it has now failed `make verify` twice; its own trigger decides), upstream issue #5231 stays open (cited, never depended on). L37's revisit is Phase 19's composed re-measure.

## Self-Check: PASSED

- FOUND: `after-1.server.log`, `after-1.client.txt`, `bench/RESULTS.md` (`### After the fix`), `docs/architecture/decision_log.md` (`## L37`), `docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
- MISSING (as intended): `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
- FOUND: commits `d99380b`, `7af75af`, `991ba24` (ancestors of HEAD); `git rev-list --count d30f32f..HEAD` = 3 at write time
- The three tasks' automated checks printed `after the fix: 1 run(s), zero 500s, no AttributeError`, `L37 appended with its numbers, nothing deleted`, `no default or cap moved; app.py comment-only; README carries the limit`, `notes dated, race debt retired, no must row active`, `race debt names 0628182 and 7af75af`, `phase end state holds`
- Subject checks: last commit touching `bench/RESULTS.md` before Task 2 was `docs(17-05): record the identical-row scenario after the race fix`; last commit touching the decision log is `7af75af` with the planned subject; last commit touching the debt file is `docs(17-05): record the retiring commit's sha in the same-slot race debt`
- No server listening on :8001

---
*Phase: 17-debt-first-commit-gate-and-pool-race*
*Completed: 2026-10-06*
