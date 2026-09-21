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

## Requirements

### Validated

Shipped in the v0 baseline already in the tree and confirmed by `make verify` (ruff, mypy
`--strict`, import-linter, unfinished-work scan, pytest — L13). See `REQUIREMENTS.md` for
the full list with sources and acceptance evidence.

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

### Active

None. **Forward scope for the next milestone is undefined** — nothing in the ingested
README, SPECs, or decision log states what ships after v0. This is a known, accepted
consequence of scoping this ingest to the existing tree, not an omission to silently fill.
The human sets the next milestone's requirements (`/gsd-new-milestone` or equivalent),
optionally drawing from the candidate pools below — see `ROADMAP.md` for the two pools.

### Out of Scope

<!-- Not excluded as bad ideas — deferred, and already tracked under their own lifecycle per CLAUDE.md, not repeated here. -->

- Trochoidal (vs. radial) root fillet below the base circle — `docs/ideas/` idea; L10 is
  the documented, accepted approximation for now.
- A browser-driven test for the 3D viewer — `docs/ideas/` idea; not required for v0's
  `make verify` gate.
- Moving CAD builds off the event loop (process pool) — `docs/tech_debt/active/` (must);
  root cause of the event-loop-stall concern; deferred, a phase of its own if picked up.
- Structured logging, a typed `/api/info` response contract, a coverage floor —
  `docs/tech_debt/active/` (must) — deferred, each with its own trigger.
- CadQuery `Shape` typing cleanup, server-side request cancellation, Enji Guard / CVE
  alerting integration — `docs/tech_debt/active/` (nice) — deferred.

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
- Active tech debt (not carried into this ingest by user decision; own lifecycle):
  `docs/tech_debt/active/` — 3 `must`, 5 `nice`. Ideas backlog: `docs/ideas/` — 2 items.

## Constraints

- **Runtime**: Python 3.10–3.12 — `cadquery-ocp` publishes wheels for nothing newer or
  older; Docker image pins `python:3.12-slim-bookworm` (L01, L12).
- **Stack**: CadQuery/OpenCascade for the solid, FastAPI + Pydantic v2 + uvicorn for the
  API, argparse for the CLI, vanilla JS + a vendored tree-shaken three.js bundle for the
  viewer (no Node at runtime), pytest, Docker + compose, GitHub Actions (L01, L11).
- **Module boundaries**: `calc.py` never imports the CAD kernel and does no I/O (runs on
  every keystroke); `model.py` is the only doorway to `cadquery`/`OCP`, no vendor object
  escapes it; `cli.py` never imports `app`/`fastapi`/`starlette`. Enforced by import-linter
  contracts, not discipline (L01/AGENTS.md, L04, L06).
- **Concurrency**: one `RLock` around every OpenCascade call (OCCT is not thread-safe);
  admission control (bounded build queue, `503` + `Retry-After`) lives in the web layer,
  never the CLI (L04, L06).
- **Memory**: solid cache bounded by entry count, export cache by total bytes,
  `malloc_trim(0)` after every cache-missing export; `compose.yaml` sets `mem_limit: 2g` as
  a measured backstop (1g failed ~5% of requests under a sweep) (L07).
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
  container checks CI also runs (L13). mypy strict with `disallow_any_explicit` off as a
  named ratchet (L14). `TRY003` off — error messages are the product (L15). No automatic
  formatter (L16).

## Key Decisions

Full log: `docs/architecture/decision_log.md` (single source of locked decisions — do not
re-litigate). Ingested verbatim into `.planning/intel/decisions.md`; carried here for
quick reference.

| ID | Decision | Outcome |
|----|----------|---------|
| L01 | Stack: Python 3.10–3.12, CadQuery/OCCT, FastAPI+Pydantic v2+uvicorn, argparse, vanilla JS + vendored three.js, pytest, Docker, GitHub Actions — detected, not chosen | ✓ Good |
| L02 | One `GearParams` model drives the web form, CLI flags, and API query params | ✓ Good |
| L03 | Cap and warn a trimmable dimension; refuse (422) a direct conflict — never guess | ✓ Good |
| L04 | Admission control (bounded build queue) lives in the web layer, not `model.py`; CLI never queues | ✓ Good |
| L05 | Defaults are absolute mm and never rescale; shareable links depend on them | ✓ Good |
| L06 | One `RLock` around every OpenCascade call; concurrency buys latency, not throughput | ✓ Good |
| L07 | Bounded caches (entries / bytes) + `malloc_trim(0)` after cache-missing export — measured 1.87 GiB → 1.5 GiB → 358 MiB | ✓ Good |
| L08 | `centre_distance()` returns `None` (bisection, not Newton) rather than a confidently wrong number | ✓ Good |
| L09 | Root fillets solved analytically in the 2D outline, ~50× faster than OCCT's fillet operator | ✓ Good |
| L10 | Radial (not trochoidal) root below the base circle, with an undercut warning | ⚠️ Revisit — trochoidal fillet is a tracked idea |
| L11 | three.js vendored as a committed, CI-byte-checked bundle; no Node at runtime | ✓ Good |
| L12 | `requirements.txt` is a generated, full pinned closure installed `--no-deps` | ✓ Good |
| L13 | `make verify` is the gate (dev shell, pre-commit, CI); `make check` adds container checks | ✓ Good |
| L14 | mypy strict, `disallow_any_explicit` off as a ratchet (`/api/info` is honest `dict[str, Any]`) | ⚠️ Revisit — tracked as untyped-info-contract tech debt |
| L15 | `TRY003` disabled; the rest of `TRY` on — error messages name the field and say what to change | ✓ Good |
| L16 | No automatic formatter — would flatten 648 lines of hand-set comment alignment | ✓ Good |

## Success Metric (Next Milestone)

**Not derivable.** No ingested document (README, SPECs, decision log) states a
developer-facing success metric for a next milestone — none was invented to fill the gap.
The human must set this when defining the next milestone's scope.

---
*Last updated: 2026-09-21 after initial GSD bootstrap from doc ingest + codebase map
(`/gsd-new-project` unified init, mode `new-project-from-ingest`).*
