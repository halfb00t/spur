---
phase: 33-interfaces-and-parity
review: 33-REVIEW.md
updated: 2026-10-28
---

# Phase 33 code review disposition

One row per finding in `33-REVIEW.md`. Every row starts `open`; nothing was fixed or skipped
during the execute-phase run. The human decides each one.

| ID | Severity | Disposition | Note |
|----|----------|-------------|------|
| WR-01 | warning | open | `buildForm` clears the page before setting `part`; a throw mid-build leaves `part` stale |
| WR-02 | warning | open | blank line splits the three shaft rows from the endpoint table in `docs/architecture/http-api.md` |
| IN-01 | info | open | reproduced by the orchestrator: `spoke_count=0-0` and `hole_count=0-0` answer 200 (pydantic 2.13.5 reads `"0-0"` as int 0) while Chromium blanks the box; built part equals the default today, but it breaks L49's "no blanked token gets a 200" invariant and the 91-token table cannot see it |
| IN-02 | info | open | `+-5` suggestion guesses "-5" |
| IN-03 | info | open | cache/queue API tests rely on unique parameters to avoid the shared export cache |
| IN-04 | info | open | browser `_js_fmt` rounds half-even vs page `fmt()` half-up; duplicates `displayed()` |
| IN-05 | info | open | CLI top-level description still says gears; `slug()` six significant digits (name frozen by L49) |
| IN-06 | info | open | repeated `designation` key reads last value; no test pins it |
