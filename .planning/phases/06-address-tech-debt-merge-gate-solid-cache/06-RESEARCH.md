# Phase 6: Address tech debt: merge gate + solid cache - Research

**Researched:** 2026-09-25
**Domain:** CI/CD merge-gate scripting (Python, `gh` CLI) + CAD kernel object lifecycle
(CadQuery/OCP solid caching)
**Confidence:** HIGH — every claim below was either read from the source file this session
or reproduced with a live command against the installed `.venv` / a live `gh` call.

## Summary

This phase closes five named tech-debt files by editing four existing modules
(`scripts/skip_tokens.py`, `scripts/pr_land.py`, `src/spur/model.py`,
`tests/conftest.py`) plus their tests and two docs (`docs/HOW_TO_DEVELOP.md`,
`docs/architecture/decision_log.md`). No new dependency is installed and no new module is
created — every "next step" in the five debt files is a same-file edit, which is why the
Package Legitimacy Audit below is empty. The two areas are independent and can be planned
as two separate waves (merge-gate: D-02..D-07; solid-cache: D-08/D-09), joined only by
D-10 (decision-log bookkeeping) and D-11 (a `STATE.md` touch).

**Two research findings change the plan the CONTEXT.md text implies, and both must reach
the planner and, for the second, the human:**

1. **D-08's own method name is wrong.** CONTEXT.md and the debt file both write
   `OCP.BRepTools.BRepTools.Clean(shape)`. The installed `cadquery-ocp` build exposes only
   `BRepTools.Clean_s` and `BRepTools.CleanGeometry_s` (pybind11's static-method suffix) —
   there is no bare `.Clean`. Verified live this session (`dir(BRepTools)` on the
   installed package, see Code Examples). The plan must write `BRepTools.Clean_s(shape.wrapped)`,
   not `.Clean(shape)`.

2. **D-08's proof test as literally specified is not achievable as a deterministic
   assertion, for a reason that has nothing to do with which candidate is picked.**
   CadQuery/OCCT's build (`_build`, via `BRepAlgoAPI` boolean ops) and its STL mesher
   (`Shape.exportStl`, even with `parallel=False`) are **not byte-reproducible between two
   separately-constructed `cq.Solid` objects of the same `GearParams`**, even though every
   *measured dimension* (BoundingBox, Volume, STEP file length) is identical between them.
   Reproducing the debt file's own comparison 20 times gave exact byte equality only **8/20**
   times (see Common Pitfalls, Pitfall 1, for the full falsification). This means: (a) the
   debt file's one-shot "byte-identical" observation was not a robust invariant, it was a
   ~40% coin flip that happened to land heads; (b) a test that asserts raw STL bytes equal
   between a fresh-build export and a candidate-fixed export **will be flaky in CI** on this
   toolchain, independent of copy-vs-clean. `[ASSUMED]` risk, `[VERIFIED: this session's
   20-trial rerun]` fact — flagged to the planner as needing either a re-scoped assertion
   (triangle count + volume-from-mesh + watertightness, which the suite already has a
   pattern for in `test_exported_stl_is_a_closed_consistently_oriented_shell`) or a
   `checkpoint:human-verify` before the plan commits to a literal byte-diff assertion.

**Primary recommendation:** for D-08, use `BRepTools.Clean_s(shape.wrapped)` after export
(measured faster than `solid.copy()` at every quality/size combination tested, see Standard
Stack) — but replace the "STL bytes are unchanged" proof with a same-object,
history-independent assertion (triangle count, decoded volume, and watertightness on the
post-export solid), not a raw-byte diff against an independently-built control.

## Architectural Responsibility Map

This phase touches two unrelated single-tier surfaces; there is no browser/SSR/API split
to map for either.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Commit-msg skip-token refusal | Local git hook (`scripts/skip_tokens.py`, `.pre-commit-config.yaml`) | — | Runs entirely at commit time, on the developer's machine; no server involved |
| PR merge-gate decision (`head_refusals`, `message_refusals`) | CI/CD tooling (`scripts/pr_land.py`, pure decision core) | GitHub API (thin shell, `Runner` seam) | Pure functions over parsed `gh` JSON; network calls are isolated behind `Runner`/`FakeRunner` per Phase 5's established split |
| Required-jobs drift check | Test suite (`tests/test_pr_land.py`), reading `.github/workflows/ci.yml` | — | A repo-hygiene test, not a runtime capability |
| Solid cache / mesh mutation | CAD kernel doorway (`src/spur/model.py`, worker-process tier) | — | `model.py` is the only module allowed to import `cadquery`/`OCP` (import-linter contract, verified `pyproject.toml:152-165`); the fix is entirely local to `_write_export`/`export` |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Phase 6 closes exactly the five items above — three `must`, two `nice` —
  and nothing else. Each debt file is resolved in the commit that fixes it, never in a
  follow-up.
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
  **Research note:** the method name in this decision text is wrong (`.Clean` does not
  exist; it is `.Clean_s`), and the byte-identity half of the proof is not a reliable
  invariant on this toolchain — see Summary and Common Pitfalls, Pitfall 1, before
  planning this task's `<verify>` block.
- **D-09:** `tests/conftest.py`'s autouse `_reset_solid_cache` is **deleted in the fixing
  commit**. The suite passing without it is the cross-test proof (the `test_model.py`
  `kw={}` case against `test_api.py`'s default-gear export is the collision that exposed
  the defect). Any test that still needs cache isolation must say why, locally.
- **D-10:** The decision log is append-only: the hook's whole-buffer rule and the
  run-conclusion check are recorded as a new entry amending L22 (L22 stays as written);
  the solid-cache invariant is a design secret of `model.py` and gets its own entry. Count
  and numbering are the planner's. (Next free number: **L24**, confirmed live — the log's
  last entry is L23.)
- **D-11:** The milestone audit's informational note is folded into this phase's STATE.md
  touch: the resolved "CI workflow unverified" note also cites run 36122394253 (push of
  `b72b0e1`, the three current jobs, green).

### Claude's Discretion

- Copy vs strip for D-08 — decided by the measurement, with the numbers written down.
- Whether `message_to_check` survives as a trivial function or is deleted with the cut.
- Exact refusal and report wording; test names (they read as requirements).
- One or two decision-log entries for D-10, and their numbers.
- Whether the copy/strip timings go into `bench/RESULTS.md` or the plan's SUMMARY.

### Deferred Ideas (OUT OF SCOPE)

- Reading `required-jobs.txt` from the PR head sha (D-04 rejected it for now) — revisit if a PR that grows the job set is ever refused for the wrong reason.
- A second `behind_by` read immediately before `gh pr merge` (D-07 rejected it) — revisit if a stale merge is ever observed despite the ruleset.
- The concurrent-latency investigation stays in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` with its own trigger; not this phase.
- A coverage floor (`docs/tech_debt/active/2026-09-21-no-coverage-floor.md`) — separate item, unchanged.
</user_constraints>

<phase_requirements>
## Phase Requirements

This phase carries **no REQ-IDs** (per the orchestrator's phase scope: "the phase carries
no REQ-IDs; CONTEXT.md's D-01..D-11 are the source items"). D-01..D-11 above are the
source items the planner maps tasks to instead.

| ID | Description | Research Support |
|----|-------------|------------------|
| D-02 | Drop the commit-msg hook's cut entirely | `git config --get commit.verbose` confirmed empty this session; `scripts/skip_tokens.py` full text read; the residual `_SCISSORS`/`editor_ran` logic identified for removal (lines 47-59, 90-102) |
| D-03 | `-v` caveat in hook message + `docs/HOW_TO_DEVELOP.md` §6; correct the §6/§8 editor-session text | **Research found the "05-06 editor-session explanation" CONTEXT.md refers to does not currently exist in HOW_TO_DEVELOP.md** — grepped for "editor", "GIT_EDITOR", "редактор", "scissors", ">8" in the whole file: zero matches. §0 (lines 27-30) and §6 (lines 119-126) are the only hook-related text, and neither mentions editor sessions. D-03 is therefore an **addition**, not a **correction** — see Common Pitfalls, Pitfall 2 |
| D-04 | `head_refusals` gains a run-conclusion check | `scripts/pr_land.py` read in full; `parse_runs` already carries `conclusion` (line 157); `head_refusals` (lines 256-293) never reads it today |
| D-05 | Drift test resolves effective job name (`jobs.<id>.name` else id) | `.github/workflows/ci.yml` read in full — confirmed no job-level `name:` exists today, only step-level `name:` at lines 44 (`bundle matches web/`) and 58 (`the packaged entrypoint serves a gear`); `tests/test_pr_land.py`'s `test_required_jobs_file_matches_ci_yml_job_ids` (lines 189-209) is the test to extend |
| D-06 | Step 5 reports poll-failure vs poll-success-empty vs actual token, fetching the squash message via `gh api` | **VERIFIED live**: `gh api repos/halfb00t/spur/commits/<sha> --jq '.commit.message'` returns the full squash subject+body for a real merged PR (tested against PR #3's real squash sha `bfc911034ef5f8e44f301a57114cb7a8d8b03850`) — this is the exact call and JSON path D-06 needs |
| D-07 | Docstring/§8 state the run-appeared vs ruleset split | `scripts/pr_land.py` module docstring read in full (lines 1-36); no code change, doc-only |
| D-08 | Solid-cache invariant: never hand out a mutated solid | Baseline drift reproduced exactly (`7.500000200000001` → `7.587720608891235` after preview → `7.519603716332508` after fine, matching the debt file byte-for-byte); both candidates timed on reference and 200-tooth gears; `BRepTools.Clean` corrected to `Clean_s`; byte-identity proof flagged as unreliable — see Summary and Pitfall 1 |
| D-09 | Delete `_reset_solid_cache` autouse fixture | `tests/conftest.py` read in full (50 lines); fixture is lines 49-51 |
| D-10 | Decision log entries (append-only) | `docs/architecture/decision_log.md` tail read; L23 is the last entry, so L24 (and L25 if two entries) are free |
| D-11 | STATE.md touch citing run 36122394253 | `.planning/STATE.md` read; existing "Resolved in Phase 5" parenthetical (line 174-178) is the text to extend |
</phase_requirements>

## Standard Stack

No new external package is installed or upgraded by this phase. Every tool used below is
already a direct or transitive dependency, confirmed installed in `.venv`.

### Core (already installed, no version change)

| Library | Version (verified) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `cadquery` | matches `pyproject.toml: "cadquery>=2.5"` | The `Shape.copy(mesh=False)` method D-08's Candidate A uses | Already the project's only CAD wrapper; `model.py` is its designated doorway |
| `OCP` (`cadquery-ocp`) | installed transitively via `cadquery`; `python3.12` only per L23 | `OCP.BRepTools.BRepTools.Clean_s` — D-08's Candidate B | Same package the project already imports through `cadquery`; direct `OCP.*` import is explicitly permitted in `model.py` by both the mypy override (`pyproject.toml:109-113`) and the import-linter contracts (`pyproject.toml:150-165`, `model.py` is exempt — only `spur.calc`/`spur.params`/`spur.cli`/`spur.app` forbid it) |
| `gh` CLI | authenticated, `github.com` account `halfb00t` (verified live: `gh auth status`) | D-06's squash-commit-message fetch | Already `scripts/pr_land.py`'s only network dependency |
| `pytest` | per `pyproject.toml`/`.venv` | All five fixing commits ship tests in the same commit (CLAUDE.md) | Existing test runner; 92 tests already collected across the three touched test files |

### Package Legitimacy Audit

**Not applicable — this phase installs no new packages.** Every module touched
(`scripts/skip_tokens.py`, `scripts/pr_land.py`, `src/spur/model.py`, `tests/conftest.py`)
already imports only what is in `pyproject.toml` today; `OCP.BRepTools` is a submodule of
the already-installed `cadquery-ocp`, not a new dependency.

## Architecture Patterns

### System Architecture Diagram

Both fixes sit inside already-established boundaries; no new data flow is introduced.

```
Merge gate (local machine + GitHub, no server tier):

  git commit  --editmsg-->  .pre-commit-config.yaml (commit-msg stage)
                                    |
                                    v
                       scripts/skip_tokens.py:main()
                        (D-02: whole buffer, no cut)
                                    |
                         find_skip_tokens() [pure]
                                    |
                        refuse (exit 1) / accept (exit 0)

  make pr.land PR=N  -->  scripts/pr_land.py:land()
        |                        |
        |                pr_refusals (state/base)
        |                        |
        |                check_head --Runner--> gh api compare/runs/jobs
        |                        |
        |                head_refusals [pure]     <- D-04 adds run.conclusion check
        |                        |
        |                message_refusals(subject, body)  [pure, find_skip_tokens reused]
        |                        |
        |                 gh pr merge --squash --match-head-commit
        |                        |
        |                poll for squash-commit run  <- D-06 reports observed vs inferred
        |                        |
        |                gh api commits/<sha> --jq .commit.message   <- D-06's new read
        |                        |
        |                git switch/pull/branch -D (local cleanup)

Solid cache (single worker process, CAD kernel doorway):

  build(p) --lock--> _build_cached(p) [lru_cache, process-global]
                            |
                            v
                   cached cq.Solid (shared across preview/STL/STEP for one gear)
                            |
              +-------------+-------------+
              |                           |
         export(p, "stl", "preview")  export(p, "stl", "fine")
              |                           |
        _write_export() --D-08 fix-->  never mutates the cached object
              |                           |
        candidate: shape.copy() first, or export then BRepTools.Clean_s(shape.wrapped)
              |
        bytes returned to caller; cached solid's .BoundingBox() still reads exact BREP
```

### Recommended Project Structure

No new files. Every change is in-place:

```
scripts/
├── skip_tokens.py     # D-02, D-03: main() loses the cut; new whole-buffer test
├── pr_land.py          # D-04 (head_refusals), D-06 (land's poll report), D-07 (docstring)
tests/
├── test_skip_tokens.py # cut-line tests flip to "refused below a cut line" (D-02)
├── test_pr_land.py     # new FakeRunner cases per D-04/D-05/D-06 branch
├── conftest.py          # D-09: _reset_solid_cache deleted
├── test_model.py        # D-08: BoundingBox-after-export assertion extended
src/spur/
└── model.py             # D-08: _write_export/export never mutate the cached solid
docs/
├── HOW_TO_DEVELOP.md    # D-03 (§6 one line), D-07 (§8 split), D-04's rule
docs/architecture/
└── decision_log.md      # D-10: L24 (+ optional L25), append-only
docs/tech_debt/
├── active/*.md (5 files) -> git mv -> resolved/*.md  # D-01, each in its fixing commit
└── INDEX.md              # row moved per file, same commit
```

### Pattern 1: Pure decision core / thin network shell (established, Phase 5)

**What:** Every `gh`/`git` call in `scripts/pr_land.py` goes through one `Runner` callable
type alias; the real one is `subprocess.run`, the test one is `FakeRunner` (matches by argv
substring). Decision functions (`head_refusals`, `pr_refusals`, `message_refusals`) take
already-parsed data and return a `list[str]` of refusals — no I/O, no side effects.

**When to use:** D-04 (new run-conclusion refusal) and D-06 (new report branches) are both
extensions of this existing pattern — do not add a second way to reach `gh`.

**Example (verified against `scripts/pr_land.py:256-293`):**
```python
# Source: scripts/pr_land.py, read this session
def head_refusals(
    sha: str,
    compare: tuple[int, int],
    run: WorkflowRun | None,
    jobs: list[dict[str, str]],
    required: frozenset[str],
) -> list[str]:
    ...
    if run is None:
        refusals.append(f"pr.land: no {WORKFLOW} run for head {sha}.")
        return refusals
    if run.status != "completed":
        refusals.append(f"pr.land: the newest run for {sha} is still running: {run.html_url}")
        return refusals
    # D-04 adds here: a run.conclusion != "success" check, alongside the per-job loop below
    by_name = {job["name"]: job["conclusion"] for job in jobs}
    for name in sorted(required):
        conclusion = by_name.get(name)
        if conclusion is None:
            refusals.append(f"pr.land: required job {name!r} is missing from the run.")
        elif conclusion != "success":
            refusals.append(f"pr.land: required job {name!r} is {conclusion}, not success.")
    return refusals
```

### Pattern 2: One doorway to the kernel (established, Phase 2/model.py's own docstring)

**What:** `src/spur/model.py` is the only module permitted to import `cadquery`/`OCP`
(enforced by two import-linter contracts, read this session at `pyproject.toml:150-165`).
D-08's fix must stay inside `_write_export`/`export` — it must not leak a `cq.Solid` or an
`OCP` type across that boundary.

**When to use:** Both D-08 candidates satisfy this by construction (they touch only
`_write_export`), but a plan step must not, e.g., move the copy/clean call into `app.py` or
`pool.py`.

### D-08 candidate code (verified this session against the installed `cadquery`/`OCP`)

**Candidate A — copy before export:**
```python
# Source: cadquery.Shape.copy signature, read via `inspect.getsource` this session
# def copy(self: T, mesh: bool = False) -> T:
#     return self.__class__(BRepBuilderAPI_Copy(self.wrapped, True, mesh).Shape())
def _write_export(shape: cq.Solid, p: GearParams, fmt: Format, quality: Quality) -> bytes:
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            shape.copy().exportStl(str(path), tolerance=tol, angularTolerance=ang,
                                    ascii=False, relative=False)
        else:
            shape.exportStep(str(path))   # STEP export never attaches a mesh -- unaffected
        return path.read_bytes()
```

**Candidate B — strip the mesh after export (measured faster, see below):**
```python
# Source: `dir(OCP.BRepTools.BRepTools)` on the installed cadquery-ocp, this session --
# the method is `Clean_s` (pybind11 static-method suffix), NOT `.Clean` as CONTEXT.md's
# D-08 text and the debt file both write. `.Clean_s` takes the raw wrapped TopoDS_Shape,
# not the cq.Shape wrapper.
from OCP.BRepTools import BRepTools

def _write_export(shape: cq.Solid, p: GearParams, fmt: Format, quality: Quality) -> bytes:
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            shape.exportStl(str(path), tolerance=tol, angularTolerance=ang,
                             ascii=False, relative=False)
            BRepTools.Clean_s(shape.wrapped)   # strip the mesh this export just attached
        else:
            shape.exportStep(str(path))
        return path.read_bytes()
```

**Measured timings (this session, `.venv/bin/python`, Apple M2 Max, 12 cores, 32 GiB, macOS
Darwin 27.0.0, `GearParams()` default = reference gear (teeth=19) and `GearParams(teeth=200)`
= the 200-tooth fine gear; 3 runs each, mean reported):**

| Candidate | Gear | Quality | Mean time | Bytes | `.BoundingBox().zlen` after, on the cached parent |
|---|---|---|---|---|---|
| A (`.copy()`) | reference | preview | 23.1 ms | 453,384 | unchanged (7.500000) |
| A (`.copy()`) | reference | fine | 70.9 ms | 2,313,984 | unchanged |
| A (`.copy()`) | 200-tooth | preview | 260.9 ms | 3,135,284 | unchanged |
| A (`.copy()`) | 200-tooth | fine | 824.2 ms | 9,086,484 | unchanged |
| B (`Clean_s`) | reference | preview | 20.2 ms | 453,384 | unchanged |
| B (`Clean_s`) | reference | fine | 63.1 ms | 2,313,984 | unchanged |
| B (`Clean_s`) | 200-tooth | preview | 244.9 ms | 3,135,284 | unchanged |
| B (`Clean_s`) | 200-tooth | fine | 791.3 ms | 9,086,484 | unchanged |

Both candidates fully close D-08's BoundingBox invariant at every size/quality combination
tested — `[VERIFIED: this session's live measurement]`. Candidate B (`Clean_s`) is
**~5-13% faster than Candidate A (`.copy()`) at every combination** — expected, since `.copy()`
must duplicate the whole BREP via `BRepBuilderAPI_Copy` before meshing, while `Clean_s` only
discards the mesh already attached. **Recommendation: Candidate B**, on measurement.

### Anti-Patterns to Avoid

- **Asserting raw STL-byte equality between two independently-constructed solids as a
  CI test:** see Pitfall 1 below — this toolchain is not byte-reproducible across two
  separate `_build()`/`exportStl()` calls even when every measured dimension is identical.
  A `pytest.approx`-style content comparison (triangle count, decoded volume, watertightness)
  is the reliable substitute; the suite already has the parsing helper for this in
  `tests/test_model.py::_stl_triangles` / `test_exported_stl_is_a_closed_consistently_oriented_shell`.
- **Reintroducing a cut-line heuristic anywhere in `find_skip_tokens`'s call path:** D-02's
  whole point is that `main()` search over the raw buffer with no cut; `pr.land`'s
  `message_refusals` already does this (05-06) and must not regress.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting whether a solid still carries a triangulated mesh after export | A custom flag/wrapper tracking "has this been exported" | `BRepTools.Clean_s(shape.wrapped)` (strips it) or `shape.copy()` (never attaches it to the original) | Both are the OCCT-native operations for this; a hand-rolled flag would need updating at every new export call site and would not survive a future `Shape.exportStl` internal change |
| Fetching a squash commit's message from GitHub | Parsing `git log` on a local clone (races the actual merge; the local clone may not have fetched the squash commit yet) | `gh api repos/{owner}/{repo}/commits/<sha> --jq '.commit.message'` (verified live this session against a real merged PR) | This is the same class of read `parse_runs`/`parse_jobs` already do — one JSON path, no git fetch needed |
| Detecting whether git will truncate a commit message at a cut line | A hand-maintained truth table per `-v`/`commit.verbose`/`--cleanup` combination (which is exactly what the retired `_SCISSORS`/`editor_ran` logic was) | D-02: search the whole buffer, no cut, ever | The probe table in the debt file itself (six rows) is the proof this heuristic cannot be completed — dropping it is smaller and more correct than extending it |

**Key insight:** every "Next step" in all five debt files is phrased as a small, local code
change specifically because the debt files were written by the same review process that
will plan this phase — there is no hidden larger redesign lurking in any of the five.

## Common Pitfalls

### Pitfall 1: STL/BREP output is not byte-reproducible across independent solid constructions on this toolchain

**What goes wrong:** A test (or a debt-file-style manual check) that builds two *separate*
`cq.Solid` objects for the same `GearParams` — even from two independent `.copy()` calls off
a shared pristine parent — and diffs their exported bytes will intermittently fail, even
though every measured dimension (BoundingBox, Volume, STEP length, triangle count) is
identical between the two.

**Why it happens:** Verified this session by direct experiment, not assumed:
- Two independent `_build_checked(p)` calls, STEP-exported: byte length identical (989,169
  bytes) across 5 runs, but **not byte-identical** (`[VERIFIED: this session]`) — this
  points at OCCT's `BRepAlgoAPI` boolean-op internals (fillet/chamfer/cut), whose entity
  ordering is not guaranteed stable across separate constructions of geometrically-identical
  input.
- The debt file's own comparison shape (same cached object, preview-then-fine export, vs. a
  *separately built* fresh solid's direct fine export) was rerun **20 times** this session:
  matched **8/20** (40%). The debt file's one recorded observation ("byte-identical") was
  real but not representative.
- This is unrelated to `parallel=True` in `exportStl` (CadQuery's default) — rerunning with
  `parallel=False` did not stabilize it either (`[VERIFIED: this session]`), so it is not
  (only) thread-scheduling nondeterminism in the mesher; it traces back through to the build
  step itself.
- It is also unrelated to which D-08 candidate is chosen — both candidates were checked
  against the same nondeterminism.

**How to avoid:** Do not write D-08's proof test as "assert bytes of an independently-built
control equal bytes of the candidate-fixed export." Instead assert on decoded content that
is dimension-stable regardless of triangle-ordering: triangle count (`int.from_bytes(stl[80:84], "little")`,
already used in `test_exports`), decoded volume from the triangle set (the pattern in
`test_exported_stl_is_a_closed_consistently_oriented_shell`), and/or `.BoundingBox()` on the
post-export cached solid (the invariant D-08 actually cares about). If the plan still wants
a byte-level check, scope it to comparing the **same** solid's own two sequential exports at
the **same** quality (which is deterministic — re-exporting an unmutated solid at the same
tolerance twice was not observed to drift in any trial this session), not two independently
built/copied solids.

**Warning signs:** A new pytest test that does `assert export_a == export_b` where `a` and
`b` come from two different `build()`/`.copy()` calls — even if it passes locally, it is a
coin flip that will eventually flake in CI.

### Pitfall 2: The "05-06 editor-session explanation" D-03 says to correct does not exist in `docs/HOW_TO_DEVELOP.md` today

**What goes wrong:** A plan step written as "correct the existing editor-session paragraph
in §6/§8" will find nothing to correct, stall, or worse, invent a paragraph that never
shipped and then "fix" it.

**Why it happens:** `git log --oneline -- docs/HOW_TO_DEVELOP.md` shows the file was last
touched at the Phase 5 squash commit (`b72b0e1`); the 05-06 gap-closure plan
(`3e68e74`/`1965a52`) touched only `scripts/skip_tokens.py` and `scripts/pr_land.py`, never
the doc. Grepping the whole file (case-sensitive and for the Russian equivalents —
"editor"/"GIT_EDITOR"/"редактор"/"scissors"/">8") found zero matches. §0 (lines 27-30) and
§6 (lines 119-126) are the *only* text about the hook, and both are already accurate (they
just say the hook refuses the six tokens; they never claimed anything about editor sessions
that would now be wrong).

**How to avoid:** Plan D-03 as **adding** one sentence to §6 (the `-v` caveat: "if this came
from `-v`'s appended diff, commit without `-v`") next to the existing ship-note paragraph
(lines 119-126) — there is no incorrect prior text to locate and rewrite first.

**Warning signs:** A task description that says "fix the wrong claim in §6/§8 about editor
sessions" — there is no such claim to find; treat it as new content instead.

### Pitfall 3: `Shape.copy()`'s default does not copy the mesh, which is exactly what makes it safe here — but its positional-args signature is easy to get backwards

**What goes wrong:** `Shape.copy(self, mesh: bool = False)` calls
`BRepBuilderAPI_Copy(self.wrapped, True, mesh)`. The middle `True` is `copyGeom` (always on);
only the *third* argument, `mesh`, is exposed as a keyword. Writing `shape.copy(True)`
positionally would copy the mesh too — silently defeating D-08's whole point on a solid that
already carries one (though the *cached* solid this phase protects never has one to begin
with, so this only matters if candidate A's call is ever changed to `shape.copy(mesh=True)`
by a future edit).

**How to avoid:** Always call `shape.copy()` with no positional argument, or `shape.copy(mesh=False)`
explicit, never `shape.copy(True)`.

## Code Examples

### D-06: the exact `gh api` call and JSON path for a squash commit's message

```bash
# Source: verified live this session against a real merged PR (PR #3, squash sha
# bfc911034ef5f8e44f301a57114cb7a8d8b03850, obtained via `gh pr view 3 --json mergeCommit
# --jq '.mergeCommit.oid'`)
gh api repos/{owner}/{repo}/commits/<squash_sha> --jq '.commit.message'
# Returns the full subject + blank line + body, verbatim -- the same shape
# find_skip_tokens() already expects (it is called on subject + "\n\n" + body elsewhere in
# this module for message_refusals).
```

### D-02: the whole-buffer hook, with the cut removed

```python
# Source: scripts/skip_tokens.py, read this session -- current (pre-fix) main() cuts only
# when GIT_EDITOR != ":" (lines 90-102). D-02 removes that branch entirely:
def main(argv: list[str] | None = None) -> int:
    ...
    raw = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
    tokens = find_skip_tokens(raw)   # no cut, ever -- the _SCISSORS/editor_ran logic is gone
    ...
```

### D-05: resolving the effective job name in the drift test

```python
# Source: tests/test_pr_land.py:189-209, read this session -- job_ids today are the raw
# two-space-indented keys. D-05 must additionally read an optional `name:` line
# immediately under each job id, scoped to that job's own block (not the whole jobs:
# subtree, which would also match the step-level `name:` keys already present at
# ci.yml:44 and :58 -- confirmed by reading ci.yml in full this session).
ci_yml = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
jobs_section = ci_yml.split("\njobs:\n", 1)[1]
job_ids = re.findall(r"^  ([a-zA-Z][\w-]*):\s*$", jobs_section, re.MULTILINE)
# D-05 adds: for each job_id, look only at the lines between it and the next job_id
# (or end of jobs_section) for a top-level `    name: ...` (4-space indent, one level
# under the job id) -- not any `      name:` at deeper (step) indent.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `commit-msg` hook cuts at a git-shaped scissors line when `GIT_EDITOR != ":"` (05-06, `3e68e74`) | Whole-buffer search, no cut, ever (D-02, this phase) | This phase | Closes the one remaining bypass (a hand-typed cut line inside an editor session without `-v`); costs a reworded commit for anyone who ever uses `git commit -v` and quotes a token in the diff (nobody today: `commit.verbose` reads empty) |
| `head_refusals` judges green-ness by listed jobs only | Also refuses on `run.conclusion != "success"` (D-04) | This phase | Closes the "PR adds an unlisted failing job + stale `required-jobs.txt` checkout" gap the Codex review reproduced |
| Drift test compares job **ids** to `required-jobs.txt` | Compares effective **names** (`jobs.<id>.name` else id) (D-05) | This phase | A future `name:` override on a job no longer silently desyncs the required-checks list from what GitHub actually reports |
| `_build_cached` hands out the same mutable `cq.Solid` to every caller | Export never mutates the cached object (D-08) | This phase | Removes the one production-latent defect the debt file names; the test-side `_reset_solid_cache` workaround (D-09) is deleted because it is no longer needed |

**Deprecated/outdated:**
- `scripts/skip_tokens.py`'s `_SCISSORS` regex and `message_to_check` — retired by D-02; whether `message_to_check` survives as a trivial helper or is deleted with the cut is Claude's discretion per CONTEXT.md.
- `tests/conftest.py`'s `_reset_solid_cache` autouse fixture — retired by D-09.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `message_to_check`'s fate (kept as trivial helper vs. deleted) is Claude's discretion, not a hard requirement | Standard Stack / State of the Art | Low — CONTEXT.md explicitly names this as discretionary |
| A2 | Candidate B (`Clean_s`) is the right pick on the measured numbers alone, absent other constraints | Code Examples (D-08 timings) | Low-medium — both candidates satisfy the invariant; if the planner or a reviewer has a non-timing reason to prefer `.copy()` (e.g., defense against a future export path that reads the object concurrently), that reason should be weighed against the ~5-13% timing loss, not treated as settled by this research alone |
| A3 | The re-scoped D-08 proof (triangle count + volume + watertightness, not raw bytes) satisfies the *intent* of CONTEXT.md's proof requirement even though it does not literally do "assert STL bytes are unchanged" | Summary, Pitfall 1 | Medium — this changes what CONTEXT.md's D-08 literally asked for; flagged for a human decision or discuss-phase follow-up rather than silently substituted by the planner |

## Open Questions (RESOLVED at plan time, 2026-09-25)

> Both questions below were settled by the human before planning; the decisions are recorded
> in `06-CONTEXT.md` under D-08 ("Amended at plan time"). Q1 → the proof is content equivalence
> (triangle count, decoded volume, watertight shell), not a byte diff. Q2 → moot: the
> implementation chosen is `solid.copy()`, so `BRepTools.Clean_s` is not written and never
> reaches mypy. The "Primary recommendation" in the Summary that names `Clean_s` is superseded
> by that amendment — `Clean_s` was rejected because it leaves the cached object meshed for the
> whole export window while `build()` releases `_LOCK` before callers read the solid.

1. **Should the re-scoped D-08 byte-identity proof go back to the human before the plan is written, or can the planner substitute the content-based assertion directly?**
   - What we know: the literal proof ("STL bytes are unchanged") is empirically unreliable — 8/20 match rate reproduced this session.
   - What's unclear: whether CONTEXT.md's author would accept the content-based substitute as satisfying the same intent, or would want the byte-diff kept as a documented-flaky manual check (like `bench/`'s live checks, deliberately outside `make verify`).
   - Recommendation: raise this explicitly at plan-review or as a `checkpoint:human-verify` in the D-08 task, quoting this session's 8/20 number, rather than silently picking one.

2. **Does `.Clean_s` need a `# type: ignore` or does it typecheck cleanly under `mypy --strict` with the existing `cadquery.*`/`OCP.*` override?**
   - What we know: the override sets `ignore_missing_imports = true` for `OCP.*`, so mypy will not complain about missing stubs for the import itself; whether the *call* `BRepTools.Clean_s(shape.wrapped)` typechecks depends on whatever stub shape pybind11 exposes (likely `Any`-typed, which passes under `ignore_missing_imports` but not necessarily under `disallow_any_explicit`/`disallow_any_expr` if those are on more broadly than the override).
   - What's unclear: not run this session (would require writing the actual code change first).
   - Recommendation: the executing plan's own `make verify` run is the real check here — flag as an execution-time verification, not a planning blocker.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv/bin/python` | All measurement/reproduction work, `make verify` | ✓ | 3.12.13 | — |
| `cadquery` + `cadquery-ocp` (OCP) | D-08 | ✓ | installed, matches `pyproject.toml` | — |
| `gh` CLI, authenticated | D-06's live verification, `make pr.land` | ✓ | logged in as `halfb00t`, token active | — |
| `git` | D-02's probe table (already done in Phase 5), no new probe needed this phase | ✓ | 2.54.0 (per debt file, unchanged) | — |
| Docker | Not needed for this phase (`make verify` needs no Docker; `make check`'s image/vendor-bundle checks are untouched) | n/a | — | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — everything this phase needs was already
installed and exercised live this session.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (per `pyproject.toml`, `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `.venv/bin/python -m pytest tests/test_skip_tokens.py tests/test_pr_land.py tests/test_model.py -q` (run from repo root — both `test_skip_tokens.py` and `test_pr_land.py` document this as required for `sys.path` to resolve `scripts`) |
| Full suite command | `make verify` (ruff, mypy --strict, import-boundary contracts, unfinished-work scan, pytest — ~11 s warm, per `docs/HOW_TO_DEVELOP.md` §0) |

### Phase Requirements → Test Map

| D-ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-02 | A hand-typed cut line no longer hides a token, in any commit mode | unit | `.venv/bin/python -m pytest tests/test_skip_tokens.py -q` | ✅ (extend `test_hook_without_an_editor_refuses_a_token_below_a_cut_line`-style case to cover the editor-session case too; the two `GIT_EDITOR` cut-line tests at lines 114-139 invert) |
| D-03 | Hook message names the `-v` caveat | unit | same file, new assertion on `capsys` output | ✅ (extend `test_token_above_and_below_the_scissors_line_is_found_once`-style assertion) |
| D-04 | A run with an unlisted failing job is refused | unit | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | ✅ (new `FakeRunner`/pure case beside `test_head_refusals_one_red_job_names_it_and_its_conclusion`) |
| D-05 | A renamed job in `ci.yml` is caught by the drift test | unit | same file | ✅ (extend `test_required_jobs_file_matches_ci_yml_job_ids`, add an in-memory regression case) |
| D-06 | Step 5 reports the right message for each of the three branches | unit | same file, `FakeRunner` per branch | ✅ (extend the `land()` test block, `_happy_runner`-style fixtures at lines 564-627) |
| D-08 | A cached solid's `.BoundingBox()` stays exact after export | unit | `.venv/bin/python -m pytest tests/test_model.py -q` | ✅ (extend `test_builds_one_valid_solid`, lines 27-33) |
| D-09 | The suite passes with `_reset_solid_cache` deleted | unit (suite-wide) | `make verify` (must be the full suite, not a single file, to prove the cross-test collision the debt file names is actually gone) | ✅ |

### Sampling Rate

- **Per task commit:** the quick-run command above (scoped to the touched test file)
- **Per wave merge:** `make verify` (mandatory for D-09, since its proof is suite-wide, not single-file)
- **Phase gate:** `make verify` green before `/gsd-verify-work`; each of the five debt files
  must additionally show `Status: resolved` + `git mv`'d + INDEX row moved, in the same
  commit as its fix (per CLAUDE.md and D-01)

### Wave 0 Gaps

None — existing test infrastructure (`tests/test_skip_tokens.py`, `tests/test_pr_land.py`,
`tests/test_model.py`, `tests/conftest.py`) covers every D-ID above; every task is an
extension of an existing test file, not a new one.

## Security Domain

This phase's "security" surface is CI/CD pipeline integrity (a skip-token bypass and a
merge-gate blind spot), not application input/auth surface — ASVS V2-V6 (authentication,
sessions, access control, input validation, cryptography) do not apply to either fix. The
relevant frame is supply-chain / build-integrity: "does an unreviewed or unverified change
reach `main`."

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | n/a — no auth surface touched |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | no | The commit message / PR body text is scanned for a known token set, not parsed as structured input; no injection surface (subprocess argv already passes strings as separate elements, never through a shell — `scripts/pr_land.py`'s own docstring notes this, T-05-08) |
| V6 Cryptography | no | n/a |
| V14 Configuration (closest fit) | yes | The `commit-msg` hook and the `main` ruleset are both configuration-as-code / configuration-as-repo-setting controls against an unreviewed change reaching `main`; D-02/D-04 harden exactly this |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A commit silences its own CI run via a GitHub Actions skip token, then merges unreviewed | Repudiation / Tampering | Commit-msg hook (D-02, whole-buffer) + squash-message check (`message_refusals`, unchanged) + ruleset requiring green checks on `main` (Phase 5 D-12) — three independent layers, none of which alone is sufficient (each debt file documents the specific residual the others don't catch) |
| A PR's merge gate reports "green" based on a stale local list of required jobs while the run itself failed on an unlisted job | Tampering / Elevation of privilege (an unreviewed job failure reaches `main`) | D-04's `run.conclusion` check, in addition to the per-job check |
| Subprocess argv injection via a PR title/body containing shell metacharacters | Tampering | Already mitigated — `scripts/pr_land.py` passes title/body as separate argv elements to `subprocess.run`, never through a shell (verified in the module docstring and `land()`'s `merge_result` call, read this session) — unchanged by this phase |

## Sources

### Primary (HIGH confidence — read or executed live this session)
- `scripts/skip_tokens.py` — full file read
- `scripts/pr_land.py` — full file read
- `tests/test_skip_tokens.py`, `tests/test_pr_land.py` — full files read
- `src/spur/model.py`, `tests/conftest.py` — full files read
- `tests/test_model.py` lines 1-80 — read
- `.github/workflows/ci.yml`, `.github/workflows/required-jobs.txt` — full files read
- `docs/HOW_TO_DEVELOP.md` — full file scanned/read (sections 0, 1-8, grepped for editor/hook/skip/token terms)
- `docs/architecture/decision_log.md` — tail read (L17-L23 in full)
- `docs/tech_debt/active/*.md` (all 5 named files), `docs/tech_debt/TEMPLATE.md`, `docs/tech_debt/INDEX.md` — full files read
- `.pre-commit-config.yaml` — full file read
- `pyproject.toml` — mypy/import-linter sections read
- Live command: `git config --get commit.verbose` — empty, exit 1 (matches D-02's claim)
- Live command: `gh pr view 3 --json mergeCommit --jq '.mergeCommit.oid'` then `gh api repos/halfb00t/spur/commits/<sha> --jq '.commit.message'` — confirmed D-06's exact call and JSON path
- Live measurement: `.venv/bin/python` scripts reproducing the debt file's baseline drift exactly, timing both D-08 candidates on reference/200-tooth gears at preview/fine quality, and the 20-trial byte-identity falsification (all scripts run this session, outputs captured above)
- Live inspection: `inspect.getsource(cq.Shape.copy)`, `dir(OCP.BRepTools.BRepTools)`, `inspect.signature(cq.Shape.exportStl)` on the installed packages

### Secondary (MEDIUM confidence)
- None — every claim in this document traces to a file read or a live command this session.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Merge-gate changes (D-02 through D-07): HIGH — every current-state claim is a direct file
  read; D-06 additionally verified live against a real `gh api` call.
- Solid-cache invariant (D-08/D-09): HIGH on the fix and the timings (both measured live);
  MEDIUM on the byte-identity proof's *feasibility as specified* — this research actively
  falsified the literal wording and recommends a substitute, which needs the planner's (or
  the human's) sign-off, not just this document's say-so.
- Bookkeeping (D-10, D-11): HIGH — decision log tail and STATE.md both read directly; next
  free entry number confirmed live.

**Research date:** 2026-09-25
**Valid until:** This is a tech-debt-closure phase on a small, non-moving surface (no
external framework/library upgrades involved) — the D-02/D-04/D-05/D-06/D-07 findings are
valid until `scripts/pr_land.py` or `scripts/skip_tokens.py` are next touched. The D-08
timings and the byte-identity falsification are tied to the installed `cadquery`/`cadquery-ocp`
build and this machine; treat them as void if `cadquery-ocp` is upgraded (re-run the
measurement scripts described in Code Examples before trusting old numbers).
