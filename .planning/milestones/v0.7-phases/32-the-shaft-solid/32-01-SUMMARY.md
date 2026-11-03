---
phase: 32-the-shaft-solid
plan: 01
subsystem: testing
tags: [gate-baseline, float-evidence, decision-checkpoint, din5480, bench]

requires:
  - phase: 31-din-5480-maths
    provides: the merged code (b4cfd71) the baseline is read on, and `shaft_calc` / `din5480` the floor evidence imports
provides:
  - one recorded `make verify` on Phase 31's code (the baseline 32-06 subtracts from)
  - the floor rule's float behaviour, measured on decimal grids and the shaft lattice
  - the human's picks A1 B1 C1 D1 with exact values (`## Decision result`)
  - the nice debt item "shaft contention row"
affects: [32-02, 32-04, 32-05, 32-06, 33]

actuals:
  tokens: 136343   # chars/4 over the added lines of 7c1bc2c..HEAD; 1503 of that is bench/ and docs/, the rest is the kept verify log and grid log/script
  tasks: 2
  commits: 2
plan_head_before: 7c1bc2c78852f9d2472d9644d02c8cab6e9c4f81
plan_head_after: a1a46e1e04570013348375d31fd3627b4edf1f1f

tech-stack:
  added: []
  patterns:
    - "evidence script under investigation/ shown to the human before a rounding rule is picked"

key-files:
  created:
    - .planning/phases/32-the-shaft-solid/investigation/32-01-verify.log
    - .planning/phases/32-the-shaft-solid/investigation/32-01-verify-meta.log
    - .planning/phases/32-the-shaft-solid/investigation/32-01-floor-grid.py
    - .planning/phases/32-the-shaft-solid/investigation/32-01-floor-grid.log
    - docs/tech_debt/active/2026-10-27-shaft-contention-row.md
  modified:
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "A1: end_chamfer_effective is floored to 0.001 mm with a 1e-9 guard, floor(v*1000 + 1e-9)/1000, on the request, the tooth-height cap and the splined-length cap, then the minimum of the three"
  - "B1: end_chamfer_effective is the 13th ShaftDimensions key, after measure_over_pins and before designation"
  - "C1: ShaftParams.slug() stem is spur_shaft_w{reference_d:g}x{module:g}x{teeth}, default spur_shaft_w25x1.25x18"
  - "D1: single-build shaft rows only in Phase 32; contention row filed as nice debt, trigger Phase 33's /api/shaft/model.{fmt}"

patterns-established:
  - "A choice no logged decision covers is measured first, shown inline, then picked by the human and recorded with exact values"

requirements-completed: []  # 32-01 only advances REQ-shaft-solid, REQ-shaft-build-measured and REQ-gate-cost-recorded (baseline and choices); later plans deliver them

duration: 17 min
completed: 2026-10-27
status: complete
---

# Phase 32 Plan 01: Gate baseline, floor evidence and the four open choices Summary

One `make verify` baseline on Phase 31's code (2387 passed in 251.15 s), the chamfer floor rule measured float-safe on 500,001 three-place decimals, and the human's picks A1 B1 C1 D1 recorded for plans 32-02, 32-04 and 32-05.

## Decision result

All four picked by the human on 2026-10-27 (answer `recommended`, which is A1 B1 C1 D1). Plans 32-02, 32-04 and 32-05 read this table.

| Letter | Option | Exact value | Date | Picked by |
|---|---|---|---|---|
| A | A1 | `end_chamfer_effective` = floor to 0.001 mm with a 1e-9 guard, `floor(v*1000 + 1e-9)/1000`, applied to the request, the tooth-height cap and the splined-length cap, then the minimum of the three | 2026-10-27 | picked by the human |
| B | B1 | `end_chamfer_effective` is the 13th `ShaftDimensions` key, placed after `measure_over_pins` and before `designation` | 2026-10-27 | picked by the human |
| C | C1 | `ShaftParams.slug()` stem `spur_shaft_w{reference_d:g}x{module:g}x{teeth}`; the default shaft's slug is `spur_shaft_w25x1.25x18` (numbers only, no fit) | 2026-10-27 | picked by the human |
| D | D1 | single-build rows only, each in a fresh process on macOS and in a Linux container beside the 199-tooth gear; a `nice` debt item "shaft contention row" filed, trigger Phase 33 adding `/api/shaft/model.{fmt}` | 2026-10-27 | picked by the human |

Already settled and not asked (CONTEXT D-01..D-10, the carried-forward locks and the objective's Claude's-Discretion list) stayed as stated.

## Baseline

`make verify` on HEAD `7c1bc2c` (`src`, `tests`, `bench`, `pyproject.toml`, `Makefile`, `requirements.txt` byte-equal to Phase 31's merge `b4cfd71`), host `18 CPUs, arm64, 64.0 GiB RAM`:

- pytest: `======================= 2387 passed in 251.15s (0:04:11) =======================`
- `/usr/bin/time -p`: real 253.13, user 663.56, sys 495.87; make exit status 0
- Coverage TOTAL 98.24% (floor 96.0%); `Contracts: 10 kept, 0 broken.`
- 1-minute load 7.96 before, 15.03 after
- CONTEXT's `2387 passed / 221.86 s` appears in no log. The count matches, the time does not. 32-06 compares against 251.15 s, not 221.86 s.

Logs: `investigation/32-01-verify.log`, `32-01-verify-meta.log`. Recorded in `bench/RESULTS.md` `### The gate baseline (32-01)`.

## Floor evidence (A2 of the research, measured here)

From `investigation/32-01-floor-grid.log`:

1. 500,001 three-place decimals 0.000..500.000 with `+1e-9`: 0 mismatches.
2. Without `+1e-9`: 2957 mismatches (0.59%), first 1.001, 1.003, 1.005.
3. 5,000,001 four-place decimals: 0 floor above their input.
4. Shaft grid, 13,552 feasible rows: floored tooth height equals the module on all; 0 lattice chamfers in the 1e-9..1e-4 band.
5. Lengths 2.0006 and 5.0007: half-even rounding gives 2.001 and 5.001 (above the length), floor gives 2.0 and 5.0.

## Task commits

1. Task 1 (tracer): `8409e5a` docs(bench): Phase 32's gate baseline and the chamfer floor's float evidence
2. Task 2 (decision, no code): debt item `a1a46e1` docs(32-01): file the shaft contention row as nice debt

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's 0.29 example is false in binary64**
- **Found during:** Task 1 (floor grid, line 2)
- **Issue:** The plan, the checkpoint option A2 and the objective claim `0.29 * 1000 == 289.99999999999994` and that the exact floor turns a typed 0.29 into 0.289. In binary64 `0.29 * 1000` is exactly `290.0`, so A2 floors 0.29 to 0.29. The real A2 cost is 2957 of 500,001 three-place decimals (0.59%) losing one 0.001 step, the first being 1.001, 1.003, 1.005.
- **Fix:** A 0.29 probe was added to log line 2, and the bench section states the plan expected 0.29 and it is not among the failures. The human picked A1, which does not depend on the false example; the correct A2 evidence (2957 mismatches) was in the log shown at the checkpoint.
- **Files modified:** `32-01-floor-grid.py`, `32-01-floor-grid.log`, `bench/RESULTS.md`
- **Commit:** 8409e5a

Plan 32-02's L47 wording and any test comment must not repeat the 0.29 claim; cite 1.001 instead.

### Unverified claim carried forward

A1's statement that the result can exceed `splined_length` only by under 1e-12 mm was not measured by the 32-01 script. It rests on research `32-windows-axial.log`. 32-02 or 32-03 should measure it before a test or comment states it as fact.

## Auth gates

None.

## Debt filed

Yes: `/Users/half/git/halfb00t/spur/docs/tech_debt/active/2026-10-27-shaft-contention-row.md` (Severity nice, trigger Phase 33's `/api/shaft/model.{fmt}`), with its row in `docs/tech_debt/INDEX.md`. No idea item filed.

## Known Stubs

None. Nothing under `src/` or `tests/` was edited (`git status --porcelain -- src tests` is empty).

## Threat Flags

None. T-32-01 is mitigated: the baseline is a fresh logged run on Phase 31's code and the unsourced figure is named as unused.

## Self-Check: PASSED

Commits 8409e5a and a1a46e1 are ancestors of HEAD; the created files exist.
