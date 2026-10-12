# Phase 23: Conditional Form Fields - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-11
**Phase:** 23-conditional-form-fields
**Areas discussed:** Relation grammar, Dim reason wording and placement, Relation set and the calc proof, Browser proof shape

---

## Relation grammar

### Shape of `enabled_when`

| Option | Description | Selected |
|--------|-------------|----------|
| Bare list of {field, op, value} | The list is the AND; one shape, ~12 lines of JS, serves Phase 24's selector `when:` lists | ✓ |
| Explicit wrapper {all: [...]} | STACK's proposal; one more level, reserves room for `any` nobody declares | |
| JSON-Schema-flavoured fragment | `{"bore_hex": {"const": 0}}`; reuses JSON Schema keywords inside a non-JSON-Schema key (CF-3) | |

**User's choice:** Bare list of {field, op, value} (recommended)

### Operators

| Option | Description | Selected |
|--------|-------------|----------|
| eq and gt only | The five declared relations and Phase 24's four bore states need nothing else; a sixth op is a stop-and-ask | ✓ |
| eq, ne, gt, ge | ARCH's set; `ne` would serve a Literal gate that is dropped this milestone | |

**User's choice:** eq and gt only (recommended)

### Value and field types

| Option | Description | Selected |
|--------|-------------|----------|
| Numbers only; numeric drivers | Every declared and Phase 24 gate is numeric; the walk rejects a string value or a Literal driver | ✓ |
| Numbers and strings; Literal drivers | `recess_sides eq 'none'` expressible now; a type switch in the JS and an enum check in the test for a case that does not exist | |

**User's choice:** Numbers only (recommended)

### Where a malformed relation is caught

| Option | Description | Selected |
|--------|-------------|----------|
| Typed when() helper + model-driven test | `when(field, op: Literal['eq','gt'], value)`; a bad op fails mypy at the call site; the walk proves fields exist, are numeric, depth 1, schema emits unchanged | ✓ |
| Test only, raw dicts | No helper; mypy sees JsonDict and cannot check `op` | |
| Import-time check after the class body | Fails `import spur.params` on a typo; a second place that knows the grammar in production code | |

**User's choice:** Typed when() helper + model-driven test (recommended)

---

## Dim reason wording and placement

### One wording for both classes, or a class marker?

| Option | Description | Selected |
|--------|-------------|----------|
| One neutral wording, no marker | True for ignored (needs it to matter) and refused (needs it to be allowed); no second schema key; refused styling stays deferred | ✓ |
| Class marker in the metadata | A second key or flag so the form can say "Refused with …"; grows the one-key vocabulary | |

**User's choice:** One neutral wording, no marker (recommended)

### Where the reason renders, and when

| Option | Description | Selected |
|--------|-------------|----------|
| Visible while inactive, own span | `<span class="reason">`, shown only while `.field.inactive`, `aria-describedby`; help `<small>` keeps focus-only | ✓ |
| Tooltip only (title attribute) | No layout change; invisible on touch and in screen readers' normal flow | |
| In the help <small>, shown on focus | Hidden exactly when the dim state is first seen | |

**User's choice:** Visible while inactive, in its own span (recommended)

### One dim tone, or a second "set but ignored" tone

| Option | Description | Selected |
|--------|-------------|----------|
| One tone: .field.inactive only | SC3 names one class; the rendered warning already names set-but-ignored values | ✓ |
| Two tones: .inactive plus .inactive.set | A stronger colour when the value differs from the default; a second rule, assertion and comparison | |

**User's choice:** One tone (recommended)

### Wording pattern

| Option | Description | Selected |
|--------|-------------|----------|
| "Needs {title} = 0" / "Needs {title} above 0" | Two templates, one per op; several conditions join with " and " | ✓ |
| "{title} must be 0" / "must be above 0" | Reads as an instruction to change the gate; wrong for the keyway | |
| Include the gate's current value | "Needs Hex bore A/F = 0 (now 6)"; more text, re-rendered on every input | |

**User's choice:** "Needs {title} = 0" / "Needs {title} above 0" (recommended)
**Notes:** Titles corrected during the discussion: `spoke_count` is "Spoke arms" (not "Spokes"), `hole_count` is "Lightening holes", `hex_cell` is "Honeycomb cell A/F". The template is unchanged; the test derives the text from the schema.

---

## Relation set and the calc proof

### Declare `keyway_* ← bore_d gt 0` as well?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the roadmap's set | Every driver a pure driver (depth 1); the no-bore keyway stays a visible 422 | ✓ |
| Add keyway ← bore_d gt 0 | The first two-condition relation; relaxes depth 1 to "no cycle"; expands SC2's named set | |

**User's choice:** Keep the roadmap's set (recommended)

### What the parity test proves

| Option | Description | Selected |
|--------|-------------|----------|
| Forward direction + reverse coverage | SC2's rows plus: no undeclared field is ever named by a derive() "ignored" sentence | ✓ |
| Forward direction only (SC2 as written) | The minimum; a new calc ignored-rule with no relation caught only by a human | |
| Forward + the converse (relation true ⇒ live) | False today for half-set cutout rows; needs per-row exceptions | |

**User's choice:** Forward direction + reverse coverage (recommended)

### Perturbation values

| Option | Description | Selected |
|--------|-------------|----------|
| The two bounds: ge + step and le | Where a check() rule not gated on the relation would bite; two derive() calls per dependent | ✓ |
| One value: the midpoint | Fewest rows; misses a rule that fires at a bound | |
| A short sweep (5 values) | No distinct proof for the extra rows | |

**User's choice:** The two bounds (recommended)

### Where the kernel-free proofs live

| Option | Description | Selected |
|--------|-------------|----------|
| New tests/test_relations.py in the commit slice | One module for well-formedness, calc parity and the keyword-collision test; runs under `make verify.fast` | ✓ |
| Append to tests/test_calc.py | Light tier too; the walk and keyword test sit oddly beside root geometry | |
| Extend the walk in tests/test_cli.py | Heavy tier: a wrong relation caught at pre-push, not at commit | |

**User's choice:** New tests/test_relations.py (recommended)

---

## Browser proof shape

### Source of the expected inactive set

| Option | Description | Selected |
|--------|-------------|----------|
| Python evaluator over /api/schema, in the test | ~10 lines in browser_session.py; model-driven; two evaluators that must agree is the proof | ✓ |
| Committed golden_inactive.json with a regen target | Pins the JS against itself | |
| Hand-listed expected sets per driver state | A relation added on the model is invisible until someone edits the list | |

**User's choice:** Python evaluator over /api/schema (recommended)

### Page states beyond the 44 golden sets

| Option | Description | Selected |
|--------|-------------|----------|
| Model-driven flips from the schema | One link per distinct gate condition; none named in the test; 422 acceptable | ✓ |
| Hand-picked links | Chosen to answer 200; a new relation invisible until the list grows | |

**User's choice:** Model-driven flips (recommended)
**Notes:** Measured during the discussion: none of the 44 golden records sets a gate field, so under all 44 the inactive set is identical (the seven cutout dims).

### Placement in the Phase 21 scenario

| Option | Description | Selected |
|--------|-------------|----------|
| Extend sweep() + one new step | sweep() reads the inactive set in the same pass; `golden sweep` compares both; one new `inert fields` step | ✓ |
| One new step that re-sweeps | ~44 extra hashchanges for nothing the first pass could not read | |
| Two new steps | Clearest red lines, most duplicated walking | |

**User's choice:** Extend sweep() + one new step (recommended)

### Proof of editable-and-sent

| Option | Description | Selected |
|--------|-------------|----------|
| A real keystroke into the dimmed field | fill hub_d under spoke_count=0; the next request carries it; type into spoke_count, hub_d un-dims before the debounce; Reset | ✓ |
| Attribute checks only | No `disabled`, value kept, query carries it; never proves a keystroke reaches the request | |

**User's choice:** A real keystroke (recommended)

---

## Claude's Discretion

- The hex-warning debt file's severity and trigger (recommended `nice`, trigger: Phase 24's selector or a user report).
- Whether `.invalid` and `.inactive` coexist on the keyway pair under hex (recommended: yes).
- The gate-cost reading for the new step (22 D-06's pattern: the step's own timing, three readings).
- How the two bare-`Field` `Literal` fields carry the key (one shared builder; a mechanism test).
- The dim visual and the `.reason` span's typography.
- The exact rewritten `fields.set(...)` pin token under L41.
- The deliberately-wrong-relation evidence's record.
- L41's text.

## Deferred Ideas

- `keyway_* ← bore_d gt 0` — considered, not declared (depth-1 rule).
- Refused-vs-inert styling / a class marker — REQUIREMENTS "Form follow-ups".
- The two unbacked relations with a calc warning first — idea filed this phase.
- The hex warning on default bore_d/bore_flat — debt filed this phase.
- Cutout "pick one" lock — REQUIREMENTS "Form follow-ups".
