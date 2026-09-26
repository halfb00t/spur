---
phase: "07"
slug: "foundation-generalized-edge-selection-regression-fixture"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-26"
---

# Phase 07 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register authored at plan time (both PLAN.md files carry a `<threat_model>` block). Highest
severity in the register is `medium`; `workflow.security_block_on` is `high`, ASVS level 1 —
verified at grep depth by the orchestrator against the tree at `f3523e4`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| working tree → checked-in oracle | `tests/regression/pre_v0_2.json` is the value every later phase's gate trusts; whoever writes it decides what "unchanged" means | 44 records: `derive()` fields, solid volume / bbox / face+edge counts, provenance header |
| capture script → git | `capture.py` shells out to `git` for provenance | read-only `git` output (HEAD sha, dirty state) |
| package index → CI venv | CI resolves `cadquery` / `cadquery-ocp` from `pyproject.toml` ranges at run time; the oracle's numbers are kernel-specific | kernel version pair |
| client → build pipeline | API query / CLI flags reach `_build` only as a validated, frozen `GearParams`; this phase adds no field and no parsing | validated parameters |
| build pipeline → client | a `BuildError` message becomes a 422 `detail` (API) or stderr (CLI) | static guard text |
| keystroke path | `calc.py` runs on every form change and must stay free of the kernel | pure arithmetic |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-07-01 | Tampering | `tests/regression/pre_v0_2.json` | medium | mitigate | `test_pre_v0_2.py` has no write/dump/open call (grep); `capture.py` is invoked only by `Makefile:133` (`fixture.regen`); `test_the_fixture_records_every_corpus_set` (`test_pre_v0_2.py:55`) fails on a hand-edited or stale JSON; own-commit rule logged as L26 (`decision_log.md:738`) | closed |
| T-07-02 | Repudiation | a regeneration that hides a regression | medium | mitigate | Provenance header present: `git_head 6f06d77…`, `src_clean true`, `cadquery 2.8.0`, `cadquery-ocp 7.9.3.1.1`, `captured 2026-09-26`, plus the `regenerate` rule string; no test or pytest flag regenerates (grep: only `capture.py` writes) | closed |
| T-07-03 | Tampering | `capture.py` git subprocess | low | mitigate | `capture.py:74-75`: fixed argv `["git", *args]`, `cwd=_REPO_ROOT`, `check=True`, `capture_output=True`, no `shell=True`, no user input | closed |
| T-07-04 | Tampering | CI kernel resolution vs the oracle | medium | mitigate | `test_the_fixture_was_captured_on_the_kernel_this_run_uses` (`test_pre_v0_2.py:64`) fails naming both version pairs; unpinned CI install filed as `must` debt `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` | closed |
| T-07-05 | Denial of service | `make verify` runtime on every hook and CI run | low | mitigate | D-06 measured delta 16.27 s (two runs each way) recorded in `bench/RESULTS.md` § "Regression fixture cost (Phase 7, D-06)"; over the 15.0 s line, accepted by the human (option A) rather than silently trimmed | closed |
| T-07-06 | Tampering | `_bore_rim_edges` / `_groove_floor_edges` feeding `.chamfer()` / `.fillet()` | medium | mitigate | `model.py:233-238` and `:264-269` raise `BuildError` on an empty selection; `test_each_edge_selector_picks_exactly_its_own_edges` (`test_model.py:66`, 10 rows) plus two refusal tests (`:122`, `:136`); fixture byte-unchanged through 07-02 (`git log -- pre_v0_2.json` shows only 07-01 commits), tripwire 32 red / 0 derive | closed |
| T-07-07 | Information disclosure | guard message → API 422 body / CLI stderr | low | mitigate | Both messages are static string literals naming only the feature and the parameter to zero (`model.py:235-237`, `:266-268`); no exception repr, path or kernel type interpolated | closed |
| T-07-08 | Denial of service | per-request cost of the guard | low | accept | One `if not edges:` on a list the selector already built (`model.py:233`, `:264`); no extra kernel call — see R-07-01 | closed |
| T-07-09 | Tampering | `calc.py` purity | low | mitigate | `calc.py` imports only `math`, `dataclasses`, `typing`, `pydantic` (grep: no `cadquery` / `OCP`); import-linter contract "The gear maths stays free of the CAD kernel" (`pyproject.toml:142`) passes in `make verify` | closed |
| T-07-SC | Tampering | package installs | low | accept | `git diff c640ed8..HEAD -- pyproject.toml requirements*.txt` is empty: no package installed, no dependency changed — see R-07-02 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-07-01 | T-07-08 | The guard is one list-emptiness check on data the selector already produced; it adds no kernel call and no allocation, so it cannot change the per-request cost profile measured in Phase 2 | plan 07-02 (`<threat_model>`), unchanged at audit | 2026-09-26 |
| R-07-02 | T-07-SC | The phase installs no package and changes no dependency range; the supply-chain surface is the one v0.1 already audited | plans 07-01 / 07-02 (`<threat_model>`), unchanged at audit | 2026-09-26 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-26 | 10 | 10 | 0 | orchestrator (grep-depth, ASVS L1 short-circuit; tree `f3523e4`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-26
