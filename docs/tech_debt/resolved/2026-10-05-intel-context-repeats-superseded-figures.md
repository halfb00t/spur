# `.planning/intel/` still repeats two figures the live docs have since corrected

Severity: must
Status: resolved
Date: 2026-10-05
Resolved in: docs(intel): correct the Python floor and gate duration; index L17–L35
Source: PR #21 (translating `docs/HOW_TO_DEVELOP.md`); the drift was noticed while fixing
the same file's "guide is in Russian" bullet
Related files:
- .planning/intel/context.md:21-22 ("Python 3.10+ locally, but `cadquery-ocp` wheels only
  exist for 3.10–3.12")
- .planning/intel/context.md:40 ("`make verify` ... ~11s warm")
- .planning/intel/constraints.md:90 ("~11s warm"; "CI (Python 3.10 and 3.12)")
- .planning/intel/decisions.md:17 (L01 as recorded: "Python 3.10–3.12"; the file has no
  L23 entry)
- .planning/intel/decisions.md:89 ("~11s warm")
- docs/architecture/decision_log.md:553 (L23 — Python 3.12 only, supersedes L01's floor)
- docs/HOW_TO_DEVELOP.md §0 (the ~64 s figure, `bench/RESULTS.md`, Phase 15)

## Context
`context.md` is the gsd ingest synthesis — "running notes from the 6 documents classified
DOC", written once when the docs were ingested and not re-synthesised since. Two of its
claims were true then and are false now:

- The Python floor. L23 locked "3.12 only" (the `cadquery-ocp` wheels argument that L23
  records); `README.md` and `AGENTS.md` say 3.12. `context.md` still describes a 3.10+
  install with wheels for 3.10–3.12.
- The gate's duration. Phase 15 re-measured `make verify` at ~64 s on a warm cache
  (12-core dev host) and wrote that into `docs/HOW_TO_DEVELOP.md`; two runs on 2026-10-05
  read 65.11 s and 67.98 s. `context.md` still says ~11 s — six times short.

PR #21 corrected a third stale sentence in the same file (the workflow bullet still named
`make worktree.land` as the merge path, superseded by `make pr.land` in Phase 5) only
because it stood in the way of the translation.

The sibling intel files were grepped for the same two claims when this was filed.
`constraints.md:90` and `decisions.md:89` repeat "~11s warm"; `constraints.md:90` also
has CI running on "Python 3.10 and 3.12"; `decisions.md:17` records L01's 3.10–3.12
range and the file contains no L23 entry — the intel's decision list predates the
decision that supersedes one it records. `requirements.md` and `SYNTHESIS.md` carry
neither claim. Whether `decisions.md` also lacks other post-ingest decisions (L24
onward) was not checked.

## Why it matters
`.planning/intel/` is what gsd planners and researchers load as trusted background. A
planner that believes the gate takes 11 s accepts timeouts a 65 s run will blow — the
already-filed `2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` is that failure
mode. A researcher that believes the project runs on 3.10 can propose compatibility
shims or a 3.10 test matrix that contradict a locked decision. Both are plausible-looking
numbers nobody will re-measure before planning on them.

## Next step
Correct the five lines by hand — "Python 3.12 only (L23)" and "~64 s warm
(`bench/RESULTS.md`, Phase 15)" — and, in the same change, diff the `Lxx` ids
`decisions.md` records against `docs/architecture/decision_log.md` and add what is
missing, L23 at minimum. Alternatively re-run the ingest synthesis and diff it against
the current files, if a broader refresh is wanted. Revisit no later than the start of the
next milestone's planning, or the first time a PLAN/RESEARCH document cites a file under
`.planning/intel/`.

## Resolution (2026-10-05)

By hand, no re-synthesis — the files are small and a diff is easier to check than a new
ingest:

- The five lines named above now read "Python 3.12 only (L23)" and "~64 s warm on the
  12-core dev host (`bench/RESULTS.md`, Phase 15)", each with "this entry read X at
  ingest" where the old figure sat in a decision entry, so a reader sees the correction
  rather than a silently different number.
- One more stale line found on the way, `constraints.md:105`: `derive(p) -> dict[str,
  Any]` plus a separate `with_mate(info, p, z2)`. The live signature is
  `derive(p, mate_teeth=None, mate_shift=0.0) -> DerivedDimensions` (L21, `src/spur/calc.py`);
  its source doc `docs/architecture/gear-maths/tactics.md` was already right, only the
  intel copy lagged.
- `decisions.md` listed L01–L16 as `locked` with no supersession marks. L06, L07 and L14
  now read `superseded by` (L18, L17, L21); L01's Python floor, L09, L10, L12 and L13
  carry `amended by` (L23, L33, L33, L34, L34). A new section indexes L17–L35 by heading
  with what each supersedes or amends — headings only, copied from the log, so the index
  cannot drift on a figure; a planner that needs a number reads the log entry. The log
  stays the single source (AGENTS.md).
- `SYNTHESIS.md` and `ingest-manifest.yaml` are left as the dated record of the
  2026-09-21 ingest they describe.
