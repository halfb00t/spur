---
phase: "23"
slug: "conditional-form-fields"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-11"
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-xdist + pytest-cov; Playwright 1.63.0 (Chrome Headless Shell) for `tests/test_browser.py` |
| **Config file** | `pyproject.toml` (`filterwarnings = ["error", ...]`, `fail_under = 96`, mypy `strict` with `disallow_any_explicit` over `tests/`) |
| **Quick run command** | `make verify.fast` (static steps + the commit slice, which includes the new `tests/test_relations.py`; not the five heavy files) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest `-n 8` with coverage; includes `tests/test_api.py`, `tests/test_cli.py`, `tests/test_browser.py`) |
| **Estimated runtime** | quick ~18 s (RESEARCH: 17.9 s wall, budget 30 s, L36); full ~190-240 s on this host; the browser file alone ~7-10 s at `-n0` |

---

## Sampling Rate

- **After every task:** the task's targeted runs -- `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k ..."`, `make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q"`, `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` into a kept log -- plus `git diff --exit-code` on `tests/regression/pre_v0_2.json` and `tests/regression/golden_requests.json`; every commit runs `make verify.fast` through the pre-commit hook
- **After every plan wave:** `make verify`, its log kept under `investigation/` ending `make verify exit N` (23-01 Task 2, 23-02 Task 2, 23-03 Task 2, 23-04 Task 2)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 s for a targeted run (the browser file builds one part); ~240 s for the full gate

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 23-01-01 | 01 | 1 | REQ-enabled-when-metadata, REQ-form-walk-proves-relations | T-23-01, T-23-04, T-23-05 | `app.js` pins tightened (new `fields.set` token, call sites, effective value, no disabled/hidden/markup write); `hub_d`'s relation emitted unchanged; `gearQuery()` untouched | static + integration (`TestClient`) | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'schema_drives_the_form or openapi_documents or every_key_the_ui_reads or shareable_link_round_trips or root_shape_link'"` (5 passed); the params.py AST check; the app.js region check | ✅ file; pins written first in-task | ⬜ pending |
| 23-01-01 | 01 | 1 | REQ-dim-and-editable | T-23-02, T-23-03 | `#spoke_count=0&hub_d=40` loads `hub_d` dimmed with its reason, editable, sent; input re-evaluates before the debounce; Reset restores the evaluator's set | e2e (uvicorn + headless shell) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` into `investigation/23-01-browser-green.log` (1 passed, `inert fields: hub_d: Needs Spoke arms above 0`) | ✅ file; step written first in-task | ⬜ pending |
| 23-01-02 | 01 | 1 | REQ-dim-and-editable, REQ-form-walk-proves-relations | T-23-03, T-23-05 | the visible dim never uses opacity/pointer-events/visibility; L41 last decision; one commit of ten files; regression files unmoved | e2e + doc + git | the styled browser log + CSS check; the L41 citation check; the commit file-set check; `investigation/23-01-verify.log` ends `make verify exit 0` | n/a | ⬜ pending |
| 23-02-01 | 02 | 2 | REQ-relations-calc-backed, REQ-enabled-when-metadata | T-23-06, T-23-08 | the proof module goes red exactly where the set is incomplete | unit (kernel-free) | `make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q -rf"` expected `3 failed, 7 passed`; the import AST check | ❌ W0 -- created by this task (TDD red) | ⬜ pending |
| 23-02-02 | 02 | 2 | REQ-relations-calc-backed, REQ-form-walk-proves-relations | T-23-06, T-23-07 | all eleven D-09 rows declared and proved; walk covers every relation; a wrong relation seen red | unit + integration + e2e | `make test.fast PYTEST_ARGS="tests/test_relations.py -n0 -q"` (10 passed); the D-09 set check; `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -n0 --no-cov -q -k '...'"` (4 passed); the browser log; `investigation/23-02-verify.log` ends `make verify exit 0` | ✅ (after 23-02-01) | ⬜ pending |
| 23-02-03 | 02 | 2 | REQ-relations-calc-backed | T-23-06 | the two left-out items filed with INDEX rows | doc + git | the ledger and commit check in Task 3 verify | n/a | ⬜ pending |
| 23-03-01 | 03 | 3 | REQ-form-walk-proves-relations | T-23-09, T-23-10 | each of 44 golden links: query == pin and dimmed set == evaluator; regen byte-identical; readHash call seen red | e2e + regen proof | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`; `make golden.regen` then `git diff --exit-code tests/regression/golden_requests.json`; `make test.fast PYTEST_ARGS="tests/test_browser_pins.py -n0 -q"` | ✅ | ⬜ pending |
| 23-03-02 | 03 | 3 | REQ-dim-and-editable, REQ-form-walk-proves-relations | T-23-10 | four schema-derived flips, the refused pair (`.invalid` + `.inactive`, gate never dimmed), Reset; dim visible; #reset call seen red; idea retired | e2e + doc + git | the flips log check (four flips, one per gate, at least one 422); the retirement and commit check; `investigation/23-03-verify.log` ends `make verify exit 0` | ✅ | ⬜ pending |
| 23-04-01 | 04 | 4 | REQ-form-walk-proves-relations | T-23-11 | three browser and three commit-slice readings on the committed tree, `inert fields` < 15 s, slice < 25 s | measurement | the log-parsing check in 23-04 Task 1 verify | n/a | ⬜ pending |
| 23-04-02 | 04 | 4 | REQ-form-walk-proves-relations | T-23-11, T-23-12 | readings equal their logs; every red recorded; logs committed; no source or test file in the commit | doc + git + full gate | the two checks in 23-04 Task 2 verify; `investigation/23-04-verify.log` ends `make verify exit 0` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_relations.py` — created by 23-02 Task 1 (TDD red, `3 failed, 7 passed` against the one-relation model) before 23-02 Task 2 declares the other ten relations; covers SC1 (walk, keyword collision, one-path, `Literal` probe) and SC2 (forward parity with warning names, the refused pair, reverse coverage, three meta-red tests)
- Everything else extends existing files: `tests/test_api.py`, `tests/test_cli.py`, `tests/browser_session.py`, `tests/test_browser.py`, `tests/capture_requests.py`. No new framework, config or fixture file; no package installed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
*None: all phase behaviors have automated verification. Two `backstop` truths (schema concurrency in 23-02, the browser test's single-server sequencing in 23-03) rest on structure rather than a test and abstain to `human_needed` if the verifier cannot confirm them.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < {N}s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** {pending / approved YYYY-MM-DD}
