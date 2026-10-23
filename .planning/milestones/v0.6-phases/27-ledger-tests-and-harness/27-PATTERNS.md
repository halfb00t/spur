# Phase 27: Ledger Tests and Harness - Pattern Map

**Mapped:** 2026-10-20
**Files analyzed:** 22 new/modified (code and records)
**Analogs found:** 22 / 22 (all paths checked with `git ls-files`; none is a gitignored mirror)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/process_group.py` (new, extraction) | test harness util | event-driven (OS signals) | `tests/browser_session.py:92-139` (the code itself moves) | exact (move) |
| `tests/test_process_group.py` (new) | test | event-driven | `tests/test_selector.py:226-234` (playwright-free copy precedent) + RESEARCH Code Examples sketch | role-match |
| `tests/browser_session.py` (modify: import, comment, launch text, IN-01/02/11, IN-02 docstring) | test harness | request-response | itself | exact |
| `tests/test_trochoid.py` (add slug totality) | test | transform | `tests/test_trochoid.py:~205-232` (`test_the_download_name_follows_the_root_root_mode_builds`) | exact |
| `tests/test_api.py` (fresh_exports fixture, openapi walk) | test | request-response | `tests/test_api.py:1296-1320` (the test being fixed) | exact |
| `tests/test_browser_pins.py` (launch pin, 21 IN-03) | test (AST pin) | transform | itself (`INSTALL_COMMAND` at :35, `_scan_set`) | exact |
| `tests/test_browser.py` (`_js_number` pairs, `fixture_hashes`) | test | transform | `tests/test_browser.py:604-628` | exact |
| `tests/test_relations.py` (`honeycomb (4)`, meta-test) | test | transform | `tests/test_relations.py:253-262` | exact |
| `tests/test_model.py` (:899, :926 patches; D-04) | test | transform | `tests/test_model.py:976` (already `lambda _p, _rm=None: 0.9506`) | exact |
| `tests/test_bench.py` (`_host_state` test) | test | transform | `tests/test_bench.py:65` import of `bench.trochoid_part` | role-match |
| `src/spur/model.py` (`_chamfer_tips(..., rm)`, `_build`) | model | transform | `src/spur/calc.py:371` `tip_chamfer_effective(p, rm=None)` | exact |
| `bench/trochoid_part.py` (`rm.curve`, `_host_state` catch) | bench | transform | `bench/trochoid_part.py:109-121, 329-348` | exact |
| `tests/composition.py` (22 IN-01 shared `_BORE_OFF`, optional) | shared test table | n/a | itself (uncollected shared-tables module) | role-match |
| `bench/RESULTS.md` (2 corrections, "Seen red once (Phase 27)", D-05 subsection) | record | append-only | `bench/RESULTS.md:4696-4702`, `:4805`, `:5306`, `:5515`, `:5980` | exact |
| `docs/architecture/decision_log.md` (L40 amendment) | decision record | append | `decision_log.md:1658, 1799, 1889` | exact |
| `docs/tech_debt/active/*` -> `resolved/*` + `INDEX.md` (5 items) | debt record | move | `docs/tech_debt/resolved/2026-10-20-pr-land-merges-a-stale-head.md` | exact |
| `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` (edit in place) | debt record | edit | same item (not moved) | exact |
| `.planning/phases/27-.../27-TRIAGE.md` (new) | triage table | batch | `.planning/phases/26-gate-fails-with-a-cause/26-REVIEW-DISPOSITION.md` | role-match |
| Throwaway branch `.github/workflows/ci.yml` (D-05, branch only) | config | event-driven | `.planning/phases/26-gate-fails-with-a-cause/26-02-PLAN.md` tasks 1-3 | exact |
| `.planning/phases/27-.../investigation/27-0N-run-*.log` | evidence | n/a | `.planning/phases/26-gate-fails-with-a-cause/investigation/26-02-run-*.log` | exact |

## Pattern Assignments

### (a) Debt item retirement
**Analog:** `docs/tech_debt/resolved/2026-10-20-pr-land-merges-a-stale-head.md`; INDEX Resolved row at `docs/tech_debt/INDEX.md:45`.

Item header shape (lines 1-9 of the resolved file):
```
# `make pr.land` merges the pushed PR head without checking the local branch is pushed

Severity: blocker
Status: resolved
Resolved in: fix(pr_land): refuse a local head branch the PR head does not carry
Date: 2026-10-20
Source: `/gsd-verify-work 26`, after `make pr.land PR=41`
```
`Resolved in:` is the fixing commit's own subject (a sha cannot be known inside the commit).

INDEX row (moved from `## Active` to the top of `## Resolved`, a 2-column table):
```
| [`make pr.land` merges ... pushed](resolved/2026-10-20-pr-land-merges-a-stale-head.md) | fix(pr_land): refuse a local head branch the PR head does not carry — see the file's own `Resolved in:` field |
```
Active rows are 3-column (`Severity | Item | Trigger to revisit`), e.g. the stop_group row at INDEX Active; drop the severity and trigger cells on the move.

Steps per item, same commit as the fix: edit `Status:` and add `Resolved in:`; `git mv docs/tech_debt/active/<f> docs/tech_debt/resolved/`; fix relative link `active/` -> `resolved/`; move the row. Items: slug-totality, failed-build-name, stop-group, group-floor, launch-message. Do NOT move `2026-10-09-phase-19-review-info-findings-deferred.md` (IN-04 `root_fillet` is Phase 28's): edit it in place, adjust its INDEX trigger text. Say in the final reply whether an item was filed.

### (b) Dated correction under a `bench/RESULTS.md` reading
**Analog:** `bench/RESULTS.md:4696-4702` (append-only paragraph, original not rewritten):
```
### Waist at the smallest arc thickness (19-REVIEW CR-01)
... `root_waist` is the narrowest arc. The walk table above is dated history and is not rewritten.
```
Target rows: macOS "3 (uvicorn and two pool workers)" at ~:4768 (table ends ~:4780, then blank line, then the `PNG_RATIO_BAR` paragraph) and ubuntu row at ~:4902 (table ends :4903, before :4905). Put one paragraph immediately AFTER each table (a paragraph between rows ends the table), naming the row in bold: `**Correction (2026-10-20, 27-0N), row "Group members seen before the kill".**` followed by the RESEARCH draft text (uvicorn + `multiprocessing.resource_tracker` + one or two workers; "the count 3 above stands as recorded; only its naming is corrected"). Never touch the 21-01 "Seen red once" row at :4817 that quotes the old failure text. Check: `git diff --numstat v0.5 -- bench/RESULTS.md` deleted column `0`; `grep -c "Correction (2026-10-" bench/RESULTS.md` rises by 2.

### (c) Dated amendment to a decision in `decision_log.md`
**Analog:** `docs/architecture/decision_log.md:1658`:
```
**Amendment (2026-10-06, 14-REVIEW IN-02).** The tip rows' gaps (5.85e-10 to 6.55e-10 mm3)
sit below D-06's literal trigger of 1e-9 mm3, so at `abs=1e-9` they pass; ...
the cause was the headroom.
```
Also `:1799` (`**Amendment (2026-10-06, 15-REVIEW WR-01 and IN-03).**`), `:1889`, `:1894`. Appended as a bold-led paragraph at the end of the entry, before the next `## L..` heading. For L40, append before `## L41` (heading at ~:2598, after the "Machine: ..." paragraph): `**Amendment (2026-10-20, 22-REVIEW IN-03).**` with the 1.13/3.20/3.56 s, mean 2.63 s range from `bench/RESULTS.md` "The download step, priced (22-02)"; `BUILD_WAIT_MS` conclusion unchanged. Optionally one sentence that L40's "The sweep is a command, not a test" Totality paragraph is now also guarded by the seeded test. No rewrite of L40 text.

### (d) Triage / disposition table
**Analog:** `.planning/phases/26-gate-fails-with-a-cause/26-REVIEW-DISPOSITION.md` (frontmatter + table; tracked). Table form (lines ~40-48):
```
| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 26-REVIEW-FIX.md |
| IN-01 | info | open | - |
Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell
```
Frontmatter keys: `phase`, `review`, `titles`, `findings: [{id, severity, disposition, title}]`, `open`, `total`, `recorded`. Older analog (v0.5 phases): `.planning/milestones/v0.5-phases/22-download-name-carries-the-root/22-REVIEW-DISPOSITION.md`. `27-TRIAGE.md` has no direct precedent file: use RESEARCH's "Draft triage table" with columns `Finding | Review | Proposed disposition | Fix / path | Phase`, using the dispositions vocabulary above; D-07 records 19 IN-02 near-copy replacement as `skipped` with reason (assert vs `ValueError`, fixed 400 vs `samples`, signature). Phase 26's five `| info | open |` rows are in no triage list: surface to the human, do not triage.

### (e) Throwaway-PR plan task shape (D-05)
**Analog:** `.planning/phases/26-gate-fails-with-a-cause/26-02-PLAN.md:115-219` (three tasks). Copy:
- Task 1 `type="tracer"`: `<precondition>` clean tree; `git switch -c spike/27-... <base>`; record `date -u`, branch and sha; refuse if branch exists locally or on origin (`git ls-remote --heads origin`), never reuse; plain `git commit` (hooks run; `tests/test_pr_land.py` reads only `ci.yml` job names, keep three jobs); subject `ci(spike): ... -- DO NOT MERGE`; switch back and confirm sha and clean tree. Verify with `git diff --name-only` and `--numstat` assertions.
- Task 2 `type="checkpoint:human-action" gate="blocking-human"`: `<instructions>` give `git push -u origin <spike>` and `gh pr create --draft --base main --head <spike> --title "spike(27): ... -- DO NOT MERGE" --body "..."`; note pre-push hook runs `make verify` (3-5 min); `<resume-signal>Type "pushed, PR #N", or "not pushing".</resume-signal>`.
- Task 3 `type="auto"`: `gh run list --branch ... --limit 1 --json databaseId,headSha,...` (headSha must equal spike commit), `gh run watch {id} --exit-status --interval 30` (timeout 5400000), `gh run view {id} --log --job {job-id} > investigation/27-0N-run-{id}-test.log` (whole logs, never `--log-failed` alone), grep `Image:`/`Version:` in `Set up job` and the distinctive listing marker, record in `bench/RESULTS.md`, commit one concern, `gh pr close N --comment "... Closed unmerged; the branch is the human's to delete."` with no `--delete-branch`, never `gh pr merge`. Verify that the PR state is `CLOSED unmerged` and `git ls-remote --heads origin <spike>` is non-empty.
- Phase 27 differences: workflow edit is `ci.yml` `test` job `- run: make verify PYTHON=python` -> `make test PYTHON=python PYTEST_ARGS="tests/test_browser.py -s -n0 --no-cov"`, plus a temporary `spur-group-listing:` print in `tests/browser_session.py::serve` after `members = group_members(proc.pid)`, on the spike branch only. Cut from the Phase 27 head (not `v0.5`). Run it before other plans (shared working tree, `use_worktrees` false). Take the local macOS listing with a scratch `-p` plugin wrapping `browser_session.group_members` (no repo edit).

### (f) "Seen red, recorded" subsection in `bench/RESULTS.md`
**Analogs:** `### Seen red once (Phase 21)` at :4805, `(Phase 22)` :5306, `(Phase 23)` :5396, `(Phase 24)` :5515. Shape:
```
### Seen red once (Phase 22)

These are 22-01's red runs (PD-10): each pin was run red before the code it pins existed, or while the rejected rule was in place, and the first failure line is copied from 22-01's SUMMARY and its kept logs. Later plans append rows.

| Plan | Test or step | Deliberate break | First failure line | Reverted |
|---|---|---|---|---|
| 21-01 | `webgl2` | `launch()` passes `args=["--disable-3d-apis"]` | `1 failed`: `AssertionError: ...`, note `step: webgl2` | yes, `git diff --exit-code` clean |
```
Add `### Seen red once (Phase 27)` (place after the Phase 26 `### The phase's first CI run (26-07)` section, `## ` heading level per the Phase 26 section at :5934). Rows required: slug test vs raising `_junction` (`RuntimeError: mutated _junction`), vs raising `_root_curve`; failed-build name (`assert 200 == 422` with pre-seeded `_EXPORTS`, old shape); `stop_group` old code (2 failed: signal-first assertion, `CalledProcessError`); leader-only `os.kill` re-run (`Failed: server process group N still has live pids [...]`); launch-message pin vs old text (D-09); 21 IN-03 two synthetic snippets; 24 IN-03 synthetic doc; 23 IN-08 (`wrong or extra driver`); `_host_state` no git. "Reverted" cell: `yes, git checkout -- <file>; git diff --exit-code -- <file> clean` (e.g. `git diff --stat v0.5 -- src/spur/calc.py` empty). D-05 record goes in its own `###` subsection in 26-02's form (`### Ubuntu 26.04, pre-classified (26-02)` at :5980: intro of who pushed what, run table, `#### Host state`, `#### Readings`, closing paragraph).

### `tests/process_group.py` / `tests/browser_session.py` (harness, event-driven)
**Analog:** `tests/browser_session.py:92-139` (moves verbatim, then reordered). Existing body to start from:
```python
def _signal_group(pgid: int, sig: signal.Signals) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pgid, sig)

def stop_group(proc, log) -> None:
    pgid = proc.pid  # start_new_session makes the leader's pid the group id
    survivors = group_members(pgid)        # <- ps read before any signal (the defect)
    bound = TERM_BOUND_S                   # <- dead assignment (21 IN-01)
    for sig, bound in ((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S)):
        _signal_group(pgid, sig)
        ...
```
Target body: RESEARCH Pattern 3 (signal first inside the loop; `except (subprocess.CalledProcessError, OSError)` -> `survivors = None`; reap with `proc.wait` after; two `pytest.fail` messages, "survivors unknown" and "after SIGTERM (X s) and SIGKILL (Y s)"). `group_members` stays `check=True`. Own commit for the move before the reorder (D-06); `browser_session` re-imports the names (`serve`, `_wait_for_pool` use them). No `playwright` import in `process_group.py` (image lacks playwright and `ps`; precedent `tests/test_selector.py:230` copies `_js_number` for the same reason). Name has no `browser`, so the `*browser*` glob exclusion does not catch it.

**Unit test shape:** RESEARCH "Fake-`ps` ordering test" sketch: `subprocess.Popen(["sleep","60"], start_new_session=True)`, spy `_signal_group` and fake `group_members` recording events, `finally: os.killpg(...)` suppressed for `ProcessLookupError, PermissionError` then `proc.wait(timeout=5)` (pytest `filterwarnings = ["error"]` turns an un-waited Popen into a failure). Name unused lambda args `_g`, `_s` (ruff `ARG`).

### `MIN_GROUP_MEMBERS` comment and launch message in `tests/browser_session.py`
**Current text** (lines 55-57, line numbers per RESEARCH are now `:57`; re-grep before editing):
```python
# uvicorn plus the shipped pool of 2 workers (D-11, 21-RESEARCH Pattern 1). Seen before the
# kill so that the zero seen after it is a real zero and not a reader that matches nothing.
MIN_GROUP_MEMBERS = 3
```
Comment style to match: dated, host-and-measurement-bearing, e.g. the `BUILD_WAIT_MS` block above it ("2.53 s on macOS (21-01, M5 Max, load 3-5) and 4.75 s on ubuntu-latest (21-02, run 38044109910, 4 vCPU ...)"). Write the Linux clause only after reading the D-05 log (cite run id, image, date). Also reword "pool workers" in the `serve()` docstring and the assertion message.

**Launch message** (current, lines ~219-227, keep `pytest.fail` and a string constant containing `playwright install --only-shell chromium`, pinned by `tests/test_browser_pins.py:35` `INSTALL_COMMAND`):
```python
pytest.fail(
    "the headless shell is not installed: run `playwright install --only-shell "
    f"chromium` (PLAYWRIGHT_BROWSERS_PATH={path}); `make test` runs the install "
    f"stamp for you.\nPlaywright said: {error}"
)
```
Drop the last clause; name `rm -f .venv/.browser && make test` (VENV override noted) and `BROWSER_INSTALL_ARGS=--with-deps` for Linux. One pin in `tests/test_browser_pins.py` (D-09), seen red against the old text.

### `tests/test_trochoid.py` slug totality (test, transform)
**Analog:** `tests/test_trochoid.py` `test_the_download_name_follows_the_root_root_mode_builds` (~:205-232; `pytest.param(..., id="tip-land-gone-refused")`, literals, docstring citing REQ and SC). Already imports `_junction`, `_root_curve` from `spur.calc` and defines `_BORE_OFF` (:88, :208). Body: RESEARCH Pattern 1 (`typing.get_args(RootReason)` equality, four stratified boxes, `random.Random(20261020)`, bucket = `root_mode`'s answer, each bucket `> 0`; forced rows via `monkeypatch.setattr("spur.calc._junction", lambda c, eps: None)` and `("spur.calc._root_curve", lambda c: "curve invalid")`, ids `forced-bracket-degenerate`, `forced-curve-invalid`). Docstring style: cite REQ id, then the claim.

### `tests/test_api.py` failed-build name (test, request-response)
**Analog (the test under edit):** `tests/test_api.py:1296-1320`:
```python
app.dependency_overrides[build_backend] = lambda: backend
try:
    # 25 teeth trochoid is downloaded by no other test ... so the byte cache cannot answer ...
    r = client.get("/api/model.stl", params={"quality": "preview", **fields})
finally:
    app.dependency_overrides[build_backend] = lambda: _inline_backend
assert r.status_code == 422
assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven
```
Add fixture (RESEARCH Pattern 2; `src/spur/app.py:88` `_EXPORTS = _BlobCache(...)`, `_BlobCache.__init__(self, budget: int)`), use `from spur import app as app_module` inside (as at test_api.py:949, 1024, 1036); delete the "downloaded by no other test" comment. Siblings at ~:1255, :1322, :1357 untouched (D-08). 24 IN-03 at `tests/test_api.py:143` (`assert "selectors" not in client.get("/openapi.json").text`) -> recursive key walk.

### `src/spur/model.py` + `tests/test_model.py` (D-03/D-04)
**Analog:** `src/spur/calc.py:371` `tip_chamfer_effective(p, rm: RootMode | None = None)`; `tests/test_model.py:976` already uses `lambda _p, _rm=None: 0.9506`. Changes: `model.py:625-636` `_chamfer_tips(solid, p, pr, rm)` -> `tip_chamfer_effective(p, rm)`; `_build` (~:768-779) passes the `rm` it already asked for at :773; add `RootMode` to the `.calc` import block (:33-49, after `RootCurve`). `test_model.py:899` -> `lambda solid, _p, _pr, _rm: solid`; `:926` -> `lambda _p, _rm=None: 2.9875`. Proof: `git diff --exit-code v0.5 -- tests/regression/` and `-k chamfer`; no call-count test.

### `bench/trochoid_part.py` + `tests/test_bench.py`
**Analog:** `bench/trochoid_part.py:109-121` (`trochoid_curve`: replace re-solve with `rm.curve`, keep the `ValueError` naming the reason, delete the "does not exist until 19-04" paragraph) and `:329-348` (`_host_state`: wrap `subprocess.run(["git","rev-parse","--short","HEAD"], ..., check=True)` in `except (subprocess.CalledProcessError, FileNotFoundError): head = "unknown"`). Test: `tests/test_bench.py` (imports `bench.trochoid_part` at :65, in the commit slice); patch `bench.trochoid_part.subprocess.run` to raise, assert line `HEAD: \`unknown\``.

### `tests/test_relations.py` (23 IN-08)
**Analog:** `tests/test_relations.py:253-262` `CUTOUT_STATES`: add `"honeycomb (4)": {"hex_cell": 4, "hex_wall": 1}`; cell counts derive from `len(CUTOUT_STATES)` (14 states x 11 relations = 154); meta-test `test_a_relation_true_only_at_the_first_open_count_goes_red` gains `("hex_wall", "hex_cell", 0.05)` (third parametrize element replacing hardcoded `1.0`); reword "twelve"/"count gate".

### `tests/test_browser_pins.py` / `tests/test_browser.py` / `fixture_hashes`
**Analog:** `tests/test_browser_pins.py:43-101` (`ALLOWED_ENVIRON_MARKERS = ("SPUR_", "PLAYWRIGHT_BROWSERS_PATH")`, first-source-line match -> `ast.Constant` strings of the enclosing statement); `tests/test_browser.py:604-628` pairs table for `_js_number` (`(-0.0, "0")`, `pytest.raises(AssertionError)` for `1e21`, `1e-7`); `browser_session.py:~668-698` `fixture_hashes` (assert value type, output unchanged so `tests/regression/golden_requests.json` is untouched).

## Shared Patterns

### Seen red once, recorded
**Source:** `bench/RESULTS.md:4805` onward. **Apply to:** every new guard (slug x2, name isolation, `stop_group` x2, launch pin, 21 IN-03, 24 IN-03, 23 IN-08, `_host_state`). Mutation is temporary; `git checkout -- <file>` and a clean `git diff` confirm the revert. Record command and first failure line.

### Append-only records, one concern per commit
**Source:** CLAUDE.md, L08; `git diff --numstat v0.5 -- bench/RESULTS.md` deleted column 0; `git diff --exit-code v0.5 -- tests/regression/` empty. Retire each debt item in the commit that fixes it (pattern (a)). Conventional Commits, trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

### Gate
**Source:** `make verify` (full), `make verify.fast` (commit slice, under L36's 30 s; 922 passed, 9.80 s before this phase). Targeted: `.venv/bin/python -m pytest <file> -k <expr> -n0 --no-cov -q`. No `TODO`/`FIXME`/`pass`-as-done in `*.py` (`make no-fake-done`); ruff `ARG`/`TRY`/`PT`/`ERA`, mypy `--strict` over `src tests docker bench scripts`.

### Comments carry the measurement
**Source:** `tests/browser_session.py` `BUILD_WAIT_MS` / `PNG_RATIO_BAR` comments: host, load, date, run id, image.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `27-TRIAGE.md` | triage table | batch | No prior phase-directory triage file exists (`git ls-files .planning | grep -i triage` is empty); the nearest forms are `*-REVIEW-DISPOSITION.md` files. Use their vocabulary with the RESEARCH draft columns. |
| `tests/test_process_group.py` | test | event-driven | No existing process-group unit test; compose from the RESEARCH sketch and `tests/test_selector.py:226-234` copy-instead-of-import precedent. |

## Metadata

**Analog search scope:** `docs/tech_debt/`, `docs/architecture/decision_log.md`, `bench/RESULTS.md`, `.planning/phases/26-*`, `.planning/milestones/v0.5-phases/22-*`, `tests/`, `bench/`, `src/spur/`.
**Files scanned:** about 20 read or grepped; all analog paths confirmed tracked with `git ls-files` (the line numbers for RESEARCH-cited code were not all re-verified: `MIN_GROUP_MEMBERS` is at about :57, not :49).
**Pattern extraction date:** 2026-10-20
