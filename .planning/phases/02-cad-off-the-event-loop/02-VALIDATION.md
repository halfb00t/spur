---
phase: "2"
slug: "cad-off-the-event-loop"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
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
| T1 One STL built in another process | 02-01 | 1 | REQ-cad-off-event-loop | T-02-02 | Only a validated, frozen `GearParams` crosses the process boundary; the callable is resolved by qualified name in the child | integration (real subprocess) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ❌ new in this task | ⬜ |
| T2 Byte cache in the parent, queue from the pool | 02-01 | 1 | REQ-cad-off-event-loop | T-02-01 | Queue depth cannot be configured deeper than the pool can drain | unit/integration | `make test PYTEST_ARGS="tests/test_api.py -q"` | ✅ existing file, new cases | ⬜ |
| T3 The kernel-free contract | 02-01 | 1 | REQ-cad-off-event-loop | T-02-02 | The serving process cannot reach the CAD kernel by any path, enforced not reviewed | import-linter contract + regression test | `make lint-imports` | ❌ new contract | ⬜ |
| T1 Corpus + latency scenarios | 02-02 | 1 | REQ-cad-off-event-loop | T-02-04 | The harness is outside the gate, so its saturating load never runs in CI | CLI smoke + lint/type gate | `.venv/bin/python -m bench.latency --help` | ❌ new | ⬜ |
| T2 Container memory sweep | 02-02 | 1 | REQ-measured-memory-ceiling | T-02-05 | `docker compose` is invoked as an argument list, never a shell string | CLI smoke + lint/type gate | `.venv/bin/python -m bench.memory --help` | ❌ new | ⬜ |
| T3 `make bench` wiring | 02-02 | 1 | REQ-cad-off-event-loop | T-02-04 | `bench` is a sibling of `verify`, never a prerequisite | make-target check | `make -n bench.latency bench.memory bench` | ❌ new | ⬜ |
| T1 Timeout that stops the build | 02-03 | 2 | REQ-cad-off-event-loop | T-02-07 | A crafted expensive gear costs one build's wall time, not 1/N of the service | integration (real subprocess) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ from 02-01 | ⬜ |
| T2 Three failure modes, three answers | 02-03 | 2 | REQ-cad-off-event-loop | T-02-08 | Every failure path releases its admission slot; the semaphore cannot drain | contract (injected backend) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ from 02-01 | ⬜ |
| T3 Decision: `/api/health` field shape | 02-03 | 2 | REQ-cad-off-event-loop | T-02-09 | A published contract is gated before it becomes permanent | checkpoint:decision | n/a — blocking human decision | n/a | ⬜ |
| T4 Pool state on `/api/health` | 02-03 | 2 | REQ-cad-off-event-loop | T-02-09 | Parent-local counters only: no IPC, no lock, no await on a worker | contract + human check | `make test PYTEST_ARGS="tests/test_pool.py tests/test_api.py -q"` | ✅ from 02-01 | ⬜ |
| T1 Environment gate before measuring | 02-04 | 3 | REQ-cad-off-event-loop | T-02-14 | No number is produced until a human has confirmed a quiet host and a running Docker daemon; an un-quiet machine is recorded as a caveat, never hidden | checkpoint:human-action (`gate="blocking-human"`) | n/a — blocking human action | n/a | ⬜ |
| T2 Re-run both load scenarios | 02-04 | 3 | REQ-cad-off-event-loop | T-02-12, T-02-14 | The build timeout is set above an observed worst build, never a plausible number | manual-only (load harness) + human check | `make bench.latency` then `make verify` | ❌ harness from 02-02 | ⬜ |
| T3 Memory sweep and `mem_limit` | 02-04 | 3 | REQ-measured-memory-ceiling | T-02-11, T-02-14 | The chosen limit is confirmed at zero failures over the same 40-gear corpus that earned 2g | manual-only (container sweep) + human check | `docker compose config` then `make verify` | ❌ harness from 02-02 | ⬜ |
| T4 README + packaging docs | 02-04 | 3 | REQ-measured-memory-ceiling | T-02-13 | Every published number is traceable to `bench/RESULTS.md` | doc assertion | `grep -nE 'SPUR_BUILD_WORKERS\|SPUR_BUILD_TIMEOUT' README.md` | ✅ existing files | ⬜ |
| T1 Decision: append L17 and L18 | 02-05 | 4 | REQ-measured-memory-ceiling | T-02-18 | The last cheap look before a permanent, append-only entry | checkpoint:decision | n/a — blocking human decision | n/a | ⬜ |
| T2 L17 and L18 | 02-05 | 4 | REQ-measured-memory-ceiling | T-02-16 | L06 and L07 are superseded, never edited: the diff adds lines only | doc assertion + diff gate | `git diff --stat HEAD -- docs/architecture/decision_log.md` | ✅ existing file | ⬜ |
| T3 Healthcheck down, debt resolved | 02-05 | 4 | REQ-cad-off-event-loop | T-02-15, T-02-17 | A `git mv`, never a delete; the container is actually built and run | container gate + git assertions | `make check` | ✅ existing files | ⬜ |
| T4 Redraw the system map | 02-05 | 4 | REQ-cad-off-event-loop | — | The three architecture documents tell one story | doc assertion | `grep -nE 'pool\.py\|build pool\|worker process' docs/architecture/overview.md` | ✅ existing file | ⬜ |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Every item below is now owned by a plan task; none is left for execution to improvise.

- [ ] Kernel-free `BuildError` module (D-02) — so `app.py` can catch build failures without importing `cadquery`. **Owner: 02-01 Task 1** (also adds `BuildTimeout`, because `asyncio.TimeoutError` is not the builtin `TimeoutError` on the 3.10 floor CI runs)
- [ ] New import-linter contract in `pyproject.toml`: `spur.app` forbidden from `cadquery`/`OCP`, `allow_indirect_imports = false`. **Owner: 02-01 Task 3**
- [ ] The one real end-to-end test (D-15), opened with `with TestClient(app) as client:` (lifespan does not run otherwise). **Owner: 02-01 Task 1**, as `tests/test_pool.py::test_a_real_worker_builds_and_downloads` — placed in a new module rather than `tests/test_api.py`, so the module-scoped inline-backend fixture that keeps the 12 existing API tests pool-independent does not also neutralise the one test that must cross the boundary
- [ ] The injectable build backend itself (D-15), hard-failing rather than falling back to inline when no pool started. **Owner: 02-01 Task 1**
- [ ] Tests for the three D-12 failure-mode → status-code mappings (`BuildError` → 422, `BrokenProcessPool` → 503, timeout → 503). **Owner: 02-03 Task 2**
- [ ] Load/memory harness + `make bench` target (D-16): both load scenarios and the N=1,2,4 memory sweep over the existing 40-gear corpus (reuse `docs/plan-2026-09-21.md` F2 methodology). **Owner: 02-02 Tasks 1-3**; run by **02-04 Tasks 2-3**
- [ ] Regression test asserting the `ProcessPoolExecutor` instance's `_processes` mapping exists, so a future CPython silently breaking D-10's termination path fails `make verify` loudly. **Owner: 02-01 Task 3** (deliberately landed one wave *before* the timeout path that depends on it)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/api/health` p95 within 2× idle p95 under both load scenarios | REQ-cad-off-event-loop | Load harness, not part of `make verify`; needs the real container topology and a quiet machine | `make bench` (D-16); record numbers next to the baseline (0.22 s → 0.76 s → 2.00 s single; >5 s ten concurrent, 12-core) |
| Memory sweep N=1,2,4 over the 40-gear corpus produces a peak-per-N table | REQ-measured-memory-ceiling | Container-side RSS measurement, minutes of wall time | `make bench` memory mode (D-16/D-18) |
| `compose.yaml` `mem_limit` re-run at the chosen value shows zero failures over the corpus | REQ-measured-memory-ceiling | Requires Docker and the sweep | `docker compose up` + sweep at the chosen limit |
| The host was quiet and Docker was up before either measurement ran | REQ-cad-off-event-loop, REQ-measured-memory-ceiling | Claude can read `docker info` and the load average but cannot quiet a machine or start Docker Desktop | 02-04 Task 1 — blocking-human checkpoint; `02-04` is `autonomous: false` for this reason |
| `docs/architecture/decision_log.md` gains two superseding entries for L06 and L07 | REQ-measured-memory-ceiling | Content judgement; each must cite the new measurement | Human review of the two entries |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — every `auto`/`tracer` task in all five plans carries at least one runnable `<automated>` command with a stated `<fails_when>`; the two `checkpoint:decision` tasks and 02-04's `checkpoint:human-action` environment gate are blocking human steps and carry none by design
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — the longest run without one is a single checkpoint task
- [x] Wave 0 covers all MISSING references — each of the seven Wave 0 items above names the plan and task that owns it
- [x] No watch-mode flags — every command is one-shot (`make test`, `make verify`, `make lint-imports`, `make check`, `grep`, `docker compose config`)
- [x] Feedback latency < 15s — `make test PYTEST_ARGS="tests/test_pool.py -q"` and `make lint` are the per-task commands; `make verify` (~11 s warm, L13) is the per-wave one. `make check` and `make bench` are deliberately slower and are used once each, at the points that need them
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending — set `status: validated` once `/gsd-validate-phase` or execution confirms the per-task map against the shipped tests.
