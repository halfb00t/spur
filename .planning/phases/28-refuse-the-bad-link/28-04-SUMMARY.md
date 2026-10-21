---
phase: 28-refuse-the-bad-link
plan: 04
subsystem: tech-debt-ledger
tags: [review-disposition, tech-debt, triage, ledger]

requires:
  - phase: 28-refuse-the-bad-link
    provides: the shas of 28-01 (cb93d4e), 28-02 (61154d1, 282fa63, 235e51d) and 28-03 (87d98ab, 54f3b53, 9092802) that the ledger cites
  - phase: 27-ledger-tests-and-harness
    provides: 27-TRIAGE.md, the draft cells for Phases 19 and 21-24
provides:
  - nine review-disposition ledgers (Phases 10, 18, 19, 21-24, 26, 27) with no open row, in the front matter and the table
  - one nice debt item for 18 IN-03/04/05/08 and 10 IN-01, one must debt item for 10 IN-02 (a decision for the human)
  - the two items 28-01 and 28-02 retired now lead with their short shas
affects: [v0.6 milestone audit, /gsd-verify-work 28]

actuals:
  tokens: 11200
  tasks: 3
  commits: 3
plan_head_before: a01bb056cb8e02e60200d240ff2bcdf01403c0c5
plan_head_after: 8e868392085ee902c0f792621c975cf952e41625

tech-stack:
  added: []
  patterns:
    - "A hand-triaged disposition file keeps the gate's own stamp in a comment on the recorded: line (9001695's shape)"

key-files:
  created:
    - docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md
    - docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md
  modified:
    - .planning/milestones/v0.2-phases/10-tooth-tip-chamfer/10-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.4-phases/18-trochoid-maths-proved/18-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.4-phases/19-the-trochoid-in-the-part/19-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.5-phases/21-browser-test-of-the-viewer/21-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.5-phases/22-download-name-carries-the-root/22-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.5-phases/23-conditional-form-fields/23-REVIEW-DISPOSITION.md
    - .planning/milestones/v0.5-phases/24-bore-shape-selector/24-REVIEW-DISPOSITION.md
    - .planning/phases/26-gate-fails-with-a-cause/26-REVIEW-DISPOSITION.md
    - .planning/phases/27-ledger-tests-and-harness/27-REVIEW-DISPOSITION.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md
    - docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md
    - docs/tech_debt/resolved/2026-10-09-phase-19-review-info-findings-deferred.md

key-decisions:
  - "18 IN-01 is recorded fixed by 767317b (the cap sentence already reads 'within 0.001 mm of the largest' in the tree) instead of filed as debt that does not exist; a reading of D-12 flagged for the verifier"
  - "10 IN-02 is deferred to a must item whose next step is the human's decision (fix under a new Lxx with its own make fixture.regen commit, or keep with a reason); not fixed here (D-13)"
  - "10 IN-01 shares the nice item with the Phase 18 leftovers under its own trigger line, so it is revisited when bench/tip_chamfer_spike.py changes, not only with the trochoid maths (D-18)"
  - "21 IN-04 is fixed for 04a (1981d93, branch 6ff1269) and its Source cell names 04b's debt path, the parked-wait item, whose trigger no longer names this phase (D-16)"

requirements-completed: [REQ-info-findings-triaged, REQ-old-info-findings-triaged]

coverage:
  - id: D1
    description: "All 41 findings open at 0efc87c (plus 19 IN-01..IN-04 and 22 WR-01/WR-02) carry one disposition with evidence in both the front matter and the table: fixed with a resolving sha, deferred with an existing path, or skipped with a reason"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: other
        ref: "ledger check (scratchpad ledger_check.py, the plan's Task 2 script): prints 'ledger closed: 41 rows read', exit 0; grep '| open |' over the nine files prints nothing"
        status: pass
    human_judgment: false
  - id: D2
    description: "Phase 18 and Phase 10 leftovers are filed with named triggers (nice item, two trigger lines) and 10 IN-02 is left as the human's decision (must item with both probe outcomes)"
    requirement: "REQ-old-info-findings-triaged"
    verification:
      - kind: other
        ref: "Task 1 verify script: 'Phase 10 ledger closed against two filed items'; Severity greps print 1 and 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "The two items 28-01 and 28-02 retired name their commits by short sha in the file and the INDEX row; the parked-wait trigger no longer names Phase 28"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: other
        ref: "Task 3 verify (grep -q for each sha in file and INDEX row) and Task 2's parked-wait script: exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "Whether 10 IN-02's field should print null or 0.0 for a chamfer that was asked for and not cut"
    requirement: "REQ-old-info-findings-triaged"
    verification: []
    human_judgment: true
    rationale: "A printed-value contract decision (L08) that this plan deliberately leaves to the human; the must item records both options"

duration: ~25min
completed: 2026-10-21
status: complete
---

# Phase 28 Plan 04: Close the review-finding ledger Summary

**Forty-one open review findings of Phases 10, 18, 19, 21-24, 26 and 27 each carry one evidenced disposition (28 fixed, 6 skipped with a reason, 7 deferred to a debt or idea file that exists), in both representations of nine disposition files; the leftovers are filed as one `nice` item and one `must` decision for the human.**

## Performance

- **Duration:** about 25 min (no start time was recorded in-session; approximate)
- **Completed:** 2026-10-21T13:08Z (gate finished)
- **Tasks:** 3 (Task 1 tracer, Tasks 2 and 3 auto)
- **Files modified:** 13 tracked plus 2 created, 3 commits

## Accomplishments

- Two debt items filed from the template, each re-checked against the tree first (every named line still held the defect), with INDEX rows.
- Nine `*-REVIEW-DISPOSITION.md` files closed: `open: 0`, no `disposition: open`, no `| open |` row, every `recorded:` line in `9001695`'s shape (`recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was <old stamp>`).
- Split findings keep one row with one disposition and the other half named in the Source cell: 19 IN-02 (bench half fixed, near-copies kept with the reason), 19 IN-04 (`_host_state` and the label, both fixed), 21 IN-04 (04a fixed, 04b the parked-wait item), 24 IN-02 and CX-03 (one wording commit).
- The five vacuous-pass findings (24 CX-05, 23 IN-08, 23 IN-11, 21 IN-03, 21 IN-04) all read `fixed`.
- The `_wait_until_parked` item's trigger no longer names Phase 28's triage, in the file and its INDEX row.
- The two retired items lead with `cb93d4e` and `61154d1`, in the file and the INDEX row.

## Filed debt items

| Path | Severity | Holds |
|---|---|---|
| `docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md` | nice | 18 IN-03, IN-04, IN-05, IN-08 (trigger: next phase changing the trochoid / hob-root maths in `calc.py` or its tests) and 10 IN-01 (own trigger: next edit of `bench/tip_chamfer_spike.py` or the `tip_chamfer` bound) |
| `docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md` | must | 10 IN-02, a decision for the human (fix under a new Lxx with its own `make fixture.regen` commit, or keep with a reason) |

## 10 IN-02 probe (run at planning and again here, on this tree)

- `derive(GearParams(tip_chamfer=0.0004)).tip_chamfer_effective` is `0.0`, with the warning "Tip chamfer 0.0004 mm is below the 0.001 mm resolution it is cut at and was not cut."
- `derive(GearParams(tip_chamfer=0.0)).tip_chamfer_effective` is `None`, no warning.
- `tip_chamfer` appears in neither `tests/regression/pre_v0_2.json` nor `tests/regression/golden_requests.json` (`grep -c` reads 0 in both).

## Ledger check

`ledger closed: 41 rows read` (the plan's Task 2 script, run after the ledger commit and again after the gate). Rows of the 41 by disposition: **28 fixed, 6 skipped, 7 deferred**.

| Phase | fixed | skipped | deferred | rows |
|---|---|---|---|---|
| 10 | 0 | 0 | 2 | IN-01, IN-02 |
| 18 | 2 | 2 | 4 | IN-01, IN-07 fixed; IN-02, IN-06 skipped; IN-03/04/05/08 deferred |
| 19 | 4 | 0 | 0 | IN-01..IN-04 |
| 21 | 7 | 0 | 0 | WR-01..WR-03, IN-01..IN-04 |
| 22 | 5 | 0 | 0 | WR-01, WR-02, IN-01..IN-03 |
| 23 | 2 | 0 | 0 | IN-08, IN-11 |
| 24 | 5 | 0 | 1 | IN-01, IN-02, IN-03, CX-03, CX-05 fixed; IN-04 deferred |
| 26 | 2 | 3 | 0 | IN-03, IN-04 fixed; IN-01, IN-02, IN-05 skipped |
| 27 | 1 | 1 | 0 | IN-11 fixed; IN-12 skipped |

## Retiring shas

- `cb93d4e` for `docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md` (28-01)
- `61154d1` for `docs/tech_debt/resolved/2026-10-09-phase-19-review-info-findings-deferred.md` (28-02)

## Gate

Command: `make verify`. Tail of its output: `1348 passed in 201.99s (0:03:21)`, `exit 0`; import contracts `5 kept, 0 broken`; coverage `TOTAL 97.99%`. `git diff --exit-code v0.5 -- tests/regression/` is empty. `git status --short` shows no tracked change (only the tool-managed `.planning/state.json` and `.planning/milestone.lock`, which are not committed). The pre-commit hook passed on all three commits.

## Task Commits

1. **Task 1: file the two leftover debt items** - `e1f5b81` (docs)
2. **Task 2: close the other ledgers, restate the parked-wait trigger** - `1e0bbb9` (docs; includes the Phase 10 ledger edit that Task 1 left uncommitted by design)
3. **Task 3: name the retiring shas** - `8e86839` (docs)

## Decisions Made

See key-decisions. The one reading of the plan to check: D-12 sent "everything except IN-02, IN-06 and IN-07" to the `nice` item, but 18 IN-01 is already fixed in the tree (`767317b`; `calc.py:1749` reads "within 0.001 mm of the largest"), so it is `fixed` with that sha rather than filed as debt that does not exist.

## Deviations from Plan

None - plan executed exactly as written. Two small notes, neither a deviation: the Related-files line numbers in the `nice` item were taken from the tree (for example `calc.py:1415` for `cutter`'s `rho` guard, `bench/trochoid.py:568-575` for `_oracle`) and differ from the review's older ones; and cells name the full commit subject beside each sha, read from `git log` by a scratch script (not committed) so no sha was typed by hand.

## Issues Encountered

None. A stray scratch file written to a mistyped path under `/private/tmp/claude-501/-Users-half/` was removed with its parent directory; that parent could not be confirmed empty beforehand, but it sits outside the repo and holds only session scratch.

## Known Stubs

None.

## Threat Flags

None. Docs and ledger files only; no network, auth, file-access or schema surface.

## Debt ledger

Filed: the two items above (nice and must) with INDEX rows. Retired: none beyond the two 28-01/28-02 items whose shas this plan wrote.

## Next Phase Readiness

Phase 28 has all four plans summarised. Both requirements this plan owns (REQ-info-findings-triaged, REQ-old-info-findings-triaged) are markable complete. 10 IN-02 stays open as a `must` item awaiting the human's decision.

## Self-Check: PASSED

- Created files exist: both `docs/tech_debt/active/2026-10-21-*.md` items.
- Commits `e1f5b81`, `1e0bbb9`, `8e86839` are ancestors of HEAD; `commits: 3` measured from `a01bb05..HEAD`.
- Task 1, Task 2 and Task 3 verify scripts and acceptance greps re-run green; `make verify` exit 0.
