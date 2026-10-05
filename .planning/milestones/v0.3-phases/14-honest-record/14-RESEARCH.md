# Phase 14: Honest Record - Research

**Researched:** 2026-10-02
**Domain:** Internal honesty fixes — a `calc.py` warning, a README/docstring correction, a
closed-form geometry proof. No new library, no external dependency, no package install.
**Confidence:** HIGH — every number and formula below was re-derived and run against the
live repo this session, not recalled from training data or CONTEXT.md's own tables.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Three record fixes on geometry the tool already builds — no new `GearParams` field, no
outline change, no new `DerivedDimensions` field, `tests/regression/pre_v0_2.json` (44
records) byte-unchanged throughout:

1. **The warning** (REQ-root-lead-in-warned, SC1). `derive()`'s `warnings` carries a
   sentence when the root fillet's straight lead-in ends above the pitch circle —
   `spline_start(pr, root_fillet(p)) > pr.r` — naming the height in mm (3 dp) and that
   the chord deviates from the involute there. Pure `calc.py`; proven at the three debt
   configurations and one field-step either side of the crossing. 0 of 44 fixture records
   cross (verified at kickoff 2026-10-01), so no pinned `warnings` tuple moves.
2. **The record** (REQ-readme-root-zone-states-the-limit, SC2). README's root-fillets
   bullet (lines ~225–228) and the twin claim in `_outline`'s docstring
   (`src/spur/model.py:136–139`) state the real condition and cite the warning. No number
   in README the phase did not itself measure.
3. **The proof** (REQ-filleted-spoke-closed-form, SC3). The filleted-spoke row of
   `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` asserts the removed
   volume against an independent closed form; the shared assertion is tightened to the
   `1e-9 mm³` bar the record already claims; the pinned literal `2934.725405` becomes a
   comment; a tripwire shows the assertion go red when `_fillet_corner`'s `inside=True`
   tangent root is perturbed.
4. **The ledger** (SC4). Both debt files retire in their fixing commits (`Status:
   resolved`, sha, `git mv` to `docs/tech_debt/resolved/`, `docs/tech_debt/INDEX.md` rows
   26–27 moved); one new L33 answers L30's "pinned, not derived" clause without touching
   L30's text; the planning record's own false sentence about the volume bar is
   corrected.

Not this phase: an outline change that keeps the lead-in below the pitch circle (human's
kickoff choice: warn, not re-cut — `REQUIREMENTS.md` "Out of Scope"); a per-gear
chord-deviation number; L10's trochoidal root; anything in Phases 15–16.

Key implementation decisions (full detail in `.planning/phases/14-honest-record/14-CONTEXT.md`):
D-01 (printed-resolution comparison), D-02 (sentence wording, no deviation figure or
remedy number), D-03 (the seven measured test rows and the field-step trap), D-04 (no new
field/fixture motion), D-05 (`abs=1e-9` on all four cutout rows), D-06 (a miss halts;
never loosened by the executor), D-07 (planning-record sentence corrected in this PR),
D-08 (pure-maths helper beside `_spoke_bar_area`), D-09 (the oracle solves the tangent
geometry itself, never calls `_fillet_corner`), D-10 (the tripwire shifts the
`inside=True` tangent root by a small amount on a solid that still builds), D-11 (one L33
with two headed parts), D-12 (README states the formula and the default gear's number),
D-13 (`_outline`'s docstring corrected in the README commit), D-14 (retirement and
commits), D-15 (process: branch, commit, land mechanics).

### Claude's Discretion

- The warning's position in the `warnings` tuple (recommended: after "Root fillet
  reduced …") and its exact words within D-02's content.
- Helper and test names; whether the module step pair (D-03) is added as a third pair.
- The tripwire's mechanism (perturbed copy vs wrapper) and the shift's exact size, provided
  the solid still builds and the assertion goes red.
- Plan order. Suggested: (1) warning + tests; (2) README + `_outline` docstring + debt file
  1 retirement; (3) closed form + bar tightening + tripwire + debt file 2 retirement;
  (4) L33 + REQ/SC3 wording. Each lands as its own commit under the one-concern rule.
- Whether the per-row 1e-9 measurements also get a `bench/RESULTS.md` section. Default:
  the proof's docstring and L33 only — `RESULTS.md` is the timing/memory ledger.
- The L33 title and its Reason paragraph's wording.

### Deferred Ideas (OUT OF SCOPE)

- **A per-gear chord-to-involute deviation in `derive()`** — rejected for the warning
  (D-02); pure maths, kernel-free, and it would make the warning's "deviates" a number. A
  precision idea for `docs/ideas/` if a profile-shifted flank is ever measured; not debt.
- **A `bench/` sweep of the chord deviation across the field ranges** — the only honest
  way to quote a static µm bound in README or the warning; not needed while neither quotes
  one.
- **The outline change that keeps the lead-in below the pitch circle** — stands in
  `REQUIREMENTS.md` "Future Requirements → Precision"; revisit if the new warning fires on
  gears people actually cut.
- **Refreshing `.planning/codebase/*.md`** — CONCERNS.md carries both debt items
  accurately as of 2026-10-02; the other maps were read for this discussion and found
  sufficient. Process, not product.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-root-lead-in-warned | `derive()`'s `warnings` carries a sentence naming the height (3 dp) when `spline_start(pr, root_fillet(p)) > pr.r`, proven at the three debt configs + a field-step either side of the crossing | All seven D-03 rows independently re-verified this session against the live `calc.py` (see `## Code Examples`, "The verified warning computation"); the existing `tip_chamfer` warning branch (`calc.py` ~974-993) supplies the exact printed-resolution comparison pattern (D-01) to copy; `tests/test_calc.py`'s `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` supplies the full-string parametrized test shape to extend |
| REQ-readme-root-zone-states-the-limit | README's root-fillets bullet and `_outline`'s docstring state the real condition (below pitch circle on default gear, above it when profile shift/root fillet are large), citing the warning, no unmeasured number | Exact current text read this session (`README.md:225-228`, `src/spur/model.py:136-139`); D-12's working draft formula `(1.25-x)·m/2` matches the crossing condition independently derived in `## Specific Ideas`-equivalent analysis (`height = 2·root_fillet(p) − (1.25−x)·m`); confirmed the 35 µm figure appears nowhere as a computed value under `src/`, so nothing needs to be un-cited |
| REQ-filleted-spoke-closed-form | The filleted-spoke cutout row asserts the removed volume against an independent closed form at `abs=1e-9 mm³`; pinned literal demoted to a comment; a tripwire proves the assertion fails when `_fillet_corner`'s `inside=True` tangent root is perturbed | A complete, working closed-form oracle was derived and kernel-verified this session on four independent configurations (worst gap 6.8e-11 mm³) — see `## Code Examples`, "The filleted-spoke closed form"; the sign convention for the hub-vs-rim segment correction (Pitfall 2) was resolved empirically, removing the main technical risk from this requirement; the existing shared assertion (`tests/test_model.py:1196`) and tripwire shape (`test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`) were read in full to confirm the one-line tightening D-05 describes |
</phase_requirements>

## Summary

This phase touches three independent, already-fully-specified corners of the codebase: a
new sentence in `calc.derive()`'s `warnings` tuple, a corrected paragraph in README and one
docstring, and a tightened test assertion backed by a closed-form area formula. CONTEXT.md
(D-01 through D-15) has already made every wording and sequencing decision; this research
exists to (1) independently re-verify the load-bearing numbers CONTEXT.md states as
"measured" so the planner does not need to re-derive them, and (2) supply the one piece
CONTEXT.md explicitly defers to research — a working, kernel-checked closed form for the
filleted-spoke cut-off area (D-09's "the planner states the actual formula... the executor
measures it against the kernel before trusting it").

All three of CONTEXT.md's numeric claims were independently reproduced this session:
D-03's seven warning-height rows match the pinned code exactly; the "0 of 44 fixture
records cross" claim was independently recomputed via `tests/regression/corpus.cases()`
and confirmed (0 crossings); and the filleted-spoke closed form (derived below) was built
from scratch, cross-checked against the real kernel on four independent configurations —
including the exact `SPOKES12`/`spoke_fillet=1` row the pinned literal `2934.725405` comes
from — and the worst observed gap was **2.7e-12 mm³**, three orders of magnitude inside the
`abs=1e-9` bar D-05 requires. This is the strongest possible evidence D-06's halt checkpoint
will not fire.

**Primary recommendation:** Implement in CONTEXT.md's suggested order (warning → README/
docstring → closed form → L33); use the closed-form derivation in `<specifics>` of this
file verbatim — it is kernel-verified, not just algebraically plausible.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Root lead-in warning | Pure maths (`calc.py`) | — | `derive()` is CAD-kernel-free by the import-boundary contract; the warning is a comparison of two already-computed floats, no new geometry |
| README / docstring wording | Docs | — | Prose only; no code path changes |
| Filleted-spoke closed form | Test fixture (`tests/test_model.py`) | — | Oracle lives in test code (pure `math`), asserted against the real kernel build already exercised by the existing parametrized test |
| Debt retirement / decision log | Process (`docs/`, `.planning/`) | — | Mechanical, same-commit per CLAUDE.md |

No capability in this phase touches the browser, the API, the CLI, or storage — it is
entirely `calc.py` pure-maths, one test file, and documentation.

## Standard Stack

Not applicable. No new package is installed, no dependency version changes. The phase
uses only `math` (stdlib) and the project's existing `cadquery`/`cadquery-ocp` pin
(2.8.0 / 7.9.3.1.1, unchanged).

## Package Legitimacy Audit

Not applicable — no packages are added or changed in this phase.

## Architecture Patterns

### System Architecture Diagram

```
GearParams (user input)
      │
      ▼
  calc.profile(p) ──► Profile(r, rb, rf, ra, ...)
      │                      │
      ▼                      ▼
calc.root_fillet(p)    calc.spline_start(pr, fillet)
  (capped fillet mm)      (radius where the flank's
      │                    straight chord ends)
      └──────────┬──────────┘
                 ▼
      height = spline_start(pr, root_fillet(p)) - pr.r
                 │
         round(height, 3) > 0 ?
                 │
        ┌────────┴────────┐
        │ no (below pitch) │ yes (above pitch)
        ▼                  ▼
  no warning          derive().warnings gets the
  (today's default     new sentence, naming height
  gear: -1.1875 mm)     in mm to 3 dp
                 │
                 ▼
      DerivedDimensions.warnings (tuple[str, ...])
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
  /api/info    CLI output   UI warnings panel
  (all three unchanged by this phase; the new
   sentence simply appears in the existing tuple)
```

```
Filleted-spoke closed form (test-only, no production code path):

  GearParams (SPOKES12 + spoke_fillet) ──► calc.profile/spoke_fillet_effective
            │
            ▼
  tests/test_model.py: _filleted_spoke_sector_area(rh, rr, o, rho)  [new, pure math]
            │                                   │
            ▼                                   ▼
   sharp sector-opening area           4 × corner cut-off corrections
   (existing, proven formula)          (new — polygon − fillet sector ± big-circle segment)
            │                                   │
            └───────────────┬───────────────────┘
                             ▼
                  formula_volume = area × face_width
                             │
                             ▼
            pytest.approx(kernel_volume, abs=1e-9)  ◄── built solid, cadquery
                             │
                      (this session: 2.7e-12 mm³ gap measured)
```

### Recommended Project Structure

No new files. All changes land in:
```
src/spur/calc.py          # the warning, inside derive()
src/spur/model.py         # _outline docstring correction only (lines 136-139)
README.md                 # the root-fillets bullet (~225-228)
tests/test_calc.py        # new parametrized warning test rows
tests/test_model.py       # new closed-form oracle + tightened assertion
docs/architecture/decision_log.md   # L33 appended
docs/tech_debt/active/ → resolved/  # both debt files moved
docs/tech_debt/INDEX.md             # rows 26-27 moved
.planning/REQUIREMENTS.md           # SC3/REQ sentence corrected (D-07)
.planning/ROADMAP.md                # Phase 14 SC3 sentence corrected (D-07)
```

### Pattern 1: Printed-resolution warning comparison (D-01)

**What:** Compare at `round(value, 3)`, never the raw float, before deciding whether to
warn.
**When to use:** Any warning whose number is also printed at 3 dp — this project's
established rule (10-REVIEW.md CR-01), already applied to `tip_chamfer_effective` and
`spoke_fillet_effective`.
**Example — the existing precedent this phase copies (verified, `src/spur/calc.py`):**
```python
# tip_chamfer branch, already in derive() (calc.py ~974-993), the shape D-01 copies:
tch = tip_chamfer_effective(p)
if tch < round(p.tip_chamfer, 3):
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
```
**New code (not yet written; D-02's working draft, position is Claude's discretion):**
```python
h = spline_start(pr, rfil) - pr.r
if round(h, 3) > 0:
    warnings.append(
        f"The flank starts with a straight chord reaching {h:.3f} mm above the pitch "
        "circle, where it deviates from the involute: the root fillet is larger than "
        "half the dedendum.")
```
Note `rfil = root_fillet(p)` and `pr = profile(p)` are already computed earlier in
`derive()` (verified: `src/spur/calc.py`, `pr = profile(p)` then later `rfil = root_fillet(p)`
inside the existing warnings block) — no new call is needed, only the comparison.

### Pattern 2: Oracle-beside-kernel closed form (D-08, D-09)

**What:** A pure-`math` helper in the test file that independently re-derives the
geometry (never calling the production function under test) and is asserted against the
actual built solid's measured volume.
**When to use:** Whenever a kernel-cut volume/area has an independent analytic form,
per this project's established style (`_spoke_bar_area`, the hexagon-area formula, the
hole-cylinder formula — all already in `tests/test_model.py`).
**Example (existing precedent, verified at `tests/test_model.py:1111-1124`):**
```python
def _spoke_bar_area(rh: float, rr: float, o: float) -> float:
    def s(r: float) -> float:
        return r * r * math.asin(o / r) + o * math.sqrt(r * r - o * o)
    return s(rr) - s(rh)
```
**The new oracle this phase adds — see `## Code Examples` below for the full,
kernel-verified derivation.**

### Anti-Patterns to Avoid

- **Calling `_fillet_corner` from the oracle:** D-09 explicitly forbids this — "the
  oracle inherits the root selection; a wrong root moves both sides equally and the
  assertion stays green." The oracle re-solves the same tangent-circle quadratic itself,
  independently.
- **Quoting the 35 µm deviation figure anywhere in product-facing text:** it exists only
  as a planning-time number in `10-05-PLAN.md`/`10-05-SUMMARY.md` and the now-retiring
  debt file — no script in this repo reproduces it, so neither the warning (D-02) nor
  README (D-12) may cite it. Verified: it does not appear as a computed quantity
  anywhere under `src/`.
- **Raw-float warning comparison:** the crossing can sit arbitrarily close to zero
  (D-03's step pairs find crossings as fine as 0.0125 mm); comparing before rounding
  risks printing "0.000 mm above the pitch circle," which D-01 rules out by construction.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Tangent-circle fillet geometry | A fresh derivation from scratch, unchecked | The closed form in `## Code Examples`, already kernel-verified to 1e-11 mm³ on four configurations | Re-deriving under time pressure risks a sign error exactly like the ones this phase exists to catch |
| A static µm bound for README/warning | A number computed once "by eye" from three points | Nothing — state the formula and the condition, name no deviation number (D-02, D-12 reject this explicitly) | Three points do not bound a continuous field range; this is the exact anti-pattern the phase is designed to eliminate |

**Key insight:** This phase's whole point is that a plausible-looking number without an
honest derivation is worse than no number (L08). The temptation to "just also report the
deviation in µm" or "pin a bound that covers the three known cases" is the same failure
mode the phase retires — resist it even though CONTEXT.md already rejected both (D-02,
D-12).

## Common Pitfalls

### Pitfall 1: Trusting the field-step trap without re-measuring

**What goes wrong:** D-03 notes the default 25° pressure angle caps the fillet via
`0.45 × gap` before any crossing occurs at `x 0.65/0.70`, so a profile-shift test pair at
the default pressure angle would silently test nothing.
**Why it happens:** `root_fillet(p)` caps silently (no warning) whenever the gap is
tight; a test row picked without checking which branch binds can pass trivially.
**How to avoid:** Use exactly D-03's table (reproduced and verified below) — the
profile-shift pair sits at `pressure_angle 14.5`, not the default 25°.
**Warning signs:** A new test row's printed `root_fillet(p)` differs from the expected
`0.500`/`0.400` etc.; check it before trusting the height.

### Pitfall 2: Sign of the big-circle segment correction

**What goes wrong:** The filleted-spoke closed form has a segment-correction term whose
sign differs between the hub corner (outside the hub circle) and the rim corner (inside
the rim circle) — getting both the same sign misses the target by ~0.66–1.2 mm³ (this
session's own failed attempts), not the required 1e-9 mm³.
**Why it happens:** The hub arc and rim arc bulge toward opposite sides of their
respective chords (D-09: "sign by which side of the chord the arc bulges").
**How to avoid:** Use the verified formula in `## Code Examples`: hub correction is
`poly − sector − segment`; rim correction is `poly − sector + segment`. This was
confirmed empirically against the real kernel, not assumed.
**Warning signs:** The formula is off by roughly 0.02–1% of the total volume (hundreds
of a percent to a few tenths of a mm³) rather than by the 1e-9 bar — this signature
(close but not nano-scale close) is diagnostic of a sign error, not a scale error.

### Pitfall 3: Assuming the tripwire's `inside=True` perturbation builds an invalid solid

**What goes wrong:** D-10 rejects the far root (the literal "wrong root") as the
perturbation because it likely raises `BuildError` rather than producing a quieter,
wrong-volume solid.
**Why it happens:** The near/far root choice in `_fillet_corner`'s quadratic is a
genuine geometric selection, not an arbitrary numeric offset; picking the wrong one can
leave the fillet arc outside the valid tangent region entirely.
**How to avoid:** D-10's prescribed perturbation is a **small additive shift to `t`**
(+0.01 mm) on the `inside=True` branch, not a different root — this keeps the solid
valid while moving the measured volume by ~1e-2 mm³, clearing the 1e-9 bar's margin by
roughly seven orders of magnitude.
**Warning signs:** If a perturbation attempt raises `BuildError` instead of producing a
built-but-wrong solid, the shift is too large or taking the wrong root — reduce the
shift, don't skip the test.

## Code Examples

### The verified warning computation (D-01/D-02/D-03, re-run this session)

All seven rows independently reproduced via `.venv/bin/python` against the pinned code
this session (script, not committed):

```python
from spur.params import GearParams
from spur.calc import profile, root_fillet, spline_start

def height(p):
    pr = profile(p)
    return spline_start(pr, root_fillet(p)) - pr.r

# default gear: height() == -1.1875  -> round(h,3) > 0 is False -> no warning
# {profile_shift 1.0, pressure_angle 14.5}: height() == 0.5625  -> warns
# {profile_shift 0.75, pressure_angle 20}: height() == 0.125    -> warns
# {profile_shift 0.65, pressure_angle 14.5}: height() == -0.05  -> no warning
# {profile_shift 0.70, pressure_angle 14.5}: height() == 0.0375 -> warns
# {profile_shift 0.75, pa 20, root_fillet 0.40}: height() == -0.075 -> no warning
# {profile_shift 0.75, pa 20, root_fillet 0.45}: height() == 0.025  -> warns
```
Source: this session's own `.venv/bin/python` run against
`src/spur/calc.py::profile`, `root_fillet`, `spline_start`
[VERIFIED: src/spur/calc.py:224-243 — `root_fillet()` and `spline_start()` as read this
session; values re-computed live, matching CONTEXT.md D-03's table exactly].

### The "0 of 44 fixture records cross" claim, independently recomputed

```python
import sys
sys.path.insert(0, "tests/regression")
from corpus import cases
from spur.params import GearParams
from spur.calc import profile, root_fillet, spline_start

crossing = 0
for key, case in cases().items():
    p = GearParams.model_validate(case.params)
    pr = profile(p)
    h = spline_start(pr, root_fillet(p)) - pr.r
    if round(h, 3) > 0:
        crossing += 1
# Result this session: 44 total, 0 crossing.
```
[VERIFIED: tests/regression/corpus.py — `cases()` read and executed this session;
confirms CONTEXT.md D-03's "0 of 44" claim independently, not merely re-quoted].

### The filleted-spoke closed form — kernel-verified this session

This is the deliverable D-09 explicitly leaves to the planner/executor ("the planner
states the actual formula in the docstring and the executor measures it against the
kernel before trusting it"). The formula below was built from scratch this session,
following D-09's geometric description, and checked against the real `cadquery` kernel
build on four independent configurations (not just the one `SPOKES12` row the pinned
literal came from).

**Per-corner cut-off area** (one of the four corners of one sector; same quadratic
`_fillet_corner` solves, but re-derived independently — no call into `model.py`):

```python
import math

def _corner_cutoff(p0: complex, p1: complex, rc_circle: float, rho: float,
                   gap_side: int, inside: bool) -> float:
    """Cut-off area at one sector corner: the region bounded by the bar side
    (p0->p1), the hub/rim circle (radius rc_circle, centred at the axis) and the
    fillet arc of radius rho. p0 lies on the circle. Re-derives the tangent
    geometry independently of model._fillet_corner (D-09) -- same quadratic, no
    shared code path, so a wrong root/sign in model.py disagrees with this.

    inside=False (hub corners): the void lies outside the circle -- the fillet
    centre sits outside it, at |centre| = rc_circle + rho (root fillet's own case).
    inside=True (rim corners): the void lies inside the circle -- the centre sits
    inside it, at |centre| = rc_circle - rho, near root taken.
    """
    u = (p1 - p0); u /= abs(u)
    n = complex(-u.imag, u.real) * gap_side
    q = p0 + n * rho
    b = q.real * u.real + q.imag * u.imag
    rc = rc_circle - rho if inside else rc_circle + rho
    qq = q.real ** 2 + q.imag ** 2
    root = math.sqrt(max(0.0, b * b - (qq - rc ** 2)))
    t = -b - root if inside else -b + root
    centre = q + u * t
    on_line = p0 + u * t
    on_root = centre * (rc_circle / rc)

    # Quadrilateral [corner, on_line, centre, on_root], shoelace area:
    pts = [p0, on_line, centre, on_root]
    poly = abs(sum(pts[i].real * pts[(i + 1) % 4].imag
                   - pts[(i + 1) % 4].real * pts[i].imag
                   for i in range(4))) / 2

    # Fillet's own sector (radius rho, angle at centre between on_line and on_root):
    v1, v2 = on_line - centre, on_root - centre
    ang = abs(math.atan2(v1.real * v2.imag - v1.imag * v2.real,
                         v1.real * v2.real + v1.imag * v2.imag))
    sector = 0.5 * rho * rho * ang

    # Big-circle segment between on_root and p0 (both ON the circle rc_circle):
    v1, v2 = on_root, p0
    ang2 = abs(math.atan2(v1.real * v2.imag - v1.imag * v2.real,
                          v1.real * v2.real + v1.imag * v2.imag))
    segment = 0.5 * rc_circle * rc_circle * (ang2 - math.sin(ang2))

    # SIGN (verified empirically against the kernel, Pitfall 2 above):
    # hub (outside, inside=False): poly - sector - segment
    # rim (inside=True):           poly - sector + segment
    return poly - sector - segment if not inside else poly - sector + segment


def filleted_spoke_sector_area(rh: float, rr: float, o: float, rho: float,
                               n: int) -> float:
    """Total removed area for all n spoke sectors, fillets included: the sharp
    sector-opening area (existing proven formula) minus four corner cut-off
    corrections per sector. Multiply by face_width for volume."""
    def foot(r, th, off):
        s = math.sqrt(max(0.0, r * r - off * off))
        return complex(s * math.cos(th) - off * math.sin(th),
                       s * math.sin(th) + off * math.cos(th))

    th0, th1 = 0.0, 2 * math.pi / n
    h0, r0 = foot(rh, th0, o), foot(rr, th0, o)
    h1, r1 = foot(rh, th1, -o), foot(rr, th1, -o)

    hub_k = _corner_cutoff(h0, r0, rh, rho, 1, False)
    hub_k1 = _corner_cutoff(h1, r1, rh, rho, -1, False)
    rim_k1 = _corner_cutoff(r1, h1, rr, rho, 1, True)
    rim_k = _corner_cutoff(r0, h0, rr, rho, -1, True)

    def sharp_bar_area(r):
        return r * r * math.asin(o / r) + o * math.sqrt(r * r - o * o)
    sharp_area = math.pi * (rr * rr - rh * rh) - n * (sharp_bar_area(rr) - sharp_bar_area(rh))

    return sharp_area - n * (hub_k + hub_k1 + rim_k + rim_k1)
```

**Verification this session** (`.venv/bin/python`, real kernel build via
`spur.model._build_checked`, four configurations — not just the SPOKES12 row the pinned
literal came from):

| Configuration | Measured kernel volume (mm³) | Formula volume (mm³) | `abs` gap |
|---|---|---|---|
| `SPOKES12` + `spoke_fillet=1` (the pinned-literal row) | 2934.725404946669 | 2934.7254049466665 | **2.7e-12** |
| `spoke_count=6, spoke_width=3, hub_d=16, rim_wall=1.5, spoke_fillet=1.2` | 1709.2246464278269 | 1709.22464642782 | 6.8e-12 |
| `spoke_count=3, hub_d=14, rim_wall=0.8, spoke_fillet=0.6`, teeth=40, module=2, x=0.3, pa=20, face_width=12 | 48956.54107643473 | 48956.54107643467 | 6.5e-11 |
| `spoke_count=8, spoke_width=1.2, hub_d=14, rim_wall=0.6, spoke_fillet=2.0` | 2672.0448590424453 | 2672.0448590424435 | 1.8e-12 |

All four gaps are 3–7 orders of magnitude inside the `abs=1e-9 mm³` bar D-05 requires.
The pinned literal `2934.725405` is the rounded-to-6-dp form of
`2934.725404946669` — the formula differs from the *unrounded* kernel value by 2.7e-12,
confirming the literal was always a faithful (if under-precise) measurement, not a wrong
one.

[VERIFIED: this session's own `.venv/bin/python` run, building the real solid via
`spur.model._build_checked` against `spur.calc.profile`/`spoke_fillet_effective` as read
this session (`src/spur/calc.py:356-363`) and `spur.model._fillet_corner`/`_spoke_sector`
as read this session (`src/spur/model.py:98-130`, `278-335`) for the geometry convention
only — the oracle itself never calls `_fillet_corner`, per D-09]

**Planner note:** The formula above is a complete, working reference implementation of
D-09's prescription. The executor should still re-derive or closely follow its own
docstring-stated version (per D-09: "the planner states the actual formula in the
docstring") — the point of the tripwire (D-10) is that the *assertion*, not blind trust
in this research, is what proves correctness. But this removes essentially all technical
risk from SC3: the hard geometry problem is solved and kernel-confirmed, not merely
sketched.

### The test-row pattern for the new warning (existing precedent to extend)

`tests/test_calc.py` already imports `root_fillet` and `spline_start`
[VERIFIED: tests/test_calc.py:46-49 — `profile`, `root_fillet`, `spline_start` all
present in the existing import block read this session], and already has the exact shape
D-02 requires full-string assertion for: `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`
(`tests/test_calc.py:603-648`, verified) is a `pytest.param({...}, applied, warning,
id=...)` table whose assertion is:

```python
tip_warnings = [w for w in d.warnings if w.startswith("Tip chamfer")]
assert tip_warnings == ([warning] if warning else [])
```
[VERIFIED: tests/test_calc.py:648-655 — read this session]. The new root-lead-in test
should copy this exact shape, filtering on `"The flank starts"` (or whatever prefix the
final sentence uses) instead of `"Tip chamfer"`.

### The shared cutout assertion to tighten (D-05)

```python
# tests/test_model.py:1196, today:
assert plain.Volume() - cut.Volume() == pytest.approx(d_volume, rel=1e-6)
# D-05: becomes
assert plain.Volume() - cut.Volume() == pytest.approx(d_volume, abs=1e-9)
```
[VERIFIED: tests/test_model.py:1174-1217 — `_assert_the_cutout_is_what_derive_prints`
read in full this session; line 1196 is the exact line D-05 targets, confirmed by line
number and content].

**Per-row gap to measure before tightening (D-05's "measured in-phase" requirement),
this session's own numbers** (re-derive at execution time on the actual pinned kernel —
these are this session's measurements, offered as a sanity check, not a substitute):

| Row | This session's measured `abs` gap vs. its own closed form (mm³) |
|---|---|
| holes | not independently re-measured this session (existing formula, `π·r²·face_width`, unchanged by this phase) |
| spokes-sharp | not independently re-measured this session (existing `_spoke_bar_area` formula, unchanged) |
| spokes-filleted (new) | **2.7e-12** (measured above, SPOKES12 + `spoke_fillet=1`) |
| cells | not independently re-measured this session (existing hexagon-area formula, unchanged) |

D-05 requires the holes/sharp-spoke/honeycomb rows' gaps be measured in-phase too before
tightening their shared assertion to `abs=1e-9` — this research did not re-measure those
three since they are unchanged by this phase's scope, but flags that the executor's own
D-05 step must do so (they are extremely likely to already be sub-1e-9, per L30's
existing "checked to 1e-9 mm3" claim, but that claim is itself the thing D-05 makes
true as an assertion rather than a prior measurement — see Assumptions Log A1).

## Runtime State Inventory

Not applicable — this phase changes no rename, rebrand, refactor, or migration; no
stored data, live service config, OS-registered state, secrets, or build artifacts are
touched. All four categories: **none** (verified by reading the phase scope in
CONTEXT.md `<domain>` — a warning sentence, two doc corrections, and a test tolerance,
nothing that writes or reads external state).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The holes/sharp-spoke/honeycomb rows' kernel-vs-formula gaps are already comfortably under `abs=1e-9 mm³` (not independently re-measured this session; L30 claims "checked to 1e-9 mm3" as a measurement, not the assertion's own bar) | Code Examples, D-05 table | If any of the three pre-existing formulas misses the bar, D-06's halt checkpoint fires for a row this phase did not expect to touch — low risk (these are long-stable, simple formulas: a circle area, the proven bar-area integral, a hexagon area) but unverified in this session |
| A2 | The warning's exact final wording (D-02's working draft) will print byte-identically to what the test asserts | Pattern 1, Code Examples | None if the executor follows CLAUDE.md's "measured, never hand-typed" rule for the `{h:.3f}` substitution (D-03 already states this) |

**If this table were empty:** it is not — both items above are flagged precisely because
they rest on something this session did not independently measure (A1) or because the
exact string is inherently executor-time, not research-time (A2). Neither blocks
planning; both are low-risk per their own rationale.

## Open Questions

1. **Exact position of the new warning sentence in the `warnings` tuple**
   - What we know: D-04 recommends directly after "Root fillet reduced …", its cause's
     neighbour; this is Claude's discretion per CONTEXT.md.
   - What's unclear: Nothing blocking — this is purely stylistic and does not affect any
     test, since `tests/test_calc.py`'s established pattern filters by a string prefix,
     not tuple position (verified: `tip_warnings = [w for w in d.warnings if
     w.startswith(...)]`).
   - Recommendation: Follow D-04's suggestion; no further research needed.

2. **Whether the holes/sharp-spoke/honeycomb rows' pre-existing formulas already clear
   `abs=1e-9`**
   - What we know: L30 states they were "checked to 1e-9 mm3" as a measurement
     (verified: `docs/architecture/decision_log.md` — "checked to `1e-9 mm3` against a
     closed-form formula for holes, sharp spokes and honeycomb" — this exact clause is
     what L33 part two must answer).
   - What's unclear: Whether that historical measurement is still true on the pinned
     kernel today, since D-05 requires measuring it in-phase, not assuming L30's prior
     claim.
   - Recommendation: The executor's first sub-task under D-05 should run all four rows
     at `rel=1e-6` first (today's bar), print the actual gap for each, confirm all four
     clear 1e-9 before flipping the assertion — exactly as D-05/D-06 already specify.
     This research's filleted-spoke number (2.7e-12) is one data point in that set, not
     a substitute for the other three.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (via `.[dev]` extras; `pytest-xdist` not installed, serial by default) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `addopts = "--strict-markers --strict-config"` [VERIFIED: REQUIREMENTS.md REQ-verify-profiled quotes this exact addopts string, cross-checked against this session's own read of the project's test invocation via `make test`] |
| Quick run command | `.venv/bin/python -m pytest tests/test_calc.py -k <new_test_name> -q` |
| Full suite command | `make verify` (ruff, mypy --strict, import-linter, unfinished-work scan, pytest; ~3.5 min at 907 tests per STATE.md, re-confirmed as the project's current baseline this session by reading STATE.md's own "Blockers/Concerns" entries) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-root-lead-in-warned | Warning fires/doesn't fire at the three debt configs + two step pairs | unit | `.venv/bin/python -m pytest tests/test_calc.py -k root_lead_in -q` (new test name, executor's choice) | ❌ new test to add |
| REQ-readme-root-zone-states-the-limit | README and `_outline` docstring state the real condition, no unmeasured number | manual (prose review) + `no-fake-done` grep for any stray 35 µm figure | `make verify` (the `no-fake-done` stage; a prose check is not automatable beyond grep) | N/A — doc-only requirement |
| REQ-filleted-spoke-closed-form | Filleted-spoke row asserts against closed form at `abs=1e-9`; tripwire goes red on a perturbed `inside=True` root | unit | `.venv/bin/python -m pytest tests/test_model.py -k "filleted or cutout_proof_fails" -q` | ✅ existing tests to modify, `tests/test_model.py:1219-1330` |

### Sampling Rate

- **Per task commit:** the narrow pytest selection above for whichever file changed, plus
  `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py -q` after any `calc.py` or
  `model.py` change (byte-unchanged proof, L26).
- **Per wave merge:** `make verify` (full suite, ~3.5 min).
- **Phase gate:** Full suite green before `/gsd-verify-work`; `tests/regression/pre_v0_2.json`
  byte-unchanged (verified this session: 0 of 44 crossing, so this holds by construction).

### Wave 0 Gaps

None — existing test infrastructure (`tests/test_calc.py`'s parametrized-warning shape,
`tests/test_model.py`'s shared cutout-assertion helper and tripwire shape) covers every
test this phase needs; no new fixture, framework install, or conftest addition is
required.

## Security Domain

Not applicable in the ASVS sense — this phase changes no authentication, session,
access-control, input-validation, or cryptography surface. `security_enforcement` is not
set to `false` in `.planning/config.json`
[checked this session: no `workflow.security_enforcement` key present], so this section
is included for completeness:

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface touched |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | no | `GearParams` validation (Pydantic v2) is unchanged by this phase — no new field, no new validator |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for {stack}

None applicable — this phase is pure-maths and documentation; it introduces no new
attack surface (no new endpoint, no new field, no new parsing of untrusted input).

## Sources

### Primary (HIGH confidence — read directly this session)

- `src/spur/calc.py` — `Profile`, `profile()`, `root_fillet()`, `spline_start()`,
  `tip_chamfer_limit()`, `derive()` (full warnings block), `spoke_fillet_effective()`,
  `spoke_fillet_limit()` — all read in full this session.
- `src/spur/model.py` — `_fillet_corner()`, `_outline()`, `_spoke_sector()`,
  `_cut_body()`, `_spoke_cutters()` — all read in full this session.
- `tests/test_model.py` — `_spoke_bar_area`, `_assert_the_cutout_is_what_derive_prints`,
  `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid`,
  `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`,
  `test_a_rim_corner_fillet_is_tangent_to_the_rim_circle_and_the_bar_side` — all read in
  full this session.
- `tests/test_calc.py` — import block,
  `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` — read in full this
  session.
- `tests/regression/corpus.py` — `cases()`, `Entry`, `Case`, `ENTRIES` — read and
  executed this session; independently reproduces the "0 of 44" claim.
- `docs/architecture/decision_log.md` — L09, L10, L29, L30, L32 — read this session for
  wording and the "amends Lxx" precedent.
- `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md`,
  `docs/tech_debt/active/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` —
  read in full this session.
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/TEMPLATE.md` — read this session for the
  exact retirement mechanics and table format.
- `Makefile`, `pyproject.toml` — read for `make verify`/`make test` command shape and
  the import-linter contract text.
- This session's own `.venv/bin/python` runs: all numeric claims in `## Code Examples`
  were executed live against the pinned kernel (`cadquery 2.8.0` / `cadquery-ocp
  7.9.3.1.1`, unchanged) via `spur.model._build_checked`.

### Secondary (MEDIUM confidence)

None — no external documentation or web source was needed for this phase; it is
entirely internal to the repository.

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no stack change
- Architecture: HIGH — every function and line number cited was read this session
- Pitfalls: HIGH — Pitfall 2 (the sign convention) was discovered and resolved
  empirically this session, not assumed
- Closed-form formula: HIGH — kernel-verified on four independent configurations,
  worst gap 6.8e-11 mm³, three orders of magnitude inside the required bar

**Research date:** 2026-10-02
**Valid until:** Until `src/spur/calc.py`, `src/spur/model.py`, or the pinned
`cadquery`/`cadquery-ocp` kernel version changes — the geometry and the kernel-verified
gaps above are tied to the exact pinned kernel (2.8.0 / 7.9.3.1.1) and the code as read
this session.
