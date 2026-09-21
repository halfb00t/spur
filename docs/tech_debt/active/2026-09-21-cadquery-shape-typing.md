# CadQuery's `Shape` typing forces four `type: ignore`s

Severity: nice
Status: active
Date: 2026-09-21
Source: setting up the gate — mypy --strict over src/spur/model.py
Related files:
- src/spur/model.py:169, 183, 185, 192

## Context

CadQuery ships `py.typed`, and types every boolean result as the wide `Shape`. `Shape`
declares neither `fillet` nor `chamfer` — those live on `Mixin3D`, which `Solid` and
`Compound` carry but `Shape` itself does not — and `Workplane.val()` is typed as a
four-way union. Verified against the installed package, not assumed:
`hasattr(cq.Shape, "fillet")` is `False`, `hasattr(cq.Solid, "fillet")` is `True`.

The pipeline is correct at runtime: a boolean on a solid yields a `Solid` or a
`Compound`, both of which have the methods, and `_build()` re-checks that exactly one
valid solid came out before anything leaves. But the annotations say `Shape`, so mypy
reports four errors, suppressed with narrow coded ignores that each state the reason.

## Why it matters

Low. The ignores are specific (`attr-defined`, `arg-type`, `return-value`), each carries
its justification, and `RUF100` will fail the build if one becomes unnecessary. The cost
is that four lines in the project's most delicate file are outside the type checker.

## Next step

Narrow the annotations through `_gear_blank` → `_cut_face_recesses` → `_cut_bore` to the
type the values actually have, casting once at the `.val()` boundary rather than ignoring
at four call sites. Small, but it is a change to the geometry pipeline, so it wants its
own tested change rather than riding along with something else.

Revisit when: CadQuery narrows its own return types, or that pipeline is being touched
anyway.
