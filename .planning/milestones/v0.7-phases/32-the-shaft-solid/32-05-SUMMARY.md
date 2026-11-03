---
phase: 32-the-shaft-solid
plan: 05
subsystem: bench
tags: [bench, build-time, fresh-process, peak-rss, din5480, bounds-sweep, l17, l37, l47, d-09]

requires:
  - phase: 32-the-shaft-solid
    provides: "32-04 model.build / model.export taking a ShaftParams through shaft_model; 32-01 decision D1 (single-build rows only); 32-02 ShaftParams bounds"
provides:
  - "bench.build_time: a `part` switch in load_sweep (shaft row vs gear row), `--fresh` (one child process per row, in file order) and the memory columns"
  - "bench/sweeps/shaft.json: nine shaft rows and the 199-tooth gear reference, pinned by a test that every solid field's `le` is reached"
  - "bench/RESULTS.md `### The heaviest shaft (32-05)`: both hosts' tables and the verdicts"
  - "an L47 amendment: the four solid-field bounds as swept, D-09 confirmed"
affects: [32-06, 33]

actuals:
  tokens: 8635   # chars/4 over the added lines of 99ac99a..HEAD (34,540 chars, of which the two sweep logs, the tracer log and the RESULTS section are the bulk)
  tasks: 3
  commits: 4
plan_head_before: 99ac99aeb3c3b19fc6ed49542cb91bf0c035ad16
plan_head_after: 8c49ba16be24dd9dec0870f9451134a17753a59c

tech-stack:
  added: []
  patterns:
    - "a per-row memory figure comes only from a fresh child process; an in-process Timing leaves it None and a mixed report raises (L08)"
    - "a bound is pinned by the sweep that earned it: a test reads each `le` from the model and requires a sweep row on it"

key-files:
  created:
    - bench/sweeps/shaft.json
    - .planning/phases/32-the-shaft-solid/investigation/32-05-tracer.json
    - .planning/phases/32-the-shaft-solid/investigation/32-05-tracer.log
    - .planning/phases/32-the-shaft-solid/investigation/32-05-sweep-macos.log
    - .planning/phases/32-the-shaft-solid/investigation/32-05-sweep-linux.log
  modified:
    - bench/__init__.py
    - bench/build_time.py
    - bench/export_cost.py
    - bench/RESULTS.md
    - tests/test_bench.py
    - tests/test_shaft_params.py
    - src/spur/shaft_params.py
    - docs/architecture/decision_log.md
    - docs/tech_debt/active/2026-10-27-shaft-contention-row.md

key-decisions:
  - "D-09 confirmed, no bound moved: splined_length 500, end_chamfer 10, shank_d 850 and shank_length 500 stand as the sweep reached them"
  - "maxrss_bytes moved from bench/export_cost.py to bench/__init__.py so build_time and export_cost share it (build_time cannot import export_cost)"
  - "the Linux row is the linux/amd64 container emulated on the arm64 host, as 26-06 recorded; its walls carry the emulation cost and are never mixed with macOS's"

requirements-completed: [REQ-shaft-build-measured]

duration: about 55 min
completed: 2026-10-27
status: complete
---

# Phase 32 Plan 05: The heaviest allowed shaft, measured and its bounds pinned Summary

`python -m bench.build_time bench/sweeps/shaft.json --fresh` times nine shaft rows and the 199-tooth gear each in its own process, and the heaviest allowed shaft builds and exports in 2.23 s on macOS and 5.44 s in the Linux container against L37's 30 s, with every shaft's peak RSS under the gear's in the same run, so the four solid-field bounds are confirmed (D-09) and logged as an L47 amendment.

## What shipped

Commits (single repo, hooks on, no `--no-verify`):

1. `b8ad8e0` feat(bench): time a shaft row in its own process with its own peak memory (Task 1, tracer)
2. `c8608ba` test(bench): the shaft sweep, with a test that it reaches every solid-field bound (Task 2, sweep file and its test)
3. `37fdc21` docs(bench): the heaviest allowed shaft, measured on macOS and Linux (32-05) (Task 2, the two logs and the RESULTS section)
4. `8c49ba1` docs(decisions): L47 amendment, the shaft's solid-field bounds as swept (Task 3)

`load_sweep` returns `list[tuple[str, Part]]`: a row without `part` is a `GearParams` (every earlier sweep file loads unchanged, checked over all of `bench/sweeps/*.json`), `"part": "shaft"` a `ShaftParams`, any other value is refused naming the file, the set and the value. `--fresh` runs `python -m bench.build_time <sweep> --child-row i` one row at a time in file order; the child prints one JSON line with its times, STL size, own `ru_maxrss` (through `bench.maxrss_bytes`) and, on Linux, `VmRSS`. `Timing.peak_rss_bytes` and `resident_bytes` stay `None` in-process, so the plain report is byte-for-byte today's table, and a report mixing rows with and without a peak raises.

## The measurement

Full tables and host lines are in `bench/RESULTS.md` `### The heaviest shaft (32-05)`; logs `32-05-sweep-macos.log` and `32-05-sweep-linux.log` under `investigation/`. HEAD `c8608ba` for both runs.

| Reading | macOS (18 CPUs, arm64; load 6.46 at start) | Linux container (linux/amd64, emulated on the arm64 host) |
|---|---|---|
| Heaviest shaft row, build + slower export | 2.23 s (z 82 m 10, `shank_d` = `tip_d`; the `splined_length` 1 row also reads 2.23) | 5.44 s (z 82 m 10, `splined_length` 1, `end_chamfer` 1, `shank_length` 0) |
| Margin to 30 s | 27.77 s, 13.5x | 24.56 s, 5.5x |
| Highest shaft peak RSS / gear peak, same run | 1066 / 1356 MiB = 0.786 | 1309 / 1449 MiB = 0.903 |
| Resident after build, heaviest shaft / gear | not read (macOS) | 869 / 844 MiB = 1.030 |
| Largest shaft fine STL / gear STL | 3326584 / 9062784 bytes = 0.367 | 3342384 / 9062784 bytes = 0.369 |

D-09 outcome: confirmed. No `**NO**` in either log, no shaft peak above the gear's, so no solid field was re-run at half its `le` and none was lowered. D-10 was not triggered.

## The bounds as pinned

`splined_length` 1 to 500, `end_chamfer` 0 to 10, `shank_d` 1 to 850, `shank_length` 0 to 500, unchanged from 32-02. `tests/test_shaft_params.py`'s bound test carries a comment citing `### The heaviest shaft (32-05)`; `tests/test_bench.py::test_the_shaft_sweep_reaches_every_solid_field_bound_and_carries_the_gear_reference` fails if a bound is raised without a sweep row on it, and pins the two exact-equality rows (`shank_d` = `tip_d` and = `root_d`), the prism-only row and the single 199-tooth gear.

## Verification

- `make verify`: `======================= 2644 passed in 312.50s (0:05:12) =======================`, exit 0 (`real 314.05`); coverage 98.22 % (floor 96.0); `Contracts: 10 kept, 0 broken.`; `gear.unchanged: ... byte-equal to v0.6`. 2638 at the 32-04 close plus the six tests this plan added.
- Task 1: `pytest -n0 tests/test_bench.py` passed; `ruff check bench tests` and `mypy src tests docker bench scripts` clean; the tracer log's row reads `yes`; tracer gate re-run end to end after the commit before Task 2 began.
- Task 2: `grep -c '| part=shaft'` is 9 in each log; `grep -c '**NO**'` is 0 in each; the RESULTS section holds two `Peak RSS (MiB)` tables; `shaft.json` is `10 9`.
- Task 3: `pytest -n0 tests/test_shaft_params.py tests/test_bench.py` 124 passed; the decision-log commit adds 13 lines and deletes 0; `git diff --exit-code` over `calc.py`, `params.py`, `model.py`, `shaft_model.py` for that commit exits 0; `git status --porcelain -- src tests bench docs pyproject.toml` empty.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `load_sweep` returning `Part` broke `mypy --strict` over eleven existing gear-sweep tests**
- **Found during:** Task 1, `mypy src tests docker bench scripts` (51 errors: `tip_chamfer_limit` and `root_shape` on `GearParams | ShaftParams`).
- **Fix:** a test-local `load_gear_sweep(path) -> list[tuple[str, GearParams]]` in `tests/test_bench.py` asserts each row is a `GearParams` and returns them typed; the eleven gear-sweep call sites use it, so a shaft row in a gear sweep fails by name. The new shaft tests and the label-only call use `load_sweep` directly.
- **Files modified:** `tests/test_bench.py`
- **Commit:** `b8ad8e0`

**2. [Rule 1 - Wording] The child's resident figure is read after the build and both exports, not after the build alone**
- **Found during:** Task 2, writing the RESULTS reading.
- **Issue:** the plan's column is titled "Resident after build", and `_run_child` reads `VmRSS` at the end of the child, after `time_set` (build, fine STL, STEP; an export releases the kernel arenas, the solid stays cached). The header text is the plan's and the verify greps for the peak column only.
- **Fix:** `_run_child`'s docstring and the RESULTS paragraph say exactly when it is read; the header is unchanged.
- **Files modified:** `bench/build_time.py`, `bench/RESULTS.md`
- **Commit:** `37fdc21`

### Plan wording that did not match the tree

**3. Debt item for choice D1 not re-filed.** The plan's Task 3 asks for `docs/tech_debt/active/<date>-shaft-contention-row-not-measured.md`. 32-01 had already filed the same item as `2026-10-27-shaft-contention-row.md` (nice, trigger Phase 33's `/api/shaft/model.{fmt}`, with its INDEX row), and the dispatch said not to re-file. I added the single-build margins to that item's Context instead; the plan's file-name acceptance line is therefore not met by a new file, by design.

**4. The Task 2 verify `-k "shaft"` selects three tests, not "at least 5".** Only three of the plan's named tests carry `shaft` in their name (the other two new tests are named for the part switch and the memory columns). The whole file ran instead: 51 passed.

No pool-level contention row was measured and `investigation/32-05-contention.py` was not written (D2 not chosen).

## Caveats the reader should carry

- The Linux numbers are from a linux/amd64 container emulated on an arm64 host (`VirtualApple @ 2.50GHz`), the same arrangement `### make test-image (26-06)` records. The shaft-to-gear ratios within a run are the comparison; Linux and macOS walls are not compared to each other.
- Triangle and byte counts differ between hosts for the same row (the default shaft is 5662 triangles on macOS, 5728 on Linux); each host's STL size is read on its own table.
- Run-to-run variance was not measured here: each host has one run, and the memory criterion's 5 % is L17's recorded figure, not a new one. The shaft peaks sit 10 to 21 percent under the gear's, so the verdict does not depend on it; the Linux resident ratio (1.030) is the one reading that does, and it is reported as inside the 5 %, not as a difference.
- A run that fills the 4-entry solid cache with four shafts was not made; one cache entry's resident memory (760 to 869 MiB on Linux) is measured, the sum is not.

## Debt and ideas

Nothing new filed. `docs/tech_debt/active/2026-10-27-shaft-contention-row.md` (nice) was edited to cite this plan's single-build margins and remains open for Phase 33.

## Known Stubs

None.

## Threat Flags

None. T-32-10 is mitigated by the sweep at every solid-field maximum on both hosts with D-09 confirmed; T-32-12 by the `--fresh` child per row, the `None` memory fields in-process and the mixed-report refusal; T-32-11 is covered by 32-02's non-finite test and every sweep row going through `load_sweep`'s validation. No new endpoint, auth path or file access was added (the bench only reads its own sweep file).

## Self-Check: PASSED

Commits `b8ad8e0`, `c8608ba`, `37fdc21` and `8c49ba1` are ancestors of HEAD; every created file exists on disk.
