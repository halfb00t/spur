# Project skills

Skills specific to **spur** live here — repeatable workflows unique to this codebase, not
the general-purpose skills installed at the user level (gsd, caveman, ponytail).

This directory starts empty on purpose. Don't pre-build skills you might need; add one
when a real, repeating need shows up.

## When to add a skill

- A multi-step task done the same way two or three times.
- A project convention an agent keeps getting wrong — encode it once.
- A domain workflow with rules an agent can't infer from the code alone.

If it happens once, it's a note in `docs/`. If it repeats, it's a skill.

Plausible candidates for this project, listed as examples and **not** to be built
speculatively: bumping `three` and re-vendoring the bundle (`make vendor`, commit, prove
with `make vendor-check`); regenerating the pinned closure after a dependency change
(`make lock`, verify both architectures build); running the memory sweep that produced
the numbers in `docs/plan-2026-09-21.md`. Each is currently a documented `make` target —
turn one into a skill only when someone has actually got it wrong twice.

## How to add one

Easiest: ask the agent to use the `skill-creator` skill — it drafts, tests and tunes the
trigger for you.

By hand: make `<skill-name>/SKILL.md` with YAML frontmatter and steps:

```
---
name: my-workflow
description: >-
  What it does AND when to use it. This is the trigger — be specific about the
  phrases and situations that should fire it, or the agent won't reach for it.
---

# My Workflow

Imperative steps the agent follows...
```

Keep `SKILL.md` short; put long reference material in a sibling file it points to.

## Cross-CLI

This directory is tool-neutral on purpose (same idea as `AGENTS.md`) — one source of truth
every agent can use, not tied to one CLI. Agents read the relevant `SKILL.md` here as
plain instructions. Claude Code auto-discovers them through the `.claude/skills` symlink
that points here; another CLI can point its own skills path at this directory the same
way.
