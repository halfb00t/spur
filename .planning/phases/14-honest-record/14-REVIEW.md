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
reviewer_lanes: [codex]
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
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

No blockers. Three warnings: whether the new bars hold on CI, whether two tripwire rows
prove what L33 says they prove, and whether the debt file's "no closed form exists" claim is
true.

**External lane:** codex reviewed the same scope (`reviewer_lanes: [codex]`). Both of its
claims were re-read against source and re-measured before inclusion. Claim 1 is WR-02's
mechanism and is merged into WR-02 (corroborated by codex). Claim 2 is a separate defect and
is WR-03 (external: codex). Details of where codex was right and where it was loose are in
each finding.

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

**File:** `tests/test_model.py:1356-1383` (rows and test), `tests/test_model.py:1258` (the `abs=1e-9` line), `docs/architecture/decision_log.md` (L33, "all three skip-the-cutout tripwire rows run at abs=1e-9")
**Corroborated by codex** (codex P2, same mechanism, found independently; I re-measured it below).
**Issue:** The `holes` row passes the literal `565.486678` (line 1358) and the `cells` row
`1052.220866` (line 1365) into the shared assertion, whose default is `abs=1e-9`
(line 1258, `volume_rel is None`). Each literal is the true closed-form value rounded to 6 dp,
so each is off by about 4e-7, roughly 400 times the bar:
- holes: closed form `6 * pi * (4/2)**2 * 7.5 = 180*pi = 565.4866776462`. Literal minus
  closed form is +3.54e-7 mm3.
- cells: closed form `18 * (sqrt(3)/2) * 3**2 * 7.5 = 1052.2208655981` (18 cells, size 3).
  Literal minus closed form is +4.02e-7 mm3.
- I built the **unpatched** solid for both (recess_sides "none", this host) and read the
  removed volume directly: holes `565.4866776461604`, cells `1052.220865598084`. Gaps to the
  literals are -3.538e-7 and -4.019e-7 mm3, both far above 1e-9. So on a correct, unskipped
  build the volume line at 1258 raises `AssertionError` on these two rows.

Why `pytest.raises(AssertionError)` (lines 1379-1383) cannot tell patched from unpatched:
- Patched (`_cut_body` a no-op): `faces_delta` is empty, so `assert faces_delta == d_faces`
  (line 1250) raises first. The volume line is never reached.
- Unpatched (correct build): faces and edges pass, then the volume line raises on the 6 dp
  literal.
- Both raise the same bare `AssertionError`, and nothing in the test inspects the message or
  which line fired. The two outcomes are indistinguishable to the test.

Consequences:
- The volume line is not exercised as a tripwire on these two rows. Only the face-delta
  assertion proves anything, and it is the assertion the phase did not change.
- If the face or edge assertions were ever reordered or weakened, these rows would still pass
  for a reason unrelated to the cutout step.
- L33's wording presents the three rows as evidence the 1e-9 bar bites. For two of them it is
  vacuous.

The `spokes-filleted` row uses `_filleted_spoke_volume(p)` and is fine.
**The closed forms already exist in this file**, so no new derivation is needed:
- cells: the proof test computes it at `tests/test_model.py:1348`,
  `len(cells) * (math.sqrt(3) / 2) * size * size * p.face_width`, from `hex_cells(p, pr.rf)`.
- holes: the proof test computes it at `tests/test_model.py:1314`,
  `p.hole_count * math.pi * (p.hole_d / 2) ** 2 * p.face_width`. The recessed-holes test at
  `tests/test_model.py:901-903` derives the same cylinder-area form times the remaining web.
**Fix:** Pass those closed forms (not literals) as `d_volume` for the `holes` and `cells`
rows, as the `spokes-filleted` row already does with `_filleted_spoke_volume`. Better, add a
control: before applying the monkeypatch, call the shared function on the same row and
assert it passes, so the `raises` can only be satisfied by the skipped cutout. Or split the
raise: assert the faces delta is non-empty and the volume delta is zero, directly, and keep
`pytest.raises` only for the shared call. Reword the L33 sentence to say which rows are
discriminating.

### WR-03: The debt file, L33 and two test docstrings claim "no closed form exists" for the composed volumes; it exists for several rows and is only underived for the rest (external: codex)

**File:** `docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md:15-17`, `docs/architecture/decision_log.md:1579-1580` and `:1607-1608`, `tests/test_model.py:1245-1246`, `:1601-1602` and `:1657-1658`
**Issue:** The debt file says the fifteen `d_volume` values are 6 dp literals "because no
closed form exists after an arbitrary boolean". L33 repeats it ("no closed form exists for
it") and says the 15 rows "cannot" meet 1e-9. The shared function's docstring says "no
closed form to agree with". As a blanket statement it is false, and this phase exists to make
the record honest (L08: a claim no one verified is a plausible number). Evidence it is false:
- `tests/test_model.py:901-903` (not a composed row, but the same geometry) already derives a
  recessed-hole volume as `6*pi*(hole_d/2)**2*web` and asserts it at `rel=1e-6`.
- I computed that form against the composed literals. Both-recess web is `7.5 - 2*2.0 = 3.5`:
  `6*pi*4*3.5 = 263.89378290` vs literal `263.893783` (the d-flat, round and keyed holes rows,
  3 of the 12 tip-chamfer rows). Top-only web is `5.5`: `6*pi*4*5.5 = 414.69023027` vs literal
  `414.69023` (the single-sided holes row). So 4 of the 15 rows have an exact, trivial closed
  form today. The hole circle (radius 10 +/- 2) sits inside the recess annulus
  (6.506 to 12.506 mm) on those rows, which is why the web formula is exact.
- Codex said the formula "also applies to the composed round/D-flat hole cases". True, and also
  to keyed. It does **not** apply to `hex-holes` (263.92552, differs from 263.893783 by
  0.0317 mm3): the hex bore pulls the recess annulus to 5.994 to 11.994 mm, and the holes reach
  r = 12, so they cross the recess outer wall and add a sliver of full-thickness cut (this is
  also why that row has 16 CYLINDER faces, not 6). Codex did not note that exception.
- The remaining rows (spokes, cells, and hex-holes) straddle the recess walls, so their closed
  form is a polar or polygon-versus-circle integral split at the recess radii (plus the
  fillet torus on the single-sided rows). That is real work, not an impossibility.
  `_filleted_spoke_volume` in this very phase is a closed polar derivation of the same kind.
  The accurate statement is "not yet derived", not "cannot exist".

Tip-chamfer overlap (the question of whether the plain-solid closed form carries over
unchanged to the 12 tip rows): measured, the chamfer does not geometrically overlap any
cutout on those rows.
- Default gear: pitch radius `r = 16.625`, tip radius `18.375`, `rf = 14.438`. The tip chamfer
  is 1.75 mm off the tip arcs, so its radial band is `16.625` to `18.375` mm.
- Outermost cutout reach on those rows: holes `12`, cells `12.288`, spokes `13.438`
  (`rf - cutout_rim_wall`). All sit below the chamfer band, a gap of at least 3.2 mm. All
  four bore shapes give the same `r`, `rf` and rim radii.
- So the tip chamfer cannot change the removed volume on any of the 12 rows. What makes those
  rows differ from the plain-solid proof rows is not the chamfer but the recess (the tipped
  rows keep the default both-sided recess, with `recess_fillet` 0) and, for the hex bore,
  the shifted recess radii. The plain-solid (`recess_sides "none"`) closed form therefore does
  **not** apply unchanged to them: the recess removes the web material first, which is exactly
  why the holes rows land on the web formula. Open question, not asserted: whether the
  spokes and cells rows on the three non-hex bores are plain-solid-formula minus a recess
  correction that is simple to write. I did not derive it.
- Wording consequence: the debt file's Related-files framing "a tip chamfer or a one-sided
  recess together with a cutout" and its "the composition itself is what these rows prove"
  over-credit the tip chamfer. On these cutout volumes it contributes nothing measurable.

Why it is a warning, not info: the debt file is what stops someone from tightening these rows.
A false "cannot" tells the next person not to try, when 4 of 15 rows could be tightened to the
formula bar today. The debt file's own Next step ("or derive them as the plain-solid closed
form plus the composition's own measured delta") also points the wrong way for the holes rows:
the web formula is the whole answer there, with no measured delta.
**Fix:** Reword all five places to "no closed form has been derived for the rows that straddle
a recess wall". Split the debt: the four holes rows (d-flat, round, keyed, single-sided) pass
the web closed form at `abs=1e-9` now, drop `volume_rel` for them (the function already has
the strict default), and shrink the debt to the remaining 11 rows. State in the debt file that
the tip chamfer is radially clear of every cutout on the 12 tip rows and is not what the rows
add. Keep the 6 dp literals only where no derivation exists.

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
