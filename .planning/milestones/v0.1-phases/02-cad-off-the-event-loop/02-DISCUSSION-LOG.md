# Phase 2: CAD Off the Event Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-22
**Phase:** 2-CAD Off the Event Loop
**Areas discussed:** Pool topology, Cache + boundary, Load behavior, Measurement

---

## Pool topology

### Process layout

| Option | Description | Selected |
|--------|-------------|----------|
| 1 server + N builders | `SPUR_WORKERS=1` in compose, new `SPUR_BUILD_WORKERS` sizes the pool; one knob moves processes and caches together | ✓ |
| 1 server + 1 builder | Full latency decoupling, near-zero memory delta, zero throughput gain | |
| 2 servers + pool each | Keeps compose as-is; 2 + 2N processes, 2N unshared solid caches | |

### What the serving process still imports

| Option | Description | Selected |
|--------|-------------|----------|
| Hard split + contract | `app.py` never reaches `model.py`; `BuildError` moves; import-linter forbids `spur.app` → `cadquery`/`OCP` indirectly | ✓ |
| Hard split, no contract | Same shape, no enforcement — next edit can silently regress the memory result | |
| Keep the import | Smallest diff; OCP stays resident in the server process | |

### Pool mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| `ProcessPoolExecutor` | Stdlib; `mp_context=spawn`, `initializer` pre-warm, `max_tasks_per_child` | ✓ |
| `anyio.to_process` | Already a transitive dep; no initializer or recycle control | |
| Hand-rolled workers | Only route to sticky-route by parameter hash; most to get wrong | |

### Pool startup

| Option | Description | Selected |
|--------|-------------|----------|
| Eager, import only | Lifespan starts the pool; initializer imports cadquery; sweep measures steady state from t=0 | ✓ |
| Eager + warm build | Also builds the stock gear; fastest first build, N solids resident before anyone asks | |
| Lazy | Fastest startup; first user build eats the import, sweep must separate warm from cold | |

**Notes:** Left open at the end of this area and folded into Load behavior / Measurement:
the Dockerfile `HEALTHCHECK` timeout and start-period, and the `SPUR_BUILD_WORKERS` default.

---

## Cache + boundary

### What crosses the process boundary

| Option | Description | Selected |
|--------|-------------|----------|
| `export(p,fmt,quality)->bytes` | Only finished bytes cross; vendor types never leave `model.py` | ✓ |
| build then export, two calls | Needs worker affinity or a handle table to keep the solid alive between calls | |
| derive + export in one call | Pointless — `derive()` is pure `calc.py` and must stay off the pool | |

### Cache placement

| Option | Description | Selected |
|--------|-------------|----------|
| Bytes parent, solids worker | `_BlobCache` moves to the serving process; solid `lru_cache` stays per worker; new L07 formula = parent bytes + N × solids | ✓ |
| Both stay in the worker | Smallest change; N × 64 MB unshared, repeat downloads cross the boundary | |
| Both, both sides | Doubles the accounting for no gain | |

### Routing

| Option | Description | Selected |
|--------|-------------|----------|
| Affinity by param hash | N single-worker executors indexed by hash; preserves build-once-export-three-times; no work stealing | ✓ |
| No affinity | Least code; same solid cached N times, three builds for one user's three downloads | |
| Affinity + fallback | Keeps throughput under mixed load; makes cache behaviour non-deterministic, so the sweep has no fixed topology | |

### The kernel lock

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `_LOCK` | Uncontended, guards OCCT process-global state; the superseding Lxx retires L06's consequence, not the lock | ✓ |
| Remove it | Less code; safety then rests on one-task-per-worker holding forever | |

---

## Load behavior

### Admission control sizing

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from N | `MAX_QUEUED_BUILDS` = workers + shallow queue (~2×N); still fail-fast `503` | ✓ |
| Keep 4, absolute | Smallest diff; 4 means something different at N=1 than N=4 and nothing says so | |
| Block with timeout | Better UX under light contention; reintroduces the coupling this phase removes | |

### Per-build timeout

| Option | Description | Selected |
|--------|-------------|----------|
| Generous timeout + replace | `SPUR_BUILD_TIMEOUT` set above the worst measured build; terminate and recreate the worker on expiry | ✓ |
| No timeout | Big gears legitimately take seconds on slow hardware; accepts a stranded worker on a real hang | |
| Timeout, no replacement | Misleading — the build keeps running and holding memory | |

**Notes:** chosen specifically because affinity (D-07) makes a wedged worker fatal to 1/N of
the parameter space.

### Status codes for new failure modes

| Option | Description | Selected |
|--------|-------------|----------|
| 422 / 503 / 503 | `BuildError` unchanged; broken pool and timeout both retryable `503` + `Retry-After` | ✓ |
| 422 / 500 / 504 | More precise for a log reader; three shapes for the UI, and 500 with no retry hint | |
| 422 / 503 / 422 | Treats a timeout as the parameters' fault — wrong, the same gear succeeds on faster hardware | |

### Worker memory hygiene

| Option | Description | Selected |
|--------|-------------|----------|
| malloc_trim, recycle if swept | Keep the measured win; enable `max_tasks_per_child` only if the sweep shows drift, and record which way it went | ✓ |
| Recycle every K builds | Unconditional, works off glibc too; costs a respawn and wipes the warm solid cache | |
| malloc_trim only | Today's behaviour per worker; if the sweep disagrees, the ceiling has to be padded | |

### Dockerfile HEALTHCHECK

| Option | Description | Selected |
|--------|-------------|----------|
| Drop to 5 s, from the measurement | Set from the measured under-load p95, comment rewritten to cite it | ✓ |
| Leave 10 s | Harmless headroom; leaves a comment asserting a stall that no longer exists | |
| Drop it and tighten start-period | Both numbers; start-period needs its own measurement given eager startup | |

**Notes:** start-period stays 30 s unless the eager-startup measurement says otherwise.

### `/api/health`

| Option | Description | Selected |
|--------|-------------|----------|
| Unchanged | Bare liveness ping keeps the p95 measurement clean | |
| Add pool state | Operator visibility into workers and queue depth | ✓ |
| Separate readiness endpoint | Clean measurement plus the signal; a new public endpoint | |

**Notes:** Claude flagged the risk — health is the success criterion's measurement target,
so putting the pool behind it can reintroduce the coupling in a new place. Follow-up
question pinned the implementation:

| Option | Description | Selected |
|--------|-------------|----------|
| Parent-local counters only | Live executors, semaphore value, workers replaced; no IPC, no lock, O(1) | ✓ |
| Query the workers | Detects an alive-but-wedged worker; puts IPC behind the measured endpoint | |
| Parent-local, plus last-seen | Also a per-worker timestamp; one more field for Phase 4 to type | |

### Test strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Seam + one real test | Injectable backend, inline for most tests, one real spawned-worker end-to-end | ✓ |
| Session-scoped real pool | Highest fidelity; errors arrive through IPC and get harder to read | |
| Inline only | Fastest gate; the process boundary untested by `make verify` | |

---

## Measurement

### Harness

| Option | Description | Selected |
|--------|-------------|----------|
| Committed + make target | Rerunnable `make bench` covering both scenarios and the sweep; not in `make verify` | ✓ |
| Ad-hoc, numbers recorded | Matches how the baseline was produced; nobody can reproduce it later | |
| Committed + gate assertion | Strongest guarantee; a latency assertion on shared hardware flaps and gets ignored | |

### Authoritative environment

| Option | Description | Selected |
|--------|-------------|----------|
| Container, on this machine | One environment; `mem_limit` measured under container accounting | |
| Host, matching the baseline | Like-for-like with the 0.22→0.76→2.00 s baseline; wrong accounting for `mem_limit` | |
| Both: latency host, memory container | Comparable latency *and* a container-accounted ceiling; roughly double the work | ✓ |

### Sweep design

| Option | Description | Selected |
|--------|-------------|----------|
| Per-N table, then confirm | N ∈ {1,2,4} over L07's 40-gear corpus; set from default-N peak + named headroom; confirm zero failures at that limit | ✓ |
| Default N only, then confirm | Half the time; a deployer raising N is back to guessing | |
| Bisect only | Least work; one number with no shape | |

### Superseding decision-log entries

| Option | Description | Selected |
|--------|-------------|----------|
| Two entries, numbers inline | L17 supersedes L07, L18 supersedes L06; numbers in the entries so claim and evidence cannot drift | ✓ |
| Two entries, numbers in a report | Short entries citing a dated measurement report; one more hop to the evidence | |
| One combined entry | Fewer ids; the roadmap criterion names two, and a reader tracing L06 would have to find it under memory | |

### `SPUR_BUILD_WORKERS` default

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed 2, from the sweep | Absolute default, justified by the per-N table, comment cites it | ✓ |
| Derived from CPU count | Adapts to the hardware; makes the memory ceiling machine-dependent | |
| Fixed 1, from the sweep | Minimum that satisfies the requirement; no throughput | |

### The Raspberry Pi 5 claim

| Option | Description | Selected |
|--------|-------------|----------|
| Defer as an idea | File in `docs/ideas/`, trigger is someone actually running one | ✓ |
| Soften the README now | Cheap and honest; a README change riding along in a runtime phase | |
| Measure it in this phase | Most honest answer; needs hardware and time this phase has not scoped | |

---

## Claude's Discretion

The human made every call offered; no "you decide" answers. These were recorded in
CONTEXT.md as planner/executor latitude because they were never put to the human:

- Name and placement of the kernel-free boundary module, and where `BuildError` lands.
- Bench harness location (`bench/` vs `docker/`) and output format.
- Literal values of `SPUR_BUILD_TIMEOUT` and the `mem_limit` headroom factor — the rule is
  fixed, the numbers come from the measurement.
- Whether `docs/architecture/overview.md` and `packaging.md` need updating, and how the debt
  resolution is sequenced against the code commits.

## Deferred Ideas

- Measure the Raspberry Pi 5 claim, or soften the README — `docs/ideas/`, trigger: someone
  actually running one.
- Server-side cancellation on client abort — existing `nice` debt; this phase unblocks its
  stated trigger, it does not do the work.
- Work stealing / non-affinity fallback routing — revisit only with a measurement showing
  affinity starves throughput.
- Querying workers from `/api/health` — revisit only if the build timeout proves
  insufficient for spotting an alive-but-wedged worker.
