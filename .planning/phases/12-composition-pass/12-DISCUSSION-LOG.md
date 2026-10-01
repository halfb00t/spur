# Phase 12: Composition Pass - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-29
**Phase:** 12-composition-pass
**Areas discussed:** Composed sweep rows + the over-30s lever; Composition matrix vs make verify cost; Interface parity proof + the UI pass verdict; SC4/SC5 wording + the close-out record

Session facts: branch `gsd/phase-12-composition-pass` cut from `origin/main` `c9a169d`
before the discussion (HOW_TO_DEVELOP §2); no SPEC.md, no prior CONTEXT.md, no plans, no
matching todos; all six 11-REVIEW findings read `fixed`. Two evidence conflicts were
surfaced up front: SC3's "recess + hex pattern" vs the measured spokes + tip-chamfer
risk; SC5's "identical export" vs L26.

---

## Composed sweep rows + the over-30s lever

| Option | Description | Selected |
|--------|-------------|----------|
| Stacks on each cutout's heaviest row | Each pattern's recorded heaviest row + tip chamfer at cap + recess both, on the heaviest bore that fits, at module 1.75 and 10 (~12 rows) + six single-feature baselines | ✓ |
| Full cross product | cutout × tip × bore × module, 48 rows, ~20–30 min | |
| SC3 literal only | Recess + honeycomb (+ tip) plus per-feature heaviest rows | |

**User's choice:** Stacks on each cutout's heaviest row (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Lower the count le again | D-07/D-18 precedent; schema-visible; second offer raise the timeout; honeycomb → HEX_CELL_CAP | ✓ |
| Raise SPUR_BUILD_TIMEOUT with L31 | The tip-chamfer debt file's own suggestion; no part changes | |
| Teeth-dependent cap | Rejected twice before; listed for completeness | |

**User's choice:** Lower the count le again (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Quiet host required, load < 1.5 | The spoke debt file's bar; loaded readings recorded but not decisive | ✓ |
| Accept as measured under whatever load | Phase 11's UAT precedent | |

**User's choice:** Quiet host required (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Amend SC3 via edit-phase tooling | First plan task, one human confirmation; names no winner before the number | ✓ |
| Leave SC3 as written | Stays literally true, points at the wrong row | |

**User's choice:** Amend (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Single-gear sweep only | Success Metric 2's scope; ten-concurrent stays a debt trigger | ✓ |
| Also one ten-concurrent run of the worst composed row | bench.latency with the composed row in flight | |

**User's choice:** Single-gear only (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Resolved by the composed measurement, same commit | Status flipped, number and decision recorded, git mv, INDEX rows; stays active if a decision is deferred | ✓ |
| Keep both active until v0.2 closes | Resolve at gsd-complete-milestone | |

**User's choice:** Resolve in the same commit (recommended).
**Notes:** The user asked for "More questions" once in this area (concurrency, debt closure) before moving on.

---

## Composition matrix vs make verify cost

| Option | Description | Selected |
|--------|-------------|----------|
| Two tiers: full calc cross product + kernel rows for unbuilt pairs | 96 calc rows; ~18 kernel rows (tip applied × cutouts × bores; single-sided recess × cutouts) | ✓ |
| Full kernel cross product | 96 built rows, est. +100–150 s on the gate | |
| Kernel matrix outside the gate | Marker / separate target; the gate would not prove composition | |

**User's choice:** Two tiers (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| +30 s line for this phase's new tests, halt if over | D-06's shape, two alternating runs | ✓ |
| No line — measure and record only | | |
| Hard ceiling on the whole gate | Forces trimming existing tests | |

**User's choice:** +30 s line (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Every refusal × every other family, calc level | ~40 parametrized rows + one API and one CLI routing row per refusal | ✓ |
| One composed row per refusal | Planner-chosen; does not prove invariance | |

**User's choice:** Every refusal × every other family (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse each feature's own proof helper on the composed solid | 10-03's tip helper, 11-08's cutout and fillet-survival helpers, selector Counters | ✓ |
| Validity and derive parity only | | |

**User's choice:** Reuse the proof helpers (recommended).
**Notes:** "Next area" chosen; tier-2 row parameters, table construction, keyed D-flat coverage and a composed tripwire left to Claude's discretion.

---

## Interface parity proof + the UI pass verdict

| Option | Description | Selected |
|--------|-------------|----------|
| One model-driven Python test + manual browser UAT | Walk GearParams.model_fields across schema/CLI/one composed link; static app.js round-trip check; browser checklist at verify-work | ✓ |
| Fund the first headless browser test | Playwright via Node in web/; new CI job; slower gate | |
| Keep per-feature tests only | | |

**User's choice:** Model-driven test + manual UAT (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Leave the form schema-driven; record the verdict | 08 D-09 stands; both idea files get the verdict and a new trigger | ✓ |
| Take conditional form fields | Needs a schema key or hard-coded relations; supersedes 08 D-09 | |
| Take the bore-shape selector | Biggest UI change; supersedes 08 D-09 | |

**User's choice:** Leave schema-driven (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Fold in the cli.md exit-code debt: fix "Errors" + status asserts, resolve | Trigger fires in this phase anyway | ✓ |
| Leave it active | | |

**User's choice:** Fold it in (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, one composed README link run by the tests | "Everything on" example; post-v0.2 set, out of the corpus | ✓ |
| No README change | | |

**User's choice:** One composed link (recommended).
**Notes:** "Next area" chosen; the composed link's values, the UAT checklist wording, the idea files' trigger sentences and whether the test pins group order left to Claude's discretion.

---

## SC4/SC5 wording + the close-out record

| Option | Description | Selected |
|--------|-------------|----------|
| Amend SC5 to the fixture's real contract | Same first task as SC3; PROJECT Success Metric 3 read the same way; L31 says so | ✓ |
| Leave SC5; the fixture replay is the proof | | |
| Pin export bytes after all | Contradicts L24/L26 | |

**User's choice:** Amend SC5 (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| The composed-sweep row with the largest measured fine STL | build_time.py records STL bytes and triangle count per row | ✓ |
| Honeycomb at cap + recess both, by inspection | | |
| Re-measure on every composed row | | |

**User's choice:** Largest measured fine STL (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| A committed bench script + make target | gzip 1/6/9 time and bytes; STL on shape.copy() vs in place with peak RSS; test_bench row | ✓ |
| One-off numbers with the command recorded in RESULTS.md | | |

**User's choice:** Committed script + make target (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| Apply L19's rule as written: change _GZIP_LEVEL if it flips, L31 cites the table | L24's copy cost recorded only | ✓ |
| Record only; keep level 1 regardless | | |

**User's choice:** Apply the rule (recommended).

| Option | Description | Selected |
|--------|-------------|----------|
| One L31, append-only | L27–L30's shape; milestone close stays gsd-complete-milestone's | ✓ |
| Two entries: L31 sweep/lever, L32 UI-pass verdict | | |

**User's choice:** One L31 (recommended).
**Notes:** "Done with this area" chosen; the script's name and output shape, the peak-RSS reading and the exact SC3/SC5 sentences left to Claude's discretion. At the final gate the user chose "I'm ready for context" over exploring the codebase-map refresh and the L17 mem_limit re-sweep.

## Claude's Discretion

- Names: sweep file, RESULTS.md sections, test names, the export-cost script and target,
  tier-1 table construction.
- Sweep-row exactness: per-row largest hex the hub rule allows; adjusted rows recorded
  beside, not instead of, the unchanged ones; `spoke_fillet` on the module-10 row.
- Tier-2 row parameters; keyed D-flat row; a composed tripwire.
- Whether the parity test pins field/group order literally (recommend yes).
- The composed README link's values; the UAT checklist wording; the idea files' verdict
  and trigger sentences.
- Peak-RSS reading and the ten-concurrent gzip harness for the export-cost script.
- Plan order: amendments first; sweep before the re-measurement; L31 and debt
  resolutions last.

## Deferred Ideas

- Headless-browser test (idea stands; trigger gains "either UI idea is taken").
- Conditional form fields; bore-shape selector (not taken at the UI pass; new triggers).
- The composed worst row under ten concurrent builds (re-homed trigger in the waived
  latency-bar debt file).
- L17's `mem_limit` re-sweep on v0.2 topology (milestone-audit candidate).
- Refreshing `.planning/codebase/*.md` before plan-phase (process).
- STL triangle counts for the earlier sweep sections (not rewritten).
