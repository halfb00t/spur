# Phase 5: CI Observed Green - Context

**Gathered:** 2026-09-25
**Status:** Ready for planning

<domain>
## Phase Boundary

**The roadmap premise is stale and was corrected in this discussion.** The roadmap and
STATE.md say `.github/workflows/ci.yml` "has never executed inside GitHub Actions". It has:
13 runs since 2026-09-21 (verified with `gh api` on 2026-09-25; details in `<specifics>`).
The original goal — "prove the workflow runs" — is already met by main push run
`35963114939`. What the runs *revealed* is the phase's real work: the gate has two holes,
both observed on `main`'s last two merges.

**Reframed goal.** CI is the *trusted* merge gate for `main`: every commit that lands on
`main` has a GitHub Actions run attached — structurally, not by discipline; a red, missing or
stale run cannot be merged through the sanctioned path; the supported Python is the one that
actually runs (3.12); and the 2026-09-21 "CI workflow unverified" blocker is retired with run
URLs as evidence.

**Reframed success criteria** (for `/gsd-phase --edit 5`, to be applied before planning —
D-10):

1. No commit in this repository can carry a GitHub skip token: a repo-owned `commit-msg`
   hook rejects all six, proven by a test; the repository's squash-merge message is the PR
   title + body, never the branch's commit subjects (D-02, D-03).
2. `make pr.land PR=N` is the documented merge path: it refuses a PR whose head sha lacks a
   green run for every named job, refuses a branch behind `main`, squash-merges, and exits
   non-zero unless a run appears for the squash commit — printing its URL (D-05).
3. spur supports Python 3.12 only: `requires-python`, ruff target, the CI matrix, Makefile,
   README and a decision-log entry superseding L01's floor all agree; `make verify` is green
   (D-09).
4. The STATE.md blocker is retired citing runs `35963114939` and `36088409707`; the
   skip-token debt file is `Status: resolved` in the same commit as the hook + setting; L22
   (merge gate) and L23 (Python 3.12) are appended to the decision log (D-07, D-08, D-11).

**Not in scope:** new CI jobs (coverage floor, browser test — own debt/idea files); branch
protection or required checks (needs a public repo or GitHub Pro — a visibility/money
decision, deferred); any change to *what* `make verify` checks; patching the global
`~/.claude/gsd-core/workflows/ship.md`.

</domain>

<decisions>
## Implementation Decisions

### Scope
- **D-01:** Phase 5 is reframed from "observe CI run" to "CI is the trusted merge gate", per
  the evidence in `<specifics>`. "Bookkeeping only" (record URLs, leave the `must` debt file
  active) was rejected: the debt file itself says "Phase 5 owns the decision".

### Skip-token leak (retires `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`)
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

### Red-merge prevention
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

### Evidence & bookkeeping
- **D-07:** The STATE.md blocker "CI workflow unverified" is **retired in this phase**, citing
  the evidence that already exists: main push run
  <https://github.com/halfb00t/spur/actions/runs/35963114939> (`59f02c3`, 2026-09-24 —
  `test (3.10)`, `test (3.12)`, `vendor-bundle`, `image` all success: a real push to `main`
  with the gate and both container checks green, REQ-ci-verified's wording) and PR #3 head run
  <https://github.com/halfb00t/spur/actions/runs/36088409707> (`2c4b544`, tree-identical to
  `main` HEAD `bfc9110`). Phase 5's own squash-commit run URL is printed by `make pr.land` at
  merge and recorded on the next STATE.md touch — **not** by a docs-only commit on `main`
  (one phase = one PR = one squash commit, HOW_TO_DEVELOP). Stale claims corrected in the
  same change: `.planning/codebase/CONCERNS.md` L221 ("never executed"),
  `.planning/codebase/INTEGRATIONS.md` CI section, `README.md` L207, REQUIREMENTS.md
  REQ-ci-verified ("both supported Python versions").
- **D-08:** Two decision-log entries, **appended, dated, never edited in place** (the log's
  own policy; L13 stays as written — still true, L22 extends it): **L22 — the merge gate**
  (D-02…D-05), citing as trigger PR #2's red merge (run `35993984796` failed `test (3.10)`,
  merged five minutes later) and the two run-less squash commits `538d26f`, `bfc9110`;
  **L23 — Python 3.12 only** (D-09), superseding L01's floor. Numbering order is the
  planner's. — **Reversibility:** one-way — the log is append-only by policy.
- **D-10:** The ROADMAP Phase 5 goal and success criteria are rewritten **now, before
  planning**, via `/gsd-phase --edit 5`, to the text in `<domain>`. The planner and verifier
  must work from true criteria; "fix it at phase completion" was rejected.
- **D-11:** The skip-token debt file is resolved **in the fix commit** (D-02 + D-03), per
  CLAUDE.md: `Status: resolved`, sha, `git mv` into `docs/tech_debt/resolved/`, INDEX row
  moved — citing the hook's test and the PR-head run as evidence; `pr.land`'s post-merge
  check (D-05 step 5) is the standing verification the file's "Next step" asks for.
  "Resolve after the merge is observed" was rejected (a follow-up commit on `main`).

### Python versions (supersedes L01's floor)
- **D-09:** **spur supports Python 3.12 only.** `requires-python = ">=3.12,<3.13"` (the
  upper bound makes L01's ceiling checkable — pip refuses instead of spending minutes trying
  to build OpenCascade), ruff `target-version = "py312"`, mypy `python_version = "3.12"`
  unchanged (its comment keeps the numpy-stub reason and drops the "floor checked by
  execution" paragraph), CI matrix `["3.12"]`, Makefile's interpreter loop and its error
  message narrowed to `python3.12`, README "Python 3.10+" → 3.12, L01 superseded on the
  floor by L23 (ceiling reasoning stands: no wheels above 3.12; widen when a wheel *and* a
  consumer appear). **Why:** the floor was never a requirement — L01 says "detected, not
  chosen"; the Docker image, the dev machine and the pre-commit hook are all 3.12; the only
  3.10 execution this code ever had was CI's leg; mypy cannot hold a floor below 3.12 (numpy's
  bundled stubs use `type` statements), so any lower floor is checked by execution only — the
  gap that let `records.py`'s `logging.StreamHandler[TextIO]` (3.11+ at runtime) reach `main`
  unimportable on 3.10 (runs `35993984796`, `36028253714`, `36028759311`; fixed `990d1fe`).
  With one version, the type checker's version equals the runtime and the gap closes
  structurally. Ubuntu 22.04 `pip install` users use Docker (needs no local Python) or `uv`.
  Rejected: 3.11–3.12 (keeps the gap); 3.10 in the pre-commit hook (every clone needs 3.10,
  hook time ~doubles). — **Reversibility:** costly — widening back is a one-line matrix
  change plus a new log entry, but any 3.12-only stdlib or syntax adopted meanwhile must be
  unwound, and the published `requires-python` change refuses a `pip install` on 3.10/3.11
  that worked before.

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirement
- `.planning/ROADMAP.md` — "### Phase 5: CI Observed Green" (to be rewritten per D-10; the
  reframed text is in `<domain>` above)
- `.planning/REQUIREMENTS.md` — REQ-ci-verified (Delivery); its acceptance wording "both
  supported Python versions" changes with D-09
- `.planning/STATE.md` — "Blockers/Concerns", first bullet: the blocker D-07 retires
- `docs/plan-2026-09-21.md` L135–137 — where the blocker was born ("GitHub Actions cannot be
  run here")

### The two holes and their evidence
- `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` — the
  `must` debt file this phase resolves (D-02, D-03, D-11); its "Next step" lists the options
  chosen from
- `.github/workflows/ci.yml` — the three jobs; `test` matrix collapses to `["3.12"]` (D-09);
  job names are the contract `pr.land` reads (D-05)
- `~/.claude/gsd-core/workflows/ship.md` — `track_shipping` step: the hardcoded `[ci skip]`
  ship note and the "BLOCKED with zero checks" recovery that never fires here (external file,
  read-only for this phase — D-04)

### Process docs this phase edits
- `docs/HOW_TO_DEVELOP.md` §6 "PR" (ship-note manual step, D-04) and §8 "Влить" (`make
  pr.land` replaces the GitHub button; the `gh api` PATCH for D-03) — Russian, keep the language
- `docs/architecture/decision_log.md` — L01 (Stack: 3.10–3.12 "detected, not chosen" — floor
  superseded by L23), L13 (`make verify` is the gate — extended by L22); append L22 and L23
  (D-08)
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/TEMPLATE.md` — the resolve lifecycle (D-11)
- `CLAUDE.md` — "Finishing work properly", "Capturing ideas and debt": same-commit resolution
  rule; "Stop and ask first": superseding a locked decision is proposed, not ignored
- `docs/CODING_VALUES.md` — coding standard for anything added

### Build and gate surfaces touched
- `Makefile` — `verify`/`check`, the `PYTHON` interpreter loop (D-09), `worktree.land`
  (precedent for a landing target: verify-before-merge, lock/trap; new `pr.land` sits next to
  it)
- `.pre-commit-config.yaml` — the local `verify` hook; the `commit-msg` hook joins it (D-02)
- `pyproject.toml` — `requires-python` L10, `[tool.ruff] target-version` L38, `[tool.mypy]`
  L80–85 (the 3.12/numpy-stubs comment), `[tool.importlinter]`
- `README.md` L95, L200–212 (Python version claims), L207 (CI wording)
- `.planning/codebase/CONCERNS.md` L221, `.planning/codebase/INTEGRATIONS.md` "CI/CD &
  Deployment", `.planning/codebase/STACK.md` L13–15 — stale "never executed" / 3.10 lines

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Makefile` `worktree.land`: the existing "verify before you land" target — dirty-tree
  checks, a `mkdir` lock with `trap`, `reset --hard` only after proving the base clean, one
  `echo` per refusal. `pr.land` follows its shape and sits beside it.
- `.pre-commit-config.yaml`: local-hook pattern (`repo: local`, `language: system`,
  `pass_filenames: false`) — the `commit-msg` hook is a second entry with
  `stages: [commit-msg]` (receives the message file path as its argument).
- `no-fake-done` target: a `git grep` message-pattern scan with an explanatory refusal —
  the tone and shape for the token hook's refusal text.
- `docker/smoke.py`: the only standalone script outside `src/`; typed under mypy
  `--strict` + `disallow_any_explicit` because `make typecheck` lists `docker`. Any new
  Python dir must be added to that list.
- `gh` is authenticated as `halfb00t` (repo scope; `billing` needs `user` scope — not
  needed). `gh api repos/halfb00t/spur/actions/runs?head_sha=…`, `…/runs/<id>/jobs`,
  `gh pr view N --json headRefOid,statusCheckRollup,mergeStateStatus`, and
  `repos/…/compare/main...<sha>` (`behind_by`) are the calls `pr.land` needs; all were
  exercised in this discussion.

### Established Patterns
- Comments explain *why* and carry the measurement or constraint (CODING_VALUES). The
  `pyproject.toml` mypy comment is the model for the D-09 rewrite.
- Decisions are appended to the log with dates and superseded-by pointers; nothing edited in
  place (L06→L18, L07→L17, L14→L21 precedents).
- Debt resolution happens in the fix commit: `Status: resolved`, sha, `git mv`, INDEX row
  (Phases 2–4 all did this).
- Tests read like requirements; `make verify` is the gate and pre-commit runs it (~42 s —
  the reason Phase 4 committed with plain `git commit` instead of `gsd_run query commit`'s
  30 s wrapper).
- One phase = one branch = one PR = one squash commit (HOW_TO_DEVELOP); `.planning/`
  artifacts ride in the PR.

### Integration Points
- `.github/workflows/ci.yml` `test.strategy.matrix.python` → `["3.12"]`; job names →
  `pr.land`'s required set.
- `Makefile`: new `pr.land` target (`## help` line), narrowed `PYTHON` loop and its error text.
- `.pre-commit-config.yaml`: `commit-msg` hook + `default_install_hook_types`.
- `pyproject.toml`: `requires-python`, ruff `target-version`, mypy comment.
- `docs/HOW_TO_DEVELOP.md` §6/§8; `docs/architecture/decision_log.md` L22/L23;
  `docs/tech_debt/` move + INDEX; `README.md`; `.planning/codebase/*.md` stale lines;
  `.planning/STATE.md` blocker via gsd state tooling (no direct edits to STATE/ROADMAP).
- GitHub repository settings (not in git): `squash_merge_commit_title`,
  `squash_merge_commit_message` via `gh api -X PATCH`.

### Verified GitHub facts (2026-09-25)
- Repo `halfb00t/spur` is **private on a free plan**: `branches/main/protection` and
  `rulesets` return HTTP 403 ("Upgrade to GitHub Pro or make this repository public").
- Merge settings today: `allow_squash_merge/merge_commit/rebase_merge: true`,
  `delete_branch_on_merge: false`, `squash_merge_commit_title: COMMIT_OR_PR_TITLE`,
  `squash_merge_commit_message: COMMIT_MESSAGES`.
- A full run is ~3 min wall: `vendor-bundle` ~10 s, `test (3.x)` ~1.5–2 min each,
  `image` ~2.5 min. ~9 job-minutes per run today, ~7 after D-09.

</code_context>

<specifics>
## Specific Ideas

### Observed state that drives this phase (all via `gh api`, 2026-09-25)

13 workflow runs total. Push runs on `main` — all six green, all four jobs:
`10e8699` (PR #1 merge commit), `de5b3da`, `5252bdc` (2026-09-21), `e07d0f3`, `63066ff`,
`59f02c3` (2026-09-24, run `35963114939`). **No run for `538d26f` (PR #2 squash) or
`bfc9110` (PR #3 squash, current HEAD).**

| Commit | Where | Skip token present | Run |
|---|---|---|---|
| `20b63e4` | PR #2 head — `docs(03): ship phase 3 — PR #2 [ci skip]` | subject | none |
| `18bc4ad` | PR #2 last real run | — | `35993984796` **failure**: `test (3.10)` — 4 test modules fail at collection, `TypeError: 'type' object is not subscriptable`; merged 5 min later |
| `538d26f` | `main`, PR #2 squash | body line 348 (inherited subject) | none |
| `49ae671`, `87d500e` | PR #3 | — | `36028253714`, `36028759311` **failure**: same 3.10 error |
| `990d1fe` | PR #3 | — | fix: `_JsonHandler`'s generic base behind `TYPE_CHECKING` |
| `6fce500` | PR #3 ship note — "No [ci skip] on purpose" | **prose mention in body** | none (needed empty commit `87d500e`) |
| `2c4b544` | PR #3 head | — | `36088409707` **success**, all four jobs; tree == `bfc9110`'s |
| `bfc9110` | `main`, PR #3 squash | body line 404 (inherited from `6fce500`) | none |

Why mypy did not see the 3.10 break: `python_version = "3.12"` (numpy stubs) and typeshed
marks `StreamHandler` generic for every version; ruff `py310` holds syntax only; the local
`.venv` is 3.12.13 and no 3.10 exists on the dev machine.

### Wording the user wants kept
- "A tool, not a wall" for `pr.land` — the docs must say the web button still works and
  what a wall would take (D-06).
- The L23 entry says why 3.10 was ever there: "detected, not chosen" (L01), and that the
  ceiling reasoning is unchanged.

</specifics>

<deferred>
## Deferred Ideas

- **Branch protection / required checks** — the only true wall; needs the repo public or
  GitHub Pro. A visibility/money decision the human makes outside this phase. If either
  happens, the required checks are the `pr.land` job set and "require branches to be up to
  date" — D-05 is then redundant, not wrong.
- **Actions minutes on a private free plan** (2,000 min/month): ~7–9 job-minutes per run
  today; not measured (billing API needs the `user` scope). Watch if runs multiply.
- **Stale remote branches** `origin/gsd/phase-03-…`, `origin/gsd/phase-04-…`,
  `origin/review-fixes-2026-09-21` (`delete_branch_on_merge: false`) — housekeeping, not
  this phase.
- **`make check` asserting the repository's squash setting** — would put a network call in
  the gate; not now.
- **A local 3.10 floor run** — moot after D-09; recorded only so the option is not
  re-derived.

None of these came from the user as scope requests — discussion stayed within the phase.

</deferred>

---

*Phase: 05-ci-observed-green*
*Context gathered: 2026-09-25*
