# Phase 14: Honest Record - Context

**Gathered:** 2026-10-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Three record fixes on geometry the tool already builds — no new `GearParams` field, no
outline change, no new `DerivedDimensions` field, `tests/regression/pre_v0_2.json` (44
records) byte-unchanged throughout:

1. **The warning** (REQ-root-lead-in-warned, SC1). `derive()`'s `warnings` carries a
   sentence when the root fillet's straight lead-in ends above the pitch circle —
   `spline_start(pr, root_fillet(p)) > pr.r` — naming the height in mm (3 dp) and that
   the chord deviates from the involute there. Pure `calc.py`; proven at the three debt
   configurations and one field-step either side of the crossing. 0 of 44 fixture records
   cross (verified at kickoff 2026-10-01), so no pinned `warnings` tuple moves.
2. **The record** (REQ-readme-root-zone-states-the-limit, SC2). README's root-fillets
   bullet (lines ~225–228) and the twin claim in `_outline`'s docstring
   (`src/spur/model.py:136–139`) state the real condition and cite the warning. No number
   in README the phase did not itself measure.
3. **The proof** (REQ-filleted-spoke-closed-form, SC3). The filleted-spoke row of
   `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` asserts the removed
   volume against an independent closed form; the shared assertion is tightened to the
   `1e-9 mm³` bar the record already claims; the pinned literal `2934.725405` becomes a
   comment; a tripwire shows the assertion go red when `_fillet_corner`'s `inside=True`
   tangent root is perturbed.
4. **The ledger** (SC4). Both debt files retire in their fixing commits (`Status:
   resolved`, sha, `git mv` to `docs/tech_debt/resolved/`, `docs/tech_debt/INDEX.md` rows
   26–27 moved); one new L33 answers L30's "pinned, not derived" clause without touching
   L30's text; the planning record's own false sentence about the volume bar is
   corrected.

Not this phase: an outline change that keeps the lead-in below the pitch circle (human's
kickoff choice: warn, not re-cut — `REQUIREMENTS.md` "Out of Scope"); a per-gear
chord-deviation number; L10's trochoidal root; anything in Phases 15–16.

</domain>

<decisions>
## Implementation Decisions

### The warning (REQ-root-lead-in-warned)
- **D-01:** **Fires at the printed resolution, not the raw float.** `h = spline_start(pr,
  root_fillet(p)) - pr.r`; the warning is appended iff `round(h, 3) > 0` (h ≥ 0.0005 mm),
  so "0.000 mm above the pitch circle" can never print. 10-REVIEW.md CR-01's rule: `derive()`
  compares at the resolution it prints (the tip-chamfer and spoke-fillet branches'
  precedent). Rejected: raw `spline_start > pr.r` (can print a zero height at a
  float-residue crossing).
- **D-02:** **The sentence is fact + cause; it quotes no deviation figure and no remedy
  number.** Working draft: `The flank starts with a straight chord reaching {h:.3f} mm
  above the pitch circle, where it deviates from the involute: the root fillet is larger
  than half the dedendum.` The planner may tune the words, not the content; the test
  asserts the full string (CR-01: a prefix assert cannot see a wrong suffix). Rejected: a
  per-gear computed deviation (new product maths and a new derivation to prove — deferred);
  a static "up to about 0.035 mm" bound (the 35.29/32.28/31.73 µm figures exist only as
  planning-time numbers in `10-05-PLAN.md` and the debt file — no script in the repo
  produced them, and three points do not bound a field range); "a root fillet of X mm or
  less keeps it below" (a second number to prove at every step).
- **D-03:** **Test rows: the three debt configurations plus two measured step pairs.**
  Measured 2026-10-02 on the pinned code (`.venv/bin/python`, `spline_start(pr,
  root_fillet(p)) - pr.r`), reproducing the debt file's three numbers exactly:

  | Row | `root_fillet(p)` | dedendum `r−rf` | height | warns (3 dp) |
  |---|---|---|---|---|
  | default | 0.500 | 2.1875 | −1.1875 | no |
  | `{profile_shift 1.0, pressure_angle 14.5}` | 0.500 | 0.4375 | +0.5625 | yes |
  | `{profile_shift 0.75, pressure_angle 20}` | 0.500 | 0.8750 | +0.1250 | yes |
  | `{profile_shift 0.65, pressure_angle 14.5}` | 0.500 | 1.0500 | −0.0500 | no |
  | `{profile_shift 0.70, pressure_angle 14.5}` | 0.500 | 0.9625 | +0.0375 | yes |
  | `{profile_shift 0.75, pressure_angle 20, root_fillet 0.40}` | 0.400 | 0.8750 | −0.0750 | no |
  | `{profile_shift 0.75, pressure_angle 20, root_fillet 0.45}` | 0.450 | 0.8750 | +0.0250 | yes |

  The `profile_shift` pair steps the field's own 0.05 at pa 14.5; the `root_fillet` pair
  steps 0.05 at `{0.75, 20}`. **Trap, measured:** at the default 25° pressure angle the
  0.5 mm fillet is capped by `0.45 × gap` at x 0.65/0.70 (0.414/0.403 mm) and no crossing
  occurs — the profile-shift pair must sit at pa 14.5, and along `root_fillet` at the
  default gear the cap binds before any crossing (1.09 mm needed, cap 0.724). The expected
  string in each warning row is whatever `f"{h:.3f}"` yields on the pinned code, captured
  once and asserted exactly — never hand-typed (0.0375 is not exact in binary; its 3-dp
  print is the code's to decide). A third pair along `module` is available but not
  required: `{x 1.0, pa 14.5}` m 3.95 → +0.0125 / m 4.05 → −0.0125 (measured). Rejected:
  `profile_shift` only (leaves the `root_fillet` driver unproven at its step); all three
  axes as a requirement.
- **D-04:** **No new field, no fixture motion.** The height is not added to
  `DerivedDimensions` — a new key would change every fixture record's `derived` dict (a
  byte change under L26) — and `GearParams` gains nothing (milestone rule). The warning's
  position in the tuple is Claude's discretion (recommended: directly after "Root fillet
  reduced …", its cause's neighbour); `tests/regression/test_pre_v0_2.py` stays green by
  construction since 0 of 44 records cross.

### The volume bar (REQ-filleted-spoke-closed-form, the conflict)
- **D-05:** **`abs=1e-9 mm³` on all four rows of
  `_assert_the_cutout_is_what_derive_prints`.** Today the shared assertion is
  `pytest.approx(d_volume, rel=1e-6)` (`tests/test_model.py:1196`, ≈2.9e-3 mm³ at 2935
  mm³); the "1e-9 mm³" in the test docstring, L30 and `11-08-SUMMARY.md` is a *measured
  agreement*, not the asserted bar — REQUIREMENTS.md's "the same 1e-9 mm³ bar the holes,
  sharp-spoke and honeycomb rows already meet" is true as measurement, false as assertion.
  The phase makes the claim true: each row's kernel–formula gap is measured in-phase
  before the tolerance is tightened, and the per-row gaps are recorded in the proof's
  docstring and in L33. Rejected: keep `rel=1e-6` and record two numbers (leaves the
  record saying one thing and the assertion another); tighten the filleted row only
  (inconsistent bars inside one proof). — **Reversibility:** reversible — one test
  tolerance.
- **D-06:** **A miss halts; the bar is never loosened by the executor.** If any row's
  measured gap reads above 1e-9 mm³, the executor stops at a checkpoint with the per-row
  numbers (13 D-09's shape) and the human picks between a formula error to find and a bar
  loosened to a measured value logged in L33 with its reason. "Measured, never tuned"
  (REQUIREMENTS.md rules; L08). Rejected: the executor loosening to the measured gap (bakes
  a formula error in as a 'measured' bar — the exact failure the debt file names).
- **D-07:** **The planning record's sentence is corrected in this PR.** One sentence each
  in `REQUIREMENTS.md` REQ-filleted-spoke-closed-form and `ROADMAP.md` Phase 14 SC3:
  measured to 1e-9 mm³ in Phase 11, asserted at `rel=1e-6` until this phase. Honest Record
  applies to the ledger too; rides the `.planning/` commit of the closed-form plan.
  Rejected: leave it and let L33 carry the correction alone.

### The closed form and its tripwire
- **D-08:** **A pure-maths helper beside `_spoke_bar_area` (`tests/test_model.py:1111`),
  derivation in its docstring.** Name is Claude's discretion
  (`_filleted_spoke_sector_area(rh, rr, o, rho)` or kin). No kernel import, no `bench/`
  script, no new module. The proof's filleted row **and** the tripwire parametrization
  (`test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`, the `spokes-filleted`
  row currently carrying `2934.725405`) both take `d_volume` from it — one oracle. The
  literal survives only as a comment in the proof's docstring: "first measurement
  2026-09-29 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1: 2934.725405 mm³". Rejected: a
  `bench/` script imported by the test (bench/ is for measurements; the import crosses a
  boundary); keeping the literal in the tripwire's row (a second copy of the number being
  demoted).
- **D-09:** **The oracle solves the tangent geometry itself; it never calls
  `_fillet_corner`.** For each of a sector's four corners the helper re-derives the tangent
  points in its own scalar/polar form — hub corners outside the hub circle (centre at
  `rh + ρ`), rim corners inside the rim circle (centre at `rr − ρ`), bar sides at
  perpendicular offset `±o` from the sector's radial lines, every corner on its circle
  (`_spoke_sector`'s `foot()` convention) — and computes the cut-off area from them. A
  wrong root, sign or side in `model.py` then disagrees with the oracle, which is the debt
  file's whole point. **Note for the planner:** REQ's "four circular-segment corrections"
  is loose wording — the area removed at a line–circle corner is the region bounded by
  the bar side, the hub/rim circle and the fillet arc: the polygon `[corner, on_line,
  centre, on_root]`, minus the fillet's own sector between its two tangent points, plus or
  minus the big circle's segment between `on_root` and the corner. The planner states the
  actual formula in the docstring and the executor measures it against the kernel (D-05)
  before trusting it. Rejected: taking the points from `_fillet_corner` and computing areas
  only (the oracle inherits the root selection; a wrong root moves both sides equally and
  the assertion stays green — does not retire the debt as written).
- **D-10:** **The tripwire shifts the `inside=True` tangent root by a small amount on a
  solid that still builds.** `spur.model._fillet_corner` is monkeypatched (10-03 / 11-08's
  shape; `_spoke_sector` resolves it through the module global) with a version whose
  `inside=True` branch moves `t` by +0.01 mm; the part builds, the removed volume moves on
  the 1e-2 mm³ scale, and the `abs=1e-9` assertion goes red while `derive()` still prints
  `spoke_fillet_effective`. Whether the perturbed solve is a copy in the test or a wrapper
  around the original is Claude's discretion; the original function is unchanged.
  Rejected: the far root (`t = -b + root` under `inside=True` — the literal "wrong root",
  but likely an invalid solid raising `BuildError`, a louder failure than the one the debt
  names); both as two rows (a second kernel build for a different claim).

### The record
- **D-11:** **One L33 with two headed parts, append-only.** L26–L32 are exactly one entry
  per phase; L33 keeps the pattern. Part one amends L09/L10's neighbourhood — the README
  and `_outline` claim — recording the kickoff choice "warned, not re-cut" (the outline
  change with fixture regeneration was the path not taken; the trochoidal root stays
  `docs/ideas/`) and the D-01/D-02 rule. Part two amends L30's "pinned for the filleted
  spoke, which has none" clause — L30's text untouched (Phase 12 D-18 precedent) — with
  the closed form, the per-row measured gaps, and the bar now asserted (D-05). Title is
  Claude's discretion; it should name both. Rejected: L33 + L34 (one id per topic; breaks
  the one-per-phase pattern).
- **D-12:** **README's root-fillets bullet states the formula and the default gear's
  number.** Working draft for `README.md` ~225–228: "… Where a fillet needs room above
  the base circle, the flank starts with a short chord onto the involute — 1.188 mm below
  the pitch circle on the default gear, and above it when the root fillet exceeds half the
  dedendum, `(1.25 − x)·m / 2`, in which case `warnings` says how far." Both numbers are
  proven by D-03's tests, so both are numbers the phase measured; the 35 µm figure is not
  quoted. The undercut bullet's "the UI warns when that applies" is the shape to match.
  Rejected: condition in words only (REQ's own wording; says less than the tool knows);
  formula without the default's number.
- **D-13:** **`_outline`'s docstring (`src/spur/model.py:136–139`) is corrected in the
  README commit.** "the chord sits in the non-working root zone and deviates from the
  involute by microns" is the same false claim; prose-only `src/` change, fixture untouched
  by construction. The sentence points at the warning (`calc.derive` warns when the chord
  ends above the pitch circle).
- **D-14:** **Retirement and commits.** Debt file 1
  (`2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md`) retires in the README
  commit, citing both the warning commit's sha and its own (REQ: "with this and the
  previous requirement's sha"); debt file 2
  (`2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md`) retires in the
  closed-form commit; `docs/tech_debt/INDEX.md` rows 26–27 move to the resolved table in
  those commits. L33's commit placement is Claude's discretion (precedent both ways: L29
  was its own docs commit, L32 rode the retiring plan).
- **D-15:** **Process (13 D-18, ROADMAP "Process Notes").** Branch
  `gsd/phase-14-honest-record` cut from `origin/main` `5d9e907` (PR #16 landed); plain
  `git commit` with explicitly staged files (the `make verify` hook runs ~3.5 min at 907
  tests; `gsd_run query commit`'s 30 s timeout cannot survive it); lands via `make pr.land
  PR=N` (L22/L25); `.planning/` rides the same PR. Who wrote the diff does not review it
  (CLAUDE.md: cross-CLI review).

### Claude's Discretion
- The warning's position in the `warnings` tuple (recommended: after "Root fillet
  reduced …") and its exact words within D-02's content.
- Helper and test names; whether the module step pair (D-03) is added as a third pair.
- The tripwire's mechanism (perturbed copy vs wrapper) and the shift's exact size, provided
  the solid still builds and the assertion goes red.
- Plan order. Suggested: (1) warning + tests; (2) README + `_outline` docstring + debt file
  1 retirement; (3) closed form + bar tightening + tripwire + debt file 2 retirement;
  (4) L33 + REQ/SC3 wording. Each lands as its own commit under the one-concern rule.
- Whether the per-row 1e-9 measurements also get a `bench/RESULTS.md` section. Default:
  the proof's docstring and L33 only — `RESULTS.md` is the timing/memory ledger.
- The L33 title and its Reason paragraph's wording.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements, roadmap, project
- `.planning/REQUIREMENTS.md` — "### Honest record": REQ-root-lead-in-warned,
  REQ-readme-root-zone-states-the-limit, REQ-filleted-spoke-closed-form (the three
  contracts and their acceptance text); "Rules every requirement lives by" (same part;
  retired in the fixing commit; measured, never tuned); "Out of Scope" (outline fix); the
  sentence D-07 corrects.
- `.planning/ROADMAP.md` "### Phase 14: Honest Record" — goal, SC1–SC4 (SC3 is the
  sentence D-07 corrects), "Research flag: No"; "## Process Notes (carried forward)".
- `.planning/PROJECT.md` — "Current Milestone: v0.3 Clean Ledger" (the root lead-in and
  filleted-spoke target-feature text, the three rules).
- `CLAUDE.md` — the two standing rules (L08, L05/L03), "Finishing work properly",
  "Capturing ideas and debt" (the retirement mechanics), "Code style".
- `docs/CODING_VALUES.md` — the coding standard the tests and the docstrings must match.

### The debt and its history
- `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` —
  the three measured configurations and numbers, the false README sentence, the path not
  taken.
- `docs/tech_debt/active/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` —
  the missing cross-check, the failure modes (wrong root / sign / side), the "next step"
  that D-08/D-09 implement.
- `docs/tech_debt/INDEX.md` rows 26–27 — move to the resolved table in the retiring
  commits; `docs/tech_debt/TEMPLATE.md` for the `Status`/`Resolved in` fields.
- `.planning/milestones/v0.2-phases/10-tooth-tip-chamfer/10-05-PLAN.md` line ~116 and
  `10-05-SUMMARY.md` ~160–170 — where the 35.29/32.28/31.73 µm figures were written down
  (no script; planning-time), the reason D-02 quotes none.
- `.planning/milestones/v0.2-phases/11-body-cutouts/11-08-SUMMARY.md` — the 1e-9 mm³
  agreement as first measured for holes, sharp spokes and honeycomb (the record D-05 makes
  true as an assertion).

### Decisions
- `docs/architecture/decision_log.md` — L03 (cap and warn), L05 (defaults stay put), L08
  (no number is better than a wrong number), L09 (root fillets computed, not filleted),
  L10 (radial root below the base circle, with a warning — the entry L33 part one sits
  beside), L26 (the fixture pins the pre-v0.2 part), L29 (`spline_start` and the
  tip-chamfer flank cap), L30 (lines ~1140–1285; the "pinned for the filleted spoke, which
  has none" clause at ~1268–1269 that L33 part two answers), L32 (the "amends Lxx"
  append-only shape to copy).
- `.planning/phases/13-latency-bar/13-CONTEXT.md` — D-09 (the halt-with-numbers checkpoint
  shape D-06 reuses), D-12 (the amending-entry shape), D-18 (process).

### The code under change
- `src/spur/calc.py` — `Profile` (64–90: `r`, `rb`, `rf`, `r_start`), `profile()`
  (91–99: `rf = r − m·(1.25 − x)`), `root_fillet()` (224–227, the 0.45·gap cap),
  `spline_start()` (230–243), `tip_chamfer_limit()` (258–281, the one existing consumer of
  the above-pitch-circle case), `derive()` (946–1143; the warnings block from 967; the
  tip-chamfer printed-resolution branch 974–993 that D-01 copies).
- `src/spur/model.py` — `_fillet_corner()` (98–130, the `inside=True` branch D-09 must
  disagree with and D-10 perturbs), `_outline()` (133–175; docstring 136–139 is D-13's
  target), `_spoke_sector()` (278–335; `foot()` and the four `_fillet_corner` calls).
- `tests/test_model.py` — `_spoke_bar_area()` (1111–1124, the precedent helper),
  `_assert_the_cutout_is_what_derive_prints()` (1174–1217; the `rel=1e-6` at 1196),
  `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` (1219–1283),
  `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` (1286–~1320), the
  hand-checked `_fillet_corner` case at ~939–958.
- `tests/test_calc.py` — `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`
  (~600–655: one step either side of each limit, full-string warnings, the
  printed-resolution precision edge) and
  `test_a_sub_print_precision_tip_chamfer_request_still_warns` (full-string assert
  rationale).
- `tests/regression/pre_v0_2.json`, `tests/regression/test_pre_v0_2.py` — the standing
  byte-unchanged proof; provenance header pins cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1.
- `README.md` — "Geometry notes" bullets ~220–236 (the root-fillets bullet at ~225–228;
  the undercut bullet's "the UI warns when that applies" shape; the tip-chamfer bullet's
  "measured; decision log L29" citation style).
- `bench/RESULTS.md` "## Tooth-tip chamfer spike (Phase 10, D-05)" (~998–1117) — the
  measured kernel boundary at `ra − spline_start` on the above-pitch-circle configurations
  (context for why the lead-in height matters).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `calc.spline_start(pr, fillet)` and `calc.root_fillet(p)` — the two functions whose
  difference from `pr.r` is the warning's number; already used together in
  `tip_chamfer_limit`.
- `derive()`'s tip-chamfer branch (`if tch < round(p.tip_chamfer, 3)`) — the
  printed-resolution comparison D-01 copies; its comment block explains the rule.
- `tests/test_model.py::_spoke_bar_area` — the closed-form-helper shape (pure math,
  derivation in the docstring, "matching the built solid rather than a pinned literal").
- `_assert_the_cutout_is_what_derive_prints` — the one shared assertion to tighten (D-05);
  both the proof and the tripwire go through it.
- The 10-03 / 11-08 tripwire shape — `monkeypatch.setattr("spur.model.<step>", ...)`
  then `pytest.raises(AssertionError)` around the shared assertion while `derive()` still
  prints the number.
- `tests/test_calc.py`'s parametrized warning tests — `pytest.param({...}, applied,
  warning, id=...)` rows with full-string expected warnings.

### Established Patterns
- Warnings: f-strings, 3 dp or `:g`, fact then cause ("… reduced to X mm to keep it …");
  compared at the printed resolution; tests assert full strings or exact tuples.
- Comments carry the measurement and the date ("Measured 2026-09-29 on the pinned
  kernel…"); a demoted literal keeps its provenance as a comment.
- `calc.py` never imports `cadquery`; the import-boundary contracts in `make verify`
  enforce it. The oracle helper lives in tests and uses `math` only.
- Decision log entries are append-only and "amend" earlier ids by name (L32 ← L18).
- Debt retirement is mechanical and same-commit (CLAUDE.md).

### Integration Points
- `derive()` → `DerivedDimensions.warnings` → `/api/info`, the CLI's output and the UI's
  warnings panel, all unchanged; the new sentence simply appears in the tuple.
- `README.md` "Geometry notes" and `_outline`'s docstring — the two prose sites.
- `docs/architecture/decision_log.md` — L33 appended; `docs/tech_debt/` — two files moved,
  INDEX rows moved.
- `.planning/REQUIREMENTS.md` / `ROADMAP.md` — the D-07 sentence.

</code_context>

<specifics>
## Specific Ideas

- **The closed form behind the warning** (measured 2026-10-02, pinned code): with a
  fillet that needs room, `spline_start = rf + 2·root_fillet(p)` (the mid-tooth cap never
  binds in the field ranges tried), so `height = 2·root_fillet(p) − (r − rf)` and
  `r − rf = (1.25 − x)·m`. Pressure angle enters only through the `0.45·gap` fillet cap
  (D-03's trap). The crossing is `root_fillet(p) = (1.25 − x)·m / 2`. The planner may use
  this to pick rows and to word README (D-12); the tests prove it at seven points.
- **Warning draft (D-02):** "The flank starts with a straight chord reaching 0.563 mm
  above the pitch circle, where it deviates from the involute: the root fillet is larger
  than half the dedendum."
- **README draft (D-12):** "… the flank starts with a short chord onto the involute —
  1.188 mm below the pitch circle on the default gear, and above it when the root fillet
  exceeds half the dedendum, `(1.25 − x)·m / 2`, in which case `warnings` says how far."
- **`_outline` docstring draft (D-13):** "… extended as a short chord onto the involute
  when the fillet needs room (below the pitch circle on the default gear; `calc.derive`
  warns when the chord ends above it, naming the height)."
- **The oracle's geometry (D-09):** sector k spans `th0 = 2πk/n` to `th1 = 2π(k+1)/n`;
  bar sides at perpendicular offset `o = spoke_width/2` from the radial lines through
  `th0` (offset `+o`) and `th1` (offset `−o`); hub circle `rh = hub_d/2`, rim circle
  `rr = rf − rim_wall`; `ρ = spoke_fillet_effective(p)`. Hub corners: fillet centre at
  distance `rh + ρ` from the axis and `ρ` from the bar side, on the sector's side of the
  line; rim corners: distance `rr − ρ` from the axis, `ρ` from the side. Cut-off area per
  corner = area(polygon corner → on_line → centre → on_root) − (fillet sector, angle at
  centre between on_line and on_root) ± (segment of the big circle between on_root and the
  corner; sign by which side of the chord the arc bulges). Sector area = sharp area (the
  sharp row's `π(rr² − rh²) − n·_spoke_bar_area` already proven) − 4 × corner cut-offs; ×
  `face_width`.
- **The tolerance line:** `tests/test_model.py:1196`, `pytest.approx(d_volume, rel=1e-6)`
  → `abs=1e-9` after the per-row measurement (D-05).
- **Halt checkpoint contents (D-06):** per row, the kernel volume delta, the formula
  value, the gap, and the kernel pair — in that order, so the human reads the miss before
  the proposal.

</specifics>

<deferred>
## Deferred Ideas

- **A per-gear chord-to-involute deviation in `derive()`** — rejected for the warning
  (D-02); pure maths, kernel-free, and it would make the warning's "deviates" a number. A
  precision idea for `docs/ideas/` if a profile-shifted flank is ever measured; not debt.
- **A `bench/` sweep of the chord deviation across the field ranges** — the only honest
  way to quote a static µm bound in README or the warning; not needed while neither quotes
  one.
- **The outline change that keeps the lead-in below the pitch circle** — stands in
  `REQUIREMENTS.md` "Future Requirements → Precision"; revisit if the new warning fires on
  gears people actually cut.
- **Refreshing `.planning/codebase/*.md`** — CONCERNS.md carries both debt items
  accurately as of 2026-10-02; the other maps were read for this discussion and found
  sufficient. Process, not product.

</deferred>

---

*Phase: 14-honest-record*
*Context gathered: 2026-10-02*
