# Architecture overview

One-page map of the system. Grows as the project does.

## What it is

A parametric involute spur gear generator. One validated parameter set produces a live
3D preview, the derived dimensions you would measure on the finished part, and an STL or
STEP download. The same parameters and the same answers are reachable three ways — a web
UI, an HTTP API and a CLI — because they all sit on one model (`GearParams`, L02).

Two properties define the product and constrain every change:

- A printed number is a number someone machines to. If it cannot be computed honestly it
  is reported as a warning and no number (L08).
- A parameter the user did not set must not silently change the part (L05).

## Stack

- **Core / API:** Python 3.10–3.12, FastAPI + Pydantic v2, uvicorn. Why → `L01`.
- **Geometry kernel:** CadQuery 2.x over OpenCascade (`cadquery-ocp`). Why → `L01`.
- **Viewer:** vanilla JS + a vendored, tree-shaken three.js bundle built with esbuild in
  `web/`; the runtime needs no Node. Why → `L11`.
- **Delivery:** Docker (linux/amd64 + linux/arm64) and compose; GitHub Actions CI.

See `decision_log.md` for why each of these, and for the locked behavioural decisions.

## Main pieces

| Subsystem | Lives in | Owns |
|---|---|---|
| Parameters | `src/spur/params.py` | the one validated, frozen, hashable parameter model; the JSON schema that builds the UI form and the CLI flags |
| Gear maths | `src/spur/calc.py` | involute geometry, derived dimensions, measurement aids, feasibility. No CAD kernel — see `gear-maths/` |
| Build pool | `src/spur/pool.py` | worker-process lifecycle (N `SPUR_BUILD_WORKERS`, spawned and warmed eagerly), parameter-hash affinity routing, the per-build timeout and worker replacement — see `packaging.md` |
| Solid model | `src/spur/model.py` | the CadQuery solid, the kernel lock, the per-worker solid cache, STL/STEP export — runs inside a build-pool worker process, not the server, since Phase 2 — see `solid-model/` |
| HTTP API + UI serving | `src/spur/app.py` | endpoints, admission control, the parent-side exported-bytes cache and static hosting; drives the pool but never reaches the CAD kernel itself — see `http-api.md` |
| Web UI | `src/spur/static/`, `web/` | the form, the three.js preview, shareable URLs — see `web-ui.md` |
| CLI | `src/spur/cli.py` | `spur serve` / `info` / `export` — see `cli.md` |
| Packaging + runtime | `Dockerfile`, `compose.yaml`, `requirements.txt`, `docker/`, `.github/` | the reproducible image and the checks that keep it honest — see `packaging.md` |

The dependency direction is enforced, not hoped for: `pyproject.toml` declares four
import-linter contracts and `make verify` fails on a violation. `calc.py` must never
import the CAD kernel; the CLI must never import the web layer; and, since Phase 2, the
serving process itself must never import the CAD kernel, by any path including an
indirect one (`spur.app` → `cadquery`/`OCP`, `allow_indirect_imports = false`) — which is
what makes the measured memory ceiling (L17) a statement about a kernel-free parent plus
N workers, not a guess.

## Source of truth

- **The part** — nothing is stored. Every answer is derived from `GearParams` on demand;
  caches are a speed optimisation and are safe to lose at any moment. Since Phase 2 there
  are two of them, not one: one exported-bytes cache in the serving process, one solid
  cache per build worker (L17, supersedes L07).
- **The parameters** — the URL. A model link carries its full parameter set, which is why
  defaults are frozen (L05).
- **The dependency closure** — `requirements.txt`, generated (L12). `pyproject.toml`
  holds loose ranges for developer environments, not for the image.
- **The viewer bundle** — `web/`. `src/spur/static/vendor/` is a build artefact that CI
  proves is reproducible from it (L11).
