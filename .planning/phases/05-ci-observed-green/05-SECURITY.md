---
phase: "05"
slug: "ci-observed-green"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-25"
---

# Phase 05 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register source: the `<threat_model>` blocks of `05-01` through `05-06-PLAN.md` (authored at
plan time, 30 rows; `05-06` is the gap-closure plan). No SUMMARY carried a `## Threat Flags`
section. ASVS level 1 with `register_authored_at_plan_time: true` and every row closed at
grep depth took the workflow's short-circuit: no auditor agent was spawned; the evidence
column below is what the orchestrator checked in the tree at `9e89555`, plus two live
GitHub read-backs made during this audit (`gh api repos/halfb00t/spur/rules/branches/main`
and `gh api repos/halfb00t/spur`). Line numbers refer to that tree.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| commit message → commit-msg hook (`scripts/skip_tokens.py`) | Any contributor or tool writes arbitrary text; git hands the hook the unprocessed buffer and the hook reads it as data | commit message bytes (possibly invalid UTF-8) |
| process environment → commit-msg hook | The hook reads `GIT_EDITOR`, which git sets to `:` itself for commit hooks when no editor runs (githooks(5)) | one environment variable |
| GitHub API → `make pr.land` | PR fields (title, body, branch name) are written by whoever opened the PR; run/job JSON decides whether a merge happens | PR title/body, head sha, runs and jobs JSON, compare status |
| `pr.land` → `gh pr merge` | The one irreversible step: a squash commit on `main` | checked head sha, checked subject and body |
| PR title/body → `main`'s squash commit | After D-03 GitHub records the PR title and body verbatim as `main`'s commit message | the text a skip token would ride in |
| `pr.land` → local repository | `git switch`, `git pull`, `git branch -D` change the developer's clone | branch names, the merged sha |
| developer shell → GitHub repository settings | `gh api -X PATCH` (squash message, D-03) and `gh api -X PUT` (ruleset 23977515, D-12) change server-side settings that are not in git and decide every merge into `main` | repository settings JSON |
| documentation → the human who merges | `docs/HOW_TO_DEVELOP.md` §8, `packaging.md` and L22 decide what the human believes GitHub will and will not refuse | prose about the wall and the tool |
| `pyproject.toml` → pip on a user's machine | `requires-python` decides whether an install is attempted at all | interpreter version |
| planning record → the next session | `STATE.md` and the codebase map are what the next agent believes about CI | run URLs, blocker text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Tampering | `scripts/skip_tokens.py` reading the message | low | mitigate | `skip_tokens.py:89` `Path(...).read_text(encoding="utf-8", errors="replace")`; matched with `re` only — the module imports `argparse`, `os`, `re`, `pathlib` and nothing that reaches a shell (`subprocess`, `eval`, `os.system` absent); `tests/test_skip_tokens.py::test_hook_entry_handles_invalid_utf8_with_a_token_without_crashing` (:213) and `::..._without_a_token` (:224) | closed |
| T-05-02 | Repudiation | `git commit --no-verify` / `SKIP=no-skip-token` | medium | accept | R-05-01: backstops verified — live ruleset requires green `test (3.12)`, `vendor-bundle`, `image` on an up-to-date head (`strict_required_status_checks_policy: true`); `pr_land.py` refuses a run-less head (`tests/test_pr_land.py::test_check_head_zero_runs_refuses_naming_no_ci_yml_run_and_the_sha` :539) and exits 1 when the squash commit gets no run (`::test_land_poll_timeout_reports_merged_but_no_run` :617) | closed |
| T-05-03 | Elevation of Privilege | `gh api -X PATCH repos/halfb00t/spur` (D-03) | low | mitigate | Read back live during this audit: `squash_merge_commit_title: PR_TITLE`, `squash_merge_commit_message: PR_BODY`; the exact command is recorded in `docs/HOW_TO_DEVELOP.md` §8 beside the ruleset commands; admin precondition and read-back pattern recorded in `05-03-SUMMARY.md` (key-decisions, patterns-established) | closed |
| T-05-04 | Denial of Service | hook false positives on legitimate commits | low | mitigate | Only GitHub's own token forms match: `test_bracketed_words_joined_by_a_hyphen_is_a_near_miss` (:91), `test_two_words_without_brackets_is_a_near_miss` (:97), `test_clean_multi_paragraph_message_gives_no_tokens` (:78); git's `-v` diff below the cut line is skipped in an editor session: `test_token_only_below_the_scissors_line_gives_no_tokens` (:115) | closed |
| T-05-05 | Tampering | check → merge window (a push lands between them) | high | mitigate | `scripts/pr_land.py:420` passes `--match-head-commit` with the sha `check_head` verified; GitHub refuses the merge if the head moved; the merge argv is asserted by `tests/test_pr_land.py::test_land_happy_path_returns_0_and_prints_the_run_url` (:598) | closed |
| T-05-06 | Tampering | PR title/body edited between check and merge, or carrying a skip token onto `main` | medium | mitigate | `pr_land.py:422` `--subject` and `:424` `--body` carry the checked text; `message_refusals` runs at `:406` before any merge; `::test_message_refusals_token_in_the_title_is_found_naming_it` (:412), `::..._token_in_a_later_paragraph_of_the_body_is_found` (:419) | closed |
| T-05-07 | Spoofing / Repudiation | Reporting a merge as evidenced when it is not | high | mitigate | Every refusal path prints `pr.land: nothing was merged.` and returns 1 (`pr_land.py:381`–`:411`); after a merge, exit 0 only once a `ci.yml` run for the squash sha is found — poll timeout (`::test_land_poll_timeout_reports_merged_but_no_run` :617), zero runs (:539), unfinished run (:267), missing job (:275), unparseable read (:516) are each a non-zero exit with a test | closed |
| T-05-08 | Tampering (injection) | Titles, bodies, branch names reaching `gh`/`git` | medium | mitigate | One process boundary: `pr_land.py:514` `subprocess.run(argv, capture_output=True, text=True, check=False)`; `shell=` appears nowhere in the module; every value travels as its own argv element | closed |
| T-05-09 | Tampering (local data loss) | `git branch -D` on the developer's clone | medium | mitigate | Dirty tree refused before any call (`::test_land_dirty_tree_refuses_no_merge_call` :657); `pr_land.py:485`–`:497` deletes the local branch only when `local_tip == pr.head_sha`, otherwise keeps it and says why (`::test_land_local_tip_differs_keeps_the_branch` :629, `::test_land_local_branch_absent_no_delete_no_error` :639) | closed |
| T-05-10 | Denial of Service | the post-merge poll | low | mitigate | `pr_land.py:67` `POLL_ATTEMPTS = 12`, `:68` `POLL_INTERVAL_S = 5.0` — bounded at 60 s, then `merged, but no run appeared` and exit 1 | closed |
| T-05-11 | Elevation of Privilege | Merging a red, check-less or behind head through GitHub's web button | medium | mitigate | Live read-back this audit: rule types exactly `deletion`, `non_fast_forward`, `pull_request`, `required_status_checks`; strict policy; required checks exactly `test (3.12)`, `vendor-bundle`, `image` — GitHub refuses the merge and any direct push (D-12, L22) | closed |
| T-05-20 | Repudiation | A button merge of a green, current head skipping pr.land's token and post-merge run checks | low | accept | R-05-02: `docs/HOW_TO_DEVELOP.md` §8 names `make pr.land` as the path and says exactly what the button skips; `docs/architecture/packaging.md:50`–`:54` says the same; a run-less commit on `main` is visible in the Actions run list | closed |
| T-05-12 | Tampering | Weakening the gate by editing `required-jobs.txt` | low | mitigate | `tests/test_pr_land.py::test_required_jobs_file_matches_ci_yml_job_ids` (:188) fails `make verify` unless the list equals the jobs `ci.yml` runs; the file's header says so | closed |
| T-05-13 | Repudiation | `docs/architecture/decision_log.md` (L22) | low | mitigate | `git log --numstat origin/main..HEAD -- docs/architecture/decision_log.md`: `a6c1114` +100 / −0 | closed |
| T-05-14 | Spoofing | Docs misstating the gate | medium | mitigate | §8, `packaging.md:50`–`:54` and L22 describe the ruleset as read back from `rules/branches/main` (L22 body: "Read back from `rules/branches/main`", `integration_id: 15368`) and name what only `pr.land` checks (the squash text, the squash commit's run) | closed |
| T-05-21 | Elevation of Privilege | `gh api -X PUT repos/halfb00t/spur/rulesets/23977515` | medium | mitigate | `05-03-SUMMARY.md` coverage: the PUT body was built from the live GET, the live read-back after the PUT matched the task's assertion byte-for-byte; §8 records apply, read-back and removal commands together; the read-back is re-asserted live in this audit (see T-05-11) | closed |
| T-05-22 | Spoofing | A same-named status posted by something other than `ci.yml` | medium | mitigate | Live read-back: all three required checks carry `integration_id: 15368` (GitHub Actions) — a status from any other app does not satisfy the rule | closed |
| T-05-23 | Denial of Service | A required check no job reports, leaving every PR unmergeable | medium | mitigate | Live required checks equal `.github/workflows/required-jobs.txt` (`test (3.12)`, `vendor-bundle`, `image`); no `test (3.10)` anywhere; the drift test ties the file to `ci.yml`'s jobs; §8 says to re-run the apply command whenever the file changes | closed |
| T-05-24 | Tampering | The ruleset removed or edited later, silently weakening the wall | low | accept | R-05-03: only an admin can change it; `make pr.land` keeps its own job and behind-`main` checks (`check_head`), so the sanctioned path stays exact without the wall; the removal command is D-12's documented reversal in §8 | closed |
| T-05-15 | Tampering | The venv reinstall triggered by `pyproject.toml` | low | accept | R-05-04: no commit in the phase range touches `requirements.txt`; the `pyproject.toml` diff changes `requires-python`, ruff `target-version` and comments only — no dependency line | closed |
| T-05-16 | Denial of Service | Users on Python 3.10/3.11 | low | accept | R-05-05: `requires-python = ">=3.12,<3.13"` makes pip refuse up front with a clear message instead of failing inside an OpenCascade build; the Docker path (no local Python) is documented in `README.md` §Docker; L23 records the decision | closed |
| T-05-17 | Repudiation | `docs/architecture/decision_log.md` (L23) | low | mitigate | `980f343` +55 / −0 (same numstat query as T-05-13) | closed |
| T-05-18 | Repudiation | `.planning/STATE.md` recording evidence | medium | mitigate | `STATE.md:177`–`:178` cite exactly the two runs that exist (35963114939, 36088409707) and nothing else; this phase's own squash-commit run is recorded only after `make pr.land` prints it (D-07) | closed |
| T-05-19 | Tampering | `.planning/STATE.md` structure | low | mitigate | One scoped edit: the old blocker bullet is gone and the `(Resolved in Phase 5: …)` note stands at `STATE.md:176` with its continuation lines intact; 05-05's `<verify>` and 05-VERIFICATION SC-4 both re-checked it | closed |
| T-05-06-01 | Tampering | `scripts/pr_land.py` `message_refusals` | high | mitigate | `pr_land.py:248` `find_skip_tokens(subject + "\n\n" + body)` — no cut on PR text; `::test_message_refusals_checks_the_whole_body_even_below_a_git_cut_line` (:431) and `::test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body` (:681, asserts no `gh pr merge` call); 05-VERIFICATION re-ran the reproduction and 05-REVIEW (clean) confirmed CR-01 closed | closed |
| T-05-06-02 | Tampering | `scripts/skip_tokens.py` `main` on `-m`/`-F` commits | medium | mitigate | `skip_tokens.py:101` `editor_ran = os.environ.get("GIT_EDITOR") != ":"` — the cut applies only then; `::test_hook_without_an_editor_refuses_a_token_below_a_cut_line` (:160); a real refused `git commit -m` recorded in `05-06-SUMMARY.md` | closed |
| T-05-06-03 | Tampering | `main` in an editor session without `-v` | low | accept | R-05-06: filed as `must` debt — `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` with its `INDEX.md` row and trigger; backstops are T-05-11 (wall), T-05-07 (run-less head refused) and D-03 (a branch commit's message never becomes `main`'s) | closed |
| T-05-06-04 | Spoofing | `GIT_EDITOR` read by the hook | low | accept | R-05-07: git sets `GIT_EDITOR=:` for commit hooks itself, overriding the caller's value (githooks(5), cited at `skip_tokens.py:90`–`:93`; probe table in the debt file); outside git, setting it only restores the pre-05-06 cut, never a wider bypass than `--no-verify` (T-05-02) | closed |
| T-05-06-05 | Denial of Service | hook over-match on `git commit -v -m` | low | accept | R-05-08: refusing there is the documented safe over-match (`skip_tokens.py:97`, module docstring); the author rewords | closed |
| T-05-06-06 | Tampering | PR title/body reaching a shell | low | mitigate | Unchanged from T-05-08: `pr_land.py:514` argv list, no `shell=` | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-05-01 | T-05-02 | Local hooks are advisory by design; the ruleset on `main` and `make pr.land` refuse a run-less head, verified live and by test | Plan 05-01 threat model (plan approved by the human) | 2026-09-25 |
| R-05-02 | T-05-20 | The ruleset cannot see the squash text or the post-merge run; §8 names `make pr.land` as the only sanctioned path and a run-less commit is visible in the Actions list | Plan 05-02 threat model | 2026-09-25 |
| R-05-03 | T-05-24 | Only an admin can change the ruleset; `pr.land` keeps its own checks so the path stays exact without the wall; removal is D-12's documented reversal | Plan 05-03 threat model | 2026-09-25 |
| R-05-04 | T-05-15 | No dependency added or changed in the phase; `requirements.txt` untouched | Plan 05-04 threat model | 2026-09-25 |
| R-05-05 | T-05-16 | pip now refuses 3.10/3.11 up front instead of failing minutes into a build; Docker documented as the no-local-Python path (L23) | Plan 05-04 threat model (D-09, human decision) | 2026-09-25 |
| R-05-06 | T-05-06-03 | Content-indistinguishable from git's own `-v` buffer; filed as `must` debt with a named trigger; three independent backstops keep a run-less commit off `main` | Plan 05-06 threat model (gap closure, plan approved by the human) | 2026-09-25 |
| R-05-07 | T-05-06-04 | git overrides `GIT_EDITOR` for commit hooks itself; outside git the variable only restores the earlier cut, never more than `--no-verify` already allows | Plan 05-06 threat model | 2026-09-25 |
| R-05-08 | T-05-06-05 | Over-matching is the documented safe direction for a skip-token check; cost is a reworded message | Plan 05-06 threat model | 2026-09-25 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-25 | 30 | 30 | 0 | /gsd-secure-phase 5 orchestrator (L1 short-circuit; no auditor agent; two live GitHub read-backs) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-25
