---
phase: 23-conditional-form-fields
verified: 2026-10-12T03:14:13Z
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
covered_digest: "v3:sha256:08b061761dfd6a78cdccb7207a4c38eec3770ec64370beb3671b50456e19ddfb"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/4
  gaps_closed: []
  gaps_remaining: []
  regressions: []
advisory:
  - finding: "23-REVIEW IN-08 (narrowed): the honeycomb family is still probed at one open value (hex_cell 0.05); the spoke and hole families now have a second open value."
    category: other
    reason: "Test-strength residual in the regression net, not a behaviour gap. Needs a follow-up test, not a code fix."
    evidence_status: "23-REVIEW (72bac17) read; not exercised"
  - finding: "23-REVIEW IN-11: _js_number in tests/browser_session.py is exact for 1e-6 <= |value| < 1e21 only; no declared relation threshold is near that range."
    category: other
    reason: "Oracle edge range. Latent: no declared threshold is affected, and the oracle's own test pins the range it covers."
    evidence_status: "code read; test_the_oracle_reads_a_link_as_the_page_does passes"
---

# Phase 23: Conditional Form Fields Verification Report

**Phase Goal:** The form says a field is inert before it is typed: a relation lives on the model as schema metadata, is proved against `calc` row by row, and is rendered by generic `app.js` code as dimmed-and-editable, and no link sends a different field or a different value than it does today.
**Verified:** 2026-10-12
**Status:** passed
**Re-verification:** Yes. The report from `03e264e` (passed 4/4 on `7fc03cc`) went stale when the IN-01..IN-10 review fixes changed covered files. Every must-have was re-checked against HEAD `90d6f7f`; no verdict was carried over.

## What changed since the last report

`git diff 7fc03cc HEAD` over `src` and `tests` touches four files: `src/spur/static/app.js` (+4), `tests/browser_session.py`, `tests/test_browser.py`, `tests/test_relations.py`. Confirmed by `git diff --stat`:

| Path | Diff since `7fc03cc` |
|------|----------------------|
| `src/spur/calc.py`, `model.py`, `app.py`, `cli.py` | empty (also empty since Phase 22's `c065d6d`) |
| `src/spur/params.py` | empty (the phase's own edits predate `7fc03cc`) |
| `src/spur/static/style.css` | empty (+11 lines since `c065d6d`, all from this phase, before the UAT) |
| `tests/regression/pre_v0_2.json`, `golden_requests.json` | empty (also empty since `c065d6d`) |
| `tests/test_api.py`, `test_cli.py`, `capture_requests.py` | empty |

The only runtime change is `app.js`: `reason.setAttribute('aria-hidden', 'true')` on the reason span (`app.js:93`), with a comment. Everything else is tests and docs (`decision_log.md` L41 tense plus one sentence on the per-field catch; `23-01-PLAN.md`, `23-SECURITY.md`, two filings).

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `/api/schema` carries every declared relation as the model wrote it; `_f()` accepts `enabled_when`; the two `Literal` fields carry it the same way; AND-only project grammar; `GearParams` gained no field; `app.js` names no `GearParams` field outside `DIMS` | VERIFIED | `GearParams.model_json_schema()` dumped now: 31 properties, 11 carry `enabled_when` (`bore_d bore_flat hex_wall hole_circle_d hole_d hub_d keyway_depth keyway_width rim_wall spoke_fillet spoke_width`), the L41 list. `params.py` has an empty diff since the last report. The `app.js` / CLI schema-walk pins pass (6 passed). |
| 2 | Every declared relation is one `calc` backs, and a test goes red on drift; the keyway pair is refused (422), never gated on each other; `recess_*` and `bore_flat`-at-`bore_d=0` not declared; `pre_v0_2.json` untouched | VERIFIED | `calc.py` and `tests/regression/` have an empty diff. `tests/test_relations.py`: 56 passed (54 at the last report; +1 meta-test, +1 from the two new cutout states in the parametrised control). Mutation, run by me: see below. |
| 3 | In a real browser an inert field is `.field.inactive` with a reason from the gate's `title`, stays editable, keeps its value, is still sent; the 44 golden queries are unchanged; `#spoke_count=0&hub_d=40` loads with `hub_d` editable and sent; re-evaluated on `input`, `readHash`, Reset, `hashchange`; dim state asserted per relation | VERIFIED | Real headless Chromium, `tests/test_browser.py`: `2 passed in 12.03s`. Output shows the four flip links (`bore_hex=0.05`, `spoke_count=1`, `hole_count=1`, `hex_cell=0.05`), the refused pair (`invalid ['bore_hex','keyway_depth','keyway_width'], dimmed and invalid ['keyway_depth','keyway_width']`), and `unknown relation op: bore_d unreadable, the form still builds the part`. The `gearQuery()` and `DIMS` code is not in any diff. The three `applyRelations()` call sites are unchanged (`readHash`, the input listener, `#reset`). |
| 4 | Pins tightened, not removed, under one `Lxx` that supersedes 08 D-09 and keeps L02; idea and debt filed with INDEX rows; conditional-fields idea retired | VERIFIED | L41 is in `decision_log.md` with "supersedes 08 D-09, keeps L02"; line 2630 now records that the throw is caught per field in `applyRelations()` (IN-09 closed). Filing edits since the last report are wording only (`702d6ba`, `247d09e`). |

**Score:** 4/4 truths verified, 0 present but behavior-unverified.

### Mutation evidence that the new tests are load-bearing

Each mutation was applied, run, and restored from a copy; `git status` is clean afterwards.

| Mutation | Test run | Result |
|----------|----------|--------|
| Delete `reason.setAttribute('aria-hidden', 'true')` from `app.js` (the IN-02 line) | `tests/test_browser.py` | `1 failed, 1 passed`: `AssertionError: inert fields: reasons readable twice: ['reason-teeth', ...]` at `test_browser.py:781`. The new browser assertion catches the only runtime change. |
| `hub_d` gate changed to `spoke_count eq 1` in `params.py` | `tests/test_relations.py` | `3 failed, 53 passed` (the forward check, `test_each_relation_names_the_driver_calc_obeys`, and the control). A relation true only at one count is red. |
| Remove the two new cutout states (`spokes (4)`, `holes (3)`) from `CUTOUT_STATES` | `tests/test_relations.py` | `2 failed, 54 passed`: both `test_a_relation_true_only_at_the_first_open_count_goes_red` cases fail. The meta-test genuinely depends on the second open value, which is the IN-08 fix. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `when()`, `_extra()`, 11 declarations | VERIFIED | Unchanged; schema dump above. |
| `src/spur/static/app.js` | generic `applyRelations()`, `holds()`, `need()`, `effective()`, per-field catch | VERIFIED | Read `:75-175`. No `disabled`/`hidden`/`readOnly`/`.value` write in the relations section; the `catch` writes only `classList.remove('inactive')`, `textContent`, `aria-describedby`. |
| `src/spur/static/style.css` | `.field.inactive`, `.reason`, `.reason:empty` | VERIFIED | Unchanged since the UAT. |
| `tests/test_relations.py` | kernel-free proof, 12 cutout states | VERIFIED | 56 passed. |
| `tests/browser_session.py`, `tests/test_browser.py` | oracle, sweep, flips, refused pair, unknown-op step | VERIFIED | 2 passed (including the new `test_the_oracle_reads_a_link_as_the_page_does`, which needs no browser). `ruff check` clean; `mypy --strict` clean on the three touched test files. |
| `docs/architecture/decision_log.md` L41 | decision, filings | VERIFIED | Present. |

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `GearParams` (`_extra`) | `/api/schema` | `model_json_schema()` | WIRED (11 in dump) |
| `/api/schema` `enabled_when` | `fields` map | `rels: prop.enabled_when ?? []` (`app.js:97`) | WIRED |
| `fields` map | `.inactive` + reason | `applyRelations()` | WIRED (3 call sites) |
| `applyRelations()` failure | build | per-field `catch` | WIRED; browser step asserts the next keystroke reaches `api/model.stl?teeth=24` and the error row's text survives it |
| reason span | input's description | `input.setAttribute('aria-describedby', reason.id)` | WIRED, pinned byte-for-byte at `tests/test_api.py:224` and `:298`; the browser step also asserts the described set equals the dimmed set |
| form fields | request query | `gearQuery()` | UNCHANGED, not in any diff |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Real Data | Status |
|----------|---------------|--------|-----------|--------|
| `.reason` text | `rels` + gate `title` | `/api/schema` | Yes | FLOWING |
| `.reason` text (error row) | `err.message` | the schema's own op string | Yes, asserted verbatim in the browser | FLOWING |
| `.inactive` class | `holds()` over `effective(field)` | live input values | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Relation proof | `.venv/bin/python -m pytest tests/test_relations.py -q -p no:cacheprovider -n0 --no-cov` | 56 passed in 0.14s | PASS |
| No-disable guard (`writes_a_field_shut`) and `app.js` pins | `pytest tests/test_api.py tests/test_cli.py -k "every_gear_field_reaches or schema_drives_the_form or openapi_documents or shareable_link_round_trips or every_key_the_ui_reads or root_shape_link or no_disabled or inactive or relation"` | 6 passed | PASS |
| Real browser: dim state, sweep, flips, refused pair, Reset, unknown op, aria | `.venv/bin/python -m pytest tests/test_browser.py -q -p no:cacheprovider -n0 --no-cov -s` | 2 passed in 12.03s | PASS |
| Import contracts | `make lint-imports` | 5 kept, 0 broken | PASS |
| Unfinished-work scan | `make no-fake-done`; `TBD/FIXME/XXX` count over the 5 changed src/test files | exit 0; 0 | PASS |
| Lint and types on touched tests | `ruff check src tests`; `mypy --strict` on 3 test files | All checks passed; no issues | PASS |
| Full gate | not re-run by me; the orchestrator ran `make test` on `5fe41d7` (same source as HEAD): 1295 passed, 97.99 % | accepted | n/a |

### Probe Execution

No probe is declared or conventional for this phase. SKIPPED.

### Requirements Coverage

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-enabled-when-metadata | 23-01, 23-02 | SATISFIED | Truth 1 |
| REQ-relations-calc-backed | 23-02 | SATISFIED | Truth 2, and the driver-level mutation |
| REQ-dim-and-editable | 23-01, 23-03, 23-04 | SATISFIED | Truth 3 |
| REQ-form-walk-proves-relations | 23-01, 23-02, 23-03, 23-04 | SATISFIED | Truths 3 and 4 |

All four IDs appear in plan frontmatter (`23-01`: lines 19; `23-02`: 16; `23-03`: 16; `23-04`: 32) and in `.planning/REQUIREMENTS.md` (`[x]` at lines 114, 120, 128, 133; traceability rows 254-257, Complete). No requirement maps to Phase 23 without a claiming plan, so nothing is orphaned.

### Prohibitions (ADR-550)

| Prohibition | Tier | Verdict |
|-------------|------|---------|
| Never disable/hide/clear an inert field or drop it from what is sent | test | Enforced. `writes_a_field_shut` (19 positive probes, must-not-match list incl. `input.setAttribute('aria-describedby', reason.id)`) passes on the current `app.js`. `aria-hidden` is not in its alternatives and is not a field write: it sits on the reason span, not the input, and the field stays editable. The browser value/editable/sent assertions still pass. |
| `app.js` names no `GearParams` field outside `DIMS`; restates no calc rule | test | Enforced (pin passes). |
| Never filter, reword or hide a calc warning in `app.js` | test | Enforced by absence: `showMessages` is not in any diff. |
| Add no `GearParams` field; move no default, bound or type | test | Enforced: 31 fields, `params.py` unchanged. |
| Declare no relation `calc` does not back | test | Enforced by two independent checks, both shown red under mutation above. |
| Change no `calc`/`model`/`app.py`/CLI; both regression files byte-identical | test | Enforced: empty diff since `c065d6d`. |
| Do not delete, loosen or allow-list an `app.js` pin | judgment | `unverified-prohibition: human review recommended` (non-authoritative LLM reading, previously resolved by the person in the UAT). Facts re-checked: `git diff c065d6d HEAD -- tests/test_api.py` deletes exactly two lines (a docstring clause and the `fields.set(...)` token, replaced by a longer one); `test_api.py` is unchanged since `7fc03cc`. Nothing loosened. |
| Do not drop, add or alter a D-09 row | judgment | Same flag. The schema dump shows the 11 rows equal to L41's list. |
| Move no wait, timeout or bar toward a pass | judgment | Same flag. A grep of `git diff 7fc03cc HEAD -- tests` for `timeout`, `BUILD_WAIT_MS`, `wait_for`, `debounce`, `sleep` on changed lines is empty. The new assertions only add checks (stricter refused-pair comparison, post-keystroke text, aria). |

### Anti-Patterns Found

None blocking. No `TBD`/`FIXME`/`XXX` in any changed file; `make no-fake-done` exits 0. Review of the fixes (`72bac17`): 0 critical, 0 warning, 2 info open (IN-08 honeycomb, IN-11); both are in the advisory list.

## Human Verification: does the UAT verdict still apply?

Yes. `23-UAT.md` (2/2 passed) judged (1) the dim's legibility in light and dark themes and the refused keyway pair, and (2) the three judgment-tier prohibitions.

1. Visual: `style.css` is byte-identical to the tree the person saw. The only `app.js` change is `aria-hidden="true"` on a span, an attribute with no visual effect. The success path of `applyRelations()` is the same statements in the same order. I found no visible change, so no human look is needed.
2. Prohibitions: re-derived above from the current tree. Nothing loosened, dropped or moved.

The `Cannot tell whether this field is used: ...` row remains something the UAT never saw (reachable only with a tampered or stale schema, styled by the existing `.reason` rule, asserted by text in the browser). Optional, not a gate.

Human verification items outstanding: none.

### Gaps Summary

No gaps. The goal holds on the current tree: the relation is model metadata (11 declarations in 31 fields), `calc` backs each and the cutout drivers are proved by name at two open values per count family, generic `app.js` renders it dimmed-and-editable in a real browser, and the query path (`gearQuery()`, `DIMS`, both regression files) is untouched. The one runtime change since the last report (`aria-hidden` on the reason span) is covered by a browser assertion that goes red when the line is removed. Remaining open items are two info-level test-strength notes (IN-08 honeycomb, IN-11 `_js_number` edge range).

---

_Verified: 2026-10-12_
_Verifier: Claude (gsd-verifier)_
