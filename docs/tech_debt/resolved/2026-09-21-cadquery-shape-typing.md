# CadQuery's `Shape` typing forces five `type: ignore`s

Severity: nice
Status: resolved
Date: 2026-09-21
Resolved in: 4f7e8fe
Source: setting up the gate — mypy --strict over src/spur/model.py
Related files:
- src/spur/model.py:213, 237, 239, 411, 420 (the five sites at 085e5a6, before this fix)

## Context

CadQuery ships `py.typed`, and types every boolean result as the wide `Shape`. `Shape`
declares neither `fillet` nor `chamfer` — those live on `Mixin3D`, which `Solid` and
`Compound` carry but `Shape` itself does not — and `Workplane.val()` is typed as a
four-way union. Verified against the installed package, not assumed:
`hasattr(cq.Shape, "fillet")` is `False`, `hasattr(cq.Solid, "fillet")` is `True`.

The pipeline is correct at runtime: a boolean on a solid yields a `Solid` or a
`Compound`, both of which have the methods, and `_build()` re-checks that exactly one
valid solid came out before anything leaves. But the annotations say `Shape`, so mypy
reports five errors, suppressed with narrow coded ignores that each state the reason.

Phase 10's tip chamfer (10-02) added the fifth ignore, on `_chamfer_tips`'s
`solid.chamfer(...)` call — the same `Mixin3D` reason as the bore chamfer's.

## Why it matters

Low. The ignores are specific (`attr-defined`, `arg-type`, `return-value`), each carries
its justification, and `RUF100` will fail the build if one becomes unnecessary. The cost
is that five lines in the project's most delicate file are outside the type checker.

## Next step

Narrow the annotations through `_gear_blank` → `_cut_face_recesses` → `_cut_bore` to the
type the values actually have, casting once at the `.val()` boundary rather than ignoring
at each call site. Small, but it is a change to the geometry pipeline, so it wants its
own tested change rather than riding along with something else.

Revisit when: CadQuery narrows its own return types, or that pipeline is being touched
anyway.

## Resolution (2026-10-04)

Phase 16, plan 16-01. Sources are 16-CONTEXT.md's domain facts and decisions D-01 to D-05,
measured on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1 on 2026-10-04:

- Mechanism: two `isinstance` helpers in `src/spur/model.py`, each raising `BuildError`.
  `_body(shape: cq.Shape) -> cq.Solid | cq.Compound` stands at the three `fillet` /
  `chamfer` sites and `_shape_of(wp: cq.Workplane) -> cq.Shape` at the two `.val()` sites.
  Both raise "Geometry kernel returned a {} where a solid body was expected: a modelling
  defect in the build pipeline, not a parameter problem." with the class name filled in,
  so the message names the invariant and never a field (D-03).
- Why this file's own next step could not hold: `Shape.cut -> Shape` returns the wide type
  whatever goes in, so casting once at `.val()` reaches only `_ring` and the bore's
  `hole.val()`, two of five. The three `attr-defined` sites need `Mixin3D` after any `cut`
  (measured: `_gear_blank` returns a Solid, every boolean after it a Compound, and a step
  whose feature is off passes its input through).
- Why `isinstance` and not a cast: a cast claims the narrowing and nothing checks it at
  runtime; `isinstance` checks it on every call and a test sees it fail (D-01).
- `_gear_blank` stays `-> cq.Shape`: `-> cq.Solid` makes mypy infer `solid: Solid` in
  `_build`, and every later step's `cq.Shape` return becomes an `[assignment]` error, five
  of them (16-RESEARCH Pitfall 1).
- `cadquery.*` leaves `[[tool.mypy.overrides]]`, which now names `OCP.*` alone: cadquery
  ships `py.typed`, OCP ships no type information. mypy's output over
  `src tests docker bench scripts` with the cache cleared is byte-identical before and
  after (`cmp`; both read "Success: no issues found in 37 source files").
- The pin: `make no-fake-done` greps `src/spur/*.py` for the suppression phrase. It is
  scoped to `src/spur/` because `tests/test_calc.py` and `tests/test_cli.py` each carry
  one on purpose.
- Correction to "Why it matters" above, kept as history: `RUF100` governs `noqa`, not
  mypy suppressions. mypy strict's `warn_unused_ignores` is what refused a stale one
  (16-RESEARCH Finding 7), and nothing refused a new one until the pin.
- Tests: 927 -> 929 collected; two refusal tests in `tests/test_model.py` assert the full
  message with `==`.
- No geometry change: the five-site gear, `build(GearParams(tip_chamfer=0.5))`, reads
  `('Solid', True, 4446.54642, 210, 604)` for (type, isValid, volume at 6 dp, faces,
  edges) before and after, and `tests/regression/pre_v0_2.json` is byte-identical to
  085e5a6.
