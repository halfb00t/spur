---
phase: 10-tooth-tip-chamfer
reviewed: 2026-09-28T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - bench/RESULTS.md
  - bench/sweeps/tip_chamfer.json
  - bench/tip_chamfer_spike.py
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/implementation.md
  - docs/architecture/solid-model/tactics.md
  - docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md
  - docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md
  - docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md
  - docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
  - docs/tech_debt/INDEX.md
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
  info: 2
  total: 3
status: issues_found
---

# Phase 10: Code Review Report

**Reviewed:** 2026-09-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Reviewed the phase-10 delta only (`git diff 277a98f..HEAD`) against the listed files: the
new `tip_chamfer` field, its three-limit cap (`calc.tip_chamfer_limit`/
`tip_chamfer_effective`), the kernel cut and selector (`model._chamfer_tips`/
`_tip_edges`), the `calc.spline_start` extraction from `model._outline`, the bench spike
and committed sweep, docs, and the accompanying tests. `make verify` (ruff, mypy
`--strict`, import-linter, pytest) passes clean — 453 tests, 0 failures — and I traced
the geometry logic, the cap arithmetic, and the cross-file consistency between
`calc.py`'s three limit terms and `model.py`'s cut/selector by hand rather than trusting
the green run.

The implementation is unusually well-measured for a v1 review target — the flank cap is
backed by a 20-step bisection on 6 configurations plus a 405-set grid, and three items of
honestly-filed tech debt (CLI exit-code doc drift, the root-fillet lead-in claim, the
build-timeout margin) are already disclosed exactly as the codebase's own process
requires, with content that matches the bench numbers I could verify independently. I did
not re-raise those as new findings since they are correctly filed, not silently dropped.

I found one genuine, reproducible warning-suppression gap introduced by this phase's new
`derive()` comparison (a sub-print-precision `tip_chamfer` request is silently rounded
away with no "reduced" warning, unlike every sibling capped field), and two minor
quality/maintainability items. No blockers.

## Warnings

### WR-01: A `tip_chamfer` request under 0.0005 mm is silently rounded to nothing, with no warning

**File:** `src/spur/calc.py:543-549`

**Issue:** `derive()`'s warning gate for the tip chamfer rounds *both* sides of the
comparison to 3 dp before deciding whether to warn:

```python
tch = tip_chamfer_effective(p)
if tch < round(p.tip_chamfer, 3):
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
```

This is deliberate for the case the surrounding comment describes (a *limit's* own float
residue, e.g. 0.1999999999999993, must not warn when the request is exactly 0.2). But it
has a side effect the comment doesn't cover: when the *request itself* is small enough
that `round(p.tip_chamfer, 3)` is `0.0` — i.e. `0 < p.tip_chamfer < 0.0005` — the
comparison becomes `0.0 < 0.0`, which is always false, so no warning fires at all, even
though the requested chamfer was not applied.

Verified directly against the pinned kernel:

```
>>> from spur.params import GearParams
>>> from spur.calc import derive
>>> from spur.model import _build_checked
>>> p0, p1 = GearParams(), GearParams(tip_chamfer=0.0004)
>>> derive(p1).tip_chamfer_effective, derive(p1).warnings
(0.0, ())
>>> s0, s1 = _build_checked(p0), _build_checked(p1)
>>> len(s0.Faces()) == len(s1.Faces()), abs(s0.Volume() - s1.Volume()) < 1e-9
(True, True)
```

The built part for `tip_chamfer=0.0004` is byte-for-byte the same as the unchamfered
default (no chamfer cut at all — `model._chamfer_tips`'s `if c <= 0: return solid` skips
it), `tip_chamfer_effective` prints `0.0` (not `null`, since the gate is `p.tip_chamfer >
0`), and `warnings` is empty. This is a direct instance of the project's own standing
rule "cap and warn... never silent" (CLAUDE.md, `docs/CODING_VALUES.md` "Failure
handling") being violated for a field this exact phase introduces: the sibling fields
`root_fillet` and `recess_fillet` compare the *raw* (unrounded) requested value instead
and do warn in the equivalent case (`GearParams(root_fillet=0.0004)` prints `"Root fillet
reduced to 0.00 mm to fit the tooth gap."` even though the message's stated reason is
technically wrong there too — it still tells the caller something changed). `tip_chamfer`
is the only capped field in this codebase that can silently discard a nonzero user
request with zero signal.

This is unreachable through the web UI (its step is 0.05 mm), but reachable from any
direct `/api/info`, `/api/model.stl` or `spur export --tip-chamfer` caller sending a
high-precision value — exactly the class of caller `calc.py`'s own `ROOT_CONTACT`
docstring already worries about for `bore_d`.

**Fix:** Compare against the raw request, like `root_fillet`/`recess_fillet` do, rather
than rounding both sides:

```python
tch = tip_chamfer_effective(p)
if tch < p.tip_chamfer and round(tip_chamfer_limit(p)[0], 3) < round(p.tip_chamfer, 3):
    warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p)[1]}.")
```
or, more simply, warn whenever `tch != round(p.tip_chamfer, 3)` is false only because of
a *limit's* residue — i.e. keep the 3-dp comparison for the limit-vs-request check the
comment describes, but always warn separately when `p.tip_chamfer > 0` and `tch == 0.0`
(a full round-to-nothing is never the "print residue" case the current comparison was
built to protect against).

## Info

### IN-01: Bench spike hardcodes the `tip_chamfer` field's `le=3` bound in two places

**File:** `bench/tip_chamfer_spike.py:201`, `bench/tip_chamfer_spike.py:286`

**Issue:** Both `boundary()`'s `hi = min(3.0, 0.45 * p.face_width)` and `grid_check()`'s
`cap = min(0.45 * p.face_width, pr.ra - pr.r, 3.0)` repeat the literal `3.0`, which is
`GearParams.model_fields["tip_chamfer"].metadata`'s `le=3` copied by hand. If the field's
upper bound is ever changed (as `docs/CODING_VALUES.md` notes new fields are meant to
flow through the schema automatically), this bench script's grid would silently stop
representing the field's real analytic ceiling and no test would catch the drift — the
bench script isn't part of `make verify`'s pytest run.

**Fix:** Read the bound from the field instead of repeating it, e.g.
`GearParams.model_fields["tip_chamfer"].metadata` (or a `le` extracted the same way
`_add_gear_args` in `cli.py` reads `field.annotation`), so a future field-bound change is
reflected here without a second hand-edit.

### IN-02: `DerivedDimensions.tip_chamfer_effective`'s null-gate reads the raw field, not the applied value

**File:** `src/spur/calc.py:618`

**Issue:** `tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None` — the same
underlying rounding-to-zero case as WR-01 means a request the model quietly cuts nothing
for still prints a non-`null` `0.0`, rather than `null` ("no tip chamfer") or a value that
comes with the "reduced" warning WR-01's fix would add. Once WR-01 is fixed the printed
`0.0` will at least always ship with an explanatory warning; consider whether `tch > 0`
is closer to the field's own documented contract ("null with no tip chamfer") than
`p.tip_chamfer > 0`, since `tch` (not the raw request) is what the built part actually
reflects.

**Fix:** Low priority, and coupled to how WR-01 is resolved — a warning fixes the "silent"
half of this; whether `0.0` vs `null` is the more honest value for the field is a smaller
follow-on decision.

---

_Reviewed: 2026-09-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
