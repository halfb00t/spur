# Phase 30: Scope, Seam and Gear-Safety Guard - Pattern Map

**Mapped:** 2026-10-23
**Files analyzed:** 22 new or modified
**Analogs found:** 20 / 22 (all analog paths verified git-tracked: scripts/, src/spur/app.py, tests/, Makefile, pyproject.toml, bench/RESULTS.md, docs/architecture/decision_log.md)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/gear_unchanged.py` | script (dev tooling) | batch / request-response (in-process GET) | `scripts/pr_land.py` | role-match |
| `Makefile` (`gear.unchanged`, `verify.static`, `.PHONY`) | config | batch | `Makefile` `fixture.regen`, `pr.land`, `verify.static` | exact |
| `pyproject.toml` (4 contracts after :223) | config | static analysis | `pyproject.toml:170-223` | exact |
| `src/spur/parts.py` | model (alias only) | none | none in repo (docstring-only module) | no analog |
| `src/spur/shaft_params.py`, `shaft_calc.py`, `din5480.py`, `din5480_tables.py`, `shaft_model.py` | placeholders | none | none (docstring-only) | no analog |
| `src/spur/app.py` (`_serve_model`, `Part`, 503 text) | controller | request-response | `app.py` `model()` itself (pure move) | exact |
| `src/spur/pool.py`, `records.py`, `model.py` (`Part` annotations) | service | CRUD / event | themselves (annotation swap) | exact |
| `tests/test_gear_unchanged.py` | test | batch (scratch git repo) | `tests/test_hooks.py` (subprocess + repo-level pins) | role-match |
| `tests/test_seam.py` (route pin, name-existence guard, regex belts) | test | request-response / static | `tests/test_records.py:246` | role-match |
| `tests/test_hooks.py` (dry-run pin addition) | test | batch | `tests/test_hooks.py:109-155` | exact |
| `tests/test_api.py` (503 text pin) | test | request-response | `tests/test_api.py:985` | exact |
| `docs/architecture/decision_log.md` (L46) | docs | none | L45 / L44 entries | exact |
| `AGENTS.md`, `.planning/ROADMAP.md` | docs | none | self (edit in place) | exact |
| `bench/RESULTS.md` (gate delta, Seen red once) | docs | append-only | `bench/RESULTS.md` "Seen red once (Phase 28)" :6683 | exact |

## Pattern Assignments

### `scripts/gear_unchanged.py` (script, batch)

**Analog:** `scripts/pr_land.py` (tracked). Module docstring that opens with the command and states *why it exists* with the incident or measurement, then `from __future__ import annotations`, stdlib imports, argparse `main(argv) -> int`, `raise SystemExit(main())`.

**Header/imports pattern** (pr_land.py:1-3, :46-52):
```python
"""`make pr.land PR=N`: the sanctioned path onto `main` (D-05, L22).

Why this exists: PR #2 merged five minutes after ... failed ...
...
Needs network and an authenticated `gh`. Runs only as `make pr.land`; never part
of `make verify` or `make check` (like `bench`, D-16).
"""

from __future__ import annotations

import argparse
import json
import subprocess
```

**Entry point pattern** (pr_land.py:595-606):
```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts.pr_land",
        description="Squash-merge a PR only if ...",
    )
    args = parser.parse_args(argv)
    return land(args.pr, _real_runner)

if __name__ == "__main__":
    raise SystemExit(main())
```
Also copy `_real_runner(argv) -> CompletedProcess` injection style (pr_land.py:590-592) so tests inject a runner / `schema_of` instead of touching real git.

**Core logic:** use RESEARCH Pattern 2 verbatim (`ensure_tag`, `PROBE`, `schema_of` with `PYTHONPATH` + `python -P` + `spur.__file__` shadow assertion, `git archive v0.6 src` into `TemporaryDirectory` with `tarfile.extractall(filter="data")`, `git diff --exit-code --stat` plus `git ls-files --others --exclude-standard` over `WATCHED`). Read-only git only (no `worktree add`; hook sets `GIT_INDEX_FILE`). `mypy --strict` covers `scripts/` so full annotations are needed. List-form `subprocess.run`, never `shell=True`. Failure path: `sys.exit("gear.unchanged: ...")` naming the cause (D-05).

---

### `Makefile` (config)

**Analog:** `Makefile:317-321` (dotted target with `##` description), `:362-364` (script target), `:113-115` (gate prefix).

```make
fixture.regen: $(STAMP)  ## rewrite tests/regression/pre_v0_2.json (...); commit it alone, saying what moved and why
	$(PY) tests/regression/capture.py

pr.land: $(STAMP)  ## PR=<n> : squash-merge a PR only if ...
	$(PY) -m scripts.pr_land $(PR)
```
Gate wiring (Makefile:113): add `gear.unchanged` as a prerequisite of `verify.static` (not of `verify`) so `tests/test_hooks.py` shared-prefix pin still holds:
```make
verify.static: $(HOOKS) lint typecheck lint-imports no-fake-done  ## the gate's static steps: ruff, mypy, import boundaries, unfinished-work scan
```
Add `gear.unchanged` to the `.PHONY` list (Makefile:34-39), update the `verify.static` description, and write a *why* comment above the target (measured 0.66 s; read-only git because of hook `GIT_INDEX_FILE`). `help` greps `^[a-z][a-z.-]*:.*##`, so keep the `## ` form. New target: `gear.unchanged: $(STAMP)  ## ...` then `$(PY) -m scripts.gear_unchanged`.

---

### `pyproject.toml` new contracts (config)

**Analog:** `pyproject.toml:176-223`. Contract = `name`, why-comment as the first lines inside the table, `type = "forbidden"`, `source_modules`, `forbidden_modules`, explicit `allow_indirect_imports` with the reason.

```toml
[[tool.importlinter.contracts]]
name = "The gear maths stays free of the logger"
# calc.py runs on every keystroke in the UI and must stay pure arithmetic, ... 
# tests/test_records.py's test_calc_module_stays_log_free is a regex-based belt on the
# same claim; this contract is the suspenders ...
type = "forbidden"
source_modules = ["spur.calc"]
forbidden_modules = ["spur.records", "logging"]

[[tool.importlinter.contracts]]
name = "The serving process never imports the CAD kernel"
# ... a transitive path is as bad as a direct one -- allow_indirect_imports = false ...
type = "forbidden"
source_modules = ["spur.app"]
forbidden_modules = ["cadquery", "OCP"]
allow_indirect_imports = false
```
Use RESEARCH Pattern 1 for the four tables (insert after :223) and add a why comment to each, naming the paired belt test. Contract 3's comment must record the Phase 32 handoff: when `model.py` statically imports `shaft_model`, add `ignore_imports = ["spur.model -> spur.shaft_model"]` in that same commit (it errors if added earlier). Contract 2 omits `allow_indirect_imports` (matches the existing logger contract).

---

### `src/spur/app.py` — `_serve_model` pure move (controller, request-response)

**Analog:** `model()` itself, `app.py:384-504`.

Decorator/signature stay on `model()`:
```python
@app.get("/api/model.{fmt}", response_class=Response,
         responses={200: {"content": {t: {} for t in MEDIA_TYPES.values()}}})
async def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()],
                request: Request,
                backend: Annotated[BuildBackend, Depends(build_backend)]) -> Response:
```
Move the body from `request_id = uuid.uuid4().hex[:8]` (:393) to `return Response(data, ...)` (:504) unchanged into `async def _serve_model(params: Part, fmt: Literal["stl","step"], quality: Literal["preview","fine"], request: Request, backend: BuildBackend) -> Response`. Replace `q.quality` with `quality` (:401, 417, 418, 422, 423, 436, 447, 461, 490, 494) and drop `params = _gear(q)` (:394). `model()` ends `return await _serve_model(_gear(q), fmt, q.quality, request, backend)`. Keep the existing why-comments with the moved lines. Own commit; no test edits.

**503 reword** (app.py:285-286): change only the noun:
```python
"msg": f"Busy: {MAX_QUEUED_BUILDS} parts are already being built or "
       "compressed. Try again in a moment."
```
**Part annotations:** `BuildBackend = Callable[[Part, str, str], Awaitable[bytes]]` (:117), `_build_slot(request_id, p: Part, ...)` (:263). `GearParams` stays in `app.py` for `_gear`, query classes, `schema()`. In `pool.py` (:32 import; :53, 100, 103, 165, 252) and `records.py` (:39 import; :171, 211, 221, 235, 259) replace the import with `from .parts import Part` (ruff F401 otherwise). In `model.py`: `build` (:804) and `export` (:833) only.

---

### `src/spur/parts.py` and the five shaft placeholders (no analog)

RESEARCH-verified shapes. `parts.py`: a docstring plus a plain assignment, which stays out of UP040 and keeps `isinstance` usable (not `TypeAlias`, not `type Part =`):
```python
from .params import GearParams

Part = GearParams
```
The five shaft placeholders: a docstring only, no `pass`, `TODO`, `FIXME`, `XXX`, `HACK`, `NotImplementedError`, `type: ignore` anywhere (including prose), because `make no-fake-done` greps the text (Makefile `no-fake-done`, git grep -w). Coverage shows `0 stmts, 100%`. Existing module docstring style: why-first prose (see `scripts/pr_land.py` header).

---

### `tests/test_seam.py` (test)

**Analog:** `tests/test_records.py:244-256` regex belt:
```python
def test_calc_module_stays_log_free() -> None:
    """L01, REQ boundary: calc.py runs on every keystroke ... the pyproject.toml import-linter
    contract "The gear maths stays free of the logger" is the suspenders for this same
    claim; this regex is the belt, so it must catch a `from .records import ...` ... too."""
    source = Path(calc_module.__file__).read_text()
    assert not re.search(
        r"^\s*(import|from)\s+(logging|\.records|spur\.records)\b", source, re.MULTILINE)
```
Copy: docstring names the contract it belts. Write the belts for contracts 1-4 from RESEARCH "Regex belt" (SHAFT_MATHS loop; add gear-maths-does-not-know-shaft belt on `calc.py`/`params.py`). Route pin from RESEARCH Pattern 3 (`APIRoute` set vs `V06_API`, extras must start `/api/shaft/`, non-`/api/` paths in fixed set, query keys from `app.openapi()` vs `GearParams.model_fields | {"mate_teeth"}` / `| {"quality"}`). Contract-name existence guard from RESEARCH (`tomllib`), because a typo in a forbidden module is silently accepted.

---

### `tests/test_gear_unchanged.py` (test)

**Analog:** `tests/test_hooks.py` (REPO_ROOT, subprocess against git/make, `_make_env` scrubbing, module docstring explaining the pin). Pattern:
```python
REPO_ROOT = Path(__file__).resolve().parents[1]
```
Build a scratch git repo in `tmp_path` with a fake `v0.6` tag; inject `schema_of` / runner; cases: green, regression file edit, untracked file, `ci.yml` edit, schema bytes differ, tag missing + unreachable origin (message names the cause), shadow guard (probe `spur.__file__` outside the target `src`). Scrub `GIT_*` env as `_make_env` scrubs `MAKEFLAGS` etc. (test_hooks.py:30).

---

### `tests/test_hooks.py` addition (test)

**Analog:** `tests/test_hooks.py:74-83` and :109-155.
```python
def _dry_run(target: str) -> list[str]:
    result = subprocess.run(
        ["make", "-n", "-o", BROWSER_STAMP, "--no-print-directory", target],
        cwd=REPO_ROOT, env=_make_env(), capture_output=True, text=True, check=True)
    return result.stdout.splitlines()
```
New test: `"scripts.gear_unchanged"` appears in `_dry_run("verify")` and `_dry_run("verify.fast")` static lines. Do not edit the existing shared-prefix assertion (it passes as long as the prerequisite sits on `verify.static`).

---

### `tests/test_api.py` addition (test)

**Analog:** `tests/test_api.py:985-999`, `test_a_saturated_service_refuses_instead_of_queueing`: exhaust `app_module.BUILD_QUEUE` with `acquire(blocking=False)` x `MAX_QUEUED_BUILDS`, `client.get("/api/model.stl", params={"quality": "preview"})`, release in `finally`. Add a sibling test asserting the full message (RESEARCH "503 reword and its pin"), status 503, `retry-after == "5"`, `detail[0]["type"] == "busy"`. Do not edit the existing test.

---

### `docs/architecture/decision_log.md` L46 (docs)

**Analog:** L44 header (:2948) and L45 (:3029-end). Header: `## L46 — <title> (amends L02 and L05; keeps L03, L04, L06, L08 and L44)`, then `Date: 2026-10-23`, bold-lead paragraphs in L45's order: **The decision**, **What it amends**, **What it leaves alone**, **The proof**, **Reversibility.**, then `Reason:` line. Do not edit L02/L05 text; amend by reference. State D-18 (shaft names changeable by logged decision until Phase 33 publishes the first link) and that a stray `part=` on the gear page moves from ignored to refused in Phase 33. Commit precedes every shaft-module commit (D-20); check with the order command in RESEARCH.

---

### `bench/RESULTS.md` (docs, append-only)

**Analog:** `### Seen red once (Phase 28)` at `bench/RESULTS.md:6683`. Section opens "What this section holds: ..." (see `## Ubuntu 26 final reading (Phase 29)` for the per-phase H2). Table shape:
```
| Plan | Test or step | Deliberate break | First failure line | Reverted |
|---|---|---|---|---|
| 28-06 | `tests/test_calc.py::...` | the old gate ... | `AssertionError: assert 0.0 is None` at ...; `1 failed, 20 passed ...`, log `28-06-red-tip-chamfer-null.log` | the fix replaced it |
```
Heading `## Scope, seam and gear-safety guard (Phase 30)` with `### The gate delta (30-NN)` (host, `uptime` before/after, `git rev-parse --short HEAD`, pytest result line, baseline `236.23s` plus 239.51s cross-check) and `### Seen red once (Phase 30)`. Logs go to `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/`. First-failure lines for contracts come from RESEARCH "Existing-contract failure strings". Rows needed: `gear.unchanged` x3 watched items (+ untracked file, missing tag), contracts 1-4, route pin with `/api/foo`, name-existence guard, 503 pin, `verify.static` dry-run pin. Append only; never rewrite.

## Shared Patterns

### Guard counts only after seen red
**Source:** CODING_VALUES "Coupling"; `bench/RESULTS.md` Phase 28 tables. **Apply to:** every contract, belt, route pin, `gear.unchanged` watched item, 503 pin.

### Why-comments carry the measurement
**Source:** `pyproject.toml:177-223`, `Makefile:100-112`. **Apply to:** every new contract, the new Makefile target, the script docstring.

### Read-only git inside the gate
**Source:** RESEARCH Pitfall 1. **Apply to:** `scripts/gear_unchanged.py` (use `rev-parse`, `diff`, `ls-files`, `archive`, `fetch` of a tag only).

### Unfinished-work scan
**Source:** `Makefile` `no-fake-done`. **Apply to:** placeholders, docstrings, comments; avoid the five marker words and `type: ignore`.

### Pure-move discipline
**Source:** D-07. **Apply to:** `_serve_model` commit alone; `make gear.unchanged` plus `tests/test_api.py` and `tests/regression` green with no test edits, after each seam commit (`Part`, move, 503 reword).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `src/spur/parts.py` | alias module | none | no alias-only module exists; use RESEARCH plain `Part = GearParams` |
| `src/spur/shaft_params.py`, `shaft_calc.py`, `din5480.py`, `din5480_tables.py`, `shaft_model.py` | placeholders | none | docstring-only modules are new; constraints in RESEARCH Pitfall 5 |

## Metadata

**Analog search scope:** `scripts/`, `Makefile`, `pyproject.toml`, `tests/test_hooks.py`, `tests/test_records.py`, `tests/test_api.py`, `src/spur/app.py`, `docs/architecture/decision_log.md`, `bench/RESULTS.md`
**Files scanned:** about 10 (targeted line ranges)
**Pattern extraction date:** 2026-10-23
