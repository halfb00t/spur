---
phase: 09-keyway-bore
fixed_at: 2026-09-28T07:05:00Z
review_path: .planning/phases/09-keyway-bore/09-REVIEW.md
iteration: 2
findings_in_scope: 5
fixed: 5
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

## Iteration 2 — Codex cross-review of PR #10 (2026-09-28)

HOW_TO_DEVELOP §7: Claude wrote the two iteration-1 fixes, so Codex reviewed them. Driven
from `/gsd-ship` as the doc allows (diff on stdin, JSON verdict back): `codex exec --sandbox
read-only` (codex-cli 0.156.1), scope `a4509c1..7a88d7a -- src tests` (+34/−1).

**Verdict 1: REVISE, confidence 97.** Verbatim summary: "The wall-gap formula, exclusions,
and unchanged refusal boundary are correct. WR-02 reproduced identically in five builds; a
nearby 2e-8 mm gap built successfully. Targeted make test: 36 passed, 100 deselected. Lint,
types, and import contracts passed; full make verify was not run in this read-only review."

| # | Severity | Finding | Verified against the tree |
|---|---|---|---|
| 1 | major | WR-01's warning shipped with no test asserting it (AGENTS.md: new behavior ships with its tests) | `grep -rn "of wall to the root" tests/` → nothing |
| 2 | minor | `calc.py` ~30-34 called the residual band "unreachable through the UI's own stepped widgets"; `app.js` does not enforce `step` | `app.js:68` sets `input.step` (metadata), `:99` forwards `input.value` as typed; no `checkValidity` |
| 3 | info | 24.724999998 has 11 significant figures, not the "8-9" (`calc.py`) / "9" (`test_model.py`) claimed | counted |

**Fix: `882dd76`** — `test(09): pin the thin-root-wall warning; correct WR-02's reach and
precision claims`. One commit, one concern (the review's three findings on the same two
fixes):

- `tests/test_calc.py::test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap`,
  10 parametrized cases on the default gear (rf 14.4375 mm, chamfer 0.4, clearance 0.15):
  bore_d 27.1 silent (0.4125 mm left) / 27.15 warns "0.39 mm" (0.3875 mm) — one step either
  side of `MIN_WALL`; 27.905 → "0.01 mm"; the D-flat case (27.525 / flat 27.4 → "0.20 mm");
  the clearance flip at bore_d 27.2 (0.15 → "0.36 mm", 0 → silent); silent on a hex bore
  with an ignored bore_d, on `bore_d = 0`, on the default and on the keyed default. Values
  were probed with `calc.derive()` before being written; gap 0 (bore_d 27.925) is D-12's
  refusal, already tested.
- `calc.py` comment now says the UI's step buttons never land in the band but a typed value,
  a shared link or an API/CLI caller can (what `app.js` actually does).
- Both comments say 11 significant figures.

Checks on `882dd76`: `ruff check` clean (after one PT006 fix — the parametrize names as a
tuple, the file's existing style); targeted `pytest -k under_min_wall_from_the_root` →
`10 passed`; pre-commit `make verify` → `Passed`; CI run 36388996468 on the PR head → `test
(3.12)` pass 1m58s, `vendor-bundle` pass 7s, `image` pass 1m46s.

**Verdict 2 on `882dd76`: APPROVED, confidence 98, no issues.** Verbatim summary: "882dd76
closes all three findings. The deterministic, requirement-named test covers adjacent bore
steps around MIN_WALL, the D-flat, clearance flip, and hex/no-bore/default/keyed-default
exclusions. Independently calculated rf = 1.75×19/2 − 1.75×1.25 = 14.4375 mm; subtracting
((bore_d + 0.15)/2 + 0.4) gives 0.4125 mm for 27.1 and 0.3875 mm for 27.15. The remaining
expected gaps also match. The ROOT_CONTACT comment correctly distinguishes stepped inputs
from typed/shared values forwarded unchanged by app.js. Both precision statements correctly
say 11 significant figures. Comments retain measurements; no abstraction or CAD import was
introduced. PYTHONDONTWRITEBYTECODE=1 make test PYTEST_ARGS='tests/test_calc.py -q
--capture=sys -p no:cacheprovider': 65 passed. Cache-disabled lint/typecheck and
unfinished-work checks passed; import contracts: 5 kept, 0 broken. Full make verify was not
run in the read-only sandbox. No files changed or debt items filed."

`09-VERIFICATION.md` was re-run by `gsd-verifier` after `882dd76` (its digest covers
`calc.py`, `test_calc.py`, `test_model.py`); see that file for the result.

---

_Fixed: 2026-09-28T07:05:00Z_
_Fixer: Claude (gsd-code-fixer, iteration 1); Claude via /gsd-ship with Codex as reviewer (iteration 2)_
_Iteration: 2_
