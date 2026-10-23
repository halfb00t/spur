# Project Research Summary

**Project:** spur — milestone v0.7 Splined Shaft
**Domain:** DIN 5480 external involute splined shaft as a second part type beside the spur gear
**Researched:** 2026-10-23
**Confidence:** MEDIUM (no researcher read the standard; every DIN formula is an ASSUMPTION until checked against the human's copy)

*Synthesised from STACK.md, FEATURES.md, ARCHITECTURE.md and PITFALLS.md. The synthesizer's
file write was refused (#222); the orchestrator persisted its returned synthesis and folded in
the human's three answers given after research (edition, licence, carried thickness).*

## Executive Summary

v0.7 adds the shaft as a clean sibling part type, not a generalisation of the gear. No
dependency is added (stdlib `math`/`re`, the pinned Pydantic and CadQuery). A new
`ShaftParams` sits beside `GearParams`; `params.py` and `calc.py` are not edited for shaft
maths. The shaft gets its own `/api/shaft/...` routes: an unknown query key on a gear route is
silently ignored (ARCHITECTURE probe: `/api/model.stl?part=shaft&bogus=1` returns 200), so a
`part=` key on shared routes would build a default gear. The kernel dispatches inside
`model._build` by type, so the one lock, both caches and the pool are reused.

The main risks are a plausible-but-wrong printed number (L08), the wrong edition or a
transcription error in the tables, and regressing the gear through the shared routes, page,
CLI and pool (L05/L26).

**Human answers after research (2026-10-23):** the copy is the **DIN 5480 2006 series**; the
transcribed values live in a **private, gitignored local file** (the public repo ships code,
formulas, clause/table citations and only human-approved anchor values); the solid carries the
**effective maximum-material tooth thickness** (s + es).

## Key Findings

### Recommended Stack

No new runtime or dev dependency; `requirements.txt` byte-identical (STACK, measured against the
venv and `docker/refresh-requirements.sh`).

**Core technologies:**
- stdlib `math` — involute, profile shift, M_Re; a guarded bisection for inv(α) inversion
  (`calc._involute_angle` precedent: 2.9e-15 rad over 20,000 angles, 2.8 µs/call). Copied into
  the shaft maths module, not shared (keeps gear and shaft numbers uncoupled).
- stdlib `re` — designation codec (`W 25x1.25x18x8f`; accept `.` and `,` decimals).
- CadQuery 2.8.0 — one extruded outline, `Shape.fuse` with the shank (never `Workplane.union`
  + `.clean()`: invalid when shank d = tip d), end chamfer as a revolved-cone `intersect`
  (`Solid.chamfer` past the tooth height returns an invalid solid with wrong volume, no error).
- No scipy (dev-only, pruned from the image). No open-source DIN 5480 oracle is usable
  (unlicensed or geometry-only).

### Expected Features

**Must have (table stakes):**
- Input by d_B, m, z and tolerance field; designation printed and parsed.
- Profile shift from d_B: `x·m = (d_B − z·m)/2 − 0.55·m` (reproduces KISSsoft W70x3x22 and
  Hexagon W120x3x38; shaft range x ∈ [−0.05, +0.45] needs an epsilon — W30x2x14 computes to
  −0.05000000000000004).
- d_a, d_f, tooth thickness s; effective vs actual thickness windows; M_Re max/min with pin
  diameter D_Re.
- Splined length, plain shank, end chamfer; STL/STEP; parity web/API/CLI.

**Should have (differentiators):**
- Every number proved against an independent oracle or warned (L08).
- Shareable shaft link with frozen field names and defaults.

**Defer / anti-features:**
- d_Ff (form diameter) prints `null` + a sentence in v0.7: the public construction gave 113.880
  against a vendor's 113.91, and KISSsoft prints two different values (63.718 vs 63.920) for
  one shaft.
- Strength/torque, table interpolation, snapping to the nearest size, free-profile splines, the
  hub side, ISO-style `f8` aliases, hob root on the shaft (v0.7.x).

### Architecture Approach

Sibling part type behind path-prefixed routes; dispatch inside `model._build`.

**Major components:**
1. `ShaftParams` (new) — validated once at its boundary; field names and defaults frozen when the
   interface ships, including the tolerance fields (L05).
2. Shaft maths module (new, pure) — import-linter contract: no `cadquery`, no logger, no gear
   coupling.
3. `shaft_model` (new) — reachable only through `model`; under `_LOCK`.
4. `/api/shaft/{schema,info,model.{stl,step}}`, `spur shaft` CLI group, web part select outside
   `#params`; shaft result rows in a schema-carried `dims` key (two `app.js` pins forbid a second
   row table and quoted field names, `tests/test_api.py:176-180`, `:314-340`).
5. `_serve_model` extracted from `app.py`'s `model()` as a pure-move commit (stop-and-ask).
6. The private tables file — gitignored, path by config/env; absent → table-dependent numbers
   warned, never guessed.

### Critical Pitfalls

1. **Wrong profile-shift formula** — the brief's `−1.1m` was off by 2×; test the range edge with
   an epsilon.
2. **Edition drift** — in the 2006 series the tolerance system and the root-diameter allowance
   are in Part 1, the dimension tables in Part 2; PROJECT.md's "DIN 5480-2 tolerance fields" is
   wrong and is corrected at requirements.
3. **Transcription errors** — two independent reads diffed to zero, structural invariants
   (`T_G = T_act + T_eff`, µm-vs-mm range), Unicode-minus guard, a citation on every row.
4. **Gear regression** — shared names (`module`, `teeth`), the stray-key-ignored behaviour,
   WR-02 firing on any edit of `refuse()`/`gearQuery()`. Every phase re-checks
   `git diff v0.6 -- tests/regression/ .github/workflows/ci.yml`; `make fixture.regen` forbidden.
5. **M_Re** — the theoretical pin touches at `m·z + 2xm`, not d_B; contact must lie between the
   form and tip diameters; odd z (`cos(90°/z)`) has no oracle row yet.
6. **Gate budget** — `make verify` 236 s against the 300 s bar (L43); shaft tests mostly pure.

## Implications for Roadmap

### Phase 1: Seam, scope and gear-safety guard
**Rationale:** the only phase that edits gear files; everything else depends on it.
**Delivers:** product-scope `Lxx` and the L02/L05 amendments, `parts.py`, type widening in
`pool`/`records`/`model`, `_serve_model` pure-move, import-linter contracts, the regression
proof harness (`git diff --exit-code` on `tests/regression/` and `ci.yml`, byte-equal
`/api/schema`).

### Phase 2: Shaft maths, parameters and designation (pure)
**Delivers:** `ShaftParams` (frozen names/defaults), profile shift, d_a/d_f/s, M_Re even and odd
with contact guard, designation codec ("cannot be checked" for tolerance letters until tables
load), an independent stdlib oracle.

### Phase 3: Solid
**Delivers:** `build_shaft` with closed-form volume and section read-back; build time, worker
memory and STL size in `bench/RESULTS.md` against L17/L37; field bounds from a sweep.

### Phase 4: Interfaces and parity
**Delivers:** API routes, `spur shaft`, web part select, `part=shaft` hashes only for shafts, a
stray `part=` on the gear page refused (L44-class), an explicit WR-02 decision, a browser
scenario.

### Phase 5: Fit tables and tolerance window
**Delivers:** private tables file loaded from config, two-reader transcription with citations,
thickness limits, M_Re max/min, the solid switching to the effective maximum-material thickness.
v0.7 releases as one unit.

### Phase Ordering Rationale

- Tables last: only table-dependent values wait on the copy; formulas don't.
- Licence, edition, carried thickness answered (2026-10-23); `h_fP` process and anchor rows
  still needed before Phase 2 planning.

### Research Flags

- Phase 2: needs the human's copy (formula confirmation, h_fP, anchor rows incl. one odd z).
- Phase 3: kernel spike with real DIN proportions.
- Phase 5: transcription risk.
- Phases 1, 4: standard patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Measured in the venv; third-party tool survey LOW |
| Features | MEDIUM | One vendor data point reproduced; tables not read |
| Architecture | HIGH / MEDIUM | File facts HIGH; module shape MEDIUM |
| Pitfalls | MEDIUM | Repo-integration HIGH; standard content MEDIUM |

**Overall confidence:** MEDIUM

### Gaps to Address

- Every DIN formula is an ASSUMPTION until checked against the 2006 copy by clause.
- `h_fP` convention (hobbing 0.60 vs others) — vendors differ.
- No odd-z M_Re oracle row; without one, odd-z M_Re stays `null`.
- d_Ff construction and root-fillet radius location in the 2006 copy.
- Build times measured on placeholder proportions only.
- Whether a size absent from the tables may be built (recommend: build it, withhold
  table-dependent numbers).

## Sources

### Primary (HIGH confidence)
- Repo code and probes: `src/spur/`, `tests/`, decision log, `.planning/codebase/`.
- CadQuery 2.8.0 spikes in the repo venv (STACK, PITFALLS).

### Secondary (MEDIUM confidence)
- KISSsoft W70x3x22 report; Hexagon W120x3x38x8f example; DIN publisher pages and the
  2026-01-20 warning notice (FEATURES).

### Tertiary (LOW confidence)
- GitHub/PyPI oracle survey; workshop articles on size ranges.

---
*Research completed: 2026-10-23*
*Ready for roadmap: yes*
