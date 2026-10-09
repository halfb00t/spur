---
phase: 19-the-trochoid-in-the-part
reviewed: 2026-10-09
depth: standard
files_reviewed: 30
findings:
  critical: 1
  warning: 1
  info: 4
  total: 6
status: issues_found
---

# Phase 19: Code Review Report

## Summary

I reviewed the diff against `df4749e`, with the changed hunks in `calc.py`, `model.py`, `params.py` and `app.js` read in full. I read the test and bench diffs, and checked the docs for claims the code does not back.

- **Gate:** `make verify` ran green: ruff, mypy, import contracts and `1210 passed in 198.94s`, EXIT 0.
- **Fuzz:** I built 234 random trochoid gears through `model._build_checked`, covering 6 to 116 teeth, shift -0.6 to 1.0, tip radius 0 to 3, backlash 0 to 1 and tip chamfers. All were one valid solid with no `BuildError`. The last of the four runs was still going when I stopped, so the true total is slightly higher.
- **Arithmetic in comments and docs:** the figures I re-computed all hold (for example 10.0x, 15.8x, 40.9x, 75.0x, 13.6x, 2.92x and 1.54x).
- **Cited test names:** all of the 42 test names the docs cite exist.
- **Defect found:** one defect in a printed number (`root_waist`) is the only thing that breaks a standing rule. It sits on the path L08 protects.

## Critical Issues

### CR-01: `root_waist` is not the narrowest tooth, and the thin-waist warning goes silent on gears that are thinner than the floor

**File:** `src/spur/calc.py:1175-1183` (`derive()` waist), `src/spur/calc.py:1553-1585` (`_waist`)

**Issue:** `_waist` finds the point where the half-angle `h` is smallest. `derive()` then prints `2 * r * h` there as `root_waist`, "Narrowest tooth in the root", and compares it to `ROOT_WAIST_FLOOR`.

The arc thickness `2 r h` has its minimum at a lower radius than the minimum of `h`. At the minimum of `h`, `d(rh)/dr = r'·h > 0`, so thickness is still falling as radius falls. On every crossing join (the undercut case this field exists for), the printed value is therefore larger than the true narrowest arc thickness. Tangent joins are exact, because the minimum of `h` is at the junction there.

I measured the true minimum of `2 r h` by dense sampling (4,000+ samples up to the junction radius) on three gears:

| Gear | Printed `root_waist` | True narrowest arc | Over-statement |
|---|---|---|---|
| 7 teeth, module 2, 25 degrees, shift 0.27, tip radius 0 | 3.269 mm | 3.149 mm | 3.8 % |
| 8 teeth, module 2, 25 degrees, shift 0.24, tip radius 1 | 3.536 mm | 3.428 mm | 3.1 % |
| 10 teeth, module 1, 20 degrees, backlash 0, tip radius 0.38 | 1.473 mm | 1.442 mm | 2.1 % |

The over-statement also changes the floor warning. I bisected the profile shift until the printed waist read 0.4005 mm, which prints as 0.401, so no "waist thin" warning fires.

- **8 teeth, module 1, 14.5 degrees:** shift about -0.5132, true narrowest 0.3948 mm.
- **6 teeth, module 1, 14.5 degrees:** shift about -0.3103, true narrowest 0.3909 mm.

Both are under the 0.4 mm floor. That is a number someone cuts to, printed 2 to 4 % high, with the warning meant to catch it suppressed. `test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere` pins 1.473, and the README and L38 repeat "narrowest" without qualification.

**Fix:** Take the waist as the minimum of the arc thickness, not of the angle. Keep the minimum-`h` search only for the `tooth severed` test (`waist[1] <= 0`), and add a second refinement for the thickness:
```python
def _arc_min(c, betas, points):
    f = lambda b: (lambda r, h: r * h)(*_trochoid_point(c, b))
    i = min(range(len(points)), key=lambda k: points[k][0] * points[k][1])
    lo, hi = betas[max(i - 1, 0)], betas[min(i + 1, len(betas) - 1)]
    # same 60-step golden section as _waist, on f
```
Then print `2 * min(r*h)` as `root_waist`, and re-pin 1.473 and the other waist figures. If you keep the current definition instead, rename the field and the UI label to say "thickness at the narrowest half-angle" and drop "narrowest tooth" from the README and L38.

## Warnings

### WR-01: Unguarded kernel calls in the trochoid outline get the wrong remedy

**File:** `src/spur/model.py:316-322` (`_trochoid_outline` calls `makeSpline`, `makeThreePointArc`, `assembleEdges`), `src/spur/model.py:769-774` (`_build_checked`)

**Issue:** `solid-model/implementation.md` says `_build_checked` blames the user's fillets for any kernel exception ("try smaller fillets or chamfers"). It says a new way for the hob outline to fail "should be a new guard", not another case for the relabel. The four guards cover only point geometry and the finished face area.

Every kernel call inside `_trochoid_outline` is still outside any guard: `makeSpline`, `makeThreePointArc` and `assembleEdges`. The same goes for `makeFromWires` in `_gear_blank`. Any exception from them reaches the user as "Geometry kernel failed (...); try smaller fillets or chamfers." Under the hob root, `root_fillet` is the hob tip radius, so that advice is wrong.

The ROOT_ARC_MIN dead band is precisely this failure class: `makeThreePointArc` raised `GC_MakeArcOfCircle` and was found only by measurement. I did not reproduce one in my 234 fuzz builds, so this is a robustness gap, not an observed failure.

**Fix:** Wrap the edge construction in `_trochoid_outline` and `_gear_blank`'s `makeFromWires`:
```python
try:
    ...edge construction...
except BuildError:
    raise
except Exception as exc:
    raise BuildError(f"The hob-root outline could not be built ({type(exc).__name__}): "
                     f"{_NOT_A_PARAMETER_PROBLEM}") from exc
```
Add a test that patches `cq.Edge.makeSpline` to raise.

## Info

### IN-01: `_build`'s "one answer" comment is only partly true

**File:** `src/spur/model.py:743-750`, `src/spur/model.py:612`

**Issue:** The comment says `root_mode` is asked once so "the part and the numbers cannot name different roots". `_chamfer_tips` calls `tip_chamfer_effective(p)` with no `rm`. That re-runs `tip_chamfer_limit`, which calls `root_mode` and re-solves the curve for any chamfered trochoid build. The new `rm` parameters on `tip_chamfer_effective` and `tip_chamfer_limit` are used only by `derive()`. `root_mode` is pure, so the two answers cannot diverge today.

**Fix:** Pass `rm` through `_chamfer_tips(solid, p, pr, rm)` and `tip_chamfer_effective(p, rm)`. Otherwise soften the comment.

### IN-02: Stale docstring and duplicated code in `bench/trochoid_part.py`

**File:** `bench/trochoid_part.py:109-121`, `bench/trochoid_part.py:172-195`, `tests/test_model.py` (`_root_edges`, `_oracle_reading`)

**Issue:** `trochoid_curve` says `RootMode.curve` "does not exist until 19-04" and re-solves with `trochoid_root(rm.cutter)`. It has existed since 19-04, so `rm.curve` could be read directly, and `tests/test_bench.py` repeats the re-solve. `root_edges`, `tooth0_root_edges` and `oracle_reading` are near-copies of `_root_edges` and `_oracle_reading` in `tests/test_model.py`. That is two definitions of the "selector that must count" and the oracle reading, which can drift.

**Fix:** Read `rm.curve` and delete the stale paragraph. Let one module import the other's helpers, or move them to a shared test helper.

### IN-03: Gate-cost comments are now stale

**File:** `Makefile:152-156`, `docs/architecture/decision_log.md` (L34, L38)

**Issue:** The Makefile comment still says "the whole gate is 63.555 s (L34)". I measured `make verify` at 198.94 s in this review, 3.0 times the quoted figure. L38 records that the human accepted the 192.94 s mean and left the 66 s bar "on paper", so this is a documented acceptance. The Makefile comment is now a claim the repo contradicts.

**Fix:** Update the Makefile comment to cite L38's reading, or open the follow-up debt item L38 says is separate.

### IN-04: Minor label and robustness nits

**File:** `src/spur/static/app.js:23`, `bench/trochoid_part.py:333`

**Issue:** The result row `['root_fillet', 'Root fillet used']` reads "Root fillet used" while a hob root is in force, where the value is the hob's tip radius, not a fillet. `_host_state` runs `git rev-parse` with `check=True`, so the bench crashes outside a git checkout instead of printing "unknown".

**Fix:** Make the label a function of the document, for example `(d) => d.root_form_d != null ? 'Hob tip radius used' : 'Root fillet used'`. Catch `CalledProcessError` and `FileNotFoundError` and print "unknown".

---

_Reviewed: 2026-10-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
