# Requirements

No PRD exists anywhere in this ingest set (0 of 22 docs classified PRD). Per orchestrator
instruction, these requirements are derived only from what the root `README.md` and the
15 SPEC documents actually state — never manufactured to fill the gap. Where a source is
silent on acceptance criteria, it is marked absent rather than guessed.

`docs/requirements/README.md` (classified DOC) is a placeholder describing an intended
taxonomy (`functional.md`, `nfr.md`, `errors.md`, `security.md`) — none of those files
exist. It is not a source of requirements; see `context.md`.

## REQ-involute-geometry
- source: README.md; docs/architecture/gear-maths/strategy.md; docs/architecture/gear-maths/tactics.md
- description: Generate involute spur gear tooth geometry from module, tooth count, pressure angle and profile shift.
- acceptance: Flanks are true involutes sampled into B-splines from the base circle (or the root circle, if larger) to the tip (README, "Geometry notes"); `test_default_dimensions` in `tests/test_calc.py` pins the stock gear's numbers (per docs/architecture/gear-maths/tests.md).
- scope: involute flank geometry, module, tooth count, pressure angle, profile shift

## REQ-bore-and-fillets
- source: README.md; docs/architecture/gear-maths/implementation.md
- description: Support backlash, root fillets, and a D-flat or round bore with print clearance and chamfer.
- acceptance: absent — README states the feature; docs/architecture/gear-maths/implementation.md names `bore_radius(p)` and `root_fillet(p)` but no test is cited for this requirement specifically in the ingested SPECs.
- scope: backlash, root fillet, bore (round or D-flat), bore clearance, bore chamfer

## REQ-face-recesses
- source: README.md; docs/architecture/gear-maths/implementation.md; docs/architecture/solid-model/tactics.md
- description: Support annular face recesses on one or both sides, with filleted floors; a recess that does not fit is narrowed (or dropped) rather than refused, per L03.
- acceptance: `test_recess_removes_expected_volume` and `test_a_gear_too_small_for_the_stock_recess_still_builds` in `tests/test_model.py` (docs/architecture/solid-model/tests.md); the cap-and-warn warning-text assertions in `tests/test_calc.py` (docs/architecture/gear-maths/tests.md).
- scope: recess_sides, recess_depth, recess_width, recess_inner_d, recess_fillet

## REQ-measurement-aids
- source: README.md ("Matching an existing gear"); docs/architecture/gear-maths/tactics.md; docs/architecture/gear-maths/tests.md
- description: Provide measurement aids for matching an existing physical gear: caliper reading across tips (corrected for odd tooth counts), span measurement over k teeth (Wildhaber), and centre distance to a mating gear.
- acceptance: `test_caliper_reading_is_short_for_odd_tooth_counts`, `test_span_measurement` (three hand-checked Wildhaber spans), `test_centre_distance_matches_an_independent_solver` — all in `tests/test_calc.py` (per docs/architecture/gear-maths/tests.md).
- scope: span_measurement, centre_distance, with_mate, odd-tooth-count caliper correction

## REQ-shareable-links
- source: README.md; docs/architecture/web-ui.md
- description: Every parameter lives in the URL, so a gear configuration can be shared as a link.
- acceptance: absent — web-ui.md describes reading the hash into the inputs, but no test is cited in the ingested SPECs for URL round-trip fidelity.
- scope: URL hash parameter encoding, shareable model links, SPUR_ROOT_PATH relative URLs

## REQ-stl-step-export
- source: README.md; docs/architecture/http-api.md; docs/architecture/cli.md; docs/architecture/solid-model/tactics.md
- description: Produce STL (for slicing) and STEP (a proper solid for CAD) downloads of the generated gear, from the web UI, the HTTP API, and the CLI.
- acceptance: `test_exports` (both formats produce bytes with the right magic) and `test_exported_stl_is_a_closed_consistently_oriented_shell` in `tests/test_model.py` (docs/architecture/solid-model/tests.md).
- scope: export(p, fmt, quality) -> bytes, GET /api/model.{stl,step}, spur export

## REQ-three-interfaces
- source: README.md; docs/architecture/overview.md
- description: The same gear and the same derived numbers are reachable three ways — a web UI, an HTTP API, and a CLI — all driven by one parameter model (`GearParams`, L02).
- acceptance: absent — asserted architecturally via L02 and overview.md; no single test in the ingested SPECs exercises all three interfaces together for equivalence.
- scope: web UI, HTTP API, CLI, GearParams

## REQ-error-contract
- source: README.md; docs/architecture/http-api.md; docs/architecture/cli.md; docs/architecture/gear-maths/errors_and_logging.md
- description: Parameters that cannot make a sound part are rejected (`422` over the API, exit 2 on the CLI) naming the offending fields; dimensions that can be trimmed without contradicting an explicit user choice are trimmed instead and reported in `warnings`; an impossible mating pair is reported as a warning rather than a fabricated centre distance.
- acceptance: `test_infeasible_parameters_name_their_fields` and the cap-and-warn warning-text assertions in `tests/test_calc.py` (docs/architecture/gear-maths/tests.md); the `422` shape tests among the 12 tests in `tests/test_api.py` (docs/architecture/http-api.md, "Tests").
- scope: check(), 422 responses, exit-2 CLI errors, warnings list, centre_distance None case

## REQ-no-auth-default
- source: README.md; docs/architecture/http-api.md
- description: The application ships with no authentication; the compose file binds to `127.0.0.1` by default, and exposing it beyond that is the deployer's explicit choice (reverse proxy with auth).
- acceptance: absent — documented behavior, not test-asserted in the ingested SPECs. Tracked separately as `docs/tech_debt/active/2026-09-21-no-authentication.md`, out of scope for this ingest per orchestrator instruction.
- scope: authentication posture, default network binding

## REQ-docker-multiarch
- source: README.md; docs/architecture/packaging.md
- description: Deployable via Docker (and docker compose) for `linux/amd64` and `linux/arm64`.
- acceptance: `docs/review-2026-09-21.md` records `docker compose build` (linux/amd64) and `docker build --platform linux/arm64` both clean — a historical verification; see `INGEST-CONFLICTS.md` (INFO) for the historical-vs-live caveat on that document.
- scope: Dockerfile, compose.yaml, multi-arch build

## REQ-cli-parity
- source: README.md; docs/architecture/cli.md
- description: The CLI (`spur serve` / `info` / `export`) offers the same gear, the same numbers, and the same errors as the API, from a shell.
- acceptance: `tests/test_cli.py`, 4 tests, run the README's own commands verbatim; check that the mate is reported, that the narrowed-recess warning reaches stderr, and that an infeasible parameter exits 2 naming the field (docs/architecture/cli.md, "Tests").
- scope: spur serve, spur info, spur export, CLI error formatting
