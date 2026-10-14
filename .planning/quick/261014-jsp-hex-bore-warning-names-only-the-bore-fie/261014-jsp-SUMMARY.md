---
phase: quick-261014-jsp
plan: 01
subsystem: calc
tags: [warnings, hex-bore, L27, tech-debt]
requires: []
provides:
  - "hex-bore warning names only bore_d / bore_flat set away from their schema defaults"
affects: [calc, api, cli, web-form-warnings]
key-files:
  modified:
    - src/spur/calc.py
    - tests/test_calc.py
    - tests/composition.py
    - tests/test_api.py
    - tests/test_cli.py
    - tests/test_relations.py
    - tests/test_browser.py
    - docs/architecture/decision_log.md
    - README.md
    - docs/tech_debt/INDEX.md
    - docs/ideas/INDEX.md
  created:
    - docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md
  moved:
    - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md -> docs/tech_debt/resolved/
decisions:
  - "Rule: name a round field under a hex bore only when non-zero AND != type(p).model_fields[name].default (read from the model, never a literal)"
  - "L27 amended in place (dated paragraph + pointer in D-02); no new Lxx, L43 stays free"
commits: 1
plan_head_before: 94dfc19e9f03d09eb6eb3a87eab9ed4b00f45729
plan_head_after: c6ca194f2e931c802d97e8ded4c775cf198cc0cc
status: complete
completed: 2026-10-14
actuals:
  tokens: 8500    # chars/4 over the realized diff (33,990 chars)
  tasks: 3
  commits: 1
---

# Quick 261014-jsp: Hex-bore warning names only the fields set away from their defaults

**`?bore_hex=6` and `spur info --bore-hex 6` now answer `"warnings": []`; `bore_hex=6&bore_flat=3` names exactly `bore_flat (3 mm)`.**

## Commit

- `c6ca194` fix(calc): name only the hex-ignored bore fields set away from their defaults (single commit, 14 paths: the debt file shows as delete + add, the rename being under the similarity threshold after its Resolution section).
- It was amended once, before anything left the machine: the first sha was `2f655ae`. The plan's own check for the in-place pointer in L27 failed because my parenthetical wrapped between "this" and "entry"; I rewrapped it and amended.

## Evidence

- Task 1 red (rewritten pins, calc untouched): `57 failed, 56 passed, 512 deselected`. That is 6 parametrized hex cases, 48 composition hex rows, 1 API test, 2 CLI tests. Task 1 green after the calc change: `113 passed, 512 deselected`.
- Task 2 red (calc changed, relation harness untouched): exactly the three predicted failures (`test_every_field_calc_ignores_is_declared`, `test_each_relation_names_the_driver_calc_obeys`, `test_an_ignored_field_without_its_relation_goes_red`). Green after: `58 passed`.
- Reverse-scan count on the full declared set (`_assert_calc_ignores_only(frozenset(_relations()))`): **1**, as at HEAD.
- Browser: `warnings per link (two, one, none expected): [2, 1, 0]`, `2 passed in 21.32s`.
- Collected tests: **1311 before, 1317 after** (`pytest --collect-only -q --no-cov`).
- Gate: `make verify` -> `1317 passed in 185.40s (0:03:05)`, wall 186 s, coverage 97.99 % against the floor of 96, ruff clean, mypy clean, import contracts `5 kept, 0 broken`.
- Commit hook (`make verify.fast`) passed on both the commit and the amend.
- `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json`: clean after Task 1, Task 2, before the commit and against `94dfc19` after it.

## What changed

- `src/spur/calc.py`: the `if p.bore_hex > 0:` filter in `derive()` is `value > 0 and value != type(p).model_fields[name].default`. `type(p)` because calc imports `GearParams` only under `TYPE_CHECKING` and the instance accessor is deprecated. The D-02 comment carries the why: `> 0` named the 9 and 8 mm defaults, `model_fields_set` is lost in `app.py`'s `_gear` and would split cache keys, and the blind spot (an explicit default is silent). The spoke, hole and honeycomb sentences were not touched.
- Tests: the hex test in `test_calc.py` is nine `pytest.param` requirements asserting the hex sentences equal `[expected]`; the composition constant `HEX_IGNORES_ROUND` is gone; API, CLI (README example and parity test with `--bore-d 12`) and the browser link (`bore_hex=6&bore_d=12`) follow.
- `tests/test_relations.py`: the reverse scan runs on a base of every non-zero numeric default one schema step off it (built from the schema, not from `declared`); the driver check's fallback steps off a non-zero default; the dropped-field meta-test is parametrized over `spoke_fillet`, `bore_d`, `bore_flat`.
- Docs: L27 amendment (D-02's main decision stands; the "warning only for non-default fields" alternative it listed as rejected is adopted, because the comparison with the schema default needs no `model_fields_set`) plus the in-place pointer; README sentence; debt retired (`Status: resolved`, `Resolved in:` subject, `git mv`, INDEX row moved, `## Resolution (2026-10-14)`).
- Idea filed per the orchestrator addendum: `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md`, with its row under Open in `docs/ideas/INDEX.md`.

## Deviations from Plan

None to the code scope; no locked file (`app.py`, `params.py`, `model.py`, `pool.py`, `cli.py`, `static/app.js`) was touched.

1. **[Plan wording] Red count for the calc cases.** The plan expected five of the nine `<behavior>` cases red; six were red. `bore_flat-set-named` is also red before the fix, because the old rule named `bore_d (9 mm)` beside `bore_flat (3 mm)`. No effect on the work.
2. **[Plan wording] Commit file count.** The plan's verify script asserts 11 paths in the commit. With the orchestrator addendum's idea file and its INDEX row, the commit holds 14 name-status lines (13 paths; the debt move counts as a delete and an add). I ran the script's other checks individually, and all pass.
3. **[Orchestrator addendum] Two decisions applied** inside Task 3 as dispatched: the L27 wording (point 1) and the idea file (point 2). The plan's statement "no new debt or idea item was filed" no longer holds because of point 2: one idea was filed.
4. The idea template has no "Why not now" heading, so that content sits in the INDEX row's third column and in the file's Next step.

## Debt and ideas

- Retired: `docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md`.
- Filed: `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md` (the deferred half of 24-REVIEW IN-04). No tech-debt item was filed.

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path, file access or schema change. T-261014-01..04 stay accepted as planned.

## Self-Check: PASSED

- FOUND: src/spur/calc.py, tests/test_relations.py, docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md, docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md
- MISSING (as intended): docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
- FOUND commit: c6ca194 (ancestor of HEAD, `git rev-list --count 94dfc19..HEAD` = 1)
- Tracked tree clean; untracked `.DS_Store` and `.planning/quick/` left for the orchestrator.
