# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Context

**Gathered:** 2026-10-14
**Status:** Ready for planning

<domain>
## Phase Boundary

The gate is measured once, on the `HEAD` the milestone ships, under a rule committed to
`bench/RESULTS.md` before the first reading: an idle-host method (1-minute load under 1.5,
sampled the way Phase 13 D-05 sampled it, before every run), N = 5 green runs per arm,
interleaved A/B (the full gate without and with `tests/test_browser.py`), every red run
kept, a 15-minute give-up per run that marks the run non-decisive. The human sets the bar at
a checkpoint from min/median/max per arm against a pre-registered candidate (the largest
decisive B run rounded up to a whole second), accepting it or writing another number with a
reason. One `Lxx` (L43, the next free number) amends L34 with the bar, the host, the method,
the stale xdist knee and — if the probe is green — the widened CI sentence; the stale
`63.555 s` / `~64 s` / `about 64 s` sentences in `Makefile`, `.pre-commit-config.yaml`,
`docs/HOW_TO_DEVELOP.md` and `README.md` are rewritten and IN-03 retired in that commit.

After the last reading, `make venv` is probed under `PIP_CONSTRAINT=requirements.txt` in a
linked worktree (`make worktree.new SLUG=venv-probe`), never the main checkout; `make
verify`'s result line, `pip check`, the freeze diff and the hook shim's `INSTALL_PYTHON` line
are recorded; green adds `-c requirements.txt` and a `requirements.txt` prerequisite to
`$(STAMP)`, red records the failing pins and leaves the idea filed.

The small ledger closes: README states the hardware every number came from and makes no
Raspberry Pi 5 performance claim; the reverify loop — hit five times in the record — becomes
`.ai_skills/reverify-phase` with one sentence in `docs/HOW_TO_DEVELOP.md` §6 pointing at it.
Each idea and the IN-03 finding retire in the commit that closes them.

No production code moves: no `GearParams` field, no `calc`, `model`, `pool`, `app`, `cli` or
`app.js` edit; `git diff --exit-code tests/regression/pre_v0_2.json
tests/regression/golden_requests.json` is clean after every task. The only recipe change is
`$(STAMP)`'s constraint on green. The probe never runs during a reading; the xdist knee is
not re-swept; no Raspberry Pi is measured.

</domain>

<decisions>
## Implementation Decisions

### The rule, written before any reading (REQ-gate-rule-pre-registered; kickoff decision 13)
- **D-01:** **Idle threshold X = 1.5 on the 1-minute load, and the human quiets the host.**
  Phase 12/13's precedent, no new figure. The host reads 2.6–3.7 with agent sessions open
  (13:39 local, 11 users, `fleet-client-cli` at 99 % seen in 21-07), Phase 13 met 1.5 in 2
  of 5 sessions and Phase 15 saw ~2.0 with one Claude session open — so the number is met
  by closing other sessions and heavy processes, not by raising X. Rejected: 2.0 (a new
  figure the `Lxx` would have to justify against 1.5); 3.0 ("nothing CPU-heavy" is all it
  proves, closer to L34's loaded method than to an idle one). — **Reversibility:** costly
  once the rule commit exists — moving X after a reading is the "tuned toward a pass" L08
  and L34 forbid; a different X is a new rule and a new session of readings.
- **D-02:** **Phase 13 D-05's sampling, applied before every run.** A run (A or B) starts
  only after three consecutive 30 s samples of the 1-minute `sysctl -n vm.loadavg` read
  under 1.5 and `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'` prints nothing (Phase 15
  R1). The cool-down between runs is that same wait: a gate run lifts the 1-minute load by
  about 13 (19-09: 3.16 → 16.71) and it decays on a ~60 s constant, so the wait is minutes
  and is never a fixed number of them. Load is read before and after every run. Rejected:
  a fixed 5-minute sleep plus one sample (a run that starts the moment load dips passes a
  weaker check); one idle gate at session start then back-to-back runs (PITFALLS GB-1: each
  run's eight workers set the next run's starting load, so only run 1 would be idle).
- **D-03:** **N = 5 green runs per arm, interleaved A1 B1 A2 B2 … A5 B5, ten decisive
  runs.** Arm A is `PYTEST_ADDOPTS="--ignore=tests/test_browser.py" make verify` — 21-07's
  spelling, forced by the hook pin that reads the caller's `PYTEST_ARGS`
  (`docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md`); arm B is
  `make verify`. Both under `/usr/bin/time -p`, the recipe as committed (`-n 8 --cov`,
  15 D-02). A red run (the resource-tracker flake, the 98 % hang, anything else) never
  counts toward N and is never replaced silently: its whole log is kept, it is classified
  against the recorded flake occurrences and listed under `#### Red runs` with its node ids.
  Attempt budget 8 per arm; past that the arm is short and the record says so. Rejected:
  N = 6 (an even count makes the median an average; buys little against a 47 s spread);
  ten attempts total with reds as gaps (the bar would rest on fewer readings than the rule
  promised).
- **D-04:** **Give-up: a 15-minute cap on the idle wait per run; on expiry the run goes
  ahead and is marked non-decisive.** Phase 13 D-05's shape: the run is recorded with its
  load, counts for the record and never for the bar. Session cap 3 h of wall from the first
  wait. If any run is non-decisive, the record states that the host did not quiet, and the
  human decides what that means at the bar checkpoint (SC2) — including whether the
  decisive runs alone are enough to set a bar. Rejected: stop on expiry with no reading
  (loses the loaded figure as context); no cap (Phase 13 rejected it — a host with other
  agents on it may never release).
- **D-05:** **The bar candidate is pre-registered; the human confirms or overrides it with a
  written reason.** The rule text names the candidate: the largest `real` of the decisive B
  runs rounded up to a whole second (L34's shape), shown with min, median, max and mean per
  arm and mean(B) − mean(A) as the browser file's idle cost. At the checkpoint the human
  accepts the candidate or writes another number and the reason, verbatim, under
  `#### Gate decision` in `bench/RESULTS.md`; the `Lxx` carries both the candidate and the
  human's number. Never tuned toward a pass. Rejected: a free pick from the table with no
  candidate (nothing committed before the read — weaker against L08); a purely mechanical
  bar (contradicts SC2 and L34's human checkpoint). — **Reversibility:** costly — the
  candidate rule is in the rule commit; changing it after a reading is the thing the rule
  exists to prevent.
- **D-06:** **Wall time only.** Phase 15's R3 process-tree RSS sampler is dropped: the bar
  is wall seconds and nothing in this phase reads peak RSS. Per run the record carries the
  pytest result line, `real`, 1-minute load before → after, UTC start and end, and `HEAD`.
  The host-state header carries `bench.machine_facts()` (`bench/__init__.py:19`), Python /
  cadquery / cadquery-ocp versions, `PYTEST_WORKERS`, pip version, and the D-09 snapshot.
- **The rule commit** is a `bench/RESULTS.md` section (`## The gate re-set (Phase 25)`,
  `### The rule (25-01)`) carrying D-01 to D-06 and the A/B design, committed alone before
  any reading so `git log` orders them (SC1). It says in its first paragraph that this is a
  new method, not L34's (Phase 15 D-04 read loads of 5–30 and took the largest of three).

### What `HEAD` is measured (kickoff decision 14; sequencing)
- **D-07:** **The hex-warning `/gsd-quick` lands on `main` first, through its own PR; Phase
  25's branch is cut from that `main`.** Its trigger fired when the selector shipped
  (`470b78a`) and its file says "fix as a /gsd-quick before Phase 25's reading"
  (`docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`). The
  measured `HEAD` is then the phase branch after the rule commit — a docs-only delta from
  `main` — and is recorded beside every run. Rejected: measuring `94dfc19` now (the shipped
  `HEAD` would differ from the measured one by a `calc` change plus tests); folding the fix
  into this phase (a `calc` change inside a measurement phase, and the rule commit would no
  longer be first on the branch). — **Reversibility:** costly — a reading on one `HEAD`
  cannot be relabelled for another; it would be re-measured.
- **D-08:** **The xdist knee is not re-swept.** `PYTEST_WORKERS` stays 8 (the knee swept on
  12 CPUs; this host has 18) and the bar describes the gate as shipped. The `Lxx` names the
  stale knee as a known limit, and the re-sweep stays in REQUIREMENTS.md "Form follow-ups".
  Rejected: sweeping N ∈ {8, 12, 16, 18} first (about an hour of gate runs and a Makefile
  literal change, after which the bar would describe a new gate).
- **D-09:** **The human quiets the host at a blocking checkpoint before run 1.** The
  executor prints `uptime`, `who | wc -l` and the CPU-heaviest processes
  (`ps -Ao pid,pcpu,comm -r | head -n 8` and the R1 `pgrep`), the human closes other agent
  sessions and heavy processes and replies `go`; both snapshots go in the host-state header.
  Rejected: starting whenever D-02's gate releases (with other sessions open the 15-minute
  cap would fire on every run and the whole session would be non-decisive).

### The venv probe (REQ-venv-constraint-probe; kickoff decision 15)
- **D-10:** **A linked worktree, `make worktree.new SLUG=venv-probe`, with its own `.venv`.**
  `.claude/worktrees/` is gitignored, so no untracked 1.4 GB appears in the main tree
  (PITFALLS VP-1 #2); the Makefile's `$(HOOKS)` branch skips `pre-commit install` in a
  linked worktree and `tests/test_hooks.py` already proves both branches, so the shim at
  `.git/hooks/pre-commit` (`INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`,
  read 2026-10-14) is never rewritten. Inside the worktree:
  `PIP_CONSTRAINT="$PWD/requirements.txt" make venv` (an absolute path — pip resolves the
  variable against its own cwd), then `make verify` (result line and wall recorded, marked
  "not a gate reading", never entering the bar), `.venv/bin/python -m pip check`, and a
  freeze diff against the main `.venv`. From the main checkout, before and after:
  `grep INSTALL_PYTHON .git/hooks/pre-commit` must still name `.venv/bin/python`. The
  worktree is removed afterwards (`git worktree remove`); deleting its `agent/venv-probe`
  branch is a destructive step and is a confirm checkpoint, not an executor default
  (CLAUDE.md "Stop and ask first"). Timestamps place every probe step after the last
  reading (SC4). Rejected: a scratch clone in the scratchpad (isolated, but a second
  checkout with no repo target covering it).
- **D-11:** **Recorded as a `bench/RESULTS.md` section beside the gate reading**
  (`### The venv probe (25-0N)`): pip version, the `PIP_CONSTRAINT` value, the `make verify`
  result line and wall, `pip check`'s output, the freeze diff, the shim line before and
  after, UTC start and end. Rejected: the idea file alone (a retired idea is a poor home for
  a measurement the `Lxx` cites).
- **D-12:** **Green adds `-c requirements.txt` to the install line and `requirements.txt` to
  the stamp's prerequisites.** `$(STAMP): pyproject.toml requirements.txt` and
  `$(PY) -m pip install -e '.[dev]' -c requirements.txt`; the `pip install --upgrade pip`
  line stays unconstrained (pip is not in the closure). The `Lxx` notes that
  `PIP_CONSTRAINT` and `-c` reach the same pip call, so the probe proves the adoption, and
  carries the pip 26.2 caveat (PITFALLS VP-1 #5: constraints no longer reach isolated build
  environments, so `hatchling` builds unconstrained — L34's "a conflicting pin fails
  closed" is evidence about runtime pins only). Green means: `make verify` green, `pip check`
  prints "No broken requirements found.", and the freeze diff shows the moves the constraint
  predicts (at the research read: `fastapi` 0.142.4 → 0.141.1, `starlette` 1.7.0 → 1.6.0,
  `uvicorn` 0.54.0 → 0.53.0; re-read at probe time) — any other line is recorded, not
  explained away. Red: the pins that fail are recorded, `$(STAMP)` is untouched, the idea
  stays filed and L34's CI sentence does not widen. Rejected: `export PIP_CONSTRAINT` at the
  top of the Makefile (every pip call in the file constrained, less visible at the install
  line).
- **D-13:** **Existing venvs are left alone.** The dev `.venv` keeps its newer
  `fastapi`/`starlette`/`uvicorn` until `make clean && make venv`; one sentence in
  `docs/HOW_TO_DEVELOP.md`'s venv paragraph and in the `Lxx` says so. CI already runs the
  pins on Linux, and the dev venv passes the gate either way. Rejected: touching
  `pyproject.toml` or renaming the stamp to force every clone through a 1.4 GB reinstall
  plus the browser shell.

### The `Lxx` and the stale figures (REQ-gate-bar-reset; SC3)
- **D-14:** **One entry, L43, amends L34 once.** It carries: the bar and the human's words;
  the host (`bench.machine_facts()`), `HEAD`, UTC; the method as new (idle, D-01 to D-05)
  against L34's loaded one; min/median/max per arm and the browser file's idle cost
  (mean(B) − mean(A)); the stale knee (D-08); the probe's outcome and, on green, the widened
  CI sentence ("every environment that claims to run the gate installs under the closure")
  plus the pip 26.2 caveat; L36's 30 s kill and the `verify.fast` shape unchanged; L13's
  "~11 s" left as history. No check enforces the new bar (Makefile bench section D-16 and
  ARCH §7.4: a wall-time assertion on shared hardware flaps); the bar is a recorded figure.
  Rewritten in the same commit, each to cite L43 and the new reading: `Makefile:105`
  ("about 64 s … L34's 66 s bar"), `Makefile:173` ("63.555 s (L34)"),
  `.pre-commit-config.yaml:10` ("measured 63.555 s"), `docs/HOW_TO_DEVELOP.md:21` ("~64 s")
  and `:129` ("about 64 s"), `README.md:307` ("~64 s warm on a 12-core dev host"). The
  search `grep -n -E '63\.555|~64 s|about 64 s' Makefile .pre-commit-config.yaml
  docs/HOW_TO_DEVELOP.md README.md` prints nothing afterwards. IN-03 retires in the debt
  file (`docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`): its
  finding marked resolved with the sha; the file stays active for IN-01, IN-02 and IN-04 and
  its INDEX trigger loses the IN-03 clause.

### The small ledger (REQ-pi5-claim-softened, REQ-reverify-recipe; SC5)
- **D-15:** **README:39-40 keeps the architecture list and adds "built for, not measured
  on" with a hardware statement.** Shape: the image builds for `linux/amd64` and
  `linux/arm64` (Apple silicon, Graviton, Raspberry Pi 5); every performance number in the
  README and `bench/RESULTS.md` was read on the dev hosts named there (12-CPU Apple M2 Max,
  18-CPU Apple M5 Max), none on an arm64 board. The Pi idea retires in that commit
  (`Status: retired`, `Retired in:` the commit subject, `git mv` to `docs/ideas/retired/`,
  INDEX row moved). Rejected: dropping the Pi from the list (removes a true build-target
  fact); a bare architecture sentence with no named machines.
- **D-16:** **README:307 is rewritten in the L43 commit (D-14); README:96 is not touched.**
  Line 96's "12-core dev host" attributes a Phase 12 build-time reading that is still true
  for its host and is not a gate figure.
- **D-17:** **`.ai_skills/reverify-phase` plus one sentence in `docs/HOW_TO_DEVELOP.md` §6.**
  The record shows the loop hit five times — Phase 9 twice on 2026-09-28 (the idea's own
  source), Phase 17 (`0f1209f`), Phase 23 (`23-VERIFICATION.md` "Re-verification: Yes") and
  Phase 24 (`24-VERIFICATION.md` "Re-verification: Yes") — past the idea's and
  `.ai_skills/README.md`'s "three times / twice is a skill" rule. The skill carries the
  idea file's recipe: dispatch `gsd-verifier` (model from `gsd_run query resolve-model
  gsd-verifier`) with the phase dir, goal, requirement ids and the exact delta since the
  stale report (`git diff --stat <old-report-sha>..HEAD -- <covered files>`) and why it
  happened; the agent does not commit; the report is committed by hand as
  `docs(NN): re-verify phase N after …` (the pre-commit hook runs `make verify.fast`); then
  `/gsd-ship N`. §6's sentence sits beside the ship-note workaround and names the skill.
  The idea retires in that commit with the count written into its retirement. Rejected: a
  paragraph only (contradicts the rule both files state); the skill with no §6 pointer (a
  reader who hits the stale-report refusal finds nothing).
- **D-18:** **The skill is proved by a dry read, not a test.** Frontmatter has `name` and
  `description`; the steps match the idea file; `ls .claude/skills/reverify-phase/SKILL.md`
  resolves through the existing `.claude/skills -> ../.ai_skills` symlink. `SKILL.md` stays
  short per `.ai_skills/README.md`. Rejected: exercising it in this phase (fires only if a
  review finds something; not plannable).

### Planning-time amendments (2026-10-14; research findings, human answers at plan-phase)
- **D-19:** The reverify skill leads with the route the record shows working: a stale
  `VERIFICATION.md` is re-routed through `/gsd-execute-phase N` (GSD 1.16.0, #4682; Phase 24
  used it). D-17's hand dispatch of `gsd-verifier` with the delta stays in the skill as the
  fallback for when that route refuses. Amends D-17; the "five hits" count and the §6 sentence
  stand.
- **D-20:** On a green probe, the L43 commit also edits the `tests/test_hooks.py` fixtures that
  copy the `Makefile` into a bare repo so they copy `requirements.txt` beside it; without that,
  `$(STAMP): pyproject.toml requirements.txt` fails two of those tests with "No rule to make
  target 'requirements.txt'" (reproduced in 25-RESEARCH.md). A test fixture edit is not
  production code; `tests/regression/*.json` stay byte-unchanged. Amends D-12's "the only
  recipe change" sentence.
- **D-21:** Three additions to the rule, written in the rule commit before any reading: (1) all
  ten runs on one host, named in the rule (Phases 22–24 were read on the 12-CPU M2 Max, 19/21 on
  the M5 Max); (2) a 15-minute wall cap per gate run — a run past it is killed, red, kept and
  classified against the 98 % hang debt, never decisive; (3) if A1's idle wait expires, the
  executor returns to the D-09 quiet-host checkpoint instead of running non-decisive (later runs
  keep D-04's shape). Amends D-02 to D-04.
- **D-22:** IN-03 closes with the commit subject, not a sha — a commit cannot carry its own sha,
  and the last three files in `docs/tech_debt/resolved/` used the subject. Amends D-14.
- Settled from research without a human call: the probe runs before L43 (D-14 says L43 carries
  the probe's outcome, so the discretion bullet's "then L43, then the probe" is superseded —
  rule, readings, probe after the last reading, bar checkpoint, one L43 commit);
  `docs/architecture/packaging.md:44` also quotes `~64 s` and joins the D-14 sweep and its
  empty-search pin; `fonttools` 4.66.1 → 4.65.0 is a fourth predicted move beside `fastapi`,
  `starlette` and `uvicorn`; D-13's sentence goes in `docs/HOW_TO_DEVELOP.md` §0's venv
  bullet (no venv paragraph exists); D-07 is done — `1864bcd` (#37) is on `main` and is this
  branch's merge-base. Expected result lines on this `HEAD`: `1315 passed` (arm A),
  `1317 passed` (arm B).

### Claude's Discretion
- The plan split (rule / readings and bar / L43 and stale figures / probe / ledger), with
  the ordering fixed by the roadmap: rule commit first, then readings, then the bar
  checkpoint, then L43, then the probe (after the last reading), ledger items anywhere
  after the rule commit.
- The idle-wait implementation: an inline shell loop recorded verbatim in the rule section
  is enough (the gate runs themselves are `make verify`, a committed target — Phase 12
  D-17); a `bench/` script is not required for a wait loop.
- Section titles and numbering inside `bench/RESULTS.md`; the exact snapshot commands in
  D-09 beyond `uptime`, `who | wc -l` and the R1 `pgrep`.
- Wording of the rewritten comments in D-14 (history sentences such as `Makefile:105` may
  keep their past figure as history if they say so, but must cite L43 for the current bar).
- Whether the probe's `make verify` in the worktree is kept as a log file beside the gate
  logs (recommended: yes, same naming as the gate runs).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The phase and its requirements
- `.planning/ROADMAP.md` — Phase 25 goal, SC1–SC5, decisions 13–15, boundaries, fixed
  order (rule → readings → bar → probe after the last reading).
- `.planning/REQUIREMENTS.md` — REQ-gate-rule-pre-registered, REQ-gate-bar-reset,
  REQ-venv-constraint-probe, REQ-pi5-claim-softened, REQ-reverify-recipe; "Form follow-ups"
  (the xdist knee stays there).
- `.planning/research/ARCHITECTURE.md` §7.1–7.4 — the premise correction (L34 was loaded),
  the protocol additions, the two readings as different jobs, what the re-set edits.
- `.planning/research/PITFALLS.md` — GB-1 (no idle host unless you wait; the gate raises its
  own load), GB-2 (spread beats effect), VP-1 (hook clobbering, untracked venv, version
  moves, missing prerequisite, pip 26.2, "passes proves little").
- `.planning/research/SUMMARY.md` — "Where the Four Files Disagree" row 2 (idle re-set is a
  new method).

### The decisions this phase amends or applies
- `docs/architecture/decision_log.md` — L34 (the gate measured; 66 s on the 12-CPU M2 Max;
  the loaded method; CI installs the closure), L36 (the commit slice; 30 s; untouched),
  L39 (the browser test admitted; its 21-07 price; "Phase 25 sets the bar"), L08 (no
  plausible numbers), L12/L13 (closure and one definition of passing), L42 (the last entry;
  L43 is next).
- `.planning/milestones/v0.3-phases/15-the-gate-measured-and-pinned/15-CONTEXT.md` — D-02
  (absolute wall seconds on the dev host; CI as context only), D-04 (the loaded method this
  phase departs from), R1–R5 recipe.
- `.planning/milestones/v0.3-phases/13-latency-bar/13-CONTEXT.md` — D-05 (three consecutive
  30 s samples under 1.5, 15-minute cap, non-decisive marking): the sampling shape D-02 and
  D-04 copy.
- `.planning/phases/21-browser-test-of-the-viewer/21-CONTEXT.md` — D-12 (the N = 3 admission
  A/B sets no bar), and 21-07's `PYTEST_ADDOPTS` spelling for arm A.
- `.planning/phases/21-browser-test-of-the-viewer/21-07-SUMMARY.md` — the A/B that found no
  separable browser cost (B − A = −2.47 s inside a 47 s spread), the red-run handling.

### The record this phase extends
- `bench/RESULTS.md` — `### The gate, priced (19-09)` (host-state header and three-run table
  shape; 192.94 s mean), `### The browser test, priced (21-07)` (`#### Host state`,
  `#### Full gate, A/B interleaved`, `#### Red runs`, `#### Outcome`), `### The bore-shape
  step, priced (24-04)` (the latest readings), `## The gate, measured and pinned (Phase 15)`
  (the L34 reading this re-set supersedes on this host), the Phase 13 bar sessions (the
  quiet-gate sample tables).

### The ledger items this phase closes
- `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` — IN-03 (the
  Makefile comment quoting 63.555 s); IN-01, IN-02, IN-04 stay open.
- `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` — the probe's origin and its
  green/red branches.
- `docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md` — the recipe the skill
  carries; the "third time → skill" rule.
- `docs/ideas/2026-09-22-measure-or-soften-the-pi5-claim.md` — the claim and the soften
  branch.
- `docs/ideas/INDEX.md`, `docs/tech_debt/INDEX.md` — the rows that move; the retirement
  shape (`retired/`, `Status: retired`, `Retired in:`).
- `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` — the
  `/gsd-quick` that must land on `main` before this phase's branch is cut (D-07).
- `docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md` — why arm A
  is spelled with `PYTEST_ADDOPTS`.
- `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`,
  `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` — the
  two known red-run shapes every red is classified against.

### Project rules
- `CLAUDE.md` — the gate, the two standing rules, destructive operations need the human,
  retire-in-the-closing-commit, caveman for replies and plain prose for persisted text.
- `docs/HOW_TO_DEVELOP.md` — §0 (the `~64 s` sentence), §6 (the ship-note workaround the
  reverify sentence sits beside), the venv paragraph (D-13's sentence), the worktree
  paragraph (why a worktree needs its own `.venv`).
- `.ai_skills/README.md` — when a skill is warranted, the `SKILL.md` shape, the
  `.claude/skills` symlink.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Makefile` — `verify` (`verify.static test`), `test` (`pytest -n $(PYTEST_WORKERS) --cov
  --cov-report=term $(PYTEST_ARGS)`), `PYTEST_WORKERS` (8 clamped to online CPUs),
  `$(STAMP)` (`pyproject.toml` → `python -m venv`, pip upgrade, `pip install -e '.[dev]'`),
  `$(HOOKS)` (skips `pre-commit install` in a linked worktree, warns on `core.hooksPath`),
  `$(BROWSER)` (the headless shell under `$(VENV)/ms-playwright`), `worktree.new SLUG=`
  (branch `agent/<slug>` into `.claude/worktrees/<slug>`, gitignored), `clean` (removes
  `.venv`).
- `bench.machine_facts()` (`bench/__init__.py:19`) — the host-state line every RESULTS.md
  section opens with.
- `tests/test_hooks.py` — proves both `$(HOOKS)` branches and pins the `make -n verify`
  recipe (the reason arm A uses `PYTEST_ADDOPTS`).
- `bench/RESULTS.md` section shapes: host state, runs table (`Run | Result line | real (s) |
  1-minute load before -> after | UTC`), `#### Red runs`, `#### Gate decision` with the
  human's verbatim answer (Phase 15), `#### Outcome` (21-07).
- `.git/hooks/pre-commit` line 6, `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python`
  — the before/after check of D-10.

### Established Patterns
- A rule is committed before the number is read (L34's knee rule; 21 D-12; this phase's
  SC1), and `git log` is the proof.
- Readings carry load, machine, `HEAD` and UTC; bars from other hosts are quoted, never
  rescaled (19-09, 21-07).
- A red run is kept with its log and classified, never dropped or re-run in its place
  (19-01, 21-07).
- A human checkpoint sets the number, recorded verbatim (`15-CONTEXT.md` D-01 addendum,
  19-09 `accept-A`, 21-07 `accept`).
- An idea or debt item retires only in the commit that closes it: `Status`, sha or subject,
  `git mv`, INDEX row (CLAUDE.md; `docs/ideas/retired/` holds three examples).
- `Lxx` entries are append-only amendments: "amends L34" in the title, L34 left as written.

### Integration Points
- `bench/RESULTS.md` — new `## The gate re-set (Phase 25)` with the rule, host state,
  readings, red runs, gate decision, and `### The venv probe (25-0N)`.
- `docs/architecture/decision_log.md` — L43 appended after L42 (line 2682).
- `Makefile:105`, `Makefile:173`, `.pre-commit-config.yaml:10`, `docs/HOW_TO_DEVELOP.md:21`
  and `:129`, `README.md:307` — the stale figures; `Makefile` `$(STAMP)` on green.
- `README.md:39-40` — the Pi 5 sentence.
- `docs/HOW_TO_DEVELOP.md` §6 — the reverify sentence; the venv paragraph — the
  `make clean && make venv` sentence on green.
- `.ai_skills/reverify-phase/SKILL.md` — new; discovered through `.claude/skills`.
- `docs/ideas/`, `docs/tech_debt/` — three retirements and one finding closed.

</code_context>

<specifics>
## Specific Ideas

- Scale for the rule's expectations, not bars: the gate read 192.94 s mean (19-09, load
  4.03 → 9.06), 163.96 s B-arm mean (21-07, load 5.8–13.2), both on this M5 Max; L34's 66 s
  was read on a 12-CPU M2 Max at 63.555 s. Ten idle runs plus waits are budgeted at roughly
  75–90 minutes; the 3 h session cap in D-04 is the hard stop.
- The host at discussion time: Apple M5 Max (`Mac17,6`), 18 CPUs, load 3.72 / 3.05 / 2.57 at
  13:39 local with 11 users logged in; pip 26.2.1 in `.venv`; `fastapi` 0.142.4,
  `starlette` 1.7.0, `uvicorn` 0.54.0 installed against pins 0.141.1 / 1.6.0 / 0.53.0.
- The reverify count is a fact read from the record and is written into the idea's
  retirement: five hits across four phases (9 ×2, 17, 23, 24).
- The stale-figure search in D-14 is run and its empty output recorded in the L43 commit's
  SUMMARY, the way 21-06 recorded its exclusion pins.

</specifics>

<deferred>
## Deferred Ideas

- Re-sweeping the xdist knee on the 18-CPU host — already in REQUIREMENTS.md "Form
  follow-ups"; D-08 confirms it stays there and L43 names the stale knee.
- The CI runner's move to Ubuntu 26 on 2026-10-19
  (`docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`)
  is adjacent, not this phase's: if this phase's PR is the first CI run after that date, its
  `Set up job` log is read whole and classified per that debt file before any fix, and the
  reading of CI's wall time is context only (15 D-02).
- IN-01, IN-02 and IN-04 of the Phase 19 review stay open on their own trigger.

None of these came up as new scope — discussion stayed within the phase.

</deferred>

---

*Phase: 25-gate-bar-re-set-venv-probe-ledger-close*
*Context gathered: 2026-10-14*
