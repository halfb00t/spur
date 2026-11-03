---
phase: 33-interfaces-and-parity
plan: 06
subsystem: ui
tags: [vanilla-js, three.js, playwright, part-switch, schema-driven-form]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-04 shaft API (/api/shaft/schema with dims, /info, /model.{stl,step}); 33-01 decision C1 (refuse() and gearQuery() stay byte-identical)"
provides:
  - "A Gear | Shaft radio switch outside the form, native keyboard switching"
  - "PARTS descriptor, buildForm(which), switchTo(which), clearScene(), the text-input branch and the schema-row renderer in app.js"
  - "Per-part page texts and hints, the mate box hidden by CSS on body[data-part]"
  - "Browser step 'part switch'; path-aware no_foreign_key; _shaft_stl_requests"
affects: [33-07, 33-08, 33-09]

actuals:
  tokens: 4449   # chars/4 over the added lines of src/, tests/ and bench/ (logs excluded)
  tasks: 2
  commits: 2
plan_head_before: c160c82c0142fb7dfeea0c14d8a652a08b37818f
plan_head_after: 13884db0f3e9d49c854a914663f4610f22acd3ec

tech-stack:
  added: []
  patterns:
    - "One descriptor (PARTS) holds only routes and texts; fields, defaults and rows come from the part's own schema"
    - "A build counter (formSeq) so an overtaken schema fetch returns false and nothing runs after it"
    - "Hiding is CSS on body[data-part], never a script write (writes_a_field_shut guard)"

key-files:
  created:
    - .planning/phases/33-interfaces-and-parity/investigation/33-06-red-pins.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-06-red-browser.log
  modified:
    - src/spur/static/app.js
    - src/spur/static/index.html
    - src/spur/static/style.css
    - tests/test_api.py
    - tests/test_browser.py
    - bench/RESULTS.md

key-decisions:
  - "switchTo loads the new part's defaults into its fields itself (not through readHash), because readHash would read the other part's hash; the hashchange listener and readHash stay as they were for 33-07"
  - "update() keeps the pinned `const mate = ...` line and gates the send with `mate && P.mate`, so the gear's token is unchanged and the shaft never sends or tags a mate"
  - "The gear's PARTS texts equal index.html's static texts, so the gear page reads exactly as before"

patterns-established:
  - "Pins for new generic paths are added beside the old ones; none removed (L49 sentence in the pin test's history comment)"
  - "no_foreign_key splits recorded requests by path and checks a shaft hash (first pair part=shaft) against the shaft properties"

requirements-completed: [REQ-shaft-web]

coverage:
  - id: D1
    description: "Gear | Shaft radio group above the form, outside #params, switchable by ArrowLeft/ArrowRight"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step part switch)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Shaft form from /api/shaft/schema at defaults (fit a text box), preview from the shaft STL route, rows from schema dims with the designation row, downloads on api/shaft/model.*, hash #part=shaft; Gear restores 31 fields, empty hash, gear rows"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step part switch)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Title, sub line, canvas aria-label, fit tooltip, mate box and hints follow the part by CSS on body[data-part]"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step part switch)"
        status: pass
    human_judgment: true
    rationale: "The structure is asserted, but whether the shaft texts and the radio row read well is a visual judgment"
  - id: D4
    description: "Pins hold the new generic paths beside the old ones, seen red first; ShaftParams names guarded; const DIMS = [ appears once"
    requirement: REQ-shaft-web
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_every_key_the_ui_reads_is_a_derived_dimensions_field"
        status: pass
    human_judgment: false

duration: 17min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 06: The Gear | Shaft switch Summary

**A Gear | Shaft radio switch builds each part's form, preview, rows and downloads from its own routes through one PARTS descriptor, with the page's texts and mate box following the part and the gear page, its pins and its 44 golden queries untouched.**

## Performance

- **Duration:** 17 min
- **Started:** 2026-10-27T17:05:00Z
- **Completed:** 2026-10-27T17:22:00Z
- **Tasks:** 2
- **Files modified:** 6 (plus two red logs)

## Accomplishments

- `fieldset.part-switch` sits above `#params` inside `<aside>`; the radios are not fields, so `form#params [name]` counts schema fields only and `fields.set(` stays 1.
- `PARTS` (`schema`, `info`, `model`, `tag`, `noun`, `mate`, `title`, `sub`, `aria`, `fitTitle`) is indexed only by a radio's literal value or by `'gear'` in the bootstrap. `buildForm(which)` bumps `formSeq`, returns `false` if overtaken, then clears the form, `fields`, `defaults`, `selectors`, `stash`, `rejected`, the mate box, the debounce, any in-flight request and `seq`, the rows, messages, downloads and the scene (`clearScene()`).
- `fit` renders as a text box (schema type `string`); result rows come from the schema's `dims` in order, a number as `fmt(v)` plus its unit when it has one, a string as itself. The shaft page shows `W 25x1.25x18x8f` in the designation row.
- `update()` and `setDownloads()` read the descriptor; the hash is `[P.tag, infoQ].filter(Boolean).join('&')`, so the shaft hash is `#part=shaft` and the gear's stays empty at defaults. `refuse()` and `gearQuery()` are byte-identical to `6800769` (checked by extracting both functions and comparing).
- Browser step `part switch`: Shaft click to 8 fields, `fit` text, hash `part=shaft`, rows equal to the schema's `dims` applied to `/api/shaft/info` (labels and value texts), downloads on `api/shaft/model.{stl,step}`, `data-triangles` equal to the shaft STL header; then ArrowLeft back to Gear with 31 fields at defaults, an empty hash and the fresh-load rows. `no_foreign_key` is path-aware.

## Task Commits

1. **Task 1: Tracer: click Shaft, the shaft form, preview, rows and downloads come from the shaft routes; click Gear, the gear comes back** - `69a2431` (feat)
2. **Task 2: The page reads as the part it shows** - `13884db` (feat)

**Plan metadata:** the `docs(33-06): complete ...` commit that adds this file.

## Pins and their red

- Pin tokens added, none removed: the tagged hash builder, `${P.info}?`, `${P.model}.stl?`, `${P.model}.${kind}`, `fields.clear();`, `stash.clear(); rejected.clear();`, `selectors.length = 0;`, `dims = schema.dims ?? null;`, `input.type = 'text';` and the radio `change` listener. The `hashchange` token is unchanged (33-07 swaps it). The quoted-name and `.field` guard now covers `[*GearParams.model_fields, *ShaftParams.model_fields]`; `source.count("const DIMS = [") == 1` is asserted.
- Red against the pre-change app.js (`33-06-red-pins.log`): `E AssertionError: const hash = [P.tag, infoQ.toString()].filter(Boolean).join('&');`, `1 failed, 1 passed`. Row recorded under `### Seen red once (Phase 33)` in `bench/RESULTS.md`.
- The browser step was red first against the unchanged page (`33-06-red-browser.log`: `Locator.click: Timeout 30000ms exceeded ... waiting for locator("input[name=part][value=shaft]")`), and again red at Task 2's text assertions (`Locator expected to have attribute 'shaft'` on `body[data-part]`) before the texts landed.

## Verification

- Browser test, last line: `3 passed in 33.70s` (`make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"`). The plan's fails_when text says `1 passed`; the file holds three tests (two no-browser ones from earlier phases), so the line reads `3 passed` and nothing failed.
- `make gear.unchanged`: byte-equal to v0.6 (`/api/schema` 8723 bytes). `make no-fake-done`: clean. `tests/test_browser_pins.py`: 15 passed. mypy on `tests/test_browser.py`: clean.
- `make verify.fast`: 2308 passed, real 15.60 s (1-minute load 11.03 at the start of the run, under the 30 s bar).
- `make verify` (the gate): `2773 passed in 280.47s`, wall 4:41.67, rc 0; 1-minute load 16.01 before and 12.22 after.

## Decisions Made

- `switchTo` writes the new part's defaults into its fields directly instead of calling `readHash()`, which would read the other part's hash. This is the D-13 "no value crosses a switch" path.
- `update()` keeps the pinned `const mate = ...` token and adds `mate && P.mate` at the send, so the gear's pin is untouched.
- The shaft hint and text strings are the planner's choices recorded in the plan.

## Deviations from Plan

None - plan executed exactly as written. The one difference from the plan's text is that the browser test's last line is `3 passed`, not `1 passed` (see Verification); no code change followed from it.

## Issues Encountered

- Variable-name collisions in the long test function made mypy `--strict` fail on the first version of the step (`got`, `shown` already typed earlier); the step's locals were renamed. No behavior change.

## Known Stubs

None.

## Threat Flags

None. Schema labels, row values and the per-part texts reach the DOM through `textContent` or `setAttribute` only (T-33-16); `innerHTML` and `insertAdjacentHTML` count 0. `buildForm(which)` clears every map and the mate box, `update()` sends the mate only when `P.mate`, and the path-aware recorder runs after every step (T-33-17).

## Debt and ideas filed

None filed.

## Next Phase Readiness

- 33-07 can add `part=shaft` link round trips, gear links without `part`, an unknown `part` refused and the `followHash` swap for the `hashchange` token. Until then a hash navigation on the shaft page runs `readHash()` against the shaft's fields and a `#part=shaft` link opened fresh still loads the gear form (the bootstrap builds `'gear'`).
- `refuse()` and `gearQuery()` are untouched for 33-09's diff against `6800769`.

## Self-Check: PASSED

- Created and modified files exist (`app.js`, `index.html`, `style.css`, `test_api.py`, `test_browser.py`, `RESULTS.md`, both red logs).
- Commits `69a2431` and `13884db` are ancestors of HEAD.
- Acceptance criteria re-run: `fields.set(` 1, `const DIMS = [` 1, `innerHTML|insertAdjacentHTML` 0, fieldset before `<form id="params"`, `hashchange` token 1 in each file, `data-for="shaft"` 1, `data-part` in style.css 4, gear `<title>` kept, `^| 33-06 | shareable-link pins` row 1.
