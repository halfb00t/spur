---
phase: 06-address-tech-debt-merge-gate-solid-cache
reviewed: 2026-09-25T13:32:31Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - docs/architecture/decision_log.md
  - docs/HOW_TO_DEVELOP.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md
  - docs/tech_debt/resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md
  - docs/tech_debt/resolved/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md
  - docs/tech_debt/resolved/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md
  - docs/tech_debt/resolved/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md
  - scripts/pr_land.py
  - scripts/skip_tokens.py
  - src/spur/model.py
  - tests/conftest.py
  - tests/test_model.py
  - tests/test_pr_land.py
  - tests/test_skip_tokens.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: clean
---

# Phase 06: Code Review Report

**Reviewed:** 2026-09-25T13:32:31Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** clean

## Summary

Four independent fixes, each closing a filed tech-debt item: (1) `_write_export`'s STL
branch now meshes `shape.copy()` instead of the process-cached `cq.Solid` itself, closing
the shared-solid-cache corruption; (2) the commit-msg hook drops its cut-line heuristic
entirely and searches the whole buffer git hands it; (3) `pr.land`'s `head_refusals` now
also refuses on a completed run's own `conclusion != "success"`, independent of the
per-job loop, and the required-jobs drift test now derives GitHub's effective job names
(`jobs.<id>.name` override, else id) instead of raw ids; (4) `pr.land`'s post-merge
"nothing appeared" message (`no_run_report`) now reports exactly one of three things it
actually observed — a poll's last read error, an Actions link, or a skip token read from
the squash commit's own message — instead of asserting a skip token unconditionally.

Verification performed independent of the phase's own artifacts, against the actual
tree at HEAD:

- `git diff b72b0e1..HEAD -- docs/architecture/decision_log.md` shows only additions —
  L22/L23 are untouched, L24/L25 are strictly appended.
- `.venv/bin/pytest tests/test_pr_land.py tests/test_skip_tokens.py` — 85 passed.
- `.venv/bin/pytest tests/test_model.py` — 15 passed.
- `.venv/bin/ruff check` and `.venv/bin/mypy --strict` on all five changed `.py` files —
  clean.
- The five `Resolved in:` commit shas cited in the tech-debt files
  (`655ec52`, `e46ed34`, `9ca8320`, `e4345a4`, `0573319`) all resolve to real commits in
  this history.
- `docs/HOW_TO_DEVELOP.md`'s new §8 prose was checked sentence-by-sentence against
  `scripts/pr_land.py`'s actual step order and `no_run_report`'s three branches — no
  drift found.
- `tests/test_pr_land.py`'s `_effective_job_names` regex helper was checked against the
  real `.github/workflows/ci.yml` and `.github/workflows/required-jobs.txt` — they
  agree, and the `image:`-rename regression case correctly excludes both of `ci.yml`'s
  step-level `name:` keys.
- Traced every `subprocess.run` call in `scripts/pr_land.py` and `scripts/skip_tokens.py`:
  all pass `argv` as a list with no `shell=True` — no command-injection surface from
  `pr.title`, `pr.body`, `pr.head_branch` or any sha interpolated into a `gh api` path.

No logic errors, unhandled edge cases, or security gaps were found in the phase's own
diff. The two items below are minor, non-blocking observations on new code, not defects
that change behavior incorrectly.

## Info

### IN-01: A `None` run conclusion prints as the literal word `None` in a refusal

**File:** `scripts/pr_land.py:295-299`
**Issue:** `head_refusals`'s new branch does `f"...concluded {run.conclusion!r}, not
success: {run.html_url}"`. `WorkflowRun.conclusion` is typed `str | None`; for a
`status == "completed"` run this should always be a real string in practice (GitHub
does not report `null` conclusions on completed runs), but nothing here enforces that
short of GitHub's own API contract, and `!r` on `None` renders as `concluded None, not
success`, not a quoted string. Harmless today — no test exercises a completed run with
a null conclusion — but a reader debugging live `pr.land` output would see an
un-quoted `None` and might mistake it for a missing f-string substitution.
**Fix:** Not urgent; if ever exercised, `run.conclusion or "<no conclusion>"` would read
more clearly than the bare `None`.

### IN-02: `no_run_report` drops the poll loop's `last_error` if the final commit read also fails

**File:** `scripts/pr_land.py:404-406`
**Issue:** When every poll attempt fails, `last_error` holds the most recent poll
failure. If the subsequent read of the squash commit's own message (done once, after
the poll loop, to look for a skip token) *also* fails, `no_run_report` reports only the
commit-read failure and silently discards the poll's `last_error` — the two distinct
failure signals (repeated poll failures vs. a one-off commit read failure, which could
indicate different root causes, e.g. sustained rate-limiting vs. a transient blip) are
never both surfaced. Consistent with the docstring's "a failed commit read *or* the
poll's own last error gives the last-error report" and covered by
`test_no_run_report_a_failed_commit_read_is_the_last_error` (which only exercises the
commit-read failure in isolation, with `last_error=None`) — no test exercises the
double-failure case, so this is an intentional simplification rather than an oversight,
but it does mean a real double-failure (e.g. `gh auth` expiring mid-poll) reports only
the last symptom.
**Fix:** Optional: `f"{prefix}; last error: {error}" + (f" (poll: {last_error})" if
last_error else "")` if both signals are ever wanted; not worth the complexity unless
this message is seen for real with both causes present.

---

_Reviewed: 2026-09-25T13:32:31Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
