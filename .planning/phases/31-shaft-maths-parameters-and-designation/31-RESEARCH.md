# Phase 31: Shaft Maths, Parameters and Designation - Research

**Researched:** 2026-10-24
**Domain:** pure-Python DIN 5480 external-shaft maths (involute splines), a frozen Pydantic v2 parameter model, a designation codec, and an independent stdlib oracle
**Confidence:** MEDIUM. The repo-integration findings are HIGH (files read, lints and Pydantic behaviour run this session). The DIN 5480 formulas are reproduced to 1e-4 mm or better against two vendor reports and a geometric oracle, but every one stays `[ASSUMED]` until the human's copy confirms it by clause (L08, D-06). Nothing in this file came from the standard itself.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)
- `Part` widening and the model and records internals: Phase 32 (D-14).
- The copy's D_Re replacing the computed pin: Phase 34 (D-10).
- Whether a `fit` token exists in the tables: Phase 34 (D-02).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-shaft-params | `ShaftParams` validated once at its boundary; field names and defaults frozen, tolerance field included | Pydantic v2 frozen model reusing `params._f/_extra`; `str` field with `pattern`; pinned-defaults test shape; list of eight field names (Architecture Patterns, Pattern 1) |
| REQ-profile-shift-from-dB | shift from d_B, m, z by the copy's formula; out-of-range is a 422 naming the range; epsilon accepts the edge | `xm = (d_B - z m)/2 - 0.55 m` reproduced on 5 shafts; float-order trap and the epsilon cases that actually need it (Pitfalls 1 and 2); refusal shape copied from `GearParams._feasible` |
| REQ-shaft-basic-dims | d_B, tip, root, nominal tooth thickness, each proved against the oracle and two copy rows | closed forms plus numbers for five shafts; two different `0.55` constants; vendor rows at both h_fP values; checkpoint row table |
| REQ-form-diameter-honest | d_Ff `null` with a sentence unless the construction is reproduced on a copy row | public construction reproduces KISSsoft 63.718 exactly and Hexagon to 0.03 mm; both vendors print the standard's value as a limit, so `null` is the expected outcome (Pitfall 8) |
| REQ-mre-nominal | M_Re and D_Re at nominal for even and odd z; contact guard; odd z `null` until anchored | closed-form theoretical pin, copied bisection for inv, geometric oracle agreeing to 2.3e-13 mm on 252 cases; guard margin sizing; why the guard cannot fire at the theoretical pin |
| REQ-designation-codec | print and parse back to the same parameters; `.`/`,` decimals; unparseable string names the bad token | grammar, tokenising strategy, `repr`-based number printing, ASCII-only regex, length bound |
</phase_requirements>

## Summary

All Phase 31 maths is closed-form except one inversion (the involute function), and it can be proved without the copy to the extent a third-party vendor report allows. Re-derived and run this session: `xm = (d_B - z*m)/2 - 0.55*m`, `d_a = d_B - 0.2*m`, `d_f = m*z + 2*xm - 2*h_fP*m`, `s = pi*m/2 + 2*xm*tan(30 deg)`, the measurement over pins `M_Re = d_b/cos(a_M) + D` for even z with `inv(a_M) = D/d_b + s/d + inv(30 deg) - pi/z`, and `d_b*cos(90 deg/z)/cos(a_M) + D` for odd z. They reproduce the KISSsoft W70x3x22 report (x*m 0.35, d_a 69.400, s 5.1165, theoretical pin 5.8253, M_Re 76.1835 to 2e-4) and the Hexagon W120x3x38x8f picture (d_a 119.40, d_f 113.40, s 6.271, M 126.017 / 125.956 at the vendor's two actual thicknesses). The theoretical pin has a closed form, so D_Re needs no solver; only M_Re needs the copied `_involute_angle` bisection.

The independent oracle is cheap and works. A 60-line stdlib file that builds the flank as a parametric involute, places it from the textbook base-thickness identity, and finds each pin by a tangency search agreed with the maths to 2.3e-13 mm over 252 even/odd cases (m 0.5 to 10, z 6 to 82, x -0.05 to 0.45) at 8 ms per call. It shares nothing with `calc.py` or `din5480`. Three things in CONTEXT/ROADMAP do not survive contact with the numbers and are surfaced in Open Questions: D-04's claim that the default "exercises the epsilon", the pin guard that cannot fire at the theoretical pin, and the vendors' d_Ff being a limit value that the nominal construction is not meant to equal.

Layout: constants and pure float functions in `din5480.py`, the typed result and `check_shaft`/`derive_shaft` in `shaft_calc.py`, `ShaftParams` in `shaft_params.py` with a local import of `shaft_calc` (the `params.py` pattern). `calc.py`, `params.py`, `tests/regression/`, `ci.yml` and `requirements.txt` are not edited, so `make gear.unchanged` stays green. No dependency is added.

**Primary recommendation:** build `din5480.py` as small pure float functions with the two `0.55` constants named apart, prove each against `tests/shaft_oracle.py` plus the two vendor sets, stop at the D-06 checkpoint with a pre-printed table of our predictions for five shafts, and expect d_Ff and odd-z M_Re to stay `null` unless the human's rows say otherwise.

## Architectural Responsibility Map

This phase has no browser, route or storage tier; every capability is pure logic behind the one parameter model.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Field ranges, `fit` shape, range refusal | API / Backend (`shaft_params`, validated once) | — | L03/CODING_VALUES "validated once at the boundary"; Phase 33 serves it as 422 |
| DIN 5480 formulas, constants, designation codec | API / Backend (`din5480`, pure floats) | — | No kernel, no logger (contracts C1-C2); formulas copied not imported (C5) |
| Typed numbers with `null` + warning | API / Backend (`shaft_calc`) | — | Mirrors `calc.derive`; the same document will feed API, CLI, web in Phase 33 |
| Independent oracle | Test tree (`tests/shaft_oracle.py`) | — | Must share no code with `src/spur` |
| Gate cost record | Bench docs (`bench/RESULTS.md`) | — | REQ-gate-cost-recorded, Phase 30 precedent |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `math`, `re`, `dataclasses` | 3.12.15 | involute maths, codec, result records | No new dependency (REQUIREMENTS "No new runtime or dev dependency"); `[VERIFIED: .venv/bin/python -c, 3.12.15]` |
| pydantic | 2.13.5 (pinned venv) | `ShaftParams`, `ShaftDimensions` | The gear's own boundary; `[VERIFIED: .venv/bin/python -c "import pydantic"]` |
| pytest | 9.1.1 | tests, `pytest.approx` | `[VERIFIED: .venv/bin/pytest --version]` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `spur.params._f`, `_extra`, `when` | in-repo | field metadata builders | Import, never edit `params.py` (gear schema stays byte-equal); `_f` takes numeric `ge`/`le` only, so the `str` field uses `Field(...)` + `_extra(group)` as `root_shape` does (`src/spur/params.py:30`, `:75`) |
| ruff, mypy `--strict`, import-linter | in `.venv` | the gate | `[VERIFIED: ls .venv/bin]` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| copied `_involute_angle` bisection | Newton / scipy | scipy is dev-only and pruned from the image; a bracket-less Newton is the L08 origin story (PITFALLS 8c) |
| closed-form theoretical pin | root-finding | no solver needed: `a_M = tan(a_c) - s/d - inv(30 deg) + pi/z`, then `D = d_b*(tan a_M - tan a_c)`; matches 5.8253 `[VERIFIED: scratchpad calc3.py]` |
| one regex for the whole designation | split then per-token regex | a single regex cannot say which token is bad; D-05 requires naming it |

**Installation:** none. `requirements.txt` stays byte-identical.

**Version verification:** no external package is recommended. Pydantic and pytest versions above were read from the project venv, not the registry.

## Package Legitimacy Audit

No external packages are installed by this phase (stdlib, the existing pydantic and pytest only).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | — | none to audit |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Project Constraints (from CLAUDE.md)

- `make verify` is the gate (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest); state the command and the result line. It needs no Docker.
- A number the tool prints is a number someone will cut metal to: no computable-honestly means a warning and no number (L08).
- Defaults are absolute and frozen (L05); a direct conflict between two user choices is a 422, a trim that contradicts nothing is capped and warned (L03).
- English throughout; comments explain why and carry the measurement; no `Any` (L21); vendor types stop at the boundary.
- `no-fake-done` fails on `TODO|FIXME|XXX|HACK|NotImplementedError` in `*.py` `[VERIFIED: Makefile:144]`. The word `ASSUMPTION` is fine.
- Debt rules: a fixed item is flipped, sha-stamped, `git mv`'d and its INDEX row moved in the same commit.
- New behaviour ships with its tests; claims about performance are measured and recorded.
- Conventional Commits, one concern per commit; whoever writes the diff does not review it.
- Stop and ask on: an evidence conflict (doc vs code vs numbers), an unverified library behaviour, a locked decision that looks wrong. Two such conflicts are in Open Questions.

## Architecture Patterns

### System Architecture Diagram

```
 user input (Phase 33: URL / CLI / form; Phase 31: tests only)
        |
        v
 ShaftParams (frozen, validated ONCE)  <---- Field ge/le, fit pattern  (shaft_params.py)
        |   model_validator(after)
        |   local import --------------> shaft_calc.check_shaft(p) -> [(message, fields)]
        |                                   uses din5480.profile_shift_xm + X range + EPS
        |                                   refusal => PydanticCustomError("infeasible", ...)
        v  (valid shaft)
 shaft_calc.derive_shaft(p) -> ShaftDimensions (frozen; null + warning per value)
        |
        |-- din5480.profile_shift_xm(d_B, m, z)  -> xm, x
        |-- tip_diameter, root_diameter(h_fP), tooth_thickness(m, xm)
        |-- internal_form_diameter(...)  ------> used ONLY by the guard, never printed
        |-- theoretical_pin_diameter(...) -> round to 0.01 -> pin_d
        |-- measure_over_pins(z, m, s, pin_d) -> (M_Re, contact_d) | None
        |        even z: copied _involute_angle bisection
        |        odd z : computed, then gated to null + warning (D-13)
        |-- guard: contact_d in [d_Ff_int + margin, d_a - margin] else null + warning
        '-- format_designation(d_B, m, z, fit) -> "W 25x1.25x18x8f"

 din5480.parse_designation(text) -> flat values | DesignationError(token)
        (round trip: parse(format(v)) == v)

 tests/shaft_oracle.py (floats only, imports nothing from spur)
        '-- parametric involute flank + base-thickness identity + pin tangency search
            compared with din5480 at abs=1e-9; vendor rows labelled "not the standard"
```

### Recommended Project Structure
```
src/spur/
├── din5480.py        # constants block (cited slots), pure float formulas, codec
├── shaft_calc.py     # ShaftDimensions, check_shaft, derive_shaft, guard margin
└── shaft_params.py   # ShaftParams (eight fields), _feasible -> shaft_calc (local import)
src/spur/parts.py     # docstring correction only (D-14)
tests/
├── shaft_oracle.py          # not collected, no `spur` import, plain floats
├── test_din5480.py          # formulas vs oracle + vendor rows + codec
├── test_shaft_params.py     # frozen/hashable, pinned names+defaults, range refusal, fit shape
└── test_shaft_calc.py       # derive_shaft nulls, guard, warnings (may merge with the first)
bench/RESULTS.md      # appended "Shaft maths ... (Phase 31)" section: gate delta + seen-red table
```
`din5480_tables.py` and `shaft_model.py` stay docstring-only (D-12 of Phase 30, Phase 34 and 32).

### Component responsibilities

| Module | Knows | Must not import |
|--------|-------|-----------------|
| `din5480` | floats, `math`, `re`, `dataclasses`; constants with clause slots | `calc` (C5), `model`, `shaft_model`, `records`, `logging`, `cadquery` |
| `shaft_calc` | `din5480`; `ShaftParams` for typing only (`TYPE_CHECKING`, as `calc.py` does for `GearParams`) | same list |
| `shaft_params` | pydantic, `params._f/_extra/when`, `din5480` (for the designation), local `shaft_calc` | same list; `spur.calc` directly (C5 is direct-only; reaching it via `params` is by design) |

`[VERIFIED: pyproject.toml:226-290]` contracts C1 to C5; C1 and C2 forbid indirect imports and `params` imports `calc` only inside a function, which import-linter reads as an edge, but `calc` itself reaches no forbidden module, so `shaft_params -> params -> calc` is clean. Run `make lint-imports` after the first commit that adds the import and read `Contracts: 10 kept, 0 broken.`

### Pattern 1: ShaftParams (frozen contract)

**What:** eight fields, names and defaults frozen by a pinned test.
**When to use:** D-01 to D-04 plus the Discretion block.

| Field | Default | Bounds (provisional, `[ASSUMED]`, see A3) | Note |
|-------|---------|------------------------------------------|------|
| `reference_d` | 25.0 | 3 to 850 | derived from module and teeth bounds, not from the standard |
| `module` | 1.25 | 0.5 to 10 | `[CITED: din.de search summary: "module range of 0.5 to 10 ... 6 to 82 ... 30°"]` |
| `teeth` | 18 | 6 to 82 | same source |
| `fit` | "8f" | pattern `^[1-9][0-9]?[a-z]$`, max_length 3 | shape only (D-02) |
| `splined_length` | 30.0 | >0 | solid-only, Phase 32 revises |
| `end_chamfer` | 1.0 | 0 to ... , 0 = none | solid-only |
| `shank_d` | 25.0 | >0 | solid-only |
| `shank_length` | 20.0 | 0 to ..., 0 = none | solid-only |

```python
# Source: src/spur/params.py:87 (frozen model), :256-265 (validator shape); sketch for shaft_params.py
class ShaftParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    reference_d: float = _f(25.0, 3, 850, title="Reference Ø d_B", group="Shaft",
                            unit="mm", step=0.05, help="...")
    fit: str = Field("8f", pattern=r"^[1-9][0-9]?[a-z]$", max_length=3, title="Fit",
                     description="...", json_schema_extra=_extra("Shaft"))

    @model_validator(mode="after")
    def _feasible(self) -> ShaftParams:
        from .shaft_calc import check_shaft  # local import, as params.py does
        problems = check_shaft(self)
        if problems:
            raise PydanticCustomError(
                "infeasible", "{message}",
                {"message": " ".join(m for m, _ in problems),
                 "fields": sorted({f for _, fs in problems for f in fs})})
        return self
```
The `PydanticCustomError("infeasible", "{message}", {"message", "fields"})` shape is the gear's, so Phase 33's 422 handling can be identical `[VERIFIED: src/spur/params.py:262-265]`. A throwaway model with the same field and validator ran this session: the error type was `infeasible` with `ctx` carrying `message` and `fields`; `hash(T()) == hash(T())`; a `\n`-suffixed, `f8` and Arabic-digit `fit` were all refused with `string_pattern_mismatch`; `nan`, `inf` and `1e400` for a bounded float were refused (`less_than_equal`) `[VERIFIED: ran in .venv, 2026-10-24]`.

Pinned-defaults test shape (the gear has no equivalent; this is new): assert `list(ShaftParams.model_fields)` equals the eight names in order and `{n: f.default for n, f in ShaftParams.model_fields.items()}` equals the literal dict, plus `designation(ShaftParams()) == "W 25x1.25x18x8f"`. Use the class-level `model_fields` (pydantic 2.11+ deprecates the instance attribute and `filterwarnings = ["error"]` is on; `tests/test_calc.py:1467` notes the same).

### Pattern 2: ShaftDimensions (typed, null plus warning)

Mirror `calc.DerivedDimensions` (`src/spur/calc.py:927`): frozen `BaseModel`, every key always present, `None` when it does not apply or cannot be computed honestly, `warnings: tuple[str, ...]`. Suggested keys: `reference_d`, `profile_shift` (x), `profile_shift_mm`, `pitch_d`, `tip_d`, `root_d`, `nominal_thickness`, `form_d` (always `None` here), `pin_d`, `measure_over_pins`, `designation`, `warnings`. Names are not frozen (they are results, not parameters; L05 does not apply) but they will become Phase 33's schema `dims` rows, so choose once.

### Pattern 3: pure functions over floats in `din5480`

Constants in one block, each with a source slot and an `ASSUMPTION` marker until the checkpoint:

| Constant | Value | Meaning | Status |
|----------|-------|---------|--------|
| `PRESSURE_ANGLE` | 30 degrees | fixed by the standard `[CITED: din.de summary]` | assumed until clause |
| `ADDENDUM_FACTOR` (h_aP) | 0.45 | tip height over the shifted reference circle | `[ASSUMED]`; KISSsoft `[haP*] 0.450` read |
| `TIP_DIAMETER_OFFSET` | 0.2 | `d_B - d_a1 = 0.2*m` | `[VERIFIED]` 69.400 = 70 - 0.6 and 119.40 = 120 - 0.6 in the two vendor reports |
| `SHIFT_TERM` | `ADDENDUM_FACTOR + TIP_DIAMETER_OFFSET/2` = 0.55 | the `0.55` in the shift formula | derived, see Pitfall 1 |
| `H_FP` | 0.55 provisional | dedendum factor (process dependent) | D-07, copy decides |
| `RHO_FP` | 0.16 | hob tip radius, only for the internal d_Ff | `[VERIFIED: KISSsoft report "ρfP* 0.160"; Hexagon dialog 0.16]` |
| `X_MIN`, `X_MAX`, `X_EPS` | -0.05, 0.45, 1e-9 | shaft shift range and the comparison epsilon | range `[ASSUMED: FEATURES/PITFALLS, two vendor-adjacent sources]` |
| `PIN_STEP` | 0.01 mm | D-11 gauge step | see A4 |
| `GUARD_MARGIN_FACTOR` | 0.1 (times m) | D-12 margin on diameters | see A5 |

The core functions, each one quantity (CODING_VALUES "one operation per routine"):

```python
# Source: derived and run in the research session; every number below was reproduced by scratchpad calc1/calc3.py
def profile_shift_xm(d_b: float, m: float, z: int) -> float:
    """xm in mm. d_b = m*z + 2*xm + 1.1*m, so xm = (d_b - z*m)/2 - 0.55*m."""
    return (d_b - z * m) / 2 - SHIFT_TERM * m          # x = xm / m gives exactly 0.45 for W25x1.25x18

def theoretical_pin_diameter(m: float, z: int, xm: float) -> float:
    """The pin that touches the flank on the circle m*z + 2*xm (D-10), closed form."""
    d = m * z; d_b = d * math.cos(ALPHA); d_c = d + 2 * xm
    a_c = math.acos(d_b / d_c)
    s = m * math.pi / 2 + 2 * xm * math.tan(ALPHA)
    a_m = math.tan(a_c) - s / d - inv(ALPHA) + math.pi / z   # D cancels out of the equation
    return d_b * (math.tan(a_m) - math.tan(a_c))

def measure_over_pins(m: float, z: int, s: float, pin_d: float) -> tuple[float, float] | None:
    """(M_Re, contact diameter) for a thickness s on the circle m*z; None when no honest root."""
    d = m * z; d_b = d * math.cos(ALPHA)
    target = pin_d / d_b + s / d + inv(ALPHA) - math.pi / z
    if not 0 < target < inv(math.radians(89.0)):
        return None
    a_m = _involute_angle(target)                  # copied from calc.py:1327, never imported
    ...                                            # centre-circle diameter d_b/cos(a_m); odd z times cos(pi/(2z))
```
The function takes the thickness `s` as an argument (not xm) so it reproduces the Hexagon rows at the vendor's actual thicknesses 6.220 and 6.180 today and takes the limit thicknesses in Phase 34 unchanged. `D` cancels in the theoretical-pin equation, which is why no solver is needed for it.

### Pattern 4: designation codec

Print: `f"W {num(d_b)}x{num(m)}x{z}x{fit}"` with `num(v) = repr(float(v)).removesuffix(".0")`. `repr` is the shortest string that round-trips a float, so `parse(print(p)) == p` holds for every float, unlike `:g` which keeps six significant digits (`25.123456` would not round-trip). The fields are bounded (0.5 to 850), where `repr` never switches to exponent form.

Parse, in this order, each step naming the offending token: (1) bound the input length (suggest 64 characters) before anything else; (2) the type letter: a leading `W`, else refuse (`N` gets its own sentence: hub not supported, other standards' strings likewise); (3) `re.split(r"[xX]", rest, maxsplit=3)` must give exactly four tokens (`maxsplit=3` keeps a fit letter `x` inside the last token); (4) each token is checked with its own `re.fullmatch` using `[0-9]` (never `\d`, which matches Unicode digits and `float("٣")` succeeds) and `[.,]` as the decimal mark, then `float(token.replace(",", "."))`; (5) `teeth` must be an integer token; (6) `fit` must match the same pattern as the field. Raise `DesignationError(ValueError)` whose message quotes the token; Phase 33 maps it to 422. Optional single space after `W` (`W\s?` or equivalent), no other whitespace.

### Anti-Patterns to Avoid
- **One `0.55` constant for two things.** See Pitfall 1.
- **Importing `inv` or `_involute_angle` from `calc`.** C5 forbids it; copy both.
- **A bare `x >= -0.05` / `x <= 0.45`.** Use `X_EPS`.
- **Printing the internal d_Ff.** It exists only as the guard's lower bound (D-12).
- **A solver for the theoretical pin.** It is closed form.
- **`float()` on unvalidated text, `\d`, `$`, `:g`.** See Pitfall 6.
- **Widening `Part`, adding `slug()` or any `model`/`records` change.** Phase 32 (D-14).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Inverting the involute function | Newton loop | the 60-halving bisection copied from `calc._involute_angle` (`src/spur/calc.py:1327`) | monotonic on (0, pi/2), no starting guess can escape the bracket; 2.9e-15 rad measured by the STACK research `[CITED: .planning/research/SUMMARY.md]` |
| Field range/shape checks | manual `if` in the validator | `Field(ge=, le=, pattern=)` | already refused `nan`, `inf`, `1e400`, `\n`-suffixed and non-ASCII-digit input in the probe above |
| Cross-field refusal plumbing | a new error class | `PydanticCustomError("infeasible", ...)` | the gear's shape; Phase 33 reuses its 422 mapping |
| Float comparison of results | `==` | `pytest.approx(abs=1e-9)` against the oracle; `abs=2e-4` for KISSsoft's rounded x | the oracle agrees to 2.3e-13 |
| Pin contact location | analytic inverse in the oracle | tangency search against the parametric flank | that is what makes the oracle independent |

**Key insight:** every quantity here has a one-line closed form except M_Re's inversion. The risk is not difficulty but a plausible wrong constant, so the work is in proof and in what is allowed to print.

## Common Pitfalls

### Pitfall 1: two different 0.55s
**What goes wrong:** the shift formula's `0.55` and `h_fP = 0.55` are different quantities. The shift term is `h_aP + 0.1 = 0.45 + 0.2/2`, i.e. it comes from `d_a1 = d_B - 0.2*m`. If both read one constant, then the copy's likely `h_fP = 0.60` (hobbing; KISSsoft prints `0.60 / 0.16 / 0.45 Hobbing`) silently moves x, d_a, s and every M_Re.
**Why it happens:** the numbers coincide at the provisional value.
**How to avoid:** two named constants; a test that changing `H_FP` moves `d_f` and nothing else (KISSsoft: h_fP 0.60 with xm 0.3501 `[VERIFIED: read]`, same xm as the 0.55 formula 0.35); a test per vendor row at its own `h_fP` (Hexagon 0.55 gives 113.40, KISSsoft 0.60 gives 63.100, the 0.55 formula gives 63.400 for the same shaft).
**Warning signs:** a single `0.55` in the source; x changes when the process changes.

### Pitfall 2: the epsilon the default does not exercise
**What goes wrong:** D-04 says the default's x "computes to 0.44999999999999996" and "exercises the range epsilon". Measured: with `xm / m` (the form above) W25x1.25x18 gives exactly `0.45`; with `d_B/(2m) - z/2 - 0.55` it gives `0.44999999999999996`. Either way the value is at or below 0.45, so a bare `x <= 0.45` accepts it and removing the epsilon does not turn a default-based test red. The epsilon matters at the upper edge only for a combination whose float lands above 0.45, e.g. `(17.6, 0.8, 20)` gives `0.4500000000000008`, and at the lower edge for W30x2x14 (`-0.050000000000000044`).
**How to avoid:** pin the default as "validates and its x is within `X_EPS` of 0.45"; add a separate guard test for the upper edge using `(17.6, 0.8, 20)` (or any listed case under the form actually shipped) and for the lower edge `(30, 2, 14)` and `(25, 1.25, 19)`; see each seen red with `X_EPS = 0`. Pick one expression order and pin it; the epsilon cases depend on it `[VERIFIED: scratchpad, 74 upper-edge and 850 lower-edge float misses over standard modules]`.
**Warning signs:** a "range edge" test that passes with the epsilon deleted.

### Pitfall 3: commented-out-code lint, naming lint and the import belt
**What goes wrong:** (a) ruff `ERA001` rejects comments shaped like assignments: `# xm = (d_B - z*m)/2 - 0.55*m` fails `[VERIFIED: ran ruff with the repo config on a probe file]`; put formulas in docstrings. (b) `N803`/`N806` reject `D` and `M_Re` as argument or local names `[VERIFIED: same probe]`; use `pin_d`, `m_re`. (c) `tests/test_seam.py::_import_lines` is a line-anchored regex: a wrapped docstring or comment line that begins with `from calc`, `import logging`, `from model` and the like matches as an import `[VERIFIED: tests/test_seam.py:40-55, quoted: "^[ \t]*(?:import[ \t]+(?:spur\.)?(?:{alt})\b" and "|from[ \t]+(?:spur\.|\.)?(?:{alt})\b"]`. Never start a prose line with `from <gear-module>` or `import <name>`; the placeholder docstrings already say "never imports from calc.py" mid-line for this reason.

### Pitfall 4: the guard cannot fire at the theoretical pin
**What goes wrong:** D-12's guard sits between internal d_Ff plus margin and d_a minus margin. Over 7,392 cases (16 modules, z 6 to 82, six x values) the rounded theoretical pin's contact stays within 0.0069 mm of `m*z + 2xm`, at least 0.62*m above the internal d_Ff and at least 0.886*m below d_a `[VERIFIED: scratchpad calc, 0 failures]`. So in `derive_shaft` for Phase 31 the guard never trips, and a test that expects the `null` branch through `derive_shaft` can never be written.
**How to avoid:** make the guard a function of an explicit `pin_d` and cover its `null` branches by calling it (and `measure_over_pins`) with an oversize and an undersize pin; it becomes live in Phase 34 when the copy's D_Re (6.000 at m 3: contact 116.78 against d_Ff_int 113.88 and d_a 119.40 `[VERIFIED: scratchpad]`) arrives. State this honestly in the code comment and the plan, or CODING_VALUES' "no unreachable branches" is broken by appearance.
**Warning signs:** a coverage gap on the guard's `null` branches; a test that monkeypatches the pin to reach them without saying so.

### Pitfall 5: odd z formula tested only by itself
**What goes wrong:** using the even formula for odd z is wrong by 0.081 mm at W25x1.25-type z 19 with a 1.75 pin `[VERIFIED: scratchpad calc3]`, and with the factor `cos(90 deg/z)` applied the maths still has no copy row. The geometric oracle independently reproduces the odd formula (two pins in the spaces at angles pi/z and pi, centre distance plus D) to 1e-13, which proves the algebra, not that the standard measures this way.
**How to avoid:** D-13 stands: build it, oracle-test it, print `null` with a warning until the copy confirms. A natural odd-z anchor is W25x1.25x19 (odd, and the same d_B and m as the default; see the checkpoint table).

### Pitfall 6: parser accepting what it should not
**What goes wrong:** `float()` accepts `inf`, `nan`, `1e3`, `1_0` and Unicode digits; Python `re`'s `\d` matches Unicode digits and `$` matches before a trailing newline. A permissive parser builds parts the user did not ask for (L44's spirit).
**How to avoid:** length bound first, then `re.fullmatch` with `[0-9]`, `[.,]` and nothing else; the codec must also refuse what D-05 does not list: `DIN 5480 -` prefix, `×`, spaces around `x`, an upper-case fit letter, hub `N`, `INT`/ANSI strings. Test each as a refusal naming its token (Open Question 3 asks whether spaces around `x` should join the accepted list).

### Pitfall 7: vendor rows are not at nominal thickness, and one rounds x
**What goes wrong:** the Hexagon M values (126.017, 125.956) are at the vendor's actual thicknesses 6.220 and 6.180, not at nominal 6.271 (nominal gives 126.0949). KISSsoft prints x*m 0.3501 where the formula gives 0.35 (it rounds x to 0.1167), so its M_Re 76.1835 is 1.7e-4 above the exact 76.18337 `[VERIFIED: scratchpad; xm 0.3501 gives 76.18354]`.
**How to avoid:** call `measure_over_pins` with the vendor's `s` for the Hexagon rows (abs=1e-3, the print precision), and compare KISSsoft's 76.1835 at abs=2e-4 (or feed xm 0.3501 and use abs=1e-4), commenting the reason with these numbers. Do not loosen the oracle comparison to hide it.

### Pitfall 8: expecting d_Ff to print
**What goes wrong:** both vendors print the standard's form diameter as a limit, not the constructed nominal: Hexagon `dFf1 113,91 max`, KISSsoft two values, `63.718` "calculated on the basis of the constructed involute" and `63.920` "Root diameter allowances in accordance with DIN 5480-1, Table 5" `[VERIFIED: Hexagon page 2 image; KISSsoft report 5.3 text]`. The public construction reproduces KISSsoft's constructed value exactly (63.7180 at h_fP 0.60, rho 0.16 m) and Hexagon's to 0.03 (113.8802 against 113.91), so the gaps (0.202 and 0.030 mm at m 3) are the Table 5 allowance, not a construction error.
**How to avoid:** plan d_Ff as `null` with its sentence and treat "prints a number" as a conditional follow-up that only the copy's row can trigger, with an agreement rule fixed at the checkpoint (suggest: to the printed digit of the copy's row). Do not spend tasks making the number print.

### Pitfall 9: the din5480 docstring promises clauses that do not exist yet
**What goes wrong:** the placeholder says "A formula whose clause cannot be cited does not go in" (`src/spur/din5480.py` docstring). D-06/D-07 build the formulas first with a clause slot.
**How to avoid:** rewrite the docstring in the first commit that fills the file to say what is true: formulas present are assumptions until the checkpoint records each clause. At the post-checkpoint commit fill the slots; a constant still marked `ASSUMPTION` at close is a visible, deliberate state (d_Ff internal, odd z), not an accident. Optional: a test asserting each constant listed as copy-confirmed has a non-empty citation string.

### Pitfall 10: a gate-cost claim without a baseline
Record the `make verify` result line and `real` time with load before and after, on this host, against Phase 30's `1369 passed`, `233.18 s`, `real 234.48 s` `[VERIFIED: bench/RESULTS.md Phase 30 section]`. The run-to-run spread is about 8 percent (about 19 s), so a small delta is "inside the noise", not a speed claim. Cost expectation: the oracle is 8 ms per call, so even 1,000 oracle comparisons is under 10 s of CPU spread over xdist workers; keep sweep sizes in the low hundreds (252 cases took 2.0 s `[VERIFIED: scratchpad]`).

## Code Examples

### Reproduction table (computed this session from the `[ASSUMED]` formulas; use as the checkpoint prediction table)

| Shaft | x | xm mm | d_a | d_f (0.55 / 0.60) | s | internal d_Ff | theoretical D | rounded D | M_Re at rounded D | contact d |
|-------|---|-------|-----|-------------------|---|---------------|---------------|-----------|-------------------|-----------|
| W25x1.25x18 | 0.45 | 0.5625 | 24.750 | 22.250 / 22.125 | 2.6130 | 22.450 | 2.7305 | 2.73 | 27.9987 | 23.625 |
| W25x1.25x19 (odd) | -0.05 | -0.0625 | 24.750 | 22.250 / 22.125 | 1.8913 | 22.563 | 2.3598 | 2.36 | 27.1464 | 23.625 |
| W30x2x14 | -0.05 | -0.1000 | 29.600 | 25.600 / 25.400 | 3.0261 | 26.169 | 3.8348 | 3.83 | 33.6851 | 27.795 |
| W70x3x22 | 0.1167 | 0.3500 | 69.400 | 63.400 / 63.100 | 5.1165 | 63.985 (0.55), 63.718 (0.60) | 5.8253 | 5.83 | 75.7192 | 66.705 |
| W120x3x38 | 0.45 | 1.3500 | 119.400 | 113.400 / 113.100 | 6.2712 | 113.880 | 5.9258 | 5.93 | 125.9018 | 116.705 |

### Vendor cross-checks the tests may commit (D-08; label "vendor cross-check, not the standard")
- KISSsoft `12 Spline (DIN 5480)`, W 70.00x3.00x22x6f, `https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf`, read with `pdftotext` this session: reference diameter 70.00, `[x*m] 0.3501`, `[d] 66.000`, `[db] 57.158`, `[da] 69.400`, `[df] 63.100` (profile `0.60 / 0.16 / 0.45 Hobbing`), `[dFf] 63.718` and `63.920`, theoretical pin `[dm] 5.8253`, effective pin `[DMeff] 6.0000`, `[MRe/Mri-pin] 76.1835`. Our values: d_a 69.4, d_f 63.100 at h_fP 0.60, s 5.1165, D 5.82529, M at pin 6.000 76.18337 (xm 0.35) or 76.18354 (xm 0.3501).
- Hexagon WN2 brochure `https://www.hexagon.de/pdf/wn2_d.pdf` (page 2 is an embedded image; read by rendering it this session): `W 120 x 3 x 38 x 8f`, `hfp/m 0.55`, `da1 119,40 h11`, `dFf1 113,91 max`, `df1 113,40 -1,15`, `s v max 6,243`, `s max act. Ref. 6,220`, `s min actual 6,180`, `DM 6,000`, `M1maxRef 126,017`, `M1min 125,956`, `evmin = e2 = s1 = 6,271`. Our values: d_a 119.4, d_f 113.40, s 6.2712, M at 6.000 pin 126.01692 (s 6.220) and 125.95596 (s 6.180).

### Oracle sketch (the proven prototype, to be written as `tests/shaft_oracle.py`)
```python
# Independent of spur: nothing here is inv(), _involute_angle or the closed-form pin.
def flank_point(r_b, psi_b, t):
    """Upper flank of the tooth centred on +x: mirrored parametric involute rotated by psi_b."""
    qx, qy = r_b * (cos(t) + t * sin(t)), -r_b * (sin(t) - t * cos(t))
    return cos(psi_b) * qx - sin(psi_b) * qy, sin(psi_b) * qx + cos(psi_b) * qy

# base-circle half-thickness angle from the textbook BASE thickness identity, not from s on d:
#   s_b = m*cos(a)*(pi/2 + z*(tan(a) - a)) + 2*xm*sin(a);   psi_b = s_b / (2*r_b)
# pin centre on the space centreline at angle pi/z; bisect its radius until the distance to the
# flank (grid of 400 + golden refine, t up to the tip) equals D/2; bracket (r_b, r_a + D).
# even z: M = 2*rho + D.   odd z: second pin at angle pi, M = |c1 - c2| + D.
```
Written to a file and run: `measure(3, 22, 0.35, 6.0)` returned 76.18336835729897 against the maths' 76.18336835729896; odd z19 and even z18 at m 1.25 agree to 1e-13; 252 grid cases worst 2.27e-13 mm `[VERIFIED: scratchpad oracle_proto.py]`. Add `contact_diameter` (radius at the minimising t, times two) so the guard's contact value is oracle-tested too. Gotchas found while prototyping: the parametric flank must be the mirrored-and-rotated involute (a straight base tangent is not an involute), and the bisection bracket must extend to `r_a + D` because the pin centre sits outside the tip circle.

## Checkpoint design (D-06) for the planner

Stop at `checkpoint:human-action` after the build tasks. Present the table above (our predictions, with `ASSUMPTION` status) and ask the human to supply, per row, `part / clause / table` and the copy's value for: `d_a`, `d_f` (and which `h_fP` the table assumes), `s` (or `e`), the profile shift, and where available the copy's D_Re and M_Re. Minimum set (CONTEXT D-06): two basic-dimension rows; one d_Ff row (which value, what it is a limit of, its digit precision); one odd-z row. Suggest W25x1.25x18 and W25x1.25x19 (same d_B and m, x at +0.45 and -0.05, one even and one odd z, both range edges, both rows of the default's own module page) and W30x2x14 as the ideal third. Decisions the human must also give: `h_fP` by clause, whether the shift range -0.05 to +0.45 is the shaft range by clause, the `fit` token notation (quality digits and letter set), and the d_Ff agreement rule. Outcomes route as D-09: any contradiction stops, shows the clause against the code, logs an `Lxx`, and the guard test is seen red against the old constant. Record the result in the plan summary.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 2006 series: Parts 1, 2, 15, 16 hold the tolerance system and the Table 5 root allowance (Part 1) | DIN 5480-1:2025-08 and -2:2025-10 four-part series; DIN 5480-1:2026-05 replaced the 2025-10 text | 2025-2026 | The human's copy is the 2006 series (human answer 2026-10-23); vendors compute to 2006 `[CITED: .planning/research/SUMMARY.md, PITFALLS.md]` |
| `h_fP = 0.55` theoretical | 0.60 hobbing, 0.65 shaping per process | process-dependent | one constant, copy decides (D-07) |

**Deprecated/outdated:** the research brief's `x*m = (d_B - z*m)/2 - 1.1*m` is wrong by a factor 2 on the correction term (PITFALLS); do not use it.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Every DIN 5480 formula above (shift, d_a, d_f, s, M_Re even and odd, shift range) matches the 2006 copy | Standard Stack, Patterns | A shipped wrong number; mitigated entirely by the D-06 checkpoint |
| A2 | The shaft shift range is -0.05 to +0.45 | Constants | A legal size refused or an illegal one accepted; copy clause needed |
| A3 | Field bounds `reference_d` 3 to 850, `module` 0.5 to 10, `teeth` 6 to 82, `fit` max length 3, solid-only bounds | Pattern 1 | Module and teeth ranges are web-summary MEDIUM (din.de), d_B bound is arithmetic from them (the earlier "6 to 500" was unverified); Phase 32's sweep sets solid-field and heaviest-shaft bounds; widening later is additive, narrowing refuses links |
| A4 | The 0.01 mm gauge step is common practice | Constants | Both vendors' *effective* pins are round values (6.000, 5.500), consistent with a coarser series for the standard's own D_Re; no documented series for the theoretical pin was found, so D-11's default stands. Wrong step = a pin the user cannot buy |
| A5 | Guard margin = 0.1 * m on diameters | Pitfall 4 | Sized from the two observed d_Ff gaps (0.030 and 0.202 mm, both at m 3: 0.01*m and 0.067*m) with 1.5x headroom over the larger; scaling with m is untested. The nominal guard cannot fire either way, so a wrong margin costs nothing until Phase 34 |
| A6 | The fit token shape `[1-9][0-9]?[a-z]` | Pattern 1 | Quality range and deviation letters are unverified (4 to 9 or 5 to 12; letters a to v); a too-narrow pattern refuses a real fit at Phase 34 |
| A7 | Odd-z measurement is the distance between the two nearest-opposite pin centres plus D | Pitfall 5 | No copy row; oracle proves algebra only |
| A8 | `D_Re` prints for odd z while `M_Re` is `null` (it is parity-independent and oracle-proved) | Open Question 4 | A pin printed beside no measure; harmless but surprising |

## Open Questions

1. **D-04 says the default "exercises the epsilon"; the numbers say it does not.** (Evidence conflict, stop-and-ask.)
   - Known: W25x1.25x18 is `0.45` or `0.44999999999999996` depending on expression order, never above 0.45 `[VERIFIED: scratchpad]`.
   - Unclear: whether D-04's intent is just "the default is on the edge" (still true).
   - Recommendation: keep the default and the "x is the edge" pin; add the dedicated upper-edge epsilon case `(17.6, 0.8, 20)` and the lower-edge cases, each seen red with `X_EPS = 0`. Update the wording in the plan summary.

2. **The guard is unreachable through `derive_shaft` in this phase** (Pitfall 4). Recommendation: implement it as a function of explicit `pin_d`, test it by direct calls, say so in the comment.

3. **Whitespace around `x`.** D-05 lists three accepted variants; catalogues (Ameco) print `W 25 x 1,25 x 18 x 8f`. Recommendation: stay with D-05's closed list for this phase (stricter, safer, L44), test spaced input as a refusal naming the token, and log the spaced form as an idea if the human wants it.

4. **D_Re for odd z.** CONTEXT D-13 nulls only M_Re. Recommendation: print D_Re (parity-independent, oracle-proved), null M_Re with the warning; confirm at plan review.

5. **Cross-field rules among the solid-only fields** (`end_chamfer` vs tooth height and splined length, `shank_d` vs tip). The kernel behaviour for real DIN proportions is Phase 32's spike (SUMMARY research flag, `Solid.chamfer` past the tooth height returns an invalid solid). Recommendation: Phase 31 enforces ranges only; the cap-and-warn or refusal arrives with the solid; hand it off explicitly.

6. **Tech-debt route (D-14).** Recommendation: option 2, re-target. Keep the item active, edit its Context and Next step to say the docstring was corrected in Phase 31 and the trigger is now Phase 32, update its INDEX trigger cell in the same commit. Splitting forces a resolved-file sha that cannot be self-referenced (the Phase 13 note in STATE: sha recorded in a follow-up commit).

7. **Decision-log entry.** Prior phases append one `Lxx` at close (L27 to L33 pattern). Recommendation: one entry at close recording the frozen field set, the checkpoint's `h_fP` and range clauses, the pin policy (D-10/D-11), the guard margin and why, and the shipped `null`s, citing numbers from SUMMARY or `bench/RESULTS.md`. Mandatory earlier if D-09 fires.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 venv (`.venv`) | all tests, gate | yes | 3.12.15 | `make venv` |
| pytest, ruff, mypy, import-linter | the gate | yes | pytest 9.1.1; others in `.venv/bin` | `make venv` |
| `make verify` | gate and cost record | yes | needs no Docker | — |
| git, tag `v0.6` | `make gear.unchanged`, close diff | yes | `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` is empty now | — |
| `pdftotext`, `pdftoppm` | only this research (vendor PDFs) | yes (`/opt/homebrew/bin`) | — | not needed by the executor |
| Host idle | gate-cost record | 1-min load 6.10 at research time | — | record the load, as Phase 30 did |

**Missing dependencies with no fallback:** the human's DIN 5480 (2006) copy, needed at the D-06 checkpoint and not obtainable by any tool here.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + xdist + pytest-cov (`pyproject.toml [tool.pytest.ini_options]`, `filterwarnings = ["error"]`) |
| Config file | `pyproject.toml`; coverage `fail_under = 96`, branch coverage on |
| Quick run command | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_din5480.py tests/test_shaft_params.py tests/test_shaft_calc.py tests/test_seam.py` |
| Full suite command | `make verify` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-shaft-params | eight names in order, literal defaults, frozen, hashable, `hash != GearParams()`; default validates; `fit` shape (`8f` ok; `f8`, `08f`, `8F`, `8`, `٣f`, `8f\n` refused) | unit | `pytest tests/test_shaft_params.py -x` | no, Wave 0 |
| REQ-profile-shift-from-dB | `xm` for 5 shafts; epsilon edges `(30,2,14)`, `(25,1.25,19)`, `(17.6,0.8,20)`; just-outside refused with a sentence naming range and fields; `H_FP` change does not move x | unit | `pytest tests/test_din5480.py -k shift -x` | no, Wave 0 |
| REQ-shaft-basic-dims | d_a, d_f (both h_fP), s agree with oracle (abs 1e-9) and both vendor sets; derived from the oracle's own inversion `d_B = m z + 2xm + 1.1m` | unit | `pytest tests/test_din5480.py -k dims -x` | no, Wave 0 |
| REQ-form-diameter-honest | `form_d is None` for every shaft with a warning naming why; internal construction reproduces 63.718 and 113.880 and is not exposed | unit | `pytest tests/test_shaft_calc.py -k form -x` | no, Wave 0 |
| REQ-mre-nominal | even-z and odd-z M_Re and contact vs oracle on a grid; Hexagon rows at s 6.220 / 6.180; closed-form D vs oracle contact; odd z `null` + warning through `derive_shaft`; guard `null` branches by direct call with oversize/undersize pin; no root (`target` out of range) `null` | unit | `pytest tests/test_din5480.py tests/test_shaft_calc.py -k "pin or measure" -x` | no, Wave 0 |
| REQ-designation-codec | print canonical; parse accepts D-05 variants; round trip over asymmetric values (d_B != z; m 1.25, 0.75, 10); refusal table naming the token (foreign standards, hub, prefix, `z=18.5`, `8F`, 65-char input) | unit | `pytest tests/test_din5480.py -k designation -x` | no, Wave 0 |
| Seam | contracts and belts stay green with the filled files | contract | `make lint-imports`; `pytest tests/test_seam.py` | yes |
| Oracle independence | `tests/shaft_oracle.py` has no `spur` import | unit (source read) | `pytest tests/test_din5480.py -k oracle_imports -x` | no, Wave 0 |
| Oracle sensitivity | a mutated odd-z factor / shift constant makes the comparison fail (durable mutation test) | unit | `pytest tests/test_din5480.py -k mutat -x` | no, Wave 0 |
| REQ-gate-cost-recorded | delta recorded in `bench/RESULTS.md` | measurement | `/usr/bin/time -p make verify` with a meta log | n/a |
| Gear unchanged | `make gear.unchanged`; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml`; `calc.py`, `params.py`, `requirements.txt` diff empty | gate | `make gear.unchanged` | yes |

### Sampling Rate
- **Per task commit:** `make verify.fast` (static steps plus every test file but the five heavy ones; the commit hook budget is 30 s, last priced 10.01 s `[VERIFIED: bench/RESULTS.md 30-01]`; new shaft tests are pure and fast).
- **Per wave merge:** `make verify`.
- **Phase gate:** `make verify` green with the result line recorded, `make gear.unchanged`, the v0.6 diff empty, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/shaft_oracle.py` (not collected, `from __future__ import annotations`, typed, plain floats)
- [ ] `tests/test_din5480.py`, `tests/test_shaft_params.py`, `tests/test_shaft_calc.py`
- [ ] No framework install needed.
- Seen-red recording (Phase 30 pattern): logs under `.planning/phases/31-shaft-maths-parameters-and-designation/investigation/` and a "Seen red once (Phase 31)" table in `bench/RESULTS.md`. Candidate breaks: shift term 0.55 to 0.5; odd-z cosine dropped; `X_EPS = 0` (upper and lower edge cases); `H_FP` changed (D-09 guard); a default changed (the frozen pin); `:g` instead of `repr` in the printer; guard bounds swapped; oracle comparison with a mutated oracle input.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | none in this project (CODING_VALUES) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Pydantic `Field` bounds and `pattern` at the one boundary; codec: length bound, anchored `re.fullmatch`, ASCII classes, no `float()` on unvalidated text |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Regex denial of service on the designation | Denial of service | cap length first, split on a single character class, per-token `fullmatch` of linear patterns |
| Non-finite or huge numbers (`nan`, `inf`, `1e400`, a 10 kB digit string) | Tampering / DoS | field bounds refuse non-finite `[VERIFIED: probe]`; codec digits-only grammar plus length bound |
| Unicode digits / trailing newline slipping past a pattern | Tampering | `[0-9]`, `fullmatch`; the Pydantic probe refused both |
| A parsed designation silently differing from the fields | Tampering | numeric fields are the truth (L03); the contradiction 422 is Phase 33 |

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `31-CONTEXT.md`, `REQUIREMENTS.md`, `STATE.md` (first 381 lines), ROADMAP Phase 31 section, `.planning/research/SUMMARY.md`, `PITFALLS.md` (Pitfall 1, 5, 8, 9 and ground-truth table), `FEATURES.md` 2a, `ARCHITECTURE.md` (grep of §3, §4), `src/spur/{params,parts,shaft_params,shaft_calc,din5480,din5480_tables,shaft_model}.py`, `src/spur/calc.py` excerpts (`inv`, `check`, `DerivedDimensions`, `_involute_angle`, imports), `pyproject.toml`, `Makefile` excerpts, `tests/test_seam.py`, `tests/trochoid_oracle.py` header, `docs/CODING_VALUES.md`, `docs/architecture/decision_log.md` L46, `bench/RESULTS.md` Phase 30 section, the tech-debt item and INDEX.
- Probes run in `.venv` and a scratchpad: pydantic behaviour, ruff `ERA001`/`N803`/`N806`, the formula, oracle, float-order and grid scripts (scratchpad `calc1.py`, `calc2.py`, `calc3.py`, `oracle_proto.py`).
- KISSsoft report PDF (read by `pdftotext`) and Hexagon WN2 brochure page 2 (rendered and viewed): `https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf`, `https://www.hexagon.de/pdf/wn2_d.pdf`. These are vendor reports, authoritative for what the vendors print, not for the standard.

### Secondary (MEDIUM confidence)
- din.de / dinmedia search summaries for module 0.5 to 10, z 6 to 82, 30 degrees: https://din.de/en/wdc-proj:din21:349032941 (abstract page; the standard text itself was not read).

### Tertiary (LOW confidence)
- Search for a published gauge-pin series and the Part 2 D_Re table found only paywalled DIN pages; nothing citable (A4).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, stdlib and existing pins only.
- Architecture: HIGH for module layout and contracts (files and probes), MEDIUM for result-field names (they become Phase 33's `dims` rows).
- Formulas: MEDIUM, reproduced to the vendors' print precision and to an independent oracle, all `[ASSUMED]` until the copy.
- Pitfalls: HIGH for the lint, regex, float-order and guard findings (run this session); MEDIUM for the d_Ff interpretation.

**Research date:** 2026-10-24
**Valid until:** the D-06 checkpoint; the repo-integration findings hold until `params.py`/`calc.py` or the contracts change (30 days otherwise).
