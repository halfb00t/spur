---
phase: 33-interfaces-and-parity
plan: 07
subsystem: ui
tags: [vanilla-js, hashchange, part-switch, shareable-link, playwright]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-06 Gear | Shaft switch, PARTS descriptor, buildForm(which), formSeq; 33-01 decision C1 (refuse() and gearQuery() stay byte-identical)"
provides:
  - "partOf(hash), followHash(), refuseLink(values) and the refused state in app.js; the hashchange listener and the bootstrap go through followHash"
  - "A part=shaft link opens the shaft form on any page and round-trips; a gear link carries no part key; any other part is refused in the page's words and builds nothing"
  - "Browser steps 'shaft link round trip' and 'bad part refused'; the swapped hashchange pin with three more tokens"
  - "L49 paragraphs 'The part switch' and 'An unknown part'; web-ui.md; the add-alongside rows idea"
affects: [33-08, 33-09]

actuals:
  tokens: 7165   # chars/4 over the added lines of src/, tests/, bench/ and docs/ (logs excluded)
  tasks: 2
  commits: 2
plan_head_before: fd8ffccaa0832c9d6b90c82cc96d3a60b26bb5f6
plan_head_after: d1f60e73b5ab0d77ffa8ccce1c1c35fa8f7a65ff

tech-stack:
  added: []
  patterns:
    - "A link is read in two steps: partOf picks the part by literal comparison, then the form of that part is built before the hash is read into it"
    - "A same-part hashchange runs before any await, in the event itself, so the golden sweep's one-request-per-link count holds"
    - "A refused state (a variable the update loop checks first) instead of a second code path: an edit or Reset reaches update() and update() returns"

key-files:
  created:
    - docs/ideas/2026-10-27-gear-result-rows-from-the-schema.md
    - .planning/phases/33-interfaces-and-parity/investigation/33-07-red-pins.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-07-red-browser.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-07-browser.log
  modified:
    - src/spur/static/app.js
    - tests/test_api.py
    - tests/test_browser.py
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/architecture/web-ui.md
    - docs/ideas/INDEX.md

key-decisions:
  - "part starts as the empty string, not 'gear': followHash's same-part test then cannot be true before a form exists, and a bad part at a fresh load still builds the gear form"
  - "refuseLink always rebuilds the gear form through buildForm('gear') instead of keeping a second reset path for the case where the gear already shows; one schema fetch per bad link, and every clear (rows, downloads, scene, in-flight request, debounce) comes from the one place that already does them"
  - "followHash bumps formSeq before it looks at the part, so a slower build of an earlier link (a click, a refused link) returns false instead of landing under the newest link"
  - "the same-part branch calls markPart() before readHash(), so a valid link after a refused part checks the radio again"

patterns-established:
  - "The pin test asserts that no await precedes followHash's same-part line, so the synchronous path cannot be lost by a reorder"

requirements-completed: [REQ-shaft-web]

coverage:
  - id: D1
    description: "A shaft link (#part=shaft&reference_d=26&teeth=19) round-trips on hashchange and on a fresh page: form built then filled, shaft query sent, hash part-first in schema order; gear links carry no part, an empty part is the gear"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step shaft link round trip)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A null shaft number has no row (odd-z link: no Measurement over pins M_Re, designation W 26x1.25x19x8f); the download is named spur_shaft_w26x1.25x19.stl by the server"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step shaft link round trip)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Shaft boundary: shank_length=500 builds; 500.5 and fit=8F are 422s that mark their boxes with no shaft STL requested; the shank diameter box is dimmed with its reason exactly when shank_length is 0; gear keys and designation in a shaft link are ignored"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step shaft link round trip)"
        status: pass
    human_judgment: false
  - id: D4
    description: "An unknown part (bogus, gear, Shaft, constructor, __proto__, part given twice) shows the page's message, the gear form at defaults, neither radio checked, nothing drawn, no build request; an edit or Reset builds nothing; a radio click or a new link ends it"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bad part refused)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The hashchange pin is replaced by the followHash token and three tokens are added, seen red against 33-06's app.js; the same-part branch is asserted to run before any await"
    requirement: REQ-shaft-web
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
    human_judgment: false
  - id: D6
    description: "L49 'The part switch' and 'An unknown part', web-ui.md, the add-alongside rows idea and the browser cost match the page as shipped"
    verification: []
    human_judgment: true
    rationale: "Whether the decision-log prose and the architecture page say what the page does is a reading judgment; the grep acceptance criteria only prove the paragraphs exist"

duration: 15min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 07: Shaft links and the unknown part Summary

**A `part=shaft` link opens and round-trips on any page through `partOf` and `followHash`, a gear link stays `part`-free, and any other `part` is refused in the page's own words with nothing built until a switch or a new link, with the L49 record, web-ui.md and the rows idea written.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-10-27T17:26:35Z (ledger written; reading began about 2 min earlier)
- **Completed:** 2026-10-27T17:41:00Z
- **Tasks:** 2
- **Files modified:** 7 tracked files modified or created (plus 3 logs)

## Accomplishments

- `partOf(hash)` reads the `part` values of the hash through `partValues` and returns `'gear'` for none or one empty value, `'shaft'` for exactly one `shaft`, else `null`, by literal comparison only (T-33-15). `followHash()` clears `refused`, bumps `formSeq`, and then: same part -> `markPart(); readHash(); update();` before any `await`; `null` -> `refuseLink`; another part -> `await buildForm(which)` and on `true` `readHash(); update();`. A build error shows `Could not build the form: ...`.
- `refuseLink(values)` sets `refused` to `` Unknown part "<values joined by ', '>" in the link; use the Gear or Shaft switch `` (JSON-quoted, shown through `showMessages`, T-33-23), rebuilds the gear form, puts every field at its default, unchecks both radios and leaves the hash as it is. `update()` returns right after `showMessages([refused])` while `refused` is set, so an edit or Reset builds nothing (T-33-24). `switchTo` clears `refused` first.
- The `hashchange` listener is `window.addEventListener('hashchange', followHash);` and the bootstrap is `applyTheme(); resize(); followHash();`. `refuse()` and `gearQuery()` are byte-identical to `6800769` (extracted and compared; `git diff 6800769` count of edited lines naming them: 0). The golden sweep step is unchanged and still reads `golden sweep: 44 records, 44 distinct queries, 1 distinct dimmed sets`.
- Browser step `shaft link round trip`: the odd-z link from the gear (form shows 26 and 19, sent pairs `reference_d=26`, `teeth=19`, hash `part=shaft&reference_d=26&teeth=19`, no `Measurement over pins M_Re` row, `W 26x1.25x19x8f` shown, download `spur_shaft_w26x1.25x19.stl`); `shank_length=0` dims `shank_d` with `Needs Shank length above 0`, `shank_length=20` does not; `shank_length=500` builds and draws; `shank_length=500.5` and `fit=8F` are 422s marking one box each with no shaft STL asked for; a link with gear keys and `designation=` sends `teeth=19` only; a fresh page opened on the odd-z link builds the shaft form and the same query; `teeth=24` and `part=&teeth=23` return to the gear with `part`-free hashes.
- Browser step `bad part refused`: the six bad links each show the message, uncheck both radios, leave 31 gear fields at their defaults, no rows, no href, no `data-triangles`, the hash as written; the request count across them, then a teeth edit and Reset, is unchanged; a radio click builds the shaft and clears the message; `part=bogus` from the shaft refuses again; `teeth=20` builds the gear.
- L49 gained **The part switch** and **An unknown part** (39 lines appended, 0 deleted), web-ui.md gained the switch, the descriptor, the rows from `dims`, the unknown-part message and the three steps, and the add-alongside rows decision is filed as an idea with its trigger.

## Task Commits

1. **Task 1: Tracer: shaft links round-trip, gear links stay `part`-free, an unknown `part` is refused and builds nothing** - `c728f9a` (feat)
2. **Task 2: Record the page: L49's paragraphs, web-ui.md, the add-alongside idea and the browser cost** - `d1f60e7` (docs)

**Plan metadata:** the `docs(33-07): complete ...` commit that adds this file.

## Pins and their red

- Replaced: `window.addEventListener('hashchange', () => { readHash(); update(); });` -> `window.addEventListener('hashchange', followHash);`. Added: `new URLSearchParams(hash.slice(1)).getAll('part')`, `if (which === part) { markPart(); readHash(); update(); return; }`, `else if (await buildForm(which)) { readHash(); update(); }`, `if (refused) { showMessages([refused]); return; }`, and an assertion that no `await` precedes the same-part line in `followHash`. The history comment in the pin test records the swap.
- Red against 33-06's app.js (`investigation/33-07-red-pins.log`): `E           AssertionError: window.addEventListener('hashchange', followHash);`, `1 failed, 1 passed`. Row recorded under `### Seen red once (Phase 33)` in `bench/RESULTS.md`. The three added tokens and the await assertion sit after the first token in the tuple, so they were red by being absent too, but only the first failure line is recorded; each is green now.
- The browser steps were red first against 33-06's page (`investigation/33-07-red-browser.log`): `Timeout 45000ms exceeded while waiting for event "request"`, `step: shaft link round trip` (the old page loads the gear form for a `#part=shaft` link and never sends `/api/shaft/info`).

## Verification

- Browser test, last line: `3 passed in 40.94s` (`make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`, log `33-07-browser.log`). The plan's fails_when says `1 passed`; the file holds three tests (as 33-06 recorded), so the line reads `3 passed` and nothing failed. Step timers: `part switch` 0.73 s, `shaft link round trip` 5.63 s, `bad part refused` 3.33 s. 1-minute load 14.63 at the start of that run and 10.52 after; the first green run read 43.65 s call time at load 11.47. Recorded in `bench/RESULTS.md` `### The page with a part switch (33-07)` against 33-03's 29.14 s; no speed claim made from the pair.
- Pins: `tests/test_api.py -k "shareable or every_key"` 2 passed; `tests/test_browser_pins.py` green inside `make verify`.
- `make gear.unchanged`: byte-equal to v0.6 (`/api/schema` 8723 bytes). `make no-fake-done`: rc 0. mypy `--strict` on `tests/test_browser.py` and ruff on `tests/`: clean.
- `make verify.fast`: 2308 passed in 21.51 s, `real 23.18` (under the 30 s bar), 1-minute load 22.60 at the start.
- `make verify` (the gate): `2773 passed in 249.66s (0:04:09)`, `real 251.17`, rc 0; 1-minute load 32.66 before and 18.59 after (another heavy process was running on the host, so this wall time is not compared with 33-06's 280.47 s).
- Acceptance criteria re-run: golden sweep diff count 0; `getAll('part')` 1 and `Unknown part` 1 in `app.js`; the new `hashchange` token 1 in `app.js` and 1 in `tests/test_api.py`, the old one 0; `^| 33-07 | shareable-link pins` 1; `### The page with a part switch (33-07)` 1; L49 numstat `39 0`; both L49 bold leads 1; the idea in INDEX 1.

## Decisions Made

- `part` starts as `''`, so the bootstrap always builds and a bad part at a fresh load still builds the gear form (with `'gear'` as the start value the same-part branch would have skipped the first build).
- `refuseLink` rebuilds the gear form every time instead of resetting a gear that already shows. One extra `/api/schema` fetch per bad link (not a build request, and the request count in the step excludes it by path) buys a single place that clears rows, downloads, scene, in-flight request and debounce.
- `followHash` bumps `formSeq` first, so a slower build started by an earlier link or click returns false and cannot land under the newest link.

## Deviations from Plan

None - plan executed exactly as written. Differences of wording only: the plan says `refuseLink` "awaits the gear form if another part is showing"; it awaits it always (see Decisions Made), and the same-part pin line includes `markPart();` and `return;` (the plan describes the line as `readHash(); update();` with no `await` before it, which the pin test asserts).

## Issues Encountered

- mypy `--strict` on the long test function: two local names collided with earlier ones (`recovered`, `refusal` possibly undefined after the loop); renamed (`after_bad`, a `_bad_part_text` helper). No behavior change.
- The host was under load from other processes for the whole plan (1-minute load 10 to 32), so every timing in this plan carries that spread.

## Known Stubs

None.

## Threat Flags

None. The echoed `part` value reaches the DOM only through `JSON.stringify` and `textContent` (T-33-23); `innerHTML` and `insertAdjacentHTML` count 0 and the `writes_a_field_shut` guard is green (T-33-23 mitigated). `partOf` compares literals and `PARTS` is indexed only by `'gear'`, a radio's value, or the fixed answers of `partOf` (T-33-15). `update()` returns before any request while `refused` is set and the `bad part refused` step counts requests across six links, an edit and Reset (T-33-24).

## Debt and ideas filed

- Idea filed: `docs/ideas/2026-10-27-gear-result-rows-from-the-schema.md` (row added to `docs/ideas/INDEX.md`). No tech-debt item filed.

## Next Phase Readiness

- 33-08 can compare the web with the API over the parity set through `part=shaft` links; the page's shaft links, odd-z null row and server-named download are proven here.
- `refuse()` and `gearQuery()` are untouched for 33-09's diff against `6800769`.

## Self-Check: PASSED

- Created and modified files exist (`app.js`, `test_api.py`, `test_browser.py`, `RESULTS.md`, `decision_log.md`, `web-ui.md`, the idea and `INDEX.md`, the three logs).
- Commits `c728f9a` and `d1f60e7` are ancestors of HEAD.
- Acceptance criteria and plan-level verification re-run (see Verification).
