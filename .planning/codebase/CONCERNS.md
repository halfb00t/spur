---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
# Codebase Concerns

**Analysis Date:** 2026-10-02

## Tech Debt — Must-Fix

**Blocker severity tracked in `docs/tech_debt/INDEX.md`:** none active. Four `must` items block certain work paths.

### Same-slot timeout cleanup race produces undocumented 500

**Issue:** When two requests to `_run_with_timeout` on the same worker slot both timeout within the same incident, a race condition causes the second timeout handler to read `executor._processes` against an executor already shut down by the first handler's `recreate_for` call, raising `AttributeError: 'NoneType' object has no attribute 'values'`. This surfaces as an undocumented raw HTTP `500` to the client instead of one of the three contracted `503` types (`busy` | `timeout` | `pool_broken`).

**Files:** `src/spur/pool.py` lines 183-210 (specifically line 204: `for proc in executor._processes.values():`), lines 99-155 (`recreate_for` method)

**Observed in:** Phase 13 measurement SC3 (`.planning/phases/13-latency-bar/investigation/sc3.server1.records.jsonl`), the composed worst row (29.42 s alone) under ten concurrent builds, where requests `912cd2d4` and `0fc30d53` crashed with this exception.

**Impact:** Clients written against the `/api/model.stl` contract have no branch for a raw `500` and will surface a raw server error. The underlying mechanism shows the timeout clock starts at submission, not execution, so queue wait on a shared slot counts toward the 30s timeout. Any two heavy same-hash-slot requests landing close together can reproduce this.

**Related finding:** The worst row's 0.58 s margin (measured alone in Phase 12 re-run) vanishes under concurrent load; the composed row exceeded the 30 s `SPUR_BUILD_TIMEOUT` entirely, not just timed out at margins.

**Fix approach:** `_run_with_timeout`'s `except TimeoutError` branch should detect that its `executor` local has already been replaced (compare identity against `self._executors[i]`, mirroring `recreate_for`'s own check) and skip re-terminating an executor no longer live.

**Revisit when:** The deferred ten-identical-worst-row scenario is run, a `500` is observed in production, `_run_with_timeout`/`recreate_for` is next touched, or `SPUR_BUILD_TIMEOUT`'s default is reconsidered.

---

### Root fillet lead-in can reach above the pitch circle

**Issue:** `spline_start` lifts the involute spline start to `rf + 2 × root_fillet` when the fillet needs room, and `_outline` runs a straight chord from the root up to it. The README claims this chord sits "in the non-working root zone," but for large profile shifts (e.g., `profile_shift: 1.0, pressure_angle: 14.5`), the spline's start sits **above** the pitch circle by 0.5625 mm — part of the working flank — contradicting README's statement.

**Measured deviations (pinned code, 2026-09-28):**
- Default gear: chord deviates from true involute by 35.29 µm; spline start 1.1875 mm **below** pitch circle ✓
- `profile_shift: 1.0, pressure_angle: 14.5`: chord 32.28 µm off; spline start 0.5625 mm **above** pitch circle ✗
- `profile_shift: 0.75, pressure_angle: 20`: chord 31.73 µm off; spline start 0.125 mm **above** pitch circle ✗

**Files:** `src/spur/calc.py` (`spline_start`), `src/spur/model.py` (`_outline`), `README.md` (Geometry notes)

**Impact:** A claim the tool makes about the part is false for a subset of configurations. Per L08 (wrong number worse than no number), either the lead-in must stay below the active profile's start (fixture regeneration, needs `Lxx` decision) or README must state the limit accurately.

**Fix approach:** Decide between: (a) keep lead-in below active profile start and regenerate fixture (architectural change), or (b) correct README to state the limit accurately per measured data.

**Revisit when:** A profile-shifted flank is measured, L10's trochoidal-root idea is taken up, or `_outline` is next touched.

---

### Filleted-spoke removed-volume proof is pinned, not derived

**Issue:** Every other cutout pattern's removed-volume assertion is checked against an independent closed-form formula to 1e-9 mm³ precision (holes: `π·r²·face_width`, sharp spokes: bar-area formula, honeycomb: hexagon-area formula). The filleted-spoke case — added by Phase 11, exercising new `_fillet_corner(inside=True)` mirrored-quadratic tangent-circle geometry — is checked only against a pinned literal (`d_volume=2934.725405`) measured once on the current kernel.

**Files:** `tests/test_model.py` (lines ~1224-1240, ~1186-1263), `src/spur/model.py` (`_fillet_corner`, `inside=True` branch), `docs/architecture/decision_log.md` (L30)

**Impact:** A silent regression in `_fillet_corner`'s `inside=True` branch, or a future OCP/CadQuery kernel bump that changes tangent-circle root selection, would move the pinned literal without any independent formula flagging drift as wrong. This is exactly the failure mode L08 prevents for every other cutout pattern; the filleted-spoke row is the gap.

**Fix approach:** Derive an independent closed-form for filleted-sector volume (sharp-sector area minus four circular-segment corrections of radius `spoke_fillet_effective(p)`, using the same bar-area formula already deployed) and assert against it to 1e-9 mm³.

**Revisit when:** `_fillet_corner` is next touched (bugfix, sign-convention change, mirrored-branch edit) or the pinned CadQuery/OCP kernel version is bumped.

---

### CI resolves the kernel from an unpinned range; the fixture pins one kernel exactly

**Issue:** `tests/regression/pre_v0_2.json` pins exact topology and dimensions captured on one resolved kernel: cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1. CI's `make verify PYTHON=python` builds a fresh venv from `pyproject.toml`'s `cadquery>=2.5` range at run time — no pinned version. Today CI and the fixture agree only because cadquery 2.8.0 caps `cadquery-ocp<8.0,>=7.9.3.1`, but cadquery-ocp 8.0.1.0.0 is already published. When a future cadquery release changes that cap, CI's resolve can land on a different kernel.

**Files:** `tests/regression/pre_v0_2.json` (provenance header), `tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_run_uses`, `pyproject.toml` (`cadquery>=2.5`), `.github/workflows/ci.yml` (`make verify PYTHON=python` on fresh venv)

**Impact:** A kernel-driven OCCT topology change (face count, bounding-box corner, volume) would turn CI red with no code change in this repository to explain it. The dedicated test `test_the_fixture_was_captured_on_the_kernel_this_run_uses` will name both kernel pairs when this happens, but it does not prevent CI from going red.

**Fix approach:** Either pin CI to install from `requirements.txt`'s locked versions before `make verify` (consistent with L12), or add an explicit upper bound in `pyproject.toml`'s `cadquery` range. Either is a decision against L12's "why floors and ranges are chosen" and requires human approval.

**Revisit when:** A fresh `pip install -e '.[dev]'` resolves a `cadquery`/`cadquery-ocp` pair different from the fixture's provenance header.

---

## Tech Debt — Nice-to-Fix

**Nice severity:** Five open items, none blocking shipping.

### CadQuery's `Shape` typing forces five `type: ignore`s

**Issue:** CadQuery types boolean results as the wide `Shape`, which declares neither `fillet` nor `chamfer` (those live on `Mixin3D`, carried by `Solid` and `Compound` but not `Shape` itself). The pipeline is correct at runtime (a boolean on a solid yields a `Solid` or `Compound`), but the annotations say `Shape`, forcing five narrow `type: ignore` comments.

**Files:** `src/spur/model.py` lines 195, 219, 221, 264, 273 (Phase 10's tip chamfer added the fifth)

**Impact:** Low. Ignores are specific (`attr-defined`, `arg-type`, `return-value`) with justifications. `RUF100` will fail the build if one becomes unnecessary. The cost is five lines outside the type checker in the project's most delicate file.

**Fix approach:** Narrow the annotations through `_gear_blank` → `_cut_face_recesses` → `_cut_bore` to the type the values actually have, casting once at the `.val()` boundary rather than ignoring at each call site.

**Revisit when:** CadQuery narrows its own return types, or that pipeline is touched anyway.

---

### No server-side cancellation on client abort

**Issue:** The UI aborts its in-flight fetch on parameter change and drops out-of-order responses with a sequence counter (correct browser behavior), but the server does not find out. The build proceeds to completion and bytes are produced for nobody. Dragging a slider queues work already irrelevant.

**Files:** `src/spur/static/app.js` (update loop's `AbortController`), `src/spur/app.py` (`model` endpoint)

**Impact:** Wastes the one scarce resource (the serialised kernel), fills the bounded queue with requests nobody waits for, so real requests get `503 busy` behind abandoned ones. The debounce keeps this small today.

**Fix approach:** Check `await request.is_disconnected()` before taking a build slot and again before starting export. Catches the cheap case without needing cancellation inside the kernel call (which is not interruptible anyway).

**Revisit when:** Slider-dragging saturates the queue in practice, or after the process pool lands (would make real cancellation possible).

---

### No coverage floor in the gate

**Issue:** `[tool.coverage.run]` is configured with `branch = true` and `source = ["src/spur"]`, but nothing measures coverage in `make verify` and there is no `fail_under`. The reason: a floor picked before measuring is a number, not a guarantee, and a floor set too low is worse than none.

**Files:** `pyproject.toml` (`[tool.coverage.run]`), `Makefile` (`verify` target)

**Impact:** Low today: 50 tests cover geometry, API, CLI, and STL topology, written against a measured review. Risk is drift — new code landing with no test and nothing noticing until someone looks.

**Fix approach:** Run `pytest --cov` once on the current suite, read the real number, set `fail_under` just under it, and add `--cov --cov-fail-under` to the `test` target so it gates.

**Revisit when:** Immediately after one measured baseline run (ten-minute item held only until the number exists).

---

### The service has no authentication

**Issue:** There is no authentication, authorisation, or rate limiting beyond the build queue. This is a known, documented position: `compose.yaml` binds to `127.0.0.1` on purpose, the container runs non-root with security hardening, and the README documents putting a reverse proxy with auth in front to expose it.

**Files:** `src/spur/app.py`, `compose.yaml`

**Impact:** Sound while binding is localhost. An unauthenticated endpoint that builds a 200-tooth gear is a DoS primitive (seconds of CPU, hundreds of MB per request) if exposed.

**Fix approach:** If ever exposed: reverse proxy carries auth (Caddy/Traefik/Cloudflare Access/Tailscale), and the app should rate-limit by client on model endpoints, since `SPUR_MAX_QUEUED_BUILDS` bounds concurrency but not cost per client.

**Revisit when:** The port mapping changes, or the service is deployed anywhere but one person's machine.

---

### gsd's 30s commit timeout kills the pre-commit `make verify` hook on cold cache

**Issue:** gsd's SDK commit runs `git commit` under a hard-coded 30s timeout with no config knob. This repo's pre-commit hook runs `make verify`, which is ~11s warm and takes minutes on first run after OpenCascade pages evict. Observed: first SDK commit of the session returned `{committed: false, reason: 'commit_timeout'}`, killed mid-hook.

**Files:** `.pre-commit-config.yaml` (verify hook: ~11s warm, minutes cold), `~/.claude/gsd-core/bin/lib/commands.cjs:3655` (hard-coded `COMMIT_TIMEOUT_MS = 30_000`, outside this repo)

**Impact:** Every gsd workflow that commits (`execute-phase`, `complete-milestone`, `new-milestone`) hits this on first cold commit of a session. The executor's recovery (retry once warm) works but costs one wasted `make verify` per session and opens a window for stale `index.lock` if the kill lands mid-write.

**Fix approach:** Warm the cache before the first commit (`make verify` once, e.g., at start of `/gsd-execute-phase`), and raise upstream that `COMMIT_TIMEOUT_MS` should be configurable.

**Revisit when:** gsd exposes a commit-timeout setting, or when an executor's warm retry also times out.

---

### Enji Guard not connected

**Issue:** GitHub App `https://guard.enji.ai/app` offering continuous AI audit (security, dependencies, test coverage, AI-readiness) was offered during setup and the owner declined. Connecting it requires OAuth click by someone with admin; cannot be scripted from here.

**Files:** (none — repository integration, not code)

**Impact:** Low, partially covered: CI runs the full gate on two Python versions, builds the image, smoke-tests the container, dependency closure is fully pinned (L12). What is not covered: ongoing CVE alerting — nothing watches for a vulnerability in the 31 pinned packages.

**Fix approach:** Either connect Enji Guard, or enable GitHub's free Dependabot alerts and security updates — addresses the one real gap without third-party dependency.

**Revisit when:** The owner decides they want continuous AI audit, or at next dependency bump.

---

## Performance Bottlenecks

### Composed worst row exceeds timeout margin under concurrent load

**Finding from Phase 13 SC3 measurement (`bench/RESULTS.md` lines 472-598):**

The composed worst row (29.42 s alone: `teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`) was timeout-terminated at 30.004s when run alongside nine other concurrent requests — it did not finish inside the 30s `SPUR_BUILD_TIMEOUT` default despite being the one request actually executing on its slot. Phase 12's re-run measured this row alone at 29.42 s with 0.58 s margin ("~1.02x" of budget).

**Files:** `bench/RESULTS.md` (### Composed worst row, lines 472-598), `bench/sweeps/composed.json` (row 4, the worst), `src/spur/app.py` (`int_env("SPUR_BUILD_TIMEOUT", 30)`)

**Impact:** The single-build margin does not survive concurrent load on the test machine (M2 Max, 12 cores). On slower hardware or under higher contention, the worst row becomes unservable within the default timeout.

**Interpretation:** The underlying mechanism (timeout clock starts at submission, not execution; queue wait counts toward the 30s per `_run_with_timeout`'s `asyncio.wait_for(future, timeout=self.timeout)` at line 183 of `pool.py`) means queue depth + build duration must stay under 30s total. With 4 queued builds and 2 workers, the worst case sees a request wait 30s in queue, then timeout immediately on its turn. The "0.58 s margin alone" claim is therefore an artifact of single-build measurement; under load the system has no margin at all.

**Future work:** The deferred ten-identical-worst-row scenario (13-CONTEXT.md) would cleanly isolate queue wait from kernel contention for a single hash slot. Once run, it can inform whether the timeout value itself should change or whether the queue depth (`MAX_QUEUED_BUILDS`) should tighten.

---

### Latency bar not demonstrated on both runs of concurrent scenario

**Finding from Phase 13 bar sessions (`bench/RESULTS.md` lines 303-470):**

The `concurrent` scenario (ten concurrent 200-tooth fine builds) acceptance clause "under-load p95 <= 2.00x idle p95" was:
- Runs 1-2 (host not fully idle): not met (2.02x, 2.45x)
- Runs 3-4 (re-run on quieter host): not met (2.32x, 2.35x)
- Runs 5-6 (post-fix with gzip caching): mixed (1.31x pass, 2.10x fail)
- Runs 7-8 (quieter host, post-fix): mixed (1.86x pass, 2.02x fail)
- **Bar-1 (Runs 9-10):** non-decisive (quiet gate expired)
- **Bar-2 (Runs 11-12):** non-decisive (quiet gate expired)
- **Bar-3 (Runs 13-14, DECISIVE):** met (1.31x, 1.42x)

**Files:** `bench/RESULTS.md` (## Latency, lines 34-469), `bench/latency.py` (harness), `.planning/phases/13-latency-bar/investigation/` (investigation sessions A-C)

**Interpretation:** The decisive session (bar-3, 2026-10-02T07:14:05Z) cleared the bar on both runs of the `concurrent` scenario. The pattern across eight runs (pre- and post-fix) shows the second run of a pair consistently worse than the first (before and after fix), and the bar sits at the harness's floor (idle p95 0.6 ms, under-load p95 1.2-1.3 ms) where small changes flip the verdict.

**Fragility:** The bar is now demonstrated, but not robustly — one more 0.1 ms of under-load p95 flips either Run 13 or Run 14. The floor is real per Phase 13's investigation (13-LATENCY-INVESTIGATION.md Verdict on Observation 2).

---

### Admitted builds share a worker slot; both timeout in tandem

**Finding from Phase 13 SC3 (`bench/RESULTS.md` lines 472-598):**

Requests `51e80f35` (worst row) and `912cd2d4` were hash-routed to the same worker slot (`executor_for` hash affinity, `hash(p) % self.workers`). Both exceeded the 30s timeout within the same incident (`duration_ms 30002-30004`). The first request's cleanup (`recreate_for`) shut down the executor; the second request's cleanup then crashed trying to read the already-shut-down `executor._processes`. (See: **Same-slot timeout cleanup race** above.)

**Files:** `src/spur/pool.py` (hash affinity at `executor_for`, lines 99-155), `bench/RESULTS.md` lines 536-560 (per-request outcomes table), `bench/sweeps/composed.json` (ten distinct keys chosen to spread over both workers)

**Impact:** A deterministic failure mode when two heavy requests hash to the same slot and both timeout. The compose test hit it by hash-affinity chance, not by design; a stress test of ten identical worst rows would hit it reliably.

**Design note:** The hash affinity (D-07) is intentional (request locality, cache efficiency). The parallel timeout is a consequence of `MAX_QUEUED_BUILDS` filling the queue faster than builds drain, creating a queue-wait condition where multiple requests waiting on the same slot's executor all timeout together when that executor exceeds the 30s.

---

## Test Coverage Gaps

### No independent cross-check for filleted-spoke cutout proof

**See:** **Filleted-spoke removed-volume proof is pinned, not derived** (above).

---

## Fragile Areas

### `pool.py` — ProcessPoolExecutor lifecycle race condition

**Fragility:** The identity check in `_run_with_timeout`'s timeout handler (line 204: `for proc in executor._processes.values()`) assumes only the current request will call `recreate_for` for its slot. When two requests timeout within the same incident, the second request reads a reference that the first request's `recreate_for` already invalidated, causing an `AttributeError`.

**Mechanism:** Each request holds its own `executor` local captured at line 169. Both requests on the same slot hold the same `ProcessPoolExecutor` object. `recreate_for` shuts down this executor and installs a new one in `self._executors[i]`. The second request's timeout handler still refers to the old, shut-down executor.

**Why fragile:** Concurrent access to the same slot's executor with no re-entrant guard. The `recreate_for` identity check (line 103: `if self._executors[i] is not executor:`) only protects `recreate_for` itself from re-installing; it does not protect the *caller's* reference after `recreate_for` has moved the slot.

**Safe modification:** Detect slot replacement before touching `executor._processes` (same identity check `recreate_for` uses), or hold `self._executors[i]` as the live reference instead of caching it locally.

**Test coverage:** `tests/test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced` covers single-timeout recovery; no test covers parallel timeout on the same slot (would need `MAX_QUEUED_BUILDS >= 2 * SPUR_BUILD_WORKERS` or the deferred ten-identical-worst-row scenario).

---

### `model.py` — CadQuery Shape return types outside mypy

**Fragility:** Five `type: ignore` comments in `model.py` (lines 195, 219, 221, 264, 273) suppress type errors on calls to `fillet` and `chamfer`, which are not declared on `Shape` even though the pipeline always produces a `Solid` or `Compound` at those points.

**Why fragile:** The ignores are specific and have inline justifications (`# type: ignore[attr-defined]`), but they remain unmaintained and cannot be simplified by the type checker. A future narrowing of the annotations would need to revert all five ignores; a narrowing missed would leave a dead ignore that `RUF100` would flag.

**Safe modification:** Cast the result at the boundary (`_gear_blank` → `_cut_face_recesses` → `_cut_bore`), so the pipeline's intermediate types narrow at once rather than being suppressed piecemeal.

**Test coverage:** Integration tests verify geometry (volume, topology, watertightness); type-checking is enforced at gate. No test specifically checks that the cast is correct.

---

### `calc.py` — Pure math with one-off measurements

**Fragility:** `spline_start` and `profile_outline` encode measured geometry (fillet reach, involute approximation deviation) as literal constants. A misunderstanding of the measurement method could bake a wrong constant into production without any independent cross-check.

**Why fragile:** The measurements are point-in-time against one kernel version (the M2 Max measurement set dates to early phases). A kernel update could change absolute values without this code knowing it changed.

**Safe modification:** Document the measurement method and corpus (module/teeth/profile ranges) for every constant, so a future reviewer can re-measure and compare. Periodically (e.g., after a kernel bump) re-run the measurement and confirm numbers have not drifted.

**Test coverage:** `tests/test_calc.py` checks the functions with known inputs; it does not re-verify the measurements themselves.

---

### `app.py` — Hash affinity couples request latency to hash distribution

**Fragility:** Every request's worker slot is determined by `hash(params) % self.workers` (D-07). If the parameter distribution is skewed (e.g., many users requesting the same tooth count and module), all their requests hash to the same slot, serialising their builds on one worker and starving the other.

**Why fragile:** The hash function is built into the `executor_for` method and the only alternative is to round-robin, which would lose cache locality. No monitoring alerts on slot load imbalance today.

**Safe modification:** Monitor the distribution of requests across slots at runtime; if the distribution is skewed, either log a warning or gather histogram data for a future scheduler decision.

**Test coverage:** `tests/test_pool.py` exercises the pool's lifecycle; it does not exercise hash distribution under realistic parameter patterns.

---

## Security Considerations

### Unauthenticated API can be used for resource exhaustion

**Issue:** The service has no authentication and no rate limiting beyond the bounded queue (L04). An unauthenticated client can craft requests to build expensive gears (e.g., 200-tooth fine) and DoS the service by filling the queue with builds for nobody.

**Current mitigation:**
- Runs on `127.0.0.1:8000` by default (localhost only)
- Container runs non-root with `read_only`, `cap_drop: ALL`, `no-new-privileges`, tmpfs `/tmp` (process isolation)
- README documents using a reverse proxy with auth for exposure

**Risk:** If the port mapping changes (e.g., `8000:8000` for convenience) or the service is deployed without the proxy, the DoS vector is live.

**Recommendation:** If exposed, add per-client rate limiting on the model endpoints (`/api/model.stl`, `/api/model.step`) in addition to the reverse proxy auth. `SPUR_MAX_QUEUED_BUILDS` limits concurrency but not cost per client.

---

### No CVE monitoring on pinned dependencies

**Issue:** The dependency closure is fully pinned in `requirements.txt` (L12), but nothing watches for a CVE published after the pin. The 31 packages will age; a vulnerability in a transitive dependency could go unnoticed.

**Current mitigation:**
- CI runs `make verify` on two Python versions; `lint` includes ruff's security rules
- GitHub Actions runs the full gate on every PR and push

**Recommendation:** Enable GitHub's free Dependabot alerts and security updates, or connect Enji Guard for continuous audit. Either catches CVEs without third-party services.

---

## Scaling Limits

### Queue depth cannot be too deep without timeout contention

**Current capacity:**
- Default: `MAX_QUEUED_BUILDS = 2 × SPUR_BUILD_WORKERS = 4` (2 workers + 4 queued = 6 total in flight)
- Worst row alone: 29.42 s
- Worst row + queue wait under 30 s timeout: 0.58 s max queue wait

**Limit:** If `MAX_QUEUED_BUILDS` is raised or the number of concurrent requests grows, queue wait can exceed the timeout window. The Phase 13 SC3 measurement shows two concurrent requests hitting timeout together when routed to the same slot.

**Scaling path:**
- Measure the realistic queue-depth distribution under expected load
- If queue grows, either raise `SPUR_BUILD_TIMEOUT` (coarse, affects all builds) or implement a tighter timeout for queued requests separately from builds (fine-grained, but more complex)
- Monitor slot load distribution; if skewed, consider a smarter scheduler

---

### Memory plateau at 358 MiB (bounded cache, with `malloc_trim`)

**Measured capacity (L07, `bench/RESULTS.md` ## Memory):**
- One worker, 40-gear corpus: 358 MiB steady-state
- `SPUR_SOLID_CACHE=4` (4 solids at ~280 MiB each would overflow; cache bounds it)
- `SPUR_EXPORT_CACHE_MB=64` (total export bytes bounded)
- `malloc_trim(0)` after every cache-missing export (glibc arena release)

**Limit:** The 358 MiB is on a single Docker worker with `mem_limit: 1g` (the backstop in `compose.yaml`). With more concurrent workers or a smaller limit, memory pressure could trigger early cache eviction or OOM kills.

**Scaling path:**
- Measure memory on the actual deployment target (not M2 Max)
- If heap grows, check whether `malloc_trim` is running (monitor RSS in production)
- If OOM is hit, prioritize `SPUR_SOLID_CACHE` reduction over `SPUR_EXPORT_CACHE_MB` (solids are the larger cost)

---

## Dependencies at Risk

### CadQuery/OpenCascade kernel version must stay in sync across CI and development

**Issue:** CI resolves `cadquery>=2.5` at run time (unpinned); the fixture pins one kernel exactly. If an upstream cadquery release changes its `cadquery-ocp` cap, CI can resolve a different kernel, and the regression fixture's exact-value assertions will fail even if the code is correct.

**Current status:** cadquery 2.8.0 pins `cadquery-ocp<8.0,>=7.9.3.1`. cadquery-ocp 8.0.1.0.0 is already published on PyPI.

**Migration path:** Either (a) pin CI to install from `requirements.txt` before `make verify`, consistent with L12's locked deployment, or (b) add an explicit cap to `pyproject.toml`'s `cadquery` range. Either needs the human to decide against L12's documented reasoning.

---

### No automatic security updates on pinned closure

**Issue:** `requirements.txt` is fully pinned and committed, but no automation re-pins when a CVE is found in a transitive dependency. The 31 packages will age.

**Recommendation:** Enable GitHub's Dependabot security updates (free, no third party) or connect Enji Guard. Set up an automated weekly-or-monthly rescan.

---

## Deferred Ideas (Not Now)

**Open items in `docs/ideas/` (8 items):**

1. **Trochoidal root fillets for undercut gears** (2026-09-21) — Current radial root is a documented approximation that only matters for undercut; revisit when profile-shifted flank is measured or L10 is taken up
2. **Browser test for the viewer** (2026-09-21) — Deferred for cheaper first step (Python schema→form assertions); revisit when either deferred UI idea below is taken
3. **Measure or soften the Raspberry Pi 5 claim** (2026-09-22) — Needs hardware nobody here has; all Phase 2 numbers from 12-core dev machine
4. **Bore-shape selector in web form** (2026-09-27) — Judged "not taken" at Phase 12 (08 D-09 stands); revisit when browser test exists or users report ignored-field warnings as insufficient
5. **Recipe for re-verifying a phase after post-verification fixes** (2026-09-28) — Process, not product; one HOW_TO_DEVELOP paragraph or project skill once it repeats a third time
6. **Rotation field for spoke arms and lightening holes** (2026-09-29) — D-03 fixes +X and nobody has asked for another angle; additive field is the safe undo when someone does
7. **Teeth- or module-dependent honeycomb cell-count cap** (2026-09-29) — D-12 rejected it for one constant; revisit only if small gear needs more cells and sweep shows cost falling with gear size
8. **Conditional form fields ("disabled when")** (2026-09-29) — Judged "not taken" at Phase 12 (08 D-09 stands); revisit when browser test exists or users report insufficient

---

*Concerns audit: 2026-10-02*
