# Phase 6: Address tech debt: merge gate + solid cache - Context

**Gathered:** 2026-09-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the open `must` debt in the two areas the roadmap names, and the two `nice` items
that live in the same files:

1. **Merge gate** (`scripts/skip_tokens.py`, `scripts/pr_land.py`, `tests/test_pr_land.py`,
   `docs/HOW_TO_DEVELOP.md` §6/§8):
   - the `commit-msg` hook trusts a cut line typed by hand inside an editor session
     (`docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`, must);
   - `make pr.land` judges a run by the listed jobs only, never by the run's own
     conclusion (`…pr-land-admits-a-run-with-a-failing-unlisted-job.md`, must);
   - the required-jobs drift test reads job ids, so a `jobs.<id>.name` override slips
     past it (`…required-jobs-drift-test-ignores-job-name-overrides.md`, nice);
   - `pr.land` reports "a skip token reached main" for any run it failed to observe, and
     its docstring/§8 over-claim what `--match-head-commit` proves
     (`…pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md`, nice).
2. **Solid cache** (`src/spur/model.py`, `tests/conftest.py`, `tests/test_model.py`):
   `_build_cached` hands out one mutable `cq.Solid`; `exportStl()` attaches a mesh to it and
   a later `.BoundingBox()` reads the mesh (zlen 7.5877 / 7.5196 vs the exact 7.5000 mm),
   masked today only by the autouse `_reset_solid_cache` fixture
   (`…shared-solid-cache-corrupts-later-boundingbox.md`, must).

Done means: each of the five debt files is `Status: resolved` with its sha, `git mv`'d
into `docs/tech_debt/resolved/` with its INDEX row moved, in the commit that fixes it
(CLAUDE.md); every behaviour change ships with its test; `make verify` green; numbers
measured, not estimated.

**Not in scope:** the concurrent-latency waiver (a measurement investigation with its own
trigger, `2026-09-23-concurrent-latency-bar-waived.md`); the coverage floor; the five v0
`nice` items; any new CI job; any change to what `make verify` checks; new features.

</domain>

<decisions>
## Implementation Decisions

### Scope
- **D-01:** Phase 6 closes exactly the five items above — three `must`, two `nice` —
  and nothing else. Each debt file is resolved in the commit that fixes it, never in a
  follow-up.

### Commit-msg hook (retires `2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`)
- **D-02:** **Drop the cut entirely.** `main()` hands the whole buffer git gives it to
  `find_skip_tokens`; the scissors pattern, the editor-only branch keyed on `GIT_EDITOR`,
  and their tests go away. A new test proves a token *below* a git-shaped cut line is
  refused regardless of `GIT_EDITOR`. Accepted cost: a `git commit -v` whose appended
  staged diff quotes a token (this repository's own tests and docs do) is refused — the
  author commits without `-v` or rewords. `git config --get commit.verbose` reads empty
  here (2026-09-25); nobody is opted in. Rejected: a config-driven cut (`-v` on the
  command line stays invisible, so it over-matches anyway and keeps the heuristic);
  accepting the residual (leaves a `must` open by design). — **Reversibility:**
  reversible — the cut is ~20 lines and its tests are in history (`3e68e74`).
- **D-03:** The `-v` caveat lives in two places: the hook's refusal names the matched
  token and line and adds one sentence — if this came from `-v`'s appended diff, commit
  without `-v` — and `docs/HOW_TO_DEVELOP.md` §6 gets the same one line, in Russian like
  the rest of the file. The 05-06 editor-session explanation in §6/§8 is corrected in the
  same change.

### `pr.land`'s run verdict (retires `…admits-a-run-with-a-failing-unlisted-job.md` and `…drift-test-ignores-job-name-overrides.md`)
- **D-04:** `head_refusals` refuses when the newest completed run's **`conclusion` is not
  `"success"`** — naming the conclusion and the run URL — *in addition to* the per-job
  check, which stays because it is what names a *missing* job. The required list stays the
  local `.github/workflows/required-jobs.txt`; the stale-checkout half is closed by rule,
  not by a fetch: §8 says `make pr.land` is run from an up-to-date `main` checkout (which
  its own local follow-up leaves you on). Rejected: reading `required-jobs.txt` at the PR
  head sha (a network read in front of the pure core, for a case the run-conclusion check
  already refuses). — **Reversibility:** reversible.
- **D-05:** The drift test **resolves the effective job name**: `jobs.<id>.name` when
  present, else the id, with the matrix expansion unchanged; the parse is scoped to the
  job block so step-level `name:` keys (`ci.yml` lines 44, 58 today) are untouched. One
  regression case renames `image` in an in-memory `ci.yml` and expects the derived set to
  follow. Rejected: asserting no job-level `name:` exists (a grep, and it would surprise
  the first legitimate rename).

### `pr.land`'s post-merge report (retires `…blames-a-skip-token-for-any-missed-post-merge-run.md`)
- **D-06:** Step 5 **reports what it observed**. The poll keeps its last error; the exit
  is non-zero in every case, and the message is one of three: reads failed
  (`no ci.yml run observed within N s; last error: …`); reads succeeded and nothing
  appeared (`no ci.yml run observed within N s` plus the Actions URL to check); or — only
  after fetching the squash commit's message through `gh api` and running
  `find_skip_tokens` on it — the token, named. One `FakeRunner` case per branch. Rejected:
  never diagnosing (loses the one cause the tool can actually establish).
- **D-07:** The module docstring and §8 **state the split**: `pr.land` proves the
  run-appeared half (step 5) and refuses a head it *saw* behind `main`; the window between
  that read and `gh pr merge` rests on the ruleset's strict up-to-date policy (Phase 5
  D-12, no bypass actors) — `--match-head-commit` pins the head, not the base. No
  behaviour change. Rejected: a second `behind_by` read immediately before the merge
  (narrows the window without closing it; one more read per land).

### Solid cache (retires `2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`)
- **D-08:** **Invariant: a solid returned by `_build_cached` never carries a mesh.**
  Export must not mutate the cached object. Two implementations qualify — export from
  `solid.copy()` (`BRepBuilderAPI_Copy`), or strip the triangulation after export
  (`BRepTools.Clean`) — and the planner picks by **measurement**: time both on the
  reference gear and on the 200-tooth fine gear, preview and fine, and record the numbers
  (the CLAUDE.md standard; `bench/RESULTS.md` is the precedent for where numbers live).
  Proof: a test builds, exports preview (then fine), and asserts `.BoundingBox().zlen ==
  pytest.approx(p.face_width)` on the cached object afterwards, and that the STL bytes are
  unchanged (the debt file measured them byte-identical). Rejected: call-site discipline
  (an `exact_bounds()` helper plus a grep that nothing calls `.BoundingBox()` — the cache
  would still hand out a mutated object). — **Reversibility:** reversible — either
  implementation is local to `_write_export`/`export`.
  - **Amended at plan time (2026-09-25, human decision on 06-RESEARCH.md findings):**
    (a) the installed `cadquery-ocp` exposes `BRepTools.Clean_s(shape.wrapped)`, not
    `.Clean` — the name above is corrected, not the intent. (b) The implementation is
    **`solid.copy()`**. Research timed both on reference / 200-tooth × preview / fine:
    copy 23.1 / 70.9 / 260.9 / 824.2 ms, `Clean_s` 20.2 / 63.1 / 244.9 / 791.3 ms.
    `Clean_s` was rejected despite being 5–13 % faster: it strips the mesh *after*
    export, so the cached object carries a mesh for the whole export window, while
    `build()` releases `_LOCK` before callers read the solid — the invariant would hold
    only between exports. (c) The "STL bytes are unchanged" proof is replaced by
    **content equivalence** — triangle count, decoded mesh volume and a watertight,
    consistently oriented shell on the fixed export — because rerunning the debt file's
    byte comparison 20 times matched only 8/20 (OCCT export is not byte-reproducible
    across independently built solids; every measured dimension was identical each time).
- **D-09:** `tests/conftest.py`'s autouse `_reset_solid_cache` is **deleted in the fixing
  commit**. The suite passing without it is the cross-test proof (the `test_model.py`
  `kw={}` case against `test_api.py`'s default-gear export is the collision that exposed
  the defect). Any test that still needs cache isolation must say why, locally.

### Bookkeeping
- **D-10:** The decision log is append-only: the hook's whole-buffer rule and the
  run-conclusion check are recorded as a new entry amending L22 (L22 stays as written);
  the solid-cache invariant is a design secret of `model.py` and gets its own entry. Count
  and numbering are the planner's.
- **D-11:** The milestone audit's informational note is folded into this phase's STATE.md
  touch: the resolved "CI workflow unverified" note also cites run 36122394253 (push of
  `b72b0e1`, the three current jobs, green).

### Claude's Discretion
- Copy vs strip for D-08 — decided by the measurement, with the numbers written down.
- Whether `message_to_check` survives as a trivial function or is deleted with the cut.
- Exact refusal and report wording; test names (they read as requirements).
- One or two decision-log entries for D-10, and their numbers.
- Whether the copy/strip timings go into `bench/RESULTS.md` or the plan's SUMMARY.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The debt being closed (one file per item; each states the residual, the backstops and the closing options)
- `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` — the probe table of what git records per commit mode; D-02 picks its option 1
- `docs/tech_debt/active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md` — the unlisted-job scenario; D-04
- `docs/tech_debt/active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md` — job-level vs step-level `name:`; D-05
- `docs/tech_debt/active/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md` — the three silences and the docstring over-claim; D-06, D-07
- `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` — the measured drift (7.5877 / 7.5196 vs 7.5000), STL bytes unaffected; D-08, D-09
- `docs/tech_debt/TEMPLATE.md`, `docs/tech_debt/INDEX.md` — the resolve lifecycle (status flip, sha, `git mv`, INDEX row) in the fixing commit

### The merge gate as decided in Phase 5
- `.planning/phases/05-ci-observed-green/05-CONTEXT.md` — D-02 (the six tokens), D-03 (squash message), D-05 (pr.land's check order and step 5), D-12 (the ruleset, no bypass actors)
- `.planning/phases/05-ci-observed-green/05-REVIEW.md` — CR-01, the cut-line bypass that 05-06 narrowed
- `docs/architecture/decision_log.md` §L22, §L23 — append-only; new entries amend, never edit
- `docs/HOW_TO_DEVELOP.md` §6 (ship note, `-v` caveat), §7 (cross-CLI review), §8 (`make pr.land`, the ruleset's apply/read-back/removal commands) — Russian
- `scripts/pr_land.py` module docstring — the claim D-07 corrects; `head_refusals`, `parse_runs`, `land`'s poll loop
- `tests/test_pr_land.py` — the drift test's `job_ids` regex and matrix expansion; the `FakeRunner` seam
- `.github/workflows/ci.yml`, `.github/workflows/required-jobs.txt` — the pair the drift test holds equal

### The kernel doorway
- `src/spur/model.py` — `_build_cached` (lru, `SPUR_SOLID_CACHE`), `_write_export` (`exportStl` at the quality's tolerance), `export`; the module docstring's per-worker cache rationale (D-07 affinity from Phase 2)
- `tests/conftest.py` — `_reset_solid_cache` (deleted by D-09); `tests/test_model.py` — `test_builds_one_valid_solid`

### Standards
- `CLAUDE.md` / `AGENTS.md` — the gate, the two standing rules, the debt lifecycle
- `docs/CODING_VALUES.md` — comments carry the measurement or constraint; vendor types stop at `model.py`
- `.planning/v0.1-MILESTONE-AUDIT.md` — the audit that scoped this phase (tech-debt verdict; informational note for D-11)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/skip_tokens.py::find_skip_tokens` — cut-free whole-text search since 05-06; the hook and `pr.land` both call it, and D-06's commit-message check reuses it unchanged.
- `scripts/pr_land.py::parse_runs` already parses `conclusion` into the run record (`WorkflowRun.conclusion: str | None`); D-04 only reads it in `head_refusals`.
- `scripts/pr_land.py`'s `Runner` seam and `tests/test_pr_land.py`'s `FakeRunner` (answers by argv substring) — every new refusal and every report branch is an offline case.
- `tests/test_pr_land.py`'s drift test — the `jobs:`-section regex and `python: [...]` matrix expansion D-05 extends.
- `src/spur/model.py::_build_cached` / `_write_export` — the two functions D-08 touches; `build()` and `export()` are the only public doorways.
- `tests/test_skip_tokens.py` — 27 cases; the cut-line cases flip to "refused below a cut line".

### Established Patterns
- Pure decision core / thin network shell (05-02): decisions are plain functions over parsed `gh` JSON; the shell is exercised live, read-only.
- Git behaviour is probed in a scratch repository and the probe recorded (05-01's scissors bytes, the debt file's per-mode table) — the hook change is verified the same way, plus two real pre-commit runs (refused / passed).
- Numbers are measured and written down (`bench/RESULTS.md`, L17–L19); a choice between two implementations is made on timings, not on taste.
- Every commit goes through the ~45 s pre-commit `make verify` with plain `git commit` (the `gsd_run query commit` wrapper's 30 s timeout kills it); the `commit-msg` hook refuses skip tokens — no message may quote one.
- Debt resolved in the fixing commit; INDEX row moved in the same commit.

### Integration Points
- `scripts/skip_tokens.py::main` (hook entry) and `.pre-commit-config.yaml`'s `no-skip-token` hook — unchanged wiring, changed body.
- `scripts/pr_land.py::head_refusals` (D-04), `land` step 5 (D-06), module docstring (D-07); `Makefile`'s `pr.land` target is untouched.
- `docs/HOW_TO_DEVELOP.md` §6 (D-03) and §8 (D-04's rule, D-07's split).
- `src/spur/model.py::_write_export`/`export` (D-08); `tests/conftest.py` (D-09); `docs/architecture/decision_log.md` (D-10); `.planning/STATE.md` blocker note (D-11).

</code_context>

<specifics>
## Specific Ideas

- The hook is a wall, not a heuristic: with the cut gone there is no content the hook trusts; the only false positive is a `-v` diff quoting a token, and the message tells the author what to do.
- "Green" for `pr.land` means the run's own verdict *and* the named jobs — a run with a failing job we have not listed yet is not green.
- The measured drift to reproduce in D-08's test: zlen 7.500000200000001 before export, 7.587720608891235 after preview STL export (≈ preview's 0.08 mm linear deflection), 7.519603716332508 after fine — from the debt file, `GearParams()` teeth=19.
- Runs to cite in D-11: 36122394253 is the push run of `b72b0e1` with exactly `test (3.12)`, `vendor-bundle`, `image`.

</specifics>

<deferred>
## Deferred Ideas

- Reading `required-jobs.txt` from the PR head sha (D-04 rejected it for now) — revisit if a PR that grows the job set is ever refused for the wrong reason.
- A second `behind_by` read immediately before `gh pr merge` (D-07 rejected it) — revisit if a stale merge is ever observed despite the ruleset.
- The concurrent-latency investigation stays in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` with its own trigger; not this phase.
- A coverage floor (`docs/tech_debt/active/2026-09-21-no-coverage-floor.md`) — separate item, unchanged.

</deferred>

---

*Phase: 06-address-tech-debt-merge-gate-solid-cache*
*Context gathered: 2026-09-25*
