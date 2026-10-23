---
phase: "30"
slug: "scope-seam-and-gear-safety-guard"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-23"
---

# Phase 30 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`, coverage `fail_under = 96` |
| **Quick run command** | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_seam.py tests/test_gear_unchanged.py` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | ~15 s (`make verify.fast`), ~240 s (`make verify`) |

---

## Sampling Rate

- **After every task commit:** Run `make verify.fast` (carries `gear.unchanged` and the import contracts once wired)
- **After every seam commit:** also `make gear.unchanged` and `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py tests/regression`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds (L36 commit slice)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD by planner | — | — | REQ-scope-decision-logged | — | N/A | doc + git order | `grep -n '^## L46 ' docs/architecture/decision_log.md` | ✅ | ⬜ pending |
| TBD by planner | — | — | REQ-gear-unchanged-proof | T-30-* | never compares a tree with itself; fetch failure fails with cause | unit + target | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_gear_unchanged.py` ; `make gear.unchanged` | ❌ W0 | ⬜ pending |
| TBD by planner | — | — | REQ-gear-unchanged-proof | — | N/A | dry-run pin | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_hooks.py` | ✅ (new test W0) | ⬜ pending |
| TBD by planner | — | — | REQ-shaft-routes-separate | — | N/A | contract | `make lint-imports` | ✅ | ⬜ pending |
| TBD by planner | — | — | REQ-shaft-routes-separate | — | N/A | unit | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_seam.py` | ❌ W0 | ⬜ pending |
| TBD by planner | — | — | D-07 / D-09 | — | N/A | existing + unit | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py tests/regression` | ✅ | ⬜ pending |
| TBD by planner | — | — | REQ-gate-cost-recorded | — | N/A | measurement | `make verify` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/gear_unchanged.py` + Makefile wiring (`gear.unchanged` target, `verify.static` prerequisite)
- [ ] `tests/test_gear_unchanged.py` — scratch repo, red/green per watched item, missing-tag path, shadow guard
- [ ] `tests/test_seam.py` — route pin, contract-module existence guard, regex belt
- [ ] `tests/test_hooks.py` — dry-run pin: both `verify` and `verify.fast` run the check
- [ ] `tests/test_api.py` — 503 part-neutral text pin

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| L46 commit precedes the first shaft-module commit | REQ-scope-decision-logged | commit order is history, not a test | `git log --format='%h %s' --diff-filter=A -- src/spur/shaft_*.py src/spur/din5480*.py` vs the L46 commit |
| Each guard seen red once, reds recorded | REQ-gear-unchanged-proof, REQ-shaft-routes-separate | deliberate violations are reverted, not committed | rows in `bench/RESULTS.md` `### Seen red once (Phase 30)` |
| CI shallow checkout fetches the `v0.6` tag | REQ-gear-unchanged-proof | not testable from this host (A1) | first CI run of the phase reads green |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
