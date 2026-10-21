---
phase: 27-ledger-tests-and-harness
plan: 02
subsystem: testing
tags: [pytest, slug, root_mode, seeded-draws, monkeypatch, openapi, tech-debt]

requires:
  - phase: 27-ledger-tests-and-harness
    provides: 27-01 switched the shared working tree back to the phase branch (no code used)
provides:
  - a seeded, stratified `slug()` totality test in the commit slice, seen red twice
  - a fresh `_BlobCache` per test for the failed-build name test, seen red with a pre-seeded cache
  - 24 IN-03, 22 IN-01 and 23 IN-08 fixed in the ledger test files
  - two retired debt items (slug totality, failed-build name cache order)
affects: [27-06 bench/RESULTS.md "Seen red once (Phase 27)" rows and triage table, Phase 28 disposition files]

actuals:
  tokens: 6500
  tasks: 3
  commits: 3   # MEASURED: git rev-list --count 49cc9a0..HEAD at write time (before the SUMMARY commit)

plan_head_before: 49cc9a03419adcc1e7d56d3baecc03c1a83d1921
plan_head_after: c30ebd0804bb4c4a0ea0a4dc8030c1b529669f54

tech-stack:
  added: []
  patterns:
    - "A stratified, seeded draw whose buckets are the oracle's answer (`root_mode`), each asserted non-empty, plus `typing.get_args` on the Literal so a new reason turns the test red"
    - "Isolation by replacing the whole module-state object per test (`monkeypatch.setattr` of `_EXPORTS`) instead of a hand-kept uniqueness rule"

key-files:
  created:
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-red-slug-junction.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-red-slug-root-curve.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-slug-green.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-verify-fast.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-red-name-preseeded.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-green-name-preseeded.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-red-openapi-walk.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-02-red-honeycomb.log
  modified:
    - tests/test_trochoid.py
    - tests/test_api.py
    - tests/composition.py
    - tests/test_relations.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md
    - docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md

key-decisions:
  - "The totality test draws 1,300 gears in five boxes (the fifth, radial, fills `not requested`); the bucket is `root_mode`'s answer, never the box's intent"
  - "Task 1 used the file's existing `_BORE_OFF`; Task 3 then replaced it with the shared `BORE_OFF`, so each commit stands alone"
  - "`tests/test_cli.py` keeps its own `_BORE_OFF` copy: outside 22 IN-01's two files and outside this plan; 27-06 notes it in the triage table"

requirements-completed: [REQ-slug-totality-guarded, REQ-failed-build-name-isolated]

coverage:
  - id: D1
    description: "`slug()` is total over every reachable refusal reason and ends `_trochoid` exactly when `root_mode` says trochoid; the two unreachable reasons are forced and labelled"
    requirement: REQ-slug-totality-guarded
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_slug_is_total_and_ends_trochoid_exactly_when_root_mode_does"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_slug_stays_total_on_the_two_reasons_only_a_patch_reaches"
        status: pass
    human_judgment: false
  - id: D2
    description: "The totality test cannot pass vacuously: seen red against a `_junction` and a `_root_curve` that raise on entry"
    requirement: REQ-slug-totality-guarded
    verification:
      - kind: other
        ref: "investigation/27-02-red-slug-junction.log and 27-02-red-slug-root-curve.log: `1 failed` with the RuntimeError text; `git diff --exit-code v0.5 -- src/` exits 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "The failed-build name test reads 422 whatever ran before it, both rows, under a fresh export cache"
    requirement: REQ-failed-build-name-isolated
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_a_failed_build_records_the_name_of_the_part_it_would_have_been"
        status: pass
      - kind: other
        ref: "investigation/27-02-red-name-preseeded.log (2 failed, assert 200 == 422) and 27-02-green-name-preseeded.log (3 passed) under the same pre-seed"
        status: pass
    human_judgment: false
  - id: D4
    description: "24 IN-03, 22 IN-01 and 23 IN-08 fixed, the OpenAPI walker and the honeycomb meta-test row each seen red"
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_openapi_documents_the_typed_contracts; tests/test_relations.py#test_a_relation_true_only_at_the_first_open_count_goes_red"
        status: pass
    human_judgment: false
  - id: D5
    description: "The two debt items are retired in their fixing commits (Status resolved, git mv, INDEX row moved)"
    verification:
      - kind: other
        ref: "Task 1 and Task 2 automated checks over docs/tech_debt/{resolved,active}/ and INDEX.md"
        status: pass
    human_judgment: true
    rationale: "Whether the `Resolved in:` wording and the INDEX row read as the ledger's convention is a reading, not a test"

duration: 9min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 02: Ledger guards that cannot pass vacuously Summary

**A seeded 1,300-draw `slug()` totality test in the commit slice (every reachable refusal reason hit, the two unreachable ones forced and labelled, red against a raising `_junction` and `_root_curve`), a fresh `_BlobCache` per test for the failed-build name test, and three info findings closed; two debt items retired.**

## Performance

- **Duration:** 9 min (including one `make verify`, 3 min 54 s)
- **Started:** 2026-10-20T13:21:38Z
- **Completed:** 2026-10-20T13:31Z
- **Tasks:** 3
- **Files modified:** 15 in the three task commits (4 test files, INDEX, 2 moved debt items, 8 logs)

## Accomplishments

- `tests/test_trochoid.py::test_slug_is_total_and_ends_trochoid_exactly_when_root_mode_does`: seed 20261020, five boxes, 1,300 draws. Measured buckets: 564 `trochoid`, 303 `nothing radial to replace`, 82 `not requested`, 13 `tip land gone`, 9 `tooth severed`; 329 draws skipped by the validator; the call takes 0.07 s. `set(get_args(RootReason))` is asserted equal to the four reachable plus the two forced reasons, and no validated draw may land in a forced one. The two forced rows (`forced-bracket-degenerate`, `forced-curve-invalid`) patch `spur.calc._junction` and `spur.calc._root_curve`; `slug()` returns `spur_z23_m1.75_pa25` in both.
- `make verify.fast` reads `real 11.15` s with the new tests in it (`925 passed in 10.55s`), under L36's 30 s; kept in `investigation/27-02-verify-fast.log`.
- `fresh_exports` (`monkeypatch.setattr(spur.app, "_EXPORTS", spur.app._BlobCache(1 << 20))`) is applied to the name test only; the "downloaded by no other test" comment is gone and the three siblings keep their unique teeth (D-08). The whole of `tests/test_api.py` passes under `-n 4` (`62 passed in 5.79s`).
- 24 IN-03: `_has_key` walks the parsed `/openapi.json` for a dict key `selectors`, with two synthetic-document self-checks. 22 IN-01: one `BORE_OFF` in `tests/composition.py`. 23 IN-08: `"honeycomb (4)": {"hex_cell": 4, "hex_wall": 1}` in `CUTOUT_STATES`, the meta-test gains `("hex_wall", "hex_cell", 0.05)`, the counts read fourteen states (154 cells).

## Red runs (first failure line, log)

| Guard | Break | First failure line | Log |
|---|---|---|---|
| totality test | `raise RuntimeError("mutated _junction")` as the first body line of `_junction` | `E       RuntimeError: mutated _junction`, `1 failed, 100 deselected in 0.09s` | `investigation/27-02-red-slug-junction.log` |
| totality test | the same in `_root_curve` | `E       RuntimeError: mutated _root_curve`, `1 failed, 100 deselected in 0.08s` | `investigation/27-02-red-slug-root-curve.log` |
| failed-build name test | a temporary test downloaded both rows' gears first, old shape | `E       assert 200 == 422` on both rows, `2 failed, 1 passed, 60 deselected` | `investigation/27-02-red-name-preseeded.log` |
| same, with `fresh_exports`, same pre-seed | none (green) | `3 passed, 60 deselected` | `investigation/27-02-green-name-preseeded.log` |
| OpenAPI walker | `_has_key` returned `False` | `E       AssertionError: assert False` where `_has_key({'x': [{'selectors': []}]}, 'selectors')`, `1 failed, 61 deselected` | `investigation/27-02-red-openapi-walk.log` |
| honeycomb meta-test row | `honeycomb (4)` absent | `E       Failed: DID NOT RAISE AssertionError`, `1 failed, 2 passed, 56 deselected` | `investigation/27-02-red-honeycomb.log` |

After both `calc.py` mutations, `git checkout -- src/spur/calc.py` and `git diff --exit-code v0.5 -- src/spur/calc.py src/spur/params.py` exited 0 before any commit. 27-06 copies its "Seen red once (Phase 27)" rows from these logs.

## Task Commits

1. **Task 1: seeded slug totality test, red twice, item retired** - `345ee08` (test)
2. **Task 2: fresh export cache for the failed-build name test, red with a pre-seed, item retired** - `c47bfc4` (test)
3. **Task 3: OpenAPI key walk, shared bore-off block, `honeycomb (4)`** - `c30ebd0` (test)

**Plan metadata:** the commit that adds this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md (docs: complete plan)

## Files Created/Modified

- `tests/test_trochoid.py` - the totality test, the two forced rows, `_SlugBox`, `_SLUG_BOXES`; `_BORE_OFF` removed in favour of `BORE_OFF`
- `tests/test_api.py` - `fresh_exports`, `_has_key`, `import spur.app`, `BORE_OFF` in `SMALL_GEAR` and the `refused` row
- `tests/composition.py` - `BORE_OFF`
- `tests/test_relations.py` - `honeycomb (4)`, the meta-test's third parametrize element, "fourteen" for "twelve"
- `docs/tech_debt/INDEX.md` and the two items under `docs/tech_debt/resolved/` - retired
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-02-*.log` - the eight logs above

## Decisions Made

- Boxes and draw order follow the plan; a fifth `radial` box (100 draws) fills `not requested` and is drawn last, so the first 1,200 draws keep the sequence 27-RESEARCH measured.
- `tests/test_cli.py:524` keeps its own `_BORE_OFF`: the plan names only `test_trochoid.py` and `test_api.py` for 22 IN-01, and test_cli is a file this plan does not otherwise touch. 27-06 lists it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A docstring tripped two acceptance greps**
- **Found during:** Task 1 acceptance check
- **Issue:** the test's docstring spelled `get_args(RootReason)` and `random.Random(20261020)`, so the plan's `grep -c ... prints 1` checks read 2.
- **Fix:** reworded the docstring ("the members of the `RootReason` union", "a generator seeded 20261020"); each literal now appears once, in the code.
- **Files modified:** tests/test_trochoid.py
- **Verification:** both greps print 1; the three tests pass; `make lint` clean.
- **Committed in:** `345ee08` (part of the Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** none; a wording change to match the plan's own acceptance greps.

## Issues Encountered

- `.planning/milestone.lock` is an untracked file that predates this plan; it was left alone and not committed.
- The plan's Task 1 verify block carries a `fails_when` per `<automated>`; the tracer gate ran as "re-run the verify" (end-of-phase mode, automated-only), passed, and expansion went ahead.

## Known Stubs

None. No `TODO`, empty placeholder or unwired data in the files this plan touched.

## Debt filed

None filed. Two items were retired:

- `docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md` (`Resolved in: test(27): guard slug() totality with a seeded, stratified test in the commit slice`)
- `docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md` (`Resolved in: test(27): give the failed-build name test its own export cache`)

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required.

## Gate

`make verify` on the phase branch before the Task 3 commit: `1326 passed in 234.80s (0:03:54)`, exit 0. `git diff --exit-code v0.5 -- src/ tests/regression/` exits 0.

## Next Phase Readiness

- 27-06 can write the "Seen red once (Phase 27)" rows from the eight logs and note the remaining inline bore-off copies (`tests/test_cli.py:524`, `tests/test_calc.py`, `tests/test_bench.py`, `tests/test_model.py`) in the triage table.
- The totality test's thinnest buckets are `tooth severed` (9) and `tip land gone` (13); a change of CPython's `random` sequence or a moved bound shows up as an empty bucket, not a silent pass.

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*

## Self-Check: PASSED

Verified: the eight `27-02-*.log` files, the two items under `docs/tech_debt/resolved/` and `tests/composition.py` exist; `345ee08`, `c47bfc4` and `c30ebd0` are ancestors of HEAD; no `docs/tech_debt/active/` copy of either item remains; `git diff --exit-code v0.5 -- src/` exits 0.
