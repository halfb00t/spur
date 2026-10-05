---
phase: "07"
slug: "foundation-generalized-edge-selection-regression-fixture"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-05"
reconstructed: true
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Reconstructed on 2026-10-05 by `/gsd-validate-phase 7` (State B: the phase shipped
> without a VALIDATION.md). Every status below was re-measured on the working tree at
> that date, not copied from the SUMMARYs.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (pytest-xdist, pytest-cov) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `xfail_strict`, warnings are errors) |
| **Quick run command** | `.venv/bin/python -m pytest tests/regression "tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores" "tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore" "tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges" "tests/test_model.py::test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error" -q -p no:cacheprovider` (exactly the eight tests in the map below; the whole of `tests/test_calc.py tests/test_model.py` is 693 cases and took 182.35 s serial on 2026-10-05, not a quick run) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-linter, no-fake-done scan, pytest) |
| **Estimated runtime** | quick: ~35 s serial for the 119 phase-7 cases (33.08 s and 34.38 s on two 2026-10-05 runs); full: ~65 s wall (929 passed in 63.71 s, 8 workers, 2026-10-05) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command above, then `git diff --exit-code tests/regression/pre_v0_2.json`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~65 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | REQ-defaults-off-regression | T-07-01 / T-07-02 | Only `make fixture.regen` writes the oracle; the provenance header names HEAD, `src_clean`, kernel versions and the capture date | regression | `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py -q` (`test_a_pre_v0_2_parameter_set_derives_the_same_dimensions`, `test_a_pre_v0_2_parameter_set_builds_the_same_solid`) | ✅ | ✅ green |
| 07-01-02 | 01 | 1 | REQ-defaults-off-regression | T-07-01 | A hand-edited or stale JSON fails one named test instead of passing silently | regression | `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py::test_the_fixture_records_every_corpus_set tests/regression/test_corpus.py -q` | ✅ | ✅ green |
| 07-01-03 | 01 | 1 | REQ-defaults-off-regression | T-07-04 / T-07-05 | A kernel that differs from the fixture's provenance fails one test naming both version pairs, not dozens of topology mismatches | regression | `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_run_uses -q` | ✅ | ✅ green |
| 07-02-01 | 02 | 2 | REQ-edge-selection-proven | T-07-09 / T-07-06 | `calc.py` stays kernel-free; an empty bore-rim selection raises `BuildError` through the real build path | unit + contract | `.venv/bin/python -m pytest tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore -q && make lint-imports` | ✅ | ✅ green |
| 07-02-02 | 02 | 2 | REQ-edge-selection-proven | T-07-06 / T-07-07 | Exact edge multiset per bore shape, with and without recesses; both guards raise a static-string `BuildError`, never the catch-all's "try smaller" wording | unit | `.venv/bin/python -m pytest tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges tests/test_model.py::test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error -q` | ✅ | ✅ green |
| 07-02-03 | 02 | 2 | REQ-defaults-off-regression | — | The fixture is byte-unchanged by the selector change; L26 is appended, not edited | integration | `git diff --exit-code 540f1a0 -- tests/regression/pre_v0_2.json && grep -c '^## L26' docs/architecture/decision_log.md && make verify` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Measured 2026-10-05 on the working tree (branch `gsd/phase-16-typing-validation-debt`,
HEAD `dcb3518`):

- Quick run of every phase-7 test above: `119 passed in 34.38s`.
- `make verify`: `929 passed in 63.71s`, mypy `Success: no issues found in 37 source
  files`, all 5 import contracts `KEPT`.
- `git log --oneline -- tests/regression/pre_v0_2.json` shows a single commit
  (`540f1a0`, the Phase 7 merge): the fixture has never been regenerated since it
  landed, so every v0.2 phase through 12 ran against the oracle captured on pre-v0.2
  code.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-06 cost gate: the fixture's `make verify` delta is measured and, above 15.0 s, decided by a human rather than trimmed silently | REQ-defaults-off-regression | Human judgment by design (plan 07-01, prohibition 2): a test cannot auto-pass a cost decision | Read `bench/RESULTS.md` § "Regression fixture cost (Phase 7, D-06)" (delta 16.27 s, Option A accepted). To re-measure: two `make verify` runs with `tests/regression` and two without, same session, report the mean delta |
| Regeneration is byte-stable: two consecutive `make fixture.regen` runs on an unchanged tree write identical JSON | REQ-defaults-off-regression | Automated one-liner, kept out of the suite: it rebuilds all 39 solids twice, doubling the 16.27 s the D-06 gate already accepted | `F=$(mktemp) && cp tests/regression/pre_v0_2.json "$F" && make fixture.regen && cmp tests/regression/pre_v0_2.json "$F"`. Run on a tree whose `src/` matches the fixture's `git_head`; afterwards `git checkout -- tests/regression/pre_v0_2.json`. Never commit a regenerated fixture outside its own D-03 commit |
| Tripwire: a silently vanished bore chamfer turns exactly the 32 chamfered-bore solid cases red and no derive case | REQ-defaults-off-regression | Deliberately fails 32 cases, so it cannot live in the suite; the 07-02 guard now makes the production path raise instead, so this stays a one-off proof that the oracle has teeth | `.venv/bin/python -c "import sys, pytest, spur.model as m; m._bore_rim_edges = lambda *a, **k: []; sys.exit(pytest.main(['tests/regression/test_pre_v0_2.py', '-q', '-p', 'no:cacheprovider']))"` — expect `32 failed, 53 passed`; then `git status --porcelain -- src tests` must be empty. Re-run 2026-10-05: `32 failed, 53 passed in 13.81s`, tree clean |

---

## Reconstruction Notes

Drift between phase close (2026-09-26) and this audit (2026-10-05), none of which
weakens the phase's coverage:

- `test_each_edge_selector_picks_exactly_its_own_edges` grew from 10 to 30 parametrized
  rows: Phases 8-10 added hex, keyway and tip-chamfer rows to the same matrix, and a third
  guarded selector (`Tip chamfer selected no tip-arc edges`) now sits beside the two this
  phase guarded.
- The `must` debt item this phase filed (`2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`)
  is resolved (`839dfea`) and lives in `docs/tech_debt/resolved/`.
- Suite size went from 289 to 929 tests; the fixture's 85 cases are unchanged.

---

## Validation Audit 2026-10-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

## Validation Audit 2026-10-05 (re-run, HEAD `8ae468e`)

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Re-measured, not copied: all eight mapped tests exist (`grep -rl "def <name>" tests/`),
`119 passed in 33.08s`; `tests/regression/pre_v0_2.json` is byte-identical to `540f1a0`;
`## L26` present once; no commit touched `src/`, `tests/`, `Makefile` or `pyproject.toml`
since the first audit's commit `655583f`. One correction: the quick-run command row
previously listed all of `tests/test_calc.py tests/test_model.py` (693 cases, 182.35 s
serial) while claiming the 119-case ~35 s figure; the row now names the eight tests
that figure was measured on.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 65s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-05 (`/gsd-validate-phase 7`, State B reconstruction; every status re-measured). Re-audited 2026-10-05 (State A, HEAD `8ae468e`): 0 gaps, quick-run row corrected.
