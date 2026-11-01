# `SCHEMA_VERSION` is defined and never used

Severity: nice
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-03)
Related files:
- src/spur/din5480_tables.py:32
- src/spur/din5480_tables.py:143
- scripts/din5480_read1.py:203
- scripts/din5480_tables_tool.py:221
- scripts/din5480_tables_tool.py:258

## Context
`SCHEMA_VERSION = 1` has no reader. The schema uses the literal `Literal[1]` (line 143), and the two scripts and the tests write the bare `1`.

## Why it matters
A version bump has four places to miss, and the constant suggests a single source that does not exist.

## Next step
Remove the constant, or use it in the scripts and derive the `Literal` from it. Revisit when the schema version next changes.
