---
phase: 33-interfaces-and-parity
verified: 2026-10-29T09:00:00Z
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
covered_digest: "v3:sha256:054666bedad6bdeeccce5ac1fd0fe97fcec77b3da5564d92d100231df4209074"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5
  gaps_closed:
    - "G-33-2: Gear | Shaft switch below the canvas under 820 px"
    - "G-33-2: refused-link form still looks editable"
    - "G-33-2: dark-mode primary button text 3.75:1 under WCAG AA"
  gaps_remaining: []
  regressions: []
coincidental_reliance_items:
  - truth: "SC4: no link token the number box blanks builds a non-default part under a blank box"
    reason: undeclared-precondition
    harden: "Holds for the int-field tokens 0-0 and 00-0 only because spoke_count and hole_count both default to 0; app.py blank_in_a_number_box does not refuse them. Tracked in docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md (must). Human accepted this residual at UAT test 1 (result: pass)."
advisory:
  - finding: "WR-03 (33-REVIEW.md): when the gear build behind a refused link throws, refused and body[data-refused] stay set, so the old part's form is dimmed and unresponsive with a build-error message and no way out except the other radio or a reload (app.js:259-288)"
    category: other
    reason: "Reachable only with a failing /api/schema fetch or a malformed schema, not from today's server (same reach as WR-01); a side effect of 33-10's visible refused look. Open in 33-REVIEW-DISPOSITION.md"
    evidence_status: "read by the orchestrator and by me against app.js:259-288; not reproduced in a browser"
  - finding: "WR-04 (33-REVIEW.md): the refused look is CSS only; the form stays focusable and typable by keyboard and carries no aria-disabled / aria-describedby"
    category: other
    reason: "A trade the 33-10 plan and style.css's comment record against the L41 guard; the review notes aria-disabled and aria-describedby do not match the guard. 33-REVIEW.md says to file it as must debt if deferred; no such item exists in docs/tech_debt/active/ yet"
    evidence_status: "review finding, guard regex not re-run by me"
---

# Phase 33: Interfaces and Parity Verification Report

**Phase Goal:** The same shaft (preview, numbers, designation and STL/STEP) comes from the web page, the API and the CLI, one set of numbers for all three, the designation can be given in place of the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Verified:** 2026-10-29T09:00:00Z
**Status:** passed
**Re-verification:** Yes, after gap closure (UAT gap G-33-2, plan 33-10)

## What changed since the last report

`git diff --stat 0248ce3 HEAD -- src tests bench Makefile pyproject.toml docs` touches only `src/spur/static/app.js` (6 lines), `src/spur/static/style.css` (34), `tests/test_browser.py` (137), `bench/RESULTS.md`, `docs/architecture/web-ui.md`, the debt INDEX and one new debt file. No Python module under `src/spur/`, no `index.html`, nothing under `src/spur/static/vendor/`, no `tests/regression/` and no `ci.yml` changed (all diffs empty; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` clean). So the 33-01..33-09 code verified earlier is untouched; the regression check below re-ran its tests rather than trusting that.

## Goal Achievement

### Observable Truths (ROADMAP success criteria, regression-checked)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | API and CLI serve the shaft with the gear routes' contract; designation in place of the fields; clash is a 422 naming the fields; gear routes and `/api/schema` unchanged | VERIFIED (regression) | No `src/spur/*.py` change since the prior report. I re-ran the 260 light tests (`tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py`): `260 passed in 11.63s` |
| 2 | Web page serves the shaft: part switch, preview, schema rows, designation, STL/STEP, `part=shaft` round trip, other `part` refused visibly; browser test in `make verify` | VERIFIED (regression) | I ran `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/pytest --no-cov -n0 -q tests/test_browser.py`: `4 passed in 48.62s` (the prior run was 3 tests; the fourth is the new `test_the_contrast_ratio_is_the_wcag_formula`). The `bad part refused`, `part switch`, `shaft link round trip` and `golden sweep` steps are inside the one browser test and pass with 33-10's edits in place |
| 3 | One parametrised test proves web, API and CLI report the same value for every shaft number and download name | VERIFIED (regression) | `tests/test_shaft_parity.py` in the 260 above; browser step `parity: web and API` inside the passing browser test. Seen-red evidence for it is unchanged in `bench/RESULTS.md` |
| 4 | WR-02 fixed where the part switch edits `refuse()`/`gearQuery()`, read as C1 (server-side fix); browser proof over every number field | VERIFIED as read by C1, IN-01 residual accepted | `refuse()` and `gearQuery()` bodies at HEAD are string-identical to `6800769` (compared from `git show`, both functions; the `app.js` diff since `0248ce3` contains no line of either). `as-written sweep`, `number box tokens`, `shaft as-written sweep` pass in the browser run above. IN-01 (`0-0`, `00-0` on int fields): human recorded `pass` at UAT test 1, debt file filed |
| 5 | Gate delta recorded in `bench/RESULTS.md`; Phase 30 check green; the 44 golden links still send what `golden_requests.json` pins | VERIFIED | `golden sweep` step passes in the browser run; `tests/regression/` and `ci.yml` byte-equal to `v0.6`. The orchestrator's gate on this HEAD: `make verify` ends `2779 passed in 245.64s` (`postgate.log` tail read by me). `bench/RESULTS.md` has the 33-01 baseline and 33-09 delta sections plus three new 33-10 seen-red rows |

**Score:** 5/5 truths verified (0 present, behavior-unverified).

### Gap closure: G-33-2 and the plan 33-10 must_haves

Each truth below is behavior-dependent (computed layout, computed style, contrast), so presence in the CSS is not enough: each is backed by a browser step that I ran green in the `4 passed` run above, and that the plan and `bench/RESULTS.md` record as seen red on the unfixed page.

| # | 33-10 must-have | Status | Evidence |
|---|-----------------|--------|----------|
| G1 | Under 820 px the Gear | Shaft switch sits above the canvas; switch still first child of `<aside>`; index.html unchanged; landmark holds both radios; desktop column unchanged | VERIFIED | `style.css` narrow block: `aside { display: contents; }`, `.part-switch { order: -2; ... }`, `#view { order: -1; }`, margins moved onto the three children; the old `aside { border-right: 0; border-top }` rule is gone with the box. Step `narrow layout` (test_browser.py:2909) passes; recorded tops at 800x900: switch 57, canvas 109, results 604, form 1217; red on the unfixed page: `switch 1170, canvas 45`. `git diff --stat 0248ce3 HEAD -- src/spur/static/index.html` empty. I read `33-10-narrow.png`: header, PART with both radios, canvas, downloads, warnings, results, form, Reset/Copy link |
| G2 | A refused-part link leaves the form visibly non-editable (opacity 0.45, pointer-events none on `form#params` and `#reset`, solid outline on `.part-switch`); a radio click or valid link restores it; message words unchanged in `#messages`; edits and keyboard Reset still build nothing | VERIFIED | `style.css` `body[data-refused] #params, body[data-refused] #reset { opacity: .45; pointer-events: none; }` and `body[data-refused] .part-switch { outline: 2px solid var(--accent); ... }`. `app.js` sets `document.body.dataset.refused = ''` once (in `refuseLink`, beside `refused = text`) and deletes it twice (`switchTo`, `followHash`, beside each `refused = null`): `grep -n "refused = " ` shows exactly the four assignments, each with its dataset twin. The step `bad part refused` asserts `REFUSED_LOOK == DEAD_LOOK` after each bad link and during the D-20 block, and `LIVE_LOOK` after a radio click (test_browser.py:2711) and after a valid link (:2729). I read `33-10-refused.png`: dimmed fields, outlined PART switch with neither radio checked. Red on the unfixed page: `At index 0 diff: '1' != '0.45'` |
| G3 | Dark-mode `.btn.primary` text at least 4.5:1, light unchanged | VERIFIED | Dark block sets `--accent-fg: #131619` (the dark `--bg`); `.btn.primary { color: var(--accent-fg); background: var(--accent) }` (style.css:158); light `--accent-fg: #ffffff`, `--accent: #b8412c` untouched. I recomputed with the WCAG 2 formula: `#131619` on `#e0573f` = 4.846:1, white on `#b8412c` = 5.482:1, white on `#e0573f` (old) = 3.747:1. Step `primary button contrast` reads the computed colours of `#dl-stl` under `emulate_media` and passes; `test_the_contrast_ratio_is_the_wcag_formula` passes |
| G4 | Each new check seen red once, a row under `### Seen red once (Phase 33)` | VERIFIED | `bench/RESULTS.md` lines 7594-7596: three `33-10` rows with the red assertion text (`'1' != '0.45'`, `switch 1170, canvas 45`, `3.75:1`) |
| G5 | `make verify` green; L41 guard `writes_a_field_shut` green; `refuse()`/`gearQuery()` identical to `6800769`; vendor and index.html unchanged | VERIFIED | Orchestrator gate `2779 passed`; I ran the guard's group myself (`tests/test_api.py -k "shut or field"`: `15 passed`); identity and unchanged-file checks above |
| G6 | Dark link-text shortfall (4.47:1 on `--panel`) filed as `must` debt, not fixed | VERIFIED | `docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md` has `Severity: must`, `Status: active`, and an INDEX row (INDEX.md:19). The file is dated 2026-10-29, not the plan's 2026-10-28; the plan allowed a later date. Dark `--accent` is unchanged (diff adds only `--accent-fg`), as the prohibition requires |

Prohibitions in 33-10 (all `resolved`, `verification: test` or judgment): none is violated. Switch stays in `<aside>` with index.html untouched (D-12); no script writes a shut verb and the guard is green (L41); the refused message is still `showMessages([text])` into `#messages` with its words unchanged (D-15, `app.js:259-269`); `refuse()`/`gearQuery()` and `vendor/` untouched; the light tokens and dark `--accent` are unchanged in the css diff. None of these test-tier prohibitions is left without enforcement: C1 identity is an explicit check in the plan and the guard test and browser asserts cover the rest.

**Is G-33-2 closed?** Yes. All three root causes named in `33-UAT.md` (the aside-held switch reordered by `#view { order: -1 }`, a refusal that left a live-looking form, dark `--accent-fg` of white at 3.75:1) are fixed in the shipped files, each with a browser assertion and a red-first record. One UAT "missing" item reads "place the message by the switch": the plan met it by outlining the switch while the message stays in `#messages` (D-15 locks the message's place); the orchestrator's fresh `33-UI-REVIEW.md` (18/24) confirms the three fixes on the live page and I read the two pictures above.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/static/style.css` | `display: contents`, `body[data-refused]`, dark `--accent-fg` | VERIFIED | all three present, substantive, used by the page |
| `src/spur/static/app.js` | `dataset.refused` beside each `refused` assignment | VERIFIED | 3 occurrences (lines 199, 262, 278) |
| `tests/test_browser.py` | `REFUSED_LOOK`, steps `narrow layout`, `primary button contrast`, `_contrast` + formula test | VERIFIED | lines 167, 2909, 2954, 297, 311; all pass |
| `docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md` | measured, deferred | VERIFIED | `Severity: must`, INDEX row |
| Prior artifacts (`app.py`, `cli.py`, `shaft_params.py`, `shaft_model.py`, parity tests, `bench/`) | unchanged | VERIFIED | no diff since the prior report; light tests pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app.js` `refuseLink`/`switchTo`/`followHash` | `style.css` `body[data-refused]` | attribute set/deleted beside `refused` | WIRED | grep shows exactly these three writes; step `bad part refused` observes the computed effect |
| step `bad part refused` | computed opacity/pointer-events/outline | `REFUSED_LOOK` constant | WIRED | used at test_browser.py:2668, 2692, 2711, 2729 |
| step `primary button contrast` | `#dl-stl` computed colours | `_contrast`, pinned by its formula test | WIRED | both pass |
| Prior links (`/api/shaft/model.{fmt}` -> `_serve_model`, CLI -> `resolve_shaft`, `renderInfo` -> `schema.dims`, hash -> `followHash`) | | | WIRED (regression) | tests above |

### Data-Flow Trace (Level 4)

No new data-rendering artifact in 33-10 (CSS state and one body attribute). Prior shaft rows and preview flows are unchanged and covered by the browser test (`rows equal the API's`, `data-triangles` equals the served STL).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Browser test incl. the 33-10 steps | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/pytest --no-cov -n0 -q tests/test_browser.py` | 4 passed in 48.62s | PASS |
| Light shaft/CLI/parity/as-written/seam tests | `.venv/bin/pytest --no-cov -n0 -q tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py` | 260 passed in 11.63s | PASS |
| L41 guard group | `.venv/bin/pytest --no-cov -n0 -q tests/test_api.py -k "shut or field"` | 15 passed | PASS |
| `refuse`/`gearQuery` untouched | body of each at `6800769` vs HEAD | equal | PASS |
| Contrast numbers | WCAG 2 formula by hand | 4.846 / 5.482 / 3.747 | PASS |
| Whole gate | not re-run by me; orchestrator: `make verify` `2779 passed in 245.64s` | | PASS (orchestrator evidence, same HEAD, no source change since) |

### Probe Execution

No `probe-*.sh` declared or present. Skipped.

### Requirements Coverage

All six phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md; none is orphaned. `REQ-gate-cost-recorded` (33-01, 33-09) is mapped by REQUIREMENTS.md to Phase 34 and is not judged here.

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-shaft-api | 33-02, 33-04, 33-09 | SATISFIED | truth 1 (regression) |
| REQ-shaft-cli | 33-05, 33-09 | SATISFIED | truths 1, 3 |
| REQ-shaft-web | 33-02, 33-06, 33-07, 33-08, 33-09, 33-10 | SATISFIED | truth 2, plus G1-G3: the page's primary control is reachable under 820 px, a refusal looks refused, the download buttons read at 4.85:1 |
| REQ-designation-input | 33-04, 33-05, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-parity | 33-05, 33-08, 33-09 | SATISFIED | truth 3 |
| REQ-wr02-fixed | 33-01, 33-03, 33-08, 33-09 | SATISFIED as read by C1, IN-01 residual accepted by the human (UAT test 1: pass) | truth 4 |

Bookkeeping, not a gap: in `.planning/REQUIREMENTS.md` only `REQ-shaft-web` is ticked and marked Complete (lines 90, 176); the other five checkboxes (lines 85, 88, 94, 96, 98) and Pending rows (174, 175, 177-179) are still unticked. Tick them when the phase is closed.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (33-10 diff) | | `TBD`, `FIXME`, `XXX`, `TODO`, `HACK` in added lines of `src`, `tests`, `bench`, `docs/architecture` | none | grep returned nothing |
| `src/spur/static/app.js` | 259-288 | WR-03: dimmed, stuck form if the gear build behind a refused link throws | Warning (advisory) | Needs a failing schema fetch or malformed schema; open in the disposition ledger. Not a must-have failure |
| `src/spur/static/style.css`, `app.js:262` | 221-223 | WR-04: refused look is visual only, no aria state | Warning (advisory) | Deliberate trade recorded in the css comment; the review asks that deferral be filed as `must` debt and no such file exists yet |
| `src/spur/static/app.js` | 97-113, 174 | WR-01 (prior): `buildForm` throw leaves `part` stale | Warning (open) | as before |
| `docs/architecture/http-api.md` | 45-48 | WR-02 (prior): split endpoint table | Warning (open) | docs rendering only |

All of these are `open` in `33-REVIEW-DISPOSITION.md`; `33-REVIEW.md` has 0 critical findings. None touches a must-have.

### Human Verification Required

None open for the phase goal. UAT test 1 is `pass` (IN-01 accepted). UAT test 2 is the gap now closed; its visual judgments (that the outline reads as attached to the switch; that the narrow page reads like the desktop column) were checked against the screenshots `33-10-refused.png` and `33-10-narrow.png` and the fresh 33-UI-REVIEW.md. If the human wants a last eyeball, `/gsd-verify-work 33` re-runs UAT test 2. The two manual-only rows in `33-VALIDATION.md` (`nyquist_compliant: false`) are human-deferred and were accepted at `/gsd-validate-phase 33`; they are not a verification item here.

### Gaps Summary

No gap. G-33-2 is closed: three fixes in `style.css` and `app.js`, each asserted by a browser step I ran green, each recorded red on the unfixed page, with D-12, D-15, D-20, L41 and C1 intact. The five roadmap success criteria still hold on the same HEAD (260 light tests, 4 browser tests, orchestrator's `make verify` 2779 passed). Follow-ups, none blocking: file WR-04 as `must` debt or fix it with `aria-disabled`/`aria-describedby` (the review says neither matches the L41 guard), decide WR-03, and tick the five open boxes in REQUIREMENTS.md.

---

_Verified: 2026-10-29T09:00:00Z_
_Verifier: Claude (gsd-verifier)_
