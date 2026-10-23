# Pitfalls Research

**Domain:** v0.7 Splined Shaft on spur: an external DIN 5480 involute spline shaft (30 degree, flank-centred, hob root, plain shank, end chamfer) added as a second part type to a gear generator whose rules are "no number beats a wrong number" (L08), "an absent field changes nothing" (L05) and "the pre-v0.2 part is pinned" (L26).
**Researched:** 2026-10-23
**Confidence:** HIGH for repo-integration pitfalls (read from code, decision log and debt files, kernel claims measured today). MEDIUM for standard-content facts: DIN 5480 is paywalled and was not read; every standard fact below rests on cross-checked web sources and on numbers I recomputed. The human's licensed copy overrides everything in the "standard" rows.

**Claim tags.** `CALC` = I computed it today (`python3 -I`, or the repo `.venv`, cadquery 2.8.0 on this M-series Mac) and the script is in the session scratchpad. `READ` = read in a named page, file or report. `ASSUMPTION` = inference, not checked; must not become a decision or a code comment as fact. Source confidence follows the project seam: a single web source is LOW, a cross-checked one MEDIUM.

**Phase labels.** No roadmap exists yet; "Phase to address" uses these working labels:

| Label | Scope |
|---|---|
| **A. Scope, model and routes** | the product-scope `Lxx`, `ShaftParams` and its boundary, the part discriminator on API, CLI and page, the gear-regression guard, written first |
| **B. Tables** | transcription pipeline for the human's copy of DIN 5480; blocked until the human supplies the local path |
| **C. Basic dimensions and designation** | pure maths beside `calc.py`: x*m, d_a, d_f, form diameter, tooth thickness, designation parse and print |
| **D. Fit tolerances and measurement** | DIN 5480 tolerance fields, effective and actual limits, M_Re at the pin the standard names |
| **E. Solid** | outline, extrusion, shank, end chamfer, STL and STEP, build-time and size measurement |
| **F. Parity and close** | the same numbers and files from web, API and CLI; gate cost; README and docs |

---

## Ground truth established during this research

These settle the brief's open "verify the formula and sign" question. Treat them as the oracle until the human's copy says otherwise.

| Fact | Value | Basis |
|---|---|---|
| Profile shift of a shaft | `x*m = (d_B - z*m)/2 - 0.55*m`, i.e. `x = (d_B - z*m - 1.1*m)/(2*m)`, i.e. `d_B = m*z + 2*x*m + 1.1*m`. **The brief's `- 1.1*m` outside the halving is wrong by a factor of 2 on the correction term.** | `CALC` against KISSsoft W70x3x22 (`x*m = 0.3501`, `x = 0.1167`), Hexagon letter 194 (d_B 120, m 3, z 38: `x = 0.45000`, `x*mn = 1.350`); formula quoted in a web search summary of a calculator page (LOW alone) |
| Shaft profile-shift range | `x` from -0.05 to +0.45 (hub: +0.05 to -0.45) | READ: eassistant handbook ch. 17, Engineersedge calculator "Shift limit -0.05 to +0.45" |
| Shaft tip diameter | `d_a1 = m*z + 2*x*m + 0.9*m = d_B - 0.2*m` (69.400 for W70x3x22) | `CALC` + READ (KISSsoft report 5.3) |
| Shaft root diameter | `d_f1 = m*z + 2*x*m - 2*h_fP*m`, with `h_fP` set by the process: 0.60 hobbing (63.100 for W70x3x22), 0.65 shaping; the "theoretical" value is 0.55 | READ: KISSsoft report 5.1 ("DIN 5480:2006 0.60 / 0.16 / 0.45 Hobbing"), DIN 5480-1:2025-08 Table 3 quoted by dinmedia/din.de abstracts, Hexagon letter 188 |
| Tooth thickness | `s = pi*m/2 + 2*x*m*tan(30 deg)` = 5.1165 for W70x3x22; KISSsoft implies 5.1166 | `CALC` |
| Measurement over pins, even z | `M_Re = d_b/cos(a_M) + D`, `inv(a_M) = D/d_b + s/d + inv(30 deg) - pi/z`, `d_b = m*z*cos(30 deg)` | `CALC`: reproduces KISSsoft `M_Re = 76.1835` for W70x3x22, D = 6.000 |
| Measurement over pins, odd z | `M_Re = d_b*cos(90 deg/z)/cos(a_M) + D` (centres of the two nearest-opposite pins are `2*r_c*cos(90 deg/z)` apart) | `CALC` (derived, not checked against a printed odd-z value: **no oracle row yet**) |
| Theoretical pin | the pin that touches the flank at the diameter `m*z + 2*x*m` (66.70 mm), not at d_B: 5.8253 for W70x3x22; the effective, standard-size pin is 6.000 | `CALC`: contact radius 33.3501 solves D = 5.8253 |
| Tolerance structure (shaft, 6f, d_B 70, m 3) | `T_G = 0.0280 = T_act 0.0180 + T_eff 0.0100`. Effective tooth thickness in `[s + es - T_eff, s + es]`; actual in `[s + es - T_G, s + es - T_eff]`, `es = -0.025`. Printed: S_v 5.0916 / 5.0816, S 5.082 / 5.064 | `CALC` from READ: KISSsoft report 6, 6.1, 6.2 |
| Tip diameter tolerance | ISO 286 h11: `0 / -0.190` at 69.4 mm | READ: KISSsoft report 5.3; matches ISO h11 for 50-80 mm |
| Root diameter tracks tooth thickness | `Delta d_f = 1.73 * Delta s` (1.73 = 1/tan 30 deg); generating shift `x_E = x + es_act/(2*m*tan 30 deg)`: 0.1066 vs 0.1167 | `CALC` from READ: KISSsoft 5.2 and 5.3 (`x_E.e/i`, `Adf`) |
| Form diameter has two definitions | KISSsoft prints `d_Ff = 63.718` (constructed involute) and `63.920` ("allowances in accordance with DIN 5480-1 Table 5") for the same shaft; hub 70.193 vs 69.480 | READ: KISSsoft report 5.3 |
| Designation order | first number is the **reference diameter** d_B, then module, then z, then tolerance: `W 25x1.25x18x8f` is d_B 25, m 1.25, z 18. W = shaft (Welle), N = hub (Nabe) | READ: Ameco catalogue pages, KISSsoft report 2, Hexagon letter 194 (`I 120 x 3 x 38 x H7 h6 x 9H 9e` for inside centring) |
| Edition state | DIN 5480-1:2025-08 and DIN 5480-2:2025-10 replace the 2006/2015 editions; the series is four parts instead of sixteen; fit dimensions and tolerances (old Part 14) now sit in Part 1; the full root radius for shafts and cold rolling are new; Table 1 (fillet radii) was deleted from Part 2 | READ: din.de/dinmedia abstracts; Hexagon letter 188 (2006 series: Parts 1, 2, 15, 16; tolerances and Table 5 in Part 1) |

Oracle rows to pin in tests (all from one KISSsoft 2024 non-commercial demo report, 2006 edition, `W 70.00x3.00x22x6f`, hobbing 0.60/0.16/0.45): `x*m` 0.3501, `d` 66.000, `d_b` 57.158, `d_a` 69.400, `d_f` 63.100, `s` 5.1166, `W_k` (k = 4) 31.9898, `M_Re` nominal 76.1835, effective max/min 76.1462 / 76.1313, actual max/min 76.1313 / 76.1044. This is a third-party tool, not the standard: **no number ships on it alone** (L08, the rule that nothing ships without a clause in the human's copy).

---

## Critical Pitfalls

### Pitfall 1: The profile-shift formula is implemented as briefed, or its range edge is tested with floats

**What goes wrong:**
The brief reads `x*m = (d_B - z*m)/2 - 1.1*m`. Taken literally, W 25x1.25x18 gives `x*m = -0.125` (x = -0.1) instead of the correct `+0.5625` (x = 0.45), every tip, root, thickness and M_Re number is silently wrong, and nothing refuses it because -0.1 is still "a plausible shift". Second failure: both textbook sizes sit on the range edge. `CALC`: `(25 - 18*1.25 - 1.1*1.25)/(2*1.25)` is `0.45` and passes `x <= 0.45`; `(30 - 2*14 - 1.1*2)/(2*2)` is `-0.050000000000000044` and **fails** `x >= -0.05`, so a legitimate standard size is refused. And `x` printed to 4 places and reused moves M_Re by 0.17 micrometre (`CALC`: 76.18337 at `x*m = 0.35` vs 76.18354 at 0.3501).

**Why it happens:**
The formula is carried from a note, not from the standard; the sign and the factor are easy to garble. Range checks are written with bare `<=`. KISSsoft-style reports print rounded x and invite copying it back.

**How to avoid:**
- One function `profile_shift_xm(d_B, m, z)`, derived once, with the four oracle rows above as tests (70/3/22, 120/3/38, 25/1.25/18, 30/2/14) and a docstring citing the clause in the human's copy.
- Range comparisons carry an explicit epsilon (`1e-9` relative), the way `calc.py` already rounds at a named digit (`round(h, 3) > 0`, L33). Never round x before it feeds another number.
- Carry `x*m` in millimetres (the standard's quantity), not x in modules. `GearParams.profile_shift` is in modules, capped at 1.0; do not reuse the field.
- Decide up front what a combination outside -0.05..+0.45 means: not a standard size, so build if geometrically legal and print every table-dependent number as `null` with a sentence; do not 422 a legal shape (L03).

**Warning signs:**
Tip diameter not equal to `d_B - 0.2*m`; a test that "passes" with x outside the range; a standard size refused at the edge; M_Re agreeing to only 3 decimals.

**Phase to address:** C (formula and tests), A (decision on out-of-range sizes).

---

### Pitfall 2: Building to an edition the human's copy is not (or a part number that moved)

**What goes wrong:**
PROJECT.md settles "current DIN 5480 editions (parts 1 and 2)" and calls the tolerance fields "DIN 5480-2". Evidence disagrees on both counts. In the 2006 series the tolerance system and the root-diameter allowance Table 5 live in **Part 1**, and Part 2 is the nominal and inspection dimension tables (Hexagon letter 188; KISSsoft cites "DIN 5480-1, Table 5"). The 2025 editions merged the series to four parts and moved fit dimensions and tolerances into Part 1; Part 2 (2025-10) dropped its fillet-radius table. KISSsoft, the only oracle found, computes to 2006. The full root radius for shafts is new in 2025. A 2006-edition formula transcribed with a 2025-edition table (or the reverse) yields internally inconsistent numbers that each look plausible. Hexagon also documents a defect in the 2006 Table 5: the `d_f1` allowance formula `-(0.2m + 1.73(-As + T_G))` is only valid for `h_fP = 0.55 m`; for 0.60 m and 0.65 m it must read `-((1.3 - 2*h_fP)*m + ...)`.

**Why it happens:**
A paywalled standard is known through secondary sources; editions are not named in tutorials; vendors lag the standard by years.

**How to avoid:**
- First act of phase B: the human states the edition, part numbers and year of the licensed copy; record it as `EDITION` in the data module and in the designation output footnote. Every table row carries edition, part, table and clause.
- Correct the PROJECT.md wording ("tolerance fields from Part 1 or Part 2, per the copy") at phase start, as an `Lxx` amendment, not by silent drift.
- If the copy is 2006/2015 and the KISSsoft oracle is 2006, differences from 2025 stay a recorded `ASSUMPTION`; do not claim "current edition".
- Any formula the standard prints per dedendum variant is transcribed per variant, not generalised from the one that was easy to read.

**Warning signs:**
A table cell cited to a Part that does not contain it; formulas matching the KISSsoft report to 1e-4 but a tolerance cell off; an `h_fP` constant with no variant named.

**Phase to address:** B (edition capture, citation schema), A (PROJECT/`Lxx` wording).

---

### Pitfall 3: Transcription errors from a paywalled copy, and a public repo

**What goes wrong:**
The tables are keyed by hand into a data file. One wrong digit in a fundamental deviation or tolerance cell becomes a printed tooth-thickness limit someone cuts metal to (L08), and no test notices because the test data came from the same keying. Typical errors for this material: dropped or doubled digits; a decimal comma read as a point or thousands separator; **micrometre vs millimetre** (standards print tolerances in um, code is mm: a 1000x error); a PDF-copied minus sign arriving as U+2212 or an en dash, which `float()` refuses or a regex silently drops, flipping the sign of `es`; merged table cells shifting a row by one column; a bracket row ("over 50 up to 80") attached to the wrong size.
The repository is **public with no licence file** (`gh repo view`: visibility PUBLIC, licenseInfo null). Committing a verbatim reproduction of a licensed DIN table is a copyright and licence-terms question the human must decide; no agent may settle it (CLAUDE.md "stop and ask").

**Why it happens:**
One reader, one pass, no structural check; the temptation to treat a vendor report as the second source.

**How to avoid:**
- **Two independent readers, one diff.** Reader 1 is the human keying from the licensed copy. Reader 2 is a separate pass over the same pages by a different channel (the agent reading the human-supplied PDF with `Read`/`pdftotext`, or the human re-keying blind a day later). A script diffs the two files; the transcription commit lands only at zero diff, with both source hashes in the message. Both channels can misread digits, so reader 2 is a check, not an oracle.
- **Structural invariants as tests, run on the data file:** tolerance grades are monotone in grade and in size bracket; consecutive grades keep a ratio near 1.6 (ISO R5 progression, `ASSUMPTION` that DIN 5480 follows it; verify on the first two rows read); `T_G = T_act + T_eff` holds in every cell (`CALC`: 0.0280 = 0.0180 + 0.0100 in the oracle); `es` is non-positive for shaft positions e, f, g, h, d; units asserted (every value between 0.0005 and 1.0 mm, never between 1 and 999).
- **Cross-table checks free of charge:** Part 2 nominal rows against the formulas of Pitfall 1 (they must agree to the printed digit, so each table checks the other); at least three full rows against the KISSsoft oracle.
- **Cited or absent.** Schema `{value, unit, edition, part, table, clause, page}`; `test_no_uncited_value` fails on any empty field; a cell not transcribed is absent, and absent means `null` plus a warning, never a neighbour's value (L08).
- **Read-back.** A `make` target prints the stored table in the standard's own row/column layout for the human to proofread against the page.
- **Licence first.** Ask before phase B writes a file: (1) commit the numeric tables as data with clause citations and no prose or layout copied, (2) keep them in a private, gitignored file with a clean-checkout skip (breaks CI determinism, L13), (3) transcribe only the cells the oracle rows and the tested sizes need. Recommendation: (1) limited to numbers and citations, after the human confirms it is acceptable under the licence of their copy. Never copy standard prose into docstrings; cite clause numbers only.
- Normalise on read: map U+2212 and en dash to `-`, `,` to `.`, and reject any cell that still fails `float()`; do not `try/except` it away.

**Warning signs:**
Table values entered in one commit with no second reader; a tolerance 1000x off its neighbours; a sign test missing; a citation field filled with "DIN 5480" only.

**Phase to address:** B (all of it); A (licence decision before B starts).

---

### Pitfall 4: Reusing gear machinery for a DIN profile (and breaking the gear to do it)

**What goes wrong:**
Three traps in one reflex ("a spline is a gear, call `profile()` and `cutter()`").
(a) `calc.profile()` hard-wires tip radius `r + m*(1 + x)` and `_dedendum(m, x) = m*(1.25 - x)`; `cutter()` reads the same `1.25`. DIN 5480 has addendum 0.45 m and dedendum 0.55 / 0.60 / 0.65 m. Passing a `GearParams` built from spline numbers yields a root 0.65 m too deep and a tip 0.55 m too tall, with every check passing because the geometry is a valid gear.
(b) Generalising `_dedendum`/`profile()` in place risks moving a gear byte (L05, L26); the fixture is the tripwire, and a red fixture "is a bug in that phase, not a reason to regenerate".
(c) `GearParams` limits do not fit: `profile_shift` is in modules, `-0.6..1.0`; `module` 0.2..10; `teeth` 6..200; `pressure_angle` is a field (14.5..35). A spline has no editable pressure angle: 30 degrees is a constant of the standard. Making it a field invites 25-degree "splines".
(d) Small z: with `h_fP = 0.6 m` the root circle lies below the base circle when `x < 0.6 - 0.067*z` (`CALC`; `rf < rb` iff `0.134*r < 0.6*m - x*m`). That is x < 0.20 at z = 6, 0.13 at z = 7, 0.06 at z = 8, about 0 at z = 9. DIN 5480 starts at z = 6 (FVA workbench: 6 to 82). Below the base circle the flank continues into the hob's trochoid, not the radial line of L10; a radial root there is a false profile and a false form diameter.

**Why it happens:**
The v0.4 trochoid work (`Cutter`, `root_mode`, `RootCurve`) is the only hob-root code in the tree and looks directly reusable; its constants are baked into one rack.

**How to avoid:**
- Write the shaft's maths as a sibling (`spline.py` or a section of `calc.py` the gear never calls), taking `ShaftParams`, with 30 degrees a module constant and `h_aP`, `h_fP`, `rho_fP` named values from the standard.
- If the trochoid code is shared, parametrise it with a rack record whose gear instance is the current literal (`1.25 - x`, `1 + x`), and prove it with `git diff --exit-code tests/regression/` against the `v0.6` tag plus the 192 calc rows of Phase 19. Otherwise copy and leave the gear path alone (a copy is the cheaper regression risk; note the duplication as `nice` debt).
- For z <= 9 always use the hob-root envelope and refuse or null whatever it cannot prove (the existing `root_mode` reasons are the model: a reason sentence, never a plausible curve).
- Oracle for the root: KISSsoft's smallest root curvature radius (0.509 / 0.510 mm for W70x3x22, `rho_fP* = 0.16`) and an independent swept-cutter construction like `tests/trochoid_oracle.py`, sharing no code with the maths.

**Warning signs:**
The shaft module imports `GearParams`; `1.25` appears in a spline code path; a spline test builds at z < 10 without a root-mode assertion; the regression fixture is touched in a feature commit.

**Phase to address:** A (the sibling-model decision), C (the maths), E (the outline).

---

### Pitfall 5: Root-form variants conflated (flat root with corner radius, full fillet, process-dependent dedendum)

**What goes wrong:**
"Root fillet" means different things. Under ANSI B92.1 and ISO 4156 a **flat root** has the flanks joined to the root circle by separate fillets and a **fillet root** has one full-radius fillet (READ: geartechnology/eng-tips search summaries, LOW). DIN 5480 uses a hob profile with a tip radius `rho_fP = 0.16 m` (a flat bottom with corner radii) and, in the 2025 edition, adds a full root radius for shafts. Dedendum depends on the process (0.60 hob, 0.65 shaping, 0.55 theoretical). The root diameter also moves with the tooth thickness (Pitfall 7: `Delta d_f = 1.73 * Delta s`). A UI that offers "root fillet: flat / full" invites a combination the standard has no number for.

**Why it happens:**
The existing gear has a `root_fillet` radius field and a `root_shape` select; copying them gives the shaft the same vocabulary with different meanings.

**How to avoid:**
- Settled scope is the hob root only: no root-shape field on the shaft in v0.7. Say so in the `Lxx`. A full-radius variant is a later field only if the human's copy tabulates it.
- Fix `h_fP`, `rho_fP` as constants of the one supported process (0.60 / 0.16 / 0.45 if the human's copy lists it; ask which process the human wants and cite the table), and name the process in the output sentence.
- Build the root from the hob envelope at the generated (tolerance-shifted) shift, and print `d_f` for the same part the solid is built from (L08).
- Do not borrow the gear's `root_fillet` semantics (a radius the user can set, capped to fit); for the shaft the radius is the cutter's, not a design choice.

**Warning signs:**
A shaft schema containing `root_fillet` or `root_shape`; `d_f` printed at nominal while the thickness is modelled at `es`; a form field that cannot be mapped to a table.

**Phase to address:** A (field list), C (constants), E (outline).

---

### Pitfall 6: A "form diameter" that is the wrong form diameter

**What goes wrong:**
KISSsoft's own report prints two root form diameters for one shaft, 63.718 (constructed involute) and 63.920 ("in accordance with DIN 5480-1 Table 5"), and 70.193 vs 69.480 for the hub. The standard's value is defined by formula and depends on the mating part (Hexagon letter 188: the limit value "is dependent on the counterpart and therefore only applies to the selected shaft/hub joint"); the geometric junction of the trochoid and the involute is what v0.4 already computes and prints as `root_form_d` for gears. Printing the geometric junction under the standard's symbol `d_Ff` is a false claim of the kind L08 forbids; printing the standard's value for a part built with another root is the same claim reversed. The two differ by 0.2 mm on a 3 mm module shaft.

**Why it happens:**
Same word, two definitions; the existing `root_form_d` is there to be reused; a shaft alone has no counterpart to take the standard's definition from.

**How to avoid:**
- Name the quantity in the field and the sentence ("involute begins at" for the geometric, `d_Ff` only for the standard's formula).
- Print the standard's `d_Ff` only if its formula (clause and table) is transcribed and the pairing it assumes is stated (nominal hub of the same size); otherwise `null` with a warning (L08).
- Test the geometric number against an independent swept-cutter oracle and the standard's number against its table cell; do not assert one equals the other.

**Warning signs:**
One field name used for both; a test comparing `root_form_d` to a table cell; a form diameter printed with no hub assumption.

**Phase to address:** C (definition), B (formula and Table 5 transcription), D (if tied to a tolerance).

---

### Pitfall 7: Effective vs actual tooth thickness, and which one the solid carries

**What goes wrong:**
DIN 5480 gives four tooth-thickness limits per fit: effective max and min (what a gauge sees, flank and form errors included) and actual max and min (a single caliper reading). `CALC` on the 6f oracle: effective in `[s + es - T_eff, s + es]` and actual in `[s + es - T_G, s + es - T_eff]`, with `T_G = T_act + T_eff`. If the code treats "tolerance 8f" as one symmetric band it prints a tooth thickness that no limit corresponds to. A CAD solid is one shape: it can carry one thickness. Choosing silently (nominal, `s + es`, or the mid of the band) makes the printed "tooth thickness" ambiguous, and then M_Re (Pitfall 8) differs per limit: the oracle shows 76.1835 nominal, 76.1462 / 76.1313 effective, 76.1313 / 76.1044 actual.
Related traps: the root diameter and generated shift move with the thickness deviation (`Delta d_f = 1.73 * Delta s`), so modelling the flank at `es` but the root at nominal builds a part no hob cuts; and fundamental deviations are not ISO 286 diameter deviations (tip diameter is h11 = ISO 286, but `es` of f at d_B 70 is -25 um where ISO 286 f for 50-80 mm is -30 um, `ASSUMPTION` that this is not a typo in the report: do not substitute ISO 286 tables for DIN 5480 tooth-thickness tables).

**Why it happens:**
The fit letter is the only thing in the designation; the structure behind it is in Part 1.

**How to avoid:**
- Decide, log and print which thickness the solid carries. Recommendation: the effective maximum-material thickness (`s + es`), because it is the one a gauge and a mating hub see, with the other three limits printed beside it and labelled effective/actual.
- Derive the other three limits from table values `es`, `T_eff`, `T_act` (never from one `T`); assert the identity `T_G = T_act + T_eff` on every table cell.
- Apply the same shift to the root and tip generation that the standard applies (cite the clause), or print root and tip as the nominal with a sentence that the part is modelled at nominal root; the solid and the number must be the same part.
- This is shaft-only: print no clearance or backlash figure that needs the hub.

**Warning signs:**
A single `tooth_thickness` field with no qualifier; `s_min` computed as `s - T`; M_Re printed once for a fit; ISO 286 tables imported for `es`.

**Phase to address:** D (limits and M_Re), E (what the solid carries), A (the `Lxx` that names it).

---

### Pitfall 8: Measurement over pins done right in the even case and wrong everywhere else

**What goes wrong:**
(a) Odd z uses the even formula (error: `d_b/cos(a_M) * (1 - cos(90/z))`, tens of micrometres to over a millimetre). (b) The pin is the wrong size: the "theoretical" pin touches at `m*z + 2*x*m` (5.8253 for the oracle); the standard names an effective size (6.000) and tabulates it in Part 2. A different pin changes the contact diameter. If it lands below the form diameter or above the tip, the pin touches a part of the flank that is not involute (or the tip land) and `M_Re` is not a flank measurement. (c) Solving `inv(a_M) = ...` by Newton without a bracket (the L08 origin story: 138 parameter sets of confident garbage). (d) Rounding `x` before use (0.17 um, Pitfall 1). (e) The oracle shares code with the implementation. (f) The hub's M_Ri has negative z in KISSsoft and a different sign; not in scope, but reusing the function for it later without the sign is the usual bug. Balls and pins give the same number for straight teeth (KISSsoft prints identical values); "ball vs pin" is a gauge question and a cosmetic label, not two formulas, until helix appears.

**Why it happens:**
The even case is the textbook one; odd z needs one more factor; pin choice is invisible in the designation.

**How to avoid:**
- One function over `(s, z, D)` using bisection on a bracket (as `_involute_angle` does for gears), returning `None` (and a sentence) when no root exists, when the pin contact diameter is not between the form diameter and the tip diameter, or when the pin does not fit in the space.
- Pin diameter is an input with the standard's value as default taken from the human's Part 2 row; an out-of-range pin is a 422 naming `pin_d` (a direct conflict) and a missing table row is `null` (L08).
- Independent oracle: build the 2D outline, place a circle of the pin diameter in the gap by tangency search against the polyline, measure across (even) or across the two nearest-opposite pins projected on the line of centres (odd). Share no code with `calc`. Pin the oracle against the KISSsoft row for even z (done: 76.1835) and against the human's Part 2 row for at least one odd-z size; an odd-z row from the standard is the missing oracle.
- Table both parities in the tests: even and odd z, and the smallest and largest tooth counts.

**Warning signs:**
M_Re tests that only use even z; a function with no pin-contact guard; a Newton loop; the test imports `inv` from `calc`.

**Phase to address:** D.

---

### Pitfall 9: Designation parse and print that do not round-trip (and a parser that guesses)

**What goes wrong:**
`W 25x1.25x18x8f` is d_B 25, m 1.25, z 18, tolerance 8f. A reader who sees "25x1.25x18" as "25 teeth" is wrong (a web summary of this very string made that mistake in this research). Variants that real documents contain: `DIN 5480 - W 70.00x3.00x22x6f` (KISSsoft prints two decimals), `W 25 x 1,25 x 18 x 8f` (decimal comma, Ameco), `X` or the multiplication sign for `x`, optional `DIN 5480 -` prefix, hub `N`, pairs `9H/8f`, centring variants (`I 120 x 3 x 38 x H7 h6 x 9H 9e`, Hexagon letter 194). Print and parse that disagree on `1.25` vs `1.250`, `25` vs `25.0`, or case (`8F`), a parse that accepts what print never emits, and two fields that disagree (designation says z 18, field says z 20) all produce parts the user did not ask for. A permissive parser also guesses at ISO 4156 strings (`INT 18z x 1.25m x 30R x 6H`) and ANSI pitch (`24/48`).

**Why it happens:**
The designation is both an output (a label) and an input (a link); one-sided testing lets drift pass.

**How to avoid:**
- The numeric fields are the truth; the designation is a view, like the bore-shape select (L42): printed from the fields, parsed into the same fields, never stored beside them. If both arrive, they must agree or the request is a 422 naming both (L03).
- Canonical print: shortest `:g` numbers, one `x` separator, space after the type letter, no prefix unless asked. Lenient on input for the documented variants above; everything else is refused, including other standards, with a sentence saying so (L44's spirit: never rebuild a default from a bad link).
- Tests: round-trip both directions over asymmetric values (d_B != z; m = 1.25 and 0.75 and 10), the `70.00x3.00` and `1,25` spellings, and a refusal table for foreign strings. Bound the input length and use an anchored, non-backtracking pattern.
- A designation whose d_B/m/z give x outside the range is parsed, then handled as in Pitfall 1 (not a standard size), not rejected as a syntax error.

**Warning signs:**
A `designation` stored on the model; `float()` on unstripped text; the parser accepting `INT`/`EXT` or `/`; the first and third numbers ever equal in a test.

**Phase to address:** C.

---

### Pitfall 10: ANSI B92.1, ISO 4156 and inch leakage

**What goes wrong:**
ANSI B92.1 is inch and diametral pitch (30, 37.5 and 45 degree, flat and fillet roots, side and major-diameter fits); ISO 4156 / ANSI B92.2M is metric module with the pitch diameter `m*z` as the reference and no d_B; DIN 5480 is module with a reference diameter, 30 degrees only. `m = 25.4 / DP` is exact only as a number, but the standard dimensions of the families are not conversions of each other (tip and root diameters, fillet radii, tolerance classes and effective/actual tolerancing differ; Hexagon letter 111: ISO 4156 forces the same tolerance class on hub and shaft and the hub position to H where DIN 5480 does not). A user pastes an ANSI callout into the designation field, or a team later copies the shaft model for ISO 4156 and keeps DIN's `+0.55*m` shift.

**Why it happens:**
"Spline" feels like one thing; a unit field or a `standard` enum looks like cheap generality.

**How to avoid:**
- Name everything for what it is (`din5480`, `d_b`), keep `pressure_angle` a constant, no `standard` field, no unit switch (L05: absolute millimetres). One family per milestone is already the PROJECT rule; the pitfall is only that code written now should not pretend otherwise.
- The parser refuses every non-DIN form with a sentence ("ISO 4156 and ANSI B92.1 are not supported; this is DIN 5480"), tested.
- Do not accept inch anywhere; refuse a `DP`-style value.

**Warning signs:**
A `standard` or `unit` parameter; `25.4` in the spline code; a shared "spline" module with DIN constants inside.

**Phase to address:** A (naming, no `standard` field), C (refusal table).

---

### Pitfall 11: Rounding, size brackets and "interpolation" of tolerance tables

**What goes wrong:**
(a) Tolerances and fundamental deviations are tabulated per size bracket (ISO convention: "over X up to and including Y"). A bracket boundary written with `<` instead of `<=` gives the next row's tolerance for d_B = 80, and linear interpolation between rows yields a value the standard does not contain. (b) A value that is in the standard as a table cell is also computable; code that "improves" the cell with the formula, or the reverse, disagrees by the standard's own rounding. (c) Comparing a computed number with a printed one at full float precision fails every row; comparing at a loose tolerance hides real errors. (d) Fit letters/grades outside the tabulated combinations (a letter the standard has but the human did not transcribe) get extrapolated from neighbours. (e) Parameters that determine the bracket (which dimension: d_B or m? `ASSUMPTION`, unknown until the copy is read) are chosen wrong. (f) The ISO 286 bracket rule uses the geometric mean of the bracket limits, not the actual size (`ASSUMPTION` for DIN 5480): feeding the real d_B into a formula instead of looking up the row changes the third decimal.

**Why it happens:**
Spreadsheet thinking: a missing value feels like an interpolation job.

**How to avoid:**
- Lookup, never interpolate. A (grade, position, bracket) cell not in the data returns `None` and the caller prints `null` plus "outside the transcribed tables" (L08).
- Bracket tests at both edges of every bracket (d_B = 50, 50.001, 80, 80.001) with the edge convention taken from the copy and cited.
- Where a table and a formula both exist, one is the source and the other a test (Pitfall 3); the test tolerance is half the last printed digit, recorded with the table (L26 records the number that set every tolerance; do the same).
- Keep raw doubles through the chain; round only for display, to the digit the standard prints.

**Warning signs:**
`numpy.interp` or a hand lerp in the tolerance code; a bracket test absent at the edges; two sources for one number with no cross-check test.

**Phase to address:** B (data shape), D (lookup).

---

### Pitfall 12: Regressing the gear: routes, schema, hash, CLI, slug, caches and a `must` debt trigger

**What goes wrong:**
The whole product is gear-shaped. Touchpoints read in the tree: `GET /api/schema` is `GearParams`'s schema and builds the page form; `/api/info` and `/api/model.{fmt}` take gear query fields (`InfoQuery`, `ModelQuery`); `app.js` reads `location.hash` as gear fields with no part marker, has a fixed dimension list (`span`, centre distance), a `mate-teeth` input and a page title naming a spur gear; `cli.py` generates flags from `GearParams.model_fields`; `records._gear_fields`, `pool.build_export/executor_for/recreate_for`, `BuildBackend` and `_EXPORTS` are typed on `GearParams`; `slug()` is `spur_z..._m..._pa...` (and L40 forbids keying any cache by slug); `model._build_cached` is one `lru_cache` of 4. Concrete failure modes:
- Unknown query keys are silently ignored at runtime (mypy forbids extras, pydantic does not). A shaft link `#d_b=25&module=1.25&teeth=18` opened by the gear page, or sent to the gear route, builds a **gear** with those two shared names and defaults for the rest: the silent wrong part L44 was written to prevent. The shared field names `module` and `teeth` make it near-certain.
- Changing the shape of `/api/schema` (a `oneOf`, a `part` field) breaks the form builder and the 44 pinned request records (`tests/regression/golden_requests.json`, L39).
- Editing `gearQuery()` or `refuse()` in `app.js` to dispatch on part **fires the `must` debt trigger** of `2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` ("next edit of `refuse()` or `gearQuery()`"); a shaft form inherits the blank-box-but-built-token defect for `+22`, `22.`, ` 22`.
- Widening types to `GearParams | ShaftParams` through `pool`, `records`, `app` under `mypy --strict`/`disallow_any_explicit` is a multi-file change in the most delicate modules; `lru_cache(maxsize=4)` and the `_BlobCache` byte budget become shared between parts, so a shaft evicts gear solids that L17's memory ceiling was measured for.
- A new filename prefix colliding with the gear's: `spur_z18_m1.25_pa30` is a valid gear name.

**Why it happens:**
"Second part type" is added at the leaf (a new model) while the trunk (routes, page, CLI, pool, caches) is gear-only.

**How to avoid:**
- Gear routes, schema, query models, `DerivedDimensions` (19 fields, frozen), `slug()` and `tests/regression/` stay **byte-identical**; the shaft gets sibling routes (`/api/shaft/info`, `/api/shaft/model.{fmt}`, `/api/shaft/schema`), a sibling model with `extra="forbid"` from day one (no legacy to protect), a sibling dimensions model and its own slug (`spur_shaft_...`, derived only from validated numeric fields, never from raw text).
- Part selection is explicit in the shaft URL (a path or a `part=shaft` key) and a gear link without it stays a gear. Prove with the 44-record fixture, `golden_requests.json`, and `git diff --exit-code tests/regression/ ci.yml` against `v0.6` after every phase. `make fixture.regen` is forbidden in v0.7.
- Decide WR-02 deliberately: either leave `refuse()` and `gearQuery()` untouched (page dispatch in new code) or take WR-02 as a planned task with its own `Lxx`; do not fire it by accident.
- Type the pool and records with a small `Protocol` or a union in one commit, keeping gear call signatures unchanged; measure the cache and memory effect before accepting a shared `lru_cache` (L07, L17).
- CLI: a new subcommand rather than a `--part` flag on `export`; `argparse` abbreviation (`allow_abbrev` default) means new flags can change what a short prefix resolves to on existing commands.

**Warning signs:**
A diff in `tests/regression/`; `golden_requests.json` changing; a shaft URL returning 200 on a gear route; `GearParams` imported by spline code; a shared `lru_cache`.

**Phase to address:** A (design and guard first), F (parity, WR-02 decision, final diff checks).

---

### Pitfall 13: Kernel and mesh surprises, mostly not the ones expected

**What goes wrong:**
Prototype `CALC` (cadquery 2.8.0, one closed wire of `makeSpline` flanks and three-point-arc lands and roots, `extrudeLinear`, 16 points per flank; crude hob root, so shape not accuracy): z = 22 / m = 3: extrude 0.01 s, fuse with a shank 0.18 s, cone-cut chamfer 0.34 s; z = 82 / m = 1: extrude 0.03 s, fuse 1.0-1.5 s, cone cut 1.1-1.6 s; STL preview 0.8 MB / fine 0.96 MB. A fine z = 200 gear is 9 MB; the shaft is not the heavy case. The risks are correctness, not speed:
- **Tangent or coincident geometry.** A shank diameter exactly equal to the tip diameter (a common drawing) overlapping the teeth fused correctly here (volume matched the closed-form to 1e-4 at deltas 0, +/-1e-9, +1e-6, +1e-3), but OCCT is known to drop a solid silently on exact tangency in other configurations (search result on CadQuery vs OpenSCAD: "union operations can silently discard geometry"; MEDIUM-LOW). One passing configuration is not proof.
- **"End chamfer" is two different features.** An edge chamfer along the end-face outline (88 edges at z = 22, 328 at z = 82; 0.4 s and 3.3-3.6 s here, valid) is not the conical lead-in a spline drawing shows (a revolved cut, one boolean). The printed chamfer size must be the one actually cut (L45: asked and not cut prints `null`), capped by the splined length and by the root, L03.
- **Sweeping/twisting or per-tooth booleans** for a straight shaft: slow and unnecessary. A single closed wire extruded is 10-45 ms.
- **Printed vs built.** Tooth thickness at d_B is a formula; the solid's value depends on the 16-point spline. Without a read-back on the built solid the number is a promise, not a measurement (the keyway depth was read back within 1e-6 mm for exactly this reason, L28).
- **Tessellation.** The tolerances in `TESSELLATION` are absolute millimetres (preview 0.08 / 0.5 rad, fine 0.01 / 0.1 rad): a 10 mm shank preview is visibly faceted, a 200 mm one is fine; harmless but record it.
- **Spline run-out and "splined length" are undefined for a prism.** A real shaft has a hob run-out zone where the profile fades; a plain prism has none. State what "splined length" means (full-form prism) in the field help and the sentence.

**Why it happens:**
Kernel fears are inherited from the gear (29 s worst rows); the shaft is cheap, so the guard is skipped.

**How to avoid:**
- Closed-form volume guard on every kernel test: `V = A_spline*L_s + pi*r_shank^2*L_k - overlap`, with `A_spline` from `1/2 * integral r(theta)^2 d(theta)` of the analytic profile in the test (own involute, no `calc` import). Rows: shank equal to `d_a`, to `d_f`, between, and above `d_a` by 1e-6 and 1e-3.
- Chamfer as a revolved-cone intersection (single boolean), verified valid, with the applied size read back; keep the edge-chamfer variant out unless the human asks for it.
- Read back the tooth thickness and tip/root radii from a z-section of the built solid within a named tolerance (set it from a measurement, as L26 does).
- Record timing and STL/STEP size for the largest and smallest tooth counts in `bench/RESULTS.md` before any claim; do not assume the prototype's numbers (different root, one host).

**Warning signs:**
`isValid()` used as the only check; a volume test with a pinned literal instead of a closed form (the filleted-spoke gap in CONCERNS.md); an "chamfer" number with no read-back.

**Phase to address:** E (all), D (the thickness read-back needs the limits).

---

### Pitfall 14: The gate budget is already 79 % spent

**What goes wrong:**
L43 sets the bar to 300 s; v0.6 closed at `1348 passed in 236.23s` (PROJECT.md), leaving 64 s. A shaft test matrix with kernel builds (even 40 rows at 1-2 s) plus a browser scenario can breach the bar, and then the bar gets "re-set" toward a pass, which L34/L43 forbid.

**How to avoid:**
Pure-maths tests (formulas, tables, designation, M_Re, tolerances) carry the weight: milliseconds each, thousands of rows. Kernel rows only where the kernel is the question (a handful: smallest/largest z, shank equal to `d_a`, chamfer). Measure the delta in the phase that adds tests and record it before the phase closes (the D-06 pattern); `make verify.fast` (pre-commit slice, L36) must stay under 30 s.

**Warning signs:**
A parametrised kernel test over the full size table; a new browser scenario per field.

**Phase to address:** every phase that adds tests; F verifies the total.

---

### Pitfall 15: Printing a number for a size the tables do not cover

**What goes wrong:**
The user types any d_B, m, z (the field set allows it); the standard defines a discrete series. Formula-derived numbers (x*m, d_a, d_f, s, M_Re) exist for all of them; table-derived ones (tolerance, `es`, T, h_fP variants, standard pin D) exist only inside the transcribed set. Mixing them silently prints a "fit 8f tooth thickness" for a size with no 8f cell, or a formula-derived pin for a size where the standard names another.

**How to avoid:**
Three tiers, explicit in the `Lxx`: (1) formula numbers always, with the sentence "not a size in DIN 5480" when x is outside the range or the combination is not in the transcribed Part 2 rows; (2) table numbers only when the cell exists, `null` plus the reason otherwise; (3) the designation printed with its tolerance only when tier 2 holds. Hard 422 only for a geometric impossibility (negative land, shank conflicts, chamfer beyond the length, a pin that cannot be in the space) per L03.

**Phase to address:** A (policy), C and D (implementation).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| Call `profile()`/`cutter()` with a faked `GearParams` | No new maths | Wrong addendum/dedendum (Pitfall 4); a gear-fixture risk the first time anyone "fixes" it | Never |
| Copy the trochoid code for the shaft rack | Gear path untouched | Two copies of a delicate algorithm | Acceptable if filed as `nice` debt with the trigger "third rack" |
| One shared `lru_cache`/`_EXPORTS` for both part types | Zero new code | Memory ceiling (L17) measured for gears only; eviction coupling | Only after a measured sweep of mixed requests |
| Hand-keyed tables, single reader | Fast | One wrong digit becomes a cut number | Never |
| Table cell filled by formula "for completeness" | No gaps | A number with no clause; formula and table disagree later | Never; absent means `null` |
| Designation stored next to its fields | Simple link | Two truths | Never |
| Pin diameter fixed to the theoretical value | No Part 2 transcription | Not the standard's M_Re; may touch off-flank | Never as a printed standard number; fine as a labelled "theoretical" |
| Reuse the gear page's `gearQuery()`/`refuse()` by editing them | Less JS | Fires WR-02 (`must` debt) with no plan for it | Only as a planned WR-02 task |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|---|---|---|
| `/api/schema` + form builder | Return a union schema, or add a `part` field to `GearParams` | Leave it byte-identical; add `/api/shaft/schema`; new field metadata (`group`, `unit`, `step`, `enabled_when`) reuses the existing vocabulary (L41) |
| URL hash | Put shaft fields in the hash with no marker | Explicit part marker; absent marker means gear (L05); unknown keys on the shaft model are a 422 |
| CLI flag generation from `model_fields` | One generator for both, or a `--part` on `export` | A subcommand per part; flags generated from the sibling model; `argparse` abbreviation checked |
| `BuildPool` (hash affinity, `hash(p) % workers`) | Assume `GearParams` in signatures | A `Protocol` or union in one commit; affinity keeps working for any hashable frozen model |
| Logging (`records._gear_fields` uses `slug()` and `model_dump(exclude_defaults=True)`) | Record the raw designation or free text | Record the validated numeric fields and the slug only |
| Kernel pin / fixture (L34, L26) | Rebuild the fixture "because the kernel changed" | Not in v0.7: no kernel bump, no `make fixture.regen` |
| Browser test (L39) | New scenario inside the existing 44-record pin | New, separate pins for the shaft; the gear pins unchanged |
| KISSsoft/Hexagon/Engineersedge as oracles | Treat a vendor tool as the standard | Oracle for spot checks only; the human's copy decides; edition recorded |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|---|---|---|---|
| Per-tooth booleans or `polarArray` unions | Build time scales with z | One closed wire, one extrude (10-45 ms, `CALC`) | Visible at z = 82 |
| Edge chamfer on a long outline | 3.3-3.6 s at z = 82 vs 1.1 s for a cone cut (`CALC`) | Revolved-cone intersection | z >= 60, all within the 30 s `SPUR_BUILD_TIMEOUT` today, so a cost not a failure |
| Shaft and gear sharing a 4-entry solid cache | Gear cache misses after shaft requests | Measure; separate caches if it matters | Mixed traffic |
| Large kernel test matrix | `make verify` over 300 s (236 s today) | Pure-maths tests carry the volume (Pitfall 14) | The first parametrised kernel table |
| Solving M_Re by unbracketed iteration | Rare hang or garbage | Bisection on a bracket (L08 precedent) | Small z, large pins |

## Security Mistakes

| Mistake | Risk | Prevention |
|---|---|---|
| Echoing the raw designation into `Content-Disposition` or a log line | Header/log injection, odd filenames | Slug built only from validated numbers (L40 spirit); log validated fields |
| A backtracking designation regex on unbounded text | CPU denial of service on an unauthenticated endpoint | Length cap, anchored linear pattern |
| Unbounded `splined_length`/`shank_length` | Huge STL/STEP, memory | Field bounds from a measured sweep; the 4g container ceiling (L17) is not re-derived for shafts |
| Committing licensed tables to a public repo | Licence/copyright exposure | Ask the human before phase B writes data (Pitfall 3) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---|---|---|
| Designation box plus separate fields | Which one wins? | Fields are truth; the designation is shown and can be pasted (parse into the fields); conflicts are a 422 naming both |
| "Tooth thickness" with no qualifier | Wrong gauge, wrong reading | Label effective/actual, max/min, and the one the solid carries |
| A dropdown of fits including ones not transcribed | Selecting a fit that prints `null` | Offer exactly the transcribed set; the schema carries the list |
| A size outside the standard silently accepted | False confidence | A visible warning "not a DIN 5480 size; table-dependent values withheld" |
| Gear page chrome (mate teeth, caliper hint, "spur gear" title) on the shaft page | Confusing | Part-specific dimension list; page title from the part; no gear controls |
| Blank number box carrying a hidden link token (WR-02) | Form says default, part is not | Decide WR-02 explicitly before building the shaft form |

## "Looks Done But Isn't" Checklist

- [ ] **x*m formula:** matches 70/3/22 (0.3501 or 0.35 by the rounding rule), 120/3/38 (0.45), 25/1.25/18 (0.5625 mm) and 30/2/14 (-0.1 mm) with the edge epsilon -- verify the four rows and the `-0.05000000000000004` case.
- [ ] **Edition recorded:** every data row carries edition, part, table, clause -- verify `test_no_uncited_value` and the edition string in the output.
- [ ] **Two-reader transcription:** diff is empty, hashes in the commit -- verify before B closes.
- [ ] **Unit/sign sweep:** no tolerance outside 0.0005-1.0 mm, no `es > 0` for e/f/g/h/d -- verify the invariant test.
- [ ] **Odd z M_Re:** an odd-z row from the standard's Part 2, not only the even-z KISSsoft row -- verify; if absent, the number stays `null` for odd z.
- [ ] **Pin contact on the flank:** contact diameter between the form diameter and the tip diameter -- verify the guard returns `None` outside.
- [ ] **Form diameter named:** geometric junction and the standard's value are separate, labelled fields -- verify the sentences.
- [ ] **Which thickness the solid carries:** stated in the `Lxx`, the field help and the output; read back from a z-section -- verify within a tolerance set from a measurement.
- [ ] **Out-of-table size:** prints formula numbers plus a sentence, table numbers `null` -- verify with a size not in the data.
- [ ] **Gear untouched:** `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml`, `/api/schema` payload byte-equal, 44 golden requests unchanged -- verify after every phase.
- [ ] **Designation round trip:** both directions, asymmetric values, `70.00x3.00`, `1,25`, foreign strings refused.
- [ ] **Closed-form volume** for shank = `d_a`, `d_f`, between and above; applied chamfer read back.
- [ ] **WR-02 decision:** `refuse()`/`gearQuery()` either untouched or taken on purpose.
- [ ] **Gate cost:** `make verify` total re-measured and recorded against 300 s.
- [ ] **Licence:** the human has answered the public-repo question before any table is committed.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---|---|---|
| Wrong x*m formula shipped | LOW | Fix the one function; the four oracle rows fail first; no link depends on it yet (new part type) |
| Wrong table digit found after release | MEDIUM | Correct the cell, rerun the invariant and two-reader diff, add a regression row for the cell, record in the debt ledger; links keep building the same solid but printed limits change: note it in the release |
| Edition mismatch discovered late | HIGH | Re-key the affected tables for the right edition; formulas tested against both oracles; `Lxx` supersedes the earlier assumption |
| Gear fixture goes red | MEDIUM | Revert the feature commit; it is by definition a defect of the phase (L26 D-03); never regenerate |
| Licensed table committed to the public repo | MEDIUM | Remove from the tip, rewrite history only on the human's decision (destructive: stop and ask), replace with citations plus a local-only loader |
| Silent boolean loss in a shank fuse | LOW | The closed-form volume guard fails; switch the shank construction (cut from a cylinder, or a revolve) |
| WR-02 fired by accident | LOW | Move dispatch into new code, or take WR-02 as an explicit task |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---|---|---|
| 1. Profile-shift formula and edge | C (A for out-of-range policy) | Four oracle rows, epsilon edge test |
| 2. Edition and part drift | B first act; A wording | Edition constant, citation test, `Lxx` amendment |
| 3. Transcription and licence | A (licence ask), B | Two-reader diff, invariants, read-back, `test_no_uncited_value` |
| 4. Gear machinery reuse | A, C, E | No `GearParams` import in spline code; regression diff empty |
| 5. Root-form variants | A, C, E | No root field on the shaft; constants cited |
| 6. Form diameter | C (B for Table 5) | Two names, one oracle each |
| 7. Effective vs actual | D, E (A for the `Lxx`) | `T_G = T_act + T_eff` on every cell; read-back |
| 8. Over-pins | D | Even and odd rows; independent oracle; contact guard |
| 9. Designation | C | Round-trip and refusal tests |
| 10. ANSI/ISO leakage | A, C | No `standard`/unit field; refusal sentence tested |
| 11. Rounding and brackets | B, D | Edge tests at every bracket; no interpolation |
| 12. Gear regression | A (guard), F | Fixture/golden/ci.yml diff against `v0.6`; schema byte-equal |
| 13. Kernel and mesh | E | Closed-form volume; read-back; timings in `bench/RESULTS.md` |
| 14. Gate budget | every phase; F | Measured delta recorded; total under 300 s |
| 15. Out-of-table sizes | A, C, D | Three-tier tests with an out-of-set size |

## Stop-and-ask list (CLAUDE.md triggers raised by this research)

1. The brief's `- 1.1*m` conflicts with the evidence (`- 0.55*m`): conflicting evidence, human to confirm against the copy.
2. The tolerance fields are "DIN 5480-2" in PROJECT.md, but Part 1 holds them in the 2006 series and the 2025 series: the human to name the edition and parts of the licensed copy.
3. Public repo, no licence file: where may transcribed tables live (Pitfall 3)?
4. Which tooth thickness does the solid carry (Pitfall 7): recommendation effective maximum-material.
5. Which process's `h_fP` (hobbing 0.60 by default in the only oracle): the human to choose and cite the table.
6. WR-02: untouched or taken on purpose.

## Sources

- KISSsoft 2024 non-commercial demo report "12 Spline (DIN 5480)", `W 70.00x3.00x22x6f` / `N 70.00x3.00x22x7H` (https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf): READ via `pdftotext`; the oracle rows. MEDIUM (third-party tool, 2006 edition).
- Hexagon newsletters 188 and 194 (https://hexagon.de/pdf/info188e.pdf, https://hexagon.de/pdf/info194e.pdf): series structure, Table 5 formula defect, counterpart-dependent form diameter, x = 0.45 worked example, centring-variant designation. READ. MEDIUM.
- Hexagon letter 111 (https://hexagon.de/info111/index.htm): ISO 4156 vs DIN 5480 tolerance differences. MEDIUM.
- DIN Media / din.de abstracts for DIN 5480-1:2025-08 and DIN 5480-2:2025-10 (https://www.din.de/en/getting-involved/standards-committees/nam/publications/wdc-beuth:din21:394645667, https://www.dinmedia.de/en/standard/din-5480-2/394645667), and web search summaries of the series change: edition dates, four-part series, `h_fP = 0.55 m` theoretical, Table 3, full root radius. MEDIUM (abstracts only; the standard was not read).
- eassistant handbook chapter 17 (https://www.eassistant.eu/fileadmin/dokumente/eassistant/etc/HTMLHandbuch/en/eAssistantHandbch17.html): shaft x range, hub range, measuring conventions. READ. MEDIUM.
- Engineersedge DIN 5480 calculator (https://www.engineersedge.com/calculators/din5480/din5480.html): shift limit -0.05 to +0.45. READ. LOW-MEDIUM.
- Web search summaries (calculator pages, GrabCAD, eng-tips, Ameco catalogue): `d_B = m*z + 2*x*m + 1.1*m`, designation examples. LOW alone; used only where reproduced by `CALC` or a second source. Pages returning 403 or TLS failures (eng-tips, GrabCAD) were not read.
- Local scripts (session scratchpad): `chk.py`, `chk2.py` (x*m, M_Re reproduction, theoretical pin contact radius, float edge), `proto.py`, `proto2.py`, `proto3.py` (kernel prototype timings). Not committed.
- Repo: `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `docs/architecture/decision_log.md` (L02, L03, L05, L08, L26, L38, L40, L41, L42, L43, L44, L45), `src/spur/{calc,params,model,pool,records,app,cli}.py`, `src/spur/static/app.js`, `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`.

---
*Pitfalls research for: DIN 5480 splined shaft as a second part type (spur v0.7)*
*Researched: 2026-10-23*
