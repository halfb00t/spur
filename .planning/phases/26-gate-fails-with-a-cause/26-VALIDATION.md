---
phase: "26"
slug: "gate-fails-with-a-cause"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-15"
---

# Phase 26 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `26-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `filterwarnings = error`) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q -p no:cacheprovider` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick ~1 s; `tests/test_pool.py` ~20 s; browser file ~45 s; `make verify` under L43's 300 s bar |

---

## Sampling Rate

- **After every task commit:** quick command for the touched file (`tests/test_hooks.py`, `tests/test_pool.py -n0 --no-cov`, or `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py --no-cov -q"`)
- **After every plan wave:** `make verify`, result line recorded
- **Before `/gsd-verify-work`:** `make verify` green; `git diff --exit-code v0.5 -- tests/regression/` empty; `git diff v0.5 -- src/spur/pool.py` empty; no `filterwarnings` line changed
- **Max feedback latency:** 60 seconds per task (excluding `make verify`, `make test-image` and acceptance runs)

---

## Per-Task Verification Map

Filled by the planner per task. Requirement → guard map:

| Requirement | Test Type | Automated Command | Red looks like | File Exists |
|-------------|-----------|-------------------|----------------|-------------|
| REQ-hook-pin-ignores-caller-args | unit | `PYTEST_ARGS="--ignore=tests/test_browser.py" .venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q` and `make test PYTEST_ARGS="--ignore=tests/test_browser.py tests/test_hooks.py -n0 --no-cov -q"` | assertion at `tests/test_hooks.py:120` with `PYTEST_ARGS` set | ❌ W0 (new tests) |
| REQ-twin-selectors-race-fixed | browser integration | `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py --no-cov -q"` | `AssertionError: twin selectors: 1 request(s) sent by two pending picks` | ✅ (edit in place) |
| REQ-tracker-flake-fixed-from-repro | integration (subprocess) | `.venv/bin/python -m pytest tests/test_pool.py -n0 --no-cov -q -k forced_gc` | subprocess exit 1, `FAILED ...test_a_closed_pool_never_builds_a_replacement_worker`, `ResourceTracker called reentrantly` | ❌ W0 (new test) |
| REQ-hang-leaves-evidence | pin + manual throwaway | `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q` (pin on `-v`/`--durations` in `test` recipe only) | `-v` missing from `test`, or present in `test.fast` | ❌ W0 (pin) |
| REQ-test-image-runs-what-it-claims | integration (Docker) | `make test-image` | non-zero exit; collection error; pin mismatch on mounts/`PYTHONPATH`/`--ignore` | ✅ (pin extended) |
| REQ-ubuntu26-preclassified | manual (CI, human push) | `gh run view <id> --log` per job | record missing from `bench/RESULTS.md` | n/a |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New env-form and command-line-form tests in `tests/test_hooks.py` — red first, both shapes
- [ ] Forced-GC subprocess gate test in `tests/test_pool.py` — red first against the unfixed file
- [ ] `investigation/` directory under the phase for stall, test-image, CI and acceptance logs
- [ ] Committed acceptance protocol (cap, arms, stop rule) before the first interleaved run
- Framework install: none

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Stalled test names itself | REQ-hang-leaves-evidence | the stall test is a throwaway, never committed (D-08) | temp `tests/test_zz_stall_probe.py`, `make test PYTEST_ARGS="tests/test_zz_stall_probe.py -o faulthandler_timeout=5 --cov-fail-under=0"`, keep log under `investigation/`, quote in `bench/RESULTS.md`, delete the file |
| Ubuntu 26 jobs classified | REQ-ubuntu26-preclassified | human pushes the throwaway PR (D-15) | `gh run view --log` per job; `Image:` line + result into `bench/RESULTS.md` |
| CI `--durations` confirms timeout | REQ-hang-leaves-evidence | needs the phase's first CI run (D-07) | read CI `--durations`; change 120 s only if slowest × 2 > 120 |
| Post-merge `main` green | REQ-twin-selectors-race-fixed | needs merge to `main` (D-05) | record first post-merge `main` run id and result |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
