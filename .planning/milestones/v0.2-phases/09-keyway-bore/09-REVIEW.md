---
phase: 09-keyway-bore
reviewed: 2026-09-28T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md
  - docs/ideas/INDEX.md
  - src/spur/calc.py
  - tests/test_calc.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 9: Code Review Report (incremental, post-fix)

**Reviewed:** 2026-09-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** clean

## Summary

Incremental review of the three commits since the iteration-1 report (`a4509c1`):
`f4818a0` (WR-01 fix), `7a88d7a` (WR-02 fix), `882dd76` (Codex cross-review fixes), plus a
`docs/ideas/` entry and its `INDEX.md` row.

Verified, not just read:

- **WR-01** (`derive()`'s new thin-root-wall warning, `src/spur/calc.py:495-500`): its gate
  is `p.bore_d > 0 and 0 <= wall_gap < MIN_WALL`, using the identical `wall_gap = pr.rf -
  (bore_radius(p) + p.bore_chamfer)` measure `check()`'s D-12 rule uses
  (`src/spur/calc.py:296`, `r_bore + p.bore_chamfer > pr.rf - ROOT_CONTACT`). Confirmed
  algebraically the two never contradict: `check()` refuses only `wall_gap < ROOT_CONTACT`
  (1e-9 mm), so every `wall_gap` the warning can see (`>= ROOT_CONTACT` by construction,
  since `GearParams` is validated once at the boundary — CLAUDE.md, L03) already passed
  `check()`. Ran the new 10-case parametrized test
  (`tests/test_calc.py:442-476`) by hand against `calc.py` directly (not just trusting the
  suite) — every expected `{wall_gap:.2f} mm` string matches the live computation exactly,
  including the `bore_clearance` and D-flat interaction cases.
- **WR-02** (`tests/test_model.py:475-488`, the residual-band pin): recomputed
  `wall_gap` for `bore_d=24.724999998` independently — `1.000000082740371e-09`, matching
  the docstring's quoted figure and the comment in `calc.py:35-38` verbatim. Ran the test
  in isolation (`pytest tests/test_model.py::test_the_kernel_can_fail_inside_the_root_
  contact_residual_band`) — passes deterministically, and raises the specific
  `"Geometry kernel produced an invalid solid"` message (the `.isValid()` failure path,
  `model.py:321`), correctly distinguished from the sibling test's
  `"Geometry kernel failed"` (the exception path, `model.py:331`) — not a copy-paste
  mismatch between the two failure modes.
- **Comment accuracy** (`calc.py:29-38`): the claim that `step` in `params.py`'s `_f()` is
  JSON-schema metadata only, never a pydantic `multiple_of`, is correct
  (`params.py:17-23`, only feeds `json_schema_extra`). The claim that `app.js` forwards a
  typed value as-is is correct (`app.js:99`, `q.set(name, input.value)` — the raw string,
  no rounding to the field's `step`). The "11 significant figures" claim for
  `24.724999998` is correct (11 digits).
- Ran the full targeted suite (`pytest tests/test_calc.py tests/test_model.py`, 146
  passed), `ruff check`, `mypy --strict`, and `lint-imports` on the changed files — all
  clean, confirming `calc.py` still imports no CAD kernel (the import-boundary contract
  "The gear maths stays free of the CAD kernel" holds).
- `docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md` follows
  `docs/ideas/TEMPLATE.md`'s structure exactly, and its `INDEX.md` row was added in the
  same commit (`8c09e12`); all three files it cites
  (`docs/HOW_TO_DEVELOP.md`, `.ai_skills/README.md`,
  `.planning/phases/09-keyway-bore/09-VERIFICATION.md`) exist.

No new Critical or Warning findings. One Info-level nit, not worth blocking on.

External reviewer lane `codex` returned no file:line citations ("no actionable findings"),
so there was nothing to independently verify or promote into this report.

## Info

### IN-02: WR-01's warning guard admits an unreachable sub-range at its lower bound

**File:** `src/spur/calc.py:496`
**Issue:** The guard is `0 <= wall_gap < MIN_WALL`, but `wall_gap` values in
`[0, ROOT_CONTACT)` (i.e. `[0, 1e-9)` mm) can never reach `derive()` — `check()` already
refuses any `GearParams` with `wall_gap < ROOT_CONTACT` at construction (`calc.py:296`),
and `derive()` is only ever called with a validated `GearParams` in production. So the
`0 <=` half of the guard is dead: the reachable range is really `[ROOT_CONTACT, MIN_WALL)`.
Harmless — behaviour is identical either way, since the sub-range never occurs — but it
means the code's own condition is looser than what it actually protects against, which
this codebase's own precision culture (CLAUDE.md: "a number... someone will cut metal to";
comments that "carry the measurement") would otherwise flag. The new test's docstring
(`tests/test_calc.py:464-468`, "and only inside (0, MIN_WALL)") already gets this right
with an open lower bound — the code just doesn't match it exactly.
**Fix:** Optional; either tighten the guard to `ROOT_CONTACT <= wall_gap < MIN_WALL` to
make the reachable range explicit in the code (matching the test docstring), or leave a
short comment noting the `0 <=` includes an already-refused sub-range on purpose (defensive
slack, e.g. in case `derive()` is ever called on a bypassed/unvalidated `GearParams` as some
tests already do via `model_copy()`/`model_construct()`). Not urgent either way.

---

## Prior review (iteration 1, `a4509c1`)

- **WR-01** — thin-root-wall bore-chamfer gap not surfaced as a warning: **fixed**
  (`f4818a0`, re-verified above; 10-case regression test added in `882dd76`).
- **WR-02** *(external: codex)* — `ROOT_CONTACT`'s sub-2e-8 mm residual band claimed
  unreachable by any user/API value, but was reachable via an 11-significant-figure
  `bore_d`: **fixed** (`7a88d7a`, comment corrected and pinned with a live kernel-failure
  test; comment's UI-reachability claim further corrected against `app.js` in `882dd76`;
  re-verified above).
- **IN-01** — `keyway_width_effective`'s zero-gate (`p.keyway_width > 0`) is looser than
  its siblings' gates (which also check the paired dimension); deliberately not fixed at
  iteration 1. **Untouched by this incremental diff** — stays Info, no new evidence found
  to raise its severity.

---

_Reviewed: 2026-09-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
