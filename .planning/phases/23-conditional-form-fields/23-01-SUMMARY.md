---
phase: 23-conditional-form-fields
plan: 01
subsystem: ui
tags: [pydantic, json-schema, enabled_when, vanilla-js, playwright, decision-log]

requires:
  - phase: 21-browser-test-of-the-viewer
    provides: "the headless-shell scenario, step(), serve_stl_from, the golden sweep (L39)"
  - phase: 22-download-name-carries-the-root
    provides: "the one-commit-per-plan pattern and L40's decision-log shape"
provides:
  - "when() and _extra() in params.py: the one builder of json_schema_extra, enabled_when on hub_d"
  - "generic applyRelations()/holds()/need()/effective() in app.js: a field the model says is inert is dimmed with its reason, never disabled, hidden or cleared"
  - "the app.js pins in tests/test_api.py tightened under L41"
  - "tests/browser_session.py expected_inactive() (the Python evaluator) and eval_inactive(); the browser step `inert fields`"
  - "docs/architecture/decision_log.md L41"
affects: [23-02, 23-03, 23-04, 24-bore-selector]

actuals:
  tokens: 7946
  tasks: 2
  commits: 1
plan_head_before: c61fea924511f751185eacea7bc389fc161b6ac0
plan_head_after: e09f834ac4bef35b26371ca09db2b710ff5e1a66
commits: 1

tech-stack:
  added: []
  patterns:
    - "A field relation is schema metadata: a bare list of {field, op, value} conditions under one key, built by when(), emitted through _extra()"
    - "Two evaluators that share no code (JS holds() and the Python expected_inactive()) agreeing over every state is the proof"
    - "A pin changes only to a stricter one, under an Lxx, in the same commit as the code it pins"

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
  - "L41 supersedes 08 D-09 and keeps L02: the relation lives on the model and reaches the form through the schema, so app.js names no GearParams field outside DIMS"
  - "enabled_when is one key holding a bare list of {field, op, value}; the list is the AND; op is eq or gt only (D-01, D-02); costly to reverse"
  - "holds() is a switch with a throwing default, never a table: a row-shaped table is harvested as a DIMS key and an object lookup resolves constructor"
  - "applyRelations() evaluates every condition (rels.map(holds).includes(false)) so an unknown op anywhere throws"
  - "An inert field is dimmed through existing custom properties only; no opacity, pointer-events or visibility, so the 422 mark on the refused keyway pair stays the stronger"

patterns-established:
  - "One builder (_extra) for json_schema_extra on both number fields and Literal fields, so a relation cannot be dropped on one construction path"
  - "The browser step derives its expected dimmed set from /api/schema, never a literal"

requirements-completed: [REQ-enabled-when-metadata, REQ-dim-and-editable, REQ-form-walk-proves-relations]

coverage:
  - id: D1
    description: "/api/schema carries hub_d's relation exactly as the model wrote it; root_shape and recess_sides build their extra through _extra() and still read the same; GearParams keeps its 31 fields unchanged"
    requirement: REQ-enabled-when-metadata
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_schema_drives_the_form"
        status: pass
      - kind: other
        ref: "the Task 1 ast/schema command: params.py: 31 fields unchanged, one relation on hub_d, three Field calls through _extra"
        status: pass
    human_judgment: false
  - id: D2
    description: "A shared link #spoke_count=0&hub_d=40 loads hub_d dimmed with the reason 'Needs Spoke arms above 0', visible, editable, holding 40 and sent; a real keystroke reaches the request; the gate going live un-dims it before the debounce; Reset restores the evaluator's set"
    requirement: REQ-dim-and-editable
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step inert fields)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The app.js pins in tests/test_api.py are tightened under L41 (the fields.set token, call-site and evaluator tokens, the DIMS-only harvest, the no disabled/hidden/markup write assertion); none deleted or allow-listed"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_every_key_the_ui_reads_is_a_derived_dimensions_field"
        status: pass
    human_judgment: false
  - id: D4
    description: "The dim looks right: muted text, dashed control border, reason as a full row in the foreground colour, legible in both themes, and the accent outline still the stronger mark on an invalid field"
    verification: []
    human_judgment: true
    rationale: "Visual adequacy in the two themes is not asserted by any test; the browser step proves the rules exist and the field stays editable, not that the dim reads well"
  - id: D5
    description: "L41 records the decision (supersedes 08 D-09, keeps L02) and the feature, its pins and L41 land in one commit with both regression files unmoved"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: other
        ref: "the Task 2 verify commands: one commit, the ten files all modified, L41 last heading citing 40 items, git diff --exit-code on the regression files"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-10-11
status: complete
---

# Phase 23 Plan 01: Conditional form fields tracer Summary

**One relation (`hub_d` under `spoke_count gt 0`) carried from `GearParams` through `/api/schema` into generic `applyRelations()` code, seen dimmed, still editable and still sent in a real browser, with the app.js pins tightened and L41 recording the decision, in one commit.**

## Performance

- **Duration:** 9 min (573 s wall; `make verify` alone was 234 s of it)
- **Started:** 2026-10-11T12:11:14Z
- **Completed:** 2026-10-11T12:20:47Z
- **Tasks:** 2 (Task 1 tracer, Task 2 auto; one commit for both, per PD-02)
- **Files modified:** 10

BASE: `c61fea9` (the commit's parent). Commit: `e09f834`.

## Accomplishments

- `params.py` gains `when()` and `_extra()`; `_f()` takes `enabled_when`; `root_shape` and `recess_sides` build their extra through `_extra()` with an unchanged emitted schema. `hub_d` alone is declared. The 31 `GearParams` fields keep their names, annotations, defaults and bounds.
- `app.js` gains `effective()`, `holds()`, `need()` and `applyRelations()`, a `reason` span per field and exactly three call sites (the end of `readHash()`, the form `input` listener before `scheduleUpdate`, `#reset` before `update()`). `gearQuery()`, the `hashchange` line, `DIMS` and the `if (prop.enum)` branch are byte-identical to BASE.
- `style.css` dims through `--muted` and a dashed control border only; the reason is a full row shown while filled.
- `tests/test_api.py`: the `fields.set` token rewritten, 11 tokens added, the `['word',` harvest restricted to `DIMS`, a static no-disabled/hidden/markup assertion with a non-vacuity line, one relation assertion in `test_schema_drives_the_form`. The `gearQuery()` pin in the root-shape test is untouched.
- `tests/browser_session.py`: `expected_inactive()` (the second evaluator, names no field), `eval_inactive()`, and `eval_pairs` takes an `expression`. `tests/test_browser.py`: the `inert fields` step.
- L41 appended to the decision log (supersedes 08 D-09, keeps L02); `web-ui.md`, `http-api.md` and `README.md` gain the relation sentence.

## Task Commits

PD-02: Task 1 does not commit; Task 2 commits both.

1. **Tasks 1 and 2: tracer, dim, pins, L41, docs** - `e09f834` (feat). The subject is `feat(23): an inert field is dimmed and stays a field -- enabled_when on the model, log L41`.

**Plan metadata:** the `docs(23-01)` commit that follows this SUMMARY.

## One-off parity (Task 1 step 4)

Run before `hub_d` was declared, with the default `spoke_count` 0:

```
0.05 ['warnings'] ['No spoke arms with spoke_count 0: hub_d (0.05 mm) is ignored.']
400 ['warnings'] ['No spoke arms with spoke_count 0: hub_d (400 mm) is ignored.']
```

At both bounds only `warnings` changes, to one sentence naming `hub_d`: `calc` backs the relation.

## Seen red

Each first failure line, with the command that produced it.

1. `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'schema_drives_the_form or openapi_documents or every_key_the_ui_reads or shareable_link_round_trips or root_shape_link'"` against the unchanged `params.py` and `app.js`: `2 failed, 3 passed`.
   - `FAILED tests/test_api.py::test_schema_drives_the_form - KeyError: 'enabled_when'`
   - `FAILED tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code` with `AssertionError: fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason });`
2. `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` against the unchanged code (`investigation/23-01-browser-red.log`): `1 failed`, `AssertionError: inert fields: the link's own field is not expected dimmed`, `assert 'hub_d' in {}`, note `step: inert fields`. (The message was shortened to "is not dimmed" afterwards to satisfy ruff E501.)
3. The input path (step 8): the listener put back to `form.addEventListener('input', scheduleUpdate);`, same browser command (`investigation/23-01-browser-input-red.log`): `1 failed`, `AssertionError: inert fields: hub_d still dimmed right after spoke_count's input event, so the input listener did not re-evaluate before scheduleUpdate`, `assert not True`, note `step: inert fields`. Reverted by editing the line back; a `cmp` against a copy saved before the break read identical, and the token pin passed again (`5 passed`).

## Green readings

Host: Apple M2 Max, 12 CPUs, macOS 27.0.1, Python 3.12.13, playwright 1.63.0, Chrome Headless Shell. `uptime` at the readings: load averages 3.83 4.44 3.06 (green), 5.00 4.59 3.19, 5.25 4.70 3.29 (styled).

| Run | `step inert fields` | `step golden sweep` | result |
|---|---|---|---|
| `23-01-browser-green.log` (first) | 1.15 s | 0.26 s | 1 passed in 10.17 s |
| `23-01-browser-green.log` (after lint fixes, kept) | 1.13 s | 0.27 s | 1 passed in 7.96 s |
| `23-01-browser-styled.log` | 1.13 s | 0.37 s | 1 passed in 9.71 s |

Every run printed `inert fields: hub_d: Needs Spoke arms above 0`, and it is the only dimmed field under this link and today's one declared relation.

## make verify

`make verify` exit 0: `1238 passed in 234.12s (0:03:54)`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`, `params.py` 100.00 %. Log: `investigation/23-01-verify.log`. The commit hook ran `make verify.fast` and passed, twice (see Issues).

## Kept logs

All under `.planning/phases/23-conditional-form-fields/investigation/`, untracked until 23-04 (PD-11): `23-01-browser-red.log`, `23-01-browser-green.log`, `23-01-browser-input-red.log`, `23-01-browser-styled.log`, `23-01-verify.log`.

## Decisions Made

L41 (see the decision log) and the plan's PD-01..PD-14 stand as written. One implementation choice beyond the plan text: `eval_pairs` takes its expression as a keyword with a module constant default, and `eval_inactive` reuses its narrowing, as PD-03 asked.

## Deviations from Plan

None - plan executed exactly as written.

Two small adjustments that are not deviations from the plan's behaviour: ruff E501 and PT018 on the new test code were fixed in place (split assertions, shortened two messages, a comment moved above its line), and the `inert fields` comment cites `23-RESEARCH Pitfall 8`.

## Issues Encountered

- The first commit (`d3d0078`) omitted the Co-Authored-By trailer. It was unpushed, so the message was amended (`e09f834`); the tree is identical. The commit hook, `make verify.fast`, therefore ran twice and passed both times. The "exactly one commit carries the subject" check reads 1.
- `git status` still shows `.planning/STATE.md`, `.planning/state.json` and `.planning/milestone.lock` as the orchestrator's bookkeeping (PD-13); the `docs(23-01)` commit below stages STATE.md through the state verbs.

## Debt and ideas filed

None in this plan. 23-02 files PD-12's two (`docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md` and `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`).

## Known Stubs

None.

## Threat Flags

None. The reason is written with `textContent` only and a static assertion forbids any markup write in `app.js` (T-23-01); no new endpoint, auth path or file access.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 23-02: the permanent proof module (`tests/test_relations.py`), red against the one-relation model, then the other ten relations behind it, then the two filings. `expected_inactive()` reads the schema, so the browser step's expected set grows from one dimmed field to seven with no test edit when 23-02 declares the rest (PD-03).

## Self-Check: PASSED

- Files: all ten modified paths exist; `git show --name-status` on `e09f834` lists exactly them, all `M`.
- Commit `e09f834` is an ancestor of HEAD and the only commit since BASE `c61fea9`.
- `make verify` exit 0 with `1238 passed`; both regression files and `calc.py`, `model.py`, `pool.py`, `app.py`, `cli.py` show an empty diff across the commit.

---
*Phase: 23-conditional-form-fields*
*Completed: 2026-10-11*
