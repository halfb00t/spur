# Phase 7: Foundation — Generalized Edge Selection + Regression Fixture - Pattern Map

**Mapped:** 2026-09-26
**Files analyzed:** 8 (2 modified source, 6 new)
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/spur/calc.py` (new `bore_rim_limit(p)`) | utility (pure-maths function) | transform | `src/spur/calc.py::bore_radius`/`recess_radii` | exact — same file, same role |
| `src/spur/model.py` (`_bore_rim_edges` bound + guard) | model / selector (kernel geometry query) | transform | `src/spur/model.py::_cut_bore` calling `bore_radius` | exact — same function, minimal diff |
| `src/spur/model.py` (`_groove_floor_edges` guard) | model / selector | transform | `src/spur/model.py::_cut_face_recesses` calling `_groove_floor_edges` | exact — same function |
| `src/spur/model.py` (named slack constant) | config (module-level constant) | n/a | `src/spur/model.py::TOL` | exact — same file, same pattern (named tolerance + comment) |
| `tests/regression/corpus.py` (new) | utility (test fixture data) | batch | `bench/corpus.py` | role-match — deterministic, source-tagged corpus, different domain (pre-v0.2 sets vs mem sweep) |
| `tests/regression/pre_v0_2.json` (new) | config (data fixture) | file-I/O | none in-tree (new pattern); layout follows D-01/D-04 | no analog — new category, see below |
| `tests/test_regression.py` (new) | test | request-response (build + assert) | `tests/test_model.py::test_builds_one_valid_solid` + `tests/test_calc.py::test_default_dimensions` | role-match — parametrized build/derive assertions |
| `scripts/regen_fixture.py` or `tests/regression/regen.py` (new, Claude's discretion on path) | utility (script behind a `make` target) | batch | `scripts/pr_land.py` / `bench/memory.py` `main()` shape; `Makefile`'s `bench.latency`/`lock` targets | role-match — argparse-free or argparse `main()` + `if __name__ == "__main__"`, invoked via a bare `$(PY) -m` target |
| `tests/test_model.py` (selector count tests + zero-edge `BuildError` tests) | test | request-response | `tests/test_model.py::test_builds_one_valid_solid` (matrix shape); `tests/test_api.py`/`tests/test_pool.py`'s `BuildError("D-flat too small for this bore")` parametrize rows (message-matching precedent) | exact — same test module, same idioms |
| `docs/architecture/decision_log.md` (possible L26) | config (append-only doc) | n/a | `docs/architecture/decision_log.md::L24` (most recent full entry: Decision / Why / Rejected / Reversibility / Reason) | exact — same file, same section shape |

## Pattern Assignments

### `src/spur/calc.py` — new `bore_rim_limit(p)` (utility, transform)

**Analog:** `src/spur/calc.py::bore_radius` (line 57) and `recess_radii` (lines 61–81)

**Imports pattern** (lines 1–13, already present, nothing new to add):
```python
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .params import GearParams
```
`calc.py` never imports `cadquery`/`OCP` (import-linter contract "The gear maths stays
free of the CAD kernel", `pyproject.toml` lines 141–155) — `bore_rim_limit` must stay a
plain function of `p`'s fields, no kernel types in or out.

**Core pattern — a bound computed in calc.py, consumed in model.py** (`bore_radius`,
lines 57–58):
```python
def bore_radius(p: GearParams) -> float:
    return (p.bore_d + p.bore_clearance) / 2 if p.bore_d > 0 else 0.0
```
`recess_radii` (lines 61–81) is the richer version of the same shape — a docstring that
states the geometric fact plainly, then the body, with a comment on each line that earns
its keep (`# clear of the hub wall`, `# clear of the tooth rim`). D-18 fixes
`bore_rim_limit(p)`'s contract as "the exact geometric bound, no slack" — round/D-flat
both reduce to `bore_radius(p)` (the D-flat rim is a strict subset of the circle) — so
the function is closer to `bore_radius`'s one-line shape than to `recess_radii`'s capping
logic. No kernel tolerance belongs here (D-18: "`calc.py` knows no kernel tolerances");
that is `model.py`'s named slack constant, not this function's job.

**Docstring convention** — every derived-bound function states *why* the bound is what
it is, e.g. `recess_radii`'s "The requested width is a wish, not a constraint" (line
68). `bore_rim_limit`'s docstring should say why round/D-flat both collapse to
`bore_radius(p)` (the docstring the research phase already drafted, Q2 in
`.planning/research/ARCHITECTURE.md`), and that Phase 8 adds a hex case here, not by
widening this one.

---

### `src/spur/model.py` — `_bore_rim_edges`'s bound, `_cut_bore`'s call, the slack constant (model/selector, transform)

**Analog:** `src/spur/model.py::_cut_bore` (lines 180–197), `_bore_rim_edges` (lines
213–232), `TOL` (line 41)

**Imports pattern** (lines 28–30, current):
```python
from .build_errors import BuildError
from .calc import Profile, bore_radius, profile, recess_fillet, recess_radii, root_fillet
from .params import GearParams
```
Adding `bore_rim_limit` joins this same `from .calc import ...` line (alphabetical,
matching `ruff`'s `I` import-sort rule already enforced).

**The constant to copy — `TOL`'s comment shape** (line 41):
```python
TOL = 1e-6              # mm, for matching kernel geometry back to the numbers we asked for
```
D-18's new slack constant sits beside it, same file, same comment convention: name, mm,
one sentence stating *why this value* — "must exceed the kernel's post-boolean vertex
tolerances and stay far below `MIN_WALL` (0.4 mm)" is the reason already supplied by
CONTEXT.md; the plan only needs to pick the name (e.g. `BORE_RIM_SLACK`) and place the
comment the same way `TOL` does.

**Core pattern — the inline `lim` today** (lines 213–232, the exact block D-18 replaces
one line of):
```python
def _bore_rim_edges(solid: cq.Shape, r_bore: float, face_width: float) -> list[cq.Edge]:
    """The bore opening on the two end faces.

    Selected by position, not by type: a D-bore rim is an arc plus a straight line. The
    only other edges on an end face belong to a recess, and recess_radii() keeps at
    least MIN_WALL plus the chamfer between that and the bore, so a radius test
    separates them.
    """
    lim = r_bore + 0.01

    def on_rim(e: cq.Edge) -> bool:
        a, b = e.startPoint(), e.endPoint()
        if abs(a.z - b.z) > TOL or TOL < a.z < face_width - TOL:
            return False
        if max(math.hypot(a.x, a.y), math.hypot(b.x, b.y)) > lim:
            return False
        return all(math.hypot(q.x, q.y) < lim
                   for q in (e.positionAt(s / 4) for s in range(1, 4)))

    return [e for e in solid.Edges() if on_rim(e)]
```
`lim = r_bore + 0.01` becomes `lim = bore_rim_limit(p) + BORE_RIM_SLACK` (or the limit is
computed at the `_cut_bore` call site and passed in — CONTEXT.md D-18 leaves the
signature to the planner). The `on_rim` closure and the `solid.Edges()` filter are
untouched: D-18 only changes where the bound value comes from, not the selection logic
("the only change is where `lim` comes from", `<code_context>` Reusable Assets).

**Call site to update** (`_cut_bore`, lines 180–197, the chamfer call at 194–195):
```python
def _cut_bore(solid: cq.Shape, p: GearParams) -> cq.Shape:
    """Round or D-shaped bore, chamfered on both rims."""
    if p.bore_d <= 0:
        return solid
    r_bore = bore_radius(p)
    hole = cq.Workplane("XY").circle(r_bore).extrude(p.face_width)
    if p.bore_flat > 0:
        flat = p.bore_flat + p.bore_clearance          # flat to opposite side
        keep = cq.Workplane("XY").center(flat - 2 * r_bore, 0).rect(2 * r_bore, 2 * r_bore + 2)
        hole = hole.intersect(keep.extrude(p.face_width))
    solid = solid.cut(hole.val())  # type: ignore[arg-type]  # .val() is typed as a 4-way union
    if p.bore_chamfer > 0:
        solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
            p.bore_chamfer, None, _bore_rim_edges(solid, r_bore, p.face_width))
    return solid
```
`_bore_rim_edges(solid, r_bore, p.face_width)` is the call the planner decides to change
to `_bore_rim_edges(solid, p, p.face_width)` (passing `p`) or to keep passing a
pre-computed limit — "takes whatever the planner prefers (`p` or the limit)" (D-18).

**Guard pattern to add (D-15) — model this on the existing invalid-solid raise**
(`_build`, lines 237–246):
```python
def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]
```
Same shape for both new guards: compute the edge list, `if not edges: raise
BuildError("...")`, before the `.chamfer()`/`.fillet()` call that would otherwise accept
an empty list silently (research Q2). D-15's message must name the selector/feature and
say it is a modelling defect, distinct from `_build_checked`'s catch-all wording ("try
smaller fillets or chamfers", lines 253–256) — this is D-15's explicit rejection, so the
new message must read differently from that one.

**Error routing — no new plumbing needed** (`build_errors.py`, full file, 24 lines):
```python
class BuildError(RuntimeError):
    """The CAD kernel could not produce a valid solid for these parameters."""
```
Routed already: `src/spur/app.py:414` (`except BuildError as exc:` → `HTTPException(422,
...)`) and `src/spur/cli.py:111` (`except BuildError as exc:` → `SystemExit`). D-15
rides this without touching either file.

---

### `tests/regression/corpus.py` (new) — utility, batch

**Analog:** `bench/corpus.py` (full file, 25 lines)
```python
"""L07's own memory-sweep corpus: 40 distinct 160-199 tooth gears.
...
Do not narrow, shorten or re-pick this corpus to make a ceiling look better: a different
workload produces a number that cannot be compared with the one on record, which
defeats the entire point of measuring (02-02-PLAN.md prohibitions).
"""

from __future__ import annotations


def corpus() -> list[dict[str, object]]:
    """40 distinct gears, tooth counts 160 through 199 inclusive, one per tooth count.
    ...
    """
    return [{"teeth": teeth} for teeth in range(160, 200)]
```
Copy: the module docstring's "do not narrow/re-pick" stance (D-05's "closed set... never
tracks later test edits" is this project's second instance of that same rule, and
CONTEXT.md's Claude's Discretion item explicitly names `bench/corpus.py`'s docstring
stance as what the new module's docstring should carry); a single public function
returning a list of dict-like records, no I/O, no kernel import. Differs from
`bench/corpus.py` in D-05's required shape: each entry needs a **source tag** (string
key) alongside the params, e.g. a `list[tuple[str, dict[str, object]]]` or a
`dict[str, dict[str, object]]` keyed by tag (Claude's Discretion: "source tag as the key
is the obvious choice"), and dedup by `GearParams` equality before emitting — `GearParams`
is frozen (`model_config = ConfigDict(frozen=True)`, `src/spur/params.py:29`) so
`set[GearParams]` or a dict keyed by the built model works directly; `model_validate(kw)`
(pydantic v2, already the pattern `tests/test_calc.py:159` and `test_model.py:28` use for
building a `GearParams` from a raw dict) is the way to turn each hand-copied literal back
into one for the dedup check.

**Source-tag literals to copy verbatim into the corpus** (already-tracked lines, cite the
tag exactly as CONTEXT.md D-05 names it):
- `tests/test_model.py:16-25` — the nine `kw` dicts under
  `@pytest.mark.parametrize("kw", [...])` above `test_builds_one_valid_solid` (line 28);
  tag as `test_model.py::test_builds_one_valid_solid[<index or repr>]`.
- `tests/test_calc.py` inline `GearParams(...)` calls — lines 20, 42, 52, 63, 70, 76, 78,
  84, 104, 114, 121, 128, 136, 142, 148 (grep `GearParams(` for the exact list); the
  mate-teeth pairs at `tests/test_calc.py:154-157`
  (`test_impossible_pairs_have_no_centre_distance`'s two `(kw, mate)` rows) are D-07's
  "sets that appear with a mate" — pin `mate_teeth`/`centre_distance` including the
  `None` + warning case, no extra `build()`.
- `tests/test_cli.py:16,51,60,69,81,85,94` — `cli.main([...])` argument lists (D-09
  explicitly includes these).
- `tests/test_api.py` `params=` dicts — D-09 quotes "up to 29", many info-only or 422 (422
  cases excluded by construction); dedupe drops the repeats (`teeth=21` appears at least
  8 times across the file).
- `tests/test_pool.py` — teeth 21, 22, 43, 44 sets (lines 76-410 area).
- `README.md:106-108,126` — the four examples: `spur export -o gear.step` (defaults),
  `--teeth 24 --module 1 --pressure-angle 20 --bore-flat 0`, `spur info --teeth 19
  --mate-teeth 40`, `curl .../api/model.step?teeth=19&module=1.75&pressure_angle=25`.

**Explicitly excluded (D-08/D-09) — do not add these:**
`bench/corpus.py`'s 40 sets, `docker/smoke.py`'s set, and
`tests/test_calc.py::test_centre_distance_matches_an_independent_solver`'s
teeth×pressure-angle×shift loop (lines 170–196, ~100 sets machine-generated).

---

### `tests/regression/pre_v0_2.json` (new) — config/data fixture, file-I/O

**No in-tree analog** — this is a new file category for this project (checked-in JSON
data fixture with a provenance header). CONTEXT.md D-01/D-04 fix its shape directly, so
follow the decisions rather than an existing file:
- One record per source tag (D-14's test id doubles as the JSON key, per Claude's
  Discretion).
- A record stores **only the fields its source set** (D-04) — e.g. `{"teeth": 24,
  "module": 1, "pressure_angle": 20, "bore_flat": 0}` for the README's `--teeth 24
  --module 1 --pressure-angle 20 --bore-flat 0` example, not all 17 `GearParams` fields.
- A **file-level provenance header**: git sha, `cadquery`/`cadquery-ocp` versions
  (`pip show cadquery cadquery-ocp` or `importlib.metadata.version`), capture date
  (D-04, Pitfall 11).
- Per record: the input params (as-set only), `derive()`'s 19 fields (D-10, exact), plus
  `mate_teeth`/`centre_distance` for D-07's mated sets, `build().Volume()` (D-11),
  six bbox corners `xmin/xmax/ymin/ymax/zmin/zmax` (D-12), `len(Faces())` and
  `len(Edges())` (D-13).
- `indent=2`, sorted keys, trailing newline (Claude's Discretion, "minimal diffs").

**Reference for the 19 `DerivedDimensions` field names to pin exactly** (`src/spur/
calc.py:165-222`, the full `class DerivedDimensions(BaseModel)` block): `pitch_d,
tip_d, root_d, base_d, caliper_over_tips, tip_thickness, root_thickness, root_gap,
root_fillet, span_teeth, span, bore_effective, recess_id, recess_od, recess_fillet,
web, warnings, mate_teeth, centre_distance` — 19 fields, `model_config =
ConfigDict(frozen=True)` (line 173) confirms exact-equality comparison is honest (no
mutation between capture and replay).

---

### `tests/test_regression.py` (new) — test, request-response

**Analog A — the parametrized build/assert shape:** `tests/test_model.py::
test_builds_one_valid_solid` (lines 16–34):
```python
@pytest.mark.parametrize("kw", [
    {},
    {"pressure_angle": 20},
    ...
])
def test_builds_one_valid_solid(kw: dict[str, object]) -> None:
    p = GearParams.model_validate(kw)
    s = build(p)
    assert s.isValid()
    bb = s.BoundingBox()
    assert bb.zlen == pytest.approx(p.face_width)
    assert max(bb.xlen, bb.ylen) <= p.module * (p.teeth + 2 + 2 * p.profile_shift) + 1e-6
```
Copy: `GearParams.model_validate(kw)` to rebuild each record's params from its as-set
fields; `build(p)` (public API, `src/spur/model.py:262-264`) for the solid;
`pytest.approx` for the float comparisons. D-14 requires **one parametrized case per
record with `id=` the source tag** — use `pytest.param(record, id=tag)` inside the
`parametrize` call (a shape `test_model.py` doesn't need since its ids are the dict
reprs already; the executor adds explicit `id=` here) so a red test names the exact
source line, not a record number.

**Analog B — exact-field comparison on `derive()`:** `tests/test_calc.py::
test_default_dimensions` (lines 19–35):
```python
def test_default_dimensions() -> None:
    d = derive(GearParams())
    assert d.pitch_d == pytest.approx(33.25)
    assert d.tip_d == pytest.approx(36.75)
    ...
    assert d.warnings == ()
    assert d.mate_teeth is None
    assert d.centre_distance is None
```
This is the existing, narrower L05 tripwire CONTEXT.md calls out as "must not move" —
the new fixture generalizes this exact pattern (one field-by-field or
`model_dump()`-equality assertion per record) across every pre-v0.2 set, not just the
default. D-10 wants **exact** equality including the warning text, so
`assert derive(p, mate_teeth=...).model_dump() == expected_derive_dict` (or per-field
`==`, not `pytest.approx`, since `derive()` is Python-rounded to 3 dp already — Phase 4
D-10) is closer to the contract than `test_default_dimensions`'s individual asserts.

**Analog C — content-equivalence tolerances for kernel output:** `tests/test_model.py::
test_an_stl_export_matches_a_first_export_whatever_came_before` (lines 128–140) is this
project's precedent for "the kernel's number is compared with a tolerance, not
byte-for-byte" (L24) — reuse `pytest.approx(expected_volume, rel=1e-6)` for D-11's
`Volume()` check and `pytest.approx(expected_corner, abs=1e-6)` for each of D-12's six
bbox corners.

**Analog D — `BuildError` message-matching for the zero-edge guard tests:**
`tests/test_api.py:489` and `tests/test_pool.py:233,314` construct `BuildError("D-flat
too small for this bore")` directly as a parametrize row and assert on the resulting
HTTP/exit behavior — the precedent for testing a `BuildError` by its text, matching D-15
("tests match on the text"). The new zero-edge tests (in `tests/test_model.py`, per
`<code_context>` Integration Points — "the natural home") should follow the same shape:
`with pytest.raises(BuildError, match="<distinctive substring>"):` around a call that
provokes zero edges (a bore-less solid handed to `_bore_rim_edges`, or a monkeypatched
`bore_rim_limit` — Claude's Discretion leaves the provocation method open).

**Analog E — selected-edge-count assertions:** no existing test reads `.Edges()` counts
directly, but `test_exporting_leaves_the_cached_solid_exact` (`tests/test_model.py:
116-124`) is the precedent for reaching into a built solid's kernel properties
(`.BoundingBox()`) inside a test — the new count tests do the same with
`len(model._bore_rim_edges(...))` / `len(model._groove_floor_edges(...))`, asserting the
D-16 numbers (round bore 2, D-flat 4, recess floor 2 per filleted side) with and without
recesses (D-17).

---

### `scripts/regen_fixture.py` (or `tests/regression/regen.py` — Claude's discretion) — utility, batch

**Analog:** `scripts/pr_land.py`'s `main()` (tail, shown above) and `bench/memory.py`'s
`main()` (tail, shown above) — both `argparse.ArgumentParser` + `if __name__ ==
"__main__": sys.exit(main())` (or `raise SystemExit(main())`), invoked from the Makefile
via `$(PY) -m <module path>`.

**Simpler shape to prefer — `bench/corpus.py`'s no-argparse-needed pattern**: a regen
script here likely takes no arguments at all (D-02: "regeneration is a `make` target
running a script... the same script performs the first-time capture") — closer to a
plain `def main() -> int:` that imports `tests.regression.corpus.corpus()`, builds every
`GearParams`, writes the JSON, and returns 0, without `argparse` at all if there is
nothing to parametrize. Follow `scripts/pr_land.py`'s file docstring shape either way —
name the trigger and the mechanism up front, in prose, not just what the code does.

**Where it must live for `make typecheck` (D-Claude's-Discretion note in
`<code_context>`):** `Makefile:54` already lists `scripts` in mypy's scope:
```
typecheck: $(STAMP)  ## mypy --strict over the package and its tests
	$(PY) -m mypy src tests docker bench scripts
```
So `scripts/regen_fixture.py` needs no `Makefile` change to join `make typecheck`; a
script placed inside `tests/regression/` instead joins automatically too (`tests` is
already in that same list) — either choice needs zero edits to line 54, only a new
target.

**`Makefile` target to copy — the `lock`/`vendor` "generated artefact" section shape**
(lines 122–128):
```
lock:  ## regenerate requirements.txt, the pinned closure the image installs
	docker/refresh-requirements.sh

vendor:  ## rebuild the vendored three.js bundle (needs node)
	cd web && npm ci && npm run build
```
And the argument-checked shape from `pr.land` (lines 171–173):
```
pr.land: $(STAMP)  ## PR=<n> : squash-merge a PR only if its head is green and current with main
	@test -n "$(PR)" || { echo "PR= required"; exit 1; }
	$(PY) -m scripts.pr_land $(PR)
```
D-02's `make fixture.regen` (name is the planner's) takes no required argument, so the
plain `lock`/`vendor` shape (a `## help` comment line + one command, `$(STAMP)`
dependency to guarantee the venv exists) is the closer template; add it to the "generated
artefacts" section (after line 128, before `worktree.bootstrap`) alongside `lock` and
`vendor` — same section, same kind of thing (a committed artefact regenerated on demand,
never on every commit).

---

## Shared Patterns

### `BuildError` routing (no new plumbing)
**Source:** `src/spur/build_errors.py` (full file), `src/spur/app.py:414`,
`src/spur/cli.py:111`
**Apply to:** both new guards in `model.py` (`_bore_rim_edges`, `_groove_floor_edges`)
```python
class BuildError(RuntimeError):
    """The CAD kernel could not produce a valid solid for these parameters."""
```
`model.py`'s existing contract — "`BuildError` is the only exception that leaves
`model.py`" (`_build_checked`, lines 249–256: catches everything else and re-raises as
`BuildError`) — already covers a `raise BuildError(...)` added inside `_bore_rim_edges`
or `_cut_face_recesses`, since both run inside `_build`, itself wrapped by
`_build_checked`. No `app.py`/`cli.py` change needed (D-15's explicit rejection of "an
internal error → HTTP 500" as "beyond foundation scope").

### Named tolerance/slack constants carry their reason in a comment
**Source:** `src/spur/model.py:41` (`TOL`), `src/spur/calc.py:15-17` (`MIN_WALL`,
`MIN_TIP_FDM`, `MIN_RECESS_WIDTH`)
**Apply to:** the new slack constant in `model.py` (D-18)
```python
MIN_WALL = 0.4          # mm, thinnest wall allowed anywhere in the body
MIN_TIP_FDM = 0.4       # mm, below this a tip is roughly one extrusion line wide
MIN_RECESS_WIDTH = 1.0  # mm, below this a face groove is not worth cutting
...
TOL = 1e-6              # mm, for matching kernel geometry back to the numbers we asked for
```
Every constant in this codebase is one line of code, one line (or clause) of comment
naming the unit and the reason for that exact number, never left to a docstring
elsewhere. The new slack constant's comment must state why 10 µm and not `TOL` (1e-6) —
CONTEXT.md already supplies the reason ("must exceed the kernel's post-boolean vertex
tolerances and stay far below `MIN_WALL`") — copy that reasoning into the comment
verbatim, not just the number.

### `GearParams.model_validate(kw)` — the one way to rebuild a params object from a raw dict
**Source:** `tests/test_model.py:29`, `tests/test_calc.py:159-160`
**Apply to:** `tests/regression/corpus.py` (dedup), `tests/test_regression.py` (rebuild
from a JSON record's stored fields), the regen script.
```python
p = GearParams.model_validate(kw)
```
`disallow_any_explicit` under mypy `--strict` (Phase 4 D-08) is why this, not
`GearParams(**kw)` with a `# type: ignore`, is the sanctioned way to build one from a
`dict[str, object]`.

### Content equivalence over byte/float equality for anything the kernel produces
**Source:** `docs/architecture/decision_log.md::L24`; `tests/test_model.py::
test_an_stl_export_matches_a_first_export_whatever_came_before` (lines 128-140)
**Apply to:** `tests/test_regression.py`'s `Volume()` (`rel=1e-6`, D-11) and bbox
(`abs=1e-6`, D-12) assertions — never exact float equality on anything OCCT computed,
always exact equality on anything `derive()` computed in Python (D-10).

### Every deliberate constant/tolerance choice is measured and recorded, not assumed
**Source:** `docs/architecture/decision_log.md::L24`'s "Research's timings..." and "What
the copy costs" sections; `bench/RESULTS.md`
**Apply to:** D-06's `make verify` delta, D-11's `rel=1e-6`, D-12's `abs=1e-6` — all
carry a measured-on-date number in CONTEXT.md's `<specifics>` already; the plan
re-measures and records the final number either in `bench/RESULTS.md` (the precedent
for "numbers that outlive a phase") or the plan SUMMARY (Claude's Discretion).

### One phase = one branch = one PR = one squash commit; plain `git commit`, explicit files
**Source:** `.planning/milestones/v0.1-phases/06-address-tech-debt-merge-gate-solid-cache/
06-CONTEXT.md` "Established Patterns"; D-19/D-20 in this phase's own CONTEXT.md
**Apply to:** every commit in this phase's execution — never `git add -A`, run `make
verify` once warm at session start (D-20).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/regression/pre_v0_2.json` | config/data fixture | file-I/O | No checked-in JSON data fixture exists yet in this codebase; CONTEXT.md D-01/D-04 fully specify its shape (see Pattern Assignments above), so the planner should follow the decisions directly rather than an existing analog. |
| `docs/architecture/decision_log.md` L26 (if taken) | config (append-only doc) | n/a | Not a "file to create" in the code sense, but flagged here because its analog (L24, above) is a full worked template already extracted — no gap, just noting it is a doc entry, not source. |

## Metadata

**Analog search scope:** `src/spur/` (calc.py, model.py, build_errors.py, params.py,
app.py, cli.py), `tests/` (test_model.py, test_calc.py, test_api.py, test_cli.py,
test_pool.py), `bench/` (corpus.py, latency.py, memory.py), `scripts/` (pr_land.py),
`Makefile`, `pyproject.toml`, `docs/architecture/decision_log.md`, `README.md`.
**Files scanned:** 19 (all confirmed git-tracked via `git ls-files`; no gitignored
mirrors encountered — this project has no `.gsd/capabilities/` install mirror).
**Pattern extraction date:** 2026-09-26.
