# Phase 18: Trochoid Maths, Proved - Pattern Map

**Mapped:** 2026-10-07
**Files analyzed:** 7 (1 modified source, 2 new test files, 1 new bench script, 2 modified docs/bench records, 1 reused fixture test)
**Analogs found:** 7 / 7 (all paths verified git-tracked with `git ls-files`; no gitignored mirror paths)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/spur/calc.py` (`Cutter` + `cutter()`) | model (frozen dataclass) + utility | transform | `calc.py` `Profile` / `profile()` lines 70-98 | exact |
| `src/spur/calc.py` (`RootCurve`, `RootMode`) | model (frozen dataclass) | transform | `calc.py` `Profile` lines 70-90 (+ `params.py:91` `Literal` field) | exact |
| `src/spur/calc.py` (`trochoid_root`, junction bisections) | utility | transform | `calc.py` `_involute_angle` lines 1158-1171 + `centre_distance` 1174-1191 | role-match |
| `src/spur/calc.py` (`root_mode`, one warning function, closed-form onset / `x_min`) | utility | request-response | `calc.py` `root_fillet` 224-228, `derive()` ignored-field sentences 1014-1019 / 1063-1070 | role-match |
| `tests/test_trochoid.py` | test | transform (oracle, sweep) | `tests/test_calc.py` centre-distance oracle 574-596 and 15-row boundary test ~747 | exact |
| `tests/trochoid_oracle.py` | test helper (not collected) | transform | `tests/composition.py` | exact |
| `bench/trochoid_step.py` | utility (bench) | batch | `bench/latency.py` (header, `machine_facts`, not-in-verify note) | role-match |
| `bench/RESULTS.md` (new section) | docs/record | n/a | `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)" lines 2138-2166 | exact |
| `docs/architecture/gear-maths/implementation.md` (layout rows) | docs | n/a | same file, `## Layout` table lines 7-39 | exact |
| fixture guard (all 44 records read `radial`) | test | CRUD (replay) | `tests/regression/test_pre_v0_2.py` | role-match |

Placement note: RESEARCH recommends a sibling `tests/test_trochoid.py`. `make test.fast` ignores only four named files, so it runs at commit with no Makefile change. Tests import helpers from `tests/` by bare name (`from composition import ...`, `tests/test_calc.py` line 7), so `from trochoid_oracle import ...` works the same way.

## Pattern Assignments

### `src/spur/calc.py` : `Cutter` + `cutter(p, rho)` (model/utility, transform)

**Analog:** `src/spur/calc.py` `Profile` + `profile()` (lines 70-98)

**Imports already in file** (lines 5-13; add nothing, pure stdlib `math`; `Literal` needs `from typing import TYPE_CHECKING, Literal`):
```python
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING
...
if TYPE_CHECKING:
    from .params import GearParams
```

**Frozen-dataclass shape with unit comments** (lines 70-80):
```python
@dataclass(frozen=True)
class Profile:
    z: int
    m: float
    alpha: float    # pressure angle, radians
    r: float        # pitch radius
    rb: float       # base radius
    ra: float       # tip radius
    rf: float       # root radius
    psi_p: float    # half tooth-thickness angle at the pitch circle
```

**The expressions the cutter must read, not copy** (lines 93-98). `d` must be the same expression as `rf`'s, and the first curve point must use `Profile.rf` itself (RESEARCH Pattern 1: `R(0) - rf = 0.0` only if it is the same float):
```python
def profile(p: GearParams, backlash: float | None = None) -> Profile:
    a = math.radians(p.pressure_angle)
    m, z, x = p.module, p.teeth, p.profile_shift
    bl = p.backlash if backlash is None else backlash
    r = m * z / 2
    s = m * (math.pi / 2 + 2 * x * math.tan(a)) - bl
    return Profile(z=z, m=m, alpha=a, r=r, rb=r * math.cos(a), ra=r + m * (1 + x),
                   rf=r - m * (1.25 - x), psi_p=s / (2 * r))
```
Copy: signature style `f(p: GearParams, ...)`, `m, z, x = p.module, p.teeth, p.profile_shift`, `s = ...` with the backlash subtraction. New: `d = m * (1.25 - x)`, `e = math.pi * m - s`, `w_c = rho - d`, `a = e / 2 + w_c * math.tan(al) - rho / math.cos(al)` (RESEARCH Pattern 1). Cap: `math.floor(cap * 1000) / 1000`, not `round()` (F3). Lint: name `w_c`, never `wC` (ruff `N`); a comment shaped like an assignment trips `ERA`.

**Constant-with-measurement comment convention** (lines 15-62, e.g. `ROOT_CONTACT`, `TIP_CHAMFER_MARGIN`, `HEX_CELL_CAP`): the D-09 epsilon (`1e-4 * rb`, relative to `rb`) goes at module level in this shape. A comment that carries date, host, the two bracketing measurements, and the headroom. Quote of the style:
```python
TIP_CHAMFER_MARGIN = 0.001  # mm, how far inside the start of the involute spline the
# tip chamfer's footprint stops. Measured 2026-09-28 (bench/RESULTS.md "Tooth-tip
# chamfer spike"): a 20-step bisection on six configurations ...
```

---

### `src/spur/calc.py` : `RootCurve`, `RootMode` result types (model, transform)

**Analog:** `Profile` above for `@dataclass(frozen=True)`. `Literal` field analog: `src/spur/params.py:91` (`recess_sides: Literal["both", "top", "bottom", "none"] = Field(`). `RootCurve` holds a tuple of `(radius, half_angle)` pairs (immutable: tuple, not list; `derive()` already returns `warnings=tuple(warnings)`, line ~1150). `RootMode`: `mode: Literal["radial", "trochoid"]` plus `reason: str` (D-03; the reason set should be a `Literal` of the named strings so Phase 19 and the tests share it).

---

### `src/spur/calc.py` : `trochoid_root(cutter) -> RootCurve | None` (utility, transform)

**Analog:** `_involute_angle` and its caller `centre_distance` (lines 1158-1191)

**Sign-only bisection, fixed bracket, 60 halvings, no Newton** (lines 1158-1171):
```python
def _involute_angle(target: float) -> float:
    """Inverse of inv() on (0, pi/2): the angle whose involute function is `target`.

    Bisection rather than Newton: inv is monotonic here, 60 halvings reach full double
    precision, and there is no starting guess that can send it outside the bracket.
    """
    lo, hi = 1e-12, math.radians(89.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if inv(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
```
The crossing needs two of these (bracket `R_E(beta) = rb`, then `g(beta) = 0` on `[beta_b, beta_end]`). RESEARCH Code Examples gives a `bisect(f, lo, hi, n=60)` variant that takes the sign from `f(lo)`; write it as a private helper next to `_involute_angle` with the same docstring register (why bisection, why 60).

**Honest-refusal shape** (`centre_distance`, lines 1174-1191): returns `float | None`; the docstring says why no number is the honest answer ("the number is not merely imprecise, it does not exist"), and the guard precedes the solve:
```python
    if not 0 < target < inv(math.radians(89.0)):
        return None
```
Copy the "guard, then solve, `None` means numerical failure the closed form did not predict" shape (D-10). Add the post-solve strictly-increasing-R guard and return `None` if it fails (RESEARCH Pattern 3). `half_angle` is only called at `R >= rb` (its `min(1.0, rb/R)` absorbs a last-ulp excursion, line 88-89).

**Envelope and junction formulas to implement:** RESEARCH Pattern 2 (`E(beta)` in contact-normal angle, sampling uniform in `s = tan(beta)`) and Pattern 3 (tangent: no root-find, `R_join = sqrt(rb^2 + xi^2)`; crossing: two bisections). Not the `E(phi) = C + rho(C-I)/|C-I|` form (wrong for `w_c >= 0`, F4).

---

### `src/spur/calc.py` : `root_mode(p, pr, *, requested="radial", rho=...)` and the warning function (utility, request-response)

**Analog for the shape:** `root_fillet(p)` (lines 224-228) -- a small public function over `GearParams` that returns the value actually used after capping:
```python
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```
Contrast, on purpose: this rounds to nearest. The new ρ cap must floor (`math.floor(cap*1000)/1000`), see F3 / Pitfall 2.

**Analog for warning sentences** (generated in one calc place, captured in tests, never typed): the ignored-field shape in `derive()` (lines 1063-1070) and the cap-and-warn shape (lines 1004-1006):
```python
    rfil = root_fillet(p)
    if rfil < p.root_fillet:
        warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```
```python
        if ignored:
            warnings.append(
                f"No spoke arms with spoke_count 0: {_listed(ignored)} "
                f"{'are' if len(ignored) > 1 else 'is'} ignored.")
```
Copy: sentences built in calc with f-strings and `:.3f` / `:g` formats; the "... is ignored." tail for the `rb <= rf` request (D-02); the "capped value at 3 dp" naming for the ρ cap. One function keyed on the reason (D-10); `derive()` is NOT edited this phase (SC5), including the stale 11.5 usec docstring at lines 955-956, which is a doc correction only if the plan decides it is inside `calc.py` (it is, and allowed: `calc.py` is the one file this phase may touch).

**Comparison rule to copy** (`derive()` lines ~1007-1010 comment): compare at the printed 3 dp, never the raw float, so "0.000 mm" never prints.

**Cheap-to-expensive order** (RESEARCH Pattern 5 / F9, undercut implies `rb > rf`): requested -> `rb <= rf` -> `a(rho=0) < 0` (tip land gone) -> run generator for "tooth severed" (`min half_angle <= 0`, D-17) -> trochoid. The three "undercut"s stay separate: `teeth < z_min` (the shipped line `z_min = 2 * (1 - p.profile_shift) / math.sin(pr.alpha) ** 2`, line 1007, untouched), `rb > rf`, the cutter's form circle.

---

### `tests/test_trochoid.py` (test, transform)

**Analog 1:** `tests/test_calc.py:574-596`, the independent oracle inside a test, sharing no code with the implementation:
```python
def test_centre_distance_matches_an_independent_solver() -> None:
    def bisect(p: GearParams, z2: int) -> float | None:
        a = math.radians(p.pressure_angle)
        target = inv(a) + 2 * math.tan(a) * p.profile_shift / (p.teeth + z2)
        if target <= 0:
            return None
        lo, hi = 1e-12, math.radians(89.0)
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inv(mid) < target else (lo, mid)
        return p.module * (p.teeth + z2) / 2 * math.cos(a) / math.cos((lo + hi) / 2)

    checked = 0
    for teeth in (6, 12, 19, 60, 200):
        ...
                try:
                    p = GearParams(teeth=teeth, pressure_angle=pa, profile_shift=x,
                                   bore_d=0, bore_flat=0, bore_chamfer=0,
                                   recess_sides="none")
                except ValidationError:
                    continue  # not a gear; centre distance is moot
                ...
                    assert (got is None) == (expected is None), (teeth, pa, x, z2)
                    if expected is not None:
                        assert got == pytest.approx(expected, rel=1e-12)
```
Copy: grid built in the test, `GearParams` invalid rows `continue`d (x = -1 is rejected by the field; use -0.6, F5), 200 halvings in the oracle versus 60 in the implementation, comparison with `pytest.approx`. For the sweep, tally outcomes by reason and assert the counts, not just absence of failure (Pitfall 1).

**Analog 2:** `tests/test_calc.py` ~lines 735-775, the boundary table: `@pytest.mark.parametrize` with `pytest.param(..., id=...)` rows one field step either side of a crossing, strings captured from the function, docstring recording the capture date and kernel pair:
```python
def test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle(
        kw: dict[str, object], fillet: float, height: float, warning: str | None) -> None:
    """REQ-root-lead-in-warned / D-01 to D-03: ... Every expected string was captured
    from derive() on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1's pinned code, 2026-10-02,
    never typed ... The rows are ... one field step either side of the crossing ..."""
    p = GearParams.model_validate(kw)
    ...
    assert root_fillet(p) == pytest.approx(fillet)
```
Use for: tooth step either side (17/18 at 20 deg rho* 0.38; z 41/42 at 20 deg x 0), field step either side (tip land: 32.0/32.5 at backlash 0, 33.0/33.5 at default; tuned shift z 10, 20 deg, x 0.40/0.45), cap (m 0.5, 15 deg, backlash 0 floors to 0.293, rounds to refuse 0.294). Warning text: call the calc warning function, never type the string (L33).

**Analog 3 (bar docstring):** `tests/test_model.py:1153` `_filleted_spoke_volume` -- closed form in the test module, never calls the production helper; the docstring records the date, kernel pair and measured gap, and the assertion bar sits at `abs=1e-9`:
```python
    It re-derives every centre and tangent point in this polar form and never touches
    model._fillet_corner's quadratic and root choice, so a wrong root, sign or side
    there disagrees with this function instead of moving both sides together (L08).
    Measured 2026-10-03 against the built solid (cadquery 2.8.0 / cadquery-ocp
    7.9.3.1.1): SPOKES12 + spoke_fillet 1 agrees to 2.73e-12 mm3.
```
Copy the docstring discipline for T1/T2/T3/T4 bars: two recorded numbers, headroom stated beside the bar (>= 10x, else the human; T4's 1.4x is the one pre-accepted exception per D-15). T3/T4 constants recorded as literals with a provenance docstring (source file, commit `4cc4b1a233c232e15c3fdfb8a35909aa0d828796`, GPL-3.0 for freecad.gears; Zhang AGMA 18FTM02 Table 7 example 7 with the inferred diametral pitch 8 noted). Nothing fetched at test time, nothing imported.

**Import block convention** (`tests/test_calc.py` lines 1-50): stdlib, `pytest`, bare-name helper import from `tests/` (`from composition import ...`), `pydantic.ValidationError`, then `from spur.calc import (...)` one name per line sorted (ruff `I`).

**Config traps:** `filterwarnings = ["error", ...]` and `--strict-markers` (a stray warning fails); `fail_under = 96` with `branch = true`, so every `None` / refusal / epsilon arm in `calc.py` needs a test that reaches it (hand-built out-of-box `Cutter` with `a < 0`; a `xi` inside epsilon built by choosing x). Per-file ignore `"tests/*" = ["ARG001"]` (`pyproject.toml:78-80`).

---

### `tests/trochoid_oracle.py` (test helper, not collected, transform)

**Analog:** `tests/composition.py` (lines 1-40)

**Header and no-self-reference rule** (lines 1-11):
```python
"""The family and refusal tables shared by `tests/test_calc.py` ...

Not collected: no `test_` prefix (`tests/regression/corpus.py`'s precedent for a shared,
non-collected data module under `tests/`). Every table here is written out by hand from
the planning probe -- never computed by calling `spur.calc`'s own functions (the code
under test) to build its own expectation, because a tautological test is a plausible
wrong number (L08, CLAUDE.md).
"""

from __future__ import annotations
```
Copy: `from __future__ import annotations`, a module docstring stating "not collected" and "shares no code with `spur.calc`". The oracle must build the cutter from plain definitions (half-width `e/2`, flank angle, flat tip, ρ), not from `E(beta)`, and must include neighbouring cutter teeth `k in {-1, 0, +1}` or it reads 0 on severed teeth (RESEARCH Pattern 6). It may import `GearParams` fields' raw numbers but should not import `spur.calc.cutter`/`profile`; pass plain floats in.

---

### `bench/trochoid_step.py` (bench utility, batch)

**Analog:** `bench/latency.py`

**Header / "not part of make verify"** (lines 1-12) and import block (lines 14-28):
```python
"""Does `/api/health` stay fast while a build is in flight?
...
Not part of `make verify` (D-16): it needs a running service and minutes, and a latency
assertion on shared hardware would flap until someone stopped believing it. Run it with
`make bench.latency` after `make serve` is up.
"""

from __future__ import annotations

import argparse
...
from bench import machine_facts
```
Copy: docstring stating what is measured and why it is not gated; `from bench import machine_facts` (`bench/__init__.py:19` returns `"12 CPUs, arm64, 32.0 GiB RAM"`), printed with every row. `argparse` main, run as `.venv/bin/python -m bench.trochoid_step` (the `-m` form puts the repo root on `sys.path`, `tests/test_bench.py` header). This script imports `model._fillet_corner` (cadquery), which is why it lives in `bench/` and not in `calc` or the kernel-free tests. Also holds the D-13 fallback full-grid T2 if the gate sweep prices over about 2 s. If `tests/test_bench.py` pins bench helpers by pure predicates (it does for the existing scripts), add a pure test for any predicate this script introduces (the comparison rule for D-05, e.g. "within +-25% of 0.14 m").

Ranking note: other bench scripts (`bench/honeycomb_spike.py`, `bench/tip_chamfer_spike.py`) are spike-style single-purpose scripts that write a `bench/RESULTS.md` section; check one of them for the table-printing helper before writing a new one (not read here, early stop).

---

### `bench/RESULTS.md` (new section "Trochoid maths (Phase 18)")

**Analog:** the "Composition pass test cost (Phase 12, D-10)" section, lines 2138-2166, and the Phase 17 section's `#### Host state` (lines 2867-2880)

**Section shape:** `## <Title> (Phase N, D-xx)` with a one-paragraph statement of what was measured and the agreed line, then `### Host state`, then method and tables. Host-state bullet list to copy:
```markdown
### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-09-30
- Phase-start HEAD ...
- Load averages (1-minute, `sysctl -n vm.loadavg`), read immediately before each run
  started building: ...; no quiet bar is required for this measurement
```
Add cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1 (Phase 17 block lists it) and HEAD sha. Content to record: epsilon bracket, cap reconciliation, junction bar, sweep wall time at `-n 8`, per-call costs (`derive`, `root_mode`, `trochoid_root`, best of 5 via `.venv/bin/python -m timeit`), and two step tables (17/18 teeth at 20 deg; `rb = rf` crossover z 41/42), each row stating rho and the shipped fillet (Pattern 8).

---

### `docs/architecture/gear-maths/implementation.md` (layout rows)

**Analog:** the `## Layout` table (lines 7-39). One row per new piece, same two-column `| Piece | Does |` form, same order as the file (constants, then functions near their neighbours). Existing row shapes to copy:
```markdown
| `Profile` + `profile(p)` | radii (`r`, `rb`, `ra`, `rf`), pitch half-angle, `r_start`, `half_angle(rho)` |
| `_involute_angle(target)` | bisection inverse of `inv` |
| `centre_distance(p, z2, x2=0)` | working centre distance, or `None` |
```
Also update the sentence at line 5 ("two classes, `Profile` and the frozen `DerivedDimensions`") because the new dataclasses make it false. `strategy.md` and `README.md` are NOT edited (CONTEXT).

---

### Fixture guard: every pre-v0.2 record reads `radial` / "not requested"

**Analog:** `tests/regression/test_pre_v0_2.py` and `tests/regression/corpus.py` (`cases()`), `tests/regression/capture.py` (`FIXTURE`, `Record`). Do not touch `tests/regression/pre_v0_2.json` (SC5: `git diff --exit-code tests/regression/pre_v0_2.json` after every task). The 44-record mode check in `test_trochoid.py` can iterate `corpus.cases()` the way the `_RECORDS` parametrisation does (lines 33-37), and call `root_mode(p, profile(p))` with defaults; add no new record to the fixture. Note `tests/regression/` is imported by bare name in its own tests (`from capture import ...`); check how its `conftest`/pythonpath exposes `corpus` before importing it from `tests/test_trochoid.py`, or hand-write the parameter sets instead.

## Shared Patterns

### One place decides, tests capture the text
**Source:** `tests/test_calc.py` ~line 747 docstring; `src/spur/calc.py` `derive()` warnings.
**Apply to:** the warning function, every refusal reason, every test that checks a sentence. Strings are produced by calc and read back by the test (L33); the same reason string is the `RootMode.reason` Phase 19 hangs `derive()` sentences on.

### No number is better than a wrong number (L08)
**Source:** `calc.py` `centre_distance` (lines 1174-1191, returns `None`) and `derive()`'s "Compared at the 3 dp it prints" comment (lines ~1007-1010).
**Apply to:** `trochoid_root` (`None` on bracket failure, non-monotone R), `root_mode` (named refusal, analytic root fallback), the ρ cap (floored once, used and printed as the same number). Never clip to the centreline or hide a loop (D-11).

### Comments carry the measurement
**Source:** `calc.py` lines 15-62 constants block.
**Apply to:** the epsilon constant, any tolerance, every bar in the tests. Date, host load, kernel pair, the two bracketing measurements, the headroom (CODING_VALUES / CLAUDE.md).

### Pure stdlib `math`, `calc.py` never imports cadquery
**Source:** `calc.py` module docstring (lines 1-2) and the import-linter contract. `grep -rnE 'numpy|scipy' src/spur` must stay empty; `requirements.txt` stays at 31 pins; `git diff --name-only <phase base> -- src/spur` names only `calc.py`.

### Boundary checks after every task (SC5)
`git diff --exit-code tests/regression/pre_v0_2.json`; `git diff --name-only 807fd2d -- src/spur | grep -v '^src/spur/calc.py$'` prints nothing; `grep -rnE 'numpy|scipy' src/spur` prints nothing; `grep -c '==' requirements.txt` prints 31. Commit-time gate is `make verify.fast` (L36); `make verify` by hand before push.

## No Analog Found

| File / piece | Role | Data Flow | Reason |
|--------------|------|-----------|--------|
| Swept-cutter signed-distance oracle (inside `tests/trochoid_oracle.py`) | test helper | transform | No geometric oracle exists; existing oracles are scalar closed forms. Use RESEARCH Pattern 6 (rounded-trapezoid signed distance, golden-section refinement, neighbours k in {-1,0,+1}). The structural wrapper (header, no shared code) still comes from `tests/composition.py`. |
| Envelope `E(beta)` and the crossing solve | utility | transform | No curve-generation code in `calc`; formulas come from RESEARCH Patterns 2-4 and the prototype in "Code Examples" (adapt names to ruff `N`/`ERA`). Only the bisection style has an in-repo analog. |
| T3 / T4 recorded external constants | test data | n/a | No existing externally sourced reference in the tests; provenance docstring style follows `test_model.py` `_filleted_spoke_volume` (date, kernel pair) plus the source/commit/licence fields from CONTEXT D-15 and RESEARCH Pattern 7. |
| `Literal`-typed result in `calc.py` | model | n/a | `calc.py` uses no `Literal` yet; precedent is `params.py:10,91` and `cli.py:12,47`. Add `Literal` to the `typing` import. |

## Metadata

**Analog search scope:** `src/spur/calc.py`, `src/spur/params.py`, `tests/` (test_calc, test_model, composition, conftest, regression), `bench/` (latency, `__init__`, RESULTS, README, test_bench header), `docs/architecture/gear-maths/implementation.md`, `pyproject.toml` lint/test config.
**Tracked-source gate:** `git ls-files` printed all of `src/spur/calc.py`, `tests/test_calc.py`, `tests/test_model.py`, `tests/composition.py`, `bench/RESULTS.md`, `docs/architecture/gear-maths/implementation.md` (6 of 6); `bench/*.py` and `tests/regression/*` also appear in the tracked listing. The planning dir `18-VALIDATION.md` is tracked as well. No mirror paths named.
**Files scanned:** ~14 (line ranges quoted above; large `tests/test_calc.py` and `bench/RESULTS.md` read by range only).
**Pattern extraction date:** 2026-10-07
