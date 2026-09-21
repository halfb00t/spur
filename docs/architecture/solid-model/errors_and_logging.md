# solid-model — errors & logging

## Failure handling

**Fail loud, once, with a usable message.** There is no retry tier here: a kernel failure
is deterministic for a given parameter set, so retrying would only burn seconds.

- `_build()` raises `BuildError` when the result is not exactly one valid solid. This is
  a positive check on the invariant, not an exception handler.
- `_build_checked()` catches everything else OCCT can raise — a family of
  `Standard_Failure` subclasses that share no useful base — and re-raises it as
  `BuildError(f"Geometry kernel failed ({type(exc).__name__}); try smaller fillets or
  chamfers.")`. The original is chained, so the traceback survives.
- `BuildError` is the only exception the module lets out. `app.py` turns it into `422`
  with the message; `cli.py` prints `error: <message>` and exits 2.

Parameters that cannot make a sound part never get this far — `calc.check()` rejects them
at the `GearParams` boundary (L03). A `BuildError` therefore means the kernel failed on
input that passed every rule we know how to state, which is worth reading as a signal
that a rule is missing.

**Memory is a failure mode here, and it is handled by measurement, not by hope.** The
caches are bounded (L07), the arenas are returned after each cache-missing export, and
`compose.yaml` sets `mem_limit: 2g` as the backstop — a number that was measured, after
`1g` failed ~5% of requests under a sweep.

## Logging

None. The module emits no log lines at all.

That is a real gap, not a design choice: a `BuildError`, a cache eviction or a build that
took three seconds are all things you would want to see in production, and today the only
evidence is the HTTP status. Tracked in
`docs/tech_debt/active/2026-09-21-no-structured-logging.md`. Do not add ad-hoc `print()`
calls in the meantime — that is how a logging decision gets made by accident.
