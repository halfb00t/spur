---
phase: "2"
slug: "cad-off-the-event-loop"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-22"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `02-RESEARCH.md` § Validation Architecture; the per-task
> map is filled from the PLAN.md files once they exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pytest>=8` dev extra), `httpx>=0.27` for `TestClient` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `xfail_strict = true`, `filterwarnings = ["error", ...]` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_api.py -q` |
| **Full suite command** | `make verify` (ruff, mypy --strict, import-linter contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | pytest ~11 s warm (L13); `make verify` total not measured in this session |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_api.py -q`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green, plus one manual `make bench` run (D-16)
  producing the numbers success criteria 1–2 require
- **Max feedback latency:** ~15 s (pytest subset); `make verify` per wave

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *(populated from PLAN.md tasks by the planner / validate-phase)* | | | | | | | | | |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Kernel-free `BuildError` module (D-02) — so `app.py` can catch build failures without importing `cadquery`
- [ ] New import-linter contract in `pyproject.toml`: `spur.app` forbidden from `cadquery`/`OCP`, `allow_indirect_imports = false`
- [ ] `tests/test_api.py::test_a_real_worker_builds_and_downloads` — the one real end-to-end test (D-15), opened with `with TestClient(app) as client:` (lifespan does not run otherwise)
- [ ] Tests for the three D-12 failure-mode → status-code mappings (`BuildError` → 422, `BrokenProcessPool` → 503, timeout → 503)
- [ ] Load/memory harness + `make bench` target (D-16): both load scenarios and the N=1,2,4 memory sweep over the existing 40-gear corpus (reuse `docs/plan-2026-09-21.md` F2 methodology)
- [ ] Regression test asserting `hasattr(<ProcessPoolExecutor instance>, "_processes")` so a future CPython silently breaking D-10's termination path fails `make verify` loudly

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/api/health` p95 within 2× idle p95 under both load scenarios | REQ-cad-off-event-loop | Load harness, not part of `make verify`; needs the real container topology and a quiet machine | `make bench` (D-16); record numbers next to the baseline (0.22 s → 0.76 s → 2.00 s single; >5 s ten concurrent, 12-core) |
| Memory sweep N=1,2,4 over the 40-gear corpus produces a peak-per-N table | REQ-measured-memory-ceiling | Container-side RSS measurement, minutes of wall time | `make bench` memory mode (D-16/D-18) |
| `compose.yaml` `mem_limit` re-run at the chosen value shows zero failures over the corpus | REQ-measured-memory-ceiling | Requires Docker and the sweep | `docker compose up` + sweep at the chosen limit |
| `docs/architecture/decision_log.md` gains two superseding entries for L06 and L07 | REQ-measured-memory-ceiling | Content judgement; each must cite the new measurement | Human review of the two entries |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
