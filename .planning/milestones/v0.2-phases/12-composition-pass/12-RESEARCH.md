# Phase 12: Composition Pass - Research

**Researched:** 2026-09-29
**Domain:** Integration/measurement pass — no new cut, no new field; grounding the plan
against the exact current shape of `bench/`, the test surface, and the interface-parity
mechanism.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

D-01…D-23 are locked in `.planning/phases/12-composition-pass/12-CONTEXT.md` and are
**binding — this research does not re-litigate them.** Summary (full text in CONTEXT.md):

- **D-01…D-06 (the composed sweep):** a new `bench/sweeps/<composed>.json` stacking each
  cutout's heaviest row + tip chamfer at its cap + the heaviest bore the hub rule allows,
  at module 1.75 and 10 (~12 rows), plus six single-feature baselines re-run same-host.
  Decisive readings need load < 1.5 at start (D-02); single-gear only, no concurrent load
  (D-04); a row over `SPUR_BUILD_TIMEOUT=30s` halts for a human decision, first offer a
  lower `le` (D-03); the two must-debt files whose trigger is this sweep are resolved in
  its commit (D-05); SC3 is amended via edit-phase tooling, one human confirmation (D-06).
- **D-07…D-10 (the composition matrix):** two tiers — 96-row `calc.py`-only cross product
  (bore × cutout × recess × tip chamfer) plus ~18 kernel rows for untested pairs (D-07);
  every locked refusal × every other family switched on, `calc`-level (D-08); each tier-2
  row re-runs the feature's own built-solid proof helper (D-09); new tests add at most
  30 s to `make verify`, measured (D-10).
- **D-11…D-14 (interface parity):** one model-driven parity test walking
  `GearParams.model_fields` against `/api/schema`, the CLI parser, and one composed link's
  `spur info`/`/api/info` document + refusal-sentence parity; the shareable-URL round-trip
  is proven **statically** by reading `static/app.js`; the browser itself is checked by
  hand at `gsd-verify-work` (D-11). Form stays schema-driven, no conditional logic — the
  UI pass's verdict on both deferred UI ideas is "not taken" (D-12). `cli.md`'s exit-code
  must-debt is folded in and resolved (D-13). One composed README example, run by tests
  (D-14).
- **D-15…D-19 (SC4/SC5, close-out):** SC5 amended to the fixture's real contract — export
  bytes not compared (D-15). "Heaviest v0.2 face topology" = the composed-sweep row with
  the largest measured fine STL, decided by a number (D-16). Re-measurement is a committed
  `bench/` script behind a `make` target (D-17). L19's selection rule applied as written
  (D-18). One append-only L31 (D-19).
- **D-20…D-23 (process):** fixture replays byte-unchanged (D-20); branch
  `gsd/phase-12-composition-pass` cut from `origin/main` `c9a169d`, lands via
  `make pr.land PR=N`; plain `git commit` with explicitly staged files, never `git add -A`
  (D-21).

### Claude's Discretion

- Names: the composed sweep file, RESULTS.md section titles, parity/matrix test names,
  the export-cost script and its `make` target, tier-1 table construction
  (`itertools.product` vs written out).
- Sweep-row exactness (D-01): each row's exact bore computed from `bore_mouth_limit`
  against the cutout's hub datum; adjusted rows recorded beside the unchanged ones, never
  replacing them.
- Tier-2 row parameters (D-07): the 11-08 sets at 19-tooth defaults with `tip_chamfer` at
  the default gear's cap (1.75 mm); whether a keyed D-flat bore row is added; whether a
  composed tripwire is added beyond existing per-feature tripwires.
- Parity test strictness (D-11): whether it pins field declaration order = form order =
  CLI order and the eight group names literally. **Recommend yes** — the order is a
  published contract.
- The composed README link's values (D-14) and the manual UAT checklist's wording.
- The idea files' verdict paragraphs and trigger sentences (D-12).
- Peak-RSS reading and concurrency harness for D-17 (`resource.getrusage` in a subprocess;
  ten threads as the L19 measurement did).
- Whether `bench/build_time.py`'s new STL columns (D-16) also print triangle count for
  every earlier sweep file — recommended yes, since the runner is shared; earlier
  RESULTS.md sections are not rewritten.
- Plan order: SC3/SC5 amendment first (D-06, D-15); the sweep before the re-measurement
  (D-16 depends on the sweep's STL sizes); the matrix, parity and `cli.md` work
  independent of both; L31 and debt resolutions last, citing shas.

### Deferred Ideas (OUT OF SCOPE)

- A headless-browser test for the form/viewer — idea stands
  (`docs/ideas/2026-09-21-browser-test-for-the-viewer.md`); D-11 takes its "cheaper first
  step" only.
- Conditional form fields and a bore-shape selector — judged "not taken" at this phase's
  UI pass (D-12); their idea files get a verdict paragraph and a new trigger.
- The composed worst row under ten concurrent builds — not run (D-04); the question
  re-homes into `2026-09-23-concurrent-latency-bar-waived.md`'s triggers when the
  tip-chamfer debt file is resolved.
- L17's `mem_limit: 4g` re-swept on v0.2 topology — not this phase's (SC4 names L19/L24
  only).
- Adding STL triangle counts to earlier sweep RESULTS.md sections — the columns print for
  every sweep file going forward; history is not rewritten.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-measured-build-time | A recorded build time, plus fine-STL and STEP export time inside the admission slot, per feature at its heaviest allowed configuration — including a recess combined with each cutout pattern, and the honeycomb at its cap — in `bench/RESULTS.md`, inside `SPUR_BUILD_TIMEOUT`. | `bench/build_time.py` is unchanged and reused (verified this session, full text below); `bench/sweeps/*.json` schema confirmed from five existing sweep files; `tests/test_bench.py`'s per-sweep-file pinning-test pattern (63-269, verified) is the shape D-01's new sweep test copies; the six baseline numbers (D-01) and `SPUR_BUILD_TIMEOUT`'s "~4x the 7.39s worst build" rationale (`bench/RESULTS.md` line 271-278, verified) are the anchors D-03's checkpoint reasons against. |
| REQ-three-interfaces-extended | Every new parameter is on the web form (in its own group), the API query and the CLI flags from the one `GearParams` model, round-trips through the shareable URL, appears in `/api/schema`, and `spur info`/`spur export` print the same numbers and errors as the API. | `src/spur/params.py`'s eight `_f()`-declared groups confirmed by grep (Teeth/Body/Bore/Recess/Spokes/Holes/Honeycomb + `recess_sides`'s own group="Recess"); `cli.py`'s `_add_gear_args` (lines 41-53, verified) generates flags generically from `GearParams.model_fields` — no per-field code to audit; `static/app.js`'s `buildForm()` (line 45), `readHash()` (94), `gearQuery()` (101), `history.replaceState` (180) and the copy-link handler (348) all read `schema.properties`/`fields` generically — verified this session, and these line numbers **differ from CONTEXT.md's canonical_refs (49-89)**, a drift the planner must use the live numbers for; `tests/test_cli.py::test_cli_and_api_print_the_same_document` (47) and `tests/test_api.py::test_schema_drives_the_form` (58) are the parity-test precedents D-11 generalises. |

</phase_requirements>

## Summary

Phase 12 adds no field, no cut, no dependency — its job is to point the plan at exactly
what exists today so the composed sweep, the composition matrix, and the parity test are
written against real line numbers and real committed scripts, not against Phase 8-11's
CONTEXT.md descriptions of themselves (which have already drifted in at least one place:
`app.js`'s function line numbers). Every piece of tooling the phase needs is already
built and unchanged: `bench/build_time.py` times build + fine-STL + STEP export against
`SPUR_BUILD_TIMEOUT` from a JSON sweep file and is explicitly designed to be reused by
Phases 9-12 without modification (its own docstring says so, verified this session); the
sweep-file schema is a flat JSON list of `GearParams`-shaped dicts; `tests/test_bench.py`
pins each sweep file's exact row set with one test per file, a pattern that scales
directly to a sixth (composed) sweep file. Nothing about the build-time harness needs
inventing — only a new sweep JSON, D-16's two new STL-size columns in `Timing`/`report`,
and one new `bench/RESULTS.md` section in the existing house style (host-state header,
table, named heaviest row).

The composition matrix (D-07/D-08) has direct precedent to reuse rather than invent: the
existing selector-matrix test (`tests/test_model.py:314`,
`test_every_selector_takes_only_its_own_edges_with_a_body_cutout`, 19 rows) and the
recess-survival matrix (`tests/test_model.py:1352`, 13 rows) already cover most of the
pairs a naive Tier 2 would re-test — the phase's own discretion note says these rows are
**not** repeated. The three built-solid proof helpers D-09 names —
`_assert_only_the_tip_arcs_were_chamfered` (705), `_assert_the_cutout_is_what_derive_
prints` (1142), `_assert_the_recess_fillet_survives` (1302) — are all present, unchanged,
and callable on any composed solid without modification; their signatures were read this
session and are quoted below (Code Examples).

Interface parity (D-11) is materially easier than a from-scratch design would suggest:
both `cli.py`'s flag generation and `app.js`'s form renderer are already fully generic
over `GearParams.model_fields`/`schema.properties` — no per-field code exists anywhere to
audit for a missed v0.2 parameter. The one genuine gap the research surfaces is `cli.md`'s
"Errors" paragraph (lines 33-36, read this session, quoted verbatim below), which
currently states a contract the code does not implement: it claims exit 2 for "an unknown
output extension," but `cmd_export` raises `SystemExit("error: ...")` — a *string*
`SystemExit`, which Python exits at status **1**, not 2 — for both the unknown-extension
case and every `BuildError`. Only argparse's own parameter-validation path
(`raise SystemExit(2)`, an *integer* `SystemExit`) exits 2. This is exactly the "must"
tech debt D-13 already schedules to fold in and resolve.

L19 (gzip level) and L24 (mesh-copy cost) are both re-measurable with the exact same
method already on record — L19's table lives in a code comment above `_GZIP_LEVEL` in
`app.py` (read this session, quoted below) and its selection rule is one arithmetic
check; L24's number was a **one-off planning-session probe** using
`resource.getrusage(...).ru_maxrss`, never turned into a committed script — this is the
gap D-17 exists to close, and there is no existing `bench/` script to reuse for it
(`bench/memory.py` reads Docker's own `docker stats`, a different mechanism for a
different measurement target; grepping the whole repo for `ru_maxrss`/`getrusage` found
exactly one hit, in the decision log's prose, confirmed this session). The nearest
reusable shape is `bench/honeycomb_spike.py`/`bench/tip_chamfer_spike.py`'s own pattern:
a `bench/<name>.py` module run as `.venv/bin/python -m bench.<name>`, printing Markdown,
exiting 1 on a failed verdict, not part of `make verify`.

**Primary recommendation:** treat this phase as a grounding-and-wiring exercise, not a
design exercise — every task should cite a file and line range read this session (not a
CONTEXT.md description of one), reuse `bench/build_time.py` unchanged, extend
`tests/test_bench.py` in its existing per-sweep-file pattern, and write the export-cost
script (D-17) in `bench/honeycomb_spike.py`'s committed-module shape since no prior
committed harness measures gzip/copy cost at all.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Composed sweep timing (build, fine STL, STEP, per parameter set) | Database/Storage (`bench/` artefacts) | API/Backend (`spur.model` called in-process) | `bench/build_time.py` runs `spur.model.build`/`export` directly, no HTTP layer; results land in `bench/RESULTS.md`, never a live assertion (D-16 of Phase 8, unchanged) |
| Composition matrix — calc-only cross product (Tier 1) | API/Backend (`calc.py`) | — | Pure math, no kernel; `calc.py` never imports `cadquery` (import-linter enforced); this is why Tier 1 is "free" at 96 rows |
| Composition matrix — built-solid proofs (Tier 2) | CAD Kernel (`model.py`, exercised through `tests/test_model.py`) | — | Only the kernel can prove a feature "still holds" on a shared solid; reuses each feature's own proof helper, no new proof shape (D-09) |
| Interface parity — schema/CLI/form field walk | API/Backend (`GearParams.model_fields` is the one source) | Frontend Server (`/api/schema` endpoint), Browser (`app.js`'s generic renderer) | One model drives all three; the parity test walks the model, not any one consumer |
| Shareable-URL round-trip | Browser (`app.js`: `readHash`/`gearQuery`/`history.replaceState`) | — | Client-side hash ↔ query-string mapping; proven statically by reading the JS source, not by driving a browser (D-11) |
| Build-time re-measurement (L19 gzip, L24 mesh copy) | Database/Storage (`bench/` artefacts) | API/Backend (`app.py`'s `_GZIP_LEVEL`, `model.py`'s export-copy call, both possibly changed by the result) | A number measured on the pinned kernel/host, landing in a committed script + `bench/RESULTS.md`, only feeding back into `app.py`/`model.py` if the measured rule (L19) or invariant (L24) says so |
| Regression fixture replay | API/Backend (`calc.derive`, `model.build` — read-only for this phase) | — | `tests/regression/test_pre_v0_2.py` runs unmodified; a red result here is this phase's bug per the fixture's own docstring, never the fixture's |

## Standard Stack

No new dependency, library or tool is introduced by this phase — it is a pure
integration/measurement pass over an already-complete v0.2 feature set. Every tool used
is already pinned and present.

### Core (reused, unchanged)

| Library | Version | Purpose | Verified |
|---------|---------|---------|----------|
| `cadquery` | 2.8.0 | CAD kernel the composed-sweep and matrix rows build through | `[VERIFIED: .venv/bin/python -c "importlib.metadata.version('cadquery')"` run this session — printed `2.8.0`] |
| `cadquery-ocp` | 7.9.3.1.1 | OCCT bindings under `cadquery` | `[VERIFIED: same command, printed 7.9.3.1.1]` |
| `pytest` | pinned via `pyproject.toml` dev extras | `tests/test_bench.py`, `tests/test_calc.py`, `tests/test_model.py`, `tests/test_api.py`, `tests/test_cli.py`, `tests/regression/` — every test surface this phase extends | `[VERIFIED: pytest already invoked project-wide via make test, confirmed present in .venv]` |
| Python | 3.12.13 | The only supported runtime (L23) | `[VERIFIED: .venv/bin/python --version, run this session]` |
| stdlib `gzip` | stdlib | L19's re-measurement subject (`gzip.compress`) | already imported in `app.py`, no new dependency |
| stdlib `resource` | stdlib | L24's `ru_maxrss` peak-RSS reading, precedent in the decision log prose only — **no existing bench script uses it** | `[VERIFIED: grep -rn "ru_maxrss\|getrusage" across src/tests/bench/docs found exactly one hit, in docs/architecture/decision_log.md's prose (line 646), not in any committed script]` |
| stdlib `itertools` | stdlib | Tier-1 96-row cross product construction (Claude's Discretion: `itertools.product` vs written out) | already used this way in `tests/test_bench.py`'s sweep-pinning tests (e.g. line 143, `itertools.product`) |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `httpx` | already a dev/prod dependency | Used by `bench/latency.py` and `bench/memory.py`; not needed by this phase's new scripts unless D-17's concurrency harness drives HTTP rather than in-process calls | Only if the export-cost script's ten-concurrent gzip measurement is implemented as HTTP calls against a running `make serve` rather than in-process `gzip.compress` calls — the L19 table itself was measured in-process (quick task 260923-qwr), so in-process is the precedented approach |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing `bench/build_time.py` unchanged for the composed sweep | Writing a new composed-sweep script | Rejected by the phase framing itself and by 08-CONTEXT.md D-12: "Phases 9-12 add their own sweep file and run this script unchanged" — `Timing`/`report`/`load_sweep`/`main` need only D-16's two new columns, not a rewrite |
| A committed `bench/export_cost.py` script for L19/L24 (D-17) | A one-off measurement script, discarded after use | Rejected explicitly by D-17: "the v0.1 numbers came from one-offs nobody can re-run" — this phase's whole point for SC4 is making the number re-derivable |

**Installation:** none — no new package this phase.

## Package Legitimacy Audit

Not applicable. This phase installs no new package in any ecosystem; every library used
(`cadquery`, `cadquery-ocp`, `pytest`, `httpx`, stdlib `gzip`/`resource`/`itertools`) is
already pinned in `pyproject.toml` and present in `.venv`, verified this session.

## Architecture Patterns

### System Architecture Diagram

```
                         ┌─────────────────────────────┐
                         │   bench/sweeps/<composed>    │
                         │   .json  (D-01, new file)    │
                         └───────────────┬─────────────┘
                                         │ load_sweep()
                                         ▼
┌──────────────┐      ┌─────────────────────────────────┐      ┌─────────────────┐
│ GearParams   │─────▶│  bench/build_time.py (unchanged) │─────▶│ bench/RESULTS.md │
│ (validated)  │      │  time_set(): build → fine STL →  │      │  new section    │
└──────────────┘      │  STEP, wraps SPUR_BUILD_TIMEOUT  │      │  (D-16 columns) │
                       └─────────────────┬─────────────────┘      └─────────────────┘
                                         │
                    ┌────────────────────┼──────────────────────┐
                    ▼                    ▼                      ▼
          ┌──────────────────┐ ┌──────────────────┐  ┌─────────────────────┐
          │ tests/test_bench │ │ tests/test_calc   │  │ tests/test_model.py  │
          │ .py: pins the    │ │ .py: Tier 1, 96   │  │ Tier 2, ~18 built-   │
          │ sweep row set    │ │ calc-only rows +  │  │ solid rows reusing   │
          │ (D-01)           │ │ refusal composit- │  │ each feature's own   │
          │                  │ │ ion (D-07/D-08)   │  │ proof helper (D-09)  │
          └──────────────────┘ └──────────────────┘  └─────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ Interface parity (D-11) — one test walks GearParams.model_fields       │
│                                                                          │
│  GearParams.model_fields ──┬──▶ /api/schema (group/title/unit/step)    │
│                             ├──▶ cli.py's argparse flags (generic loop) │
│                             ├──▶ spur info == /api/info (byte-for-byte) │
│                             └──▶ static/app.js read statically for the │
│                                  hash→form→query generic path           │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ L19/L24 re-measurement (D-16/D-17)                                     │
│                                                                          │
│  Composed sweep's largest fine STL row (found via D-16's new columns)  │
│         │                                                               │
│         ▼                                                               │
│  bench/<export_cost>.py (new, committed) ──▶ bench/RESULTS.md section  │
│    - gzip.compress at levels 1/6/9, single + 10-concurrent (L19 shape) │
│    - shape.copy() vs in-place STL export, wall time + peak RSS (L24)   │
└────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

No new directories. New files land in existing locations:

```
bench/
├── sweeps/
│   └── <composed>.json          # D-01, new — Claude's Discretion for the name
├── build_time.py                # D-16 — extend Timing/report with STL byte/triangle cols
├── <export_cost>.py             # D-17, new — L19/L24 re-measurement, planner names it
└── RESULTS.md                   # D-01/D-16/D-17/D-19/D-20 — new sections appended

tests/
├── test_bench.py                # D-01 — one new test pinning the composed sweep's rows
├── test_calc.py                 # D-07/D-08 — Tier 1 96-row matrix + refusal composition
├── test_model.py                # D-07/D-09 — Tier 2 ~18 built-solid rows
├── test_api.py                  # D-11 — parity test rows, routing tests
├── test_cli.py                  # D-11/D-13 — parity test, cli.md exit-code asserts
└── regression/test_pre_v0_2.py  # D-20 — runs unmodified, replay only

docs/
├── architecture/
│   ├── decision_log.md          # D-19 — append-only L31
│   └── cli.md                   # D-13 — "Errors" paragraph rewritten
├── tech_debt/
│   ├── active/  → resolved/     # D-05, D-13 — three files git mv'd
│   └── INDEX.md                 # rows moved to Resolved table
└── ideas/
    ├── 2026-09-29-conditional-form-fields.md          # D-12 verdict paragraph
    └── 2026-09-27-bore-shape-selector-in-the-web-form.md  # D-12 verdict paragraph

README.md                        # D-14 — one composed example link
```

### Pattern 1: A sweep file is a flat JSON list of `GearParams`-shaped dicts

**What:** `bench/sweeps/*.json` — a top-level JSON array; each element is a dict of field
name → value, validated through `GearParams.model_validate()` on load.
**When to use:** the composed sweep (D-01) and every future `bench.build` sweep.
**Verified this session** (`bench/sweeps/hex_bore.json`, first two rows):
```json
[
  {"teeth": 200, "module": 1.75, "bore_hex": 200, "recess_sides": "both", "bore_chamfer": 0.4},
  {"teeth": 200, "module": 1.75, "bore_hex": 200, "recess_sides": "both", "bore_chamfer": 3}
]
```
`load_sweep()` (`bench/build_time.py:56-71`, quoted verbatim) raises `ValueError` naming
the set and file index if any row fails validation — nothing is silently skipped.

### Pattern 2: `bench/build_time.py`'s `time_set` — the exact code the composed sweep runs unchanged

```python
# Source: bench/build_time.py, read in full this session (lines 76-86)
def time_set(p: GearParams) -> tuple[float, float, float]:
    """Build wall time (cold solid cache), fine-STL export time, STEP export time."""
    model._build_cached.cache_clear()
    t0 = time.perf_counter()
    model.build(p)
    build_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model.export(p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model.export(p, "step")
    step_s = time.perf_counter() - t0
    return build_s, stl_s, step_s
```
D-16's two new columns (fine-STL byte count, triangle count) are a small addition
alongside this function or in `Timing`/`report` — not a rewrite. Binary STL's triangle
count is available directly from the header (`int.from_bytes(data[80:84], "little")`,
the same read `tests/test_model.py:_stl_triangles` at line 1403 already does) — no need
to iterate every facet just to count them.

### Pattern 3: `tests/test_bench.py`'s one-test-per-sweep-file pinning shape

**What:** each committed sweep file gets exactly one test asserting `len(sets)` and the
full row set as a `set` of tuples, built from `itertools.product` over the sweep's own
axes, plus targeted `pytest.raises(ValidationError)` assertions pinning any row that
sits exactly one step from a refusal.
**Verified this session** — the Phase 8 hex-bore sweep's test
(`tests/test_bench.py:141-152`, quoted):
```python
def test_the_hex_bore_sweep_is_every_combination_d_11_names() -> None:
    sets = load_sweep(DEFAULT_SWEEP)
    assert len(sets) == 16
    got = {(p.teeth, p.module, p.bore_hex, p.recess_sides, p.bore_chamfer)
           for _, p in sets}
    want = set(itertools.product((200,), (1.75, 10.0), (200.0, 12.7),
                                  ("both", "none"), (0.4, 3.0)))
    assert got == want
```
D-01's new composed sweep test follows this exact shape.

### Pattern 4: The three built-solid proof helpers Tier 2 must reuse (D-09)

All three read and confirmed present in `tests/test_model.py` this session:
```python
# Source: tests/test_model.py:705 (signature; body omitted — reused unmodified)
def _assert_only_the_tip_arcs_were_chamfered(cut: cq.Solid, plain: cq.Solid,
                                             p: GearParams, p0: GearParams) -> None: ...

# Source: tests/test_model.py:1142
def _assert_the_cutout_is_what_derive_prints(...): ...

# Source: tests/test_model.py:1302
def _assert_the_recess_fillet_survives(cut: cq.Solid, p: GearParams, torus: int) -> None: ...
```
Each Tier-2 row builds one composed solid and calls the relevant helper(s) — "composes
correctly" means every single-feature proof still holds on the shared solid, not a new
proof shape (D-09, explicit).

### Pattern 5: A committed `bench/<name>.py` measurement module, run standalone

**What:** `bench/honeycomb_spike.py` and `bench/tip_chamfer_spike.py` are both
`.venv/bin/python -m bench.<name>`-runnable modules that print a Markdown report and
`sys.exit(1)` on a failed verdict — not part of `make verify` (confirmed: neither
appears in the `verify` target's dependency chain in the Makefile).
**When to use:** D-17's export-cost script (L19/L24 re-measurement) should follow this
exact shape — a new `Makefile` target (`make bench.export SET=…`, name the planner's)
invoking `.venv/bin/python -m bench.<name>`, results appended to `bench/RESULTS.md`.
**Verified this session** (`bench/honeycomb_spike.py`'s own docstring, quoted):
```
Run it as `.venv/bin/python -m bench.honeycomb_spike` from the repo root. It prints
Markdown and exits 1 when the verdict fails.
```

### Pattern 6: `cli.py` and `app.js` are already fully generic over `GearParams`

**What:** neither file has any per-field code — a new v0.2 parameter needs zero CLI or
form changes to appear correctly. `cli.py`'s `_add_gear_args` (lines 41-53, verified,
quoted):
```python
# Source: src/spur/cli.py:41-53
def _add_gear_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("gear parameters (defaults in brackets)")
    for name, field in GearParams.model_fields.items():
        flag = "--" + name.replace("_", "-")
        help_text = f"{field.description} [{field.default}]".replace("%", "%%")
        if get_origin(field.annotation) is Literal:
            g.add_argument(flag, dest=name, default=None, help=help_text,
                            choices=list(get_args(field.annotation)))
        else:
            assert field.annotation is not None
            g.add_argument(flag, dest=name, default=None, help=help_text,
                            metavar="V", type=field.annotation)
```
`app.js`'s `buildForm()` (line 45) loops `schema.properties` the same way, generic over
`group`/`title`/`unit`/`step`/`enum` — verified this session. This is why D-11's parity
test can be one generic walk instead of 30 per-field tests: the risk is not "a field was
coded wrong," it is "a field is missing a `group`/`title`/`unit`/`step` key," which only
a generic walk over every field catches.

### Anti-Patterns to Avoid

- **Trusting CONTEXT.md's cited line numbers as current:** `app.js`'s function line
  numbers have already drifted from CONTEXT.md's `<canonical_refs>` (which cites 49-89;
  the real numbers, read this session, are 45/94/101/180/348). Every file citation in
  the plan should be re-verified at plan time or execute time, not copied from
  CONTEXT.md unchecked.
- **Re-deriving the sweep runner:** `bench/build_time.py` is explicitly designed to be
  reused unchanged across Phases 9-12 (its own docstring says so); writing a new runner
  for the composed sweep would duplicate `Timing`/`report`/`load_sweep`/`main` for no
  reason.
- **A new proof shape for Tier 2:** D-09 is explicit that "composes correctly" means the
  existing single-feature proofs still hold — inventing a new composed-solid assertion
  shape (e.g. a fresh face/edge Counter contract) contradicts the locked decision.
- **Assuming `bench/memory.py`'s pattern applies to D-17's peak-RSS reading:** it reads
  `docker stats`' MEM USAGE column via polling a running container — a different
  mechanism for a different measurement target (container ceiling vs. one process's
  peak). L24's number came from `resource.getrusage(...).ru_maxrss` in a bare planning
  probe, never committed. D-17's script needs its own `resource.getrusage` call, not a
  `bench/memory.py` import.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Timing a build + export against `SPUR_BUILD_TIMEOUT` | A new sweep-timing loop | `bench/build_time.py`'s `time_set`/`Timing`/`report`/`main`, unchanged | Explicitly designed for this reuse (08-CONTEXT.md D-12); rewriting it duplicates a working, already-tested harness |
| Pinning a sweep file's exact row set | Manual row-by-row assertions | `itertools.product` over the sweep's own axes, compared as a `set` of tuples (Pattern 3) | Every existing sweep test in `tests/test_bench.py` uses this shape; it is shorter and catches an accidentally-dropped or duplicated row automatically |
| A percentile calculation for any latency-shaped measurement this phase might touch | A hand-rolled percentile | `statistics.quantiles(samples, n=20)[-1]`, `bench/latency.py`'s own `_p95` (line 47-54) | `bench/latency.py`'s own docstring explicitly names hand-rolled percentiles as the L08-forbidden "plausible but off-by-one" number this project refuses to ship |
| Counting STL triangles for D-16's new column | Iterating every facet with `_stl_triangles` and `len()` | Reading the 4-byte triangle-count header directly (`int.from_bytes(data[80:84], "little")`) | The count is already in the binary STL header — `_stl_triangles` (test_model.py:1403) exists for content proofs (per-facet vertex data), not counting; reading the header is O(1) instead of O(n) |

**Key insight:** almost nothing in this phase needs new code beyond the plumbing that
wires existing, already-proven mechanisms together — the risk profile is entirely in
citing stale line numbers or duplicating a harness that already exists, not in inventing
new measurement logic.

## Common Pitfalls

### Pitfall 1: `cli.md`'s documented exit-code contract does not match the code

**What goes wrong:** a plan or a test written against `docs/architecture/cli.md`'s
current "Errors" paragraph will assert exit 2 for an unknown output extension and expect
the same for `BuildError` — both wrong.
**Why it happens:** `raise SystemExit("error: ...")` (a string argument) exits status
**1**, not 2 — this is a Python stdlib behaviour, not a bug, but it reads as "should be
2" if you only read the doc.
**How to avoid:** the real contract, verified this session directly in `cli.py`:
argparse's own `_params()` catch does `raise SystemExit(2)` (integer — parameter errors
only, cli.py lines ~89); `cmd_export`'s unknown-extension check and its `BuildError`
catch both do `raise SystemExit(f"error: ...")` (string — exits 1). D-13 already
schedules the doc fix; the plan should cite the code, not the doc, as ground truth.
**Warning signs:** a test asserting `exc.value.code == 2` for anything other than an
argparse-caught `ValidationError` path.

### Pitfall 2: The current host is not quiet — D-02's decisive-reading bar needs a wait

**What goes wrong:** running the composed sweep immediately, without checking
`uptime`, risks a non-decisive reading exactly like the spoke-sweep debt file's 32.17
load average.
**Why it happens:** this session's own `uptime` read **load averages 3.20/2.94/3.15** —
above D-02's <1.5 bar for a decisive run.
**How to avoid:** the plan's sweep-execution task should check `uptime` immediately
before running and either wait for a quiet window or record the load explicitly and
treat the reading as non-decisive per D-02 (never dropped or silently re-run to green).
**Warning signs:** a sweep row reading close to `SPUR_BUILD_TIMEOUT` with no load figure
recorded beside it.

### Pitfall 3: `docs/tech_debt/INDEX.md`'s row-number references in CONTEXT.md are not literal line numbers

**What goes wrong:** CONTEXT.md's canonical_refs says "rows 27, 28, 30 move to the
resolved table" — this reads like it names literal table rows, but the Active table's
current row order (verified this session) does not put the three D-05/D-13 target files
at positions 27/28/30 in any obvious numbering; the identification must be by filename,
not by a numeric row index.
**Why it happens:** the debt file's own filename is the only stable identifier;
`INDEX.md`'s Active table has no explicit row-number column.
**How to avoid:** match by filename when editing `INDEX.md` for D-05/D-13's `git mv`
step: `2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`,
`2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`,
`2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md` — all three confirmed
present in the Active table this session.
**Warning signs:** an edit that moves the wrong row, or leaves a stale row referencing a
file that has already been `git mv`'d to `resolved/`.

### Pitfall 4: `bench/memory.py` is not a template for D-17's peak-RSS reading

**What goes wrong:** assuming `bench/memory.py`'s peak-reading code can be imported or
copied for D-17's per-export peak-RSS measurement.
**Why it happens:** CONTEXT.md's Claude's Discretion note phrases this as "as
`bench/memory.py` reads containers," which is easy to misread as "reuse
`bench/memory.py`'s reading mechanism."
**How to avoid:** `bench/memory.py` polls `docker stats`' MEM USAGE column
(`_MEM_UNITS` table, `POLL_INTERVAL = 0.5`, verified this session) — a container-level
measurement via Docker's own accounting. L24's number instead came from
`resource.getrusage(...).ru_maxrss` read directly in a bare Python probe (the *only*
occurrence of `getrusage`/`ru_maxrss` anywhere in the repo, confirmed by a full-repo
grep this session, and it is prose in the decision log, not code). D-17's script needs
its own `resource.getrusage` call — most simply, run the export in a subprocess and read
`resource.getrusage(resource.RUSAGE_CHILDREN)` in the parent, since `ru_maxrss` measures
the calling process (or its children) directly, not a container.
**Warning signs:** an import of `bench.memory` in the new export-cost script, or a
`docker` dependency where none is needed (L24's measurement is host-level, matching how
the original number was taken).

### Pitfall 5: The honeycomb's lever for D-03's over-budget checkpoint is `HEX_CELL_CAP`, not `hex_cell`'s field bound

**What goes wrong:** if a composed row with `hex_cell` at its expected cap crosses
`SPUR_BUILD_TIMEOUT`, reaching for a schema-level `hex_cell` bound change (the way
`spoke_count`/`hole_count`'s `le` was lowered in Phase 11) is the wrong lever.
**Why it happens:** the honeycomb's cell count is derived from `hex_cell` and capped by
the module-level constant `HEX_CELL_CAP = 120` (`src/spur/calc.py:51`, confirmed this
session), not directly by a field bound — `hex_cell` itself has `ge=0, le=100` as a raw
cell-size field, unrelated to the count cap.
**How to avoid:** D-03 already states this explicitly: "The honeycomb's lever stays
`HEX_CELL_CAP` (11 D-11: 'lowered before any honeycomb link exists in the wild')." A
composed honeycomb row over budget is addressed by lowering `HEX_CELL_CAP` in
`calc.py`, not by touching `hex_cell`'s `Field(le=...)`.
**Warning signs:** a plan step that edits `hex_cell`'s bound in `params.py` in response
to a build-time overage.

### Pitfall 6: `bore_hex=200` does not compose with the recorded spoke/hole heaviest rows without adjustment

**What goes wrong:** naively pairing the recorded heaviest spoke row (`hub_d=52`) or
hole row (`hole_circle_d=183.4`) with a 200mm hex bore produces a 422, not a composed
build.
**Why it happens:** a 200mm across-flats hex bore's corner sits at ~115.47mm radius
(`bore_mouth_limit` ≈115.9mm with the default 0.4mm chamfer) — this is well outside both
the spoke row's 26mm hub ring and the module-1.75 hole row's 91.2mm inner hole edge, so
either composition is refused naming the hub field.
**How to avoid:** this is already flagged in CONTEXT.md's `<specifics>` section and
assigned to Claude's Discretion for the planner: compute each row's largest `bore_hex`
that clears `bore_mouth_limit(p) + MIN_WALL` against the cutout's own hub datum,
recording the adjusted row beside the unchanged one, never replacing it.
**Warning signs:** a composed sweep row that fails `GearParams.model_validate` at
`load_sweep` time — the failure is immediate and names the fields, per
`load_sweep`'s own contract (raises before any build, `bench/build_time.py:56-71`).

## Runtime State Inventory

Not applicable — this phase renames nothing and migrates no stored state. It adds a
sweep file, a bench script, test rows, and doc edits; nothing here has a rename/refactor
shape.

## Code Examples

### The `_gzip` function and `_GZIP_LEVEL` L19 targets (re-measurement subject)

```python
# Source: src/spur/app.py, read in full this session
_GZIP_LEVEL = 1

def _gzip(data: bytes) -> bytes:
    """gzip-encode at the level Task 1 measured (`_GZIP_LEVEL`, set from a real 9 MB STL,
    above)."""
    return gzip.compress(data, compresslevel=_GZIP_LEVEL)
```
The comment block directly above `_GZIP_LEVEL` (`app.py`, verified this session) carries
L19's exact 1/6/9 measurement table and the selection rule D-18 applies as written:
"adopt a higher level only if it shrinks output by ≥10% **and** costs ≤1.5× the
10-concurrent wall of the level below."

### The exact `SPUR_BUILD_TIMEOUT` rationale D-03's checkpoint reasons against

```
# Source: src/spur/app.py, comment above int_env("SPUR_BUILD_TIMEOUT", 30), read this session
# 200-tooth fine gear, ten concurrent requests, this machine under host
# contention -- see bench/RESULTS.md's Machine caveat). 30s is ~4x that
# observation, chosen as margin for hardware slower than the measurement
# machine (the debt file's own concern: the stall is proportionally worse on
# slower hardware). Re-measure and adjust if bench/RESULTS.md's worst observed
# build ever approaches this value.
```

### The L24 mesh-copy comment in `model.py` (D-17's other re-measurement target)

```python
# Source: src/spur/model.py, near line 549-559, read this session
# and build() returns it after releasing _LOCK -- meshing it in place left
# .BoundingBox() reading the mesh (zlen 7.5000 -> 7.5877 mm after a preview
# ...reuse the fine mesh (46,278 triangles instead of 9,066). A copy keeps the
# cached solid mesh-free for its whole life, at 1.4-17.6 ms per export
# (L24) -- no positional argument to copy(): its one parameter is mesh,
# default False, and copy(mesh=True) would carry a mesh across.
shape.copy().exportStl(str(path), tolerance=tol, angularTolerance=ang, ...)
```

### `cli.md`'s current (wrong) "Errors" paragraph — D-13's rewrite target

```
# Source: docs/architecture/cli.md, lines 33-36, read verbatim this session
## Errors

Exit 2 with `error: …` on stderr for bad parameters and for an unknown output extension;
`BuildError` becomes `error: <kernel message>`. Nothing is written when the build fails.
```
The real contract (verified against `cli.py` this session): parameter errors (argparse,
`_params()`) exit **2**; an unknown output extension and every `BuildError` both exit
**1** (both raised as string `SystemExit`s in `cmd_export`).

## State of the Art

Not applicable in the usual "old library vs new library" sense — this phase touches no
external dependency version. The one process-level "old approach vs new approach" is
D-17 itself: L19 and L24's original numbers were one-off planning-session probes
(`gzip_bench.py` for L19 per the decision log's own citation; a bare
`resource.getrusage` probe for L24), superseded by this phase's committed,
`make`-target-driven re-measurement script — the same "measured once, re-measurable
forever" shift every prior phase's sweep already made for build time (08 D-12).

**Deprecated/outdated:**
- L19/L24's own numbers stay on record in `docs/architecture/decision_log.md` (append-
  only) but are explicitly flagged by this phase's own CONTEXT.md as measured on
  v0.1-era topology (L19: a 9,062,784-byte fine STL with no v0.2 feature; L24: a plain
  200-tooth fine export) — not assumed to still hold on v0.2's composed topology.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Nothing else in the repo reads `_GZIP_LEVEL` or the L24 copy-cost comment besides the two sites quoted above (no other code path would need updating if D-18 flips `_GZIP_LEVEL`) | Code Examples, Pitfall 4 | If a second call site exists, D-18's level change would be incomplete; low risk — a grep for `_GZIP_LEVEL` at plan/execute time closes this cheaply |
| A2 | `bore_hex=200`'s hub-clearance conflict with the recorded spoke/hole heaviest rows (Pitfall 6) is correctly derived from `bore_mouth_limit`'s documented formula, without having re-run the kernel this session to confirm the 422 actually fires | Pitfall 6 | This is explicitly flagged in CONTEXT.md's own `<specifics>` as "no kernel probe was run this session" — the arithmetic is training-adjacent, not tool-verified; the planner's first sweep-row task should treat this as a hypothesis to confirm via `load_sweep`'s own validation, not a settled fact |

**If this table is empty:** N/A — two low-risk items above, both self-resolving at plan
or execute time via a grep or a `load_sweep` call.

## Open Questions

None that block planning. CONTEXT.md's own framing states this phase measures and
integrates against decisions already locked in Phases 7-11 — this research found no
technical unknown requiring a checkpoint before planning starts. The two items in the
Assumptions Log above are self-resolving cheaply and do not need a pre-plan decision.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | The only supported runtime (L23) | ✓ | 3.12.13 | — |
| `cadquery` | Every build/export in the sweep and matrix | ✓ | 2.8.0 | — |
| `cadquery-ocp` | OCCT bindings under `cadquery` | ✓ | 7.9.3.1.1 | — |
| `.venv/bin/spur` (CLI) | D-11's parity test, D-14's README example | ✓ | present, confirmed this session | — |
| `make` targets (`verify`, `test`, `bench.build`, `bench.latency`, `bench.memory`) | The gate and every bench script | ✓ | confirmed via `make help`, `bench.build`/`bench.latency`/`bench.memory` all present | — |
| Docker | `make check`, `bench.memory` | not probed this session (D-04 excludes concurrent/memory re-sweeps from this phase's scope) | — | not needed — this phase's scope (D-04, deferred items) explicitly excludes the container-memory and concurrent-build measurements |
| Quiet host (load < 1.5) | D-02's decisive-reading bar for the composed sweep | ✗ at research time | load averages 3.20/2.94/3.15, read this session via `uptime` | wait for a quiet window before the decisive sweep run; a non-quiet reading is recorded with its load figure per D-02, never dropped |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** a quiet host for the decisive sweep reading — the
fallback (wait, or record-with-caveat) is D-02's own contract, not invented here.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest, pinned via `pyproject.toml` dev extras `[VERIFIED: already invoked project-wide, confirmed present in .venv this session]` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_calc.py -x` (Tier 1, pure-math, no kernel — seconds) |
| Full suite command | `make verify` (ruff + mypy --strict + import-linter + no-fake-done + full pytest; baseline this session: 621 passed, 177.62s pytest / 178.55s wall at Phase 11's end, host load 3.07-4.65 — `bench/RESULTS.md` "make verify wall time", verified) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-measured-build-time | Composed sweep: recess + each cutout + tip chamfer + heaviest bore, both modules, inside `SPUR_BUILD_TIMEOUT` | bench (not `make verify`) | `make bench.build SWEEP=bench/sweeps/<composed>.json` | ❌ Wave 0 (new sweep JSON + `test_bench.py` row) |
| REQ-measured-build-time (SC4, L19/L24 re-measurement) | gzip level table + mesh-copy cost re-measured on the composed sweep's largest fine STL | bench (not `make verify`) | `make bench.export SET=<name>` (name the planner's, D-17) | ❌ Wave 0 (new script + Makefile target) |
| REQ-three-interfaces-extended (SC1, matrix Tier 1) | 96-row bore×cutout×recess×chamfer cross product: derives or refuses correctly, calc-only | unit (`calc.py`, no kernel) | `.venv/bin/python -m pytest tests/test_calc.py -x` | ❌ Wave 0 |
| REQ-three-interfaces-extended (SC1, matrix Tier 2) | ~18 built-solid rows re-running each feature's own proof helper on the composed solid | built-solid | `.venv/bin/python -m pytest tests/test_model.py -x` | ❌ Wave 0 |
| REQ-three-interfaces-extended (SC1, refusal composition) | Every locked refusal × every other family switched on, same sentence/fields | unit (`calc.py`) + one API row + one CLI row per refusal | `.venv/bin/python -m pytest tests/test_calc.py tests/test_api.py tests/test_cli.py -x` | ❌ Wave 0 |
| REQ-three-interfaces-extended (SC2, parity) | `GearParams.model_fields` walk: schema group/title/unit/step, CLI flags, composed-link `spur info`==`/api/info`, refusal sentence parity | unit (`test_api.py`/`test_cli.py`) + static `app.js` read | `.venv/bin/python -m pytest tests/test_api.py tests/test_cli.py -x` | ❌ Wave 0 |
| REQ-three-interfaces-extended (SC2, cli.md fix) | `cli.md` "Errors" matches real exit-code contract; `exc.value.code` pinned | doc + unit | `.venv/bin/python -m pytest tests/test_cli.py -k exit -x` | ❌ Wave 0 (new asserts on existing tests) |
| REQ-three-interfaces-extended (SC2, README example) | One composed link builds, is the parity test's input | unit (`test_cli.py::test_readme_export_examples_run`-shaped) | `.venv/bin/python -m pytest tests/test_cli.py -k readme -x` | ✅ (existing test extended, not new file) |
| REQ-defaults-off-regression (SC5, final fixture pass) | Pre-v0.2 fixture byte-unchanged, replay unmodified | regression | `.venv/bin/python -m pytest tests/regression/test_pre_v0_2.py -x` | ✅ (existing, unmodified) |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -x` (Tier 1 fast, Tier 2 kernel-touching but scoped)
- **Per wave merge:** `make verify` (full gate; D-10 caps this phase's added wall time at 30s over the phase-start reading, measured)
- **Phase gate:** Full suite green before `/gsd-verify-work`; `make bench.build`/`make bench.export` sweeps run separately (never part of `make verify`, per `bench/build_time.py`'s own docstring and the Makefile's `verify` target dependency list, confirmed this session to exclude every `bench.*` target)

### Wave 0 Gaps

- [ ] `bench/sweeps/<composed>.json` — the new composed sweep file (D-01)
- [ ] A new row in `tests/test_bench.py` pinning the composed sweep's exact row set, in
      the existing per-sweep-file shape (Pattern 3)
- [ ] `bench/build_time.py`'s `Timing`/`report` extended with fine-STL byte count and
      triangle count columns (D-16) — small addition, not a rewrite
- [ ] `bench/<export_cost>.py`, new, committed (D-17) — L19's gzip table + L24's copy
      cost, in `bench/honeycomb_spike.py`'s standalone-module shape (Pattern 5)
- [ ] `Makefile` — a new `bench.export` target (name the planner's)
- [ ] `tests/test_calc.py` — 96-row Tier 1 matrix + refusal-composition rows (D-07/D-08)
- [ ] `tests/test_model.py` — ~18 Tier 2 built-solid rows (D-07/D-09)
- [ ] `tests/test_api.py` / `tests/test_cli.py` — the parity test (D-11), routing rows
      for the refusal matrix (D-08), `exc.value.code` asserts for D-13's `cli.md` fix
- [ ] `docs/architecture/cli.md` — "Errors" paragraph rewritten (D-13)
- [ ] `README.md` — one composed example link (D-14)

*(No framework install needed — pytest and every other tool are already pinned and
present.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface (single-user local/self-hosted CAD generator), unchanged by this phase |
| V3 Session Management | no | Stateless request/response |
| V4 Access Control | no | No access-control surface |
| V5 Input Validation | yes | `GearParams._feasible` remains the single validation choke point (unchanged); this phase's own work *proves* the existing bounds compose correctly under every combination, it does not add new input surface |
| V6 Cryptography | no | No cryptographic operation anywhere in this tool |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Resource exhaustion via a composed request that crosses `SPUR_BUILD_TIMEOUT` (this phase's own subject — D-03's checkpoint) | Denial of Service | `SPUR_BUILD_TIMEOUT` admission control (unchanged, `app.py`); D-03's lowered `le` on the pattern's own selector is the first-offer mitigation, applied the same way D-18 of Phase 11 already lowered `spoke_count`/`hole_count` |
| A composed row that silently under-reports which feature "vanished" on a shared solid | Tampering (silent) | D-09's re-run of each feature's own built-solid proof helper on the composed solid is exactly this mitigation — the same class of guard the tripwire pattern (Phases 7, 10, 11) already proves works |
| A stale documented contract (`cli.md`'s exit codes) misleading an integrator's own error-handling code | Tampering (of an external consumer's expectations, not this system) | D-13's doc rewrite plus `exc.value.code` pins in the CLI tests close this — the same "doc drift is a correctness bug" standard this project already applies to `bench/RESULTS.md` |

## Sources

### Primary (HIGH confidence)

- `bench/build_time.py` — read in full this session; the sweep runner this phase reuses unchanged
- `bench/corpus.py`, `bench/__init__.py`, `bench/README.md`, `bench/latency.py` (head), `bench/memory.py` (head) — read this session for the harness's existing conventions
- `bench/sweeps/hex_bore.json` — read this session for the sweep-file JSON schema
- `bench/RESULTS.md` — full header listing read this session (86 section headers), plus the "SPUR_BUILD_TIMEOUT", "Room beside Phase 10's tip-chamfer row", "make verify wall time", "Gate", and "Machine" sections read verbatim
- `tests/test_bench.py` — read in full this session; the sweep-pinning test pattern
- `src/spur/app.py` — the `_GZIP_LEVEL`/`_gzip`/`_build_slot` region and the `SPUR_BUILD_TIMEOUT` comment, both read verbatim this session
- `src/spur/model.py` — the L24 mesh-copy comment region, read this session
- `src/spur/params.py` — the full field-group listing, read via grep and direct read this session
- `src/spur/cli.py` — `_add_gear_args`, `cmd_export`, exit-code paths, read in full this session
- `docs/architecture/cli.md` — "Errors" section read verbatim this session
- `docs/architecture/decision_log.md` — L19 and L24 entries read in full this session
- `src/spur/static/app.js` — `buildForm`, `readHash`, `gearQuery`, `history.replaceState`, copy-link handler, all located by grep and read this session (line numbers verified: 45, 94, 101, 180, 348 — corrects CONTEXT.md's stale 49-89 citation)
- `tests/test_cli.py`, `tests/test_api.py`, `tests/test_calc.py`, `tests/test_model.py` — parity, schema, refusal-order and proof-helper sections all read this session
- `tests/regression/test_pre_v0_2.py` — read in full this session
- The four tech-debt files D-05/D-13/D-04 target — read in full this session
- `docs/tech_debt/INDEX.md`, `docs/ideas/INDEX.md` — read this session
- `.planning/config.json` — read this session; no `workflow.nyquist_validation` key present, treated as enabled per instructions
- Environment probes this session: `.venv/bin/python --version` → 3.12.13; `importlib.metadata.version('cadquery')` → 2.8.0; `importlib.metadata.version('cadquery-ocp')` → 7.9.3.1.1; `git rev-parse --short HEAD` → `2e4890a`; `uptime` → load averages 3.20/2.94/3.15

### Secondary (MEDIUM confidence)

None — every claim in this document was either read directly from a file this session
(HIGH) or is explicitly flagged as an assumption in the Assumptions Log (LOW).

### Tertiary (LOW confidence)

- A2 in the Assumptions Log (`bore_hex=200` vs. recorded spoke/hole rows' hub-clearance
  conflict) — CONTEXT.md's own `<specifics>` section already flags this as "no kernel
  probe was run this session," carried forward unverified rather than re-verified with a
  fresh kernel probe in this research pass (the phase's own framing says the composed
  sweep is where this gets resolved for real).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency; every version verified live against the
  installed venv this session.
- Architecture (bench harness, interface parity mechanism): HIGH — every file, function
  and line range cited was read directly this session, not inferred from CONTEXT.md's
  descriptions (one drift already caught: `app.js` line numbers).
- Pitfalls: HIGH for cli.md/exit-codes, HEX_CELL_CAP lever, and the memory.py-is-not-a-
  template point (all directly verified by reading code); MEDIUM for the exact composed
  hex-bore-vs-hub-datum arithmetic (Pitfall 6), since no kernel probe confirmed the 422
  fires this session — flagged as A2 in the Assumptions Log.

**Research date:** 2026-09-29
**Valid until:** This phase is expected to complete within days of this research; no
long validity window needed. Re-verify any cited line number if execution is delayed
past a subsequent commit touching the same files (the `app.js` drift already found is
the cautionary example).
