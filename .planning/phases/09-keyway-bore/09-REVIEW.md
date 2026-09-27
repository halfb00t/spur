---
phase: 09-keyway-bore
reviewed: 2026-09-27T00:00:00Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - bench/RESULTS.md
  - bench/sweeps/keyway_bore.json
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/implementation.md
  - docs/architecture/solid-model/tactics.md
  - docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md
  - README.md
  - src/spur/calc.py
  - src/spur/model.py
  - src/spur/params.py
  - src/spur/static/app.js
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-09-27T00:00:00Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Reviewed the keyway-bore diff since `b522044`: the two new `calc.py` helpers
(`keyway_width_effective`, `keyway_corner_radius`, `keyway_flat_wall`), `bore_mouth_limit`'s
extension to take the keyway corner into account, the six new `check()` refusal rules, the
new `ROOT_CONTACT`-based round/D-flat chamfer-reach rule (L28/D-12), `model._cut_keyway`,
`DerivedDimensions`' two new fields, and the matching docs/bench/test changes.

`make verify` passes clean (396 tests, ruff, mypy --strict, import-linter, unfinished-work
scan). I re-derived the keyway geometry formulas by hand against the code and the numbers
the decision log and tests cite (`keyway_corner_radius`, `keyway_flat_wall`,
`keyway_floor_to_wall`, the bench sweep's "heaviest" row) and they all check out; I found no
crash, no domain-error (`acos`/`sqrt` out of range), and no discrepancy between a documented
number and what the code produces. The `check()` branch ordering (`if`/`elif` placement
around `keyed`, `has_keyway`, the D-flat range guard) is deliberately structured so that
`keyway_flat_wall`'s two `acos` calls are only ever reached with arguments proven to stay in
`[-1, 1]`; I traced that proof and it holds.

One real gap: the new round/D-flat bore-chamfer-vs-root rule (`ROOT_CONTACT`, 1e-9 mm)
is dramatically more permissive than every comparable rule in this codebase (hex bore,
keyway floor corner, recess) and lets a bore's chamfer land within microns of the root
circle — far below `MIN_WALL` — with a valid build and zero warning. See WR-01.

## Warnings

### WR-01: A round/D-flat bore's chamfer can land microns from the root circle with no warning at all

**File:** `src/spur/calc.py:18-31` (the `ROOT_CONTACT` constant) and `src/spur/calc.py:289-295`
(the `check()` rule that uses it)

**Issue:** `MIN_WALL` is documented, in its own comment, as "the thinnest wall allowed
**anywhere** in the body." Every other place a bore-derived feature can approach the root
circle enforces exactly that: the hex bore's corner-vs-root rule refuses at
`bore_mouth_limit(p) > pr.rf - MIN_WALL`, and this same phase's own new keyway-floor-corner
rule (D-10) refuses at `keyway_corner_radius(p) + MIN_WALL > pr.rf`. The new round/D-flat
bore-chamfer-vs-root rule this phase adds is the one exception: it refuses only at
`r_bore + p.bore_chamfer > pr.rf - ROOT_CONTACT`, where `ROOT_CONTACT = 1e-9` mm — a margin
40 million times smaller than `MIN_WALL`. This is a deliberate, well-measured choice
(L28/D-12, explicitly to avoid refusing round links that built before this phase), but its
practical effect is that a bore/chamfer combination can leave a wall as thin as a few
hundredths of a millimetre (or less) between the chamfered bore mouth and the tooth root,
build a perfectly "valid" solid, and `derive()` emits **no warning whatsoever** — unlike the
codebase's usual cap-and-warn pattern (`root_fillet`, `recess_radii`) for exactly this kind
of "requested dimension runs into a physical limit" case (L03).

Confirmed on this build (`bore_d`, `bore_chamfer` are ordinary floats — the schema's `step`
is UI metadata only, not a `multipleOf` constraint, so this is reachable from the plain
API/CLI, not just from probing test code):

```python
>>> from spur.params import GearParams
>>> from spur.model import build
>>> from spur.calc import derive
>>> p = GearParams(bore_d=27.905, bore_flat=0)   # default 19T m=1.75 gear
>>> derive(p).warnings
('No room for a face recess between the bore wall and the tooth rim; it was left out.',)
>>> build(p).isValid()
True
# gap between the chamfered bore mouth and the root circle here is 0.01 mm --
# 40x thinner than MIN_WALL, and nothing in warnings says so.
```

**Fix:** Keep the refusal boundary at `ROOT_CONTACT` (L05's "don't refuse a link that
builds today" reasoning is sound and well-measured), but add a warning, mirroring the
existing cap-and-warn pattern, whenever the mouth-to-root gap is positive but under
`MIN_WALL`:

```python
gap = pr.rf - (bore_radius(p) + p.bore_chamfer)
if p.bore_d > 0 and p.bore_hex == 0 and 0 <= gap < MIN_WALL:
    warnings.append(
        f"Bore chamfer leaves only {gap:.2f} mm of wall to the root circle, "
        f"under the {MIN_WALL:g} mm this design otherwise holds everywhere else.")
```
placed in `derive()` alongside the existing `root_fillet`/`recess` warnings, so a user
gets the same signal here that every other thin-wall situation in this tool already gives.

## Info

### IN-01: `keyway_width_effective`'s own zero-gate is looser than its sibling helpers'

**File:** `src/spur/calc.py:81-84`

**Issue:** `keyway_corner_radius(p)` (the function every call site actually gates on)
returns `0.0` unless *both* `p.keyway_width > 0` and `p.keyway_depth > 0` — correctly
mirroring `_cut_keyway`'s "a keyway exists only with both fields set" invariant.
`keyway_width_effective(p)` guards on `p.keyway_width > 0` alone. Every current call site
(`keyway_corner_radius` itself, `keyway_flat_wall`, `_cut_keyway`, and `derive()`'s
`keyway_corner_radius(p) > 0` gate) only ever reaches `keyway_width_effective` once both
fields are known to be set (via `check()`'s D-13 refusal upstream, or `model.py`'s own
gate), so this is unreachable in practice today. But the function's own docstring says
"0.0 with no keyway," and on a half-set, validation-bypassed `GearParams`
(`keyway_width=3, keyway_depth=0`) — the same kind of construction this phase's own tests
use elsewhere (`model_copy(update=...)`) — it returns `3.15`, not `0.0`, even though no
keyway will ever be cut for that object. A future caller that reaches for this helper
directly (outside the two guarded call sites) inherits a contract weaker than the one its
own docstring states.

**Fix:** Gate it the same way as `keyway_corner_radius`:
```python
def keyway_width_effective(p: GearParams) -> float:
    return (p.keyway_width + p.bore_clearance
            if p.keyway_width > 0 and p.keyway_depth > 0 else 0.0)
```

---

_Reviewed: 2026-09-27T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
