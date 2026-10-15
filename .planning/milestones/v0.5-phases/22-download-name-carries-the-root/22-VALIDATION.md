---
phase: "22"
slug: "download-name-carries-the-root"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-11"
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0; Playwright 1.63.0 (Chrome Headless Shell) for `tests/test_browser.py` |
| **Config file** | `pyproject.toml` (`filterwarnings = ["error", ...]`, `fail_under = 96`, mypy `strict` with `possibly-undefined`) |
| **Quick run command** | `make verify.fast` (static steps + the commit slice; runs `tests/test_trochoid.py`, not the five heavy files) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest `-n 8` with coverage; includes `tests/test_api.py` and `tests/test_browser.py`) |
| **Estimated runtime** | quick ~11-20 s; full ~190-240 s on this host; the browser file alone ~4-10 s at `-n0` |

---

## Sampling Rate

- **After every task:** the task's targeted runs (`make test PYTEST_ARGS="... -n0 --no-cov -q -k ..."`, `make test.fast PYTEST_ARGS="..."`); 22-01 makes one commit at Task 3 (D-11), and the pre-commit hook runs `make verify.fast` on it
- **After every plan wave:** `make verify` (22-01 Task 3 before its commit; 22-02 Task 2 before its commit), log kept under `investigation/` ending `make verify exit N`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~60 s for a targeted run (the browser file builds one or two parts); ~240 s for the full gate

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 22-01-01 | 01 | 1 | REQ-slug-carries-effective-root | T-22-01, T-22-02 | the filename is built only from validated fields and the literal `_trochoid` chosen by `root_mode`; whole-header equality pins | integration (`TestClient`) | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k 'download_name or root_shape_link or test_model_download'"` (7 passed) | ✅ file; tests written first in-task | ✅ green |
| 22-01-01 | 01 | 1 | REQ-slug-carries-effective-root | T-22-02 | the browser saves the server's name, `spur_z23_m1.75_pa25_trochoid.stl` | e2e (uvicorn + headless shell) | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (1 passed, `step download name:` printed) | ✅ file; step written first in-task | ✅ green |
| 22-01-01 | 01 | 1 | REQ-slug-carries-effective-root | T-22-03 | `slug()` calls the predicate with no guard and no helper; D-03 files and both fixtures unedited | static (AST + git) | `make lint typecheck` + the slug AST check + `git diff --exit-code` on app/records/model/cli/pool/app.js and the two fixtures + calc.py docstring-only AST check | ✅ | ✅ green |
| 22-01-02 | 01 | 1 | REQ-slug-carries-effective-root | T-22-02, T-22-03 | `slug()` total on refused and ignored requests; ignored rows red under the requested-root rule | unit (no kernel) | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -n0 -q -k download_name_follows"` (6 passed) | ✅ file; rows written in-task | ✅ green |
| 22-01-02 | 01 | 1 | REQ-slug-carries-effective-root | T-22-03 | the `build.failed` record carries the would-be name | integration (caplog) | `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q -k failed_build_records_the_name"` (2 passed) | ✅ file; rows written in-task | ✅ green |
| 22-01-02 | 01 | 1 | REQ-slug-carries-effective-root | T-22-03 | no valid request makes `slug()` raise; name agrees with the predicate | one-off sweep | the `sweep_cases()` command in 22-01 Task 2 verify (17567 valid, 9954 `_trochoid`, none raised) | ✅ | ✅ green |
| 22-01-03 | 01 | 1 | REQ-slug-consumers-read-first | T-22-04, T-22-05 | L40 lists every consumer at the parent sha and the cache keys; idea retired; one commit; fixtures unchanged | doc + git | the three Python/git checks in 22-01 Task 3 verify; `investigation/22-01-verify.log` ends `make verify exit 0` | n/a | ✅ green |
| 22-02-01 | 02 | 2 | REQ-slug-carries-effective-root | T-22-06, T-22-07 | three readings on the committed tree, each under 15 s | measurement | the log-parsing check in 22-02 Task 1 verify | n/a | ✅ green |
| 22-02-02 | 02 | 2 | REQ-slug-carries-effective-root | T-22-06, T-22-07 | readings equal their logs; `BUILD_WAIT_MS` unmoved, comment-only change; gate green | doc + git + full gate | the two checks in 22-02 Task 2 verify; `investigation/22-02-verify.log` ends `make verify exit 0` | n/a | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements: `tests/test_api.py`, `tests/test_trochoid.py` and
`tests/test_browser.py` exist, and each new test function is written by its own task before the code it pins moves
(22-01 PLAN, PD-10), so no task verifies against a test that does not exist yet. The headless shell installs through
`make test`'s `$(BROWSER)` stamp (about 20 s the first time; absent on this host at research time). No new framework,
config or fixture file.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
All phase behaviors have automated verification. Not automated here, by design: the step's reading on
`ubuntu-latest` (RESEARCH assumptions A2, A3), read from the pull request's first CI run when the human pushes.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 240s (the full gate; targeted runs under 60 s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-11 — every behavior green under `make verify` on `3b71355` (1238 passed, 97.92% coverage)

## Validation Audit 2026-10-11

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
