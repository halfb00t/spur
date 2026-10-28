---
phase: 33-interfaces-and-parity
verified: 2026-10-28T03:00:00Z
status: human_needed
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
  - "bench/RESULTS.md"
  - "bench/latency.py"
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
covered_digest: "v3:sha256:5606a17556f146295913d8c6936b34e071b878e5e32ccf6f6448cc0018033763"
behavior_unverified: 0
overrides_applied: 0
coincidental_reliance_items:
  - truth: "SC4: no link token the number box blanks builds a non-default part under a blank box"
    reason: undeclared-precondition
    harden: "Holds for the int-field tokens 0-0 and 00-0 only because spoke_count and hole_count both default to 0; the rule (app.py blank_in_a_number_box) does not refuse them. Tracked in docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md (must)."
human_verification:
  - test: "Accept or reject the IN-01 residual against REQ-wr02-fixed's wording"
    expected: "The human confirms that spoke_count=0-0, hole_count=0-0 and hole_count=00-0 answering 200 (the box shows blank, the part built is the default) is an accepted, tracked residual and not a gap in 'WR-02 is fixed'. The human already deferred it at /gsd-validate-phase 33; this item records it so ship sees it."
    why_human: "Whether a token the box blanks but the API still accepts counts as 'fixed' when the built part equals the blank box's part is a reading of the requirement, not something a test can decide."
  - test: "Look at the UI-REVIEW findings on the real page (33-UI-REVIEW.md, 18/24)"
    expected: "Under 820 px the Gear | Shaft switch sits below the canvas; a refused link leaves a form that still looks editable; the dark-mode primary button text is about 3.7:1 (under WCAG AA 4.5:1). The human decides fix now, file as debt, or accept."
    why_human: "Visual layout and colour contrast on the real page; the browser test proves the switch works, not that it is findable or legible."
---

# Phase 33: Interfaces and Parity Verification Report

**Phase Goal:** The same shaft (preview, numbers, designation and STL/STEP) comes from the web page, the API and the CLI, one set of numbers for all three, the designation can be given in place of the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Verified:** 2026-10-28T03:00:00Z
**Status:** human_needed
**Re-verification:** No, initial verification

## Goal Achievement

No code, test, bench or Makefile file changed after `5c256c1`, the last plan commit; the nine commits since are `docs(...)` only (`git diff --stat 5c256c1..HEAD -- src tests bench Makefile pyproject.toml` is empty). The orchestrator's `make verify` (2778 passed, rc 0, coverage 98.48 %) therefore describes the code verified here.

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | API and CLI serve the shaft with the gear routes' contract; designation in place of the fields; clash is a 422 naming the fields; an unparseable designation names the bad token; gear routes, query keys and `/api/schema` unchanged | VERIFIED | Read `app.py:661-681`: `/api/shaft/schema`, `/info`, `/model.{fmt}`; `shaft_model` calls `_serve_model(_shaft(q), ...)`, the gear route's second caller. Run against the live app (TestClient with lifespan): `designation=W 30x2x14x8f` gives 200 with `reference_d` 30.0, `teeth=14` beside it gives 422 `type: conflict` with `ctx.fields ["designation","teeth"]`, `W 30x2xZZx8f` gives 422 "The tooth count 'ZZ' is not a whole number...", `garbage` gives 422 "must start with the type letter W, not 'garbage'", the STL answers `filename="spur_shaft_w25x1.25x18.stl"`. CLI: same clash and `ZZ` text on stderr, exit 2; `spur shaft export --designation ... -o x.step` writes the file. `GET /api/schema` keys are `description, properties, selectors, title, type` (no `dims`); route table is the gear's three plus the shaft's three; `gear.unchanged` passes inside the gate (`/api/schema` 8723 bytes equal to v0.6); `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty. 260 light tests (interfaces, parity, as-written, CLI, seam, shaft params) passed in my run |
| 2 | Web page serves the shaft: part switch; preview; numbers from a schema-carried row list; designation; STL and STEP downloads; `part=shaft` link round-trips; gear link has no `part`; other `part` refused visibly; browser test in `make verify` proves each | VERIFIED | `app.js` `PARTS`, `switchTo`, `followHash`, `partOf`, `refuseLink`; rows come from `schema.dims` (`shaft_params.py` `json_schema_extra`), `DIMS` stays the gear's only table; `index.html` radios outside `#params`. `tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` passed in my own run (3 passed, 47.8 s, with `PLAYWRIGHT_BROWSERS_PATH=.venv/ms-playwright`). Its steps `part switch` (rows equal the API's, `Designation W 25x1.25x18x8f` row, `href` `api/shaft/model.stl`/`.step`, triangle count equals the served STL, ArrowLeft on the radio returns to the gear at defaults with an empty hash), `shaft link round trip`, `bad part refused` and the 44-record `golden sweep` are in the `make verify` path |
| 3 | One parametrised test proves web, API and CLI report the same value for every shaft number and the same download name, seen red once on a perturbed number | VERIFIED | `tests/test_shaft_parity.py` (API vs CLI, raw-equal, four-shaft fixed set, name against `slug()`) and the browser step `parity: web and API` (page `dt`/`dd` pairs equal the API's at displayed text, downloaded file names equal the API's and a literal). Red: `investigation/33-05-red-perturbed.log` (`tip_d` one ulp up, `4 failed`) and `33-08-red-fmt.log`; `test_the_comparison_sees_a_one_ulp_change_and_a_changed_name` keeps the comparator itself honest. Both ran green here |
| 4 | WR-02 fixed where the part switch edits `refuse()`/`gearQuery()`: a token the box blanks but the API accepts no longer builds a non-default part under a blank box; browser proof over every number field and `mate_teeth`; debt item retired in the fixing commit | VERIFIED, read as C1 (residual noted below) | Human decision C1 (`33-01-SUMMARY.md`, `ROADMAP.md` criterion 4 and `REQUIREMENTS.md` "Reading (C1 ...)"): the fix is server-side in `69c1aa3`. Checked: `app.py:274-343` `blank_in_a_number_box` (outer whitespace, `_`, leading `+`, trailing `.`) and `_numbers_as_written` as a route dependency on `/api/info`, `/api/model`, and both shaft routes; live: `teeth=%2B18`, `module=2.`, `mate_teeth=%2020` each answer 422 `number_as_written` on gear and shaft. `refuse()` and `gearQuery()` bodies are byte-identical to `6800769` (md5 of both function bodies equal). Browser steps `blank, unknown and accepted tokens`, `number box tokens` (91-token table), `as-written sweep` (gear fields and `mate_teeth`) and `shaft as-written sweep` passed. `69c1aa3` contains the `git mv active -> resolved`, the `Resolved in:` sha and the INDEX row. Residual, see below |
| 5 | Gate delta recorded in `bench/RESULTS.md`, browser test included; Phase 30 check green; the 44 fixture links still send what `golden_requests.json` pins | VERIFIED | `bench/RESULTS.md` has `### The gate baseline (33-01)` (2644 passed, 229.17 s) and `### The gate delta (33-09)` (2778 passed, 241.55 s, +5.40 %, browser call 61.24 s) plus twelve close checks. `gear.unchanged` green; `golden sweep` step passed in my browser run; `tests/regression/` and `ci.yml` byte-equal to `v0.6` |

**Score:** 5/5 truths verified (0 present, behavior-unverified). Every behavior-dependent truth (switch, round trip, refusal, parity, as-written) has a passing behavioral test that I ran, not a presence check.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/app.py` | shaft routes, designation conflict dependency, as-written dependency | VERIFIED | substantive, wired, data flows to `derive_shaft` and `_serve_model` |
| `src/spur/cli.py` | `spur shaft info|export`, `--designation` | VERIFIED | `import spur.cli` loads no fastapi, starlette, cadquery, OCP, `spur.app`, `spur.model`, `spur.shaft_model` (checked, list empty) |
| `src/spur/shaft_params.py` | `dims` rows in schema, `SPLINE_KEYS`, `designation_clash`, `resolve_shaft`, frozen `slug()` | VERIFIED | one resolver used by API and CLI |
| `src/spur/static/app.js`, `index.html`, `style.css` | part switch, per-part routes, schema rows | VERIFIED | no second row table; `PARTS` indexed only by literals |
| `tests/test_shaft_parity.py`, `tests/shaft_parity.py`, `tests/test_browser.py` | parity, browser proof | VERIFIED | ran green |
| `tests/test_number_as_written.py`, `tests/number_box_tokens.py` | 91-token walker | VERIFIED | ran green |
| `bench/latency.py`, `bench/RESULTS.md` | shaft contention scenarios, gate delta | VERIFIED | 10 concurrent heaviest shafts: 4 x 200, 6 x 503 busy, no timeout or 500 (recorded, not re-run) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `/api/shaft/model.{fmt}` | `_serve_model` | `_shaft(q)` strips the per-endpoint class so a designation link and its flat link share a cache entry | WIRED | `app.py:681` |
| CLI `_shaft_params` | `resolve_shaft` / `designation_clash` | same functions as the API dependency | WIRED | one clash rule, two front ends |
| `app.js renderInfo` | `/api/shaft/schema` `dims` | `dims = schema.dims ?? null` | WIRED | browser `part switch` step |
| `app.js` hash | per-part form | `followHash` -> `partOf` -> `buildForm` before `readHash` | WIRED | browser `shaft link round trip` and `bad part refused` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| shaft rows in `#dims` | `info[key]` for each `dims` key | `/api/shaft/info` -> `derive_shaft` | Yes (browser rows equal the API's, null skipped) | FLOWING |
| shaft preview | STL buffer | `/api/shaft/model.stl?quality=preview` -> kernel | Yes (`data-triangles` equals triangles of the served STL) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Light shaft, number, parity, CLI, seam tests | `pytest --no-cov -n0 -q tests/test_shaft_interfaces.py tests/test_shaft_parity.py tests/test_number_as_written.py tests/test_cli.py tests/test_seam.py tests/test_shaft_params.py` | 260 passed in 11.23 s | PASS |
| Browser test (switch, round trip, bad part, parity, as-written, golden sweep, framing) | `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright pytest --no-cov -n0 -q tests/test_browser.py` | 3 passed in 47.80 s | PASS |
| Designation, clash, bad token, `+18`, `2.`, ` 20` on live routes | TestClient with lifespan | statuses and messages as in truth 1 and 4 | PASS |
| CLI clash, bad token, export | `spur shaft info|export ...` | exit 2 with the API's sentences; file written | PASS |
| `refuse`/`gearQuery` untouched | md5 of the two function bodies at `6800769` and HEAD | equal | PASS |
| Whole gate | not re-run by me; orchestrator: `make verify` 2778 passed in 216.91 s, rc 0 | | PASS (orchestrator evidence) |

### Probe Execution

No `probe-*.sh` is declared or present for this phase. Skipped.

### Requirements Coverage

All six phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md; none is orphaned.

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-shaft-api | 33-02, 33-04, 33-09 | `/api/shaft/{schema,info,model.stl,model.step}` with the gear routes' contract | SATISFIED | truth 1 |
| REQ-shaft-cli | 33-05, 33-09 | `spur shaft ...` same part, same numbers | SATISFIED | truth 1 and 3 |
| REQ-shaft-web | 33-02, 33-06, 33-07, 33-08, 33-09 | switch, preview, schema rows, designation, downloads, link round trip, visible refusal | SATISFIED | truth 2 |
| REQ-designation-input | 33-04, 33-05, 33-09 | designation in place of the fields; clash is a 422 | SATISFIED | truth 1 |
| REQ-shaft-parity | 33-05, 33-08, 33-09 | one parametrised test, web = API = CLI, download name | SATISFIED | truth 3 |
| REQ-wr02-fixed | 33-01, 33-03, 33-08, 33-09 | WR-02 fixed; debt item retired in the fixing commit | SATISFIED as read by C1, with the IN-01 residual (human item 1) | truth 4 |

`REQ-gate-cost-recorded` appears in 33-01 and 33-09 frontmatter but `REQUIREMENTS.md` maps it to Phase 34 and calls it cross-cutting; it is not a Phase 33 ID and is not judged here (the Phase 33 gate delta it needs is present). The checkboxes and the Pending rows for the six IDs are unticked in `REQUIREMENTS.md`, deliberately, per the orchestrator; tick them after the human items below are answered.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (phase diff) | | `TBD`, `FIXME`, `XXX`, `TODO`, `HACK` in added lines of `src`, `tests`, `bench/latency.py` | none | grep returned nothing |
| `src/spur/static/app.js` | `buildForm` (clear at ~97-113, `part = which` ~174) | WR-01 (review): a throw between the clear and `part = which` leaves the page empty while `part` names the old part; next same-part hashchange runs `readHash`/`update` over an empty `fields` map | Warning | Needs a malformed schema or a `buildSelectors` throw, neither reachable from today's server; the failure shows "Could not build the form". Open in `33-REVIEW-DISPOSITION.md`. Not a must-have failure |
| `docs/architecture/http-api.md` | 45-48 | WR-02 (review): blank line splits the endpoint table, so the shaft rows render as paragraph text | Warning | Documentation rendering only. Open in the disposition ledger |
| `src/spur/app.py` and L49 | `blank_in_a_number_box` | IN-01: `0-0`, `00-0` read as int 0 by pydantic, box blanks them | Warning (tracked residual) | I reproduced it: `hole_count` and `spoke_count` accept `0-0` and `00-0`; `1-0`, `5-0`, `0-1` and `teeth=0-0` are refused. Built part equals the default (both default 0). L49 and the function docstring still say no blanked token gets a 200, which is false for these two tokens |

### Human Verification Required

#### 1. IN-01 against REQ-wr02-fixed

**Test:** Read criterion 4 and REQ-wr02-fixed against the IN-01 residual: `GET /api/info?spoke_count=0-0` answers 200 while Chromium's number box shows blank.
**Expected:** Accepted as a tracked residual (`docs/tech_debt/active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md`, severity must, trigger: L49's rule is next touched, or an int field's default leaves 0, or an int field gets a lower bound below 0).
**Why human:** My finding: criterion 4's operative words ("no longer builds a non-default part under a blank box") hold, because the part built is the default, so page and part agree. The requirement's parenthetical definition of WR-02 ("a token the number box blanks but the API accepts") is still true for two tokens on two fields. The human already chose to defer at `/gsd-validate-phase`; I report it as a WARNING, not a BLOCKER, and the L49 sentence "no blanked token gets a 200" should be corrected or qualified when the item is next touched.

#### 2. UI review findings

**Test:** Open the page at under 820 px wide and in dark mode; follow a link with an unknown `part`.
**Expected:** Decide on the three `33-UI-REVIEW.md` top issues (18/24): the part switch below the canvas under 820 px, the refused-link form that still looks editable, the dark-mode primary button at about 3.7:1.
**Why human:** Layout and contrast are visual judgements. None is a success criterion, and the browser test proves function, not findability.

### Gaps Summary

No gap blocks the phase goal. All five roadmap success criteria are backed by tests I ran: the 260 light tests and the full browser test pass, the live routes and CLI behave as SC1 states, the gear schema and route table are unchanged, and `refuse()`/`gearQuery()` are byte-identical to `6800769` as C1 describes. SC4 is verified against the human-approved C1 reading. The status is `human_needed` only because two open items need a human decision: the IN-01 residual (already deferred by the human, now on record) and the UI audit findings. Two open review warnings (WR-01 stale `part` after a failed build, WR-02 split table in `http-api.md`) and the six info items stay in the disposition ledger; none touches a must-have.

---

_Verified: 2026-10-28T03:00:00Z_
_Verifier: Claude (gsd-verifier)_
