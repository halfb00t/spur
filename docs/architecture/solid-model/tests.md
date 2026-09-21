# solid-model — tests

## Coverage

`tests/test_model.py` — 13 tests, integration tier: they drive the real kernel, no mocks.
Mocking OpenCascade would test the mock.

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
