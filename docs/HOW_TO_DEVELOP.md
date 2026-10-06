# How to develop spur (a guide for the human)

The cycle that work with AI agents follows in this repository, and your role at each
step.

```
discussion -> plan -> plan review -> execution (phase branch) -> acceptance -> PR -> review by other CLI -> merge
you set the   AI writes you approve  AI builds on gsd/phase-NN   you verify    CI    cross-check            squash
   goal       the plan
```

One pass = one phase = one branch = one PR = one squash commit on `main`. Keep phases
small.

## 0. What is already guaranteed

Before talking about the cycle — here is what already stands in the repository and
works, so that raw work does not slip through:

- `make verify` — the single gate: ruff, mypy `--strict`, the import-boundary contracts,
  the unfinished-work scan (`TODO`/`FIXME`/`NotImplementedError`), pytest. ~64 s on a warm
  cache (12-core dev host, `bench/RESULTS.md`, Phase 15).
- The same `make verify` runs in the pre-push hook, in CI (on every push to `main` and
  on every PR, Python 3.12) and inside `make worktree.land` before landing. One
  definition of "passed" in three places. The pre-commit hook runs `make verify.fast`:
  the gate's static steps plus every test file but `tests/test_model.py`,
  `tests/test_pool.py`, `tests/test_api.py` and `tests/test_cli.py`, under 30 s (`L36`),
  so a local commit can be red on those four while `main` cannot: the push runs the whole
  gate, but `--no-verify`, `SKIP=` or pushing a ref other than the checked-out one skips
  it, so CI and the ruleset are the wall (`L36`). Run
  `make venv` once in the main checkout and it installs all three hooks.
- `gsd-ship` will not create a PR until the phase's verification is `passed`, the tree is
  clean, and the phase's `SECURITY.md` states `threats_open: 0`. A gate, not a reminder.
- Three newer guarantees (`L22`): the `commit-msg` hook refuses a commit carrying any of
  the six GitHub Actions CI-skip tokens, in the subject or the body; the ruleset on `main`
  makes GitHub refuse a merge without green `test (3.12)`, `vendor-bundle` and `image` on
  a head that is not behind `main`, and refuse any direct push (D-12); `make pr.land PR=N`
  is the path into `main` that additionally checks the squash text and the run on the
  squash commit (section 8).
- `make check` — all of the above plus the image build, the smoke test inside the
  container and the check that the vendored three.js is built byte for byte from `web/`.
  Needs Docker.
- `AGENTS.md` — the rules the agent reads first; `docs/architecture/` — the system map
  and the `Lxx` decision log.

The first run after `make clean` pulls ~1.4 GB of OpenCascade and takes a couple of
minutes — that is the page cache, not the tests.

## 1. Discussion

`gsd-discuss-phase` (for the project's first gsd setup — `gsd-map-codebase`, then
`gsd-ingest-docs`). Discuss what is needed next. Your role: state the goal and the
constraints, not the solution.

## 2. Plan

`gsd-plan-phase`. The agent writes a step-by-step plan into `.planning/`. Your role: wait.

`main` accepts changes only through a pull request (the wall is the ruleset, `L22`); a
direct push to it is refused. So the phase branch is cut from `origin/main` before
`gsd-discuss-phase` (`git switch -c gsd/phase-NN-<slug> origin/main`), and both the
discussion and the plan commits already ride on it; `gsd-execute-phase` at step 4 reuses
this ready branch instead of cutting a new one. Phase 5 went exactly this way: its
discussion, research and plan all on `gsd/phase-05-ci-observed-green`, not one commit on
`main`.

## 3. Plan review and revision

`gsd-review --phase N` — the second CLI looks at the plan before anything is written.

**Do not approve a plan you do not understand — ask until you do.** Here a mistake costs
minutes; after the build, hours.

For this project, three things are especially worth checking on the plan:

- Does the shape of a part change that the user did not ask to change? Defaults are
  frozen (`L05`); every link to a model relies on them.
- Does a number appear that could be untrue? Rule `L08`: a warning with no number beats a
  plausible number.
- Is there a measurement under a claim about speed or memory? That is the convention in
  this repository: comments carry the figures and the load they were taken under.

## 4. Execution on the phase branch

`gsd-execute-phase N`. `.planning/config.json` has `git.branching_strategy: "phase"`, so
the command itself cuts the branch `gsd/phase-NN-<slug>` from `origin/main`, switches the
main checkout to it and puts every commit of the phase there — plans, code, verification,
`ROADMAP`/`STATE`. `main` stays what has already been landed. Throughout the work,
`make verify` must stay green.

gsd's SDK commit stops at 30 s. On `{committed: false, reason: 'commit_timeout'}` the hook
keeps running as an orphan, so wait until `pgrep -fl 'pre_commit hook-impl|pytest|mypy'`
prints nothing, then make exactly one plain `git commit` and record it in the plan's
SUMMARY; never retry the SDK commit blind. This replaces the executor's
remove-the-lock-and-retry recovery for this repository (`L36`).

Inside a phase gsd may run the executors of parallel plans in agent worktrees
(`.claude/worktrees/agent-*`). On a phase branch this almost never kicks in: Claude Code
cuts such worktrees from `origin/HEAD`, and as soon as the branch has its first commit,
gsd honestly falls back to sequential execution in the main checkout and reports
`⚠ Worktree base mismatch`. That is normal, not a breakage — Phase 2 went that way
entirely.

**One trap specific to this project.** Any worktree — an agent's or one made by hand via
`make worktree.new` — has no `.venv` of its own, and here it weighs ~1.4 GB. The
temptation is to point it at the shared one from the main checkout. Do not, and this is
verified: the editable install in `.venv` is pinned to the main checkout's `src/`, so
`import spur` from the worktree resolves back there, and the tests silently check the
unchanged code and pass. Either `make venv` inside the worktree (the first `make verify`
there does it itself — a couple of minutes), or `make test-image` (runs the suite in a
container; no local Python needed). `make worktree.new` prints this reminder itself.

## 5. Acceptance

`gsd-verify-work N` — on the phase branch, before the PR. Walk through the feature as a
user. For spur that means: open the UI, build a part, look at the warnings and — if
geometry or numbers changed — check the measurements. If it does not add up — back to
discussion, not blind patching.

Why before the PR: `gsd-ship` refuses a phase whose verification is not `passed`, and it
is exactly your manual checks that move it from `human_needed` to `passed`. Also before
the PR: `gsd-secure-phase N` (produces `SECURITY.md`; without it ship will not pass) and
`gsd-validate-phase N`.

## 6. PR

Run `make verify` before every push, then push: the pre-push hook runs the whole gate
(about 64 s warm), and the explicit run warms the page cache and shows the result.

```sh
/gsd-ship N
```

Checks the verification, the clean tree and that you are not on `main`; pushes the phase
branch; creates a PR "Phase N: …" into `main` with a body assembled from the planning
artifacts. CI starts on the PR by itself — green CI before the merge, not after.

The ship-note commit carries `[ci skip]` in its subject, and the `no-skip-token` hook
(D-02) refuses it: `gsd-ship` prints a warning and leaves `.planning/STATE.md` modified
but uncommitted. Commit it by hand: `docs(NN): ship phase N — PR #M`, without the token,
then `git push`. The push starts one more CI run (~3 min) on the new PR HEAD — the one
`make pr.land` requires. The global `~/.claude/gsd-core/workflows/ship.md` is not
patched: the edit would be lost at the next gsd update and is invisible to this
repository.

The hook reads the message whole, together with the diff that `git commit -v` appends
below the cut line: if that diff names a CI-skip token, the commit is refused — commit
without `-v` or rephrase.

## 7. Code review by the *other* CLI

Claude wrote it → **Codex** reviews; Codex wrote it → **Claude** reviews. Both CLIs read
the same `AGENTS.md`, so the rules are shared while the perspective differs. The second
model will not rubber-stamp its own work. The subject of the review is the PR
(`gh pr diff N`, or `gh pr checkout N` for the second CLI).

Real findings go in as fix commits on the phase branch, `make verify`, `git push`; the PR
updates itself. (If you want to automate it: `workflow.code_review_command` in
`.planning/config.json` — ship feeds it the diff on stdin and expects JSON with a
`verdict`; `REVISE` blocks ship.)

## 8. Land

The repository's squash-message setting lives outside git and is applied once with the
command below (`docs/HOW_TO_DEVELOP.md` is its only record). Without it the squash commit
inherits the branch's commit subjects, concatenated; that is how the token reached `main`
twice (`538d26f`, `bfc9110`, neither has a run). With it the squash commit carries the PR
title and body — the same curated text `gsd-ship` assembles from the planning artifacts:

```sh
gh api -X PATCH repos/halfb00t/spur \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY
```

The wall is also a repository setting outside git (D-12): the public ruleset `default`
(id `23977515`) targeting `main`. It requires green `test (3.12)`, `vendor-bundle` and
`image` from GitHub Actions on a head that is not behind `main`, and a pull request for
every change; GitHub refuses a merge without them and refuses a direct push (`L22`,
D-12). The command is here because a repository setting does not live in git:

```sh
gh api repos/halfb00t/spur/rulesets/23977515 --jq '{conditions: {ref_name: {include: ["refs/heads/main"], exclude: []}}, rules: ([.rules[] | select(.type != "required_status_checks")] + [{type: "required_status_checks", parameters: {strict_required_status_checks_policy: true, do_not_enforce_on_create: false, required_status_checks: [{context: "test (3.12)", integration_id: 15368}, {context: "vendor-bundle", integration_id: 15368}, {context: "image", integration_id: 15368}]}}])}' | gh api -X PUT repos/halfb00t/spur/rulesets/23977515 --input -

gh api repos/halfb00t/spur/rules/branches/main   # read the wall as it stands

gh api -X DELETE repos/halfb00t/spur/rulesets/23977515   # take the wall down
```

When `.github/workflows/required-jobs.txt` changes, fix the contexts in the apply command
and run it again — it replaces the required-checks rule whole rather than adding a second
one; until it is re-run, the wall and `make pr.land` require different lists of checks.
The names in it are the ones GitHub shows: `jobs.<id>.name` if set, otherwise the id,
plus the matrix values (`test (3.12)`); the drift test in `tests/test_pr_land.py` derives
them from `ci.yml` and compares (D-05).

A phase reaches `main` through `make pr.land PR=N` (`L22`):

```sh
make pr.land PR=N
```

Run `make pr.land` from an up-to-date checkout of `main` — `git switch main && git pull
--ff-only` — the list of required jobs is read from the local
`.github/workflows/required-jobs.txt` in the checkout where the command runs, and
`pr.land`'s own step 6 leaves you on `main` at the end anyway (D-04).

In order, it: reads the PR's current head; refuses if the PR is not `OPEN` or is not based
on `main`; refuses on a dirty tree; refuses if the head is behind `main` (`behind_by > 0`
— then rebase, push, wait for the CI run on the real tree and retry) or equal to it;
refuses if the head has no completed green `ci.yml` run for every check in
`.github/workflows/required-jobs.txt`, and if the run itself did not finish `success`
(`conclusion`): a failed job that is not on the list still makes the run red; refuses if
the PR title or body carries a CI-skip token (after D-03 that text becomes `main`'s
commit message). Then it squash-merges exactly the verified head with exactly the
verified title and body, waits up to a minute for the CI run on the new `main` commit and
prints its URL, then switches to `main`, pulls it, and deletes the local phase branch only
if its tip is the landed commit.

Any refusal means nothing was landed.

If after the squash merge no `ci.yml` run appeared within the wait window, `pr.land`
exits non-zero with the PR already landed and reports exactly what it saw, no more:
`last error: …` — the reads failed (network, `gh auth status`, rate limit) — check them
and look for the run yourself; a link to `…/actions/workflows/ci.yml` — the reads
succeeded but no run appeared in the window — open the link, GitHub may have started it
later; a named CI-skip token — it reached the squash commit text, which is an `L22`
regression — file it in `docs/tech_debt/`.

**The wall and the tool** (D-12). Keep the words "a tool, not a wall" — they are about
`pr.land`. The wall is the ruleset from the paragraph above: GitHub itself refuses to
merge a head without green required checks or one behind `main`, and refuses any direct
push. `make pr.land` is a tool, not a wall, and it is the sanctioned way through the wall
precisely because it does what the wall cannot: refuses on a CI-skip token in the PR
title or body (after D-03 that text becomes `main`'s commit message, so the token fires
only after the wall); proves that a run appeared for the squash commit; does the local
cleanup itself. It checks the job list and the lag behind `main` itself, but only at the
moment of its read: the window between that read and `gh pr merge` is closed by the
ruleset's strict up-to-date policy (D-12, no bypass actors) — `--match-head-commit` pins
the PR head, not the base. The second half `pr.land` proves itself: that a run appeared
for the squash commit. The button on GitHub merges only what the wall accepts, but skips
these checks — so it is not the way.

`pr.land` deletes the local branch the way it used to be done by hand — `-D`, not `-d`:
after a squash the branch is not an ancestor of `main`, and `-d` refuses. So it first
compares the branch tip with the landed commit and erases it only on a match.

Red CI or open review findings — no merge. Work landed by hand that skipped review and
verify is exactly the hole all of this exists to close.

## Parallel cycles

gsd phases go one at a time: each is cut from the already-landed `main`. What makes sense
to parallelize is work outside phases — `gsd-quick`, point fixes: for those it is still
`make worktree.new SLUG=<slug>` (branch `agent/<slug>` in `.claude/worktrees/<slug>`) and
`make worktree.land SLUG=<slug> MSG="<commit>"`, which itself checks cleanliness,
squash-merges, runs `make verify` once more on the merged result and only then commits.
It commits straight into the worktree's base branch; if that base turned out to be
`main`, the result cannot be pushed — the ruleset refuses a direct push (`L22`): use a
branch as the base and bring it into `main` as a PR via `make pr.land`.

Your role shifts from "waiting for one thing" to "keeping the pipeline full": while one
phase executes, you discuss or review the plan of the next. But judge dependencies
honestly — two cycles editing `calc.py` will collide on landing. Not sure the tasks are
independent — ask the agent before starting both.

## Practical rules

- Never approve a plan or a result you do not understand. Ask.
- `make verify` and review by the other CLI are insurance, not a formality. Skipping
  either is exactly how slop gets into the project.
- Small phases beat big ones. One at a time.
- Found a good idea or cut a corner — record it as a file in `docs/ideas/` or
  `docs/tech_debt/`, or it vanishes with the session.
- If the agent claims something got faster or leaner, demand the figure and the load.
