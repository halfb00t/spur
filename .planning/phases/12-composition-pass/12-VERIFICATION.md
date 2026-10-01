---
phase: 12-composition-pass
verified: 2026-09-30T20:25:00Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/phases/12-composition-pass/12-01-PLAN.md", ".planning/phases/12-composition-pass/12-01-SUMMARY.md", ".planning/phases/12-composition-pass/12-02-PLAN.md", ".planning/phases/12-composition-pass/12-02-SUMMARY.md", ".planning/phases/12-composition-pass/12-03-PLAN.md", ".planning/phases/12-composition-pass/12-03-SUMMARY.md", ".planning/phases/12-composition-pass/12-04-PLAN.md", ".planning/phases/12-composition-pass/12-04-SUMMARY.md", ".planning/phases/12-composition-pass/12-05-PLAN.md", ".planning/phases/12-composition-pass/12-05-SUMMARY.md", ".planning/phases/12-composition-pass/12-06-PLAN.md", ".planning/phases/12-composition-pass/12-06-SUMMARY.md", ".planning/phases/12-composition-pass/12-07-PLAN.md", ".planning/phases/12-composition-pass/12-07-SUMMARY.md", ".planning/phases/12-composition-pass/12-08-PLAN.md", ".planning/phases/12-composition-pass/12-08-SUMMARY.md", ".planning/phases/12-composition-pass/12-09-PLAN.md", ".planning/phases/12-composition-pass/12-09-SUMMARY.md", "Makefile", "README.md", "bench/RESULTS.md", "bench/build_time.py", "bench/export_cost.py", "bench/sweeps/composed.json", "bench/sweeps/spoke_cutout.json", "docs/architecture/cli.md", "docs/architecture/decision_log.md", "docs/ideas/2026-09-21-browser-test-for-the-viewer.md", "docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md", "docs/ideas/2026-09-29-conditional-form-fields.md", "docs/ideas/INDEX.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md", "docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md", "docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md", "docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md", "src/spur/app.py", "src/spur/params.py", "tests/composition.py", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v2:sha256:6da9e9e8f55fdf6e3e40074fc3368d0cc0d956c683df6739c2de704254b23476"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open the app with `make serve`. Confirm the form shows the seven fieldsets in order: Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb."
    expected: "Seven fieldsets appear in exactly that order, matching the human-confirmed 12-01 answer and the live /api/schema group order the automated test already pins."
    why_human: "Rendered fieldset order/count on the actual page is not observable from a static read of app.js; only a human opening the page can see it."
  - test: "Open `http://127.0.0.1:8000/#bore_flat=0&keyway_width=3&keyway_depth=1.4&spoke_count=4&spoke_width=2&hub_d=13.2&rim_wall=1&spoke_fillet=1&tip_chamfer=0.4`."
    expected: "All nine fields show the link's value, the 3D preview builds, the dimensions list shows the tip chamfer, keyway, recess, both cutout walls and the spoke fillet, and no warning appears."
    why_human: "Hash-to-form population, live preview build, and dimensions-panel rendering are runtime DOM/WebGL behavior the static app.js read and the API/CLI parity tests cannot observe."
  - test: "Click 'copy link' on that page, open the copied link in a new tab."
    expected: "The same nine values load and the same numbers print."
    why_human: "The copy-to-clipboard interaction and a second page load are live-browser behavior with no server-side or static-source proxy."
  - test: "In that new tab, set `bore_hex` to 6."
    expected: "A 422 sentence naming the keyway and the hex fields appears in the UI, and the bore fields are marked invalid."
    why_human: "Live client-side error rendering in response to a real 422 response is a runtime UI behavior, not something the static source read proves."
---

# Phase 12: Composition Pass Verification Report

**Phase Goal:** Every v0.2 feature composes correctly across the full matrix, the
milestone's heaviest-configuration build time is measured, and all three interfaces stay
in parity — closing out v0.2.
**Verified:** 2026-09-30T20:25:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Success criteria as amended by 12-01 (SC3, SC5) and confirmed present, byte-identical, in
the current `.planning/ROADMAP.md` Phase 12 section.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: full composition matrix passes — recess × each bore shape, recess × each cutout, each cutout × each bore, every locked refusal (keyway×hex, two-cutout) with the 422 naming fields | ✓ VERIFIED | `tests/composition.py` + `tests/test_calc.py::test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers` (96 rows, collected and confirmed) + `::test_every_refusal_reads_the_same_with_each_other_family_switched_on` (138 rows, collected and confirmed) — calc tier; `tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore` (12 rows) + `::test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess` (3 rows) — kernel tier, spot-run `[keyed-spokes]` passed live (`1 passed in 5.07s`); `tests/test_cli.py::test_every_refusal_reads_the_same_on_the_api_and_the_cli` (23 rows, collected and confirmed) — API/CLI tier. Fresh `make verify`: 907 passed. |
| 2 | SC2: every v0.2 parameter on the form (own group), API, CLI from one `GearParams` model; round-trips the shareable URL; appears in `/api/schema`; `spur info`/`spur export` match the API | ✓ VERIFIED | `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`, `test_the_shareable_link_round_trips_every_field_through_generic_code`, `test_cli_and_api_print_the_same_composed_document`, `test_every_refusal_reads_the_same_on_the_api_and_the_cli` — all collected and passing in the fresh `make verify` run (907 passed). Seven-group order (Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb) is the 12-01 human-confirmed answer, re-verified live against `/api/schema` per 12-07-SUMMARY.md. The live-browser half of this truth (rendered form, link load, copy-link, live 422) is not exercised by any test and is routed to human verification below. |
| 3 | SC3 (amended): `bench/RESULTS.md` records build + fine-STL/STEP export time for the composed sweep (each cutout stacked with tip chamfer and a recess on the heaviest bore its rules allow, module 1.75 and 10) and for each individual feature, inside `SPUR_BUILD_TIMEOUT` | ✓ VERIFIED | `bench/sweeps/composed.json` confirmed 18 rows on disk. `bench/RESULTS.md` "Composed build and export time (Phase 12)" section confirmed present with four runs, a gate probe, `spoke_count` lowered 40→32 (`src/spur/params.py` grep-confirmed `le=32`), and a final re-run with every row inside 30 s (heaviest 29.42 s). |
| 4 | SC4: L19's gzip-level table and L24's mesh-copy timing re-measured against the heaviest v0.2 face topology | ✓ VERIFIED | `bench/export_cost.py` exists; `bench/RESULTS.md` "Export cost on the heaviest v0.2 topology (Phase 12)" section confirmed present with the re-measured table and L24's copy-cost numbers; `src/spur/app.py` gained the dated comment addition above `_GZIP_LEVEL` (grep-confirmed `_GZIP_LEVEL = 1` unchanged). |
| 5 | SC5 (amended): Phase 7's regression fixture passes one final time across the whole matrix — identical `DerivedDimensions` and solid (volume, bounding box, face and edge counts); export bytes not compared | ✓ VERIFIED | `git diff --quiet c9a169d -- tests/regression/pre_v0_2.json` confirmed clean (byte-unchanged). Fresh `make verify` this session: `tests/regression/test_pre_v0_2.py` all passed as part of the 907-passed full run. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/composition.py` | shared family/refusal tables for calc- and CLI-level composition tests | ✓ VERIFIED | Exists, imported by `tests/test_calc.py` and `tests/test_cli.py`, non-collected data module |
| `bench/sweeps/composed.json` | 18-row composed sweep (D-01) | ✓ VERIFIED | 18 entries confirmed by direct JSON load |
| `bench/build_time.py` | `stl_size()`, `Timing.stl_bytes`/`stl_triangles`, largest-fine-STL reporting | ✓ VERIFIED | File present, referenced by passing `tests/test_bench.py` rows |
| `bench/export_cost.py` | L19/L24 re-measurement script behind `make bench.export` | ✓ VERIFIED | File present, referenced by passing `tests/test_bench.py` rows |
| `docs/architecture/decision_log.md` L31 | phase close-out entry, append-only | ✓ VERIFIED | `## L31 —` present once; `git diff --numstat c9a169d` shows 0 deleted lines; cites all three Phase 12 bench/RESULTS.md section titles |
| `docs/architecture/cli.md` Errors section | real 2/1/1 exit contract | ✓ VERIFIED | Confirmed rewritten with 2× "exit 2", 2× "exit 1", the false single-status claim absent |
| `docs/tech_debt/resolved/*` (3 files) | two build-timeout debts + the cli.md debt resolved | ✓ VERIFIED | All three present in `resolved/`, absent from `active/` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.planning/ROADMAP.md` Phase 12 SC3 | `12-CONTEXT.md` D-01/D-03/D-06 | citation string in the amended criterion | ✓ WIRED | `grep -cF '12-CONTEXT.md D-01/D-03/D-06'` present in SC3 text |
| `.planning/ROADMAP.md` Phase 12 SC5 | `tests/regression/test_pre_v0_2.py` comparison contract | SC5 names DerivedDimensions + solid geometry, export bytes excluded | ✓ WIRED | SC5 text confirmed matches the replay's actual comparison (volume, bounding box, face/edge counts; no export byte comparison) |
| `bench/RESULTS.md` "Largest fine STL" line | `bench/export_cost.py` input row | same 17,306,084-byte row named in both sections | ✓ WIRED | Confirmed identical row cited in both "Composed build and export time" and "Export cost on the heaviest v0.2 topology" sections |
| `src/spur/params.py` `spoke_count.le=32` | `bench/sweeps/composed.json`/`spoke_cutout.json` | every `spoke_count=40` row moved to 32 | ✓ WIRED | `grep -c 'le=32'`-style confirmation via file inspection; composed sweep re-run confirmed all rows inside 30 s at the new bound |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| A composed kernel-tier row (tip chamfer + spokes on a keyed bore) actually builds and passes both feature proofs | `.venv/bin/python -m pytest -q "tests/test_model.py::test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore[keyed-spokes]"` | `1 passed in 5.07s` | ✓ PASS |
| The 96-row and 138-row calc-level composition matrices collect exactly as claimed | `pytest --collect-only -q tests/test_calc.py -k "..."` | `234/389 tests collected (155 deselected)` | ✓ PASS |
| The 12-row and 3-row kernel-level composition matrix collects exactly as claimed | `pytest --collect-only -q tests/test_model.py -k "..."` | `15/200 tests collected (185 deselected)` | ✓ PASS |
| The 23-row API/CLI refusal-parity table plus the two other parity tests collect exactly as claimed | `pytest --collect-only -q tests/test_cli.py -k "..."` | `25/44 tests collected (19 deselected)` | ✓ PASS |
| Full gate: `make verify` | `make verify` (fresh run, this session) | `907 passed in 212.42s`; all 5 import-boundary contracts kept; exit 0 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| REQ-measured-build-time | 12-01, 12-02, 12-03, 12-04, 12-09 | Recorded build/export time per feature at its heaviest, recess × each cutout, honeycomb at cap, inside `SPUR_BUILD_TIMEOUT` | ✓ SATISFIED | `REQUIREMENTS.md` marks Complete; `bench/RESULTS.md` sections confirmed present with real measured numbers |
| REQ-three-interfaces-extended | 12-01, 12-05, 12-06, 12-07, 12-08, 12-09 | Every v0.2 parameter on form/API/CLI, URL round trip, `/api/schema`; `spur info`/`export` match the API | ✓ SATISFIED | `REQUIREMENTS.md` marks Complete; parity tests confirmed collected and passing in fresh `make verify` run |

No orphaned Phase 12 requirements found in `REQUIREMENTS.md` beyond these two.

### Anti-Patterns Found

None. Scanned every file this phase touched (`git diff --name-only c9a169d..HEAD`, ~43 files across `.py`/`.md`/`.js`) for `TBD`/`FIXME`/`XXX` (debt-marker gate) and `TODO`/`HACK`/`PLACEHOLDER` — zero matches in both passes.

### Prohibitions (12-01-PLAN.md must_haves.prohibitions)

| # | Statement | Status | Evidence |
|---|-----------|--------|----------|
| 1 | MUST NOT write ROADMAP.md directly or before human approval | resolved | Commit history (`4a4c679`) shows the write landed only after the recorded checkpoint answer; Task 1 built the diff without writing (verified by `git diff --quiet` gate in the plan itself) |
| 2 | MUST NOT name a winning configuration in SC3 before the sweep measured it | resolved | Current SC3 text names no specific winning feature combination — it describes the sweep's design generically ("each cutout pattern stacked with the tip chamfer and a recess on the heaviest bore its rules allow") |

### Human Verification Required

`docs/architecture/decision_log.md` D-11 (cited by `12-CONTEXT.md`, applied in `12-07-SUMMARY.md`) designed interface parity (SC2) as three complementary proofs: a model-driven parity test, a static URL round-trip proof, and a manual browser checklist. The first two are done and passing. The third — the manual browser checklist 12-07-SUMMARY.md produced verbatim for `gsd-verify-work` — has not yet been run by a human; no `12-UAT.md` or equivalent record exists in the phase directory. Because SC2's own design calls for this third leg and it is unexercised, it is surfaced here rather than silently dropped.

1. **Seven fieldsets render in order** — see frontmatter `human_verification[0]`.
2. **The composed link loads into the live form and builds a preview** — see frontmatter `human_verification[1]`.
3. **Copy-link round trip** — see frontmatter `human_verification[2]`.
4. **Live 422 on the hex+keyway conflict** — see frontmatter `human_verification[3]`.

### Gaps Summary

No gaps. All five roadmap success criteria (as amended by 12-01) are verified against
actual artifacts, tests collected and spot-run, and a fresh `make verify` (907 passed,
212.42s, all contracts kept). Both requirement IDs are satisfied. No debt markers, no
stub patterns, no orphaned requirements. The only open item is the manual browser
checklist the phase's own D-11 design calls for — not a defect, but unexercised human
verification that the phase's own SUMMARY explicitly deferred to `gsd-verify-work`.

---

*Verified: 2026-09-30T20:25:00Z*
*Verifier: Claude (gsd-verifier)*
