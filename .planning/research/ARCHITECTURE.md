# Architecture Research: v0.4 True Root

**Domain:** parametric involute spur gear generator (shipped; subsequent milestone)
**Researched:** 2026-10-06
**Scope:** integration of three features into the existing code. Nothing here re-researches the gear maths (that is STACK/FEATURES/PITFALLS territory) or re-derives the race diagnosis.
**Confidence:** HIGH on every seam, file and line cited (each was read this session); MEDIUM on the trochoid geometry itself (not researched here); every inference is marked `ASSUMPTION:`.

Measured by me this session, scratch only, nothing committed and no repo file modified: the fixture counts in section 1.5 (a script over `tests/regression/pre_v0_2.json` and the repo's own `calc`), and the pre-fix race reproduction in section 2.2 (`BuildPool(workers=2, timeout=1)` against `HEAD`).

## 0. Two corrections to the brief, found by reading the files

1. **`calc.py` does not compute outline points.** It holds the *decisions* (`root_fillet(p)` at `calc.py:224`, `spline_start(pr, fillet)` at `:230`, `Profile.half_angle(rho)` at `:85`, `_tooth` at `:211`). The points are built in `model.py::_outline` (`model.py:133-185`) with `cq.Vector`, `_polar` (`:94`) and `_fillet_corner` (`:98`). The analytic fillet is therefore *split*: radius and cap in calc, tangency maths in model. A trochoid generator that stays pure must be a **new** pure function in `calc.py` that returns plain floats; it cannot be "beside the analytic fillet" in the sense of living where the fillet's geometry lives, because that code imports `cadquery`.
2. **"Below the base circle" is not "undercut".** The radial lead-in exists whenever `rb > rf` (`Profile.r_start = max(rb, rf)`, `calc.py:81-83`), which includes the stock 19-tooth gear (`rb - rf = 0.63 mm`). `derive()`'s undercut warning is a different, narrower test, `teeth < 2(1-x)/sin^2(alpha)` (`calc.py:1006-1009`; 11.2 teeth at 25 degrees, x = 0). Section 1.5 counts both against the fixture. The root-mode decision turns on which of the two "A" means.

## 1. Feature A: the trochoidal root

### 1.1 What the outline contract with the kernel is today

`_outline(pr, fillet)` returns one closed `cq.Wire` from `cq.Wire.assembleEdges(edges)` (`model.py:185`). Per tooth, in order (`model.py:164-184`):

| Edge | Built with | Present when |
|---|---|---|
| fillet arc (root circle to line) | `makeThreePointArc(fl[0], fl[1], fl[2])` from `_fillet_corner` | `straight and fillet > 0` |
| straight lead-in line | `makeLine` | `r0 > pr.rf + 1e-6` (`straight`) |
| left involute flank | `makeSpline(left)`, 16 points at `r0 + (ra-r0)*(i/15)**1.5` | always |
| tip arc | `makeThreePointArc(left[-1], _polar(ra, c), right[0])` | always |
| right flank, line, fillet arc | mirror of the above | as above |
| root arc to next tooth | `makeThreePointArc(start, _polar(rf, c + pitch/2), end)` | always |

Facts that bound a trochoid edge:

- **Splines are interpolated, not fitted.** `cq.Edge.makeSpline(listOfVector, ..., tol=1e-6)` is `GeomAPI_Interpolate` (read from the installed cadquery 2.8.0 source); its docstring says `tol` checks that points "are not too close to each other" and interpolation "may fail" if they are. A trochoid sample list needs point spacing well above 1e-6 mm, and a cusp or a near-coincident pair at the junction will fail inside the kernel, not in calc.
- **Joins are by coincident endpoints.** `assembleEdges` is `BRepBuilderAPI_MakeWire` over an unordered list; the existing joins hold because both sides are computed from the same float (`fl[2]` is the line's start and the arc's end; `left[0]` is the spline's first point). The trochoid-to-involute junction must share one float pair the same way: `RootCurve`'s first point and the flank's first point must come from one call, not two roundings.
- **Kinks are already tolerated.** The chord-to-spline joint at `left[0]` is not tangent today (that is what L33's lead-in warning is about) and builds. A non-tangent trochoid/involute junction (the undercut case) is not a new class of input.
- **The kernel limit that matters is the tip chamfer.** `tip_chamfer_limit` (`calc.py:258-281`) caps the chamfer at `ra - spline_start(pr, root_fillet(p)) - TIP_CHAMFER_MARGIN` because the kernel "cannot carry an end-face chamfer from the involute spline across onto the straight lead-in" (`calc.py:235-238`, `bench/RESULTS.md` "Tooth-tip chamfer spike"). Whether it can cross a spline-to-spline junction is **unmeasured** and needs the same bisection spike before the third bound can be called moot.
- **Face counts change by construction.** Extrusion makes one face per edge. Per tooth the radial path has 8 side faces (2 fillet arcs, 2 lines, 2 flanks, tip arc, root arc); a trochoid replaces arc + line with one spline per side, so 6. Any hard-pinned topology count for an affected gear moves; the default gear's pin (172 faces / 490 edges, `test_pre_v0_2.py` docstring) moves only if the default gear is affected (section 1.5).

### 1.2 Recommended structure

```
GearParams (frozen, validated once)                     params.py
   |  [B only] root_shape: Literal["radial","trochoid"] = "radial"
   v
calc.profile(p) -> Profile                              calc.py:91
calc.root_fillet(p) -> rho (cutter tip radius, ASSUMPTION: reuse this field)
   |
   v
calc.trochoid_root(pr, rho, ...) -> RootCurve | None    NEW, pure stdlib math
   |   RootCurve (frozen dataclass, like Profile):
   |     junction radius, junction half-angle,
   |     points: ((rho, half_angle), ...) junction -> root-circle tangent point
   |   None = cannot be computed honestly (L08) -> radial path + a warning
   |
   +--> calc.root_mode(p, pr) -> bool   NEW single predicate "trochoid active?"
   |
   +--> calc.spline_start(pr, fillet, root=None)  MODIFIED: returns the junction radius
   |       when a RootCurve is active (default arg keeps the 2-arg call sites that
   |       tests/test_calc.py:765, :811, :839 and bench/tip_chamfer_spike.py use)
   |
   +--> calc.derive(p) : new field + warnings (1.4)
   |
   v
model._build(p) -> _gear_blank(pr, fillet, root, face_width) -> _outline(pr, fillet, root)
        _outline: when root is not None, per tooth replaces [fillet arc + line]
        with makeSpline([_polar(rho, c -/+ ha) for rho, ha in root.points]);
        the involute spline starts at root.junction radius (same float).
```

Why calc owns it: `model.py` "builds; it does not decide" (`solid-model/strategy.md`); the calc/kernel boundary is an import-linter contract (`pyproject.toml:167`); and calc tests cost 0.06 s for 404 tests (`bench/RESULTS.md` "Per-file share"), so the oracle comparison belongs in the cheap tier, not in `test_model.py` (74 % of pytest's seconds). `RootCurve.points` is deliberately `(rho, half_angle)` pairs, exactly what `_outline` already forms for flanks (`_polar(rho, c - pr.half_angle(rho))`), so the model-side change is one `makeSpline` per side and the mirror is free.

`Profile.half_angle(rho)` is documented "rho >= rb" (`calc.py:85-89`, `acos(min(1.0, rb/rho))`); the trochoid region is below `rb` where it is meaningless. The generator must not reuse `half_angle` below the junction.

### 1.3 Where the junction is computed

In calc, inside `trochoid_root`. For a gear that is undercut the involute is truncated where the trochoid crosses it, so the junction is a root of a one-variable equation; for a gear that is not, the curve is tangent to the involute at a point fixed by the cutter. Either way solve by **bisection on a bracket where the function is monotone**, the project's own precedent (`_involute_angle`, `calc.py:1158-1171`: "no starting guess that can send it outside the bracket"; `centre_distance` returning `None`, L08). A failed bracket returns `None`, never a clamped plausible radius. `ASSUMPTION:` the monotone bracket exists on the whole parameter box (teeth 6-200, alpha 14.5-35, x -0.6 to 1.0, `params.py:34-44`); that is a phase-2 research item and a sweep test, not something to assume.

`ASSUMPTION:` the cutter tip radius is `root_fillet(p)` (default 0.5 mm, field label "Root fillet", `params.py:47`): a hob's corner radius *is* the root fillet radius, so no new cutter input is needed and the field keeps one meaning. Alternatives (a new field, or a standard's tip-radius constant) each add an input or an unsourced number (L08). The cap `min(p.root_fillet, 0.45 * gap)` in `root_fillet()` (`calc.py:224-227`) is a gap-fit rule for the radial model; in trochoid mode neighbouring trochoids can overlap at low tooth counts, so the cap needs its own bound (L03: trim and warn, not refuse). That cap makes `root_fillet(p)` mode-aware; it must read the same predicate as `_outline`.

### 1.4 What `derive()` changes

| Item | Today | In trochoid mode | Note |
|---|---|---|---|
| `root_d` (`calc.py:1119`) | `2*rf` | unchanged | the cutter tip still reaches `rf = r - m(1.25 - x)` (`calc.py:97`); every rim-wall, recess and cutout rule reads `rf` and is unaffected |
| `root_thickness`, `root_gap` (`:1123-1124`, from `_tooth`, `calc.py:211-221`) | arcs "on the root circle", from `half_angle(r_start)`, "below the base circle the flank is radial" | not measurable: a trochoid touches `rf` at one point | L08: print null plus a sentence, do not print the radial model's number for a part that no longer has that profile. Needs `float` -> `float | None` on two currently non-optional fields (`DerivedDimensions`, `calc.py:840+`). `app.js` already skips null rows (`app.js:139`). `_tooth` itself stays untouched: `check()` (`:541+`, tip/gap refusals) and `root_fillet`'s cap still consume it identically in both modes |
| new `root_form_d: float \| None` | n/a | diameter where the involute begins above the trochoid (the true-involute-form diameter an inspector reads) | null with a radial root, so additive and replay-safe (the replay requires every post-capture field to read null, `test_pre_v0_2.py:49`). An mm length: `DIMS` prints every value as `... mm` (`app.js:144`), so no angle or flag goes in it. Add one `DIMS` row (`app.js:13-38`); the field walk forbids per-field JS outside `DIMS` (`test_api.py:180-199`) |
| lead-in warning (`:973-994`, L33) | fires when `round(spline_start - r, 3) > 0` | must not fire on a trochoid root (no chord exists) | one `if`, reads the same predicate |
| undercut warning (`:1006-1009`) | `"Below {z_min:.1f} teeth a cut gear would be undercut; this model uses a radial root instead."` | the sentence is false in this mode | restate from evidence: undercut iff the junction radius exceeds `rb` at the printed 3 dp (the lead-in warning's own "compare at the resolution it prints" rule). Whether the textbook `z_min` agrees with that exact criterion for this cutter (tip radius, 1.25 m dedendum) is exactly the "re-stated or retired on evidence" question: answer it with a calc-only sweep around the threshold, in the style of `test_centre_distance_matches_an_independent_solver` |

Keep the old warning byte-identical for the radial mode: five fixture records carry its exact text (`pre_v0_2.json:582,632,948,996,1588`) and the replay compares warnings exactly.

Keystroke cost: `derive()` is documented at ~11.5 microseconds and "fast enough to run on every keystroke" (`calc.py:946+` docstring). A bisection plus N samples is more. Measure and record it, as that docstring does; under B it costs nothing for default links (predicate false), under A it costs only gears below the limit.

### 1.5 The root-mode decision, costed (counted this session against the fixture)

44 records: 39 built, 5 mate-only. Computed with the repo's `profile()` over each record's `params`:

| Definition of "trochoid applies" | Records | Built | Includes the stock gear? |
|---|---|---|---|
| radial lead-in exists (`rb > rf`) | 28 | 23 | **yes** (19 teeth, m 1.75, 25 degrees) |
| derive's undercut test (`teeth < z_min`) | 5 | 3 | no |

The three built undercut records are the 6-tooth `{x -0.6, 14.5 degrees}` of `test_api.py::test_impossible_mate_is_a_warning_not_a_number`, the 6-tooth `{x -0.5, 14.5 degrees}` of `test_calc.py::test_impossible_pairs_have_no_centre_distance[1]`, and the 8-tooth m 1.5 of `test_model.py::test_builds_one_valid_solid[7]`; the two mate-only records are their `+mate` twins. By the code's own formulas the radial lead-in can only exist below `2(1.25 - x)/(1 - cos alpha)` teeth (26.7 at 25 degrees, x = 0; 116.2 at the box corner x = -0.6, 14.5 degrees), so even the broad definition never reaches the 200-tooth gears that set the build-time timeout margin.

**Option A: always-on.**
- Seam: the predicate is derived from geometry, no `GearParams` change.
- L05: every shared link below the limit that omits any new field changes part and changes its printed numbers. Under the narrow definition that is real low-tooth-count gears (the ones people cut); under the broad one it is the stock link. L33 already refused this class of change once ("regenerates the pre-v0.2 fixture ... changes the part of every shared link", `decision_log.md` L33), so A reverses a prior human choice for a different reason; it needs its own `Lxx` superseding L10 and amending L33.
- L26, which records move (narrow definition): 5 `derived` blocks (the warning text, plus `root_thickness`/`root_gap` if nulled, plus the new `root_form_d`), 3 `solid` blocks (`faces`, `edges`, `volume`; bbox unlikely but unproven until measured), and one added null field in the other 39 `derived` blocks; `provenance.git_head` and `captured` rewrite. 39 records must be otherwise byte-identical, and the regen diff is the review control for that.
- **Commit-shape problem (finding):** the replay goes red on 5 rows the moment the behaviour changes, and the pre-commit hook runs the whole gate, so the feature commit cannot land without the regenerated fixture; L26 D-03 says the fixture "never changes in a feature commit". Workable shapes: (1) build the generator and field under B first (default off, fixture untouched), then a *single* final commit that flips the predicate and runs `make fixture.regen`, carrying the new `Lxx` (L26 names "a deliberate contract change carrying its own `Lxx`" as a legitimate regen reason, and the flip commit is the fixture's "own commit"); (2) one combined commit, which needs the new `Lxx` to amend D-03's wording. A flag-guarded dead branch merged ahead of the flip is not a third shape: `CLAUDE.md` forbids unreachable branches presented as finished.
- Kernel risk lands on the most hostile inputs first: the 6-tooth, x = -0.6 records are in the regen set.

**Option B: a new default-off field.**
- Name and type: `root_shape: Literal["radial", "trochoid"] = "radial"` (name is the discuss-phase's; the shape is the point). It must be a `Literal`, not a `bool`: `cli.py:47-56` handles `Literal` through `choices=` and everything else through `type=field.annotation`, and `type=bool` makes `--flag false` read as true; `app.js:64-66` renders `prop.enum` as a `<select>` and everything else as `<input type=number>`. The one precedent is `recess_sides` (`params.py:91-93`, written with plain `Field`, not the numeric `_f` helper). Group `"Teeth"` (after `root_fillet`/`tip_chamfer`) so the pinned seven-group order holds (`test_cli.py` field walk).
- Validation: pydantic rejects other strings as a 422 for free. No `check()` rule is needed: a request that does not apply (`rb <= rf`, nothing radial to replace) is not a conflict between two user choices (L03), it is an ignored field, warned in the existing sentence shape ("No spoke arms with spoke_count 0: ... is ignored", `calc.py` `derive`, D-15).
- Form and CLI: free. `InfoQuery`/`ModelQuery` subclass `GearParams` (`app.py:227-234`); `/api/schema` is `GearParams.model_json_schema()` (`app.py:370`); `cli._add_gear_args` iterates `model_fields`; `gearQuery()` omits any value equal to its default (`app.js:100-107`), so a link without the field is "radial".
- Test edit this forces: `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (`test_cli.py`) hard-codes `recess_sides` as the single enum with no `step` (`if name == "recess_sides": assert "step" not in prop else: assert "step" in prop`); the new enum needs the exemption generalised. Also README's parameter table (around `README.md:175-185`) is hand-written and unchecked.
- L05: honoured by construction. L26: the 44 records replay unmodified with no regen, because the replay builds `GearParams` from each record's own fields, the new field defaults to `"radial"`, and every new derived field is null; the proof is `git diff --exit-code tests/regression/pre_v0_2.json` plus the unmodified 85 cases, as Phases 8-16 did.
- Cost: a second user-facing control for what, to the user, is one gear. If the human wants it always-on eventually, B is the staging for A.

**Recommendation (the human's call, per PROJECT.md):** build the seam as B, with the one `root_mode` predicate. A is then one function body changing plus one regen commit, and everything the known-good proof and the kernel spikes need exists before any shared link moves. If A is chosen, use the narrow (`teeth < z_min` / junction above `rb`) definition: the broad one changes the stock gear's part and makes L05 an exception rather than a rule.

### 1.6 The known-good-profile test: data flow

- **Reference lives in `tests/`, not `src/`.** Precedent: L33's `_filleted_spoke_volume` oracle "never calls `_fillet_corner`" so a wrong root "disagrees with the oracle instead of moving both sides together" (D-09). The trochoid oracle must share no code with `calc.trochoid_root`: an independent derivation (closed-form parametric envelope of a straight-flanked, round-cornered rack, or a brute-force rack-envelope simulation at far higher resolution), evaluated in the test module. A snapshot captured from the implementation proves nothing; the L26 fixture is exactly that kind of artefact and must not be mistaken for the known-good reference.
- **Two tiers.** (1) calc tier, no kernel, fast: sampled points of `RootCurve` vs the oracle curve; the junction radius vs the oracle's; the `z_min`-vs-junction agreement sweep (1.4); the bisection bracket sweep over the parameter box. (2) kernel tier, a handful of rows: build a small gear (6 and 8 teeth already build in the pinned set), take the end-face wire, sample `Edge.positionAt` along the trochoid edges and compare radial distance to the oracle; this is what catches the spline interpolation error and a wrong tooth rotation. Geometric assertion, not a snapshot (`solid-model/tests.md` style).
- **Provenance of any external data.** `ASSUMPTION:` "a known-good undercut profile" is not in the repo; if it is a published table or a CAD export, it lives as a committed data file with its source and licence named, loaded by the test; its provenance is a discuss-phase question, because an unsourced reference is a plausible number (L08).
- **Tolerance.** Not chosen here. Follow the L33 14-04 rule: measure the implementation-to-oracle gap per row, set the bar with stated headroom, and when headroom is under about 10x, put the bar to the human at a checkpoint (D-06; the `abs=1e-8` precedent). The spline's 16-point interpolation error is itself a measured input; sample count and spacing are set from it, not guessed.

### 1.7 Other consumers that need a look

- `tip_chamfer_limit` / `tip_chamfer_effective` (`calc.py:258-291`): read `spline_start`; pass the active root through so the cap and the outline keep reading one radius.
- `_tip_edges` (`model.py`, selects tip arcs by radius and end-face endpoints, raises `BuildError` on an empty selection, L26): trochoid edges are not circles at `ra`, so unaffected in principle; the compose test (trochoid x tip chamfer at its cap x recess x each cutout) proves it. The undercut gears are small (below 52 teeth under the narrow definition), so build time is not the constraint it was at 200 teeth, but record a row in `bench/` anyway (`CLAUDE.md`: performance claims are measured).
- Docs that state the radial claim: `README.md:222-224`, `docs/architecture/gear-maths/strategy.md` ("L10 - the root is radial..."), `docs/ideas/2026-09-21-trochoidal-root-fillets.md` (idea becomes implemented), `docs/architecture/decision_log.md` L10 (`Revisit`); the new `Lxx` supersedes or amends L10 and carries the measurements.

## 2. Feature B: the same-slot timeout race

### 2.1 The shape of the identity check

`_run_with_timeout` (`pool.py:157-219`) captures `executor = self.executor_for(p)` once (`:169`). In the `except TimeoutError` branch (`:184`) it loops `executor._processes.values()` (`:204-205`) and then `self.recreate_for(p, executor, "timeout")` (`:206`). `recreate_for` already guards itself with `if self._executors[i] is not executor: return` (`:123-125`) and then `shutdown(wait=False)`s the old executor and installs a new one (`:151-153`). After `shutdown`, `executor._processes` is `None`, so a sibling's loop at `:204` raises `AttributeError`, which `app.py`'s `except` chain does not map (it reaches the `except Exception` log-and-reraise and uvicorn's 500).

Narrow fix: compare identity before touching `_processes`, using the live slot:

```python
        except TimeoutError:
            if self.executor_for(p) is executor:      # this slot still holds our executor
                for proc in executor._processes.values():
                    proc.terminate()
                self.recreate_for(p, executor, "timeout")
            raise BuildTimeout(...) from None         # unchanged either way
```

`executor_for(p)` is `self._executors[hash(p) % self.workers]` (`:96-97`), the same index `recreate_for` computes (`:123`); there is no `await` between the check and the loop, so on the single event-loop thread the check cannot go stale. A sibling that finds the slot already replaced skips the terminate (the first caller already terminated the shared process) and still raises `BuildTimeout`, the documented 503 `timeout` (`app.py`, `type: "timeout"`). `recreate_for`'s guard stays (the `BrokenProcessPool` branch at `:211-219` still depends on it). Nothing else moves: not `recreate_for`, not `app.py`, not the `worker.replaced` record (still one per incident, emitted inside the guard, as the docstring at `:114-121` requires).

Touching `_run_with_timeout` fires the revisit trigger of two `nice` debts (`docs/tech_debt/INDEX.md`): the lost worker-coverage flush (trigger names `BuildPool.shutdown`/`_run_with_timeout`) and the `resource_tracker` flake (trigger names `tests/test_pool.py`'s shutdown path). The plan should schedule a read of each, not necessarily a fix.

### 2.2 The test that proves it, with injected timeouts

Verified this session on current `HEAD` with a throwaway script (`BuildPool(workers=2, timeout=1)`, `GearParams(teeth=21)`, a module-level sleeping function, tasks created with no `await` between them, `asyncio.gather(..., return_exceptions=True)`):

| Shape | Result before the fix |
|---|---|
| 3 same-slot requests, same tick | `[BuildTimeout, AttributeError("'NoneType' object has no attribute 'values'"), AttributeError(...)]`, `replaced == 1` |
| 2 same-slot requests, same tick | `[BuildTimeout, AttributeError]`, `replaced == 1` |
| 3 requests, siblings 0.5 s later (the existing test's shape) | `[BuildTimeout, BrokenProcessPool, BrokenProcessPool]`, `replaced == 1` |

Why it is deterministic: the wait timers fire in one loop pass, each task's step then runs in the next batch; the first runs terminate-and-recreate synchronously (no `await` in the branch), and the manager thread's `BrokenProcessPool` delivery reaches the loop only after that batch. `ASSUMPTION:` the ordering argument is inferred from asyncio internals; the three runs above are the evidence, so the committed test must itself be seen red before the fix (the existing tests record that discipline: "VERIFIED ... pre-fix and post-fix").

The test, in `tests/test_pool.py` beside `test_four_same_slot_requests_all_refuse_without_cancellation` (`:400`) and `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` (`:492`), reusing `_sleep_past_timeout`, `_event_records`, `_field` and the `with TestClient(app): pool = app.state.pool` idiom:

- `pool.timeout = 1.0` (restored in `finally`, as the neighbours do); create 3 tasks of `pool._run_with_timeout(params, _sleep_past_timeout, 10.0)` in one tick (no gap, no `sleep(0)`), gather with `return_exceptions=True`.
- assert every result `isinstance(r, BuildTimeout)` (not `AttributeError`, not `BrokenProcessPool`); `pool.replaced == replaced_before + 1`; exactly one `worker.replaced` record with `cause == "timeout"` and the slot index; the next request on the slot runs on a new pid.
- Keep the existing 0.5 s-gap test unchanged: the pair delimits the two windows (same-tick sibling gets `BuildTimeout`; later sibling gets `BrokenProcessPool`, both documented 503s).
- Cost is about one injected timeout plus a worker respawn; the neighbours read 4.4-5.2 s serial (`bench/RESULTS.md` "Slowest 25"). Coverage: the new false-arm of the `if` is covered only by this test (`fail_under = 96`).

### 2.3 The ten-identical-worst-row scenario in `bench/latency.py`

Registry facts: `_SCENARIOS` (`latency.py:321-325`) maps name to `Callable[[str], ScenarioResult]`; argparse `choices=sorted(_SCENARIOS)` picks up a new name for free; `DEFAULT_SCENARIOS = ("concurrent", "single")` (`:332`) must **not** gain it (the comment at `:327-331` exists because a scenario that times out and replaces a worker would pollute the bar); the worst row is `COMPOSED_ROWS[0]` = index 3 of `bench/sweeps/composed.json` (200 teeth, module 10, 32 spokes, tip chamfer 3, keyed bore, both recesses), read by `_composed_rows()` as raw JSON because `latency.py` must not import `spur.model` (`:136-155`).

Changes:
- `run_composed(base_url)` (`:219`) reads `_composed_rows()` itself; give it an optional `rows` argument and a scenario label, and add `scenario_identical` passing `[worst] * 10`. Ten identical `GearParams` hash to one slot by construction (`hash(p) % workers`, D-07), so no hash-affinity luck is involved; admission control (`MAX_QUEUED_BUILDS` 4, `app.py:100`) takes four, all on that slot. There is no single-flight in `app.model()` (`app.py:380+`): each identical request misses `_EXPORTS`, takes its own slot.
- **`_fetch` raises on a 500** (`latency.py:181-204`, `raise_for_status()`), and `tests/test_bench.py::test_a_503_is_recorded_by_the_reason_the_server_gave` pins that (`pytest.raises(httpx.HTTPStatusError)`). Reproducing "the old 500" requires recording it, so add a keyword (for example `record_500=False`) that turns a 500 into status `"500"`; the default and the pinned test stay as they are.
- `_report_markdown` suppresses the recorded-baseline line only for `name == "composed"` (`:354-358`); extend that test to the new name. `test_the_no_argument_latency_run_is_still_concurrent_then_single` asserts `set(_SCENARIOS) == {"concurrent","single","composed"}` (`test_bench.py:604`): a deliberate edit.
- What it measures is a before/after pair on a **fresh** server (the existing `held`/`_pool_state` checks enforce that): before the fix `500` rows and `workers_replaced` +1; after, only `200` / `503 timeout` / `503 busy` / `503 pool_broken`. It is bench, not gate (D-16). `ASSUMPTION:` which of requests 2-4 time out depends on build plus export time for a cached solid (later siblings pay export only, since `_build_cached` hits); that is exactly what the run records, so do not state the expected row mix in advance.
- The margin finding (worst row 29.42 s alone, over 30 s under contention) is a *separate* decision on `SPUR_BUILD_TIMEOUT` (`app.py:146`), a cap (`params.py` `spoke_count`), or a recorded limit; it follows the measurement, not the other way round.

## 3. Feature C: the commit-timeout vs the 64 s hook

Facts: gsd's SDK commit passes `timeout: COMMIT_TIMEOUT_MS` to `git commit` (`~/.claude/gsd-core/bin/lib/commands.cjs:2441`, constant at `:3794`, hard-coded 30 000; the debt file's `:3655` is stale). The hook is one `verify` hook, `stages: [pre-commit]`, `always_run: true` (`.pre-commit-config.yaml:21-32`). Gate cost, warm: 63.555 s at `-n 8` with coverage (L34); the four static stages read 0.07 + 0.37 + 0.11 + 0.02 = 0.57 s (P1) and 0.03 + 0.20 + 0.09 + 0.01 = 0.33 s (P2), pytest being 99.75 % and 99.85 % of the serial gate (`bench/RESULTS.md:2314-2317`). Cold mypy and a cold OpenCascade page-in are not measured separately; measure before claiming any sub-30 s figure.

| Option | Lives in | Guarantee change |
|---|---|---|
| (a) upstream knob | nothing in the repo; gsd-core code | none locally; every SDK commit still dies, so every executor commit in every later phase is a hand `git commit`. gsd already has a `--no-verify` path (`cmdCommit(..., noVerify, ...)`, `commands.cjs:1746`, `:2398`) but its own workflows forbid using it by default (`references/git-integration.md:65`, `workflows/execute-phase.md:674`). Reject as a fix; at most record it |
| (b) `make verify` at pre-push | `.pre-commit-config.yaml`: add `pre-push` to `default_install_hook_types` (`:18`), `stages: [pre-push]` on `verify`; `no-skip-token` stays at `commit-msg`. Re-run `pre-commit install` per clone (hook files are per-clone state outside git; the file header already documents this pattern, `:15-17`) | a red commit can exist locally and on a phase branch; it cannot reach `main` (ruleset, `pr.land`, CI: L22). The pre-commit stage runs on the staged tree; pre-push runs on the working tree, so it can pass on uncommitted edits; CI still tests the pushed content. `make worktree.land` (`Makefile`) runs `make verify` and then `git commit`, which today fires the hook a second time; under (b) that double run disappears. `gsd-ship`'s push is an agent shell command (`workflows/ship.md:195`), not the SDK's `execGit`; its tool timeout is the shell's, so a cold hook may exceed it (`ASSUMPTION:` Claude Code's default Bash timeout applies) |
| (c) sub-30 s pre-commit subset | `Makefile`: new target (for example `verify.fast: lint typecheck lint-imports no-fake-done`) and `verify: verify.fast test`, so the full gate is *defined as* the subset plus pytest and "one definition" stays structural; `.pre-commit-config.yaml`: the pre-commit hook runs `make verify.fast` | commit-time keeps the static half (about 0.6 s warm); pytest (99.75 %) moves out of the commit. This is the "tier the hook skips and CI runs" that L34 D-03 and `bench/RESULTS.md:2628` rejected for *cuts*; it is only coherent with the full gate living at pre-push, so (c) alone is a weaker (b) |

Opinionated recommendation (an `Lxx` is the human's): **(b) + (c) together**: static subset on commit, full `make verify` on push. It keeps cheap commit-time feedback, moves the 64 s off gsd's 30 s window, and leaves CI, the ruleset and `pr.land` as the wall. Amend L13 ("one command in three places") by adding that the *same command* still runs in three places and the hook stage moved; amend L34's closing sentence ("the commit-timeout debt stays active").

Places that say "pre-commit hook runs make verify" and must change in the same commit as the decision: `.pre-commit-config.yaml:1-3` header, `docs/HOW_TO_DEVELOP.md:23-26` (section 0, "One definition of passed in three places") and the section 6 ship-note paragraph that assumes a commit hook, `README.md:288`, `docs/architecture/packaging.md:49-51`, `.github/workflows/ci.yml:24-26` comment, `docs/architecture/decision_log.md` L13 (`:118-126`) and L34, plus `scripts/pr_land.py:67` (a stale "~42 s pre-commit hook" comment, drift only). `tests/` has no test reading `.pre-commit-config.yaml` (`git grep` found none), so the change is guarded by the docs and one live check: commit through the SDK and record that it returns `committed: true`.

## 4. New vs modified components

| Component | New / modified | What |
|---|---|---|
| `calc.trochoid_root`, `calc.RootCurve`, `calc.root_mode` | **new** | pure generator, frozen dataclass, single predicate |
| `calc.spline_start`, `calc.root_fillet`, `calc.tip_chamfer_limit`, `calc.derive`, `DerivedDimensions` | modified | optional root argument; mode-aware cap; new warning branches; `root_form_d`; `root_thickness`/`root_gap` nullable |
| `GearParams.root_shape` (B) | **new field** | `Literal`, default `"radial"`, group Teeth |
| `model._outline`, `_gear_blank`, `_build` | modified | consume `RootCurve`; trochoid spline replaces arc + line per side |
| `app.js` `DIMS` | modified | one row for `root_form_d` |
| `pool._run_with_timeout` | modified | identity check, 2 lines |
| `bench/latency.py` | modified | `rows` argument, `scenario_identical`, `record_500` |
| `.pre-commit-config.yaml`, `Makefile` | modified | per the hook option chosen |
| `tests/test_calc.py` + a trochoid oracle module | **new tests** | the known-good proof, the `z_min` sweep, the bracket sweep |
| `tests/test_model.py` | modified | kernel-tier rows, compose with tip chamfer / recess / cutouts |
| `tests/test_pool.py`, `tests/test_bench.py`, `tests/test_cli.py` | modified | same-tick test; scenario registry and `_fetch` rows; enum exemption in the field walk |
| `tests/regression/pre_v0_2.json` | **unchanged** under B; regenerated alone under A | via `make fixture.regen` only |
| docs: README, gear-maths docs, HOW_TO_DEVELOP, packaging, decision log, ideas, tech_debt | modified | new `Lxx` entries (hook, race/margin, trochoid, root mode, fixture if regenerated); two debt files retired in their fixing commits |

## 5. Suggested build order and dependencies

1. **Hook decision first** (`Lxx`, config, docs, `pre-commit install`), because every later executor commit runs under it; under (a) nothing ships and every commit is by hand. Dependency for everything below.
2. **Race, measure then fix then re-measure**: bench scenario edit, run on a fresh server (records the 500), `_run_with_timeout` identity check plus the same-tick test (seen red first), re-run (no 500), then the margin decision, and retire the debt file in the fixing commit. The two `must` items are Phase 1 per PROJECT.md.
3. **Trochoid generator and oracle, calc only**: `trochoid_root`, junction by bisection, the oracle, the `z_min`-vs-junction sweep, the bracket sweep, the keystroke timing. No model, no field, no fixture contact. This is the research-heavy step (cutter geometry, undercut onset with a tip radius, reference provenance, tolerance).
4. **Wire into the part under B**: `root_shape` field, `_outline`/`_gear_blank`/`_build`, `spline_start` and `tip_chamfer_limit`, `derive()` fields and warnings, field-walk and CLI/UI parity, kernel-tier rows, the tip-chamfer spike for a spline-to-spline junction, compose rows, build-time row, docs and the `Lxx` superseding L10. Gate: the fixture byte-identical (`git diff --exit-code`), 85 replay cases unmodified.
5. **Only if A is wanted: the flip**, one commit that changes `root_mode`'s predicate and runs `make fixture.regen`, with the `Lxx` stating what moved (5 `derived`, 3 `solid`, the added null field) and why; reviewed by the regen diff. Never mixed with 3 or 4.

Research flags: step 3 needs deeper research (the maths, the reference, the tolerance); step 4's kernel behaviour at the junction needs a spike; steps 1 and 2 are standard patterns with the evidence above.

## 6. Anti-patterns for this change

- **A trochoid generator inside `model.py`.** Puts the maths where it can only be tested through the kernel (the 74 % file) and where `calc.derive` cannot read the junction; `derive()` and `_outline` would drift (the failure `spline_start`'s docstring was written to prevent).
- **A `bool` field.** Breaks the CLI generator and the form silently (section 1.5).
- **Reusing `Profile.half_angle` below `rb`.** Undefined there.
- **Printing the radial model's `root_thickness`/`root_gap` for a trochoid part.** A plausible number for a profile that is not cut (L08).
- **Letting the feature commit carry the regenerated fixture** (L26 D-03) or regenerating to launder a red replay.
- **An oracle that imports the implementation**, or a tolerance chosen after seeing it pass (L33 D-06, D-09).
- **Widening `recreate_for`** to fix the race: its guard is correct (`pool.py:100-122`); the defect is the caller reading `_processes` first.

## 7. Open questions for discuss-phase

1. Root mode: A (narrow definition) vs B vs B-then-A; is the stock gear's root allowed to change? (Sections 1.5, 5.)
2. Cutter tip radius: reuse `root_fillet`? (`ASSUMPTION`, 1.3.)
3. `root_thickness`/`root_gap` in trochoid mode: null them (L08, type widening) or redefine at the form diameter?
4. The known-good reference: source, licence, and who sets the tolerance (1.6).
5. Hook: (b)+(c) vs (b) vs (a); who owns `pre-commit install` per clone.
6. Margin finding: `SPUR_BUILD_TIMEOUT`, a cap, or a recorded limit.

## Sources

- Read this session (HIGH): `.planning/PROJECT.md`; `docs/architecture/overview.md`, `gear-maths/*`, `solid-model/*`; `src/spur/calc.py`, `model.py`, `params.py`, `pool.py`, `app.py`, `cli.py`, `static/app.js`; `tests/regression/capture.py`, `test_pre_v0_2.py`, `corpus.py`; `tests/test_pool.py`, `test_bench.py`, `test_cli.py`, `test_api.py`; `bench/latency.py`, `bench/sweeps/composed.json`, `bench/RESULTS.md` (Phase 15 sections); both debt files and `docs/tech_debt/INDEX.md`; `docs/architecture/decision_log.md` L03, L05, L08, L09, L10, L13, L26, L33, L34; `.pre-commit-config.yaml`, `Makefile`, `.github/workflows/ci.yml`, `docs/HOW_TO_DEVELOP.md`, `README.md`, `pyproject.toml` import-linter contracts.
- External code read: `~/.claude/gsd-core/bin/lib/commands.cjs` (commit timeout, `noVerify`), `~/.claude/gsd-core/workflows/ship.md`, `references/git-integration.md`; installed cadquery 2.8.0 `Edge.makeSpline` and `Wire.assembleEdges` (via `inspect`).
- Scratch measurements (not committed): fixture counts (section 1.5), the three race runs (section 2.2), the tooth-count bound formula check.
