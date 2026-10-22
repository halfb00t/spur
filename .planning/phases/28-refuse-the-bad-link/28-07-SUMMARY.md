---
phase: 28-refuse-the-bad-link
plan: 07
subsystem: web-ui
tags: [gap-closure, app.js, L44, review-findings, pins]
status: complete
gap_closure: true
gap_ids: [G-28-1]

requires:
  - phase: 28-refuse-the-bad-link
    provides: D-19 (`fix`), D-20 (`defer`), D-22 (`fix`) in 28-CONTEXT.md, the human's dispositions from 28-05
provides:
  - write() clears the rejected entry of each field it writes (WR-01, D-19)
  - readHash() assigns the mate box once, its pin tightened through the read-back (IN-01, D-22)
  - two dated amendments at the end of L44 and a pointer in its "When it clears"
affects: [28-08]

actuals:
  tokens: 2800          # chars/4 over the non-.planning diff (11,267 chars); the two red logs are excluded
  tasks: 3
  commits: 2
plan_head_before: 947e05105043511e49000f70d7a049d8ae529326
plan_head_after: aede0fddc7a5358a77cc58d4ed7b807cf7852d0b

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/28-refuse-the-bad-link/investigation/28-07-red-selector-write.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-07-red-readhash-pin.log
  modified:
    - src/spur/static/app.js
    - tests/test_browser.py
    - tests/test_api.py
    - docs/architecture/decision_log.md
    - bench/RESULTS.md

key-decisions:
  - "WR-01 (D-19) is closed by write()'s own clear of the field it writes, not the empty-box check RESEARCH Pitfall 3 offered; L44 amended 2026-10-21"
  - "IN-01 (D-22) replaces the readHash-end pin with a longer token through the mate read-back, read by the human as tightening SC2; L44 amended 2026-10-21"
  - "WR-02 (D-20) is deferred as the human chose; nothing changed here"

requirements-completed: [REQ-bad-link-refused, REQ-bad-link-decision-logged, REQ-info-findings-triaged]

coverage:
  - id: D1
    description: "After #bore_d=abc and a pick of No bore, /api/info carries bore_d=0 (what the box shows), the build ends green and no field is marked"
    requirement: "REQ-bad-link-refused"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser#bad link cleared"
        status: pass
      - kind: unit
        ref: "tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
    human_judgment: false
  - id: D2
    description: "readHash() assigns the mate box once; the pin covers assignment, mate read-back and tail as one token"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser#bad link refused, bad link cleared"
        status: pass
    human_judgment: false
  - id: D3
    description: "L44 carries a dated amendment per fix (WR-01, IN-01) and no sentence of it is rewritten"
    requirement: "REQ-bad-link-decision-logged"
    verification:
      - kind: other
        ref: "the task 1 and task 3 verify scripts print `D-NN fix: carried out` checks on L44 text"
        status: pass
    human_judgment: false
---

# Phase 28 Plan 07: app.js review findings per the human's dispositions Summary

WR-01 and IN-01 are fixed in `src/spur/static/app.js`, each as its own commit with its test seen red first and L44 amended; WR-02 is deferred as the human chose and nothing moved for it.

## Findings

| Finding | D line | Token | Commit | Red line |
|---|---|---|---|---|
| WR-01 | D-19 | `fix` | `3224ec7` `fix(28): a selector pick that writes a field ends its rejected link token (28-REVIEW WR-01)` | `AssertionError: /api/info was sent 'bore_d=abc', not 'bore_d=0'`, `1 failed, 17 passed in 27.85s`, log `28-07-red-selector-write.log` |
| WR-02 | D-20 | `defer` | not run | not run: D-20 defer (28-05 filed `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`; 28-08 writes the ledger) |
| IN-01 | D-22 | `fix` | `aede0fd` `refactor(28): assign the mate box once in readHash, its pin tightened through the read-back (28-REVIEW IN-01)` | `AssertionError: mateInput.value = h.get('mate_teeth') ?? ''; refuse('mate_teeth', mateInput, h.get('mate_teeth')); applyRelations(); deriveSelectors(); }` at `tests/test_api.py:311`, `1 failed, 61 deselected in 2.08s`, log `28-07-red-readhash-pin.log` |

## What changed

- **WR-01.** The pick path assigns the box without an `input` event on that field, so the form's clearing listener never ran and the request kept sending the link token while the box showed the pick. `write()` now runs `rejected.delete(field)` right after the box assignment. New `bad link cleared` case: `#bore_d=abc`, pick "No bore", `/api/info` carries `bore_d=0` alone (the plan's ASSUMPTION held on the green run), STL link set, nothing marked, no error. One new `tests/test_api.py` token, `input.value = to; rejected.delete(field);`. The selectors-section guard still counts exactly one value write.
- **IN-01.** The second assignment of the mate box in `readHash()` and its justifying comment are deleted. The readHash-end token in `tests/test_api.py` is replaced by a longer one containing the old assignment and tail with the `refuse('mate_teeth', ...)` read-back between them (kept on one line with `# noqa: E501`, 162 columns). The separate `refuse('mate_teeth', ...)` token stays.
- **L44.** Two `**Amendment (2026-10-21, ...)**` paragraphs at the end of the entry, before `## L45 — `, and one pointer in **When it clears** after the sentence about a selector pick. No other sentence of L44 is edited.
- **bench/RESULTS.md.** Two 28-07 rows in `### Seen red once (Phase 28)`.

## Verification

- `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q"` after each fix: `18 passed` (every step, the golden sweep included).
- `.venv/bin/python -m pytest tests/test_api.py -k "shareable_link" -n0 --no-cov -q -p no:cacheprovider`: `1 passed, 61 deselected in 2.04s`.
- `make verify`: `======================= 1348 passed in 197.99s (0:03:17) =======================`, `exit 0`.
- `git diff --exit-code v0.5 -- tests/regression/`: exit 0, empty.

## Deviations from Plan

None - plan executed exactly as written. The IN-01 pin was at `tests/test_api.py:263`, not 262 as the orchestrator note said; the plan's line number was right. The `# noqa: E501` token comment gives 162 columns, not a guessed 140 (fixed before commit).

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path or file access; `write()` and `readHash()` only change which value the existing `/api/info` request carries.

## Deferred

WR-02 (D-20): `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`, filed by 28-05. No new item filed by 28-07.

## Next

Ready for 28-08.

## Self-Check: PASSED

- FOUND: `src/spur/static/app.js`, `tests/test_browser.py`, `tests/test_api.py`, `docs/architecture/decision_log.md`, `bench/RESULTS.md`, both 28-07 red logs
- FOUND: commits `3224ec7`, `aede0fd` (`git rev-list --count` from the ledger base: 2)
