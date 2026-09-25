# Phase 2: CAD Off the Event Loop - Context

**Gathered:** 2026-09-22
**Status:** Ready for planning

<domain>
## Phase Boundary

CAD kernel work moves out of the request-serving process into worker processes, and the
memory ceiling of the resulting multi-process topology is **measured**, not derived from
L07's per-process numbers. Two superseding entries land in
`docs/architecture/decision_log.md` (L06, L07), and
`docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` is resolved and moved
in the same commit as the fix.

Requirements: REQ-cad-off-event-loop, REQ-measured-memory-ceiling.

Not in this phase: any new gear geometry; structured logging (Phase 3); the typed
`DerivedDimensions` contract (Phase 4); CI observation (Phase 5); server-side cancellation
(`nice` debt, its own trigger is "after the process pool lands" — so it follows this, it is
not part of it).

</domain>

<decisions>
## Implementation Decisions

### Pool topology

- **D-01:** One server process, N builders. `compose.yaml` drops to `SPUR_WORKERS: "1"`;
  a new `SPUR_BUILD_WORKERS` sizes the CAD pool. Serving is pure I/O once builds leave it,
  so process count and cache count move together on one knob — the memory sweep has one
  variable, not two multiplied.
- **D-02:** Hard split: the serving process never imports the CAD kernel. `app.py` stops
  importing `model.py`; `BuildError` moves to a kernel-free module so the web layer can
  still name it. A new import-linter contract forbids `spur.app` → `cadquery`/`OCP`
  **including indirectly** (`allow_indirect_imports = false`), so the boundary is enforced
  rather than reviewed. — **Reversibility:** costly — undoing it means moving `BuildError`
  back, re-entangling `app.py` with `model.py`, and deleting a contract; every memory
  number this phase records assumes a kernel-free parent.
- **D-03:** `concurrent.futures.ProcessPoolExecutor`, driven from the async endpoint via
  `loop.run_in_executor`. `mp_context = spawn` (portable, and with D-02 the parent has no
  OCP to fork); `initializer` imports `cadquery`/`model` to pre-warm; `max_tasks_per_child`
  available as the recycling lever (see D-11). Stdlib only — no new dependency, no
  hand-rolled IPC.
- **D-04:** Pool comes up eagerly in the FastAPI lifespan, initializer importing only (no
  warm build). The memory sweep then measures steady state from t=0 instead of a ramp.

### Cache and process boundary

- **D-05:** The function that crosses the boundary is `export(params, fmt, quality) ->
  bytes`. The solid is built, cached and exported entirely inside the worker; no `cq.Solid`
  is ever pickled, and vendor types still stop at `model.py`. — **Reversibility:** costly —
  this is the worker protocol; changing it later re-plumbs both caches and the worker-side
  entry point.
- **D-06:** Cache placement: the exported-bytes cache (`_BlobCache`, 64 MB) moves into the
  serving process, keyed on `(params, fmt, quality)`; the solid `lru_cache` stays per
  worker. A repeat download never crosses the boundary and never wakes a worker; there is
  one byte cache instead of N. The superseding L07 formula therefore reads: *parent byte
  budget + N × solid cache*.
- **D-07:** Routing has affinity: N single-worker executors indexed by a hash of the
  `GearParams`, not one N-worker pool. The UI's preview STL → fine STL → STEP are three
  byte-cache keys but one solid, so affinity preserves build-once-export-three-times and
  stops the same ~280 MiB solid becoming resident in N workers. Accepted cost: no work
  stealing — a hot gear serialises, which is what it does today.
- **D-08:** `_LOCK` in `model.py` stays. It is uncontended under one-task-per-worker, costs
  nothing measurable, and still guards OCCT's process-global state against a future
  in-process thread. The superseding L06 entry retires the *consequence* ("concurrency buys
  latency, not throughput") — now false — not the lock.

### Behaviour under load

- **D-09:** `MAX_QUEUED_BUILDS` is derived from `SPUR_BUILD_WORKERS` (workers plus a
  shallow queue, ~2×N) instead of the absolute 4. Still a bounded semaphore, still
  non-blocking acquire → `503` + `Retry-After`; env override kept. One knob moves both, so
  a deployer cannot configure a queue deeper than the pool can drain. L04 is untouched:
  admission control stays in the web layer, the CLI still never queues.
- **D-10:** Per-build timeout (`SPUR_BUILD_TIMEOUT`), set **above the worst measured
  build**, not picked. On expiry: terminate that worker, recreate its executor, refuse the
  request. This exists because D-07's affinity makes a wedged worker fatal to 1/N of the
  parameter space.
- **D-11:** Worker memory hygiene: keep `malloc_trim(0)` per worker (it is the measured
  win). Enable `max_tasks_per_child` **only if** the sweep shows drift that trim does not
  flatten — and record which way it went, with the numbers, in the superseding L07 entry.
  Recycling otherwise costs a respawn plus a `cadquery` import and wipes the solid cache
  D-07 exists to keep warm.
- **D-12:** Failure modes map to status codes: `BuildError` → `422` (unchanged, the kernel
  refused these parameters); `BrokenProcessPool` → `503` + `Retry-After` with its own
  `type`, matching the existing `busy` detail shape; timeout → `503` + `Retry-After` too.
  A timeout is explicitly **not** a `422` — the same gear succeeds on faster hardware, so
  it is not a property of the parameters. — **Reversibility:** costly — these are published
  API error shapes the web UI reads; changing them later is a client-visible break.
- **D-13:** `/api/health` gains pool state, from **parent-local counters only**: live
  executors, current semaphore value, workers replaced since start. No IPC, no lock, no
  await on a worker — O(1) attribute reads, so the endpoint whose p95 is this phase's
  success criterion still measures the event loop and not the pool. — **Reversibility:**
  one-way — it is a published response contract; the web UI and Phase 4's
  `DerivedDimensions`/OpenAPI work inherit the new fields, and removing a field later
  breaks any client that read it.
- **D-14:** Dockerfile `HEALTHCHECK --timeout` drops from 10 s to ~5 s, **set from the
  measured under-load p95** rather than reverted by reflex, with the comment rewritten to
  cite the new number. That comment currently asserts a stall this phase removes; if the
  timeout still has to be 10 s, the phase did not land. `--start-period=30s` stays unless
  the eager-startup measurement (D-04) says otherwise.
- **D-15:** Test strategy: the build backend is injectable, so most API tests run the
  export inline in-process (fast, and the same code path the CLI takes), plus **one** real
  end-to-end test that spawns a worker and downloads bytes. `make verify` stays near its
  ~11 s warm budget while the process boundary is still proven by the gate.

### Measurement (the part the success criteria rest on)

- **D-16:** The harness is committed and rerunnable, wired to a `make` target (`make
  bench`), running both of the debt file's scenarios and the memory sweep. It is **not**
  part of `make verify` — it needs a running service and minutes, and a latency assertion
  on shared hardware would flap and get ignored. The point is that the claim stays
  falsifiable by whoever doubts it later.
- **D-17:** Two environments, deliberately: **latency on the host** (`make serve`), the way
  the 0.22 s → 0.76 s → 2.00 s baseline was produced, so old and new numbers are
  like-for-like; **memory in the container** (`docker compose up`), because `mem_limit` is a
  container setting and must be measured under the container's accounting. CPU count, arch
  and RAM are recorded alongside every number.
- **D-18:** The sweep varies worker count (N = 1, 2, 4) over L07's own corpus — 40 distinct
  160–199 tooth gears — recording peak container memory per N. `mem_limit` is set from the
  shipping default's peak plus a **named** headroom, then confirmed by re-running the
  corpus at that limit and requiring zero failures — the same way 2g was earned. The per-N
  table ships too, so `compose.yaml`'s "raise it if you raise the workers" finally has
  numbers behind it.
- **D-19:** `SPUR_BUILD_WORKERS` defaults to a fixed **2**, justified by the per-N table
  rather than inherited from today's `SPUR_WORKERS: "2"`. Not derived from `cpu_count`:
  that would make the memory ceiling machine-dependent, and `mem_limit` is one number that
  has to be true everywhere (same reasoning L05 protects for parameter defaults).
- **D-20:** Two decision-log entries, numbers inline. **L17 supersedes L07** — the new
  cache/memory formula (parent byte budget + N × solid cache), the per-N peak table, the
  confirmed `mem_limit`. **L18 supersedes L06** — the lock stays, its consequence does not.
  Each dated, each stating what it supersedes, neither edited in place; the numbers live in
  the entry so the claim and its evidence cannot drift apart. — **Reversibility:** one-way
  — `docs/architecture/decision_log.md` is append-only by policy; a wrong entry is
  superseded by a further entry, never rewritten.

### Claude's Discretion

Decided by the planner/executor, not by the human — but do not drop them:

- The name and placement of the kernel-free boundary module that owns the pool, and where
  `BuildError` lands (D-02). It must be importable by `app.py` without pulling in
  `cadquery`.
- The bench harness's location (`bench/` vs `docker/`) and its output format, given D-16.
- The literal values of `SPUR_BUILD_TIMEOUT` (D-10) and the `mem_limit` headroom factor
  (D-18) — both are set *from* the measurement; only the rule is fixed here.
- Whether `docs/architecture/overview.md` and `docs/architecture/packaging.md` need updating
  for the new topology, and how the debt-file resolution (`Status: resolved`, sha, `git mv`,
  INDEX row) is sequenced against the code commits. Not discussed; CLAUDE.md already
  requires the debt move to land in the same commit as the fix.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The debt this phase retires
- `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` — the baseline
  numbers (0.22 s → 0.76 s → 2.00 s; >5 s under ten concurrent builds, 12-core machine),
  the two load scenarios this phase must repeat, and the "next step" this phase executes.
  Must end the phase `Status: resolved`, sha recorded, `git mv`'d to
  `docs/tech_debt/resolved/`, row moved in `docs/tech_debt/INDEX.md`.
- `docs/tech_debt/INDEX.md` — the row that moves with it.
- `docs/tech_debt/active/2026-09-21-no-server-side-cancellation.md` — *not* in scope; its
  own trigger is "after the process pool lands", so this phase unblocks it and leaves it.

### Locked decisions
- `docs/architecture/decision_log.md` — L04 (admission control belongs to the web layer),
  L06 (one lock; to be superseded), L07 (bounded caches + `malloc_trim`, the 1.87 GiB →
  358 MiB measurement; to be superseded), L08 (no number is better than a wrong number),
  L13 (`make verify` is the gate). Append-only: supersede, never edit in place.
- `CLAUDE.md` / `AGENTS.md` — the two standing rules, the gate, the debt-file lifecycle.
- `docs/CODING_VALUES.md` — read before writing code.

### Architecture
- `docs/architecture/overview.md` — the system map the new topology changes.
- `docs/architecture/packaging.md` — image and compose story that `mem_limit`,
  `SPUR_WORKERS` and the HEALTHCHECK live in.
- `docs/architecture/http-api.md` — the error/response contract D-12 and D-13 touch.

### Code this phase edits
- `src/spur/app.py` — `_build_slot`, `BUILD_QUEUE`/`MAX_QUEUED_BUILDS`, the `model.{stl,step}`
  endpoint, `/api/health`; currently imports `model` (D-02 removes that).
- `src/spur/model.py` — `_LOCK`, `_build_cached` (`SPUR_SOLID_CACHE`), `_BlobCache`
  (`SPUR_EXPORT_CACHE_MB`), `_release_arenas`, `export()`; the worker-side entry point.
- `src/spur/cli.py` — calls `model.export` directly and must keep doing so (L04: the CLI
  never queues and gets no pool).
- `pyproject.toml` `[tool.importlinter]` — the contract D-02 adds/tightens.
- `compose.yaml` — `SPUR_WORKERS`, new `SPUR_BUILD_WORKERS`, `mem_limit` and its comment.
- `Dockerfile` — `HEALTHCHECK --timeout`, `--start-period`, and the comment that asserts the
  stall.
- `tests/test_api.py::test_a_saturated_service_refuses_instead_of_queueing` — reaches into
  `app_module.BUILD_QUEUE` directly; D-09 changes what it is sized from.

### Milestone context
- `.planning/REQUIREMENTS.md` — REQ-cad-off-event-loop, REQ-measured-memory-ceiling and
  their acceptance criteria.
- `.planning/ROADMAP.md` §Phase 2 — the five success criteria.
- `.planning/STATE.md` §Blockers/Concerns — "L07 needs superseding, not rewriting" is named
  there as the largest risk in v0.1.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- `_BlobCache` (`model.py`) already implements a byte-bounded LRU with no lock of its own —
  it moves to the parent process essentially as-is under D-06.
- `_build_slot()` + `BoundedSemaphore` (`app.py`) already produce the exact `503` +
  `Retry-After` detail shape D-12 reuses for the two new refusal modes.
- `int_env()` (`spur/__init__.py`) is the established pattern for every new knob
  (`SPUR_BUILD_WORKERS`, `SPUR_BUILD_TIMEOUT`).
- `docker/smoke.py` already exercises kernel + both exporters + the ASGI app inside the
  image — the natural place to notice a broken pool at build time.

### Established patterns
- Module boundaries are enforced by import-linter contracts, not discipline — D-02's
  contract is the same shape as the existing three.
- Vendor types stop at `model.py`; D-05's bytes-only boundary is that rule holding under a
  process split rather than a new rule.
- Caches are bounded by the resource that actually runs out (entries for solids, bytes for
  exports) and every bound in the tree carries the measurement that set it.
- Comments carry the measurement or constraint that forced the choice — the `mem_limit`,
  `HEALTHCHECK` and `MAX_QUEUED_BUILDS` comments all currently do, and all three become
  false or unjustified in this phase (D-09, D-14, D-18).

### Integration points
- `app.py` → pool: the only place a build is requested over HTTP.
- `cli.py` → `model.export`: unchanged, in-process, no pool, no queue.
- `compose.yaml` + `Dockerfile`: the deployment numbers that the sweep sets.
- `pyproject.toml` contracts + `make verify`: the gate that keeps the split from rotting.

</code_context>

<specifics>
## Specific Ideas

- The baseline to beat is the debt file's own, quoted verbatim: `/api/health` 0.22 s → 0.76 s
  → 2.00 s under one 200-tooth fine build; repeatedly over 5 s under ten concurrent builds;
  12-core machine. The success threshold is a property — p95 under load within **2× of idle
  p95** — with the absolute figures recorded next to it.
- The memory corpus is L07's own: 40 distinct 160–199 tooth gears. Same corpus, so the old
  and new ceilings are comparable.
- `mem_limit` is earned the way 2g was: find what fails, then set above it with named
  headroom, then confirm zero failures at the chosen value.
- If `HEALTHCHECK --timeout` cannot come down from 10 s, treat that as evidence the phase
  did not land, not as a detail to leave alone.

</specifics>

<deferred>
## Deferred Ideas

- **Measure the Raspberry Pi 5 claim, or soften it.** The README advertises a Pi 5 and the
  debt file says the stall is proportionally worse on slow hardware; nothing in this repo
  has ever measured one. File in `docs/ideas/` (`YYYY-MM-DD-measure-or-soften-the-pi5-claim.md`
  + INDEX row); trigger is someone actually running one. Out of scope here — measuring
  hardware nobody has is not a phase deliverable.
- **Server-side cancellation on client abort** — existing `nice` debt whose own trigger is
  "after the process pool lands, which would make real cancellation possible". This phase
  makes it possible; it does not do it.
- **Work stealing / non-affinity fallback routing** (rejected variant of D-07) — revisit only
  with a measurement showing affinity starves throughput under mixed load.
- **Querying workers from `/api/health`** (rejected variant of D-13) — the only way to spot a
  worker that is alive but wedged. Revisit if D-10's timeout proves insufficient; it costs
  IPC behind the measured endpoint.

</deferred>

---

*Phase: 2-CAD Off the Event Loop*
*Context gathered: 2026-09-22*
