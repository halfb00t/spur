# Phase 16: Typing & Validation Debt - Pattern Map

**Mapped:** 2026-10-04
**Files analyzed:** 14 (one `src/` file, one test file, config, prose and record; no new modules)
**Analogs found:** 13 / 14 (the two `VALIDATION.md` files are written by a skill; shape analog only)

All analog paths verified git-tracked (`git ls-files`). No gitignored mirrors named. Line numbers are HEAD `e306f51` (model.py unchanged since `085e5a6`).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/model.py` (+`_body`, `_shape_of`, `_NOT_A_BODY`; 5 sites) | utility (vendor-type boundary) | transform | `_groove_floor_edges` / `_bore_rim_edges` / `_tip_edges` guards (model.py ~423-505) and `_build` end check (519-522) | role-match (same `BuildError` register) |
| `tests/test_model.py` (+2 refusal tests, import block) | test | request-response (unit, no kernel build) | `tests/test_model.py` 236-244 (`_bore_rim_edges` BuildError row) | exact |
| `Makefile` (`no-fake-done`, second `@if`) | config | batch | `Makefile` 63-68, the existing `@if git grep ... fi` | exact (in place) |
| `pyproject.toml` (`[[tool.mypy.overrides]]` ~111-115) | config | n/a | same block; comment style of lines 100-110 | exact (in place) |
| `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` -> `resolved/` | debt retirement | CRUD (`git mv`) | `docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md` | exact |
| `docs/tech_debt/INDEX.md` (row 19 -> Resolved table, ~line 51; +gap rows if any) | index | CRUD | its Resolved table rows 32-50 | exact |
| `docs/tech_debt/active/2026-10-xx-phase-0{7,8}-nyquist-gaps.md` (only if gaps) | debt (nice) | CRUD | `docs/tech_debt/TEMPLATE.md`; `active/2026-09-21-cadquery-shape-typing.md` for section shape | exact |
| `docs/architecture/solid-model/implementation.md:29-33` | prose | n/a | same bullet list ("Things that will bite") | exact (in place) |
| `docs/architecture/decision_log.md` (L35, appended) | record | append-only | `## L34` (line 1628), `## L33` (1517), `## L32` (1427) | exact |
| `.planning/milestones/v0.2-MILESTONE-AUDIT.md` (nyquist block 37-41, table ~156-167) | planning record | prose amend | same block; dated sub-heading is new | role-match |
| `.planning/REQUIREMENTS.md`, `ROADMAP.md`, `PROJECT.md` sentence corrections | planning record | prose edit | 14 D-07 / 15 D-01 (ROADMAP via gsd tooling only; REQUIREMENTS scoped Edit) | role-match |
| `.planning/milestones/v0.2-phases/07-*/07-VALIDATION.md`, `08-hex-bore/08-VALIDATION.md` | planning record | skill-written | `.planning/phases/15-the-gate-measured-and-pinned/15-VALIDATION.md`, `13-latency-bar/13-VALIDATION.md` | shape only |
| `tests/regression/pre_v0_2.json` | fixture | n/a | n/a, byte-unchanged (`git diff --exit-code 085e5a6 --`) | n/a |

## Pattern Assignments

### `src/spur/model.py` (utility, transform)

**Analog:** the D-15 guards in the same file and the `_build` end check. Imports already present (lines 15-31): `import cadquery as cq`, `from .build_errors import BuildError`. No import change.

**Placement:** under the `# --- picking kernel geometry back out ---` banner (line 416), before `_ring`.

**Helpers** (RESEARCH "Pattern 1", prototyped green under mypy strict, ruff, 289 tests):
```python
_NOT_A_BODY = ("Geometry kernel returned a {} where a solid body was expected: a modelling "
               "defect in the build pipeline, not a parameter problem.")


def _body(shape: cq.Shape) -> cq.Solid | cq.Compound:
    # comment: measured runtime types + 2026-10-04; Mixin3D is on Solid and Compound only
    if not isinstance(shape, cq.Solid | cq.Compound):
        raise BuildError(_NOT_A_BODY.format(type(shape).__name__))
    return shape


def _shape_of(wp: cq.Workplane) -> cq.Shape:
    value = wp.val()   # Vector | Location | Shape | Sketch
    if not isinstance(value, cq.Shape):
        raise BuildError(_NOT_A_BODY.format(type(value).__name__))
    return value
```
Constraints: one wrapped constant (a single f-string line is 174 chars, ruff E501 at 100); helper comments must NOT contain the literal text `type: ignore` (D-05's grep would refuse them); `_gear_blank` stays `-> cq.Shape` (RESEARCH Pitfall 1: `cq.Solid` gives five `[assignment]` errors in `_build`).

**Five call-site edits** (current text, 213/237/239/411/420):
```python
# 213  (_cut_face_recesses) -- also delete comment 211-212
solid = _body(solid).fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))
# 237  (_cut_bore)
solid = solid.cut(_shape_of(hole))
# 239-240
solid = _body(solid).chamfer(p.bore_chamfer, None, _bore_rim_edges(solid, p))
# 411-412 (_chamfer_tips)
solid = _body(solid).chamfer(c, None, _tip_edges(solid, pr.ra, p.face_width))
# 418-420 (_ring)
return _shape_of(cq.Workplane("XY").workplane(offset=z0)
                 .circle(r_out).circle(r_in).extrude(height))
```
Assign the `Any` result to the `cq.Shape`-typed `solid` before returning (10-02 `warn_return_any` rule; `_chamfer_tips` 411-413 already does).

**Message-register precedent** (existing guards, same "defect, not parameter" voice; read the guard text at model.py ~501-504 and mirror its wording): `_bore_rim_edges` raises with "selected no bore-rim edges" (asserted at test_model.py 242).

**End-of-pipeline positive assertion to mirror** (model.py 519-522): `len(solids) != 1 or not solids[0].isValid()` -> `BuildError`.

---

### `tests/test_model.py` (test, unit)

**Analog:** `tests/test_model.py` 236-244 (docstring says why; `pytest.raises(BuildError, ...) as exc_info`; a negative assertion on the catch-all relabel).

**Imports pattern** (lines 25-36, isort order; ruff `I` on): add `_body` before `_bore_rim_edges`, `_shape_of` between `_groove_floor_edges` and `_tip_edges`.
```python
from spur.model import (
    TESSELLATION,
    TOL,
    Quality,
    _bore_rim_edges,
    _build_checked,
    _fillet_corner,
    _groove_floor_edges,
    _tip_edges,
    build,
    export,
)
```
`cq`, `pytest`, `BuildError` already imported (lines 8-11).

**Core pattern** (RESEARCH, green under `filterwarnings = error`; assert full string with `==`, not `match=`, because `match` is a regex search -- 10-REVIEW CR-01):
```python
def test_a_non_body_shape_in_the_build_pipeline_is_named_as_a_modelling_defect() -> None:
    with pytest.raises(BuildError) as exc_info:
        _body(cq.Face.makePlane(1, 1))
    assert str(exc_info.value) == (
        "Geometry kernel returned a Face where a solid body was expected: a modelling "
        "defect in the build pipeline, not a parameter problem.")


def test_a_workplane_value_that_is_not_a_shape_is_named_as_a_modelling_defect() -> None:
    with pytest.raises(BuildError) as exc_info:
        _shape_of(cq.Workplane("XY"))   # empty stack: val() is the plane origin, a Vector
    assert str(exc_info.value) == (...Vector...)
```
Names must contain `non_body` / `not_a_shape` (RESEARCH quick-run `-k`). Count 927 -> 929. Existing-style note: existing rows use `match=` for prefixes; the new ones deliberately do not.

---

### `Makefile` (config, batch)

**Analog:** `Makefile` 63-68 (`no-fake-done`). Hand-align (L16, no formatter); tab-indented recipe.
```make
no-fake-done: ## refuse unfinished work dressed up as finished
	@if git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b' \
	     -- '*.py' '*.js' '*.sh' ':!src/spur/static/vendor'; then \
	  echo "make: unfinished-work markers above. Finish it, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi
```
Add a second `@if git grep -nE 'type: ignore' -- 'src/spur/*.py'; then ... exit 1; fi` after it, own sentence ("a suppression in src/spur is unfinished work: narrow the type, or file it in docs/tech_debt/"). Scope stays `src/spur/` (`tests/test_calc.py:1472`, `tests/test_cli.py:423` are deliberate). Show RED once (5 hits on unedited model.py), then GREEN; do not commit RED. Must land in the same commit as the ignore removal (hook runs `make verify`).

---

### `pyproject.toml` (config)

**Analog:** same block, 111-115 (current):
```toml
[[tool.mypy.overrides]]
# The CAD kernel ships no type information. Scoped to the two packages that lack it --
# never a global ignore_missing_imports, which would blind the whole project.
module = ["cadquery.*", "OCP.*"]
ignore_missing_imports = true
```
Edit to `module = ["OCP.*"]`; rewrite the comment (OCP has 0 `.pyi`, no `py.typed`; cadquery 2.8.0 ships `py.typed`, so the entry was inert for it; keep the "never global" clause). Gate (D-04): `rm -rf .mypy_cache && make typecheck` before and after, byte-identical (`Success: no issues found in 37 source files`); a difference means stop and ask. Match the comment voice of lines 100-110 (measurement, source, date).

---

### `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` -> `resolved/` (debt retirement)

**Analog:** `docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md` (header + trailing `## Resolution (date)` section).

**Header shape** (lines 1-10): `Severity: nice`, `Status: resolved`, `Date:`, `Resolved in: <sha-or-subject>`, `Source:`, `Related files:`. Flip `Status: active` -> `resolved`, add `Resolved in:`, correct `Related files` `src/spur/model.py:195, 219, 221, 264, 273` -> `213, 237, 239, 411, 420`, append a `## Resolution (2026-10-04)` section recording: "cast once at `.val()`" could not hold because `Shape.cut -> Shape`; mechanism taken (`_body`, `_shape_of`); `cadquery.*` override dropped. Also fix the stale "RUF100 will fail the build" sentence is history, leave it; RESEARCH Finding 7 says mypy `unused-ignore` is the real mechanism, say so in Resolution.

**Sha handling (CORRECTION to CONTEXT D-14, RESEARCH Finding 10):** a commit cannot embed its own sha. Fix commit: `git mv`, status flip, `Resolved in: <commit subject>`, INDEX row moved. Then a second docs-only commit "record the retiring commit's sha in the Shape-typing debt" (precedent: `825095f` -> `775ee6f`, `2aadcea` -> `b8926e7`, `6709953` -> `05668ef`). Plain `git commit`, never `gsd_run query commit`.

**INDEX:** remove row 19 from Active table (INDEX.md line 19); add to Resolved table (rows 32-50 shape):
```
| [CadQuery's `Shape` typing forces five `type: ignore`s](resolved/2026-09-21-cadquery-shape-typing.md) | `<sha>` — see the file's own `Resolved in:` field |
```

---

### `docs/tech_debt/active/2026-10-xx-phase-0{7,8}-nyquist-gaps.md` (only if gaps)

**Analog:** `docs/tech_debt/TEMPLATE.md` plus the active shape above (`Severity: nice`, `Status: active`, `Source:`, `Related files:`, `## Context`, `## Why it matters`, `## Next step`, `Revisit when:`). One file per phase, one INDEX Active row each in the INDEX row format at line 19 (`| nice | [title](active/file.md) | trigger |`), trigger "the covered file is next touched". Zero gaps = no file. A behaviour with no test at all is `must` -> `checkpoint:decision` (D-09).

---

### `docs/architecture/solid-model/implementation.md:29-33`

**Analog:** the bullet itself (bold lead-in, then 3-4 wrapped lines, pointer to a doc). Replace the "`type: ignore` comments are load-bearing" bullet with: two `isinstance` boundaries (`_body`, `_shape_of`) that raise `BuildError`; why (`Shape.cut -> Shape`, `Mixin3D` on `Solid`/`Compound` only); the `make no-fake-done` pin; pointer to the resolved debt file and L35. Wording may use `type: ignore` here (docs are outside the `src/spur/` grep).

---

### `docs/architecture/decision_log.md` (L35)

**Analog:** `## L34 — ... (amends L12 and L13)` at line 1628 (title with "amends Lxx", prose paragraphs, `**Reversibility.**` paragraph, closing `Reason:` paragraph, `Machine:` line when measured). Append after the last line; L21 untouched. Content per D-13; cite measured types to CONTEXT domain facts / SUMMARY shas; Nyquist outcome numbers from the two VALIDATION frontmatters as read; record Finding 14 (422 + WARNING for a pipeline defect is the same known trade-off as the three D-15 guards).

---

### `.planning/milestones/v0.2-MILESTONE-AUDIT.md` (D-11)

**Analog:** itself. Current frontmatter block (lines 37-41):
```yaml
nyquist:
  compliant_phases: ["09", "10", "11", "12"]
  partial_phases: []
  not_validated_phases: []
  missing_phases: ["07", "08"]
  overall: partial
```
Set `missing_phases: []`, place `07`/`08` per the frontmatter read (`partial_phases` if `nyquist_compliant: false`), add `amended: 2026-10-xx by Phase 16 (16-0N-SUMMARY.md)`, say how `overall` was derived (RESEARCH A2). Table rows (~156-167) `| 07 | missing | — | — | MISSING (pre-capability; ...) |` stay; add a dated sub-heading with two new rows in the same column shape (`| 07 | exists | validated | <read> | <classification> |`). Never assert `true`.

---

### Planning-record corrections (D-12)

**Analog:** 14 D-07 / 15 D-01. REQUIREMENTS via scoped `Edit` (lines 152-171, rows 226-227 untouched); ROADMAP Phase 16 SC1/SC4 via gsd tooling (`/gsd-phase edit 16 --force` or scoped Edit bracketed by `gsd_run query roadmap milestone-scope`, which must still read `scope: complete`, phases 13-16; no version token/status emoji/"Milestone" in a heading); PROJECT.md only at the phase transition. Also correct SC2's "RUF100" mechanism sentence (Finding 7: mypy `unused-ignore` retires a stale ignore, RUF100 governs `noqa`).

---

### `07-VALIDATION.md` / `08-VALIDATION.md` (skill-written)

**Analog for what the executor reads back:** `13-VALIDATION.md` / `15-VALIDATION.md` (frontmatter `status: validated`, `nyquist_compliant`, per-task map, Manual-Only rows). Executor post-check (RESEARCH): `grep -E '^(status|nyquist_compliant):' .planning/milestones/v0.2-phases/07-*/07-VALIDATION.md .planning/milestones/v0.2-phases/08-hex-bore/08-VALIDATION.md`; `git diff --stat 085e5a6 -- tests/` limited to `tests/test_model.py`. Human commits with plain `git add <file> && git commit -m "docs(phase-07): add validation strategy"` if the helper times out.

## Shared Patterns

### One fixing commit carries the proof and the record
**Source:** CONTEXT D-07, RESEARCH Pitfall 4.
**Apply to:** plan 1. In ONE commit: `model.py`, `tests/test_model.py`, `Makefile`, `pyproject.toml`, `implementation.md`, debt `git mv` + INDEX. The pin is red against any remaining ignore, and the hook runs `make verify`. `.planning` corrections ride the same plan's separate `.planning` commit; sha-follow-up is a third small commit.

### Plain `git commit`, explicit staging
**Source:** CONTEXT D-15; `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`.
**Apply to:** every commit in the phase (hook ~64 s; `gsd_run query commit` times out at 30 s).

### Errors are named as defects, never blamed on a parameter
**Source:** `_build_checked` (model.py 525-532) wraps any non-`BuildError` as "Geometry kernel failed (X); try smaller fillets or chamfers"; the D-15 guards raise `BuildError` first. Test idiom at test_model.py 236-244 asserts `"try smaller" not in str(exc_info.value)` for the guard family.
**Apply to:** `_body`, `_shape_of`, their tests.

### Measured, dated claims in comments and Lxx
**Source:** model.py comments (e.g. `_cut_keyway` docstring "178 faces / 508 edges ... research Pattern 1, 2026-09-27", `_cut_bore` "planning probe, 2026-09-26").
**Apply to:** the helper comments (runtime types after each step, 2026-10-04) and L35. Never re-estimate; cite CONTEXT domain facts.

### Gate commands
**Source:** CLAUDE.md, RESEARCH Validation Architecture.
**Apply to:** all plans. Quick: `make test PYTEST_ARGS="tests/test_model.py -k 'non_body or not_a_shape' -q -n0 --no-cov"`; `rm -rf .mypy_cache && make typecheck`; final `make verify` (929 tests) and `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json`; `git grep -nE 'type: ignore' -- 'src/spur/*.py'` prints nothing.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Dated amendment sub-heading in `v0.2-MILESTONE-AUDIT.md` | planning record | prose | No closed audit has been amended in place before; follow decision-log append-only spirit |
| `0{7,8}-VALIDATION.md` content | planning record | skill-written | Authored by `/gsd-validate-phase` State B at a human checkpoint; 13/15 VALIDATION are shape references only |

## Metadata

**Analog search scope:** `src/spur/model.py`, `tests/test_model.py`, `Makefile`, `pyproject.toml`, `docs/tech_debt/`, `docs/architecture/`, `.planning/phases/15-*`, `.planning/milestones/v0.2-MILESTONE-AUDIT.md`
**Files scanned:** about 12 read, 5 `git ls-files` checks
**Pattern extraction date:** 2026-10-04
