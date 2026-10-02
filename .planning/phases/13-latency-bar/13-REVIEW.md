---
phase: 13-latency-bar
reviewed: 2026-10-02T10:19:44Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - Dockerfile
  - bench/RESULTS.md
  - bench/latency.py
  - docs/architecture/decision_log.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md
  - docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md
  - tests/test_bench.py
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-10-02T10:19:44Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the latency-bar phase's diff against `9f26052`: the `Dockerfile` HEALTHCHECK
comment, the composed-sweep (`SC3`) addition to `bench/latency.py` and its tests, the new
`L32` decision-log entry, and the tech-debt file move/creation. Cross-checked every
numeric claim in `bench/latency.py`'s `COMPOSED_ROWS`/`_composed_rows` comments against
`bench/RESULTS.md`'s "Re-run after the gate" table and the raw `bench/sweeps/composed.json`
file directly (`python3 -c "json.load(...)"`); every row index, build time and firing
order matches exactly — no defect found there. `mypy --strict` and `ruff check` both pass
clean on `bench/latency.py` and `tests/test_bench.py`, and the four new tests in
`tests/test_bench.py` pass (`pytest -k "composed or no_argument_latency or 503"`).
Cross-checked `decision_log.md`'s L32 entry's Pair A/B/C worse/not-worse characterization
against `bench/RESULTS.md`'s own investigation-session table — matches exactly. The
`_sample_while_building` generalization to a PEP 695 type parameter (flagged by the
orchestrator as outside the plan's byte-identical promise) was traced: its body is
unchanged from `9f26052`, only the signature became generic, `mypy --strict` accepts it,
and the three call sites (`scenario_single`, `scenario_concurrent`, `run_composed`)
instantiate the type parameter correctly — **verified behavior-preserving, not a defect**.

One finding did confirm an orchestrator-flagged discrepancy: the `Dockerfile` HEALTHCHECK
comment's claim of "across the fifteen `bench/RESULTS.md` latency runs" is false by the
file it cites — the fifteenth run (SC3) is documented in `bench/RESULTS.md` as having no
`/api/health` p95 at all ("do not exist for this run"), so it cannot be one of the runs
that produced the cited 0.7–2.3 ms range. See CR-01.

## Critical Issues

### CR-01: Dockerfile HEALTHCHECK comment cites 15 runs for a range only 14 of them produced

**File:** `Dockerfile:42-43`
**Issue:** The comment reads: "its measured under-load p95 is 0.7-2.3 ms across the
fifteen bench/RESULTS.md latency runs". `bench/RESULTS.md`'s own "Composed worst row
under ten concurrent builds (Phase 13)" section — the fifteenth run this count is counting
(confirmed by the commit that introduced this wording, `6709953`: "run count eight ->
fifteen (Runs 1-8, the three bar sessions, the SC3 run)") — states explicitly, verbatim:
"**In-process and split-poller idle/under-load p95: do not exist for this run.**" SC3
aborted (`exit 1`) before `run_composed` ever returned a `ScenarioResult`, so no
`/api/health` idle or under-load p95 was ever computed for it. A reader who takes "across
the fifteen ... latency runs" at face value — exactly the plausible-but-unmeasured
reading this project's own L08 standard forbids for any number stated as measured —
would believe the 0.7–2.3 ms range rests on 15 runs' worth of evidence; it rests on 14
(Runs 1–14; `bench/RESULTS.md`'s own tables show the 0.7 ms floor and 2.3 ms ceiling both
occurring within Runs 1–14, confirmed by direct read of every `under-load p95` cell in
that range). This is the same comment that justifies the container `HEALTHCHECK`'s 2 s
timeout margin in production — the evidence count backing it should be exact, per
`CLAUDE.md`'s standard that "comments explain *why*, and carry the measurement or the
constraint that forced the choice."
**Fix:**
```diff
- # D-13): its measured under-load p95 is 0.7-2.3 ms across the fifteen
- # bench/RESULTS.md latency runs (worst: 2.3 ms, concurrent Run 3, pre-L19; 1.3 ms
- # post-L19) -- three orders of magnitude below the old 10 s. 2 s leaves that margin
+ # D-13): its measured under-load p95 is 0.7-2.3 ms across fourteen numbered
+ # bench/RESULTS.md latency runs (worst: 2.3 ms, concurrent Run 3, pre-L19; 1.3 ms
+ # post-L19) -- three orders of magnitude below the old 10 s. (A fifteenth run, the
+ # Phase 13 composed-sweep SC3, aborted before producing a p95 at all and is not part
+ # of this range -- see bench/RESULTS.md "Composed worst row under ten concurrent
+ # builds".) 2 s leaves that margin
```

## Warnings

### WR-01: `scenario_composed`'s success path would print the single/concurrent `RECORDED_BASELINE` under a "composed" heading

**File:** `bench/latency.py:348-364` (`_report_markdown`), reached via `_run_scenario` for
`name="composed"`
**Issue:** `_report_markdown` unconditionally prints `RECORDED_BASELINE` — the debt file's
`single`/`concurrent` numbers ("single: 0.22s -> 0.76s -> 2.00s under one 200-tooth fine
build; concurrent: repeatedly over 5s under ten concurrent builds") — under whatever
`name` is passed in, including `"composed"`. If `scenario_composed` is ever invoked and
`run_composed` returns normally (the crash in the one recorded `SC3` run is not
guaranteed on every host/timing), the printed `## Latency: composed` report would carry a
"Recorded baseline" line that has nothing to do with the composed sweep, inviting a reader
to compare the composed ratio against numbers measured for a different scenario entirely.
This is a pre-existing function reused for a new scenario without being adapted to it —
not a new regression this phase introduced carelessly, but the composed path is new in
this phase and nothing guards against the misleading output.
**Fix:** Either make `RECORDED_BASELINE` conditional on `name != "composed"`, or give
`_report_markdown` a `baseline: str | None` parameter and have `scenario_composed`'s
caller pass `None`:
```python
def _report_markdown(name: str, idle_p95: float, idle_n: int, load_p95: float,
                      load_n: int, slowest_build: float, attempted: int,
                      refused: int) -> str:
    ratio = load_p95 / idle_p95 if idle_p95 > 0 else float("inf")
    baseline_line = (
        f"- Recorded baseline (different machine, ratio-only comparison per D-17): "
        f"{RECORDED_BASELINE}\n" if name != "composed" else ""
    )
    return (
        f"## Latency: {name}\n\n"
        ...
        f"{baseline_line}"
    )
```

---

_Reviewed: 2026-10-02T10:19:44Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
