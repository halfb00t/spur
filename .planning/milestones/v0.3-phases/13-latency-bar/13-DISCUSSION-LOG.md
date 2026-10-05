# Phase 13: Latency Bar - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 13-latency-bar
**Areas discussed:** Investigation design, Session rules, Outcome (b) + record, SC3 concurrent protocol

Pre-discussion facts presented: the Dockerfile `HEALTHCHECK` cites measured p95s, not the
≤ 2× bar; `spur-spur-1` (:8000) and `fleet-user` (restart-looping) still run beside the
host; `pool.py`'s `wait_for` starts at submit so queue wait counts toward the timeout
(ASSUMPTION from code); the v0.3 roadmap lived only on `gsd/milestone-v0.3-start`.

---

## Branch (process question asked with the area selection)

| Option | Description | Selected |
|--------|-------------|----------|
| Land milestone-start first | PR for `gsd/milestone-v0.3-start`, `make pr.land`, then cut `gsd/phase-13-latency-bar` from the new `origin/main` (HOW_TO_DEVELOP §2) | ✓ |
| Cut phase branch from milestone-start | One PR carrying the three milestone-start commits | |
| Stay on milestone-start for now | Decide at plan-phase | |

**User's choice:** Land milestone-start first.
**Notes:** Done during the discussion: PR #15 opened, CI green (image, test (3.12),
vendor-bundle), landed via `make pr.land PR=15` → `origin/main` `9f26052`;
`gsd/phase-13-latency-bar` cut from it.

---

## Investigation design

### Which pair legs separate the three candidates for observation 1?

| Option | Description | Selected |
|--------|-------------|----------|
| Three pairs | A same server/same teeth; B same server, run 2 on teeth 180–189 (cold cache, warm workers); C restart between runs; split poller beside every run | ✓ |
| The two legs the debt file names | Restart pair + split-poller pair only | |
| Two legs, add B only if needed | Conditional third leg | |

**User's choice:** Three pairs.

### How is observation 2 (the ~0.1 ms floor) measured?

| Option | Description | Selected |
|--------|-------------|----------|
| Raw samples + sensitivity | JSONL samples, p95 at full precision to 3 dp, p94/p95/p96, samples at the timer quantum | ✓ |
| Raw samples + longer idle window | The above plus a 10 s idle window in the scratch harness | |
| Repeat-run spread only | Floor stated from printed p95 spread | |

**User's choice:** Raw samples + sensitivity.

### Where do the scratch harness and raw results live?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase dir, in the PR | Scripts, JSONL and per-run summaries under `.planning/phases/13-latency-bar/investigation/` | ✓ |
| Scratchpad only, write-up carries tables | 02's precedent (its scripts are gone) | |
| Phase dir, scripts only | Scripts committed, raw samples in the scratchpad | |

**User's choice:** Phase dir, in the PR.

### How many times does each pair run before its direction counts?

| Option | Description | Selected |
|--------|-------------|----------|
| Twice, directions must agree | 12 runs; a split is "not separable on this host"; predictions pre-registered | ✓ |
| Once per pair | Six runs, noise band stated | |
| Up to three, stop when two agree | 12–18 runs | |

**User's choice:** Twice, directions must agree.

---

## Session rules

### What makes a bar-demonstration session decisive?

| Option | Description | Selected |
|--------|-------------|----------|
| Wait, capped, else non-decisive | Three consecutive 30 s samples < 1.5, cap 15 min; on expiry run, record, mark non-decisive | ✓ |
| < 1.5 at start, no wait | 12 D-02's wording | |
| Any load, record as measured | The harness as it stands, whatever the host does | |

**User's choice:** Wait, capped, else non-decisive.

### `spur-spur-1` and `fleet-user` during the sessions?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep both, serve on :8001 | Same environment as Runs 1–8 | |
| Stop both for the sessions | Cleaner host; environment change recorded | |
| Keep spur-spur-1, stop fleet-user | Removes the restart loop only; still a recorded environment change | ✓ |

**User's choice:** Keep spur-spur-1, stop fleet-user.
**Notes:** Recommended option (keep both) not taken; the change is recorded in every
host-state header and the write-up (CONTEXT D-06).

### How many decisive sessions does outcome (a) get?

| Option | Description | Selected |
|--------|-------------|----------|
| One decisive session | One pair, no extra poller; either run over → (b) | ✓ |
| Two decisive sessions | Both must pass | |
| Pair A doubles as (a) | Investigation runs count if decisive | |

**User's choice:** One decisive session.

### Both scenarios in order, or `concurrent` only?

| Option | Description | Selected |
|--------|-------------|----------|
| Both scenarios, in order | `single` then `concurrent`, as Runs 1–8 | ✓ |
| concurrent only | Shorter; different inherited cache | |

**User's choice:** Both scenarios, in order.

---

## Outcome (b) + record

### How is (b)'s harness/bar change chosen?

| Option | Description | Selected |
|--------|-------------|----------|
| Cause-mapped first offer at a checkpoint | 12 D-03's shape; obs 1 → restart between runs, obs 2 → absolute threshold, MIN_SAMPLES only if n is the problem | ✓ |
| Fixed ranking, no checkpoint | Restart first, threshold second, MIN_SAMPLES last, no halt | |
| Checkpoint, no pre-agreed offer | All three open | |

**User's choice:** Cause-mapped first offer at a checkpoint.

### Shape of an absolute threshold if the floor survives?

| Option | Description | Selected |
|--------|-------------|----------|
| Ratio with an additive floor | pass = under-load p95 ≤ max(2.00 × idle, idle + M ms), M from the floor analysis | ✓ |
| Ratio, p95 reported at 3 dp | Report precision only | |
| Absolute ms on this host class | K ms, machine named | |

**User's choice:** Ratio with an additive floor.

### If (b)'s re-measurement also misses on both runs?

| Option | Description | Selected |
|--------|-------------|----------|
| Halt; debt stays active | Checkpoint; second change only by a second Lxx; otherwise close with the measurement, debt not retired, SC4 not met | ✓ |
| Record the measured ratio as the bar | Tuning toward a pass | |
| Accept with caveat again | L18 repeated | |

**User's choice:** Halt; debt stays active.

### Record shape at the close?

| Option | Description | Selected |
|--------|-------------|----------|
| One L32, amends L18 | One entry in L27–L31's shape; L18 untouched; PROJECT.md row at transition; Dockerfile comment sentence updated | ✓ |
| L32 for the bar only | Investigation and SC3 outside the log | |
| Two entries | L32 + L33 | |

**User's choice:** One L32, amends L18.

---

## SC3 concurrent protocol

### What are the ten concurrent builds?

| Option | Description | Selected |
|--------|-------------|----------|
| Worst row + nine other composed rows | Ten distinct keys; admission takes 4; affinity spreads over both workers | ✓ |
| Ten identical worst-row requests | One slot, serial; measures queue-wait semantics | |
| Both, two recorded rows | Two scenarios on separate fresh servers | |

**User's choice:** Worst row + nine other composed rows.

### What does RESULTS.md record?

| Option | Description | Selected |
|--------|-------------|----------|
| Per-request table + health ratio | Parameters, outcome, wall time; worst row vs 30 s; `workers_replaced` before/after; p95 ratio | ✓ |
| Worst-row time + counts only | The bare number | |

**User's choice:** Per-request table + health ratio.

### Where does the SC3 scenario live?

| Option | Description | Selected |
|--------|-------------|----------|
| bench/latency.py scenario, own commit | Third scenario reading `composed.json`, `test_bench` row, lands after the bar's session | ✓ |
| Script in the phase dir | No make target, no test | |
| One-off, command recorded | Not re-runnable | |

**User's choice:** bench/latency.py scenario, own commit.

### When and on which server?

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh server, after the bar sessions, same quiet rule | Own `make serve`; after the decisive session; 15-min cap | ✓ |
| Any time, load recorded | Whenever convenient | |

**User's choice:** Fresh server, after the bar sessions, same quiet rule.

---

## Claude's Discretion

- The pre-registered prediction table's final form; script and field names; whether
  `run_experiment.py` drives `make bench.latency` or imports the harness's functions.
- The write-up's section order within 02's shape; its file name.
- The host-state header's exact contents beyond Runs 7–8's set.
- The SC3 scenario's name, firing-order mechanics, per-request outcome source, and
  whether its poller samples feed the floor analysis.
- Plan order (investigation → write-up → decisive session → (b) checkpoint if reached →
  SC3 → record and retirement).
- Enforcement of a restart-between-runs rule if D-09 adopts it.

## Deferred Ideas

- Ten identical worst-row requests (queue-wait scenario) — not run; becomes a debt
  file's next step if SC3 shows a timeout terminating an in-flight build.
- Server-side admission for cache-hit sends — a `src/` change outside this phase if
  candidate (1) survives.
- L17's `mem_limit` re-sweep on v0.2 topology — stands from Phase 12.
- Refreshing `.planning/codebase/*.md` (dated 2026-09-21).
- A `make bench.latency SCENARIO=` selector — convenience only.
