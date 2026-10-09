---
phase: 19-the-trochoid-in-the-part
fixed_at: 2026-10-09T00:00:00Z
review_path: .planning/phases/19-the-trochoid-in-the-part/19-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 19: Code Review Fix Report

**Fixed at:** 2026-10-09
**Source review:** .planning/phases/19-the-trochoid-in-the-part/19-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2
- Fixed: 2
- Skipped: 0 (plus 4 info findings out of scope, listed below)

**Gate:** `make verify` on the final tree (commit `b51931c`) ran green: ruff, mypy `--strict`, import contracts, unfinished-work scan and pytest, ending `1220 passed in 196.18s (0:03:16)`, coverage 97.92 % (bar 96.0 %), EXIT 0. `make test PYTEST_ARGS="tests/regression -q -n0 --no-cov"` gave `86 passed in 15.36s`, and `tests/regression/pre_v0_2.json` has no diff against `df4749e`. Verification ran in the main checkout: `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree was created. Both commits passed the `make verify.fast` pre-commit hook.

## Fixed Issues

### CR-01: `root_waist` is not the narrowest tooth, and the thin-waist warning goes silent on gears that are thinner than the floor

**Files modified:** `src/spur/calc.py`, `tests/test_trochoid.py`, `tests/test_cli.py`, `README.md`, `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `docs/architecture/gear-maths/implementation.md`, `docs/architecture/gear-maths/tests.md`
**Commit:** `e733cc2`
**Status:** fixed: requires human verification (a logic fix; the new tests compare it with an independent dense sample)
**Applied fix:** Redefined `_waist` to minimise the arc thickness `R h` (sample argmin, then the same fixed 60-step golden section on `R h` between the neighbours) instead of `h`. I redefined the field rather than adding a second one, because no consumer needs the minimum-angle point. The severed-tooth test `waist[1] <= 0` is unchanged, since `R > 0` makes `R h <= 0` exactly when `h <= 0`. The consumers are `derive()`, `bench/trochoid_part.py` and the tests. The bench code stays as written and now reads the true narrowest arc.

- **Print choice:** `derive()` still prints `2 * R * h`, the arc on its own radius. The docstring says why: every thickness this tool prints is an arc (`tip_thickness`, `root_thickness`). The chord `2 R sin(h)` reads about 0.5 % lower. The orchestrator's chord figures (1.435, 3.107) therefore differ from the arc figures below.
- **Measured** (40,000-sample dense minimum of `2 R h` to the junction, run before and after on the same code):

  | Gear | Printed before | Printed after | Dense minimum |
  |---|---|---|---|
  | 10 teeth, module 1, 20 degrees, backlash 0, tip radius 0.38 | 1.473 | 1.442 | 1.442 |
  | 7 teeth, module 2, 25 degrees, shift 0.27, tip radius 0 | 3.269 | 3.149 | 3.149 |
  | 8 teeth, module 2, 25 degrees, shift 0.24, tip radius 1 | 3.536 | 3.428 | 3.428 |
  | 8 teeth, module 1, 14.5 degrees, shift -0.5132 | 0.401 | 0.395 | 0.395 |
  | 6 teeth, module 1, 14.5 degrees, shift -0.3103 | 0.401 | 0.391 | 0.391 |
  | default gear (tangent join) | 3.303 | 3.303 | 3.303 |

- **Re-pinned by measurement:**
  - `test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere`: 1.473 becomes 1.442.
  - `test_every_root_sentence_is_ascii_and_in_a_fixed_order`: 0.262 becomes 0.257.
  - The two `tests/test_cli.py` rows: 1.62 becomes 1.605, and 1.586 becomes 1.56.
  - `test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees` now pins the waist as `R h` in mm: -0.089372, -0.012726, +0.004709. Its dense-scan gap is 1.5e-9 mm at worst, against a 1e-8 bar (6.7x). The oracle gouges at the waist move to -0.141352 and -0.020146.
  - `tests/composition.py` and `test_calc.py` pin no waist figure and did not change.
- **New tests:**
  - `test_the_printed_waist_is_the_narrowest_arc_of_the_root_on_a_crossing_join`: three crossing gears, with the printed waist within 0.001 mm of a 20,001-sample minimum.
  - `test_the_thin_waist_warning_fires_where_the_smallest_half_angle_read_over_the_floor`: the two gears above at shift -0.5132 and -0.3103. The warning fires at 0.395 and 0.391 where the old reading, 0.401, was silent.
  - Both fail on the old `calc.py` (5 of 5 parametrised cases) and pass now.
- **Wording:**
  - The `root_waist` field description and the `RootCurve.waist` and `_waist` docstrings now describe the minimum arc.
  - README "Geometry notes", `gear-maths/implementation.md` and `gear-maths/tests.md` say the same.
  - L38 says it too, with the 303 of 1,061 and 775 of 10,326 counts. It keeps all 11 required tokens and removes no L01-L37 line.
  - `bench/RESULTS.md` has a new dated subsection, "Waist at the smallest arc thickness (19-REVIEW CR-01)", appended under `## Trochoid in the part (Phase 19)`. The 19-02 walk table is untouched.
- **Floor and walk counts:** `ROOT_WAIST_FLOOR` stays 0.4 mm. The walk grid warns on 303 of 1,061 gears (294 before) and the product on 775 of 10,326 (771 before). The thinnest walk waist is 3.2317e-3 mm (3.2325e-3 before).
- **Not re-run:** the walk's kernel and oracle columns. No curve moved, only which point of it is called the waist.

### WR-01: Unguarded kernel calls in the trochoid outline get the wrong remedy

**Files modified:** `src/spur/model.py`, `tests/test_model.py`, `tests/test_cli.py`, `docs/architecture/solid-model/implementation.md`, `docs/architecture/solid-model/errors_and_logging.md`
**Commit:** `b51931c`
**Applied fix:**
- Added `_hob_root_kernel_failure(exc)`. It builds a `BuildError("The hob-root outline could not be built (<ExcType>): " + _NOT_A_PARAMETER_PROBLEM)`, the same remedy sentence as the four guards.
- `_trochoid_outline` wraps the edge construction and `assembleEdges`, with `except BuildError: raise` first so the annulus guard passes through unchanged.
- `_gear_blank` wraps `makeFromWires` and re-raises unchanged when there is no curve, so the radial outline's behaviour is untouched. `_guard_area` stays outside the `try`.
- **New tests:**
  - A parametrised model test patches `cq.Edge.makeSpline`, `cq.Edge.makeThreePointArc`, `cq.Wire.assembleEdges` and `cq.Face.makeFromWires` to raise. It asserts the hob-root sentence, the `RuntimeError` cause and the absence of "try smaller". It also asserts that the radial gear keeps "try smaller fillets or chamfers".
  - A test in `tests/test_cli.py` confirms the API answers 422 `build_error` with the hob-root sentence.
  - All 5 cases fail without the `model.py` change and pass with it.
- The two `solid-model` docs each gained the one sentence asked for.

## Skipped Issues

### IN-01: `_build`'s "one answer" comment is only partly true

**File:** `src/spur/model.py:743-750`, `src/spur/model.py:612`
**Reason:** out of fix scope (info)
**Original issue:** `_chamfer_tips` calls `tip_chamfer_effective(p)` without `rm`, so `root_mode` is re-run for a chamfered trochoid build and the comment overstates the single answer.

### IN-02: Stale docstring and duplicated code in `bench/trochoid_part.py`

**File:** `bench/trochoid_part.py:109-121`, `bench/trochoid_part.py:172-195`, `tests/test_model.py`
**Reason:** out of fix scope (info)
**Original issue:** The docstring says `RootMode.curve` does not exist until 19-04, and the bench helpers duplicate `_root_edges` and `_oracle_reading` from `tests/test_model.py`.

### IN-03: Gate-cost comments are now stale

**File:** `Makefile:152-156`, `docs/architecture/decision_log.md` (L34, L38)
**Reason:** out of fix scope (info)
**Original issue:** The Makefile comment still quotes the 63.555 s gate, while `make verify` now takes about 3x that (accepted in L38).

### IN-04: Minor label and robustness nits

**File:** `src/spur/static/app.js:23`, `bench/trochoid_part.py:333`
**Reason:** out of fix scope (info)
**Original issue:** The "Root fillet used" label reads wrongly under a hob root, and `_host_state` crashes outside a git checkout.

## Debt and ideas filed

None. No `docs/tech_debt/` or `docs/ideas/` item was created.

---

_Fixed: 2026-10-09_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
