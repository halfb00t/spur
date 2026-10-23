---
phase: 28-refuse-the-bad-link
fixed_at: 2026-10-22T00:00:00Z
review_path: .planning/phases/28-refuse-the-bad-link/28-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 28: Code Review Fix Report

**Fixed at:** 2026-10-22
**Source review:** .planning/phases/28-refuse-the-bad-link/28-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (IN-03, IN-04; the human chose `fix` for both)
- Fixed: 2
- Skipped: 0
- Not touched: WR-02 (deferred by the human, D-20, debt item filed)

**Verification:** `make verify` ran in the main checkout (`workflow.use_worktrees` is `false`, so
there was no worktree) after both commits: `1348 passed in 214.83s (0:03:34)`, exit clean.
`git diff --exit-code v0.5 -- tests/regression/` is empty.

## Fixed Issues

### IN-03: The old `input.value = to;` pin is now a substring of the new one and can never fail on its own

**Files modified:** `tests/test_api.py`, `docs/architecture/decision_log.md`
**Commit:** cced006
**Applied fix:** Dropped `"input.value = to;"` from the pinned-token tuple and added a comment
beside the L44 token history saying the longer write() token supersedes it. Appended a dated
(2026-10-22) correction at the end of L44, because the WR-01 amendment's "gains an eleventh token
and loses none" is no longer true. No existing sentence was edited.

Deviation from the review: `src/spur/static/app.js` is unchanged. The review says the comment on
`write()` ("test_api.py counts it") claims a count the test does not make. It does make one:
`test_api.py` asserts `len(writes_a_value.findall(selectors.group(1))) == 1` over the selectors
section, and `write()`'s `input.value = to; rejected.delete(field);` is that one match (`write()`
sits after the `-- selectors (L42)` marker). The comment is accurate, so rewording it would have
made it less true. The L44 correction records that count as unchanged.

### IN-04: L45's "only a request under 0.0005 mm prints differently" and the field description both miss the capped-to-zero case

**Files modified:** `src/spur/calc.py`, `docs/architecture/decision_log.md`
**Commit:** 6ff2d55
**Applied fix:** Reworded the `tip_chamfer_effective` field description to "null when no chamfer is
cut: none requested, or the request or the cap rounds below the 0.001 mm resolution it is cut at."
Appended a dated (2026-10-22) correction at the end of L45, widening "Only a request under 0.0005 mm
prints differently" to include a cap that rounds to 0, and naming the "Tip chamfer reduced to 0 mm
..." warning that case takes. The original sentence is untouched. No printed value changes.

## Notes

- The commit messages end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the
  attribution line the session gave, not the `Opus 5.5` line in the task brief.
- `.planning/state.json` and `.planning/milestone.lock` were not staged.

---

_Fixed: 2026-10-22_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
