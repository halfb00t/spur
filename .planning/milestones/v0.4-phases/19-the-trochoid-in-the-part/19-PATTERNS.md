# Phase 19: The Trochoid in the Part - Pattern Map

**Mapped:** 2026-10-08
**Files analyzed:** 20 (new/modified)
**Analogs found:** 20 / 20 (all analogs verified git-tracked; no gitignored mirror paths)

Line numbers are at HEAD `e7ddbb0`. Excerpts below are the shipped radial/Phase 18 code the new code sits beside or replaces. RESEARCH Pattern 2 (`_trochoid_outline`), Pattern 5 (derive table), Pattern 6 (field walk) and Pattern 7 (kernel tier) already hold the new-code sketches; this file adds the real-code analogs to copy structure from.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (`root_shape`, `root_fillet` help) | model (schema field) | request-response | `params.py:91-93` `recess_sides` | exact |
| `src/spur/calc.py` (`RootMode.curve`) | model (frozen dataclass) | transform | `calc.py:1501-1506` `RootMode` itself | exact |
| `src/spur/calc.py` (`spline_start`, `tip_chamfer_limit`, `tip_chamfer_effective` take curve / `rm`) | utility | transform | `calc.py:266-291`, `294-318` (modified in place) | exact |
| `src/spur/calc.py` (`derive`, `DerivedDimensions`) | service + schema | request-response | `derive()` 1005-1070 warnings blocks, `DerivedDimensions` 895-905 | exact |
| `src/spur/calc.py` (`_ROOT_SENTENCES`, `root_warnings`: waist, thickness, undercut sentences) | utility | request-response | `calc.py:1550-1590` | exact |
| `src/spur/model.py` (`_outline`, `_gear_blank`, `_build`, guards) | service (CAD) | transform | `model.py:133-193` radial `_outline`, `_tip_edges` 510-538 (guard wording) | exact |
| `src/spur/cli.py` | controller | request-response | `cli.py:40-54` (no edit expected) | exact |
| `src/spur/static/app.js` (`DIMS` rows) | component | request-response | `app.js:21-23` rows; enum branch at 64-67 (no edit) | exact |
| `tests/test_trochoid.py` (derive branches, sentences, x_min, spline_start, fixture read) | test | transform | same file: `test_root_mode_refuses...` 538-568, `test_every_pre_v0_2_record_reads_radial...` 455 | exact |
| `tests/test_model.py` (kernel tier, guards, compose, source-grep) | test | transform | `test_model.py:416-450` `_tip_edges` spy tests, `:468` `positionAt` use | role-match |
| `tests/test_cli.py` (field walk) | test | request-response | `test_cli.py:185-222` | exact |
| `tests/test_api.py` (adjacency, key set, DIMS regex) | test | request-response | `test_api.py:78-92`, `130`, `314-315` | exact |
| `tests/composition.py` (trochoid column; `ALWAYS` set) | test helper | batch | same file `TIPS` / `ALWAYS` 38-50 | exact |
| `bench/trochoid.py` (new subcommands: chamfer, build, spline, waist) | utility (bench) | batch | same file `main()` 867-876, `tuned_shift` 84; `bench/tip_chamfer_spike.py` | exact |
| `bench/sweeps/trochoid.json` | config | batch | `bench/sweeps/tip_chamfer.json` | exact |
| `tests/test_bench.py` | test | transform | its `from bench.trochoid import ...` block (line 55) | exact |
| `bench/RESULTS.md` (new section) | docs/record | n/a | `## Trochoid maths (Phase 18)` at 3035; `## The gate, measured and pinned (Phase 15)` 2208 | exact |
| `docs/architecture/decision_log.md` (L38) | docs | n/a | `## L37` at 1995 (amends form), `## L34` at 1635 | exact |
| `README.md`, `docs/architecture/gear-maths/*.md`, `solid-model/*.md`, `docs/ideas/2026-09-21-trochoidal-root-fillets.md` | docs | n/a | their own current radial claims | exact |

## Pattern Assignments

### `src/spur/params.py` : `root_shape` field (schema, request-response)

**Analog:** `params.py:91-93` (the only `Literal` field). Insert after `tip_chamfer` (params.py ~50-54), group `"Teeth"`, no `step`.
```python
    recess_sides: Literal["both", "top", "bottom", "none"] = Field(
        "both", title="Recess sides", description="Which faces get an annular groove.",
        json_schema_extra={"group": "Recess", "unit": ""})
```
`root_fillet` (lines 47-49) help text to rewrite for both meanings; keep `_f(0.5, 0, 3, ...)`:
```python
    root_fillet: float = _f(0.5, 0, 3, title="Root fillet", group="Teeth", unit="mm",
                            step=0.05,
                            help="Fillet radius at the tooth roots, capped to fit. 0 = sharp.")
```
Note `cli.py:40-54` builds help as `f"{field.description} [{field.default}]"` so the description must carry the default-meaningful text.

---

### `src/spur/calc.py` : `RootMode.curve`, `spline_start`, `tip_chamfer_*`

**Analog:** `RootMode` (1501-1506) and `root_mode` (1509-1547). Add trailing `curve: RootCurve | None = None`, filled at the `return RootMode("trochoid", None, c)` line, which currently discards `curve`:
```python
    curve = _root_curve(c)
    if isinstance(curve, RootCurve):
        return RootMode("trochoid", None, c)
    return RootMode("radial", curve, c)
```
Update the docstring sentence "Nothing in production calls this until Phase 19 ... D-07 forbids reading `p.root_fillet`" (it is superseded by D-01).

**`spline_start`** (266-291), keep the two-arg form, add `curve: RootCurve | None = None`; under a curve return `curve.points[-1][0]` and skip the radial clamp:
```python
    r_line = max(pr.rb, pr.rf + 2.0 * fillet) if fillet > 0 else pr.rb
    r_line = min(r_line, pr.rf + 0.5 * (pr.ra - pr.rf))
    return max(r_line, pr.r_start)
```
**`tip_chamfer_limit`** (294-318): the third bound is the only line that changes; it is a `(value, reason)` tuple compared as a tuple:
```python
        (pr.ra - spline_start(pr, root_fillet(p)) - TIP_CHAMFER_MARGIN,
         "to keep it on the involute flank, above the straight lead-in from the root "
         "fillet"),
```
Under trochoid the reason text must not say "straight lead-in" (no chord); give it its own reason string. `tip_chamfer_effective(p, rm=None)` calls `root_mode` itself when `rm is None` (RESEARCH Pattern 1). `derive()` calls `tip_chamfer_limit(p)[1]` at 1037, so thread `rm` there.

---

### `src/spur/calc.py` : `derive()` and `DerivedDimensions`

**Analog:** the existing blocks in `derive()`; mode-key each, compute `rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` once near the top.

**Root fillet + capped warning** (1010-1012): in trochoid mode the value is `rm.cutter.rho` and the sentence comes from `root_warnings(rm)`; the L09 gap-cap sentence must not fire:
```python
    rfil = root_fillet(p)
    if rfil < p.root_fillet:
        warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```
**Lead-in warning** (1013-1025): guard the whole `h = spline_start(...)` block with `rm.mode == "radial"`. Keep its "compared at the 3 dp it prints" comment convention.

**Undercut sentence** (1047-1050): fixture-pinned text in radial mode (`pre_v0_2.json:582,632,948,996,1588`); restate only in trochoid mode. Compare at printed resolution, print `ceil(x_min*1000)/1000`:
```python
    z_min = 2 * (1 - p.profile_shift) / math.sin(pr.alpha) ** 2
    if p.teeth < z_min:
        warnings.append(f"Below {z_min:.1f} teeth a cut gear would be undercut; "
                        "this model uses a radial root instead.")
```
**Ignored-field sentence shape** (hex bore, 1063-1070): use for "does not apply"-style sentences, `ignored = [...]` then one `warnings.append(f"...")`.

**Return block** (1155-1165) uses a local `r3` and rounds every length once at construction:
```python
        root_thickness=r3(root),
        root_gap=r3(gap),
```
becomes `r3(root) if trochoid-off else None`. New fields `root_form_d`, waist field: `r3(2 * rm.curve.points[-1][0])` and the arc form of `curve.waist`.

**`DerivedDimensions`** (895-905) field shape to copy for the two widened and two new fields; post-fixture fields are `float | None` and null on replay (L27 pattern), described as the cutter-envelope junction:
```python
    root_thickness: float = Field(description="Tooth thickness on the root circle, as an arc.",
                                  json_schema_extra={"unit": "mm"})
```
Look at the last existing `float | None` field in this class for the exact `Field(None, ...)` spelling before writing.

**New sentences:** add to `_ROOT_SENTENCES` (1550-1570), a dict of `{placeholders}` strings filled from one `values` dict in `root_warnings` (1572-1590) so the lookup has no branches; tests capture sentences from `root_warnings`, never type them.

---

### `src/spur/model.py` : `_outline`, `_gear_blank`, `_build`, guards

**Analog:** the radial `_outline` (133-187) itself. Add `curve: RootCurve | None = None` and branch at the top; the radial branch must stay float-for-float unchanged (replay compares faces, edges, volume at `rel=1e-6`). The trochoid body is RESEARCH Pattern 2. Per-tooth loop and wire assembly to mirror:
```python
    r0 = spline_start(pr, fillet)  # where the involute spline starts
    radii = [r0 + (pr.ra - r0) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
    pitch = 2 * math.pi / pr.z
    ...
        left = [_polar(rho, c - pr.half_angle(rho)) for rho in radii]
        right = [_polar(rho, c + pr.half_angle(rho)) for rho in reversed(radii)]
    ...
        edges.append(cq.Edge.makeSpline(left))
        edges.append(cq.Edge.makeThreePointArc(left[-1], _polar(pr.ra, c), right[0]))
        edges.append(cq.Edge.makeSpline(right))
        ...
        edges.append(cq.Edge.makeThreePointArc(start, _polar(pr.rf, c + pitch / 2), end))
    return cq.Wire.assembleEdges(edges)
```
Under trochoid, the first involute point is the curve's last `Vector` object, not a recomputation (a 1e-6 gap opens the wire).

**`_gear_blank`** (190-193) and **`_build`** (540-552): thread `rm.curve`. `_build` calls `root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` and passes `root_fillet(p)` unchanged for radial:
```python
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
```
Import `RootCurve` and `root_mode` from `.calc` (block at model.py ~40-45); do not import `cutter`, `trochoid_root`, `_root_curve`, `_junction` (source-grep test).

**Guard wording** (copy from `_tip_edges`, 530-535 and `_NOT_A_BODY` uses at 361/434/444): raise `BuildError` with "a modelling defect in spur, not a conflict in these parameters."
```python
        raise BuildError(
            "Tip chamfer selected no tip-arc edges: a modelling defect in spur, not a "
            "conflict in these parameters. Set tip_chamfer to 0 to build this gear "
            "without it.")
```
**Error path to know:** `_build_checked` (555-562) relabels any non-`BuildError` kernel exception as "try smaller fillets or chamfers." That is the wrong remedy for the degenerate-root-arc `Standard_Failure`, so the `ROOT_ARC_MIN` branch must avoid the raise rather than rely on this wrapper.

`_tip_edges` (510-538) selects `CIRCLE` edges at `ra`; trochoid edges are `BSPLINE`, so it needs no change (compose test proves it).

---

### `src/spur/cli.py` and `src/spur/static/app.js`

**No code change expected** for the field. `cli.py:45-49` routes any `Literal` through `choices=`:
```python
        if get_origin(field.annotation) is Literal:
            g.add_argument(flag, dest=name, default=None, help=help_text,
                            choices=list(get_args(field.annotation)))
```
`app.js:64-67` renders `prop.enum` as `<select>`. Only the `DIMS` table changes (rows at `app.js:21-23`, shape `['key', 'Label'],` is regex-extracted by `tests/test_api.py:130`):
```js
  ['root_thickness', 'Tooth at root'],
  ...
  ['root_fillet', 'Root fillet used'],
```
Add `['root_form_d', ...]` and the waist row in the same shape; `renderInfo` skips null rows.

---

### `tests/test_cli.py` : field walk (generalise the exemption)

**Analog:** lines 205-215. Replace the hard-coded name with the model-driven Literal list (RESEARCH Pattern 6); also update the docstring that says `recess_sides` is the exempt field.
```python
    for name in names:
        prop = props[name]
        ...
        if name == "recess_sides":
            assert "step" not in prop
        else:
            assert "step" in prop, name

    assert props["recess_sides"]["enum"] == list(
        get_args(GearParams.model_fields["recess_sides"].annotation))
```

### `tests/test_api.py`

- 314-315: second assertion breaks with D-02 placement; must become `root_shape` after `tip_chamfer`, `face_width` after `root_shape`:
```python
    assert names.index("tip_chamfer") == names.index("root_fillet") + 1
    assert names.index("face_width") == names.index("tip_chamfer") + 1
```
- 78-92: literal set of 29 `DerivedDimensions` names (`assert set(component["required"]) == fields`); add the two new names, and check how required/optional is handled for existing `float | None` fields before adding.
- 130: DIMS regex `re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)`.

### `tests/composition.py`

**Analog:** the `TIPS` / `ALWAYS` tables. `ALWAYS` (line ~50) lists `root_thickness`, `root_gap` as non-null on every row; wrong for any row with `root_shape: "trochoid"`. Add a separate trochoid column rather than editing `ALWAYS`. House rule from the module docstring: tables are hand-written, never computed from `spur.calc`.
```python
TIPS: dict[str, dict[str, object]] = {
    "off": {},
    "on": {"tip_chamfer": 1.75},   # the default 19-tooth gear's pitch-circle cap, no warning
}
```

### `tests/test_trochoid.py`

**Analog:** the existing refusal and fixture tests. Reuse helpers `_gear(**fields)` (81) and `trochoid_oracle`; refusal parametrize shape at 538 `(fields, mode, reason, sentence)`; fixture guard at 455 (`test_every_pre_v0_2_record_reads_radial_because_nobody_asked`) which now should assert the same through `root_shape` default. Calc-tier tests stay in `verify.fast`.

### `tests/test_model.py`

**Analog:** spy tests 416-450 (`monkeypatch.setattr("spur.model._tip_edges", spy)`) for guard tests; line 468 shows `e.positionAt(0.5)` use. Kernel tier per RESEARCH Pattern 7: select root BSPLINE edges by position, assert count `== 2 * teeth` (L26: a selector that selects nothing must fail), sample 41 points, feed `trochoid_oracle.clearance` with `derive(p).root_fillet` as rho. Add a source-grep test that `model.py` names no generator symbol, following `test_calc_module_stays_log_free` in `tests/test_records.py`.

### `bench/trochoid.py`, `bench/sweeps/trochoid.json`, `tests/test_bench.py`

**Analog:** `bench/trochoid.py` `main()` (867-876) adds subcommands the same way:
```python
    sub = parser.add_subparsers(dest="scenario", required=True)
    sub.add_parser("epsilon", help="measure TROCHOID_JOIN_EPS (D-09)")
    ...
    sub.add_parser("step", help="the root-shape step at both boundaries (D-05)")
```
Reuse `tuned_shift` (84) for the tuned-backlash short-arc test. For the chamfer re-bisection copy `bench/tip_chamfer_spike.py` (`tip_arcs` 35, `chamfered` 56, `boundary` 189, `main` 304, header docstring "not part of `make verify`", prints Markdown, exits 1 on failed verdict, `machine_facts` from `bench`). Use the 20-step bisection of L29. Sweep file is a JSON list of flat dicts of `GearParams` fields (see `tip_chamfer.json`: `teeth`, `module`, `tip_chamfer`, `recess_sides`); add `root_shape: "trochoid"`. `tests/test_bench.py` imports pure predicates from `bench.trochoid` (line 55) and tests them without building; follow that for any new pure helper (floor/bar predicate).

### `bench/RESULTS.md`, `docs/architecture/decision_log.md`

- RESULTS: new `## Trochoid in the part (Phase 19)` after line 3035's section; each figure with host, load, kernel pair, date (F10: M5 Max host here vs L34's M2 Max host).
- Log: next id L38. Header form `## L37 — <title> (amends L31 and L32)` at line 1995; entries end with a Reversibility paragraph, `Reason:` and `Machine:` lines (see tail of file). Title: supersedes L10, amends L09 and L33.

## Shared Patterns

### Fixture byte-identity (applies to every src/ task)
**Source:** `tests/regression/pre_v0_2.json`, `tests/regression/test_pre_v0_2.py`. Run `git diff --exit-code tests/regression/pre_v0_2.json` after each task. Every new `DerivedDimensions` field is `None` on replay and in radial mode; radial `_outline` is untouched.

### One predicate, one sentence source
**Source:** `calc.root_mode` (1509) and `calc.root_warnings` (1572). `derive`, `_build`, `tip_chamfer_limit` all call `root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)`; no other place decides mode; tests capture sentences from `root_warnings`.

### Honest-number comments and constants
**Source:** `calc.py:15-62` (`TIP_CHAMFER_MARGIN`, `ROOT_CONTACT`). A module constant carries date, host, the two bracketing measurements and headroom in its comment. Apply to `ROOT_ARC_MIN`, the guard bars and the waist floor. ruff `N` forbids upper-case locals; `ERA` flags comment text shaped like code; `calc.py` never imports `cadquery`; `model.py` never names the generator.

### BuildError for defects
**Source:** `model.py:530-535`, `:551`. Guards raise `BuildError` with "a modelling defect in spur, not a conflict in these parameters"; refusals of user input stay `GearParams`/`check()` (no new `check()` refusal this phase).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Guard helpers in `model.py` (coincident vectors, spacing ratio, annulus bounds, area check) | utility | transform | No existing structural geometry guard besides `_tip_edges`' selector check and `isValid()`; use RESEARCH Pattern 4 numbers and the wording above |
| Kernel-tier `positionAt` vs oracle test | test | transform | Only `positionAt` spot use at `test_model.py:468`; no existing oracle-vs-solid test; use RESEARCH Pattern 7 |
| Undercut waist field and floor constant | model field | transform | No existing measured-then-pinned floor on a printed number beyond `MIN_TIP_FDM`/`MIN_WALL` style constants; floor goes to a human checkpoint (D-07, Open Question 1) |

## Open conflicts the planner must carry (from RESEARCH)

- SC5 "exit 2" for new refusals vs `docs/architecture/cli.md` (BuildError exits 1; only `GearParams` boundary errors exit 2); this phase adds no new `check()` refusal. Ask the human before writing the test.
- `tests/test_api.py:315` is a second adjacency pin broken by D-02 placement.

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `bench/`, `docs/architecture/decision_log.md`
**Files scanned:** about 20 targeted reads
**Pattern extraction date:** 2026-10-08
