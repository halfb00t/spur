---
phase: 19-the-trochoid-in-the-part
plan: 11
subsystem: docs
tags: [readme, ideas, roadmap, phase-20-skip, trochoid, root_shape, L38, slug]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-06's root_form_d / root_waist / undercut sentence, 19-07's README rows, 19-09's bench/RESULTS.md figures, 19-10's L38 (cited by id only)
provides:
  - "README Geometry notes true for both root modes: root_shape, root_form_d as the cutter-envelope junction, root_waist and its 0.4 mm floor, no root-circle thickness, the undercut sentence, the lead-in chord as the radial root's, the trochoid's third chamfer bound"
  - "docs/ideas/2026-09-21-trochoidal-root-fillets.md brought true: the opt-in shipped (L38), the default flip waits on D-09's trigger; its INDEX row says so"
  - "docs/ideas/2026-10-08-download-name-carries-the-root-shape.md and its INDEX row"
  - "Phase 20 recorded Skipped (O4, flip deferred) in ROADMAP's Progress row and criteria, STATE's Roadmap Evolution, and REQUIREMENTS' trochoid follow-ups, which now own the flip with D-09's trigger"
affects: [next-milestone-planning, 20]

# Actuals (#2632): chars/4 over the added lines of the seven changed files, 2e3a352..9594f09.
actuals:
  tokens: 1581
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "a README claim about a number cites the bench/RESULTS.md subsection it comes from; a number from elsewhere is left out"
    - "a skipped phase keeps its number and its row; the skip is recorded by scoped edits in the three files that own the flip"

key-files:
  created:
    - docs/ideas/2026-10-08-download-name-carries-the-root-shape.md
  modified:
    - README.md
    - docs/ideas/2026-09-21-trochoidal-root-fillets.md
    - docs/ideas/INDEX.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "README says root_form_d is 'a different quantity from the ISO 21771 one, and not to be read as it', never the phrase 'form diameter': the existing test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it fails any README that holds both root_form_d and that phrase"
  - "The README gives no number that is not in bench/RESULTS.md: the 0.4 mm waist floor and the 14 chamfer rows are cited to their subsections; FEATURES' 4.68 to 3.51 mm thickness figures are left out"

requirements-completed: [REQ-root-mode-decided, REQ-trochoid-composes-and-is-priced, REQ-undercut-warning-restated]

coverage:
  - id: D1
    description: "README's Geometry notes describe both root shapes, root_form_d as the cutter-envelope junction (never a form diameter), root_waist and its floor, the null root thickness, the undercut sentence, the radial-only lead-in chord and the trochoid's junction bound on the tip chamfer; every command in the README still runs"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: other
        ref: "the plan's geometry-notes check (prints 'README and ideas brought true')"
        status: pass
      - kind: unit
        ref: "tests/test_cli.py#test_readme_export_examples_run"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it"
        status: pass
    human_judgment: true
    rationale: "Whether the prose is true and reads well against the code is a reviewer's judgment; the checks prove the named terms are present, the ISO wording is absent and the README commands run."
  - id: D2
    description: "The trochoid idea cites L38 and D-09's trigger with its INDEX row updated; the slug idea is filed with its INDEX row in the same commit"
    verification:
      - kind: other
        ref: "the plan's ideas check (same 'README and ideas brought true' line)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Phase 20 is recorded skipped without orphaning the flip: ROADMAP's Progress row reads Skipped (O4, flip deferred), its criteria say not applicable under L38, STATE has the dated line, REQUIREMENTS names L38 and D-09's trigger"
    requirement: REQ-root-mode-decided
    verification:
      - kind: other
        ref: "the plan's skip check (prints 'Phase 20 skip recorded')"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate after the edits: make verify exit 0, 1210 passed in 221.30s, coverage 97.90 %"
    verification:
      - kind: other
        ref: "make verify"
        status: pass
    human_judgment: false

duration: "8 min"
completed: 2026-10-09
status: complete
plan_head_before: 2e3a35209bafc6800fc138e8616dd7a3d7d578e7
plan_head_after: 9594f092c5860007fb3063ac36a9b8fb6dcd5222
commits: 2
---

# Phase 19 Plan 11: README, the trochoid idea and Phase 20's skip made true Summary

**README's geometry notes now say what the two root shapes are, where the hob root applies and what `/api/info` prints under it (`root_form_d` as the cutter-envelope junction, `root_waist` under a 0.4 mm floor, no root-circle thickness); the trochoid idea records the shipped opt-in and D-09's trigger for the default flip; a slug idea is filed; and Phase 20 is recorded `Skipped (O4, flip deferred)` under L38 in ROADMAP, STATE and REQUIREMENTS.**

## Performance

- **Duration:** about 8 min (first reads about 07:52Z, last commit before this SUMMARY at about 07:57Z, then the one `make verify` of 3 min 42 s)
- **Started:** 2026-10-09T07:54:58Z (guard and ledger; reads preceded it)
- **Completed:** 2026-10-09T08:01:13Z (clock read before the SUMMARY write)
- **Tasks:** 2
- **Files modified:** 7 (6 modified, 1 created)

## Accomplishments

- **README Geometry notes (SC5).** The "Below the base circle the flank is radial" bullet becomes the two-mode bullet: `radial` by default as in most generators; `trochoid` the curve a hob with tip radius `root_fillet` sweeps, applied only where the base circle lies above the root circle, ignored and warned elsewhere. Under it `/api/info` prints `root_form_d` (the cutter-envelope junction, "a different quantity from the ISO 21771 one, and not to be read as it") and `root_waist` (warned below 0.4 mm, cited to `bench/RESULTS.md` "Waist floor"), prints no root-circle thickness or gap (ill-conditioned there, so a warning and no number, L08), and states the undercut onset and the avoiding shift. The default is stated unmoved (L38). The root-fillet bullet now opens "With the radial root" and ends by saying the lead-in chord and its warning are the radial root's. The tip-chamfer bullet gains the trochoid's third bound, the junction of the hob root with the involute flank, measured on 14 gear rows none of which built above it (`bench/RESULTS.md` "Chamfer across the junction", L38).
- **The trochoid idea.** Context records the shipped opt-in and that the default did not move; Next step names the flip's trigger (a real fit report or a mating-pair request below `z_min`, D-09, not a date), its shape (one commit, own `Lxx`, regen rules, L26 D-03) and its owner (REQUIREMENTS "Trochoid follow-ups"; Phase 20 skipped for it). Its INDEX row now says the opt-in shipped and the flip waits on that trigger.
- **The slug idea.** `docs/ideas/2026-10-08-download-name-carries-the-root-shape.md` from TEMPLATE (Source: 19-RESEARCH Open Question 6): `GearParams.slug()` names teeth, module and pressure angle, so a radial and a trochoid download of one gear share a name; revisit when a user reports mixing them up or when the flip is planned, under its own `Lxx` because the slug is also written into records. INDEX row dated 2026-10-08, in the same commit.
- **Phase 20 skipped, by scoped `Edit`s.** ROADMAP Progress row `| 20. The Flip (conditional) | v0.4 | 0/0 | Skipped (O4, flip deferred) | - |` and "Not applicable: skipped under L38 (O4, flip deferred), the trigger D-09 names." under the Phase 20 Success Criteria heading; STATE "Roadmap Evolution" has `Phase 20 skipped (O4, flip deferred) under L38, 2026-10-09: ...`; REQUIREMENTS' flip bullet says O4 was taken, names L38 and D-09's trigger, and says the bullet owns the flip from here.
- **Gate.** `make verify` exit 0, **`1210 passed in 221.30s (0:03:41)`**, coverage 97.90 % (floor 96), ruff, mypy `--strict`, import contracts and the unfinished-work scan green, 0 `ReentrantCallError` in the log. Host load at the start 5.27, 6.29, 6.22. That is 221 s against 19-10's 166 s and 19-09's mean 193 s on the same host: the accepted cost (`accept-A`, L38), host-load dependent, not a fault.

## Task Commits

1. **Task 1: README and the trochoid idea brought true, slug idea filed** - `1807d1e` (docs)
2. **Task 2: Phase 20 recorded skipped under L38, flip deferred** - `9594f09` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md, REQUIREMENTS.md and `.planning/state.json`.

`commits: 2` is measured from the ledger: `git rev-list --count 2e3a352..HEAD` read 2 at SUMMARY write.

## Files Created/Modified

- `README.md` - Geometry notes: both root shapes, `root_form_d`/`root_waist`, the radial-only lead-in chord, the trochoid chamfer bound
- `docs/ideas/2026-09-21-trochoidal-root-fillets.md` - Context and Next step brought true (opt-in shipped, flip trigger D-09)
- `docs/ideas/2026-10-08-download-name-carries-the-root-shape.md` - the slug idea (new)
- `docs/ideas/INDEX.md` - the trochoid row reworded, the slug row added
- `.planning/ROADMAP.md` - Phase 20 Progress row and not-applicable criteria line
- `.planning/STATE.md` - the dated Roadmap Evolution line
- `.planning/REQUIREMENTS.md` - the trochoid follow-ups' flip bullet names L38 and D-09

## Decisions Made

See `key-decisions`. L38 was cited by id only; no text was taken from it and the decision log was not touched (`git diff 2e3a352 HEAD` on it is empty, as on `tests/regression/pre_v0_2.json`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The first README draft broke an existing test**
- **Found during:** Task 1 (running the plan's verify)
- **Issue:** The draft called `root_form_d` "not a form diameter in ISO 21771's sense". `tests/test_api.py::test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it` fails any README containing both `root_form_d` and the phrase "form diameter", even in a denial (D-04, 19-06).
- **Fix:** Reworded to "a different quantity from the ISO 21771 one, and not to be read as it"; D-04's meaning kept, the phrase gone. The test and the plan's `cutter-envelope junction` assertion both pass. Caught before the commit.
- **Files modified:** `README.md`
- **Verification:** `tests/test_api.py` and `tests/test_cli.py` `-k 'form_d or readme'`: 2 passed
- **Committed in:** `1807d1e`

**2. A figure the plan implied was left out.** The D-03 thickness figures (4.68 mm falling to 3.51 mm) live in FEATURES, not in `bench/RESULTS.md`, and the plan says numbers in README only from `bench/RESULTS.md`; the README states the ill-conditioning in words and quotes no figure for it.

---

**Total deviations:** 1 auto-fixed (Rule 1), 1 plan-literal item. **Impact on plan:** none on scope.

## Issues Encountered

- **Commit attribution line.** Commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives. The dispatch text named `Claude Fable 5.1`; `CLAUDE.md` names neither, so the reminder was followed, as 19-05 to 19-10 did.
- **Verify ordering.** The plan lists `make verify` under Task 2's verify; it was run once, after both task commits (the dispatch asked for it at the end), and covers both. The two commit hooks ran `make verify.fast` (Passed).
- **L34's bar.** The gate reads 221 s on this host at a load of about 5 to 6, against L34's 66 s bar set on a 12-CPU M2 Max; L38 records the human's acceptance (`accept-A`) and names re-setting the bar as a separate decision. Not touched here.

## Known Stubs

None. No placeholder, skipped test or unrun `<verify>` was left behind; nothing was appended to `.planning/WINDOWS.md`.

## Threat Flags

None. A record only: no network, auth, file-access or trust-boundary surface. T-19-21 is mitigated: the only numbers in the README are cited to `bench/RESULTS.md` subsections, `root_form_d` is never called a form diameter (the existing test passes), the README's commands still run, and Phase 20's skip is recorded by scoped edits with REQUIREMENTS naming L38 and D-09's trigger as the flip's owner.

## User Setup Required

None - no external service configuration required.

## Debt and Ideas Filed

One idea filed: `docs/ideas/2026-10-08-download-name-carries-the-root-shape.md` (INDEX row added in the same commit). No debt item filed. The candidate 19-10 raised for the human (L34's 66 s bar against a gate near 190 to 220 s on this host) is still the human's call and was not filed.

## Next Phase Readiness

- Phase 19 has all 11 SUMMARYs; the phase is ready for verification (`/gsd-verify-work`) and the PR (`make pr.land`, `/gsd-ship`).
- Phase 20 is skipped, not deleted; the flip is owned by REQUIREMENTS "Trochoid follow-ups" with D-09's trigger.

## Self-Check: PASSED

- FOUND: `README.md`, the slug idea, the trochoid idea, `docs/ideas/INDEX.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/REQUIREMENTS.md`.
- FOUND: commits `1807d1e` and `9594f09` are ancestors of HEAD; `git rev-list --count 2e3a352..HEAD` read 2 before this SUMMARY.
- The plan's three automated checks printed `README and ideas brought true`, `Phase 20 skip recorded` and a passing `test_readme_export_examples_run`; `docs/architecture/decision_log.md` and `tests/regression/pre_v0_2.json` are byte-identical to the phase's start of this plan; `make verify` exit 0, `1210 passed`.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
