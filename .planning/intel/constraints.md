# Constraints

Extracted from the 15 SPEC documents in this ingest set. Type taxonomy used below:
`api-contract` (HTTP/CLI/exported interface behavior), `schema` (data/module shape),
`nfr` (performance, memory, reliability, coverage budgets), `protocol` (internal module
interaction rules: import boundaries, build pipelines, failure propagation).

No SPEC in this set was found to contradict a locked ADR decision; all SPECs elaborate
the `decisions.md` entries they cite. See `INGEST-CONFLICTS.md` — no auto-resolved
ADR-vs-SPEC entries were needed.

## Module dependency direction (import-linter contracts)
- source: docs/architecture/overview.md
- type: protocol
- content: The dependency direction is enforced, not hoped for — `pyproject.toml` declares import-linter contracts and `make verify` fails on a violation. `calc.py` must never import the CAD kernel; the CLI must never import the web layer.

## Source-of-truth principles
- source: docs/architecture/overview.md
- type: nfr
- content: Nothing is stored — every answer is derived from `GearParams` on demand; caches are a speed optimisation, safe to lose (L07). The parameters live in the URL (L05). The dependency closure is `requirements.txt`, generated (L12). The viewer bundle is built from `web/`, and CI proves reproducibility (L11).

## CLI command surface generated from GearParams
- source: docs/architecture/cli.md
- type: api-contract
- content: Gear flags are generated from `GearParams.model_fields`, including help text and the bracketed default; `Literal` fields become `choices`. A new parameter appears in the CLI with no edit here (L02). `_params(ns)` builds the model only from flags actually passed — omitted flags take the model's defaults rather than `None`.

## CLI error and exit-code contract
- source: docs/architecture/cli.md
- type: api-contract
- content: A `ValidationError` becomes `error: <field>: <message>` on stderr with exit 2, the same information the API puts in `detail[].ctx.fields`. `BuildError` becomes `error: <kernel message>`. Nothing is written when the build fails. `spur export` derives format from file extension (`.stp` → `step`) unless `--format` overrides it, and prints any `warnings` to stderr after writing.

## CLI must not inherit web-serving policy
- source: docs/architecture/cli.md
- type: protocol
- content: The CLI does not import `app`, `fastapi` or `starlette`; an import-linter contract enforces that (L04). `spur serve` starts uvicorn by import string (`"spur.app:app"`), which is a string, not an import. `calc` and `model` are imported inside subcommand functions so `spur --help`/`spur info` do not pay for loading OpenCascade.

## HTTP endpoint contract
- source: docs/architecture/http-api.md
- type: api-contract
- content: `GET /` (the UI), `GET /api/health`, `GET /api/schema`, `GET /api/info?…[&mate_teeth=N]`, `GET /api/model.{stl,step}?…`. `InfoQuery` adds `mate_teeth`, `ModelQuery` adds `quality`, both subclassing `GearParams`; `_gear(q)` strips them back to a plain `GearParams` before anything downstream sees them, so a cache entry is shared across query-model subclasses.

## Admission control (bounded build queue)
- source: docs/architecture/http-api.md
- type: nfr
- content: A bounded, non-blocking semaphore (`SPUR_MAX_QUEUED_BUILDS`, default 4) guards the model endpoints; full → `503` with `Retry-After: 5` (L04). Queueing past that buys latency and memory, not throughput, because every build serialises on the kernel lock anyway (L06).

## HTTP error contract
- source: docs/architecture/http-api.md
- type: api-contract
- content: Infeasible parameters → `422` from `GearParams`'s own validator, offending fields in `detail[].ctx.fields` (L03). `BuildError` from the kernel → `422` with the kernel's message. Queue full → `503` + `Retry-After`. There is no authentication — deliberate, documented in the README, the reason `compose.yaml` binds to `127.0.0.1`.

## Response compression threshold
- source: docs/architecture/http-api.md
- type: nfr
- content: `GZipMiddleware` above 1024 bytes: STEP compresses ~6x, STL ~4x.

## UI form generated from API schema
- source: docs/architecture/web-ui.md
- type: protocol
- content: The UI knows no gear geometry — the form is generated from `GET /api/schema`, including each field's group, unit and step, so a parameter added in `params.py` appears in the UI with no edit (L02).

## Vendored, Node-free runtime bundle
- source: docs/architecture/web-ui.md
- type: nfr
- content: The runtime needs no Node (L11). `static/vendor/three.bundle.min.js` is a committed, tree-shaken esbuild output; `web/` exists only to regenerate it, and CI fails if the committed bytes differ from a fresh build.

## Relative URLs / sub-path deployment
- source: docs/architecture/web-ui.md
- type: protocol
- content: All URLs are relative, so `SPUR_ROOT_PATH` works — with the caveat that the proxy must redirect `/spur` to `/spur/`, or the browser resolves `static/app.js` one level too high.

## Generated pinned dependency closure
- source: docs/architecture/packaging.md
- type: nfr
- content: `requirements.txt` is generated, not written (L12): full resolved closure, 31 of 31 packages, installed with `--no-deps`. Regenerate with `make lock` (`docker/refresh-requirements.sh`); never hand-edit a line, because with `--no-deps` pip will not flag a bumped version that breaks the closure.

## Container hardening
- source: docs/architecture/packaging.md
- type: nfr
- content: `compose.yaml` is hardened and measured: `127.0.0.1` binding, `read_only`, `tmpfs /tmp` capped at 256 MB, `cap_drop: ALL`, `no-new-privileges`, and `mem_limit: 2g` — a number set after `1g` failed ~5% of requests under a sweep (L07).

## Build-time smoke test
- source: docs/architecture/packaging.md
- type: nfr
- content: `docker/smoke.py` runs during the image build and exercises the kernel, both exporters and the ASGI app, so a wrong dependency closure fails the build instead of production.

## The verify/check gate
- source: docs/architecture/packaging.md
- type: protocol
- content: `make verify` = ruff + mypy `--strict` + import-linter + unfinished-work scan + pytest (~11s warm, no Docker), run in the pre-commit hook, CI (Python 3.10 and 3.12), and `make worktree.land` before merge (L13). `make check` = verify + the in-image smoke test + the vendored-bundle byte check (needs Docker).

## calc.py module boundary (no CAD kernel, no I/O/state)
- source: docs/architecture/gear-maths/strategy.md
- type: protocol
- content: No CAD kernel, ever — enforced by an import-linter contract, not discipline (L13). No I/O, no state, no logging; pure functions of `GearParams`, same input same answer, always. It decides; it does not act — `model.py` consumes the effective values `calc.py` returns rather than re-deriving them.

## calc.py three-layer architecture
- source: docs/architecture/gear-maths/tactics.md
- type: schema
- content: Layer 1 `Profile` (frozen dataclass of radii + half-tooth angle, from `profile(p)`, every other function starts here); layer 2 Rules (`bore_radius`, `recess_radii`, `root_fillet`, `recess_fillet`, `_tooth`, `check`) each returning the effective, already-capped value; layer 3 Reports (`derive(p)`, `with_mate(info, p, z2)`) assembling the JSON document including `warnings`.

## calc.py output contract and rounding
- source: docs/architecture/gear-maths/tactics.md
- type: api-contract
- content: `check(p) -> list[(message, fields)]`; `derive(p) -> dict[str, Any]` including `warnings: list[str]`, keys vary with parameters (recess fields `None` when there is no recess); `with_mate(info, p, z2)` adds `mate_teeth`/`centre_distance` or a warning plus `None`. Reported values are rounded to 3 decimals (µm) at the boundary in `derive()`; internal arithmetic is full double precision.

## centre_distance solver
- source: docs/architecture/gear-maths/tactics.md
- type: nfr
- content: `centre_distance()` solves `inv(aw) = inv(α) + 2·tan(α)·Σx/Σz` for the working pressure angle by bisection over `(0, 89°)`, because `inv` is monotonic there and bisection has no failure mode that returns a plausible wrong answer (L08).

## calc.py physical constants and layout
- source: docs/architecture/gear-maths/implementation.md
- type: schema
- content: `src/spur/calc.py`, 270 lines, no classes but `Profile`. `MIN_WALL`, `MIN_TIP_FDM`, `MIN_RECESS_WIDTH` are the three physical constants the rules are written against, in mm. Function table: `inv`, `Profile`/`profile`, `bore_radius`, `recess_radii`, `root_fillet`/`recess_fillet`, `_tooth`, `check`, `span_measurement`, `derive`, `_involute_angle`, `centre_distance`, `with_mate`.

## GearParams field metadata drives UI/CLI
- source: docs/architecture/gear-maths/implementation.md
- type: schema
- content: `src/spur/params.py` — field metadata (`group`, `unit`, `step`) travels through the JSON schema into the web form, so a new field appears in the UI and the CLI without either being edited. `_feasible()` is the model validator that calls `check()`; it imports `calc` locally to keep the module import graph one-directional.

## Three-way failure handling in calc.py
- source: docs/architecture/gear-maths/errors_and_logging.md
- type: protocol
- content: Refuse (a conflict between two things the user set explicitly — `check()` returns the message and field names, `GearParams` raises `PydanticCustomError("infeasible")`, FastAPI turns it into `422`). Cap and warn (a requested dimension trimmable without contradicting an explicit choice — the capping function returns the effective value silently, `derive()` adds the sentence to `warnings`). Report nothing (`centre_distance()` returns `None` where no working pressure angle exists, `with_mate()` states why in a warning) (L03, L08).

## No logging in calc.py
- source: docs/architecture/gear-maths/errors_and_logging.md
- type: nfr
- content: None, deliberately. This code runs on every keystroke; it is pure, and its output *is* its diagnostic — `warnings` in the response says what was changed and why.

## gear-maths test coverage
- source: docs/architecture/gear-maths/tests.md
- type: nfr
- content: `tests/test_calc.py`, 21 unit tests, all pure. Gaps: no property-based test over the whole feasible parameter space (the centre-distance sweep is the closest thing, hand-rolled); no coverage floor in the gate yet (references `docs/tech_debt/active/2026-09-21-no-coverage-floor.md`, out of scope for this ingest).

## model.py is the kernel's only doorway
- source: docs/architecture/solid-model/strategy.md
- type: protocol
- content: `cadquery` and `OCP` are imported here and in no other module; no CadQuery object escapes past `export()`, which returns `bytes`. An import-linter contract fails the build on a violation, verified to actually break when one is introduced.

## model.py does not decide, does not queue
- source: docs/architecture/solid-model/strategy.md
- type: protocol
- content: Which fillet radius fits, whether a recess fits at all, whether the parameters are buildable — all answered in `calc.py` before anything here runs (L03). Concurrency policy is the web layer's (L04); this module holds one lock because the kernel requires it (L06), and refuses nothing.

## Kernel tolerance convention
- source: docs/architecture/solid-model/strategy.md
- type: nfr
- content: `TOL = 1e-6` mm is how kernel output is matched back to the numbers that were asked for.

## Solid build pipeline
- source: docs/architecture/solid-model/tactics.md
- type: protocol
- content: `_build(p)`: `profile(p)` → `_gear_blank` (outline, extrude) → `_cut_face_recesses` (annulus cut, floor fillets) → `_cut_bore` (circle or D, rim chamfers) → one validated Solid. Edge re-selection is isolated: `_groove_floor_edges()` matches circles by radius and z; `_bore_rim_edges()` matches by position, sampling three interior points, because a D-bore rim is not one geometric type.

## model.py output contract
- source: docs/architecture/solid-model/tactics.md
- type: api-contract
- content: `build(p) -> cq.Solid` (used only by tests — a deliberate test affordance, not a public contract); `export(p, fmt, quality) -> bytes` (what `app.py` and `cli.py` use); `BuildError` is the only exception that leaves. Invariant, checked rather than assumed: `_build()` asserts exactly one valid solid before returning.

## Solid/export cache bounds
- source: docs/architecture/solid-model/tactics.md
- type: nfr
- content: `SPUR_SOLID_CACHE` (entries, default 4) and `SPUR_EXPORT_CACHE_MB` (megabytes, default 64), both read through `int_env()`, both per worker process. `build()`/`export()` take `_LOCK`, then go through `_build_cached` (an `lru_cache` on the parameter object) and `_EXPORTS` (an LRU bounded by total bytes).

## model.py layout and constants
- source: docs/architecture/solid-model/implementation.md
- type: schema
- content: `src/spur/model.py`, ~320 lines, four bands separated by comment rules (kernel housekeeping; 2D outline; the part; picking geometry back out; build and export). Constants: `TESSELLATION` (linear/angular deflection per quality), `FLANK_POINTS = 16`, `TOL = 1e-6`.

## Export via temp file in capped tmpfs
- source: docs/architecture/solid-model/implementation.md
- type: nfr
- content: `_write_export()` writes into a `TemporaryDirectory` and reads the bytes back, because CadQuery's exporters take a path. In the container `/tmp` is a size-capped tmpfs, so a huge STL fails there rather than eating the memory limit.

## model.py failure contract
- source: docs/architecture/solid-model/errors_and_logging.md
- type: protocol
- content: `_build()` raises `BuildError` when the result is not exactly one valid solid (a positive check on the invariant, not an exception handler). `_build_checked()` catches all `Standard_Failure` subclasses OCCT can raise and re-raises as `BuildError(f"Geometry kernel failed ({type(exc).__name__}); try smaller fillets or chamfers.")`, chaining the original. `BuildError` is the only exception the module lets out — `app.py` → `422`, `cli.py` → exit 2.

## Memory as a measured failure mode
- source: docs/architecture/solid-model/errors_and_logging.md
- type: nfr
- content: Caches are bounded (L07), arenas are returned after each cache-missing export, and `compose.yaml` sets `mem_limit: 2g` as the backstop — measured, after `1g` failed ~5% of requests under a sweep.

## solid-model test coverage
- source: docs/architecture/solid-model/tests.md
- type: nfr
- content: `tests/test_model.py`, 13 integration tests against the real kernel (no mocks — mocking OpenCascade would test the mock). Gaps: nothing tests cache eviction or the `_BlobCache` byte budget directly; nothing asserts the L07 memory behaviour automatically (the numbers in `docs/plan-2026-09-21.md` came from a manual sweep); no test covers `_release_arenas()` on glibc (no-op on the macOS dev machine). Cold run pages in ~1.4 GB of OpenCascade (~2 minutes); warm ~8s.
