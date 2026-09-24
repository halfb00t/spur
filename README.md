# spur

Parametric involute spur gear generator. Set the parameters in a web page, get a live
3D preview and the numbers you'd measure on a real gear, and download the result as
**STL** (for slicing) or **STEP** (a proper solid for CAD). The same thing is available
as an HTTP API and a CLI.

Built on [CadQuery](https://github.com/CadQuery/cadquery) (OpenCascade), FastAPI and three.js.

- Involute flanks from module, tooth count, pressure angle and profile shift
- Backlash, root fillets, D-flat or round bore with print clearance and chamfer
- Annular face recesses (one or both sides) with filleted floors
- Measurement aids: calipers across tips (corrected for odd tooth counts), span over
  *k* teeth (Wildhaber), centre distance to a mating gear
- Shareable links: every parameter lives in the URL

## Run it

### Docker

```sh
docker compose up -d --build        # http://localhost:8000
```

or without compose:

```sh
docker build -t spur .
docker run --rm -p 127.0.0.1:8000:8000 spur
```

The image is about 1.7 GB, most of it OpenCascade and VTK;
`docker/refresh-requirements.sh` keeps the rest of cadquery's dependency tree out of
it. It builds for `linux/amd64` and `linux/arm64`, so Apple silicon, Graviton and a
Raspberry Pi 5 all work:

```sh
docker buildx build --platform linux/amd64,linux/arm64 -t registry.example.com/spur:0.1.0 --push .
```

### On a remote host

The Docker CLI can build and run on another machine over SSH, no registry needed:

```sh
DOCKER_HOST=ssh://user@host docker compose up -d --build
ssh -L 8000:localhost:8000 user@host      # then open http://localhost:8000
```

**The app has no authentication.** The compose file binds to `127.0.0.1` on purpose.
To expose it, change the port mapping and put a reverse proxy with auth in front
(Caddy, Traefik, nginx, Cloudflare Access, Tailscale serve, ...). Under a sub-path,
set `SPUR_ROOT_PATH=/spur`; the UI uses relative URLs and works as-is — but the proxy
must redirect `/spur` to `/spur/`, or the browser resolves `static/app.js` one level too
high.

The container runs as a non-root user and the compose file adds a read-only root
filesystem, `tmpfs` on `/tmp`, `cap_drop: ALL` and `no-new-privileges`.

| Variable | Default (image) | |
|---|---|---|
| `SPUR_HOST` | `0.0.0.0` | Bind address |
| `SPUR_PORT` | `8000` | Port |
| `SPUR_WORKERS` | `1` | Uvicorn processes serving HTTP. They only route and cache now — no CAD build ever runs in one |
| `SPUR_BUILD_WORKERS` | `2` | CAD build worker processes (a separate pool from `SPUR_WORKERS`). Each one gear-build runs in |
| `SPUR_BUILD_TIMEOUT` | `30` (seconds) | Per-build ceiling. Past it the overrunning build's worker is killed and replaced, and the request is refused with `503` |
| `SPUR_ROOT_PATH` | | URL prefix when proxied under a sub-path |
| `SPUR_SOLID_CACHE` | `4` | Built solids kept per **build worker**. A 200-tooth solid costs a few hundred MB |
| `SPUR_EXPORT_CACHE_MB` | `64` | Budget for cached STL/STEP bytes — one budget in the serving process, not one per worker |
| `SPUR_MAX_QUEUED_BUILDS` | `2 × SPUR_BUILD_WORKERS` | Requests allowed to queue before the API answers `503`. Set explicitly to override the derived default |
| `SPUR_LOG_LEVEL` | `INFO` | Root logger level for the structured JSON logs on stderr. An unrecognised value falls back to `INFO` |

The service writes one JSON object per log line to stderr (`L20`); `docker logs` — or
`make serve 2>&1 | jq` outside Docker — captures them.

Memory scales with the size of the gears people ask for, not with traffic. The formula
is now a parent byte budget plus N times the solid cache (`SPUR_EXPORT_CACHE_MB` once, in
the serving process, plus `SPUR_BUILD_WORKERS` build workers each holding
`SPUR_SOLID_CACHE` solids) — see `bench/RESULTS.md`'s Memory section for the measured
per-`SPUR_BUILD_WORKERS` peaks this ceiling is set from, and check it rather than take it
on faith. The compose file's `mem_limit` is a measured backstop, not a guess; re-measure
(`make bench.memory`) and raise it if you raise `SPUR_BUILD_WORKERS` or the cache
settings.

CAD builds run in their own worker processes, so the API stays responsive while one is
in flight — `/api/health` measures in single-digit milliseconds under load
(`bench/RESULTS.md`'s Latency section). A build past `SPUR_BUILD_TIMEOUT` is refused
rather than waited on: the request gets `503` with `Retry-After`, and the worker behind
it is terminated and replaced so the next request to that gear doesn't queue behind a
wedged one. Past `SPUR_MAX_QUEUED_BUILDS` the API also answers `503` with `Retry-After`
rather than piling work up.

### Without Docker

Python 3.10+:

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
spur serve                                    # http://127.0.0.1:8000
```

## CLI

```sh
spur export -o gear.step                                  # defaults
spur export -o gear.stl --teeth 24 --module 1 --pressure-angle 20 --bore-flat 0
spur info --teeth 19 --mate-teeth 40                      # derived dims as JSON
spur export --help                                        # every parameter
```

## API

Every gear parameter is a query-string field; anything omitted takes its default.
Interactive docs are at `/docs`.

| Endpoint | Returns |
|---|---|
| `GET /api/model.stl?…&quality=preview\|fine` | Binary STL |
| `GET /api/model.step?…` | STEP solid |
| `GET /api/info?…[&mate_teeth=N]` | Derived dimensions, measurement aids, warnings |
| `GET /api/schema` | JSON schema of the parameters (the UI form is built from it) |
| `GET /api/health` | Liveness |

```sh
curl -OJ 'http://localhost:8000/api/model.step?teeth=19&module=1.75&pressure_angle=25'
```

Parameters that can't make a sound part — a bore wider than the root, teeth that come
to a point, recesses that leave no web — return `422` with a message and the offending
fields in `detail[].ctx.fields`. Dimensions that can be trimmed without contradicting
something you asked for are trimmed instead, and say so in `warnings`: the root fillet
is capped to the tooth gap, and the face recess is narrowed to fit between the bore wall
and the tooth rim. `503` with `Retry-After` means the build queue is full.

## Parameters

Lengths in mm, angles in degrees.

| Name | Default | |
|---|---|---|
| `teeth` | 19 | Number of teeth |
| `module` | 1.75 | Pitch diameter / teeth. Must match the mating gear |
| `pressure_angle` | 25 | Higher gives thinner tips and thicker roots. Must match the mating gear |
| `profile_shift` | 0 | Coefficient *x*; positive thickens the root and moves the tip outward |
| `backlash` | 0.1 | Removed from the circular tooth thickness (printing clearance) |
| `root_fillet` | 0.5 | Fillet radius at the tooth roots, capped to fit. 0 = sharp |
| `face_width` | 7.5 | Overall thickness |
| `bore_d` | 9 | Round part of the bore. 0 = no bore |
| `bore_flat` | 8 | Flat to opposite side of the bore. 0 = round bore |
| `bore_clearance` | 0.15 | Added to bore and flat for print shrinkage. 0 for resin/SLS |
| `bore_chamfer` | 0.4 | Chamfer on both bore edges |
| `recess_sides` | `both` | `both`, `top`, `bottom` or `none` |
| `recess_depth` | 2 | Depth of each groove |
| `recess_width` | 6 | Radial width of the groove. Narrowed automatically if it won't fit |
| `recess_inner_d` | 0 | Inner diameter of the groove. 0 = centred so hub wall equals rim wall |
| `recess_fillet` | 0.5 | Fillet at the groove floor corners |

The defaults describe a 19-tooth printer gear this project started from. They are
absolute millimetres, so on a much smaller gear the bore and the recess stop fitting;
the recess is narrowed (or dropped) to suit and the reason appears in the warnings,
while a bore too wide for the root is still refused.

## Matching an existing gear

1. Count the teeth and measure across the tips. With an **odd** tooth count the jaws sit
   on a tip on one side and a gap on the other, so the reading is short of the true tip
   diameter; the UI shows the value you should expect.
2. Estimate the module as tip diameter / (teeth + 2) and round to a standard value
   (0.5, 0.6, 0.8, 1, 1.25, 1.5, 1.75, 2, ...).
3. Confirm with **span over *k* teeth**: jaws flat against the flanks, spanning *k* teeth.
   It is insensitive to worn tips and distinguishes neighbouring modules and pressure
   angles.
4. If the mating gear is at hand, count its teeth and check the **centre distance**
   between the shafts.

## Geometry notes

- Flanks are true involutes sampled into B-splines, from the base circle (or the root
  circle, if that is larger) to the tip.
- Below the base circle the flank is radial, as in most gear generators. Real hobbed
  gears have a trochoidal root there; it only matters for undercut on small tooth
  counts, and the UI warns when that applies.
- Root fillets are computed analytically in the 2D outline rather than with the kernel's
  fillet operator, which is far slower on a many-toothed profile. Where a fillet needs
  room above the base circle, the flank starts with a short chord onto the involute,
  in the non-working root zone.
- Backlash is taken from the tooth thickness, so the part still meshes at nominal
  centre distance.
- Centre distance to a mate solves `inv(aw) = inv(a) + 2·tan(a)·Σx/Σz` for the working
  pressure angle. A total profile shift negative enough makes the right-hand side
  negative, and then no such angle exists — the pair cannot mesh at any distance. That
  is reported as a warning rather than a number.

## Development

`make` on its own lists every target. The ones you want first:

```sh
make venv        # .venv with the dev extras (needs CPython 3.10-3.12; see below)
make verify      # the gate: ruff, mypy --strict, import boundaries, pytest (~11 s, no Docker)
make up          # build the image and wait for the service on :8000
make check       # verify + the image smoke test + the vendored-bundle check (needs Docker)
```

`make verify` is the one command that decides whether a change is done. The same command
runs in the pre-commit hook, in CI on Python 3.10 and 3.12, and inside
`make worktree.land` before a merge, so "it passed" means the same thing everywhere.
There is deliberately no automatic formatter; see `L16`.

`make test-image` runs the suite inside the container instead, which needs no local
Python at all. **`cadquery-ocp` only publishes wheels for CPython 3.10-3.12**, so a
newer default `python3` will send pip off trying to build OpenCascade from source;
`make venv` picks a supported interpreter itself and says so if it cannot find one.
On Apple silicon, `PLATFORM=linux/arm64 make image` builds natively rather than
inheriting a `DOCKER_DEFAULT_PLATFORM=linux/amd64` from your shell.

`requirements.txt` is the exact pinned closure the image installs with `--no-deps`, not
a hand-maintained list. Regenerate it with `make lock` after bumping anything in
`pyproject.toml`, and verify both architectures build. The image build runs
`docker/smoke.py`, which exercises the kernel, both exporters and the ASGI app, so an
incomplete closure fails the build rather than production.

`docs/` holds the project's durable knowledge, and `AGENTS.md` is the brief every AI
agent reads first (`CLAUDE.md` is a symlink to it):

| | |
|---|---|
| `docs/architecture/overview.md` | one-page system map |
| `docs/architecture/decision_log.md` | the locked decisions, `L01`–`L16`, cited from the code |
| `docs/architecture/<subsystem>/` | strategy, tactics, implementation, errors, tests |
| `docs/CODING_VALUES.md` | what code this project welcomes and rejects |
| `docs/HOW_TO_DEVELOP.md` | the development loop (in Russian) |
| `docs/tech_debt/`, `docs/ideas/` | known gaps and deferred work, one file each |
| `docs/review-2026-09-21.md`, `docs/plan-2026-09-21.md` | the audit that produced most of the above, and its outcome |

The viewer uses a tree-shaken three.js bundle committed at
`src/spur/static/vendor/`, so the runtime needs no Node. To rebuild it (for example
after bumping three in `web/package.json`):

```sh
cd web && npm ci && npm run build
```
