---
phase: 23-conditional-form-fields
plan: 03
subsystem: testing
tags: [playwright, browser-test, enabled_when, golden-sweep, idea-retirement]

requires:
  - phase: 23-conditional-form-fields
    provides: "expected_inactive()/eval_inactive() (23-01), the eleven declared relations (23-02)"
provides:
  - "tests/browser_session.py: Swept(query, inactive), sweep() reading the dimmed set in the same pass as the query, flip_links(), one shared _holds() for the eq/gt grammar"
  - "tests/test_browser.py: golden sweep compares the dimmed set of all 44 fixture links; inert fields runs one flip link per gate condition, the refused keyway pair, the visible dim and Reset from the refused state"
  - "The conditional-fields idea retired (docs/ideas/retired/, INDEX row moved)"
affects: [23-04, 24-bore-selector]

actuals:
  tokens: 5834
  tasks: 2
  commits: 2
plan_head_before: 7e39240ba5dde62817d09fd3c5cb8aa549ded549
plan_head_after: e4f63ffc61ad00e1381e6c12ae01e97f38234de0
commits: 2

tech-stack:
  added: []
  patterns:
    - "Two evaluators with no shared code (JS applyRelations, Python expected_inactive) must agree on every state: the 44 fixture links, one derived flip per gate condition, the refused pair and Reset"
    - "A test helper that derives its inputs from the schema (flip_links) names no field, so a fifth relation adds its own link"

key-files:
  created:
    - docs/ideas/retired/2026-09-29-conditional-form-fields.md
  modified:
    - tests/browser_session.py
    - tests/capture_requests.py
    - tests/test_browser.py
    - docs/architecture/web-ui.md
    - docs/ideas/INDEX.md

key-decisions:
  - "sweep() returns Swept(query, inactive); the regen script keeps writing .query only, so make golden.regen is byte-identical"
  - "The eq/gt comparison lives in one private _holds() used by both expected_inactive and flip_links, not copied"

patterns-established:
  - "A deliberate break of one call site (readHash, #reset) is run once, the failing step kept as a log, the file restored and proved with git diff --exit-code"

requirements-completed: [REQ-form-walk-proves-relations, REQ-dim-and-editable]

coverage:
  - id: D1
    description: "The golden sweep compares, for each of the 44 fixture links, the dimmed set and reasons the page shows with the Python evaluator's over /api/schema, beside the unchanged query pin"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step golden sweep; investigation/23-03-browser-sweep.log)"
        status: pass
    human_judgment: false
  - id: D2
    description: "make golden.regen on this tree rewrites tests/regression/golden_requests.json byte for byte (44 records), proved with git diff --exit-code and never staged"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: other
        ref: "make golden.regen; git diff --exit-code tests/regression/golden_requests.json tests/regression/pre_v0_2.json"
        status: pass
    human_judgment: false
  - id: D3
    description: "One schema-derived flip link per gate condition (bore_hex, spoke_count, hole_count, hex_cell) leaves the dimmed set equal to the evaluator's and different from the default, whether the API answers 200 or 422; the refused keyway pair carries .invalid and .inactive together; Reset from it sends the empty query and restores the default set"
    requirement: REQ-dim-and-editable
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step inert fields; investigation/23-03-browser-flips.log)"
        status: pass
    human_judgment: false
  - id: D4
    description: "applyRelations() is load-bearing at readHash() and at #reset: removed from each, the browser test fails in the golden sweep and in inert fields respectively"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: e2e
        ref: "investigation/23-03-readhash-red.log (step: golden sweep), investigation/23-03-reset-red.log (step: inert fields)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The dim is visible: a reason is displayed for exactly the dimmed fields and their names are drawn in colours no live field's name uses"
    requirement: REQ-dim-and-editable
    verification:
      - kind: e2e
        ref: "tests/test_browser.py (step inert fields, visible dim block)"
        status: pass
    human_judgment: true
    rationale: "The test proves computed colours differ and the reason is displayed; whether the dim reads as legible and sensible to a person is a judgement for the phase's end-of-phase verification"
  - id: D6
    description: "The conditional-fields idea is retired in this plan's last commit: git mv, Status: retired, Retired in:, Outcome, INDEX row moved to Retired"
    verification:
      - kind: other
        ref: "git show --name-status e4f63ff (4 modified files and the rename)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-11
status: complete
---

# Phase 23 Plan 03: The browser proves the dim state Summary

**The golden sweep now reads the fields the page dims under all 44 fixture links and compares them with a Python evaluator over /api/schema, one derived flip link per gate, the refused keyway pair and Reset do the same, and the conditional-fields idea is retired.**

## Performance

- **Duration:** about 25 min
- **Completed:** 2026-10-11T12:57:00Z
- **Tasks:** 2
- **Files modified:** 6 (plus the idea file moved)

## Accomplishments

- `sweep()` returns `Swept(query, inactive)`, the dimmed set read right after each link's own request; the regen script reads `.query` only and rewrites the pin byte for byte.
- The `golden sweep` step asserts at least one record expects a non-empty set, then compares query (the unchanged pin) and dimmed set per record.
- `flip_links()` derives one link per distinct gate condition from the schema, naming no field; today it yields `bore_hex=0.05` (API 200), `spoke_count=1`, `hole_count=1`, `hex_cell=0.05` (each API 422).
- The refused pair `bore_hex=6&keyway_width=3&keyway_depth=1.4` shows `.invalid` and `.inactive` together on the two keyway fields, the gate `bore_hex` invalid and never dimmed; the dim is visible; Reset restores the default set and clears every `.invalid`.
- The idea is retired (`docs/ideas/retired/2026-09-29-conditional-form-fields.md`, subject below), INDEX row moved to `## Retired`.

## Evidence

Green sweep (`investigation/23-03-browser-sweep.log`):

```
golden sweep: 44 records, 44 distinct queries, 1 distinct dimmed sets
step golden sweep: 0.35 s
```

Regen proof (`investigation/23-03-golden-regen.log`): `wrote 44 records (44 distinct queries) to .../tests/regression/golden_requests.json`, then `git diff --exit-code tests/regression/golden_requests.json tests/regression/pre_v0_2.json` clean. Never staged.

Green flips (`investigation/23-03-browser-flips.log`), after the 23-01 lines for the `#spoke_count=0&hub_d=40` page:

```
inert fields: flip #bore_hex=0.05: API 200, dimmed ['bore_d', 'bore_flat', 'hex_wall', 'hole_circle_d', 'hole_d', 'hub_d', 'keyway_depth', 'keyway_width', 'rim_wall', 'spoke_fillet', 'spoke_width']
inert fields: flip #spoke_count=1: API 422, dimmed ['hex_wall', 'hole_circle_d', 'hole_d']
inert fields: flip #hole_count=1: API 422, dimmed ['hex_wall', 'hub_d', 'rim_wall', 'spoke_fillet', 'spoke_width']
inert fields: flip #hex_cell=0.05: API 422, dimmed ['hole_circle_d', 'hole_d', 'hub_d', 'rim_wall', 'spoke_fillet', 'spoke_width']
inert fields: refused pair: invalid ['bore_hex', 'keyway_depth', 'keyway_width'], dimmed and invalid ['keyway_depth', 'keyway_width']
step inert fields: 1.33 s
1 passed in 9.60s
```

Seen red (PD-10), each file restored with `git checkout -- src/spur/static/app.js` and proved with `git diff --exit-code -- src/spur/static/app.js`:

- Task 1, `applyRelations();` deleted from `readHash()`, `investigation/23-03-readhash-red.log`, `1 failed`, `step: golden sweep`. First failure: `AssertionError: golden sweep: the dimmed sets differ: README:export-defaults: the page dims {}, the schema says {'spoke_width': 'Needs Spoke arms above 0', 'hub_d': ...` (every record's page set empty against the seven).
- Task 2, `applyRelations();` deleted from the `#reset` handler, `investigation/23-03-reset-red.log`, `1 failed`, `step: inert fields`. First failure: `AssertionError: inert fields, Reset: the dimmed set differs from the empty link's` (the 23-01 fresh-page Reset check, which runs first, found the stale set: 4 of the 7 fields missing). The new Reset-from-refused-state check was not separately seen red because the earlier check fails the step first.

`make verify`: `1248 passed in 291.59s`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`, `TOTAL 1355 22 386 13 97.99%`, `make verify exit 0` (`investigation/23-03-verify.log`). Kept logs, all under `.planning/phases/23-conditional-form-fields/investigation/` (committed by 23-04): `23-03-golden-regen.log`, `23-03-browser-sweep.log`, `23-03-readhash-red.log`, `23-03-browser-flips.log`, `23-03-reset-red.log`, `23-03-verify.log`.

## Task Commits

1. **Task 1: the golden sweep reads the dim state of every fixture link** - `4c1eba3` (test)
2. **Task 2: one flip link per gate, the refused pair and Reset -- retire the conditional-fields idea** - `e4f63ff` (test)

**Plan metadata:** the docs(23-03) commit that carries this file.

## Files Created/Modified

- `tests/browser_session.py` - `Swept`, `sweep()` returning it, `flip_links()`, shared `_holds()`
- `tests/capture_requests.py` - reads `.query` from `Swept`; docstring says the regen pins the query only
- `tests/test_browser.py` - golden sweep compares dimmed sets; `REFUSED_LINK`; flips, refused pair, visible dim and Reset in `inert fields`
- `docs/architecture/web-ui.md` - Tests paragraph names the dim-state checks (L41)
- `docs/ideas/retired/2026-09-29-conditional-form-fields.md`, `docs/ideas/INDEX.md` - the retirement

## Decisions Made

None beyond the plan. The eq/gt comparison is one `_holds()` used by `expected_inactive` and `flip_links`, as the plan asked.

## Deviations from Plan

None - plan executed exactly as written. Two mechanical slips (a BSD `sed` line number that deleted the wrong line once, and a too-greedy rename of a local variable) were caught immediately; the first was reverted with `git checkout -- src/spur/static/app.js` and redone, so no wrong state was ever committed.

## Issues Encountered

- The first `#reset` red run deleted `mateInput.value = ''` instead of `applyRelations();` (line off by one), so it passed and its log was overwritten by the correct run. `app.js` was restored and verified identical to HEAD before and after.

## Filed items

No idea or tech-debt item filed. Bore-shape idea note: `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` and its INDEX row still say "(08 D-09 stands)"; that clause is now historical (L41 supersedes 08 D-09). I did not edit it, for Phase 24 to restate when it closes that idea.

## Known Stubs

None.

## Threat Flags

None.

## Next Phase Readiness

Ready for 23-04 (commits the kept investigation logs). Phase 24 can rely on the golden sweep and `flip_links()` picking up any new relation with no test edit.

## Self-Check: PASSED

Files found: `tests/browser_session.py`, `tests/capture_requests.py`, `tests/test_browser.py`, `docs/ideas/retired/2026-09-29-conditional-form-fields.md`. Commits `4c1eba3` and `e4f63ff` exist on this branch; `src/spur/static/app.js`, `golden_requests.json` and `pre_v0_2.json` identical to HEAD.

---
*Phase: 23-conditional-form-fields*
*Completed: 2026-10-11*
