---
phase: 10-tooth-tip-chamfer
verified: 2026-09-28T15:15:39Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/phases/10-tooth-tip-chamfer/10-01-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-01-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-02-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-02-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-03-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-03-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-04-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-04-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-05-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-05-SUMMARY.md", "README.md", "bench/RESULTS.md", "bench/sweeps/tip_chamfer.json", "bench/tip_chamfer_spike.py", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md", "docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md", "docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v2:sha256:5af1d2eff979211745c22d94eb36766cb5be619bfc9d164df8659e7bbabb80d2"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 10: Tooth-Tip Chamfer Verification Report

**Phase Goal:** A user can break the tooth-tip edges for a safer, more printable part,
with flanks, root fillets, bore and outside diameter untouched.
**Verified:** 2026-09-28T15:15:39Z
**Status:** passed
**Re-verification:** Yes — the prior report (passed 5/5 at commit `4f191ab`) went stale
because covered source changed after it ran: the code-review loop landed two fixes to
`src/spur/calc.py`'s `derive()` and `tests/test_calc.py` (`54fe020` WR-01, `60d02f7`
CR-01). This report re-verifies at HEAD `13aacb3`.

## What changed since the prior report

- **`54fe020` (WR-01):** `derive()`'s tip-chamfer warning gate compared
  `tip_chamfer_effective(p)` against `round(p.tip_chamfer, 3)`, so a request under
  0.0005 mm rounded to `0.0` on both sides and never warned — the built part silently
  kept the unchamfered default. Fixed by comparing against the raw `p.tip_chamfer`.
- **`60d02f7` (CR-01):** the WR-01 fix's raw-request comparison over-fired: any
  ordinary request with more than 3 decimal places (e.g. `0.1234`) now warned too, and
  borrowed `tip_chamfer_limit(p)[1]`'s reason text even when no limit was anywhere near
  binding — a false stated cause, exactly what CLAUDE.md's "a number the tool prints is
  a number someone will cut metal to" rule exists to prevent. Fixed by splitting into
  two branches: the original 3-dp comparison (`tch < round(p.tip_chamfer, 3)`) attributes
  a reduction to a limit only when that limit binds at the model's own 0.001 mm cut
  resolution; a new `elif p.tip_chamfer > 0 and tch == 0.0` branch catches the
  rounds-to-nothing case and states its true cause (print resolution), never a limit.
  Sub-µm rounding of a nonzero request (0.1234 → 0.123) stays silent, matching every
  other 3-dp field (`root_fillet`, `recess_fillet`, `bore_chamfer`).

Both fixes are confined to `derive()`'s warning logic and its tests — no change to
`tip_chamfer_effective`, `tip_chamfer_limit`, `model.py`, or any DIMS/geometry code path.
Read directly from `src/spur/calc.py` at HEAD (lines 543-563) — matches
`10-REVIEW-FIX.md`'s description exactly.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Setting `tip_chamfer` breaks tooth-tip arc edges at both end faces; flanks, root fillets, bore, cutouts untouched; OD unchanged | VERIFIED | `src/spur/model.py:_tip_edges`/`_chamfer_tips` unchanged by the review fixes (only `calc.py`'s `derive()` and its tests changed); `pytest tests/test_model.py -k "tip_chamfer or tip_arc"` re-run live — 9 passed |
| 2 | Chamfer is the end-face edge break (3D edge op), recorded as new `Lxx` with measured cost; no sizing guidance cited as sourced standard | VERIFIED | `docs/architecture/decision_log.md` `## L29 —` present at line 1045 (unchanged by the fixes); `git grep -nE '0\.1 ?[–-] ?0\.2' -- README.md src docs` returns no match |
| 3 | A chamfer larger than the tip land allows is capped and reported in `warnings` (L03) — **and the warning states a true cause** | VERIFIED | `src/spur/calc.py:tip_chamfer_limit`/`tip_chamfer_effective`, `derive()`'s two-branch warning (lines 543-563) re-read at HEAD; `pytest tests/test_calc.py -k "tip_chamfer or spline_start"` re-run live — **27 passed** (was 25 at the prior report; +2 rows: `test_a_sub_print_precision_tip_chamfer_request_still_warns` rewritten to assert the full string, and a new `print-precision-inside` (`0.1234`→`0.123`) row asserting silence). Full `tests/test_calc.py` re-run live — 92 passed (matches `10-REVIEW-FIX.md`'s stated count, up from 91/454 pre-fix to 92/455 post-fix) |
| 4 | Operator's cost at heaviest allowed config measured against `SPUR_BUILD_TIMEOUT=30s` and recorded in `bench/RESULTS.md` | VERIFIED | `bench/RESULTS.md` unchanged by the review fixes (not in their diff); `pytest tests/test_bench.py -k tip_chamfer` re-run live — 1 passed |
| 5 | Phase 7's regression fixture still passes — `tip_chamfer` defaults to off, every pre-v0.2 parameter set unchanged | VERIFIED | `git diff --exit-code 25b2216 HEAD -- tests/regression/pre_v0_2.json` — 0 diff (also checked against the prior report's baseline `4f191ab` — 0 diff); `pytest tests/regression` re-run live — 86 passed |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Truth 3 in detail (SC3, honesty rule)

The review fixes only strengthened SC3 — a warning must state a true cause. Verified by
reading the current `derive()` source and the test table directly, not by trusting
`10-REVIEW-FIX.md`'s narrative:

- **Rounds-to-nothing (WR-01's target case):** `GearParams(tip_chamfer=0.0004)` →
  `tip_chamfer_effective(p) == 0.0`; `derive()` emits exactly
  `"Tip chamfer 0.0004 mm is below the 0.001 mm resolution it is cut at and was not
  cut."` — names print resolution, not a limit. Test asserts the **full string**
  (not a prefix — CR-01's own lesson was that a prefix assertion let the false-cause
  bug through the first fix's test).
- **Ordinary rounding stays silent (CR-01's fix target):** `tip_chamfer=0.1234` → applied
  `0.123`, `warning=None` — a request well inside every limit (pitch-circle cap 1.75 mm)
  does not warn, even though it isn't 3-dp-aligned. Confirmed live in the parametrize
  table at `tests/test_calc.py:613`.
- **A limit that actually binds still attributes correctly:** e.g. `tip_chamfer=1.8` →
  applied `1.75`, warning `"Tip chamfer reduced to 1.75 mm to keep it above the pitch
  circle."` — unchanged behavior, still correct.
- **Float residue at the printed resolution stays silent:** `teeth=200, module=0.2,
  tip_chamfer=0.2` → pitch-circle limit `0.1999999999999993` rounds to the same `0.2`
  the request carries, no warning — the original pre-WR-01 guarantee, restored by
  CR-01's first branch.

All four rows re-run live in this verification (part of the 27-pass
`-k "tip_chamfer or spline_start"` selection above).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `tip_chamfer` field, Teeth group, after `root_fillet` | VERIFIED | Unchanged by review fixes; re-confirmed at HEAD, line 49 |
| `src/spur/calc.py` | `TIP_CHAMFER_MARGIN`, `spline_start`, `tip_chamfer_limit`, `tip_chamfer_effective`, `DerivedDimensions.tip_chamfer_effective`, two-branch warning in `derive()` | VERIFIED | All present; `derive()`'s warning logic re-read at HEAD lines 543-563, matches `10-REVIEW-FIX.md`'s CR-01 diff exactly |
| `src/spur/model.py` | `_tip_edges`, `_chamfer_tips` last in `_build`, `_outline` reading `calc.spline_start` | VERIFIED | Untouched by the review fixes (not in either fix commit's diff); re-confirmed present |
| `src/spur/static/app.js` | one DIMS row | VERIFIED | Untouched by review fixes; re-confirmed line 24 |
| `tests/test_api.py` | the tip-chamfer link over HTTP; the 24-field contract | VERIFIED | Untouched by review fixes; `pytest tests/test_api.py -k tip_chamfer` re-run live — 2 passed |
| `tests/test_calc.py` | cap at each limit, warning (now with true-cause attribution), no-other-number, rounded cap inside kernel boundary | VERIFIED | `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` now has 16 parametrize rows (was 14; `+print-precision-inside`); `test_a_sub_print_precision_tip_chamfer_request_still_warns` rewritten to assert full string — both re-run passing |
| `tests/test_cli.py` | CLI/API parity, README example run, empty-selection guard | VERIFIED | Untouched by review fixes; re-run passing (3 selected) |
| `bench/tip_chamfer_spike.py` | committed spike, `cost_row(` | VERIFIED | Untouched by review fixes; present |
| `bench/RESULTS.md` | two Phase 10 sections | VERIFIED | Untouched by review fixes; both sections present |
| `bench/sweeps/tip_chamfer.json` | 9 Phase 10 parameter sets | VERIFIED | Untouched by review fixes; present |
| `docs/architecture/decision_log.md` | L29 | VERIFIED | Untouched by review fixes; `## L29 —` present at line 1045 |
| `docs/architecture/gear-maths/implementation.md` / `solid-model/tactics.md` | four calc rows, `_chamfer_tips` in pipeline | VERIFIED | Untouched by review fixes |
| `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` | Severity: must | VERIFIED | File exists, indexed in `docs/tech_debt/INDEX.md` |
| `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` | Severity: must | VERIFIED | File exists, indexed in `docs/tech_debt/INDEX.md` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `model.py (_build)` | `model.py (_chamfer_tips)` | last step, after `_cut_keyway` | WIRED | Unchanged by review fixes; re-confirmed `solid = _chamfer_tips(solid, p, pr)` is `_build`'s final line |
| `model.py (_chamfer_tips)` | `calc.py (tip_chamfer_effective)` | applies exactly the printed cap | WIRED | `tip_chamfer_effective` itself untouched by the review fixes (only `derive()`'s warning gate changed); re-confirmed |
| `calc.py (derive)` | `calc.py (tip_chamfer_limit)` | warning reason text, only when a limit actually binds | WIRED (fixed) | `tch < round(p.tip_chamfer, 3)` branch borrows `tip_chamfer_limit(p)[1]` only when the limit is at or below print resolution; a rounds-to-nothing request takes the separate `elif` branch with its own literal reason string, never borrowing `tip_chamfer_limit`'s text — re-read at HEAD, confirms CR-01's fix landed as described |
| `static/app.js (DIMS)` | `calc.py (DerivedDimensions)` | UI reads a real derived field | WIRED | Untouched by review fixes |
| `README.md (CLI example)` | `tests/test_cli.py (test_readme_export_examples_run)` | example executed as a test | WIRED | Untouched by review fixes |

### Behavioral Spot-Checks (re-run live by verifier, not trusted from SUMMARY/REVIEW-FIX)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Built-solid proof (only tip arcs changed) — regression check, file untouched by fixes | `pytest tests/test_model.py -k "tip_chamfer or tip_arc"` | 9 passed | PASS |
| Cap/warning/true-cause contract — full 3-level check, file changed by both fixes | `pytest tests/test_calc.py -k "tip_chamfer or spline_start"` | 27 passed | PASS |
| Full calc suite (includes the +1 print-precision-inside row) | `pytest tests/test_calc.py` | 92 passed | PASS |
| API link + 422 guard — regression check | `pytest tests/test_api.py -k tip_chamfer` | 2 passed | PASS |
| CLI parity + README example + export guard — regression check | `pytest tests/test_cli.py -k "tip_chamfer or readme"` | 3 passed | PASS |
| Cost sweep pinned — regression check | `pytest tests/test_bench.py -k tip_chamfer` | 1 passed | PASS |
| Pre-v0.2 regression (both baselines) | `pytest tests/regression` + `git diff --exit-code 25b2216 HEAD -- tests/regression/pre_v0_2.json` + `git diff --exit-code 4f191ab HEAD -- tests/regression/pre_v0_2.json` | 86 passed, both diffs empty | PASS |
| Static analysis on the two files the review fixes touched | `ruff check src/spur/calc.py tests/test_calc.py` | All checks passed | PASS |
| Strict typing on the file the review fixes touched | `mypy --strict src/spur/calc.py` | Success, no issues | PASS |
| Debt-marker scan on the two touched files | `grep -n -E "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER" src/spur/calc.py tests/test_calc.py` | no matches | PASS |

Full `make verify` was not re-run in this session (unchanged since the pre-commit hook
ran it green on HEAD `13aacb3` per the task brief: 455 passed, ruff/mypy --strict/import
contracts clean); this report instead re-ran the targeted selections above live plus the
full `tests/test_calc.py` and `tests/regression` suites, which cover every file the
review fixes touched.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-tip-chamfer | 10-02, 10-03, 10-05 | Tip-arc chamfer, positional selector, untouched flanks/fillets/bore/OD | SATISFIED | Unaffected by the review fixes (geometry code untouched); built-solid proof re-run passing; REQUIREMENTS.md marks Complete |
| REQ-tip-chamfer-capped | 10-01, 10-02, 10-04, 10-05 | Capped and reported in warnings; cost measured against `SPUR_BUILD_TIMEOUT` | SATISFIED | Directly strengthened by the review fixes — cap tests (27) re-run passing including the two new true-cause rows; `bench/RESULTS.md` unaffected; REQUIREMENTS.md marks Complete |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s "Phase 10" rows (lines 192-193)
list exactly REQ-tip-chamfer and REQ-tip-chamfer-capped, matching both plans' frontmatter
declarations (`10-01` through `10-05`).

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` (case-insensitive) over the two
files the review fixes touched (`src/spur/calc.py`, `tests/test_calc.py`) returned no
matches. Both tech-debt items filed this phase remain `Severity: must` (deferred with a
named trigger), not `blocker`.

### Human Verification Required

None. All must-haves are code-verifiable and were verified by re-running the actual
tests live (not by trusting SUMMARY/REVIEW-FIX claims), reading `derive()`'s current
source directly against the CR-01/WR-01 commit diffs, and confirming the regression
fixture is byte-identical against two baselines (the phase-start commit `25b2216` and
the prior verification's baseline `4f191ab`).

### Gaps Summary

No gaps. This re-verification confirms the two code-review fixes (`54fe020` WR-01,
`60d02f7` CR-01) changed only `derive()`'s tip-chamfer warning logic and its tests — no
geometry, DIMS, API, CLI, or bench code was touched — and that the fixes correctly
strengthen SC3's honesty guarantee: a rounds-to-nothing request now warns with its true
cause (print resolution), a limit is only cited as the reason when it actually binds at
the model's cut resolution, and ordinary sub-µm rounding of a nonzero request stays
silent like every other 3-dp field in the codebase. All five ROADMAP success criteria
remain independently verified against HEAD `13aacb3`; the Phase 7 regression fixture is
still byte-unchanged (86 tests passing); the full calc-module test count moved from
91→92 (one new parametrize row), all previously-passing assertions unchanged.

---

_Verified: 2026-09-28T15:15:39Z_
_Verifier: Claude (gsd-verifier)_
