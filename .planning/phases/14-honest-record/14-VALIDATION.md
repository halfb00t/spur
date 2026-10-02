---
phase: "14"
slug: "honest-record"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-02"
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `14-RESEARCH.md` "## Validation Architecture". Two of the three
> requirements are test-suite-visible (a new parametrized warning test in `tests/test_calc.py`;
> a tightened shared assertion plus a tripwire in `tests/test_model.py`); the third is prose
> (README bullet and `_outline` docstring) and is reviewed by eye. The Per-Task map is filled
> by the planner and audited by validate-phase.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python 3.12, `.venv`; `pyproject.toml` pins `pytest>=8`; `addopts = "--strict-markers --strict-config"`; no `pytest-xdist`, serial) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `make test PYTEST_ARGS="-k <pattern>"` — or the equivalent `.venv/bin/python -m pytest tests/<file>.py -k <pattern> -q` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | ~218 s wall for `make verify` at 907 tests (Phase 12 measurement, `bench/RESULTS.md`; STATE.md records ~3.5 min as the current baseline) |

---

## Sampling Rate

- **After every task commit:** Run `make test PYTEST_ARGS="-k <the task's test pattern>"` for the file the task changed, plus `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py -q` after any `calc.py` or `model.py` change (byte-unchanged proof, L26)
- **After every plan wave:** Run `make verify` (the pre-commit hook runs it on every `git commit` regardless — D-15)
- **Before `/gsd-verify-work`:** Full suite must be green; `tests/regression/pre_v0_2.json` byte-unchanged
- **Max feedback latency:** ~218 s — `make verify` is the only automated tier the repo has; the quick command is the developer's loop between commits, not a replacement for the hook

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | REQ-root-lead-in-warned | T-14-01 / T-14-02 | the warning names a non-zero 3-dp height or does not print; fixture and params.py byte-unchanged | unit + end-to-end (CLI, `/api/info`) | `.venv/bin/python -m pytest tests/test_calc.py -k root_lead_in -q` ("2 passed"), plus the `spur info` and TestClient one-liners in the plan | ❌ new test (created by this task) | ⬜ pending |
| 14-01-02 | 01 | 1 | REQ-root-lead-in-warned | T-14-01 | 15 rows: debt configurations, three driver pairs, mid-tooth trio, zero fillet, sub-resolution silent row | unit | `.venv/bin/python -m pytest tests/test_calc.py -k root_lead_in -q` ("15 passed") | ✅ (from 14-01-01) | ⬜ pending |
| 14-01-03 | 01 | 1 | REQ-readme-root-zone-states-the-limit | T-14-03 / T-14-02 | README's numbers are tested rows only; model.py change is docstring-only | prose check + AST | the README and model.py `.venv/bin/python -c` checks in the plan; debt-retirement and sha checks | N/A — prose | ⬜ pending |
| 14-02-01 | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-05 | the oracle shares no code with `_fillet_corner`; gaps measured before any tolerance moves | integration (real kernel) | `.venv/bin/python -m pytest tests/test_model.py -k "each_cutout_is_exactly or cutout_proof_fails" -q` ("7 passed"), plus the AST oracle check | ✅ existing tests modified | ⬜ pending |
| 14-02-02 | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-04 | a gap over 1e-9 mm³ stops for the human; the executor never loosens the bar | checkpoint (blocking-human, presented only on a miss) | SUMMARY records "D-06 not reached" or the human's answer | N/A | ⬜ pending |
| 14-02-03 | 02 | 2 | REQ-filleted-spoke-closed-form | T-14-04 / T-14-06 | all four rows at `abs=1e-9`; a 1e-6 mm rim-corner root shift goes red | integration (real kernel) | `.venv/bin/python -m pytest tests/test_model.py -k "each_cutout_is_exactly or cutout_proof_fails" -q` ("8 passed"), plus the bar, debt and D-07 checks | ❌ new tripwire (created by this task) | ⬜ pending |
| 14-03-01 | 03 | 3 | all three | T-14-07 / T-14-08 | decision log append-only; L33's figures and shas come from the record | record check | `git diff --numstat 5d9e907 -- docs/architecture/decision_log.md` (deleted column 0), plus the L33 check | N/A | ⬜ pending |
| 14-03-02 | 03 | 3 | all three | T-14-02 | phase end state: gate green, part unchanged, both debts retired | full gate | `make verify`, plus the src-scope, contract and ledger checks | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. `tests/test_calc.py`'s parametrized
full-string warning rows and `tests/test_model.py`'s shared cutout assertion
(`_assert_the_cutout_is_what_derive_prints`) plus its monkeypatch tripwire shape are the
precedents every new test extends; no new fixture, conftest entry or framework install is
needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README root-fillets bullet (~225–228) and `_outline` docstring (`src/spur/model.py:136–139`) state the real condition and cite the warning | REQ-readme-root-zone-states-the-limit | Prose wording cannot be asserted beyond a grep | Read both sites. Confirm: the condition is stated (below the pitch circle on the default gear; above it when the root fillet exceeds half the dedendum and the profile shift exceeds 0.125), the warning is cited, the only numbers present are ones 14-01's tests prove (the default gear's 1.188 mm; the `(1.25 − x)·m / 2` crossing; the 0.125 mid-tooth floor), and no 35 µm figure appears anywhere in README. |
| D-06 halt: if any cutout row's measured kernel–formula gap exceeds 1e-9 mm³ the executor stops with the per-row numbers | REQ-filleted-spoke-closed-form | A human decides between a formula error and a measured bar; never the executor | Read the checkpoint's table (kernel delta, formula value, gap, kernel pair per row) before choosing. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 220s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
