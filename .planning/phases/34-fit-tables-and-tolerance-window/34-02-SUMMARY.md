---
phase: 34-fit-tables-and-tolerance-window
plan: 02
subsystem: shaft
tags: [din5480, tables-loader, pydantic, invariants, private-file, fixtures]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-01: /private/ ignored by git and Docker, gate baseline, reading toolchain"
provides:
  - "src/spur/din5480_tables.py: strict pydantic schema with provenance on every row, `problems()` invariants including the load-time M1 identity, a once-per-process `active()` / `install()` / `reset()`, `canonical()`, and the size and Table 7 fit lookups"
  - "tests/din5480_tables_fixture.py: `text()`, `build()`, `write(path)`, invented filler plus only the approved anchors"
  - "tests/conftest.py: autouse `_no_table_file` and the `with_tables` fixture"
  - "Two red logs showing each invariant and each guard failing once"
affects: [34-03, 34-04, 34-05, 34-06, 34-07, 34-08, 34-09, 34-10, 34-11, 34-12, 34-13, 34-14, 34-15, 34-16, 34-17]

actuals:
  tokens: 13700   # chars/4 over the six files this plan changed (54,788 chars: module 18,214, fixture 4,195, tests 17,724, conftest 3,037, two logs 7,619)
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Process-wide tables as lazily loaded module state: a failed load is cached and re-raised, not retried"
    - "Refusals name row kind, key, field and pages, never a value (pydantic `errors(include_input=False)`)"
    - "Repository guards that need git skip when the tree has no .git (make test-image mounts src and tests only)"

key-files:
  created:
    - tests/din5480_tables_fixture.py
    - tests/test_din5480_tables.py
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-02-red-invariants.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-02-red-guards.log
  modified:
    - src/spur/din5480_tables.py
    - tests/conftest.py

key-decisions:
  - "The size-to-column edge is `d_b_over_mm < d_B <= d_b_upto_mm` ([ASSUMED], 34-RESEARCH A1), in one function, `_columns_selecting`, so 34-16 can reverse it without touching a read"
  - "A failed load is cached: `active()` re-raises a fresh TablesError with the same text on every call and never re-reads"
  - "The repository guard tests skip when there is no git checkout (the test image has neither git nor the ignore files)"

requirements-completed: [REQ-tables-private-file, REQ-tables-transcribed-twice]

coverage:
  - id: D1
    description: "`active()` reads SPUR_DIN5480_TABLES once per process; unset or empty is None; `install` sets the state without the environment; a broken file is a cached TablesError naming the path"
    requirement: REQ-tables-private-file
    verification:
      - kind: test
        ref: "tests/test_din5480_tables.py#test_the_file_is_read_once_per_process"
        status: pass
      - kind: test
        ref: "tests/test_din5480_tables.py#test_a_broken_file_is_an_error_on_every_call_and_is_read_once"
        status: pass
      - kind: test
        ref: "tests/test_din5480_tables.py#test_install_sets_the_state_without_reading_the_environment"
        status: pass
    human_judgment: false
  - id: D2
    description: "Each structural invariant (T_G sum, micrometre and millimetre ranges, duplicate keys, provenance, column and row indices, one column per size, the M1 identity at exactly 0.0005 and 0.0005 + 2e-9) refuses a broken row, and was seen red once"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: test
        ref: "tests/test_din5480_tables.py#test_a_broken_row_refuses_to_load (24 ids)"
        status: pass
      - kind: other
        ref: "investigation/34-02-red-invariants.log: with problems() disabled, 16 cases fail DID NOT RAISE, the 8 type and encoding cases still pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "`Tables.fit` returns A_s, T_G, T_act, T_eff from the one column the module and d_B select; the d_B edge falls in the range it closes; letters and classes come from the file"
    requirement: REQ-tables-private-file
    verification:
      - kind: test
        ref: "tests/test_din5480_tables.py -k 'edge or column or fit or letters'"
        status: pass
    human_judgment: true
    rationale: "The edge reading (x < d_B <= y) is an assumption the human confirms or reverses at 34-15; the tests prove the code does what it says, not that DIN means it"
  - id: D4
    description: "private/ is ignored by git and Docker and no tracked JSON validates as a Tables document, each guard seen red"
    requirement: REQ-tables-private-file
    verification:
      - kind: test
        ref: "tests/test_din5480_tables.py#test_the_private_directory_is_ignored_by_git_and_by_docker, #test_no_tracked_json_file_is_a_table_file"
        status: pass
      - kind: other
        ref: "investigation/34-02-red-guards.log: three failures (.gitignore line removed, .dockerignore line removed, a tracked renamed copy)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every test starts with the variable deleted and the loader reset; `with_tables` installs the synthetic tables and empties the solid and export caches of modules already imported"
    requirement: REQ-tables-private-file
    verification:
      - kind: test
        ref: "tests/test_din5480_tables.py#test_with_tables_installs_the_tables_and_empties_the_caches"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-10-30
status: complete
plan_head_before: 315d8c10721c670fc60fe852b04c05202f5df3f0
plan_head_after: bf62f1dc9a4c820b9599076174ebe19c8d962d1d
commits: 3
---

# Phase 34 Plan 02: The table loader, its invariants and the synthetic fixture Summary

**One checked, process-wide `Tables` object read once from `SPUR_DIN5480_TABLES`, with a strict pydantic schema, provenance on every row, a load-time M1 identity against `din5480.measure_over_pins`, and exact-key size and Table 7 fit lookups, all tested against a synthetic fixture that carries no value beyond the approved anchors.**

## Performance

- **Duration:** 6 min (2026-10-30T13:33:51Z to 13:39:57Z)
- **Tasks:** 3 of 3
- **Files:** 2 modified, 4 created (plus the two red logs)
- **Tests:** `tests/test_din5480_tables.py` has 53 tests

## Accomplishments

- `din5480_tables.active()` returns None for an unset or empty `SPUR_DIN5480_TABLES`, otherwise reads, validates and caches the file once; a refusal is cached too and re-raised on every call (D-02, D-04, D-13). `install(t)` sets the state for a build worker, `reset()` is for tests.
- `parse()` scans the raw text for U+2212 and U+2013 (naming the line), validates with strict pydantic models, then runs `problems()`. Refusals are `loc` plus error `type`, or a row kind, key, field and pages; never `input_value`.
- The load-time M1 identity: every size row's printed M1 is checked against `measure_over_pins(m, z, tooth_thickness(m, profile_shift(d_B, m, z) * m), pin_d_mm)` within `M1_TOLERANCE = 0.0005 + 1e-9`. The boundary pair accepts exactly 0.0005 and refuses 0.0005 + 2e-9.
- `Tables.fit(module, reference_d, fit)` returns `FitTolerance(a_s_um, t_g_um, t_act_um, t_eff_um)` from the single column `column_for` selects, or None; `letters` and `tolerance_classes` are read from the file.
- `make verify.fast`: `2367 passed in 13.93s` (wall 15.1 s, under the 30 s bar); `make lint-imports`: `Contracts: 10 kept, 0 broken.`

## The schema as built

All models are `frozen`, `extra="forbid"`, `strict`; every float is `allow_inf_nan=False`; micrometre fields are `int`.

| Model | Fields |
|---|---|
| `Provenance` | `part` (1 or 2), `clause`, `table`, `pages` (tuple of int, at least one) |
| `SizeRow` | `provenance`, `module`, `reference_d`, `teeth` (>= 1), `pin_d_mm`, `m1_mm`, `form_d_max_mm`; `key` = `(module, reference_d, teeth)` |
| `DeviationRow` | `provenance`, `letter` (`^[a-z]$`), `a_s_um` (tuple of int) |
| `ClassRow` | `provenance`, `tolerance_class` (1..99), `row_by_column` (tuple of int) |
| `ToleranceRow` | `provenance`, `row` (>= 1), `t_g_um`, `t_act_um`, `t_eff_um` |
| `ColumnRow` | `provenance`, `module_min_mm`, `module_max_mm`, `d_b_over_mm` or None, `d_b_upto_mm` or None, `column` (>= 1) |
| `Tables` | `schema_version` (Literal 1), `sizes`, `deviations`, `classes`, `tolerances`, `columns` (tuples) |
| `FitTolerance` | NamedTuple `a_s_um, t_g_um, t_act_um, t_eff_um` |

Constants: `ENV_VAR`, `SCHEMA_VERSION = 1`, `MAX_FILE_BYTES = 4 MiB`, `UM_LIMIT = 1000`, `M1_TOLERANCE`, `PART_2_MODULES` (16), `TABLE_7_PROVENANCE`. Functions: `part_2_provenance`, `problems`, `parse`, `load_file`, `active`, `install`, `reset`, `canonical`; methods `size`, `column_for`, `fit`; properties `letters`, `tolerance_classes`.

## The invariant list (`problems()`)

Per size row: module is one of the 16; provenance equals `part_2_provenance(module)`; `0 < pin_d_mm < reference_d`; `0 < form_d_max_mm < reference_d`; `m1_mm > 0`; M1 computable and within `M1_TOLERANCE` of the formula; when `columns` is not empty, exactly one column row selects the size. Per tolerance row: `T_G == T_act + T_eff`; micrometre fields within `UM_LIMIT`. Per deviation row: micrometre fields within `UM_LIMIT`; one column count. Per class row: that column count; every `row_by_column` value names an existing tolerance row. Per column row: module bounds ordered and in `PART_2_MODULES`; `d_b_over_mm < d_b_upto_mm` when both set; `column` within 1..n. Provenance of every Table 7 row is `TABLE_7_PROVENANCE`. Unique keys in each of the five row kinds. Encoding, type, NaN and inf, and unknown keys are refused by the raw scan and by pydantic. File level: regular file, size cap (exact at `MAX_FILE_BYTES`, refused one byte over), non-empty, UTF-8.

Completeness (721 size rows, 18 letters, 8 classes, 24 tolerance rows, 21 column rows) is deliberately not a load-time check; a document of empty row tuples loads (34-03 `check --complete`).

## Seen red

| Plan | Test id | Deliberate break | First failure line | Restored |
|---|---|---|---|---|
| 34-02 | `test_a_broken_row_refuses_to_load[t_g sum off by one]` | `problems()` returns `[]` at its first line | `Failed: DID NOT RAISE TablesError` (tests/test_din5480_tables.py:215) | yes |
| 34-02 | `[deviation over the micrometre limit]` | same | same | yes |
| 34-02 | `[pin typed in micrometres]` | same | same | yes |
| 34-02 | `[form diameter at d_B]` | same | same | yes |
| 34-02 | `[duplicate size]`, `[duplicate deviation]`, `[duplicate class]`, `[duplicate tolerance row]`, `[duplicate column row]` | same | same | yes |
| 34-02 | `[clause changed]` | same | same | yes |
| 34-02 | `[column index beyond the last]` | same | same | yes |
| 34-02 | `[row_by_column naming no row]` | same | same | yes |
| 34-02 | `[default size has no column]`, `[two columns select the default size]` | same | same | yes |
| 34-02 | `[M1 plus a thousandth]`, `[pin plus a hundredth]` | same | same | yes |
| 34-02 | `test_the_m1_identity_refuses_a_hair_beyond_half_a_printed_digit` | same | `Failed: DID NOT RAISE TablesError` (:269) | yes |
| 34-02 | `test_the_private_directory_is_ignored_by_git_and_by_docker` | `/private/` line removed from `.gitignore` | `AssertionError: private/din5480-tables.json`, `assert 1 == 0` (:387) | yes, `git diff` empty, `git check-ignore` exits 0 |
| 34-02 | same test | `private` line removed from `.dockerignore` | `AssertionError: assert 'private' in [...]` (:388) | yes |
| 34-02 | `test_no_tracked_json_file_is_a_table_file` | a copy of the synthetic document tracked at `tests/_seen_red_tables.json` | `Failed: DID NOT RAISE ValidationError` (:399) | yes, `git rm --cached` and deleted, never committed |

The disabled-checker run had 16 `DID NOT RAISE` plus the boundary test, and 9 passes: the 8 cases pydantic or the raw scan refuse (the two minus signs, NaN, `1e999`, three int-type cases, the unknown key) and `test_a_broken_file_is_an_error_on_every_call_and_is_read_once` (the file `{` is not JSON). The log is `investigation/34-02-red-invariants.log`; the guards are in `34-02-red-guards.log`.

## The synthetic fixture's provenance of every number

`tests/din5480_tables_fixture.py`: the four DIN 5480-2 rows (W 25x1.25x18, W 26x1.25x19, W 30x2x14, W 30x2x13) carry their approved D_M and M1 from `tests/test_din5480_anchors.py`; the W 120x3x38 row carries Part 1 Fig. 6's gauge pin 6.000 and d_Ff1 max 113.91 (approved) and an M1 computed by `measure_over_pins` at that pin and the nominal thickness. `form_d_max_mm` of the four Part 2 rows is `round(form_diameter(...) - 0.05 * m, 2)`, invented by formula. Table 7 is invented whole: three columns, letters f h k, classes 7 8 9, five tolerance rows from `t_eff = 6 + 4r`, `t_act = 9 + 6r`, `t_g` their sum. No number was read from, or compared to, the private file.

## Task Commits

1. **Task 1 (tracer): load once per process** - `4f3ab8e`
2. **Task 2: structural invariants, each seen red** - `e4437c2`
3. **Task 3: Table 7 lookup, guards, `with_tables`** - `bf62f1d`

**Tracer gate:** the tracer's `<verify>` carries only `<automated>` commands and was green after its commit (6 passed, ruff, mypy, 10 contracts kept, no-fake-done and gear.unchanged exit 0), so the plan expanded without a checkpoint.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The repository guards cannot run inside `make test-image`**
- **Found during:** Task 3
- **Issue:** `make test-image` mounts only `src`, `tests`, `bench`, `scripts` and `pyproject.toml`; the image has no `git` and no `.gitignore` or `.dockerignore`, so `git check-ignore` and `git ls-files` would error there. `tests/test_hooks.py` pins that recipe, so the recipe was not edited.
- **Fix:** the two guard tests carry `pytest.mark.skipif` on "no git binary or no `.git` at the repository root". They run in the checkout and in CI.
- **Files modified:** tests/test_din5480_tables.py
- **Verification:** both tests pass here; both seen red (above).
- **Committed in:** `bf62f1d`

**2. [Rule 1 - Bug] Lint: ambiguous minus characters, an unused `noqa`, a `None`-not-last union**
- **Found during:** Task 1
- **Fix:** the two minus characters are written `chr(0x2212)` and `chr(0x2013)`; the `noqa: PLW0603` directives were removed (the rule is not enabled); `_state` is typed `Tables | TablesError | object | None`.
- **Committed in:** `4f3ab8e`

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug). **Impact on plan:** none on scope.

### Process disclosures (TDD)

- Task 1's RED was a collection `ImportError` (the module held only its docstring), which the TDD reference classes as invalid RED, not a failing assertion. The tracer's behaviours were green on the first run after the module was written.
- Task 2's tests went green on first run; their red evidence is the disabled-`problems()` run above, which is the plan's stated method.
- Task 3's lookup tests (`fit`, `column_for`, `letters`, `tolerance_classes`) were written together with the code and were not watched failing; only the two repository guards were seen red. The lookups are small, exact comparisons, and a regression in them would fail the edge and fit tests, but they are not "seen red once".

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. The only new surface is the operator-named file in `SPUR_DIN5480_TABLES`, which is T-34-04 to T-34-09 of this plan's threat model (cap, regular file only, strict schema, cached refusal, value-free messages).

## Debt and ideas

None filed.

## Issues Encountered

- A pre-commit hook stashes unstaged files during each commit (its own patch under `~/.cache/pre-commit`); the user's uncommitted `.planning/state.json` change was restored each time and was never staged.
- The two skipped-in-image guards mean `make test-image` does not exercise the ignore rules; CI and `make verify` do.

## Next Phase Readiness

34-03 can write its tooling against `Tables`, `canonical`, `parse` and `problems`; 34-05 can hand `active()` to the pool through `install`; 34-08 to 34-13 write reads in the field names above. The A1 edge convention sits in `_columns_selecting` for 34-15 and 34-16. No blocker.

## Self-Check: PASSED

- FOUND: the module, fixture, test file, conftest and both red logs
- FOUND: commits `4f3ab8e`, `e4437c2`, `bf62f1d` (`git merge-base --is-ancestor` exit 0); `git rev-list --count 315d8c1..HEAD` prints 3
- `git ls-files private/` prints nothing; `git check-ignore -q private/din5480-tables.json` exits 0; `tests/_seen_red_tables.json` is not tracked
- `pytest tests/test_din5480_tables.py tests/test_seam.py`: 61 passed; `make lint-imports`: `Contracts: 10 kept, 0 broken.`; `make verify.fast`: 2367 passed

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
