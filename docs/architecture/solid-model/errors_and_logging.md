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
- Two raise it themselves, before the kernel can, for a defect that is spur's and not the
  user's: the edge selectors on an empty selection while their feature is on (L26), e.g.
  `_tip_edges`: "Tip chamfer selected no tip-arc edges: a modelling defect in spur, not a
  conflict in these parameters. Set tip_chamfer to 0 to build this gear without it."; and
  the four hob-root guards, which refuse a trochoid outline that is wrong without resting on
  `isValid()`. Each ends with the same sentence, "a modelling defect in spur, not a conflict
  in these parameters. Set root_shape to radial to build this gear with the analytic root.",
  never the "try smaller fillets or chamfers" above. They begin:
  - `_guard_junction`: "The hob root leaves the involute at its junction by {gap} rad (bar
    {ROOT_JUNCTION_BAR_RAD}): "
  - `_guard_spacing`: "The hob root's point spacing is uneven (largest chord {ratio}x the
    smallest, bar {ROOT_SPACING_RATIO_MAX}): "
  - `_guard_annulus`: "A hob-root spline leaves the root-to-tip annulus (radius {r} mm
    outside {rf} to {ra}): "
  - `_guard_area`: "The hob-root outline's area is {miss} off the polygon of its own points
    (bar {ROOT_AREA_REL_MAX}): "
  A kernel exception raised while that outline is being built (an edge constructor, the
  wire or the face) takes the same remedy with "The hob-root outline could not be built
  ({type(exc).__name__}): " in front, only on the trochoid branch (19-REVIEW WR-01).
  An honest curve never trips one (0 failures over the 10,326 trochoid gears of the Phase 18
  product, 19-02), so reading one is a bug report, not a parameter to adjust.
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

None here, **by decision**, not by oversight (`L20`, D-06). The worker process that
actually runs `_build_checked()` configures no handler and emits no record — every
`build.started`/`build.failed`/`export.served` record this project emits comes from the
parent, in `app.py`, around the pool call, where the existing `except BuildError` /
`BuildTimeout` / `BrokenProcessPool` branches already run.

The accepted cost: the kernel's own traceback reaches the parent only as the
`_RemoteTraceback` text `concurrent.futures` ships back inside `BuildError`'s message —
readable by a human, but not available to the parent as a class object the way
`BuildTimeout`/`BrokenProcessPool` are. A `BuildError` means the kernel failed on input
that passed every rule we know how to state (see above) — worth reading as "a rule is
missing," and that reading is exactly why it logs at WARNING, not ERROR, in `app.py`'s
`build.failed` record.
