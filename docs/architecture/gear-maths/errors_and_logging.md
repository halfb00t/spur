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
  where no working pressure angle exists, and `derive()` states why in a warning
  (L08).

Adding a rule means deciding which of the three it is. That is the decision, not the
arithmetic.

### The hob-cut (trochoid) root

`root_shape` is `radial` unless the user asks for `trochoid`, so a gear nobody asked about
prints the sentences above unchanged (L05). What a user reads once they ask, all from
`_ROOT_SENTENCES` (`calc.py`) and all ASCII:

- **Report nothing** — `root_thickness` and `root_gap` are null under the hob-cut root,
  with one sentence saying the tooth's thickness changes too fast near the root circle to
  give an honest number (`thickness not printed`). `root_form_d` and `root_waist` are null
  wherever the hob-cut root is not the one built.
- **Refuse into the radial root, with a reason** — a requested trochoid root that cannot be
  honest (no radial root to replace, no tip land, an unsolved junction, an invalid curve,
  a severed tooth) builds the radial root and says why. The radial numbers print beside
  that sentence, and so does the shipped undercut sentence ("this model uses a radial root
  instead"), which is still true there, byte for byte.
- **Cap and warn** — `root_fillet` is the hob's tip radius under the hob-cut root. Above
  the largest radius that keeps a tip land it is cut at that largest value floored to 3 dp,
  and the sentence names `root_fillet` and says the printed radius is within 0.001 mm of
  the largest (a bare "the largest" is not true of a floored value, and the floor can print
  0.000).
- **Undercut, restated** — where the hob-cut join is a crossing the sentence gives the
  cutter's own onset (rounded up to 0.1 teeth) and the smallest profile shift that avoids
  it (rounded up to 0.001), with no radial-root wording. Above the `profile_shift` field's
  1.0 it says no shift in range avoids it and prints none. A tangent join prints nothing.
- **Thin waist** — below `ROOT_WAIST_FLOOR` (0.4 mm, at the 3 dp printed) one sentence says
  how thin the tooth is at its narrowest in the hob-cut root and that more `teeth`, a larger
  `profile_shift` or a larger `pressure_angle` thickens it. It never refuses (a waist at or
  under zero is the refusal `tooth severed`) and never says undercut. **Known caveat:** the
  floor is a printability number, so it warns on 771 of the 10,326 gears of the Phase 18
  sweep product, 595 of the 616 at module 0.2, many of them with no undercut at all
  (`bench/RESULTS.md` "Bars adopted (19-02)"); on a small module the sentence is about the
  part's size, not a fault in it.

## Logging

None, deliberately. This code runs on every keystroke; it is pure, and its output *is*
its diagnostic — `warnings` in the response says what was changed and why. Nothing here
has a failure that a log line would help reproduce.

The serving layers have a structured logger now (`L20`, `src/spur/records.py`). This
module's silence is a boundary, not a shared gap: `calc.py` never imports it, the way it
never imports the CAD kernel — pure functions on every keystroke stay pure.
