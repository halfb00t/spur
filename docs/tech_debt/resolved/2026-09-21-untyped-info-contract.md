# The info contract is `dict[str, Any]`

Severity: must
Status: resolved
Date: 2026-09-21
Resolved in: 013900d
Source: setting up the gate — mypy `disallow_any_explicit` had to be left off (L14)
Related files:
- src/spur/calc.py (`derive`, `with_mate`)
- src/spur/app.py (`info`, `schema`)
- pyproject.toml (`[tool.mypy]`)

## Context

`derive()` returns a JSON document whose keys depend on the parameters — the recess
fields are `None` when there is no recess, `mate_teeth` and `centre_distance` appear only
when a mate was asked for, `warnings` is a list of sentences. `dict[str, Any]` is the
honest type for that today, so `disallow_any_explicit` is off in the mypy config.

Everything else about mypy is strict: `strict = true`, `warn_unreachable`,
`ignore-without-code`, `redundant-expr`, `truthy-bool`, `possibly-undefined`. `src/` has
zero errors. `src/spur/py.typed` was added so the project's own tests and any consumer
check against the real types rather than `Any`.

## Why it matters

This is the response body the web UI, the CLI and any API client parse. A renamed or
dropped key is currently a runtime surprise for all three, and the type checker cannot
say a word about it. The UI already reads `detail[].ctx.fields` and `warnings` by name.

## Why it is not fixed now

Turning the rule on today fails the gate on code that is correct. It is a ratchet, not an
exemption — the rule stays in the config, commented, with this file named next to it.

## Next step

Give the report a real shape: a `DerivedDimensions` model (Pydantic, so it also improves
the OpenAPI document) with explicit optional fields, returned by `derive()` and serialised
at the API boundary. Then turn `disallow_any_explicit` on and delete this file.

Revisit when: a client depends on the shape, or a third consumer of `/api/info` appears.

## Resolution (2026-09-24)

`Resolved in: 013900d` is Plan 04-01 Task 1's commit (`feat(04-01): derive() returns a
frozen DerivedDimensions model`), which gave the report its real shape — not the present
commit, which turns `disallow_any_explicit` on and is the last step this file's own
"Next step" asked for (a file cannot carry its own commit's sha).

What now exists: `DerivedDimensions`, a frozen pydantic model in `calc.py`, returned by
`derive()` with every key always present (`mate_teeth`/`centre_distance` `null` when no
mate was asked for, rather than absent); `HealthReport`/`PoolState` for `/api/health`
(Plan 04-02); `spur info --mate-teeth` range-checked to the same bounds `InfoQuery`
enforces (this plan, REQ-cli-parity); the 22 baseline `explicit-any` errors this phase
started with (`04-CONTEXT.md`) all removed; `disallow_any_explicit` on globally in
`pyproject.toml`, satisfiable via the pydantic plugin's `init_typed`/`init_forbid_extra`
settings (R-1, `L21`) rather than a suppression comment per model. `L21` (supersedes
`L14`) records why.

Three tests hold the contract in place: `tests/test_api.py::test_openapi_documents_the_
typed_contracts` (the OpenAPI shape), `tests/test_api.py::test_every_key_the_ui_reads_
is_a_derived_dimensions_field` (the `app.js` belt), and
`tests/test_cli.py::test_cli_and_api_print_the_same_document` (CLI-equals-API).
