---
phase: 24-bore-shape-selector
plan: 01
subsystem: ui
tags: [json_schema_extra, selectors, vanilla-js, playwright, pydantic, enabled_when]

requires:
  - phase: 23-conditional-form-fields
    provides: "the when() condition vocabulary, holds()/effective()/need() in app.js, applyRelations() and its three call sites, the Python evaluator in the browser test (L41)"
provides:
  - "GearParams.model_config carries a model-level selectors list (one Bore shape selector, four options Round, D-flat, Hex, No bore) emitted at the top level of /api/schema and absent from /openapi.json"
  - "generic buildSelectors(), deriveSelectors(), pick() and pend() in app.js: a select derived from the flat fields, written back as the minimum flat fields, stashed and pending"
  - "the app.js pins in tests/test_api.py tightened under L42, none removed"
  - "the bore shape browser step, the selector tamper and twin selector in unknown relation op, and the schema-driven helpers expected_shown, state_links, expected_pick, negative_link"
  - "L42 in docs/architecture/decision_log.md"
affects: [24-02, 24-03, 24-04, 25]

actuals:
  tokens: 14700   # chars/4 over the added lines of the realized diff (58,758 chars), the plan's estimate scale; not a harness count
  tasks: 3
  commits: 1
plan_head_before: 07cba051d611969ee662c68233f2a8f7c083cf2a
plan_head_after: 470b78a814a955c6fb23e85dfffccce0c03de1fe

tech-stack:
  added: []
  patterns:
    - "A selector is a view of fields and never a field: own wrapper class, no name, no fields entry, derived at the three applyRelations() call sites"
    - "A pick plans first and writes after, so a pick that cannot be made true writes nothing"
    - "A pending pick stops the event's propagation; a writing pick lets it bubble to the form listener, which derives and schedules the one request"

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/static/app.js
    - src/spur/static/style.css
    - tests/test_api.py
    - tests/browser_session.py
    - tests/test_browser.py
    - docs/architecture/decision_log.md
    - docs/architecture/web-ui.md
    - docs/architecture/http-api.md
    - README.md

key-decisions:
  - "The selectors key reaches /api/schema only: FastAPI flattens InfoQuery and ModelQuery into parameters, so /openapi.json is byte-identical; the CONTEXT claim that it reaches the OpenAPI component schemas is corrected in L42 and pinned both ways in test_openapi_documents_the_typed_contracts"
  - "deriveSelectors() sits beside applyRelations() at its three call sites (tokens 4, 10 and 11 tightened), not inside applyRelations() (PD-03)"
  - "A select shows an option only when exactly one holds; none or two holding is a blank select, caught per selector (PD-06, D-18)"
  - "A pending pick calls stopPropagation; a writing pick lets the event bubble so the form listener sends the one debounced request (PD-04)"
  - "L42 appended: the carriage, the four states, derive/write/stash/pending, the keyway left to the 422, the pins, the proof, what is retired and restated"

patterns-established:
  - "Browser expectations for a selector come from /api/schema through expected_shown(), state_links() and expected_pick(); no option label, field name or threshold is a literal in the step"
  - "Each deliberate break is saved with cp, restored with cp, proved with cmp, and its first failure line recorded"

requirements-completed: [REQ-selector-schema-carried, REQ-selector-derives-and-writes-through]

coverage:
  - id: D1
    description: "/api/schema carries one top-level selectors key beside an unchanged properties; GearParams keeps its 31 fields; /openapi.json carries no selectors"
    requirement: "REQ-selector-schema-carried"
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_schema_drives_the_form"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_openapi_documents_the_typed_contracts"
        status: pass
    human_judgment: false
  - id: D2
    description: "Generic app.js code builds the Bore shape select first in the Bore fieldset from the schema, derives its option from the flat fields at the three applyRelations() call sites, and never writes on load"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bore shape: fresh load, row place, Reset, every state link, 0.0 form, negative link)"
        status: pass
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step golden sweep, unchanged queries)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A pick writes only the string 0 into the chosen option's false eq fields, restores a stashed string into a gt field, or stays pending and writes nothing"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bore shape: Round sends bore_flat=0, restore, pending, typed number, Reset clears the stash)"
        status: pass
    human_judgment: false
  - id: D4
    description: "An unreadable option or two holding options leaves the select blank and the part still builds"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step unknown relation op with the selector tamper and twin selector)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The app.js pins in tests/test_api.py are stricter than before and none is deleted or allow-listed"
    requirement: "REQ-selector-schema-carried"
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
    human_judgment: false
  - id: D6
    description: "The pending state reads as pending to a person in both themes (dashed control border and dimmed name), and the pending wording reads clearly"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (computed borderTopStyle dashed while pending, not dashed after a typed number)"
        status: pass
    human_judgment: true
    rationale: "The test asserts the computed style and the note text, not that the dimmed tone is legible in light and dark or that the wording is clear; that is a person's call"
  - id: D7
    description: "L42 records the decision in full and in L41's shape"
    verification:
      - kind: other
        ref: "the Task 3 verify script: L42 is the last ## L heading and cites 39 required items"
        status: pass
    human_judgment: true
    rationale: "Whether the entry argues the decision well is a judgment no script makes; the script checks only that the named items are present"

duration: 22min
completed: 2026-10-12
status: complete
---

# Phase 24 Plan 01: Bore-shape selector tracer Summary

**A model-level `selectors` list on `GearParams` becomes a Bore shape select built, derived and written back by generic `app.js` code: Round from the default part sends exactly `bore_flat=0`, Hex from the default part stays pending, and the four options, the pins and L42 land in one commit behind a green `make verify`.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-10-12T14:58:21Z
- **Completed:** 2026-10-12T15:20:32Z (the feature commit; the SUMMARY and state commits follow)
- **Tasks:** 3
- **Files modified:** 10 (no file created in the repository)

## Accomplishments

- The four D-02 options (Round, D-flat, Hex, No bore) are declared once on `GearParams.model_config` with `_option()` and `when()`, emitted as the one new top-level `selectors` key of `/api/schema`, and the 31 `GearParams` fields are byte-for-byte what they were (checked by an AST comparison against `HEAD`).
- Generic `buildSelectors()`, `deriveSelectors()`, `pick()` and `pend()` in a new `-- selectors (L42)` section build the select as the first row of the Bore fieldset, show the option whose conditions hold only when exactly one does, and write the minimum on a pick: the string `0`, a stashed string back, or nothing while the pick is pending.
- `deriveSelectors()` is called beside `applyRelations()` at exactly its three call sites and writes no field; a negative link, an unreadable option and a twin selector with two holding options each load a blank select and the part still builds.
- The browser proves it: a `bore shape` step (fresh Hex load, the row's place, Reset, a writing pick, the restore, the pending pick, a typed number, Reset clearing the stash, every state link, the `0.0` form, the negative link) and the selector tamper plus twin selector in `unknown relation op`, with every expectation read from `/api/schema`.
- Four deliberate breaks were each seen red once and restored.
- The `app.js` pins in `tests/test_api.py` are stricter (three tokens tightened, fourteen added, a `fields.set(` count, a one-value-write pin on the new section) and none was removed or allow-listed.
- L42 is the last entry of the decision log, with the web-ui, http-api and README sentences.

## Task Commits

The plan commits once, at Task 3 (PD-02): Tasks 1 and 2 build and verify and do not commit, so no task has a commit of its own.

1. **Tasks 1, 2 and 3 together** - `470b78a` (feat): `feat(24): a bore shape is picked in the form and written back as flat fields -- selectors on the model, log L42`

BASE was `07cba05`, and the commit's parent is `07cba05`. `git rev-list --count 07cba05..HEAD` read 1 when this file was written.

**Plan metadata:** the SUMMARY commit and the STATE/ROADMAP/REQUIREMENTS commit follow this file.

## Files Created/Modified

- `src/spur/params.py` - `_option()`, `_BORE_SHAPE`, the model-level `selectors` list in `model_config`; docstring and Bore comment sentences
- `src/spur/static/app.js` - the `selectors (L42)` section (`stash`, `selectors`, `buildSelectors`, `deriveSelectors`, `pick`, `pend`), the `buildSelectors(...)` call in `buildForm()`, `deriveSelectors();` at the three `applyRelations()` call sites, `stash.clear();` in Reset
- `src/spur/static/style.css` - `.selector` joins the `.field` grid, name, control, select and reason rules; `.selector.pending` dims the name and dashes the select
- `tests/test_api.py` - the pins tightened under L42, the selectors assertions in `test_schema_drives_the_form`, the selectors-in-`/api/schema`-not-in-`/openapi.json` assertions
- `tests/browser_session.py` - `_given()`, `SHOWN_OPTIONS`, `eval_shown()`, `expected_shown()`, `state_links()`, `Pick`, `expected_pick()`, `negative_link()` and the small narrowing helpers they share
- `tests/test_browser.py` - `_schema_selectors()`, the pick helpers, the `bore shape` step, the selector tamper and twin in `unknown relation op`
- `docs/architecture/decision_log.md` - `## L42`
- `docs/architecture/web-ui.md`, `docs/architecture/http-api.md`, `README.md` - the selector sentences

## Decisions Made

- `/api/schema` carries the key and `/openapi.json` does not, so L42 corrects the CONTEXT text and the pin asserts both halves (24-RESEARCH Finding 1).
- `deriveSelectors()` beside `applyRelations()` at the three sites, with tokens 4, 10 and 11 rewritten (PD-03), kept the relations section byte-identical.
- A pending pick calls `stopPropagation`; a writing pick lets `input` bubble so the form listener's derive lands the select on the chosen option and one debounced request is sent (PD-04). Each half was seen red.
- Exactly one holding option shows; none or two is blank (PD-06), caught per selector.

## One-off grid (Task 1 step 4, before the options were declared)

`.planning/phases/24-bore-shape-selector/investigation/24-01-grid-oneoff.log`:

```
grid: 8 of 8 cells hold exactly one option; defaults ['D-flat']; 27 cells: 13 hold none, 13 of them with a negative, 0 hold two
```

This equals the planning measurement, so PD-14's stop did not fire.

## Seen red

Every red below was run through `make test` (so the headless shell path is the project's own). Kept logs are under `.planning/phases/24-bore-shape-selector/investigation/`, untracked until 24-04 commits them.

**Pins against the unchanged `params.py` and `app.js`** (Task 1 step 3), `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'schema_drives_the_form or openapi_documents or every_key_the_ui_reads or shareable_link_round_trips or root_shape_link'"`, `24-01-api-red.log`, `3 failed, 2 passed in 4.39s`:

1. `test_schema_drives_the_form` - `KeyError: 'selectors'`
2. `test_openapi_documents_the_typed_contracts` - `AssertionError: L42: /api/schema lost its selectors`
3. `test_the_shareable_link_round_trips_every_field_through_generic_code` - `AssertionError: mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }`

**Browser with the model carrying the key and `app.js` unchanged** (Task 1 step 6), `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`, `24-01-browser-red.log`, `1 failed, 1 passed in 7.45s`: `AssertionError: bore shape, #bore_hex=0.05: the page shows ()` (`assert () == ('Hex',)`), note `step: bore shape`.

**Four deliberate breaks** (Task 2 step 5), same command, `app.js` saved with `cp` first, restored with `cp` after each and proved with `cmp` (silent), the saved copy deleted after the fourth:

| Break | Log | Result | First failure line | Note |
|---|---|---|---|---|
| a. the `event.stopPropagation();` line deleted from `pend()` | `24-01-stop-red.log` | 1 failed, 1 passed in 9.61 s | `AssertionError: bore shape, pending Hex: the select snapped back to ('D-flat',)` | `step: bore shape` |
| b. `stash.has(field) &&` replaced by `false &&` in `pick()` | `24-01-restore-red.log` | 1 failed, 1 passed in 8.47 s | `AssertionError: bore shape, #bore_flat=0 + D-flat: the pick was left pending` | `step: bore shape` |
| c. the `try`/`catch` removed from `deriveSelectors()` | `24-01-catch-red.log` | 1 failed, 1 passed in 14.66 s | `Locator expected to have JS Property '-1'`, actual value 0, on `<select id="selector-0">` | `step: unknown relation op` |
| d. `s.select.selectedIndex = i === hits.lastIndexOf(true) ? i : -1;` replaced by `= i;` (first match wins) | `24-01-twin-red.log` | 1 failed, 1 passed | `AssertionError: unknown relation op: two holding options must leave the select blank`, expected `-1`, actual 0, on `<select id="selector-1">` | `step: unknown relation op` |

After the last restore the Task 2 verify confirmed `event.stopPropagation();`, `stash.has(field) && Number(` and the exactly-one line each occur once in `app.js`.

## Green readings

Host: Apple M2 Max, 12 CPUs, macOS 27.0.1, Python 3.12.13, playwright 1.63.0, Chrome Headless Shell 153.0.8010.12.

Task 1 (`24-01-browser-green.log`, `uptime` 21:03, load averages 9.65 7.50 5.90): `step golden sweep: 0.52 s`, `step inert fields: 1.51 s`, `bore shape: loaded #bore_hex=0.05: shows 'Hex'`, `bore shape: # + Round -> sent 'bore_flat=0'`, `step bore shape: 0.81 s`, `step unknown relation op: 5.19 s`, `2 passed in 15.94s`.

Task 2 (`24-01-browser-picks.log`, `uptime` 21:06, load averages 3.28 5.76 5.49): `step golden sweep: 0.37 s`, `step inert fields: 1.35 s`, `step bore shape: 1.86 s`, `step unknown relation op: 4.09 s`, `2 passed in 14.01s`, and these lines:

```
bore shape: loaded #bore_hex=0.05: shows 'Hex'
bore shape: # + Round -> sent 'bore_flat=0'
bore shape: #bore_flat=0 + D-flat -> sent ''
bore shape: bore_flat back to '8' from the stash
bore shape: # + Hex -> pending: bore_hex: Hex needs Hex bore A/F above 0
bore shape: typed bore_hex=0.05: shows 'Hex'
bore shape: # + Round -> sent 'bore_flat=0'
bore shape: #bore_flat=0 + D-flat -> pending: bore_flat: D-flat needs D-flat above 0
bore shape: loaded #bore_flat=0: shows 'Round'
bore shape: loaded #bore_hex=0.05: shows 'Hex'
bore shape: loaded #bore_d=0: shows 'No bore'
bore shape: loaded #bore_flat=0.0: shows 'Round'
bore shape: loaded #bore_hex=-0.05: shows ''
unknown relation op: bore_d unreadable, the bore-shape select blank, two holding options blank, the form still builds the part
```

The golden sweep still compared every one of the 44 fixture links to `tests/regression/golden_requests.json` and passed with that file unmoved. The step costs 0.81 to 1.86 s on this host; 24-04 prices it properly.

OpenAPI claim, read once before the commit: `openapi: no selectors`.

## The gate

`make verify`, 600 s tool timeout, `24-01-verify.log`:

- First run: `1 failed, 1294 passed in 296.91s (0:04:56)`, host load 15.6 at the start. The failure was `tests/test_pool.py::test_health_reports_pool_state` with an `ExceptionGroup` of five `multiprocessing.resource_tracker.ReentrantCallError` warnings, which is the signature of the open debt `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`. Kept as `24-01-red-1.log`. No file this plan touches is in that test's path.
- One re-run on the identical tree (the plan allows exactly one): `1295 passed in 272.91s (0:04:32)`, `make verify exit 0`.
- Coverage: `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`. `params.py` reads 100.00%.
- The commit hook ran `make verify.fast` and passed (twice, see Deviations).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A `# noqa: E501` on one pin token**
- **Found during:** Task 1 step 1b (the pins).
- **Issue:** The plan requires token 10 to be one exact string a `grep -F` finds on one line of `tests/test_api.py`. As a tuple item it is 108 columns, and ruff's limit is 100. Splitting the literal across two lines would have left no single line to grep.
- **Fix:** One `# noqa: E501`, by code, with a comment line above it saying why. The repository already carries the same suppression on two long test names in `tests/test_bench.py`; `SELECT_BORDER` in `tests/test_browser.py` carries one for the same reason (one JS expression kept on one line).
- **Files modified:** `tests/test_api.py`, `tests/test_browser.py`
- **Verification:** `make lint` passes; the acceptance grep for the exact token finds it once in `tests/test_api.py`.
- **Committed in:** `470b78a`

**2. [Rule 2 - Missing critical functionality] `buildSelectors()` throws a named error when a selector's group has no fieldset**
- **Found during:** Task 1 step 7.
- **Issue:** `groups.get(group)` is `undefined` for a group no field has, and `fs.insertBefore` would then fail with an unreadable `TypeError` inside `buildForm()`, which the page reports as a schema load failure.
- **Fix:** `if (!fs) throw new Error(...)` naming the selector and the group. The page's existing catch shows it in the messages strip, so a mistake in the metadata is loud and says which selector.
- **Files modified:** `src/spur/static/app.js`
- **Verification:** reading only; the shipped schema's group exists, so no test reaches this line, and no pin counts it. 24-02's walk checks that a selector's group is a real one on the model.
- **Committed in:** `470b78a`

**3. [Plan wording followed over a note] The commit trailer**
- **Found during:** Task 3 commit.
- **Issue:** The dispatch note asked for the trailer `Co-Authored-By: Claude Fable 5.1`; the plan says to end with "the attribution line the session reminder gives", and the session reminder gives `Co-Authored-By: Claude Sonnet 5.5`, which is the model that did this work. The first commit (`871e460`) carried the dispatch note's name.
- **Fix:** Amended the just-created, unpushed commit to the session reminder's trailer (`470b78a`); the hook ran again and passed. Nothing else in the commit changed.
- **Files modified:** none (message only)
- **Committed in:** `470b78a`

**4. [Added structure, not a deviation of behaviour] Helpers beyond the artifact list**
- `tests/browser_session.py` also holds `negative_link()` and the narrowing helpers `_options()`, `_property_number()` and `_box_number()`; `tests/test_browser.py` holds `_pick()`, `_writing_pick()`, `_pending_pick()` and three constants. The plan's step text described these as inline code; they are module-level functions so the step reads as the cases it proves and Task 2's cases reuse them. No behaviour differs from the plan's description.

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical), 1 attribution correction, 1 structural note.
**Impact on plan:** None changes what the select does or what any pin asserts. The suppression is by code with a stated reason; the thrown error only fires on a malformed schema.

## Issues Encountered

- `make verify` read the known resource-tracker flake once at host load 15.6 and was green on the one allowed re-run on the identical tree. The debt file stays active; this is an occurrence for its log, not a new defect.
- The `evaluation-scope` resolver reports `no-matching-commits` for plan `24-01` because it matches commit subjects of the form `feat(24-01): ...`, and the plan mandates the subject `feat(24): ...`. The commit was verified by `git merge-base --is-ancestor 470b78a HEAD` and by the plan's own Task 3 verify (exactly one commit carries the subject, it holds exactly the ten files, all modified, and none of the kept-unedited files moved). Later phases that rely on that resolver should be told.

## Known Stubs

None. Every value the select shows or writes comes from the schema and the fields.

## Threat Flags

None. The only new surface is the selector's title and labels reaching the page, which is T-24-01 in the plan's register: they go through `textContent` and `new Option(label)` only, and `writes_a_field_shut` still finds no markup write anywhere in `app.js`.

## User Setup Required

None - no external service configuration required.

## Debt and ideas

No debt item and no idea was filed in this plan. The hex-bore warning that a selector-made Hex part carries, and the idea's retirement, are restated and retired by 24-03's last commit (L42 names both).

## Next Phase Readiness

- 24-02 can write `tests/test_selector.py` against the real model: the options, their order and the Hex condition are fixed by L42 and by `test_schema_drives_the_form`, and `expected_pick()` here is the browser-side mirror it must agree with in spirit.
- 24-03 can widen the browser proof: `Swept` and `sweep()` are untouched, `browser.new_page()` counts 7 sites, and the `bore shape` step is a single place to add the every-pick-from-every-state matrix and the keyed bore.
- Nothing is blocked. The kept logs sit untracked under `investigation/` until 24-04 commits them.

## Self-Check: PASSED

- No file was created in the repository; the ten modified files exist and are in `470b78a` (`git show --name-status` lists exactly the ten, all `M`).
- `git merge-base --is-ancestor 470b78a HEAD` found the commit; its parent is `07cba05`, the recorded BASE.
- The Task 3 verify script passed: one commit carries the subject, L42 is the last `## L` heading and cites 39 required items, `make verify exit 0` is in the kept log.
- All Task 1 and Task 2 acceptance greps and verify commands were re-run after the last change to `app.js` and passed (the four breaks restored with `cmp`, the saved copy deleted).
- `git diff --exit-code` on `tests/regression/pre_v0_2.json`, `tests/regression/golden_requests.json`, `src/spur/calc.py`, `model.py`, `pool.py`, `app.py` and `cli.py` is empty across the commit.

---
*Phase: 24-bore-shape-selector*
*Completed: 2026-10-12*
