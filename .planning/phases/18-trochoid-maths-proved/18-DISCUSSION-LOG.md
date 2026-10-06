# Phase 18: Trochoid Maths, Proved - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-06
**Phase:** 18-trochoid-maths-proved
**Areas discussed:** Root mode O1–O4, Cutter: dedendum/ρ/T4, Refusal + z_min rules, Sweep + cost bars

Preliminary: the phase branch `gsd/phase-18-trochoid-maths-proved` was cut from
`origin/main` before the discussion (HOW_TO_DEVELOP §2). No SPEC.md, no prior checkpoint,
no matching todos, no spike/sketch findings.

---

## Root mode O1–O4

| Option | Description | Selected |
|--------|-------------|----------|
| O4: O3 now, flip later | Default-off `Literal` field in Phase 19; 0 of 44 fixture records move; the flip is a conditional Phase 20 under its own `Lxx` | ✓ |
| O3: default-off field, no planned flip | Same seam, Phase 20 dropped; stays opt-in like FreeCAD gears | |
| O2: always-on wherever rb > rf | 28 of 44 move incl. the default gear by up to ≈0.30 mm | |
| O1: always-on when teeth < z_min | 5 of 44 move; ≈0.14·m step between 17 and 18 teeth at 20° | |

| Option | Description | Selected |
|--------|-------------|----------|
| Only where rb > rf | The region L10 names; L09 fillet stays wherever rb <= rf; a request with nothing to replace is ignored and warned | ✓ |
| Every gear when requested | Hob root replaces the analytic fillet everywhere; 200-tooth build time unmeasured | |

| Option | Description | Selected |
|--------|-------------|----------|
| Mode + reason | Frozen result: `mode` Literal plus a `reason` naming why it stayed radial | ✓ |
| Mode only | Literal string; reasons recomputed by whoever warns | |

| Option | Description | Selected |
|--------|-------------|----------|
| Both boundaries | Undercut threshold and the rb = rf crossover; two tables in one RESULTS.md section | ✓ |
| Undercut threshold only | Exactly what SC4 names | |

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit argument, default radial | `root_mode(p, pr, requested="radial")`; Phase 19 passes the field | ✓ |
| Read the field from `p` in Phase 19 only | Body always radial until Phase 19 edits it | |

**User's choice:** O4; narrow region; mode + reason; both boundaries measured; explicit `requested` argument.
**Notes:** All five were the recommended option.

---

## Cutter: dedendum, ρ, T4

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed at 1.25·m | Read from the same expression as `rf`, never a copy | ✓ |
| Cutter parameter, defaulting to 1.25 | `hf_star` argument for a later ISO 53 profile D | |

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit mm argument, no root_fillet binding | `cutter(p, rho)`; sweep covers ρ* ∈ {0, 0.1, 0.25, 0.38, 0.5}·m plus each case's `root_fillet` | ✓ |
| Bind ρ = root_fillet now | Pre-empts Phase 19's field decision | |

| Option | Description | Selected |
|--------|-------------|----------|
| No — three tiers only | T1 closed form, T2 swept-cutter oracle, T3 freecad.gears at ρ = 0 | ✓ |
| Yes — I will supply one | Name source, licence, resolution, cutter assumptions | |

**User's choice:** fixed dedendum; explicit ρ argument; no T4 reference.
**Notes:** none.

---

## Refusal + z_min rules

| Option | Description | Selected |
|--------|-------------|----------|
| Tangent join inside a measured epsilon | Undercut from the sign of ξ_join; a degenerate bracket uses the flank join; epsilon set from a measurement in the phase (STACK's 1.3e-7 / 5e-11 mm bracket) | ✓ |
| Refuse: None + warning | Honest but refuses a legal gear within ~1e-7 mm of z_min | |

| Option | Description | Selected |
|--------|-------------|----------|
| root_mode owns every refusal | Single place that says radial-and-why; `trochoid_root` returns `RootCurve \| None`, None = numerical failure, sweep must show zero; warning sentences from one calc function | ✓ |
| trochoid_root returns (curve, warnings) | Each refusal re-detected inside the generator | |

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse with a named reason | Invalid one-flank construction → None + warning, analytic fallback; any inside the box goes to the human at a checkpoint | ✓ |
| Clip to the space centreline | Trim and ship; a plausible shape with no proof | |

**User's choice:** tangent join with measured epsilon; `root_mode` owns refusals; invalid cases refuse and go to the human.
**Notes:** none.

---

## Sweep + cost bars

| Option | Description | Selected |
|--------|-------------|----------|
| STACK's grid + the project's box corners | 7,296 cases as the floor plus α 30 / tip-land limit ± one step / 35, module at both field limits, x at both limits, ρ at each case's cap; every refusal counted | ✓ |
| STACK's grid only | Exactly the 7,296 cases | |

| Option | Description | Selected |
|--------|-------------|----------|
| Gate test under a measured budget | In `tests/test_calc.py` via `verify.fast`; ~2 s at `-n 8` expected; over budget → sample in gate, full grid in bench; T2 on a handful of rows in gate | ✓ |
| Bench script only | Full sweep in `bench/`; gate keeps a hand-picked sample | |

| Option | Description | Selected |
|--------|-------------|----------|
| Measure and record, no bar | Re-measure `derive()` (correct the stale 11.5 µs), measure `root_mode` and `trochoid_root` with host load; Phase 19 decides the keystroke path | ✓ |
| Set a derive() budget now | A ceiling picked before the measurement exists | |

**User's choice:** grid + box corners; gate test under a measured budget; measure and record, no bar.
**Notes:** The sweep option as presented said "module 0.5 and 10"; corrected in CONTEXT.md to the real field limits 0.2 and 10 (`params.py:36`) and acknowledged before the wrap-up check.

---

## Claude's Discretion

- `RootCurve`'s exact shape beyond immutable `(radius, half_angle)` pairs; sample count and spacing (N = 16 uniform in φ as the start).
- The cutter result's shape and the warning function's name.
- The ρ tripwire amount; the epsilon measurement method.
- How T3 is recorded (constants with a provenance docstring is the default reading).
- Test layout (`tests/test_calc.py` vs a sibling module); bench script name; whether the step measurement is a script or a one-off recorded run.
- The exact grid for the box corners (tip-land limit ± `pressure_angle`'s field step).

## Deferred Ideas

None raised. Items the discussion touched that the roadmap maps elsewhere: the field's name and the ρ field choice (Phase 19), `root_thickness` / `root_gap` and the waist floor (Phase 19), the restated warning text (Phase 19), the flip (conditional Phase 20).
