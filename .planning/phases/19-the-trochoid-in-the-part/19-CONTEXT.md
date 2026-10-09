# Phase 19: The Trochoid in the Part - Context

**Gathered:** 2026-10-08
**Status:** Ready for planning

<domain>
## Phase Boundary

The proven Phase 18 curve reaches the built solid, the printed numbers and all three
interfaces behind one default-off field, and no part a shared link produces today changes:

1. **The field** — `root_shape: Literal["radial", "trochoid"] = "radial"` on `GearParams`
   (group Teeth), read by `calc.root_mode(p, pr, requested=p.root_shape, rho=...)`; the
   fixture `tests/regression/pre_v0_2.json` is byte-identical after every task and the 85
   replay cases pass unmodified (L05, L26).
2. **ρ** — `root_fillet` is reinterpreted as the hob tip radius in trochoid mode (D-01
   below); the capped value is printed in the existing `root_fillet` derived field.
3. **The outline** — `model._outline` replaces the fillet arc plus lead-in, per tooth side,
   with one `makeSpline` through `RootCurve`; the involute spline starts at the junction
   radius taken from the same float; structural guards that do not depend on `isValid()`
   (coincident junction vectors, spacing-ratio check, annulus bounds, closed-form area
   check); `spline_start` and `tip_chamfer_limit` read the active root; the trochoid
   generator never enters `model.py`.
4. **The numbers** — every number printed beside the trochoid has a proof or a warning:
   `root_thickness`/`root_gap` null with a warning, `root_form_d` printed as the
   cutter-envelope junction, the waist printed and warned below a measured floor, the
   undercut sentence restated from the cutter with `x_min`, no lead-in warning without a
   chord; in radial mode the five fixture records carrying the old sentence stay
   byte-identical.
5. **Composition and price** — tip chamfer (L29's boundary re-bisected across the
   spline-to-spline junction, spiked before any schema change), face recesses and each
   cutout pattern with the trochoid on; the heaviest allowed low-tooth row measured against
   `SPUR_BUILD_TIMEOUT` in `bench/RESULTS.md`; `make verify` priced against the 66 s bar
   (L34); a kernel-tier proof comparing `Edge.positionAt` samples of the root edge to the
   Phase 18 oracle at a measured bar.
6. **Parity and record** — the model-driven field walk covers the new field across schema,
   web form and CLI (the `recess_sides` enum exemption generalised); `spur info` and
   `/api/info` byte-identical; every new refusal a `422` and exit 2; the new `Lxx`
   (supersedes L10, amends L09 and L33) names the deferred flip and its trigger; README,
   `docs/architecture/gear-maths/`, `docs/architecture/solid-model/` and
   `docs/ideas/2026-09-21-trochoidal-root-fillets.md` brought true in the same change.

Not in this phase: the flip itself (Phase 20, recorded skipped per D-07 below); any
change to the 44 fixture records; a second ρ field; a strength or stress number
(FEATURES: geometry only); numpy/scipy; any new pin.

Success criteria 1–5 of the ROADMAP entry are the acceptance.

</domain>

<decisions>
## Implementation Decisions

### The two new fields
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

### Root numbers under the trochoid
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

### Undercut waist floor
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

### The flip's schedule (Phase 20)
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

### Carried forward from Phase 18 (locked, not re-discussed)
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

### Carried forward from ROADMAP.md / REQUIREMENTS.md (locked)
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and milestone intent
- `.planning/ROADMAP.md` — Phase 19 entry (goal, success criteria 1–5, placement of
  REQ-root-mode-decided and REQ-undercut-warning-restated, order inside the phase, research
  flag); Phase 20 skip condition.
- `.planning/REQUIREMENTS.md` — REQ-root-mode-decided, REQ-outline-consumes-root-curve,
  REQ-derived-numbers-honest-under-trochoid, REQ-cutter-tip-radius-settable,
  REQ-undercut-warning-restated, REQ-trochoid-composes-and-is-priced; "Trochoid follow-ups".
- `.planning/phases/18-trochoid-maths-proved/18-CONTEXT.md` — D-01…D-17 (root mode, the
  cutter, refusals, the sweep) that this phase consumes.
- `.planning/phases/18-trochoid-maths-proved/18-REVIEW.md` and `18-REVIEW-DISPOSITION.md` —
  the 8 open info items and the two cross-review fixes; IN-02 (two entry points, discarded
  curve) and IN-07 (`ValueError` from `root_mode`) touch this phase's wiring.

### Milestone research (v0.4)
- `.planning/research/ARCHITECTURE.md` §1.5 (seam B: the `Literal` field, the field-walk
  exemption, `gearQuery()` omitting defaults), §1.6 (known-good proof: two tiers,
  `Edge.positionAt`), §1.7 (other consumers: `tip_chamfer_limit`, `_tip_edges`, docs that
  state the radial claim).
- `.planning/research/FEATURES.md` — finding 3 (root thickness ill-conditioned), finding 5
  (waist vs fillet), the 0.021·m waist corner, the open decisions 2 and 3 this context
  settles.
- `.planning/research/PITFALLS.md` — 1 (three predicates), 2 (landing dark), 6 (printed
  numbers drift), 7 (sampling and kernel handling), 8 (tolerance picked to pass), 16
  (undercut warning), 17 (`root_fillet` meaning changes silently), 18 (gate and build
  budget), 19, 20.
- `.planning/research/STACK.md` — the N = 16 deviation table, the `Edge.positionAt` proof
  shape; `.planning/research/SUMMARY.md` — corrections 14 and 16.

### Decisions and code
- `docs/architecture/decision_log.md` — L03, L05, L08, L09, L10, L26, L27, L29, L33, L34,
  L36, L37 (the new `Lxx` supersedes L10 and amends L09 and L33).
- `src/spur/calc.py` — `root_fillet`, `spline_start`, `tip_chamfer_limit`, `derive`
  (the `z_min` sentence at ~1047, the lead-in warning at ~1023, the ignored-field sentence
  shape at ~1052), `cutter`, `undercut_teeth`, `undercut_shift`, `root_mode`,
  `_ROOT_SENTENCES`, `root_warnings`, `RootCurve`, `trochoid_root`.
- `src/spur/model.py` — `_outline` (133–187), `_gear_blank`, `_tip_edges`.
- `src/spur/params.py` — `root_fillet` (47), `tip_chamfer` (50), `recess_sides` (91).
- `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`
  (187) — the field walk and its `recess_sides` exemption.
- `tests/regression/pre_v0_2.json` and the replay in `tests/` — the 44 records, 85 cases.
- `tests/test_trochoid.py`, `tests/trochoid_oracle.py`, `bench/trochoid.py`,
  `bench/RESULTS.md` ("root-shape step", "worst junction gaps", the per-call costs) — the
  oracle and bars this phase's kernel tier compares against.
- `docs/architecture/gear-maths/strategy.md`, `implementation.md`, `tests.md`;
  `docs/architecture/solid-model/*.md`; `README.md` geometry notes (~222–226) and the
  parameter table; `docs/ideas/2026-09-21-trochoidal-root-fillets.md` — the documents the
  phase brings true.
- `docs/HOW_TO_DEVELOP.md` §2, §7, §8 — branch, cross-CLI review, landing.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `calc.root_mode` / `root_warnings` / `cutter` / `trochoid_root` / `RootCurve`: the whole
  predicate and curve exist and are proved; this phase only passes `requested=p.root_shape`
  and `rho=p.root_fillet` and consumes `mode`, `reason`, `cutter.rho` and the curve.
- `calc.root_fillet()` cap-and-round shape and `derive()`'s capped-value warning: the
  pattern for printing ρ at 3 dp with the cap named.
- `derive()`'s ignored-field sentence (hex bore, D-02 of Phase 8) and L33's lead-in
  warning: the sentence shapes for anything that does not apply.
- `params.recess_sides`: the one `Literal` field; `cli._add_gear_args` and `app.js`'s
  `enum` → `<select>` already handle it.
- `_fillet_corner` and `_outline`'s per-tooth loop: the arc/line/spline assembly the
  trochoid spline replaces per side.
- `bench/trochoid.py` (`rack`, `check_curve`, the sweep and oracle runners) and
  `tests/trochoid_oracle.py::clearance`: the independent oracle for the kernel tier.

### Established Patterns
- A parameter validated once at `GearParams`; `root_fillet` is already `_f(0.5, 0, 3)`.
- Post-fixture `DerivedDimensions` fields are `float | None`, null on replay (L27 pattern).
- Bars from two recorded numbers with headroom beside them; under ~10× to the human.
- Structural kernel assertions, never `isValid()` alone (L26's edge selector, PITFALLS 7).
- `verify.fast` at commit, `make verify` before push; cross-CLI review on the PR.

### Integration Points
- `params.GearParams`: `root_shape` field (D-02); `root_fillet` help text (D-01).
- `calc.derive`: `root_mode` call, `root_form_d`, the waist field, null `root_thickness`/
  `root_gap`, the restated undercut sentence, the lead-in warning guard.
- `calc.spline_start` / `tip_chamfer_limit`: read the junction radius under trochoid.
- `model._outline` / `_gear_blank` / `build`: the spline per side; guards; `_tip_edges`
  unaffected in principle (compose test proves it).
- `tests/test_cli.py` field walk; README parameter table; `docs/architecture/*`;
  `decision_log.md` new `Lxx`; `bench/RESULTS.md` new rows.

</code_context>

<specifics>
## Specific Ideas

- The user wants one knob for root rounding: `root_fillet` means "the radius that shapes
  the root" in both modes, with the mode select beside it.
- Honest-number stance throughout: null + warning over a redefined field; the waist is
  printed, not refused; `root_form_d` is a junction, not a standard's form diameter.
- The flip trigger is demand, not time: a real fit report or a mating pair below `z_min`.

</specifics>

<deferred>
## Deferred Ideas

- The default flip (Phase 20): `Skipped (O4, flip deferred)`; owned by REQUIREMENTS.md
  "Trochoid follow-ups" with D-09's trigger.
- Form-circle thickness/gap fields (rejected in D-03): revisit only if a user asks for a
  number at `root_form_d`.
- A separate `cutter_tip_radius` field (rejected in D-01): revisit if a shop needs a hob
  radius different from the analytic fillet on the same link.

</deferred>

---

*Phase: 19-The Trochoid in the Part*
*Context gathered: 2026-10-08*
