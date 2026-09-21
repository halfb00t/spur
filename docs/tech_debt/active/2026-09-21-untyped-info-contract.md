# The info contract is `dict[str, Any]`

Severity: must
Status: active
Date: 2026-09-21
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
