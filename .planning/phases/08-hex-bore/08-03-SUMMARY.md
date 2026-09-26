---
phase: 08-hex-bore
plan: 03
subsystem: cad
tags: [hex-bore, calc, validation, warnings, readme]

# Dependency graph
requires:
  - phase: 08-hex-bore
    provides: "08-02's bore_hex field, hex_across_flats(p), bore_rim_limit(p)/bore_mouth_limit(p) hex branches, and the re-datumed recess_radii(), proven end to end on the built solid"
provides:
  - "calc.check()'s hex branch: corner-vs-root refusal naming bore_hex; chamfered-corner-vs-root refusal naming bore_chamfer and bore_hex; round-profile rules skipped under a hex"
  - "calc.derive()'s D-02 warning: names each non-zero round-bore field (bore_d, bore_flat) a hex bore ignores, with its value"
  - "the chamfer-vs-side probe (D-03's Flagged Assumption A4), recorded as a test rather than a rule: the kernel copes with chamfer against a hex's side at every allowed size"
  - "README.md and params.py help text documenting bore_hex, with a hex CLI example the test suite runs"
affects: [08-04-PLAN.md, 09-keyway-bore]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 4722
  tasks: 2
  commits: 2
  plan_head_before: eed22b0248b8a4bb7b7d5dd358b06c895621f21e

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "check()'s bore-shape branch is if/elif/else on bore_hex, not a flag threaded through the existing round rules -- a later bore shape (Phase 9's keyway) adds its own branch rather than growing conditionals inside this one"
    - "A shape-independent rule (chamfer vs. face_width) stays outside the per-shape if/elif/else, applying after it unconditionally"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - src/spur/params.py
    - README.md
    - tests/test_calc.py
    - tests/test_api.py
    - tests/test_cli.py
    - tests/test_model.py

key-decisions:
  - "D-03's chamfer bound sits on the root circle (bore_mouth_limit(p) > pr.rf - MIN_WALL), not on the hex's side length: the planning probe (bore_hex=0.5, chamfer up to 3 mm, side 0.375 mm, ratio 8) found no kernel failure against the side at any allowed size, matching the analytic hex frustum volume within rel 1e-6 -- so no side rule was added, and the probe became a test instead (Flagged Assumption A4)."
  - "The corner rule (bore_hex alone) and the chamfered-corner rule (bore_chamfer + bore_hex) never stack: with bore_chamfer 0 the mouth equals the corner, so only the first `if` can fire before the `elif` is reached (Flagged Assumption A5)."
  - "One commit per task (D-14, CLAUDE.md 'one concern per commit'): each task's tests and implementation landed together rather than as separate RED/GREEN commits, per the plan's explicit single-commit instruction for this tdd=\"true\" tracer task."

patterns-established:
  - "A per-shape bore rule lives inside its own if/elif branch in check(), with the shape-independent rules (chamfer vs. face_width, the recess web) staying outside it -- Phase 9's keyway rules join the same if/elif chain."

requirements-completed: [REQ-hex-bore]

coverage:
  - id: D1
    description: "A hex whose corners reach within MIN_WALL of the root circle is a 422 naming only bore_hex, decided in calc.check() before any CAD work; the corner rule ignores the chamfer and refuses one step past the measured boundary (24.2 mm), builds one step inside it (24.15 mm)"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_hex_bore_is_refused_when_its_corners_reach_the_root_and_builds_one_step_inside"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_hex_bore_the_root_cannot_hold_is_422_naming_bore_hex"
        status: pass
      - kind: integration
        ref: "tests/test_cli.py#test_a_hex_bore_the_root_cannot_hold_exits_2_and_names_it"
        status: pass
      - kind: integration
        ref: "tests/test_model.py#test_the_largest_hex_each_root_rule_allows_builds[corner-limit]"
        status: pass
    human_judgment: false
  - id: D2
    description: "A bore_chamfer that carries the hex's corners within MIN_WALL of the root circle is a 422 naming bore_chamfer and bore_hex, refused one step past the measured boundary (23.4 mm), builds one step inside it (23.35 mm)"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_hex_bore_chamfer_that_carries_the_corners_to_the_root_is_refused_naming_both"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_hex_bore_chamfer_reaching_the_root_is_422_naming_both_fields"
        status: pass
      - kind: integration
        ref: "tests/test_model.py#test_the_largest_hex_each_root_rule_allows_builds[chamfered-corner-limit]"
        status: pass
    human_judgment: false
  - id: D3
    description: "With bore_hex > 0 the round-profile rules (bore too large, D-flat range) do not run -- a bore_flat or bore_d that would refuse under a round bore builds under a hex; the shape-independent chamfer-vs-face-width rule still applies and names only bore_chamfer"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_hex_bore_skips_the_round_bore_rules"
        status: pass
    human_judgment: false
  - id: D4
    description: "The chamfer-vs-side probe: the kernel chamfers a 0.375 mm side at the full 3 mm field bound (ratio 8) with removed volume matching the analytic hex frustum within rel 1e-6 -- no rule was added, and the probe result is recorded as a test instead (D-03 Flagged Assumption A4)"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_kernel_chamfers_a_hex_bore_far_past_its_side_length"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every hex link that leaves bore_d or bore_flat non-zero carries exactly one warning naming each non-zero ignored field with its value; no warning when both are 0"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_hex_bore_warns_about_each_round_field_it_ignores (5 rows)"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_hex_link_with_a_d_flat_builds_and_says_both_round_fields_are_ignored"
        status: pass
    human_judgment: false
  - id: D6
    description: "The API, the CLI and derive() print calc's own sentences with no per-interface wording -- the CLI's exit 2 matches the API's 422 detail, and spur info --bore-hex 6 equals /api/info?bore_hex=6 key-for-key, including the D-02 warning"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_hex_bore_document"
        status: pass
    human_judgment: false
  - id: D7
    description: "README.md lists the hex bore in the feature bullet, a bore_hex parameter row carrying D-08's help sentence, and a spur export ... --bore-hex 6 example that the CLI test suite runs and confirms warns; bore_d and bore_clearance help texts stay true for a hex bore; the example stays out of the closed pre-v0.2 regression corpus"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
      - kind: other
        ref: "git diff --quiet 540f1a0 -- tests/regression/corpus.py"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-09-26
status: complete
---

# Phase 8 Plan 3: Hex Bore Refusals and the Ignored-Field Warning Summary

**`calc.check()` refuses a hex bore or chamfer the root cannot hold with two measured boundary rules, `calc.derive()` warns which round-bore fields a hex ignores, and the README/help text now say the same thing every interface already proves.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-26T16:05Z (session start; `PLAN_START_TIME` not captured at the top of this run)
- **Completed:** 2026-09-26
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- `calc.check()`'s round-bore block is now an `if p.bore_hex > 0: ... else: ...` pair. The hex branch carries two rules, both refusing before any CAD work touches the kernel: the corner rule (`bore_rim_limit(p) > pr.rf - MIN_WALL`, naming `bore_hex`) and the chamfered-corner rule (`bore_mouth_limit(p) > pr.rf - MIN_WALL`, naming `bore_chamfer` and `bore_hex`). The round-profile rules (`bore_d` too large, D-flat range) sit unchanged in the `else` branch and never run under a hex. The shape-independent chamfer-vs-face-width rule and the recess web rule stay outside the pair, applying to every bore shape.
- The two rules' boundaries were measured on the pinned kernel exactly as the plan's `<interfaces>` section pinned them: `bore_hex` 24.15 builds, 24.2 refuses ("its corners (28.12 mm across) must stay 0.4 mm inside the root circle (28.88 mm)"); at the default chamfer, `bore_hex` 23.35 builds, 23.4 refuses with the mirror sentence naming `bore_chamfer` and `bore_hex`.
- `calc.derive()` gains the D-02 warning: when `bore_hex > 0`, it collects every non-zero `bore_d`/`bore_flat` with its value and appends one sentence — `"Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored."` — pluralizing "is"/"are" correctly, and saying nothing when both round fields are 0.
- D-03's chamfer-vs-side probe (Flagged Assumption A4) was re-run inside a test rather than left in planning notes: `bore_hex=0.5` (side 0.375 mm) at `bore_chamfer=3` (ratio 8, the field's maximum) builds cleanly, and the removed volume against the un-chamfered build matches the analytic hex frustum formula within `rel=1e-6`. No chamfer-vs-side rule exists in `check()` because the kernel copes at every allowed size — the absence of a rule is itself the tested claim.
- Every interface prints `calc`'s own sentences: the API's 422 `detail[].msg`/`ctx.fields`, the CLI's `error:`-prefixed stderr and exit 2, and `spur info --bore-hex 6` byte-for-byte equal to `/api/info?bore_hex=6` (including the D-02 warning and field order).
- README.md documents the hex bore: the feature bullet, a `bore_hex` parameter row carrying D-08's commodity-sizes sentence, a `spur export -o hexgear.stl --bore-hex 6` CLI example (run by `test_readme_export_examples_run`, and confirmed to stay out of the closed pre-v0.2 regression corpus), and a sentence in the 422/warnings paragraph. `bore_d`'s help text drops the now-false "0 = solid, no bore" wording; `bore_clearance`'s help text says clearance is added across the hex flats too.

## Task Commits

Each task was committed atomically (one commit per task, per the plan's explicit D-14 instruction for this `tdd="true"` tracer task — tests were written first and confirmed failing before implementation, then both landed in one commit per CLAUDE.md's "one concern per commit"):

1. **Task 1: hex refusals + ignored-field warning** — `6b29c02` (feat) — `calc.check()`'s hex branch, `calc.derive()`'s D-02 warning, and the boundary/skip/parity/probe tests across `test_calc.py`, `test_api.py`, `test_cli.py`, `test_model.py`.
2. **Task 2: README + help text** — `7bbf31e` (docs) — the feature bullet, `bore_hex` row, hex CLI example, `bore_d`/`bore_clearance` help text, and the README example's CLI test.

**Plan metadata:** commit pending (this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md).

## Files Created/Modified

- `src/spur/calc.py` — `check()`'s hex `if`/`elif`/`else` branch (two refusals, measured bound); `derive()`'s D-02 warning
- `src/spur/params.py` — `bore_d`'s help text ("0 = no round bore"); `bore_clearance`'s help text (hex across-flats clause)
- `README.md` — feature bullet, `bore_hex` row, `bore_d`/`bore_clearance` row text, CLI example, 422/warnings paragraph sentence
- `tests/test_calc.py` — 4 new tests (2 boundary refusals, the round-rule skip, the 5-row warning parametrize)
- `tests/test_api.py` — 3 new tests (both 422 shapes, the ignored-field warning + STL preview over HTTP)
- `tests/test_cli.py` — 2 new tests (exit 2, CLI/API parity) + the README hex example extended into the existing test
- `tests/test_model.py` — 2 new tests (both boundary builds, the chamfer-past-the-side probe as a test)

## Decisions Made

- D-03's chamfer bound sits on the root circle (`bore_mouth_limit(p) > pr.rf - MIN_WALL`), not on the hex's side length — see key-decisions above. The probe found the kernel copes with chamfer-vs-side at every allowed size, so no side rule was added; this resolves Flagged Assumption A4 as stated.
- The corner rule and the chamfered-corner rule never stack (`if`/`elif`, not two independent `if`s) — with `bore_chamfer` 0 the mouth equals the corner, so exactly one rule can fire. Resolves Flagged Assumption A5.
- One commit per task rather than separate RED/GREEN commits, per the plan's explicit instruction and CLAUDE.md's "one concern per commit, not micro-commits" — tests were written and confirmed failing (RED) before implementation (GREEN) within each task, evidenced below.

## Deviations from Plan

None — plan executed exactly as written. Every acceptance criterion and verify command in the plan passed unmodified from the plan's literal text (exact grep patterns, exact CLI invocations, exact boundary values).

## TDD Gate Compliance

Task 1 (`type="tracer" tdd="true"`) followed the RED → GREEN cycle:

- **RED:** all four new `tests/test_calc.py` tests, all three new `tests/test_api.py` tests, both new `tests/test_cli.py` tests, and the parametrized `tests/test_calc.py::test_a_hex_bore_warns_about_each_round_field_it_ignores` rows were written and run against the pre-implementation `calc.py` — 12 of 34 hex-scoped tests failed on the expected assertion (the refusal not yet raised, or the warning not yet present), confirming intentional RED, not an import/collection error. The two new `tests/test_model.py` tests passed immediately in RED because they assert the *accepted* side of each boundary, which already built without the new rules — consistent with the plan's own framing ("one step inside builds; the step past it is test_calc's refusal").
- **GREEN:** `calc.check()`'s hex branch and `calc.derive()`'s warning were implemented; all 34 hex-scoped tests, and the full `tests/test_calc.py tests/test_api.py tests/test_cli.py tests/test_model.py tests/regression` scope (211 tests), passed.
- **Commit shape:** per the plan's explicit `<action>` text ("Commit with plain git commit... Commit the five files by name: feat(08-03): ...") and CLAUDE.md's "one concern per commit, not micro-commits", RED and GREEN landed in a single commit (`6b29c02`) rather than separate `test(...)`/`feat(...)` commits. This is a deliberate, plan-directed choice, not a gate violation — `workflow.tdd_mode` is not enabled in `.planning/config.json`, so the mechanical RED/GREEN/REFACTOR commit-pattern gate from `tdd.md` does not apply to this plan.
- **No REFACTOR commit** — the implementation needed no follow-up cleanup after GREEN.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- REQ-hex-bore's warning clause, ROADMAP SC1 (a non-zero `bore_d` alongside `bore_hex` warns) and amended SC2 (`bore_flat` alongside `bore_hex` builds and is named, never a 422) are all observable through the API, the CLI and the README.
- D-03's two rules are in place, measured and tested at both boundaries; the chamfer-vs-side probe is recorded rather than left as a rule.
- 08-04 (build-time sweep) can run against a hex bore whose error states are now fully specified, across the full `bore_hex` range up to the measured refusal boundaries.
- No blockers. No tech debt or ideas filed this plan — no out-of-scope issue surfaced during execution.

## Self-Check: PASSED

Both key files (`src/spur/calc.py`, `README.md`) and all seven modified files found on
disk; both commit hashes (`6b29c02`, `7bbf31e`) found in `git log --oneline --all`;
every plan-level `<verification>` command re-run and green (`make test` on the four
test files + regression, the two CLI refusal invocations, `git diff --exit-code` on
`tests/regression/pre_v0_2.json`); `make verify` green at 328 tests.

---
*Phase: 08-hex-bore*
*Completed: 2026-09-26*
