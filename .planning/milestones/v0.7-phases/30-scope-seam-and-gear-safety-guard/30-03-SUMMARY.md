---
phase: 30-scope-seam-and-gear-safety-guard
plan: 03
subsystem: infra
tags: [import-linter, module-boundaries, route-pin, regex-belt, fastapi, tomllib]

requires:
  - phase: 30-scope-seam-and-gear-safety-guard
    provides: "30-01: make gear.unchanged, which proves every edit here left the gear alone; 30-02: L46 (5d61f8e), which must precede the first shaft module (D-20)"
provides:
  - "five docstring-only shaft modules under the frozen D-13 names, flat in src/spur/"
  - "src/spur/parts.py: Part = GearParams, imported by nothing until 30-04"
  - "five import-linter contracts (C1 to C5), ten kept in all, the five existing ones byte-identical"
  - "tests/test_seam.py: contract-name existence guard, three regex belts, route-table pin, query-key pin"
  - "bench/RESULTS.md: nine rows in Seen red once (Phase 30), each with a kept log"
affects: [30-04, 30-05, 31, 32, 33, 34]

plan_head_before: 85c5e7a808247414c960c7a096b8360115bd3e62
plan_head_after: 77f41feea0b8275fc515c7f1b0241419800f71ac

actuals:
  tokens: 22700   # chars/4 over `git diff 85c5e7a HEAD` (90855 chars, the ten kept logs included), before this SUMMARY
  tasks: 3
  commits: 2      # MEASURED: git rev-list --count 85c5e7a808247414c960c7a096b8360115bd3e62..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "a contract is paired with a line-based regex belt that also catches the `from . import name` shape, and the belt's helper is proved on both sides (shapes it must catch, longer names it must let through) inside the first belt test"
    - "tomllib reads the contracts back so the existence guard stays in step with pyproject.toml, closing import-linter's silent acceptance of a missing forbidden module"
    - "the route pin reads app.routes and app.openapi() only and fails on a route of an unexpected type instead of skipping it"

key-files:
  created:
    - src/spur/parts.py
    - src/spur/shaft_params.py
    - src/spur/shaft_calc.py
    - src/spur/din5480.py
    - src/spur/din5480_tables.py
    - src/spur/shaft_model.py
    - tests/test_seam.py
  modified:
    - pyproject.toml
    - bench/RESULTS.md

key-decisions:
  - "C5 'The shaft maths copies the gear maths, never imports it' (CONTEXT D-14 item 6, chosen by the human at plan-phase) is what covers REQ-shaft-routes-separate's 'no gear maths': direct imports of spur.calc only, allow_indirect_imports = true set explicitly, because shaft_params is expected to import spur.params and params imports calc inside its validators"
  - "C2 carries no allow_indirect_imports key and import-linter 2.15's default is false, so it forbids indirect imports too; 30-RESEARCH Pattern 1's note that the default allows indirect is wrong and is not repeated in any comment"
  - "Phase 32 handoff: when model.py first imports shaft_model statically, that same commit adds ignore_imports = [\"spur.model -> spur.shaft_model\"] to C3; it errors with 'No matches for ignored import' if added before the edge exists. It is recorded as a comment in C3's why-block, not as a key"

patterns-established:
  - "A guard counts after it was seen red: nine reds of five contracts, three belts, the existence guard and both route pins, each log kept under the phase's investigation folder"

requirements-completed: [REQ-shaft-routes-separate]

coverage:
  - id: D1
    description: "Five shaft modules exist flat in src/spur/ under the D-13 names, each exactly one docstring; parts.py holds the plain assignment Part = GearParams"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: other
        ref: "AST check printed 'docstring-only: 5 of 5 []'; make no-fake-done, ruff and mypy clean; grep -c '^Part = GearParams$' src/spur/parts.py (1)"
        status: pass
      - kind: unit
        ref: "tests/test_seam.py#test_every_module_a_contract_names_exists_and_the_layout_is_frozen"
        status: pass
    human_judgment: false
  - id: D2
    description: "make lint-imports reads 'Contracts: 10 kept, 0 broken.': the five existing contracts unchanged (0 lines deleted from pyproject.toml) plus C1 to C5"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: other
        ref: "make lint-imports (30-03-green.log); make verify's Contracts line"
        status: pass
    human_judgment: false
  - id: D3
    description: "A mistyped or missing module name in any contract fails a test, although import-linter accepts a missing forbidden module"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: unit
        ref: "tests/test_seam.py#test_every_module_a_contract_names_exists_and_the_layout_is_frozen"
        status: pass
      - kind: other
        ref: "bench/RESULTS.md Seen red once (Phase 30), the 30-03 existence row, log 30-03-red-existence.log (lint-imports stayed 10 kept; the test failed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Regex belts for C1, C2, C5 (one belt over the four shaft-maths files), C3 and C4, each catching the `from . import name` shape"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: unit
        ref: "tests/test_seam.py#test_the_shaft_maths_imports_no_kernel_no_solid_no_logger_and_no_gear_maths"
        status: pass
      - kind: unit
        ref: "tests/test_seam.py#test_only_model_may_import_the_shaft_solid"
        status: pass
      - kind: unit
        ref: "tests/test_seam.py#test_the_gear_maths_imports_no_shaft_module"
        status: pass
    human_judgment: false
  - id: D5
    description: "The /api/ route set contains the v0.6 four exactly, every other /api/ route is under /api/shaft/, nothing outside /api/ is added; the gear routes take the v0.6 query keys"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: unit
        ref: "tests/test_seam.py#test_every_route_beyond_v0_6_lives_under_the_shaft_prefix"
        status: pass
      - kind: unit
        ref: "tests/test_seam.py#test_the_gear_routes_take_the_v0_6_query_keys"
        status: pass
    human_judgment: false
  - id: D6
    description: "Each new contract and test was seen red once against a deliberate violation, reverted with a clean diff, and recorded with its first failure line"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: other
        ref: "bench/RESULTS.md: grep -c '^| 30-03 |' (9); logs 30-03-red-*.log (9); the RESULTS commit changed no file under src, tests or pyproject.toml and deleted 0 lines of RESULTS.md"
        status: pass
    human_judgment: false
  - id: D7
    description: "The wall commit descends from the L46 commit (D-20)"
    requirement: REQ-shaft-routes-separate
    verification:
      - kind: other
        ref: "git merge-base --is-ancestor 5d61f8e bdf224d (exit 0)"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-23
status: complete
---

# Phase 30 Plan 03: The shaft wall Summary

**Five docstring-only shaft modules, `parts.py` and five import-linter contracts (10 kept) put in force before any shaft code, paired with three regex belts, a contract-name existence guard and a route and query-key pin, each seen red once**

## Performance

- **Duration:** about 10 min (start about 2026-10-23T16:12Z, end 2026-10-23T16:22Z); the full `make verify` was 3 min 27 s of it
- **Tasks:** 3
- **Files modified:** 9 source/doc files plus 10 logs

## Accomplishments

- The five placeholders (`shaft_params`, `shaft_calc`, `din5480`, `din5480_tables`, `shaft_model`) are one docstring each, and every docstring says which phase fills the file and why it exists first. The AST check read `docstring-only: 5 of 5 []`, and `make no-fake-done`, ruff and mypy are clean. Coverage lists each as `0 0 0 0 100.00%`; `parts.py` reads 0 of 2 statements until 30-04 imports it, and the total is 97.88 %, above the floor of 96.
- `parts.py` holds `Part = GearParams` as a plain assignment (UP040 would rewrite a `TypeAlias`, a `type` statement cannot take `isinstance`).
- Five contracts were appended after the last existing one. C1 and C2 and C5 have the four shaft-maths modules as sources; C3's sources are app, cli, pool, records and parts; C4's are calc and params. `make lint-imports` reads `Contracts: 10 kept, 0 broken.` and `pyproject.toml` lost 0 lines.
- `tests/test_seam.py` has six tests: the existence guard (which also pins the six D-13 names and a flat layout), one belt over the shaft maths for C1, C2 and C5, a belt each for C3 and C4, the route-table pin and the query-key pin. The first belt also proves its helper on both sides: it catches `import model`, `import spur.model`, `from model import`, `from .model import`, `from spur.model import`, `from . import model`, `from . import params, model`, `from spur import model` and an indented one, and lets `shaft_model`, `params` and `models` through.
- Nine deliberate breaks, each reverted (`git checkout -- <file>`, `git status --porcelain -- src pyproject.toml` empty), each with a row in `### Seen red once (Phase 30)` and a log. The two that are not obvious from the name: the existence row records that `make lint-imports` still read `10 kept, 0 broken` with a mistyped forbidden module while the test failed; the query-key row records that `make gear.unchanged` stayed green with a stray `part` field on `ModelQuery`, so only the pin sees a stray key on a gear route.

## Task Commits

1. **Tasks 1 and 2: the five placeholders, `parts.py`, the contracts and `tests/test_seam.py`** - `bdf224d528e53accd58b7a24b3908395faddf047` (feat). One commit, as the plan directs; the stat lists the five placeholders, `parts.py`, `pyproject.toml` and `tests/test_seam.py`. It descends from the L46 commit `5d61f8e` (`git merge-base --is-ancestor` exit 0), so D-20 holds. **This is the wall commit sha that 30-05's order check uses.**
2. **Task 3: nine rows and ten logs** - `77f41feea0b8275fc515c7f1b0241419800f71ac` (docs)

**Plan metadata:** the `docs(30-03)` commit that adds this file, STATE.md, ROADMAP.md and REQUIREMENTS.md.

## Files Created/Modified

- `src/spur/shaft_params.py`, `shaft_calc.py`, `din5480.py`, `din5480_tables.py`, `shaft_model.py` - docstring-only, frozen names (D-13)
- `src/spur/parts.py` - `Part = GearParams`
- `pyproject.toml` - five `[[tool.importlinter.contracts]]` tables, 67 lines added, 0 deleted
- `tests/test_seam.py` - six tests
- `bench/RESULTS.md` - nine rows appended (9 added, 0 deleted)
- `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-03-green.log` and nine `30-03-red-*.log`

## Decisions Made

- C5 (human-chosen at plan-phase, CONTEXT D-14 item 6) is the contract that covers REQ-shaft-routes-separate's "no gear maths". It forbids direct imports of `spur.calc` only, with `allow_indirect_imports = true` set explicitly, because import-linter's default is false and `shaft_params` is expected to import `spur.params`, which imports calc inside its validators.
- C2 has no `allow_indirect_imports` key, so it forbids indirect imports too (import-linter 2.15's default is false, read in the venv). 30-RESEARCH's contrary note was not repeated.
- C1's `cadquery` failure in the `from . import model` red is the indirect path `shaft_calc -> model -> cadquery`, which the contract forbids because its indirect flag is off. That is the stricter form the human accepted (D-14).
- Phase 32 handoff, carried in C3's why-comment: add `ignore_imports = ["spur.model -> spur.shaft_model"]` to C3 in the same commit that first imports `shaft_model` in `model.py` (30-RESEARCH Pitfall 4: `cli -> model -> shaft_model` breaks C3 otherwise; adding the key earlier errors with "No matches for ignored import"). ROADMAP Phase 32 already names it (30-02).

## Deviations from Plan

**1. [Process] The plan commit ledger (task_commit_protocol 0c) was not written before the first commit**
- **Found during:** SUMMARY
- **Issue:** `.git/gsd-plan-head-before-30-03` does not exist.
- **Fix:** `plan_head_before` is `85c5e7a`, the parent of the wall commit and the HEAD at the start (`git log` shows `bdf224d` directly on it), and `commits:` is measured from it: `git rev-list --count 85c5e7a..HEAD` printed 2.
- **Files modified:** none

**2. [Test count] The helper's shape check sits inside the first belt test, not in a seventh test**
- **Found during:** Task 2
- **Issue:** the plan fixes the count at six tests (`grep -c '^def test_'` prints 6, `6 passed`), and a separate test proving the helper would be a seventh.
- **Fix:** the first belt test asserts the helper's behaviour on both sides before it reads the files.
- **Files modified:** `tests/test_seam.py`

**3. [Instruction conflict] Commit trailer**
- The session's attribution reminder names `Claude Sonnet 5.5`; both commits carry it, as 30-01's and 30-02's do.

**Total deviations:** 0 auto-fixed, 1 process note, 1 test-structure note, 1 instruction conflict. **Impact:** none on the wall or its proofs.

## Issues Encountered

- The `30-03-green.log` holds the whole `make lint-imports` output (it was written with `tee` before the commit), not only the count the plan's one-liner prints.
- A line-based belt cannot see a parenthesised multi-line `from . import (` list. The helper's docstring says so; the contract catches that shape.
- The pre-commit hook ran `make verify.fast` (with `gear.unchanged`) on both commits and passed.
- No item was filed under `docs/tech_debt/` or `docs/ideas/`.

## Known Stubs

None. The five placeholders hold no statement; they are the contract targets D-12 requires, not stubs of a feature.

## Threat Flags

None. No endpoint, auth path or schema change; the tests only read the route table.

## User Setup Required

None - no external service configuration required.

## Verification

- `make verify`: exit 0, `1368 passed in 205.48s (0:03:25)`, `Contracts: 10 kept, 0 broken.`, `Required test coverage of 96.0% reached. Total coverage: 97.88%` (1-minute load about 10 at the end, a busy host).
- `make lint-imports`: `Contracts: 10 kept, 0 broken.`; `tests/test_seam.py`: `6 passed`; `make gear.unchanged` green after the wall commit and after the last revert (8723 bytes, byte-equal to v0.6).
- `git diff --exit-code v0.6 -- src/spur/calc.py src/spur/params.py src/spur/model.py tests/regression/ .github/workflows/ci.yml requirements.txt` empty.
- Plan acceptance re-run: 10 contract tables, the five names appear once each, C5's `allow_indirect_imports = true` count 1, C3's handoff a comment (`^#.*ignore_imports` 1, `^ignore_imports *=` 0), `Part = GearParams` count 1, six tests, 9 `| 30-03 |` rows, 6 logs with `is not allowed to import`, the existence log holds `10 kept, 0 broken` and a `failed` line, route and query-key logs each hold `1 failed`, the query-key log holds the `are byte-equal to v0.6` line, the RESULTS commit's diff over `src pyproject.toml tests` is empty.

## Next Phase Readiness

30-04 can import `Part` from `parts.py` in its first commit, switch the annotations, and move `_serve_model`; every such edit is covered by C3 (the pool, records and parts may not name `shaft_model`), C4 (calc and params may not name `parts`), the route pin and `make gear.unchanged`. 30-05 checks the order with `5d61f8e` (L46) and `bdf224d` (the wall) and records the gate delta. Phase 31 widens `Part` in one line of `parts.py` and fills the four maths modules under C1, C2 and C5.

## Self-Check: PASSED

Files found: `src/spur/parts.py`, the five placeholders, `tests/test_seam.py`, ten `30-03-*.log` files. Commits found in HEAD: `bdf224d`, `77f41fe`.

---
*Phase: 30-scope-seam-and-gear-safety-guard*
*Completed: 2026-10-23*
