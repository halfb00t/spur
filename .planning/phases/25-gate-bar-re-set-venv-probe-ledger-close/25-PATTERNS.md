# Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close - Pattern Map

**Mapped:** 2026-10-14
**Files analyzed:** 16 (this phase moves no production code; all are docs, one Makefile recipe, one test fixture)
**Analogs found:** 16 / 16 (all tracked: `git ls-files` printed bench/RESULTS.md, Makefile, .pre-commit-config.yaml, docs/HOW_TO_DEVELOP.md, README.md, docs/architecture/packaging.md, tests/test_hooks.py; the idea/debt/retired files are tracked docs)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `bench/RESULTS.md` `## The gate re-set (Phase 25)` / `### The rule (25-01)` | measurement record (rule) | batch / pre-registration | `bench/RESULTS.md:2208-2250` Phase 15 intro + Host state + Method (R1-R5) | exact |
| `bench/RESULTS.md` host, readings, `#### Red runs`, `#### Gate decision` | measurement record | batch | `bench/RESULTS.md:5030-5165` (21-07: Host state, A/B table, Red runs, Outcome); `:2202-2207` (Gate decision) | exact |
| `bench/RESULTS.md` `### The venv probe (25-03)` | measurement record | request-response | `bench/RESULTS.md:5440-5475` (24-04 host-state + readings table) | role-match |
| `.planning/phases/25-*/investigation/*.log` | kept logs | file-I/O | `.planning/phases/24-bore-shape-selector/investigation/24-0N-*.log` | exact |
| `docs/architecture/decision_log.md` L43 | decision entry | append-only amendment | L34 (`:1664`), L39 (`:2328`), L42 (`:2711`; L41 `:2596`) | exact |
| `Makefile` `$(STAMP)` (green only) + comments `:105`, `:173` | config | build recipe | `Makefile` `$(HOOKS)` / `$(BROWSER)` blocks `:60-92` (comment style) | exact |
| `.pre-commit-config.yaml:10` | config comment | n/a | `Makefile:173` rewrite (same sentence class) | role-match |
| `docs/HOW_TO_DEVELOP.md` §0 `:21`, `:30-32`, §6 `:129` + reverify sentence | doc | n/a | §6 ship-note paragraph `:139-145` | exact |
| `README.md:39-40`, `:307` | doc | n/a | `README.md:36-42` itself | exact |
| `docs/architecture/packaging.md:44` | doc | n/a | `README.md:307` (same figure) | exact |
| `tests/test_hooks.py` two fixtures (green only) | test | file-I/O | same file `:175-195`, `:222-232` | exact |
| `.ai_skills/reverify-phase/SKILL.md` (new) | skill | n/a | `.ai_skills/README.md` "How to add one" template (no other skill exists) | role-match |
| `docs/ideas/{pi5,reverify,venv}` -> `retired/` + `INDEX.md` rows | ledger | file move | `docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md` + INDEX `## Retired` rows | exact |
| `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` (IN-03) + `docs/tech_debt/INDEX.md:38` | ledger | edit in place | `docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md` (subject form) | role-match |

## Pattern Assignments

### `bench/RESULTS.md` rule section (25-01)

**Analog:** Phase 15 intro, `bench/RESULTS.md:2208-2250`. Copy: a one-paragraph statement of method that names what differs from the prior one, a `### Host state` bullet list, a `### Method` list of numbered recipe steps R1..Rn.

**Opening-paragraph shape** (`:2210-2216`): "What this section measures ... The method is D-04's ... without a quiet bar ... the human sets the bar at 15-03's checkpoint". The Phase 25 first paragraph must say the opposite: a new method (idle, N=5 interleaved), not L34's (loads 5-30, largest of three).

**Recipe step shape** (`:2246-2250`):
```
- R1: before each run, `pgrep -fl '[p]ytest|[p]re_commit|[m]ake verify'` prints nothing -- ...
  (The bracketed first letters are `pytest|pre_commit|make verify` spelt so the pattern does not match the shell
  command line that holds it.)
- R2: read `sysctl -n vm.loadavg` and keep the 1-minute figure.
```
Put the Pattern 1 wait loop (RESEARCH Pattern 1) and Pattern 2 run recipe verbatim in the rule. Rule must also carry D-19 to D-21 additions: single host, 15-min per-run kill (red, classified against the 98% hang debt), first-wait expiry returns to D-09 checkpoint, expected result lines `1315 passed` (A) / `1317 passed` (B), median of an even count, candidate = `math.ceil(max decisive B real)`.

Rule commit must touch only `bench/RESULTS.md` (heading `### The rule (25-01)` is the `git log -S` anchor).

---

### `bench/RESULTS.md` readings (host state, runs table, red runs, gate decision)

**Analog:** `### The browser test, priced (21-07)`, `:5030-5165`.

**Host state block** (`:5040-5052`): bullets Machine (`bench.machine_facts()` + chip string via `sysctl -n machdep.cpu.brand_string`), Python/cadquery/cadquery-ocp/pytest versions + `PYTEST_WORKERS`, "Read <date>, <UTC window>", and an explicit idle/not-idle statement with `ps` evidence. Add pip version, `pip freeze | grep -E 'fastapi|starlette|uvicorn|fonttools'` (P10) and the D-09 snapshots.

**Runs table columns** (CONTEXT code_context): `Run | Result line | real (s) | 1-minute load before -> after | UTC` plus `HEAD` (D-06).

**Per-arm stats table shape** (`:5100-5106`):
```
| | A (no browser test) | B (`make verify`) | B - A |
| `real` mean | 166.44 s | 163.96 s | **-2.47 s** |
| `real` range | 145.50 to 192.59 s | 158.44 to 168.30 s | |
```
Extend to min / median / max / mean per RESEARCH Pattern 3.

**Red runs shape** (`:5113-5136`): table `Run | Log | Result line | real (s) | Load before -> after | UTC`, then bullets **What failed**, **Classification** (the `grep -c -E 'resource_tracker|ReentrantCall|ExceptionGroup'` test), **Re-run**, **Budget**.

**Gate decision shape** (`:2202-2206`):
```
### Gate decision

The human's verbatim answer to Task 2's checkpoint: "accept (Recommended)". The measured
**28.28s** delta against D-10's 30.0s line stands as recorded above; ...
```
Use `#### Gate decision` with the candidate, then the human's words verbatim and why. Outcome shape: `#### Outcome` ending `Human's answer: "accept" (option id ...), given <date> UTC.` (`:5165`).

**Arm A spelling** (21-07 `:5122-5136`): `PYTEST_ADDOPTS="--ignore=tests/test_browser.py" make verify`; never `PYTEST_ARGS=` (hook pin reads it).

---

### `bench/RESULTS.md` `### The venv probe (25-03)`

**Analog:** `### The bore-shape step, priced (24-04)`, `:5440-5475`: intro stating command and log naming (`.planning/phases/NN-*/investigation/NN-0M-name.log`, "every figure below is copied from it"), `#### Host state`, `#### Readings` table with a UTC start column. Fields per D-11: pip version, `PIP_CONSTRAINT` value, `make verify` result line + wall marked "not a gate reading", `pip check` output, freeze diff (four predicted moves: fastapi, starlette, uvicorn, fonttools), shim hash/`INSTALL_PYTHON` before and after, UTC start/end. Commands: RESEARCH Pattern 4.

---

### `docs/architecture/decision_log.md` L43

**Analog:** L34 (`:1664-1700`), L39 (`:2328`), L42 (`:2711`; ends of entries at `:2682-2710` show the tail shape).

**Header + preamble** (L34 `:1664-1668`):
```
## L34 — The gate is measured, runs on eight workers under a coverage floor, and CI installs the pinned kernel (amends L12 and L13)

Date: 2026-10-04.

L12 and L13 stay as written; this entry amends L13's "~11 s warm" and its unmeasured gate, ...
```
L43 title must contain `amends L34`; next number confirmed (last entry is L42, no `## L43`). Then bold-led paragraphs (`**The measured gate** (D-01 to D-08).`), the human's answer quoted verbatim (L34: `"knee-headroom N=8 bar=66 cuts=none before=244.59"`), `**Reversibility.**` (`:2689-2691`), `Reason:`, and a closing `Machine:` line:
```
Machine: 12 CPUs, Apple M2 Max, 32 GiB RAM (`sysctl -n hw.ncpu machdep.cpu.brand_string hw.memsize`, read
2026-10-11); macOS 27.0.1 (`sw_vers -productVersion`), Darwin kernel 27.0.0 (`uname -r`); Python 3.12.13, ...
```
Cite every figure to RESULTS.md section or plan; do not carry a figure between hosts (L42 preamble). Must contain: bar + human's words + candidate, method new vs L34, per-arm stats and browser idle cost, stale xdist knee (D-08), probe outcome (+ widened CI sentence and pip 26.2 caveat on green), D-13 existing-venv sentence, L36 30 s kill unchanged, L13 "~11 s" as history, "no check enforces the bar".

---

### `Makefile` (comments `:105`, `:173`; `$(STAMP)` on green)

**Analog:** the file's own comment style, `Makefile:60-92`: comments carry the measurement and the constraint with a source and date ("read 2026-10-06", "198 MB, 16.4 s ... (21-RESEARCH, scratch runs)").

**Stale lines to rewrite** (cite L43; empty-grep pin `grep -n -E '63\.555|~64 s|about 64 s'`, so the history sentence must not keep the literal strings, P6):
- `:105` `# slice twice, taking the gate from about 64 s to about 75 s, over L34's 66 s bar.`
- `:173` `# whole gate is 63.555 s (L34). Every test file but the five heavy ones, named by`

**Green-only change** (RESEARCH Code Examples; current line numbers `$(STAMP): pyproject.toml` at `:45`, install at `:53`):
```make
$(STAMP): pyproject.toml requirements.txt
	$(PY) -m pip install --quiet --upgrade pip
	$(PY) -m pip install -e '.[dev]' -c requirements.txt
```
Leave the `--upgrade pip` line unconstrained.

### `.pre-commit-config.yaml:10`
Same rewrite class. Current text: `# stamp). A warm `make verify` measured 63.555 s (`-n 8` with coverage, mean of two runs)` followed by lines 11-14 about the 12-core M2 Max, RESULTS.md section "Before and after", 2026-10-04. Rewrite lines 10-12 as a whole sentence citing L43 and the new reading; keep it as history where the old figure matters but without the literal `63.555`. Note: editing this file makes `$(HOOKS)` stale in the main checkout (re-installs on next `make`); do it after the last reading.

### `docs/HOW_TO_DEVELOP.md`
- `:21` "~64 s on a warm cache (12-core dev host, `bench/RESULTS.md`, Phase 15)." and `:129` "(about 64 s warm)": rewrite to cite L43's bar and its host.
- Green only: one sentence in §0's venv bullet (`:30-32`, "Run `make venv` once in the main checkout ...") that an existing `.venv` keeps its older resolve until `make clean && make venv` (D-13, A6).
- Reverify sentence in §6, beside the ship-note paragraph (`:139-145`), phrased like that paragraph's workaround voice: "The ship-note commit carries `[ci skip]` ... Commit it by hand: ...". One sentence naming `.ai_skills/reverify-phase`.
- Do not touch the "four heaviest" drift (`:25-27`, README:315): out of scope (Pitfall 7); file as nice debt only if the human wants.

### `README.md`
- `:36-40`: current text is "It builds for `linux/amd64` and `linux/arm64`, so Apple silicon, Graviton and a\nRaspberry Pi 5 all work:". Keep the architecture list; add "built for, not measured on" and a hardware statement naming 12-CPU Apple M2 Max and 18-CPU Apple M5 Max, none on an arm64 board (D-15). The `sh` fence after it stays.
- `:307`: `make verify      # the gate: ... (~64 s warm on a 12-core dev host, no Docker)` -> cite the new bar and host. Do not touch `:96` or `:315`.
- Guard: `tests/test_cli.py::test_readme_export_examples_run` and the `test_api.py` root-form-d test read README (RESEARCH Pitfall 6); keep the `spur export` example lines.

### `docs/architecture/packaging.md:44`
`make verify   ruff + mypy --strict + import-linter + unfinished-work scan + pytest   (~64 s warm on the 12-core dev host, `-n 8` with coverage; no Docker)`. Same rewrite as README:307; add this file to the SC3 empty-search. On green also `:17-18` (who is constrained; Open Question 4).

---

### `tests/test_hooks.py` (green only, D-20)

**Analog:** the two existing fixtures themselves. First test builds a bare repo with Makefile copy + empty `pyproject.toml`:
```python
shutil.copy(REPO_ROOT / "Makefile", main / "Makefile")
(main / "pyproject.toml").write_text("", encoding="utf-8")
(main / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
...
for checkout in (main, worktree):
    # `$(STAMP)` up to date, so only `$(HOOKS)` has work to do.
    os.utime(checkout / "pyproject.toml", (1_000_000_000, 1_000_000_000))
```
(`:180-182`, `:193-195`; second test `:225-227`, `:230`). Add beside each: `(main / "requirements.txt").write_text("", encoding="utf-8")` and a matching `os.utime(... "requirements.txt" ...)` at the same old mtime so `$(STAMP)` stays current. In the first test the file reaches the worktree through `git add .`. Without this, make stops with "No rule to make target 'requirements.txt'".

---

### `.ai_skills/reverify-phase/SKILL.md` (new)

**Analog:** no existing skill (`.ai_skills/` holds only README.md). Follow `.ai_skills/README.md` "How to add one":
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
Keep short. Content (D-17 amended by D-19): lead with `gsd_run query verification.status <phase_dir>` -> owner's `next_command` (`/gsd-execute-phase N`, GSD 1.16.0 #4682); fallback hand dispatch of `gsd-verifier` (model from `gsd_run query resolve-model gsd-verifier`) with phase dir, goal, requirement ids, `git diff --stat <old-report-sha>..HEAD -- <covered files>` and why; agent does not commit; commit by hand `docs(NN): re-verify phase N after ...`; then `/gsd-ship N`. Source recipe: `docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md`. Dry-read proof: `ls .claude/skills/reverify-phase/SKILL.md` (symlink `.claude/skills -> ../.ai_skills`, verified).

---

### Idea retirements (venv, Pi 5, reverify) and `docs/ideas/INDEX.md`

**Analog:** `docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md`.

File header shape (from `retired/2026-09-21-browser-test-for-the-viewer.md:1-5`):
```
# A browser test for the viewer

Date: 2026-09-21
Status: retired
Retired in: docs(21): log L39 and retire the browser-test idea -- a headless browser runs in make verify and CI
```
Append `## Outcome` (bore-shape file tail: names the phase, the route taken, the feature commit). Reverify outcome writes the count: five hits across four phases (9 x2, 17, 23, 24). Then `git mv` into `docs/ideas/retired/`.

**INDEX move** (`docs/ideas/INDEX.md`): delete the row from `## Open`, append to `## Retired`:
```
| 2026-09-27 | [A bore-shape selector in the web form](retired/2026-09-27-bore-shape-selector-in-the-web-form.md) | test(24): every pick ... -- retire the bore-shape idea |
```
Each retires in the commit that closes it: venv idea in the L43 commit (green only; red leaves it filed), Pi 5 in the README commit, reverify in the skill commit. `Retired in:` is the commit subject (cannot carry its own sha). Do not batch retirements (PITFALLS m-4).

---

### IN-03 close: `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` + `docs/tech_debt/INDEX.md:38`

**Analog:** `docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md` header:
```
Severity: nice
Status: resolved
Date: 2026-10-11
Resolved in: fix(calc): name only the hex-ignored bore fields set away from their defaults
```
(subject form, D-22). The IN-03 file stays in `active/` for IN-01, IN-02, IN-04: edit the IN-03 bullet at `:18` to mark it resolved with the commit subject, update the `## Next step` paragraph (`:25`, drop the "IN-03 belongs to the L34 re-set" sentence), drop the Makefile Related-files entry, and delete from the INDEX trigger (line 38) the clause `; the L34 bar is re-set under a new `Lxx` (IN-03)`. File's own footer comment (`:27-28`) describes resolve mechanics for a whole-file move; here only the finding closes.

## Shared Patterns

### Records are ordered and honest (L08)
**Source:** `bench/RESULTS.md` 21-07 and 24-04 sections. **Apply to:** rule, readings, probe. Every reading carries load before/after, machine (`bench.machine_facts()`), HEAD and UTC; bars from other hosts are quoted, never rescaled; red runs kept with whole log and classified, never replaced silently; the human's checkpoint answer is recorded verbatim.

### Stale-figure sweep
**Apply to:** the L43 commit. `grep -n -E '63\.555|~64 s|about 64 s' Makefile .pre-commit-config.yaml docs/HOW_TO_DEVELOP.md README.md docs/architecture/packaging.md` must print nothing; record the empty output in the commit's SUMMARY (21-06 exclusion-pin precedent).

### Standing invariants after every task (RESEARCH Validation)
- `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json`
- `git diff --name-only <R>^..HEAD -- src docker scripts pyproject.toml requirements.txt` prints nothing
- `git diff --name-only <R>^..HEAD -- tests`: nothing, or only `tests/test_hooks.py` on green
- Measured HEAD equals the rule commit's short sha on all ten rows; commit nothing between first wait and last run (hook load, HEAD drift).

### Retire in the closing commit
**Source:** CLAUDE.md "Capturing ideas and debt"; `docs/ideas/retired/*`. Status flip, subject (not sha), `git mv`, INDEX row, same commit.

### Do-not-run
Per the orchestrator: no `make verify`, `make venv` or gate run during pattern mapping or in the main checkout during planning; the probe runs only in the linked worktree after the last reading.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.ai_skills/reverify-phase/SKILL.md` | skill | n/a | `.ai_skills/` holds no skill yet; use the README template and the idea file's recipe |
| idle-wait loop (in rule section) | inline shell | polling | No script in repo; copy RESEARCH Pattern 1 and the Phase 13 D-05 / Phase 15 R1-R2 wording (`bench/RESULTS.md:2246-2250`, Phase 13 sessions near `:303-329`) |

## Metadata

**Analog search scope:** `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `Makefile`, `.pre-commit-config.yaml`, `docs/HOW_TO_DEVELOP.md`, `README.md`, `docs/architecture/packaging.md`, `tests/test_hooks.py`, `.ai_skills/`, `docs/ideas/`, `docs/tech_debt/`
**Files scanned:** about 20 (targeted reads; RESEARCH.md lines 443-690 beyond the Validation table not fully read, and its V1-V25 command list should be taken from RESEARCH directly)
**Pattern extraction date:** 2026-10-14
