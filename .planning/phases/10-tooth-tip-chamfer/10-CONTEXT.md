# Phase 10: Tooth-Tip Chamfer - Context

**Gathered:** 2026-09-28
**Status:** Ready for planning

<domain>
## Phase Boundary

The one v0.2 cut that touches the teeth, and the one in L09's cost family: an end-face
edge break on the tooth-tip arcs, cut with the kernel's chamfer operator and measured
before it is designed.

1. **The field.** `tip_chamfer: float = 0` (mm, `0 = off`, `ge` 0, step 0.05) joins
   `GearParams`' Teeth group, declared after `root_fillet` (D-10). The CLI flag
   `--tip-chamfer`, the `/api/schema` entry, the form field and the shareable-URL
   round-trip fall out of the model (L02). Nothing else in `GearParams` changes.
2. **The cut.** When `tip_chamfer > 0`, `_build` appends one last step after
   `_cut_keyway`: `solid.chamfer(c, None, tip_edges)` — `bore_chamfer`'s call and
   meaning, symmetric 45°, `c` off the end face and `c` off the tip — on the `2 × teeth`
   tip-arc edges (one per tooth per end face), selected by position (D-03, D-13). Flanks,
   root fillets, bore, recess and keyway edges are never selected; the outside diameter is
   unchanged (SC1). The reading is the one decided 2026-09-25: a 3D edge operation on the
   built solid, **not** a 2D corner in `_outline()` and **not** tip relief (REQUIREMENTS
   "Out of Scope"; ROADMAP SC2).
3. **The cap.** `c` is trimmed, never refused (L03, REQ-tip-chamfer-capped), to
   `min(0.45 × face_width, ra − r)` — the tip land between the two chamfers keeps 10 % of
   the face width, and the chamfer's footprint on the end face stays above the pitch
   circle (D-01, D-02) — lowered further only to a kernel boundary the plan measures
   (D-04). The applied value is a new `DerivedDimensions` field and, when it differs from
   the request, one warning sentence (D-08, D-09).
4. **The measurement.** Plan 10-01 is a measurement-only spike (D-05): the chamfer
   operator at 19/40/200 teeth, module 1.75 and 10, `c` at the analytic cap, on a probe
   path before any field exists — build, fine-STL and STEP times in `bench/RESULTS.md`,
   the radial kernel boundary probed. Then a 9-row sweep at 200 teeth through
   `make bench.build SWEEP=bench/sweeps/tip_chamfer.json` (D-06). A row over
   `SPUR_BUILD_TIMEOUT=30s` halts for a human decision with the number; the pre-agreed
   first offer is a lower `le` on the field (D-07). The cost is never hidden (SC4).
5. **The proof.** The tip selector gets a column on every existing row of the selector
   matrix plus a 200-tooth and a module-0.2 row (D-13); a built-solid test proves the
   chamfer present and everything else untouched by topology and bounding box (D-12); a
   no-op tripwire shows that proof going red, and the empty-selection guard is a
   `BuildError` (D-14). The pre-v0.2 fixture stays byte-unchanged and the replay requires
   the new field null (D-15, SC5).
6. **The record.** L29 in `docs/architecture/decision_log.md` with the cap rule, the
   measured boundary and the heaviest row's time (D-16, SC2). Help text names the purpose
   and no size; the 0.1–0.2 × module figure appears nowhere (D-11, SC2).

**Out of this phase:** the Phase 11 cutouts and their composition with the chamfer
(Phase 12's matrix); a second chamfer field or angle; chamfering the flank end-face edges;
any sizing rule; the analytic 2D chamfer (see Deferred).

</domain>

<decisions>
## Implementation Decisions

### The cap — what "the tip land allows" means
- **D-01:** **Axial cap `c ≤ 0.45 × face_width`.** Both end faces are chamfered, so the
  tip land between them is `face_width − 2c`; the 0.45 rule is `root_fillet`'s
  (`0.45 × gap`) and `recess_fillet`'s (`0.45 × width`, `0.45 × depth`) — one family of
  caps, 10 % of the dimension the cut eats always remains. On a 1 mm face the largest
  chamfer is 0.45 mm; on the 7.5 mm default, 3.375 mm (so D-02 bites first there).
  Rejected: `(face_width − MIN_TIP_FDM) / 2` (a second constant in the rule; a 1 mm face
  keeps only 0.3 mm chamfers); `c < face_width / 2` (chamfers meeting at a ridge — a tip
  land of zero contradicts the requirement's wording).
  — **Reversibility:** costly — a link that sets `tip_chamfer` above the cap gets a
  different part and a different warning if the rule changes later (L05 protects only
  links that omit the field).
- **D-02:** **Radial cap `c ≤ ra − r`** — the addendum, `m (1 + x)`: the chamfer's
  footprint on the end face reaches inward from the tip circle to about `ra − c` and
  stays above the pitch circle, so the working flank is untouched at the faces — the
  honest reading of SC1's "flanks untouched". Analytic, in `calc.py`, no kernel import.
  1.75 mm on the default gear and on every module-1.75 gear; 0.2 mm at module 0.2; 10 mm
  at module 10. Rejected: kernel-measured only (the cap would carry no geometric meaning
  a user can reason about, and L27 saw a kernel bound move between 19 and 40 teeth); a
  tip-arc bound `c ≤ tip thickness` (the arc length does not bound an end-face chamfer —
  a proxy that caps chamfers the kernel builds).
  — **Reversibility:** costly — same reason as D-01.
- **D-03:** **Symmetric 45°, one field:** `solid.chamfer(c, None, tip_edges)` —
  `bore_chamfer`'s exact call and meaning. One number, one meaning; D-01 and D-02 read the
  same `c`. Rejected: a second length or an angle (a new capability).
- **D-04:** **The kernel is probed inside the analytic caps, and the cap is lowered to
  the measured boundary if it sits inside** (08 D-03's method): the spike (D-05) drives
  `c` toward `min(0.45 × face_width, ra − r)` at small and large tooth counts and at
  module 0.2, 1.75 and 10; if `Mixin3D.chamfer()` fails or yields an invalid solid inside
  the bound, the cap becomes the measured boundary one step inside, the measurement is
  written next to the rule, and it is tested one step either side. Always a cap, never a
  422 (REQ-tip-chamfer-capped). If the boundary moves with tooth count or module such
  that no single rule keeps every buildable chamfer buildable, the planner surfaces that
  as a checkpoint rather than choosing. Rejected: keeping the analytic caps and letting
  a kernel failure inside them reach `_build_checked`'s catch-all ("try smaller fillets
  or chamfers" → 422 — a refusal for a trimmable dimension, against L03).

### The cost — spike, sweep, and the over-budget rule
- **D-05:** **Plan 10-01 measures only** (ROADMAP's research flag: "the plan opens with
  a measured spike of its cost before the cap is designed"). On a probe path with no
  field yet: `Mixin3D.chamfer()` on the `2 × teeth` tip-arc edges at 19, 40 and 200
  teeth, module 1.75 and 10 (and 0.2 for D-04's boundary), `c` at the analytic cap and
  at 0.4; build, fine-STL and STEP wall time per configuration; D-04's radial boundary.
  Numbers into `bench/RESULTS.md` before the field, cap, selector and proof plans are
  written — they are planned with the numbers in hand. Rejected: the spike as the first
  task of the field plan (a halt mid-plan leaves half a feature).
- **D-06:** **A 9-row sweep at 200 teeth, every row recorded, the worst row named
  "heaviest":** 08 D-11's shape — `module ∈ {1.75, 10}` × `tip_chamfer ∈ {0.4, the
  cap's maximum}` × `recess_sides ∈ {both, none}`, default bore — 8 rows, **plus one row
  at module 0.2** (the finest tips, the cap biting hardest, the kernel's hard case). The
  planner fixes the exact rows. Per row: build wall time (solid cache cleared between
  rows), fine-STL and STEP export time. A new sweep file (e.g.
  `bench/sweeps/tip_chamfer.json`) run by the unchanged `bench/build_time.py` behind
  `make bench.build SWEEP=…` (08 D-12); a new `bench/RESULTS.md` section in the Phase
  8/9 shape (host-state header with the load-average caveat, the table, the named
  heaviest row). Every row must build inside `SPUR_BUILD_TIMEOUT=30s`. Rejected: the 8
  rows alone (assumes the fine-module case is not the heavy one).
- **D-07:** **A row over budget halts for a human decision with the number, never a
  silent narrowing (08 D-11); the checkpoint offers lowering `tip_chamfer`'s `le`
  first.** A schema-visible maximum is the same on every machine and every tooth count —
  a chamfer size never depends on how many teeth the gear has (L05's spirit) — and the
  number is published in `bench/RESULTS.md` and L29 (SC4). The second option at the
  checkpoint is a teeth-dependent analytic cap from a measured per-edge cost (the
  honeycomb's shape), warned per request. Rejected as the first offer: that cap (a
  per-host measurement deciding a dimension); pre-deciding either without the number;
  a halt with no pre-agreed direction (the plan would stall on an open design).

### Numbers, warning, form, help text
- **D-08:** **One new `DerivedDimensions` field**, `float | None`: the chamfer actually
  cut after the cap (name the planner's, on the order of `tip_chamfer_effective`),
  `null` when `tip_chamfer == 0`, rounded to 3 dp at construction (Phase 4 D-10),
  `unit: mm` — mirrors `root_fillet` and `recess_fillet`, which report applied values.
  The 23 existing fields keep their names, types and values; the replay requires the new
  field null on every fixture record (08's additive rule); `disallow_any_explicit` stays
  on with no suppressions (L21). A `DIMS` row in `static/app.js` and a README row land
  this phase (08 D-06/D-10). Rejected: also reporting the remaining tip land
  (`face_width − 2c` — derivable, a second row); warning only (the fit number would
  appear nowhere — 08 D-05's rule).
  — **Reversibility:** costly — a published `/api/info` field under L21's typed contract.
- **D-09:** **One warning sentence in the existing "reduced to X mm to …" family**,
  naming the applied value and the limit that bound it — the tip land (D-01), the pitch
  circle (D-02) or the measured boundary (D-04). When two caps bite, the smaller wins and
  the sentence names that limit. Exact wording the planner's (L15: messages are the
  product). Rejected: one sentence per limit that applied.
- **D-10:** **`tip_chamfer` lives in the Teeth group, declared after `root_fillet`**
  (field order is form order and CLI order) — it is tooth geometry, beside the other
  tooth-edge treatment; 08 D-07's reading of REQ-three-interfaces-extended's "in its own
  group" as "each feature's fields grouped". Title on the order of "Tip chamfer", unit
  mm, step 0.05, `ge` 0; `le` is Claude's discretion (see below). Rejected: the Body
  group beside `face_width` (the dimension it eats, but not what it is); a one-field
  "Tip" group (08 D-07's reason).
- **D-11:** **Help text names the purpose and no size:** on the order of "Chamfer on the
  tooth-tip edges at both faces — an edge break for handling and printing. 0 = none."
  No `0.1–0.2 × module`, no standard, no "typical" value anywhere in help, README or
  docs (SC2; research SUMMARY Known Conflict #2: the figure has no source). README: a
  feature bullet, a parameter row carrying the same sentence, the derived-field row;
  an example that the tests run is the planner's and, as a post-v0.2 set, stays out of
  the regression corpus (07 D-05).

### Proof
- **D-12:** **SC1 is proven on the built solid by topology and bounding box** (09
  D-07's shape, no new kernel reads): face count = the unchamfered solid's plus one
  chamfer face per tip-arc edge (expected `+2 × teeth` — the exact face and edge deltas
  are **measured on the pinned kernel in the spike and pinned**, not derived: a chamfer
  terminating at unchamfered flank vertices may add more edges than faces); volume
  strictly smaller; `BoundingBox()` x/y extents and `derive().tip_d` unchanged within
  `TOL` (the outside diameter); the bore-rim and groove-floor selector counts unchanged
  on the same configuration (bore, recess and keyway untouched). Rejected: reading each
  chamfer face back as a datum test (09 D-14's shape — the applied `c` is the cap
  function's own output, tested in `calc.py`).
- **D-13:** **The tip selector is position-based, guarded, runs last, and gets a
  column on every matrix row.** A new selector (name the planner's, e.g. `_tip_edges`)
  picks the tip-arc edges on the two end faces by radius `ra` (criterion detail below);
  it runs only when `tip_chamfer > 0` and raises `BuildError` on an empty selection with
  a message in `_bore_rim_edges`'s shape — a modelling defect, never an answer (07
  D-15). The chamfer step is appended **last** in `_build()`, after `_cut_keyway`: the
  tip band is farthest from every other cut and the selector may assume the final
  outline (research ARCHITECTURE.md "Tip chamfer last"). Matrix
  (`test_each_edge_selector_picks_exactly_its_own_edges`): a tip `Counter` column on
  **every existing row** (round, D-flat, hex, keyway × recess settings), expecting
  `2 × teeth` tip edges, plus a 200-tooth row and a module-0.2 row — the selector ignores
  every other end-face feature (research PITFALLS.md Pitfall 4). Runtime guard non-empty
  only; tests exact count (07 D-16). Rejected: one row per bore shape at defaults.
- **D-14:** **Tripwire plus guard.** One test patches the tip step to a no-op (as the
  matrix patches `_cut_keyway`) and asserts D-12's proof fails — the proof demonstrably
  catches a silently vanished chamfer (Phase 7's tripwire precedent). One test asserts
  that an empty tip selection while `tip_chamfer > 0` is a `BuildError` naming the
  defect, routed 422 on the API and exit 2 on the CLI. Rejected: the guard test alone
  (trusts the face-count assertion without demonstrating it).

### Contract and process (carried forward; recorded so the plan carries them)
- **D-15:** **`tip_chamfer` defaults to 0 = off; the pre-v0.2 fixture is byte-unchanged;
  the replay requires the new derived field null on every record** (L26, 08's rule,
  SC5). `derive()` and `build()` for a chamfer-free gear compute identical floats in
  identical order — the cap function returns 0 and the tip step is a no-op when
  `tip_chamfer == 0`; no existing float path changes.
- **D-16:** **L29 is appended** to `docs/architecture/decision_log.md` (append-only, 0
  deleted lines) in L27/L28's shape: the field, the cap rule (D-01/D-02 and D-04's
  measured boundary), the build order, the derived field, the heaviest sweep row's time,
  and — if D-07 fired — the lowered `le` with its number (SC2).
- **D-17:** **Process.** The phase runs on **`gsd/phase-10-tooth-tip-chamfer`**, cut
  this session from `origin/main` `277a98f` (PR #10's squash), and lands via
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR. Commits are plain
  `git commit` with explicitly staged files, never `git add -A`: the pre-commit hook runs
  `make verify` (~78 s warm at 396 tests) and the gsd SDK commit wrapper kills it at 30 s
  (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`);
  run `make verify` once at session start. Any ROADMAP/REQUIREMENTS sentence a decision
  supersedes is amended through the edit-phase tooling with one human confirmation (09
  D-20) — none is known to need it: SC3 (capped and warned), SC4 (cap lowered, number
  published), REQ-tip-chamfer ("selected by position") all match D-01…D-07 as written.

### Claude's Discretion
- **Names:** the field title (D-10), the derived field (D-08), the selector and the
  chamfer step in `model.py` (D-13), the cap function in `calc.py` (a sibling of
  `root_fillet(p)` / `recess_fillet(p, rf)` returning the applied value), the sweep file
  and the RESULTS.md section title.
- **`tip_chamfer`'s `le`:** recommend **3, like `bore_chamfer`** — one chamfer family, one
  bound; D-01/D-02 bite long before 3 mm on every default-size gear; D-07 may lower it
  from the measured number. A smaller `le` chosen by inspection would be a guess.
- **The selector's criterion:** `_groove_floor_edges`'s shape (`geomType() == "CIRCLE"`,
  `radius()` within `TOL` of `ra`, start point on an end face) versus `_bore_rim_edges`'s
  pure radial band. The planner verifies on the pinned kernel first that the extruded tip
  arc's end-face edge is a `CIRCLE` of radius `ra` (the outline builds it with
  `makeThreePointArc`; nothing splits it), and records the count per face.
- **The spike's probe path (D-05):** a script under `bench/` or a throwaway; only the
  numbers are the deliverable. The probe must include the analytic-cap maximum at each
  (teeth, module) pair, and the D-04 boundary search should follow 09-03's bisection
  method with its step count recorded.
- **Export time and the halt (D-07):** the halt fires on build time against
  `SPUR_BUILD_TIMEOUT`; fine-STL and STEP times are recorded per row (08 D-11) for Phase
  12's REQ-measured-build-time, not gated here.
- **Warning and help sentences (D-09, D-11), the README example.**
- **Recess interaction:** the recess sits inside `rf`, the chamfer above `r`; no
  interaction is expected and D-06's recess rows show it. No `tol=` fuzzy boolean —
  the chamfer is an edge operation; the planner confirms rather than adding one.
- **The existing "Tip is only X mm wide" FDM warning** reports the arc at `ra`
  mid-face and is unchanged by an end-face chamfer; no wording change.
- **Sweep-row exactness (D-06):** which `bore_d`/`bore_chamfer` the "default bore" rows
  carry, and whether the module-0.2 row keeps its recess (at module 0.2 and 200 teeth
  `rf` is ~19.7 mm, so the default recess fits) — the planner decides and records.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` — REQ-tip-chamfer, REQ-tip-chamfer-capped (this phase);
  REQ-three-interfaces-extended, REQ-measured-build-time (Phase 12's bar this phase
  feeds); REQ-derived-dimensions-additive, REQ-edge-selection-proven,
  REQ-defaults-off-regression (standing contracts); "Out of Scope" rows for tip relief
  and the 2D corner chamfer.
- `.planning/ROADMAP.md` "### Phase 10: Tooth-Tip Chamfer" — goal, SC1–SC5, the research
  flag that makes 10-01 a spike.
- `.planning/PROJECT.md` — v0.2 goal and rules (defaults off, measured build time per
  cut, `DerivedDimensions` additive); Key Decisions L01–L28.

### Decisions
- `docs/architecture/decision_log.md` — L03 (cap vs refuse), L05 (defaults), L08 (no
  plausible numbers), **L09** (root fillets computed, not filleted — the cost family this
  chamfer sits in), L15 (messages are the product), L21 (typed contract), L26 (fixture;
  selector guard), L27/L28 (the entry shape L29 follows, the sweep, the measured-bound
  method). Append-only; L29 is this phase's.
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-CONTEXT.md`
  — D-15/D-16 (selector guard contract, exact-count tests), D-03/D-05 (fixture policy,
  corpus sources), D-19/D-20 (process).
- `.planning/phases/08-hex-bore/08-CONTEXT.md` — D-03 (measure the kernel boundary, cap
  one step inside, test either side), D-05/D-06 (fit number in the response; DIMS rows
  this phase), D-07 ("in its own group" reading), D-10 (README), D-11/D-12 (the sweep
  and `make bench.build`).
- `.planning/phases/09-keyway-bore/09-CONTEXT.md` — D-06/D-07 (build order and the
  built-solid proof shape), D-15 (derived-field shape), D-18…D-20 (process); its
  `<specifics>` for the kernel's chamfer behaviour on end-face edges.

### Research (v0.2 kickoff)
- `.planning/research/SUMMARY.md` — Known Conflict #1 (the two chamfer readings; the
  end-face reading was chosen 2026-09-25) and #2 (the sizing figure is unsourced).
- `.planning/research/PITFALLS.md` — Pitfall 3 (the chamfer operator's L09-family cost —
  the risk 10-01 measures; its analytic-outline remedy is **rejected** by the locked
  reading), Pitfall 4 (position selectors on changed topology — D-13's matrix rows).
- `.planning/research/STACK.md` §4 — `Mixin3D.chamfer(length, length2, edgeList)`
  verified on the installed `cadquery==2.8.0`.
- `.planning/research/ARCHITECTURE.md` — "Tip chamfer last" (build order), Q4 (the
  applied-value derived field and the cap-vs-refuse split).
- `.planning/research/FEATURES.md` "Standards Cited — Tooth-Tip Chamfer" — no numeric
  standard exists; edge break ≠ tip relief.

### Measurement and process
- `bench/RESULTS.md` — the Phase 8 and Phase 9 sections (host-state header, table,
  named heaviest row) that D-06's section copies; the Phase 7 fixture-cost section.
- `bench/build_time.py`, `bench/sweeps/hex_bore.json`, `bench/sweeps/keyway_bore.json`,
  `Makefile` `bench.build` (`SWEEP=`) — the sweep runner and file shape, reused
  unchanged.
- `docs/HOW_TO_DEVELOP.md` §2/§4 — the phase branch is cut before discuss-phase and
  reused by execute-phase; `main` only via `make pr.land`.
- `docs/CODING_VALUES.md`, `CLAUDE.md` — comments carry the measurement; `calc.py` never
  imports the kernel; one validation at the `GearParams` boundary.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — why
  commits are plain `git commit`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/spur/model.py` `_bore_rim_edges(solid, p)` (277–310) and
  `_groove_floor_edges(solid, radii, floor_z)` (254–275): the two position selectors with
  the D-15 guard and its message shape — the tip selector is a third of the family.
- `src/spur/model.py` `_cut_bore` (196–221): `solid.chamfer(p.bore_chamfer, None,
  _bore_rim_edges(solid, p))  # type: ignore[attr-defined]` — the exact call D-03 reuses,
  with the comment explaining the ignore (`Mixin3D`).
- `src/spur/model.py` `_build` (312–322): four steps, "one decision per step"; the tip
  step is a single append after `_cut_keyway`; `_build_checked` is the catch-all D-04's
  cap must keep the chamfer away from.
- `src/spur/model.py` `_outline` (114–166): the tip arc is
  `makeThreePointArc(left[-1], _polar(pr.ra, c), right[0])` — one arc per tooth at
  radius `ra`, the edge the selector picks after extrusion.
- `src/spur/calc.py` `Profile` (`ra`, `r`, `rf`), `_tooth()` (tip arc width),
  `root_fillet(p)` / `recess_fillet(p, rf)` (the cap-function shape: requested value,
  capped, rounded to 3 dp, returned as the applied value), `derive()`'s warning list
  (471–513: the "reduced to … to fit …" sentences D-09 joins), `DerivedDimensions`
  (368–447: `float | None` fields with `description` and `unit`).
- `src/spur/params.py` `_f(default, ge, le, title=, group=, unit=, step=, help=)` and
  the Teeth group (32–48) — `root_fillet` at line 46 is the insertion point.
- `tests/test_model.py` `test_each_edge_selector_picks_exactly_its_own_edges` (122–):
  the matrix — `monkeypatch` of a cut step, `_build_checked` bypassing the cache, a
  `Counter` per selector; `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp`
  (323–): the built-solid proof shape D-12 copies; `test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root`
  (465–): the measured-boundary test shape D-04 copies.
- `tests/test_calc.py` (390–, 462–): refusal/warning tests naming fields and quoting the
  measured gap — the cap tests' shape.
- `tests/regression/pre_v0_2.json` + its replay: byte-unchanged; new derived fields
  required null (D-15).
- `bench/build_time.py` + `bench/sweeps/*.json` + `make bench.build SWEEP=` — D-06 adds
  a file, not code. `bench/RESULTS.md` Phase 8/9 sections — the section shape.
- `src/spur/static/app.js` `DIMS` (13–) and the schema-driven group rendering (44–84) —
  a `DIMS` row is the only UI change; the field renders itself from `group: "Teeth"`.
- `README.md` parameter table (~150–165) and derived-numbers prose (~205–212).

### Established Patterns
- A cap lives in one `calc.py` function that returns the applied value; `derive()` warns
  when it differs from the request; `model.py` calls the same function — the part and the
  number cannot disagree (L08).
- A selector runs only while its feature is on, is position-based, and raises
  `BuildError` naming the defect when empty (L26); tests pin exact counts per shape.
- A kernel boundary is measured (bisection, step count recorded), the rule sits one step
  inside, the comment carries the numbers and the date, tests sit one step either side
  (08 D-03, 09 D-12).
- New numbers: measured on the pinned kernel via a committed script and `make` target,
  recorded in `bench/RESULTS.md` with host state, cited in the `Lxx` entry.
- `calc.py` never imports `cadquery` (import-linter); vendor objects stop at `model.py`.

### Integration Points
- `src/spur/params.py` — `tip_chamfer` in the Teeth group after `root_fillet`.
- `src/spur/calc.py` — the cap function; a `derive()` warning; one `DerivedDimensions`
  field.
- `src/spur/model.py` — the tip selector; the chamfer step appended to `_build`.
- `tests/test_model.py` — matrix column + two rows; built-solid proof; tripwire; guard.
  `tests/test_calc.py` — cap at each limit, one step either side of the measured
  boundary; the warning text. `tests/test_api.py` / `tests/test_cli.py` — the DIMS-subset
  and flag parity tests pick the field up; a 422/exit-2 routing test for the guard.
- `bench/sweeps/tip_chamfer.json`, `bench/RESULTS.md` — the sweep and its section.
- `src/spur/static/app.js` `DIMS`, `README.md` — one row each.
- `docs/architecture/decision_log.md` — L29.

</code_context>

<specifics>
## Specific Ideas

Arithmetic on the parameter model only — **no kernel probe was run this session**; the
spike (D-05) measures everything below that is a cost or a boundary.

- **Default gear** (19 teeth, m 1.75, α 25°, x 0, face 7.5): `r` 16.625, `ra` 18.375,
  `rf` 14.4375 (09-CONTEXT). Addendum `ra − r` = 1.75 → D-02 caps at **1.75 mm**; D-01
  allows 3.375 → the pitch-circle rule bites first on every module-1.75 gear with a face
  over 3.9 mm. 38 tip-arc edges.
- **Face width 1 mm** (the field's floor): D-01 caps at 0.45 mm regardless of module.
- **Module 0.2, 200 teeth** (D-06's ninth row): addendum 0.2 → cap **0.2 mm** (four
  steps of 0.05); `ra` 20.2, `rf` 19.75, tip arc ≈ 0.12 mm wide (`2·ra·half_angle(ra)`
  with `psi_p` at the default backlash) — the finest tips the model allows, and the
  `MIN_TIP_FDM` warning already fires there.
- **Module 10, 200 teeth**: addendum 10 → D-01 bites for any face under 22.2 mm; at the
  default 7.5 mm face the cap is 3.375 mm, so `le` 3 is the binding limit.
- **200 teeth**: 400 tip-arc edges in one `chamfer()` call. Baselines the spike compares
  against: Phase 8's heaviest row 5.08 s and Phase 9's 4.85 s of 30 s (200 teeth, recess
  both, chamfer 0.4), both with a two-edge or twelve-edge bore chamfer. L09 measured
  OCCT's fillet operator at ~50× the analytic outline on the same many-toothed shape —
  the reason the spike comes first.
- **Kernel behaviour on end-face edges already recorded** (09-CONTEXT `<specifics>`): a
  one-shot chamfer on mixed arc + line edge sets failed (`BRep_API: command not done`)
  where arcs alone were valid; edges of one type on one face chamfer cleanly. The tip
  set is arcs only, all at one radius — the benign case, to be confirmed at 200 teeth.
- Expected proof numbers (D-12) are **to be measured**: face delta `+2 × teeth` is the
  expectation; the edge delta depends on how the kernel terminates each chamfer at the
  two unchamfered flank vertices.

</specifics>

<deferred>
## Deferred Ideas

- **Analytic 2D tip-corner chamfer in `_outline()`** (research PITFALLS.md Pitfall 3) —
  rejected 2026-09-25 as the reading of "tip chamfer" (REQUIREMENTS "Out of Scope": it
  changes the meshing profile). Recorded so it is not re-derived. If D-07's checkpoint
  finds no `le` at which 200 teeth fit the budget, it is the fallback to **surface** to
  the human as a superseding decision, never to build under the chamfer's name.
- **Chamfering the flank end-face edges too** (a full end-face deburr) — a different
  cut, not asked for; SC1 says flanks untouched.
- **A second chamfer length or an angle field** — D-03; one field, symmetric.
- **A teeth-dependent chamfer cap from the measured per-edge cost** — D-07's second
  option, taken only at the over-budget checkpoint.
- **Reporting the remaining tip land `face_width − 2c`** — D-08 rejected it as a
  derivable second row; revisit if a user asks for the number.

No scope creep surfaced during discussion — nothing else deferred.

</deferred>

---

*Phase: 10-tooth-tip-chamfer*
*Context gathered: 2026-09-28*
