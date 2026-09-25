---
phase: "06"
slug: "address-tech-debt-merge-gate-solid-cache"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-25"
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml`, `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_skip_tokens.py tests/test_pr_land.py tests/test_model.py -q` (from the repo root — `test_skip_tokens.py` and `test_pr_land.py` need it for `sys.path` to resolve `scripts`) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | ~11 s warm (`docs/HOW_TO_DEVELOP.md` §0); ~45 s when run as the pre-commit hook (06-CONTEXT.md) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command, scoped to the touched test file
- **After every plan wave:** Run `make verify` — mandatory for D-09, whose proof is suite-wide (the `test_model.py` × `test_api.py` cache collision), not single-file
- **Before `/gsd-verify-work`:** Full suite must be green; each of the five debt files must show `Status: resolved`, be `git mv`'d into `docs/tech_debt/resolved/`, with its INDEX row moved, in the same commit as its fix (CLAUDE.md, D-01)
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Seeded from 06-RESEARCH.md § Validation Architecture before plans exist. Task ID / Plan / Wave are assigned by the PLAN.md files; the requirement column carries the CONTEXT.md decision id because this phase has no REQ-IDs.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01 T1 | 06-01 | 1 | D-08 | T-06-01 | `.BoundingBox().zlen == approx(face_width)` on the cached solid after preview + fine + STEP export; every STL export content-equivalent to a first in-place export (triangle count, decoded volume, closed shell) -- a preview after fine is 9,066 triangles, not 46,278 | unit + public-doorway one-liner | `make test PYTEST_ARGS="tests/test_model.py -q"` | ✅ | ✅ green |
| 06-01 T1 | 06-01 | 1 | D-09 | — | Suite green with `tests/conftest.py::_reset_solid_cache` deleted | suite | `make verify` | ✅ | ✅ green |
| 06-02 T1 | 06-02 | 2 | D-02 | T-06-04 | A token below a git-shaped cut line is refused regardless of `GIT_EDITOR`; a real editor-session commit is refused in a scratch clone | unit + scratch-clone git probe | `make test PYTEST_ARGS="tests/test_skip_tokens.py -q"` | ✅ | ✅ green |
| 06-02 T1, T2 | 06-02 | 2 | D-03 | T-06-05 | Refusal names the token, the line, and `commit without -v`; §6 carries the same line in Russian | unit + pre-commit commit-msg run + doc grep | `make test PYTEST_ARGS="tests/test_skip_tokens.py -q"` | ✅ | ✅ green |
| 06-03 T1 | 06-03 | 3 | D-04 | T-06-07 | A run whose `conclusion` is not `success` is refused even when every listed job is green; live `check_head` on run 36116930241 gives three refusals | unit + live read-only probe | `make test PYTEST_ARGS="tests/test_pr_land.py -q"` | ✅ | ✅ green |
| 06-03 T2 | 06-03 | 3 | D-05 | T-06-09 | A `jobs.<id>.name` override in an in-memory `ci.yml` moves the derived required set | unit | `make test PYTEST_ARGS="tests/test_pr_land.py -q -k job_name"` | ✅ | ✅ green |
| 06-04 T1 | 06-04 | 4 | D-06 | T-06-10 | Step 5 reports one of three observed outcomes, never a blamed token it did not see; live `no_run_report` on `b72b0e1` and `20b63e4` | unit + live read-only probe | `make test PYTEST_ARGS="tests/test_pr_land.py -q"` | ✅ | ✅ green |
| 06-04 T2 | 06-04 | 4 | D-07 | T-06-13 | Docstring and §8 state the split; the commit changes no code in `scripts/pr_land.py` (AST compare) | grep + AST gate | `grep -qF 'pins the head, not the base' scripts/pr_land.py` | ✅ | ✅ green |
| 06-01 T2, 06-04 T2 | 06-01, 06-04 | 1, 4 | D-10 | — | L24 and L25 appended after L23; no line of the log removed | grep + numstat | `grep -n '^## L2[2-5] ' docs/architecture/decision_log.md` | ✅ | ✅ green |
| 06-04 T3 | 06-04 | 4 | D-11 | — | STATE.md cites run 36122394253; only the Phase 2 concern stays open | grep | `grep -qF 'actions/runs/36122394253' .planning/STATE.md` | ✅ | ✅ green |
| 06-01 T2, 06-02 T2, 06-03 T3, 06-04 T2 | all | 1-4 | D-01 | T-06-03 | Each debt file `Status: resolved`, `Resolved in:` = the commit that changed its fix file, moved with its INDEX row in the commit that completes the fix | git proof (each plan's retirement `<verify>`) | see each plan's retirement task | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — every task extends `tests/test_skip_tokens.py`, `tests/test_pr_land.py` or `tests/test_model.py`; no new test file, no framework install.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-08 copy-vs-strip timings are recorded, not asserted | D-08 | A timing is a measurement to write down (CLAUDE.md), not a pass/fail bound | Confirm L24 (`docs/architecture/decision_log.md`) and `06-01-SUMMARY.md` carry research's numbers (copy 23.1 / 70.9 / 260.9 / 824.2 ms; Clean_s 20.2 / 63.1 / 244.9 / 791.3 ms), the plan-time in-place vs copy cost (18.7→20.3, 59.6→61.0, 216.0→230.0, 719.2→736.8 ms) and the 200-tooth fine peak RSS; Plan 06-01 Task 2's verify greps for them. `bench/RESULTS.md` is not used: its header scopes it to `make bench.*` harness output |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none — existing files extended)
- [x] No watch-mode flags
- [x] Feedback latency < 60s (`make verify` measured 32–35 s at HEAD)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-09-25 by /gsd-validate-phase (execute-phase verify:post hook), HEAD 5470a29

---

## Validation Audit 2026-09-25

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Audited after all four plans executed (HEAD `5470a29`). Evidence, re-run by the auditor rather
than taken from the SUMMARYs: every one of the 17 test functions the four `coverage:` blocks
name exists in its file (`grep '^def <name>'`); `make verify` exits 0 at HEAD — 191 passed
(three independent runs this session: post-wave gate, regression gate, pre-commit hook); the
D-07 grep + AST gate, the D-10 order check (`L22, L23, L24, L25`; `git show --numstat` reports
0 deletions for `e91d7de`, `f17bda0`, `b72b0e1`), the D-11 STATE.md greps and the five D-01
retirement proofs (`Status: resolved`, `Resolved in:` = `655ec52` / `e46ed34` / `9ca8320` /
`0573319` / `e4345a4`, INDEX row moved) all pass. The manual-only D-08 row stays manual by
design; its seven numbers (824.2, 791.3, 736.8, 719.2, 1270.7, 7.587720608891235, 46,278) are
present in L24. `uat classify-coverage` reports `all_auto_covered: true` for all four SUMMARYs
(18 deliverables, none `human_judgment: true`). No test files generated; no auditor spawned.
