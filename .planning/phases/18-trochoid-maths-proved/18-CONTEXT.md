# Phase 18: Trochoid Maths, Proved - Context

**Gathered:** 2026-10-06
**Status:** Ready for planning

<domain>
## Phase Boundary

The trochoid a hob cuts below the base circle exists as pure `calc.py` maths — stdlib
`math` only, no kernel, no `GearParams` field, no fixture contact:

1. **The cutter, defined once** — one pure function holds the basic rack (dedendum
   1.25·m read from the same expression as `rf`, tip radius ρ, backlash as cutter-tooth
   thickening, profile shift); every other function reads it. ρ is capped to the geometric
   maximum computed from the real cutter with backlash included, warned when trimmed
   (L03); ρ = 0 is legal. Above the pressure angle where the 1.25·m rack has no tip land
   (≈32.1°) no curve is computed.
2. **The curve, generated or honestly refused** — `calc.trochoid_root` returns an
   immutable `RootCurve` of `(radius, half_angle)` pairs, the envelope of the cutter tip
   arc, with the junction found by bisection on a monotone bracket only after a
   closed-form sign test says a crossing exists.
3. **One predicate** — `calc.root_mode` is the single answer to "does the trochoid apply
   to this gear" and owns every refusal reason. The three things called "undercut" today
   (`teeth < z_min`, `rb > rf`, the cutter's form circle) are never mixed.
4. **An independent oracle** in `tests/` sharing no code with the implementation: T1
   closed-form undercut onset, T2 swept-cutter no-gouge oracle, T3 freecad.gears one-off
   at ρ = 0 (recorded with source file, commit, licence; never imported, never vendored).
   Each bar from two recorded numbers with headroom stated; a ρ tripwire seen red.
5. **The root-mode decision** (O1–O4), taken here because it fixes the predicate's body:
   **O4** — see D-01. Its `Lxx` lands in Phase 19 with the geometry.

Not in this phase: any edit under `src/spur/` other than `calc.py`; any `GearParams`
field (Phase 19); wiring `_outline`, `root_fillet`, `spline_start`, `tip_chamfer_limit`
or `derive` to the predicate (Phase 19); the fixture flip (conditional Phase 20); the
restated undercut warning text in `derive()` (REQ-undercut-warning-restated is mapped to
Phase 19 — this phase supplies the closed-form onset and `x_min` it prints); numpy or
scipy anywhere under `src/spur/`; any new pin in `requirements.txt` (31 today).

Success criteria 1–5 of the ROADMAP entry are the acceptance; SC5's four checks
(`git diff --exit-code tests/regression/pre_v0_2.json` after every task; `git diff
--stat` against the phase base names only `calc.py` under `src/spur/`;
`grep -rnE 'numpy|scipy' src/spur` empty; 31 pins) hold after every task.

</domain>

<decisions>
## Implementation Decisions

### Root mode (the decision the roadmap sends here)
- **D-01:** **O4 — a default-off `Literal` field in Phase 19, the flip later under its
  own `Lxx` as a conditional Phase 20.** 0 of 44 fixture records move in this milestone
  unless Phase 20 runs; L05 and L26 hold byte for byte. Rejected: O1 (always-on when
  `teeth < z_min`: 5 of 44 move and the root shape jumps ≈0.14·m between 17 and 18 teeth
  at 20°, a step no real hob produces — FEATURES argues against it on merits); O2
  (always-on wherever `rb > rf`: 28 of 44 move including the default 19T/25° gear by up to
  ≈0.30 mm of root material, L05 becomes an exception); O3 alone (same seam, Phase 20
  dropped — rejects the tool-survey norm that the hob root is eventually the default).
  Phase 19's `Lxx` records this choice; it supersedes L10 and amends L09 and L33.
  — **Reversibility:** costly — reversing to always-on is exactly Phase 20 (one flip
  commit, `make fixture.regen`, an `Lxx` naming the moving records in advance), which O4
  already prices; reversing to "never" is dropping Phase 20.
- **D-02:** **When requested, the trochoid applies only where `rb > rf`** — the region
  L10 names, the radial lead-in replaced. Wherever `rb <= rf` the L09 analytic fillet
  stays (the milestone brief: "the analytic fillet kept for the normal case"). A request
  on a gear with nothing radial to replace is ignored and warned in the existing
  ignored-field sentence shape (L27 / Phase 13 D-15: "No spoke arms with spoke_count 0:
  … is ignored"). Consequence: the mode never reaches 200-tooth gears (ARCHITECTURE:
  `rb > rf` only below `2(1.25 − x)/(1 − cos α)` teeth — 26.7 at 25°, x = 0; 116.2 at
  x = −0.6, 14.5°). Rejected: every gear when requested (supersedes L09 for opted-in
  gears, 200-tooth build time unmeasured, Phase 19's composed sweep grows).
- **D-03:** **`root_mode` returns a frozen result: `mode: Literal["radial", "trochoid"]`
  plus a `reason`** naming why it stayed radial — not requested / nothing radial to
  replace (`rb <= rf`) / tip land gone at this pressure angle / bracket degenerate.
  Consumers read only `mode`; Phase 19's warnings and `derive()` sentences read `reason`.
  The two `Literal` values become the Phase 19 field's values (field name is Phase 19's;
  ARCHITECTURE's `root_shape` is the candidate). Rejected: mode only (the reasons get
  recomputed by whoever warns and the three predicates drift apart again).
- **D-04:** **`root_mode(p, pr, requested="radial")` — the user's choice is an explicit
  argument defaulting to radial.** Phase 19 passes the field's value. Every present
  caller gets `radial` with reason "not requested", so the fixture cannot move; tests
  exercise `requested="trochoid"` directly, so every geometric branch is testable through
  the public signature in this phase. Rejected: a body that always returns radial until
  Phase 19 edits it (the roadmap's literal `root_mode(p, pr)`, untestable until then).
- **D-05:** **SC4's root-shape step is measured at both boundaries**: the undercut
  threshold (17 vs 18 teeth at 20°; FEATURES' simulation ≈0.14·m) as the roadmap requires,
  **and** the `rb = rf` crossover where the trochoid hands back to the L09 fillet under
  D-02 — the edge a user stepping `teeth` will actually see. One `bench/RESULTS.md`
  section, two tables, host state recorded as every section does. A figure that
  contradicts D-01's premises reopens the choice before Phase 19 is planned (ROADMAP).

### The cutter
- **D-06:** **Dedendum fixed at 1.25·m.** The cutter reads the tip depth `(1.25 − x)·m`
  from the same expression that defines `rf = r − m(1.25 − x)` in `calc.profile`, never a
  copy (PITFALLS 22); `root_d == 2·rf` holds in both modes (FEATURES G7, measured
  3.75000007 vs 3.75). No surveyed tool exposes the dedendum. Rejected: an `hf_star`
  cutter parameter defaulting to 1.25 (speculative flexibility; two places could disagree
  about `rf`).
- **D-07:** **ρ is an explicit millimetre argument; nothing in Phase 18 reads
  `p.root_fillet` as ρ.** The sweep covers ρ* ∈ {0, 0.1, 0.25, 0.38, 0.5}·m plus each
  case's own `root_fillet` value and each case's cap, so Phase 19's
  REQ-cutter-tip-radius-settable choice (reinterpret `root_fillet` or a new field) is
  covered either way. Rejected: binding ρ = `root_fillet` now (pre-empts Phase 19; 0.5 mm
  is 0.5·m at m 1, above the 0.472 cap at 20°, so the default would be capped and warned
  on small modules).
- **D-08:** **No T4 reference exists; three oracle tiers only.** The human has no hob
  data sheet or KISSsoft export; research found no public table (STACK, LOW for the
  absence). T1 closed-form onset, T2 swept-cutter no-gouge oracle (primary), T3
  freecad.gears one-off at ρ = 0. Consequence: nothing anchors the construction outside
  its own derivation, so `root_form_d` (Phase 19) is labelled the cutter-envelope junction
  and never ISO 21771 parity (STACK ASSUMPTION stays open; L08).

### Refusal and the z_min double root
- **D-09:** **Undercut is decided from the sign of `ξ_join` (exact algebra); a negative
  `ξ_join` whose radius bracket degenerates uses the flank join as the form point.**
  STACK measured the bracket found at `ξ_join = −2.9e-3 mm` (cusp 1.3e-7 mm above `rb`)
  and lost at `−2.9e-5 mm` (join 5e-11 mm above `rb`): double precision cannot separate
  `R` from `rb` below ~1e-15·R, a roll resolution of ~1e-7 mm — the same order as the
  kernel tolerance L26 measured. The epsilon on `ξ_join` (or on `R − rb`) is **set from a
  measurement in this phase**, with the two STACK points as its bracket, and recorded
  beside the constant with date and host (L08, PITFALLS 23). The double root at exactly
  `z_min` is therefore a tangent join, not a refusal, and is tested one tooth step either
  side and, at a tuned profile shift, one field step either side (the L33 pattern).
  Rejected: `None` + warning on a degenerate bracket (refuses a legal gear within
  ~1e-7 mm of `z_min` with no geometric reason).
- **D-10:** **`root_mode` owns every refusal.** It is the single place that says
  radial-and-why (D-03's reasons). `trochoid_root` is called only when the mode is
  `trochoid` and returns `RootCurve | None`; `None` means a numerical failure the closed
  form did not predict (bracket not found, non-monotone radius), and the sweep (D-12)
  must show zero of them inside the allowed box. Warning sentences come from **one calc
  function keyed on the reason**; tests capture them from it, never typed (the L33 rule).
  Rejected: `trochoid_root` returning `(curve, warnings)` (two places know the domain
  rules).
- **D-11:** **An invalid one-flank construction refuses with a named reason** — a loop, a
  curve past the space centreline, `a < 0` after the cap, anything STACK's one-flank
  sweep did not exercise (ROADMAP's open item "two-flank interaction at very low tooth
  counts or large ρ"). `None` + warning, the analytic root as the fallback. The sweep
  counts and lists every such case; **any inside the allowed box goes to the human at a
  checkpoint before a rule is chosen.** Never clip to the centreline or hide the loop
  (PITFALLS 20, L08).

### The sweep and the cost figures
- **D-12:** **Sweep box: STACK's 7,296-case grid as the floor, plus the project's box
  corners.** STACK's grid (m = 1; z 6–40, 60, 100, 200; x ∈ {−1, −0.5, −0.2, 0, 0.2,
  0.5, 1}; α ∈ {14.5, 20, 25}; ρ* ∈ {0, 0.1, 0.25, 0.38, 0.5}; backlash ∈ {0, 0.1}) plus
  the real `GearParams` limits: α 30, one step either side of the tip-land limit
  (≈32.1°), 35; **module at both field limits, 0.2 and 10** (`params.py:36`; deviation
  scales with m); x at both field limits (−0.6, 1.0); ρ at each case's cap and at that
  case's `root_fillet`. Asserted: zero bracket failures, monotone radius on every curve,
  no point above `ra` or beyond the crossing; every refusal inside the box is counted and
  listed by reason, not only bracket failures. Rejected: STACK's grid alone (leaves α
  above 25°, the real module range and the field limits unexercised).
- **D-13:** **The generator sweep is a gate test under a measured budget.** It lives in
  `tests/test_calc.py` and runs at commit via `verify.fast` (11.3 s warm, L36). STACK's
  slowest solve was 0.19 ms, so ~1.5–2 s is the expectation; its wall time is measured at
  `-n 8` and recorded. **If it prices over ~2 s**, the plan keeps a sample in the gate and
  moves the full grid to a `bench/` script with a `bench/RESULTS.md` row. The T2 oracle
  (STACK: 41 points × 2,001 rolling angles, 0.07 s per case) runs on a handful of rows in
  the gate; the full-grid oracle only in bench. Rejected: bench only (a bracket regression
  is caught only when someone reruns the bench).
- **D-14:** **Per-call cost is measured and recorded; no budget is set.** Re-measure
  `derive()` and correct its stale 11.5 µs docstring figure (`calc.py:955-956`; PITFALLS
  saw 20.4 µs at load ≈6.8); measure `root_mode` and `trochoid_root` per call the way the
  docstring does (`.venv/bin/python -m timeit`, best of 5, default `GearParams`), with
  host load and date beside them. `derive()` does not call either until Phase 19; Phase
  19 decides what enters the keystroke path from these numbers. Rejected: a `derive()`
  ceiling fixed now (a number picked before the measurement exists).

### Carried forward from ROADMAP.md / REQUIREMENTS.md (locked, not re-discussed)
- Stdlib `math` only; bisection (sign-only), never Newton, because `acos(min(1, rb/R))`
  has a square-root singularity at `R = rb` (the `_involute_angle` precedent, L08).
- The curve is the **envelope of the tip arc** `E(φ) = C + ρ·(C − I)/|C − I|`, never the
  centre path and never an offset of it (PITFALLS 5); `Profile.half_angle` is never
  reused below `rb`.
- The junction is tangent when not undercut and a crossing when undercut (PITFALLS 4);
  tangency (position and direction) is asserted only for `z ≥ z_min`.
- The cap: ρ above the geometric maximum **computed from the real cutter with backlash
  included** is capped and warned naming the capped value at 3 dp; the first test of the
  phase reconciles PITFALLS' 0.363·m (m 1.75, 25°) with STACK/FEATURES' 0.318·m (SUMMARY's
  inference: backlash 0.10 entering the tip land as `backlash/2`) and records the
  reconciliation. The cap and the domain limit each tested one step either side.
- Junction equality: the cutter's join with the involute equals `Profile.half_angle` at
  backlash 0 and 0.10, to a bar **re-measured in the phase** (PITFALLS: 4.9e-17 rad at
  19T/25°, 6.9e-18 rad at 30T/20°); a cutter without backlash leaves a 0.046 mm step on
  the default gear, which is why backlash is cutter-tooth thickening.
- Bars from two recorded numbers (the model's own error and the reference's stated
  resolution) with headroom written beside them; **under about 10× goes to the human**
  (L33 D-06). STACK's T2 separation: −1.6e-11 mm on the genuine segment vs +3.9e-3 mm
  past the form point — eight orders, so a bar anywhere between is not tuned. The ρ
  tripwire moves ρ by a stated amount and is seen red.
- T3 numbers are recorded once in the test with source file, commit and licence
  (GPL-3.0); STACK measured 1.8e-15 mm in R and 1.1e-16 rad in angle at z = 8, 10, 14,
  x = 0, 0.3. Module is recorded with every crossing number (SUMMARY correction 14).
- Every scratch number a plan leans on is re-created inside the repo as a test or bench
  row with kernel pair, load and date (SUMMARY "Gaps"; the four research prototypes are
  not the oracle).
- Commit discipline: L36 — `verify.fast` at commit (keeps `tests/test_calc.py` and the
  fixture replay at the commit boundary), the full gate at pre-push, `make verify` run
  by hand before every push (Phase 17 D-09). Phase branch
  `gsd/phase-18-trochoid-maths-proved`, cut from `origin/main` at discuss time
  (HOW_TO_DEVELOP §2); lands through a PR via `make pr.land`.

### Claude's Discretion
- `RootCurve`'s exact shape beyond "immutable `(radius, half_angle)` pairs" — whether it
  also carries the junction radius and the join kind (tangent / crossing); the sample
  count and spacing (STACK's N = 16 uniform in φ, 3.6–4.0e-5 mm at m = 1, is the start;
  Phase 19 reconciles the two spline-deviation methods before any kernel bar is set).
- The cutter result's shape (a frozen dataclass holding the derived rack constants, the
  requested and capped ρ, the tip land `a`) and the warning function's name.
- The tripwire amount for ρ; the epsilon measurement method in D-09 (bisection on
  `ξ_join` toward the point where the bracket is lost, as STACK did).
- How T3 is recorded (constants in the test with a provenance docstring is the default
  reading; no data file, no network).
- Test layout inside `tests/test_calc.py` versus a sibling module under `tests/` for the
  oracle (the L33 `_filleted_spoke_volume` precedent lives in `tests/test_model.py`); the
  bench script's name and whether the step measurement (D-05) is a bench script or a
  one-off recorded run.
- The exact grid for the box corners in D-12 (one step either side of the tip-land limit
  uses `pressure_angle`'s field step).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and acceptance
- `.planning/ROADMAP.md` § "Phase 18: Trochoid Maths, Proved" — goal, the five success
  criteria, the root-mode paragraph, the boundary with Phase 19, the research flag and
  its four open items.
- `.planning/REQUIREMENTS.md` § "Trochoid maths — `calc.py` only, no kernel, no field, no
  fixture contact" (REQ-cutter-defined-once, REQ-trochoid-root-generated,
  REQ-root-mode-single-predicate, REQ-trochoid-proved-independently, and
  REQ-undercut-warning-restated for the onset/`x_min` this phase supplies), § "Rules every
  requirement lives by", § "Out of Scope".
- `.planning/PROJECT.md` — core value (L08), the v0.4 brief, "Rules this milestone lives
  by".

### Research (derivation, measured windows, pricing, pitfalls)
- `.planning/research/SUMMARY.md` — corrections 1–4, 13–18, 20; "Phase 18" under
  "Implications for Roadmap"; "Decisions the human must make" items 1, 2, 7, 8 (decided
  here); "Gaps to Address".
- `.planning/research/STACK.md` § "(a) The trochoidal root inside a pure-Python 2D
  outline" (the construction, the 7,296-case sweep, the bracket-collapse numbers, the
  degenerate-rack counts, N = 16 sampling) and § "(b) A known-good reference for the
  test" (the three tiers, T2's measured separation, the freecad.gears cross-check, every
  rejected reference); § "Open questions".
- `.planning/research/FEATURES.md` § "Findings the roadmap must know first", § "Reference:
  the generating geometry" (G1–G10; G8 the ρ cap table; G4 the onset and `x_min`), § "What
  changes on the real part, measured", § "Always-on vs opt-in: evidence and price" (the
  O1–O4 table D-01 chose from), § "Open decisions for discuss-phase".
- `.planning/research/ARCHITECTURE.md` § 1.2 (recommended structure), § 1.3 (where the
  junction is computed), § 1.5 (the root-mode costing, the 28/5 counts, the commit-shape
  finding), § 1.6 (the known-good-profile test: data flow, provenance, tolerance), § 6
  (anti-patterns), § 7.
- `.planning/research/PITFALLS.md` — Pitfalls 1 (three predicates), 3 (cutter frame:
  backlash, shift, rolling direction), 4 (tangent vs crossing; the double root), 5
  (envelope not centre path; the oracle), 6 (printed numbers drift), 8 (tolerance from
  the reference, the tripwire), 16 (the warning), 20 (loops hidden), 21 (`derive()` stays
  pure), 22 (cutter constants in two places), 23 (cite symbols, record kernel pair and
  date).

### Decisions this phase is bound by or will amend (in Phase 19)
- `docs/architecture/decision_log.md` L03 (cap and warn, or refuse), L05 (absolute-mm
  defaults), L08 (no number is better than a wrong number), L09 (root fillets computed,
  not filleted), L10 (radial root below the base circle — superseded by Phase 19's
  `Lxx`), L26 (the fixture rule; the 1e-7 mm kernel tolerance), L33 (the lead-in warning;
  the `_filleted_spoke_volume` oracle precedent and the D-06 10× rule), L36 (the commit
  subset this phase's tests run under).
- `docs/ideas/2026-09-21-trochoidal-root-fillets.md` — the idea this milestone implements
  (its scope sentence: "generate the trochoid from the cutter geometry, keep the analytic
  fillet path for the normal case (L09)").
- `docs/architecture/gear-maths/strategy.md` (its L10 line), `README.md:222-227` (the
  radial-root claim) — read for what Phase 19 must bring true; **not edited here**.

### Process and style
- `CLAUDE.md` — the two standing rules, "Finishing work properly", "Capturing ideas and
  debt", the gate.
- `docs/CODING_VALUES.md` — comments carry the measurement that forced the choice.
- `docs/HOW_TO_DEVELOP.md` §2 (branch before discuss), §6 (`make verify` before push).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/spur/calc.py`: `Profile` (frozen dataclass, `rb`, `rf`, `ra`, `psi_p`,
  `half_angle(rho)` for `rho >= rb`, `r_start = max(rb, rf)`) and `profile(p, backlash)`
  (`rf = r − m(1.25 − x)`; `s = m(π/2 + 2x·tan α) − backlash`) at lines 70–98 — the cutter
  reads its constants from here. `inv(a)` at 64. `_involute_angle` (1158) is the sign-only
  bisection precedent; `centre_distance` (1174) its caller. `_tooth` (211), `root_fillet`
  (224), `spline_start` (230), `tip_chamfer_limit` (258) are the Phase 19 consumers —
  untouched here. `derive()` at 946; its cost docstring at 955–956 (the stale 11.5 µs);
  the shipped undercut sentence at 1006–1009 (`z_min = 2(1 − x)/sin²α`, "uses a radial
  root instead" — pinned verbatim in `pre_v0_2.json:582,632,948,996,1588`, untouched
  here). Module docstring: "must never import `cadquery`"; the import-linter contract
  enforces it.
- `src/spur/params.py`: field limits the sweep box reads — `teeth` 6–200, `module`
  0.2–10 step 0.05, `pressure_angle` 14.5–35, `profile_shift` −0.6–1.0, `backlash` 0–1
  step 0.01, `root_fillet` 0–3 (lines 34–47).
- `tests/test_calc.py` (1,554 lines): the `bisect` oracle inside the centre-distance test
  at 574–596 (an independent bisection in the test, sharing no code); the 15-row
  `test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle` at 747 (one field step
  either side of a crossing; strings captured from `derive()`).
- `tests/test_model.py:1153` `_filleted_spoke_volume` — the oracle precedent: closed form
  in the test module, never calls the production helper, bar at `abs=1e-9` with the
  measured gap in the docstring.
- `bench/RESULTS.md` — every section carries a "### Host state" block (machine, Python,
  kernel pair, HEAD, date/time, load); the step measurement (D-05) and the cost figures
  (D-14) follow it.
- `Makefile`: `verify.fast` / `test.fast` (L36) — `tests/test_calc.py` is inside the
  commit-time slice, so the sweep's wall time is paid on every commit (D-13's budget).

### Established Patterns
- A parameter is validated once at `GearParams` and trusted afterwards; `calc` functions
  take `GearParams` (and often a `Profile`) and return floats, tuples or frozen
  dataclasses — `root_mode(p, pr, requested=...)`, `cutter(p, rho)` and `trochoid_root`
  follow that shape.
- Constants carry the measurement that set them (`ROOT_CONTACT`, `TIP_CHAMFER_MARGIN`,
  `HEX_CELL_CAP` comments at `calc.py:18-62`); D-09's epsilon is written the same way.
- Warnings are sentences generated in one place and captured in tests from the function,
  never typed (L33); ignored-field warnings use the "… is ignored" sentence shape.
- Test names read like requirements (`test_<requirement_as_phrase>`); shared tables are
  hand-written, not computed from code under test (`tests/composition.py`, L08).
- Decision entries append-amend and quote the measured number that set them; the Phase 19
  `Lxx` will quote this phase's numbers (the epsilon, the cap reconciliation, the step,
  the costs).

### Integration Points
- New code: `src/spur/calc.py` only — the cutter function and result, `root_mode` and its
  result type, `trochoid_root` and `RootCurve`, the warning function, the closed-form
  onset / `x_min`; `tests/test_calc.py` (or a sibling test module) — the sweep, T1, T2,
  T3, the tripwire, the junction-equality and cap tests, the one-step-either-side rows;
  `bench/RESULTS.md` — the step section (D-05) and the cost figures (D-14); possibly a
  `bench/` script (D-13's fallback).
- Nothing reads `root_mode` or `trochoid_root` from production code in this phase
  (ROADMAP boundary) — every present caller of `spline_start` / `root_fillet` is
  unchanged, which is what keeps SC5 true.
- Phase 19 wires `_outline`, `root_fillet`, `spline_start`, `tip_chamfer_limit`, `derive`
  to `root_mode`; adds the `Literal` field whose values are D-03's; prints the onset and
  `x_min`; records D-01 as the `Lxx`.

</code_context>

<specifics>
## Specific Ideas

- The human's root-mode choice is O4 with the narrow region (D-01 + D-02): "opt-in first,
  flip later or never costs nothing extra; always-on costs exactly one extra phase"
  (SUMMARY). Phase 20 stays conditional in the roadmap.
- D-05's second table (the `rb = rf` crossover) is the number the human wants to see
  before Phase 19 is planned: it is the step a user actually meets under D-02.
- The reason enum in D-03 is the contract Phase 19's warning text hangs off; the four
  reasons named there are the floor, and D-11 may add named invalid-construction reasons
  after the sweep.
- "Any refusal inside the allowed box goes to the human" (D-11) and "a bar under ~10×
  goes to the human" (L33 D-06) are real pauses: the sweep's refusal list and the measured
  gaps in front of the human, named options, no default.
- Every number this phase prints into a docstring, a constant or `bench/RESULTS.md`
  carries date, host load and the kernel pair (PITFALLS 23); the research prototypes'
  numbers are brackets for expectation, never the recorded value.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. Items the discussion touched but that are
mapped elsewhere by the roadmap and not re-decided here: the field's name and the
`root_fillet`-versus-new-field choice for ρ (Phase 19, REQ-cutter-tip-radius-settable);
`root_thickness` / `root_gap` under the trochoid and the waist floor (Phase 19,
REQ-derived-numbers-honest-under-trochoid); the restated warning text (Phase 19); the
flip (conditional Phase 20).

</deferred>

---

*Phase: 18-trochoid-maths-proved*
*Context gathered: 2026-10-06*
