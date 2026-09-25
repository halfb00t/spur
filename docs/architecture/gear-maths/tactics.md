# gear-maths — tactics

## Shape

Three layers, each built on the one below:

1. **`Profile`** — a frozen dataclass of the radii and the half-tooth angle, produced by
   `profile(p)`. Every other function starts here. `half_angle(rho)` is the involute
   relation that the whole module leans on.
2. **Rules** — `bore_radius`, `recess_radii`, `root_fillet`, `recess_fillet`, `_tooth`,
   `check`. Each answers one question and returns the *effective* value, already capped.
   `recess_radii()` returning `None` means "no room for a groove at all", which is a
   legitimate outcome, not an error.
3. **Reports** — `derive(p, mate_teeth=None, mate_shift=0.0)`, which builds the `DerivedDimensions`
   document the API, the UI and the CLI all print, `warnings` included.

`centre_distance()` sits apart: it solves `inv(aw) = inv(α) + 2·tan(α)·Σx/Σz` for the
working pressure angle by bisection over `(0, 89°)`, because `inv` is monotonic there and
bisection has no failure mode that returns a plausible wrong answer (L08).

## Contracts

**In:** a validated `GearParams`. Range checks have already happened; this module deals
only with combinations that are individually in range but jointly impossible.

**Out:**

- `check(p) -> list[(message, fields)]` — consumed by `GearParams`'s own validator, which
  raises a `PydanticCustomError` carrying the field names. That is what becomes the
  `422` body's `detail[].ctx.fields`.
- `derive(p, mate_teeth=None, mate_shift=0.0) -> DerivedDimensions` — a frozen pydantic
  model. Every key is always present, and a value that does not apply (no bore, no
  recess, no mate) or cannot be computed honestly (a pair that cannot mesh, L08) is
  `None`, with the reason in `warnings`. The impossible-pair decision is made here once
  for both front ends.

**Rounding:** reported lengths are rounded to 3 decimals (µm) once, when `derive()`
builds the model, through `r3()`. That covers every length, the two capped fillets
included; their helpers also round internally, so this changed no value. Internal
arithmetic stays full double precision.
