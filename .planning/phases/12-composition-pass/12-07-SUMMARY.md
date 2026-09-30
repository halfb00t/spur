---
phase: 12-composition-pass
plan: 07
subsystem: testing
tags: [api, cli, ui, parity, composition, d-11, d-14]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-01-SUMMARY.md: the human's binding \"seven\" groups answer (Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb); 12-03-SUMMARY.md: spoke_count's le lowered 40 -> 32; 12-05-SUMMARY.md: tests/composition.py's BORE_REFUSALS/CUTOUT_REFUSALS tables"
provides:
  - "README.md's CLI block: the composed README link (D-14), every v0.2 family on one 19-tooth gear, run by tests/test_cli.py::test_readme_export_examples_run"
  - "tests/test_cli.py: COMPOSED, _flags(), test_cli_and_api_print_the_same_composed_document, test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order, test_every_refusal_reads_the_same_on_the_api_and_the_cli (23 rows)"
  - "tests/test_api.py: test_the_shareable_link_round_trips_every_field_through_generic_code"
  - "REQ-three-interfaces-extended proven generically for every v0.2 field: one field walk across the schema, the form's source and the CLI parser, in the one pinned group order"
affects: [12-08-cli-md-exit-contract, 12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 3351
  tasks: 3
  commits: 3
  plan_head_before: 9f557b29a6f91a3f588e6d8ba82325cc2e89e960
  plan_head_after: 3fb99017823168f0a2092381af26a18dd1572723

# Tech tracking
tech-stack:
  added: []
  patterns: ["A byte-for-byte CLI/API document comparison reads the API's compact JSON re-indented with json.dumps(indent=2, ensure_ascii=False) -- the CLI's own model_dump_json(indent=2) and that re-indented form are equal (verified this session), so the comparison proves value AND key-order identity without asserting the CLI serialises like the API's raw bytes (which it never will, since the API serves compact JSON)."]

key-files:
  created: []
  modified:
    - README.md
    - tests/test_cli.py
    - tests/test_api.py

key-decisions:
  - "D-11's group count pinned as **seven**, from 12-01-SUMMARY.md's binding human answer: Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb, in that order; recess_sides lives inside Recess, checked as enum (not step). Verified this session directly against the live /api/schema: 30 properties, group first-appearance order exactly this list, no group reappearing after another starts."
  - "Task 3's composed-refusal params ({tip_chamfer: 1.75, recess_sides: \"top\", **refusal}) were verified against check() directly, for all 23 refusals, before writing the test: neither family key appears in 12-05's TWO_REFUSALS or DATUM_ROWS tables, and a standalone probe this session confirmed zero mismatches between the refusal alone and composed with both families together (12-05 only proved each family individually, never both switched on at once)."
  - "The README's composed link is documented space-separated (--flag value, matching every other README CLI example); tests/test_cli.py's COMPOSED/_flags() build the equivalent --flag=value form to run it, and test_readme_export_examples_run asserts the space-separated documented form is a literal substring of README.md, not the run form."

patterns-established: []

requirements-completed: []  # REQ-three-interfaces-extended is shared with 12-08 and 12-09 per the shared-ID gate (#2388) -- `requirements.ready-ids` returned 0/1 ready this session (12-08 and 12-09 have no SUMMARY yet); marks complete only once 12-09 (the last declaring plan) finishes.

coverage:
  - id: D1
    description: "README.md's CLI block carries the composed example (every v0.2 family on: keyed round bore, spoke arms, both recesses, tip chamfer) and test_readme_export_examples_run runs it, asserting the README holds the exact documented line and that the export writes a file over 1000 bytes with no warning; the composed set stays out of tests/regression's corpus (07 D-05, post-v0.2 sets excluded)"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
      - kind: other
        ref: "grep -c 'everything' tests/regression/corpus.py == 0; git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json == clean"
        status: pass
    human_judgment: false
  - id: D2
    description: "The composed link and the empty link print the identical document on spur info and /api/info, byte for byte once the API's compact JSON is re-indented (json.dumps(indent=2, ensure_ascii=False)) to match the CLI's own indent=2, in DerivedDimensions key order; on the composed link every family's own number is non-null and warnings is empty"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_composed_document"
        status: pass
    human_judgment: false
  - id: D3
    description: "One model-driven test walks GearParams.model_fields: /api/schema lists every field in declaration order with a group, title and unit, a step on every non-enum field and the enum on recess_sides; the seven groups (Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb) appear once each, contiguously, in the human-confirmed order; spur info --help lists one --name-with-dashes flag per field in the same order"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order"
        status: pass
    human_judgment: false
  - id: D4
    description: "The shareable-URL round trip is proven statically from src/spur/static/app.js: the form is built from every schema property, the hash is read into every field, the query and hash are written from every field that differs from its default, the copy-link button copies location.href, and no GearParams field name appears as a quoted literal or a .field property access outside the DIMS rows"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_the_shareable_link_round_trips_every_field_through_generic_code"
        status: pass
    human_judgment: false
  - id: D5
    description: "Each of the 23 locked refusals, composed with the tip chamfer and a single-sided recess, gives the same sentence on the API's 422 (detail.msg, ctx.fields) and on the CLI's exit 2 (error: <sentence> on stderr), and that sentence is calc's own for the refusal alone"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_every_refusal_reads_the_same_on_the_api_and_the_cli (23 rows)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The browser itself is checked by hand at gsd-verify-work against the checklist this plan produced (below)"
    verification: []
    human_judgment: true
    rationale: "Visual/interactive form behaviour (fieldset order and count as rendered, a link loading into the live form, the copy-link round trip, a live 422 marking invalid fields) is not something the static app.js read or the API/CLI parity tests can observe -- a human must actually open the page."

# Metrics
duration: ~55min
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 07: Interface Parity (Schema, Form, CLI, Refusals) Summary

**One model-driven test walks all 30 GearParams fields across `/api/schema`, the CLI parser and `app.js`'s hash-to-form-to-query path with no per-field code; the README's new composed link (keyed bore + spokes + both recesses + tip chamfer) prints byte-identical documents on `spur info` and `/api/info`; and all 23 locked refusals read the same sentence on the API's 422 and the CLI's exit 2 when composed with two other families at once.**

## Performance

- **Duration:** ~55 min (four full `make verify` runs at ~3.5 min each dominate; edits and targeted test runs are seconds each)
- **Completed:** 2026-09-30T12:33Z (approx, this session)
- **Tasks:** 3 (1 tracer, 2 auto)
- **Files modified:** 3 (`README.md`, `tests/test_cli.py`, `tests/test_api.py`)

## Accomplishments

- README.md's CLI block gained the composed example (D-14): `spur export -o everything.stl --bore-flat 0 --keyway-width 3 --keyway-depth 1.4 --spoke-count 4 --spoke-width 2 --hub-d 13.2 --rim-wall 1 --spoke-fillet 1 --tip-chamfer 0.4` -- every v0.2 family on one gear (a keyed round bore, four spoke arms, both face recesses at their defaults, and a tooth-tip chamfer). `test_readme_export_examples_run` now asserts this exact line is present in README.md and runs it, producing a 1.57 MiB STL with no warning.
- `test_cli_and_api_print_the_same_composed_document`: the composed link and the empty link (`{}`, edge: empty) print byte-identical documents on `spur info` and `/api/info`, once the API's compact JSON is re-indented with `json.dumps(indent=2, ensure_ascii=False)` to match the CLI's own `indent=2` -- confirmed equal by direct comparison this session, not assumed (A1's flagged assumption, resolved). On the composed link, `warnings == []` and all eleven family-specific `DerivedDimensions` fields (`tip_chamfer_effective`, `bore_effective`, `keyway_floor_to_wall`, `keyway_width_effective`, `recess_id`, `recess_od`, `recess_fillet`, `web`, `cutout_hub_wall`, `cutout_rim_wall`, `spoke_fillet_effective`) are non-null.
- `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`: walks `GearParams.model_fields` (never the API's or CLI's own list) across `/api/schema` (30 properties, same order, each with `group`/`title`/`unit`, a `step` on every field but `recess_sides`, whose `enum` matches the model's `Literal` args) and `spur info --help`'s flag list (one `--name-with-dashes` per field, same order). The seven groups collapse to exactly `Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb`, in that order, each a contiguous run -- 12-01-SUMMARY.md's binding human answer ("seven"), re-verified live against the schema this session.
- `test_the_shareable_link_round_trips_every_field_through_generic_code` (tests/test_api.py): reads `src/spur/static/app.js` and asserts the eight generic snippets the hash -> form -> query -> hash round trip rests on are present verbatim, then proves no `GearParams` field name appears outside the `DIMS` block as a complete quoted string literal or a `.field` property access -- including an explicit check that the pattern does not false-positive on the `'#mate-teeth'` DOM id (the known near-miss named in `<interfaces>`).
- `test_every_refusal_reads_the_same_on_the_api_and_the_cli`, parametrized over all 23 rows of `tests/composition.py`'s `BORE_REFUSALS`/`CUTOUT_REFUSALS` (ids the refusal ids): each refusal, composed with `tip_chamfer=1.75` and `recess_sides="top"` together, gives the identical `check()` sentence and fields on the API's 422 (`detail[0].msg`, `detail[0].ctx.fields`) and the CLI's exit 2 (`error: <sentence>` on stderr, stripped). Verified independently against `check()` before writing the test: composing both families together (not just one at a time, which is all 12-05 proved at the calc level) changes nothing for any of the 23 rows.
- `make verify`: 906 passed (full suite, after all three commits), up from 880 before this plan -- 26 new test items (1 + 2 + 23), +1.22 s of wall time, comfortably inside D-10's phase-wide 30 s budget. `make lint typecheck lint-imports` clean throughout; the pre-v0.2 fixture is byte-unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer -- the composed README link through the CLI export, spur info and /api/info** - `af42087` (test)
2. **Task 2: Every field reaches the schema, the form and the CLI in one order; the URL round trip is generic** - `415a9ae` (test)
3. **Task 3: Every locked refusal reads the same on the API's 422 and the CLI's exit 2** - `3fb9901` (test)

**Plan metadata:** committed separately (see below)

## Files Created/Modified

- `README.md` -- the composed CLI example added to the "## CLI" block, after the honeycomb line
- `tests/test_cli.py` -- `COMPOSED`, `_flags()`, `test_cli_and_api_print_the_same_composed_document`, `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`, `test_every_refusal_reads_the_same_on_the_api_and_the_cli` (23 parametrized rows), and an extension to `test_readme_export_examples_run` for the composed link
- `tests/test_api.py` -- `test_the_shareable_link_round_trips_every_field_through_generic_code`

## Decisions Made

See `key-decisions` in the frontmatter: the seven-group order pinned and re-verified live; the composed-refusal params independently verified against `check()` for all 23 rows before the test was written (both extra families together, not just one at a time); the README's documented (space-separated) vs. run (`=`-joined) flag forms kept distinct in the extended `test_readme_export_examples_run` assertion.

## Deviations from Plan

None -- plan executed exactly as written. One environmental note, not a deviation: each of the three commits' pre-commit `make verify` hook (run against the staged snapshot, ~3.5 min) coincided once with a concurrent write to `.planning/state.json` by the orchestrator's own background process, which pre-commit's stock file-modification detector flagged as "files were modified by this hook" and aborted the commit (Task 2's first attempt). `make verify` itself had already passed (883/883) inside that run; nothing in this plan's own files was affected, and a plain retry of the identical `git commit` succeeded. `.planning/state.json` was never staged or touched by this plan's commits.

## Issues Encountered

- Task 2's first commit attempt failed with pre-commit's "files were modified by this hook" (see Deviations above) -- not a real verification failure (the hook's own `make verify` had passed 883/883); a retry of the same `git commit` command succeeded once the concurrent `.planning/state.json` write settled.

## User Setup Required

None -- no external service configuration required.

## Manual Browser Checklist (for gsd-verify-work, D-11)

Copied verbatim from this plan's `<verification>` section, to run with `make serve`:

1. The form shows the seven fieldsets (or the count the human confirmed at 12-01) in order: Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb.
2. Open `http://127.0.0.1:8000/#bore_flat=0&keyway_width=3&keyway_depth=1.4&spoke_count=4&spoke_width=2&hub_d=13.2&rim_wall=1&spoke_fillet=1&tip_chamfer=0.4`: every one of the nine fields shows the link's value, the preview builds, the dimensions list shows the tip chamfer, keyway, recess, both cutout walls and the spoke fillet, and no warning appears.
3. Click "copy link", open the copied link in a new tab: the same nine values load and the same numbers print.
4. Set `bore_hex` to 6 in that tab: a 422 sentence naming the keyway and the hex appears and the bore fields are marked.

## Next Phase Readiness

- `REQ-three-interfaces-extended` stays open in `REQUIREMENTS.md` (shared with 12-08 and 12-09 per the shared-ID gate, #2388) -- `requirements.ready-ids` reported 0/1 this session (12-08 and 12-09 have no SUMMARY yet); marks complete only once 12-09 (the last declaring plan) finishes.
- 12-08 (the `cli.md` exit-code fix, D-13) can proceed independently -- this plan asserted the CLI's real exit behaviour (`SystemExit(2)` for parameter refusals) directly against `src/spur/cli.py`, not against `cli.md`'s current text, so it carries no dependency on 12-08's doc fix landing first.
- `make verify`: 906 passed (full suite, after all three commits) -- green, no regressions; `make lint typecheck lint-imports` and the plan's own `<verification>` block all pass; the pre-v0.2 fixture is byte-unchanged.
- No blockers.

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `README.md` (modified, composed CLI example added)
- FOUND: `tests/test_cli.py` (modified, `COMPOSED`/`_flags`, 3 new test functions incl. 23 parametrized rows, `test_readme_export_examples_run` extended)
- FOUND: `tests/test_api.py` (modified, 1 new test function)
- FOUND: commit `af42087` in `git log --oneline --all`
- FOUND: commit `415a9ae` in `git log --oneline --all`
- FOUND: commit `3fb9901` in `git log --oneline --all`
- Re-ran all task acceptance criteria: `grep -c 'everything' tests/regression/corpus.py` = 0; `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` = clean; `test_cli_and_api_print_the_same_composed_document`/`test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`/`test_the_shareable_link_round_trips_every_field_through_generic_code`/`from composition import` greps = 1 each; refusal-row collect count = 23; both post-commit `^src/` greps (Tasks 2 and 3) = 0 -- all PASS
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py tests/regression -q"` -- 183 passed; `make lint typecheck lint-imports` -- all clean
- `git rev-list --count 9f557b2..HEAD` = 3, matching `commits: 3` above
