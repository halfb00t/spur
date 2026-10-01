# Phase 7: Foundation — Generalized Edge Selection + Regression Fixture - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-26
**Phase:** 7-Foundation — Generalized Edge Selection + Regression Fixture
**Areas discussed:** Fixture storage & regeneration, Corpus & make verify cost, Tolerances & topology invariants, Selector guard contract

---

## Process (before the areas)

| Option | Description | Selected |
|--------|-------------|----------|
| Cut `gsd/phase-07-foundation…` from `origin/main` now | STATE.md's next step; L22/L25 phase-branch process; non-destructive | ✓ |
| Stay on `gsd/milestone-v0.2-start` | CONTEXT.md would land on the already-merged PR #7 branch | |
| Write files, don't commit | Skip git_commit / STATE.md steps | |

**User's choice:** Cut the phase branch. Done at `b3ca789` (PR #7's squash commit).

---

## Fixture storage & regeneration

### Where do the captured numbers live?

| Option | Description | Selected |
|--------|-------------|----------|
| Checked-in JSON data file | One record per parameter set; diffable, regenerable, keeps the test small; new pattern for the repo | ✓ |
| Python literals in the test module | `test_default_dimensions` scaled up: ~1000 hand-aligned lines under L16 | |
| Generated Python module | Machine-written source under mypy `--strict` | |

**User's choice:** Checked-in JSON data file.

### How is the JSON regenerated?

| Option | Description | Selected |
|--------|-------------|----------|
| `make` target + script | Reuses the repo command surface; the script is also the first-time capture | ✓ |
| pytest option / env flag | One code path, but a test that rewrites its own oracle | |
| No tool — captured once by hand | Smallest surface; the first OCCT bump becomes a chore | |

**User's choice:** `make` target + script.

### When is a regeneration legitimate during v0.2?

| Option | Description | Selected |
|--------|-------------|----------|
| Own commit, reason stated, never in a feature commit | Pin bump (L12) or a contract change with a new `Lxx`; a red fixture in Phases 8–12 is a bug | ✓ |
| Frozen for the whole milestone | Strictest; a routine pin refresh would block | |
| Regenerate whenever red | The oracle becomes a mirror of HEAD — listed to be rejected | |

**User's choice:** Own commit, reason stated.

### What does one record store?

| Option | Description | Selected |
|--------|-------------|----------|
| Only the fields the source set, plus a provenance header | A record is a link that omits fields; header carries sha, kernel versions, date | ✓ |
| Fully expanded params | A drifted default would rebuild the same part unnoticed | |
| Source-set fields, no header | Kernel version lives only in git history | |

**User's choice:** Source-set fields + provenance header.

---

## Corpus & make verify cost

### How is "every existing test's parameter set" enumerated?

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-listed corpus module with source tags | Closed pre-v0.2 set; deduped by `GearParams` equality; imported by script and test | ✓ |
| Harvest by instrumenting `GearParams` | Drift-proof but hidden, order-dependent, captures throwaway instances | |
| Import the source tests' parametrize lists | Oracle coupled to test-file internals | |

**User's choice:** Hand-listed corpus module with source tags.

### How much CAD build time may the fixture add to `make verify` (32 s today)?

| Option | Description | Selected |
|--------|-------------|----------|
| Build every set; measure and record the cost | > ~15 s → planner returns with a trim proposal, never a silent subset | ✓ |
| derive() all, build() a curated subset | Bounded, but "every set" becomes "a representative subset" | |
| Build all, build-side in CI only | A marker splits what `make verify` means (L13) | |

**User's choice:** Build every set; measure and record.

### Record derive(p, mate_teeth) for sets with a mate?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — mate variants are their own records | `mate_teeth` is a shareable-link field; cannot-mesh cases pinned; solid shared | ✓ |
| No — always derive(p) without a mate | Mate fields always null in the fixture | |

**User's choice:** Yes.

### Which other parameter sources join the corpus?

| Option | Description | Selected |
|--------|-------------|----------|
| tests/ + README only | Roadmap wording; smoke.py is a container check; bench corpus is minutes of builds | ✓ |
| Also docker/smoke.py's sets | Pins what CI's image job exercises | |
| Also bench/corpus.py, derive() side only | Two kinds of record | |

**User's choice:** tests/ + README only.

### Are machine-generated grids "an existing test's parameter set"? (raised after the probe)

| Option | Description | Selected |
|--------|-------------|----------|
| No — hand-written sets only | The solver grid (~100 sets, ~20 at 200 teeth × 2.3 s) has its own oracle | ✓ |
| Yes, derive() records only for the grid | Wider derive coverage; two kinds of record | |
| Yes, full records including build() | ~+60 s; the 15 s rule fires immediately | |

**User's choice:** Hand-written sets only.

---

## Tolerances & topology invariants

### Volume tolerance

| Option | Description | Selected |
|--------|-------------|----------|
| `rel=1e-6` | Volume() deterministic on the pinned kernel (diff 0.0 over 3 builds); catches the 1.05e-3 chamfer with margin | ✓ |
| `rel=1e-3` | The existing ring test's tolerance; would miss a vanished chamfer — rejected on the record | |
| Exact float equality | Brittle without gain | |

**User's choice:** `rel=1e-6`.

### Pin B-rep topology counts (faces, edges) exactly?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — face and edge counts, exact | Sharpest cheap tripwire for a lost chamfer/fillet; a kernel re-split is a stated-reason regen | ✓ |
| No — volume and bbox only | Roadmap's literal wording | |

**User's choice:** Yes, exact.

### How are the 19 DerivedDimensions fields compared?

| Option | Description | Selected |
|--------|-------------|----------|
| Exact on all 19, warnings text included | Python-computed, rounded at construction; warning sentences are the product (L15) | ✓ |
| Exact numbers, warnings by count | Wording free to change | |
| approx on floats | Looser than r3() needs | |

**User's choice:** Exact on all 19 including warnings.

### Bounding box representation and failure reporting

| Option | Description | Selected |
|--------|-------------|----------|
| Six corner values, `abs=1e-6`; one case per record, id = source tag | Catches a shifted part; a red names its source | ✓ |
| Three extents, one looping test | Misses a translation; first mismatch hides the rest | |
| Six corners, `rel=1e-6` | Degenerates to exact at a 0.0 coordinate | |

**User's choice:** Six corners abs 1e-6, one parametrized case per record.

---

## Selector guard contract

### What is raised on zero edges while the feature is on?

| Option | Description | Selected |
|--------|-------------|----------|
| `BuildError` with a message naming the selector | Existing routing (422 / exit 2); tests match on text; no new type | ✓ |
| `EdgeSelectionError(BuildError)` subclass | A type later phases could target | |
| Internal error → HTTP 500 | Needs the catch-all and an app.py branch changed | |

**User's choice:** `BuildError` naming the selector.

### Runtime guard strength vs the test

| Option | Description | Selected |
|--------|-------------|----------|
| Runtime non-empty; test exact count per shape | Round 2, D-flat 4, recess floor 2 per floor (verified by probe) | ✓ |
| Runtime exact expected count per shape | A second geometry model every bore phase must extend | |

**User's choice:** Non-empty at runtime, exact counts in tests.

### Does `_groove_floor_edges` get the same guard and test now?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — both selectors now | REQ names chamfer *and* fillet selectors; Phase 11 re-audits the floor selector | ✓ |
| Bore rim only | Narrowest reading of SC 1/2 | |

**User's choice:** Both selectors.

### What does `bore_rim_limit(p)` return; where does the 0.01 mm slack live?

| Option | Description | Selected |
|--------|-------------|----------|
| Exact geometric bound; model.py adds a named slack | calc.py knows no kernel tolerances; comment states why 10 µm not TOL | ✓ |
| `bore_rim_limit` includes the slack | A model.py secret in the pure-maths module | |
| Replace the radial band with positive identification | A selector redesign — beyond foundation scope | |

**User's choice:** Exact bound + named slack in model.py.

---

## Claude's Discretion

- File/directory names (JSON, corpus module, regression test module, regen script, make target).
- JSON layout for minimal diffs; record keying.
- How the zero-edge test provokes the guard; exact refusal wording.
- `_bore_rim_edges` signature; the slack constant's name.
- Where the measured `make verify` delta is recorded (`bench/RESULTS.md` vs plan SUMMARY).
- Whether D-03 + D-15 become one appended L26 (recommended yes).
- Test names; the corpus docstring's "do not re-pick" stance.

## Deferred Ideas

- Positive-identification edge selection (Pitfall 4 §4) — Phase 11/12 territory.
- `EdgeSelectionError(BuildError)` subclass.
- Runtime exact-count guard.
- `docker/smoke.py` / `bench/corpus.py` sets in the fixture.
- derive()-only records for the solver grid.
