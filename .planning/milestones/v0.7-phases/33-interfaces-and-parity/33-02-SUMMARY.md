---
phase: 33-interfaces-and-parity
plan: 02
subsystem: shaft-kernel
tags: [shaft, kernel-guard, end-face-readback, enabled-when, tech-debt, d-16, d-18, l08, l41]

requires:
  - phase: 32-shaft-model-and-solid
    provides: "shaft_model.build_shaft and the volume bracket whose gap the reviewer found (32-REVIEW WR-01)"
  - phase: 33-interfaces-and-parity (33-01)
    provides: "the `### Seen red once (Phase 33)` table this plan appends two rows to"
provides:
  - "_guard_volume(solid, area, ra, rf, c, length, shank_length, shank_d) reads the end face back: a chamfer the kernel never cut is a BuildError before any byte is exported"
  - "a durable test for the one-valid-solid guard; build_shaft without the unreachable `except BuildError: raise`"
  - "ShaftParams.shank_d with enabled_when=[when('shank_length', 'gt', 0)], backed by a bit-equal kernel test"
  - "investigation/33-02-cut-probe.{py,log}: the measured case for an end-face read-back over a volume test"
affects: [33-04, 33-06, 33-07, 33-09]

actuals:
  tokens: 4278    # chars/4 over the 17110 added chars of 3e1eded..a07fdb8 (the estimate of 60000 counted reads too)
  tasks: 3
  commits: 5
plan_head_before: 5520c4f37bb56a0a8f99f24fe2f0e93ab76f31fd
plan_head_after: a07fdb86ae95dbb5818384fbce4c04620de14727

tech-stack:
  added: []
  patterns:
    - "a printed number is read back off the solid inside the build path, not only in the tests (the end face for the applied chamfer)"
    - "a relation is declared only after a kernel test shows the dimmed field changes nothing (L41, D-18)"

key-files:
  created:
    - .planning/phases/33-interfaces-and-parity/investigation/33-02-cut-probe.py
    - .planning/phases/33-interfaces-and-parity/investigation/33-02-cut-probe.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-02-red-uncut.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-02-red-two-solids.log
  modified:
    - src/spur/shaft_model.py
    - src/spur/shaft_params.py
    - tests/test_shaft_model.py
    - tests/test_shaft_params.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md
    - docs/tech_debt/resolved/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md

key-decisions:
  - "The uncut-chamfer guard reads the solid's end face (largest vertex radius of the one planar face at z = 0 must equal tip_d/2 - c), not the volume: the debt item's `upper - volume <= 0` would refuse the heaviest honest shaft (-0.215 mm^3 at c = 0.001)"
  - "shank_d gets its relation on the kernel's evidence (four values, bit-equal volume, equal topology), not on the plan's say-so"

requirements-completed: [REQ-shaft-api, REQ-shaft-web]

coverage:
  - id: D1
    description: "A chamfer the kernel never cut is refused with a BuildError saying the end face was not cut, before any export (D-16, L08)"
    requirement: "REQ-shaft-api"
    verification:
      - kind: test
        ref: "tests/test_shaft_model.py#test_a_chamfer_the_kernel_never_cut_is_refused"
        status: pass
      - kind: other
        ref: "grep -c 'DID NOT RAISE' .planning/phases/33-interfaces-and-parity/investigation/33-02-red-uncut.log (the red against the old guard)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every honest shaft still builds with the new check (42 prior kernel tests) and the doorway exports (model.export STL preview, 209484 bytes)"
    requirement: "REQ-shaft-api"
    verification:
      - kind: test
        ref: "tests/test_shaft_model.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "A kernel result that is not one valid solid is refused, held by a durable test seen red once; the dead re-raise is gone"
    requirement: "REQ-shaft-api"
    verification:
      - kind: test
        ref: "tests/test_shaft_model.py#test_a_kernel_result_that_is_not_one_solid_is_refused"
        status: pass
    human_judgment: false
  - id: D4
    description: "shank_d is declared dim exactly when shank_length is 0, on bit-equal kernel evidence; no other shaft property carries a relation"
    requirement: "REQ-shaft-web"
    verification:
      - kind: test
        ref: "tests/test_shaft_model.py#test_shank_d_changes_nothing_without_a_shank"
        status: pass
      - kind: test
        ref: "tests/test_shaft_params.py#test_shank_d_is_dimmed_without_a_shank"
        status: pass
    human_judgment: false
  - id: D5
    description: "The form actually dims the shank_d box on the shaft page"
    requirement: "REQ-shaft-web"
    verification: []
    human_judgment: true
    rationale: "No front end consumes the relation yet; 33-04 serves it and the generic applyRelations() dims the box from 33-06, proved in the browser in 33-07"

duration: 8min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 02: The shaft kernel's open guards Summary

**`_guard_volume` now reads the chamfer back off the solid's end face, so a cone the kernel never cut is a BuildError instead of a printed `end_chamfer_effective` that is not on the part; the one-valid-solid guard has a durable test, the dead re-raise is gone, and `shank_d` dims without a shank on bit-equal kernel evidence.**

## Performance

- **Duration:** 8 min (started about 2026-10-27T16:05Z, the first read; the executor did not record the start epoch, so the figure is approximate)
- **Completed:** 2026-10-27T16:13Z
- **Tasks:** 3 (1 tracer, 2 auto/tdd)
- **Files modified:** 12 (8 changed, 4 created)

## Accomplishments

- **The probe (`33-02-cut-probe.log`, 2026-10-27, this host)** confirmed the planning read on every row. The end-face reading is within 1.7e-13 mm of `tip_d/2 - c` (worst: the heaviest shaft); the volume cannot carry the guard because the heaviest shaft with an honest 0.001 mm chamfer reads `upper - volume = -0.215028 mm^3` (relative -4.04e-10), so the debt item's own next step (`upper - volume <= 0`) would refuse a good part. The debt's reproduction (the solid of `end_chamfer=0` against the default's `c = 1.0`) reads 1 mm wide of `tip_d/2 - 1.0`. `end_chamfer=0.0001` applies no chamfer (c 0, no CONE face). The heaviest build took 2.86 s with the scan in place.
- **Task 1 (tracer):** `_guard_volume` gains `ra` and, after the bracket and length check, requires exactly one planar face with `zmax` within `TOL` of 0 whose largest vertex radius is `ra - c` within `TOL`. Red against the old guard: `Failed: DID NOT RAISE BuildError` (`33-02-red-uncut.log`). Green after the fix; all 42 earlier kernel tests pass with the new check on every row they build; `model.export(ShaftParams(), "stl", "preview")` returned 209484 bytes.
- **Task 2:** `test_a_kernel_result_that_is_not_one_solid_is_refused` stubs `intersect` on `cq.Shape` and `cq.Compound` to return two disjoint solids. With the `len(solids) != 1 or not isValid()` check deleted it fails on the message it pins (`AssertionError: Regex pattern did not match`; the new end-face check refuses the two solids with a different BuildError, so the test fails exactly because the one-solid sentence is gone); restored, green. `except BuildError: raise` is removed (nothing inside the `try` raises a BuildError).
- **Task 3:** `test_shank_d_changes_nothing_without_a_shank` builds `shank_d` in 1, 25, 60 and 850 at `shank_length=0`: volume `13038.149031505543` for all four (compared with `==`), equal bounding boxes, 93 faces, 273 edges, 182 vertices. So the relation landed (not the idea-file path): `shank_d` carries `enabled_when=[when("shank_length", "gt", 0)]`, pinned in `test_shank_d_is_dimmed_without_a_shank`, which also asserts no other shaft property has one.
- Both debt items retired to `docs/tech_debt/resolved/` with `Status: resolved`, INDEX rows moved, each in its fixing commit and then a sha commit.
- Gate checks: `make verify.fast` 2201 passed, 11.8 s wall (under the 30 s bar); ruff and `mypy` clean on `src/spur` and the touched tests; `make lint-imports` prints `Contracts: 10 kept, 0 broken.`; `make no-fake-done` and `make gear.unchanged` green (gear `/api/schema` 8723 bytes byte-equal to v0.6).

## Task Commits

1. **Task 1: Tracer, a chamfer the kernel never cut is refused** - `3e1eded` (fix), then `7c42369` (docs, sha of the retired must item)
2. **Task 2: The one-solid guard pinned, the dead re-raise dropped** - `49021f5` (test), then `c07cc35` (docs, sha of the retired nice item)
3. **Task 3: `shank_d` dimmed without a shank** - `a07fdb8` (feat)

**Plan metadata:** the `docs(33-02): complete ...` commit that adds this file.

## Files Created/Modified

- `src/spur/shaft_model.py` - `_guard_volume` end-face read-back (docstring carries the probe's numbers); `build_shaft` passes `ra`, no bare re-raise
- `src/spur/shaft_params.py` - `shank_d` `enabled_when`, `when` imported
- `tests/test_shaft_model.py` - the three new kernel tests
- `tests/test_shaft_params.py` - `test_shank_d_is_dimmed_without_a_shank`
- `bench/RESULTS.md` - `### The applied chamfer, read off the end face (33-02)` and two rows under `### Seen red once (Phase 33)`
- `docs/tech_debt/` - INDEX and the two items, moved to `resolved/`
- `investigation/33-02-*` - probe, probe log, two red logs

## Decisions Made

The end-face read-back instead of the debt item's volume test (measured: -0.215 mm^3 on the heaviest honest row), and the `shank_d` relation on kernel evidence. Neither is a new `Lxx`: the first is D-16's own named function with a better test inside it, the second is D-18 and applies L41.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The first Task 1 commit captured only the debt rename**
- **Found during:** Task 1 commit
- **Issue:** my `git add` listed the old `active/` path, which no longer existed after `git mv`, so git aborted the whole `add`; the commit that followed held only the staged rename (`2eca49d`).
- **Fix:** amended that unpushed commit with the full file set (`3e1eded`); the history holds one Task 1 fix commit. The remaining commits listed the paths that exist.
- **Files modified:** none beyond the plan's.
- **Verification:** `git show --stat 3e1eded` lists 8 files; `git status` clean apart from `.planning/milestone.lock`.
- **Committed in:** `3e1eded`

**2. [Plan wording] The Task 2 red fails on a different BuildError message, as the plan's behavior block allows**
- With the one-solid check deleted, the end-face check fires first on the two-solid result, so the failure line is a regex mismatch, not `DID NOT RAISE`. The plan's behavior says "a different BuildError or none"; `33-02-red-two-solids.log` shows `1 failed`.

---

**Total deviations:** 1 auto-fixed (history repair), 1 note on expected behavior
**Impact on plan:** none on scope.

## Issues Encountered

None.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-33-03 is mitigated (end-face read-back, seen red); T-33-04: the heaviest build reads 2.86 s with the scan in place, 33-09's gate delta carries the whole-gate figure. No new network surface.

## Debt and ideas filed

None filed. Two items retired: `docs/tech_debt/resolved/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md` (3e1eded) and `docs/tech_debt/resolved/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md` (49021f5). The idea-file path for `shank_d` did not apply.

## Next Phase Readiness

- The shaft download routes (33-04) can land: a printed applied chamfer is now on the part or the build is refused.
- 33-04 serves `enabled_when` on `shank_d` at `/api/shaft/schema`; 33-06's generic `applyRelations()` dims the box, 33-07 proves it in the browser.
- REQ-shaft-api and REQ-shaft-web are declared by later plans too and stay open until the last declaring plan finishes.

## Self-Check: PASSED

- Files found: the four investigation files, `shaft_model.py`, `shaft_params.py`, both test files and both resolved debt items exist; neither debt item remains under `active/`.
- Commits `3e1eded`, `7c42369`, `49021f5`, `c07cc35` and `a07fdb8` are ancestors of HEAD; `git rev-list --count 5520c4f..HEAD` is 5 (the measured `commits:`).
- Acceptance greps: `end face` 4 times and `_guard_volume(solids[0], area, ra, rf, c` once in `shaft_model.py`; `Status: resolved` once in each item; `DID NOT RAISE` once in the red log; two `| 33-02 |` rows in `bench/RESULTS.md`.
- `requirements.ready-ids` read `0/2 ready`: REQ-shaft-api and REQ-shaft-web are declared by later plans, so they stay open (the frontmatter copies the plan's list verbatim).

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
