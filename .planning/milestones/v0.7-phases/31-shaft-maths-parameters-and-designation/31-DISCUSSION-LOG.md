# Phase 31: Shaft Maths, Parameters and Designation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-24
**Phase:** 31-shaft-maths-parameters-and-designation
**Areas discussed:** Field contract, Copy-gated values, Pin diameter D_Re, Part widening (WR-03)

---

## Field contract

| Option | Description | Selected |
|--------|-------------|----------|
| reference_d | Gear's `bore_d`/`hub_d` suffix style, lower case | ✓ |
| d_b | Short, close to the symbol, loses the DIN capital | |
| d_B | Exact symbol; only mixed-case field; may trip N815 | |

**User's choice:** reference_d

| Option | Description | Selected |
|--------|-------------|----------|
| One `fit` string | Same token as the designation; shape-checked now, table existence in Phase 34 | ✓ |
| Two fields | `quality: int` + `deviation` letter; two URL keys | |

**User's choice:** One `fit` string

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse module, teeth | Same words on separate routes, own ranges and defaults | ✓ |
| Distinct names | `shaft_module`, `shaft_teeth` | |

**User's choice:** Reuse module, teeth

| Option | Description | Selected |
|--------|-------------|----------|
| W 25x1.25x18x8f | PROJECT.md example; x = +0.45 on the range edge | ✓ |
| An interior size | x well inside the range; needs a size confirmed in the copy | |

**User's choice:** W 25x1.25x18x8f

| Option | Description | Selected |
|--------|-------------|----------|
| You decide | Claude proposes proportional values; planner records for review | ✓ |
| Shank Ø = reference_d | Bearing-seat shank, shoulder above the tip | |
| I'll give values | Human types all four | |

**User's choice:** You decide
**Notes:** Claude's example in the question was a shank at 22.25 mm (the root). The
STACK.md:88-96 finding, that a shank at the nominal diameter is the ordinary design and builds
valid with plain fuse, led CONTEXT.md to propose 25 mm instead, for the human's review.

| Option | Description | Selected |
|--------|-------------|----------|
| W 25x1.25x18x8f canonical | One space, shortest numbers, `.`; parser lenient | ✓ |
| Echo the input decimal | Print `,` when typed; breaks round-trip equality | |

**User's choice:** Canonical print form

---

## Copy-gated values

| Option | Description | Selected |
|--------|-------------|----------|
| At a plan checkpoint | Build maths, oracle, codec; stop at checkpoint:human-action for rows and clauses | ✓ |
| Now, in this discussion | Paste rows into CONTEXT.md | |
| Not this phase | Every copy-dependent number null; changes close criteria | |

**User's choice:** At a plan checkpoint

| Option | Description | Selected |
|--------|-------------|----------|
| Copy decides; 0.55·m provisional | Reproduces Hexagon W120 d_f; ASSUMPTION constant until confirmed | ✓ |
| 0.60·m (hobbing) | Does not reproduce Hexagon d_f | |
| A process field | New frozen field, new scope | |

**User's choice:** Copy decides; 0.55·m provisional

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, labelled vendor | KISSsoft W70x3x22, Hexagon W120x3x38x8f as cross-checks, never counted as anchors | ✓ |
| No, copy rows only | Nothing external until the checkpoint | |

**User's choice:** Yes, labelled vendor

| Option | Description | Selected |
|--------|-------------|----------|
| Stop, log, fix | Stop, show clause vs code, new Lxx, guard seen red | ✓ |
| Fix inline | Correct the constant, cite in summary, no Lxx | |

**User's choice:** Stop, log, fix

---

## Pin diameter D_Re

| Option | Description | Selected |
|--------|-------------|----------|
| Computed, labelled | Theoretical pin, contact at m·z + 2xm; Phase 34 switches to the copy's | ✓ |
| Copy's D_Re only | Only anchor sizes print; others null | |
| Null until Phase 34 | Narrows REQ-mre-nominal | |

**User's choice:** Computed, labelled

| Option | Description | Selected |
|--------|-------------|----------|
| Internal d_Ff, not printed | Public construction plus a margin as the guard's lower bound | ✓ |
| Base circle d_b | Simpler, weaker: the fillet may reach above it | |
| Always null until d_Ff proven | Strict; no M_Re until then | |

**User's choice:** Internal d_Ff, not printed

| Option | Description | Selected |
|--------|-------------|----------|
| Rounded, M_Re recomputed | Gauge step (e.g. 0.01 mm), M_Re and contact recomputed | ✓ |
| Exact theoretical | Unbuyable pin | |

**User's choice:** Rounded, M_Re recomputed

---

## Part widening (WR-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 32, with the solid | Fix the parts.py docstring now; WR-03 trigger moves to Phase 32 | ✓ |
| Phase 31, typed internals | Widen now; adds a branch nothing reaches | |

**User's choice:** Phase 32, with the solid

---

## Claude's Discretion

- Solid-only field names and default values (proposed in CONTEXT.md, for review).
- Result type shape, range-refusal placement, oracle file layout, exact `fit` regex.

## Deferred Ideas

- Part widening: Phase 32. The copy's D_Re: Phase 34. Fit existence in the tables: Phase 34.
