---
phase: 34-fit-tables-and-tolerance-window
plan: 05
subsystem: startup-policy
tags: [din5480, tables, cli, lifespan, build-pool, initargs, refuse-to-start, docs]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-02: din5480_tables.active / install / reset / canonical / ENV_VAR / TablesError, the synthetic fixture, the conftest _no_table_file guard"
provides:
  - "cli.main reads the tables once after parse_args for every subcommand; a TablesError becomes SystemExit('error: SPUR_DIN5480_TABLES=<path>: <reason>'), exit 1, before cmd_serve imports uvicorn"
  - "app.lifespan reads the tables before BuildPool and passes them in; a broken file raises TablesError and leaves no pool on app.state"
  - "BuildPool(workers, timeout, *, tables=None); _warm(tables) installs them before importing the kernel; initargs=(self._tables,) in both executor constructions"
  - "README SPUR_DIN5480_TABLES row, packaging.md 'The private table file', cli.md Errors case"
affects: [34-06, 34-07, 34-17]

actuals:
  tokens: 4890    # chars/4 over the diff of src, tests, docs and README (19,560 chars); red logs and this file excluded
  tasks: 3
  commits: 3      # measured: git rev-list --count f78cc13..HEAD before this SUMMARY's own commit
plan_head_before: f78cc13b181dbb64dde79362fddab1432d493575
plan_head_after: 95de724f063111c0fa54773fd63cd92aa61bc923

tech-stack:
  added: []
  patterns:
    - "One startup check in main() for every subcommand, ahead of any lazy heavy import"
    - "Process-wide state handed to spawned workers through initargs, never re-read from the environment"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-05-red-refusal.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-05-red-initargs.log
  modified:
    - src/spur/cli.py
    - src/spur/app.py
    - src/spur/pool.py
    - tests/test_cli.py
    - tests/test_pool.py
    - docs/architecture/cli.md
    - docs/architecture/packaging.md
    - README.md

key-decisions:
  - "A5 (restated for L50 / 34-17): every subcommand refuses on a broken table file, gear commands included. Research A5 suggested sparing `spur info` / `spur export`; one call in main() is simpler, CONTEXT says 'the server and the CLI refuse to start', and with the variable unset (everyone's default) the gear is untouched. An operator who set a broken file is told so whatever they run. --help and --version still answer."
  - "cmd_serve has no call of its own: main() refuses before cmd_serve imports uvicorn, so the refusal does not depend on how uvicorn's multi-worker supervisor treats a lifespan failure (research A4, still unverified)."
  - "app.lifespan reads the tables too, as defence in depth for a direct `uvicorn spur.app:app` start; it is not what makes `spur serve` safe."

requirements-completed: [REQ-tables-private-file, REQ-solid-max-material]

coverage:
  - id: D1
    description: "With SPUR_DIN5480_TABLES naming a missing file or one whose first tolerance row's T_G is off by one, shaft info, shaft export, info, export and serve each stop with `error: SPUR_DIN5480_TABLES=<path>: ...` (exit 1 by SystemExit string), write no file and never reach uvicorn.run"
    requirement: REQ-tables-private-file
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_a_broken_table_file_stops_every_command_with_the_reason (10 cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real `python -m spur.cli serve --port 0` process with a broken file exits 1, stderr starts `error: SPUR_DIN5480_TABLES=` and names the path, stdout is empty; --version still exits 0"
    requirement: REQ-tables-private-file
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_spur_serve_refuses_a_broken_table_file_from_the_real_process, #test_version_still_answers_with_a_broken_table_file"
        status: pass
    human_judgment: false
  - id: D3
    description: "A build worker and a worker replaced by recreate_for carry exactly the parent's tables (fingerprint) even when the variable names a different valid file; a pool built without tables gives its workers none even when the variable names a valid file"
    requirement: REQ-solid-max-material
    verification:
      - kind: integration
        ref: "tests/test_pool.py#test_a_worker_and_its_replacement_carry_the_parents_tables, #test_a_pool_built_without_tables_gives_its_workers_none"
        status: pass
    human_judgment: false
  - id: D4
    description: "`with TestClient(app)` with a broken file raises TablesError from the lifespan and leaves no pool on app.state"
    requirement: REQ-tables-private-file
    verification:
      - kind: integration
        ref: "tests/test_pool.py#test_a_broken_table_file_stops_the_server_starting"
        status: pass
    human_judgment: false
  - id: D5
    description: "The operator's documentation (README row, packaging.md bind mount, cli.md Errors case) says how to run with the file, that the image never holds it, and what an unset or broken variable does"
    requirement: REQ-tables-private-file
    verification: []
    human_judgment: true
    rationale: "Prose a person must judge for clarity; the only automated pins are the two grep counts and the unchanged compose.yaml / Dockerfile."
  - id: D6
    description: "Unset variable changes nothing: every existing test of tests/test_cli.py and tests/test_pool.py passes unedited and make gear.unchanged is byte-equal to v0.6"
    requirement: REQ-solid-max-material
    verification:
      - kind: other
        ref: "make verify (2912 passed); make gear.unchanged"
        status: pass
    human_judgment: false

duration: 13min
completed: 2026-10-30
status: complete
---

# Phase 34 Plan 05: Startup policy and the pool hand-off Summary

**A set-but-broken `SPUR_DIN5480_TABLES` stops every `spur` command and the server with `error: SPUR_DIN5480_TABLES=<path>: <reason>` (exit 1), and the parent's one loaded tables object reaches every build worker and every replaced worker through `ProcessPoolExecutor(initargs=...)`.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-10-30T14:31:47Z
- **Completed:** 2026-10-30T14:44:22Z (before this file)
- **Tasks:** 3
- **Files modified:** 8 (plus 2 red logs)
- **Host load:** 7.8 / 10.6 / 20.5 (1/5/15 min) at start; 17.8 / 18.0 / 18.3 after `make verify`. The `make verify` wall time (290 s pytest, 4:51 total) was measured under that load and is a floor on the real cost, not a benchmark.

## Accomplishments

- `cli.main` calls `din5480_tables.active()` once between `parse_args` and `ns.func(ns)`. Refusal as printed: `error: SPUR_DIN5480_TABLES=<path>: <reason>` on stderr, exit status 1 (a `SystemExit` with a string, the BuildError convention). For a file with T_G off by one the reason names `tolerances`; for a missing path it ends `does not exist`. Real-process `spur serve`: exit 1, empty stdout, no listening socket.
- `app.lifespan` reads the tables before building the pool and passes `tables=` in; a broken file raises `TablesError` and leaves no pool.
- `BuildPool(workers, timeout, *, tables=None)` stores `self._tables`; `_warm(tables)` installs them, then imports the kernel; both executor constructions pass `initargs=(self._tables,)` (grep count 2).
- Docs: README environment row, packaging.md "The private table file" (read-only `:ro` bind mount plus the variable in an operator override; the image never holds the file), cli.md Errors fourth case.

## Seen red

| Task | Red run | What failed | Log |
|---|---|---|---|
| 1 | The five commands with a broken file, run against the unchanged CLI | 11 failed, 1 passed: all ten in-process cases (the gear commands ran, shaft commands raised a bare `TablesError`, `uvicorn.run` was reached) and the real-process `serve`, which started a server and hit its 60 s timeout. The `--version` guard passed, as it should before and after | `investigation/34-05-red-refusal.log` |
| 2 | `initargs` removed from the `recreate_for` construction only | `test_a_worker_and_its_replacement_carry_the_parents_tables` failed on the replaced worker: `assert b'none' == b'e9d70dbdacb...'`; the first worker (initargs intact) passed that same test's first assertion. Restored; green | `investigation/34-05-red-initargs.log` |

## Task Commits

1. **Task 1: tracer, a broken table file stops every command with its reason** - `ba6c305` (feat)
2. **Task 2: lifespan refusal and the parent's tables to every worker** - `f38c1e1` (feat)
3. **Task 3: operator documentation** - `95de724` (docs)

**Plan metadata:** this SUMMARY's commit (docs: complete plan)

## Files Created/Modified

- `src/spur/cli.py` - the one `din5480_tables.active()` call in `main()`, with the measured-fact comment (D-04, A4)
- `src/spur/app.py` - `lifespan` reads the tables before `BuildPool`, passes `tables=`
- `src/spur/pool.py` - `BuildPool(..., *, tables=None)`, `_warm(tables)`, `initargs` in both constructions
- `tests/test_cli.py` - refusal for five commands x two faults, `--version` guard, real-process serve
- `tests/test_pool.py` - `_installed_tables`, worker/replacement fingerprint, no-tables pool, lifespan refusal
- `docs/architecture/cli.md`, `docs/architecture/packaging.md`, `README.md` - operator documentation

## Decisions Made

See key-decisions: the A5 choice (every subcommand refuses), no call in `cmd_serve`, and the lifespan as defence in depth. These are the planner's choices recorded for L50 at 34-17; none needed a new `Lxx` here.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The plan's Task 2 selector `-k 'tables or real_worker'` does not match `test_a_broken_table_file_stops_the_server_starting` ("table", singular). I ran `-k 'table or real_worker'` and then the whole file (25 passed); the full `make verify` also covers it.
- The research's exit-3 claim for a lifespan failure with one uvicorn worker (cited in `app.py`'s comment) was taken from 34-RESEARCH, not re-measured here. The test pins what is ours: `TablesError` out of the lifespan and no pool left.
- `.planning/state.json`, `.planning/milestone.lock` and `.planning/ui-reviews/` were the user's and were never staged.

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path or file access beyond the one read the plan's threat model (T-34-18 to T-34-21) already covers; the path appears only in the startup refusal on the operator's stderr.

## User Setup Required

None - no external service configuration required. An operator who wants the shaft's table rows sets `SPUR_DIN5480_TABLES` (README, packaging.md).

## Debt / ideas filed

None filed. The A4 uncertainty (how uvicorn's multi-worker supervisor treats a lifespan failure) is bounded by `spur serve` refusing in `main()` first, and sits with 34-17's record.

## Verification

- `make verify`: `2912 passed in 290.37s (0:04:50)`, exit 0 (ruff, mypy --strict, import contracts `Contracts: 10 kept, 0 broken.`, no-fake-done, gear.unchanged and pytest).
- `make test PYTEST_ARGS="tests/test_pool.py tests/test_cli.py -n0 --no-cov -q"`: `110 passed in 48.41s`.
- `make gear.unchanged`: `tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`.
- `git diff ddfb3ea -- requirements.txt` empty; `git diff ddfb3ea -- compose.yaml Dockerfile` empty.
- `import spur.cli` pulls in none of fastapi, starlette, cadquery, OCP, spur.app, spur.model, spur.shaft_model (prints `[]`).

## Next Phase Readiness

34-06 and 34-07 can rely on a worker's `din5480_tables.active()` being the parent's object, so a maximum-material solid built in a worker matches the numbers the info response prints. Nothing blocks.

## Self-Check: PASSED

All ten created/modified files exist; commits `ba6c305`, `f38c1e1`, `95de724` are ancestors of HEAD.

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
