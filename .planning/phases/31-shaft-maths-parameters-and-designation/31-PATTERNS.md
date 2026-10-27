# Phase 31: Shaft Maths, Parameters and Designation - Pattern Map

**Mapped:** 2026-10-24
**Files analyzed:** 13 new/modified
**Analogs found:** 12 / 13 (all analog paths verified git-tracked: `src/spur/*`, `tests/trochoid_oracle.py`, `bench/RESULTS.md`, `docs/*`)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/shaft_params.py` | model (frozen pydantic) | request-response (validate once) | `src/spur/params.py` (`GearParams`, lines 18-132, 256-265) | exact |
| `src/spur/shaft_calc.py` | service (typed derived dims + `check`) | transform | `src/spur/calc.py` (`check` :628, `DerivedDimensions` :927) | exact |
| `src/spur/din5480.py` | utility (pure float formulas + codec + constants) | transform | `src/spur/calc.py` (`inv` :117, `_involute_angle` :1327) | role-match (maths); codec has no analog |
| `src/spur/parts.py` | config (docstring only, D-14) | n/a | itself | exact |
| `tests/shaft_oracle.py` | test helper (not collected) | transform | `tests/trochoid_oracle.py` | exact |
| `tests/test_din5480.py` | test | transform | `tests/test_calc.py`, `tests/test_trochoid.py` | role-match |
| `tests/test_shaft_params.py` | test | request-response | `tests/test_calc.py:60-90`, `:138` | role-match |
| `tests/test_shaft_calc.py` | test | transform | `tests/test_calc.py:60-92` | role-match |
| `bench/RESULTS.md` (append section) | doc | n/a | Phase 30 section, lines 6812-6900 | exact |
| `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md` + `docs/tech_debt/INDEX.md` row (line 20) | doc | n/a | the item itself | exact |
| `docs/architecture/decision_log.md` (only if D-09 fires; new `Lxx`) | doc | n/a | L46 entry (file tail) | exact |
| `.planning/phases/31-.../investigation/*.log` | evidence | n/a | Phase 30 `investigation/` | exact |
| pinned-defaults test (frozen names + defaults) | test | n/a | none (gear has no equivalent; 31-RESEARCH Pattern 1) | no analog |

## Pattern Assignments

### `src/spur/shaft_params.py` (model, validate-once)

**Analog:** `src/spur/params.py`. Import `_f`, `_extra` (and `when` if needed); do not edit `params.py` (`make gear.unchanged`, C-rules).

**Imports** (params.py:9-15):
```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.config import JsonDict
from pydantic_core import PydanticCustomError
```
Add `from .params import _extra, _f`.

**Frozen model + numeric field** (params.py:87-92):
```python
model_config = ConfigDict(frozen=True, json_schema_extra={"selectors": [_BORE_SHAPE]})  # shaft: frozen=True only
teeth: int = _f(19, 6, 200, title="Teeth", group="Teeth", step=1, help="Number of teeth.")
module: float = _f(1.75, 0.2, 10, title="Module", group="Teeth", unit="mm", step=0.05, help="...")
```
Shaft values: `reference_d` 25.0, `module` 1.25, `teeth` 18, `fit` "8f" plus the four solid-only fields (RESEARCH Pattern 1 table).

**Non-numeric field** (`fit`; `_f` takes numeric ge/le only; copy `root_shape`, params.py:115-121):
```python
root_shape: Literal["radial", "trochoid"] = Field(
    "radial", title="Root shape", description="...", json_schema_extra=_extra("Teeth"))
```
Use `Field("8f", pattern=r"^[1-9][0-9]?[a-z]$", max_length=3, title="Fit", description=..., json_schema_extra=_extra("Shaft"))`.

**Validator with local import** (params.py:256-265):
```python
@model_validator(mode="after")
def _feasible(self) -> GearParams:
    from .calc import check  # local import: calc only needs the attributes
    problems = check(self)
    if problems:
        fields = sorted({f for _, fs in problems for f in fs})
        raise PydanticCustomError(
            "infeasible", "{message}",
            {"message": " ".join(m for m, _ in problems), "fields": fields})
    return self
```
Shaft: `from .shaft_calc import check_shaft`. Same error type/ctx so Phase 33's 422 mapping is identical.

---

### `src/spur/shaft_calc.py` (service, transform)

**Analog:** `src/spur/calc.py`.

**Typing-only import of the params class** (calc.py:9-13): `from typing import TYPE_CHECKING, Literal` then `if TYPE_CHECKING:` import `ShaftParams`. Never import `calc` (C5), `model`, `logging`, `cadquery`.

**`check` return shape** (calc.py:628-647) is `list[tuple[str, tuple[str, ...]]]`, one `(sentence, field names)` per problem:
```python
errors.append(("Neighbouring teeth merge at the root; lower the profile shift.", ("profile_shift",)))
```
Shaft range refusal: same tuple shape, naming `reference_d`, `module`, `teeth` and the range -0.05..+0.45 with `X_EPS` on both edges.

**Typed result** (calc.py:927-960): frozen `BaseModel`, every key present, `None` means not applicable or not honestly computable (L08):
```python
class DerivedDimensions(BaseModel):
    model_config = ConfigDict(frozen=True)
    pitch_d: float = Field(description="Pitch circle diameter.", json_schema_extra={"unit": "mm"})
    root_thickness: float | None = Field(description="... null where ...", json_schema_extra={"unit": "mm"})
    ...
    warnings: tuple[str, ...]
```
`ShaftDimensions`: `form_d` always `None` with its sentence; `measure_over_pins` `None` for odd z (D-22: `pin_d` still prints); `warnings` tuple. The call ends `warnings=tuple(warnings)` (calc.py:1322 area).

---

### `src/spur/din5480.py` (utility, pure floats)

**Analog:** `src/spur/calc.py` maths. Copy, never import (C5).

**`inv`** (calc.py:117-119):
```python
def inv(a: float) -> float:
    """Involute function."""
    return math.tan(a) - a
```

**`_involute_angle`** (calc.py:1327-1340), copy verbatim:
```python
def _involute_angle(target: float) -> float:
    lo, hi = 1e-12, math.radians(89.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if inv(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
```

**Constants block with unit comment** (calc.py:110-114 `PROFILE_SHIFT_MAX = 1.0  # modules, ...`): trailing comment states unit and why. Here each constant carries an `ASSUMPTION` marker and clause slot (D-07).

**Pitfalls (31-RESEARCH 3, 6):**
- Formulas go in docstrings: ruff `ERA001` rejects comments shaped like assignments.
- Use `pin_d`, `m_re` as names (`N803`/`N806` reject `D`, `M_Re`).
- Never start a prose line with `from <gear-module>` or `import <name>` (test_seam regex belt, tests/test_seam.py:40-60).
- Rewrite the placeholder docstring (it promises clause citations that do not exist yet; Pitfall 9).
- No `TODO|FIXME|XXX|HACK|NotImplementedError` in `*.py`.

**Codec:** no analog. Use RESEARCH Pattern 4 (`repr`-based number printing, length bound, `re.split(r"[xX]", rest, maxsplit=3)`, per-token `re.fullmatch` with `[0-9]`, `DesignationError(ValueError)` quoting the token). D-21: spaces around `x` refused.

---

### `src/spur/parts.py` (docstring correction only)

Current lines 3-5 claim Phase 31 widens `Part` with a one-line edit. Keep `Part = GearParams` and the `from .params import GearParams` assignment untouched. Rewrite the docstring to say Phase 32 widens it, and that the change also touches `model._build_checked`, `model._write_export` and `records._gear_fields`. Keep the existing paragraph on why it is a plain assignment (UP040).

---

### `tests/shaft_oracle.py` (oracle, not collected)

**Analog:** `tests/trochoid_oracle.py` (layout lines 1-45).
- Module docstring explains: not collected (no `test_` prefix), imports nothing from `spur`, plain floats, why independence matters (L08), and what was measured.
- `from __future__ import annotations`, `import math` only.
- Private tuned constants at top: `_GRID = 2001`, `_GOLDEN = (math.sqrt(5) - 1) / 2`.
- Body: use the sketch in 31-RESEARCH "Oracle sketch" (parametric flank, base-thickness identity, pin tangency bisection with bracket to `r_a + D`). Add `contact_diameter`.
- Do not use `inv`, `_involute_angle` or the closed-form pin here.

---

### `tests/test_din5480.py`, `tests/test_shaft_calc.py`

**Analog:** `tests/test_calc.py`.
- Typed-result key coverage via class-level `model_fields` (test_calc.py:84, 1467-1470). Instance `model_fields` is deprecated and `filterwarnings = ["error"]` is on:
```python
got = {name for name in DerivedDimensions.model_fields
       if name != "warnings" and getattr(d, name) is not None}
```
- Frozen result test: `test_a_derived_dimensions_result_cannot_be_changed` (test_calc.py:79).
- `pytest.approx(abs=1e-9)` against the oracle; vendor rows `abs=1e-3` (Hexagon) and `abs=2e-4` (KISSsoft), each labelled "vendor cross-check, not the standard" with its URL (D-08).
- Epsilon cases (D-19): upper `(17.6, 0.8, 20)`, lower `(30, 2, 14)` and `(25, 1.25, 19)`. Each is seen red with `X_EPS = 0`.
- Guard (D-20): test `measure_over_pins` and the guard by direct calls with explicit `pin_d`. Say in the comment that it goes live in Phase 34.
- A test that changing `H_FP` moves only `d_f` (Pitfall 1).

### `tests/test_shaft_params.py`

**Analog:** `tests/test_calc.py:138` (parametrized refusal naming fields, `kw: dict[str, object], field: str`). The pinned test has no gear analog. Assert:
- `list(ShaftParams.model_fields)` equals the eight names in order.
- Defaults equal the literal dict.
- The default validates and its x is within `X_EPS` of 0.45 (D-19 wording).
- `hash(ShaftParams()) == hash(ShaftParams())`, and assignment raises (frozen).
- `fit` refusals: `f8`, a `\n` suffix, non-ASCII digits.
- The `infeasible` error carries `ctx` `message` and `fields`.

---

### `bench/RESULTS.md` (append)

**Analog:** the Phase 30 section (lines 6812-6900). Append a section "Shaft maths, parameters and designation (Phase 31)":
- A gate-delta table with fields Host, HEAD, UTC start/end, load before/after, make exit status, pytest result line, `/usr/bin/time -p`, coverage TOTAL line. Compare to `1369 passed`, `233.18 s`, `real 234.48`. Run-to-run spread is about 8 %, so say "inside the noise" and make no speed claim.
- A seen-red table with columns `| Plan | Test or step | Deliberate break | First failure line | Reverted |`. Rows: epsilon at 0, the shared `0.55` constant, the oracle sign flip, the parser accepting `\d`, and so on.
- Logs under `.planning/phases/31-.../investigation/`.

### Tech debt (D-14, RESEARCH recommends option 2, re-target)

**Analog:** `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md`. Format: H1, `Severity:`, `Status:`, `Date:`, `Source:`, `Related files:`, then `## Context`, `## Why it matters`, `## Next step`.
- Edit Context and Next step to say the docstring was corrected in Phase 31 and the trigger is Phase 32.
- Edit the INDEX row (`docs/tech_debt/INDEX.md:20`, trigger cell currently `Phase 31 widens \`Part\``) in the same commit.
- Split into a resolved file only with the sha problem in mind (the sha cannot be self-referenced).

### Decision log (only on D-09 / amended defaults)

**Analog:** the L46 entry at the tail of `docs/architecture/decision_log.md`. Style: bold lead-ins ("**When the shaft's contract freezes**"), a "**Reversibility.**" paragraph, a closing "Reason:" line.

## Shared Patterns

### L08: no number is better than a wrong number
**Source:** `calc.DerivedDimensions` docstring (calc.py:927-935).
**Apply to:** `shaft_calc`, the guard, d_Ff (always null), odd-z M_Re (null until anchored).

### Validate once, local import
**Source:** params.py:256-265.
**Apply to:** `ShaftParams._feasible` only. Downstream code trusts the model.

### Import contracts C1-C5
**Source:** `pyproject.toml:226-290`, `tests/test_seam.py:40-60` (regex belt).
**Apply to:** all three shaft modules. Run `make lint-imports` and expect `Contracts: 10 kept, 0 broken.`. `calc.py`, `params.py`, `tests/regression/`, `ci.yml` and `requirements.txt` are untouched (`make gear.unchanged`).

### Seen-red once
**Source:** the Phase 30 table in `bench/RESULTS.md`.
**Apply to:** every guard test.

### Checkpoint
D-06 `checkpoint:human-action` follows the build tasks. Present the prediction table from 31-RESEARCH "Reproduction table". Constants stay `ASSUMPTION` until the human confirms them by clause.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| designation codec (inside `din5480.py`) | utility | transform/parse | No parser exists in the repo; use RESEARCH Pattern 4. |
| pinned names-and-defaults test | test | n/a | Gear has none; deferred from Phase 30. Use RESEARCH Pattern 1. |

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `bench/RESULTS.md`, `docs/tech_debt/`, `docs/architecture/decision_log.md`
**Files scanned:** about 14 (targeted reads; `calc.py` and `params.py` by line range)
**Pattern extraction date:** 2026-10-24
