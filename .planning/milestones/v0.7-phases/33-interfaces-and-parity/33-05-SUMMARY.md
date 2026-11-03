---
phase: 33-interfaces-and-parity
plan: 05
subsystem: cli
tags: [argparse, shaft, din5480, designation, parity, decision-log, l49]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-04's SPLINE_KEYS, DesignationConflict, designation_clash, clash_message, resolve_shaft and the /api/shaft/ routes"
provides:
  - "spur shaft info and spur shaft export (-o required, --format, --quality, the eight ShaftParams flags, --designation)"
  - "help group 'shaft parameters (defaults in brackets)'; the gear group and help unchanged"
  - "tests/shaft_parity.py: SHAFTS, cli_argv, displayed, differences, web_rows (the one fixed set 33-08 reuses)"
  - "tests/test_shaft_parity.py: API = CLI raw-equal over the fixed set, the download name, the comparator self-test"
  - "L49 paragraphs The shaft's CLI and One shaft, three readers; a Seen-red row for 33-05"
affects: [33-06, 33-07, 33-08, 33-09]

actuals:
  tokens: 7951   # chars/4 over every added or removed line of the three commits since d3240a4 (31804 chars); the estimate of 75000 counted reads
  tasks: 3
  commits: 3
plan_head_before: d3240a41488cc627138f0579e5de2bc7163f1212
plan_head_after: 6e6ec80a686da65a126a78ccfeaaf1a18744ad19

tech-stack:
  added: []
  patterns:
    - "the CLI resolves a designation through the same resolve_shaft the API calls, and judges a clash on which flags were given, so the two refuse the same requests with one sentence"
    - "one fixed set of parameter dicts in a tests/ helper module, read by the API, CLI and browser comparisons; API = CLI is raw equality, web = API is the displayed text"
    - "a comparator is proved by a durable self-test on a one-ulp change, and the comparison by one recorded red"

key-files:
  created:
    - tests/shaft_parity.py
    - tests/test_shaft_parity.py
    - .planning/phases/33-interfaces-and-parity/investigation/33-05-red-perturbed.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-05-verify.log
  modified:
    - src/spur/cli.py
    - tests/test_cli.py
    - README.md
    - docs/architecture/cli.md
    - docs/architecture/decision_log.md
    - bench/RESULTS.md

key-decisions:
  - "A ValidationError under --designation is printed at 'designation' for the model's own refusal and for a spline field, and at the solid field's own name for a bound on it, which is where the API's 422 puts each (checked against the API in a test)"
  - "The CLI's shaft imports (din5480, shaft_calc, shaft_params) sit at the top of cli.py; only model stays lazy, so spur shaft info does not load OpenCascade"

patterns-established:
  - "test names that must be selected by a plan's -k filter carry the filter word (the second tracer test says 'shaft')"

requirements-completed: [REQ-shaft-cli, REQ-shaft-parity, REQ-designation-input]

coverage:
  - id: D1
    description: "spur shaft info prints the document /api/shaft/info answers, for defaults, flags and a designation, in ShaftDimensions key order"
    requirement: REQ-shaft-cli
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_shaft_document"
        status: pass
    human_judgment: false
  - id: D2
    description: "spur shaft export writes the STEP or STL through model.export, warns on stderr, has no default output name, and every refusal exits 2 with no file"
    requirement: REQ-shaft-cli
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_shaft_export_writes_the_step_and_the_stl_and_warns_on_stderr"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_a_refused_shaft_exits_2_and_writes_no_file"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_a_shaft_build_error_exits_nonzero_and_writes_no_file"
        status: pass
    human_judgment: false
  - id: D3
    description: "a designation beside a spline flag, an unreadable, empty or infeasible designation, and a solid field out of bounds read on the CLI as the API's 422 reads them"
    requirement: REQ-designation-input
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_a_shaft_designation_with_a_spline_flag_exits_2_like_the_api_422"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_a_shaft_refusal_reads_the_same_on_the_api_and_the_cli"
        status: pass
    human_judgment: false
  - id: D4
    description: "shaft help lists every ShaftParams field plus --designation under its own group; the gear help is unchanged; the README's shaft lines run"
    requirement: REQ-shaft-cli
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_every_shaft_field_is_a_flag_under_its_own_group_and_the_gear_help_is_unchanged"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_readme_shaft_examples_run"
        status: pass
      - kind: other
        ref: "make gear.unchanged; make lint-imports (Contracts: 10 kept, 0 broken.)"
        status: pass
    human_judgment: false
  - id: D5
    description: "API and CLI print one document, and the API names the download by the slug, over the fixed set of four shafts; the comparison goes red on a one-ulp change"
    requirement: REQ-shaft-parity
    verification:
      - kind: unit
        ref: "tests/test_shaft_parity.py#test_the_api_and_the_cli_print_one_shaft_document"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_parity.py#test_the_download_is_named_by_the_slug"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_parity.py#test_the_comparison_sees_a_one_ulp_change_and_a_changed_name"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 05: The shaft CLI and the API = CLI parity Summary

**`spur shaft info|export` serve the same shaft as the API through the API's own `resolve_shaft`, and a parity test over a fixed four-shaft set proves one document and one download name, seen red on a one-ulp change to `tip_d`**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-27T16:52:00Z (approximate, not captured at start)
- **Completed:** 2026-10-27T17:04:00Z
- **Tasks:** 3
- **Files modified:** 10 (6 modified, 4 created)

## Accomplishments

- `spur shaft info` prints `derive_shaft(...).model_dump_json(indent=2)`, equal as parsed JSON and in key order to `/api/shaft/info` for defaults, for `--reference-d 30 --module 2 --teeth 14` and for `--designation "W 30x2x14x8f"`.
- `spur shaft export -o FILE` (`--format`, `--quality`, no default name) writes through `model.export` after the build returns, prints `wrote ...` and each warning to stderr. Refusals: a spline flag beside `--designation` (the API's `conflict` sentence), an empty, unreadable or infeasible designation, and a bound on a solid field exit 2 with no file; a `BuildError` exits 1 with `error: `.
- Help: `shaft parameters (defaults in brackets):` lists the eight `ShaftParams` flags in model order and `--designation`; the gear group and help are untouched. `cli.py` imports no `app`, `fastapi`, `starlette` or `shaft_model` (10 contracts kept).
- `tests/shaft_parity.py` holds the one fixed set (`default`, `w30x2x14`, `odd-z`, `no-shank-no-chamfer`) and the readers `cli_argv`, `displayed` (the port of `fmt()`), `differences` and `web_rows` that 33-08 reuses. `tests/test_shaft_parity.py` asserts API = CLI raw-equal with ordering and nulls, and the `Content-Disposition` name equal to `ShaftParams.slug()` plus the suffix; no tolerance (`grep -cE 'approx|isclose|rel=|abs='` prints 0).
- The red (SC3): `cmd_shaft_info` printing `tip_d` one ulp up (`math.nextafter`) failed all four shafts: `E       AssertionError: assert ['tip_d: 24.7...004 != 24.75'] == []`, `4 failed, 13 passed`, log `investigation/33-05-red-perturbed.log`; reverted (`git diff HEAD -- src/spur/cli.py` empty) and the row is in `bench/RESULTS.md` under `### Seen red once (Phase 33)`.

## Task Commits

1. **Task 1: tracer, `spur shaft info` prints the API's document** - `07275dc` (feat)
2. **Task 2: `spur shaft export`, its refusals, help and README lines** - `1763b5d` (feat)
3. **Task 3: one fixed set, API = CLI on every number and the download name, seen red once** - `6e6ec80` (test)

**Plan metadata:** the docs commit that carries this file (docs: complete plan).

Tracer gate: the tracer's `<verify>` carries only `<automated>`, so it was re-run before expansion (2 tests, contracts 10 kept, mypy, ruff) and passed.

## Files Created/Modified

- `src/spur/cli.py` - `_add_shaft_args`, `_shaft_params`, `cmd_shaft_info`, `cmd_shaft_export`, the `shaft` sub-command with `info` and `export`
- `tests/test_cli.py` - 8 shaft tests (document parity, clash sentence, export, six refusals, API sentence parity, BuildError, no default name, help, README lines)
- `tests/shaft_parity.py`, `tests/test_shaft_parity.py` - the fixed set, the readers and the parity tests
- `README.md` - three `spur shaft` lines under `## CLI`
- `docs/architecture/cli.md` - "The shaft group"
- `docs/architecture/decision_log.md` - L49: **The shaft's CLI**, **One shaft, three readers**
- `bench/RESULTS.md` - the 33-05 row under `### Seen red once (Phase 33)`

## Decisions Made

- A ValidationError under `--designation` is printed at `designation` when it is the model's own refusal or concerns a spline field, and at the solid field's own name for a bound on it. This is where the API's 422 puts each; the plan said to print every error at `designation`, and `test_a_shaft_refusal_reads_the_same_on_the_api_and_the_cli` pins the API's `loc` and `msg` instead.
- `din5480`, `shaft_calc` and `shaft_params` are top-level imports of `cli.py` (none reaches the kernel); `model` stays inside `cmd_shaft_export`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's `-k shaft` filter would not select the second tracer test**
- **Found during:** Task 1
- **Issue:** the plan names `test_a_designation_with_a_spline_flag_exits_2_like_the_api_422`; the verify command `-k shaft` selects tests by name, so only one of the two would have run.
- **Fix:** named it `test_a_shaft_designation_with_a_spline_flag_exits_2_like_the_api_422`.
- **Files modified:** tests/test_cli.py
- **Committed in:** 07275dc

**2. [Rule 1 - Bug] Errors under `--designation` printed at `designation` only where the API does**
- **Found during:** Task 2
- **Issue:** printing every ValidationError as `error: designation: ...` (the plan's wording) would name `designation` for `--shank-length 500.5`, where the API's 422 names `shank_length`.
- **Fix:** see Decisions Made.
- **Files modified:** src/spur/cli.py, tests/test_cli.py
- **Committed in:** 07275dc, 1763b5d

---

**Total deviations:** 2 auto-fixed (2 Rule 1)
**Impact on plan:** both keep the CLI equal to the API as the plan intends; no scope change.

## Issues Encountered

None. Two small lint/gate points were fixed before the Task 3 commit: ruff PT018 on a combined assert, and `make no-fake-done` forbids `type: ignore`, so the tests build a `ShaftParams` with `model_validate` instead.

## Verification

- `make test PYTEST_ARGS="tests/test_cli.py --no-cov -n0 -q"`: `72 passed in 10.43s`.
- `.venv/bin/python -m pytest --no-cov -n 8 -q tests/test_shaft_parity.py tests/test_shaft_interfaces.py`: `87 passed in 0.84s`.
- `make lint-imports`: `Contracts: 10 kept, 0 broken.`; `make no-fake-done`, `make gear.unchanged` green; mypy over `src tests` and `ruff check .` clean.
- `make verify.fast`: `2308 passed in 11.73s`, `real 12.71` s (load 10.29 -> 9.58), under the 30 s bar (L36).
- `make verify`: `2773 passed in 240.77s`, `real 241.70` s, load averages (1-minute) 9.14 at start and 11.53 at end; log `investigation/33-05-verify.log`. For comparison Phase 32 closed at `2644 passed`, `real 234.78` s at load 5.24 -> 7.66 (a busier host this time).

## Issues for later

No debt or idea item was filed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 33-06. `tests/shaft_parity.py` exports `SHAFTS`, `displayed` and `web_rows` for 33-08's browser step (`from shaft_parity import ...`); `displayed` is a Python port of `fmt()` that 33-08 must check against the browser. `refuse()` and `gearQuery()` are untouched (C1).

## Known Stubs

None.

## Self-Check: PASSED

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
