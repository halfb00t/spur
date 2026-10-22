---
phase: 29-ubuntu-26-final-reading
plan: 01
subsystem: ci-ledger
tags: [ubuntu-26, ubuntu-latest, close-condition, trigger-not-fired, tech-debt]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: the 26-02 pre-classification of run 38724011970 on the pinned label ubuntu-26.04, the baseline a migrated run is read against
provides:
  - three dated reads of the ubuntu-latest window in bench/RESULTS.md, each with its raw Image lines kept as a tsv, all outcome not fired
  - Phase 29 closed on its close condition, on the human's call (close)
  - REQ-ubuntu26-classified-on-migration moved to Future Requirements in the words the human approved
  - the Ubuntu 26 debt item left active with its trigger restated and the 26-02 record attached
affects: [v0.6 milestone close]

actuals:
  tokens: 60000
  tasks: 3
  commits: 6
plan_head_before: 0ffb33d9933f0ea9b7679603a290466bddbba1c3
plan_head_after: c16daa8a40149150cca2425955efeb4bc74f04e1

tech-stack:
  added: []
  patterns:
    - "A date-gated phase reads the window from each job's own log (message part, never the step column) and closes on a stated condition instead of holding the milestone"

key-files:
  created:
    - .planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T0658Z.tsv
    - .planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T1208Z.tsv
    - .planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T1313Z.tsv
  modified:
    - bench/RESULTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/REQUIREMENTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md

key-decisions:
  - "Phase 29 closed on its close condition, trigger not fired, on the human's call (close) at 2026-10-22T13:28Z"
  - "The Ubuntu 26 debt item stays active; its trigger is the first ubuntu-latest run whose job log holds Image: ubuntu-26.04, Phase 29's own PR and the v0.6 milestone-close PR counting"

requirements-completed: []

coverage:
  - id: D1
    description: "The ubuntu-latest window is read run by run from each job's own log and the outcome is derived from the table, never from the date or the label"
    requirement: "REQ-ubuntu26-classified-on-migration"
    verification:
      - kind: judgment
        ref: "bench/RESULTS.md `### The ubuntu-latest window, read <stamp> (29-01)` x3, each with one Outcome line and a tsv; the read commits were made in the earlier executor runs, and Task 1's verify scripts were not re-run in this continuation"
  - id: D2
    description: "The requirement is neither orphaned silently nor reported complete: it leaves v0.6 and the Traceability table for Future Requirements in the approved words"
    requirement: "REQ-ubuntu26-classified-on-migration"
    verification:
      - kind: judgment
        ref: ".planning/REQUIREMENTS.md `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)`; Task 3's verify script (close branch), run in this continuation after the close commit: passed"
---

# Phase 29 Plan 01: Ubuntu 26 Final Reading Summary

**Three dated reads of the `ubuntu-latest` window found 30 of 30 jobs on `ubuntu-24.04` and no 26.04 run, so Phase 29 closed on its close condition (trigger not fired) with the Ubuntu 26 item still active and its trigger restated.**

## Performance

- **Completed:** 2026-10-22
- **Tasks:** 3 (Task 1 tracer read, Task 2 human decision, Task 3 close branch)
- **Files modified:** 6 tracked files, 3 tsv files created

## Reads and outcomes

| Read (UTC) | `ci` runs in window | Jobs | Image values found | Outcome | Human's answer |
|---|---|---|---|---|---|
| 2026-10-22T06:58Z (`074a46f`) | 8 | 24 | `ubuntu-24.04` `20261012.334.1`, `20261018.339.1` | not fired | `wait` (07:12Z, `1d20547`) |
| 2026-10-22T12:08Z (`e8e9c8c`) | 10 | 30 | the same two | not fired | `wait` (13:02Z, `9d56e06`) |
| 2026-10-22T13:13Z (`1aeeec9`) | 10 | 30 | the same two | not fired | `close` (13:28Z, `c16daa8`) |

No job of any `ubuntu-latest` run read `ubuntu-26.04`, and no pinned-label run on 26.04 was in the window, so there was no first 26.04 run to classify and no job log kept whole. The 26-02 spike's `ubuntu-26.04` run (38724011970) stays the only 26.04 reading.

## Human's answer (Task 2)

Recorded verbatim in `bench/RESULTS.md` as `Decision (2026-10-22T13:28Z): close -- "close, with the REQUIREMENTS.md edit exactly as proposed, parts (a)-(e), unedited"`. The REQUIREMENTS.md edit was applied as approved: (a) bullet removed, (b) `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)` added under Future Requirements, (c) Traceability row removed, (d) coverage lines now 16 total and 16 mapped, (e) last-updated line. Every anchor was found verbatim; nothing was improvised.

## Close branch, as carried out

- `bench/RESULTS.md`: Decision line after the 13:13Z Outcome line.
- `.planning/ROADMAP.md`: Progress row reads `1/1 | Closed — trigger not fired | 2026-10-22`; the Phase 29 criteria carry `Not applicable: closed 2026-10-22 on the close condition ...`; the phase-list line stays `- [ ]` (Phase 20 precedent).
- `.planning/STATE.md`: Roadmap Evolution has `- Phase 29 closed (trigger not fired), 2026-10-22: ...`. The orchestrator's pre-existing phase-start hunks were kept and committed with it; `.planning/state.json` was left unstaged.
- Debt item `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`: stays `Status: active` with a dated paragraph, the trigger restated and the 26-02 record (run 38724011970, image `20261012.163.1`, install 14.44 s) attached. The INDEX row's trigger column matches.
- `.github/workflows/ci.yml` untouched. `requirements.mark-complete` not run.

## Commits

| Commit | Subject |
|---|---|
| `074a46f` | docs(29): record the ubuntu-latest window read at 2026-10-22T06:58Z, outcome not fired |
| `1d20547` | docs(29): record the human's wait after the ubuntu-latest window read at 2026-10-22T06:58Z |
| `e8e9c8c` | docs(29): record the ubuntu-latest window read at 2026-10-22T12:08Z, outcome not fired |
| `9d56e06` | docs(29): record the human's wait after the ubuntu-latest window read at 2026-10-22T12:08Z |
| `1aeeec9` | docs(29): record the ubuntu-latest window read at 2026-10-22T13:13Z, outcome not fired |
| `c16daa8` | docs(29): close Phase 29 on its close condition, trigger not fired |

## Verification

- `make verify`: `======================= 1348 passed in 221.25s (0:03:41) =======================` then `exit 0` (run before the close commit).
- `git diff --exit-code v0.5 -- tests/regression/ .github/workflows/ci.yml`: clean (exit 0).
- `git diff --numstat v0.5` deleted lines: `bench/RESULTS.md` 0, `docs/architecture/decision_log.md` 0.

## Deviations from Plan

None - plan executed exactly as written. The two earlier `wait` answers were the plan's own resumable branch, not deviations.

## For the transition

- The orchestrator's phase completion must leave the ROADMAP Progress row at `Closed — trigger not fired`.
- `requirements-completed` is empty on purpose: the ROADMAP says the requirement is "neither orphaned silently nor reported complete".
- STATE.md Blockers/Concerns still carries the two Ubuntu lines (`[v0.6]` rollout window and `[Phase 21]` item); they need updating to "Phase 29 closed, trigger not fired, item active".

## Known Stubs

None.

## Threat Flags

None. No code, endpoint or workflow file changed.

## Debt and ideas filed

No new debt item or idea was filed. The existing Ubuntu 26 item at `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` stayed active with its trigger restated.

## Self-Check: PASSED

- `.planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T1313Z.tsv` and the two earlier tsv files exist.
- Commits `074a46f`, `1d20547`, `e8e9c8c`, `9d56e06`, `1aeeec9`, `c16daa8` are ancestors of HEAD.
