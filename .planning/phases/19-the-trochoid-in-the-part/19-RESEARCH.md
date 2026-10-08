# Phase 19: The Trochoid in the Part - Research

**Researched:** 2026-10-08
**Domain:** wiring the proved Phase 18 hob-root curve (`calc.RootCurve`) into the CadQuery outline, the printed numbers and the three interfaces behind one default-off `Literal` field, without moving any part a shared link produces today
**Confidence:** HIGH for every kernel fact and number marked "scratch run" (built and measured this session on the repo's `.venv`, HEAD `cb5fbd9`); HIGH for the in-repo seams (all files read this session); MEDIUM for the thresholds proposed for guards, the kernel bar and the waist floor (they rest on a 5,159-gear sample of the sweep product, not the whole box, and two of them are human checkpoints by the project's own 10x rule).

How to read the tags. `[VERIFIED: scratch run]` = built or computed this session by throwaway scripts kept in the scratchpad (outside the repo); every such number is a bracket for the planner and must be re-created inside the repo as a test or `bench/` row with host load, kernel pair and date beside it (the 18-RESEARCH rule, PITFALLS 23). `[VERIFIED: path:lines "quote"]` = a discrete in-repo value, file opened with `Read` this session, quoted verbatim. `[CITED: file]` = read from the named project document. `[ASSUMED]` = proposal or inference, listed in the Assumptions Log. No external library or web source was needed: every API claim was checked against the installed cadquery 2.8.0 source (`inspect.getsource`) and every geometry claim by running it.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The two new fields**
- **D-01:** **`root_fillet` is reinterpreted as the cutter tip radius ρ in trochoid mode.**
  In radial mode it stays the analytic fillet radius (L09, unchanged). In trochoid mode its
  millimetre value is passed to `cutter()` as ρ, capped by the cutter's geometric maximum
  and warned with the cap sentence `root_warnings` already carries (L03); ρ = 0 is a sharp
  hob and legal. The default 0.5 mm stays (L05); on small modules it is capped (0.471 mm
  at m 1, 20°) and the warning says so. No field is ever ignored, so no ignored-field
  sentence is needed. The field's help text and the README parameter row say both
  meanings. Rejected: a new `cutter_tip_radius` mm field (two controls for one root, and
  a user-set value ignored-and-warned in the other mode); a module-factor ρ* field (breaks
  L05's absolute-millimetre rule).
  — **Reversibility:** costly — a later separate ρ field would have to keep reading
  `root_fillet` for every shared link that set it under trochoid mode.
- **D-02:** **The mode field is `root_shape: Literal["radial", "trochoid"]`, default
  `"radial"`, group Teeth, after `tip_chamfer`.** Values are 18 D-03's `RootShape`
  literal, so `calc` maps nothing. Written with plain `Field` like `recess_sides`
  (`params.py:91-93`), no `step`; `cli.py` renders a `Literal` through `choices=`,
  `app.js` renders `enum` as a `<select>`. Never a `bool` (`--flag false` reads true).
  Rejected: `root_mode` (reads as a setting, and collides with the function's name);
  `root: analytic | hob` (diverges from the Phase 18 literal).
  — **Reversibility:** one-way — the field name is in every shareable link and the CLI
  flag from the first release that ships it.

**Root numbers under the trochoid**
- **D-03:** **`root_thickness` and `root_gap` read null with one warning where the trochoid
  applies.** Both fields widen to `float | None`; the warning names why (the thickness at
  the root circle is ill-conditioned under a hob root — FEATURES: 4.68 mm at rf + 0.001·m
  falling to 3.51 mm at rf + 0.3·m on the default gear, against the 3.253 mm the radial
  flank prints). In radial mode both keep their numbers, so the fixture's 19 pinned fields
  are untouched. Rejected: redefining both at the form circle (one field name meaning two
  things by mode, PITFALLS 6); new form-circle thickness/gap fields (every new number needs
  its own proof; nobody asked for them).
- **D-04:** **`root_form_d` ships in `DerivedDimensions`**: twice the junction radius from
  `RootCurve`, 3 dp, null in radial mode and on replay, described as the *cutter-envelope
  junction* and never as ISO 21771 form diameter (18 D-08, D-15). Its proof is Phase 18's:
  the junction bars at 1e-12 and T4's KISSsoft anchor on the tangent branch.
- **D-05:** **The tip radius actually used is printed in the existing `root_fillet` derived
  field** (`derive()` already prints the capped radius at 3 dp). Under trochoid it carries
  the capped ρ from `cutter()`; the field description names which cap applies by mode. No
  new field, nothing null on replay. Rejected: a new `cutter_tip_radius` derived field (two
  numbers for one knob).

**Undercut waist floor**
- **D-06:** **The waist is printed and warned below a floor; nothing is refused for being
  thin.** A new derived field (the undercut waist thickness, mm, null in radial mode and
  on replay) is printed wherever the trochoid applies; below the floor one warning names
  `teeth`, `profile_shift` and `pressure_angle`. The gear still builds — only the kernel
  guards (SC2) refuse, with a `BuildError`, a wire that would open. "tooth severed" (18
  D-17, waist ≤ 0) stays a refusal. Rejected: a `422` below the floor (no preview at all
  for a gear whose number is honest); refusing like severed (the part silently differs
  from the hob root the user asked for).
- **D-07 (floor):** **The floor is measured in this phase, then pinned.** The bench walks
  the low-tooth corner (6 teeth, 14.5°, x −0.6 and its neighbours, ρ at 0, 0.38·m and the
  cap) and finds where the built waist stops being a tooth — the kernel refuses, or the
  spline-to-oracle gap leaves its bar — and the floor is set from that with stated
  headroom, recorded beside the constant with date and host (L08; the L33 bar rule). A
  reading under about 10× goes to the human at a checkpoint. Rejected: a module fraction
  or an absolute millimetre picked before the measurement exists.

**The flip's schedule (Phase 20)**
- **D-08:** **The flip is deferred past v0.4; Phase 20 is recorded `Skipped (O4, flip
  deferred)`.** The `Lxx` this phase appends (supersedes L10, amends L09 and L33) says the
  hob root is opt-in through `root_shape`, that the default does not move in this
  milestone, and names the regen rules a future flip must follow (one commit carrying the
  predicate change, `make fixture.regen` and an `Lxx` listing the moving records first —
  L26 D-03, 18 D-01). No shared link moves; the 0.08–0.14 mm step 18 D-05 measured at
  41→42 teeth never reaches a default user. REQUIREMENTS.md "Trochoid follow-ups" owns the
  flip from here.
  — **Reversibility:** reversible — running the flip later is exactly Phase 20's one
  commit; nothing in this phase has to be undone.
- **D-09 (trigger):** **The `Lxx` names the trigger as a real fit report or a mating-pair
  request below `z_min`** — the trigger `docs/ideas/2026-09-21-trochoidal-root-fillets.md`
  already records: someone matching a hobbed low-tooth gear, or a request for a mating
  pair below the undercut limit. Not calendar-based, not "the next milestone that touches
  the root".

**Carried forward from Phase 18 (locked, not re-discussed)**
- O4 root mode: default off this milestone (18 D-01); the trochoid applies only where
  `rb > rf`, the analytic fillet everywhere else, a request with nothing radial to replace
  ignored and warned in `root_warnings`' sentence (18 D-02).
- `root_mode(p, pr, *, requested, rho)` is the single predicate and owns every refusal;
  every sentence comes from `root_warnings`; tests capture sentences, never type them (18
  D-03, D-04, D-10, D-16). Phase 19 passes `requested=p.root_shape` and `rho=p.root_fillet`.
- `d05-hold` (bench/RESULTS.md, 2026-10-08): the root-shape step premises hold; Phase 19
  is planned on D-01/D-02 as recorded.
- Carried from 18-REVIEW: the tip radius is validated once at its `GearParams` field
  (`root_fillet` already is: `_f(0.5, 0, 3)`), so `cutter()`'s `ValueError` guard becomes
  unreachable from user input and stays as the internal contract; the `ASSUMPTION:` on
  the ρ 0 crossover figure in `bench/RESULTS.md` stays recorded.

**Carried forward from ROADMAP.md / REQUIREMENTS.md (locked)**
- Fixture discipline: `git diff --exit-code tests/regression/pre_v0_2.json` clean after
  every task; 85 replay cases unmodified; every new `DerivedDimensions` field null on
  replay (L26, L27 pattern); `root_d == 2·rf` asserted in both modes.
- Order inside the phase: the spline-to-spline junction under the tip chamfer and the
  build time on the heaviest allowed low-tooth row are spiked first, before any schema
  change (PITFALLS 18); the kernel-tier bar is set only after STACK's and PITFALLS'
  spline-deviation methods are reconciled (SUMMARY correction 16; STACK's N = 16 at
  3.6–4.0e-5 mm is the starting point).
- The undercut sentence is restated from the cutter actually used (`undercut_teeth`,
  `undercut_shift`) with `x_min` beside it and no "radial root" wording, only where the
  predicate says the trochoid applies; in radial mode the old sentence stays so
  `pre_v0_2.json:582,632,948,996,1588` stay byte-identical. No lead-in warning where no
  chord exists (L33).
- Three-interface parity the way Phase 12 did it: the model-driven field walk in one
  order, `spur info` and `/api/info` byte-identical, every new refusal a `422` and exit 2.
- Commit discipline: L36 (`verify.fast` at commit, the full gate at pre-push, `make
  verify` by hand before every push — 17 D-09). Phase branch
  `gsd/phase-19-the-trochoid-in-the-part` cut from `origin/main` at `df4749e` (PR #28);
  lands through a PR via `make pr.land`.

### Claude's Discretion
- The `root_fillet` help text and README row wording under the two meanings; where the
  `root_shape` select sits on the form within the Teeth group; the new waist field's name
  and the exact warning sentences (all from `root_warnings` / `derive()`, captured by
  tests).
- The kernel-tier bar's value and sample count once the two deviation methods are
  reconciled; the structural guards' exact thresholds (spacing ratio, annulus bounds).
- How `_outline` carries the trochoid per side (one spline per side through `RootCurve`
  mirrored, the root arc between neighbouring curves) and how `spline_start` /
  `tip_chamfer_limit` are threaded the junction radius.
- The compose matrix's rows and the bench script's shape for the waist floor and the
  heaviest low-tooth row.
- Where the `Lxx` text sits in `docs/architecture/decision_log.md` and the exact
  superseding/amending wording for L09, L10, L33.

### Deferred Ideas (OUT OF SCOPE)
- The default flip (Phase 20): `Skipped (O4, flip deferred)`; owned by REQUIREMENTS.md
  "Trochoid follow-ups" with D-09's trigger.
- Form-circle thickness/gap fields (rejected in D-03): revisit only if a user asks for a
  number at `root_form_d`.
- A separate `cutter_tip_radius` field (rejected in D-01): revisit if a shop needs a hob
  radius different from the analytic fillet on the same link.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-root-mode-decided | The root-mode choice is logged as an `Lxx` superseding L10, amending L09 and L33; the field is a `Literal` (never `bool`), reaches the form and the CLI from the model, the field-walk enum exemption is generalised; fixture `git diff --exit-code` after every task | The field is one `Field(...)` like `recess_sides`; the walk's exemption is a hard-coded name at `tests/test_cli.py:209-215` and a second adjacency pin at `tests/test_api.py:315` that D-02's placement breaks (Pitfalls 1, 2); next free id is L38; regen rules for a future flip are L26 D-03 |
| REQ-outline-consumes-root-curve | `_outline` replaces fillet arc + lead-in per side with one `makeSpline` through `RootCurve`; involute spline starts at the junction from the same float; four structural guards not resting on `isValid()`; `root_d == 2·rf` in both modes; kernel-tier `Edge.positionAt` proof against the oracle at a bar set from the measured gap; generator never enters `model.py` | A working scratch outline built 5,159 swept gears with 0 kernel failures (F1); the dead band of a tiny root arc (F4) is the one construction hazard found; the two deviation methods are reconciled and the kernel tier reproduces them to 3 digits (F2, F3); guard candidates measured (Pattern 4) |
| REQ-derived-numbers-honest-under-trochoid | `root_thickness`/`root_gap` null + warning; `root_form_d`; undercut waist with a floor; lead-in warning silent without a chord; additive fields, null on replay | `derive()` branch table (Pattern 5); `RootCurve.waist` is the source of the waist; the waist walk (F8) shows the kernel never refuses above 5e-3 mm at module 1, so the floor is a human checkpoint (Open Question 1) |
| REQ-cutter-tip-radius-settable | ρ explicit, printed at 3 dp, capped, trimmed value warns with the cap; reaches form and CLI from the model | D-01/D-05: `root_fillet` carries `Cutter.rho`; `root_warnings` already holds the `rho capped` sentence; the oracle run with the printed ρ is the "printed equals cut" proof (Pattern 7) |
| REQ-undercut-warning-restated | `derive()`'s undercut sentence from the cutter constants, no "radial root", `x_min` beside it; radial fixture records byte-identical | `undercut_teeth`/`undercut_shift` exist and are proved (Phase 18 T1); two traps found: `x_min` can exceed the field maximum 1.0 and must be rounded up, never to nearest (F9); the sentence's firing condition must compare at the printed resolution (Open Question 3) |
| REQ-trochoid-composes-and-is-priced | Tip chamfer (L29 boundary re-bisected across the spline-to-spline junction), recesses and each cutout build with the trochoid on; heaviest low-tooth row vs `SPUR_BUILD_TIMEOUT`; `make verify` vs the 66 s bar; three-interface parity; docs brought true | The chamfer law `kernel limit = ra - R_join` holds across tangent and crossing junctions (F5); the heaviest row measures 12.2 s of 30 s (F6); `make verify` baseline 46.21 s on a different host than L34's (F7); the SC5 "exit 2" wording conflicts with `docs/architecture/cli.md` for `BuildError` (Open Question 2) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Treated as locked alongside CONTEXT.md. [VERIFIED: /Users/half/git/halfb00t/spur/CLAUDE.md, read this session]

- **Gate:** nothing is done until `make verify` passes (ruff, `mypy --strict`, import-boundary contracts, unfinished-work scan, pytest); state the command and the result line. `make check` adds Docker checks and is not needed here.
- **Two standing rules:** a printed number is a number someone cuts metal to; if it cannot be computed honestly, a warning and no number (L08). A parameter the user did not set never silently changes the part; defaults are absolute millimetres (L05); trimmable dimensions are capped and warned, a direct conflict between two explicit choices is a `422` (L03).
- **Style:** `calc.py` runs on every keystroke and never imports `cadquery`; vendor types stop at their boundary (`cadquery` objects do not escape `model.py`); a parameter is validated once at `GearParams` and trusted afterwards; comments explain why and carry the measurement.
- **Simplicity:** surgical edits; no speculative flexibility; one concern per commit (Conventional Commits); new behaviour ships with its tests; performance claims measured and recorded; no `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError` (whole-word scan), no mypy suppression under `src/spur/`.
- **Ideas and debt:** one file per item from `docs/<dir>/TEMPLATE.md`, INDEX row in the same commit; state before the final reply whether any item was filed. Blocker debt: fix or stop and ask.
- **Stop and ask** when evidence conflicts (doc vs code vs prior decision): this research found one such conflict (Open Question 2).
- **Ruff selects** `E,F,W,I,N,UP,B,SIM,C4,PTH,TID,ARG,ERA,TRY,LOG,G` (`pyproject.toml`): `N` forbids upper-case locals, `ERA` flags commented-out code; `filterwarnings = ["error", ...]`; `fail_under = 96` with `branch = true`, so every new fallback arm needs a test that reaches it (guards in `model.py` are reachable only with hand-built bad curves).
- **Skills:** `.claude/skills/` and `.ai_skills/` hold only a `README.md` (read: no project skill applies).

## Summary

The curve is ready and the kernel takes it. I built the Phase 18 `RootCurve` into a closed trochoid outline in a scratch module (two splines per tooth side, shared `Vector` at the junction, a three-point arc between neighbouring teeth) and ran it over 15,723 cases of the Phase 18 sweep product (stride 2 of 31,446): 5,159 are gears the trochoid applies to, and **all 5,159 produced a closed wire and a valid extruded solid, with zero kernel exceptions** (blank build 0.008-0.25 s). The measured kernel facts the plan needs: the spline-to-spline junction under the tip chamfer obeys L29's law exactly (the kernel's limit is `ra - R_join`, to 5 digits at 100 teeth), so `spline_start` reading the junction radius is the whole fix; the heaviest allowed low-tooth composed row (116 teeth at the box corner) builds in 12.2 s against the 30 s timeout and costs within about +10 % of the radial build; and the one construction hazard is a degenerate root arc (cutter tip land 2a below about 2e-7 mm makes `makeThreePointArc` raise `GC_MakeArcOfCircle::Value() - no result`, which `_build_checked` would relabel with the wrong remedy "try smaller fillets or chamfers").

The two research files' spline-deviation methods reconcile (SUMMARY correction 16): STACK's trochoid figures are a point-to-polyline distance and reproduce to 3 digits (3.58e-5, 3.89e-5, 3.99e-5 mm); STACK's shipped-flank figures (6.0e-5, 1.0e-4) are the vertex-spacing floor of its 20,001-point reference curve, not a deviation; PITFALLS' 0.13 micrometre is not reproduced by either method. The kernel tier is therefore the Phase 18 oracle (`tests/trochoid_oracle.clearance`) applied to `Edge.positionAt` samples of the built root edges: it reads 2.2e-5 to 6.2e-4 mm on seven rows and equals the polyline distance. Over the swept box the spline error is 3.7e-6 to **1.79e-4 times the module** (median 3.0e-5), 4.5x worse than STACK's starting point at the corners (14.5 degrees, x -0.6).

Three things in the roadmap/CONTEXT wording do not survive contact with the code and need the planner's attention: SC5's "every new refusal routes identically to a 422 and to exit 2" contradicts `docs/architecture/cli.md` for a `BuildError` (exit 1; only `GearParams`-boundary errors exit 2), and this phase adds no new `check()` refusal (Open Question 2); the D-02 field placement breaks a second field-adjacency assertion beside the one SC5 names (`tests/test_api.py:315`); and the restated undercut sentence can advise a profile shift above the field's maximum of 1.0 (6 teeth, 14.5 degrees, tip radius 0 gives x_min 1.0619) and must round `x_min` up, because rounding to nearest prints a shift that still undercuts.

**Primary recommendation:** spike first in `bench/` (chamfer law, heaviest row, deviation reconciliation, guard numbers, waist walk), then land field + `RootMode.curve` + `_outline` + `derive()` as one vertical slice (never the field without its model and derive consumers: a field that is accepted but ignored breaks L08 at that commit), then interface parity, then compose/price/docs/`Lxx` (L38).

### Findings that change or sharpen the plan (all [VERIFIED: scratch run] unless tagged)

| # | Finding | Evidence | Consequence for the plan |
|---|---------|----------|--------------------------|
| F1 | The trochoid outline builds everywhere the sweep says it applies | 5,159 trochoid gears of 15,723 swept cases: 0 open wires, 0 invalid solids, 0 kernel exceptions; `root_mode` refused the rest as 3,594 `nothing radial to replace`, 489 `tip land gone`, 42 `tooth severed`; 6,439 combinations are refused by `GearParams` itself | `_build_checked`'s catch-all is not reached by an honest curve; the guards are defect detectors, not the normal path |
| F2 | STACK's and PITFALLS' deviation methods reconcile (see Pattern 4a) | method B (point to polyline) reproduces STACK's trochoid figures to 3 digits; method A (nearest vertex) reproduces its flank figures as the 20,001-point spacing floor | Set the bar from method B / the oracle, not from either file's quoted flank number |
| F3 | The kernel tier is the existing oracle on `positionAt` samples | oracle `clearance` on 41 samples per edge of tooth 0: default gear 2.2e-5; z 8/10/14 m 1 tip radius 0.38: 3.55e-5, 3.82e-5, 3.82e-5; 6 teeth x -0.5: 4.4e-5; 30 teeth m 0.2 x -0.6: 3.58e-5 (= 1.79e-4 m); 30 teeth m 10: 6.2e-4 (= 6.2e-5 m); 0.7 s per row | No second oracle; bar proposal in Pattern 7 |
| F4 | A root arc shorter than about 2e-7 mm raises; 0 raises too | tip land half-width a = 0 and 1e-9, 1e-8, 1e-7 mm: `Standard_Failure: GC_MakeArcOfCircle::Value() - no result`; 1e-10 and below silently drops the arc (62 faces instead of 74 on 12 teeth); 3e-7 and above builds, including a full composed build at a = 6e-7 | A guard branch in `_outline` for the short arc is mandatory and reachable by users (tune `backlash` so the 3 dp floor lands within 1e-6 of the cap) |
| F5 | L29's kernel law holds across the spline-to-spline junction | 14-16 step bisection per config: kernel max c vs `ra - R_join`: 3.19434 vs 3.1945 (default, tip radius 0), 3.09608 vs 3.0962 (default, 0.5), 1.32429 vs 1.3244, 1.35417 vs 1.3543, 1.28255 vs 1.2826, 100 teeth 1.72150 vs 1.7215 and 1.54108 vs 1.5411; six of the thirteen rows build past it (conservative, as L29's sixth did: 10 teeth tip radius 0, 8 teeth both, 6 teeth tip radius 0.5, 30 teeth both) | `spline_start` returns `RootCurve.points[-1][0]` under trochoid; `TIP_CHAMFER_MARGIN` 0.001 stands; repeat as the 20-step bisection the L29 way in `bench/` |
| F6 | The junction is above the pitch circle in 240 of 5,159 gears (all 13 teeth or fewer) and above the radial model's halfway clamp in 1,713 | counted over the same sample | The third chamfer bound binds only for low-tooth crossings; `spline_start`'s `min(r_line, rf + 0.5 (ra - rf))` clamp must NOT apply under trochoid |
| F7 | Build times (this host, load 6.5-11) | 116 teeth, module 10, 14.5 degrees, x -0.6, keyed bore, 32 spokes, chamfer 3, both recesses: radial 11.12 s, trochoid 12.24 s per request (build + slower export); module 1.75: 9.59 / 10.57 s; honeycomb: 7.10 / 7.18 s; bare and chamfer+recess rows 0.6 and 4.1 s; gate-size composed rows 0.2-1.7 s (trochoid) vs 0.16-1.4 s (radial; the 12-tooth module-2 row reads 0.71 vs 0.32 s) | Every composed trochoid row is far inside 30 s; the 200-tooth worst row (29.42 s, L37) is untouched by construction because a trochoid request on it is ignored |
| F8 | The kernel never refuses a thin waist above 5e-3 mm (module 1) | walk of 6/7/8 teeth, 14.5 degrees, x -0.6..0 step 0.01, tip radius 0, 0.38, 3.0 (capped): thinnest built waist 4.98e-3 mm (6 teeth, x -0.48, tip radius 0, 0.005 m), next 9.4e-3 mm; `tooth severed` below; all valid | D-07's "kernel refuses" signature does not exist above the spline-error scale; the floor will be set by the oracle bar and goes to the human (Open Question 1) |
| F9 | `x_min` has two traps | 10 teeth, m 1, 20 degrees, tip radius 0.38: `x_min` = 0.41508; x = 0.414 xi -3.2e-3 (undercut), 0.416 xi +2.7e-3; at 6 teeth, 14.5 degrees, tip radius 0 `x_min` = 1.0619 > the field's 1.0 | Print `ceil(x_min * 1000) / 1000`; when it exceeds 1.0 say no shift in range avoids it, never print an out-of-range shift (L08) |
| F10 | `make verify` baseline on this host | `1023 passed in 45.59s`, wall 46.21 s, 2026-10-08, 1-minute load 6.12 before / 15.73 after, Apple M5 Max (18 CPUs), Python 3.12.15 | L34's 63.555 s and the 66 s bar were read on an Apple M2 Max (12 CPUs); record both hosts and measure the phase's delta on one host (Pitfall 9) |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `root_shape` value validation | `params.py` (`GearParams`) | `cli.py` (`choices=`), `app.js` (`<select>`) | Validated once at the boundary; `Literal` gives a free 422 and argparse `choices` |
| Does the trochoid apply; the curve; ρ cap | `calc.py` (`root_mode`, `cutter`, `RootCurve`) | — | Phase 18 built and proved it; Phase 19 only adds the curve to `RootMode` and reads it |
| Junction radius for the spline start and the tip-chamfer cap | `calc.py` (`spline_start`, `tip_chamfer_limit`) | `model.py` reads the number | One radius for the outline and the cap (L29) |
| Printed numbers, warnings, new derived fields | `calc.py` (`derive`, `DerivedDimensions`, `_ROOT_SENTENCES`) | `app.js` `DIMS` rows | Sentences from one function; the part and the number cannot disagree (L08) |
| Outline assembly from floats, guards, kernel wire | `model.py` (`_outline`, new guard helpers) | — | The only module allowed to touch `cadquery`; the generator stays in `calc` |
| Proof of the curve in the part | `tests/` (oracle on `positionAt`) | `bench/` (spikes, bars) | Oracle shares no code with `calc` or `model` |
| Prices (chamfer law, build time, gate cost) | `bench/` + `bench/RESULTS.md` | `docs/architecture/decision_log.md` L38 | Measured, host state beside each figure |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `math`, `dataclasses`, `typing.Literal` | CPython 3.12.15 [VERIFIED: `.venv/bin/python --version`] | all maths and the field type | L01/L23; no new dependency (REQUIREMENTS rule) |
| cadquery / cadquery-ocp | 2.8.0 / 7.9.3.1.1 [VERIFIED: `.venv/bin/pip list`] | `Edge.makeSpline`, `Edge.makeThreePointArc`, `Wire.assembleEdges`, `Edge.positionAt` | The pinned pair (L12, L34); fixture provenance names it |
| pydantic / FastAPI | 2.13.5 / 0.142.4 [VERIFIED: `.venv/bin/pip list`] | the `Literal` field, `/api/schema` enum, `DerivedDimensions` | Existing |
| pytest, xdist, cov | 9.1.1, 3.8.0, 7.1.0 [VERIFIED: `.venv/bin/pip list`] | proofs and gate | Existing |
| ruff / mypy / import-linter | 0.16.10 / 2.4.0 / 2.15 [VERIFIED: `.venv/bin/pip list`] | static gate | Existing |

### Supporting
None. No numpy/scipy (REQUIREMENTS "Out of Scope").

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Edge.makeSpline` through 16 sampled points | `makeSpline` with `tangents=` at the root-circle end | `makeSpline(listOfVector, tangents=None, periodic=False, parameters=None, scale=True, tol=1e-06)` [VERIFIED: inspect.signature, cadquery 2.8.0] supports end tangents, but the measured error (1.8e-4 m worst) is already below anything printable; adds a parameter to keep honest. Not recommended |
| N = 16 samples (`ROOT_CURVE_POINTS`) | a larger N | Deviation falls but the constant is Phase 18's measured one; the physical gain is nil (180 nm at module 1, worst corner). Keep 16 and state the bar from the measurement |

**Installation:** none.

**Version verification:** `.venv/bin/pip list` this session (above); `requirements.txt` stays at 31 pins [CITED: 18-RESEARCH, unchanged: no package added].

## Package Legitimacy Audit

No external package is installed or recommended by this phase, so the legitimacy gate has nothing to check.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 shared link / form / CLI flags / API query
        |  root_shape (Literal, default "radial"), root_fillet (mm)
        v
 GearParams  (validated once; root_fillet already _f(0.5, 0, 3): finite, >= 0)
        |
        +-----------------------------+---------------------------------------------+
        v                             v                                             v
 calc.derive(p)                 model._build(p)                              calc.tip_chamfer_limit(p)
   rm = root_mode(p, pr,          rm = root_mode(p, pr,                        rm = root_mode(...)  (default arg)
        requested=p.root_shape,        requested=p.root_shape,                 spline_start(pr, fillet, curve=rm.curve)
        rho=p.root_fillet)             rho=p.root_fillet)                      -> ra - R_join - TIP_CHAMFER_MARGIN
   mode "radial"  ----------+     mode "radial"  -> _outline(pr, fillet)  [byte-identical path]
     old numbers, old       |     mode "trochoid"-> _outline(pr, fillet, curve=rm.curve)
     sentences (fixture)    |            |
   mode "trochoid" ---------+            v
     root_thickness/gap=None       per tooth k, centre c = k * 2pi/z:
     root_form_d = 2 R_join          left  = polar(R_i, c - h_i)   i = 0..15  (root circle -> junction)
     waist field, sentences          right = polar(R_i, c + h_i)   reversed
     rfil = cutter.rho               makeSpline(left) ; makeSpline(involute from the SAME junction Vector)
        |                            tip arc ; makeSpline(right involute) ; makeSpline(right root)
        v                            root arc (rf) to the next tooth  -- OR shared Vector if 2a < ROOT_ARC_MIN
   DerivedDimensions                       |
        |                                  v  guards (BuildError, not isValid): coincident vectors,
        v                                  spacing ratio, annulus bounds, area vs polygon of the points
   /api/info , spur info                   Face -> extrudeLinear -> recess -> bore -> keyway -> cutout -> chamfer
   (byte-identical JSON)                   -> solid  -> positionAt samples -> tests/trochoid_oracle.clearance
```

### Recommended Project Structure
```
src/spur/params.py        # + root_shape Literal field after tip_chamfer; root_fillet help text (both meanings)
src/spur/calc.py          # RootMode.curve; spline_start(..., curve=None); tip_chamfer_limit/effective(p, rm=None);
                          #  derive(): mode-keyed branch; DerivedDimensions: root_thickness/root_gap -> float|None,
                          #  + root_form_d, + waist field; new sentences in _ROOT_SENTENCES / root_warnings
src/spur/model.py         # _outline(pr, fillet, curve=None); _gear_blank(..., curve); _build reads root_mode;
                          #  ROOT_ARC_MIN; guard helpers raising BuildError. NO generator names (see Pitfall 11)
src/spur/static/app.js    # DIMS: two rows (root_form_d, the waist field)
tests/test_trochoid.py    # calc-tier: derive branches, sentences, x_min, waist floor, spline_start/chamfer limit  (in verify.fast)
tests/test_model.py       # kernel tier: build rows, positionAt vs oracle, guards with hand-built curves, compose matrix (not in verify.fast)
tests/test_cli.py, tests/test_api.py, tests/composition.py   # field walk, parity, literal sets
bench/trochoid.py (or a sibling)  # spike subcommands: chamfer, build, spline, waist; bench/sweeps/trochoid.json
bench/RESULTS.md          # new section "Trochoid in the part (Phase 19)"
docs/architecture/decision_log.md # L38; README; gear-maths/{strategy,implementation,tests}.md; solid-model/tactics.md; docs/ideas/...
```

### Recommended plan shape (planner decides)
1. **Spike plan (bench only, no `src/`, no schema):** chamfer re-bisection, heaviest row, deviation reconciliation, guard numbers, waist walk, `ROOT_ARC_MIN`. Ends with two human checkpoints (bar and floor, Open Questions 1 and 4). The spike's outline builder lives in the bench script (the L29 precedent "measures the chamfer before the field exists", `bench/tip_chamfer_spike.py`) and is re-run against the real build once the field lands.
2. **Vertical slice plan:** `root_shape` + `RootMode.curve` + `spline_start`/`tip_chamfer_*` + `_outline` + guards + `derive()` + `DerivedDimensions` + the tests that pin them. Splitting the field from `derive()`/`model` would leave a commit that accepts `root_shape=trochoid` and prints radial numbers for a part built another way or ignores it silently.
3. **Interface parity plan:** field walk generalisation, `DIMS` rows, README example, parity tests.
4. **Compose / price / record plan:** compose matrix, chamfer boundary test, `bench/RESULTS.md`, gate cost, `Lxx` L38, docs, Phase 20 skip bookkeeping (ROADMAP progress row `Skipped (O4, flip deferred)` and a dated STATE.md Roadmap Evolution line naming L38, per the ROADMAP Phase 20 skip condition).

### Pattern 1: `RootMode` carries the curve; default arguments keep every old call site
**What:** `root_mode` already builds the curve and throws it away (18-REVIEW IN-02: the two entry points disagree and the solve runs twice, 33.7 vs 30.7 microseconds tangent, 88.9 crossing [CITED: bench/RESULTS.md "Per-call cost (18-05, D-14)"]). Add a trailing defaulted field `curve: RootCurve | None = None` to `RootMode`, filled exactly when `mode == "trochoid"`. Then `derive`, `model._build`, `spline_start` and `tip_chamfer_limit` all read one object.
**When to use:** every consumer. Keep `spline_start(pr, fillet)`'s two-argument form (callers: `model.py:146`, `calc.py:314`, `bench/tip_chamfer_spike.py:194-285`; 15 lines in `tests/` call one of `root_fillet`, `spline_start`, `tip_chamfer_limit`, `tip_chamfer_effective`) by adding `curve: RootCurve | None = None`; `tip_chamfer_limit(p, rm: RootMode | None = None)` and `tip_chamfer_effective(p, rm=None)` compute `root_mode(...)` themselves when `rm is None` (362 nanoseconds when nothing is requested [CITED: bench/RESULTS.md per-call table]).
**Verbatim in-repo values** (read this session):
- `[VERIFIED: src/spur/calc.py:1241-1243 "RootShape = Literal["radial", "trochoid"]" and "RootReason = Literal["not requested", "nothing radial to replace", "tip land gone", "bracket degenerate", "curve invalid", "tooth severed"]"]`
- `[VERIFIED: src/spur/calc.py:1501-1506 "class RootMode: mode: RootShape ... reason: RootReason | None ... cutter: Cutter | None"]` (frozen dataclass)
- `[VERIFIED: src/spur/calc.py:1338-1346 "class RootCurve" with fields "points", "join", "waist"]`; `points` are "(radius mm, half-angle from the tooth centre rad), strictly increasing radius, ROOT_CURVE_POINTS long"
- `[VERIFIED: src/spur/calc.py:66 "ROOT_CURVE_POINTS = 16"]`, `[VERIFIED: src/spur/calc.py:42 "TIP_CHAMFER_MARGIN = 0.001"]`
- `[VERIFIED: src/spur/model.py:54-55 "FLANK_POINTS = 16" and "TOL = 1e-6"]`
**Trap:** under trochoid `spline_start` returns `curve.points[-1][0]` and skips the radial clamp `r_line = min(r_line, pr.rf + 0.5 * (pr.ra - pr.rf))` (F6: 1,713 of 5,159 junctions lie beyond halfway).

### Pattern 2: The trochoid `_outline` (adapted from the working scratch build)
**What:** per tooth, two splines per side. The first involute point is the curve's last `Vector` object, not a recomputation (a gap of 1e-6 mm silently opens a wire, PITFALLS 7; a shared object has no gap).
```python
# Source: scratch build, 15,723 swept cases, 0 failures (names adapted; not repo code yet)
def _trochoid_outline(pr: Profile, curve: RootCurve) -> cq.Wire:
    pitch = 2 * math.pi / pr.z
    r0 = curve.points[-1][0]                       # junction radius, the curve's own float
    radii = [r0 + (pr.ra - r0) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
    teeth = []
    for k in range(pr.z):
        c = k * pitch
        root_l = [_polar(r, c - h) for r, h in curve.points]               # root circle -> junction
        root_r = [_polar(r, c + h) for r, h in reversed(curve.points)]     # junction -> root circle
        flank_l = [root_l[-1]] + [_polar(r, c - pr.half_angle(r)) for r in radii[1:]]
        flank_r = [_polar(r, c + pr.half_angle(r)) for r in reversed(radii[1:])] + [root_r[0]]
        teeth.append((c, root_l, root_r, flank_l, flank_r))
    edges: list[cq.Edge] = []
    for k, (c, root_l, root_r, flank_l, flank_r) in enumerate(teeth):
        edges += [cq.Edge.makeSpline(root_l), cq.Edge.makeSpline(flank_l),
                  cq.Edge.makeThreePointArc(flank_l[-1], _polar(pr.ra, c), flank_r[0]),
                  cq.Edge.makeSpline(flank_r), cq.Edge.makeSpline(root_r)]
        nxt = teeth[(k + 1) % pr.z]
        edges.append(cq.Edge.makeThreePointArc(root_r[-1], _polar(pr.rf, c + pitch / 2), nxt[1][0]))
    return cq.Wire.assembleEdges(edges)
```
Topology: 6 side faces per tooth (2 root splines, 2 flanks, tip arc, root arc) against 8 on the radial path: the default gear's bare blank is 116 faces / 342 edges; the radial path's pinned 172 / 490 is for the full default part [CITED: ARCHITECTURE 1.1, tests/regression docstring]. The radial path in `_outline` must stay float-for-float unchanged (the replay compares faces, edges and volume at `rel=1e-6`).
**The root arc at the circle's end:** the root curve's first point has half-angle `pi/z - a/r` (`a` = the cutter's flat tip land), so the arc between neighbouring teeth spans `2a` of arc length. See Pattern 3.

### Pattern 3: The degenerate root arc (F4)
Measured on 12 teeth, module 1, 20 degrees (arc half-width `a` set by moving the first point along the root circle):

| a (mm) | chord 2a | result |
|--------|----------|--------|
| 0 | 0 | `Standard_Failure: GC_MakeArcOfCircle::Value() - no result` |
| 1e-12, 1e-10 | | builds, valid, arc silently dropped (62 faces instead of 74) |
| 1e-9, 1e-8, 1e-7 | 2e-9 to 2e-7 | same exception |
| 3e-7 and above | 6e-7 up | builds, valid, 74 faces; a composed build (keyway, 4 spokes, both recesses, tip chamfer) also builds and validates down to a = 6e-7 |

`a` reaches this band from user input: the cap is floored to 3 dp, so `a = (rho_max - used) * (sec - tan)` is below 5e-4 mm and is arbitrarily small whenever `rho_max` lands within a few microns above a multiple of 0.001 (the smallest `a` in the sample was 4.0e-5 mm); `backlash` is not stepped on the wire (`step` is schema metadata, `calc.py:34-41`), so a user can type such a value (a request equal to the unrounded cap to the last bit would give `a` of order 1e-17 or 0, reachable only by float equality, so the tuned-`backlash` route is the realistic one). **Rule:** if the chord `2a` (or the actual chord between `root_r[-1]` and the next `root_l[0]`) is below `ROOT_ARC_MIN`, add no arc and let the next tooth's first root vector be the same object as this tooth's last. The last failing chord is 2e-7 mm, the first building one 6e-7 mm; a constant of 2e-6 mm is 10x the last failure [ASSUMED: the value is a proposal, re-measure in the bench]. Test it by tuning `backlash` (bisection, the `bench.trochoid.tuned_shift` pattern) so `a` lands at 1e-8 mm, plus a direct hand-built curve at `a = 0`.

### Pattern 4: The four structural guards (BuildError, independent of `isValid()`)
These detect a generator or assembly defect; an honest curve never trips them (F1), so they are reachable only with hand-built curves in tests (coverage floor `fail_under = 96`). The message should follow the `_NOT_A_BODY` / `_tip_edges` wording "a modelling defect in spur, not a conflict in these parameters" [CITED: model.py:417-419, 530-534]. Measured candidate numbers, all over the 5,159 trochoid gears:

| Guard | Measured over the sample | Boundary evidence | Proposal [ASSUMED] |
|-------|--------------------------|-------------------|--------------------|
| Coincident junction vectors | shared `Vector` objects: gap 0 by construction | a 1e-6 mm gap opens a wire (PITFALLS 7); root arc dead band (Pattern 3) | assert the junction `Vector`s are the same objects; `ROOT_ARC_MIN` branch |
| Spacing ratio (max/min chord of the 16 root points) | median 1.71, max 11.34 (60 teeth, m 1.75, 14.5 degrees, backlash 1, tip radius 1.69); min chord 0.0073 m | resampling the same smooth curve with bunching up to ratio 2e5 keeps the spline within 5e-4 mm; the kernel builds at min chord 1.7e-6 mm (ratio 2e5) and raises at 1.4e-7 mm (ratio about 3e6) | ratio bar 1000 (88x the box maximum, 1.5e-4 mm deviation at ratio 600) |
| Annulus bounds (sampled spline radius vs `[rf, ra]`) | min(R - rf) = -2.8e-14 mm; max(R - ra) = -0.044 mm | 81 `positionAt` samples per root edge | `[rf - TOL, ra + TOL]` with TOL 1e-6 (3.5e7x over the lowest reading) |
| Closed-form area (face area vs shoelace area of the interpolated points) | `abs(face.Area() / polygon - 1)` max 3.65e-3 (tip arc taken as a chord) | PITFALLS' bad spline: volume 347.9 vs 21.4 (a factor 16) | bar 5e-2 (14x over the sample, far under a swing) |

Because the sample is a stride-2 slice of the product (A7), the plan should run the guards over the whole product in `bench/` and record the maxima before pinning.

### Pattern 5: `derive()` keyed on the mode (one `rm`, computed once)
| Item | Radial (and any refusal) | Trochoid |
|------|--------------------------|----------|
| `root_d`, `tip_d`, ..., `span` | unchanged | unchanged (`root_d == 2*rf`; the root circle is `rf` in both) |
| `root_thickness`, `root_gap` | `r3(root)`, `r3(gap)` from `_tooth` | `None` + one sentence (D-03); `_tooth` itself stays untouched because `check()` and `root_fillet` consume it in both modes |
| `root_fillet` (printed) | `r3(root_fillet(p))`, "Root fillet reduced to ... to fit the tooth gap." when capped | `r3(rm.cutter.rho)`; `root_warnings(rm)` supplies the `rho capped` sentence; the L09 gap-cap sentence must not fire |
| lead-in warning (`round(h, 3) > 0`) | as shipped | not evaluated (no chord) |
| undercut sentence | shipped text, fixture-pinned | restated: onset `undercut_teeth(c)`, shift `undercut_shift(c)` of `rm.cutter`, no "radial root" |
| `root_form_d` | `None` | `r3(2 * curve.points[-1][0])` |
| waist field | `None` | `r3(2 * R_w * h_w)` from `curve.waist` (arc, like `tip_thickness`); warning below the floor |
| refused request (`rm.reason`) | `root_warnings(rm)` sentence, then everything radial | n/a |
Spot values to design tests around [VERIFIED: scratch run, default gear]: `root_mode(..., requested="trochoid", rho=0.5)` gives `trochoid`, `cutter.rho` 0.5, `rho_max` 0.6347789, `a` 0.0858637, `xi` 2.533063, join `tangent`, junction `(15.2788075, 0.1080838)`, last-point half-angle gap to `Profile.half_angle` 1.4e-17 rad.
**Sentence mechanics (proposals, F9):** print `x_min` as `ceil(x_min * 1000) / 1000` (rounding to nearest prints 0.415 for 0.41508, which is still undercut by xi -7.9e-5); when `x_min` exceeds the field maximum (1.0) say that no profile shift in range avoids it. Compare the firing condition at the printed resolution (`teeth < round(z_min, 1)`), the lead-in warning's precedent [CITED: calc.py:1015-1017, 10-REVIEW CR-01]: with `xi < 0` alone, 10 teeth at 30 degrees, tip radius 0, backlash 0 has `z_min` exactly 10 and float xi -4.4e-15 [CITED: 18-RESEARCH Pattern 4], so "Below 10.0 teeth" would print for a 10-tooth gear.

### Pattern 6: One field, three interfaces, one walk
**Field** (D-02), written like `recess_sides`: `[VERIFIED: src/spur/params.py:91-93 "recess_sides: Literal["both", "top", "bottom", "none"] = Field(" ... "Recess sides", description="Which faces get an annular groove.", json_schema_extra={"group": "Recess", "unit": ""})"]`. Use group `"Teeth"`, `unit` `""`, no `step`.
**What the field's position breaks:** `[VERIFIED: tests/test_api.py:314-315 "assert names.index("tip_chamfer") == names.index("root_fillet") + 1" / "assert names.index("face_width") == names.index("tip_chamfer") + 1"]` - inserting `root_shape` after `tip_chamfer` makes the second assertion false; it must become `root_shape` then `face_width`. `test_openapi_documents_the_typed_contracts` holds a literal set of 29 `DerivedDimensions` field names [VERIFIED: tests/test_api.py:78 "fields = {" and :92 "assert set(component["required"]) == fields"]; add the two new names. `tests/composition.py` `ALWAYS` (root_thickness, root_gap in the non-null set) is correct for every radial row but wrong for any row with `root_shape = "trochoid"`.
**The generalised exemption** (replace the hard-coded name): `[VERIFIED: tests/test_cli.py:209-215 "if name == "recess_sides":" / "assert "step" not in prop" / "assert props["recess_sides"]["enum"] == list(" / "get_args(GearParams.model_fields["recess_sides"].annotation))"]`:
```python
literal_fields = [n for n, f in GearParams.model_fields.items() if get_origin(f.annotation) is Literal]
assert literal_fields == ["root_shape", "recess_sides"]          # order pinned: this walk is the model's own
for name in names:
    ...
    if name in literal_fields:
        assert "step" not in prop and prop["enum"] == list(get_args(GearParams.model_fields[name].annotation))
    else:
        assert "step" in prop, name
```
`cli.py` already routes any `Literal` through `choices=` [VERIFIED: src/spur/cli.py:47 "if get_origin(field.annotation) is Literal:" and :49 "choices=list(get_args(field.annotation)))"]; `app.js` renders `prop.enum` as a `<select>` and `gearQuery()` omits default values [VERIFIED: src/spur/static/app.js:64 "if (prop.enum) {" and :101 "function gearQuery() {"]. `--root-shape trochoid` flows to `GearParams(**values)`; a bad value is argparse exit 2 and an API 422 (pydantic literal error), both free.
**UI rows:** the DIMS test extracts keys with a regex [VERIFIED: tests/test_api.py:130 "dims_keys = re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)"]; keep the `['key', 'Label'],` shape. `renderInfo` skips null rows, so the nulled thickness/gap simply disappear and the warning explains. There is no browser test (deferred in the project), so the select and rows are verified only by reading `app.js` and by the schema/DIMS tests (A10).

### Pattern 7: The kernel-tier proof (printed equals cut)
Use the public pipeline (`model.build(p)` with the real bore, recess and chamfer: they do not touch the root edges), select the root splines by position, sample `positionAt`, convert to `(radius, half-angle)`, and feed the Phase 18 oracle with the ρ that `derive()` printed:
```python
# Source: scratch run reproducing F3 (tests/trochoid_oracle.clearance is the existing independent oracle)
root = [e for e in solid.Edges() if e.geomType() == "BSPLINE"
        and abs(e.startPoint().z) < TOL and abs(e.endPoint().z) < TOL
        and min(abs(hypot(*e.startPoint().toTuple()[:2]) - rf), abs(hypot(*e.endPoint().toTuple()[:2]) - rf)) < TOL]
assert len(root) == 2 * teeth                                  # a selector that selects nothing must fail (L26)
for e in (e for e in root if abs(atan2(e.positionAt(0.5).y, e.positionAt(0.5).x)) < pi / teeth):   # tooth 0
    pts = [(hypot(v.x, v.y), abs(atan2(v.y, v.x))) for v in (e.positionAt(i / 40) for i in range(41))]
    assert max(abs(c) for c in clearance(tuple(pts), teeth=..., module=..., pressure_angle=...,
               profile_shift=..., backlash=..., rho=derive(p).root_fillet)) <= BAR_PER_MODULE * p.module
```
(`positionAt(d, mode="length")` default [VERIFIED: inspect.signature, cadquery 2.8.0]; edge direction in the solid may be reversed, so compare unordered.) Using `derive(p).root_fillet` as the oracle's ρ is the L08 proof that the printed radius is the cut radius; a tripwire with ρ + 0.05 mm must read over the bar (sensitivity of the reading is 0.221 per unit ρ [CITED: 18-RESEARCH Pattern 6]).
**Bar arithmetic (L33 D-06):** the model's own floor is the spline error, 1.79e-4 m at the worst of the 5,159 gears (typical 3.0e-5 m, kernel rows 1.3e-5 m to 1.8e-4 m); the oracle's resolution is about 1e-15 m. A bar of `2e-3 * module` is 11x the worst measured and 50x STACK's 4e-5 m; ρ shifts of 0.05 mm read 1.1e-2 (5.5x that bar). 11x is at the project's 10x line, so the proposal is [ASSUMED] and goes to the human with the numbers if the bench moves either way (Open Question 4). Cost: 0.7 s per row at 41 samples per edge on two edges; keep these rows in `tests/test_model.py` (excluded from `verify.fast` by the Makefile slice, L36).

### Pattern 8: Composition and the chamfer law
Build matrix proven by scratch (all valid, one solid): default gear plus chamfer at its cap (1.75) with both recesses, keyway, hex bore, 4 spokes, 6 holes, honeycomb; 10 teeth chamfer 0.5; 12 teeth module 2 x -0.3 chamfer 1.0 plus recess; 40 teeth 14.5 degrees x -0.6 chamfer plus 6 spokes. Chamfer cap under trochoid: `min(0.45 * face_width, ra - r, ra - R_join - TIP_CHAMFER_MARGIN)` with `R_join` from the curve (the same expression `tip_chamfer_limit` has, only `spline_start` changes). `_tip_edges` is unaffected (the new root arcs are CIRCLE edges at `rf`, not `ra`; trochoid edges are BSPLINE); the compose test should run the existing selector matrix with a trochoid column to prove it. The bench re-bisection in `bench/` must use the 20-step method of L29 (the scratch run used 14-16 steps, resolving about 2e-4 mm).

### Anti-Patterns to Avoid
- **Accepting `root_shape` before its consumers exist** (a field that does nothing, or numbers for a part not built that way): L08.
- **Rounding `x_min` to nearest, or advising a shift above 1.0.** (F9)
- **Letting the trochoid generator, `_trochoid_point`, `_junction`, `_root_curve`, `trochoid_root` or `cutter(` appear in `model.py`.** `model.py` consumes the `RootCurve` that `RootMode` carries. Prove it with a source-grep test the way `test_calc_module_stays_log_free` does [CITED: tests/test_records.py].
- **Recomputing the involute's first point** instead of sharing the curve's last `Vector` (gap risk) or sizing the involute radii from `spline_start`'s radial clamp.
- **Widening `check()`** to refuse trochoid-specific cases: 18 D-02/D-10/D-17 make every refusal a fall-back to radial with a sentence; `check()` consumes `_tooth` (radial) in both modes.
- **A second oracle or a bar picked after seeing a pass.** Reuse `tests/trochoid_oracle.py`; write both numbers beside the bar.
- **Putting kernel rows in `tests/test_trochoid.py`:** it runs at commit (`verify.fast`, 30 s kill, L36); kernel rows belong in `tests/test_model.py`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Root curve, cap, junction, undercut onset, `x_min`, waist | any new maths in `model.py` or `derive()` | `calc.root_mode` / `RootMode.curve`, `undercut_teeth`, `undercut_shift`, `RootCurve.waist` | Phase 18 proved them against T1-T4; the sweep has zero unexplained failures |
| Independent proof of the curve in the part | a second oracle or a snapshot of the implementation | `tests/trochoid_oracle.clearance` on `positionAt` samples | Shares no code with `calc`; floor 6.7e-15 m (18-RESEARCH) |
| Warning sentences | strings typed in tests or in `derive()` | `_ROOT_SENTENCES` + `root_warnings`; tests capture, never type (L33) | One place says it |
| Kernel fillet on the root | OCCT's fillet operator | the analytic radial path (unchanged) or the trochoid spline | L09: about 50x slower on a many-toothed outline |
| `bool` flag for the mode | `type=bool` | `Literal["radial", "trochoid"]` | `--flag false` reads true on the CLI |
| Float ceil/floor of printed values | `round()` for a bound | `math.ceil(x * 1000) / 1000` for `x_min`, the existing floor for the cap | A bound printed rounded the wrong way is false (F9, 18 F3) |

**Key insight:** every hard problem in this phase is already solved in `calc` or in the oracle. What remains is joining floats to a kernel without a gap and keeping every printed number tied to the same floats.

## Common Pitfalls

### Pitfall 1: The field-walk exemption is a hard-coded name
**What goes wrong:** `tests/test_cli.py:209-215` special-cases `recess_sides`; a second `Literal` fails "step in prop" and nothing else names it. **How to avoid:** derive the exempt set from `get_origin(annotation) is Literal` (Pattern 6). **Warning signs:** `KeyError: 'step'` on `root_shape` in the walk.

### Pitfall 2: D-02's placement breaks an adjacency pin from the tip-chamfer phase
**What goes wrong:** `tests/test_api.py:315` asserts `face_width` immediately follows `tip_chamfer`. **How to avoid:** edit it deliberately in the same commit as the field (it is the tip-chamfer phase's pin, not a defect). Also the 29-name set at `tests/test_api.py:78` and `tests/composition.py` `ALWAYS`.

### Pitfall 3: The tiny root arc
**What goes wrong:** F4. A user-typed `backlash` (or a request exactly at the cap) gives `a` in the dead band; `_build_checked` reports "try smaller fillets or chamfers" for a defect no user setting remedies. **How to avoid:** the `ROOT_ARC_MIN` branch plus the tuned-`backlash` test. **Warning signs:** `GC_MakeArcOfCircle::Value() - no result`.

### Pitfall 4: Numbers for a part not built
**What goes wrong:** `derive()` and `model._build` each deciding "trochoid or not" would be the three-predicates failure (PITFALLS 1). **How to avoid:** one `root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` per consumer call, the result passed down; `rfil` in trochoid mode is `rm.cutter.rho`, and `model` never calls `root_fillet(p)` for a trochoid part.

### Pitfall 5: SC5's "exit 2" for a kernel guard
**What goes wrong:** the plan promises every new refusal exits 2 on the CLI and the kernel guards cannot. See Open Question 2.

### Pitfall 6: Old sentence on a refused request
**What goes wrong:** with `root_shape = "trochoid"` refused for `tip land gone` or `tooth severed`, the radial path is built; the old undercut sentence ("this model uses a radial root instead") is then true and must stay, alongside the refusal sentence. Only a gear where `mode == "trochoid"` gets the restated sentence. (`nothing radial to replace` cannot co-occur with the old sentence: undercut implies `rb > rf`, 18-RESEARCH F9.)

### Pitfall 7: Tip chamfer effective can go negative if the junction nears the tip
**What goes wrong:** `ra - R_join - 0.001` is negative if the junction is within 1 micron of `ra`. **Measured:** the smallest `ra - R_join` over the sample is 0.044 mm, so unreachable today; a `max(0.0, ...)` or an assertion in the test keeps it that way. Low priority.

### Pitfall 8: `IN-01` becomes user-visible
**What goes wrong:** the `rho capped` sentence says "the largest" but prints a 3-dp floor, and can print "0.000 mm" (18-REVIEW IN-01: 12 teeth, module 1, 32.14 degrees, backlash 0 has a cap of 1.05e-4 mm). Phase 19 is where users first read it: fix the wording ("within 0.001 mm of the largest") and test the sentence from `root_warnings`.

### Pitfall 9: The 66 s bar is host-bound
**What goes wrong:** L34's 63.555 s was read on an Apple M2 Max with 12 CPUs; this host (Apple M5 Max, 18 CPUs) reads 46.21 s for 1,023 tests. A phase delta measured against the wrong baseline hides cost. **How to avoid:** record the baseline and the end-of-phase gate on the same host in the same session, with host and load beside both, and report the delta against the 66 s bar as L34 does.

### Pitfall 10: `derive()`'s docstring cost figure goes stale
**What goes wrong:** `calc.py:991-1000` quotes a measured per-call cost (14.7 microseconds, 2026-10-08). The default path gains one `root_mode` call (362 ns), and a trochoid request adds 33.7-88.9 microseconds. **How to avoid:** re-run `.venv/bin/python -m timeit -r 5 -s "from spur.calc import derive; from spur.params import GearParams; p=GearParams()" "derive(p)"` and the trochoid-on form, update the figure with host, load and date (D-14).

### Pitfall 11: "The generator never enters `model.py`" needs a check that can fail
**How to avoid:** a test that reads `src/spur/model.py` and asserts none of `_trochoid_point`, `_junction`, `_root_curve`, `trochoid_root`, `cutter(` appears (cheap, shaped like `test_calc_module_stays_log_free`).

### Pitfall 12: The must-debt trigger "Phase 19 planning"
`docs/tech_debt/INDEX.md` names it for the resource-tracker flake (`Severity: must`), re-deferred at Phase 18 close. Schedule a read and a recorded decision in the plan (not a `src/spur` edit): this session's `make verify` was green (1 of 43+ occurrences have printed it); Phase 19 adds no process-spawning test (all new kernel tests are in-process).

## Code Examples

### Reading the junction and the waist from the curve (derive side)
```python
# Source: calc.RootCurve as read this session (calc.py:1338-1346); field names are proposals
curve = rm.curve                              # RootMode.curve, set when mode == "trochoid"
form_d = round(2 * curve.points[-1][0], 3)    # D-04: cutter-envelope junction, never "ISO form diameter"
radius, half = curve.waist                    # smallest half-angle on the curve, refined between samples
waist = round(2 * radius * half, 3)           # arc, like tip_thickness; > 0 on any curve that survives
```

### A sentence from the cutter actually used (x_min rounding)
```python
# Source: scratch run; names proposed
x_min = undercut_shift(rm.cutter)                    # 0.4150787 at 10 teeth, m 1, 20 deg, rho 0.38
shown = math.ceil(x_min * 1000) / 1000               # 0.416: xi +2.7e-3 (0.415 would still undercut)
fits = shown <= 1.0                                  # 6 teeth, 14.5 deg, rho 0 -> x_min 1.0619: say so, print no shift
```

### The kernel-tier selector must fail loudly (L26 shape)
See Pattern 7: `assert len(root) == 2 * teeth` before sampling, so an empty or wrong selection is a failure and not a pass.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Radial lead-in + analytic fillet below the base circle (L09, L10) | Opt-in hob root: envelope of the tip arc as a spline per side (`root_shape = "trochoid"`) | this phase | Superseded for opted-in gears only; default part unchanged (L05) |
| Shipped undercut warning `2(1 - x)/sin^2(alpha)` (right only at 20 degrees) | Cutter-derived onset and `x_min` (trochoid mode only) | this phase | Radial wording stays so five fixture records stay byte-identical |
| STACK/PITFALLS spline deviation quoted from two different methods | One method, reproduced: point-to-polyline and the oracle on `positionAt` | this research | Kernel bar from a measurement |

**Deprecated/outdated:** the claim "the shipped flank deviates 6.0e-5 / 1.0e-4 mm" (STACK; a measurement floor) and "0.13 / 0.004 micrometre" (PITFALLS; not reproduced).

## Assumptions Log

> Claims tagged `[ASSUMED]` or proposals the planner or human must confirm before they become locked.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | SC5's "every new refusal routes identically to a 422 and to exit 2" means: invalid `root_shape` (422 / argparse exit 2) and the kernel guards (422 `build_error` / `spur export` exit 1 per `docs/architecture/cli.md`), not a literal exit 2 for a `BuildError` | Summary, Open Question 2 | If the human wants exit 2 for `BuildError`, `cmd_export` and the documented CLI contract change (a decision beyond this phase) |
| A2 | Kernel-tier bar `2e-3 * module` (11x the worst measured spline error); guard bars (spacing ratio 1000, area 5e-2, annulus TOL) | Pattern 4, Pattern 7 | Bars set too tight flake on CI libm; too loose miss a wrong root. 11x is at the project's 10x line, so it may be a checkpoint |
| A3 | `ROOT_ARC_MIN = 2e-6` mm | Pattern 3 | Wrong value either keeps the dead band reachable (too small) or drops a real arc (too large; harm bounded by the value) |
| A4 | The waist floor will be set by the oracle bar rather than a kernel failure, and will land at a human checkpoint | F8, Open Question 1 | If a different physical meaning is wanted (printability), D-07's rejected "absolute millimetre" option is back on the table |
| A5 | The chamfer law repeats on a 20-step bisection as it did at 14-16 steps | F5 | A configuration where the kernel fails earlier than `ra - R_join` would need a margin or a cap change |
| A6 | Timings are from an Apple M5 Max (18 CPUs), load 6-11, not the M2 Max of earlier sections | F7, F10 | Numbers are upper bounds for this host only; the phase must re-measure on one host |
| A7 | The 5,159-gear sample (stride 2 of the 31,446-entry product) represents the whole box | Pattern 4, F1 | A case outside the sample could trip a guard or the kernel; run the full product in `bench/` before pinning |
| A8 | `x_min` printed rounded up; "advise nothing" above 1.0 | Pattern 5, F9 | Wording choice; the rounding direction is arithmetic, the message is the planner's |
| A9 | Sentence firing condition compares at the printed `z_min` resolution | Pattern 5 | A tiny undercut (xi < 0 by less than 0.05 teeth) is silent though the join is a crossing |
| A10 | The web form and `DIMS` rows are verified by reading `app.js` and the schema/DIMS tests; no browser test exists | Pattern 6 | A UI regression would not be caught by the gate |
| A11 | The spike lives in `bench/` with its own outline builder, then is re-run against the real build | Plan shape | If the planner prefers a `curve=` parameter on `_outline` first, an intermediate commit has a branch only tests reach |
| A12 | The heaviest allowed low-tooth row is the 116-tooth corner (14.5 degrees, x -0.6, module 10) composed with keyway + 32 spokes; the 60-hole composed row at 116 teeth was not measured (the probe refused `hole_circle_d`) | F7 | Another composed row could be heavier; bench the full composed matrix after the field exists |

## Open Questions

1. **What does the waist floor mean, and who sets it?**
   - What we know: nothing breaks in the kernel above a 4.98e-3 mm waist at module 1; the spline error at the corners is 1.79e-4 m; `tooth severed` (waist <= 0) is already refused. The floor D-07 asks the bench to find ("the kernel refuses, or the spline-to-oracle gap leaves its bar") will therefore sit near the kernel bar (about 2e-3 m), below every built gear in the walk, so the warning would almost never fire.
   - What's unclear: whether a floor that never fires is what the human wants, or a printability floor (the project already has `MIN_TIP_FDM = 0.4` mm for tips [VERIFIED: src/spur/calc.py:19 "MIN_TIP_FDM = 0.4       # mm"]).
   - Recommendation: run the bench walk as D-07 says, present the numbers at the checkpoint D-07 already schedules, and let the human choose; do not pick before the walk exists.
2. **SC5's "exit 2" for kernel guards.** `[VERIFIED: docs/architecture/cli.md:38 "A parameter error raises `SystemExit(2)` — exit 2" and :47 "Every `BuildError` raises `SystemExit(f"error: {exc}")` the same way — exit 1"]`. This phase adds no `check()` refusal (every trochoid refusal is a fall-back with a sentence), so the only new refusals are the pydantic enum error (422 / exit 2, free) and the kernel guards (422 `build_error` / exit 1). Recommend recording A1's reading in the plan and the parity test (both code paths asserted separately), and stopping to ask only if the human wants the CLI contract changed.
3. **When does the restated undercut sentence fire** (printed resolution vs raw `xi < 0`)? Recommend the printed resolution with a one-tooth-step and one-field-step test (17/18 teeth at 20 degrees, tip radius 0.38; tuned shift either side).
4. **Is an 11x kernel bar acceptable or does the human want the checkpoint?** The 10x rule says "under about 10x goes to the human"; 11x is not under, but it is one measurement host. Recommend including the bar in the spike plan's checkpoint with the full-product maxima.
5. **`RootMode` is Phase 18's public shape.** Adding a defaulted `curve` field (IN-02's suggestion) changes no constructor call; confirm no test compares `RootMode` by tuple or `asdict`.
6. **`slug()` ignores `root_shape`,** so a radial and a trochoid download of the same gear share a filename [VERIFIED: src/spur/params.py:179-181 "return f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}""]. Not a defect of this phase; file a `docs/ideas/` item if the planner agrees.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + `.venv` | everything | yes | 3.12.15 | none needed |
| cadquery / cadquery-ocp | spikes, kernel tier | yes | 2.8.0 / 7.9.3.1.1 | none |
| pytest, xdist, cov, ruff, mypy, import-linter | the gate | yes | 9.1.1 / 3.8.0 / 7.1.0 / 0.16.10 / 2.4.0 / 2.15 | none |
| `make` (GNU) | gate and bench targets | yes | 4.4.1 | none |
| git | commits, fixture diff | yes | 2.56.0 | none |
| Docker | `make check` only | client present (29.8.2, orbstack context); daemon not probed | not needed for `make verify` | skip |
| `gh` | `make pr.land` | yes | 2.102.0 | none |

**Missing dependencies with no fallback:** none.
**Host (for every timing, A6):** Apple M5 Max, 18 CPUs, macOS 27.0.1; `PYTEST_WORKERS` stays 8.

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` (keys: `workflow._auto_chain_active`, `workflow.use_worktrees`, `git.branching_strategy`), so it is treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + xdist 3.8.0 + cov 7.1.0 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`: `filterwarnings = ["error", ...]`, `--strict-markers`; `[tool.coverage.*]`: `branch = true`, `fail_under = 96`) |
| Quick run command | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (targeted; kernel rows: `tests/test_model.py -k trochoid`) |
| Commit-time slice | `make verify.fast` (11.3 s on the M2 Max, L36; includes every test file except `test_model.py`, `test_pool.py`, `test_api.py`, `test_cli.py`) |
| Full suite command | `make verify` (1023 passed in 45.59 s here, F10) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-root-mode-decided | default `root_shape` is `"radial"`; all 44 fixture records read radial / "not requested" through `p.root_shape`; fixture unchanged; walk generalised; `--root-shape false` rejected; L38 exists | unit + regression | `git diff --exit-code tests/regression/pre_v0_2.json && make test PYTEST_ARGS="tests/regression tests/test_cli.py -k 'root_shape or every_gear_field or pre_v0_2' -q -n0 --no-cov"` | partly (`tests/test_trochoid.py::test_every_pre_v0_2_record_reads_radial_because_nobody_asked` exists; walk edit Wave 0) |
| REQ-outline-consumes-root-curve | closed valid solid per swept rows; 6 faces/tooth; `positionAt` samples vs oracle at the bar; tripwire (printed ρ + 0.05 mm) over the bar; each guard raises `BuildError` on a hand-built curve; short-arc branch (tuned `backlash`, `a = 0`); `root_d == 2*rf` in both modes; source grep: no generator names in `model.py` | kernel + unit | `make test PYTEST_ARGS="tests/test_model.py -k trochoid -q -n0 --no-cov"` | no, Wave 0 |
| REQ-derived-numbers-honest-under-trochoid | `root_thickness`/`root_gap` null + one captured sentence; same numbers radial; `root_form_d` == 2 * R_join at 3 dp; waist value == 2 R h; floor warning at the pinned boundary one field step either side; no lead-in warning under trochoid; new fields null on replay | unit | `make test PYTEST_ARGS="tests/test_trochoid.py tests/test_calc.py -k 'derive or waist or form_d' -q -n0 --no-cov"` | no, Wave 0 |
| REQ-cutter-tip-radius-settable | `derive().root_fillet` == `cutter(p, p.root_fillet).rho` at 3 dp; cap sentence from `root_warnings`; cap one step either side (m 1, 20 degrees: 0.471 vs 0.472 requested); the CLI/API expose it | unit + CLI | `make test PYTEST_ARGS="tests/test_trochoid.py tests/test_cli.py -k 'tip_radius or rho' -q -n0 --no-cov"` | no, Wave 0 |
| REQ-undercut-warning-restated | radial sentence byte-identical (five records); trochoid sentence captured from `derive()`, no "radial root"; fires 17 vs 18 teeth (20 degrees, tip radius 0.38); tuned shift either side; `x_min` rounded up; out-of-range `x_min` message | unit | `make test PYTEST_ARGS="tests/test_trochoid.py -k undercut -q -n0 --no-cov"` | partly (T1 closed forms exist) |
| REQ-trochoid-composes-and-is-priced | compose matrix builds (tip chamfer at cap x recess x each cutout, trochoid on); chamfer cap builds / one step past fails on a binding config; `_tip_edges` selector matrix trochoid column; `bench/RESULTS.md` rows (heaviest row vs 30 s, chamfer bisection, gate cost vs 66 s); `spur info` == `/api/info` bytes for trochoid and radial; new sweep file pinned by `tests/test_bench.py` | kernel + parity + bench | `make test PYTEST_ARGS="tests/test_model.py tests/test_cli.py tests/test_bench.py -k 'trochoid or compos' -q -n0 --no-cov"`; bench: `make bench.build SWEEP=bench/sweeps/trochoid.json` | no, Wave 0 |

### Sampling Rate
- **Per task commit:** plain `git commit` (the L36 hook runs `make verify.fast`), plus by hand: `git diff --exit-code tests/regression/pre_v0_2.json`; `.venv/bin/python -m pytest tests/regression -q -n0 --no-cov` (86 passed this session); `grep -rnE 'numpy|scipy' src/spur` prints nothing; `grep -c '==' requirements.txt` stays 31.
- **Per wave merge:** `make verify` (full gate).
- **Phase gate:** `make verify` green with the result line stated, and its wall time recorded against the 66 s bar with host and load, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_trochoid.py` additions: derive branch, sentences, waist/floor, `x_min`, `spline_start`/chamfer limit, enum/CLI parity pieces that need no kernel
- [ ] `tests/test_model.py` additions: kernel tier (build rows, `positionAt` vs oracle, guards, short arc, compose, selector column)
- [ ] `tests/test_cli.py` (walk generalisation, parity document, bad value exit 2) and `tests/test_api.py` (line 315 adjacency, the literal field set, DIMS keys)
- [ ] `tests/composition.py`: a root axis or a separate trochoid table; `ALWAYS` split
- [ ] `bench/` spike subcommands + `bench/sweeps/trochoid.json` + `tests/test_bench.py` pin + `bench/RESULTS.md` section
- [ ] Framework install: none

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. The phase adds one validated enum field, pure functions and a CAD path; no endpoint, no new dependency, no file or network access.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `root_shape` is a pydantic `Literal` (422 for anything else); `root_fillet` is `ge=0, le=3` and rejects NaN/inf [VERIFIED: scratch run, `GearParams(root_fillet=nan/inf)` refused; `-0.0` accepted, pre-existing]; the new `cutter()` `ValueError` stays unreachable from user input |
| V6 Cryptography | no | — |
| V14 Supply chain | yes | no new package; `requirements.txt` unchanged |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Resource exhaustion via a slow build (a requested trochoid on a heavy composed gear) | Denial of service | `SPUR_BUILD_TIMEOUT` (30 s) + 503 (L37); measured: heaviest low-tooth row 12.2 s, 200-tooth rows ignore the request so are unchanged |
| A wire that opens or a spline that swings producing a valid-looking wrong part | Tampering (integrity, L08) | the four structural guards raising `BuildError`, not `isValid()` alone |
| A plausible wrong number for a part not built that way | Information integrity (L08) | one `root_mode` per consumer, null + sentence for numbers that do not apply, printed ρ is the cut ρ (Pattern 7) |
| Unvalidated numeric reaching `acos`/`atan2` | Tampering | unchanged: Phase 18's `min(1.0, rb/R)` and the closed-form refusals |

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `CLAUDE.md`; `.planning/phases/19-the-trochoid-in-the-part/19-CONTEXT.md`; `.planning/REQUIREMENTS.md`; `.planning/ROADMAP.md` (Phase 20 entry); `.planning/phases/18-trochoid-maths-proved/18-RESEARCH.md`, `18-REVIEW.md` (IN-01, IN-02, IN-05, IN-07), `18-REVIEW-DISPOSITION.md`, `18-CONTEXT.md` (D-13..D-17); `.planning/research/{ARCHITECTURE (1.1-1.7, 4-7), PITFALLS (7, 8, 16-20, phase table), SUMMARY (correction 16), STACK (grep)}.md`; `src/spur/calc.py` (lines 1-340, 577-700, 860-1240, 1240-1589); `src/spur/model.py` (whole); `src/spur/params.py`; `src/spur/cli.py`; `src/spur/static/app.js` (1-160); `src/spur/app.py` (info/model routes); `tests/test_cli.py` (field walk, README example), `tests/test_api.py` (schema, openapi, adjacency), `tests/composition.py`, `tests/trochoid_oracle.py`, `tests/regression/test_pre_v0_2.py`; `bench/trochoid.py` (sweep grids, `rack`, `check_curve`), `bench/build_time.py`, `bench/tip_chamfer_spike.py` (head); `bench/RESULTS.md` (Phase 18 sections); `docs/architecture/decision_log.md` (L09, L10, L29, L33, L34, L36, L37), `docs/architecture/cli.md` (Errors), `docs/architecture/http-api.md`, `docs/architecture/solid-model/tactics.md`, `gear-maths/{strategy,implementation}.md`, `docs/ideas/2026-09-21-trochoidal-root-fillets.md`, `README.md` (CLI, parameters, geometry notes), `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`, `docs/tech_debt/INDEX.md`, `Makefile`, `pyproject.toml`.
- Installed-source checks: `inspect.signature`/`getsource` of `cq.Edge.makeSpline`, `cq.Edge.positionAt`, `cq.Wire.assembleEdges` (cadquery 2.8.0).
- Scratch runs this session (scratchpad, outside the repo; HEAD `cb5fbd9`, Apple M5 Max, Python 3.12.15, cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1): trochoid outline builder; the 15,723-case sweep with guard numbers; the deviation reconciliation (A/B methods, shipped flank and trochoid); bunching experiment (ratio vs deviation vs kernel exception); root-arc dead band; chamfer bisection on 8 configs (14-16 steps); build times on six rows radial vs trochoid and nine gate-size composed rows; waist walk (6/7/8 teeth, 14.5 degrees); kernel-tier oracle on `positionAt`; `x_min` rounding and range; `make verify` baseline (`1023 passed in 45.59s`).

### Secondary (MEDIUM confidence)
- STACK/FEATURES/PITFALLS figures as quoted by SUMMARY (cross-checked above where this session could reproduce them).

### Tertiary (LOW confidence)
- None used for a recommendation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - nothing new; versions read from `.venv`.
- Architecture: HIGH - the seams are read; a scratch build proves the outline over 5,159 gears.
- Pitfalls: HIGH for F4, F5, F9 and the test-edit traps (each run or read); MEDIUM for the proposed bars and floor (sample, not whole product; A2, A4, A7).

**Research date:** 2026-10-08
**Valid until:** about 30 days for the repo facts (HEAD `cb5fbd9`); the kernel pair is pinned, so the kernel numbers hold until it moves.
