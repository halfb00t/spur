---
phase: "4"
slug: "typed-derived-dimensions-contract"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-24"
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (measured in research: `pytest --version` during the `make verify` run) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `filterwarnings = ["error", ...]`: a pydantic deprecation warning from a model definition fails the suite |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_calc.py -q"` (per-file; the form Phase 3 used) |
| **Full suite command** | `make verify` (ruff + mypy `--strict` with the new `disallow_any_explicit` + import-linter + unfinished-work scan + pytest) |
| **Estimated runtime** | `make verify` 41.8s wall measured in research (99 tests; pytest alone 30.3s). L13 cites ~11s warm; the executor records its own number rather than trusting either |

---

## Sampling Rate

- **After every task commit:** Run `make test PYTEST_ARGS="<touched test file> -q"`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green, and `disallow_any_explicit = true` must be present in `pyproject.toml` `[tool.mypy]` — `make typecheck` reads the config file, not a CLI flag, so a green hand-run `mypy --disallow-any-explicit` does not count
- **Max feedback latency:** ~45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | REQ-{XX} | T-{N}-01 / — | {expected secure behavior or "N/A"} | unit | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_api.py` — `/openapi.json` structural test (D-11): `/api/info` `200` `$ref`s `DerivedDimensions`, component lists every field, a length field carries `unit: mm`, `/api/health` `$ref`s `HealthReport`
- [ ] `tests/test_records.py` (or a new `tests/test_static.py`) — `app.js` `DIMS`-vs-`DerivedDimensions` regex belt (D-12), pattern copied from `test_calc_module_stays_log_free`
- [ ] `tests/test_cli.py` — CLI-vs-API equivalence test (D-13): `json.loads(spur info stdout) == client.get("/api/info").json()` with and without a mate; without one, `mate_teeth`/`centre_distance` present-and-`null` on both
- No framework/config gap: pytest, `TestClient` and the CLI's subprocess/import pattern are already in place and exercised by the existing 99 passing tests.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| {behavior} | REQ-{XX} | {reason} | {steps} |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
