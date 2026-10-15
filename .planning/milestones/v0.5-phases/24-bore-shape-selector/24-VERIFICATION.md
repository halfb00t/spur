---
phase: 24-bore-shape-selector
verified: 2026-10-13T05:10:00Z
status: passed
score: 8/8 must-haves verified
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
  - "docs/architecture/web-ui.md"
  - "src/spur/params.py"
  - "src/spur/static/app.js"
  - "src/spur/static/style.css"
  - "tests/browser_session.py"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_selector.py"
covered_digest: "v3:sha256:c619952075a1980d8cb342cc0b62758b5f2294691bfe4598be30a0167718af81"
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
coincidental_reliance_items: []
re_verification:
  previous_status: passed
  previous_score: 6/6
  gaps_closed: []
  gaps_remaining: []
  regressions: []
advisory:
  - finding: "The seen-red table in bench/RESULTS.md (Phase 24) covers the four 24-0x plans only; the reds for the three post-ship fixes (faed50a, 9da4851, 94bccc4) are not tabulated there"
    category: other
    reason: "I re-ran two of the breaks myself (below) and both went red, so the tests prove the fixes; the table is a record gap, not a proof gap. A line in the disposition or RESULTS.md would close it."
    evidence_status: "none provided (record only)"
---

# Phase 24: Bore Shape Selector Verification Report

**Phase Goal:** A user picks a bore shape instead of inferring it from a warning. The select's options come from the schema, its state is derived from the flat fields on load, and it writes only the flat fields. The API, the CLI and the URL contract are unchanged (L05).
**Verified:** 2026-10-13T05:10:00Z
**Status:** passed
**Re-verification:** Yes, regenerated whole against the tree at `fd4604c` (#4682). The prior report went stale because `faed50a`, `9da4851` and `94bccc4` changed `app.js`, `tests/test_browser.py`, `tests/browser_session.py`, `decision_log.md` and `web-ui.md` after it was written.

## Goal Achievement

Verdict: the goal is achieved in the current tree. The model carries the selector, the page renders it from the schema with no bore field name in generic code, loading never writes, a pick writes only flat fields, and the golden request sets and `pre_v0_2.json` have an empty diff. The three post-ship commits changed one thing on purpose: a pending pick now stays until the number it asked for is typed and then writes what it held back, and it never moves the focus. I read that code, ran the tests, and broke it two ways to see the tests go red. I did not take the SUMMARY or the review dispositions as evidence.

### Roadmap Success Criteria

| # | Success Criterion | Status | Evidence |
|---|-------------------|--------|----------|
| 1 | The selector is schema-carried; `app.js` renders it with no bore field name; the field-name pin and DIMS-key pin hold | VERIFIED | `GearParams.model_json_schema()` keys are `['description','properties','selectors','title','type']`; 31 fields; one selector with options `['Round','D-flat','Hex','No bore']`. `sed -n 292,491p src/spur/static/app.js \| grep bore_` returns nothing; `buildSelectors()` takes `schema.selectors` and `holds()`. `tests/test_api.py`: 62 passed (run by me). |
| 2 | Loading never writes; a change writes only the minimum switch-off fields as `"0"`, restores typed values, adds no `fields` entry; no non-`GearParams` key in any `/api/*` request or the hash | VERIFIED | `deriveSelector()` assigns `selectedIndex` and reason text only. `plan()` returns writes as strings (`String(value)` for `eq`, the stashed string for `gt`), `write()` holds the section's one `input.value =` statement. `grep -n "fields.set(" app.js` finds only line 99 (`buildForm`). The select has no `name`. `git diff --quiet 07cba05..HEAD -- tests/regression/` exits 0. `tests/test_browser.py`: 2 passed (run by me); its recorder asserts no foreign key after each step. |
| 3 | Each selector state round-trips through `derive()`; `pre_v0_2.json` is clean; the idea is retired in the closing commit | VERIFIED | `tests/test_selector.py`: 16 passed (run by me). `git diff --quiet 470b78a..HEAD -- src/spur/params.py` exits 0 (the model is as 24-01 left it). The retired idea, the restated debt trigger, `## L42` and the priced section were verified in the first report and none of those files has changed since (`git diff --stat 1634195..HEAD` touches only `decision_log.md` (the L42 amendment), `web-ui.md`, `app.js`, `tests/browser_session.py`, `tests/test_browser.py`). |

### Observable Truths (roadmap contract merged with the PLAN must-haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 24-01: `/api/schema` carries `selectors`; `GearParams` unchanged; `/openapi.json` has none | VERIFIED | Schema printed above; 31 fields; `test_openapi_documents_the_typed_contracts` is in the 62 passed. |
| 2 | 24-01: a fresh load of a state link shows the right option, writes nothing, sends the link's query; `applyRelations()` and `deriveSelectors()` have exactly three call sites | VERIFIED | `app.js:109-110` (`readHash`), `:608` (form `input` listener), `:619-620` (`#reset`). The `bore shape` and `golden sweep` browser steps pass. The `readHash()` and `#reset` removals were seen red in 24-03 (`24-03-readhash-red.log`, `24-03-reset-red.log`). |
| 3 | 24-01: Round writes `bore_flat=0`; D-flat restores the exact stashed string; Hex from a part with no hex bore is pending with a reason row; Reset clears the stash. The plan text adds "with focus"; that clause is superseded (see the note below) | VERIFIED | `pick()`, `plan()`, `write()`, `pend()` read in full (`app.js:382-435`). The `bore shape` step drives all sixteen picks and passes. The stash-restore break was seen red in 24-01 (`24-01-restore-red.log`). |
| 4 | 24-01: schema edge cases (twin selector, unknown op, negative value) load blank without skipping `update()` | VERIFIED | `try`/`catch` per selector in `deriveSelector()` (`app.js:362-372`); `first match wins` is `i === hits.lastIndexOf(true) ? i : -1`. `unknown relation op` step passes; catch and first-match breaks seen red in 24-01. |
| 5 | 24-02: walk, grid, round trip and stash round trip hold; doctored schemas go red | VERIFIED | 16 passed; three real-`params.py` breaks seen red in 24-02 (logs on disk). |
| 6 | 24-03, 24-04: the sweep reads the select for the 44 links; recorder on every page; every pick from every state; priced readings kept; gate green | VERIFIED | Browser test passes. `make verify` on the current tree (run by me): `1311 passed in 245.48s`, coverage 97.82 % against the 96.0 % bar, exit 0. |
| 7 | Post-ship (L42 amendment, CX-01, CX-02, CX-04, WR-02): a pending pick stays until the number it asked for is typed and then writes what it held back; the focus never leaves the select; another selector's pick, another field, Reset or a hash navigation ends it and puts the row and the select back on the fields' state; an emptied box is not a typed number | VERIFIED | Code: `completePending()` (`app.js:476-491`) runs `plan()` again on the asked field, writes through the one `write()`, keeps the pick with `keep: true` when another number is missing, treats `input.value === ''` as not typed, and for any other target calls `endPending(s, true)` then `deriveSelector(s)`. `pend()` contains no `focus()` call (the only `focus()` in the section is in a comment). Tests: `_complete_pending` (chained case, `empty_first`), the abandon case, the `SELECT_FOCUSED` assertion after every pending pick, and the `twin selectors` step all pass. See the mutation checks below. |
| 8 | 24-01 backstop truth: a pick plans and writes inside one synchronous handler, so nothing interleaves | VERIFIED (human evidence) | `pick()`, `pend()` and `completePending()` contain no `await`, timer or callback, and `update()` guards stale answers with `seq` and `AbortController` (`app.js:239-284`). `24-UAT.md` item 2 is `pass`, recorded by the human. The code that item covers is unchanged in shape: `pick()`/`pend()` remain synchronous handlers and `completePending()` is a synchronous capture-phase listener. |

**Score:** 8/8 truths verified (rows 1 to 7 are the first report's six plus the post-ship amendment; row 8 is the backstop truth carried by the UAT). No truth is behavior-unverified.

### Mutation checks I ran on the post-ship behavior

`app.js` was restored byte-for-byte after each (`git diff --quiet -- src/spur/static/app.js` clean).

| Break | Command | First failure | Status |
|-------|---------|---------------|--------|
| `completePending()`: drop the `input.value === ''` guard (`const next = plan(chosen);`) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | `AssertionError: bore shape, D-flat with bore_flat emptied: the pick completed on the default` | red, as intended |
| `completePending()`: drop `deriveSelector(s);` on the other-target path | same command | `AssertionError: twin selectors: shows ('D-flat', 'Hex'), expected ('Round', 'Hex')` | red, as intended |

### Note on the superseded "with focus" clause

The 24-01 must-have and the first report said a pending pick "focuses the field that needs a number". That behavior was deliberately replaced after the Codex cross-review: on Blink and Gecko (Windows, Linux) an arrow key on the focused select commits the next option and fires `input`, so moving the focus at the first pending step sent the next arrow key into the number box (WR-01 / CX-02). L42 carries a dated amendment (2026-10-13) that says so and says which sentences it supersedes; the superseded paragraph in the entry is marked in place. This is a recorded decision, not a drift, and it does not weaken any roadmap success criterion; it removes the one defect the first report had left open. I do not mark the 24-01 truth failed for a clause a logged decision retired.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `_option()`, `_BORE_SHAPE`, `json_schema_extra={"selectors": [_BORE_SHAPE]}` | VERIFIED | Unchanged since `470b78a`; emitted through the schema. |
| `src/spur/static/app.js` | `buildSelectors()`, `deriveSelectors()`/`deriveSelector()`, `plan()`, `write()`, `pick()`, `pend()`, `showPending()`, `endPending()`, `completePending()`, stash, three derive call sites | VERIFIED | Present, substantive, wired (`select.addEventListener('input', ...)` at `:332`; the form listener at `:608`). |
| `src/spur/static/style.css` | `label.selector` grid sharing and `.selector.pending` | VERIFIED | Unchanged since the first report. |
| `tests/test_selector.py` | walk, grid, round trip, meta-red tests | VERIFIED | 16 passed. |
| `tests/browser_session.py`, `tests/test_browser.py` | selector helpers, `bore shape` step, recorder, every pick, completion, abandon, focus, `twin selectors` | VERIFIED | 2 passed; two breaks go red. |
| `tests/test_api.py` | tightened pins under L42 | VERIFIED | 62 passed. |
| `docs/architecture/decision_log.md` | `## L42` plus the 2026-10-13 amendment | VERIFIED | Amendment matches the code read above (capture-phase listener, one value write, no focus, empty box). |
| `docs/architecture/web-ui.md` | states the shipped behavior | VERIFIED | Says the typed number completes the pick, anything else ends it, the focus never leaves the select. |
| `bench/RESULTS.md` and `investigation/*.log` | priced section and seen-red table | VERIFIED | Present, unchanged since the first report. |

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `GearParams.model_config` | `GET /api/schema` | `json_schema_extra` top-level key | WIRED |
| `buildForm()` | `buildSelectors()` | `schema.selectors ?? []` | WIRED |
| `readHash()`, form `input` listener, `#reset` | `deriveSelectors()` | after `applyRelations()` | WIRED (three sites) |
| form capture-phase `input` listener | `completePending()` | pending pick completion | WIRED (browser steps drive it) |
| `pick()` / `completePending()` | `plan()` then `write()` | one rule, one write statement | WIRED |
| `deriveSelector()` | `holds()` | one evaluator for relations and selectors | WIRED |
| `tests/test_selector.py` | `tests/test_relations.py` | evaluator import | WIRED |

### Data-Flow Trace (Level 4)

| Artifact | Data | Source | Real data | Status |
|----------|------|--------|-----------|--------|
| Bore shape select options | option labels | `/api/schema` `selectors`, from the model | Yes | FLOWING |
| Bore shape select state | `selectedIndex` | `holds()` over live field values | Yes | FLOWING |
| A completed pick's writes | `eq` zeros and stashed strings | `plan()` over the live fields and the stash, never an invented number | Yes | FLOWING |

### Behavioral Spot-Checks and Probes

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Model-side proof | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"` | 16 passed in 0.07s | PASS |
| API pins and schema | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q"` | 62 passed in 15.47s | PASS |
| Browser proof | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | 2 passed in 25.89s | PASS |
| Golden pins untouched | `git diff --quiet 07cba05..HEAD -- tests/regression/` | exit 0 | PASS |
| Full gate | `make verify` | `1311 passed in 245.48s`, coverage 97.82 %, exit 0 | PASS |

No `probe-*.sh` scripts are declared by this phase.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-selector-schema-carried | 24-01, 24-02 | Options on the model in L41's vocabulary; `app.js` renders from the schema with no bore field name | SATISFIED | SC1, truths 1 and 5 |
| REQ-selector-derives-and-writes-through | 24-01, 24-03, 24-04 | State derived on load without writing; a change writes the minimum as `"0"`, stashes and restores, adds no `fields` entry; no foreign key in any request or the hash | SATISFIED | SC2, truths 2, 3, 6, 7. The keyboard path no longer has the first report's open warning. |
| REQ-selector-round-trips-per-state | 24-02, 24-03 | Model-driven round trip per state; the 44 golden sets unchanged | SATISFIED | SC3, truths 5 and 6 |

All three IDs appear in the PLAN frontmatter (`24-01`: schema-carried, derives-and-writes-through; `24-02`: round-trips, schema-carried; `24-03`: derives-and-writes-through, round-trips; `24-04`: derives-and-writes-through, round-trips) and in `.planning/REQUIREMENTS.md` lines 140-153 (checked) and traceability rows 258-260. No requirement maps to Phase 24 without a plan claiming it.

### Prohibitions (ADR-550 D3)

| Prohibition | Tier | Result |
|-------------|------|--------|
| No `GearParams` field added or default moved (L05) | test | Enforced: 31 fields; golden and `pre_v0_2.json` diff empty |
| No bore field name, option table or second grammar in `app.js` | test | Enforced by the field-name pin; `grep bore_` over the selectors section is empty |
| Write only the chosen option's own false conditions, never an invented value | test | Enforced by `plan()`: `eq` gets `String(value)`, `gt` gets only a stashed string or goes pending; the browser step compares every pick with a rule computed from the schema |
| Never write while deriving | test | Enforced by the `bore shape` and `golden sweep` steps and the red-seen derive-call removals |
| No foreign key in any `/api/*` request or the hash | test | Enforced by the recorder with `no_foreign_key` after every step |
| `golden_requests.json` and `pre_v0_2.json` not edited to absorb a change | test | Empty diff |
| A completed pick writes no number nobody typed (L08) | test | Enforced: the empty-box case stays pending, seen red by my break above |
| No wait, timeout or bar moved toward a pass (24-04) | judgment | Non-authoritative LLM-judge verdict: no violation found (`c0675b9` touched only `bench/RESULTS.md` and logs). The 2026-10-13 amendment declines to compare its single timing reading with 24-04's mean, which is the honest choice. |

No prohibition is flagged unverified.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | `TBD`, `FIXME`, `XXX`, `TODO` greps over `params.py`, `app.js`, `tests/test_selector.py`, `tests/test_browser.py`, `tests/browser_session.py` return nothing | - | - |
| `src/spur/static/app.js` | 294-300, 387-389 | Stash is not cleared when the user edits the same field by hand (IN-01); a restore can bring back an older or page-default string | Info | Accepted knowingly for the hash case by D-19; open in the disposition |
| `src/spur/static/app.js` | 315 | A selector naming a missing group throws in `buildForm()` (IN-02, CX-03) | Info | Cannot occur with the shipped model; `test_selector.py` walks the group |
| `tests/test_api.py` | 142 | `"selectors" not in /openapi.json` is a substring test (IN-03) | Info | Not a defect today |
| `tests/test_browser.py` | ~1612 | Zero-request assertion in `twin selectors` can pass before a 350 ms debounce fires (CX-05) | Info | Test-strength nit; the same step's row assertions are what went red in my break |
| `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` | - | Hex warning names snake_case fields (IN-04) | Info | Filed, trigger fired, fix scheduled before Phase 25 |

None of these is a blocker. The six open items in `24-REVIEW-DISPOSITION.md` are all `info` severity.

### Human Verification Required

None open. Both items from the first report were put to the human and recorded as `pass` in `24-UAT.md` (2 passed, 0 issues). Item 1 (keyboard walk) stands: the focus rule changed in the user's favour, since the focus now never leaves the select and the test asserts it after every pending pick. Item 2 (synchronous pick) stands: the handlers are still synchronous. One limit is stated plainly: no engine that commits an option per arrow key is driven by the test (Chrome Headless Shell on macOS opens the popup), so the keyboard walk on Blink and Gecko (Windows, Linux) rests on the human's UAT pass and on the focus assertion, not on a machine-driven key press. L42's amendment says the same.

### Gaps Summary

No gaps. Every roadmap success criterion and every plan truth holds in the current tree, including the behavior added after the ship: the pending-pick completion, the focus rule, the twin-selector cleanup and the empty-box guard. The only item filed against this report is advisory: the seen-red table does not list the three post-ship fixes' reds. I re-ran two of those breaks and both went red.

---

_Verified: 2026-10-13T05:10:00Z_
_Verifier: Claude (gsd-verifier)_
