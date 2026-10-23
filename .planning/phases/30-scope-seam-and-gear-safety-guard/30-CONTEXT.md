# Phase 30: Scope, Seam and Gear-Safety Guard - Context

**Gathered:** 2026-10-23
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things:

- **L46.** A decision-log entry that widens the product to a gear and spline generator.
- **The seam.** Done ahead of time so that later phases add shaft code instead of editing gear
  code: `_serve_model`, `parts.Part`, and part-neutral 503 text.
- **Import-linter contracts and a route-table pin.** They wall the shaft off from the gear, and
  are in force before any shaft code exists.
- **`make gear.unchanged`.** One check that proves no existing gear link builds a different
  part.

Out of scope:

- No shaft maths, no `ShaftParams`, and no route that answers a shaft.
- No new `GearParams` field.
- `make fixture.regen` and `make golden.regen` are not run.
- `requirements.txt`, `tests/regression/` and `.github/workflows/ci.yml` stay byte-identical to
  `v0.6`.

**Fact found at discuss-phase:** the `v0.6` tag exists. It is annotated, pushed to origin, and
peels to `792b45c` (`git rev-parse v0.6^{commit}`; `git ls-remote --tags origin` lists
`refs/tags/v0.6^{}` → `792b45c…`). The roadmap's first-task stop-and-ask ("the human tags
`792b45c` as `v0.6`") is already satisfied. Do not plan it as a task; pin `v0.6` as the baseline.

</domain>

<decisions>
## Implementation Decisions

### Gear-safety check (`make gear.unchanged`)
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

### Seam work
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

### Import contracts and module layout
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

### L46 — scope decision
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 30: Scope, Seam and Gear-Safety Guard" — goal, success
  criteria 1–4, boundaries. Note D-11's amendment and the stale tag task (see Phase Boundary).
- `.planning/REQUIREMENTS.md` — the three requirements this phase delivers:
  `REQ-scope-decision-logged`, `REQ-gear-unchanged-proof` and `REQ-shaft-routes-separate`.
  `REQ-gate-cost-recorded` is cross-cutting.

### Research
- `.planning/research/SUMMARY.md` — milestone synthesis; Phase 1 = this phase.
- `.planning/research/ARCHITECTURE.md` — the following parts:
  - F1: path-prefix routes, unknown query keys ignored.
  - F3: the `_serve_model` extraction.
  - F4: caches and pool key by class.
  - §"files touched": `pool`/`records`/`app` line refs.
  - §6: the import contracts, verbatim source for D-14.
  - "Rejected" list.
- `.planning/research/PITFALLS.md` — gear-regression pitfall (#4): shared names, stray-key
  behaviour, WR-02.

### Locked decisions
- `docs/architecture/decision_log.md` — the following entries:
  - L02 and L05: amended by L46.
  - L03, L04, L06 and L08.
  - L36: the commit slice / `verify.fast`.
  - L43: the 300 s gate bar.
  - L44: the gear link's 422 rule, which must keep holding.
  - L45: the latest entry. L46 is the next free id.

### Code and config
- `pyproject.toml:166-223` — the existing import-linter contracts. The new ones go after
  `:223`.
- `Makefile:114-124` — `verify`, `verify.fast`, `lint-imports`. `gear.unchanged` hooks in here.
- `.github/workflows/ci.yml` — must stay byte-identical. CI runs `make verify PYTHON=python`
  (`:46`) from a shallow checkout (D-05).
- `src/spur/app.py` — the following lines:
  - `:117` `BuildBackend`
  - `:232-249` `InfoQuery`/`ModelQuery`/`_gear`
  - `:263` `_build_slot`
  - `:285` the 503 text
  - `:329-387` the four `/api/` routes
  - `model()` body: the move source
- `src/spur/pool.py`, `src/spur/records.py` and `src/spur/model.py` — `GearParams` entry-point
  annotations widened to `Part` (D-08).
- `tests/test_api.py` — the move's proof suite. The `app.js` pins at `:176-180` and
  `:314-340` are untouched here.
- `tests/test_records.py:60` (record key set, no `part` key) and `:246` (the regex-belt pattern
  for contracts).
- `bench/RESULTS.md` — where the reds and the gate delta are recorded.
- `AGENTS.md` — "What we're building" (D-19).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` is the file half of
  `gear.unchanged` as it stands. It is empty today.
- FastAPI `TestClient(app).get("/api/schema").content` gives the byte-level schema read for both
  trees. Run it from each tree's `src` under the same venv.
- The existing import-linter contract shapes (`pyproject.toml:170-223`), and the
  contract-plus-regex-test pairing (`tests/test_records.py:246`).

### Established Patterns
- Each `make` target carries a `## description` comment; `make` alone lists them.
- Dotted target names: `fixture.regen`, `golden.regen`, `bench.memory`.
- `bench/RESULTS.md` sections are appended per plan and never rewritten. Each section opens with
  "What this section holds: …".
- Contracts carry *why* comments with the measured or decided constraint. Match that.
- A guard counts only after it has been seen red once against a deliberate violation, with the
  red recorded (CODING_VALUES "Coupling"; roadmap boundaries).
- `pool._warm` imports kernel modules by `importlib` string, which import-linter does not see
  (`pool.py:41-50`). Phase 32 relies on this; this phase does not.

### Integration Points
- `make verify` → `gear.unchanged` (D-04).
- `app.model()` → `_serve_model` (D-07); Phase 33's shaft routes are its second caller.
- `parts.Part` is imported by `pool`, `records`, `app` and `model` (D-08); Phase 31 widens it.
- The new contracts in `pyproject.toml` name the D-13 placeholder modules.

</code_context>

<specifics>
## Specific Ideas

- The human picked the recommended option on every question. The pattern: the stricter guard
  over the cheaper one, and doing gear-side work now so later phases stay additive.
- `gear.unchanged` must never turn a missing baseline into a pass (D-05). The human rejected the
  "skip with notice" option as a silent pass.

</specifics>

<deferred>
## Deferred Ideas

- The `README.md` scope wording moves to Phase 33 (D-19).
- The `model._build` shaft dispatch and the `pool._warm` shaft import move to Phase 32 (D-10,
  D-11).
- The `ShaftParams` frozen/hashable/hash-inequality tests move to Phase 31 (D-14).

</deferred>

---

*Phase: 30-scope-seam-and-gear-safety-guard*
*Context gathered: 2026-10-23*
