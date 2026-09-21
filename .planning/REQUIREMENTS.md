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

## v1+ Requirements

**None defined.** Forward scope beyond the v0 baseline is undefined — no ingested document
states what ships next. This is intentional per the routing decision that produced this
file, not an omission. See `PROJECT.md` ("Active" requirements) and `ROADMAP.md` for the
candidate pools (`docs/ideas/`, `docs/tech_debt/active/`) the human may draw the next
milestone's requirements from.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Trochoidal root fillet (vs. radial, L10) | Documented, accepted approximation; tracked as a `docs/ideas/` item, not required for v0 |
| Browser-driven viewer test | `docs/ideas/` item; not required for v0's `make verify` gate |
| CAD builds on a process pool (off the event loop) | `docs/tech_debt/active/` (must); root cause of an accepted, mitigated limitation (admission queue + raised health-check timeout) |
| Structured logging | `docs/tech_debt/active/` (must); revisit at first production incident or multi-user deploy |
| Typed `/api/info` response contract | `docs/tech_debt/active/` (must); revisit when a third consumer of the endpoint appears |
| Coverage floor in the gate | `docs/tech_debt/active/` (must); a ten-minute item, deferred, not blocking |
| CadQuery `Shape` typing cleanup, server-side cancellation, Enji Guard / CVE alerting | `docs/tech_debt/active/` (nice); each has its own named trigger |
| Authentication | Deliberate for a single-user/localhost tool (REQ-no-auth-default is itself satisfied by this absence); revisit if ever exposed beyond one machine |

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

**Coverage:**
- v0 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-21*
*Last updated: 2026-09-21 after initial GSD bootstrap from doc ingest + codebase map.*
