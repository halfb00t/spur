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

| Requirement | Behavior | Plan / Task | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-------------|-----------|-------------------|-------------|--------|
| REQ-shaft-params | field names/order, literal defaults, frozen, hashable, fit shape, bounds, non-finite, null | 31-01 T1-T2 (red T3) | unit | `pytest tests/test_shaft_params.py -x` | ❌ W0 (31-01) | ⬜ pending |
| REQ-profile-shift-from-dB | one pinned order; epsilon edges (17.6,0.8,20), (30,2,14), (25,1.25,19); range refusal; H_FP moves only the root | 31-01 T2 (red T3), oracle 31-02 | unit | `pytest tests/test_shaft_params.py tests/test_shaft_calc.py tests/test_din5480.py -k shift -x` | ❌ W0 (31-01) | ⬜ pending |
| REQ-shaft-basic-dims | d_a, d_f (0.55/0.60), s vs oracle on a 192-case grid and both vendor sets; key order | 31-01 T1, 31-02 T1-T2 (red T3), 31-04 T2 | unit | `pytest tests/test_din5480.py -k dims -x` | ❌ W0 (31-02) | ⬜ pending |
| REQ-form-diameter-honest | form_d None + reason on every shaft; internal construction vs oracle and vendors, never exposed | 31-03 T1-T2 (red T3) | unit | `pytest tests/test_din5480.py tests/test_shaft_calc.py -k form -x` | ❌ W0 (31-03) | ⬜ pending |
| REQ-mre-nominal | even/odd M_Re and contact vs oracle (72 cases); odd z null + warning, D_Re prints; guard by explicit pin_d; closed window; gauge step | 31-03 T1-T2 (red T3) | unit | `pytest tests/test_din5480.py tests/test_shaft_calc.py -k "pin or measure" -x` | ❌ W0 (31-03) | ⬜ pending |
| REQ-designation-codec | print canonical, parse D-05 variants, round trip, 25 refusals naming the token, length bound | 31-04 T1-T2 | unit | `pytest tests/test_din5480.py tests/test_shaft_calc.py -k designat -x` | ❌ W0 (31-04) | ⬜ pending |
| Copy anchors | ≥2 basic-dimension rows, d_Ff row, odd-z row, cited; each seen red | 31-05 T2 (checkpoint), 31-06 T1-T2 | unit | `pytest tests/test_din5480_anchors.py -x` | ❌ (31-06) | ⬜ pending |
| Seam | contracts + belts green | every plan | contract | `make lint-imports && pytest tests/test_seam.py` | ✅ | ⬜ pending |
| Oracle independence / sensitivity | no `spur` import; durable mutation tests; mutated formulas seen red | 31-02 T1-T3, 31-03 T2-T3 | unit | `pytest tests/test_din5480.py -k "oracle_imports or mutat" -x` | ❌ W0 (31-02) | ⬜ pending |
| Gear unchanged | v0.6 byte-equal | every plan; close 31-06 T3 | gate | `make gear.unchanged` | ✅ | ⬜ pending |
| Gate cost | delta in bench/RESULTS.md against Phase 30 | 31-06 T3 | measurement | `/usr/bin/time -p make verify` | n/a | ⬜ pending |

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
