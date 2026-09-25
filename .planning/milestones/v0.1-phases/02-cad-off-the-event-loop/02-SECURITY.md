---
phase: "2"
slug: "cad-off-the-event-loop"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 2 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> The register below is the union of the five plans' `<threat_model>` blocks
> (02-01 … 02-05), authored at plan time; this file records what the shipped tree
> does about each entry. Depth is ASVS L1 (grep-level presence checks against named
> files, commits and tests), which is what `workflow.security_asvs_level: 1` asks for.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| HTTP client → `app.py` | Untrusted query parameters; validated once by `GearParams` (L03) and trusted afterwards | gear parameters (public, low sensitivity) |
| `app.py` (parent) → worker process | A `spawn` process boundary; the callable is resolved by qualified name in the child, never unpickled from request data | a pickled, frozen, already-validated `GearParams` plus two `Literal` strings out; STL/STEP bytes back |
| bench harness → running service | A client of the same public HTTP surface any user has; no new boundary | requests and timings |
| `bench/memory.py` → Docker daemon | `docker compose` / `docker inspect` / `docker stats` on the developer's machine | fixed literals and harness-generated integers, as argv |
| `compose.yaml` → container runtime | `mem_limit` is the backstop behind the in-code cache bounds | a measured limit (4g) |
| container runtime → HEALTHCHECK probe | The probe's timeout is the only thing between a legitimately slow response and a restart loop | one `GET /api/health` per 30 s |
| repository history → future agents | The decision log and the debt index are the record later agents treat as settled | append-only entries; `git mv`, never delete |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-02-01 | Denial of Service | `app.py` model endpoint / `BuildPool` | high | mitigate | `MAX_QUEUED_BUILDS = 2 × SPUR_BUILD_WORKERS` (`app.py:92`), `BoundedSemaphore` (`:96`), non-blocking acquire → `503` + `Retry-After` (`:233-240`); `tests/test_api.py::test_a_saturated_service_refuses_instead_of_queueing`, `::test_max_queued_builds_is_derived_from_build_workers`. Its prerequisite, the per-build timeout, is T-02-07 | closed |
| T-02-02 | Tampering | worker boundary (`build_export` pickle payload) | low | accept | See Accepted Risks R-02-01 | closed |
| T-02-03 | Elevation of Privilege | worker process | low | accept | See Accepted Risks R-02-02; premise re-checked: `Dockerfile:33-34` `USER 10001`, `compose.yaml:32-34` `cap_drop: [ALL]`, `no-new-privileges:true`, `read_only: true` | closed |
| T-02-04 | Denial of Service | `bench/latency.py`, `bench/memory.py` | medium | accept | See Accepted Risks R-02-03 | closed |
| T-02-05 | Tampering | `bench/memory.py` → `docker compose` | low | mitigate | Every `subprocess.run` call passes an argument list built from literals and harness-generated values (`bench/memory.py:93, 116, 127, 185, 294`); no `shell=` anywhere in the file | closed |
| T-02-06 | Information Disclosure | `bench/` output | low | accept | See Accepted Risks R-02-04 | closed |
| T-02-07 | Denial of Service | `BuildPool.export` / affinity routing | high | mitigate | `SPUR_BUILD_TIMEOUT` (default 30, `app.py:132`) bounds every build; on overrun the worker is terminated (`pool.py:183-184`) and the slot's executor replaced (`recreate_for`, `pool.py:94`), once per incident; `tests/test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced`, `::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` | closed |
| T-02-08 | Denial of Service | admission semaphore (`BUILD_QUEUE`) | high | mitigate | `_build_slot` releases in `finally` (`app.py:245-247`), so every failure path returns its slot; `tests/test_pool.py::test_each_build_failure_mode_maps_to_its_own_status_and_type` asserts capacity is restored after each of the three failures | closed |
| T-02-09 | Information Disclosure | `/api/health` pool fields | low | accept | See Accepted Risks R-02-05; premise re-checked: `compose.yaml:8` binds `127.0.0.1:8000:8000` | closed |
| T-02-10 | Spoofing | error `detail[].type` values | low | accept | See Accepted Risks R-02-06; `tests/test_pool.py::test_the_four_failure_types_are_pairwise_distinct` pins the closed set | closed |
| T-02-11 | Denial of Service | `compose.yaml` `mem_limit` | high | mitigate | `compose.yaml:26` `mem_limit: 4g`; earned by `bench.memory confirm 4g` over the full 40-gear corpus, 0 of 40 failed (`bench/RESULTS.md:355-358`), with the failing `1g` attempt recorded beside it | closed |
| T-02-12 | Denial of Service | `SPUR_BUILD_TIMEOUT` default | medium | mitigate | Default 30 s (`app.py:132`); slowest build observed across all eight runs is 11.04 s (`bench/RESULTS.md:124`, Run 3 concurrent) — the derivation is in `bench/RESULTS.md` § `SPUR_BUILD_TIMEOUT` (`:271`) | closed |
| T-02-13 | Information Disclosure | `bench/RESULTS.md` | low | accept | See Accepted Risks R-02-07 | closed |
| T-02-14 | Repudiation | measurement provenance | medium | mitigate | `bench/RESULTS.md` opens with a `## Machine` block (`:8-20`) for the one host every run and the sweep used, and states there that the baseline was a different machine so only ratios are comparable; each re-run has its own dated section. 02-04 Task 1's blocking-human quiet-host gate preceded the runs | closed |
| T-02-15 | Denial of Service | Dockerfile HEALTHCHECK | high | mitigate | `Dockerfile:49` `--timeout=2s` set from the measured under-load p95 (0.7–2.3 ms, `bench/RESULTS.md`), inner `urlopen(..., timeout=1)` kept below the outer timeout; container reached healthy under it — `02-UAT.md` test 1 passed 2026-09-24 | closed |
| T-02-16 | Repudiation | `docs/architecture/decision_log.md` | high | mitigate | The only phase-2 commit touching the file is `163a84b`: 151 insertions, 0 deletions (`git log --numstat 31c0bad..HEAD`); L17/L18 supersede L06/L07 without editing them | closed |
| T-02-17 | Repudiation | `docs/tech_debt/` lifecycle | medium | mitigate | `becedc0` records `R063` (a git rename) from `active/` to `resolved/` for `2026-09-21-cad-builds-block-the-event-loop.md`; the file still carries its original problem statement and names both shas | closed |
| T-02-18 | Tampering | measured numbers copied into the decision log | high | mitigate | Every unit-bearing figure in L17/L18 (26 distinct: MiB peaks, ratios, percentages) is found verbatim in `bench/RESULTS.md`; the four the strict grep missed are spacing variants (`292.8s`, `0.5s`, `32.0 GiB`) and one reporting-granularity statement ("~0.1 ms resolution floor") that describes the table's precision rather than transcribing a value | closed |
| T-02-SC | Tampering | npm/pip/cargo installs | high | mitigate | Not applicable: no package was installed in phase 2. `git diff 31c0bad..HEAD -- requirements.txt pyproject.toml` touches only `pyproject.toml`'s import-linter contracts; `requirements.txt` is unchanged | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-02-01 | T-02-02 | Only a closed, already-validated frozen `GearParams` and two `Literal` strings cross the worker boundary; the callable is resolved by qualified name in the child. `spawn` itself rejects lambdas/closures (they do not pickle) | plan author (02-01-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-02 | T-02-03 | Workers inherit the parent's uid 10001 under `cap_drop: ALL` and `no-new-privileges`; `spawn` adds no privilege path | plan author (02-01-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-03 | T-02-04 | The harness saturates a service by design; it is outside `make verify` and CI, and the `503` + `Retry-After` path it trips is the behaviour under test | plan author (02-02-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-04 | T-02-06 | Recorded output is machine facts and timings, committed deliberately as evidence; no credentials or request payloads | plan author (02-02-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-05 | T-02-09 | Worker count, remaining capacity and a replacement counter are operational facts about a service that ships without authentication by design (`REQ-no-auth-default`) and binds to `127.0.0.1`; no per-worker detail | plan author (02-03-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-06 | T-02-10 | The four `detail[].type` values are a closed, documented set carrying no caller-supplied content beyond the kernel's own `BuildError` message, already surfaced before this phase | plan author (02-03-PLAN.md), confirmed by secure-phase | 2026-09-22 |
| R-02-07 | T-02-13 | `bench/RESULTS.md` holds machine facts, durations and byte counts only — the evidence is the point (D-16) | plan author (02-04-PLAN.md), confirmed by secure-phase | 2026-09-22 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 19 | 19 | 0 | `/gsd-secure-phase 2` orchestrator, L1 grep depth; no auditor spawned (plan-authored register, `threats_open: 0`, ASVS 1 short-circuit) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
