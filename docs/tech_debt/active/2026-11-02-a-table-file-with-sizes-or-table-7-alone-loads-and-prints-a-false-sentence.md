# A table file with the sizes list or Table 7 alone loads and prints a false sentence

Severity: must
Status: active
Date: 2026-11-02
Source: Phase 34.1 plan 04, the human's answer to the edge checkpoint (34.1-01, `edge: option-a`)
Related files:
- src/spur/din5480_tables.py (`problems()`, the all-or-none rule on the four Table 7 lists)
- scripts/din5480_tables_tool.py (`_check_file`, `cmd_assemble`)
- scripts/din5480_read1.py (`main`)

## Context
The all-or-none rule added for the Table 7 item (D-05) covers the four Table 7 lists only, so the sizes list sits outside it. Reproduced on the synthetic fixture: with the four Table 7 lists emptied and the sizes kept, `parse` loads and `derive_shaft(ShaftParams())` prints "the fit 8f is not in DIN 5480-1 Table 7, whose shaft deviations are  and whose tolerance classes are ."; with only `sizes` emptied, `parse` loads and the same call prints "DIN 5480-2 does not list W 25x1.25x18 in its size tables". Both are claims about the standard that are really claims about a truncated file.

The sizes list was left out because the transcription tools read the two halves separately: `make tables.check` on one read and `make tables.read1`'s own check parse a sizes-only or a Table-7-only document, and a rule over all five lists would refuse every such read (34.1-RESEARCH F3). A whole file is already held to every list by `check --complete`'s counts, so the gap is a file that skips that step.

## Why it matters
A printed statement about DIN 5480 that is false is the L08 failure class, and a truncated file that loads is the way to reach it.

## Next step
Widen the rule to the sizes list with a keyword-only part-read flag: `problems(t, *, whole: bool = True)` and `parse(text, *, whole: bool = True)`, `sizes` joining the rule only when `whole`; `_check_file` in `scripts/din5480_tables_tool.py` and `main` in `scripts/din5480_read1.py` pass `whole=False`; `load_file` and `cmd_assemble` keep the default. Tests: a part read is held to the four-list rule only; `check` says `ok` for each part read; read 1's `main` writes a sizes-only read the loader accepts. Revisit when the loader is next edited.
