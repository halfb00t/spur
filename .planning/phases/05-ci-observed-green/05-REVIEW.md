---
phase: 05-ci-observed-green
reviewed: 2026-09-25T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md
  - docs/tech_debt/active/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md
  - docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md
  - tests/test_pool.py
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-09-25T00:00:00Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

This is the second review of Phase 5, scoped to what changed since commit `a353c94`:
`tests/test_pool.py`'s wedged-worker test (commits `ae052f8`, `3c096de`) and four new
tech-debt records filed from a cross-CLI review of PR #4 plus the CI flake those
commits fixed.

The test fix itself is sound. I traced `test_a_wedged_build_is_terminated_and_its_
worker_replaced` against `src/spur/pool.py`'s `_run_with_timeout`/`recreate_for`: the
manager thread is captured before `recreate_for`'s `shutdown(wait=False)` drops the
executor's reference to it, `manager.join(timeout=5)` is followed by a liveness check
before `proc.exitcode` is read (closing the residual `waitpid` race that `ae052f8`
alone left open), and the signal-number assertion (`-signal.SIGTERM`) is a stronger,
race-free replacement for the old `proc.is_alive()` check. No bug found in the test
logic itself.

The issues are all in the surrounding documentation: three of the four new/updated
tech-debt records contain a factual or attribution error, verified independently
against the actual source they cite (`scripts/pr_land.py`, `.github/workflows/ci.yml`)
rather than taken on the external reviewer's word. One further issue, found
independently: the resolved debt record's provenance is now stale relative to
`3c096de`. None of these are runtime bugs — the shipped test and pool code are
correct — but three are "must"/"nice" tracked items whose own fix guidance would
mislead or misfire if followed literally, which defeats the purpose of filing them.

## Warnings

### WR-01: The unlisted-job debt record's fix guidance names the wrong function and variable (external: codex)

**File:** `docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md:9-10,41`
**Issue:** The record's "Related files" section attributes the per-job verdict loop
(`for name in sorted(required): ...`) to `check_head`, and its "Next step" says "In
`check_head`, refuse when `run.conclusion != "success"`". Neither is where that code
lives. Verified against `scripts/pr_land.py`:
- The loop is inside `head_refusals` (`scripts/pr_land.py:286`), not `check_head`
  (`scripts/pr_land.py:296`). `check_head` only calls `head_refusals` at its end
  (`scripts/pr_land.py:337`).
- Inside `check_head`'s own scope, the name `run` is bound to the `Runner` callable
  parameter (`def check_head(sha: str, run: Runner, required: frozenset[str])`,
  `scripts/pr_land.py:296`) — used throughout that function as `run(["gh", "api", ...])`.
  It has no `.conclusion` attribute; that attribute exists only on `head_refusals`'s
  same-named but differently-typed parameter (`run: WorkflowRun | None`,
  `scripts/pr_land.py:256`). A literal reading of the guidance ("in `check_head`, refuse
  when `run.conclusion`") points at the wrong object and would raise `AttributeError`
  on the `Runner` callable if implemented as written.
**Fix:** Correct the citation and guidance to point at `head_refusals`: "In
`head_refusals`, alongside the per-job loop, refuse when `run.conclusion != "success"`
(`run` here is the `WorkflowRun`, not the `Runner` callable `check_head` takes)."

### WR-02: The drift-test debt record's proposed fix would reject the workflow's own step names (external: codex)

**File:** `docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md:32-34`
**Issue:** The record's "Next step" proposes: "assert that no `name:` key appears in
the `jobs:` section (three lines, next to the existing `assert "test" in job_ids`)".
`jobs_section` in the drift test is `ci_yml.split("\njobs:\n", 1)[1]`
(`tests/test_pr_land.py:195`) — everything under `jobs:`, which includes step-level
`name:` keys, not just job-level ones. `.github/workflows/ci.yml` already has two:
`- name: bundle matches web/` (line 44) and `- name: the packaged entrypoint serves a
gear` (line 58). A literal "no `name:` key in the `jobs:` section" assertion would fail
immediately against the current, correct workflow — the opposite of the record's own
stated goal (catching a *job*-level rename, not flagging legitimate step names).
**Fix:** Scope the proposed assertion to job-level `name:` only — e.g. a regex anchored
to the same two-space job-id indent already used for `job_ids`
(`^  name:\s`, immediately after a job-id line, or restrict the search to lines that
are siblings of the `^  ([a-zA-Z][\w-]*):\s*$` matches) rather than any `name:` in the
whole `jobs:` subtree.

### WR-03: The wedged-build test states an inferred race mechanism as established fact, unlike the debt record it summarizes (external: codex)

**File:** `tests/test_pool.py:173-186`
**Issue:** The comment above `manager.join(timeout=5)` asserts as fact: "the manager
thread and this one wake on the same process sentinel and race to `os.waitpid` for the
same child... The old `proc.join(timeout=5); assert not proc.is_alive()` failed that
way on the GitHub runner on 4 of 5 attempts... with the worker in fact dead". The
resolved debt record this test's fix is drawn from is explicit that this is *not*
established: "The one mechanism found that makes the assertion lie... inferred from
CPython 3.12's source this session, not observed (**ASSUMPTION**)"
(`docs/tech_debt/resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-
runner.md:46-47`), and its own "Next step" section says the race hypothesis is proven
"by the next runner failure printing an exit code instead of `assert not True` -- or by
there being none" — i.e., not yet, at time of filing. `CLAUDE.md` requires guesses to
be flagged as `ASSUMPTION:` and surfaced; the test comment drops that qualifier and
reads as a confirmed diagnosis. A future reader debugging a *different* flake in this
test, working only from the comment (not the resolved debt file), would treat the
`waitpid` race as proven when it is still an inference.
**Fix:** Carry the qualifier into the test comment, e.g. replace "failed that way" with
"is consistent with failing that way (ASSUMPTION, not directly observed — see the
resolved debt record for what was and wasn't checked)".

### WR-04: The resolved wedged-worker debt record's provenance is stale — it doesn't mention `3c096de`'s follow-up fix to its own fix

**File:** `docs/tech_debt/resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md`
**Issue:** This record was moved to `resolved/` in `9cf4a30` ("resolved, the fix itself
is `ae052f8`"), and still says only `Resolved in: ae052f8` with no mention of
`3c096de`. But `3c096de` — committed *after* `9cf4a30` — is itself a fix to a residual
race in `ae052f8`'s fix, found by a Codex re-review of `ae052f8`: `ae052f8`'s version
joined the manager thread and immediately read `proc.exitcode` with no liveness check
in between, and per `3c096de`'s own commit message, "a timed `Thread.join` gives no
guarantee the manager thread finished, and `proc.exitcode` read while it is still
running calls `Popen.poll` -- the same concurrent `waitpid` the fix set out to remove."
That is exactly the class of bug this debt record exists to track, reintroduced by the
record's own prescribed fix and closed by a commit the record never references. A
reader who trusts "Status: resolved, Resolved in: ae052f8" and stops there is trusting
an account that stopped one commit short of what actually shipped.
**Fix:** Amend the record (or its `Related files`/body) to add `3c096de` alongside
`ae052f8` as part of "Resolved in", and note the residual race Codex's re-review found
and what closed it — the same standard of evidence this project applies everywhere
else in this file (it already names run IDs and reproduction counts; this is the one
gap).

---

_Reviewed: 2026-09-25T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
