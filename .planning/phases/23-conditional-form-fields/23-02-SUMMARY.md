---
phase: 23-conditional-form-fields
plan: 02
subsystem: ui
tags: [pydantic, json-schema, enabled_when, pytest, calc-parity, decision-log]

requires:
  - phase: 23-conditional-form-fields
    provides: "when() and _extra() in params.py, enabled_when on hub_d, the generic applyRelations() form code, L41 (plan 23-01)"
provides:
  - "The ten remaining D-09 relations on GearParams: bore_d, bore_flat, keyway_width, keyway_depth <- bore_hex eq 0; spoke_width, rim_wall, spoke_fillet <- spoke_count gt 0; hole_d, hole_circle_d <- hole_count gt 0; hex_wall <- hex_cell gt 0"
  - "tests/test_relations.py: the kernel-free proof module in make verify.fast (grammar walk, keyword collision, one-path and Literal probes, forward parity with warning names, refused pair, reverse coverage, three meta-red tests)"
  - "tests/test_cli.py: the schema walk checks every relation reaches /api/schema as the model wrote it, gated on a rendered field"
  - "docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md and docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md, each with its INDEX row"
affects: [23-03, 23-04, 24-bore-selector]

actuals:
  tokens: 8549
  tasks: 3
  commits: 2
plan_head_before: 8f7e1c9c45427b46685b7b701277c4c566d471a3
plan_head_after: d11af97271687a8d6b768f10f1aed9e4ae15251b
commits: 2

tech-stack:
  added: []
  patterns:
    - "A relation is proved against calc in both directions at commit time: forward (the dependent moves only the warning that names it) and reverse (every field an 'ignored' sentence names has a relation)"
    - "A checker takes the relation map as an argument so a doctored map can be fed to it and seen red permanently"

key-files:
  created:
    - tests/test_relations.py
    - docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md
    - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  modified:
    - src/spur/params.py
    - tests/test_cli.py
    - docs/ideas/INDEX.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The D-09 set is declared exactly as locked: 11 relations over 31 properties, nothing else carries enabled_when"
  - "The keyway pair is refused under a hex bore, not ignored, so REFUSED is pinned in the test and the two fields are gated on bore_hex and never on each other (CF-2)"
  - "A relation is true only if derive() moves nothing but warnings AND a warning names the field; derive-invariance alone passes bore_chamfer (23-RESEARCH Pitfall 2)"

patterns-established:
  - "The unbacked relations and the hex-warning noise are filed, not declared or filtered: the fix is a calc change with its own Lxx and fixture regen"

requirements-completed: [REQ-relations-calc-backed, REQ-enabled-when-metadata, REQ-form-walk-proves-relations]

coverage:
  - id: D1
    description: "The eleven D-09 relations are declared exactly on the model and /api/schema carries 11 relations over 31 properties, nothing else"
    requirement: REQ-enabled-when-metadata
    verification:
      - kind: other
        ref: "the Task 2 schema command: D-09 declared exactly: 11 relations, 20 fields without one"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_every_relation_is_well_formed_and_emitted_unchanged"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every declared relation is one calc backs: with it false, each dependent moves only the warning that names it at minimum+step and maximum, the keyway pair is refused naming the gate and both, and every field an 'ignored' sentence names has a relation"
    requirement: REQ-relations-calc-backed
    verification:
      - kind: unit
        ref: "tests/test_relations.py#test_with_its_relation_false_a_dependent_moves_only_the_warning_that_names_it"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_the_keyway_pair_is_refused_under_a_hex_bore_alone_and_together"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_every_field_calc_ignores_is_declared"
        status: pass
    human_judgment: false
  - id: D3
    description: "A wrong relation is red: the three meta-tests keep recess_depth, bore_chamfer and the set without spoke_fillet failing, and bore_chamfer was seen red once on the real model"
    requirement: REQ-relations-calc-backed
    verification:
      - kind: unit
        ref: "tests/test_relations.py#test_a_relation_calc_uses_goes_red"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_a_relation_calc_never_calls_ignored_goes_red"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_an_ignored_field_without_its_relation_goes_red"
        status: pass
    human_judgment: false
  - id: D4
    description: "No extra key is a JSON Schema word, both construction styles build their extra through _extra(), and a Literal field emits its relation unchanged"
    requirement: REQ-enabled-when-metadata
    verification:
      - kind: unit
        ref: "tests/test_relations.py#test_no_extra_key_is_a_json_schema_keyword"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_both_construction_styles_build_their_extra_through_one_helper"
        status: pass
      - kind: unit
        ref: "tests/test_relations.py#test_a_literal_field_carries_enabled_when_unchanged"
        status: pass
    human_judgment: false
  - id: D5
    description: "tests/test_cli.py's schema walk checks every relation reaches /api/schema exactly as the model wrote it, gated on a field the form renders"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order"
        status: pass
    human_judgment: false
  - id: D6
    description: "The browser step picks the new relations up from the schema with no test edit: the #spoke_count=0&hub_d=40 page dims seven fields and prints a reason for each"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step inert fields; investigation/23-02-browser.log)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The idea for the two unbacked relations and the debt for the hex warning are on file at PD-12's paths, each with its INDEX row"
    verification:
      - kind: other
        ref: "the Task 3 verify command: filed: one idea and one debt, each with its INDEX row, in one commit"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-11
status: complete
---

# Phase 23 Plan 02: Relations calc backs Summary

**The other ten D-09 relations declared on GearParams behind a kernel-free tests/test_relations.py that proves each against calc in both directions at commit time, seen red 3 failed / 7 passed before the declarations and red once more with a wrong relation on the real model.**

## Performance

- **Duration:** about 11 min (the `make verify` run alone was 215 s)
- **Started:** about 2026-10-11T12:29Z (not captured at start; reconstructed from the shell clock)
- **Completed:** 2026-10-11T12:40Z
- **Tasks:** 3 (Task 1 no commit, Task 2 feat, Task 3 docs, per the plan)
- **Files modified:** 7 (3 created, 4 modified)

BASE2: `8f7e1c9` (HEAD before the plan; 23-01's commit is `e09f834` underneath it).
Commits: `fb97ba2` (Task 2, feat) and `d11af97` (Task 3, docs).

## Accomplishments

- `tests/test_relations.py` (new, 357 lines, 10 tests): imports the standard library, `pydantic`, `pytest`, `spur.params` and `spur.calc` only, so it is in `make verify.fast`. It holds the grammar walk, the JSON Schema keyword collision, the one-path `ast` check, the `Literal` probe, forward parity with the warning names, the refused keyway pair, reverse coverage and three meta-tests.
- `src/spur/params.py` declares the ten relations beside `hub_d`'s: 4 on `bore_hex eq 0`, 3 on `spoke_count gt 0`, 2 on `hole_count gt 0`, 1 on `hex_cell gt 0`. No default, bound, title, unit, step or help text moved. One comment per group carries the constraint; the Bore comment records that the keyway pair is refused, not ignored.
- `tests/test_cli.py`'s schema walk gains the relation check (`enabled_when` in the schema exactly when the model has it, equal to the model's list, every gate a rendered field); its docstring says the walk extends to every relation (L41).
- The idea (`recess_*` under `recess_sides=none`, `bore_flat` at `bore_d=0`) and the debt (the hex bore warns about default `bore_d`/`bore_flat`) are filed with INDEX rows.

## Task Commits

1. **Task 1: the proof module, seen 3 failed / 7 passed** - not committed, by design (the plan commits it with Task 2).
2. **Task 2: declare the ten relations, proofs green, CLI walk, wrong relation seen red** - `fb97ba2` (feat). Files: `tests/test_relations.py` (A), `src/spur/params.py` (M), `tests/test_cli.py` (M).
3. **Task 3: file the idea and the debt** - `d11af97` (docs). Files: the idea (A), the debt (A), `docs/ideas/INDEX.md` (M), `docs/tech_debt/INDEX.md` (M).

**Plan metadata:** the `docs(23-02)` commit that follows this SUMMARY.

## Filed

Item filed in this plan, per CLAUDE.md:

- Idea: `docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md` (row in `docs/ideas/INDEX.md`, `## Open`).
- Debt: `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`, `Severity: nice` (row in `docs/tech_debt/INDEX.md`, `## Active`).

Both carry the plan's text, with the debt's related-file line numbers read by `grep -n` at execution: `src/spur/calc.py:1166`, `src/spur/params.py:102` and `:105`, `tests/test_browser.py:425`. The idea file carries the plan's `ASSUMPTION:` line.

## Seen red

TDD RED for Task 1, against the one-relation model (`hub_d` only). Command and log: `make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q -rf"`, `investigation/23-02-relations-red.log`. Result `3 failed, 7 passed in 0.11s`. Exit 2. The classifier verb `check tdd-red-evidence` was not run: the plan's own `<verify>` (the three named FAILED lines and the result line) is the evidence, and this plan has no committed RED step to feed it.

1. `test_the_keyway_pair_is_refused_under_a_hex_bore_alone_and_together`: `AssertionError: ['keyway_depth', 'keyway_width']` (the `set(relations) >= REFUSED` assertion; the pair is not declared yet).
2. `test_every_field_calc_ignores_is_declared`: `AssertionError: bore_hex=0.05: calc says 'Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored.', naming bore_d, but no relation declares bore_d`.
3. `test_an_ignored_field_without_its_relation_goes_red`: the same `bore_hex=0.05 ... no relation declares bore_d` line, from its first (non-vacuity) call, before the `spoke_fillet` branch is reached.

Semantic assessment: all three failed on the planned assertion for the intended reason (the declared set is incomplete), each target executed, and none is an import, collection or fixture fault. The structural tests, the forward check on `hub_d` and the other meta-tests passed. The first red run was `5 failed, 5 passed` and was a module bug, fixed before the evidence above (see Deviations).

Wrong relation on the real model (Task 2 step 3): `enabled_when=[when("bore_hex", "eq", 0)]` added to `bore_chamfer`, `make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q -rf" > investigation/23-02-wrong-relation-red.log`. Result `1 failed, 9 passed in 0.08s`:

- `AssertionError: bore_chamfer=0.05 with bore_hex=0.05: no warning names bore_chamfer (0.05 mm): calc does not say it is ignored` (the forward test; nothing in `derive()` moves, so only the warning-names check sees it).

Reverted by copying the saved good `params.py` back; `cmp` read identical, and `grep -c 'enabled_when=\[when(' src/spur/params.py` reads 11 again.

## Green readings

`make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q"` reads `10 passed in 0.06s`.

The commit slice, `/usr/bin/time -p make verify.fast`, against L36's 30 s kill (Apple M2 Max, 12 CPUs):

| Reading | `real` | pytest | Load averages (1/5/15 min) | Log |
|---|---|---|---|---|
| before (HEAD `8f7e1c9`, no `test_relations.py`) | 14.85 s | `840 passed in 14.30s` | 4.04 6.72 6.71 | `23-02-fast-before.log` |
| after (relations declared) | 14.92 s | `850 passed in 14.35s` | 2.45 4.69 5.84 | `23-02-fast-after.log` |

The module adds 10 tests and 0.07 s; 15 s of headroom remains under the 30 s kill.

`make verify` exit 0: `1248 passed in 214.84s (0:03:34)`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`; `params.py` 100.00 %. Log: `investigation/23-02-verify.log`, last line `make verify exit 0`.

Targeted: `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -n0 --no-cov -q -k 'every_gear_field_reaches or schema_drives_the_form or openapi_documents or shareable_link_round_trips'"` reads `4 passed`. Browser (`investigation/23-02-browser.log`): `1 passed in 9.83s`, with a reason line for each of the seven cutout fields (`hex_wall`, `hole_circle_d`, `hole_d`, `hub_d`, `rim_wall`, `spoke_fillet`, `spoke_width`), and `step inert fields: 1.15 s`.

`git diff --exit-code` on `tests/regression/pre_v0_2.json` and `tests/regression/golden_requests.json` is empty, and across `fb97ba2` the diff of those two plus `src/spur/calc.py` and `src/spur/static/app.js` is empty.

## Kept logs

All under `.planning/phases/23-conditional-form-fields/investigation/`, untracked until 23-04 (PD-11): `23-02-relations-red.log`, `23-02-wrong-relation-red.log`, `23-02-browser.log`, `23-02-verify.log`, `23-02-fast-before.log`, `23-02-fast-after.log`.

## Decisions Made

None beyond the plan: D-09's set stands as locked, with no row dropped, added or altered. The proof module's constants and checker functions follow the plan's names exactly.

## Deviations from Plan

None to the plan's behaviour. Two small corrections to the Task 1 module before its first accepted red run, both mine and both before the evidence was kept:

**1. [Rule 1 - Bug] `DerivedDimensions.warnings` dumps as a tuple, not a list**
- **Found during:** Task 1 (first red run: `5 failed, 5 passed`, the forward test and the `bore_chamfer` meta-test failing on `isinstance(warnings, list)`)
- **Fix:** accept `list | tuple`
- **Files modified:** `tests/test_relations.py`
- **Verification:** the re-run read `3 failed, 7 passed`
- **Committed in:** `fb97ba2`

**2. [Rule 3 - Blocking] ruff SIM300 on `REFUSED <= set(relations)`**
- **Found during:** Task 1 (`make lint`)
- **Fix:** written as `set(relations) >= REFUSED`
- **Files modified:** `tests/test_relations.py`
- **Verification:** `make lint typecheck` clean; the red log was re-run afterwards and still reads `3 failed, 7 passed`
- **Committed in:** `fb97ba2`

**Total deviations:** 2 auto-fixed (1 bug in the new module, 1 lint). **Impact on plan:** none; both fixed in code that did not exist before this plan.

## Issues Encountered

- `gsd_run` was not a shell function in the executor's shell, so the git-protection query returned "unavailable"; the plan's fallback (the branch `gsd/phase-23-conditional-form-fields` is not one of the five protected names) applied. State updates then used the resolver block.
- The pre-commit hook stashes and restores unstaged files around each commit (`.planning/state.json`, the untracked logs). It restored them each time; nothing was lost.

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path or file access; the changes are schema metadata and tests. T-23-06 (a relation calc does not back) is mitigated by the forward and reverse proofs and the three meta-tests; T-23-07 by the empty `calc.py` and regression diffs; T-23-08 by `REFUSED`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 23-03. The browser step's expected dimmed set now covers seven fields with no test edit, because `expected_inactive()` reads the schema. The one thing to carry forward: `tests/test_relations.py` runs in the commit slice, so any later change to a `calc` "ignored" sentence or to a relation is judged at commit.

## Self-Check: PASSED

- Files: `tests/test_relations.py`, `docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md` and `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` exist; `git show --name-status` on `fb97ba2` and `d11af97` lists exactly the planned paths.
- Commits `fb97ba2` and `d11af97` are ancestors of HEAD; `git rev-list --count 8f7e1c9..HEAD` read 2 before this SUMMARY.
- `make verify` exit 0 with `1248 passed`; both regression files, `calc.py` and `app.js` show an empty diff across the feat commit.

---
*Phase: 23-conditional-form-fields*
*Completed: 2026-10-11*
