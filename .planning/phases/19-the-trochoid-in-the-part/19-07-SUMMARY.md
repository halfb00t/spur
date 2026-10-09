---
phase: 19-the-trochoid-in-the-part
plan: 07
subsystem: testing
tags: [trochoid, root_shape, cli, api, readme, three-interface-parity, exit-codes, build-error]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-04's root_shape end to end and the generated --root-shape flag; 19-05's four root guards and their "modelling defect ... root_shape" sentences; 19-06's root_form_d, root_waist and the restated undercut sentence; 19-08's TROCHOID_THICKNESS in tests/composition.py
provides:
  - "the human's answer to the SC5 exit-status conflict, recorded verbatim: exit-documented"
  - "tests/test_cli.py: the four trochoid documents byte-identical on spur info and /api/info (default, undercut-17, nothing-radial-42, capped-12), seven unknown root_shape spellings refused on both front ends, both valid values and the omitted parameter, a root guard's BuildError routed as decided, the README example found verbatim and run"
  - "tests/test_api.py: the root_shape link served end to end (schema, info, model download)"
  - "README.md: root_fillet's two meanings, the root_shape row after tip_chamfer, a runnable spur export -o hob-root.stl --root-shape trochoid example"
affects: [19-09, 19-10, 19-11]

# Actuals (#2632): chars/4 over the added lines of the three changed files, 63cc041^..63cc041.
actuals:
  tokens: 3250
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "a parity row table whose expectations are captured sentences typed in once (L33), the shared one imported from tests/composition.py instead of copied"
    - "a /api/model call from a test that has no lifespan overrides build_backend with the in-process export through monkeypatch.setitem, as tests/test_api.py does module-wide"
    - "a tooth count for a cache-dodging build is chosen where the hob root applies (below 27 teeth at the default module and angle), or the request is ignored and the two parts are the same"

key-files:
  created: []
  modified:
    - tests/test_cli.py
    - tests/test_api.py
    - README.md

key-decisions:
  - "exit-documented (the human, 2026-10-09): keep the CLI contract as shipped; ROADMAP SC5's 'exit 2' is read as the parameter refusals; a root guard's BuildError exits 1 with its sentence (D-14, cli.md 'Errors')"
  - "src/spur/cli.py, docs/architecture/cli.md and ROADMAP's SC5 sentence were not edited; 19-10 records the reading in L38"

patterns-established:
  - "A refusal that is a defect in spur takes the BuildError route on both front ends (422 build_error / exit 1); a refusal that is a conflict in the user's parameters takes the parameter route (422 with a loc / argparse exit 2)"

requirements-completed: [REQ-cutter-tip-radius-settable]  # declared by this plan: REQ-root-mode-decided, REQ-trochoid-composes-and-is-priced, REQ-cutter-tip-radius-settable; requirements.ready-ids (#2388) answered 1/3 ready after this SUMMARY: REQ-cutter-tip-radius-settable (19-07 is its last declaring plan) was marked complete; the other two are also declared by siblings with no SUMMARY yet (19-09, 19-10, 19-11) and were left for their last declaring plan

coverage:
  - id: D1
    description: "The four trochoid documents (default; 17 teeth undercut; 42 teeth with nothing radial to replace; 12 teeth with a trimmed tip radius) print byte for byte on spur info what /api/info serves once re-indented (12-07's reading), keys in DerivedDimensions order; the hob root prints root_thickness and root_gap null and root_form_d 30.558 / 15.975 / 11.294, the 42-tooth row prints the radial 2.065 and 0.889 with the refusal sentence, the 12-tooth row prints root_fillet 0.471 with the cap sentence"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_trochoid_documents (4 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "An unknown root shape is refused the same way everywhere: false, Trochoid, TROCHOID, hob, empty, ' trochoid' and 'trochoid ' exit 2 from argparse naming the choices and are a 422 whose loc ends in root_shape; radial and trochoid are accepted; an omitted root_shape is the radial document on both front ends"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_an_unknown_root_shape_exits_2_on_the_cli_and_is_a_422_on_the_api (7 passed)"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_both_root_shapes_are_accepted_and_omitting_it_reads_radial"
        status: pass
    human_judgment: false
  - id: D3
    description: "A root guard's BuildError reads the same on both front ends: /api/model.stl is a 422 of type build_error carrying 'modelling defect' and 'root_shape' and never 'try smaller'; spur export stops with SystemExit('error: <the same sentence>'), writes nothing, exits 1 (the human's exit-documented answer)"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_a_root_guard_build_error_reads_the_same_on_the_api_and_the_cli"
        status: pass
    human_judgment: false
  - id: D4
    description: "The root_shape link is served end to end: schema (group Teeth, title Root shape, enum radial/trochoid, default radial, no step), /api/info root_thickness null and root_form_d 30.558, the form omitting a default value from its query, and a 23-tooth model download that differs from the radial one under the same download name"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_a_root_shape_link_is_served_with_the_root_it_cut"
        status: pass
    human_judgment: false
  - id: D5
    description: "README.md documents root_fillet's two meanings and the root_shape row, and carries one runnable hob-root export command that test_readme_export_examples_run finds verbatim and runs, its one stderr warning the captured thickness sentence"
    requirement: REQ-cutter-tip-radius-settable
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
    human_judgment: true
    rationale: "Whether the README prose for the two root_fillet meanings and the root_shape row reads true and clear is a reviewer's judgment; the test proves the command is present and runs, not the wording."

duration: "about 25 min for this continuation (the first executor's checkpoint wait is not counted)"
completed: 2026-10-09
status: complete
plan_head_before: 012236698b59063eb40f369065103ffc5e60c589
plan_head_after: 63cc0410226df83b47253ac25a2b71cf74c5f06b
commits: 1
---

# Phase 19 Plan 07: The hob-root field reads the same on the API, the CLI and the README Summary

**The four trochoid documents are byte-identical on `spur info` and `/api/info`, seven spellings of an unknown `root_shape` are refused with exit 2 / 422, a root guard's `BuildError` is a 422 `build_error` on the API and `error: ...` / exit 1 on the CLI as the human decided (`exit-documented`), and the README carries both meanings of `root_fillet`, the `root_shape` row and a runnable hob-root export; `src/spur/cli.py`, `cli.md` and ROADMAP were not touched.**

## Performance

- **Duration:** about 25 min for this continuation, of which the one `make verify` is 3 min 24 s (05:33:00Z to 05:36:24Z). The first executor paused at Task 1 before writing anything and its time is not counted.
- **Completed:** 2026-10-09T05:40Z (SUMMARY write)
- **Tasks:** 2 (Task 1 the checkpoint, answered; Task 2 the tests and README)
- **Files modified:** 3 (`tests/test_cli.py`, `tests/test_api.py`, `README.md`)

## The human's answer (Task 1)

The two texts the human settled between: ROADMAP Phase 19 SC5 says every new refusal routes identically to a `422` and to exit 2; `docs/architecture/cli.md` "Errors" and D-14 (amended 2026-09-28) say a parameter error exits 2 and every `BuildError` exits 1 (`SystemExit("error: ...")`). This phase adds no `check()` refusal; its two new refusal kinds are the enum (422 / argparse exit 2) and the root guards (422 `build_error` / exit 1).

The human's reply, verbatim, on 2026-10-09: **`exit-documented`**

That is option 1 of the checkpoint, chosen by the human directly. The reading it implies:

- an unknown `root_shape` value is `422` with `loc` naming `root_shape` / argparse exit 2;
- a root guard's `BuildError` (`_guard_junction`, `_guard_spacing`, `_guard_annulus`, `_guard_area`) is `422 build_error` carrying the guard's "modelling defect ... root_shape" sentence / `SystemExit("error: ...")`, exit 1;
- SC5's "exit 2" is read as meaning the parameter refusals;
- `src/spur/cli.py`, `docs/architecture/cli.md` and ROADMAP's SC5 sentence are not edited.

**For 19-10:** L38 must record that SC5's "exit 2" means the parameter refusals, and that a root guard's `BuildError` exits 1 under D-14. SC5's sentence stays literally false for the guard (the option's stated cost); L38 is where the reading is written down.

## Accomplishments

- **Parity (`63cc041`).** `test_cli_and_api_print_the_same_trochoid_documents` runs four rows (`default`, `undercut-17`, `nothing-radial-42`, `capped-12`): the CLI's stdout equals `json.dumps(<the /api/info JSON>, indent=2, ensure_ascii=False)`, its keys are `DerivedDimensions.model_fields` in order, and per-row asserts pin what differs in kind. Captured on 2026-10-09 and typed in (L33), the thickness sentence imported from `tests/composition.py`'s `TROCHOID_THICKNESS` rather than copied:

  | Row | root_thickness / root_gap | root_form_d | root_waist | root_fillet | warnings |
  |---|---|---|---|---|---|
  | default | null / null | 30.558 | 3.303 | 0.5 | thickness |
  | undercut-17 (m 1, 20 deg, 0.38, bore off, recess none) | null / null | 15.975 | 1.62 | 0.38 | thickness, "Below 17.1 teeth ... 0.006 or more" |
  | nothing-radial-42 (backlash 0, 0.38) | 2.065 / 0.889 | null | null | 0.38 | "No radial root to replace ... 19.734 ... 19.750 ... ignored." only |
  | capped-12 (backlash 0, asked 3.0) | null / null | 11.294 | 1.586 | 0.471 | cap, thickness, "Below 16.1 teeth ... 0.239" |

- **Refusals.** `test_an_unknown_root_shape_exits_2_on_the_cli_and_is_a_422_on_the_api` runs seven spellings (`false`, `Trochoid`, `TROCHOID`, `hob`, empty, leading space, trailing space): argparse exit 2 with "invalid choice" and both valid names after "choose from"; the API a 422 whose `loc` ends in `root_shape`. The enum match is exact and case-sensitive on both (T-19-14), an empty value is refused, never read as the default. `test_both_root_shapes_are_accepted_and_omitting_it_reads_radial` shows `radial` and `trochoid` read the same document on both front ends and an omitted parameter is the radial one.
- **The guard's routing, as decided.** `ROOT_AREA_REL_MAX` patched to 0.0 trips `_guard_area`. `/api/model.stl?teeth=26&root_shape=trochoid&quality=preview` is a 422 `build_error` carrying "modelling defect" and "root_shape" and no "try smaller"; `spur export` raises `SystemExit` whose code is the string `error: <the same sentence>` (exit 1), and the file is not written. A mutation (CLI exit 2 for a `BuildError`) turned this test red; `cli.py` was restored and `git diff --exit-code src/spur/cli.py` read clean.
- **The API link.** `test_a_root_shape_link_is_served_with_the_root_it_cut`: `/api/schema` `root_shape` has group `Teeth`, title `Root shape`, enum `["radial", "trochoid"]`, default `radial`, no `step`; `/api/info?root_shape=trochoid` is 200 with `root_thickness` null and `root_form_d` 30.558; a 23-tooth preview download is 200, differs from the radial 23-tooth part, and has the same `Content-Disposition` (`spur_z23_m1.75_pa25.stl`: the slug ignores root_shape, RESEARCH Open Question 6, filed as an idea by 19-11). The form's omission of a default is pinned by the token in `gearQuery()` (the runtime has no Node, so the existing source-token style of `test_the_shareable_link_round_trips_every_field_through_generic_code`).
- **README.** `root_fillet` row rewritten to both meanings; `| \`root_shape\` | radial | ... |` after `tip_chamfer` (`radial` the shipped default; `trochoid` the hob-cut root, ignored and warned where the base circle is not above the root circle; `/api/info` then prints `root_form_d` and `root_waist` and no root-circle thickness); `spur export -o hob-root.stl --root-shape trochoid` in the CLI block. `test_readme_export_examples_run` asserts the line present and runs it: the file is written and stderr carries exactly one `warning:` line, the thickness sentence.

## Task Commits

1. **Task 1: the exit-status decision** - no commit; the answer is recorded above (a checkpoint writes no code).
2. **Task 2: parity, refusals, guard routing, API link, README** - `63cc041` (test)

**Plan metadata:** the docs commits that carry this SUMMARY, STATE.md, ROADMAP.md and `.planning/state.json`.

`commits: 1` counts only the commit titled `(19-07)`. A raw `git rev-list --count 0122366..HEAD` from `plan_head_before` reads 5 at SUMMARY write: it also counts sibling 19-08's four commits (`2be041e`, `6607f69`, `b78e47e`, `2da4236`), which landed while this plan waited at its checkpoint; they are not this plan's, as 19-02 and 19-03 counted theirs.

## Decisions Made

See `key-decisions`: the human chose `exit-documented`; nothing in `cli.py`, `cli.md` or ROADMAP moved; 19-10 writes the reading into L38.

## Deviations from Plan

### Plan-literal items that did not apply as written

**1. Tooth counts 57 and 59 would have tested nothing.** The first draft used the plan's "a tooth count no other test downloads" with 57 (the link test) and 59 (the guard test). At those counts the base circle is above the root circle (from 27 teeth up at the default module 1.75 and 25 degrees) so the trochoid request is ignored: the two downloads were byte-equal and the patched guard never ran. The tests use **23** (the link test, root form diameter 37.351) and **26** (the guard test, 42.49), both unused by any other test and both with the hob root applied; the docstrings say why.

**2. The guard test overrides the build backend.** `tests/test_cli.py` has no lifespan override, so `/api/model.stl` there raised "Build pool not started". The test installs the same in-process backend `tests/test_api.py` uses (`monkeypatch.setitem` on `app.dependency_overrides`, undone at teardown).

**3. argparse prints its choices as `(choose from radial, trochoid)` on 3.12** (`'radial', 'trochoid'` on later versions). The first draft asserted the quoted form; the test now reads the text after "choose from" and looks for both names.

**4. TDD ceremony.** Task 2 is `tdd="true"` but the plan is `type: execute` and the behaviour under test (19-04 to 19-06) already existed, so there is no separate RED commit. The README half did have a real RED: with the new assertion in `test_readme_export_examples_run` and no README line, the run failed on `assert "spur export -o hob-root.stl --root-shape trochoid" in readme`; the README edit turned it green; both went into the plan's single commit. The guard test's teeth are shown by the mutation above. The nine failures of the first run were test-authoring mistakes (items 1 to 3 and a download-name assertion written as `23t` against the real `spur_z23_m1.75_pa25.stl`), not behaviour.

**5. Commit attribution line.** Commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives, as 19-05, 19-06 and 19-08 did. The dispatch text named `Claude Fable 5.1`; `CLAUDE.md` names neither.

**Total deviations:** 0 auto-fixed, 5 plan-literal items. **Impact on plan:** none on behaviour; the production code, `cli.py`, `cli.md` and ROADMAP are untouched.

## Issues Encountered

- **Gate result:** `make verify` exit 0, **`1209 passed in 203.69s (0:03:23)`**, coverage **97.90 %** (floor 96); ruff, mypy `--strict` (43 source files), 5 import contracts kept, unfinished-work scan clean. 14 tests were added to 19-08's 1195 (4 parity rows, 7 refusal spellings, the two-valid-values test, the guard test, the API link test). Host 1-minute load was 6.55 at the start. The 203 s is the host-load-dependent figure 19-08 recorded (202 s); this plan's tests are cheap (the one builds are two preview parts and a failing build), so nothing here moves L34's question, which stays 19-09's.
- **No `ReentrantCallError` or other flake appeared** in the full gate (the log was searched, zero matches) or the commit hook, so the resource-tracker debt item's trigger did not fire and nothing was kept under `investigation/`.
- **Scope.** 19-08's files (`tests/composition.py`, `tests/test_calc.py`, `tests/test_model.py`) were built on and not touched; `tests/test_cli.py` still imports `BORE_REFUSALS` and `CUTOUT_REFUSALS` unchanged (23 refusal tests pass).

## Known Stubs

None. No placeholder values, empty data flows or TODO markers were added.

## Threat Flags

None. T-19-14 (a case or whitespace variant normalised into a value the user did not send) is mitigated: seven spellings are pinned on both front ends. T-19-15 (the guard's text on a 422) is accepted as planned: the sentence names the check and the remedy only, and the catch-all's "try smaller" is asserted absent. No new network, auth or file surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-09 prices the gate (203 s here, load dependent) against L34 and swaps the bench's `trochoid_outline`; nothing from this plan changes its numbers.
- 19-10 writes L38 and must carry the reading of SC5 given above (parameter refusals exit 2; a root guard's `BuildError` exits 1 under D-14); it also owns `strategy.md`.
- 19-11 files the download-name idea (the slug ignores root_shape; the link test pins today's behaviour and will need the edit if the idea is taken).
- Files filed: no debt or idea item was filed by this plan.

## Self-Check: PASSED

- Files: `tests/test_cli.py`, `tests/test_api.py`, `README.md` exist and carry `def test_cli_and_api_print_the_same_trochoid_documents(`, `def test_a_root_shape_link_is_served_with_the_root_it_cut(` and `| \`root_shape\` |`; this SUMMARY is at `.planning/phases/19-the-trochoid-in-the-part/19-07-SUMMARY.md`.
- Commit `63cc041` is an ancestor of HEAD; `git rev-list --count 0122366..HEAD` read 5, of which one is titled `(19-07)`.
- Acceptance: the `parity tests and README rows present` line and the `SC1 holds` line printed; the 16 targeted tests passed; `git diff` over `src/`, `docs/architecture/cli.md` and `.planning/ROADMAP.md` was empty after the task commit; `make verify` exit 0, `1209 passed`.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
