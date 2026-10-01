# Phase 13: Latency Bar - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 11
**Analogs found:** 11 / 11

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `.planning/phases/13-latency-bar/investigation/poller.py` | utility (standalone script, subprocess) | streaming (sample loop → JSONL) | `bench/latency.py::_sample_while_building` + 02's lost `poller.py` (described in `02-LATENCY-INVESTIGATION.md` "## Method") | role-match (function-level exact; file itself is gone) |
| `.planning/phases/13-latency-bar/investigation/run_experiment.py` | utility (CLI harness, imports library code) | event-driven (orchestrates subprocess + ThreadPoolExecutor) | `bench/latency.py::scenario_concurrent`/`main` + 02's described `run_experiment.py` | role-match |
| `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` | doc (investigation write-up) | transform (raw samples → verdict) | `.planning/milestones/v0.1-phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md` | exact |
| `bench/latency.py` (new scenario, SC3, D-15) | service/CLI (bench scenario) | request-response (HTTP calls + ThreadPoolExecutor) | `bench/latency.py::scenario_concurrent` (same file) | exact |
| `tests/test_bench.py` (new row for SC3 scenario) | test | CRUD (asserts row selection) | `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines` | exact |
| `bench/RESULTS.md` (new sections) | doc (results record) | batch (markdown tables) | "### `concurrent` scenario" + Runs 7-8 host-state header + "### `SPUR_BUILD_TIMEOUT`" | exact |
| `docs/architecture/decision_log.md` (L32) | config/doc (decision record) | transform (measurement → locked claim) | L25 (amends L22) for amendment shape; L27-L31 for entry shape | exact |
| `Dockerfile` (HEALTHCHECK comment, lines 41-50) | config | n/a (prose comment) | same lines, in-place edit | exact |
| `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` → `resolved/` | doc (debt retirement) | transform (active → resolved) | `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` | exact |
| `docs/tech_debt/INDEX.md` (row 19 move) | doc (index) | CRUD (row move) | existing "Resolved" table rows (lines 42, 45, 46) | exact |
| `bench/README.md` (possible, if outcome (b) adopts restart protocol) | doc | n/a | existing "Where each half must run, and why" section | role-match |

## Pattern Assignments

### `.planning/phases/13-latency-bar/investigation/poller.py` (utility, streaming)

**Analog:** `bench/latency.py::_sample_while_building` (lines 70-83) + 02's Method section description (no surviving file to copy from — 02's scratch scripts are gone, D-03's own reasoning).

**Sampling loop pattern to reuse verbatim in spirit** (`bench/latency.py:70-83`):
```python
def _sample_while_building(base_url: str, client: httpx.Client,
                            futures: list[Future[float | None]]) -> list[float]:
    """Keep sampling `/api/health` for as long as at least one build is in flight.

    A do-while shape (sample first, check after) guarantees at least one sample even
    for a build that finishes before the first check would otherwise run.
    """
    samples: list[float] = []
    while True:
        t0 = time.perf_counter()
        client.get(f"{base_url}/api/health", timeout=30.0)
        samples.append(time.perf_counter() - t0)
        if all(future.done() for future in futures):
            return samples
```

**What `poller.py` must do differently, per 02-LATENCY-INVESTIGATION.md "## Method" and D-01/D-03:**
- Run as a genuinely separate OS process (`subprocess.Popen`), own `httpx.Client`, own GIL.
- Timestamp with `time.monotonic()` (not `time.perf_counter()` — 02's choice: monotonic is
  CLOCK_MONOTONIC-backed system/boot-time, comparable across processes with no clock-sync step;
  `perf_counter()` is not guaranteed cross-process comparable).
- Loop until a `--stop-file` path appears (checked each iteration), not until futures are done
  (it has no visibility into the harness process's futures).
- Write every `(time.monotonic(), latency_seconds)` pair to `--out` as JSON lines, one per line,
  as it samples (not buffered to the end) — so an orphaned poller (the 02 `try/finally` lesson)
  still leaves partial, honest data.
- `try/finally` around the sample loop: on exit (stop-file seen, or `kill()` from the parent),
  flush/close the JSONL file cleanly. 02's own documented failure: an unhandled 422 in the
  harness skipped its own cleanup, orphaned the poller (it never saw the stop-file), and a retry
  with the same file path then had two processes appending to one JSONL concurrently, corrupting
  it. D-03's fix: a fixed `--label`/`--run` naming scheme per pair×run makes a repeat run a new
  file, never an append onto a stale one.

### `.planning/phases/13-latency-bar/investigation/run_experiment.py` (utility, event-driven)

**Analog:** `bench/latency.py` (import these functions unmodified — D-04's "Claude's Discretion" note, also 02's own rule): `_sample_for` (59-66), `_sample_while_building` (70-83), `_build` (86-101), `_p95` (48-54).

**Import pattern** (`bench/latency.py:1-27`, adapt `sys.path.insert` for a script outside `bench/`):
```python
from __future__ import annotations

import argparse
import statistics
import sys
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

import httpx

from bench import machine_facts
```
`run_experiment.py` lives under `.planning/phases/13-latency-bar/investigation/`, outside the
package root, so it needs `sys.path.insert(0, PROJECT_ROOT)` before `from bench.latency import
_sample_for, _sample_while_building, _build, _p95` (02's own documented approach — "imported
unmodified ... never reimplemented").

**Concurrent-build firing pattern to mirror** (`bench/latency.py:135-144`, `scenario_concurrent`):
```python
def scenario_concurrent(base_url: str) -> ScenarioResult:
    with httpx.Client() as client:
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(_build, base_url, client, teeth, "fine")
                       for teeth in range(190, 200)]
            under_load = _sample_while_building(base_url, client, futures)
        slowest, attempted, refused = _collect(futures)
    return ScenarioResult("concurrent", idle, under_load, slowest, attempted, refused)
```
`run_experiment.py` reuses this shape but launches `poller.py` as a subprocess *before* starting
the in-process `_sample_for`/build phase, and must stop it (stop-file + `poller_proc.wait()`,
`kill()` fallback on timeout) inside a `try/finally` wrapping the build phase — the exact 02
lesson (see poller.py section above).

**Error-handling / refusal pattern** (`bench/latency.py:86-101`, `_build`):
```python
def _build(base_url: str, client: httpx.Client, teeth: int, quality: str) -> float | None:
    t0 = time.perf_counter()
    response = client.get(f"{base_url}/api/model.stl",
                           params={"teeth": teeth, "quality": quality}, timeout=120.0)
    if response.status_code == 503:
        return None
    response.raise_for_status()
    return time.perf_counter() - t0
```
`503` (admission-control refusal) is not a harness failure — return `None`; any other non-2xx
raises. Reuse unmodified via import, never reimplement (D-04's discretion note states this rule
explicitly).

**`--base-url` requirement (Pitfall 1, RESEARCH.md "Session Mechanics"):** every invocation of
`run_experiment.py` (and every ad hoc `python -m bench.latency` call inside it or in session
notes) must pass `--base-url http://127.0.0.1:8001` explicitly — `DEFAULT_BASE_URL` in
`bench/latency.py:28` is `:8000`, which is `spur-spur-1`'s port, not the test server's.

### `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` (doc, transform)

**Analog:** `02-LATENCY-INVESTIGATION.md` (full file; see Sources above).

**Frontmatter shape** (lines 1-8):
```yaml
---
phase: 02-cad-off-the-event-loop
plan: 04
type: investigation
status: complete
date: 2026-09-23
---
```
Adapt: `phase: 13-latency-bar`, drop or adapt `plan:` to whichever plan number covers the
investigation, `type: investigation`, `date: 2026-10-01` (or actual run date).

**Section order** (02's shape, Claude's Discretion per D-01/CONTEXT.md confirms this order):
`# <Question as a header>` / `## Question` / `## Environment` (host-state table, see below) /
`## Method` (reusable pieces named, scripts cited by file name per D-03) / `## Results` (one
subsection per experiment/pair/leg) / `## Verdict` / `## Recommendation` / `## Cleanup`.

**Host-state table pattern** (`02-LATENCY-INVESTIGATION.md` lines 15-34, the "## Environment"
table): one row per sampling point, columns `When | 1/5/15-min loadavg | Top CPU (excl. header)`,
each loadavg from `sysctl -n vm.loadavg`, each top-CPU line from `ps -Ao %cpu,comm -r | head -N`.
D-05's quiet-bar sampling (three consecutive 30s samples under 1.5) and D-06's `fleet-user`
stopped / `spur-spur-1` left running note are added rows/lines beyond 02's shape (02 never
reached a quiet host — every sample in its table reads loadavg 2.9-8.4, well above D-05's 1.5
bar — so 02's table is the shape to copy, not a quiet-session precedent to expect).

**Predictions-before-first-run instruction** (D-04): the prediction table (candidates ×
pair-legs, `<specifics>`'s starting table) goes in `## Method` or its own `## Predictions`
subsection, written before the `## Results` section's first row is filled in — 02's H1/H2/H3
shape (grep `02-LATENCY-INVESTIGATION.md` for "## Question" preceding "## Method" confirms
predictions-before-evidence is 02's own order).

### `bench/latency.py` (new SC3 scenario, request-response)

**Analog:** `scenario_concurrent` (same file, lines 135-144) for the firing-order/executor
shape; `bench/build_time.py::load_sweep` (lines 62-80) for reading rows from a sweep JSON file.

**Scenario registration pattern** (`bench/latency.py:135-152`):
```python
def scenario_concurrent(base_url: str) -> ScenarioResult:
    """Idle p95, then ten concurrent fine builds -- the scenario that repeatedly
    exceeded 5s. Admission control (MAX_QUEUED_BUILDS, D-09) refuses whatever doesn't
    fit the queue; see `_build`'s docstring."""
    with httpx.Client() as client:
        idle = _sample_for(base_url, client, SETTLE_SECONDS)
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(_build, base_url, client, teeth, "fine")
                       for teeth in range(190, 200)]
            under_load = _sample_while_building(base_url, client, futures)
        slowest, attempted, refused = _collect(futures)
    return ScenarioResult("concurrent", idle, under_load, slowest, attempted, refused)


_SCENARIOS: dict[str, Callable[[str], ScenarioResult]] = {
    "single": scenario_single,
    "concurrent": scenario_concurrent,
}
```
The new scenario (name is the planner's) registers in `_SCENARIOS` exactly here, follows the
same `idle = _sample_for(...)` then build-and-sample shape, but reads its ten build requests'
parameters from `bench/sweeps/composed.json` (rows 4, 2, 3, 1, 9, 6, 10, 12, 11, 5, 1-based —
confirmed exact in RESEARCH.md "Verified Code Citations") instead of a `teeth` range. `_build`'s
signature (`base_url, client, teeth, quality`) does not fit a full `GearParams` set — the new
scenario needs its own request-building step (constructing query params from each sweep row's
full field dict, then `client.get(f"{base_url}/api/model.stl", params={...})`), not a reuse of
`_build` unmodified, since `_build` only parametrizes `teeth`/`quality`.

**Sweep-reading pattern** (`bench/build_time.py:62-80`, `load_sweep`):
```python
def load_sweep(path: Path) -> list[tuple[str, GearParams]]:
    """Read a JSON list of shareable-link parameter sets, each validated into a
    `GearParams`. Label is the set's own `key=value` pairs, in file order.
    """
    raw: list[dict[str, object]] = json.loads(path.read_text())
    sets: list[tuple[str, GearParams]] = []
    for i, obj in enumerate(raw):
        label = " ".join(f"{k}={v}" for k, v in obj.items())
        try:
            p = GearParams.model_validate(obj)
        except ValidationError as exc:
            raise ValueError(
                f"{path} set {i} ({label}) is not a buildable gear: {exc}") from exc
        sets.append((label, p))
    return sets
```
The SC3 scenario either imports `load_sweep` directly from `bench.build_time` (reuse, no
reimplementation — same rule D-04 states for the investigation) or reads the ten named rows from
`bench/sweeps/composed.json` through it, then fires each row's full parameter dict as a
`/api/model.stl` request (worst row first, per D-13, then the other nine at t=0).

**Report formatting pattern** (`_report_markdown`, lines 168-184) — reuse as-is or extend with a
per-request table (D-14) printed alongside it; do not reimplement the idle/under-load p95
printing.

### `tests/test_bench.py` (new row, CRUD)

**Analog:** `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines` (lines 386-...).

**Shape to copy** (`tests/test_bench.py:386-413`):
```python
def test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines() -> None:
    """..."""
    sets = load_sweep(DEFAULT_SWEEP.parent / "composed.json")
    ...
```
The new test pins the SC3 scenario's row selection: `load_sweep(... / "composed.json")`, then an
exact `want` list comparing the ten expected labels/params against indices 4, 2, 3, 1, 9, 6, 10,
12, 11, 5 (1-based) in that order (worst row first per D-13) — a `want` equality assertion, same
shape as the composed-sweep test's own exact-list comparison, not a subset/contains check.

### `bench/RESULTS.md` (new sections, batch)

**Analog:** "### `concurrent` scenario" table (lines ~56-65) for the per-run latency table;
Runs 7-8's host-state header (`02-LATENCY-INVESTIGATION.md`-adjacent section) and "### Idle-host
re-run (Runs 3-4)" environment snapshot (lines ~75-83) for the host-state header shape; "###
`SPUR_BUILD_TIMEOUT`" (lines 271-279) for citing a worst-observed number against a configured
default.

**Per-run table pattern** (lines 56-65):
```markdown
### `concurrent` scenario (ten concurrent fine builds)

| Run | Idle p95 (n) | Under-load p95 (n) | Ratio | Slowest build | Refused |
|---|---|---|---|---|---|
| 1 | 0.6 ms (n=3694) | 1.2 ms (n=9051) | 2.02x | 7.39 s | 2 of 10 |
| 2 | 0.6 ms (n=3718) | 1.5 ms (n=8160) | 2.45x | 6.96 s | 0 of 10 |

Pass bar: under-load p95 <= 2.00x idle p95. **Not met** on either run (2.02x, then
2.45x — got worse, not better, on the second attempt).
```
New sections (investigation pairs, the decisive session, D-14's SC3 per-request table) follow
this `| Run | ... |` column shape, with the pass/fail prose sentence directly below stating
**Met**/**Not met** per run — never silently omitted.

**Host-state header pattern** (lines 75-83, adapt for D-05's quiet-wait three-sample format and
D-06's `fleet-user` note):
```markdown
**Environment snapshot (2026-09-23, ~12:11-12:12 UTC, immediately before the runs):**

- `docker info`: exit 0.
- `sysctl -n vm.loadavg`, three samples 30 s apart: `{ 3.33 2.86 2.23 }` (12:11:13 UTC),
  `{ 3.79 3.02 2.31 }` (12:11:48 UTC), `{ 3.96 3.13 2.37 }` (12:12:18 UTC).
- Top CPU (`ps -Ao %cpu,comm -r | head -5`), latest sample: ...
- `docker ps --format '{{.Names}} {{.Status}}'`: `spur-spur-1 Up 2 hours (healthy)`, ...
```
D-06's addition: a line stating `fleet-user` was stopped for the session (verbatim text given in
CONTEXT.md `<specifics>`: "`fleet-user` (unrelated, restart-looping every ~40 s beside Runs 1–8)
was stopped for this session; `spur-spur-1` left running.").

**Finding/record prose pattern** (lines 252-268, the two named observations) — write new
findings the same way: numbered, stated as observations not causes unless a cause was actually
ruled in, each tied to the specific runs/numbers that show it.

### `docs/architecture/decision_log.md` L32 (config/doc, transform)

**Analog:** L25 (amends L22) for the amendment mechanics; L27-L31 for a fresh-entry shape; L18
itself (the entry being amended) for what must stay untouched.

**Amendment header pattern** (`docs/architecture/decision_log.md:674`):
```markdown
## L25 — The merge gate reads the whole commit message and the run's own verdict (amends L22)

Date: 2026-09-25.

L22 stays as written; this entry amends three of its claims, closed in the three plans of
this phase.
```
L32's header: `## L32 — <title> (amends L18)`, `Date: <session date>.`, then `L18 stays as
written; this entry amends its concurrent-scenario caveat paragraph with <what changed>.` —
L18's own text is untouched (D-12); only PROJECT.md's L18 row's Outcome column is updated at
the milestone transition, not L18 itself.

**Body shape to follow** (L18's own body, lines 214-241, is the closest in-domain precedent —
same latency ratios, same `bench/RESULTS.md` citation style): cite measured numbers with the
exact `bench/RESULTS.md` section name, never re-estimate; end with a `Reason:` paragraph and the
machine/date line, matching L18's own closing two lines:
```markdown
Reason: the lock's cost and purpose are unchanged and stay logged at L06; what changed
is the shape of what it guards ... Machine: 12-core Apple M2 Max, 32 GiB RAM, macOS 27.0
(Darwin 27.0.0), 2026-09-23 (`bench/RESULTS.md` § Latency).
```

### `Dockerfile` HEALTHCHECK comment (config, in-place edit)

**Analog:** the same lines, current text (`Dockerfile:41-50`):
```dockerfile
# /api/health no longer touches the CAD kernel or waits on a build worker (Phase 2,
# D-13): its measured under-load p95 is 0.7-2.3 ms across the eight bench/RESULTS.md
# latency runs (worst: 2.3 ms, concurrent Run 3, pre-L19; 1.3 ms post-L19) -- three
# orders of magnitude below the old 10 s. 2 s leaves that margin for what actually varies here: the probe
# itself is a fresh Python process starting inside the container on every check, so its
# floor is interpreter startup, not the ~1 ms request. The inner urlopen timeout (1 s)
# stays below the outer --timeout so a genuinely hung request fails the check on its own
# terms rather than via Docker's outer kill.
HEALTHCHECK --interval=30s --timeout=2s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request as u; u.urlopen('http://127.0.0.1:' + os.environ.get('SPUR_PORT', '8000') + '/api/health', timeout=1)"]
```
Only the first sentence changes per D-12: update "eight bench/RESULTS.md latency runs (worst:
2.3 ms ...)" to the new run count and worst reading from this phase's sessions — do **not** add
a ≤2x bar citation here (D-12 explicitly forbids it); the `HEALTHCHECK` directive itself is
untouched.

### Debt retirement (`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` → `resolved/`)

**Analog:** `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`
(frontmatter + body shape) and its `INDEX.md` row (line 45).

**Frontmatter diff pattern** (resolved file's header):
```markdown
Severity: must
Status: resolved
Date: 2026-09-28
Resolved in: 89304e2
Source: 10-04's sweep
Related files:
- src/spur/app.py (the `SPUR_BUILD_TIMEOUT` line)
...
```
Apply to the retiring file: flip `Status: active` → `Status: resolved`, add `Resolved in: <sha>`
directly below `Status:`, leave `Date:` as the original creation date (2026-09-23 — unchanged;
`Resolved in:` carries the resolving commit, not a new date), then `git mv` into `resolved/` —
**only if** this phase's bar is demonstrated or superseded (D-11: a double miss does NOT retire
this file).

**INDEX.md row-move pattern** (line 45):
```markdown
| [A 200-tooth tip chamfer narrows SPUR_BUILD_TIMEOUT's margin](resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md) | `89304e2` — see the file's own `Resolved in:` field |
```
Row 19 (currently in the "Active" table, line 19) moves to the "Resolved" table in this exact
two-column shape: `[title](resolved/<filename>.md)` | `` `<sha>` — see the file's own `Resolved
in:` field ``.

## Shared Patterns

### No-plausible-number / refuse-rather-than-guess (L08)
**Source:** `bench/latency.py::_p95_or_warn` (lines 155-165):
```python
def _p95_or_warn(samples: list[float], label: str) -> tuple[float, int] | None:
    if len(samples) < MIN_SAMPLES:
        print(f"warning: {label} has only {len(samples)} /api/health samples "
              f"(need >= {MIN_SAMPLES}); refusing to report a p95", file=sys.stderr)
        return None
    return _p95(samples), len(samples)
```
**Apply to:** `run_experiment.py`'s own p95 computation (D-02's recomputation from raw JSONL),
the SC3 scenario's reporting, and the write-up's floor analysis — any series under
`MIN_SAMPLES` (20) gets a warning and no number, never an estimate.

### Machine-identification on every printed number
**Source:** `bench/__init__.py::machine_facts()`, used at `bench/latency.py:175` inside
`_report_markdown` (`f"- Machine: {machine_facts()}\n"`).
**Apply to:** every new `bench/RESULTS.md` section, the write-up's Environment section, and any
L32 text citing a ratio — a number without its machine is not comparable (D-17's own reasoning
for why the ratio, not the absolute ms, is the portable claim).

### Measured, never tuned, recorded even when it misses
**Source:** `bench/RESULTS.md` prose at the `concurrent` Runs 1-2 finding and Runs 7-8 finding
("Neither run was repeated or restarted in search of a passing number"); `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s own "Next step" ("a logged decision, not a tune
toward a pass").
**Apply to:** the decisive session (D-07), SC3's run (D-16), outcome (b)'s re-measurement
(D-09) — every run's number is recorded as read, pass or miss, never re-run in search of green.

### Debt lifecycle: flip status, add sha, `git mv`, move INDEX row — one commit
**Source:** `CLAUDE.md` "Capturing ideas and debt" section; concretely instantiated by
`docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` +
`docs/tech_debt/INDEX.md` line 45.
**Apply to:** the retiring commit for `2026-09-23-concurrent-latency-bar-waived.md` (D-18: "the
debt file retires in the commit that demonstrates or supersedes the bar").

### Decision log: append-only, amendments are new entries citing the old
**Source:** `docs/architecture/decision_log.md` L25 ("L22 stays as written; this entry amends
three of its claims") — the precedent D-12 names explicitly.
**Apply to:** L32's relationship to L18.

## No Analog Found

None — every file this phase creates or touches has a concrete, in-repo analog (the phase is
explicitly a measurement/record-keeping phase reusing `bench/latency.py`'s own machinery and
02's prior investigation shape; no new architectural pattern is introduced).

## Metadata

**Analog search scope:** `bench/`, `tests/test_bench.py`, `docs/architecture/decision_log.md`,
`docs/tech_debt/{active,resolved}/`, `docs/tech_debt/INDEX.md`, `Dockerfile`,
`.planning/milestones/v0.1-phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md`.
**Files scanned:** `bench/latency.py` (full), `bench/build_time.py` (partial, `load_sweep` +
docstring), `tests/test_bench.py` (composed-sweep test), `bench/RESULTS.md` (Latency section,
lines 34-279), `docs/architecture/decision_log.md` (L18, L25, headings L26-L31), `Dockerfile`
(lines 35-50), `docs/tech_debt/resolved/2026-09-28-...md`, `docs/tech_debt/INDEX.md`,
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` (full),
`02-LATENCY-INVESTIGATION.md` (frontmatter + Question/Environment/Method opening).
**Pattern extraction date:** 2026-10-01
