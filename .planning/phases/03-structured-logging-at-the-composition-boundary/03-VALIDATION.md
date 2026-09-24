---
phase: "3"
slug: "structured-logging-at-the-composition-boundary"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-24"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ (`pyproject.toml` `dev` extra `pytest>=8`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `filterwarnings = ["error", ...]` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | ~30 seconds for pytest alone (76 tests, 29.02s measured in research); `make verify` adds ruff, mypy `--strict`, import-linter and the unfinished-work scan |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {filled by planner from PLAN.md tasks} | | | REQ-structured-logging | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_<new logging module>.py` — JSON formatter round-trip test (`json.loads` on an emitted record proves `extra` fields survive) and `SPUR_LOG_LEVEL` parsing tests — new file; no logging module exists yet.
- [ ] Every D-16 branch test (`build.started`, `build.failed`, `export.served`, `queue.refused`, `worker.replaced`) needs `caplog.set_level(logging.INFO)` — `caplog` defaults to WARNING (reproduced in research); the suite has zero `caplog` precedent today.
- [ ] `calc.py` stays log-free — one-line negative assertion (no `import logging` in `src/spur/calc.py`), cheap insurance against drift.
- No framework install needed — pytest's `caplog` fixture is built in.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
