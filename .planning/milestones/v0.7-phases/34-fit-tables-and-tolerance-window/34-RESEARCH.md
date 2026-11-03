# Phase 34: Fit Tables and Tolerance Window - Research

**Researched:** 2026-10-30
**Domain:** a private, validated DIN 5480 table file feeding pure shaft maths, a CAD worker and three front ends; two-read transcription of a licensed standard
**Confidence:** HIGH on the code seams and the transcription mechanics (all read or run this session); MEDIUM on Table 7's nomogram semantics (one image page, no text layer, one open convention); LOW on nothing the plan cannot gate behind a checkpoint

**Licence note for readers of this file.** No table value, clause text or page image of DIN 5480 is in this file. It records structure (column names, row counts, units, layout quirks), counts and coarse statistics of unnamed rows, the values quoted in 34-CONTEXT.md, and values already committed in `tests/test_din5480_anchors.py`. Every scratch artefact of this research (rendered pages, `read1_probe.py`, its JSON output) is in the session scratchpad and is not in the repo.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### The copy and the private file
- **D-01:** The copy is on the human's machine:
  - `~/Downloads/ISO standards/din-5480-1.pdf` is DIN 5480-1:2006-03, the unofficial English translation (27 pages), the same copy as Phase 31.
  - `~/Downloads/ISO standards/din-5480-2.pdf` is DIN 5480-2:2006-05 (40 pages), the same copy.

  Nothing from the copy is committed, except the anchors the human approves by name (D-07). The PDFs carry a licence stamp naming a third party, so no clause text, table or page image enters the repo.
  - The scratch renders and extractions go in the session scratchpad, not the repo.
  - **Reversibility:** one-way. A committed value is public history.
- **D-02:** One environment variable, `SPUR_DIN5480_TABLES`, names the file. There is no config file and no default path. The API server, every worker and the CLI read the same variable.
- **D-03:** The file is one JSON document, validated at the loader boundary by a pydantic model.
  - Every row carries its provenance: part, clause and table (REQ-tables-transcribed-twice).
  - The two reads produce documents in the same schema, so they diff to zero as sorted JSON.
- **D-04:** When the file is unset, missing or broken:
  - Unset: table numbers are `null`, with a warning naming the missing file (REQ-tables-private-file). The part still builds.
  - Set, but missing, unreadable or failing a structural check: the server and the CLI refuse to start and exit with the reason. A file someone meant to load that degrades quietly to `null` would be a silent partial success.
  - The structural checks: `T_G = T_act + T_eff`, the µm-against-mm range, and no Unicode minus. The check must be seen failing once against a deliberately broken row.
  - **Reversibility:** reversible. This is startup policy, not a wire contract.

#### The two independent reads
- **D-05:** Part 1 Table 7 has no text layer. It is an image of a nomogram:
  - the deviation series a to v (shaft) across the d_B ranges and the module groups 0.5 to 1.5, 1.75 to 4 and 5 to 10;
  - 24 rows of T_G, T_act and T_eff;
  - diagonal lines from the tolerance class (5 to 12) through the module group and d_B to a tolerance row.

  It is read twice, by two blind vision reads: two separate agents each read the rendered page alone and write JSON in the D-03 schema. Neither sees the other's output, and the files are then diffed.
  - The page's own worked example, W 120x3x38x8f, must come out of the result:
    - s_vmax 6.243, s_max 6.220 and s_min 6.180;
    - T_G 63 µm, T_act 40 µm, T_eff 23 µm and A_s −28 µm.
  - That example ties to Phase 31's approved anchor `M1` minimum 125.956 at s 6.180.
  - Table 6, the formulas for the limits, has a text layer. Table 9, the types of fit, also has a text layer.
- **D-06:** Part 2 is read twice by two different methods. They fail in different ways.
  - Read 1 is a `pdftotext -layout` parser, like Phase 31's scratch parser (720 nominal and 721 inspection rows).
  - Read 2 is an agent reading the rendered pages.
  - The copy prints decimal commas, a duplicated Table 12 row (d_B 20 where Table 13 has 19), and licence-stamp lines in the body text. The parser handles each of these on purpose.
- **D-07:** The anchors are chosen at a human checkpoint, as in Phase 31 D-06.
  - The plan stops and shows the candidate rows. At least: the page's W 120x3x38x8f example, the default shaft W 25x1.25x18x8f, and one odd tooth count.
  - The human approves each by name.
  - Only the approved values are committed, as tests, each seen red once.
- **D-08:** When the two reads disagree, the human settles it from the page.
  - The plan lists each disagreement with its table, row, column and page.
  - Nothing loads, and no number prints, until the diff is zero.

#### The pin and the M_Re limits
- **D-09:** For a size in the tables:
  - D_Re is the tabulated D_M.
  - M_Re is computed for that pin, by the existing `din5480.measure_over_pins`. It is not copied from M1.
  - A test over the anchor rows checks the computed M against the table's M1.
  - This replaces the theoretical pin and changes an output number only, so L05 does not apply (31 D-10).
  - When the switch happens, the warning says so. `THEORETICAL_PIN` stays in force off the table.
- **D-10:** M_Re maximum and minimum are computed by the formula at the actual thickness limits of Table 6, with the tabulated pin:
  - s_max = s1 + A_s − T_eff;
  - s_min = s1 + A_s − T_G.

  This is how Phase 31 matched the copy's M1 minimum, 125.956 (difference 0.00004). Part 2's deviation factor A*M1 is not used, so it is not transcribed.
  - `MEASURE_AT_NOMINAL_THICKNESS` is retired wherever the limits print (31-03 handoff).
- **D-11:** An odd tooth count prints M_Re and its limits at the tabulated pin, for a size in the tables (211 of 211 odd Part 2 rows agree).
  - Off the table, or with no file, an odd tooth count stays `null` with `ODD_Z_UNCONFIRMED`, as today.
  - This resolves the idea item `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md`.
- **D-12:** For a tabulated size, the pin-contact guard's lower bound is the copy's d_Ff1 maximum plus the margin. The real form circle lies at or below that maximum, so contact above it is safe.
  - Off the table, the theoretical pin stays. That guard cannot fire (31 D-20), and the internal construction stays internal.
  - This resolves `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`.
  - Its test: over the approved rows, the bound is at or below the maximum.
  - The guard goes live with the tabulated pin. If it fires on a tabulated row, that is a finding to surface, not something to widen silently.

#### The solid and the fit rules
- **D-13:** With the tables loaded and the fit in the tables, the solid carries the maximum effective tooth thickness s_vmax = s1 + A_s (REQ-solid-max-material), read back from the solid. Otherwise it carries the nominal thickness, with a warning that says so.
  - A user can tell the two apart in two ways: a row with the thickness the solid carries, and the nominal-thickness warning.
  - The download name stays as L49 froze it.
  - The tables load once at startup and stay fixed for the process, so the solid cache, keyed by the parameters, stays correct.
  - **Reversibility:** costly. The new row's key and place become part of the info response's rows once released.
- **D-14:** A fit outside Table 7 (e.g. `3z`) gives a warning and `null`, as the roadmap says. It is not a `422`.
  - The part builds at nominal.
  - The warning names Table 7's deviation letters and tolerance classes.
  - `FIT_PATTERN` is unchanged, so no link that validates today starts failing.
  - This resolves `docs/tech_debt/active/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md` through the warning.
- **D-15:** The user sees five new limit rows:
  - s_vmax (maximum effective);
  - s_max and s_min (actual);
  - M_Re maximum and minimum.

  - A_s, T_G, T_act and T_eff are not printed.
  - The existing nominal `measure_over_pins` row stays.
  - The new rows ride Phase 33's list of rows carried on the schema, and the parity test covers them (ROADMAP criterion 3).
  - **Reversibility:** costly. Each row key becomes a wire key in the info response and the CLI output.

### Claude's Discretion
- The JSON schema's shape. D-03 fixes JSON, pydantic and per-row provenance; the planner designs the rest.
- Where the loader lives, and how the tables reach `derive_shaft`. The shaft maths must stay free of the logger and the kernel (import contracts), and must do no file I/O on every keystroke.
- The row keys, labels and order, within D-15.
- The wording of the warnings, following the existing sentence style in `shaft_calc.py`.
- How the two reads' agents are prompted, within D-05 and D-06 (blind, one schema, no shared output).

### Deferred Ideas (OUT OF SCOPE)
- Span measurement W_k with k (Part 2's inspection tables print it). It is a new measurement method, so a later phase.
- The hub (internal spline) and its space-width window. Out of scope (REQUIREMENTS).
- The shift-range exceptions for large tooth counts: the existing debt item stays active, and Phase 34 does not touch it.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-tables-private-file | Transcribed values load from a gitignored file whose path is set by env; without it every table-dependent number is `null` with a warning naming the missing file; no transcribed value committed beyond approved anchors | Loader in `din5480_tables.py` (already named in 6 import contracts); lazy per-process state; `private/` + `.gitignore` + `.dockerignore`; "Common Pitfalls" 9 and 10 (leak routes) |
| REQ-tables-transcribed-twice | Two independent reads diffed to zero; every row carries part/clause/table; loader invariants seen red once | Schema proposal; read-1 feasibility probe (721/721 rows); canonical-JSON diff tool; load-time M1 identity (721/721 pass); invariant list and the three broken-row reds |
| REQ-fit-tolerance-window | For a tabulated size and fit the user sees the effective and actual tooth-thickness windows; a fit outside the tables is a warning and `null` | Table 6 formulas (text layer); Table 7 structure; tier matrix; 5 new `ShaftDimensions` keys; `dims` rows ripple |
| REQ-mre-limits | M_Re max and min at the chosen fit with D_Re from the copy, proved against the oracle on the anchor rows | `measure_over_pins(m, z, s, pin_d)` takes a thickness already; oracle `measure(m, z, x, pin)` with the "thickness written as the shift" trick (existing anchor test); guard-at-limit finding |
| REQ-solid-max-material | With tables loaded the solid carries s + es, read back; without, nominal with a warning | `build_shaft` reads `derive_shaft`; `_outline` takes `xm`; read-back pattern `_flank_error`; pool/CLI/cache plumbing |
| REQ-off-table-builds | A d_B/m/z absent from the size tables builds from the formulas with every table-dependent number `null` and warned | Tier matrix; exact-key lookup, no snapping (L08) |
| REQ-gate-cost-recorded | Each phase records `make verify` time against its predecessor; the milestone close reading is inside L43's 300 s or the human decides | `bench/RESULTS.md` `### The gate delta (33-09)` is the predecessor reading (242.47 s real, 2778 passed); recording pattern and phase-close checks |
</phase_requirements>

## Summary

Phase 34 is three problems that happen to share one file. (1) **Plumbing:** one process-wide, lazily loaded, validated `Tables` object, read from `SPUR_DIN5480_TABLES`, reaches `derive_shaft` through a module accessor with no per-call I/O; the composition roots (`app.lifespan`, `cli.cmd_serve`, `cli` shaft commands) force the load early so a set-but-broken file stops the process with the reason. The loader module already exists as an empty, contract-named file (`src/spur/din5480_tables.py`), so six import contracts and the seam belts are already in force around it. (2) **Transcription:** Part 2 (721 nominal and 721 inspection rows over 16 modules, one page per table) has a clean text layer; a 40-line `pdftotext -layout` parser read all 721 + 721 rows in this session, and the table values it read reproduce the printed M1 on **721 of 721** rows through `din5480.measure_over_pins` at the tabulated pin and the formula thickness (worst difference 0.0005, the printed half unit). That identity is a free, strong load-time check and should be a loader invariant. Part 1 Table 7 is a single 600 ppi image page (19 stacked strips, no text layer): 18 deviation letters x 9 columns of A_s, an 8-class x 9-column diagonal map into 24 tolerance rows, and a skewed grid that maps 7 d_B ranges x 3 module groups onto the 9 columns. (3) **Maths and solid:** Table 6's three formulas are trivial; the work is the tier matrix (no file / size absent / fit absent / all present), the pin switch, the guard going live, five new rows, and the solid taking a thickness.

Three findings the planner must not miss. **(a)** The default shaft's d_B (25) sits exactly on a Table 7 reference-diameter range edge; the page's worked example is interior and proves nothing about edges. The header uses "über/bis"; the DIN convention (over x, up to and including y) is [ASSUMED] and a wrong choice silently moves the default shaft one column. It needs the human at the D-07 checkpoint. **(b)** The guard going live is not a formality: at the tabulated pin and the **nominal** thickness it fires on 0 of 710 in-range tabulated rows, but its worst row has only about 0.06*m of margin above the lower bound, and a limit thickness moves the contact by up to about 0.08*m per 0.05*m of thickness. A coarse fit can therefore push a limit-thickness measurement outside the window. D-12 already says that is a finding to surface; the plan needs a sweep and a per-limit null, not a single nominal check. **(c)** Disagreement listings (D-08) and sweep logs are the habitual leak route: this repo commits `investigation/*.log` files, and a log of "reading A says X, reading B says Y" is a table value. Location-only listings in anything committed; values only in the conversation and in gitignored files.

**Primary recommendation:** Build the loader and every consumer against a **synthetic** table builder (invented filler plus only the approved anchor values), land the read tooling and both reads in parallel behind human checkpoints, wire the real file last; keep the loader a lazily loaded module-level state in `din5480_tables.py`, hand the parent's loaded object to build workers through `ProcessPoolExecutor(initargs=...)`, insert the five new keys as one block right after `measure_over_pins`, and log the whole phase as `L50`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read, validate and hold the private table file | Backend startup (`din5480_tables.py`, called from `app.lifespan` and `cli`) | Pool worker (receives the parent's object) | Once per process, never on the keystroke path; the module is already inside the shaft-maths import walls (no kernel, no logger) |
| Refuse to start on a set-but-broken file | Composition roots: `cli.cmd_serve` and the shaft CLI commands; `app.lifespan` as defence in depth | — | Startup policy, not a wire contract (D-04); the CLI may not import `app` (contract), so both call the same loader function |
| Table-dependent numbers (windows, M_Re limits, tabulated pin, guard bound) | API/Backend shaft maths (`derive_shaft`, `shaft_calc.py`; Table 6 formulas in `din5480.py`) | CLI (same function) | Pure arithmetic over floats; one document for API, CLI and page |
| Maximum-material tooth thickness in the solid | CAD build worker (`shaft_model.py`) reading `derive_shaft` | — | `build_shaft` already takes every printed number from `derive_shaft` (L08) |
| Display of the five rows | Browser, generically from `dims` in the shaft schema | — | The page prints non-null rows from the schema; no page code (CONTEXT, `app.js:444-459`) |
| Transcription tooling (parser, canonical diff, completeness check) | Developer-time scripts (`scripts/`, `make` targets) | — | Never imported by the package; no licensed value in code |
| Private file and reads at rest | Operator's disk, repo-local gitignored `private/` (recommended) | — | Must be unreachable by `git add`, by the Docker build context and by the wheel |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.13.5 [VERIFIED: requirements.txt:29; `.venv` import] | The table schema, strict, `extra="forbid"`, frozen | Already the project's boundary validator (L02, CODING_VALUES "validated once") |
| stdlib `json`, `os`, `pathlib`, `hashlib`, `re`, `subprocess` | Python 3.12.15 [VERIFIED: `.venv/bin/python -I`] | File read, env var, canonical dump, the read-1 parser | No new dependency; `requirements.txt` must stay byte-identical (ROADMAP Phase 30/34 boundaries) |
| `pdftotext` (poppler) | 26.10.0 [VERIFIED: `pdftotext -v`, `/opt/homebrew/bin`] | Read 1 of Part 2, developer-time only | The text layer of Part 2 is clean (721/721 rows read) |
| `pdftoppm`, `pdfimages` (poppler) | same [VERIFIED: `which`] | Page renders for the vision reads | Page 24 of Part 1 holds 19 native-resolution strips (3689x271 px at 600 ppi) [VERIFIED: `pdfimages -list`], so a 600 ppi render loses nothing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest, pytest-xdist | 9.1.1 [VERIFIED: import] | The existing runner (`-n 8`, `fail_under = 96`) | All new tests; real-file tests use `skipif` on the env var |
| fastapi `TestClient` | 0.141.1 [VERIFIED: requirements.txt:20] | Lifespan-refusal test: `with TestClient(app)` runs the lifespan, a bare `TestClient(app)` does not | tests/test_pool.py already uses both forms |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Module-level lazy accessor `active()` | An explicit `tables` argument through `derive_shaft`, `build_shaft`, `model.export`, `BuildPool.export` | Pure, but it changes the signature of every caller and every existing test, and the worker still needs process state; the accessor is one mechanism for parent, CLI and worker |
| `initargs` hands the parent's `Tables` to workers | Workers re-read the env var in `_warm` | Re-read is one line and is the literal D-02, but a replaced worker (`recreate_for`) could read an edited file and diverge from the parent mid-run, breaking D-13's "fixed for the process"; `initargs` costs about 6 lines and removes the case |
| Repo-local `private/` (gitignored) | A path outside the repo (`~/...`) | Outside the repo cannot be committed at all; repo-local satisfies the roadmap's "gitignored file" wording and keeps the working files beside the code. Needs the three guards in Pitfall 9 |
| PyPI/npm packages for PDF or table extraction | — | None needed and none may be added (`requirements.txt` frozen); do not add |

**Installation:** none. `make venv` is unchanged.

**Version verification:** no package is added, so there is nothing to look up on a registry; the versions above are the installed, pinned ones.

## Package Legitimacy Audit

No external package is installed by this phase (stdlib, the already pinned pydantic, and the system tool poppler). `requirements.txt` stays byte-identical.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 OFFLINE (developer time, once)                                RUNTIME (every process)
 ──────────────────────────────                                ───────────────────────
 din-5480-2.pdf ──pdftotext -layout──► read-1 parser ─┐
        └─pdftoppm renders──► vision agent B ─────────┤        SPUR_DIN5480_TABLES (env)
 din-5480-1.pdf p.24 ──600 ppi render──► vision agent 1 ┤           │
        └──────────────────────────────► vision agent 2 ┤           ▼
                                                        ▼   din5480_tables.active()
                       canonical-JSON diff (scripts/) ──► human settles each disagreement
                                                        ▼        │  (lazy, once per process,
                                  private/din5480-tables.json    │   TablesError on a bad file)
                                  (gitignored; make tables.check)│
                                                                 │
   cli.main (serve / shaft *) ──► active() ── refuse: SystemExit("error: <reason>")
   app.lifespan ───────────────► active() ── refuse: exception => uvicorn exits (code 3, workers=1)
                                   │
                                   ├─► BuildPool(tables=active())  ──initargs──► _warm(tables) in each
                                   │                                              build worker (spawn)
 HTTP /api/shaft/info ─┐           ▼
 spur shaft info ──────┼──► derive_shaft(p)
 build_shaft(p) (worker)┘     1. key = (module, reference_d, teeth)  ── exact float match, no snapping
                              2. size row?  no ─► formulas only, theoretical pin, ODD_Z gate, 5 rows null, warn
                                            yes ─► pin = D_M (tabulated), guard floor = d_Ff1 max + 0.1*m
                              3. fit in Table 7 (letter in series, class in 5..12)?
                                            no ─► nominal M at the tabulated pin, 5 rows null, warn (names Table 7's set)
                                            yes ─► column = f(module group, d_B range); A_s, T_G, T_act, T_eff
                                                   s_vmax = s1 + A_s ; s_max = s_vmax - T_eff ; s_min = s_vmax - T_G
                                                   M_Re max / min = measure_over_pins(m, z, s_max / s_min, D_M),
                                                   each through the contact-window guard
                              4. ShaftDimensions (18 keys) ──► JSON (API, CLI) ──► page rows from schema `dims`
                                 build_shaft reads the printed s_vmax (or nominal) ──► _outline ──► solid
```

### Recommended Project Structure
```
src/spur/
├── din5480_tables.py     # models, load_file(), active(), install(), TablesError, lookups, canonical()
├── din5480.py            # + Table 6 limit formulas as pure functions (cited); flank_half_angle takes a thickness
├── shaft_calc.py         # derive_shaft ordering, tier matrix, new ShaftDimensions keys, new warning constants
├── shaft_model.py        # build_shaft passes the printed thickness to _outline
├── shaft_params.py       # + 5 entries in the `dims` list, `fit` description text
├── pool.py               # BuildPool(tables=...) -> initializer initargs
├── app.py                # lifespan: active() before BuildPool
└── cli.py                # serve + shaft commands: refuse on TablesError
scripts/
├── din5480_read1.py      # Part 2 pdftotext parser (no values in code; pdf path is an argument)
└── din5480_tables.py     # `diff A B` (location-only report) and `check FILE` (invariants + completeness)
private/                  # gitignored: din5480-tables.json, reads/*.json  (never src/, never tests/)
tests/
├── din5480_tables_fixture.py   # not collected: synthetic builder + approved anchors
├── test_din5480_tables.py      # light: schema, invariants (seen red), lookups, env semantics, canonical/diff
├── test_din5480_read1.py       # light: parser against synthetic text in the copy's layout
└── test_din5480_real_tables.py # skipif no env var: the real file against every approved anchor and sweep
```

### Pattern 1: Process-wide tables as lazily loaded module state
**What:** `din5480_tables.active() -> Tables | None` reads `os.environ["SPUR_DIN5480_TABLES"]` on the first call, validates, caches the result (including "unset") for the life of the process; `install(tables)` sets it for a worker; a `reset()` exists for tests. A broken file raises `TablesError` (a `ValueError` subclass whose `str()` is the reason, the shape of `DesignationError`).
**When to use:** every consumer (`derive_shaft`, CLI, lifespan, `_warm`).
**Why this and not a startup-only `configure()`:** an entry point that never calls `configure()` (a library import, a replaced worker, a test) would otherwise report "no file is set" while the variable is set, which is a false statement in a warning (L08). Lazy load makes the variable the one source (D-02); the startup code calls `active()` only to turn a bad file into a refusal at the right moment.
**Constraint:** `din5480_tables` may import `os`, `json`, `pathlib`, `pydantic` and `.din5480`; it may not import `logging`, `records`, `model`, `shaft_model`, `calc` or `cadquery` [VERIFIED: pyproject.toml contracts "The shaft maths stays free of the CAD kernel and the solid", "... of the logger", "... copies the gear maths"; belt `tests/test_seam.py::test_the_shaft_maths_imports_no_kernel_no_solid_no_logger_and_no_gear_maths`].
**Example:**
```python
# Sketch; every name is a proposal. No value of the standard appears in it.
_UNSET = object()
_state: Tables | None | object = _UNSET     # one write per process (documented module state, D-13)

def active() -> Tables | None:
    global _state
    if _state is _UNSET:
        raw = os.environ.get("SPUR_DIN5480_TABLES", "")
        _state = load_file(Path(raw)) if raw else None   # raises TablesError
    return cast("Tables | None", _state)
```
`ruff` has `PLW`/global rules off; `mypy --strict` with `disallow_any_explicit` needs `object` narrowing, as written.

### Pattern 2: Startup refusal, one function, three call sites
**What:** `cli.py` calls `active()` at the top of `cmd_serve`, `cmd_shaft_info` and `cmd_shaft_export` and converts `TablesError` into `raise SystemExit(f"error: {exc}") from None`, the exit-1 shape `cmd_export` already uses for a `BuildError` [VERIFIED: src/spur/cli.py cmd_export; docs/architecture/cli.md "Errors"; tests/test_cli.py asserts `exc.value.code == "error: ..."` and a real-process `returncode == 1`]. `app.lifespan` calls `active()` before `BuildPool(...)` and lets the exception propagate.
**Gear CLI commands (`info`, `export`) do not call it:** a broken shaft table must not stop a gear export (gear-unchanged ethos; CONTEXT says "the server and the CLI" and the CLI's only table consumer is the shaft group). [ASSUMED: A5]
**Why `cmd_serve` pre-validates:** uvicorn 0.53.0 with one worker prints the lifespan traceback, "Application startup failed. Exiting." and exits with code 3 [VERIFIED: probe run this session, `boom_app.py` in the scratchpad: `exit=3`]. With `workers > 1` the probe failed for an unrelated socket reason in this sandbox ("Address already in use" in the child), so the multi-worker supervisor's behaviour on a lifespan failure is **not verified**. A pre-check in the parent before `uvicorn.run` makes the refusal independent of that, and the clean `error: <reason>` line is the one operators read.
**How tests exercise it:** (1) unit: `din5480_tables.load_file(bad)` raises with the invariant named; (2) `pytest.raises(SystemExit)` around `cli.main([...])` with the env var pointing at a broken file (the `test_cli.py` pattern, `exc.value.code` string); (3) `with pytest.raises(TablesError): with TestClient(app): ...` for the lifespan; (4) one real-process test, `subprocess.run([sys.executable, "-m", "spur.cli", "serve", "--port", "0"...], timeout=...)` expecting a non-zero return and the reason on stderr and no listening socket, costing about 2 s like the existing real-process CLI test [CITED: tests/test_cli.py:497 "costs ~2 s"].

### Pattern 3: Hand the parent's tables to the build workers
**What:** `BuildPool.__init__(self, workers, timeout, *, tables=None)` stores `tables`; both `ProcessPoolExecutor(...)` constructions (`__init__` line 96 and `recreate_for` line 160 [VERIFIED: src/spur/pool.py]) pass `initializer=_warm, initargs=(tables,)`; `_warm(tables)` calls `din5480_tables.install(tables)` then imports `spur.model` as today. `lifespan` passes `tables=din5480_tables.active()`. A pydantic frozen model pickles (151 bytes for a two-field probe; the real object is a few hundred KB at most) and goes across `spawn` once per worker.
**CLI in-process builds** (`spur shaft export` calls `model.export` in the same process) read the module state directly.
**Solid cache:** `model._build_cached = lru_cache(maxsize=SPUR_SOLID_CACHE)(...)` and `app._EXPORTS` are keyed by the parameters only [VERIFIED: src/spur/model.py:810; src/spur/app.py `key = (params, fmt, quality, encoding)`]. That is correct because the tables are fixed per process (D-13) and the caches are per process. **Tests that flip tables inside one process must `model._build_cached.cache_clear()` and replace `app._EXPORTS`**, or the second build returns the first build's solid (existing tests already call `cache_clear`, e.g. `tests/test_shaft_model.py:435`).

### Pattern 4: The tier matrix is the contract for REQ-off-table-builds
| Situation | Pin D_Re and M_Re | Guard floor | Odd z | Five limit rows | Solid | Warnings added |
|-----------|-------------------|-------------|-------|-----------------|-------|----------------|
| `SPUR_DIN5480_TABLES` unset | theoretical pin, nominal M (as today) | internal construction (cannot fire, 31 D-20) | `ODD_Z_UNCONFIRMED`, null | all null | nominal | "no table file is set (`SPUR_DIN5480_TABLES`)", solid-at-nominal |
| Set, size not listed | as unset | as unset | as unset | all null | nominal | "size not in DIN 5480-2's tables", solid-at-nominal |
| Set, size listed, fit not in Table 7 | **tabulated D_M**, M at nominal thickness for that pin; odd z prints | d_Ff1 max + 0.1*m | prints | all null | nominal | pin-switch sentence, fit sentence naming Table 7's letters and classes, solid-at-nominal |
| Set, size and fit listed | tabulated D_M, nominal M | d_Ff1 max + 0.1*m | prints | s_vmax, s_max, s_min, M_Re max, M_Re min | s_vmax | pin-switch sentence only (limits sentence replaces `MEASURE_AT_NOMINAL_THICKNESS`) |
Row 3 is a reading of D-09 ("for a size in the tables ... D_Re is the tabulated D_M", independent of the fit) and D-14 ("a fit outside Table 7 ... warning and null ... builds at nominal"); it is not stated outright for the combination. [ASSUMED: A6]
The off-size case must stay byte-identical to today's numbers (only warnings and null rows are added): the existing `THEORETICAL_PIN` text says "DIN 5480-2 tabulates its own measuring pin D_M for the sizes it lists" [VERIFIED: src/spur/shaft_calc.py:46-49] and stays valid there.

### Pattern 5: Thickness reaches the solid as a printed number
`build_shaft` takes tip and root radii from `derive_shaft` and only the flank from `din5480.flank_half_angle` [VERIFIED: src/spur/shaft_model.py:176-186]. Add one printed number (the thickness the solid carries) and pass it to `_outline`. Two ways, planner's choice:
- Give `flank_half_angle` an optional `s` (thickness on the circle `m*z`, default `tooth_thickness(m, xm)`), the way `measure_over_pins` already takes `s`.
- Or pass `_outline` the shift that gives that thickness, `xm_flank = (s - pi*m/2) / (2*tan(ALPHA))`, which needs no `din5480.py` change; `tests/test_din5480_anchors.py` already uses exactly this inversion for the oracle.
The printed row is rounded to 0.001 (`r3`), so the solid carries the printed value, as it does for `tip_d` and `root_d` (L08: part and number cannot name different shafts). Tip and root diameters do not change with A_s.

**Read-back (REQ: "read back from the solid").** Existing pattern: `_flank_error` in `tests/test_shaft_model.py` samples every BSPLINE edge of a z-section at 201 positions and compares the polar half angle with `shaft_oracle.tooth_half_angle(m, z, x, r)`; the oracle takes the shift `x`, so a solid at s_vmax is compared against the oracle at `x_eff = (s - pi*m/2)/(2*m*tan(30 deg))` [VERIFIED: tests/test_shaft_model.py:134-165; shaft_oracle.py `tooth_half_angle`]. Add a direct reading as well: the arc thickness at radius `m*z/2`, interpolated from the section's flank points, equals the printed s_vmax within the flank bar (`FLANK_BAR_PER_MODULE = 5e-4` mm per mm of module). `_guard_volume` cannot see thickness (its bracket uses the face's own area), so this read-back is a test, not an in-build guard.

### Pattern 6: The file's schema (proposal; D-03 fixes only JSON, pydantic and per-row provenance)
Every model: `ConfigDict(frozen=True, extra="forbid", strict=True)`; every float `Field(allow_inf_nan=False)`; units in the field name (`_mm`, `_um`) so the unit check is typed, not commented. Micrometre fields are `int` (a millimetre slip such as 0.063 fails as a non-int; the printed Table 7 values are whole micrometres on the rendered page). Provenance is a nested model on **every row**.
```
Provenance : part: Literal[1, 2]; clause: str; table: str; page: int          # PDF page = printed page in both copies
SizeRow    : provenance; module: float; reference_d: float; teeth: int         # key = (module, reference_d, teeth)
             pin_d_mm  (shaft D_M, Part 2 inspection table, shaft block)
             m1_mm     (printed M1, used only by the load-time identity)
             form_d_max_mm (d_Ff1 max, Part 2 nominal table, shaft block)
DeviationRow : provenance; letter: str; a_s_um: tuple[int, ...]                # 9 signed values, the merged `h` cell expanded
ClassRow     : provenance; tolerance_class: int; row_by_column: tuple[int, ...]# 9 values, 1-based index into ToleranceRow.row
ToleranceRow : provenance; row: int; t_g_um: int; t_act_um: int; t_eff_um: int # 24 rows
ColumnMap    : provenance; module_group: Literal[1, 2, 3]; d_b_over_mm: float | None; d_b_upto_mm: float | None; column: int  # 21 entries
Tables       : schema_version: int; sizes; deviations; classes; tolerances; columns   # tuples of the row models
```
Notes for the planner:
- The two reads write the **same** models and the diff tool compares them as models after sorting each tuple by its key (`(module, reference_d, teeth)`, `letter`, `tolerance_class`, `row`, `(module_group, d_b_over_mm)`), then emits one line per differing cell: part, table, row key, column, page. `json.dumps(..., sort_keys=True, indent=1)` of the sorted dump is the "diff to zero as sorted JSON" artefact.
- Provenance strings must not be free text: fix the module-to-(clause, table pair, page) map in one checked place and put the map in the read prompts, otherwise "9" versus "section 9" becomes a spurious disagreement (A11).
- Load-time invariants (all cheap, all refuse with the row named): `T_G = T_act + T_eff` per `ToleranceRow`; micrometre fields are `int` and `abs <= 1000`; millimetre fields lie in a plausible range and `pin_d_mm < reference_d`; a raw-text scan of the file for U+2212 and U+2013 before parsing; unique keys; `column` in 1..9, `row_by_column` in 1..24, class in 5..12; **`m1_mm` agrees with `measure_over_pins(m, z, s_nominal, pin_d_mm)` within 0.0005 + 1e-9 for every size row** (721 of 721 do on the read-1 probe, 2.4 ms in all). A last-digit typo in D_M, d_B, z or M1 moves the difference to between 0.0005 and 0.0015, so it is caught except at an exact tie. `form_d_max_mm` is **not** covered by the identity; only the two reads (and the plausibility bound `0 < form_d_max_mm < tip_d`) protect it.
- Completeness (721 size rows, 16 modules, 18 letters x 9, 8 classes x 9, 24 tolerance rows, 21 column entries) is a **transcription-time** check in `make tables.check`, not a load-time one, so the synthetic fixture can stay small. The consequence the plan must own: a real file missing a letter silently reads as "fit outside Table 7" (warned, null); the completeness check is what prevents that.
- File size is about 70 KB for the size rows plus a few KB for Table 7; no compression, one `read_bytes()` with a cap.

### Anti-Patterns to Avoid
- **Reading the file in `derive_shaft`, per call, or in a request handler.** `shaft_info` runs `derive_shaft` on the event loop for every keystroke.
- **Snapping, nearest-row or interpolating** a module, d_B or z that is not listed (L08, ROADMAP boundary). Match the exact float key; user-typed `25`, `25.0` and `25,0` all parse to `25.0`.
- **Echoing the filesystem path in a warning.** Warnings go to every API client. Name the variable `SPUR_DIN5480_TABLES`, not the path; the full path belongs only in the startup refusal on the operator's stderr.
- **Taking Table 7's letters and classes from a constant in the repo.** They would be transcribed values; derive the "names Table 7's set" sentence from the loaded file.
- **A second row table in `app.js`** (forbidden by two pins) or any page edit. New rows ride `ShaftParams.model_config["json_schema_extra"]["dims"]`.
- **Putting the data file anywhere under `src/`.** `[tool.hatch.build.targets.wheel] packages = ["src/spur"]` and the Dockerfile's `COPY src ./src` [VERIFIED: pyproject.toml; Dockerfile:27] would ship it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Schema validation of the file | A dict walker with `isinstance` | pydantic models, `ConfigDict(frozen=True, extra="forbid", strict=True)`, `model_validate_json` | Strict mode rejects `"28"`, `28.0` for an `int` field and the string `"−28"` (all `int_type`), and rejects unknown keys [VERIFIED: probe this session] |
| NaN / infinity | Trusting `strict=True` | `Field(allow_inf_nan=False)` on every float | A strict `float` field accepted JSON `NaN` and `1e999` (inf) [VERIFIED: probe this session: `b=nan`, `b=inf` loaded] |
| Measure over pins at a thickness | A second involute solver | `din5480.measure_over_pins(m, z, s, pin_d)` | Takes the thickness and the pin already; reproduces M1 on 721/721 rows [VERIFIED: probe this session] |
| An independent M_Re for the anchors | Copying M1 | `tests/shaft_oracle.measure(m, z, x, pin)` | Tangency search by geometry, no shared formula (L08) |
| Table 6 limits | Re-deriving | Three one-line pure functions in `din5480.py`, each cited `DIN 5480-1:2006, Table 6` | `s_vmax = s1 + A_s`, `s_max = s1 + A_s - T_eff`, `s_min = s1 + A_s - T_G` (D-10; text layer of p. 23 confirms) |
| Decimal comma and en-dash minus | Per-call `replace` scattered in the parser | One `normalise(line)` that maps U+2013 and U+2212 to `-` and `,` to `.` and then fails loudly on anything that still does not parse | The copy prints negatives with U+2013 [VERIFIED: pdftotext output of p. 18, `–` in the deviation column] |
| Sorted-JSON diff of two reads | `diff` on hand-formatted files | `json.dumps(model_dump(mode="json"), sort_keys=True, indent=1)` after sorting row lists by their key tuple; compare as models, report cell-level | D-08 needs "table, row, column, page", which a text diff cannot give |
| Startup refusal | `sys.exit` inside the loader | Loader raises `TablesError`; each root decides (`SystemExit("error: ...")` in the CLI, propagate in `lifespan`) | The loader stays pure and testable |
| Page text extraction | OCR for Part 2 | `pdftotext -layout` | Text layer is complete: 32 pages, 721 + 721 rows |

**Key insight:** every check that makes a transcription trustworthy here is one the repo can run for free, because the numbers must satisfy formulas the repo already holds. The two reads catch typing errors; the M1 identity catches anything either of them or both got wrong in D_M, d_B, z or M1.

## Runtime State Inventory

Not a rename/refactor/migration phase. State this phase adds, for completeness:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | The private file `private/din5480-tables.json` (new, gitignored) | Create and guard (Pitfall 9) |
| Live service config | `compose.yaml` has `read_only: true` and no volume | Document a read-only bind mount plus `SPUR_DIN5480_TABLES` in README / `packaging.md`; do not bake the file into the image |
| OS-registered state | None | None |
| Secrets/env vars | `SPUR_DIN5480_TABLES` (new; a path, not a secret) | README env table, `cli.md`, `http-api.md` |
| Build artifacts | `__pycache__`, `.mypy_cache`, `.import_linter_cache` exist; no table artefact | None |

## Common Pitfalls

### Pitfall 1: The default shaft sits on a Table 7 range edge
**What goes wrong:** Table 7's reference-diameter header is a stack of "über" (over) and "bis" (up to) labels with edges at 12, 25, 50, 100, 200 and 400. The default shaft W 25x1.25x18x8f has d_B = 25, exactly on an edge, and so do many tabulated rows (every row whose d_B equals an edge, in every module). The page's own example, d_B 120, is interior and says nothing about edges. A one-column error changes A_s and the tolerance row and so changes M_Re limits and the solid, silently.
**Why it happens:** the column map is read from a drawing; the convention is not stated in the table.
**How to avoid:** the DIN convention "über x bis y" meaning x < d_B <= y is [ASSUMED] (A1; it is how DIN ISO 286 reads the same words). Make the human confirm it at the D-07 checkpoint, show the default shaft's row explicitly with both neighbouring columns' candidate values, and record the answer in L50. Encode edges in the schema as `d_b_over_mm` (exclusive) and `d_b_upto_mm` (inclusive) and test the edge on both sides. If the human cannot confirm, the honest fallback under L08 is `null` plus a warning for a d_B exactly on an edge, not a guess.
**Warning signs:** the default shaft's s_vmax equals the value of the neighbouring range; a lookup written with `<=` on both ends.

### Pitfall 2: A float that is `NaN` or `inf` loads
**What goes wrong:** a vision agent or a typo writes `NaN`/`1e999`; strict pydantic accepts it [VERIFIED]. Comparisons with NaN are False, so every `if not low <= contact <= high` guard degenerates.
**How to avoid:** `allow_inf_nan=False` on every float field; a seen-red row for it.

### Pitfall 3: Leaks through logs, listings and fixtures
**What goes wrong:** the repo commits `investigation/*.log` files (Phase 31 and 33 have dozens). A D-08 disagreement listing that prints "A reads X, B reads Y" is a transcribed value; so is a `make tables.check` dump pasted into a SUMMARY; so is a test fixture "copied from the file to make the test realistic"; so is a coarse statistic that identifies a row (Phase 31's VERIFICATION already flagged three of those as T-31-13 residue).
**How to avoid:** `scripts/din5480_tables.py diff` prints **locations only** (part, table, row key, column, page) by default and values only with an explicit flag that the plan forbids in committed output; disagreement values are shown to the human in the conversation. Test fixtures are synthetic filler plus only the approved anchors. A grep of the committed diff for the private file's values is impractical (short decimals match everywhere), so the close check is procedural: the plan's close step lists `git diff <phase-base>..HEAD --stat`, reads every added log and SUMMARY, and states that none holds a value.

### Pitfall 4: Test isolation (env, state, caches)
**What goes wrong:** (a) a developer who has `SPUR_DIN5480_TABLES` exported runs `make verify` and every "tables unset" assertion fails; (b) `din5480_tables` module state set by one test leaks into the next on the same xdist worker; (c) `model._build_cached` and `app._EXPORTS` keep a solid or bytes built under the other table state.
**How to avoid:** an autouse fixture in `tests/conftest.py` that `monkeypatch.delenv("SPUR_DIN5480_TABLES", raising=False)`, calls `din5480_tables.reset()` before and after, and clears the two caches for tests that opt in (a `with_tables` fixture). `tests/browser_session.py` already strips every `SPUR_*` variable from the server's env [VERIFIED: tests/browser_session.py:128], so the browser test is immune; a browser step that needs tables must add the variable explicitly.
**Real-file tests** read the variable at import (collection) time, before the autouse fixture deletes it, and carry `pytest.mark.skipif(not REAL, reason="SPUR_DIN5480_TABLES is not set")`. CI (`.github/workflows/ci.yml`, byte-watched by `make gear.unchanged`, so it cannot be edited) skips them; the human's host runs them.

### Pitfall 5: A replaced worker diverges from the parent
See Pattern 3. With `initargs` it cannot. With a worker-side re-read it can after an edit of the file while the server runs.

### Pitfall 6: The guard goes live, and a limit thickness can leave the window
**What goes wrong:** D-12 sets the lower bound at the tabulated d_Ff1 maximum plus 0.1*m. Measured this session over the 710 tabulated rows inside the shift range (the 11 outside are refused by `check_shaft`): at the tabulated pin and the formula thickness the contact lies inside `[d_Ff1max + 0.1*m, d_a - 0.1*m]` on **all 710**, with the worst row about 0.06*m above the lower bound and about 0.41*m below the upper one. Perturbing the thickness by -0.05*m or +0.02*m moves the contact by up to about 0.08*m [VERIFIED: probe this session; statistics of unnamed rows only]. A fit whose `T_G + |A_s|` exceeds a few hundredths of the module (any coarse class, small modules) can therefore put the **minimum** or **maximum** measurement outside the window although the nominal one is inside.
**How to avoid:** evaluate the window at each thickness that prints (nominal, s_max, s_min), null **that** M with the existing "M_Re ... not given: a pin of ... touches at a diameter of ... outside the window" sentence, and keep the others. Do not widen the margin (D-12). Run the sweep over every tabulated row x every Table 7 (letter, class) once the real file exists, record the count in `bench/RESULTS.md`, and surface it. Add a direct-call test per null branch, which the code comment in `pin_measurement` says is currently covered only by direct calls [VERIFIED: src/spur/shaft_calc.py:244-255 docstring].
**Warning signs:** `pin_measurement` called once with the nominal thickness while three numbers print.

### Pitfall 7: A thin tooth can close the tip land; a thick one can close the space
**What goes wrong:** the solid's outline is a spline up each flank, a three-point arc across the tip and an arc across the root; `flank_half_angle` shrinks as A_s goes negative. A large negative A_s on a small module (letters toward `a`) or a large positive A_s toward `v` changes tooth and space widths by tens of percent of the half pitch at m 0.5. Nothing in `build_shaft` checks that the half angle at the tip radius stays positive or that neighbouring teeth do not overlap; the guards only catch a kernel result that is invalid or off in volume.
**How to avoid:** a pure-maths sweep (half angle at `ra` > 0, tooth thickness < circular pitch) over every tabulated row x every Table 7 fit, plus building the extreme rows (thinnest tip land, thickest tooth) and reading them back. If any combination is unbuildable, that is a `BuildError`-class refusal or a warning-and-nominal decision, and it is the human's (stop-and-ask). Magnitude cannot be stated before the real file exists. [ASSUMED: A8]

### Pitfall 8: Agreement margin at the copy's M_min is thinner than it looks
Phase 31 matched M1 minimum 125.956 using the copy's printed s 6.180 (difference 0.00004). Computed from the **formula** s1 (6.27123) with A_s -28 µm and T_G 63 µm, s_min is 6.18023 and `measure_over_pins(3, 38, s_min, 6.0)` reads 125.95632, a difference of 0.00032 from the printed 125.956 [VERIFIED: ran this session with the quoted CONTEXT values]. That is inside the printed half unit (0.0005) but uses 64 % of it. Compare to the printed digit (`abs=0.0005`), never to a rounded intermediate, and do not round s before the measure. Also: printed M is `r3` of the unrounded value; the s rows print `r3` of the unrounded values, and `s_max` / `s_min` / `s_vmax` must each be rounded once, from the unrounded sum.

### Pitfall 9: Ways the private file reaches git, an image or a wheel
- `.gitignore` has no entry for it today [VERIFIED: .gitignore read] and `git check-ignore -v private/x.json` returns 1 (not ignored) [VERIFIED: ran this session]. Add `/private/` first, commit that alone, then create any file there.
- `.dockerignore` lists `.git`, `tests`, `docs`, `web` and others but **not** a `private` directory [VERIFIED: .dockerignore read]; the Dockerfile only `COPY`s `requirements.txt`, `pyproject.toml README.md`, `src` and `docker`, so the file would not be copied today, but the build context would still be sent to the daemon. Add `private` to `.dockerignore` as a second belt.
- `git ls-files | grep -i table` already matches `src/spur/din5480_tables.py` and a Phase 33 token table [VERIFIED: ran this session], so the ROADMAP close check "`git ls-files` holds no table file" must be a precise test, not a name grep: `git ls-files private/` is empty, `git check-ignore private/din5480-tables.json` succeeds, and no tracked `*.json` validates as a `Tables` document (a test that loads each tracked JSON with `Tables.model_validate_json` and expects `ValidationError` is cheap and catches a renamed copy).
- Never under `src/`, `tests/` or `docs/`.

### Pitfall 10: The parser's known quirks (all measured this session)
- 32 licence-stamp lines (one per table page), each on its own line, never fused to a row [VERIFIED: parse of pages 8-39].
- Footnote marks after the tooth count in the nominal tables and after k in the inspection tables, glued (`8a`) or spaced (`12 a`); **two letters occur, `a` and `b`** (the `b` appears once, on an m = 8 inspection row, `13b`). Phase 31's note says only "a"; a parser that strips only `a` reads 720 inspection rows and misses that one [VERIFIED: my first run read 720, the fixed regex 721].
- Decimal commas in every number; U+2013 as the minus sign; U+22C5 (`⋅`) in headers.
- Table 12 prints one row twice under d_B 20 where Table 13 has d_B 19 (same z). The nominal table therefore has one duplicate `(module, d_B, z)` key and the inspection table has the row the nominal table lacks. Read 1 must not guess: report it, and let the human settle it (D-08). The row belongs under d_B 19 (the inspection table and the formulas agree), but that is the human's call from the page.
- Row shape: 14 numeric tokens in a nominal row, 10 in an inspection row, once marks and stamp lines are removed. The module header lines (`Module m = ... mm`, 6 tokens) look numeric-ish and must be excluded by shape (they were the only other "odd" lines).
- D_M prints with varying precision (`1,0`, `2,75`, `18`); read it as a decimal, never assume two places.
- The inspection table has **two** D_M columns (hub, then shaft); the shaft block is the second.

### Pitfall 11: Existing tests assert exact warning tuples and key lists
`tests/test_shaft_calc.py` asserts `d.warnings == (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN, DEFAULT_HOBBED_ROOT_WARNING, MEASURE_AT_NOMINAL_THICKNESS, ROOT_FORM_CONSTRUCTION, ...)` at lines 74 and 109, and `list(ShaftDimensions.model_fields) == [...13 keys...]` at line 92 [VERIFIED: tests/test_shaft_calc.py]. Any new warning on the no-file path changes those tuples, and `tests/shaft_parity.py`'s `NULLS` set in `tests/test_shaft_parity.py` gains the five keys for every shaft. Budget these edits; they are expected, not regressions. `test_the_rows_are_every_dimension_but_the_warnings_in_order_with_their_own_units` (test_shaft_interfaces.py:94) fails until the five `dims` entries carry the same `key` and `unit` as the five new fields.

### Pitfall 12: Browser parity row counts do not move without a file
The browser parity step prints "4 shafts, 42 rows" [VERIFIED: bench/RESULTS.md:7445]. A null row is not printed (`app.js:444-459`), the browser test's server runs with every `SPUR_*` variable stripped, so with no tables the count stays 42 and the new rows are invisible there. Criterion 3 ("the parity test stays green and covers them") therefore needs a parity run **with tables loaded**: API against CLI in-process with the fixture file (light), and one browser step whose server gets `SPUR_DIN5480_TABLES` pointing at a synthetic fixture file (heavy file, `tests/test_browser.py`, plus an env hook in `tests/browser_session.py`). Parity compares equality, not truth, so synthetic filler is fine there; the anchors carry truth.

## Code Examples

Verified patterns from this repo and this session (no standard value appears).

### Table 6 as three pure functions (formulas from CONTEXT D-10 and the text layer of p. 23)
```python
# din5480.py, next to tooth_thickness. A_s, T_G, T_eff arrive in micrometres from Table 7.
def thickness_limits(s1: float, a_s_um: int, t_g_um: int, t_eff_um: int) -> tuple[float, float, float]:
    """(s_vmax, s_max, s_min) in mm. DIN 5480-1:2006, Table 6."""
    s_vmax = s1 + a_s_um / 1000
    return s_vmax, s_vmax - t_eff_um / 1000, s_vmax - t_g_um / 1000
```

### The M_Re limits, each through the guard
```python
# shaft_calc.py sketch. pin_measurement grows `s` and `floor`; today it takes (p, pin_d)
# and derives s itself (shaft_calc.py:244-260).
m_max = pin_measurement(p, pin_d, s=s_max, floor=row.form_d_max_mm + margin)
m_min = pin_measurement(p, pin_d, s=s_min, floor=row.form_d_max_mm + margin)
```

### A structural invariant, seen red once (shape of the three D-04 reds)
```python
# tests/test_din5480_tables.py. `broken` edits one row of the synthetic builder's output.
@pytest.mark.parametrize(("what", "edit", "needle"), [
    ("T_G != T_act + T_eff", lambda d: d["tolerances"][0].update(t_g_um=d["tolerances"][0]["t_g_um"] + 1), "T_G"),
    ("a micrometre value in a millimetre field", lambda d: d["sizes"][0].update(pin_d_mm=1000 * d["sizes"][0]["pin_d_mm"]), "pin_d_mm"),
    ("Unicode minus in the text", None, "U+2212"),   # replace '-' in one number by − in the raw text
    ("NaN", None, "nan"),
])
def test_a_broken_row_refuses_to_load(...): ...
```

### Lifespan and CLI edits (the whole of the composition-root change)
```python
# app.py lifespan, before BuildPool:     tables = din5480_tables.active()    # TablesError propagates
#                                         app.state.pool = BuildPool(..., tables=tables)
# cli.py, top of cmd_serve / cmd_shaft_info / cmd_shaft_export:
#     try: din5480_tables.active()
#     except din5480_tables.TablesError as exc: raise SystemExit(f"error: {exc}") from None
```

### Read 1 of Part 2, the shape that read 721 + 721 rows (scratch, `read1_probe.py`; code only, no values)
```python
NUM = re.compile(r"^-?\d+(\.\d+)?$")
def toks(line: str) -> list[str]:
    line = line.replace("–", "-").replace("−", "-").replace(",", ".")
    line = re.sub(r"(?<=\d)\s*[ab]\b", " ", line)         # footnote marks a and b, glued or spaced
    return line.split()
# a nominal row is 14 numeric tokens, an inspection row 10; the stamp line and the module
# header never match that shape. The title line ("Table N - Nominal|Inspection dimensions,
# m = ... mm") decides which of the two a page is; pages 8..39 alternate.
```

## Table structure (record of what was inspected; no values)

**DIN 5480-2:2006-05 (40 pages, text layer, RC4 "encrypted" with copy and print allowed).** Pages 8 to 39 hold Tables 2 to 33, one table per page, a nominal-dimensions table then an inspection-dimensions table for each of **16 modules** (0.5, 0.6, 0.75, 0.8, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 6, 8, 10), under section headings numbered 4 to 19 (module m = 0.5 is section 4, m = 10 is section 19; seen on pages 8, 18, 20, 22 and 38). Printed page = PDF page. 721 rows in each kind; reference diameters are integers 6 to 500, tooth counts integers 6 to 82. Only these columns are needed:
- Nominal table (14 columns): d_B, z, d, d_b, x1*m, e2 = s1, df2, Adf2, dFf2 min, da2, da1, **dFf1 max**, df1, Adf1. Needed: d_B, z, dFf1 max.
- Inspection table (10 columns): d_B, z, then hub D_M, M2, A*M2, then shaft **D_M**, **M1**, A*M1, then k, Wk. Needed: d_B, z, shaft D_M, M1 (identity check only). Not needed (deferred or D-10): hub block, A*M1, k, Wk.
- Table 1 (p. 7) holds root fillet radii and deviation factors: not needed.

**DIN 5480-1:2006-03 (27 pages).** Table 6 (p. 23, clause heading not captured) and Table 9 (p. 25, "Types of fit") have text layers. Table 7 (p. 24, under heading "10.9 Deviations and tolerances") has 47 words of text and **19 images** (3689x271 px each, 600 ppi): one page-wide bitmap in strips. Blocks, top to bottom:
1. A skewed grid: 3 module-group rows (labelled 0.5 to 1.5, 1.75 to 4, 5 to 10) by 7 reference-diameter columns (header "über"/"bis", edges 12, 25, 50, 100, 200, 400), whose intersections project onto **9** vertical lines (7 + 3 - 1 = 9, consistent with the 9 value columns below).
2. The deviation block: shaft letters a b c d e f g h j k m n p r s t u v (18 rows; the hub letters F G H J K M sit in a left margin and are out of scope) by 9 columns of A_s in µm. Row `h` is a single merged cell reading 0 across all nine columns, so a reader must expand it. Negative entries carry a printed minus. Letters a to g read negative and j to v positive on the rendered page [CITED: rendered p. 24, viewed this session], which gives a sign invariant.
3. The tolerance-class map: class labels 5 to 12 (8 classes) on the left, diagonals up and right to the 9 vertical lines, ending on a row of the table at the right. Shaft and hub have separate diagonals; the worked example marks both.
4. A table of **24 rows** of T_G, T_act, T_eff (µm), and beside it a second table of guide values (f_p, F_p, F_alpha, F_beta) that is **out of scope** (CONTEXT).
5. The worked example box (W 120x3x38x8f shaft and N 120x3x38x9H hub), already quoted in CONTEXT.
The print quirk: some digits in the T_eff column are drawn with a stray slash that makes a "4" look like "1/4" at screen resolution; a vision reader must work from a 600 ppi render and be told so.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Theoretical pin rounded to 0.01 mm (L47 D-10) | The copy's tabulated shaft D_M for a listed size | This phase (D-09) | `pin_d` and `measure_over_pins` change for tabulated sizes only; L05 does not apply (output numbers) |
| Guard lower bound = internal form-diameter construction | d_Ff1 max + 0.1*m on a tabulated row | This phase (D-12) | Resolves the form-diameter debt item; the construction exceeds the printed maximum on 483 of 719 rows at h_fP 0.55 [CITED: the debt item] |
| One nominal-thickness solid | s_vmax solid when tables and fit are present | This phase (D-13) | Same link, different part per process: the info response's new row and the nominal-thickness warning are how a user tells |
| `FIT_PATTERN` shape only | Shape plus Table 7 membership as a warning | This phase (D-14) | The 422 contract is unchanged |

**Deprecated/outdated:** `MEASURE_AT_NOMINAL_THICKNESS` where limits print (D-10); `ODD_Z_UNCONFIRMED` for a tabulated odd count (D-11); the `fit` field description sentence "Whether the fit exists in the tables is not checked yet." (shaft_params.py) and the code comments that say "Phase 34 removes it".

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | "über x bis y" means x < d_B <= y (the DIN ISO 286 reading) | Pitfall 1 | The default shaft and every row whose d_B equals an edge use the wrong column; all five new rows and the solid are wrong for them with no error |
| A2 | The tolerance-class map is affine in (class, column): parallel diagonals over equally spaced verticals, so `row(q, k) = r0 + c*(q-5) + s*(k-1)` with integer c and s. Seen on the render; the shaft and hub rows of the page's own example sit three rows apart in the 24-row list, which fits one class step of three rows | Table structure | If true, 72 transcribed numbers collapse to three and become a strong check; if false, the plan loses nothing but the check. Verify against the file after the reads before adopting |
| A3 | The A_s rows are monotone across the 9 columns (magnitude non-increasing left to right) and letters a-g <= 0, h = 0, j-v >= 0 | Table structure | Same: an optional transcription-time check, a hard loader check only for the sign rule if the human confirms |
| A4 | uvicorn with `workers > 1` stops the parent when a child fails its lifespan | Pattern 2 | The pre-check in `cmd_serve` makes this moot for `spur serve`; a bare `uvicorn spur.app:app --workers 2` may restart-loop |
| A5 | A broken shaft table file does not stop `spur info` / `spur export` (gear commands) | Pattern 2 | A reviewer reading "the CLI refuses" literally may want every command to refuse |
| A6 | Size listed + fit outside Table 7 still prints the tabulated pin and nominal M (tier 3) | Pattern 4 | If the human wants every table-dependent number null for a bad fit, the pin stays theoretical there |
| A7 | The private file's home is repo-local `private/` | Standard Stack | Any other home changes only the `.gitignore`/`.dockerignore` entries and the guard test |
| A8 | Table 7 fits will not make a tooth unbuildable (closed tip land, overlapping teeth) | Pitfall 7 | A fit/size combination throws `BuildError` or builds a wrong tooth; needs the sweep and a human decision |
| A9 | Exit status 1 with `error: <reason>` for a bad file (the `BuildError` convention), not 2 | Pattern 2 | Cosmetic; `cli.md` "Errors" must say so |
| A10 | Table 7 is only ever looked up for one of the 16 tabulated modules, so the module-to-group map needs those 16 only and the group edges (1.5/1.75, 4/5) never matter | Pattern 4 | A future "size need not be tabulated" decision would reopen the group-edge question |
| A11 | Clause strings for Part 2 rows are the module section number (4 to 19) and the table pair, e.g. "9" and "12 and 13" | Schema | Provenance strings differ between reads; fix them in the read prompts and in a checked map |

## Open Questions

1. **The reference-diameter edge convention (A1).**
   - What we know: the header says über/bis; the default shaft is on an edge; the example is interior.
   - What's unclear: whether the copy states the convention anywhere (clause text) and which way it goes.
   - Recommendation: a D-07 checkpoint item, shown with the default shaft's row. Without an answer, null-and-warn at an edge (L08).
2. **Where does the guard-at-limit sweep stop the phase?**
   - What we know: nominal fires on 0 of 710; limit thicknesses can move contact by up to about 0.08*m per 0.05*m.
   - What's unclear: how many (row, fit) pairs fire.
   - Recommendation: write the sweep as a plan task after the real file exists; record the count; the human decides if it is more than a handful (CLAUDE.md stop-and-ask: "evidence conflicts" / "a choice trades stability for speed").
3. **Tip-land and overlap sweep (A8)** as above.
4. **Is `private/` the home (A7), and does the human want a `make tables.check` target?** Recommended yes to both; neither is in CONTEXT.
5. **Does the human want a read-back print of the stored table in the standard's layout for proofreading?** PITFALLS.md suggests it; CONTEXT does not ask. Cheap to add to `tables.check --layout`; not required.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 venv | everything | ✓ | 3.12.15 | — |
| poppler `pdftotext`, `pdftoppm`, `pdfimages` | read 1, page renders | ✓ | 26.10.0 | none needed; developer-time only, not in CI or the image |
| The two PDFs | both reads | ✓ | din-5480-1.pdf 518,733 bytes (27 pp), din-5480-2.pdf 1,053,112 bytes (40 pp) | — |
| Vision-capable agent runs (Task/Agent tool) | reads 2 and the two Table 7 reads | not probed here (executor capability) | — | the human re-keys a day later (PITFALLS.md alternative) |
| Docker | `make check`, `make test-image` | ✓ | 29.8.2 | `make verify` needs none |
| Playwright headless shell | browser test | ✓ | chromium_headless_shell-1243 in `.venv/ms-playwright` | — |
| Idle host for gate readings | REQ-gate-cost-recorded | ✗ at research time (1-minute load 12.45 of 18 CPUs) | — | Record the load beside every reading, as 33-01 and 33-09 do |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** vision agents (probe at plan start; the human's blind re-key is the alternative).

## Validation Architecture

Nyquist validation is enabled (`.planning/config.json` has no `workflow.nyquist_validation` key, so it is treated as enabled) [VERIFIED: .planning/config.json read].

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 with pytest-xdist, pytest-cov [VERIFIED: import] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`filterwarnings = ["error", ...]`, `--strict-markers`) |
| Quick run command | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_din5480_tables.py tests/test_din5480_read1.py tests/test_shaft_calc.py tests/test_shaft_parity.py` |
| Full suite command | `make verify` (ruff, mypy `--strict`, import-linter, no-fake-done, `gear.unchanged`, pytest `-n 8` with `fail_under = 96`) |
| Commit-time slice | `make verify.fast` (every file but the six heavy ones, under 30 s, L36); new loader/maths tests must stay in it, kernel builds go in `tests/test_shaft_model.py` / `tests/test_pool.py` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-tables-private-file | env unset: five rows null + warning naming `SPUR_DIN5480_TABLES`, part builds | unit | `pytest --no-cov -n0 tests/test_shaft_calc.py -k tables` | ❌ Wave 0 (extend) |
| REQ-tables-private-file | set but missing / unreadable / invalid JSON / failing invariant: `TablesError`, CLI exit 1 `error: ...`, lifespan raises, real `spur serve` exits non-zero without listening | unit + cli + app + subprocess | `pytest --no-cov -n0 tests/test_din5480_tables.py tests/test_cli.py -k tables` ; `tests/test_pool.py -k tables` for the lifespan | ❌ Wave 0 |
| REQ-tables-private-file | `private/` is ignored by git and listed in `.dockerignore`; nothing tracked under it; no tracked JSON validates as `Tables` | unit (git) | `pytest --no-cov -n0 tests/test_din5480_tables.py -k ignored` | ❌ Wave 0 |
| REQ-tables-private-file | the warning never carries the file path | unit | `-k warning_has_no_path` | ❌ Wave 0 |
| REQ-tables-transcribed-twice | each of T_G != T_act + T_eff, unit-slip, U+2212, NaN, duplicate key, bad provenance refuses to load, seen red once | unit | `pytest --no-cov -n0 tests/test_din5480_tables.py -k broken` | ❌ Wave 0 |
| REQ-tables-transcribed-twice | the load-time M1 identity refuses a row with a wrong D_M, d_B, z or M1 | unit | `-k m1_identity` | ❌ Wave 0 |
| REQ-tables-transcribed-twice | the two reads diff to zero; `diff` reports locations only; the d_B 19/20 row is reported, not guessed | unit + procedural | `pytest --no-cov -n0 tests/test_din5480_tables.py -k diff` ; `make tables.diff A=... B=...` on the real reads (checkpoint) | ❌ Wave 0 |
| REQ-tables-transcribed-twice | read-1 parser: commas, en dash, marks a and b, stamp lines, duplicate row, header lines excluded | unit | `pytest --no-cov -n0 tests/test_din5480_read1.py` | ❌ Wave 0 |
| REQ-fit-tolerance-window | page example W 120x3x38x8f: s_vmax 6.243, s_max 6.220, s_min 6.180 from synthetic table + approved anchor | unit | `pytest --no-cov -n0 tests/test_shaft_calc.py -k window` | ❌ Wave 0 |
| REQ-fit-tolerance-window | fit outside Table 7 (`3z`, class 13, letter q): warning naming the file's letters and classes, five rows null, 200 not 422 | unit + api | `-k fit_outside` | ❌ Wave 0 |
| REQ-fit-tolerance-window | range-edge convention at both sides of an edge (A1) | unit | `-k edge` | ❌ Wave 0 |
| REQ-mre-limits | computed M_Re at the tabulated pin equals the printed M1 within 0.0005 on every approved anchor and the oracle at 1e-9 | unit | `pytest --no-cov -n0 tests/test_din5480_anchors.py tests/test_shaft_calc.py -k m1` | ✅ partly (`test_anchor_part_2_measure_over_pins_at_the_tabulated_pin`) |
| REQ-mre-limits | M_Re max/min vs `shaft_oracle.measure` at `x_eff` for the thickness; page example M min ties to 125.956 within 0.0005 | unit | `-k limits` | ❌ Wave 0 |
| REQ-mre-limits | odd z prints at the tabulated pin (W 26x1.25x19, W 30x2x13); off-table odd stays null with `ODD_Z_UNCONFIRMED` | unit | `-k odd` | ❌ Wave 0 (rewrites `test_an_odd_tooth_count_prints_the_pin_and_no_measure_over_pins`) |
| REQ-mre-limits | guard: bound <= d_Ff1 max on approved rows; each null branch hit by a direct call at a limit thickness | unit | `-k guard` | ❌ Wave 0 |
| REQ-solid-max-material | with tables the solid's thickness, read from a z-section, equals the printed s_vmax within the flank bar; without, the nominal | kernel | `pytest --no-cov -n0 tests/test_shaft_model.py -k thickness` | ❌ Wave 0 (heavy file) |
| REQ-solid-max-material | a pool worker builds the tabulated solid (initargs) and a replaced worker still does | kernel + pool | `pytest --no-cov -n0 tests/test_pool.py -k tables` | ❌ Wave 0 (heavy file) |
| REQ-solid-max-material | caches cannot serve the other state: `_build_cached` / `_EXPORTS` cleared by the fixture; download name unchanged | unit | `-k cache` | ❌ Wave 0 |
| REQ-off-table-builds | listed-size neighbours (d_B +0.001, z +1, module +0.05) build from formulas, five rows null and warned, numbers identical to today's | unit | `pytest --no-cov -n0 tests/test_shaft_calc.py -k off_table` | ❌ Wave 0 |
| REQ-fit-tolerance-window / criterion 3 | API = CLI = page over the fixed shafts with tables loaded; new keys in `dims`; browser step with a synthetic file | unit + browser | `pytest --no-cov -n0 tests/test_shaft_parity.py tests/test_shaft_interfaces.py` ; `tests/test_browser.py` | ✅ extend |
| (real file) | every approved anchor, all 721 M1 identities, the guard sweep and the tip-land sweep on the real file | real-file, skipped in CI | `SPUR_DIN5480_TABLES=private/din5480-tables.json pytest --no-cov -n0 tests/test_din5480_real_tables.py` | ❌ Wave 0 |
| REQ-gate-cost-recorded | baseline reading at phase start and close reading, same host, in `bench/RESULTS.md` under `### The gate delta (34-NN)`; `make gear.unchanged` green; close checks | procedural | `/usr/bin/time -p make verify` ; `make gear.unchanged` ; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` | n/a |

### Sampling Rate
- **Per task commit:** `make verify.fast` (runs in the pre-commit hook).
- **Per wave merge:** `make verify`, one run at a recorded load (the phase's readings are appended to `bench/RESULTS.md`).
- **Phase gate:** `make verify` green, plus `make gear.unchanged`, `make lint-imports` (10 contracts kept), the real-file test module green on the human's host, and the procedural close checks below.

### Wave 0 Gaps
- [ ] `tests/din5480_tables_fixture.py`: the synthetic builder (invented filler + the approved anchors only).
- [ ] `tests/test_din5480_tables.py`, `tests/test_din5480_read1.py`, `tests/test_din5480_real_tables.py`.
- [ ] `tests/conftest.py` autouse isolation (env var, module state) and the `with_tables` fixture (clears `_build_cached`, replaces `_EXPORTS`).
- [ ] `scripts/din5480_read1.py`, `scripts/din5480_tables.py` and `make tables.check` / `make tables.diff` (and the `.PHONY` and help lines; `make` lists targets by `##` comments).
- [ ] `.gitignore` `/private/`, `.dockerignore` `private`, in a commit of their own before any file exists there.
- [ ] Updates to the exact-tuple and key-list assertions named in Pitfall 11.
- [ ] A browser-session hook to pass `SPUR_DIN5480_TABLES` to the server for one step.

### Procedural close checks (extend Phase 33's twelve)
1. `git ls-files private/` empty and `git check-ignore private/din5480-tables.json` succeeds (not a name grep; Pitfall 9).
2. `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty (ROADMAP).
3. `git diff <phase-base> -- requirements.txt` empty.
4. Every added or changed file in the phase's diff read for a table value (logs and SUMMARYs included).
5. The seen-red table in `bench/RESULTS.md` has one row per invariant, per anchor and per guard.
6. The Phase 30 check (`make gear.unchanged`) green at the milestone close.
7. Three debt/idea items moved in the same commits as their fixes: `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`, `docs/tech_debt/active/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md` (`git mv` to `resolved/`, `Status: resolved`, sha, INDEX row moved) and `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md` (to `retired/`, `Status: retired`, `Retired in:`) [VERIFIED: the three files read; INDEX rows read].
8. `L50` appended to `docs/architecture/decision_log.md` (the next free id; the last heading is L49) [VERIFIED: grep of `## L` headings].

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is enabled. This is a local operator-supplied file read, not user input, but three surfaces matter.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | The app has none by design (`docs/tech_debt/active/2026-09-21-no-authentication.md`) |
| V3 Session Management | no | — |
| V4 Access Control | no | The table file is operator-owned; set permissions `0600` as advice in the README |
| V5 Input Validation | yes | pydantic strict models with `extra="forbid"`, `allow_inf_nan=False`, a size cap on the read (a few MB is generous for a ~300 KB document), the raw-text scan for U+2212/U+2013 before parsing |
| V6 Cryptography | no | No secret; a SHA-256 of the file may be logged for traceability, never needed for security |
| V7 Error handling / logging | yes | Startup refusal names the path (operator's stderr); **warnings sent to API clients name the variable, not the path**; the loader imports no logger |
| V8 Data protection | yes | Third-party licensed data: never in git, the image, the wheel or committed logs (Pitfalls 3 and 9). Table-derived **outputs** (s_vmax, M_Re limits, D_M as `pin_d`) are served to whoever can reach the API; README already says localhost only |
| V12 File handling | yes | `Path(os.environ[...])` read as a regular file; a directory or special file is a `TablesError`; no path built from user input anywhere (the user cannot influence the path) |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A silently wrong number from a mistranscribed cell | Tampering (of data at rest) | Two reads, load-time invariants, the M1 identity, anchors seen red (L08) |
| A broken file degrading quietly to `null` | Repudiation / silent partial success | Refuse to start (D-04) |
| Licensed data reaching the public repo or an image | Information disclosure | `.gitignore`, `.dockerignore`, location-only logs, a precise tracked-file test |
| Filesystem path in an API warning | Information disclosure | Name the variable only; test that no warning contains the path |
| Oversized or hostile JSON | Denial of service | Read cap, strict models; the file is operator-controlled so this is hygiene |
| NaN/inf in a float | Tampering | `allow_inf_nan=False` |

## Sources

### Primary (HIGH confidence)
- This repo, read this session: `src/spur/{app,cli,pool,records,model,shaft_calc,shaft_model,shaft_params,din5480,din5480_tables,parts,__init__}.py`; `pyproject.toml` (all ten import contracts); `Makefile`; `.gitignore`, `.dockerignore`, `Dockerfile`, `compose.yaml`; `tests/{conftest,shaft_parity,test_shaft_parity,test_shaft_interfaces,test_din5480_anchors,shaft_oracle,test_shaft_model,test_seam,browser_session}.py` and parts of `test_shaft_calc.py`, `test_cli.py`, `test_browser.py`; `docs/architecture/decision_log.md` L43 and L47 to L49; `bench/RESULTS.md` Phase 30 to 33 gate sections; `.planning/{ROADMAP,REQUIREMENTS,STATE,config.json}`; Phase 31 `31-05-SUMMARY.md`, `31-REVIEW-FIX.md`; the three debt/idea items; `docs/CODING_VALUES.md`; `.planning/research/PITFALLS.md` Pitfall 3.
- Commands run: `make gear.unchanged` (green), `make lint-imports` (10 kept), `pytest --collect-only` (2783 tests), the pydantic strict probe, the uvicorn lifespan probe, `git check-ignore`, `git ls-files | grep`.
- The two PDFs, inspected for structure only: `pdftotext -layout` of Part 1 pp. 23-25 and Part 2 pp. 7-39, `pdfimages -list` and a 130 dpi render of Part 1 p. 24.
- The read-1 feasibility probe and the M1 identity and guard-margin probes (scratchpad: `read1_probe.py`, `margin_probe.py`).

### Secondary (MEDIUM confidence)
- The über/bis reading as DIN ISO 286's convention (training knowledge; A1).

### Tertiary (LOW confidence)
- The affine and monotone structure of Table 7 (A2, A3), from one viewed render and the page's own example.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, no new dependency, all versions read from `requirements.txt`.
- Architecture: HIGH for loader, refusal, pool and caches (read and probed); MEDIUM for the tier-3 reading and the exit code (A5, A6, A9).
- Transcription mechanics: HIGH for Part 2 (721/721 rows and the M1 identity run); MEDIUM for Table 7 (image, nomogram semantics, edge convention A1).
- Pitfalls: HIGH for the repo-specific ones (each traced to a file or a run); MEDIUM for the guard and tip-land sweeps (their size is unknown until the real file exists).

**Research date:** 2026-10-30
**Valid until:** 2026-11-29 (stable codebase; re-check the `src/spur/*.py` line references if any of the five edited modules moves before planning ends)
