# Phase 30: Scope, Seam and Gear-Safety Guard - Research

**Researched:** 2026-10-23
**Domain:** Python repo guardrails: import-linter contracts, a git-tag-baselined regression check, a pure-move refactor of a FastAPI handler, a type alias seam, a FastAPI route-table pin
**Confidence:** HIGH (every unknown below was resolved by running the command on this host, in scratch copies, with nothing committed to the repo)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Gear-safety check (`make gear.unchanged`)
- **D-01:** The target is named `make gear.unchanged`, in the dotted style of
  `fixture.regen`/`golden.regen`.
- **D-02:** The baseline is read from the `v0.6` tag at run time, and nothing is committed.
  - `tests/regression/` and `.github/workflows/ci.yml` are compared with
    `git diff --exit-code v0.6 -- …`, or the `git show v0.6:<path>` equivalent.
  - The gear schema is produced from a temporary `git worktree` of `v0.6` under the same venv.
  - A committed snapshot was rejected: it is a second source of truth that someone could
    regenerate by mistake.
- **D-03:** The schema comparison is on raw HTTP response bytes. Fetch `GET /api/schema`
  through FastAPI's TestClient on both trees and compare bytes, not dicts. This catches
  serialization and ordering drift in the route layer as well.
- **D-04:** The check is its own target, and `make verify` calls it. Every gate run and pre-push
  therefore proves it.
  - Its cost is measured and recorded as part of the phase's gate delta (L43: 300 s bar).
  - Whether it also joins `verify.fast` (the L36 commit slice, under 30 s) is Claude's
    discretion, decided on the measured cost.
- **D-05:** CI runs `make verify` from a shallow checkout that has no tags, and `ci.yml` may not
  be edited. When `v0.6` is missing locally, the check fetches it itself:
  `git fetch --depth=1 origin tag v0.6`, or equivalent.
  - If the fetch fails, the check fails and names the cause.
  - It never skips and never passes without comparing (L08: no silent partial success).
- **D-06:** The check reads green on the tree as it stands. It is seen red once per watched
  item, through deliberate edits to:
  - a file in `tests/regression/`
  - `ci.yml`
  - something that changes the `/api/schema` bytes

  Each red is recorded in `bench/RESULTS.md`. Every gear-file edit this phase makes (D-07–D-09)
  must leave the check green.

#### Seam work
- **D-07:** `_serve_model(params, fmt, quality, request, backend)` is extracted from `app.py`'s
  `model()` in this phase, as a pure-move commit of its own. This resolves the roadmap's
  stop-and-ask: the human chose "extract now, own commit".
  - Proof: `gear.unchanged` stays green, and the whole existing `tests/test_api.py` suite and
    the golden requests pass with no test edits.
  - Gear `model()` becomes a call to `_serve_model(_gear(q), …)`. Do not duplicate the body
    (research F3).
  - **Reversibility:** reversible.
- **D-08:** Add `src/spur/parts.py` holding `Part = GearParams` (an alias), and nothing else.
  - Switch the shared entry-point annotations from `GearParams` to `Part` now:
    - `pool.py`: `:53`, `:100`, `:103`, `:165`, `:252`
    - `records.py`: `:171`, `:211`, `:221`, `:235`, `:259`
    - `app.py`: `BuildBackend` `:117`, `_build_slot` `:263`, `_serve_model`
    - `model.py`: the export/build entry points only. The internal gear helpers, such as
      `_cut_bore(p: GearParams)`, stay `GearParams`.
  - Phase 31 turns the alias into `GearParams | ShaftParams` with a one-line edit to
    `parts.py`, which is not a gear file.
  - This resolves the conflict between the research's "type widening in Phase 30" and the
    boundary "no `ShaftParams` in Phase 30".
- **D-09:** The 503 queue-full message (`app.py:285`, "…{MAX_QUEUED_BUILDS} gears are already
  being built…") is reworded to a part-neutral noun in this phase, with one pinned test.
  - Only a response string changes. No request, part, schema byte or status code changes.
- **D-10:** No `model._build` dispatch stub lands in this phase. An unreachable `isinstance`
  branch would fail the unfinished-work scan, and dead code is not done (CLAUDE.md). The
  dispatch lands with `shaft_model` in Phase 32.
- **D-11:** Amend the roadmap claim that this is "the only phase of the milestone that edits
  gear-side files". It is false: Phase 32 edits `model._build` and `pool._warm`, and Phase 33
  adds routes in `app.py`. Replace it with this rule:
  - Later phases make only additive edits to the shared modules `model.py`, `pool.py` and
    `app.py`, each proved by `make gear.unchanged`.
  - `calc.py`, `params.py`, `tests/regression/`, `ci.yml` and `requirements.txt` are not
    edited for the rest of the milestone.

  Edit `.planning/ROADMAP.md` (Phase 30 "Depends on" and Phase 32/33 text as needed) in this
  phase's docs commit.

#### Import contracts and module layout
- **D-12:** Every shaft contract goes in force in this phase. The shaft modules are created now
  as docstring-only placeholders, since import-linter rejects contract names for modules that do
  not exist. This settles the roadmap's ASSUMPTION: the placeholder files exist so that the
  contracts precede all shaft code.
  - The planner must verify that docstring-only modules pass `make no-fake-done` and coverage.
  - A placeholder may not contain `pass`, `TODO` or a stub function.
- **D-13:** The module layout is frozen now, as the research's flat split (package stays flat).
  Phase 31 onward must use exactly these names:
  - `src/spur/parts.py`
  - `src/spur/shaft_params.py`
  - `src/spur/shaft_calc.py`
  - `src/spur/din5480.py`
  - `src/spur/din5480_tables.py`
  - `src/spur/shaft_model.py`
  - **Reversibility:** costly. Renaming later means editing every contract and every Phase 31–34
    plan that names them.
- **D-14:** These contracts land, as specified in `.planning/research/ARCHITECTURE.md` §6:
  1. **Shaft maths stays free of the CAD kernel and the solid.**
     - Sources: `shaft_params`, `shaft_calc`, `din5480`, `din5480_tables`.
     - Forbidden: `cadquery`, `OCP`, `spur.model`, `spur.shaft_model`.
     - `allow_indirect_imports = false`. The human accepted this stricter form: shaft maths
       cannot reach the kernel even through `params`/`model`.
  2. **Shaft maths stays free of the logger.**
     - Sources: the same four.
     - Forbidden: `spur.records`, `logging`.
  3. **The kernel doorways are model and shaft_model.**
     - Sources: `spur.app`, `spur.cli`, `spur.pool`, `spur.records`, `spur.parts`.
     - Forbidden: `spur.shaft_model`.
     - `allow_indirect_imports = false`.
  4. **Gear maths does not know the shaft.**
     - Sources: `spur.calc`, `spur.params`.
     - Forbidden: every shaft module plus `spur.parts`.
     - `allow_indirect_imports = false`.
  5. The existing "serving process never imports the CAD kernel" contract stays as it is. It
     already covers the shaft through `allow_indirect_imports = false`.

  Each contract is seen red once against a deliberate violation, and the red is recorded.

  Also add the regex belt tests the repo pairs with each contract (`tests/test_records.py:246`
  pattern). The `ShaftParams` hash/frozen tests wait for Phase 31, because no `ShaftParams`
  exists yet.
- **D-15:** The route-table pin is a test.
  - The set of `/api/` routes (path + methods) equals the v0.6 set:
    - `/api/health`
    - `/api/schema`
    - `/api/info`
    - `/api/model.{fmt}`
  - Every additional `/api/` route must start with `/api/shaft/`.
  - It is seen red once against a deliberately added `/api/foo` route.
  - The test asserts that the gear routes' query keys and responses are unchanged.
    `gear.unchanged` covers `/api/schema`; the existing `test_api` suite covers the rest.

#### L46 — scope decision
- **D-16:** L46 calls the product a **"gear and spline generator"**. "Spline" covers later
  ISO 4156 / DIN 5481 families without another scope entry. Each family is still its own
  milestone (REQUIREMENTS.md "Future").
- **D-17:** L46 amends L02 and L05 by reference, giving the new wording, without editing the
  old entries (the log's existing practice).
  - L02 becomes "one parameter model per part type, three front ends each".
  - L05 gains "a second frozen link contract: the shaft's field names and defaults".
  - L46 states what it supersedes and what it leaves alone. It leaves alone: L03, L04, L06,
    L08, the gear's defaults, and L44's 422 rule for gear links.
- **D-18:** Shaft field names and defaults are pinned by a test in Phase 31, but may change by
  logged decision until Phase 33 publishes the first shaft link. From then on, L05's rule
  applies in full: no link exists before Phase 33, so none can break. L46 says this explicitly,
  and it is compatible with Phase 31 criterion 1's pinned test.
- **D-19:** Change `AGENTS.md`'s "What we're building" (CLAUDE.md is a symlink to it) in this
  phase. `README.md` changes at Phase 33, when the shaft is usable; it must not advertise a
  feature that does not exist yet.
- **D-20:** The L46 commit precedes the first commit that adds a shaft module, including the
  D-12 placeholders. Commit order inside the phase is therefore: L46 → contracts and
  placeholders.

### Claude's Discretion
- The exact contents and location of the route-table pin test.
- The format of the red-run records in `bench/RESULTS.md`, following the section convention
  already there.
- **Gate-delta baseline.** Either re-run `make verify` on the `v0.6` tree on this host, or use
  the recorded close reading `1348 passed in 236.23s` (18-CPU M5 Max). Prefer the re-run if
  host or load conditions differ, and state which was used.
- Whether `gear.unchanged` also joins `verify.fast` (D-04).
- How the temp worktree is created and cleaned up (trap on exit; no leftover worktrees under
  `.git/worktrees`).
- Commit split, within "one concern per commit". The `_serve_model` move must be its own
  commit (D-07).

### Deferred Ideas (OUT OF SCOPE)
- The `README.md` scope wording moves to Phase 33 (D-19).
- The `model._build` shaft dispatch and the `pool._warm` shaft import move to Phase 32 (D-10,
  D-11).
- The `ShaftParams` frozen/hashable/hash-inequality tests move to Phase 31 (D-14).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-scope-decision-logged | A new `Lxx` widens the product to a gear and spline generator, amends L02/L05, logged before any shaft code lands | "L46 and docs commit" (log format, commit order, AGENTS.md and ROADMAP edit sites); commit-order check command in Validation Architecture |
| REQ-gear-unchanged-proof | A check run at every phase close proves regression dir, `ci.yml` and gear `/api/schema` bytes are unchanged vs `v0.6`; seen red once | Resolved Unknown 3: working prototype, measured 0.66 s, 6 red scenarios run; hook-environment hazard; CI shallow-clone fetch behaviour |
| REQ-shaft-routes-separate | Shaft under `/api/shaft/...`; gear routes unchanged; import contracts keep shaft maths free of `cadquery`, the logger and gear maths; solid reachable only through `model` | Resolved Unknowns 1 and 6: contract behaviour measured (5 reds), the Phase 32 `cli -> model -> shaft_model` hazard, the exact route list |
| REQ-gate-cost-recorded (cross-cutting) | Each phase records its `make verify` delta on the same host | Resolved Unknown 4: same-host `make verify` reading on v0.6-equivalent code, cost of the new check, `RESULTS.md` section shape |
</phase_requirements>

## Project Constraints (from CLAUDE.md / AGENTS.md)

Read this session: `/Users/half/git/halfb00t/spur/CLAUDE.md` (symlink to `AGENTS.md`) and `docs/CODING_VALUES.md` "Coupling". The planner verifies each plan against these:

- **Gate:** `make verify` is the only "done" (ruff, `mypy --strict` over `src tests docker bench scripts`, import contracts, `no-fake-done`, pytest with coverage). State the command and the result line. `make check` needs Docker; not required here.
- **Stop and ask** on: a locked decision that looks wrong, unverified library behaviour, conflicting evidence, destructive git operations. The one open item below (worktree vs `git archive`) is a deviation from D-02's wording and is surfaced as Open Question 1.
- **Standing rules:** a printed number is a number someone cuts metal to (L08); a parameter the user did not set never silently changes the part (L05, L03). This phase's whole purpose is proving the second.
- **Simple and small:** surgical edits; one concern per commit; no speculative abstraction. No `TODO`, `pass`, unreachable branches (`make verify` greps for them).
- **New behaviour ships with its tests;** a guard counts only after it was seen red once against a deliberate violation and the red is recorded (CODING_VALUES "Coupling").
- **Comments explain why** and carry the measurement that forced the choice. `calc.py` never imports `cadquery`; vendor types stop at their boundary; a parameter is validated once at the `GearParams` boundary.
- **Debt/ideas:** non-blocking items go to `docs/tech_debt/active/` or `docs/ideas/` with an INDEX row; state in the final reply whether any item was filed.
- **Commit messages:** Conventional Commits, normal prose; end with the Co-Authored-By line from the session attribution reminder. User-facing text terse (caveman).
- **English throughout.**

## Summary

Phase 30 adds guards and a seam; it must change no gear byte. All seven unknowns resolved by measurement on this host (import-linter 2.15, grimp 3.17, git 2.56.0, GNU Make 4.4.1, Python 3.12.15). The decisive findings:

1. **Import-linter accepts docstring-only modules** as contract sources and forbidden modules, and all four new contracts load and read `KEPT`. Two behaviours differ from the CONTEXT's assumption: a nonexistent **source** module is a hard error (`Module 'spur.nonexistent' does not exist.`) but a nonexistent **forbidden** module is **silently accepted** (`9 kept, 0 broken` with `shaft_model.py` deleted). A typo in a forbidden list would never go red, so add a tiny existence-guard test. A larger hazard waits for Phase 32: contract 3 lists `spur.cli` as a source with `allow_indirect_imports = false`; the moment `model.py` statically imports `shaft_model`, `cli -> model -> shaft_model` breaks it (measured). Phase 32 must add `ignore_imports = ["spur.model -> spur.shaft_model"]` with that edge (it errors with "No matches for ignored import" if added before the edge exists).
2. **`make gear.unchanged` is cheap and shadow-proof** if the `v0.6` source is extracted with `git archive v0.6 src` and each tree's `/api/schema` is fetched in a subprocess with `PYTHONPATH=<tree>/src` (it precedes the editable install's `.pth`, which appends `src` last). The whole prototype ran in 0.66 s wall. A literal `git worktree add` also works (0.24 s) but is **unsafe inside the pre-commit hook**: git exports `GIT_INDEX_FILE` to hooks, and a `git worktree add` run in the hook emptied the commit being made (reproduced in a scratch repo). Since the check is wired into `verify.static`, which `verify.fast` runs at every commit, use `git archive`. This deviates from D-02's wording ("temporary git worktree") and needs the human's confirmation (Open Question 1).
3. **Docstring-only placeholders pass everything:** coverage reports them `0 stmts, 100.00%` and leaves the total untouched; `no-fake-done` only trips on the five marker words or a mypy-suppression comment.
4. **`verify.static` is the right home** for the check: `tests/test_hooks.py` pins that `verify` and `verify.fast` share one identical static prefix, so adding it there needs no test edit, and costs about 0.7 s of the 30 s commit budget (slice measured 14.6 s wall at load ~11).

**Primary recommendation:** Commit order L46 (+ AGENTS.md + ROADMAP amendment) -> `gear.unchanged` (script, Makefile wiring, tests) -> the wall (placeholders, `parts.py`, four contracts, belt tests, route pin) -> seam edits made under all guards (`Part` annotations, `_serve_model` pure move, 503 wording) -> `bench/RESULTS.md` reds and gate delta.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Scope decision L46 | Docs (decision log, AGENTS.md, ROADMAP) | — | Pure documentation; must land first (D-20) |
| Gear-safety check | Dev tooling (`scripts/`, Makefile, git) | API tier (the probe imports `spur.app`) | It reads git objects and calls the app in-process; ships nothing |
| Import walls | Build/lint tier (`pyproject.toml`, import-linter) | Test tier (regex belts) | Static module-graph facts, enforced by `make lint-imports` |
| Route-prefix pin | API / Backend (test over `app.routes`) | — | A fact about the ASGI route table |
| `_serve_model` | API / Backend (`app.py`) | — | Admission, cache and error mapping already live in the handler |
| `Part` alias | API / Backend + Database-free shared types (`parts.py`) | — | Imported by pool, records, app, model; no logic |
| 503 wording | API / Backend | — | Response string only |

## Standard Stack

### Core (all already installed; no new dependency)

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| import-linter | 2.15 | `forbidden` contracts | Already the repo's boundary tool (`pyproject.toml:166-223`) [VERIFIED: `.venv/bin/pip list`] |
| grimp | 3.17 | module graph under import-linter | Transitive dependency of import-linter [VERIFIED: `.venv/bin/pip list`] |
| FastAPI / Starlette | 0.141.1 / 1.6.0 | `TestClient`, `app.routes` | The app's framework [VERIFIED: `.venv/bin/pip list`] |
| httpx | 0.28.1 | `TestClient` transport | Already a dev dependency [VERIFIED: `.venv/bin/pip list`] |
| pytest / pytest-cov / pytest-xdist | 9.1.1 / 7.1.0 / 3.8.0 | tests, coverage | Existing gate [VERIFIED: `.venv/bin/pip list`] |
| git | 2.56.0 | `diff`, `archive`, `rev-parse`, `fetch` | Baseline source [VERIFIED: `git --version`] |
| Python stdlib: `subprocess`, `tarfile`, `tempfile`, `tomllib` | 3.12.15 | the script and the existence guard | No new package [VERIFIED: `python -c "import tomllib"`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `git archive v0.6 src` | `git worktree add --detach` (D-02 wording) | Same cost (0.24 s + 0.07 s remove) but mutates `.git/worktrees`, leaves a prunable entry if killed, and corrupts a commit when run inside a hook (below). |
| Python script `scripts/gear_unchanged.py` | Makefile shell recipe | The script is testable on a scratch git repo (red scenarios without touching the real tree) and matches `scripts/pr_land.py` (`$(PY) -m scripts.pr_land`). A shell recipe cannot be unit-tested. |
| `PYTHONPATH` + subprocess | importing both trees into one process | One process cannot hold two `spur` packages; `sys.modules` caching makes the second import silently reuse the first. |

**Installation:** none. `requirements.txt` stays byte-identical (REQUIREMENTS.md rule).

## Package Legitimacy Audit

No external package is installed or added by this phase. `requirements.txt` and `pyproject.toml` dependency tables are not edited (`pyproject.toml` gains only `[[tool.importlinter.contracts]]` tables). The `slopcheck`-style gate is therefore not applicable.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | — | — | — | — | n/a | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 make verify / verify.fast / make gear.unchanged
      |
      v
 verify.static ----> lint | typecheck | lint-imports | no-fake-done | gear.unchanged
                                              |                           |
                                  pyproject contracts                     v
                                  C1..C4 + existing           scripts/gear_unchanged.py
                                  (names -> src/spur/*.py)       |
                                                                 1. tag v0.6 local?  --no--> git fetch --depth=1 origin tag v0.6 --fail--> RED (names cause)
                                                                 2. git diff --exit-code v0.6 -- tests/regression/ ci.yml  (+ untracked files there) --> RED
                                                                 3. git archive v0.6 src --> temp dir  (cleaned by TemporaryDirectory)
                                                                 4. subprocess A: PYTHONPATH=<temp>/src  python -P -c PROBE
                                                                    subprocess B: PYTHONPATH=<repo>/src  python -P -c PROBE
                                                                    PROBE: TestClient(app).get("/api/schema", Accept-Encoding: identity)
                                                                           prints spur.__file__, status, raw body
                                                                 5. assert each spur.__file__ is under its own src (shadow guard)
                                                                 6. bytes(A) == bytes(B) else RED

 request path after the seam (gear only, shape unchanged):
 GET /api/model.{fmt} -> model(fmt, q, request, backend)
                            -> _serve_model(_gear(q), fmt, q.quality, request, backend)   [Phase 33: shaft route is the 2nd caller]
                                  -> _EXPORTS cache -> _build_slot (503 "Busy: N parts ...") -> backend(Part, fmt, quality)
```

### Recommended Project Structure

```
src/spur/
├── parts.py            # Part = GearParams  (imports params only)            NEW
├── shaft_params.py     # docstring only                                       NEW placeholder
├── shaft_calc.py       # docstring only                                       NEW placeholder
├── din5480.py          # docstring only                                       NEW placeholder
├── din5480_tables.py   # docstring only                                       NEW placeholder
└── shaft_model.py      # docstring only                                       NEW placeholder
scripts/gear_unchanged.py        # the check                                  NEW
tests/test_seam.py               # route pin, regex belts, contract-name guard NEW
tests/test_gear_unchanged.py     # the script on a scratch git repo           NEW
```

### Pattern 1: Contract tables (add after `pyproject.toml:223`)

Contract names follow the existing "The ... stays free of ..." phrasing; each carries a *why* comment with the measured constraint. Shapes below were run and all read `KEPT` against placeholders [VERIFIED: scratch copy, `lint-imports`, 47 files, 85 dependencies, `Contracts: 9 kept, 0 broken`]:

```toml
[[tool.importlinter.contracts]]
name = "The shaft maths stays free of the CAD kernel and the solid"
type = "forbidden"
source_modules = ["spur.shaft_params", "spur.shaft_calc", "spur.din5480", "spur.din5480_tables"]
forbidden_modules = ["cadquery", "OCP", "spur.model", "spur.shaft_model"]
allow_indirect_imports = false

[[tool.importlinter.contracts]]
name = "The shaft maths stays free of the logger"
type = "forbidden"
source_modules = ["spur.shaft_params", "spur.shaft_calc", "spur.din5480", "spur.din5480_tables"]
forbidden_modules = ["spur.records", "logging"]

[[tool.importlinter.contracts]]
name = "The kernel doorways are model and shaft_model"
type = "forbidden"
source_modules = ["spur.app", "spur.cli", "spur.pool", "spur.records", "spur.parts"]
forbidden_modules = ["spur.shaft_model"]
allow_indirect_imports = false

[[tool.importlinter.contracts]]
name = "The gear maths does not know the shaft"
type = "forbidden"
source_modules = ["spur.calc", "spur.params"]
forbidden_modules = ["spur.shaft_params", "spur.shaft_calc", "spur.din5480",
                     "spur.din5480_tables", "spur.shaft_model", "spur.parts"]
allow_indirect_imports = false
```

Contract 2 omits `allow_indirect_imports` (default allows indirect), matching the existing "gear maths stays free of the logger" contract and ARCHITECTURE §6 item 2; D-14 only asks `false` for contracts 1, 3, 4. [VERIFIED: pyproject.toml:201-211 read this session]

### Pattern 2: `gear.unchanged` script skeleton (prototype ran green and red)

```python
# scripts/gear_unchanged.py  -- prototype from scratch; mypy --strict style still to be applied
TAG = "v0.6"
WATCHED = ("tests/regression/", ".github/workflows/ci.yml")
PROBE = r"""
import sys
import spur
from fastapi.testclient import TestClient
from spur.app import app
r = TestClient(app).get("/api/schema", headers={"Accept-Encoding": "identity"})
sys.stdout.buffer.write(spur.__file__.encode() + b"\n" + str(r.status_code).encode() + b"\n" + r.content)
"""

def ensure_tag() -> None:
    if git("rev-parse", "-q", "--verify", f"{TAG}^{{commit}}", check=False).returncode == 0:
        return
    got = git("fetch", "--depth=1", "origin", "tag", TAG, check=False)
    if got.returncode != 0:
        sys.exit(f"gear.unchanged: tag {TAG} is not local and could not be fetched: {got.stderr.decode().strip()}")

def schema_of(src: Path) -> bytes:
    env = {**os.environ, "PYTHONPATH": str(src)}
    out = subprocess.run([sys.executable, "-P", "-W", "ignore", "-c", PROBE], env=env,
                         capture_output=True, check=True).stdout
    where, status, body = out.split(b"\n", 2)
    if status != b"200" or not Path(where.decode()).resolve().is_relative_to(src.resolve()):
        sys.exit(f"gear.unchanged: probe imported {where!r} (status {status!r}), not {src}")
    return body
# main(): ensure_tag(); git diff --exit-code --stat TAG -- WATCHED; git ls-files --others --exclude-standard -- WATCHED;
#         TemporaryDirectory: git archive TAG src | tarfile.extractall(filter="data"); compare bytes.
```

Source: prototype `proto/gear_unchanged.py` in the session scratchpad; behaviours in Resolved Unknown 3. `-P` (don't prepend cwd) was verified to keep `PYTHONPATH` first on `sys.path` [VERIFIED: ran `python -P` with PYTHONPATH; `sys.path[0]` was the archive `src`].

### Pattern 3: Route-table pin

`app.routes` (read this session by running `from spur.app import app`) holds, in order [VERIFIED: ran against the tree]:

```
Route    /openapi.json            ['GET','HEAD']
Route    /docs                    ['GET','HEAD']
Route    /docs/oauth2-redirect    ['GET','HEAD']
Route    /redoc                   ['GET','HEAD']
Mount    /static                  []              (Mount has no .methods)
APIRoute /                        ['GET']
APIRoute /api/health              ['GET']
APIRoute /api/schema              ['GET']
APIRoute /api/info                ['GET']
APIRoute /api/model.{fmt}         ['GET']
```

```python
from fastapi.routing import APIRoute
V06_API = {("/api/health", frozenset({"GET"})), ("/api/schema", frozenset({"GET"})),
           ("/api/info", frozenset({"GET"})), ("/api/model.{fmt}", frozenset({"GET"}))}

def test_every_api_route_beyond_v0_6_lives_under_the_shaft_prefix() -> None:
    api = {(r.path, frozenset(r.methods)) for r in app.routes
           if isinstance(r, APIRoute) and r.path.startswith("/api/")}
    extra = {p for p, _ in api - V06_API}
    assert V06_API <= api
    assert all(p.startswith("/api/shaft/") for p in extra), extra
```

Also assert every non-`/api/` route path is in the fixed set `{"/", "/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc", "/static"}`, so a shaft route added outside `/api/` (e.g. `/shaft`) is caught too. For the query-key assertion, read `app.openapi()["paths"]` parameter names of `/api/info` and `/api/model.{fmt}` and compare with `set(GearParams.model_fields) | {"mate_teeth"}` / `| {"quality"}` (`InfoQuery`/`ModelQuery` extras, `app.py:232-240`). A shaft field leaking into a gear route's query then fails.

### Anti-Patterns to Avoid

- **`git worktree add` from a gate target.** It runs at pre-commit through `verify.fast`; git exports `GIT_INDEX_FILE` (to `.git/index.lock` for `commit -a`, a `next-index-*.lock` for `git commit <path>`) and the worktree checkout then overwrote the index of the commit in progress (measured: the resulting commit was empty). See Pitfall 1.
- **Comparing the tree with itself.** If the editable install shadowed `PYTHONPATH`, both probes would import the working tree and every run would pass. The `spur.__file__` assertion is not optional.
- **`Accept-Encoding: gzip` for the byte compare.** The app's `GZipMiddleware(minimum_size=1024)` compresses the 8.7 KB schema and gzip headers carry an mtime; request identity so the bytes are the JSON itself. `TestClient.get(...).content` otherwise returns decoded bytes and hides the encoding difference. [VERIFIED: `app.py:212` read this session; prototype used `identity`]
- **A `model._build` dispatch stub or `pass` in a placeholder** (D-10, D-12).
- **`Part: TypeAlias = GearParams` or `type Part = GearParams`.** With `UP` selected and `target-version = "py312"`, `TypeAlias` is rewritten by UP040; a `type` statement makes `Part` a `TypeAliasType`, which cannot be called or used in `isinstance`. Use the plain assignment `Part = GearParams`; Phase 31's `Part = GearParams | ShaftParams` still works with `isinstance`. Ruff and mypy `--strict` were run on a scratch copy with the plain alias and `Part` used in `pool.py` signatures: `All checks passed!`, `Success: no issues found in 16 source files`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Is a file the same as at `v0.6`? | A hash manifest or committed snapshot | `git diff --exit-code v0.6 -- <paths>` | D-02 rejects a second source of truth |
| Getting the old source tree | Checkout, copy, `git show` per file | `git archive v0.6 src \| tarfile` | One call, no repo state |
| Detecting a forbidden import | An AST walker or grep | import-linter contract + a regex belt | Repo convention (CODING_VALUES "Coupling") |
| Enumerating routes | Parsing `/openapi.json` | `app.routes` + `fastapi.routing.APIRoute` | Includes routes hidden from OpenAPI (`/` has `include_in_schema=False`) |
| Finding contract module names | Hand-copied list | `tomllib.load` of `pyproject.toml` in the guard test | Keeps the guard in step with the contracts |

**Key insight:** every guard here is a few lines over a tool the repo already runs; the cost is in the red-run evidence, not the code.

## Common Pitfalls

### Pitfall 1: A git mutation inside a commit hook corrupts the commit
**What goes wrong:** `make verify.fast` runs at pre-commit; any `git` subcommand that writes the index inherits `GIT_INDEX_FILE`.
**Why it happens:** git sets `GIT_INDEX_FILE` for hooks (`.git/index`, `.git/index.lock` for `commit -a`, `.git/next-index-<pid>.lock` for a path commit) [VERIFIED: scratch repo hook dumped `env | grep ^GIT_`].
**How to avoid:** use only read-only git (`rev-parse`, `diff`, `ls-files`, `archive`, `fetch` of a tag). With a hook calling `git worktree add -q --detach ... v1` the commit came out empty while `git status` still showed ` M a` and `?? newfile` [VERIFIED: scratch repo].
**Warning signs:** a commit with no files in `git show --stat`.

### Pitfall 2: The editable install shadows the other tree (silent self-compare)
**What goes wrong:** both probes import the working tree; `gear.unchanged` is green forever.
**Why it happens:** the venv installs spur editable via `_editable_impl_spur.pth`, which **appends** `/Users/half/git/halfb00t/spur/src` to `sys.path` [VERIFIED: printed `sys.path`; `.pth` content]. `PYTHONPATH` entries come before it, so `PYTHONPATH=<archive>/src` wins [VERIFIED: probe printed `spur.__file__` under the archive].
**How to avoid:** set `PYTHONPATH` for both probes, run `python -P`, and assert `spur.__file__` lies under the intended `src`. CI installs the same way [ASSUMED: Linux setuptools editable layout matches; the assertion fails loudly if it does not].

### Pitfall 3: `include_external_packages` and silent typos
**What goes wrong:** a mistyped *forbidden* module (`spur.shaftmodel`) never fails.
**Why it happens:** import-linter validates source modules only; with `shaft_model.py` deleted, all nine contracts still read `KEPT` [VERIFIED: scratch copy].
**How to avoid:** guard test: every `spur.*` name in every contract resolves to `src/spur/<name>.py`; also a placeholder file exists for every name D-13 freezes.

### Pitfall 4: Phase 32's `cli -> model -> shaft_model` breaks contract 3
**What goes wrong:** when Phase 32 adds `from . import shaft_model` in `model.py`, contract 3 (sources include `spur.cli`, `allow_indirect_imports = false`) fails: `spur.cli -> spur.model (l.102)` then `spur.model -> spur.shaft_model`. [VERIFIED: scratch copy, appended a local import to `model.py`]
**How to avoid / handoff to Phase 32:** add `ignore_imports = ["spur.model -> spur.shaft_model"]` to contract 3 in the same commit as the edge (measured: `C3 ... KEPT (1 ignored import)`). Adding it earlier errors with `No matches for ignored import spur.model -> spur.shaft_model.` [VERIFIED]. Record this in the Phase 30 summary and in the contract's why-comment. Alternative for Phase 32: import by `importlib` string like `pool._warm` (invisible to the linter), which would hide the doorway.

### Pitfall 5: The unfinished-work scan reads docstrings
**What goes wrong:** a placeholder docstring that says "stub" is fine, but one containing `TODO`, `FIXME`, `XXX`, `HACK`, `NotImplementedError`, or `type: ignore` / `mypy: ignore-errors` fails `make no-fake-done`. [VERIFIED: Makefile `no-fake-done` recipe read; first block is tracked-files-only `git grep -nwE`, second block uses `--untracked`]
**How to avoid:** describe the module's future role in prose without those words; run `make no-fake-done` after `git add`.

### Pitfall 6: `gear.unchanged` ignores untracked files
**What goes wrong:** `git diff v0.6 -- tests/regression/` does not show a new, untracked file there.
**How to avoid:** also fail on `git ls-files --others --exclude-standard -- tests/regression/ .github/workflows/ci.yml` (prototype: red, exit 1 for `tests/regression/new.json`). `__pycache__` and `*.pyc` are in `.gitignore`, so they do not trip it.

### Pitfall 7: `test_hooks.py` pins the shared static prefix
**What goes wrong:** putting `gear.unchanged` as a prerequisite of `verify` only makes `whole_static != fast_static` in `test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe`. [VERIFIED: tests/test_hooks.py:109-155 read this session]
**How to avoid:** make it a prerequisite of `verify.static` (Makefile:113). Add a `.PHONY` entry, a `## ...` comment (the `help` target greps `^[a-z][a-z.-]*:.*##`), and update the `verify.static` description text.

### Pitfall 8: Reading the result line of a loaded host as the phase measurement
**What goes wrong:** the research-time reading (below) was taken at 1-minute load 11 to 37, not idle; Phase 25's rule demands an idle host for a decisive reading.
**How to avoid:** the phase records its own readings with `uptime`/load beside them, and states which baseline it used (see Resolved Unknown 4).

## Code Examples

### Existing-contract failure strings (use as the `First failure line` column)
Measured by appending one import line to a placeholder or gear module in a scratch copy and running `lint-imports` [VERIFIED: scratch]:

| Contract | Deliberate violation | First failure line |
|----------|---------------------|--------------------|
| 1 kernel and solid | `shaft_calc.py`: `import cadquery` | `spur.shaft_calc is not allowed to import cadquery:` |
| 1 kernel and solid | `shaft_calc.py`: `from . import model` | `spur.shaft_calc is not allowed to import spur.model:` |
| 2 logger | `shaft_calc.py`: `import logging` | `spur.shaft_calc is not allowed to import logging:` |
| 2 logger | `shaft_params.py`: `from . import records` | `spur.shaft_params is not allowed to import spur.records:` |
| 3 doorways | `app.py`: `from . import shaft_model` | `spur.app is not allowed to import spur.shaft_model:` |
| 3 doorways | `cli.py` / `pool.py` / `records.py` / `parts.py` same line | `spur.<module> is not allowed to import spur.shaft_model:` |
| 4 gear maths | `calc.py`: `from . import parts` | `spur.calc is not allowed to import spur.parts:` |
| 4 gear maths | `params.py`: `from . import shaft_params` | `spur.params is not allowed to import spur.shaft_params:` |

Each run printed `Contracts: 8 kept, 1 broken.`. Real runs revert with `git checkout -- <file>` and record the log.

### Contract-name guard (closes Pitfall 3)

```python
import tomllib
from pathlib import Path

def test_every_module_a_contract_names_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    names = {m for c in cfg["tool"]["importlinter"]["contracts"]
             for key in ("source_modules", "forbidden_modules") for m in c.get(key, [])
             if m.startswith("spur.")}
    missing = [m for m in sorted(names) if not (root / "src/spur" / f"{m.removeprefix('spur.')}.py").exists()]
    assert not missing, missing
```

### Regex belt (pattern of `tests/test_records.py:246`)

```python
SHAFT_MATHS = ("shaft_params", "shaft_calc", "din5480", "din5480_tables")
FORBIDDEN = r"^\s*(import|from)\s+(logging|cadquery|OCP|\.model|\.shaft_model|\.records|spur\.(model|shaft_model|records))\b"
def test_shaft_maths_sources_import_no_kernel_solid_or_logger() -> None:
    for name in SHAFT_MATHS:
        source = (SRC / f"{name}.py").read_text(encoding="utf-8")
        assert not re.search(FORBIDDEN, source, re.MULTILINE), name
```

(The belt is vacuously true against docstring placeholders; it earns its keep from Phase 31. It is seen red by appending `import logging` to a placeholder, together with contract 2.)

### The 503 reword and its pin

`app.py:285` reads `"msg": f"Busy: {MAX_QUEUED_BUILDS} gears are already being built or "` followed by `"compressed. Try again in a moment."` [VERIFIED: Read app.py:280-290]. Change the noun to `parts`. Pin in `tests/test_api.py` as a new test next to `test_a_saturated_service_refuses_instead_of_queueing` (line 985) or extend nothing: no existing test or other file pins the old text [VERIFIED: grep over tests/, bench/, docker/, scripts/, web/, src/spur/static, README, docs for "gears are", "already being built", "Busy:" found only `app.py:285`; `tests/test_bench.py:649` and `test_api.py` read only `detail[0]["type"] == "busy"`].

```python
assert r.json()["detail"][0]["msg"] == (
    f"Busy: {app_module.MAX_QUEUED_BUILDS} parts are already being built or compressed. "
    "Try again in a moment.")
```

## Resolved Unknowns (the seven checks)

### 1. import-linter behaviour [VERIFIED: scratch copy of `src/` + `pyproject.toml`, `PYTHONPATH=<copy>/src lint-imports`]

| Question | Result |
|----------|--------|
| Docstring-only source modules (`shaft_params`, `shaft_calc`, `din5480`, `din5480_tables`, `parts`) | Accepted. `Analyzed 47 files, 85 dependencies`, all nine contracts `KEPT` |
| Forbidden module that exists but imports nothing (`shaft_model`) | Accepted |
| Contract names a nonexistent **source** module | Hard error: `Module 'spur.nonexistent' does not exist.` |
| Contract names a nonexistent **forbidden** module (`spur.ghost`, or `shaft_model.py` deleted) | **Silently accepted**: `Contracts: 9 kept, 0 broken.` |
| Contract 3 sources (`app`, `cli`, `pool`, `records`, `parts`) vs `shaft_model` with `allow_indirect_imports = false` | Expressible; red on a direct import from each source |
| Contract 4 (`calc`, `params` forbidden every shaft module + `parts`) | Expressible; red on `calc -> parts` and `params -> shaft_params` |
| Contract 1 with `cadquery`, `OCP`, `spur.model`, `spur.shaft_model` forbidden, indirect off | Expressible; red on `shaft_calc -> cadquery` and `shaft_calc -> spur.model` |
| Contract 2 with `logging` forbidden | Expressible; red on `import logging` |
| Phase 32 shape (`model` statically imports `shaft_model`) | Contract 3 BROKEN via `spur.cli -> spur.model (l.102)` -> `spur.model -> spur.shaft_model (l.841 in the scratch)`; `ignore_imports` fixes it; adding `ignore_imports` for an absent edge errors |

Implication for D-12: placeholders are required for the five *source* modules (`shaft_params`, `shaft_calc`, `din5480`, `din5480_tables`, `parts`); `shaft_model` is only ever a forbidden name today, so D-13's six-file layout is kept for the frozen names and the existence-guard test, not because the linter forces it.

### 2. Placeholders vs `make no-fake-done` and coverage [VERIFIED]

- Coverage: `[tool.coverage.run] source = ["src/spur"]`, `branch = true`; `[tool.coverage.report] fail_under = 96`, `precision = 2` (pyproject.toml read this session). A scratch package with a one-line-docstring module reported `src/pk/empty.py  0 0 0 0 100.00%` and a `TOTAL` unaffected by it; no `skip_empty` or `omit` is configured. A module with zero statements is a 0/0 row shown as 100 %, not a failure and not excluded.
- Current total with the tree as it stands: `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached` (this session's `make verify`). `parts.py` adds one covered statement.
- `no-fake-done`: see Pitfall 5.
- mypy `--strict` and ruff accept a docstring-only module and the plain `Part = GearParams` alias [VERIFIED: scratch].

### 3. `gear.unchanged` prototype [VERIFIED: prototype + scratch clones]

| Measurement | Value |
|-------------|-------|
| Editable install | `_editable_impl_spur.pth`; `sys.path` ends `.../site-packages`, `/Users/half/git/halfb00t/spur/src` |
| One probe (import `spur.app`, TestClient, one GET) | 0.33 s wall; `cadquery`/`OCP` not in `sys.modules`; no pool (a `TestClient` used without `with` does not run `lifespan`) |
| `git archive v0.6 src \| tar -x` | 0.016 s |
| Whole prototype, green | 0.66 s wall, 8723 schema bytes, both trees equal |
| `git worktree add --detach <tmp> v0.6` / `worktree remove --force` | 0.24 s / 0.07 s; `.git/worktrees` absent after removal |
| `git fetch --depth=1 origin tag v0.6` in a `--depth=1` clone (file:// origin) | 0.074 s; afterwards `git diff --exit-code v0.6 -- ...` and `git archive v0.6 src` both work in the shallow clone |
| Missing tag + unreachable origin | `fatal: '/nonexistent' does not appear to be a git repository`; script exits 1 naming the cause |
| `v0.6` ref | annotated tag object `b7f217f4efc692968e4b06d515cc7867d2f6c6e0`, peels to `792b45c033c38b0fef12f85cdbba1df36adb3a69` on origin [VERIFIED: `git ls-remote --tags origin 'v0.6*'`]; every `git diff/archive v0.6` peels automatically; `rev-parse v0.6^{commit}` for existence |

Red scenarios run in a scratch clone with the prototype: regression file edit (exit 1, `tests/regression/corpus.py | 1 +`); new untracked file in `tests/regression/` (exit 1); `ci.yml` edit (exit 1); schema bytes (changing a field `title="Teeth"` to `title="Teeth!"` in `params.py`: `gear.unchanged: /api/schema bytes differ from v0.6`, exit 1); tag missing and origin unreachable (exit 1, cause named). Green on the unedited tree: exit 0.

CI: `.github/workflows/ci.yml` uses `actions/checkout@v4` with no `fetch-depth` or `fetch-tags` and runs `make verify PYTHON=python` (ci.yml:19, :46). Whether the persisted checkout credentials allow `git fetch --depth=1 origin tag v0.6` on a runner is [ASSUMED]; the repo is public and the fetch is of a tag of the same repo. The first CI run of the phase is the proof, the same way L36 A1 was read; if it fails, the check fails and names the cause (D-05), and ci.yml cannot be edited, so the fallback would be a human decision.

Cleanup: with `tempfile.TemporaryDirectory` no trap is needed and nothing is registered under `.git`. If the human prefers the literal worktree, strip `GIT_INDEX_FILE`/`GIT_DIR`-family variables from the subprocess env and register cleanup in `try/finally` plus a `git worktree prune`.

### 4. Gate and `verify.fast` cost [VERIFIED: ran both on this host, 2026-10-23]

- Makefile:113-115 (read this session): `verify.static: $(HOOKS) lint typecheck lint-imports no-fake-done`, `verify: verify.static test`, `verify.fast: verify.static test.fast`.
- `make verify.fast`: `947 passed in 13.86s`, total 14.6 s wall (1-minute load 11.39 at start). Adding ~0.7 s keeps it far under L36's 30 s.
- `make verify` on `HEAD 760ac4e`: `1348 passed in 239.51s (0:03:59)`, `make verify 668.52s user 508.04s system 489% cpu 4:00.37 total`, coverage `97.99%`. `git diff --stat v0.6 HEAD -- src tests Makefile pyproject.toml bench requirements.txt .github` is empty, so this tree is v0.6-equivalent code. Load during the run was heavy and variable (1-minute 11 to 37; other sessions active), CPU `Apple M5 Max`. This is a **non-idle corroborating reading**, not a decisive one under Phase 25's rule.
- Recorded v0.6 close reading: `1348 passed in 236.23s` [CITED: `.planning/PROJECT.md`, `.planning/RETROSPECTIVE.md`, `.planning/milestones/v0.6-MILESTONE-AUDIT.md`]. The two differ by +3.28 s (1.4 %), inside Phase 25's ~8 % run-to-run spread (Makefile comment at the `test:` target).
- Recommendation: use the recorded `236.23 s` as the baseline of record, quote this session's 239.51 s as a same-host cross-check, and record the Phase 30 close reading with its load beside it. The new tests add a few seconds at most (no CAD); `gear.unchanged` adds ~0.7 s, `lint-imports` a few more ms. Expected delta is far inside the spread, which the section should say instead of claiming a precise delta.

### 5. Annotation sites and the `model()` move [VERIFIED: grep/Read this session]

| File | Lines (current) | Symbol |
|------|-----------------|--------|
| `pool.py` | `32` import; `53` `build_export`; `100` `executor_for`; `103` `recreate_for`; `165` `_run_with_timeout`; `252` `export` | all `p: GearParams` |
| `records.py` | `39` import; `171` `_gear_fields`; `211` `build_started`; `221` `export_served`; `235` `build_failed`; `259` `queue_refused` | all `p: GearParams` |
| `app.py` | `38` import; `117` `BuildBackend = Callable[[GearParams, str, str], Awaitable[bytes]]`; `263` `_build_slot(request_id, p: GearParams, ...)`; `285` 503 text | `_gear` (`:242`), `InfoQuery`/`ModelQuery` (`:232-240`), `schema()` (`:375`) stay `GearParams` |
| `model.py` | `51` import; `772` `_build`; `791` `_build_checked`; `804` `build`; `809` `_write_export`; `833` `export` | D-08 says entry points only: `build` (`:804`) and `export` (`:833`); the internals at `:425-709` stay `GearParams` |

After the switch, `GearParams` becomes unused in `pool.py` and `records.py` (their only uses are these annotations), so the import is replaced by `from .parts import Part` (ruff F401 would flag a leftover). `app.py` keeps `GearParams` for `_gear`, the query classes and `schema()`. With the plain alias, mypy sees identical types, so nothing else changes.

`model()` body (`app.py:386-504`): signature `async def model(fmt: Literal["stl","step"], q: Annotated[ModelQuery, Query()], request: Request, backend: Annotated[BuildBackend, Depends(build_backend)]) -> Response`, decorator at `:384-385`. The body from `request_id = uuid.uuid4().hex[:8]` (`:393`) through `return Response(data, media_type=MEDIA_TYPES[fmt], headers=headers)` (`:504`) is moved; its only uses of `q` are `q.quality` (lines 401, 417, 418, 422, 423, 436, 447, 461, 490, 494) and `params = _gear(q)` (`:394`). `_serve_model(params, fmt, quality, request, backend)` takes `params` and `quality` as arguments and the body is otherwise byte-for-byte the same; `model()` keeps the decorator, signature, OpenAPI `responses=` and the sentences of its comments that talk about the endpoint, and ends `return await _serve_model(_gear(q), fmt, q.quality, request, backend)`. Types: `fmt: Literal["stl","step"]`, `quality: Literal["preview","fine"]` (`ModelQuery.quality`), `params: Part`. The OpenAPI document does not change, because the handler signature is untouched; `gear.unchanged` covers `/api/schema`, `test_api.py` covers the rest.

### 6. Route-table pin: see Pattern 3 above.

### 7. `bench/RESULTS.md` convention [VERIFIED: read lines 5549-5600, 6508-6611, 6683-6700]

- Append-only; one `## <Title> (Phase N)` section per phase, opening with `What this section holds: ...` (one paragraph naming the phase, that readings are appended per plan and never rewritten, and the investigation folder for whole logs).
- Subsections `### <what> (NN-MM)` per plan reading; a final `### Seen red once (Phase N)`: "Each deliberate break was run red once and reverted ..." then the table `| Plan | Test or step | Deliberate break | First failure line | Reverted |`, the first failure line copied from a kept log under `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/`, `Reverted` stating the `git checkout --` and a clean diff.
- Gate-delta readings follow the "The gate re-set (Phase 25)" habit: host line, `uptime` before and after, commit `git rev-parse --short HEAD`, the pytest result line.
- No test reads `RESULTS.md` [VERIFIED: grep over tests/*.py].
- Suggested heading: `## Scope, seam and gear-safety guard (Phase 30)` with `### The gate delta (30-NN)` and `### Seen red once (Phase 30)`. Rows to record: `gear.unchanged` x3 watched items (+ untracked file and missing-tag as extras), contracts 1-4 (each at least once), the route pin (`/api/foo`), the existence guard (rename a forbidden name), the 503 pin (revert the noun), the `verify.static` wiring dry-run pin.

## L46 and docs commit (REQ-scope-decision-logged)

- Entry format [VERIFIED: tail of `docs/architecture/decision_log.md` read]: `## L46 — <title> (amends L02 and L05; keeps L03, L04, L06, L08 and L44)`, `Date: 2026-10-23`, bold-lead paragraphs (**The decision**, **What it amends**, **What it leaves alone**, **The proof**, **Reversibility.**, then `Reason:`). Header of the log: "to change one, add a new entry that supersedes it and say which"; earlier entries are not edited (L02 text at lines 21-28 stays).
- Content per D-16 to D-18: product = "gear and spline generator"; L02 reads "one parameter model per part type, three front ends each"; L05 gains "a second frozen link contract: the shaft's field names and defaults"; shaft names and defaults may change by logged decision until Phase 33 publishes the first shaft link (no link exists before then); leaves L03, L04, L06, L08, the gear defaults and L44's 422 rule alone. ARCHITECTURE.md §F7/§risk also asks it to record that a stray `part=` on the gear page changes from ignored to refused (an L44-class invalid-link change; Phase 33 implements it; no fixture or README link carries one per the research's grep).
- No test reads `decision_log.md` [VERIFIED: grep over tests, scripts, Makefile found none].
- Same docs commit: `AGENTS.md` "What we're building" (CLAUDE.md is a symlink, `ls -la` read; no test reads either file); `.planning/ROADMAP.md` Phase 30 "Depends on" paragraph (lines 189-195: the "only phase of the milestone that edits gear-side files" claim and the stale "No `v0.6` tag exists" text) replaced with D-11's rule, and the Phase 32/33 text as needed. `README.md` untouched (D-19).
- Later-phase docs note (Phase 32, not here): `docs/CODING_VALUES.md:72` ("`model.py` is the only doorway to `cadquery`/`OCP`") and `docs/architecture/solid-model/strategy.md:12` become false when `shaft_model` imports the kernel.
- Order check command (run at phase close): `git log --diff-filter=A --format='%h %s' -- 'src/spur/shaft_*.py' src/spur/din5480.py src/spur/din5480_tables.py` must list only commits after `git log --format=%h -1 -- docs/architecture/decision_log.md` for the L46 commit.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Research ARCHITECTURE F3: "type widening in Phase 30" | `Part = GearParams` alias now, one-line union in Phase 31 | D-08 | No `ShaftParams` before Phase 31 |
| Research §6: contracts ride with the module-creating commit | Placeholders first, contracts in force before any shaft code | D-12 | Contracts precede all shaft code |
| ROADMAP: "only phase that edits gear-side files" | Later phases make additive edits, proved by `gear.unchanged` | D-11 | ROADMAP text amended |

**Deprecated/outdated:** the ROADMAP's "No `v0.6` tag exists" and its first-task stop-and-ask (CONTEXT: the tag exists and is pushed; do not plan it).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | On the GitHub Actions runner, persisted checkout credentials let `git fetch --depth=1 origin tag v0.6` succeed | Resolved Unknown 3 | `make verify` red in CI on the phase's first run; `ci.yml` cannot be edited, so the human decides (the check is designed to fail loudly, not skip) |
| A2 | The Linux CI venv's editable install also puts `PYTHONPATH` ahead of the repo `src` | Pitfall 2 | The shadow guard fails the run loudly (never a silent pass) |
| A3 | Replacing D-02's "temporary git worktree" with `git archive` is acceptable | Open Question 1 | Human prefers the literal worktree: use it with the hook-env strip and `try/finally` + `worktree prune` |
| A4 | A `Part` import cycle cannot form in Phase 31 (`parts -> shaft_params -> params`, `records -> parts`) | Contracts | Contract 2 and 4 would flag a cycle through `records`/`params` immediately |

## Open Questions

1. **Worktree (D-02 wording) vs `git archive`.**
   - What we know: D-02 names "a temporary `git worktree` of `v0.6` under the same venv", but also leaves "how the temp worktree is created and cleaned up" to discretion. A worktree run from the pre-commit hook corrupts the commit in progress (reproduced) and leaves `.git/worktrees/<id>` if killed; `git archive` is read-only, cost-equal, and needs no cleanup beyond a `TemporaryDirectory`.
   - What's unclear: whether the human reads D-02 as the tool or as the intent (the baseline read from the tag at run time, nothing committed).
   - Recommendation: `git archive` (intent preserved, zero repo state); ask in one line at plan time because it departs from the literal wording.

2. **Add `requirements.txt` to the watched paths?**
   - What we know: REQUIREMENTS.md says it stays byte-identical, but D-02/Success Criterion 2 name only `tests/regression/` and `ci.yml`.
   - Recommendation: do not add it (scope as locked). If wanted later it is a one-token edit to `WATCHED`.

3. **Pin the expected `v0.6` commit sha in the script?**
   - A force-moved tag would silently move the baseline. A constant `792b45c0...` guards it at the price of a second copy of the baseline.
   - Recommendation: skip; tags in this repo are pushed and annotated, and D-02 rejects second sources of truth. Surface only if the human wants it.

4. **Gate-delta baseline.** Recommendation in Resolved Unknown 4: record 236.23 s as baseline, 239.51 s as the same-host cross-check, state the load for the Phase 30 close reading.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | `gear.unchanged`, commit order check | yes | 2.56.0 | none (blocking) |
| GNU Make | targets | yes | 4.4.1 | none |
| `.venv` (Python 3.12.15) | everything | yes | 3.12.15 | `make venv` |
| import-linter / grimp | contracts | yes | 2.15 / 3.17 | none |
| `origin` remote reachable | tag fetch only when `v0.6` is absent locally | yes (`git ls-remote --tags origin` answered) | — | none by design (D-05: fail, never skip) |
| `v0.6` tag locally | `gear.unchanged` | yes | tag `b7f217f`, peels `792b45c` | the script's fetch |
| Docker | `make check` only | not needed | — | — |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 (`filterwarnings = ["error", ...]`, `--strict-markers`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (testpaths `tests`), coverage `fail_under = 96` |
| Quick run command | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_seam.py tests/test_gear_unchanged.py` |
| Per-commit command | `make verify.fast` (static steps incl. `gear.unchanged` + every test file but the five heavy ones; 947 tests, ~14.6 s) |
| Full suite command | `make verify` (1348 tests at v0.6, ~236-240 s) |
| Direct guards | `make lint-imports`, `make gear.unchanged`, `make no-fake-done` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-scope-decision-logged | L46 exists, names the scope, amends L02/L05; precedes the first shaft-module commit | doc + git-order check | `grep -n '^## L46 ' docs/architecture/decision_log.md` and the order-check command above | no, planned (verification step, not a permanent test: commit order is history) |
| REQ-gear-unchanged-proof | Green on the tree; red on each watched item; fetch failure fails with cause; never compares a tree with itself | unit (script on a scratch git repo with a fake tag, `schema_of` injected) + target | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_gear_unchanged.py` ; `make gear.unchanged` | no, Wave 0 |
| REQ-gear-unchanged-proof | `gear.unchanged` is in both `verify` and `verify.fast` | dry-run pin | new test in `tests/test_hooks.py` reusing `_dry_run`: `"scripts.gear_unchanged"` in `make -n verify` and `make -n verify.fast` | file exists, test is Wave 0 |
| REQ-gear-unchanged-proof | The seam edits leave every gear request unchanged | existing | `make gear.unchanged` after each seam commit; `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py tests/regression` | yes |
| REQ-shaft-routes-separate | Import walls 1-4 hold | contract | `make lint-imports` | contracts planned in `pyproject.toml` |
| REQ-shaft-routes-separate | Contract-named modules exist (forbidden typo is silent) | unit | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_seam.py::test_every_module_a_contract_names_exists` | no, Wave 0 |
| REQ-shaft-routes-separate | Belt: shaft-maths sources hold no kernel/solid/logger import line | unit (regex) | `... tests/test_seam.py -k shaft_maths_sources` | no, Wave 0 |
| REQ-shaft-routes-separate | Route set equals the v0.6 set plus `/api/shaft/*` only; gear query keys unchanged | unit | `... tests/test_seam.py -k route` | no, Wave 0 |
| D-07 `_serve_model` | pure move: `test_api.py` passes without a test edit | existing | `.venv/bin/python -m pytest --no-cov -n0 -q tests/test_api.py` | yes |
| D-09 503 wording | part-neutral message, status, `retry-after`, `type` unchanged | unit | `... tests/test_api.py -k saturated` (new test added beside it) | no, Wave 0 |
| REQ-gate-cost-recorded | `make verify` result line + load recorded vs baseline | measurement | `make verify`; entry in `bench/RESULTS.md` | n/a |

### Sampling Rate
- **Per task commit:** `make verify.fast` (it now carries `gear.unchanged` and the contracts).
- **Per seam commit:** also `make gear.unchanged` explicitly and `tests/test_api.py` + `tests/regression`.
- **Per wave merge / phase gate:** full `make verify` green, result line recorded, `make gear.unchanged` green, then `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `scripts/gear_unchanged.py` and its Makefile wiring (`.PHONY`, `gear.unchanged: $(STAMP)`, `verify.static` prerequisite, help text)
- [ ] `tests/test_gear_unchanged.py` (scratch repo; red/green per watched item, missing-tag path, shadow-guard path)
- [ ] `tests/test_seam.py` (route pin, existence guard, regex belt)
- [ ] `tests/test_hooks.py` addition: dry-run pin that both gates run the check
- [ ] `tests/test_api.py` addition: 503 text pin
- Framework install: none needed.

## Security Domain

`security_enforcement` is absent from `.planning/config.json` (read this session), so treated as enabled. The phase ships no network input path; the surface is dev tooling.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | limited | The script's inputs are a constant tag name and repo paths; no user string reaches `subprocess` (list form, no `shell=True`). Extract the archive with `tarfile.extractall(filter="data")` (3.12) so a hostile member cannot escape the temp dir |
| V6 Cryptography | no | — |
| V14 Configuration | yes | `git fetch` only to `origin` and only for tag `v0.6`; no credentials are read or printed by the script |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Tampered baseline (moved tag) | Tampering | Annotated pushed tag; optional pinned sha (Open Question 3) |
| Silent self-comparison (shadowed import) | Repudiation of the guard | `spur.__file__` assertion + `PYTHONPATH` + `python -P` |
| Archive path traversal | Tampering | `tarfile` `filter="data"`, temp dir, own repo's tree only |
| Hook corruption by git mutation | Tampering | read-only git commands only (Pitfall 1) |
| Stray secret in logs from `git fetch` stderr | Information disclosure | print `git`'s stderr only on failure; it names the remote, not credentials [ASSUMED] |

## Sources

### Primary (HIGH confidence, all run or read this session)
- Scratch experiments (nothing committed to the repo): import-linter 2.15 contract runs; coverage report on a docstring-only module; `gear.unchanged` prototype with green/red scenarios in a scratch clone; `git worktree add` timing; shallow-clone `git fetch --depth=1 origin tag v0.6`; pre-commit hook environment dump and the worktree-in-hook reproduction; ruff and mypy on a scratch `parts.py`.
- `make verify.fast` and `make verify` run on `HEAD 760ac4e` (code equal to `v0.6`).
- Files read: `.planning/phases/30-.../30-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/research/ARCHITECTURE.md` (F3, §6), `.planning/ROADMAP.md` (Phase 30), `Makefile`, `pyproject.toml:140-224` and the ruff/mypy/pytest tables, `src/spur/{app,pool,records,model,cli,__init__}.py` (cited ranges), `tests/test_hooks.py`, `tests/test_records.py`, `tests/test_api.py`, `.github/workflows/ci.yml`, `bench/RESULTS.md` (section headers and Phase 25/27/28 sections), `docs/architecture/decision_log.md` (header, L02, L45), `docs/CODING_VALUES.md` "Coupling", `AGENTS.md`/`CLAUDE.md`.

### Secondary (MEDIUM confidence)
- Recorded v0.6 baseline `1348 passed in 236.23s`: `.planning/PROJECT.md`, `RETROSPECTIVE.md`, `milestones/v0.6-MILESTONE-AUDIT.md` (grep match; figure not re-read in context beyond the CONTEXT.md quote).

### Tertiary (LOW confidence)
- CI runner behaviour for the tag fetch and for the Linux editable layout (A1, A2): not testable from this host.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, no new packages; versions read from the venv.
- Architecture: HIGH, prototype ran green and red, contracts ran green and red.
- Pitfalls: HIGH for the five reproduced ones (hook index, shadowing, silent forbidden typo, Phase 32 break, `ignore_imports` strictness); MEDIUM for CI-only behaviour.

**Research date:** 2026-10-23
**Valid until:** 2026-11-22 (stable tooling; re-check import-linter behaviour if it is upgraded, and the CI fetch after the phase's first CI run)
