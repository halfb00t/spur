---
phase: 24-bore-shape-selector
plan: 02
subsystem: testing
tags: [pytest, selectors, pydantic, json_schema_extra, round-trip, grid, meta-red]

requires:
  - phase: 24-bore-shape-selector
    provides: "plan 24-01: the model-level selectors list on GearParams.model_config (Bore shape, four options), feature commit 470b78a"
  - phase: 23-conditional-form-fields
    provides: "the when() condition grammar and the Python evaluator in tests/test_relations.py (_conditions, _condition_holds, _properties)"
provides:
  - "tests/test_selector.py: a kernel-free module in the make verify.fast slice with the walk, the top-level keyword check, the grid, the round trip per state, the stash round trip and the doctored-copy tests"
  - "A Python mirror of the D-07/D-08 write rule (_pick: plan, then write) and the write-first order kept only to be seen red"
  - "Evidence that three deliberately wrong options on the real params.py each turn the module red"
affects: [24-03, 24-04]

actuals:
  tokens: 7147   # chars/4 over the added file (28,587 chars), the plan's estimate scale; not a harness count
  tasks: 2
  commits: 1
plan_head_before: a8a34fabe0af83949d55ec5dea521af0da9d7496
plan_head_after: 505999ee07896be230baf32dae95a5b6e6ca4c1a

tech-stack:
  added: []
  patterns:
    - "A checker takes the data as an argument, so a doctored copy can be fed to it permanently (the 23-02 precedent), and each doctored case matches the checker's own message so it cannot go red by accident"
    - "A pick is proved against the typed path by exact GearParams and derive().model_dump() equality, plus the changed-field set and the chosen option's truth, because derive() alone cannot tell Round from D-flat"

key-files:
  created:
    - tests/test_selector.py
  modified: []

key-decisions:
  - "The module also imports _number from tests/test_relations.py beside the plan's six names: a one-line schema-number reader reused rather than copied, still one evaluator and no kernel"
  - "Every doctored malformed case is matched against its own message (no such field, is not numeric, is outside, empty label, under both eq and gt, above the maximum), so a case cannot go red for another reason"
  - "The commit trailer is Co-Authored-By: Claude Sonnet 5.5, the line the plan and the session reminder give, not the dispatch note's Fable 5.1 (see Deviations)"

patterns-established:
  - "A start state per label is computed from the model (a false eq gets its value, a false gt the first of minimum + step and maximum above its threshold), so no option label or threshold is written into the round trip"

requirements-completed: [REQ-selector-round-trips-per-state, REQ-selector-schema-carried]

coverage:
  - id: D1
    description: "Every selector on GearParams.model_config is a well-formed {title, group, options} judged by L41's one grammar, with thresholds inside the fields' bounds and the schema emitting the list unchanged"
    requirement: "REQ-selector-schema-carried"
    verification:
      - kind: unit
        ref: "tests/test_selector.py#test_every_selector_is_well_formed_and_emitted_unchanged"
        status: pass
      - kind: unit
        ref: "tests/test_selector.py#test_a_malformed_selector_goes_red (6 doctored copies)"
        status: pass
    human_judgment: false
  - id: D2
    description: "selectors is the one top-level key the model adds and is no JSON Schema 2020-12 or legacy keyword"
    requirement: "REQ-selector-schema-carried"
    verification:
      - kind: unit
        ref: "tests/test_selector.py#test_selectors_is_the_one_top_level_key_and_no_json_schema_keyword"
        status: pass
    human_judgment: false
  - id: D3
    description: "Exactly one option holds on every non-negative triple of the condition fields, never two on any cell, every no-match cell holds a negative value, and the default part shows D-flat"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: unit
        ref: "tests/test_selector.py#test_exactly_one_option_holds_on_every_valid_cell_and_the_default_is_d_flat"
        status: pass
      - kind: unit
        ref: "tests/test_selector.py#test_a_wrong_option_goes_red (wrong field 1, wrong op 2, overlap 1, gap 2)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every pick from each of the four states, and every second pick with the stash the first left, validates from the page's strings, makes the chosen option the only one that holds, changes exactly the false conditions' fields, and equals the typed path in GearParams and derive().model_dump()"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: unit
        ref: "tests/test_selector.py#test_each_pick_from_each_state_writes_the_minimum_and_matches_the_typed_path"
        status: pass
      - kind: unit
        ref: "tests/test_selector.py#test_writing_before_planning_goes_red"
        status: pass
    human_judgment: false
  - id: D5
    description: "A zeroed value comes back from the stash and never from a starter value; with an empty stash the pick back is pending"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: unit
        ref: "tests/test_selector.py#test_a_zeroed_value_comes_back_from_the_stash_and_never_from_a_starter"
        status: pass
    human_judgment: false
  - id: D6
    description: "Each proof was seen red against a deliberately wrong option on the real params.py, and params.py is restored byte for byte"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: other
        ref: "the Task 2 verify scripts: three red logs with a non-zero make test.fast exit, and git diff --exit-code -- src/spur/params.py"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-10-12
status: complete
---

# Phase 24 Plan 02: Bore-shape selector model-side proof Summary

**`tests/test_selector.py` proves the bore-shape options are well formed, total, exclusive and round-trip through the flat fields (16 tests in the commit slice, 35 grid cells, 40 writing and 16 pending picks), and a wrong field, a wrong op and an overlap on the real model each turned it red.**

## Performance

- **Duration:** 8 min (the 5 min `make verify` is inside it)
- **Started:** 2026-10-12T15:34:17Z
- **Completed:** 2026-10-12T15:42:12Z
- **Tasks:** 2
- **Files modified:** 1 (one file created, no existing file touched)

## Accomplishments

- The walk checks every selector and option against L41's one grammar judge (`_conditions` from `tests/test_relations.py`), requires numeric model fields, thresholds inside the schema `minimum`..`maximum`, disjoint `eq` and `gt` field sets per option, unique clean labels, no shared condition object, and equality with `GearParams.model_json_schema()['selectors']`.
- The keyword check pins the schema's top-level keys to `description, properties, selectors, title, type` and `selectors` outside both keyword lists.
- The grid returns 35 cells (8 non-negative plus 27 of `{-1, 0, positive}`): exactly one option on each non-negative cell, never two, and the 13 no-match cells each hold a negative value. The default part shows `['D-flat']`.
- The round trip walks four starts (Round `{bore_flat: 0}`, D-flat `{}`, Hex `{bore_hex: 0.05}`, No bore `{bore_d: 0}`) times four first picks times four second picks: 40 writing and 16 pending picks. Each writing pick is validated from the strings the page sends and compared with the typed path by exact equality, with the changed-field set and the chosen option's truth asserted beside `derive()` equality (24-RESEARCH Finding 6).
- The stash test shows a zeroed field comes back with the user's own number and that an empty stash makes the pick back pending.
- Ten doctored copies (four wrong options, six malformed selectors) and a write-before-plan mirror keep every checker red-proof permanently.

## Task Commits

1. **Task 1: tests/test_selector.py** - built and verified, not committed on its own (the plan commits once, at Task 2).
2. **Task 2: three wrong options seen red, make verify green, one commit** - `505999e` (test): `test(24): the bore-shape options are total, exclusive and round-trip through the flat fields -- tests/test_selector.py`

`git rev-list --count a8a34fa..HEAD` read 1 when this was written; the commit adds only `tests/test_selector.py` and touches nothing under `src` or `tests/regression`.

**Plan metadata:** the SUMMARY commit and the STATE/ROADMAP/REQUIREMENTS commit follow this file.

## TDD note

Task 1 carries `tdd="true"`, but nothing is implemented in it: the selector it tests shipped in 24-01 (`470b78a`), so there is no code to write between a red test and a green one, and `workflow.tdd_mode` is off (the Phase 11 precedent). The module was green on its first run (`16 passed in 0.09s`), so the red evidence is the permanent doctored-copy tests and the three breaks on the real model below, each of which failed for the planned reason before the module was committed.

## Test result

`make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"`, log `24-02-selector.log`: `16 passed in 0.09s`. The 16 are 6 plain tests plus 4 wrong-option and 6 malformed-selector cases. `make lint typecheck`: `All checks passed!` and `Success: no issues found in 49 source files`.

## Seen red

Each break edited only `_BORE_SHAPE` in `src/spur/params.py`, was run with `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q -rf"`, and was restored by `cp` from a saved copy followed by `git diff --exit-code -- src/spur/params.py` (silent). The saved copy was deleted after the last restore, and `cmp` against it was clean before deletion. Logs are under `.planning/phases/24-bore-shape-selector/investigation/` (untracked until 24-04).

| Break | Log | Result | First assertion lines | Restore |
|---|---|---|---|---|
| wrong field: D-flat's `when("bore_flat", "gt", 0)` became `when("bore_hex", "gt", 0)` | `24-02-wrong-field-red.log` | 15 failed, 1 passed; `make test.fast exit 2` | `AssertionError: selector 0, D-flat: ['bore_hex'] is under both eq and gt` (the walk, which also caught it); then `AssertionError: Bore shape: cell (0.0, 9.0, 8.0) holds [], not exactly one option` (the grid) and `AssertionError: ('D-flat', {'bore_hex': 0.05})` (the starts) | `cp`, `git diff --exit-code` clean |
| wrong op: Round's `when("bore_flat", "eq", 0)` became `"gt"` | `24-02-wrong-op-red.log` | 8 failed, 8 passed; `make test.fast exit 2` | `AssertionError: Bore shape: cell (0.0, 9.0, 0.0) holds [], not exactly one option` (the grid) and `AssertionError: ('Round', {})` (the round trip's starts) | `cp`, `git diff --exit-code` clean |
| overlap: Round's `bore_flat eq 0` condition removed | `24-02-overlap-red.log` | 8 failed, 8 passed; `make test.fast exit 2` | `AssertionError: Bore shape: cell (0.0, 9.0, 8.0) holds ['Round', 'D-flat'], not exactly one option` (the grid) and `AssertionError: ('Round', {})` (the round trip) | `cp`, `git diff --exit-code` clean |

All three FAILED lists contain `test_exactly_one_option_holds_on_every_valid_cell_and_the_default_is_d_flat`, and the wrong-op and overlap lists also contain `test_each_pick_from_each_state_writes_the_minimum_and_matches_the_typed_path`, as the plan expects. Under every break the module's own doctored-copy tests also fail, because their unedited-model control no longer holds, which is correct. The wrong-field break was additionally caught by the walk (`test_every_selector_is_well_formed_and_emitted_unchanged`), since the edit leaves `bore_hex` under both `eq` and `gt`.

## The gate

`make verify`, 600 s tool timeout, `24-02-verify.log`: `1311 passed in 294.40s (0:04:54)`, `make verify exit 0`. That is 1295 from 24-01 plus the 16 new tests. Coverage: `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`, with `params.py` at 100.00%. The commit hook ran `make verify.fast` and passed. No re-run was needed, so the resource-tracker flake did not appear this time.

## Files Created/Modified

- `tests/test_selector.py` - the walk, keyword check, grid, round trip, stash round trip and the doctored-copy tests; kernel-free, imports `spur.params`, `spur.calc` and `tests/test_relations.py` only, not in `HEAVY_TEST_FILES`

## Decisions Made

- The module imports `_number` from `tests/test_relations.py` beside the six names the plan lists, to read schema bounds without a copy (see Deviations).
- Each malformed-selector case is matched against its own message, so a case cannot go red for another reason.
- `_page_string` is a copy of `browser_session._js_number` with a comment saying why: that module imports playwright and this one must stay in the commit slice.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A 103-column assertion line**
- **Found during:** Task 1 (`make lint`)
- **Issue:** One `assert ... f"..."` line in `_check_pick` was 103 columns against ruff's limit of 100.
- **Fix:** Wrapped the message in parentheses on the next line.
- **Files modified:** `tests/test_selector.py`
- **Verification:** `make lint typecheck` passes.
- **Committed in:** `505999e`

### Other deviations

**2. [Plan wording followed over a dispatch note] The commit trailer.** The orchestrator's note asked for `Co-Authored-By: Claude Fable 5.1`. The plan says to end with the attribution line the session reminder gives, the reminder gives `Co-Authored-By: Claude Sonnet 5.5`, and that is the model that wrote this commit, so `505999e` carries it. This is the same call 24-01 made. The orchestrator may want to reconcile the note and the reminder before 24-03.

**3. [Added import] `_number`.** The plan lists six names to import from `tests/test_relations.py`; the module also imports `_number` (the helper that reads a numeric key of a schema property). It is a reuse of an existing one-line helper, adds no kernel import, and the AST check in the plan's verify still passes. Surfaced rather than hidden.

---

**Total deviations:** 1 auto-fixed (lint), 2 noted (trailer, one extra import)
**Impact on plan:** None changes what the module proves or what any criterion asserts.

## Issues Encountered

None. The module was green on the real model at its first run, so the PD-14 stop (a failure on the real model is a finding) did not fire. No break left the grid test passing, so no hole in the proof was found.

## Known Stubs

None.

## Threat Flags

None. The module reads the model and writes no file at run time; T-24-07 and T-24-08 are mitigated as the plan's register says (the grid and the `derive()` class per label are in the commit slice, three wrong options were seen red, and the commit was checked to add only the test file with `params.py` equal to the 24-01 commit).

## User Setup Required

None - no external service configuration required.

## Debt and ideas

No debt item and no idea was filed in this plan.

## Next Phase Readiness

- 24-03 can widen the browser proof knowing the model half is pinned: `CLASS`, `_starts`, `_pick` and the exactly-one grid are the Python statement of what the browser step must agree with.
- 24-04 should commit the kept logs under `investigation/`: `24-02-selector.log`, `24-02-{wrong-field,wrong-op,overlap}-red.log` and `24-02-verify.log`.
- Nothing is blocked.

## Self-Check: PASSED

- `tests/test_selector.py` exists (28,587 bytes) and is the only file in `505999e` (`git show --name-status` lists one `A`).
- `git merge-base --is-ancestor 505999e HEAD` found the commit; `git rev-list --count a8a34fa..HEAD` read 1.
- Both Task 2 verify scripts passed after the commit: the three red logs, the saved copy gone, `git diff --exit-code -- src/spur/params.py` clean, exactly one commit carries the subject, no tracked file left modified, `make verify exit 0` and a passed line in the kept log.
- Task 1 acceptance: `16 passed` in `24-02-selector.log`; 8 `^def test_` lines; one `^from test_relations import`; 2 `@pytest.mark.parametrize`; `git diff --exit-code -- src tests/regression tests/test_relations.py tests/test_hooks.py` empty.

---
*Phase: 24-bore-shape-selector*
*Completed: 2026-10-12*
