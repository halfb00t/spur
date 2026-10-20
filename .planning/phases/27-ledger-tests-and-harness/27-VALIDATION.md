---
phase: "27"
slug: "ledger-tests-and-harness"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-20"
---

# Phase 27 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `27-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1, pytest-xdist 3.8.0 (`-n 8`), `filterwarnings = ["error", ...]`, `--strict-markers --strict-config` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `make verify.fast` |
| **Full suite command** | `make verify` |
| **Targeted** | `.venv/bin/python -m pytest <file> -k <expr> -n0 --no-cov -q` |
| **Estimated runtime** | quick ~10 s (922 passed, 10.40 s wall, 2026-10-20); full ~190 s (1321 passed in 187.05 s, Phase 26) |

---

## Sampling Rate

- **After every task commit:** Run `make verify.fast` (pre-commit runs it; must stay under L36's 30 s)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green, result line recorded; `git diff --exit-code v0.5 -- tests/regression/` empty; `git diff --numstat v0.5 -- bench/RESULTS.md` deleted column 0
- **Max feedback latency:** 30 seconds

---

## Per-Requirement Verification Map

Task IDs are filled when plans exist.

| Requirement | Behavior | Test Type | Automated Command | Fails when | File Exists | Status |
|-------------|----------|-----------|-------------------|------------|-------------|--------|
| REQ-slug-totality-guarded | `slug()` total; `_trochoid` suffix == `root_mode`; every bucket non-empty; forced rows labelled | unit (commit slice) | `.venv/bin/python -m pytest tests/test_trochoid.py -k "slug_is_total" -n0 --no-cov` | non-zero exit, or `0 passed`/`deselected` only | ❌ W0 | ⬜ pending |
| REQ-slug-totality-guarded (red) | raising `_junction`, raising `_root_curve` | temporary mutation | same command with a temporary `raise RuntimeError` | `1 failed` absent from either mutated run | n/a | ⬜ pending |
| REQ-failed-build-name-isolated | 422 under a pre-seeded `_EXPORTS` | HTTP | `.venv/bin/python -m pytest tests/test_api.py -k "records_the_name" -n0 --no-cov` | non-zero exit | ✅ edit | ⬜ pending |
| REQ-failed-build-name-isolated (red) | old shape + pre-seed reads 200 | temporary pre-seed | same command, old code | no `assert 200 == 422` in the output | n/a | ⬜ pending |
| REQ-stop-group-signals-first | signal before any read; failed `ps` = survivors unknown | unit (commit slice, sub-second) | `.venv/bin/python -m pytest tests/test_process_group.py -n0 --no-cov --durations=3` | non-zero exit, or any duration ≥ 1 s | ❌ W0 | ⬜ pending |
| REQ-stop-group-signals-first (red) | old order | new test vs old `stop_group` | same command, old code | anything other than `2 failed` | n/a | ⬜ pending |
| REQ-stop-group-signals-first (kept) | leader-only break still red | temporary `os.kill` for `os.killpg` + browser test | `make test PYTEST_ARGS="tests/test_browser.py --no-cov -q"` | `still has live pids` absent from output | ✅ | ⬜ pending |
| REQ-group-floor-recorded-true | comment + two dated corrections | grep/diff | `git diff --numstat v0.5 -- bench/RESULTS.md`; `grep -n "resource_tracker" tests/browser_session.py` | deleted column ≠ 0, or grep empty, or `MIN_GROUP_MEMBERS = 3` changed | ✅ | ⬜ pending |
| REQ-launch-message-true | install command named; literal `playwright install --only-shell chromium` kept | AST pin | `.venv/bin/python -m pytest tests/test_browser_pins.py -n0 --no-cov` | non-zero exit | ✅ extend | ⬜ pending |
| 19 IN-01 (D-03) | part unchanged | regression + chamfer | `git diff --exit-code v0.5 -- tests/regression/` and `.venv/bin/python -m pytest tests/regression tests/test_model.py -k "chamfer or regression" -n0 --no-cov` | non-zero exit from either | ✅ | ⬜ pending |
| 23 IN-08 | `honeycomb (4)` makes `eq 0.05` raise | unit | `.venv/bin/python -m pytest tests/test_relations.py -n0 --no-cov` | non-zero exit | ✅ edit | ⬜ pending |
| 23 IN-11, 21 IN-02 | `_js_number` range and `-0.0` | unit | `.venv/bin/python -m pytest tests/test_browser.py -k "oracle_reads" -n0 --no-cov` | non-zero exit | ✅ edit | ⬜ pending |
| `_host_state` | no git → `unknown` | unit | `.venv/bin/python -m pytest tests/test_bench.py -k host_state -n0 --no-cov` | non-zero exit, or `0 selected` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_process_group.py` (+ the extracted module, if chosen) — REQ-stop-group-signals-first
- [ ] slug totality test in `tests/test_trochoid.py` — REQ-slug-totality-guarded
- [ ] fresh-`_BlobCache` fixture in `tests/test_api.py` — REQ-failed-build-name-isolated
- [ ] `_host_state` test in `tests/test_bench.py`

Framework install: none.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Linux `ps` member listing | REQ-group-floor-recorded-true | needs a CI runner; push is a human step (D-05, 26-02 precedent) | human pushes the throwaway branch, opens a DO-NOT-MERGE draft PR; executor reads the whole log; PR closed unmerged |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
