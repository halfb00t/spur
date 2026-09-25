---
phase: 04-typed-derived-dimensions-contract
reviewed: 2026-09-25T00:00:00Z
depth: standard
files_reviewed: 22
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
  - docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md
  - docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md
  - pyproject.toml
  - src/spur/app.py
  - src/spur/calc.py
  - src/spur/cli.py
  - src/spur/params.py
  - src/spur/pool.py
  - src/spur/records.py
  - tests/test_api.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-09-25T00:00:00Z
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

Second review of this phase's full file scope. No structural findings were supplied for
this pass. This is a careful codebase with strong invariants (frozen/hashable
`GearParams`, `L08` no-plausible-numbers, `L03` cap-and-warn, `calc.py` kernel-free) and
they hold up under inspection: `derive()`'s math (`profile`, `recess_radii`,
`root_fillet`, `centre_distance`, `_involute_angle`) is internally consistent and matches
its own test suite's independent-solver cross-check; the import boundaries (`calc.py`
never imports `cadquery` or `logging`; `spur.app` never imports the CAD kernel even
indirectly; `spur.cli` never imports `spur.app`/`fastapi`/`starlette`) are enforced by
`pyproject.toml`'s import-linter contracts, not merely by convention; `app.py`'s admission
control, byte cache, and gzip-inside-the-slot logic are single-threaded on one event loop
by design and free of the races a naive reading might suspect; the Python-3.10 fix to
`records.py`'s `_JsonHandler` base (`990d1fe`) is minimal and correct — `TYPE_CHECKING`
gates the only 3.11+ construct, and the runtime class is unchanged.

One real defect was found: `DerivedDimensions.warnings` is a plain `list[str]` on a model
declared `ConfigDict(frozen=True)` — Pydantic's `frozen` blocks attribute *reassignment*
only, not mutation of a mutable field's contents, so `result.warnings.clear()` silently
succeeds against a type whose own test claims "cannot be changed" (WR-01). No documentation
staleness beyond the one item carried forward from the first review, plus one newly found
stale line count/class-list in `gear-maths/implementation.md`.

Both claims from the external (codex) reviewer lane were independently re-read against
current source and CONFIRMED; both are reflected below as WR-01 and IN-02.

## Warnings

### WR-01: `DerivedDimensions.warnings` is a mutable field on a model that claims to be frozen (external: codex)

**File:** `src/spur/calc.py:173-214` (field declared at line 214; `model_config` at 173)
**Issue:** `DerivedDimensions` sets `model_config = ConfigDict(frozen=True)`, and
`tests/test_calc.py:38-44` (`test_a_derived_dimensions_result_cannot_be_changed`) asserts
that "DerivedDimensions is frozen, so every field assignment raises" — true for
`setattr(d, name, ...)` on every field, including `warnings`, which the test does
literally check. But Pydantic's `frozen=True` intercepts `__setattr__` only; it does not
make a field's own value immutable. `warnings: list[str]` (line 214) is a plain mutable
list, so `d = derive(p); d.warnings.append("fake warning")` or `d.warnings.clear()`
succeeds silently against the same object the test calls immutable. I independently
verified this is standard Pydantic v2 behaviour (shallow freeze: the model's `__dict__`
slots are locked, not the objects they reference) and confirmed no other
`DerivedDimensions` field is mutable (`bore_effective`, `recess_id`, etc. are all
`float | None`; `mate_teeth` is `int | None`) — `warnings` is the only offender.

Verified this is not exploited by any current call path: `derive()` (`calc.py:224-307`)
is the sole construction site and is called fresh, uncached, per request in
`app.py:358-360` (`/api/info`) and per invocation in `cli.py:96,115` (`cmd_info`,
`cmd_export`); `grep -rn "DerivedDimensions"` across `src/` shows no cache or shared
holder of a `derive()` result — unlike exported bytes (`_EXPORTS` in `app.py`), nothing
memoizes `DerivedDimensions` objects across requests today. So this is not presently a
live data-corruption path (would not meet the Critical bar — no crash, no auth bypass, no
number silently changed on the wire, since a single request's own object is discarded
after serialization). It is, however, a real contract gap in a codebase whose whole
design leans on trusting frozen/hashable types as safe to share (`GearParams` is frozen
specifically so it is a safe cache key, per `L02`/`L07`): the moment a future change adds
any memoization of `derive()` results (a very plausible extension given how aggressively
this codebase already caches — `_BlobCache`, the per-worker solid `lru_cache`), a caller
that mutates `.warnings` in place would corrupt what every other reader of that cache
entry sees, with no test currently able to catch it because the existing frozen-model
test only checks attribute reassignment, not field-content mutation.

**Fix:** Type the field as an immutable collection so the frozen contract is real, not
just field-reassignment-deep:
```python
warnings: tuple[str, ...] = Field(
    description="Sentences about values that were capped, dropped or cannot be computed.")
```
Pydantic coerces a `list[str]` input to `tuple[str, ...]` automatically, so `derive()`'s
own construction site (`warnings=warnings` at `calc.py:304`, where `warnings` is still
built as a local `list[str]`) needs no change. Extend
`test_a_derived_dimensions_result_cannot_be_changed` (or add a sibling test) to assert
`with pytest.raises(AttributeError): d.warnings.append(...)` (a tuple has no `.append`),
closing the gap the current test's docstring already implies but does not prove.

## Info

### IN-01: `tactics.md`'s Reports bullet omits `derive()`'s `mate_shift` parameter (carried forward)

**File:** `docs/architecture/gear-maths/tactics.md:14`
**Issue:** Still reads `**Reports** — \`derive(p, mate_teeth=None)\`, which builds the
\`DerivedDimensions\` document...` — `derive()`'s real signature (`calc.py:224-225`) is
`derive(p, mate_teeth=None, mate_shift=0.0)`. Confirmed unchanged since the first review
(`e1bd08a`), which raised this as its own IN-01; carried forward per this review's
instructions since the underlying signature and doc text are both still exactly as
before.
**Fix:** `**Reports** — \`derive(p, mate_teeth=None, mate_shift=0.0)\`, which builds the
\`DerivedDimensions\` document...`

### IN-02: `gear-maths/implementation.md`'s layout description is stale (external: codex)

**File:** `docs/architecture/gear-maths/implementation.md:5`
**Issue:** Reads "`src/spur/calc.py` — 270 lines, no classes but `Profile`." Verified
directly: `wc -l src/spur/calc.py` reports 343 lines, and `calc.py` now defines a second
class, `DerivedDimensions` (`calc.py:165-221`, a Pydantic `BaseModel`, not the dataclass
`Profile` is), added by this phase (Plan 04-01, `L21`). The rest of the file (the table
of pieces at lines 7-20) already lists `derive(p, mate_teeth=None, mate_shift=0.0)` and
correctly describes it as building "the `DerivedDimensions` document" — only the one-line
summary at the top of the file was not updated to match.
**Fix:** Update the line to something like: "`src/spur/calc.py` — 343 lines; `Profile`
(frozen dataclass) and `DerivedDimensions` (frozen pydantic model) are its only classes."
(and keep the line count loose or drop it, since it will drift again on the next edit).

---

_Reviewed: 2026-09-25T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
