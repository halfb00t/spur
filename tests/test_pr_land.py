"""Tests for `scripts.pr_land` -- the whole `make pr.land PR=N` path, offline, against
recorded `gh` JSON.

Run as `.venv/bin/python -m pytest tests/test_pr_land.py -q` **from the repository
root** -- the `-m` form puts the repo root on `sys.path`, the same constraint
`tests/test_bench.py` and `tests/test_skip_tokens.py` document for `bench` and
`scripts`.

Every literal fixture below traces to a real, read-only `gh`/`gh api` call made against
this repository on 2026-09-25 (RESEARCH.md's "Verified Live State", or a call made
directly during this plan's own execution) -- a comment above each names the call.
Per-case variants change **values** (state, a PR number, conclusions, ids), never
**shape**. Every test except the drift test (`test_required_jobs_file_matches_ci_yml_job_ids`)
is independent of `.github/workflows/required-jobs.txt`'s current contents: pure tests
pass `required`/`REQUIRED` explicitly, and `land()` tests use only `test (3.12)`,
`vendor-bundle` and `image` -- the jobs required both now and after Plan 05-04 drops the
`test (3.10)` line.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from scripts.pr_land import (
    PullRequest,
    WorkflowRun,
    check_head,
    head_refusals,
    land,
    message_refusals,
    newest_run,
    parse_compare,
    parse_jobs,
    parse_pull_request,
    parse_runs,
    pr_refusals,
    required_jobs,
    squash_subject,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def cp(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    """A `subprocess.CompletedProcess` stand-in, `args` unused by anything under test."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    """Answers `gh`/`git` calls from handlers registered with `.on(substring, ...)`,
    matched by substring against the joined argv, first-registered-first-matched.
    Records every argv it was called with. A handler may carry more than one response
    -- each call pops the next one, and the last response repeats once the queue is
    exhausted (the poll test's "no run, then a run" shape)."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self._handlers: list[tuple[str, list[subprocess.CompletedProcess[str]]]] = []

    def on(self, substring: str, *responses: subprocess.CompletedProcess[str]) -> FakeRunner:
        self._handlers.append((substring, list(responses)))
        return self

    def replace(self, substring: str, *responses: subprocess.CompletedProcess[str]) -> FakeRunner:
        """Swap the queue for every handler whose registered substring starts with
        `substring` -- used by the poll-timeout/local-follow-up variant tests to
        override one leg of `_happy_runner()` without rebuilding the whole thing."""
        self._handlers = [
            (sub, list(responses)) if sub.startswith(substring) else (sub, resp)
            for sub, resp in self._handlers
        ]
        return self

    def __call__(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        joined = " ".join(argv)
        for substring, responses in self._handlers:
            if substring in joined:
                if len(responses) > 1:
                    return responses.pop(0)
                return responses[0]
        raise AssertionError(f"FakeRunner: no handler registered for {argv!r}")


# --- recorded shapes -----------------------------------------------------------------
# `gh pr view 3 --json number,state,baseRefName,headRefOid,headRefName,title,body`
# (2026-09-25). PR #3's real state is MERGED; the OPEN variants below change only
# `state` and `number` for the happy-path/refusal tests -- same shape, not literally
# recorded as OPEN (PR #3 itself was already merged by the time this plan ran).
PR3_HEAD_SHA = "2c4b544c63ff2f4b27e7554efa380fdebfbeb6ae"
PR3_VIEW_JSON = (
    '{"number":3,"state":"MERGED","baseRefName":"main",'
    f'"headRefOid":"{PR3_HEAD_SHA}",'
    '"headRefName":"gsd/phase-04-typed-derived-dimensions-contract",'
    '"title":"Phase 4: Typed Derived-Dimensions Contract",'
    '"body":"## Summary\\n\\nTyped DerivedDimensions contract.\\n"}'
)

# `gh api repos/halfb00t/spur/actions/workflows/ci.yml/runs?head_sha=2c4b544...`
# (2026-09-25): one completed, successful run.
PR3_RUNS_JSON = (
    '[{"id":36088409707,"status":"completed","conclusion":"success",'
    '"html_url":"https://github.com/halfb00t/spur/actions/runs/36088409707"}]'
)

# `gh api repos/halfb00t/spur/actions/runs/36088409707/jobs` (2026-09-25): all four
# jobs, all `success`.
PR3_JOBS_JSON = (
    '[{"name":"vendor-bundle","status":"completed","conclusion":"success"},'
    '{"name":"image","status":"completed","conclusion":"success"},'
    '{"name":"test (3.12)","status":"completed","conclusion":"success"},'
    '{"name":"test (3.10)","status":"completed","conclusion":"success"}]'
)

# `gh api repos/halfb00t/spur/compare/main...2c4b544...` (2026-09-25, this plan's own
# execution): PR #3's real head sits one commit behind main (`ahead_by: 32,
# behind_by: 1`) -- the live probe in this plan's `<verify>` block re-reads this.
PR3_COMPARE_JSON = '{"ahead_by":32,"behind_by":1}'

# A synthetic "current, ahead" compare, used only for the happy-path fixtures below
# (a synthetic OPEN PR, not literally PR #3's real state) -- same shape as
# PR3_COMPARE_JSON, different values.
CURRENT_COMPARE_JSON = '{"ahead_by":3,"behind_by":0}'

# `gh api repos/halfb00t/spur/actions/runs/35993984796/jobs` (RESEARCH.md, PR #2's
# last real run): `test (3.10)` failed, the other three succeeded.
RED_RUN_JOBS_JSON = (
    '[{"name":"vendor-bundle","status":"completed","conclusion":"success"},'
    '{"name":"image","status":"completed","conclusion":"success"},'
    '{"name":"test (3.10)","status":"completed","conclusion":"failure"},'
    '{"name":"test (3.12)","status":"completed","conclusion":"success"}]'
)

# `gh pr view 2 --json ...statusCheckRollup...` (RESEARCH.md "Verified Live State"):
# a MERGED PR whose head carried a skip token -- zero recorded checks, not a red run.
PR2_HEAD_SHA = "20b63e453a3cd0c72e5d0f995a107a238c652a90"
PR2_VIEW_JSON = (
    '{"number":2,"state":"MERGED","baseRefName":"main",'
    f'"headRefOid":"{PR2_HEAD_SHA}",'
    '"headRefName":"gsd/phase-03-structured-logging",'
    '"title":"Phase 3: Structured Logging","body":"ship phase 3 [ci skip]"}'
)

# `gh api repos/halfb00t/spur/actions/workflows/ci.yml/runs?head_sha=20b63e4...`
# (2026-09-25, this plan's own execution): zero runs -- the skip token on PR #2's own
# head suppressed the run entirely, not a red run (RESEARCH.md's own "PR #2's own
# recorded shape" -- `statusCheckRollup: []`).
PR2_RUNS_JSON = "[]"

REQUIRED = frozenset({"test (3.12)", "vendor-bundle", "image"})

# A compare result that is neither behind nor identical -- the neutral value the Task 1
# tests use for `head_refusals`, which now requires a `compare` argument as of Task 2.
NOT_BEHIND = (1, 0)


# --- required_jobs() -------------------------------------------------------------


def test_required_jobs_reads_non_comment_non_blank_lines(tmp_path: Path) -> None:
    """`#` lines, blank lines and names with spaces (`test (3.12)`) -- the exact
    shape `.github/workflows/required-jobs.txt` uses."""
    path = tmp_path / "required-jobs.txt"
    path.write_text(
        "# a header comment\n\ntest (3.12)\nvendor-bundle\n\n# another comment\nimage\n",
        encoding="utf-8",
    )
    assert required_jobs(path) == frozenset({"test (3.12)", "vendor-bundle", "image"})


def test_required_jobs_file_matches_ci_yml_job_ids() -> None:
    """D-05: `required_jobs()` must equal the job ids `ci.yml` actually runs, or a PR
    could be judged green on a job GitHub never runs. Job ids are the two-space-indented
    keys directly under `jobs:`; the `test` id expands to `test ({v})` for each version
    in its `python: [...]` matrix list -- `test` itself must appear among the derived
    ids, or the expansion below would silently match nothing."""
    ci_yml = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    jobs_section = ci_yml.split("\njobs:\n", 1)[1]
    job_ids = re.findall(r"^  ([a-zA-Z][\w-]*):\s*$", jobs_section, re.MULTILINE)
    assert "test" in job_ids

    matrix_match = re.search(r"python:\s*\[([^\]]*)\]", jobs_section)
    assert matrix_match is not None, "no python matrix found in ci.yml"
    versions = [v.strip().strip('"') for v in matrix_match.group(1).split(",")]

    derived = {
        name
        for job_id in job_ids
        for name in ([f"test ({v})" for v in versions] if job_id == "test" else [job_id])
    }
    assert required_jobs() == frozenset(derived)


# --- pure decisions ----------------------------------------------------------------


def test_squash_subject_is_title_and_pr_number() -> None:
    pr = parse_pull_request(PR3_VIEW_JSON)
    assert squash_subject(pr) == "Phase 4: Typed Derived-Dimensions Contract (#3)"


def test_pr_refusals_empty_for_an_open_pr_based_on_main() -> None:
    pr = PullRequest(
        number=99, state="OPEN", base="main", head_sha="abc123",
        head_branch="gsd/phase-99", title="t", body="b",
    )
    assert pr_refusals(pr) == []


def test_pr_refusals_names_the_state_for_a_merged_pr() -> None:
    pr = parse_pull_request(PR2_VIEW_JSON)
    refusals = pr_refusals(pr)
    assert len(refusals) == 1
    assert "MERGED" in refusals[0]


def test_pr_refusals_names_the_base_for_a_pr_not_targeting_main() -> None:
    pr = PullRequest(
        number=5, state="OPEN", base="develop", head_sha="abc",
        head_branch="feature/x", title="t", body="b",
    )
    refusals = pr_refusals(pr)
    assert len(refusals) == 1
    assert "develop" in refusals[0]


def test_newest_run_picks_the_highest_id_regardless_of_order() -> None:
    older = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u1")
    newer = WorkflowRun(id=2, status="completed", conclusion="success", html_url="u2")
    assert newest_run([older, newer]) is newer
    assert newest_run([newer, older]) is newer


def test_newest_run_of_empty_list_is_none() -> None:
    assert newest_run([]) is None


def test_head_refusals_empty_when_every_required_job_succeeded() -> None:
    run = newest_run(parse_runs(PR3_RUNS_JSON))
    jobs = parse_jobs(PR3_JOBS_JSON)
    assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED) == []


def test_head_refusals_no_run_names_the_sha() -> None:
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, None, [], REQUIRED)
    assert len(refusals) == 1
    assert PR3_HEAD_SHA in refusals[0]


def test_head_refusals_run_in_progress_names_still_running_and_url() -> None:
    run = WorkflowRun(id=1, status="in_progress", conclusion=None, html_url="https://x/1")
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, [], REQUIRED)
    assert len(refusals) == 1
    assert "still running" in refusals[0]
    assert "https://x/1" in refusals[0]


def test_head_refusals_empty_jobs_list_reports_every_required_job_missing() -> None:
    """PR #2's own recorded shape: `statusCheckRollup: []` -- zero jobs at all, not
    one failing -- must refuse the same as a red job."""
    run = WorkflowRun(id=1, status="completed", conclusion="success", html_url="u")
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, [], REQUIRED)
    assert len(refusals) == len(REQUIRED)
    assert all("missing" in r for r in refusals)


def test_head_refusals_one_red_job_names_it_and_its_conclusion() -> None:
    """Run 35993984796's own recorded shape: `test (3.10)` failed. `test (3.12)` is
    the job in `REQUIRED` here, so put the failure there instead -- same shape."""
    run = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u")
    jobs = [
        {"name": "test (3.12)", "conclusion": "failure"},
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED)
    assert len(refusals) == 1
    assert "test (3.12)" in refusals[0]
    assert "failure" in refusals[0]


def test_head_refusals_matches_the_recorded_red_run_verbatim() -> None:
    """The literal shape run 35993984796 returned, unmodified -- a required set that
    includes `test (3.10)` (this task's pre-D-09 set) catches the one red job."""
    jobs = parse_jobs(RED_RUN_JOBS_JSON)
    run = WorkflowRun(id=35993984796, status="completed", conclusion="failure", html_url="u")
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED | {"test (3.10)"})
    assert len(refusals) == 1
    assert "test (3.10)" in refusals[0]
    assert "failure" in refusals[0]


def test_head_refusals_a_required_job_cancelled_or_skipped_is_refused() -> None:
    run = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u")
    for bad_conclusion in ("cancelled", "skipped"):
        jobs = [
            {"name": "test (3.12)", "conclusion": bad_conclusion},
            {"name": "vendor-bundle", "conclusion": "success"},
            {"name": "image", "conclusion": "success"},
        ]
        refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED)
        assert len(refusals) == 1
        assert bad_conclusion in refusals[0]


# --- compare: behind / identical / ahead --------------------------------------------


def test_head_refusals_behind_main_names_behind_and_says_rebase() -> None:
    run = newest_run(parse_runs(PR3_RUNS_JSON))
    jobs = parse_jobs(PR3_JOBS_JSON)
    refusals = head_refusals(PR3_HEAD_SHA, (5, 2), run, jobs, REQUIRED)
    assert len(refusals) == 1
    assert "behind" in refusals[0]
    assert "rebase onto main" in refusals[0].lower()


def test_head_refusals_identical_to_main_refused_as_nothing_to_merge() -> None:
    run = newest_run(parse_runs(PR3_RUNS_JSON))
    jobs = parse_jobs(PR3_JOBS_JSON)
    refusals = head_refusals(PR3_HEAD_SHA, (0, 0), run, jobs, REQUIRED)
    assert len(refusals) == 1
    assert "nothing to merge" in refusals[0]


def test_head_refusals_ahead_not_behind_no_compare_refusal() -> None:
    run = newest_run(parse_runs(PR3_RUNS_JSON))
    jobs = parse_jobs(PR3_JOBS_JSON)
    assert head_refusals(PR3_HEAD_SHA, (3, 0), run, jobs, REQUIRED) == []


def test_head_refusals_several_problems_at_once_prints_both_lines() -> None:
    """Behind, and one red job, together -- both refusal lines present (the third
    line, a skip token, is `message_refusals`' own concern -- tested combined at the
    `land()` level below)."""
    run = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u")
    jobs = [
        {"name": "test (3.12)", "conclusion": "failure"},
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    refusals = head_refusals(PR3_HEAD_SHA, (5, 2), run, jobs, REQUIRED)
    assert len(refusals) == 2
    assert any("behind" in r for r in refusals)
    assert any("test (3.12)" in r for r in refusals)


# --- ordering: several runs for one sha ----------------------------------------------


def test_ordering_newer_failed_run_refuses_even_with_an_older_green_run() -> None:
    older_green = WorkflowRun(id=1, status="completed", conclusion="success", html_url="u1")
    newer_red = WorkflowRun(id=2, status="completed", conclusion="failure", html_url="u2")
    jobs = [{"name": name, "conclusion": "failure"} for name in REQUIRED]
    picked = newest_run([older_green, newer_red])
    assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, picked, jobs, REQUIRED) != []


def test_ordering_older_failed_run_does_not_block_a_newer_green_one() -> None:
    older_red = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u1")
    newer_green = WorkflowRun(id=2, status="completed", conclusion="success", html_url="u2")
    jobs = [{"name": name, "conclusion": "success"} for name in REQUIRED]
    picked = newest_run([older_red, newer_green])
    assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, picked, jobs, REQUIRED) == []


def test_ordering_shuffled_run_order_never_changes_the_verdict() -> None:
    older_red = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u1")
    newer_green = WorkflowRun(id=2, status="completed", conclusion="success", html_url="u2")
    jobs = [{"name": name, "conclusion": "success"} for name in REQUIRED]
    for run_list in ([older_red, newer_green], [newer_green, older_red]):
        picked = newest_run(run_list)
        assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, picked, jobs, REQUIRED) == []


def test_head_refusals_shuffled_job_order_never_changes_the_verdict() -> None:
    run = WorkflowRun(id=1, status="completed", conclusion="success", html_url="u")
    jobs = [{"name": name, "conclusion": "success"} for name in sorted(REQUIRED)]
    reversed_jobs = list(reversed(jobs))
    assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED) == []
    assert head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, reversed_jobs, REQUIRED) == []


# --- message_refusals() (the squash subject/body skip-token check) -------------------


def test_message_refusals_empty_for_a_clean_subject_and_body() -> None:
    assert message_refusals("feat(05-02): add the merge gate", "A clean PR body.\n") == []


def test_message_refusals_empty_body_is_no_refusal() -> None:
    assert message_refusals("feat(05-02): add the merge gate", "") == []


def test_message_refusals_token_in_the_title_is_found_naming_it() -> None:
    refusals = message_refusals("fix: bug [skip ci]", "clean body")
    assert len(refusals) == 1
    assert "[skip ci]" in refusals[0]
    assert "edit the pr title or body" in refusals[0].lower()


def test_message_refusals_token_in_a_later_paragraph_of_the_body_is_found() -> None:
    """The `6fce500` shape (tests/test_skip_tokens.py's own fixture): a clean
    subject, a token mentioned in prose two paragraphs down."""
    body = (
        "This commit changes nothing about the pipeline.\n\n"
        "No [ci skip] on purpose -- this one should run.\n"
    )
    refusals = message_refusals("docs(04): note on CI behaviour", body)
    assert len(refusals) == 1
    assert "[ci skip]" in refusals[0]


# --- parsers ------------------------------------------------------------------------


def test_parse_pull_request_reads_the_recorded_shape() -> None:
    pr = parse_pull_request(PR3_VIEW_JSON)
    assert pr == PullRequest(
        number=3, state="MERGED", base="main", head_sha=PR3_HEAD_SHA,
        head_branch="gsd/phase-04-typed-derived-dimensions-contract",
        title="Phase 4: Typed Derived-Dimensions Contract",
        body="## Summary\n\nTyped DerivedDimensions contract.\n",
    )


def test_parse_pull_request_raises_on_unparseable_output() -> None:
    with pytest.raises(ValueError, match="does not parse"):
        parse_pull_request("not json")


def test_parse_pull_request_raises_on_missing_field() -> None:
    with pytest.raises(ValueError, match="does not parse"):
        parse_pull_request('{"number": 3}')


def test_parse_runs_reads_the_recorded_shape() -> None:
    runs = parse_runs(PR3_RUNS_JSON)
    assert runs == [
        WorkflowRun(
            id=36088409707, status="completed", conclusion="success",
            html_url="https://github.com/halfb00t/spur/actions/runs/36088409707",
        )
    ]


def test_parse_runs_empty_array() -> None:
    assert parse_runs("[]") == []


def test_parse_jobs_reads_the_recorded_shape() -> None:
    jobs = parse_jobs(PR3_JOBS_JSON)
    assert {"name": "test (3.12)", "conclusion": "success"} in jobs
    assert len(jobs) == 4


def test_parse_compare_reads_the_recorded_shape() -> None:
    assert parse_compare(PR3_COMPARE_JSON) == (32, 1)


def test_parse_compare_raises_on_unparseable_output() -> None:
    with pytest.raises(ValueError, match="does not parse"):
        parse_compare("not json")


# --- check_head (the read-only network shell, faked) --------------------------------


def test_check_head_green_returns_no_refusals() -> None:
    runner = (
        FakeRunner()
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, PR3_JOBS_JSON))
    )
    assert check_head(PR3_HEAD_SHA, runner, REQUIRED) == []


def test_check_head_a_failed_runs_read_is_a_refusal_showing_stderr() -> None:
    runner = (
        FakeRunner()
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(1, "", "gh: rate limited"))
    )
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1
    assert "rate limited" in refusals[0]


def test_check_head_unparseable_runs_output_is_a_refusal() -> None:
    runner = (
        FakeRunner()
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, "not json"))
    )
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1


def test_check_head_a_failed_compare_read_is_a_refusal_showing_stderr() -> None:
    runner = FakeRunner().on(f"compare/main...{PR3_HEAD_SHA}", cp(1, "", "gh: not found"))
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1
    assert "not found" in refusals[0]


def test_check_head_unparseable_compare_output_is_a_refusal() -> None:
    runner = FakeRunner().on(f"compare/main...{PR3_HEAD_SHA}", cp(0, "not json"))
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1


def test_check_head_zero_runs_refuses_naming_no_ci_yml_run_and_the_sha() -> None:
    """PR #2's own live shape (this plan's own execution, 2026-09-25): zero `ci.yml`
    runs for a head sha -- a skip token on the head commit suppressed the run
    entirely, the same shape a never-triggered workflow would leave."""
    runner = (
        FakeRunner()
        .on(f"compare/main...{PR2_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR2_HEAD_SHA}", cp(0, PR2_RUNS_JSON))
    )
    refusals = check_head(PR2_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1
    assert "no ci.yml run" in refusals[0]
    assert PR2_HEAD_SHA in refusals[0]


# The live, read-only check that `check_head` on PR #3's real head returns exactly one
# `behind` refusal (must_haves truth 8) is deliberately NOT a pytest test here -- it
# needs network and an authenticated `gh`, which `make verify`/`make test` must never
# require. It is this plan's own `<verify>` block, run once as a standalone command
# (05-02-PLAN.md Task 2 `<verify>`), not part of the offline suite.


# --- land(): the whole path, offline -------------------------------------------------


def _happy_runner(pr_json: str = PR3_VIEW_JSON.replace('"MERGED"', '"OPEN"')) -> FakeRunner:
    """An OPEN PR based on main, a clean tree, a current (not behind) compare, one
    green completed run, a successful merge, the squash commit's oid, and -- for the
    squash sha -- no run on the first poll, one on the second (the poll-success
    shape)."""
    return (
        FakeRunner()
        .on("pr view 3 --json number", cp(0, pr_json))
        .on("git diff --quiet", cp(0))
        .on("git diff --cached --quiet", cp(0))
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, PR3_JOBS_JSON))
        .on("pr merge 3 --squash", cp(0))
        .on("pr view 3 --json mergeCommit", cp(0, "deadbeef1234"))
        .on(
            "runs?head_sha=deadbeef1234",
            cp(0, "[]"),
            cp(
                0,
                '[{"id":1,"status":"completed","conclusion":"success",'
                '"html_url":"https://github.com/halfb00t/spur/actions/runs/1"}]',
            ),
        )
        .on("git switch main", cp(0))
        .on("git pull --ff-only origin main", cp(0))
        .on(
            "rev-parse --verify --quiet refs/heads/gsd/phase-04",
            cp(0, PR3_HEAD_SHA),
        )
        .on("git branch -D gsd/phase-04", cp(0))
    )


def test_land_happy_path_returns_0_and_prints_the_run_url() -> None:
    runner = _happy_runner()
    sleeps: list[float] = []
    assert land(3, runner, sleep=sleeps.append) == 0
    assert sleeps == [5.0]  # exactly one sleep before the second poll finds the run
    merge_calls = [c for c in runner.calls if c[:3] == ["gh", "pr", "merge"]]
    assert merge_calls == [
        [
            "gh", "pr", "merge", "3", "--squash", "--match-head-commit", PR3_HEAD_SHA,
            "--subject", "Phase 4: Typed Derived-Dimensions Contract (#3)",
            "--body", "## Summary\n\nTyped DerivedDimensions contract.\n",
        ]
    ]
    assert not any("--delete-branch" in c for c in runner.calls)
    assert ["git", "switch", "main"] in runner.calls
    assert ["git", "pull", "--ff-only", "origin", "main"] in runner.calls
    assert ["git", "branch", "-D", "gsd/phase-04-typed-derived-dimensions-contract"] in runner.calls


def test_land_poll_timeout_reports_merged_but_no_run(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _happy_runner().replace("runs?head_sha=deadbeef", cp(0, "[]"))
    sleeps: list[float] = []
    result = land(3, runner, attempts=3, interval_s=1.0, sleep=sleeps.append)
    assert result == 1
    assert sleeps == [1.0, 1.0]  # attempts - 1
    out = capsys.readouterr().out
    assert "IS merged" in out
    assert "deadbeef1234" in out
    assert "no ci.yml run appeared" in out


def test_land_local_tip_differs_keeps_the_branch(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _happy_runner().replace(
        "rev-parse --verify", cp(0, "0123456789abcdef0123456789abcdef01234567")
    )
    assert land(3, runner, sleep=lambda _: None) == 0
    assert not any(c[:3] == ["git", "branch", "-D"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "differs from the merged head" in out


def test_land_local_branch_absent_no_delete_no_error() -> None:
    runner = _happy_runner().replace("rev-parse --verify", cp(1))
    assert land(3, runner, sleep=lambda _: None) == 0
    assert not any(c[:3] == ["git", "branch", "-D"] for c in runner.calls)


def test_land_pr_not_open_refuses_before_any_other_call(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runner = FakeRunner().on("pr view 2 --json number", cp(0, PR2_VIEW_JSON))
    result = land(2, runner, sleep=lambda _: None)
    assert result == 1
    assert len(runner.calls) == 1  # nothing else was ever called
    out = capsys.readouterr().out
    assert "MERGED" in out
    assert "nothing was merged" in out


def test_land_dirty_tree_refuses_no_merge_call(capsys: pytest.CaptureFixture[str]) -> None:
    runner = (
        FakeRunner()
        .on("pr view 3 --json number", cp(0, PR3_VIEW_JSON.replace('"MERGED"', '"OPEN"')))
        .on("git diff --quiet", cp(1))
    )
    result = land(3, runner, sleep=lambda _: None)
    assert result == 1
    assert not any(c[:3] == ["gh", "pr", "merge"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "nothing was merged" in out


def test_land_unparseable_pr_read_refuses_no_merge_call(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runner = FakeRunner().on("pr view 3 --json number", cp(0, "not json"))
    result = land(3, runner, sleep=lambda _: None)
    assert result == 1
    assert not any(c[:3] == ["gh", "pr", "merge"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "nothing was merged" in out


def test_land_gh_pr_merge_failure_returns_1_no_poll_no_follow_up(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runner = (
        FakeRunner()
        .on("pr view 3 --json number", cp(0, PR3_VIEW_JSON.replace('"MERGED"', '"OPEN"')))
        .on("git diff --quiet", cp(0))
        .on("git diff --cached --quiet", cp(0))
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, CURRENT_COMPARE_JSON))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, PR3_JOBS_JSON))
        .on("pr merge 3 --squash", cp(1, "", "gh: PR is not mergeable"))
    )
    result = land(3, runner, sleep=lambda _: None)
    assert result == 1
    assert not any(c[:2] == ["git", "switch"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "gh pr view 3" in out


def test_land_several_problems_at_once_prints_all_then_one_nothing_was_merged_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Behind, one red job, and a skip token in the body -- all three refusal lines
    printed together, then a single trailing `nothing was merged` line; no merge call."""
    pr_json = json.dumps(
        {
            "number": 3, "state": "OPEN", "baseRefName": "main",
            "headRefOid": PR3_HEAD_SHA,
            "headRefName": "gsd/phase-04-typed-derived-dimensions-contract",
            "title": "Phase 4: Typed Derived-Dimensions Contract",
            "body": "clean intro\n\nDon't add [ci skip] here.\n",
        }
    )
    behind_compare = '{"ahead_by":5,"behind_by":2}'
    red_jobs = json.dumps(
        [
            {"name": "test (3.12)", "status": "completed", "conclusion": "failure"},
            {"name": "vendor-bundle", "status": "completed", "conclusion": "success"},
            {"name": "image", "status": "completed", "conclusion": "success"},
        ]
    )
    runner = (
        FakeRunner()
        .on("pr view 3 --json number", cp(0, pr_json))
        .on("git diff --quiet", cp(0))
        .on("git diff --cached --quiet", cp(0))
        .on(f"compare/main...{PR3_HEAD_SHA}", cp(0, behind_compare))
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, red_jobs))
    )
    result = land(3, runner, sleep=lambda _: None)
    assert result == 1
    out = capsys.readouterr().out
    assert "behind" in out
    assert "test (3.12)" in out
    assert "[ci skip]" in out
    assert out.count("nothing was merged") == 1
    assert not any(c[:3] == ["gh", "pr", "merge"] for c in runner.calls)
