# A pytest-xdist worker segfaults in OCCT at interpreter exit

Severity: nice
Status: active
Date: 2026-10-09
Source: conversation 2026-10-09, during Phase 19 wave 2 — the human pasted a crash-report analysis; the orchestrator checked it against the reports and the suite
Related files:
- Makefile:150 (the `test` target: `pytest -n 8 --cov`)
- ~/Library/Logs/DiagnosticReports/Python-2026-10-09-083646.ips (one of the twelve reports; outside the repo)

## Context
Twelve macOS crash reports between 2026-10-08 16:46 and 2026-10-09 08:36 share one stack:
`BRepAlgoAPI_BuilderAlgo::~BRepAlgoAPI_BuilderAlgo()` (libTKBO 7.9.3) called from
`Py_FinalizeEx → finalize_modules → _PyModule_ClearDict → insertdict → list_dealloc →
tupledealloc → OCP`, `EXC_BAD_ACCESS` at a different garbage address each time. The
crashing process is a child Python whose pid is 1–5 above its parent's, 28–34 s old, with
18 threads and `tracer.cpython-312` (pytest-cov), OCP, `_multiprocessing`, `_posixshmem`,
`_asyncio` and `_pydantic_core` loaded: a pytest-xdist worker of a whole-suite run, not a
`BuildPool` worker (those spawn later, far from the parent's pid) and not a
`python -m spur.cli` child. One worker per run crashes, after its tests have reported. A
module-level list of tuples still holds an OCCT boolean builder when the module dicts are
cleared; which module is unknown, because the two OCP frames are unsymbolized.

Not reproduced on demand. Three whole-suite runs on 2026-10-09 produced no report:
`make test` (1034 passed in 58.74 s), a `-n 8 --cov` run with an `atexit` probe loaded into
all nine pytest processes (0 module-level holders, 0 live builders at atexit), and
`make verify.fast` (713 passed in 11.07 s). Every executor run between 2026-10-08 22:25 and
2026-10-09 00:51 (at least five whole-suite gates, seven pre-commit `verify.fast` runs and
sixty two-file loops) also produced none. Every run between 07:19 and 08:36 on 2026-10-09
did; those were the human's, and their command, cwd and environment are not recorded.

The repo has no `BRepAlgoAPI` use of its own and no module-level caches of OCP objects.
cadquery's `_bool_op` keeps the builder local and returns `Shape.cast(op.Shape())`, and
pybind11 does not keep the builder alive through the returned shape (checked with a
weakref: the builder is collected after `del op` while the shape is still held).

Each crashing run also left a second report: a 0.1 s single-threaded `python -c` child
dying inside `os.kill` (SIGSEGV, no OCP loaded). Nothing in `tests/`, `src/`, `bench/` or
`scripts/` calls `os.kill` or raises SIGSEGV. Its origin is unknown.

## Why it matters
The crash comes after the worker's tests have reported, so it cannot fail the gate, and no
`BuildPool` worker has been seen to die this way. Today's cost is crash-report noise and an
unexplained object-lifetime bug in the test session. If the same holder ever forms inside a
`BuildPool` worker, a serving process would log a worker segfault at every shutdown.

## Next step
Revisit when the human names the command that crashed every run on 2026-10-09 between
07:19 and 08:36 (command, cwd, venv, environment), or when a `BuildPool` worker's exit
logs SIGSEGV. Then run that command with an `atexit` hook that scans every module in
`sys.modules` for a list of tuples holding an `OCP` object and prints the module and
attribute name — `atexit` runs before `finalize_modules`, so the holder is still intact
there. Clear the holder in that hook or drop the reference at its source, and if it lives
in cadquery or OCP, file it upstream.
