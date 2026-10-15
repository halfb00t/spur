---
phase: 24-bore-shape-selector
reviewer: codex
model: gpt-6.1-sol
reasoning_effort: xhigh
subject: PR #36 diff outside .planning/ (16 files) at 8dcc073, repo tree read-only
procedure: docs/HOW_TO_DEVELOP.md section 7
date: 2026-10-13
tokens_used: 162943
verdict: REVISE
---

# Cross-CLI review of PR #36 by Codex

The second CLI reviewed the pull request diff and the checked-out tree, read-only, with the prompt kept at the end of this file. Its last message follows verbatim.

## Findings

src/spur/static/app.js:347: WARNING: Pending choices are discarded before completion. Load `#bore_d=0`, pick Round, then type `9` in the focused Bore Ø field: the select becomes D-flat because `bore_flat` remains `8`, contradicting D-09. Retain the pending choice and retry its writes when the required value is supplied; test this sequence.
src/spur/static/app.js:411: WARNING: WR-01 follows from [Blink](https://raw.githubusercontent.com/chromium/chromium/main/third_party/blink/renderer/core/html/forms/select_type.cc) and [Gecko](https://raw.githubusercontent.com/mozilla/gecko-dev/master/layout/forms/HTMLSelectEventListener.cpp) handlers on Windows/Linux: ArrowDown from D-flat selects Hex and transfers focus to `bore_hex`; the next arrow edits that number instead of reaching No bore. Keep focus on the select and describe the pending need there; add real-key coverage. Switching to `change` alone fails because both events fire per arrow.
src/spur/static/app.js:311: WARNING: Missing `options`, a null selector, or an unknown group throws during construction. Startup then returns before loading the hash or calling `update()`, leaving numeric fields blank. Isolate malformed selectors, report their errors, and continue initializing the form; add construction-failure coverage.
Verdict: REVISE

## Re-review of the fix commit faed50a

Claude Code fixed findings 1 and 2 in `faed50a` (`fix(24): a pending bore-shape pick completes when its number is typed and never moves the focus`). Codex reviewed that commit's diff and the fixed tree, read-only, with the second prompt kept below. Its last message follows verbatim.

### Findings

src/spur/static/app.js:474: WARNING: With two bore selectors, load `#bore_d=0`, pick Round in the first, then Hex in the second: the first loses `.pending` but still displays Round and leaves its reason text, although the fields imply No bore. The second pending pick suppresses the cleanup derive. Restore canceled rows and rederive canceled selectors on this path; add two-selector coverage.
Verdict: REVISE

The one finding is recorded as CX-04 in `24-REVIEW-DISPOSITION.md` and fixed in the commit that carries this section: `completePending()` now puts the first selector's row back and re-derives it when another selector's pick ends its pending pick, and the browser step `twin selectors` proves it on a schema served with its selector list doubled.

## Review of the fix commit 9da4851

Claude Code fixed CX-04 in `9da4851`. Codex reviewed that commit's diff and the fixed tree, read-only. Its last message follows verbatim.

### Findings

tests/test_browser.py:1611: INFO: The request-count assertion can pass before a queued 350 ms debounce fires; closing the page then hides the request. Settle the initial load and observe beyond the debounce before asserting zero requests.
Verdict: APPROVE

The one finding is recorded as CX-05 (info, open) in `24-REVIEW-DISPOSITION.md`.

## Review of the fix commit 94bccc4

Claude Code fixed the second internal review's WR-02 (an emptied box completed a pending pick with the field's default) in `94bccc4`. Codex reviewed that commit's diff and the fixed tree, read-only. Its last message follows verbatim.

### Findings

Verdict: APPROVE

No finding. Every Codex finding on this pull request is now closed or recorded: CX-01, CX-02 and CX-04 fixed, CX-03 and CX-05 open as info in `24-REVIEW-DISPOSITION.md`.

## Prompt (first review)

You are the second CLI in this repository's cross-CLI review (docs/HOW_TO_DEVELOP.md section 7): Claude Code wrote pull request #36 ("Phase 24: Bore-Shape Selector", branch gsd/phase-24-bore-shape-selector against main); you review it. Read AGENTS.md first. Its two standing rules (a printed number is a number someone will cut metal to, L08; a parameter the user did not set must never silently change the part, L05) and docs/CODING_VALUES.md are the standard.

The diff to review is in <scratchpad>/pr-36.diff: the PR's changes outside .planning/, 16 files. The checked-out tree at /Users/halfb00t/git/halfb00t/spur is the PR head; read any file you need for grounding, in particular src/spur/params.py, src/spur/static/app.js, tests/test_selector.py, tests/test_browser.py, tests/browser_session.py, tests/test_api.py and the L42 entry in docs/architecture/decision_log.md.

What to check, in order of weight:
1. Correctness of the selector contract: the four options (Round, D-flat, Hex, No bore) hold exactly one each on every non-negative triple of bore_d, bore_flat and bore_hex; a pick writes only the string "0" to unmet eq fields and restores stashed gt strings; nothing is written on load; no key GearParams lacks reaches any request or the hash; the keyway is left to the server's 422. Find a concrete input or event sequence that breaks any of these.
2. The known open warning WR-01: the select listens on the input event only and pend() calls input.focus() in the same handler, so an engine that commits an option and fires input on each arrow key may move focus off the select in the middle of a keyboard walk. Say whether the wiring has that defect, on which engines, and the smallest fix, or say that it is not a defect and why.
3. Regressions to existing behaviour: the pins in tests/test_api.py are tightened, the relations section of app.js is claimed byte-identical, gearQuery() unchanged, both regression fixtures unchanged. Name anything the diff changes that the tests do not pin.
4. Test quality: does each new test prove behaviour rather than implementation; is anything over-mocked; is any deliberate break in the "seen red" evidence not actually red.
5. Docs and comments: a comment must say why, with the measurement or constraint that forced the choice; the L42 claims must match the code; README.md and docs/architecture/web-ui.md must match the shipped behaviour.
6. Robustness of the schema-driven JS: a malformed selectors entry from /api/schema must not break the form or skip update().

Rules for your output: no praise and no summary of what the PR does. One finding per line in the form `path:line: SEVERITY: problem. Fix.` with SEVERITY one of CRITICAL (a wrong number, a silent part change, data loss), WARNING (a correctness or maintainability defect) or INFO (minor). Cite the file and line of the checked-out tree, not the diff hunk. End with one line `Verdict: APPROVE` or `Verdict: REVISE`; REVISE only when at least one CRITICAL or WARNING finding is real and reproducible from the cited lines. Do not modify any file.

## Prompt (re-review)

You are the second CLI in this repository's cross-CLI review (docs/HOW_TO_DEVELOP.md section 7). You reviewed pull request #36 ("Phase 24: Bore-Shape Selector") earlier today and returned three findings; your last message is kept at .planning/phases/24-bore-shape-selector/24-CROSS-REVIEW.md in the checked-out tree. Claude Code then wrote one fix commit, faed50a, for your findings 1 and 2 (finding 3 was recorded as INFO and left as is). Review that fix.

The diff of the fix is in <scratchpad>/fix-faed50a.diff (src/spur/static/app.js, tests/test_browser.py, tests/browser_session.py, docs/architecture/web-ui.md and the dated amendment at the end of L42 in docs/architecture/decision_log.md). The checked-out tree at /Users/halfb00t/git/halfb00t/spur is the fixed head; read any file you need. AGENTS.md and docs/CODING_VALUES.md are the standard.

What to check:
1. Does the fix close your finding 1? A pending pick now stays until the number it asked for is typed, when completePending() (a capture-phase input listener on the form) re-runs plan() and writes what the pick held back; any other field typed, another pick, Reset or a hash navigation ends it. Look for a sequence that still loses the pick or writes a field the user did not ask to change: the keep flag consumed by deriveSelectors(), the was record restored by endPending(), two selectors, a pending pick followed by a hash navigation, Reset, a negative typed into the asked field, typing the asked field to a value that clears the threshold while another condition's stash is stale.
2. Does the fix close your finding 2? pend() no longer calls focus(); the field's reason row describes the field and the select. Is anything lost for keyboard or screen-reader users that the previous behaviour gave.
3. Regressions: the pins in tests/test_api.py still hold (exactly one value write in the selectors section, the three call sites, the fourteen tokens); gearQuery(), the relations section and the regression fixtures untouched; one debounced request per pick and per completion.
4. Test quality of the new browser coverage (_complete_pending, the chained case from a link with every gt field at its threshold, the abandon case, the focus assertion): does each prove behaviour, is any expectation a tautology, is the keyboard walk itself still unproved and said so.
5. Comments and the L42 amendment: each says why with the constraint or measurement; the amendment's claims match the code.

Rules for your output: no praise and no summary of what the fix does. One finding per line in the form `path:line: SEVERITY: problem. Fix.` with SEVERITY one of CRITICAL, WARNING or INFO, citing the checked-out tree's file and line. End with one line `Verdict: APPROVE` or `Verdict: REVISE`; REVISE only when at least one CRITICAL or WARNING finding is real and reproducible from the cited lines. Do not modify any file.

## Prompt (review of 9da4851)

You are the second CLI in this repository's cross-CLI review (docs/HOW_TO_DEVELOP.md section 7). Earlier today you reviewed pull request #36 ("Phase 24: Bore-Shape Selector") and then its fix commit faed50a, where you returned one finding: with two selectors, a pending pick in the second ended the first's pending pick without restoring its row or re-deriving it. Claude Code wrote one more commit, 9da4851, for that finding. Review that commit only.

The diff is in <scratchpad>/fix-9da4851.diff (src/spur/static/app.js and tests/test_browser.py). The checked-out tree at /Users/halfb00t/git/halfb00t/spur is the fixed head; read any file you need. AGENTS.md and docs/CODING_VALUES.md are the standard.

What to check:
1. Does completePending() now put the ended pick's row back and re-derive that selector on a pick in another selector, for both a pending and a writing pick in the other selector, and for a field typed while two selectors are pending? Is deriveSelector() equivalent to the loop body it replaced?
2. Does the new browser step "twin selectors" prove the behaviour rather than restate it: the schema served with its selector list doubled, the pair of labels chosen from the schema, the first select back on the fields' option with its row restored, the second pending, no field written, no request sent. Name any expectation that is a tautology.
3. Any regression to the pins in tests/test_api.py (exactly one value write in the selectors section, the tokens) or to the single-selector behaviour you reviewed before.

Rules for your output: no praise and no summary of what the commit does. One finding per line in the form `path:line: SEVERITY: problem. Fix.` with SEVERITY one of CRITICAL, WARNING or INFO, citing the checked-out tree's file and line. End with one line `Verdict: APPROVE` or `Verdict: REVISE`; REVISE only when at least one CRITICAL or WARNING finding is real and reproducible from the cited lines. Do not modify any file.

## Prompt (review of 94bccc4)

You are the second CLI in this repository's cross-CLI review (docs/HOW_TO_DEVELOP.md section 7). You reviewed pull request #36 ("Phase 24: Bore-Shape Selector") and its fix commits faed50a and 9da4851 earlier today. A second internal code review then found WR-02: completePending() re-planned a pending pick through holds(), whose effective() reads an empty box as the field's default, so a Backspace or a leading "." in the asked field (bore_d, default 9) completed a pending Round or D-flat pick, wrote bore_flat=0 and sent a 9 mm bore nobody typed. Claude Code wrote one commit, 94bccc4, for it. Review that commit only.

The diff is in <scratchpad>/fix-94bccc4.diff (src/spur/static/app.js, tests/test_browser.py, docs/architecture/decision_log.md). The checked-out tree at /Users/halfb00t/git/halfb00t/spur is the fixed head; read any file you need. AGENTS.md and docs/CODING_VALUES.md are the standard.

What to check:
1. Is an empty box the only unreadable state a type=number input reports as '' (a leading "-", ".", "e"), and does the fix hold for all of them? Is there any other path by which a pending pick completes on a value the user did not type (effective() elsewhere, a hash navigation, Reset)?
2. The test: the every-state loop empties the asked field first only where the field's schema default clears the threshold (_default_clears), then asserts the pick stays pending with its note and only that field moved. Is the selection rule right, and does the assertion prove the fix rather than restate it?
3. Any regression to the pins in tests/test_api.py (exactly one value write in the selectors section; the tokens) or to the single- and twin-selector behaviour you reviewed before.

Rules for your output: no praise and no summary of what the commit does. One finding per line in the form `path:line: SEVERITY: problem. Fix.` with SEVERITY one of CRITICAL, WARNING or INFO, citing the checked-out tree's file and line. End with one line `Verdict: APPROVE` or `Verdict: REVISE`; REVISE only when at least one CRITICAL or WARNING finding is real and reproducible from the cited lines. Do not modify any file.
