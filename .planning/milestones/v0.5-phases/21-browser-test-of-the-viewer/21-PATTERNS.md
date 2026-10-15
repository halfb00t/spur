# Phase 21: Browser Test of the Viewer - Pattern Map

**Mapped:** 2026-10-10
**Files analyzed:** 17 new/modified
**Analogs found:** 14 / 17 (3 have no codebase analog; RESEARCH.md Code Examples 1-3 and 7 are the pattern source)

All analog paths verified tracked with `git ls-files` (tests/*, Makefile, pyproject.toml, .gitignore, .github/workflows/ci.yml, .pre-commit-config.yaml, bench/RESULTS.md, docs/*, src/spur/static/app.js). None is a gitignored mirror. `.venv/`, `.gsd/` and `.planning/research/.cache/` are ignored and must not be cited.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/test_browser.py` (new) | test (heavy tier) | request-response, subprocess | `tests/test_pool.py` + `tests/test_cli.py:465-480` (real subprocess) | role-match |
| `tests/browser_session.py` (new, not collected) | test helper | subprocess + request-response | `tests/composition.py` (non-collected shared module) | role-match |
| `tests/capture_requests.py` (new) | script (regen) | batch / file-I/O | `tests/regression/capture.py` | exact (role) |
| `tests/test_browser_pins.py` (new) | test (light, static pins) | transform | `tests/test_hooks.py` | role-match |
| `tests/regression/golden_requests.json` (new) | fixture data | file-I/O | `tests/regression/pre_v0_2.json` | exact |
| `tests/test_hooks.py` (mod) | test | request-response (`make -n`) | itself (lines 24, 56-60, 85-121) | exact |
| `src/spur/static/app.js` (mod, 1 line) | component | event-driven | `showModel` in same file (:303-313) | exact |
| `Makefile` (mod) | config | batch | `$(STAMP)`/`$(HOOKS)` stamps (:34-75), `fixture.regen` (:248) | exact |
| `.github/workflows/ci.yml` (mod) | config | batch | its own `test` job step | exact |
| `pyproject.toml` (mod) | config | n/a | `[dev]` extra (:20-30) | exact |
| `.gitignore` (mod) | config | n/a | existing commented entries | exact |
| `.pre-commit-config.yaml` (mod, comment) | config | n/a | itself ("four heavy ones") | exact |
| `bench/RESULTS.md` (mod) | doc | n/a | `### The gate, priced (19-09)` (:4589+) | exact |
| `docs/architecture/decision_log.md` (mod, new Lxx) | doc | n/a | L36 (:1869), L38 (:2091), L34 (:1635) | exact |
| `docs/architecture/web-ui.md` (mod, :51) | doc | n/a | itself | exact |
| `docs/tech_debt/active/2026-10-10-root-shape-bogus-blanks-select.md` (new) + `INDEX.md` row | doc | n/a | `docs/tech_debt/active/2026-10-06-wedged-worker-holds-process-exit.md` | exact |
| `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` (retire) + `INDEX.md` | doc | n/a | CLAUDE.md retirement rule | exact |

## Pattern Assignments

### `tests/test_browser.py` (test, request-response + subprocess)

**Analogs:** `tests/test_pool.py` (real pool, no mock; header comment explains why it differs from `test_api.py`), `tests/test_cli.py:465-480` (real subprocess, measured cost in docstring), `tests/test_api.py:1-36` (import and fixture style), `tests/conftest.py` (autouse `_reset_root_logger`; applies automatically, no action).

**Imports/style** (`tests/test_api.py:1-12`, `tests/test_pool.py:10-32`): `from __future__ import annotations`; stdlib first, third party, then `spur.*`. The test file must NOT import `cadquery` or `spur.model` (the server is a subprocess).

**Real-subprocess pattern** (`tests/test_cli.py:474-477`):
```python
result = subprocess.run(
    [sys.executable, "-m", "spur.cli", "export", "-o", str(out)],
    capture_output=True, text=True, check=False)
```
Fixed arg list, no `shell=True`, `sys.executable`. Docstring states the measured cost. Copy that: the module fixture and the scenario docstring carry the measurement (3.2-3.8 s research, spike reading), not an estimate.

**Server fixture:** no in-repo analog for `--fd`/`killpg`. Use RESEARCH.md Code Examples 1 (module-scope fixture, pre-bound `127.0.0.1` socket, `start_new_session=True`, env scrubbed of `SPUR_*`, `TemporaryFile` log, `stop_group` with `ps -A -o pgid=,stat=,pid=` ignoring `Z`, escalate then fail). Use `tests/test_api.py:21-36` fixture shape (`@pytest.fixture(scope="module")`, `Iterator[...]`, docstring explains why).

**Fail-closed launch** (RESEARCH Code Examples 3): launch inside the test body, catch `playwright.sync_api.Error`, `pytest.fail` with `playwright install --only-shell chromium`, the effective `PLAYWRIGHT_BROWSERS_PATH`, and "`make test` runs the install stamp" (D-07). No `importorskip`, no skip/xfail, no env opt-out (D-02).

**Typed wrappers** (RESEARCH Code Examples 3): `value: object = page.evaluate(...)` then `isinstance` assert; never `return page.evaluate(...)` (mypy `no-any-return`); never write `Any` (L21). `page.route(..., lambda r: parked.append(r))` not `parked.append`.

**Waits** (RESEARCH Pattern 3): content-based; `timeout=45_000` on build-bound waits only; no `wait_for_timeout`. Each step's assertion message carries the step name (D-10).

**Naming:** `test_<requirement_as_phrase>`, e.g. `test_the_viewer_...` (test_hooks.py style: long, reads as a requirement).

**Lint traps** (RESEARCH P12): line length 100, no compound assert (PT018), no commented-out code (ERA), never write the words TODO/FIXME/XXX/HACK/NotImplementedError (the `no-fake-done` scan).

---

### `tests/browser_session.py` (helper, not collected)

**Analog:** `tests/composition.py:1-12` (no `test_` prefix, module docstring says "Not collected" and why; flat in `tests/` so no `sys.path` games, same as `tests/regression/capture.py` importing sibling `corpus`).

Holds server start/stop, shell launch, typed wrappers and `sweep()` (RESEARCH Code Examples 7) shared by the test and the capture script, so there is one sweep, not two (rejects D-09's "second implementation").

---

### `tests/capture_requests.py` (script, batch/file-I/O)

**Analog:** `tests/regression/capture.py`

**Module docstring** (lines 1-9): "Regenerates X: `make <target>`, never anything else", trigger and mechanism, commit-alone rule.

**Typed JSON + writer** (lines 58-72, 107-111, 114-115):
```python
FIXTURE = Path(__file__).with_name("pre_v0_2.json")
...
    FIXTURE.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(records)} records ... to {FIXTURE}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```
Read `pre_v0_2.json` `records` (TypedDict `Record` at capture.py:58-65: `params`, optional `mate_teeth`), write `golden_requests.json` with the same record names -> exact `api/info` query string. Keep `sort_keys=True`, trailing newline. Subprocess use follows capture.py:78-82 (`["git", ...]`, no shell). Running as `python tests/capture_requests.py` puts `tests/` first on `sys.path`, so `from browser_session import ...` works like `from corpus import cases` (capture.py:20).

---

### `tests/test_browser_pins.py` (test, static pins, light tier, no playwright import)

**Analog:** `tests/test_hooks.py` (reads repo text, asserts policy; module docstring explains which drift becomes a red test). Use `REPO_ROOT = Path(__file__).resolve().parents[1]` (:21) and `read_text(encoding="utf-8")`. Assertions: no `importorskip`/`pytest.skip`/`skipif`/`xfail`/opt-out env read in `tests/test_browser*.py`; `pyproject.toml` dev has exact `playwright==`; no `pytest-playwright`; no `channel=`; `requirements.txt`, `Dockerfile`, `docker/refresh-requirements.sh` have no `playwright`. This file must stay fast (it runs in `verify.fast`).

---

### `tests/test_hooks.py` (mod)

**Line 24** (extend in the exclusion commit):
```python
HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli")
```
add `"test_browser"`.

**`_dry_run`** (lines 56-65): add `-o <stamp path>` so `make -n verify` stays byte-identical to `make -n verify.fast` before the pytest line (RESEARCH P2, verified). Keep the stamp path in one place beside `HEAVY_TEST_FILES`:
```python
["make", "-n", "--no-print-directory", target],
```
**Pin that must go red** (lines 118-121, already generic over the tuple):
```python
ignored = {
    w.removeprefix("--ignore=") for w in fast_pytest.split() if w.startswith("--ignore=")
}
assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}
```
New assertions in the same style: `make -n -o <stamp> test-image` contains `--ignore=tests/test_browser.py`; `make -n test` (no `-o`) names `$(BROWSER)`. "Seen red" = delete the `--ignore` and run.

---

### `src/spur/static/app.js` (mod, one line)

**Analog:** `showModel` itself, lines 303-313. Insert after `scene.add(mesh, edges);` (:313):
```js
  scene.add(mesh, edges);
  canvas.dataset.triangles = String(geometry.attributes.position.count / 3);
```
Constraint (CONTEXT code_context): must not add a `['word',` row or a `GearParams` field name; `tests/test_api.py:123` and `:162` pins untouched. A failed build never reaches `showModel`, so the previous count stays (RESEARCH Ex. 5).

---

### `Makefile` (mod)

**Stamp analog** (`Makefile:34-43`, `:61`): file under `$(VENV)`, dependency chain, `@touch $@`, no `|| true`:
```make
$(STAMP): pyproject.toml
	...
	@touch $@
$(HOOKS): .pre-commit-config.yaml $(STAMP)
```
New (RESEARCH Pattern 5): `export PLAYWRIGHT_BROWSERS_PATH := $(abspath $(VENV))/ms-playwright` (absolute, measured), `BROWSER := $(VENV)/.browser`, `BROWSER_INSTALL_ARGS ?=`, recipe `$(PY) -m playwright install $(BROWSER_INSTALL_ARGS) --only-shell chromium` then `@touch $@`. Declare variables beside `PY`/`STAMP`/`HOOKS` (:19-21) and `PYTEST_ARGS ?=` (:5-8 block).

**`test:` recipe** (:149-150): `test: $(STAMP)` becomes `test: $(STAMP) $(BROWSER)`. Not a prerequisite of `verify.static`, `test.fast`, `lint`, `typecheck`.

**`test.fast`** (:171-174): append `--ignore=tests/test_browser.py` to the existing `--ignore` set. Update the "four heavy ones" text at Makefile:88,153,171 (RESEARCH P10); do NOT touch the `63.555 s`/`~64 s` sentences (Phase 25).

**`test-image`** (:186-192): `$(PYTEST_ARGS)` is last; add `--ignore=tests/test_browser.py` inside the `-c "..."` pytest invocation (playwright is not in the image).

**Regen target** (`Makefile:248-249`, and the `.PHONY` list :25-28):
```make
fixture.regen: $(STAMP)  ## rewrite tests/regression/pre_v0_2.json (the L05 fixture); commit it alone, saying what moved and why
	$(PY) tests/regression/capture.py
```
New target: same shape, `: $(STAMP) $(BROWSER)`, `## ...` help text (the `help` grep needs `^[a-z][a-z.-]*:.*##`), add to `.PHONY`.

---

### `.github/workflows/ci.yml` (mod)

**Analog:** the existing step (:38-40):
```yaml
      - run: make verify PYTHON=python
        env:
          PIP_CONSTRAINT: requirements.txt
```
Add `BROWSER_INSTALL_ARGS: --with-deps` to `env` (or on the make line). `tests/test_pr_land.py` ties job names to `required-jobs.txt`: do not rename the `test` job or add a job. Comment style: explain why, with measurement.

---

### `pyproject.toml` (mod)

**Analog:** `[project.optional-dependencies].dev` (:20-30): append one exact line `"playwright==1.63.0",` after `"pytest-cov>=7.1",`. Only `[dev]`; the runtime closure, `requirements.txt`, `Dockerfile` and `docker/refresh-requirements.sh` do not move. Leave `[tool.coverage.run]` and `filterwarnings` alone. A `checkpoint:human-verify` precedes the pin (SUS-flagged packages, RESEARCH legitimacy audit).

---

### `.gitignore` (mod)

**Analog:** the commented single-purpose entries (`# agent worktrees (make worktree.new)` / `/.claude/worktrees/`). `.venv/` is already ignored, so `$(VENV)/ms-playwright` and `.browser` need nothing. Add an entry with a one-line why-comment only if the spike writes failure screenshots or traces.

---

### `bench/RESULTS.md` (mod)

**Analog:** `### The gate, priced (19-09)` (:4589-4620): intro paragraph with HEAD sha, `#### Host state` bullets (machine, CPUs, RAM, Python, kernel pair, read window UTC, load caveat "upper bound ... none is a bar"), then runs table:
```
| Run | Result line | `real` (s) | 1-minute load before -> after | UTC |
```
A/B (D-12): 6 interleaved runs, flake-failed runs in their own rows, mean `real`, coverage TOTAL vs floor 96. Also record: spike PNG sizes/ratio bar (macOS and Linux), renderer string, per-step times, real `ubuntu-latest` run id and wall time, "seen red once" evidence.

---

### `docs/architecture/decision_log.md` (mod, new Lxx)

**Analog:** headings like `## L36 — The commit stage runs a named prefix of the gate under 30 s, and the whole gate moves to pre-push (amends L13 and L34)` (:1869) and L38 tail (**Reversibility.** paragraph per D-xx, `Reason:` paragraph). New entry: title ends `(amends L13 and L36, restates L11 unchanged)`; names the `canvas.dataset.triangles` line as the milestone's one production change; carries the A/B price and the human acceptance verbatim; Reversibility per D-01/D-04/D-09 (costly) and D-06 (reversible). Next id follows L38 (verify the latest id at write time).

---

### `docs/tech_debt/active/<date>-root-shape-bogus-...md` + `docs/tech_debt/INDEX.md` (new)

**Analog:** `docs/tech_debt/active/2026-10-06-wedged-worker-holds-process-exit.md` structure (title; `Severity:` / `Status:` / `Date:` / `Source:` / `Related files:`; `## Context`, `## Why it matters`, `## Next step`) from `docs/tech_debt/TEMPLATE.md`. Severity: `must` is the research recommendation (A9), needs human confirmation (blocker means fix now). Context facts: RESEARCH section 8 (`#root_shape=bogus&teeth=22` leaves the select at `''`, requests omit `root_shape`, fragment rewritten, API alone returns 422). INDEX row format in the `## Active` table: `| must | [title](active/file.md) | trigger |`, in the same commit.

---

### `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` + `docs/ideas/INDEX.md` (retire)

**Analog:** CLAUDE.md retirement rule; the INDEX row `| 2026-09-21 | [A browser test for the viewer](...) | 12-07 took the cheaper first step ...` is removed/moved in the commit that closes the phase. Note the other two INDEX rows (bore-shape selector, conditional form fields) say "revisit when a browser test exists": update their "why not now" text in the same commit.

---

### `.pre-commit-config.yaml` / `docs/architecture/web-ui.md` (mod, text drift)

"four heavy ones" in the header and hook name of `.pre-commit-config.yaml`; `web-ui.md:51` says "There is no browser test." Update in the admission commit. Editing `.pre-commit-config.yaml` re-triggers the `$(HOOKS)` stamp once in the main checkout (expected).

## Shared Patterns

### No mocks, test the real thing
**Source:** `tests/test_pool.py:1-8` header, `tests/test_cli.py:466-471`. **Apply to:** `tests/test_browser.py`. Real `uvicorn`, real `BuildPool` (default `SPUR_BUILD_WORKERS`, D-11), real browser.

### Comments carry the measurement or the constraint
**Source:** `Makefile:140-170` (`test.fast` comment block with dated readings), `tests/test_cli.py:469-472`. **Apply to:** every new test, Makefile and ci.yml comment. Every bar asserted is set from a reading taken this phase and recorded in `bench/RESULTS.md`.

### Regen script behind a make target, JSON committed alone
**Source:** `tests/regression/capture.py:1-9,107-115`, `Makefile:248-249`. **Apply to:** `capture_requests.py`, `golden_requests.json`, its make target. Deliberate change = regen commit saying what moved and why; `git diff --exit-code tests/regression/pre_v0_2.json` clean after every task.

### Exclusion over inclusion, pinned by test_hooks
**Source:** `Makefile:171-174`, `tests/test_hooks.py:24,118-121`. **Apply to:** `test.fast`, `test-image`, `HEAVY_TEST_FILES`. No markers (`--strict-markers`, none registered). The exclusion edits land no later than the commit adding `tests/test_browser.py` (RESEARCH P1, Open Question 1; surface to the human at plan-check).

### Typing and warnings strictness
**Source:** `Makefile:94-95` (`mypy --strict` over `src tests docker bench scripts`), `pyproject.toml` `filterwarnings = ["error", ...]`. **Apply to:** all new Python. No `Any`, no new `filterwarnings` entry (not even for the resource-tracker flake).

### Fixed argument lists, no shell
**Source:** `tests/regression/capture.py:78-82` (T-07-03). **Apply to:** server Popen, `ps` call, `make -n` helper.

## No Analog Found

| File / Concern | Role | Data Flow | Reason |
|---|---|---|---|
| Server fixture (pre-bound socket, `--fd`, `killpg`, `ps` survivor check) in `tests/browser_session.py` | fixture | subprocess | No test in the repo starts a long-lived server; use RESEARCH Code Examples 1 |
| Playwright launch, typed `evaluate` wrappers, `expect` waits, route capture | test helper | request-response | No browser code exists; use RESEARCH Code Examples 2, 3, 4, 7 and Pattern 3 |
| Canvas PNG byte-ratio check | assertion | transform | Nothing comparable; bar comes from the spike reading, not the research figure (D-05) |

## Metadata

**Analog search scope:** `tests/`, `tests/regression/`, `Makefile`, `.github/workflows/`, `pyproject.toml`, `.gitignore`, `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `docs/tech_debt/`, `docs/ideas/`, `src/spur/static/app.js`
**Files scanned:** about 20 read or grepped
**Pattern extraction date:** 2026-10-10
