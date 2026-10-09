---
phase: 19-the-trochoid-in-the-part
plan: 04
subsystem: geometry
tags: [cadquery, trochoid, root_shape, hob-root, pydantic, derive, oracle, kernel-tier, tracer]

requires:
  - phase: 18-trochoid-maths-proved
    provides: RootCurve / root_mode / the swept-cutter oracle tests/trochoid_oracle.clearance
  - phase: 19-the-trochoid-in-the-part
    provides: 19-01's trochoid_outline and root-edge selector (moved here), 19-02's adopted kernel bar, D-02 confirmation and waist/guard bars
provides:
  - "GearParams.root_shape Literal radial/trochoid (default radial), group Teeth directly after tip_chamfer; generated --root-shape flag, schema enum, form select"
  - "root_fillet read as the hob's tip radius under the trochoid root; the printed root_fillet is the radius cut (rm.cutter.rho)"
  - "RootMode.curve, spline_start(pr, fillet, curve), tip_chamfer_limit(p, rm) / tip_chamfer_effective(p, rm): one root_mode call per consumer"
  - "model._trochoid_outline / _outline(curve) / _gear_blank(curve): six side faces per tooth, junction from one Vector"
  - "DerivedDimensions.root_thickness / root_gap as float | None (still required), null with one sentence under the hob root"
  - "tests/test_model.py KERNEL_BAR_PER_MODULE = 2e-3 and the kernel-tier proof: seven rows, tripwire, root_d in both modes, rb = rf boundary, same-link twice, cache key, generator kept out of model.py"
affects: [19-05, 19-06, 19-07, 19-08, 19-09, 19-10]

# Actuals (#2632): chars/4 over the added lines of the eight changed files, da07882..ad8c51a.
actuals:
  tokens: 7750
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "one root_mode call per consumer, the curve carried on RootMode: derive, model._build and tip_chamfer_limit cannot name different roots (PITFALLS 1)"
    - "a field-walk exemption derived from get_origin(annotation) is Literal, pinned in model order, instead of a hard-coded name"
    - "a source test with its own tripwire keeps a vendor-facing module free of a generator's names"

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - src/spur/model.py
    - tests/test_trochoid.py
    - tests/test_model.py
    - tests/test_cli.py
    - tests/test_api.py
    - tests/test_calc.py

key-decisions:
  - "KERNEL_BAR_PER_MODULE = 2e-3 written into tests/test_model.py exactly as adopted at 19-02 (10.9x the worst whole-product spline error 1.8431e-4 per module; tripwire 5.5x over); not re-decided"
  - "Under a trochoid mode the shipped undercut sentence is silenced (kept for a refused request that builds the radial root); 19-06 restates it for the cutter that cut the part"
  - "_chamfer_tips still reads tip_chamfer_effective(p), which asks root_mode a second time with identical inputs inside one build, as the plan specified: passing rm down would break the existing monkeypatch test that replaces tip_chamfer_effective with a one-argument lambda"

patterns-established:
  - "Kernel-tier rows read the oracle at 401 positions per root edge with the tip radius derive() printed, never 41 (19-02: 41 can sit 28 percent low)"
  - "A tripwire row sits on a module-1 gear (the 0.05 mm shift reads 0.66x of the bar on module 10)"

requirements-completed: []  # REQ-root-mode-decided, REQ-outline-consumes-root-curve, REQ-derived-numbers-honest-under-trochoid, REQ-cutter-tip-radius-settable are declared here and by sibling plans (19-05, 19-06, 19-07, 19-10, 19-11) with no SUMMARY yet: the #2388 shared-ID gate leaves them for the last declaring plan; this plan satisfies them in part; nothing marked

coverage:
  - id: D1
    description: "The default gear asked for the hob root end to end: spur info --root-shape trochoid and GET /api/info?root_shape=trochoid print the same document (null root_thickness and root_gap, root_fillet 0.5, one warning), and build() returns one valid solid with 38 fewer faces and 114 fewer edges than the default part (134 / 376 against 172 / 490)"
    requirement: REQ-root-mode-decided
    verification:
      - kind: integration
        ref: ".venv/bin/spur info --root-shape trochoid | python -c ... (prints 'hob root end to end on the CLI and the API')"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_default_gear_asked_for_the_hob_root_prints_its_numbers_and_no_radial_ones"
        status: pass
    human_judgment: false
  - id: D2
    description: "No number or sentence for a radial-flank root is printed beside a hob-cut root: root_thickness and root_gap null, no gap-cap sentence, no lead-in chord sentence, no undercut sentence that says the model uses a radial root; a request refused for nothing radial to replace prints the radial thickness, gap and fillet with the refusal sentence"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_trochoid_request_with_nothing_radial_to_replace_prints_the_radial_numbers_and_says_so"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_default_gear_asked_for_the_hob_root_prints_its_numbers_and_no_radial_ones"
        status: pass
    human_judgment: false
  - id: D3
    description: "The root_shape field is a plain Literal reaching the schema (enum, default radial), the form and the CLI (--root-shape choices) from the model, directly after tip_chamfer; the field walk's exemption is every Literal field read from the model and pinned equal to [root_shape, recess_sides]; a link spelling the default equals one omitting it"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_link_that_spells_the_default_root_shape_is_the_link_that_omits_it"
        status: pass
    human_judgment: false
  - id: D4
    description: "The built hob root is the oracle's root: on the seven rows 19-02 measured, tooth 0's root splines read within 2e-3 x module at 401 positions per edge with the printed tip radius, and the module-1 10-tooth row read 0.05 mm off the printed radius reads over the bar (1.1039e-2 mm, 5.5x)"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_built_root_is_the_oracle_s_root_on_every_kernel_row"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_kernel_tier_proof_fails_when_the_printed_tip_radius_is_off_by_0_05_mm"
        status: pass
    human_judgment: false
  - id: D5
    description: "root_d is the root circle in both modes, the rb = rf boundary builds the radial part at 42 teeth and the hob root at 41, the same trochoid link builds the same solid twice, a radial and a trochoid request never share a cached solid, and the generator's names never appear in model.py"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_root_d_is_the_root_circle_in_both_root_modes"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_nothing_radial_to_replace_builds_the_radial_part"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_same_trochoid_link_builds_the_same_solid_twice"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_a_radial_and_a_trochoid_request_never_share_a_cached_solid"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_trochoid_generator_never_enters_the_model_module"
        status: pass
    human_judgment: false
  - id: D6
    description: "No link that omits root_shape moved: tests/regression/pre_v0_2.json byte-identical to the phase base and plan start, its 86 replay and provenance tests pass unmodified, all 44 records read radial / not requested with no curve and no warning through root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)"
    requirement: REQ-root-mode-decided
    verification:
      - kind: unit
        ref: "tests/regression (86 passed)"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_every_pre_v0_2_record_reads_radial_because_nobody_asked"
        status: pass
      - kind: other
        ref: "SC1 check (prints 'SC1 holds')"
        status: pass
    human_judgment: false
  - id: D7
    description: "root_fillet in trochoid mode is the hob's tip radius, cut and printed as one number (rm.cutter.rho); a request over the cap is trimmed with the cap sentence from root_warnings"
    requirement: REQ-cutter-tip-radius-settable
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_built_root_is_the_oracle_s_root_on_every_kernel_row[30t-m0.2-14.5deg-x-0.6] (asked 0.5, printed and cut 0.183)"
        status: pass
    human_judgment: false

duration: "about 30 min"
completed: 2026-10-09
status: complete
plan_head_before: da07882d31043fb24ae637e13b0dbb23a0ac84e6
plan_head_after: ad8c51a261f8fab486bf93dc606842bc4f115075
commits: 2
---

# Phase 19 Plan 04: Ask any gear for the hob root, and prove the built root against the oracle Summary

**`root_shape` (radial or trochoid, default radial) now carries the hob's trochoid root from the field through one `root_mode` call into `derive()`, the outline and all three interfaces, with `root_thickness`/`root_gap` null under it, `root_fillet` the tip radius actually cut, and the built root read within 2e-3 x module by the independent oracle on all seven 19-02 rows.**

## Performance

- **Duration:** about 30 min (the start time was not recorded at launch; approximate, from file times)
- **Started:** about 2026-10-09T03:35Z (approximate)
- **Completed:** 2026-10-09T04:04Z
- **Tasks:** 2 (one tracer, one auto/tdd test-only)
- **Files modified:** 8 (`src/spur/params.py`, `calc.py`, `model.py`; `tests/test_trochoid.py`, `test_model.py`, `test_cli.py`, `test_api.py`, `test_calc.py`)

## Accomplishments

- **Tracer, end to end on the default gear.** `spur info --root-shape trochoid` and `GET /api/info?root_shape=trochoid` print the same document: `root_thickness` null, `root_gap` null, `root_fillet` 0.5 (the cutter tip radius used; its cap is 0.6348 mm), `root_d`, `pitch_d`, `tip_d`, `base_d`, `caliper_over_tips`, `tip_thickness`, `span_teeth` and `span` equal to the radial document's, and `warnings` exactly one sentence. `build(GearParams(root_shape="trochoid"))` is one valid solid with **134 faces / 376 edges against the default part's 172 / 490** (38 and 114 fewer: six side faces per tooth against eight), its 38 root splines selected by position with the count asserted.
- **D-02 as confirmed at 19-02.** `root_shape: Literal["radial", "trochoid"] = Field("radial", ...)` in group Teeth directly after `tip_chamfer`, plain `Field` with no `step`; `/api/schema` carries `enum ["radial","trochoid"]` and `default "radial"`; `spur info --help` lists `--root-shape {radial,trochoid}` between `--tip-chamfer` and `--face-width` with no edit to `cli.py`. `root_fillet`'s help names both meanings.
- **One predicate per consumer.** `RootMode` gained a trailing `curve: RootCurve | None = None`, set exactly when the mode is trochoid. `derive`, `model._build` and `tip_chamfer_limit` each call `root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)`. `spline_start(pr, fillet, curve)` returns `curve.points[-1][0]` and skips the halfway clamp; the tip chamfer's third bound under trochoid is `ra - R_join - TIP_CHAMFER_MARGIN` with a reason that does not mention a lead-in; the radial bound and reason are byte-identical.
- **The outline from one float.** `model._trochoid_outline` (moved from the 19-01 bench copy, no rewrite) shares the root curve's last `Vector` with the first involute point; `_outline(pr, fillet, curve=None)` returns it first, the radial body below untouched. `model.py` imports `root_mode` and `RootCurve` only; the source test finds none of the generator's names (and flags a string that holds one).
- **Honest numbers (D-03, D-05).** Under the curve the document prints no radial-flank number or sentence: no thickness, no gap, no gap-cap sentence, no lead-in chord sentence, no "this model uses a radial root" sentence. A refused request (for example 42 teeth, `nothing radial to replace`) builds the radial root and prints the radial thickness, gap and fillet with the refusal sentence. In trochoid mode the printed `root_fillet` is `rm.cutter.rho`; on the module-0.2 row asked 0.5 mm it prints and cuts 0.183 mm.
- **Kernel tier (SC2) at the human's bar.** `KERNEL_BAR_PER_MODULE = 2e-3`, read at 401 positions per root edge with the printed tip radius. The tripwire, the module-1 10-tooth row read 0.05 mm off the printed radius, reads over the bar.
- **Fixture untouched (L05, L26, SC1).** `git diff --exit-code tests/regression/pre_v0_2.json` clean after both tasks, `tests/regression` 86 passed, `cli.py` and `app.js` byte-identical to plan start, no numpy or scipy under `src/spur`, 31 pins.

### Kernel readings (oracle, mm; bar = 2e-3 x module; 401 positions per root edge, tooth 0)

| Row | Printed = cut tip radius | Reading | Bar | Reading / bar |
|---|---|---|---|---|
| 19 teeth, m 1.75, 25 deg, x 0 (default) | 0.5 | 2.2595e-05 | 3.5e-03 | 0.0065 |
| 8 teeth, m 1, 20 deg, x 0 | 0.38 | 3.5794e-05 | 2.0e-03 | 0.018 |
| 10 teeth, m 1, 20 deg, x 0 | 0.38 | 3.8929e-05 | 2.0e-03 | 0.019 |
| 14 teeth, m 1, 20 deg, x 0 | 0.38 | 3.9846e-05 | 2.0e-03 | 0.020 |
| 6 teeth, m 1, 14.5 deg, x 0 | 0.0 | 3.4905e-05 | 2.0e-03 | 0.017 |
| 30 teeth, m 0.2, 14.5 deg, x -0.6 | 0.183 (asked 0.5) | 3.5795e-05 | 4.0e-04 | 0.089 |
| 30 teeth, m 10, 14.5 deg, x -0.6 | 0.5 | 6.2097e-04 | 2.0e-02 | 0.031 |
| **Tripwire** 10 teeth, m 1, tip radius 0.38 + 0.05 | 0.43 | **1.1039e-02** | 2.0e-03 | **5.52x over** |

All seven agree with 19-02's `Oracle` column to the digits printed there, which was the check that the bar rests on the same readings it was set from.

### Captured sentences (L33)

Captured from `derive()` on 2026-10-09 and typed into the tests after capture, never composed in a test:

- Trochoid thickness: "root_thickness and root_gap are not printed with the hob-cut root: the tooth's thickness changes too fast with radius near the root circle to give one honest number there."
- 42 teeth, module 1, 20 degrees, x 0, backlash 0, tip radius 0.38 (`nothing radial to replace`): "No radial root to replace on this gear (base circle 19.734 mm, root circle 19.750 mm): the trochoid root request is ignored." (the sentence `root_warnings` already produced on 2026-10-08, now read through `derive()`.)

### Per-call cost of `derive()` (re-measured 2026-10-09, `calc.derive` docstring updated)

`python -m timeit -r 5` best of 5, Apple M5 Max, Python 3.12.15, 1-minute load 2.75: **10.3 usec** for the default gear and **29.6 usec** with `root_shape="trochoid"`. The earlier 14.7 usec figure was an M2 Max at load 14.4, so the two are not a delta.

### Gate result and cost (for 19-09)

`make verify` exits 0: ruff, mypy `--strict`, 5 import contracts kept, unfinished-work scan clean, **`1054 passed in 117.21s (0:01:57)`**, coverage 97.51 % (floor 96). A second full `make test` at 1-minute load 6.7 to 9.1 read `1054 passed in 128.56s`. 19-01's baseline on this host was 52.89 s (mean of three green runs), so the nine new kernel-tier tests moved the gate by roughly +65 to +75 s, **well past L34's 66 s bar**. Load was 5.5 to 9 during these runs (19-01's runs began at 3 to 12), so the size of the delta carries a host-load caveat; the direction does not. `--durations` of the new tests (second run, load 6.7 to 9.1):

| Test | Seconds |
|---|---|
| `test_the_kernel_tier_proof_fails_when_the_printed_tip_radius_is_off_by_0_05_mm` | 20.28 |
| `...every_kernel_row[19t-m1.75-25deg-x0]` | 16.55 |
| `test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root` | 13.08 |
| `...every_kernel_row[8t-m1-20deg-x0]` | 11.13 |
| `...every_kernel_row[10t-m1-20deg-x0]` | 10.30 |
| `...every_kernel_row[30t-m10-14.5deg-x-0.6]` | 10.19 |
| `...every_kernel_row[30t-m0.2-14.5deg-x-0.6]` | 10.18 |
| `...every_kernel_row[14t-m1-20deg-x0]` | 10.17 |
| `...every_kernel_row[6t-m1-14.5deg-x0]` | 10.05 |

First run (load 5.5 to 7.3, 8 workers, `-k` slice): 7.0 to 8.3 s per row, 14.55 s for the tripwire. The oracle read dominates (401 positions x 2 edges per read, a golden-section search per position); the build is about 1 s. The tripwire test reads twice (the true radius and +0.05 mm), so it is the slowest; the "true radius under the bar" half duplicates its row in the parametrized test and could go if 19-09 needs the seconds. The 401-position count is 19-02's requirement and was not changed here. **This is a gate-cost decision for 19-09 (L34), not made here.**

## Task Commits

1. **Task 1 (tracer): the default gear asked for the hob root, end to end** - `d58707f` (feat)
2. **Task 2: the kernel-tier proof** - `ad8c51a` (test)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md (hash in the STATE.md session line).

`commits: 2` is measured from the ledger: `git rev-list --count da07882..HEAD` read 2 at SUMMARY write.

## Files Created/Modified

- `src/spur/params.py` - `root_shape` field, `root_fillet` help naming both meanings, class docstring
- `src/spur/calc.py` - `RootMode.curve`, `spline_start(..., curve)`, `tip_chamfer_limit/effective(p, rm)`, `DerivedDimensions` types and descriptions, `derive()` keyed on the mode, the thickness sentence, comments and docstrings that said nothing in production calls `root_mode`
- `src/spur/model.py` - `_trochoid_outline`, `_outline(..., curve)`, `_gear_blank(..., curve)`, `_build` reads `root_mode`
- `tests/test_trochoid.py` - the tracer's calc test, the spelled-default test, the fixture read through `root_shape`, the 41/42 derive rows
- `tests/test_model.py` - `KERNEL_BAR_PER_MODULE`, `_root_edges`, `_oracle_reading`, the tracer's kernel test, the seven rows, tripwire, both-modes `root_d`, boundary, same-link, cache key, generator source test
- `tests/test_cli.py`, `tests/test_api.py` - the generalised field walk and the adjacency pin
- `tests/test_calc.py` - two `is not None` narrowings (see Deviations)

## Decisions Made

- The kernel bar, the field name, the junction law and the D-02 values are 19-02's and 19-01's, copied, not re-decided.
- The undercut sentence is kept for radial mode and for a refused request, and silent under a trochoid mode until 19-06 restates it. Between these two commits a trochoid request on an undercut gear therefore prints no undercut sentence: missing, not false, as the plan flagged.
- `_chamfer_tips` was left reading `tip_chamfer_effective(p)` (the plan's text). That call asks `root_mode` a second time inside one build with the same inputs, so the answers cannot differ. Passing `rm` down would break `test_the_kernel_fails_one_step_past_the_start_of_the_involute`, which monkeypatches `spur.model.tip_chamfer_effective` with a one-argument lambda; the cost is about 20 usec per build.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `tests/test_calc.py` narrowed for `float | None`**
- **Found during:** Task 1 (`make typecheck`, mypy `--strict` over `tests`)
- **Issue:** the plan's `files_modified` does not list `tests/test_calc.py`, but two existing tests compare `derive(...).root_thickness` and `root_gap` (`b.root_thickness > a.root_thickness`, `d.root_thickness + d.root_gap`), which stop type-checking when the fields become `float | None` (a plan-mandated change).
- **Fix:** an `assert ... is not None` before each use (4 added lines); no assertion about the numbers changed.
- **Files modified:** `tests/test_calc.py`
- **Verification:** `make verify.fast` and `make verify` green.
- **Committed in:** `d58707f`

**2. [Rule 2 - Missing Critical] `derive()`'s per-call cost figure re-measured**
- **Found during:** Task 1 (19-RESEARCH Pitfall 10)
- **Issue:** the docstring quotes 14.7 usec for a call that now makes one more `root_mode` call and, with `root_shape="trochoid"`, solves the curve. CLAUDE.md: performance claims are measured, not stale.
- **Fix:** measured both forms and added one paragraph with host, load and date (10.3 and 29.6 usec).
- **Files modified:** `src/spur/calc.py`
- **Committed in:** `d58707f`

### Plan-literal items that did not apply as written

**3. FEATURES' "4.68 mm ... 3.51 mm" thickness figures did not reproduce.** The plan asks the new sentence's comment to cite them. Measured on the default gear at tip radius 0.5 mm: **4.532 mm** of arc at rf + 0.00175 mm and **3.405 mm** at rf + 0.525 mm (0.3 module), by bisection on the contact-normal angle. The comment in `_ROOT_SENTENCES` carries the measured figures and says FEATURES quoted others; the sentence itself carries no figure. `d58707f`.

**4. [TDD ceremony] Task 2 is `tdd="true"` but has no RED.** It adds tests only, to behaviour Task 1 had already built, so a test written first could only have been green; `task.is-behavior-adding` is false (test-only files). The tests' ability to fail is shown instead by the tripwire test itself (a 0.05 mm radius error reads 5.5x over the bar) and by the generator test's own tripwire assertion. The plan is `type: execute`, so the plan-level gate does not apply. The pre-commit hook (`make verify.fast`) passed on both commits.

**5. The tracer feedback gate.** `type="tracer"`, no `gate=` attribute, `HUMAN_VERIFY_MODE` default `end-of-phase`, `<verify>` automated-only: the tracer verify (CLI and API end to end, the regression replay, SC1, `make verify.fast`) was re-run on the committed tree and passed, logged "Tracer verified end-to-end -- expanding", and no checkpoint was raised.

---

**Total deviations:** 2 auto-fixed (1 Rule 3, 1 Rule 2) and 3 plan-literal items.
**Impact on plan:** none on behaviour; the only unplanned file is a four-line type narrowing in `tests/test_calc.py`.

## Issues Encountered

- **The gate cost moved far.** See "Gate result and cost" above: +65 to +75 s against 19-01's baseline, over L34's 66 s bar, from the nine kernel-tier tests the plan asked for at the position count 19-02 required. Not fixed here; 19-09 owns the pricing and the decision.
- **No `ReentrantCallError` or other flake appeared** in the two full-suite runs, the 86-test regression slice or either commit hook, so 19-03's trigger ("the next `make verify` failure with its whole log kept") did not fire and nothing was kept.
- The tracer's first `derive()` edit mangled one block (a partial replacement left the lead-in text under the chamfer comparison); caught before running anything and rewritten from the original text. No commit contained it.

## Known Stubs

None. No placeholder values, empty data flows or TODO markers were added.

## Threat Flags

None. `root_shape` is a `Literal` refused with a 422 (API) or exit 2 (argparse) for anything else, `root_fillet` keeps its `_f(0.5, 0, 3)` bounds so `cutter()`'s ValueError is unreachable from user input (T-19-06); the default is radial with the radial body untouched and the fixture replayed unmodified (T-19-07); one `root_mode` per consumer, nulls and silenced sentences, the printed tip radius is the cut one and the oracle reads it back (T-19-08). T-19-09 (a request that builds slower) is 19-09's re-timing. No new network, auth or file surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-05 can add the structural guards (`ROOT_ARC_MIN` 2e-6 mm, spacing, annulus, area, junction bars from `### Bars adopted (19-02)`) inside `_trochoid_outline`; a gear whose root arc is in the dead band still reaches the kernel today and fails with the wrong remedy ("try smaller fillets or chamfers").
- 19-06 adds `root_form_d`, `root_waist` (floor 0.4 mm) and the restated undercut sentence; until then a trochoid request on an undercut gear prints no undercut sentence.
- 19-07 and 19-08 compose the trochoid column with the other families; `tests/composition.py` `ALWAYS` still lists `root_thickness` and `root_gap` as always non-null, which is wrong for any `root_shape="trochoid"` row (19-08).
- 19-09 must decide the gate cost: 117 to 129 s on this host against L34's 66 s bar, from the kernel-tier tests (see the durations table).
- Files filed: no debt or idea item was filed by this plan.

## Self-Check: PASSED

- Files: `src/spur/params.py`, `calc.py`, `model.py`, `tests/test_trochoid.py`, `test_model.py`, `test_cli.py`, `test_api.py`, `test_calc.py` exist.
- Commits `d58707f` and `ad8c51a` are ancestors of HEAD; `git rev-list --count da07882..HEAD` read 2.
- Acceptance greps found `root_shape: Literal["radial", "trochoid"] = Field(`, `curve: RootCurve | None = None`, the new `spline_start` and `tip_chamfer_limit` signatures, `rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` in `derive`, and `def _trochoid_outline(` and `requested=p.root_shape` in `model.py`.
- The tracer end-to-end line, the `kernel-tier tests present` line and the `SC1 holds` line printed; the fixture diff is clean.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
