# Phase 31: Shaft Maths, Parameters and Designation - Context

**Gathered:** 2026-10-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Pure maths for a DIN 5480 external shaft, with no solid, no route and no page:

- `ShaftParams`, with its field names and defaults frozen and pinned by a test.
- The profile shift derived from the reference diameter, with the range refusal.
- Tip diameter, root diameter and nominal tooth thickness.
- M_Re and D_Re at nominal thickness.
- d_Ff, `null` with a reason until it is proven.
- The designation codec.
- An independent stdlib oracle.

Code goes into the Phase 30 placeholders `src/spur/shaft_params.py`, `src/spur/shaft_calc.py`
and `src/spur/din5480.py` (frozen layout, 30-CONTEXT D-13). `din5480_tables.py` stays a
placeholder until Phase 34.

The phase cannot close without the human's DIN 5480 (2006) copy: formula clauses, `h_fP` and
anchor rows (ROADMAP Phase 31 "Needs the human before it can close").

</domain>

<decisions>
## Implementation Decisions

### Field contract (ShaftParams)
- **D-01:** The reference diameter field is named `reference_d`. It follows the gear's `bore_d`
  and `hub_d` suffix style. The UI title may say "Reference Ø d_B"; the field name is
  `reference_d`.
  - **Reversibility:** one-way from Phase 33. It becomes a URL key when the first shaft link is
    published (L05, L46). Until then a logged decision may change it (30-CONTEXT D-18).
- **D-02:** The tolerance field is one string field named `fit`, holding the same token the
  designation carries (e.g. `8f`).
  - Phase 31 checks its shape only: one or two digits, then one lower-case letter. The planner
    confirms the exact pattern against the copy's fit notation.
  - Whether a fit exists in the tables is checked in Phase 34 (ROADMAP criterion 4).
  - Allowed values may grow later. The name and the default may not change.
  - ISO-style `f8` is refused (REQUIREMENTS Out of Scope).
  - **Reversibility:** one-way from Phase 33. It is a public URL token (research ARCHITECTURE
    F7).
- **D-03:** The shaft reuses the gear's field names `module` and `teeth`. They live on separate
  routes (`/api/shaft/...`, Phase 33) with their own ranges and defaults. Switching part never
  carries values across (research ARCHITECTURE §5).
- **D-04:** The default shaft is **W 25x1.25x18x8f**: `reference_d=25`, `module=1.25`,
  `teeth=18`, `fit="8f"`.
  - Its profile shift is x = +0.45, on the upper edge of the shaft range, and computes to
    0.44999999999999996 in floating point.
  - The range epsilon is therefore exercised by the default itself. A pinned test asserts that
    the default validates and that its x is the range edge.
  - W30x2x14 (x = −0.05) is the lower-edge test case (ROADMAP criterion 1).
- **D-05:** The designation prints in one canonical form, `W 25x1.25x18x8f`:
  - one space after `W`, lower-case `x`, numbers in shortest form (`1.25`, not `1.250`), and `.`
    as the decimal mark;
  - the parser also accepts no space (`W25x…`), an upper-case `X`, and `,` decimals;
  - print followed by parse returns equal parameters (round-trip);
  - an unparseable string is refused, naming the bad token (REQ-designation-codec).

### Copy-gated values
- **D-06:** The anchor rows and clause checks arrive at a plan checkpoint, not now.
  - The plan first builds `ShaftParams`, the formulas, the oracle and the codec.
  - It then stops at a `checkpoint:human-action`. There the human types the anchor rows (with
    part, clause and table) and confirms each formula by clause.
  - Minimum set: 2 basic-dimension rows, 1 form-diameter row, 1 odd-z row if odd-z M_Re is to
    print a number, and ideally W30x2x14.
  - No copy-dependent number ships before that checkpoint (L08). The checkpoint result is
    recorded in the plan summary.
  - The plan does not close the phase on vendor vectors alone.
- **D-07:** `h_fP` is decided by the copy. 0.55·m is the provisional constant.
  - 0.55·m reproduces Hexagon's W120x3x38 d_f = 113.40.
  - It sits in one constant block with an `ASSUMPTION` marker and a clause-citation slot.
  - The root diameter d_f does not count as proven until the human confirms `h_fP` by clause at
    the D-06 checkpoint.
  - `h_fP` is not a user field. A process-dependent field would be new scope and a new frozen
    token.
- **D-08:** The public vendor vectors may be committed as test cross-checks: KISSsoft W70x3x22
  and Hexagon W120x3x38x8f (research FEATURES, PITFALLS).
  - Each carries its public URL and is labelled "vendor cross-check, not the standard".
  - They never count toward the ≥2 anchor rows from the copy.
  - Their purpose is to give the oracle tests real numbers before the checkpoint.
- **D-09:** If the copy contradicts a research formula at the checkpoint (e.g. the 0.55·m shift
  term, or tip = d_B − 0.2·m), the executor follows this order:
  1. It stops and shows the clause against the code.
  2. The fix lands with a new decision-log entry (`Lxx`).
  3. The guard test is seen red against the old constant.
  - A constant is never edited silently, even to match the copy.

### Pin diameter D_Re and M_Re at nominal
- **D-10:** D_Re is computed: the pin whose contact point lies on the shifted reference circle
  m·z + 2xm (research PITFALLS #5; not d_B).
  - It is printed with a note that it is the theoretical pin, not the copy's D_Re.
  - Phase 34 switches to the copy's D_Re where the tables give one, and warns that it changed.
    This changes an output number, not a parameter, so L05 does not apply. The planner states
    this in the Phase 34 handoff.
- **D-11:** D_Re is rounded to a stated gauge step. M_Re is then recomputed, and the contact
  rechecked, for the rounded pin.
  - The printed pin is one that can be bought and measured with, and the printed M_Re is exact
    for that pin.
  - The step is 0.01 mm unless research finds a documented gauge series the copy or common
    practice uses. The planner records the choice and its source.
- **D-12:** The pin-contact guard's lower bound is an internal d_Ff that is never printed.
  - The internal d_Ff comes from the public construction (113.880 against the vendor's 113.91,
    about 0.03 mm apart).
  - The guard adds a stated margin.
  - If contact falls within the margin of the internal d_Ff, or above d_a − margin, M_Re and D_Re
    are `null` with a warning.
  - The printed d_Ff stays `null` with its sentence (REQ-form-diameter-honest) until an anchor row
    proves the construction.
  - The planner sizes the margin from the 0.03 mm disagreement and records why.
- **D-13:** Odd z: the `cos(90°/z)` M_Re formula is built and oracle-tested. It prints `null` with
  a warning until an odd-z anchor row confirms it (REQ-mre-nominal; ROADMAP criterion 3).

### Part widening (WR-03)
- **D-14:** `Part` stays `GearParams` in Phase 31. It widens to `GearParams | ShaftParams` in
  Phase 32, in the same change that makes `model` able to build a shaft.
  - Phase 31 has no solid and no route, so nothing passes a `ShaftParams` to `pool`, `records`
    or `model`.
  - Widening now would force an unreachable shaft branch into the model internals, which
    30-CONTEXT D-10 forbids.
  - Phase 31 corrects the `src/spur/parts.py` docstring. It must name Phase 32 and say the
    widening touches `model._build_checked`, `model._write_export` and `records._gear_fields`,
    not only `parts.py`.
  - Phase 31 also updates the tech-debt item
    `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md`: the docstring
    half is resolved, and the trigger moves to Phase 32. The planner chooses one of two ways:
    1. Split the item: resolve the docstring part, keep a Phase 32 item.
    2. Re-target the trigger.
    Either way, the INDEX row moves in the same commit (AGENTS.md debt rules).

### Claude's Discretion
- The solid-only defaults. Names: `splined_length`, `end_chamfer`, `shank_d`, `shank_length`;
  the planner confirms the names in the gear's naming style. Proposed values for W25:
  - splined length 30 mm;
  - end chamfer 1.0 mm (below the 1.25 mm tooth height at h_fP 0.55);
  - shank Ø 25 mm (= `reference_d`, a shoulder above the 24.75 mm tip);
  - shank length 20 mm.

  The planner records them for the human's review in the plan summary. Phase 32's sweep may
  revise them by logged decision until Phase 33 (D-18).

  Note: the discussion floated a shank Ø of 22.25 mm, equal to the root, as an example.
  25 mm is proposed instead. The research calls a shank at the nominal diameter the
  ordinary design, and it measured plain `Shape.fuse` valid for a shank above, at or below
  the tip and below the root (`.planning/research/STACK.md:88-96`). The human reviews it.
- The result type: a typed shaft dimensions model with `null` plus a warning per value. It
  mirrors `calc.DerivedDimensions` (Phase 4's typed derived-dimensions contract) and stays
  inside the shaft modules.
- Where the range refusal lives. It sits inside the `ShaftParams` validator, so the API can serve
  it as a `422` in Phase 33. The planner decides how the validator reaches `shaft_calc`, e.g. by
  local import as `params` does.
- The oracle's file layout, following `tests/trochoid_oracle.py`:
  - not collected;
  - imports nothing from `spur`;
  - takes plain floats.
- The exact `fit` regex, within D-02.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 31: Shaft Maths, Parameters and Designation": goal, five
  success criteria, boundaries, the "needs the human" clause.
- `.planning/REQUIREMENTS.md`:
  - "Rules every requirement lives by";
  - REQ-shaft-params, REQ-profile-shift-from-dB, REQ-shaft-basic-dims,
    REQ-form-diameter-honest, REQ-mre-nominal, REQ-designation-codec, REQ-gate-cost-recorded;
  - Out of Scope (`f8` aliases, interpolation, snapping).

### Research (authoritative resolutions in SUMMARY)
- `.planning/research/SUMMARY.md`: entry point. Its resolutions override the single files.
- `.planning/research/PITFALLS.md`:
  - formula table (profile shift, tip, root);
  - pitfall #1 (shift formula, epsilon);
  - pitfall #5 (M_Re contact at m·z + 2xm, odd z).
- `.planning/research/FEATURES.md`: Hexagon W120x3x38x8f and KISSsoft W70x3x22 vectors (D-08),
  the D_Re and tolerance unknowns, designation codec notes.
- `.planning/research/ARCHITECTURE.md`:
  - §3 module table;
  - §4.1 ShaftParams field set;
  - F7 (tolerance field as URL token);
  - the designation parse / `resolve_shaft` sketch.
- `.planning/research/STACK.md`: stdlib only, no scipy; the `_involute_angle` copy precedent.

### Locked decisions
- `docs/architecture/decision_log.md`:
  - L46 (gear and spline generator; the shaft's frozen link contract);
  - L05 (defaults absolute, frozen);
  - L03 (cap or refuse, never guess);
  - L08 (no number is better than a wrong number);
  - L44 (a link value is sent and refused by a 422).
- `.planning/phases/30-scope-seam-and-gear-safety-guard/30-CONTEXT.md`:
  - D-08 (Part alias);
  - D-10 (no unreachable dispatch);
  - D-12/D-13 (placeholders, frozen module names);
  - D-14 (contracts C1–C5);
  - D-18 (names changeable by logged decision until Phase 33).

### Tech debt touched
- `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md`: WR-03, handled
  per D-14.

### Coding standard
- `docs/CODING_VALUES.md`: read before writing code (AGENTS.md).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `params._f`, `params.when`, `params._extra` (`src/spur/params.py:18-80`): field metadata
  builders. The research recommends importing them into `shaft_params` with zero edits to
  `params.py` (the gear schema must stay byte-equal to v0.6).
- `calc._involute_angle` (`src/spur/calc.py:1327`) and `calc.inv` (`:117`): copy, never import
  (contract C5).
- `calc.DerivedDimensions` (`src/spur/calc.py:927`): the shape the shaft result type mirrors.
- `tests/trochoid_oracle.py`: the independent-oracle precedent (not collected, no `spur`
  import, plain floats).

### Established Patterns
- `GearParams` is a frozen pydantic model, validated once at its boundary; `model_config` uses
  `frozen=True`. `ShaftParams` must be frozen and hashable. The tests for that were deferred
  from Phase 30 (30-CONTEXT Deferred).
- A value that cannot be computed honestly is a warning and no number (calc.py pattern, L08).
- Every guard test is seen red once and the red recorded under the phase's `investigation/` and
  `bench/RESULTS.md` (Phase 30 pattern).
- `make gear.unchanged` runs inside `make verify`. Phase 31 must leave it green.
  `calc.py`, `params.py`, `tests/regression/`, `ci.yml` and `requirements.txt` are not edited
  (30-CONTEXT D-11).

### Integration Points
- The `src/spur/shaft_params.py`, `shaft_calc.py` and `din5480.py` placeholders, already under
  contracts C1–C5 (`pyproject.toml`).
- `tests/test_seam.py` regex belts and the contract-existence guard already cover these module
  names.
- `src/spur/parts.py`: docstring correction only (D-14).

</code_context>

<specifics>
## Specific Ideas

- The human again picked the recommended option on every question: the stricter guard, honest
  `null` over a plausible number, and work deferred to the phase that can actually use it.
- The default sitting on the range edge (x = +0.45) is intentional: it keeps the epsilon under
  test on every default build.

</specifics>

<deferred>
## Deferred Ideas

- `Part` widening and the model and records internals: Phase 32 (D-14).
- The copy's D_Re replacing the computed pin: Phase 34 (D-10).
- Whether a `fit` token exists in the tables: Phase 34 (D-02).

</deferred>

---

*Phase: 31-shaft-maths-parameters-and-designation*
*Context gathered: 2026-10-24*
