# gear-maths — strategy

## Responsibility

Everything about an involute spur gear that can be known without building a solid:
the profile geometry, the derived dimensions, the numbers you would measure on the
finished part, which parameter combinations cannot produce a sound gear, and which
requested dimensions had to be trimmed to fit.

`src/spur/calc.py`, with `src/spur/params.py` as its input contract.

## Boundaries

- **No CAD kernel, ever.** This module runs on every keystroke in the UI. If it could
  reach OpenCascade, that property would disappear quietly and nobody would notice until
  the form went slow. Enforced by an import-linter contract, not by discipline (L13).
- **No I/O, no state, no logging.** Pure functions of `GearParams`. Same input, same
  answer, always.
- **It decides; it does not act.** `root_fillet()` and `recess_fillet()` return the
  radius that will actually be used; `model.py` consumes that number rather than
  re-deriving it. There is one place each rule is written down.
- Talks to nobody. `model.py`, `app.py` and `cli.py` all call into it; it calls none of
  them. `params.py` calls `check()` from its validator — the one edge pointing inward.

## Key decisions

- **L03** — cap and warn, or refuse; never guess. This module is where that line is
  drawn: `check()` holds the conflicts only the user can resolve, the `*_fillet()` and
  `recess_radii()` functions hold the ones that can be trimmed.
- **L05** — defaults are absolute millimetres and do not rescale.
- **L08** — an impossible mating pair gets a warning, not a number. `centre_distance()`
  returns `None` and `with_mate()` turns that into a warning, once, for both the API and
  the CLI.
- **L10** — the root is radial below the base circle; `derive()` warns where that
  matters.
