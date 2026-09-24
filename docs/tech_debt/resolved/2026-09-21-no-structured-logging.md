# No structured logging anywhere

Severity: must
Status: resolved
Date: 2026-09-21
Resolved in: 21b8fe4
Source: writing docs/architecture/*/errors_and_logging.md — verified by grep, not assumed
Related files:
- src/spur/app.py
- src/spur/model.py
- docker/smoke.py

## Context

`grep` over `src/` and `docker/` finds no `logging` import and no logger anywhere. The
only evidence a production request leaves is its HTTP status. A `503` from the build
queue, a `BuildError` out of the kernel, a cache eviction, and a build that took three
seconds are all invisible.

`calc.py` legitimately needs none — it is pure, and its `warnings` output is its
diagnostic. The gap is in the serving and building layers.

## Why it matters

The first time something goes wrong in a deployment, there is nothing to read. The
project's own standard is that claims are measured, not estimated; without logs, nothing
about production behaviour can be measured at all.

There is a second-order risk: with no logger configured, the first person who needs
visibility will reach for `print()`, and the logging decision gets made by accident at
the worst moment.

## Next step

Configure a structured logger at the composition boundary (`cli.cmd_serve` /
`app.py` startup), and log the decision branches that already exist: build started with
which parameter slug, build failed with which exception class, export served from cache
or built, queue refused. Redact nothing sensitive because there is nothing sensitive —
but pick the field names once.

Revisit when: the first production incident, or any deploy beyond one person's machine.

## Resolution (2026-09-24)

`Resolved in: 21b8fe4` is Plan 03-02's `worker.replaced` commit
(`feat(03-02): worker.replaced -- one record per incident, inside the guard that already
counts once`) — the last code-changing commit of Phase 3, not the present commit, which
resolves this file and makes the documentation describing it true (per flagged
assumption 1, a file cannot carry its own commit's sha).

`src/spur/records.py` configures one stderr JSON logger at two idempotent call sites
(`cli.cmd_serve` and `app.py`'s `lifespan()` — the second required once
03-RESEARCH.md falsified the single-call-site assumption; see `L20`) and emits all five
branches this file named: `build.started` with the parameter slug, `build.failed` with
the exception class, `export.served` with `source` in `{cache, compressed, built}`,
`queue.refused`, plus `worker.replaced` for the pool-recovery branch Phase 2 added after
this file was written. Each is proven by a `caplog`-based test asserting the literal
event and field names (D-16), plus one formatter round-trip test. `calc.py` stays
log-free, as this file said it should.
