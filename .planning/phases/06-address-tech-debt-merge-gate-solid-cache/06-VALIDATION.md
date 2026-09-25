---
phase: "06"
slug: "address-tech-debt-merge-gate-solid-cache"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| — | — | — | D-02 | — | A token below a git-shaped cut line is refused regardless of `GIT_EDITOR` | unit | `.venv/bin/python -m pytest tests/test_skip_tokens.py -q` | ✅ | ⬜ pending |
| — | — | — | D-03 | — | Refusal names the token, the line, and the `-v` caveat | unit | `.venv/bin/python -m pytest tests/test_skip_tokens.py -q` | ✅ | ⬜ pending |
| — | — | — | D-04 | — | A run whose `conclusion` is not `success` is refused even when every listed job is green | unit | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | ✅ | ⬜ pending |
| — | — | — | D-05 | — | A `jobs.<id>.name` override in an in-memory `ci.yml` moves the derived required set | unit | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | ✅ | ⬜ pending |
| — | — | — | D-06 | — | Step 5 reports one of three observed outcomes, never a blamed token it did not see | unit | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | ✅ | ⬜ pending |
| — | — | — | D-08 | — | `.BoundingBox().zlen == approx(face_width)` on the cached solid after preview + fine export; export content-equivalent (triangle count, decoded volume, watertight shell) | unit | `.venv/bin/python -m pytest tests/test_model.py -q` | ✅ | ⬜ pending |
| — | — | — | D-09 | — | Suite green with `tests/conftest.py::_reset_solid_cache` deleted | suite | `make verify` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — every task extends `tests/test_skip_tokens.py`, `tests/test_pr_land.py` or `tests/test_model.py`; no new test file, no framework install.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-08 copy-vs-strip timings are recorded, not asserted | D-08 | A timing is a measurement to write down (CLAUDE.md), not a pass/fail bound | Confirm the numbers from 06-RESEARCH.md (copy 23.1 / 70.9 / 260.9 / 824.2 ms; Clean_s 20.2 / 63.1 / 244.9 / 791.3 ms) are carried into the plan's SUMMARY or `bench/RESULTS.md` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
