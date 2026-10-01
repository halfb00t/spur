# Milestones

## v0.2 Fit to Shaft (Shipped: 2026-10-01)

**Delivered:** A generated gear mounts on a real shaft and prints light — hex and keyway
bores, a tooth-tip chamfer, and one body-cutout pattern per part (spokes, holes or a
honeycomb), every one additive on the shipped pipeline with the pre-v0.2 part byte-unchanged,
every cut with a measured build time inside `SPUR_BUILD_TIMEOUT`, and all three interfaces in
parity from the one `GearParams` model.

**Phases completed:** 7–12 (34 plans, 82 tasks).

**Key accomplishments:**
- Foundation (Phase 7): the bore-rim and groove-floor selectors raise instead of silently
  selecting nothing; the 44-record `tests/regression/pre_v0_2.json` fixture replays every
  pre-v0.2 parameter set for identical `DerivedDimensions` and solid and stayed
  byte-unchanged through all six phases (L26).
- Hex and keyway bores (Phases 8–9): `bore_hex` replaces the round profile, warned not
  refused, with two measured root-circle rules at the chamfered corner (L27); the keyway is
  a slot after the chamfer with an explicit as-cut-wall depth datum, six refusals before any
  CAD, the recess yielding rather than refusing, and the round bore's own chamfer-reach gap
  closed at the kernel's measured contact (L28).
- Tooth-tip chamfer (Phase 10): a 3-D edge break capped at the smallest of tip land,
  addendum and a kernel boundary bisected to ~2 µm; help names no size because the
  research-era figure has no source (L29).
- Body cutouts (Phase 11): spokes with analytic tangent-arc corners, holes, and a
  whole-cell honeycomb capped at a measured `HEX_CELL_CAP = 120`; one pattern per part, every
  wall rule through `_under_min_wall` and pinned one step either side on the kernel; D-18's
  gate fired and set `hole_count`/`spoke_count` `le` 60/40 (L30).
- Composition pass (Phase 12): the 18-row composed sweep measured across four runs, D-02
  superseded for one gate on the human's word, `spoke_count` `le` 40 → 32 from a probe and
  every composed row inside 30 s (heaviest 29.42 s); 96 + 138 calc rows and 15 kernel rows
  prove the matrix; a model-driven field walk, a byte-identical composed document and 23
  identically routed refusals prove three-interface parity; L19 re-applied keeps
  `_GZIP_LEVEL = 1`; the phase's +28.28 s gate cost accepted against D-10's 30 s line (L31).
- Records kept honest: two cross-CLI review passes on Phase 12 (Codex lane) found and fixed
  14 findings — a regression test that could not fail, three over-claims in RESULTS.md and
  L31, the CLI's real 2/1/1 exit contract — before the close.

**Stats:**
- 185 files changed (+48,807 / −164) from the v0.1 tag to the last squash; 28 of them
  code, tests or bench (+11,623 / −62)
- 3,131 lines of package Python, 7,889 of tests, 1,881 of bench, 370 of hand-written UI JS;
  907 tests in `make verify` (191 at v0.1)
- 6 phases, 34 plans, 82 tasks; 6 PRs (#7–#13) through `make pr.land`
- 6 days from the milestone start commit (2026-09-26) to the last squash (2026-10-01)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins)
- ~11 h 45 min of executor time where measured (Phases 7–10, STATE.md per-plan table;
  Phases 11–12 not timed per plan)

**Git range:** `b3ca789` (Milestone v0.2: Fit to Shaft — start (#7)) → `fd29c2c` (Phase 12:
Composition Pass (#13))

**Closeout:** `override_closeout` (human decision, 2026-10-01). Phases 7–11 read `stale` in
`init.manager` because Phase 12 legitimately changed files their reports fingerprint
(`src/spur/params.py`, the five test files, `bench/RESULTS.md`, the decision log); Phase 12's
own matrices and the byte-unchanged fixture re-exercise those phases on the final code, and
Phase 12 itself was re-verified on 2026-10-01 after its review fixes (`passed`, fresh digest).
Known verification overrides: 0 newly acknowledged, 0 carried forward (`audit-open` clear);
human decisions on record: D-06 (fixture cost), D-18 (`le` 60/40), D-02 superseded for one
gate, D-03 (`le` 32), D-10 (+28.28 s accepted).

**Audit:** `milestones/v0.2-MILESTONE-AUDIT.md` — status `tech_debt`; requirements 20/20,
phases 6/6, integration 9/9, flows 5/5, security 6/6 with 0 open threats; Nyquist partial
(Phases 7 and 8 predate the capability); 10 active debt items (4 `must`), each with a trigger.

**What's next:** v0.3 candidates carried from the v0.1 kickoff list and the v0.2 scoping
decision — a gear family (helical first; internal/ring and rack later, one type per phase)
or precision (trochoidal root fillet, the waived latency bar). `/gsd-new-milestone` decides.

---

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
