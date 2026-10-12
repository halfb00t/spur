---
phase: "24"
slug: "bore-shape-selector"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-12"
---

# Phase 24 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + xdist + cov; Playwright 1.63.0 with Chrome Headless Shell for `tests/test_browser.py` |
| **Config file** | `pyproject.toml` (`filterwarnings = ["error", ...]`, `fail_under = 96`, mypy `strict` + `disallow_any_explicit` over `tests/`) |
| **Quick run command** | `make verify.fast` (static steps + the commit slice, `tests/test_selector.py` included from 24-02) |
| **Full suite command** | `make verify` |
| **Estimated runtime** | ~17 s quick (`896 passed`, 16.16 s real at `87462cb`, 24-RESEARCH); ~300 s full (Phase 23's reading); the browser file alone ~15-25 s |

Targeted commands (each proven in Phase 23 or measured in 24-RESEARCH; run through `make`, which exports `PLAYWRIGHT_BROWSERS_PATH`):

- API pins: `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'schema_drives_the_form or openapi_documents or every_key_the_ui_reads or shareable_link_round_trips or root_shape_link'"` (`5 passed`)
- Selector proofs: `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"` (`16 passed`)
- Browser: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (`2 passed`, the `step bore shape:` line)
- Browser pins: `make test.fast PYTEST_ARGS="tests/test_browser_pins.py -n0 -q"`
- Golden pin byte identity: `make golden.regen` then `git diff --exit-code tests/regression/golden_requests.json tests/regression/pre_v0_2.json`

---

## Sampling Rate

- **After every task commit:** `make verify.fast` (the pre-commit hook) plus the task's targeted command, plus `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json` after every task (D-17)
- **After every plan wave:** `make verify`, its log kept as `investigation/24-NN-verify.log` ending `make verify exit 0` (each plan runs it before its last commit; the waves are sequential, PD-01)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds for a targeted command (the browser file is the slowest, ~15-25 s); `make verify` ~300 s once per plan

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 24-01-01 | 01 | 1 | REQ-selector-schema-carried, REQ-selector-derives-and-writes-through | T-24-01, T-24-02, T-24-06 | schema strings reach the DOM through `textContent`/`new Option` only; the select has no `name` and no `fields` entry; `/openapi.json` carries no `selectors` while `/api/schema` does (pinned in `test_openapi_documents_the_typed_contracts`); the regression files do not move | integration + static + e2e | the API-pins command (`5 passed`; its red `3 failed, 2 passed` in `24-01-api-red.log`); the one-off grid's summary line grepped in `24-01-grid-oneoff.log`; the browser command into `24-01-browser-green.log`; the `params.py` AST pin and the `app.js` region pin of the plan | ✅ (edits) | ⬜ pending |
| 24-01-02 | 01 | 1 | REQ-selector-derives-and-writes-through | T-24-03, T-24-04 | a pick writes only its option's own false conditions (`0` or a stashed string); a pending pick writes and sends nothing; an unreadable option or a negative value never skips `update()`; two holding options load a blank select (the twin selector) | e2e | the browser command into `24-01-browser-picks.log`; four red logs (`stop`, `restore`, `catch`, `twin`) | ✅ (edits) | ⬜ pending |
| 24-01-03 | 01 | 1 | REQ-selector-schema-carried | T-24-06 | L42 and the pins in one commit; nothing in `calc`/`model`/`pool`/`app.py`/`cli` moves | docs + gate | `make verify` into `24-01-verify.log`; the L42 token check and the one-commit file-set check | ✅ (edits) | ⬜ pending |
| 24-02-01 | 02 | 2 | REQ-selector-round-trips-per-state, REQ-selector-schema-carried | T-24-07 | exactly one option per valid triple; each label falls in its `derive()` class; the walk refuses malformed options | unit (kernel-free) | `make test.fast PYTEST_ARGS="tests/test_selector.py -n0 -q"` (`16 passed`); the import/AST check | ❌ W0 (created by this task) | ⬜ pending |
| 24-02-02 | 02 | 2 | REQ-selector-round-trips-per-state | T-24-08 | three wrong options on the real model go red and `params.py` is restored byte for byte | unit + git | three `24-02-*-red.log`; `git diff --exit-code -- src/spur/params.py`; `make verify` into `24-02-verify.log` | ✅ | ⬜ pending |
| 24-03-01 | 03 | 3 | REQ-selector-derives-and-writes-through, REQ-selector-round-trips-per-state | T-24-09, T-24-10 | no `/api/*` request on any of the seven pages and no hash carries a key `GearParams` lacks; the 44 golden queries and the regenerated pin are byte-identical | e2e + git | the browser command into `24-03-browser-sweep.log`; `make golden.regen` + `git diff --exit-code`; the seven-pages/fourteen-steps count; `24-03-readhash-red.log` | ✅ (edits) | ⬜ pending |
| 24-03-02 | 03 | 3 | REQ-selector-derives-and-writes-through | T-24-03 | every pick from every state matches the mirror; the stash survives hash navigations; over a keyed bore the keyway pair is left to the server's 422 | e2e + docs + gate | the browser command into `24-03-browser-picks.log`; `24-03-reset-red.log`; the idea/debt file checks; `make verify` into `24-03-verify.log` | ✅ (edits) | ⬜ pending |
| 24-04-01 | 04 | 4 | REQ-selector-derives-and-writes-through | T-24-11 | three browser and three slice readings on the committed tree, each under its limit | bench | the browser command ×3 into `24-04-reading-N.log`; `make verify.fast` ×3 into `24-04-slice-N.log`; the parser of the plan | ✅ | ⬜ pending |
| 24-04-02 | 04 | 4 | REQ-selector-round-trips-per-state | T-24-11, T-24-12 | every recorded figure equals its log; no `src/` or `tests/` file in the commit | docs + gate | the `bench/RESULTS.md` parser; `make verify` into `24-04-verify.log`; the commit file-set check | ✅ (edits) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements: pytest, xdist, Playwright 1.63.0 and the headless shell are
installed (`make test` fetches the shell through the `$(BROWSER)` stamp); no package is added. The one new test file,
`tests/test_selector.py`, is written by the task that first runs it (24-02 Task 1); every other proof extends an
existing file (`tests/test_api.py`, `tests/browser_session.py`, `tests/test_browser.py`). No task's `<verify>` is
`MISSING`.

- [x] `tests/test_selector.py` — created in 24-02 Task 1 (kernel-free, commit slice), for REQ-selector-round-trips-per-state and REQ-selector-schema-carried
- [x] Framework install — none needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The selector row and the pending state read well in both themes (the dashed tone, the reason row, the focus ring) | REQ-selector-derives-and-writes-through | the browser step proves the rules exist (computed `borderTopStyle` dashed while pending, the reason text, the focus), not that they read well (23-VALIDATION's same judgement row) | open `/`, pick Hex: check the select and `Hex bore A/F` in light and dark; type `6` and check the dim on `Bore Ø` and `D-flat`; pick Round and check the hash reads `#bore_flat=0` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (nine tasks, each with at least one command and its `<fails_when>`)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none)
- [x] No watch-mode flags
- [x] Feedback latency < 60s for targeted commands
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending (status stays `draft` until `/gsd-validate-phase` sets it)
