---
phase: 11-body-cutouts
plan: 09
subsystem: docs
tags: [readme, decision-log, architecture-docs, ideas, bench-results, close-out]

# Dependency graph
requires:
  - phase: 11-01
    provides: "the amended REQ-spoke-cutout/ROADMAP SC2 text and the spoke-arm wall rule this plan's README rows and L30 cite"
  - phase: 11-02
    provides: "the honeycomb spike's measured HEX_CELL_CAP=120 and cut spelling (star), cited in the geometry note and L30's cap paragraph"
  - phase: 11-03
    provides: "the hole cutout pattern, cutout_walls()/_under_min_wall() and the shared _cut_body shape, documented in the README and L30"
  - phase: 11-04
    provides: "the spoke cutout pattern, the analytic fillet and the one-pattern rule, documented in the README and L30"
  - phase: 11-05
    provides: "the honeycomb cutout pattern, HEX_CELL_CAP written into calc.py and the raise-to-fit, documented in the README and L30"
  - phase: 11-06
    provides: "D-18's build-time gate outcome (hole_count le 60, spoke_count le 40, HEX_CELL_CAP unchanged) and its heaviest measured rows, cited in L30's cost paragraph and README's Parameters bounds context"
  - phase: 11-07
    provides: "the selector spy, kernel-boundary and tangent-cutter proofs, cited in L30's proof paragraph"
  - phase: 11-08
    provides: "the built-solid and recess-fillet-survival proofs, cited in L30's proof paragraph"
provides:
  - "README.md: one feature bullet, three CLI examples, an API refusal/trim paragraph, ten Parameters rows and a geometry note naming cutout_hub_wall/cutout_rim_wall/spoke_fillet_effective/hex_cell_effective/hex_cell_count with their datums"
  - "tests/test_cli.py's test_readme_export_examples_run runs all three new README examples, asserting each writes a file over 1000 bytes and prints no warning"
  - "docs/architecture/decision_log.md L30, appended after L29 with 0 deleted lines, citing every number to a SUMMARY sha or a bench/RESULTS.md section"
  - "docs/architecture/gear-maths/implementation.md and docs/architecture/solid-model/tactics.md updated for HEX_CELL_CAP, every new calc function and the _cut_body build-chain step"
  - "Three deferred ideas filed under docs/ideas/ with INDEX rows: a cutout rotation field, a teeth/module-dependent honeycomb cap, and conditional form fields"
  - "bench/RESULTS.md's make verify wall-time measurement at the phase's end: 621 passed in 177.62s -- 178.55s wall, against Phase 10's 453 passed / 98.17s"
affects: [12-composed-sweep]

# Actuals (#2632)
actuals:
  tokens: 8181
  tasks: 3
  commits: 3
  plan_head_before: 43760833658f79dfa919cfcc4d1dcc32c0d03ee1
  plan_head_after: 847af3f0a06caa6934f703c9b4f55783148f3f54

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The phase-closing plan's L30 entry cites every number to a SUMMARY sha or a
      bench/RESULTS.md section rather than re-deriving or re-estimating it (D-25),
      continuing L26-L29's own precedent."

key-files:
  created:
    - docs/ideas/2026-09-29-cutout-rotation-field.md
    - docs/ideas/2026-09-29-teeth-dependent-honeycomb-cap.md
    - docs/ideas/2026-09-29-conditional-form-fields.md
  modified:
    - README.md
    - tests/test_cli.py
    - docs/architecture/decision_log.md
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/solid-model/tactics.md
    - docs/ideas/INDEX.md
    - bench/RESULTS.md

key-decisions:
  - "L30's paragraph shape follows L29's exactly, one bold-led paragraph per topic (The
    fields, The cut, The honeycomb, The cap, The refusals, The numbers, The cost, The
    proof, Reversibility), each citing a SUMMARY sha or a bench/RESULTS.md section --
    no number in L30 was re-estimated or re-derived from memory."
  - "The make verify wall-time measurement (621 passed in 177.62s -- 178.55s wall) was
    taken on a host at load 3.07/4.04/4.65, not a quiet host by the project's own
    >1.5 bar, but well below the exceptional 32.17 load 11-06's re-run measured under;
    recorded with its host state rather than presented as clean (L08)."
  - "The three deferred ideas were written verbatim from 11-CONTEXT.md's Deferred Ideas
    section (the rotation field, the teeth/module-dependent cap, conditional form
    fields) rather than re-phrased, so their Next-step triggers match what the phase's
    own context already recorded."

patterns-established: []

requirements-completed: [REQ-hole-cutout, REQ-spoke-cutout, REQ-honeycomb-cutout, REQ-cutout-derived-numbers]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "README.md names the three cutout patterns in its feature list, has
      one Parameters row per new field, one CLI example per pattern, an API sentence on
      the cutout refusals and the two trimmable sizes, and a geometry note naming all
      five new derived fields with their datums"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: other
        ref: "grep -cE '^\\| `(spoke_count|spoke_width|hub_d|rim_wall|spoke_fillet|hole_count|hole_d|hole_circle_d|hex_cell|hex_wall)` \\| 0 \\|' README.md (10)"
        status: pass
      - kind: other
        ref: "grep -cE '^spur export -o (holes|spokes|honeycomb)\\.stl ' README.md (3)"
        status: pass
      - kind: other
        ref: "grep -c 'cutout_hub_wall' README.md; cutout_rim_wall; spoke_fillet_effective; hex_cell_effective; hex_cell_count (each >= 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_readme_export_examples_run runs the three new README examples
      end to end, each writing a file over 1000 bytes and printing no warning"
    requirement: REQ-hole-cutout
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
      - kind: other
        ref: "make test PYTEST_ARGS='tests/test_cli.py tests/regression -q' (104 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/architecture/decision_log.md gains L30 after L29 with 0 deleted
      lines, in L29's paragraph shape, every number cited to a SUMMARY sha or a
      bench/RESULTS.md section"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: other
        ref: "git diff --numstat b86a0e9 -- docs/architecture/decision_log.md (146 added, 0 deleted)"
        status: pass
      - kind: other
        ref: "sed -n '/^## L30 /,$p' docs/architecture/decision_log.md | grep -cE 'HEX_CELL_CAP|Honeycomb cell-count spike|Body cutout build and export time|[0-9a-f]{7}' (22)"
        status: pass
    human_judgment: false
  - id: D4
    description: "gear-maths/implementation.md lists every new calc function and
      HEX_CELL_CAP; solid-model/tactics.md's build chain shows _cut_body between
      _cut_keyway and _chamfer_tips with one sentence on the one-cut-call cutters"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: other
        ref: "grep -c '_cut_body' docs/architecture/solid-model/tactics.md (2)"
        status: pass
      - kind: other
        ref: "grep -c 'hex_cells' docs/architecture/gear-maths/implementation.md (1)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Three deferred ideas filed under docs/ideas/ with INDEX rows in the
      same commit: a rotation field, a teeth/module-dependent honeycomb cap, and
      conditional form fields, each with every TEMPLATE.md heading"
    requirement: REQ-honeycomb-cutout
    verification:
      - kind: other
        ref: "grep -cE '(cutout-rotation-field|teeth-dependent-honeycomb-cap|conditional-form-fields)\\.md' docs/ideas/INDEX.md (3)"
        status: pass
    human_judgment: false
  - id: D6
    description: "bench/RESULTS.md records make verify at the phase's end (passed
      count, pytest seconds, wall seconds) against Phase 10's 453 passed / 98.17s, the
      phase's added cost measured, not assumed; make verify is green"
    requirement: REQ-spoke-cutout
    verification:
      - kind: other
        ref: "sed -n '/^## Body cutout build and export time (Phase 11)/,$p' bench/RESULTS.md | grep -cE '[0-9]+ passed in [0-9.]+s' (1)"
        status: pass
      - kind: other
        ref: "make verify (621 passed in 177.62s, 178.55s wall; ruff, mypy --strict, lint-imports, no-fake-done all clean)"
        status: pass
      - kind: other
        ref: "git diff --numstat b86a0e9 -- bench/RESULTS.md (355 added, 0 deleted)"
        status: pass
    human_judgment: false

# Metrics
duration: ~31min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 09: Body Cutouts Documentation and Close-Out Summary

**The README now names the three body cutout patterns with ten Parameters rows, three
tested CLI examples and a geometry note naming all five new derived fields; decision log
L30 records the phase's fields, cut, honeycomb lattice, cap methodology, refusals,
numbers, measured costs and proofs, every number cited to a SUMMARY sha or
`bench/RESULTS.md`; three deferred ideas are filed; and `make verify` reads 621 passed in
177.62s -- 178.55s wall at the phase's end.**

## Performance

- **Duration:** ~31 min
- **Started:** 2026-09-29T16:03Z (approx, this session's opening `make verify` baseline)
- **Completed:** 2026-09-29T16:34:11Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 10 (7 modified, 3 created)

## Accomplishments

- README.md gained a body-cutout feature bullet, three CLI examples (`holes.stl`,
  `spokes.stl`, `honeycomb.stl`) that run clean with no warnings, an API paragraph on
  the cutout refusals (two patterns, half-set, MIN_WALL breach, no whole honeycomb
  cell) and the two trimmable sizes (`spoke_fillet`, honeycomb cell size), ten
  Parameters rows in schema order (Spokes, Holes, Honeycomb) copying the help text
  verbatim, and a geometry note naming `cutout_hub_wall` (with its bore-mouth datum),
  `cutout_rim_wall` (root-circle datum), `spoke_fillet_effective`, `hex_cell_effective`
  and `hex_cell_count`, plus `HEX_CELL_CAP`'s measured value (120).
- `tests/test_cli.py`'s `test_readme_export_examples_run` gained three new blocks
  running the holes/spokes/honeycomb examples end to end, each asserting the exported
  file is over 1000 bytes and stderr carries no `"warning:"` — verified against the
  real (unmodified) kernel before being written in: all three commands build with zero
  warnings on the default gear.
- `docs/architecture/decision_log.md` gained `## L30`, appended after L29 with 0
  deleted lines (146 added), in L29's own paragraph shape: The fields (D-01, D-04,
  D-18, D-19), The cut (D-02, D-03, D-05, D-24), The honeycomb (D-07, D-08, D-09,
  D-13), The cap (D-11, D-12, D-24), The refusals (D-10, D-14 to D-17), The numbers
  (D-06, D-20), The cost (D-18), The proof, and Reversibility — every number cited to a
  `11-0N-SUMMARY.md` sha or a `bench/RESULTS.md` section, none re-estimated (D-25).
- `docs/architecture/gear-maths/implementation.md` gained `HEX_CELL_CAP` in the
  constants row and eleven new function rows (`_under_min_wall`, `_listed`,
  `cutout_walls`, `hole_gap`, `spoke_opening`, `spoke_fillet_limit`,
  `spoke_fillet_effective`, `whole_cells`/`cell_count_floor`/`cells_within`,
  `hex_cells`); `docs/architecture/solid-model/tactics.md`'s build-chain diagram gained
  `_cut_body` between `_cut_keyway` and `_chamfer_tips`, with one paragraph on the
  one-cut-call cutters and why no selector before the tip step sees a cutout edge.
- Three ideas filed under `docs/ideas/` from `TEMPLATE.md`, each with every heading,
  and one `INDEX.md` row per file added in the same commit: a rotation field for spoke
  arms and holes (`2026-09-29-cutout-rotation-field.md`), a teeth/module-dependent
  honeycomb cap (`2026-09-29-teeth-dependent-honeycomb-cap.md`), and conditional form
  fields (`2026-09-29-conditional-form-fields.md`).
- `bench/RESULTS.md` gained `### make verify wall time` at the end of the "## Body
  cutout build and export time (Phase 11)" section: **621 passed in 177.62s** --
  **178.55s** wall (host: 12 CPUs, arm64, load 3.07/4.04/4.65 at start), against Phase
  10's recorded 453 passed / 98.17s; the phase's 168 new tests add +80.38s to the gate,
  measured rather than assumed. Noted that the wall time is now past 150s, so every
  commit's pre-commit hook (which runs this same `make verify`) takes about that long
  too (D-23).

## Task Commits

Each task was committed atomically:

1. **Task 1: Document the body cutouts in the README and run its examples** —
   `19825ac` (docs)
2. **Task 2: Log L30 and document the body cutout step** — `67e0e3b` (docs)
3. **Task 3: File the cutout ideas and record make verify's wall time** — `847af3f`
   (docs)

**Plan metadata:** this SUMMARY and the STATE.md/ROADMAP.md/REQUIREMENTS.md bookkeeping
are committed separately per `execute-plan.md`'s `git_commit_metadata` step.

## Files Created/Modified

- `README.md` — feature bullet, three CLI examples, API refusal/trim paragraph, ten
  Parameters rows, geometry note (Task 1).
- `tests/test_cli.py` — three new blocks in `test_readme_export_examples_run` (Task 1).
- `docs/architecture/decision_log.md` — `## L30` appended (Task 2).
- `docs/architecture/gear-maths/implementation.md` — `HEX_CELL_CAP`, eleven function
  rows (Task 2).
- `docs/architecture/solid-model/tactics.md` — `_cut_body` in the build chain, one new
  paragraph (Task 2).
- `docs/ideas/2026-09-29-cutout-rotation-field.md`,
  `docs/ideas/2026-09-29-teeth-dependent-honeycomb-cap.md`,
  `docs/ideas/2026-09-29-conditional-form-fields.md` — new idea files (Task 3).
- `docs/ideas/INDEX.md` — three new rows (Task 3).
- `bench/RESULTS.md` — `### make verify wall time` subsection (Task 3).

## Decisions Made

See `key-decisions` in the frontmatter for L30's paragraph shape and citation
discipline, the make-verify measurement's host-load caveat, and the deferred ideas'
verbatim sourcing from `11-CONTEXT.md`.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' `<verify>` and acceptance
criteria passed on the first attempt; no Rule 1–4 auto-fix was needed.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 11 (Body Cutouts) is complete: all nine plans have their `SUMMARY.md`, the
  README, decision log and architecture docs reflect the shipped patterns, three
  deferred ideas are on record, and `make verify` (621 tests) is green.
- `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  (must, filed in 11-06) is open — Phase 12's own composed sweep is its named trigger.
- Phase 12 (composed sweep, per `.planning/ROADMAP.md`) can build directly on this
  phase's ten fields, five derived numbers, `HEX_CELL_CAP`, and the measured `le`
  bounds (`spoke_count` 40, `hole_count` 60) recorded in L30.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f README.md ]` → FOUND
- `[ -f tests/test_cli.py ]` → FOUND
- `[ -f docs/architecture/decision_log.md ]` → FOUND
- `[ -f docs/architecture/gear-maths/implementation.md ]` → FOUND
- `[ -f docs/architecture/solid-model/tactics.md ]` → FOUND
- `[ -f docs/ideas/2026-09-29-cutout-rotation-field.md ]` → FOUND
- `[ -f docs/ideas/2026-09-29-teeth-dependent-honeycomb-cap.md ]` → FOUND
- `[ -f docs/ideas/2026-09-29-conditional-form-fields.md ]` → FOUND
- `[ -f docs/ideas/INDEX.md ]` → FOUND
- `[ -f bench/RESULTS.md ]` → FOUND
- `git log --oneline --all | grep 19825ac` → FOUND (Task 1 commit)
- `git log --oneline --all | grep 67e0e3b` → FOUND (Task 2 commit)
- `git log --oneline --all | grep 847af3f` → FOUND (Task 3 commit)
- All plan-level `<verification>` re-run above: PASS (README/test_cli greps, L30
  numstat and citation-count grep, `_cut_body`/`hex_cells` presence, three idea INDEX
  rows, `bench/RESULTS.md`'s "passed in" line, `make verify` 621 tests green, 0 deleted
  lines in both `decision_log.md` and `bench/RESULTS.md`)
