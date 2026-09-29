# Phase 12: Composition Pass - Pattern Map

**Mapped:** 2026-09-29
**Files analyzed:** 12 (1 new sweep, 1 new bench script, 2 modified bench files, 5 test
modules, 2 docs, 1 README)
**Analogs found:** 12 / 12 — this is an integration/measurement pass; every file either
extends an existing module in an established shape or copies an existing sibling file's
shape verbatim (sweep JSON, spike script). No wholly new architectural pattern is
introduced.

All analog paths below were checked with `git ls-files` this session; every one is
git-tracked source (no `.gsd/capabilities` mirrors in this repo).

RESEARCH.md flags that `static/app.js`'s function line numbers have drifted from
CONTEXT.md's citations (49-89 → the live numbers below: 45/94/101/180/348). This map
cites the live numbers RESEARCH.md verified this session, not CONTEXT.md's.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `bench/sweeps/<composed>.json` (new) | config/bench artefact | batch (measurement sweep) | `bench/sweeps/tip_chamfer.json` (whole file, verbatim shape) | exact |
| `bench/build_time.py` (+STL byte/triangle columns) | service (bench harness) | batch (build→export→report, in-process) | same file: `time_set` (76-86), `Timing`/`report`/`load_sweep`/`main` | exact |
| `bench/<export_cost>.py` (new, D-17) | utility/bench script | batch (measure gzip + copy cost, standalone) | `bench/honeycomb_spike.py` (whole file — standalone `-m bench.<name>` module, prints Markdown, exits 1 on failed verdict) | exact |
| `Makefile` (+`bench.export` target) | config | — | same file: `bench.build` target (121-124) | exact |
| `bench/RESULTS.md` (+3 sections) | doc/bench artefact | batch (record) | same file: Phase 10/11 sweep sections (host-state header, table, named heaviest row) | exact |
| `tests/test_bench.py` (+1 sweep-pinning test) | test | request-response (load→assert row set) | same file: `test_the_tip_chamfer_sweep_is_every_combination_d_06_names` (136-160-ish) and the Phase 11 hole/spoke/honeycomb pinning tests it documents in its own module docstring (1-19) | exact |
| `tests/test_calc.py` (+96-row Tier 1 matrix, +refusal-composition rows) | test | request-response (pure calc, no kernel) | same file: `test_infeasible_parameters_name_their_fields` (107), keyway refusal tests (315-395), hex-first order test (~333), two-cutout-patterns test (~888), `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (616) | exact |
| `tests/test_model.py` (+~18 Tier 2 built-solid rows) | test | request-response (build→assert on solid) | same file: `_assert_only_the_tip_arcs_were_chamfered` (705), `_assert_the_cutout_is_what_derive_prints` (1142), `_assert_the_recess_fillet_survives` (1302), `test_every_selector_takes_only_its_own_edges_with_a_body_cutout` (314), `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore` (1352) | exact |
| `tests/test_api.py` (+parity test, +routing rows) | test | request-response (HTTP-shaped, via test client) | same file: `test_schema_drives_the_form` (58), `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (120), `test_two_cutout_patterns_are_422_naming_both` (467) and its per-feature 422 siblings | exact |
| `tests/test_cli.py` (+parity test, +`exc.value.code` asserts) | test | request-response | same file: `test_cli_and_api_print_the_same_document` (47) + five per-feature siblings (145-277), `test_unknown_output_extension_is_refused` (288), `test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing` (294) | exact |
| `docs/architecture/cli.md` ("Errors" rewrite) | doc | — | same file, lines 33-36 (the paragraph being corrected) | exact |
| `README.md` (+1 composed example link) | doc | — | existing per-phase README example links (Phase 8-11 each added one) | role-match |

## Pattern Assignments

### `bench/sweeps/<composed>.json` (new, D-01)

**Analog:** `bench/sweeps/tip_chamfer.json` (whole file)

**Shape** (verbatim precedent, a flat JSON array of `GearParams`-shaped dicts):
```json
[
  {"teeth": 200, "module": 1.75, "tip_chamfer": 0.4, "recess_sides": "both"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 0.4, "recess_sides": "none"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 1.75, "recess_sides": "both"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 1.75, "recess_sides": "none"},
  {"teeth": 200, "module": 10, "tip_chamfer": 0.4, "recess_sides": "both"}
]
```
The composed sweep is each cutout's heaviest row (spoke `hub_d`52/`spoke_width`0.4/
`rim_wall`0.4/`spoke_fillet`5 at `le`40; holes at `le`60; honeycomb `hex_cell`3/
`hex_wall`0.4 at the cap) stacked with `tip_chamfer` at its per-gear cap and the largest
`bore_hex`/keyed round bore the row's hub rule allows (D-01, Claude's Discretion:
"heaviest bore" computed per row from `bore_mouth_limit(p) + MIN_WALL` against the
cutout's own hub datum — see RESEARCH.md Pitfall 6), at module 1.75 and 10, plus the six
single-feature baseline rows re-run unchanged. `load_sweep()` (`bench/build_time.py:56-71`)
validates every row through `GearParams.model_validate()` and raises naming the set/file
index on any 422 before any build — this is the mechanism that will surface Pitfall 6's
hub-clearance conflict immediately if a row is composed wrong.

---

### `bench/build_time.py` (D-16, new STL byte/triangle columns)

**Analog:** same file — `time_set` (verbatim, lines 76-86):
```python
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
D-16's two new columns (fine-STL byte count, triangle count) are a small addition beside
this function, inside `Timing`/`report` — not a rewrite. Read the triangle count from the
binary STL header directly (`int.from_bytes(data[80:84], "little")` — the same read
`tests/test_model.py:_stl_triangles` at line 1403 already does for content proofs), never
by iterating every facet — an O(1) header read is the pattern, not `_stl_triangles`'s
O(n) per-facet walk (that helper exists for content proofs, not counting; do not import
it for this).

---

### `bench/<export_cost>.py` (new, D-17: L19 gzip + L24 mesh-copy re-measurement)

**Analog:** `bench/honeycomb_spike.py` (whole file, standalone-module shape, verbatim
docstring pattern):
```python
"""Measures the honeycomb cutout before any honeycomb field exists (11-CONTEXT.md D-24,
ROADMAP Phase 11 SC3's research flag).
...
Run it as `.venv/bin/python -m bench.honeycomb_spike` from the repo root. It prints
Markdown and exits 1 when the verdict fails.
"""
```
Not part of `make verify` (confirmed: neither `honeycomb_spike` nor `tip_chamfer_spike`
appears in the `verify` target's dependency chain). The new script needs its own
`resource.getrusage(resource.RUSAGE_CHILDREN)` call in a parent process around a
subprocess export — **do not** import `bench.memory` (it polls `docker stats`' MEM USAGE
column via `_MEM_UNITS`/`POLL_INTERVAL = 0.5`, a container-level mechanism for a
different measurement target; RESEARCH.md Pitfall 4). Grep for `ru_maxrss`/`getrusage`
found exactly one hit in the whole repo — prose in the decision log, not code — so there
is no in-tree `resource.getrusage` call to copy; this script is the first one.

**L19 target — the exact code and its comment to re-measure against** (verbatim,
`src/spur/app.py`):
```python
_GZIP_LEVEL = 1

def _gzip(data: bytes) -> bytes:
    """gzip-encode at the level Task 1 measured (`_GZIP_LEVEL`, set from a real 9 MB STL,
    above)."""
    return gzip.compress(data, compresslevel=_GZIP_LEVEL)
```
The comment block directly above `_GZIP_LEVEL` carries L19's exact 1/6/9 table and the
selection rule D-18 applies as written: adopt a higher level only if it shrinks output by
≥10% **and** costs ≤1.5× the 10-concurrent wall of the level below.

**L24 target — the mesh-copy comment** (verbatim, `src/spur/model.py`, near 549-559):
```python
# and build() returns it after releasing _LOCK -- meshing it in place left
# .BoundingBox() reading the mesh (zlen 7.5000 -> 7.5877 mm after a preview
# ...reuse the fine mesh (46,278 triangles instead of 9,066). A copy keeps the
# cached solid mesh-free for its whole life, at 1.4-17.6 ms per export
# (L24) -- no positional argument to copy(): its one parameter is mesh,
# default False, and copy(mesh=True) would carry a mesh across.
shape.copy().exportStl(str(path), tolerance=tol, angularTolerance=ang, ...)
```
The script measures and records only — L24's copy cost stays a correctness decision, not
a cost trade (D-18: "L24's copy cost is recorded only").

---

### `Makefile` (+`bench.export` target)

**Analog:** same file, `bench.build` target (verbatim, lines 121-124):
```makefile
# bench.build needs no service: it times spur.model in-process, the code a worker runs
bench.build: $(STAMP)  ## build, fine STL and STEP time per set vs SPUR_BUILD_TIMEOUT; SWEEP=<json> (default: the Phase 8 hex-bore sweep)
	$(PY) -m bench.build_time $(SWEEP)
```
`bench.export` follows the same `$(STAMP)` dependency + `$(PY) -m bench.<name> $(SET)`
shape, with a one-line `##` help comment (`make` on its own lists targets — CLAUDE.md).

---

### `bench/RESULTS.md` (+3 new sections)

**Analog:** the Phase 10/11 sweep sections — host-state header, table, named heaviest
row. Same house style: a `### <Name> (Phase 12)` heading, an `uptime`/host line, a
Markdown table of rows and readings, then a sentence naming the heaviest/decisive row and
any `le`/timeout decision taken (D-01, D-16, D-17).

---

### `tests/test_bench.py` (+1 composed-sweep pinning test)

**Analog:** same file — the module's own docstring (1-19) documents the exact precedent
chain this new test extends (Phase 8 hex-bore, Phase 9 keyway, Phase 10 tip-chamfer,
Phase 11 body-cutout pinning tests); `test_the_tip_chamfer_sweep_is_every_combination_d_06_names`
is the closest single example (verbatim shape):
```python
def test_the_tip_chamfer_sweep_is_every_combination_d_06_names() -> None:
    sets = load_sweep(DEFAULT_SWEEP.parent / "tip_chamfer.json")
    assert len(sets) == 9
    module_chamfer_pairs = ((1.75, 0.4), (1.75, 1.75), (10.0, 0.4), (10.0, 3.0))
    want = {
        (200, module, 0.1, chamfer, recess)
        for module, chamfer in module_chamfer_pairs
        for recess in ("both", "none")
    }
    ...
```
The composed-sweep test follows the same shape: `load_sweep(...)`, `assert len(sets) ==
<N>`, a `set` of field tuples built from `itertools.product` (or written out — Claude's
Discretion) over the sweep's own axes, compared with `==` — never manual row-by-row
assertions (Pattern 3 in 11-PATTERNS.md, still current). `import itertools` and
`from pydantic import ValidationError` are already in this file's header (23-24).

---

### `tests/test_calc.py` (Tier 1: 96-row matrix + refusal composition)

**Analog:** same file — `test_infeasible_parameters_name_their_fields` (107) for the
422-naming-fields shape; the keyway refusal tests (315-395) and the "hex first" order
test (~333) for the refusal-order precedent D-08 extends; the two-cutout-patterns test
(~888) for the "every locked refusal × every other family switched on" composition shape;
`test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (616) for the cap-and-warn
test shape. Tier 1 rows call `calc.derive()` / `GearParams.model_validate()` directly —
no kernel import anywhere in this file (import-linter enforced) — so all 96 rows plus the
~40 refusal-composition rows run in the same microseconds-per-row budget this file
already runs at. Every refusal row asserts the same `(message, (field, ...))` shape
`check()` already returns (11-PATTERNS.md's 422-refusal contract, `calc.py:283-420`,
still current), including the sentence-order precedent when two refusals fire on one
parameter set ("hex first").

---

### `tests/test_model.py` (Tier 2: ~18 built-solid rows re-running each feature's own proof)

**Analog:** same file — the three proof helpers D-09 names, present and unchanged:
```python
# tests/test_model.py:705 (signature; body reused unmodified)
def _assert_only_the_tip_arcs_were_chamfered(cut: cq.Solid, plain: cq.Solid,
                                             p: GearParams, p0: GearParams) -> None: ...
# tests/test_model.py:1142
def _assert_the_cutout_is_what_derive_prints(...): ...
# tests/test_model.py:1302
def _assert_the_recess_fillet_survives(cut: cq.Solid, p: GearParams, torus: int) -> None: ...
```
Each Tier-2 row builds **one composed solid** and calls the relevant helper(s) on it — no
new proof shape (D-09 explicit: "composes correctly" means every single-feature proof
still holds when features share a solid). The existing matrices at 314
(`test_every_selector_takes_only_its_own_edges_with_a_body_cutout`, 19 rows) and 1352
(`test_the_recess_floor_fillet_survives_every_cutout_on_every_bore`, 13 rows) already
cover most cutout×bore pairs — Tier 2 does **not** repeat these rows (Claude's Discretion
note in CONTEXT.md), only the pairs no existing test builds (tip chamfer applied × 3
cutouts × 4 bores, and a single-sided recess × 3 cutouts). TORUS/CONE/edge counts on
composed rows are measured on the pinned kernel and pinned as literal numbers, never a
closed-form guess after an arbitrary boolean (11-PATTERNS.md precedent, still current).

**Proof + tripwire pattern**, if a composed tripwire is added (Claude's Discretion),
mirrors the tip-chamfer pair verbatim:
```python
def test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped(monkeypatch):
    monkeypatch.setattr("spur.model._chamfer_tips", lambda solid, _p, _pr: solid)
    assert derive(p).tip_chamfer_effective == 1.0  # the number still prints -- L08's failure
    with pytest.raises(AssertionError):
        _assert_only_the_tip_arcs_were_chamfered(...)
```

---

### `tests/test_api.py` / `tests/test_cli.py` (D-11 parity test, D-08 routing rows, D-13 exit-code asserts)

**Analog `test_api.py`:** `test_schema_drives_the_form` (58) generalises directly into
D-11's model-driven walk — same shape (read `/api/schema`, assert per-property
`group`/`title`/`unit`/`step`), just over every field instead of three; the group-set
assertion is new (the eight names {Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb} +
`recess_sides`'s own group). `test_every_key_the_ui_reads_is_a_derived_dimensions_field`
(120) is the precedent for the static `app.js`-reading check (D-11's shareable-URL
round-trip proof — read the source file, assert the hash→form→query path is generic, no
per-field code — never drive a browser). `test_two_cutout_patterns_are_422_naming_both`
(467) and its per-feature 422 siblings are the shape for D-08's one-API-row-per-refusal.

**Analog `test_cli.py`:** `test_cli_and_api_print_the_same_document` (47) plus five
per-feature siblings (145-277) are the shape D-11's composed-link parity assertion
generalises — `spur info` on the composed link printing `/api/info`'s document
byte-for-byte in `DerivedDimensions` key order. `test_unknown_output_extension_is_refused`
(288) and `test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing`
(294) are exactly where D-13's `exc.value.code` asserts land — read the real contract
from `cli.py`, not `cli.md`:
```python
# src/spur/cli.py:41-53 -- the generic flag generator D-11's CLI walk reads
def _add_gear_args(ap: argparse.ArgumentParser) -> None:
    g = ap.add_argument_group("gear parameters (defaults in brackets)")
    for name, field in GearParams.model_fields.items():
        flag = "--" + name.replace("_", "-")
        ...
```
Real exit-code contract (verified in `cli.py` this session, RESEARCH.md Pitfall 1):
argparse's own parameter-validation catch (`_params()`, ~line 89) does `raise
SystemExit(2)` — integer, exits **2**; `cmd_export`'s unknown-extension check and its
`BuildError` catch both do `raise SystemExit(f"error: ...")` — string, exits **1**. The
new asserts pin `exc.value.code == 2` only for the argparse path and `== 1` for both
`cmd_export` paths.

---

### `docs/architecture/cli.md` ("Errors" rewrite, D-13)

**Current (wrong) text being replaced** (verbatim, lines 33-36):
```
## Errors

Exit 2 with `error: …` on stderr for bad parameters and for an unknown output extension;
`BuildError` becomes `error: <kernel message>`. Nothing is written when the build fails.
```
Rewrite to state: argparse parameter errors exit 2; an unknown output extension and every
`BuildError` both exit 1 (string `SystemExit`, both in `cmd_export`). Same commit resolves
`docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md` —
flip `Status: resolved`, record the commit sha, `git mv` to
`docs/tech_debt/resolved/`, move its `docs/tech_debt/INDEX.md` row (matched by filename,
not by a numeric row position — the Active table has no row-number column; RESEARCH.md
Pitfall 3). `docs/tech_debt/INDEX.md`'s current Active table shape (verbatim header):
```
| Severity | Item | Trigger to revisit |
|---|---|---|
```

---

### `README.md` (+1 composed example link, D-14)

**Analog:** existing per-phase README example links (each of Phases 8-11 added its own
CLI/API example when it shipped a feature — role-match, not read verbatim this pass; find
the nearest existing example block and copy its Markdown shape). Values: one 19-tooth gear
with every v0.2 family on (keyed round bore, one cutout, a recess, tip chamfer) — the
`test_cli.py::test_readme_export_examples_run`-shaped test already exists and is extended
with this link rather than a new test file (RESEARCH.md's Phase Requirements → Test Map:
this row is "✅ existing test extended, not new file").

---

### `docs/tech_debt/{active,resolved}/*.md` (D-05, D-13 resolutions) and `docs/ideas/*.md` (D-12 verdicts)

**Analog:** CLAUDE.md's own debt-resolution recipe, already exercised by every prior
phase's must-debt resolutions: flip `Status: resolved`, add the commit sha, `git mv` into
`resolved/`, move the `INDEX.md` row — all in the same commit as the fix. `docs/ideas/`
verdict paragraphs follow the same file's own template shape (`docs/ideas/TEMPLATE.md`,
not read this session but referenced by every existing idea file) — append a "Judged at
Phase 12" paragraph and a new trigger sentence, do not delete or restructure the file.

---

### `docs/architecture/decision_log.md` (+1 append-only L31, D-19)

**Analog:** L27-L30 (own file, lines 826, 908, 1045, 1140) — each entry is dated, opens
with a one-line summary heading, and cites `SUMMARY.md` shas / `bench/RESULTS.md`
sections for every number, never re-estimating. L30's shape (verbatim heading, line
1140):
```
## L30 — Body cutouts are one pattern per part, cut in one boolean, and the honeycomb's
cell count is capped at a measured constant
```
followed by dated sub-sections ("The fields", "The cut", "The cost", ...) each citing a
`SUMMARY.md`/commit sha. L31 follows this exact shape: composed-sweep numbers and any
`le`/timeout decision, the matrix's measured verify cost, the parity proof, the L19/L24
re-measurement and any `_GZIP_LEVEL` change, the UI-pass verdict, the SC3/SC5 amendments
and the Success Metric 3 reading — each cited, none re-estimated. Append-only: never edit
L01-L30.

## Shared Patterns

### A number is measured on the pinned kernel via a committed script + `make` target, recorded with host state, cited by sha — never re-estimated
**Source:** `bench/honeycomb_spike.py` (whole file), `bench/build_time.py`'s `main`,
08-CONTEXT.md D-12, L27-L30.
**Apply to:** the composed sweep (D-01), the export-cost script (D-17), L31's every
citation.

### Rows over budget are recorded as measured, never dropped or silently re-run to green
**Source:** 11-PATTERNS.md's own precedent (11-06); this phase's D-02 (host load) and
D-03 (timeout checkpoint) apply the identical rule.
**Apply to:** every composed-sweep row; a non-quiet load reading is recorded beside the
number, not discarded (RESEARCH.md Pitfall 2 — this session's own `uptime` read
3.20/2.94/3.15, above D-02's <1.5 bar).

### A sweep file is pinned by one test comparing a `set` of field tuples built from `itertools.product`
**Source:** `tests/test_bench.py`, every existing per-sweep-file test (Pattern 3,
11-PATTERNS.md, still current); `itertools` already imported at line 23.
**Apply to:** the new composed-sweep pinning test (D-01).

### The 422-refusal contract: `(message, (field, ...))` tuples, if/elif non-stacking, order proven when two refusals fire together
**Source:** `src/spur/calc.py:283-420` (`check()`), 11-PATTERNS.md's "422-refusal
contract" (still current, unmodified this phase — no new refusal is added).
**Apply to:** every D-08 refusal-composition row; the sentence and `ctx.fields` must be
byte-identical whether the refusal fires alone or with every other family switched on.

### A proof reuses the feature's own helper; a tripwire shows it going red — never a new proof shape
**Source:** `tests/test_model.py`'s tip-chamfer proof/tripwire pair (630-657, quoted
above); 11-PATTERNS.md, D-09 explicit in 12-CONTEXT.md.
**Apply to:** every Tier 2 row (D-07/D-09).

### The model is the one source; CLI and form are generic loops over `GearParams.model_fields` / `schema.properties` — no per-field code to audit
**Source:** `src/spur/cli.py:41-53` (`_add_gear_args`), `src/spur/static/app.js`'s
`buildForm()` (line 45, confirmed live this session — corrects CONTEXT.md's stale 49-89
citation), `readHash()` (94), `gearQuery()` (101), `history.replaceState` (180), the
copy-link handler (348).
**Apply to:** D-11's entire parity test — it walks the model once and asserts against
three consumers, it does not write 30 per-field tests.

### Debt is resolved in the fixing commit: status flipped, sha recorded, `git mv`, INDEX row moved, matched by filename not row number
**Source:** CLAUDE.md; `docs/tech_debt/INDEX.md`'s Active table (no row-number column,
confirmed this session — RESEARCH.md Pitfall 3).
**Apply to:** D-05 (two build-timeout debt files) and D-13 (`cli.md` debt file), same
commit as each fix.

## No Analog Found

None. Every file this phase touches either extends an existing module in an established
in-tree shape, or is a new file that copies an existing sibling file's shape verbatim
(the composed sweep JSON copies `tip_chamfer.json`'s shape; the export-cost script copies
`honeycomb_spike.py`'s standalone-module shape). The one piece of the export-cost script
with no in-tree precedent to copy directly is the `resource.getrusage` peak-RSS reading
itself — RESEARCH.md confirms via full-repo grep that no committed script does this today
(the only prior hit is prose in the decision log) — flagged here so the executor does not
go looking for a `bench/` helper that does not exist; `bench/memory.py`'s Docker-polling
mechanism is explicitly not a template (Pitfall 4, Shared Patterns above).

## Metadata

**Analog search scope:** `bench/{build_time.py,honeycomb_spike.py,sweeps/,RESULTS.md}`,
`Makefile`, `tests/test_{bench,calc,model,api,cli}.py`, `src/spur/{app,model,cli,params}.py`,
`src/spur/static/app.js`, `docs/architecture/{cli.md,decision_log.md}`,
`docs/tech_debt/{INDEX.md,active/}`, `docs/ideas/INDEX.md`, `README.md`.
**Files scanned:** 12 source/test/bench/doc files read or grepped directly this session
(via 12-CONTEXT.md/12-RESEARCH.md's own verified excerpts, cross-checked live for the
Makefile, `honeycomb_spike.py`, `tests/test_bench.py`, `docs/tech_debt/INDEX.md`,
`docs/ideas/INDEX.md`, and `decision_log.md`'s L27-L31 heading positions), plus the prior
phase's `11-PATTERNS.md` read in full for shape continuity.
**Pattern extraction date:** 2026-09-29
