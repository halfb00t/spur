---
phase: 18-trochoid-maths-proved
plan: 05
subsystem: gear-maths
tags: [trochoid, root-shape-step, d05-premise, per-call-cost, derive-docstring, tech-debt, calc-layout, bench, stdlib-math]

requires:
  - phase: 18-trochoid-maths-proved
    provides: "plans 01-04: the cutter, the generator, root_mode and its six refusals, the sweep product, the independent oracle and the T3/T4 cross-checks"
provides:
  - "bench.trochoid step: the shipped root zone rebuilt the way model._outline builds it, read against the trochoid outline at 2,001 radii, both tables and a verdict"
  - "PREMISE_STEP_PER_M 0.14, PREMISE_TOLERANCE 0.25, premise_holds and its pin, committed before any table existed (8badc55)"
  - "bench/RESULTS.md Root-shape step (18-05, D-05): threshold and crossover tables, the verdict, the human's dated reading, one open note"
  - "bench/RESULTS.md Per-call cost (18-05, D-14): five timeit figures, each with its 1-minute load and date; no budget set"
  - "derive()'s docstring carries 14.7 usec at load 14.4 on 2026-10-08, the earlier 9.19 / 11.5 kept as dated history"
  - "docs/architecture/gear-maths/implementation.md lists every Phase 18 calc piece and names the five classes"
  - "the resource-tracker debt re-deferred with a named trigger (next make verify failure, or Phase 19 planning)"
affects: [19]

actuals:
  tokens: 6974    # chars/4 over the added lines of the six plan commits (27,896 chars, RESULTS.md and the debt file included)
  tasks: 3        # Task 2 was the checkpoint:decision, resolved by the human
  commits: 6      # MEASURED: git rev-list --count f55aaed..3ffb824 (this SUMMARY's and the state commit follow)
plan_head_before: f55aaedfcaf0c5d1763607d5254cbefb3bab34f8
plan_head_after: 3ffb824f19adc68ec0bdeca5137733726a5429f4
commits: 6

tech-stack:
  added: []
  patterns:
    - "a comparison line is committed and pinned before the measurement it judges, and the verify checks the commit order"
    - "a cost figure is printed with the 1-minute load before and after and the date, or not at all"
    - "an unreconciled figure is written as an open note with the assumption marked, never as a fact"

key-files:
  created: []
  modified:
    - bench/trochoid.py
    - tests/test_bench.py
    - bench/RESULTS.md
    - src/spur/calc.py
    - docs/architecture/gear-maths/implementation.md
    - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Decision 1 (D-05), taken by the human on 2026-10-08: d05-hold. The premises hold; Phase 19 is planned on D-01 (root-mode option, default off) and D-02 (trochoid only where rb > rf) as decided"
  - "Decision 2 (debt), taken by the human on 2026-10-08: debt-redefer. The resource-tracker flake keeps Severity must and Status active; trigger is now the next make verify failure, or Phase 19 planning, whichever comes first"
  - "No derive() budget is set; Phase 19 decides what enters the keystroke path from the five per-call figures"

requirements-completed: [REQ-root-mode-single-predicate, REQ-trochoid-root-generated]

coverage:
  - id: D1
    description: "D-01's premise is judged by a line written first: the gap at 17 and 18 teeth within 25 percent either side of 0.14 m, pinned at points 1e-4 m inside and outside the band and committed before the tables"
    requirement: REQ-root-mode-single-predicate
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_d05_premise_line_sits_25_percent_either_side_of_0_14_m"
        status: pass
    human_judgment: false
  - id: D2
    description: "The root-shape step measured at the undercut threshold (teeth 16-19) and at the rb = rf crossover (teeth 40-43) on this phase's generator; the premise holds, and the human read both tables and chose d05-hold"
    requirement: REQ-root-mode-single-predicate
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid step (exit 0, D-01 premise holds)"
        status: pass
    human_judgment: true
    rationale: "Whether a measured step keeps D-01 and D-02 standing is a design judgement; D-05 puts it to the human with no default, and the human answered d05-hold on 2026-10-08"
  - id: D3
    description: "Five per-call costs measured the way derive()'s docstring reads them, each with its load and date, and derive()'s stale 11.5 usec corrected to the re-measure; no derive() code changed, no budget set"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: other
        ref: "bench/RESULTS.md Per-call cost (18-05, D-14) and the plan's step-and-cost verify command"
        status: pass
    human_judgment: false
  - id: D4
    description: "implementation.md lists every Phase 18 calc piece in the | Piece | Does | form and its opening sentence names the five classes"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: other
        ref: "the plan's layout-rows verify command (reading recorded; layout rows present)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The fired 'Phase 18 planning' trigger of the must-severity resource-tracker debt has a recorded decision, taken by the human, in a commit of its own"
    verification:
      - kind: other
        ref: "the plan's debt-decision verify command (debt decision recorded in active)"
        status: pass
    human_judgment: true
    rationale: "Whether to isolate, re-defer or filter a must-severity gate defect is the human's call (T-18-16); the human chose re-defer"

duration: 19min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 05: Records and close Summary

**The root-shape step measured at both boundaries against a 25 percent line committed first (0.1449 to 0.1463 mm at 17 and 18 teeth, premise holds), five per-call costs with their load, derive()'s stale 14.7-versus-11.5 usec docstring corrected, the human's d05-hold and debt re-deferral recorded, and `make verify` green at 1017 passed.**

## Performance

- **Duration:** 19 min from the first commit (`8badc55`, 2026-10-08T02:47:54Z) to this SUMMARY (about 03:06Z). Task 1's own start was not recorded, and the wait for the human at Task 2 falls inside the figure.
- **Tasks:** 3 (Task 1 auto, Task 2 checkpoint:decision resolved by the human, Task 3 auto)
- **Files modified:** 7 (plus this SUMMARY and the planning state files)

## Accomplishments

- **The line first.** `PREMISE_STEP_PER_M = 0.14`, `PREMISE_TOLERANCE = 0.25` and `premise_holds` were committed with their pin (`8badc55`) before `bench.trochoid step` existed, and the plan's verify confirms by commit order that the pin precedes the RESULTS commit (`383d04b`). The pin tests points 1e-4 m inside and outside the band at modules 1 and 2, never the float64 edges.
- **The step, both boundaries** (module 1, 20 degrees, no shift, no backlash; the shipped root zone rebuilt as `model._outline` builds it, read at 2,001 radii; maximum at the root circle in every row):

  | table | teeth | tip radius / shipped fillet | step (mm) | join |
  |---|---|---|---|---|
  | 1, threshold | 17 | 0.38 / 0.38 | +0.1463 | crossing |
  | 1, threshold | 18 | 0.38 / 0.38 | +0.1449 | tangent |
  | 1, threshold | 17 | 0.471 / 0.471 | +0.1328 | tangent |
  | 1, threshold | 18 | 0.471 / 0.471 | +0.1329 | tangent |
  | 2, crossover | 41 | 0 / 0 | +0.1403 | tangent |
  | 2, crossover | 41 | 0.38 / 0.38 | +0.0800 | tangent |
  | 2, crossover | 41 | 0.471 / 0.406 | +0.1213 | tangent |

  Verdict: **D-01 premise holds**. All four 17- and 18-tooth rows sit inside 0.1050 to 0.1750 mm. The step barely moves across the threshold itself (16 to 19 teeth: 0.1479 to 0.1433 mm at 0.38), so it is not a feature of the 17/18 edge. At the crossover a user stepping `teeth` from 41 to 42 meets the 41-tooth gap, because the request is ignored and warned from 42 teeth up under D-02: **0.1403 mm at a sharp cutter and no fillet, 0.0800 mm at 0.38, 0.1213 mm at 0.471**. The shipped fillet is capped to 0.45 of the gap in the last four rows (0.411, 0.406, 0.4, 0.396 at a request of 0.471).
- **Five per-call costs** (`timeit -r 5`, best of 5, 2026-10-08, host busy with Spotlight indexing, 1-minute load 14.4 to 16.0 across the five):

  | call | best of 5 | load before -> after |
  |---|---|---|
  | `derive(p)` | 14.7 usec | 14.38 -> 14.75 |
  | `root_mode(p, pr)`, nothing requested | 362 nsec | 14.75 -> 14.75 |
  | `root_mode(p, pr, requested="trochoid", rho=0.5)`, default gear | 33.7 usec | 14.75 -> 15.49 |
  | `trochoid_root(c)`, default gear (tangent) | 30.7 usec | 15.49 -> 15.49 |
  | `trochoid_root(c)`, tracer gear (crossing) | 88.9 usec | 15.49 -> 16.01 |

  The crossing costs about three times the tangent solve. These are upper bounds for an idle host, and nothing measured here separates a regression from load in `derive()`'s 14.7 against its old 11.5: 18-RESEARCH read 14.5 at load 14.33 and PITFALLS 20.4 at about 6.8. **No budget is set.**
- **derive()'s docstring** now carries 14.7 usec with its load (14.4) and date (2026-10-08), the command, and the earlier 9.19 / 11.5 usec as dated history; the 2.3 usec model-construction remark is kept. No code in `derive()` changed.
- **implementation.md** names `Profile`, `Cutter`, `RootCurve`, `RootMode` and `DerivedDimensions`, and lists, in file order, the two constants with their measured basis, `_dedendum` and `_pitch_thickness`, `RootShape` and `RootReason`, `Cutter` + `cutter(p, rho)`, `undercut_teeth(c)` and `undercut_shift(c)`, `RootCurve`, `_trochoid_point`, `_waist`, `_bisect`, `_junction`, `_root_curve`, `trochoid_root(c)`, `RootMode` + `root_mode(p, pr, *, requested, rho)`, and `_ROOT_SENTENCES` with `root_warnings(rm)`. `strategy.md` and `README.md` are untouched.

## The human's two answers (Task 2, 2026-10-08, "d05-hold debt-redefer")

1. **D-05: d05-hold.** The premises hold; Phase 19 is planned on D-01 and D-02 as decided. The dated reading sits beside the tables in `bench/RESULTS.md` (`a62116f`). The crossover step stays a visible discontinuity in the opt-in mode, on record for Phase 19's Lxx.
2. **Debt: debt-redefer.** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` stays `Severity: must`, `Status: active`, in `active/`. Its dated paragraph records the reason: the phase made four full `make verify` runs (963, 981, 996 and 1016 passed), none printing the `ReentrantCallError` chain; Phase 18 added no process-spawning test (`grep -nE 'multiprocessing|ProcessPool|subprocess' tests/test_trochoid.py tests/trochoid_oracle.py` prints nothing; the pooled oracle is in `bench/`, outside the gate); `make verify.fast` excludes the process-spawning files. The trigger is now "the next `make verify` failure, or Phase 19 planning, whichever comes first", and the INDEX row's trigger cell matches. No isolation loops were run and no `filterwarnings` entry was added. Commit `0cf6de2`.

## Open note for Phase 19 (not resolved here)

18-RESEARCH Pattern 8's prototype quoted the sharp-cutter crossover as "rho 0 -> -0.1885"; this run reads **+0.1403 mm** at rho 0, 41 teeth (+0.1471 at 40), the opposite sign. Its other crossover figures match to four decimals. `ASSUMPTION:` the prototype paired rho 0 with a non-zero shipped fillet, where this table's rho 0 row sets the shipped fillet to 0 too. Not checked: the prototype's script is not in the repository, and the verdict does not turn on it, because the premise rule reads only the 17- and 18-tooth rows of table 1, none of which uses rho 0. Phase 19 should re-derive that row if it prices the sharp-cutter crossover, and quote neither figure.

## Task Commits

1. **Task 1a: the comparison line** - `8badc55` (test)
2. **Task 1b: `bench.trochoid step`** - `1db6fc6` (feat)
3. **Task 1c: tables, costs, derive() docstring** - `383d04b` (docs)
4. **Task 2: checkpoint:decision** - no commit; the answers are carried out in Task 3
5. **Task 3: the human's D-05 reading** - `a62116f` (docs)
6. **Task 3: the debt re-deferral** - `0cf6de2` (docs(debt))
7. **Task 3: the layout rows** - `3ffb824` (docs(gear-maths))

**Plan metadata:** this SUMMARY and the STATE, ROADMAP and REQUIREMENTS update follow as separate `docs(18-05)` commits, outside the measured `commits: 6`.

All through the pre-commit hook (`make verify.fast`, passed each time); no `--no-verify`, no `SKIP=`.

## Deviations from Plan

None - plan executed exactly as written.

### Judgement calls inside the plan (not rule deviations)

- **Co-Authored-By trailer.** The dispatch prompt's project rules named `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which is what `8badc55`, `1db6fc6` and `383d04b` carry (and 18-01 to 18-04). This continuation's first three commits (`a62116f`, `0cf6de2`, `3ffb824`) carry `Claude Fable 5.1`, following the dispatch prompt, before the conflict was noticed. They were not rewritten (history surgery for a trailer is not worth the risk); the SUMMARY and state commits carry `Claude Sonnet 5.5`. Raise it if the trailer matters.
- **Pre-existing working-tree changes** (`.planning/state.json` modified, `.DS_Store` and `.planning/milestone.lock` untracked) were there before the plan started and are in no commit.
- **The `step` subcommand's kernel import** stays inside the scenario function (`spur.model` loads cadquery), so `tests/test_calc.py`'s import of `bench.trochoid` stays kernel-free, as the plan's interfaces required.
- **No filed debt or idea item.** The unreconciled rho 0 figure is carried as an open note in `bench/RESULTS.md` and above; it blocks nothing and names Phase 19 as its reader. The resource-tracker debt was updated, not filed.

## Issues Encountered

- The host was heavily loaded throughout (1-minute load 14 to 54 across the cost measurements and the final gate), so every timing in this plan is an upper bound and is printed with its load. The step tables are geometry and do not move with load.

## Threat flags

None. This plan touched `bench/`, `docs/`, `tests/test_bench.py` and one docstring in `src/spur/calc.py`: no new network surface, auth path, file-access pattern or schema.

## Known Stubs

None.

## Verification

- `make verify` after the last commit of the plan (`3ffb824`), at 2026-10-08T03:04:02Z, 1-minute load 29.99 before and 54.03 after, wall 86 s: ruff, mypy `--strict`, import contracts and the unfinished-work scan green, **`1017 passed in 85.12s (0:01:25)`**, `Required test coverage of 96.0% reached. Total coverage: 97.68%`. 1016 from 18-04 plus the premise pin.
- `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k d05_premise"`: green (the Task 1 verify).
- `D-05 line committed before the measurement`; `step and cost recorded; docstring corrected`; `reading recorded; layout rows present`; `debt decision recorded in active`.
- `SC5 holds: fixture byte-identical, only calc.py under src/spur, stdlib maths, 31 pins; README and strategy.md untouched`.

## Next Phase Readiness

Phase 18 is complete: the trochoid maths is generated, selected by one predicate, proved independently, and its cost and root-shape step are on record. Phase 19 reads, in order: the open rho 0 note above; the crossover step the opt-in mode will show (0.1403 / 0.0800 / 0.1213 mm at 41 teeth); the five per-call costs (`root_mode` with nothing requested costs 0.362 usec, so the present callers pay nothing measurable; a requested trochoid costs 33.7 usec on the default gear and about three times that on a crossing gear); and the resource-tracker debt, whose trigger now names Phase 19 planning.

## Self-Check: PASSED

- Created and modified files exist: `bench/trochoid.py`, `tests/test_bench.py`, `bench/RESULTS.md`, `src/spur/calc.py`, `docs/architecture/gear-maths/implementation.md`, `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`, `docs/tech_debt/INDEX.md` (checked below).
- Commits `8badc55`, `1db6fc6`, `383d04b`, `a62116f`, `0cf6de2`, `3ffb824` are ancestors of HEAD.

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
