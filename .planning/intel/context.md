# Context

Running notes from the 6 documents classified DOC, keyed by topic, appended with source
attribution. These are not requirements or constraints — they are background, process,
and (in two cases) historical records superseded by the live decisions/SPECs. See
`INGEST-CONFLICTS.md` (INFO) for the historical-vs-live caveat on the review and plan.

## Product summary
- source: README.md
- Parametric involute spur gear generator. Set parameters via a web page, get a live 3D
  preview and the numbers you'd measure on a real gear, download as STL (slicing) or STEP
  (CAD). Same thing available as an HTTP API and a CLI. Built on CadQuery (OpenCascade),
  FastAPI and three.js.
- Feature list (verbatim bullets): "Involute flanks from module, tooth count, pressure
  angle and profile shift"; "Backlash, root fillets, D-flat or round bore with print
  clearance and chamfer"; "Annular face recesses (one or both sides) with filleted
  floors"; "Measurement aids: calipers across tips (corrected for odd tooth counts), span
  over k teeth (Wildhaber), centre distance to a mating gear"; "Shareable links: every
  parameter lives in the URL".
- Deployment: Docker/compose (`http://localhost:8000`), remote host over SSH, or
  without Docker via `pip install -e '.[dev]'` + `spur serve` (Python 3.10+ locally, but
  `cadquery-ocp` wheels only exist for 3.10–3.12).
- Full parameter table with defaults and units is in the README's "Parameters" section
  (teeth=19, module=1.75, pressure_angle=25, profile_shift=0, backlash=0.1,
  root_fillet=0.5, face_width=7.5, bore_d=9, bore_flat=8, bore_clearance=0.15,
  bore_chamfer=0.4, recess_sides=both, recess_depth=2, recess_width=6,
  recess_inner_d=0, recess_fillet=0.5) — cross-referenced into `requirements.md` and
  `constraints.md` rather than duplicated here in full.
- "Matching an existing gear" walkthrough: count teeth and measure across tips (odd
  tooth count reads short); estimate module as tip diameter / (teeth + 2) rounded to a
  standard value; confirm with span over k teeth; check centre distance if the mate is at
  hand.

## Development workflow
- source: docs/HOW_TO_DEVELOP.md
- Human-facing guide (in Russian) to the AI-agent collaboration cycle: обсуждение (discuss)
  → план (plan) → проверка плана (review the plan) → выполнение в worktree (execute in an
  isolated worktree) → ревью другим CLI (cross-CLI code review — Claude's work is reviewed
  by Codex and vice versa) → влить (merge via `make worktree.land`) → приёмка (acceptance
  as a user).
- Repo guarantees before any of that: `make verify` (ruff, mypy --strict, import-boundary
  contracts, unfinished-work scan, pytest, ~11s warm) runs in the developer's shell,
  pre-commit hook, and CI; `make check` adds the image build, in-container smoke test, and
  the vendored three.js byte check (needs Docker).
- Named project-specific trap: a worktree must not share the main checkout's `.venv` —
  its editable install resolves `import spur` back to the main tree's `src/`, so tests
  would silently run against unmodified code. Use `make venv` inside the worktree or
  `make test-image`.
- Plan-review checklist specific to this project: does the change alter a part the user
  did not ask to change (L05, defaults frozen)? Does it introduce a number that could be
  wrong (L08, prefer a warning to a plausible number)? Is a performance/memory claim
  backed by a measurement and its workload?

## Coding values and standards
- source: docs/CODING_VALUES.md
- Full reference behind `AGENTS.md`'s short version. Vision: "Code reads like the
  architecture says it works." Comments must carry the measurement or constraint that
  forced the choice ("1578 MiB resident without this, 360 MiB with it.") — a comment that
  restates the code is worse than none.
- Explicitly absent by design: no database, no queue, no cache server, no external
  service client, no migrations, no authentication — do not add any of these sections
  back speculatively.
- Code values restate L08 ("a wrong number is worse than no number"), L05 ("never change
  the part the user did not ask to change"), and add: measure before you claim; explicit
  types at every boundary (vendor types stop at their boundary); self-documenting,
  domain-vocabulary names; one operation per routine; simplest thing that works; limits
  live in code (env var + check), not only in infra.
- Coupling rules restated: `calc.py`/`params.py` never import the CAD kernel; `cli.py`
  never imports `app`/`fastapi`/`starlette`; `model.py` is the only doorway to
  `cadquery`/`OCP` — all enforced by import-linter contracts in `pyproject.toml`.
- Validation: `GearParams` is the one inbound boundary for all three front ends; trust
  the types after that boundary; do not re-validate a `GearParams` downstream.
- Testing tiers: unit (`calc.py`, pure/fast/exhaustive, test names read as requirements),
  integration (`model.py` against the real kernel, no mocking OpenCascade), contract
  (`app.py` via `TestClient`, including error shapes the UI parses). "The README's own
  commands are tests" — `tests/test_cli.py` exists because a documented example did not
  run.
- Tech debt process: found during normal work → `docs/tech_debt/active/` item (location,
  smell, fix, trigger), not a silent fix in an unrelated change.

## Requirements taxonomy (intended, not yet populated)
- source: docs/requirements/README.md
- States the intended durable requirements structure for this project, once something
  exists to put there: `functional.md` (checkable product statements), `nfr.md`
  (performance/memory/portability/reproducibility budgets with the number and how it was
  measured), `errors.md` (the error contract — which conditions refuse, which cap-and-warn,
  what a client can rely on in a `4xx`/`5xx` body), `security.md` (the threat model
  actually defended against, and what is explicitly out of scope).
- Explicit statement: "Nothing is written here yet, and nothing should be invented to fill
  it." None of the four named files exist in `docs/requirements/`.
- Points to where each requirement kind already lives today: the error contract in
  `decision_log.md` (L03, L08) and exercised in `tests/test_calc.py`/`tests/test_api.py`;
  memory/reproducibility budgets in L07 and L12 with measurements in
  `docs/plan-2026-09-21.md`; the security posture (no auth, localhost binding, hardened
  container) in the README and `docs/tech_debt/active/2026-09-21-no-authentication.md`.
- This taxonomy is a pointer for `gsd-roadmapper` when it authors `REQUIREMENTS.md`, not
  a source of requirement content itself.

## Historical audit — Review 2026-09-21 (superseded; see INGEST-CONFLICTS.md INFO)
- source: docs/review-2026-09-21.md
- Audit of `spur` at commit `9345338` (the initial commit), every claim measured with a
  reproduction command given per finding. Verified-working checks: Docker builds for
  amd64/arm64, container health/shutdown timings, all served routes and media types, gzip
  ratios, error-path shapes, the in-image test suite (34/34), CLI, `SPUR_ROOT_PATH`
  behavior, and a byte-identical vendored three.js bundle.
- Eight findings, F1–F8: F1 (high) `centre_distance` Newton solver returns confidently
  wrong — sometimes negative — numbers for 138 parameter sets, all `200 OK`; F2 (high)
  caches bounded by entry count not bytes, anon RSS unbounded (~3.0 GiB after 35 large
  gears); F3 (high) absolute-mm bore/recess defaults make 17% of the (module 0.5–3.0,
  teeth 6–120) grid infeasible, including the README's own CLI example; F4 (medium) no
  admission control, a build stalls the event loop and health probes time out under
  concurrency; F5 (medium) only 6 of 56 installed packages pinned in `requirements.txt`;
  F6 (low) `root_thickness` measured at the wrong radius for `rb > rf` gears (including
  the project's own default, z=19); F7 (low) ~440 MB of the image is never imported;
  F8 (low) structure/process notes (mixed altitudes in `_build()`, undocumented `_gear()`
  rationale, zero CLI tests, no CI, undocumented sub-path trailing-slash requirement).
- This document itself carries no resolution status — it must be paired with
  `docs/plan-2026-09-21.md` to know what was fixed.

## Remediation plan and outcome — 2026-09-21 (historical, completed)
- source: docs/plan-2026-09-21.md
- Seven-step remediation plan against the review's F1–F8, plus an "Outcome" section with
  measured before/after numbers on the same machine. All seven steps are recorded as
  landed: F1 bisection solver + `None` on no-solution (138 → 0 wrong values); F6
  `root_thickness` measured at `rf` (z=19: 4.9125+1.6085 → 4.7744, matching root-circle
  pitch exactly); F3 recess capped instead of refused (feasible grid share 83% → 94%,
  README's own CLI example now runs with a warning); F2 bounded-by-bytes export cache +
  solid cache dropped to 4 entries + `malloc_trim(0)` (anon RSS after 35 large gears:
  ~3.0 GiB, still climbing → 358 MiB, flat from gear 10); F4 bounded admission queue +
  `503`/`Retry-After` (health-probe timeouts under 10 concurrent builds: 3 of 25 → 0 of
  20); F5 pinned closure (6 of 56 → 31 of 31); F7 image trimmed (2.15/2.07 GB →
  1.70/1.61 GB); F8 structure/docs/CI cleanup, CLI tests added (34 → 50 tests total).
- Two results explicitly flagged as contradicting the plan's own prior reasoning: cache
  sizing alone was not the fix for F2 (arena release via `malloc_trim(0)` did the actual
  work); `mem_limit: 1g` was too tight and failed ~5% of requests under a sweep even
  though steady state was ~740 MB for two workers, so the compose file uses `2g`.
- Deliberately not done (recorded, not silently dropped): moving CAD work to a process
  pool (root cause of F4 remains — a single large build still stalls the event loop for a
  few seconds); cancelling server-side work on browser abort (`app.js:174`);
  `.github/workflows/ci.yml` is explicitly flagged **unverified** — GitHub Actions could
  not be run during this work, only each step was run by hand.
