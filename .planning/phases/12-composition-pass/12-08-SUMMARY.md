---
phase: 12-composition-pass
plan: 08
subsystem: testing
tags: [cli, docs, tech-debt, ideas, d-12, d-13]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-07-SUMMARY.md: tests/test_cli.py's COMPOSED/_flags() and the 23-row refusal-parity table this plan's tests sit alongside; 12-01-SUMMARY.md: the human's binding 'seven' groups answer, cited by the two UI ideas' verdict"
provides:
  - "docs/architecture/cli.md's Errors section states the CLI's real exit contract (2 / 1 / 1), pinned by three tests including one that runs the real process"
  - "docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md: the must-debt closed, sha recorded"
  - "The UI pass's verdict: both deferred form ideas are 'not taken', 08 D-09 stands; the browser-test idea records 12-07's cheaper-first-step"
affects: [12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 3761
  tasks: 2
  commits: 3
  plan_head_before: 765249dd538d46bc7d5d79aae13839d7bf859307
  plan_head_after: 22e530d9ffaeffc061822cdb92cc84398792b8c4

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - tests/test_cli.py
    - docs/architecture/cli.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md
    - docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md
    - docs/ideas/2026-09-29-conditional-form-fields.md
    - docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md
    - docs/ideas/2026-09-21-browser-test-for-the-viewer.md
    - docs/ideas/INDEX.md

key-decisions:
  - "cli.md moved to the code, not the code to the doc (10 D-14's human decision stands): src/spur/cli.py is byte-unchanged from c9a169d; only the doc and the tests changed"
  - "Debt resolution followed 09-03's two-commit precedent exactly: the file's `Resolved in:` field and the INDEX cell first hold the fixing commit's own subject (a commit cannot carry its own sha), then a follow-up commit replaces both with the short sha (0deb25a)"
  - "Both deferred UI ideas judged 'not taken' at Phase 12 per D-12: a proof-and-measurement phase must not ship the first bore-specific/field-relation logic in app.js with no UI test; the ignored-field warnings stay the honest signal until a browser test exists or a user reports them insufficient"

patterns-established: []

requirements-completed: []  # REQ-three-interfaces-extended is shared with 12-07 and 12-09 per the shared-ID gate (#2388) -- ready-ids reports 0/1 ready (12-09 has no SUMMARY yet); marks complete once 12-09 (the last declaring plan) finishes.

coverage:
  - id: D1
    description: "docs/architecture/cli.md's Errors section states the real contract: parameter errors exit 2 (argparse's SystemExit(2)); an unknown output extension and every BuildError exit 1 (a SystemExit carrying a string), naming the three tests that pin each case"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_cli.py#test_unknown_output_extension_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_an_unknown_output_extension_exits_1_from_the_real_process"
        status: pass
      - kind: other
        ref: "sed -n '/^## Errors/,/^## Logging/p' docs/architecture/cli.md | grep -c 'exit 1' == 2; grep -c 'exit 2' == 2; grep -cF 'for bad parameters and for an unknown output extension' == 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md is resolved: Status: resolved, Resolved in: 0deb25a, a Resolution section, git mv to resolved/, INDEX row moved (by filename) from Active to Resolved"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: other
        ref: "test -f docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md && ! test -e docs/tech_debt/active/... ; grep -cE '^Resolved in: [0-9a-f]{7,}' resolved file == 1; sed -n '/^## Active/,/^## Resolved/p' INDEX.md | grep -c 'cli-md-claims-exit-2' == 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/ideas/2026-09-29-conditional-form-fields.md and docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md each gain a '## Judged at Phase 12' section: not taken, 08 D-09 stands, the reason, and the new trigger (a browser test exists, or a user reports the ignored-field warnings as insufficient); the conditional-fields file names the schema-driven route if ever taken (enabled_when); the selector file notes the keyway makes it four-plus-one shapes"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: other
        ref: "grep -l '^## Judged at Phase 12' both files | wc -l == 2; grep -c 'enabled_when' conditional-form-fields.md == 1; git diff --exit-code c9a169d -- src/spur/static/app.js == clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "docs/ideas/2026-09-21-browser-test-for-the-viewer.md records that 12-07 took its 'cheaper first step' and gains the trigger 'either UI idea is taken'; docs/ideas/INDEX.md's three rows updated in the same commit"
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: other
        ref: "grep -c 'Phase 12 (2026-09-30)' browser-test file == 1; grep -c 'a browser test exists' across the 3 files each >= 1; git diff c9a169d -- docs/ideas/ removed-line count == 3 (only INDEX rows rewritten, no idea text deleted)"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 08: CLI Exit Contract and UI Pass Verdict Summary

**`docs/architecture/cli.md` now states the CLI's real exit contract (parameter errors exit 2, an unknown extension and every `BuildError` exit 1) pinned by a test that runs the real process, closing the must-debt that found the doc's claim had never been executed; both deferred UI form ideas are recorded "not taken" per D-12, with the schema-driven form (08 D-09) standing unchanged.**

## Performance

- **Duration:** ~35 min (two `make verify` full runs at ~3.5 min each dominate; three `git commit` calls each ran past the 120s foreground timeout under the cold pre-commit `make verify` hook and were moved to background, per the known debt `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — each completed successfully and its own stash of unstaged `docs/ideas/` edits and `.planning/state.json` restored correctly on exit)
- **Started:** 2026-09-30 (this session)
- **Completed:** 2026-09-30
- **Tasks:** 2 (1 tracer, 1 auto)
- **Files modified:** 9

## Accomplishments

- `docs/architecture/cli.md`'s "Errors" section rewritten from the false single-status claim ("Exit 2 ... for bad parameters and for an unknown output extension") to the real three-way contract: a parameter error exits 2 via `argparse`'s own `SystemExit(2)`; an unknown output extension and every `BuildError` both exit 1, because both are raised as `SystemExit("...")` — a `SystemExit` carrying a string argument, which Python prints and exits 1 on. No status changed on `src/spur/cli.py` (byte-unchanged from `c9a169d`, confirmed) — the doc moved to the code, per 10 D-14's human decision.
- `tests/test_cli.py` pins every status the doc now claims: `test_unknown_output_extension_is_refused` gained `assert exc.value.code == "error: output must end in .stl or .step (or pass --format)"`; the tip-selector `BuildError` test gained `assert isinstance(exc.value.code, str)`; and the new `test_an_unknown_output_extension_exits_1_from_the_real_process` runs `python -m spur.cli export` as a real subprocess (measured 2.17 s — the kernel import `cmd_export` pays before the extension check) and asserts its own `returncode == 1` with the sentence on stderr and nothing written — the doc's claim executed once end to end, which is exactly what the debt said had never happened.
- `docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md` resolved following 09-03's exact two-commit precedent: `git mv`'d to `resolved/`, `Status: resolved`, a `## Resolution (2026-09-30)` section naming the doc's new 2/1/1 statuses and the three tests that pin them, `Resolved in:` first held the fixing commit's own subject (a commit cannot carry its own sha), then a follow-up commit (`eceafff`) replaced it with `0deb25a` in both the file and the `docs/tech_debt/INDEX.md` Resolved row.
- Both deferred UI ideas — `docs/ideas/2026-09-29-conditional-form-fields.md` and `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` — gained a `## Judged at Phase 12 (2026-09-30)` section: verdict "not taken", 08 D-09 stands (the form is generated from `/api/schema` and nothing else), reason (a proof-and-measurement phase must not ship the first bore-specific/field-relation logic in `app.js` with no UI test — the ignored-field warnings are the current, honest signal), and a new trigger ("a browser test exists, or a user reports the ignored-field warnings as insufficient"). The conditional-fields file additionally names the schema-driven route if ever taken (a `json_schema_extra` key on the order of `enabled_when`, superseding 08 D-09 with a new `Lxx`); the selector file notes the keyway is a modifier, making it four-plus-one shapes — the largest of the deferred UI changes. `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` gained a `## Phase 12 (2026-09-30)` note recording that 12-07 took its own "cheaper first step" (`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`), leaving the headless-browser cost question open, with the trigger "either UI idea above is taken". `docs/ideas/INDEX.md`'s three rows updated to match, in the same commit; `git diff c9a169d -- docs/ideas/` shows exactly 3 removed lines across the whole directory (the 3 INDEX rows rewritten) — no idea text was deleted from any of the three idea files.
- `make verify`: 907 passed (up from 906 at 12-07's close) — one new test item, +2.17 s measured directly; `ruff`, `mypy --strict`, the four import-linter contracts and the unfinished-work scan all clean, run twice this session (once mid-edit, once on the finished tree).

## Task Commits

Each task was committed atomically (two commits for Task 1, per the debt-resolution precedent's own two-step shape):

1. **Task 1a: Tracer — the CLI's real exit contract from the process's own status to the doc** - `0deb25a` (docs) — `tests/test_cli.py`, `docs/architecture/cli.md`, `docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md` (moved, `Resolved in:` held this commit's own subject as a placeholder)
2. **Task 1b: Record the exit-contract commit's sha in its resolved debt record** - `eceafff` (docs) — replaced the placeholder subject with `0deb25a` in both the debt file and the INDEX row
3. **Task 2: Record the UI pass's verdict in the two UI ideas and the browser-test idea** - `22e530d` (docs) — the four `docs/ideas/` files

**Plan metadata:** committed separately (see below)

## Files Created/Modified

- `tests/test_cli.py` — two new assertions on existing tests, one new subprocess test (`test_an_unknown_output_extension_exits_1_from_the_real_process`); `subprocess`/`sys` added to imports
- `docs/architecture/cli.md` — "Errors" section rewritten to the real 2/1/1 contract, naming the three pinning tests
- `docs/tech_debt/INDEX.md` — the debt's row moved from Active to Resolved (twice: placeholder subject, then the sha)
- `docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md` — moved from `active/`, `Status: resolved`, `Resolved in: 0deb25a`, new `## Resolution (2026-09-30)` section
- `docs/ideas/2026-09-29-conditional-form-fields.md`, `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` — new "## Judged at Phase 12" sections
- `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` — new "## Phase 12" section
- `docs/ideas/INDEX.md` — three rows' "Why it is not now" cells rewritten

## Decisions Made

See `key-decisions` in the frontmatter: cli.py stays byte-unchanged (the doc moves to the code); the debt-resolution two-commit shape followed 09-03's precedent exactly (subject placeholder, then sha); both UI ideas judged "not taken" per D-12's reasoning (no bore-specific/field-relation logic ships in `app.js` with no UI test).

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written; both tasks' `<action>` and `<verify>` steps ran without needing a Rule 1-3 fix.

---

**Total deviations:** 0
**Impact on plan:** None — no scope creep.

## Issues Encountered

- **Commit-timeout debt reproduced (pre-filed, not re-filed):** all three `git commit` invocations this session ran past the harness's 120 s foreground timeout — the pre-commit hook's own cold `make verify` (~3.5 min) — and each was moved to background per this plan's own project-rule instruction (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`, not re-filed). Each commit completed with exit 0. Between the first commit's dispatch and completion, `pre-commit`'s own stash mechanism (stash unstaged changes, run hooks, restore) held the unstaged `docs/ideas/` edits (Task 2, not yet committed) and `.planning/state.json` in the stash; a harness file-change notification during that window reported the four `docs/ideas/` files as reverted to their pre-edit content. This was the expected stash-and-restore behavior, not data loss — confirmed by re-reading the files after the commit completed (edits intact, `git stash list` empty) before proceeding.
- **`docs/architecture/cli.md`'s "Tests" section is stale** (still says "4 tests" against the file's real dozens) — named as a tangent in the plan's `<interfaces>` and left untouched, exactly as instructed; also noted in the resolved debt file's own Resolution section as out of this debt's scope.
- **No debt or idea filed beyond this plan's own scope.** No new tech debt or idea file was created during this plan; only the one pre-named debt was resolved and the three pre-named idea files were updated.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `REQ-three-interfaces-extended` stays open in `REQUIREMENTS.md` (shared with 12-07 and 12-09 per the shared-ID gate, #2388) — `requirements.ready-ids` reports 0/1 this session (12-09 has no SUMMARY yet); marks complete once 12-09 (the last declaring plan) finishes.
- 12-09 (the milestone record) can proceed — this plan's own debt and idea bookkeeping is fully closed, and `make verify` is green (907 tests) with the pre-v0.2 fixture and `app.js` both byte-unchanged from `c9a169d`.
- No blockers.

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `tests/test_cli.py`, `docs/architecture/cli.md`, `docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md`, `docs/ideas/2026-09-29-conditional-form-fields.md`, `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md`, `docs/ideas/2026-09-21-browser-test-for-the-viewer.md`, `docs/ideas/INDEX.md` — all on disk
- CONFIRMED GONE: `docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md`
- FOUND: commits `0deb25a`, `eceafff`, `22e530d` in `git log --oneline --all`
- Re-ran all task and plan-level acceptance criteria: `exit 1`/`exit 2` counts in cli.md's Errors section = 2/2; the false "for bad parameters and for an unknown output extension" phrase = 0; `Resolved in: [0-9a-f]{7,}` = 1; INDEX Active-section grep for the debt = 0; both idea files' "## Judged at Phase 12" = 2; `enabled_when` = 1; `src/spur/static/app.js`, `src/spur/cli.py`, `tests/regression/pre_v0_2.json` all byte-unchanged from `c9a169d`; `docs/ideas/` diff removed-line count = 3 (exactly the 3 INDEX rows rewritten) — all PASS
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_cli.py -q"` — 44 passed; the real-process export exit check — `exit=1`; `make verify` (full suite, run twice this session) — 907 passed, ruff/mypy/import-linter/unfinished-work-scan all clean
- `git rev-list --count 765249d..HEAD` = 3, matching `commits: 3` above
