# solid-model — implementation

## Layout

`src/spur/model.py` — ~320 lines, four bands separated by comment rules.

| Band | Functions | Note |
|---|---|---|
| kernel housekeeping | `_load_malloc_trim`, `_release_arenas`, `_LOCK` | `malloc_trim` is glibc-only; on macOS and musl it resolves to `None` and does nothing |
| 2D outline | `_polar`, `_fillet_corner`, `_outline` | pure vector maths on `cq.Vector`; no booleans yet |
| the part | `_gear_blank`, `_cut_face_recesses`, `_cut_bore` | one product decision each |
| picking geometry back out | `_ring`, `_groove_floor_edges`, `_bore_rim_edges` | the fragile predicates, isolated |
| build and export | `_build`, `_build_checked`, `_build_cached`, `build`, `_BlobCache`, `_EXPORTS`, `_write_export`, `export` | |

Constants: `TESSELLATION` (linear and angular deflection per quality), `FLANK_POINTS = 16`,
`TOL = 1e-6`.

## Entry points

`build(p)` and `export(p, fmt, quality)`. Both acquire `_LOCK` first; nothing else in the
module should be called from outside.

## Things that will bite

- **Export goes through a temp file.** `_write_export()` writes into a
  `TemporaryDirectory` and reads the bytes back, because CadQuery's exporters take a path.
  In the container `/tmp` is a size-capped tmpfs, so a huge STL fails there rather than
  eating the memory limit.
- **`type: ignore` comments are load-bearing and explained.** CadQuery types every boolean
  result as `Shape`, which declares neither `fillet` nor `chamfer` (they live on `Mixin3D`,
  carried by `Solid` and `Compound`). The ignores are narrow, coded, and each says why.
  Re-typing this pipeline properly is tracked in
  `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md`.
- **A single large build stalls the event loop** for a second or two, because OCCT holds
  the GIL. Known, bounded by L04, not fixed — see
  `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md`.
