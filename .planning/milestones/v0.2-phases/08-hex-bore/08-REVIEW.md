---
phase: 08-hex-bore
reviewed: 2026-09-26T00:00:00Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - bench/build_time.py
  - bench/RESULTS.md
  - bench/sweeps/hex_bore.json
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/implementation.md
  - docs/architecture/solid-model/tactics.md
  - docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md
  - docs/tech_debt/INDEX.md
  - Makefile
  - README.md
  - src/spur/calc.py
  - src/spur/model.py
  - src/spur/params.py
  - src/spur/static/app.js
  - tests/regression/capture.py
  - tests/regression/test_pre_v0_2.py
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: issues_found
---

# Phase 08: Code Review Report

**Reviewed:** 2026-09-26
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found (Info only)

## Summary

Phase 8 adds a hexagonal bore (`bore_hex`) end to end: `GearParams.bore_hex`,
`calc.hex_across_flats/bore_rim_limit/bore_mouth_limit`, `check()`'s hex-specific
refusal rules, `model._cut_bore`'s hexagon cut, two new `DerivedDimensions` fields, the
web/CLI/API surfaces, a `bench.build_time` timing harness plus its committed sweep, and
docs/decision-log updates.

Traced every changed function against its callers and its tests:

- **Standing rules held.** `calc.py` imports no `cadquery` (`grep` confirms); `cadquery`
  types stay inside `model.py` (only `model.py` imports `cq`); `GearParams._feasible`
  is still the sole validation point; the new `bore_hex` default (`0.0`) is an absolute
  mm value that changes nothing for an existing link (L05); the hex rules cap-or-refuse
  per L03 (corner-vs-root and chamfered-corner-vs-root are direct conflicts → 422,
  never a guessed number); the `derive()`/CLI/API/UI all read the one `DerivedDimensions`
  document, no per-interface wording.
- **Math checked against the built kernel, not just derived on paper.** Verified by
  hand (and cross-checked against the project's own tests) that `bore_rim_limit`'s
  hex branch is the correct circumradius (`across-flats / sqrt(3)`), that
  `bore_mouth_limit`'s `2c/sqrt(3)` chamfer-to-corner reach is right, and that the two
  `check()` boundary values (24.15/24.2 mm, 23.35/23.4 mm) are exactly where the code
  places them — confirmed numerically against `calc.py` directly, not just by reading
  the docstrings' claims.
- **`recess_radii()`'s refactor to `bore_rim_limit`/`bore_mouth_limit` is behaviour-
  preserving for round/D-flat bores** — for `bore_hex == 0`, `bore_mouth_limit(p)`
  reduces to the old `bore_radius(p) + chamfer`, so the round-bore recess datum is
  unchanged; only the hex path is new behaviour.
- **Tests are not decorative.** Ran `tests/test_calc.py`, `tests/test_model.py`,
  `tests/test_api.py`, `tests/test_cli.py`, `tests/test_bench.py` and
  `tests/regression/` (216 tests) — all pass. `ruff check` and `mypy --strict` on the
  four touched source files are clean. The regression fixture's additive-field
  contract (a pre-v0.2 record's new fields must read `null`) is real and exercised.
- **Docs match the code.** Spot-checked `bore_mouth_limit(GearParams(teeth=200,
  module=1.75, bore_hex=200, recess_sides="both", bore_chamfer=3))` against
  `decision_log.md` L27's cited 119.02/172.41 mm figures — they match to the decimal
  place printed. `bench/sweeps/hex_bore.json`'s 16 rows match `bench/RESULTS.md`'s
  reported sweep exactly.
- **The one known gap is filed, not silently shipped.** The round bore's own
  chamfer-vs-root gap (pre-existing, not introduced by this phase) is correctly
  recorded in `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md`
  and indexed in `docs/tech_debt/INDEX.md` at `must` severity with a named trigger,
  rather than left as an undocumented loose end.

No Critical or Warning-level defect was found in the reviewed diff. One Info-level
robustness nit is recorded below.

## Info

### IN-01: `make bench.build`'s SWEEP path is unquoted

**File:** `Makefile:124`
**Issue:** `$(PY) -m bench.build_time $(SWEEP)` expands `$(SWEEP)` unquoted. A sweep
file path containing a space (e.g. `make bench.build SWEEP="my sweeps/foo.json"`) splits
into two positional arguments to `argparse`, which either errors confusingly or, with
`nargs="?"`, silently takes only the first token as the path and ignores/mis-parses the
rest.
**Fix:**
```make
bench.build: $(STAMP)
	$(PY) -m bench.build_time "$(SWEEP)"
```
Low impact in practice — the committed sweep files live under `bench/sweeps/` with no
spaces in their names — but the fix is one character-class away from free.

---

_Reviewed: 2026-09-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
