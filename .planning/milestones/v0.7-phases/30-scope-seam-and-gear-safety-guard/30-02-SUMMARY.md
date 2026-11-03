---
phase: 30-scope-seam-and-gear-safety-guard
plan: 02
subsystem: docs
tags: [decision-log, scope, roadmap, agents-brief]

requires:
  - phase: 30-scope-seam-and-gear-safety-guard
    provides: "30-01: make gear.unchanged, named in the roadmap text and L46 as the proof of the gear's link contract"
provides:
  - "L46: the product is a gear and spline generator; amends L02 and L05 by reference; the last entry of the decision log"
  - "AGENTS.md 'What we're building' names the gear and spline generator and the shaft in progress; README.md untouched"
  - "ROADMAP Phase 30 Depends on states the v0.6 tag exists and D-11's rule; Phase 32 and 33 name their additive edits"
affects: [30-03, 30-05, 31, 32, 33]

plan_head_before: 14b5f7717c2bcfe2ea30c3f85a98d2f75c4c0d4e
plan_head_after: 5d61f8e3d82c2751164dfa22cf5e3381b35415b1

actuals:
  tokens: 2244   # chars/4 over `git diff 14b5f77 HEAD` (8974 chars), before this SUMMARY
  tasks: 2
  commits: 1     # MEASURED: git rev-list --count 14b5f7717c2bcfe2ea30c3f85a98d2f75c4c0d4e..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "scope change logged as an append-only amendment entry that quotes the new wording of the old entries, which stay as written"

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - AGENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "L46 (2026-10-23): spur is a gear and spline generator; amends L02 to one parameter model per part type, three front ends each, and L05 with a second frozen link contract: the shaft's field names and defaults; keeps L03, L04, L06, L08 and L44"
  - "The shaft's field names and defaults may change by logged decision until Phase 33 publishes the first shaft link; L05 applies in full from then (D-18)"
  - "A stray part= token on a gear link becomes refused when Phase 33 adds the part switch, an L44-class invalid-link change; grep counts read 0 in golden_requests.json, pre_v0_2.json and README.md"

patterns-established:
  - "The decision-log commit carries the brief and roadmap text with it, and no file under src/, so 30-03 and 30-05 can order-check it against the first commit that adds a shaft module"

requirements-completed: [REQ-scope-decision-logged]

coverage:
  - id: D1
    description: "L46 is the last '## L' heading of the decision log, ends '(amends L02 and L05; keeps L03, L04, L06, L08 and L44)', and quotes the new L02 and L05 wording on single lines; no earlier line changed (41 added, 0 deleted)"
    requirement: REQ-scope-decision-logged
    verification:
      - kind: other
        ref: "grep '^## L' docs/architecture/decision_log.md | tail -1 | grep -c '^## L46 — .*(amends L02 and L05; keeps L03, L04, L06, L08 and L44)$' (1); git diff --numstat 14b5f77 5d61f8e -- docs/architecture/decision_log.md (41 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "AGENTS.md names a gear and spline generator (4 lines, 3 deleted); README.md and the gear-side watched paths are byte-identical to v0.6"
    requirement: REQ-scope-decision-logged
    verification:
      - kind: other
        ref: "git diff --exit-code v0.6 -- README.md tests/regression/ .github/workflows/ci.yml requirements.txt (exit 0); grep -c 'gear and spline generator' AGENTS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "ROADMAP Phase 30 Depends on states the tag exists and D-11's rule without the stale tag-absent text; Phase 32 and 33 carry the additive-edit sentences (ignore_imports once, _serve_model)"
    requirement: REQ-scope-decision-logged
    verification:
      - kind: other
        ref: "sed -n '/^### Phase 30:/,/^\\*\\*Requirements\\*\\*/p' .planning/ROADMAP.md | grep -c 'make gear.unchanged' (1), 'peel' (1), 'git tag -l' (0); Phase 32 'ignore_imports' (1); Phase 33 '_serve_model' (1)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The L46 commit lists decision_log.md, AGENTS.md and ROADMAP.md and no path under src/, and no shaft module exists yet (the 'precedes' half is checked by 30-03 and 30-05)"
    requirement: REQ-scope-decision-logged
    verification:
      - kind: other
        ref: "git show --stat --format= 5d61f8e (3 files); ls src/spur/shaft_params.py src/spur/parts.py (absent)"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-10-23
status: complete
---

# Phase 30 Plan 02: Scope decision Summary

**L46 logs spur as a gear and spline generator (amends L02 and L05 by reference, old entries untouched), with the AGENTS.md brief and the roadmap's stale Phase 30 text fixed in one docs commit before any shaft module**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-23T16:05:42Z
- **Completed:** 2026-10-23T16:12Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- `L46` is appended after L45's amendment: the decision (D-16), the L02 and L05 amendments with D-17's exact wording, what it leaves alone, when the shaft's contract freezes (D-18), the one gear-link behaviour that will change (a stray `part=` token), the frozen layout, walls and `/api/shaft/` prefix (D-12 to D-15), the proof and the reversibility. 41 lines added, 0 deleted.
- The `part=` evidence was run, not quoted from the plan: `grep -c '"part'` reads 0 for `tests/regression/golden_requests.json` and 0 for `tests/regression/pre_v0_2.json`, and `grep -c 'part=' README.md` reads 0.
- `AGENTS.md` "What we're building" now reads "A parametric gear and spline generator (L46): the involute spur gear is shipped, a DIN 5480 splined shaft is in progress (v0.7)" and ends "one parameter model per part type". 4 lines added, 3 deleted. README.md is untouched (D-19).
- ROADMAP Phase 30 "Depends on" now says the `v0.6` tag exists, annotated and pushed, peeling to `792b45c`, and states D-11's rule. Read-only checks this session: `git cat-file -t v0.6` prints `tag`, `git ls-remote --tags origin 'v0.6*'` lists `v0.6` and `v0.6^{}` at `792b45c`. Phase 32 and 33 "Depends on" carry their additive-edit sentences, including the `ignore_imports` handoff.

## Task Commits

1. **Tasks 1 and 2: L46, the AGENTS.md brief and the roadmap text** - `5d61f8e` (docs). One commit, as the plan directs (D-20); the stat lists `.planning/ROADMAP.md`, `AGENTS.md`, `docs/architecture/decision_log.md` and no path under `src/`.

**Plan metadata:** the `docs(30-02)` commit that adds this file, STATE.md, ROADMAP.md and REQUIREMENTS.md.

**The L46 commit sha for 30-03 and 30-05 is `5d61f8e3d82c2751164dfa22cf5e3381b35415b1`.**

## Files Created/Modified

- `docs/architecture/decision_log.md` - L46 appended
- `AGENTS.md` - first paragraph of "What we're building" (CLAUDE.md is a symlink to it)
- `.planning/ROADMAP.md` - Phase 30, 32 and 33 "Depends on" paragraphs (13 added, 8 deleted)

## Decisions Made

- L46 itself is the decision, taken by the human at Phase 30's discuss-phase; this plan only wrote it down. See `key-decisions` above.
- The plan's ROADMAP line numbers (189-195, 292, 327) had shifted; the edits were located by text, not by line number.

## Deviations from Plan

**1. [Instruction conflict] Commit trailer**
- The dispatch asked for `Co-Authored-By: Claude Opus 5.5`; the session's attribution reminder, which governs commits, names `Claude Sonnet 5.5`, the model that made this commit. The commit carries the Sonnet line, as 30-01's did.

**Total deviations:** 0 auto-fixed, 1 instruction conflict. **Impact:** none on the content.

## Issues Encountered

- The pre-commit hook ran `make verify.fast` (with `gear.unchanged`) on the docs commit and passed.
- Tangent, not fixed (surgical): `AGENTS.md` "Full intent" still says `.planning/PROJECT.md` is "not written yet", but the file exists (102954 bytes). It is a wording fix for a later docs commit.
- `.planning/STATE.md` still lists the blocker "No `v0.6` tag exists" under Blockers/Concerns. It is false now (the tag exists locally and on `origin`); the state handler is to clear it.

## Known Stubs

None.

## Threat Flags

None. Docs only; no endpoint, auth path or schema change.

## User Setup Required

None - no external service configuration required.

## Verification

- `make verify`: 1362 passed in 188.85s (0:03:08), run after the commit (last line of the output; the docs commit's hook had already run `make verify.fast`).
- `git diff --exit-code v0.6 -- README.md tests/regression/ .github/workflows/ci.yml requirements.txt` empty.
- Plan acceptance for both tasks re-run after the commit: L46 is the last `^## L` heading; `git diff --numstat 5d61f8e^ 5d61f8e -- docs/architecture/decision_log.md` reads `41 0`, `AGENTS.md` reads `4 3`.
- No debt or idea item was filed.

## Next Phase Readiness

30-03 can add the five shaft placeholders and `parts.py`: no shaft module exists (`ls src/spur/shaft_params.py src/spur/parts.py` prints nothing), and L46 is committed first, so the D-20 order holds. 30-03 and 30-05 use `5d61f8e` as the L46 commit. The Phase 32 `ignore_imports` handoff is written in the roadmap.

## Self-Check: PASSED

Files found: `docs/architecture/decision_log.md`, `AGENTS.md`, `.planning/ROADMAP.md`. Commit `5d61f8e` found in HEAD.

---
*Phase: 30-scope-seam-and-gear-safety-guard*
*Completed: 2026-10-23*
