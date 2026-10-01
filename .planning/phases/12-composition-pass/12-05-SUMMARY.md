---
phase: 12-composition-pass
plan: 05
subsystem: testing
tags: [calc, composition-matrix, refusals, d-07, d-08]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-03-SUMMARY.md: spoke_count's le lowered 40 -> 32 (D-03 gate); 12-01-SUMMARY.md: the human's binding \"seven\" groups answer"
provides:
  - "tests/composition.py: the family and refusal tables shared by test_calc.py (this plan) and test_cli.py (12-07's API/CLI routing rows) -- BORES, CUTOUTS, RECESSES, TIPS, ALWAYS, BORE_FIELDS, CUTOUT_FIELDS, RECESS_FIELDS, TIP_FIELDS, HEX_IGNORES_ROUND, SPOKE_BASE, BORE_REFUSALS, CUTOUT_REFUSALS, REFUSAL_HEX, BORE_REFUSAL_FAMILIES, CUTOUT_REFUSAL_FAMILIES"
  - "D-07 tier 1 proven at the calc level: the 96-row bore x cutout x recess x tip-chamfer cross product each derives exactly its families' non-null DerivedDimensions fields and warnings, the keyed-round + spokes adjacency (0.421 mm hub wall) included"
  - "D-08 proven at the calc level: all 23 locked refusals x 6 other families switched on (138 rows) keep the same check() fields/sentence as the refusal alone, except 18 pinned two-refusal rows and 6 pinned datum rows -- the 114/6/18 split measured this session matches the planning probe in 12-05-PLAN.md <interfaces> exactly, no difference to record"
affects: [12-07-parity, 12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 4247
  tasks: 2
  commits: 2
  plan_head_before: 24a7ff0d586c5f2896ff136a7fb2dbc68de5d8ef
  plan_head_after: 9e2960d6f513dd67b758814d65dd9d7c37127cf0

# Tech tracking
tech-stack:
  added: []
  patterns: ["a shared, non-collected tests/ data module (tests/composition.py, no test_ prefix) following tests/regression/corpus.py's precedent, imported by bare name (from composition import ...) because pytest's rootdir-based sys.path insertion adds tests/ itself, with no __init__.py anywhere under tests/", "GearParams.model_construct(**kw) to read check() on an already-infeasible parameter set, skipping _feasible -- centralized behind one _unvalidated() helper carrying the single type: ignore[arg-type] mypy strict cannot avoid when unpacking a dict[str, object] into pydantic's per-field-typed generated signature without writing Any (L21)"]

key-files:
  created:
    - tests/composition.py
  modified:
    - tests/test_calc.py

key-decisions:
  - "The 114/6/18 refusal-composition split was re-derived from check() this session before pinning (D-08's own instruction) rather than trusted from the planning probe -- it matched 12-05-PLAN.md <interfaces> exactly (same 6 datum-row ids, same 18 TWO_REFUSALS field sequences, same sentences on every matching-fields pair), so no difference is recorded and no field or sentence was adjusted to make a row pass."
  - "The refusal-composition test matches alone's (sentence, fields) entries to composed's by fields (a dict keyed by the fields tuple), not by list position -- for spoke-annulus-keyed and spoke-opening-keyed the keyed bore's own hub rule fires FIRST in composed, pushing the original annulus/opening entry to position 1; matching by fields finds it correctly regardless of order."
  - "REFUSAL_HEX uses bore_hex 8, not the tier-1 table's 6, for every cutout refusal composed with a hex bore (12-05-PLAN.md <interfaces>): a 6 mm hex's chamfered mouth (4.01 mm) sits inside the default D-flat's (4.975 mm), so a hub/rim refusal composed with hex 6 would stop refusing and the row would prove nothing; 8 mm's mouth (5.167 mm) keeps every refusal firing."

patterns-established:
  - "A differential composition test (check() run twice, alone vs {**family, **refusal}) proves an invariant without deriving its expectation from the code under test -- the 'alone' values are the file's own already-pinned refusal boundaries, and the composed run is asserted equal to them, not computed and then asserted against itself."

requirements-completed: []  # REQ-three-interfaces-extended is shared with 12-07 per the shared-ID gate (#2388); marks complete only once 12-07 (the last declaring plan) finishes.

coverage:
  - id: D1
    description: "Tier 1 (D-07): the full 96-row bore x cutout x recess x tip-chamfer cross product on the default 19-tooth gear derives exactly the non-null DerivedDimensions fields and warnings its families imply, written out in tests/composition.py and never computed from derive() itself; the tip chamfer and spoke fillet print unchanged across every unrelated family switch; the keyed-round + spokes row derives a 0.421 mm hub wall instead of refusing"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers (96 rows)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-08: every one of the 23 locked refusals composed with each of the 6 other families (138 rows) keeps the same check() field-tuple sequence and sentence as the refusal alone, except the 18 rows where the switched-on family's own rule adds a second refusal (pinned, check()'s own append order) and the 6 rows where the switched-on bore moves the quoted hub datum (pinned, masked-sentence comparison)"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_every_refusal_reads_the_same_with_each_other_family_switched_on (138 rows)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase's fixture and CI-gate contracts stay unmoved by this plan: the pre-v0.2 fixture is byte-unchanged, no src/ file was touched by either commit, and this plan's own new-test cost (234 rows, 0.15 s combined) is well inside D-10's phase-wide 30 s budget"
    verification:
      - kind: other
        ref: "git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json (exit 0); git show --name-only --format= <each commit> | grep -c '^src/' (0 for both); .venv/bin/python -m pytest tests/test_calc.py -q -k 'every_refusal or every_bore_cutout' --durations=1 (234 passed, slowest under 0.005s)"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 05: Composition Matrix (Calc Level) Summary

**234 new calc-level rows (96 tier-1 derivations, 138 refusal-composition rows) prove D-07 and D-08 in microseconds each, with zero kernel calls and zero source-file changes -- the 114/6/18 refusal split re-derived from `check()` this session matches the planning probe exactly.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-09-30 (this session)
- **Completed:** 2026-09-30
- **Tasks:** 2 (1 tracer, 1 auto)
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- `tests/composition.py` created: the shared, non-collected family and refusal tables (`BORES`, `CUTOUTS`, `RECESSES`, `TIPS`, `ALWAYS`, `BORE_FIELDS`, `CUTOUT_FIELDS`, `RECESS_FIELDS`, `TIP_FIELDS`, `HEX_IGNORES_ROUND`, `SPOKE_BASE`, `BORE_REFUSALS`, `CUTOUT_REFUSALS`, `REFUSAL_HEX`, `BORE_REFUSAL_FAMILIES`, `CUTOUT_REFUSAL_FAMILIES`), written out by hand from the planning probe, never computed by calling `derive()`/`check()` — `tests/regression/corpus.py`'s precedent for a shared `tests/` data module, importable by 12-07's `test_cli.py` the same way.
- D-07 tier 1 proven: `test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers` (96 rows) — every bore x cutout x recess x tip-chamfer combination on the default 19-tooth gear derives exactly the non-null `DerivedDimensions` fields and warnings its families imply; the tip chamfer always prints 1.75 and the spoke fillet always prints 1.0 whatever else composes with it; the keyed-round bore composed with spokes derives a 0.421 mm hub wall (0.021 mm above `MIN_WALL`) instead of refusing.
- D-08 proven: `test_every_refusal_reads_the_same_with_each_other_family_switched_on` (138 rows) — all 23 locked refusals x 6 other families switched on keep the same `check()` sentence and fields as the refusal alone, except 18 pinned two-refusal rows (`TWO_REFUSALS`, `check()`'s own append order) and 6 pinned datum rows (`DATUM_ROWS`, masked-sentence comparison — the switched-on bore moves the quoted hub datum, never the fields).
- The 114/6/18 split was independently re-derived from `check()` this session (a probe script over the full 138-row matrix) before pinning either table, per the task's own instruction to record any difference from the planning probe — it matched exactly: same six datum-row ids, same 18 `TWO_REFUSALS` field sequences in the same order, and zero sentence mismatches between every alone entry and its matching-fields composed entry across all 138 rows. Nothing needed adjusting.
- Both commits touch zero `src/` files (verified via `git show --name-only`), keep `make lint typecheck lint-imports` clean, and leave the pre-v0.2 fixture byte-unchanged (`git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — the 96-row tier-1 matrix, family tables to derive() and back** - `f24d30c` (test)
2. **Task 2: Every locked refusal with each other family switched on, 138 calc rows** - `9e2960d` (test)

**Plan metadata:** committed separately (see below)

## Files Created/Modified

- `tests/composition.py` — the family and refusal tables shared by `test_calc.py` (this plan) and `test_cli.py` (12-07)
- `tests/test_calc.py` — `test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers` (96 rows), `test_every_refusal_reads_the_same_with_each_other_family_switched_on` (138 rows), `_masked()` and `_unvalidated()` helpers, `TWO_REFUSALS` and `DATUM_ROWS`

## Decisions Made

See `key-decisions` in the frontmatter: the re-derived 114/6/18 split matching the planning probe with no difference; matching `alone`'s entries to `composed`'s by fields (not list position), needed for the two rows where the keyed bore's own rule fires first; `REFUSAL_HEX` at 8 mm, not the tier-1 table's 6 mm, so hub/rim refusals keep firing when composed with a hex bore.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `GearParams.model_construct(**dict[str, object])` fails mypy strict**
- **Found during:** Task 2 (the refusal-composition test)
- **Issue:** `mypy --strict` with the pydantic plugin's `init_typed = true` generates a per-field-typed signature for `model_construct`; unpacking a plain `dict[str, object]` into it cannot be verified statically and raised 8 `arg-type` errors (one per field-typed parameter, at both call sites).
- **Fix:** Centralized the call behind one `_unvalidated(kw: dict[str, object]) -> GearParams` helper carrying a single `# type: ignore[arg-type]` with a comment explaining why (this codebase writes no explicit `Any`, L21, so an ignore is the only honest option here — `src/spur/model.py` has four existing precedents for this exact pattern with CadQuery's own untyped return types).
- **Files modified:** tests/test_calc.py
- **Verification:** `make lint typecheck` clean; both new tests pass
- **Committed in:** `9e2960d` (part of Task 2 commit)

**2. [Rule 3 - Blocking] `import re` misplaced, breaking ruff's import ordering**
- **Found during:** Task 2
- **Issue:** Added `import re` as its own group between `itertools`/`math` and the third-party imports, which ruff's `I` (isort) rule flagged as unsorted.
- **Fix:** Moved it into the stdlib group alongside `itertools` and `math`.
- **Files modified:** tests/test_calc.py
- **Verification:** `make lint` clean
- **Committed in:** `9e2960d` (part of Task 2 commit)

**3. [Rule 1 - Bug] Two composition.py comments contained the literal substring `derive(`**
- **Found during:** Task 1's own acceptance criteria (`grep -c 'derive(' tests/composition.py` must print 0)
- **Issue:** Two doc comments referenced `derive()` by name (prose, not a call), which the plan's own acceptance grep does not distinguish from an actual call.
- **Fix:** Reworded both comments to describe the same fact without the literal substring (e.g. "computed by calling `spur.calc`'s own functions" instead of naming `derive()`/`check()` directly).
- **Files modified:** tests/composition.py
- **Verification:** `grep -c 'derive(' tests/composition.py` prints 0; comment meaning unchanged
- **Committed in:** `f24d30c` (part of Task 1 commit)

---

**Total deviations:** 3 auto-fixed (2 blocking type/lint fixes, 1 bug fix to satisfy the task's own acceptance criterion)
**Impact on plan:** All three are mechanical fixes required to keep the plan's own gates green; no scope creep, no field or sentence in `src/` touched.

## Issues Encountered

None beyond the three deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tests/composition.py` is ready for 12-07's `test_cli.py` API/CLI routing rows to import the same `BORE_REFUSALS`/`CUTOUT_REFUSALS` tables (`12-05-PLAN.md`'s `key_links`).
- `REQ-three-interfaces-extended` stays open in `REQUIREMENTS.md` (shared with 12-07 per the shared-ID gate, #2388) — marks complete only once 12-07 finishes.
- `make verify`: 865 passed in 181.94 s (full suite, this session, after both commits) — green, no regressions; `make lint typecheck lint-imports` and the plan's own `<verification>` block all pass; the pre-v0.2 fixture is byte-unchanged.
- This plan's own 234 new rows cost 0.15 s of pytest time combined (`-k 'every_refusal or every_bore_cutout' --durations=1`, slowest row under 0.005 s) — negligible against D-10's phase-wide 30 s budget; 12-09 measures and records the phase total.
- No blockers.

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `tests/composition.py` (created)
- FOUND: `tests/test_calc.py` (modified, two new parametrized tests)
- FOUND: commit `f24d30c` in `git log --oneline --all`
- FOUND: commit `9e2960d` in `git log --oneline --all`
- Re-ran all task acceptance criteria: `grep -c 'derive(' tests/composition.py` = 0; both cadquery/model import greps = 0; both `git show --name-only` src/ greps = 0; `hex-corner-spokes` grep-count-of-nonzero-files = 1; collect counts 96 and 138 confirmed
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_calc.py tests/regression -q"` — 475 passed; `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` — clean (exit 0); `make lint typecheck lint-imports` — all clean
- `git rev-list --count 24a7ff0..HEAD` = 2, matching `commits: 2` above
