---
phase: "2"
slug: "cad-off-the-event-loop"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-22"
validated: "2026-09-24"
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
| T1 One STL built in another process | 02-01 | 1 | REQ-cad-off-event-loop | T-02-02 | Only a validated, frozen `GearParams` crosses the process boundary; the callable is resolved by qualified name in the child | integration (real subprocess) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ❌ new in this task | ✅ `test_pool.py::test_a_real_worker_builds_and_downloads` |
| T2 Byte cache in the parent, queue from the pool | 02-01 | 1 | REQ-cad-off-event-loop | T-02-01 | Queue depth cannot be configured deeper than the pool can drain | unit/integration | `make test PYTEST_ARGS="tests/test_api.py -q"` | ✅ existing file, new cases | ✅ `test_api.py::test_a_second_identical_download_is_served_from_the_byte_cache`, `::test_a_saturated_service_refuses_instead_of_queueing`, `::test_max_queued_builds_is_derived_from_build_workers` |
| T3 The kernel-free contract | 02-01 | 1 | REQ-cad-off-event-loop | T-02-02 | The serving process cannot reach the CAD kernel by any path, enforced not reviewed | import-linter contract + regression test | `make lint-imports` | ❌ new contract | ✅ contract 4 in `pyproject.toml` (`allow_indirect_imports = false`); `test_pool.py::test_executor_processes_attribute_still_exists` |
| T1 Corpus + latency scenarios | 02-02 | 1 | REQ-cad-off-event-loop | T-02-04 | The harness is outside the gate, so its saturating load never runs in CI | CLI smoke + lint/type gate | `.venv/bin/python -m bench.latency --help` | ❌ new | ✅ `--help` run 2026-09-24; `bench/` is inside `mypy src tests docker bench` and `ruff check .` |
| T2 Container memory sweep | 02-02 | 1 | REQ-measured-memory-ceiling | T-02-05 | `docker compose` is invoked as an argument list, never a shell string | CLI smoke + lint/type gate | `.venv/bin/python -m bench.memory --help` | ❌ new | ✅ `--help` run 2026-09-24; `test_bench.py` (3 tests) pins the ceiling cap |
| T3 `make bench` wiring | 02-02 | 1 | REQ-cad-off-event-loop | T-02-04 | `bench` is a sibling of `verify`, never a prerequisite | make-target check | `make -n bench.latency bench.memory bench` | ❌ new | ✅ `make -n` prints both recipes, 2026-09-24 |
| T1 Timeout that stops the build | 02-03 | 2 | REQ-cad-off-event-loop | T-02-07 | A crafted expensive gear costs one build's wall time, not 1/N of the service | integration (real subprocess) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ from 02-01 | ✅ `test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced` |
| T2 Three failure modes, three answers | 02-03 | 2 | REQ-cad-off-event-loop | T-02-08 | Every failure path releases its admission slot; the semaphore cannot drain | contract (injected backend) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ from 02-01 | ✅ `test_pool.py::test_each_build_failure_mode_maps_to_its_own_status_and_type`, `::test_the_four_failure_types_are_pairwise_distinct`, `::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` |
| T3 Decision: `/api/health` field shape | 02-03 | 2 | REQ-cad-off-event-loop | T-02-09 | A published contract is gated before it becomes permanent | checkpoint:decision | n/a — blocking human decision | n/a | ✅ decided — the fields shipped (02-03-SUMMARY D4) |
| T4 Pool state on `/api/health` | 02-03 | 2 | REQ-cad-off-event-loop | T-02-09 | Parent-local counters only: no IPC, no lock, no await on a worker | contract + human check | `make test PYTEST_ARGS="tests/test_pool.py tests/test_api.py -q"` | ✅ from 02-01 | ✅ `test_pool.py::test_health_reports_pool_state`, `::test_health_queue_available_falls_while_a_slot_is_held`, `::test_health_workers_replaced_increases_after_a_forced_termination`, `::test_health_handler_never_awaits_or_touches_pool_internals` |
| T1 Environment gate before measuring | 02-04 | 3 | REQ-cad-off-event-loop | T-02-14 | No number is produced until a human has confirmed a quiet host and a running Docker daemon; an un-quiet machine is recorded as a caveat, never hidden | checkpoint:human-action (`gate="blocking-human"`) | n/a — blocking human action | n/a | ✅ gate passed — the runs it guards are in `bench/RESULTS.md` |
| T2 Re-run both load scenarios | 02-04 | 3 | REQ-cad-off-event-loop | T-02-12, T-02-14 | The build timeout is set above an observed worst build, never a plausible number | manual-only (load harness) + human check | `make bench.latency` then `make verify` | ❌ harness from 02-02 | ⚠️ single ✅ on every recorded run; concurrent not demonstrated on both runs of any session, waived by the human (L18; `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`) |
| T3 Memory sweep and `mem_limit` | 02-04 | 3 | REQ-measured-memory-ceiling | T-02-11, T-02-14 | The chosen limit is confirmed at zero failures over the same 40-gear corpus that earned 2g | manual-only (container sweep) + human check | `docker compose config` then `make verify` | ❌ harness from 02-02 | ✅ manual — sweep in `bench/RESULTS.md`; `compose.yaml:26` `mem_limit: 4g` |
| T4 README + packaging docs | 02-04 | 3 | REQ-measured-memory-ceiling | T-02-13 | Every published number is traceable to `bench/RESULTS.md` | doc assertion | `grep -nE 'SPUR_BUILD_WORKERS\|SPUR_BUILD_TIMEOUT' README.md` | ✅ existing files | ✅ grep 2026-09-24: `README.md:65-83`, `packaging.md:33,82` |
| T1 Decision: append L17 and L18 | 02-05 | 4 | REQ-measured-memory-ceiling | T-02-18 | The last cheap look before a permanent, append-only entry | checkpoint:decision | n/a — blocking human decision | n/a | ✅ decided — L17/L18 appended |
| T2 L17 and L18 | 02-05 | 4 | REQ-measured-memory-ceiling | T-02-16 | L06 and L07 are superseded, never edited: the diff adds lines only | doc assertion + diff gate | `git diff --stat HEAD -- docs/architecture/decision_log.md` | ✅ existing file | ✅ L17 (`decision_log.md:163`), L18 (`:214`), L19 (`:256`) |
| T3 Healthcheck down, debt resolved | 02-05 | 4 | REQ-cad-off-event-loop | T-02-15, T-02-17 | A `git mv`, never a delete; the container is actually built and run | container gate + git assertions | `make check` | ✅ existing files | ✅ `Dockerfile:49` `--timeout=2s`; debt file under `resolved/` names daeb284; UAT test 1 passed 2026-09-24 |
| T4 Redraw the system map | 02-05 | 4 | REQ-cad-off-event-loop | — | The three architecture documents tell one story | doc assertion | `grep -nE 'pool\.py\|build pool\|worker process' docs/architecture/overview.md` | ✅ existing file | ✅ `overview.md:34` build-pool row; UAT test 2 passed 2026-09-24 |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Every item below is now owned by a plan task; none is left for execution to improvise.

- [x] Kernel-free `BuildError` module (D-02) — so `app.py` can catch build failures without importing `cadquery`. **Owner: 02-01 Task 1** (also adds `BuildTimeout`, because `asyncio.TimeoutError` is not the builtin `TimeoutError` on the 3.10 floor CI runs)
- [x] New import-linter contract in `pyproject.toml`: `spur.app` forbidden from `cadquery`/`OCP`, `allow_indirect_imports = false`. **Owner: 02-01 Task 3**
- [x] The one real end-to-end test (D-15), opened with `with TestClient(app) as client:` (lifespan does not run otherwise). **Owner: 02-01 Task 1**, as `tests/test_pool.py::test_a_real_worker_builds_and_downloads` — placed in a new module rather than `tests/test_api.py`, so the module-scoped inline-backend fixture that keeps the 12 existing API tests pool-independent does not also neutralise the one test that must cross the boundary
- [x] The injectable build backend itself (D-15), hard-failing rather than falling back to inline when no pool started. **Owner: 02-01 Task 1**
- [x] Tests for the three D-12 failure-mode → status-code mappings (`BuildError` → 422, `BrokenProcessPool` → 503, timeout → 503). **Owner: 02-03 Task 2**
- [x] Load/memory harness + `make bench` target (D-16): both load scenarios and the N=1,2,4 memory sweep over the existing 40-gear corpus (reuse `docs/plan-2026-09-21.md` F2 methodology). **Owner: 02-02 Tasks 1-3**; run by **02-04 Tasks 2-3**
- [x] Regression test asserting the `ProcessPoolExecutor` instance's `_processes` mapping exists, so a future CPython silently breaking D-10's termination path fails `make verify` loudly. **Owner: 02-01 Task 3** (deliberately landed one wave *before* the timeout path that depends on it)

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

**Approval:** validated 2026-09-24 by `/gsd-validate-phase 2` — the per-task map above was checked row by row against the shipped tests, contracts and documents (see the audit below).

---

## Validation Audit 2026-09-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Evidence, in the order the map lists it:

- `make verify` green at `6722cb3` (the pre-commit hook of the UAT commit ran it: ruff,
  mypy `--strict` over `src tests docker bench`, the four import-linter contracts, the
  unfinished-work scan, pytest — 59 test functions in six modules, 76 collected items once parametrised).
- Every automated row names a test or contract that exists in the tree today; the names in
  the Status column are the ones `pytest --collect-only` reports.
- The doc-assertion rows (02-04 T4, 02-05 T2/T4) and the CLI-smoke rows (02-02 T1-T3) were
  re-run this session with the exact commands the map lists.
- Manual-only rows are manual by design and recorded in `bench/RESULTS.md` (eight runs,
  four sessions). One caveat stands and is not hidden: the concurrent latency scenario never
  met the 2x bar on both runs of one session and was waived by the human (L18; must-severity
  debt `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`).
- The two `<human-check>` rows deferred to end of phase (02-05 T3, T4) passed in
  `02-UAT.md` on 2026-09-24.
- No tests were generated: nothing was missing.
