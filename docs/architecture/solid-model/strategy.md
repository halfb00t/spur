# solid-model — strategy

## Responsibility

Turn a `GearParams` into one valid solid, and turn that solid into STL or STEP bytes.
Everything that touches the CAD kernel lives here and nowhere else.

`src/spur/model.py`.

## Boundaries

- **This is the kernel's only doorway.** `cadquery` and `OCP` are imported here and in no
  other module; no CadQuery object escapes past `export()`, which returns `bytes`. An
  import-linter contract fails the build on a violation, and the contract has been
  verified to actually break when one is introduced.
- **It builds; it does not decide.** Which fillet radius fits, whether a recess fits at
  all, whether the parameters are buildable — all answered in `calc.py` before anything
  here runs. `model.py` consumes the effective values (L03).
- **It does not queue.** Concurrency policy is the web layer's (L04). This module holds
  one lock because the kernel requires it (L06), and refuses nothing.
- It knows nothing about HTTP, files on disk that outlive a call, or the CLI.

## Design secrets it hides

Three, and they are the reason the module exists rather than being inlined:

1. **That OpenCascade is single-threaded and leaky.** One `RLock` (L06) and a
   `malloc_trim(0)` after every cache-missing export (L07). Callers see neither.
2. **How kernel geometry is picked back out.** After a cut, the edges to fillet or
   chamfer have to be found again — by radius and z for a groove floor, by position for a
   D-bore rim (which is an arc plus a straight line, so a type test would not do). These
   predicates are the fragile part and they are private.
3. **That a fast root fillet is arithmetic, not a kernel call** (L09).

## Key decisions

L06 (one lock), L07 (bounded caches + arena release), L09 (analytic root fillets),
and the tolerance convention: `TOL = 1e-6` mm is how kernel output is matched back to the
numbers that were asked for.
