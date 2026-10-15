# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Research

**Researched:** 2026-10-14
**Domain:** gate measurement protocol (macOS wall time under a pre-registered idle rule), a `PIP_CONSTRAINT` install probe in a linked git worktree, and ledger housekeeping (decision log, idea and debt files, README, a project skill). No production code, no new package.
**Confidence:** HIGH for the mechanics (every Makefile, hook, test and file shape below was read this session); MEDIUM for how long the idle waits take on this host (it read load 1.88 to 2.18 with a session open); LOW only where tagged `[ASSUMED]`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- Re-sweeping the xdist knee on the 18-CPU host — already in REQUIREMENTS.md "Form
  follow-ups"; D-08 confirms it stays there and L43 names the stale knee.
- The CI runner's move to Ubuntu 26 on 2026-10-19
  (`docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`)
  is adjacent, not this phase's: if this phase's PR is the first CI run after that date, its
  `Set up job` log is read whole and classified per that debt file before any fix, and the
  reading of CI's wall time is context only (15 D-02).
- IN-01, IN-02 and IN-04 of the Phase 19 review stay open on their own trigger.

None of these came up as new scope — discussion stayed within the phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-gate-rule-pre-registered | Before any reading, `bench/RESULTS.md` carries the idle threshold, cool-down, N >= 5 per arm, give-up rule and A/B design, and says it is a new method | Rule section shape, the wait and run recipes, the pre-registration ordering checks, the gaps in D-01..D-06 that the rule must close (per-run hang cap, first-wait expiry, host identity) |
| REQ-gate-bar-reset | Readings recorded with load, machine and `HEAD`; the human sets the bar; one `Lxx` amends L34; stale `63.555 s` / `~64 s` sentences rewritten and IN-03 retired in the same commit | Readings section shape, statistics snippet, L43 shape (read from L34, L41, L42), the exact stale lines (one more file than CONTEXT names), the IN-03 sha paradox |
| REQ-venv-constraint-probe | `make venv` under `PIP_CONSTRAINT` in a linked worktree, never the main checkout; `make verify` line, `pip check`, freeze diff recorded; green adds the constraint to `$(STAMP)` | Probe script, measured freeze delta (four moves, not three), the `tests/test_hooks.py` breakage that a green `$(STAMP)` prerequisite causes, hook-shim before/after checks |
| REQ-pi5-claim-softened | README states the hardware every number came from and makes no Pi 5 claim without a measurement; idea retired | Exact README lines and the two README-reading tests that must keep passing |
| REQ-reverify-recipe | Paragraph in `HOW_TO_DEVELOP.md` section 6, or `.ai_skills/reverify-phase` if the loop hit three times; idea retired | The count read from the record (verified), the skill shape, and a finding that GSD 1.16.0 now routes a stale report itself, which the skill must not contradict |
</phase_requirements>

## Summary

This phase writes almost no code. It is a measurement protocol, one amendment to the decision log, one install probe and three ledger retirements, and almost every risk is a **sequencing or bookkeeping** risk, not a technical one. The mechanics CONTEXT.md relies on all exist and behave as it says: `$(HOOKS)` skips `pre-commit install` in a linked worktree, `worktree.new` branches off the current branch into the gitignored `.claude/worktrees/`, `PYTEST_ADDOPTS` is the one spelling of arm A that the hook pin does not read, and the hook shims at `.git/hooks/` name `.venv/bin/python` on line 6. On the current `HEAD` the suite collects **1317** tests, of which `tests/test_browser.py` holds **2**, so arm A should read `1315 passed` and arm B `1317 passed`.

Eight things in CONTEXT.md's plan do not hold as written or are missing, and the planner must resolve them (they are collected under "Planner alerts" below). The two that change task structure: (1) CONTEXT's discretion note orders "L43, then the probe", but L43 must carry the probe's outcome and L34 is amended once, so the probe must come **before** the L43 commit; (2) a green probe adds `requirements.txt` as a prerequisite of `$(STAMP)`, which **turns two tests in `tests/test_hooks.py` red** (a throwaway repo without a `requirements.txt` makes `make` stop with "No rule to make target"), so green needs a test edit in the same commit, contrary to "the only recipe change is `$(STAMP)`". Two more are factual corrections: the freeze diff has a **fourth** predicted move (`fonttools`), and GSD 1.16.0 (`#4682`) now routes a stale `VERIFICATION.md` back through `/gsd-execute-phase`, which is the reason the idea's hand recipe exists, so the `reverify-phase` skill should be confirmed with the human before it is written.

**Primary recommendation:** Commit order is rule (alone) -> readings under the rule, nothing else committed during them -> probe (after the last reading) -> human bar checkpoint -> one L43 commit (bar, probe outcome, stale figures, IN-03, and on green the `$(STAMP)` change with its test fix) -> Pi 5 commit -> reverify commit. Keep the measured `HEAD` fixed at the rule commit by landing every ledger and doc change after the last reading, and prove "no production code moved" with a `git diff --name-only` pin.

## Planner alerts (read these before splitting plans)

| # | Alert | Evidence | What to do |
|---|-------|----------|------------|
| P1 | **Ordering: the probe goes before L43.** CONTEXT "Claude's Discretion" lists "...the bar checkpoint, then L43, then the probe". But D-14 makes L43 carry "the probe's outcome and, on green, the widened CI sentence", and the roadmap says L34 is amended once. L43 cannot be written before the outcome exists without a second amendment. | CONTEXT D-14; ROADMAP Phase 25 goal ("L34 is amended once") | Order: rule -> readings -> probe -> bar checkpoint -> L43 commit. The probe still comes only after the last reading (SC4). |
| P2 | **A green probe breaks `tests/test_hooks.py`.** Adding `requirements.txt` to `$(STAMP)`'s prerequisites makes `make .venv/.hooks-installed` fail in the two tests that copy the Makefile into a throwaway repo holding only `pyproject.toml` and `.pre-commit-config.yaml` (`test_the_hook_stamp_installs_from_the_main_checkout_and_never_from_a_linked_worktree`, `test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set`). Reproduced in scratch: `make: *** No rule to make target 'requirements.txt', needed by '.venv/.installed'.  Stop.` and `exit 2`; with an empty, old-mtime `requirements.txt` it reads `'.venv/.installed' is up to date.` and `exit 0`. | `tests/test_hooks.py:180-182,225-227` (read this session); scratch reproduction 2026-10-14 | On green the L43 commit also edits those two tests to write a `requirements.txt` and `os.utime` it to the same old mtime as `pyproject.toml`. This is the one test edit in the phase; `git diff --name-only` pins must allow `tests/test_hooks.py` on green and nothing else. These two tests are in the commit slice (`tests/test_hooks.py` is not one of the five heavy files), so `make verify.fast` at commit catches it. |
| P3 | **The freeze diff has four predicted moves, not three.** `pip freeze` of the dev `.venv` against `requirements.txt`: `fastapi` 0.142.4 -> 0.141.1, `starlette` 1.7.0 -> 1.6.0, `uvicorn` 0.54.0 -> 0.53.0 **and `fonttools` 4.66.1 -> 4.65.0** (`fonttools` is a transitive of `ezdxf` and `matplotlib`, pinned in the closure). | `comm -23` of the sorted pins against the sorted freeze printed `fastapi==0.141.1`, `fonttools==4.65.0`, `starlette==1.6.0`, `uvicorn==0.53.0` (2026-10-14) | D-12's "any other line is recorded, not explained away" stands; re-read the list at probe time. Filter the editable line (`grep -v '^-e'`): the dev venv's is `-e git+ssh://git@github.com/halfb00t/spur.git@d6cb1f3...#egg=spur`, a different sha and path in a worktree. |
| P4 | **Dev tools float outside the closure, so a red probe may not be the constraint's fault.** The 31 pins are runtime only. `pytest`, `mypy`, `ruff`, `playwright`'s siblings resolve fresh: the dev venv has `mypy==2.4.0`, `ruff==0.16.10`, `pytest==9.1.1`; a new venv built later resolves whatever is newest that day. | `pip freeze` of the dev venv; PITFALLS VP-1 #7 | Classify a red `make verify` by the freeze diff first: a red caused by a floated dev tool is "not the pins", recorded as such, and still leaves the idea filed (the idea's own green test is a clean `make verify`). |
| P5 | **IN-03 cannot be closed "with the sha" inside the commit that closes it** (a commit cannot contain its own sha). Recent practice resolved this by naming the commit **subject**: the three latest resolved debt files read `Resolved in: fix(calc): name only the hex-ignored bore fields set away from their defaults`, `fix(gate): match unfinished-work markers with -w so the scan runs on macOS`, `docs(intel): correct the Python floor and gate duration; index L17–L35`. | `docs/tech_debt/resolved/*.md` lines 6; `docs/ideas/retired/*.md` `Retired in:` lines; SC3 says "closed with the sha" | Use the commit subject (the idea files' form, and the form the debt ledger already used three times). If the human insists on a sha, it needs a follow-up commit, which breaks "same commit"; surface it, recommend the subject. Note the squash-merge debt: shas on a phase branch do not survive onto `main` anyway (`2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`). |
| P6 | **A fifth file quotes the stale gate figure**, and CONTEXT's grep would still match it: `docs/architecture/packaging.md:44` reads `(~64 s warm on the 12-core dev host, `-n 8` with coverage; no Docker)`. The grep's file list is the three roadmap files plus README; the pattern `~64 s` also matches this line. | repo-wide `grep -rn -E '63\.555|~64 s|about 64 s'` (2026-10-14) | Rewrite `docs/architecture/packaging.md:44` in the L43 commit and add it to the SC3 search. Also: the pinned search matches the *literal* strings, so a "history" sentence in `Makefile:105` must not keep `about 64 s` (spell it "the then-measured gate" and cite L43) or the empty-output pin fails. |
| P7 | **Per-run hang cap is missing from the rule.** D-04's 15-minute cap bounds the *idle wait* only. A run can also hang with no failure (the open `must` debt: a whole-suite `make verify` "hung near the end with no failure" until the harness SIGTERMed it at 600 s). Without a pre-registered cap, a hung run decides the session. Also the Bash tool's foreground limit is 600 000 ms and the slowest gate read so far is 336.15 s (24-03). | `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`; bench/RESULTS.md 24-03 line | Add to the rule (before any reading): a per-run wall cap (recommend 15 minutes, about 2.7 times the slowest gate on record), a capped run is killed, kept as a red run classified against that debt, and counts against the attempt budget of 8. Needs the human's nod because it adds a number D-01..D-06 do not carry. |
| P8 | **If the first wait expires, stop and ask.** D-09's reason for the quieting checkpoint is that with other sessions open "the 15-minute cap would fire on every run and the whole session would be non-decisive". D-04 says an expired run goes ahead non-decisive. Run 1 expiring means the checkpoint failed; continuing burns up to 3 h. | CONTEXT D-04, D-09; Phase 13 `bar-1` sampled 30 times over 15 min and never saw three consecutive readings under 1.5 (bench/RESULTS.md:303-329) | Write into the rule: an expired wait before A1 returns to the D-09 checkpoint; after A1 the D-04 behaviour applies. Phase 13 met 1.5 in only 2 of 5 sessions on the M2 Max and this M5 Max host read 1.88 to 2.18 with one session open, so this is the schedule risk. |
| P9 | **Arm sizes on this `HEAD`:** `1317 tests collected` in total and `2` in `tests/test_browser.py`, so A (`PYTEST_ADDOPTS="--ignore=tests/test_browser.py" make verify`) prints `1315 passed` and B prints `1317 passed`. Put both in the rule so a mismatch is a red run by definition (21-07 saw 1225/1226 for the earlier file of one test). | `.venv/bin/python -m pytest --collect-only -q` (2026-10-14): `1317 tests collected in 2.00s`; `tests/test_browser.py` -> `2 tests collected in 0.07s` | Pin in the rule. If tests are added before the rule commit, re-collect. |
| P10 | **The venv under measurement is the unconstrained one.** The dev `.venv` carries `fastapi==0.142.4` etc., not the pins. The bar describes the gate on that venv. A fresh clone after green adoption builds a constrained venv. | `pip freeze`; D-13 | The host-state header records `pip freeze | grep -E 'fastapi|starlette|uvicorn|fonttools'` and the L43 says the bar was read on the pre-adoption venv. Nothing to re-measure (D-13). |
| P11 | **The host may not be the M5 Max.** Phase 22-24 readings were taken on the 12-CPU M2 Max (`bench.machine_facts()` read `12 CPUs, arm64, 32.0 GiB RAM` in 24-04) and Phase 19/21 on the 18-CPU M5 Max. The idle threshold 1.5 means different things on 12 and 18 CPUs. | bench/RESULTS.md 24-04 host state; this session `bench.machine_facts()` -> `18 CPUs, arm64, 64.0 GiB RAM` | The rule requires one host for all ten runs, the machine line and chip string on every run row, and says a host change voids the session. The bar is quoted for that host and never rescaled (GB-3, 19-09). |
| P12 | **D-07 is already satisfied.** The hex-warning fix is `1864bcd` (PR #37); the phase branch is cut from it (`git merge-base HEAD main` printed `1864bcdca18922fd5c649c58f04632b9ea0c1706`). The debt file is already under `docs/tech_debt/resolved/`. | git; `docs/tech_debt/INDEX.md` Resolved table first row | Do not schedule it. Note a new idea (`2026-10-14-hex-warning-names-fields-by-form-title.md`) exists; it is not this phase's. |
| P13 | **Reverify premise partly superseded upstream.** See "State of the Art" and Open Question 1. | `~/.claude/gsd-core/workflows/execute-phase.md:365-380`, `verify-work.md:664-668`, `VERSION` `1.16.0` | Confirm with the human before authoring the skill (CLAUDE.md "Stop and ask first": evidence conflicts). |

## Architectural Responsibility Map

This phase is not a multi-tier feature; the "tiers" are the repo's recording and enforcement layers. The map is here so the planner puts each change in the layer that owns it.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| The rule and the readings | `bench/RESULTS.md` (committed measurement record) | `.planning/phases/25-*/investigation/*.log` (kept logs, tracked like 24's) | Every earlier figure lives here; D-12/17 "reproducible from committed material". No `bench/` script: the gate runs are `make verify`, a committed target |
| The bar | Decision log (`L43`, amends L34) | `bench/RESULTS.md` `#### Gate decision` (the human's verbatim words) | L34 set the old bar; entries are append-only amendments |
| "No check enforces the bar" | Not enforced (ARCH 7.4, Makefile bench section D-16) | — | A wall-time assertion on shared hardware flaps; the bar is a recorded figure, the 30 s `verify.fast` kill (L36) stays the only enforced time |
| `PIP_CONSTRAINT` adoption | `Makefile` `$(STAMP)` recipe | `tests/test_hooks.py` (pins the stamp behaviour), CI `ci.yml` (already sets the env var; unchanged) | The install happens in the stamp recipe; the throwaway-repo tests copy the Makefile |
| Hook-shim integrity | `.git/hooks/*` shims written by `pre-commit install` (`$(HOOKS)`) | `tests/test_hooks.py` (both branches) | The probe must not rewrite them; checked by hashing before and after |
| Stale-figure comments | `Makefile`, `.pre-commit-config.yaml`, `docs/HOW_TO_DEVELOP.md`, `README.md`, `docs/architecture/packaging.md` | — | Prose claims the repo contradicts (IN-03) |
| Ledger closure | `docs/ideas/`, `docs/tech_debt/` + their `INDEX.md` | — | One commit per closure: status, subject, `git mv`, INDEX row |
| Reverify workflow | `.ai_skills/reverify-phase/SKILL.md` (via `.claude/skills` symlink) | `docs/HOW_TO_DEVELOP.md` section 6 pointer | Project skills live in `.ai_skills/` (README) |

## Standard Stack

No external package is added. The "stack" is the host tooling the protocol uses, every item probed this session.

### Core
| Tool | Version | Purpose | Why standard here |
|------|---------|---------|-------------------|
| `make` (GNU) | 4.4.1 | the gate, `worktree.new`, `venv` | The project's one command surface [VERIFIED: `make --version`] |
| `/usr/bin/time -p` | macOS BSD | wall seconds (`real 0.00` format) | The method of Phase 15 R3, 19-09, 21-07 [VERIFIED: ran it; prints `real`, `user`, `sys` to stderr] |
| `sysctl -n vm.loadavg` | macOS 27.0.1 | 1-minute load; prints `{ 2.18 2.38 2.83 }`, so field 2 is the 1-minute | Phase 13 D-05 / Phase 15 R2 [VERIFIED: ran it] |
| `pgrep -fl '[p]ytest\|[p]re_commit\|[m]ake verify'` | macOS | Phase 15 R1, prints nothing when no gate is alive | [VERIFIED: printed nothing, `rc=1`, with no gate running, also from inside a `bash -c` string that contains `make verify`] |
| `bench.machine_facts()` | `bench/__init__.py:19` | the host-state line | Prints `18 CPUs, arm64, 64.0 GiB RAM` here [VERIFIED: ran it from `.venv`] |
| Python | 3.12.15 (`python3.12` at `/opt/homebrew/bin/python3.12`; `.venv`) | `statistics`, `math` for min/median/max/mean/ceil | stdlib; no script needed |
| pip | 26.2.1 (`.venv`) | the probe | `PIP_CONSTRAINT` + `-c` for the same file together are accepted [VERIFIED: `PIP_CONSTRAINT=requirements.txt .venv/bin/python -m pip install --dry-run --no-deps --ignore-installed -c requirements.txt idna` printed `Would install idna-3.20`] |
| git | 2.56.0 | `worktree add`, ordering proofs | `extensions.worktreeConfig` is `true` and `core.hooksPath` unset in this checkout [VERIFIED: `git config`] |
| pytest / xdist / cov | 9.1.1 / 3.8.0 / 7.1.0 | the gate | Versions from the dev venv freeze [VERIFIED: `pip freeze`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| inline shell wait loop (D-discretion) | a `bench/` script | A script needs its own tests under `mypy --strict` for ~15 lines (Phase 15 Open Question 3 decided the same) |
| linked worktree for the probe (D-10) | scratch clone | Rejected by D-10: a second checkout no repo target covers |
| `PIP_CONSTRAINT` env at the top of the Makefile | `-c requirements.txt` on the install line (D-12) | Rejected: every pip call constrained, less visible |

**Installation:** none. **Version verification:** versions above are read from the live environment; no registry lookup applies because nothing is installed that `pyproject.toml` and `requirements.txt` do not already name.

## Package Legitimacy Audit

No external package is introduced by this phase. The probe installs `pyproject.toml`'s existing `[dev]` extras under the existing 31 pins in `requirements.txt`; no new name enters either file. **Packages removed due to [SLOP] verdict:** none. **Packages flagged as suspicious [SUS]:** none. The `package-legitimacy` gate was not run because there is no candidate name to check.

## Architecture Patterns

### System Architecture Diagram

```
 phase branch (cut from main@1864bcd)
        |
        v
 [25-01] rule commit R  (bench/RESULTS.md only)  -----------------------+
        |                                                               | git log orders R before every reading (SC1)
        v                                                               |
 [checkpoint D-09] human quiets host -> "go"  (uptime, who, ps, pgrep snapshots into host-state header)
        |
        v
  for pair in 1..5:                      (attempt budget 8 per arm)
     wait_idle (3 x 30 s samples < 1.5, pgrep clear, 15 min cap)  -> A_k  (PYTEST_ADDOPTS=--ignore=tests/test_browser.py make verify)
     wait_idle                                                    -> B_k  (make verify)
        red or hung run? -> keep whole log, classify, "#### Red runs", does not count
        |
        v
 [25-02] readings commit (RESULTS.md section + kept logs, HEAD recorded = R)
        |
        v   (host no longer needed; probe may load it)
 [25-03] probe in .claude/worktrees/venv-probe:  shim hash before -> PIP_CONSTRAINT make venv -> make verify
         -> pip check -> freeze diff -> shim hash after -> record -> worktree remove (branch delete = confirm)
        |
        v
 [checkpoint D-05] human accepts the pre-registered candidate or writes a number + reason  -> "#### Gate decision"
        |
        v
 [25-04] ONE commit: L43 (bar + host + method + stale knee + probe outcome [+ widened CI sentence])
         + stale figures x7 lines in 5 files + IN-03 closed + INDEX trigger edited
         + (green only) $(STAMP) constraint, tests/test_hooks.py fix, venv idea retired, HOW_TO_DEVELOP sentence
        |
        v
 [25-05] README hardware sentence + Pi 5 idea retired      [25-06] reverify skill + section 6 sentence + idea retired
```

### Recommended commit structure

```
bench/RESULTS.md                         # new "## The gate re-set (Phase 25)" appended after line 5543
  ### The rule (25-01)
  ### The host, before run 1 (25-02)     # bench.machine_facts(), versions, snapshots, pip freeze excerpt
  ### The gate, idle, A/B interleaved    # runs table, per-arm stats, #### Red runs, #### Gate decision
  ### The venv probe (25-03)
.planning/phases/25-.../investigation/   # 25-02-A-1.log ... 25-02-B-5.log, wait samples, probe logs (tracked, like 24's)
docs/architecture/decision_log.md        # L43 appended after L42 (now the last entry)
.ai_skills/reverify-phase/SKILL.md       # new
```

One concern per commit (CLAUDE.md; PITFALLS m-4: do not batch retirements). The pre-commit hook runs `make verify.fast` on each (about 15.6 s on the M2 Max in 24-04, under the 30 s kill). No commit is made between the first wait and the last run: a commit's hook is a gate-shaped load. Keep every log untracked until the readings commit; untracked files do not break `git status --porcelain --untracked-files=no`.

### Pattern 1: the wait (Phase 13 D-05's shape, D-02)
**What:** Three consecutive 30 s samples of the 1-minute load below 1.5 **and** R1 clear; the wait is the cool-down; 15-minute cap; load read before and after every run.
**When:** before every one of the ten runs.
**Example:**
```bash
# Source: Phase 13 D-05 / Phase 15 R1-R2 (bench/RESULTS.md:2246-2250), command shapes verified 2026-10-14
X=1.5; CAP=900; ok=0; t0=$(date +%s)
while :; do
  l1=$(sysctl -n vm.loadavg | awk '{print $2}')
  busy=$(pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify' | wc -l | tr -d ' ')
  if awk -v l="$l1" -v x="$X" 'BEGIN{exit !(l<x)}' && [ "$busy" = 0 ]; then ok=$((ok+1)); else ok=0; fi
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$l1" "$busy" "$ok" >> "$S/wait-$L.tsv"
  [ "$ok" -ge 3 ] && { echo IDLE; break; }
  [ $(( $(date +%s) - t0 )) -ge $CAP ] && { echo GAVE_UP; break; }
  sleep 30
done
```
The cap (900 s) is longer than the Bash tool's 600 000 ms foreground limit: start the loop with `run_in_background` and poll its file, or split it into resumable calls. [ASSUMED: the harness limit applies to the executor's Bash tool as it did to the Phase 21 orchestrator's gate, which was SIGTERMed at 600 s]

### Pattern 2: one run (R3 without the RSS sampler, D-06)
```bash
# arm B; arm A prefixes  PYTEST_ADDOPTS="--ignore=tests/test_browser.py"  to the same line
l_before=$(sysctl -n vm.loadavg | awk '{print $2}'); t_start=$(date -u +%FT%TZ)
/usr/bin/time -p make verify > "$LOG" 2>&1; echo "make verify exit $?" >> "$LOG"
t_end=$(date -u +%FT%TZ); l_after=$(sysctl -n vm.loadavg | awk '{print $2}')
real=$(awk '/^real /{print $2}' "$LOG")
```
Redirecting (not `| tee`) keeps the exit status; 24-04's logs end with `make verify.fast exit 0` in this form. Run it in the background and poll; a foreground call dies at 600 s. Result line: `grep -E '^=+ .* passed' "$LOG"` and the coverage `TOTAL` row; record `HEAD` from `git rev-parse --short HEAD` and `git status --porcelain --untracked-files=no` (empty, `.planning/STATE.md` and `state.json` excepted, as 24-04 did).

### Pattern 3: the statistics and the candidate (D-05)
```python
# Source: stdlib; L34's rule is "largest decisive run, rounded up to the next whole second"
import math, statistics as st
b = [...]  # decisive B `real` values
a = [...]  # decisive A `real` values
for name, xs in (("A", a), ("B", b)):
    print(name, min(xs), st.median(xs), max(xs), round(st.mean(xs), 2))
print("browser file idle cost, mean(B)-mean(A):", round(st.mean(b) - st.mean(a), 2))
print("candidate bar:", math.ceil(max(b)))   # worked check: [163.2,165.1,158.4,168.3,160.0] -> 169
```
With N = 5 the median is the third value. If an arm is short (a red used the budget) the median of an even count is an average: the rule should say so in advance.

### Pattern 4: the probe (D-10, D-11), after the last reading
```bash
# in the MAIN checkout, before:
H0=$(shasum -a 256 .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push)
sed -n 6p .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push   # each: INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python
make worktree.new SLUG=venv-probe        # branch agent/venv-probe off the CURRENT branch into .claude/worktrees/venv-probe
cd .claude/worktrees/venv-probe
PIP_CONSTRAINT="$PWD/requirements.txt" make venv > "$P/venv.log" 2>&1; echo "make venv exit $?" >> "$P/venv.log"   # expect the line "a linked worktree -- the hooks live in the main checkout's .git/hooks"
/usr/bin/time -p make verify > "$P/verify.log" 2>&1; echo "make verify exit $?" >> "$P/verify.log"   # NOT a gate reading
.venv/bin/python -m pip check
diff <(../../../.venv/bin/python -m pip freeze | grep -v '^-e' | sort) <(.venv/bin/python -m pip freeze | grep -v '^-e' | sort)
# back in the MAIN checkout, after:
cd ../../.. && [ "$H0" = "$(shasum -a 256 .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push)" ] && echo SHIMS_UNCHANGED
git worktree remove --force .claude/worktrees/venv-probe     # 1.4 GB .venv inside is untracked, so --force
# git branch -D agent/venv-probe  -> destructive: a confirm checkpoint, not an executor default
```
The `make venv` target is `venv: $(STAMP) $(HOOKS)`; in a linked worktree the `$(HOOKS)` branch prints the "linked worktree" line and only touches its own stamp [VERIFIED: Makefile:74-83 read; `tests/test_hooks.py:205-216` asserts it]. The probe's `make verify` also installs the headless shell (`$(BROWSER)`), about 16 s [CITED: Makefile:85-90 comment, 21-RESEARCH].

### Pattern 5: the ledger retirement (idea files)
Idea file: add `Status: retired` and `Retired in: <the commit's subject>` right after the `Date:` line (the shape of all four retired files), append a `## Outcome` section, `git mv` to `docs/ideas/retired/`, delete the row from the INDEX `## Open` table and append a row to `## Retired` (`| date | [title](retired/<file>) | <subject> |`). Debt finding (IN-03): the file stays in `active/`; mark the IN-03 bullet resolved with the commit subject, drop the `Makefile:152-156` entry from "Related files" (the lines have moved), update "Next step", and delete the `; the L34 bar is re-set under a new `Lxx` (IN-03)` clause from the INDEX trigger.

### Pattern 6: the `Lxx` shape
L34, L41 and L42 all read: `## Lnn — <claim> (amends/follows ...)`, `Date: ...`, a paragraph saying what stays as written, bold-led paragraphs, `**Reversibility.**`, `Reason:`, and a closing `Machine:` line giving CPUs, chip, RAM, macOS, Python, versions and the dates read. L43's title must contain `amends L34`. Next free number: the last entry is `## L42` at `decision_log.md:2711` and `grep` finds no `## L43` [VERIFIED].

### Anti-Patterns to Avoid
- **Committing between runs.** The commit hook is a `make verify.fast` (eight workers) and lifts the load; it also dirties `HEAD`. Write nothing tracked until after run B5.
- **`| tee` around the gate.** Loses the exit status; a red run would look green in the table.
- **Averaging a non-decisive run into the bar.** It counts for the record, never for the bar (D-04).
- **Tuning X, the candidate rule, or N after seeing a number.** That is the "tuned toward a pass" L08 and L34 forbid; a different X is a new rule and a new session.
- **Running `make venv` or `make verify` in the probe while a reading is pending.** It loads the host for minutes.
- **Editing `requirements.txt` or `docker/refresh-requirements.sh` in this phase.** After green, a newer `requirements.txt` re-stales `$(STAMP)` and every clone reinstalls 1.4 GB; and a header edit in the script is a second concern.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-arm statistics | a `bench/` script with tests | `statistics` + `math.ceil` inline (Pattern 3) | Phase 15 Open Question 3: a script needs mypy-strict tests for a few lines |
| Idle detection | a custom poller daemon | the Pattern 1 loop, recorded verbatim in the rule | Phase 13 D-05 precedent; the discretion note in CONTEXT |
| Hook-shim integrity | reading `pre-commit`'s internals | `shasum -a 256 .git/hooks/{pre-commit,commit-msg,pre-push}` before and after, plus `sed -n 6p` | Byte equality is stronger than the one line `INSTALL_PYTHON=`; all three shims carry that line on 6 [VERIFIED: all three read] |
| Freeze comparison | hand-diffing 91 lines | `diff` of two sorted `pip freeze` outputs minus `-e` lines | The editable line differs by sha and path in a worktree |
| Isolating the probe | a second clone | `make worktree.new SLUG=venv-probe` | The Makefile already skips the hook install there and `.claude/worktrees/` is gitignored [VERIFIED: `.gitignore:19-20`] |
| A "verifier re-run" | hand-writing `covered_digest` | the verifier agent (or the owner's route) | Hand-writing a digest asserts a check nobody ran (idea file, L08's spirit) |

**Key insight:** every artefact this phase produces is a record, and the record's value is its order and its honesty. Prefer committed prose plus `make` targets over new code.

## Runtime State Inventory

Not a rename or migration phase, but the probe and the retirements touch state that lives outside the files. All five categories answered:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None: no database, cache or datastore holds a renamed string. The stale figures are prose only | none (verified by the repo-wide grep that found only text files) |
| Live service config | None. CI's `ci.yml` already sets `PIP_CONSTRAINT: requirements.txt` and is untouched (a duplicate of the Makefile's `-c` on green is harmless: pip accepted the pair, see Standard Stack) | none |
| OS-registered state | The three git hook shims in `.git/hooks/` (`pre-commit`, `commit-msg`, `pre-push`), each with `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python` on line 6, written 14 Oct 14:08 | Hash before and after the probe; never run `make venv` in the main checkout. Note: editing `.pre-commit-config.yaml` (the stale-figure comment, L43 commit) makes `.venv/.hooks-installed` stale, so the **next** `make` in the main checkout re-runs `pre-commit install` and rewrites the shims with the same python. That is expected, so keep the probe's before/after pair before that edit |
| Secrets/env vars | `PIP_CONSTRAINT` (probe only, set for the one `make venv` call), `PYTEST_ADDOPTS` (arm A only, set for the one command), `PLAYWRIGHT_BROWSERS_PATH` (exported by the Makefile, per venv) | Do not `export` any of them in a persistent shell |
| Build artifacts / installed packages | main `.venv` stamps: `.installed` and `.hooks-installed` 14 Oct 14:08:56, `.browser` 14:35:54, all newer than `requirements.txt` (6 Oct 09:49) and `pyproject.toml` (11 Oct); the probe worktree's own 1.4 GB `.venv`; branch `agent/venv-probe` | Confirm stamps are fresh before A1 (`make -n verify` must print no `pip install` or `playwright install`, else A1 pays an install); remove the worktree after the probe; branch deletion is a human confirm |

## Common Pitfalls

### Pitfall 1: A reading that starts on a cold or stale stamp
**What goes wrong:** If any stamp is stale, run A1 pays `pip install` or the browser download and reads high, which biases B minus A.
**Why it happens:** `$(STAMP)` depends on `pyproject.toml`; `$(HOOKS)` on `.pre-commit-config.yaml`; `$(BROWSER)` on `$(STAMP)`. A branch switch or checkout can move mtimes.
**How to avoid:** Before A1: `make -n verify | grep -E 'pip install|playwright install|pre-commit install'` prints nothing. `make -n test | grep -o -- '-n [0-9]*'` prints `-n 8` [VERIFIED today].
**Warning signs:** A1 more than a minute above the others.

### Pitfall 2: The load never reaches 1.5
**What goes wrong:** Every wait hits the 15-minute cap and the session yields ten non-decisive runs.
**Why it happens:** This host reads 1.88 to 2.18 with one agent session, iTerm2, WindowServer, iStat and a browser open (`ps` top: iTerm2 15.9 %, WindowServer 7.8 %, claude 6.9 %); 11 users are logged in; Phase 13's `bar-1` never produced three consecutive samples under 1.5 in 30 tries.
**How to avoid:** The D-09 checkpoint is the control. Per P8, return to it if A1's wait expires. Record the snapshots.
**Warning signs:** the first three samples are all above 1.8 after the human says `go`.

### Pitfall 3: The machine sleeps mid-run
**What goes wrong:** `real` includes sleep time; one run reads minutes high with no failure.
**Why it happens:** a laptop (`pmset -g batt` showed `AC Power`, 100 %, charged today) can display-sleep or system-sleep during a 90-minute unattended session.
**How to avoid:** [ASSUMED] start one `caffeinate -i` for the session (`caffeinate -i -w <pid of the session shell>` or a timed `-t 14400`) before run 1; it is not part of a measured command line. Record `pmset -g batt | head -1` in the host-state header (GB-1 item 3 asks for the power source).

### Pitfall 4: Resource-tracker flake and the 98 % hang read as reds
**What goes wrong:** A red run is silently re-run, or a hung run is waited on.
**Why it happens:** the flake reddens roughly 1 whole-suite run in 6 locally (GB-2 item 3; `must` debt), and the hang debt is open.
**How to avoid:** Keep every red's whole log; classify with `grep -c -E 'resource_tracker|ReentrantCall|ExceptionGroup' "$LOG"` (21-07's own test, which printed 0 for non-flake reds); budget 8 attempts per arm; add the per-run cap (P7).

### Pitfall 5: A green probe breaks the commit-slice tests
Covered in P2. The failing output the executor will see at the L43 commit's hook if the test fix is forgotten: `make: *** No rule to make target 'requirements.txt', needed by '.venv/.installed'.  Stop.` inside `CalledProcessError` from `tests/test_hooks.py`.

### Pitfall 6: README/packaging tests read the files being edited
`tests/test_cli.py::test_readme_export_examples_run` asserts `spur export -o everything.stl ...` and `spur export -o hob-root.stl --root-shape trochoid` are in `README.md`, and `tests/test_api.py::test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it` reads it too [VERIFIED: tests/test_cli.py:149-166, tests/test_api.py:190-191]. Neither file is in the commit slice (both are heavy), so the commit hook will not catch a README mistake; the push-time `make verify` will. Run both after any README edit: `make test PYTEST_ARGS="tests/test_cli.py -k readme tests/test_api.py -k root_form_d -n0 --no-cov -q"` (the Makefile comment documents `-n0 --no-cov` for partial runs).

### Pitfall 7: The README edit tempts adjacent fixes
`README.md:315` ("the four heaviest") and `docs/HOW_TO_DEVELOP.md:25-27` still list four heavy test files, while the slice now ignores five. That is real drift and **not this phase's**: CLAUDE.md says note the tangent and raise it afterwards. File it under `docs/tech_debt/active/` (nice) if the human wants it kept, in its own commit.

### Pitfall 8: The probe's "green" proves little
`test_the_fixture_was_captured_on_the_kernel_this_run_uses` already passes on the dev venv; the pins' arm64 wheels were measured in research (PITFALLS VP-1 says every one has a pure or macOS arm64 wheel). Record what the probe can show (no harm, the version delta, a clean `pip check`) and say in L43 what it cannot (arm64 Linux, the Pi, build requirements: pip 26.2 constraints no longer reach isolated build environments, so `hatchling` builds unconstrained). [CITED: PITFALLS.md VP-1 #5, pip news 2026-07-29 as quoted there]

### Pitfall 9: Commit timestamps carry `+06:00`
`git log --format=%cI` prints local offsets (`2026-10-13T10:36:42+06:00`). Compare the rule commit with the readings' `...Z` timestamps by epoch: `git log -1 --format=%ct <sha>` against `date -u -j -f '%Y-%m-%dT%H:%M:%SZ' '<UTC>' +%s` [VERIFIED: both commands ran].

## Code Examples

The `$(STAMP)` change on green (D-12), against the current lines `$(STAMP): pyproject.toml` (Makefile:45) and `$(PY) -m pip install -e '.[dev]'` (Makefile:53):
```make
$(STAMP): pyproject.toml requirements.txt
	...
	$(PY) -m pip install --quiet --upgrade pip
	$(PY) -m pip install -e '.[dev]' -c requirements.txt
```
The matching test edit (both throwaway-repo tests in `tests/test_hooks.py`, beside the existing `pyproject.toml` lines at 181 and 226 and the `os.utime` at 193 and 230):
```python
(main / "requirements.txt").write_text("", encoding="utf-8")
...
os.utime(checkout / "requirements.txt", (1_000_000_000, 1_000_000_000))   # as pyproject.toml, so $(STAMP) stays current
```
(In the first test the loop `for checkout in (main, worktree)` runs `os.utime` for both checkouts, so the worktree gets the file through `git add .` and the commit; the second test has one checkout.)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `/gsd-ship` and `/gsd-verify-work` could not refresh a stale `VERIFICATION.md`; the idea's recipe hand-dispatches `gsd-verifier` (GSD 1.14.0) | `verification.status` returns `stale` with `next_command: /gsd-execute-phase N`; execute-phase "resumes at the phase gates to re-run the verifier (#4682)", running `code_review_gate`, `regression_gate` and the verifier, and its text says the manual workaround "skipped all three, and that gap is the reason this route exists rather than telling users to spawn the verifier by hand"; `verify-work` itself runs that route for a stale report | GSD 1.16.0 (installed), after the idea file (2026-09-28) | The skill's recipe should lead with the owner's route and keep the hand dispatch as a fallback. Phase 24's report records `Re-verification: Yes, regenerated whole against the tree at fd4604c (#4682)` |
| pip constraints reach build environments | Constraints (including `PIP_CONSTRAINT`) no longer affect isolated build environments (pip 26.2) | pip news 2026-07-29 [CITED: PITFALLS.md VP-1 #5] | `hatchling` builds unconstrained; L34's "fails closed" evidence is for runtime pins only |
| L34's loaded-host method (loads 5-30, largest of three) | Idle-host, N = 5 per arm, interleaved, pre-registered | this phase | Different quantity; say so in the rule and L43 |

**Deprecated/outdated:** the idea file's "ship and verify-work never dispatch the verifier" premise; L13's "~11 s" (history, left as is per D-14); the dev-host-"12-core" qualifier on the gate figure.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The Bash tool's 600 000 ms foreground limit applies to the executor, so waits and runs must be backgrounded and polled | Patterns 1-2 | Low: if the limit is higher, a single call is simpler, nothing breaks |
| A2 | A session-level `caffeinate -i` prevents a sleep that would inflate `real`, and adds no measurable load | Pitfall 3 | Low: if skipped and the host sleeps, one run reads high and is classified a red/non-decisive run |
| A3 | A per-run cap of 15 minutes (about 2.7 times the slowest recorded gate, 336.15 s) is the right size | P7 | Medium: too short kills a legitimate slow run; the number is the human's to confirm, it is not research |
| A4 | Idle gate wall on this host will be roughly 100-250 s, so ten runs plus waits fit the 3 h cap (CONTEXT budgets 75-90 min) | Summary | Low: the 3 h cap is the hard stop either way |
| A5 | The README "hardware" sentence should name the two dev hosts (CONTEXT D-15 names the M2 Max and M5 Max) and no arm64 board | Ledger | Low: wording is the planner's |
| A6 | D-13's "venv paragraph" in `docs/HOW_TO_DEVELOP.md` means the `section 0` bullet at lines 30-32 (the only place that says to run `make venv`) | Open Question 2 | Low: wrong placement of one sentence |
| A7 | Leaving `ci.yml`'s `PIP_CONSTRAINT: requirements.txt` in place after green is harmless and not worth a second concern | Runtime State | Low: verified that pip accepts the env var plus `-c` of the same file |

## Open Questions

1. **Does the human still want the hand-dispatch recipe in `reverify-phase`?**
   - What we know: D-17 locks the skill and says it "carries the idea file's recipe"; the count is verified (Phase 9 twice per the idea file and its report, Phase 17 `0f1209f docs(17): re-verify the phase after the code review fixes`, Phase 23 and Phase 24 reports each say `Re-verification: Yes`). GSD 1.16.0 now routes a stale report through `/gsd-execute-phase N` (Phase 24 used it, `#4682`), and `verify-work` does the same.
   - What's unclear: whether the hand recipe (delta in the prompt, agent does not commit, commit by hand, then ship) is still better or only a fallback.
   - Recommendation: write the skill as: (1) `gsd_run query verification.status <phase_dir>`; (2) take the owner's `next_command`; (3) if the verifier is dispatched by hand, pass the delta (`git diff --stat <old-report-sha>..HEAD -- <covered files>`), do not let it commit, commit the report as `docs(NN): re-verify phase N after ...`, then `/gsd-ship N`. Ask the human at plan time, because D-17 and ROADMAP SC5 are worded for the hand recipe. Either way the skill meets the "three times" rule and the idea retires with the count.
2. **Where does D-13's sentence go?**
   - What we know: `docs/HOW_TO_DEVELOP.md` has no paragraph about the venv itself; `section 0` (lines 30-32) says to run `make venv` once in the main checkout, and the worktree paragraph (lines 105-112) says to `make venv` inside a worktree.
   - Recommendation: the `section 0` bullet; one sentence ("an existing `.venv` keeps its older resolve until `make clean && make venv`"). Green only.
3. **`Resolved in:` for IN-03: subject or sha?** See P5; recommend the subject.
4. **Should `docs/architecture/packaging.md:17-18` and `docs/CODING_VALUES.md:181` change on green?** They say the constraint is "CI's"; the "loose ranges for developer environments" wording of the second and `overview.md:58` stays true for `pyproject.toml` itself. Recommend: edit `packaging.md:17-18` only (it states who is constrained); leave `requirements.txt`'s generated header and `refresh-requirements.sh` alone (P-anti-pattern above).
5. **Does the rule pre-register a warm-up?** Interleaving fixed as A1 B1 ... A5 B5 puts A first after the quiet wait. With fresh stamps (Pitfall 1) and 64 GiB RAM the page cache is not a concern, so no warm-up is recommended, but the rule should say the choice was made before reading.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| GNU make | everything | yes | 4.4.1 | — |
| python3.12 | `make venv` (probe) | yes | 3.12.15 at `/opt/homebrew/bin/python3.12` | — |
| `/usr/bin/time`, `sysctl`, `pgrep`, `caffeinate`, `pmset` | readings | yes | macOS 27.0.1 | — |
| git | worktree, ordering proofs | yes | 2.56.0 (`extensions.worktreeConfig=true`, `core.hooksPath` unset) | — |
| pip | probe | yes | 26.2.1 (`.venv`) | — |
| Network to PyPI and the Playwright CDN | probe (`make venv`, `$(BROWSER)`) | yes (a pip dry-run fetched metadata today) | — | none: a red here is "no observation", not a failed pin |
| Disk | probe's 1.4 GB `.venv` | yes | 1.5 TiB free | — |
| `gh`, Docker, node | not needed | present | gh 2.102.0 | — |
| gsd tools (`resolve-model`, `verification.status`) | reverify skill dry read | yes | GSD 1.16.0; `resolve-model gsd-verifier` printed `"model": "sonnet"` | — |

**Missing dependencies with no fallback:** none. **Host condition (not a tool):** a quiet host. Today: load `2.18 2.38 2.83`, 11 users, 18 CPUs.

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation` absent from `.planning/config.json`, which holds only `workflow._auto_chain_active`, `use_worktrees` and `ui_safety_gate` plus `git.branching_strategy: phase`). This phase's "tests" are mostly commands over files and `git log`; `pytest` is exercised only through the gate and the two README-reading tests.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0, driven by `make` |
| Config file | `pyproject.toml` (`[tool.coverage.report] fail_under = 96`, `--strict-markers`) |
| Quick run command | `make verify.fast` (the commit hook; about 15.6 s on the M2 Max, 24-04) |
| Full suite command | `make verify` (reads `1317 passed` on this `HEAD`; B arm of the reading) |

### Standing invariants (run after EVERY task)
| Invariant | Command | Passing output | Failing output |
|-----------|---------|----------------|----------------|
| Fixtures untouched | `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json; echo rc=$?` | no diff, `rc=0` (clean at research time) | a diff hunk and `rc=1` |
| No production code moved | `git diff --name-only <R>^..HEAD -- src docker scripts pyproject.toml requirements.txt` where `<R>` is the rule commit | prints nothing | any path |
| Only the allowed tests moved | `git diff --name-only <R>^..HEAD -- tests` | red/no probe: nothing; green: only `tests/test_hooks.py` | any other `tests/` path |
| Measured `HEAD` stays the rule commit until the last reading | `git rev-parse --short HEAD` equals the `HEAD` column of every run row | same short sha on all ten rows | a different sha on any row (ledger edits leaked in) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-gate-rule-pre-registered | The rule section exists, alone, with every element, and precedes the first reading | git-log + grep | see below (V1-V5) | Wave 0: section does not exist yet |
| REQ-gate-bar-reset | Ten (or fewer, recorded) decisive rows with load, machine, `HEAD`; per-arm min/median/max; the human's words; L43; stale figures gone; IN-03 closed | grep + arithmetic | see below (V6-V12) | Wave 0 |
| REQ-venv-constraint-probe | Probe ran in a worktree after the last reading; shims unchanged; outcome recorded; on green `$(STAMP)` constrained and tests fixed | grep + hash + `make -n` + pytest | see below (V13-V19) | Wave 0 |
| REQ-pi5-claim-softened | README hardware statement; no unmeasured Pi claim; idea retired | grep + file moves + pytest | see below (V20-V22) | Wave 0 |
| REQ-reverify-recipe | Skill present and discoverable (or paragraph), section 6 pointer, idea retired with the count | `ls`/`head`/grep | see below (V23-V25) | Wave 0 |

**V1-V5, the rule (SC1).** Shell variables: `R` = rule commit, `F` = first reading commit.
- V1 `R=$(git log -1 --format=%H -S'### The rule (25-01)' -- bench/RESULTS.md); test -n "$R" && echo ok` — failing: prints nothing (the heading is CONTEXT's, verbatim).
- V2 `git show --stat --format=%s "$R" | tail -n +2` — passing: exactly `bench/RESULTS.md | N +` and the summary line; failing: any other path (the rule was not committed alone).
- V3 element pins over the section: `S=$(awk '/^## The gate re-set \(Phase 25\)/{f=1} f' bench/RESULTS.md); for p in '1\.5' 'cool-down' 'N = 5' 'give-up|15-minute|15 minutes' 'interleav' 'tests/test_browser\.py' 'new method' 'Phase 15 D-04' 'candidate' '1315 passed' '1317 passed' 'PYTEST_ADDOPTS'; do printf '%s\t%s\n' "$p" "$(printf '%s' "$S" | grep -c -E "$p")"; done` — failing: any count `0`. (Run it at the rule commit with `git show "$R":bench/RESULTS.md` in place of the file so a later edit cannot mask a missing element.)
- V4 ordering by ancestry: `F=$(git log --reverse --format=%H -S'<the readings heading, e.g. "The gate, idle, A/B interleaved">' -- bench/RESULTS.md | head -1); git merge-base --is-ancestor "$R" "$F" && [ "$R" != "$F" ] && echo R_before_F` — failing: no output.
- V5 ordering by clock: `[ "$(git log -1 --format=%ct "$R")" -lt "$(date -u -j -f '%Y-%m-%dT%H:%M:%SZ' '<UTC start of A1>' +%s)" ] && echo rule_before_first_run` — failing: no output.
- Wait/stamp pre-check (before A1): `make -n verify | grep -E 'pip install|playwright install|pre-commit install'` prints nothing; `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'; echo rc=$?` prints `rc=1`.

**V6-V12, the readings, the bar, L43 (SC2, SC3).**
- V6 rows: `awk '/^## The gate re-set \(Phase 25\)/{f=1} f' bench/RESULTS.md | grep -c -E '^\| (A|B)[1-5] '` — passing: `10` (or fewer with an explicit "arm is short" sentence); each row must carry load before -> after, UTC start -> end, `HEAD` (`grep -E '^\| (A|B)[1-5] ' ... | awk -F'|' 'NF<9'` prints nothing).
- V7 result lines: arm A rows contain `1315 passed`, arm B rows `1317 passed`: `grep -E '^\| A[1-5] ' | grep -vc '1315 passed'` is `0` and `grep -E '^\| B[1-5] ' | grep -vc '1317 passed'` is `0`.
- V8 stats recompute: pull the `real` column per arm from the table and recompute min/median/max with Pattern 3; the section's printed figures must equal them. Failing: any mismatch (a hand-typed statistic).
- V9 the decision: `grep -n '#### Gate decision' bench/RESULTS.md` has a hit in the Phase 25 section and the next lines hold the human's verbatim words; `grep -c 'candidate' ` in the same section is at least 2 (pre-registered and applied). If the give-up rule fired: a sentence saying the host did not quiet.
- V10 one L43: `grep -c '^## L43 — ' docs/architecture/decision_log.md` prints `1`, `grep -c '^## L44' docs/architecture/decision_log.md` prints `0`, `grep '^## L43' docs/architecture/decision_log.md | grep -c 'amends L34'` prints `1`; L43 body contains the human's number and the candidate, `Machine:`, and (green) the sentence "every environment that claims to run the gate installs under the closure".
- V11 stale figures, the pinned search (SC3): `grep -n -E '63\.555|~64 s|about 64 s' Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md README.md docs/architecture/packaging.md; echo rc=$?` — passing: no lines and `rc=1` (at research time it prints seven lines: Makefile:105, Makefile:173, .pre-commit-config.yaml:10, HOW_TO_DEVELOP.md:21, :129, README.md:307, packaging.md:44, `rc=0`). Record the empty output in the commit's SUMMARY, as 21-06 did. Each rewritten line must cite `L43`: `grep -n 'L43' Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md README.md docs/architecture/packaging.md`.
- V12 IN-03: `grep -n 'IN-03' docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` shows a resolved marking and the commit subject; `grep -c 'IN-03' docs/tech_debt/INDEX.md` prints `0`; `grep -c -E 'IN-0[124]' docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` is at least `3` (the other findings stay open); the file is still in `active/`.

**V13-V19, the probe (SC4).**
- V13 never the main checkout: the probe log's `make venv` output contains `a linked worktree`, and `git worktree list` showed `.claude/worktrees/venv-probe` during the probe; `ls -d .venv-proof 2>/dev/null` prints nothing.
- V14 shims: `H0` equals the after-hash (Pattern 4), and `sed -n 6p .git/hooks/pre-commit` prints `INSTALL_PYTHON=/Users/half/git/halfb00t/spur/.venv/bin/python` before and after. Failing: a different hash or a path containing `.claude/worktrees` or `venv-probe`. Record both.
- V15 constraint in force: in the worktree, `.venv/bin/python -m pip freeze | grep -E '^(fastapi|starlette|uvicorn|fonttools)=='` reads `fastapi==0.141.1`, `starlette==1.6.0`, `uvicorn==0.53.0`, `fonttools==4.65.0` (re-read at probe time). A different value means the constraint did not reach the install.
- V16 recorded outputs: the `### The venv probe (25-03)` section has pip version, the literal `PIP_CONSTRAINT` value (an absolute path), the `make verify` result line, its wall (marked "not a gate reading"), `pip check` output (`No broken requirements found.` on green), the freeze diff, shim line before and after, UTC start and end.
- V17 sequencing: probe start is after the last reading's end: `[ "<probe UTC start>" \> "<B5 UTC end>" ] && echo probe_after_last_reading` (same date, `Z` strings compare lexicographically), and the probe section is committed after the readings commit (`git merge-base --is-ancestor`).
- V18 green only: `grep -n -E '^\$\(STAMP\): pyproject.toml requirements.txt$' Makefile` has one hit and `grep -n -- "-c requirements.txt" Makefile` has one hit; the `pip install --upgrade pip` line is unchanged; `make -n -o .venv/.browser verify >/dev/null; echo rc=$?` is `0` and `make -n -W requirements.txt .venv/.installed | grep -c "pip install"` is at least `1`; `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q` ends `6 passed` (a red here prints the "No rule to make target" line).
- V19 red only: `$(STAMP)` untouched (`git diff <R>..HEAD -- Makefile` shows comments only), the failing pins are listed, the idea file is still in `docs/ideas/` with the outcome noted, and L43 does not contain the widened sentence.
- Optional green proof of the adopted line itself: from the main checkout `.venv/bin/python -m pip install --dry-run -e '.[dev]' -c requirements.txt` (no change to the venv) names the constrained versions in its `Would install` line.

**V20-V22, the Pi 5 claim (SC5).**
- V20 `grep -n -i 'raspberry' README.md` shows only lines that say the claim is not measured (e.g. "built for, not measured on"); `grep -n 'all work' README.md` prints nothing (today it prints line 40); `grep -n -E 'M2 Max|M5 Max' README.md` has a hit.
- V21 the README pins still hold: `make test PYTEST_ARGS="tests/test_cli.py -k readme tests/test_api.py -k root_form_d -n0 --no-cov -q"` passes (these two are outside the commit slice, so run them explicitly).
- V22 idea retired in the same commit: `test -f docs/ideas/retired/2026-09-22-measure-or-soften-the-pi5-claim.md && ! test -e docs/ideas/2026-09-22-measure-or-soften-the-pi5-claim.md`; `grep -n -E '^(Status: retired|Retired in: )' <file>` prints two lines; `awk '/^## Retired/{f=1} f' docs/ideas/INDEX.md | grep -c 'retired/2026-09-22-measure-or-soften'` prints `1` and `awk '/^## Open/{f=1} /^## Retired/{f=0} f' docs/ideas/INDEX.md | grep -c 'measure-or-soften'` prints `0`; `git show --stat --name-status -1 | grep -E '^R'` shows a rename.

**V23-V25, the reverify recipe (SC5).**
- V23 `ls .claude/skills/reverify-phase/SKILL.md` resolves through the symlink (`.claude/skills -> ../.ai_skills` exists); `head -5 .ai_skills/reverify-phase/SKILL.md` shows `---`, `name: reverify-phase`, `description:`; `wc -l` stays short (README: "Keep `SKILL.md` short").
- V24 the section 6 pointer: `awk '/^## 6\. PR/{f=1} /^## 7\./{f=0} f' docs/HOW_TO_DEVELOP.md | grep -c 'reverify-phase'` prints at least `1`, and the sentence sits within a few lines of the ship-note workaround (`[ci skip]`).
- V25 the dry read against the idea file (D-18): every command the skill names runs: `node ~/.claude/gsd-core/bin/gsd-tools.cjs query resolve-model gsd-verifier` printed JSON with `"model": "sonnet"`; `... query verification.status <phase_dir>` prints a `status`. The idea is retired (V22's checks on `2026-09-28-reverify-after-post-verification-fixes.md`) with the count: `grep -c -i 'five\|5 ' docs/ideas/retired/2026-09-28-reverify-after-post-verification-fixes.md` is at least `1`.

### Sampling Rate
- **Per task commit:** the four standing invariants plus the task's own V-pins; the commit hook runs `make verify.fast`.
- **Per wave merge / phase gate:** `make verify` once at the end (it will itself be a reading-shaped load, so it comes after the last reading and is not a bar reading) printing `1317 passed` (or the count after the test edit), coverage at or above 96, and `git status --porcelain --untracked-files=no` empty.
- **Before `/gsd-verify-work`:** every V-pin above, the empty stale-figure search recorded.

### Wave 0 Gaps
- [ ] `bench/RESULTS.md` section `## The gate re-set (Phase 25)` does not exist (the rule task creates it).
- [ ] `.planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/` does not exist (logs go there, tracked like 24's).
- [ ] No pytest changes are needed on red; on green `tests/test_hooks.py` needs the `requirements.txt` fixture lines (P2).
- [ ] No framework install: existing infrastructure covers everything.

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is enabled. This phase changes no code path, endpoint or input handling; the attack surface is unchanged. The relevant concerns are integrity of the developer toolchain and the dependency supply chain.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | the service has no authentication (open `nice` debt, unchanged) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | no | `GearParams` boundary unchanged; no field added |
| V6 Cryptography | no | none used; do not hand-roll hashing beyond `shasum` for the hook check |
| V14 Configuration / dependency integrity | yes | the closure pins (`requirements.txt`, 31 `==` lines) as pip constraints; `pip check`; no new package |

### Known Threat Patterns for this phase
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Hook shim rewritten to a deleted or foreign venv python (every later commit then runs the wrong interpreter or fails) | Tampering / Denial of service | never `make venv` in the main checkout; hash the three shims before and after; the `$(HOOKS)` linked-worktree branch (tested) |
| Dependency drift under loose ranges (a floating package changes behaviour between hosts) | Tampering | the `-c requirements.txt` constraint on green; record the freeze diff; do not claim it covers build requirements (pip 26.2) or dev tools |
| A 1.4 GB untracked venv committed by `git add -A` | Information disclosure (junk, paths) | probe inside gitignored `.claude/worktrees/`; remove the worktree afterwards |
| Destructive cleanup (`git branch -D agent/venv-probe`, `git worktree remove --force`) | Denial of service (lost work) | the worktree holds only the probe's venv; the branch delete is a human confirm checkpoint (CLAUDE.md "Stop and ask first") |
| Environment variable leaking into later commands (`PIP_CONSTRAINT`, `PYTEST_ADDOPTS`) | Tampering | set per command, never `export`ed in a persistent shell |

## Sources

### Primary (HIGH confidence): files read this session
- `/Users/half/git/halfb00t/spur/Makefile` (`$(STAMP)` :45-54, `$(HOOKS)` :74-83, `$(BROWSER)` :91-93, `verify` :106-108, `test` :169-170, `PYTEST_WORKERS` :166-167, `test.fast` :193-197, `worktree.new` :285-294)
- `/Users/half/git/halfb00t/spur/tests/test_hooks.py` (whole file)
- `/Users/half/git/halfb00t/spur/bench/__init__.py` (`machine_facts`), `bench/RESULTS.md` (sections 19-09 :4589-4694, 21-07 :5030-5167, 24-04 :5422-5543, Phase 15 :2208-2833, Phase 13 sessions :271-330, Phase 12 quiet-host wait :2052-2074)
- `.git/hooks/{pre-commit,commit-msg,pre-push}` (line 6 of each), `.gitignore:19-20`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `requirements.txt`, `pyproject.toml`
- `docs/architecture/decision_log.md` (L34 :1664-1790, L41-L42 tail), `docs/ideas/INDEX.md`, `docs/tech_debt/INDEX.md`, the three idea files, the IN-03 debt file, the retired idea files, resolved debt files
- `README.md:30-45,90-100,300-335`, `docs/HOW_TO_DEVELOP.md`, `docs/architecture/packaging.md`, `.ai_skills/README.md`
- `.planning/research/PITFALLS.md` (GB-1..3, VP-1, M-5, M-6, m-4), `.planning/research/ARCHITECTURE.md` section 7
- `~/.claude/gsd-core/workflows/execute-phase.md:355-395`, `verify-work.md:660-672`, `ship.md:65`, `VERSION` (`1.16.0`)
- Phase 23/24/17/9 `*-VERIFICATION.md` re-verification lines

### Commands run this session (read-only or dry-run; no gate, no `make venv`)
`sysctl`, `uptime`, `who`, `ps`, `pgrep`, `pmset`, `bench.machine_facts()`, `pip --version`, `pip freeze`, a pip `--dry-run` under `PIP_CONSTRAINT` plus `-c`, `pytest --collect-only`, `make -n` dry runs, `git config`, `git worktree list`, `shasum`, `gsd-tools query resolve-model|verification.status`, and one scratch reproduction of the `requirements.txt` prerequisite failure under the scratchpad directory.

### Secondary / Tertiary
- pip 26.2 constraint behaviour: `[CITED: .planning/research/PITFALLS.md VP-1 #5, quoting pip news 2026-07-29]`; not re-fetched.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, all tools probed live.
- Architecture (ordering, commit split): HIGH, derived from the roadmap's goal sentence and verified files; P1 is an inference from two locked texts and should be confirmed by the human only if they intended two amendments.
- Pitfalls: HIGH for P2, P3, P6, P9 (reproduced or measured); MEDIUM for the host-quiet risk (one host snapshot).

**Research date:** 2026-10-14
**Valid until:** 2026-10-19 for the CI runner (the `ubuntu-latest` move to Ubuntu 26 is the deferred item; if this phase's PR is the first CI run after that date, read its `Set up job` log whole before any fix); otherwise 30 days, or until `tests/`, the Makefile or GSD change.
