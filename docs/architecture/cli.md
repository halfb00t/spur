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
`error: <field>: <message>` on stderr with exit 2, the same fields the API puts in
`detail[].ctx.fields`; a `check()` refusal prints `error: <message>` instead, with no
field prefix (see "Errors" below).

`spur export` derives the format from the file extension (`.stp` → `step`) unless
`--format` says otherwise, writes the bytes, then prints any `warnings` to stderr — so a
capped recess is visible to someone scripting exports.

## Errors

Three cases, two exit statuses — the CLI's real contract, not a guess from the API's:

- A parameter error raises `SystemExit(2)` — exit 2 — with one of three stderr shapes:
  argparse's own `spur <cmd>: error: argument --x: ...` for a flag it cannot parse;
  `error: <field>: <message>` for a field-level `GearParams` bound; and
  `error: <message>` (no field prefix — the `infeasible` error's `loc` is empty) for a
  `check()` refusal, the sentence the API's 422 carries in `detail[].msg`. The fields the
  API names in `detail[].ctx.fields` are not printed by the CLI.
- An unknown output extension raises `SystemExit("error: output must end in .stl or
  .step (or pass --format)")` — a string argument, which Python prints to stderr and
  turns into exit 1, not exit 2.
- Every `BuildError` raises `SystemExit(f"error: {exc}")` the same way — exit 1, same
  as the extension case.

Nothing is written when the build fails.

Pinned by `tests/test_cli.py::test_unknown_output_extension_is_refused` (asserts
`exc.value.code` equals the exact string),
`::test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing`
(asserts `exc.value.code` is a string, not `2`), and
`::test_an_unknown_output_extension_exits_1_from_the_real_process` (the real
`python -m spur.cli export` process's own exit status, not just `SystemExit`'s `code`
attribute).

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

`tests/test_cli.py` — added because the CLI had none and the README's own example did
not run (F3/F8). They run the README's commands verbatim, check that the mate is
reported, that the narrowed-recess warning reaches stderr, and that an infeasible
parameter exits 2 naming the field.

Run: `.venv/bin/python -m pytest tests/test_cli.py -q`.
