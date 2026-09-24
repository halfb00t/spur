# Roadmap: spur

## Overview

`spur` already ships. Phase 1 records the completed v0 baseline — the working parametric
involute spur gear generator currently in the tree, with all 11 ingested requirements
satisfied and `make verify` passing. Milestone v0.1 ("Hardening") builds forward from
there: Phases 2–5 pay down the three `must` tech-debt items and close the standing
CI-unverified blocker, so the generator is operable under real load and its response
contract is type-checked — before any new gear geometry (helical/internal/rack gears,
tooth chamfers, new bore profiles, body cutouts) makes every build heavier. No new gear
features ship in this milestone; see "Forward Scope" below for where those candidates are
tracked.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: v0 Baseline (Shipped)** - The generator, its three interfaces, and its
  error/measurement/export contract, as already built and verified.
- [x] **Phase 2: CAD Off the Event Loop** - CAD kernel work moves to worker processes, and (completed 2026-09-24)
  the multi-process memory ceiling is measured, not carried over from the single-process
  design.
- [ ] **Phase 3: Structured Logging at the Composition Boundary** - Production requests
  leave evidence: a structured logger at startup covers the decision branches that already
  exist.
- [ ] **Phase 4: Typed Derived-Dimensions Contract** - `derive()`'s response gets a real
  shape, checked by mypy with `disallow_any_explicit` on.
- [ ] **Phase 5: CI Observed Green** - The CI workflow is proven by a real GitHub Actions
  run, not by hand-verification.

## Phase Details

### Phase 1: v0 Baseline (Shipped)

**Goal**: Users can generate a correct, print/CNC-ready involute spur gear — with numbers
they can trust — from a web UI, an HTTP API, or a CLI, all driven by one parameter model.
**Depends on**: Nothing (first phase)
**Requirements**: REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses,
REQ-measurement-aids, REQ-three-interfaces, REQ-cli-parity, REQ-shareable-links,
REQ-stl-step-export, REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch
**Success Criteria** (what is observably TRUE today):

  1. The same gear and the same derived numbers are reachable from the web UI, the HTTP
     API, and the CLI, all built from one `GearParams` model; the CLI's numbers, warnings,
     and exit codes match the API's. *(REQ-three-interfaces, REQ-cli-parity)*
  2. Every gear configuration lives in the URL, so it can be shared and reopened as a
     link. *(REQ-shareable-links)*
  3. The generated solid reflects involute tooth geometry (module, teeth, pressure angle,
     profile shift), backlash, root fillets, a D-flat or round bore with clearance and
     chamfer, and optional filleted-floor face recesses on one or both sides.
     *(REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses)*
  4. Users can download the generated gear as STL (for slicing) or STEP (for CAD) from
     any of the three interfaces. *(REQ-stl-step-export)*
  5. Users get caliper, span (Wildhaber), and centre-distance measurements for matching an
     existing physical gear, with a warning — never a fabricated number — when no working
     centre distance exists. *(REQ-measurement-aids)*
  6. A direct conflict between two explicit parameters is refused (422 / exit 2) naming the
     offending fields; a trimmable dimension is capped and the trim is reported in
     `warnings`; the service deploys via Docker/compose on `linux/amd64` and `linux/arm64`,
     bound to `127.0.0.1` with no built-in authentication by default.
     *(REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch)*
**Plans**: N/A — this baseline predates GSD planning and was built and verified directly
against `make verify`; there is no PLAN.md history to point to.

### Phase 2: CAD Off the Event Loop

**Goal**: CAD kernel work runs in worker processes outside the request-serving event loop,
and the resulting multi-process memory ceiling is a measured number — not an assumption
carried forward from the single-process design L07 measured.
**Depends on**: Phase 1
**Requirements**: REQ-cad-off-event-loop, REQ-measured-memory-ceiling
**Success Criteria** (what must be TRUE, each backed by a measurement, not a prediction):

  1. Repeating the debt file's own two load scenarios — one 200-tooth fine build in
     flight, and ten concurrent builds — against the new topology shows `/api/health` p95
     within 2× of idle p95, with the measured numbers recorded next to the baseline on
     record (0.22 s → 0.76 s → 2.00 s for the single build; repeatedly over 5 s for ten
     concurrent, 12-core machine). *(REQ-cad-off-event-loop)*
  2. A memory sweep of the actual N-worker topology — not L07's per-process numbers
     multiplied out — produces a measured ceiling, and `compose.yaml`'s `mem_limit` is set
     from that number. *(REQ-measured-memory-ceiling)*
  3. `docs/architecture/decision_log.md` gains two new entries that supersede, and say they
     supersede, L07 (per-process cache/memory formula) and L06 ("concurrency buys latency,
     not throughput") — each dated, each citing the new measurement, neither edited in
     place. *(REQ-measured-memory-ceiling)*
  4. `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` is
     `Status: resolved` with its commit sha recorded, `git mv`'d into
     `docs/tech_debt/resolved/`, and its row moved in `docs/tech_debt/INDEX.md` — in the
     same commit as the fix. *(REQ-cad-off-event-loop)*
  5. `make verify` passes with the new topology in place; admission control still lives in
     the web layer and the CLI still never queues (L04) — unchanged by the process pool.
**Plans**: 5/5 plans executed, in 4 waves (01 and 02 run in parallel)

- [x] 02-01-PLAN.md — One build, in another process: the kernel-free `BuildError`, the
  affinity-routed `BuildPool`, the async endpoint, the parent-side byte cache, and the
  import-linter contract that makes the boundary enforced rather than reviewed *(wave 1)*
- [x] 02-02-PLAN.md — The measuring instrument: `bench/` (L07's own 40-gear corpus, both
  load scenarios, the N=1,2,4 container memory sweep) and `make bench`, deliberately
  outside the gate *(wave 1, parallel with 02-01)*
- [x] 02-03-PLAN.md — Failure modes and liveness: the per-build timeout that terminates a
  wedged worker, the three failure-mode status codes, and pool state on `/api/health`
  *(wave 2)*
- [x] 02-04-PLAN.md — The measured numbers: run both harnesses, record `bench/RESULTS.md`,
  and set `SPUR_BUILD_TIMEOUT`, `mem_limit`, `SPUR_BUILD_WORKERS` and
  `max_tasks_per_child` from what was measured *(wave 3)*
- [x] 02-05-PLAN.md — Close the loop: L17 (supersedes L07) and L18 (supersedes L06), the
  healthcheck timeout brought down from the measurement, and the debt file resolved and
  moved in the same commit *(wave 4)*

### Phase 3: Structured Logging at the Composition Boundary

**Goal**: Production requests leave evidence — a structured logger configured once at the
composition boundary, covering the decision branches that already exist.
**Depends on**: Phase 1 (no dependency on Phase 2 found in the debt files — the logging
gap and the event-loop gap are independent; nothing in
`docs/tech_debt/active/2026-09-21-no-structured-logging.md` ties its fields to the process
pool's build-queue mechanics)
**Requirements**: REQ-structured-logging
**Success Criteria** (what must be TRUE, proven by a test, not console-reading):

  1. A test asserts that each of the four existing decision branches — build started (with
     parameter slug), build failed (with exception class), export served from cache vs.
     built, queue refused — emits a structured log record with named fields.
  2. `calc.py` stays log-free: it remains pure, runs on every keystroke, and its
     `warnings` output is its only diagnostic (L01/AGENTS.md boundary, unchanged).
  3. `docs/tech_debt/active/2026-09-21-no-structured-logging.md` is `Status: resolved`
     with its commit sha recorded, `git mv`'d into `docs/tech_debt/resolved/`, and its row
     moved in `docs/tech_debt/INDEX.md` — in the same commit as the fix.
  4. `make verify` passes.

**Plans**: 2/3 plans executed, in 3 waves (each wave depends on the one before — `records.py` and
`app.py` are touched by both code plans, so there is no honest parallelism here)

- [x] 03-01-PLAN.md — The tracer and the module: kernel-free `records.py` (`configure()`,
  the JSON formatter, the level knob), wired at both composition points (`cli.cmd_serve`
  with `log_config=None`, and the `lifespan()` call research proved mandatory), plus
  `export.served`/`build.started` and the record format's edges *(wave 1)*
- [x] 03-02-PLAN.md — The failure branches: `build.failed` with the exception class and
  duration, `queue.refused` with the in-flight count, and `worker.replaced` emitted inside
  `recreate_for`'s identity guard so one incident is one record *(wave 2)*
- [ ] 03-03-PLAN.md — Close the loop: `L20`, the four §Logging sections and the README row
  that are now false, and the debt file resolved and moved in the same commit *(wave 3)*

### Phase 4: Typed Derived-Dimensions Contract

**Goal**: The response every interface reads has a real shape — a typed model, checked by
mypy, instead of an honest but unchecked `dict[str, Any]`.
**Depends on**: Phase 1 (independent of Phases 2 and 3 — the contract change touches
`calc.py`'s return type and the API/CLI/UI's read of it, not the process topology or the
logger)
**Requirements**: REQ-typed-derived-dimensions
**Success Criteria** (what must be TRUE, checked by the gate, not asserted):

  1. `derive()` returns a `DerivedDimensions` Pydantic model with explicit optional fields
     in place of `dict[str, Any]`.
  2. `make verify` passes with mypy's `disallow_any_explicit` turned on across `src/` —
     L14's named ratchet is retired, not re-deferred.
  3. The generated OpenAPI document reflects the new typed shape, and the web UI's
     existing reads of `detail[].ctx.fields` and `warnings` still work, verified by the
     test suite.
  4. `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` is `Status: resolved`
     with its commit sha recorded, `git mv`'d into `docs/tech_debt/resolved/`, and its row
     moved in `docs/tech_debt/INDEX.md` — in the same commit as the fix.
**Plans**: TBD

### Phase 5: CI Observed Green

**Goal**: The CI workflow is proven by a real GitHub Actions run executing it — not by
reading `.github/workflows/ci.yml` and predicting it will pass.
**Depends on**: Phase 1 (independent of Phases 2–4; small and deliberately not bundled
into any of them per the milestone's own scoping)
**Requirements**: REQ-ci-verified
**Success Criteria** (what must be TRUE, evidenced by a run URL, not a prediction):

  1. A real push to GitHub produces a run URL showing the `test` job green on both matrix
     entries (`python: ["3.10", "3.12"]`).
  2. The same run shows the `vendor-bundle` job (the committed three.js bundle matches a
     fresh build of `web/`) and the `image` job (the packaged container serves
     `/api/health`, `.stl`, and `.step`) both green.
  3. The "CI workflow unverified" blocker carried in `STATE.md` since the 2026-09-21
     bootstrap is retired, with the run URL recorded as the evidence.
**Plans**: TBD

## Forward Scope

Milestone v0.1 is hardening only — no new gear geometry ships in Phases 2–5. Candidates
for the *next* milestone are gathered, not scoped, in `REQUIREMENTS.md` under "Future
Requirements": helical/internal/rack/bevel gears, tooth chamfers, new bore/centre-hole
profiles, parametric body cutouts (spokes, lightening holes, hex patterns), the trochoidal
root-fillet idea (would supersede L10), and a browser-driven viewer test. None of these
are phases yet — the next `/gsd-new-milestone` run picks from that list deliberately, the
way this one did.

The five `nice`-severity tech-debt items in `docs/tech_debt/active/` (coverage floor,
CadQuery `Shape` typing, server-side cancellation, no authentication, Enji Guard/CVE
alerting) stay in their own lifecycle, each with its own trigger — not carried into this
roadmap.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. v0 Baseline (Shipped) | N/A | Complete | Shipped (pre-dates this roadmap) |
| 2. CAD Off the Event Loop | 5/5 | Complete    | 2026-09-24 |
| 3. Structured Logging at the Composition Boundary | 2/3 | In Progress|  |
| 4. Typed Derived-Dimensions Contract | 0/TBD | Not started | - |
| 5. CI Observed Green | 0/TBD | Not started | - |
