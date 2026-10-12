# Phase 24: Bore-Shape Selector - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-12
**Phase:** 24-bore-shape-selector
**Areas discussed:** The gate (decision 9), Option set & totality, Pending vs starter, What a choice writes, Proof & placement

---

## The gate (kickoff decision 9, the open half)

Before the areas: measured at discuss-phase that `ConfigDict(json_schema_extra={"selectors": [...]})`
emits the key at the top level of `model_json_schema()` and that a subclass inherits it, so the
roadmap's second skip trigger (the pin would have to be weakened) does not fire.

| Option | Description | Selected |
|--------|-------------|----------|
| Build it | S1 confirmed buildable; all four states fit the L41 grammar; Phase 25 measures a HEAD that includes it | ✓ |
| Skip (cut) | `Skipped (cut)` row, STATE.md line, three REQs to Future, success metric 2 partly met | |
| Defer the decision | Stop here, no CONTEXT.md | |

**User's choice:** Build it
**Notes:** none

---

## Option set & totality

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, No bore option | `bore_d=0, bore_hex=0` is a legal 200 (MEASURED); without it the select lies or goes blank (BS-3); totality provable | ✓ |
| No, four shapes only | Blank select at `bore_d=0`; needs a disabled placeholder; totality unprovable | |

| Option | Description | Selected |
|--------|-------------|----------|
| Keyway outside the select | A modifier of Round and D-flat (L27 research, 23 D-09); dimmed under Hex by L41 | ✓ |
| Composite options | Six entries; each keyed one pending until both fields typed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Round, D-flat, Hex, No bore | Shapes first from simplest, the off state last | ✓ |
| No bore, Round, D-flat, Hex | Off state first | |
| D-flat, Round, Hex, No bore | Default first; reads oddly | |

| Option | Description | Selected |
|--------|-------------|----------|
| Top of Bore fieldset, "Bore shape" | First row before `Bore Ø`; title and labels from metadata; never in `fields` | ✓ |
| Fieldset legend row | Control beside the legend; new CSS; the browser test's label read would miss it | |
| You decide | Claude picks within the `.field` grid | |

**User's choice:** No bore included; keyway outside; order Round, D-flat, Hex, No bore; top of the Bore fieldset titled "Bore shape"
**Notes:** none

---

## Pending vs starter (kickoff decision 11)

| Option | Description | Selected |
|--------|-------------|----------|
| Hex at 0: Pending state, no write | Select shows Hex, field focused, part unchanged until typed; no invented A/F | ✓ (later folded into the one stash rule) |
| Hex at 0: Stash, else pending | Restore an earlier typed `bore_hex` if stashed, else pending | |

| Option | Description | Selected |
|--------|-------------|----------|
| D-flat at 0: Stash, else pending | Restore the user's own earlier `bore_flat`, else pending; same rule as Hex | ✓ |
| D-flat at 0: Stash, else schema default 8 | Fills `defaults['bore_flat']`; a flat the user did not type; two rules | |
| D-flat at 0: Pending only, no stash | Loses the typed flat on D-flat → Round → D-flat (BS-1) | |

The asymmetry (Hex never restores, D-flat restores) was surfaced and resolved:

| Option | Description | Selected |
|--------|-------------|----------|
| One rule: stash every zeroed field | Any field the selector writes to 0 is stashed; a `gt 0` field restores if stashed, else pending | ✓ |
| Keep asymmetry | Hex always pending; only `bore_flat` stashed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Select keeps the choice; target field focused + its reason row filled | `.pending` on the select's wrap (dashed tone); L41's `.reason` span on the `gt 0` field carries a need built from its title | ✓ |
| Select snaps back on next re-derive | The pick only focuses the field; the click looks undone | |
| You decide | Within L41's vocabulary | |

| Option | Description | Selected |
|--------|-------------|----------|
| Next re-derive from fields | Any `input`, `hashchange`, Reset or reload re-derives; a reload never remembers a pick | ✓ |
| Only when the chosen option becomes true | Pending survives edits to other fields | |

**User's choice:** one stash rule for every zeroed field; stash-else-pending for Hex and D-flat; pending shown as `.pending` + focus + reason row; ends on the next re-derive
**Notes:** the user first chose "pending, no write" for Hex and "stash, else pending" for D-flat, then chose one rule for both when the asymmetry was pointed out

---

## What a choice writes (SUMMARY row 13)

| Option | Description | Selected |
|--------|-------------|----------|
| Leave the keyway pair; the 422 marks the fields | Writes derive from the option's `eq 0` conditions only; no new key; server stays the authority on refusals | ✓ |
| Zero it with stash, via a `clears` key | Prevents the bore group's one 422 from the form; a second metadata key the walk must prove | |
| Zero it, derived from relations | Also zeroes the inert `bore_d`/`bore_flat` under Hex — rejected by FEATURES and ARCH | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, Reset clears the stash | Reset means forget this session's edits | ✓ |
| No, stash survives Reset | A pick after Reset could restore a pre-Reset value | |

**User's choice:** keyway pair left to the 422; writes derived from `eq` conditions only; Reset clears the stash
**Notes:** none

---

## Proof & placement

| Option | Description | Selected |
|--------|-------------|----------|
| New `tests/test_selector.py` | Commit slice; imports the Python evaluator from `tests/test_relations.py`; keeps that file to 23 D-12's scope | ✓ |
| Extend `tests/test_relations.py` | One module for the whole vocabulary; grows past the three proofs it was named for | |

| Option | Description | Selected |
|--------|-------------|----------|
| Whole scenario, every step | One `page.on('request')` listener at scenario start; asserted after every step against `model_fields | {quality, mate_teeth}` | ✓ |
| Selector step only | Cheaper; leaves the other steps unguarded | |

| Option | Description | Selected |
|--------|-------------|----------|
| Quick task after 24, before 25's reading | A `calc` change plus the `warning rendered` baseline, kept out of a UI-only phase; 24's closing commit restates the trigger as fired | ✓ |
| Fold into Phase 24 as its last plan | Mixes a `calc` warning change into the selector PR | |
| Leave in v0.5.x | Every hex part picked through the selector warns about two defaults | |

**User's choice:** new `tests/test_selector.py`; scenario-wide request-key assertion; hex-warning debt as a `/gsd-quick` after Phase 24 lands
**Notes:** none

---

## Claude's Discretion

- Schema key name and option-object shape (recommended `selectors: [{title, group, options: [{label, when}]}]`)
- The select's DOM identity (no `name`; metadata-derived id), wrapper class, `.pending` CSS
- Pending reason wording, built from the target field's schema title
- Pick → `update()` directly vs the debounce (recommended: directly, as `hashchange` does)
- Browser step name and placement; how `Swept` carries the select's value
- L42's text; the deliberately-wrong-option red evidence

## Deferred Ideas

- A `clears` key (zero the keyway pair with a stash) — on a user report
- A starter value for D-flat (schema default 8) — on a user report
- The hex warning on default `bore_d`/`bore_flat` — `/gsd-quick` after Phase 24, before Phase 25's reading
- A second selector for the cutout "pick one" — REQUIREMENTS.md "Form follow-ups"
- Refused-vs-inert styling — REQUIREMENTS.md "Form follow-ups"
