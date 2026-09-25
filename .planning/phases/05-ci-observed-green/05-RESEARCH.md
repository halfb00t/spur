# Phase 5: CI Observed Green - Research

**Researched:** 2026-09-25
**Domain:** Git/GitHub merge-gate tooling (pre-commit hooks, GitHub Actions skip semantics, `gh` CLI/API, Python version floor)
**Confidence:** HIGH (every load-bearing claim was checked against a live `gh api`/`gh` call against this repo, the actual repo files, or an official docs page fetched this session; the two genuine gaps are called out explicitly in Open Questions and Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Phase 5 is reframed from "observe CI run" to "CI is the trusted merge gate", per
  the evidence in `<specifics>`. "Bookkeeping only" (record URLs, leave the `must` debt file
  active) was rejected: the debt file itself says "Phase 5 owns the decision".
- **D-02:** A repo-owned **`commit-msg` hook** in `.pre-commit-config.yaml` rejects the six
  tokens GitHub Actions honours — `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]`,
  `[actions skip]`, `skip-checks: true` — case-insensitive, anywhere in the message, subject
  or body. Ships with a test that feeds it sample messages. Why the hook and not only the
  repo setting: GitHub applies the token to the *PR head* as well as to a push, so a
  token-carrying ship note leaves the PR with zero checks (PR #2 head `20b63e4`); and a
  literal mention in *prose* is enough — Phase 4's note "No [ci skip] on purpose" (`6fce500`)
  got skipped too and needed the empty trigger commit `87d500e`. Blocking at commit time
  closes both, for every tool that commits here.
- **D-03:** Repository squash-merge settings become `squash_merge_commit_title=PR_TITLE`,
  `squash_merge_commit_message=PR_BODY` (today: `COMMIT_OR_PR_TITLE` / `COMMIT_MESSAGES`, the
  concatenation that carried the token into `538d26f` and `bfc9110`). Applied with one
  `gh api -X PATCH repos/halfb00t/spur ...`; the exact command is recorded in
  `docs/HOW_TO_DEVELOP.md` §8 because a repo setting is not in git. `main`'s commit then
  carries the curated PR description `gsd-ship` builds from the planning artifacts instead
  of a 17–22 KB subject list. Rejected: `BLANK` (title only), keeping `COMMIT_MESSAGES`.
- **D-04:** `gsd-ship`'s `track_shipping` step commits the ship note with `[ci skip]` in the
  subject, hardcoded in the global `~/.claude/gsd-core/workflows/ship.md` (no config knob —
  grepped). With D-02 that commit is **rejected** and ship prints its warning. The procedure
  is a **documented manual step**: `docs/HOW_TO_DEVELOP.md` §6 gains one line — after
  `/gsd-ship N`, commit `.planning/STATE.md` as `docs(NN): ship phase N — PR #M` (no token)
  and push. Cost: one extra ~3 min pipeline per ship. Rejected: a wrapping project skill
  (one more thing tracking gsd-core changes); keeping the ship note local-only. The global
  workflow file is not patched (lost on update, invisible to the repo).
- **D-05:** **`make pr.land PR=N` is the only sanctioned merge path**; HOW_TO_DEVELOP §8
  points at it instead of the GitHub button. In order it: (1) resolves the PR's current head
  sha; (2) **refuses if the branch is behind `main`** (`behind_by > 0` → rebase, push, let CI
  run on the real tree, retry) — this reproduces the "require branches to be up to date"
  protection the free plan lacks, and is what makes step 5 sound; (3) **requires exactly the
  named jobs** to exist and be `success` for that head sha — after D-09: `test (3.12)`,
  `vendor-bundle`, `image`; a missing job is a refusal, zero checks is a refusal; the list
  lives next to `ci.yml` and changes in the same commit; (4) `gh pr merge --squash`;
  (5) **polls (~60 s) until a workflow run exists whose head sha is the squash commit, prints
  its URL, exits non-zero if none appears** (the token leak is back). It does **not** wait for
  that run to finish: with (2) the merged tree is byte-identical to the green PR head's tree
  (observed: `bfc9110` and `2c4b544` share tree `6ebbeaa2…`). A tool, not a wall — the web
  button still works; a wall needs branch protection (D-06).
- **D-06:** Rejected for this phase: making the repo public (unlocks branch protection +
  required checks + unlimited minutes — a visibility decision about the code and docs, not a
  CI one; deferred), GitHub Pro (money, not code; deferred), doc rule only (it is the rule
  PR #2 broke).
- **D-07:** The STATE.md blocker "CI workflow unverified" is **retired in this phase**, citing
  the evidence that already exists: main push run
  <https://github.com/halfb00t/spur/actions/runs/35963114939> (`59f02c3`, 2026-09-24 —
  `test (3.10)`, `test (3.12)`, `vendor-bundle`, `image` all success) and PR #3 head run
  <https://github.com/halfb00t/spur/actions/runs/36088409707> (`2c4b544`, tree-identical to
  `main` HEAD `bfc9110`). Phase 5's own squash-commit run URL is printed by `make pr.land` at
  merge and recorded on the next STATE.md touch — **not** by a docs-only commit on `main`
  (one phase = one PR = one squash commit). Stale claims corrected in the same change:
  `.planning/codebase/CONCERNS.md` L221 ("never executed"),
  `.planning/codebase/INTEGRATIONS.md` CI section, `README.md` L207, REQUIREMENTS.md
  REQ-ci-verified ("both supported Python versions").
- **D-08:** Two decision-log entries, **appended, dated, never edited in place**: **L22 — the
  merge gate** (D-02…D-05), citing as trigger PR #2's red merge (run `35993984796` failed
  `test (3.10)`, merged five minutes later) and the two run-less squash commits `538d26f`,
  `bfc9110`; **L23 — Python 3.12 only** (D-09), superseding L01's floor. Numbering order is
  the planner's. — **Reversibility:** one-way — the log is append-only by policy.
- **D-09:** **spur supports Python 3.12 only.** `requires-python = ">=3.12,<3.13"`, ruff
  `target-version = "py312"`, mypy `python_version = "3.12"` unchanged (its comment keeps
  the numpy-stub reason and drops the "floor checked by execution" paragraph), CI matrix
  `["3.12"]`, Makefile's interpreter loop and its error message narrowed to `python3.12`,
  README "Python 3.10+" → 3.12, L01 superseded on the floor by L23 (ceiling reasoning
  stands). Rejected: 3.11–3.12 (keeps the gap); 3.10 in the pre-commit hook. —
  **Reversibility:** costly — widening back is a one-line matrix change plus a new log
  entry, but any 3.12-only stdlib or syntax adopted meanwhile must be unwound.
- **D-10:** The ROADMAP Phase 5 goal and success criteria are rewritten **now, before
  planning**, via `/gsd-phase --edit 5`, to the reframed text. The planner and verifier
  must work from true criteria; "fix it at phase completion" was rejected.
- **D-11:** The skip-token debt file is resolved **in the fix commit** (D-02 + D-03):
  `Status: resolved`, sha, `git mv` into `docs/tech_debt/resolved/`, INDEX row moved —
  citing the hook's test and the PR-head run as evidence; `pr.land`'s post-merge check
  (D-05 step 5) is the standing verification the file's "Next step" asks for. "Resolve
  after the merge is observed" was rejected (a follow-up commit on `main`).

### Claude's Discretion

- Hook install mechanics: `default_install_hook_types: [pre-commit, commit-msg]` in
  `.pre-commit-config.yaml` so the documented `pre-commit install` installs both stages;
  check the README/HOW_TO_DEVELOP install line still holds.
- Hook implementation (language, location) and its test — the repo has no `scripts/` dir;
  `docker/smoke.py` is the only script outside `src/`. Anything Python must join
  `make typecheck`'s `src tests docker bench` list and ruff's scope.
- `pr.land` implementation: shell in the Makefile (next to `worktree.land`, whose lock/trap
  idiom is the local precedent) vs a Python module. The live GitHub API has no offline test;
  keep the decision logic (job-set check, behind check, run-appeared check) a pure function
  tested against recorded `gh` JSON, and the network shell thin.
- Fold §8's local follow-up (`git switch main && git pull --ff-only && git branch -D …`) into
  `pr.land`.
- Keep the one-entry matrix (job stays `test (3.12)`; widening is one line) vs a bare `test`
  job — either way `pr.land`'s list matches.
- Whether `make check` asserts the repo squash setting (probably not — a `gh api` read makes
  the gate need network and auth).
- L22/L23 numbering order; wording of the HOW_TO_DEVELOP edits (the doc is in Russian — keep
  its language).

### Deferred Ideas (OUT OF SCOPE)

- **Branch protection / required checks** — the only true wall; needs the repo public or
  GitHub Pro. A visibility/money decision the human makes outside this phase. If either
  happens, the required checks are the `pr.land` job set and "require branches to be up to
  date" — D-05 is then redundant, not wrong.
- **Actions minutes on a private free plan** (2,000 min/month): ~7–9 job-minutes per run
  today; not measured (billing API needs the `user` scope). Watch if runs multiply.
- **Stale remote branches** `origin/gsd/phase-03-…`, `origin/gsd/phase-04-…`,
  `origin/review-fixes-2026-09-21` — housekeeping, not this phase.
- **`make check` asserting the repository's squash setting** — would put a network call in
  the gate; not now.
- **A local 3.10 floor run** — moot after D-09; recorded only so the option is not
  re-derived.

None of these came from the user as scope requests — discussion stayed within the phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-ci-verified | `.github/workflows/ci.yml` is observed executing green in GitHub Actions on the supported Python version(s) — not hand-verified step-by-step. Retires the "CI workflow unverified" blocker. | The blocker's premise is falsified (13 runs exist; see Summary and D-07's cited run URLs, both re-confirmed live this session — see `## Verified Live State`). What remains for REQ-ci-verified to be *true going forward* rather than true-once is D-02–D-05: a structural guarantee that every future `main` commit has a run, which is what `## Architecture Patterns` and `## Code Examples` below design. `## Package Legitimacy Audit` confirms no new external dependency is needed to build it. |
</phase_requirements>

## Summary

The roadmap's stated premise for this phase — "the CI workflow has never executed" — is
false and was corrected in `05-CONTEXT.md`. Re-verified live in this research session
(`## Verified Live State` below): 13 completed workflow runs exist, the most recent `main`
push (`59f02c3`, run `35963114939`) is green on all four jobs, and PR #3's head (`2c4b544`,
run `36088409707`) is also green on all four. `REQ-ci-verified`'s literal acceptance text
("a run URL, on a real push, showing the gate and both container checks green") is already
satisfied by evidence that predates this research.

What the runs *reveal*, and what this phase must actually build, is that the merge gate has
two structural holes, both observed on `main`'s own last two merges: (1) a GitHub Actions
skip token — five bracket forms plus a `skip-checks` trailer — silently suppresses a run
when it appears **anywhere** in a commit message, including prose (`6fce500`'s "No
`[ci skip]` on purpose" note skipped CI on its own mention), and GitHub's default
squash-merge message (`COMMIT_OR_PR_TITLE`/`COMMIT_MESSAGES`) concatenates every branch
commit subject into the squash commit, so a token anywhere on the branch rides onto `main`
(confirmed live: `main`'s current HEAD `bfc9110` has zero workflow runs against it — see
below); (2) nothing stops a human or tool from clicking "merge" on a PR with a red or absent
check — PR #2 was merged five minutes after `test (3.10)` failed on run `35993984796`.
Closing both holes is a commit-time hook (rejects the token before it can be written) plus a
CLI-based merge path (`make pr.land`) that refuses to squash-merge unless every required job
is green for the PR's current head sha and the branch is not behind `main`.

A third, independent finding forces itself in: the reason `test (3.10)` failed on the Phase 3
branch was a real Python-version gap — `logging.StreamHandler[TextIO]` (a 3.11+-only
generic-subscript construct) reached `main` and was unimportable on 3.10, undetected by mypy
(pinned to `python_version = "3.12"` for numpy's stub syntax) or by ruff (syntax-only
`target-version = "py310"`) — the floor was checked by CI execution alone, and CI execution
is exactly the thing this phase's own holes let slip past review. Narrowing to Python 3.12
only (D-09) removes the only place the 3.10 floor was actually exercised, closing the gap
structurally rather than hoping the CI leg catches the next one.

**Primary recommendation:** Build the commit-msg hook as a `language: system`
`repo: local` entry in `.pre-commit-config.yaml` (bash/grep, matching the existing
`no-fake-done` idiom — no new mypy-strict surface, no new dependency), patch the two squash
settings with one `gh api -X PATCH`, and implement `make pr.land`'s decision logic (job-set
check, behind-check, run-appeared check) as small pure Python functions under a new
top-level `scripts/` (or similarly-scoped) directory, tested with recorded `gh` JSON exactly
the way `bench/memory.py`'s `_is_capped` is tested by `tests/test_bench.py` — importable
without installation via `.venv/bin/python -m pytest`, the same mechanism `bench` already
uses. Keep the network calls (`gh api`, `gh pr merge`) in a thin Makefile/shell shell around
that pure core.

## Verified Live State

All of the following were captured live via `gh api`/`gh` this session (2026-09-25,
`gh version 2.101.0`, authenticated as `halfb00t`, scopes `repo`, `workflow`):

**Repo merge settings** — `gh api repos/halfb00t/spur`:
```json
{"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true,
 "default_branch":"main","delete_branch_on_merge":true,
 "squash_merge_commit_message":"COMMIT_MESSAGES","squash_merge_commit_title":"COMMIT_OR_PR_TITLE"}
```
`squash_merge_commit_title`/`squash_merge_commit_message` match 05-CONTEXT.md's recorded
"today" values exactly — D-03's PATCH target is still correct. **`delete_branch_on_merge` is
now `true`**, not `false` as 05-CONTEXT.md's `<code_context>` recorded earlier the same day
(`updated_at` on the repo object reads `2026-09-25T03:49:03Z`, ~30 minutes before this
research ran). This is a live discrepancy against CONTEXT.md, not a research error — flagged
in `## Open Questions` below because it changes what `pr.land`'s local-branch-cleanup step
needs to do (GitHub will now delete the *remote* branch itself on merge; `gh pr merge
--delete-branch` may then be a no-op or error against an already-gone ref, and `pr.land`
still owns the *local* branch switch/delete regardless).

**`main`'s current HEAD has no run** — `gh api "repos/halfb00t/spur/actions/runs?head_sha=8fa2ad77ad0bcdb8e519cbec289a3601faf95f83"` (the STATE.md-context commit, itself downstream of the un-run squash `bfc9110`) → `{"total_count":0,...}`. Confirms 05-CONTEXT.md's claim that `bfc9110` carries no run, live.

**PR #3's head run, all four jobs, exact names** — `gh api repos/halfb00t/spur/actions/runs/35963114939/jobs`:
```json
{"conclusion":"success","name":"image","status":"completed"}
{"conclusion":"success","name":"test (3.10)","status":"completed"}
{"conclusion":"success","name":"vendor-bundle","status":"completed"}
{"conclusion":"success","name":"test (3.12)","status":"completed"}
```
This is the literal string set `pr.land` must check membership against (minus `test (3.10)`
after D-09 lands).

**`gh pr view 2 --json headRefOid,statusCheckRollup,mergeStateStatus,state`** (PR #2, merged
five minutes after its last real run failed):
```json
{"headRefOid":"20b63e453a3cd0c72e5d0f995a107a238c652a90","mergeStateStatus":"UNKNOWN",
 "state":"MERGED","statusCheckRollup":[]}
```
Empty `statusCheckRollup` confirms the skip-token-on-PR-head claim: GitHub recorded *zero*
checks for that head sha, not a failed one — the token suppressed the run entirely, it did
not just fail it.

**`gh pr view 3` — the shape a healthy rollup has** (for `pr.land`'s job-membership check):
```json
{"statusCheckRollup":[
  {"name":"test (3.10)","conclusion":"SUCCESS","status":"COMPLETED","workflowName":"ci"},
  {"name":"test (3.12)","conclusion":"SUCCESS","status":"COMPLETED","workflowName":"ci"},
  {"name":"vendor-bundle","conclusion":"SUCCESS","status":"COMPLETED","workflowName":"ci"},
  {"name":"image","conclusion":"SUCCESS","status":"COMPLETED","workflowName":"ci"}]}
```
Note the GraphQL-derived `statusCheckRollup` shape (`conclusion: SUCCESS`, uppercase) differs
from the REST jobs-endpoint shape above (`conclusion: success`, lowercase) — a pure decision
function must pick one source and not assume the other's casing. Recommendation: source the
job-membership/conclusion check from the REST `actions/runs?head_sha=`/`.../jobs` endpoints
(lowercase `conclusion`, matches D-05's own wording "requires exactly the named jobs to
exist and be `success`"), and use `gh pr view --json headRefOid` only to resolve the current
head sha, not to read check state.

**`compare/main...<sha>` shape** — `gh api repos/halfb00t/spur/compare/main...HEAD`:
```json
{"ahead_by":0,"behind_by":0,"status":"identical"}
```
`behind_by` is the field D-05 step 2 gates on (`behind_by > 0` → refuse).

**Only one workflow exists** — `gh api repos/halfb00t/spur/actions/workflows` →
`{"id":363331628,"name":"ci","path":".github/workflows/ci.yml"}`. The unfiltered
`actions/runs?head_sha=` endpoint is safe to use as-is; there is no second workflow whose
runs could be confused with `ci.yml`'s.

**`gh pr merge --help`** (this installed version, 2.101.0) — confirms `--squash`,
`--delete-branch`, `--match-head-commit SHA`, `-t`/`-b` (subject/body override) all exist as
flags. `--match-head-commit` is present, so `pr.land` can pass the sha it already resolved
in step 1 to guard against a TOCTOU race between the check and the merge (a PR getting a new
push between steps 1–4).

## Architectural Responsibility Map

This phase is infrastructure/tooling, not the layered web app `spur` itself — the standard
Browser/Frontend/API/CDN/DB tiers do not apply cleanly. Adapted tiers for this phase:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Skip-token rejection | Local dev tooling (git `commit-msg` hook, `pre-commit`) | — | Must fire before a commit object exists at all — the only point that covers every tool (human, `gsd-ship`, any CLI) that commits to this repo, per D-02's own reasoning. |
| Squash-message shape | GitHub repository settings (not in git) | Documented manual step (`docs/HOW_TO_DEVELOP.md`) | A `gh api -X PATCH` setting with no git representation; the doc is the only record, per D-03. |
| Red/behind-branch merge refusal | Local dev tooling (`make pr.land`, `gh` CLI) | GitHub Actions (source of the check data) | The decision logic runs locally against data GitHub's REST/GraphQL API supplies; GitHub itself enforces nothing here (no branch protection available, D-06). |
| Green-run evidence | GitHub Actions (CI) | `make pr.land`'s post-merge poll | CI produces the run; `pr.land` only observes and reports it. |
| Python-version floor | Local dev tooling (`Makefile`, `pyproject.toml`) + CI matrix | — | Enforced by what interpreters `make venv` will pick and what mypy/ruff/CI check against; no runtime-tier component. |

## Project Constraints (from CLAUDE.md)

- **`make verify` is the gate** — ruff, mypy `--strict`, import-boundary contracts,
  unfinished-work scan, pytest. Any new Python file this phase adds (the hook, if Python;
  `pr.land`'s decision module) must pass under `--strict` with `disallow_any_explicit` on
  (L21) and must be added to `make typecheck`'s directory list (`src tests docker bench`,
  currently) or it silently escapes the gate.
- **A number the tool prints is a number someone will cut metal to (L08)** — not directly
  in scope for this phase (no geometry numbers), but the same epistemics apply to `pr.land`:
  it must never report "merged" or "run appeared" on a guess; a poll timeout is a non-zero
  exit and a printed reason, never a silent success.
- **A parameter the user did not set must never silently change the part (L05)** — not
  applicable to this phase's surface (no `GearParams` involved).
- **Simplest solution that actually works; surgical edits; one concern per commit.** The
  hook implementation and `pr.land` are two genuinely separate concerns (D-02/D-03 vs D-05)
  and should very likely land as separate commits even within one phase branch, per "one
  logical unit of work" — the planner should treat them as separate plans/waves rather than
  one mega-commit.
- **New behavior ships with its tests in the same change.** D-02 explicitly requires a test
  for the hook; the Claude's-discretion note explicitly requires `pr.land`'s decision logic
  be a pure function "tested against recorded `gh` JSON" — both are hard requirements, not
  nice-to-haves.
- **Capturing debt (D-11).** The skip-token debt file's resolution (`Status: resolved`,
  `git mv`, INDEX row) must land in the *same commit* as the hook + setting fix, per
  CLAUDE.md's "Capturing ideas and debt" section and D-11's own text.
- **Decisions are append-only (D-08).** L22/L23 are new entries; L01 is not edited, only
  superseded by pointer, matching the L06→L18, L07→L17, L14→L21 precedents already in the
  log (`docs/architecture/decision_log.md`, read in full this session).
- **English throughout** — `docs/HOW_TO_DEVELOP.md` is the one documented exception (it is
  written in Russian by established convention); D-08/discretion notes say keep its
  language when editing §6/§8.

## Standard Stack

No new external dependency is needed for this phase (see `## Package Legitimacy Audit`).
The relevant tools are already present in this environment; versions confirmed live this
session:

| Tool | Verified version | Purpose | Source |
|------|------|---------|--------|
| `pre-commit` | 4.6.2 (`.venv/bin/pre-commit --version`) | Hosts the new `commit-msg` hook alongside the existing `verify` hook | [VERIFIED: `.venv/bin/pre-commit --version` output this session] |
| `gh` (GitHub CLI) | 2.101.0 (`gh --version`) | `pr.land`'s network shell: `gh api`, `gh pr view`, `gh pr merge` | [VERIFIED: `gh --version` output this session] |
| Python | 3.12 only, after D-09 | The one supported interpreter; `requires-python = ">=3.12,<3.13"` | [VERIFIED: `pyproject.toml:10` read this session, current value `">=3.10"`, D-09 is the change] |

**`gh pr merge` flags confirmed present on this installed version** (`gh pr merge --help`,
this session): `-s/--squash`, `-d/--delete-branch`, `--match-head-commit SHA`,
`-t/--subject`, `-b/--body`. [VERIFIED: `gh pr merge --help` output this session]

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bash/grep `commit-msg` hook (`language: system`) | A small Python script under a new dir | Python gains mypy-strict type safety but adds a directory to `make typecheck`'s scope and to the module set the CAD-kernel import-boundary contracts must not accidentally reach; a 6-token grep is well within bash's competence and matches the existing `no-fake-done` idiom exactly (same file, same tone). Recommend bash unless the hook grows real logic. |
| Makefile shell target for `pr.land`'s network shell + a pure Python decision module | Pure-Python `pr.land` end to end (network calls via `subprocess.run(["gh", ...])`) | A pure-Python implementation gets it under mypy strict end to end and is more testable at the seams (mock `subprocess.run`), at the cost of leaving the Makefile's existing shell idiom (`worktree.land`) inconsistent. Either is defensible; the *decision logic* (job-set/behind/run-appeared checks) should be pure and tested either way — that part is not discretionary per Claude's-discretion note. |
| `gh api -X PATCH` one-shot for the squash settings (D-03) | A script/Makefile target that re-applies the setting idempotently | D-03 explicitly wants one manual command recorded in the docs, not automation — the setting is not in git and re-applying it needs to stay a conscious act, not something `make verify` silently does. |

## Package Legitimacy Audit

**N/A — no new external packages are introduced by this phase.** `pre-commit` and `gh` are
already installed dev dependencies/tools (`pre-commit>=4` is already in
`pyproject.toml`'s `dev` extras, `gh` is a pre-authenticated host tool, not a project
dependency). If the planner chooses a Python implementation for the hook or `pr.land`, no
new PyPI package is required — `subprocess`/`json`/`re`/`sys` from the standard library
cover every need identified in this research (grep-equivalent matching, JSON parsing of
`gh` output, process invocation).

## Architecture Patterns

### System Flow Diagram

```
 developer / gsd-ship            commit-msg hook              GitHub
 writes a commit  ───────────►  grep message file  ──reject──►  (commit never created)
      │                          for 6 skip tokens
      │                          (case-insensitive,
      │                           subject + body)
      │  passes
      ▼
 git commit succeeds  ───push──►  branch on GitHub  ──triggers──► ci.yml
                                                                    │ test(3.12), vendor-bundle, image
                                                                    ▼
                                                              workflow run, jobs
                                                                    │
                       make pr.land PR=N                            │
                       ┌──────────────────────────────────────────┘
                       │ 1. gh pr view --json headRefOid  (resolve head sha)
                       │ 2. gh api compare/main...<sha>   (behind_by > 0 ? refuse)
                       │ 3. gh api actions/runs?head_sha=<sha> + .../jobs
                       │    (every named job present AND conclusion=success ? else refuse)
                       ▼
                 gh pr merge --squash --match-head-commit <sha>
                       │  (repo squash settings: PR_TITLE / PR_BODY, D-03)
                       ▼
                 squash commit lands on main  ──triggers──► ci.yml (push event)
                       │
                       ▼
                 5. poll actions/runs?head_sha=<squash-sha> (~60s)
                    run appears ? print URL, exit 0 : exit non-zero
                       │
                       ▼
                 git switch main; git pull --ff-only; git branch -D <phase-branch>
```

### Recommended Project Structure (additions only)

```
.pre-commit-config.yaml   # + one new "commit-msg" hook entry (D-02)
scripts/                  # new — the only home for pr.land's pure decision logic;
├── pr_land.py            #   mirrors bench/'s "importable without installation" pattern
└── (commit_msg check)    #   OR keep the hook as inline bash; see Alternatives Considered
tests/
└── test_pr_land.py       # pure-function tests against recorded gh JSON (no network)
docs/tech_debt/resolved/
└── 2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md   # git mv'd here (D-11)
```

### Pattern 1: Local `repo: local` hook at a new git-hook stage

**What:** Add a second hook entry to the existing single-repo `.pre-commit-config.yaml`,
this one scoped to `stages: [commit-msg]`, alongside the existing `verify` entry (which
defaults to the `pre-commit` stage and uses `pass_filenames: false`).
**When to use:** Any check that must inspect the commit message itself, not the changed
files.
**Verified mechanics this session:**
- A `commit-msg`-stage hook is invoked by git with **one positional argument: the path to a
  temp file containing the message being validated** — this is git's own `commit-msg` hook
  contract, and `pass_filenames` does not suppress it (that flag governs *changed-file*
  arguments for the `pre-commit` stage; the message-file argument for `commit-msg` is
  separate and always passed). [CITED: pre-commit.com docs, fetched this session]
- `default_install_hook_types: [pre-commit, commit-msg]` at the top level of
  `.pre-commit-config.yaml` makes the *already-documented* `pre-commit install` command
  (comment at `.pre-commit-config.yaml:5`, "Install once per clone") install **both** git
  hook types with no change to that documented command. [CITED: pre-commit.com docs, fetched
  this session]
- A known footgun (GitHub issue #3120, read directly via `gh api` this session, not just a
  summary) turned out to be **not** a pre-commit limitation but a user configuration error:
  the reporter's local hook lived inside a *nested* nested repo-local-referencing-itself
  config and only had `stages: [commit-msg]` set on the *inner* hook without
  `default_install_hook_types` covering `commit-msg` at the top level actually in use. A
  flat, single `.pre-commit-config.yaml` (this repo's exact shape) with the stage and
  `default_install_hook_types` both set at top level is the maintainer-confirmed-working
  shape (a minimal reproduction posted in the same thread by another user demonstrates it
  working). [VERIFIED: `gh api repos/pre-commit/pre-commit/issues/3120/comments` read in
  full this session — this repo's own config, read this session
  (`.pre-commit-config.yaml`), already matches the working flat shape, not the broken nested
  one]

```yaml
# Source: .pre-commit-config.yaml (this repo, read this session) + pre-commit.com docs
repos:
  - repo: local
    hooks:
      - id: verify
        name: make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest)
        entry: make verify
        language: system
        pass_filenames: false
        always_run: true
      - id: no-skip-token
        name: reject GitHub Actions skip tokens in the commit message
        entry: scripts/reject-skip-tokens.sh   # or an inline grep; see Code Examples
        language: system
        stages: [commit-msg]
        # no pass_filenames: false here -- the message-file path IS the argument this
        # hook needs; suppressing it would break the check.
```

### Pattern 2: Pure decision core, thin network shell (`pr.land`)

**What:** Separate "what does this JSON mean" (pure functions, no I/O) from "go get the
JSON" (`gh api`/`gh pr view`/`gh pr merge` calls). This repo already has exactly this shape
in `bench/memory.py`'s `_is_capped` (a pure predicate) versus `sweep()` (the I/O-heavy
orchestrator that calls it) — `_is_capped` is unit-tested with literal numbers in
`tests/test_bench.py`, no Docker daemon needed. [VERIFIED: `bench/memory.py:73-79`,
`tests/test_bench.py:1-30` read this session — `_is_capped(peak_bytes: int, ceiling_bytes:
int) -> bool: return peak_bytes >= ceiling_bytes * (1 - _CAP_TOLERANCE_FRACTION)`]
**When to use:** Any Makefile target that must make a go/no-go call against live external
state but whose *logic* should be testable offline.
**Why this matters here:** "The live GitHub API has no offline test" (Claude's discretion
note) is exactly the constraint `bench/memory.py` already solved for Docker-dependent
memory sweeps — same shape, different external system.

```python
# Source: modeled on bench/memory.py's _is_capped / tests/test_bench.py pattern,
# read this session. Shapes below are the real REST/GraphQL fields, confirmed live
# (see "## Verified Live State").
from __future__ import annotations

REQUIRED_JOBS = frozenset({"test (3.12)", "vendor-bundle", "image"})  # D-05, post-D-09

def jobs_are_green(jobs: list[dict[str, str]]) -> bool:
    """`jobs` is the REST `.../actions/runs/<id>/jobs` response's `jobs` array
    (field names `name`, `conclusion` -- confirmed live this session). True only
    when every job in REQUIRED_JOBS is present with conclusion == "success";
    a missing job or a non-"success" conclusion is a refusal (D-05 step 3)."""
    by_name = {j["name"]: j["conclusion"] for j in jobs}
    return REQUIRED_JOBS <= by_name.keys() and all(
        by_name[name] == "success" for name in REQUIRED_JOBS
    )

def branch_is_current(compare: dict[str, object]) -> bool:
    """`compare` is `repos/.../compare/main...<sha>`'s response (`behind_by` field,
    confirmed live this session). D-05 step 2: refuse if behind main."""
    return compare["behind_by"] == 0
```

```python
# tests/test_pr_land.py -- no network, mirrors tests/test_bench.py's inline-literal style
from scripts.pr_land import jobs_are_green, branch_is_current

def test_all_three_named_jobs_green_passes() -> None:
    jobs = [
        {"name": "test (3.12)", "conclusion": "success"},
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    assert jobs_are_green(jobs)

def test_a_missing_job_refuses() -> None:
    # PR #2's own recorded shape this session: statusCheckRollup == [] --
    # zero jobs at all, not one failing -- must refuse the same as a red job.
    assert not jobs_are_green([])

def test_one_red_job_refuses() -> None:
    jobs = [
        {"name": "test (3.12)", "conclusion": "failure"},  # run 35993984796's shape
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    assert not jobs_are_green(jobs)

def test_branch_up_to_date() -> None:
    # repos/halfb00t/spur/compare/main...HEAD, captured live this session
    assert branch_is_current({"ahead_by": 0, "behind_by": 0, "status": "identical"})

def test_branch_behind_refuses() -> None:
    assert not branch_is_current({"ahead_by": 0, "behind_by": 3, "status": "behind"})
```

### Anti-Patterns to Avoid

- **Reading `gh pr view`'s `statusCheckRollup` for the merge-gate check instead of the REST
  jobs endpoint.** Confirmed live this session: the two shapes differ in field name
  (`conclusion` present in both, but GraphQL's is uppercase `"SUCCESS"`, REST's is lowercase
  `"success"`) and in what's included (`statusCheckRollup` can include check-suite-level
  rollups, not just per-job names). Pick one source of truth and match D-05's own wording
  ("the named jobs... `success`", lowercase) — that's the REST endpoint.
- **Calling `gh pr merge` without `--match-head-commit`.** Between `pr.land`'s job-set check
  (step 3) and the actual merge (step 4) there is a TOCTOU window — a new push to the PR
  branch in that window would mean the merge commits a tree that was never actually checked.
  `--match-head-commit <sha-resolved-in-step-1>` closes this; confirmed present on the
  installed `gh` version this session.
- **Waiting for the post-merge run to *finish* (D-05 explicitly rejects this).** The design
  only waits for the run to *appear*, because step 2's behind-check already proves the
  merged tree is byte-identical to the just-checked, already-green PR head tree (observed:
  `bfc9110`/`2c4b544` share tree `6ebbeaa2…`, per 05-CONTEXT.md). Waiting for completion
  would double the wall-clock cost of every merge (~3 min per the file's own measurement)
  for no additional certainty.
- **Assuming `gh pr merge --delete-branch` also cleans up the local checkout.** It does not
  address the *local* branch at all, and per this session's confirmation that
  `delete_branch_on_merge` is now `true` on the repo, GitHub will delete the *remote* branch
  itself on merge — `--delete-branch` may then race or no-op against an already-deleted ref.
  `pr.land` must still explicitly `git switch main && git pull --ff-only && git branch -D
  <branch>` for the *local* clone regardless of what flag (if any) is passed to `gh pr
  merge`, exactly as the discretion note asks to fold in. Test this interaction directly at
  execution time rather than assuming a documented behavior — the docs (`cli.github.com`)
  did not specify it precisely this session (see Open Questions).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting whether a PR's checks are green | A custom "poll the workflow run until green" loop reimplementing GitHub's own rollup logic | `gh api actions/runs?head_sha=<sha>` + `.../jobs`, filtered to the named job set (D-05's own design) | GitHub's rollup already exists in two forms (REST jobs, GraphQL `statusCheckRollup`); reinventing "what does success mean" risks diverging from what the merge button itself would show a human. |
| Enforcing "branch must be up to date with main" | A hand-rolled `git merge-base` diff count | `gh api repos/.../compare/main...<sha>`'s `behind_by` field (confirmed live this session) | This is literally what GitHub's own "require branches to be up to date" branch-protection rule uses internally; recomputing it locally with raw git risks a different answer if the local clone's `main` ref is stale (the compare call always reads the server's true `main`). |
| Squash-commit message shaping | A script that rewrites the squash message client-side after merge | Repository settings `squash_merge_commit_title=PR_TITLE`, `squash_merge_commit_message=PR_BODY` (D-03) applied once via `gh api -X PATCH` | GitHub already computes this correctly server-side once configured; a client-side rewrite would need a second commit (`git commit --amend` + force-push to `main`, forbidden) to fix a message after the fact. |

**Key insight:** every piece of this phase's "merge gate" is data GitHub's API already
computes (job conclusions, ahead/behind, squash message composition) — the phase's actual
work is *reading that data correctly and refusing to proceed on the wrong answer*, not
computing any of it independently. The failure mode this research found twice
(PR #2's silent-zero-checks head, and `main`'s two run-less squash commits) was never "CI
lied" — it was "nobody looked before merging."

## Common Pitfalls

### Pitfall 1: Trusting `gh pr merge`'s default behavior without `--squash --subject/--body` explicitly matching the intended settings

**What goes wrong:** If a future `gh` default ever changes, or if someone runs `gh pr merge`
by hand without `-s`, the squash message could silently diverge from the D-03 settings.
**Why it happens:** `gh pr merge` with `-s` and no `-t`/`-b` honors the *repository's*
squash-message settings — confirmed via web search this session, not the official `gh`
manual page (which did not state this explicitly when fetched) — so the settings PATCH
(D-03) is necessary but the *behavior* it changes is unverified in `gh`'s own docs.
**How to avoid:** `pr.land` should call `gh pr merge --squash` with **no** `-t`/`-b`
override, so the repo setting is what actually fires, and the plan should include an
execution-time smoke check (merge one real PR, read the resulting commit body, confirm it
matches the PR body not the commit-subject list) rather than trusting the documentation.
**Warning signs:** A squash commit on `main` whose body is a commit-subject list again after
D-03 supposedly landed.

### Pitfall 2: A commit-msg hook that only checks the subject line, not the body

**What goes wrong:** `6fce500`'s prose mention of `[ci skip]` was in the *body*, not the
subject, and still suppressed the run — a hook that only greps the first line of the message
file would miss exactly this case, which is the case that actually happened in this repo.
**Why it happens:** Many commit-msg hook examples online only validate subject-line
conventions (Conventional Commits format checkers, for instance) and readers copy that
narrower pattern by habit.
**How to avoid:** grep/scan the **entire** message file content, not just its first line.
**Warning signs:** A test suite for the hook that only feeds single-line messages — the test
matrix must include a multi-line message with the token buried in a later paragraph (matching
`6fce500`'s actual shape).

### Pitfall 3: `skip-checks:true` vs `skip-checks: true` — both must match, and the trailer's own formatting rule is easy to get wrong in a same-session test fixture

**What goes wrong:** GitHub's docs state the trailer must be "preceded by two empty lines"
and be the last trailer if others exist; a naive grep for the literal string `skip-checks`
anywhere still catches the intent even if the *trailer itself* is malformed and wouldn't
actually trigger the skip in GitHub's eyes — meaning the hook can be **stricter** than
GitHub, which is safe, but a test that insists the hook matches GitHub's trailer-formatting
pedantry exactly would be testing the wrong thing.
**Why it happens:** Over-precisely mirroring GitHub's trailer syntax in the hook's own
regex risks a hook that fails to reject a message GitHub *would* have skipped, if the
message's whitespace doesn't exactly match what GitHub expects.
**How to avoid:** Match the six tokens as **substrings**, case-insensitively, anywhere in
the message (D-02's own stated design) — this is deliberately broader than GitHub's own
exact trigger conditions, which is the safe direction for a gate to err in.
**Warning signs:** A hook regex anchored to line start/end or requiring exact blank-line
spacing before `skip-checks:` — that's precision in the wrong direction for a rejection gate.

### Pitfall 4: Python-version-floor gaps that only CI execution catches, reappearing after D-09

**What goes wrong:** The concrete incident this phase is partly responding to
(`logging.StreamHandler[TextIO]`, 3.11+-only, reached `main` because mypy is pinned to 3.12
and ruff is syntax-only) is *closed* by D-09 (mypy's version now equals the only supported
runtime), but any **future** decision to widen the supported range again would silently
reopen exactly this gap unless a real interpreter at the new floor re-enters CI or local
testing.
**Why it happens:** mypy's `python_version` and the runtime floor are two independent knobs
that happened to diverge once already (`docs/architecture/decision_log.md`'s L14, read this
session, already documents "the floor is checked by execution, not by the type checker's
opinion" as a known, accepted gap at the time it was written).
**How to avoid:** if a future phase widens `requires-python` again, treat re-introducing a
real-interpreter CI leg (not just a version bump in one file) as part of that same change,
not a follow-up.
**Warning signs:** `requires-python`'s lower bound and the CI matrix's minimum version
diverging again without a corresponding decision-log entry explaining why the gap is closed
some other way.

## Code Examples

### Skip-token grep (bash, matching the `no-fake-done` idiom read this session)

```bash
#!/usr/bin/env bash
# Source: modeled on Makefile's no-fake-done target (read this session,
# Makefile:61-66) -- same tone, same "git grep"-style pattern-and-refuse shape,
# applied to a commit message file instead of tracked source.
set -euo pipefail
MSG_FILE="$1"
# Six tokens GitHub Actions honours (docs.github.com, fetched this session):
# [skip ci] [ci skip] [no ci] [skip actions] [actions skip], plus the skip-checks
# trailer. Matched as substrings, case-insensitive, across the WHOLE file --
# 6fce500 proved a prose mention in the body is enough to trigger it.
if grep -iE '\[(skip ci|ci skip|no ci|skip actions|actions skip)\]|skip-checks: ?true' \
     "$MSG_FILE"; then
  echo "make: this commit message carries a GitHub Actions skip token (shown above)."
  echo "      A skip token here silences CI on this commit AND rides into the next"
  echo "      squash-merge message -- see docs/tech_debt/resolved/"
  echo "      2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md."
  exit 1
fi
```

### The `gh api -X PATCH` for D-03 (docs only — do not apply from this research)

```bash
# Source: docs.github.com REST reference "Update a repository", fetched this
# session -- verbatim enum values (squash_merge_commit_title only has TWO valid
# values; squash_merge_commit_message has three):
gh api -X PATCH repos/halfb00t/spur \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `[skip ci]`/`[ci skip]` only | GitHub added `[no ci]`, `[skip actions]`, `[actions skip]`, and the `skip-checks:` trailer | Ongoing GitHub product surface, not a version-dated change (fetched live this session, no changelog date on the docs page) | The commit-msg hook must cover all six, not just the two everyone remembers — D-02 already specifies all six. |
| Required-status-check branch protection as the merge gate | For a private repo on a free plan, branch protection is unavailable (HTTP 403 "Upgrade to GitHub Pro or make this repository public" — confirmed live in 05-CONTEXT.md's own research, not re-verified this session since it would require a destructive/blocked call) | N/A — a plan-tier limitation, not a product change | Forces the CLI-tool approach (D-05) instead of a server-enforced wall — explicitly named "a tool, not a wall" throughout the CONTEXT. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub's skip-token matching is case-insensitive. | Pattern 1 / Pitfall 3 / D-02 | The official docs page (fetched verbatim this session) does **not** state this explicitly — it lists the five bracket strings and the trailer with no stated case rule. This claim traces to secondary/community sources (blog posts surfaced by web search), not the official page. The hook matching case-insensitively is safe regardless of whether GitHub itself is case-sensitive (worst case: the hook rejects a message GitHub would have actually run, a false-positive commit-msg retry — annoying, not merge-gate-defeating), so the design is not harmed if this assumption is wrong, but it should not be cited as a GitHub-confirmed fact in the decision log. |
| A2 | `gh pr merge --squash` with no `-t`/`-b` honors the repository's `squash_merge_commit_title`/`squash_merge_commit_message` settings rather than some `gh`-internal default. | Pitfall 1 / D-03 | Sourced from web search results describing this behavior, not the official `gh` CLI manual page (which, when fetched directly this session, did not state it). If false, D-03's `gh api -X PATCH` setting change would have no effect on `pr.land`'s actual merges, and the squash message would still carry whatever `gh`'s own default is. **Must be falsified at execution time**: the plan should verify this by performing (or having the human perform) one real `gh pr merge --squash` after the PATCH and reading the resulting commit body, before relying on it structurally. |
| A3 | `gh pr merge --delete-branch`'s exact interaction with a repo that already has `delete_branch_on_merge: true` server-side (no-op vs. error vs. redundant-but-harmless). | Anti-Patterns / Open Questions | The `gh` manual page did not specify this when fetched this session. Low risk either way since `pr.land`'s design (per discretion note) already does its own explicit local `git switch/pull/branch -D` regardless of what `gh` does server-side — but the plan should decide whether to pass `--delete-branch` to `gh pr merge` at all, or rely purely on the repo setting plus `pr.land`'s own local cleanup, and that decision should be tested against the real `gh` CLI at execution time (a live merge, not a dry run) rather than assumed. |

## Open Questions (RESOLVED)

1. **`delete_branch_on_merge` is `true` live, not `false` as 05-CONTEXT.md recorded ~30
   minutes earlier the same session.** — RESOLVED
   - What we know: confirmed live twice this session (`gh api repos/halfb00t/spur`, two
     separate calls, both returned `true`; `updated_at: 2026-09-25T03:49:03Z`).
     05-CONTEXT.md's `<code_context>` section states "today: ... `delete_branch_on_merge:
     false`" as part of its own live-verified findings, dated the same day.
   - What's unclear: whether the setting changed between the CONTEXT session and this
     research session (a GitHub default, or someone/something toggled it — this repo has no
     audit-log access on a free private plan to check), or whether CONTEXT.md's transcription
     was simply wrong at the time.
   - Recommendation: the planner should not treat this as blocking — `pr.land`'s design
     already does its own explicit local branch cleanup independent of this setting (per the
     discretion note) — but should note in the plan that `pr.land`'s Makefile target should
     not assume any particular value for this setting (don't special-case "if remote branch
     already gone" as an error condition; treat it as expected either way).
   - **RESOLVED** by `05-02-PLAN.md` (flagged assumption 7 and the must_haves truth on the
     local follow-up): `pr.land` never passes `--delete-branch` and never touches the remote
     branch; it deletes the local branch only when that branch's tip equals the merged head
     sha. It is correct whether the setting is `true` (re-read live during planning,
     2026-09-25) or `false`, so the value is not on its path.

2. **Exact `gh pr merge` non-mergeable-PR exit behavior (exit code, stderr text) was not
   confirmed against the actual CLI this session** — RESOLVED. Only the `--help` flag list was
   confirmed, not runtime behavior, since triggering an actual failed merge attempt against
   this real repo was avoided per the read-only-only instruction governing this research
   session.
   - What we know: `pr.land`'s own design (D-05) never *calls* `gh pr merge` unless steps
     1–3 already passed, so a non-mergeable-PR call to `gh pr merge` should be rare/never in
     the intended flow.
   - What's unclear: what `pr.land` should print/do if `gh pr merge` itself still fails
     for some reason not covered by steps 1–3 (e.g., a merge conflict introduced between the
     behind-check and the merge call — an even narrower TOCTOU window than the job-status one
     `--match-head-commit` closes).
   - Recommendation: the plan should have `pr.land` check `gh pr merge`'s own exit code and
     propagate it as a refusal (not swallow it), and the plan's own execution-verification
     step should include one real merge exercised end to end (this phase's own PR is the
     natural test subject, per D-05/D-07's own "Phase 5's own squash-commit run URL" language)
     rather than relying on documented behavior that could not be confirmed by reading alone.
   - **RESOLVED** by `05-02-PLAN.md` Task 1 (`land()` step 4): a non-zero `gh pr merge` exit
     is propagated, never swallowed — gh's stderr is printed with "check `gh pr view N`
     before retrying", the exit is 1, and there is no poll and no local follow-up (tested
     offline with a fake runner). `pr.land` depends on the exit status only, not on gh's
     stderr text, so the unconfirmed text does not matter. The one real merge end to end is
     this phase's own landing (`05-05-PLAN.md`, the after-phase steps). Since D-12 (the
     ruleset on `main`), GitHub's own refusal of a red or behind head reaches `pr.land`
     through the same path.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI, authenticated | `pr.land`'s network shell | ✓ | 2.101.0, scopes `repo`, `workflow`, `admin:org`, `gist` | — |
| `pre-commit` (in `.venv`) | The new `commit-msg` hook | ✓ | 4.6.2 | — |
| GitHub branch protection / required checks | Would be the "wall" alternative to `pr.land` | ✗ (HTTP 403 on a private free-plan repo, per 05-CONTEXT.md) | — | `make pr.land` (D-06) — already the chosen path, not a fallback needed at execution time |
| A second, non-3.12 Python interpreter on the dev machine | Would let `make test-image`-style local floor testing continue after D-09 | ✗ (only `.venv` 3.12.13 confirmed on this machine, per 05-CONTEXT.md; not independently re-checked this session) | — | `make test-image` (Docker, 3.12-slim-bookworm) already covers the one supported version; no fallback needed since 3.12 is the only floor after D-09 |

**Missing dependencies with no fallback:** none — branch protection's absence is the premise
D-05/D-06 already designed around, not a blocker discovered here.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8 (`pyproject.toml` dev extra `pytest>=8`, `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` — `testpaths = ["tests"]`, `addopts = "--strict-markers --strict-config"`, `xfail_strict = true`, `filterwarnings = ["error", ...]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_pr_land.py -q` (mirrors `tests/test_bench.py`'s own documented invocation, read this session) |
| Full suite command | `make verify` (includes `make test` → `$(PY) -m pytest $(PYTEST_ARGS)`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-ci-verified | Skip-token hook rejects all six token forms, case-insensitive, subject and body | unit | `.venv/bin/python -m pytest tests/test_no_skip_tokens.py -q` (or a bash-test harness if the hook stays pure bash — see below) | ❌ Wave 0 |
| REQ-ci-verified | `pr.land`'s decision logic (job-set check, behind check) refuses correctly on recorded red/missing/behind fixtures | unit | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | ❌ Wave 0 |
| REQ-ci-verified | `make pr.land PR=N` actually merges a real PR end to end and a run appears for the squash commit | manual/live (cannot be automated in `make verify` — needs network + a real merge) | executed once, live, as *this phase's own* PR merge (D-05/D-07's own design: Phase 5's squash-commit run URL is the evidence) | — (evidence is the run URL itself, not a test file) |
| REQ-ci-verified | `requires-python`, ruff `target-version`, mypy `python_version`, CI matrix, README, Makefile interpreter loop all agree on 3.12-only | smoke/consistency | `make verify` (mypy/ruff will fail if 3.12 syntax leaks under a stale `target-version`; the Makefile change is exercised by `make venv` itself failing/succeeding correctly) | Partially — no single automated cross-file consistency test exists today; consider a small test that greps `pyproject.toml` and `ci.yml` for the version string, matching the spirit of `tests/test_records.py`'s `test_calc_module_stays_log_free` regex-belt pattern (read via decision log L20's own description) | ❌ Wave 0, optional |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_pr_land.py tests/test_no_skip_tokens.py -q` (or equivalent, whatever the hook's test file ends up named) plus `make lint`/`make typecheck` if new Python files were added.
- **Per wave merge:** `make verify` (full suite, ~11 s warm per the repo's own documented figure).
- **Phase gate:** `make verify` green **and** one live end-to-end `make pr.land` execution against this phase's own PR, with the resulting run URL recorded in STATE.md per D-07's own design — this is the one success criterion this phase cannot fully satisfy without actually exercising the real tool against the real GitHub API.

### Wave 0 Gaps

- [ ] `tests/test_no_skip_tokens.py` (or a bash-harness equivalent) — covers the six-token
      hook, including the multi-line/body case (Pitfall 2) and the empty-rollup case
      (Pitfall — PR #2's own recorded shape).
- [ ] `tests/test_pr_land.py` — covers `jobs_are_green`/`branch_is_current`-shaped pure
      functions against the literal JSON shapes recorded in `## Verified Live State` above
      (all of it captured live this session, safe to use as fixture data verbatim).
- [ ] No new fixtures directory exists in `tests/` today (confirmed by `ls tests/` this
      session: only `test_*.py` + `conftest.py`) — inline literal dicts in the test file
      itself, matching `tests/test_bench.py`'s own style, is the established convention;
      don't introduce a `tests/fixtures/` directory as a first for this phase unless the
      JSON fixtures grow large enough to be unreadable inline.

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled. This
phase's surface is git/CI tooling, not the `spur` web application, so most ASVS categories
that govern the application (session management, the geometry input-validation contract)
do not apply here. The categories that do apply, narrowly:

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | `gh`'s own OAuth token (keyring-stored, scopes `repo`/`workflow`) is out of this phase's scope to manage; it's a pre-existing host credential, not something this phase creates or touches. |
| V3 Session Management | No | Not applicable — no user sessions involved. |
| V4 Access Control | No | GitHub's own repository permissions gate who can push/merge; this phase adds a *procedural* gate (structural, per D-01's own framing), not an access-control mechanism. |
| V5 Input Validation | Yes, narrowly | The commit-msg hook parses an untrusted-ish input (a commit message any contributor, human or AI tool, can write arbitrarily) — treat the message file's content as untrusted text for the grep/regex (no `eval`, no shell-interpolating the message content into a command, per `## code_seam` conventions elsewhere in this org's tooling). The bash example above reads the file path as `$1` and greps its *contents*, never interpolating message text into a shell string — this is the correct shape. |
| V6 Cryptography | No | No new cryptographic material; the `gh` token is host-managed, not generated or stored by this phase. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A crafted commit message attempting shell injection into the hook's own execution (e.g. a message body containing `` `$(rm -rf /)` `` or similar, if the hook ever echoed the message content back through an unquoted shell expansion) | Tampering | Read the message file's content only via `grep -f`-style file reads / quoted variable expansion, never `eval` or unquoted interpolation of message content into a command string — the bash example above passes `"$MSG_FILE"` as a quoted argument to `grep`, and never re-embeds the *content* of the message into a new command. |
| A malicious or compromised local tool bypassing the `commit-msg` hook entirely (`git commit --no-verify`) | Tampering / Repudiation | Out of scope for a local hook by design — `--no-verify` always bypasses local hooks; this is why D-05's server-observed evidence (a real run must *appear* for the squash commit) is the actual backstop, not the hook alone. The hook prevents accidents and habit, not a deliberately adversarial committer — consistent with this being a single-maintainer private repo, not a public trust boundary. |

## Sources

### Primary (HIGH confidence — verified live this session via tool call)

- `gh api repos/halfb00t/spur` — merge settings, `delete_branch_on_merge` discrepancy
- `gh api repos/halfb00t/spur/actions/runs`, `.../actions/runs/<id>/jobs`,
  `.../actions/workflows`, `.../compare/main...HEAD` — run history, job names/shapes,
  single-workflow confirmation, behind_by shape
- `gh pr view 2`, `gh pr view 3`, `gh pr list` — PR check-rollup shapes (empty vs. green)
- `gh pr merge --help`, `gh --version` — flag surface on the installed CLI version
- `gh api repos/pre-commit/pre-commit/issues/3120/comments` — full issue thread, read
  directly, not summarized
- `.venv/bin/pre-commit --version` — 4.6.2
- Repo files read in full this session: `.pre-commit-config.yaml`, `Makefile`,
  `pyproject.toml`, `.github/workflows/ci.yml`,
  `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`,
  `docs/HOW_TO_DEVELOP.md`, `docs/architecture/decision_log.md`,
  `docs/tech_debt/TEMPLATE.md`, `docs/tech_debt/INDEX.md`, `README.md`,
  `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md`,
  `.planning/codebase/STACK.md`, `.planning/REQUIREMENTS.md`, `docs/plan-2026-09-21.md`,
  `bench/memory.py`, `tests/test_bench.py`, `Dockerfile`, `docker/refresh-requirements.sh`,
  `docs/CODING_VALUES.md`, `.planning/config.json`

### Secondary (MEDIUM confidence — official docs fetched this session)

- <https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/skipping-workflow-runs> — exact five bracket tokens + `skip-checks` trailer syntax, fetched twice (structured summary + raw HTML text) this session; does **not** itself state case-sensitivity or precise in-message-position rules (see Assumption A1)
- <https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#update-a-repository> — verbatim enum values for `squash_merge_commit_title` (`PR_TITLE`, `COMMIT_OR_PR_TITLE` only) and `squash_merge_commit_message` (`PR_BODY`, `COMMIT_MESSAGES`, `BLANK`)
- <https://pre-commit.com/index.html> — `commit-msg` hook filename-argument contract, `default_install_hook_types` semantics

### Tertiary (LOW confidence — WebSearch only, not independently confirmed against an official page this session)

- `gh pr merge --squash` honoring repo squash settings when no `-t`/`-b` passed (Assumption A2) — this claim came from WebSearch result summaries citing third-party blog/issue discussions, not from `cli.github.com`'s own manual page, which did not state it when fetched directly
- GitHub skip-token case-insensitivity (Assumption A1) — same caveat

## Metadata

**Confidence breakdown:**
- Merge-gate mechanics (job names, behind_by, PR check shapes): HIGH — every shape came from a live call against this exact repo this session.
- Skip-token grammar (the six tokens themselves): HIGH — fetched verbatim from the official GitHub docs page, twice, matching 05-CONTEXT.md's own D-02 list exactly.
- Skip-token case-sensitivity / `gh pr merge` default-settings honoring: LOW — not confirmed against an official source this session; flagged as assumptions requiring an execution-time falsification check (see Assumptions Log A1/A2).
- pre-commit `commit-msg` stage mechanics: HIGH — confirmed against official docs plus a read GitHub issue thread showing the repo's own existing flat-config shape already matches the working pattern.
- Python-3.12-only migration mechanics: HIGH — every file this touches (`pyproject.toml`, `Makefile`, `README.md`, `Dockerfile`, `docker/refresh-requirements.sh`) was read this session; the Dockerfile and refresh script already target 3.12 with nothing to change.

**Research date:** 2026-09-25
**Valid until:** ~7 days for the live GitHub state (run history, repo settings — these
change with every merge); ~30 days for the mechanics (pre-commit hook contract, GitHub skip-
token grammar, Python version floor reasoning) unless GitHub or `gh` ships a relevant
change.
