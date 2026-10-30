---
phase: 33-interfaces-and-parity
verified: 2026-10-30T05:33:27Z
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
covered_digest: "v3:sha256:d48b3122bbc6566175326df047a8152ee5e29ef09a7e33e32f9d5b8b975b7f77"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed:
    - "PR #53 Codex review: while a link's or switch's schema loads, the old form's pending debounced edit or a Reset no longer rewrites the hash the new form reads, so a shaft link's numbers are no longer replaced by defaults (91910cd)"
    - "Prior advisory (IN-05 slug rounding had no debt file): filed as docs/tech_debt/active/2026-10-29-shaft-slug-rounds-to-six-significant-digits.md, severity nice, INDEX row present (737a3ee)"
  gaps_remaining: []
  regressions: []
coincidental_reliance_items:
  - truth: "SC4: no link token the number box blanks builds a non-default part under a blank box"
    reason: undeclared-precondition
    harden: "Holds for the int-field tokens 0-0, 00-0, 0-9 and 00-9 only because spoke_count and hole_count both default to 0; app.py blank_in_a_number_box does not refuse them. The docstring says so and a walker test fails if any int field of the gear or shaft query models reads those tokens as anything but its default. Residual tracked in docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md (must); human accepted it at UAT test 1 (pass)."
advisory:
  - finding: "A fetch failure of the new part's schema (non-overtaken) re-arms the old form (formShown = build) but does not replay an edit that update() dropped while the schema was loading. The old form is then live but its preview and hash can lag one edit behind until the next edit or Reset"
    category: other
    reason: "Error path only (a failed schema fetch), page says 'Could not build the form', the old form is untouched and the next keystroke rebuilds. No number is printed from a stale form: the download href and rows are those of the last successful build. Not a must-have; not reproduced by any test"
    evidence_status: "read from app.js:104-112 and :479; no test exercises it"
---

# Phase 33: Interfaces and Parity Verification Report

**Phase Goal:** The same shaft (preview, numbers, designation and STL/STEP) comes from the web page, the API and the CLI, one set of numbers for all three, the designation can be given in place of the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Verified:** 2026-10-30T05:33:27Z
**Status:** passed
**Re-verification:** Yes. The previous report (a717ce6, status passed) went stale: commit 91910cd landed on covered files (`src/spur/static/app.js`, `tests/test_browser.py`).

## What changed since the last report

`git diff --stat a717ce6..HEAD -- src tests`: `src/spur/static/app.js` (+12/-3) and `tests/test_browser.py` (+39). The rest of that range is `.planning/STATE.md`, a new tech-debt file and its INDEX row. No other `src/` file moved, so `app.py`, `cli.py`, `shaft_model.py`, `shaft_params.py`, `index.html`, `style.css` and `vendor/` are byte-identical to what the last report verified.

The bug (Codex, PR #53): while a link or a switch fetched another part's schema, the old form was still on the page. Its pending debounced edit, or a Reset, called `update()`, which wrote the old part's query to the hash with `history.replaceState`. The new form then ran `readHash()`, read that hash, and the shaft link's numbers became defaults. That is an L05 breach (an unset or foreign value changing the part).

## The fix, read line by line (`app.js`)

| Place | Change | Read as |
|-------|--------|---------|
| `:90` | `let formShown = 0` -- the `formSeq` of the form on the page | New state, initial 0 = `formSeq` initial 0 |
| `:324` `followHash` | `formShown = ++formSeq` (was `formSeq++`) | Every link starts with the page "shown at the current seq"; a same-part link stays live, synchronously, before any await |
| `:110` `buildForm` catch | after the overtaken check, `formShown = build` before rethrow | A non-overtaken fetch failure leaves the old form on the page, so it must answer edits again |
| `:198` `buildForm` success | `formShown = build`, set in the same synchronous block as `part = which` | No await between the last overtake check (`:113`) and `:198`, so `build === formSeq` there and the new form is live the instant it exists |
| `:479` `update()` | `if (!part \|\| formShown !== formSeq) return;` | While any `buildForm` is in flight, `formSeq` is ahead of `formShown` and `update()` is a no-op |

Paths walked against that code:

- **Bootstrap** (`:904`): `followHash` sets both to 1, `buildForm('gear')` takes seq 2, `part` is `''` so `update()` returns either way; success sets `formShown = 2`. A failing bootstrap fetch sets `formShown = 2` and rethrows to the `followHash` catch; `part` stays `''`, so nothing builds (WR-05 holds).
- **Same-part link** (`which === part`, `:326`): `formShown = ++formSeq` runs first, so `update()` passes. If a switch's build was in flight, it is now overtaken (`build !== formSeq`) and returns `false` after its fetch; the page stays on the part it shows. The golden sweep (one request per link) relies on this synchronous branch and passes.
- **Link to the other part** (`:329`): `formShown` is behind `formSeq` for the whole fetch; edits and Reset of the old form are dropped; on success the new form is built, `formShown = build`, then `readHash()` reads the untouched link and `update()` sends it. This is the fixed case.
- **`switchTo`** (`:243`): no `formShown` write of its own; `buildForm` supplies it. During the fetch the old form's edits are dropped (the old form is about to be thrown away and the switch is defined as "no value crosses", D-13). Success: `update()` runs with the new part live. Non-overtaken failure: old form re-armed, `markPart()` puts the radio back.
- **`refuseLink`** (`:304`): `refused` is set before `buildForm('gear')`; the fetch no longer lets `update()` re-show the refusal message early, but `refuseLink` shows it itself after the build (`:314`), and a keystroke after the build reaches `update()` live and hits `if (refused)`. The superseded-failure case (WR-01) is unchanged: the overtaken build returns `false` at `:108` before the new `formShown` write, so it cannot re-arm a form the newer link owns.
- **Throw midway** (`:118`-`:196`, WR-05): `part = ''` keeps `update()` a no-op whatever `formShown` is; the next link's `followHash` or the next switch's `buildForm` restores both.
- **Overtake after the page is emptied**: impossible. No await sits between `:113` and `:208`.

`refuse()` (102 chars) and `gearQuery()` (299 chars) are byte-equal to `6800769` (compared by SHA-1 of the extracted bodies, both refs), so the WR-02 fix still reads as C1.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | API and CLI serve the shaft with the gear routes' contract; designation in place of the fields; a clash is a 422 naming the fields; gear routes and `/api/schema` unchanged | VERIFIED | No `app.py`/`cli.py`/`shaft_*.py` change since a717ce6. I re-ran `tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py`: `264 passed in 11.80s` |
| 2 | Web page serves the shaft: part switch, preview, schema rows, designation, STL/STEP, `part=shaft` round trip, other `part` refused visibly; browser test in `make verify` | VERIFIED | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -q -n0 --no-cov`: `4 passed in 55.46s`. The one browser test carries `bad part refused`, `part switch`, `shaft link round trip`, `golden sweep`, `superseded build that fails`, `form build that throws midway`, `refused link whose build fails` and the new `old form edited while a link's form loads`; all pass |
| 3 | One parametrised test proves web, API and CLI report the same value for every shaft number and download name | VERIFIED | `tests/test_shaft_parity.py` is in the 264 above; the browser's `parity: web and API` step passes. `slug()` and the model are untouched |
| 4 | WR-02 fixed where the part switch edits `refuse()`/`gearQuery()`, read as C1 (server-side fix); browser proof over every number field | VERIFIED as read by C1, IN-01 residual accepted | Both function bodies equal `6800769` (above). `as-written sweep`, `number box tokens` and `shaft as-written sweep` pass in the browser run |
| 5 | Gate delta recorded in `bench/RESULTS.md`; Phase 30 check green; the 44 golden links still send what `golden_requests.json` pins | VERIFIED | `golden sweep` passes in the browser run (it drives the synchronous same-part branch of `followHash`, the path this fix touched). `bench/RESULTS.md`, `tests/regression/` and `bench/` are not in the delta. Orchestrator gate at HEAD 91910cd: `make verify` = `2783 passed in 239.79s` (not re-run by me) |

**Score:** 5/5 truths verified (0 present, behavior-unverified).

### Delta check: the 91910cd fix (behavior-dependent: an ordering invariant across an await)

| # | Claim | Status | Evidence |
|---|-------|--------|----------|
| D1 | While another part's schema loads, the old form's debounced edit and Reset cannot rewrite the hash the new form reads | VERIFIED | Code: `update()` returns at `:479` while `formShown !== formSeq`, and `formSeq` is bumped by `buildForm` at `:98` before its fetch. Test: new browser step holds `/api/shaft/schema`, `fill`s a gear field, sets the shaft link, waits 1000 ms (`DEBOUNCE_SETTLE_MS`, past the 350 ms debounce), clicks Reset, asserts the fragment still equals the link, releases the schema and asserts `reference_d=30`, `module=2`, `teeth=14` in the controls. Passes in my run. The orchestrator saw it red on the unfixed code (`assert '' == 'part=shaft&reference_d=30&module=2&teeth=14'`) |
| D2 | The same-part link path is not broken | VERIFIED | Branch at `:326` runs after `formShown = ++formSeq`, so `update()` is live; `golden sweep` (44 links, one request each) and `shaft link round trip` pass |
| D3 | The refused-link path (`refuseLink`) is not broken | VERIFIED | `refused` still set first, message shown after the build, `update()` reaches `if (refused)` once live. Steps `bad part refused`, `superseded build that fails`, `refused link whose build fails` and the `aria-disabled` read pass. L41 guard group: `17 passed` (`.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py -k "shut or field or refused"`) |
| D4 | `switchTo` and the bootstrap are not broken | VERIFIED | Walked above; `part switch`, bootstrap load of every page in the browser test, and the radio-follow checks pass |
| D5 | WR-01 (stale failing build writes no error over a newer page) and WR-05 (no build while the page holds no part) still hold | VERIFIED | The overtaken-failure `return false` at `:108` precedes the `formShown = build` write, so a stale build cannot re-arm a form; `part = ''` precedes everything in the emptied window. Steps `superseded build that fails` and `form build that throws midway` pass |
| D6 | No new `TBD`/`FIXME`/`XXX`, no shut verb written by script | VERIFIED | `grep` on the changed files finds no marker; `node --check src/spur/static/app.js` is clean; the L41 guard is green |

### Deferred Items

None. No gap, so nothing to defer.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | A failed fetch of the new part's schema re-arms the old form but does not replay an edit `update()` dropped while the schema loaded; preview and hash can lag one edit until the next edit or Reset | other | Error path only, page shows "Could not build the form", no test evidence, no printed number is wrong (rows and download href stay those of the last successful build) |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/static/app.js` | `formShown` declared, set in `followHash`, on `buildForm` success and on non-overtaken failure, read in `update()` | VERIFIED | 5 touch points read at `:90 :110 :198 :324 :479`; wired (every `buildForm` caller goes through them); `node --check` clean |
| `tests/test_browser.py` | step reproducing the race | VERIFIED | `:2827`-`:2864`, runs in the passing browser test |
| `docs/tech_debt/active/2026-10-29-shaft-slug-rounds-to-six-significant-digits.md` + INDEX row | closes the earlier advisory | VERIFIED | file present, `nice`, INDEX line 23 |
| Earlier artifacts (`shaft_model.py`, `shaft_parity.py`, `bench/`, `index.html`, `style.css`, `app.py`, `cli.py`) | unchanged | VERIFIED | no diff since a717ce6 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `buildForm` fetch start | `update()` no-op | `formSeq` ahead of `formShown` | WIRED | new browser step |
| `buildForm` success / non-overtaken failure | `update()` live | `formShown = build` | WIRED | `part switch`, `refused link whose build fails`, golden and link steps |
| `followHash` | `update()` live (same-part) | `formShown = ++formSeq` | WIRED | `golden sweep` |
| `hash` -> `readHash` of the new form | the link's own numbers | old form can no longer rewrite the hash | WIRED | new browser step reads `reference_d`, `module`, `teeth` |
| Prior links (`/api/shaft/model.{fmt}` -> `_serve_model`, CLI -> `resolve_shaft`, `renderInfo` -> `schema.dims`, `refuseLink` -> `markRefused`) | | | WIRED (regression) | tests above |

### Data-Flow Trace (Level 4)

The delta renders nothing new: an integer counter and an early return. Shaft rows and preview flow as before (`rows equal the API's`, `data-triangles equals the served STL` inside the passing browser test).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Browser test incl. the new race step | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -q -n0 --no-cov` | 4 passed in 55.46s | PASS |
| Light shaft/CLI/parity/as-written/seam tests | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py` | 264 passed in 11.80s | PASS |
| L41 guard group | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py -k "shut or field or refused"` | 17 passed, 52 deselected in 2.31s | PASS |
| JS syntax | `node --check src/spur/static/app.js` | no output | PASS |
| `refuse` / `gearQuery` identical to `6800769` | extract bodies from `git show <ref>:src/spur/static/app.js`, SHA-1 | equal (102 and 299 chars) | PASS |
| New step red before the fix | not re-run by me (would mean editing a covered file); orchestrator saw `assert '' == 'part=shaft&reference_d=30&module=2&teeth=14'` on the unfixed code | | accepted orchestrator evidence |
| Whole gate | orchestrator: `make verify` at 91910cd | 2783 passed in 239.79s | PASS (orchestrator evidence) |

### Probe Execution

No `probe-*.sh` declared or present. Skipped.

### Requirements Coverage

All six phase IDs appear in PLAN frontmatter and are ticked `[x]` in REQUIREMENTS.md (lines 85-98) with traceability rows 174-179 reading `Complete`. None is orphaned. `REQ-gate-cost-recorded` (33-01, 33-09) belongs to Phase 34 and is not judged here.

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-shaft-api | 33-02, 33-04, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-cli | 33-05, 33-09 | SATISFIED | truths 1, 3 |
| REQ-shaft-web | 33-02, 33-06, 33-07, 33-08, 33-09, 33-10 | SATISFIED | truth 2, D1-D5 |
| REQ-designation-input | 33-04, 33-05, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-parity | 33-05, 33-08, 33-09 | SATISFIED | truth 3 |
| REQ-wr02-fixed | 33-01, 33-03, 33-08, 33-09 | SATISFIED as read by C1, IN-01 residual accepted (UAT test 1: pass) | truth 4 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/static/app.js` | | `TBD` / `FIXME` / `XXX` | none | grep found none |
| `src/spur/static/app.js` | `:104-112`, `:479` | dropped edit not replayed after a failed schema fetch | Info (advisory above) | error path only |

### Human Verification Required

None. UAT test 1 is `pass`; nothing in the delta changes what a person sees on a successful path except that the link's numbers now survive an edit made while its form loads, which the browser step reads directly in the controls.

### Gaps Summary

No gap. The five roadmap success criteria hold at HEAD 91910cd. The one new commit is a 12-line change to `app.js` plus a browser step: `update()` is a no-op while another part's form is loading, and each of the three ways a build ends (success, non-overtaken failure, a same-part link's own bump) re-arms the form on the page. I walked the bootstrap, same-part, other-part, switch, refused-link, overtaken and throw-midway paths against the code and ran the browser test (4 passed), the 264 light tests and the 17 L41 guard tests green. `refuse()` and `gearQuery()` are byte-equal to `6800769`, so the WR-02 fix still reads as C1. The IN-05 follow-up from the previous report is closed by the filed debt item.

---

_Verified: 2026-10-30T05:33:27Z_
_Verifier: Claude (gsd-verifier)_
