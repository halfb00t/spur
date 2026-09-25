---
phase: 05-ci-observed-green
fixed_at: 2026-09-25T10:05:10Z
review_path: .planning/phases/05-ci-observed-green/05-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 05: Code Review Fix Report

**Fixed at:** 2026-09-25T10:05:10Z
**Source review:** .planning/phases/05-ci-observed-green/05-REVIEW.md
**Iteration:** 1

**Verification environment:** main checkout (`workflow.use_worktrees: false` in
`.planning/config.json` — no worktree was created; edits and commits happened directly
on `gsd/phase-05-ci-observed-green`). Each commit's pre-commit hook ran the full
`make verify` gate (ruff, mypy `--strict`, import-boundary contracts, unfinished-work
scan, pytest) and passed.

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: The unlisted-job debt record's fix guidance names the wrong function and variable

**Files modified:** `docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md`
**Commit:** `6406de1`
**Applied fix:** Verified against `scripts/pr_land.py` that the per-job verdict loop
lives in `head_refusals` (not `check_head`), and that `check_head`'s own `run`
parameter is the `Runner` callable, not the `WorkflowRun` with a `.conclusion`
attribute. Corrected the "Related files" citation and the "Next step" guidance to
point at `head_refusals` and to distinguish the two same-named `run` parameters.

### WR-02: The drift-test debt record's proposed fix would reject the workflow's own step names

**Files modified:** `docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md`
**Commit:** `3d15b2b`
**Applied fix:** Confirmed against `.github/workflows/ci.yml` (lines 44, 58) that the
`jobs:` section already contains two step-level `name:` keys (`bundle matches web/`,
`the packaged entrypoint serves a gear`), and against `tests/test_pr_land.py:195` that
`jobs_section` spans the whole `jobs:` subtree, not just job ids. Rewrote the "Next
step" guidance to scope the proposed assertion to job-level `name:` only, anchored to
the same two-space job-id indent already used for `job_ids`, and named the two
existing step-level `name:` keys that a literal whole-subtree assertion would
immediately trip on.

### WR-03: The wedged-build test states an inferred race mechanism as established fact

**Files modified:** `tests/test_pool.py`
**Commit:** `f3bd1ed`
**Applied fix:** The comment above `manager.join(timeout=5)` (lines 173-188) stated the
`waitpid` race as fact ("failed that way"), while the resolved debt record it
summarizes is explicit the mechanism is an inference from CPython 3.12's source, not
observed, and unproven at time of filing. Reworded to carry the `ASSUMPTION, not
directly observed` qualifier and point at the resolved debt record, and changed "failed
that way" to "is consistent with failing that way." Code (assertions, structure) is
unchanged — comment only. Tier 2 syntax check (`python -c "import ast; ast.parse(...)"`)
passed.

### WR-04: The resolved wedged-worker debt record's provenance is stale

**Files modified:** `docs/tech_debt/resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md`
**Commit:** `c3dcdf0`
**Applied fix:** Verified via `git log` that `3c096de` (committed after `9cf4a30` moved
this record to `resolved/`) fixes a residual race in `ae052f8`'s own fix, found by a
Codex re-review. Added `3c096de` alongside `ae052f8` in the `Resolved in:` field and a
new paragraph in "Next step" naming the residual race (`Thread.join` with no liveness
check before reading `exitcode`), how it was reproduced, and what `3c096de` closed it
with — matching the evidence standard (run IDs, reproduction counts) the rest of the
record already holds. `docs/tech_debt/INDEX.md` was left untouched: its row still says
"see the file's own `Resolved in:` field," which remains accurate, and it is outside
this finding's cited file.

## Skipped Issues

None — all findings were fixed.

---

_Fixed: 2026-09-25T10:05:10Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
