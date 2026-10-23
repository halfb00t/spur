---
phase: 28-refuse-the-bad-link
plan: 02
subsystem: web-ui
tags: [app.js, dims-table, root_fillet, playwright, tech-debt, ideas]

requires:
  - phase: 28-refuse-the-bad-link
    provides: 28-01's app.js and tests/test_browser.py changes (the shared working tree), the Phase 28 section of bench/RESULTS.md
  - phase: 19-the-trochoid-in-the-part
    provides: root_form_d in the info document and the hob branch of derive()
provides:
  - the root_fillet row labelled by the root the server built ("Hob tip radius used" or "Root fillet used")
  - the stash comment saying what the stash holds, and the hand-edit invalidation filed as an idea
  - the form-build failure reading "Could not build the form: ..."
affects: [28-03, 28-04]

actuals:
  tokens: 6400
  tasks: 3
  commits: 3
plan_head_before: 359b6d5e7cbbb6f72b180e7791d325facd26a517
plan_head_after: 235e51d4c11ec1b91bc302243455b4324dd1224b

tech-stack:
  added: []
  patterns:
    - "A DIMS label as a function of the info document, keyed on a field the server sets only when it built the thing (root_form_d), not on the request"

key-files:
  created:
    - docs/ideas/2026-10-21-stash-entry-survives-a-hand-edit.md
    - .planning/phases/28-refuse-the-bad-link/investigation/28-02-red-label.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-02-green-label.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-02-red-wording.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-02-green-wording.log
  modified:
    - src/spur/static/app.js
    - tests/test_browser.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/ideas/INDEX.md
    - docs/tech_debt/resolved/2026-10-09-phase-19-review-info-findings-deferred.md

key-decisions:
  - "D-10: the root_fillet label keys on the loose d.root_form_d != null, so it follows the root the server built; a trochoid request that falls back to radial keeps 'Root fillet used'"
  - "D-14: the stash comment is reworded and the behavioural half of 24 IN-01 is filed as an idea; Codex's isolate-and-continue proposal for 24 IN-02 is not taken"

requirements-completed: [REQ-root-fillet-label-follows-root, REQ-info-findings-triaged]

coverage:
  - id: D1
    description: "The root_fillet row reads 'Hob tip radius used' while root_form_d is non-null and 'Root fillet used' otherwise, derived from the API body for the query the page sent, on both sides of the rb <= rf flip"
    requirement: "REQ-root-fillet-label-follows-root"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser (step `root_fillet label`)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The label change moves no part, number or request: the golden sweep stays green and tests/regression is unchanged against v0.5"
    requirement: "REQ-root-fillet-label-follows-root"
    verification:
      - kind: other
        ref: "git diff --exit-code v0.5 -- tests/regression/ exits 0; the golden sweep step passes in 28-02-green-label.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "24 IN-01 comment reworded (comment-only diff, one value write still in the selectors section) and its behavioural half filed as an idea; 24 IN-02 / CX-03 wording fixed with a step seen red"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser (step `form build error`)"
        status: pass
      - kind: unit
        ref: "tests/test_api.py -k shareable_link (selectors-section guard): 4 passed"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-10-21
status: complete
---

# Phase 28 Plan 02: Info-finding text fixes Summary

**The `root_fillet` dimension row now reads "Hob tip radius used" under a hob root and "Root fillet used" otherwise, keyed on the server's `root_form_d`; the stash comment is true; the form-build failure says "Could not build the form". Three text-only commits, two new browser steps each seen red first.**

## Performance

- **Duration:** about 20 min (no start time was recorded in-session; approximate)
- **Tasks:** 3 (Task 1 tracer + tdd, Task 2 auto, Task 3 auto + tdd)
- **Commits:** 3, measured from `359b6d5..HEAD`

## Accomplishments

- `app.js`: the `root_fillet` row in `DIMS` is a label function of the info document (`d.root_form_d != null`), in the shape of the `span` row, with a three-line comment; no field name enters `app.js` outside `DIMS`.
- `tests/test_browser.py`: constant `LABEL_LINKS`; step `root_fillet label`, which follows three links and derives the expected label from `/api/info`'s body for the query the page sent; step `form build error`, which serves a schema whose first selector names "No such group" and asserts the text and that no `/api/info` request is sent.
- The Phase 19 debt item is `Status: resolved` and moved to `resolved/` with its INDEX row in the label commit.
- The `stash` comment now says the map holds what the box held at the zeroing pick (typed value, page default or a value from an earlier link), that a hand edit does not update it, and points at the idea; the diff is comments only.
- The bootstrap catch reads `Could not build the form: ${err.message}`.

## The three labels read (`28-02-green-label.log`)

| Link | `root_form_d` | Label shown |
|---|---|---|
| `teeth=26&root_shape=trochoid` | non-null | Hob tip radius used |
| `teeth=27&root_shape=trochoid` | null (falls back to radial) | Root fillet used |
| `teeth=23` | null (nothing requested) | Root fillet used |

## Red evidence

| Step | First failure line | Log |
|---|---|---|
| `root_fillet label` (old row; `1 failed, 2 passed in 27.40s`) | `AssertionError: #teeth=26&root_shape=trochoid: the rows ['Pitch Ø', ..., 'Root fillet used', ...] lack 'Hob tip radius used'` (note `step: root_fillet label`) | `.planning/phases/28-refuse-the-bad-link/investigation/28-02-red-label.log` |
| `form build error` (old wording; `1 failed, 2 passed in 27.27s`) | `Locator expected to have text 'Could not build the form: Selector "Bore shape" names the group "No such group", which no field has'`, actual `Could not load the parameter schema: Selector "Bore shape" ...` (note `step: form build error`) | `.planning/phases/28-refuse-the-bad-link/investigation/28-02-red-wording.log` |

Green logs: `28-02-green-label.log` (exit 0, `18 passed in 27.62s`, step 0.20 s) and `28-02-green-wording.log` (exit 0, `18 passed in 28.81s`, step 1.10 s). The two `bench/RESULTS.md` rows and sections (`### The root_fillet label (28-02)`, `### The form build error (28-02)`) carry the same figures.

## Gate

`make verify` ran (ruff, `mypy src tests docker bench scripts`, import-linter `5 kept, 0 broken`, unfinished-work scan, pytest). Result line: `1348 passed in 207.30s (0:03:27)`, `TOTAL 97.99%`, `Required test coverage of 96.0% reached`, `exit 0`. Each commit also passed the pre-commit `make verify.fast`. `git diff --exit-code v0.5 -- tests/regression/` is empty.

## Commits

- `61154d1` fix(28): label the root_fillet row by the root the server built
- `282fa63` docs(28): say what the bore-shape stash holds, and file its hand-edit invalidation as an idea
- `235e51d` fix(28): say the form could not be built when a selector names an unknown group

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] mypy rejected re-used local names in the browser test**
- **Found during:** Task 1, the first commit attempt (pre-commit `make verify.fast`)
- **Issue:** the test function is one long scope; my `labels`, `shown` and `other` clashed with earlier variables of other types (`mypy --strict`: incompatible assignment).
- **Fix:** renamed to `row_labels`, `dim_labels` and `absent`; wrapped two assert messages for the line limit. The green log was re-run on the final test before the commit.
- **Files modified:** `tests/test_browser.py`
- **Commit:** `61154d1`

**Total deviations:** 1 auto-fixed (blocking lint/type). **Impact:** none on behaviour; the red log predates the rename and fails on the same assertion text.

## Debt ledger

No debt item was filed. One item was retired: `docs/tech_debt/resolved/2026-10-09-phase-19-review-info-findings-deferred.md` (`Resolved in:` carries the commit subject; Plan 28-04 writes the short sha). One idea was filed: `docs/ideas/2026-10-21-stash-entry-survives-a-hand-edit.md`, with its row in `docs/ideas/INDEX.md`.

## Known Stubs

None.

## Threat Flags

None. The label is set through `textContent`; the stash comment adds no value write (the selectors-section guard still counts one).

## Self-Check: PASSED

- Files exist: the idea, the four logs, the moved debt item (the `active/` path is gone), `app.js`, `tests/test_browser.py`.
- Commits `61154d1`, `282fa63`, `235e51d` are ancestors of HEAD; `commits: 3` measured from `359b6d5..HEAD`.
- Acceptance greps: the `root_fillet` row line once, `d.root_form_d != null` once, `with step("root_fillet label"` once, `with step("form build error"` once, `Could not build the form: ${err.message}` once, the old wording 0, `24-REVIEW IN-01` in `app.js` once, four Phase 28 rows in the Seen-red table.
