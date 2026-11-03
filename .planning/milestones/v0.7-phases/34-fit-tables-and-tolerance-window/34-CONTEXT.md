# Phase 34: Fit Tables and Tolerance Window - Context

**Gathered:** 2026-10-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 34 adds the fit-dependent numbers. They come from a private table file transcribed from the
human's DIN 5480 (2006) copy:
- the tooth-thickness limits at the chosen fit;
- M_Re maximum and minimum, measured at the standard's pin;
- a solid at the maximum-material tooth thickness.

When the file is absent, or when the size or fit is not in the tables, the part builds from the
formulas. Every table-dependent number is then `null`, with a warning that says why. The milestone
releases when this phase closes.

Out of scope:
- the shift-range exceptions;
- the hub (internal spline);
- span measurement W_k (k/Wk in Part 2's inspection tables);
- the Table 7 individual deviations f_p, F_p, F_α and F_β (guide values, not tolerances);
- a manufacturing-process field.

</domain>

<decisions>
## Implementation Decisions

### The copy and the private file
- **D-01:** The copy is on the human's machine:
  - `~/Downloads/ISO standards/din-5480-1.pdf` is DIN 5480-1:2006-03, the unofficial English
    translation (27 pages), the same copy as Phase 31.
  - `~/Downloads/ISO standards/din-5480-2.pdf` is DIN 5480-2:2006-05 (40 pages), the same copy.

  Nothing from the copy is committed, except the anchors the human approves by name (D-07). The
  PDFs carry a licence stamp naming a third party, so no clause text, table or page image enters
  the repo.
  - The scratch renders and extractions go in the session scratchpad, not the repo.
  - **Reversibility:** one-way. A committed value is public history.
- **D-02:** One environment variable, `SPUR_DIN5480_TABLES`, names the file. There is no config
  file and no default path. The API server, every worker and the CLI read the same variable.
- **D-03:** The file is one JSON document, validated at the loader boundary by a pydantic model.
  - Every row carries its provenance: part, clause and table (REQ-tables-transcribed-twice).
  - The two reads produce documents in the same schema, so they diff to zero as sorted JSON.
- **D-04:** When the file is unset, missing or broken:
  - Unset: table numbers are `null`, with a warning naming the missing file (REQ-tables-private-file).
    The part still builds.
  - Set, but missing, unreadable or failing a structural check: the server and the CLI refuse to
    start and exit with the reason. A file someone meant to load that degrades quietly to `null`
    would be a silent partial success.
  - The structural checks: `T_G = T_act + T_eff`, the µm-against-mm range, and no Unicode minus.
    The check must be seen failing once against a deliberately broken row.
  - **Reversibility:** reversible. This is startup policy, not a wire contract.

### The two independent reads
- **D-05:** Part 1 Table 7 has no text layer. It is an image of a nomogram:
  - the deviation series a to v (shaft) across the d_B ranges and the module groups 0.5 to 1.5,
    1.75 to 4 and 5 to 10;
  - 24 rows of T_G, T_act and T_eff;
  - diagonal lines from the tolerance class (5 to 12) through the module group and d_B to a
    tolerance row.

  It is read twice, by two blind vision reads: two separate agents each read the rendered page
  alone and write JSON in the D-03 schema. Neither sees the other's output, and the files are then
  diffed.
  - The page's own worked example, W 120x3x38x8f, must come out of the result:
    - s_vmax 6.243, s_max 6.220 and s_min 6.180;
    - T_G 63 µm, T_act 40 µm, T_eff 23 µm and A_s −28 µm.
  - That example ties to Phase 31's approved anchor `M1` minimum 125.956 at s 6.180.
  - Table 6, the formulas for the limits, has a text layer. Table 9, the types of fit, also has a
    text layer.
- **D-06:** Part 2 is read twice by two different methods. They fail in different ways.
  - Read 1 is a `pdftotext -layout` parser, like Phase 31's scratch parser (720 nominal and 721
    inspection rows).
  - Read 2 is an agent reading the rendered pages.
  - The copy prints decimal commas, a duplicated Table 12 row (d_B 20 where Table 13 has 19), and
    licence-stamp lines in the body text. The parser handles each of these on purpose.
- **D-07:** The anchors are chosen at a human checkpoint, as in Phase 31 D-06.
  - The plan stops and shows the candidate rows. At least: the page's W 120x3x38x8f example, the
    default shaft W 25x1.25x18x8f, and one odd tooth count.
  - The human approves each by name.
  - Only the approved values are committed, as tests, each seen red once.
- **D-08:** When the two reads disagree, the human settles it from the page.
  - The plan lists each disagreement with its table, row, column and page.
  - Nothing loads, and no number prints, until the diff is zero.

### The pin and the M_Re limits
- **D-09:** For a size in the tables:
  - D_Re is the tabulated D_M.
  - M_Re is computed for that pin, by the existing `din5480.measure_over_pins`. It is not copied
    from M1.
  - A test over the anchor rows checks the computed M against the table's M1.
  - This replaces the theoretical pin and changes an output number only, so L05 does not apply
    (31 D-10).
  - When the switch happens, the warning says so. `THEORETICAL_PIN` stays in force off the table.
- **D-10:** M_Re maximum and minimum are computed by the formula at the actual thickness limits of
  Table 6, with the tabulated pin:
  - s_max = s1 + A_s − T_eff;
  - s_min = s1 + A_s − T_G.

  This is how Phase 31 matched the copy's M1 minimum, 125.956 (difference 0.00004). Part 2's
  deviation factor A*M1 is not used, so it is not transcribed.
  - `MEASURE_AT_NOMINAL_THICKNESS` is retired wherever the limits print (31-03 handoff).
- **D-11:** An odd tooth count prints M_Re and its limits at the tabulated pin, for a size in the
  tables (211 of 211 odd Part 2 rows agree).
  - Off the table, or with no file, an odd tooth count stays `null` with `ODD_Z_UNCONFIRMED`, as
    today.
  - This resolves the idea item `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md`.
- **D-12:** For a tabulated size, the pin-contact guard's lower bound is the copy's d_Ff1 maximum
  plus the margin. The real form circle lies at or below that maximum, so contact above it is safe.
  - Off the table, the theoretical pin stays. That guard cannot fire (31 D-20), and the internal
    construction stays internal.
  - This resolves
    `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`.
  - Its test: over the approved rows, the bound is at or below the maximum.
  - The guard goes live with the tabulated pin. If it fires on a tabulated row, that is a finding
    to surface, not something to widen silently.

### The solid and the fit rules
- **D-13:** With the tables loaded and the fit in the tables, the solid carries the maximum
  effective tooth thickness s_vmax = s1 + A_s (REQ-solid-max-material), read back from the solid.
  Otherwise it carries the nominal thickness, with a warning that says so.
  - A user can tell the two apart in two ways: a row with the thickness the solid carries, and the
    nominal-thickness warning.
  - The download name stays as L49 froze it.
  - The tables load once at startup and stay fixed for the process, so the solid cache, keyed by
    the parameters, stays correct.
  - **Reversibility:** costly. The new row's key and place become part of the info response's
    rows once released.
- **D-14:** A fit outside Table 7 (e.g. `3z`) gives a warning and `null`, as the roadmap says. It
  is not a `422`.
  - The part builds at nominal.
  - The warning names Table 7's deviation letters and tolerance classes.
  - `FIT_PATTERN` is unchanged, so no link that validates today starts failing.
  - This resolves `docs/tech_debt/active/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md`
    through the warning.
- **D-15:** The user sees five new limit rows:
  - s_vmax (maximum effective);
  - s_max and s_min (actual);
  - M_Re maximum and minimum.

  - A_s, T_G, T_act and T_eff are not printed.
  - The existing nominal `measure_over_pins` row stays.
  - The new rows ride Phase 33's list of rows carried on the schema, and the parity test covers
    them (ROADMAP criterion 3).
  - **Reversibility:** costly. Each row key becomes a wire key in the info response and the CLI
    output.

### Claude's Discretion
- The JSON schema's shape. D-03 fixes JSON, pydantic and per-row provenance; the planner designs
  the rest.
- Where the loader lives, and how the tables reach `derive_shaft`. The shaft maths must stay free
  of the logger and the kernel (import contracts), and must do no file I/O on every keystroke.
- The row keys, labels and order, within D-15.
- The wording of the warnings, following the existing sentence style in `shaft_calc.py`.
- How the two reads' agents are prompted, within D-05 and D-06 (blind, one schema, no shared
  output).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The copy (local, private, never committed)
- `~/Downloads/ISO standards/din-5480-1.pdf`:
  - Table 6 (p. 23, the limit formulas);
  - Table 7 (p. 24, the nomogram, image only);
  - Table 9 (p. 25, the types of fit);
  - Tables 3 and 4 (the basic rack, the minimum form clearance).
- `~/Downloads/ISO standards/din-5480-2.pdf`:
  - Table 1 (root fillet radii and deviation factors);
  - Tables 2 to 33 (nominal and inspection dimensions, m 0.5 to 10).

### Scope and requirements
- `.planning/ROADMAP.md` § Phase 34: the goal, the five success criteria, the boundaries, the phase
  close checks.
- `.planning/REQUIREMENTS.md` § Fit tables and tolerance window, § Gate: the seven REQ ids.

### Locked decisions
- `docs/architecture/decision_log.md`:
  - L47 and its amendments: the shaft maths, the checkpoint result, the pin policy, the guard, the
    Part 2 anchors and comparison;
  - L48: the solid;
  - L49: the interfaces, the frozen download name;
  - L05, L08, L03, L43 (the 300 s gate bar).
- `.planning/phases/31-shaft-maths-parameters-and-designation/31-CONTEXT.md`:
  - D-06: the anchor checkpoint;
  - D-10 and D-11: the pin and the Phase 34 handoff;
  - D-12 and D-20: the guard;
  - D-13 and D-22: odd z.
- `.planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md` § Checkpoint
  result: how anchors are compared, to the printed digit.
- `.planning/phases/31-shaft-maths-parameters-and-designation/31-03-SUMMARY.md`: the Phase 34
  handoff for the tabulated pin and the guard.

### Debt and ideas this phase resolves
- `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`
  (D-12)
- `docs/tech_debt/active/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md` (D-14)
- `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md` (D-11)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/spur/din5480.py`:
  - `measure_over_pins(m, z, s, pin_d)` computes M at any thickness and pin (D-09, D-10);
  - `tooth_thickness` gives s1;
  - `FIT_PATTERN` stays as is (D-14).
- `src/spur/shaft_calc.py`:
  - `pin_measurement(p, pin_d)` and `pin_contact_window` are the guard, a function of an explicit
    pin, ready to go live (D-12);
  - `ShaftDimensions` is the document. It has 13 keys, always present, `None` plus a warning;
  - the warning constants: `THEORETICAL_PIN`, `MEASURE_AT_NOMINAL_THICKNESS`, `ODD_Z_UNCONFIRMED`.
- `src/spur/__init__.py` `int_env`, and the `SPUR_*` variables in `app.py` and `cli.py`: the
  pattern for reading environment variables.
- `tests/test_din5480_anchors.py`: the approved-anchor tests, each seen red once.
  `tests/shaft_oracle.py`: the independent oracle.

### Established Patterns
- A value that cannot be said honestly is `null` plus a sentence (L08), never a plausible number.
- The shaft maths runs on every keystroke, and the import contracts keep it free of the kernel and
  the logger (`pyproject.toml` importlinter contracts). Loading the file therefore happens at
  startup, outside `shaft_calc`.
- The rows are carried on the schema (`dims`, Phase 33), and the web page renders them generically.
  A new row needs no page code, but the browser parity test and the 42-row comparison will change.

### Integration Points
- `app.py` `lifespan()` (line 138) and the CLI entry are where D-04's refusal to start belongs.
  `records.py` is the code that runs in every spawned uvicorn worker under `SPUR_WORKERS>1`, so
  each worker must see the same tables.
- `shaft_model.py` builds the solid. D-13 changes the thickness it is given, and the read-back
  check lives there.
- `tests/shaft_parity.py` and `tests/test_shaft_parity.py`: the API = CLI = page parity, which
  must cover the new rows.

</code_context>

<specifics>
## Specific Ideas

The page's own worked example, W 120x3x38x8f (Part 1 p. 24), is the first test the result must pass:
- the shaft's tooth thickness runs from s_min 6.180 through s_max 6.220 to s_vmax 6.243, with T_G
  0.063;
- the hub's space width runs from e_vmin 6.271 to e_max 6.361, with T_G 0.090.

Phase 31 already committed `M1` minimum 125.956 at s 6.180 for this designation.

</specifics>

<deferred>
## Deferred Ideas

- Span measurement W_k with k (Part 2's inspection tables print it). It is a new measurement
  method, so a later phase.
- The hub (internal spline) and its space-width window. Out of scope (REQUIREMENTS).
- The shift-range exceptions for large tooth counts: the existing debt item stays active, and
  Phase 34 does not touch it.

</deferred>

---

*Phase: 34-fit-tables-and-tolerance-window*
*Context gathered: 2026-10-30*
