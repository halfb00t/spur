---
phase: "14"
slug: "honest-record"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-03"
---

# Phase 14 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Phase 14 adds no endpoint, auth path, file access or schema; every SUMMARY's `## Threat
Flags` reads "None". Its attack surface is the one this project names in CLAUDE.md: a number
the tool prints is a number someone will cut metal to (L08). The threats below are therefore
about *honesty of the record* — a warning that fires on a false height, a proof that agrees
with the kernel by construction, a tolerance an executor could loosen to turn red green, and a
decision-log entry that misstates what was measured. Each mitigation is a check that was run,
not a promise.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `derive()` → machinist | the lead-in warning and its height are printed by the API, the CLI and the UI and read as fact about the part | a height in mm at 3 dp; one sentence in `warnings` |
| README / docstring → reader | the geometry notes are what a user trusts about the flank without measuring it | the three measured heights (1.188, 1.25, 0.125 mm) and the condition under which the chord rises above the pitch circle |
| kernel → proof | the built solid's removed volume is checked against a number the tests compute; whether that check can fail is the boundary | volumes in mm³ at `abs=1e-9` (plain rows), `abs=1e-8` (three tip-chamfer hole rows), `volume_rel=1e-6` (eleven rows still at a literal) |
| executor → bar | a tolerance is the one value an executor could tune to turn a red proof green | the `abs`/`volume_abs`/`volume_rel` keywords of `_assert_the_cutout_is_what_derive_prints` |
| decision log → later phases | L33 is read as locked fact; a false "cannot" there steers future work | L33's figures, shas and the "not derived here" wording |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-14-01 | Spoofing (a false number presented as measured) | `derive()` lead-in warning | medium | mitigate | `calc.py` fires only at `round(spline_start(pr, root_fillet(p)) − pr.r, 3) > 0`; `tests/test_calc.py -k root_lead_in` (15 passed, re-run by the verifier) covers the default gear (−1.1875 mm, silent), `{1.0, 14.5°}` (+0.5625 mm) and `{0.75, 20°}` (+0.1250 mm), one field step either side of each crossing, and the print-precision-silent row; strings asserted in full | closed |
| T-14-02 | Tampering | `tests/regression/pre_v0_2.json`, `GearParams`, `DerivedDimensions` | medium | mitigate | fixture and `src/spur/params.py` byte-identical to `5d9e907` (verifier: `git diff --quiet`); `tests/regression` 86 passed; `src/` changed only in `calc.py` (+12) and `model.py` (+4/−3, docstring-only by AST, 14-01); 14-04 touched no `src/` file | closed |
| T-14-03 | Repudiation | README root-fillets bullet | low | mitigate | README's bullet carries only the three heights 14-01 measured (ROADMAP SC2, verified 2026-10-03); no micron figure anywhere in README | closed |
| T-14-04 | Tampering | the shared cutout assertion's tolerance | medium | mitigate | `abs=1e-9` is the fall-through for every row that sets neither `volume_rel` nor `volume_abs` (code review 2026-10-03 confirmed it cannot be masked); the rim-corner tripwire goes red when `_fillet_corner`'s `inside=True` root is perturbed (1 passed, verifier); 14-02's D-06 checkpoint measured the gaps before the bar moved | closed |
| T-14-05 | Spoofing (an oracle that agrees by construction) | `_filleted_spoke_volume` | medium | mitigate | polar closed form sharing no code with `_fillet_corner`; AST check for `_fillet_corner`/`cq` names (14-02 verify); kernel agreement 2.73e-12 mm³ recorded in L33 and the test docstring; the perturbation tripwire proves the oracle disagrees with a wrong root | closed |
| T-14-06 | Repudiation | the filleted-spoke debt and the planning record | low | mitigate | `docs/tech_debt/resolved/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` carries the measured table and the retiring sha (`b00c44c`); INDEX row moved in the same commit | closed |
| T-14-07 | Tampering | L09, L10, L30 and earlier decision-log entries | medium | mitigate | `git diff --numstat 5d9e907 -- docs/architecture/decision_log.md` deletes 0 lines (re-proved by 14-04's verify and the verifier); L33 is the last and only L33 heading | closed |
| T-14-08 | Repudiation | L33's figures and shas | low | mitigate | every e-notation figure in L33 appears in `tests/test_model.py` (verifier); the `feat(14-01)`, `test(14-01)`, `docs(14-01)` and `test(14-02)` shas, `abs=1e-9`, `0.125` and "warned, not re-cut" are present (14-04 must-have, verified) | closed |
| T-14-09 | Tampering | the four hole-through-web rows' volume bar | medium | mitigate | gaps measured on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1 before any bar moved (5.85e-10, 5.94e-10, 6.55e-10, 2.79e-12 mm³; executor ×2, verifier, reviewer — identical to every digit); the `1e-8` tip-row bar is the human's `blocking-human` checkpoint answer, recorded in L33, the debt file and the docstrings; the spy verify asserts each row's exact `d_volume` source and bar (`bar ok`) | closed |
| T-14-10 | Spoofing (a tripwire green for the wrong reason) | `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` | medium | mitigate | one control call outside `pytest.raises`, before the single `setattr` (AST order check, verifier); the parametrize holds no float literal except the `0.0` angles; `_holes_volume` / `_hex_cells_volume` bit-identical to the proof's former inline expressions; the control call passes on the unpatched build and the patched call still raises | closed |
| T-14-11 | Repudiation | the debt file, L33 and three docstrings | low | mitigate | normalized-text claim scan across `docs/`, `tests/`, `src/`, `README.md` finds no remaining "no closed form exists" beyond the four named exceptions (`claims ok`, verifier); L33's figures sit in test docstrings; numstat against `5d9e907` re-proves append-only | closed |
| T-14-SC | Tampering | npm/pip/cargo installs | low | accept | no package installed: `requirements.txt`, `pyproject.toml`, `Dockerfile` unchanged across `5d9e907..36c974a` (`git diff --stat` empty) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Residual, stated, not a threat in this register: the volume bars (`abs=1e-9`, `abs=1e-8`)
were calibrated on macOS arm64 while CI runs ubuntu-latest. That is a correctness/portability
finding from the prior code review (`8cfbc16`'s WR-01), dropped from the review ledger when
its id was reused; it is tracked under STATE.md Blockers/Concerns, not here.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-14-01 | T-14-SC (declared ×4, once per plan) | No package is installed in any plan of this phase; the pinned closure (L12) is unchanged, verified by `git diff --stat 5d9e907..HEAD` on the dependency manifests | execute-phase orchestrator, from the four PLAN.md threat models | 2026-10-03 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-03 | 15 (11 numbered + T-14-SC declared ×4) | 15 | 0 | ship orchestrator — secure-phase (State B, from PLAN.md threat models and SUMMARY threat flags), ASVS L1, short-circuit (register authored at plan time, threats_open 0); evidence from the 2026-10-03 verifier re-run (8/8) and the 14-04 executors' verifies, not from a separate auditor pass |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-03
