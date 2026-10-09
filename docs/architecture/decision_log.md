# Decision log

Locked decisions. Cite by id (L01, L02, ...). Agents must not re-litigate a logged
decision; to change one, add a new entry that supersedes it and say which.

L01–L12 were reconstructed on 2026-09-21 from the code, the README and
`docs/review-2026-09-21.md` / `docs/plan-2026-09-21.md`. They record choices that were
already made and are visible in the tree — not new ones. L13–L16 were taken on
2026-09-21 while setting the repo up for agent work.

## L01 — Stack

Python 3.10–3.12, CadQuery/OpenCascade, FastAPI + Pydantic v2 + uvicorn, argparse,
vanilla JS with a vendored three.js bundle, pytest, Docker, GitHub Actions.

Reason: detected, not chosen — this is what the project is built from. The 3.12 ceiling
is not a preference: `cadquery-ocp` publishes wheels for 3.10–3.12 only, and pip will
otherwise spend minutes trying to build OpenCascade from source and fail. Migrating the
stack is out of scope; a mismatch is a tech-debt item, not a rewrite.

## L02 — One parameter model, three front ends

`GearParams` (frozen, hashable, Pydantic) is the single definition of a gear. The JSON
schema it generates builds the web form; `cli.py` generates its flags from the same
fields; the API takes them as query parameters.

Reason: a field added once shows up in all three. It also makes the parameter set a
usable cache key, which the build and export caches rely on (L07).

## L03 — Cap and warn, or refuse — never guess

A dimension that can be trimmed to fit **without contradicting something the user asked
for** is trimmed, and the trim is reported in `warnings` (the root fillet, the face
recess). A direct conflict between two things the user set explicitly is a `422` naming
the offending fields.

Reason: refusing over a parameter the user never touched is the bug F3 documented — 17%
of the standard module/teeth grid was unbuildable at stock defaults. Silently shrinking
a shaft bore would be worse than refusing. The line is "did the user ask for this?".

## L04 — Admission control belongs to the web layer

The bounded build queue (`SPUR_MAX_QUEUED_BUILDS`, `503` + `Retry-After`) lives in
`app.py`, not in `model.py`.

Reason: queue depth is a property of serving HTTP. A CLI export must never queue behind
anything. Enforced by an import-linter contract, not by convention.

## L05 — Defaults are absolute millimetres and do not rescale

The stock values describe the 19-tooth m=1.75 printer gear this project started from.
They stay put even when they do not suit a much smaller gear (L03 handles that instead).

Reason: every shareable model link omits the fields it left at default. Rescaling the
defaults would silently rebuild a different part from an old URL.

## L06 — One lock around the geometry kernel

Every OpenCascade call goes through one `RLock` in `model.py`.

Reason: OCCT is not safe to drive from several threads at once. Consequence, accepted
knowingly: concurrency buys latency, not throughput — which is what makes L04 necessary.

## L07 — Bounded caches, and hand the arenas back

Solids are cached by entry count (`SPUR_SOLID_CACHE`, default 4), exported bytes by
total size (`SPUR_EXPORT_CACHE_MB`, default 64), and `malloc_trim(0)` runs after every
cache-missing export.

Reason: measured. "32 entries" is not a memory bound when one solid costs ~280 MiB.
Cache trimming alone moved the plateau from 1.87 GiB to 1.5 GiB; the arena release took
it to 358 MiB — almost all of the apparent leak was glibc holding freed arenas, not live
cached data. The caches stay because they make the ceiling predictable.

## L08 — No number is better than a wrong number

`centre_distance()` returns `None` when `inv(aw) = inv(α) + 2·tan(α)·Σx/Σz` has no
solution, and the API reports a warning instead of a value. The solver is bisection on
`(0, 89°)`, not Newton.

Reason: this is the tool's headline "match a real gear" number, and a wrong one gets cut
into a bracket. The unguarded Newton loop returned confident garbage for 138 parameter
sets — some of them negative distances — all `200 OK`.

## L09 — Root fillets are computed, not filleted

The root fillet arcs are solved analytically in the 2D outline instead of calling OCCT's
fillet operator.

Reason: ~50× faster on a many-toothed profile, for identical geometry.

## L10 — Radial root below the base circle, with a warning

Below the base circle the flank is radial rather than trochoidal, as in most generators.
Where that matters — undercut on low tooth counts — `derive()` warns.

Reason: a known, documented approximation. It only affects undercut gears, and the
warning tells the user when they are in that region. Revisiting it is `docs/ideas/`.

## L11 — three.js is vendored as a committed bundle

`src/spur/static/vendor/three.bundle.min.js` is a tree-shaken esbuild output of `web/`,
committed to the repo. CI rebuilds it and fails if a single byte differs.

Reason: the runtime image needs no Node at all. The byte check is what stops a 568 KB
blob nobody can account for from drifting away from its source.

## L12 — The image installs a generated pinned closure

`requirements.txt` is the full resolved set (31 of 31 packages), generated by
`docker/refresh-requirements.sh` and installed with `--no-deps`. `pyproject.toml` keeps
loose ranges for developer environments.

Reason: with six of 56 packages pinned, a rebuild next month produced a different image
and a `starlette` major could break the build with no warning. Do not hand-edit it —
with `--no-deps`, pip will not tell you when a hand-bumped version breaks the closure.

## L13 — `make verify` is the gate

`make verify` = ruff + mypy `--strict` + import-linter + an unfinished-work scan +
pytest. No Docker, ~11 s warm. It runs in three places: a developer's shell, the
pre-commit hook, and CI. `make check` keeps its old meaning and now means `verify` plus
the two container checks.

Reason: "it works" has to mean "the checks passed", and there has to be exactly one
command that says so, or agents and humans end up asserting different things.

## L14 — mypy is strict, with `disallow_any_explicit` off as a ratchet

Strict mode, `warn_unreachable`, `ignore-without-code` and friends are on. Explicit
`Any` is still allowed.

Reason: `derive()` and `/api/info` return a JSON document whose keys depend on the
parameters, and `dict[str, Any]` is the honest type for that today. Turning the rule on
now would fail the gate on correct code. It is a ratchet, not an exemption — the trigger
and the intended shape are in
`docs/tech_debt/active/2026-09-21-untyped-info-contract.md`.

Two related choices: mypy targets `python_version = 3.12` because numpy's bundled stubs
refuse to be read below it — ruff (`target-version = py310`) and a real 3.10 test run in
CI are what hold the language floor. And `src/spur/py.typed` was added, so consumers and
the project's own tests are checked against the real types rather than `Any`.

## L15 — TRY003 is off; error messages are the product

Ruff's `TRY003` ("avoid long messages outside the exception class") is disabled. The
rest of the `TRY` set is on.

Reason: this project's errors name the offending parameter and say what to change —
"D-flat must be between 4.5 and 9 mm (flat to opposite side)". A class per message would
make them worse. The rule is wrong for this codebase, not the codebase for the rule.

## L16 — No automatic formatter

`ruff format` is not run and there is no `make fmt`. Ruff's `E`/`W` rules still enforce
line length and whitespace.

Reason: measured before deciding — the formatter would rewrite 10 files and 648 lines,
flattening comment alignment and continuation layout that was set by hand so the
geometry reads. The cost is real and the benefit here is style uniformity the project
already has. Revisit if the codebase grows past what hand-formatting can hold.

## L17 — The memory ceiling of a kernel-free server plus N builders (supersedes L07)

Date: 2026-09-23.

L07's formula assumed bounded caches inside one process. Under Phase 2's process-pool
split (D-01–D-08) that formula no longer describes what is resident: the exported-bytes
cache (`_BlobCache`, `SPUR_EXPORT_CACHE_MB`, default 64 MiB) lives in the parent alone,
and the solid `lru_cache` (`SPUR_SOLID_CACHE`, default 4 entries) lives once per build
worker. The new formula, in words: **a parent byte budget, plus N × the per-worker solid
cache.**

Swept, not derived by multiplying L07's per-process figures by N — that distinction is
the whole reason `REQ-measured-memory-ceiling` is its own requirement. `mem_limit`
temporarily relaxed so the sweep could not be capped by the value it exists to determine;
same 40-gear, 160–199-tooth corpus L07's `2g` was earned against (`bench/corpus.py`,
D-18). Peak container memory per `SPUR_BUILD_WORKERS` (N), sampled via `docker stats
--no-stream` polling every 0.5 s:

| N | Peak |
|---|---|
| 1 | 2052.1 MiB |
| 2 | 2878.5 MiB |
| 4 | 4731.9 MiB |

A second, otherwise-identical sweep gave 2015.2 / 2821.1 / 4502.5 MiB for the same three
N — run-to-run variance of roughly 2–5%, the noise floor for this measurement. The naive
cache-only formula (64 MiB + N × 4 × ~280 MiB) predicts roughly 1184/2304/4544 MiB; the
measured peaks are higher by an amount that grows with N (roughly 810–870 MiB per added
worker beyond the naive term) — each worker's own `cadquery`/OCP/VTK baseline footprint
(loaded once per worker at D-04's eager warm-up), not cache contents, which L07's
single-process formula never had to account for.

`mem_limit`: N=2 is the shipping default (`SPUR_BUILD_WORKERS=2`, D-19). Measured peak
2878.5 MiB × a named **1.3** (30%) headroom = 3742.05 MiB, rounded up to **4g**.
Confirmed by re-running the full 40-gear corpus at `4g`: **0 of 40 requests failed** —
the same zero-failure bar `2g` cleared and `1g` did not, before this phase.

`max_tasks_per_child`: stays **off**. N=1's late-half peak is lower than its early-half
(1833.0 vs 2052.1 MiB — no growth). N=2 and N=4 both show late > early (2878.5 vs
2566.1 MiB; 4731.9 vs 4155.4 MiB), but the 40-gear corpus is strictly ascending tooth
count, so the "late" half of any run is inherently the biggest gears in the corpus — the
bounded 4-entry solid cache holding progressively larger solids explains the rise
without a leak. No run showed unbounded growth, a rising failure rate, or elapsed time
trending up across three repeated sweeps (276.8–292.8 s).

Reason: measured, over the real multi-process topology this phase shipped — not derived
by multiplying L07's per-process numbers by N, which is exactly the
plausible-but-unmeasured guess L08 forbids. Machine: 12-core Apple M2 Max, 32 GiB RAM,
macOS 27.0 (Darwin 27.0.0), Docker 29.4.0 / Compose v5.1.2, 2026-09-23, ~09:50–10:35 UTC
(`bench/RESULTS.md` § Memory).

## L18 — One lock, and what it no longer costs (supersedes L06)

Date: 2026-09-23.

L06's decision stands: every OpenCascade call still goes through one `RLock` in
`model.py`, unchanged this phase. The lock stays because it is uncontended under
one-task-per-worker, costs nothing measurable, and still guards OCCT's process-global
state against a future in-process thread — none of that changed. What this entry
retires is L06's stated *consequence*: "concurrency buys latency, not throughput." That
was true of one process holding the lock across every request; it stopped being true the
moment there were N independent kernels in N independent processes (D-01–D-08). The
lock's scope is now per worker, not global, so concurrency across different gears now
buys throughput too, not only latency.

Measured, `single` scenario (one 200-tooth fine build in flight) vs `concurrent` (ten
concurrent fine builds), under-load p95 / idle p95 ratio, pass bar <= 2.00x
(`bench/RESULTS.md` § Latency, this machine, 2026-09-23):

- `single`: **met** on every run recorded — Runs 1–2 (1.12x, 1.18x), Runs 3–4 (1.68x,
  1.17x), Run 5 (1.10x; Run 6 had too few samples for a p95, per L08).
- `concurrent`: **accepted with caveat, not demonstrated met on both runs of one
  session.** Eight runs across four sessions: pre-fix 2.02x/2.45x and 2.32x/2.35x;
  post-fix (gzip level set from measurement and moved inside the admission slot, L19)
  1.31x/2.10x and 1.86x/2.02x, the last pair on a host held under the file's own 1.5
  idle-load bar. On 2026-09-23 the human waived this ledger item on that evidence rather
  than fix further or re-run again; the caveat and two uninvestigated observations
  (every second run of a pair reads worse than its first, before and after the fix; the
  verdict sits at the harness's ~0.1 ms-of-p95 resolution floor) live in
  `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`.

No throughput number is recorded here: `bench/RESULTS.md` contains no throughput
measurement (the memory sweep's elapsed times are sequential requests, not a load test).
"Concurrency now buys throughput too" is a property of N independent kernels in N
independent processes, not a measured requests/second figure — that is the one thing
this entry claims beyond the ratios above, and it is a structural claim, not a number
L08 would require evidence for.

Reason: the lock's cost and purpose are unchanged and stay logged at L06; what changed
is the shape of what it guards — one process becoming N — and that is what made its old
consequence false. Machine: 12-core Apple M2 Max, 32 GiB RAM, macOS 27.0 (Darwin
27.0.0), 2026-09-23 (`bench/RESULTS.md` § Latency).

## L19 — Model bodies are gzip-encoded at a measured level, inside the admission slot, once per cache fill

Date: 2026-09-23.

`GZipMiddleware`'s default (`compresslevel=9`, Starlette, never measured against this
app's bodies) cost ~1.2 s to compress a real 9,062,784-byte fine STL (`gzip_bench.py`,
single-threaded: **1181.7 ms**, `02-LATENCY-INVESTIGATION.md` E2c), and a cache hit in
`model()` bypassed `_build_slot()`'s admission control entirely — nothing bounded
concurrent compression of repeat downloads. With the build pool never running, E2c
measured the `concurrent` scenario's under-load/idle ratio at **4.33x** and **5.52x**
from this mechanism alone, both well over the 2.00x bar.

**(1)** `_GZIP_LEVEL = 1`, chosen from a measured 1/6/9 table against the real STL
(`teeth=199&quality=fine`), host loadavg 2.68/3.07/2.78 (quick task 260923-qwr):

| level | single-threaded median | output bytes (% of input) | 10-concurrent wall |
|---|---|---|---|
| 1 | 51.5 ms | 2,632,467 (29.0%) | 74.4 ms |
| 6 | 147.9 ms | 2,403,312 (26.5%) | 198.9 ms |
| 9 | 788.0 ms | 2,404,371 (26.5%) | 925.5 ms |

Rule: move up a level only if it shrinks output by >=10% **and** costs <=1.5x the lower
level's 10-concurrent wall time. Level 6 over level 1 is only 8.7% smaller; level 9 over
level 1 is only 8.66% smaller (and 12.4x the wall time) — both miss the 10% bar
decisively, so level 1 was chosen with no ambiguity (`src/spur/app.py`'s `_GZIP_LEVEL`
comment carries this table).

**(2)** Model-body gzip moved out of `GZipMiddleware` and into `model()`, performed in a
worker thread (`run_in_threadpool(_gzip, raw)`) **inside** `_build_slot()`, cached in
`_EXPORTS` under an encoding-tagged key `(params, fmt, quality, encoding)`. This is the
only place the bound can apply: `GZipMiddleware` compresses only after the endpoint has
returned and released its slot, so a limit placed inside the endpoint without moving the
compression itself would have capped nothing (`_build_slot`'s own docstring).

**(3)** Consequences: concurrent compressions are now bounded by `MAX_QUEUED_BUILDS`,
the same admission bound builds use; a repeat download of an already-compressed gear
takes no slot and performs no compression
(`test_an_already_compressed_download_needs_no_slot_at_all`); a first compression of an
already-built-but-not-yet-compressed gear can now be refused `503` busy
(`test_a_cache_hit_that_still_needs_compressing_goes_through_admission_control`).
`health()`'s `queue_available` now means slots free for build **and** first gzip encode,
not build alone. `GZipMiddleware` stays, at the same measured level, for JSON/HTML
responses — those never went through `_build_slot()` and were never the mechanism.
Starlette's private `_gzip_capacity_limiter` `RunVar` is deliberately not sized — the
same objection D-13 already raised against reaching into another module's private
internals.

Re-measured, `concurrent` scenario, under-load p95 / idle p95 (`bench/RESULTS.md`
"Post-fix re-run (Runs 5-6)", "Idle-host re-run (Runs 7-8)"): **1.31x, 2.10x, 1.86x,
2.02x** — down from the pre-fix 2.02x–2.45x range, one pass and one narrow miss each
session; not demonstrated met on both runs of one session (see L18 and
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`).

Reason: the middleware compresses after admission control has already released its
slot, so bounding compression required moving where it happens, not just how expensive
it is; the level and the architecture are both measured, not assumed. Commits:
`2d47994` (gzip level), `7a61fad` (admission-bound, cached compression).

## L20 — Structured JSON logging, configured at two idempotent call sites

Date: 2026-09-24.

The serving process now leaves structured evidence for the decision branches that
already existed (Phase 2's queue, pool and failure paths): `build.started`,
`build.failed`, `export.served`, `queue.refused`, `worker.replaced`, one JSON object per
line, on stderr. `src/spur/records.py` is the module that owns this — one formatter, one
level knob, and one small function per event (D-17), so `app.py` and `pool.py` call
intent-named helpers instead of assembling `extra=` dicts by hand.

**Library and format.** stdlib `logging` with a project-owned JSON `Formatter` — one
JSON object per line, always, built from the record's attributes plus `extra` (D-01,
D-03). No `SPUR_LOG_FORMAT` knob and no TTY detection: one formatter is one code path,
which is the one thing the round-trip test proves. `structlog` was rejected — a new
pinned dependency against `L12`'s closure, in an image that already carries 1.6 GB of
OpenCascade and VTK, for a five-event problem. logfmt was rejected too — a convention
with no parser, where `jq` is the intended reader (`make serve 2>&1 | jq`).

**The stream.** One handler, on stderr (D-04), matching the convention `cli.py` already
sets: stdout is product output (`spur info` prints JSON there), stderr is diagnostics.
uvicorn's own records (`uvicorn`, `uvicorn.error`, `uvicorn.access`) join the same
stream because `cli.cmd_serve` passes `log_config=None` to `uvicorn.run` (D-02). Verified
by reading the installed uvicorn's `Config.configure_logging()`: its entire body is
gated behind `if self.log_config is not None:`, so passing `None` skips `dictConfig`
altogether and both uvicorn loggers keep `propagate=True`, landing on whatever the root
logger is configured with — the one handler `records.configure()` installs.

**Two idempotent configuration points, not one.** `cli.cmd_serve` (before
`uvicorn.run`, the composition root for the default `SPUR_WORKERS=1` deployment) **and**
`app.py`'s `lifespan()` startup both call `records.configure()`. The original design
assumed one call site was enough, on the premise that uvicorn's worker children inherit
the parent's logging configuration when `SPUR_WORKERS>1`. `03-RESEARCH.md` tested that
premise directly — reading uvicorn's installed `_subprocess.py` /
`supervisors/multiprocess.py`, which start extra workers via
`multiprocessing.get_context("spawn")`, and a live reproduction showing a spawned
child's root logger holds zero handlers immediately after the parent installed one — and
found it **false**: a spawned worker is a fresh interpreter that re-imports `spur.app`
but never runs `cli.cmd_serve`, so `lifespan()` is the only code that reaches every
worker regardless of `SPUR_WORKERS`. **Removing either call is a regression, not a
cleanup**: dropping `cli.cmd_serve`'s call leaves the degraded paths (a bare `uvicorn
spur.app:app`, `docker/smoke.py`) with no configured logger before `lifespan()` runs;
dropping `lifespan()`'s call silently drops every record in every worker but the one
that happened to run `cli.cmd_serve`, for any deployment with `SPUR_WORKERS` above 1.
`records.configure()` is guarded idempotent (checks for an already-installed handler
instance) so both calls landing in the same process, the common `SPUR_WORKERS=1` case,
never double-prints a line.

**Where records are emitted.** The parent process only (D-06). No handler is configured
in `pool._warm()`, no record is emitted from `model.py` — workers stay silent by
decision. Accepted cost: the kernel's own traceback reaches the parent only as the
`_RemoteTraceback` text `concurrent.futures` ships back inside `BuildError`'s message,
not as a class object.

**Default level and its knob.** INFO by default (`build.started`/`export.served` live
there, so every branch is visible out of the box), with a `SPUR_LOG_LEVEL` environment
variable following the existing `SPUR_*` pattern and falling back to INFO on a name
`logging.getLevelName()` doesn't recognise — the same "read once, fall back on
nonsense" shape as `int_env` (`spur/__init__.py`) (D-14).

Reason: no number is the headline claim here — this is the observability decision the
debt file (`docs/tech_debt/resolved/2026-09-21-no-structured-logging.md`) asked to be
made once, with the field names pinned by tests rather than re-derived by eye each time
someone needs to read an incident. The two-call-site correction in particular is the
single most likely future regression: a reader finding `lifespan()`'s `configure()` call
redundant next to `cli.cmd_serve`'s and deleting it would silently blind every worker
process above the first, with nothing in a `SPUR_WORKERS=1` dev environment to catch it.

## L21 — mypy rejects explicit `Any`; the published responses are typed models (supersedes L14)

Date: 2026-09-24.

L14 kept `disallow_any_explicit` off because `derive()`'s and `/api/info`'s document had
keys that varied with the parameters, and `dict[str, Any]` was the honest type for that.
It no longer is: `DerivedDimensions` (Plan 04-01) is a frozen pydantic model whose keys
never vary — `mate_teeth`/`centre_distance` are always present, `null` when they do not
apply — so the reason the rule was off is gone. `HealthReport`/`PoolState` (Plan 04-02)
closed the second published-response gap the same way. `disallow_any_explicit` is now
**on**, globally, with `make verify` passing under it.

**The rule is on globally, with no per-module override** (D-04). A carve-out for
`tests.*`, `docker.*` or `bench.*` would be a second ratchet in the shape this entry
retires — the whole point of a ratchet is that it tightens, not that it grows a permanent
exception.

**The house rule** (D-04, D-07). `Any` is not written in this codebase, full stop. A
genuinely untyped value is `object`, narrowed where it is used. A value a library already
names keeps the library's own alias: the `Any` inside pydantic's `JsonSchemaValue` (used
for `schema()`'s return type) or starlette's `Message` (used in `docker/smoke.py`) is the
library's `Any`, not ours, and does not count as writing one.

**The two plugin settings — the human's decision, 2026-09-24 (R-1).** Without
`init_typed` and `init_forbid_extra`, the pydantic mypy plugin writes an explicit `Any`
into the initialiser it generates for every model and reports it on the model's own
`class` line — every model with fields produced this error, confirmed by reading the
installed plugin's `add_initializer` and by a hand-run `mypy --disallow-any-explicit`
before this phase's fix: exactly six errors, one per model (`GearParams`,
`DerivedDimensions`, `InfoQuery`, `ModelQuery`, `PoolState`, `HealthReport`), all on the
`class` line (04-02-SUMMARY.md's "Intermediate Proof"). With both settings, the generated
initialiser is typed from the fields and none of the six remain. **Trade-off accepted:**
mypy now type-checks every model constructor call against its field types. Static only —
no model's runtime handling of extra fields changed; none gained `extra="forbid"`. The
rejected alternative was six per-class explicit-Any suppression comments, one per model
(RESEARCH.md's recommendation) — a carve-out in comment form, the same shape as a
per-module override.

**`DerivedDimensions`** (D-09). A frozen pydantic `BaseModel`, defined in `calc.py` next
to `derive()`, validated when it is built, in exactly one place — `derive()` itself, its
single construction site. Two homes were rejected: a frozen `@dataclass` with pydantic
only at the API edge (two spellings of one contract, when the roadmap already names
Pydantic); and `params.py` (the lazy `params → calc` import used to avoid a cycle would
become a real one).

**Null over absent** (D-01, D-06). Both `/api/info` and `/api/health` carry every key,
always, with `null` for a value that does not apply or cannot be computed honestly (L08)
— `mate_teeth`/`centre_distance` on the info document, `pool` on the health document
under a lifespan-free client. Conditional keys were rejected: OpenAPI cannot state a
key's presence as conditional on a runtime value honestly, only its absence entirely.

**Uniform rounding** (D-10). Every length `DerivedDimensions` returns is rounded once, at
construction, through `r3()`. Correction: this changed no value on the wire — `r3()` now
also wraps `root_fillet`/`recess_fillet`, but `root_fillet()` and `recess_fillet()`
already `round(..., 3)` internally, so wrapping them again is idempotent. The point is
the invariant, not a value that moved: the rule "every length is rounded once, at
construction" stays true even if either helper's internal rounding is ever removed.

**The measured cost.** `derive()` now constructs and validates one `DerivedDimensions`
per call. `.venv/bin/python -m timeit`, best of 5, default `GearParams`, arm64,
Python 3.12.13 (04-01-SUMMARY.md): **9.19 usec** before the model, **11.5 usec** after —
about +2.3 usec (~1.25x), recorded in `derive()`'s own docstring, well under the plan's
2x stop-and-surface bar and negligible next to an HTTP round trip.

Reason: the ratchet was a promise to turn the rule on once the report had a real shape,
not a permanent exemption, and that shape now exists. The single most likely future
regression is someone re-adding `Any` "just for this one dict" or adding a per-module
override the next time a genuinely dynamic-looking value shows up; this entry is where
that stops being re-litigable — the answer is `object`, narrowed where it is used, or a
library's own alias, never a local respelling of `Any`.

## L22 — CI is the merge gate: a ruleset walls main, every commit on main has a run, and main is landed with `make pr.land`

Date: 2026-09-25.

L13 made `make verify` the gate, but nothing tied a merge on `main` to CI having
actually run it. PR #2 was merged five minutes after run 35993984796 failed
`test (3.10)` — four test modules failed at collection with a `TypeError`, and nothing
stopped the merge. Two squash commits already on `main`, `538d26f` and `bfc9110`, carry
no GitHub Actions run at all: a GitHub Actions skip token in a branch commit rode into
GitHub's default squash message (`COMMIT_OR_PR_TITLE`/`COMMIT_MESSAGES`, the
concatenation of branch commit subjects) and reached `main` twice.

**The commit-msg hook** (D-02, Plan 05-01). A repo-owned `commit-msg` hook in
`.pre-commit-config.yaml` refuses all six tokens GitHub Actions honours anywhere in the
message — subject or body — case-insensitively, above git's `commit -v` scissors line.
Why a hook and not only the repository setting: PR #2's head `20b63e4` showed zero
checks because the token sat in the commit subject; PR #3's `6fce500`, a prose mention
("No [ci skip] on purpose"), got skipped too and needed an empty trigger commit,
`87d500e`, to get a real run. GitHub's own documentation, fetched during this phase's
research, does not state a case rule for the six tokens (RESEARCH A1) — the hook's
case-insensitive match is a deliberate over-match on top of an unconfirmed case rule,
not a GitHub-documented fact. The `verify` hook is pinned to `stages: [pre-commit]`
(it otherwise ran twice per commit once `commit-msg` joined the same config).

**The squash message is the PR title and body** (D-03, Plan 05-01). The repository's
squash-merge settings are now `squash_merge_commit_title=PR_TITLE`,
`squash_merge_commit_message=PR_BODY` (read back live after one `gh api -X PATCH`); the
exact command lives in `docs/HOW_TO_DEVELOP.md` §8, next to this decision, because a
repository setting is not in git.

**The ship note** (D-04, Plan 05-01). `/gsd-ship`'s ship-note commit carries `[ci skip]`
in its subject, hardcoded in the global `~/.claude/gsd-core/workflows/ship.md` with no
project config knob. With the hook (D-02) that commit is refused, so the ship note is a
documented manual step (`docs/HOW_TO_DEVELOP.md` §6): the global workflow file is not
patched, since a local patch would be lost on the next `gsd` update and is invisible to
this repository anyway.

**`make pr.land` is the sanctioned path** (D-05, Plan 05-02). `scripts/pr_land.py`
resolves the PR's current head, refuses a behind or identical head, requires every job
named in `.github/workflows/required-jobs.txt` to be `success` for that head, refuses a
skip token in the squash subject or body (`message_refusals`, reusing D-02's
`find_skip_tokens` unmodified), then squash-merges with `gh pr merge --squash
--match-head-commit`, binding the merge to the exact head sha just checked. It passes
the checked subject and body itself rather than trusting `gh`'s defaults, so RESEARCH A2
(whether `gh pr merge` honours the repository squash-message setting at all) is off its
path either way, and the token refusal holds regardless. The list in
`required-jobs.txt` sits next to `ci.yml`, and a test in `tests/test_pr_land.py` derives
the required set from `ci.yml`'s own text and asserts the two agree, so the file cannot
silently drift from what CI actually runs. The behind check is what makes "the merged
tree is the checked tree" true: `bfc9110` (PR #3's squash commit on `main`) and
`2c4b544` (PR #3's checked head, run `36088409707` green on all four jobs) share tree
`6ebbeaa2…`, confirmed live this phase — which is why step 5 waits only for a run to
*appear* on the squash commit, not to finish. `pr.land` then does the local follow-up
(`git switch`/`pull --ff-only`/`branch -D`, the last only when the local branch's tip
equals the merged head) and never passes `gh pr merge --delete-branch`.

**The wall: the ruleset on `main`** (D-12, which superseded D-06; Plan 05-03). CONTEXT.md
recorded the repository as private on a free plan and D-06 deferred branch protection on
that account; by 2026-09-25 the repository was public and the human chose to put the
wall up in this phase rather than keep deferring it. It is the repository's own ruleset
`default` (id 23977515), retargeted from no branch onto `refs/heads/main` — not a second
ruleset created beside an inert one. Read back from `rules/branches/main`: the rule
types are exactly `deletion`, `non_fast_forward`, `pull_request` and
`required_status_checks`, all from ruleset 23977515; the strict up-to-date policy is on;
the required checks are exactly `test (3.12)`, `vendor-bundle` and `image`, each pinned
to GitHub Actions (`integration_id: 15368`), so a same-named status from anywhere else
cannot satisfy it. It never names `test (3.10)`: it is the post-D-09 set from the start,
because `main`'s `ci.yml` already reports all three names on every PR, while naming the
3.10 job would leave every PR after this phase waiting for a check no job reports.
No bypass actors: nothing lands on `main` except through a pull request with the
required checks green, milestone-completion and worktree-landing commits included —
chosen by the human over making the repository admin a bypass actor, which would
re-open the PR #2 red-merge hole from the button. The apply command, the read-back and
the removal call all live in `docs/HOW_TO_DEVELOP.md` §8, and are re-run whenever
`required-jobs.txt` changes.

**And `make pr.land` is still the path — a tool, not a wall.** The ruleset cannot see the
squash text, where a skip token still acts *after* the merge (D-02/D-03 unchanged), or
the squash commit's own run; `pr.land` checks both, and does the local follow-up the
ruleset has no concept of. It keeps its own required-job and behind checks even though
the ruleset now duplicates them, because its claim that the merged tree is the checked
tree must not rest on a repository setting outside git that it does not itself read.

**Reversibility.** This entry is appended, one-way: the log is append-only by policy, and
nothing above it changes. The mechanisms it records are each cheap to undo on their own —
remove the hook, `gh api -X PATCH` the squash setting back, `gh api -X DELETE` the
ruleset, stop invoking `make pr.land`. The ruleset is D-12's own "costly": one `gh api`
call removes it, but the documented merge path in `docs/HOW_TO_DEVELOP.md` §8 and this
entry would both need rewriting to match.

Reason: the single most likely future regression is someone re-adding a skip token "to
save a pipeline" — the ship workflow's own hardcoded default — or renaming or adding a
CI job without re-running the ruleset's apply command. A rename leaves every PR waiting
on a check no job reports; an addition leaves the GitHub merge button weaker than
`make pr.land`. The answer is already on file: the commit-msg hook refuses the first;
the drift test in `tests/test_pr_land.py` keeps `required-jobs.txt` equal to `ci.yml`,
and `docs/HOW_TO_DEVELOP.md` §8 says to re-run the ruleset command when that list
changes; and `make pr.land` exits non-zero, naming the gap, whenever a squash commit
gets no run.

## L23 — Python 3.12 only (supersedes L01's floor)

Date: 2026-09-25.

L01 recorded 3.10-3.12 as "detected, not chosen": the floor was never a requirement, only
what `cadquery-ocp`'s wheel range happened to cover at the time. The ceiling reasoning
stands unchanged: `cadquery-ocp` publishes no wheels past 3.12, and widening upward waits
on a wheel *and* a consumer appearing, same as before.

**Why the floor goes.** mypy cannot hold a floor below 3.12, because numpy's bundled
stubs use `type` statements and mypy refuses to read them below that version. Ruff's
3.10 target held syntax only. So the floor was checked by CI's 3.10 run alone, and that
let `logging.StreamHandler[TextIO]` — runtime subscripting needs 3.11 — reach `main`
unimportable on 3.10 (runs 35993984796, 36028253714, 36028759311; fixed `990d1fe`). The
Docker image, the dev machine and the pre-commit hook are all 3.12 already. With one
version, the type checker's version is the runtime, and the gap closes structurally
rather than depending on a CI leg to catch the next one.

**What changes.** `requires-python = ">=3.12,<3.13"` (the upper bound makes L01's
ceiling checkable: pip refuses instead of spending minutes building OpenCascade from
source). Ruff `target-version = "py312"`; mypy `python_version = "3.12"` is unchanged —
it was already there for the numpy-stub reason. CI matrix narrows to `["3.12"]`, keeping
the job name `test (3.12)`. `make venv` picks `python3.12` only. `pr.land`'s required
list (`required-jobs.txt`) loses the `test (3.10)` job in the same commit as the matrix
(L22); the ruleset on `main` never required it in the first place (D-12).

**Who is affected.** `pip install` on Python 3.10 or 3.11 is now refused by pip itself,
naming the requirement. Ubuntu 22.04 users, whose system Python predates 3.12, use
Docker — which needs no local Python — or `uv`.

**What 3.12-only adopts: the unwind list.** At planning, `ruff check --target-version
py312 .` reported three findings that this decision forces, not chooses: a PEP 695 type
parameter replacing the module-level `TypeVar` on `params._f` (UP047); catching the
builtin `TimeoutError` instead of the qualified `asyncio.TimeoutError` in `pool.py`
(UP041); and `datetime.UTC` replacing `datetime.timezone.utc` in `records.py` (UP017).
Beyond ruff's own findings, `records._JsonHandler` now subclasses
`logging.StreamHandler[TextIO]` directly in the class statement — the `TYPE_CHECKING`
indirection that gave the type checker and the interpreter different base classes existed
solely to survive a floor below 3.11, and that floor is gone. Any future widening below
3.11 must undo this list, not just the version strings.

**Rejected.** 3.11-3.12, which keeps the same structural gap one version narrower. A
3.10 interpreter in the pre-commit hook, which would put a 3.10 install on every clone
and roughly double the hook's running time for a floor nothing else exercises.

**Reversibility: costly.** Widening back is a one-line matrix change plus a new decision
entry, but every construct in the unwind list above must be undone first, and the
published `requires-python` upper bound refuses installs that worked before it was
tightened.

**Reason:** the most likely future regression is lowering the floor for one machine or
one convenience without bringing a real interpreter at the new floor into CI in the same
change — mypy cannot check a floor below its own `python_version`, so a floor with no
real interpreter behind it is a floor checked by hope (RESEARCH.md Pitfall 4).

## L24 — A cached solid never carries a mesh: STL export meshes a copy

Date: 2026-09-25.

`_build_cached` (an `lru_cache`, per worker, sized by `SPUR_SOLID_CACHE`) hands every
caller the same `cq.Solid` for identical `GearParams`, by design (D-07 affinity keeps
one gear's preview/STL/fine/STEP requests on the same worker). `Shape.exportStl()`
attaches a triangulation to whatever solid it is called on. Measured (planning probe,
`GearParams()`, teeth=19): before any export, `.BoundingBox().zlen` reads
7.500000200000001; after a preview STL export, 7.587720608891235; after a fine one,
7.519603716332508. Worse than a stale diagnostic: a preview STL export taken *after* a
fine one returned the fine mesh — 46,278 triangles, not the 9,066 a first preview export
gives — because OCCT keeps an existing triangulation that already satisfies the coarser
tolerance. Export content depended on what a worker had exported before for that gear.

**The invariant.** A solid returned by `_build_cached` never carries a mesh.
`_write_export`'s STL branch meshes `shape.copy()` — no positional argument to `copy()`
(its one parameter is `mesh`, default `False`; `copy(mesh=True)` would carry a mesh
across). The STEP branch is unchanged: a STEP export attaches no mesh, so the cached
solid already stayed exact through it (zlen 7.500000200000001 after
`export(p, "step")`).

**Why a copy and not a strip.** `BRepTools.Clean_s(shape.wrapped)` — the installed
`cadquery-ocp`'s actual name for the debt file's `.Clean` — strips a mesh *after*
export, so the cached object would carry a mesh for the whole export window; `build()`
releases `_LOCK` before callers read the solid, so the invariant would hold only between
exports, not during one. Research's timings (06-RESEARCH.md, 2026-09-25,
`.venv/bin/python`, Apple M2 Max, 12 cores, 32 GiB, macOS Darwin 27.0.0, mean of 3):
reference preview / reference fine / 200-tooth preview / 200-tooth fine — copy 23.1 /
70.9 / 260.9 / 824.2 ms, `Clean_s` 20.2 / 63.1 / 244.9 / 791.3 ms. `Clean_s` measured
4-13% faster across the board and was rejected anyway, by the human at plan time, for
the export-window reason above.

**What the copy costs** (planning measurement, same machine, load average 3.5-5.0 — a
busy host — mean of 3, export only, build excluded): in place 18.7 / 59.6 / 216.0 /
719.2 ms vs. copy 20.3 / 61.0 / 230.0 / 736.8 ms (+1.4 to +17.6 ms per export); STL
bytes identical across in-place, copy and `Clean_s` runs (453,384 / 2,313,984 /
3,135,284 / 9,086,484 bytes). Peak RSS of one 200-tooth fine export, one process per
run, `resource.getrusage(...).ru_maxrss` on macOS: in place 1263.0 and 1264.4 MiB, copy
1270.7 and 1267.6 MiB — not a container measurement, so `mem_limit` (L17) is not
re-derived here; `make bench.memory` is the instrument if that is ever needed. The two
timing sessions (research's and planning's) differ by up to ~15% on the same machine; both
are recorded rather than one cleaned-up figure.

**The proof is content equivalence, not a byte diff.** OCCT export is not
byte-reproducible across independently built solids — matched byte-for-byte in only
8 of 20 reruns (06-RESEARCH.md Pitfall 1) — but triangle count and decoded volume are:
8 preview and 4 fine independent builds of `GearParams()` gave 9,066 / 46,278 triangles
every time, decoded-volume difference 0.0. `tests/test_model.py::
test_exporting_leaves_the_cached_solid_exact` and `::test_an_stl_export_matches_a_first_
export_whatever_came_before` are the tests; `tests/conftest.py`'s autouse solid-cache
reset (Phase 3's test-side workaround) was deleted in the fixing commit (D-09) — the
whole suite passing without it is the cross-test proof.

**Rejected.** Call-site discipline (an exact-bounds helper plus a grep asserting nothing
calls `.BoundingBox()` on a cached solid) — the cache would still hand out a mutated
object to any caller that did. The strip-after-export route (above).

**Reversibility.** Reversible — local to `_write_export`; reverting is one call, and no
data, published contract or other module reads the cached object.

**Reason:** the most likely future regression is a new mesh-attaching call on the cached
object (a new export format, a tessellation for a preview endpoint) or a copy call that
carries the mesh across (`copy(mesh=True)`); the two named tests above go red the moment
either happens.

## L25 — The merge gate reads the whole commit message and the run's own verdict (amends L22)

Date: 2026-09-25.

L22 stays as written; this entry amends three of its claims, closed in the three plans of
this phase.

**The hook has no cut** (D-02, Plan 06-02). L22's "above git's `commit -v` scissors line"
no longer holds: the `commit-msg` hook now searches the whole buffer git hands it, with no
cut, ever. Why: a cut line typed by hand in an editor session is byte-identical to git's
own, and `GIT_EDITOR` only tells the hook whether an editor ran, not whether `-v` was
given -- no content or environment signal distinguishes the two. A scratch-clone probe
this phase (a hand-typed cut line inside an editor session): committed with the token
before this change, refused after. Cost: a `git commit -v` whose appended staged diff
names a token is refused too -- the refusal names the line and says to commit without
`-v`; `git config --get commit.verbose` read empty on this machine, 2026-09-25 -- nobody
is opted in.

**Green is the run's own verdict and every named job** (D-04, Plan 06-03). `head_refusals`
now also refuses a completed run whose own `conclusion` is not `success`, naming the
conclusion and the run's `html_url` -- in addition to the unchanged per-job loop, which
stays because it is what names a *missing* job, something a green run conclusion cannot.
The required list is still the local `.github/workflows/required-jobs.txt`; the
stale-checkout half is closed by rule, not by a fetch -- `docs/HOW_TO_DEVELOP.md` §8 says
`make pr.land` is run from an up-to-date `main` checkout. Evidence: the real failed run
36116930241, through the live `gh`, refused with two lines before this fix and three
after (the added line names `conclusion 'failure'` and the run's URL). The drift test in
`tests/test_pr_land.py` now compares `required_jobs()` against the effective job names
GitHub actually reports (`jobs.<id>.name` when a job sets one, else the id), not raw job
ids, so a `name:` override moves the derived required set the same way it moves what
GitHub reports.

**What `pr.land` proves, and what rests on the ruleset** (D-07, D-06, Plan 06-04). L22's
sentence that its merged-tree claim "is proven here, not rested on a server setting
outside git this module does not read" over-claimed: `gh pr merge --match-head-commit`
pins the head, not the base, so the window between `pr.land`'s `behind_by` read and the
merge call rests on the ruleset's strict up-to-date policy (D-12, no bypass actors), not
on anything this module itself reads. The module docstring and `docs/HOW_TO_DEVELOP.md`
§8 now say so explicitly. Step 5 no longer blames a skip token for every unobserved
post-merge run: it reports exactly what it observed -- the last read error, an Actions
link to check when the reads worked and nothing appeared, or a named skip token, and only
after reading it from the squash commit's own message through
`gh api repos/{owner}/{repo}/commits/<sha> --jq '.html_url, .commit.message'`.

**Rejected.** A config-driven cut for the hook -- a `-v` on the command line stays
invisible to config, so it over-matches anyway and keeps the heuristic it was meant to
replace. Accepting the cut-line residual -- leaves a `must` item open by design. Reading
`required-jobs.txt` from the PR head over the network -- a read in front of the pure
decision core, for a case the run-conclusion check already refuses. A second `behind_by`
read immediately before `gh pr merge` -- narrows the read-to-merge window without closing
it, for one more network read per land. Never diagnosing an unobserved post-merge run --
loses the one cause the tool can actually establish (a token, read after the fact).

**Reversibility.** Reversible -- each change is local to `scripts/skip_tokens.py`'s
`main()`, `scripts/pr_land.py`'s `head_refusals`, or `land`'s step 5 and its new
`no_run_report`; the cut and its own tests are in history (`3e68e74`).

**Reason:** the most likely future regressions -- the cut re-added "so `-v` commits
pass"; a run judged green by its listed jobs alone again, missing an unlisted job's
failure; a post-merge report that names a cause it did not itself read. Each is now a
test this phase added: the whole-buffer cut-line case in `tests/test_skip_tokens.py`, the
unlisted-job case and the real-run probe in `tests/test_pr_land.py`, and the three
`no_run_report` branch cases plus the live probe against `b72b0e1` and `20b63e4`.

## L26 — The pre-v0.2 part is pinned by a regression fixture, and an edge selector never silently selects nothing

Date: 2026-09-26.

**The fixture.** `tests/regression/pre_v0_2.json` pins every pre-v0.2 hand-written
parameter set (78 source-tagged entries from `tests/` and `README.md`, deduplicating to
44 records: 39 built, 5 mate-only): `derive()`'s 19 fields exactly, warning text
included; face and edge counts exactly; `Volume()` within `rel=1e-6`; six
`BoundingBox()` corners within `abs=1e-6`. Each tolerance carries the number that set
it: `Volume()` read identical (max diff 0.0) over three independent builds of the
default gear; the bore chamfer is 1.05e-3 and the recess fillets 2.9e-3 of that volume
(why `rel=1e-3` — `test_recess_removes_expected_volume`'s own tolerance — was rejected,
as too loose to catch a vanished chamfer); the box's kernel-tolerance padding reads
~1e-7 per side; the default gear's topology is 172 faces / 490 edges with the bore
chamfer, 168 / 482 without (the sharpest cheap tripwire for a vanished chamfer or
fillet). Export bytes are not compared (L24 — OCCT export is not byte-reproducible
across independently built solids). Measured cost to `make verify`: 16.27s delta at
capture (07-01, `bench/RESULTS.md` "Regression fixture cost (Phase 7, D-06)"), which
exceeded the plan's 15.0s line and halted for a `checkpoint:decision`; the human chose
Option A (07-01-SUMMARY.md) — accept the cost and keep all 44 records built, because
16.27s sat under the planner's ~20s ceiling, the cost spread evenly across all 39
builds with no single outlier, and Success Metric 3 ("old links unchanged") stays
literal rather than trimmed to a curated subset. This plan (07-02) added 13 more tests
(1 `calc.py` unit test, 10 selector-matrix rows, 2 zero-edge refusals) without touching
the fixture at all — `git diff --exit-code tests/regression/pre_v0_2.json` after every
task, and the fixture's own 85 cases stayed green throughout (`bench/RESULTS.md` "After
the selector change (07-02)").

**The regeneration rule** (D-03). The fixture changes only via `make fixture.regen`,
only in its own commit whose message states what moved and why: a `cadquery`/
`cadquery-ocp` pin bump (L12), or a deliberate contract change carrying its own `Lxx`.
It never changes in a feature commit. A red fixture in Phases 8–12 is, by definition, a
bug in that phase, not a reason to regenerate. `tests/regression/test_pre_v0_2.py::
test_the_fixture_was_captured_on_the_kernel_this_run_uses` names the one exception this
rule already anticipates — a resolved kernel drifting from the one the fixture was
captured on — and CI resolving `cadquery`/`cadquery-ocp` from an unpinned range while
the fixture pins one resolved kernel's exact topology is the `must`-severity debt item
`docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`
[retired in Phase 15 under L34; the file now lives in `docs/tech_debt/resolved/`].

**The selector rule** (D-15..D-18). `calc.bore_rim_limit(p)` is the exact geometric
bound per bore shape, no slack — `bore_radius(p)` for round and D-flat bores (the
D-flat rim is the round hole intersected with a rectangle, a strict subset of the
circle), 0.0 with no bore; Phase 8 adds the hex circumradius here rather than widening
the band. `model.BORE_RIM_SLACK` (0.01 mm) is the selection slack, measured at 1e-7 mm
(the kernel's post-boolean vertex and edge tolerance on both bore shapes, 2026-09-26)
and kept five orders of magnitude above that while staying forty times under
`MIN_WALL` (0.4 mm). Both position-based selectors raise `BuildError` on an empty
selection while their feature is on: `_bore_rim_edges`, "Bore chamfer selected no
bore-rim edges: a modelling defect in spur, not a conflict in these parameters. Set
bore_chamfer to 0 to build this gear without it."; `_groove_floor_edges`, "Recess
fillet selected no groove-floor edges: a modelling defect in spur, not a conflict in
these parameters. Set recess_fillet to 0 to build this gear without it." Ten
parametrized rows assert the exact selected-edge count and identity per bore shape,
with and without recesses, with no bore, and at a recess's minimum hub clearance; two
tests provoke each guard through the real build path. The runtime guard checks
non-empty only — the tests, not the guard, assert the exact count, so every bore phase
does not need to keep a second geometry model in step at runtime.

**Rejected.** Python literals in the test module, and a generated Python module (D-01);
a pytest flag that regenerates the fixture itself, and capture by hand with no tool
(D-02); frozen for the whole milestone, and regenerate whenever red (D-03); fully
expanded params in each record (D-04); harvesting the corpus by instrumenting
`GearParams` during a suite run, and importing the source tests' own parametrize lists
(D-05); a curated build subset, and a CI-only marker (D-06); `rel=1e-3` and exact float
volume equality (D-11); three bounding-box extents, and a relative bbox tolerance
(D-12); volume and bbox only, with no topology count (D-13); one test looping over
every record instead of one parametrized case per record (D-14); letting the empty
selection reach `_build_checked`'s catch-all and be relabelled "try smaller fillets or
chamfers"; an `EdgeSelectionError(BuildError)` subclass (deferred, not refused); an
internal error surfaced as HTTP 500 (D-15); a runtime exact-count guard,
`bore_rim_edge_count(p)` (D-16); guarding the bore-rim selector alone and leaving the
recess-floor selector unguarded (D-17); slack folded inside `bore_rim_limit` itself,
and redesigning the selectors around positive identification of the cutter's own edges
(both deferred) (D-18).

**Reversibility.** Reversible: `tests/regression/` is local to the tests and the two
guards are one `if not edges: raise BuildError(...)` each, inside `model.py`. The
regeneration rule changes only by a superseding entry; the fixture's own JSON changes
only through `make fixture.regen`.

**Reason:** the regressions this pair exists to catch — a new cut step silently
touching an old part, a reworded warning, a drifted default, a kernel bump that
re-splits faces, and a selection bound too small for a new bore shape (the hex case,
research SUMMARY.md Known Conflict #6, reproduced in miniature by this phase's own
monkeypatch test). Both are now load-bearing: a chamfer or fillet that silently
selects nothing can no longer ship a defective part, and a change to the pre-v0.2 part
can no longer ship unnoticed.

## L27 — A hex bore replaces the whole round profile, and its limits are the chamfered corner's, measured

Date: 2026-09-26.

**The field** (D-07, D-08). `bore_hex` — the across-flats in mm — joins `GearParams`'
Bore group after `bore_flat`, from 0 to 200 in steps of 0.05. Its help text gives
commodity stock as examples ("5, 6, 8, 10, 12.7 mm") and names no standard: FEATURES.md
found none for gear hex bores. The cut is `Workplane.polygon(6, effective_af,
circumscribed=True)`, with a flat facing +X (the same side the D-flat sits on) and no
rotation parameter.

**Replaces, never refuses** (D-01, D-02). `bore_d` and `bore_flat` are ignored — never
refused — and named in one warning sentence with their values when non-zero (e.g. "Hex
bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored."). This
supersedes the old REQ-hex-bore wording and ROADMAP Phase 8 SC2's `bore_flat` 422
sentence, because `bore_flat`'s default of 8.0 would otherwise refuse every plain hex
link (`?bore_hex=6` alone) — a default the user never set must not block the part (L05).
The hex x keyway 422 moved to REQ-keyway-bore and Phase 9 (`fddf9b8`, 08-01). Rejected: a
422 gated on `model_fields_set` (transport-coupled — a script sending the full form would
be refused for a value it never chose); the 422 as written; one warning per field; a
warning only for non-default fields; a union with the round bore (REQUIREMENTS.md "Out of
Scope").

**The numbers** (D-04, D-05, D-06). `bore_effective` is `null` on a hex bore — a hexagon
has no diameter. `DerivedDimensions` gains `hex_across_flats` (across-flats including
clearance) and `hex_across_corners` (corner-to-corner diameter), both `null` off a hex
bore: for `bore_hex` 6 they read 6.15 and 7.101 mm, measured this session, and the built
solid's corners agree within 5e-4 mm. Both land as UI rows. The replay
(`test_pre_v0_2.py`) now compares the fields a record holds exactly and requires every
field added since the capture to read `null` — refining L26's replay without touching
`pre_v0_2.json`, and this is `REQ-derived-dimensions-additive` enforced for every
pre-v0.2 set. Rejected: repurposing `bore_effective` for the hex (its published
description and UI label would become wrong); reporting the corners only (the fit
dimension would appear nowhere in the response).

**The limits, measured** (D-03). Two rules in `check()`, before any CAD work: the
corner-vs-root rule (a 422 naming only `bore_hex`) refuses one step past the measured
boundary (24.2 mm) and builds one step inside it (24.15 mm); the chamfered-corner-vs-root
rule (a 422 naming `bore_chamfer` and `bore_hex`) refuses at 23.4 mm and builds at 23.35
mm (08-03-SUMMARY.md D1/D2). The side never limits the chamfer: the planning probe found
the kernel chamfers a 0.375 mm side at the field's full 3 mm bound (ratio 8), with removed
volume matching the analytic hex frustum within `rel=1e-6` — so no side rule was added,
and the probe became a test instead. Both rules sit on the root circle with `MIN_WALL`,
not on the hex's side, because that is where the kernel actually fails: it raised
"BRep_API: command not done" 0.05 mm past the root where a corner meets a tooth gap (19
teeth), but built 0.30 mm past it where a corner meets a tooth (40 teeth) — the failure
depends on where each corner lands, not on a fixed margin. `recess_radii()`'s hub
clearance is `bore_mouth_limit(p) + MIN_WALL`, where a hex's chamfered mouth reaches its
corner at `2c/sqrt(3)`, not `c`: `R + c` undercounted by 0.155c and drove a 3 mm chamfer
on a 6 mm hex into an invalid solid at 2.586 mm and a kernel failure at 3 mm (research
PITFALLS.md Pitfall 1) — which is also why no fuzzy boolean (`tol=`) was needed; no
tangency is reachable by construction. The corner rule and the chamfered-corner rule
never stack (`if`/`elif`, not two independent `if`s): with `bore_chamfer` 0 the mouth
equals the corner, so exactly one hex refusal can fire. Rejected: capping the chamfer and
warning (the user asked for that chamfer on that hex — a direct conflict, L03's refuse
branch); leaving it to `_build_checked`'s catch-all ("try smaller fillets or chamfers",
after a timed build in a worker slot, without naming `bore_hex`); a chamfer-against-side
rule (measured unnecessary).

**The measurement** (D-11, D-12). `make bench.build` (`bench/build_time.py`) times build,
fine-STL and STEP export per parameter set, from a committed JSON sweep file, reused
unchanged by Phases 9-12 (its own `make typecheck`/ruff scope). The 16-row Phase 8 sweep
(D-11's 8-row cross product x module {1.75, 10}, added because the planning probe showed
module drives fine-STL export time) recorded every row inside `SPUR_BUILD_TIMEOUT=30s`;
the heaviest was `teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4`
at **5.08 s of 30 s** (`bench/RESULTS.md` "Hex bore build and export time (Phase 8,
D-11)") — below the worst single build already on record (7.39 s, "###
`SPUR_BUILD_TIMEOUT`"). Rejected: a single configuration (assumes the default recess and
chamfer are the heavy case rather than showing it); build time only (Phase 12's
`REQ-measured-build-time` wants export time per feature too); an ad hoc command pasted
into RESULTS.md (each later phase would re-derive it).

**Reversibility.** Costly: D-01 (a link that builds alongside `bore_flat` cannot become a
refusal later without breaking a published link, L05) and D-04 (`bore_effective`'s meaning
under L21's typed contract — changing it later is a contract change with its own `Lxx`).
Reversible: the two root-circle rules (relaxing either only lets more links build, never
fewer) and the bench script.

**Reason:** a hex bore is the first bore shape with points outside the round radius, so it
is the first real test of L26's selector seam and of the recess datum. Both moved to the
bore's true extent — the chamfered corner, not a round stand-in.

## L28 — A keyway is a slot cut after the bore's chamfer, its depth measured from the as-cut bore wall

Date: 2026-09-27.

**The fields** (D-16, D-17). `keyway_width` and `keyway_depth` join `GearParams`' Bore
group, mm, 0 = off, 0 to 200 in steps of 0.05, declared after `bore_flat` and before
`bore_hex`. Help text states the DIN 6885 / ISO R773 `t2` convention and warns that ANSI
B17.1's "T" is measured across the bore and is a different quantity; it names no size —
a looked-up number is one someone cuts metal to (L08). There is no `keyway_clearance`
field: `bore_clearance` is added to the width, as it already is to the bore and the hex
across-flats. Rejected: a DIN 6885 example row in help text, even as an example.

**Placement and composition** (D-01, D-04, D-13). The keyway sits on +Y, a quarter turn
from the D-flat on +X, one fixed position stated in `model._cut_keyway`'s docstring, not
a field — so the wall opposite the keyway is always the round wall, and the derived
floor-to-wall number is the same formula whether or not a flat exists. `bore_flat` stays
when a keyway is added: `?keyway_width=3&keyway_depth=1.4` on the default parameters is a
D-flat bore with a keyway. A keyway on a hex bore, or with no round bore at all, is a 422
naming the fields (`calc.check()`, before the per-shape branches). Rejected: −X, opposite
the flat (the 422 becomes unreachable and the opposite wall becomes the flat — a second
formula); a `keyway_angle` field (a third parameter, angle-dependent rules, not asked
for).

**The datum** (D-14). The keyway floor sits at `bore_radius(p) + keyway_depth`, where
`bore_radius(p) = (bore_d + bore_clearance)/2` is the as-cut bore wall — the DIN 6885 /
ISO R773 `t2` convention. ROADMAP Phase 9's SC1 and REQ-keyway-bore originally wrote that
wall as `bore_d/2 + bore_clearance`, a point `bore_clearance/2` outside the wall that
exists on the part (research PITFALLS.md Pitfall 9); 09-01 (`69948df`) amended both texts
to the as-cut formula before any code was written. The built solid measures the slot's
floor `keyway_depth` outside the kernel-read bore-wall radius within `model.TOL` (1e-6
mm) — 5.975 mm floor, 4.575 mm wall, 1.4 mm depth, on both a D-flat and a round bore
(09-02). Rejected: keeping the original formula literally — nobody can measure a point
that sits inside material.

**Chamfer and build order, measured** (D-05, D-06, D-07, D-08). `model._build` calls the
unchanged `_cut_bore` — which cuts and chamfers the round or D-flat rim exactly as before
— and only then `_cut_keyway`, which subtracts a rectangular slot with a flat floor and
square floor corners, through the full face width. The order is not a style choice: a
one-shot chamfer cut after the keyway existed failed with "BRep_API: command not done"
on a D-flat bore in every variant probed (recess on or off, either depth or chamfer
tried, either rotation), while chamfer-then-cut built every time — 178 faces / 508 edges
on the default keyed D-flat link (research, then re-confirmed 09-02). Consequently the
keyway's own three rim edges (two sides, the floor) stay sharp on every bore shape;
`bore_chamfer` reaches only the round part of the rim. `calc.bore_rim_limit(p)` is
unchanged for a keyway bore — the rim selector runs before the slot exists, and a spy on
the real pipeline proved it takes exactly the pre-keyway edges
(`Counter({"CIRCLE": 2, "LINE": 2})` D-flat, `Counter({"CIRCLE": 2})` round, 09-02). DIN
6885's small floor-corner radius is not modelled — a fixed radius or a field, if a real
key ever needs it. Rejected: chamfering the keyway's own edges too (deliverable on a
round bore only, with extra recess clearance, and not on a D-flat bore with a one-shot
chamfer); two separate chamfer operations after the keyway (valid but no behavioural
gain over one).

**The recess yields** (D-09). `calc.bore_mouth_limit(p)` takes the larger of the
chamfered rim's reach and the keyway's un-chamfered floor corner
(`calc.keyway_corner_radius(p)`), so `recess_radii()` keeps `MIN_WALL` from the corner
and narrows or drops the recess with the existing warnings — never a 422. Measured
reason: the DIN-6885-correct 3 × 1.4 mm key on the default 9 mm bore puts its corner
0.327 mm from the default recess hub wall, under `MIN_WALL` — the roadmap's original
"or a recess wall" refusal would have refused the default gear with its own correctly
sized key. This supersedes that clause of ROADMAP SC3 and REQ-keyway-wall-refused
(09-01, `69948df`). The default keyed link's recess moves out to 13.158 / 25.158 mm with
no warning; a 3 × 5 mm keyway narrows it to 3.93 mm; a 3 × 9 mm keyway drops it entirely
(09-02). Rejected: the 422 as written; a hybrid rule that yields when `recess_inner_d`
is 0 and refuses when set (a new distinction the recess contract does not otherwise
draw).

**The refusals** (D-02, D-03, D-10, D-11, D-13). A keyway on a hex bore, with no round
bore, or with only one of its two fields set is a 422 naming the fields, decided before
the per-shape branches. In the round/D-flat branch: a keyway that leaves less than
`MIN_WALL` of round bore wall between the D-flat's corner and its own side
(`calc.keyway_flat_wall(p)`) is a 422 naming `bore_flat` and `keyway_width`; a keyway
whose floor corner comes within `MIN_WALL` of the root circle is a 422 naming
`keyway_depth` and `keyway_width`; a keyway as wide as the bore (`keyway_width >=
bore_d`) is a 422 naming `keyway_width` and `bore_d`. 09-03 re-confirmed none of these
three is a kernel limit: the kernel built a keyway tangent to and notching the D-flat, a
floor 0.12 mm past the root, and a slot at 166% of `bore_d`, as one valid solid every
time (a `model_copy(update=...)`-bypassed-validation test, since `model_construct`'s
keyword arguments fail mypy strict against pydantic's plugin-typed initialiser). D-11's
bound is therefore stated as definitional in the rule's own comment, not a searched-for
kernel failure. Rejected: a fixed ratio such as `keyway_width <= bore_effective / 2`
(an opinion, no standard states a hard limit); refusing keyway-vs-D-flat only on
geometric overlap (a near-tangent sliver reaches the kernel after a timed build).

**The round bore's own chamfer reach** (D-12). The must-severity debt
`docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` is resolved
(`4b6a5b9`, moved to `docs/tech_debt/resolved/`). 09-03 re-measured the kernel's real
boundary rather than trusting the planning-time probe: a 20-step bisection over twelve
(teeth, module, chamfer, shape) configurations landed identically on every one — last
failing gap −3.8e-8 mm, first building gap 1.9e-8 mm, gap 0.0 failing on all twelve —
teeth-independent, unlike the hex corner (L27). `calc.ROOT_CONTACT = 1e-9` mm refuses a
round or D-flat bore whose chamfered mouth reaches the root circle, naming
`bore_chamfer` and `bore_d`, at that measured contact point — never at
`bore_mouth_limit(p) > rf − MIN_WALL` like the hex, so no round or D-flat link that
builds today is refused (L05); the two round rules never stack (`elif`). One
configuration failed to build at a gap of exactly `ROOT_CONTACT` even though `check()`
accepts it there — a sub-2e-8 mm residual band below the kernel's own ~1e-7 mm
tolerance, unreachable by any value the 0.05 mm field step can set, recorded in the
resolved debt file rather than treated as a fresh trigger. Rejected: refusing at
`rf − MIN_WALL` (refuses round links that build today with a thin wall); deferring
again.

**The numbers** (D-15). `DerivedDimensions` gains `keyway_floor_to_wall`
(`bore_effective + keyway_depth` — what a pin-and-caliper check reads from the floor
across the bore to the opposite wall) and `keyway_width_effective`
(`keyway_width + bore_clearance` — what calipers read across the slot), both `null` with
no keyway. On the default keyed link they read 10.55 and 3.15 mm, matched on the built
solid within 5e-4 mm (09-02). Both land as `DIMS` rows in the web UI and as README rows
this phase. Rejected: the floor-to-wall number alone (the as-cut slot width would appear
nowhere in the response).

**The measurement.** `bench/sweeps/keyway_bore.json` is a 32-row cross product (module
{1.75, 10} × `bore_flat` {0, 150} × keyway {the largest each rule allows, 3 × 1.4 mm} ×
`recess_sides` {both, none} × `bore_chamfer` {0.4, 3}) at 200 teeth on the largest bore
the rules allow (`bore_d` 200) — every row inside `SPUR_BUILD_TIMEOUT=30s` on the first
run (09-04). The heaviest row, quoted from `bench/RESULTS.md` "Keyway bore build and export time (Phase 9)":
`teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4
recess_sides=both bore_chamfer=0.4` — build 4.20 s, fine STL 0.66 s, STEP 0.41 s, build +
slower export **4.85 s of 30 s**. It is a small keyway,
not the largest the rules allow: the largest keyway at module 1.75 pushes the face
recess out entirely and builds in about half the time, confirming the planning
hypothesis that the sweep had to measure both keyway sizes to find the heaviest
configuration, not assume the largest is heaviest.

**Reversibility.** Costly: D-01 (the keyway's position), D-09 (the recess yields rather
than refuses), D-14 (the datum) and D-15 (the two published numbers) — each is part of
every keyed link ever published, or of L21's typed contract. Reversible: the refusal
rules D-02/D-10/D-11/D-12 (relaxing one only lets refused links build, never fewer) and
the sweep.

**Reason:** the keyway is the first bore feature that composes with an existing shape
instead of replacing it, so it is the first to add an edge to the part after the rim
selector has already run. Cutting it after the chamfer keeps L26's selector seam exact —
the selector never has to learn a second geometric type — and measuring its depth from
the wall that actually exists on the part, rather than a nominal point inside material,
keeps the printed numbers ones a user can check with a pin and a pair of calipers (L08).

## L29 — The tooth-tip chamfer is a 3D edge break on the end-face tip arcs, capped at the tip land, the pitch circle and the start of the involute

Date: 2026-09-28.

**The field** (D-10, D-11). `tip_chamfer` joins `GearParams`' Teeth group, declared after
`root_fillet`, mm, 0 = off, 0 to 3 in steps of 0.05. The help text names the purpose and
no size; the research-era sizing figure has no source (research SUMMARY.md Known
Conflict #2) and appears nowhere in help text, README or docs. Rejected: the Body group
(the dimension it eats, not what it is); a one-field group.

**The cut** (D-03, D-13). The 2026-09-25 reading: `solid.chamfer(c, None, edges)` on the
built solid — `bore_chamfer`'s exact call and meaning, symmetric 45 degrees, `c` off the
end face and `c` off the tip. Not a corner in `_outline`, which would change the meshing
profile, and not tip relief. `_tip_edges` selects the `CIRCLE` edges at `ra` with both
endpoints on an end face; the end-face test has a measured reason — after a chamfer of
`c` the tip land keeps `2 x teeth` arcs at `ra`, now sitting at `z = c` and
`z = face_width - c`, so a radius test alone would pick those moved arcs again on a
re-chamfer. `_chamfer_tips` runs last in `_build`, after `_cut_keyway`: the tip band is
farthest from every other cut, and the selector may assume the final outline.

**The cap** (D-01, D-02, D-04). Three limits, the smallest applied: `0.45 x face_width`
(a land stays on the tip between the two chamfers — `root_fillet`'s and
`recess_fillet`'s own 0.45 family); `ra - r`, the addendum (the chamfer's footprint on
the end face stays above the pitch circle); and a measured kernel boundary. D-04 fired:
10-01's spike (`bench/RESULTS.md` "Tooth-tip chamfer spike") found the kernel failing
inside the first two caps wherever the root fillet's straight lead-in reaches above the
pitch circle — a 20-step bisection on six configurations landed within about 2 microns
of `pred = ra - spline_start` on five of six, teeth-independent between 19 and 40 teeth;
the sixth (module 1, profile_shift 1.0) built 0.04 mm past `pred`, conservative there,
never optimistic. A 405-set grid found 0 failures at `pred` or 0.05 mm inside it across
163 conservative sets, 17 of which also built at the larger analytic cap. The 200-tooth
pair confirmed the boundary at the size that matters for the budget: `pred - 0.001` mm
builds, `pred + 0.05` mm does not. The rule is one analytic radius, `ra - spline_start`,
so D-04's "no single rule keeps every buildable chamfer buildable" checkpoint did not
apply — the boundary held across tooth count and module everywhere it was measured.
`spline_start` moved out of `model._outline` into `calc.spline_start` so the outline and
the cap read one number. `TIP_CHAMFER_MARGIN` is 0.001 mm because
`tip_chamfer_effective`'s 3-dp rounding can move a cap up by half a step (2.9365 mm
rounds to 2.937 mm), and a cap sitting exactly at the measured contact could round past
it. Always a cap, never a 422 (L03). Rejected: the analytic caps alone (a 422 from
`_build_checked`'s catch-all for a trimmable size); a constant margin taken from one
configuration (the boundary moves with module, profile shift and root fillet); a
tip-arc-width bound (the arc length does not bound an end-face chamfer, D-02's
rationale).

**The number** (D-08, D-09). `tip_chamfer_effective`, `float | None`, `null` when
`tip_chamfer` is 0, rounded to 3 dp at construction, one `DIMS` row — mirrors
`root_fillet` and `recess_fillet`, which also report applied values. One warning in the
existing "reduced to X mm to …" family, naming whichever limit bound — the tip land, the
pitch circle or the measured boundary. `X` is printed with `:g` of the applied value, the
same number `tip_chamfer_effective` carries, and the comparison is at 3 dp so a limit's
own float residue never warns and prints the request back.

**The cost** (D-05, D-06, D-07). 10-01's spike (measurement only, before the field
existed) timed `Mixin3D.chamfer()` at 38/80/400 edges: 0.29–0.51 s, 0.79–1.07 s and
11.85–12.81 s respectively — cost scales with edge count, not with `c` or module
(changing `c` from the small value to the analytic cap moved the 200-tooth chamfer time
by only 2–4 %, inside that session's run-to-run noise). 10-04's 9-row sweep at 200 teeth
(`bench/sweeps/tip_chamfer.json`, D-06's cross product) found every row inside
`SPUR_BUILD_TIMEOUT=30s`; the heaviest, `teeth=200 module=1.75 tip_chamfer=1.75
recess_sides=both`, read **14.87 s of 30 s** (`bench/RESULTS.md` "Tooth-tip chamfer
build and export time (Phase 10)"). That leaves the timeout's margin at about 2.0x, half
of the 4x `SPUR_BUILD_TIMEOUT`'s default was sized against — filed as must-severity debt,
`docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`.
D-07's over-budget checkpoint never fired: every row measured comfortably inside 30 s on
the first run, so no human decision was needed on the field's `le` or a teeth-dependent
cap. Because the spike found cost tracks edge count, not chamfer size, a lower `le`
would not have lowered the heaviest row's cost — D-07's first offer would not have
helped here; recorded for Phase 12's composed sweep to weigh instead.

**The proof** (D-12, D-13, D-14). `_tip_edges` (position-based, guarded) gets a column
on the 30-row selector matrix — every existing bore/recess row plus a 200-tooth and a
module-0.2 row (10-03) — and a real-pipeline spy proves it is called exactly once,
selecting `Counter({"CIRCLE": 38})` split 19/19 across faces, on three bore shapes with
the bore chamfer, recess and keyway all present. The built-solid proof measures the
chamfer directly: `+2 x teeth` (`+38` at 19 teeth) CONE faces, `+6 x teeth` (`+114`)
edges, volume `-22.7557` mm3, bounding box and `tip_d` unchanged, the rim and
groove-floor selectors' counts unchanged, no tip arc left on an end face, and the
45-degree geometry (moved circles at `ra`, sharp circles at `ra - c`) confirmed on all
three bore shapes. A tripwire shows that proof fail when the chamfer step is silently
skipped, while `derive()` still prints the chamfer as applied — the L08 failure it
exists to catch. The empty-selection guard is a `BuildError` (model), a 422 naming the
field (API), and a stopped CLI export that writes nothing and exits 1, never argparse's
exit 2 (D-14 as amended 2026-09-28: the "exit 2" first written in D-14 contradicted
`cmd_export`, which turns every `BuildError` into a string `SystemExit` that exits 1;
exit 2 stays argparse's own parameter-error code, per 10-03-SUMMARY.md). The flank
limit's kernel boundary held one step either side: the cap (2.937 mm on
`{profile_shift 1.0, pressure_angle 14.5}`) builds `+38` faces over the unchamfered
baseline; one 0.05 mm step past the measured contact (2.9875 mm) the kernel returns an
invalid solid.

**Reversibility.** Costly: a link that sets `tip_chamfer` above a limit gets a different
part and a different warning if the rule changes later (L05 protects only links that
omit the field).

## L30 — Body cutouts are one pattern per part, cut in one boolean, and the honeycomb's cell count is capped at a measured constant

Date: 2026-09-29.

**The fields** (D-01, D-04, D-18, D-19). Ten new `GearParams` fields in three groups —
Spokes (`spoke_count`, `spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet`), Holes
(`hole_count`, `hole_d`, `hole_circle_d`), Honeycomb (`hex_cell`, `hex_wall`) —
declared after the Recess group, the pattern's own selector field first in each group
(D-19), every default 0/off (L05). `hub_d` is the hub ring's outer diameter; `rim_wall`
is the rim ring's radial thickness measured inward from the root circle (D-01) — both
caliper numbers on the part, not derived from the bore or the tip circle. `spoke_fillet`
(mm, 0 = sharp) was the human's addition over the sharp-corners recommendation (D-04),
amending REQ-spoke-cutout and ROADMAP Phase 11 SC2 through the edit-phase tooling with
one human checkpoint (`11-01-SUMMARY.md`, `f0db74a`). `spoke_count`'s and `hole_count`'s
`le` were lowered from 200 to 40 and 60 after the build-time gate fired for real (D-18,
"The cost" below) — the final bound this phase ships, not the 200 the fields launched
with.

**The cut** (D-02, D-03, D-05, D-24). One new `_build` step, `_cut_body`, sits between
`_cut_keyway` and `_chamfer_tips` — the recess floor fillet and the bore-rim chamfer are
already baked geometry when it runs, so their selectors never see a cutout edge, and the
tip step stays last. Each pattern builds its own cutter set and subtracts all of it in
one `solid.cut(*cutters)` call, the spelling `bench/RESULTS.md`'s "Honeycomb cell-count
spike (Phase 11, D-24)" measured against `compound` and `fuse` at the cap's cell count:
all three read within 0.03 s of each other, inside the run's own noise, never clearing
D-24's 10% bar (`11-02-SUMMARY.md`, `35f0137`/`fb2e34c`). Arm 0 and hole 0 are centred on
+X, one fixed convention for both patterns (D-03). Spoke sectors are parallel-sided bars
(D-02) with their four corners rounded by analytic tangent arcs baked into the cutter's
own 2D wire — `_fillet_corner` gained an `inside=` parameter (D-05) so the same
tangent-line-vs-axis-centred-circle solve covers both the hub corners (outside the hub
circle, the root-fillet precedent) and the rim corners (inside the rim circle, the new
mirror), hand-checked against a 3-4-5-style tangent case before trusting it broadly
(`11-04-SUMMARY.md`, `1650bdf`).

**The honeycomb** (D-07, D-08, D-09, D-13). Whole cells only — a cell is cut only if its
entire hexagon lies inside the web annulus, never clipped (D-07) — on a lattice centred
on the gear axis with flats facing ±X, the same convention the hex bore's own polygon
call already uses (D-08). `hex_wall` is the wall everywhere, including both boundaries:
`bore_mouth_limit(p) + hex_wall` inside, `rf − hex_wall` outside (D-09). When the derived
whole-cell count would exceed the cap, `hex_cell` is raised in 0.05 mm steps — the
field's own step — until the exact count fits; an area-based estimate
(`cell_count_floor`) bounds the search from below first, so the exact enumeration never
runs against a count in the millions (D-13). `whole_cells`/`cell_count_floor`/
`cells_within` moved from `bench/honeycomb_spike.py` into `spur.calc` unchanged in
11-05, so the spike now imports the shipped lattice back — one definition (L08)
(`11-05-SUMMARY.md`, `d6bfe0e`).

**The cap** (D-11, D-12, D-24). The honeycomb spike (`bench/honeycomb_spike.py`, a
measurement-only script with no honeycomb field anywhere in `GearParams`, per D-24) ran
before `HEX_CELL_CAP` was written: 11 cost rows at 200 teeth, module 10, both recesses
(D-11's configuration — the largest web, so the cap always binds) found the row that cut
120 of a requested 125 cells reading 7.15 s of the 7.5 s share D-11 sets (a quarter of
`SPUR_BUILD_TIMEOUT`, beside the 14.87 s tip-chamfer row L29 recorded); the next row,
150 cells, read 7.95 s — over. `HEX_CELL_CAP = 120` is written from that row and nowhere
else (D-12) — `bench/RESULTS.md` "Honeycomb cell-count spike (Phase 11, D-24)"
(`11-02-SUMMARY.md`, `fb2e34c`). A module-1.75 confirmation at the same 120 cells read
7.25 s, 0.10 s heavier than the module-10 cap row — the smaller-module gear is the
heavier one, at a narrower margin than the planning probe found. `derive()`'s measured
cost at the honeycomb's heaviest input (14.1 µs on a bare `GearParams()`, 115 µs on the
tracer link, 15.6 ms at `teeth=200, module=10, hex_cell=3, hex_wall=0.4`) is recorded in
`hex_cells`' own docstring, not cached (`11-05-SUMMARY.md`, `baad230`).

**The refusals** (D-10, D-14 to D-17). Two or three cutout selectors set on one part is a
422 naming all of them, before any per-pattern rule runs (`REQ-one-cutout-pattern`). A
half-set pattern — a count set with a dimension still 0 — is a 422 naming the zero
fields; the reverse (a dimension set with the count at 0) builds nothing and warns,
naming the ignored fields (D-15). `0 < hex_wall < MIN_WALL` is a 422 (D-10); a honeycomb
with no whole cell fitting the web annulus is a 422 quoting the annulus's own inner and
outer radius (D-14). The hub and rim breaches read the recess's own datums —
`bore_mouth_limit(p) + MIN_WALL` on the hub side, `rf − MIN_WALL` on the rim — and
neighbours (adjacent holes, the sector opening between adjacent bars) must clear
`MIN_WALL` too (D-16, D-17). The arm rule is the human's own ruling, not the planner's
default: `0 < spoke_width < MIN_WALL` is refused naming `spoke_width`, exactly like every
other wall in the part (`11-01-SUMMARY.md`'s Flagged Assumption A1, `f0db74a`; shipped in
`11-04-SUMMARY.md`, `6901948`). Every `MIN_WALL` comparison goes through
`calc._under_min_wall`, `round(wall, 6) < MIN_WALL` rather than a bare `<` — float
residue at a wall sized to exactly `MIN_WALL` was measured at `0.39999999999999947` at
the tracer's own hub boundary, which a bare comparison would have wrongly refused
(`11-03-SUMMARY.md`, `5d8ae53`). Every refusal was pinned one field-step either side on
the real kernel — the boundary itself builds and `check()` accepts it; one step past it
`check()` refuses, but the kernel itself still cuts a valid solid there (pinned,
validation bypassed), the past-the-rule rows reusing `test_calc.py`'s own boundary values
rather than a re-derived estimate (`11-07-SUMMARY.md`, `eca02a9`) — proof these are the
part's own `MIN_WALL`, not a kernel limit.

**The numbers** (D-06, D-20). Five new `DerivedDimensions` fields: `cutout_hub_wall` and
`cutout_rim_wall` (the thinnest remaining wall on each side, `null` with no cutout — the
hub datum is `bore_mouth_limit(p)`'s farthest reach, exact for a round or D-flat bore and
the corner's reach for a hex or keyed one; the rim datum is `rf`), `spoke_fillet_effective`
(D-06: capped to `0.45 ×` whichever of the sector's hub opening or annulus width binds
first, reported after the cap, `null` with no spokes or `spoke_fillet` 0), and
`hex_cell_effective`/`hex_cell_count` (the raised cell size and the whole cells cut,
`null` with no honeycomb). The honeycomb's walls are read exactly off the cut hexagons —
the nearest edge and farthest vertex on the polygon itself — not the whole-cell test's
conservative circumradius: the naive bound under-reported the tracer's own hub wall by
0.232 mm (Flagged Assumption A3, `11-05-SUMMARY.md`, `d6bfe0e`). The cell count rides in
the `DIMS` row's own label (`Honeycomb cell A/F (18 cells)`), `span_teeth`'s precedent.

**The cost** (D-18). Each pattern's own sweep (`bench/RESULTS.md` "Body cutout build and
export time (Phase 11)") measured the heaviest allowed row at `le` 200: a hole row
crossing the module-1.75 recess groove read 41.85 s of 30 s; three spoke rows crossing a
recess groove read 65.70–68.70 s; the honeycomb's own cap row read 8.65 s against D-11's
7.5 s share (inside the 30 s absolute timeout). D-18's over-budget gate fired for real
and offered a lower `le`; the human accepted it verbatim: `spoke_count` 200 → 40,
`hole_count` 200 → 60, the honeycomb's own over-share row accepted as measured,
`HEX_CELL_CAP` unchanged at 120 (`11-06-SUMMARY.md`, `2224697`). The re-run measured
every row of both sweeps back inside 30 s — heaviest hole row 11.79 s, heaviest spoke row
18.52 s (`11-06-SUMMARY.md`, `f290860`). Placed arithmetically beside Phase 10's 14.87 s
tip-chamfer row (L29) — not a real composed build, Phase 12 measures that — the hole
total (26.66 s) still leaves 3.34 s of margin; the spoke total (33.39 s) reads 3.39 s
over 30 s under this run's own exceptionally loaded host (load 32.17 against the first
run's own 5–10), filed as must-severity debt rather than rounded away
(`docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`).

**The proof.** A real-pipeline spy (`test_every_selector_takes_only_its_own_edges_with_a_body_cutout`,
19 rows) proves the bore-rim and groove-floor selectors still take exactly their
pre-cutout edges with every pattern, bore shape and recess setting present, because both
selectors run on the solid before their own operator applies, strictly before
`_cut_body`; three more rows prove the tip selector still takes exactly `2 × teeth` arcs
with a cutout present (`11-07-SUMMARY.md`, `faf3616`). Eighteen kernel-boundary rows pin
every `MIN_WALL` rule exactly at its boundary and one field-step past it, on the real
kernel via `model_copy` (validation bypassed, never re-validated); ten tangent-cutter
rows — a hole edge on a recess wall, a spoke's hub/rim arcs tangent to each, sharp and
filleted, a spoke web at exactly `MIN_WALL` with no recess, a honeycomb cell's flat
tangent to a recess wall — all built one valid solid with the plain `cut(*cutters)`, so
no fuzzy-boolean tolerance ships, only a comment recording the measurement
(`11-07-SUMMARY.md`, `eca02a9`). The built-solid proof reads each pattern's cut back
against `derive()`'s own printed numbers — face-type deltas, edge count, removed volume
(checked to `1e-9 mm3` against a closed-form formula for holes, sharp spokes and
honeycomb; pinned for the filleted spoke, which has none) — and the printed
`cutout_hub_wall`/`cutout_rim_wall` read back at a probe point either side
(`11-08-SUMMARY.md`, `c50c61a`). The recess floor fillet's survival is counted, not
assumed: 13 rows across every pattern and bore shape with both recesses find zero sharp
floor-to-wall corners and a pinned `TORUS` count (`11-08-SUMMARY.md`, `a84c800`). Two
tripwires demonstrate both proofs fail when their own step is skipped — `_cut_body`
patched to a no-op leaves `derive()` printing a wall that no longer matches the part (the
L08 failure); `recess_fillet` patched to `0.0` leaves sharp corners the survival proof's
own assertion catches.

**Reversibility.** Costly, on every axis this phase touched: the published meaning of
`hub_d`, `rim_wall`, `spoke_width`, the +X convention and the whole-cell lattice all
re-cut every link that sets them if changed later (D-01, D-02, D-07, D-08; L05 protects
only links that omit the fields). `HEX_CELL_CAP` and the counts' `le` are the same shape
— a lower cap or bound later changes what a published link cuts; a higher one is
additive, exactly as this phase's own `le` lowering (200 → 40/60) already was for every
link that had not yet been shared (D-11, D-18).

## L31 — v0.2 composes: every feature proven on one gear, the composed build time measured, and the three interfaces in parity

Date: 2026-09-30.

**The composed sweep** (D-01 to D-05). `bench/sweeps/composed.json`'s 18-row design
stacks each of the three cutout patterns' own recorded heaviest row (spokes, holes,
honeycomb) with the tip chamfer at that gear's own cap and both recesses, on the
largest `bore_hex` its hub rule allows and separately on a keyed round bore, at module
1.75 and module 10, plus six single-feature baselines re-run same-host — citing
`bench/RESULTS.md` "Composed build and export time (Phase 12)" and `12-02-SUMMARY.md`
(`278d982`). Two runs (loads 12.66 and 7.04 at the runner's own reading) were not
decisive by D-02's <1.5 bar; the runner itself was found to be reading load at the end
of a 6–7 minute sweep, not its start, and was fixed to read before the first row builds
(`9b9af43`, `12-03-SUMMARY.md`). Two further quiet re-runs (loads 2.74 and 1.54 at a
genuine at-start reading) still missed the 1.5 bar. **The D-02 supersession, taken this
phase:** the human reviewed all four runs — loads 12.66 and 7.04 (both read at the end
of the run, the tool-bug reading; see above) and 2.74 and 1.54 (read at a genuine start,
after the fix) — an eightfold spread across the two measurement methods — and found the
same four `spoke_count=40` composed rows over
`SPUR_BUILD_TIMEOUT` (30 s) in every one, at 31.16–33.32 s, a band that did not track
the load figure (Run 3, load 2.74, read higher than Run 1, load 12.66, on three of the
four rows). The human's answer was "Supersede D-02: treat Run 4 as decisive"
(`12-03-SUMMARY.md`) — D-02's <1.5 bar is superseded for this one gate on the measured
load-independence of four runs; D-02's own bar otherwise stands for any future sweep
unless superseded again by a new entry. Run 4's heaviest row, module=10 keyed-bore
spokes with `tip_chamfer=3`, read 32.03 s of 30 s; a probe (step 5 down, then up by 1)
found `spoke_count=32` the largest count still inside budget (29.41 s, 33 read 30.11 s
over); the human's answer was "lower-le: spoke_count 32", applied in `src/spur/params.py`
(`547214e`). The whole composed sweep re-run at the new `le` reads every row inside
30 s, heaviest 29.42 s (0.58 s margin) — `bench/RESULTS.md` "### Re-run after the gate".
Two of the three patterns' worst composed rows read below the Phase 10/11 arithmetic
total they replaced by measurement, not assumption: spokes 32.03 s against a 33.39 s
total (-1.36 s), holes 25.05 s against 26.66 s (-1.61 s). The third, honeycomb, measured
above its total: 27.49 s against 23.52 s (+3.97 s) — the one pattern where stacking cost
more than the naive sum. Two
build-timeout debts this sweep triggered were resolved with the measured number and the
decision (`docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`,
`docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`,
sha recorded `359f8db`, `12-03-SUMMARY.md`); the tip-chamfer debt's unanswered
concurrent-load question was re-homed into
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s own trigger set.

**The composition matrix** (D-07 to D-10). Tier 1: 96 rows (the full bore × cutout ×
recess × tip-chamfer cross product on the default 19-tooth gear) each derive exactly the
non-null `DerivedDimensions` fields and warnings their families imply, computed from
`tests/composition.py`'s own pinned tables, never from `derive()` itself — the
keyed-round + spokes row derives a 0.421 mm hub wall instead of refusing
(`12-05-SUMMARY.md`, `9e2960d`). Refusals: all 23 locked refusals composed with each of
the 6 other families (138 rows) keep the refusal-alone `check()` field sequence and
sentence, except 18 rows where the switched-on family adds a second refusal and 6 rows
where the switched-on bore moves the quoted hub datum — the 114/6/18 split was
re-derived from `check()` this session, not trusted from the planning probe, and
matched it exactly (`12-05-SUMMARY.md`). Tier 2, on the real kernel: 12 rows (the tip
chamfer applied with each cutout on each bore — d-flat, round, hex, keyed round), each
re-running the tip-arc and cutout proofs unchanged on one composed solid, plus 3 rows
proving the single-sided-recess × cutout pairing no earlier matrix built — 15 kernel
rows total, every face-type delta, edge delta, removed volume and `TORUS` count matching
the planning probe exactly (`12-06-SUMMARY.md`, `ae53fea`). D-10's gate: the phase's own
added `make verify` cost, measured same-host, alternating, against the phase-start code
(`c9a169d`) — four runs (A1 183.67 s / B1 216.90 s / A2 184.89 s / B2 216.73 s pytest;
193.30 / 217.90 / 185.88 / 217.83 s wall), mean(A) 189.59 s, mean(B) 217.87 s, **delta
+28.28 s** against the 30.0 s line (1.72 s of margin) — `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)".
The human's verbatim answer was "accept": the measured
cost stands, no tier-2 row is trimmed, `tests/test_model.py` untouched
(`12-09-SUMMARY.md`, `b7271ba`).

**The parity proof** (D-11, D-13, D-14). The pinned group order — Teeth, Body, Bore,
Recess, Spokes, Holes, Honeycomb — was verified this session directly against the live
`/api/schema` (30 properties, group first-appearance order exactly this list, no group
reappearing after another starts), settling D-11's evidence conflict as "seven" groups
per the human's binding 12-01 answer (`12-07-SUMMARY.md`, `3fb9901`). One generic field
walk (`tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`)
proves every v0.2 field reaches the schema and the CLI parser in that one order, without a
per-field test; a second
(`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`)
proves `app.js` carries the hash -> form -> query path generically, naming no field.
README's composed link (every family on one
19-tooth gear) prints the identical document on `spur info` and `/api/info`, byte for
byte once the API's compact JSON is re-indented to the CLI's own `indent=2` — proving
value and key-order identity, not just value equality. All 23 refusals read identically
on the API's 422 and the CLI's exit 2 (`tests/test_cli.py::test_every_refusal_reads_the_same_on_the_api_and_the_cli`).
The CLI's real exit contract — parameter errors exit 2, an unknown output extension and
every `BuildError` exit 1 — was moved to `docs/architecture/cli.md` (the doc moved to
the code, `src/spur/cli.py` byte-unchanged from `c9a169d`), pinned by three tests
including one that runs the real process, and the debt this closed
(`docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md`)
was resolved in two commits per the project's own placeholder-then-sha precedent
(`0deb25a` fixing, `eceafff` recording the sha) (`12-08-SUMMARY.md`, `22e530d`).

**The UI pass** (D-12). Both deferred form ideas —
`docs/ideas/2026-09-29-conditional-form-fields.md` and
`docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` — are judged "not taken"
at Phase 12: 08 D-09 stands, the form stays generated from `/api/schema` and nothing
else, because a proof-and-measurement phase must not ship the first bore-specific or
field-relation logic in `app.js` with no UI test; the ignored-field warnings stay the
honest signal until a browser test exists or a user reports them insufficient. Each
idea file gained a new trigger to that effect; `docs/ideas/2026-09-21-browser-test-for-the-viewer.md`
records that 12-07 took its own cheaper first step (the generic field-walk test above),
leaving the headless-browser cost question open with the trigger "either UI idea is
taken" (`12-08-SUMMARY.md`, `22e530d`).

**The re-measurement** (D-16 to D-18). The composed sweep's largest fine STL — named by
its own byte count, not by inspection — is
`teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400
tip_chamfer=3 recess_sides=both`, 17,306,084 bytes, 346,120 triangles, on every recorded
run of the sweep (`bench/RESULTS.md` "Export cost on the heaviest v0.2 topology (Phase
12)"). L19's gzip-level rule, re-applied exactly as written: level 6 shrinks output by
7.46% (bar 10%), level 9 by 7.44% (bar 10%) — both miss the bar, `_GZIP_LEVEL` stays at
1, and D-18's rule selects level 1 again; the table lands as a dated comment addition
above `_GZIP_LEVEL` in `src/spur/app.py`, L19's own text unedited, per 12-01's binding
answer "comment + L31" (this entry is the "L31" half). L24's mesh-copy cost is recorded
only, not adopted as a decision: +52.9 ms mean export, −56.0 MiB mean peak RSS over
in-place, on this run's own 346,120-triangle heaviest topology — the copy in
`model._write_export` stays regardless, because it is a correctness decision (a cached
solid never carries a mesh, L24), not a cost trade (`12-04-SUMMARY.md`, `4782322`).

**The fixture and the amendments** (D-06, D-15, D-20). ROADMAP Phase 12 SC3 was amended
to name the composed sweep D-01 designed rather than a pre-measured winner, and SC5 was
amended to state the regression replay's real contract — identical `DerivedDimensions`
and an identical solid (volume, bounding box, face and edge counts) — both through
edit-phase's own write step, approved verbatim by the human ("approved")
(`12-01-SUMMARY.md`, `4a4c679`). `PROJECT.md` Success Metric 3's "identical export" is
read, explicitly, as identical `DerivedDimensions` and an identical solid: **export bytes are not compared**
(L26 — OCCT export is not byte-reproducible across independently built solids). The
pre-v0.2 fixture (`tests/regression/pre_v0_2.json`) is byte-unchanged from `c9a169d`
through the whole phase
(`git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json`, clean) and its final
replay this session is green and unmodified: **86 passed in 19.24 s**, its own share of
the phase-end gate (`bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)", "### Regression fixture share").

**Reversibility.** `spoke_count`'s `le` (40 → 32, `547214e`) is the same shape as L30's
own `le` lowerings — a lower bound later re-cuts what a published link can request;
raising it again is additive. `_GZIP_LEVEL` is unchanged, so nothing here moves that
axis. The 286 new composition tests added across 12-02 through 12-08 are reversible by
deletion alone, but their +28.28 s gate cost is not free to future contributors unless a
later entry trims it — accepted, not undone, by this phase's own gate decision above.
The parity tests and the CLI doc fix are pure additions with no published contract
change. Milestone bookkeeping (`MILESTONES.md`, the audit) is left to
`gsd-complete-milestone`, per D-19.

## L32 — The concurrent latency bar, demonstrated on the harness as it stands (amends L18)

Date: 2026-10-02.

L18 stays as written; this entry amends its concurrent-scenario caveat paragraph with what
was measured in Phase 13.

**The two observations** (D-01 to D-04). A six-session, twelve-run campaign (Pairs A, B, C,
each run twice) tested the three candidates the 2026-09-23 debt file left open for
observation 1 (every second run of a pair reads worse than its first). Pair A split between
its two repetitions (A1: 1.327x -> 1.940x, worse; A2: 1.896x -> 1.517x, not worse); the
pre-registered rule states that when Pair A does not point worse, observation 1 is not
reproduced and Pairs B and C (B: worse in both repetitions; C: split) cannot rule anything
in or out. No candidate — four instant ~2.6 MB cache-hit sends, worker-side state, or a
shorter load window read at the floor — is ruled in or out
(`13-LATENCY-INVESTIGATION.md` § Verdict, § Observation 1). The split-process poller's
run-2-vs-run-1 direction agreed with the in-process direction in all six sessions (H1 stays
refuted, as 02's own H1 re-check found pre-fix). Observation 2 (the verdict sits at the
harness's resolution floor) is ruled to candidate (ii), "the floor is real": four of
twenty-four (run, source) verdict cells flip inside one percentile
(`A1-run2`, `C1-run1`, `A2-run1` in-process; `B1-run2` on the poller), which refutes
candidate (i) outright; candidate (iii)'s exact claim (the flipping runs are exactly the
below-median-n runs) was checked directly and found false — three below-median-n runs do
not flip (`13-LATENCY-INVESTIGATION.md` § Verdict, § Observation 2). The clock resolution
read 41.7 ns on this host, uniform across all twelve runs; the measured smallest gap
between distinct samples (2.328e-10 s) is reported as a float64-precision artifact below
that resolution, not used to set a floor constant — the one-percentile spreads that
actually flipped a verdict ran 0.090-0.296 ms, 100-700x the clock resolution rather than the
~10x a floor-threshold heuristic would anticipate (`13-LATENCY-INVESTIGATION.md` §
Recommendation). No server-side cause survived to be filed as debt (D-17): observation 1 was
not reproduced and observation 2's cause is a harness/measurement-floor property, not a
server defect.

**The environment** (D-06). `fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8)
was stopped for every session this phase (the investigation campaign, the three bar
sessions, and SC3); `spur-spur-1` was left running throughout
(`bench/RESULTS.md` § "Phase 13 investigation sessions", § "Bar session bar-3"). This is an
environment change relative to Runs 1–8, where `fleet-user` was up and restart-looping
throughout every recorded run; a pass in this phase is not read as explaining the misses
recorded on that noisier environment.

**The bar** (D-05, D-07, D-09 to D-11). Observation 2 ruled to the floor being real, with no
threshold change adopted — D-09's checkpoint for an outcome-(b) harness change was never
reached because the decisive session demonstrated outcome (a) directly, so D-10's absolute
floor was not needed and D-11's double-miss halt was not reached either. Two attempts
(bar-1, bar-2) capped out on the D-05 quiet gate at 900 s and are recorded as non-decisive,
never counted toward the verdict (`bench/RESULTS.md` § "Bar session bar-1 (Runs 9-10)", §
"Bar session bar-2 (Runs 11-12)"). The third attempt (bar-3) released after 320 s on three
consecutive 30 s load samples under 1.5 (1.39, 1.12, 0.96) and is decisive: both runs of the
`concurrent` scenario read under the 2.00x pass bar — Run 13 printed 1.31x, Run 14 printed
1.42x — on the unmodified harness, with the `single` scenario's Run 13 also passing (1.12x)
and Run 14's single/under-load series refused for insufficient samples (n=18 < 20,
`concurrent` decides it per D-08) (`bench/RESULTS.md` § "Bar session bar-3 (Runs 13-14)").
**Outcome (a): demonstrated.** The bar is no longer accepted with caveat — it is measured,
on both runs of one decisive session, on the harness as it stands.

**SC3** (D-13 to D-16). The composed sweep's worst row (29.42 s alone, Phase 12's own
0.58 s margin) plus the next nine heaviest composed rows were fired at a fresh server under
the shipped configuration (2 workers, 4 queued builds, 30 s per-build timeout). The session
never reached the D-05 quiet gate (900 s cap, non-decisive) and is recorded regardless, per
D-16: 0 of 10 requests were served; 6 of 10 were refused by admission control (`503 busy`,
exactly as designed); 4 of 10 were admitted, and all four exceeded `SPUR_BUILD_TIMEOUT` —
two via the documented `BuildTimeout` path, two via an undocumented `500` raised by a
same-slot timeout-cleanup race in `_run_with_timeout`. `/api/health`'s `workers_replaced`
moved 0 -> 2 (`bench/RESULTS.md` § "Composed worst row under ten concurrent builds (Phase
13)"). The worst row's own 0.58 s margin, measured alone in Phase 12, did not survive this
contention — it too was terminated past `SPUR_BUILD_TIMEOUT`. The undocumented-`500` crash
and the margin's disappearance under load are filed together as must-severity debt,
`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
— a server defect this phase does not fix (D-17).

**Reversibility.** `fleet-user`'s stop is reversible by `docker start` and is restored by
the human at this plan's close (D-06). The composed scenario SC3 added to `bench/latency.py`
is reversible by deletion alone; `DEFAULT_SCENARIOS` keeps the no-argument run at
(`concurrent`, `single`) unchanged, so the bar's own run is exactly what it was before this
phase. The floor itself — sample-to-sample variation at the achieved sample counts, not a
fixed property of this host — is costly to re-measure, not to revert: the bar's published
definition (<= 2.00x idle p95, no absolute-floor amendment adopted) is unchanged by this
entry, because outcome (a) made D-10's floor moot.

Reason: the 2026-09-23 waiver left two observations and a composed-concurrency question
open; this phase closed all three by measurement — two candidates ruled out or found not
reproducible, the bar demonstrated rather than accepted, and the composed worst row's
behaviour under real concurrency recorded and filed as debt rather than guessed at.
Machine: 12 CPUs, arm64, 32.0 GiB RAM (`.venv/bin/python -c "from bench import
machine_facts; print(machine_facts())"`, read 2026-10-02); macOS 27.0 (`sw_vers
-productVersion`), Darwin kernel 27.0.0 (`uname -r`); the investigation campaign ran
2026-10-02T02:36:53Z–03:11:43Z, the bar sessions 2026-10-02T03:41:00Z–07:18:00Z (approx),
and SC3 2026-10-02T08:08:01Z–08:23:01Z, all on this host.

## L33 — The root lead-in is warned, not re-cut, and the filleted-spoke cutout is proved against a closed form (amends L09, L10 and L30)

Date: 2026-10-03.

L09, L10 and L30 stay as written; this entry amends the root-zone claim README and
`_outline` made beside L09 and L10, and L30's clause that the filleted spoke's removed
volume is pinned because it has no closed form, with what Phase 14 measured and proved.

**The root lead-in** (D-01 to D-04, D-12, D-13). The kickoff choice, "warned, not re-cut":
the root fillet's straight chord can end above the pitch circle, and the alternative was to
re-cut the outline so it never does. That path was not taken — it regenerates the pre-v0.2
fixture under its own `Lxx` and changes the part of every shared link that sets a large
profile shift or root fillet (L05); REQUIREMENTS.md "Out of Scope" records it, and L10's
trochoidal root stays in `docs/ideas/`. The rule: `derive()` appends one sentence when
`round(spline_start(pr, root_fillet(p)) - pr.r, 3) > 0`, comparing at the resolution it
prints (10-REVIEW.md CR-01), so a height that would print as `0.000` is silent. The sentence
names the height and the cause (the root fillet is larger than half the dedendum) and quotes
no deviation figure and no remedy number: the retired debt file's planning-time deviation
figures had no script in the repo behind them, so the warning and README quote none of them
(L08). The real condition: the chord ends above the pitch circle exactly when the root fillet
exceeds half the dedendum, `(1.25 - x)*m/2`, **and** the profile shift `x` exceeds 0.125,
because the chord is capped halfway up the tooth at `r + (x - 0.125)*m`, so at or below that
shift a fillet over half the dedendum still ends at or under the pitch circle. The second
clause was found in planning (the first draft's condition alone was false wherever the cap
binds) and is pinned by the mid-tooth rows. The evidence: the 15 rows of
`test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle` — the default gear's
-1.1875 mm (silent), the debt file's two crossing configurations (+0.5625 mm at
`{profile_shift 1.0, pressure_angle 14.5}`, which prints 0.562 because Python rounds the
binary value half-to-even, and +0.125 mm at `{profile_shift 0.75, pressure_angle 20}`), one
field step either side of the crossing on each of `profile_shift`, `root_fillet` and
`module`, the mid-tooth trio (x 0.10 silent, 0.125 an exact touch and silent, 0.15 warns),
zero fillet, and the print-resolution pair (0.0003 mm silent, 0.001 mm warns) — each
asserting the fillet actually used, the height and the full warning string, captured from
`derive()` and never typed. All 44 records of the pre-v0.2 fixture sit below the crossing:
0 of 44 warn, recomputed 2026-10-03 on the committed code over `tests/regression/corpus.py`'s
cases (`14-03-SUMMARY.md`), so the fixture is byte-identical to `5d9e907` and
`tests/regression/test_pre_v0_2.py` still passes (85 passed, `14-01-SUMMARY.md`). README's
root-fillets bullet and `_outline`'s docstring no longer call the chord non-working; they
state the condition, the default gear's 1.188 mm below the pitch circle, and cite
`warnings`. Commits: `13857e1` (`feat(14-01)`, the warning), `ac607d7` (`test(14-01)`, the
15 rows), `825095f` (`docs(14-01): state ...`, README and `_outline`, the debt retired).

**The filleted-spoke proof** (D-05 to D-10). L30 said the cutout proof was checked to
`1e-9 mm3` against a closed form for holes, sharp spokes and honeycomb and pinned for the
filleted spoke, which has none. The filleted spoke does have one. `_filleted_spoke_volume`
in `tests/test_model.py` is the sharp opening, `pi*(rr^2 - rh^2) - n*_spoke_bar_area`, minus
the four corner cut-offs the fillets of radius `spoke_fillet_effective(p)` take off it (two
mirror pairs, one hub and one rim corner derived and each counted twice), times
`face_width`. Each fillet centre is placed from its two distances — `rho` off the bar side,
and `rh + rho` (hub) or `rr - rho` (rim) from the axis — and the circle's chord-versus-arc
sliver is subtracted at the hub and added at the rim; it never calls `_fillet_corner`, so a
wrong root, sign or side there disagrees with the oracle instead of moving both sides
together (D-09, L08). Measured 2026-10-03 on the pinned kernel pair, the kernel-to-formula
gap per row is: holes 2.39e-12 mm3, spokes-sharp 1.36e-12 mm3, spokes-filleted 2.73e-12 mm3,
cells 8.87e-12 mm3 (copied from the proof's docstring). Phase 11 measured this agreement but
asserted a relative bar on the filleted row (about 2.9e-3 mm3 there); the four rows now
assert the removed volume at `abs=1e-9` mm3, the largest gap (8.87e-12 mm3) under 1% of the bar. D-06
(a gap above 1e-9 mm3, which would have gone to the human for a decision) was not reached
on these four rows: no tolerance was loosened and none was set from a measured gap. The bar does **not** apply
to every caller of the shared assertion. Eleven composed-solid rows (9 of the 12 in
`test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore`, 2 of
the 3 in `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess`) pass
`volume_rel=1e-6`. Their `d_volume` is a 6 dp literal measured on the pinned kernel, because
no closed form has been derived for them here: the spokes and cells rows straddle the recess
walls, and on the hex bore the holes cross the recess outer wall. A 6 dp literal cannot meet
`abs=1e-9`; they keep the relative bar they had before this phase and never carried the 1e-9
claim. The other four composed rows (the d-flat, round and keyed holes with both recesses and
the tip chamfer, and the single-sided holes row) cut cylinders wholly inside the recess
annulus, so their removed volume is `6*pi*(hole_d/2)**2*web` and each asserts it instead of
a literal. Measured 2026-10-03 on the pinned kernel pair, the kernel-formula gaps are 5.85e-10,
5.94e-10 and 6.55e-10 mm3 on the three tip-chamfer rows and 2.79e-12 mm3 on the single-sided
row (copied from the docstrings). The tip chamfer causes the tip rows' offset: the d-flat row
without it measured 1.36e-12 mm3. The tip rows sit within 10x of `1e-9`, so before the bar
moved that went to the human (14-04 Task 2), who chose `abs=1e-8` for them, about 15x their
largest gap; the single-sided row asserts `abs=1e-9`. That `1e-8` is the one bar in this
phase set from a measured gap, and the human set it, not the executor (D-06). The eleven are
filed as
`docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md`
(nice; revisit when the kernel pair is bumped). The four cutout rows (holes, sharp spokes,
filleted spokes, honeycomb) and all three skip-the-cutout tripwire rows run at `abs=1e-9`.
The tripwire, `test_the_cutout_proof_fails_when_a_rim_corner_tangent_root_moves`: the
`inside=True` tangent root of `_fillet_corner` is moved by 1e-6 mm. The solid still builds
valid, the face delta (`{CYLINDER: 24, PLANE: 8}`) and edge delta (96) are the right ones,
and `derive()` still prints `spoke_fillet_effective`, so every check but the volume is blind
to it. The removed volume moves by 2.522e-4 mm3 (relative 8.59e-8) — inside the old
`rel=1e-6` bar, about 2.5e5 times the new one — and the `abs=1e-9` assertion goes red, so
loosening the bar back turns the test red. The shift is 1e-6 mm, not 0.01 mm: 0.01 mm moves
the volume by 2.522 mm3, which the old relative bar catches too. The literal 2934.725405
survives only as the docstring's record of the 2026-09-29 first measurement. Commits:
`61e1bea` (`test(14-02)`, the oracle, the bar, the tripwire, the debt retired) and `b00c44c`
(`docs(14-02)`, its sha recorded in the debt file).

**Reversibility.** Reversible on every axis this entry adds: the warning is one appended
sentence from a pure function that no fixture record carries; README and the docstring are
prose; the bar is one test tolerance (D-05). The path not taken stays costly and untouched:
re-cutting the outline re-cuts every link that sets a large profile shift or root fillet and
regenerates the fixture (L05, L26).

Reason: the record claimed two things it could not back — a lead-in always in the
non-working root zone, and a `1e-9` bar asserted on every cutout row with the filleted row
only pinned. This phase made each true, or warned, by tests rather than by re-pinning: the
lead-in warns where it crosses the pitch circle and README says where it really ends, the
four formula rows assert `1e-9` against closed forms, the four hole-through-web composed rows
assert the web formula (`1e-9` on the single-sided row, `1e-8` on the three tip rows), and
the 11 composed rows whose closed form is not derived here are named as debt instead of
implied.
Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1 (`importlib.metadata.version`), Python
3.12.13 (`sys.version.split()[0]`), read 2026-10-03; the four plain-row gaps, the tripwire's
shift and the four hole-through-web gaps were measured on 2026-10-03, the first
filleted-spoke measurement on 2026-09-29, all on this kernel pair.

**Amendment (2026-10-06, 14-REVIEW IN-02).** The tip rows' gaps (5.85e-10 to 6.55e-10 mm3)
sit below D-06's literal trigger of 1e-9 mm3, so at `abs=1e-9` they pass; they went to the
human at 14-04 Task 2 because the headroom was about 1.5x, thinner than D-06 anticipated,
not because the trigger fired. "The human set it, not the executor (D-06)" above credits
the trigger; the cause was the headroom.

## L34 — The gate is measured, runs on eight workers under a coverage floor, and CI installs the pinned kernel (amends L12 and L13)

Date: 2026-10-04.

L12 and L13 stay as written; this entry amends L13's "~11 s warm" and its unmeasured gate,
and L12's "loose ranges for developer environments" as far as CI is concerned, with what
Phase 15 measured, decided and proved.

**The measured gate** (D-01 to D-08). At the phase's start the gate was serial and had never
been profiled. Two runs of `make verify` without coverage, taken in the session
`bench/RESULTS.md` § "Host state" dates 2026-10-03 (HEAD `862a807`, code identical to
`20cd484`), read P1 230.20 s at load 6.53 and P2 218.36 s at load 9.09, mean 224.28 s, so
L13's "~11 s warm" was not what the gate cost. Pytest was 99.75 % and 99.85 % of the
gate (ruff, mypy, import-linter and the unfinished-work scan read 0.07, 0.37, 0.11 and 0.02 s
in P1), and `tests/test_model.py` was 74.1 % and 73.3 % of pytest's seconds (167.76 s over
201 items in P1): the kernel-level geometry proofs of L24, L26 to L31 and L33, with
`tests/test_pool.py` (8.5 % / 8.3 %), the pre-v0.2 regression replay (7.8 % / 7.9 %) and
`tests/test_api.py` (4.8 % / 5.2 %) behind it (`bench/RESULTS.md` § "Per-stage wall time",
§ "Per-file share", § "Heaviest contributors"). The `pytest-xdist` sweep read N = 2 at
130.72 s, N = 4 at 84.76 s, N = 8 at 68.93 s and N = 12 at 75.47 s, every row green with
927 passed (§ "xdist sweep"). The knee rule was fixed before any number was read: the
smallest N whose wall is within 1.10 times the fastest green wall. It gave K = 8 (N = 12
was inside the ceiling but is the larger N and slower). D-05's verdict is **adopted**: six
alternating runs at N = 8, three without and three with coverage, were 6 of 6 green with 927
passed each, no shared-state module failed, no `xdist_group` was needed and `tests/` is
untouched; coverage costs 3.51 s there, mean 60.61 s without it against 64.12 s with it
(§ "Tolerance and coverage cost"). The human's answer at the profile checkpoint, verbatim:
"knee-headroom N=8 bar=66 cuts=none before=244.59" (`15-CONTEXT.md` D-01 addendum;
§ "Gate decision"). The bar is 66 s of `make verify` wall time on the dev host, the largest of
the three `-n 8 --cov` runs (65.83 s) rounded up, read as the mean of alternating runs of
the gate as committed. N is 8. Cuts: none accepted; all 15 rows of § "Proposed cuts" were
priced from P1 and P2's own `--durations` lines and refused by name (three samples of
`tests/test_model.py` rows, skips of the pre-v0.2 solid replay and of two pool process tests,
seven removals in `tests/test_api.py` and two dedups), so no test was removed, skipped,
sampled or marked; the whole cut set deselected at once still read 96.40 %
coverage against the floor below. The Before row is the serial run with coverage, 244.59 s
(C0), not the no-coverage profile's 224.28 s. The Makefile `test` recipe runs
`pytest -n $(PYTEST_WORKERS) --cov --cov-report=term`, `PYTEST_WORKERS` being 8 clamped to
the host's online CPUs, one literal, overridable on the command line (`5797199`; `-n` stays out
of `addopts`, so a bare `pytest` and `make test-image` are serial, D-07). The reading, on
the same host and recipe, alternating serial A (`PYTEST_ARGS="-n0"`, coverage on) with B (the
gate as committed): A1 228.23 s, B1 64.19 s, A2 229.75 s, B2 62.92 s, so mean(A) 228.99 s and
**mean(B) 63.555 s**, a delta of -165.435 s (3.60 times faster), **the bar met** with 2.445 s
to spare (§ "Before and after", `b8b4dd1`). That is the warm figure that replaces L13's
"~11 s": the whole gate, `-n 8` with coverage, on a 12-core M2 Max; a commit through the
pre-commit hook (the gate plus the commit-msg hook) was timed at 63-64 s by `date`
(`15-04-SUMMARY.md`, context and not a bar reading). CI's 4-vCPU runner is never the bar
(D-02): its run read 203.16 s of pytest at `-n 4`. RESEARCH Open Question 3 is decided
as: no `bench/` script, the per-file awk and the RSS sampler are committed prose in
§ "Method" (a script would need its own tests under `mypy --strict` for two lines of awk).
Open Question 4 is decided as: CI's worker count is whatever the clamp gives, and the CI run's
own line states it, `created: 4/4 workers` (§ "CI run"). The five sites that repeated
"~11 s" outside this log now carry the figure (`ad99df9`); the commit-timeout debt stays
active, because the hook is ~64 s and gsd's 30 s commit timeout still kills it. Commits:
`39eb062` (the profile), `65ef9db` (the dev extras and the sweep), `5797199` (the workers),
`b8b4dd1` (the reading), `a5c9365` (the summary of it).

**The floor** (D-09 to D-12). C0, the serial `--cov` baseline, read 96.99 % over 1,069
statements and 294 branches (26 missed statements, 15 partial branches); the three `-n 8
--cov` runs read 97.21 % each (23 missed statements), so their spread is 0.00 points
(§ "Coverage baseline", § "Tolerance and coverage cost"). D-10's rule, a whole percent under
the lowest total less `max(0.25, spread)`, gives L = 96.99, S = 0.00, slack 0.25, 96.74 and
so `fail_under = 96`; `precision = 2` is set because coverage compares the total rounded to
`precision` and the default of 0 let a 45.93 % run pass a floor of 46, and one point is
13.63 units of 1,069 statements plus 294 branches, not the ~31 lines D-10's first text
counted (§ "Coverage floor"; the D-10 addendum). The literal lives in `pyproject.toml`
`[tool.coverage.report]` alone: `make test` passes no `--cov-fail-under`, so the floor is
read from config only (RESEARCH Open Question 2). Worker lines count through
`concurrency = ["multiprocessing", "thread"]`, `parallel = true` and `sigterm = true`,
and not through `pytest-cov`: version 7 dropped its subprocess hook, and `"multiprocessing"`
alone replaces coverage's default `"thread"`, which stops tracing the thread that builds and
shuts down `BuildPool` in the app's lifespan. This corrects D-09's first text (the D-09
addendum); `tests/test_pool.py` alone reads `src/spur/pool.py` at 100.00 % serially and at
`-n 2`. The red run: without `tests/test_cli.py` a full run at `-n 8` read 90.24 % against 96
and failed with `Coverage failure: total of 90.24 is less than fail-under=96.00` (§ "Red on
the floor", scratch, not committed). That section also records why the recipe is `--cov
--cov-report=term` and not a bare `--cov`: a bare `--cov` took the first path in
`PYTEST_ARGS` as its coverage source and ran the whole suite. One loss is not fixed and not
hidden: all three serial full `--cov` runs of the phase lost `pool.py` lines 63-67 and 222
(0.22 points, below the 0.99-point margin) and no `-n 8` run did; it is filed as the nice
debt `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`
(`4fef83d`). Commits: `f771c5e` (the config), `2aadcea` (the floor and `--cov` in `make
test`; the no-coverage-floor debt retired there, its sha recorded in `b8926e7`).

**The pin** (D-13 to D-16). CI's `make verify` step runs under `PIP_CONSTRAINT:
requirements.txt`, so L12's closure does one more job: its 31 `==` lines pin both halves of
the kernel pair, `cadquery` and `cadquery-ocp`, and every other runtime package to what the
image ships, for the pip calls inside `make venv`'s recipe (`ci(15-05)`, `839dfea`). L12's
"`pyproject.toml` keeps loose ranges for developer environments" stays true: the ranges and
`make venv` are untouched, and a developer's venv can still drift under the fixture, where
`test_the_fixture_was_captured_on_the_kernel_this_run_uses` stays the local remedy; the
unconstrained local path is `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md`
(D-14). Neither option the debt file named was taken. Installing the closure with `--no-deps`
and then the dev extras works, but the second install pulls the pruned transitive
dependencies back in and is CI-only by construction; an upper bound on `cadquery` pins every
environment and still leaves `cadquery-ocp` free to move inside cadquery 2.8.0's own cap, a
7.9.x patch under the fixture. A separate `pip -c` step would install into the runner's
Python, not `.venv` (RESEARCH Pitfall 8). The proof is one green run on draft PR #18,
https://github.com/halfb00t/spur/actions/runs/37181871926: the step `kernel pair this run
resolved` printed `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`, pytest printed `created: 4/4
workers` and `927 passed in 203.16s`, coverage read 97.29 % against the floor (§ "CI run").
Locally, a dry-run install under the constraint resolved that pair and the same install
under a scratch constraint of `cadquery-ocp==8.0.1.0.0` failed with `ResolutionImpossible`,
so the constraint fails closed. One run cannot show which of the constraint and cadquery
2.8.0's own `cadquery-ocp<8.0` cap held the pair, since both give 7.9.3.1.1 today. The
tripwire stays, its docstring now names `requirements.txt`, `PIP_CONSTRAINT`,
`docker/refresh-requirements.sh` and `make fixture.regen`; the fixture file is untouched. D-16
justified its print step with "absent on a cache hit"; that is false for this workflow (the D-16
addendum, RESEARCH Pitfall 14): run 37116412012 hit setup-python's pip cache and still printed
the pair in pip's install output, because the cache restores downloads and the venv is
created fresh, and the pin run did the same. The print step stands as the cheaper-to-read
proof, not the only one. The CI-kernel debt
`docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` retired
citing `839dfea` and that run (`454af54`).

**Reversibility.** `-n` is one Makefile variable and the floor one config literal; neither
touches a test. The pin is one env line in `ci.yml` (D-13 rated it reversible). The costly
direction is a kernel bump: it moves `requirements.txt` through
`docker/refresh-requirements.sh` and regenerates the fixture together (`make fixture.regen`),
under its own `Lxx`.

Reason: L13 promised a gate whose cost nobody had measured, and it had grown to 224.28 s
serial without a floor on what it covered; L12's ranges let CI's kernel drift under a
fixture that pins one pair. Phase 15 measured the first, brought it to 63.555 s without
removing a single proof, put a floor under coverage that counts the worker processes, and
made CI install what the fixture was captured on.
Machine: 12 CPUs, arm64, 32.0 GiB RAM (`.venv/bin/python -c "from bench import
machine_facts; print(machine_facts())"`, read 2026-10-04), Apple M2 Max; macOS 27.0.1
(`sw_vers -productVersion`), Darwin kernel 27.0.0 (`uname -r`). The profile session is the
one `bench/RESULTS.md` § "Host state" dates 2026-10-03; the coverage, tolerance and
before/after runs were taken on 2026-10-04, and CI run 37181871926 on the same day on
GitHub's 4-vCPU `ubuntu-latest`.

**Amendment (2026-10-06, 15-REVIEW WR-01 and IN-03).** "Runs on eight workers" means up to
eight: `PYTEST_WORKERS` is 8 clamped to the online CPUs, so GitHub's 4-vCPU runner runs
`-n 4`, and there the gain is not reproduced — `927 passed in 193.21s` serial without
coverage (run 37116412012) against `203.16s` at `-n 4` with coverage (run 37181871926), two
single runs on different commits, set beside each other in `bench/RESULTS.md` § "CI run".
The 3.60x above is against the re-measured serial A mean (228.99 s), taken in alternation
with B in 15-04, not against C0's 244.59 s in the human's answer; C0 was taken before `-n 8`
went in and is 15.6 s slower than the A mean, cause untested (against C0 the delta would
read -181.0 s, 3.85x).

## L35 — Vendor shape typing stops at two checked boundaries, and Phases 7 and 8 carry a Nyquist record (amends L21)

Date: 2026-10-05.

L21 stays as written; this entry amends its house rule ("a value a library already names
keeps the library's own alias") with where CadQuery's own `Shape` typing now stops in
`model.py`, and records Phases 7 and 8's Nyquist pass. The five `type: ignore`s that L21's
ratchet left standing in `model.py` are gone, and a sixth cannot arrive unseen.

**The narrowing** (16-CONTEXT D-01 to D-07, D-14, D-16). `_body(shape: cq.Shape) ->
cq.Solid | cq.Compound` stands at the three `fillet`/`chamfer` sites and `_shape_of(wp:
cq.Workplane) -> cq.Shape` at the two `.val()` sites. Each is one `isinstance` check that
raises `BuildError` with the same message, the class name filled in: "Geometry kernel
returned a {} where a solid body was expected: a modelling defect in the build pipeline,
not a parameter problem." The five suppressions it retired stood at lines 213, 237, 239,
411 and 420 of `src/spur/model.py` at `085e5a6`. It is `isinstance` and not `typing.cast`
because a cast can turn mypy green while the value is wrong and gives a test nothing to
see; and not `TypeIs`, which is the same check behind more ceremony. The runtime types are
the ones 16-CONTEXT's domain facts measured on 2026-10-04 (cadquery 2.8.0, cadquery-ocp
7.9.3.1.1): a `Solid` after `_gear_blank`, a `Compound` after `_cut_face_recesses` and
after every later step, a step whose feature is off returning its input unchanged, and
`Solid.cut(Solid)` a `Compound`. `Shape.cut` is typed `-> Shape` whatever goes in, and
`fillet` and `chamfer` belong to `Mixin3D`, which only `Solid` and `Compound` carry. That is
why the debt file's plan, "cast once at `.val()`", could not hold: it reaches `_ring` and
the bore's `hole.val()`, two of five, and the three `attr-defined` sites need `Mixin3D`
after a `cut`. The pipeline's annotations stay at `cq.Shape`, `_gear_blank` included: the
narrower `-> cq.Solid` made mypy infer `solid: Solid` in `_build` and gave five
`[assignment]` errors there (16-RESEARCH Pitfall 1). `cadquery.*` left
`[[tool.mypy.overrides]]`, which now names `OCP.*` alone: cadquery ships `py.typed` (mypy
reads its annotations, which is why the errors existed) and OCP ships no type information.
With the cache cleared, mypy's output over `src tests docker bench scripts` was
byte-identical before and after, both "Success: no issues found in 37 source files"
(16-01-SUMMARY, D-04's gate). `make no-fake-done` now refuses a mypy suppression under
`src/spur/` and only there, because `tests/test_calc.py` and `tests/test_cli.py` each carry
one on purpose; it was seen red against the five lines at `085e5a6` and green after.
`RUF100` governs `noqa` and never mypy suppressions; mypy strict's `warn_unused_ignores` is
what refuses a stale one, and until the pin nothing refused a new one. The error surfaces
as a 422 `build_error` and a WARNING record, like the three selector guards
(`_groove_floor_edges`, `_bore_rim_edges`, `_tip_edges`) that already say "a modelling
defect"; no settable field can make it fire, so the status code is a known trade-off and
no new exception class was added (16-RESEARCH Finding 14). The suite went from 927 to 929
collected, the two refusal tests asserting the whole message with `==`. The five-site
gear's (type, isValid, volume at 6 dp, faces, edges), `build(GearParams(tip_chamfer=0.5))`,
reads `('Solid', True, 4446.54642, 210, 604)` before and after, and
`tests/regression/pre_v0_2.json` is byte-identical to `085e5a6`. Commits: `4f7e8fe` (the
code, the gate, the override, the implementation note and the debt retired) and `c11213e`
(its sha recorded in the debt file).

**The Nyquist pass** (D-08 to D-11). The human ran `/gsd-validate-phase 7` and `8` at
16-02's checkpoint, against the archived directories in place under
`.planning/milestones/v0.2-phases/`: `init.phase-op` resolves them, so no temporary copy was
made. `07-VALIDATION.md` reads `nyquist_compliant: true` and `08-VALIDATION.md` reads
`nyquist_compliant: true`, both at `status: validated`, as read from the committed
frontmatter and not asserted. Phase 7 ran twice (`655583f`, then `5ba02d2`, which corrected
one quick-run command); Phase 8 once (`8ae468e`). Both audits reported 0 gaps, so, as far
as the record shows, the "Fix all gaps / Skip" gate was never reached; no D-09 question was
asked. 16-02's gap
ledger counts every Manual-Only data row, whatever the audit called it: three for Phase 7,
none for Phase 8, all `nice`, none a behaviour without a test. The three are one debt file,
`docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` (`4035b04`); Phase 8 has no
debt file. No test was written. The v0.2 audit's `nyquist` block was amended in place and
dated (`3b9d977`): `missing_phases: []`, 07 and 08 in `compliant_phases`, `overall:
compliant` by the rule written beside the new rows (a phase is COMPLIANT on
`status: validated`, `nyquist_compliant: true` and every Status cell green or manual;
`overall` reads `compliant` only when no phase is partial, not validated or missing). The
original six rows and the original Overall line are byte-identical; audit-milestone §5.5
defines the per-phase classes but not `overall`, so that rule is inferred from the original
`partial` for 4 compliant and 2 missing.

**Reversibility.** Reversible: two helpers and five call sites (D-01), one override entry
(D-04), one Makefile block (D-05); the audit amendment is dated and additive.

Reason: L21 ended with a ratchet that had a hole in it, five suppressions it could not see
and nothing to stop a sixth, and the record said Phases 7 and 8 had no Nyquist file because
nobody knew whether the skill could reach an archived directory. Phase 16 narrowed the
types where a check is possible, pinned the result, and measured the second question
instead of assuming it.
Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1, read 2026-10-04 (16-CONTEXT.md, domain
facts); the five-site gear tuple and the mypy comparison were taken the same day (16-01).

**Amendment (2026-10-06, 16-REVIEW WR-01).** A third narrowing survived in `_cell_cutters`,
raising a bare `TypeError` that `_build_checked` relabelled as the catch-all remedy; it now
goes through `_shape_of` and raises `BuildError` with the same message, so "two checked
boundaries" reads as the two helpers plus that one call site, which reuses them.

**Amendment (2026-10-06, 16-REVIEW WR-02).** "A sixth cannot arrive unseen" overstated the
pin: it matched one spelling in tracked files. It now refuses `type: ignore` with any
spacing and case and the whole-file `mypy: ignore-errors`, in `src/spur/*.py` tracked or
untracked (`git grep -i --untracked`), each probed by `tests/test_no_fake_done.py`;
`pyright: ignore` is not refused and nothing wider is claimed.

## L36 — The commit stage runs a named prefix of the gate under 30 s, and the whole gate moves to pre-push (amends L13 and L34)

Date: 2026-10-06.

L13 and L34 stay as written. This entry amends L13's "the pre-commit hook" (the same
`make verify` still runs in three places, now the pre-push hook, CI and `make worktree.land`,
and the commit stage runs `make verify.fast`, a named prefix of it) and L34's closing
sentence that the commit-timeout debt stays active.

**The conflict.** gsd-core 1.16.0 kills every SDK `git commit` at `COMMIT_TIMEOUT_MS = 30_000`
(`bin/lib/commands.cjs`; the symbol, not a line, because lines drift) and has no config key
for it. The pre-commit hook ran the whole gate, 63.555 s warm (L34), so every SDK commit
returned `{committed: false, reason: 'commit_timeout'}`.

**The decision** (D-01). Two moves together: a sub-30 s subset at the commit stage and the
whole `make verify` at the push stage; CI, the `main` ruleset and `make pr.land` stay the wall
(L22, L25). Rejected: raising the timeout upstream alone, because nothing ships and the next
SDK commit is still killed; moving the gate to pre-push alone, because no check would run at
the commit boundary during the trochoid phases, where the L26 fixture replay matters most;
the subset alone, because the full gate would go unenforced locally until CI.

**The subset** (D-02, D-04). The four static steps (`lint typecheck lint-imports no-fake-done`)
plus pytest over every test file but tests/test_model.py, tests/test_pool.py, tests/test_api.py
and tests/test_cli.py, chosen by `--ignore=` exclusion so a new test file runs at commit until
someone names it heavy, at `-n 8 --no-cov`. `--no-cov` is mandatory: `fail_under = 96` reads a
partial run as a failure. Re-priced on 2026-10-06 on the 12-CPU M2 Max, `make verify.fast` read
11.28 s wall at 08:54:31Z (1-min load 2.99), 11.30 s at 08:54:42Z (load 4.40) and 11.28 s at
08:54:54Z (load 5.51), each with `620 passed` in 10.75 to 10.76 s, and 19.94 s at 08:55:05Z
(load 5.04) with an empty mypy cache (`620 passed in 10.77 s`). All four are under the 30.0 s
kill with at least 10 s of headroom. The earlier baseline from 17-RESEARCH (2026-10-06, load
3.75 to 4.07) was 617 passed in 11.98 s (12.18 s wall) and 8.68 s for mypy with an empty cache;
the three extra tests are tests/test_hooks.py. The slice imports the kernel (tests/test_bench.py
through `bench.build_time`, and the regression replay's solids), so an OS-cold page cache was
not priced: D-07 is the recovery if a commit ever runs over.

**The shape** (D-03). `verify: verify.static test` and `verify.fast: verify.static test.fast`,
with `verify.static` the shared prefix and `test.fast` the gate's own pytest recipe with
narrower arguments, so `make -n verify` lists the four static recipes before exactly one pytest
line and the gate's cost is unchanged. `verify: verify.fast test` was rejected: it runs the
slice twice, taking the gate from about 64 s to about 75 s, over L34's 66 s bar.
tests/test_hooks.py pins the hook entries, their stages and the shared prefix, so the commit
stage cannot become a second list of checks.

**The hooks and what pre-push guarantees** (D-05). `default_install_hook_types` is
`[pre-commit, commit-msg, pre-push]` and every hook is pinned to one stage: `verify-fast` at
pre-commit, `verify` at pre-push, `no-skip-token` at commit-msg. Nine pre-push scenarios were
run in a scratch repo with a bare remote (pre-commit 4.6.2, git 2.54.0, 2026-10-06; a hook
that appends to a log, counted per push):

| # | Scenario | `full` runs | Evidence |
|---|----------|-------------|----------|
| 1 | first push of `HEAD:main` | 1 | the log line |
| 2 | the same push again | 0 | `Everything up-to-date` |
| 3 | unstaged edit to a tracked file and an untracked file | 1 | log `tracked=base untracked=untracked.txt`; `Stashing unstaged files` |
| 4 | two refs in one `git push` | 1 | once per push, not per ref |
| 5 | tag-only push, tag on an already-pushed commit | 0 | `[new tag]`, no hook |
| 6 | delete-only push | 0 | `[deleted]`, no hook |
| 7 | `git push --no-verify` | 0 | no hook |
| 8 | `SKIP=full git push` | 0 | `Skipped` |
| 9 | fresh clone of the remote | no hook | `.git/hooks` holds no `pre-push`: hooks are per clone |

Row 5 needs the remote added by name (`git remote add origin`): pre-commit's
`hook_impl.py` selects the commits to check with `rev-list ... --not --remotes=<remote name>`,
so a push to a bare URL matches no remote-tracking ref and ran the hook on the tag-only push
(1 run in the first, URL-form run). The repository's own pushes go to `origin`. This settles
the research's open question about unstaged changes: they are stashed, so the gate reads the
committed content plus untracked files, which stay visible. What pre-push does not verify is
an arbitrary sha pushed from another checkout (PITFALLS 13): the hook runs against whatever is
checked out, and CI and the ruleset are what catch it.

**Who installs** (D-06). The Makefile's `$(HOOKS)` stamp (`.venv/.hooks-installed`, newer than
`.pre-commit-config.yaml` and `$(STAMP)`) runs `pre-commit install` from `verify.static` and
`venv`, so "run `make venv` once in the main checkout" installs all three types and a config
change re-installs on the next gate run. Only in the main checkout: pre-commit 4.6.2 writes into
`git rev-parse --git-common-dir`, which every linked worktree shares, and bakes the installing
venv's python into the shim, so an install from a worktree would point every checkout's hooks
at a venv `make worktree.land` deletes. tests/test_hooks.py proves both branches. CI runs the
same install against its own checkout and fires no hook (assumption A1: checked on a shallow
clone locally in 17-02; the phase's first CI run is read at ship).

**Which commits can now be red.** A local or phase-branch commit that fails only
tests/test_model.py, tests/test_pool.py, tests/test_api.py or tests/test_cli.py, so
`git bisect` can land on one. The push runs the whole gate, and `main` cannot receive one:
L22's ruleset, `make pr.land` and CI refuse a red head.

**A killed commit** (D-07). Measured in PITFALLS 15 (git 2.54.0, Node `spawnSync`, 2026-10-06):
a killed `git commit` leaves nothing committed and no `index.lock`, and the hook keeps running
to completion as an orphan with parent PID 1. The rule for this repository: wait until
`pgrep -fl 'pre_commit hook-impl|pytest|mypy'` prints nothing, then make exactly one plain
`git commit`, record it in the plan's SUMMARY, and never retry the SDK commit blind. It
supersedes the `commit_timeout` bullet of `~/.claude/gsd-core/agents/gsd-executor.md`, whose
remove-the-lock-and-retry recovery assumed a warm retry passes.

**Before a push** (D-09). Run `make verify`, then push: the explicit run warms the page cache
and shows the result, so the pre-push hook runs warm inside a shell tool's 120 s default.

**Upstream** (D-08). A request for a configurable `COMMIT_TIMEOUT_MS` is filed on
open-gsd/gsd-core, cited here and never depended on, with #3886 as prior art; `~/.claude/gsd-core`
is not patched. Its URL and date are recorded below with this entry's commit sha (17-02).

**Reversibility.** Costly (D-01): undoing touches `.pre-commit-config.yaml`, the Makefile,
eight doc sites and needs a superseding entry.

Reason: the gate outgrew the SDK's commit window. The commit stage keeps the fixture replay and
the calc tests (where Phase 18's maths lands) at the commit boundary, and the whole gate still
runs before anything leaves the machine.
Machine: 12 CPUs, Apple M2 Max, 32 GiB RAM (`sysctl -n hw.ncpu machdep.cpu.brand_string
hw.memsize`); macOS 27.0.1 (`sw_vers -productVersion`), Darwin kernel 27.0.0 (`uname -r`); the
four `make verify.fast` readings and the nine scratch rows were taken on 2026-10-06.

**Recorded after this entry's commit (2026-10-06).** The hook commit is `c06749d`
(`build(gate): run make verify.fast at commit and make verify at push (L36)`); it went through
its own new commit stage in 12.33 s real (`make verify.fast ... Passed`). Two proofs a commit
cannot carry about itself were taken afterwards, in 17-02. The pre-push stage: `make verify`
first (D-09), exit 0, `937 passed in 61.19s`, 97.24% coverage, 61.97 s real; then a plain
`git push` of HEAD to an empty scratch bare repository with this repository's own hooks, no
`--no-verify` and no `SKIP=`, printed `make verify (ruff, mypy, import boundaries,
unfinished-work scan, pytest).......................Passed`, created the branch and took 63.97 s
real. The install: a `--depth 1` clone of the branch ran `pre-commit install` and
`.git/hooks` held commit-msg, pre-commit and pre-push. That clone was macOS, not GitHub's
Linux runner, so assumptions A1 and A3 stay open until the phase's first CI run is read at ship.
The upstream request is filed: https://github.com/open-gsd/gsd-core/issues/5231, 2026-10-06, with #3886 as prior art; a search of open and
closed issues for `COMMIT_TIMEOUT_MS` found nothing and for "commit timeout" only #3886. This
paragraph is committed by gsd's own SDK commit, the commit L36 exists to make possible; its JSON
result is `.planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-sdk-commit.json`.

## L37 — The heaviest allowed composed row is a documented 503 timeout under concurrent load, and no default moves (amends L31 and L32)

Date: 2026-10-06.

L31 and L32 stay as written. L31's "every row inside 30 s" holds one build at a time; this
entry records what happens past it under contention, and closes the margin finding that L32
filed together with the same-slot timeout race. The race itself was fixed in 17-04 (`0628182`);
the margin is decided here, by recording it, not by moving a number.

**The row** (D-10). `bench/sweeps/composed.json` row 4 (1-based), the heaviest composed row the
limits allow: `teeth=200 module=10 bore_d=9 bore_flat=0 keyway_width=3 keyway_depth=1.4
spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3
recess_sides=both`. A cold request for it is one build plus one export.

**The numbers that set it** (D-11), each in the unit it was recorded in and cited to its section.
No dedicated worst-row-under-N sweep was run; these are the readings that exist.

- *Alone:* 29.42 s of 30 s, 0.58 s of margin, one build at a time, on the 12-core M2 Max, on
  2026-09-30 at 1-minute load 1.65 before launch and 1.68 at the runner's own start reading
  (`bench/RESULTS.md` "### Re-run after the gate (lower-le: spoke_count 32)", Phase 12; the
  paragraph after its table carries a dated note since this entry).
- *The threshold pair the cap rests on:* `spoke_count` 32 read 29.41 s and 33 read 30.11 s on this
  row (`bench/RESULTS.md` "### Gate probe", Phase 12, build plus the slower export, host load
  2.40 to 29.51 across the probe).
- *SC3, both workers busy, ten distinct rows:* this row's request (`51e80f35`) ended
  `BuildTimeout` at `duration_ms` 30004, as the server recorded it
  (`.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl`;
  `bench/RESULTS.md` "### Composed worst row under ten concurrent builds (Phase 13)"), on
  2026-10-02 with the quiet-gate samples at 1.53 to 9.92 and the load after at 4.74. Four of the
  ten requests were admitted, and all four exceeded `SPUR_BUILD_TIMEOUT`.
- *`identical`, one worker busy, three requests queued behind it:* the same row ten times, one
  cache key, one hash slot, on a fresh server with shipping defaults (`bench/RESULTS.md` "##
  Same-slot timeout race (Phase 17)"). The slot-holding request (29.42 s alone) read `503
  timeout` both times: at this load, 5.48 to 5.88 (1-minute), on 2026-10-06 at 09:17Z, 30.01 s
  client wall and server `duration_ms` 30003 (17-03, request `cf3e6608`, commit `814f4f3`, before
  the fix); and at this load, 18.94 at the server start to 15.30 after the client, on 2026-10-06
  at 09:58Z, 30.01 s client wall and server `duration_ms` 30003 (17-05, request `d6cd9587`,
  commit `0628182`, after the fix).

The two contention shapes are kept apart: SC3 had both workers busy with ten different rows;
`identical` had one worker busy and the other idle. Neither is a margin under N concurrent builds,
and none of the four lines above is converted into a ratio here. A timeout reading records only
that the build had not returned when the 30 s elapsed, not how long it would have taken: 30004
and 30003 are the deadline firing, not the row's own time.

**The decision** (D-10). The limit is recorded as documented behaviour. `SPUR_BUILD_TIMEOUT`
stays 30 s and `spoke_count`'s `le` stays 32. `503 timeout` is the contract for this row under
concurrent load, and a slower or busier host raises the variable. L05 holds (no default or cap moved, so
every shared link that builds today still builds, and an unset parameter still never changes the
part) and L08 holds (no figure was tuned toward a pass; each is a recorded reading with its
section and its load). Rejected, with the reason: raising the default, because every deployment
would wait longer on a wedged worker, the 4x-slower-hardware rationale in `app.py`'s comment would
need restating, and there is no proven margin on slower hosts either; lowering `spoke_count`'s
`le` a third time (200 to 40 in Phase 11, 40 to 32 in Phase 12), because it needs a new concurrent
sweep to choose the number and every link at 32 spokes would start returning `422`.

**The contract at the boundary.** A build that has not returned when `SPUR_BUILD_TIMEOUT` elapses
gets `503 timeout` and its worker is terminated and replaced, whatever it takes alone; SC3's 30004
ms is that boundary observed. Since 17-04's fix (`0628182`), a second same-slot timeout of the same
incident gets the same documented 503 and never a raw 500: `_run_with_timeout` terminates and
replaces the worker only when the slot still holds its own executor and that executor's
`_processes` is not `None`, and `BuildPool._closed` stops a closed pool building a replacement.
The proof is the deterministic stale-executor test, red before (`3 failed, 1 passed`, the passing
one being the ast check that is meant to pass on the old code) and green after (`74 passed` for
`tests/test_pool.py` and `tests/test_api.py`), plus the loops: 20 of 20 runs at `-n 8 --cov`, 20
of 20 at `-n 4 --cov`, and 2 of 3 whole `make verify` runs, the third lost to the known
resource-tracker flake and accepted by the human (`17-04-SUMMARY.md`, per run in
`.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-stability.md`). The
bench agrees but is not the proof: the same scenario showed three `500`s with three `AttributeError`
`build.failed` records on `814f4f3`, and on `0628182` four admitted requests all ended `503 timeout`
with no `500` and no `AttributeError` (`bench/RESULTS.md` "### Before the fix: verdict" and "###
After the fix").

**Where it reaches users** (D-12). One sentence in `README.md`'s paragraph on build workers; one
sentence in the comment beside `int_env("SPUR_BUILD_TIMEOUT", 30)` in `src/spur/app.py`, whose own
trigger ("re-measure and adjust if the worst observed build ever approaches this value") has
fired and which this entry answers; and a dated note on the 0.58 s paragraph in `bench/RESULTS.md`
and on the resolved tip-chamfer debt's 30 s over 29.42 s line. The earlier text of both is
unedited.

**Revisit when** (D-13). Phase 19's composed re-measure (REQ-trochoid-composes-and-is-priced
measures the heaviest row against `SPUR_BUILD_TIMEOUT` anyway), or any change to
`SPUR_BUILD_TIMEOUT`'s default or to an `le` cap.

**Reversibility.** Reversible: no default, cap or code path moved by this entry. A later entry
can raise the default or lower a cap with its own measurement; nothing here has to be undone first.

Reason: the margin finding L32 filed was a single-build figure that did not survive contention,
and the choice was between moving a number a shared link depends on and saying what the service
does. L05 and L08 pick the second, so the limit is now stated where it is read, with the readings
that set it and the load each was taken at.
Machine: 12 CPUs, Apple M2 Max, 32 GiB RAM (`sysctl -n hw.ncpu machdep.cpu.brand_string
hw.memsize`); macOS 27.0.1 (`sw_vers -productVersion`), Darwin kernel 27.0.0 (`uname -r`); the
two `identical` readings were taken on 2026-10-06, SC3 on 2026-10-02, the Phase 12 readings on
2026-09-30.

## L38 — The hob-cut root is opt-in through root_shape, every number beside it is proved or warned, and the default does not move in v0.4 (supersedes L10, amends L09 and L33)

Date: 2026-10-09.

L09, L10, L33 and L37 stay as written; this entry supersedes L10 and amends L09 and L33 with
what Phase 19 built, measured and had the human decide, and it answers L37's "Revisit when"
clause. Every figure below is cited to the plan SUMMARY (and its commit sha) or to the
`bench/RESULTS.md` subsection under "Trochoid in the part (Phase 19)" that holds it. None is
re-estimated here, and no figure is carried from one host to another.

**The choice** (D-01, D-02, D-05, D-08; O4). The hob-cut root is opt-in.
`root_shape: Literal["radial", "trochoid"] = "radial"` joins `GearParams`' Teeth group directly
after `tip_chamfer`, a plain `Field` with no `step`, so the schema carries the enum, the form
renders a `<select>` and the CLI generates `--root-shape {radial,trochoid}` with no edit to
`cli.py`. It is a `Literal`, never a bool, because `--flag false` reads true. Under `trochoid`
`root_fillet` is the hob's tip radius: its millimetre value goes to `cutter()` as the radius,
capped by the cutter's geometric maximum and warned with the cap sentence, `0` a legal sharp hob,
and the printed `root_fillet` is the radius actually cut (19-04, `d58707f`). In radial mode it
stays the analytic fillet radius (L09). The trochoid applies only where the base circle is above
the root circle; a request elsewhere builds the radial part and says so ("No radial root to
replace on this gear (base circle 19.734 mm, root circle 19.750 mm): the trochoid root request
is ignored." at 42 teeth, module 1, 20 degrees, 19-04) (18 D-02). **The default does not move in
v0.4**: a link that omits `root_shape` reads `radial`, so no shared link moves (L05), the 44
fixture records all read radial with no curve and no warning, and `tests/regression` passed
unmodified at every plan (86 passed, 19-04 to 19-06). Phase 20, the flip, is skipped. The
human confirmed the field name, the group and the `root_fillet` reinterpretation at 19-02
(`d02-confirm`, replying `take the recommendations` on 2026-10-09, the option ids mapped by the
orchestrator from the first executor's stated recommendations; 10,326 of 10,326 trochoid gears of
the sweep product built, `bench/RESULTS.md` "Bars adopted (19-02)").

**What a future flip must do** (D-08, D-09). Changing the default is one commit that carries the
predicate change, the `make fixture.regen` output and an `Lxx` that lists the moving records
before they move (L26 D-03: the fixture changes only via `make fixture.regen`, in its own commit,
never in a feature commit; 18 D-01: the default stays off this milestone). 19-CONTEXT D-08 quotes
18 D-05's measured step of 0.08 to 0.14 mm at 41 to 42 teeth, which a default user never meets
while the default stays radial. The trigger is demand, not time: **a real fit report, or a
request for a mating pair below `z_min`** (D-09), the trigger `docs/ideas/2026-09-21-trochoidal-root-fillets.md`
already records. REQUIREMENTS.md "Trochoid follow-ups" owns the flip from here. It is not
"the next milestone that touches the root".

**What it supersedes and amends.** *L10* (radial root below the base circle, with a warning):
the radial root is now the default, not the only root. In radial mode, and for a trochoid request
that was refused for having nothing radial to replace, the undercut sentence is byte-identical to
the string the five fixture records carry ("Below 51.0 teeth a cut gear would be undercut; this
model uses a radial root instead.", 19-06, `fe8fed9`). Where the trochoid applies, the sentence is
restated from the cutter that cut the part and says nothing about a radial root: it fires on the
crossing join (`curve.join == "crossing"`), not on the printed onset, so a join inside the `1e-4`
`rb` band reads tangent and prints nothing, exactly as its part is built; the onset is rounded up to
0.1 teeth and the avoiding shift up to 0.001, residue removed first, and no shift is printed above
the field's 1.0 (the sentence then says none in range avoids it). 17 teeth print "Below 17.1 teeth
... 0.006 or more", 18 print nothing; 10 teeth advise 0.416, where the cutter's roll is +2.7e-3 mm
and negative at 0.415, which rounding to nearest would have printed (19-06). *L09* (root fillets are
computed, not filleted): the analytic fillet stays for the radial root. The hob root is one spline
per tooth side through `RootCurve`, six side faces per tooth against eight (134 faces and 376 edges
against the default part's 172 and 490, 19-04), not a kernel fillet, and the generator never enters
`model.py` (a source test with its own tripwire, 19-04 and 19-05). *L33* (the root lead-in is warned,
not re-cut): the lead-in warning is evaluated only where a chord exists, the radial root; under the
hob root there is no chord and no lead-in sentence. L33's condition and its 15 rows are untouched
in radial mode.

**The part** (19-04, 19-05, 19-01, 19-09). `_trochoid_outline` takes the junction vector from one
float: the root curve's last `Vector` is the first involute point, so the two splines cannot name
different junctions. `tip_chamfer_limit` reads the same root through `RootMode.curve`, and its third
bound under the trochoid is `ra - R_join - TIP_CHAMFER_MARGIN`. L29's law was re-bisected across the
spline-to-spline junction, 20 halvings on 14 rows (19-01, `7a0268f`): `Verdict: law holds -- 8 rows
on the law, 6 conservative`, no optimistic row, worst `last ok - pred` on a row on the law -3.06e-06 mm
(`bench/RESULTS.md` "Chamfer across the junction (19-01)"), and `TIP_CHAMFER_MARGIN` stands at 0.001 mm.
The same 14 rows were re-run on the shipped build with identical results (19-09, `4b08aa8`,
"Chamfer law on the real build (19-09)"), and 19-08 pins the cap on the 6-tooth row where it binds: the printed 0.9 mm builds, and one 0.05 mm
step past `ra - R_join` the kernel raises (`6607f69`).

- *`ROOT_ARC_MIN` = 2e-6 mm* (19-02, "Root arc dead band (19-02)"; 19-05, `4b2b03a`). The kernel
  raises `GC_MakeArcOfCircle::Value() - no result` at every root-arc chord from 2e-9 to 2.0e-7 mm
  and at exactly 0, silently drops the arc at 2e-12 and 2e-10 mm (62 faces where 74 are expected)
  and builds from 4.0e-7 mm. The constant is 10.0x the last failing chord and 15.8x below the
  smallest real chord in the product, 3.1644e-5 mm. A root arc under it is left out and the two
  teeth share one vertex. The band is reachable from user input (12 teeth, module 1, 20 degrees,
  `root_fillet` 3.0, backlash 0.19898413579248878 leaves a tip land of 1.000e-08 mm); that gear
  now builds one valid solid of 62 faces, 5 x 12 + 2, through `build(p)`.
- *Four guards that do not rest on `isValid()`* (19-05, `356682b`; bars from "Bars adopted
  (19-02)", set from the whole product of 10,326 trochoid gears, no stride): junction gap
  `ROOT_JUNCTION_BAR_RAD` 1e-11 rad (40.9x the tangent-join maximum 2.442e-13 rad; 18-01's 1e-12
  rad is only 4.1x over it and is not reused); point spacing `ROOT_SPACING_RATIO_MAX` 1000 (75.0x the
  worst ratio 13.325; the kernel first fails at a chord ratio of 728,888, 729x above the bar); the
  root splines inside the annulus `[rf - TOL, ra + TOL]` with `TOL` = 1e-6 mm (8.8e6x the worst
  excursion, 1.137e-13 mm); face area against the polygon through each arc's midpoint,
  `ROOT_AREA_REL_MAX` 5e-2 (13.6x the worst miss, 3.6791e-3). The plan's own measure, with both
  arcs taken as chords, read 1.2162e-2 and no listed bar reached 10x (the largest, 0.1, is 8.2x), so
  the human chose the midpoint measure at 19-02. Each guard raises a `BuildError` that says it is a
  modelling defect in spur and names `root_shape` radial as the remedy, never "try smaller", and
  each is reached by its own test, and loosening its bar makes that test fail (a mutation run, 19-05).
- *The kernel tier* (19-02 d8abb23; 19-04, `ad8c51a`). The spline deviation is the distance from a
  kernel-spline sample to the reference polyline (method B). It reproduces the research's three
  figures to 0.07, 0.33 and 0.53 of a unit of the third digit, and the oracle agrees with it to 0.01 of
  that unit on seven rows; method A (nearest vertex) is the reference's own vertex-spacing floor and
  is never a bar ("Spline deviation and the kernel bar (19-02)"). `KERNEL_BAR_PER_MODULE` = 2e-3 is
  10.9x the worst whole-product spline error, 1.8431e-4 per module, and the human adopted it
  (`bar-proposed`, `take the recommendations`, 2026-10-09). It is read at 401 positions per root
  edge, because 41 positions can sit 28 % low (4.4785e-4 against 6.2097e-4 mm on the module-10 row).
  The seven rows read 2.2595e-05 to 6.2097e-04 mm (19-04's table). The tripwire, the module-1
  10-tooth row read 0.05 mm off the printed radius, reads 1.1039e-2 mm, 5.5x over the bar; it must stay on
  a module-1 row, because on module 10 the same shift reads 0.66x of the bar.

**The numbers** (D-03, D-04, D-05, D-06, D-07). A number printed beside the hob root has a proof or
a warning, or it is null.
- `root_thickness` and `root_gap` are null with one sentence under the hob root. The thickness at the
  root circle changes too fast with radius to give one honest number there: on the default gear at tip
  radius 0.5 mm it measured 4.532 mm of arc at `rf + 0.00175` mm and 3.405 mm at `rf + 0.525` mm (19-04;
  the research's 4.68 and 3.51 mm did not reproduce). Both keep their numbers in radial mode.
- `root_form_d` is twice the junction radius from `RootCurve`, 3 dp, null in radial mode and on replay:
  the cutter-envelope junction (30.558 on the default gear, 19-06, `6032926`). It is not a form
  diameter in ISO 21771's sense, and no label, schema description or README line calls it one (a test
  holds that). Its proof is Phase 18's junction bars and T4's KISSsoft anchor on the tangent branch.
- `root_waist` is the tooth's narrowest thickness in the hob-cut root (3.303 mm on the default gear;
  on a tangent join equal to the involute's own thickness at the junction, checked through
  `Profile.half_angle`), printed wherever the trochoid applies and null elsewhere. The name is the
  human's (`name-root_waist`, 19-02) and is a published key on `/api/info` and `spur info` from its
  first release. It is warned below `ROOT_WAIST_FLOOR` = 0.4 mm, absolute, and never refused (D-06);
  `tooth severed` (waist at or under zero) stays a refusal. The floor is the human's (`floor-print`,
  `take the recommendations`, 2026-10-09) and a printability choice, because D-07's walk found no
  failure signature: 1,098 gears (37 `tooth severed`), all 1,061 trochoid gears built one valid solid,
  worst oracle reading 6.8995e-5 mm, thinnest built waist 3.2325e-3 mm. The floor is 124x that
  waist and warns on 294 of 1,061 walk gears and 771 of 10,326 product gears. Small-module caveat,
  adopted with the counts in front of the human: 595 of the 616 module-0.2 gears warn, 195 of them on
  tangent joins with no undercut at all, against 176 of 9,710 at module 1 and above, so the sentence
  never uses the word undercut ("Waist walk (19-02, D-07)", "Bars adopted (19-02)").
- The cap sentence names `root_fillet` and says the printed radius is within 0.001 mm of the largest
  that keeps the cutter a tip land (0.471 silent, 0.472 trimmed to 0.471 with the sentence, 0.4715
  used as given, at module 1, 20 degrees, backlash 0, 19-06).

**The interfaces** (19-04, 19-07, 19-08). The field walk exempts every `Literal` field read from the
model (`get_origin(annotation) is Literal`) and pins the exemption equal to `[root_shape, recess_sides]`.
Four trochoid documents (default, 17-tooth undercut, 42-tooth nothing-radial, 12-tooth capped) print
byte-identical on `spur info` and `/api/info`. Seven spellings of an unknown `root_shape` (`false`,
`Trochoid`, `TROCHOID`, `hob`, empty, leading and trailing space) are refused on both front ends. The
composition matrix gained a root axis: 192 calc-tier rows and 24 kernel-tier rows, every trochoid row reading
its radial twin's pinned deltas, with no delta, bar or oracle position count moved (19-08, `2be041e` and
`6607f69`). **The refusal routing the human chose at 19-07** (`exit-documented`, 2026-10-09): "keep the
CLI contract as shipped; ROADMAP SC5's 'exit 2' is read as the parameter refusals; a root guard's
BuildError exits 1 with its sentence (D-14, cli.md 'Errors')" (`19-07-SUMMARY.md`, `63cc041`). An
unknown `root_shape` is a `422` with a `loc` naming it on the API and argparse exit 2 on the CLI. A root
guard's `BuildError` is a `422` of type `build_error` carrying its "modelling defect ... root_shape"
sentence, and `error: <the same sentence>` with exit 1 on the CLI. SC5's sentence therefore stays
literally false for the guard, which was that option's stated cost; `cli.py`, `docs/architecture/cli.md` and
ROADMAP's SC5 text were not edited, and this is where the reading is written down.

**The price** (SC4; 19-01, 19-09). *The heaviest row a trochoid request can change*: the 116-tooth,
module-1.75 gear with a 156.3 mm hex bore, 60 holes of 1 mm on a 183.4 mm circle, the tip chamfer at 1.75
and both recesses, at 14.5 degrees and profile shift -0.6 (the corner where `rb > rf` still holds). It
reads **14.64 s of 30 s** with the hob root (14.28 s build plus the slower export, the fine STL, 0.36 s),
15.36 s of margin; its radial twin reads 9.50 s, 1.54 times, the largest of the 17 pairs (the other 16
read 0.98 to 1.19); the heaviest radial request in the sweep reads 11.33 s; 19-01's spike read the same
row at 16.61 s. All 34 requests are inside `SPUR_BUILD_TIMEOUT` (19-09, `4b08aa8`, `make bench.build
SWEEP=bench/sweeps/trochoid.json`; "Composed build time on the real build (19-09)", 1-minute load 3.3 to 7.7,
so each figure is an upper bound for this host). This answers L37's "Revisit when Phase 19's composed
re-measure": L37's 29.42 s row is the 200-tooth composition, where a trochoid request is ignored and
warned (the trochoid applies only below 116.1 teeth), so it was not re-run and stands. The 503-under-load
contract, `SPUR_BUILD_TIMEOUT` = 30 s and `spoke_count`'s `le` of 32 are unchanged.

*The gate* (`bench/RESULTS.md` "Gate baseline (19-01)", "The gate, priced (19-09)"). Both readings are on
one host, an Apple M5 Max with 18 CPUs; **L34's 66 s bar was set on an Apple M2 Max with 12 CPUs**
(63.555 s read there), so the bar is quoted as written and no figure here is scaled between the two. At
the phase base the mean of three green `make verify` runs was 52.89 s (`real`, 1023 tests, 19-01,
`7a0268f`). At the phase's end three runs read 208.52, 161.71 and 208.60 s (`1210 passed` each), mean
**192.94 s**: 2.92 times L34's 66 s, 126.94 s over, and **+140.05 s on the same host against 19-01's
52.89 s**, with 187 more tests. The loads were 4 to 9 and rose with each run's own eight workers, so these
are upper bounds for an idle host; a fourth reading after Task 2, not in the mean, was `1210
passed in 166.25s`. The cost came in by wave (`make test` walls on this host: 112.79 s at 1054 tests after 19-04,
137.76 s at 1081 after 19-06, 206.05 s at 1209 after 19-07). 21 of the 25 slowest calls are this
phase's kernel-tier tests in `tests/test_model.py`, 305.5 s of the run's 1,664 worker-seconds (18.4 %), a
lower bound for the phase's share; the oracle's 401 positions per row (19-02) set their cost.
`make verify.fast` read 11.39 to 11.54 s at 824 tests, inside L36's 30 s kill (L36 read 11.28 s on the
M2 Max). `derive()` costs 10.3 usec per call for the default gear and 30 usec with `root_shape="trochoid"`
(load 2.55 to 2.67, best of 5; 10.2 and 29.8 usec at a load near 5), because the hob root solves the curve
once. **The human accepted the gate's cost** (`accept-A`, 2026-10-09, at 19-09's step-2 gate, in the
precedent of Phase 12 D-10 recorded in L31, whose verbatim answer was "accept"): the measured cost stands,
no kernel row moved out of the gate, **L34's 66 s bar and the 401-position oracle count are unchanged**.
That leaves 66 s on paper while the gate reads about 193 s on this host; re-setting the bar from an
idle-host reading, or a measured revisit of the per-row position count, is a separate decision that this
entry does not make. The known resource-tracker flake (`ReentrantCallError`) was re-deferred at 19-03
with 60 isolation loops that did not reproduce it (`0f7c375`); no run of 19-04 to 19-09 hit it.

**Reversibility.** D-01 is **costly**: a later separate tip-radius field must keep reading `root_fillet`
for every shared link that set it under the trochoid, because those links already mean a hob radius.
D-02 is **one-way**: `root_shape` is in every shareable link and CLI flag from the first release that
ships it. D-08 is **reversible**: the flip is deferred, so running it later is exactly one commit under its
own `Lxx` and nothing recorded here has to be undone. The bars, `ROOT_ARC_MIN` and the waist floor are
constants beside their measurements and move by a new entry with a new measurement; the field name
`root_waist` and the `root_form_d` key cannot be renamed without keeping the old key.

Reason: no default moved (L05), and every number printed beside the hob root is proved against an
independent oracle, or null, or warned (L08); every bar sits 10x or more over the worst reading it rests
on, and where one sat under 10x it went to the human instead of being tuned toward a pass. The
choice was between flipping the default for everyone and offering the hob root to those who ask; the
price (14.64 s of 30 s on the heaviest row it can change, a gate that reads 2.92 times its bar) was
measured and accepted rather than trimmed or hidden.
Machine: 18 CPUs, Apple M5 Max, 64 GiB RAM (`sysctl -n hw.ncpu machdep.cpu.brand_string hw.memsize`);
macOS 27.0.1 (`sw_vers -productVersion`), Darwin kernel 27.0.0 (`uname -r`); Python 3.12.15, cadquery 2.8.0,
cadquery-ocp 7.9.3.1.1 (`importlib.metadata.version`); the gate baseline and the heaviest-row spike were read on
2026-10-08 (19-01), the other spikes, guards, floor and bars on 2026-10-08 and 2026-10-09 (19-02), the corner
rows, the gate's three runs and the `derive()` timings on 2026-10-09 (19-09). L34's bar and L36's 11.28 s were
read on a 12-CPU Apple M2 Max.
