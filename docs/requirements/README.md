# Requirements

Durable, cross-phase requirements — the ones that outlive any single piece of work.
Per-phase discovery and the roadmap belong to gsd, in `.planning/`; this directory holds
what stays true after a phase is archived.

Nothing is written here yet, and nothing should be invented to fill it. Requirements land
here when they are real: when a stated expectation survives a phase and someone would be
wrong to change it without noticing.

What goes where, once there is something to write:

- `functional.md` — what the product must do, phrased as a checkable statement.
- `nfr.md` — performance, memory, portability, reproducibility budgets, with the number
  and how it was measured.
- `errors.md` — the error contract: which conditions refuse, which cap-and-warn, what a
  client can rely on in a `4xx`/`5xx` body.
- `security.md` — the threat model actually being defended against, and what is
  explicitly out of scope.

Where a requirement already exists in another form today, cite it rather than copying it:

- The error contract is stated in `docs/architecture/decision_log.md` (L03, L08) and
  exercised in `tests/test_calc.py` and `tests/test_api.py`.
- The memory and reproducibility budgets are in L07 and L12, with the measurements in
  `docs/plan-2026-09-21.md`.
- The security posture — no authentication, localhost binding, hardened container — is in
  the README and tracked as `docs/tech_debt/active/2026-09-21-no-authentication.md`.
