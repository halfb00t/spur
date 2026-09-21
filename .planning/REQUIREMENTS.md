# Requirements: spur

**Defined:** 2026-09-21 (from doc ingest — no PRD existed; derived from root `README.md`
and 15 SPEC documents per `.planning/intel/requirements.md`)
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

## v0 Requirements (Shipped Baseline)

**These are not work to be done.** All 11 describe behavior that already exists and works
in the current tree; `make verify` passes. Recorded here as the baseline this project ships
from, not as a plan. Where the ingested SPECs stated no test or explicit acceptance
criterion, `acceptance` is marked **absent** — nothing was invented to fill it.

### Geometry

- [x] **REQ-involute-geometry**: Generate involute spur gear tooth geometry from module,
  tooth count, pressure angle and profile shift.
  - *Acceptance*: Flanks are true involutes sampled into B-splines from the base circle (or
    root circle, if larger) to the tip (README, "Geometry notes"); `test_default_dimensions`
    in `tests/test_calc.py` pins the stock gear's numbers.
- [x] **REQ-bore-and-fillets**: Support backlash, root fillets, and a D-flat or round bore
  with print clearance and chamfer.
  - *Acceptance*: **absent** — README states the feature; `docs/architecture/gear-maths/implementation.md`
    names `bore_radius(p)`/`root_fillet(p)` but no test is cited for this requirement
    specifically in the ingested SPECs.
- [x] **REQ-face-recesses**: Support annular face recesses on one or both sides, with
  filleted floors; a recess that does not fit is narrowed (or dropped) rather than refused
  (L03).
  - *Acceptance*: `test_recess_removes_expected_volume` and
    `test_a_gear_too_small_for_the_stock_recess_still_builds` in `tests/test_model.py`; the
    cap-and-warn warning-text assertions in `tests/test_calc.py`.

### Measurement

- [x] **REQ-measurement-aids**: Provide measurement aids for matching an existing physical
  gear — caliper reading across tips (corrected for odd tooth counts), span measurement
  over k teeth (Wildhaber), and centre distance to a mating gear.
  - *Acceptance*: `test_caliper_reading_is_short_for_odd_tooth_counts`,
    `test_span_measurement` (three hand-checked Wildhaber spans),
    `test_centre_distance_matches_an_independent_solver` — all in `tests/test_calc.py`.

### Interfaces

- [x] **REQ-three-interfaces**: The same gear and the same derived numbers are reachable
  three ways — a web UI, an HTTP API, and a CLI — all driven by one parameter model
  (`GearParams`, L02).
  - *Acceptance*: **absent** — asserted architecturally via L02 and `docs/architecture/overview.md`;
    no single test in the ingested SPECs exercises all three interfaces together for
    equivalence.
- [x] **REQ-cli-parity**: The CLI (`spur serve` / `info` / `export`) offers the same gear,
  the same numbers, and the same errors as the API, from a shell.
  - *Acceptance*: `tests/test_cli.py`, 4 tests, run the README's own commands verbatim;
    check that the mate is reported, that the narrowed-recess warning reaches stderr, and
    that an infeasible parameter exits 2 naming the field.
- [x] **REQ-shareable-links**: Every parameter lives in the URL, so a gear configuration
  can be shared as a link.
  - *Acceptance*: **absent** — `docs/architecture/web-ui.md` describes reading the hash
    into the inputs, but no test is cited in the ingested SPECs for URL round-trip
    fidelity.

### Export

- [x] **REQ-stl-step-export**: Produce STL (for slicing) and STEP (a proper solid for CAD)
  downloads of the generated gear, from the web UI, the HTTP API, and the CLI.
  - *Acceptance*: `test_exports` (both formats produce bytes with the right magic) and
    `test_exported_stl_is_a_closed_consistently_oriented_shell` in `tests/test_model.py`.

### Errors & Deployment

- [x] **REQ-error-contract**: Parameters that cannot make a sound part are rejected (422
  over the API, exit 2 on the CLI) naming the offending fields; dimensions that can be
  trimmed without contradicting an explicit user choice are trimmed instead and reported
  in `warnings`; an impossible mating pair is reported as a warning rather than a
  fabricated centre distance.
  - *Acceptance*: `test_infeasible_parameters_name_their_fields` and the cap-and-warn
    warning-text assertions in `tests/test_calc.py`; the 422-shape tests among the 12
    tests in `tests/test_api.py`.
- [x] **REQ-no-auth-default**: The application ships with no authentication; the compose
  file binds to `127.0.0.1` by default, and exposing it beyond that is the deployer's
  explicit choice (reverse proxy with auth).
  - *Acceptance*: **absent** — documented behavior, not test-asserted in the ingested
    SPECs. Tracked separately as `docs/tech_debt/active/2026-09-21-no-authentication.md`,
    out of scope for this ingest.
- [x] **REQ-docker-multiarch**: Deployable via Docker (and docker compose) for
  `linux/amd64` and `linux/arm64`.
  - *Acceptance*: `docs/review-2026-09-21.md` records `docker compose build` (linux/amd64)
    and `docker build --platform linux/arm64` both clean — a historical verification; see
    `.planning/INGEST-CONFLICTS.md` (INFO) for the historical-vs-live caveat.

## v0.1 Requirements (Milestone: Hardening)

**Work to be done.** Five requirements, all paying down `must` tech debt or closing a
standing blocker — no new gear geometry ships in v0.1. Each cites the debt file or blocker
it retires. Feature work is deferred to the next milestone ("Future Requirements" below).

### Runtime & Concurrency

- [ ] **REQ-cad-off-event-loop**: CAD builds execute outside the serving process, so
  `/api/health` latency no longer scales with the size of the gear someone asked for.
  - *Retires*: `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` (must).
  - *Acceptance*: p95 health latency under load stays within **2× of idle p95**, measured
    with that file's own two scenarios — one 200-tooth fine build in flight, and ten
    concurrent builds. Baseline to beat, on record from the same file: 0.22 s → 0.76 s →
    2.00 s for the first scenario, repeatedly over 5 s for the second (12-core machine).
    The threshold is a property (latency decoupled from build size), not a plucked number;
    the absolute figures are recorded alongside it.
  - *Note*: admission control stays in the web layer and the CLI still never queues (L04).

- [ ] **REQ-measured-memory-ceiling**: The memory ceiling for the multi-process topology is
  measured, `compose.yaml`'s `mem_limit` is set from that measurement, and a superseding
  `Lxx` replaces L07 in `docs/architecture/decision_log.md`.
  - *Why it is separate*: L07's numbers (1.87 GiB → 1.5 GiB → 358 MiB, `mem_limit: 2g` as a
    measured backstop after 1g failed ~5% of requests) assume caches bounded **per process**.
    N workers multiply that. An estimated replacement ceiling is exactly the plausible-but-
    unverified number L08 forbids, so this is a requirement in its own right rather than a
    footnote to the one above — it is the part most likely to be skipped.
  - *Acceptance*: the new ceiling is reported from a measured sweep, not derived
    arithmetically; the superseding decision entry cites the measurement.

### Observability

- [ ] **REQ-structured-logging**: A structured logger is configured at the composition
  boundary (`cli.cmd_serve` / `app.py` startup) and emits the decision branches that already
  exist — build started (with parameter slug), build failed (with exception class), export
  served from cache vs. built, queue refused.
  - *Retires*: `docs/tech_debt/active/2026-09-21-no-structured-logging.md` (must).
  - *Acceptance*: a test asserts the branch records are emitted with their field names — not
    console eyeballing. Field names are chosen once, deliberately, before the first incident
    forces the choice.
  - *Boundary*: `calc.py` stays log-free. It is pure, it runs on every keystroke, and its
    `warnings` output is its diagnostic (L01/AGENTS.md).

### Contracts & Types

- [ ] **REQ-typed-derived-dimensions**: `derive()` returns a `DerivedDimensions` model with
  explicit optional fields instead of `dict[str, Any]`; `disallow_any_explicit` is turned on
  in the mypy config and `make verify` passes with it on.
  - *Retires*: `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` (must), and L14's
    named ratchet with it.
  - *Acceptance*: `make verify` green with the rule enabled; the web UI, CLI and API all read
    the same typed shape, and the OpenAPI document reflects it. The fields the UI already
    reads by name (`detail[].ctx.fields`, `warnings`) keep working.

### Delivery

- [ ] **REQ-ci-verified**: `.github/workflows/ci.yml` is observed executing green in GitHub
  Actions on both supported Python versions — not hand-verified step-by-step.
  - *Retires*: the "CI workflow unverified" blocker carried in `STATE.md` since the
    2026-09-21 bootstrap (source: `docs/plan-2026-09-21.md`).
  - *Acceptance*: a run URL, on a real push, showing the gate and both container checks
    green. Predicting that it would pass is not the same as watching it pass (L13).

## Future Requirements

**Next milestone — features.** Gathered at v0.1 kickoff, deferred deliberately. Not yet
scoped, estimated, or ordered; recorded so they survive the session that named them.

### New gear types
- Helical gears — twisted extrusion; materially heavier OCCT work, which is part of why
  `REQ-cad-off-event-loop` comes first.
- Internal / ring gears.
- Rack — the spur-family special case (infinite radius).
- Bevel gears — **needs a product-scope decision first.** Bevel is not an extension of the
  involute spur pipeline in `calc.py`, and it contradicts what `PROJECT.md` says this is
  ("A parametric involute spur gear generator"). Either the product definition changes or
  this does not belong here; that is a decision, not a geometry task.

### Tooth and bore detail
- Chamfers on the teeth. (The chamfer that ships today is on the **bore**, per
  `REQ-bore-and-fillets` — tooth-tip chamfer is new geometry.)
- Additional centre-hole types: keyway, hex, spline, and similar. (D-flat and round
  **already ship** under `REQ-bore-and-fillets` — only the new profiles are work.)

### Web / body cutouts
- Parametric body cutouts: spoke arms, circular lightening holes, hexagonal patterns, each
  with their own parameters. Every added boolean cut makes builds heavier — a second reason
  `REQ-cad-off-event-loop` is prerequisite rather than optional.

### Carried over from `docs/ideas/`
- Trochoidal (vs. radial) root fillet below the base circle — would supersede L10's
  documented approximation.
- A browser-driven test for the 3D viewer — a test, not a user feature; the cost of the
  first one is the whole question.

**Deferred `nice` tech debt** (out of v0.1 by explicit choice, each keeps its own trigger in
`docs/tech_debt/active/`): coverage floor in the gate, CadQuery `Shape` typing cleanup,
server-side cancellation on client abort, Enji Guard / Dependabot CVE alerting.

## Out of Scope

Explicitly excluded from **milestone v0.1**, with reasoning. Items merely *deferred* live
under "Future Requirements" above — this table is for things that are not planned work.

| Feature | Reason |
|---------|--------|
| Any new gear geometry (helical, internal/ring, rack, bevel, tooth chamfers, new bore profiles, body cutouts) | v0.1 is a hardening milestone by explicit decision — features ship next milestone, on top of a runtime that no longer stalls and a response contract that is type-checked |
| Coverage floor in the gate | `docs/tech_debt/active/` (nice); a ten-minute measured item, deliberately not bundled with the `must` work |
| CadQuery `Shape` typing cleanup | `docs/tech_debt/active/` (nice); its own file says it wants its own tested change to the geometry pipeline, not a ride-along |
| Server-side cancellation on client abort | `docs/tech_debt/active/` (nice); its own trigger is "after the process pool lands, which would make real cancellation possible" — so it is correctly *after* v0.1, not in it |
| Enji Guard / CVE alerting | `docs/tech_debt/active/` (nice); needs an OAuth click by a repo admin, or the narrower free equivalent (Dependabot alerts) — not code work |
| Authentication | Deliberate for a localhost/single-user tool; `REQ-no-auth-default` is *satisfied* by its absence. Its debt file's own next step is "Nothing now". Revisit only if the binding changes or it is deployed beyond one machine |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-involute-geometry | Phase 1 | Complete (shipped v0) |
| REQ-bore-and-fillets | Phase 1 | Complete (shipped v0) |
| REQ-face-recesses | Phase 1 | Complete (shipped v0) |
| REQ-measurement-aids | Phase 1 | Complete (shipped v0) |
| REQ-three-interfaces | Phase 1 | Complete (shipped v0) |
| REQ-cli-parity | Phase 1 | Complete (shipped v0) |
| REQ-shareable-links | Phase 1 | Complete (shipped v0) |
| REQ-stl-step-export | Phase 1 | Complete (shipped v0) |
| REQ-error-contract | Phase 1 | Complete (shipped v0) |
| REQ-no-auth-default | Phase 1 | Complete (shipped v0) |
| REQ-docker-multiarch | Phase 1 | Complete (shipped v0) |
| REQ-cad-off-event-loop | Phase 2 | Pending |
| REQ-measured-memory-ceiling | Phase 2 | Pending |
| REQ-structured-logging | Phase 3 | Pending |
| REQ-typed-derived-dimensions | Phase 4 | Pending |
| REQ-ci-verified | Phase 5 | Pending |

**Coverage:**
- v0 requirements (shipped baseline): 11 total, 11 mapped, 0 unmapped ✓
- v0.1 requirements (this milestone): 5 total, 5 mapped, 0 unmapped ✓ (Phase 2: 2,
  Phase 3: 1, Phase 4: 1, Phase 5: 1)

---
*Requirements defined: 2026-09-21*
*Last updated: 2026-09-21 — milestone v0.1 (Hardening) roadmap written; all 5 requirements mapped to Phases 2-5.*
