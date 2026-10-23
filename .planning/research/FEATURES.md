# Feature Research

**Domain:** external DIN 5480 involute splined shaft (W-profile, flank-centred) as a second part type in an existing parametric gear generator; milestone v0.7 Splined Shaft
**Researched:** 2026-10-23
**Confidence:** MEDIUM overall. HIGH for what the standard's parts cover and which editions are current (publisher pages) and for what the commercial tools print (vendor brochures). HIGH that one published worked example reproduces from the formulas below (I ran it). LOW for every table value: none was read, none is stated here as fact, and the human's copy is the only source for them.

Evidence tags: **PUBLISHER** = DIN Media / DIN page, read 2026-10-23. **VENDOR** = a vendor's own brochure or manual page. **REPRO** = I computed it in a scratch script (not committed) against a VENDOR data point. **ASSUMPTION** = inferred, must be settled against the human's copy. The research-store seam was not used (no digest cached); web search was `WebSearch`/`WebFetch`, so provider-tier confidence is MEDIUM at best for everything not from the publisher.

---

## 1. How the field works (what the tools do)

| Tool | Input model | Printed / produced | Source |
|---|---|---|---|
| **HEXAGON WN2 / WN2+** (DIN 5480 only) | reference diameter d_B, pressure angle, module, z, tolerance field; ships a database of "all combinations of spline connections to DIN 5480 (about 700 records)" the user picks from; WN2+ adds free addendum and profile-shift factors for non-standard profiles | all production data; tooth thickness (eff. max, actual max ref., actual min); form circle; **diametral two-roller measure and span width as min, max and nominal, with measuring tooth count and roller diameter changeable**; all deviations and form/angle/runout tolerances ("all table values supplied by WN2"); drawing tables with inspection rules; DXF/IGES and STL; strength (Niemann/Hohn, Roloff/Matek) | VENDOR, `hexagon.de/pdf/wn2_d.pdf` (MEDIUM) |
| **HEXAGON WNXE** (any involute spline: ISO 4156, DIN 5480, ANSI B92.1, DIN 5482, DIN 9611) | module or pitch, z, tip/root diameters or height factors, profile shift **or** tooth thickness **or** two-roller measure **or** span (any one, the rest back-calculated) | tooth thickness, span, two-roller measure, tool dimensions, scale tooth profile for wire-EDM and 3D printing; **no tolerances** | VENDOR, `hexagon.de/pdf/wnxe_d.pdf` (MEDIUM) |
| **GWJ eAssistant** "Zahnwelle nach DIN 5480 und weiteren Normen" | choose the standard, then **search the profile by d_B, module, z, tip diameter, profile shift** (or a custom geometry); tolerance quality 5-12, deviation series (letters), actual vs effective tolerance, measuring tooth count and ball diameter; hob / shaper / constructed tool | actual tooth thickness A_s and gap A_e with limits, span W_k with A_We/A_Wi, root and tip diameters, **effective vs actual values**, diametral ball measure M_d / two-ball measure, M_dR roller measure, coordinate table, DXF, STEP/IGES, strength per DIN 6892 | VENDOR, `eassistant.eu` handbook chapter 17 (MEDIUM) |
| **MITCalc** spline | standard picked from a list, direct size input, strength coefficients | dimensions, strength check, 2D CAD output of shaft and hub profile | VENDOR via search snippet, page itself unreachable (LOW-MEDIUM) |
| **KISSsoft** | its public spline page covers DIN 5481 and DIN 5482 only; user enters "effective and actual tolerances" | graphical profile, DXF | `geartechnology.com/kisssoft-implements-spline-connections` (MEDIUM). I found no public evidence of DIN 5480 in KISSsoft; do not claim it. |
| **Catalogue shops** (Maedler, Ameco, OnDrives) | pick a designation `W 25 x 1.25 x 18` | a part; the calculator of OnDrives/MESYS takes a pair designation | search snippets (LOW) |

What this means for the shape of the feature:

1. **Two input idioms coexist.** Calculators take d_B, m, z, tolerance as fields (WN2, eAssistant). Catalogues and drawings carry the designation string. Nobody makes the user type the profile shift: **x is derived from d_B, m, z** (REPRO below). The spur app's rule (one model, three front ends) says: fields are canonical, designation is a codec in both directions.
2. **Every serious tool prints a window, not a point.** Tooth thickness and measure over rollers come as max and min, and they distinguish **effective** from **actual** (DIN 5480's effective-tolerance system, where the form deviation is carried inside the tolerance). A single "M_Re = 126.0" would be the one thing none of them print.
3. **Strength, DXF, drawing tables and the hub (N) side are what the bigger tools add**; the table-stakes core is geometry + tolerances + inspection measures.
4. **The 3D solid is not what these tools sell** (2D DXF and a scale outline are). spur's STL/STEP and live preview are already a differentiator before any new work.

---

## 2. What the standard defines, and where (edition state, 2026-10-23)

PUBLISHER facts (HIGH):

| Part | Current edition | What it is | Notes |
|---|---|---|---|
| DIN 5480-1 | **2026-05** (30 pp). 2025-10 was withdrawn and replaced | Generalities: 30 degree pressure angle, one reference profile for all pitches, flank centring (diameter centring the exception), profile shifts to reach the reference diameters, fit system with tolerances for effective form deviations. Tables 1 and 2 revised in 2025, Annex A expanded | **DIN's own warning notice (2026-01-20) corrects Annex A.2 of the 2025-10 text: `M_1min = M_1 + (A_s + T_G)*A*_M1` must read `M_1min = M_1 + (A_s - T_G)*A*_M1`.** A copy dated 2025-10 carries the wrong sign. |
| DIN 5480-2 | **2025-10** (89 pp). Replaces 2015-03 | Nominal and inspection dimensions: the per-size tables | "Table 1 'Fillet radii and dimensioning factors' has been deleted" in this edition. Where the root-fillet radii and height factors live now is unknown to me. |
| DIN 5480-15 | 2025-10 (41 pp) | Inspection: gauges and measuring procedures; "formula in the third row corrected in Table 9" | Not in the milestone's "parts 1 and 2" scope. M over rollers may be cut across parts 1, 2 and 15. |
| DIN 5480-16 | 2025-12 **draft** | Tools | A hob root defined only here would not be citable as a published standard. |

Scope figures the publisher and vendors agree on (MEDIUM): module 0.5 to 10, z 6 to 82, alpha 30 degrees. **d_B 6 to 500 mm is UNVERIFIED**: the one search that "confirmed" it echoed my query. Old pre-2006 series was one part per module (part 5 = m 1.5 and 1.75, part 10 = m 5, publisher titles), so the module list is not 0.5..10 in uniform steps; read it from the copy.

### 2a. Reproducible from public vendor data (REPRO, one data point)

HEXAGON's own demo prints, for **W 120x3x38x8f** (DIN 5480:2006 output, page 2 of `wn2_d.pdf`): hfP/m 0.55, da1 119.40 h11, dFf1 113.91 max, df1 113.40, s v max 6.243, s max act ref 6.220, s min actual 6.180, roller DM 6.000, M1maxRef 126.017, M1min 125.956; tolerance panel A_s1 -0.028, T_act 0.040, T_eff 0.023, T_G 0.063; nominal e2 = s1 = 6.271.

I computed these from textbook involute relations with x = d_B/(2m) - z/2 - 0.55 = 0.45 (script in session scratchpad, not committed):

| Quantity | My computation | Vendor | Result |
|---|---|---|---|
| nominal thickness `s = m(pi/2 + 2 x tan 30)` | 6.2712 | 6.271 | match |
| `d_f = m z + 2 x m - 2*0.55 m` | 113.40 | 113.40 | match |
| `d_a1 = m z + 2 x m + 2*0.45 m` (= d_B - 0.2 m) | 119.40 | 119.40 | match |
| M over 6.000 rollers, even z, at s = 6.220 | 126.0169 | 126.017 | match |
| same at s = 6.180 | 125.9560 | 125.956 | match |
| `s_eff,max = s + A_s = 6.271 - 0.028`; `s_act,min = s + A_s - T_G` = 6.180 | 6.243; 6.180 | 6.243; 6.180 | match; same sign structure as DIN's corrected Annex A.2 |
| form diameter d_Ff: tangent point of a hob tip arc rho = 0.16 m on the 30 degree flank | 113.880 | 113.91 | **no match (0.03 mm)**. rho = 0.17 m gives 113.910, but WN2's own dialog shows rho_f/m = 0.16 for the shaft. Unresolved. |

Reading: tooth thickness, root and tip diameters and M over rollers are **derivable and independently checkable** (x range consistent too: -0.05..+0.45, which for 25 / 1.25 gives z in {18, 19}, and the milestone's own example is z = 18 at x = 0.45). The **form diameter is not**: do not promise `d_Ff` until the standard's construction is read. Treat all of the above as ASSUMPTION until the same relations are confirmed from the human's copy with clause numbers; the vendor row is a cross-check vector, not a source.

### 2b. Needs the tables (human's copy), do not guess

- Tolerance deviations: the fundamental deviation A_s and tolerance T (actual, effective/form allowance, total T_G) per quality (vendors disagree on the range, 5-12 by eAssistant, 4-9 by a workshop article: **read it**) and per deviation letter (shaft letters a..v per eAssistant, hub F..M, also unverified). Whether they are tabulated per d_B and m ranges or formula-based: unknown (ASSUMPTION: tabulated, since WN2 says "all table values are supplied").
- Roller/ball diameter D_Re (WN2 example 6.000 for m = 3, shaft; 5.250 hub): per size or per module, unknown. If per module, the transcription is small; if per size it is part 2's 89 pages.
- Whether a listed size is required: ~700 standard (d_B, m, z) records exist (VENDOR). The x window above means a (d_B, m) pair admits at most two z.
- Root form: fillet radius and height factors (WN2+ dialog: rho_f/m 0.16 shaft, 0.2 hub; hfP/m 0.55; ha/m 0.45 for the shaft), and the form diameter construction. See 2025 deletion of the part-2 table.
- Where tolerance on d_a (h11 in the vendor demo) and d_f (shown "-1.15") come from.

---

## 3. Feature Landscape

### Table Stakes (users expect these)

| Feature | Why Expected | Complexity | Notes / dependency on existing |
|---|---|---|---|
| Shaft part type with its own sibling parameter model | Product widened by a new `Lxx`; every tool treats shaft and hub as distinct objects | MEDIUM | New model beside `GearParams`, validated once at its own boundary. Touches L02 ("one parameter model") by amendment, not new `GearParams` fields (L26 fixture stays byte-identical). |
| Inputs as fields: d_B, module, z, tolerance quality, deviation letter, plus shank (d, length), splined length, end chamfer | WN2, eAssistant | LOW | Profile shift is **derived, never an input**; validate that derived x lies in the standard's window, else 422 naming the fields (L03, direct conflict). |
| Designation printed **and** accepted, round-tripping (`W 25x1.25x18x8f`) | Drawings, catalogues, brief | MEDIUM | A codec over the fields, not a second source of truth. If both designation and fields arrive and disagree: 422. Parse: `x`/`×`, decimal point or comma, optional `DIN 5480 -` prefix, case-insensitive W; print one canonical form. Reject ISO-style `f8` ordering rather than guess. Property test: parse(print(p)) == p. |
| Basic dimensions: d_B, reference d, x, tip d_a, root d_f, tooth thickness s | All tools | LOW-MEDIUM | Formulas reproduce (2a) once confirmed in the copy; pure maths in a new module with no `cadquery` import (import-boundary contract). Reuse `inv()`, the involute point and `Profile.half_angle` ideas from `calc.py`; **do not reuse `_dedendum`/`cutter`/`profile`** unchanged, they take `GearParams` and hard-code the 1.25 m dedendum. |
| Tooth-thickness window: effective max, actual max, actual min, A_s, T_G | DIN 5480's effective-tolerance system; every tool | MEDIUM | Values need the tolerance tables; transcription with clause/table citation and second read. Outside the tables: warning and null (L08). |
| Measure over rollers/balls M_Re, max and min (and nominal), with the roller diameter D_Re it assumes | WN2, eAssistant, brief | MEDIUM | Even and odd z differ (diametrically opposite vs offset roller, `cos(90/z)`). Proved against an independent oracle (REPRO shows a closed form agrees to 1e-3). Print D_Re next to M_Re, since a number without its roller is unusable. Mind the Annex A.2 erratum. |
| Form diameter d_Ff | brief; WN2 prints it | HIGH (until construction known) | See 2a: not reproduced. If the construction cannot be settled from the copy, print a warning and **no number** (L08). Do not ship a plausible value. |
| Solid: splined section (hob root), step, plain shank, end chamfer; STL and STEP | the product | MEDIUM-HIGH | New build path in `model.py` (kernel stays inside it, vendor types stop at the boundary). Spline outline can reuse the trochoid-root machinery's concept (`Cutter`, `trochoid_root`, swept-cutter oracle, `xi` form roll) but needs a cutter with hfP = 0.55 m and 30 degrees: generalise or fork, decision for discuss/plan. End chamfer is a revolve-cut cone; L29's tip-chamfer code is gear-face specific. |
| Say what size the solid is | an honest tool | LOW | The solid is built at one stated tooth thickness (recommend effective max, i.e. s + A_s, the max-material limit), printed as such; never leave "nominal" implied. User decision at discuss-phase. |
| Warnings instead of numbers outside the tables or when uncomputable | L08 | LOW | Reuse the `warnings` tuple pattern; a new typed result model (`ShaftDimensions`) with every key always present, `null` where it does not apply. |
| Parity: live preview, numbers, STL/STEP from web UI, HTTP API and CLI | brief, REQ-three-interfaces | HIGH | Cross-cutting: a part-type discriminator through `/api/schema`, `/api/info`, `/api/model.{fmt}`, CLI subcommands, form generation, share links, download slug (L40: no cache keyed by slug), pool hash-affinity routing and both caches, and the browser test's per-fixture request pins (L39). Existing gear links must build and send exactly what they do now (L05). |
| Shareable link for the shaft | REQ-shareable-links | LOW-MEDIUM | Same URL-hash mechanism; defaults absolute mm (L05). Bad enum or out-of-range link is sent and refused by the 422 (L44). |
| Defence against bad geometry: shank vs tip/root diameters, spline length vs total, chamfer vs spline length | build safety | MEDIUM | Cap-and-warn only where nothing explicit is contradicted (L03); direct conflicts 422. Each gets a measured build time under `SPUR_BUILD_TIMEOUT`. |

### Differentiators (competitive advantage)

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| A live 3D shaft with the printed numbers next to it | None of WN2/WNXE/eAssistant/MITCalc leads with a printable solid | (covered above) | WNXE does emit 3D-printing outlines only as 2D. |
| Numbers proved against the **built solid**, not only against formulas | Matches the project's culture ("read back on the built solid within 1e-6 mm") | MEDIUM | Measure over simulated rollers on the kernel result; compare to M_Re within a stated tolerance. Independent of the closed form. |
| Independent oracle for each printed value | Core Value; the one differentiator that fits "a number is a number someone cuts metal to" | MEDIUM | Use the vendor demo above as a cross-check vector (not a source), plus 2 to 3 rows from the copy chosen by the human. Oracle shares no code with the implementation. |
| Span (base tangent) W_k alongside M_Re | WN2/eAssistant print it; calipers are cheaper than rollers | LOW-MEDIUM | Existing `span_measurement(p)` is gear-typed; the maths is the same family. k comes from the standard; ASSUMPTION that DIN 5480 gives a measuring tooth count. |
| Citation per number | Unique among the tools: each tolerance value carries its clause/table | LOW | Metadata beside the transcribed table; shows in the docs, optionally in the response. |
| DIN-style "drawing table" text block of the same numbers | WN2 makes drawing tables | LOW | A formatter over `ShaftDimensions`; no new numbers. Defer past v0.7 core. |
| Hob-cut root through the same trochoid proof as the gear | Reuses L38's proven root; one root story across the product | MEDIUM-HIGH | Only after the standard's root form is read; otherwise radial root with a warning. |
| Mating hub (N) numbers and clearance (c_v min/max, WN5 prints them) | Fit is the point of the standard | HIGH | Needs the hub tables too. Later milestone. |
| Warning on the tooth-to-shank transition | A workshop article reports notch factors 3-5 without a relief groove (DIN 509) | LOW | A single sentence in `warnings`; no groove in v0.7. Source is a vendor/workshop article (LOW-MEDIUM). |
| 2D profile DXF | WN2/WNXE/eAssistant all export it | MEDIUM | Not requested. Park in `docs/ideas/`. |

### Anti-Features (commonly requested, often problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| Strength / torque capacity (Niemann, DIN 6892, Roloff) | Every commercial tool has it | A load number is exactly "a number someone loads"; needs materials, K factors, load distribution; unverifiable here; L08 | Out of scope; state so. |
| Inventing or interpolating table values outside the copy | Covers more sizes | Silent wrong numbers; violates the milestone rule and L08 | Warn, null; only transcribed values ship. |
| Snapping a non-standard (d_B, m, z) to the nearest standard size | Forgiving | A parameter the user set changing the part (L03, L05) | 422 naming the fields. |
| Non-standard profiles with free addendum / profile shift (WN2+ "Sonderverzahnung") | Flexible | Breaks "every number from the standard"; a second product | Not in v0.7. |
| Diameter-centred fit, hub (internal) spline, ISO 4156 / ANSI B92.1, DIN 5481 / 5482, ISO 14 | "Full spline support" | Each is a family with its own tables; the brief queues one family per milestone | Flank-centred external W only (ASSUMPTION). |
| Extra print-clearance / offset field that moves the tooth | Printer users want a tuned fit | Moves s and M_Re away from the standard; numbers must follow or lie; new field | Defer. If added: M_Re and s computed at the offset or null. |
| Accepting ISO-style `f8` / hub `H9` designations | Looks friendly | Order-of-letters ambiguity; round-trip breaks | Print and accept DIN's `8f` only. |
| Helical / worm-like splines, relief groove (DIN 509), hardened-zone modelling | Real shafts have them | Separate standards and decisions | Warning sentence only. |

---

## 4. Feature Dependencies

```
Tables transcribed from the human's copy (clause/table cited, second read)
    |--requires--> human supplies the local path (milestone blocker)
    |--requires--> decide: per-size tables vs per-module tables vs formulas
    |--enables---> tolerance window (A_s, T, T_G) --enables--> M_Re max/min, s limits
    '--enables---> D_Re --enables--> M_Re

Basic dimensions (x, d_a, d_f, s)      -- needs only formulas (confirm in copy)
    |--enables--> designation codec (validates x window)
    |--enables--> solid outline (involute flanks)
    '--enables--> M_Re nominal, span

Root form (rho_fP, hfP, d_Ff construction) --requires--> copy (2025-10 deleted the part-2 table)
    |--enables--> d_Ff
    '--enables--> hob-cut root in the solid (else radial root + warning)

Sibling shaft model --requires--> part-type discriminator through schema/info/model/CLI/UI
    |--requires--> amendment to L02 and the product-scope Lxx
    '--conflicts--> any change to GearParams, tests/regression/pre_v0_2.json (L26)

Built-solid proof --requires--> solid + M_Re closed form (two independent paths)
Drawing table, DXF, hub N, strength   --depend on--> everything above; deferred
```

### Dependency Notes

- **Tables block three things, not all of them.** Geometry, codec, solid shape and the x window need only formulas and can go first (confirm each in the copy). Tolerance window, D_Re, M_Re limits and probably d_Ff wait on the copy. A phase order that builds the geometry and the part-type plumbing while the path is outstanding avoids idling.
- **The designation depends on the tolerance letters being known** to validate `8f`; until the table is in, the codec can parse and round-trip but must report the field "cannot be checked" rather than accept anything.
- **Parity is the expensive part**, not the maths: the gear is assumed throughout (`GearParams`, `DerivedDimensions`, `app.js`'s `gearQuery()`, the model cache key, the slug, CLI flags generated from the model). WR-02 (`refuse()` / `gearQuery()`) is carried in "on its own trigger" and will fire the moment those functions are edited for a second part type.
- **Existing machinery to keep out of the way:** `calc.py` must not import `cadquery`; vendor types stop at `model.py`; the 44-record fixture is untouched.

---

## 5. MVP Definition

### Launch With (v0.7)

- [ ] Part-type plumbing and the sibling `ShaftParams`/`ShaftDimensions`, parity on all three interfaces, share link, preview and STL/STEP of the shank + spline + chamfer solid (radial root, stated so).
- [ ] Basic dimensions from formulas (d_B, d, x, d_a, d_f, s), each with an independent oracle and the vendor vector as a cross-check.
- [ ] Designation codec, round-trip tested, x-window validation as 422.
- [ ] Tolerance window (A_s, T_G, s eff max, s act min) and M_Re max/min with D_Re from the copy; M_Re proved against an oracle and against the built solid.
- [ ] Everything not in the tables: warning, no number.

### Add After Validation (v0.7.x / next)

- [ ] d_Ff and the hob-cut root once the construction is read and reproduces (2a) - trigger: copy read, vendor vector reproduced to 0.005 mm.
- [ ] Span W_k - trigger: the copy gives k.
- [ ] Drawing-table text block.

### Future Consideration (v0.8+)

- [ ] Hub (N) and fit clearance; ISO 4156 / ANSI; DIN 5481 / ISO 14 serrations (one family per milestone, per the brief).
- [ ] DXF profile, print-offset field, relief groove.

---

## 6. Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Part-type plumbing + parity | HIGH | HIGH | P1 |
| Basic dimensions + oracle | HIGH | LOW-MEDIUM | P1 |
| Solid (spline, shank, step, chamfer) | HIGH | MEDIUM-HIGH | P1 |
| Designation codec | HIGH | MEDIUM | P1 |
| Tolerance window + M_Re max/min | HIGH | MEDIUM (gated on copy) | P1 |
| Built-solid proof of M_Re | MEDIUM-HIGH | MEDIUM | P1 |
| Form diameter d_Ff | MEDIUM | HIGH until construction known | P2 |
| Hob-cut root | MEDIUM | MEDIUM-HIGH | P2 |
| Span W_k | MEDIUM | LOW-MEDIUM | P2 |
| Drawing-table block | LOW-MEDIUM | LOW | P3 |
| DXF, hub, clearance, print offset | MEDIUM | HIGH | P3 |
| Strength | n/a (anti) | n/a | none |

---

## 7. Competitor Feature Analysis

| Feature | WN2 | eAssistant | WNXE | Our approach |
|---|---|---|---|---|
| Input | d_B, m, z, tolerance, database of ~700 | search by d_B/m/z/da/x or custom | m, z + any of x/s/M/W | fields canonical, designation codec, x derived |
| Tolerances | all, from tables | actual and effective, quality 5-12 | none | transcribed from the copy, cited, null outside |
| Measures | M over rollers and span, min/max/nom | M_d, M_dK, M_dR, W_k | s, W, M | M_Re window first, span later |
| Output | numbers, drawing, DXF/IGES, STL | numbers, DXF, STEP/IGES, GDE | numbers, DXF | numbers + STL/STEP + live preview |
| Strength | yes | yes (DIN 6892) | no | no (anti-feature) |
| Hub | yes | yes | yes | no (later) |

---

## 8. Open questions for the human (before the tables phase)

1. Edition of the copy: DIN 5480-1 **2026-05** (corrected) or **2025-10** (A.2 sign error)? DIN 5480-2 2025-10? Is **part 15** also in hand (inspection, "corrected Table 9")?
2. Where in the copy are the tolerance deviations and tolerance values, the roller diameter D_Re, and the root-fillet radii (the 2025-10 part 2 deleted its fillet table)? Per size, per module, or formula?
3. Which sizes does the copy list (d_B range, module list), and may a combination absent from the table be built (recommend: 422 in v0.7)?
4. What tooth thickness should the solid carry: effective max (recommended), nominal, or mid-window?
5. Does the standard define the form diameter's construction and its tolerance (the 0.03 mm gap in 2a)?

## Sources

- DIN Media, DIN 5480-1:2025-10 (withdrawn) and 2026-05 listing: `https://www.dinmedia.de/en/standard/din-5480-1/394645155`, `https://www.dinmedia.de/en/standard/din-5480-1/399672170` (PUBLISHER, HIGH)
- DIN Media, DIN 5480-2:2025-10, 89 pp, replaces 2015-03: `https://www.dinmedia.de/en/standard/din-5480-2/394645667`, also `https://www.din.de/en/wdc-beuth:din21:394645667` (HIGH)
- DIN Media, DIN 5480-15:2025-10: `https://www.dinmedia.de/en/standard/din-5480-15/394645765`; DIN 5480-16 draft via search results (HIGH / MEDIUM)
- DIN warning notice 2026-01-20 on DIN 5480-1:2025-10 Annex A.2: `https://www.dinmedia.de/en/fachdaten-einzelsicht/wdc-beuth:din21:399323168/infoPdf-download` (PUBLISHER, HIGH)
- HEXAGON WN2/WN2+ brochure (incl. the W 120x3x38x8f example): `https://www.hexagon.de/pdf/wn2_d.pdf`; WNXE: `https://www.hexagon.de/pdf/wnxe_d.pdf`; WN5: `https://hexagon.de/info111/index.htm` (VENDOR, MEDIUM)
- GWJ eAssistant handbook ch. 17: `https://www.eassistant.eu/fileadmin/dokumente/eassistant/etc/HTMLHandbuch/de/eAssistantHandbch17.html` (VENDOR, MEDIUM)
- KISSsoft spline note: `https://www.geartechnology.com/kisssoft-implements-spline-connections` (MEDIUM)
- Workshop article on fits and relief grooves: `https://dswerk.de/kerbverzahnung-zahnwellen-din-5480/` (LOW-MEDIUM)
- Catalogue designation format: Maedler / Ameco / OnDrives product listings for "W 25 x 1.25 x 18" (LOW; several pages unreachable)
- MITCalc, grabcad "Tolerances in DIN 5480 splines" and eng-tips threads: reached only as search snippets or HTTP 403/404 (LOW; used for the effective/actual concept only)
- Existing code read for dependency notes: `src/spur/calc.py` (`Profile`, `_dedendum`, `cutter`, `span_measurement`, `DerivedDimensions`), `src/spur/params.py`, `docs/architecture/decision_log.md` (L02, L03, L05, L08)

---
*Feature research for: DIN 5480 external splined shaft, spur milestone v0.7*
*Researched: 2026-10-23*
