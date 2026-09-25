---
phase: "06"
slug: "address-tech-debt-merge-gate-solid-cache"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-25"
---

# Phase 06 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register source: the `<threat_model>` blocks of `06-01` through `06-04-PLAN.md` (authored at
plan time, 13 rows). No SUMMARY carried a `## Threat Flags` section. ASVS level 1 with
`register_authored_at_plan_time: true` and every row closed at grep depth took the workflow's
short-circuit: no auditor agent was spawned; the evidence column below is what the
orchestrator checked in the tree at `b475d36` (HEAD after all four plans and the validation
audit). Line numbers refer to that tree. No row in this phase is rated above `medium`, so
`threats_open` (open rows at or above `workflow.security_block_on = high`) is 0 by construction;
the rows were nevertheless each verified rather than waved through.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| one request's export → the worker's cached solid | `_build_cached` shares one `cq.Solid` across every request for the same `GearParams` routed to that worker (Phase 2 D-07 affinity) | a mutable OCCT solid |
| `build()` result → a caller outside `_LOCK` | the cached object is read after the lock is released | the same solid, unlocked |
| commit message → commit-msg hook | any contributor or tool writes the message; git hands the hook the unprocessed buffer, including `-v`'s appended diff | commit message bytes |
| hook verdict → a PR head's checks | a token that passes the hook leaves a PR head with zero recorded checks | the skip token |
| GitHub Actions run/jobs JSON → `head_refusals` | `gh api` output decides whether `pr.land` merges | run `conclusion`, job names and conclusions |
| local `required-jobs.txt` → the verdict | the list is read from whatever checkout `pr.land` runs in | job names |
| `ci.yml` text → the drift test | the test is the only guard that the list names what GitHub reports | job ids and `name:` overrides |
| GitHub API responses → `pr.land`'s printed diagnosis | the runs poll and the squash-commit read decide which report a human acts on | run list, commit URL and message |
| squash sha → `gh api` argv | the sha, read from `gh pr view`, becomes part of an argv element | a 40-hex sha |
| docs and decision log → the next agent's model of the gate | a claim that over-states what `pr.land` proves weakens whoever relies on it | prose about the wall and the tool |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-06-01 | Tampering | `model._write_export` mutating the shared cached solid | medium | mitigate | `src/spur/model.py:281` `shape.copy().exportStl(...)` inside `_write_export` (:267), with the L24 comment at :272–:279 stating why the copy and not `Clean_s`; `_reset_solid_cache` is absent from `tests/conftest.py`; `tests/test_model.py::test_exporting_leaves_the_cached_solid_exact` (:116) and `::test_an_stl_export_matches_a_first_export_whatever_came_before` (:128) go red on regression | closed |
| T-06-02 | Denial of Service | the copy's extra time and memory per STL export | low | accept | R-06-01: measured and recorded in L24 (`docs/architecture/decision_log.md:608`; +1.4 to +17.6 ms per export at :643, 1270.7 / 1267.6 MiB peak RSS at :647) against `SPUR_BUILD_TIMEOUT=30s` and the L17 memory ceiling | closed |
| T-06-03 | Repudiation | the debt record naming the wrong fixing commit | low | mitigate | `docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` reads `Resolved in: 655ec52`; `git show --name-only 655ec52` = `src/spur/model.py tests/conftest.py tests/test_model.py`; `git merge-base --is-ancestor 655ec52 f17bda0^` holds (the mover follows the fix); the same proof re-run by `/gsd-validate-phase` (06-VALIDATION.md audit) | closed |
| T-06-04 | Tampering | `scripts/skip_tokens.py` `main` — a token hidden below a hand-typed cut line | medium | mitigate | No cut-line regex, no `GIT_EDITOR` read and no `message_to_check` remain in `scripts/skip_tokens.py` (the words appear only in the docstring/comments at :19–:22, :53, :71–:75 explaining their absence); `main` hands the raw buffer to `find_skip_tokens` (:79); `tests/test_skip_tokens.py::test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says` (:115) for `vi`, unset and `:`; the scratch-clone editor-session commit was refused with HEAD unmoved (06-02-SUMMARY, Task 1 verification) | closed |
| T-06-05 | Denial of Service | refusal of a `git commit -v` whose appended diff names a token | low | accept | R-06-02: the refusal names `line N: 'token'` (:91) and says `commit without -v` (:98–:99); `::test_hook_refuses_a_token_in_the_appended_commit_v_diff_and_says_to_commit_without_v` (:137); `docs/HOW_TO_DEVELOP.md:128` §6 carries the same line in Russian; `git config --get commit.verbose` read empty at planning | closed |
| T-06-06 | Elevation of Privilege | `git commit --no-verify` skipping the hook | low | accept | R-06-03: unchanged from T-05-02 / R-05-01 (`05-SECURITY.md:47`, `:87`) — the ruleset on `main` refuses a head without green required checks, `make pr.land` refuses a run-less head, and after Phase 5 D-03 a branch commit's message never becomes `main`'s | closed |
| T-06-07 | Elevation of Privilege | `head_refusals` admitting a run that failed on an unlisted job | medium | mitigate | `scripts/pr_land.py:295` refuses `conclusion != "success"` inside `head_refusals` (:259), naming the conclusion and the run URL, with the per-job loop kept; `tests/test_pr_land.py::test_head_refusals_a_failed_run_is_refused_even_when_every_listed_job_is_green` (:386), `::test_check_head_names_the_run_conclusion_of_recorded_run_36116930241` (:419); live read-only `check_head` on `73535a2` returned three refusals (06-03-SUMMARY, Task 1 verification) | closed |
| T-06-08 | Tampering | a stale local `required-jobs.txt` | low | mitigate | `docs/HOW_TO_DEVELOP.md:183` §8: run from an up-to-date `main` (`git switch main && git pull --ff-only`); a job the list does not know still fails the run, which T-06-07 refuses; a removed job fails closed as a `missing` refusal (`::test_head_refusals_empty_jobs_list_reports_every_required_job_missing` :360) | closed |
| T-06-09 | Denial of Service | a `name:` override desyncing the list from what GitHub reports | low | mitigate | `tests/test_pr_land.py::test_required_jobs_file_matches_ci_yml_job_names` (:269) compares effective names; `::test_a_job_name_override_moves_the_derived_required_set` (:277) proves a rename moves the derived set | closed |
| T-06-10 | Repudiation | `land` step 5 naming a cause it did not observe | low | mitigate | `no_run_report` (`scripts/pr_land.py:372`) reads `repos/{owner}/{repo}/commits/<sha>` (:399) and calls `find_skip_tokens(message)` (:409) before naming any token; one `FakeRunner` case per branch: `::test_land_reports_the_last_read_error_when_every_poll_failed` (:746), `::test_land_reports_no_run_observed_with_the_actions_url_when_reads_succeeded` (:768), `::test_land_names_a_skip_token_only_after_reading_it_from_the_squash_commit` (:788), `::test_no_run_report_a_failed_commit_read_is_the_last_error` (:830); live probe against `b72b0e1` and `20b63e4` (06-04-SUMMARY, Task 1 verification) | closed |
| T-06-11 | Tampering | the squash sha in the new `gh api` argv | low | mitigate | One process boundary: `pr_land.py:576` `subprocess.run(argv, capture_output=True, text=True, check=False)`; `shell=` appears nowhere in the module; the sha comes from `gh pr view --json mergeCommit --jq .mergeCommit.oid` (:495) and is interpolated into a single argv element (:399) | closed |
| T-06-12 | Information Disclosure | printing the squash commit's tokens | low | accept | R-06-04: only the tokens `find_skip_tokens` matched are printed (:409 onward); the squash commit's message is already public on a public repository | closed |
| T-06-13 | Elevation of Privilege | docs over-claiming that `pr.land` alone keeps the merged tree equal to the checked tree | low | mitigate | `scripts/pr_land.py:16` module docstring: `--match-head-commit` pins the head, not the base; `docs/HOW_TO_DEVELOP.md:219` §8 names the ruleset's up-to-date policy (D-12, no bypass actors) as what carries the read-to-merge window; L25 (`decision_log.md:674`) amends L22 the same way; the D-07 AST gate shows the commit changed no code | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-06-01 | T-06-02 | The copy costs +1.4 to +17.6 ms and +3.2 to +7.7 MiB per STL export (measured, L24); an in-place `Clean_s` was rejected because it leaves the cached solid meshed for the whole export window (D-08 amendment (b)) | Plan 06-01 threat model (plan approved by the human) | 2026-09-25 |
| R-06-02 | T-06-05 | A `git commit -v` whose appended diff names a token is refused; the refusal names the line and the way out, §6 says the same, and `commit.verbose` is unset here (D-02) | Plan 06-02 threat model (plan approved by the human) | 2026-09-25 |
| R-06-03 | T-06-06 | Local hooks are advisory by design; the ruleset on `main` and `make pr.land` refuse a run-less head — unchanged from R-05-01 | Plan 06-02 threat model (plan approved by the human) | 2026-09-25 |
| R-06-04 | T-06-12 | Only matched tokens are printed, from a message that is already public | Plan 06-04 threat model (plan approved by the human) | 2026-09-25 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-25 | 13 | 13 | 0 | execute-phase orchestrator (verify:post secure-phase hook; ASVS 1 short-circuit, no auditor spawned) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-25
