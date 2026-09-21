# No structured logging anywhere

Severity: must
Status: active
Date: 2026-09-21
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
