# Milestones

## v0.1 Hardening (Shipped: 2026-09-25)

**Delivered:** The generator hardened for real load and honest contracts — CAD builds off
the event loop with a measured memory ceiling, structured logging, a typed
derived-dimensions contract with `disallow_any_explicit` on, CI as the structural merge
gate on Python 3.12 only, and the five debt items those phases surfaced retired.

**Phases completed:** 2–6 (21 plans, 59 tasks). Phase 1 is the pre-GSD v0 baseline,
recorded for context, not re-verified.

**Key accomplishments:**
- CAD builds run in `BuildPool` worker processes off the serving event loop, routed by
  parameter-hash affinity; `/api/health` p95 under one build within 2× idle on every
  recorded run; per-build timeout 30 s from the worst measured build, three failure-mode
  status codes, pool state on `/api/health`; `compose.yaml` `mem_limit: 4g` from an
  N=1/2/4 sweep of the real topology, not a formula (L17–L19 supersede L06/L07).
- Structured JSON logging (`records.py`) configured idempotently at both composition
  points; `build.started`/`build.failed`/`export.served`/`queue.refused`/`worker.replaced`
  proven by tests; `calc.py` provably log-free by an import-linter contract (L20).
- `derive()` returns a frozen 19-field `DerivedDimensions`; `HealthReport`/`PoolState`;
  mypy `disallow_any_explicit` on globally with no suppressions; `spur info --mate-teeth`
  refuses what the API refuses (L21 supersedes L14).
- CI is the merge gate: a repo-owned `commit-msg` hook refuses Actions skip tokens,
  `make pr.land PR=N` is the only path to `main`, a ruleset on `main` requires
  `test (3.12)`/`vendor-bundle`/`image` green on an up-to-date head plus a pull request;
  Python 3.12 only (L22, L23).
- Five debt records retired in Phase 6: the cached solid never carries a mesh
  (`shape.copy()`, L24); the hook reads git's whole buffer; `pr.land` refuses
  `conclusion != success`, resolves `jobs.<id>.name` in the drift test, and reports only
  what it observed after the merge (L25 amends L22).
- Tech-debt ledger 11 → 6 active items (1 `must`, 5 `nice`), 10 resolved during the
  milestone, every remaining item with a named trigger.

**Stats:**
- 169 files changed (+38,660 / −508) from the roadmap commit to the last squash; 64 of
  them outside `.planning/` (+7,524 / −381)
- 6,410 lines of Python (`src`, `tests`, `scripts`, `bench`, `docker`); 361 lines of
  hand-written UI JS; 191 tests in `make verify`
- 5 phases, 21 plans, 59 tasks; 64 commits on `main`; Phase 2 landed by direct push,
  Phases 3–6 as PRs #2–#5 (Phases 5–6 through `make pr.land`)
- 4 days from roadmap (2026-09-21) to ship (2026-09-25)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins)
- ~8 h 45 min of executor time across the 21 plans (STATE.md per-plan table)

**Git range:** `f82a4d1` (docs: create milestone v0.1 roadmap) → `1173d21` (Phase 6:
Address tech debt: merge gate + solid cache (#5))

**Closeout:** `override_closeout` (human decision, 2026-09-25). Phase 1 has no phase
directory (pre-GSD baseline; `verification: missing` by construction). Phases 2–6 read
`stale` in `init.manager` because each VERIFICATION.md fingerprints `.planning/STATE.md`,
which GSD's own phase-complete step rewrites; for Phase 6 the declared `covered_digest`
recomputes exactly on `110b827` and only STATE.md changed afterwards (`4c39df8`,
`b35d7e9`). No source, test, plan or summary changed after any report. Known verification
overrides: 0 newly acknowledged, 0 carried forward (`audit-open` clear); 1 human waiver on
record — the Phase 2 ten-concurrent latency bar (WINDOWS.md item 1, L18, `must` debt).

**Audit:** `milestones/v0.1-MILESTONE-AUDIT.md` — status `tech_debt`; requirements 5/5,
phases 5/5, integration 14/14, flows 6/6, security 0 open; Nyquist partial (Phases 4 and 5
still `draft` — `/gsd-validate-phase 4`, `5` when convenient).

**Evidence:** PR #5 squash `1173d21`, run 36145323487 green on all three required jobs;
Phase 5 squash `b72b0e1`, run 36122394253.

**What's next:** Not yet defined — `/gsd-new-milestone`. Candidates gathered at v0.1
kickoff (`milestones/v0.1-REQUIREMENTS.md`, "Future Requirements"): helical, internal and
rack gears (bevel needs a product-scope decision first), tooth chamfers, keyway/hex bores,
spoke/hex body cutouts, the trochoidal root fillet (would supersede L10), a browser-driven
viewer test.

---
