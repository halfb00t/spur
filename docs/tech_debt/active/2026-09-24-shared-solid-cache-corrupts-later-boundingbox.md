# A cached solid's `.BoundingBox()` reads wrong after it has been STL-exported

Severity: must
Status: active
Date: 2026-09-24
Source: 03-01-PLAN.md Task 2 -- discovered while adding the required all-default-gear
  structured-logging test (tests/test_api.py), which collided with
  tests/test_model.py's pre-existing `kw={}` case (see tests/conftest.py's
  `_reset_solid_cache` fixture, added the same commit to work around it)
Related files:
- src/spur/model.py (`_build_cached`, `_write_export`, `export`)
- tests/conftest.py (`_reset_solid_cache` -- the test-side workaround)
- tests/test_model.py (`test_builds_one_valid_solid` -- the test that exposed it)

## Context

`_build_cached` is a process-global `functools.lru_cache` that returns the *same*
`cq.Solid` object for identical `GearParams`, by design (D-07 affinity: preview, then
STL, then STEP for one gear reuse the same worker's cache). `Shape.exportStl()` has a
side effect on that shared object: it attaches a triangulated mesh at the requested
tolerance, and a *later* `.BoundingBox()` call on the same object apparently reads that
mesh's approximate extent instead of exact BREP geometry -- reproduced directly:

```
before export,        zlen: 7.500000200000001
after preview STL export, zlen: 7.587720608891235   (off by ~0.088mm, close to
                                                       "preview"'s 0.08mm linear deflection)
after fine STL export,    zlen: 7.519603716332508
```

Measured this session (`.venv/bin/python`, `GearParams()` all-default, teeth=19): the
actual **exported STL bytes are unaffected** -- a fresh build and a preview-then-fine
build produce byte-identical fine-quality STL files. Only a diagnostic `.BoundingBox()`
call made *after* an export, on the *same* cached object, reads the mesh's looser
tolerance instead of the exact solid.

## Why it matters

No file under `src/spur/*.py` calls `.BoundingBox()` today (checked this session), so
there is no live production impact -- what ships to a user is correct regardless of
prior exports on the same cached solid. The risk is latent: if a future feature ever
calls `.BoundingBox()` (or a similar post-export geometry query) on a solid pulled from
this cache to report or verify a dimension, it would silently violate L08 ("a wrong
number is worse than no number") by reading a tessellation-approximate value instead of
the exact one -- and the corruption is *ordering*-dependent (whichever quality was
exported first sets the mesh a later measurement sees), so it would not show up in
isolated testing.

`tests/conftest.py`'s `_reset_solid_cache` autouse fixture (added alongside this file)
clears `_build_cached` before every test, which fully isolates the test suite from this
defect -- but it is a test-side workaround, not a fix to the underlying cache-sharing
behavior in `model.py`.

## Next step

If a production consumer of `.BoundingBox()` (or equivalent) is ever added: either stop
sharing the cached `cq.Solid` object across calls that mutate it (a `.copy()` before any
mesh-attaching operation), or explicitly recompute the bounding box from exact BREP
geometry rather than an attached mesh (check whether CadQuery/OCCT exposes a
non-optimal, mesh-independent bounding-box call). Revisit when: a feature needs to
compute or report a measured dimension from a `Solid` after it may have been exported,
or if a test outside this suite's autouse-fixture protection hits the same symptom.
