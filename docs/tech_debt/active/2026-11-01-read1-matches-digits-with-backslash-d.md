# Read 1 matches digits with `\d`, against the repository's own stated rule

Severity: nice
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-07)
Related files:
- scripts/din5480_read1.py:53
- scripts/din5480_read1.py:81
- src/spur/din5480.py:220-223

## Context
`_NUM` and `_tooth_count` use `\d`, which matches Unicode digits, and `float()` / `int()` accept them. `src/spur/din5480.py:220-223` records exactly this as a pitfall and uses `[0-9]`. A `pdftotext` token with a non-ASCII digit would be read as a number rather than raise as a row-shaped line holding a non-number.

## Why it matters
A mis-extracted digit would enter the read instead of failing it; the two-reads gate would still catch a differing pair, but not the same slip made twice.

## Next step
`re.compile(r"^-?[0-9]+(\.[0-9]+)?$")` and `re.fullmatch(r"[0-9]+", token)`. Revisit when `scripts/din5480_read1.py` is next edited.
