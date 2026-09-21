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
3. **Reports** — `derive(p)` and `with_mate(info, p, z2)`. These assemble the JSON
   document the API, the UI and the CLI all print, including the `warnings` list.

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
- `derive(p) -> dict[str, Any]` — the dimensions document, including `warnings: list[str]`.
  Keys vary with the parameters: recess fields are `None` when there is no recess. The
  `Any` here is deliberate and tracked (L14).
- `with_mate(info, p, z2)` — `derive()`'s output plus `mate_teeth` and `centre_distance`,
  or plus a warning and a `None`. Shared so the "impossible pair" decision is written
  once for both front ends.

**Rounding:** reported values are rounded to 3 decimals (µm) at the boundary, in
`derive()`. Internal arithmetic is full double precision.
