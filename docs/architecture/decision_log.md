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
`docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`.

**The selector rule** (D-15..D-18). `calc.bore_rim_limit(p)` is the exact geometric
bound per bore shape, no slack — `bore_radius(p)` for round and D-flat bores (the
D-flat rim is the round hole intersected with a rectangle, a strict subset of the
circle), 0.0 with no bore; Phase 8 adds the hex circumradius here rather than widening
the band. `model.BORE_RIM_SLACK` (0.01 mm) is the selection slack, measured at 1e-7 mm
(the kernel's post-boolean vertex and edge tolerance on both bore shapes, 2026-09-26)
and kept three orders of magnitude below that while staying forty times under
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
