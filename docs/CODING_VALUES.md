# spur — Coding Values

What code this project welcomes and rejects. Agents read this before writing; reviewers
judge against it. `AGENTS.md` carries the short version loaded every turn — this is the
full reference, read on demand.

The owner can override any value — when they do, log it as a decision (`Lxx` in
`docs/architecture/decision_log.md`) and update this file. An agent that disagrees with a
value raises it; it does not quietly ignore it.

Sections the template ships that are **deliberately absent**: there is no database, no
queue, no cache server, no external service client, no migrations and no authentication
in this project. Do not add a section back speculatively — add it when the thing exists.

## Vision

Code reads like the architecture says it works. Open a file and see its responsibility,
its data and its failure path. Stable beats fast.

This codebase has one asset that is easy to destroy and hard to rebuild: **its comments
carry the measurement or the constraint that forced the choice.** "1578 MiB resident
without this, 360 MiB with it." "~50x slower on a many-toothed outline." "1g made ~5% of
those requests fail." Match that standard or do not add a comment. A comment that
restates the code is worse than none; a comment that records the number that settled an
argument is the most valuable line in the file.

## Stack

Pointers only; the *why* is in `decision_log.md`.

- **Core + API:** Python 3.10–3.12, FastAPI, Pydantic v2, uvicorn. Why → `L01`.
- **Geometry:** CadQuery over OpenCascade. Why → `L01`, and the constraints it imposes →
  `L06`, `L07`, `L09`.
- **Viewer:** vanilla JS + a vendored three.js bundle. Why → `L11`.
- **Delivery:** Docker, compose, GitHub Actions. Closure pinning → `L12`.

## Code values

- **A wrong number is worse than no number.** This is the first rule, not a nicety. If a
  value cannot be computed honestly, return `None` and say why (`L08`). Never return a
  plausible one.
- **Never change the part the user did not ask to change.** Defaults are frozen (`L05`);
  a dimension may be capped only when capping contradicts nothing the user set, and the
  cap must appear in `warnings` (`L03`).
- **Measure before you claim.** Performance, memory and size statements ship with the
  number and the workload that produced it. "Faster" without a figure does not go in a
  comment, a commit message or a reply.
- Explicit types at every boundary. Vendor types stop at their boundary — no CadQuery
  object escapes `model.py`.
- `Any` is not written here (`L21`), and the type checker enforces it
  (`disallow_any_explicit`). A genuinely untyped value is `object`, narrowed where it is
  used; a value a library already names keeps the library's own alias.
- Self-documenting names. Domain names over pattern names: `recess_radii`, `root_fillet`,
  `_bore_rim_edges` — not `Manager`, `Processor`, `handle`.
- One operation per routine. `model.py`'s build pipeline is one product decision per step
  on purpose; keep it that way when adding a feature.
- Simplest thing that works. Three similar lines beat a premature abstraction.
- Limits live in code with an env var and a check, not only in infra. `compose.yaml`'s
  `mem_limit` is the backstop *behind* `SPUR_SOLID_CACHE` and `SPUR_EXPORT_CACHE_MB`, not
  instead of them.

## Coupling

The module graph is a designed object, not an accident, and it is enforced — see the
import-linter contracts in `pyproject.toml`. `make verify` fails on a violation, and that
has been verified by deliberately introducing one.

- `calc.py` (and `params.py`) must never import the CAD kernel. It runs on every
  keystroke; the moment it can reach OpenCascade that property is gone silently.
- `cli.py` must never import `app`, `fastapi` or `starlette`. Web-serving policy is not
  the CLI's to inherit (`L04`).
- `model.py` is the only doorway to `cadquery`/`OCP`.
- Adding a module means deciding where it sits in that graph, and usually adding a
  contract. A new contract is cheap; discovering an accidental cycle six months later is
  not.

## File and function boundaries

No line-count rules — they invite gaming. Surface a boundary problem to the human when:

- A function cannot be named in one sentence.
- A file mixes concerns — transport with geometry, policy with mechanics.
- A change needs editing three unrelated places.
- A parameter list passes ~5 raw arguments; group them into a typed object (`GearParams`
  and `Profile` are the existing examples).
- Nesting passes ~3 deep.
- A function both decides and acts. `calc.py` decides; `model.py` acts. Keep it.

## Validation

Types are the primary contract, and validation happens exactly once.

- `GearParams` is the inbound boundary for all three front ends. Range checks are field
  metadata; cross-field feasibility is `check()` called from the model validator.
- After that boundary, trust the types. Do not re-validate a `GearParams` downstream.
- An invariant a type cannot express is asserted positively, not assumed — `_build()`
  checks that exactly one valid solid came out.
- Positive boolean names (`is_paid`, `has_stock`); negated forms are banned.

## Naming

English throughout: identifiers, files, comments, commits, PR titles. Domain terms in
their standard form — `module`, `pressure_angle`, `profile_shift`, `backlash` are gear
vocabulary and stay as they are. Single-letter names are acceptable only where they are
the standard symbol for the quantity inside a short mathematical routine (`r`, `rb`, `ra`,
`rf`, `z`, `m`, `x`, `alpha`), and the file must define them once — as `Profile` does.
Anything that escapes such a routine gets a real name.

## State

There is almost none, and it should stay that way.

- Nothing is persisted. Every answer is derived from `GearParams` on demand.
- The caches are a speed optimisation and must remain safe to lose at any moment (`L07`).
  Nothing may become correct only because something was cached.
- The one piece of true process state is the kernel lock (`L06`) and the build semaphore
  (`L04`). Both are module-level by necessity and both are documented where they live.
- If this project ever needs durable state, that is a decision (`Lxx`) and a phase, not a
  module-level dict.

## Failure handling

Three responses, and picking the right one is the design work:

- **Refuse** — a conflict between two things the user set explicitly. Name the fields.
- **Cap and warn** — a requested dimension that can be trimmed without contradicting an
  explicit choice. Never silent.
- **Report nothing** — a value that does not exist. A warning, not a number (`L08`).

Beyond user input: fail loud, once, with an actionable message. There is no retry tier —
a kernel failure is deterministic for the same parameters, so retrying only burns seconds.
`BuildError` is the only exception that leaves `model.py`, and it says what to try
instead.

## Logging

One JSON-lines logger, on stderr, configured at the composition boundary (`L20`):
`src/spur/records.py` owns the formatter, the `SPUR_LOG_LEVEL` knob and one small
function per event — `build_started`, `build_failed`, `export_served`, `queue_refused`,
`worker_replaced`. `app.py` and `pool.py` call these intent-named helpers; they never
assemble a log record's `extra=` dict by hand, and never call `logging` directly.

**The logger exists, so use it — do not add `print()` for diagnostics** in `src/`. That
prohibition is stronger now than when there was no logger to reach for instead: a
`print()` call today is not filling a gap, it is bypassing a mechanism that exists
specifically to be the one place diagnostics go. `cli.py` printing to stderr is
user-facing output, which is different, and is fine.

`calc.py` needs no logging even after that lands — it is pure, and `warnings` is its
diagnostic.

## Testing

Tests verify behaviour from the user's perspective. Asserting private calls or internal
call counts is banned.

- **Unit** — `calc.py`. Pure, fast, exhaustive on the rules. Test names read as
  requirements.
- **Integration** — `model.py` against the real kernel. Do not mock OpenCascade; a mock
  would test the mock. Assert geometry (volume, topology, watertightness), not snapshots.
- **Contract** — `app.py` through `TestClient`, including the error shapes the UI parses.
- **The README's own commands are tests.** `tests/test_cli.py` exists because a documented
  example did not run. Keep it that way.
- New behaviour ships with its tests in the same change.
- A regression gets the test that would have caught it, named after the property, not the
  bug number — `test_tooth_thickness_and_gap_are_measured_on_the_same_circle`.

## Tech debt and refactoring

- Refactoring for taste: no. Refactoring because a boundary broke: yes, as its own scoped
  task, surfaced first.
- Debt found during normal work becomes a `docs/tech_debt/active/` item — location, smell,
  suggested fix, and a trigger. Not a silent fix in an unrelated change.
- "Good enough for now" is not a reason to drop error handling or validation the contract
  implies. A deliberate cut is a logged item with the owner's sign-off, never silent.

## Dependencies

- A new dependency is a decision — ask first. Every one lands in the image, and this
  image already carries 1.6 GB of OpenCascade and VTK.
- `pyproject.toml` keeps loose ranges for developer environments; `requirements.txt` is
  the generated, fully-pinned closure the image installs (`L12`). Regenerate with
  `make lock`; never hand-edit a line.
- Prefer the standard library. `cli.py` uses `argparse`, not a CLI framework; the STL
  topology test parses the format with `struct`. That is the house style working.
- Upgrading `three` means `make vendor` and committing the rebuilt bundle; CI proves it
  matches (`L11`).

## Project-specific

- **Python 3.10–3.12 only.** `cadquery-ocp` publishes no wheels past 3.12 and pip will
  spend minutes failing to build OpenCascade from source. `make venv` picks a supported
  interpreter itself. Do not "modernise" the floor or the ceiling without checking wheels.
- **`requirements.txt` is installed with `--no-deps`.** A hand-bumped version there fails
  silently rather than loudly.
- **The vendored bundle is a build artefact.** Never edit `src/spur/static/vendor/` by
  hand; edit `web/` and run `make vendor`.
- **No automatic formatter** (`L16`). Line length and whitespace are linted; the
  arrangement within that is a human decision here.
