# solid-model — tests

## Coverage

`tests/test_model.py` — 235 tests collected (2026-10-09), integration tier: they drive the real
kernel, no mocks. Mocking OpenCascade would test the mock. The first five below are the
original set; the cutout, chamfer and fillet-survival proofs that followed are described in
their own docstrings, and the hob root's are listed after them.

- `test_builds_one_valid_solid` — eight parameter sets across the interesting corners
  (no bore, no flat, no recess, one-sided recess, no fillets at all, a small gear, a
  large shifted gear). Asserts validity and exactly one solid.
- `test_recess_removes_expected_volume` — the recess is checked by volume against the
  annulus it should have removed, to 0.1%. A geometric assertion, not a snapshot.
- `test_exports` — both formats produce bytes with the right magic.
- `test_a_gear_too_small_for_the_stock_recess_still_builds` — the L03 contract at the
  kernel level: capping must produce a sane annulus, not a degenerate one.
- `test_exported_stl_is_a_closed_consistently_oriented_shell` — parses the binary STL and
  checks the topology directly: every directed edge unique and paired, no degenerate
  facets, positive volume. A flipped or missing facet is invisible in the 3D preview and
  turns up as a broken print, so this is the test that protects the actual deliverable.

**The hob root (Phase 19, `root_shape="trochoid"`).** Each of these builds a real solid:

- `test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root` — the tracer: one
  valid solid, 134 faces and 376 edges against the default part's 172 and 490, and tooth 0's
  root splines read by the independent swept-cutter oracle within the bar.
- `test_the_built_root_is_the_oracle_s_root_on_every_kernel_row` — seven rows typed out from
  19-02 (never generated from `calc`), each read at 401 positions per root edge within
  `KERNEL_BAR_PER_MODULE` (2e-3 mm per mm of module) of the oracle, given the tip radius
  `derive()` printed; the printed radius is pinned to the one the cutter used.
- `test_the_kernel_tier_proof_fails_when_the_printed_tip_radius_is_off_by_0_05_mm` — the
  tripwire that gives the rows teeth: the module-1 10-tooth row read 0.05 mm off reads 5.5x
  over the bar. It sits on module 1 because on module 10 the same shift reads 0.66x of it.
- `test_root_d_is_the_root_circle_in_both_root_modes` — one CIRCLE edge per gap on the root
  circle, `root_d == round(2 rf, 3)`, no root spline sample below it.
- `test_nothing_radial_to_replace_builds_the_radial_part` — the rb = rf boundary, 42 teeth
  refused and building the radial part, 41 building the hob root.
- `test_the_same_trochoid_link_builds_the_same_solid_twice` and
  `test_a_radial_and_a_trochoid_request_never_share_a_cached_solid` — L05 and the cache key.
- `test_the_trochoid_generator_never_enters_the_model_module` — a source test: the
  generator's names, as whole identifiers, never appear in `model.py`.
- `test_a_root_arc_shorter_than_root_arc_min_is_left_out_and_the_teeth_share_a_vertex`,
  `test_a_hand_built_curve_with_no_tip_land_builds_without_a_root_arc` and
  `test_a_root_arc_above_root_arc_min_is_kept` — the short-arc rule: a backlash bisected
  until the tip land is near 1e-8 mm builds through `build(p)` with 5 side faces per tooth
  (and the two teeth hold one `Vector`), a chord of about 0 builds, and lands of 1e-5 and
  1.5e-6 mm keep every arc.
- `test_a_root_curve_that_leaves_the_involute_at_its_junction_is_a_build_error`,
  `test_root_points_bunched_past_the_spacing_bar_are_a_build_error`,
  `test_a_root_spline_outside_the_root_to_tip_annulus_is_a_build_error` and
  `test_an_outline_whose_area_misses_its_polygon_is_a_build_error` — one hand-built defect per
  guard (the junction and spacing ones with the kernel patched to fail if reached), the area
  guard on a real gear with its bar set to zero; each error says it is a modelling defect in
  spur and names `root_shape`. `test_no_guard_fires_on_an_honest_curve` builds the default
  gear and the seven kernel rows through `_build_checked` with all four in place.

`docker/smoke.py` runs at image build time and exercises the kernel, both exporters and
the ASGI stack inside the trimmed image — so an incomplete dependency closure fails the
build rather than production.

## Gaps

- Nothing tests cache eviction or the byte budget in `_BlobCache` directly.
- Nothing asserts the memory behaviour L07 was built for; the numbers in
  `docs/plan-2026-09-21.md` came from a manual sweep that is not automated.
- No test covers `_release_arenas()` on glibc — it is a no-op on the macOS dev machine.

## Run

```
make verify                                  # the gate (these tests included)
make test-image                              # the suite inside the container, no local python
make smoke                                   # the build-time smoke test, in the image
.venv/bin/python -m pytest tests/test_model.py -q
```

A cold first run pages in ~1.4 GB of OpenCascade and takes ~2 minutes; warm it is ~8 s.
