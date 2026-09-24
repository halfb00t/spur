# cli

`src/spur/cli.py`. One file.

## Responsibility

`spur serve`, `spur info`, `spur export` — the same gear, the same numbers, the same
errors as the API, from a shell.

## Boundaries

- **The CLI must not inherit web-serving policy** (L04). It does not import `app`,
  `fastapi` or `starlette`; an import-linter contract enforces that. `spur serve` starts
  uvicorn by import string (`"spur.app:app"`), which is a string, not an import.
- `calc` and `model` are imported inside the subcommand functions, so `spur --help` and
  `spur info` do not pay for loading OpenCascade.

## Shape

Gear flags are generated from `GearParams.model_fields`, including the help text and the
default shown in brackets, and `Literal` fields become `choices`. A new parameter appears
in the CLI with no edit here (L02).

`_params(ns)` builds the model from only the flags actually passed — omitted flags take
the model's defaults rather than `None` — and turns a `ValidationError` into
`error: <field>: <message>` on stderr with exit 2, the same information the API puts in
`detail[].ctx.fields`.

`spur export` derives the format from the file extension (`.stp` → `step`) unless
`--format` says otherwise, writes the bytes, then prints any `warnings` to stderr — so a
capped recess is visible to someone scripting exports.

## Errors

Exit 2 with `error: …` on stderr for bad parameters and for an unknown output extension;
`BuildError` becomes `error: <kernel message>`. Nothing is written when the build fails.

## Logging

`spur serve` configures the structured JSON logger (`records.configure()`, `L20`) before
starting uvicorn — it is the composition root for every production deployment
(Dockerfile `CMD ["spur", "serve"]`, `make serve`). `spur info` and `spur export`
deliberately do not: none of the logged branches exist on the CLI path (no admission
queue, no byte cache, no build pool — L04), so there is nothing here for a logger to
observe. Their stderr prose above (`error: …`, `warning: …`) is their diagnostic,
matching the stdout-is-product-output / stderr-is-diagnostics convention `records.py`'s
own stream choice (D-04) was built to match, not the other way around.

## Tests

`tests/test_cli.py`, 4 tests — added because the CLI had none and the README's own
example did not run (F3/F8). They run the README's commands verbatim, check that the
mate is reported, that the narrowed-recess warning reaches stderr, and that an infeasible
parameter exits 2 naming the field.

Run: `.venv/bin/python -m pytest tests/test_cli.py -q`.
