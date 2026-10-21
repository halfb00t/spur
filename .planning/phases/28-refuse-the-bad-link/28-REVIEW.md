---
phase: 28-refuse-the-bad-link
reviewed: 2026-10-22T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/web-ui.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md
  - docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md
  - src/spur/calc.py
  - src/spur/static/app.js
  - tests/test_api.py
  - tests/test_browser.py
  - tests/test_calc.py
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 28: Code Review Report

**Reviewed:** 2026-10-22
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Incremental re-review of `b62cc54..HEAD`: the gap-closure commits 6497c28 (L45), 3224ec7 (L44 amendment),
aede0fd (single mate assignment, longer pin) and 2368718 (web-ui.md re-wrap).

Closed by the diff, verified against the code and not re-raised:

- WR-01 (a pick that writes a rejected field kept sending the old token). `write()` now calls
  `rejected.delete(field)` as it assigns the box. I traced every programmatic writer of a field box: `write()`
  (reached from `pick()` and `completePending()`), `readHash()` and Reset. The latter two clear `rejected`
  themselves. No writer is left that assigns a box and leaves a stale token. The new `#bore_d=abc` then "No bore"
  step asserts `bore_d=0`, and `_pick`, `_follow_link` and `recovered` all exist and are used consistently.
- WR-03 (`tip_chamfer_effective` gated on the request). It is now `r3(tch) if tch > 0 else None`. `tch` comes from
  `tip_chamfer_effective()`, which already rounds to 3 dp, so `tch > 0` is exactly "a chamfer is cut" and `model.py`'s
  own `c <= 0` early return is the same test. The two sites cannot disagree. The other tests that read the field
  (`test_model.py:902, 956, 990`, `test_calc.py:1477`) are unaffected. I swept 304 (teeth, shift, angle, fillet,
  root shape) combinations for a limit under 0.0005 mm and found none, so no pinned record moves, consistent with
  the L45 fixture claim.
- IN-01 (`readHash()` double assignment). Removed. `refuse()` only reads the box, so the single assignment is
  correct. The longer pin is 162 columns with a `noqa: E501`, matching the neighbouring pin's precedent.
- IN-02 (190-character line). Re-wrapped; the Shape paragraph's lines are now 78 to 91 characters like their neighbours.

One earlier finding is still true and is carried forward under its original title. Two small new items follow.
The new items take ids IN-03 and IN-04, so no earlier id in the disposition ledger is reused.

## Warnings

### WR-02: A token the box blanks but the API accepts builds a non-default part under a blank box

**File:** `src/spur/static/app.js:115-117` (refuse), `src/spur/static/app.js:132-139` (gearQuery), `tests/test_browser.py` (`ACCEPTED_LINK = "face_width=5."`)
**Issue:** Unchanged by this diff. For ` 22`, `22 `, `1_0` (`teeth`, `face_width`) and `22.`, `5.`, `+5` (`face_width`), the
number box reads back `''`, `refuse()` records the token, `gearQuery()` sends it, and the API answers 200. The part is
built from the token while the form shows a blank box, which the page's own convention (D-06) reads as "default". That
is a standing L05 tension: a value the form does not display changes the part. The 28-REVIEW disposition deferred it
(D-20) and `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` now records it with a
concrete trigger (next edit of `refuse()` or `gearQuery()`, or a report). The filing is sound and the trigger is a real
event, which fixes the earlier complaint about unschedulable debt. This stays a WARNING because the behaviour is
unchanged and still visible in the shipped page.
**Fix:** Tracked in the debt item. The honest options are a page-written notice beside the server's messages, or putting
the token in the control's `title` or `placeholder`. Either needs a UI design decision, so take it at a discuss-phase as
the item says. Until then no code change is requested here.

## Info

### IN-03: The old `input.value = to;` pin is now a substring of the new one and can never fail on its own

**File:** `tests/test_api.py:295-296`
**Issue:** The 3224ec7 change added the token `"input.value = to; rejected.delete(field);"` directly under the existing
`"input.value = to;"`. The check is `snippet in collapsed_source`, so the shorter token is satisfied whenever the longer
one is, and it cannot go red unless the longer one already did. It reads as an independent pin of "write() assigns the
box" while adding no coverage. The L44 amendment's claim that the suite "gains an eleventh token and loses none" is true
by count, but the shorter token is now dead weight, and the app.js comment on `write()` ("the one statement in this
section that writes a field (test_api.py counts it)") still describes a count the test does not make.
**Fix:** Drop `"input.value = to;"` from the tuple and note in the comment that the longer token supersedes it. Or keep
it with a comment saying it is deliberately subsumed. Fix the `write()` comment so it does not claim a count.

### IN-04: L45's "only a request under 0.0005 mm prints differently" and the field description both miss the capped-to-zero case

**File:** `docs/architecture/decision_log.md` (L45, **What moves**), `src/spur/calc.py:973-977`
**Issue:** `tip_chamfer_effective()` is `round(min(request, limit), 3)`. It rounds to `0.0` for a request under 0.0005
mm, and also for any request whose limit under the tip-land, pitch-circle or flank bound is under 0.0005 mm. In that
second case `tch == 0.0` while `p.tip_chamfer > 0`, so the field now also prints `null`, which the old gate printed as
`0.0`, and the warning is the "Tip chamfer reduced to 0 mm ..." branch, not the "below the 0.001 mm resolution"
branch. L45 says "Only a request under 0.0005 mm prints differently", and the new description says "null when none is
cut: none requested, or a request below the 0.001 mm resolution". Both are narrower than the code. I could not reach
the second case in a 304-combination sweep, so this is a statement-accuracy defect, not a reproduced misprint, and the
printed number is still honest (null with no chamfer cut).
**Fix:** Reword the description to "null when no chamfer is cut: none requested, or the request or the cap rounds below
the 0.001 mm resolution it is cut at". Add a one-line correction to L45 in a following amendment rather than editing
the entry.

---

_Reviewed: 2026-10-22_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
