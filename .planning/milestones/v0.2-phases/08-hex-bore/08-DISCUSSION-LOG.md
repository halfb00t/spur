# Phase 8: Hex Bore - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-26
**Phase:** 08-hex-bore
**Areas discussed:** Round-profile fields alongside the hex, What the numbers say for a hex bore, Form placement / help text / UI behaviour, Heaviest configuration and the measurement

---

## Round-profile fields alongside the hex

### When `bore_hex > 0`, what happens to `bore_flat` (default 8.0)?

| Option | Description | Selected |
|--------|-------------|----------|
| Warn, same as `bore_d` | The hex replaces the whole round/D-flat profile; both fields get a warning saying they don't apply. `?bore_hex=6` works on the web, API and CLI. Supersedes the `bore_flat` half of REQ-hex-bore's 422 wording and ROADMAP SC2; the 422 stays for hex + keyway in Phase 9. | ✓ |
| 422 only when `bore_flat` was explicitly sent | `GearParams.model_fields_set`. Viable today (the form sends only non-default fields, the CLI only given flags) but a client that echoes every field gets a 422 for a value it never chose. | |
| Keep the 422 as written | Every hex link must carry `bore_flat=0`. Breaks the requirement's own "link that only adds `bore_hex` still works" sentence and L05's spirit. | |

**User's choice:** Warn, same as `bore_d`.
**Notes:** Trigger was an evidence conflict inside REQ-hex-bore itself (`bore_flat` defaults to 8.0, so its 422 clause and its "still works" clause cannot both hold). The plan amends REQ-hex-bore and ROADMAP SC2.

### Shape of the "does not apply" warning on a hex bore?

| Option | Description | Selected |
|--------|-------------|----------|
| One sentence naming both fields | e.g. "Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored." Only non-zero fields are named. | ✓ |
| One sentence per ignored field | Two warnings on a default-based hex link. | |
| Warn only when the field is non-default | Needs `model_fields_set` again; contradicts REQ-hex-bore's "warns when `bore_d` is also non-zero". | |

**User's choice:** One sentence naming both fields.
**Notes:** Every plain `?bore_hex=6` link carries the warning because `bore_d` defaults to 9 — accepted as what REQ-hex-bore asks for.

### With `bore_hex > 0`, do the round-profile checks in `check()` still run?

| Option | Description | Selected |
|--------|-------------|----------|
| Skip them; the hex gets its own checks | Ignored fields are not validated. Corner (circumradius incl. clearance) within `MIN_WALL` of the root circle is a 422 naming `bore_hex`. | ✓ |
| Keep them running | Simpler diff, but a link can be refused over `bore_flat` while the warning says `bore_flat` is ignored. | |

**User's choice:** Skip them; the hex gets its own checks.

### A `bore_chamfer` too large for the hex's side cannot build. Where is that caught?

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse early in `check()`, bound measured | 422 naming `bore_chamfer` and `bore_hex` before any CAD work; the planner probes the pinned kernel for the actual failure point; no rule if the kernel copes at every allowed size. | ✓ |
| Let the kernel catch-all report it | Zero new code; costs a timed build first and the message doesn't name `bore_hex`. | |
| Cap and warn the chamfer instead | L03's trimmable branch — but the user asked for that chamfer on that hex, a direct conflict. | |

**User's choice:** Refuse early in `check()`, bound measured.

---

## What the numbers say for a hex bore

### On a hex bore, what does `bore_effective` report?

| Option | Description | Selected |
|--------|-------------|----------|
| `null` — `bore_d` does not apply | Honest to the field's description ("Bore diameter including print clearance"); the hex's numbers live in new fields. | ✓ |
| The effective across-flats | One fewer new field, but the description and UI label become wrong for a hex. | |

**User's choice:** `null`.

### Which new `DerivedDimensions` fields does the hex bore add?

| Option | Description | Selected |
|--------|-------------|----------|
| Two: across-flats effective + corner-to-corner | `bore_hex + bore_clearance` (what calipers read across two flats) and that × 2/√3 (across two corners). Both `null` when off. Names are the planner's. | ✓ |
| One: corner-to-corner only | Literal to ROADMAP SC3; with `bore_effective` null the fit dimension would appear nowhere. | |

**User's choice:** Two fields.

### When do the two hex `DIMS` rows land in the web UI?

| Option | Description | Selected |
|--------|-------------|----------|
| This phase | Success Metric 1: UI, API and CLI in the same change. | ✓ |
| Phase 12 | Smaller diff now; a hex gear in the browser shows no hex numbers until then. | |

**User's choice:** This phase.

---

## Form placement, help text, UI behaviour

### Where does `bore_hex` sit on the web form and in the schema?

| Option | Description | Selected |
|--------|-------------|----------|
| In the Bore group, after `bore_flat` | One fieldset shows the whole bore profile; Phase 9's keyway fields join it. | ✓ |
| Its own "Hex bore" group | Literal to REQ-three-interfaces-extended's "in its own group"; a one-field fieldset. | |

**User's choice:** In the Bore group, after `bore_flat`.

### Help text for `bore_hex`?

| Option | Description | Selected |
|--------|-------------|----------|
| State the replacement + examples | "Across-flats of a hex bore; replaces the round bore and D-flat. Common hex stock: 5, 6, 8, 10, 12.7 mm. 0 = round bore." No standard named. | ✓ |
| Replacement only, no sizes | Loses the 12.7 mm = ½″ hint. | |
| Add the clearance rule too | `bore_clearance`'s own help is the place for that. | |

**User's choice:** State the replacement + examples.

### When `bore_hex > 0`, does the form change how `bore_d` and `bore_flat` look?

| Option | Description | Selected |
|--------|-------------|----------|
| No; the warning is the signal | Zero new form mechanism; the form stays schema-driven (L02). | ✓ |
| Grey out `bore_d` and `bore_flat` | First conditional-field rule in `app.js`; Phase 9 would need its own. | |

**User's choice:** No; the warning is the signal.

### Does Phase 8 update README.md?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, in the same change | Feature bullet, a `bore_hex` table row, one example link; the new example stays out of the regression corpus (07 D-05). | ✓ |
| Defer to Phase 12 | A shipped feature undocumented for four phases. | |

**User's choice:** Yes, in the same change.

---

## Heaviest configuration and the measurement

### SC4 says "max teeth, max `bore_hex`". What is measured?

| Option | Description | Selected |
|--------|-------------|----------|
| Small sweep, worst row is the number | 200 teeth × `bore_hex` {le, 12.7} × recesses {both, none} × `bore_chamfer` {0.4, max allowed}; every row recorded, the worst named "heaviest". | ✓ |
| One configuration | 200 teeth, `bore_hex` at its le, everything else default. | |

**User's choice:** Small sweep.

### Build time only, or also fine-STL and STEP export time now?

| Option | Description | Selected |
|--------|-------------|----------|
| Build + fine STL + STEP export | Same sweep, three more columns; Phase 12 still re-measures the combined configuration. | ✓ |
| Build time only | Literal to SC4. | |

**User's choice:** Build + fine STL + STEP export.

### How is the sweep run?

| Option | Description | Selected |
|--------|-------------|----------|
| Committed bench script + `make` target | e.g. `bench/build_time.py`, `make bench.build`; Phases 9–12 reuse it unchanged. | ✓ |
| Ad hoc command, recorded verbatim | As Phase 7 did for the fixture cost; each later phase re-derives it. | |

**User's choice:** Committed bench script + `make` target.

### Upper bound (`le`) for `bore_hex`?

| Option | Description | Selected |
|--------|-------------|----------|
| 200, same as `bore_d` | One family, one bound; anything larger than the root is refused anyway. | ✓ |
| Smaller, e.g. 50 | Closer to real hex stock, but a guess about the user's shaft. | |

**User's choice:** 200.

---

## Claude's Discretion

Field, script and target names; exact warning and refusal sentences; hexagon orientation
(kernel default, flat on +X); how the hex extent reaches `recess_radii` and `_cut_bore`;
`bore_clearance`'s help text; the selector-matrix hex rows; a solid-measurement test for
the derived numbers; the chamfer-vs-side probe design; whether a max-module row joins the
sweep; whether Phase 8 logs an `Lxx` (recommended: yes, L27); confirming `tol=` is not
needed. Full list in `08-CONTEXT.md` "Claude's Discretion".

## Deferred Ideas

Commodity hex sizes as UI presets (REQ-hex-presets, already tracked); conditional form
fields; rotating the hexagon relative to tooth 0; `model_fields_set`-aware refusals
(rejected, recorded); a hex-specific mouth chamfer size.
