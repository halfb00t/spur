# gear-maths — errors & logging

## Failure handling

There is no failure tier here in the usual sense: the module performs no I/O, calls no
external service and has nothing to retry. What it has is a two-way split on *user*
input, and that split is the product decision (L03):

- **Refuse** — a conflict between two things the user set explicitly. `check()` returns
  the message and the field names; `GearParams` raises `PydanticCustomError("infeasible")`
  carrying them; FastAPI turns that into `422` with the fields in `detail[].ctx.fields`,
  and the UI marks those inputs. Examples: a bore wider than the root, teeth that come to
  a point, recesses that leave no web.
- **Cap and warn** — a requested dimension that can be trimmed without contradicting an
  explicit choice. The capping function returns the effective value silently; `derive()`
  adds the sentence to `warnings`. Examples: a root fillet larger than the tooth gap, a
  face recess that does not fit between the hub wall and the tooth rim.
- **Report nothing rather than something wrong** — `centre_distance()` returns `None`
  where no working pressure angle exists, and `with_mate()` states why in a warning
  (L08).

Adding a rule means deciding which of the three it is. That is the decision, not the
arithmetic.

## Logging

None, deliberately. This code runs on every keystroke; it is pure, and its output *is*
its diagnostic — `warnings` in the response says what was changed and why. Nothing here
has a failure that a log line would help reproduce.

The project as a whole has no structured logger yet. That is an open gap for the serving
layers, not for this one: see `docs/tech_debt/active/2026-09-21-no-structured-logging.md`.
