---
phase: 33-interfaces-and-parity
verified: 2026-10-29T14:13:48Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/phases/33-interfaces-and-parity/33-01-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-01-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-02-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-02-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-03-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-03-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-04-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-04-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-05-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-05-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-06-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-06-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-07-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-07-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-08-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-08-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-09-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-09-SUMMARY.md"
  - ".planning/phases/33-interfaces-and-parity/33-10-PLAN.md"
  - ".planning/phases/33-interfaces-and-parity/33-10-SUMMARY.md"
  - "bench/RESULTS.md"
  - "bench/latency.py"
  - "docs/architecture/http-api.md"
  - "docs/architecture/web-ui.md"
  - "src/spur/app.py"
  - "src/spur/cli.py"
  - "src/spur/shaft_model.py"
  - "src/spur/shaft_params.py"
  - "src/spur/static/app.js"
  - "src/spur/static/index.html"
  - "src/spur/static/style.css"
  - "tests/number_box_tokens.py"
  - "tests/shaft_parity.py"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_cli.py"
  - "tests/test_number_as_written.py"
  - "tests/test_shaft_interfaces.py"
  - "tests/test_shaft_parity.py"
covered_digest: "v3:sha256:0b4ef65c0cb7a3952c26d0b28b52e7f9eab1bef717703f63ebab32295756f661"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed:
    - "33-REVIEW WR-01: a superseded buildForm that rejects no longer writes its error over a newer page (1d3c2ce)"
    - "33-REVIEW WR-05: update() builds nothing while the page holds no part (b0de2ba)"
    - "WR-03 (prior advisory): a refusal whose own gear build fails is cleared, the form is live again (13dcdfd)"
    - "WR-04 (prior advisory): a refusal now sets aria-disabled / aria-describedby on the form's fieldsets and Reset (cace100)"
    - "WR-02 (prior advisory): shaft route rows rejoined to the endpoint table in http-api.md (dfba6f4)"
  gaps_remaining: []
  regressions: []
coincidental_reliance_items:
  - truth: "SC4: no link token the number box blanks builds a non-default part under a blank box"
    reason: undeclared-precondition
    harden: "Holds for the int-field tokens 0-0, 00-0, 0-9 and 00-9 only because spoke_count and hole_count both default to 0; app.py blank_in_a_number_box does not refuse them. IN-01 (8e913c4) now says so in the docstring and a walker test fails if any int field of the gear or shaft query models reads those tokens as anything but its default. Residual tracked in docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md (must); human accepted it at UAT test 1 (pass)."
advisory:
  - finding: "33-REVIEW-FIX.md IN-01 and IN-05 each say 'see debt below' but the report has no debt section and no debt file was filed in e6ed56e..HEAD for IN-05 (slug() keeps six significant digits, so reference_d 123.4567 and 123.4571 share a download stem; whether to go repr-exact would supersede L49). The caveat is recorded only in the slug() docstring. IN-01's residual does have its debt file (2026-10-28)"
    category: other
    reason: "CLAUDE.md asks for deferred decisions to live in docs/tech_debt or docs/ideas. It touches a download file name only, not a number the tool prints, so it does not touch a must-have; the orchestrator may want to file a nice/must item"
    evidence_status: "grep of docs/tech_debt/active and docs/ideas for slug / six-digit / repr-exact found nothing; git diff --stat e6ed56e..HEAD -- docs/tech_debt is empty"
---

# Phase 33: Interfaces and Parity Verification Report

**Phase Goal:** The same shaft (preview, numbers, designation and STL/STEP) comes from the web page, the API and the CLI, one set of numbers for all three, the designation can be given in place of the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Verified:** 2026-10-29T14:13:48Z
**Status:** passed
**Re-verification:** Yes. The previous report (e6ed56e) went stale: two code-review fix rounds (13dcdfd..c496b37) landed on covered files afterwards.

## What changed since the last report

Delta read from the source, not from the fix report. `git diff e6ed56e..HEAD -- src/`:

| File | Change | Read as |
|------|--------|---------|
| `src/spur/static/app.js` | `buildForm` wraps the schema fetch in try/catch and returns `false` when overtaken (WR-01); sets `part = ''` once the old page is emptied (WR-05 / midway throw); `update()` returns first when `part` is empty; new `markRefused()` / `clearRefusal()` set and clear `aria-disabled` + `aria-describedby="messages"` on `#params fieldset, #reset`; `followHash` catch clears the refusal and calls `markPart()` (WR-03) | Client-side robustness on failure paths. No change to `refuse()` or `gearQuery()` |
| `src/spur/app.py` | `_as_written_message` offers the generic suggestion for `+-5` (IN-02); `blank_in_a_number_box` docstring names the `0-0` exception (IN-01) | Message wording and a docstring. The rule's four conditions are unchanged (L49 locks them) |
| `src/spur/cli.py` | top-level description now "Parametric spur gears and DIN 5480 splined shafts." (IN-05) | Help text |
| `src/spur/shaft_params.py` | `slug()` docstring only; the output is unchanged (IN-05) | Comment. The frozen download name (L49, D-17) is untouched |
| `src/spur/static/style.css` | one comment line | none |
| tests and docs | new browser steps, guard assertions, token table rows, docs paragraphs | evidence, not behaviour |

No other `src/spur/` file, no `index.html`, `vendor/`, `tests/regression/` or `.github/workflows/ci.yml` entry is in the delta.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | API and CLI serve the shaft with the gear routes' contract; designation in place of the fields; a clash is a 422 naming the fields; gear routes and `/api/schema` unchanged | VERIFIED | Delta in `app.py`/`cli.py`/`shaft_params.py` is a docstring, a message string for the refusal of a non-number token, and help text. I re-ran `tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py`: `264 passed in 11.66s` (260 last time; the four are IN-01, IN-02, IN-05, IN-06). The new designation test sends `designation=nonsense&designation=W 30x2x14x8f` and pins 200 with the canonical designation |
| 2 | Web page serves the shaft: part switch, preview, schema rows, designation, STL/STEP, `part=shaft` round trip, other `part` refused visibly; browser test in `make verify` | VERIFIED | I ran `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/pytest --no-cov -n0 -q tests/test_browser.py`: `4 passed in 58.68s`. The one browser test now carries the 33-REVIEW steps `superseded build that fails`, `form build that throws midway`, `refused link whose build fails`, the 820/821 px checks and the `aria-disabled` read (test_browser.py:167-175, 2680, 2747-2869, 3086-3096), beside the earlier `bad part refused`, `part switch`, `shaft link round trip`, `golden sweep` steps; all pass |
| 3 | One parametrised test proves web, API and CLI report the same value for every shaft number and download name | VERIFIED | `tests/test_shaft_parity.py` is in the 264 above; the `part switch` step now builds its expected rows with `shaft_parity.displayed` (IN-04) and the browser step `parity: web and API` passes. `slug()` output is unchanged (docstring-only diff) so the download name still matches across the three |
| 4 | WR-02 fixed where the part switch edits `refuse()`/`gearQuery()`, read as C1 (server-side fix); browser proof over every number field | VERIFIED as read by C1, IN-01 residual accepted | I extracted both function bodies from `6800769:src/spur/static/app.js` and from HEAD and compared them: `refuse` equal (99 chars), `gearQuery` equal (296 chars). `as-written sweep`, `number box tokens` (now with `0-0`, `0-9`, `00-9` re-read in Chromium) and `shaft as-written sweep` pass in the browser run. IN-01 is now documented in the rule's docstring and pinned by a walker test over every int field of both query models |
| 5 | Gate delta recorded in `bench/RESULTS.md`; Phase 30 check green; the 44 golden links still send what `golden_requests.json` pins | VERIFIED | `golden sweep` passes in the browser run; `bench/RESULTS.md` and `tests/regression/` are not in the delta. Orchestrator's gate at HEAD c496b37: `make verify` ends `2783 passed in 236.86s` (not re-run by me; I re-ran the 264 light tests, the 4 browser tests and the L41 group) |

**Score:** 5/5 truths verified (0 present, behavior-unverified).

### Review-fix delta, checked against the code

These are behavior-dependent (ordering, failure paths, ARIA state); each is backed by a browser or guard test that I ran green, and the fix report records the first four seen red on the unfixed code.

| # | Change | Status | Evidence |
|---|--------|--------|----------|
| R1 | WR-01: a stale `buildForm` that rejects cannot write its error or clear the refusal of a newer link | VERIFIED | `app.js:94-105`: `catch` returns `false` when `build !== formSeq`, else rethrows. Browser step `superseded build that fails` holds the shaft schema answer, follows `part=bogus`, releases a 500 and asserts the refusal text, `DEAD_LOOK`, and that a keystroke builds nothing |
| R2 | WR-05 / midway throw: after a build throws, the page holds no part and `update()` builds nothing | VERIFIED | `part = ''` at `app.js:110` is set after the last await, so nothing runs between it and the end of the synchronous body that sets `part = which` (`:179`); `update()` returns first when `part` is empty (`:470`). Step `form build that throws midway` asserts no build request, rows, download `href` or `data-triangles` after Reset and a keystroke in `#mate-teeth`, and that the next link rebuilds |
| R3 | WR-03 (earlier advisory): a refusal whose own gear build throws is cleared | VERIFIED | `followHash` catch calls `clearRefusal()`, shows the build error and `markPart()`; step `refused link whose build fails` asserts the form is live and the error is the build's |
| R4 | WR-04 (earlier advisory): the refused state is announced, not only dimmed, without the shut verbs the L41 guard refuses | VERIFIED | `markRefused()` sets `aria-disabled` and `aria-describedby="messages"` on fieldsets and Reset (valid on a group and a button, noted in the comment); `clearRefusal()` removes them. The guard test (test_api.py:432-437) now also asserts `dataset.refused` has exactly one setter and one `delete`, and `markRefused(` appears twice. I ran `tests/test_api.py -k "shut or field or refused"`: `17 passed`. The L41 regex is untouched; the attributes are not `disabled`/`inert`, so focus and typing still work and IN-10 asserts the field holds `30` |
| R5 | IN-07: the narrow breakpoint is read at 800, 820 and 821 px; the refused look is read on the shaft path | VERIFIED | test_browser.py:3086-3096; passes |
| R6 | WR-02 (earlier advisory): shaft route rows rejoined to the endpoint table | VERIFIED | `docs/architecture/http-api.md` lines 45-48 now sit in one table with the gear rows; I read them |

Prohibitions: C1 (`refuse`/`gearQuery` untouched) re-proved above. L41 (no script writes a shut verb) proved by the guard, which is green. D-15 (the refusal is `showMessages([text])` into `#messages`, words unchanged) holds; `aria-describedby="messages"` only points at it. L05 (a value from one part's form never reaches the other's request) is stronger than before: `part = ''` plus the `update()` guard means a failed build cannot send the old part's defaults under a blank form.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/static/app.js` | try/catch in `buildForm`, `part = ''`, `markRefused`/`clearRefusal`, `update()` guard | VERIFIED | all present, substantive, called (`clearRefusal` from `switchTo` and `followHash`; `markRefused` from `refuseLink`) |
| `src/spur/app.py` | `_as_written_message` `+-5` branch; docstring | VERIFIED | read in the diff; covered by the new parametrised message case |
| `src/spur/cli.py` | shaft named in `spur --help` | VERIFIED | one-line diff; test in `tests/test_cli.py` passes |
| `tests/test_browser.py`, `tests/test_api.py`, `tests/number_box_tokens.py`, `tests/test_number_as_written.py`, `tests/test_shaft_interfaces.py` | new steps and pins | VERIFIED | pass |
| `docs/architecture/web-ui.md`, `docs/architecture/http-api.md` | describe the failed-build steps and the focus-order limit; one endpoint table | VERIFIED | read |
| Earlier artifacts (`shaft_model.py`, `shaft_parity.py`, `bench/`, `index.html`, `style.css` rules) | unchanged or comment-only | VERIFIED | no code diff |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app.js` `refuseLink` | `markRefused` -> `aria-*` on `#params fieldset, #reset` | one call | WIRED | guard asserts exactly two occurrences of `markRefused(` |
| `switchTo` / `followHash` | `clearRefusal` -> attribute + aria removal | beside each `refused = null` | WIRED | `refused = null` now lives only in `clearRefusal`; step reads the ARIA values after a radio click and a valid link |
| `buildForm` | `followHash` / `switchTo` catch | rethrow only when current | WIRED | step `superseded build that fails` |
| `update()` | `part` | early return when empty | WIRED | step `form build that throws midway` |
| Prior links (`/api/shaft/model.{fmt}` -> `_serve_model`, CLI -> `resolve_shaft`, `renderInfo` -> `schema.dims`, hash -> `followHash`) | | | WIRED (regression) | tests above |

### Data-Flow Trace (Level 4)

The delta renders no new data (an attribute and an early return). The shaft rows and preview flows are unchanged and covered by `rows equal the API's` and `data-triangles equals the served STL` inside the passing browser test.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Browser test incl. the review-fix steps | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/pytest --no-cov -n0 -q tests/test_browser.py` | 4 passed in 58.68s | PASS |
| Light shaft/CLI/parity/as-written/seam tests | `.venv/bin/pytest --no-cov -n0 -q tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py` | 264 passed in 11.66s | PASS |
| L41 guard group | `.venv/bin/pytest --no-cov -n0 -q tests/test_api.py -k "shut or field or refused"` | 17 passed | PASS |
| `refuse`/`gearQuery` identical to `6800769` | function bodies from `git show 6800769:src/spur/static/app.js` vs the working file | equal, both | PASS |
| Whole gate | orchestrator: `make verify` at c496b37 | 2783 passed in 236.86s | PASS (orchestrator evidence) |

### Probe Execution

No `probe-*.sh` declared or present. Skipped.

### Requirements Coverage

All six phase IDs appear in PLAN frontmatter (the counts are 3, 2, 3, 6, 3 and 5 across plans for the six) and in REQUIREMENTS.md; none is orphaned. `REQ-gate-cost-recorded` (33-01, 33-09) is mapped to Phase 34 and is not judged here.

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-shaft-api | 33-02, 33-04, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-cli | 33-05, 33-09 | SATISFIED | truths 1, 3 |
| REQ-shaft-web | 33-02, 33-06, 33-07, 33-08, 33-09, 33-10 | SATISFIED | truth 2, R1-R5 |
| REQ-designation-input | 33-04, 33-05, 33-09 | SATISFIED | truth 1 (IN-06 pins a repeated key) |
| REQ-shaft-parity | 33-05, 33-08, 33-09 | SATISFIED | truth 3 |
| REQ-wr02-fixed | 33-01, 33-03, 33-08, 33-09 | SATISFIED as read by C1, IN-01 residual accepted (UAT test 1: pass) | truth 4 |

The earlier bookkeeping note is closed: REQUIREMENTS.md lines 85-98 are ticked `[x]` and the traceability rows 174-179 read `Complete` for all six.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/static/app.js`, `app.py`, `cli.py` | | `TBD` / `FIXME` / `XXX` | none | grep found none |
| `docs/tech_debt` | | IN-05 slug rounding noted in a docstring, with no debt file | Info (advisory above) | Download name only |

`33-REVIEW.md` has 0 critical findings; `33-REVIEW-DISPOSITION.md` records 16 of 16 `fixed`, 0 open. The prior open WR-01, WR-03, WR-04 and the doc WR-02 are all fixed in the code I read above.

### Human Verification Required

None. UAT test 1 is `pass` (IN-01 accepted) and UAT test 2 (the G-33-2 gap) was closed and verified in the previous report; nothing in the delta changes what a person sees except a screen-reader announcement on a refused link, which the browser step reads as attributes. The `33-VALIDATION.md` manual-only rows were accepted earlier and are not a verification item here.

### Gaps Summary

No gap. The five roadmap success criteria still hold at HEAD c496b37: the two review rounds changed failure-path logic in `app.js`, one refusal message, one help string and docstrings, and every behavior-dependent change has a browser or guard test that I ran green (4 browser, 264 light, 17 guard). `refuse()` and `gearQuery()` are byte-equal to `6800769`, so the WR-02 fix still reads as C1. One non-blocking follow-up: file the IN-05 `slug()` rounding as debt or an idea, since the fix report points to a debt entry that does not exist.

---

_Verified: 2026-10-29T14:13:48Z_
_Verifier: Claude (gsd-verifier)_
