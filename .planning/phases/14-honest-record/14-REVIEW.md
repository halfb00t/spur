---
phase: 14-honest-record
reviewed: 2026-10-03T12:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - tests/test_model.py
  - docs/architecture/decision_log.md
  - docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md
  - docs/tech_debt/INDEX.md
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
reviewer_lanes: [codex]
---

# Phase 14: Code Review Report

**Reviewed:** 2026-10-03
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Incremental re-review after gap-closure plan 14-04 (a4347be, 4892853, ff38fad), diff base
8cfbc16. The codex lane returned "no findings" with no file:line citations (down-weighted;
nothing in it to verify or reject).

Verified independently, by running the code on the pinned kernel (cadquery 2.8.0 /
cadquery-ocp 7.9.3.1.1, this machine):

- Every measured figure the docstrings and L33 state reproduces. Kernel-formula gaps on the
  composed holes rows: d-flat 5.85e-10, round 5.94e-10, keyed 6.55e-10 (tip chamfer, both
  recesses), single-sided 2.79e-12 (signed -2.79e-12). Without the tip chamfer: d-flat
  1.36e-12, round 2.27e-12, keyed -6.82e-12, so the claim "the tip chamfer causes the
  offset" holds for all three rows, not only the one the docstring measured. The WR-02
  literals sit +3.54e-7 (holes) and +4.02e-7 (cells) off their closed forms, as stated.
- "About 15x" (1e-8 / 6.55e-10 = 15.3) and "about 1.5x of headroom at 1e-9" (1.53) are
  arithmetically right.
- The recess outer wall is 12.506 mm on the d-flat and round bores, 12.579 mm on keyed and
  11.994 mm on hex, against a hole reach of 8 to 12 mm: the "wholly inside the recess
  annulus" precondition holds for the four formula rows, and the hex-holes exception
  (hex-holes gap 0.0317 mm3) is real and correctly excluded.
- Row counts: 12 tip rows less 3 formula rows is 9 literal rows, plus 2 of 3 single-sided
  rows is 11, matching the debt file's enumeration (8 spokes/cells, hex-holes, 2
  single-sided) and the INDEX row.
- The 25 affected tests (tripwire, plain proof, both composed matrices) pass; the tripwire's
  control call passes on the unpatched build and the patched call still raises, so the
  WR-02 vacuity is closed. `_build_checked` is not cached, so the control build cannot
  leak into the patched one.
- The `volume_abs` keyword cannot mask a row that specifies neither tolerance: the `else`
  arm falls through to `abs=1e-9`, the strictest bar. The `1e-8` bar is stated accurately
  in the shared assertion's docstring, both composed-test docstrings, L33 (body and Reason
  paragraph) and the debt file; no stale "fifteen" remains in a live claim (the one hit in
  the resolved debt file is history).
- L33 still says the three-row tip bar is `1e-8` and the single-sided row is `1e-9`; the
  code agrees.

The WR-01 platform-calibration concern from the prior review (disposition: open) applies
equally to the new bars (1e-8 has 15x headroom, 1e-9 on the single-sided row has about 360x);
it is not re-filed here.

## Warnings

### WR-01: `volume_rel` silently shadows `volume_abs` when both are passed

**File:** `tests/test_model.py:1291-1296`
**Issue:** The new branch order is `if volume_rel is not None: ... elif volume_abs is not
None: ... else: abs=1e-9`. A caller that passes both keywords gets the relative bar and the
absolute one is dropped without error. Today no caller does (the tip test sets
`volume_rel` to `None` when it sets `volume_abs`), but the default for the tip test is
`volume_rel: float | None = 1e-6`, so the only thing keeping the two exclusive is one
hand-written tuple assignment in the test body. A future row that sets `volume_abs` and
forgets to clear `volume_rel` would assert the 2.6e-4 mm3 relative bar while reading as
the 1e-8 one, which is exactly the "bar that does not say what it enforces" defect this
phase exists to remove. The "neither" case is safe; the "both" case is not.
**Fix:** Reject the ambiguity at the top of the helper:

```python
assert volume_rel is None or volume_abs is None, "pass one volume bar, not both"
```

## Info

### IN-01: Test docstrings cite `14-REVIEW WR-02` / `WR-03`, a file this review replaces

**File:** `tests/test_model.py:1188`, `tests/test_model.py:1427`, `tests/test_model.py:1677`
**Issue:** Three comments cite finding ids in `14-REVIEW.md`. That file is regenerated each
review pass (this one renumbered it), so the ids will point at a different finding or none.
The durable ledger is `14-REVIEW-DISPOSITION.md`, and `.planning/` is not part of the
shipped tree a later reader of `tests/` will have. The comments already carry the full
reasoning (the 11.994 mm wall, the +3.54e-7 / +4.02e-7 offsets), so the citation adds
nothing a reader needs.
**Fix:** Drop the `(14-REVIEW WR-xx)` parentheticals, or cite `14-REVIEW-DISPOSITION.md`
with the finding title.

### IN-02: L33 attributes the tip-row bar to D-06, whose stated trigger was not met

**File:** `docs/architecture/decision_log.md:1573-1592`
**Issue:** L33 defines D-06 as "a gap above 1e-9 mm3, which would have gone to the human".
The tip rows' gaps (5.85e-10 to 6.55e-10) are below 1e-9, so at `abs=1e-9` they pass; the
escalation was driven by thin headroom (about 1.5x), not by D-06's trigger. The text then
says the tip rows "sit within 10x of 1e-9" and closes "the human set it, not the executor
(D-06)". The honest account is in the test docstring ("would leave them about 1.5x of
headroom"); L33 should say that D-06's literal trigger was not reached and the human was
asked because of headroom, so a reader does not infer that the tip rows failed 1e-9.
**Fix:** Reword the sentence at 1589-1592, for example: "The tip rows pass 1e-9 but with
about 1.5x headroom, which is thinner than D-06's trigger anticipated; the human chose
`abs=1e-8` (about 15x their largest gap) at 14-04 Task 2." Drop the bare "(D-06)" credit.

---

_Reviewed: 2026-10-03T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
