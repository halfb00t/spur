---
phase: "31"
slug: "shaft-maths-parameters-and-designation"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-24"
---

# Phase 31 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + xdist + pytest-cov (`filterwarnings = ["error"]`) |
| **Config file** | `pyproject.toml` (coverage `fail_under = 96`, branch coverage on) |
| **Quick run command** | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_din5480.py tests/test_shaft_params.py tests/test_shaft_calc.py tests/test_seam.py` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick ~5 s; `make verify.fast` ~10 s (bench 30-01); full `make verify` per bench/RESULTS.md |

---

## Sampling Rate

- **After every task commit:** Run `make verify.fast` (commit-hook budget 30 s)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green, `make gear.unchanged` green, `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Filled by the planner per task; requirement-to-test mapping from `31-RESEARCH.md` § Validation Architecture:

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REQ-shaft-params | field names/order, literal defaults, frozen, fit shape | unit | `pytest tests/test_shaft_params.py -x` | ❌ W0 | ⬜ pending |
| REQ-profile-shift-from-dB | xm for 5 shafts; epsilon edges (30,2,14), (25,1.25,19), (17.6,0.8,20); range refusal; H_FP independent of shift | unit | `pytest tests/test_din5480.py -k shift -x` | ❌ W0 | ⬜ pending |
| REQ-shaft-basic-dims | d_a, d_f, s vs oracle and vendor sets | unit | `pytest tests/test_din5480.py -k dims -x` | ❌ W0 | ⬜ pending |
| REQ-form-diameter-honest | form_d None + reason; internal construction not exposed | unit | `pytest tests/test_shaft_calc.py -k form -x` | ❌ W0 | ⬜ pending |
| REQ-mre-nominal | even/odd M_Re vs oracle; odd z null + warning; D_Re prints odd z; guard by explicit pin_d | unit | `pytest tests/test_din5480.py tests/test_shaft_calc.py -k "pin or measure" -x` | ❌ W0 | ⬜ pending |
| REQ-designation-codec | print canonical, parse D-05 variants, round trip, refusal names token | unit | `pytest tests/test_din5480.py -k designation -x` | ❌ W0 | ⬜ pending |
| Seam | contracts + belts green | contract | `make lint-imports && pytest tests/test_seam.py` | ✅ | ⬜ pending |
| Oracle independence / sensitivity | no `spur` import; mutation seen red | unit | `pytest tests/test_din5480.py -k "oracle or mutat" -x` | ❌ W0 | ⬜ pending |
| Gear unchanged | v0.6 byte-equal | gate | `make gear.unchanged` | ✅ | ⬜ pending |
| Gate cost | delta in bench/RESULTS.md | measurement | `/usr/bin/time -p make verify` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/shaft_oracle.py` — not collected, imports nothing from `spur`, plain floats
- [ ] `tests/test_din5480.py`, `tests/test_shaft_params.py`, `tests/test_shaft_calc.py`
- [ ] No framework install needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Formula clauses and anchor rows confirmed against DIN 5480 (2006) | REQ-profile-shift-from-dB, REQ-shaft-basic-dims, REQ-form-diameter-honest, REQ-mre-nominal | Only the human holds the copy (L08, D-06) | `checkpoint:human-action`: human types anchor rows (part, clause, table) and confirms each formula; rows become pinned tests |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
