# A code comment still points at the debt file Phase 34 moved to `resolved/`

Severity: nice
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-02)
Related files:
- src/spur/din5480.py:211
- src/spur/din5480.py:165

## Context
The `form_diameter` docstring cites `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`, which Phase 34 `git mv`'d to `docs/tech_debt/resolved/`. The path is dead. Line 165 (`measure_over_pins`) still says "Phase 34 can pass limit thicknesses unchanged", which is now done.

## Why it matters
A reader who follows the path finds nothing, and the future-tense note misdescribes the code.

## Next step
Point the docstring at `resolved/` and reword line 165 to the present tense. Revisit when `src/spur/din5480.py` is next edited.
