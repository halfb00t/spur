# Pitfalls Research

**Domain:** a debt-sweep milestone (v0.6 Clean Ledger) on spur: a gate that must stay trustworthy (pytest-xdist `-n 8 --cov`, 300 s bar, headless browser, spawn-context `BuildPool`), a hunt for a rare flake and a rare hang, two guard tests, a process-group teardown, one user-visible link refusal, a runner-OS migration, and info-finding triage.
**Researched:** 2026-10-15
**Confidence:** HIGH for repo-specific pitfalls (read from code, debt files and retrospectives, several re-measured today); MEDIUM for upstream/runner facts (web-sourced, tagged below).

**Claim tags used below:** `MEASURED` = I ran it today in this repo (2026-10-15, `.venv`, Python 3.12.15, pytest 9.1.1); `READ` = read in a named file or fetched page; `UNVERIFIED` = inference or assumption, not checked. Anything tagged `UNVERIFIED` must not be written into a decision or a comment as fact.

**Phase labels.** The roadmap does not exist yet. "Phase to address" uses these working labels, which map one-to-one onto the milestone's target features:

| Label | Scope |
|---|---|
| **A. Gate reliability** | `resource_tracker` flake loops and fix-or-redefer; 98 % hang evidence capture |
| **B. Phase 22 guard pair** | seeded `slug()` totality test; `_EXPORTS`-order-independent failed-build name test |
| **C. Browser harness pair** | `stop_group` signal-before-read; group-floor comment and dated RESULTS corrections |
| **D. Invalid-enum link** | `#root_shape=bogus` refused visibly; new `Lxx`; browser pin flips |
| **E. Ubuntu 26 CI** | classify the first Ubuntu-26 CI run before any fix (date-gated, from 2026-10-19) |
| **F. Triage and cheap items** | info findings of Phases 19, 21-24; hook pin, launch message, `make test-image` |

---

## Critical Pitfalls

### Pitfall 1: Closing the flake on a non-reproduction (or on a quiet fortnight)

**What goes wrong:**
The loops run, read zero reds, and the item is resolved ("could not reproduce") or the milestone's success line reads "gate no longer flakes". The flake returns in the next milestone, the sixth occurrence, with the trigger again naming a lapsed event.

**Why it happens:**
The flake is rare and the loops are expensive. The record is 5 occurrences (3 local, 1 CI, 1 more local) against 100 clean two-file loops and 60 clean isolation loops (READ: `2026-10-06-resource-tracker-flake-fails-the-gate.md`). The whole-suite rate is unmeasured; the debt file's only local estimate is 2 in 12 before Phase 23 (READ), and 5 occurrences in a few dozen whole-suite runs puts it somewhere in a few to roughly fifteen percent (UNVERIFIED: the denominators were never recorded). Zero reds in N loops bounds the rate only to about 3/N (rule of three): 30 clean loops leave an upper bound near 10 %, 60 near 5 %. With an unknown true rate the chance of seeing nothing is large (arithmetic: at a true 3 % rate, 30 loops see no red 40 % of the time; at 10 %, 4 %; 60 loops at 3 %: 16 %). A negative from a short loop is therefore not evidence of absence, which is exactly the v0.4 lesson ("60 isolation loops saw nothing, one whole-suite baseline run did").

**How to avoid:**
- Commit the stop rule before the first loop (the v0.3 pre-registration pattern, which worked): arms, loop count, what counts as a red, and the allowed outcomes. Suggested: whole-suite `make test` loops, one variable per arm (`-n 8 --cov` vs `-n 8 --no-cov`), interleaved round by round on the same host, run until the first red in an arm or 60 loops per arm, whichever comes first.
- The only outcomes: (a) a captured red with its whole log, then diagnose and fix; (b) no red in the cap, then re-defer with the stated 95 % upper bound (about 3/N) and a trigger that names an event, not a phase. Never "resolved".
- Write the milestone success line about what the milestone controls ("loops run to the pre-registered cap, outcome recorded, evidence armed"), not "flake gone". v0.3's own lesson: a success metric the milestone's discoveries or luck can fail.
- Loops must be whole-suite. Two-file loops were already shown not to sample the gate's population (READ: 19-03, "probably do not sample the same population").

**Warning signs:**
A loop count chosen after seeing the first runs; "looks stable" in a SUMMARY; two variables changed between arms (see Pitfall 2); a debt file flipped to `resolved` with no commit that changes code or a filter; a trigger phrased "Phase NN planning".

**Phase to address:** A (stop rule is the first commit of the phase, before any loop).

---

### Pitfall 2: Changing two variables at once, or comparing arms that are not comparable

**What goes wrong:**
An arm differs from the baseline in more than the intended factor, so a red or a no-red cannot be attributed. Concrete traps here:
- `--no-cov` also removes coverage's `multiprocessing` and `thread` concurrency patching (READ: `pyproject.toml` `[tool.coverage.run]`), the tracer's allocations and the combine step. A no-red under `--no-cov` says the tracer shifts the timing; it does not say coverage is the cause.
- Host differs by hour: recorded load at the occurrences ranged from about 2.5 to 17.5 (READ). `tests/test_pool.py` uses injected 0.2 s and 1.0 s timeouts (READ: `Makefile` comment on `PYTEST_WORKERS`), so concurrent arms or a busy dev host produce timing failures that are not the flake.
- CI is not the dev host: `PYTEST_WORKERS` clamps to the online CPU count, so ubuntu-latest (4 vCPU) runs `-n 4`, and the RESULTS rows say `pytest -n 4` (READ). The debt file's third occurrence says "`-n 8`" for the CI run, which the Makefile clamp contradicts (READ; the clamp predates the occurrence). Do not reason from "-n 8" for CI.
- Dev tools float: `requirements.txt` pins the runtime closure only and `pytest`, `pytest-xdist`, `pytest-cov` are `>=` in `[dev]` (READ), so CI and the laptop can run different pytest or xdist. Record `pip freeze | grep -E 'pytest|xdist|cov|coverage'` with every loop.

**Why it happens:**
The first idea is "turn things off until it stops". Each factor is also a timing change.

**How to avoid:**
- One factor per arm, arms interleaved, never concurrent (concurrent arms starve each other and trip the 0.2 s/1.0 s pool timeouts).
- Do not repeat v0.5's mistake: its idle-host precondition could not be met on a shared developer host (eight waits, then a human waiver). Pre-register a loaded-host method: record `uptime` before and after each loop as a covariate, do not gate on it.
- Classify every non-green loop by signature before counting it: a red counts as the flake only if the log contains `ReentrantCallError` or `ResourceTracker called reentrantly`; any other failure is recorded as its own row, not discarded and not counted.
- Record per loop: wall time, effective `-n`, tool versions, load, and the worker-to-test assignment (see Pitfall 4's journal). Keep whole logs under `.planning/.../investigation/` as 19-01 and 23-04 did.
- If CI is a loop population, use a separate `workflow_dispatch` workflow file. A new job in `ci.yml` must be added to `required-jobs.txt` (READ: `tests/test_pr_land.py` drift test reads `ci.yml`) and becomes a required check on every PR.

**Warning signs:**
"Also bumped `-n`" or "also pinned a version" in a loop note; a loop log with a `test_pool.py` timing assertion failure counted as the flake; no effective `-n` recorded.

**Phase to address:** A.

---

### Pitfall 3: Fixing the symptom: a `filterwarnings` entry, or a `shutdown(wait=True)` added on a guess

**What goes wrong:**
The warning is filtered, or an explicit shutdown is sprinkled into tests, and the item is retired, while the cause is unlocated. The prior two deferrals refused exactly this (READ: "a fix would be a guess", "a filter would hide the symptom"); the milestone is about to be tempted to do it anyway because it is the third milestone to carry a `must`.

**What is actually known (use it):**
- The chain is a CPython 3.12 resource-tracker reentrancy: a garbage-collection pass finalizes a dead `Finalize` of a semaphore (`multiprocessing.synchronize._cleanup` calling `resource_tracker.unregister`) while the same thread is already inside the tracker. CPython added `ReentrantCallError` plus an `RLock` (GH-109629) and later a queue of reentrant messages (gh-131788) (READ: CPython commit pages found by search; MEDIUM).
- This venv's 3.12.15 has `ReentrantCallError` and `RLock` but not the reentrant-message queue (MEASURED: `inspect.getsource(multiprocessing.resource_tracker)` shows `ReentrantCallError` and `RLock`, no `_reentrant_messages`). So the later upstream fix is not in the project's only supported interpreter (L23), and the project cannot upgrade past 3.12. Whether it will ever be backported to 3.12 is UNVERIFIED.
- The test id does not localise the cause. Of the five occurrences, four name a test, and those four name three different ones (the dying-worker test twice, the same-slot-timeouts test, `test_health_reports_pool_state`; the first occurrence's log was truncated before the id) (READ). pytest 9.1.1 attributes an unraisable exception to whichever test phase is running when the hook fires (MEASURED: `_pytest.unraisableexception` source: the hook appends to a deque and `pytest_runtest_call/setup/teardown` drain it; the explicit `gc.collect()` runs only at unconfigure). The reported test is the victim of a GC pass, not the origin. The debt file's reasoning "no occurrence was localised to a pool a test leaves to its finalizer" therefore sets a bar the evidence format cannot meet.

**How to avoid:**
- The honest fix has to be framed as removing the precondition (no dead semaphore `Finalize` objects awaiting GC while the tracker is busy), proven by a reproduction, not as removing the warning.
- To get a reproduction cheaply, amplify GC and keep a control: run the suite (or the pool tests plus a long tail of other files, since "other tests on the same worker" is the recorded `ASSUMPTION`) with an investigation-only plugin that lowers GC thresholds (for example `gc.set_threshold(1, 1, 1)` from a `-p` module outside the repo). Pre-register it as a separate arm against an untouched control. If it reproduces at a higher rate, that shows the mechanism (UNVERIFIED that it will). It does not show the in-gate rate is cured.
- Then the candidate changes are ordered by honesty: (1) deterministic teardown in the pool tests (`shutdown(wait=True)`, drop references, an explicit `gc.collect()` at the fixture boundary after the pool is gone), shown red-to-green on the amplified arm and re-looped on the unamplified one; (2) a narrow filter naming the message, only with the upstream citation and the measured trigger rate recorded, as an explicit human decision. A `gc.collect()` that merely shifts timing is a mitigation and must be called one in the log and the comment.
- Keep the filter off unless the human picks it. Never a blanket `ignore::pytest.PytestUnraisableExceptionWarning` (the debt file already says so).

**Warning signs:**
A change to `pyproject.toml` `filterwarnings` in a commit that cites the flake; a fix whose evidence is "42 loops green"; a comment asserting which test "leaks the semaphore" with no listing; the word "probably" in a decision-log sentence.

**Phase to address:** A.

---

### Pitfall 4: The hang deliverable (evidence capture) costs the gate, or cannot see the hang

**What goes wrong:**
Diagnostics are added to every `make verify` and either slow it past the 300 s bar on CI and the laptop, change the pinned recipe, or still record nothing when the hang recurs.

**Why it happens:**
The obvious tools do not fit this failure:
- The hang stalled after about 1200 of 1220 items reported and produced nothing until the harness's SIGTERM at 600 s (READ). The harness kill loses any summary written at session end (`--junitxml`, `--durations`, the terminal summary). Only a stream flushed as it happens survives.
- `-v` under xdist prints a test id on completion, not on start, so it names the last finished tests, not the stuck one. `--durations` reports at the end. Neither shows a test that never finishes.
- A per-test timeout does nothing for a stall in the exit window after the last test (where the debt file says the stall sat) and `pytest-timeout` is not a dependency (READ: not in `[dev]`, and the lock is `>=`); adding it is a dev-dependency change and its signal method can itself kill the worker and erase the evidence.
- The recipe is pinned: `tests/test_hooks.py` requires `verify` and `verify.fast` to share one pytest recipe through the `-n` argument and `--ignore=` to appear only in the fast one (READ). Adding flags to one target's recipe, or `-v` to both unequally, goes red or silently forks "one definition of passing" (L13, L36).
- Host-specific cost is invisible locally: the same suite read 487 s, 895 s and 924 s on ubuntu-latest `main` runs against 180-300 s on the M5 Max (READ: `bench/RESULTS.md`). A diagnostic priced only on the laptop is not priced.

**How to avoid:**
- Capture, do not interpret: an append-only, per-worker journal of test start and finish lines, flushed per line, written by a small conftest hook (`pytest_runtest_logstart` / `logfinish`), to a temp directory outside the git tree, one file per xdist worker (`PYTEST_XDIST_WORKER`). On a stall, the last unfinished line per worker names the stuck test, and it survives SIGTERM. This is the "per-test ids and durations" the milestone asks for, in a form the failure cannot erase. Price it: 1,318 one-line flushed writes; measure the gate with and without it on the same host, in the same interleaved A/B shape as v0.5's browser test (L39), before accepting (L08: a gate cost is measured before it is accepted).
- Add stack evidence for the exit window: `faulthandler_timeout` (a built-in pytest ini option; it dumps all thread stacks after N seconds of one test) covers an in-test hang with no dependency. Whether its output reaches the terminal from an xdist worker is UNVERIFIED and must be tested on purpose by a deliberately sleeping test, run once and reverted. It does not cover the exit window; for that the runbook is operational: do not kill the stuck run first. Run `ps -A -o pid,ppid,pgid,stat,command` for the pytest tree (workers, `BuildPool` spawn children, `resource_tracker`) and a stack sampler on each (`sample <pid>` on macOS), then kill.
- Keep the recipe pin green by making any new flag common to both targets or by putting the journal in `conftest.py` only (no Makefile change).
- Explicitly leave the 98 % hang unfixed. Its debt file says one occurrence with no repro "can be watched, not fixed".

**Warning signs:**
`--timeout` or `-v` appearing in `Makefile` `test:` but not `test.fast:`; a new dev dependency in `pyproject.toml`; a gate reading more than noise slower in the A/B; the journal written inside the repo working tree (dirty tree on every run, and the pre-commit stash/`git grep` steps see it).

**Phase to address:** A (design and price it before arming).

---

### Pitfall 5: A `slug()` totality test that is vacuous (the debt's own suggested design mostly never reaches the refusal reasons)

**What goes wrong:**
The test passes, is green forever, and exercises almost nothing. This repo's retrospective already names the class: "a regression test is only a test if the bug it names makes it fail" (v0.2 lesson 2, WR-06).

**Measured facts (all MEASURED today, seed fixed, validated `GearParams` only):**
- Uniform random draws over the schema box with `root_shape="trochoid"`: of 24,776 requests that validate, 22,049 (89 %) end at `nothing radial to replace`, 2,687 (11 %) build the trochoid root, 40 (0.16 %) hit `tip land gone`, and 0 reach `bracket degenerate`, `curve invalid` or `tooth severed`. A seeded "few hundred random requests" test (the debt file's first suggestion) therefore reaches the interesting branches about zero times.
- The full `bench.trochoid.sweep_cases()` grid (31,446 cases, 1.7 s): 13,879 fail validation; of the rest, 9,954 build the trochoid, 6,674 `nothing radial to replace`, 866 `tip land gone`, 73 `tooth severed`, and 0 `bracket degenerate`, 0 `curve invalid`. So the debt file's other suggestion, "a slice of `sweep_cases()` covering every refusal reason", is also unsatisfiable through validated parameters for two of the six reasons.
- `slug()` reads only `root_mode(...).mode`. Its real failure is not "a reason string it cannot handle" (any reason gives the radial name); it is an exception raised inside `cutter` / `_junction` / `_root_curve` for some validated request (READ: `params.py` `slug`; `calc.py` `root_mode`). A test that counts reasons tests the wrong thing.

**Why it happens:**
The test is written from the debt file's wording ("reach every refusal reason") rather than from the failure it must catch (an exception on the failure-record path, which would turn a `BuildError` 422 into a 500 and lose the cause).

**How to avoid:**
- Assert the invariant over a stratified region, not the whole box: draw seeded cases from the undercut region (low tooth counts where `rb > rf`), plus the pinned boundary rows already in `test_the_download_name_follows_the_root_root_mode_builds` (26/27 flip, the tip-land row). Count modes and reasons inside the test and assert each reachable bucket is non-empty (`trochoid`, `tip land gone`, `tooth severed`). A counter assertion is what turns "passes" into "passes having looked".
- For the two unreachable reasons, say so in the test (an explicit assertion that validated sweeps never produce them, so a future change that makes them reachable fails loudly and prompts adding coverage) and drive them by monkeypatching `_root_curve` or `_junction` to return/raise them, asserting `slug()` returns the radial name for a returned reason. This is a decision for the human: either the two reasons are reachable only by construction, or the predicate has dead branches (a finding worth a line in the ledger).
- Prove it can fail: monkeypatch `_junction` (or `_root_curve`) to raise and show the new test goes red, with the control call on the unpatched code first (the v0.3 pattern: "a control call on the unpatched build before any monkeypatch"). Record the red in `bench/RESULTS.md`'s "Seen red once" table, the convention every browser/gate pin in this repo follows.
- Seed with a local `random.Random(n)` instance, never `random.seed()` (the module generator is shared with every other test in the xdist worker). No new dependency (`hypothesis` is not in `[dev]`).
- Budget: the whole 31k grid costs 1.7 s serial. The test belongs in a non-heavy file so it runs in `make verify.fast` (30 s kill, about 11 s used); a few hundred stratified cases are milliseconds. If importing `bench.trochoid` is needed, note `tests/test_calc.py` and `tests/test_trochoid.py` already do (READ), which matters for Pitfall 14.

**Warning signs:**
A test whose assertion is only `slug().endswith(...) == (...)` with no bucket counts; a runtime in milliseconds with 20k random cases (the draw is mostly the cheap branch); a test that never imports `_root_curve`/`_junction` to attack it; a pass the first time it is written.

**Phase to address:** B.

---

### Pitfall 6: Fixing cache-order dependence by leaking `_EXPORTS` state, or by fixing one test of a convention used everywhere

**What goes wrong:**
Three failure modes:
1. `_EXPORTS.clear()` does not exist (READ: `_BlobCache` has `get` and `put` only). Adding a `clear()` to production code for a test, or an autouse fixture that empties the cache after every test, adds API surface or costs rebuilds across the whole suite.
2. A fixture that replaces `app._EXPORTS` but forgets to restore it leaks a fresh or emptied cache into later tests on the same xdist worker. Each worker is its own process (the cache is per-process, as the debt file says), so the leak is intra-worker and depends on scheduling, the same order-dependence being removed.
3. The convention is not local to the two cited tests. `test_pool.py` picks `teeth=43` and `teeth=44` with the comment "a count no other test ever successfully downloads", and `test_api.py` has more (READ: `tests/test_pool.py:262, :293`, `tests/test_api.py` teeth 71 and 73 comments). Fixing two leaves the same hand-kept uniqueness rule elsewhere.

**How to avoid:**
- Use `monkeypatch.setattr(app_module, "_EXPORTS", _BlobCache(budget))` inside the test (or a narrowly scoped fixture): monkeypatch restores automatically, needs no production change, and `app.py` reads the module global at call time (READ: the endpoint references `_EXPORTS`), so it takes effect. The alternative in the debt file (a private cache key such as `face_width=7.7`) keeps the by-hand uniqueness rule and is weaker.
- Keep the non-vacuity assertion the test already has (`r.status_code == 422` and `caplog.records`): a cache hit would be a 200, so the existing assertion is what proves the isolation worked. Prove it red: seed `_EXPORTS` with an entry for the same request (or run after a test that downloads it), watch the 422 become a 200 on the old test, then watch the new test hold.
- Prove order-independence by running the file with the downloading test first via explicit node ids at `-n 0`, plus a few `-n 8` repetitions, rather than asserting "seems independent".
- Note the other instances (`teeth=43/44/71/73`) in the debt entry or a new `nice` item; fix them only if the human asks (surgical edits, CLAUDE.md).
- The test is in `tests/test_api.py`, a heavy file: it does not run in the commit slice, so only the pre-push `make verify` and CI exercise it.

**Warning signs:**
A new method on `_BlobCache` that only tests call; an autouse fixture in `conftest.py` touching `app`; a passing run on one worker that fails with `-n 0` in a different order.

**Phase to address:** B.

---

### Pitfall 7: `stop_group`: reordering the signal and the read creates the hazards the current order avoids

**What goes wrong:**
The fix for "a failed `ps` skips the signals" (READ: `tests/browser_session.py`, `group_members` has `check=True`; `stop_group` reads `ps` before and after each signal) is done by reordering, and one of these slips in:
- **PID reuse.** The group id is the leader's pid. While the leader is un-reaped (a zombie), nothing else can take that pid, so `os.killpg(pgid, ...)` is safe. `proc.wait()` and `proc.poll()` reap the leader. Today the reap is last (`proc.wait` after the loop) (READ). Any `proc.poll()` added "to check whether it already exited" before the signals reaps it, frees the pid and makes the `killpg` a shot at a recycled group number. `_signal_group` also swallows `PermissionError` (READ), which on a recycled group owned by another uid would hide that this happened.
- **Immediate SIGKILL.** "Signal unconditionally" read as "SIGTERM then SIGKILL straight away" removes the SIGTERM grace and defeats the property the test proves (the shipped server stops on SIGTERM within `TERM_BOUND_S`, 0.22-0.25 s measured; READ: RESULTS). The wait between the signals must not depend on `ps` being healthy: on `ps` failure treat the survivors as unknown, sleep the bound, then escalate.
- **A silent pass.** If a failed read is swallowed, the final assertion must still fail ("survivors unknown"), or the teardown reports green with an unverified group.
- **Portability.** BSD `ps` on macOS and procps on the runner both accept `-A -o pgid=,stat=,pid=` (READ: both hosts have run it). Adding `command=` to the helper breaks `len(fields) == 3` for commands containing spaces. Listing the group's commands is a one-off diagnostic, not a change to `group_members`.

**How to avoid:**
- Order: record `pgid = proc.pid`; send SIGTERM; wait up to `TERM_BOUND_S`, polling the group only to end the wait early (a failed read means "keep waiting"); send SIGKILL if the leader or any member can still exist; reap the leader last; final assertion reads once more and fails on survivors or on an unreadable `ps`.
- Do not call `proc.poll()`, `proc.wait()`, `communicate()` or `returncode` before the signals.
- Make the new path testable without a browser: a unit test that starts a real process group (`start_new_session=True`, a small child that ignores or handles SIGTERM, plus a grandchild), patches `group_members` to raise `CalledProcessError`, and asserts the group is gone. The test must clean up after itself in a `finally` with its own `os.killpg`, since the red state of the old code leaves an orphan group (a test of a leak that leaks). It runs in `make verify.fast` as a non-heavy file; a new file there is picked up automatically (the exclusion list names heavy files only; READ).
- See it red first: run the new test against the unfixed `stop_group` and record the orphan. Then re-run the leader-only break from `bench/RESULTS.md` "Seen red once (Phase 21)", row 21-01 "no orphan after the kill" (`os.kill(pgid, SIGKILL)` for `os.killpg`), and confirm the survivor assertion still fires; the debt file asks for this and it is the proof the survivor check was not weakened.
- Also remove the dead first `survivors = group_members(pgid)` (WR-01/IN-01), and fix the failure message's bound (`{bound}` prints the last loop's bound).

**Warning signs:**
A `proc.poll()` in `stop_group`; a `ps` failure that no longer fails the test; `SIGKILL` within the same tick as `SIGTERM`; a new test that leaves `uvicorn` or `sleep` children after a red run (check with `ps -A -o pgid=,stat=,pid=` after the run).

**Phase to address:** C.

---

### Pitfall 8: Writing the group-floor correction from one host's listing, or rewriting the readings

**What goes wrong:**
The comment on `MIN_GROUP_MEMBERS = 3` says "uvicorn plus the shipped pool of 2 workers"; two RESULTS rows say "uvicorn and two pool workers" on macOS and on ubuntu-latest (READ). The reviewer's listing says uvicorn, `resource_tracker` and one worker, and the debt file itself marks the member set an `ASSUMPTION` the orchestrator did not re-list (READ). The fix lists the group on the laptop, corrects the comment and both RESULTS rows, and the Linux row is now wrong or right by accident. Or the RESULTS numbers (3, and "group read 2 before the first build") are edited, destroying a record.

**How to avoid:**
- List the group on each host, from a real run: on macOS during the test (`ps -A -o pid=,pgid=,command=`, one-off), and on Linux from a CI log. For Linux the test run itself must print the listing: add the command column to the already-printed "server group members before the kill" line (a separate `ps` call, not the helper) on a draft PR and read the run's log (the 15-05 draft-PR-to-read-CI pattern). Do not claim the Linux member set from macOS.
- Corrections are dated notes under the rows. "Measurements are records: prose may be corrected, numbers and run headings never" (v0.2 pattern, READ). The reading `3` stays; the dated correction names what the three were. Do not rewrite "before the first build the group read 2" either; its explanation (uvicorn plus the tracker) is the correction.
- Decide, as the debt file asks, whether the floor should name the tracker or force two concurrent builds; if a second worker is forced, that is a behaviour change of the test (a new concurrent build) and needs its own measurement, so default to the comment-only correction.
- The floor stays a non-vacuity check (three live before, zero after); do not lower it to 2.

**Warning signs:**
A RESULTS diff with deleted lines (the v0.2 rule was 0 deleted lines for added-in-PR text, and older rows are never reworded); a comment that names members without a date or a host; the Linux row corrected with no CI run cited.

**Phase to address:** C.

---

### Pitfall 9: The invalid-enum fix changes what a valid link sends or builds (the L05 trap), through the shared code path

**What goes wrong:**
The silent drop happens in two generic places: `readHash()` assigns `input.value = h.get(name) ?? defaults[name]` (a select given a value it has no option for reads `''` at index -1) and `gearQuery()` skips `''` (READ: `app.js`). Any change there is the path every valid link takes. A careless fix changes what some valid link sends, and nothing in the 44 golden records will say so:
- The 44 `golden_requests.json` records are the pre-v0.2 fixture's links (MEASURED: 11 contain `recess_sides=...`, 0 contain `root_shape`). The two enum fields' non-default valid values (`root_shape=trochoid`, `recess_sides=top|bottom|both`) are exercised only by LINK_A / LINK_B and the round-trip steps in `test_browser.py` (READ). The golden sweep guards L05 for numbers well and for enums thinly.
- Empty string. `#root_shape=` (present but empty) is today "an emptied box is its default" (`?? ` does not fire on `''`; `gearQuery` skips it). The API returns 422 for an empty enum. Whether the page now refuses it is a policy call. Silently treating `''` as invalid changes behaviour for links that currently build the default part; silently leaving it changes nothing. Decide it explicitly in the new `Lxx`.
- The same family, undecided scope: `<input type="number">` sanitises a non-numeric value to `''` (standard behaviour; UNVERIFIED in this page, which I did not run), so `#teeth=abc` is dropped the same way. The milestone names enums only. Fixing numbers is scope creep (file an idea per CLAUDE.md); but the new `Lxx` must say enums-only, or the next reviewer will find the numeric twin and call the fix incomplete.
- Source-token pins. `tests/test_api.py` greps `app.js` for exact tokens (the `readHash` loop, the `gearQuery` condition `if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value);`, and L41/L42's added tokens) (READ). Editing those lines turns pins red; the right response is to extend the token list (L42's pattern: "removed none"), not to delete the pin that proves the round trip is generic.
- A refused value must survive the page. The 422 marking path marks `d.loc[1]` (READ: `problems()`), which resolves for a select named `root_shape`. But the value must first reach the request: a select cannot hold a value it has no option for, so the fix needs somewhere to keep the raw string (a temporary option or a side map). Whatever it is, it must not leave a phantom option visible after the user picks a valid one, must not disturb `deriveSelectors()` / `applyRelations()` ordering at `readHash()`'s end, and must keep the fragment (today `update()` rewrites `#root_shape=bogus&teeth=22` to `#teeth=22`, which erases the evidence of what was asked) (READ: RESULTS/pin).
- The fix must be generic over every schema enum (`root_shape`, `recess_sides`), not special-cased to `root_shape`: L02 says the form is generated from `/api/schema` and nothing else, and `test_the_shareable_link_round_trips_every_field_through_generic_code` forbids per-field code.

**How to avoid:**
- Read the `Lxx` decision as the first artifact (the milestone says shape is settled at discuss-phase): enum-only; empty-string policy; whether the page refuses client-side or sends the value for the API to refuse. The milestone's chosen route (the existing 422 marking path) is the cheaper and keeps one source of truth (the API) for what is valid, so prefer sending the raw value and letting the server's 422 mark it, with the select showing the offending value.
- Prove L05 mechanically: after the change, `tests/regression/pre_v0_2.json` and `golden_requests.json` are byte-identical to `v0.5` (`git diff v0.5 HEAD -- ...` empty; the v0.5 audit used exactly this check), the golden sweep passes unchanged, and add a valid-enum row (trochoid, and each `recess_sides` value) to the round-trip step if not already pinned.
- Keep the diff to invalid-link behaviour: the new code path must be unreachable for any value in `prop.enum`.
- Run `make verify` (the browser test is in it) and `make golden.regen` must show an empty diff; if `golden.regen` changes the file, the change is wrong (D-09: only in its own commit).

**Warning signs:**
The golden sweep or round-trip pin goes red for a valid link (that is the fix being wrong, not the pin); `fragment` assertions changing for valid links; a diff touching `gearQuery()` rather than only the enum branch; a new `if (name === 'root_shape')`.

**Phase to address:** D.

---

### Pitfall 10: Flipping the browser pin without seeing it red first, or seeing it red for the wrong reason

**What goes wrong:**
The `root_shape=bogus as today` step asserts today's behaviour in about a dozen sub-assertions (query `teeth=22`, `selectedIndex -1`, fragment `#teeth=22`, no `.error`, API 422) (READ: `test_browser.py`). It is rewritten to the new behaviour in the same commit as the fix, and never observed failing against the new code, so nobody knows whether the old assertions were still reachable or whether the new ones can fail. The repo's own rule is that every pin is shown red once (`bench/RESULTS.md` "Seen red once"), and the history shows the trap: breaks "never reach the new step" because an earlier step fails first (21-04 hashchange break; 21-05 sweep break), so the red seen was not the pin's.

**How to avoid:**
- Order inside the one change: (1) apply the `app.js` fix with the old pin untouched and run the browser test: the `bogus as today` step must go red at the first sub-assertion that the fix changes (and only that step, not an earlier one); record its first failure line. (2) Rewrite the pin to the new contract. (3) Revert only the `app.js` fix and confirm the new pin goes red at the new assertions; record that too. Both lines go in "Seen red once".
- The new pin must assert the three user-visible facts: the invalid value is not dropped from the request, the field is marked (`.invalid` on the wrap, the existing path) with the API's message in `#messages`, and the fragment still carries the asked value. Plus the control that proves L05: the valid-link steps are unchanged and green.
- Keep the string `today's behaviour, filed as debt` and `TODAY` out of the new step's messages: the message names the debt file by path, and that file moves to `resolved/` in the fixing commit (CLAUDE.md), so a stale path in an assertion message misleads.
- The debt must be retired in the same commit (`Status: resolved`, sha, `git mv` to `resolved/`, INDEX row), and the debt file's trigger names finished phases (v0.5 audit item 4), so restating nothing is needed once it is resolved.

**Warning signs:**
One commit that edits both `app.js` and the pin with no recorded red; a "Seen red once" row whose first failure is an earlier step; the old step's `TODAY` constant still referenced after the debt moved.

**Phase to address:** D.

---

### Pitfall 11: Ubuntu 26 migration: fixing before classifying, and mistaking a rolling migration for a single event

**What goes wrong:**
The date gate is 2026-10-19. The migration is not a switch: GitHub states it "will roll out gradually between October 19 and November 19, 2026" (READ: github.blog changelog 2026-09-17; MEDIUM). So after the 19th, successive `ubuntu-latest` runs can land on 24.04 or 26.04; a green run on 24.04 proves nothing about 26.04, a red 26.04 run followed by a green re-run on 24.04 can read as a flake, and the item "first run whose `Set up job` names Ubuntu 26" may not arrive on the 19th. Worse, the first red can be unrelated to the OS (an unrelated flake, the resource-tracker chain, a `main` run reading 487-924 s) and get "fixed" as a migration problem.

**Facts relevant to classification (READ unless tagged):**
- Labels `ubuntu-26.04` and `ubuntu-24.04` exist today, so a deliberate trial run on `ubuntu-26.04` can be made before the migration reaches this repo (changelog, MEDIUM). Using one is a human decision (the debt file reserves pinning `runs-on: ubuntu-24.04` for the human; a trial is a CI change). Note that `ci.yml` has three jobs, all on `ubuntu-latest`: `test (3.12)`, `vendor-bundle`, `image`; all three migrate, and `docker/setup-buildx`, `build-push-action`, `setup-node@v4` with `cache: npm` ride the new image too. Read all three jobs' whole logs, not just `test`.
- Python: the `actions/python-versions` manifest lists 3.12.13, 3.12.14 and 3.12.15 for linux 26.04 and none of the 3.12.12-and-earlier ones (MEASURED today by fetching the manifest). So a `python-version: "3.12"` resolves on 26.04; the interpreter patch can differ from the run that was green on 24.04 (CI saw 3.12.14).
- Playwright: Ubuntu 26.04 support arrived in v1.61.0 (June 2026) per the upstream issue (MEDIUM); this repo pins 1.63.0, whose driver names `ubuntu26.04-x64` (MEASURED: `coreBundle.js` contains the platform entries). That shows the driver knows the platform; it does not show `--with-deps` installs the right libraries there. The upstream issue lists the `t64` renamed libraries (`libasound2t64`, `libatk1.0-0t64`, ...) as what a 26.04 needs (MEDIUM); a failure there reads as an apt error in the install step, a different class from a WebGL or timing failure.
- The browser test fails closed (D-02): a broken install turns `test (3.12)` red on every PR at once, with the failure in the browser test and not in the code under review.
- The canvas PNG ratio bar (4.9) was set from two hosts (macOS, ubuntu-24.04 image); a different Mesa/SwiftShader on 26.04 can move the ratio without the viewer being wrong (READ: `browser_session.py`, `PNG_RATIO_BAR`).

**How to avoid:**
- The item's own rule, kept: classify from the whole log (apt, Python, Playwright install, WebGL ratio, timeouts, the other two jobs) before any fix, as 21-08 did. Write the classification (a short table: step, 24.04 baseline, 26.04 reading) into `bench/RESULTS.md` as a new reading before touching `ci.yml`.
- Record each CI run's image name and version (the `Set up job` group) next to its result for the whole migration window; treat the milestone item as "armed until a 26.04 run has been read", not "done on the 19th".
- If red: pinning `ubuntu-24.04` is the documented fallback and the human's call; a fix to the install (`--with-deps`, package names) is a second option; a ratio-bar change is a third and needs the same two-host derivation (PD-03). If green: record the image version and install seconds and resolve the item in that commit.
- Do not let the date gate block the other phases or the milestone close: schedule E last, or run it as a watch, with the milestone able to close with E honestly open (as v0.1-v0.5 did with named triggers).
- Keep the first-run read separate from other CI noise: re-run a red 26.04 job once on the same label before concluding (the resource-tracker chain also reds `test (3.12)`; classify by the failing test, per Pitfall 3).

**Warning signs:**
An edit to `runs-on` or `BROWSER_INSTALL_ARGS` before the log is read; a "green on 26" claim from a run whose `Set up job` says 24.04; treating `vendor-bundle` or `image` red as unrelated without reading; a RESULTS row with no image version.

**Phase to address:** E.

---

### Pitfall 12: Info-finding triage that closes without reasons, mislabels severity, or turns into refactors

**What goes wrong:**
About 18 info findings are open across Phases 19 and 21-24 (MEASURED by reading the five `*-REVIEW-DISPOSITION.md` tables: 21 IN-01..04; 22 IN-01..03; 23 IN-08, IN-11; 24 IN-01..04 plus CX-03, CX-05; and 19 IN-01, IN-02, IN-04 deferred in a debt file, IN-03 already resolved). The sweep marks them `closed` wholesale, or fixes them as a batch.

**Why it happens / what is really hiding in the list (READ: titles):**
- Severity labels understate. Several "info" findings are about tests that can pass without proving anything, the failure class this repo's retrospectives rank highest: 24 CX-05 ("the request-count assertion can pass before a queued 350 ms debounce fires"), 23 IN-08 ("the driver check cannot tell `hex_cell eq 0.05` from `hex_cell gt 0`"), 23 IN-11 (`_js_number` unguarded outside 1e-6 to 1e21 and for -0.0), 21 IN-03 (the "no path that passes without the browser" scan is line- and spelling-based), 21 IN-04 ("inconsistent waits and a hot loop", adjacent to the flake/hang hunt). Triage by what the finding can do to the gate, not by its label.
- 24 IN-02 / CX-03 (a selector naming an unknown group throws in `buildForm()`, so the page shows the schema message and never calls `update()`) touches the same `app.js` bootstrap as the enum fix (Pitfall 9); order and scope matter.
- 22 IN-03 ("L40 quotes the best-case reading as its cost") and 22 IN-01 (duplicated test block) are record and refactor items; the decision log is append-only, so a correction is a dated note, not a rewrite (READ: v0.2 and v0.3 patterns).
- v0.3's lesson 5 and v0.5's lesson 2 are the same lesson twice: untriaged `open` findings are invisible until an audit. The sweep must end with zero `open`.

**How to avoid:**
- One disposition per finding, in its `*-REVIEW-DISPOSITION.md`, from the closed set the files already use: `fixed` (with sha), `deferred` (with a debt/idea file path), `skipped` (with the reason). A reason in one line for every `skipped`. No bulk "wontfix".
- Triage pass first (read-only), fix pass second: write all dispositions with a proposed action, put the "info that is really a vacuity bug" set in front of the human, and only then change code. Fix only what is tiny and inside this milestone's files; everything else becomes `deferred` with a trigger that names an event.
- Hold the line on scope: a fix is surgical (CLAUDE.md "note the tangent, raise it after"). The IN-01/IN-02 pair for Phase 19 (`_chamfer_tips` re-solving, `bench/trochoid_part.py` near-copies) is a refactor; the debt file already ties it to "when model.py is next touched". Deferring with that trigger is correct.
- Retire debt only in the commit that closes it (CLAUDE.md); the disposition table and the debt file's `Status` move together.

**Warning signs:**
A disposition with `closed` and no sha or path; a diff touching `model.py` or `calc.py` from this phase; a fix that edits a finding's own test to make it pass; fewer than 18 rows touched.

**Phase to address:** F.

---

## Moderate Pitfalls

### Pitfall 13: The hook-pin fix hides the next leak of environment into the pin

**What goes wrong:**
`PYTEST_ARGS` is removed from the test's child environment (`_make_env`), but the failure came from make exporting a command-line variable into recipes' environments (READ: debt file). `_MAKE_VARIABLES` strips make's own flags, and `PYTEST_ARGS` is not on it. A fix that sets `PYTEST_ARGS=` on the dry-run command line works; a fix that only pops the env var may not cover a value passed via `MAKEFLAGS`.

**How to avoid:**
Prove it with a case that runs the pin with `PYTEST_ARGS` set in the environment and again as a `make verify PYTEST_ARGS=...` command-line variable, and see both red against the old helper first (the debt file reproduced the env-var form; the command-line form is what actually bit 21-07). Keep `through_worker_count` and the `--ignore=` assertions unchanged. Mind the recipe-pin behaviour from Pitfall 4 if any new flag lands in `test:`.

**Phase to address:** F.

### Pitfall 14: `make test-image` is worse than the debt file says; "exclude two files" would gut it

**What goes wrong:**
The debt file lists `test_hooks.py` and `test_browser_pins.py`. The image mounts only `src/`, `tests/` and `pyproject.toml` and installs only `pytest` and `httpx` (READ: Makefile). Tests that read other host files or import `bench` / `scripts` (grep, READ): `test_api.py`, `test_cli.py`, `test_bench.py`, `test_pr_land.py`, `test_no_fake_done.py`, `test_skip_tokens.py`, `test_browser_pins.py`, `test_hooks.py`; and `tests/test_calc.py` and `tests/test_trochoid.py` import `bench.trochoid` (READ), which is not in the image. Some of those hits only reference a repo root for a few tests, so the true red set is unknown (UNVERIFIED: the debt file's own ASSUMPTION; I did not run it). Docker is up on this host (MEASURED: `docker info` succeeded), so it can be measured.

**How to avoid:**
Run `make test-image` once and read the red set before designing the fix. Excluding `test_calc.py` and `test_trochoid.py` would drop the product's two largest pure-maths suites from the image run; prefer mounting `bench/` (and whatever else the red set needs, read-only) over a long `--ignore` list, or retire the target's claim. This is the human's choice (CLAUDE.md "stop and ask": locked decision territory), with options priced. Keep `tests/test_browser.py` ignored as today. Do not fix by editing tests to skip when a file is absent; that adds a pass-without-the-thing path (the browser pins already forbid this class, D-02).

**Phase to address:** F.

### Pitfall 15: The launch-failure message "fix" that shifts the stamp's behaviour

**What goes wrong:**
Changing the `$(BROWSER)` stamp to depend on the shell's revision directory changes what `make test` rebuilds (READ: `Makefile` stamp, `test_hooks.py` pins it; "the commit slice never builds it"). The simplest honest fix is text only: print Playwright's own error first, then the advice `rm .venv/.browser && make test`. A stamp change needs the dry-run pin and the "install lines in verify, not in verify.fast" pin kept green and a cold-checkout check.

**How to avoid:**
Text-only unless the human wants the stamp; read `tests/test_hooks.py` pins for `BROWSER_STAMP` first. A message change is unit-testable without a browser (the fail-closed test already sets `PLAYWRIGHT_BROWSERS_PATH` to an empty dir; READ). Keep "fails closed" intact; do not add a skip path.

**Phase to address:** F.

### Pitfall 16: Debt/ledger bookkeeping done out of band

**What goes wrong:**
An item is declared retired in a later commit or a SUMMARY, not in the fixing commit; `INDEX.md` rows or `Resolved in:` shas point at squashed branch commits (an open debt item: `2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`, READ by name). Retiring a flake or hang item that stays `active` is correct; flipping it is not.

**How to avoid:**
For each retired item: `Status: resolved`, `Resolved in:` a sha that will exist on `main` (see that debt item; use the PR's squash after landing or state the branch sha explicitly), `git mv` to `resolved/`, INDEX row moved, all in the fixing commit (CLAUDE.md). Items re-deferred keep `active` and gain the measurement paragraph. State in the final reply whether any item was filed and its path.

**Phase to address:** all.

### Pitfall 17: Gate-cost drift from the work itself, measured on the wrong host

**What goes wrong:**
The 300 s bar (L43) was set on the M5 Max from two non-decisive readings (READ), while the CI job on `main` reads 8.9-16.6 min. New tests (slug totality, stop_group unit, name-test fixture), the journal, and the browser pin changes each add seconds; the milestone ends with the gate near the bar and nobody knows which change did it.

**How to avoid:**
Price each added piece against the same-host `make verify` baseline (v0.4's lesson: "record the delta against the same-host baseline"), keep new tests in non-heavy files where possible, and record deltas in `bench/RESULTS.md`. A change to the 300 s bar is out of scope; surface it if crossed.

**Phase to address:** A, B, C, D (each prices itself).

---

## Minor Pitfalls

### Pitfall 18: Commit trailer and branch hygiene
**What goes wrong:** Mixed `Co-Authored-By` trailers across a model switch (recurring in v0.4 and v0.5). **Prevention:** use the single attribution line given for the session; note a switch rather than mixing.

### Pitfall 19: Verification digests read `stale` again
**What goes wrong:** Five closes, five stale overrides (READ). **Prevention:** do not re-stamp; use `.ai_skills/reverify-phase` only when a phase's report is needed to ship, and record the cause once at the close.

### Pitfall 20: A diagnosis pasted from elsewhere over-claims
**What goes wrong:** The v0.4 crash-report analysis said "every worker", "probably spur" and cost a validation pass (READ: RETROSPECTIVE). **Prevention:** tag every claim in loop notes and decisions `MEASURED/READ/UNVERIFIED`; the xdist OCCT segfault item stays separate from the tracker flake (shared trait is only "whole-suite runs"; READ), so do not merge them in a fix or an explanation.

### Pitfall 21: Date-gated work stranded by a branch
**What goes wrong:** E needs a CI run after 2026-10-19 on a branch that has CI (`gsd/milestone-v0.6-*`), and the first Ubuntu-26 run may be on `main` after a merge, not on the PR. **Prevention:** note which runs count (PR head or push to `main`); a draft PR opened early reads CI (the 15-05 pattern, READ).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `filterwarnings` entry for the tracker warning | Gate green at once | Hides a CPython bug class; the next precondition change is invisible | Only as an explicit human decision, with the upstream citation and measured rate recorded, and a narrow message match |
| `shutdown(wait=True)` added to every pool test unmeasured | Looks like a fix | Cost and a masked cause if timing merely shifts | Only after a reproduction (amplified or natural) goes red to green |
| Random-only totality test | Fast to write | Reaches the cheap branch 89 % of the time, deep branches never | Never as the only mechanism |
| Special-casing `root_shape` in `app.js` | Smallest diff | Breaks L02 and the generic-code pin; `recess_sides` stays silently dropped | Never |
| Tuning the 4.9 PNG bar to turn a red 26.04 run green | Quick CI green | Un-derived bar; masks a rendering change | Only re-derived from both hosts' ratios under PD-03, human's call |
| Marking info findings `skipped` without a reason | Empties the table | Reopens as an audit finding next milestone | Never; one-line reason or a debt file |
| Per-test `--timeout` plugin for the hang | Names a stuck test | New dev dependency, kills evidence, blind to the exit window | Only after the journal and faulthandler prove insufficient |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| pytest-xdist + spawn pools | Treat the failing test as the culprit | Treat it as the victim of whichever GC pass fired; log worker-to-test assignment |
| coverage `multiprocessing` + `--no-cov` arm | Read a no-cov green as "coverage is the cause" | Report it as "timing differs"; keep a separate GC-amplified arm |
| `make -n` hook pin | Add flags to one recipe | Share flags across `test:` and `test.fast:` or use `conftest.py` |
| Playwright `--with-deps` on a new Ubuntu | Assume 24.04 package names | Classify an apt failure separately (t64 renames) from a WebGL/ratio failure |
| macOS vs Linux `ps` | Add columns to the helper | Keep `pgid=,stat=,pid=`; use `command=` only in one-off diagnostics |
| `_EXPORTS` module cache | Clear via new production method | `monkeypatch.setattr` a fresh `_BlobCache` in the test |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Whole-suite loops on the dev host while working | Pool-timeout failures counted as the flake; browser pins slow | Interleave arms; classify by signature; record load | Always on a shared host (v0.5 never got idle) |
| Diagnostics priced on the M5 Max only | CI job past a runner limit or much slower | A/B on the same host and read one CI run | CI jobs already read 487-924 s |
| Full 31k-case sweep inside the commit slice | `make verify.fast` creeps toward the 30 s kill | A few hundred stratified cases; the full sweep stays in `bench/` | Slice has about 10 s of headroom |
| Gate rerun per tiny change in a long loop phase | Hours per day lost | Loop in the background on a quiet window, develop B-F meanwhile on a worktree | Each full gate 3-5 min |

## "Looks Done But Isn't" Checklist

- [ ] **Flake:** a stop rule committed before the first loop, a recorded outcome (capture or bounded non-reproduction), debt file still `active` if no fix, trigger an event
- [ ] **Hang:** evidence armed (journal that survives SIGTERM), priced in the gate, runbook for the exit window; item not marked resolved
- [ ] **Slug totality:** bucket counts asserted non-empty, two unreachable reasons stated, red seen against a monkeypatched `_junction`, seeded with a local `Random`
- [ ] **Name test:** restored cache after the test, red seen when the cache holds the entry, order-independent under `-n 0` reordering and `-n 8`
- [ ] **stop_group:** `ps` failure still signals and still fails the test with "survivors unknown"; leader-only break still red; no `proc.poll()` before signals
- [ ] **Group floor:** listing taken on each host from a real run; RESULTS numbers untouched, dated notes added
- [ ] **Enum link:** golden and fixture files byte-identical to `v0.5`; the old pin seen red against the fix, the new pin seen red without it; empty-string policy decided in the `Lxx`; generic over every schema enum
- [ ] **Ubuntu 26:** a run's image version recorded; classification table before any `ci.yml` edit; all three jobs read
- [ ] **Info findings:** zero `open`; every `skipped` has a reason; every `deferred` has a path; the vacuity-class infos surfaced to the human
- [ ] **Ledger:** retired items moved in their fixing commit; a statement of any item filed and its path in the final reply

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Flake closed on a guess, recurs | Medium | Re-open: `Status: active`, add the recurrence log, restate the trigger; do not delete the earlier non-reproduction |
| Vacuous totality test shipped | Low | Add bucket-count assertions and a monkeypatch red; re-record in RESULTS |
| Cache leaked across tests by a fixture | Low | Replace with `monkeypatch.setattr`; rerun the file in reversed order |
| `stop_group` orphaned a server | Low | `ps -A -o pgid=,stat=,pid=`; `kill -KILL -<pgid>` by hand; add the unit test |
| Valid link behaviour changed by the enum fix | High if shipped | Revert the `app.js` change; golden sweep and fixture bytes are the tripwire (L05) |
| First 26.04 run red and "fixed" blind | Medium | Revert the `ci.yml` change; classify from the whole log; re-apply with the table |
| Info finding closed with no reason | Low | Reopen the row, write the reason or a debt file |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1 Closing on a non-reproduction | A | Stop rule commit predates the first loop; outcome is capture or bounded re-deferral |
| 2 Two variables / incomparable arms | A | One factor per arm; effective `-n` and tool versions logged; signature classification |
| 3 Symptom fix for the flake | A | No `filterwarnings` change without a human decision and upstream citation; a red-to-green on a reproduction |
| 4 Evidence capture cost / blindness | A | A/B gate cost; journal survives a deliberate SIGTERM; recipe pin green |
| 5 Vacuous totality test | B | Bucket counts and a monkeypatch red recorded |
| 6 `_EXPORTS` leak / local fix | B | `monkeypatch` restore; reordered runs; other conventions noted |
| 7 `stop_group` ordering hazards | C | New unit test red then green; leader-only break still red |
| 8 Group-floor correction | C | Per-host listings cited; dated notes; no number rewritten |
| 9 Enum fix changes valid links | D | Fixture and golden byte-identical to `v0.5`; generic code only |
| 10 Pin flipped without seeing red | D | Two recorded reds (old pin vs fix; new pin vs reverted fix) |
| 11 Ubuntu 26 fix before classify | E | Table in RESULTS before any `ci.yml` edit; image version per run |
| 12 Info triage without reasons | F | Zero `open`; reason or path per row |
| 13 Hook-pin env leak | F | Both env-var and command-line forms red then green |
| 14 `test-image` red set | F | `make test-image` read before the fix; human picks mount vs ignore |
| 15 Launch message | F | Text-only unless asked; stamp pins green |
| 16 Ledger bookkeeping | all | Same-commit retirement |
| 17 Gate-cost drift | A-D | Same-host delta recorded per addition |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| A. Flake loops | Non-reproduction read as a fix; arms differ in more than one factor | Pre-registered stop rule, interleaved single-factor arms, signature-classified reds, the 95 % bound written down |
| A. Flake fix | Filter or `shutdown` added on a guess; test id read as the culprit | GC-amplified reproduction arm with a control; victim-not-culprit framing; mitigation named as mitigation |
| A. Hang evidence | `-v`/`--timeout` cost, recipe fork, evidence erased by the kill | Flushed per-worker journal outside the tree, `faulthandler_timeout` tested on purpose, A/B price |
| B. Totality test | 89 % of random draws are the cheap branch; two reasons unreachable | Stratified undercut region, bucket assertions, monkeypatch red, local `Random` |
| B. Name test | Production `clear()`, fixture leak, local fix | `monkeypatch.setattr` a fresh `_BlobCache`; reorder runs |
| C. stop_group | PID reuse via `poll()`, immediate SIGKILL, silent pass, `ps` columns | Signal first, bounded wait, reap last, unit test with its own cleanup |
| C. Group floor | One host's listing generalised; RESULTS numbers edited | Listing from a CI log; dated notes only |
| D. Enum link | Valid links change; empty-string policy; token pins; fragment rewritten | `Lxx` first; byte-identical fixture and golden; extend token pins; generic over enums |
| D. Pin flip | Never seen red, or red at the wrong step | Fix with old pin first, then new pin with the fix reverted |
| E. Ubuntu 26 | Rolling migration, fix before classification, all three jobs | Image version per run; table before edits; human owns pinning |
| F. Triage | Closing without reasons; "info" that is a vacuity bug; refactor creep | One disposition each, read-first pass, deferred items carry event triggers |
| F. `test-image` | Excluding the biggest suites | Run it, read the red set, mount `bench/` or retire the claim |

## Suggested Ordering Constraints (from the pitfalls, for the roadmap)

1. **C before D.** D's red-first protocol and its many browser runs depend on a teardown that cannot leak a server group; C also fixes the comment D's runs read.
2. **A's loops are long and load-sensitive.** Run them in a quiet window or on a dispatch-only workflow, and develop B, C, D, F on a separate worktree meanwhile; do not run the loops concurrently with the browser test or each other.
3. **E last or as a watch.** It cannot be done before the migration reaches this repo (2026-10-19 to 2026-11-19, rolling); the milestone must be able to close with E open and its trigger restated.
4. **F's triage pass first, its fixes last.** Some infos (24 CX-03 / IN-02) touch the `app.js` bootstrap that D edits.
5. **Phases that need deeper research or a human decision before planning:** A (stop rule, GC amplifier, `gc`-threshold plugin design), D (the `Lxx`: empty string, send-vs-refuse-client-side, enum-only scope), F `test-image` (run it, then options).

## Sources

- `/Users/half/git/halfb00t/spur/.planning/PROJECT.md`, `.planning/RETROSPECTIVE.md`, `.planning/STATE.md`, `.planning/milestones/v0.5-MILESTONE-AUDIT.md` (READ)
- `/Users/half/git/halfb00t/spur/docs/tech_debt/active/*.md`, especially the flake, hang, slug-totality, cache-order, stop-group, group-floor, bogus-enum, Ubuntu-26, hook-pin, launch-message, test-image and Phase-19-info items (READ)
- `tests/browser_session.py`, `tests/test_browser.py`, `tests/test_hooks.py`, `tests/test_api.py`, `tests/test_pool.py`, `tests/test_trochoid.py`, `src/spur/app.py`, `src/spur/static/app.js`, `src/spur/params.py`, `src/spur/calc.py`, `Makefile`, `pyproject.toml`, `.github/workflows/ci.yml`, `bench/RESULTS.md` (READ)
- Local measurements 2026-10-15 in `.venv` (Python 3.12.15, pytest 9.1.1): `multiprocessing.resource_tracker` source inspection; `_pytest.unraisableexception` source inspection; random and `bench.trochoid.sweep_cases()` reason counts through validated `GearParams`; golden record enum counts; Playwright driver platform entries; `docker info`; `actions/python-versions` `versions-manifest.json` (MEASURED)
- CPython resource-tracker reentrancy fixes (GH-109629, gh-131788): search results listing CPython commit mirrors, for example https://code.everydayimshuflin.com/greg/cpython/commit/f53e7de6a84a0f535efb75c3671283b801a1af0f and https://remotebranch.eu/Stowage/cpython/commit/f24a012350f71141648cbd61081a25a458dd7fff (MEDIUM; mirrors, not python.org; whether 3.12 will receive gh-131788 is UNVERIFIED)
- GitHub changelog, "Ubuntu 26 generally available and latest migration", 2026-09-17: https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration (MEDIUM)
- Playwright issue on Ubuntu 26.04 support (added in v1.61.0, t64 library names): https://github.com/microsoft/playwright/issues/40117 (MEDIUM)
- `actions/python-versions` manifest: https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json (MEASURED)
