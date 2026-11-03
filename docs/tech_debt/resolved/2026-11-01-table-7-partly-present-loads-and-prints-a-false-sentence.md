# A file with Table 7 only partly present loads and then prints a false sentence

Severity: must
Status: resolved
Date: 2026-11-01
Resolved in: 1ea2e45 fix(34.1-04): refuse a table file with Table 7 partly present (D-05)
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

## Resolution
`problems()` refuses a document whose four Table 7 lists (`deviations`, `classes`, `tolerances`, `columns`) are neither all empty nor all non-empty, with one sentence naming the empty lists and no value (D-05). The all-empty document still loads (`test_a_document_of_empty_row_tuples_loads`, unchanged). Four `BROKEN` cases, one per list (`Table 7 without its deviations`, `... classes`, `... tolerances`, `... columns`; the columns case is this item's own reproduction), each seen failing with the rule's append replaced by `pass` (log `.planning/phases/34.1-address-tech-debt-din-5480-table-loader-and-gear-guard/investigation/34.1-04-red-table-7.log`: three `DID NOT RAISE`, and the tolerances case, which the `row_by_column` check still refuses, fails on its needle).

The rule covers the four Table 7 lists only; the sizes list is outside it. A file with the sizes or Table 7 alone is filed separately: `docs/tech_debt/active/2026-11-02-a-table-file-with-sizes-or-table-7-alone-loads-and-prints-a-false-sentence.md`.
