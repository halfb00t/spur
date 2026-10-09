# solid-model — implementation

## Layout

`src/spur/model.py` — ~810 lines, in the bands below, separated by comment rules.

| Band | Functions | Note |
|---|---|---|
| kernel housekeeping | `_load_malloc_trim`, `_release_arenas`, `_LOCK` | `malloc_trim` is glibc-only; on macOS and musl it resolves to `None` and does nothing |
| 2D outline | `_polar`, `_fillet_corner`, `_outline` | pure vector maths on `cq.Vector`; no booleans yet |
| hob-root outline | `_Tooth`, `_trochoid_teeth`, `_trochoid_polygon`, `_trochoid_outline`, `_guard_junction`, `_guard_spacing`, `_guard_annulus`, `_guard_area` | only reached with a `RootCurve` (`root_shape="trochoid"` where `root_mode` answers trochoid); `_outline(pr, fillet, curve)` hands over to `_trochoid_outline` |
| the part | `_gear_blank`, `_cut_face_recesses`, `_cut_bore` | one product decision each; `_gear_blank` also runs `_guard_area` when it has a curve |
| picking geometry back out | `_ring`, `_groove_floor_edges`, `_bore_rim_edges` | the fragile predicates, isolated |
| build and export | `_build`, `_build_checked`, `_build_cached`, `build`, `_BlobCache`, `_EXPORTS`, `_write_export`, `export` | |

Constants: `TESSELLATION` (linear and angular deflection per quality), `FLANK_POINTS = 16`,
`TOL = 1e-6`, and for the hob root `ROOT_ARC_MIN = 2e-6` mm, `ROOT_JUNCTION_BAR_RAD = 1e-11`,
`ROOT_SPACING_RATIO_MAX = 1000.0`, `ROOT_AREA_REL_MAX = 5e-2`. Each carries its measurement,
headroom, host and date in the comment beside it (19-02, `bench/RESULTS.md` "Bars adopted").

## Entry points

`build(p)` and `export(p, fmt, quality)`. Both acquire `_LOCK` first; nothing else in the
module should be called from outside.

## Things that will bite

- **Export goes through a temp file.** `_write_export()` writes into a
  `TemporaryDirectory` and reads the bytes back, because CadQuery's exporters take a path.
  In the container `/tmp` is a size-capped tmpfs, so a huge STL fails there rather than
  eating the memory limit.
- **Vendor shape typing stops at two checked helpers.** CadQuery types every boolean
  result as `Shape` (`Shape.cut -> Shape`), which declares neither `fillet` nor `chamfer`
  (they live on `Mixin3D`, carried by `Solid` and `Compound`), and `Workplane.val()` as a
  four-way union. `_body()` and `_shape_of()` narrow both with `isinstance` and raise
  `BuildError` on a shape the pipeline must never see; `_cell_cutters` narrows its
  prototype to a `Solid` with the same guard. `src/spur/` carries no mypy
  suppression and `make no-fake-done` refuses a new one; history in
  `docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md`.
- **A single large build stalls the event loop** for a second or two, because OCCT holds
  the GIL. Known, bounded by L04, not fixed — see
  `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md`.
- **The root arc has a dead band in the kernel.** Between neighbouring hob roots the outline
  draws a three-point arc whose chord is about twice the cutter's tip land. 12 teeth,
  module 1, 20 degrees, cadquery 2.8.0: `makeThreePointArc` raises
  `GC_MakeArcOfCircle::Value() - no result` at every chord from 2e-9 mm to 2.0e-7 mm and at
  exactly 0, silently drops the arc (a valid solid, 62 faces where 74 are expected) at
  2e-12 and 2e-10 mm, and builds from 4.0e-7 mm. A typed backlash reaches it, because the
  tip radius cap floors to 3 dp and backlash is not stepped on the wire: backlash
  0.19898413579248878 with `root_fillet` 3.0 leaves a tip land of 1.0e-8 mm. `ROOT_ARC_MIN`
  routes around it; do not lower it without re-reading the table in `bench/RESULTS.md`
  "Root arc dead band".
- **`_build_checked()` blames the user's fillets for any kernel exception.** Its relabel,
  "try smaller fillets or chamfers", is the wrong remedy for a defect in the hob-root
  outline (the user set neither). That is why the hob-root guards raise `BuildError`
  themselves, with their own sentence, before the kernel can: a new way for that outline to
  fail should be a new guard or a new branch, not another case for the relabel. The kernel
  calls inside that outline (`makeSpline`, `makeThreePointArc`, `assembleEdges` in
  `_trochoid_outline` and `makeFromWires` in `_gear_blank`) are covered the same way by
  `_hob_root_kernel_failure`, only on the trochoid branch (19-REVIEW WR-01).
- **The generator stays out of this module.** `model.py` receives a `RootCurve` from
  `calc.RootMode` and never names the generator; `test_the_trochoid_generator_never_enters_the_model_module`
  reads this file's source for the generator's names, as whole identifiers (`_guard_junction`
  is not `_junction`).
