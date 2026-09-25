---
phase: 06-address-tech-debt-merge-gate-solid-cache
plan: 01
subsystem: cad-kernel
tags: [cadquery, opencascade, solid-cache, tdd, pytest, tech-debt]

# Dependency graph
requires: []
provides:
  - "`_write_export`'s STL branch meshes `shape.copy()`, never the cached solid itself"
  - "Content-equivalence tests (`test_exporting_leaves_the_cached_solid_exact`, `test_an_stl_export_matches_a_first_export_whatever_came_before`) proving a cached solid never carries a mesh"
  - "`tests/conftest.py`'s autouse solid-cache reset deleted; `make verify` passes without it"
  - "`docs/architecture/decision_log.md` L24 -- the solid-cache invariant with every measured number"
  - "The `2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` debt file retired"
affects: []

# Actuals (#2632) -- pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 4774
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Content equivalence (triangle count + decoded volume within rel=1e-6), not raw STL-byte equality, for asserting two OCCT exports carry the same geometry -- OCCT export matched byte-for-byte in only 8 of 20 reruns across independently built solids"
    - "A reference export built on a solid the cache never handed out (`_export_in_place`, calling `_build_checked` directly) as the ground truth a cached-path export must match"

key-files:
  created: []
  modified:
    - src/spur/model.py
    - tests/test_model.py
    - tests/conftest.py
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md
    - "docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md -> docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md (git mv)"

key-decisions:
  - "shape.copy() before exportStl(), not BRepTools.Clean_s() -- Clean_s measured 4-13% faster but strips the mesh after export, so the cached object would carry a mesh through the whole export window while build() releases _LOCK before callers read the solid (human decision at plan time, CONTEXT.md D-08 amendment (b))"
  - "Prove content equivalence (triangle count + decoded volume), never raw STL bytes, between independently built or copied solids (CONTEXT.md D-08 amendment (c))"
  - "No replacement autouse fixture for the deleted solid-cache reset (D-09) -- the suite-wide make verify pass with it gone is the cross-test proof; no test needed a local reset"

patterns-established:
  - "Content-equivalence testing over byte-diff testing for OCCT/CadQuery exports"

requirements-completed: [D-01, D-08, D-09, D-10]

coverage:
  - id: D1
    description: "A solid returned by _build_cached never carries a mesh: .BoundingBox() reads the exact BREP after any export, and every STL export has the content of a first export of that gear (D-08)"
    requirement: "D-08"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_exporting_leaves_the_cached_solid_exact"
        status: pass
      - kind: integration
        ref: "tests/test_model.py#test_an_stl_export_matches_a_first_export_whatever_came_before"
        status: pass
      - kind: other
        ref: "make test PYTEST_ARGS=\"tests/test_model.py -q -k 'cached_solid_exact or first_export'\""
        status: pass
    human_judgment: false
  - id: D2
    description: "The autouse solid-cache reset fixture is gone and the whole suite passes without it (D-09)"
    requirement: "D-09"
    verification:
      - kind: other
        ref: "make verify (185 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "L24 records the solid-cache invariant with every measured cost/RSS number, appended after L23 with no existing line removed (D-10)"
    requirement: "D-10"
    verification:
      - kind: other
        ref: "docs/architecture/decision_log.md L24 content grep + git show --numstat (0 deletions)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The debt file is resolved, moved, and indexed in the same commit that adds L24, naming Task 1's fixing commit (D-01)"
    requirement: "D-01"
    verification:
      - kind: other
        ref: "docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md + docs/tech_debt/INDEX.md"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min
completed: 2026-09-25
status: complete
---

# Phase 6 Plan 1: Solid-Cache Mesh Isolation Summary

**`_write_export`'s STL branch now meshes `shape.copy()` instead of the process-global cached `cq.Solid`, closing the one production-latent `must` debt item (D-08/D-09) with content-equivalence tests, not a byte diff.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 2
- **Files modified:** 6 (3 code/test, 1 decision log, 1 debt file moved+edited, 1 index)

## Accomplishments

- `src/spur/model.py`'s `_write_export` STL branch calls `exportStl` on `shape.copy()`
  (no positional arg -- `copy(mesh=True)` would carry a mesh across); the STEP branch is
  unchanged (it never attached a mesh).
- Two new tests in `tests/test_model.py` prove D-08 directly: the cached solid stays
  exact through a preview/fine/STEP export sequence
  (`test_exporting_leaves_the_cached_solid_exact`), and every STL export has the content
  of a fresh export regardless of what was exported before
  (`test_an_stl_export_matches_a_first_export_whatever_came_before`), matched against a
  new `_export_in_place` helper that builds a solid the cache never hands out.
  `test_exported_stl_is_a_closed_consistently_oriented_shell`'s topology assertions moved
  into a reusable `_closed_shell_volume` helper the new tests share.
- `tests/conftest.py`'s autouse `_reset_solid_cache` fixture, its import, and its
  docstring paragraph are deleted (D-09); the full 185-test suite passes without it.
- `docs/architecture/decision_log.md` gained `## L24` recording the defect, the
  invariant, why a copy beats `BRepTools.Clean_s` (measured faster but wrong window),
  every timing and RSS number from both the research and planning sessions, and the
  content-equivalence proof -- appended after L23 with zero lines removed from the file.
- `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`
  retired: `git mv`'d to `resolved/`, `Status: resolved`, `Resolved in: 655ec52` (Task 1's
  fixing commit), a dated `## Resolution` section correcting two of the file's own
  findings without touching its Context, and the INDEX row moved -- all in the same
  commit that adds L24 (D-01's "never a bookkeeping-only follow-up").

## Task Commits

Each task was committed atomically. Both TDD tasks land RED + GREEN in one commit per
this project's established convention (STATE.md Phase 3: the pre-commit hook runs the
full `make verify` with no bypass, so a separate failing-test commit would itself fail
the hook):

1. **Task 1: End to end -- an STL export never meshes the cached solid** -
   `655ec52` (fix) -- RED confirmed on the two new tests (zlen 7.519603716332508 vs
   expected ~7.5; preview 46278 vs expected 9066 triangles, 13 passed/2 failed), then the
   one-line `shape.copy()` fix and the D-09 fixture deletion, verified by
   `make verify` (185 passed).
2. **Task 2: L24 records the solid-cache invariant; debt file retired** -
   `f17bda0` (docs) -- appended L24, moved and annotated the debt file, updated the
   INDEX. Amended twice in place before any other work depended on it: once because a
   failed `git add` pathspec silently dropped `decision_log.md`/`INDEX.md` from staging
   (caught by post-commit verification, not by `make verify`, which only checks the
   files it is given), once to fix an "8 of 20" acceptance-criteria token that had
   wrapped across two lines in the markdown source. Both amends predate any push or
   dependent work.

**Plan metadata:** committed alongside this SUMMARY per the standard docs commit step.

## Files Created/Modified

- `src/spur/model.py` - `_write_export`'s STL branch meshes `shape.copy()`, with the
  why-comment carrying the measured cost (1.4-17.6 ms/export, L24)
- `tests/test_model.py` - two new D-08 tests, `_closed_shell_volume` and
  `_export_in_place` helpers, the existing shell test refactored onto the shared helper
- `tests/conftest.py` - `_reset_solid_cache` fixture, its import and its docstring
  paragraph removed (D-09)
- `docs/architecture/decision_log.md` - `## L24` appended
- `docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` -
  moved from `active/`, `Status: resolved`, `## Resolution (2026-09-25)` section
- `docs/tech_debt/INDEX.md` - row moved from `## Active` to `## Resolved`

## Decisions Made

- `shape.copy()` over `BRepTools.Clean_s` -- the human's plan-time call (CONTEXT.md D-08
  amendment (b)), reconfirmed by this plan's own research numbers: `Clean_s` measured
  4-13% faster but strips the mesh *after* export, so the cached object would carry a
  mesh through the entire export window rather than never at all.
- Content equivalence (triangle count + decoded volume, `rel=1e-6`), never raw STL bytes,
  as the D-08 proof (CONTEXT.md D-08 amendment (c)) -- OCCT export matched byte-for-byte
  in only 8 of 20 reruns across independently built solids at planning/research time.
- No replacement autouse fixture for the deleted solid-cache reset (D-09) -- flagged
  assumption 4 held: `make verify`'s 185-test pass with the fixture gone is the only
  cross-test proof needed; no test relied on a cold cache for an unrelated reason.

## Deviations from Plan

None - plan executed exactly as written. (Two mid-task self-corrections via
`git commit --amend` are documented under Task Commits above -- both fixed my own
staging/formatting mistakes before the commit's SHA was referenced by any other work,
not a deviation from the plan's design.)

## Issues Encountered

- A `git add` invocation that named a since-`git mv`'d path (a leftover from composing
  the command before the move) exited non-zero and silently staged none of its other
  listed paths, including two files (`decision_log.md`, `INDEX.md`) meant for the Task 2
  commit. `make verify`'s pre-commit hook does not catch this -- it only checks what is
  staged. Caught by re-running the plan's own post-commit acceptance-criteria checks
  (`git show --name-only` on the commit), which is exactly the kind of drift those
  checks exist to catch. Fixed with `git commit --amend` before anything else referenced
  the commit's SHA. Lesson for future plans: stage each file with its own `git add`
  call, or verify `git status --short` shows no unstaged changes immediately after a
  multi-path `git add`, rather than trusting the command's exit code alone when one
  pathspec might not match.
- A required acceptance-criteria token ("8 of 20") happened to fall across a markdown
  line wrap in the first draft of L24, so the literal-string grep check failed on first
  run. Reworded the sentence so the token stays on one line; re-verified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

D-08 and D-09 are closed: the cached solid is provably mesh-free after any export, and
the suite needs no cache reset. D-10 and D-01's bookkeeping are done in the same commit
as the fix. Plans 06-02, 06-03, and 06-04 (merge-gate hardening) are independent of this
plan's changes per the phase's source audit and can proceed in any order relative to it.

---
*Phase: 06-address-tech-debt-merge-gate-solid-cache*
*Completed: 2026-09-25*

## Self-Check: PASSED

- FOUND: `.planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-01-SUMMARY.md`
- FOUND: commit `655ec52` (Task 1)
- FOUND: commit `f17bda0` (Task 2)
- FOUND: `shape.copy().exportStl(` in `src/spur/model.py`
- FOUND: `docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`
- CONFIRMED: no `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` remains
