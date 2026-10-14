# The hex-bore warning names its fields by form title

Date: 2026-10-14
Source: `.planning/phases/24-bore-shape-selector/24-REVIEW.md` finding IN-04 (second half: the field-name wording is separate from the default-values wording)
Related files:
- src/spur/calc.py (the "Hex bore replaces the round profile: ... ignored" sentence in `derive()`)
- src/spur/params.py (the `title` metadata: `bore_d` is "Bore Ø", `bore_flat` is "D-flat")

## Context
Quick task 261014-jsp made the hex-bore warning name only the round fields the request set
away from their defaults. It still says `bore_d (12 mm)` and `bore_flat (3 mm)`, which the
form labels "Bore Ø" and "D-flat". A user who set the field in the form reads a name the
form never showed. The review asked for the form titles; that half was outside the quick
task's locked scope and is not done.

## Why it matters
A warning in words the form does not use costs the reader one lookup per hex part with a
round field set. It is small, but the form is where most users meet the warning.

## Next step
Decide whether `warnings` should speak form titles everywhere or stay on field names. Field
names are what the API and CLI users type, and a warning text that reads the schema titles
couples `calc` to form metadata, so the answer is a decision with its own `Lxx`, not a
tweak to one sentence. Revisit when a user reports the snake_case name as confusing, or
when another warning is next reworded.
