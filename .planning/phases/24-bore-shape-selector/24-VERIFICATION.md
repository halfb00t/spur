---
phase: 24-bore-shape-selector
verified: 2026-10-12T17:30:00Z
status: human_needed
score: 6/6 must-haves verified
covered_files:
  - ".planning/phases/24-bore-shape-selector/24-01-PLAN.md"
  - ".planning/phases/24-bore-shape-selector/24-01-SUMMARY.md"
  - ".planning/phases/24-bore-shape-selector/24-02-PLAN.md"
  - ".planning/phases/24-bore-shape-selector/24-02-SUMMARY.md"
  - ".planning/phases/24-bore-shape-selector/24-03-PLAN.md"
  - ".planning/phases/24-bore-shape-selector/24-03-SUMMARY.md"
  - ".planning/phases/24-bore-shape-selector/24-04-PLAN.md"
  - ".planning/phases/24-bore-shape-selector/24-04-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "src/spur/params.py"
  - "src/spur/static/app.js"
  - "src/spur/static/style.css"
  - "tests/browser_session.py"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_selector.py"
covered_digest: "v3:sha256:37d4fb6c771039de585802e02eb989176db7b456f64be68f328f31cb16ccd875"
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
coincidental_reliance_items: []
human_verification:
  - test: "On Firefox (any platform) or Chrome on Windows or Linux, focus the Bore shape select with the keyboard (Tab) and press ArrowDown once from the default D-flat, then ArrowDown again."
    expected: "Focus stays on the select so the second ArrowDown reaches No bore, or at minimum the next arrow key does not spin the Hex bore A/F number box and no request for a 0.05 mm hex bore is sent."
    why_human: "Code review WR-01 confirms on the wiring that the select listens on input only and pend() calls input.focus() in the same handler, so on engines where an arrow key commits the next option and fires input, the first step to a pending option moves focus to bore_hex. It did not reproduce with real arrow keys in headless Chrome on macOS (arrow keys open the popup there), and the browser test drives the select with select_option, which fires input once and never presses a key. No engine that exhibits the behavior is available in this environment."
  - test: "Read the pick() and pend() handlers in src/spur/static/app.js and confirm that no await, timer or callback sits between the plan loop and the writes."
    expected: "Both run as one synchronous input-event handler; the only deferred work is the form listener's scheduleUpdate() debounce, and update()'s seq counter drops answers to older queries."
    why_human: "The 24-01 truth 'Probe (write, concurrency)' is tagged verification: backstop (non-inferable). No test exercises interleaving, so the truth cannot be marked verified on presence and wiring alone. The code reads as synchronous, with no await between lines 290 and 415, and update() carries seq at lines 239 to 277, so I expect it to hold. It stays a human confirmation by the rules for backstop truths."
---

# Phase 24: Bore Shape Selector Verification Report

**Phase Goal:** A user picks a bore shape instead of inferring it from a warning. The select's options come from the schema, its state is derived from the flat fields on load, and it writes only the flat fields. The API, the CLI and the URL contract are unchanged (L05).
**Verified:** 2026-10-12T17:30:00Z
**Status:** human_needed
**Re-verification:** No, initial verification

## Goal Achievement

Verdict in one paragraph: the goal is achieved in the codebase for every path I could exercise. The model carries the selector, the page renders it from the schema with no bore field name in generic code, loading never writes (the 44 golden request sets and `pre_v0_2.json` have an empty diff against the phase base), and every pick from every state is proven both in Python (`tests/test_selector.py`) and in a real browser. The status is `human_needed` rather than `passed` for two reasons: one confirmed-on-wiring keyboard defect that I could not exercise on an affected engine (code review WR-01), and one backstop-tagged truth that no test can prove. Neither is a failed truth.

### Roadmap Success Criteria

| # | Success Criterion | Status | Evidence |
|---|-------------------|--------|----------|
| 1 | The selector is schema-carried; `app.js` renders it with no bore field name; the field-name pin and DIMS-key pin hold with an empty diff | VERIFIED | `GearParams.model_json_schema()` keys are exactly `description, properties, selectors, title, type`; `selectors` holds one entry `Bore shape` / group `Bore` with the four options Round, D-flat, Hex, No bore in the `when()` vocabulary (`src/spur/params.py:57-71`, `model_config` at line 87). `grep bore_ src/spur/static/app.js` finds only the pre-existing derived-value rows (`bore_effective`, `keyway_*`), none in the selector code (lines 292-413), which reads `schema.selectors ?? []` and uses `holds()`. `GearParams` still has 31 fields. `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q"` ran 62 passed on this tree, including the pins and the added `selectors` assertions (in `/api/schema`, not in `/openapi.json`). |
| 2 | Loading never writes; a change writes only the minimum switch-off fields as `"0"`, restores typed values, adds no `fields` entry; no non-`GearParams` key in any `/api/*` request or the hash | VERIFIED | `deriveSelectors()` assigns only `selectedIndex` and reason text, never a field value (`app.js:331-346`). `pick()` plans before it writes, writes `String(value)` for `eq` fields and a stashed string for `gt` fields, and goes pending otherwise (`app.js:371-389`). The select has no `name` and `fields.set(` still occurs once (pin in `tests/test_api.py`). `git diff --exit-code 07cba05..HEAD -- tests/regression/` is clean. `tests/test_browser.py` passed in my run (`2 passed in 20.59s`); its recorder is attached to every page and asserts no foreign key after each step (24-03). |
| 3 | Each selector state round-trips through `derive()`; `pre_v0_2.json` is clean; the idea is retired in the closing commit | VERIFIED | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"` ran 16 passed. The idea file is in `docs/ideas/retired/` with `Status: retired` and `Retired in:` naming the `3a8028b` subject. The hex-warning debt row reads `trigger fired: the selector shipped in 470b78a; fix as a /gsd-quick before Phase 25's reading`. `## L42` exists in `docs/architecture/decision_log.md:2682`. `bench/RESULTS.md` holds `## Bore-shape selector (Phase 24)` and `### Seen red once (Phase 24)` (14 table rows). |

### Observable Truths (merged from the PLAN must-haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 24-01: `/api/schema` carries `selectors`; `GearParams` unchanged; `/openapi.json` has no `selectors` | VERIFIED | Schema printed above; 31 fields; `test_openapi_documents_the_typed_contracts` passes in the `test_api.py` run. |
| 2 | 24-01: a fresh load of a state link shows the right option, writes nothing, sends the link's query; derive is called at exactly three sites | VERIFIED | `deriveSelectors();` follows `applyRelations();` in `readHash()`, in the form `input` listener and in `#reset` (diff read; pinned by `test_api.py`). Browser test passed (`bore shape` and `golden sweep` steps). Deliberate removal of the `readHash()` and `#reset` calls was seen red (24-03 logs `24-03-readhash-red.log`, `24-03-reset-red.log`). |
| 3 | 24-01: Round writes `bore_flat=0`; D-flat restores the exact stashed string; Hex from default is pending with focus and a reason row; Reset clears the stash | VERIFIED | `pick()`/`pend()` code read; `bore shape` browser step passed; seen-red rows in `bench/RESULTS.md` for `stopPropagation()` removal and the stash-restore break, each with a kept log. |
| 4 | 24-01: schema edge cases (twin selector, unknown op, negative value) load blank without skipping `update()` | VERIFIED | `try`/`catch` per selector in `deriveSelectors()`; `unknown relation op` step passed; catch and first-match breaks seen red (`24-01-catch-red.log`, `24-01-twin-red.log`). |
| 5 | 24-02: walk, grid, round trip and stash round trip hold; doctored schemas go red; three wrong options on the real `params.py` went red and were restored | VERIFIED | 16 passed in `tests/test_selector.py`; red logs `24-02-wrong-field-red.log`, `24-02-wrong-op-red.log`, `24-02-overlap-red.log` kept; `git diff --exit-code 470b78a..HEAD -- src/spur/params.py` is empty in this tree (params.py unchanged since 24-01). |
| 6 | 24-03 and 24-04: sweep reads the select for the 44 links; recorder on every page; every pick from every state; priced readings kept; `make verify` green | VERIFIED | Browser test passed; `investigation/24-04-verify.log` ends `1311 passed in 288.08s (0:04:48)` then `make verify exit 0`; three reading and three slice logs exist and each reading log contains the `step bore shape` line the table cites. 24-04's commit `c0675b9` touches only `bench/RESULTS.md` and the kept logs, so no wait or timeout moved. |
| 7 | 24-01 backstop truth: a pick plans and writes inside one synchronous handler, so nothing interleaves | UNCERTAIN (insufficient_spec) | The code is synchronous (no `await` in `app.js` lines 290-415) and `update()` guards stale answers with `seq` and `AbortController`. No test exercises interleaving, and the truth is tagged `verification: backstop`, so presence is not accepted as proof. Routed to human item 2 below. |

**Score:** 6/6 roadmap and plan truths verified with test evidence; 1 backstop truth routed to a human (not counted as failed).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `_option()`, `_BORE_SHAPE`, `json_schema_extra={"selectors": [_BORE_SHAPE]}` | VERIFIED | Present, substantive, emitted through `/api/schema`. |
| `src/spur/static/app.js` | `buildSelectors()`, `deriveSelectors()`, `pick()`, `pend()`, stash, three derive call sites | VERIFIED | Present and wired (`buildSelectors(schema.selectors ?? [], groups)` at the end of `buildForm()`). |
| `src/spur/static/style.css` | `label.selector` grid sharing and `.selector.pending` | VERIFIED | Diff read. |
| `tests/test_selector.py` | walk, grid, round trip, meta-red tests | VERIFIED | 588 lines, 16 passed. |
| `tests/browser_session.py`, `tests/test_browser.py` | selector helpers, `bore shape` step, recorder, every pick | VERIFIED | Browser test passes. |
| `tests/test_api.py` | tightened pins under L42 | VERIFIED | 62 passed. |
| `docs/architecture/decision_log.md` | `## L42` | VERIFIED | Line 2682. |
| `docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md` | retired idea with outcome | VERIFIED | `Status: retired`. |
| `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` | restated trigger | VERIFIED | INDEX row carries the restated trigger. |
| `bench/RESULTS.md` and `investigation/*.log` | priced section and seen-red table | VERIFIED | Section and table present; logs on disk. |

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `GearParams.model_config` | `GET /api/schema` | `json_schema_extra` top-level key | WIRED (printed from `model_json_schema()`) |
| `buildForm()` | `buildSelectors()` | `schema.selectors ?? []` | WIRED |
| `readHash()`, `input` listener, `#reset` | `deriveSelectors()` | call after `applyRelations()` | WIRED (three sites) |
| `deriveSelectors()`, `pick()` | `holds()`, `need()` | one evaluator for relations and selectors | WIRED |
| `tests/test_selector.py` | `tests/test_relations.py` evaluator | `from test_relations import` | WIRED (module passes) |
| `sweep()` / `record_api()` | `golden sweep` / every `new_page()` | recorder and shown-option comparison | WIRED (browser test passes) |

### Data-Flow Trace (Level 4)

| Artifact | Data | Source | Real data | Status |
|----------|------|--------|-----------|--------|
| Bore shape select options | option labels | `/api/schema` `selectors`, from the model | Yes | FLOWING |
| Bore shape select state | `selectedIndex` | `holds()` over live field values | Yes | FLOWING |

### Behavioral Spot-Checks and Probes

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Model-side proof | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"` | 16 passed in 0.07s | PASS |
| API pins and schema | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q"` | 62 passed in 15.43s | PASS |
| Browser proof (all steps) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | 2 passed in 20.59s | PASS |
| Golden pins untouched | `git diff --exit-code 07cba05..HEAD -- tests/regression/` | exit 0 | PASS |
| Full gate | read `investigation/24-04-verify.log`, and the orchestrator's `make test` on `fdfe929` | `1311 passed`, `make verify exit 0`, coverage 97.99 % | PASS (not re-run by me) |

No probe scripts (`probe-*.sh`) are declared by this phase.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-selector-schema-carried | 24-01, 24-02 | Options live on the model in L41's vocabulary; `app.js` renders from schema with no bore field name | SATISFIED | Truths 1 and SC1 above |
| REQ-selector-derives-and-writes-through | 24-01, 24-03, 24-04 | State derived on load without writing; a change writes the minimum as `"0"`, stashes and restores, adds no `fields` entry; no foreign key in any request or the hash | SATISFIED for the mouse and programmatic path; keyboard-driven picks carry the WR-01 warning below | Truths 2, 3, 6 and SC2 |
| REQ-selector-round-trips-per-state | 24-02, 24-03 | Model-driven round trip per state proves the composed document identical; the 44 golden sets unchanged | SATISFIED | Truth 5 and SC3 |

All three IDs appear in the PLAN frontmatter and in `.planning/REQUIREMENTS.md` (lines 138-153, marked complete; traceability rows 258-260). No orphaned requirement maps to Phase 24 without a plan claiming it.

### Prohibitions (ADR-550 D3)

| Prohibition | Tier | Result |
|-------------|------|--------|
| No `GearParams` field added or default moved (L05) | test | Enforced: 31 fields, golden and `pre_v0_2.json` diff empty |
| No bore field name, option table or second grammar in `app.js` | test | Enforced by the field-name pin and `holds()` reuse; grep clean |
| Write only the chosen option's own false conditions, never an invented value | test | Enforced by `pick()` code, the `fields.set(` count pin and the round trip in `test_selector.py` |
| Never write while deriving | test | Enforced by the `bore shape` and `golden sweep` steps and the red-seen derive-call removals |
| No foreign key in any `/api/*` request or the hash | test | Enforced by the recorder with `no_foreign_key` after every step |
| `golden_requests.json` and `pre_v0_2.json` not edited to absorb a change | test | Verified: empty diff over the whole phase |
| No unmeasured reading recorded; no wait, timeout or bar moved toward a pass (24-04) | test and judgment | Reading logs exist for every table; `c0675b9` touches only `bench/RESULTS.md` and logs. My judgment verdict is non-authoritative: no violation found. |

No prohibition is flagged unverified.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | `TBD`, `FIXME`, `XXX`, `TODO` greps over `params.py`, `app.js` and `tests/test_selector.py` returned nothing | - | - |
| `src/spur/static/app.js` | 329, 411 | Select listens on `input` only; `pend()` calls `input.focus()` in the same handler | WARNING | Keyboard operability, see below (code review WR-01) |
| `src/spur/static/app.js` | 292-300, 382 | Stash is not cleared when the user edits the same field by hand (IN-01) | Info | Can restore an older or page-default value; accepted knowingly for the hash case by D-19, so a documentation or one-line hardening item |
| `src/spur/static/app.js` | 313, 558-562 | A selector naming a missing group fails with a "schema fetch" message and a half-built form (IN-02) | Info | Cannot occur with the shipped model; `test_selector.py` walks the group |
| `tests/test_api.py` | 142 | `"selectors" not in /openapi.json` is a substring test (IN-03) | Info | Can fail on unrelated prose; not a defect today |
| `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` | - | Hex warning names snake_case fields and default values (IN-04) | Info | Already filed, trigger fired, fix scheduled before Phase 25 |

### How I weighed WR-01

The goal says "a user picks a bore shape". The mouse and `select_option` path is fully proven. The keyboard path is the open question.

- The mechanism is real in the code: `select.addEventListener('input', ...)` (line 329) and `input.focus()` in `pend()` (line 411). On engines where an arrow key on a closed select commits the next option and fires `input` (Firefox everywhere, Chrome on Windows and Linux), the first step from the default D-flat to Hex is always pending, because a Hex pick from a part that never had a hex bore needs a typed number. Focus then jumps to `bore_hex`, and a second arrow key spins that number box. The reviewer reproduced this by dispatching one `input` event after setting `selectedIndex`, and it was not reproduced with real key presses.
- It does not break the writes-only-flat-fields contract. The selector itself writes nothing in that path. The unwanted value comes from the user's own key press landing on a number input. It does not make a number the tool invented, so it does not fail `REQ-selector-derives-and-writes-through`, whose text is about the select's writes and about load never writing.
- It does weaken "a user picks a bore shape" for keyboard-only users on the affected engines: they cannot walk the select past Hex. That is an accessibility defect against a feature whose goal is a usable picker, but it is not in any roadmap success criterion, and I cannot show it on a real engine here.
- So I classify it as a WARNING with a human check, not a BLOCKER and not a pass. I did not inflate it into a failed truth, and I did not drop it. `24-REVIEW-DISPOSITION.md` still lists WR-01 as `open`; a fix or an explicit deferral should be recorded before the milestone closes.

### Human Verification Required

#### 1. Keyboard walk of the Bore shape select

**Test:** On Firefox (any platform) or Chrome on Windows or Linux, Tab to the Bore shape select and press ArrowDown once from the default D-flat, then ArrowDown again.
**Expected:** Focus stays on the select so the second press reaches No bore, or at minimum the next arrow key does not spin the Hex bore A/F box and no 0.05 mm hex bore request is sent.
**Why human:** WR-01 is confirmed on the wiring but not on real key presses; no affected engine runs here, and the browser test uses `select_option`.

#### 2. Synchronous pick (backstop truth)

**Test:** Read `pick()` and `pend()` in `src/spur/static/app.js` and confirm nothing asynchronous sits between the plan and the writes.
**Expected:** One synchronous input-event handler; only the form listener's debounce defers, and `update()`'s `seq` counter drops stale answers.
**Why human:** The truth is tagged `verification: backstop`, so presence and wiring cannot verify it; I found no `await` between lines 290 and 415 and expect it to hold.

### Gaps Summary

No gaps. Every roadmap success criterion and every testable plan truth is verified against the code and against tests I ran myself. The two human items are a keyboard-engine check for WR-01 and a read-through of a backstop-tagged truth. The four info findings and the filed hex-warning debt are advisory and do not block the phase.

---

_Verified: 2026-10-12T17:30:00Z_
_Verifier: Claude (gsd-verifier)_
