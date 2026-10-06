---
phase: "17"
slug: "debt-first-commit-gate-and-pool-race"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-06"
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `17-RESEARCH.md` § Validation Architecture; the per-task map is filled from the plans.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist (`-n 8`, clamped to the host) + pytest-cov; `filterwarnings = ["error", ...]`, `--strict-markers --strict-config` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; coverage floor `fail_under = 96` |
| **Quick run command** | `make test PYTEST_ARGS="<paths or -k> -q --no-cov"` (PYTEST_ARGS comes last, so `--no-cov` wins) |
| **Full suite command** | `make verify` (~64 s warm on the dev host; the phase gate) |
| **Estimated runtime** | ~64 seconds (full); ~12.6 s for the commit-time subset `make verify.fast` once this phase ships it |

---

## Sampling Rate

- **After every task commit:** Run the command named in that task's row (heavy test files explicitly — after the hook decision the commit hook no longer runs `test_pool.py`, `test_model.py`, `test_api.py`, `test_cli.py`)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 64 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled from PLAN.md tasks by validate-phase) | — | — | REQ-hook-and-commit-timeout-decided | T-17-xx / — | N/A | structural | `make -n verify` — static recipes precede the single `pytest` line; no second pytest line | ✅ | ⬜ pending |
| (filled from PLAN.md tasks) | — | — | REQ-hook-and-commit-timeout-decided | — | N/A | live | `time gsd_run query commit "<msg>" --files <one .planning file>` — `committed: true`, hash in `git log -1`, wall < 30 s | ✅ | ⬜ pending |
| (filled from PLAN.md tasks) | — | — | REQ-same-slot-timeout-race-reproduced | — | N/A | unit | `make test PYTEST_ARGS="tests/test_bench.py -q --no-cov"` | ✅ (edit) | ⬜ pending |
| (filled from PLAN.md tasks) | — | — | REQ-same-slot-timeout-race-fixed | T-17-xx / — | documented `503 timeout` body, never an unhandled `AttributeError` | unit (deterministic) | `make test PYTEST_ARGS="tests/test_pool.py -k stale_executor -q --no-cov"` — red before the fix, green after | ❌ W0 | ⬜ pending |
| (filled from PLAN.md tasks) | — | — | REQ-same-slot-timeout-race-fixed | — | N/A | repeat loop | 20× `-n 8 --cov` and 20× `-n 4` over `tests/test_pool.py tests/test_api.py`; counts recorded | ✅ | ⬜ pending |
| (filled from PLAN.md tasks) | — | — | REQ-worst-row-margin-decided | — | N/A | grep / diff | `grep -n "^## L3[0-9]" docs/architecture/decision_log.md`; `git diff <phase-base> -- src/spur/app.py src/spur/params.py` empty for `SPUR_BUILD_TIMEOUT` and `spoke_count` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_pool.py` — three new tests (stale-executor, same-tick sibling, `_closed`), run red against the unfixed `pool.py` first
- [ ] `tests/test_bench.py` — registry assertion updated; `record_500`, identical-rows and baseline-suppression tests
- [ ] `bench/latency.py` — `record_500`, `run_composed(rows, label, record_500)`, the new scenario in `_SCENARIOS` only
- [ ] `Makefile` — `verify.static`, `verify.fast`, `test.fast`, hooks stamp, `.PHONY`
- [ ] `tests/test_hooks.py` — optional hook-drift test (text assertions only)
- [ ] a bare scratch remote for the real pre-push proof (task, not a file)
- No framework install: pytest, xdist, cov already present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Pre-push semantics (once per push, first ref, stash of unstaged changes, per-clone install) | REQ-hook-and-commit-timeout-decided | Needs a scratch repo + bare remote and a human-readable log | Scratch repo script from `17-RESEARCH.md`; paste the run table into the `Lxx` entry |
| The undocumented `500` reproduces on a fresh server before the fix | REQ-same-slot-timeout-race-reproduced | Live bench on a running server; a miss is a legitimate measured outcome (L08) | `SPUR_PORT=8001 .venv/bin/spur serve` then `.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 identical`; up to three attempts on restarted servers; record hit or miss in `bench/RESULTS.md` |
| Zero `500`s after the fix | REQ-same-slot-timeout-race-fixed | Same live bench; the deterministic test is the proof, the table is the record | Same scenario on a fresh server; append the table to `bench/RESULTS.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 64s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
