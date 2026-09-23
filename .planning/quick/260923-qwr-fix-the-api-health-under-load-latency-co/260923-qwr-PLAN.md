---
phase: quick/260923-qwr
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/spur/app.py
  - tests/test_api.py
  - bench/RESULTS.md
autonomous: true
requirements: [REQ-cad-off-event-loop]

estimate:
  tokens: 95000
  raw_tokens: 95000
  tasks: 3
  confidence: low          # gsd estimate-calibration: sample_count 0, factor 1.0 (not applied)

must_haves:
  truths:
    - "The gzip level this app compresses at is an explicit constant chosen from level-1/6/9 numbers measured in this run on the real ~9 MB teeth=199 quality=fine STL, and the comment beside it carries that table."
    - "A model body is compressed at most once per (gear, format, quality) cache fill: a repeat download of an already-compressed gear performs zero compression."
    - "Every compression this app performs for a model body happens while holding a _build_slot() admission slot, so at most MAX_QUEUED_BUILDS run concurrently."
    - "A gzip-accepting client gets Content-Encoding: gzip and, once decoded, bytes identical to what an Accept-Encoding: identity client gets for the same gear."
    - "bench/RESULTS.md records Runs 5-6 with a per-run environment snapshot and an explicit Met / Not met line per scenario, as measured."
    - "make verify is green at every commit."
  artifacts:
    - src/spur/app.py
    - tests/test_api.py
    - bench/RESULTS.md
  key_links:
    - "_EXPORTS cache key carries the content encoding, so gzip bytes can never be served to an identity client (or vice versa)."
    - "The compression call sits inside `with _build_slot():` — outside it, the bound is a no-op (see <hard_fact_2> below)."
    - "Setting Content-Encoding: gzip on the Response is what makes GZipMiddleware pass the body through instead of compressing it a second time."
---

<objective>
Fix the real, measured cost behind `/api/health`'s under-load p95 in the `concurrent`
scenario: gzip compression of multi-MB STL bodies at Starlette's default
`compresslevel=9`, unbounded on `_EXPORTS` cache hits.

Purpose: `.planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md` traced
four failing runs (2.02x, 2.45x, 2.32x, 2.35x against a <=2.00x bar) to this mechanism,
and measured it directly: ~1.18 s single-threaded / ~1.35-1.43 s per thread at 10
concurrent for a 9,062,784-byte STL, with cache hits skipping `_build_slot()` entirely
(E2c: 4.33x and 5.52x with the pool never running). Phase 2 is halted at 4/5 until this
is fixed and re-measured on evidence.

Output: a measured `compresslevel` constant, model-body compression moved inside the
admission bound and cached, four behaviour tests, and Runs 5-6 appended to
`bench/RESULTS.md`.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@docs/CODING_VALUES.md
@.planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md
@src/spur/app.py
@tests/test_api.py
@bench/RESULTS.md
</context>

<hard_facts>
Verified this session by reading the installed source and the repo. Cite these; do not
re-derive them, and do not contradict them without new evidence.

<hard_fact_1>
`src/spur/app.py:137` is `app.add_middleware(GZipMiddleware, minimum_size=1024)` —
`compresslevel` is never overridden. Installed Starlette is 1.6.0, whose default is
`compresslevel=9` (`.venv/lib/python3.12/site-packages/starlette/middleware/gzip.py:49`).
</hard_fact_1>

<hard_fact_2>
**Compression happens after the admission slot is released.** `_build_slot()`
(app.py:177-194) wraps only `await backend(params, fmt, q.quality)` (app.py:261-262).
`model()` returns a plain `Response(data, ...)` at app.py:290, and `GZipMiddleware`
compresses the body *after* the endpoint has returned and the slot is gone. So simply
putting the `_EXPORTS` cache-hit branch through `_build_slot()` as it stands today would
bound the endpoint call and **cap nothing** — the compressions would still run unbounded
inside the middleware. The compression call itself has to be inside the slot. A change
that looks like a bound but is a no-op on the actual mechanism is exactly the
plausible-looking record L08 forbids.
</hard_fact_2>

<hard_fact_3>
Starlette 1.6.0 gzip internals, read from the installed source:
- `gzip.py:105-118` — on `http.response.start` the middleware records whether
  `content-encoding` is already in the headers; if it is, the body passes through
  unchanged. A response that already carries `Content-Encoding: gzip` is **not**
  re-compressed.
- `gzip.py:60-78` — when the client's `Accept-Encoding` lacks gzip, an `IdentityResponder`
  is used. An endpoint that pre-encodes must therefore make the same accept test itself
  and serve raw bytes to identity clients.
- `gzip.py:204-208` — bodies >= 128 KiB are already compressed in a worker thread via
  `anyio.to_thread.run_sync`, so the cost is off the event loop but unbounded.
- `gzip.py:29-41` — the limiter on that thread offload is a module-private
  `RunVar("_gzip_capacity_limiter")`. Sizing it would mean writing another module's
  private internals; this codebase explicitly refused to read
  `threading.BoundedSemaphore._value` for that exact reason (app.py:89-95, D-13). Not an
  option here.
</hard_fact_3>

<hard_fact_4>
Import boundaries (`pyproject.toml [tool.importlinter]`): `spur.app` is forbidden only
`cadquery`, `OCP` (direct and indirect) and `tests`. Importing `gzip`, `anyio` and
`starlette.*` in `app.py` is allowed. (`spur.cli` must still not import `spur.app`.)
</hard_fact_4>

<hard_fact_5>
The 9 MB STL can be produced without a server:
`.venv/bin/spur export -o <path>.stl --teeth 199 --quality fine` (the CLI never queues,
L04). The investigation's captured body for `teeth=199&quality=fine` with every other
parameter at its default was **9,062,784 bytes**; if this run produces a different size,
report the size actually measured and use it (L08).
</hard_fact_5>

<hard_fact_6>
Bench convention (`bench/RESULTS.md` "## Latency", Runs 1-4): the host server runs on
`SPUR_PORT=8001`, because port 8000 is held by the long-running `spur-spur-1` container
running the **old** image — benchmarking port 8000 would measure unfixed code.
`make bench.latency` runs `$(PY) -m bench.latency` with no argument passthrough and
`bench/latency.py` defaults to `http://127.0.0.1:8000`, so Runs 1-4 were made with
`.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001`. Each run records:
`docker info` exit, three `sysctl -n vm.loadavg` samples 30 s apart,
`ps -Ao %cpu,comm -r | head -5`, `docker ps --format '{{.Names}} {{.Status}}'`, then the
`single` and `concurrent` tables the harness prints itself, then an explicit Met / Not met
line against "under-load p95 <= 2.00x idle p95".
</hard_fact_6>

<hard_fact_7>
`_EXPORTS` is a `_BlobCache` (app.py:40-73): an LRU of bytes bounded by a total byte
budget (`SPUR_EXPORT_CACHE_MB`, default 64 MB), lock-free because only the event-loop
thread touches it (D-01). `MAX_QUEUED_BUILDS` = `2 * SPUR_BUILD_WORKERS` = 4 by default
(D-09). `/api/health` reports `queue_available = MAX_QUEUED_BUILDS - _in_flight_builds`
(D-13).
</hard_fact_7>

<hard_fact_8>
httpx (and therefore `TestClient`) sends `Accept-Encoding: gzip, deflate` by default and
decompresses transparently, so existing tests reading `r.content` keep working. Identity
behaviour must be exercised with an explicit `Accept-Encoding: identity` header.
</hard_fact_8>

<hard_fact_9>
`docker/smoke.py` drives the ASGI app with a hand-built scope whose only header is
`host` — no `Accept-Encoding` — so it takes the identity path and its `len(stl) > 1000`
and `step.startswith(b"ISO-10303-21;")` assertions are unaffected by this change. It runs
without Docker: `.venv/bin/python docker/smoke.py`.
</hard_fact_9>

<hard_fact_10>
The broken-windows ledger is `.planning/WINDOWS.md`, item 1. **The orchestrator flips it
after this plan returns, on the evidence in the SUMMARY.** Do not run
`gsd-tools windows fixed 1` and do not edit `.planning/WINDOWS.md`.
</hard_fact_10>
</hard_facts>

<chosen_design>
**Compress inside the admission slot, cache the compressed bytes** (the orchestrator's
design A). In `model()`, gzip encoding for model bodies moves out of `GZipMiddleware` and
into the endpoint, performed in a worker thread while the `_build_slot()` admission slot
is still held, with the result stored in `_EXPORTS` under an encoding-tagged key.

Why this, and not the alternatives:

- It satisfies item (2) literally — "the same admission bound as fresh builds" — with no
  new semaphore, no new env knob whose default would have no measured basis, and no
  reading of another module's private internals (`<hard_fact_3>`, D-13 precedent). A
  compression can only ever happen inside an admitted slot, so at most
  `MAX_QUEUED_BUILDS` run concurrently.
- It satisfies item (3) in the same edit rather than as a third mechanism: the E2c
  scenario (repeat downloads of one popular gear, measured at 4.33x and 5.52x) becomes a
  pure cache hit that compresses **zero** times and takes **no** slot.
- Sizing Starlette's private `_gzip_capacity_limiter` instead (design B) would make
  waiters queue but leave the per-response CPU cost intact, does nothing for item (3), and
  writes another module's private RunVar.
- A separate "encode bound" (design C) is only needed if compression happens outside the
  build slot; it is not, so the extra knob is not added.

Accepted costs, to be stated in the code comments and in the SUMMARY:

1. A slot is held for build **plus first encode**, so `queue_available` in `/api/health`
   now means "slots for build and first encode". The `/api/health` docstring (D-13) and
   `_build_slot`'s docstring and busy message must say so.
2. A first-time request for an already-built gear can now be refused `503 busy`, where
   before a cache hit never was. This is the behaviour item (2) asks for; once the gzip
   bytes are cached, repeat downloads take no slot at all.
3. `_EXPORTS` now holds both encodings of a hot gear inside the same 64 MB budget
   (roughly 9 MB raw + ~2.4 MB gzip per fine gear), so it holds fewer distinct gears. The
   budget is still enforced by `_BlobCache`; the default is **not** changed here — that
   would be an unmeasured knob change.
4. Holding the slot across the encode may change the `Refused` counts the bench prints.
   If it does, say so in the Runs 5-6 text rather than leaving it unexplained.
</chosen_design>

<assumption_delta_decision>
Advisory checkpoint (`workflow.assumption_delta`). No ROADMAP phase section exists for a
quick task, so the scripted detector is `skipped` per its own rules; the transition is
recorded here by hand because it is real.

- **Signal:** `pluralization` — an exported body had exactly one representation (raw
  bytes); it now has two (raw and gzip).
- **Noun now primary:** *an encoded export* — bytes plus the content encoding they are in.
- **Decision: `promote`.** The `_EXPORTS` key gains the encoding as a component, so every
  encoding is a first-class variant of the same cache, rather than bolting a gzip-only
  sidecar cache alongside a still-primary raw cache. The alternative (add-alongside) would
  make a third encoding — Brotli, say — a second special case instead of another value.
- **Invariant the tests encode:** a body served under encoding E, decoded, equals the body
  served under identity for the same gear (Task 2 test 1). That goes red the moment a
  future change lets one encoding's bytes be served under another's label.
</assumption_delta_decision>

<threat_model>
`workflow.security_enforcement` active; ASVS level 1; block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| HTTP client -> `/api/model.{fmt}` | Untrusted query parameters and `Accept-Encoding` cross here. Parameters are validated once at the `GearParams` boundary (CLAUDE.md); `Accept-Encoding` is newly read by the endpoint in this change. |
| `_EXPORTS` cache -> response body | Bytes produced for one key are served for another request that maps to that key. The key is the whole trust argument. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-QWR-01 | Denial of Service | `model()` cache-hit path + `GZipMiddleware` | high | mitigate | The defect being fixed: unbounded concurrent ~1.2-1.4 s compressions on `_EXPORTS` hits. Task 2 moves the compression inside `_build_slot()` (capped at `MAX_QUEUED_BUILDS`) and caches the result so repeat downloads compress zero times. Proven by Task 2 tests 3 and 4, and re-measured in Task 3. |
| T-QWR-02 | Denial of Service | `_BlobCache` byte budget | low | accept | Caching both encodings raises bytes held per hot gear. Bounded: `_BlobCache.put` refuses any blob over budget and evicts LRU until the total fits (`test_the_export_cache_refuses_a_blob_bigger_than_its_budget` already covers the refusal). `SPUR_EXPORT_CACHE_MB` stays at its shipped default; the cost is documented, not silently absorbed. |
| T-QWR-03 | Tampering | `_EXPORTS` cache key | medium | mitigate | Serving gzip bytes to a client that asked for identity (or one gear's bytes for another) would be silent corruption of a file someone cuts metal from. Mitigated by putting the encoding in the cache key and by Task 2 test 1, which asserts the decoded gzip body is byte-for-byte the identity body. |
| T-QWR-04 | Information Disclosure | compressed response bodies | low | accept | Compression side channels (BREACH-shaped) need a secret reflected into a compressed response alongside attacker-controlled input. This service has no authentication, no cookies and no per-user secrets (tracked separately in `docs/tech_debt/active/2026-09-21-no-authentication.md`); the bodies are public geometry the caller just specified. Nothing new is exposed — Starlette already gzips these bodies today. |
| T-QWR-SC | Tampering | package-manager installs | low | accept | No package is installed by this plan. `gzip`/`zlib` are stdlib; `starlette` and `anyio` are already pinned transitives of `fastapi`. The Package Legitimacy Gate therefore does not apply and no RESEARCH.md audit table is required. If any task turns out to need a new dependency, stop and ask (CLAUDE.md "Stop and ask first") rather than installing it under this plan. |

No threat is at or above the `high` blocking threshold **unmitigated**: T-QWR-01 is high and
is the thing this plan mitigates.
</threat_model>

<source_audit>
A quick task has no ROADMAP phase section, no phase REQUIREMENTS ids, no RESEARCH.md and
no CONTEXT.md decisions; the source artifact is the task description plus the investigation
it acts on. `api-coverage` and `schema-gate` both resolve to `skipped` (no phase section;
no external API integrated — the change is to this project's own FastAPI app and to
already-vendored Starlette middleware; no ORM/schema files touched).

| Source item | Covered by | Status |
|---|---|---|
| (1) measure compresslevel 1/6/9 on the 9 MB STL; set it in `src/spur/app.py` from those numbers, comment carrying them | Task 1 | COVERED |
| (2) route `_EXPORTS` cache hits through the same admission bound as fresh builds, so concurrent compressions are capped, with a test | Task 2 (compression inside `_build_slot()`; tests 3 and 4) | COVERED |
| (3) cache the compressed bytes only if it stays simple | Task 2 (same key family, one extra tuple component, one extra `put`; test 2) | COVERED |
| `make serve` + `make bench.latency` twice; append Runs 5-6 to `bench/RESULTS.md` | Task 3 | COVERED |
| Report both concurrent ratios; mark WINDOWS item 1 only on <=2x on both runs | Task 3 `<done>` reports them verbatim; the orchestrator flips the ledger (`<hard_fact_10>`) | COVERED |
| `make verify` green throughout | Every task's `<verify>` | COVERED |
| RESEARCH.md / CONTEXT.md D-XX items | — | N/A (none exist for a quick task) |

No item is MISSING and nothing is deferred. If any part turns out not to fit, do not
silently drop it: file it under `docs/tech_debt/active/` (or `docs/ideas/`) from that
directory's `TEMPLATE.md` with its `INDEX.md` row in the same commit, per CLAUDE.md
"Capturing ideas and debt", and say so in the SUMMARY.
</source_audit>

<tasks>

<task type="auto">
  <name>Task 1: Measure gzip levels 1, 6 and 9 on the real 9 MB STL and set the level from the numbers</name>
  <files>src/spur/app.py</files>
  <precondition>A `.venv` belonging to **this** checkout exists and `import spur` resolves into it. If this plan is executing in a git worktree, run `make venv` inside the worktree first — the Makefile's own `worktree.new` target warns that sharing the main `.venv` makes its editable install resolve `import spur` back to the main checkout, so every check would silently exercise unmodified code. `make venv` is ~1.4 GB and takes minutes; it must finish before anything else. Confirm with `.venv/bin/python -c "import spur, pathlib; print(pathlib.Path(spur.__file__).resolve())"` and check the path is inside the checkout under test.</precondition>
  <read_first>
    - `src/spur/app.py` lines 105-140 — `lifespan`'s `SPUR_BUILD_TIMEOUT` comment (lines 115-122) is the house style to match: the number, and the measurement that forced it.
    - `.planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md`, the `gzip_bench.py` paragraph under "## Results" — the prior level-9 figures (1181.7 ms single-threaded, 2,404,371 bytes = 26.5%, 10-concurrent wall 1432.5 ms, under loadavg 5.68) exist as a cross-check on this run's level-9 row, not as a substitute for measuring it.
    - `docs/CODING_VALUES.md` "Code values" — comments carry the measurement or constraint that forced the choice.
  </read_first>
  <action>
Produce the corpus, measure it, then set one constant from what you measured. Nothing in
this task may be filled in from the investigation's numbers or from general knowledge
about zlib — every figure that lands in the comment is one this run produced.

**Step A — produce the body.** `.venv/bin/spur export -o $SCRATCH/big199.stl --teeth 199
--quality fine` into the session scratchpad (never into the repo). Record the exact byte
size. Compare it with the 9,062,784 bytes recorded in `<hard_fact_5>`; if it differs, use
and report the size you measured and note the discrepancy.

**Step B — record the host.** Immediately before measuring, capture `sysctl -n vm.loadavg`
and `ps -Ao %cpu,comm -r | head -5`. These go into the comment as the L08 caveat, exactly
as `bench/RESULTS.md` and the investigation do it. A clean-looking number from a busy
machine is the plausible-but-unmeasured number L08 forbids.

**Step C — measure.** Write a throwaway script in the scratchpad (do not commit it; the
prior session's `gzip_bench.py` under the earlier scratchpad path may be adapted). For each
of levels 1, 6 and 9, measure the function the shipped code will actually call —
`gzip.compress(data, compresslevel=LEVEL)`, not `zlib.compressobj` — so the number in the
comment describes the code under it:
  - single-threaded: at least 5 repetitions; record both the minimum and the median wall
    time in milliseconds, and state in the comment that the median is the figure the
    decision used;
  - output size in bytes and as a percentage of the input;
  - 10-concurrent: the same compression run 10 times through
    `ThreadPoolExecutor(max_workers=10)`; record the wall clock for all ten. Repeat
    this at least 3 times per level and use the median wall clock — the selection
    rule in step D keys on this figure, so a single noisy sample must not decide it.
Cross-check the level-9 row against the investigation's figures from `<read_first>`; if
this run's level-9 number is wildly different, say so rather than papering over it.

**Step D — choose, by a rule stated up front, not by taste.** The cost that matters is the
10-concurrent wall time, because that is what competes with the event-loop thread for CPU
cores; the benefit that matters is transferred bytes. Apply in order, using the medians:
  1. Start at level 1.
  2. Adopt level 6 instead only if level 6's output is at least 10% smaller than level 1's
     **and** level 6's 10-concurrent wall time is no more than 1.5x level 1's.
  3. From whatever step 2 left standing, adopt level 9 only if level 9's output is at
     least 10% smaller than that level's **and** its 10-concurrent wall time is no more
     than 1.5x that level's.
If the measured numbers make the rule ambiguous (a near-tie on either axis), stop and ask
with the table in hand rather than bending the rule — CLAUDE.md "Stop and ask first".

**Step E — set it.** Add a module-level `_GZIP_LEVEL: int` to `src/spur/app.py` near the
other module constants, pass it to the middleware as
`app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=_GZIP_LEVEL)`, and
write the comment above the constant in the style of the `SPUR_BUILD_TIMEOUT` comment:
the three-row measured table (level, single-threaded median ms, output bytes, % of input,
10-concurrent wall ms), the input's byte size, the host loadavg and top-CPU sample from
step B, the clause of the step-D rule that selected the level, and a pointer to
`02-LATENCY-INVESTIGATION.md` for why this constant exists at all. One constant, used in
both places — Task 2 reuses it for the endpoint's own compression, so the middleware and
the endpoint can never drift to different levels.

Keep the diff to this: the constant, its comment, and the `add_middleware` line. No
behaviour change yet.

Commit (Conventional Commits, one concern): `perf(app): set the gzip level from measured
compression cost`, body carrying the measured table and the host caveat. End the commit
message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Do not
commit anything under `.planning/` and do not commit the scratch measurement script.
  </action>
  <verify>
    <automated>make verify && .venv/bin/python -c "from spur.app import _GZIP_LEVEL; assert _GZIP_LEVEL in (1, 6, 9), _GZIP_LEVEL; print('gzip level:', _GZIP_LEVEL)"</automated>
  </verify>
  <done>
`make verify` is green. `_GZIP_LEVEL` exists in `src/spur/app.py`, is passed to
`GZipMiddleware`, and holds one of 1, 6 or 9. The comment beside it contains a three-row
table of numbers measured in this run against a real STL whose byte size is stated, the
host loadavg/top-CPU sample taken at measurement time, and the sentence naming which
clause of the selection rule chose the level. Nothing is committed under `.planning/`.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Compress model bodies inside the admission slot and cache the compressed bytes</name>
  <files>src/spur/app.py, tests/test_api.py</files>
  <precondition>Task 1 is committed and `make verify` was green on it: `_GZIP_LEVEL` must already exist, because this task reuses it rather than introducing a second level.</precondition>
  <read_first>
    - `.venv/lib/python3.12/site-packages/starlette/middleware/gzip.py` — read lines 29-41, 49, 60-78 and 100-120 yourself. Two things must come from that file, not from memory: the exact `Accept-Encoding` test the middleware uses to decide a client accepts gzip (the endpoint has to make the *same* test, or endpoint and middleware will disagree about who gets encoded bytes), and the pass-through branch that leaves an already-`Content-Encoding`-bearing response alone.
    - `src/spur/app.py` lines 40-96 (`_BlobCache`, `_EXPORTS`, `_max_queued_builds`, the D-13 counter comment), 177-194 (`_build_slot`), 202-236 (`health`) and 252-294 (`model`).
    - `tests/test_api.py` lines 1-35 (module-level `TestClient(app)`, the autouse inline-backend fixture) and 113-180 (`test_a_saturated_service_refuses_instead_of_queueing` — the slot-holding idiom this task's tests reuse; `test_a_second_identical_download_is_served_from_the_byte_cache` — the counting-backend idiom).
    - `tests/test_pool.py` lines 228-256 — the `_never_called` backend + held-slots assertion, which must keep passing.
  </read_first>
  <behavior>
Write these four tests in `tests/test_api.py` before the endpoint change, in the module's
existing behavioural naming style (a sentence about what the service does, not about what
the code contains). They describe behaviour at the HTTP boundary, not internals. Use
`quality=preview` and teeth values no other test in the suite uses — 31, 32 and 33 are
free (`tests/test_api.py` uses 21/22/24, `tests/test_pool.py` uses 21/43, `bench/` uses
190-200) — because `_EXPORTS` is a module global shared across the whole session.

  1. **A gzip client gets compressed bytes; an identity client gets the raw file.**
     One gear (teeth 31). Request it with the default client (httpx sends
     `Accept-Encoding: gzip, deflate` and decodes transparently, `<hard_fact_8>`): the
     response carries `content-encoding: gzip` and `vary: accept-encoding`. Request the
     same gear with `headers={"Accept-Encoding": "identity"}`: no `content-encoding`
     header, and the body starts as an STL does. Assert the decoded gzip body equals the
     identity body **byte for byte** — this is the invariant that stops one encoding's
     bytes ever being served under another's label (T-QWR-03).
  2. **A gear is compressed once per cache fill, not once per download.**
     `monkeypatch.setattr` the module-level compression helper with a wrapper that counts
     calls and delegates to the original. Two gzip-accepting requests for the same gear
     (teeth 32) both return 200 with equal content, and the counter is 1.
  3. **A cache hit that still needs compressing goes through admission control.**
     Warm only the raw bytes: one request for teeth 33 with
     `headers={"Accept-Encoding": "identity"}`. Then hold every slot the way
     `test_a_saturated_service_refuses_instead_of_queueing` does
     (`BUILD_QUEUE.acquire(blocking=False)` x `MAX_QUEUED_BUILDS`, released in `finally`)
     and issue a gzip-accepting request for the same gear: `503`, `retry-after: 5`,
     `detail[0]["type"] == "busy"`. The gear is already built, so the only thing that can
     refuse this request is the compression sitting inside the slot — which is precisely
     the property item (2) asks for, and the property `<hard_fact_2>` says a naive
     implementation would fail to deliver.
  4. **An already-compressed download needs no slot at all.**
     Same gear as test 3, now with its gzip bytes cached (issue one ordinary request
     first, slots free). Then hold every slot again and repeat the request: `200`. This is
     the E2c scenario (measured at 4.33x and 5.52x) becoming free, and it is what stops
     this fix from being "every download is now throttled".

No test asserts on private state beyond the two seams the module already exposes for
testing (`BUILD_QUEUE`/`MAX_QUEUED_BUILDS`, used by the existing tests, and the
compression helper). Test 2 monkeypatches the helper only to count calls — it does not
change what the code does.
  </behavior>
  <action>
Make the tests above pass by moving model-body gzip encoding out of `GZipMiddleware` and
into `model()`, inside the admission slot, with the result cached.

**The seam.** Add a module-level `_gzip(data: bytes) -> bytes` to `src/spur/app.py`
returning `gzip.compress(data, compresslevel=_GZIP_LEVEL)` — a named module-level
function, not an inline call, so test 2 can substitute a counting wrapper the same way the
existing tests substitute `build_backend`. Do not pass `mtime=`: the tests compare decoded
bodies, not gzip bytes, so a fixed header timestamp buys nothing here.

**The key.** Extend the `_EXPORTS` key from `(params, fmt, q.quality)` to
`(params, fmt, q.quality, <encoding>)` where the fourth component distinguishes the raw
bytes from the gzip bytes. Both encodings live in the one cache under the one byte budget,
so the budget stays honest; `_BlobCache` itself needs no change. Update its docstring (or
the `_EXPORTS` line) to name the new key shape and the accepted cost from
`<chosen_design>` item 3 — the cache now holds two encodings of a hot gear, so it holds
fewer distinct gears within the same default 64 MB.

**The endpoint.** Give `model()` a `Request` parameter (`from fastapi import Request`) and
decide `wants_gzip` from its `Accept-Encoding` header using the same test the installed
middleware makes (read it, per `<read_first>` — do not invent one). Then:
  - Look up the key for the encoding this client will actually receive. On a hit, return
    it immediately, taking **no** slot. This is the steady-state repeat-download path and
    it must stay free.
  - On a miss, enter `with _build_slot():` and do everything inside it: look up the raw
    key; if that is absent too, `await backend(params, fmt, q.quality)` and store the raw
    bytes; then, when the client accepts gzip, compress with
    `await run_in_threadpool(_gzip, raw)` (`from starlette.concurrency import
    run_in_threadpool`, permitted by `<hard_fact_4>`) and store the result under the gzip
    key. Compressing in a worker thread keeps it off the event loop, as Starlette's own
    middleware already did (`<hard_fact_3>`); what is new is that it is now bounded.
  - Keep all four existing `except` clauses (`BuildError` -> 422, `BuildTimeout`,
    `BrokenProcessPool`, and `_build_slot`'s own `HTTPException` propagating) wrapping the
    same region, with their comments intact. `tests/test_pool.py`'s four-`type` assertion
    must keep passing untouched.
  - On the `Response`, always set `Vary: Accept-Encoding`, and set
    `Content-Encoding: gzip` when the body is the compressed variant. That header is what
    makes `GZipMiddleware` pass the body straight through instead of compressing it a
    second time (`<hard_fact_3>`); say so in the comment, citing the file and lines you
    read.
  - Do not add a minimum-size branch mirroring the middleware's `minimum_size=1024`: the
    smallest model body measured in the investigation was 186,884 bytes (E2a, a 6-tooth
    preview gear, the smallest buildable gear there is), so the branch would be dead code.
    Put that measurement in the comment as the reason.

Leave `GZipMiddleware` installed — it still compresses `/api/info`, `/api/schema`, the
index page and the vendored JS bundle, all at the same `_GZIP_LEVEL`.

**The contracts this moves, which must be re-documented in the same commit:**
  - `_build_slot`'s docstring and its busy `msg`: a slot now covers a build *and* the
    first encode of its result, so a request for an already-built gear can be refused.
  - `health()`'s docstring where it explains `queue_available` (D-13): the number now
    means slots for build-and-first-encode.
Both are one-line honesty fixes; a stale docstring here is a published contract lying
about what the number means.

**Comments.** The `why` for this whole change is the measured one, and it belongs in the
code: `GZipMiddleware` compresses after the endpoint has returned and the slot is gone
(`<hard_fact_2>`), so nothing bounded compression on a cache hit — measured at 4.33x and
5.52x under-load ratio with the pool never running (`02-LATENCY-INVESTIGATION.md` E2c),
against a 2.00x bar. Cite the investigation by path.

**Check the identity path end to end** before committing: `.venv/bin/python
docker/smoke.py` (needs no Docker; `<hard_fact_9>` explains why this is the path that
exercises an `Accept-Encoding`-less client). If Docker happens to be available, `make
smoke` runs the same script inside the image, which is what CI does.

Commit: `perf(app): bound and cache model-body compression`, one concern, body naming the
E2c measurement and the two contract changes. End with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Do not commit anything under `.planning/`.
  </action>
  <reversibility rating="reversible">Adds a response header and a cache-key component; reverting is a single `git revert` with no data to migrate and no external state — the published top-level `/api/health` shape is untouched.</reversibility>
  <verify>
    <automated>.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -x -q && .venv/bin/python docker/smoke.py && make verify</automated>
  </verify>
  <done>
`make verify` is green, including the four new tests. A gzip-accepting client gets
`Content-Encoding: gzip` whose decoded body is byte-identical to the identity body; an
identity client gets the raw file with no `Content-Encoding`. A second download of a
cached gear performs zero compressions and acquires zero slots; a first compression of an
already-built gear is refused `503 busy` when all slots are held. `_build_slot`'s and
`health()`'s docstrings state that a slot now covers build plus first encode. `docker/smoke.py`
passes. `tests/test_pool.py` is unmodified and passing.
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-measure with make serve + bench.latency twice and append Runs 5-6 to bench/RESULTS.md</name>
  <files>bench/RESULTS.md</files>
  <precondition>Tasks 1 and 2 are committed and `make verify` is green, so the server started below serves the fixed code. Port 8001 must be free (`lsof -i :8001` empty) and the pre-existing `spur-spur-1` container on port 8000 must be left running and untouched — it runs the old image (`<hard_fact_6>`).</precondition>
  <read_first>
    - `bench/RESULTS.md` lines 1-141, in particular the "### Idle-host re-run (Runs 3-4)" subsection — its environment snapshot, its environment caveat paragraph, its two `#### <scenario> scenario` tables and its Met / Not met lines are the exact format Runs 5-6 must follow.
    - `bench/latency.py` `main()` and `_run_scenario` — `--base-url` is the only knob, `MIN_SAMPLES = 20` is the floor below which it refuses to report a p95.
  </read_first>
  <action>
Measure, then write down what you measured. Not the other way round.

**Start the server from the checkout under test.** `SPUR_PORT=8001 make serve` in the
background, logging to the scratchpad. Then prove three things before measuring anything:
  - `curl -s http://127.0.0.1:8001/api/health` returns 200 with a `pool` object;
  - the serving interpreter is this checkout's: `.venv/bin/python -c "import spur.app as a;
    import pathlib; print(pathlib.Path(a.__file__).resolve()); print(a._GZIP_LEVEL)"`
    prints a path inside the checkout under test and the level Task 1 chose;
  - record `git rev-parse --short HEAD` — that sha goes into `bench/RESULTS.md` as the
    commit under test.
Never run bare `make bench.latency`: it has no argument passthrough and would hit
`http://127.0.0.1:8000`, the stale container running the unfixed image.

**Environment snapshot, before each of the two runs**, exactly as Runs 3-4 recorded it:
`docker info` exit code; three `sysctl -n vm.loadavg` samples 30 s apart with their UTC
timestamps; `ps -Ao %cpu,comm -r | head -5` from the latest sample;
`docker ps --format '{{.Names}} {{.Status}}'`.

**The two runs.** `.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001`,
twice in immediate succession against the **same** server — the convention Runs 1-2 and
Runs 3-4 both used, so the comparison is like for like. That means Run 6 inherits Run 5's
`_EXPORTS` contents, as Run 2 inherited Run 1's; with this fix, Run 6's cached gears also
skip compression entirely, so Run 5 is the cold path and Run 6 is close to the E2c
repeat-download scenario. Say that in the write-up — an unexplained good number is worse
than an explained one. Do not restart the server between runs, do not re-run to search for
a passing number, and report both runs whatever they say (L08; the plan that produced Runs
1-2 recorded a failing bar rather than tuning it, and so does this one).

**Write the section.** Append `### Post-fix re-run (Runs 5-6)` to `bench/RESULTS.md` after
the "### Idle-host re-run (Runs 3-4)" subsection and before `### SPUR_BUILD_TIMEOUT`,
following the Runs 3-4 shape:
  - a lead paragraph naming the commit under test and, in one sentence each, what changed
    (the measured gzip level; model-body compression moved inside the admission slot and
    its output cached) — and the cache-carryover note above;
  - the environment snapshot, and an environment caveat paragraph stating plainly whether
    the host cleared the ">1.5 on a 12-core host" idle bar this file itself names. If it
    did not, say so; the caveat is not a disclaimer, it is part of the measurement;
  - `#### single scenario (Runs 5-6)` and `#### concurrent scenario (Runs 5-6)` tables in
    the file's existing column layout (Run | Idle p95 (n) | Under-load p95 (n) | Ratio |
    Slowest build | Refused), transcribed from what the harness printed;
  - the `Pass bar: under-load p95 <= 2.00x idle p95.` line with **Met** or **Not met** per
    run, per scenario;
  - if the `Refused` counts moved relative to Runs 1-4, one sentence explaining it (a slot
    is now held across build plus first encode, `<chosen_design>` cost 4). If they did not
    move, say nothing about them.
  - a closing sentence stating, in the file's own terms, whether the `concurrent`
    scenario's acceptance clause is now demonstrated on this machine. If either run is
    above 2.00x, that sentence says it is not. Do not edit the Runs 1-4 "**Finding.**"
    paragraph; this subsection is the update.

**Stop the server**: `pkill -f "spur serve"`, then confirm `lsof -i :8001` comes back
empty. Leave `spur-spur-1` running.

**Do not touch `.planning/WINDOWS.md` and do not run any `windows fixed` command**
(`<hard_fact_10>`). Report both `concurrent` ratios verbatim in the SUMMARY; the
orchestrator decides the ledger on that evidence.

Commit: `docs(bench): record the post-fix latency re-run (Runs 5-6)`. End with
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Do not commit
anything under `.planning/`.
  </action>
  <verify>
    <automated>grep -q 'Runs 5-6' bench/RESULTS.md && grep -c 'Pass bar: under-load p95' bench/RESULTS.md && make verify && test -z "$(lsof -ti :8001)"</automated>
  </verify>
  <done>
`bench/RESULTS.md` has a `### Post-fix re-run (Runs 5-6)` subsection naming the commit
under test, carrying a per-run environment snapshot and caveat, both scenario tables, a
Met / Not met line per run per scenario, and a closing sentence on whether the
`concurrent` acceptance clause is demonstrated. Both runs were made against port 8001 on a
server proven to be running the fixed code; nothing is left listening on 8001 and
`spur-spur-1` is untouched. `make verify` is green. `.planning/WINDOWS.md` is unmodified.
The SUMMARY reports both `concurrent` ratios verbatim (Run 5 and Run 6), the `single`
ratios, and the host load figures they were measured under.
  </done>
</task>

</tasks>

<verification>
1. `make verify` green at each of the three commits (a pre-commit hook enforces it with no
   bypass, so this is also self-enforcing).
2. `.venv/bin/python docker/smoke.py` passes — the identity path still returns a usable STL
   and a parseable STEP.
3. `git log --oneline -3` shows three commits, one concern each, none touching
   `.planning/`.
4. `.planning/WINDOWS.md` unmodified: `git status --short .planning/WINDOWS.md` is empty.
5. The comment beside `_GZIP_LEVEL` and the Runs 5-6 section contain only numbers measured
   in this run, each with the host-load conditions it was measured under.
</verification>

<success_criteria>
- `_GZIP_LEVEL` is set from a three-level measurement made in this run against a real STL
  of a stated byte size, and the comment carries that table and the selection rule.
- Every model-body compression happens inside `_build_slot()`; a repeat download of an
  already-compressed gear performs zero compressions and takes zero slots.
- Four new behaviour tests pass, including the two that pin the admission bound (`503` on a
  compression that still has to happen, `200` on one that does not).
- `bench/RESULTS.md` carries Runs 5-6 as measured, with both concurrent ratios and an
  explicit Met / Not met per run.
- The SUMMARY reports both concurrent ratios verbatim so the orchestrator can decide
  WINDOWS item 1 on evidence.
</success_criteria>

<output>
Create `.planning/quick/260923-qwr-fix-the-api-health-under-load-latency-co/260923-qwr-SUMMARY.md`
when done. It must contain, at minimum: the measured gzip table and the level chosen; the
two `concurrent` ratios and the two `single` ratios from Runs 5-6 with the host load they
were measured under; whether the <=2.00x bar was met on **both** runs; any item filed under
`docs/tech_debt/active/` or `docs/ideas/`; and the three commit shas.
</output>
