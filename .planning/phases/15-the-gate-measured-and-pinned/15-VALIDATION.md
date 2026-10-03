---
phase: "15"
slug: "the-gate-measured-and-pinned"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-03"
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

Source: `15-RESEARCH.md` § Validation Architecture. This phase ships configuration and a
measurement record, not product behaviour, so most proofs are commands whose output is
checked, not new pytest tests. Do not add a test that pins the `fail_under` literal — it
would restate the config and fail on every legitimate re-pin.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (installed); `pytest-xdist` 3.8.0 and `pytest-cov` 7.1.0 after the `[dev]` edit |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (untouched) and `[tool.coverage.*]` |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_pr_land.py tests/test_bench.py -q --no-cov -n0"` |
| **Full suite command** | `make verify` (ends with `927 passed` unless a test-count change is named) |
| **Estimated runtime** | ~193 s serial (CI run 37116412012); ~4 min via the pre-commit hook on the dev host today; 83–93 s at `-n 4` in scratch runs |

---

## Sampling Rate

- **After every task commit:** the pre-commit hook runs `make verify` itself (plain `git commit`, D-21); run the quick command above while iterating
- **After every plan wave:** `make verify`, state the command and the result line in the reply (CLAUDE.md)
- **Before `/gsd-verify-work`:** `make verify` green; the three D-05 tolerance runs; the CI run URL; `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src`
- **Max feedback latency:** ~240 s (one hook run on the dev host before the bar lands)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | REQ-verify-profiled | — | N/A | structural | *(filled from PLAN.md `<verify>` blocks by validate-phase)* | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement → proof map (from research):

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REQ-verify-profiled | RESULTS section has the per-stage, per-file, top-N, sweep {2,4,8,12}, three tolerance rows, cost rows, host-state header | structural | `grep -nE '^(##|###) ' bench/RESULTS.md \| tail -20`; every full-run row says `927 passed` |
| REQ-verify-profiled | xdist tolerance is measured | measurement | three consecutive `make verify` runs at the chosen N, each `927 passed`, exit 0, zero reruns |
| REQ-verify-at-the-bar | wall time at or under the bar, same method | measurement | `/usr/bin/time -p make verify` alternating A/B, `sysctl -n vm.loadavg` before each; `mean(B) <= bar` |
| REQ-verify-at-the-bar | runtime closure untouched | diff | `git diff --exit-code 20cd484 -- requirements.txt` |
| REQ-verify-at-the-bar | hook comment corrected | grep | `git grep -n '~11' -- ':!bench/RESULTS.md' ':!docs/architecture/decision_log.md' ':!.planning/codebase'` returns only D-19 sites |
| REQ-coverage-floor | `pytest-cov` in `[dev]`; floor in config | grep | `grep -n 'pytest-cov\|fail_under\|precision' pyproject.toml` |
| REQ-coverage-floor | worker lines counted | run | `make test PYTEST_ARGS="tests/test_pool.py --cov-report=term-missing:skip-covered -q"` — `pool.py` absent from skip-covered list or without 50, 63-67 |
| REQ-coverage-floor | gate goes red below the floor | run | `make verify PYTEST_ARGS="--ignore=tests/test_cli.py"` exits non-zero with `Coverage failure` (recorded, not committed) |
| REQ-coverage-floor | `.coverage*` ignored | grep | `git check-ignore .coverage .coverage.host.1.x` prints both |
| REQ-ci-installs-the-pinned-kernel | the pair on CI | CI log | `gh run view <id> --log \| grep -E 'cadquery 2.8.0 cadquery-ocp 7.9.3.1.1'` |
| REQ-ci-installs-the-pinned-kernel | tripwire stays | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_run_uses -q` |
| REQ-ci-installs-the-pinned-kernel | ci.yml edit keeps required jobs | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/test_pr_land.py -q` |
| SC5 / D-18 | both debt files retired | grep | `grep -c 'active/2026-09-21-no-coverage-floor\|active/2026-09-26-ci-resolves' docs/tech_debt/INDEX.md` equals 0 |
| Whole phase | fixture and `src/` byte-unchanged (D-20) | diff | `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src` |

---

## Wave 0 Requirements

- [ ] `pyproject.toml` `[dev]` gains `pytest-xdist>=3.8`, `pytest-cov>=7.1`, then one `make` to install them (neither is in `.venv` today) — blocks the sweep, belongs in plan 1 with the profile
- [ ] `.gitignore` gains `.coverage*` — before the first `--cov` run lands on a commit
- [ ] No new test files or fixtures. Existing tests cover the touched seams: `tests/test_pr_land.py` (ci.yml parser), `tests/regression/test_pre_v0_2.py` (the tripwire), `tests/test_pool.py` (worker-coverage proof)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CI resolves `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` on the Linux runner | REQ-ci-installs-the-pinned-kernel | the run exists only after a push; the local dry-run is a simulation of linux/x86_64 | push the branch; `gh run view <id> --log`; record the URL in L34 and the retired debt file (D-16) |
| The bar is read at or under on the dev host | REQ-verify-at-the-bar | load-dependent timing; the human sets the number at the D-01 checkpoint | alternate A/B `make verify` runs in one session with load recorded (D-04); before/after rows in `bench/RESULTS.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
