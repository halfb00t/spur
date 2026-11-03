---
phase: "34"
slug: "fit-tables-and-tolerance-window"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-30"
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `34-RESEARCH.md` § Validation Architecture. No transcribed table value appears here (D-01).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 with pytest-xdist, pytest-cov |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_din5480_tables.py tests/test_din5480_read1.py tests/test_shaft_calc.py tests/test_shaft_parity.py` |
| **Full suite command** | `make verify` |
| **Commit-time slice** | `make verify.fast` (L36, under 30 s) |
| **Estimated runtime** | ~245 seconds full (Phase 33 close: 242.47 s real; L43 bar 300 s) |

---

## Sampling Rate

- **After every task commit:** Run `make verify.fast`
- **After every plan wave:** Run `make verify`, reading recorded with load
- **Before `/gsd-verify-work`:** Full suite green, plus `make gear.unchanged`, `make lint-imports` (10 kept), the real-file module green on the human's host
- **Max feedback latency:** 30 seconds (commit slice)

---

## Per-Task Verification Map

Task IDs are filled in by the planner; requirement rows come from research.

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REQ-tables-private-file | env unset: new rows null + warning naming `SPUR_DIN5480_TABLES`, part builds | unit | `pytest --no-cov -n0 tests/test_shaft_calc.py -k tables` | ✅ | ✅ green |
| REQ-tables-private-file | set but missing/unreadable/invalid/failing invariant: refuse to start (CLI, lifespan, `spur serve`) | unit + cli + app | `pytest --no-cov -n0 tests/test_din5480_tables.py tests/test_cli.py tests/test_pool.py -k tables` | ✅ | ✅ green |
| REQ-tables-private-file | `private/` gitignored + dockerignored; no tracked JSON validates as tables; warning never carries the path | unit | `pytest --no-cov -n0 tests/test_din5480_tables.py -k "ignored or warning_has_no_path"` | ✅ | ✅ green |
| REQ-tables-transcribed-twice | each invariant (T_G sum, unit slip, U+2212, NaN, duplicate, provenance, M1 identity) refuses, seen red once | unit | `pytest --no-cov -n0 tests/test_din5480_tables.py -k "broken or m1_identity"` | ✅ | ✅ green |
| REQ-tables-transcribed-twice | two reads diff to zero, locations only; read-1 parser quirks | unit + procedural | `pytest --no-cov -n0 tests/test_din5480_tables.py tests/test_din5480_read1.py tests/test_din5480_tables_tool.py -k "diff or read1"` | ✅ | ✅ green |
| REQ-fit-tolerance-window | page example window; fit outside Table 7 warns + null (200 not 422); range edge | unit + api | `pytest --no-cov -n0 tests/test_shaft_calc.py -k "window or fit_outside or edge"` | ✅ | ✅ green |
| REQ-mre-limits | M_Re at tabulated pin vs printed M1 on anchors; limits vs oracle; odd z; guard bound | unit | `pytest --no-cov -n0 tests/test_din5480_anchors.py tests/test_shaft_calc.py -k "m1 or limits or odd or guard"` | ✅ | ✅ green |
| REQ-solid-max-material | solid thickness read back = s_vmax with tables, nominal without; pool worker sees tables; caches separated | kernel + pool | `pytest --no-cov -n0 tests/test_shaft_model.py tests/test_pool.py -k "thickness or tables or cache"` | ✅ | ✅ green |
| REQ-off-table-builds | neighbours of listed sizes build from formulas, rows null + warned, numbers unchanged | unit | `pytest --no-cov -n0 tests/test_shaft_calc.py -k off_table` | ✅ | ✅ green |
| criterion 3 parity | API = CLI = page with tables loaded, new keys in `dims` | unit + browser | `pytest --no-cov -n0 tests/test_shaft_parity.py tests/test_shaft_interfaces.py tests/test_browser.py` | ✅ | ✅ green |
| real file | anchors, M1 identities, guard and tip-land sweeps on the real file (skipped in CI) | real-file | `make tables.test FILE=private/din5480-tables.json` (`tests/din5480_real_tables_check.py`, not collected by the gate) | ✅ | ✅ green |
| REQ-gate-cost-recorded | baseline + close readings in `bench/RESULTS.md`; Phase 30 check green | procedural | `/usr/bin/time -p make verify` ; `make gear.unchanged` | n/a | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/din5480_tables_fixture.py` — synthetic builder (invented filler + approved anchors only)
- [x] `tests/test_din5480_tables.py`, `tests/test_din5480_read1.py`, `tests/din5480_real_tables_check.py` (shipped under this name, run by `make tables.test`)
- [x] `tests/conftest.py` autouse isolation of env var and loader state; `with_tables` fixture clearing solid/export caches
- [x] `scripts/din5480_read1.py`, `scripts/din5480_tables_tool.py` (shipped under this name), `make tables.check` / `make tables.diff`
- [x] `.gitignore` `/private/` and `.dockerignore` `private`, committed before any file exists there
- [x] Update exact warning-tuple and key-list assertions (research Pitfall 11)
- [x] Browser-session hook to pass `SPUR_DIN5480_TABLES` to the server for one step

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Anchor approval by name | REQ-tables-transcribed-twice | D-07: the human approves each committed value | Checkpoint shows candidate rows; human names approvals |
| Disagreement resolution | REQ-tables-transcribed-twice | D-08: the human reads the page | Checkpoint lists table/row/column/page; human settles each |
| Range-edge convention | REQ-fit-tolerance-window | Research A1: über/bis convention unverified | Human confirms from the copy at the D-07 checkpoint |
| Leak review | REQ-tables-private-file | No tool can tell a transcribed value from a computed one | Read every added file in the phase diff for table values |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-31 (validate-phase audit: 12 rows, 0 gaps; every row's command run green, real-file row via `make tables.test`: 22 passed)

## Validation Audit 2026-10-31

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
