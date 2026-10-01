---
phase: 07-foundation-generalized-edge-selection-regression-fixture
fixed_at: 2026-09-26T00:00:00Z
review_path: .planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 07: Code Review Fix Report

**Fixed at:** 2026-09-26
**Source review:** .planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01 .. WR-05; no CR/BL findings this review)
- Fixed: 5
- Skipped: 0

**Verification environment:** `workflow.use_worktrees` is `false` for this project
(`.planning/config.json`) -- all edits, syntax checks, `make verify` runs, and commits
happened directly in the main checkout on branch
`gsd/phase-07-foundation-generalized-edge-selection-regression-fixture`. No worktree was
created; the transactional worktree-cleanup tail is a no-op under this config.

The fixture `tests/regression/pre_v0_2.json` was diffed against HEAD (`git diff
--exit-code`) after every fix in this run and confirmed byte-unchanged before each commit.

## Fixed Issues

### WR-01: `corpus.cases()`'s synthesized mate-case key is never checked for collision

**Files modified:** `tests/regression/corpus.py`, `tests/regression/test_corpus.py` (new)
**Commit:** `3eccc54`
**Applied fix:** Added a guard before the synthesized `case_key` is written into
`result` (mirroring `seen_tags`'s existing literal-tag guard): `if case_key in result:
raise ValueError(f"corpus key collision: {case_key}")`. Added a new test file that
monkeypatches `corpus.ENTRIES` with a synthetic pair whose literal tag ("a+mate=40")
equals the mate key a second entry ("a", mate=40) would synthesize, and asserts
`cases()` raises naming the colliding key.

### WR-02: The fixture's coverage test cannot catch a missing `solid` snapshot

**File modified:** `tests/regression/test_pre_v0_2.py`
**Commit:** `86c4251`
**Applied fix:** Added a standalone assertion inside
`test_the_fixture_records_every_corpus_set` that every record with no `mate_teeth` also
carries a `solid` key, naming any offending record id(s) in the failure message. Verified
the assertion actually catches a missing snapshot by testing it (outside the suite,
against an in-memory copy of the fixture with one `solid` key deleted) -- not against
`pre_v0_2.json` itself, which was never touched and stays byte-unchanged.

### WR-03: Selector-matrix test proves counts, not edge identity, for the recess-floor selector

**File modified:** `tests/test_model.py`
**Commit:** `f7d769d`
**Applied fix:** Added a per-edge identity check for `_groove_floor_edges`'s selection
(radius within `TOL` of a known groove radius, `startPoint().z` within `TOL` of a known
floor height) mirroring the bore-rim loop's existing per-edge check. Added a per-face
check to the bore-rim loop itself (`{round(e.startPoint().z / face_width) for e in
rim_edges} == {0, 1}`) so a selection concentrated on one end face is now distinguishable
from one that spans both. All 10 parametrized rows of
`test_each_edge_selector_picks_exactly_its_own_edges` still pass.

### WR-04: The fixture's own module docstring contradicts D-03

**File modified:** `tests/regression/test_pre_v0_2.py`
**Commit:** `48ffad5`
**Applied fix:** Reworded the module docstring's closing instruction to match
`capture.py`'s own (correct) wording: fix the code until the test is green again, full
stop; `make fixture.regen` is for a cadquery/cadquery-ocp pin bump (L12) or a deliberate,
`Lxx`-carrying contract change only -- never to launder a fix. Docstring-only change; no
test behaviour affected.

### WR-05: `BORE_RIM_SLACK`'s margin over the measured kernel tolerance was off by two orders of magnitude

**Files modified:** `src/spur/model.py`, `docs/architecture/decision_log.md`
**Commit:** `e0048e9`
**Applied fix:** `0.01 / 1e-7 = 1e5` (five orders of magnitude, not three) -- changed
"three orders of magnitude" to "five orders of magnitude" in both `model.py`'s comment
and L26's text in `decision_log.md`. Also corrected `decision_log.md`'s "kept ... below
that" to "above that" (BORE_RIM_SLACK, 0.01 mm, sits above the measured 1e-7 mm tolerance
it must clear, not below it) -- a factual correction inside the L26 text already being
amended for the order-of-magnitude fix, not a new append-only entry. Checked
`docs/architecture/solid-model/tactics.md` for the same claim per the review's
instruction; it does not repeat it, so no change was needed there.

## Skipped Issues

None -- all five in-scope findings were fixed.

---

_Fixed: 2026-09-26_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
