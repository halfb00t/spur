# spur — AGENTS.md

Standing brief for every AI agent working in this repo. Read it first. All agents
(Claude Code, Codex, Cursor, ...) read this one file; `CLAUDE.md` is a symlink to it.

Keep this file short. It is loaded on every interaction. Project detail lives in `docs/`
and is read on demand.

## What we're building

A parametric involute spur gear generator: set the parameters, get a live 3D preview, the
numbers you would measure on the real part, and an STL or STEP download — from a web UI,
an HTTP API or a CLI, all driven by the same parameter model.

Full intent: gsd `.planning/PROJECT.md` (not written yet — run `gsd-map-codebase`, then
`gsd-ingest-docs`). System map: `docs/architecture/overview.md`. Global requirements:
`docs/requirements/`. How the human drives this: `docs/HOW_TO_DEVELOP.md`.

## Stack

Python 3.10–3.12 (`cadquery-ocp` publishes wheels for nothing newer), CadQuery /
OpenCascade for the solid, FastAPI + Pydantic v2 + uvicorn for the API, argparse for the
CLI, vanilla JS + a vendored tree-shaken three.js bundle for the viewer (the runtime needs
no Node), pytest for tests, Docker + compose for delivery, GitHub Actions for CI.

Why this stack and every other locked choice: `docs/architecture/decision_log.md` (cite
decisions by id, e.g. L01).

## How to verify (the gate)

Nothing is "done", "fixed", or "working" until checks pass. The one command:

```
make verify
```

It runs ruff, mypy `--strict`, the import-boundary contracts, an unfinished-work scan and
pytest. It needs no Docker. `make check` adds the two container checks CI also runs (the
in-image smoke test and the vendored-bundle byte check) and does need Docker.

State the command you ran and the result line in your reply. Predicting that tests pass is
not the same as running them.

## Stop and ask first

Surface to the human and wait for a decision when:

- An architectural claim isn't in the decision log.
- A locked decision (Lxx) looks wrong — propose superseding it, don't just ignore it.
- A library/API behavior is unverified after a real check.
- Evidence conflicts (doc vs code vs prior decision vs what the human said).
- A destructive operation is involved (`git reset --hard`, force push, `rm -rf`, dropping
  data, deleting branches, overwriting uncommitted work).
- A choice trades stability for speed — pick stability and surface it.

Ask format: the trigger, 2-3 options, your recommendation, then wait.

## Decisions

- `docs/architecture/decision_log.md` is the single source of locked decisions.
- New non-trivial choice: give 2-3 options + tradeoffs + a recommendation, let the human
  pick, then log it as a new `Lxx`. Don't re-litigate logged decisions.
- Ground claims in evidence: a cited decision, a file you read, a command you ran, docs you
  fetched, or the human's confirmation. Flag guesses as `ASSUMPTION:` and surface them
  before acting.

## This project's two standing rules

They are easy to break by accident and expensive to notice later:

- **A number the tool prints is a number someone will cut metal to.** If a value cannot be
  computed honestly, report a warning and no number — never a plausible one (L08).
- **A parameter the user did not set must never silently change the part.** Defaults are
  absolute millimetres and stay put, because every shareable link that omits a field
  depends on them (L05). Dimensions that can be trimmed without contradicting an explicit
  choice are capped and warned about; a direct conflict between two things the user asked
  for is a `422`, not a guess (L03).

## Keep it simple, keep it small

- Simplest solution that actually works. Three similar lines beat a premature abstraction.
  Don't add speculative features or flexibility nobody asked for.
- Default to surgical edits. Don't refactor or rename adjacent code unless asked; note the
  tangent and raise it after.
- One concern per commit. Commits are semantic checkpoints — one logical unit of work, not
  micro-commits. Mixed-concern diffs hide regressions.

## Finishing work properly

New behavior ships with its tests in the same change. Claims about performance or memory
are measured and the numbers recorded, not estimated — that is the standard the existing
`docs/review-2026-09-21.md` and `docs/plan-2026-09-21.md` set. Don't leave `TODO`, `pass`
or unreachable branches as if they were finished; `make verify` fails on the markers.

## Capturing ideas and debt (don't lose them)

Non-blocking work survives in files, not just in a reply. One file per item,
`YYYY-MM-DD-short-slug.md`, from `docs/<dir>/TEMPLATE.md`; add a row to that dir's
`INDEX.md` in the same commit.

- Good idea that isn't for now → `docs/ideas/`.
- Known-bad code, missing test, risky shortcut, deferred fix → `docs/tech_debt/active/`.
  Tag `Severity:` — **blocker** (corruption / silent partial success / source-of-truth /
  paid-API drain) | **must** (correctness/maintainability, or deferred with a named
  trigger) | **nice**.
- Blocker → fix it now or stop and ask; never just file it and move on.
- On fixing debt: flip `Status: resolved`, add the commit sha, `git mv` into
  `docs/tech_debt/resolved/`, move the INDEX row — in the same commit as the fix.
- Before your final reply, state whether you filed any item and its path.

## Tools and skills

- Reuse the project's command surface (`make`) instead of ad-hoc shell. `make` on its own
  lists every target. Check for an existing one before inventing a command.
- Planning and execution: gsd skill suite (`gsd-plan-phase`, `gsd-execute-phase`, ...).
- User-facing text (explanations, reviews): caveman — terse, no filler.
- Commit messages: Conventional Commits, normal prose — NOT caveman.
- Writing code: ponytail — simplest thing that works, no speculative abstractions.
- Project-specific skills live in `.ai_skills/` (see its `README.md`). When a project
  workflow repeats, add a skill there (use `skill-creator`) instead of re-deriving it each
  session.
- Cross-CLI review: this repo is set up for both Claude Code and Codex. Whoever wrote the
  diff does not review it.

## Code style

Full coding standard: `docs/CODING_VALUES.md` — read it before writing code. The
essentials:

- Comments explain *why*, and carry the measurement or the constraint that forced the
  choice. This codebase's comments are its best asset; match them or don't add one.
- Pure maths stays out of the CAD kernel's way: `calc.py` runs on every keystroke and must
  never import `cadquery`. The import-boundary contracts enforce this.
- Vendor types stop at their boundary. `cadquery` objects do not escape `model.py`.
- A parameter is validated once, at the `GearParams` boundary, and trusted afterwards.
- English throughout: identifiers, comments, commits, PR titles.
