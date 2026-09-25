# Phase 3: Structured Logging at the Composition Boundary - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-24
**Phase:** 3-Structured Logging at the Composition Boundary
**Areas discussed:** Format & library, Config point & emitting process, Record vocabulary, Levels & the proof

---

## Format & library

### What produces the structured records?

| Option | Description | Selected |
|--------|-------------|----------|
| stdlib logging + own JSON formatter | No new dependency; L12 closure untouched; ~30-line Formatter; ruff LOG/G already police call sites; caplog captures natively | ✓ |
| structlog | Bound context and processors; new pinned package, image rebuild, stdlib bridging for uvicorn | |
| logfmt text via stdlib | Greppable; "structured" becomes a convention with no parser | |

### What happens to uvicorn's own plain-text access/error lines?

| Option | Description | Selected |
|--------|-------------|----------|
| Same JSON handler, one stream | Root handler + `log_config=None`; uvicorn records come out as JSON; access log kept | ✓ |
| Leave uvicorn untouched | Two formats in one stream | |
| Drop the access log, JSON for the rest | `/api/info`, `/api/schema`, `/api/health`, 422s leave no trace | |

### What does `make serve` show on a dev terminal?

| Option | Description | Selected |
|--------|-------------|----------|
| JSON always | One formatter, one code path; `make serve 2>&1 \| jq` | ✓ |
| SPUR_LOG_FORMAT=json\|text knob | Second renderer to keep in sync | |
| Auto-detect a TTY | Piped vs terminal behave differently | |

### Which stream carries the JSON lines?

| Option | Description | Selected |
|--------|-------------|----------|
| stderr | Matches cli.py's stdout-is-product / stderr-is-diagnostics; docker captures both | ✓ |
| stdout | 12-factor convention; a second convention in one codebase | |
| Keep uvicorn's split | Two handlers, reader merges by timestamp | |

**User's choice:** all four recommended options.
**Notes:** none.

---

## Config point & emitting process

### Where does the one call that configures the root logger live?

| Option | Description | Selected |
|--------|-------------|----------|
| cli.cmd_serve, before uvicorn.run | The literal composition root; smoke.py / bare uvicorn / TestClient get lastResort. ASSUMPTION to verify: SPUR_WORKERS>1 children inherit | ✓ |
| cmd_serve + idempotent call in app lifespan | Covers every entry; two call sites, idempotence to test | |
| app.py lifespan only | uvicorn's pre-lifespan lines miss it; boundary moves one layer in | |

### Which process records build started / build failed?

| Option | Description | Selected |
|--------|-------------|----------|
| The parent, around the pool call | Existing except branches see BuildError/BuildTimeout/BrokenProcessPool + slot; workers silent; CLI export emits nothing | ✓ |
| The worker, in model.py | Raw OCCT class; second config point in `_warm()`; N writers; CLI export emits | |
| Both | Most information, most surface; each build appears twice | |

### Do `spur info` / `spur export` configure the JSON logger too?

| Option | Description | Selected |
|--------|-------------|----------|
| No — only `serve` | No branches exist on the CLI (L04); stderr prose stays; lastResort covers stray WARNING+ | ✓ |
| Yes — every command | JSON interleaved with human prose for commands that emit no records | |

### How do Phase 2's timeout / broken-pool / worker-replaced paths map onto "build failed"?

| Option | Description | Selected |
|--------|-------------|----------|
| Timeout/broken are build.failed kinds; worker.replaced its own record | Exception class on build.failed; /api/health only has a count, the log carries the when | ✓ |
| Timeout/broken are build.failed kinds; nothing for replacement | Inferable from a failure on the same slot | |
| Strictly the four | Timeout and broken pool unrecorded — the 503s incidents are about | |

**User's choice:** all four recommended options.
**Notes:** none.

---

## Record vocabulary

### How is the gear identified in a record?

| Option | Description | Selected |
|--------|-------------|----------|
| slug + non-default params object | `model_dump(exclude_defaults=True)` — the shareable-link form L05 keeps stable; reproducible | ✓ |
| slug + stable content hash | Short, joinable, not reproducible; `hash(p)` is per-process salted | |
| slug only | Ambiguous beyond teeth/module/pressure angle | |

### "Export served from cache vs built" — one event or two?

| Option | Description | Selected |
|--------|-------------|----------|
| One event, `source` with three values | `export.served`, `source: cache \| compressed \| built`, each an existing path in app.model() | ✓ |
| Two events; fold compressed into cache | The compress-under-a-slot path disappears | |
| Three events | Three names for one field's distinction | |

### Does export.served carry the slot duration?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — duration_ms on served and failed | One monotonic clock in the parent around the slot; zero on a cache hit is evidence | ✓ |
| No — strictly the four branches | Reader subtracts timestamps after joining | |

### How do one request's records find each other?

| Option | Description | Selected |
|--------|-------------|----------|
| Per-request id generated in the endpoint | uuid4 hex[:8], a local; not middleware/contextvars/header | ✓ |
| No id — join on params + fmt + quality + time | Fails for two concurrent identical requests | |
| Honour incoming X-Request-ID | Proxy integration — scope creep, deferred | |

**User's choice:** all four recommended options.
**Notes:** none.

---

## Levels & the proof

### Default level and knob?

| Option | Description | Selected |
|--------|-------------|----------|
| INFO default, SPUR_LOG_LEVEL knob | Branches visible out of the box; deployer sets WARNING; nonsense falls back to INFO | ✓ |
| INFO, no knob | Quieting needs a code change | |
| WARNING default, knob to raise | Two of four branches invisible by default | |

### Which level does each branch get?

| Option | Description | Selected |
|--------|-------------|----------|
| Split by whose fault it is | started/served INFO; BuildError WARNING; Timeout/BrokenPool/worker.replaced ERROR; queue.refused WARNING | ✓ |
| Every failure is ERROR | ERROR stops meaning "service broken" | |
| Everything INFO; filter on event | Makes the level knob useless | |

### What does the proving test assert?

| Option | Description | Selected |
|--------|-------------|----------|
| caplog per branch + one formatter round-trip | Branches driven via TestClient + injected backend and the existing wedge test; literal names asserted; formatter proven once | ✓ |
| Parse emitted JSON in every branch test | Handler setup per test; couples every test to the formatter | |
| caplog only | A formatter dropping `extra` would pass | |

### Where do event/field names live?

| Option | Description | Selected |
|--------|-------------|----------|
| One kernel-free module with a function per event | Field sets are mypy-checked signatures; tests assert literal strings; module not named `spur/logging.py` | ✓ |
| Name constants; `extra=` at call sites | Names centralised, field sets not | |
| String literals at call sites | Drift across five sites | |

**User's choice:** all four recommended options.
**Notes:** none.

---

## Claude's Discretion

- Module name and placement (not `spur/logging.py`).
- Which of `app.py` / `pool.py` calls each helper.
- Remaining field names: exception class on build.failed; slot and cause on worker.replaced; in-flight count and MAX_QUEUED_BUILDS on queue.refused; envelope keys (timestamp, level, logger). Timestamp format. Traceback on ERROR records. Whether `version` rides on every record.
- How `SPUR_LOG_LEVEL` is parsed.
- Sequencing of the docs updates, the `L20` entry and the debt move against the code commits.

## Deferred Ideas

- Honour an incoming `X-Request-ID` header (proxy integration).
- A byte-cache eviction record.
- Worker-side logging (rejected D-06 variant).
- Querying workers from `/api/health` (still deferred from Phase 2).
