# Phase 18: Trochoid Maths, Proved - Research

**Researched:** 2026-10-07
**Domain:** pure-stdlib rack-cutter envelope (trochoidal root) geometry in `src/spur/calc.py`, proved by an independent swept-cutter oracle in `tests/`
**Confidence:** HIGH for the maths, the sweep findings and every number marked "scratch run" (all re-derived and run this session with stdlib Python on the repo's `.venv`); MEDIUM for the one external anchor found (Zhang / KISSsoft, one data point, one inferred input); LOW for ISO 21771 parity (clause unobtainable) and for the absence-of-a-reference claim.

How to read the tags. `[VERIFIED: scratch run]` = computed this session by a throwaway stdlib script kept outside the repo (scratchpad); every such number is a bracket for the planner's expectation and must be re-created inside the repo as a test or bench row with host load, kernel pair and date beside it (CONTEXT "Every scratch number a plan leans on", PITFALLS 23). `[VERIFIED: path:lines "quote"]` = a discrete in-repo value, file opened this session, quoted verbatim. `[CITED: url]` = read from the source named. `[ASSUMED]` = not verified; listed in the Assumptions Log.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Root mode (the decision the roadmap sends here)**
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

**The cutter**
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

**Refusal and the z_min double root**
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

**The sweep and the cost figures**
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

**Carried forward from ROADMAP.md / REQUIREMENTS.md (locked, not re-discussed)**
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

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. Items the discussion touched but that are
mapped elsewhere by the roadmap and not re-decided here: the field's name and the
`root_fillet`-versus-new-field choice for ρ (Phase 19, REQ-cutter-tip-radius-settable);
`root_thickness` / `root_gap` under the trochoid and the waist floor (Phase 19,
REQ-derived-numbers-honest-under-trochoid); the restated warning text (Phase 19); the
flip (conditional Phase 20).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-cutter-defined-once | One pure `calc` function defines the basic rack cutter (dedendum 1.25·m, tip radius ρ, backlash as cutter-tooth thickening, profile shift); ρ capped with backlash included and warned; no curve above the tip-land limit; junction equals `Profile.half_angle` at backlash 0 and 0.10; cap and domain limit each tested one step either side | Cutter constants and closed-form cap derived and run (Standard Stack, Pattern 1); cap reconciliation done (0.318·m vs 0.363·m explained, F1); the domain limit is not a constant 32.1° (F2); cap must round down, not to nearest (F3); junction equality measured 7.6e-17 rad |
| REQ-trochoid-root-generated | `calc.trochoid_root` returns an immutable `RootCurve` of `(radius, half_angle)` pairs or `None` plus a warning; closed-form sign test before bisection; explicit rule at the `z_min` double root; sweep with zero bracket failures and monotone radius; `derive()` cost re-measured | Contact-angle (β) parametrisation that has no singularity at any ρ (F4); the closed-form junction and the one bisection (Pattern 2, 3); the double-root rule with a measured epsilon scaling with `rb` (F6); sweep numbers and what the "7,296 floor" really contains (F5); per-call cost measurements |
| REQ-root-mode-single-predicate | `calc.root_mode` is the one predicate; the three "undercut"s never mixed; one tooth step either side and one field step either side | The three predicates nest exactly: undercut implies `rb > rf` (proof + 557k-combination check); reason set and the two things root_mode still needs that CONTEXT's signature lacks (ρ, and the severed-tooth test, F7); D-05 measurement design and prototype figures |
| REQ-trochoid-proved-independently | T1 closed form, T2 swept-cutter no-gouge oracle, T3 freecad.gears one-off at ρ = 0; bars from two recorded numbers; tripwire seen red | T2 oracle built and run (needs neighbouring cutter teeth to see the two-flank interaction); T3 run against the real module at a named commit (2.66e-15 mm); T4 candidate found (Zhang 2018 Table 7, KISSsoft, one point, F8); bars, headroom and tripwire response measured |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Treated as locked decisions alongside CONTEXT.md. [VERIFIED: /Users/halfb00t/git/halfb00t/spur/CLAUDE.md, read this session]

- **Gate:** nothing is done until `make verify` passes; state the command and the result line in the reply. `make verify` = ruff, `mypy --strict`, import-boundary contracts, unfinished-work scan (`no-fake-done`), pytest. No Docker needed.
- **Two standing rules:** a number the tool prints is a number someone will cut metal to; if it cannot be computed honestly, report a warning and no number (L08). A parameter the user did not set must never silently change the part; defaults are absolute mm (L05); trimmable dimensions are capped and warned, a direct conflict between two explicit choices is a `422` (L03).
- **Style:** `calc.py` runs on every keystroke and must never import `cadquery`; vendor types stop at their boundary; a parameter is validated once at `GearParams` and trusted afterwards. Comments explain why and carry the measurement or constraint that forced the choice. English throughout.
- **Simplicity:** surgical edits, no speculative flexibility, one concern per commit (Conventional Commits, normal prose).
- **Finishing:** new behaviour ships with its tests in the same change; performance claims are measured and recorded; `make verify` fails on `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError` markers (whole-word, `*.py`) and on a mypy suppression under `src/spur/`.
- **Ideas and debt:** one file per item from `docs/<dir>/TEMPLATE.md`, INDEX row in the same commit; state before the final reply whether any item was filed and its path.
- **Reuse `make`** instead of ad-hoc shell; project skills live in `.ai_skills/` (empty by design, `README.md` read).
- **Ruff selects** `E,F,W,I,N,UP,B,SIM,C4,PTH,TID,ARG,ERA,TRY,LOG,G` (`pyproject.toml:52-65`): `N` forbids upper-case local variable names (write `w_c`, not `wC`) and `ERA` flags commented-out code, so a comment that looks like an assignment fails lint. `[tool.pytest.ini_options]` sets `filterwarnings = ["error", ...]` and `--strict-markers`; `fail_under = 96` with `branch = true` (`pyproject.toml:121-129,152`), so every fallback branch added to `calc.py` needs a test that reaches it.

## Summary

The maths in the milestone research is right, and it reproduces: I re-implemented the cutter, the envelope, the junction, the crossing solve and an independent swept-cutter oracle in stdlib Python and ran them against the repo's own `profile()`. The cutter's `rb`, `rf` and `psi_p` agree with `calc.profile` to 0.0 over 62,185 allowed gears; the junction equals `Profile.half_angle` to 7.6e-17 rad at 19T/25° with backlash 0.10; the oracle reads 1e-15 mm (times the module) on every honest curve and 5e-2 mm on a curve left running past the form point; STACK's form radius (4.72560 vs `rb` 4.69846 at z = 10, 20°, ρ = 0.38) and FEATURES' waist figure (0.0220·m at 6T, 14.5°, x = −0.6, ρ = 0.38) both come out as published. The real freecad.gears module at a named commit matches the ρ = 0 case to 2.66e-15 mm.

But the prototype work found nine things that CONTEXT.md and the research files do not say, and several change the plan. The ones that matter most: (1) STACK's formula `E = C + ρ(C − I)/|C − I|` is only valid while the cutter's tip-circle centre sits below the rolling line (ρ < (1.25 − x)·m); above it the sign must flip, and at equality it is 0/0 — the "7,296 cases" silently excluded exactly the 684 rows where this happens, and those rows are reachable inside the allowed box (393 of 28,957 gears at ρ = 0.5 mm). A contact-normal-angle parametrisation has no such singularity and was proved to 1e-15 mm. (2) The two-flank interaction is real inside the allowed box: at ρ = 0 the neighbouring spaces' trochoids cut the tooth through (196 `GearParams`-valid combinations, z 6–9, α ≤ 24°, x ≤ −0.4), and even at the cap a tooth can be left a few thousandths of a module thick. This is the D-11 checkpoint. (3) The tip-land limit is 32.14° only at zero backlash; at the default backlash and module it is 33.07°. (4) Rounding the capped ρ to 3 dp can round it up past the true cap and refuse a legal gear (a = −3.6e-4 mm at z 12, m 0.5, 15°). (5) The degenerate-bracket epsilon scales with `rb`, not with millimetres: measured loss at |ξ|/rb ≤ 1.0e-5.

**Primary recommendation:** implement `calc.cutter` / `calc.trochoid_root` on the contact-normal-angle form `E(β) = (rf + ρ(1 − cos β))·n(φ) + (ρ sin β − w_c tan β)·t(φ)`, `φ = (a + w_c tan β)/r` (one closed form for every ρ, both signs of `w_c`), take the junction in closed form when `ξ_join ≥ −ε·rb` and by two sign-only bisections otherwise, floor the ρ cap to 3 dp, have `root_mode` own the severed-tooth refusal (by running the generator), and prove it with an oracle that includes the adjacent cutter teeth. Stop at two checkpoints for the human before locking rules: the severed-tooth class (D-11) and whether to adopt the KISSsoft anchor as T4 (D-08).

### Findings that change or sharpen the plan (all [VERIFIED: scratch run] unless tagged)

| # | Finding | Evidence | Consequence for the plan |
|---|---------|----------|--------------------------|
| F1 | The 0.318·m and 0.363·m caps are the same formula at backlash 0 and 0.10. `ρ_max = (π·m/4 + backlash/2 − 1.25·m·tan α)/(sec α − tan α)`, independent of x | m 1.75, 25°: backlash 0 gives 0.55629 mm = 0.31788·m; backlash 0.10 gives 0.63478 mm = 0.36273·m (PITFALLS' 0.635 mm = 0.363·m). m 1, 20°, backlash 0: 0.47191 | The phase's first test records this (REQ-cutter-defined-once); the cap is x-independent and linear in backlash |
| F2 | The no-tip-land limit is `tan α = (π/4 + backlash/(2m))/1.25`, not a constant | 32.142° at backlash 0; 33.071° at the default (backlash 0.10, m 1.75); 33.756° at m 1; 39.6° at backlash 0.5, m 1; above the field's 35° whenever `backlash/m` ≥ 0.18 (the limit is then never reached) | "One step either side" must be pinned per (backlash, module): 32.0/32.5 at backlash 0, 33.0/33.5 at the default gear. ROADMAP's "≈32.1°" is the backlash-0 value |
| F3 | The cap must be floored to 3 dp, not rounded to nearest | `rho_max(0.5 mm, 15°, 0) = 0.29353`, `round(…, 3) = 0.294`, a at 0.294 = −3.6e-4 mm: a legal gear refused as "no tip land" | Use `math.floor(cap·1000)/1000`; the used ρ and the printed ρ are then the same number (L08) and `a ≥ 0` holds; sweep rows "ρ at the cap" fail spuriously otherwise (26,076 spurious refusals seen) |
| F4 | `E = C + ρ(C − I)/|C − I|` is wrong for `w_c = ρ − d > 0` (gouges 0.70 mm in the oracle) and 0/0 at `w_c = 0` | `w_c ≥ 0` means ρ ≥ (1.25 − x)·m; with the sign flipped the oracle agrees to 1.7e-15 mm | Use the β form (below); it equals the φ form to 1.8e-15 on `w_c < 0` and is continuous through `w_c = 0` where the whole arc is traced in a vanishing φ-interval |
| F5 | STACK's 7,296 = the 7,980-case product minus the 684 rows with `w_c ≥ 0` (x = 1 and ρ* ∈ {0.25, 0.38, 0.5}); it counts 912 rows with `a < 0` as solved and includes x = −1, which `GearParams` rejects (min −0.6) | Recomputed: `w_c < 0` rows = 7,296 = 3,150 undercut + 4,146 not (exactly STACK's split); 912 have `a < 0` | Define the sweep floor as the explicit 7,980 product with x = −1 replaced by the field limit −0.6, refusals tallied by reason; 7,296 is not a floor of anything |
| F6 | The bracket fails at |ξ_join|/`rb` ≲ 1e-5, so the epsilon is relative to `rb` | 361 random cases, largest failing |ξ|/`rb` = 1.0e-5 (scan 4 steps/decade); rb 0.66 to 58 mm | ε = 1e-4·`rb` is 10× over the largest observed loss; fallback error ≤ (1e-5·rb)²/(2·rb) = 5e-11·rb (3e-9 mm at rb 58) |
| F7 | Inside the allowed box (GearParams limits and `check()` clean) the neighbouring spaces' trochoids can cross inside the tooth: the tooth is severed | At ρ = 0: z 6–9, α ≤ 24°, x ≤ −0.4 (196 combinations in a finer pressure-angle/shift scan over six (module, backlash) pairs; 251 in the 149,240-point sweep-box grid). Falling with ρ: 190 at 0.1·m, 125 at 0.25·m, 76 at 0.38·m, 48 at 0.5·m, 100 at `root_fillet` 0.5 mm; none at ρ = the cap in the scan; smallest non-severed waist 2.4e-4·m | D-11 checkpoint is mandatory; `root_mode` needs the generator to name this reason; T2 must include adjacent cutter teeth to see it |
| F8 | One external, published, tool-generated number exists: Zhang, AGMA 18FTM02, Table 7 example 7, KISSsoft 4.1530, hob without protuberance | The closed-form tangent junction gives 4.153036 at diametral pitch 8 (the only DP in 8.000 ± 0.001 that fits); D-08 said none exists | Surface to the human as a T4 option; it escalates under the 10× rule by construction (rounding-limited) |
| F9 | The three "undercut" predicates nest: undercut (ξ < 0) implies `rb > rf` | Algebraic proof below; 0 counterexamples in 556,920 combinations | `root_mode` can test cheap-to-expensive in that order; "tooth step either side" rows exist for each edge |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cutter definition, ρ cap, tip-land limit, undercut onset and `x_min` | `calc.py` (pure maths) | tests/ (closed-form T1) | `calc` is the one place that decides; it must stay kernel-free (import-linter contract) |
| Trochoid generation and junction/crossing solve | `calc.py` | tests/ (T2 oracle, T3 constants) | Pure `math`; `model.py` consumes plain floats in Phase 19 (ARCHITECTURE §0) |
| `root_mode` predicate and its refusal reasons | `calc.py` | — | Single owner of "does the trochoid apply" (D-10) |
| Refusal warning sentences | `calc.py` (one function keyed on the reason) | tests capture from it | L33 rule: never typed in tests |
| Independent proof (oracle, closed forms, cross-check) | `tests/` | `bench/` (full-grid T2, step measurement) | Must share no code with `calc` (L33 `_filleted_spoke_volume` precedent) |
| Root-shape step measurement (D-05), cost figures (D-14) | `bench/` + `bench/RESULTS.md` | — | Measured, recorded with host state; the step needs `model._fillet_corner` (cadquery), so it cannot live in `calc` or in a kernel-free test |
| Any kernel / outline / field / fixture contact | none in this phase | Phase 19 | Boundary fixed by the ROADMAP |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `math`, `dataclasses`, `typing.Literal` | CPython 3.12.13 [VERIFIED: `.venv/bin/python --version`] | all of the maths; frozen result types | The stack decision (L01, L23); `_involute_angle` and `centre_distance` are the in-repo precedents for sign-only bisection |
| pytest | 9.1.1 [VERIFIED: `pip list` in `.venv`] | the proofs | already installed |
| pytest-xdist / pytest-cov | 3.8.0 / 7.1.0 [VERIFIED: `pip list`] | `-n 8`, coverage floor | already installed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ruff / mypy / import-linter | 0.16.8 / 2.3.1 / 2.15 [VERIFIED: `pip list`] | the static gate (`make verify.static`) | every commit |
| cadquery / cadquery-ocp | 2.8.0 / 7.9.3.1.1 [VERIFIED: `importlib.metadata`] | only the bench step script (`model._fillet_corner`) | D-05 measurement, not `calc` or the kernel-free tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib bisection | numpy / scipy | Rejected by CONTEXT and REQUIREMENTS: scipy is pruned from the image, numpy costs +33 ms / +11 MiB in the kernel-free parent (STACK). Measured here: the whole 7,980-case product runs in 0.23 s in unoptimised pure Python, so there is nothing to buy |
| freecad.gears imported or vendored | recorded constants | GPL-3.0; used once, numbers recorded (T3) |

**Installation:** none. No new package, runtime or dev. `requirements.txt` stays at 31 pins [VERIFIED: `grep -c '==' requirements.txt` printed 31; `grep -rnE 'numpy|scipy' src/spur` printed nothing].

**Version verification:** nothing new to verify; the table lists what the `.venv` already holds.

## Package Legitimacy Audit

No external package is installed or recommended by this phase, so the legitimacy gate has nothing to check. freecad.gears is read once from GitHub into a scratch directory outside the repo and its output recorded as numbers; it is never installed, imported by repo code or vendored.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 GearParams (validated once, frozen)            tests/ (shares no code with calc)
        |                                        T1 closed form   T2 oracle (+adjacent teeth)
        v                                        T3 constants     tripwire     bench: D-05, D-14
 calc.profile(p) -> Profile (rb, rf, ra, psi_p, half_angle)         ^
        |                                                           |  compares
        v                                                           |
 calc.cutter(p, rho) ---- reads depth d = m*(1.25 - x) (same expression as rf), e = pi*m - s
        |    caps rho (floored 3 dp), tip land a, w_c = rho - d        |
        |    a(rho=0) < 0 ?  --> "tip land gone"                       |
        v                                                              |
 calc.root_mode(p, pr, requested, rho)  [owns every refusal]           |
   requested == radial ........ radial, "not requested"                |
   rb <= rf ................... radial, "nothing radial to replace"    |
   a(rho=0) < 0 ............... radial, "tip land gone"                |
   generator says severed ..... radial, "tooth severed"  (D-11, human)  |
   else ....................... trochoid                               |
        |                                                              |
        v   (only when mode == trochoid)                               |
 calc.trochoid_root(cutter) -> RootCurve | None -----------------------+
        xi = r*sin(al) - (d - rho*(1 - sin al))/sin(al)
        xi >= -eps*rb  -> tangent: end at beta_end = pi/2 - al, R_join = sqrt(rb^2 + xi^2)
        xi <  -eps*rb  -> crossing: bisect beta_b (R_E = rb), bisect beta_c (g = 0) on [beta_b, beta_end]
        N samples uniform in s = tan(beta) -> ((R, half_angle), ...) root circle -> junction
```

### Recommended Project Structure
```
src/spur/calc.py            # + cutter(), Cutter, root_mode(), RootMode, trochoid_root(), RootCurve,
                            #   undercut_onset()/x_min() closed forms, one warning function,
                            #   the epsilon constant with its measurement comment. Nothing else under src/spur/.
tests/test_trochoid.py      # calc-tier proofs: cutter, cap, domain, root_mode, sweep, T1, T3, tripwire
tests/trochoid_oracle.py    # T2 oracle helper, not collected (tests/composition.py precedent)
bench/trochoid_step.py      # D-05 step tables (imports model._fillet_corner) and the D-13 fallback grid
bench/RESULTS.md            # one new "Trochoid maths (Phase 18)" section: host state, epsilon, cap,
                            #   junction bar, sweep wall time, per-call costs, the two step tables
docs/architecture/gear-maths/implementation.md   # the layout table lists every calc piece; add the new ones
```
Test layout is Claude's discretion (CONTEXT); a sibling module is recommended: `tests/test_calc.py` is 1,554 lines and the commit-time slice excludes only four named files, so a new `tests/test_trochoid.py` runs in `make verify.fast` automatically (`Makefile` `test.fast`: `--ignore=tests/test_model.py --ignore=tests/test_pool.py --ignore=tests/test_api.py --ignore=tests/test_cli.py`).

### Pattern 1: The cutter, defined once
**What:** one frozen result holding every rack constant; every other function reads it.
**Constants** (`s` and `rf` quoted from `calc.profile`, `calc.py:96-98`: `s = m * (math.pi / 2 + 2 * x * math.tan(a)) - bl` and `rf=r - m * (1.25 - x)`):
```
d    = m*(1.25 - x)              # tip depth below the pitch circle: the same expression as in profile(), so rf == r - d bit for bit
e    = pi*m - s                  # cutter tooth width on the rolling line = the gear's space width; backlash enters here, thickening the cutter tooth
w_c  = rho - d                   # height of the corner-circle centre above the rolling line (negative for an ordinary cutter)
a    = e/2 + w_c*tan(al) - rho/cos(al)     # half-width of the flat tip land; a >= 0 required
cap  = (pi*m/4 + bl/2 - 1.25*m*tan(al)) / (1/cos(al) - tan(al))   # largest rho with a >= 0; independent of x
limit: tan(al) < (pi/4 + bl/(2*m)) / 1.25  <=>  a(rho = 0) > 0     # depends on bl/m
```
[VERIFIED: scratch run] With this `cutter`, `rb`, `rf`, `psi_p` equal `calc.profile`'s over 62,185 `GearParams`-valid, `check()`-clean gears (max difference 0.0). **Take `rf` from `Profile`, never `r − d`:** the first curve point is `(rf, ·)` exactly only if it is the same float (R(0) − rf = 0.0 in the run).
**Cap rounding:** floor to 3 dp (F3). **Domain:** decide on `a(ρ = 0) < 0`, not on a pressure-angle constant (F2).

### Pattern 2: The envelope in contact-normal angle (the form to implement)
**What:** the point of the corner circle whose normal passes through the instantaneous pole, parametrised by the angle β between that normal and the inward radial direction. With `n(φ) = (sin φ, cos φ)`, `t(φ) = (cos φ, −sin φ)` (θ measured clockwise from the space centre, tooth centre at π/z):
```
phi(beta) = (a + w_c*tan(beta)) / r
E(beta)   = (rf + rho*(1 - cos(beta))) * n(phi) + (rho*sin(beta) - w_c*tan(beta)) * t(phi)
R_E       = hypot(rf + rho*(1 - cos beta), rho*sin beta - w_c*tan beta)
theta_E   = phi + atan2(rho*sin beta - w_c*tan beta, rf + rho*(1 - cos beta))
half_angle (RootCurve's second value) = pi/z - theta_E
beta in [0, pi/2 - alpha]:  beta = 0 -> tangent to the root circle at theta = a/r;  beta = pi/2 - alpha -> the cutter's straight-flank foot
```
[VERIFIED: scratch run] Equals STACK's `E(φ) = C + ρ(C − I)/|C − I|` to 1.8e-15 mm on every `w_c < 0` case, equals the oracle to 1e-15 mm on `w_c > 0` and `w_c = 0` cases where STACK's form fails (F4), and at ρ = 0 reduces to the classical sharp-corner trochoid `rf·n + d·tan β·t`. Because it is a closed form in β there is no root-find for the curve itself; the only roots are the two below.
**Sampling variable:** use `s = tan β` uniform (`φ` is linear in `s`: `φ = (a + w_c·s)/r`). At `w_c < 0` this is exactly STACK's "uniform in φ" and reproduces its measured spline deviation: with the real `cq.Edge.makeSpline` and N = 16, 3.58e-5, 3.89e-5, 3.98e-5 mm at z = 8, 10, 14 (STACK 3.6–4.0e-5) [VERIFIED: scratch run, cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1]. Uniform in β instead was worse there (6.2–9.6e-5) and better only where `w_c > 0` (1.8e-5 vs 6.0e-5 at z 12, 14.5°, x 0.9, ρ 0.5). Unlike uniform-in-φ, uniform-in-`s` stays defined at `w_c = 0`. The bar is Phase 19's (CONTEXT).

### Pattern 3: Junction — closed form first, one or two bisections only when needed
- Roll of the cutter's flank foot along the line of action: `ξ = r·sin α − (d − ρ(1 − sin α))/sin α`, identical to STACK's `ξ_join = (m/sin α)[(z/2) sin²α − (1.25 − x − ρ*(1 − sin α))]`. **Undercut ⇔ ξ < 0.** `z_min = 2(1.25 − x − ρ*(1 − sin α))/sin²α`, `x_min = 1.25 − ρ*(1 − sin α) − z·sin²α/2` [VERIFIED: scratch run reproduces STACK's table: 30.7909 / 17.0967 / 11.5404 at ρ* = 0.38, 14.5°/20°/25°; the shipped formula reads 31.9029 / 17.0973 / 11.1978; `x_min` 0.41508 at z 10, 20°, ρ* 0.38].
- **Tangent (ξ ≥ −ε·rb):** no root-find. `R_join = sqrt(rb² + ξ²)` and the curve ends at `β_end`; the end point equals `Profile.half_angle(R_join)` to 7.6e-17 rad (19T, 25°, ρ 0.5, backlash 0.10), 5.6e-17 (backlash 0), −6.9e-18 (30T, 20°, ρ 0.38, backlash 0.10), 1.4e-17 (30T, ρ 0, backlash 0). PITFALLS measured 4.9e-17 and 6.9e-18; same order, the bar is re-measured in the phase.
- **Crossing (ξ < −ε·rb):** `R_E(β)` is increasing on `[0, β_end]` (0 violations in the sweep; do not rely on it unchecked, see below). Step 1: bisect `R_E(β) = rb` for `β_b`. Step 2: with `g(β) = θ_E − (π/z − Profile.half_angle(R_E))`, `g(β_b) > 0 > g(β_end)`; bisect for `β_c`. 60 halvings each. `half_angle` is only ever called at `R ≥ rb` (its `min(1.0, rb/R)` absorbs a last-ulp excursion), so it is never reused below `rb`. The curve is `[0, β_c]`; the crossing radius is `R_E(β_c)`. Example: z 10, m 1, 20°, ρ 0.38: form radius 4.725602 mm, `rb` 4.698463, β_c = 1.191144, β_end = 1.221730 [VERIFIED: scratch run; equals STACK's 4.72560/4.69846].
- **Invariant worth a test (shares nothing with the implementation):** the form radius does not depend on backlash. Measured spread over backlash 0, 0.05, 0.1, 0.3 at fixed x: 1.8e-15 mm (z 10), 0 (z 8), 0 (z 35). This is also what Zhang states ("Tooth thickness is not needed in either method A or B").
- **Guard after the solve:** assert `R` strictly increasing along the samples; if not, return `None` (a numerical failure the closed form did not predict, D-10). Also assert the crossing is the *first* sign change of `g` from `β_b` (cheap on the N samples); bisection finds an arbitrary root if `g` has three.

### Pattern 4: The degenerate-bracket rule at the double root (D-09)
The decision is `ξ < 0`; the bracket is attempted only when `ξ < −ε·rb`, otherwise the flank join is the form point. **ε is relative to `rb`.** [VERIFIED: scratch run] Bracket found down to |ξ| = 1e-4 mm at m 1 (rb 4.7–6.6), 1e-3 at m 10 (rb 58), 1e-5 at m 0.2 (rb 0.66); lost beyond that and intermittent below. Over 361 random allowed cases (α 14.5–30, m 0.2–10, backlash 0–0.5, ρ 0–0.5·m) the largest |ξ|/`rb` at which a bracket was lost was **1.0e-5** (scan resolution 4 steps per decade; median 3.2e-6). Recommended constant `1e-4·rb` (10× over the largest loss, the 10× rule applied to the constant itself); error of using the flank join where the bracket would have worked ≤ `ξ²/(2·rb)` = 5e-9·rb, i.e. 3e-7 mm at rb 58, so apply the fallback only after a failed bracket and only when |ξ| ≤ ε·rb (outside it a failed bracket is a numerical failure, `None`). The exact-threshold row is free: z 10, α 30°, x 0, ρ 0, backlash 0 has `z_min = 2·1.25/sin²30° = 10` exactly and float `ξ = −4.4e-15`; the sweep hit it as "bracket failure" before the rule existed. At a tuned shift: z 10, α 30°, ρ 0 has `x_min` = 0 exactly, so x = −0.05 / 0.05 are the field steps either side (`profile_shift` step 0.05, `params.py:42-43`); or z 10, α 20°, ρ 0.38, backlash 0 with `x_min` = 0.41508: x = 0.40 undercut, 0.45 tangent.

### Pattern 5: `root_mode` — what it still needs beyond CONTEXT's signature
CONTEXT fixes `root_mode(p, pr, requested="radial")`. Two things in it cannot be answered from that signature:
1. **ρ.** The severed-tooth refusal (F7) and the cap depend on ρ, and D-07 says ρ is an explicit mm argument. Recommend a keyword-only `rho: float = 0.0` (0 is legal; it is ignored when `requested == "radial"`). Phase 19 passes whichever ρ it binds.
2. **The generator.** "Tooth severed" has no closed form; the cheap order is requested → `rb ≤ rf` → no tip land → run the envelope and test `min(half_angle) > 0` along it. So `root_mode` calls a private `_envelope(cutter)` that returns a curve or a named reason; `trochoid_root` returns `None` on any reason. This keeps "root_mode owns every refusal" (D-10) at the cost of computing the curve twice if a caller calls both (the cutter is a frozen, hashable dataclass, so `functools.lru_cache` is available but unbounded caches need an L07-style bound; do not add it speculatively).
Reasons (D-03's four plus the one this research adds): `not requested`; `nothing radial to replace` (`rb ≤ rf`); `tip land gone`; `tooth severed` (pending the D-11 checkpoint); and `bracket degenerate` retained only as the label for a numerical failure outside ε, which the sweep must show never occurs in the box.
**Nesting (F9):** `ξ < 0` implies `rb > rf`. Proof: undercut gives `(z/2)·sin²α < 1.25 − x − ρ*(1 − sin α) ≤ 1.25 − x`, and `sin²α = (1 − cos α)(1 + cos α) > 1 − cos α`, so `(z/2)(1 − cos α) < 1.25 − x`, which is `rb > rf`. Checked over z 6–200, α 14.5–35 step 0.5, x −0.6 to 1.0, ρ* 0–0.6: 0 counterexamples in 556,920 combinations. A test can assert the nesting over the sweep.

### Pattern 6: The T2 oracle — what it computes and why it needs the neighbours
**What:** a gear-frame point P is on the cut boundary iff it lies on the cutter at its own rolling angle and strictly inside the cutter at no other. The cutter is built from plain definitions only (half-width `e/2` at the rolling line, flank angle α, flat tip at depth d, tip radius ρ), not from `E(β)`.
```
rack frame of P at rolling angle phi':  D = P - r*n(phi');  w = D.n(phi');  u = r*phi' + D.t(phi')
cutter tooth = rounded trapezoid: core with corners (-+a, w_c) and (-+(a + (H - w_c) tan al), H), offset by rho
sd(P, phi') = signed distance to core - rho            (negative inside the cutter)
sd over neighbouring teeth: min over k in {-1, 0, +1} of sd(u - k*pi*m, w)     <-- needed to see the severed tooth
min over phi' in [-2*pi/z, 2*pi/z]: grid of 2001 angles, then golden-section refinement of the best bracket
```
[VERIFIED: scratch run] Results (m 1 unless noted):
- Genuine segment, z 10, 20°, ρ 0.38: max |sd| = **1.1e-15 mm**. Points left running past the form point to `β_end`: penetration **5.19e-2 mm**. Thirteen orders of separation (STACK found eight: −1.6e-11 and +3.9e-3, a coarser floor because it does not refine; the golden-section step is what takes the floor from 1e-11 to 1e-15).
- 500 random allowed-box cases (m 0.2/1/1.75/10, α 14.5–35, backlash 0–1, x −0.6…1, ρ 0…0.5·m, 21 points each): non-severed worst gouge and worst |sd| both **6.7e-15·m**. 0 failures. Cost 0.12 s per 21-point case in unoptimised Python (about 10 rows ≈ 1.2 s in the gate).
- Severed cases: **without** the neighbouring teeth the oracle reads 0 on them (it cannot see the interaction); **with** them it reports 0.141 mm (z 6, 14.5°, x −0.6, ρ 0) and 0.0201 mm (z 6, 14.5°, x −0.5, ρ 0) of gouge while `min half_angle` is −0.0474 and −0.0066. A case with positive waist (z 7, x −0.6, ρ 0, `min h` = +0.0021) reads 4e-16. So the closed predicate `min half_angle ≤ 0` and the oracle agree.
- Sensitivity for the tripwire: moving ρ by δ in the implementation moves the worst |sd| by **0.221·δ** (z 10, 20°, ρ 0.38): δ = 1e-9 → 2.2e-10; 1e-7 → 2.2e-8; 1e-6 → 2.2e-7; 1e-4 → 2.2e-5.
**Bar arithmetic (L33 D-06):** noise floor 6.7e-15·m (≤ 6.7e-14 mm at m 10); a bar of 1e-9 mm gives ≥ 1.5e4× headroom over it; the tripwire at δρ = 1e-6 mm (2.2e-7 mm) is 220× over the bar. Both well over the 10× line, so T2 should not escalate. Re-measure before writing the constant.

### Pattern 7: T3 — the freecad.gears one-off, procedure and recorded provenance
- Source: `https://github.com/looooo/freecad.gears`, file `pygears/involute_tooth.py`, class `InvoluteTooth.undercut_points`, `undercut_function_x/y`. **Commit that last touched the file: `4cc4b1a233c232e15c3fdfb8a35909aa0d828796` (2026-09-15, "ruff refactoring"); repository HEAD `83ec154b1925347622b61812f75d2ed51e956b9f` (2026-09-15, "gh-action: add ruff command"); package `__version__` "1.4.0"; licence GPL-3.0** (GitHub licence API spdx `GPL-3.0`, `LICENSE` 35,149 bytes; the file header carries the GPL v3 notice) [CITED: gh api repos/looooo/freecad.gears, read 2026-10-07]. Matches FEATURES' HEAD (83ec154) so the tree has not moved.
- Procedure that never imports or vendors: fetch the three files (`__init__.py`, `involute_tooth.py`, `_functions.py`; numpy only) with `gh api 'repos/looooo/freecad.gears/contents/pygears/<f>?ref=4cc4b1a…'` into a fresh directory outside the repo; run from a script that `sys.path.insert`s that directory; instantiate `InvoluteTooth(m=1, num_teeth=z, pressure_angle=radians(20), clearance=0.25, shift=x, backlash=bl, undercut=True)`; read `undercut_points(num=200)`; **record literals** (a few ψ, X, Y rows per gear) in the repo test with the provenance docstring. The repo never contains their code.
- Matching: their parametrisation is `R = (df/2)/cos ψ`, angle `ψ − (df/dw)·tan ψ`, rotated by `−undercut_rot − π/z + backlash/(2r)`. It is the same curve as `E(β)` at ρ = 0 under `tan ψ = (d/rf)·tan β` (algebraic identity, shown in the scratch run), so the comparison is exact point-for-point, not interpolated. Their `clearance` 0.25 and `shift` x reproduce `d = (1.25 − x)·m`; their `angular_backlash/2` is the same `backlash/2` that enters `a`.
- Result [VERIFIED: scratch run against the real module, 1,972 points over 12 cases: z 8, 10, 14; x 0, 0.3; backlash 0, 0.1; m 1; 20°]: worst |ΔR| = **2.66e-15 mm**, worst |Δangle| = **3.05e-16 rad** (STACK: 1.8e-15 and 1.1e-16, z 8/10/14, x 0/0.3). Same order; STACK did not cover backlash 0.1 and this does.
- What T3 is and is not: it checks the rolling convention, the depth, the tip-land and the backlash entry against someone else's code, for a sharp corner only. It does not check the crossing (their `undercut=True` trims polylines) or ρ > 0. Its "stated resolution" is float64 closed-form arithmetic, so there is no printed resolution to quote; say so in the docstring and use bar ≥ 10× the larger measured gap.

### Pattern 8: D-05 — what "the step" is, and prototype numbers
Define the step as the maximum same-radius arc gap `R·(h_trochoid(R) − h_shipped(R))` between the trochoid outline and the shipped analytic outline (L09 fillet plus lead-in, built from `model._fillet_corner` and `calc.spline_start`) on the same gear, over the root zone. That is what FEATURES' "shipped-versus-true gap" table measures, and it is the discontinuity a user would see if the mode flipped at that edge. It needs `cadquery.Vector` via `model._fillet_corner`, hence a `bench/` script, not `calc`.
[VERIFIED: scratch run, m 1, 20°, x 0, backlash 0, shipped fillet = ρ] Undercut threshold: 16T 0.1479, **17T 0.1463, 18T 0.1449**, 19T 0.1433, 25T 0.1312 mm (FEATURES: 0.143, 0.141, 0.128; agreement within 0.003). With ρ = fillet = 0.471: 17T 0.1328, 18T 0.1329. The `rb = rf` crossover (z 41: `rb − rf` = +0.0137 mm; z 42: −0.0165 mm): ρ = fillet 0.38 → 0.0800 mm; ρ = fillet 0.471 → 0.1213 mm (z 40: 0.0838 / 0.1214); sharp cutter ρ = 0 → −0.1885. **The figure depends on ρ and the maximum sits at the root circle** (R = rf), so each table row must state ρ and the shipped fillet. The undercut-threshold table is the O1 counterfactual (under D-02 the trochoid applies on both sides of 17/18 and the join just changes kind); the crossover table is what a user sees. These do not contradict D-01's "≈0.14·m" (0.145 vs 0.14, +3%); the plan should state the comparison rule before measuring (for example "within ±25% of 0.14·m means D-01's premise holds") so a contradiction is decided by a stated line, not afterwards.

### Anti-Patterns to Avoid
- **Using `E(φ) = C + ρ(C − I)/|C − I|` without the sign (F4).** Gouges where ρ > d, divides by zero at ρ = d. Use the β form or at minimum carry the sign.
- **The centre path or an offset of it** (PITFALLS 5): an offset of the centre path swallow-tails; the oracle catches both.
- **A single-tooth oracle.** It reads 0 on severed teeth.
- **Rounding the cap to nearest** (F3).
- **A pressure-angle constant for the domain limit** (F2); a millimetre epsilon on ξ (F6).
- **Reusing `Profile.half_angle` below `rb`**, or building the curve's end point from it instead of from `E` (the end float must come from one call so Phase 19's spline start shares it).
- **Sampling the whole β range for an undercut gear**; the curve ends at `β_c`, not `β_end` (past it the oracle reads 5.19e-2 mm of gouge at z 10, 20°, ρ 0.38). Also do not read the x = −1 rows of STACK's grid as evidence: `GearParams` rejects them and their retained curves rise above `ra` (up to 1.13·`ra`) and sever the tooth.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Inverse involute, bisection pattern | a new solver style | the `_involute_angle` pattern (`calc.py:1158-1171`): fixed bracket, 60 halvings, sign-only | no starting guess can leave the bracket; L08 |
| Convex-polygon signed distance (T2) | a polygon-boolean dependency | ~20 lines of stdlib in `tests/trochoid_oracle.py` | STACK: shapely/pyclipper are a dependency for 40 lines |
| The reference curve for T3 | importing or vendoring freecad.gears | recorded literals with provenance | GPL-3.0 |
| Warning sentences | strings typed into tests | one calc function keyed on the reason; tests call it | L33 rule |
| Printed-versus-used ρ | a separate rounding for the warning | floor once, use that number everywhere | L08: the part and the printed number cannot disagree |

**Key insight:** the generator is a closed form plus two root-finds; every piece of "cleverness" in the milestone research (the φ-bracket, Newton, scipy) either failed at an edge or bought nothing measurable. The risk in this phase is not computing the curve, it is the edges of the allowed box.

## Common Pitfalls

### Pitfall 1: A sweep floor that does not cover what it is called
**What goes wrong:** D-12 treats "STACK's 7,296" as the floor. It is the 7,980-case product minus the 684 `w_c ≥ 0` rows (x = 1 with ρ* ≥ 0.25), counts 912 `a < 0` rows as solved, and includes x = −1.
**Why:** STACK's formula could not run the `w_c ≥ 0` rows, so they were dropped without a note.
**How to avoid:** write the grid in the test explicitly; include x = −0.6 instead of −1 (`params.py:42` rejects −1); tally by outcome (`radial`, `tip land gone`, `capped`, `tangent`, `crossing`, `tooth severed`) and assert the counts; keep the x = 1, ρ ≥ d rows.
**Warning signs:** a sweep that passes with a smaller number of cases than the product.

### Pitfall 2: The cap rounds up past the geometry
**What goes wrong:** `round(cap, 3)` can exceed the true cap by up to 5e-4 mm and the resulting cutter has `a < 0`.
**How to avoid:** floor to 3 dp; test the exact row (m 0.5, 15°, backlash 0: cap 0.29353, floored 0.293, rounded 0.294 refuses).
**Warning signs:** "tip land gone" on a gear whose ρ = 0 cutter has a land.

### Pitfall 3: The tooth is cut through (the two-flank interaction)
**What goes wrong:** at small z, large negative x and small ρ, the trochoid of one space crosses the tooth centreline, i.e. meets the mirrored trochoid of the next space. The one-flank sweep cannot see it; `check()` does not refuse it (it works on the radial model, `calc.py:553-560`).
**Why it happens:** the retained curve is a graph over R with `min half_angle ≤ 0`.
**How to avoid:** `half_angle` along the curve, tested `> 0`, as a named refusal in `root_mode`; the oracle with neighbouring teeth as the independent check; checkpoint with the human before the rule is fixed (D-11).
**Warning signs:** a negative waist; `min h ≤ 0`; oracle gouge with neighbours on.

### Pitfall 4: A relative question asked in absolute units
The bracket loss, the tip-land limit and the cap all scale with `rb`, `backlash/m` and `m`. A test written only at m 1 passes while m 10 or 0.2 fails. The sweep box must carry m 0.2 and 10 with backlash up to 1 (D-12), and the epsilon test must carry two radii.

### Pitfall 5: Coverage and lint traps in new `calc` code
Every fallback arm (refusals, `None` returns, the ε arm) needs a test that reaches it or the 96% branch floor moves; arms unreachable inside the box need an out-of-box direct call (a hand-built cutter with `a < 0`; a `ξ` inside ε built by choosing x). `N806` forbids `wC`; `ERA001` flags comments shaped like code; `warn_unreachable` flags a refusal branch mypy can prove dead.

### Pitfall 6: Planning trigger of a must-debt item
`docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` (Severity: must) names "Phase 18 planning" as a revisit trigger (`docs/tech_debt/INDEX.md`). The fix is outside SC5's file list (`pool.py`), so the plan should schedule a read and a recorded decision, not a `src/spur` edit. New tests here are pure maths and spawn no processes, so they add no exposure to the flake.

### Pitfall 7: Printing a number that depends on a refused case
The Phase 19 sentence prints `z_min` and `x_min`; they are only honest if `root_mode` agrees the trochoid applies. Phase 18's closed forms must take the same `Cutter` (with the capped ρ), not retype `1.25`.

## Code Examples

Verified patterns from the scratch run (stdlib only; adapt names to lint rules, these are not repo code).

### Cutter, envelope and junction
```python
# Source: scratch prototype, run 2026-10-07; formulas cross-checked against freecad.gears (rho = 0) and the oracle below
import math

def cutter(z, m, al_deg, x, bl, rho):
    al = math.radians(al_deg)
    r = m * z / 2
    s = m * (math.pi / 2 + 2 * x * math.tan(al)) - bl      # as calc.profile
    d = m * (1.25 - x)                                      # same expression as rf = r - m*(1.25 - x)
    e = math.pi * m - s
    w_c = rho - d
    a = e / 2 + w_c * math.tan(al) - rho / math.cos(al)     # tip land half-width; >= 0 required
    return dict(z=z, r=r, rb=r * math.cos(al), rf=r - d, al=al, rho=rho, d=d, w_c=w_c, a=a)

def envelope(c, beta):
    phi = (c["a"] + c["w_c"] * math.tan(beta)) / c["r"]
    n_comp = c["rf"] + c["rho"] * (1 - math.cos(beta))
    t_comp = c["rho"] * math.sin(beta) - c["w_c"] * math.tan(beta)
    return math.hypot(n_comp, t_comp), phi + math.atan2(t_comp, n_comp)    # (R, theta from the space centre)

def bisect(f, lo, hi, n=60):                                # sign-only; f(lo), f(hi) of opposite sign
    up = f(lo) > 0
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if (f(mid) > 0) == up else (lo, mid)
    return 0.5 * (lo + hi)
```
Crossing: `b_end = pi/2 - al`; `xi = r*sin(al) - (d - rho*(1 - sin(al)))/sin(al)`; if `xi >= -1e-4*rb` stop at `b_end`; else `b_b = bisect(lambda b: envelope(c, b)[0] - rb, 0, b_end)`, `g = lambda b: theta_E(b) - (pi/z - half_angle(R_E(b)))`, `b_c = bisect(g, b_b, b_end)`; sample `s = tan(b)` uniformly on `[0, tan(b_stop)]`; points `(R, pi/z - theta)`.

### Per-call cost, measured (prototype, unoptimised, host load 14 to 27, so upper bounds)
`cutter()` 0.55 µs; tangent solve with N = 16: 5.4 µs; undercut solve (two 60-step bisections, N = 16): 58 µs (PITFALLS' estimate was 73 µs for one 60-step bisection plus call overhead); slowest single case in the 7,980 product 0.18 ms (STACK 0.19); the whole 7,980-case product with analysis 0.23 s. `derive(GearParams())` read **14.5 µs** best of 5 (`.venv/bin/python -m timeit -r 5 -s "from spur.calc import derive; from spur.params import GearParams; p=GearParams()" "derive(p)"`), host 1-minute load 14.33 (5-min 8.33, 15-min 6.93), Apple M2 Max, Python 3.12.13, 2026-10-07 21:18; the docstring says 11.5 µs, PITFALLS read 20.4 µs at load about 6.8. The figure moves with load, so the docstring must carry the number, the load and the date together (the form the existing docstring uses).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Radial lead-in plus analytic fillet below the base circle (L09/L10, shipped) | Envelope of the hob's tip arc, junction by tangency or crossing | this milestone | Phase 19 makes it reachable; Phase 18 makes it exist and proves it |
| z_min = 2(1 − x)/sin²α (shipped warning) | `2(1.25 − x − ρ*(1 − sin α))/sin²α` | derived, STACK | agree at 20°/ρ* 0.38 to 6e-4 teeth; 31.90 vs 30.79 at 14.5°, 11.20 vs 11.54 at 25° |
| One-flank sweep (STACK) | sweep plus neighbouring-space interaction | this research | needed for D-11 |

**Deprecated/outdated:** the φ-parametrised envelope for ρ ≥ d; "≈32.1°" as a fixed limit; "7,296 cases" as a floor.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Zhang's Table 7 is in diametral-pitch units and example 7 has diametral pitch 8, module 0.125 length units; inferred, because the table prints no module or pitch. Supporting evidence: only 8.000 ± 0.001 reproduces 4.1530 ± 5e-5 from the printed Z, φ, ded. factor 1.3, ρ 0.04, δ0 0 | Pattern 7 / F8 | If wrong, T4 would be pinned to a coincidence; low risk (a round number landing within 1e-3 of an integer is unlikely by chance) but the human should confirm before it becomes a bar |
| A2 | "Ded. factor" 1.3 means `(r − rf)/m` (it is printed as `(r − rf)·Z·cos φ/(2·rb)` with `rb = r·cos φ`), so `x = −0.05` in this project's terms | F8 | Same as A1; both rest on reading the table image |
| A3 | ISO 21771's `d_Ff` equals the cutter-envelope junction for a basic rack. Zhang's definition ("diameter of a circle at which the root fillet curve intersects or joins the involute") matches ours and the KISSsoft point agrees, but the ISO clause was not readable | D-08, Open Questions | Printing the number as "ISO form diameter" would be unproven (L08); CONTEXT already labels it the cutter-envelope junction |
| A4 | The absence of a public reference table is still LOW: only a paywall-limited search was possible; one point was found by reading a referenced article table | F8 | More anchors may exist (Zhang's other nine rows use protuberance hobs we do not model) |
| A5 | The epsilon constant `1e-4·rb` and the 1.0e-5 loss bracket come from 361 random cases at 4 scan steps per decade on a prototype; the in-repo measurement must redo them | Pattern 4 | The constant could move by a factor of a few; the 10× margin is there for that |
| A6 | Per-call and sweep timings are prototype, unoptimised, taken at host load 14–27 | Code Examples | Upper bounds; the plan re-measures with load beside the figure (D-14) |
| A7 | `R_E(β)` is monotone on `[0, β_end]` for every allowed gear: observed (0 violations in about 203,000 solves) not proved | Pattern 3 | A violation inside the box would be a D-10 `None`; the post-solve monotone guard turns it into a counted failure |
| A8 | The module-1 prototype results transfer to other modules because only `backlash/m` and the absolute backlash break scale-invariance; the 500-case oracle run covers m 0.2/1.75/10 | Pattern 6 | m-specific failure at an untested (z, α, x); the sweep's corner rows are the guard |

## Open Questions

1. **D-11 checkpoint: the severed-tooth class.** What we know: inside `GearParams` limits and `check()`-clean there are gears whose trochoid cuts the tooth through (z 6–9, α ≤ 24°, x ≤ −0.4 at ρ = 0; fewer at larger ρ, e.g. 100 of 28,957 `rb > rf` gears at ρ = 0.5 mm; none at the cap among those tested), and positive waists as thin as 2.4e-4·m. What is unclear: the rule. Options for the human (CONTEXT: no default): (a) refuse in calc with reason "tooth severed" when `min half_angle ≤ 0` (recommended minimum; L08); (b) refuse below a waist floor (Phase 19's REQ-derived-numbers waist-floor decision, 422 or warning); (c) allow and print a warning. Recommendation: (a) in Phase 18, with the floor deferred to Phase 19 as the roadmap already says.
2. **D-08 revisit: adopt the Zhang/KISSsoft point as T4?** One published, tool-generated value (4.1530, 4 decimals, hob without protuberance, ρ 0.04, Z 35, 22.5°) matches the closed-form tangent junction at 4.153036. It anchors only the tangent branch and rests on A1/A2. Its bar is rounding-limited: half the last printed digit is 5e-5 (about 1.3e-3 mm at DP 8) against an observed gap of 3.6e-5, headroom 1.4×, which is under the 10× line by construction, so it goes to the human if adopted. Sensitivity d(form diameter)/dρ = 0.742, so a tripwire of 1e-3 length units moves it 15× the bar. Recommendation: offer it; adopting it costs about ten lines and does not change what the phase builds.
3. **Does `root_mode` take ρ?** Recommend yes, keyword-only (Pattern 5). The planner should confirm with the CONTEXT author since CONTEXT lists the signature without it.
4. **Where does the D-05 measurement live?** Recommend `bench/trochoid_step.py` (it needs `model._fillet_corner`); a one-off run would violate "every scratch number is re-created inside the repo".
5. **Quiet host for D-14?** No quiet bar is required by CONTEXT (no gate rests on it); record load. A quiet reading would tighten the numbers but is not required.
6. **ISO 21771 parity.** RESOLVED as unobtainable here: the standard is paywalled and the public sample lacks the clause (STACK); Zhang's paper defines the same circle. Keep the label "cutter-envelope junction" (D-08). Confidence LOW for parity, MEDIUM for the definition.
7. **The must-debt trigger "Phase 18 planning"** (Pitfall 6): schedule a read and a recorded decision in the plan; not a `src/spur` edit.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + `.venv` | everything | yes | 3.12.13 | none needed |
| pytest, xdist, cov, ruff, mypy, import-linter | the gate | yes | 9.1.1, 3.8.0, 7.1.0, 0.16.8, 2.3.1, 2.15 | none needed |
| cadquery / cadquery-ocp | `bench/trochoid_step.py` only | yes | 2.8.0 / 7.9.3.1.1 | none needed |
| `gh` CLI | T3 provenance fetch (one-off) | yes | authenticated (API calls succeeded) | WebFetch of the raw file |
| numpy | T3 one-off only (the freecad.gears package needs it) | yes, in `.venv` | 2.5.3 | not used by repo code |
| Docker | not needed (`make verify`, not `make check`) | not probed | — | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` (keys present: `workflow._auto_chain_active`, `workflow.use_worktrees`, `git.branching_strategy`), so it is treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `filterwarnings = ["error", ...]`, `--strict-markers --strict-config`) and `[tool.coverage.*]` (`branch = true`, `fail_under = 96`) |
| Quick run command | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -q -n0"` (no coverage, serial; `PYTEST_ARGS` comes last so `-n0` wins) |
| Commit-time slice | `make verify.fast` (11.3 s warm per L36; includes every new test file by default) |
| Full suite command | `make verify` (about 64 s; run by hand before every push) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-cutter-defined-once | cap reconciliation (0.318·m / 0.363·m); cap and domain limit one step either side at backlash 0 and at the default; ρ = 0 legal; capped value floored and warned at 3 dp from the one warning function; depth equals `profile`'s expression and first curve point is `(rf, ·)`; junction equals `Profile.half_angle` at backlash 0 and 0.10 to a re-measured bar | unit | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -q -n0 -k cutter"` | no, Wave 0 |
| REQ-trochoid-root-generated | explicit-grid sweep (7,980 product with x −0.6 for −1, plus corners: α 30/33.0/33.5/35, m 0.2/10, backlash 0–1, x −0.6/1.0, ρ at the cap and at `root_fillet`), outcome tally, zero bracket failures, strictly increasing R, nothing above `ra`; ε rows (ξ/rb at −1e-3, −1e-9; exact-threshold z 10, 30°, ρ 0); `RootCurve` immutability; `None` paths via direct out-of-box calls; backlash-independence of the form radius | unit + sweep | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -q -n0 -k 'sweep or root_curve or epsilon'"` | no, Wave 0 |
| REQ-root-mode-single-predicate | all 44 fixture records read `radial` / "not requested"; `rb ≤ rf` one tooth step (z 41/42 at 20°, x 0, m 1); tip land one field step (backlash 0: 32.0/32.5; default gear: 33.0/33.5); undercut onset one tooth step (17/18 at 20°, ρ 0.38) and one field step at a tuned shift (z 10, 20°: x 0.40/0.45); severed rule per the D-11 answer; nesting `ξ < 0 ⇒ rb > rf` over the sweep; reasons captured from the warning function | unit | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -q -n0 -k root_mode"` | no, Wave 0 |
| REQ-trochoid-proved-independently | T1 closed forms; T2 oracle (with adjacent teeth) on a handful of rows in the gate; T3 recorded constants with provenance docstring; ρ tripwire (δρ = 1e-6 mm) seen red; every bar's two numbers and headroom in the docstring; any bar under 10× to the human | unit | `make test.fast PYTEST_ARGS="tests/test_trochoid.py -q -n0 -k 'oracle or freecad or tripwire or closed_form'"` | no, Wave 0 |
| (D-05, D-13, D-14 records) | step tables, full-grid T2 and costs in `bench/RESULTS.md`; the sweep's wall time at `-n 8` recorded | bench | `.venv/bin/python -m bench.trochoid_step` and `.venv/bin/python -m timeit …` | no, Wave 0 |

### Sampling Rate
- **Per task commit:** the plain `git commit` (the L36 hook runs `make verify.fast`), plus the four SC5 checks by hand: `git diff --exit-code tests/regression/pre_v0_2.json`; `git diff --name-only 807fd2d -- src/spur | grep -v '^src/spur/calc.py$'` prints nothing (807fd2d is `git merge-base HEAD origin/main`, read this session); `grep -rnE 'numpy|scipy' src/spur` prints nothing; `grep -c '==' requirements.txt` prints 31.
- **Per wave merge:** `make verify` (full gate).
- **Phase gate:** `make verify` green, state the result line, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_trochoid.py` — covers all four requirements
- [ ] `tests/trochoid_oracle.py` — the T2 oracle helper (non-collected, like `tests/composition.py`)
- [ ] `bench/trochoid_step.py` and a `bench/RESULTS.md` section — D-05, D-13 fallback, D-14
- [ ] `docs/architecture/gear-maths/implementation.md` layout rows for the new `calc` pieces (docs only; `strategy.md` and `README.md` stay untouched per CONTEXT)
- Framework install: none.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. The phase adds pure functions to `calc.py` and tests; no endpoint, no input surface, no new dependency.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes, indirectly | every input reaches `calc` through `GearParams` (validated once, ranges `params.py:34-49`); the new functions add no unvalidated entry point |
| V6 Cryptography | no | — |
| V14 Configuration / supply chain | yes | no new package; GPL code is neither installed nor vendored; `requirements.txt` stays at 31 pins |

### Known Threat Patterns for stdlib-math geometry

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| NaN/inf or domain error from `acos`, `atan`, division by zero reaching a printed number | Tampering / Information integrity (L08) | `min(1.0, rb/R)` as in `half_angle`; a refusal before any division by a quantity that can be zero (`tan(π/2 − α)` is finite for α ≥ 14.5°; the φ-form's `|C − I| = 0` does not exist in the β form) |
| Unbounded loop on adversarial parameters | Denial of service | fixed 60-step bisections; no data-dependent iteration count |
| A plausible wrong number from a degenerate construction | Tampering (L08) | `None` plus a warning and the analytic fallback; the sweep must show none unexplained inside the box |
| Licence contamination | (compliance) | T3 as recorded numbers only |

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `CLAUDE.md`; `.planning/phases/18-trochoid-maths-proved/18-CONTEXT.md` and `18-DISCUSSION-LOG.md`; `.planning/REQUIREMENTS.md`; `.planning/STATE.md` (first 413 lines); `.planning/research/{SUMMARY,STACK,FEATURES,PITFALLS,ARCHITECTURE}.md`; `src/spur/calc.py` (lines 1–130, 200–300, 940–1010, 1150–1191); `src/spur/params.py:25-60`; `src/spur/model.py:90-200`; `Makefile`; `pyproject.toml`; `bench/RESULTS.md` (header, Phase 10 and Phase 17 sections); `bench/README.md`; `docs/architecture/decision_log.md` (L03, L08, L09, L10, L33); `docs/architecture/gear-maths/implementation.md`; `docs/tech_debt/INDEX.md` and the resource-tracker debt file; `tests/test_calc.py` (head, centre-distance oracle, lead-in rows); `tests/conftest.py`; `tests/composition.py` head.
- Scratch stdlib/cadquery runs this session (scratchpad, outside the repo): cutter vs `profile()` (0.0 difference, 62,185 gears), envelope φ-form vs β-form (1.8e-15 mm), junction equality, the 7,980 product and the 62,185-gear allowed box, the swept-cutter oracle (500 random cases, severed cases, past-the-form-point separation, tripwire sensitivity), the epsilon scans (400 random cases drawn, 361 usable), the real freecad.gears module run at commit 4cc4b1a, `cq.Edge.makeSpline` deviation at N = 16, `derive()` timing, the D-05 prototype tables using `model._fillet_corner`.
- `gh api repos/looooo/freecad.gears` (licence GPL-3.0, HEAD 83ec154b1925347622b61812f75d2ed51e956b9, last commit on `pygears/involute_tooth.py` 4cc4b1a233c232e15c3fdfb8a35909aa0d828796, 2026-09-15) [CITED: https://github.com/looooo/freecad.gears]

### Secondary (MEDIUM confidence)
- Zhang, S., "Methods to Determine Form Diameter on Hobbed External Involute Gears", AGMA 18FTM02 (Sept 2018), via Gear Solutions: the hob model (tip arc, optional transitional edge, `δ0 = 0` means no protuberance and `φ2 = φ`), the form-diameter definition, "Tooth thickness is not needed in either method", and Table 7 (image `GS-0619-Feat-2-table-7.jpg` read directly: example 7, Z 35, φ 22.5°, ded. factor 1.3, δ0 0, ρ_a0 0.04, KISSsoft 4.1530) [CITED: https://gearsolutions.com/features/methods-to-determine-form-diameter-on-hobbed-external-involute-gears/]. Printed with AGMA's permission; one number is recorded as a fact with attribution.

### Tertiary (LOW confidence)
- ISO 21771 clause text: not available (paywalled previews contain no form-diameter equations; search results 2026-10-07). Parity with `d_Ff` unproven.
- The absence of any other public reference table: search only.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new and all versions read from the `.venv`.
- Architecture / maths: HIGH, re-derived and run against `calc.profile`, an independent oracle and the real freecad.gears module; the two places where it departs from STACK (F4, F5) were found by the sweep and the oracle.
- Pitfalls: HIGH for F1–F9 (each has a run behind it); MEDIUM for A5 and A7 (observed, not proved).
- External anchor: MEDIUM for the Zhang point (A1, A2); LOW for ISO parity.

**Research date:** 2026-10-07
**Valid until:** about 30 days for the maths; the freecad.gears commit is pinned by sha, so the T3 record does not expire
