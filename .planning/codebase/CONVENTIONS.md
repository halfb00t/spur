---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
# Coding Conventions

**Analysis Date:** 2026-10-02

## Naming Patterns

**Files:**
- `snake_case.py` throughout: `calc.py`, `params.py`, `model.py`, `app.py`, `records.py`, `pool.py`, `cli.py`, `build_errors.py`
- Test files: `test_*.py` (collected by pytest), supporting modules like `composition.py` (not collected, no `test_` prefix)
- Internal implementation details prefixed with underscore: `_fillet_corner()`, `_bore_rim_edges()`, `_build_checked()`, `_cut_bore()` in `model.py`; `_BlobCache`, `_EXPORTS`, `_max_queued_builds()` in `app.py`; `_JsonHandler`, `_JsonFormatter` in `records.py`

**Functions:**
- Domain-specific names over pattern names: `recess_radii()`, `root_fillet()`, `bore_radius()`, `hex_across_flats()`, `keyway_width_effective()`, `tip_chamfer_effective()` in `calc.py`; not `Manager`, `Processor`, `handle`
- Single-letter names acceptable only within short mathematical routines: `z` (teeth), `m` (module), `r` (radius), `rb` (base radius), `ra` (tip radius), `rf` (root radius), `alpha` (pressure angle, radians), `x` (profile shift) — always defined once per module (see `Profile` dataclass in `calc.py`)
- Test function names read as requirements: `test_default_dimensions()`, `test_a_derived_dimensions_result_cannot_be_changed()`, `test_higher_pressure_angle_gives_finer_tips_and_thicker_roots()`, `test_caliper_reading_is_short_for_odd_tooth_counts()`

**Variables:**
- `camelCase` never used; `snake_case` throughout
- Boolean variables use positive forms: `is_paid`, `has_stock` (see `CODING_VALUES.md`)
- Constants in UPPER_CASE: `MIN_WALL`, `MIN_TIP_FDM`, `ROOT_CONTACT`, `TIP_CHAMFER_MARGIN`, `HEX_CELL_CAP`, `TOL`, `BORE_RIM_SLACK` in `calc.py` and `model.py`; `TESSELLATION`, `FLANK_POINTS`, `MEDIA_TYPES` in `model.py`

**Types:**
- Pydantic models inherit from `BaseModel`: `GearParams` (`params.py`), `DerivedDimensions` (`calc.py`), `HealthReport` and `PoolState` (`app.py`), `InfoQuery` (derived from `GearParams` at `app.py`)
- Type aliases with `Literal`: `Format = Literal["stl", "step"]`, `Quality = Literal["preview", "fine"]` in `model.py`
- Frozen dataclass for mathematical types: `Profile` in `calc.py` with properties `r_start` and method `half_angle()`

## Code Style

**Formatting:**
- Line length: 100 characters (widest existing line: 99, enforced by ruff)
- Ruff linter configured with NO automatic formatter (L16 in decision log): `ruff format` is deliberately disabled
- Line length and whitespace linted, but internal arrangement is a human decision
- Continuation layout and comment alignment set by hand for readability (especially in geometry-heavy files like `calc.py`)

**Linting:**
- Ruff enabled: E, F, W (pycodestyle + pyflakes), I (import sorting), N (naming), UP (modern syntax), B (bugbear), SIM (simplifications), C4 (comprehensions), PTH (pathlib), TID (tidy imports), ARG (unused arguments), ERA (commented-out code), TRY (exception antipatterns), LOG/G (logging correctness), PT (pytest), RUF (ruff's own)
- No D/DOC (module/function docstrings are prose, not schema): `calc.py` functions lack docstrings; comments instead explain *why* and carry measurements/constraints
- No ANN (mypy strict already enforces annotations)
- One rule ignored: TRY003 (long exception messages — this project's error messages are the product with parameter names and actionable fixes; see `build_errors.py`)
- Per-file ignores: `tests/*` ignores ARG001 (fixture arguments exist for the reader, not the linter)

**Type Checking:**
- Mypy 1.18+ with `--strict` and `disallow_any_explicit = true`
- `Any` is never written explicitly; genuinely untyped values use `object`, narrowed at use sites
- Library types kept with their original names: `pydantic.json_schema.JsonSchemaValue`, `starlette.datastructures.Message`
- Pydantic plugin enabled: `pydantic.mypy` with `init_typed = true` and `init_forbid_extra = true` to type model `__init__` without implicit `Any`
- CAD kernel imports scoped to ignore missing types: `cadquery.*` and `OCP.*` skip import checking in `pyproject.toml` overrides

**No Comments Unless They Carry Measurement or Constraint:**
- Comments explain *why*, not *what* the code does
- Every constant with a measurement or boundary decision carries a comment with the number: `ROOT_CONTACT = 1e-9  # mm, bisection boundary measured 2026-09-27 on 12 configurations...`
- Measurement comments cite the file and date: `# Measured 2026-09-29 in bench/RESULTS.md "Honeycomb cell-count spike..."`
- A comment restating the code is worse than none; skip it

## Import Organization

**Order:**
1. Standard library imports: `import logging`, `from pathlib import Path`, `from collections.abc import Iterator`
2. Third-party imports: `import cadquery as cq`, `from pydantic import BaseModel`, `from fastapi import FastAPI`
3. Local package imports: `from . import __version__`, `from .calc import derive`, `from .params import GearParams`

**TYPE_CHECKING guard:**
- Used in `calc.py`, `model.py`, `app.py` to avoid circular imports: `if TYPE_CHECKING: from .params import GearParams`
- Allows type hints without runtime import cost

**Path Aliases:**
- None configured in `pyproject.toml` or used in code; full relative imports `from .` used throughout
- `STATIC = Path(__file__).parent / "static"` pattern in `app.py` for file locations

**Import Boundaries Enforced:**
- `calc.py` and `params.py` never import `cadquery` or `OCP` (enforced: contract "The gear maths stays free of the CAD kernel")
- `calc.py` never imports `spur.records` or `logging` (enforced: contract "The gear maths stays free of the logger")
- `cli.py` never imports `app`, `fastapi`, or `starlette` (enforced: contract "The CLI does not inherit web-serving policy")
- `app.py` never imports `cadquery` or `OCP` (enforced: contract "The serving process never imports the CAD kernel", `allow_indirect_imports = false`)
- Violations fail `make verify` (import-linter contract checking)

## Error Handling

**Three Responses (CODING_VALUES.md, L15):**

1. **Refuse** — A conflict between two explicit user choices. Name both fields.
   - Example: `if user_set_both_fields and they_contradict: raise ... "D-flat (bore_flat) and hex bore (bore_hex) cannot both be set"`
   - Raises `ValidationError` at `GearParams` boundary (see `params.py` `check()` method)

2. **Cap and Warn** — A requested dimension that can be trimmed without contradicting explicit user choice. Always silent to data, never silent to user.
   - Example: `root_fillet()` caps silently, `derive()` adds warning to `DerivedDimensions.warnings`
   - Warnings tuple travels through API response and CLI output

3. **Report Nothing** — A value that does not exist. No number at all, only warning.
   - Example: `bore_effective` is `None` when `bore_d` is 0; not a plausible guess
   - Contract: "A wrong number is worse than no number" (L08)

**Exception Handling:**
- `BuildError` and `BuildTimeout` are the only exceptions leaving `model.py` (`src/spur/build_errors.py`)
- Both carry actionable messages: "Bore mouth overlaps the root circle; increase bore_chamfer or reduce bore_d"
- Kernel failures are deterministic for the same parameters — no retry tier
- All other failures: fail loud, once, with actionable message

**Validation:**
- Parameters validated exactly once at `GearParams` boundary (`params.py`)
- Cross-field checks in `@model_validator` decorator (Pydantic v2 pattern)
- After that boundary, types are trusted — no re-validation downstream
- Invariants assert positively, not assumed: `_build_checked()` in `model.py` asserts exactly one valid solid came out

## Logging

**Framework:** JSON-lines structured logger on stderr (Phase 3, D-16)

**Configuration:**
- Configured at composition boundary: `records.configure()` called by `app.py` lifespan and `cli.py` on serve
- One handler, installed exactly once (checked by `test_records.py`)
- Logger owns the formatter (`_JsonFormatter`) and one function per event type

**Event Functions (src/spur/records.py):**
- Intent-named helpers: `build_started()`, `build_failed()`, `export_served()`, `queue_refused()`, `worker_replaced()`
- Called only by `app.py` and `pool.py`, never by direct logging assembly

**Level Knob:**
- `SPUR_LOG_LEVEL` environment variable controls level (default: INFO)
- Read once at `configure()` time

**Constraint:**
- `calc.py` never uses logging even after structured logger lands (pure arithmetic on every keystroke — logging import would add state/failure surface)
- `cli.py` using `print()` to stderr is user-facing output (different from `src/spur` diagnostics), fine

## Comments

**When to Comment:**
- Never restate the code: `x = x + 1  # increment x` is forbidden
- Explain *why* an unusual approach was chosen: `# 1e-9 mm, not TOL: must clear kernel tolerance by five orders...`
- Carry the measurement that settled an argument: `# Measured 2026-09-27: bisection on 12 configurations landed identically on ROOT_CONTACT = 1e-9`
- Cite decisions from decision log: `# L08: never a plausible wrong number`; `# D-06: cache moved to parent process`

**JSDoc/TSDoc:**
- Not used in this project; no docstrings on functions or classes
- All documentation is inline comments (CODING_VALUES.md, Python 3.12 only, no auto-doc tool)

## Function Design

**Size:** No line-count rules (they invite gaming); surface boundary problems when:
- A function cannot be named in one sentence
- A file mixes concerns (transport with geometry, policy with mechanics)
- A parameter list passes ~5 raw arguments (group into a typed object like `GearParams`)
- Nesting passes ~3 deep

**Parameters:** Group ~5+ raw arguments into a typed object
- `GearParams` and `Profile` are the existing examples
- Functions take one parameter dict or object, not many raw floats

**Return Values:**
- Type always explicit at function boundary
- Use `None` for "does not exist" (never a plausible wrong number)
- Use tuple for multiple returns: `(inner_radius, outer_radius)` from `recess_radii()`, `(kk, ww)` from `span_measurement()`
- Collections frozen (tuple, not list) where shared: `DerivedDimensions.warnings` is `tuple`, not `list`

**One Operation Per Routine:**
- `model.py` build pipeline is one product decision per step on purpose (see `_build_checked()` and step-by-step construction)
- Keep that pattern when adding features — do not merge unrelated geometry steps into one function

## Module Design

**Exports:**
- One concern per module: `calc.py` pure maths, `model.py` CAD kernel, `params.py` validation, `app.py` API, `cli.py` command-line
- No wildcard imports: all imports explicit
- Re-exports rare; most functions/classes defined and used where they live

**Barrel Files:**
- `__init__.py` in `src/spur/` exports `__version__` and `int_env()` utility only
- No barrel re-exports of module contents; tests import directly: `from spur.calc import derive`

**Immutability:**
- `GearParams` is frozen (`ConfigDict(frozen=True)`): every field assignment raises
- `DerivedDimensions` is frozen: asserts immutability across readers in concurrent context
- `Profile` is a frozen dataclass: mathematical types do not change

## State Management

**Philosophy:** Almost no state; everything derived from `GearParams` on demand (CODING_VALUES.md)

**Process State (minimal):**
- `model.py`: `_LOCK` (threading.RLock) for kernel access — module-level by necessity, documented where it lives
- `app.py`: `_EXPORTS` (LRU cache, bounded by bytes) for export speed — single-threaded on event loop, safe to lose at any moment
- `pool.py`: `BuildPool` holds worker processes and task queue — state specific to serving HTTP

**No Persistence:**
- Every answer derived from `GearParams` on demand
- Caches are speed optimisation only; losing them is always safe (L07)
- Nothing becomes correct only because something was cached

---

*Convention analysis: 2026-10-02*
