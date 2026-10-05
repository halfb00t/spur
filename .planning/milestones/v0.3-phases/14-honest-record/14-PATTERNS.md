# Phase 14: Honest Record - Pattern Map

**Mapped:** 2026-10-02
**Files analyzed:** 9 (no new files/modules this phase)
**Analogs found:** 9 / 9

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/calc.py` (`derive()` warnings block, new branch) | pure-maths/service | transform (request-response via `/api/info`) | `src/spur/calc.py` — the tip-chamfer branch (`derive()` ~974-993) | exact — same function, same tuple, same printed-resolution idiom |
| `src/spur/model.py` (`_outline` docstring, 136-139) | component (geometry builder) docstring only | transform | same file, same function (prose-only edit) | exact |
| `tests/test_calc.py` (new parametrized warning rows) | test | request-response (unit) | `tests/test_calc.py::test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (~603-656) | exact — same parametrize/full-string-assert shape |
| `tests/test_model.py` (new closed-form helper) | test / pure-maths oracle | transform (CRUD-adjacent: computed vs built-solid compare) | `tests/test_model.py::_spoke_bar_area` (1111-1124) | exact — same "pure math beside the proof" shape |
| `tests/test_model.py` (tightened shared assertion, 1196) | test | request-response | `tests/test_model.py::_assert_the_cutout_is_what_derive_prints` (1174-1217) | exact — the one line being edited |
| `tests/test_model.py` (new filleted-spoke row wiring + tripwire row) | test | event-driven (monkeypatch) | `tests/test_model.py::test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` (1286-1320) | exact — same monkeypatch-then-`pytest.raises` tripwire shape |
| `README.md` (root-fillets bullet, ~225-228) | docs | n/a | same file — tip-chamfer bullet's citation style ("measured; decision log L29") and undercut bullet's "the UI warns when that applies" | exact |
| `docs/architecture/decision_log.md` (append L33) | config/record | event-driven (append-only ledger) | `docs/architecture/decision_log.md` — L32 ("amends L18") | exact — same amends-by-name, append-only shape |
| `docs/tech_debt/active/*.md` → `resolved/*.md` + `INDEX.md` rows | config/record | CRUD (move/update) | `docs/tech_debt/resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` + `INDEX.md`'s Resolved table | exact — same `Status`/`Resolved in`/`git mv`/INDEX-row-move mechanics |

## Pattern Assignments

### `src/spur/calc.py` — new warning branch in `derive()` (pure-maths, request-response)

**Analog:** `src/spur/calc.py`, the tip-chamfer branch inside `derive()` (lines ~974-980)

**Core pattern to copy** (printed-resolution comparison, verbatim from the file):
```python
tch = tip_chamfer_effective(p)
if tch < round(p.tip_chamfer, 3):
    # A limit only actually binds when it sits below the request at the 0.001 mm
    # resolution the chamfer is cut at (tip_chamfer_effective rounds to 3 dp;
    # model.py cuts exactly that value, L08) -- this is the original comparison
    # from before WR-01's fix, restored. ...
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
```

**New branch (D-01/D-02's content; position after the existing root-fillet branch, its
cause's neighbour — `rfil = root_fillet(p)` is already bound just above):**
```python
rfil = root_fillet(p)
if rfil < p.root_fillet:
    warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
# D-01: compare at the printed (3 dp) resolution, never the raw float — same rule as
# the tip-chamfer branch above (10-REVIEW.md CR-01).
h = spline_start(pr, rfil) - pr.r
if round(h, 3) > 0:
    warnings.append(
        f"The flank starts with a straight chord reaching {h:.3f} mm above the pitch "
        "circle, where it deviates from the involute: the root fillet is larger than "
        "half the dedendum.")
```
`pr = profile(p)` is already computed at the top of `derive()`; `spline_start` and
`root_fillet` are already imported/defined in `calc.py` (used together already in
`tip_chamfer_limit`, lines 258-281). No new import needed.

**Comment convention to match** (from the same block): state the rule by name
("10-REVIEW.md CR-01"), state *why* at the printed resolution, not just what.

---

### `src/spur/model.py` — `_outline` docstring (136-139), prose-only

**Analog:** the same docstring, corrected in place.

**Current (false) text:**
```
extended as a short chord onto the involute when the fillet needs room (the chord sits
in the non-working root zone and deviates from the involute by microns).
```

**D-13's replacement draft** (cites the new warning, names no unmeasured number):
```
extended as a short chord onto the involute when the fillet needs room (below the pitch
circle on the default gear; calc.derive warns when the chord ends above it, naming the
height).
```

---

### `tests/test_calc.py` — new parametrized warning test

**Analog:** `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (~590-656)

**Imports already present** (verified, test file's existing import block includes
`profile`, `root_fillet`, `spline_start` per RESEARCH.md citation — no new import line
needed beyond what the test body calls).

**Parametrize + full-string-assert shape to copy:**
```python
@pytest.mark.parametrize(("kw", "warning"), [
    pytest.param({}, None, id="default"),
    pytest.param({"profile_shift": 1.0, "pressure_angle": 14.5}, "<exact string>",
                 id="flank-above"),
    pytest.param({"profile_shift": 0.75, "pressure_angle": 20}, "<exact string>",
                 id="flank-above-2"),
    pytest.param({"profile_shift": 0.65, "pressure_angle": 14.5}, None, id="below-step"),
    pytest.param({"profile_shift": 0.70, "pressure_angle": 14.5}, "<exact string>",
                 id="above-step"),
    pytest.param({"profile_shift": 0.75, "pressure_angle": 20, "root_fillet": 0.40}, None,
                 id="fillet-below-step"),
    pytest.param({"profile_shift": 0.75, "pressure_angle": 20, "root_fillet": 0.45},
                 "<exact string>", id="fillet-above-step"),
])
def test_a_root_lead_in_above_the_pitch_circle_is_warned(
        kw: dict[str, object], warning: str | None) -> None:
    """D-01 (printed-resolution compare), D-03 (seven measured rows: the three debt
    configurations plus a profile_shift step pair at pa 14.5 and a root_fillet step pair
    at {0.75, 20} — the default 25 degree pressure angle caps the fillet before any
    crossing, so the profile_shift pair must sit at pa 14.5 (the field-step trap)."""
    p = GearParams.model_validate(kw)
    d = derive(p)
    lead_in_warnings = [w for w in d.warnings if w.startswith("The flank starts")]
    assert lead_in_warnings == ([warning] if warning else [])
```
**D-03's rule:** the `{h:.3f}` substitution in each expected string must be captured by
running the pinned code once (`.venv/bin/python`), never hand-typed — "0.0375 is not
exact in binary; its 3-dp print is the code's to decide."

---

### `tests/test_model.py` — closed-form oracle beside `_spoke_bar_area`

**Analog:** `_spoke_bar_area` (1111-1124) — pure math, derivation in the docstring,
"matching the built solid rather than a pinned literal."

```python
def _spoke_bar_area(rh: float, rr: float, o: float) -> float:
    """One spoke bar's area (D-01/D-02), analytic: model._spoke_sector's foot() puts
    every bar corner exactly on the hub/rim circle, so the bar's straight sides sit at
    theta = +-asin(o / r) on the circle of radius r for every r between rh and rr -- ...
    (measured 2026-09-29: formula and kernel agree to 1e-9 mm3 on the default gear's
    SPOKES12 row) rather than a pinned literal.
    """
    def s(r: float) -> float:
        return r * r * math.asin(o / r) + o * math.sqrt(r * r - o * o)
    return s(rr) - s(rh)
```

**New helper, same shape (name Claude's discretion;
`_filleted_spoke_sector_area(rh, rr, o, rho, n)` per D-08).** A fully worked,
kernel-verified reference implementation (four configurations, worst gap 6.8e-11 mm³)
is in `14-RESEARCH.md` § "The filleted-spoke closed form" — copy its derivation
comments into the new helper's docstring, dated and measured per this project's comment
convention ("Measured 2026-10-02 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1: ..."). D-09:
the helper must never call `_fillet_corner` — it re-derives the tangent quadratic itself.

**Docstring/comment convention to match** (from `_spoke_bar_area` and the proof test's
own docstring): name the measurement date, the kernel version pin, and the agreement
figure; demote the old pinned literal to a comment exactly like the sharp-spoke row
already demotes nothing (new precedent here) — follow L30's existing citation style
instead: "the pinned literal `2934.725405` ... first measurement 2026-09-29 on cadquery
2.8.0 / cadquery-ocp 7.9.3.1.1."

---

### `tests/test_model.py` — tightened shared assertion (D-05)

**Analog / exact target:** `_assert_the_cutout_is_what_derive_prints`, line 1196:
```python
assert plain.Volume() - cut.Volume() == pytest.approx(d_volume, rel=1e-6)
```
**Becomes:**
```python
assert plain.Volume() - cut.Volume() == pytest.approx(d_volume, abs=1e-9)
```
D-06: measure all four rows' (holes, spokes-sharp, spokes-filleted, cells) gaps at the
current `rel=1e-6` bar first, print/record each gap, confirm all four clear `1e-9`
*before* flipping this line — a miss halts at a checkpoint (shape: 13-LATENCY-BAR's
D-09 halt-checkpoint precedent in `13-CONTEXT.md`) rather than being loosened.

**`spokes-filleted` row's `d_volume=2934.725405` literal** (currently in
`test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` and
`test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`, both reading the same
literal) becomes a call to the new closed-form helper, with the literal demoted to a
docstring/comment citing its provenance ("first measurement 2026-09-29 ... 2934.725405
mm³").

---

### `tests/test_model.py` — tripwire (D-10)

**Analog:** `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` (1286-1320) —
the monkeypatch-then-`pytest.raises(AssertionError)` shape:
```python
monkeypatch.setattr("spur.model._cut_body", lambda solid, _p, _pr: solid)
p0 = GearParams(recess_sides="none")
p = GearParams.model_validate(kw)
assert derive(p).cutout_hub_wall is not None  # the number still prints -- L08's failure
with pytest.raises(AssertionError):
    _assert_the_cutout_is_what_derive_prints(
        _build_checked(p), _build_checked(p0), p, p0,
        d_faces=d_faces, d_edges=d_edges, d_volume=d_volume,
        hub_angle=angle, rim_angle=angle)
```
**New row/variant (D-10):** monkeypatch `spur.model._fillet_corner` (current signature
at `src/spur/model.py:98-130`, `inside=True` branch) so its tangent `t` shifts by a
small additive amount (~+0.01 mm per D-10/RESEARCH Pitfall 3 — a shift, never the far
root) on a solid that still builds; assert the (now `abs=1e-9`) cutout assertion raises
`AssertionError` while `derive(p).spoke_fillet_effective` still prints. `_spoke_sector`
resolves `_fillet_corner` through the module global (confirmed in CONTEXT.md D-10), so
`monkeypatch.setattr("spur.model._fillet_corner", ...)` is sufficient — same technique
as the `_cut_body` patch above, just a different target function.

---

### `README.md` — root-fillets bullet (~225-228)

**Analog (citation style to match):** the tip-chamfer bullet two lines below, "...
measured; decision log L29", and the undercut bullet above, "... the UI warns when that
applies."

**Current bullet:**
```
- Root fillets are computed analytically in the 2D outline rather than with the kernel's
  fillet operator, which is far slower on a many-toothed profile. Where a fillet needs
  room above the base circle, the flank starts with a short chord onto the involute,
  in the non-working root zone.
```

**D-12's working draft replacement:**
```
- Root fillets are computed analytically in the 2D outline rather than with the kernel's
  fillet operator, which is far slower on a many-toothed profile. Where a fillet needs
  room above the base circle, the flank starts with a short chord onto the involute --
  1.188 mm below the pitch circle on the default gear, and above it when the root
  fillet exceeds half the dedendum, `(1.25 - x)*m / 2`, in which case `warnings` says
  how far.
```

---

### `docs/architecture/decision_log.md` — new L33

**Analog:** L32 — "The concurrent latency bar, demonstrated on the harness as it stands
(amends L18)" (lines ~1427+). Shape to copy:
- Title: "L33 — \<topic\> (amends L09/L10 and L30)" — D-11's two-headed, append-only form.
- Opening line pattern: "L18 stays as written; this entry amends its ... paragraph with
  what was measured in Phase 13." → for L33: "L09/L10 and README's root-fillets claim
  stay as written; this entry amends the claim that the lead-in sits in the non-working
  root zone, and L30's 'pinned, not derived' clause, with what Phase 14 measured and
  proved."
- Bold lead sentences per sub-point, citing concrete evidence files/numbers inline
  (e.g., `13-LATENCY-INVESTIGATION.md § Verdict` style citations) — L33 should similarly
  cite `tests/test_calc.py`'s new test, the seven D-03 rows, and the closed-form helper's
  per-row measured gaps (D-05).
- No edit to L09/L10/L30's own text (D-11, Phase 12 D-18 precedent) — amend by a new,
  separate, append-only entry only.

---

### `docs/tech_debt/active/*.md` → `resolved/*.md`, `INDEX.md`

**Analog:** `docs/tech_debt/resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`
plus its `INDEX.md` Resolved-table row.

**Fields to set** (from `TEMPLATE.md`'s own instruction and the resolved exemplar):
```
Status: resolved
Resolved in: <commit sha>
```
plus a new `## Resolution (YYYY-MM-DD)` section at the bottom naming the actual fixing
commit's subject line, what was chosen among the file's own "Next step" options, and
pointing at the new tests/evidence — exactly the exemplar's shape ("`Resolved in: e46ed34`
is Plan 06-02 Task 1's commit ... What now exists: ... Evidence: ...").

`git mv docs/tech_debt/active/<file>.md docs/tech_debt/resolved/<file>.md` in the same
commit as the fix (CLAUDE.md; D-14).

`INDEX.md` row move — from the Active table to the Resolved table, same two-column shape
(`| Item | Resolved in |`), same commit:
```
| [The root fillet's straight lead-in can reach above the pitch circle](resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md) | `<sha>` -- see the file's own `Resolved in:` field |
```
(and the same pattern for the second debt file, in the closed-form commit, per D-14).

## Shared Patterns

### Printed-resolution comparison before warning
**Source:** `src/spur/calc.py`, `derive()`'s tip-chamfer branch (~974-980) and
`tip_chamfer_limit()` (258-281, the existing consumer of `spline_start`/`root_fillet`
together).
**Apply to:** the new root-lead-in warning branch in `calc.py`.
```python
if round(h, 3) > 0:
    warnings.append(f"... {h:.3f} mm ...")
```
Never compare the raw float — a crossing can sit arbitrarily close to zero (D-03's
0.0125 mm step), and the printed number must never show a false positive from float
residue.

### Full-string warning assertion (never a prefix)
**Source:** `tests/test_calc.py::test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`,
line ~648:
```python
tip_warnings = [w for w in d.warnings if w.startswith("Tip chamfer")]
assert tip_warnings == ([warning] if warning else [])
```
**Apply to:** the new warning's test — filter on its own distinguishing prefix
("The flank starts"), assert the full string, not a substring (CR-01: "a prefix assert
cannot see a wrong suffix").

### Pure-math oracle beside the kernel-built proof, never reusing production code
**Source:** `tests/test_model.py::_spoke_bar_area` (1111-1124) and D-09's explicit rule.
**Apply to:** the new `_filleted_spoke_sector_area` helper — `math` only, no `cadquery`
import, no call into `spur.model._fillet_corner`; derivation lives in the function's own
docstring, dated and measured.

### Monkeypatch-then-raise tripwire
**Source:** `tests/test_model.py::test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`
(1286-1320).
**Apply to:** the new `inside=True` root-perturbation tripwire — same
`monkeypatch.setattr("spur.model.<target>", ...)` / `pytest.raises(AssertionError)`
wrapping of `_assert_the_cutout_is_what_derive_prints`, while `derive()` still prints
the relevant number (the L08 "number still prints" assertion stays as a guard line).

### Append-only decision log, amends-by-name
**Source:** `docs/architecture/decision_log.md` L32 ("amends L18"), L30's own untouched
text (Phase 12 D-18 precedent).
**Apply to:** L33 — new entry only, cites L09/L10/L30 by id, never edits their text.

### Mechanical, same-commit debt retirement
**Source:** `docs/tech_debt/TEMPLATE.md`'s own closing comment and the
`2026-09-25-commit-msg-hook...` resolved exemplar.
**Apply to:** both debt files — `Status: resolved`, `Resolved in: <sha>`, `git mv`,
`INDEX.md` row moved, all in the fixing commit.

## No Analog Found

None — every file under change in this phase has a close, exact-match analog already in
the codebase (CONTEXT.md's own `<code_context>` names them all).

## Metadata

**Analog search scope:** `src/spur/calc.py`, `src/spur/model.py`, `tests/test_calc.py`,
`tests/test_model.py`, `README.md`, `docs/architecture/decision_log.md`,
`docs/tech_debt/{active,resolved}/`, `docs/tech_debt/INDEX.md`, `docs/tech_debt/TEMPLATE.md`.
**Files scanned:** 9 target files + 8 analog source reads (all read in full or by
targeted line range this session).
**Pattern extraction date:** 2026-10-02
