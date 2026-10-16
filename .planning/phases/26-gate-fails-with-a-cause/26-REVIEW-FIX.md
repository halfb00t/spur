---
phase: 26-gate-fails-with-a-cause
fixed_at: 2026-10-16T00:00:00Z
review_path: .planning/phases/26-gate-fails-with-a-cause/26-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 26: Code Review Fix Report

**Fixed at:** 2026-10-16
**Source review:** .planning/phases/26-gate-fails-with-a-cause/26-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (WR-01, WR-02; Info findings IN-01 to IN-05 were out of scope for this run)
- Fixed: 2
- Skipped: 0

Both fixes are documentation-only edits to `docs/tech_debt/active/` items. No source, test or Makefile file was touched.

## Fixed Issues

### WR-01: The hang item names two different `faulthandler_timeout` values

**Files modified:** `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`
**Commit:** e877d2f
**Applied fix:** Checked `pyproject.toml:133` first: `faulthandler_timeout = 170`. The 2026-10-15 (26-05) paragraph now says 170 and explains that the value was first 120 (sized from a local reading) and was raised to 170 by commit faf376b after the first CI `--durations` reading (run 38750065494, slowest phase 83.55 s). The runbook already said 170 and is unchanged, so the file now has one current value.

### WR-02: The two twin-selectors records disagree on whether the 20 local runs are proof

**Files modified:** `docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md`
**Commit:** 8425d16
**Applied fix:** Read `bench/RESULTS.md` (`### Twin selectors (26-03)`, "What this does and does not show") and the resolved twin item ("Not proven by this commit") first. The Context paragraph now names only the three-run `/api/info` arms and the CX-05 control as proof of the mechanism. It reports the 20 runs as 20 of 20 green, consistent with the fix but not separating it from a fast host, because the old step was not run 20 times on this host. It cites the old step's 2 reds in 8 `main` CI runs, which is the figure RESULTS.md gives. The "Why it matters" paragraph had a sentence ("The local arms stay the proof") that would have kept the contradiction. It now says the only proof that the `main` red is fixed is the post-merge `main` CI read. No new numbers were introduced; the 75 % and 2-in-8 figures were already in the item.

## Verification

- Tier 1: re-read the modified sections of both files; the fix text is present and the surrounding text is intact.
- Where it ran: the main checkout, not a worktree. `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree, temp branch or recovery sentinel was created.
- Root pin guard (`pin.sh`) passed before the edits and before each commit.
- Commit hooks (`make verify.fast` and the skip-token check) passed on both commits.
- Command: `make verify`
- Result line: `1321 passed in 187.95s (0:03:07)`, exit 0.

`.planning/milestone.lock` (untracked) was left alone. Nothing was pushed. No debt or idea item was filed.

---

_Fixed: 2026-10-16_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
