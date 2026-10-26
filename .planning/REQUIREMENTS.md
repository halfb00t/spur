# Requirements: spur — milestone v0.7 Splined Shaft

**Defined:** 2026-10-23
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

Scope fixed in `PROJECT.md` ("Current Milestone: v0.7 Splined Shaft"). Research pass:
`.planning/research/SUMMARY.md` is the entry point; its resolutions are authoritative over any
single research file. Every DIN 5480 formula below is an ASSUMPTION until checked by clause
against the human's copy (DIN 5480, 2006 series) and the check is recorded in the plan summary.
The human's choices (2026-10-23) are baked into the wording: external shaft with one plain
shank; DIN 5480 only; fit tables transcribed into a **private gitignored file** (the repo is
public); the solid carries the **effective maximum-material** tooth thickness; d_Ff prints
`null` until proven; the web page **prints** the designation, the API and CLI **accept** it; a
size absent from the tables **builds** with its table-dependent numbers withheld; WR-02 is
**fixed** in the interface phase.

REQ-IDs continue the project's `REQ-slug` convention.

## Rules every requirement lives by

- **Same gear, same links.** `tests/regression/` and `.github/workflows/ci.yml` stay
  byte-identical to the `v0.6` tag at every phase close (`git diff --exit-code v0.6 --
  tests/regression/ .github/workflows/ci.yml` empty); `make fixture.regen` is not run in v0.7.
  No new `GearParams` field. The gear `/api/schema` response is byte-equal to `v0.6` (L05, L26).
- **Honest or absent.** A shaft number that cannot be computed, or that depends on a table value
  not loaded, is a warning and `null` — never a plausible number (L08). Every shipped shaft
  formula is proved against an independent oracle that shares no code with the shaft maths.
- **No licensed value in the public repo** except anchor values the human approves by name;
  every transcribed value carries its part, clause and table citation.
- **Every new guard test is seen red once** against the defect it guards; the red is recorded.
- **No new runtime or dev dependency** (`requirements.txt` byte-identical; CPython 3.12, L23).
- **Gate cost is measured.** The `make verify` delta of each phase is recorded; a reading above
  L43's 300 s bar is surfaced to the human, not trimmed silently.

## v0.7 Requirements

### Scope and seam — the gear does not move

- [x] **REQ-scope-decision-logged**: a new `Lxx` widens the product to a gear and spline
  generator, amends L02 to one parameter model per part type and L05 to a second frozen link
  contract (shaft field names and defaults), logged before any shaft code lands.
- [x] **REQ-gear-unchanged-proof**: a check run at every phase close proves the rule "Same gear,
  same links" (regression dir, `ci.yml`, gear `/api/schema` byte-equal); seen red once on a
  deliberate edit.
- [x] **REQ-shaft-routes-separate**: the shaft is served under `/api/shaft/...`; the gear routes,
  their query keys and responses are unchanged; import-linter contracts keep the shaft maths
  free of `cadquery`, the logger and gear maths, and the shaft solid reachable only through
  `model`.

### Shaft maths — pure, oracle-proved

- [x] **REQ-shaft-params**: `ShaftParams` (d_B, module, tooth count, tolerance field, splined
  length, end chamfer, shank diameter and length) is validated once at its boundary; its field
  names and defaults are frozen in this phase, tolerance fields included.
- [x] **REQ-profile-shift-from-dB**: the profile shift is derived from d_B, m and z by the
  copy's formula (research: `x·m = (d_B − z·m)/2 − 0.55·m`); a combination whose x falls
  outside the standard's shaft range is a `422` naming the range, with an epsilon so the
  range edge (e.g. W30x2x14, x = −0.05) is accepted.
- [ ] **REQ-shaft-basic-dims**: the user sees d_B, tip diameter, root diameter and nominal tooth
  thickness, each proved against the independent oracle and against at least two anchor rows
  from the copy.
- [x] **REQ-form-diameter-honest**: d_Ff prints `null` with a sentence naming why, unless the
  copy's construction is reproduced by the oracle on an anchor row, in which case it prints the
  number.
- [x] **REQ-mre-nominal**: the user sees measurement over pins M_Re and the pin diameter D_Re at
  the nominal thickness, for even and odd z; pin contact is checked to lie between form and tip
  diameter or the value is `null` with a warning; odd z stays `null` until an odd-z anchor row
  confirms it.
- [x] **REQ-designation-codec**: `W <d_B>x<m>x<z>x<fit>` is printed for every shaft and parsed
  back to the same parameters (`.` and `,` decimals); an unparseable string is a `422` naming
  the bad token.

### Solid

- [ ] **REQ-shaft-solid**: the user downloads a valid STL and STEP of the splined section, the
  plain shank and the end chamfer; volume matches a closed form and the applied chamfer is read
  back from the solid.
- [ ] **REQ-shaft-build-measured**: build time, worker memory and STL size of the heaviest
  allowed shaft are measured and recorded in `bench/RESULTS.md` within L17's memory ceiling and
  L37's timeout; field bounds are set from that sweep.

### Interfaces — parity

- [ ] **REQ-shaft-api**: `/api/shaft/schema`, `/api/shaft/info`, `/api/shaft/model.stl` and
  `/api/shaft/model.step` serve the shaft with the gear routes' admission, cache and error
  contract.
- [ ] **REQ-shaft-cli**: `spur shaft ...` builds the same part and prints the same numbers as
  the API for the same parameters.
- [ ] **REQ-shaft-web**: the web page switches between gear and shaft, shows the shaft preview,
  its numbers (from a schema-carried row list) and its designation, downloads it, and round-trips
  a shaft link (`part=shaft&...`); a gear link carries no `part` key; any other `part` value is
  refused visibly; a browser test proves it.
- [ ] **REQ-designation-input**: the API and CLI accept a designation in place of the fields; a
  designation together with an explicit field it contradicts is a `422` (L03).
- [ ] **REQ-shaft-parity**: one parametrised test proves web, API and CLI agree on every shaft
  number and the download name for a fixed set of shafts.
- [ ] **REQ-wr02-fixed**: WR-02 (a link token the number box blanks but the API accepts) is
  fixed where the part switch edits `refuse()`/`gearQuery()`; its debt item is retired in the
  fixing commit.

### Fit tables and tolerance window

- [ ] **REQ-tables-private-file**: transcribed DIN 5480 values load from a gitignored file whose
  path is set by config/env; without it, every table-dependent number is `null` with a warning
  naming the missing file; no transcribed value is committed beyond human-approved anchors.
- [ ] **REQ-tables-transcribed-twice**: the file is produced by two independent reads diffed to
  zero; every row carries part/clause/table; a loader check enforces structural invariants
  (e.g. `T_G = T_act + T_eff`, µm-vs-mm range, no Unicode minus) and is seen red once.
- [ ] **REQ-fit-tolerance-window**: for a tabulated size and fit the user sees the effective and
  actual tooth-thickness windows; a fit outside the tables is a warning and `null`.
- [ ] **REQ-mre-limits**: the user sees M_Re max and min at the chosen fit with D_Re from the
  copy, proved against the oracle on the anchor rows.
- [ ] **REQ-solid-max-material**: with tables loaded, the solid carries the effective
  maximum-material tooth thickness (s + es); without them, the nominal thickness with a warning
  saying so.
- [ ] **REQ-off-table-builds**: a d_B/m/z absent from the size tables builds from the formulas,
  with every table-dependent number `null` and warned.

### Gate

- [ ] **REQ-gate-cost-recorded**: each phase records the `make verify` time against its
  predecessor on the same host; the milestone close reading is inside L43's 300 s bar or the
  human decides.

## Future Requirements

- ISO 4156 / ANSI B92.1 involute splines (next milestone), then ISO 14 straight-sided, then
  DIN 5481 serrations — one family per milestone.
- A web paste box for the designation (parse endpoint + browser test).
- The hob (trochoid) root on the shaft and small-z shafts whose root falls below the base circle.
- d_Ff as a number, if not proven in v0.7.
- Stepped shafts (more than one plain section, shoulders).
- Carried, not active: REQ-ubuntu26-classified-on-migration (from v0.6).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Internal spline (hub) in a gear's bore | Human chose the external shaft; the bore stays a v0.2 out-of-scope item |
| Strength / torque capacity | A rating, not geometry; needs load cases the tool has no model for |
| Table interpolation or snapping to the nearest size | Would print a value the standard does not give (L08) |
| Free-profile or non-standard splines | The value is the standard; a free profile is a different product |
| Committing licensed table values | Public repo, no licence file; human's decision 2026-10-23 |
| ISO-style `f8` aliases for DIN fit letters | Two spellings of one field break the frozen link contract |

## Traceability

Filled by the roadmap (2026-10-23). Phase numbers continue from v0.6's Phase 29. Phase 34 is
blocked until the human supplies the DIN 5480 copy's local path, and Phase 31 needs anchor rows
from the same copy (ROADMAP.md, Phases 31 and 34). `REQ-gate-cost-recorded` is cross-cutting:
every phase records its `make verify` delta in its own criteria, and the requirement closes at
Phase 34, where the milestone close reading is taken. `REQ-shaft-routes-separate` is mapped to
Phase 30, where its import contracts and route-prefix pin are put in force; Phase 33 serves the
shaft routes under that rule and cites it, it does not re-map it.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-scope-decision-logged | Phase 30 | Complete |
| REQ-gear-unchanged-proof | Phase 30 | Complete |
| REQ-shaft-routes-separate | Phase 30 | Complete |
| REQ-shaft-params | Phase 31 | Complete |
| REQ-profile-shift-from-dB | Phase 31 | Complete |
| REQ-shaft-basic-dims | Phase 31 | Pending |
| REQ-form-diameter-honest | Phase 31 | Complete |
| REQ-mre-nominal | Phase 31 | Complete |
| REQ-designation-codec | Phase 31 | Complete |
| REQ-shaft-solid | Phase 32 | Pending |
| REQ-shaft-build-measured | Phase 32 | Pending |
| REQ-shaft-api | Phase 33 | Pending |
| REQ-shaft-cli | Phase 33 | Pending |
| REQ-shaft-web | Phase 33 | Pending |
| REQ-designation-input | Phase 33 | Pending |
| REQ-shaft-parity | Phase 33 | Pending |
| REQ-wr02-fixed | Phase 33 | Pending |
| REQ-tables-private-file | Phase 34 | Pending |
| REQ-tables-transcribed-twice | Phase 34 | Pending |
| REQ-fit-tolerance-window | Phase 34 | Pending |
| REQ-mre-limits | Phase 34 | Pending |
| REQ-solid-max-material | Phase 34 | Pending |
| REQ-off-table-builds | Phase 34 | Pending |
| REQ-gate-cost-recorded | Phase 34 | Pending |

**Coverage:**
- v0.7 requirements: 24 total
- Mapped to phases: 24 (Phase 30: 3, Phase 31: 6, Phase 32: 2, Phase 33: 6, Phase 34: 7)
- Unmapped: 0

---
*Requirements defined: 2026-10-23*
*Last updated: 2026-10-23 after roadmap creation*
