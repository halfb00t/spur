---
phase: 23-conditional-form-fields
verified: 2026-10-11T16:31:04Z
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
covered_digest: "v3:sha256:fda41a524f93680a505048411d02cb7133f9e4e7ffebccf20ae5597adf20d50c"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/4
  gaps_closed: []
  gaps_remaining: []
  regressions: []
advisory:
  - finding: "23-REVIEW IN-09: L41 (decision_log.md, 'the form' paragraph, 'an unknown op anywhere in a list throws and is not short-circuited past') and the T-23-04 row in 23-01-PLAN.md ('the form never builds a part') describe an unknown op as an uncaught throw. After cea8c54 holds() still throws, but applyRelations() catches it per field."
    category: other
    reason: "Doc and decision wording drift only. The behaviour change keeps D-02 ('reject an unknown op loudly'): the throw is still raised, the field shows a reason row, and the part still builds. Add one sentence to L41 so an agent does not remove the catch as dead code."
    evidence_status: "code and decision log read; 23-REVIEW disposition: open"
  - finding: "23-REVIEW IN-08 / IN-10: the new driver check probes each cutout gate at one open value (so 'spoke_count eq 1' vs 'gt 0' is caught only incidentally by the forward check), and the last assertion of the 'unknown relation op' step (to_have_count(1)) is true even if the row were cleared."
    category: other
    reason: "Test-strength gaps in the regression net, not in current behaviour. The mutations I ran go red; the residuals need a follow-up test, not a code fix."
    evidence_status: "code read; not exercised"
---

# Phase 23: Conditional Form Fields Verification Report

**Phase Goal:** The form says a field is inert before it is typed: a relation lives on the model as schema metadata, is proved against `calc` row by row, and is rendered by generic `app.js` code as dimmed-and-editable, and no link sends a different field or a different value than it does today.
**Verified:** 2026-10-11T16:31:04Z
**Status:** passed
**Re-verification:** Yes. The prior report was `passed`, then went stale when three review-fix commits (`cea8c54`, `59deb6e`, `ef5d4a7`) changed covered files. Every must-have was re-checked against the current tree at `7fc03cc`, not carried over.

## What changed since the last report, and what I did about it

`git diff 69ca1a6..HEAD -- src tests` (UAT to now) touches four files: `app.js` (+24/-), `test_api.py`, `test_browser.py`, `test_relations.py`. `style.css`, `params.py`, `calc.py`, `model.py`, `app.py`, `cli.py` and `tests/regression/` did not move after the UAT.

- `cea8c54` (`app.js`): the loop body of `applyRelations()` is byte-for-byte the old body inside a `try`. A throw now takes the `catch`: remove `.inactive`, write `Cannot tell whether this field is used: <message>` into the field's own `.reason`, set `aria-describedby`. The loop carries on, so all four call sites reach `update()`/`scheduleUpdate()`. The success path is unchanged, so the dim, the reason text and the `aria-describedby` behave exactly as the UAT saw them.
- `59deb6e` (`test_api.py`): the no-disable pattern is a strict superset of the old one for writes; it adds `readOnly`, `inert`, `toggleAttribute`, `classList`, `pointerEvents`, `opacity`, `setProperty`, plus a section-limited `.value`-write guard. The only shapes it stopped matching are comparisons (`x.hidden === y`), which are not writes. One probe per alternative plus a must-not-match list. No pin was loosened.
- `ef5d4a7` (`test_relations.py`): adds the whole-part driver check, 42 meta-tests, and a control.

Facts from the orchestrator, checked:

| Claim | Result |
|-------|--------|
| `calc.py`, `tests/regression/pre_v0_2.json`, `golden_requests.json` unchanged since `c065d6d` | TRUE. `git diff --stat c065d6d..HEAD` on `calc.py`, `model.py`, `app.py`, `cli.py`, `tests/regression/` is empty. |
| `params.py` unchanged since `c065d6d` | FALSE as stated. `params.py` is where this phase put the metadata (`when()`, `_extra()`, 11 declarations): +64/-19 since `c065d6d`. It is TRUE that it is unchanged since the UAT (`69ca1a6`) and since the prior report, which is the claim that matters here. |
| `style.css` / no CSS change by the fixes | TRUE. `style.css` last changed in `e09f834`, before the UAT. |
| `test_api.py` diff since `c065d6d` only adds tokens | TRUE. Two deleted lines in the whole range: the docstring clause `08 D-09 stands` and the token `fields.set(name, { input, wrap, title });`, the latter replaced by the longer `rels`/`reason` token. The `59deb6e` rewrite only widens the new guard. |
| `make test` 1292 passed, 97.82 % | Not re-run (about 5 minutes, already run on this tree). Accepted. My targeted runs are below. |
| `23-REVIEW.md` 0 critical / 0 warning / 10 info | TRUE (frontmatter and the report). |
| `23-SECURITY.md` `threats_open: 0` | Not re-derived. Nothing the fixes touch adds markup: the new row is `textContent`. |

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `/api/schema` carries every declared relation as the model wrote it; `_f()` accepts `enabled_when`; the two `Literal` fields carry it the same way; AND-only project grammar; key collides with no JSON Schema word; `GearParams` gained no field; `app.js` names no `GearParams` field outside `DIMS` | VERIFIED | I dumped `GearParams.model_json_schema()` now: 31 properties, and exactly 11 carry `enabled_when` (`bore_d bore_flat hex_wall hole_circle_d hole_d hub_d keyway_depth keyway_width rim_wall spoke_fillet spoke_width`), the L41 list. `pytest tests/test_relations.py`: 54 passed (was 10; the 44 new are the WR-03 meta-tests). The six `test_api.py`/`test_cli.py` pins that harvest `DIMS`-only keys: 6 passed. |
| 2 | Every declared relation is one `calc` backs, and a test goes red on drift; the keyway pair is refused (422) and never gated on each other; `recess_*` and `bore_flat`-at-`bore_d=0` are not declared; `pre_v0_2.json` untouched | VERIFIED | `calc.py` and `tests/regression/` have an empty diff since `c065d6d`; `params.py` is unchanged since the prior report, in which an independent parity script of mine confirmed all eleven. New this round, and run by me: I changed `spoke_width`'s gate on `params.py:173` to `hole_count gt 0` and ran `tests/test_relations.py`: `2 failed, 52 passed` (`test_each_relation_names_the_driver_calc_obeys`, `test_the_driver_check_passes_for_the_declared_owner_alone`). Restored from a copy; `git status` clean. So WR-03's claim holds: a wrong driver for a cutout dependent is now red. |
| 3 | In a real browser an inert field is `.field.inactive` with a reason from the gate's `title`, stays editable, keeps its value, is still sent; the 44 golden queries are unchanged; `#spoke_count=0&hub_d=40` loads with `hub_d` editable and sent; re-evaluated on `input`, `readHash`, Reset, `hashchange`; dim state asserted per relation | VERIFIED | Real headless Chromium, `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`: `1 passed in 12.50s`. Printed `golden sweep: 44 records, 44 distinct queries, 1 distinct dimmed sets`, `step inert fields: 1.30 s`, and the new `unknown relation op: bore_d unreadable, the form still builds the part`. `app.js:103`, `:399`, `:409` are the three call sites, unchanged; `gearQuery()` and `DIMS` are not in the diff. |
| 4 | Pins tightened, not removed, under one `Lxx` that supersedes 08 D-09 and keeps L02; idea and debt filed with INDEX rows; conditional-fields idea retired | VERIFIED | L41 is in `decision_log.md` and its header reads "supersedes 08 D-09, keeps L02". Filings and retirement were checked last round and no docs/ideas or tech_debt file is in the post-UAT diff. The `59deb6e` widening only adds cases. |

**Score:** 4/4 truths verified, 0 present but behavior-unverified.

The WR-01 behaviour (an unknown op no longer freezes the form) is behavior-dependent, so presence is not enough. It has a behavioural test, and I made it go red: I put the pre-fix `app.js` (`git show 69ca1a6:...`) in place and re-ran the browser test. Result: `1 failed in 51.72s` with `Locator expected to have attribute 'api/model.stl?teeth=23'  Actual value: None`, which is exactly the stale-download-link failure the fix report describes. I restored the current `app.js` from a copy and `git status` is clean. The test therefore proves the invariant, and does not pass by accident.

One qualification on truth 3, as last round: none of the 44 golden request sets sets `spoke_count`, `hole_count`, `hex_cell` or `bore_hex`, so the sweep reads one distinct dimmed set across all 44 (the default seven). The live side of each gate is proved by the four flip links and the refused keyway pair, not by the sweep.

### Does the WR-01 behaviour contradict a locked decision (L41 / D-02)?

No. D-02 requires that both evaluators "reject an unknown op loudly" and that an unknown op is a stop-and-ask, not a silent extension. After `cea8c54` `holds()` still throws on one (the `default:` branch is untouched); the page does not guess a dim state (the field is explicitly undimmed, and not treated as quietly active); and the failure is visible, as a reason row on the field that a build does not rewrite. The only thing that changed is that the throw no longer also prevents `update()`. That is consistent with L08 (nothing the page prints may be plausible but wrong) and with L05 (the field is untouched). L41 does still read "throws and is not short-circuited past", which stays true of `holds()`. The orchestrator's quoted phrase "so the form never builds a part" is not in L41; it is in the T-23-04 threat row of `23-01-PLAN.md:629`. Both are wording drift (review IN-09), not a must-have failure. Filed as an advisory above, with the recommended one-sentence addition to L41.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `when()`, `_extra()`, 11 declarations | VERIFIED | Unchanged since UAT; schema dump above. |
| `src/spur/static/app.js` | generic `applyRelations()`, `holds()`, `need()`, `effective()`; per-field catch | VERIFIED | Read in full (`:85-175`). No `disabled`/`hidden`/`readOnly`/`.value` write inside the relations section. |
| `src/spur/static/style.css` | `.field.inactive`, `.reason`, `.reason:empty` | VERIFIED | Unchanged. `.reason:empty { display:none }` means the new error text, being non-empty, is visible without `.inactive`. |
| `tests/test_relations.py` | kernel-free proof | VERIFIED | 54 passed (my run, 0.14 s). |
| `tests/test_api.py` | tightened pins | VERIFIED | 6 targeted pins pass. |
| `tests/browser_session.py`, `tests/test_browser.py` | evaluator, sweep, flips, refused pair, unknown-op step | VERIFIED | Passes; fails with the old `app.js`. |
| `decision_log.md` L41, ideas, debt, retired idea | decision and filings | VERIFIED | Present. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `GearParams` (`_extra`) | `/api/schema` | `model_json_schema()` | WIRED | 11 relations in my dump. |
| `/api/schema` `enabled_when` | `fields` map | `rels: prop.enabled_when ?? []` | WIRED | `app.js:96`. |
| `fields` map | `.inactive` + reason | `applyRelations()` | WIRED | Called at `:103` (readHash), `:399` (input listener, before `scheduleUpdate()`), `:409` (Reset). |
| `applyRelations()` failure | build | per-field `catch` | WIRED (new) | A throw cannot skip `update()`; browser step asserts the next keystroke reaches `/api/info?teeth=24`. |
| form fields | request query | `gearQuery()` | UNCHANGED | Not in any diff; 44 golden queries match the pin. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Real Data | Status |
|----------|---------------|--------|-----------|--------|
| `.reason` text (dimmed) | `rels` + gate `title` | `/api/schema` | Yes | FLOWING |
| `.reason` text (error row) | `err.message` | the schema's own op string | Yes, shown in the browser step | FLOWING |
| `.inactive` class | `holds()` over `effective(field)` | live input values | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Relation proof, incl. WR-03 meta-tests | `.venv/bin/python -m pytest tests/test_relations.py -n0 --no-cov -q` | 54 passed in 0.14s | PASS |
| `app.js` pins + CLI schema walk | `pytest tests/test_api.py tests/test_cli.py -k "every_gear_field_reaches or schema_drives_the_form or openapi_documents or shareable_link_round_trips or every_key_the_ui_reads or root_shape_link"` | 6 passed in 3.30s | PASS |
| Real-browser dim state, sweep, flips, refused pair, Reset, unknown op | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` | 1 passed in 12.50s | PASS |
| WR-01 test is load-bearing | same, with `app.js` from `69ca1a6` | 1 failed (href None); restored | PASS (goes red when it should) |
| WR-03 check is load-bearing | `params.py:173` gate swapped to `hole_count`, then restored | 2 failed, 52 passed; restored | PASS (goes red when it should) |
| Import contracts | `make lint-imports` | 5 kept, 0 broken | PASS |
| Unfinished-work scan | `make no-fake-done` | exit 0 | PASS |
| Full gate | not re-run by me; the orchestrator ran `make test` on `7fc03cc`: 1292 passed, 97.82 % | n/a | accepted |

### Probe Execution

No probe is declared or conventional (`scripts/*/tests/probe-*.sh` is referenced by no plan). SKIPPED.

### Requirements Coverage

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-enabled-when-metadata | 23-01, 23-02 | SATISFIED | Truth 1 |
| REQ-relations-calc-backed | 23-02 | SATISFIED | Truth 2, now with a driver-level proof |
| REQ-dim-and-editable | 23-01, 23-03, 23-04 | SATISFIED | Truth 3; visual legibility confirmed by the UAT |
| REQ-form-walk-proves-relations | 23-01, 23-02, 23-03, 23-04 | SATISFIED | Truths 3 and 4 |

All four IDs are in plan frontmatter (`23-01`: three; `23-02`: three; `23-03`: two; `23-04`: two) and in REQUIREMENTS.md (`[x]` at lines 114-133, traceability rows 254-257, Complete). No requirement maps to Phase 23 without a claiming plan, so nothing is orphaned.

### Prohibitions (ADR-550)

| Prohibition | Tier | Verdict |
|-------------|------|---------|
| Never disable/hide/clear an inert field or drop it from what is sent | test | Enforced, and stronger than before: the widened static guard, with 19 positive probes and a must-not-match list, plus the section-limited `.value` guard, plus the browser value/editable/sent assertions. The new `catch` branch writes only `classList.remove('inactive')`, `textContent` and `aria-describedby`. |
| `app.js` names no `GearParams` field outside `DIMS`; restates no calc rule | test | Enforced (pin passes). The error row states the engine's message and nothing about the part. |
| Never filter, reword or hide a calc warning in `app.js` | test | Enforced by absence: `showMessages` is not in the diff, and the error text goes in `.reason`, not `#messages`. |
| Add no `GearParams` field; move no default, bound or type | test | Enforced: 31 fields, `params.py` unchanged since UAT. |
| Declare no relation `calc` does not back | test | Enforced, now by two independent checks. |
| Change no `calc`/`model`/`pool`/`app.py`/CLI; both regression files byte-identical | test | Enforced: empty diff since `c065d6d`. |
| No regeneration of regression files; never dim a gate field; dim follows fields, not the server | test | Enforced: unchanged by the fixes. |
| Do not delete, loosen or allow-list an `app.js` pin | judgment | `unverified-prohibition: human review recommended` (non-authoritative LLM reading). Resolved by the person in the UAT on the pre-fix tree, and I re-checked the fact it relied on against the current tree: since `c065d6d`, `test_api.py` deletes exactly two lines (a docstring clause and one token, replaced by a longer one); `59deb6e` only adds cases to a guard that is a superset for writes. No pin loosened. |
| Do not drop, add or alter a D-09 row | judgment | Same flag and status. The schema dump shows the 11 rows, equal to L41's list. |
| Move no wait, timeout or bar toward a pass | judgment | Same flag and status. The only timeout expressions in the `tests/` diff are uses of the existing `BUILD_WAIT_MS`; the new step uses it too and defines nothing. |

### Anti-Patterns Found

None blocking. `TBD`/`FIXME`/`XXX` grep over every covered source and test file: no matches; `make no-fake-done` exits 0. The ten open review items are all `info`. Of those, IN-09 (decision-log wording) is covered above, and IN-08 and IN-10 (test strength) are in the advisory list. IN-01..IN-07 are unchanged from the prior round.

## Human Verification: does the UAT still apply?

`23-UAT.md` (2/2 passed) covered (1) the visual read of the dim in light and dark and of the refused keyway pair, and (2) the three judgment-tier prohibitions. Its verdict **still applies**, with no need for a human to look again:

1. The visual. The fixes changed no CSS (`style.css` last changed in `e09f834`, before the UAT) and the success path of `applyRelations()` is the same statements in the same order, so every pixel the person judged is produced by the same code and rules.
2. The judgment-tier prohibitions. I re-derived the facts they rest on from the current tree, as above. Nothing was loosened, dropped or moved.

One thing the UAT never saw: the new `Cannot tell whether this field is used: …` row. It is reachable only with a schema whose op the page does not know (a stale cached `app.js` against a newer server), is styled by the existing `.field .reason` rule, and has a browser test for its text and effect. If you want a person to look at its appearance, load the app with a tampered schema. I count this as optional and not a gate, because no must-have or success criterion depends on how it looks.

Human verification items outstanding: none.

### Gaps Summary

No gaps. The goal holds on the current tree: the relation is model metadata (11 declarations, 31 fields, schema dumped), `calc` backs each (and the cutout drivers are now proved by name, which I confirmed by breaking one), generic `app.js` renders it dimmed-and-editable in a real browser, and the query path (`gearQuery()`, `DIMS`, the 44 golden queries, both regression files) is untouched. The WR-01 fix keeps an unreadable relation from freezing the form, proved red-to-green against the old `app.js`. The remaining open items are documentation (IN-09: add a sentence to L41) and test-strength follow-ups (IN-08, IN-10), none of them a must-have failure.

---

_Verified: 2026-10-11T16:31:04Z_
_Verifier: Claude (gsd-verifier)_
