# A file with Table 7 only partly present loads and then prints a false sentence

Severity: must
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-06)
Related files:
- src/spur/din5480_tables.py:266
- src/spur/shaft_calc.py:476-479

## Context
The column-selection check runs only `if t.columns:`. A file with sizes, deviations and classes but an empty `columns` list loads, and every fit then reads "the fit 8f is not in DIN 5480-1 Table 7, whose shaft deviations are f, h and k": a claim about the standard that is really a claim about a truncated file (reproduced with the synthetic fixture). The tool's own comment accepts a missing letter reading as "fit outside Table 7", and completeness is a transcription-time check by L50, so this is a logged trade-off. The sentence is still untrue.

## Why it matters
A printed statement about DIN 5480 that is false is the L08 failure class: the tool says something about the standard that nobody checked.

## Next step
In `problems()`, refuse a file where the four Table 7 lists are neither all empty nor all non-empty. `test_a_document_of_empty_row_tuples_loads` keeps passing. Revisit when the loader is next edited.
