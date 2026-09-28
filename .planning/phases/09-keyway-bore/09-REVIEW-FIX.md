---
phase: 09-keyway-bore
fixed_at: 2026-09-28T02:36:30Z
review_path: .planning/phases/09-keyway-bore/09-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 09: Code Review Fix Report

**Fixed at:** 2026-09-28T02:36:30Z
**Source review:** .planning/phases/09-keyway-bore/09-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (WR-01, WR-02; IN-01 is Info, out of `critical_warning` scope per
  the orchestrator's instructions)
- Fixed: 2
- Skipped: 0

**Verification environment:** `workflow.use_worktrees` is `false` in `.planning/config.json`
for this project, so all edits, syntax checks, targeted pytest runs and commits ran directly
in the main checkout (`/Users/halfb00t/git/halfb00t/spur`, branch `gsd/phase-09-keyway-bore`),
not an isolated worktree. Each commit ran the real pre-commit hook (`make verify`: ruff, mypy
`--strict`, import-boundary contracts, unfinished-work scan, pytest), which passed both times
(see commit hook output below).

## Fixed Issues

### WR-01: A round/D-flat bore's chamfer can land microns from the root circle with no warning at all

**Files modified:** `src/spur/calc.py`
**Commit:** `f4818a0`
**Applied fix:** Added an `else` branch alongside `derive()`'s existing `if p.bore_hex > 0:`
block: computes `wall_gap = pr.rf - (bore_radius(p) + p.bore_chamfer)` and appends a warning
naming the field and the fix (`"... reduce bore_chamfer or bore_d for more margin."`) whenever
`p.bore_d > 0 and 0 <= wall_gap < MIN_WALL`. Did not move `ROOT_CONTACT` or the `check()`
refusal boundary (D-12 stays locked). Verified against the review's exact repro
(`bore_d=27.905, bore_flat=0` now warns `"Bore chamfer leaves only 0.01 mm of wall..."`) and
confirmed the default `GearParams()` and the existing `keyway_width=3, keyway_depth=1.4` case
(both used in `test_calc.py`'s `d.warnings == ()` assertions) still produce no warning —
their wall gaps (9.46 mm) are far above `MIN_WALL`. `tests/regression/pre_v0_2.json`'s
smallest fixture gap is 1.775 mm, also unaffected; confirmed by running the fixture replay
(`tests/regression`), not by assumption — passed, and `git diff --exit-code` on both fixture
files was clean before and after.

### WR-02: The round/D-flat chamfer-reach rule's "unreachable" rationale overstates what it proves (external: codex)

**Files modified:** `src/spur/calc.py`, `tests/test_model.py`
**Commit:** `7a88d7a`
**Applied fix:** Chose the review's own two-part fix (comment correction + pinning test) over
the project-constraints' offered alternative (raising `ROOT_CONTACT` itself) — surgical, keeps
the locked D-12 constant untouched, and is the change the review actually asked for.
1. Softened the `ROOT_CONTACT` comment (`src/spur/calc.py:15-31`): replaced "cannot be
   produced by any value a user or the API can set" with a statement of what is actually
   proven — unreachable through the UI's own stepped widgets, not proven unreachable for an
   API/CLI caller sending an ordinary high-precision float, since `params.py`'s `step` is
   JSON-schema metadata only. Named the live repro (`bore_d 24.724999998`) and the new test.
2. Added `test_the_kernel_can_fail_inside_the_root_contact_residual_band` to
   `tests/test_model.py`, pinning the kernel's current behaviour at the debt file's own
   19-tooth/module-1.75/chamfer-2/round configuration: `bore_d=24.724999998` puts the gap at
   `1.000000082740371e-09` (`check()` accepts it — `gap > ROOT_CONTACT`, ordinary
   `GearParams()` construction, no `model_copy()` validation bypass needed) and the kernel
   still raises `BuildError` ("Geometry kernel produced an invalid solid for these
   parameters"). This is bit-reproducible (unlike the review's own note that the literal
   "exactly 1e-9 mm" framing from the comment does not reproduce through decimal floats at
   this configuration) and closes the "no regression test pins this" gap the review named.

Re-verified after the constant/comment/test change: both existing D-12 boundary tests at
`tests/test_calc.py:393-415` (`GearParams(bore_d=24.7, bore_chamfer=2, bore_flat=0)` builds;
`GearParams.model_validate({"bore_d": 24.75, ...})` refuses) still pass, along with every
existing D-12 test (`test_a_round_bore_chamfer_that_touches_the_root_is_refused_naming_both`,
`test_the_largest_round_bore_the_chamfer_rule_allows_builds`,
`test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root`,
`test_the_round_bore_rules_never_stack`) — no constant was changed, so these were never at
risk, confirmed anyway. `ROOT_CONTACT`'s numeric value and the refusal boundary are unchanged;
no round or D-flat link that builds today became a `422` (L05, D-12 preserved).

## Verification run for the final tree

`.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py tests/regression -q` →
**222 passed** (up from 221 before WR-02's new test), run twice (once per fix, cumulatively
green both times). `tests/regression/pre_v0_2.json` and `tests/regression/corpus.py`
byte-unchanged throughout (`git diff --exit-code` clean).

`make verify` ran as the pre-commit hook for both commits (`f4818a0`, `7a88d7a`) and passed
both times: `make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest).......................Passed`.
It was not re-run standalone outside the hook after the second commit since no file changed
after that commit; the hook's own run on the final tree is the last recorded pass.

## Tech debt / ideas filed

None. No new debt or idea was surfaced by these two fixes — both are additive
(a warning, a comment correction plus a pinning test) with no deferred follow-up.

---

_Fixed: 2026-09-28T02:36:30Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
