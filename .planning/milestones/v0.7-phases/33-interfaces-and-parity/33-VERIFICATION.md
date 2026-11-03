---
phase: 33-interfaces-and-parity
verified: 2026-10-30T05:57:33Z
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
covered_digest: "v3:sha256:ff1a12dccfc61a369a2ebb8828d17f672e428b0010808021031ba8e27117216b"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed:
    - "Prior advisory: after a non-overtaken schema-fetch failure the re-armed old form could show an edit that update() dropped during the wait, while the rows and STL/STEP links still came from the build before it. Closed by d1c520a (rows and downloads dropped, status set, next edit builds)"
  gaps_remaining: []
  regressions: []
coincidental_reliance_items:
  - truth: "SC4: no link token the number box blanks builds a non-default part under a blank box"
    reason: undeclared-precondition
    harden: "Holds for the int-field tokens 0-0, 00-0, 0-9 and 00-9 only because spoke_count and hole_count both default to 0; app.py blank_in_a_number_box does not refuse them. The docstring says so and a walker test fails if any int field of the gear or shaft query models reads those tokens as anything but its default. Residual tracked in docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md (must); human accepted it at UAT test 1 (pass)."
advisory:
  - finding: "The new `dropped` flag is not reset by a same-part link that overtakes the build it was set under. A later non-overtaken schema failure with no dropped edit of its own then also clears the rows and STL/STEP links, though they still match the form"
    category: other
    reason: "Safe direction only: it removes numbers, never shows a wrong one (L08 holds). Needs an edit during a part-switch fetch, then a same-part link before that fetch returns, then a later failing schema fetch. Read from app.js:94, :115-120, :209, :335, :491 (the only three writes of `dropped = false` are in buildForm); no test exercises it. Resolves with a `dropped = false` in followHash's same-part branch"
    evidence_status: "read from code; no test"
---

# Phase 33: Interfaces and Parity Verification Report

**Phase Goal:** The same shaft (preview, numbers, designation and STL/STEP) comes from the web page, the API and the CLI, one set of numbers for all three, the designation can be given in place of the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Verified:** 2026-10-30T05:57:33Z
**Status:** passed
**Re-verification:** Yes. The previous report (79a245b, status passed) went stale: commit d1c520a landed on covered files (`src/spur/static/app.js`, `tests/test_browser.py`).

## What changed since the last report

`git diff --stat 79a245b..HEAD`: `src/spur/static/app.js` (+13/-1) and `tests/test_browser.py` (+42). Nothing else moved, so `app.py`, `cli.py`, `shaft_model.py`, `shaft_params.py`, `index.html`, `style.css`, `bench/` and `docs/` are byte-identical to what the last report verified.

The problem it closes: while a link's or a switch's schema loads, `update()` is a no-op (91910cd), so an edit made then builds nothing. If that schema fetch then fails, the old form is re-armed. Its box shows the dropped edit, but the rows and the STL/STEP links on the page were those of the build before it. A number no control on the page produced (L08).

## The fix, read at HEAD (`app.js`)

| Place | Change | Read as |
|-------|--------|---------|
| `:94` | `let dropped = false` | New state |
| `:491` `update()` | `if (!part) return;` then `if (formShown !== formSeq) { dropped = true; return; }` | The early return is split in two. The `!part` branch (emptied page, WR-05) does not set the flag. Only an edit the old, still shown form lost sets it |
| `:115-120` `buildForm` catch, after the overtaken check and `formShown = build` | if `dropped`: `#dims` emptied, `setDownloads(null)`, `setStatus(mesh ? "Showing the last valid <noun>" : '')`; then `dropped = false`; then rethrow | Same three calls and same text as `update()`'s own `fail()` (`:510-512`). `P` is still the old part's here because nothing was emptied, so the noun is right. The caller's catch (`switchTo`, `followHash`) shows "Could not build the form" and `markPart()` |
| `:209` successful build | `dropped = false` | The new form owns the page; the flag belongs to the form that was thrown away |

Paths walked:

- **Edit or Reset during the wait, schema fails (the advisory):** flag set, then the catch clears rows and downloads, the box (30) no longer sits above the 24-tooth rows, and the next keystroke runs `update()` live and builds. The new browser step asserts exactly that.
- **No edit during the wait, schema fails:** `dropped` is false, so rows and downloads of the last build stay. They still match the form. Unchanged behavior.
- **Schema succeeds after a dropped edit:** the old form is replaced, `dropped = false` at `:209`. The link's numbers are read by `readHash()`. Unchanged (91910cd step still covers it).
- **Overtaken failure (WR-01):** `return false` at `:112`, before the new block, so a stale failure clears nothing and leaves the flag for the build that owns the page. Unchanged.
- **Overtaken success:** `return false` at `:123`; the flag survives to the newer build, which resets or acts on it.
- **Same-part link (`followHash`, `:335`):** untouched. `formShown = ++formSeq` runs first, `update()` is live, nothing is dropped. Golden sweep passes (one request per link).
- **`refuseLink`:** a failing gear build in it throws to `followHash`'s catch, which calls `clearRefusal()` and shows the error. The clear of rows is the same as above; no refusal state is touched by the new lines.
- **`switchTo`, bootstrap, WR-05:** bootstrap has `part === ''`, so `update()` returns before the flag; the flag is false and the catch block skips. A throw midway keeps `part = ''`, same.
- **Mesh left on screen:** the preview still shows the last valid part and the status says so. Same message the 422 path uses.

`refuse()` and `gearQuery()` are not in the diff, so the WR-02 fix still reads as C1.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | API and CLI serve the shaft with the gear routes' contract; designation in place of the fields; a clash is a 422 naming the fields; gear routes and `/api/schema` unchanged | VERIFIED | No `app.py`/`cli.py`/`shaft_*.py` change since 79a245b. I re-ran `tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py`: `264 passed in 13.39s` |
| 2 | Web page serves the shaft: part switch, preview, schema rows, designation, STL/STEP, `part=shaft` round trip, other `part` refused visibly; browser test in `make verify` | VERIFIED | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -q -n0 --no-cov`: `4 passed in 58.74s`. The browser test carries `bad part refused`, `part switch`, `shaft link round trip`, `golden sweep`, `superseded build that fails`, `form build that throws midway`, `refused link whose build fails`, `old form edited while a link's form loads` and the new `old form edited while a failing form loads`; all pass |
| 3 | One parametrised test proves web, API and CLI report the same value for every shaft number and download name | VERIFIED | `tests/test_shaft_parity.py` in the 264 above; the browser's `parity: web and API` step passes. `slug()` and the model are untouched |
| 4 | WR-02 fixed where the part switch edits `refuse()`/`gearQuery()`, read as C1 (server-side fix); browser proof over every number field | VERIFIED as read by C1, IN-01 residual accepted | Neither function is in the d1c520a diff. `as-written sweep`, `number box tokens` and `shaft as-written sweep` pass in the browser run |
| 5 | Gate delta recorded in `bench/RESULTS.md`; Phase 30 check green; the 44 golden links still send what `golden_requests.json` pins | VERIFIED | `golden sweep` passes in the browser run (the synchronous same-part branch). `bench/` and `tests/regression/` are not in the delta. Orchestrator gate at HEAD d1c520a: `make verify` = `2783 passed in 260.70s` (not re-run by me) |

**Score:** 5/5 truths verified (0 present, behavior-unverified).

### Delta check: the d1c520a fix (behavior-dependent: a state invariant across an await)

| # | Claim | Status | Evidence |
|---|-------|--------|----------|
| E1 | After a non-overtaken schema failure, rows and downloads of an earlier build are not shown under an edit that built nothing | VERIFIED | Code `:115-120`. Test: new browser step holds `/api/shaft/schema`, loads the gear, `fill`s teeth=30, sets `#part=shaft`, waits past the 350 ms debounce (`DEBOUNCE_SETTLE_MS`), fulfills the schema with a 500, then asserts the "Could not build the form" message, the box still reading 30, `eval_pairs(DIMS_ROWS) == []` and `#dl-stl` with no `href`. Passes in my run. The orchestrator saw it red on the unfixed code ("rows of an earlier build shown under an edit that built nothing", 15 rows of the 24-tooth build under a box reading 30). The step checks the fix's observable effect, not symbol presence |
| E2 | The next edit after the failure builds | VERIFIED | Same step fills teeth=31 and waits for `href` matching `teeth=31` |
| E3 | The same-part link path, `refuseLink`, `switchTo` and the bootstrap are not broken | VERIFIED | Walked above; `golden sweep`, `bad part refused`, `refused link whose build fails`, `part switch` and the bootstrap load pass in the browser run |
| E4 | WR-01 and WR-05 still hold | VERIFIED | The overtaken `return false` precedes the new lines; the `!part` branch does not set the flag. `superseded build that fails` and `form build that throws midway` pass |
| E5 | The step "old form edited while a link's form loads" (91910cd) still passes | VERIFIED | In the same browser run; the success path resets `dropped` and reads the link's numbers |
| E6 | No debt marker, no script writes a shut verb, lint clean | VERIFIED | `grep -nE "TBD\|FIXME\|XXX"` on both files: none. `node --check src/spur/static/app.js` clean. `ruff check tests/test_browser.py`: all checks passed. L41 guard group: `17 passed, 52 deselected in 2.49s` |

### Deferred Items

None. No gap, so nothing to defer.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | `dropped` is not reset by a same-part link that overtakes the build it was set under, so a later failing schema fetch can clear rows and links that still match the form | other | Over-clearing only (a number removed, none wrong); rare sequence; code read, no test. Not a must-have |

The earlier advisory (dropped edit not replayed after a failed schema fetch) is closed and removed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/static/app.js` | `dropped` declared, set in `update()`, acted on and reset in the `buildForm` catch, reset on success | VERIFIED | touch points `:94 :115-120 :209 :491`; wired (every `buildForm` caller passes through them); `node --check` clean |
| `tests/test_browser.py` | step reproducing the failure-after-dropped-edit case | VERIFIED | step "old form edited while a failing form loads", runs in the passing browser test |
| Earlier artifacts (`shaft_model.py`, `shaft_parity.py`, `bench/`, `index.html`, `style.css`, `app.py`, `cli.py`, `docs/architecture/*`) | unchanged | VERIFIED | no diff since 79a245b |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `update()` dropped return | `buildForm` failure catch | `dropped` flag | WIRED | new browser step |
| `buildForm` failure catch | `#dims`, `#dl-stl` | `replaceChildren()`, `setDownloads(null)` | WIRED | step asserts empty rows and no `href` |
| `buildForm` failure catch | next `update()` live | `formShown = build` | WIRED | step builds teeth=31 |
| Earlier links (`/api/shaft/model.{fmt}`, CLI -> `resolve_shaft`, `renderInfo` -> `schema.dims`, `refuseLink` -> `markRefused`, `followHash` -> `formShown`) | | | WIRED (regression) | tests above |

### Data-Flow Trace (Level 4)

The delta removes rendered data on one error path and renders nothing new. Shaft rows and preview flow as before (`rows equal the API's`, `data-triangles equals the served STL` inside the passing browser test).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Browser test incl. both race steps | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -q -n0 --no-cov` | 4 passed in 58.74s | PASS |
| Shaft/CLI/parity/as-written/seam tests | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py` | 264 passed in 13.39s | PASS |
| L41 guard group | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py -k "shut or field or refused"` | 17 passed, 52 deselected in 2.49s | PASS |
| JS syntax | `node --check src/spur/static/app.js` | no output | PASS |
| Lint | `.venv/bin/ruff check tests/test_browser.py` | All checks passed | PASS |
| New step red before the fix | not re-run by me (would mean editing a covered file); orchestrator saw the rows assertion fail on the unfixed code | | accepted orchestrator evidence |
| Whole gate | orchestrator: `make verify` at d1c520a | 2783 passed in 260.70s | PASS (orchestrator evidence) |

### Probe Execution

No `probe-*.sh` declared or present. Skipped.

### Requirements Coverage

All six phase IDs appear in PLAN frontmatter (`REQ-shaft-api` x3, `REQ-shaft-cli` x2, `REQ-shaft-web` x6, `REQ-designation-input` x3, `REQ-shaft-parity` x3, `REQ-wr02-fixed` x5) and are ticked `[x]` in REQUIREMENTS.md (lines 85-98) with traceability rows 174-179 reading `Complete`. None is orphaned. `REQ-gate-cost-recorded` (33-01, 33-09) belongs to Phase 34 and is not judged here.

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-shaft-api | 33-02, 33-04, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-cli | 33-05, 33-09 | SATISFIED | truths 1, 3 |
| REQ-shaft-web | 33-02, 33-06, 33-07, 33-08, 33-09, 33-10 | SATISFIED | truth 2, E1-E5 |
| REQ-designation-input | 33-04, 33-05, 33-09 | SATISFIED | truth 1 |
| REQ-shaft-parity | 33-05, 33-08, 33-09 | SATISFIED | truth 3 |
| REQ-wr02-fixed | 33-01, 33-03, 33-08, 33-09 | SATISFIED as read by C1, IN-01 residual accepted (UAT test 1: pass) | truth 4 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/static/app.js` | | `TBD` / `FIXME` / `XXX` | none | grep found none |
| `src/spur/static/app.js` | `:94`, `:335` | `dropped` outlives an overtaking same-part link | Info (advisory above) | over-clears on a later failure; removes numbers, never shows a wrong one |

### Human Verification Required

None. UAT test 1 is `pass`. The delta changes what a person sees only on a failed schema fetch after an edit made during the wait, and the browser step reads that state directly (box value, rows, download link).

### Gaps Summary

No gap. The five roadmap success criteria hold at HEAD d1c520a. The new commit closes the one advisory of the last report: when a failed form build re-arms the old form after it dropped an edit, the rows and STL/STEP links of the earlier build are removed and the status says the preview is the last valid one, so no number is shown under a box that did not produce it (L08). The fix uses the same calls and text as `update()`'s own failure path, leaves the same-part, switch, refused-link, bootstrap, WR-01 and WR-05 paths as they were, and is proven by a browser step seen red before the fix and green now. The browser test (4 passed), the 264 light tests and the 17 L41 guard tests are green in my run. One minor advisory is recorded: a stale `dropped` flag can over-clear after a rare sequence.

---

_Verified: 2026-10-30T05:57:33Z_
_Verifier: Claude (gsd-verifier)_
