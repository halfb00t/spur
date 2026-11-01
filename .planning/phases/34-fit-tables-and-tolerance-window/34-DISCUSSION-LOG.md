# Phase 34: Fit Tables and Tolerance Window - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-30
**Phase:** 34-fit-tables-and-tolerance-window
**Areas discussed:** Private file and copy, Two-read transcription, Pin switch and guard, Solid and fit rules

---

## Private file and copy

| Option | Description | Selected |
|--------|-------------|----------|
| Path later, at a checkpoint | Same Phase 31 translations, path asked at the transcription checkpoint | |
| Not available | Phase stays blocked | |
| Other | `~/Downloads/ISO standards/` | ✓ |

**User's choice:** `~/Downloads/ISO standards/`. It holds `din-5480-1.pdf` (27 pages) and
`din-5480-2.pdf` (40 pages).

| Option | Description | Selected |
|--------|-------------|----------|
| SPUR_DIN5480_TABLES | Environment variable only, the SPUR_ prefix | ✓ |
| Env var + default path | Falls back to a gitignored path in the repo | |

| Option | Description | Selected |
|--------|-------------|----------|
| JSON + pydantic | One typed document, provenance per row | ✓ |
| CSV per table | Closer to print, needs its own typing | |

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse to start | A set but broken file exits the server and the CLI with the reason | ✓ |
| Null + warning | Treat it like an absent file | |

---

## Two-read transcription

**Finding shown before the questions:** Part 1 Table 7 has no text layer. It is a nomogram image.
Part 2 has a text layer.

| Option | Description | Selected |
|--------|-------------|----------|
| Two blind vision reads | Two agents read the page separately, diff, human settles | ✓ |
| You type, agent reads | Human types Table 7 once | |
| You type it twice | No agent read | |

| Option | Description | Selected |
|--------|-------------|----------|
| Text parse + vision read | pdftotext parser plus an agent reading the rendered pages | ✓ |
| Two text parsers | Both depend on the same text layer | |
| Only rows the tool needs | D_M, M1, A*M1 only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Pick at a checkpoint | As Phase 31 D-06, approved by name | ✓ |
| Decide the set now | | |

| Option | Description | Selected |
|--------|-------------|----------|
| You, from the page | Each disagreement listed with table, row, column and page | ✓ |
| A third read, majority wins | | |

---

## Pin switch and guard

| Option | Description | Selected |
|--------|-------------|----------|
| Table D_M, computed M | Pin from the table, M from `measure_over_pins`, checked against M1 | ✓ |
| Print the table's M1 | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Formula at the thickness limits | Table 6 limits, tabulated pin | ✓ |
| Part 2 deviation factor A* | Linear, needs A* transcribed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Print at tabulated pin | Odd z prints in the tables only | ✓ |
| Print everywhere | Retire ODD_Z_UNCONFIRMED | |
| Keep the gate | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Table's d_Ff1 max | The guard's lower bound for a tabulated size | ✓ |
| A safe construction | One construction at or below the maximum everywhere | |

---

## Solid and fit rules

| Option | Description | Selected |
|--------|-------------|----------|
| Row + warning, name kept | Thickness row and nominal warning, L49 name unchanged | ✓ |
| Name marks it too | Supersede L49 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Warning + null | As the roadmap, FIT_PATTERN unchanged | ✓ |
| 422 under Table 7 | Narrow FIT_PATTERN | |

| Option | Description | Selected |
|--------|-------------|----------|
| Limits only | s_vmax, s_max, s_min, M_Re max, M_Re min | ✓ |
| Limits + tolerances | Also A_s, T_G, T_act, T_eff | |

---

## Claude's Discretion

- the JSON schema's shape;
- where the loader lives;
- the row keys, labels and order;
- the wording of the warnings;
- how the read agents are prompted.

## Deferred Ideas

- Span measurement W_k.
- The hub's space-width window.
- The shift-range exceptions (the existing debt item stays).
