---
phase: 09-keyway-bore
reviewed: 2026-09-28T00:00:00Z
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
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-09-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

This is a re-review of the same `b522044..HEAD` keyway-bore diff, with a prior REVIEW.md
(WR-01, IN-01) and one external Codex-lane claim to re-verify against the current source,
per the orchestrator's instructions. I re-read `calc.py`, `model.py`, `params.py` and the
diffed tests line by line again (not from the prior report's word), re-derived the keyway
geometry formulas by hand (`keyway_corner_radius`, `keyway_flat_wall`,
`bore_mouth_limit`'s new `max(...)` term) against the numbers the decision log and tests
cite, and traced every `check()` branch that can call `math.acos`/`math.hypot` with a
keyway argument to confirm the domain stays in `[-1, 1]`. All of that holds; no new crash,
domain error or wrong-number defect found in this pass beyond what the prior review
already surfaced.

**WR-01** (round/D-flat chamfer can build microns from the root with no warning) is
re-confirmed unchanged: I re-derived its example (`bore_d=27.905, bore_flat=0` on the
default gear leaves a 0.01 mm gap, `ROOT_CONTACT` is 1e-9 mm below it) directly against the
current `calc.py` and it still holds bit-for-bit. Kept as written.

**IN-01** (`keyway_width_effective`'s zero-gate checks `keyway_width` alone) is
re-confirmed unchanged: every current call site still gates on `keyway_corner_radius(p) >
0` or `check()`'s own D-13 validator, so it stays latent, not live. Kept as written.

**New: WR-02** (external: codex). The external lane's claim was reproduced by hand, not
taken on its word: `params.py`'s `step` is confirmed to be JSON-schema metadata only (no
`multiple_of`/step validator anywhere in `_f()` or `GearParams`), so an API or CLI caller
can supply `bore_d`/`bore_chamfer` at arbitrary float precision, not just the UI's 0.05 mm
grid. I then tried to reproduce the specific data point the resolved debt file and
`calc.py:27-31`'s comment name — "one configuration (19 teeth, module 1.75, chamfer 2,
round) failed to build at a gap of exactly 1e-9 mm" — by solving the gap formula
algebraically for `bore_d` at that exact tooth/module/chamfer combination and scanning
neighbouring representable `float64`s (bore_d, then bore_chamfer, then bore_clearance) for
one that reproduces `gap == ROOT_CONTACT` bit-for-bit. None does: the representable gaps
jump from `1.0000000827…e-09` (`check()` accepts) straight to `9.999983…e-10` (`check()`
refuses), skipping the literal value. So the comment's specific "exactly 1e-9 mm" framing
is not bit-reproducible through ordinary decimal float inputs at that configuration — the
narrowest part of the external claim does not hold as stated.

What does hold, and is the substance of the external claim: `check()`'s only guarantee is
`gap > ROOT_CONTACT` (1e-9 mm); the project's own bisection record says the kernel is only
*proven* to succeed from `gap >= 1.9e-8 mm` up. Between those two numbers sits an
~1.9e-8 mm-wide band of `check()`-accepted gaps that the project's own measurement found
unpredictable (the named 19-tooth/module-1.75/chamfer-2 case failed somewhere in exactly
that band). That band is ~5,000 representable doubles wide at this magnitude — nothing
like the single-ULP needle the "exactly 1e-9 mm" framing suggests — and reaching it needs
only an ordinary `bore_d` value carrying 8-9 significant decimal digits, which the API
accepts today with no step enforcement. This is the same shape of gap the resolved debt
file itself already disclosed and accepted (L28/D-12: "unreachable by any value the 0.05
mm field step can set" — true only for the UI's own stepped widgets, not for a raw query
string). See WR-02 below; it does not propose moving the `ROOT_CONTACT` boundary D-12
locked, only that the "cannot be produced by any value a user or the API can set" claim
overreaches and that the disclosed residual has no regression test pinning it (unlike the
analogous `gap == 0.0` case, which `test_the_kernel_fails_where_a_round_bore_chamfer_
touches_the_root` does pin).

`make verify` was not re-run this pass (no source was changed); the prior review's own
"396 tests, ruff, mypy --strict, import-linter, unfinished-work scan, clean" stands
unchanged since no file in scope has moved since that run.

## Warnings

### WR-01: A round/D-flat bore's chamfer can land microns from the root circle with no warning at all

**File:** `src/spur/calc.py:18-31` (the `ROOT_CONTACT` constant) and `src/spur/calc.py:289-295`
(the `check()` rule that uses it)

**Issue:** `MIN_WALL` is documented, in its own comment, as "the thinnest wall allowed
**anywhere** in the body." Every other place a bore-derived feature can approach the root
circle enforces exactly that: the hex bore's corner-vs-root rule refuses at
`bore_mouth_limit(p) > pr.rf - MIN_WALL`, and this same phase's own new keyway-floor-corner
rule (D-10) refuses at `keyway_corner_radius(p) + MIN_WALL > pr.rf`. The round/D-flat
bore-chamfer-vs-root rule this phase adds is the one exception: it refuses only at
`r_bore + p.bore_chamfer > pr.rf - ROOT_CONTACT`, where `ROOT_CONTACT = 1e-9` mm — a margin
roughly 400 million times smaller than `MIN_WALL`. This is a deliberate, well-measured
choice (L28/D-12, explicitly so as not to refuse round links that built before this phase)
and this finding does **not** propose moving that refusal boundary — D-12 is locked, and
its reasoning (refusing at `rf - MIN_WALL` would refuse links that build today) is sound.
The gap is narrower: a bore/chamfer combination can leave a wall a few hundredths of a
millimetre thick between the chamfered bore mouth and the tooth root, build a "valid"
solid, and `derive()` emits **no warning at all** — unlike this codebase's usual cap-and-warn
pattern (`root_fillet`, `recess_radii`) for exactly this kind of "requested dimension runs
into a physical limit" case (L03).

Confirmed directly against the current source (`bore_d`/`bore_chamfer` are ordinary
floats — the schema's `step` is UI metadata only, not a `multipleOf` constraint):

```
>>> from spur.params import GearParams
>>> from spur.calc import derive, profile, bore_radius
>>> p = GearParams(bore_d=27.905, bore_flat=0)   # default 19T m=1.75 gear
>>> derive(p).warnings
('No room for a face recess between the bore wall and the tooth rim; it was left out.',)
>>> profile(p).rf - (bore_radius(p) + p.bore_chamfer)
0.010000000000005116
```
0.01 mm of wall — 40x thinner than `MIN_WALL` — and nothing in `warnings` says so.

**Fix:** Keep the refusal boundary at `ROOT_CONTACT`; add an additive warning in `derive()`,
mirroring the existing cap-and-warn pattern, whenever the mouth-to-root gap is positive but
under `MIN_WALL`:

```python
gap = pr.rf - (bore_radius(p) + p.bore_chamfer)
if p.bore_d > 0 and p.bore_hex == 0 and 0 <= gap < MIN_WALL:
    warnings.append(
        f"Bore chamfer leaves only {gap:.2f} mm of wall to the root circle, "
        f"under the {MIN_WALL:g} mm this design otherwise holds everywhere else.")
```
placed in `derive()` alongside the existing `root_fillet`/`recess` warnings.

### WR-02: The round/D-flat chamfer-reach rule's "unreachable" rationale overstates what it proves (external: codex)

**File:** `src/spur/calc.py:15-31` (the `ROOT_CONTACT` comment), `src/spur/calc.py:289-295`
(the rule itself), `docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md`

**Issue:** The `ROOT_CONTACT` comment states the sub-2e-8 mm residual band the project's own
20-step, 12-configuration bisection found "cannot be produced by any value a user or the API
can set." That is true only for the UI's stepped form widgets (0.05/0.01 mm steps): `step`
in `GearParams`' `_f()` (`src/spur/params.py:17-23`) is JSON-schema metadata handed to the
form, not a `multiple_of` or any other pydantic constraint, so `bore_d`/`bore_chamfer` (and
every other length field) accepts any float the API/CLI callers sends, at full double
precision. Reproduced live: I algebraically solved for the `bore_d` that puts the named
19-tooth/module-1.75/chamfer-2/round configuration's gap at `ROOT_CONTACT` and scanned the
neighbouring representable doubles in `bore_d`, `bore_chamfer` and `bore_clearance`; none
reproduces `gap == ROOT_CONTACT` bit-for-bit at that specific point (the two neighbouring
representable gaps are `1.0000000827…e-09`, accepted, and `9.999983…e-10`, refused — the
exact literal value is skipped), so the comment's narrowest reading ("this exact value")
is not reproducible through ordinary decimal float inputs at that configuration. But the
substance of the concern stands: `check()` accepts any `gap > ROOT_CONTACT` (1e-9 mm), while
the project's own bisection only proved the kernel builds reliably from `gap >= 1.9e-8 mm`
up — an ~1.9e-8 mm-wide, ~5,000-representable-double-wide band of `check()`-accepted gaps
where kernel success was measured as unpredictable, not proven either way, and where one of
the twelve bisected configurations demonstrably failed. Landing inside that band from the
API needs only an ordinary `bore_d` carrying 8-9 significant decimal figures — nothing like
adversarial bit-manipulation, and well within what a caller computing a bore to a measured
tolerance (rather than typing the UI's 0.05 mm steps) could plausibly send. The consequence
is a wasted build-worker slot and an opaque "Geometry kernel failed" `BuildError` instead of
a `422` naming the field — the exact failure mode D-12 was written to close, left open for
this one narrow, already-disclosed band.

This finding does **not** propose moving `ROOT_CONTACT` or the refusal boundary — that is
D-12's locked, well-measured trade-off, and re-litigating it would need its own superseding
`Lxx` with fresh measurement, not a review comment. Two additive changes would close the
gap without touching the boundary:

**Fix:**
1. Soften the comment's absolute claim (`src/spur/calc.py:27-31`) to state what is actually
   proven — unreachable via the UI's stepped fields, not via the API/CLI generally.
2. Add the missing regression test for the disclosed residual: `test_model.py` already pins
   the analogous `gap == 0.0` failure
   (`test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root`, using
   `model_copy(update=...)` to bypass validation); the `gap == ROOT_CONTACT` case the debt
   file names has no equivalent, so a future `cadquery`/`cadquery-ocp` bump that changes
   behaviour in this band would go unnoticed. A parametrized case at the debt file's own
   19-tooth/module-1.75/chamfer-2 configuration, asserting the kernel's current behaviour at
   that boundary, would close this the same way `L26`'s selector guards were pinned.

## Info

### IN-01: `keyway_width_effective`'s own zero-gate is looser than its sibling helpers'

**File:** `src/spur/calc.py:81-84`

**Issue:** `keyway_corner_radius(p)` (the function every call site actually gates on)
returns `0.0` unless *both* `p.keyway_width > 0` and `p.keyway_depth > 0` — correctly
mirroring `_cut_keyway`'s "a keyway exists only with both fields set" invariant.
`keyway_width_effective(p)` guards on `p.keyway_width > 0` alone. Every current call site
(`keyway_corner_radius` itself, `keyway_flat_wall`, `model._cut_keyway`, and `derive()`'s
`keyway_corner_radius(p) > 0` gate) only ever reaches `keyway_width_effective` once both
fields are known to be set (via `check()`'s D-13 refusal upstream, or `model.py`'s own
gate), so this is unreachable in practice today — re-confirmed this pass by tracing every
call site again. But the function's own docstring says "0.0 with no keyway," and on a
half-set, validation-bypassed `GearParams` (`keyway_width=3, keyway_depth=0`) — the same
kind of construction this phase's own tests use elsewhere (`model_copy(update=...)`) — it
returns `3.15`, not `0.0`, even though no keyway will ever be cut for that object. A future
caller that reaches for this helper directly (outside the two guarded call sites) inherits
a contract weaker than the one its own docstring states.

**Fix:** Gate it the same way as `keyway_corner_radius`:
```python
def keyway_width_effective(p: GearParams) -> float:
    return (p.keyway_width + p.bore_clearance
            if p.keyway_width > 0 and p.keyway_depth > 0 else 0.0)
```

---

_Reviewed: 2026-09-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
