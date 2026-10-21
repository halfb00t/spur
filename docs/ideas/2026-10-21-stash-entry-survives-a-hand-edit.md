# A bore-shape stash entry survives a hand edit of its box

Date: 2026-10-21
Source: 24-REVIEW IN-01, the behavioural half (Phase 28 rewords the comment, D-14)
Related files:
- src/spur/static/app.js (`stash`, `write()`, `completePending()`)

## Context
The bore-shape selector zeroes a field when a pick makes it unused and keeps the box's string in
`stash` so a later pick can put it back. Nothing updates the entry when the user then edits the
same box by hand, and a hash navigation keeps it (D-19). 24-REVIEW IN-01 names two orders:

1. On the default part, pick Round (the stash holds the page default). Type a different value,
   then 0, by hand. Pick D-flat: the box returns to the default, not the value last chosen.
2. Open a link with a value set, pick Round (the stash holds it), then follow another link with
   0. Pick D-flat: the box shows the first link's value, from a different gear.

Phase 28 rewords the `stash` comment to say what the map really holds. The behaviour is unchanged.

## Why it matters
The restored box is shown and sent, so a pick can bring back a number the user did not choose
last (L08), although D-19 accepts the second order knowingly.

## Next step
Delete the entry for a field when its box is edited by hand (in `completePending()` or the form's
input listener, keyed on `event.target.name`; selector selects have no name), with a browser case
for each order and the L42 write-rule text amended. Revisit when a user reports a restored value
they did not expect, or when the selectors section next changes.
