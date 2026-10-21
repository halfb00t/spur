---
phase: 28-refuse-the-bad-link
verified: 2026-10-21T14:00:00Z
status: human_needed
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
  - "Makefile"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/web-ui.md"
  - "src/spur/calc.py"
  - "src/spur/static/app.js"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_browser_pins.py"
covered_digest: "v3:sha256:9467640750f23c1f178a2ccecbcc9601888c7f4b34cc84950b495651495e0048"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Disposition Phase 28's own review (28-REVIEW-DISPOSITION.md): IN-01 and IN-02 (info) and WR-01, WR-02, WR-03 (warning), all still `open`"
    expected: "Each carries fixed + sha, deferred + debt/idea path, or skipped + reason, before the milestone closes. The roadmap's own grep ('| info | open |') is clean for Phases 10, 18, 19, 21-24, 26 and 27 but prints two rows for Phase 28."
    why_human: "The goal sentence says 'every open review info finding of the milestone ... none left open'. Whether 28's own review counts toward that clause, and whether WR-01/WR-02 are fixed now or accepted under L44, is a scope call for the developer."
  - test: "Decide WR-03 / Phase 10 IN-02: tip_chamfer_effective prints 0.0 for a chamfer that was asked for and not cut (src/spur/calc.py:1294)"
    expected: "Either a new Lxx plus a fix (gate on tch, print null) with its own `make fixture.regen` check, or keep-with-reason logged. The INDEX trigger is currently 'the human's decision'."
    why_human: "The phase requirement REQ-old-info-findings-triaged says this is filed as a decision for the human and not fixed. The phase did that. The open question is when the human takes it."
---

# Phase 28: Refuse the Bad Link Verification Report

**Phase Goal:** A shared link carrying a value its form control cannot hold is refused visibly, through the existing 422 marking path, instead of silently building the default part, decided and recorded as `L44`. In this last code phase, every open review info finding of the milestone ends dispositioned, none left `open`.
**Verified:** 2026-10-21
**Status:** human_needed
**Re-verification:** No, initial verification

## Verdict

The code goal is achieved, and I checked it against the tree and not the SUMMARYs. One clause of the goal sentence is not closed. The roadmap's own measure for that clause (SC5, the `| info | open |` grep) is clean for every phase it names. The phase's own post-execution review, though, left `IN-01` and `IN-02` as `open`, so "none left open, of the milestone" is literally false at HEAD. I rate that a milestone-close item, not a failure of the phase's deliverable (see Truth 5). I did not edit any code.

## Goal Achievement

### Observable Truths (ROADMAP success criteria, the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A bad link is refused visibly: `#root_shape=bogus`, `#recess_sides=bogus`, `#teeth=abc`, `#mate_teeth=abc` keep the token in the fragment, send it, and are marked through the existing 422 path with the server's own text. No STL request, no default part. Edit or Reset clears. | VERIFIED | `app.js` (`cb93d4e`): `rejected` Map (line 15), `refuse()` (113-115) runs after assignment in `readHash()` (123-128), `gearQuery()` early branch sends the raw token, `update()` mate fallback (263), clearing listeners and Reset's `rejected.clear()`. `fail()` returns before the STL fetch (292-293). `tests/test_browser.py` steps `bad link refused` (loops `BAD_LINKS`: 5 links), `bad link cleared`, `bad link on a fresh page`. The expected text is derived from the API's own 422 body (`_expected_422`), never a literal. The steps assert the sent pairs equal the link's, the fragment keeps the token, the STL request count is unchanged and no `#dl-stl` href is set. `test_the_shipped_viewer_in_a_real_browser` PASSED in the orchestrator's `make verify` (1348 passed, exit 0). I did not re-run it. |
| 2 | Every valid link is unchanged: blank still means default, unknown keys ignored, golden requests unchanged, generic over the schema, `test_api.py` pins held or tightened. | VERIFIED | `git diff --exit-code v0.5 -- tests/regression/` exits 0 (run by me). The `test_api.py` diff only adds ten snippets to the pinned-token tuple and removes none (diff `1434a47..HEAD`). The `blank, unknown and accepted tokens` step covers `BLANK_LINK` and `UNKNOWN_KEY_LINK`. `app.js` names no field outside `DIMS`: `refuse()`/`rejected` are keyed generically by the `fields` map. The `readHash`/`gearQuery`/Reset pins are in the passing test_api run. |
| 3 | The decision is logged and the old pin flipped in the same commit: `L44` amends L39, old pin seen red against the fix, new pin seen red with the fix reverted, `web-ui.md` brought true, debt item retired. | VERIFIED | `decision_log.md:2948` holds `## L44`. It states what is refused, blank kept as default, unknown keys ignored, and amends L39 and supersedes L42's byte-identical observation without editing them. The red logs are under `investigation/28-01-red-old-pin.log` and `28-01-red-new-pin.log`, and the L44 "proof" paragraph cites both first-assertion lines. `web-ui.md` lines 34, 54 and 84 cite L44. The debt item is in `docs/tech_debt/resolved/` with `Resolved in: cb93d4e` and the INDEX row moved. The commit message of `cb93d4e` groups fix, pin flip, L44, web-ui and debt retirement. |
| 4 | The `root_fillet` label follows the root, text only, own commit. | VERIFIED | `app.js:30`: `['root_fillet', (d) => (d.root_form_d != null ? 'Hob tip radius used' : 'Root fillet used')]`, keyed on the server's built root, not the form's request. In `calc.py:1292`, `root_form_d` is non-null exactly when `rm.curve` exists. Own commit `61154d1`. Browser step `root_fillet label` covers 26 teeth trochoid (hob), 27 teeth trochoid (falls back to radial) and 23 teeth, and derives the expected label from `/api/info`. Golden diff empty, no `calc.py` value change (the only `calc.py` diff is a docstring, `9092802`). |
| 5 | No review info finding is left `open`: Phases 19, 21-24 dispositioned, the five vacuous-pass findings `fixed`, Phase 18 and Phase 10 triaged as specified, and `grep '\| info \| open \|'` over the Phase 10, 18, 19, 21-24 files prints nothing. | VERIFIED as scoped (see the caveat below) | I ran the grep. Phases 10, 18, 19, 21-24, 25, 26 and 27 print nothing, and every `open:` front-matter count is `0`. Spot checks: 24 CX-05, 23 IN-08, 23 IN-11, 21 IN-03 and 21 IN-04 are all `fixed` with a sha. 18 IN-02 and IN-06 are `skipped` with an "overtaken" reason, 18 IN-07 is `fixed` `9092802`, and 18 IN-03/04/05/08 and 10 IN-01 are `deferred` to the one `nice` item (two separate triggers). 10 IN-02 is `deferred` to a `must` decision item and not fixed, as specified. Of the 20 shas I checked under `git cat-file`, 19 resolve. The exception, `94bccc4` (24 IN-05/IN-06, WR-02), is a Phase 24 branch commit squashed away, and those cells predate Phase 28 (identical at `26ddd74`). It is a pre-existing dangling sha and does not come from this phase's triage. All deferred/idea paths exist. **Caveat: Phase 28's own review leaves IN-01 and IN-02 `open` (see below).** |

**Score:** 5/5 truths verified, 0 present-but-behavior-unverified.

### The contested clause: "every open review info finding of the milestone ... none left open"

- **As the roadmap defines it** (SC5, REQUIREMENTS.md lines 112-120), the scope is Phases 10, 18, 19 and 21-24, and the operational check is the grep over those files. That is met. The scope is also exceeded: 26 and 27 are clean too.
- **As the goal sentence reads literally**, "of the milestone" includes Phase 28. Phase 28's own review (`28-REVIEW.md`, produced after execution) has `IN-01` (`readHash()` double assignment kept for a text pin) and `IN-02` (190-character line in `web-ui.md`). `28-REVIEW-DISPOSITION.md` shows both `open`, along with WR-01/02/03. A literal "none left open at the milestone close" is therefore **not true at HEAD**.
- **My judgement:** this is not a FAILED must-have. The phase's deliverable (the dispositioning work) is done and exact against its stated scope, and a closing phase's own review will always generate new findings after the ledger was written (a regress, not a missed task). It is a **milestone-close gate**: the two `info` rows (and the three warnings) must be dispositioned before the milestone is closed, or the developer must rule that 28's review is out of the clause. That decision is yours, so the report carries it as a human item and the status is `human_needed`, not `passed`.
- Both are cheap. IN-02 is a re-wrap. For IN-01, note that the reviewer's suggested fix ("delete the first assignment") is wrong as worded, because `refuse()` reads the box after the first assignment, so it is the second, identical assignment that is redundant. Whoever fixes it should check that.

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `src/spur/static/app.js` (`rejected`, `refuse`, label) | VERIFIED | Substantive and wired. The 46-line diff matches the plan. |
| `tests/test_browser.py` (4 bad-link steps, `root_fillet label`, form-build step) | VERIFIED | Exercised in the passing browser test. |
| `tests/test_api.py` (ten added pins) | VERIFIED | Additive only. |
| `docs/architecture/decision_log.md` L44 | VERIFIED | Complete (see Truth 3). |
| `docs/architecture/web-ui.md` | VERIFIED | Cites L44 in three places. Its 190-character line is the cosmetic IN-02. |
| Ledger files (9 dispositions plus the debt/idea items) | VERIFIED | See Truth 5. |
| `bench/RESULTS.md` `### Seen red once (Phase 28)` and the bad-link token rows | Present | Cited by L44. Not re-measured by me. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `readHash()` | `gearQuery()` / `update()` via `rejected` | WIRED | Same Map, written in `readHash` and read in both. |
| `gearQuery()` token | `/api/info` 422 | WIRED | `problems()` and `fail()` are unchanged and return before the STL fetch. |
| `DIMS` `root_fillet` row | `derive()` `root_form_d` | WIRED | `calc.py:1292`. |
| each `fixed` cell | a commit | WIRED, one stale sha | See Truth 5 (`94bccc4`, pre-existing). |
| each `deferred` cell | an existing path | WIRED | All paths exist. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Regression fixtures unchanged | `git diff --exit-code v0.5 -- tests/regression/` | exit 0 | PASS |
| No open info row in the roadmap's named files | `grep -rn '\| info \| open \|'` over the 10/18/19/21-27 dispositions | none | PASS |
| Open count of every ledger except 28 | `grep -c '\| open \|'` | 0 everywhere but 28 | PASS |
| Whole gate (orchestrator's run, not mine) | `make verify` | 1348 passed, coverage 97.99%, exit 0 | PASS (cited) |

### Probe Execution

SKIPPED. No probe is declared in the Phase 28 plans.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-bad-link-refused | 28-01 | SATISFIED | Truths 1 and 2 |
| REQ-bad-link-decision-logged | 28-01 | SATISFIED | Truth 3 |
| REQ-root-fillet-label-follows-root | 28-02 | SATISFIED | Truth 4 |
| REQ-info-findings-triaged | 28-01, 28-02, 28-03, 28-04 | SATISFIED for 19 and 21-24, plus 26 and 27 | Truth 5. Phase 28's own review is the milestone-close item. |
| REQ-old-info-findings-triaged | 28-03, 28-04 | SATISFIED | 18 IN-02/06 skipped with reason, IN-07 fixed, the rest in one `nice` item, 10 IN-02 filed as a human decision. |

All five phase requirement IDs appear in the PLAN frontmatter and in REQUIREMENTS.md (lines 94-120, traceability lines 187-191, all marked Complete). No ORPHANED requirements.

### Anti-Patterns Found

None blocking. No `TBD`, `FIXME` or `XXX` introduced in the touched source files (the orchestrator's `make verify` runs the unfinished-work scan and exits 0). The `readHash()` duplicate assignment is the reviewer's IN-01. It is a code-smell kept on purpose for a text pin, and it has a comment.

### Findings from the phase's own review, and whether they affect goal achievement

| ID | Effect on the goal | Class |
|----|--------------------|-------|
| WR-01 (a selector pick that writes a rejected field keeps sending the old token) | I read `write()` (app.js:423) and `plan()`. It never calls `rejected.delete`, so the claim holds. After `#bore_d=abc`, picking "No bore" shows 0 in the box while the request still carries `bore_d=abc`, and the 422 persists. The refusal stays **visible**, so SC1 (which requires only that an edit or Reset clears it) and the "never silently change the part" rule hold, and no part is built. L44 records this as knowingly accepted. It is a real UI inconsistency (box and request disagree) and not a goal failure. | WARNING (human decision: fix or accept) |
| WR-02 (a token the box blanks but the API accepts, such as `face_width=5.`, builds a part under a blank box) | L44 documents it, a step pins it, and it rests on the "server decides" rule (L02). Before the phase the page built the default part under that blank box. The behavior is now more truthful to the link but gives no UI cue. Not a goal failure. | WARNING (human decision) |
| WR-03 (`tip_chamfer_effective` prints `0.0` for an uncut chamfer, against L08) | Pre-existing since Phase 10 and not introduced here. The requirement REQ-old-info-findings-triaged explicitly says to file 10 IN-02 as a decision for the human and not fix it. The phase did that: a `must` item exists, with the measured reproduction in its text. The weakness is the INDEX trigger ("the human's decision"), which no event will fire. The file's own Next step does add "or at the next phase that touches `tip_chamfer` or `derive()`". This does not affect the goal, but a printed value that breaks L08 stays live until the decision is taken. | WARNING (human decision on timing) |

### Human Verification Required

#### 1. Close Phase 28's own review ledger
**Test:** Give `IN-01`, `IN-02`, `WR-01`, `WR-02` and `WR-03` in `28-REVIEW-DISPOSITION.md` a disposition (`fixed` + sha, `deferred` + path, or `skipped` + reason). Then rerun `grep -n '| info | open |'` over every disposition file.
**Expected:** It prints nothing, so the goal clause "none left open, of the milestone" is true literally and not only by the roadmap's phase list.
**Why human:** Whether 28's review counts toward the clause, and whether WR-01/WR-02 are fixed now or accepted, is a scope and risk decision.

#### 2. Take or schedule the `tip_chamfer_effective` decision
**Test:** Decide between a new Lxx with a fix (gate on `tch`, with `make fixture.regen --check`) and keep-with-reason. Or replace the INDEX trigger with a concrete event.
**Expected:** The `must` item no longer waits on an unscheduled decision.
**Why human:** The project rule says a decision of this kind belongs to the human. The phase correctly did not take it.

### Gaps Summary

No goal-blocking gap. The mechanism, the decision log, the label and the ledger closure are in the tree and tested. The two open items are the 28-review dispositions (one clause of the goal sentence, literally read) and the choice between fixing and accepting WR-01/WR-02/WR-03. They are surfaced for a human decision and are not treated as defects of the delivered work.

---

_Verified: 2026-10-21_
_Verifier: Claude (gsd-verifier)_
