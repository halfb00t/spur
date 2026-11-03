# Phase 30: Scope, Seam and Gear-Safety Guard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-23
**Phase:** 30-scope-seam-and-gear-safety-guard
**Areas discussed:** Gear-safety check shape, Seam scope vs no-ShaftParams, Contract timing & module names, L46 wording & reach

Before the questions, scouting found three facts:

- The `v0.6` tag already exists. It is annotated, pushed, and peels to `792b45c`.
- The research's `Part` union conflicts with "no `ShaftParams`" in this phase.
- Phases 32 and 33 also edit gear-side files.

---

## Gear-safety check shape

| Option | Description | Selected |
|--------|-------------|----------|
| Read from v0.6 at run | git show + temp worktree, nothing committed | ✓ |
| Committed snapshot file | one-off generated schema JSON | |

| Option | Description | Selected |
|--------|-------------|----------|
| HTTP response bytes | TestClient `/api/schema` on both trees | ✓ |
| model_json_schema() dict | cheaper, misses route/serialization drift | |

| Option | Description | Selected |
|--------|-------------|----------|
| Own target, inside verify | every gate run proves it | ✓ |
| Own target, phase close only | no gate cost | |
| Inside verify and CI | needs ci.yml edit — not viable | |

| Option | Description | Selected |
|--------|-------------|----------|
| gear.unchanged | dotted style, names the claim | ✓ |
| gear.guard | names the mechanism | |
| You decide | | |

Follow-up question: CI runs `make verify` from a shallow clone that has no tags.

| Option | Description | Selected |
|--------|-------------|----------|
| Fetch the tag itself | fetch when missing, fail naming the cause | ✓ |
| Skip with loud notice | silent pass — blocker-class | |
| Local-only target | no gate coverage mid-phase | |

## Seam scope vs no-ShaftParams

| Question | Options | Selected |
|----------|---------|----------|
| `_serve_model` move | Extract now, own commit / Defer to Ph33 / Duplicate | Extract now, own commit |
| `Part` type | Alias now, union in Ph31 / Defer all widening | Alias now, union in Ph31 |
| 503 text | Now, one test / Phase 33 / Leave it | Now, one test |
| Dispatch | Phase 32, amend roadmap / Stub raising BuildError now | Phase 32, amend roadmap |

**Notes:** Claude also noted two more later edits to shared files: Phase 33 adds routes to
`app.py`, and Phase 32 adds a `pool._warm` import. The roadmap claim is replaced by a rule:
later edits to `model`/`pool`/`app` are additive only, and each is proved by `gear.unchanged`.

## Contract timing & module names

| Question | Options | Selected |
|----------|---------|----------|
| When contracts land | Now, on placeholder modules / Ride with each module | Now, on placeholder modules |
| Layout | Research's flat split / Fewer modules / Subpackage `spur/shaft/` | Research's flat split |
| Strictness | Strict, no indirect / Mirror gear | Strict, no indirect |

## L46 wording & reach

| Question | Options | Selected |
|----------|---------|----------|
| Product name | Gear and spline generator / Gear and splined-shaft generator / Power-transmission part generator | Gear and spline generator |
| L02/L05 | Amend in place by reference / Supersede L02 outright | Amend in place by reference |
| Freeze | When interface ships (Ph33) / Frozen at Ph31 pin | When interface ships (Ph33) |
| Docs | AGENTS.md now, README at Ph33 / Both now / Both at Ph33 | AGENTS.md now, README at Ph33 |

## Claude's Discretion

- The route-pin test contents and location.
- The format of the red-run records.
- The gate-delta baseline: re-measure v0.6 or use the recorded 236.23 s.
- Whether `gear.unchanged` joins `verify.fast`.
- How the worktree is cleaned up.
- The commit split.

## Deferred Ideas

- README scope wording moves to Phase 33.
- The `model._build` dispatch and the `pool._warm` import move to Phase 32.
- The `ShaftParams` hash/frozen tests move to Phase 31.
