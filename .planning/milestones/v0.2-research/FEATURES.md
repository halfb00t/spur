# Feature Research: Fit to Shaft (v0.2)

**Domain:** Parametric CAD gear generator — bore profiles, body cutouts, tip chamfer
**Researched:** 2026-09-25
**Confidence:** MEDIUM overall — keyway/ISO dimensional data is cross-source-consistent
(MEDIUM); body-cutout proportions and tip-chamfer sizing have **no citable engineering
standard** and are correctly graded LOW — this is the single most important finding for
the requirements step: don't let a "sensible default" masquerade as a standard.

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Keyway bore (explicit width/depth/clearance) | The single most common shaft-mount feature outside a round/D-flat bore; every comparable tool (3d-editor.com, Eng Bench, GearWorkBench for FreeCAD) offers it | MEDIUM | Boolean-subtract a rectangular prism from the round bore cylinder, radially outward from the bore wall; composes with `bore_chamfer` on the round part only (chamfering a keyway corner is not conventional and is out of scope) |
| Hex bore (across-flats + clearance) | Common for RC/robotics/DIY shafts (5 mm, 1/4", 3/8", 1/2" hex stock is a commodity item) and for printed parts that want a wrench-flat drive without a key | LOW-MEDIUM | A regular hexagon prism subtracted from (or replacing) the round bore; simpler than the keyway because it's one convex profile, no floor fillet to reason about |
| Tooth-tip chamfer | Standard practice in both metal-cut and 3D-printed gears to break the sharp tip edge — reduces snagging/burrs and, for FDM, the tip is the most overhang-prone, defect-prone feature on the part | LOW-MEDIUM | Conical chamfer on the tip circle edges (top and/or bottom face), same shape as the existing `bore_chamfer` pattern in `params.py`/`model.py` — reuse that convention, not a new one |
| Circular lightening holes on a bolt circle | The most common weight-reduction feature in flywheels, pulleys and large gears; visually and functionally simple, easy to reason about wall thickness (same `MIN_WALL` logic already used for bore/recess) | LOW-MEDIUM | N holes evenly spaced on a bolt circle between hub and rim; needs the same "capped, not refused, with a warning" fit logic as `recess_radii()` |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Explicit-parameter keyway (no standard-table lookup) | Nearly every comparable tool that offers a keyway (Eng Bench: "cuts a standard parallel keyseat sized to DIN 6885-1 from the bore diameter") *derives* width/depth from bore Ø via a table lookup baked into the tool. `spur`'s decision — width, depth, clearance are all explicit fields the user reads off the actual shaft — is a genuine differentiator that matches the project's Core Value ("a number this tool prints is a number someone will cut metal to"): a wrong or superseded lookup table would silently produce a cut nobody asked for | LOW (once the geometry exists) | The differentiation is the *absence* of a lookup, not extra geometry — cheap to build, valuable to state clearly in the UI help text so users don't assume DIN sizing is happening for them |
| Spoke-arm / hexagonal-honeycomb body cutouts | Not offered by any of the researched comparable tools (FreeCAD's FCGear/GearWorkBench, BOSL2 gears.scad, Fusion 360 add-ins, geargenerator.com family) beyond simple lightening holes; only BOSL2's `gears.scad` even mentions "lightening holes" as a named feature. A honeycomb-pattern web with a build-time cap is unusual for a gear generator and plays to the "prints light" goal | HIGH (honeycomb: cell tiling + per-cell fit-or-drop logic + timeout-aware count cap) | This is where v0.2 goes beyond table stakes; the honeycomb cell count is explicitly capped-and-warned per the milestone brief, so treat it as the feature most likely to need its own build-time budget research (flagged in PITFALLS) |
| Composability (cutout + recess + bore, one part) | Comparable web generators (3d-editor.com, geargenerator.com family) offer bore + keyway + lightening holes as **alternatives**, not composed on the same part with face recesses; none of the researched tools advertise "recess floor stays filleted under a spoke cutout" as a guarantee | MEDIUM-HIGH (this is a geometry-ordering and edge-case problem, not new shapes) | The real cost is here, not in any single new cut — see Feature Dependencies below |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|------------------|-------------|
| Standard-table keyway sizing (auto-fill width/depth from bore Ø per DIN 6885/ANSI B17.1) | Feels convenient — "just tell me the shaft size" — and is what Eng Bench and other online generators already do | A looked-up number is a number someone cuts metal to (Core Value); DIN 6885 and ANSI B17.1 give **different numbers under different conventions** for the same nominal shaft (see Pitfalls) — baking one in without disclosing the standard and its datum silently commits the user to a convention they didn't choose. Already rejected by the human for this exact reason (PROJECT.md) | Explicit width/depth/clearance fields, `help=` text citing DIN 6885/ANSI B17.1 **ranges only** as a sanity check ("typical width for a 12 mm shaft is 4 mm, DIN 6885") — never write the number into the default |
| Spline bore (DIN 5480 etc.) | Looks like a natural sibling to keyway/hex once those exist | Already explicitly out of scope for v0.2 in PROJECT.md — "a standards surface (DIN 5480 and kin, many variants), not a cut"; multiple incompatible sub-standards, no single sane default | Keyway + hex cover the shafts a hobbyist actually has; leave spline as a v0.3+ candidate |
| Auto-derived spoke count / arm width from gear size | Feels like it should follow a formula the way tooth geometry does | **No standard exists** to derive it from (see Pitfalls) — any formula the tool invents is an opinion presented as a fact, which breaks the same Core Value the keyway decision protects | Explicit arm count + arm width fields, capped to fit like `root_fillet`/`recess_width` already are, with a warning when capped |
| Tip chamfer as a percentage of tooth height or an involute "tip relief" curve | Tip relief (a genuine gear-engineering technique — a slight profile modification near the tip to reduce impact loading at engagement) sounds more sophisticated than a flat chamfer | Tip relief is a *meshing* modification computed from load, speed and manufacturing tolerance (AGMA-class analysis) — an entirely different, much heavier feature than an edge-break chamfer, and not something `spur`'s stated feature ("Tooth-tip chamfer — the bore chamfer already ships") is asking for | A straight conical chamfer in mm, following the exact pattern `bore_chamfer` already uses — cosmetic/printability edge-break, not a meshing correction; don't conflate the two under one name |

## Feature Dependencies

```
Keyway bore ──requires──> round bore (bore_d > 0)
Hex bore ──requires──> round bore (bore_d > 0), OR replaces it as an alternate bore profile
Keyway bore ──conflicts──> Hex bore (one bore profile per part — pick one, refuse the combination as a 422)

Spoke-arm cutout ──requires──> a defined hub region (bore or bore_d=0 solid hub) and a defined rim (root diameter)
Lightening-hole cutout ──requires──> a bolt circle that clears both hub wall and rim wall (same MIN_WALL logic as recess_radii())
Hexagonal-pattern cutout ──requires──> a web area larger than a few cells, and a build-time budget (cell count must be capped)

Spoke-arm / lightening-hole / hexagonal cutouts ──conflict with each other?──> NO in principle (arms and holes can coexist geometrically), but the milestone brief scopes them as three separate cutout *types*, not a composable set within one gear — treat "more than one cutout type on one part" as an open question for requirements, not assumed in scope

Any body cutout ──composes with──> face recess (cuts through the recessed floor, floor fillet intact per PROJECT.md)
Any body cutout ──composes with──> any bore profile (round / D-flat / keyway / hex)
Tooth-tip chamfer ──independent of──> all of the above (acts on the tip circle edges only, never touches bore/body/root)
```

### Dependency Notes

- **Keyway/hex bore conflicts with each other:** a bore is one profile. `bore_flat` (D-flat) already coexists with `bore_d` in the shipped model as a second cut on the same round bore — keyway and hex should follow the same shape (an addition to the round bore, not a replacement of it) *unless* the requirements step decides hex fully replaces the round profile the way D-flat does. This is a naming/composition decision the requirements step needs to make explicitly, not infer.
- **Body cutouts require a defined hub and rim:** all three cutout types (spoke, lightening-hole, honeycomb) need to know where the "web" is — the annular region between the bore/hub wall and the tooth root, same region `recess_radii()` already reasons about. Reuse that boundary logic rather than re-deriving it.
- **Body cutout composes with face recess:** PROJECT.md states this explicitly — "cutouts combine with face recesses (cut through the recessed floor, floor fillet intact)". This means cutout depth must be allowed to exceed `recess_depth` (cutting all the way through the part) while the recess's own floor fillet geometry stays intact where the cutout doesn't reach — a CAD boolean-ordering concern (cut the cutout through the full solid, including the recess floor, rather than cutting the recess into an already-cut cutout) more than a parameter concern.
- **Honeycomb count depends on the build-time budget, not the user:** the milestone brief is explicit that cell count "follows from the web area and is capped and warned when the build cannot fit the timeout" — this is the one cutout whose *count* is not a first-class user parameter (cell size and wall thickness are; the resulting count is derived and can be trimmed). This is architecturally different from spoke arms and lightening holes, which get an explicit user-set count per PROJECT.md.
- **Tip chamfer has no dependency on anything else** — it is the lowest-risk new feature in the milestone, both geometrically (identical pattern to the shipped `bore_chamfer`) and in scope (no standard to misapply, no composition ambiguity).

## MVP Definition — mapped to PROJECT.md's already-committed v0.2 scope

PROJECT.md has already fixed the v0.2 feature set (below); this section maps the
researched risk/complexity onto that fixed list rather than re-deriving a new MVP, since
the milestone scope is a locked decision (`.planning/PROJECT.md`, "Target features"), not
an open question for this research.

### In v0.2 (already committed)

- [x] Keyway bore, explicit width/depth/clearance — LOW-MEDIUM complexity, the datum
  ambiguity below is the main risk, not the geometry
- [x] Hex bore, across-flats + clearance — LOW-MEDIUM complexity, simplest of the new bore
  profiles
- [x] Tooth-tip chamfer — LOW-MEDIUM complexity, reuses the `bore_chamfer` pattern exactly
- [x] Spoke-arm cutout, explicit arm count — MEDIUM complexity, no standard proportions to
  cite (engineering-judgment defaults only, sanity-capped like `root_fillet`)
- [x] Circular lightening-hole cutout, explicit hole count on a bolt circle — LOW-MEDIUM
  complexity, closest analogue to the shipped `recess_radii()` fit logic
- [x] Hexagonal-pattern cutout, cell size + wall thickness, count derived and capped to the
  build timeout — HIGH complexity, the one feature needing its own measured build-time
  budget (recess + hex pattern is the milestone's named "unknown")

### Explicitly out of scope for v0.2 (per PROJECT.md, do not re-litigate)

- [ ] Spline bores (DIN 5480 and kin) — deferred, "a standards surface... not a cut"
- [ ] Standard-table keyway sizing — rejected on Core Value grounds, not deferred
- [ ] Tip relief (meshing-load profile modification) — a different feature from tip
  chamfer; not asked for, don't build it under this name

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|----------------------|----------|
| Tooth-tip chamfer | MEDIUM | LOW | P1 |
| Hex bore | HIGH | LOW-MEDIUM | P1 |
| Keyway bore | HIGH | MEDIUM | P1 |
| Lightening-hole cutout | MEDIUM | LOW-MEDIUM | P1 |
| Spoke-arm cutout | MEDIUM | MEDIUM | P1 |
| Hexagonal-pattern cutout | LOW-MEDIUM (niche, but a differentiator) | HIGH | P2 (build first, but plan for it to need its own build-time research spike) |

All six are already committed in PROJECT.md; this matrix is for phase-ordering guidance
(cheapest/lowest-risk first), not for cutting scope.

## Standards Cited — Keyway (the datum ambiguity, in detail)

**DIN 6885-1 / ISO R773 / JIS B1301 / UNI 6604 — same numeric table, different document
names.** Cross-checked across multiple independent sources (engineeringhardware.com,
jwwinco.com technical PDF, ganternorm.com catalog, nexusseals.com's own citation of
ISO/R773 — MEDIUM confidence, cross-source-consistent):

| Shaft Ø range (mm) | Key b × h (mm) | t1 shaft depth (mm) | t2 hub depth (mm) |
|---|---|---|---|
| 6–8 | 2 × 2 | 1.2 | 1.0 |
| 8–10 | 3 × 3 | 1.8 | 1.4 |
| 10–12 | 4 × 4 | 2.5 | 1.8 |
| 12–17 | 5 × 5 | 3.0 | 2.3 |
| 17–22 | 6 × 6 | 3.5 | 2.8 |
| 22–30 | 8 × 7 | 4.0 | 3.3 |
| 30–38 | 10 × 8 | 5.0 | 3.3 |
| 38–44 | 12 × 8 | 5.0 | 3.3 |
| 44–50 | 14 × 9 | 5.5 | 3.8 |
| 50–58 | 16 × 10 | 6.0 | 4.3 |
| 58–65 | 18 × 11 | 7.0 | 4.4 |
| 65–75 | 20 × 12 | 7.5 | 4.9 |
| 75–85 | 22 × 14 | 9.0 | 5.4 |
| 85–95 | 25 × 14 | 9.0 | 5.4 |
| 95–110 | 28 × 16 | 10.0 | 6.4 |

Both t1 (shaft) and t2 (hub) are **radial cut depths, each measured from its own
surface** (shaft OD, or bore ID) to the keyway floor. `t1 + t2 ≈ h` plus a small
clearance. This is the sane, directly-cuttable convention — exactly what `spur`'s single
`keyway_depth` field for the hub-side cut should mean, stated in the field's `help=` text
so a user who read a DIN table off a shaft catalog knows the depth they're typing is the
bore-wall-to-floor distance.

**ANSI B17.1-1967 (R1998) — a genuinely different convention, not just different
numbers.** Cross-checked across engineersedge.com and amesweb.info (MEDIUM confidence,
consistent across both): ANSI's control values **S** (shaft) and **T** (hub) are *not*
radial cut depths at all — they are **diametral gauge/inspection dimensions**: "the
distance from the bottom of the shaft keyseat to the opposite side of the shaft" (S), and
"the distance from the bottom of the hub keyway to the opposite side of the hub bore" (T).
These exist so a machinist can check keyway depth by dropping a pin or rod into the slot
and measuring across the full diameter with calipers or a micrometer — not because the
depth itself is defined that way. **This is the classic ambiguity the research question
flags, confirmed real**: converting an ANSI S/T value to an actual radial cut depth
requires `(shaft OD − S)` arithmetic, not using S directly. A tool that lets a user read
a number off an ANSI table and type it into a "depth from bore wall" field cuts the wrong
part.

**Implication for `spur`'s parameter design:** `keyway_depth` (and any sanity-range help
text) must say explicitly **"measured radially from the bore wall to the keyway floor
(the DIN 6885 / ISO R773 t2 convention)"** — and must not cite ANSI B17.1's S/T numbers
as if they were directly usable in the same field, because they are not the same
quantity. If ANSI-style ranges are also offered as a sanity check, they need their own
clearly-labelled conversion, not a shared table.

## Standards Cited — Hex Bore

No single "hex bore for gears" standard was found; hex bores follow commodity hex-stock
sizes rather than a dimensional standard the way keyways do (LOW confidence — no
authoritative source located, only commercial size charts for hex shafting/robotics
stock, e.g. REV Robotics' 5 mm and 1/2" hex shaft lines, and generic "wrench size" /
width-across-flats references for hex fasteners, ISO 272, which is a different
application). **Recommendation:** treat across-flats as a free mm field (matching the
project's existing all-mm convention) with commodity sizes (5, 6, 8, 10, 12.7 mm / 1/4",
3/8", 1/2") offered as UI presets or examples in help text, not as a cited standard —
because there isn't one to cite for gear hex bores specifically. Say so in the parameter
help text rather than inventing a standard's name.

## Standards Cited — Body Cutouts (spoke, lightening-hole, honeycomb)

**No DIN/ISO/AGMA standard governs spoke count, arm width, hub/rim wall proportions,
lightening-hole count, or bolt-circle placement for a gear web** (LOW confidence by
design — this is the honest finding, not a gap in the research). Dudley's *Handbook of
Practical Gear Design and Manufacture* covers spoke/web stress analysis as an FEA/design
problem, not a lookup table. A cited academic paper (Kaya & Ozturk or similar, "AIAC-2019-
155: Optimization of Lightening Hole on a Spur Gear of an Aircraft Motor",
aiac.ae.metu.edu.tr) treats hole radius, position and count as free optimization
variables — confirming these are computed-per-application, not standardized. **Implication:**
`spur` should treat spoke/lightening-hole/honeycomb dimensions exactly like `root_fillet`
and `recess_width` already are — user-set values, capped silently to what fits (`MIN_WALL`),
with a warning when capped — and should not claim a standard backs the defaults. This is
consistent with, and reinforces, the milestone's own decision to reject standard-table
keyway sizing.

**Honeycomb infill cell size / wall thickness:** no gear-specific standard exists; the
closest available convention is from 3D-printing infill literature (not a standard body,
LOW confidence) — hexagonal honeycomb wall thickness of roughly 0.5–1.3 mm (0.020"–0.050")
for cell pitches from a few mm up to ~25 mm is a commonly cited practical range for
FDM-printed cellular structures, thicker walls trading weight savings for stiffness. This
is design guidance from the additive-manufacturing literature, not a cross-reference
standard the way DIN 6885 is for keyways — cite it as "typical practice," not "standard."

## Standards Cited — Tooth-Tip Chamfer

**No single named standard gives a chamfer-size-vs-module rule** (LOW confidence — the
research question's own suggested range, 0.1–0.2 × module, was not independently found in
any source located during this research; it should be treated as a plausible engineering
guess worth validating with the human, not as a sourced convention). What *was* found,
consistently, across 3D-printing-focused sources (sovol3d.com, sculpteo.com,
engineerdog.com — LOW-MEDIUM, consistent with each other but all secondary/blog sources,
not standards bodies): a **flat, small edge-break chamfer** (commonly cited as ~0.5 mm ×
45° for FDM-scale gears) on the tip corners is standard practice to prevent snagging and
reduce print-tip defects — explicitly *not* the same thing as **tip relief**, which is a
load/meshing-driven profile modification (AGMA-class analysis, out of scope per the
Anti-Features table above). KHK's technical literature separately documents
"semitopping" — a chamfer cut into the tooth top corner during hobbing, primarily to
prevent burrs — as an established manufacturing practice, supporting that a tip chamfer as
an edge-break (not a meshing correction) is legitimate, conventional gear practice, just
without a single numeric standard to cite. **Recommendation:** default the chamfer size as
an absolute mm value (matching every other length in `GearParams`, per L05) with the
`0.1–0.2 × module` range offered only as a *derived sanity suggestion* in help text or UI,
explicitly labelled as project convention, not a cited standard — and confirm the exact
default with the human before treating it as locked, since it could not be sourced.

## Comparable Tools — What They Offer

| Tool | Bore options | Body cutouts | Chamfer | Notes |
|------|--------------|--------------|---------|-------|
| **FreeCAD FCGear** (`looooo/freecad.gears`) | Round only, natively | None built in | Not found | Official/most-used FreeCAD gear workbench; keyway/hex explicitly requires exporting a round bore and post-processing in other CAD (per a tutorial found in research) — confirms round-only is the practical floor even for a mature open-source tool |
| **FreeCAD GearWorkBench** (`iplayfast/GearWorkBench`, newer/less established) | Circular, square, hexagonal, DIN 6885 keyway | Not confirmed | Not confirmed | Directly comparable ambition to `spur`'s v0.2 bore scope; worth a closer look as a peer implementation if the team wants a second reference, but confidence on its actual behavior is LOW (README-level claims only, not verified against source) |
| **BOSL2 `gears.scad`** (OpenSCAD library) | Round bore | "Lightening holes" named as a feature | Not found | The only researched library besides `spur`'s own plan that names lightening holes explicitly; no spoke or honeycomb equivalent found |
| **Fusion 360 add-ins** (GF Gear Generator and similar) | Round bore | None found | Not found | Consumer/hobbyist add-ins stay minimal — module, teeth, pressure angle, thickness, bore; confirms round-bore-only is the median feature set among "quick gear" tools, not just open-source ones |
| **3d-editor.com Gear Generator** | Round, DIN-style keyway | Lightening holes | Not confirmed | Closest online-tool analogue to `spur`'s v0.2 ambitions; also reports undercut/too-fine-teeth warnings, similar spirit to `spur`'s own warning contract |
| **Eng Bench gear generator** | Round + keyway | Not found | Not found | Explicitly documents cutting "a standard parallel keyseat sized to DIN 6885-1 **from the bore diameter**" — i.e. auto-derives keyway size from bore Ø via table lookup. This is the anti-feature `spur` has already and explicitly rejected; cite it as the contrasting approach, not a pattern to follow |
| **iLoveDXF Gear Generator** | Round, D-shaft, keyed | Not found | Not found | 2D/laser-cut focused (DXF/SVG + G-code output); confirms round/D-flat/keyway is the common floor across both 2D and 3D tools |

**Takeaway for the requirements step:** no researched comparable tool composes bore +
body cutout + face recess on one part the way v0.2 intends to. The differentiator isn't
any single new cut — it's that `spur` already ships face recesses and measurement aids
that no comparable tool offers, and v0.2 adds shaft-fit and weight-reduction features on
top without breaking that composability. That composition (not any individual geometry)
is where the real implementation risk sits, matching PROJECT.md's own framing ("Features
compose... the only refusal is a direct dimensional conflict").

## Sources

- DIN 6885 dimension table: [engineeringhardware.com — DIN 6885 Parallel Keys](https://engineeringhardware.com/guide/standard/din-6885-parallel-keys/), cross-checked against [JW Winco DIN 6885-2 PDF](https://www.jwwinco.com/fileadmin/user_upload_jwwinco/downloads/technical_section/6885-2_01.pdf) and [Ganter Norm DIN 6885 catalog PDF](https://live-katalog.ganternorm.com/pdf/ganter/en/6885_1.pdf)
- ISO R773 = DIN 6885 equivalence: [nexusseals.com — Metric Key & Keyway Dimensions per ISO/R773](https://www.nexusseals.com/sitepad-data/uploads/2020/09/Depasco-Keyway-Information-compressed.pdf)
- ANSI B17.1 S/T diametral-gauge convention: [engineersedge.com — Shaft Key Seat Depth Control Values S and T](https://www.engineersedge.com/gears/shaft_key_seat_depth_14412.htm), cross-checked against [amesweb.info — Depth Values for Shaft Keyseats/Hub Keyways](https://amesweb.info/Keys/Shaft-Keyseat-Hub-Keyway-Depth-Values.aspx)
- ANSI B17.1 square-key sizing rule of thumb (width ≈ D/4 up to 6.5"): [keyseaters.com — Keyway Dimensions Size Chart](https://www.keyseaters.com/local/keyway-dimensions-size-chart-ansi-b17-1-metric-reference-national-machine-tool/), [ficientdesign.com — Keyway & Key Sizes](https://ficientdesign.com/keyway-key-sizes-chart/)
- Hex shaft commodity sizes: [REV Robotics — 5mm and 1/2in Hex Shafts](https://www.revrobotics.com/5mm-Hex-Shafts/)
- No standard for gear spoke/lightening-hole proportions: [AIAC-2019-155 — Optimization of Lightening Hole on a Spur Gear of an Aircraft Motor](http://aiac.ae.metu.edu.tr/paper.php/AIAC-2019-155), search results referencing Dudley's *Handbook of Practical Gear Design and Manufacture*
- Honeycomb infill cell/wall conventions: general 3D-printing infill literature (e.g. [ncbi.nlm.nih.gov/pmc/articles/PMC11206172 — Mechanical Behavior of 3D-Printed Thickness Gradient Honeycomb Structures](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11206172/)) — practice, not a standard
- Tip chamfer / semitopping practice: [KHK Gears — Practical Information on Gears / Involute Gear Profile](https://khkgears.net/new/gear_knowledge/gear_technical_reference/involute_gear_profile.html), [sovol3d.com — 3D Printing Gears That Actually Work](https://www.sovol3d.com/blogs/news/3d-printing-gears-that-actually-work-backlash-orientation-and-material-tips)
- FreeCAD gear tooling: [FreeCAD Documentation — Gear Workbench](https://wiki.freecad.org/Gear_Workbench), [looooo/freecad.gears (GitHub)](https://github.com/looooo/freecad.gears), [iplayfast/GearWorkBench (GitHub)](https://github.com/iplayfast/GearWorkBench)
- OpenSCAD gear libraries: [BOSL2/gears.scad (GitHub)](https://github.com/BelfrySCAD/BOSL2/blob/master/gears.scad), [BOSL2 gears.scad wiki](https://github.com/BelfrySCAD/BOSL2/wiki/gears.scad)
- Fusion 360 add-ins: [Autodesk App Store — GF Gear Generator](https://apps.autodesk.com/FUSION/en/Detail/HelpDoc?appId=1236778940008086660&appLang=en&os=Win64)
- Online gear generators comparison: [3d-editor.com — Gear Generator](https://www.3d-editor.com/tools/gear-generator), [Eng Bench — Gear Generator](https://engbench.com/geargen.php), [iLoveDXF — Gear Generator](https://ilovedxf.com/en/gear-generator), [geargenerator.com](https://geargenerator.com/)
- Project source (required reading): `.planning/PROJECT.md`, `src/spur/params.py`, `src/spur/calc.py`

---
*Feature research for: spur v0.2 "Fit to Shaft"*
*Researched: 2026-09-25*
