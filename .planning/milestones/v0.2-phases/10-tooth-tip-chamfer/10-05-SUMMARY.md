---
phase: 10-tooth-tip-chamfer
plan: 05
subsystem: docs
tags: [decision-log, readme, tech-debt, documentation]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: "10-01's spike numbers, 10-02's field/cap/cut, 10-03's built-solid
      proof, 10-04's sweep and heaviest row -- this plan cites every one of them
      by SUMMARY sha or RESULTS.md section, estimating nothing new"
provides:
  - "README.md: a feature bullet, a CLI example the tests run, the trims-prose
    clause, the tip_chamfer parameter row (verbatim help text) and a Geometry
    notes bullet -- no chamfer size anywhere"
  - "docs/architecture/decision_log.md L29: the field, the cut, the three-limit
    cap with D-04's measured boundary, the derived field and warning, the
    spike/sweep cost record, the proof, and reversibility -- append-only"
  - "docs/architecture/gear-maths/implementation.md and solid-model/tactics.md
    updated to name TIP_CHAMFER_MARGIN, spline_start, tip_chamfer_limit,
    tip_chamfer_effective, _chamfer_tips and _tip_edges"
  - "The cadquery Shape typing debt item at five type: ignores (was four); a new
    must-severity debt item for the root fillet's straight lead-in reaching
    above the pitch circle on large-profile-shift gears, both indexed"
  - "REQ-tip-chamfer and REQ-tip-chamfer-capped marked complete in
    REQUIREMENTS.md (the shared-ID gate's last declaring plan)"
affects: [11-body-cutouts, 12-composed-sweep]

actuals:
  tokens: 6368
  tasks: 3
  commits: 3
  plan_head_before: 3a9dfe26cc5560d21a840faa7116de4bddc371f0
  plan_head_after: d600bc456c17884cf52254334b2ddb1fff8658c1

tech-stack:
  added: []
  patterns:
    - "A phase's closing plan is documentation-and-record only: no source changed
      except the one test line the README's own example needs to keep running
      (L29's own precedent, following L26/L27/L28's shape)."

key-files:
  created:
    - docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md
  modified:
    - README.md
    - tests/test_cli.py
    - docs/architecture/decision_log.md
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/solid-model/tactics.md
    - docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The root fillet's straight lead-in issue is filed as must-debt, not fixed:
    correcting it means either changing every such gear's outline (a fixture
    regeneration with its own Lxx, L05) or rewriting README's claim -- both
    outside this phase's feature, per CLAUDE.md's 'note the tangent' guidance."
  - "L29 was written to cite every number from a 10-0x SUMMARY or bench/RESULTS.md
    verbatim -- no cost or boundary was re-estimated or rounded to look tidier."

patterns-established:
  - "A closing documentation plan re-verifies its own negative constraints (the
    unsourced-sizing-figure grep) against its own new prose, not just the
    shipped code -- L29's first draft named the rejected figure literally and
    tripped the same check it was supposed to prove clean."

requirements-completed: [REQ-tip-chamfer, REQ-tip-chamfer-capped]

coverage:
  - id: D1
    description: "README documents the tip chamfer everywhere a parameter is
      described (features, CLI example, trims prose, parameter table, Geometry
      notes), with no size anywhere, and its own CLI example runs as a test"
    requirement: REQ-tip-chamfer
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
      - kind: other
        ref: "grep -c '^| \\`tip_chamfer\\` | 0 |' README.md == 1; git grep -nE '0\\.1 ?[--] ?0\\.2' -- README.md src docs == exit 1 (no match)"
        status: pass
    human_judgment: false
  - id: D2
    description: "L29 records the field, the cut, the three-limit cap with D-04's
      measured boundary, the derived field and warning, the cost, and the proof,
      each cited to a SUMMARY sha or a RESULTS.md section; the architecture docs
      name the shipped functions; the log stays append-only"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: other
        ref: "git diff --numstat 277a98f -- docs/architecture/decision_log.md (0 deletions); grep -c '^## L29 -- ' == 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "The typing debt item and its INDEX row say five type: ignores
      with current line numbers; the root-lead-in issue is filed as must-debt
      with its measurement and trigger, and indexed; make verify is green"
    verification:
      - kind: other
        ref: "grep -c 'five' docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md; ls docs/tech_debt/active/*-root-lead-in-*.md; make verify"
        status: pass
    human_judgment: false

duration: ~16min
completed: 2026-09-28
status: complete
---

# Phase 10 Plan 05: Document and Log the Tooth-Tip Chamfer Summary

**README now names the tip chamfer in every place a parameter is described (no size
anywhere), L29 records the phase's field/cut/cap/cost/proof each cited to a SUMMARY sha
or `bench/RESULTS.md`, and the debt record is current: five `type: ignore`s and a new
must-severity item for the root lead-in's reach above the pitch circle.**

## Performance

- **Duration:** ~16 min (from 10-04's close-out commit to this plan's third task
  commit; session start time not separately captured)
- **Started:** 2026-09-28T19:27:12+06:00 (previous commit on this branch, 10-04's
  close-out)
- **Completed:** 2026-09-28T19:42:52+06:00
- **Tasks:** 3
- **Files modified:** 7 (1 created, 6 modified)

## Accomplishments

- README.md: a feature bullet ("An edge-break chamfer on the tooth tips at both
  faces"), a CLI example (`spur export -o chamfered.stl --tip-chamfer 0.4`) that
  `test_readme_export_examples_run` now executes and asserts writes a file with no
  warning, the trims-prose clause naming the tip chamfer alongside the root fillet and
  the face recess, the `tip_chamfer` parameter row (the field's help text verbatim,
  trailing period dropped like every other row), and a Geometry notes bullet covering
  the 45-degree edge break, what it leaves untouched, the three-limit cap, the derived
  field, and the measured cost (about 12 s at 200 teeth, quoted from `bench/RESULTS.md`,
  not re-estimated). No chamfer size, module multiple, standard or "typical" value
  appears anywhere in README, `src/` or `docs/` (confirmed by a repo-wide negative
  `git grep`).
- `docs/architecture/decision_log.md` gained `## L29`, append-only (`git diff --numstat`
  confirms 0 deleted lines against `277a98f`): the field (D-10/D-11), the cut
  (D-03/D-13, `_tip_edges`'s end-face test and `_chamfer_tips`'s position last in
  `_build`), the cap (D-01/D-02/D-04, the measured `ra - spline_start` boundary, the
  405-set grid, the 200-tooth pair, `TIP_CHAMFER_MARGIN`'s rounding reason), the derived
  field and warning (D-08/D-09), the cost (D-05/D-06/D-07: the spike's edge-count
  finding, the sweep's heaviest row at 14.87 s of 30 s, the filed timeout-margin debt,
  D-07 never firing), the proof (D-12/D-13/D-14: the 30-row matrix, the real-pipeline
  spy, the built-solid deltas, the tripwire, the guard's amended exit code, the flank
  boundary held one step either side), and reversibility.
- `docs/architecture/gear-maths/implementation.md` now lists `TIP_CHAMFER_MARGIN`,
  `spline_start(pr, fillet)`, `tip_chamfer_limit(p)` and `tip_chamfer_effective(p)` in
  the Layout table, and names the tip chamfer in "Entry points".
  `docs/architecture/solid-model/tactics.md`'s pipeline diagram now ends
  `_cut_keyway ─▶ _chamfer_tips ─▶ one validated Solid` ("tip arcs, last"), the
  `_outline` paragraph notes `calc.spline_start`, and "Edge re-selection" describes
  `_tip_edges()`.
- The cadquery `Shape` typing debt item (`docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md`)
  now says five `type: ignore`s with the current `src/spur/model.py` line numbers
  (195, 219, 221, 264, 273) and a sentence naming the tip chamfer's fifth; the matching
  INDEX.md row title updated to match.
- Filed `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md`
  (must-severity): 10-01's spike measured the root fillet's straight lead-in reaching up
  to 0.5625 mm *above* the pitch circle at `{profile_shift 1.0, pressure_angle 14.5}`
  (0.125 mm above at `{profile_shift 0.75, pressure_angle 20}`), with the flank chord up
  to 35.29 um off the true involute there — contradicting README's "non-working root
  zone" claim on those configurations. Indexed in `docs/tech_debt/INDEX.md`.
- `make verify`: **453 passed in 99.28s (0:01:39)**, wall 100.22s (`time make verify`).
- REQ-tip-chamfer and REQ-tip-chamfer-capped marked complete in REQUIREMENTS.md — this
  is the last of 10-01..10-05 to finish, so the shared-ID gate (`requirements.ready-ids`)
  reported both ready.

## Task Commits

Each task was committed atomically:

1. **Task 1: README documents the tip chamfer wherever a parameter is described, and
   its tip-chamfer example runs as a test** - `5ebbe1c` (docs)
2. **Task 2: Append L29 and bring the gear-maths and solid-model architecture docs up
   to date** - `69c2c35` (docs)
3. **Task 3: Bring the debt record up to date and run the phase's final make verify** -
   `d600bc4` (docs)

_Plan metadata (this SUMMARY, STATE.md, ROADMAP.md) is committed separately below._

## Files Created/Modified

- `README.md` - feature bullet, CLI example, trims-prose clause, `tip_chamfer` row,
  Geometry notes bullet
- `tests/test_cli.py` - the README tip-chamfer example run in
  `test_readme_export_examples_run`
- `docs/architecture/decision_log.md` - `## L29 — ...`, append-only
- `docs/architecture/gear-maths/implementation.md` - the four new calc rows, "Entry
  points"
- `docs/architecture/solid-model/tactics.md` - pipeline diagram, `_outline` paragraph,
  "Edge re-selection" paragraph
- `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` - four becomes five
- `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` -
  new must-severity debt item
- `docs/tech_debt/INDEX.md` - typing row title; new Active row

## Decisions Made

See `key-decisions` in the frontmatter: the root-lead-in issue is filed, not fixed
(fixing it means either an outline change with its own `Lxx` and fixture regeneration,
or a README correction, both outside this phase's feature); every number in L29 is
copied from a 10-0x SUMMARY or `bench/RESULTS.md`, none re-estimated.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] L29's first draft tripped its own negative-sizing-figure check**
- **Found during:** Task 2, running the plan's own verification commands before
  committing
- **Issue:** L29's "The field" paragraph named the rejected `0.1–0.2 x module` sizing
  figure literally, to say it has no source — but the plan's own negative grep
  (`git grep -nE '0\.1 ?[–-] ?0\.2' -- docs`) matches the figure's presence, not its
  framing, so the literal number tripped the check meant to prove no sizing guidance
  appears anywhere in docs.
- **Fix:** Reworded the sentence to reference "the research-era sizing figure" and its
  source (research SUMMARY.md Known Conflict #2) without repeating the number.
- **Files modified:** `docs/architecture/decision_log.md`
- **Verification:** `! git grep -nE '0\.1 ?[–-] ?0\.2' -- docs` passes; `sed -n
  '/^## L29 — /,$p' ... | grep -cF ...` still finds the required D-04/spline_start/
  TIP_CHAMFER_MARGIN/"Tooth-tip chamfer" terms.
- **Committed in:** `69c2c35` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug, docs-only). **Impact on plan:** no behavior
change; the fix was necessary for the plan's own verification to pass. No scope creep.

## Issues Encountered

None otherwise. All three tasks' verification commands (README grep/negative-grep
checks, the `test_readme_export_examples_run` run, the decision-log append-only check
and its term grep, the debt-item counts, and the final `make verify`) passed on first or
second attempt (the one deviation above).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 10 (Tooth-Tip Chamfer) is complete: all five plans have SUMMARYs, REQ-tip-chamfer
  and REQ-tip-chamfer-capped are marked complete, `make verify` is green (453 tests).
- Two must-severity debt items remain open from this phase: the tip-chamfer timeout-
  margin narrowing (10-04) and the root-lead-in reaching above the pitch circle (this
  plan) — both filed with measurements and triggers, neither blocking.
- Phase 11 (body cutouts) and Phase 12 (composed sweep, `REQ-measured-build-time`) can
  proceed; Phase 12's composed sweep should weigh the timeout-margin debt item (D-07's
  second option — a teeth-dependent cap — was recorded but not built).
- No blockers.

---
*Phase: 10-tooth-tip-chamfer*
*Completed: 2026-09-28*

## Self-Check: PASSED

- FOUND: README.md
- FOUND: tests/test_cli.py
- FOUND: docs/architecture/decision_log.md
- FOUND: docs/architecture/gear-maths/implementation.md
- FOUND: docs/architecture/solid-model/tactics.md
- FOUND: docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md
- FOUND: docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md
- FOUND: docs/tech_debt/INDEX.md
- FOUND: .planning/phases/10-tooth-tip-chamfer/10-05-SUMMARY.md
- FOUND commit: 5ebbe1c
- FOUND commit: 69c2c35
- FOUND commit: d600bc4
- Re-ran `make verify`: 453 passed in 99.28s (0:01:39)
