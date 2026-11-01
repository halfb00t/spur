# `load_file` reads the whole file before enforcing the size cap on what it read

Severity: nice
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-04)
Related files:
- src/spur/din5480_tables.py:343-358

## Context
The cap is checked on `stat().st_size`, then `read_bytes()` reads everything, then the cap is checked again on `len(raw)`. The second check can only fire after the memory is spent, so it bounds nothing, and the file-size test cannot tell it from the first. The comment calls the cap hygiene against a wrong path naming a large file, which `stat` already covers.

## Why it matters
A check that cannot bound anything reads as protection it does not give.

## Next step
`with path.open("rb") as f: raw = f.read(MAX_FILE_BYTES + 1)` and a single cap check on `len(raw)`. Revisit when `load_file` is next edited.
