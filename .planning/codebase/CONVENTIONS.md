---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# Coding Conventions

**Analysis Date:** 2026-09-21

## Naming Patterns

**Files:**

- Lowercase with underscores: `params.py`, `calc.py`, `model.py`, `app.py`, `cli.py`
- Private modules prefixed with underscore: `_outline()`, `_ring()`, `_build()`

**Functions:**

- Domain terms over pattern names: `recess_radii()`, `root_fillet()`, `_bore_rim_edges()` instead of "Manager", "Processor", "handle"
- Lowercase snake_case: `span_measurement()`, `centre_distance()`, `profile_shift`
- Single-letter names acceptable **only** in short mathematical routines where they are standard symbols: `r` (radius), `rb` (base radius), `ra` (tip radius), `rf` (root radius), `z` (tooth count), `m` (module), `x` (profile shift), `alpha` (pressure angle). File must define them once (see `Profile` dataclass in `src/spur/calc.py`)

**Variables:**

- Descriptive names in domain language: `centre_distance`, `bore_radius`, `recess_depth`
- Temporary/loop vars may be brief: `k`, `i`, `n`, but only in short scopes
- Negative boolean names banned; use affirmative: `is_valid`, `has_stock`, not `is_not_valid`

**Types:**

- Domain-driven naming in `GearParams` (`bore_d`, `bore_flat`, `bore_chamfer`), not generic (`bore_outer`, `bore_inner`)
- `Profile` dataclass with clear fields: `z`, `m`, `alpha`, `r`, `rb`, `ra`, `rf`, `psi_p`

## Code Style

**Formatting:**

- Line length enforced at 100 characters by ruff
- **No automatic formatter** (L16 in decision log): `black`, `yapf`, or `ruff format` are NOT used
- Whitespace and line length linted; arrangement within that constraint is a human decision
- Comments are aligned by hand for geometry readability (`src/spur/model.py` shows this: continuation line alignment is intentional)

**Linting:**

- Tool: `ruff check` (correctness rules only, not reformatting)
- Explicit per-file ignores in `pyproject.toml`:
  - Tests: `ARG001` (unused arguments are named for reader clarity)
- A bare `# noqa` is a violation; suppress by code (`# noqa: E501`) or not at all
- Ruff config: Python 3.10+ target, line-length 100, no DOC (docstrings are prose, not schema), no ANN (mypy --strict already enforces annotations)

**Mypy:**

- Mode: `--strict` (required)
- Python version: 3.12 (type checker floor, not runtime floor; ruff enforces py310)
- Overrides: `cadquery.*` and `OCP.*` have `ignore_missing_imports = true` (CAD kernel ships no stubs)
- Pydantic plugin enabled to see generated `__init__` signatures
- No explicit `disallow_any_explicit` (tracked in tech debt; API's `dict[str, Any]` contracts are by design)

## Import Organization

**Order:**

1. `from __future__ import annotations` (at top of every Python file)
2. Standard library (`import math`, `from pathlib import Path`)
3. Third-party (`import pytest`, `from pydantic import BaseModel`)
4. Local (`from .calc import derive`, `from .params import GearParams`)

**Path Aliases:**

- No path aliases used; imports are absolute from package root (`from spur.calc import derive`)
- Local modules imported with `.` prefix (`from .params import GearParams`)

**Import Boundaries (enforced by import-linter contracts in `pyproject.toml`):**

- **`calc.py` and `params.py` must never import `cadquery` or `OCP`**
  - `calc` runs on every keystroke in the UI (pure, fast arithmetic only)
  - Moment it can reach OpenCascade, that property is lost silently and nobody notices until the form goes slow
  - `model.py` is the only module allowed to import the CAD kernel
- **`app.py`, `cli.py`, and `params.py` must not import from `cadquery`/`OCP` directly**
  - Only `model.py` is the gateway; reaching kernel through `model.py` is allowed (`allow_indirect_imports = true`)
- **`cli.py` must never import `app`, `fastapi`, or `starlette`**
  - Web-serving policy (admission control, bounded queue) is not the CLI's policy (L04)
  - CLI export must never queue behind HTTP requests
- **`spur` package must never import `tests`**
  - Application code is independent of test infrastructure

## Error Handling

**Three Response Patterns:**

1. **Refuse** — conflict between two things the user set explicitly
   - Example: bore flat contradicts bore diameter
   - Raises `ValidationError` at `GearParams` boundary with field names
   - User must resolve; no silent trimming
   - See `check()` in `src/spur/calc.py:114`

2. **Cap and warn** — requested dimension can be trimmed without contradicting an explicit choice
   - Example: requested root fillet trimmed to fit the tooth gap
   - Silent cap happens in helper function (`root_fillet()`, `recess_fillet()`)
   - Warning string added to `derive()` output's `warnings` list
   - User sees it in API response; CLI prints to stderr
   - See `derive()` in `src/spur/calc.py:163`

3. **Report nothing** — a value that does not exist
   - Example: centre distance when gears cannot mesh
   - Return `None`, never a plausible guess (L08)
   - Trigger a warning message instead
   - See `centre_distance()` in `src/spur/calc.py:236`

**BuildError:**

- Only exception that escapes `model.py`
- Caught by `app.py` and CLI, turned into HTTP 422 or `SystemExit(2)`
- Message is user-facing, names the problem and suggests what to try
- See `src/spur/model.py:42`

**Fail fast:**

- No retry tier; kernel failure is deterministic for same parameters, retrying only burns seconds
- Invariant checks assert positively, not assume: `if len(solids) != 1 or not solids[0].isValid(): raise BuildError(...)`

## Logging

**Current state:** No logging configured (tracked gap in `docs/tech_debt/active/2026-09-21-no-structured-logging.md`)

**Until logging is configured deliberately:**

- **Do NOT add `print()` for diagnostics in `src/`**
  - This is how logging decisions get made by accident
  - `cli.py` printing to stderr is user-facing output (exceptions, warnings) — that is fine
- **`calc.py` should use `warnings` module** only, not logging
  - Pure code; logging is deferred until the boundary

**When logging lands:**

- Decision will be logged in `docs/architecture/decision_log.md` as new `Lxx`
- Update this section and configure it deliberately

## Comments

**When to Comment:**

- Must carry measurement or constraint that forced the choice
- Never restate what the code says
- Examples (from the codebase):
  - `# 1578 MiB resident without this, 360 MiB with it` — memory measured
  - `# ~50x slower on a many-toothed outline` — performance measured
  - `# 1g made ~5% of those requests fail` — tradeoff measured
  - `# glibc keeps freed arenas to reuse and never returns them` — architectural constraint
  - `# The CAD kernel ships no type information` — why override exists

**JSDoc/TSDoc:**

- Function docstrings: one-line or short paragraph, plain English
- Parameter names documented in docstring when not obvious from signature
- Exception types documented if not standard
- Example from `src/spur/calc.py:154`: `"""Base tangent length (Wildhaber span) over k teeth, nominal (zero backlash)."""`

## Validation

**Boundary:**

- `GearParams` is the inbound validation boundary for all three front ends (API query, CLI args, tests)
- All range checks expressed as Pydantic field metadata (`ge`, `le`)
- Cross-field feasibility checked in `GearParams._feasible()` validator (calls `calc.check()`)
- Raise `PydanticCustomError` with field names and actionable message

**After boundary:**

- Trust the types; do not re-validate downstream
- `derive()`, `model.build()`, etc. assume parameters are sound
- If a `Profile` or other derived type cannot be created, that is an invariant violation, not a user error

**Invariants:**

- Asserted positively, never assumed
- Example: `if len(solids) != 1 or not solids[0].isValid(): raise BuildError(...)`
- See `_build()` in `src/spur/model.py:235`

## Function Design

**Size and Scope:**

- One operation per routine; `model.py` build pipeline is one product decision per step on purpose (`_gear_blank()`, `_cut_face_recesses()`, `_cut_bore()`)
- If a function cannot be named in one sentence, surface boundary problem to human

**Parameters:**

- ~5 raw arguments → group into typed object (examples: `GearParams`, `Profile`)
- Example: `centre_distance(p: GearParams, mate_teeth: int, mate_shift: float = 0.0)` instead of scattered floats

**Return Values:**

- Explicit types at every boundary
- Vendor types stop at their boundary: `cadquery` objects do not escape `model.py`
- `model.py` exports bytes (binary STL/STEP), `dict[str, Any]` (JSON schema, derived dimensions), or `cq.Solid` (only within module)

## Module Design

**Exports:**

- Each module has a clear responsibility (see `ARCHITECTURE.md`)
- Public functions named without leading underscore; private with underscore
- Example: `export()` is public; `_build()`, `_cut_bore()` are private build steps

**Barrel Files:**

- `__init__.py` in `src/spur/` exports version and helper only:
  ```python
  __version__ = "0.1.0"
  def int_env(name: str, default: int) -> int: ...
  ```
- No `from .module import *` re-exports

**Module Graph:**

- Designed object, not an accident; enforced by import-linter contracts
- Addition of a new module means deciding its place in the graph and usually adding a contract
- See import boundaries section above

## State Management

**Almost none, and it stays that way:**

- Nothing persisted; every answer derived from `GearParams` on demand
- Caches (`SOLID_CACHE`, `EXPORT_CACHE`) are speed optimisation, safe to lose anytime
- One piece of true process state: kernel lock (`threading.RLock()` in `model.py`), documented where it lives
- Build semaphore (`threading.BoundedSemaphore()` in `app.py`), documented in module docstring

**No module-level dicts or mutable singletons**

- If this project ever needs durable state, that is a decision (`Lxx`) and a phase, not silent code

---

*Convention analysis: 2026-09-21*
