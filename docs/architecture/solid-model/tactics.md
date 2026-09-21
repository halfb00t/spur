# solid-model — tactics

## Shape

**Build pipeline**, one decision per step, in `_build(p)`:

```
profile(p) ─▶ _gear_blank ─▶ _cut_face_recesses ─▶ _cut_bore ─▶ one validated Solid
                (outline,       (annulus cut,          (circle or D,
                 extrude)        floor fillets)         rim chamfers)
```

`_outline(pr, fillet)` assembles the closed wire tooth by tooth: a straight or filleted
lead-in from the root circle, a B-spline on each involute flank (16 points, biased toward
the tip), a three-point arc across the tip, and an arc along the root to the next tooth.
Root fillet arcs come from `_fillet_corner()`, which solves the tangency directly.

**Edge re-selection** is separated out on purpose: `_groove_floor_edges()` matches
circles by radius and z; `_bore_rim_edges()` matches by position, sampling three interior
points, because a D-bore rim is not one geometric type.

**Caching and export**: `build()` and `export()` both take `_LOCK`, then go through
`_build_cached` (an `lru_cache` on the parameter object) and `_EXPORTS` (an LRU bounded by
total bytes). `_BlobCache` needs no lock of its own — every caller already holds `_LOCK`,
and that is written down where it is defined.

## Contracts

**In:** `GearParams`, plus the effective fillets and radii it reads from `calc.py`.

**Out:**
- `build(p) -> cq.Solid` — used only by the tests. A CadQuery object crossing this line
  is a deliberate test affordance, not a public contract.
- `export(p, fmt, quality) -> bytes` — what `app.py` and `cli.py` use.
- `BuildError` — the only exception that leaves. `_build_checked()` wraps the assorted
  `Standard_Failure` subclasses OCCT raises into it with an actionable message.

**Invariant, checked rather than assumed:** `_build()` asserts exactly one solid and that
it is valid before returning. This is also why the module can annotate intermediates
loosely where CadQuery's own signatures return a wide `Shape` — the narrow type is
re-established at the end, not hoped for.

**Configuration:** `SPUR_SOLID_CACHE` (entries, default 4) and `SPUR_EXPORT_CACHE_MB`
(megabytes, default 64), both read through `int_env()`, both per worker process.
