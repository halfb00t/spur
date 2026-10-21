---
phase: 28-refuse-the-bad-link
plan: 01
subsystem: web-ui
tags: [app.js, shareable-link, 422, playwright, decision-log, L44]

requires:
  - phase: 21-browser-test
    provides: the browser test harness and the `root_shape=bogus as today` pin this plan flips
  - phase: 24-bore-shape-selector
    provides: the pinned readHash()/gearQuery() lines this plan works around
provides:
  - a link value its control cannot hold is kept, sent and refused by the API's 422 (L44)
  - four browser steps that pin the refusal, its recoveries, the fresh-page case and the blank/unknown/accepted tokens
  - L44, the Phase 28 section of bench/RESULTS.md, the retired root-shape debt item
affects: [28-02, 28-03, 28-04]

actuals:
  tokens: 9700
  tasks: 3
  commits: 1
plan_head_before: 1ffad6b2b01aeace5d9c763af0890c1f16c87b4d
plan_head_after: cb93d4ebdf37a51aba85d4911945fd7a273170b4

tech-stack:
  added: []
  patterns:
    - "A side Map (`rejected`) beside the controls, filled by a read-back after assignment, instead of a client-side validator"

key-files:
  created:
    - .planning/phases/28-refuse-the-bad-link/investigation/28-01-red-old-pin.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-01-green.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-01-red-new-pin.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-01-tokens.log
  modified:
    - src/spur/static/app.js
    - tests/test_api.py
    - tests/test_browser.py
    - docs/architecture/decision_log.md
    - docs/architecture/web-ui.md
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md

key-decisions:
  - "L44: a non-blank link token its control reads back as '' is sent as given and refused by the server's 422 (D-02); no client-side validation"
  - "L44: blank stays the default and unknown keys stay ignored while the API answers 422 for an empty value (D-06)"
  - "L44: the mate box shows the server's bare message with no outline (D-05)"
  - "Tokens a number box blanks but the API accepts (` 22`, `22 `, `1_0`; `22.`, `5.`, `+5` for face_width) are sent and built as the server reads them"

requirements-completed: [REQ-bad-link-refused, REQ-bad-link-decision-logged, REQ-info-findings-triaged]

coverage:
  - id: D1
    description: "A link value its control cannot hold is sent, kept in the fragment, refused with the server's 422 text, outlines the field (not the mate box) and builds nothing"
    requirement: "REQ-bad-link-refused"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser (steps `bad link refused`, `bad link on a fresh page`)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The token clears on an edit of its field, an enum pick, the mate box, Reset or a new link; blank, unknown and accepted tokens behave as before"
    requirement: "REQ-bad-link-refused"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser (steps `bad link cleared`, `blank, unknown and accepted tokens`)"
        status: pass
    human_judgment: false
  - id: D3
    description: "L44 is logged beside L39/L42 without editing them, with the Phase 28 RESULTS section, web-ui.md and the retired debt item in one commit"
    requirement: "REQ-bad-link-decision-logged"
    verification:
      - kind: other
        ref: "git diff --numstat v0.5 -- docs/architecture/decision_log.md bench/RESULTS.md reads 0 deleted lines; make verify exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "REQ-info-findings-triaged is declared by this plan but the info-finding triage itself is later plans' work (28-02..28-04)"
    requirement: "REQ-info-findings-triaged"
    verification: []
    human_judgment: true
    rationale: "This plan only retires 26 IN-03 (line citations to function names); the rest of the triage is not in 28-01's tasks and the verifier must classify it"

duration: ~12min
completed: 2026-10-21
status: complete
---

# Phase 28 Plan 01: Refuse the Bad Link Summary

**A shared link whose value a form control cannot hold (`#root_shape=bogus`, `#teeth=abc`) is kept in a `rejected` map, sent as given and refused by the API's own 422 through the existing `problems()`/`fail()` path, instead of being dropped and rebuilt as the default part (L44).**

## Performance

- **Duration:** about 12 min (STATE `last_updated` 12:28Z to 12:40Z; no start time was recorded in-session, so this is approximate)
- **Tasks:** 3 (Task 1 tracer, Task 2 tdd, Task 3 docs and gate)
- **Files modified:** 8 tracked files plus 4 kept logs, one commit

## Accomplishments

- `app.js`: `const rejected = new Map()`, `refuse(name, input, token)`, `readHash()` clears the map and reads every field and the mate box back after assignment, `gearQuery()` sends a rejected token in the control's place (inside its one loop, so schema order holds), `update()` falls back to it for the mate, two clearing listeners and Reset's clear. `problems()` and `fail()` are unchanged.
- `tests/test_api.py`: ten tokens appended to the shareable-link pin, none removed or allow-listed (T-28-05).
- `tests/test_browser.py`: the old pin replaced by four steps, each oracle'd on the API's own 422 body (`_expected_422`); `app.js:NNN` citations became function names (26 IN-03).
- L44 appended after L43 without editing any earlier entry; `web-ui.md` states the contract; the Phase 28 section of `bench/RESULTS.md` holds the step timings, the token table and `### Seen red once (Phase 28)`; the root-shape debt item is `Status: resolved` and `git mv`-ed to `resolved/`.

## Red evidence (D-08)

| Run | First failure line | Log |
|---|---|---|
| Old pin, fix applied, pin untouched (`1 failed, 2 passed in 23.37s`) | `AssertionError: today's behaviour, filed as debt: docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md: /api/info was sent 'teeth=22&root_shape=bogus'` | `.planning/phases/28-refuse-the-bad-link/investigation/28-01-red-old-pin.log` |
| New step, only `app.js` reverted to `0efc87c` (`1 failed, 2 passed in 23.05s`) | `AssertionError: #root_shape=bogus&teeth=22: /api/info was sent 'teeth=22', the link's pairs are [('root_shape', 'bogus'), ('teeth', '22')]` (note `step: bad link refused`) | `.planning/phases/28-refuse-the-bad-link/investigation/28-01-red-new-pin.log` |

`app.js` was restored from a saved copy and `cmp` was clean before anything was staged.

## Step timings (`28-01-green.log`, exit 0, `18 passed in 27.35s`, browser test `26.70s call`)

| Step | Seconds |
|---|---|
| `bad link refused` | 1.06 |
| `bad link cleared` | 1.83 |
| `bad link on a fresh page` | 1.10 |
| `blank, unknown and accepted tokens` | 0.20 |

## Token table: blanked by the number box but accepted by the API (`28-01-tokens.log`, Chromium 153.0.8010.12)

` 22`, `22 ` and `1_0` answer 200 for both `teeth` and `face_width`; `22.`, `5.` and `+5` answer 200 for `face_width` only. These are sent and built as the server reads them while the box shows blank; `face_width=5.` is pinned as built.

## Gate

`make verify` ran (ruff, `mypy src tests docker bench scripts`, import-linter `5 kept, 0 broken`, unfinished-work scan, pytest). Result line: `1348 passed in 206.57s (0:03:26)`, coverage `TOTAL 97.99%`, `Required test coverage of 96.0% reached`, `exit 0`. The pre-commit `make verify.fast` also passed on the commit. `git diff --exit-code v0.5 -- tests/regression/` is empty.

## Commits

- `cb93d4e` fix(28): send a link value its control cannot hold, so the 422 refuses it -- log L44 (the one commit D-07 requires: fix, pin flip, L44, web-ui.md and the debt retirement together)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `bad link cleared` compared the sent query as a string**
- **Found during:** Task 2, first green run
- **Issue:** the helper compared `/api/info`'s query to `module=3&teeth=21`; the page sends schema order, `teeth=21&module=3`. The step failed on key order, not on behaviour.
- **Fix:** the helper compares decoded pairs (`_pairs`), as the plan's "sent pairs equal" wording intends. Key order is still asserted, where the plan asks for it, in `bad link refused`.
- **Files modified:** `tests/test_browser.py`
- **Commit:** `cb93d4e`

**2. [Rule 3 - Blocking] Lint line limit on a pinned token**
- **Found during:** Task 2, ruff
- **Issue:** the Reset pin token in `tests/test_api.py` is 112 columns, over ruff's 100.
- **Fix:** `# noqa: E501` on that line, the same precedent as the existing 108-column token two lines above it in that tuple. The token itself is unchanged.
- **Files modified:** `tests/test_api.py`
- **Commit:** `cb93d4e`

**3. [Rule 2 - Missing] L44 named D-01..D-06 and D-08 but not D-07**
- **Found during:** Task 3, acceptance check after `make verify`
- **Fix:** one sentence added to L44's **Retired** paragraph naming D-07 (the amendment lives in L44 alone, one commit). Docs only; the commit's `make verify.fast` hook passed.
- **Files modified:** `docs/architecture/decision_log.md`
- **Commit:** `cb93d4e`

**Total deviations:** 3 auto-fixed (1 bug in the test I wrote, 1 lint blocker, 1 doc completeness). **Impact:** none on the contract.

### TDD note

Task 2 is `tdd="true"`, but D-07 requires one commit for the fix, the pins and the docs, and D-08 defines the red evidence as two kept logs, so there is no separate `test(...)` then `feat(...)` pair. The RED evidence is the new-pin red log above (target test, target step, planned assertion, with only `app.js` reverted).

## Tangents (not done, per scope)

- `tests/browser_session.py:678` still cites a stale `app.js:340` (that file is outside this plan). Left as is.

## Known Stubs

None.

## Threat Flags

None. The token reaches only `input.value`, `URLSearchParams` and `history.replaceState`; messages still go through `textContent` and `writes_a_field_shut` passes (T-28-01).

## Debt ledger

No debt item was filed. One item was retired: `docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md` (`Resolved in:` carries the commit subject; Plan 28-04 writes the short sha, RESEARCH Pitfall 8). The mate box's missing outline (D-05) and the page being looser than the API about blank values (D-06) are recorded in L44 as decisions, not debt.

## Self-Check: PASSED

- Files exist: `app.js`, the four logs, `decision_log.md` (L44 is the last `^## L` heading), `bench/RESULTS.md` (three Phase 28 headings), the resolved debt item (and the active path is gone).
- Commit `cb93d4e` is an ancestor of HEAD; `commits: 1` measured from `1ffad6b..HEAD`.
- Acceptance greps: `rejected.set(` once, `fields.set(` once, `BOGUS_LINK` 0, `app.js:[0-9]` 0 in `tests/test_browser.py`, `_expected_422(` 7 lines, `git diff --numstat v0.5` reads 0 deleted lines for the decision log and `bench/RESULTS.md`.
