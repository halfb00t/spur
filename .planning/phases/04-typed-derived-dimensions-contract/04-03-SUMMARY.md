---
phase: 04-typed-derived-dimensions-contract
plan: 03
subsystem: api-contract
tags: [mypy, pydantic, cli, argparse, decision-log, tech-debt]

# Dependency graph
requires:
  - phase: 04-typed-derived-dimensions-contract
    provides: "Plan 04-01's DerivedDimensions and Plan 04-02's HealthReport/PoolState,
      both frozen pydantic models with no default on any field -- the fact that closed
      the reason L14 kept disallow_any_explicit off, and left exactly six class-line
      explicit-Any errors (04-02-SUMMARY.md's 'Intermediate Proof')"
provides:
  - "`spur.cli._mate_teeth`, the argparse `type=` that gives `--mate-teeth` `InfoQuery`'s exact ge=6/le=1000 bounds"
  - "`disallow_any_explicit = true` in `pyproject.toml`'s `[tool.mypy]`, globally, with no per-module override"
  - "`[tool.pydantic-mypy]` with `init_typed = true` and `init_forbid_extra = true`, which removes the plugin's own generated-initialiser `Any` on every model's class line"
  - "`L21` in `docs/architecture/decision_log.md`, superseding `L14`"
  - "the house-rule bullet in `docs/CODING_VALUES.md`, citing `L21`"
  - "`docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md`, `Status: resolved`, `git mv`'d, `INDEX.md` row moved"
affects: []

# Actuals (#2632)
actuals:
  tokens: 4285
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "An argparse `type=` function that owns a hand-copied bound, pinned to its
      source-of-truth pydantic field by a test that reads the field's own JSON schema
      rather than a hard-coded number, because the import-linter contract forbids the
      module itself from importing the source (cli.py cannot import app.py)"

key-files:
  created: []
  modified:
    - src/spur/cli.py
    - tests/test_cli.py
    - docs/architecture/decision_log.md
    - docs/CODING_VALUES.md
    - pyproject.toml
    - docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "_mate_teeth's two bounds are written directly in cli.py rather than imported --
    the import-linter contract 'The CLI does not inherit web-serving policy' forbids
    spur.cli -> spur.app, so a shared constant would have to live in params.py for no
    gain the test does not already give (flagged assumption 1). The pin is enforced by
    test_info_rejects_a_mate_the_api_would_reject reading InfoQuery.model_json_schema()."
  - "--mate-teeth 0 changes meaning: it used to mean 'no mate' via an `or None`
    fallback (04-01's flagged assumption 2, kept byte-for-byte until this plan); it now
    exits 2 like every other out-of-range value, matching the API's 422 for the same
    input (R-2, human decision 2026-09-24)."
  - "R-1 (human decision, 2026-09-24): the six pydantic-plugin class-line errors are
    removed via [tool.pydantic-mypy]'s init_typed/init_forbid_extra, not six per-class
    explicit-Any suppression comments. Verified during planning on a scratch copy: 6 ->
    0 errors, 99 tests passing, no model gained extra=\"forbid\"."
  - "The debt file's Resolved in: names 013900d (Plan 04-01 Task 1's commit, which gave
    the report its real shape), not this plan's own commit -- a file cannot carry its
    own commit's sha, and CLAUDE.md's lifecycle wants the commit that landed the fix."

patterns-established:
  - "A tech-debt item's own 'Next step' text becomes the checklist a later plan proves
    against line by line, rather than being re-derived from the code at resolution time."

requirements-completed: [REQ-typed-derived-dimensions, REQ-cli-parity]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "spur info --mate-teeth accepts exactly the range InfoQuery.mate_teeth
      enforces and rejects anything else through argparse's error path: exit 2, an
      --mate-teeth message on stderr, no centre_distance on stdout. --mate-teeth 0 is
      now refused like every other out-of-range value (REQ-cli-parity, L08, R-2)."
    requirement: REQ-cli-parity
    verification:
      - kind: unit
        ref: "tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject"
        status: pass
      - kind: other
        ref: ".venv/bin/spur info --mate-teeth=-5 (exit 2, --mate-teeth message on stderr, no stdout)"
        status: pass
      - kind: other
        ref: ".venv/bin/spur info --mate-teeth 40 | grep -qE '\"centre_distance\": [0-9]' (numeric centre_distance still printed for a valid mate)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The CLI's copy of the bounds cannot silently drift from InfoQuery's --
      the test reads the bounds from InfoQuery's own JSON schema and checks one below
      the minimum, the minimum itself, the maximum itself, and one above the maximum."
    requirement: REQ-cli-parity
    verification:
      - kind: unit
        ref: "tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject"
        status: pass
    human_judgment: false
  - id: D3
    description: "pyproject.toml's [tool.mypy] sets disallow_any_explicit = true
      globally, with no per-module override anywhere, and [tool.pydantic-mypy]'s
      init_typed/init_forbid_extra remove the plugin's own generated-initialiser Any so
      no model class needs a suppression comment. make typecheck reports 'Success: no
      issues found in 23 source files'; make verify passes with the rule on."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: other
        ref: "make typecheck (Success: no issues found in 23 source files)"
        status: pass
      - kind: other
        ref: "grep -nE '^disallow_any_explicit = true' pyproject.toml"
        status: pass
      - kind: other
        ref: "! grep -nE 'disallow_any_explicit *= *false' pyproject.toml"
        status: pass
      - kind: other
        ref: "! git grep -nE 'type: *ignore\\[explicit-any' -- src tests docker bench"
        status: pass
    human_judgment: false
  - id: D4
    description: "L21 (supersedes L14) is appended to docs/architecture/decision_log.md,
      recording the rule on globally, the house rule, R-1's plugin-settings decision and
      its trade-off, DerivedDimensions' home, null-over-absent, uniform rounding's D-10
      correction, and derive()'s measured per-call cost. Every earlier entry, L14
      included, stays byte-identical -- the log as it stood at HEAD is an exact prefix
      of the working copy. docs/CODING_VALUES.md gains one bullet citing L21."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: other
        ref: "grep -nE '^## L21 .*supersedes L14' docs/architecture/decision_log.md"
        status: pass
      - kind: other
        ref: "exact-prefix diff of git show HEAD:docs/architecture/decision_log.md against the committed file (see Task 2's verify)"
        status: pass
      - kind: other
        ref: "grep -n 'L21' docs/CODING_VALUES.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "docs/tech_debt/active/2026-09-21-untyped-info-contract.md is
      Status: resolved, Resolved in: 013900d (a sha git cat-file -e resolves), git
      mv'd into docs/tech_debt/resolved/ (a rename, not a delete-and-recreate), and its
      row moved from Active to Resolved in docs/tech_debt/INDEX.md -- in the same commit
      that turned the rule on (D-16, CLAUDE.md, ROADMAP SC-4)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: other
        ref: "test -f docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md && test ! -f docs/tech_debt/active/2026-09-21-untyped-info-contract.md"
        status: pass
      - kind: other
        ref: "git show --stat cfe5f8d (rename docs/tech_debt/{active => resolved}/2026-09-21-untyped-info-contract.md)"
        status: pass
      - kind: other
        ref: "grep -n 'untyped-info-contract' docs/tech_debt/INDEX.md (only the Resolved-table hit)"
        status: pass
    human_judgment: false
  - id: D6
    description: "make verify passes at the end of every task, and after all three, with
      disallow_any_explicit on across everything mypy checks (L13, ROADMAP SC-2). Three
      commits, one per task, each with plain git commit (the gsd_run query commit
      wrapper's 30s timeout kills the ~42s pre-commit make verify)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: other
        ref: "make verify (104 passed, 5 import-linter contracts kept, ruff/mypy clean) -- run after each of the three task commits"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-24
status: complete
---

# Phase 4 Plan 3: `--mate-teeth` Range-Checked, `disallow_any_explicit` Retired Summary

`spur info --mate-teeth` now refuses exactly the mate tooth counts `/api/info`'s `InfoQuery`
refuses (closing the last REQ-cli-parity gap this phase found), and `disallow_any_explicit`
is on globally in `pyproject.toml` with zero suppressions anywhere — the pydantic-mypy
plugin's `init_typed`/`init_forbid_extra` settings remove its own generated-initialiser
`Any` on every model's class line, `L21` records why and supersedes `L14`, and the debt
file that asked for exactly this is resolved, moved, and reindexed in the same commit.

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-24T14:41:26Z
- **Completed:** 2026-09-24T14:50:37Z
- **Tasks:** 3 completed
- **Files modified:** 7 (0 created)

## Accomplishments
- `_mate_teeth(text: str) -> int`, an argparse `type=` in `cli.py`, replacing bare
  `type=int` on `--mate-teeth`. It converts to `int` and raises
  `argparse.ArgumentTypeError` on a non-integer or on a value outside `6..1000` (the
  bounds copied from `InfoQuery.mate_teeth`'s `ge=`/`le=`). argparse's own error path
  gives exit 2 and the stderr message (REQ-cli-parity, L08, R-2).
- `cmd_info`'s dead `or None` fallback (`--mate-teeth 0` used to mean "no mate") is
  gone; `ns.mate_teeth` — `None` or already range-checked — goes straight to `derive()`.
- `test_info_rejects_a_mate_the_api_would_reject` reads `InfoQuery`'s bounds from its
  own JSON schema and checks five rejected values (-5, 3, 0, `minimum - 1`,
  `maximum + 1`) and two accepted ones (`minimum`, `maximum`), so the CLI's copy of the
  range cannot drift from the API's without failing the gate.
- `pyproject.toml`'s `[tool.mypy]` sets `disallow_any_explicit = true` globally, with no
  per-module override anywhere; a new `[tool.pydantic-mypy]` table
  (`init_typed = true`, `init_forbid_extra = true`) removes the six class-line errors
  04-02 left (`GearParams`, `DerivedDimensions`, `InfoQuery`, `ModelQuery`, `PoolState`,
  `HealthReport`) with no suppression comment anywhere. `make typecheck` reports
  `Success: no issues found in 23 source files`.
- `L21` appended to `docs/architecture/decision_log.md`, superseding `L14`: the rule on
  globally, the house rule (`Any` is not written here; a genuinely untyped value is
  `object`; a library's own alias — `JsonSchemaValue`, `Message` — is not "ours"), the
  human's plugin-route decision (R-1) and its accepted trade-off, `DerivedDimensions`'
  home and single construction site, null-over-absent for both published responses,
  the D-10 rounding correction (no value moved — the fillet helpers already rounded),
  and `derive()`'s measured per-call cost (9.19 → 11.5 usec). Every earlier entry,
  `L14` included, is byte-identical — verified by an exact-prefix diff against HEAD.
- `docs/CODING_VALUES.md` gains one bullet next to "Explicit types at every boundary",
  citing `L21`.
- `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` is `Status: resolved`,
  `Resolved in: 013900d` (Plan 04-01 Task 1's commit, which gave the report its shape),
  `git mv`'d into `docs/tech_debt/resolved/`, with a closing resolution paragraph naming
  what now exists and the three tests that hold it. `docs/tech_debt/INDEX.md`'s row
  moved from Active to Resolved — all in the same commit that turned the rule on.

## Task Commits

Each task was committed atomically, all with plain `git commit` (not the
`gsd_run query commit` wrapper, whose 30 s timeout kills the repository's ~42 s
pre-commit `make verify`):

1. **Task 1: `spur info` refuses a mate the API refuses (REQ-cli-parity, L08; R-2)** —
   `ce5195e` (fix)
2. **Task 2: `L21` appended, citing the human's plugin-route decision, and the house
   rule written where coders read it** — `059a7e4` (docs)
3. **Task 3: The rule on, and the debt retired in the same commit (D-04, D-15, D-16;
   R-1)** — `cfe5f8d` (feat)

**Plan metadata:** committed alongside this file (see below).

## Files Created/Modified
- `src/spur/cli.py` — `_mate_teeth()` and its two bounds constants; `--mate-teeth` uses
  `type=_mate_teeth`; `cmd_info`'s `or None` fallback removed
- `tests/test_cli.py` — `test_info_rejects_a_mate_the_api_would_reject` added; imports
  `InfoQuery` from `spur.app` (the import-linter contract constrains `spur.cli`, not
  the tests)
- `docs/architecture/decision_log.md` — `L21` appended (supersedes `L14`); every
  earlier line unchanged
- `docs/CODING_VALUES.md` — one bullet citing `L21`
- `pyproject.toml` — `[tool.mypy]` gains `disallow_any_explicit = true` and a rewritten
  comment; new `[tool.pydantic-mypy]` table
- `docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md` — `git mv`'d from
  `active/`; `Status: resolved`, `Resolved in: 013900d`, closing resolution paragraph
- `docs/tech_debt/INDEX.md` — row moved from Active to Resolved

## Decisions Made

See `key-decisions` in the frontmatter. The two from the human (R-1, R-2) were made on
2026-09-24, before this plan executed, and are recorded here as followed, not chosen.

## TDD Gate Compliance

Task 1 carried `tdd="true"`. RED was run and its output inspected directly (this
repository's established convention since Phase 3 — `gsd_run check tdd-red-evidence`'s
TAP parser does not read pytest output, per `03-02-SUMMARY.md`'s Issues Encountered), not
committed separately: the pre-commit hook runs the full `make verify` with no bypass, so
a RED commit whose test fails would be rejected by the hook itself (`tdd.md`'s project
note). RED and GREEN landed together in `ce5195e`.

**RED, before the fix** (`.venv/bin/python -m pytest
tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject -v`):

```
>           with pytest.raises(SystemExit) as exc:
                 ^^^^^^^^^^^^^^^^^^^^^^^^^
E           Failed: DID NOT RAISE SystemExit
----------------------------- Captured stdout call -----------------------------
{
  ...
  "mate_teeth": -5,
  "centre_distance": 12.25
}
FAILED tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject - Failed: DID NOT RAISE SystemExit
```

The named test itself failed, on the planned assertion (`--mate-teeth=-5` should have
raised `SystemExit`, and instead printed a numeric `centre_distance`) — an intentional
RED, not a collection error, syntax error, or unrelated failure (#3770).

**GREEN, after the fix:** all 6 tests in `tests/test_cli.py` pass, including the new one.

No REFACTOR commit: no cleanup was needed after GREEN.

## Deviations from Plan

None - plan executed exactly as written. `.venv/bin/mypy --disallow-any-explicit src
tests docker bench` was re-run before starting (per this plan's dispatch instruction) and
confirmed the expected six class-line errors before Task 2/3 began.

## Issues Encountered

**`requirements mark-complete`'s `write_set` reported `applied: false` for
`REQ-cli-parity`'s checkbox and traceability surfaces.** Not a bug: `REQUIREMENTS.md`
already carried `REQ-cli-parity` as `[x]` / "Complete (shipped v0)" from Phase 1, before
this phase started (the requirement's CLI-parity acceptance was already satisfied by
`tests/test_cli.py`'s pre-existing tests; this plan closed the one gap — the
`--mate-teeth` range — that would have made a *future* regression false, not the
requirement's already-recorded acceptance). `requirements.ready-ids` correctly listed it
as ready (2/2), and the file's checkbox/traceability row read `[x]` / "Complete" both
before and after the call — the outcome (`REQ-cli-parity` complete) matches what the gate
reported ready, `mark-complete` just had nothing to change on that requirement's two
surfaces. `REQ-typed-derived-dimensions` (new to Phase 4) was written for real: `applied:
true` on both surfaces.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 4 is complete. `REQ-typed-derived-dimensions` and `REQ-cli-parity` are both marked
complete in `.planning/REQUIREMENTS.md`. `make verify` passes with `disallow_any_explicit`
on across `src tests docker bench`, with no per-module exception and no suppression
comment anywhere — `L14`'s ratchet is retired, not re-deferred (`PROJECT.md` success
metric 2). No blockers.

One tangent noted, not fixed (out of this plan's file scope):
`docs/architecture/gear-maths/tests.md:28` still cites "L14 note" for the missing
coverage floor — `L14` is now superseded by `L21`, and never mentioned coverage in the
first place, so the pointer was already stale before this phase touched anything.

Phase complete, ready for verification.

---
*Phase: 04-typed-derived-dimensions-contract*
*Completed: 2026-09-24*
