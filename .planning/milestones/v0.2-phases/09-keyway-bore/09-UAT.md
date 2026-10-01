---
status: complete
phase: 09-keyway-bore
source: 09-01-SUMMARY.md, 09-02-SUMMARY.md, 09-03-SUMMARY.md, 09-04-SUMMARY.md, 09-05-SUMMARY.md
started: 2026-09-28T06:11:38Z
updated: 2026-09-28T06:19:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running spur server. Start it fresh with `make serve` (dev, http://127.0.0.1:8000) or `make up` (container). It boots with no errors or tracebacks; `GET /api/health` returns OK; the page loads and the parameter form shows `keyway_width` and `keyway_depth` between `bore_flat` and `bore_hex`; setting keyway_width=3, keyway_depth=1.4 on the defaults renders a D-flat bore with a slot on the side a quarter turn from the flat, and the numbers panel shows keyway_floor_to_wall 10.55 mm and keyway_width_effective 3.15 mm with no warning.
result: pass

### 2. 09-01 Requirements and roadmap amendments — confirm automated coverage
expected: Every 09-01 deliverable is covered by a passing automated check and nothing needs a human read. D1 REQUIREMENTS.md REQ-keyway-bore / REQ-keyway-wall-refused amended to the as-cut datum and the yielding recess (greps for `(bore_d + bore_clearance)/2`, `Phase 9 D-14`, `Phase 9 D-09/D-10`). D2 ROADMAP Phase 9 SC1/SC3/SC4 amended, SC2/SC5/Goal untouched (scoped sed + grep, superseded phrases = 0). D3 STATE.md carries the Roadmap Evolution line; milestone scope unchanged phases 7–12. Confirm, or name a deliverable you want to read yourself.
result: pass

### 3. 09-02 Keyway cut, datum, chamfer order, derived numbers — confirm automated coverage
expected: Every 09-02 deliverable is covered by a named passing test. D1 keyed D-flat link builds through API/CLI/schema, prints floor-to-wall 10.55 mm and width 3.15 mm, recess moved to 13.158/25.158 mm, no warnings (tests/test_api.py::test_a_keyed_link_is_served_with_its_two_numbers; `spur info --keyway-width 3 --keyway-depth 1.4`). D2 floor sits at bore_radius(p)+keyway_depth measured on the built solid, D-flat and round (test_model.py::test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall). D3 bore_flat stays when a keyway is added. D4 bore chamfer survives the slot, slot edges sharp, rim selector takes exactly the pre-keyway edges (three test_model.py tests). D5 DerivedDimensions keyway_floor_to_wall / keyway_width_effective correct and null without a keyway; recess yields; pre-v0.2 regression fixture byte-unchanged (test_calc.py, tests/regression/test_pre_v0_2.py). Confirm, or name a deliverable you want to read yourself.
result: pass

### 4. 09-03 Keyway refusals and the round-bore chamfer-reach rule — confirm automated coverage
expected: Every 09-03 deliverable is covered by a named passing test. D1 keyway on hex / no bore / half-set pair is a 422 naming the fields, decided before the per-shape branches. D2 keyway wider than the bore, into the D-flat, or reaching the root corner is a 422 one step either side of each bound; accepted links build one step inside; refused configurations still cut one valid solid in the kernel (five tests across test_calc.py and test_model.py). D3 API, CLI and `spur info` agree on every refusal and on the largest accepted keyway. D4 round/D-flat chamfered mouth reaching the root circle is refused at the re-measured contact (ROOT_CONTACT), rules never stack, fixture unchanged. D5 the Phase 8 chamfer-reach debt file is resolved and moved. Confirm, or name a deliverable you want to read yourself.
result: pass

### 5. 09-04 Keyway build-time sweep — confirm automated coverage
expected: Every 09-04 deliverable is covered by a passing automated check. D1 bench/sweeps/keyway_bore.json is the full 32-row cross product, each large keyway exactly one step (0.05 mm) from a refusal (tests/test_bench.py; row count asserted = 32). D2 one keyed set runs end to end through `make bench.build` and emits its timed row. D3 bench/RESULTS.md records all 32 rows, none over 30 s, heaviest row named (4.85 s), host state and load caveat, make verify wall-time delta. Confirm, or name a deliverable you want to read yourself.
result: pass

### 6. No keyway size is given as sizing guidance (09-05 D7, human judgment)
expected: Read README.md rows 158–159 (`keyway_width`, `keyway_depth`), the Geometry-notes keyway bullet at lines 204–213, and decision_log.md L28 (from line ~910). DIN 6885 / ISO R773 t2 / ANSI B17.1 appear only as conventions naming the datum; no sentence reads as a recommendation of a keyway size for a given bore. The CLI example `--keyway-width 3 --keyway-depth 1.4` is an invocation, not a recommendation. Read L28's "The recess yields" paragraph (line ~965) with care: it calls 3 × 1.4 mm "the DIN-6885-correct" key for the default 9 mm bore as the measured reason for the yield rule — judge whether that reads as engineering rationale in a decision log or as sizing guidance (D-16, L08).
result: pass

### 7. REQUIREMENTS.md REQ-keyway-bore and REQ-keyway-wall-refused amended to match D-14 and D-09/D-10; footer updated
expected: REQUIREMENTS.md REQ-keyway-bore and REQ-keyway-wall-refused amended to match D-14 and D-09/D-10; footer updated
result: pass
source: automated
coverage_id: 09-01 D1

### 8. ROADMAP Phase 9 Requirements line unwrapped; SC1, SC3, SC4 amended; SC2, SC5, Goal, Depends on, Research flag and Plans lines untouched
expected: ROADMAP Phase 9 Requirements line unwrapped; SC1, SC3, SC4 amended to match D-14, D-09/D-10, D-05/D-07; SC2, SC5, Goal, Depends on, Research flag and Plans lines untouched
result: pass
source: automated
coverage_id: 09-01 D2

### 9. STATE.md carries one new Roadmap Evolution line; ROADMAP.md written only through edit-phase's write step
expected: STATE.md carries one new Roadmap Evolution line for the Phase 9 edit; ROADMAP.md written only through edit-phase's write step with the milestone-scope check unchanged before/after (phases 7-12)
result: pass
source: automated
coverage_id: 09-01 D3

### 10. A keyed D-flat link builds end to end through the API, CLI and form schema and prints its two numbers
expected: A keyed D-flat link builds end to end through the API, CLI and form schema and prints its floor-to-wall (10.55 mm) and width (3.15 mm), with the recess moved to 13.158/25.158 mm and no warnings
result: pass
source: automated
coverage_id: 09-02 D1

### 11. The keyway floor sits at bore_radius(p) + keyway_depth, measured on the built solid
expected: The keyway floor sits at bore_radius(p) + keyway_depth, measured on the built solid against the kernel-read bore-wall radius, for both a D-flat and a round bore (D-14)
result: pass
source: automated
coverage_id: 09-02 D2

### 12. bore_flat stays when a keyway is added
expected: bore_flat stays when a keyway is added: the default keyed link still carries its D-flat face at the expected x
result: pass
source: automated
coverage_id: 09-02 D3

### 13. The bore chamfer survives the keyway slot and the slot's own edges stay sharp
expected: The bore chamfer survives the keyway slot and the slot's own edges stay sharp on both a D-flat and a round bore; the rim selector takes exactly the pre-keyway edges
result: pass
source: automated
coverage_id: 09-02 D4

### 14. DerivedDimensions.keyway_floor_to_wall and .keyway_width_effective report the correct numbers; the recess yields
expected: DerivedDimensions.keyway_floor_to_wall and .keyway_width_effective report the correct numbers and are null with no keyway; the recess yields to the keyway corner with the existing warnings; the pre-v0.2 fixture is byte-unchanged
result: pass
source: automated
coverage_id: 09-02 D5

### 15. A keyway conflicting with a hex bore, no bore, or a half-set pair is a 422 naming the fields
expected: A keyway conflicting with a hex bore, no bore, or a half-set pair is a 422 naming the fields, decided in check() before the per-shape branches (D-13, D-03)
result: pass
source: automated
coverage_id: 09-03 D1

### 16. A keyway wider than the bore, into the D-flat, or reaching the root corner is a 422 one step either side of each bound
expected: A keyway wider than the bore, running into the D-flat, or reaching the root corner is a 422 naming its fields, one step either side of each measured or definitional bound (D-11, D-02, D-10); accepted links build one step inside, refused geometric configurations still cut one valid solid in the kernel
result: pass
source: automated
coverage_id: 09-03 D2

### 17. The API, the CLI and spur info agree on every keyway refusal and on the largest accepted keyway
expected: The API, the CLI and spur info agree on every keyway refusal and on the largest accepted keyway (REQ-keyway-composes-with-d-flat's D-flat + keyway link included)
result: pass
source: automated
coverage_id: 09-03 D3

### 18. A round or D-flat bore whose chamfered mouth reaches the root circle is refused at the re-measured contact point
expected: A round or D-flat bore whose chamfered mouth reaches the root circle is refused naming bore_chamfer and bore_d, at the re-measured contact point, never at rf - MIN_WALL; the round-bore rules never stack; the pre-v0.2 fixture is unchanged
result: pass
source: automated
coverage_id: 09-03 D4

### 19. The Phase 8 round-bore chamfer-reach debt file is resolved, moved and indexed
expected: docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md is resolved, moved to resolved/ and indexed in the fix commit, with its Resolved in: sha
result: pass
source: automated
coverage_id: 09-03 D5

### 20. bench/sweeps/keyway_bore.json holds the full 32-row cross product
expected: bench/sweeps/keyway_bore.json holds the full 32-row cross product (module x bore_flat x keyway x recess_sides x bore_chamfer), every row a buildable gear under 09-03's rules, each large keyway sitting exactly one step (0.05 mm) from a refusal
result: pass
source: automated
coverage_id: 09-04 D1

### 21. One keyed set runs end to end through make bench.build and produces its timed Markdown row
expected: One keyed set (keyway_width=3, keyway_depth=1.4) runs end to end through make bench.build and produces its timed Markdown row
result: pass
source: automated
coverage_id: 09-04 D2

### 22. bench/RESULTS.md records all 32 measured rows, none over 30 s
expected: bench/RESULTS.md records all 32 measured rows, none over 30 s, the named heaviest row, the host state with its load caveat, and the make verify wall time delta -- REQ-measured-build-time's per-feature entry for the keyway, ROADMAP Phase 9 SC5
result: pass
source: automated
coverage_id: 09-04 D3

### 23. README.md documents the keyway
expected: README.md documents the keyway: feature bullet, keyway_width/keyway_depth rows between bore_flat and bore_hex (params.py order), the bore_clearance row extended, a keyed CLI export example, refusal prose, and a Geometry notes bullet on the datum and the two printed numbers
result: pass
source: automated
coverage_id: 09-05 D1

### 24. The README's keyed CLI example builds the default D-flat bore plus keyway link end to end
expected: The README's keyed CLI example (spur export -o keyedgear.step --keyway-width 3 --keyway-depth 1.4) builds the default D-flat bore plus keyway link end to end with no warning
result: pass
source: automated
coverage_id: 09-05 D2

### 25. The Geometry notes bullet names both derived fields and what a pin/calipers check reads from each
expected: The Geometry notes bullet names both derived fields -- keyway_floor_to_wall and keyway_width_effective -- and what a pin/calipers check reads from each, matching DerivedDimensions (09-02)
result: pass
source: automated
coverage_id: 09-05 D3

### 26. L28 is appended after L27; decision_log.md stays append-only
expected: L28 is appended after L27 with the datum formula, every phase decision and its SUMMARY citation, and the sweep's heaviest row; decision_log.md stays append-only
result: pass
source: automated
coverage_id: 09-05 D4

### 27. The architecture docs name the keyway helpers, ROOT_CONTACT and _cut_keyway
expected: docs/architecture/gear-maths/implementation.md and solid-model/tactics.md name the keyway helpers, ROOT_CONTACT and _cut_keyway so the architecture docs describe the code as built
result: pass
source: automated
coverage_id: 09-05 D5

### 28. make verify is green at the end of the phase
expected: make verify is green at the end of the phase
result: pass
source: automated
coverage_id: 09-05 D6

## Summary

total: 28
passed: 28
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
