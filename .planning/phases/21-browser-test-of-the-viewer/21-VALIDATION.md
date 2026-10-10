---
phase: "21"
slug: "browser-test-of-the-viewer"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-10"
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov (`[dev]`); `playwright==1.63.0` (sync API, the default Chrome Headless Shell on SwiftShader) added by 21-01 after the legitimacy checkpoint; no `pytest-playwright` (D-03) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`: `filterwarnings = error`, `--strict-markers --strict-config`; `[tool.coverage.*]` floor 96; `[tool.mypy]` strict, `disallow_any_explicit`); `Makefile` (`$(BROWSER)` stamp, `PLAYWRIGHT_BROWSERS_PATH` under `.venv`) |
| **Quick run command** | 21-01 to 21-05 (staging name, PD-01/PD-09): `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"` (the first time after the pin: `make .venv/.browser` first). From 21-06's admission commit: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"`. Light pins: `.venv/bin/python -m pytest tests/test_browser_pins.py tests/test_hooks.py -n0 --no-cov -q` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, the unfinished-work scan, pytest `-n 8 --cov`; from 21-06 it includes `tests/test_browser.py`). The commit hook runs `make verify.fast` (L36, under 30 s), which never collects the browser test |
| **Estimated runtime** | Quick run: ~5-10 s (research prototype 4.4-6.9 s `-n0` at load 7-8; 21-01 records the real figure). `make verify.fast`: ~12 s on this host (19-09: 11.39-11.54 s). `make verify`: ~193 s on this host (19-09 mean 192.94 s) plus the browser test's A/B delta (21-07 measures it) |

---

## Sampling Rate

- **After every task commit:** the commit hook's `make verify.fast` (under 30 s, L36), plus the task's quick run above
- **After every plan wave:** `make verify` (each plan's last task carries it, or `make lint typecheck` plus the quick run where the plan ends on a record-only task)
- **Before `/gsd-verify-work`:** `make verify` green on the closing commit (21-08 Task 3) and a green `test (3.12)` run on a real `ubuntu-latest` runner (21-08 Task 2, SC5)
- **Max feedback latency:** quick run ~10 s; `make verify.fast` under 30 s (the SDK kills the hook at 30 s)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | REQ-browser-stack-pinned | T-21-SC | `playwright`, `pyee`, `greenlet` confirmed by a human before any install (blocking-human) | manual + guard | `git diff --exit-code -- pyproject.toml Makefile` and `find_spec('playwright') is None` (nothing installed before the answer) | ✅ | ⬜ pending |
| 21-01-02 | 01 | 1 | REQ-browser-server-fixture, REQ-browser-first-build-drawn, REQ-browser-fails-closed, REQ-browser-stack-pinned | T-21-01..07 | socket on 127.0.0.1 only; process group killed with no survivor; `SPUR_*` scrubbed; shell under `.venv` only; host cache unchanged | e2e (tracer) | `make .venv/.browser && make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; `make lint typecheck`; `make verify` | ❌ W0 (created by this task) | ⬜ pending |
| 21-01-03 | 01 | 1 | REQ-browser-first-build-drawn, REQ-browser-fails-closed, REQ-browser-server-fixture | T-21-02, T-21-06 | each assertion seen red once; every break reverted | e2e + record | `git diff --exit-code -- src/spur/static/app.js tests/browser_session.py tests/browser_scenarios.py && make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; the `bench/RESULTS.md` record check | ✅ | ⬜ pending |
| 21-02-01 | 02 | 2 | REQ-browser-stack-pinned | T-21-08 | the spike branch exists and is never an ancestor of the phase branch | git guard | `git rev-parse --verify -q spike/21-linux-runner && ! git merge-base --is-ancestor spike/21-linux-runner HEAD ...`; the spike branch's Makefile/ci.yml/test_hooks greps | ✅ | ⬜ pending |
| 21-02-02 | 02 | 2 | REQ-browser-stack-pinned | T-21-08 | the human pushes; the agent never does | manual | `gh run list --branch spike/21-linux-runner --workflow ci --limit 1 ...` | ✅ | ⬜ pending |
| 21-02-03 | 02 | 2 | REQ-browser-stack-pinned, REQ-browser-first-build-drawn, REQ-browser-server-fixture | T-21-09 | `--with-deps` (sudo apt) on CI only; bar and wait set from both hosts | e2e + record | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; the `### Linux runner spike (21-02)` check; `! git merge-base --is-ancestor spike/21-linux-runner HEAD` | ✅ | ⬜ pending |
| 21-03-01 | 03 | 3 | REQ-browser-form-from-schema, REQ-browser-invalid-field-marked | T-21-10, T-21-11 | expectations read from the server; content waits only; breaks reverted | e2e | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; `git diff --exit-code -- src/spur/static/app.js src/spur/static/style.css`; `make lint typecheck` | ✅ | ⬜ pending |
| 21-03-02 | 03 | 3 | REQ-browser-warning-rendered | T-21-10, T-21-11 | warnings equal `/api/info`'s for the query the page sent | e2e | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; `make verify` | ✅ | ⬜ pending |
| 21-04-01 | 04 | 4 | REQ-browser-link-round-trip | T-21-13 | fragment asserted to differ before each assignment; request-URL waits | e2e | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k round_trips"`; `make lint typecheck` | ✅ | ⬜ pending |
| 21-04-02 | 04 | 4 | REQ-browser-link-round-trip | T-21-12 | `#root_shape=bogus` pinned as today, filed as `must` debt, not fixed | e2e + ledger | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; the debt-file and INDEX greps; `make verify` | ✅ | ⬜ pending |
| 21-05-01 | 05 | 5 | REQ-browser-golden-request-sets | T-21-14, T-21-15 | only `make golden.regen` writes the pin; a regen on unchanged code is byte-identical; `pre_v0_2.json` read only | regen + pin | `make golden.regen && git diff --exit-code tests/regression/golden_requests.json`; the JSON shape check; `make help \| grep -q '^golden.regen'` | ❌ W0 (`tests/capture_requests.py`, `tests/regression/golden_requests.json` created by this task) | ⬜ pending |
| 21-05-02 | 05 | 5 | REQ-browser-golden-request-sets | T-21-14 | the test reads the pin, never writes it | e2e | `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`; `make verify` | ✅ | ⬜ pending |
| 21-06-01 | 06 | 6 | REQ-browser-fails-closed, REQ-browser-stack-pinned | T-21-16 | no skip path, exact dev-only pin, no plugin, no `channel=` | unit (AST/toml pins) | `.venv/bin/python -m pytest tests/test_browser_pins.py -n0 --no-cov -q -p no:cacheprovider`; `make verify.fast` | ❌ W0 (`tests/test_browser_pins.py` created by this task) | ⬜ pending |
| 21-06-02 | 06 | 6 | REQ-browser-in-the-gate, REQ-browser-server-fixture | T-21-17, T-21-18, T-21-19 | excluded from the commit slice and the image by name; admission in one commit | unit (make dry runs) + gate | `make test PYTEST_ARGS="tests/test_hooks.py tests/test_browser_pins.py -n0 --no-cov -q"`; the one-commit `git log` check; `make verify` | ✅ (`tests/test_hooks.py` extended) | ⬜ pending |
| 21-06-03 | 06 | 6 | REQ-browser-in-the-gate, REQ-browser-fails-closed | T-21-17 | `make verify.fast` under 30 s three times; ten `-n 8` passes; missing shell fails closed at the final path | measurement | the `### Admission (21-06)` check; `test "$(make -n test \| grep -c 'playwright install')" = 0` | ✅ | ⬜ pending |
| 21-07-01 | 07 | 7 | REQ-browser-in-the-gate | T-21-20, T-21-21 | every red run kept and classified; bars quoted with their host | measurement | the `### The browser test, priced (21-07)` check; the A1/B3 logs exist | ✅ | ⬜ pending |
| 21-07-02 | 07 | 7 | REQ-browser-in-the-gate | T-21-20 | the human decides the price (blocking-human, no auto_select) | manual | the answer-recorded check | ✅ | ⬜ pending |
| 21-08-01 | 08 | 8 | REQ-browser-in-the-gate, REQ-browser-stack-pinned | T-21-22 | the human pushes and opens the PR | manual | a CI run exists whose `headSha` is `HEAD` | ✅ | ⬜ pending |
| 21-08-02 | 08 | 8 | REQ-browser-stack-pinned | T-21-22, T-21-23 | SC5 from the phase branch's own run; the spike never merged | CI evidence | the `### The Linux path on the real runner (21-08)` check; the kept log and the spike-unmerged check | ✅ | ⬜ pending |
| 21-08-03 | 08 | 8 | REQ-browser-in-the-gate | T-21-24 | L39 cites recorded figures only; the idea retired in the same commit | docs + gate | the L39 citation check; the retirement and one-commit check; `make verify` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Created inside the plans that first need them (each by the task that runs it first), not as stubs ahead of time:

- [ ] `playwright==1.63.0` in `pyproject.toml` `[dev]`, only after the 21-01 Task 1 legitimacy checkpoint is answered; `make .venv/.browser` installs the shell under `.venv/ms-playwright` (21-01 Task 2)
- [ ] `Makefile` `BROWSER`, `BROWSER_INSTALL_ARGS`, the exported `PLAYWRIGHT_BROWSERS_PATH` and the `$(BROWSER): $(STAMP)` stamp (21-01 Task 2; becomes `test`'s prerequisite in 21-06 Task 2)
- [ ] `tests/browser_session.py` (non-collected helper) and `tests/browser_scenarios.py` (staging name, renamed `tests/test_browser.py` in 21-06 Task 2) — 21-01 Task 2
- [ ] `tests/capture_requests.py` and `tests/regression/golden_requests.json` — 21-05 Task 1
- [ ] `tests/test_browser_pins.py` — 21-06 Task 1
- [ ] `tests/test_hooks.py` edits (`HEAVY_TEST_FILES`, `BROWSER_STAMP`, `-o` in `_dry_run`, two new tests) — 21-06 Task 2

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `playwright`, `pyee`, `greenlet` are the real packages before the pin lands | REQ-browser-stack-pinned | package legitimacy is a human trust decision (rated SUS by the audit); never auto-approved | 21-01 Task 1: compare the pip index, dry-run report and PyPI JSON readings with pypi.org; answer approved or stop |
| The spike branch reaches a real `ubuntu-latest` runner | REQ-browser-stack-pinned | pushing and opening PRs are the human's (CLAUDE.md) | 21-02 Task 2: push `spike/21-linux-runner`, open a draft "DO NOT MERGE" PR |
| The browser test's measured price is accepted or its placement reopened | REQ-browser-in-the-gate | D-01 puts the price in front of the human before the phase closes | 21-07 Task 2: read `### The browser test, priced (21-07)` and answer `accept` or `reopen` |
| The phase branch's suite runs green on a real `ubuntu-latest` runner (SC5) | REQ-browser-stack-pinned, REQ-browser-in-the-gate | needs the human's push and PR | 21-08 Task 1: push the phase branch and open or update its PR; 21-08 Task 2 reads the run |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
