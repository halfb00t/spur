# A bore-shape selector in the web form

Date: 2026-09-27
Status: retired
Retired in: test(24): every pick from every bore shape, the stash across links and the keyed bore -- retire the bore-shape idea
Source: Phase 9 discussion — the human proposed a dropdown to pick round / D-flat / hex /
keyway once four bore shapes exist
Related files:
- src/spur/static/app.js (the schema-driven form; `buildForm`)
- src/spur/params.py (the Bore group: `bore_d`, `bore_flat`, `bore_hex`, the keyway fields)
- .planning/phases/08-hex-bore/08-CONTEXT.md (D-07, D-09 and the "conditional form
  fields" deferral this item supersedes)

## Context

With Phase 9 the Bore group carries a round bore (`bore_d`), an optional D-flat
(`bore_flat`), a replacing hex profile (`bore_hex`) and a keyway (`keyway_width`,
`keyway_depth`) that composes with round and D-flat only. A user reading the form sees
five numeric fields and one warning sentence saying which are ignored; a selector would
say up front which shape is being asked for.

Three locked decisions stand in the way, which is why this is an idea and not a task:

- L27 shipped `bore_hex` as a flat additive field, and research ARCHITECTURE.md Q3
  rejected a `bore_type` discriminator because the keyway is a modifier of round and
  D-flat, not a fourth type — a discriminator would force it to be exclusive with them.
- 08 D-09 locked "no conditional form behaviour": the form is generated from `/api/schema`
  and nothing else, which is what keeps L02 true (a field added once shows up everywhere).
- L05: every published link says `bore_flat=0` for round and `bore_hex=N` for hex. A
  model-level selector either changes what those mean or keeps them as a second way to
  say the same thing.

## Why it matters

Discoverability. The ignored-field warning (08 D-02) is honest but reactive; a selector
would prevent the ignored combination instead of reporting it. The value grows with the
field count — by Phase 11 the form also carries three body-cutout patterns of which
exactly one may be non-zero (REQ-one-cutout-pattern), the same "pick one" shape.

## Next step

Revisit at Phase 12's UI pass (`UI hint: yes`), judged against the whole v0.2 field set —
four bore shapes plus three cutout patterns — not one phase's slice. If taken, the viable
shape is a **UI-only** select in `app.js` that derives its state from the flat fields on
load and still sends the flat fields (the API, CLI and URL contract unchanged), superseding
08 D-09 with a new `Lxx` and accepting the first bore-specific logic in `app.js`. A
model-level `bore_type` field is the schema-driven way to get a select but needs an L05
story for every existing link (aliases or a breaking change) and would be its own phase.

## Judged at Phase 12 (2026-09-30)

Verdict: not taken; 08 D-09 stands (the form is generated from `/api/schema` and nothing
else) (superseded by L41).

Reason: a proof-and-measurement phase must not ship the first bore-specific field-relation
logic in `app.js` with no UI test; the ignored-field warnings are the current, honest
signal.

New trigger: revisit when a browser test exists, or a user reports the ignored-field
warnings as insufficient.

The keyway is a modifier of round and D-flat, not a fifth shape, so a selector is
four-plus-one shapes — why it is the largest of the deferred UI changes.

## Outcome

Phase 24 built the schema-carried route under L42, which follows L41 (the "08 D-09 stands" note above was
superseded by L41, so the form may carry field relations that come from the model and not from `app.js`).
The model carries a `selectors` list, not a `bore_type` field, so every published link means what it meant (L05):
four options -- Round, D-flat, Hex, No bore -- in L41's condition vocabulary, each derived from the flat fields on
load and written back as those same fields when picked. The keyway stays two fields, and the refusals it meets under
Hex or No bore stay the server's `422`. The feature commit is `470b78a`.
