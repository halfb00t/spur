---
phase: 28-refuse-the-bad-link
verified: 2026-10-22T02:00:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/phases/28-refuse-the-bad-link/28-01-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-01-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-02-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-02-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-03-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-03-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-04-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-04-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-05-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-05-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-06-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-06-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-07-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-07-SUMMARY.md"
  - ".planning/phases/28-refuse-the-bad-link/28-08-PLAN.md"
  - ".planning/phases/28-refuse-the-bad-link/28-08-SUMMARY.md"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/web-ui.md"
  - "src/spur/calc.py"
  - "src/spur/static/app.js"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_calc.py"
covered_digest: "v3:sha256:7d586c24ad7f1ca8e219bd353cebfbabfced3a291efab97c75f753595569c511"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5
  gaps_closed:
    - "G-28-1: Phase 28's own review findings (WR-01, WR-02, WR-03, IN-01, IN-02, plus re-review IN-03, IN-04) all dispositioned; open: 0"
    - "G-28-2: tip_chamfer_effective printed 0.0 for an uncut chamfer; fixed under L45 (6497c28)"
  gaps_remaining: []
  regressions: []
---

# Phase 28: Refuse the Bad Link Verification Report

**Phase Goal:** A shared link carrying a value its form control cannot hold is refused visibly, through the existing 422 marking path, instead of silently building the default part, decided and recorded as `L44`. In this last code phase, every open review info finding of the milestone ends dispositioned, none left `open`.
**Verified:** 2026-10-22
**Status:** passed
**Re-verification:** Yes, after gap closure (plans 28-05..28-08, then the re-review fixes cced006 and 6ff2d55)

## Verdict

The goal is achieved at HEAD `e6480cb`. I read the tree and ran the checks myself; I did not take the SUMMARYs as evidence. The one clause the first verification left open, "none left open, of the milestone", is now literally true: no disposition file anywhere under `.planning` has a row at `open`. The gate passes on HEAD.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A bad link (`#root_shape=bogus`, `#recess_sides=bogus`, `#teeth=abc`, `#mate_teeth=abc`) keeps its token, is sent, and is marked through the existing 422 path; no default part is built. Edit or Reset clears. | VERIFIED | `src/spur/static/app.js`: `rejected` Map (line 15), `refuse()` (115-117), set after assignment in `readHash()` (121-128), sent raw in `gearQuery()` (135), mate fallback in `update()` (263), cleared on input (631, 634) and Reset (642). Browser steps `bad link refused`, `bad link cleared`, `bad link on a fresh page` ran inside `test_the_shipped_viewer_in_a_real_browser`, which passed in my `make verify`. |
| 2 | Every valid link is unchanged: blank still means default, unknown keys ignored, golden requests unchanged, `test_api.py` pins held or tightened. | VERIFIED | `git diff --exit-code v0.5 -- tests/regression/` exits 0 (run by me). The `test_api.py` diff since 530110f only drops the one subsumed token (see IN-03 below); the longer token that contains it stays. |
| 3 | The decision is logged and the old pin flipped in the same commit: `L44` amends L39, red-then-green evidence, `web-ui.md` true, debt item retired. | VERIFIED | `decision_log.md:2948` `## L44`. Red logs in `investigation/28-01-red-old-pin.log` and `28-01-red-new-pin.log`. Debt item `2026-10-10-root-shape-bogus-loads-a-blank-select.md` is in `docs/tech_debt/resolved/`. `web-ui.md` cites L44. |
| 4 | The `root_fillet` label follows the root, text only, own commit. | VERIFIED | `app.js:30` keys the label on `d.root_form_d != null`. `calc.py:1292` sets `root_form_d` only when `rm.curve` exists. No number moved (regression diff empty). |
| 5 | No review info finding is left `open`: 19, 21-24 dispositioned, vacuous-pass findings fixed, 18 and 10 triaged as specified. | VERIFIED | `grep -rn '| info | open |'` over all 18 `*REVIEW-DISPOSITION.md` files (milestones v0.2 to v0.5, phases 26 to 28) prints nothing. `grep -rn '| open |'` over the same files prints nothing, and no file has a non-zero `open:` front-matter count. This includes Phase 28's own ledger. |

**Score:** 5/5 truths verified, 0 present-but-behavior-unverified.

### Gap closure

| Gap | Resolution | Evidence |
|-----|------------|----------|
| G-28-1: Phase 28's own review untriaged | Closed | `28-REVIEW-DISPOSITION.md` is `open: 0`, `total: 7`. WR-01 `fixed` (3224ec7), WR-03 `fixed` (6497c28, L45), IN-01 `fixed` (aede0fd), IN-02 `fixed` (2368718), IN-03 `fixed` (cced006), IN-04 `fixed` (6ff2d55), WR-02 `deferred` with a debt path. All shas resolve in the log. |
| G-28-2: `tip_chamfer_effective` printed `0.0` for an uncut chamfer | Closed | `calc.py:1299` is `r3(tch) if tch > 0 else None`, gated on the applied value. L45 is logged (`decision_log.md:3029`). `tests/test_calc.py:691-692` asserts `is None`, and `investigation/28-06-red-tip-chamfer-null.log` shows it red against the old gate (`assert 0.0 is None`). The fixture check log reads "44 records, no held field moved". The debt item is in `resolved/` and the INDEX row is moved. |

### Re-review items

| ID | Result |
|----|--------|
| WR-02 (accepted token under a blank box) | Deferred by the human (D-20). Debt item `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` exists, INDEX row 34, with a concrete trigger (next edit of `refuse()` or `gearQuery()`, or a report). This is a recorded, scheduled decision, not an open defect. The behavior is documented in L44 and visible, so the "never silently change the part" rule is held by the 422/accepted-token pins. |
| IN-03 (subsumed pin) | Fixed in cced006: `"input.value = to;"` dropped, the longer `"input.value = to; rejected.delete(field);"` kept, a comment and an L44 amendment record it. The re-review's second claim, that the `write()` comment states a count the test does not make, is wrong, as the orchestrator said. `tests/test_api.py:424` asserts `len(writes_a_value.findall(selectors.group(1))) == 1`, and `write()`'s assignment is that one match. I confirmed it, and the passing suite exercises it. Leaving `app.js` unchanged was correct. |
| IN-04 (capped-to-zero case) | Fixed in 6ff2d55: the field description in `calc.py` is reworded, and L45 has a dated amendment. No value changes. The wording matches `tip_chamfer_effective()`'s `round(min(request, limit), 3)`. |

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `src/spur/static/app.js` (`rejected`, `refuse`, `write()` delete, label) | VERIFIED | Substantive and wired; see the line references in Truth 1. |
| `src/spur/calc.py:1299` (applied-value gate) | VERIFIED | Matches L45. |
| `tests/test_browser.py`, `tests/test_api.py`, `tests/test_calc.py` | VERIFIED | Exercised in the passing run. |
| `docs/architecture/decision_log.md` L44 and L45 | VERIFIED | Both present with dated amendments, no existing sentence edited. |
| `docs/architecture/web-ui.md` | VERIFIED | The Shape paragraph is re-wrapped (lines 78 to 89 characters). Lines 79 and 88 (102 and 126 characters) sit in other sections, were not raised by any review, and are cosmetic only. |
| Disposition ledgers (18 files) and debt/idea items | VERIFIED | All dispositioned, all cited paths exist. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `readHash()` | `gearQuery()` / `update()` via `rejected` | WIRED | Same Map, written in `readHash`, read in both, deleted in `write()`, the input listeners and Reset. |
| `derive()` `tch` | `tip_chamfer_effective` field | WIRED | `calc.py:1120` to `1299`, the same value `model.py` uses to cut. |
| Each `fixed` disposition cell | a commit | WIRED | 3224ec7, 6497c28, aede0fd, 2368718 and the two re-review commits are all in `git log`. |
| Each `deferred` cell | an existing file | WIRED | The WR-02 debt file exists and is indexed. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Whole gate on HEAD `e6480cb` | `make verify` | `1348 passed in 203.46s (0:03:23)`, exit 0 | PASS (run by me) |
| Regression fixtures unchanged | `git diff --exit-code v0.5 -- tests/regression/` | exit 0, empty | PASS |
| No open info row, any ledger | `grep -rn '\| info \| open \|'` over 18 disposition files | no output | PASS |
| No open row of any severity | `grep -rn '\| open \|'` over the same | no output | PASS |

### Probe Execution

SKIPPED. No probe is declared in the Phase 28 plans.

### Requirements Coverage

| Requirement | Source Plan(s) | Status | Evidence |
|-------------|----------------|--------|----------|
| REQ-bad-link-refused | 28-01, 28-07 | SATISFIED | Truths 1 and 2 |
| REQ-bad-link-decision-logged | 28-01, 28-07 | SATISFIED | Truth 3, plus the L44 amendments for WR-01, IN-01 and IN-03 |
| REQ-root-fillet-label-follows-root | 28-02 | SATISFIED | Truth 4 |
| REQ-info-findings-triaged | 28-01 to 28-08 | SATISFIED | Truth 5 and G-28-1 |
| REQ-old-info-findings-triaged | 28-03, 28-04, 28-05, 28-06 | SATISFIED | 18 IN-02/06 skipped with reason, IN-07 fixed, the rest filed as one `nice` item, and 10 IN-02 resolved by L45 under D-21 (a human decision, as the requirement specified). |

**Traceability, the open item the orchestrator asked about.** `requirements mark-complete` reported `applied: false` for REQ-bad-link-decision-logged during 28-07, and I checked why it matters. It does not. `.planning/REQUIREMENTS.md` already has `- [x]` for all five IDs (lines 94, 101, 106, 112, 117) and the traceability table (lines 187-191) lists all five as `Phase 28 | Complete`. The file is committed (last change `a01bb05`), so `applied: false` is a no-op on an already-complete row. All five IDs appear in PLAN frontmatter and `requirements-completed` in the SUMMARYs. No ORPHANED requirement.

### Anti-Patterns Found

None. The unfinished-work scan is part of `make verify` and exited 0. The `readHash()` duplicate assignment (old IN-01) is gone.

### Human Verification Required

None. Both items from the first report are closed: the 28-review ledger is dispositioned (G-28-1), and the `tip_chamfer_effective` decision is taken and logged as L45 (G-28-2). The remaining deferred item (WR-02) is a recorded human decision with a concrete trigger.

### Gaps Summary

No gaps. Housekeeping for the orchestrator, outside my remit: `28-UAT.md` still shows `status: diagnosed` with both tests as `issue`. It should be re-run or closed against this report. Also `.planning/state.json` and `.planning/milestone.lock` are unstaged and not part of the phase.

---

_Verified: 2026-10-22_
_Verifier: Claude (gsd-verifier)_
