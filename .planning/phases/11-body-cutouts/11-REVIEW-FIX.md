---
phase: 11-body-cutouts
fixed_at: 2026-09-29T19:20:00Z
review_path: .planning/phases/11-body-cutouts/11-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 11: Code Review Fix Report

**Fixed at:** 2026-09-29
**Source review:** `.planning/phases/11-body-cutouts/11-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01 through WR-05; IN-01 excluded, `fix_scope` is
  `critical_warning`)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: Honeycomb spike can hide a failed trial and report `Verdict: held` regardless (external: codex)

**Files modified:** `bench/honeycomb_spike.py`
**Commit:** `5ae6cbd`
**Applied fix:** `slower(a, b)` now returns whichever row has `why` set before falling
back to comparing `request_s` — a failed trial can no longer lose to a successful one
just because the failure paid no export time. The verdict's `reasons` list now also
checks `confirm_row.ok()` and every `spelling_rows` entry (`row.ok()`), not only
`cost_rows` and `confirm_row.request_s`. `CostRow.ok()` already existed in the source
(`why == "" and cells <= target`); the fix suggestion's re-statement of it was already
present, so only `slower()` and the two missing `reasons` checks needed adding. No test
in `tests/test_bench.py` covers the spike's helpers directly, so per the fix instructions
a comment on `slower()` records the invariant instead of adding a new test. Verified with
`ast.parse`, `ruff check`, `mypy --strict` (all clean) and the full `make verify` gate at
commit time (621 tests passed).

### WR-02: L30 decision-log entry inverts its own test's conclusion (external: codex)

**Files modified:** `docs/architecture/decision_log.md`
**Commit:** `89c5548`
**Applied fix:** Reworded the L30 sentence in place (no lines deleted) to distinguish
`check()`'s validation refusal from the kernel's own capability: "the boundary itself
builds and `check()` accepts it; one step past it `check()` refuses, but the kernel
itself still cuts a valid solid there (pinned, validation bypassed) ... proof these are
the part's own `MIN_WALL`, not a kernel limit" — matching what
`test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule` actually asserts.

### WR-03: `implementation.md` documents `cell_count_floor` with a `cap` argument it does not take (external: codex)

**Files modified:** `docs/architecture/gear-maths/implementation.md`
**Commit:** `89c5548`
**Applied fix:** Updated the table row from `cell_count_floor(cap, cell, wall, inner, outer)`
to `cell_count_floor(cell, wall, inner, outer)`, matching the real signature in
`src/spur/calc.py:444`.

### WR-04: README claims the "reverse half-set" cutout case is rejected; it is accepted and warned instead

**Files modified:** `README.md`
**Commit:** `89c5548`
**Applied fix:** Reworded per D-15: the forward direction (count set, dimension still 0)
is a 422 naming the zero fields; the reverse (a dimension set, count still 0) now reads
"builds nothing and warns instead, naming the ignored fields" rather than being claimed
as rejected. Checked `tests/test_cli.py::test_readme_export_examples_run` before editing
— it exercises CLI export command examples elsewhere in the file, not the prose section
touched here, so no example command was altered.

### WR-05: The filleted-spoke removed-volume proof has no closed-form cross-check (external: codex, extended)

**Files modified:** `docs/tech_debt/active/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` (new), `docs/tech_debt/INDEX.md`
**Commit:** `7585fba`
**Applied fix:** Filed as tech debt per the finding's own stated alternative ("...or file
this as tech debt naming the gap explicitly") rather than deriving the closed-form
formula — the phase already decided the filleted row stays pinned, not derived (decision
log L30), so deriving a formula here would have re-litigated a locked decision. Filed
`docs/tech_debt/active/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` from
the project's `TEMPLATE.md`, severity `must`, with a named trigger (`_fillet_corner` next
touched, or the pinned CadQuery/OCP kernel bumped), and added the corresponding row to
`docs/tech_debt/INDEX.md`, in the same commit as the finding's own instruction requires.
Listed here under Fixed Issues (not Skipped) because the finding's own Fix text names
"file this as tech debt" as an acceptable resolution, and that is what was done.

## Skipped Issues

None — all in-scope findings were fixed.

---

_Fixed: 2026-09-29_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
