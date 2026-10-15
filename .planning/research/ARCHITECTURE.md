# Architecture Research: v0.6 Clean Ledger (integration points)

**Domain:** debt sweep on the shipped spur app (gate, test harness, CI, one form behaviour)
**Researched:** 2026-10-15
**Confidence:** HIGH for file/line facts and pins (read in the tree, three claims re-measured here); MEDIUM for the resource-tracker mechanism and the Ubuntu 26 schedule (upstream sources, summarised); LOW where marked `ASSUMPTION`.

Scope: no new component. Every item edits an existing seam. This file says which seam,
what pins it, what moves downstream, which items collide, and the order. Line numbers are
current as of `3726242` and differ from the debt files in several places (flagged inline).

## 1. Findings that change the plan (read first)

| # | Finding | Evidence | Consequence |
|---|---------|----------|-------------|
| F1 | **`main` CI is red twice on a browser-test race that is in no debt file and not in the milestone list.** Both failures are `tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` -> `AssertionError: twin selectors: 1 request(s) sent by two pending picks` (`assert 266 == 265`). Run `38347283201` (push of Phase 24, 2026-10-13, `1 failed, 1310 passed`) and run `38680454993` (push of the v0.5 close, 2026-10-15, `1 failed, 1317 passed in 401.82s`). The PR runs of the same trees were green. | `gh run view --log-failed`. Code: `tests/test_browser.py:1576` reads `requests_before = len(seen)` right after `expect_request(/api/info)` plus two Playwright round trips; the page's own `api/model.stl` request (aborted by the route, but still a `request` event the recorder counts) is sent after the info response, so on a slow runner it lands after the baseline and before the `:1611` assertion. | Add it to the milestone. It is the same family as the already-filed CX-05 (24 info finding: the same assertion is also too weak before the 350 ms debounce). One fix covers both: wait for the STL request, then settle past the debounce, then take the baseline. `ASSUMPTION` on the mechanism: two identical logs, no local reproduction. Under the milestone's own rule (fix a flake only from a captured reproduction) the two logs are the capture; the fix is deterministic and cheap, so file the debt item and fix in one commit. |
| F2 | **`slug()` cannot be driven to all six `root_mode` reasons with real parameters.** `bracket degenerate` and `curve invalid` are never produced by a validated `GearParams`: `tests/test_calc.py:1603-1604` asserts `tally["bracket degenerate"] == 0` and `tally["curve invalid"] == 0` over the 10,326-curve sweep, and `bench/trochoid.py:387` (`_REFUSALS`) names only three refusals. Existing tests reach those two only with hand-built `Cutter`s (`tests/test_trochoid.py:436-439`, `:1229`, `:1254`). | read | The debt file's "slice of `sweep_cases()` covering every refusal reason" and the milestone's "reaching every `root_mode` refusal reason" cannot be met literally by real inputs. Reach the two by `monkeypatch.setattr("spur.calc._root_curve", ...)` returning the reason, and label those rows as forced (L08: do not claim reachability). The four reachable outcomes (`not requested`, `nothing radial to replace`, `tip land gone`, `tooth severed`, plus `trochoid`) come from real seeded parameters. |
| F3 | **Group floor: the debt file's claim is confirmed, measured today.** macOS, Python 3.12.15, real `uvicorn spur.app:app --fd` in its own session: after `/api/health` reports a pool the group holds **2** (uvicorn + `multiprocessing.resource_tracker`); after one preview build **3** (+ one spawned worker); after six builds on different gears **4** (the second worker appears only when a gear hashes to the other slot, `pool.py:101` `hash(p) % workers`). | scratch script, `ps -A -o pgid=,stat=,pid=,command=`; command lines read | The comment at `tests/browser_session.py:55-57` and both `bench/RESULTS.md` rows (`:4768`, `:4902`) are wrong about what 3 means. The floor still works as a non-vacuity check for the kill. Linux is not yet listed: make the `print` at `browser_session.py:200` emit member commands so the next CI log carries the Linux listing for free. |
| F4 | **The resource-tracker warning is the *post-fix* face of CPython gh-109629.** That fix (merged to main, backported to 3.12 as PR #109898 and 3.11) added a recursion-count check so a garbage-collection-triggered re-entry into `ResourceTracker` warns ("ResourceTracker called reentrantly ... might leak") instead of deadlocking. That is exactly the message in the debt file. | WebFetch of cpython#109629 (summary, MEDIUM) | (a) The trigger is GC timing inside the process that owns the executor, which fits "whole-suite only" better than any xdist-versus-coverage story. (b) `ASSUMPTION`: the unexplained 98 % hang may be a related uncaught re-entry path; the two items may share a root. Do them in one phase, hang evidence second. (c) The honest fix is an explicit `shutdown(wait=True)` in `tests/test_pool.py` for executors left to the finalizer, or a narrow `filterwarnings` entry (the latter weakens `filterwarnings = ["error"]`, so it needs a human decision and an `Lxx`). |
| F5 | **`make test-image` is almost certainly red on collection, for more files than the debt names.** The image mounts only `src/`, `tests/`, `pyproject.toml` (Makefile `:219-226`); `README.md` is in `/app` from the Dockerfile `COPY`. Importing host-only trees: `tests/test_calc.py:27` and `tests/test_trochoid.py:21` and `tests/test_bench.py:45-65` (`bench`), `tests/test_pr_land.py:29` and `tests/test_skip_tokens.py:20` (`scripts`). Reading/running host files: `tests/test_hooks.py` (Makefile, `.pre-commit-config.yaml`, runs `make`), `tests/test_browser_pins.py` (Dockerfile), `tests/test_no_fake_done.py` (Makefile, git), `tests/test_pr_land.py:273` (`.github`). `tests/test_calc.py` is the largest unit file, so "exclude by name" gives away most of the image suite's value. | grep; no image built (no `spur:*` image locally, Docker is up) | Step 1 of that item is the run the debt file asks for (`make test-image`), not a design. Likely best shape: mount `bench/` and `scripts/` read-only, set `PYTHONPATH=/app/src:/app`, and `--ignore` only the files that need `make`/git/Dockerfile/`.github`. The choice is the human's (two options, one recommendation, per CLAUDE.md). |
| F6 | **`#root_shape=bogus` has a second victim and one more sibling.** `recess_sides=bogus` is the same defect (the second enum select in the schema). A number box has the mirror: `#teeth=abc` is sanitised by `<input type=number>` to `''` and dropped by `gearQuery()`. And `#root_shape=` (empty) is a 422 at the API (verified: `literal_error`, input `''`) but the page treats `''` as "default". | `TestClient` run today; HTML number-input value sanitisation (spec behaviour, not browser-tested here) | The fix must be generic over every `prop.enum` select, not `root_shape`-specific (a pin forbids quoted field names outside `DIMS`, see 3.7). Decide at discuss-phase whether `''` and non-numeric number boxes are in or out; recommended: enums and the `''`-on-enum case in, number boxes filed as new debt (an `Lxx` that names the boundary). |
| F7 | **The Ubuntu 26 flip is a four-week window, not a day.** `actions/runner-images#14748`: migration begins 2026-10-19 and completes 2026-11-19, gradually. `actions/setup-python` on 26.04 only installs recent patch versions; `ci.yml` asks for `"3.12"` (a minor), so it is not the hazard the issue describes. All three required jobs (`test (3.12)`, `vendor-bundle`, `image`) run on `ubuntu-latest`. | WebFetch of the issue (MEDIUM, summarised); `ci.yml` read | Any PR from 10-19 on may land on either image. A red `test (3.12)` is ambiguous unless the `Set up job` group is read first (it prints `Image: ubuntu-24.04`, verified on run 38680454993). Land the code phases that touch CI-visible behaviour before 10-19 where possible. |
| F8 | **Debt-file line numbers are stale** (Makefile `:170` is `:177`; `tests/test_hooks.py:90` is `:120`; `browser_session.py:49` is `:55-57`, `:91/116/120` are `:90/122/127`, `:217` is `:224-226`). The hook-pin failure is reproduced today: `PYTEST_ARGS=--ignore=tests/test_browser.py pytest tests/test_hooks.py::test_verify_and_verify_fast_share_...` fails at `:120`. | run today | Plan from the numbers in section 3, not from the debt files. |

## 2. The architecture this milestone touches

No runtime module changes shape except `static/app.js` (one generic branch). The rest is the
verification chain. Arrows are "calls / reads"; the number is the item (section 3).

```
developer / agent
   |  make verify  (pre-push, CI)          make verify.fast (pre-commit, <30 s)
   v                                          v
Makefile:  verify.static ----------------- verify.static          <- pins: tests/test_hooks.py
           test  (:176-177)                 test.fast (:201-205)       (recipe prefix, 5 heavy files,
             pytest -n 8 --cov $(PYTEST_ARGS)                           test-image --ignore, stamps)
             [1 loops, 2 hang evidence, 9 hook pin]
           test-image (:219-226) [12]
   |
   v
tests/ ---- test_pool.py -> BuildPool (spawn ctx, 2 single-worker executors)  [1 tracker flake]
       |--- test_api.py  -> TestClient + module-level app._EXPORTS byte cache   [4 cache order, 12]
       |--- test_trochoid.py -> GearParams.slug() -> calc.root_mode             [3 slug totality]
       |--- test_browser.py + browser_session.py -> real uvicorn (own process group) + Playwright
       |        stop_group / MIN_GROUP_MEMBERS / launch() message               [5, 6, 13]
       |        step "root_shape=bogus as today"                                [7]
       |        step "twin selectors"                                           [F1]
       '--- regression/pre_v0_2.json + golden_requests.json (frozen; must show an empty diff)
   |
   v
src/spur/static/app.js: buildForm (enum select) -> readHash -> gearQuery -> update -> problems()
                        [7 bogus enum; info: stash, bootstrap message, DIMS label]
.github/workflows/ci.yml: runs-on ubuntu-latest x3 jobs  [8 Ubuntu 26]
bench/RESULTS.md: append-only record of readings        [1, 2, 5, 6, 8 all write here]
docs/architecture/decision_log.md: L44+ for 7 (and 1 or 2 if the gate or filter changes)
```

## 3. Item by item

Legend for downstream: **R** records (`records.py`), **F** fixture (`tests/regression/pre_v0_2.json`), **G** `golden_requests.json`, **B** browser-test pins, **RES** `bench/RESULTS.md`, **DL** decision log, **DOC** other docs/debt ledger. "New" = new file/test/function; "Mod" = edit.

### 3.1 Item 1 - `resource_tracker` flake (`2026-10-06-resource-tracker-flake-fails-the-gate.md`)

| Aspect | Detail |
|---|---|
| Step 1 (no code) | Whole-suite `make test` loops, unmodified recipe: `make test PYTEST_ARGS="-v --durations=20" 2>&1 \| tee <log>`, N=20 at `-n 8 --cov` and N=20 at `-n 8 --no-cov`, interleaved, stop-and-keep on the first failure. `PYTEST_ARGS` is caller-wins (`Makefile:158`), so no recipe edit is needed to get ids. Rate on file: 2 in 12 local whole-suite runs plus the 5th occurrence (1 in 2) and one CI hit; at 15 %, 20 loops miss with p about 4 %. About 40 runs x 3-5 min = 2-3.5 h of an idle host; record 1-minute load per run. Nothing else may run `make verify` meanwhile (load changes the rate). |
| Files if a fix is chosen | `tests/test_pool.py` (executors left to the finalizer: explicit `shutdown(wait=True)`); **not** `src/spur/pool.py` unless a leak is localised to it. Touching `BuildPool.shutdown` fires three other triggers at once (the 98 % hang, the wedged-worker item, the worker-coverage-flush item). |
| Alternative | A `filterwarnings` entry in `pyproject.toml` (`[tool.pytest.ini_options]` currently `error` plus two ignores) naming `ResourceTracker called reentrantly`. Weakens the gate: human decision plus an `Lxx` (L13). |
| Downstream | R none. F/G none. B none. RES: new section with the per-loop table, host load, the 95 % bound (about 3/N). DL: only if a filter or a recipe change lands. DOC: debt file gets the measurement (re-deferral) or `Status: resolved` + sha + `git mv` + INDEX row, same commit. |
| Conflict | None with an `Lxx`. Milestone rule (fix only from a capture) holds. |
| Shares files with | Item 2 (same reading, same `Makefile` `test`), item 4 no, F1 no. |

### 3.2 Item 2 - 98 % hang evidence (`2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`)

| Aspect | Detail |
|---|---|
| Deliverable | Evidence capture, not a fix. The log shows about 1,200 of 1,220 items reported, so roughly 20 tests were still unreported: the stall may be inside a test, not only in worker exit. |
| Change | Smallest zero-dependency form: `faulthandler_timeout = <measured seconds>` in `[tool.pytest.ini_options]` (dumps every thread's traceback of a test that overruns; it dumps, never fails) and per-test ids in the log via `-v` in the `test` recipe only (`Makefile:177`; `test.fast` stays quiet). Pick the timeout from one `--durations` reading of the heaviest healthy test (the browser test is one long test), not a guess (L34: a gate cost is measured first). `pytest-timeout` is the heavier alternative (a new dev dependency; `requirements.txt` stays byte-identical because it is the runtime closure). |
| What it cannot catch | A stall after every test has reported (xdist worker exit, coverage data flush). That window needs the captured whole log plus `ps` at the time; say so in the debt file rather than claim coverage. |
| Pins that move | `tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` compares the two pytest lines only through `-n <N>` (`:116-120`), so a flag after the worker count is safe; `--ignore=` and `--cov`/`--no-cov` assertions stay. `pyproject.toml` is mounted into `test-image`, so an ini option applies there too. |
| Downstream | RES: one reading of the log-size and gate-time cost against the 300 s bar (L43; no check enforces it). DL: a short `Lxx` is advisable if the gate recipe changes (it amends L13/L34's "one definition of passing"). DOC: debt file revised to name the new evidence and keep its trigger; **do not close it** (no repro). |
| Shares files with | Item 1 (Makefile `test` recipe, RES), item 9 (`tests/test_hooks.py`). Do item 9 first. |

### 3.3 Item 3 - `slug()` totality (`2026-10-15-slug-totality-is-not-guarded-in-the-gate.md`)

| Aspect | Detail |
|---|---|
| Code today | `src/spur/params.py:285-287` `slug()` calls `calc.root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet)`; records call it at `src/spur/records.py` `_gear_fields` (`"slug": p.slug()`); the header at `src/spur/app.py:496`. |
| New test | Beside `tests/test_trochoid.py:225` (`test_the_download_name_follows_the_root_root_mode_builds`), in the commit slice (`test_trochoid.py` is not one of the five heavy files; `slug()` costs 2-38 microseconds). Seeded draws of validated `root_shape="trochoid"` requests; assert no exception and `slug().endswith("_trochoid") == (root_mode(...).mode == "trochoid")`. Assert the set of reasons actually reached equals the four reachable ones so a silent narrowing fails; force `bracket degenerate` and `curve invalid` by patching `spur.calc._root_curve` (works because `root_mode` resolves it at call time and `slug()` imports `root_mode` locally). |
| Red proof (project convention) | Make `root_mode` raise on one reachable case and see the test fail; revert. |
| Downstream | R: no change; a `build.failed` row with the forced reasons is optional, not needed. F/G none (the corpus is frozen at v0.1 `b3ca789`; `tests/regression/corpus.py` header says later test edits never enter it). DL: L40 D-02 ("slug stays total") gains its guard; no new `Lxx`. DOC: debt file retired in the same commit. |
| Conflict | F2 above (literal "every reason" is not reachable by real inputs). Wording in the retirement note must say which two were forced. |
| Shares files with | `tests/test_trochoid.py` (also imports `bench.trochoid`, so it cannot run in the image: item 12), 22-IN-01 (`_BORE_OFF` duplicate lives at `test_trochoid.py:208` and `test_api.py:~1120`). |

### 3.4 Item 4 - failed-build name test isolation (`2026-10-15-failed-build-name-test-depends-on-cache-order.md`)

| Aspect | Detail |
|---|---|
| Code today | `tests/test_api.py:1296` `test_a_failed_build_records_the_name_of_the_part_it_would_have_been` gets its 422 from a raising backend only while `spur.app._EXPORTS` (`src/spur/app.py:88`, a `_BlobCache`) lacks the key; isolation is a comment (25-tooth trochoid and the 33.5 degree gear are "downloaded by no other test"). The cache is per process, so xdist scheduling matters too. |
| Recommended change | Give the test its own cache: `monkeypatch.setattr("spur.app._EXPORTS", _BlobCache(<small budget>))` (the endpoint reads the module global at call time). Hermetic and independent of both rows. The debt file's alternatives (`face_width=7.7`, or clearing `_EXPORTS`) also work but leave a uniqueness convention to maintain. Do not apply a module-wide autouse reset: many `test_api.py` tests rely on cache hits within themselves and every rebuild is about a second of `test_api.py`'s share of the gate. |
| Same convention elsewhere | `test_api.py:1267-1271` (`teeth=71`), `:1339-1342` (`teeth=73`), `:1370`; same fixture could serve them, but the milestone item names one test. Surgical default: fix the one, note the others. |
| Downstream | F/G none: golden has a key for the sibling `test_a_failed_build_emits_build_failed_naming_the_class_and_the_level` (`teeth=71`) only because the frozen corpus tagged it at v0.1; do not alter that sibling's params. R none. DOC: debt retired in the same commit; the docstring at `test_api.py:539` ("same convention") can lose the claim. |
| Red proof | Add a download of the same gear earlier in the file, see the old test go 200, see the new one stay 422. |

### 3.5 Item 5 - `stop_group` ordering (`2026-10-10-stop-group-reads-ps-before-it-signals.md`)

| Aspect | Detail |
|---|---|
| Code today | `tests/browser_session.py:90-105` `group_members` (`ps ... check=True`); `:115-139` `stop_group`: dead first read at `:122` (overwritten at `:127`), a read after each signal at `:127` and `:130`; a `CalledProcessError` there skips the next signal. Also `bound` is overwritten by the loop target (21-REVIEW IN-01: the failure text names only the SIGKILL bound). |
| Change | `_signal_group(SIGTERM)` first, no read before it; read the group only to decide how long to wait and for the final assertion; a failed `ps` becomes "survivors unknown" and still sends SIGKILL, then fails with that wording; drop the dead assignment; format the message with `TERM_BOUND_S` and `KILL_BOUND_S` (absorbs 21-IN-01). |
| New test | `stop_group` has no unit test today (grep: only `browser_session.py` and `capture_requests.py` use it). Add one that starts a real two-process group with `start_new_session`, patches `group_members` to raise, and asserts the group is dead afterwards plus the failure wording. Name the file without `browser` (for example `tests/test_group_teardown.py`): `tests/test_browser_pins.py::_scan_set()` globs `tests/*browser*.py` and applies the no-skip spelling scan (`skip`, `xfail`, `environ`, `getenv`, `pytestmark`) to every match. A file outside the glob is not heavy and joins `make verify.fast` by design (L36); keep it well under a second. |
| Red proof | The 21-01 "Seen red once" row (`bench/RESULTS.md:4817`, leader-only SIGKILL) must still go red; re-run and add a dated reading, never rewrite the row. |
| Downstream | B: `test_browser_pins.py` must stay green (no new watched spelling in `browser_session.py`). RES: new dated reading. DOC: debt retired, INDEX row moved. DL none. |
| Shares files with | Items 6 and 13 (all three edit `browser_session.py`; one phase, one pass). |

### 3.6 Item 6 - group-floor comment (`2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`)

| Aspect | Detail |
|---|---|
| Change | Comment at `tests/browser_session.py:55-57` ("uvicorn plus the shipped pool of 2 workers") becomes the observed members: uvicorn, the resource tracker, at least one worker; a second worker only when a second gear hashes to the other slot. `serve()` docstring `:169-171` and the assertion text `:201-205` say "pool workers (>= 3)": correct them too. Optional: print `members` with commands at `:200` (Linux listing in the next CI log). |
| RES | Dated correction **under** the two rows (`bench/RESULTS.md:4768` macOS, `:4902` ubuntu-latest), not edits to them; the macOS listing is item F3's measurement (2026-10-15). The ubuntu-latest listing waits for a CI log (free if the print is extended; do it before the Ubuntu 26 reading so one run serves both). |
| Decision for the human | Keep the floor at 3 (honest comment only), or force a second concurrent build so both workers appear. Recommendation: keep 3 and fix the comment; the floor's job is non-vacuity of the kill, and forcing a second build adds a build to every browser test run. |
| Conflict | None. Debt file's own `ASSUMPTION` is now measured on macOS. |

### 3.7 Item 7 - bogus enum link refused visibly (`2026-10-10-root-shape-bogus-loads-a-blank-select.md`)

Only item with a runtime data-flow change, and the only one needing a new `Lxx`
(`L44`, names the boundary, amends L39's pin, keeps L02/L03/L05/L08).

**Today** (`src/spur/static/app.js`): `buildForm()` enum branch `:66-69` -> `readHash()` `:105-111`
runs `input.value = h.get(name) ?? defaults[name]`; a select given a value it has no option for
reads `''` (`selectedIndex` -1) -> `gearQuery()` `:114-120` skips `''` -> `update()` `:242-284`
sends no `root_shape`, rewrites the fragment without it, builds the default part, shows no error.

**After** (shape settled at discuss-phase; recommended):

```
#root_shape=bogus&teeth=22
  readHash(): for each select, drop a previous stray option, then if the hash value is not an
              option add one (marked, e.g. data-stray) BEFORE the pinned assignment line runs
  -> input.value = 'bogus' (kept)  -> gearQuery() sends root_shape=bogus (not default, not '')
  -> GET api/info?teeth=22&root_shape=bogus -> 422 literal_error loc [query, root_shape]
  -> problems() (:187-202) marks label.field.invalid + "Root shape: Input should be 'radial' or 'trochoid'"
  -> fail() keeps the downloads off (setDownloads(null)); fragment keeps root_shape=bogus
```

| Aspect | Detail |
|---|---|
| Pinned tokens that constrain the edit | `tests/test_api.py:240-241` pins, whitespace-collapsed, the exact line `for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];` and the end of `readHash` (`mateInput.value = h.get('mate_teeth') ?? ''; applyRelations(); deriveSelectors(); }`). So the new code is a pre-pass before that line, never a rewrite of it. Also pinned: the `gearQuery` token (`q.set(name, input.value)`), `fields.set(` counted once, `form.addEventListener('input', ...)`, the Reset line `mateInput.value = ''; stash.clear(); applyRelations(); deriveSelectors(); update();`. |
| Generic only | `test_api.py:277-283` fails any quoted GearParams field name or `.<field>` access outside the `DIMS` block. The code must detect `SELECT`/`prop.enum` generically; `root_shape` and `recess_sides` are then both covered. A new row-shaped table (`['word',` at line start) is harvested as a `DIMS` key and fails (`test_api.py:157-165`). |
| Reset | Reset (`app.js:615-622`) sets `input.value = defaults[name]`; a stray option must not stay selectable afterwards. Clean it in the same pre-pass helper (call it from `readHash` and `#reset`; the Reset token above is pinned, so add the call on a new line before the pinned one). |
| Browser step | `tests/test_browser.py:1754-1806` step `root_shape=bogus as today` is rewritten in the same commit: constants `BOGUS_LINK`/`TODAY` (`:97-103`) go or change; new assertions: the request carries `root_shape=bogus`, `/api/info` answers 422, `label.field` for `root_shape` has `.invalid`, `#messages .error` names the field, the fragment keeps the value, downloads stay disabled, no STL request. Keep the `no_foreign_key` recorder: `root_shape` is a GearParams key. Step name changes (`... as today` -> e.g. `root_shape=bogus is refused`); step names appear in RES (`:5071`, `:5293`, `:5365`, `:5473`) as history, leave them. |
| G / F | Unchanged by construction: valid links send what they sent. Verify with an empty `git diff --exit-code tests/regression/` at the close (L26, L39 "later phases must do"). |
| Downstream docs | `docs/architecture/web-ui.md:80` ("pinned as today's behaviour and filed as debt") is rewritten; L39 text `decision_log.md:2393-2394` and `:2448` get the amendment through L44, not an edit. Debt file retired in the same commit; INDEX row moved. |
| Open design edges for discuss-phase | (a) `#root_shape=` (empty) and number boxes with garbage (F6). (b) Whether the invalid select shows the bad value as its text (recommended: yes, so the address bar and the control agree). (c) `deriveSelectors()` / `holds()` read `Number(effective(field))`; gates on enum fields would be NaN, but today's relations gate only numeric fields (`enabled_when` `eq`/`gt`), so no change. |
| Conflict | Mild: L42's "`if (prop.enum)` branch ... byte-identical" is a recorded observation of 24-01, not a rule; L44 supersedes it. The rule that actually binds is the token list above. |

### 3.8 Item 8 - Ubuntu 26 CI (`2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`), **date-gated**

| Aspect | Detail |
|---|---|
| What changes | Probably nothing if green. Files in play: `.github/workflows/ci.yml` (`runs-on: ubuntu-latest` on `test`, `vendor-bundle`, `image`; `BROWSER_INSTALL_ARGS: --with-deps` on the `test` step), the Makefile `$(BROWSER)` stamp (`:91-93`), `bench/RESULTS.md` (new reading: image version, install seconds). `.github/workflows/required-jobs.txt` unchanged (`tests/test_pr_land.py:273-283` ties the two). |
| Gate | Classify the first run whose `Set up job` group prints `Image: ubuntu-26.04` (find it with `gh run view <id> --log \| grep "Image:"`), from the **whole** log, before any fix. Red candidates in order of likelihood: apt package set under `playwright install --with-deps`, SwiftShader frame (`PNG_RATIO_BAR = 4.9`, `browser_session.py` read on one Linux renderer only), `ps` flags (`group_members` uses `ps -A -o pgid=,stat=,pid=`), the kernel 6.17 -> 7.0 jump. Playwright 1.63.0 names `ubuntu26.04-x64/arm64` as known platforms (static check in the debt file); that is not proof `--with-deps` is complete there. |
| Fallback | Pin `runs-on: ubuntu-24.04`. Human's decision, not the executor's. |
| Optional pre-classification | A throwaway-branch run with `runs-on: ubuntu-26.04` (the issue recommends testing early). It classifies early but is not the debt's literal trigger; offer it, do not assume it. |
| Downstream | RES reading; debt file resolved with the image version and install seconds, or re-filed with the log's classification. DL only if `runs-on` is pinned (small `Lxx` amending L22/L23's CI statement). |
| Ordering | Phase last, open-ended (see section 6). Do not let it hold the milestone close beyond the 2026-11-19 end of the window; if no 26.04 run has happened, close it as "not yet fired, trigger carried" with today's reading. |

### 3.9 Item 9 - hook pin reads `PYTEST_ARGS` (`2026-10-10-hook-pin-reads-the-callers-pytest-args.md`)

| Aspect | Detail |
|---|---|
| Code | `tests/test_hooks.py:34-38` `_make_env()` strips `MAKEFLAGS`, `MFLAGS`, `MAKELEVEL` but not `PYTEST_ARGS`; make exports a command-line variable to the recipe's environment and `PYTEST_ARGS ?=` (`Makefile:6`) takes it. Failing assertions: `:120` (`"--ignore=" not in whole_pytest`) and the `ignored == {...}` set after it. Reproduced today. |
| Change | Add `"PYTEST_ARGS"` to the stripped names (or pass `PYTEST_ARGS=` on `_dry_run`'s command line, which wins over the environment). `_make_env()` also feeds `_clean_git_env`, the `-W` dry runs and the worktree test; stripping is harmless to all. |
| New test | A case that sets `PYTEST_ARGS` (`monkeypatch.setenv`) and asserts the recipes are unchanged. Cheap (`make -n`); lives in the commit slice. |
| Downstream | None beyond DOC. Unblocks narrowed `make verify PYTEST_ARGS="--ignore=..."` runs, which loops and phase work will want. |
| Order | First in its phase (item 2 and the loops assume narrowed runs are safe). |

### 3.10 Item 10 - launch-failure message (`2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`)

| Aspect | Detail |
|---|---|
| Code | `tests/browser_session.py:212-231` `launch()`; text at `:224-226`. |
| Change | Message-only (recommended): print Playwright's own error first, then the advice `rm .venv/.browser && make test` (and, on Linux, `BROWSER_INSTALL_ARGS=--with-deps`). Changing the stamp to depend on the revision directory instead touches the `Makefile` `$(BROWSER)` rule and `tests/test_hooks.py` (`BROWSER_STAMP = ".venv/.browser"`, the `-o`/`-W` dry runs): more surface for a cosmetic item. |
| Pins | `tests/test_browser_pins.py:105-127` requires `launch()` to call `pytest.fail` and to hold a string constant containing `playwright install --only-shell chromium`; keep that literal. |
| Downstream | RES `bench/RESULTS.md:4817` quotes the old message as a historic reading: leave it. DOC: debt retired. |
| Shares files with | Items 5, 6. |

### 3.11 Item 11 - info-finding triage (Phases 19, 21-24)

16 open items after removing 19-IN-03 (resolved, `34270c8`) and 24-IN-04 (already filed as `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md`). Sources: `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` and `.planning/milestones/v0.5-phases/{21..24}-*/*-REVIEW.md` plus `*-REVIEW-DISPOSITION.md` (the dispositions still read `open`). Several are already absorbed by named items.

| Finding | File(s) now | Verdict | Folds into |
|---|---|---|---|
| 19-IN-01 `_build` comment overstates "asked once"; `_chamfer_tips` re-solves | `src/spur/model.py:625-636` (`tip_chamfer_effective(p)` without `rm`), `:768-779` | fix: pass `rm` | solo, `model.py` change; **pin**: `tests/test_model.py:899` patches `_chamfer_tips` with a 3-argument lambda, update with the signature |
| 19-IN-02 bench stale paragraph, near-copy helpers | `bench/trochoid_part.py:109-121`, `:172-195` vs `tests/test_model.py:68`, `:86` | fix or close (drift risk, no user effect) | solo; `bench/` is in `mypy` scope |
| 19-IN-04 `root_fillet` label under hob root; `_host_state` crash outside git | `src/spur/static/app.js:23` (DIMS), `bench/trochoid_part.py:333` | fix both | `app.js` with item 7; label as a function row in `DIMS` (`test_api.py:157-165` pins the key shape, `(d) =>` rows like `span` are fine) |
| 21-IN-01 dead assignment, wrong bound | `browser_session.py:122`, `:123-139` | absorbed | item 5 |
| 21-IN-02 `fixture_hash` accepts `bool`/`None` | `browser_session.py:668-710` | fix (assert scalar types) | item 5/6 pass |
| 21-IN-03 pin scan is line- and spelling-based | `tests/test_browser_pins.py:46-101` | soften docstring or match on `ast.Constant`; recommend docstring | browser-test pass |
| 21-IN-04 `_follow_link` 30 s vs `BUILD_WAIT_MS`; hot park loop | `tests/test_browser.py:204`, `:584-593` | fix | browser-test pass (item F1) |
| 22-IN-01 `_BORE_OFF` duplicated | `tests/test_api.py` (inline literal beside `:1296`), `tests/test_trochoid.py:208` | fix or close | items 3-4 (same two files) |
| 22-IN-02 ragged docstring | `browser_session.py:646` (`serve_stl_from`) | fix | item 5/6 pass |
| 22-IN-03 L40 quotes the best-case reading (1.13 s) | `docs/architecture/decision_log.md` L40 "The browser proof"; `bench/RESULTS.md` | amend with the range 1.13-3.56 s | docs; the log is the locked record, so edit as a dated amendment line, not silently |
| 23-IN-08 honeycomb gate has one open value | `tests/test_relations.py:253` `CUTOUT_STATES`, `:274` meta-test | fix (add `honeycomb (4)`; count 12 -> 14 per the review) | test pass |
| 23-IN-11 `_js_number` unguarded range | `browser_session.py:325` | fix (assert range, normalise `-0`) | item 5/6 pass |
| 24-IN-01 stash comment overstates / stale restore | `app.js:292-300`, `:398-402` | reword comment (cheapest) or delete the stash entry on hand edit | `app.js` with item 7; pinned tokens `const stash = new Map();`, `if (zeroed) stash.set(field, input.value);` must survive |
| 24-IN-02 = CX-03 bootstrap message | `app.js:633-641` | reword to "Could not build the form" | `app.js` with item 7 |
| 24-IN-03 OpenAPI substring pin | `tests/test_api.py:143` | parse the JSON, walk for a `selectors` key | items 3-4 file |
| 24-CX-05 zero-request assertion too early | `tests/test_browser.py:1576-1612` | fix | **same edit as F1** |

Disposition ledger: the archived `*-REVIEW-DISPOSITION.md` files are history. Record the v0.6 triage as one table in the phase directory plus a `docs/tech_debt/active/` file for anything "filed", and flip the Phase 19 debt file only when its last open item is closed (it retires as a whole; if IN-01/02 are fixed and one is not, edit the file to say which, do not move it).

### 3.12 Item 12 - `make test-image` collects host-only tests (`2026-10-10-test-image-collects-tests-that-read-host-files.md`)

| Aspect | Detail |
|---|---|
| Step 1 | Run it (`docker info` answers; no image yet, the build installs the pinned closure and takes minutes) and read the red list. See F5 for the expected collection errors. |
| Files | `Makefile:219-226` (mounts, `PYTHONPATH`, `--ignore`s); `tests/test_hooks.py:181-190` `test_the_image_suite_ignores_the_browser_test` **pins this recipe** (`--ignore=tests/test_browser.py` in the dry-run text) and must be updated in the same commit; docs `README.md:322` and `docs/HOW_TO_DEVELOP.md:114` describe the target. |
| Constraint | `tests/test_hooks.py` also asserts the commit slice's five heavy names (`HEAVY_TEST_FILES`); changing what the image runs must not touch `test.fast`. |
| Downstream | RES none required; DOC: HOW_TO_DEVELOP/README sentence if the image suite now runs fewer files; debt retired. CI's `image` job does not run `test-image` (it builds and smoke-tests), so nothing in CI changes. |
| Conflict | None with an `Lxx`; L36/L39 only fix the browser test's exclusion. |

### 3.13 Item F1 - twin-selectors race (new)

| Aspect | Detail |
|---|---|
| Change | `tests/test_browser.py:1556-1612`: after `expect_request(/api/info)` also wait for the page's STL request (the route aborts it: `page.expect_event("requestfailed")` or `expect_request` on `STL_ROUTE`), then settle beyond the 350 ms debounce (`app.js:286-290`), then take `requests_before`. Waits on content, not clocks, per L39 "the test's waits stay on content"; the settle is the one place a bounded wait is the condition (document it, it is CX-05's own wording). |
| Proof | Red-first: make the page slow (`route` delay on `/api/info`) and see the old assertion fail with "1 request(s)"; the new one passes. |
| Downstream | B: step name `twin selectors` kept (L39). RES: a dated note naming runs 38347283201 and 38680454993. DOC: file the debt item and retire it in the fixing commit, or file-and-fix in one commit; state the file path in the reply (CLAUDE.md). |

## 4. Shared-file matrix (what must share a phase or be ordered)

| File | Items | Rule |
|---|---|---|
| `tests/browser_session.py` | 5, 6, 10, 21-IN-01/02, 22-IN-02, 23-IN-11 | one phase, one pass; keep every `test_browser_pins.py` tripwire green |
| `tests/test_browser.py` | 7 (step rewrite), F1/CX-05, 21-IN-04 | F1 and the info items first; the bogus step rewrite rides with the `app.js` change in its own phase |
| `src/spur/static/app.js` | 7, 19-IN-04, 24-IN-01, 24-IN-02 | one phase; every edit checked against the `test_api.py:240-280` token list; `golden_requests.json` and `pre_v0_2.json` must show an empty diff |
| `tests/test_hooks.py` | 9, 12, (2 if the recipe prefix changes) | item 9 first; item 12's pin update in the same commit as the Makefile edit |
| `Makefile` (`test`, `test-image`) | 1/2 (recipe flags), 12, 10 (only if the stamp route is chosen) | sequential commits, one concern each |
| `tests/test_api.py` + `tests/test_trochoid.py` | 3, 4, 22-IN-01, 24-IN-03 | one pass |
| `bench/RESULTS.md` | 1, 2, 5, 6, 8, F1 | append-only; dated corrections beside, never over, a reading; phases are sequential so no merge conflicts |
| `docs/architecture/decision_log.md` | 7 (L44), 22-IN-03 (L40 amendment), 2/1/8 only if the gate, the filter or `runs-on` change | next free id is L44 (last is L43) |
| `docs/tech_debt/INDEX.md` | every retirement | row moved in the fixing commit; the Phase 19 file moves only when whole |
| `tests/regression/*.json` | none | `git diff --exit-code tests/regression/` at every phase close |

## 5. Locked decisions and code state: conflicts

| Item | Conflict | Resolution |
|---|---|---|
| 3 slug totality | Debt/milestone wording asks for every reason; two are unreachable by real inputs (F2) | Force those two by patching `_root_curve`, label them forced; no `Lxx` |
| 7 bogus enum | L39 pins today's behaviour and says the pin is edited by whoever fixes the debt, "in the same commit"; L42 records `if (prop.enum)`/`gearQuery`/`readHash` as byte-identical; `test_api.py:240-280` pins `readHash` tokens | New `L44` supersedes the L39 pin and states the boundary (enums in, number boxes out unless chosen). Edit around the pinned tokens. L03/L05/L08 are honoured (an invalid link is refused, a valid one is unchanged) |
| 1/2 filter or recipe | `filterwarnings = error` is a gate property (L13); a filter is the "narrowest entry" the debt file allows, but it hides a symptom whose cause is unlocated; a changed `test` recipe amends L13/L34 | Human decision plus `Lxx`; default is re-deferral with the measurement |
| 2 hang capture | Debt file says "no repro, so only watch"; faulthandler cannot see a post-report stall (3.2) | State the limit in the debt file; keep it `active` |
| 8 Ubuntu pin | Pinning is "the human's decision" | Present as an option only |
| 12 test-image | Debt says "mount the files or exclude by name"; F5 shows exclusion-by-name drops `test_calc.py` | Offer both with a recommendation (mount `bench/` + `scripts/`) |
| 6 floor | Debt file offers "name the tracker" or "force a second build" | Recommend neither; honest comment only |
| 11 / 22-IN-03 | L40 is a locked record | Dated amendment line, not an in-place rewrite |
| F1 | Not in the milestone list | Add; same rule family as the milestone's (fix from captured evidence) |
| CLAUDE.md rule | "Blocker -> fix now or stop and ask" | None of these is a blocker; the three `must` flakes (items 1, 2, F1) are the highest-cost |

## 6. Date gate and build order

**Today is 2026-10-15; the Ubuntu 26 window opens 2026-10-19 and closes 2026-11-19.** Treat item 8 as an open-ended final phase that starts when a `Set up job` log names Ubuntu 26, not on a calendar day. Land the CI-visible phases before 10-19 where they are small (phases 26-27), so a red `test (3.12)` after the flip is not ambiguous.

Suggested phases (numbering continues at 26; each is a branch `gsd/phase-NN-...`, one `make verify` green, one concern per commit):

1. **Phase 26 - The gate fails with a cause** (Makefile, `pyproject.toml`, `tests/test_hooks.py`, `tests/test_browser.py`, `test_pool.py` if fixed)
   - 26a Item 9 first (hook pin, small, unblocks narrowed runs).
   - 26b **Start the tracker loops (item 1) now, unattended, on the otherwise unmodified tree**, while doing only non-gate work (reading, writing the L44 options). Gate runs during the window invalidate the measurement.
   - 26c F1 + CX-05 + 21-IN-04 (twin-selectors race; `test_browser.py`).
   - 26d Item 2 evidence capture (after the loops finish, so the loops measured the recipe the five prior occurrences came from; measure `--durations` once to set `faulthandler_timeout`).
   - 26e Item 1 outcome: fix in `test_pool.py` if localised, or re-deferral carrying the table; filter only on the human's say.
   - 26f Item 12 (`test-image`), pin update in the same commit.
2. **Phase 27 - The ledger's tests and harness** (test-only, plus one `model.py` line)
   - Items 3 and 4 with 22-IN-01 and 24-IN-03 (`test_api.py`/`test_trochoid.py`).
   - Items 5, 6, 10 with 21-IN-01/02/03, 22-IN-02, 23-IN-08/IN-11 (`browser_session.py`, `test_browser_pins.py`, `test_relations.py`); the macOS listing correction under both `RESULTS.md` rows; the member-command print for the Linux listing.
   - 19-IN-01/IN-02 (`model.py`, `bench/trochoid_part.py`), then 22-IN-03 (L40 amendment), then the triage table.
3. **Phase 28 - Refuse the bogus link** (the only behaviour change; discuss-phase first, `L44`)
   - Items 7 + 19-IN-04 label + 24-IN-01 + 24-IN-02 in `app.js`; browser step rewrite; `web-ui.md`; debt retired. Needs the human's pick on the number-box boundary and the empty-enum case.
4. **Phase 29 - Ubuntu 26** (date-gated, last, may close as "carried")
   - Item 8. Starts at the first 26.04 `Set up job`; classify from the whole log; reading into `RESULTS.md`; pin only on the human's word.

Why this order: item 9 and F1 remove false reds that would pollute every later gate reading; the loops need an idle host and an unmodified recipe; evidence capture changes the recipe so it follows the measurement; test-only phases carry no behaviour risk and finish before 10-19; the one user-visible change gets its own phase because it needs a decision record and edits the most heavily pinned file; the date-gated item cannot be scheduled and must not block the close.

## 7. Patterns to follow (project conventions the plans must carry)

- **Red first, then green.** Every new test is seen failing against a deliberately broken tree (RES has the "Seen red once" tables); record the mutation and the failure text.
- **Caller-wins `PYTEST_ARGS`** (`Makefile:157-160`): extra evidence for a one-off run goes through it; only permanent evidence changes the recipe.
- **Dated correction beside a reading, never over it** (`bench/RESULTS.md`).
- **Retire a debt item in its fixing commit:** `Status: resolved`, sha, `git mv` to `resolved/`, INDEX row moved. A re-deferral edits the file with the measurement and leaves `active`.
- **Fixture and golden stay byte-identical:** `git diff --exit-code tests/regression/` at each phase close; the frozen corpus (`tests/regression/corpus.py` header) never follows later test edits, so editing a test whose params it tagged does not move it.
- **Gate hygiene traps:** `make no-fake-done` greps `TODO|FIXME|XXX|HACK|NotImplementedError` as whole words in `*.py *.js *.sh`, so comments must avoid them; `mypy --strict` covers `tests bench scripts docker`; the commit hook runs `make verify.fast` under 30 s, so any new unit test must be milliseconds.

## 8. Anti-patterns to avoid

- **Fixing a flake or hang on a guess** (items 1, 2): without a captured failure the deliverable is a measurement.
- **A blanket `ignore::pytest.PytestUnraisableExceptionWarning`** or any filter wider than the message (the debt file already forbids it).
- **Rewriting `readHash`/`gearQuery` lines that tests pin token-for-token** (3.7); add around them.
- **A page-specific fix for `root_shape`** (breaks the generic-code pins and leaves `recess_sides` broken).
- **A module-wide autouse `_EXPORTS` reset** (3.4): cost without need.
- **Claiming a number-box or Linux-listing result that was not read** (L08).

## 9. Scalability of the sweep

Not applicable beyond gate cost: the permanent additions (`-v`, a `faulthandler_timeout`, a few millisecond tests, one process-group unit test) are priced against L43's 300 s bar with one reading in `bench/RESULTS.md`; the CI log grows with `-v` (the v0.5 close run printed a 400 s pytest section already).

## Sources

- Tree reads at `3726242`: the 21 active debt files, `docs/tech_debt/INDEX.md`, `Makefile`, `pyproject.toml`, `.github/workflows/ci.yml`, `src/spur/{app,params,records,pool,calc,model}.py`, `src/spur/static/app.js`, `tests/{browser_session,test_browser,test_browser_pins,test_hooks,test_api,test_trochoid,test_calc,test_model,test_relations}.py`, `tests/regression/*`, `bench/{trochoid,trochoid_part}.py`, `bench/RESULTS.md`, `docs/architecture/{overview,web-ui,decision_log}.md`, `.planning/milestones/v0.5-phases/{21..24}-*/*-REVIEW*.md` (HIGH).
- Run today: hook-pin reproduction under `PYTEST_ARGS`; `TestClient` 422 shapes for `root_shape=`, `root_shape=bogus`, `recess_sides=bogus`, `teeth=abc`; process-group listing of a real `uvicorn --fd` server by `ps` (HIGH).
- CI: `gh run view` for runs 38347283201 and 38680454993 (failure text, `Image: ubuntu-24.04` line) (HIGH).
- [CPython gh-109629](https://github.com/python/cpython/issues/109629) - reentrancy fix in `ResourceTracker`, backported to 3.12 and 3.11 (MEDIUM, page summarised by a small model; confirm the exact 3.12.x release before quoting it in a decision).
- [actions/runner-images#14748](https://github.com/actions/runner-images/issues/14748) - Ubuntu 26.04 migration, 2026-10-19 to 2026-11-19, setup-python patch-version limit (MEDIUM, summarised).
- [CPython `resource_tracker.py` on main](https://git.adamlamers.com/PublicArchive/cpython/src/branch/main/Lib/multiprocessing/resource_tracker.py) - `_reentrant_call_error` and the lock recursion check (MEDIUM, search-result description).

## Gaps

- No local reproduction of F1 or of the tracker flake; both rest on captured logs.
- `make test-image` was not run (no image built); F5 is from imports and mounts.
- Ubuntu 26 behaviour (apt set, SwiftShader frame) is unread by design; the date gate is the point.
- Number-box garbage in a link (`#teeth=abc`) is from HTML spec behaviour, not a browser run.
- Linux process-group listing is unmeasured until a CI log prints it.
