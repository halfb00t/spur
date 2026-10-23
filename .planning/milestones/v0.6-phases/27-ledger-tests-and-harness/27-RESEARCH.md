# Phase 27: Ledger Tests and Harness - Research

**Researched:** 2026-10-20
**Domain:** pytest guard tests, a subprocess process-group teardown, bench records, info-finding fixes (no new library, no `src/spur/` change but one `model.py` signature)
**Confidence:** HIGH (every design below was prototyped in the scratchpad against the real tree and run; the one external dependency is the Linux listing, which only a CI run can supply)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Group floor (REQ-group-floor-recorded-true)**
- **D-01:** `MIN_GROUP_MEMBERS` stays `3`, with a comment-only fix. The comment at `tests/browser_session.py:49` names the members `ps` observed: uvicorn, `multiprocessing.resource_tracker` and one spawned worker on sequential builds, with any Linux difference recorded as read (D-05). The floor is still the kill's non-vacuity check: 3 live members before, 0 after. No second concurrent build is forced, and members are not matched by command. This answers the debt item's open "then decide whether the floor should name the tracker explicitly, or whether a second concurrent build should be forced" with neither.
- **D-02:** A dated correction goes under each of the two `bench/RESULTS.md` rows that say "3 (uvicorn and two pool workers)" (macOS row ~4768, ubuntu-latest row ~4902). No reading is rewritten: `git diff --numstat v0.5 -- bench/RESULTS.md` reports 0 deleted lines.

**19 IN-01/02 in `model.py`**
- **D-03:** Yes, the milestone touches `src/spur/model.py`. `_build` asks `root_mode` once (`model.py:773`), and `_chamfer_tips` receives that `rm` and passes it to `tip_chamfer_effective(p, rm)` (today `model.py:636` calls it without `rm` and re-solves the curve on a chamfered trochoid build). The "one answer" comment becomes true. This is the milestone's only `src/spur/` change. Reversibility: reversible - a signature change to one private function and its two call shapes.
- **D-04:** Two test patches change shape with D-03, not one as the roadmap says:
  - `tests/test_model.py:899` patches `spur.model._chamfer_tips` with a 3-argument lambda.
  - `tests/test_model.py:926` patches `spur.model.tip_chamfer_effective` with `lambda _p: 2.9875`. It breaks if `rm` is passed positionally.

  The proof that nothing else changed is the 44-record fixture staying byte-identical (`git diff --exit-code v0.5 -- tests/regression/`) and the existing chamfer tests staying green. No call-count test: it would pin a private detail, not behaviour. The IN-02 bench half (`bench/trochoid_part.py` reads `rm.curve`, imports the test helpers instead of near-copies, drops the stale "does not exist until 19-04" paragraph) and `_host_state`'s `CalledProcessError`/`FileNotFoundError` catch ride in the same change, as the roadmap and the debt item's next step say.

**Linux member listing**
- **D-05:** The Linux `ps -o pid=,pgid=,command=` listing of the live group comes from **one throwaway CI run**. It is a temporary harness print on a throwaway PR whose workflow runs only the browser test with `-s -n0`, in the shape of 26-02's Ubuntu pre-classification. The listing is read from that run's whole log, the comment cites the run id, image and date, and the PR is closed unmerged. No permanent harness print, summary hook or CI artifact.
  - Why not a print in the harness: pytest captures a passing test's output and `make verify` runs without `-s`. Under xdist the output stays in the worker. A green CI log never shows a print; Phase 26's `twin selectors:` lines were absent from both post-merge `main` logs (`bench/RESULTS.md`, "The D-05 post-merge read (2026-10-20)").
  - The macOS listing is a local run, read the same way. The debt item flags its member set as the reviewer's listing plus the CPython explanation, not the orchestrator's (`ASSUMPTION:` in the item). Both listings are taken before the comment is written.

**Carried from the roadmap (locked, not re-asked)**
- `slug()` totality: a seeded test, milliseconds, in the commit slice. Draws are stratified to reach every reachable refusal reason, with each bucket asserted non-empty. `bracket degenerate` and `curve invalid` are forced by patching and labelled forced. It is seen red against a raising `_junction` and a raising `_root_curve`, both recorded. `make verify.fast` stays under L36's 30 s.
- The failed-build name test: `_EXPORTS` is replaced per test by monkeypatching a fresh `_BlobCache` (`src/spur/app.py:46`, `:88`). It is seen red with the cache pre-seeded under the old code.
- `stop_group`: it signals the group before any `ps` read and before any `proc.poll()`/`wait()`. A failed `ps` fails the teardown as "survivors unknown" with the group already signalled. The SIGTERM grace and the leader-only-break red (row 21-01) are kept. A sub-second unit test in a file whose name has no `browser` proves both paths and cleans up its own group.
- The launch message: text-only. It names a command that installs the browser when the stamp is present but the browser is not, and keeps the literal `playwright install --only-shell chromium` (`tests/test_browser_pins.py:34`).
- 22 IN-03 is a dated amendment to L40, not a rewrite. Every new guard test is seen red once and the red is recorded.

### Claude's Discretion
- The seed, draw count and stratification method for the slug test, within the millisecond budget.
- The throwaway PR's exact workflow edit for D-05, provided it changes only what runs, adds no fix and is closed unmerged.
- Which `test_model.py` patch form replaces each lambda in D-04 (for example `lambda _p, _rm=None: 2.9875`), provided each still patches the same name.

### Deferred Ideas (OUT OF SCOPE)
None. The discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-slug-totality-guarded | seeded ms test in the commit slice: `slug()` raises nothing, ends `_trochoid` exactly when `root_mode` says trochoid, draws stratified, buckets non-empty, two reasons forced | Section "Pattern 1": four proposal boxes, 300 draws each, 0.07 s measured; red against raising `_junction` and `_root_curve` reproduced |
| REQ-failed-build-name-isolated | name test reads 422 under any order/xdist; `_EXPORTS` replaced per test; red when pre-seeded | Section "Pattern 2": `monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(...))`; red and green both run |
| REQ-stop-group-signals-first | signal first; failed `ps` = "survivors unknown"; grace and leader-only red kept; sub-second non-`browser` unit test | Section "Pattern 3": reordered body, fake-`group_members` test, old code red on both paths, new green in 0.05 s; **the image has no `ps` and no playwright** (decision needed, "Open Questions" 1) |
| REQ-group-floor-recorded-true | comment names the `ps`-observed members on macOS and Linux; dated correction under both RESULTS rows | Section "Pattern 4": macOS listing taken (4, 4, 3 members over three real browser-test runs), mechanism read in `pool.py`; Linux listing needs the D-05 run |
| REQ-launch-message-true | message names a command that installs the browser when the stamp is present and the browser absent; literal kept | Section "Pattern 5": wording, the pin that must stay green, and a guard that can be seen red |
</phase_requirements>

## Summary

Nothing in this phase needs a new package or a new technique. Five guard or record changes, plus a ride-along list, all land in tests, `bench/`, `docs/` and one private signature in `model.py`. I prototyped each design in the scratchpad against the real tree: the slug test (1,200 draws, 0.07 s, red against a raising `_junction` and a raising `_root_curve`), the failed-build isolation (old shape reads 200 once the cache is pre-seeded, fresh-cache shape reads 422), the reordered `stop_group` (old code red on both the signal-first and the failed-`ps` assertion, new code green, 0.05 s for the pair), the 23 IN-08 honeycomb state (old states pass `hex_cell eq 0.05` silently, `honeycomb (4)` makes it raise `wrong or extra driver`, the 11 real relations read 154 cells on 14 states).

Three findings change the plan's shape. (1) **The new `stop_group` unit test cannot import `browser_session`**: that module imports `playwright` at the top (`tests/browser_session.py:36`), and `make test-image` installs only `pytest httpx pytest-cov pytest-xdist` (Makefile recipe, pinned as an exact set by `tests/test_hooks.py`), so the import would be a collection error in the image, the exact class of red Phase 26 removed. The image also has no `ps` (`docker run ... command -v ps` printed rc=127 on `spur:latest`). The repo's own precedent for the same constraint is `tests/test_selector.py:230`, which copies `_js_number` "because that module imports playwright and this one must stay in the commit slice". Recommended: move `group_members`, `_signal_group`, `stop_group`, `_log_tail` and the two bounds to a new playwright-free `tests/process_group.py`, and test with a fake `group_members`. (2) **The group floor's members are not "one worker"**: the pool is two single-worker executors routed by `hash(p) % workers` and `hash(GearParams())` is salted per process, so the live group is uvicorn + the resource tracker + one or two workers. Three real `tests/test_browser.py` runs on this host read 4, 4 and 3 members. The comment should say "one or two", matching REQUIREMENTS. (3) **The debt files' line numbers are stale** (`MIN_GROUP_MEMBERS` is at `browser_session.py:57`, not `:49`; `stop_group` at `:115`; `launch` at `:212`; the Phase 21 review lives in `.planning/milestones/v0.5-phases/`, not `.planning/phases/`).

**Primary recommendation:** Do the throwaway CI run (D-05) first and alone, while the tree is clean, because it needs a branch switch and a human push; then run the ledger-test plan, the harness plan and the `model.py` plan in disjoint-file waves; write the `MIN_GROUP_MEMBERS` comment and the two RESULTS corrections last, from both listings.

## Architectural Responsibility Map

Test and harness phase; the "tiers" are the repo's layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `slug()` totality guard | commit-slice unit test (`tests/test_trochoid.py`) | `spur.calc.root_mode` (the oracle) | pure maths, no kernel, must stay in `verify.fast` (L36) |
| Failed-build name isolation | HTTP-tier test (`tests/test_api.py`, heavy set) | `spur.app._EXPORTS` | the cache is module state of the app, replaced per test |
| Group teardown order | test harness module (`tests/process_group.py`, proposed) | `tests/browser_session.py` (caller) | OS process-group semantics; unit-testable without a browser |
| Group floor record | `tests/browser_session.py` comment | `bench/RESULTS.md` (append-only record) | comments carry the measurement (CODING_VALUES) |
| Launch message | `tests/browser_session.py::launch` | `Makefile` `$(BROWSER)` stamp (read only) | text-only |
| `_chamfer_tips` takes `rm` | `src/spur/model.py` (private) | `spur.calc.tip_chamfer_effective(p, rm)` (already accepts it) | one root answer per build (D-03) |

## Standard Stack

No installs. Everything is already pinned and present. [VERIFIED: ran `.venv/bin/python -c ...` this session]

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.1.1 | all new tests | pinned, L23 |
| pytest-xdist | 3.8.0 | `-n 8` gate | pinned |
| playwright | 1.63.0 | the browser test only | exact pin, `tests/test_browser_pins.py` |
| CPython | 3.12.15 (`.venv`) | `random.Random(seed)` sequences are reproducible on the one supported interpreter | L23 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `tests/process_group.py` extraction | import `browser_session` from the new test and add `--ignore=tests/test_process_group.py` to `test-image` | smaller diff in `browser_session.py`, but edits the Makefile recipe, `IMAGE_IGNORED` in `tests/test_hooks.py` and the recipe's comment, drops the test from the image, and a test that is only skipped by file name is not a test of the harness the image can run |
| `bench.trochoid.sweep_cases()` slice for the slug test | seeded random boxes | the sweep is 31,446 cases and 1.9 s (L40); a slice would not be stratified to the undercut region |

**Package Legitimacy Audit:** no external package is installed or recommended in this phase; the audit is empty. `gsd_run query package-legitimacy check` was not run because there is nothing to check.

## Architecture Patterns

### System Architecture Diagram

```
 human push (D-05)                         make verify.fast / make verify
      |                                              |
  throwaway branch --> CI "test" job            pytest -n 8
  (browser test only,                              |
   -s -n0, ps print)                  +------------+----------------+
      |                               |            |                |
   Linux listing (log)      test_trochoid.py   test_api.py     tests/test_process_group.py
      |                     slug() x root_mode  _EXPORTS swap   fake group_members + real sleep
      v                          |                  |             |  (signal-first, failed ps)
 MIN_GROUP_MEMBERS comment <-----+------------------+-------------+--> tests/process_group.py
 + 2 dated RESULTS corrections                                          ^
      ^                                                                  |
 local macOS listing (this research: 4,4,3)          tests/browser_session.py::serve --stop_group-->
```

### Recommended Project Structure
```
tests/
├── process_group.py        # NEW: group_members, _signal_group, stop_group, _log_tail, TERM/KILL bounds (no playwright)
├── test_process_group.py   # NEW: the sub-second unit test (name has no "browser")
├── browser_session.py      # imports the above; MIN_GROUP_MEMBERS comment, launch message, fixture_hashes, _js_number
├── test_trochoid.py        # + the slug totality test beside :225
├── test_api.py             # + fresh-cache fixture; openapi key walk
├── test_relations.py       # + "honeycomb (4)"
└── test_browser_pins.py    # 21 IN-03 (constant match) and the launch-message guard
```

### Pattern 1: slug totality test (REQ-slug-totality-guarded)

**The refusal reasons, verbatim.** [VERIFIED: src/spur/calc.py:1366-1367]
```
RootReason = Literal["not requested", "nothing radial to replace", "tip land gone",
                     "bracket degenerate", "curve invalid", "tooth severed"]
```
`root_mode` order (calc.py:1672-1695 read): `not requested` (root_shape != trochoid) -> `nothing radial to replace` (`pr.rb <= pr.rf`) -> `tip land gone` (`c.a0 < 0`, first line of `_root_curve`) -> `bracket degenerate` (`_junction` returns `None`) -> `curve invalid` -> `tooth severed` (`waist[1] <= 0`) -> otherwise `trochoid` (join `tangent` or `crossing`).

**Reachability.** `tests/test_calc.py` asserts the sweep tally `"bracket degenerate" == 0` and `"curve invalid" == 0` (lines 1603-1604 read), and the same tally lists `"tooth severed": 73`, `"tip land gone": 980`, `"nothing radial to replace": 7175`. So four outcomes are reachable by validated params (trochoid, nothing radial, tip land gone, tooth severed) plus `not requested` (draw `root_shape="radial"`); two are forced.

**Where the undercut region and the thin cases live** (read from the sweep over `bench.trochoid.sweep_cases()`, 76 validated `tooth severed` rows): teeth 6-10, profile_shift -0.6 and -0.5, pressure angle 14.5 and 20, any module, backlash 0 to 1. `tip land gone` needs a pressure angle at or above about 33.5 (calc.py:1620 `c.a0 < 0`; test_trochoid.py shows the limit at 32.14 degrees with backlash 0). `nothing radial` is teeth >= 27 at the defaults.

**Stratified proposal boxes (teeth, profile_shift, pressure_angle), one `random.Random(seed)`:**

| Box | teeth | shift | angle | Aimed at |
|-----|-------|-------|-------|----------|
| applies | 6-26 | -0.6..0.3 | 14.5-25 | tangent + crossing trochoid |
| ignored | 27-200 | -0.6..1.0 | 14.5-35 | `nothing radial to replace` |
| no land | 6-40 | -0.6..1.0 | 33.5-35 | `tip land gone` |
| severed | 6-10 | -0.6..-0.4 | 14.5-20 | `tooth severed` |

module `round(uniform(0.2, 10), 2)`, backlash `round(uniform(0, 1), 2)`, root_fillet `round(uniform(0, 3), 2)`, bore off, `root_shape="trochoid"`; invalid draws (`ValidationError`) are skipped and counted. The bucket is whatever `root_mode` answers, never the box's intent.

**Measured** [VERIFIED: ran in the scratchpad, seed 20261020, 300 draws per box = 1,200 draws, incl. validation, `slug()` and `root_mode`]: buckets `{'trochoid': 555, 'tooth severed': 14, 'nothing radial to replace': 304, 'tip land gone': 15}`; call duration 0.07 s; with the two forced rows 0.11 s for three tests. (A single wide box with 2,000 draws never hit `tooth severed`: stratification is not optional.)

```python
# Source: prototype run this session, tests/test_trochoid.py placement beside :225
import random, typing
from collections import Counter
from spur.calc import RootReason, profile, root_mode

REACHABLE = {"not requested", "nothing radial to replace", "tip land gone", "tooth severed"}
FORCED = {"bracket degenerate", "curve invalid"}

def test_slug_is_total_and_ends_trochoid_exactly_when_root_mode_does() -> None:
    assert REACHABLE | FORCED == set(typing.get_args(RootReason))   # a new reason turns this red
    rng = random.Random(20261020)
    buckets: Counter[str] = Counter()
    for box in BOXES.values():
        for _ in range(300):
            ...  # draw; GearParams.model_validate or `continue` on ValidationError
            rm = root_mode(p, profile(p), requested=p.root_shape, rho=p.root_fillet)
            assert p.slug().endswith("_trochoid") == (rm.mode == "trochoid")
            buckets[rm.reason or "trochoid"] += 1
    assert all(buckets[b] > 0 for b in REACHABLE - {"not requested"} | {"trochoid"}), buckets
```
`not requested`: draw `root_shape` radial for roughly one draw in five so the bucket fills, or assert it with one literal row (the existing test already has `default-gear`).

**Forced rows** (labelled `forced`, `pytest.mark.parametrize` ids `forced-bracket-degenerate`, `forced-curve-invalid`): `monkeypatch.setattr("spur.calc._junction", lambda c, eps: None)` gives `bracket degenerate`; `monkeypatch.setattr("spur.calc._root_curve", lambda c: "curve invalid")` gives `curve invalid`; each asserts `rm.reason`, that `slug()` does not raise and does not end `_trochoid`. `root_mode` and `_root_curve` resolve both names through the `spur.calc` module globals (calc.py:1620, :1688), so patching the module attribute is enough. `tests/test_trochoid.py` already imports `_junction` and `_root_curve` from `spur.calc`.

**Red recording (both required).** [VERIFIED: reproduced in scratchpad with a conftest that swaps `spur.calc._junction` / `_root_curve` for a function that raises `RuntimeError` for the one test] Result: `1 failed, 2 passed` with `RuntimeError: mutated _junction` and `mutated _root_curve` respectively. In the real tree, apply the same mutation as a temporary edit to the `calc.py` function body (or a throwaway `conftest.py`-style fixture), run `.venv/bin/python -m pytest tests/test_trochoid.py -k slug_is_total -n0 --no-cov`, paste the failing line into the plan summary, then `git checkout -- src/spur/calc.py` and confirm `git diff --stat v0.5 -- src/spur/calc.py` is empty. Which draws reach which function: `_junction` runs only for requested + rb > rf + a0 >= 0 draws (the trochoid and severed buckets); `_root_curve` additionally for the `tip land gone` check. A raising `_junction` on a `tangent` join is still called (it returns early inside `_junction`, after the call), so the mutation must raise on entry.

**Cost against L36.** [VERIFIED: ran `make verify.fast` this session, load average 7.63, warm] `922 passed in 9.80s`, `make verify.fast 42.47s user 22.67s system 626% cpu 10.398 total`. The Makefile comment's previous prices are 11.28 s (M2 Max, 2026-10-06) and Phase 23's 15.14 s of the 30 s (`bench/RESULTS.md`). The new test adds about 0.1 s.

### Pattern 2: failed-build name test isolation (REQ-failed-build-name-isolated)

[VERIFIED: src/spur/app.py:88] `_EXPORTS = _BlobCache(int_env("SPUR_EXPORT_CACHE_MB", 64) * 1024 * 1024)`; read sites at app.py:408, :419, :424, :432 resolve `_EXPORTS` as a module global at call time, and `_BlobCache.__init__(self, budget: int)` is app.py:~57-60. The cache key is `(params, fmt, q.quality, encoding)` (app.py:401, `key = (params, fmt, q.quality, encoding)`), so any earlier successful `quality=preview` download of the same gear (the 25-tooth trochoid or the 33.5 degree tip-land gear) answers before the raising backend runs and the route returns 200.

**Where:** `tests/test_api.py:1296` `test_a_failed_build_records_the_name_of_the_part_it_would_have_been` (two parametrized rows, `applies` 25 teeth trochoid and `refused` 33.5 degrees). `tests/test_api.py` already does `from spur import app as app_module` inside tests (e.g. lines 949, 1024, 1036) and imports `from spur.app import STATIC, app, build_backend` at the top.

**Fix:**
```python
@pytest.fixture
def fresh_exports(monkeypatch: pytest.MonkeyPatch) -> None:
    from spur import app as app_module
    monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))
```
Use it on the name test, delete the "downloaded by no other test" comment in its body (it is the maintained-by-hand uniqueness rule), and fix the docstring sentence in `test_a_root_shape_link_is_served_with_the_root_it_cut` (:539) only if the planner chooses to touch it (it describes a harmless collision, not a dependence). The siblings `test_a_failed_build_emits...` (:1255, teeth=71), `test_an_unclassified_exception...` (:1322, teeth=73) and `test_a_tip_chamfer_that_selects_no_tip_arcs...` (:1357, teeth=67) use the same unique-key convention; the fixture would cost them one parameter each. The debt item names only the name test, so that is the required scope; the siblings are a planner call (same defect class, one line each).

**Seen red** [VERIFIED: scratchpad, `TestClient(app)` with the inline backend]: with the 25-tooth trochoid downloaded successfully first, the old shape (raising backend, no cache swap) returns `200` (asserted equal in the prototype); with `fresh_exports` applied and the same pre-seeded global cache, the same request returns `422`. In the real tree: add a temporary line at the top of the old test body that does `client.get("/api/model.stl", params={"quality": "preview", **fields})`, run `-k records_the_name -n0 --no-cov` (red: `assert 200 == 422`), then add the fixture (green with the same pre-seed line), then remove the pre-seed line. Record both.

**24 IN-03 (same file).** `tests/test_api.py:143`: `assert "selectors" not in client.get("/openapi.json").text`. Replace with a recursive key walk over the parsed JSON (`def _has_key(node: object, key: str) -> bool`), and seen-red it with a synthetic document: `{"description": "the selectors field"}` must pass the walk (old substring test red on it), `{"x": {"selectors": []}}` must fail it.

### Pattern 3: `stop_group` signals first (REQ-stop-group-signals-first)

**Current order** [VERIFIED: tests/browser_session.py:115-139 read]: line 121 `pgid = proc.pid`; **line 122 `survivors = group_members(pgid)` (a ps read before any signal, overwritten before use)**; line 123 `bound = TERM_BOUND_S` (dead, overwritten by the loop target); loop over `((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S))`: `_signal_group`, then `group_members` (a raise here skips SIGKILL), poll loop; then `proc.wait(timeout=KILL_BOUND_S)` after the loop; the failure message names only the last `bound`. `group_members` is `subprocess.run([...], check=True)` (line 97-99), so any non-zero `ps` raises `CalledProcessError`. There is no `proc.poll()` in `stop_group`; the only poll is `_wait_for_pool` (:146).

**Reordered shape** [VERIFIED: prototype run, `pg_new.py` vs the old function lifted verbatim as `pg_old.py`]:
```python
def stop_group(proc: subprocess.Popen[bytes], log: IO[bytes]) -> None:
    pgid = proc.pid  # start_new_session makes the leader's pid the group id
    survivors: list[int] | None = []
    for sig, bound in ((signal.SIGTERM, TERM_BOUND_S), (signal.SIGKILL, KILL_BOUND_S)):
        _signal_group(pgid, sig)        # before any ps read, before any poll/wait
        try:
            survivors = group_members(pgid)
            deadline = time.monotonic() + bound
            while survivors and time.monotonic() < deadline:
                time.sleep(0.05)
                survivors = group_members(pgid)
        except (subprocess.CalledProcessError, OSError):   # ps failed or is absent
            survivors = None            # unknown; do not wait, go on to the next signal
            continue
        if not survivors:
            break
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=KILL_BOUND_S)  # reap only after the group has been signalled
    if survivors is None:
        pytest.fail(f"server process group {pgid}: survivors unknown, ps failed; the group was "
                    f"signalled SIGTERM then SIGKILL; server log tail:\n{_log_tail(log)}")
    if survivors:
        pytest.fail(f"server process group {pgid} still has live pids {survivors} after SIGTERM "
                    f"({TERM_BOUND_S:.0f} s) and SIGKILL ({KILL_BOUND_S:.0f} s); "
                    f"server log tail:\n{_log_tail(log)}")
```
This also fixes **21 IN-01** (dead assignment, message names both bounds). A failed `ps` after SIGTERM does not wait the 10 s grace (it cannot observe), it sends SIGKILL at once, which is what keeps the failed-ps test sub-second.

**Leader-only red kept.** [VERIFIED: prototype] With `_signal_group` replaced by `lambda g, s: os.kill(g, s)` (the 21-01 break, `bench/RESULTS.md` row at :4817) and a shell leader `sh -c 'sleep 60 & wait'`, the reordered `stop_group` still raises `Failed: ... still has live pids` (0.98 s with the bounds patched to 0.3 s). Not recommended as a permanent test: it needs real `ps`, which the test image lacks. Re-run it on the real thing for the record: temporarily change `_signal_group`'s body to `os.kill(pgid, sig)`, run `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright .venv/bin/python -m pytest tests/test_browser.py -n0 --no-cov -q` (about 25 s) and paste the `Failed: server process group N still has live pids [...]` line (the SIGTERM grace is unchanged, so also compare `bench/RESULTS.md` row 21-01's "Seen red once").

**The unit test** (file `tests/test_process_group.py`, imports `process_group` only) [VERIFIED: prototype, old red / new green, `2 failed, 2 passed in 0.05s`]:
- spawn `subprocess.Popen(["sleep", "60"], start_new_session=True)` (the image has `sleep`: `/usr/bin/sleep` printed by `docker run --rm --entrypoint sh spur:latest`);
- path 1 (signal-first): wrap `process_group._signal_group` to append `("signal", sig.name)` and replace `group_members` with a fake that appends `("read",)` and returns `[]`; assert `events[0] == ("signal", "SIGTERM")` (old code gives `[("read",), ("signal", ...)]`);
- path 2 (failed ps): fake `group_members` raises `subprocess.CalledProcessError(1, "ps")`; `with pytest.raises(pytest.fail.Exception, match="survivors unknown")`; assert the recorded signals are `["SIGTERM", "SIGKILL"]` and `proc.poll() is not None` (old code raises `CalledProcessError` before any signal and the group lives);
- cleanup in `finally`: `os.killpg(proc.pid, SIGKILL)` suppressed for `ProcessLookupError`, then `proc.wait(timeout=5)` (the project sets `filterwarnings = ["error", ...]`, an un-waited `Popen` is a `ResourceWarning`).
Ordering is recorded, not raced (no assertion on how fast `sleep` dies), so it is deterministic. Tools: ruff `ARG` flags unused lambda args (name them `_g`, `_s`), `TRY`/`PT` rules apply; `pytest.fail.Exception` is the mypy-typed name for the outcome.

**Why `process_group.py`.** [VERIFIED: Makefile `test-image` recipe, tests/test_hooks.py:229-263, tests/browser_session.py:36] The image runs `pip install pytest httpx pytest-cov pytest-xdist`; `IMAGE_IGNORED` is an exact set pinned by `test_the_image_suite_ignores_the_browser_test`; importing `browser_session` would raise `ModuleNotFoundError: playwright` at collection. Moving the five names out keeps `browser_session` importing them (`serve` uses `group_members` and `stop_group`; `_wait_for_pool` and `stop_group` use `_log_tail`). Nothing else imports them (`grep -rn` over `tests bench scripts` finds only `browser_session.py` itself plus the prose in `bench/RESULTS.md:4817`). `tests/test_browser_pins.py::_scan_set` globs `tests/*browser*.py`, so `process_group.py` falls outside the skip-spelling scan; it contains none.

### Pattern 4: group floor record (REQ-group-floor-recorded-true)

**The mechanism is read, not assumed.** [VERIFIED: src/spur/pool.py:96-101] `self._executors = [ProcessPoolExecutor(max_workers=1, mp_context=_SPAWN, initializer=_warm) for _ in range(workers)]` and `executor_for` returns `self._executors[hash(p) % self.workers]`, "D-07: affinity, not load-balance". Each single-worker executor spawns its worker at its first submit. [VERIFIED: ran `hash(GearParams()) % 2` in four fresh interpreters: `0 0 0 1`] the slot is salted per process. So after builds the group is uvicorn + `multiprocessing.resource_tracker` + one worker (every build hashed to one slot) or two workers.

**macOS listing, this host** [VERIFIED: ran `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright PYTHONPATH=<scratch> .venv/bin/python -m pytest -p listplugin tests/test_browser.py -s -n0 --no-cov -q`; the plugin only wrapped `browser_session.group_members` to print `ps -A -o pid=,pgid=,stat=,command=` rows of the group at the floor check; no project file edited]. Apple M5 Max, 18 CPUs, 64 GiB (`sysctl -n hw.ncpu machdep.cpu.brand_string hw.memsize`), macOS 27.0.1, Python 3.12.15, playwright 1.63.0, 2026-10-20, load average about 7.6:

| Run | `server group members before the kill` | Members (command, abbreviated) |
|-----|---|---|
| 1 | 4 | `python -m uvicorn spur.app:app --fd 5`; `python -c from multiprocessing.resource_tracker import main;main...`; two `python -c from multiprocessing.spawn import spawn_main; spawn_main(...) --multiprocessing-fork` |
| 2 | 4 | same shape |
| 3 | 3 | uvicorn; resource tracker; one `spawn_main` worker |

All three runs: `2 passed` (the browser test and the oracle unit test). Also, before any build the group is uvicorn + tracker (2), matching `serve()`'s docstring ("the group read 2 members after /api/health reported a pool and 3 after one preview build"). A separate scratch run with two back-to-back default-quality builds read 4 members, so the reviewer's "a second build added no process" held only for a build routed to the same slot.

**What the comment should say** (replaces browser_session.py:55-57): the floor is the kill's non-vacuity check (3 live members before, 0 after); the live group is uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers (two single-worker executors routed by `hash(p) % workers`, each starting at its first build; 3 with every build on one slot, 4 with both used); macOS M5 Max 2026-10-20 read 4, 4, 3; Linux read from run `<id>` on image `<name> <version>` on `<date>`. Also reword the two other places that say "pool workers": the `serve()` docstring (:168-172) and the assertion message (:201-205), which currently reads "uvicorn plus its pool workers".

**RESULTS.md corrections.** [VERIFIED: bench/RESULTS.md:4768 and :4902 read] Both rows sit inside Markdown tables, so a paragraph cannot go between a table's rows; put one dated correction immediately after each table, naming the row. macOS: the table `#### Readings` of `### Spike readings, macOS (21-01)` ends at the `git status --porcelain --ignored` row (:4780), followed by a blank line and the `PNG_RATIO_BAR` paragraph; the ubuntu table ends at :4903 (`Same job on main, for scale`) before :4905 "The three `main` runs differ". The format precedent is a dated, appended paragraph that states what moved and what stands (e.g. bench/RESULTS.md:4696-4702 "The 19-02 walk above ... is dated history and is not rewritten"). Draft text:

> **Correction (2026-10-20, 27-0N), row "Group members seen before the kill".** The row above reads "3 (uvicorn and two pool workers)". `ps -A -o pid=,pgid=,stat=,command=` on the same group shows uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers: the pool is two single-worker `ProcessPoolExecutor`s routed by `hash(p) % workers` (`src/spur/pool.py`), each spawning its worker at its first build. Read on <host> ... three runs of `tests/test_browser.py` read 4, 4 and 3 members. The count 3 above stands as recorded; only its naming is corrected. `MIN_GROUP_MEMBERS = 3` is unchanged: three live members before the kill and none after is still the non-vacuity check.

The 21-01 "Seen red once" row at :4817 quotes the old failure text and must not be touched (the `git diff --numstat v0.5 -- bench/RESULTS.md` check currently reads `570	0`, i.e. Phase 26's additions only; the bar is 0 deleted lines).

### Pattern 5: launch message (REQ-launch-message-true)

[VERIFIED: tests/browser_session.py:219-227] the message today is `"the headless shell is not installed: run `playwright install --only-shell chromium` (PLAYWRIGHT_BROWSERS_PATH={path}); `make test` runs the install stamp for you.\nPlaywright said: {error}"`. [VERIFIED: tests/test_browser_pins.py:35] `INSTALL_COMMAND = "playwright install --only-shell chromium"`; the pin requires `launch()` to hold a string `ast.Constant` containing it and to call `pytest.fail`. [VERIFIED: Makefile] `$(BROWSER): $(STAMP)` installs with `$(PY) -m playwright install $(BROWSER_INSTALL_ARGS) --only-shell chromium` then `touch`es `.venv/.browser`, and `make test` depends on `$(BROWSER)`, so with a current stamp `make test` skips the install. I confirmed what a missing shell prints today (a run without `PLAYWRIGHT_BROWSERS_PATH` in the environment launched against `~/Library/Caches/ms-playwright`, found nothing and failed with exactly this text), which is the demonstration for the "before".

Recommended wording (print Playwright's error first, then the command that works when the stamp is current): keep the literal in a constant, add `rm -f .venv/.browser && make test` (reruns the stamp recipe under the right `PLAYWRIGHT_BROWSERS_PATH`), and the Linux hint `BROWSER_INSTALL_ARGS=--with-deps` for a missing shared library. Remove "`make test` runs the install stamp for you". The venv path is `$(VENV)` (default `.venv`); say `.venv/.browser` and note `VENV=` overrides. Guard: one assertion in `test_the_browser_test_has_no_path_that_passes_without_the_browser` (or a sibling) that the message constants name `.venv/.browser`, seen red against the old text. Optional, planner's call: it pins prose, but it is the only thing that fails if the advice drifts back to the loop the debt item describes.

### Anti-Patterns to Avoid
- **Reading `ps` to decide whether to signal.** The signal is the goal; `ps` only decides how long to wait and what to report.
- **A rewrite of a RESULTS.md reading.** Append after the table; verify with `git diff --numstat v0.5 -- bench/RESULTS.md`.
- **A permanent harness print for the Linux listing.** Captured output never reaches a green CI log (D-05; the 26 `twin selectors:` lines are the evidence).
- **A call-count test for D-03.** D-04 rules it out.
- **Importing `browser_session` from a commit-slice test.** `tests/test_selector.py:230` records why it copies instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fresh cache per test | `_EXPORTS.clear()` calls or private query keys (`face_width=7.7`) | `monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(budget))` | restores itself, order- and xdist-proof, no uniqueness rule to maintain |
| Reaching a refusal reason | hand-built `Cutter`/`RootCurve` fakes | patch `spur.calc._junction` / `_root_curve` | those two are the only functions that return the unreachable reasons; every other path stays real |
| Enumerating the reasons | a typed list in the test | `typing.get_args(RootReason)` | a reason added later turns the test red until classified |
| A throwaway CI run | a permanent hook, summary writer or artifact | 26-02's throwaway branch + draft PR, closed unmerged | D-05 |
| Ordering assertions | `time.sleep` and "by now it is dead" | recorded events from wrapped functions | no race |

**Key insight:** every guard in this phase is non-vacuous by construction only if a bucket, an event order or a status is asserted from something the test did not choose: `root_mode`'s answer, the recorded call order, the HTTP status with a raising backend.

## Rides-with findings: locations and fixes

Source review docs are in `.planning/milestones/v0.5-phases/{21,22,23,24}-*/NN-REVIEW.md` and `.planning/milestones/v0.4-phases/19-*/`, dispositions in the same dirs (all `open`, except Phase 19's which reads `skipped | 19-REVIEW-FIX.md` while the live record is the debt item). Line numbers below were re-read this session.

| Finding | Where now | Concrete fix | Outside this phase's files? |
|---|---|---|---|
| 21 IN-01 | `tests/browser_session.py:122-123, :135-139` | folded into the `stop_group` rewrite (Pattern 3) | no |
| 21 IN-02 | `tests/browser_session.py:668-698` (`fixture_hash` / `fixture_hashes`) | in `fixture_hashes`, per param: `assert isinstance(value, int \| float \| str) and not isinstance(value, bool), f"record {name!r}: param {key!r} is {value!r}"`; output unchanged, so `tests/regression/golden_requests.json` is untouched (consumers: `tests/capture_requests.py:24`, `test_browser.py:938, :1844`) | no |
| 21 IN-03 | `tests/test_browser_pins.py:43-101` (the `environ` allowance reads the node's first source line, `ALLOWED_ENVIRON_MARKERS = ("SPUR_", "PLAYWRIGHT_BROWSERS_PATH")`) | match the `ast.Constant` strings in the enclosing statement instead of the line text, and soften the docstring ("no path that passes" -> a tripwire). Seen red with two synthetic snippets: `os.environ["X"]  # SPUR_` (old passes, new fails) and a multi-line `os.environ.get(\n "PLAYWRIGHT_BROWSERS_PATH")` (old fails, new passes). REQUIREMENTS lists 21 IN-03 as "fixed, not skipped" | no (REQUIREMENTS says docstring-only is not enough) |
| 22 IN-01 | `tests/test_api.py:926, :1293-1294`, `tests/test_trochoid.py:88, :208` (`_BORE_OFF`) | one shared constant in `tests/composition.py` (the repo's uncollected shared-tables module) imported by both; or accept per the review ("low value either way") and mark `skipped`. Same-file overlap with Patterns 1-2 | no (only if kept) |
| 22 IN-02 | `tests/browser_session.py:646-656` (`serve_stl_from` docstring: "must be served and not the / request aborted") | re-wrap the paragraph to the file's width | no |
| 22 IN-03 | `docs/architecture/decision_log.md` L40 "The browser proof" (`step download name read 1.13 s ... beside step first build drawn at 2.93 s`) | append, at the end of L40 (before `## L41` at :2598), a paragraph in the log's own form: `**Amendment (2026-10-NN, 22-REVIEW IN-03).**` giving the range from `bench/RESULTS.md` "The download step, priced (22-02)": 1.13, 3.20, 3.56 s, mean 2.63 s; 1.13 s was the low outlier; `BUILD_WAIT_MS` conclusion unchanged. Precedent for the form: decision_log.md:1658 "**Amendment (2026-10-06, 14-REVIEW IN-02).**". Also a natural place for one sentence that L40's "Totality" paragraph ("The sweep is a command, not a test") is now guarded by the Pattern 1 test | `docs/` only |
| 23 IN-08 | `tests/test_relations.py:253-262` (`CUTOUT_STATES`), `:289-293` (docstring "Each count gate is probed at two open values"), `:459, :475` (cell counts), comment at :243-252 ("All twelve states"), meta-test `test_a_relation_true_only_at_the_first_open_count_goes_red` | add `"honeycomb (4)": {"hex_cell": 4, "hex_wall": 1}`; the cell assertions are computed from `len(CUTOUT_STATES)` already (no literal to bump, 14 states * 11 relations = 154 cells **[VERIFIED: ran]**); add `("hex_wall", "hex_cell", 0.05)` to the meta-test (it currently hardcodes `1.0` as the `eq` threshold, so give the parametrize a third element); reword "twelve" and "count gate" to "each gate". Seen red: [VERIFIED: ran] old states return 12 cells without raising for `hex_wall <- hex_cell eq 0.05`; with the extra state it raises `wrong or extra driver` | no |
| 23 IN-11 | `tests/browser_session.py:325-333` (`_js_number`) | `number = float(value)`; `assert number == 0 or 1e-6 <= abs(number) < 1e21, ...`; `format(Decimal(repr(number)).normalize() + 0, "f")` so `-0.0` writes `0`. The pairs live in `tests/test_browser.py:604-628` (`test_the_oracle_reads_a_link_as_the_page_does`, a no-browser unit test in the heavy file): add `(-0.0, "0")` and a `pytest.raises(AssertionError)` for `1e21` and `1e-7`. `tests/test_selector.py:226-234` `_page_string` is a documented copy: decide whether to mirror the guard (it is in the commit slice and cannot import the original) | no |
| 24 IN-03 | `tests/test_api.py:143` | Pattern 2 | no |
| 19 IN-01 | `src/spur/model.py:625-636` (`_chamfer_tips(solid, p, pr)` calls `tip_chamfer_effective(p)`), `:768-779` (`_build`) | `_chamfer_tips(solid, p, pr, rm)` -> `tip_chamfer_effective(p, rm)`; `_build` passes `rm`; add `RootMode` to the `.calc` import block (:33-49, alphabetical: after `RootCurve`). `tip_chamfer_effective(p, rm: RootMode \| None = None)` is calc.py:371 and passes `rm` to `tip_chamfer_limit(p, rm)` (:333), so nothing in `calc` changes | `src/spur/` (D-03, the one touch) |
| 19 IN-02 (bench) | `bench/trochoid_part.py:109-121` (`trochoid_curve`: stale "`RootMode.curve` does not exist until 19-04" paragraph, re-solves with `trochoid_root(rm.cutter)`), `:172-215` (`root_edges`, `tooth0_root_edges`, `oracle_reading`) | read `rm.curve` (keep the `ValueError` naming the reason); drop the paragraph. The near-copies are NOT drop-in: `tests/test_model.py:68-101` `_root_edges` asserts, `_oracle_reading` fixes `ORACLE_SAMPLES = 400` while the bench's takes `samples` (40 default, `KERNEL_SAMPLES` elsewhere) and raises `ValueError`. See Open Question 2 | `bench/` (in `mypy` scope) |
| 19 IN-04 (`_host_state`) | `bench/trochoid_part.py:329-348` (`head = subprocess.run(["git","rev-parse","--short","HEAD"], ..., check=True)`) | catch `(subprocess.CalledProcessError, FileNotFoundError)` -> `head = "unknown"`. `tests/test_bench.py` already imports from `bench.trochoid_part` (:65) and is in the commit slice: add one test that patches `bench.trochoid_part.subprocess.run` to raise and asserts the line reads `HEAD: \`unknown\``; red against the old code (it raises) | `bench/`, `tests/test_bench.py` |
| 19 IN-04 (`root_fillet` label) | `src/spur/static/app.js:23` | **Phase 28's** (REQ-root-fillet-label-follows-root), not this phase | out |

D-04 patch shapes [VERIFIED: tests/test_model.py:899, :926, :976 read]: `:899` `lambda solid, _p, _pr: solid` -> `lambda solid, _p, _pr, _rm: solid`; `:926` `lambda _p: 2.9875` -> `lambda _p, _rm=None: 2.9875`. `:976` already patches `tip_chamfer_effective` with `lambda _p, _rm=None: 0.9506` (precedent for the form, no change needed). No other test patches `_chamfer_tips`; its only callers are `_build` and the comment at :431. `tests/test_model.py` is in the heavy set (ignored by `verify.fast`), so the evidence is `make verify` plus `git diff --exit-code v0.5 -- tests/regression/` plus the targeted `-k "chamfer"` run before the commit.

## The D-05 throwaway run (Linux listing)

Precedent shape [VERIFIED: 26-02-PLAN.md tasks 1-3 and 26-02-SUMMARY.md read]: Task 1 (agent) `git switch -c <spike> <base>`, one commit, plain `git commit` (hooks run, `make verify.fast` includes `tests/test_pr_land.py`, which reads only `ci.yml` job **names** (test_pr_land.py:223-292), so keep the three jobs); switch back; Task 2 `checkpoint:human-action` (the human pushes and opens a draft PR; the pre-push hook runs `make verify` on the main checkout, 3-5 min); Task 3 read the whole logs with `gh run view <id> --log --job <job-id>` (never `--log-failed` alone), keep them under the phase directory, record in `bench/RESULTS.md`, close the PR unmerged, leave the remote branch for the human.

Minimal edit for this run, on the throwaway branch only (cut from the Phase 27 branch head, tree clean first; do it **before** other plans start, because 26-02's task 1 switches the shared working tree):
1. `.github/workflows/ci.yml`, the `test` job's `- run: make verify PYTHON=python` -> `- run: make test PYTHON=python PYTEST_ARGS="tests/test_browser.py -s -n0 --no-cov"` (keeps `env: PIP_CONSTRAINT`, `BROWSER_INSTALL_ARGS: --with-deps`). The Makefile comment above `test` documents that a caller's later `-n0 --no-cov` win over `-n $(PYTEST_WORKERS) --cov`. Leave `vendor-bundle` and `image` untouched (`required-jobs.txt` stays in step; the run is not landed).
2. `tests/browser_session.py::serve`, right after `members = group_members(proc.pid)`: a temporary print of the group's rows from `ps -A -o pid=,pgid=,command=` filtered to `pgid == proc.pid`, prefixed with a distinctive marker (e.g. `spur-group-listing:`) so `grep` finds it in the 1,000-line log. Under `-s -n0` it reaches the log.
3. Read the `Set up job` `Image:` and `Version:` lines of the same log (and note it is `ubuntu-latest`; the rollout window is 2026-10-19 to 2026-11-19, ROADMAP Phase 29), because a run on 26.04 in this window is also Phase 29's evidence.

Local macOS listing needs no repo edit: the scratch plugin approach used in this research (a `-p` module that wraps `browser_session.group_members`) is the recommended way to take it again at execution time, so the comment can cite a run made at the planning head.

## Draft triage table (started here, closed in Phase 28)

Recommended home: `.planning/phases/27-ledger-tests-and-harness/27-TRIAGE.md` (ARCHITECTURE.md:211: "one table in the phase directory plus a `docs/tech_debt/active/` file for anything 'filed'"). The authoritative per-finding record stays each `*-REVIEW-DISPOSITION.md` (`fixed` + sha, `deferred` + path, `skipped` + reason; `deferred` and the reason go in the Source cell by hand); Phase 28 writes those. Columns: Finding | Review | Proposed disposition | Fix / path | Phase.

| Finding | Proposed | Fix / path | Phase |
|---|---|---|---|
| 19 IN-01 | fixed + sha | `model.py` D-03 (or `skipped` + reason if the human wants no `model.py` diff, ROADMAP) | 27 |
| 19 IN-02 | fixed + sha | bench half of D-04 | 27 |
| 19 IN-03 | already resolved | `34270c8` (debt file says so) | - |
| 19 IN-04 | split | `_host_state` fixed in 27; `root_fillet` label in 28 | 27 / 28 |
| 21 IN-01, IN-02, IN-03 | fixed + sha | Pattern 3, `fixture_hashes`, pins | 27 |
| 21 IN-04 | split | 04a fixed in 26 (`_follow_link`); 04b filed `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` | 26 |
| 22 IN-01, IN-02 | fixed + sha | shared constant; docstring | 27 |
| 22 IN-03 | fixed + sha | L40 amendment | 27 |
| 23 IN-08, IN-11 | fixed + sha | `honeycomb (4)`; `_js_number` | 27 |
| 24 IN-01, IN-02/CX-03 | Phase 28 | `app.js` comment; "Could not build the form" | 28 |
| 24 IN-03 | fixed + sha | openapi walk | 27 |
| 24 IN-04 | deferred | `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md` | 28 (record) |
| 24 CX-05 | fixed (26) | | 26 |
| Phase 22 WR-01/WR-02 | `deferred` today, become `fixed` | the slug test and the isolation fix retire their debt items | 27 |
| Phase 18 IN-01..08, Phase 10 IN-01/02 | per REQUIREMENTS | closed/filed in 28 | 28 |

Observation for Phase 28, outside this phase's list: `.planning/phases/26-gate-fails-with-a-cause/26-REVIEW-DISPOSITION.md` holds five `| info | open |` rows (IN-01..IN-05) that neither REQUIREMENTS nor the ROADMAP grep (Phases 10, 18, 19, 21-24) covers [VERIFIED: grep this session]. Raise it with the human; do not triage it here.

Debt retirement mechanics [VERIFIED: docs/tech_debt/TEMPLATE.md, a resolved item, INDEX.md read]: in the fixing commit set `Status: resolved`, `Resolved in: <the commit's own subject>` (a sha cannot be known inside the commit; INDEX rows read "<subject> - see the file's own `Resolved in:` field"), `git mv docs/tech_debt/active/<f> docs/tech_debt/resolved/`, move the INDEX row from Active to the top of Resolved. Items: slug totality; failed-build name; stop_group; group floor; launch message. **Do not move** `2026-10-09-phase-19-review-info-findings-deferred.md`: its IN-04 `root_fillet` label is Phase 28's. Edit it in place to say IN-01, IN-02 and the `_host_state` half are fixed (ARCHITECTURE.md:211) and adjust its INDEX trigger text. CLAUDE.md: "state whether you filed any item and its path" before the final reply.

## Common Pitfalls

### Pitfall 1: importing the playwright module from a commit-slice test
**What goes wrong:** `make test-image` fails at collection (no playwright in the image), or the fix quietly adds an `--ignore` and `IMAGE_IGNORED` change.
**How to avoid:** `tests/process_group.py` with no playwright import; the unit test fakes `group_members` (the image has no `ps`).
**Warning signs:** a new row in the Makefile's `--ignore` list; `tests/test_hooks.py::test_the_image_suite_ignores_the_browser_test` red.

### Pitfall 2: the unit test leaks its process group
**What goes wrong:** red on the old code leaves `sleep 60` alive, and an un-waited `Popen` raises a `ResourceWarning`, which `filterwarnings = ["error"]` turns into a failure.
**How to avoid:** `finally: os.killpg(...)` suppressed for `ProcessLookupError`/`PermissionError`, then `proc.wait(timeout=5)`.

### Pitfall 3: a stratification that passes while hitting nothing
**What goes wrong:** one wide box never reaches `tooth severed` (measured: 2,000 draws, 0 hits).
**How to avoid:** four boxes, bucket = `root_mode`'s answer, each bucket asserted `> 0`, plus `get_args(RootReason)` equality. A change of Python's `random` sequence then shows up as an empty bucket, not as a silent pass.

### Pitfall 4: "dated correction under the row" inside a table
**What goes wrong:** inserting a paragraph between table rows ends the table and renders the rest as text.
**How to avoid:** the correction goes immediately after the table; name the row in bold.

### Pitfall 5: the throwaway branch collides with the working tree
**What goes wrong:** 26-02's task 1 switches branches in the shared checkout; a plan executing in parallel edits the wrong branch.
**How to avoid:** sequence it first with a clean tracked tree and a recorded return sha; the human push is a blocking checkpoint.

### Pitfall 6: run order of the `MIN_GROUP_MEMBERS` comment
**What goes wrong:** writing the comment before the Linux log is read leaves "Linux: unknown" in a comment whose job is to carry the measurement.
**How to avoid:** the comment/records plan depends on the D-05 reading and edits `browser_session.py` after the other plans that touch it.

### Pitfall 7: the model.py change touching behaviour
**What goes wrong:** `tip_chamfer_effective(p, rm)` and `tip_chamfer_effective(p)` are the same value only if `root_mode` is pure (it is; the debt item says so).
**How to avoid:** the evidence is the regression replay (`tests/regression/test_pre_v0_2.py`, in the commit slice) and `git diff --exit-code v0.5 -- tests/regression/`, plus the existing chamfer tests. No call-count test (D-04).

## Code Examples

### Fake-`ps` ordering test (sketch; the prototype passed)
```python
# Source: scratchpad prototype run this session (pg_new green, pg_old red)
def test_the_group_is_signalled_before_ps_is_read(monkeypatch, tmp_path):
    proc = subprocess.Popen(["sleep", "60"], start_new_session=True)
    events: list[str] = []
    real = process_group._signal_group
    def spy(pgid, sig):
        events.append(f"signal {sig.name}"); real(pgid, sig)
    def fake_ps(_pgid):
        events.append("read"); return []
    monkeypatch.setattr(process_group, "_signal_group", spy)
    monkeypatch.setattr(process_group, "group_members", fake_ps)
    try:
        with open(tmp_path / "log", "w+b") as log:
            process_group.stop_group(proc, log)
        assert events[0] == "signal SIGTERM", events
    finally:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| "uvicorn and two pool workers" | uvicorn + resource tracker + one or two workers | this phase | comment and two dated corrections |
| `slug()` totality proven by a one-off 1.9 s sweep (L40, "a command, not a test") | a seeded 0.07 s stratified test | this phase | L40's Totality paragraph gets a sentence in the same amendment (planner's call) |

## Runtime State Inventory

Not a rename/refactor/migration phase (one private signature, no stored string). Omitted per the template.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The Linux group will also show uvicorn, the tracker and one or two workers (same code, `procps` `ps`) | Pattern 4 | the comment names a Linux set until the D-05 log is read; the plan must not write the Linux clause before reading it |
| A2 | `python:3.12-slim-bookworm` runner containers keep lacking `ps` (verified on `spur:latest` only) | Pattern 3 | the fake-`group_members` design does not depend on it; only the "real-`ps` leader-only test is not permanent" advice does |
| A3 | The throwaway run's `make test ... PYTEST_ARGS="tests/test_browser.py -s -n0 --no-cov"` behaves on the runner as it does here (later flags win) | D-05 | the first CI attempt might still print nothing; check the Makefile comment's own example before the push |
| A4 | Replacing the near-copies in `bench/trochoid_part.py` by imports from `test_model` is wanted by the human as written in D-04 | Open Question 2 | if not, mark 19 IN-02's bench half `skipped` with the reason (different assert vs `ValueError`, sample counts) rather than force it |
| A5 | `random.Random(seed).randint/uniform/randrange` give the same sequence across the 3.12.x patch releases | Pattern 1 | the non-empty bucket assertions turn a drift into a red, not a silent pass |

## Open Questions

1. **Where do `group_members`/`stop_group` live so the unit test can import them?** What we know: `browser_session` imports playwright at the top and the image has neither playwright nor `ps`. What's unclear: whether the human accepts moving five names to `tests/process_group.py`. Recommendation: extract (smallest surface that keeps `test-image` green and the unit test in the image); the alternative is an `--ignore` for the new test plus `IMAGE_IGNORED` and the recipe comment.
2. **What does "imports the test helpers instead of near-copies" mean in `bench/trochoid_part.py`?** What we know: the helpers differ in error type (assert vs `ValueError`), sample count (400 fixed vs a `samples` parameter) and signature (`pr, teeth` vs `p`). Importing `tests/test_model.py` underscore names from `bench/` pulls a whole test module into a bench process. Recommendation: do IN-02's cheap half (read `rm.curve`, delete the stale paragraph) and `_host_state`; for the near-copies either add a `samples` parameter to the test helper and import it, or record `skipped` with this reason. Put it to the human at plan review; it does not block the rest.
3. **Do the three sibling failed-build tests (teeth 71, 73, 67) get the same fixture?** Recommendation: only if the planner wants the whole uniqueness convention gone; required scope is the name test.
4. **Is the launch-message guard (a prose pin) wanted?** Recommendation: yes, one assertion, seen red against the old text.
5. **Phase 26's own five open info rows** are in no triage list (see above). Surface at Phase 28.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` (Python) | all tests | yes | 3.12.15 | none needed |
| headless shell | local macOS listing, leader-only re-run | yes | `chromium_headless_shell-1243` under `.venv/ms-playwright` (needs `PLAYWRIGHT_BROWSERS_PATH=$PWD/.venv/ms-playwright` when not run via `make`) | `rm -f .venv/.browser && make test` |
| `gh` | D-05 | yes | 2.102.0, logged in as `halfb00t` | none (push is a human step regardless) |
| Docker | `make check`, the ps/sleep probe | yes | 29.8.2 | not needed for the gate |
| `ps` / `sleep` | the real group listing | yes on macOS and ubuntu runner | BSD / procps | the image lacks `ps` (rc=127) |
| git | all | yes | clean tracked tree on `gsd/phase-27-ledger-tests-and-harness` | - |

**Missing dependencies with no fallback:** none. The Linux listing blocks only the comment/records plan until the human pushes the throwaway branch.

## Validation Architecture

Nyquist is enabled (`.planning/config.json` has no `nyquist_validation` key; treated as enabled).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1, pytest-xdist 3.8.0 (`-n 8`), `filterwarnings = ["error", ...]`, `--strict-markers --strict-config` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `make verify.fast` (922 passed in 9.80 s, 10.40 s wall, 2026-10-20) |
| Full suite command | `make verify` (last recorded: `1321 passed in 187.05 s`, 97.99 %, Phase 26 verification) |
| Targeted | `.venv/bin/python -m pytest <file> -k <expr> -n0 --no-cov -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-slug-totality-guarded | total, suffix == `root_mode`, buckets non-empty, forced rows | unit (commit slice) | `.venv/bin/python -m pytest tests/test_trochoid.py -k "slug_is_total" -n0 --no-cov` | no, Wave 0 (add beside `test_trochoid.py:225`) |
| (red evidence) | raising `_junction` / `_root_curve` | temporary mutation | same command with a temporary `raise RuntimeError` in `calc._junction`, then `_root_curve`; expect `1 failed` with that message | n/a |
| REQ-failed-build-name-isolated | 422 under a pre-seeded `_EXPORTS` | HTTP (heavy set) | `.venv/bin/python -m pytest tests/test_api.py -k "records_the_name" -n0 --no-cov` | exists; edit |
| (red evidence) | old shape + pre-seed reads 200 | temporary pre-seed | `assert 200 == 422` | n/a |
| REQ-stop-group-signals-first | signal before read; failed ps = survivors unknown | unit (commit slice, sub-second) | `.venv/bin/python -m pytest tests/test_process_group.py -n0 --no-cov --durations=3` | no, Wave 0 |
| (red evidence) | old order | run the new test against the old `stop_group` | `2 failed` (signal-first assertion; `CalledProcessError`) | n/a |
| (kept) | leader-only break still red | temporary `os.kill` for `os.killpg` + browser test | `Failed: server process group N still has live pids` | exists |
| REQ-group-floor-recorded-true | comment + two corrections | grep/diff | `git diff --numstat v0.5 -- bench/RESULTS.md` -> deleted column `0`; `grep -c "Correction (2026-10-" bench/RESULTS.md` increases by 2; `grep -n "resource_tracker" tests/browser_session.py` hits the comment; `MIN_GROUP_MEMBERS = 3` unchanged | exists |
| REQ-launch-message-true | install command named, literal kept | AST pin | `.venv/bin/python -m pytest tests/test_browser_pins.py -n0 --no-cov` | exists; extend |
| 19 IN-01 | nothing moved | regression + chamfer tests | `git diff --exit-code v0.5 -- tests/regression/`; `.venv/bin/python -m pytest tests/regression tests/test_model.py -k "chamfer or regression" -n0 --no-cov` | exists |
| 23 IN-08 | `honeycomb (4)` makes `eq 0.05` raise | unit | `.venv/bin/python -m pytest tests/test_relations.py -n0 --no-cov` | exists; edit |
| 23 IN-11, 21 IN-02 | range and `-0.0` | unit in `test_browser.py` | `.venv/bin/python -m pytest tests/test_browser.py -k "oracle_reads" -n0 --no-cov` (needs `PLAYWRIGHT_BROWSERS_PATH` for import-time only) | exists; edit |
| `_host_state` | no git -> `unknown` | unit | `.venv/bin/python -m pytest tests/test_bench.py -k host_state -n0 --no-cov` | no, Wave 0 |
| Phase close | gate green, fixture untouched | full | `make verify` (record the result line); `git diff --exit-code v0.5 -- tests/regression/` empty; `git diff --numstat v0.5 -- bench/RESULTS.md` 0 deleted | exists |

### Sampling Rate
- **Per task commit:** `make verify.fast` (pre-commit runs it anyway; under 30 s).
- **Per wave merge:** `make verify`.
- **Phase gate:** `make verify` result line recorded, plus the two `git diff` checks above, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/process_group.py` (extraction) and `tests/test_process_group.py` - covers REQ-stop-group-signals-first
- [ ] slug test in `tests/test_trochoid.py` - covers REQ-slug-totality-guarded
- [ ] `fresh_exports` fixture in `tests/test_api.py` - covers REQ-failed-build-name-isolated
- [ ] a `_host_state` test in `tests/test_bench.py`
- Framework install: none.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so treated as enabled. The phase adds no endpoint, input parser or secret; the surface is process control in tests and a CI workflow edit.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | - |
| V3 Session Management | no | - |
| V4 Access Control | no | - |
| V5 Input Validation | partly | `GearParams.model_validate` stays the single boundary; draws that fail are skipped, not coerced |
| V6 Cryptography | no | - |
| V14 Configuration | yes | the throwaway workflow edit: no secrets, no new action, closed unmerged, remote branch left for the human to delete |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Signalling the wrong process group (reused PID) | Tampering / DoS | signal `proc.pid`'s own group first, before any `poll()`/`wait()` reaps the leader (the reason for the order in the requirement); `start_new_session=True` keeps it a private group |
| Orphaned server surviving a failed teardown (T-21-02) | DoS | signal unconditionally, treat a failed `ps` as "survivors unknown" and still send SIGKILL |
| Shell injection in the unit test's spawn | Tampering | argv list, no shell (`["sleep", "60"]`) |
| A CI workflow edit merging by accident | Tampering | draft PR titled DO NOT MERGE, never `make pr.land`, closed unmerged (26-02 precedent) |

## Plan decomposition (suggestion)

Constraint: `use_worktrees` is false (`.planning/config.json`), so plans share one working tree; `tests/browser_session.py`, `bench/RESULTS.md`, `docs/tech_debt/INDEX.md` and `docs/architecture/decision_log.md` are the contended files.

| Wave | Plan | Owns (files) | Notes |
|------|------|--------------|-------|
| 0 | 27-01 D-05 throwaway run | spike branch only; `.planning/.../investigation/` logs | tracer + `checkpoint:human-action`; tree clean first; do the local macOS listing here too; nothing else runs until the branch switch is back |
| 1 | 27-02 ledger tests | `tests/test_trochoid.py`, `tests/test_api.py`, `tests/composition.py` | slug test (+ both reds), isolation fixture (+ red), 24 IN-03, 22 IN-01; retire the two debt items in their fixing commits |
| 1 | 27-03 harness | `tests/process_group.py`, `tests/test_process_group.py`, `tests/browser_session.py` | extraction, reorder, 21 IN-01, unit test, red against old; leader-only re-run recorded; retire the stop_group item |
| 1 | 27-04 model + bench | `src/spur/model.py`, `tests/test_model.py`, `bench/trochoid_part.py`, `tests/test_bench.py` | D-03/D-04, IN-02 (per Open Question 2), `_host_state`; edit the Phase 19 debt file in place |
| 1 | 27-05 relations | `tests/test_relations.py` | 23 IN-08 only; disjoint |
| 2 | 27-06 harness leftovers | `tests/browser_session.py`, `tests/test_browser.py`, `tests/test_browser_pins.py` | after 27-03 (same file): launch message + guard, 21 IN-02, 21 IN-03, 22 IN-02, 23 IN-11; retire the launch item |
| 3 | 27-07 records | `tests/browser_session.py` (comment, `serve` text), `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `27-TRIAGE.md` | after 27-01's log and 27-03/27-06; the two corrections, L40 amendment, group-floor retirement; phase-close `make verify` result line |

Wave 1 plans touch disjoint files, but each retires a debt item in its own commit, so `docs/tech_debt/INDEX.md` is shared: run Wave 1 serially (or have the executor re-read INDEX before each edit). One concern per commit (CLAUDE.md): the `process_group.py` move is its own commit before the reorder.

## Project Constraints (from CLAUDE.md)

- `make verify` is the gate; state the command and the result line. `make verify.fast` is the commit slice (L36, 30 s).
- Python 3.12 only; vanilla tooling; no new dependency; no `TODO`/`FIXME`/`XXX`/`HACK`/`NotImplementedError` word in a `*.py` file (`make no-fake-done`), and no `type: ignore` in `src/spur/`.
- ruff line length 100, rules incl. `ERA`, `TRY`, `PT`, `ARG`, `RUF`; mypy `--strict` over `src tests docker bench scripts`.
- Comments carry the measurement and the host, image and date (as the `BUILD_WAIT_MS` and `PNG_RATIO_BAR` comments do); `calc.py` never imports `cadquery`; vendor types stop at `model.py`.
- `tests/regression/` byte-identical to `v0.5`; `bench/RESULTS.md` append-only; every new guard test seen red once and the red recorded; debt items retired in the fixing commit (`git mv`, INDEX row); state whether an item was filed.
- New work ships with its tests; surface stop-and-ask triggers (a locked decision that looks wrong, a destructive operation). Nothing here needs a new `Lxx`; the L40 text is an amendment.
- Commit messages: Conventional Commits, normal prose.

## Sources

### Primary (HIGH confidence - read or run this session)
- `tests/browser_session.py` (whole), `tests/test_browser_pins.py`, `tests/test_hooks.py` (image-ignored set), `Makefile` (`test`, `test.fast`, `test-image`, `$(BROWSER)`), `src/spur/pool.py:70-125`, `src/spur/app.py:46-130, 395-440`, `src/spur/params.py:267-295`, `src/spur/calc.py:333-378, 1360-1790`, `src/spur/model.py:618-640, 755-800`, `tests/test_model.py:55-125, 885-980`, `tests/test_trochoid.py`, `tests/test_calc.py:1560-1620`, `tests/test_api.py:1-75, 136-170, 1255-1380`, `tests/test_relations.py:225-480`, `bench/trochoid_part.py`, `bench/RESULTS.md` (rows 4768, 4902, 4817, sections 21-01, 21-02, 22-02, 26-02), `docs/architecture/decision_log.md` L40, `docs/tech_debt/*` (five items, INDEX, TEMPLATE, a resolved sample)
- `.planning/phases/26-gate-fails-with-a-cause/26-02-PLAN.md`, `26-02-SUMMARY.md`, `26-REVIEW-DISPOSITION.md`; `.planning/milestones/v0.5-phases/{21,22,23,24}-*/*-REVIEW*.md`; `.planning/research/ARCHITECTURE.md` section 3.11, `FEATURES.md`
- Ran: `make verify.fast`; three `tests/test_browser.py` runs with a listing plugin; slug, `stop_group`, isolation and IN-08 prototypes in the scratchpad; `docker run --rm --entrypoint sh spur:latest -c 'command -v ps; command -v sleep'`; `hash(GearParams()) % 2` in four processes

### Secondary / Tertiary
- None. No web source was needed; CPython `ProcessPoolExecutor` behaviour is read from this repo's `pool.py` and observed, not cited.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no change, versions read from the venv
- Architecture: HIGH - each design prototyped and run, reds reproduced
- Pitfalls: HIGH for the image/playwright and `ps` findings (read and run); MEDIUM for the CI-run mechanics (A3) until the run exists

**Research date:** 2026-10-20
**Valid until:** 2026-11-19 (the Ubuntu 26 rollout window changes what the throwaway run's image line may say; the code reads stay valid until `tests/browser_session.py` or `pool.py` change)
