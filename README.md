# spur

Parametric involute spur gear generator. Set the parameters in a web page, get a live
3D preview and the numbers you'd measure on a real gear, and download the result as
**STL** (for slicing) or **STEP** (a proper solid for CAD). The same thing is available
as an HTTP API and a CLI.

Built on [CadQuery](https://github.com/CadQuery/cadquery) (OpenCascade), FastAPI and three.js.

- Involute flanks from module, tooth count, pressure angle and profile shift
- Backlash, root fillets, D-flat, round or hex bore with print clearance and chamfer,
  and a keyway in a round or D-flat bore
- An edge-break chamfer on the tooth tips at both faces
- Annular face recesses (one or both sides) with filleted floors
- Body cutouts, one pattern per part: lightening holes on a bolt circle, spoke arms
  between a hub and a rim ring with rounded sector corners, or a honeycomb web of whole
  hexagonal cells
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

Python 3.12:

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
spur serve                                    # http://127.0.0.1:8000
```

## CLI

```sh
spur export -o gear.step                                  # defaults
spur export -o gear.stl --teeth 24 --module 1 --pressure-angle 20 --bore-flat 0
spur export -o hexgear.stl --bore-hex 6                   # 6 mm hex bore
spur export -o keyedgear.step --keyway-width 3 --keyway-depth 1.4  # keyway in the default D-flat bore
spur export -o chamfered.stl --tip-chamfer 0.4             # tooth-tip edge break
spur export -o holes.stl --hole-count 6 --hole-d 4 --hole-circle-d 20      # six lightening holes
spur export -o spokes.stl --spoke-count 4 --spoke-width 2 --hub-d 12 --rim-wall 1 --spoke-fillet 1  # four spoke arms
spur export -o honeycomb.stl --hex-cell 3 --hex-wall 1     # honeycomb web
spur export -o everything.stl --bore-flat 0 --keyway-width 3 --keyway-depth 1.4 --spoke-count 4 --spoke-width 2 --hub-d 13.2 --rim-wall 1 --spoke-fillet 1 --tip-chamfer 0.4  # every v0.2 family on one gear
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
is capped to the tooth gap, the tip chamfer to what the tooth allows, and the face
recess is narrowed to fit between the bore wall and the tooth rim. A hex bore replaces
the round bore and D-flat, and `warnings` names
any round-bore field it ignored. A keyway pushes the face recess outward to keep its
wall, and the recess is narrowed or dropped like any other trim; a keyway on a hex bore,
one as wide as the bore, one that runs into the D-flat, or one whose floor comes too
close to the root is refused. Body cutouts add their own refusals: two cutout patterns
set on one part is rejected, naming both; a half-set pattern — a count with a dimension
still 0 — is rejected, naming the zero fields; the reverse (a dimension set with the
pattern's count at 0) builds nothing and warns instead, naming the ignored fields; a
cutout wall thinner than the design minimum, at the hub, the rim or between neighbours,
is rejected; and a
honeycomb with no whole cell that fits the web is rejected, quoting the web's own radii.
Two cutout sizes are trimmed instead: the spoke fillet is capped to the sector it
rounds, and honeycomb cells are enlarged in 0.05 mm steps until the count fits a
measured cap — both reported in `warnings`. `503` with `Retry-After` means the build
queue is full.

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
| `tip_chamfer` | 0 | Chamfer on the tooth-tip edges at both faces: an edge break for handling and printing, capped to fit the tooth. 0 = none |
| `face_width` | 7.5 | Overall thickness |
| `bore_d` | 9 | Round part of the bore. 0 = no round bore |
| `bore_flat` | 8 | Flat to opposite side of the bore. 0 = round bore |
| `keyway_width` | 0 | Width of a keyway slot in a round or D-flat bore, cut a quarter turn from the D-flat; bore_clearance is added. Its edges stay sharp: bore_chamfer chamfers the round part only. 0 = no keyway |
| `keyway_depth` | 0 | Depth from the as-cut bore wall (bore clearance included) to the keyway floor: the DIN 6885 / ISO R773 t2 convention. ANSI B17.1's T is measured across the bore and is a different number. 0 = no keyway |
| `bore_hex` | 0 | Across-flats of a hex bore; replaces the round bore and D-flat. Common hex stock: 5, 6, 8, 10, 12.7 mm. 0 = round bore |
| `bore_clearance` | 0.15 | Added to bore, flat, hex across-flats and keyway width for print shrinkage. 0 for resin/SLS |
| `bore_chamfer` | 0.4 | Chamfer on both bore edges |
| `recess_sides` | `both` | `both`, `top`, `bottom` or `none` |
| `recess_depth` | 2 | Depth of each groove |
| `recess_width` | 6 | Radial width of the groove. Narrowed automatically if it won't fit |
| `recess_inner_d` | 0 | Inner diameter of the groove. 0 = centred so hub wall equals rim wall |
| `recess_fillet` | 0.5 | Fillet at the groove floor corners |
| `spoke_count` | 0 | Number of straight arms joining a hub ring to a rim ring; the sectors between them are cut through the full face width. Arm 0 is centred on +X. 0 = no spokes |
| `spoke_width` | 0 | Width of each arm, the same along its whole length |
| `hub_d` | 0 | Outer diameter of the hub ring the arms start from |
| `rim_wall` | 0 | Radial thickness of the rim ring, measured inward from the root circle |
| `spoke_fillet` | 0 | Radius rounding the corners of each cut-out sector, capped to fit. 0 = sharp |
| `hole_count` | 0 | Number of equal round holes cut through the full face width, evenly spaced on the hole circle with hole 0 centred on +X. 0 = no holes |
| `hole_d` | 0 | Diameter of each lightening hole |
| `hole_circle_d` | 0 | Diameter of the circle the hole centres sit on |
| `hex_cell` | 0 | Across-flats of each hexagonal through-hole. Only whole cells are cut, filling the web between the bore mouth and the root circle; the cell count is derived and capped, and above the cap the cell size is raised until it fits. 0 = no honeycomb |
| `hex_wall` | 0 | Wall between cells, and between the cells and both the bore mouth and the root circle |

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
  room above the base circle, the flank starts with a short chord onto the involute:
  1.188 mm below the pitch circle on the default gear, but above it, where the chord
  deviates from the true involute, when the root fillet exceeds half the dedendum,
  `(1.25 − x)·m / 2`, and the profile shift `x` exceeds 0.125 (below that shift the chord
  stops halfway up the tooth, at or under the pitch circle). `warnings` says how far.
- The tip chamfer is a 45-degree edge break on each tooth's tip arc at both faces,
  `tip_chamfer` off the end face and the same off the tip, cut on the finished solid.
  It touches only those arcs: the flanks, the root fillets, the bore and the recess are
  untouched, and the outside diameter is unchanged. It is capped, with a warning, to
  whichever is smallest of: 45% of the face width (a land stays on the tip between the
  two faces' chamfers), the addendum (its footprint stays above the pitch circle), and
  the start of the involute above the root fillet's straight lead-in, where the kernel
  stops being able to cut it (measured; decision log L29). `/api/info` prints
  `tip_chamfer_effective`, the chamfer actually cut. It is the one cut here the kernel
  does edge by edge on every tooth: at 200 teeth it adds about 12 s to a build (400
  edges chamfered in one operation; bench/RESULTS.md's tip-chamfer spike).
- Backlash is taken from the tooth thickness, so the part still meshes at nominal
  centre distance.
- Centre distance to a mate solves `inv(aw) = inv(a) + 2·tan(a)·Σx/Σz` for the working
  pressure angle. A total profile shift negative enough makes the right-hand side
  negative, and then no such angle exists — the pair cannot mesh at any distance. That
  is reported as a warning rather than a number.
- A body cutout — spoke arms, lightening holes or a honeycomb, one pattern per part —
  cuts through the full face width in a single boolean, so it cuts through the
  recessed floor wherever a recess sits, and the floor fillet stays intact on every
  edge the cutout leaves. Arm 0 and hole 0 are centred on +X; spoke arms are
  parallel-sided, their sector corners rounded by an analytic arc drawn in the 2D
  cutter sketch, never the kernel's fillet operator. A honeycomb cuts only whole
  hexagonal cells on a lattice centred on the axis with flats facing ±X, `hex_wall`
  between cells and at both the bore-mouth and root-circle boundaries; the cell count
  is capped at a measured constant (`HEX_CELL_CAP` = 120, `bench/RESULTS.md`'s
  honeycomb cell-count spike), and above the cap the cell size is raised in 0.05 mm
  steps until the count fits. `/api/info` prints `cutout_hub_wall`, measured from the
  farthest point of the chamfered bore mouth (a hex bore's corner, a keyway's floor
  corner) — exact for a round or D-flat bore, a lower bound elsewhere; `cutout_rim_wall`,
  measured from the root circle; `spoke_fillet_effective`, the spoke fillet actually
  cut; `hex_cell_effective`, the honeycomb cell size actually cut; and `hex_cell_count`,
  the whole cells cut. `bore_clearance` is not added to any cutout dimension.
- The keyway is a rectangular slot on the bore's side a quarter turn from the D-flat,
  through the full face width. Its depth runs from the as-cut bore wall,
  `(bore_d + bore_clearance)/2` with the clearance included, to a flat floor: the DIN
  6885 / ISO R773 t2 convention; ANSI B17.1's T is measured across the bore and is a
  different number. `/api/info` prints `keyway_floor_to_wall`, what a pin and calipers
  read from the keyway floor across the bore to the opposite wall, and
  `keyway_width_effective`, the slot width with its clearance, what calipers read
  across the slot. The slot's own edges stay sharp (`bore_chamfer` chamfers the round
  part of the bore only), and its floor corners are square: DIN 6885's small
  floor-corner radius is not modelled.

## Development

`make` on its own lists every target. The ones you want first:

```sh
make venv        # .venv with the dev extras (needs CPython 3.12; see below)
make verify      # the gate: ruff, mypy --strict, import boundaries, pytest (~11 s, no Docker)
make up          # build the image and wait for the service on :8000
make check       # verify + the image smoke test + the vendored-bundle check (needs Docker)
```

`make verify` is the one command that decides whether a change is done. The same command
runs in the pre-commit hook, in CI on Python 3.12, and inside
`make worktree.land` before a merge, so "it passed" means the same thing everywhere.
There is deliberately no automatic formatter; see `L16`.

`make test-image` runs the suite inside the container instead, which needs no local
Python at all. **`cadquery-ocp` only publishes wheels up to CPython 3.12, and spur
supports 3.12 only (L23)**, so a newer default `python3` will send pip off trying to
build OpenCascade from source; `make venv` picks a supported interpreter itself and
says so if it cannot find one.
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
