---
phase: 33-interfaces-and-parity
plan: 03
subsystem: api
tags: [wr02, fastapi, dependency, number-input, chromium, playwright, l49, decision-log]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-01's Chromium token table (91 tokens, 37 inputs) and the human's picks A1, B1, C1"
provides:
  - "src/spur/app.py: blank_in_a_number_box, _number_keys, _as_written_message, _numbers_as_written, wired as route dependencies on /api/info and /api/model.{fmt}"
  - "422 detail type number_as_written, loc [query, <field>], the D-04 wording"
  - "tests/number_box_tokens.py (the table as data) and tests/test_number_as_written.py (the light walker)"
  - "browser steps number box tokens and as-written sweep; ACCEPTED_LINK flipped to refused"
  - "L49 opened in the decision log; the WR-02 debt item retired"
affects: [33-04, 33-06, 33-08, 33-09]

actuals:
  tokens: 43365   # chars/4 over every added line of the three commits since 2ed7fd6 (35440 chars are not the three committed logs)
  tasks: 2
  commits: 3
plan_head_before: 2ed7fd67526d50c7b481652964b6d3e7c5e4d16f
plan_head_after: 0a9929ff92a55a18540f680be4100dd8645e0d9f

tech-stack:
  added: []
  patterns:
    - "a request-only route dependency (dependencies=[Depends(factory(Model))]) refuses on the raw query string before pydantic reads it and adds no OpenAPI parameter"
    - "the server rule is pinned to a committed browser-measured table that the gate's own Chromium re-reads on the page's inputs"

key-files:
  created:
    - tests/number_box_tokens.py
    - tests/test_number_as_written.py
    - .planning/phases/33-interfaces-and-parity/investigation/33-03-red-light.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-03-red-browser.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-03-browser.log
  modified:
    - src/spur/app.py
    - tests/test_browser.py
    - docs/architecture/decision_log.md
    - docs/architecture/web-ui.md
    - docs/architecture/http-api.md
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md

key-decisions:
  - "A1 as given: four conditions (surrounding whitespace, underscore, leading +, trailing .), the 10 non-finite and overflow tokens not added; an empty value is never the rule's"
  - "B1 as given: 30 links (29 gear number fields + mate_teeth), no per-token browser sweep; the table is walked in the light test and re-read in Chromium on every number input"
  - "C1 as given: the fix is in app.py before the part switch; params.py, cli.py and app.js are byte-identical to 6800769"

patterns-established:
  - "Every value of a repeated query key is checked, the first offending value names the key, entries come in query order"

requirements-completed: [REQ-wr02-fixed]

coverage:
  - id: D1
    description: "A gear link token the number box blanks is refused as written (422 number_as_written) on /api/info and /api/model.{fmt}, with the D-04 wording and no build"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: integration
        ref: "tests/test_number_as_written.py#test_a_trailing_dot_is_refused_as_written_with_the_canonical_form"
        status: pass
      - kind: integration
        ref: "tests/test_number_as_written.py#test_the_message_quotes_the_token_and_suggests_the_form_when_there_is_one"
        status: pass
    human_judgment: false
  - id: D2
    description: "The rule matches Chromium's table: no blanked token gets a 200 on any walked field of either route, and no held token is refused by the rule"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: integration
        ref: "tests/test_number_as_written.py#test_every_blanked_token_is_refused_and_no_held_token_is_by_the_rule"
        status: pass
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step number box tokens)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Boundary, empty, repeated-key, ordering and precision behaviour of the rule; the gear OpenAPI query parameters are unchanged"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: integration
        ref: "tests/test_number_as_written.py (boundary, repeated-key, two-key order, before-pydantic, held-token and seam tests)"
        status: pass
      - kind: other
        ref: "make gear.unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "In a real browser every gear number field and the mate box, followed as #<field>=%2B<default>, is refused with its field marked and no STL requested; face_width=5. flipped from built to refused"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (steps blank, unknown and accepted tokens, as-written sweep)"
        status: pass
    human_judgment: false
  - id: D5
    description: "L49 opened with the WR-02 paragraphs and the WR-02 debt item retired in the fixing commit"
    requirement: "REQ-wr02-fixed"
    verification: []
    human_judgment: true
    rationale: "A decision-log entry's wording and a debt item's retirement are read by a person; the greps in the plan only prove they exist"

duration: 14min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 03: A link number the box blanks is refused as written Summary

**The gear routes now answer `422 number_as_written` for any link number Chromium's number box would blank (`5.`, `+22`, ` 22`, `1_0`), through one request-only route dependency that runs before pydantic, so a blank form box can no longer sit over a non-default part; the rule is pinned to the 91-token Chromium table in a light walker and re-read on the page's own 30 inputs at every gate run.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-10-27T16:16:01Z
- **Completed:** 2026-10-27T16:30:31Z (the code commits; the full `make verify` run of 5 min 15 s sits inside it)
- **Tasks:** 2 (1 tracer, 1 auto)
- **Files modified:** 13 (3 created source/test files, 3 created logs, 7 modified, 1 moved)

## Accomplishments

- **The rule as shipped.** `blank_in_a_number_box(token)` is A1: `token != token.strip() or "_" in token or token.startswith("+") or token.endswith(".")`. `_numbers_as_written(model)` computes the model's number keys once (`int`, `float`, `int | None`; never `bool`, `Literal` or `str`), walks `request.query_params.multi_items()`, takes the first offending value of each key and raises one `422` with one entry per key in query order. It is a `Depends` on `/api/info` (`InfoQuery`) and `/api/model.{fmt}` (`ModelQuery`). `params.py`, `cli.py`, `app.js` and the `/api/schema` bytes (8723, `gear.unchanged`) are unchanged; the OpenAPI query parameters of both routes are pinned by a test.
- **Wording (D-04).** `"5." is not a number as written; write it as 5 or 5.0`, `"+22" ... write it as 22`, `"1_0" ... write it as a plain number, e.g. 22 or 2.5`; the token is quoted with `json.dumps`, so `\x0b22\u2028` is reflected as ASCII escapes (T-33-06, a test).
- **Boundary and empty.** `teeth=200` builds, `teeth=+200` is refused as written, `teeth=201` keeps `less_than_equal`; `teeth=` keeps pydantic's `422`; `face_width=5.&teeth=abc` answers only the as-written entry (the rule runs first).
- **Seen red, then green.** The light file went `15 failed, 4 passed` against the unfixed `app.py` (first line `E       AssertionError: /api/info [('face_width', '5.')] answered 200`, log `33-03-red-light.log`). The browser test failed in the step `blank, unknown and accepted tokens` with `AssertionError: /api/info?face_width=5. answered 200, not 422` (`33-03-red-browser.log`; the step name appears three times in the log). Both rows are in `bench/RESULTS.md`, `### Seen red once (Phase 33)`.
- **The browser proof.** `number box tokens`: 30 inputs x 91 tokens agree with the table (0.03 s). `as-written sweep`: 30 links, 1.18 s, each refused with its field marked (the mate with no outline), `#dl-stl` with no href and no STL request. The golden sweep is untouched and still reads `44 records, 44 distinct queries`. Cost and comparison are in `bench/RESULTS.md`, `### The as-written sweep in the browser (33-03)`: the two steps add 1.21 s to a test that takes 29.14 s alone; Phase 32's 39.46 s was measured inside the whole gate under 18 workers, so it is not subtracted.
- **Recorded and retired.** `## L49` opens with one paragraph on the rule, why Chromium's table and not the HTML spec, the human's A1/B1/C1, the 200-to-422 move, the wording, SC4's reading under C1 and the costly reversibility (56 lines added, 0 deleted). `web-ui.md` Errors and `http-api.md` Errors name the refusal. The WR-02 item is `Status: resolved` under `docs/tech_debt/resolved/`, its INDEX row is in the Resolved table, and `Resolved in:` carries the fixing sha.
- **Gate figures.** `make verify.fast`: `2220 passed in 11.32s`, `real 12.20` (limit 30 s). `make verify` (exit 0): `2667 passed in 314.50s (0:05:14)`, `real 315.45`, coverage 98.40 %, `Contracts: 10 kept, 0 broken.`, `gear.unchanged` green. That is 26 tests above 33-01's baseline of 2644 less this plan's and 33-02's; the 314.50 s reading is above the baseline's 229.17 s and above L43's 300 s bar on a host whose load was not recorded here. Phase 32 recorded the same spread (218.58 s to 358.81 s on the same code), so this is no claim about the plan; 33-09 owns the gate delta.

## Task Commits

1. **Task 1: Tracer: `face_width=5.` is refused as written from the page through the API, seen red, debt retired, L49 opened** - `69c1aa3` (fix); the debt sha follow-up `853d64a` (docs)
2. **Task 2: The browser proof over every gear number field and the table re-read** - `0a9929f` (test)

**Plan metadata:** the `docs(33-03): complete ...` commit that adds this file (hash in the orchestrator's return).

## Files Created/Modified

- `src/spur/app.py` - the four helpers and the two `dependencies=[Depends(...)]`; a module-docstring sentence
- `tests/number_box_tokens.py` - `Token(text, blank)` and `TOKENS`, 91 rows transcribed from 33-01's JSON, ASCII only
- `tests/test_number_as_written.py` - 19 light cases: sentences, escaping, both-route table walker, held tokens, boundary, repeated keys, order, before-pydantic, non-number fields, the OpenAPI seam
- `tests/test_browser.py` - `ACCEPTED_LINK` and `BAD_LINKS` comments, the flipped third block, `NUMBER_BOX_PROBE`, the two new steps
- `docs/architecture/decision_log.md` - `## L49`
- `docs/architecture/web-ui.md`, `docs/architecture/http-api.md` - the refusal in Errors
- `bench/RESULTS.md` - two seen-red rows and `### The as-written sweep in the browser (33-03)`
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` - retired
- three logs under `.planning/phases/33-interfaces-and-parity/investigation/`

## Decisions Made

A1, B1 and C1 as in 33-01's `## Decision result`, implemented exactly. The plan text also described a B2 branch (every refused table token on every field in the browser); the human picked B1, so it was not built. One choice inside the plan's room: the "write it as ... or <n>.0" suggestion keys on the trimmed token ending in `.`, so ` 5.` reads `5 or 5.0` and `22.` on an integer field reads `22`.

## Deviations from Plan

None - plan executed exactly as written, with three notes that are not rule deviations:

- The plan's verify line expects `make test PYTEST_ARGS="tests/test_browser.py ..."` to end in `1 passed`; the file holds three tests, so it ends in `3 passed` (both before and after the change).
- The test helper imports as `from number_box_tokens import TOKENS` (the tests directory is on the path, as `browser_session` is), not a package-relative import.
- The first light red run showed 3 non-rule failures (`Build pool not started`) from a test that used the model route without the stub fixture; the fixture was added before the red was recorded, so the logged red is the rule's.

**Total deviations:** 0.

## Issues Encountered

None.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's register. T-33-05 (a blank box over a built part) is mitigated and walked; T-33-06 (the reflected token) is mitigated by `json.dumps` and tested; the existing `writes_a_field_shut` guard still holds because `app.js` is unchanged. A very long token echoed in the message (T-33-07) is accepted as planned.

## Debt and ideas filed

None filed. One item retired: `docs/tech_debt/resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` (`Resolved in: 69c1aa3`), moved in the fixing commit with its INDEX row; the sha was added in `853d64a`, as in 33-02.

## Next Phase Readiness

- 33-04 adds the shaft routes; each must take `dependencies=[Depends(_numbers_as_written(<ShaftQuery>))]` so the same rule applies, and 33-08 repeats the browser proof on the shaft's 7 inputs.
- 33-06 must leave `refuse()` and `gearQuery()` byte-identical (C1); 33-09 diffs both against `6800769` and writes the L49 reading beside ROADMAP criterion 4 and REQ-wr02-fixed.
- REQ-wr02-fixed is declared by later plans too, so it stays open until the last declaring plan finishes.

## Self-Check: PASSED

- All created files exist (`ls` of the three source/test files and three logs); `docs/tech_debt/resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` exists and the `active/` path does not.
- Commits `69c1aa3`, `853d64a` and `0a9929f` are ancestors of HEAD; `git rev-list --count 2ed7fd6..HEAD` is 3 (the measured `commits:`).
- `git diff 6800769 -- src/spur/params.py src/spur/cli.py src/spur/static/app.js` prints nothing; `LC_ALL=C grep -c '[^ -~]' tests/number_box_tokens.py` prints 0; `grep -c '^## L49 '` prints 1 with 0 deleted lines in the L49 commit.

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
