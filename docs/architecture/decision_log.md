# Decision log

Locked decisions. Cite by id (L01, L02, ...). Agents must not re-litigate a logged
decision; to change one, add a new entry that supersedes it and say which.

L01–L12 were reconstructed on 2026-09-21 from the code, the README and
`docs/review-2026-09-21.md` / `docs/plan-2026-09-21.md`. They record choices that were
already made and are visible in the tree — not new ones. L13–L16 were taken on
2026-09-21 while setting the repo up for agent work.

## L01 — Stack

Python 3.10–3.12, CadQuery/OpenCascade, FastAPI + Pydantic v2 + uvicorn, argparse,
vanilla JS with a vendored three.js bundle, pytest, Docker, GitHub Actions.

Reason: detected, not chosen — this is what the project is built from. The 3.12 ceiling
is not a preference: `cadquery-ocp` publishes wheels for 3.10–3.12 only, and pip will
otherwise spend minutes trying to build OpenCascade from source and fail. Migrating the
stack is out of scope; a mismatch is a tech-debt item, not a rewrite.

## L02 — One parameter model, three front ends

`GearParams` (frozen, hashable, Pydantic) is the single definition of a gear. The JSON
schema it generates builds the web form; `cli.py` generates its flags from the same
fields; the API takes them as query parameters.

Reason: a field added once shows up in all three. It also makes the parameter set a
usable cache key, which the build and export caches rely on (L07).

## L03 — Cap and warn, or refuse — never guess

A dimension that can be trimmed to fit **without contradicting something the user asked
for** is trimmed, and the trim is reported in `warnings` (the root fillet, the face
recess). A direct conflict between two things the user set explicitly is a `422` naming
the offending fields.

Reason: refusing over a parameter the user never touched is the bug F3 documented — 17%
of the standard module/teeth grid was unbuildable at stock defaults. Silently shrinking
a shaft bore would be worse than refusing. The line is "did the user ask for this?".

## L04 — Admission control belongs to the web layer

The bounded build queue (`SPUR_MAX_QUEUED_BUILDS`, `503` + `Retry-After`) lives in
`app.py`, not in `model.py`.

Reason: queue depth is a property of serving HTTP. A CLI export must never queue behind
anything. Enforced by an import-linter contract, not by convention.

## L05 — Defaults are absolute millimetres and do not rescale

The stock values describe the 19-tooth m=1.75 printer gear this project started from.
They stay put even when they do not suit a much smaller gear (L03 handles that instead).

Reason: every shareable model link omits the fields it left at default. Rescaling the
defaults would silently rebuild a different part from an old URL.

## L06 — One lock around the geometry kernel

Every OpenCascade call goes through one `RLock` in `model.py`.

Reason: OCCT is not safe to drive from several threads at once. Consequence, accepted
knowingly: concurrency buys latency, not throughput — which is what makes L04 necessary.

## L07 — Bounded caches, and hand the arenas back

Solids are cached by entry count (`SPUR_SOLID_CACHE`, default 4), exported bytes by
total size (`SPUR_EXPORT_CACHE_MB`, default 64), and `malloc_trim(0)` runs after every
cache-missing export.

Reason: measured. "32 entries" is not a memory bound when one solid costs ~280 MiB.
Cache trimming alone moved the plateau from 1.87 GiB to 1.5 GiB; the arena release took
it to 358 MiB — almost all of the apparent leak was glibc holding freed arenas, not live
cached data. The caches stay because they make the ceiling predictable.

## L08 — No number is better than a wrong number

`centre_distance()` returns `None` when `inv(aw) = inv(α) + 2·tan(α)·Σx/Σz` has no
solution, and the API reports a warning instead of a value. The solver is bisection on
`(0, 89°)`, not Newton.

Reason: this is the tool's headline "match a real gear" number, and a wrong one gets cut
into a bracket. The unguarded Newton loop returned confident garbage for 138 parameter
sets — some of them negative distances — all `200 OK`.

## L09 — Root fillets are computed, not filleted

The root fillet arcs are solved analytically in the 2D outline instead of calling OCCT's
fillet operator.

Reason: ~50× faster on a many-toothed profile, for identical geometry.

## L10 — Radial root below the base circle, with a warning

Below the base circle the flank is radial rather than trochoidal, as in most generators.
Where that matters — undercut on low tooth counts — `derive()` warns.

Reason: a known, documented approximation. It only affects undercut gears, and the
warning tells the user when they are in that region. Revisiting it is `docs/ideas/`.

## L11 — three.js is vendored as a committed bundle

`src/spur/static/vendor/three.bundle.min.js` is a tree-shaken esbuild output of `web/`,
committed to the repo. CI rebuilds it and fails if a single byte differs.

Reason: the runtime image needs no Node at all. The byte check is what stops a 568 KB
blob nobody can account for from drifting away from its source.

## L12 — The image installs a generated pinned closure

`requirements.txt` is the full resolved set (31 of 31 packages), generated by
`docker/refresh-requirements.sh` and installed with `--no-deps`. `pyproject.toml` keeps
loose ranges for developer environments.

Reason: with six of 56 packages pinned, a rebuild next month produced a different image
and a `starlette` major could break the build with no warning. Do not hand-edit it —
with `--no-deps`, pip will not tell you when a hand-bumped version breaks the closure.

## L13 — `make verify` is the gate

`make verify` = ruff + mypy `--strict` + import-linter + an unfinished-work scan +
pytest. No Docker, ~11 s warm. It runs in three places: a developer's shell, the
pre-commit hook, and CI. `make check` keeps its old meaning and now means `verify` plus
the two container checks.

Reason: "it works" has to mean "the checks passed", and there has to be exactly one
command that says so, or agents and humans end up asserting different things.

## L14 — mypy is strict, with `disallow_any_explicit` off as a ratchet

Strict mode, `warn_unreachable`, `ignore-without-code` and friends are on. Explicit
`Any` is still allowed.

Reason: `derive()` and `/api/info` return a JSON document whose keys depend on the
parameters, and `dict[str, Any]` is the honest type for that today. Turning the rule on
now would fail the gate on correct code. It is a ratchet, not an exemption — the trigger
and the intended shape are in
`docs/tech_debt/active/2026-09-21-untyped-info-contract.md`.

Two related choices: mypy targets `python_version = 3.12` because numpy's bundled stubs
refuse to be read below it — ruff (`target-version = py310`) and a real 3.10 test run in
CI are what hold the language floor. And `src/spur/py.typed` was added, so consumers and
the project's own tests are checked against the real types rather than `Any`.

## L15 — TRY003 is off; error messages are the product

Ruff's `TRY003` ("avoid long messages outside the exception class") is disabled. The
rest of the `TRY` set is on.

Reason: this project's errors name the offending parameter and say what to change —
"D-flat must be between 4.5 and 9 mm (flat to opposite side)". A class per message would
make them worse. The rule is wrong for this codebase, not the codebase for the rule.

## L16 — No automatic formatter

`ruff format` is not run and there is no `make fmt`. Ruff's `E`/`W` rules still enforce
line length and whitespace.

Reason: measured before deciding — the formatter would rewrite 10 files and 648 lines,
flattening comment alignment and continuation layout that was set by hand so the
geometry reads. The cost is real and the benefit here is style uniformity the project
already has. Revisit if the codebase grows past what hand-formatting can hold.
