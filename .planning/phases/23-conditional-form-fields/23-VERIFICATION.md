---
phase: 23-conditional-form-fields
verified: 2026-10-11T14:30:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/phases/23-conditional-form-fields/23-01-PLAN.md"
  - ".planning/phases/23-conditional-form-fields/23-01-SUMMARY.md"
  - ".planning/phases/23-conditional-form-fields/23-02-PLAN.md"
  - ".planning/phases/23-conditional-form-fields/23-02-SUMMARY.md"
  - ".planning/phases/23-conditional-form-fields/23-03-PLAN.md"
  - ".planning/phases/23-conditional-form-fields/23-03-SUMMARY.md"
  - ".planning/phases/23-conditional-form-fields/23-04-PLAN.md"
  - ".planning/phases/23-conditional-form-fields/23-04-SUMMARY.md"
  - "docs/architecture/decision_log.md"
  - "src/spur/params.py"
  - "src/spur/static/app.js"
  - "src/spur/static/style.css"
  - "tests/browser_session.py"
  - "tests/capture_requests.py"
  - "tests/test_api.py"
  - "tests/test_browser.py"
  - "tests/test_cli.py"
  - "tests/test_relations.py"
covered_digest: "v3:sha256:39038fcfa85915e407eb68cf9bbd3047b900ae0083135baf342cb6e26f71b6f2"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open the shipped viewer at /#spoke_count=0&hub_d=40 in light and in dark theme. Look at the seven dimmed fields (spoke_width, hub_d, rim_wall, spoke_fillet, hole_d, hole_circle_d, hex_wall) and at the keyway pair under /#bore_hex=6&keyway_width=3&keyway_depth=1.4."
    expected: "A dimmed field reads as inert but legible: muted name/value/unit, dashed control border, the reason line ('Needs Spoke arms above 0') readable as a full row in both themes. On the refused keyway pair the accent invalid outline is still the stronger mark. The field is still obviously typeable."
    why_human: "23-01 D4 and 23-03 D5 are human_judgment items. The browser step proves the CSS rules exist, computed colours differ between dimmed and live fields, the reason is displayed, and the field stays editable. No test can say the dim reads well."
  - test: "Judgment-tier prohibitions (non-authoritative LLM verdict recorded below): confirm no app.js pin in tests/test_api.py was loosened to get green, that the eleven D-09 rows were neither dropped nor altered, and that no wait/timeout/bar was moved in 23-04."
    expected: "Agree with the verifier's reading: git diff c065d6d..HEAD on tests/test_api.py deletes only one docstring clause and rewrites one token (fields.set) to a stricter one; the declared set is exactly the eleven L41 rows; the only timeout expressions in the diff are uses of the existing BUILD_WAIT_MS constant."
    why_human: "unverified-prohibition: human review recommended. Judgment-tier prohibitions carry no deterministic enforcement; the verifier's verdict is an LLM-judge reading."
advisory:
  - finding: "23-REVIEW WR-01: an unknown enabled_when op makes holds() throw inside the input listener before scheduleUpdate(), so the part, dimensions and download links would stop following the form. On load, readHash() throwing leaves a blank, unrefreshed page with only a console trace."
    category: other
    reason: "Latent. Not reachable today: when() types op as Literal['eq','gt'] (mypy --strict), tests/test_relations.py pins ops to {eq, gt}, and the shipped app.js and schema come from one tree. Becomes reachable via a stale cached app.js against a newer server or if Phase 24 extends the grammar on one side. Disposition is still open in 23-REVIEW-DISPOSITION.md; triage before Phase 24 extends the grammar."
    evidence_status: "code read (app.js:387, :420); not exercised"
  - finding: "23-REVIEW WR-02: the 'never disables/hides/clears' static guard in tests/test_api.py is narrower than L41's wording (misses readOnly, inert, classList hidden, pointer-events/opacity, value clearing; \\.hidden\\s*= also matches ===)."
    category: other
    reason: "The browser step independently proves the shared-link field loads, is editable, keeps its value and is sent, so today's behaviour is covered. The static guard is the regression net for future edits and is weaker than its comment claims. Open in the disposition."
    evidence_status: "code read (tests/test_api.py:257-261)"
---

# Phase 23: Conditional Form Fields Verification Report

**Phase Goal:** The form says a field is inert before it is typed: a relation lives on the model as schema metadata, is proved against `calc` row by row, and is rendered by generic `app.js` code as dimmed-and-editable, and no link sends a different field or a different value than it does today.
**Verified:** 2026-10-11T14:30:00Z
**Status:** human_needed
**Re-verification:** No, initial verification

Every automated truth is verified against the code, with my own runs where I could do them cheaply. The status is `human_needed` and not `passed` for one reason: the two `human_judgment: true` coverage items (does the dim read well in both themes) have no test and are routed to a person, plus the judgment-tier prohibitions that carry only a non-authoritative reading from me.

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `/api/schema` carries every declared relation as the model wrote it; `_f()` accepts `enabled_when`; the two `Literal` fields carry it the same way; AND-only project grammar; key collides with no JSON Schema word; `GearParams` gained no field; `app.js` names no `GearParams` field outside `DIMS` | VERIFIED | `params.py` diff read: `when()`, `_extra()`, `_f(..., enabled_when=)`, `root_shape`/`recess_sides` through `_extra()`. I dumped `GearParams.model_json_schema()`: 31 properties (unchanged count), 11 carry `enabled_when`, each a bare list of `{field, op, value}`. `tests/test_relations.py` (10 passed, my run) holds the grammar walk, keyword-collision test, one-path `ast` check and Literal probe. The `app.js` pin tests (6 passed, my run, `test_api.py`/`test_cli.py`) harvest keys from `DIMS` only. |
| 2 | Every declared relation is one `calc` backs, and a test goes red on drift; the keyway pair is refused (422) and never gated on each other; `recess_*` and `bore_flat`-at-`bore_d=0` are not declared; `pre_v0_2.json` untouched | VERIFIED | My own parity script, which shares no code with the phase's test: for every spoke/hole/honeycomb dependent at min+step, mid and max with its gate false, `derive()` changes only `warnings` and a warning names the field. For `bore_d`/`bore_flat` under `bore_hex=6`, only `warnings` moves (the 9 mm / 8 mm default is the baseline and does not move). `keyway_width=3` alone and `keyway_depth=1.4` alone are each a 422 naming the keyway pair and `bore_hex`. `recess_depth` under `recess_sides=none` changes nothing and has no relation. `git diff c065d6d..HEAD` on `calc.py` and `tests/regression/` is empty. Wrong-relation red evidence is in `investigation/23-02-wrong-relation-red.log`, and three permanent meta-tests in `test_relations.py` keep it red. |
| 3 | In a real browser an inert field is `.field.inactive` with a reason from the gate's `title`, stays editable, keeps its value, is still sent; the 44 golden queries are unchanged; `#spoke_count=0&hub_d=40` loads with `hub_d` editable and sent; re-evaluated on `input`, `readHash`, Reset, `hashchange`; dim state asserted per relation | VERIFIED (visual quality is routed to human) | I ran `tests/test_browser.py` in a real headless Chromium: `1 passed in 8.30s`. It printed `golden sweep: 44 records, 44 distinct queries`, a reason for each of the seven default-dimmed fields (`hub_d: Needs Spoke arms above 0`), one flip link per gate (`bore_hex`, `spoke_count`, `hole_count`, `hex_cell`) and the refused pair with `.invalid` and `.inactive` together. The test source asserts `hub_d` is visible, editable, holds `40` and is sent as `hub_d=40`, and that typing sends `hub_d=41`. `app.js` read: `applyRelations()` sits at the end of `readHash()` (which `hashchange` calls), in the `input` listener before `scheduleUpdate()`, and in `#reset`. `gearQuery()` and `DIMS` are absent from the diff, so the query path is untouched. The 23-03 logs show the call sites are load-bearing (deleting `readHash`'s call fails the sweep, deleting `#reset`'s fails `inert fields`). |
| 4 | Pins tightened, not removed, under one `Lxx` that supersedes 08 D-09 and keeps L02; the idea for the two unbacked relations and the debt for the hex warning are filed with INDEX rows; the conditional-fields idea is retired in the closing commit | VERIFIED | L41 exists at `decision_log.md:2567` ("supersedes 08 D-09, keeps L02"). The `tests/test_api.py` diff deletes one docstring clause and rewrites one token (`fields.set(...)`) to a stricter one; the other changes are additions. Filed: `docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md` (INDEX row line 18) and `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` (INDEX row line 39). Retired: `docs/ideas/retired/2026-09-29-conditional-form-fields.md` with `Status: retired`, `Retired in:` set, INDEX row under Retired. |

**Score:** 4/4 truths verified, 0 present but behavior-unverified. The truths' state-transition behaviour (dim follows `input`, `readHash`, `hashchange`, Reset) is exercised by the browser test, not just present.

One qualification on truth 3's phrase "under the golden request sets": none of the 44 golden request sets sets `spoke_count`, `hole_count`, `hex_cell` or `bore_hex` (grep count 0), so the sweep reads one distinct dimmed set across all 44 (the default seven). It proves the query contract and the default dim state for every fixture link. The live (un-dimmed) side of each gate is proved by the four flip links and the refused pair, which is where the relation-by-relation coverage actually comes from. Together they cover every declared relation; I record this so the sweep's "44" is not read as 44 distinct dim states.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `when()`, `_extra()`, 11 `enabled_when` declarations | VERIFIED | Exists, substantive, wired (emitted by schema; consumed by `app.js`). 100% covered per the 23-02 `make verify`. |
| `src/spur/static/app.js` | generic `applyRelations()`, `holds()`, `need()`, `effective()` | VERIFIED | Substantive; three call sites; no `disabled`/`hidden` write (grep: only existing `aria-disabled` on download links). |
| `src/spur/static/style.css` | `.field.inactive`, `.reason` | VERIFIED | Dims through `--muted` and dashed border; no opacity/pointer-events by design. |
| `tests/test_relations.py` | kernel-free proof module | VERIFIED | 10 passed (my run). |
| `tests/browser_session.py`, `tests/test_browser.py` | evaluator, sweep, flips, refused pair | VERIFIED | Browser test passes (my run). |
| `docs/architecture/decision_log.md` L41 | decision | VERIFIED | Present. |
| idea, debt, retired-idea files and INDEX rows | filings | VERIFIED | See truth 4. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `GearParams` (`_extra`) | `/api/schema` | `model_json_schema()` | WIRED | 11 relations emitted verbatim (my dump). |
| `/api/schema` `enabled_when` | `fields` map in `app.js` | `rels: prop.enabled_when ?? []` | WIRED | `buildForm()` diff. |
| `fields` map | `.field.inactive` + reason | `applyRelations()` | WIRED | Three call sites; the browser test reads the resulting DOM. |
| form fields | request query | `gearQuery()` | UNCHANGED | Not in the diff; 44 golden queries match the pin. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Real Data | Status |
|----------|---------------|--------|-----------|--------|
| `.reason` text | `rels` | `/api/schema` `enabled_when` and the gate's `title` from the same schema | Yes | FLOWING (browser prints the reasons) |
| `.inactive` class | `holds()` over `effective(field)` | live input values | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Relation proof module | `pytest tests/test_relations.py -n0 --no-cov` | 10 passed | PASS |
| App.js pins and CLI schema walk | `pytest tests/test_api.py tests/test_cli.py -k "every_gear_field_reaches or schema_drives_the_form or openapi_documents or shareable_link_round_trips or every_key_the_ui_reads or root_shape_link"` | 6 passed | PASS |
| Real-browser dim state, 44-link sweep, flips, refused pair, Reset | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` | 1 passed in 8.30s | PASS |
| Independent calc parity (own script) | gate-false base, vary each dependent over bounds | all dependents move only `warnings` and are named; keyway pair 422 | PASS |
| Import contracts | `make lint-imports` | 5 kept, 0 broken | PASS |
| Full gate | not re-run (orchestrator ran `make test` on `0f59b02`: 1248 passed, 97.99%; nothing under `src/` or `tests/` changed after; `git diff HEAD -- src tests` is empty) | n/a | accepted, not re-run |

### Probe Execution

Step 7c: no probe-based verification declared or conventional (`scripts/*/tests/probe-*.sh` not referenced by any plan). SKIPPED.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-enabled-when-metadata | 23-01, 23-02 | `_f()` accepts `enabled_when`, emitted unchanged, Literal fields carry it, project grammar, keyword-collision test | SATISFIED | Truth 1 |
| REQ-relations-calc-backed | 23-02 | every relation is one `calc` backs, parity test, no unbacked relation | SATISFIED | Truth 2, my own parity run |
| REQ-dim-and-editable | 23-01, 23-03, 23-04 | dimmed with reason, editable, value kept, still sent, re-evaluated on four events | SATISFIED (visual legibility to a person is human item 1) | Truth 3 |
| REQ-form-walk-proves-relations | 23-01, 23-02, 23-03, 23-04 | field walk extends to every relation, browser asserts dim state, pins tightened under one Lxx | SATISFIED | Truths 3 and 4 |

All four IDs appear in plan frontmatter and in the REQUIREMENTS.md traceability table (lines 254-257, marked Complete). No orphans: no other requirement maps to Phase 23.

### Prohibitions (ADR-550)

| Prohibition (plan) | Tier | Verdict |
|--------------------|------|---------|
| Never disable/hide/clear an inert field or drop it from what is sent (23-01) | test | Enforced: the `test_api.py` static regex (non-vacuity probed) plus the browser value/editable/sent assertions. The regex is narrower than the wording (WR-02), the browser assertions cover the shared-link case. |
| `app.js` restates no calc rule and names no `GearParams` field outside `DIMS` (23-01) | test | Enforced: `DIMS`-only harvest pin passes (my run). The reason text states only the gate's title and threshold. |
| Never filter, reword or hide a calc warning in `app.js` (23-01) | test | Enforced by absence: `showMessages` is not in the `app.js` diff and the existing warning-rendered browser step passes. |
| Add no `GearParams` field, move no default, bound or type (23-01) | test | Enforced: 31 fields before and after; `params.py` diff shows only metadata, comments and the `_extra` refactor. |
| Declare no relation `calc` does not back and leave no "ignored" rule without one (23-02) | test | Enforced: forward and reverse tests plus my parity run. |
| Change no `calc`/`model`/`pool`/`app.py`/CLI; `pre_v0_2.json` byte-identical (23-02) | test | Enforced: `git diff c065d6d..HEAD` empty for `calc.py` and `tests/regression/`. |
| No relation under a JSON-Schema-enforced key (23-02) | test | Enforced: `test_no_extra_key_is_a_json_schema_keyword`. |
| No regeneration or hand-edit of regression files in a feature commit (23-03) | test | Enforced: regression diff empty; `make golden.regen` byte-identity proof logged. |
| Never dim a gate field (23-03) | test | Enforced: `test_relations.py` pins dependents disjoint from drivers; the refused-pair step shows the gate invalid and never dimmed. |
| Dim state follows the fields, not the server answer (23-03) | test | Enforced: flip links assert the set under 422 as well as 200; `applyRelations()` is not called from a build's success path. |
| Record no reading that was not taken (23-04) | test | Not re-derived by me; the plan's own script checks the figures against the logs. Accepted. |
| Do not delete, loosen or allow-list an `app.js` pin (23-01) | judgment | `unverified-prohibition: human review recommended.` My non-authoritative reading: the `test_api.py` diff removes one docstring clause and rewrites one token to a stricter form; everything else is additions. |
| Do not drop, add or alter a D-09 row on judgment (23-02) | judgment | `unverified-prohibition: human review recommended.` My reading: the eleven declared rows match L41's list exactly. |
| Move no wait, timeout or bar toward a pass (23-04) | judgment | `unverified-prohibition: human review recommended.` My reading: the only timeout expressions in the test diff are uses of the existing `BUILD_WAIT_MS`. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/static/app.js` | 387 / 420 | A throw in `applyRelations()` (unknown op) precedes `scheduleUpdate()` and has no visible effect (WR-01) | Warning | Latent, not reachable on the shipped tree; see advisory. |
| `tests/test_api.py` | 257-261 | Static guard narrower than its comment (WR-02) | Warning | Regression net, not current behaviour. |

Debt-marker gate (`TBD`/`FIXME`/`XXX`) on the phase's source and test files: no matches. `make no-fake-done` is part of the orchestrator's green `make verify`. The five review info items (IN-01..IN-05: reason formatting divergence at extreme values, double announce by a screen reader, a stale debt line number, a stale "08 D-09 stands" index row, mixed tenses in L41) are documentation or latent items and block nothing.

### Human Verification Required

#### 1. Does the dim read well, in both themes

**Test:** Open the viewer at `/#spoke_count=0&hub_d=40` in light and then dark theme, and at `/#bore_hex=6&keyway_width=3&keyway_depth=1.4`.
**Expected:** A dimmed field is clearly inert but legible and clearly still typeable (muted text, dashed border, the reason as a full readable row). On the refused keyway pair the accent invalid outline stays the stronger mark.
**Why human:** 23-01 D4 and 23-03 D5 are `human_judgment: true`. The browser test proves the rules apply and computed colours differ, not that the result looks right.

#### 2. Judgment-tier prohibitions

**Test:** Skim the three readings in the Prohibitions table above (no pin loosened, D-09 set intact, no wait moved).
**Expected:** You agree. My verdict is a non-authoritative LLM reading, flagged `unverified-prohibition: human review recommended`, not a silent pass.

### Gaps Summary

No gaps. The goal holds: the relation is model metadata, my independent run confirms every one of the eleven is backed by `calc` (and the keyway pair is a 422 as declared), generic `app.js` renders it dimmed-and-editable in a real browser, the query path (`gearQuery()`, `DIMS`, the 44 golden queries, both regression files) is untouched, and the pins are stricter and not removed. Two open review warnings (WR-01, WR-02) are advisory, not must-have failures, but WR-01 should be triaged before Phase 24 extends the grammar. The outstanding item is human: the visual read of the dim.

---

_Verified: 2026-10-11T14:30:00Z_
_Verifier: Claude (gsd-verifier)_
