---
phase: 14-honest-record
plan: 01
subsystem: calc
tags: [warnings, derive, root-fillet, pitch-circle, readme, tech-debt]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: "spline_start and the lead-in height the tip-chamfer cap already reads; the debt file that named the false README sentence"
provides:
  - "derive() warns when the root fillet's straight chord ends above the pitch circle, naming the height at 3 dp"
  - "a 15-row test pinning the warning at the three debt configurations and one field step either side of each crossing"
  - "README's root-fillets bullet and _outline's docstring state the real condition and cite the warning"
  - "the root-lead-in debt retired with both shas on file"
affects: [14-02, 14-03, decision log L33]

actuals:
  tokens: 3930
  tasks: 3
  commits: 4
plan_head_before: ac6de10f228920f7e71c10b5743050f0d7d09f82
plan_head_after: 775ee6ffa6992474287b69ba56a6e65cc1880a22

tech-stack:
  added: []
  patterns:
    - "derive() compares at the resolution it prints (round(h, 3) > 0), the tip-chamfer branch's rule applied to a second warning"
    - "expected warning strings captured from derive() on the pinned code and asserted in full, never typed"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - tests/test_calc.py
    - README.md
    - src/spur/model.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md

key-decisions:
  - "The warning fires at round(h, 3) > 0 and sits directly after 'Root fillet reduced ...' (D-01, D-04)"
  - "README carries one clause beyond D-12's draft: the profile shift must also exceed 0.125, because the chord is capped halfway up the tooth below it (proven by the mid-tooth rows)"
  - "The debt-x1.0-pa14.5 string prints 0.562, not CONTEXT's draft 0.563: Python rounds the exact binary 0.5625 half-to-even"

requirements-completed: [REQ-root-lead-in-warned, REQ-readme-root-zone-states-the-limit]

coverage:
  - id: D1
    description: "derive() warns, naming the height at 3 dp, when the root fillet's chord ends above the pitch circle; silent on the default gear, at an exact touch and under the print resolution"
    requirement: "REQ-root-lead-in-warned"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle"
        status: pass
      - kind: other
        ref: ".venv/bin/spur info --profile-shift 0.75 --pressure-angle 20 (warnings list equals the one sentence)"
        status: pass
      - kind: other
        ref: "TestClient /api/info: default gear warnings == [], {0.75, 20} prints the sentence"
        status: pass
    human_judgment: false
  - id: D2
    description: "README's root-fillets bullet and _outline's docstring state the real condition (1.188 mm below the pitch circle on the default gear; above it when the root fillet exceeds half the dedendum and the profile shift exceeds 0.125) and cite the warning, with no unproven number"
    requirement: "REQ-readme-root-zone-states-the-limit"
    verification:
      - kind: other
        ref: "Task 3 README verify: bullet numbers subset of {1.188, 1.25, 0.125}, no micron figure, 'non-working' gone"
        status: pass
      - kind: other
        ref: "Task 3 model.py verify: AST with docstrings blanked equals 5d9e907's"
        status: pass
    human_judgment: false
  - id: D3
    description: "The root-lead-in debt file retires in the README commit with the README commit's sha recorded by a follow-up, INDEX consistent, the pre-v0.2 fixture byte-identical"
    requirement: "REQ-readme-root-zone-states-the-limit"
    verification:
      - kind: other
        ref: "Task 3 sha-consistency verify (Resolved in: == INDEX cell == the retiring commit's sha)"
        status: pass
      - kind: unit
        ref: "tests/regression/test_pre_v0_2.py (85 passed with the fixture byte-identical to 5d9e907)"
        status: pass
    human_judgment: false

duration: 22 min
completed: 2026-10-03
status: complete
---

# Phase 14 Plan 01: The Honest Record for the Root Lead-In Summary

**`derive()` now warns when the root fillet's straight chord ends above the pitch circle, naming the height at 3 dp, and README and `_outline` state where the chord really ends instead of calling it non-working; the debt that named the false sentence is retired.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-10-03T02:47:25Z
- **Completed:** 2026-10-03T03:09:36Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- `calc.derive` appends one sentence when `round(spline_start(pr, rfil) - pr.r, 3) > 0`: "The flank starts with a straight chord reaching {h:.3f} mm above the pitch circle, where it deviates from the involute: the root fillet is larger than half the dedendum." It quotes no deviation figure and no remedy (D-02). No `GearParams` field, no `DerivedDimensions` field, outline unchanged.
- `test_the_root_lead_in_warns_when_it_ends_above_the_pitch_circle` has 15 rows and asserts, per row, the fillet actually used (so no row can sit on the `0.45 x gap` cap by accident), the chord height, and the full warning string.
- README's root-fillets bullet states the condition and the default gear's number, and cites `warnings`; `_outline`'s docstring points at the warning. `tests/regression/pre_v0_2.json`, `params.py` and every line of `model.py` code are byte-identical to `5d9e907`.
- `2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` moved to `resolved/` in the README commit (`825095f`); the follow-up (`775ee6f`) wrote that sha into `Resolved in:` and the INDEX cell.

## Task Commits

1. **Task 1: Tracer, the lead-in warning end to end** - `13857e1` (feat)
2. **Task 2: Prove the warning at every step either side of its crossing** - `ac607d7` (test)
3. **Task 3: README and `_outline` state where the chord really ends; retire the debt** - `825095f` (docs), then `775ee6f` (docs, records `825095f` in the debt file and INDEX)

**Plan metadata:** the SUMMARY/STATE/ROADMAP commit that follows this file.

## The 15 rows (captured from `derive()` on the pinned code)

Heights are `spline_start(pr, root_fillet(p)) - pr.r`; every printed figure matched the planning-time prints in the plan's behavior list, so there is no difference to record.

| Row | fillet used | height (mm) | printed |
|---|---|---|---|
| default | 0.5 | -1.1875 | silent |
| debt-x1.0-pa14.5 | 0.5 | 0.5625 | 0.562 |
| debt-x0.75-pa20 | 0.5 | 0.125 | 0.125 |
| x-step-silent (x 0.65, pa 14.5) | 0.5 | -0.05 | silent |
| x-step-warns (x 0.70, pa 14.5) | 0.5 | 0.0375 | 0.038 |
| fillet-step-silent ({0.75, 20}, fillet 0.40) | 0.4 | -0.075 | silent |
| fillet-step-warns ({0.75, 20}, fillet 0.45) | 0.45 | 0.025 | 0.025 |
| module-step-warns ({1.0, 14.5}, m 3.95) | 0.5 | 0.0125 | 0.013 |
| module-step-silent ({1.0, 14.5}, m 4.05) | 0.5 | -0.0125 | silent |
| mid-tooth-silent (x 0.10, fillet 2) | 1.018 | -0.04375 | silent |
| mid-tooth-touch (x 0.125, fillet 2) | 1.012 | 0.0 | silent (an exact touch is not above) |
| mid-tooth-warns (x 0.15, fillet 2) | 1.006 | 0.04375 | 0.044 |
| no-fillet ({1.0, 14.5}, fillet 0) | 0.0 | -0.4375 | silent |
| print-precision-silent (m 3.9988) | 0.5 | 0.0003 | silent (never prints 0.000) |
| print-precision-warns (m 3.996) | 0.5 | 0.001 | 0.001 |

## README bullet, before and after

Before (`5d9e907`): "... Where a fillet needs room above the base circle, the flank starts with a short chord onto the involute, in the non-working root zone."

After: "... Where a fillet needs room above the base circle, the flank starts with a short chord onto the involute: 1.188 mm below the pitch circle on the default gear, but above it, where the chord deviates from the true involute, when the root fillet exceeds half the dedendum, `(1.25 − x)·m / 2`, and the profile shift `x` exceeds 0.125 (below that shift the chord stops halfway up the tooth, at or under the pitch circle). `warnings` says how far."

## Decisions Made

- The warning sits directly after "Root fillet reduced ..." (D-04's recommendation); nothing asserts position, since tests filter by prefix and the UI lists every warning.
- README adds one clause to D-12's draft (profile shift above 0.125). D-12's draft alone ("above it when the root fillet exceeds half the dedendum") is false wherever the halfway cap binds at x <= 0.125; the mid-tooth trio proves the 0.125 floor. This is the plan's flagged assumption, kept as planned.
- Plain `git commit` with the hook running for every commit (the `make verify` hook exceeds `gsd_run query commit`'s 30 s timeout); no `--no-verify`.

## Deviations from Plan

None - plan executed exactly as written.

Two formatting adjustments inside Task 2's own scope, neither a deviation: rows over 100 columns were wrapped to satisfy ruff's line length, and the generated block was produced by a scratch script (outside the repo) rather than typed row by row.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. The warning adds text to existing `warnings` surfaces (`/api/info`, `spur info`, the UI panel); no endpoint, auth path or schema changed.

## Verification

- `make verify` (run after the last task commit): `926 passed in 216.55s (0:03:36)`, exit 0. The pre-commit hook ran the same gate and passed on all four task commits.
- `pytest tests/test_calc.py -k root_lead_in`: `15 passed`.
- `spur info --profile-shift 0.75 --pressure-angle 20` prints exactly the one warning; `/api/info` on the default gear prints `[]`.
- `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py` exits 0; `tests/regression/test_pre_v0_2.py` passes; `model.py` differs from `5d9e907` in docstrings only (AST check).

## Debt

No new debt item filed. One retired: `docs/tech_debt/resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` (`Resolved in: 825095f`; the warning commit is `13857e1`). Its Resolution says "Decision log L33 records the choice"; L33 lands in 14-03, so that sentence is forward-referencing until then.

## Self-Check: PASSED

All five key files exist; the four commits (`13857e1`, `ac607d7`, `825095f`, `775ee6f`) are in `git log`; the active debt path is gone; the fixture and `params.py` are byte-identical to `5d9e907`.

## Next Phase Readiness

Ready for 14-02 (the filleted-spoke closed form and the tightened volume bar). `REQ-root-lead-in-warned` and `REQ-readme-root-zone-states-the-limit` are delivered here; `requirements.ready-ids` reported 0/2 ready, so the shared-ID gate held them open for a sibling plan.
