# A link token the number box blanks but the API accepts builds a non-default part under a blank box

Severity: must
Status: resolved
Resolved in: 69c1aa3 fix(api): refuse a link number the box would blank (WR-02, L49) (gsd/phase-33-interfaces-and-parity)
Date: 2026-10-21
Source: 28-REVIEW WR-02, deferred at the 28-05 checkpoint (D-20)
Related files:
- src/spur/static/app.js:115-117
- src/spur/static/app.js:135-142
- tests/test_browser.py:122
- docs/architecture/decision_log.md:2990
- bench/RESULTS.md:6637

## Context
The page's convention (D-06) is that a blank control means the default. `refuse()` (`app.js:115-117`) records a non-empty
link token that its control reads back as `''`, and `gearQuery()` (`app.js:135-142`) sends that token as given (L44).
For ` 22`, `22 ` and `1_0` (`teeth` and `face_width`) and `22.`, `5.` and `+5` (`face_width` only), the box reads `''`
and the API answers 200 (`bench/RESULTS.md:6637`, `### Tokens a control cannot hold (28-01)`). The part is then built
from the token while the box shows blank, so the form says "default" and the part is not the default. Before Phase 28 the
page built the default part, which at least matched the blank box. L44's paragraph **The server decides**
(`decision_log.md:2990`) records this and `tests/test_browser.py:122` (`ACCEPTED_LINK = "face_width=5."`) pins it as
built. The address bar names the token and the dimensions table is the server's; the form gives no sign of which field
carries the hidden value, and Reset is the only visible cue.

The token list above is not the whole class (v0.6 milestone audit, 2026-10-23). `/api/info` (FastAPI TestClient, on
`3adc939`) also answers 200 for `teeth=+22`, `mate_teeth=+22`, `mate_teeth=%2022`, `pressure_angle=20.`, `module=+2`
and `module=2.`. The `bench/RESULTS.md:6637` table probed only `teeth` and `face_width`; its `teeth=+5` row is a 422
because 5 is out of range, not because `+` is refused. That the number box blanks these tokens is inferred from the HTML
rule for a number input's value (no leading `+`, no trailing `.`, no leading space), not observed in Chromium; a fix
should probe every number field and `mate_teeth` in the browser first.

The review's suggested fix shape (page-written wording beside the server's messages, for example `<field title> was opened
as "<token>" and is built as the server reads it.` after a 200 from `/api/info`) was not taken: L44 and success
criterion 1 kept every message in the server's words (L02), and showing the token inside the control was rejected as D-01.

## Why it matters
L05: a parameter the user did not set must never silently change the part. A blank box that carries a hidden non-default
value is a visible form that disagrees with the part, and a number from that part is one someone will cut metal to (L08).
The tension is visible only in the address bar and the dimensions table.

## Next step
Revisit when the next edit of `refuse()` or `gearQuery()` in `src/spur/static/app.js`, or a report of a part that does
not match a blank box. The wording and placement of any notice are a UI design choice with more than one honest shape;
take them at a discuss-phase, not in a gap closure.

## Resolution
The API refuses the tokens as written (`number_as_written`, L49), on `/api/info` and `/api/model.{fmt}`, so the page's unchanged
`refuse()` and `gearQuery()` mark the box and no part is built. The probe this item asked for was run in Chromium over every
number input (33-01, `bench/RESULTS.md` `### Tokens the number box blanks, every field (33-01)`): every token above, and the
`+22`, `mate_teeth=%2022`, `20.`, `+2` and `2.` additions, is blank on all 37 inputs. The server rule and the table are pinned
by `tests/test_number_as_written.py`, and the browser steps `blank, unknown and accepted tokens`, `number box tokens` and
`as-written sweep` hold it on the page.
