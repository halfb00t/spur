# spur

## What This Is

A parametric involute spur gear generator. Set parameters (module, tooth count, pressure
angle, profile shift, backlash, bore, face recesses...) and get a live 3D preview, the
numbers you'd measure on the real part, and an STL (slicing) or STEP (CAD) download — from
a web UI, an HTTP API, or a CLI, all driven by one parameter model. Built on CadQuery
(OpenCascade), FastAPI, and three.js.

*Source: root `README.md`, via `.planning/intel/context.md` ("Product summary").*

## Core Value

A number this tool prints is a number someone will cut metal to — so every dimension is
either computed honestly or reported as a warning, never guessed (L08). Everything else
(the UI, the API, the CLI) exists to get parameters in and a trustworthy gear out.

## Current State

**Shipped: v0.1 Hardening (2026-09-25).** The generator is operable under real load and
its contracts are honest: CAD builds run in worker processes off the event loop with a
measured memory ceiling (L17–L19); structured logging at the composition boundary (L20);
a typed `DerivedDimensions` contract with `disallow_any_explicit` on (L21); CI is the
structural merge gate on Python 3.12 only (L22, L23); the five debt items the milestone
itself surfaced are retired (L24, L25). Record: `.planning/MILESTONES.md`,
`milestones/v0.1-ROADMAP.md`, `milestones/v0.1-MILESTONE-AUDIT.md` (status `tech_debt`:
5/5 requirements, 14/14 integration, 6/6 flows, 6 deferred debt items with triggers).

Codebase at `1173d21`: 6,410 lines of Python, 361 lines of hand-written UI JS, 191 tests,
31 pinned runtime packages (unchanged over v0.1), `make verify` green.

## Next Milestone Goals

Not yet defined — `/gsd-new-milestone` picks deliberately from the candidates gathered at
v0.1 kickoff (`milestones/v0.1-REQUIREMENTS.md`, "Future Requirements"): helical, internal
and rack gears (bevel needs a product-scope decision first — it contradicts "involute spur
gear generator"), tooth chamfers, keyway/hex/spline bores, parametric body cutouts
(spokes, lightening holes, hex patterns), the trochoidal root fillet (would supersede
L10), and a browser-driven viewer test. Every one of these makes builds heavier, which is
why v0.1's process pool came first.

## Requirements

### Validated

v0 items shipped in the baseline already in the tree; v0.1 items shipped 2026-09-25. All
confirmed by `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan,
pytest — L13). Full list with sources and acceptance evidence:
`milestones/v0.1-REQUIREMENTS.md`.

- ✓ REQ-involute-geometry — involute tooth geometry from module/teeth/pressure
  angle/profile shift — v0
- ✓ REQ-bore-and-fillets — backlash, root fillets, D-flat/round bore with clearance and
  chamfer — v0
- ✓ REQ-face-recesses — annular face recesses, one or both sides, filleted floors,
  capped-not-refused when oversized — v0
- ✓ REQ-measurement-aids — caliper, span (Wildhaber), centre distance to a mate — v0
- ✓ REQ-shareable-links — every parameter lives in the URL — v0
- ✓ REQ-stl-step-export — STL and STEP export from all three interfaces — v0
- ✓ REQ-three-interfaces — web UI, HTTP API, and CLI on one `GearParams` model — v0
- ✓ REQ-error-contract — refuse (422 / exit 2) vs. cap-and-warn vs. report-nothing — v0
- ✓ REQ-no-auth-default — no built-in auth; binds to `127.0.0.1` by default — v0
- ✓ REQ-docker-multiarch — Docker/compose for `linux/amd64` and `linux/arm64` — v0
- ✓ REQ-cli-parity — `spur serve`/`info`/`export` match the API's numbers and errors — v0
- ✓ REQ-cad-off-event-loop — CAD builds run in `BuildPool` worker processes and the serving
  process is import-linter-forbidden from the kernel; `/api/health` p95 under one build
  within 2× idle on every run recorded, the ten-concurrent scenario accepted with caveat,
  not demonstrated (L18; waived on the Runs 1–8 evidence) — Phase 2
- ✓ REQ-measured-memory-ceiling — the N=1/2/4 container sweep measured the ceiling;
  `compose.yaml` `mem_limit: 4g` is N=2's 2878.5 MiB peak × 1.3 headroom, not L07's
  formula multiplied out (L17) — Phase 2
- ✓ REQ-structured-logging — `src/spur/records.py` (stdlib `logging`, project-owned JSON
  formatter, one object per line on stderr) configured idempotently at both composition
  points; `build.started`, `build.failed`, `export.served`, `queue.refused` and
  `worker.replaced` proven by `caplog`/`json.loads` tests; uvicorn's own records share the
  stream; post-review fix renders a `traceback` field for records that carry `exc_info`
  (L20) — Phase 3
- ✓ REQ-typed-derived-dimensions — `derive()` returns a frozen 19-field `DerivedDimensions`
  model (every key always present, `null` where it does not apply); `/api/health` is a
  `HealthReport` with `pool: PoolState | None`; `/api/schema` is pydantic's own
  `JsonSchemaValue`; mypy's `disallow_any_explicit` is on globally with `make verify` green
  (104 tests) via the pydantic plugin's `init_typed`/`init_forbid_extra`, no suppressions;
  `spur info --mate-teeth` refuses the range the API refuses (L21 supersedes L14) — Phase 4
- ✓ REQ-ci-verified — CI is the merge gate for `main`: a repo-owned `commit-msg` hook
  (`scripts/skip_tokens.py`) refuses the six GitHub Actions skip tokens; `make pr.land PR=N`
  refuses a red, missing, stale or token-carrying head and exits non-zero unless the squash
  commit gets a run, printing its URL; the ruleset on `main` requires `test (3.12)`,
  `vendor-bundle` and `image` green on an up-to-date head plus a pull request (read back
  live); Python 3.12 only (L23 supersedes L01's floor); the "CI workflow unverified"
  blocker retired citing runs 35963114939 and 36088409707; the pr.land cut-line bypass
  (05-REVIEW CR-01) closed by gap plan 05-06 and re-verified 5/5 (L22, L23) — Phase 5
- ✓ Phase 6 tech-debt closure (no REQ-ID: the phase was added to v0.1 after
  `REQUIREMENTS.md` was written; its contract is `06-CONTEXT.md` D-01…D-11) — the
  commit-msg hook scans the whole buffer git hands it (no cut line, no `GIT_EDITOR`
  read; refusals name the line and the `-v` way out); `make pr.land` refuses a run whose
  own `conclusion` is not `success` (proven live on run 36116930241), resolves
  `jobs.<id>.name` overrides in the drift test, and after the merge reports only what it
  observed (read error / Actions link / a token read from the squash commit); STL export
  meshes `shape.copy()` so the cached `cq.Solid` never carries a mesh (`.BoundingBox()`
  exact, content-equivalent exports, the autouse cache reset deleted); five debt files
  retired in their fixing commits; L24/L25 carry the measured numbers; verified 9/9,
  review clean, 13/13 threats closed, `make verify` 191 tests — Phase 6

### Active

- *(none — v0.1 shipped; the next milestone's requirements are written by
  `/gsd-new-milestone` into a fresh `REQUIREMENTS.md`)*

### Out of Scope

<!-- Not excluded as bad ideas — deferred, and already tracked under their own lifecycle per CLAUDE.md, not repeated here. -->

- Trochoidal (vs. radial) root fillet below the base circle — `docs/ideas/` idea; L10 is
  the documented, accepted approximation for now.
- A browser-driven test for the 3D viewer — `docs/ideas/` idea; not required for v0's
  `make verify` gate.
- The six items still in `docs/tech_debt/active/` after Phase 6 — five `nice` (coverage
  floor, CadQuery `Shape` typing, server-side request cancellation, Enji Guard / CVE
  alerting, no built-in authentication) and one `must` (the ten-concurrent latency bar
  waived under L18, Phase 2) — deferred, each with its own trigger.

## Context

- **This product already ships.** `spur` is a working generator with a web UI, HTTP API,
  and CLI; `make verify` passes at the current commit. This PROJECT.md documents a shipped
  v0 baseline, not upcoming work.
- The 2026-09-21 audit (`docs/review-2026-09-21.md`, findings F1–F8) is history: every
  finding — the unguarded Newton `centre_distance` solver, unbounded-by-bytes caches,
  infeasible absolute-mm defaults, no admission control, an under-pinned dependency
  closure, a `root_thickness` measured at the wrong radius, unused image weight, and
  assorted structure/test/CI gaps — was remediated per `docs/plan-2026-09-21.md` and is
  reflected as already-fixed in the live SPECs synthesized into `.planning/intel/`. Treated
  as history, not live requirements.
- Full codebase map: `.planning/codebase/ARCHITECTURE.md`, `STACK.md`, `TESTING.md`,
  `CONCERNS.md` (produced by `/gsd-map-codebase`, 2026-09-21, verified against the tree).
- Ingest intel: `.planning/intel/SYNTHESIS.md` (entry point), `decisions.md`,
  `requirements.md`, `constraints.md`, `context.md`; conflict report at
  `.planning/INGEST-CONFLICTS.md` (0 blockers, 0 warnings, 5 info).
- Tech debt (own lifecycle, `docs/tech_debt/INDEX.md`): 6 active after v0.1 — 1 `must`
  (the waived ten-concurrent latency bar, `2026-09-23-concurrent-latency-bar-waived.md`,
  L18) and 5 `nice` (coverage floor, CadQuery `Shape` typing, server-side cancellation,
  no authentication, Enji Guard); 10 resolved, all during v0.1. Ideas backlog:
  `docs/ideas/` — 3 items (trochoidal root fillet, browser test for the viewer, measure or
  soften the Pi 5 claim).
- v0.1 process: phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land
  only through `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code.
  The GSD verifier fingerprints `.planning/STATE.md`, so every phase reads `stale` after
  its own bookkeeping commit — v0.1 closed as an override on proven-identical trees (see
  `MILESTONES.md`).

## Constraints

- **Runtime**: Python 3.12 only — `cadquery-ocp` publishes wheels for nothing newer, and
  the floor is L23's; Docker image pins `python:3.12-slim-bookworm` (L01, L12, L23).
- **Stack**: CadQuery/OpenCascade for the solid, FastAPI + Pydantic v2 + uvicorn for the
  API, argparse for the CLI, vanilla JS + a vendored tree-shaken three.js bundle for the
  viewer (no Node at runtime), pytest, Docker + compose, GitHub Actions (L01, L11).
- **Module boundaries**: `calc.py` never imports the CAD kernel and does no I/O (runs on
  every keystroke); `model.py` is the only doorway to `cadquery`/`OCP`, no vendor object
  escapes it; `cli.py` never imports `app`/`fastapi`/`starlette`. Enforced by import-linter
  contracts, not discipline (L01/AGENTS.md, L04, L06).
- **Concurrency**: CAD builds run in `BuildPool` worker processes (`SPUR_BUILD_WORKERS`,
  default 2), routed by parameter-hash affinity, each build bounded by
  `SPUR_BUILD_TIMEOUT=30s` (~4× the worst measured build); the serving process cannot
  import the kernel (fourth import-linter contract). One `RLock` still wraps every
  OpenCascade call inside a worker (OCCT is not thread-safe), but it is per worker now, so
  concurrency across gears buys throughput too (L18 supersedes L06). Admission control
  (bounded build queue, `503` + `Retry-After`) lives in the web layer, never the CLI
  (L04); model-body gzip runs inside that slot at a measured `compresslevel=1` (L19).
- **Memory**: a parent byte budget (export cache, `SPUR_EXPORT_CACHE_MB`) plus N × the
  per-worker solid cache (`SPUR_SOLID_CACHE`); `compose.yaml` sets `mem_limit: 4g` from
  the N=2 sweep's 2878.5 MiB peak × 1.3 headroom, confirmed at zero failures — swept, not
  derived (L17 supersedes L07).
- **Defaults**: absolute millimetres, tuned to the 19-tooth m=1.75 gear this project
  started from; they never rescale — every shareable link that omits a field depends on
  them (L05).
- **Error contract**: a direct conflict between two explicit user choices is a `422`
  naming the fields; a trimmable dimension is capped and reported in `warnings`; an
  unsolvable centre distance is `None` plus a warning, never a plausible number (L03, L08).
- **Dependency pinning**: `requirements.txt` is the full resolved closure (31/31 packages),
  generated by `docker/refresh-requirements.sh`, installed `--no-deps`; never hand-edited
  (L12).
- **Gate**: `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan,
  pytest, ~11s warm, no Docker) is the standard for "done"; `make check` adds the two
  container checks CI also runs (L13); `main` is landed only through `make pr.land PR=N`
  behind the ruleset (L22, L25). mypy strict with `disallow_any_explicit` on globally, no
  suppressions (L21 supersedes L14). `TRY003` off — error messages are the product (L15).
  No automatic formatter (L16).

## Key Decisions

Full log: `docs/architecture/decision_log.md` (single source of locked decisions — do not
re-litigate). Ingested verbatim into `.planning/intel/decisions.md`; carried here for
quick reference.

| ID | Decision | Outcome |
|----|----------|---------|
| L01 | Stack: Python 3.10–3.12, CadQuery/OCCT, FastAPI+Pydantic v2+uvicorn, argparse, vanilla JS + vendored three.js, pytest, Docker, GitHub Actions — detected, not chosen | ✓ Good — the 3.10 floor is superseded by L23 (3.12 only) |
| L02 | One `GearParams` model drives the web form, CLI flags, and API query params | ✓ Good |
| L03 | Cap and warn a trimmable dimension; refuse (422) a direct conflict — never guess | ✓ Good |
| L04 | Admission control (bounded build queue) lives in the web layer, not `model.py`; CLI never queues | ✓ Good |
| L05 | Defaults are absolute mm and never rescale; shareable links depend on them | ✓ Good |
| L06 | One `RLock` around every OpenCascade call; concurrency buys latency, not throughput | Superseded by L18 — the lock stays, its "not throughput" consequence is retired |
| L07 | Bounded caches (entries / bytes) + `malloc_trim(0)` after cache-missing export — measured 1.87 GiB → 1.5 GiB → 358 MiB | Superseded by L17 — ceiling re-swept on the N-worker topology |
| L08 | `centre_distance()` returns `None` (bisection, not Newton) rather than a confidently wrong number | ✓ Good |
| L09 | Root fillets solved analytically in the 2D outline, ~50× faster than OCCT's fillet operator | ✓ Good |
| L10 | Radial (not trochoidal) root below the base circle, with an undercut warning | ⚠️ Revisit — trochoidal fillet is a tracked idea |
| L11 | three.js vendored as a committed, CI-byte-checked bundle; no Node at runtime | ✓ Good |
| L12 | `requirements.txt` is a generated, full pinned closure installed `--no-deps` | ✓ Good |
| L13 | `make verify` is the gate (dev shell, pre-commit, CI); `make check` adds container checks | ✓ Good |
| L14 | mypy strict, `disallow_any_explicit` off as a ratchet (`/api/info` is honest `dict[str, Any]`) | ✓ Superseded by L21 (Phase 4) — ratchet retired, debt file resolved |
| L15 | `TRY003` disabled; the rest of `TRY` on — error messages name the field and say what to change | ✓ Good |
| L16 | No automatic formatter — would flatten 648 lines of hand-set comment alignment | ✓ Good |
| L17 | Memory ceiling = parent byte budget + N × per-worker solid cache, swept on the real topology: `mem_limit: 4g` from N=2's 2878.5 MiB peak × 1.3 (supersedes L07) | ✓ Good — measured, zero failures at the limit |
| L18 | The `RLock` is per worker, not global; "concurrency buys latency, not throughput" retired. Single build within 2× idle p95 on every run; ten-concurrent accepted with caveat, not demonstrated (Runs 1–8: 1.31x–2.45x) (supersedes L06) | ⚠️ Caveat — must debt `2026-09-23-concurrent-latency-bar-waived.md` |
| L19 | Model bodies gzip-encoded at measured `compresslevel=1` (51.5 ms vs 788 ms at level 9 on a 9 MB STL), inside the admission slot, cached once per encoding | ✓ Good |
| L20 | Structured JSON logging: stdlib `logging` + project-owned formatter, one object per line on stderr, `configure()` at both `cli.cmd_serve` and `app.lifespan()` (idempotent — uvicorn's spawn-based workers need the second site), parent process only, INFO default via `SPUR_LOG_LEVEL` | ✓ Good — post-review fix: records carrying `exc_info` render a `traceback` field (CR-01), `model()` catch-all logs `build.failed` (WR-01) |
| L21 | `disallow_any_explicit` on globally, no per-module override; the published responses are typed models (`DerivedDimensions`, `HealthReport`/`PoolState`); the pydantic mypy plugin's `init_typed`/`init_forbid_extra` retire the six class-line errors instead of six per-class suppressions; `Any` is never written — `object` narrowed at use, a library's own alias keeps the library's `Any` (supersedes L14) | ✓ Good — `make verify` green under the rule (104 tests); `--mate-teeth 0` now exits 2 like the API's 422 |
| L22 | CI is the merge gate: a ruleset on `main` requires `test (3.12)`, `vendor-bundle`, `image` green on an up-to-date head plus a pull request; a repo-owned `commit-msg` hook refuses the six skip tokens; the squash message is PR title + body; `main` is landed only via `make pr.land PR=N`, which refuses a red, stale, missing or token-carrying head and prints the squash commit's run URL | ✓ Good — ruleset read back live; gap plan 05-06 closed CR-01; the residual hand-typed cut line and the run-conclusion blind spot were retired in Phase 6 (L25 amends this entry); Phase 6 itself landed through the gate as PR #5 → `1173d21`, run 36145323487 |
| L23 | Python 3.12 only — `requires-python`, ruff `target-version`, the CI matrix, the Makefile interpreter and the README agree (supersedes L01's 3.10 floor; `cadquery-ocp` publishes wheels for nothing newer) | ✓ Good — `make verify` green on 3.12 (183 tests); CI job is `test (3.12)` alone |
| L24 | A cached solid never carries a mesh: STL export runs `exportStl` on `shape.copy()`, never on the process-global cached `cq.Solid` (`Clean_s` rejected: 4–13 % faster but leaves the mesh on the cached object for the whole export window); copy costs +1.4 to +17.6 ms per export and +3.2 to +7.7 MiB peak RSS on a 200-tooth fine export, measured; the autouse cache-reset fixture deleted | ✓ Good — `.BoundingBox()` exact after any export, a preview after a fine export is a preview (9,066 vs 46,278 triangles) |
| L25 | The merge gate reads the whole commit message and the run's own verdict (amends L22): the commit-msg hook takes git's entire buffer with no cut line; `pr.land` refuses `conclusion != success` and runs from an up-to-date `main`; after the merge it reports only what it observed; the read-to-merge window rests on the ruleset's up-to-date policy, not on anything `pr.land` reads (`--match-head-commit` pins the head, not the base) | ✓ Good — proven live on run 36116930241 and commits b72b0e1 / 20b63e4 |

## Success Metric (Milestone v0.1)

Set by the human at milestone start — no ingested document derived it. All four held at
close (2026-09-25); outcomes in italics:

1. **Measured event-loop latency.** `/api/health` p95 stays under an agreed threshold with
   a named build in flight, measured against the baseline on record (0.22 s → 0.76 s →
   2.00 s under one 200-tooth fine build, 12-core machine). *Met for the single-build
   scenario on every recorded run (L18); the ten-concurrent bar was waived on the Runs 1–8
   evidence and is `must` debt.*
2. **`disallow_any_explicit` on.** `make verify` passes with the rule enabled; L14's named
   ratchet is retired rather than re-deferred. *Met — L21, `make verify` green.*
3. **Logs answer an incident.** A named set of decision branches — build started, build
   failed, export served from cache or built, queue refused — is observable in structured
   output, proven by a test rather than by reading the console. *Met — L20, five records
   under `caplog` tests.*
4. **The three `must` debt files are resolved.** `Status: resolved`, commit sha recorded,
   `git mv`'d into `docs/tech_debt/resolved/`, INDEX rows moved — in the same commits as
   the fixes, per `CLAUDE.md`. *Met — retired in Phases 2–4; Phase 6 retired five more
   surfaced during the milestone (10 resolved in total).*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-25 after v0.1 milestone (`/gsd-complete-milestone v0.1`).*
