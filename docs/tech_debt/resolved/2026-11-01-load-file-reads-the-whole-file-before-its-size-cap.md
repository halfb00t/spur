# `load_file` reads the whole file before enforcing the size cap on what it read

Severity: nice
Status: resolved
Date: 2026-11-01
Resolved in: 8fb0d9e fix(34.1-03): read at most one byte past the table file's size cap (D-10)
Source: Phase 34 code review (34-REVIEW.md IN-04)
Related files:
- src/spur/din5480_tables.py:343-358

## Context
The cap is checked on `stat().st_size`, then `read_bytes()` reads everything, then the cap is checked again on `len(raw)`. The second check can only fire after the memory is spent, so it bounds nothing, and the file-size test cannot tell it from the first. The comment calls the cap hygiene against a wrong path naming a large file, which `stat` already covers.

## Why it matters
A check that cannot bound anything reads as protection it does not give.

## Next step
`with path.open("rb") as f: raw = f.read(MAX_FILE_BYTES + 1)` and a single cap check on `len(raw)`. Revisit when `load_file` is next edited.

## Resolution
`load_file` reads through `path.open("rb")` taking `f.read(MAX_FILE_BYTES + 1)` and holds one read-time cap check on what it read; the `stat` check stays for a wrong path naming a large file (D-10). The two checks print one sentence, so three tests tell them apart: `test_a_file_over_the_cap_is_refused_at_the_stat_before_it_is_opened` (the open is faulted, so only the stat can refuse), `test_a_file_that_grew_past_the_cap_after_the_stat_refuses` (passes the stat, asserts the loader took exactly `MAX_FILE_BYTES + 1` bytes) and `test_a_read_error_after_the_stat_refuses_naming_the_path`; `test_the_file_size_cap_is_exact` is the unchanged boundary test. Each was seen red with its check removed (logs under `.planning/phases/34.1-address-tech-debt-din-5480-table-loader-and-gear-guard/investigation/34.1-03-red-*.log`).
