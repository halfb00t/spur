---
phase: 04-typed-derived-dimensions-contract
reviewed: 2026-09-24T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - docker/smoke.py
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/errors_and_logging.md
  - docs/architecture/gear-maths/implementation.md
  - docs/architecture/gear-maths/strategy.md
  - docs/architecture/gear-maths/tactics.md
  - docs/architecture/http-api.md
  - docs/CODING_VALUES.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md
  - pyproject.toml
  - src/spur/app.py
  - src/spur/calc.py
  - src/spur/cli.py
  - src/spur/params.py
  - src/spur/pool.py
  - tests/test_api.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 04: Code Review Report

**Reviewed:** 2026-09-24
**Depth:** standard
**Files Reviewed:** 20
**Status:** clean

## Summary

This phase turns mypy's `disallow_any_explicit` on and gives `/api/info` and
`/api/health` typed pydantic response models (`DerivedDimensions`, `HealthReport` /
`PoolState`), replacing `derive()`'s old `dict[str, Any]` and the `with_mate()` patch
function, and adds a range-checked `spur info --mate-teeth` on the CLI.

Traced every changed code path against this project's own standing rules (L08: never
print a plausible-but-uncomputed number; L05: an unset parameter never silently changes
the part; L03: caps warn, direct conflicts 422) and against the diff's stated goal
(closing the last two `dict[str, Any]` surfaces without weakening any existing
behaviour):

- `calc.py`'s `derive(p, mate_teeth=None, mate_shift=0.0) -> DerivedDimensions` is the
  single construction site for the report; `mate_teeth`/`centre_distance` are always
  present and `null` (not absent) when no mate was asked about or the pair cannot mesh,
  matching the model's own docstring and the new OpenAPI/UI-sync tests.
- The previous falsy-check bug class (`if q.mate_teeth`/`if ns.mate_teeth`, which would
  have silently treated a `mate_teeth=0` as "no mate" instead of refusing it) is gone at
  every call site — `app.py::info()`, `cli.py::cmd_info()` and `calc.py::derive()` all
  use `is not None` now. Verified by grep across the whole call chain, not just the
  hunks shown in the diff.
- `cli.py`'s new `_mate_teeth()` argparse type mirrors `InfoQuery`'s `ge=6, le=1000`
  with a documented reason it can't import `spur.app` to share it directly (import-linter
  contract), and `tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject`
  reads the bound from `InfoQuery`'s own JSON schema rather than hardcoding it a second
  time, so the two copies can't silently drift without a test failure.
- `pool.py`'s `_run_with_timeout` switch from `*args: object` to
  `Callable[P, bytes]` / `P.args, P.kwargs` plus `functools.partial` is exercised only
  positionally by the one real caller (`export()`); the added generality is real
  (`run_in_executor` is positional-only, so a naive `**kwargs`-forwarding signature would
  type-check while silently dropping a keyword argument) and doesn't change behaviour.
- `params.py`'s `_f()` switched from an explicit `Any` return to a `TypeVar`-generic one.
  Checked this isn't a case of mypy silently accepting an implicit `Any`-to-`T` return
  (pydantic's own `Field()` is annotated `-> Any` at runtime): reproduced the same
  pattern in isolation and confirmed mypy's `pydantic.mypy` plugin substitutes a
  synthetic return type from the `default` argument at the call site rather than
  leaking `Any`, so `strict`'s `warn_return_any` has nothing to flag. `make verify`
  (ruff, mypy --strict with the new `disallow_any_explicit`, the five import-linter
  contracts, the unfinished-work scan, all 104 tests) passes clean on this branch.
- Docs (`decision_log.md`'s new L21, the four `gear-maths/*` files, `http-api.md`,
  `CODING_VALUES.md`, the resolved tech-debt file) match the code: no stray `with_mate`
  or `dict[str, Any]` references remain in `src/`, `tests/`, or `docs/architecture/`;
  the tech-debt item moved from `active/` to `resolved/` with a commit sha, and the
  `INDEX.md` row moved with it in the same diff.

No correctness, security, or robustness defects found. One minor documentation
completeness gap noted below.

## Info

### IN-01: `tactics.md`'s Reports bullet omits `derive()`'s `mate_shift` parameter

**File:** `docs/architecture/gear-maths/tactics.md:14-15`
**Issue:** The "Reports" bullet documents the entry point as
`derive(p, mate_teeth=None)`, but `derive()`'s actual signature (and
`implementation.md`'s own table, three lines below in the same PR) is
`derive(p, mate_teeth=None, mate_shift=0.0)`. A reader who only opens `tactics.md`
would not learn `mate_shift` exists.
**Fix:** Add `mate_shift=0.0` to the signature shown in `tactics.md`'s Reports bullet,
matching `implementation.md`.

---

_Reviewed: 2026-09-24_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
