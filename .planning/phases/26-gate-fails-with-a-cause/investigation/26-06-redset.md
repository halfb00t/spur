# 26-06 red set of `make test-image` on the unfixed recipe

Host: Darwin 27.0.0 arm64 (OrbStack), Docker server 29.4.0, 2026-10-15, HEAD `febe0b9`.
Image: `spur:latest` is **linux/amd64** (the shell has `DOCKER_DEFAULT_PLATFORM=linux/amd64`, `PLATFORM` unset, so the
image runs emulated on this arm64 host). Container pytest: **9.1.1** (pytest-cov and pytest-xdist are not installed).

Two readings, both from the unfixed image and the unfixed `Makefile`:

1. `26-06-first.log` -- `make test-image PYTEST_ARGS="-rs"`, exit 2, wall 125 s (image build 57 s of it): **5 errors in 4.20s**,
   `Interrupted: 5 errors during collection`. Collection errors stop the run, so no test-level red was visible.
2. `26-06-first-mounted.log` -- the same image and the same command line, with the `bench/` and `scripts/` mounts and
   `PYTHONPATH=/app/src:/app` applied by hand (Makefile not edited; docker run directly), `--ignore=tests/test_browser.py` only:
   **29 failed, 1290 passed in 863.84s (0:14:23)**, exit 1, no `SKIPPED` line. This is the reading that decides D-11.

| Test | Cause | Class |
|---|---|---|
| tests/test_bench.py (collection) | `ModuleNotFoundError: No module named 'bench'` | bench/scripts not mounted |
| tests/test_calc.py (collection) | `ModuleNotFoundError: No module named 'bench'` | bench/scripts not mounted |
| tests/test_trochoid.py (collection) | `ModuleNotFoundError: No module named 'bench'` | bench/scripts not mounted |
| tests/test_pr_land.py (collection) | `ModuleNotFoundError: No module named 'scripts'` | bench/scripts not mounted |
| tests/test_skip_tokens.py (collection) | `ModuleNotFoundError: No module named 'scripts'` | bench/scripts not mounted |
| tests/test_bench.py::test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order | `bench/build_time.py:131` runs `git`: `FileNotFoundError: 'git'` | git |
| tests/test_bench.py::test_the_report_prints_the_load_it_was_given_rather_than_reading_one_itself | `bench/build_time.py:131` runs `git`: `FileNotFoundError: 'git'` | git |
| tests/test_browser_pins.py::test_playwright_is_pinned_exactly_in_dev_and_never_in_the_runtime_closure | `FileNotFoundError: /app/Dockerfile` | Dockerfile |
| tests/test_hooks.py::test_the_commit_hook_runs_the_fast_prefix_and_the_push_hook_runs_the_whole_gate | `FileNotFoundError: /app/.pre-commit-config.yaml` | make |
| tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe | `FileNotFoundError: 'make'` | make |
| tests/test_hooks.py::test_the_pin_ignores_pytest_args_set_in_the_environment | `FileNotFoundError: 'make'` | make |
| tests/test_hooks.py::test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line | `FileNotFoundError: 'make'` | make |
| tests/test_hooks.py::test_the_whole_gate_installs_the_browser_and_the_commit_slice_never_does | `FileNotFoundError: /app/Makefile` | make |
| tests/test_hooks.py::test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves | `FileNotFoundError: 'make'` | make |
| tests/test_hooks.py::test_the_image_suite_ignores_the_browser_test | `FileNotFoundError: 'make'` | make |
| tests/test_hooks.py::test_the_hook_stamp_installs_from_the_main_checkout_and_never_from_a_linked_worktree | `FileNotFoundError: /app/Makefile` | make |
| tests/test_hooks.py::test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set | `FileNotFoundError: /app/Makefile` | make |
| tests/test_no_fake_done.py::test_a_staged_file_with_both_markers_is_refused_with_each_line_named | `FileNotFoundError: /app/Makefile` | make |
| tests/test_no_fake_done.py::test_markers_inside_longer_words_pass | `FileNotFoundError: /app/Makefile` | make |
| tests/test_no_fake_done.py::test_a_no_space_type_ignore_under_src_spur_is_refused | `FileNotFoundError: /app/Makefile` | make |
| tests/test_no_fake_done.py::test_a_whole_file_ignore_errors_in_an_untracked_module_is_refused | `FileNotFoundError: /app/Makefile` | make |
| tests/test_no_fake_done.py::test_a_deliberate_suppression_outside_src_spur_passes | `FileNotFoundError: /app/Makefile` | make |
| tests/test_pr_land.py::test_required_jobs_file_matches_ci_yml_job_names | `FileNotFoundError: /app/.github/workflows/ci.yml` | .github |
| tests/test_pr_land.py::test_a_job_name_override_moves_the_derived_required_set | `FileNotFoundError: /app/.github/workflows/ci.yml` | .github |
| tests/test_pr_land.py::test_land_happy_path_returns_0_and_prints_the_run_url | `scripts/pr_land.py:212 required_jobs`: `FileNotFoundError: /app/.github/workflows/required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_reports_the_last_read_error_when_every_poll_failed | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_reports_no_run_observed_with_the_actions_url_when_reads_succeeded | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_names_a_skip_token_only_after_reading_it_from_the_squash_commit | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_local_tip_differs_keeps_the_branch | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_local_branch_absent_no_delete_no_error | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_gh_pr_merge_failure_returns_1_no_poll_no_follow_up | same, `required-jobs.txt` | .github |
| tests/test_pr_land.py::test_land_several_problems_at_once_prints_all_then_one_nothing_was_merged_line | same, `required-jobs.txt` | .github |
| tests/test_pool.py::test_forced_gc_inside_the_resource_tracker_lock_finds_no_reentrant_cleanup | the test spawns `pytest ... --no-cov -n0` in a subprocess; the image holds neither pytest-cov nor pytest-xdist: `pytest.main(): error: unrecognized arguments: --no-cov -n0`, `check_alive calls: 0` (`tests/test_pool.py:773`) | other |

Counts: 5 collection errors + 29 test failures = 34 rows. The `git` row count is 2 (test_bench), `Dockerfile` 1, `make` 14
(9 in test_hooks, 5 in test_no_fake_done: 9 test_hooks tests = 1 hook-config read + 8 `make` or `Makefile` readers; every
test_hooks test fails), `.github` 11, `other` 1.

What D-11's rule would `--ignore`, file by file (a file is ignored only if at least one of its reds is `make`, `git`,
`Dockerfile` or `.github`): `tests/test_hooks.py` (make; all 9 tests drop), `tests/test_no_fake_done.py` (make; all 5 drop),
`tests/test_browser_pins.py` (Dockerfile; all 3 drop -- it holds the only test), `tests/test_pr_land.py` (`.github`; 11 of its
58 fail, so the whole-file ignore drops 47 passing tests with them) and `tests/test_bench.py` (git; 2 of its 43 fail, so the
whole-file ignore drops 41 passing tests). With `tests/test_browser.py` that is six ignored files. The five collection errors
are fixed by the mounts, not by an ignore, and `tests/test_calc.py`, `tests/test_trochoid.py` and `tests/test_skip_tokens.py`
stay in the image suite.

**The one red outside the rule** is `tests/test_pool.py::test_forced_gc_inside_the_resource_tracker_lock_finds_no_reentrant_cleanup`
(added by 26-04, D-02). It is not a host-file read: the image installs only `pytest` and `httpx`, and the test launches a
subprocess `pytest --no-cov -n0` that needs `pytest-cov` and `pytest-xdist`. The other 20 tests of `tests/test_pool.py` pass in
the image. This is class `other`, so the plan stops here before any fix (D-11). Evidence for the options:
`26-06-optB-probe.log` -- in the same image with `pytest-cov 7.1.0` and `pytest-xdist 3.8.0` installed beside pytest 9.1.1 and
httpx, `tests/test_pool.py -k forced_gc` gives `1 passed, 20 deselected in 24.28s`.

Whole-suite pytest summary of the diagnostic reading: `29 failed, 1290 passed in 863.84s (0:14:23)`; of those 29, 28 fit the rule
and 1 does not.
