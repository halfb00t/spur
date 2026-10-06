# Feature Research

**Domain:** parametric involute spur gear generator, milestone v0.4 "True Root" (trochoidal root fillet below the base circle)
**Researched:** 2026-10-06 (every web source below was read on this date; publication dates quoted where the page gives one)
**Confidence:** MEDIUM overall. Geometry and numbers: HIGH-ish (derived here and checked against an independent brute-force rack-cutting simulation, see "Verification method"). Standards text (ISO 53, ISO 21771, DIN 867, DIN 3960): MEDIUM at best, because the ISO PDFs behind the paywall samples were not text-extractable and every standards claim below is read from secondary pages that agree with each other. Tool-behaviour claims: MEDIUM (source code read for FreeCAD gears, BOSL2, cq_gears; marketing pages for GearGen and 3d-editor, LOW-MEDIUM).

Scope: only what the NEW feature needs. Existing features (involute outline, backlash, analytic `root_fillet`, L33 lead-in warning, bores, recesses, chamfer, cutouts, measurement aids, shareable links) are not re-researched; they appear only as dependencies.

## Findings the roadmap must know first

1. **The hob root is not only an undercut matter.** The shipped outline is radial/chord below the base circle whenever `rb > rf`, not only when the gear is undercut. That is 28 of the 44 fixture records, including the default 19-tooth 25-degree gear (rb 15.067 mm, rf 14.438 mm). Only 5 of 44 are undercut by the shipped `derive()` test (teeth 6 at 14.5 degrees x4 records, teeth 8 at 25 degrees x1). So "undercut gears only" and "wherever the flank is radial" are two very different blast radii (see "Always-on vs opt-in").
2. **ISO 53 profile A is defined at 20 degrees only, and this project runs 14.5 to 35 degrees with 25 as the default.** A hob with dedendum 1.25 m and tip radius 0.38 m physically fits only up to 23.16 degrees; above 32.14 degrees a 1.25 m deep hob tooth has no tip land at all. The cutter tip radius must be capped to the geometric maximum for the pressure angle (a trimmable dimension, L03), and above 32.14 degrees the trochoid is not computable honestly (L08).
3. **`root_thickness` and `root_gap` cannot keep their meaning under a trochoidal root.** The true tooth thickness just above the root circle is a steep function of radius (default gear: 4.68 mm at rf+0.001 m falling to 3.51 mm at rf+0.3 m), the root land is 0 to 0.13 mm wide, and the printed 3.253 mm is a radial-flank extrapolation that is neither. The honest options are a stated redefinition or null plus warning (L08).
4. **`root_d` (root diameter) keeps its meaning and its value.** The generated profile's lowest radius equals `r + x*m - 1.25*m` exactly (measured 3.75000007 against 3.75 in simulation), so every rule that reads `rf` (bore wall, recess, cutout rim wall, `check()`) is untouched.
5. **The undercut waist is small compared with the fillet-shape difference.** Shipped-versus-true profile gap is up to 0.13 to 0.15 mm per module-1 gear in every `rb > rf` case, but the extra undercut removal beyond the shipped outline is only about 0.03 mm at 10 teeth, 20 degrees. The visible change is mostly the fillet, not the undercut.
6. **Where the trochoid meets the involute:** tangentially (smooth hand-off at the cutter's flank end point) when the gear is not undercut; by a crossing with a corner, slightly above the base circle, when it is undercut. The form diameter is the hand-off or crossing radius.
7. **When tools implement the hob root, it is on by default and not a style option; the one opt-in case is FreeCAD gears.** FreeCAD's `undercut` defaults to False, reads as a retrofit onto existing documents (ASSUMPTION: its reason is not stated in what was read). No surveyed tool exposes the dedendum; the pro calculators (MITCalc, the standardsapplied calculator) expose the cutter tip radius; the hobbyist generators do not.

## Reference: the generating geometry (formulas, sources, verification status)

Notation: module m, pressure angle a, pitch radius r = z m / 2, base radius rb = r cos a, profile shift x, hob dedendum coefficient hf* = 1.25, cutter tip radius rho = rho* m. All hold for the project's existing definitions (`rf = r - m(1.25 - x)`, tooth thickness `s = m(pi/2 + 2 x tan a) - backlash`).

| # | Claim | Source | Status |
|---|-------|--------|--------|
| G1 | ISO 53 profiles share a = 20 degrees and ha* = 1.00; hf*/rho_fP*: A 1.25/0.38, B 1.25/0.30, C 1.25/0.25, D 1.40/0.39. Profile A is the general-purpose one. | drivetrainhub.com basic-rack chapter (table); engineersedge.com DIN 867 page ("only one pair of values, cp = 0,25 m and rho_fP = 0,38 m has been specified in ISO 53"); Gear Solutions, Akpolat et al., 2018-04-15 ("ISO 53:1998 and DIN 867 ... usually a cutter tip radius of 0.38") | MEDIUM: three independent secondary pages agree; ISO text itself not readable |
| G2 | The 0.38 comes from the clearance: rho_max(c) = c/(1 - sin a) = 0.25/(1 - sin 20 deg) = 0.3799 | drivetrainhub equation `rho_F = h_fillet / (1 - sin a_n)`; arithmetic checked here | MEDIUM |
| G3 | The cutter's straight flank ends at depth `d_T = (hf* - x) m - rho (1 - sin a)` below the gear's pitch circle (rack tip arc is tangent to the flank there). For ISO 53 A at 20 degrees, d_T = 0.99997 m. | derived; d_T read back from the simulation: 0.99997 | VERIFIED by simulation |
| G4 | Undercut iff `z < 2 (hf* - x - rho* (1 - sin a)) / sin^2 a`; with ISO 53 A at 20 degrees this is exactly the textbook `2 (1 - x) / sin^2 a` (17.097 at x = 0). Minimum shift to avoid it: `x_min = hf* - rho* (1 - sin a) - z sin^2 a / 2` (= `1 - z/z_min` for ISO 53 A, 0.4151 at 10 teeth). | standardsapplied.com calculator states `z_min = 2 (hf* - x - rho*(1 - sin a)) / sin^2 a`; tec-science "Undercut of gears" (`z_min = 2/sin^2 a`, 17 at 20 degrees, 14 practical) and "Profile shift" (`x = 1 - z/z_min`); KHK technical reference (17 at 20 degrees, "gears with 16 teeth or less can be usable"); BOSL2 gears.scad (17 at 20 degrees, 32 at 14.5 degrees, `2/sin^2 a`) | VERIFIED: derivation plus simulation classification on both sides of the limit for 10 teeth/20 degrees (x_min 0.4151) and 8 teeth/25 degrees (x_min 0.352) |
| G5 | The fillet is the envelope of the cutter's tip-arc circles as the rack rolls on the pitch circle ("trochoidal"). Strictly it is the parallel (equidistant) curve of the trochoid the arc centre traces, which is why one 2025 paper calls it a "transition curve". | standardsapplied.com; Gear Solutions "Transition Curve" (Gorniak, Zarebski, Marciniec, 2025-09-14); Gear Solutions "Analysis of Gear Root Forms" (Hyatt et al., 2014-02-14: trochoidal is "most commonly used as it is generated by a hob") | MEDIUM (secondary) plus reproduced in simulation |
| G6 | Not undercut: trochoid and involute meet **tangentially** at the radius of the flank end point N: `r_N = sqrt(rb^2 + (r sin a - d_T / sin a)^2)`; form diameter d_Ff = 2 r_N. Undercut: the two curves **cross at a corner** a little above the base circle (10 teeth, 20 degrees: crossing at 4.7255 mm vs rb 4.6985 mm); form diameter is the crossing radius, found numerically. | Gear Solutions "Methods to determine form diameter on hobbed external involute gears" (Zhang, 2019-09-15: "in the simplest case ... tangent"; its equations are images and could not be read); formula derived here | VERIFIED by simulation: model vs brute force within 3e-4 mm on 5 non-undercut cases; steep undercut neck within the simulation's own resolution (0.024 mm worst, at 10 teeth). The standard's own d_Ff text (ISO 21771, DIN 3960) was not read. |
| G7 | Root circle radius is unchanged: `r + x m - hf* m`. | derived; simulation minimum radius 3.75000007 vs 3.75 | VERIFIED |
| G8 | Maximum tip radius for a hob with a tip land at depth hf* = 1.25 m: `rho_max* = (pi/2 - 2 hf* tan a) / (2 tan((90 deg - a)/2))`: 0.597 at 14.5, 0.472 at 20, 0.400 at 22.5, 0.318 at 25, 0.110 at 30, 0 at 32.14 degrees; 0.38 stops fitting above 23.16 degrees. The standardsapplied calculator's default rho* 0.471 "the largest full-round corner the rack tip carries" agrees with 0.472 at 20 degrees. | derived from rack tooth width `pi m/2` at the datum line; standardsapplied.com default | MEDIUM: derivation checked against one external number |
| G9 | The 30-degree-tangent critical section of ISO 6336-3 assumes a root "generated by the radius on the tip of the gear hob", valid for tooth profiles per the ISO 53 basic rack. | Gear Solutions, Pinnekamp et al. (RENK), 2024-05-15 | MEDIUM |
| G10 | Backlash by thickening the hob tooth by `backlash` at the datum line leaves the involute where the shipped model puts it (same base circle) and leaves rf unchanged. | derived, **not simulated** | ASSUMPTION: verify in the phase |

The existing `derive()` undercut threshold `z_min = 2 (1 - x) / sin^2 a` (calc.py) equals G4 only for ISO 53 A at 20 degrees. With the cutter tip radius capped to the geometric maximum it is **conservative at 14.5 degrees** (31.9 vs 30.8 teeth) and **optimistic at 25 degrees** (11.2 vs 11.9 teeth, using rho* = 0.318). The warning text also says "this model uses a radial root instead", which stops being true under the new feature.

### What changes on the real part, measured (simulation vs the shipped outline, backlash 0, fillet = cutter tip radius)

Maximum same-radius arc gap between the shipped outline and the generated profile, in mm. Positive: shipped tooth is thinner than generated (generated fillet fills more). Negative: shipped tooth is thicker (undercut waist the shipped outline lacks).

| Gear | rb > rf | Undercut | Max gap, positive | Max gap, negative |
|------|---------|----------|-------------------|-------------------|
| 19 teeth, m 1.75, 25 deg (default), cutter 0.318 m | yes | no | +0.295 | -0.0004 |
| same, cutter 0.5 mm (the default `root_fillet`) | yes | no | +0.266 | -0.0004 |
| 25 teeth, m 1, 20 deg | yes | no | +0.128 | -0.0003 |
| 18 teeth, m 1, 20 deg | yes | no | +0.141 | -0.0003 |
| 17 teeth, m 1, 20 deg | yes | barely (17 < 17.097) | +0.143 | -0.0003 |
| 14 teeth, m 1, 20 deg | yes | yes | +0.146 | -0.005 |
| 13 teeth, m 1, 20 deg | yes | yes | +0.145 | -0.008 |
| 10 teeth, m 1, 20 deg | yes | yes | +0.134 | -0.030 |
| 10 teeth, m 1, 20 deg, x +0.5 | yes | no | +0.077 | -0.0003 |

Reading: the visible change is 0.13 to 0.30 mm of extra material near the root on every gear with `rb > rf`; the undercut waist itself is at most 0.03 mm at the sizes tested. For FDM prints these are around or below one nozzle width (ASSUMPTION: 0.4 mm nozzle, not project-sourced); for CNC, EDM, resin and for matching a hobbed gear they matter.

New infeasibility class (undercut waist): at the corner of today's allowed range (6 teeth, 14.5 degrees, x = -0.6) the generated tooth waist is 0.021 m thick, i.e. nearly cut through; 6 teeth, 20 degrees, x = -0.6: 0.152 m; 6 teeth, 14.5 degrees, x = -0.3: 0.474 m; 6 teeth, 20 degrees, x = 0: 1.06 m (fine). `GearParams` allows all of these today (teeth 6 to 200, pressure angle 14.5 to 35, x -0.6 to 1.0, `params.py` lines 34 to 47).

## Feature Landscape

### Table Stakes (the hob root is wrong without these)

| Feature | Why expected | Complexity | Notes and dependencies on the existing code |
|---------|--------------|------------|---------------------------------------------|
| Trochoidal fillet generated from the rack/hob tip arc, default ISO 53 A (hf* = 1.25 fixed, rho* = 0.38) | Every tool that implements the hob root uses it as the shape (GearGen, 3d-editor, BOSL2, standardsapplied, MITCalc, KISSsoft); users asking for it want "what a hob cuts" | MEDIUM | Replaces `_outline`'s radial/chord lead-in plus `_fillet_corner` arc when the mode applies. Closed-form parametric points (G5/G6), no kernel fillet operator, so L09's reason (speed) is not violated. `profile()` already fixes hf* = 1.25 via `rf`, so no dedendum field is needed. |
| Cutter tip radius capped to the pressure angle's geometric maximum (G8) with a warning when trimmed | The default angle (25) and most of the allowed range are outside ISO 53's 20; an uncapped 0.38 m is a pointed hob that cannot exist | LOW | A trimmable dimension, so cap-and-warn (L03), same shape as `root_fillet()`'s cap. Pure function in `calc.py`, no kernel import. |
| Tangent hand-off when not undercut; trimmed crossing when undercut; closed, non-self-intersecting outline | Without the crossing trim an undercut gear's outline self-intersects and the extrude fails | MEDIUM-HIGH | The crossing solve is the one genuinely numeric step (bisection, in the L08 spirit: no failure mode that returns a plausible wrong answer). Involute spline then starts at the form radius, not at `spline_start`. |
| Not computed above 32.14 degrees, with a warning and the shipped analytic path as the explicit fallback | A number must be honest or absent (L08); `GearParams` permits 35 degrees | LOW | Under an opt-in mode this is a visible fallback with a warning; under always-on it silently changes nothing but must still say so. |
| Root diameter printed unchanged (`root_d`) | G7: it is the same circle | LOW | No code change; add a test that asserts it equals `2*rf` in both modes. |
| Undercut warning re-stated from the real onset (G4), naming `x_min`; no longer says "radial root" | The shipped text becomes false; users reading "undercut" want the shift that avoids it | LOW | `derive()` branch at calc.py `z_min`. With the mode on the sentence reports modelled undercut and the waist; with it off it keeps today's wording or is made conditional. |
| `root_thickness` / `root_gap` made honest under the hob root | Printed numbers are cut to metal (L08); the real thickness at the root circle is ill-conditioned (finding 3) | MEDIUM | Options: (a) null both with a warning when the mode is on (`DerivedDimensions` precedent: null where it does not apply; but both fields are typed non-optional today, so the type widens), (b) redefine at the form circle and print that circle's diameter next to it. The L26 fixture pins all 19 existing fields exactly and requires post-fixture fields null on replay (L27 pattern), so mode off must stay byte-identical. |
| Interaction rules with `root_fillet`, `tip_chamfer`, the L33 lead-in warning | A parameter the user did not set must never silently change the part (CLAUDE.md) | MEDIUM | `root_fillet` under the mode: ignored and warned (L27 D-01/D-02 precedent: hex bore ignores `bore_d`/`bore_flat` with one warning) or reinterpreted as the cutter tip radius (see Open decisions). `tip_chamfer_limit`'s third bound `ra - spline_start` (L29, bisected to about 2 um on the old spline boundary) must be re-measured on the new trochoid-to-involute junction. L33's "straight chord above the pitch circle" warning does not apply when there is no chord. |
| New-behaviour proof against an independent profile | The milestone rule: a trochoid is proved against a known-good profile, plus a closed form where one exists, or the warning stays (L08) | MEDIUM | No published coordinate table was found. The oracle that exists is a brute-force rack-cutting simulation (see "Verification method"), independent of the analytic trochoid; the closed forms are G3, G4, G6 (tangent case), G7. A hob data sheet or KISSsoft export from the human would be a better oracle (ASSUMPTION: none in hand). |
| Three-interface parity, schema, form, CLI | L02/L31: one `GearParams` model drives all three; one model-driven field walk proves it | LOW | A new field flows to UI and CLI by metadata (`group`, `unit`, `step`). |
| Measured build time at the heaviest allowed configuration | L30/L31 rule; the composed worst row is already 29.42 s of 30 s alone (v0.4's other `must` item) | MEDIUM | Not measured here. Under "wherever `rb > rf`" the mode touches up to about 78 teeth at 14.5 degrees (`z < 2.5/(1 - cos a)`: 41 at 20, 27 at 25, 14 at 35 degrees); under "every gear" it reaches 200 teeth and the edge count per tooth changes (trochoid spline per flank instead of arc plus line). Flag for a spike. |

### Differentiators (valued, not required for a correct root)

| Feature | Value proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `x_min` (profile shift that avoids undercut) printed next to the warning | Tells the user the one number that fixes the part; BOSL2 offers `auto_profile_shift(get_min=true)`, 3d-editor suggests "+0.3 to +0.5" | LOW | Closed form G4, verified. Additive `DerivedDimensions` field, null when not undercut or when the mode is off (fixture replay). |
| Root form diameter `d_Ff` printed (null when not applicable) | The ISO 21771 / DIN 3960 quantity; the one number that says where the usable involute starts; GearGen and standardsapplied print it | LOW once G6 exists | Not caliper-measurable; a drawing and inspection number. Honest only with the trochoid. |
| User-settable cutter tip radius | MITCalc exposes cutting-tool `rf*`; standardsapplied exposes `rho*`; KISSsoft's root radius coefficient is the tool tip radius. Lets a shop match its actual hob. | LOW-MEDIUM | Either reuse `root_fillet` (mm) as the tip radius under the mode, or add one field. Default must stay absolute mm (L05) while ISO 53 scales with module: see Open decisions. |
| Undercut waist thickness printed, warned below a floor | The only number that says whether an undercut tooth is still a tooth (0.021 m at the range corner) | LOW-MEDIUM | New refusal-or-cap decision: a waist thinner than `MIN_WALL`-style floor is a direct geometric conflict, not trimmable by this feature (L03: 422 naming `teeth`, `profile_shift`, `pressure_angle`) unless the human prefers a warning. |
| Mate interference check against form diameter (mate's tip contact below this gear's `d_Ff`) | Closes the gap L10 left ("does not affect meshing at nominal centre distance" is only true without interference) | MEDIUM | Needs the mate's tip circle at the working distance; `centre_distance()` exists. Defer. |

### Anti-Features (look good, create problems)

| Feature | Why requested | Why problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Bending stress, safety factor, "Lewis strength" number | The trochoid is a strength feature (3d-editor: it "affects strength margins, not meshing") | Needs load, material, ISO 6336 factors the tool has no basis for; a printed strength number is a number someone relies on (L08) | Print geometry only: waist thickness, `d_Ff`. Defer ISO 6336-3 `s_Fn`/`h_Fe`/`rho_F` (30-degree tangent) as a geometry-only later item. |
| Silent switch to the trochoid below `z_min` with no opt-in | "Just make low-tooth gears right" | Changes old links' parts (L05); and the root shape jumps by about 0.14 m between 17 and 18 teeth (shipped-vs-true gap table) because 18 teeth keeps the circular fillet | Opt-in field, or a mode that applies to every gear where the flank is radial, not a z threshold. |
| Automatic profile shift to avoid undercut (BOSL2's default) | Never see an undercut | Changes the part from what the user set; violates "a parameter the user did not set must never silently change the part" | Print `x_min`, warn, let the user set `profile_shift`. |
| Circular-arc approximation sold as the trochoid | 3d-editor.com calls its root "a close approximation of the true trochoid" | Fails the milestone rule that the trochoid is proved against a known-good profile; a "true root" label on an approximation is the L08 failure | If an approximation is ever shipped, name it and print its measured deviation; otherwise keep the analytic fillet. |
| Editable dedendum / clearance coefficient | MITCalc and KISSsoft expose `hf*`/`c*` | Changes `root_d`, which the bore/recess/cutout rules and every link depend on (L05); no hobbyist input to set it from | Keep `hf* = 1.25` fixed; defer. |
| Vendoring FreeCAD gears' undercut code | It exists and runs | GPL-3.0 (GitHub API licence field, 2026-10-06); and it is a sharp-corner (rho = 0) trochoid, so its onset is 21.4 teeth at 20 degrees, not 17.1 (derived, ASSUMPTION: read from the parametrisation, which uses only `df`, `dw`, `psi`) | Reference only, never a dependency; the oracle is the independent simulation. |
| Protuberance, grinding stock, topping hob profiles (ISO 53 B to D) | Appear in the same standard | A different manufacturing process; nothing in the audience (print, hob, mill) uses it | Out of scope. |

## Always-on vs opt-in: evidence and price

### What the surveyed tools do

| Tool | Hob root | On by default? | Cutter tip radius user-set? | Source |
|------|----------|----------------|-----------------------------|--------|
| FreeCAD gears (GPL-3.0, last push 2026-09-15) | Trochoid of a sharp rack corner at root depth, trimmed against the involute (`InvoluteTooth`, `undercut_function_x/y`) | **No**: `undercut=False` by default; separate circular `root_fillet` (mm, default 0) | No | github.com/looooo/freecad.gears `pygears/involute_tooth.py`, FreeCAD docs `FCGear_InvoluteGear.md`; maintainer on 2024-02-03: "undercut is (imo) only relevant for gears with a small number of teeth. For bigger gears a root-fillet can be used" |
| BOSL2 `gears.scad` (last commit 2026-09-26) | Envelope of a sharp rack corner at depth 1.0 m (`_gear_tooth_profile`, `undercut` list) | **Yes** for any tooth count, but `profile_shift="auto"` removes the undercut for low counts by default | No | github.com/BelfrySCAD/BOSL2 |
| cq_gears (CadQuery, last push 2024-12-27) | None: three-point root arc on the dedendum circle | n/a | No (`dedendum_coeff`, `clearance` instead) | github.com/meadiode/cq_gears `spur_gear.py` |
| Fusion 360 Spur Gear add-in | Circular fillet, "root fillet radius" with a maximum, no trochoid | n/a | Radius is the fillet, not a tool tip | productdesignonline.com tutorial (LOW: secondary) |
| GearGen.xyz | "Hobbed trochoid root in every DXF ... ISO 21771 with ISO 53-style hob roots" | **Yes** | No (module, pressure angle, shift, backlash) | geargen.xyz (marketing text, LOW-MEDIUM) |
| 3d-editor.com Gear Generator | "Trochoid-approximated root fillet"; warns below about 17 teeth at 20 degrees | **Yes** | No | 3d-editor.com/tools/gear-generator (LOW-MEDIUM) |
| standardsapplied.com calculator | True generated trochoid, prints form diameter, undercut onset formula G4 | **Yes** | **Yes** (`ha*` 1.00, `hf*` 1.25, `rho*` default 0.471) | standardsapplied.com/involute-gear-design.html |
| MITCalc | Cutting-tool parameters `ha*`, `c*`, `rf*` as inputs; undercut check | **Yes** (pro tool) | **Yes** | mitcalc.com gear_theory help |
| KISSsoft | Root radius coefficient = tool tip radius; root form circle checked | **Yes** (pro tool) | **Yes** | KISSsoft product descriptions (search results only, LOW) |

Conclusion: where the hob root is implemented it is the geometry, not a style: always on, with the tip radius either fixed at the ISO 53 value (hobbyist tools) or exposed (pro tools). The only opt-in is FreeCAD's, and the only tool that dodges the part-change cost does so by changing the part another way (BOSL2's automatic shift). None of these tools had a frozen-link constraint like L05; they are not evidence about the cost of changing old parts, only about what users of such tools expect to see for a fresh gear.

### What each choice costs here (priced against the repo, 2026-10-06)

Counts come from the 44-record `tests/regression/pre_v0_2.json` fixture (39 built solids, 5 mate-only records that pin `derive()` only).

| Option | Fixture records that change | L05 (links keep their part) | Behaviour at the threshold | User-visible cost | Notes |
|--------|-----------------------------|-----------------------------|----------------------------|-------------------|-------|
| O1. Always-on when undercut (`teeth < z_min`) | 5 of 44 (3 built, 2 mate-only): teeth 6 and 8 gears | broken for low-tooth links only | **Discontinuous**: 17 teeth gets the trochoid, 18 the circular fillet; the root shape jumps by about 0.14 m | Low-tooth links change shape and their printed `root_thickness` etc. | Needs its own `Lxx`, `make fixture.regen` in its own commit (L26 D-03) |
| O2. Always-on wherever `rb > rf` (the region L10 actually names) | 28 of 44, including the default gear | broken for most links in the wild (default gear's root changes by up to 0.30 mm) | Continuous in z up to the `rb = rf` crossover (above it the shipped analytic path still differs by about 0.13 m, so a second edge remains) | Every common gear changes | Largest `Lxx` and fixture regen; closest to "what a hob cuts" |
| O3. New default-off field | 0 of 44; L05 and L26 hold byte for byte | kept | The user chooses; no threshold | One more control; a user who never sets it keeps the radial root and the undercut warning | The L27 precedent (a new field that replaces a profile and names what it ignores) applies. The mode can then apply wherever the flank is radial (no discontinuity) without touching old links |
| O4. O3 now, default flipped later under its own `Lxx` | 0 now | kept now | none | Decision deferred, not dodged | Lets the oracle and the build-time sweep land before any link changes part |

Evidence-based reading (the human decides at discuss-phase): the tools' norm argues the hob root should eventually be the default; this repo's L05 and L26 argue it should land opt-in first; and O1 is the one option the evidence argues against on its own merits (a z-threshold produces a root-shape jump no real hob produces). If the human insists on always-on, O2 is the physically consistent version and the fixture regeneration is large and must be priced as such.

## Feature Dependencies

```
Cutter tip radius (cap to rho_max*(a), G8)
    └──requires──> hf* = 1.25 fixed (already in calc.profile via rf)
Trochoid points (G5)
    └──requires──> Cutter tip radius
    └──requires──> backlash handled as hob-tooth thickening (G10, to be verified)
Form radius / crossing solve (G6)
    └──requires──> Trochoid points
    └──requires──> involute half_angle (calc.Profile.half_angle, exists)
Outline with hob root (model._outline)
    └──requires──> Form radius (involute spline start moves to it)
    └──replaces──> spline_start() lead-in chord and _fillet_corner arc, in the new mode only
tip_chamfer_limit re-measure (L29 D-04)
    └──requires──> Outline with hob root
root_thickness / root_gap honesty
    └──requires──> Form radius (if redefined at the form circle)
Undercut warning (G4) and x_min
    └──requires──> Cutter tip radius
x_min, d_Ff, waist thickness fields
    └──enhances──> Undercut warning
Build-time sweep (L30/L31 rule)
    └──requires──> Outline with hob root

Opt-in field ──conflicts──> silent z-threshold switch (O1)
Hob root mode ──conflicts──> root_fillet meaning (ignore+warn, or reinterpret)
Hob root mode ──conflicts──> L33 lead-in warning (no chord exists)
Always-on (O1/O2) ──conflicts──> L05 and the L26 fixture (needs its own Lxx + make fixture.regen)
```

### Dependency Notes

- **Cutter tip radius needs G8's cap:** the project's default angle is outside ISO 53, so the standard's 0.38 m is not always buildable; the cap is a pure `calc.py` function (calc.py never imports the kernel).
- **Outline needs the form radius:** the existing `spline_start()` is also read by `tip_chamfer_limit()`; both must read the same new radius or the L29 cap goes stale.
- **`root_thickness` rework needs the `DerivedDimensions` rule:** every key always present, null where not applicable, additive fields required null on fixture replay (L21, L27, L28).
- **Existing rules that read `rf` are untouched:** bore wall, recess radii, cutout rim wall, `check()`. This is what makes the feature local to `_outline`, `derive()` and one or two `calc.py` helpers.
- **Not affected:** `caliper_over_tips`, span (Wildhaber), `centre_distance`: they read tip radius and the involute above the base circle, which G6 leaves unchanged.

## MVP Definition

### Launch With (v0.4)

- [ ] Hob-root trochoid, ISO 53 A default, tip radius capped to G8, tangent or crossing hand-off, closed outline; applied wherever the flank is radial under the chosen mode (O3/O4), or per the human's decision
- [ ] Root diameter unchanged and asserted; undercut warning restated from G4 with `x_min`
- [ ] `root_thickness` / `root_gap` honest under the mode (null+warning or stated redefinition)
- [ ] Domain limits: no trochoid above 32.14 degrees (warning, explicit fallback); waist-thickness floor decided (422 vs warning)
- [ ] Proof: independent brute-force simulation plus the closed forms G3, G4, G6 (tangent), G7; mode-off fixture byte-identical
- [ ] `root_fillet`, `tip_chamfer_limit`, L33 interactions defined and tested; measured build time at the heaviest allowed configuration

### Add After Validation (v0.4.x)

- [ ] `d_Ff` and waist thickness printed (cheap once the geometry exists)
- [ ] User-settable cutter tip radius (trigger: someone asks to match a real hob)
- [ ] Flip the default to the hob root under its own `Lxx` (trigger: oracle plus build-time sweep green, human decides)

### Future Consideration (v0.5+)

- [ ] Mate interference check against form diameter
- [ ] Geometry-only ISO 6336-3 critical section (30-degree tangent)
- [ ] Editable dedendum/clearance (needs an L05 decision)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Hob-root trochoid with cap and hand-off | HIGH | MEDIUM-HIGH | P1 |
| Independent oracle + closed-form tests | HIGH (milestone rule) | MEDIUM | P1 |
| Honest `root_thickness` / `root_gap` | HIGH (L08) | MEDIUM | P1 |
| Undercut warning from G4, `x_min` | MEDIUM | LOW | P1 |
| Domain limits (32.14 degrees, waist floor) | MEDIUM | LOW-MEDIUM | P1 |
| Interaction rules (`root_fillet`, chamfer cap, L33) | HIGH | MEDIUM | P1 |
| Build-time sweep | HIGH (rule) | MEDIUM | P1 |
| `d_Ff` printed | MEDIUM | LOW | P2 |
| User-settable tip radius | MEDIUM | LOW-MEDIUM | P2 |
| Flip default (O4 step 2) | MEDIUM | LOW code, HIGH process | P2 |
| Mate interference vs `d_Ff` | LOW-MEDIUM | MEDIUM | P3 |
| ISO 6336-3 critical section | LOW | HIGH | P3 |

## Competitor Feature Analysis

| Feature | FreeCAD gears | BOSL2 | GearGen / 3d-editor | standardsapplied / MITCalc | Our approach |
|---------|---------------|-------|---------------------|----------------------------|--------------|
| Hob root | opt-in sharp-corner trochoid | always (sharp-corner envelope), auto shift hides it | always, tip radius fixed | always, tip radius set by user | mode decided at discuss-phase; ISO 53 A capped by angle |
| Form diameter printed | no | no | GearGen: yes (marketing) | yes | P2, null when mode off |
| Undercut warning | docs only | docs; `auto_profile_shift(get_min)` | 3d-editor warns (17 teeth rule) | formula G4 | G4, with `x_min` |
| Dedendum exposed | `clearance` | `clearance` | no | yes | no (anti-feature) |
| Auto profile shift | no | **yes** | no | no | no (anti-feature) |

## Verification method (so the phase can rebuild the oracle)

Prototyped in the session scratchpad (not committed; the repo was not modified). About 60 lines of numpy, independent of the analytic trochoid:

1. Rack tooth boundary in rack coordinates `(xi, d)` (d = depth toward the gear): right flank `xi + d tan a = pi m/4 + d0 tan a` with `d0 = -x m`, tip arc of radius rho tangent to flank and flat, flat at `d_tip = d0 + hf* m`; mirror for the left flank.
2. Gear rotation `theta` swept densely (9000 to 12000 steps); each boundary point mapped to the gear frame by `R(-theta) (xi + r theta, -r + d)`.
3. Polar binning over one tooth space (4000 to 20000 bins); generated boundary radius at each angle = minimum radius over all swept boundary points.
4. Compared against: root circle (G7), involute above the form radius (3e-4 mm non-undercut), analytic trochoid and the form radius G6, the shipped outline rebuilt from `calc.spline_start` and `model._fillet_corner` (gap table), tooth thickness versus radius.

Reproduced external numbers: ISO 53 A flank-end depth 0.99997 m; `x_min` 0.4151 at 10 teeth (equals tec-science's `1 - z/z_min`); `rho_max*` 0.4719 at 20 degrees (standardsapplied's 0.471).

Limits of this verification: it checks my derivation against a numerically independent construction, not against a published coordinate table or the ISO 21771 d_Ff formula text. A KISSsoft or hob-sheet example from the human would close that.

## Open decisions for discuss-phase (not mine to make)

1. Mode: O1, O2, O3 or O4 above, and whether the mode applies wherever the flank is radial or to every gear (200-tooth build time unmeasured).
2. `root_fillet` under the mode: ignored and warned (L27 precedent), or reinterpreted as the cutter tip radius. Tension: ISO 53's 0.38 m scales with module, the shipped default 0.5 mm is absolute (L05); 0.5 mm is 0.29 m at m 1.75 but 0.5 m at m 1 (above the 0.472 cap at 20 degrees) and 0.05 m at m 10.
3. `root_thickness` / `root_gap`: null+warning or redefined at the form circle.
4. Waist floor: 422 (direct geometric conflict) or warning.
5. ASSUMPTION to confirm: the dedendum stays fixed at 1.25 m; backlash realised as hob-tooth thickening (G10).
6. A published or tool-generated reference profile to use as the oracle in addition to the simulation.

## Sources

Checked 2026-10-06 unless stated. Provider tier from the confidence seam: web search alone LOW, cross-checked MEDIUM; source-code reads and derivations verified by simulation are tagged separately above.

- ISO 53:1998 basic rack, via secondary pages: https://drivetrainhub.com/notebooks/gears/tooling/Chapter%201%20-%20Basic%20Rack.html ; https://www.engineersedge.com/gears/basic_rack_tooth_gear_profiles_din_867_13217.htm ; Akpolat et al., Gear Solutions 2018-04-15 https://gearsolutions.com/features/effects-of-asymmetric-cutter-tip-radii-on-gear-tooth-root-bending-stress/ (MEDIUM; the ISO PDF sample https://cdn.standards.iteh.ai/samples/22643/1587e6ac15ea488b913773116bac2dad/ISO-53-1998.pdf was not text-extractable)
- ISO 21771 scope only: https://standards.iteh.ai/catalog/standards/iso/d6596c53-21c4-45e0-bf25-726e03df042a/iso-21771-2007 (text not read; LOW)
- Undercut and profile shift: https://www.tec-science.com/mechanical-power-transmission/involute-gear/undercut/ ; https://www.tec-science.com/mechanical-power-transmission/involute-gear/profile-shift/ ; https://khkgears.net/new/gear_knowledge/gear_technical_reference/involute_gear_profile.html (formulas are images there; the 17/16 statements are text)
- Trochoid, form diameter, root forms: https://gearsolutions.com/features/methods-to-determine-form-diameter-on-hobbed-external-involute-gears/ (Zhang, 2019-09-15; equations are images) ; https://gearsolutions.com/features/analysis-of-gear-root-forms-a-review-of-designs-standards-and-manufacturing-methods-for-root-forms-in-cylindrical-gears/ (Hyatt et al., 2014-02-14) ; https://gearsolutions.com/features/transition-curve-much-more-than-a-radius-at-the-root-fillet-of-a-tooth/ (Gorniak et al., 2025-09-14) ; https://gearsolutions.com/features/numerical-approach-to-account-for-actual-tooth-root-geometry/ (Pinnekamp et al., 2024-05-15) ; https://www-mdp.eng.cam.ac.uk/web/library/enginfo/textbooks_dvd_only/DAN/gears/generation/generation.html (fillet radius 0.38 for the 20-degree full-depth system)
- Tools: https://github.com/looooo/freecad.gears (commit 83ec154, 2026-09-15; `pygears/involute_tooth.py`; discussion #142, 2024-02-03/05) ; https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FCGear_InvoluteGear.md ; https://github.com/BelfrySCAD/BOSL2 `gears.scad` (last commit 2026-09-26) ; https://github.com/meadiode/cq_gears `spur_gear.py` ; https://www.geargen.xyz/index ; https://www.3d-editor.com/tools/gear-generator ; https://www.standardsapplied.com/involute-gear-design.html ; https://www.mitcalc.com/doc/gear1/help/en/gear_theory.htm ; https://productdesignonline.com/fusion-360-tutorials/create-custom-3d-printable-gears-in-fusion-360/ (LOW) ; KISSsoft: search results only (LOW)
- Repo, read in full: `.planning/PROJECT.md`; `docs/architecture/gear-maths/*.md`; `docs/ideas/2026-09-21-trochoidal-root-fillets.md`; `docs/architecture/decision_log.md` L03, L05, L08, L09, L10, L26, L33; `README.md`; `src/spur/calc.py` (`profile`, `_tooth`, `root_fillet`, `spline_start`, `derive`); `src/spur/model.py` (`_outline`, `_fillet_corner`); `src/spur/params.py` field ranges; `tests/regression/pre_v0_2.json` (44 records, counted here).

---
*Feature research for: spur, v0.4 True Root (trochoidal root fillet)*
*Researched: 2026-10-06*
