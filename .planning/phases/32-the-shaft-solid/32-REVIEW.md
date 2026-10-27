---
phase: 32-the-shaft-solid
reviewed: 2026-10-27T00:00:00Z
depth: standard
files_reviewed: 22
files_reviewed_list:
  - Makefile
  - bench/__init__.py
  - bench/build_time.py
  - bench/export_cost.py
  - pyproject.toml
  - src/spur/din5480.py
  - src/spur/model.py
  - src/spur/parts.py
  - src/spur/records.py
  - src/spur/shaft_calc.py
  - src/spur/shaft_model.py
  - src/spur/shaft_params.py
  - tests/shaft_oracle.py
  - tests/test_bench.py
  - tests/test_din5480.py
  - tests/test_hooks.py
  - tests/test_pool.py
  - tests/test_records.py
  - tests/test_seam.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_model.py
  - tests/test_shaft_params.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 32: Code Review Report

**Reviewed:** 2026-10-27
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

I reviewed the phase-32 diff (`7c1bc2c..HEAD`) of the 22 files, plus the unchanged code they call (`model._write_export`, `pool`, the import-linter contracts).

The shaft solid holds up under attack. I made these checks beyond reading the code:

- **Random builds.** I built about 400 random legal shafts and compared each volume with `tests/shaft_oracle.py`. The sample covered module 0.5 to 10 at 1 to 5 decimals, teeth 6 to 82, shift -0.05 to 0.45, reference_d at 2 to 6 decimals, random chamfers, splined and shank lengths, and shank_d at, around, and away from the tip. None raised `BuildError`, none hung, and none left the 1e-4 volume bar.
- **Near-coincident base and root circles.** I picked four legal (m, z, d_B) triples with `0 < r_b - r_f < 2e-6`, from 3.1e-7 up. All four build. The radial line there is a near-degenerate edge, and the kernel accepts it.
- **Tooth geometry over the whole shift range.** For every z from 6 to 82 and every shift from -0.05 to +0.45, the tip half-angle stays positive (minimum 0.0124 rad at z = 82, x = +0.45) and the root gap stays positive (minimum 0.0114 rad, same corner). The outline cannot self-intersect inside `ShaftParams`' range.
- **The cone-start guard.** The guard never fires on a size `derive_shaft` prints, for any parameters and not only the test GRID. `tip_d` and `root_d` are rounded to 0.001 mm, so `ra` and `rf` sit on the 0.0005 mm lattice, and `c` is on the 0.001 lattice. The offset is therefore 0 or a multiple of 0.0005, up to float noise near 1e-15.
- **Import contracts.** The `ignore_imports = ["spur.model -> spur.shaft_model"]` edge cannot hide a serving-process import. The separate contract on `spur.app` forbids cadquery and OCP transitively.

I found no security issue and no L03, L05 or L08 violation. The two warnings are a missing guard and a debuggability gap in the bench tooling. Both are verified against the source.

## Warnings

### WR-01: `_guard_volume` has no lower bound on what the cone removes, so a chamfer that was never cut passes every build-time guard

**File:** `src/spur/shaft_model.py:136-141`
**Issue:** The bracket is `[upper - c*(area - pi*rf^2), upper]`. `upper` is the uncut prism plus shank, so a solid with no chamfer at all sits exactly on the upper edge and is accepted. The bounding-box check cannot see a missing chamfer either: the cone does not change z-extent or the widest radius.

I confirmed this by building `ShaftParams(end_chamfer=0)` and calling `_guard_volume(solid, area, rf, 1.0, ...)` on it. It returned without raising, so an uncut solid is accepted as a 1.0 mm chamfered shaft.

If the intersect ever returned the body unchanged (a kernel no-op, or a future edit to `_cone`), `derive_shaft` would still print `end_chamfer_effective = c`. That is a number someone would cut metal to (L08) that is not on the part. The module docstring promises that the guards "turn each silent failure into a BuildError". For the one feature the bracket was built to police, the guard only bounds the failure from one side. Today the test-suite readbacks catch the regression, but nothing at runtime does.

**Fix:** For `c > 0`, also require the removal to be positive and about the expected size. The simplest sound option is a lower bound on the cut from numbers the kernel did not produce:
```python
cut = upper - volume  # what the cone actually removed
# the cone removes at least the tip corner of one tooth's flank band; any positive
# floor derived from the oracle's closed form works, e.g. compare against a coarse
# Simpson over the same profile (as tests/shaft_oracle.py does) and allow VOLUME_BRACKET_SLACK
if c > 0 and cut <= 0:
    raise BuildError(...)
```
If a closed form is too heavy for the runtime path, `cut <= 0` alone covers the silent no-op. Add a test that calls `_guard_volume` with an uncut solid and `c > 0` and expects `BuildError`.

### WR-02: `--fresh` throws away a failing child's stderr, and an empty stdout becomes a bare `IndexError`

**File:** `bench/build_time.py:195-203`
**Issue:** `_time_fresh` runs the child with `capture_output=True, text=True, check=True` and reads `.stdout.strip().splitlines()[-1]`.
- When the child dies (a `BuildError`, an OOM kill, a bad row index), `CalledProcessError` carries `.stderr`, but the traceback prints only "returned non-zero exit status N". The child's traceback is lost.
- If the child exits 0 with empty stdout, `splitlines()[-1]` raises `IndexError: list index out of range`. The row and cause are not named.

This path is run on the multi-minute sweep that sets the L37 bounds, so a failure at row 8 of 10 costs a full re-run just to see why. The sibling `bench/export_cost.py:261-270` already handles this: it passes `check=False`, writes `child.stderr` to stderr, and raises `SystemExit` naming the run.

**Fix:**
```python
child = subprocess.run(
    [sys.executable, "-m", "bench.build_time", str(sweep), "--child-row", str(i)],
    capture_output=True, text=True, check=False)
if child.returncode != 0 or not child.stdout.strip():
    sys.stderr.write(child.stderr)
    raise SystemExit(f"error: --child-row {i} ({label}) exited {child.returncode} "
                     "with no result line")
payload: _ChildPayload = json.loads(child.stdout.strip().splitlines()[-1])
```

## Info

### IN-01: Comments left describing the pre-wiring state

**File:** `src/spur/shaft_model.py:4-5`, `src/spur/model.py:824`, `bench/__init__.py:48-53`
**Issue:** Three comments were not updated when the phase landed.
- `shaft_model.py:4-5` says "it is reached only through model (32-04 wires that)". `model.py` now imports it statically.
- `model.py:824` says the cache hands out the same object "for one GearParams". The cache now holds both part types, and `_build_cached` is keyed by `Part`.
- The `maxrss_bytes` docstring in `bench/__init__.py` (which this phase moved there) still says "no existing bench script reads `ru_maxrss` before this one". `build_time.py` reads it too now, and the function no longer lives in the one script the sentence names.

The project treats its comments as an asset, so stale ones count.
**Fix:** Change line 4 to "it is reached only through model", say "for one part's params" at `model.py:824`, and drop the "before this one" clause.

### IN-02: `load_sweep` calls an explicit `"part": "gear"` an "unknown part"

**File:** `bench/build_time.py:97-109`
**Issue:** The dispatch is `kind == "gear" and "part" not in obj`, so an explicit `{"part": "gear"}` falls through to the `else`. The error then reads `names an unknown part 'gear'`, which contradicts itself. The docstring does say "any other value is refused", so the refusal is intended. The message is the defect.
**Fix:** Either accept the explicit value (`if kind == "gear": ...`) or word the refusal as "`part` must be absent (a gear) or \"shaft\", not 'gear'".

---

_Reviewed: 2026-10-27_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
