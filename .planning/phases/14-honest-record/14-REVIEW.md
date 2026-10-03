---
phase: 14-honest-record
reviewed: 2026-10-03T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - docs/architecture/decision_log.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md
  - docs/tech_debt/resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md
  - docs/tech_debt/resolved/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md
  - README.md
  - src/spur/calc.py
  - src/spur/model.py
  - tests/test_calc.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 14: Code Review Report

**Reviewed:** 2026-10-03
**Depth:** standard (diff ac6de10..HEAD of each file)
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the lead-in warning in `calc.derive`, the README and `_outline` prose, the
closed-form filleted-spoke oracle, the opt-in `volume_rel` on the shared cutout assertion,
and the debt and decision-log records.

Ran `make verify`: ruff, mypy, 5 import contracts kept, `927 passed in 215.83s`. I also
re-ran the rim-corner tripwire's perturbation by hand with the `volume_rel=1e-6` bar. Every
other assertion in the shared function passed, and the removed volume was off the oracle by
-2.522e-4 mm3. So the `abs=1e-9` line is the only thing that fails, as the test and L33 claim.

Verified, no defect:
- **Warning condition.** `h > 0` iff the fillet exceeds half the dedendum AND `x > 0.125`.
  - `rb < r` always.
  - `rf < r` for every `x <= 1.0` (the field bound).
  - So `r_start` never lifts the spline above `r` by itself, and the cause clause is true on
    every firing.
  - `round(h, 3)` and `f"{h:.3f}"` both round the exact binary value, so "0.000 mm above"
    cannot print.
- **README numbers.** `1.188 mm` is `2.1875 - 1.0 = 1.1875` for the default gear. The 15 rows
  in the new test count correctly, as do the 12 + 3 composed rows.
- **`volume_rel`.** Sound: strict `abs=1e-9` is the default, so loosening is explicit at the
  call site and a forgotten argument fails loudly instead of silently relaxing the bar. The 15
  composed `d_volume` values are 6 dp literals and could not meet 1e-9, so passing
  `rel=1e-6` keeps the bar they already had. The tightening is honest and the residual is filed.
- No stale references to the moved debt files remain outside `.planning/` history.

No blockers. Two warnings are about whether the new bars hold on CI and whether two
tripwire rows prove what L33 says they prove.

## Warnings

### WR-01: The new abs=1e-9 volume bars were measured on one host only; CI is ubuntu-latest

**File:** `tests/test_model.py:1253-1260` (bar), `tests/test_model.py:1297-1303` (the gaps' provenance)
**Issue:** The four formula rows now assert the removed volume at `abs=1e-9` mm3 on solids of
565 to 2959 mm3, which is about 3e-13 relative. That sits within a few hundred ulps of
double-precision volume arithmetic. The gaps (1.36e-12 to 8.87e-12 mm3) were measured on
macOS arm64 only (docstring and L33: "this host"). `.github/workflows/ci.yml` runs
`make verify` on `ubuntu-latest` (x86_64). OCCT's GProp volume integration, `libm` and FMA
contraction can differ in the last bits across platforms. The measured margin is roughly
100x, so it will probably hold. But a CI-only red from a 1e-9 bar would send someone to loosen
it, which is the move this phase set out to prevent. The record states the bar as universally
met and never says it was checked on the platform CI uses.
**Fix:** Run the four rows on the CI platform (a one-off `gh workflow run`, or a Linux
container) and record the gaps next to the arm64 ones in the docstring and L33. If any gap
comes within about 10x of 1e-9, derive the bar as a stated multiple of the observed
float-noise floor rather than a round 1e-9. Do not drop it to `rel`.

### WR-02: Two skip-the-cutout tripwire rows pass 6 dp literals at abs=1e-9, so their volume line fails on a correct build too

**File:** `tests/test_model.py:1356-1383` (rows and test), `docs/architecture/decision_log.md` (L33, "all three skip-the-cutout tripwire rows run at abs=1e-9")
**Issue:** The `holes` (565.486678) and `cells` (1052.220866) rows feed 6 dp literals into
the shared assertion, which defaults to `abs=1e-9`. A literal rounded to 6 dp is off by up to
5e-7, so on these rows the volume assertion raises on a correct, unskipped build as well. The
test wraps the call in `pytest.raises(AssertionError)` and cannot tell which assertion fired.
It stays green only because the face-delta assertion (earlier in the function) already fails
when `_cut_body` is a no-op. Consequences:
- The volume line is not exercised as a tripwire on these two rows.
- If the face or edge assertions were ever reordered or weakened, these rows would still pass
  for a reason unrelated to the cutout step.
- L33's wording presents the three rows as evidence the 1e-9 bar bites. For two of them it is
  vacuous.

The `spokes-filleted` row uses the closed form and is fine.
**Fix:** Pass the same closed forms the proof test uses (`p.hole_count * pi * (hole_d/2)**2 *
face_width`, and `len(cells) * sqrt(3)/2 * size**2 * face_width`) instead of literals. Or
split the raise: assert the faces delta is non-empty and the volume delta is zero, directly,
and keep `pytest.raises` only for the shared call. Reword the L33 sentence to say which rows
are discriminating.

## Info

### IN-01: Resolved root-lead-in debt file keeps the template's "On resolve" HTML comment

**File:** `docs/tech_debt/resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md:67-68`
**Issue:** The trailing `<!-- On resolve: set Status: resolved, ... -->` template instruction
survives in a file that is now resolved. The other resolved file does not have it. Harmless,
but it is leftover scaffolding in a record whose point is honesty.
**Fix:** Delete the comment.

### IN-02: The closed-form oracle is exercised at one configuration; the tripwire copies production code

**File:** `tests/test_model.py:1126-1178` (oracle), `tests/test_model.py:1400-1414` (`perturbed`)
**Issue:**
- `_filleted_spoke_volume` agrees with the kernel to 2.73e-12 at exactly one point (SPOKES12 +
  `spoke_fillet 1`). Its sign conventions (hub vs rim segment, `theta`) are validated at that
  one geometry only. A second configuration (different `spoke_count`, `spoke_width` or
  `rim_wall`, so a different `phi`) would show the polar derivation is general and not a
  coincidence of one angle.
- The tripwire's `perturbed` is a hand copy of `_fillet_corner`'s `inside=True` branch plus
  `+ 1e-6`. If `_fillet_corner` is refactored, the copy keeps testing the old algorithm. The
  "all other checks identical" precondition would then fail loudly, which limits the damage,
  but the copy is a maintenance trap. Only the rim corner is guarded; the hub corner's root
  choice has no tripwire.
**Fix:** Add a second oracle-vs-kernel row, for example `spoke_count=8, spoke_width=6,
spoke_fillet=0.8`. Where possible, wrap `_fillet_corner` and shift the returned tangent point
by 1e-6 along the line instead of re-implementing the quadratic.

### IN-03: Warning gives a height and a cause but no actionable threshold

**File:** `src/spur/calc.py:982-985`
**Issue:** The text "the root fillet is larger than half the dedendum" is correct. But it
omits the second necessary condition README states (`x > 0.125`) and gives no number the user
could change. The omission is correct as a cause (the clause is true on every firing), so
this is not an L08 violation. It is only an observation that README says more than the
warning does. L33 records that remedy numbers were deliberately left out.
**Fix:** None required. If the owner wants the warning self-sufficient, append the fillet size
at which it stops firing, `(1.25 - x)*m/2`, computed in `derive`, not typed.

---

_Reviewed: 2026-10-03_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
