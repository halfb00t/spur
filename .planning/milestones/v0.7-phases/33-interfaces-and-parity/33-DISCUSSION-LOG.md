# Phase 33: Interfaces and Parity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-27
**Phase:** 33-interfaces-and-parity
**Areas discussed:** WR-02 fix shape, Designation vs fields, Web designation input, Part switch behaviour

---

## WR-02 fix shape

| Option | Description | Selected |
|--------|-------------|----------|
| API refuses it | A 422 from the app.py query layer, in the server's words. The existing `rejected` map marks the box. Amends L44 "The server decides". | ✓ |
| Page fills the box from server | The API echoes the value it read and the page writes it into the box. | |
| Server-worded warning only | Builds under a blank box with a warning. Fails criterion 4 as written. | |

| Option | Description | Selected |
|--------|-------------|----------|
| What box can't hold | Rule = Chromium number-input blank read-back, probed per field. | ✓ |
| Strict decimal regex | `-?\d+(\.\d+)?`; also refuses `1e1`, `.5`. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Gear+shaft API, not CLI | One shared rule in both query layers. | ✓ |
| API and CLI | The CLI refuses `+22` and `5.` too. | |
| Gear API only | The shaft stays permissive. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Names token and form | Quote the token and suggest the canonical form when unambiguous. | ✓ |
| Generic | Pydantic-style text with no token echo. | |
| You decide | The planner picks the wording. | |

**Notes:** a check at discuss time found no non-canonical number token in either regression
fixture.

---

## Designation vs fields

| Option | Description | Selected |
|--------|-------------|----------|
| Any overlap is 422 | Designation plus any spline field gives a 422, whatever the values. | ✓ |
| Only contradicting values | Agreeing duplicates are accepted. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, they combine | The solid fields combine with a designation. | ✓ |
| No, designation alone | Solid fields take their defaults. | |

| Option | Description | Selected |
|--------|-------------|----------|
| designation / --designation | The same word as the result row. | ✓ |
| w / --w | Short and cryptic. | |

---

## Web designation input

| Option | Description | Selected |
|--------|-------------|----------|
| Print-only | A result row only, with no new route. | ✓ |
| Paste box | `GET /api/shaft/designation?text=` fills the flat fields. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Ignored | `designation=` in a page link is an unknown key. | ✓ |
| Refused visibly | Page-worded refusal. | |
| Accepted | The page forwards it to the API. | |

---

## Part switch behaviour

| Option | Description | Selected |
|--------|-------------|----------|
| Two-button toggle | A Gear \| Shaft radio pair above #params. | ✓ |
| `<select>` | A dropdown. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Part defaults | Every switch loads defaults, so the URL equals the form. | ✓ |
| Restore last values | Per-part in-memory stash. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Follow field edits | The same hash-write call as a field edit. | ✓ |
| Push entry | Back undoes the switch. | |
| Replace | No history entry. | |

| Option | Description | Selected |
|--------|-------------|----------|
| Page message, no build | Page-worded; a logged exception to L02/L44. | ✓ |
| Ask the server | A new `GET /api/part?name=` route. | |

---

## Claude's Discretion

- The parity test's comparison precision and its fixed shaft set.
- How a `null` row is displayed.
- The title, sub-heading, aria-label and hint text per part.
- The viewer framing for a long shaft.
- The CLI flag spelling.
- `enabled_when` for the shank fields.
- The README wording.

## Deferred Ideas

- A web designation paste box.
- A `<select>` part control once there is a third part.
- A strict number rule on the CLI.
