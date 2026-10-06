# Decisions

Extracted from the single ADR in this ingest set: `docs/architecture/decision_log.md`.
The file held 16 individually locked decisions (L01–L16) at the 2026-09-21 ingest, not one
blob; the log has since grown to L35 — see "Logged after this extraction" at the end and
the `superseded`/`amended` marks on the entries below (both added 2026-10-05, when two of
these figures were found stale). The log, not this file, is the single source. It carries no
`Status: Accepted` frontmatter; `locked: true` was applied on orchestrator instruction
because the file's own opening text ("Locked decisions. ... Agents must not re-litigate a
logged decision") declares every entry locked, and `AGENTS.md` names it "the single
source of locked decisions." See `INGEST-CONFLICTS.md` (INFO) for that basis, recorded
for transparency.

No LOCKED-vs-LOCKED contradictions were found among these 16 entries, and no other ADR
exists in the ingest set to contradict them.

## L01: Stack
- source: docs/architecture/decision_log.md
- status: locked; the Python floor superseded by L23
- decision: Python 3.12 only (L23; this entry read 3.10–3.12 at ingest), CadQuery/OpenCascade, FastAPI + Pydantic v2 + uvicorn, argparse, vanilla JS with a vendored three.js bundle, pytest, Docker, GitHub Actions. Detected, not chosen — this is what the project is already built from. The 3.12 ceiling is forced: `cadquery-ocp` publishes wheels for nothing newer.
- scope: language/runtime version ceiling, geometry kernel, API framework, CLI framework, frontend, test framework, delivery tooling

## L02: One parameter model, three front ends
- source: docs/architecture/decision_log.md
- status: locked
- decision: `GearParams` (frozen, hashable, Pydantic) is the single definition of a gear. Its JSON schema builds the web form; `cli.py` generates its flags from the same fields; the API takes them as query parameters.
- scope: parameter model, web form generation, CLI flag generation, API query parameters, cache key

## L03: Cap and warn, or refuse — never guess
- source: docs/architecture/decision_log.md
- status: locked
- decision: A dimension that can be trimmed to fit without contradicting something the user asked for is trimmed, and the trim is reported in `warnings` (the root fillet, the face recess). A direct conflict between two things the user set explicitly is a `422` naming the offending fields.
- scope: input validation, error handling, warnings, root fillet, face recess, bore

## L04: Admission control belongs to the web layer
- source: docs/architecture/decision_log.md
- status: locked
- decision: The bounded build queue (`SPUR_MAX_QUEUED_BUILDS`, `503` + `Retry-After`) lives in `app.py`, not in `model.py`. A CLI export must never queue behind anything. Enforced by an import-linter contract.
- scope: concurrency policy, HTTP admission control, CLI queueing exclusion

## L05: Defaults are absolute millimetres and do not rescale
- source: docs/architecture/decision_log.md
- status: locked
- decision: The stock values describe the 19-tooth m=1.75 printer gear this project started from. They stay put even when they do not suit a much smaller gear (L03 handles that instead) — every shareable model link omits the fields it left at default.
- scope: default parameter values, shareable model links, rescaling policy

## L06: One lock around the geometry kernel
- source: docs/architecture/decision_log.md
- status: superseded by L18 (amended in turn by L32)
- decision: Every OpenCascade call goes through one `RLock` in `model.py`, because OCCT is not safe to drive from several threads at once. Consequence accepted knowingly: concurrency buys latency, not throughput (makes L04 necessary).
- scope: thread safety, kernel access, concurrency

## L07: Bounded caches, and hand the arenas back
- source: docs/architecture/decision_log.md
- status: superseded by L17
- decision: Solids are cached by entry count (`SPUR_SOLID_CACHE`, default 4), exported bytes by total size (`SPUR_EXPORT_CACHE_MB`, default 64), and `malloc_trim(0)` runs after every cache-missing export. Measured: cache trimming moved the plateau from 1.87 GiB to 1.5 GiB; arena release took it to 358 MiB.
- scope: memory management, caching, arena release

## L08: No number is better than a wrong number
- source: docs/architecture/decision_log.md
- status: locked
- decision: `centre_distance()` returns `None` when `inv(aw) = inv(α) + 2·tan(α)·Σx/Σz` has no solution, and the API reports a warning instead of a value. The solver is bisection on `(0, 89°)`, not Newton — the unguarded Newton loop returned confident garbage (some negative) for 138 parameter sets, all `200 OK`.
- scope: centre distance calculation, numeric robustness, warnings vs values

## L09: Root fillets are computed, not filleted
- source: docs/architecture/decision_log.md
- status: locked; amended by L33
- decision: The root fillet arcs are solved analytically in the 2D outline instead of calling OCCT's fillet operator, ~50× faster on a many-toothed profile, for identical geometry.
- scope: root fillet geometry, performance

## L10: Radial root below the base circle, with a warning
- source: docs/architecture/decision_log.md
- status: locked; amended by L33
- decision: Below the base circle the flank is radial rather than trochoidal, as in most generators. Where that matters — undercut on low tooth counts — `derive()` warns. A known, documented approximation.
- scope: tooth profile approximation, undercut warning

## L11: three.js is vendored as a committed bundle
- source: docs/architecture/decision_log.md
- status: locked
- decision: `src/spur/static/vendor/three.bundle.min.js` is a tree-shaken esbuild output of `web/`, committed to the repo. CI rebuilds it and fails if a single byte differs. The runtime image needs no Node.
- scope: frontend bundling, Node-free runtime, CI byte check

## L12: The image installs a generated pinned closure
- source: docs/architecture/decision_log.md
- status: locked; amended by L34
- decision: `requirements.txt` is the full resolved set (31 of 31 packages), generated by `docker/refresh-requirements.sh` and installed with `--no-deps`. `pyproject.toml` keeps loose ranges for developer environments. Do not hand-edit it.
- scope: dependency pinning, Docker image reproducibility

## L13: `make verify` is the gate
- source: docs/architecture/decision_log.md
- status: locked; amended by L34
- decision: `make verify` = ruff + mypy `--strict` + import-linter + an unfinished-work scan + pytest. No Docker; ~64 s warm on the 12-core dev host at `-n 8` with coverage (`bench/RESULTS.md`, Phase 15, L34 — this entry read ~11 s at ingest). Runs in a developer's shell, the pre-commit hook, and CI. `make check` = `verify` plus the two container checks.
- scope: development gate, CI, pre-commit

## L14: mypy is strict, with `disallow_any_explicit` off as a ratchet
- source: docs/architecture/decision_log.md
- status: superseded by L21 — explicit `Any` is rejected and the published responses are typed models (amended in turn by L35)
- decision: Strict mode, `warn_unreachable`, `ignore-without-code` and friends are on. Explicit `Any` is still allowed — `derive()` and `/api/info` return a JSON document whose keys depend on the parameters, and `dict[str, Any]` is the honest type for that today. mypy targets `python_version = 3.12`; `src/spur/py.typed` was added.
- scope: type checking policy, mypy configuration

## L15: TRY003 is off; error messages are the product
- source: docs/architecture/decision_log.md
- status: locked
- decision: Ruff's `TRY003` ("avoid long messages outside the exception class") is disabled. The rest of the `TRY` set is on. This project's errors name the offending parameter and say what to change.
- scope: linter configuration, error message style

## L16: No automatic formatter
- source: docs/architecture/decision_log.md
- status: locked
- decision: `ruff format` is not run and there is no `make fmt`. Ruff's `E`/`W` rules still enforce line length and whitespace. Measured before deciding: the formatter would rewrite 10 files and 648 lines, flattening comment alignment set by hand.
- scope: formatter policy, code style

## Logged after this extraction: L17–L35

Added 2026-10-05. Headings copied from `docs/architecture/decision_log.md`, each with what
it supersedes or amends; the full text and every measurement are in the log, which stays
the single source. A planner that needs the figure reads the log entry, not this list.

- L17 — The memory ceiling of a kernel-free server plus N builders (supersedes L07)
- L18 — One lock, and what it no longer costs (supersedes L06); amended by L32
- L19 — Model bodies are gzip-encoded at a measured level, inside the admission slot, once per cache fill
- L20 — Structured JSON logging, configured at two idempotent call sites
- L21 — mypy rejects explicit `Any`; the published responses are typed models (supersedes L14); amended by L35
- L22 — CI is the merge gate: a ruleset walls main, every commit on main has a run, and main is landed with `make pr.land`; amended by L25
- L23 — Python 3.12 only (supersedes L01's floor)
- L24 — A cached solid never carries a mesh: STL export meshes a copy
- L25 — The merge gate reads the whole commit message and the run's own verdict (amends L22)
- L26 — The pre-v0.2 part is pinned by a regression fixture, and an edge selector never silently selects nothing
- L27 — A hex bore replaces the whole round profile, and its limits are the chamfered corner's, measured
- L28 — A keyway is a slot cut after the bore's chamfer, its depth measured from the as-cut bore wall
- L29 — The tooth-tip chamfer is a 3D edge break on the end-face tip arcs, capped at the tip land, the pitch circle and the start of the involute
- L30 — Body cutouts are one pattern per part, cut in one boolean, and the honeycomb's cell count is capped at a measured constant; amended by L33
- L31 — v0.2 composes: every feature proven on one gear, the composed build time measured, and the three interfaces in parity
- L32 — The concurrent latency bar, demonstrated on the harness as it stands (amends L18)
- L33 — The root lead-in is warned, not re-cut, and the filleted-spoke cutout is proved against a closed form (amends L09, L10 and L30)
- L34 — The gate is measured, runs on eight workers under a coverage floor, and CI installs the pinned kernel (amends L12 and L13)
- L35 — Vendor shape typing stops at two checked boundaries, and Phases 7 and 8 carry a Nyquist record (amends L21)
