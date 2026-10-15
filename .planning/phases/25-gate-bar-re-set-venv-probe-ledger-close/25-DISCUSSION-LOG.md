# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-14
**Phase:** 25-gate-bar-re-set-venv-probe-ledger-close
**Areas discussed:** Idle rule (decision 13), What HEAD gets measured, Venv probe mechanics, Ledger wording

Facts put in front of the human before the areas were chosen: host Apple M5 Max, 18 CPUs,
load 3.72 / 3.05 / 2.57 at 13:39 local with 11 users; 21-07 saw `fleet-client-cli` at 99 %;
Phase 13 met the 1.5 bar in 2 of 5 sessions; a gate run lifts the 1-minute load by ~13 and it
decays on a ~60 s constant; latest readings 192.94 s (19-09) and 163.96 s (21-07 arm B), both
loaded; L34's 66 s on a 12-CPU M2 Max; the reverify loop hit five times in the record (Phase 9
twice, 17, 23, 24); the hex-warning debt's trigger fired and says "fix as a /gsd-quick before
Phase 25's reading"; README:307 is a fourth stale `~64 s` site beyond the REQ's three files.

---

## Idle rule (decision 13)

### Idle threshold X

| Option | Description | Selected |
|--------|-------------|----------|
| 1.5, human quiets the host | Phase 12/13 precedent, no new number; the human closes other sessions and heavy processes; if the host never gets there the give-up rule fires and that is the finding | ✓ |
| 2.0 | Admits one idle Claude session beside the run; a new figure the Lxx must justify | |
| 3.0 | Likely met without preparing the host; proves only "nothing CPU-heavy" | |

**User's choice:** 1.5, human quiets the host.

### Sampling and cool-down shape

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 13 D-05 shape, per run | Three consecutive 30 s samples of 1-minute load under 1.5 and `pgrep` clear before every run; the cool-down is that same wait | ✓ |
| Fixed cool-down + one sample | Sleep 5 min after each run, one sample under 1.5 to start | |
| Idle gate once, then back-to-back | Meet 1.5 once, run all 10 consecutively (rejected by GB-1) | |

**User's choice:** Phase 13 D-05 shape, per run.

### N per arm

| Option | Description | Selected |
|--------|-------------|----------|
| N = 5 per arm, 10 runs | Meets the requirement; a real median; interleaved A/B | ✓ |
| N = 6 per arm, 12 runs | One more pair; even-count median | |
| N = 5 green per arm, reds extra | Same as the first, with the red-run rule stated | |

**User's choice:** N = 5 per arm, 10 runs. (The red-run rule was then asked separately.)

### Give-up rule

| Option | Description | Selected |
|--------|-------------|----------|
| 15 min cap per run, run anyway, non-decisive | Phase 13 D-05 shape; session cap 3 h; the human decides what the absence of an idle host means | ✓ |
| 15 min cap per run, stop, no reading | Nothing runs on expiry | |
| No cap, wait until idle | Blocks indefinitely (rejected by Phase 13) | |

**User's choice:** 15 min cap per run, run anyway, non-decisive.

### Bar statistic pre-registered?

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-register the candidate, human confirms or overrides with a reason | Candidate = max of decisive B runs rounded up; mean and median beside it; the human accepts or writes another number with the reason | ✓ |
| Human picks freely from the table | No candidate in advance | |
| Fully mechanical, no human number | Contradicts SC2 and L34's checkpoint | |

**User's choice:** Pre-register the candidate, human confirms or overrides with a reason.

### Does a red run count toward N = 5?

| Option | Description | Selected |
|--------|-------------|----------|
| No: attempt until 5 green per arm, every red recorded | 19-01 / 21-07 shape; classified against the recorded flake; attempt budget 8 per arm | ✓ |
| Yes: 10 attempts total, reds are gaps | Fixed wall budget; an arm may end at 4 | |

**User's choice:** No: attempt until 5 green per arm, every red recorded.
**Notes:** "Next area" chosen after this question.

---

## What HEAD gets measured

### Hex-warning /gsd-quick order

| Option | Description | Selected |
|--------|-------------|----------|
| Quick fix lands on main first, then Phase 25 branches off it | The reading measures the HEAD the milestone ships | ✓ |
| Measure main at 94dfc19 now; quick fix after | Shipped HEAD would differ from the measured one | |
| Fold the hex fix into Phase 25 | Scope creep; the rule commit would not be first | |

**User's choice:** Quick fix lands on main first, then Phase 25 branches off it.

### Decision 14: re-sweep the xdist knee?

| Option | Description | Selected |
|--------|-------------|----------|
| Stays deferred; record the stale knee in the Lxx | Bar describes the gate as shipped (-n 8) | ✓ |
| Reopen: sweep first, then the rule | ~1 h of gate runs and a Makefile change | |

**User's choice:** Stays deferred; record the stale knee in the Lxx.

### Who prepares the host?

| Option | Description | Selected |
|--------|-------------|----------|
| You quiet it; executor checkpoints before run 1 | Blocking checkpoint with `uptime`, user count and heavy processes printed; snapshot recorded | ✓ |
| Executor starts whenever the gate releases | No checkpoint; the cap would fire every run with sessions open | |

**User's choice:** You quiet it; executor checkpoints before run 1.

### Keep Phase 15's R3 RSS sampler?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop it; wall time only | Nothing in this phase reads peak RSS | ✓ |
| Keep it as context | One more column per run | |

**User's choice:** Drop it; wall time only.
**Notes:** "Next area" chosen.

---

## Venv probe mechanics

### Where the probe venv lives

| Option | Description | Selected |
|--------|-------------|----------|
| Linked worktree via `make worktree.new SLUG=venv-probe` | `$(HOOKS)` skips the hook install there; `.claude/worktrees/` gitignored; `.venv` inside it | ✓ |
| Scratch clone in the scratchpad | Fully isolated; no repo target covers it | |

**User's choice:** Linked worktree via `make worktree.new SLUG=venv-probe`.

### Where the probe is recorded

| Option | Description | Selected |
|--------|-------------|----------|
| New `bench/RESULTS.md` section beside the gate reading | pip version, constraint value, result line and wall (not a gate reading), `pip check`, freeze diff, shim line before/after, UTC | ✓ |
| In the idea file only | A retired idea is a poor home for a cited measurement | |

**User's choice:** New `bench/RESULTS.md` section beside the gate reading.

### How `$(STAMP)` carries the constraint on green

| Option | Description | Selected |
|--------|-------------|----------|
| `-c requirements.txt` on the install line, `requirements.txt` a prerequisite | Scoped to `pip install -e '.[dev]'`; pip upgrade line unconstrained; equivalence with the env var noted in the Lxx | ✓ |
| `export PIP_CONSTRAINT` in the Makefile | Every pip call constrained; less visible | |

**User's choice:** `-c requirements.txt` on the install line, `requirements.txt` a prerequisite.

### Existing venvs after adoption

| Option | Description | Selected |
|--------|-------------|----------|
| Nothing forced; HOW_TO_DEVELOP says `make clean && make venv` picks it up | No new target or stamp trick | ✓ |
| Touch `pyproject.toml` or bump the stamp name | Forces a 1.4 GB reinstall on every clone | |

**User's choice:** Nothing forced; HOW_TO_DEVELOP says `make clean && make venv` picks it up.
**Notes:** "Next area" chosen.

---

## Ledger wording

### Shape of the softened Pi 5 sentence (README:39-40)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the arch list, add "built for, not measured on" plus a hardware statement | Pi stays as a build target; numbers attributed to the M2 Max and M5 Max dev hosts, none on an arm64 board | ✓ |
| Drop the Pi 5 from the list | Removes a true build-target fact | |
| Hardware statement only, no arch examples | Loses the Apple-silicon hint | |

**User's choice:** Keep the arch list, add "built for, not measured on" plus a hardware statement.

### README:307's stale `~64 s` as a fourth site

| Option | Description | Selected |
|--------|-------------|----------|
| Yes: README:307 gets the new bar and host in the L34 commit; README:96 untouched | Line 96 is a Phase 12 build-time figure, not a gate figure | ✓ |
| Yes, both README lines | Also re-attribute line 96 | |
| No: three files only, as the REQ says | README would still contradict the new Lxx | |

**User's choice:** Yes: README:307 gets the new bar and host in the L34 commit; README:96 untouched.

### Reverify fork (count = 5)

| Option | Description | Selected |
|--------|-------------|----------|
| `.ai_skills/reverify-phase` plus one §6 sentence pointing at it | The skill carries the idea file's recipe; §6 names it beside the ship-note workaround; the count recorded in the retirement | ✓ |
| Paragraph in §6 only | Contradicts the rule both files state | |
| Skill only, no §6 sentence | Nothing points a §6 reader at the skill | |

**User's choice:** `.ai_skills/reverify-phase` plus one §6 sentence pointing at it.

### How the skill is proved

| Option | Description | Selected |
|--------|-------------|----------|
| Dry read only: frontmatter valid, steps match the idea file, discovered via `.claude/skills` | No fake test | ✓ |
| Exercise it once in this phase | Fires only if a review finds something | |

**User's choice:** Dry read only.
**Notes:** "Next area" then "I'm ready for context" chosen.

---

## Claude's Discretion

- Plan split within the roadmap's fixed order.
- The idle-wait implementation (inline loop recorded verbatim is enough).
- RESULTS.md section titles; the exact D-09 snapshot commands beyond `uptime`, `who | wc -l`
  and the R1 `pgrep`.
- Wording of the rewritten stale-figure comments (history may stay as history if labelled;
  the current bar cites L43).
- Keeping the probe's `make verify` log beside the gate logs.

## Deferred Ideas

- Re-sweeping the xdist knee on the 18-CPU host (already in REQUIREMENTS.md "Form follow-ups").
- The Ubuntu 26 runner move on 2026-10-19 — adjacent CI debt, read whole before any fix if
  this phase's PR is the first run after it.
- IN-01, IN-02, IN-04 of the Phase 19 review stay on their own trigger.
