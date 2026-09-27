---
phase: "9"
slug: "keyway-bore"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-27"
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `09-RESEARCH.md` § Validation Architecture; the per-task map is
> filled once the plans exist (validate-phase §6).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing project pin, `pyproject.toml` `[tool.pytest]`) |
| **Config file** | `pyproject.toml` (unchanged) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest — CLAUDE.md's one gate) |
| **Estimated runtime** | ~48 s warm for `make verify` (measured, 08-CONTEXT.md D-14); cold first run is page cache, not the tests |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` and `git diff --exit-code tests/regression/pre_v0_2.json` (L26: the fixture never moves in a feature commit)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green and `make bench.build SWEEP=bench/sweeps/keyway_bore.json` recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s`
- **Max feedback latency:** ~48 s (one warm `make verify`)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | REQ-{XX} | T-9-01 / — | {expected secure behavior or "N/A"} | unit | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Filled from the PLAN.md tasks by validate-phase; the requirement → test map the plans must
cover is `09-RESEARCH.md` § "Phase Requirements → Test Map".*

---

## Wave 0 Requirements

- [ ] `tests/test_calc.py` — parametrized 422 cases for D-02, D-03, D-10, D-11, D-12 and D-13's two sentences (REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused)
- [ ] `tests/test_model.py` — the built-solid datum test (D-14), the chamfer-survives-the-slot test (D-07), the D-flat + keyway coexistence build (D-04), the recess-yields test (D-09); new rows in `test_each_edge_selector_picks_exactly_its_own_edges` and `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`
- [ ] `bench/sweeps/keyway_bore.json` — the sweep file `make bench.build SWEEP=` reads (REQ-measured-build-time)
- [ ] No framework install: pytest is already installed and configured

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ROADMAP SC1/SC3/SC4 and REQUIREMENTS.md amendments (D-20) | REQ-keyway-bore, REQ-keyway-wall-refused | One human confirmation of wording before the write, through the edit-phase tooling (08-01's pattern) | `git show <commit> -- .planning/ROADMAP.md .planning/REQUIREMENTS.md`; confirm the as-cut wall formula `(bore_d + bore_clearance)/2`, the dropped "or a recess wall" clause, and SC4's amended proof sentence |
| A sweep row over `SPUR_BUILD_TIMEOUT=30s` | REQ-measured-build-time | Halts for a human decision, never a silent narrowing (08 D-11) | Read the `make bench.build` Markdown rows; any `**NO**` row stops the phase |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
