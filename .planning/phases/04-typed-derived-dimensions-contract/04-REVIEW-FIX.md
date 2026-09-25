---
phase: 04-typed-derived-dimensions-contract
fixed_at: 2026-09-25T02:57:09Z
review_path: .planning/phases/04-typed-derived-dimensions-contract/04-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-09-25T02:57:09Z
**Source review:** .planning/phases/04-typed-derived-dimensions-contract/04-REVIEW.md (second pass, `e81e0ec` — internal reviewer plus the Codex lane over the full 22-file phase scope against merge-base `538d26f`)
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (1 warning, 2 info — all three taken, on the human's choice "1" of 2026-09-25)
- Fixed: 3
- Skipped: 0

Fixes were applied by the orchestrator by hand, not by `gsd-code-fixer`; each was gated
by `make verify` (exit 0, 104 passed, mypy clean under `disallow_any_explicit`, 5/5
import contracts) locally and by the pre-commit hook at commit time.

## Fixed Issues

### WR-01: `DerivedDimensions.warnings` is a mutable field on a model that claims to be frozen

**Files modified:** `src/spur/calc.py`, `tests/test_calc.py`
**Commit:** 3483f17
**Applied fix:** The field is `tuple[str, ...]` and `derive()` passes `tuple(warnings)` at
its single construction site; the builder list inside `derive()` is unchanged. A comment
on the field records why (shallow freeze). `test_a_derived_dimensions_result_cannot_be_changed`
now also asserts `isinstance(d.warnings, tuple)` and its docstring says what it proves;
the `== []` assertion became `== ()`. Wire contract unchanged: `model_json_schema()` for
`warnings` is byte-identical (`type: array`, `items: string`), so `/openapi.json`, the UI's
read and the CLI's JSON are untouched — confirmed by the OpenAPI, UI-key and CLI/API
equivalence tests passing unchanged.

### IN-01: `tactics.md`'s Reports bullet omits `derive()`'s `mate_shift` parameter

**Files modified:** `docs/architecture/gear-maths/tactics.md`
**Commit:** 9354323
**Applied fix:** The bullet shows `derive(p, mate_teeth=None, mate_shift=0.0)`, matching the
signature and `implementation.md`'s table.

### IN-02: `gear-maths/implementation.md`'s layout description is stale

**Files modified:** `docs/architecture/gear-maths/implementation.md`
**Commit:** 9354323
**Applied fix:** The layout line no longer states a line count or "no classes but
`Profile`"; it names the two classes, `Profile` and the frozen `DerivedDimensions`
document `derive()` returns.

---

_Fixed: 2026-09-25T02:57:09Z_
_Fixer: Claude (orchestrator, by hand — option 1 of the review's three)_
_Iteration: 1_
