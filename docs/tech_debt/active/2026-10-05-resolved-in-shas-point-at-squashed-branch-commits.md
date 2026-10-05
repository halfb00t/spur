# `Resolved in:` shas in the debt ledger point at squash-merged branch commits, not at `main`

Severity: nice
Status: active
Date: 2026-10-05
Source: v0.3 milestone audit, cross-phase integration check seam 6 (`.planning/v0.3-MILESTONE-AUDIT.md`)
Related files:
- docs/tech_debt/INDEX.md (Resolved table, "Resolved in" column)
- docs/tech_debt/resolved/*.md (`Resolved in:` field)
- docs/architecture/decision_log.md (L22, L25: `main` is landed only by squash-merge through `make pr.land`)

## Context

Every phase lands on `main` as one squash commit (L22, L25). A debt file is retired in the
commit that fixes it, on the phase branch, and records that commit's sha. So 19 of the 20
`Resolved in:` shas at the v0.3 close are not ancestors of `main`: `git merge-base
--is-ancestor <sha> origin/main` fails for them. Measured 2026-10-05 at `7a491bf` over every
file in `resolved/`: only `daeb284` (Phase 2, which landed by direct push) is on `main`; 13
of the 19 are contained in no local branch at all (the objects are still present); the six
v0.3 shas (`6709953`, `825095f`, `61e1bea`, `2aadcea`, `839dfea`, `4f7e8fe`) are reachable
only through `origin/gsd/phase-1[3-6]-*`. All five spot-checked shas resolve on GitHub
(`gh api repos/halfb00t/spur/commits/<sha>`), because the merged PRs' `refs/pull/N/head`
keep them — 19 such refs on `origin`.

## Why it matters

Low. The record is true but fragile outside GitHub: a fresh clone cannot `git show 89304e2`
until it fetches `refs/pull/*/head`, and a local `git gc` after branch deletion drops the
thirteen branchless objects. No number a user cuts metal to depends on it; it is the
traceability of the ledger.

## Next step

Record the landing commit beside each `Resolved in:` sha — the PR number and the squash sha
on `main`, as a column in INDEX's Resolved table or a `Landed in:` line in each file — and
have the retirement rule say to record both. Until then a missing sha is recovered with
`git fetch origin 'refs/pull/*/head:refs/remotes/origin/pr/*'`.

Revisit when: a `Resolved in:` sha fails to resolve in a clone, a remote `gsd/phase-*` branch
is deleted, or the retirement rule in CLAUDE.md is next edited.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
