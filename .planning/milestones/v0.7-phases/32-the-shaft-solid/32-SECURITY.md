---
phase: "32"
slug: "the-shaft-solid"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-27"
---

# Phase 32 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register taken from the `<threat_model>` blocks of 32-01..32-06-PLAN.md (authored at plan time); verified at
> ASVS L1 (grep depth) against the code at the end of the phase, plus `make verify` green
> (`2644 passed in 233.72s`, `Contracts: 10 kept, 0 broken.`).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Parameters → `ShaftParams` | User-typed shaft fields (link, API, CLI) validated once at the params boundary | floats/ints, untrusted |
| Serving process → kernel worker | `spur.model -> spur.shaft_model` is the one allowed edge; the server never imports OpenCascade (L17) | validated params in, STL/STEP bytes out |
| Printed numbers → the shop | `end_chamfer_effective` and the warnings are cut to (L08) | measured values, correctness-critical |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation (evidence) | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-32-01 | Repudiation | gate baseline | medium | mitigate | Fresh logged `make verify` on Phase 31 code; 221.86 s named unused in `bench/RESULTS.md` | closed |
| T-32-02 | Tampering | `end_chamfer` reading rounded past a cap | high | mitigate | `floor_mm` in `src/spur/shaft_calc.py`; 2.0006 / 1.0009 rows in `tests/test_shaft_calc.py` | closed |
| T-32-03 | Tampering | chamfer silently capped | high | mitigate | `chamfer_capped_warning` in `shaft_calc.py`, asserted in `tests/test_shaft_calc.py` | closed |
| T-32-04 | Denial of service | cone start near root circle (kernel hang) | high | mitigate | `_guard_cone_start` in `src/spur/shaft_model.py`; `test_no_lattice_chamfer_reaches_the_root_band` | closed |
| T-32-05 | Tampering | empty shape / remnant returned as the part | high | mitigate | one-valid-solid check + `_guard_volume` in `shaft_model.py`; closed-form tests | closed |
| T-32-06 | Tampering | tangent shank invalid via cleaning step | medium | mitigate | no `.clean()` call in `shaft_model.py`; 11 shank rows; red log `32-03-red-clean.log` | closed |
| T-32-07 | Tampering | `_build` dispatch changing gear builds | high | mitigate | additive `isinstance(p, ShaftParams)` first statement in `src/spur/model.py`; `make gear.unchanged` green | closed |
| T-32-08 | Tampering | path traversal via download/temp stem | medium | mitigate | `ShaftParams.slug()` numbers-only (`spur_shaft_` pattern test in `tests/test_shaft_params.py`); `TemporaryDirectory` in `model.py` | closed |
| T-32-09 | Denial of service | serving process importing the kernel | high | mitigate | `pyproject.toml` ignores exactly `spur.model -> spur.shaft_model`; `Contracts: 10 kept, 0 broken.` | closed |
| T-32-10 | Denial of service | unbounded geometry exhausting a worker | high | mitigate | `bench/sweeps/shaft.json` at every solid-field max on macOS + Linux; D-09 confirmed (32-05) | closed |
| T-32-11 | Tampering | non-finite floats in solid fields | medium | mitigate | `test_non_finite_numbers_are_refused` in `tests/test_shaft_params.py` | closed |
| T-32-12 | Repudiation | cumulative peak reported as per-row memory | medium | mitigate | `--fresh` child per row in `bench/build_time.py` | closed |
| T-32-13 | Repudiation | estimated gate delta / closing numbers | medium | mitigate | one logged `/usr/bin/time -p make verify` vs 32-01's logged baseline (32-06) | closed |
| T-32-SC | Tampering | package installs | low | accept | `requirements.txt` unchanged since phase start (7c1bc2c) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-32-01 | T-32-SC | No package added or upgraded in this phase; `requirements.txt` diff against 7c1bc2c is empty | plan-time register (32-01..32-06) | 2026-10-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-27 | 14 | 14 | 0 | secure-phase (orchestrator, L1 grep short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-27
