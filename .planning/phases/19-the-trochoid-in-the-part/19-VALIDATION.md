---
phase: "19"
slug: "the-trochoid-in-the-part"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-08"
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0; `filterwarnings = ["error", ...]`, `--strict-markers` (read from `.venv` by 19-RESEARCH) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`; `[tool.coverage.*]` `branch = true`, `fail_under = 96`), `Makefile` |
| **Quick run command** | `make verify.fast` (commit-time slice, L36 — every test file except `test_model.py`, `test_pool.py`, `test_api.py`, `test_cli.py`); targeted: `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`, kernel rows `make test PYTEST_ARGS="tests/test_model.py -k trochoid -q -n0 --no-cov"` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest `-n 8 --cov`, 96 % floor) |
| **Estimated runtime** | `make verify.fast` 11.3 s (M2 Max, L36); `make verify` 45.59 s wall on this host (Apple M5 Max, 18 CPUs, 1023 passed — 19-RESEARCH F10). The 66 s bar (L34) was read on an M2 Max: measure the phase delta on one host. |

---

## Sampling Rate

- **After every task commit:** `make verify.fast` (the L36 pre-commit hook) plus by hand `git diff --exit-code tests/regression/pre_v0_2.json` and `.venv/bin/python -m pytest tests/regression -q -n0 --no-cov`
- **After every plan wave:** `make verify`
- **Before `/gsd-verify-work`:** `make verify` green with its result line stated and its wall time recorded against the 66 s bar with host and load
- **Max feedback latency:** 30 seconds (L36 commit-time budget)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | REQ-{XX} | T-19-01 / — | {expected secure behavior or "N/A"} | unit | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Rows are filled from the PLAN.md tasks once planning completes; the requirement → test map that seeds them is 19-RESEARCH.md "Validation Architecture".*

---

## Wave 0 Requirements

- [ ] `tests/test_trochoid.py` — derive branch, sentences, waist/floor, `x_min`, `spline_start`/chamfer limit, enum/CLI parity pieces that need no kernel
- [ ] `tests/test_model.py` — kernel tier (build rows, `Edge.positionAt` vs oracle, guards, short-arc branch, compose matrix, `_tip_edges` selector column)
- [ ] `tests/test_cli.py` (field-walk generalisation, parity document, bad value exit 2) and `tests/test_api.py` (line 315 adjacency, the literal field set, the `DerivedDimensions` key set at line 78)
- [ ] `tests/composition.py` — a root axis or a separate trochoid table; `ALWAYS` split for null `root_thickness`/`root_gap`
- [ ] `bench/` spike subcommands, `bench/sweeps/trochoid.json`, `tests/test_bench.py` pin, `bench/RESULTS.md` section
- [ ] Framework install: none — existing infrastructure covers the phase

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `make verify` wall time against the 66 s bar (L34) | REQ-trochoid-composes-and-is-priced | A timing is read on one host with its load noted, not asserted by a test | Run `make verify` by hand; record wall time, host, CPU count and load in `bench/RESULTS.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
