"""Tests for `scripts.pr_land` -- the whole `make pr.land PR=N` path, offline, against
recorded `gh` JSON.

Run as `.venv/bin/python -m pytest tests/test_pr_land.py -q` **from the repository
root** -- the `-m` form puts the repo root on `sys.path`, the same constraint
`tests/test_bench.py` and `tests/test_skip_tokens.py` document for `bench` and
`scripts`.

Every fixture below traces to a real, read-only `gh`/`gh api` call made against this
repository on 2026-09-25 (RESEARCH.md's "Verified Live State", or a call made directly
in this plan's own execution) -- a comment above each names the call. Per-case variants
change **values** (state, a PR number, conclusions, ids), never **shape**.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.pr_land import (
    PullRequest,
    WorkflowRun,
    check_head,
    head_refusals,
    land,
    newest_run,
    parse_jobs,
    parse_pull_request,
    parse_runs,
    pr_refusals,
    required_jobs,
    squash_subject,
)


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

    def __call__(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        joined = " ".join(argv)
        for substring, responses in self._handlers:
            if substring in joined:
                if len(responses) > 1:
                    return responses.pop(0)
                return responses[0]
        raise AssertionError(f"FakeRunner: no handler registered for {argv!r}")


# --- recorded shapes -------------------------------------------------------------
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

REQUIRED = frozenset({"test (3.12)", "vendor-bundle", "image"})


# --- required_jobs() --------------------------------------------------------------


def test_required_jobs_reads_non_comment_non_blank_lines(tmp_path: Path) -> None:
    """`#` lines, blank lines and names with spaces (`test (3.12)`) -- the exact
    shape `.github/workflows/required-jobs.txt` uses."""
    path = tmp_path / "required-jobs.txt"
    path.write_text(
        "# a header comment\n\ntest (3.12)\nvendor-bundle\n\n# another comment\nimage\n",
        encoding="utf-8",
    )
    assert required_jobs(path) == frozenset({"test (3.12)", "vendor-bundle", "image"})


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
    assert head_refusals(PR3_HEAD_SHA, run, jobs, REQUIRED) == []


def test_head_refusals_no_run_names_the_sha() -> None:
    refusals = head_refusals(PR3_HEAD_SHA, None, [], REQUIRED)
    assert len(refusals) == 1
    assert PR3_HEAD_SHA in refusals[0]


def test_head_refusals_run_in_progress_names_still_running_and_url() -> None:
    run = WorkflowRun(id=1, status="in_progress", conclusion=None, html_url="https://x/1")
    refusals = head_refusals(PR3_HEAD_SHA, run, [], REQUIRED)
    assert len(refusals) == 1
    assert "still running" in refusals[0]
    assert "https://x/1" in refusals[0]


def test_head_refusals_empty_jobs_list_reports_every_required_job_missing() -> None:
    """PR #2's own recorded shape: `statusCheckRollup: []` -- zero jobs at all, not
    one failing -- must refuse the same as a red job."""
    run = WorkflowRun(id=1, status="completed", conclusion="success", html_url="u")
    refusals = head_refusals(PR3_HEAD_SHA, run, [], REQUIRED)
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
    refusals = head_refusals(PR3_HEAD_SHA, run, jobs, REQUIRED)
    assert len(refusals) == 1
    assert "test (3.12)" in refusals[0]
    assert "failure" in refusals[0]


def test_head_refusals_matches_the_recorded_red_run_verbatim() -> None:
    """The literal shape run 35993984796 returned, unmodified -- a required set that
    includes `test (3.10)` (this task's pre-D-09 set) catches the one red job."""
    jobs = parse_jobs(RED_RUN_JOBS_JSON)
    run = WorkflowRun(id=35993984796, status="completed", conclusion="failure", html_url="u")
    refusals = head_refusals(PR3_HEAD_SHA, run, jobs, REQUIRED | {"test (3.10)"})
    assert len(refusals) == 1
    assert "test (3.10)" in refusals[0]
    assert "failure" in refusals[0]


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


# --- check_head (the read-only network shell, faked) --------------------------------


def test_check_head_green_returns_no_refusals() -> None:
    runner = (
        FakeRunner()
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, PR3_JOBS_JSON))
    )
    assert check_head(PR3_HEAD_SHA, runner, REQUIRED) == []


def test_check_head_a_failed_read_is_a_refusal_showing_stderr() -> None:
    runner = FakeRunner().on(f"runs?head_sha={PR3_HEAD_SHA}", cp(1, "", "gh: rate limited"))
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1
    assert "rate limited" in refusals[0]


def test_check_head_unparseable_output_is_a_refusal() -> None:
    runner = FakeRunner().on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, "not json"))
    refusals = check_head(PR3_HEAD_SHA, runner, REQUIRED)
    assert len(refusals) == 1


# --- land(): the whole path, offline -------------------------------------------------


def _happy_runner(pr_json: str = PR3_VIEW_JSON.replace('"MERGED"', '"OPEN"')) -> FakeRunner:
    """An OPEN PR based on main, a clean tree, one green completed run, a successful
    merge, the squash commit's oid, and -- for the squash sha -- no run on the first
    poll, one on the second (the poll-success shape)."""
    return (
        FakeRunner()
        .on("pr view 3 --json number", cp(0, pr_json))
        .on("git diff --quiet", cp(0))
        .on("git diff --cached --quiet", cp(0))
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
    runner = _happy_runner()
    # Override the poll handler: every attempt returns empty.
    runner._handlers = [
        (sub, ([cp(0, "[]")] if sub.startswith("runs?head_sha=deadbeef") else resp))
        for sub, resp in runner._handlers
    ]
    sleeps: list[float] = []
    result = land(3, runner, attempts=3, interval_s=1.0, sleep=sleeps.append)
    assert result == 1
    assert sleeps == [1.0, 1.0]  # attempts - 1
    out = capsys.readouterr().out
    assert "IS merged" in out
    assert "deadbeef1234" in out
    assert "no ci.yml run appeared" in out


def test_land_local_tip_differs_keeps_the_branch(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _happy_runner()
    runner._handlers = [
        (
            sub,
            [cp(0, "0123456789abcdef0123456789abcdef01234567")]
            if sub.startswith("rev-parse --verify")
            else resp,
        )
        for sub, resp in runner._handlers
    ]
    assert land(3, runner, sleep=lambda _: None) == 0
    assert not any(c[:3] == ["git", "branch", "-D"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "differs from the merged head" in out


def test_land_local_branch_absent_no_delete_no_error() -> None:
    runner = _happy_runner()
    runner._handlers = [
        (sub, [cp(1)] if sub.startswith("rev-parse --verify") else resp)
        for sub, resp in runner._handlers
    ]
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
        .on(f"runs?head_sha={PR3_HEAD_SHA}", cp(0, PR3_RUNS_JSON))
        .on("runs/36088409707/jobs", cp(0, PR3_JOBS_JSON))
        .on("pr merge 3 --squash", cp(1, "", "gh: PR is not mergeable"))
    )
    result = land(3, runner, sleep=lambda _: None)
    assert result == 1
    assert not any(c[:2] == ["git", "switch"] for c in runner.calls)
    out = capsys.readouterr().out
    assert "gh pr view 3" in out
