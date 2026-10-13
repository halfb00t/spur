---
phase: 24-bore-shape-selector
plan: 03
subsystem: testing
tags: [playwright, selectors, browser-test, request-recorder, golden-sweep, idea-retirement]

requires:
  - phase: 24-bore-shape-selector
    provides: "plan 24-01: the model-level selectors list, the generic buildSelectors/deriveSelectors/pick/pend in app.js, the bore shape step and the schema-driven helpers (feature commit 470b78a); plan 24-02: tests/test_selector.py (505999e)"
  - phase: 23-conditional-form-fields
    provides: "the golden sweep and its dimmed-set comparison, the Python evaluator over /api/schema, the refused keyway pair"
provides:
  - "Swept(query, inactive, shown) and sweep() reading the select in the same pass as the query and the dimmed set"
  - "record_api(page, seen), foreign_keys(seen, allowed) and step(name, *checks) in tests/browser_session.py"
  - "A recorder on all seven pages the scenario opens, asserted after every one of the fourteen steps and once at the end"
  - "The bore shape step widened to every pick from every state (sixteen), the stash across hash navigations and the picks over a keyed bore"
  - "The bore-shape idea retired and the hex-bore warning debt's trigger restated, both in the closing commit"
affects: [24-04, 25]

actuals:
  tokens: 4383   # chars/4 over the added lines of the realized diff (17,531 chars), the plan's estimate scale; not a harness count
  tasks: 2
  commits: 2
plan_head_before: 1d8bf751e4eba420e9c3d72f6134cfac698d0c37
plan_head_after: 3a8028bc3896ac97e685d2d632db6598fc7bbd65

tech-stack:
  added: []
  patterns:
    - "A recorder is attached to every page the scenario opens, because each page is its own browser context, and its check runs as a step's own argument so a leak is attributed to the step that sent it"
    - "A count that only a fully watched scenario can reach (more api/info requests than the sweep alone sends) proves that no page went unwatched"
    - "Each deliberate break is restored with git checkout and proved with git diff --exit-code, and the result is also compared with the feature commit"

key-files:
  created: []
  modified:
    - tests/browser_session.py
    - tests/test_browser.py
    - docs/architecture/web-ui.md
    - docs/ideas/INDEX.md
    - docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md
    - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The recorder list is shared by all seven pages and its check is passed to step() as an argument, so a request that leaked a key fails with the note of the step that sent it"
  - "The closing recorder assertion is that more api/info requests were seen than the sweep alone sends (44), which a recorder that missed the sweep's page cannot reach"
  - "The helper that lists the fields a selector's conditions name lives in tests/test_browser.py as _named_fields(), not in browser_session.py, because Task 2's file list and the closing commit's path check exclude browser_session.py"
  - "The hex-bore warning debt stays active and is restated, not resolved: its trigger fired when the selector shipped, and the fix is a /gsd-quick before Phase 25's reading"

patterns-established:
  - "The keyed-bore case derives its link from the existing REFUSED_LINK by removing the fields the selector names, so no new literal is added"

requirements-completed: [REQ-selector-derives-and-writes-through, REQ-selector-round-trips-per-state]

coverage:
  - id: D1
    description: "The golden sweep reads the shown bore-shape option under all 44 fixture links in the same pass as the query and the dimmed set; it equals the schema's derivation, every link shows one option, three distinct options are seen, and the sent queries still equal the committed pin"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step golden sweep: shown {'D-flat': 32, 'No bore': 8, 'Round': 4})"
        status: pass
    human_judgment: false
  - id: D2
    description: "A recorder on every page the scenario opens proves that no /api/* request carries a key beyond GearParams' fields, quality and mate_teeth, that the main page's hash does the same, and that the recorder saw more api/info requests than the sweep alone sends"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (no_foreign_key after each of 14 steps and at the end; request recorder: 260 /api requests (140 api/info))"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each of the four options picked from each of the four states, the shown option included, sends the query the Python mirror of the write rule predicts, or is pending as it predicts with nothing written"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bore shape: sixteen matrix picks)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The stash outlives hash navigations: Round picked, two links opened, D-flat picked restores bore_flat's 8 and sends the empty query"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bore shape: the stash outlived #bore_hex=0.05 and #bore_flat=0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Over a keyed bore every pick leaves the keyway pair as the link set it, No bore and Hex draw the server's 422 and the page marks exactly the fields it names, with the Hex keyway pair both dimmed and invalid"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bore shape: keyed + Round/D-flat API 200, keyed + Hex/No bore API 422)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The deriveSelectors() call in readHash() and in the Reset handler were each seen red, and app.js is back byte-identical to 470b78a"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: other
        ref: "investigation/24-03-readhash-red.log (step: golden sweep) and investigation/24-03-reset-red.log (step: bore shape); git diff --exit-code -- src/spur/static/app.js"
        status: pass
    human_judgment: false
  - id: D7
    description: "The bore-shape idea is retired with an outcome and the hex-bore warning debt is restated with its trigger fired, in the plan's last commit"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: other
        ref: "the Task 2 verify scripts: the idea under retired/ with Status: retired and the exact Retired in line, the INDEX row moved, the debt still under active/ with the restated trigger"
        status: pass
    human_judgment: true
    rationale: "The scripts check that the structure and the named strings are present; whether the Outcome paragraph describes what Phase 24 built fairly is a person's call"

duration: 17min
completed: 2026-10-12
status: complete
---

# Phase 24 Plan 03: Browser proof across every state and page, and the phase's work closed Summary

**The golden sweep now reads the bore-shape select under all 44 fixture links (D-flat 32, No bore 8, Round 4) with the query pin unmoved, a recorder on all seven pages proves no request or hash carries a key GearParams lacks, the bore shape step picks all four options from all four states and follows the stash and a keyed bore, and the idea is retired with the hex-warning debt restated, behind a green `make verify` (1311 passed).**

## Performance

- **Duration:** 17 min (start time was not captured; estimated from the first shell timestamps)
- **Started:** about 2026-10-12T15:47:00Z (estimated)
- **Completed:** 2026-10-12T16:04:18Z (the closing commit; the SUMMARY and state commits follow)
- **Tasks:** 2
- **Files modified:** 7 (one of them renamed; no file created)

## Accomplishments

- `Swept` has a third field `shown`; `sweep()` reads `eval_shown(page)` at both places it reads the dimmed set. The `golden sweep` step compares it with `expected_shown()` over `/api/schema` for every link, requires every link to show an option and at least two distinct tuples, and the sent queries still equal the committed pin, which is the proof that loading never writes.
- `record_api()` wraps all seven `browser.new_page()` sites. `no_foreign_key` runs as the argument of all fourteen `step()` calls and once after the last, and the recorder must have seen more `api/info` requests than the 44 the sweep alone sends.
- The `bore shape` step picks each option from each state (sixteen picks), follows the stash across two hash navigations, and picks over the keyway pair, where Round and D-flat answer 200 and No bore and Hex answer 422 with the page marking exactly what the server names.
- Both derive call sites were seen red once and `app.js` was restored byte for byte.
- `make golden.regen` rewrote the pin byte for byte (`git diff --exit-code` empty on both regression files after each task).
- The bore-shape idea moved to `docs/ideas/retired/` with `Status: retired`, the exact `Retired in:` line and an `## Outcome`; the hex-warning debt stays active with its trigger restated.

## Task Commits

1. **Task 1: the golden sweep reads the select, a recorder on every page** - `f489d3d` (test): `test(24): the golden sweep reads the bore shape each link derives, and no page sends a key GearParams lacks`
2. **Task 2: every pick from every state, the stash, the keyed bore, the idea retired** - `3a8028b` (test): `test(24): every pick from every bore shape, the stash across links and the keyed bore -- retire the bore-shape idea`

`git rev-list --count 1d8bf75..HEAD` read 2 when the commits were made; the base is `1d8bf75`. Neither commit touches `src` or `tests/regression`.

**Plan metadata:** the SUMMARY commit and the STATE/ROADMAP/REQUIREMENTS commit follow this file.

## Files Created/Modified

- `tests/browser_session.py` - `Swept.shown`, `sweep()` reading the select, `record_api()`, `foreign_keys()`, `step(name, *checks)`
- `tests/test_browser.py` - the recorder list `seen`, `allowed_query`, `allowed_hash`, `no_foreign_key`, the golden sweep's select comparison, the sixteen-pick matrix, the stash case, the keyed-bore case, `INVALID_NAMES` and `_named_fields()`
- `docs/architecture/web-ui.md` - the Tests sentences (L42)
- `docs/ideas/INDEX.md` and `docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md` - the retirement (a `git mv`, recorded as a rename)
- `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` and `docs/tech_debt/INDEX.md` - the restated trigger and the refreshed `params.py` line numbers (`:134` and `:137`)

## Decisions Made

- The recorder list is shared by all seven pages, and the check is a `step()` argument, so a leaked key fails with the note of the step that sent it (D-14).
- The count of `api/info` requests being greater than 44 is the proof that the sweep's page, which sends one per record by itself, was watched.
- `_named_fields()` is in `tests/test_browser.py`, not `browser_session.py`: Task 2's file list and its closing-commit path check exclude `browser_session.py`.
- The debt is restated and left active, as D-17 says; it is neither resolved nor moved.

## Green readings

Host: hbMBP, Apple M2 Max, macOS 27.0.1, Python 3.12.13, playwright 1.63.0, Chrome Headless Shell (webgl2 renderer ANGLE, Vulkan 1.3.0, SwiftShader).

Task 1 (`24-03-browser-sweep.log`, `uptime` 21:52, load averages 3.46 5.69 7.76): `2 passed in 13.65s`, and

```
golden sweep: 44 records, 44 distinct queries, 1 distinct dimmed sets
golden sweep: shown {'D-flat': 32, 'No bore': 8, 'Round': 4}
step golden sweep: 0.38 s
step inert fields: 1.29 s
step bore shape: 1.89 s
step unknown relation op: 4.12 s
request recorder: 167 /api requests (85 api/info) from every page, every key a GearParams field, quality or mate_teeth
```

Task 2 (`24-03-browser-picks.log`, the final run, `uptime` 21:56, load averages 2.89 4.50 6.78): `2 passed in 20.37s`, `step golden sweep: 0.35 s`, `step bore shape: 8.65 s`, `step unknown relation op: 4.11 s`, the same two `golden sweep:` lines, and `request recorder: 260 /api requests (140 api/info) from every page, every key a GearParams field, quality or mate_teeth`. The step grew from 1.89 s to 8.65 s on this host; 24-04 prices it properly. The matrix, the stash and the keyed bore:

```
bore shape: #bore_flat=0 + Round -> sent 'bore_flat=0'
bore shape: #bore_flat=0 + D-flat -> pending: bore_flat: D-flat needs D-flat above 0
bore shape: #bore_flat=0 + Hex -> pending: bore_hex: Hex needs Hex bore A/F above 0
bore shape: #bore_flat=0 + No bore -> sent 'bore_d=0&bore_flat=0'
bore shape: # + Round -> sent 'bore_flat=0'
bore shape: # + D-flat -> sent ''
bore shape: # + Hex -> pending: bore_hex: Hex needs Hex bore A/F above 0
bore shape: # + No bore -> sent 'bore_d=0'
bore shape: #bore_hex=0.05 + Round -> sent 'bore_flat=0'
bore shape: #bore_hex=0.05 + D-flat -> sent ''
bore shape: #bore_hex=0.05 + Hex -> sent 'bore_hex=0.05'
bore shape: #bore_hex=0.05 + No bore -> sent 'bore_d=0'
bore shape: #bore_d=0 + Round -> pending: bore_d: Round needs Bore Ø above 0
bore shape: #bore_d=0 + D-flat -> pending: bore_d: D-flat needs Bore Ø above 0
bore shape: #bore_d=0 + Hex -> pending: bore_hex: Hex needs Hex bore A/F above 0
bore shape: #bore_d=0 + No bore -> sent 'bore_d=0'
bore shape: the stash outlived #bore_hex=0.05 and #bore_flat=0
bore shape: keyed + Round -> 'bore_flat=0&keyway_width=3&keyway_depth=1.4': API 200
bore shape: keyed + D-flat -> 'keyway_width=3&keyway_depth=1.4': API 200
bore shape: keyed + Hex -> 'keyway_width=3&keyway_depth=1.4&bore_hex=0.05': API 422
bore shape: keyed + No bore -> 'bore_d=0&keyway_width=3&keyway_depth=1.4': API 422
```

The pick of the shown option (`# + D-flat`, `#bore_hex=0.05 + Hex`, `#bore_d=0 + No bore`, `#bore_flat=0 + Round`) sent the query the page already had, so `select_option` fires `input` on an unchanged value as the plan read at planning. The log holds 27 `bore shape: #... + ... -> ...` lines.

Regen (`24-03-golden-regen.log`): `wrote 44 records (44 distinct queries) to .../tests/regression/golden_requests.json`, `make golden.regen exit 0`, and `git diff --exit-code -- tests/regression/golden_requests.json tests/regression/pre_v0_2.json` is empty.

## Seen red

Both runs used `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`. Logs are under `.planning/phases/24-bore-shape-selector/investigation/` (untracked until 24-04).

1. **The `deriveSelectors();` line deleted from `readHash()`** (`app.js` line 110), `24-03-readhash-red.log`, `1 failed, 1 passed in 5.65s`, note `step: golden sweep`. First failure line: `AssertionError: golden sweep: the shown options differ: README:export-defaults: the page shows ('Round',), the schema says ('D-flat',); ...` (40 of the 44 records differ; the 4 that derive Round agree by accident because an unset select shows its first option). Restore: `git checkout -- src/spur/static/app.js`, then `git diff --exit-code -- src/spur/static/app.js` was silent.
2. **The `deriveSelectors();` line deleted from the `#reset` handler** (`app.js` line 540), `24-03-reset-red.log`, `1 failed, 1 passed in 6.76s`, note `step: bore shape`. First failure line: `AssertionError: bore shape, Reset: shows ('Hex',), not 'D-flat'`. Restore the same way, and `git diff 470b78a --exit-code -- src/spur/static/app.js` was silent, so `app.js` is the 24-01 file.

## The gate

`make verify`, `24-03-verify.log` (`uptime` 21:57, load averages 5.36 4.71 6.68 at the start): `1311 passed in 336.15s (0:05:36)`, `make verify exit 0`. The count equals 24-02's 1311, because this plan adds assertions to an existing test and no new test function. Coverage: `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`. The first run was green, so the resource-tracker flake did not appear and no re-run was used. The commit hook ran `make verify.fast` for both commits and passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Variable names clashed with the test function's earlier locals**
- **Found during:** Task 2 (`make typecheck`)
- **Issue:** mypy scopes a name to the whole test function, and `kept`, `invalid`, `both`, `marked` and `dimmed` already hold other types earlier in it, so the first version of the keyed-bore code failed type checking.
- **Fix:** Renamed to `changed`, `marked_names`, `dimmed_marked`, `named` and `dimmed_names`, and the selector's own field set to `chooser_fields`. No behaviour changed.
- **Files modified:** `tests/test_browser.py`
- **Verification:** `make lint typecheck` passes.
- **Committed in:** `3a8028b`

### Other deviations

**2. [Plan text already satisfied] The pick helpers were not inline.** Task 2 step 1 says to move 24-01's inline writing and pending assertions into local functions `sent_pick` and `pending_pick`. 24-01 had already made them module-level `_writing_pick` and `_pending_pick`, so the cases reuse those and nothing was moved or renamed.

**3. [Added helper placement] `_named_fields()` and `INVALID_NAMES` are in `tests/test_browser.py`.** `browser_session.py` is not in Task 2's file list and the closing-commit verify requires exactly six paths, so a helper that reads the selector's conditions could not go there.

**4. [Wording] The debt sentence starts on its own line.** The verify greps `Trigger fired: the selector shipped in <sha>` on one line, so the restated sentence begins on a new line in the file, which is a wrap choice and not a content change.

---

**Total deviations:** 1 auto-fixed (blocking), 3 noted
**Impact on plan:** None changes what any step proves or what any criterion asserts.

## Issues Encountered

- `gsd_run check evaluation-scope --plan 24-03 --commits-only` returns `no-matching-commits`, as it did for 24-01: the resolver matches subjects of the form `test(24-03): ...` and the plan mandates `test(24): ...`. Both commits were verified by `git rev-list --count 1d8bf75..HEAD` (2), by the plan's own verify scripts (exactly one commit per subject, the exact path sets) and by `git merge-base --is-ancestor`.
- Task 2's first green browser run passed at once, so no assertion in the new cases was ever red for a wrong reason; the red evidence for them is the Reset break above, which the matrix's own `reset_bore()` caught.

## Known Stubs

None.

## Threat Flags

None. T-24-09 is mitigated as the register says (seven pages wrapped and counted by the verify, the check after every step and at the end, the `api/info` count), and T-24-10 as well (the regen proved byte identity and `git diff --exit-code` on both regression files was empty after each task and across both commits).

## User Setup Required

None - no external service configuration required.

## Debt and ideas

No debt item or idea was filed in this plan. One idea was retired (`docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md`) and one debt item was restated and left active (`docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`, trigger fired in `470b78a`, to be fixed as a `/gsd-quick` before Phase 25's reading).

## Next Phase Readiness

- 24-04 can price the browser step and commit the kept logs under `investigation/`: `24-03-readhash-red.log`, `24-03-browser-sweep.log`, `24-03-golden-regen.log`, `24-03-reset-red.log`, `24-03-browser-picks.log` and `24-03-verify.log`, plus the 24-01 and 24-02 logs. The `bore shape` step now costs 8.65 s on this host.
- Nothing is blocked.

## Self-Check: PASSED

- `tests/browser_session.py`, `tests/test_browser.py`, `docs/architecture/web-ui.md`, `docs/ideas/INDEX.md`, `docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md`, `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` and `docs/tech_debt/INDEX.md` exist, and `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` does not.
- `git merge-base --is-ancestor` found `f489d3d` and `3a8028b` in HEAD; each subject is carried by exactly one commit; `git show --name-status -M` lists the two test files for the first and the six paths with one rename for the second.
- All Task 1 and Task 2 verify commands and acceptance greps were re-run after the last change and passed; `git diff --exit-code -- src tests/regression` is empty across `1d8bf75..HEAD`.

---
*Phase: 24-bore-shape-selector*
*Completed: 2026-10-12*
