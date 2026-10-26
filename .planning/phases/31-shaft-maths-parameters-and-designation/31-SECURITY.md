---
phase: "31"
slug: "shaft-maths-parameters-and-designation"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-26"
---

# Phase 31 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Caller → `ShaftParams` | Numbers and the fit token a future route or CLI passes in (no route yet; Phase 33) | Untrusted numerics and a short string; no secrets |
| Caller → `parse_designation` | Free text a user types as a DIN 5480 designation | Untrusted string, bounded to 64 code points |
| Licensed copy → repository | DIN 5480 values the human reads from a licensed, uncontrolled copy | Licensed table values and clause text; only human-approved rows may cross |
| Shaft code → gear contract | Shaft work in the same package as the shipped gear | The v0.6 gear link contract (`/api/schema`, regression corpus) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-31-01 | Tampering | `ShaftParams` numeric fields (nan, inf, 1e400, None) | medium | mitigate | Field `ge`/`le` and types refuse them; `test_non_finite_numbers_are_refused`, `test_a_missing_or_null_field_is_refused_by_its_type` (`tests/test_shaft_params.py`) | closed |
| T-31-02 | Tampering | `fit` token (Unicode digits, newline, case, ISO spelling) | medium | mitigate | `din5480.FIT_PATTERN` with ASCII classes and full anchors, `max_length=3` (`shaft_params.py`); `test_the_fit_token_is_checked_for_shape_only` | closed |
| T-31-03 | Tampering | Out-of-range combination built as a nearby shaft | high | mitigate | `shaft_calc.check_shaft` refuses past `X_MIN`/`X_MAX` with `X_EPS`, never clamps; refusal rows incl. 25.001 / 25.00001 / 24.99999 (WR-01, WR-06) | closed |
| T-31-04 | Tampering | A gear link moved by shaft work | high | mitigate | `git diff v0.6 -- src/spur/params.py src/spur/calc.py tests/regression .github/workflows/ci.yml` empty; `make gear.unchanged` byte-equal (8723-byte schema) on the final tree | closed |
| T-31-05 | Tampering | Oracle importing or copying the code it checks | high | mitigate | `test_the_shaft_oracle_imports_nothing_from_spur` (`tests/test_din5480.py`); `tests/shaft_oracle.py` imports `math` only; oracle-side mutation seen red (31-02) | closed |
| T-31-06 | Denial of service | Oracle grid cost in pre-commit `make verify.fast` | low | mitigate | Closed-form 192-case grid, 0.39 s serial (31-02 SUMMARY); `verify.fast` passes in the commit hook | closed |
| T-31-07 | Tampering | Involute inversion returning confident garbage | high | mitigate | Bracketed bisection in `din5480.py`, None outside `(0, inv(89 deg))` and below the base circle; 72-case oracle grid at 1e-9 (31-03) | closed |
| T-31-08 | Tampering | Unproved number printed (d_Ff, odd-z M_Re, M_Re for another pin) | high | mitigate | `form_d=None` always, odd-z gate, M_Re recomputed for the printed pin (`shaft_calc.py`); M_Re labelled nominal-thickness with no fit allowance (WR-02) | closed |
| T-31-09 | Denial of service | Regex work on a long designation | medium | mitigate | `DESIGNATION_MAX_LENGTH = 64` checked before any regex; linear per-token `fullmatch` (`din5480.parse_designation`) | closed |
| T-31-10 | Tampering | Unicode digits, ×, no-break space or newline slipping through | medium | mitigate | ASCII classes and `fullmatch` only; refusal rows for each in `REFUSED_DESIGNATIONS` | closed |
| T-31-11 | Tampering | `float()` accepting inf/nan/exponent/underscore; fractional teeth truncated | high | mitigate | Grammar checked before conversion; refusal rows `inf`, `1e3`, `2_5`, `18.5` (`tests/test_din5480.py:307-315`); leading zeros refused (WR-05) | closed |
| T-31-12 | Information disclosure | Echoed token in an error a page renders | low | transfer | Token bounded to 64 characters (`DesignationError.token`; the length refusal's message echoes no text). Rendering as text is Phase 33's 422 handling | closed |
| T-31-13 | Information disclosure | Licensed table values or clause text committed beyond approved anchors | high | mitigate | Only the three human-approved W 120x3x38x8f values are committed, each cited (`tests/test_din5480_anchors.py`); no table file; review fixes checked to add no DIN 5480 value (WR-03, IN-04) | closed |
| T-31-14 | Tampering | Constant edited silently to match the copy, or tolerance loosened | high | mitigate | No constant edited at 31-06 (L47); anchor tolerance half a unit of the printed digit; `H_FP_HOBBING` (IN-04) restates an already-committed 0.60 and moves no printed number (113.100 / 22.125 unchanged) | closed |
| T-31-15 | Repudiation | Anchor with no citation, or licensed value with no approval | medium | mitigate | Each `test_anchor_*` carries part, clause and figure; values from approved rows in 31-05-SUMMARY.md | closed |
| T-31-16 | Tampering | A gear link moved during the shaft phase | high | mitigate | Same evidence as T-31-04; `gear.unchanged` green at 31-06 close and after the review fixes | closed |
| T-31-SC | Tampering | npm/pip/cargo installs | low | accept | No package installed; `git diff v0.6 -- requirements.txt` empty | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-31-01 | T-31-SC | No dependency installed or changed in this phase (stdlib `math`/`re` only) | plan-phase (all plans) | 2026-10-26 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-26 | 17 | 17 | 0 | execute-phase orchestrator (L1 grep-depth, auditor skipped per short-circuit rule) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-26
