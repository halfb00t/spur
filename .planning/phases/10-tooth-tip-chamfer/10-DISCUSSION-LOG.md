# Phase 10: Tooth-Tip Chamfer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-28
**Phase:** 10-tooth-tip-chamfer
**Areas discussed:** Cap rule — what the tip land allows; Cost cap if 200 teeth × max chamfer misses 30 s; Numbers, warning and form placement; Proof shape on the built solid

All four gray areas offered were selected. No `.continue-here.md`, no SPEC.md, no prior
CONTEXT.md, no checkpoint, no matching todos (`todo.match-phase 10` → 0). Prior context
loaded: PROJECT.md, REQUIREMENTS.md, STATE.md, 07/08/09-CONTEXT.md, the four v0.2
research files, `bench/RESULTS.md`, `docs/HOW_TO_DEVELOP.md`. Codebase maps exist
(`.planning/codebase/*.md`); the scout read `model.py`, `calc.py`, `params.py`,
`tests/test_model.py`, `bench/` and `static/app.js` directly.

---

## Cap rule — what the tip land allows

### Q1 — Axial cap: how much tip land must remain between the two end-face chamfers?

| Option | Description | Selected |
|--------|-------------|----------|
| c ≤ 0.45 × face_width | Mirrors root_fillet/recess_fillet's 0.45 rule — 10 % of the face width always stays as tip land; one family of caps | ✓ |
| c ≤ (face_width − MIN_TIP_FDM) / 2 | Land never below 0.4 mm; a second constant; a 1 mm face keeps only 0.3 mm chamfers | |
| c < face_width / 2 | Chamfers may meet at a ridge; only the kernel bounds it; a land of zero contradicts the wording | |

**User's choice:** c ≤ 0.45 × face_width (recommended).

### Q2 — Radial cap: analytic bound or only the kernel's measured one?

| Option | Description | Selected |
|--------|-------------|----------|
| Addendum bound + measured check | c ≤ ra − r: the footprint stays above the pitch circle; analytic in calc.py; the plan still probes the kernel inside (08 D-03) | ✓ |
| Kernel-measured only (08 D-03) | Largest chamfer the kernel allows, but no geometric meaning and may vary with tooth count | |
| Tip-arc bound: c ≤ tip thickness | Intuitive, but a proxy — the arc length does not bound an end-face chamfer | |

**User's choice:** Addendum bound + measured check (recommended).

### Q3 — Chamfer shape: symmetric 45° like bore_chamfer?

| Option | Description | Selected |
|--------|-------------|----------|
| Symmetric 45°, one field | `solid.chamfer(c, None, tip_edges)` — bore_chamfer's call and meaning | ✓ |
| You decide | Planner picks | |

**User's choice:** Symmetric 45°, one field (recommended).

### Q4 — If the kernel fails inside the two analytic caps, what is the rule?

| Option | Description | Selected |
|--------|-------------|----------|
| Lower the cap to the measured boundary | Probe at small and large tooth counts and modules; cap one step inside the failure, measurement next to the rule, tested either side; tooth-count-dependent boundary surfaced, not chosen | ✓ |
| Keep the analytic caps; kernel failure is the existing BuildError | Simpler, but a 422 for a trimmable dimension — against L03 | |

**User's choice:** Lower the cap to the measured boundary (recommended).

**Continue?** Next area.

---

## Cost cap if 200 teeth × max chamfer misses 30 s

### Q1 — If the heaviest allowed row exceeds SPUR_BUILD_TIMEOUT=30s, what happens?

| Option | Description | Selected |
|--------|-------------|----------|
| Halt for a human decision, direction pre-agreed | 08 D-11's rule; the next question fixes the first offer | ✓ |
| Pre-decide: lower the field's `le` | Static, schema-visible, identical on every machine; no checkpoint | |
| Pre-decide: teeth-dependent analytic cap | Measured per-edge cost (honeycomb's shape), warned; a dimension depends on tooth count and one host | |

**User's choice:** Halt for a human decision, direction pre-agreed (recommended).

### Q2 — Is the cost spike its own first plan?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — 10-01 measures only | Probe path; 19/40/200 teeth; module 1.75 and 10; c at the cap; build/STL/STEP; radial boundary probed; field plans follow | ✓ |
| No — spike is the first task of the field plan | Fewer plans; a halt mid-plan leaves half a feature | |
| You decide | Planner picks | |

**User's choice:** Yes — 10-01 measures only (recommended).

### Q3 — Sweep rows for bench/RESULTS.md?

| Option | Description | Selected |
|--------|-------------|----------|
| 08 D-11 shape + a min-module row | 200 teeth × module {1.75, 10} × chamfer {0.4, cap max} × recess {both, none} = 8 rows, plus module 0.2 | ✓ |
| 08 D-11 shape only (8 rows) | Assumes the fine-module case is not the heavy one | |
| You decide | Planner designs the sweep | |

**User's choice:** 08 D-11 shape + a min-module row (recommended).

### Q4 — Which cap does the over-budget checkpoint offer first?

| Option | Description | Selected |
|--------|-------------|----------|
| Lower the field's `le` | Schema-visible maximum, the same on every machine and tooth count; number in RESULTS.md and L29 | ✓ |
| Teeth-dependent analytic cap, warned | Keeps 3 mm on small gears; a per-host measurement decides a dimension | |
| Decide at the checkpoint | No pre-agreed direction | |

**User's choice:** Lower the field's `le` (recommended).

**Continue?** Next area.

---

## Numbers, warning and form placement

### Q1 — Which new DerivedDimensions field(s)?

| Option | Description | Selected |
|--------|-------------|----------|
| Applied chamfer only | One `float | None` field (e.g. `tip_chamfer_effective`), null when off, 3 dp; DIMS + README rows this phase | ✓ |
| Applied chamfer + remaining tip land | Also `face_width − 2c`; two fields, two rows | |
| No new field — warning only | Cheapest; the fit number appears nowhere (against 08 D-05) | |

**User's choice:** Applied chamfer only (recommended).

### Q2 — Warning sentence when the cap bites?

| Option | Description | Selected |
|--------|-------------|----------|
| 'reduced to … to keep …' family | One sentence naming the applied value and the limit that bound it; wording the planner's (L15) | ✓ |
| One sentence per limit that bit | Axial and radial each get a sentence | |
| You decide | Planner writes it | |

**User's choice:** 'reduced to … to keep …' family (recommended).

### Q3 — Where does tip_chamfer live in the form and the CLI order?

| Option | Description | Selected |
|--------|-------------|----------|
| Teeth group, after root_fillet | Tooth geometry beside the other tooth-edge treatment; 08 D-07's reading of "in its own group" | ✓ |
| Body group, next to face_width | Beside the dimension it eats | |
| Own 'Tip' group | A one-field fieldset; rejected for bore_hex in 08 D-07 | |

**User's choice:** Teeth group, after root_fillet (recommended).

### Q4 — Help text?

| Option | Description | Selected |
|--------|-------------|----------|
| Purpose named, no size | "Chamfer on the tooth-tip edges at both faces — an edge break for handling and printing. 0 = none." | ✓ |
| Bare, bore_chamfer's shape | "Chamfer on the tooth-tip edges at both faces. 0 = none." | |
| You decide | Planner writes it under SC2 | |

**User's choice:** Purpose named, no size (recommended).

**Continue?** Next area.

---

## Proof shape on the built solid

### Q1 — How is SC1 proven on the built solid?

| Option | Description | Selected |
|--------|-------------|----------|
| Topology + bounding box | Face count +2·teeth, edge delta likewise, volume smaller, BoundingBox x/y and tip_d unchanged, other selectors' counts unchanged — 09 D-07's shape | ✓ |
| Topology + read the chamfer faces back | Plus a datum read of each chamfer face's vertices (09 D-14's shape) | |
| You decide | Planner picks | |

**User's choice:** Topology + bounding box (recommended). CONTEXT.md records that the
exact face/edge deltas are measured in the spike and pinned, not derived.

### Q2 — Which matrix rows for the tip selector?

| Option | Description | Selected |
|--------|-------------|----------|
| Every existing configuration | A tip Counter column on every current row (round, D-flat, hex, keyway × recess) plus a 200-tooth row and a module-0.2 row | ✓ |
| One row per bore shape at defaults | Four rows plus 200 teeth | |
| You decide | Planner picks under REQ-edge-selection-proven | |

**User's choice:** Every existing configuration (recommended).

### Q3 — A tripwire that the proof goes red on a silently vanished tip chamfer?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — guard test + topology tripwire | Patch the tip step to a no-op and assert the built-solid proof fails; plus the 07 D-15 empty-selection BuildError test | ✓ |
| Guard test only | The BuildError-on-empty test alone | |

**User's choice:** Yes — guard test + topology tripwire (recommended).

**Continue?** Ready for context (the "explore more" candidates — the field's `le`,
export timing in the halt, L29's scope — went to Claude's Discretion).

---

## Claude's Discretion

Names (field title, derived field, selector, chamfer step, cap function, sweep file,
RESULTS section); `tip_chamfer`'s `le` (recommended 3 like `bore_chamfer`); the selector's
exact criterion (verify the extruded tip arc's `geomType()` first); the spike's probe path
and bisection method; export time recorded but not gated by the halt; warning/help
sentences and the README example; recess interaction and `tol=` (confirm, don't add);
the exact sweep rows; the unchanged FDM tip-width warning.

## Deferred Ideas

- Analytic 2D tip-corner chamfer in `_outline()` — rejected reading (2026-09-25);
  recorded as the fallback to surface if no `le` fits the budget.
- Chamfering the flank end-face edges; a second chamfer length or angle; a
  teeth-dependent cost cap (D-07's second option); reporting the remaining tip land.

No scope creep surfaced during discussion.
