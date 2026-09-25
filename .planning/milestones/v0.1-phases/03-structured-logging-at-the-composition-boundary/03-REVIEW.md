---
phase: 03-structured-logging-at-the-composition-boundary
reviewed: 2026-09-24T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - docs/architecture/cli.md
  - docs/architecture/decision_log.md
  - docs/architecture/gear-maths/errors_and_logging.md
  - docs/architecture/http-api.md
  - docs/architecture/solid-model/errors_and_logging.md
  - docs/CODING_VALUES.md
  - docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-21-no-structured-logging.md
  - README.md
  - src/spur/app.py
  - src/spur/cli.py
  - src/spur/pool.py
  - src/spur/records.py
  - tests/conftest.py
  - tests/test_api.py
  - tests/test_pool.py
  - tests/test_records.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-09-24
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

`records.py`'s five per-event helpers, their wiring into `app.py`/`pool.py`/`cli.py`, and
the four rewritten `errors_and_logging.md`/`http-api.md`/`cli.md` doc sections all match
the code for the vocabulary they set out to cover: `build.started`, `build.failed`,
`export.served`, `queue.refused`, `worker.replaced` fire from exactly the branches the
docs and `L20` describe, the two idempotent `configure()` call sites are correctly placed
and guarded, the `caplog`/`capsys` tests correctly pin the level under test rather than
relying on `caplog`'s default WARNING threshold, and every log-bearing test asserts a
non-empty result before filtering by event name. `docs/tech_debt/active/2026-09-24-shared-
solid-cache-corrupts-later-boundingbox.md`'s claim ("no file under `src/spur/*.py` calls
`.BoundingBox()` today") still holds after this phase's changes.

The one real defect is in `_JsonFormatter` itself: it unconditionally discards
`exc_info`/`exc_text`/`stack_info` for every record it formats, not just for the three
exception classes `build_failed()` deliberately keeps traceback-free. That includes
uvicorn's own `"Exception in ASGI application"` error log — the exact fallback path a
genuinely unclassified crash in `model()` takes, since `model()`'s three `except` clauses
don't cover it either. Put together, the one scenario this phase's own resolved tech-debt
item names as the reason it exists — "the first time something goes wrong in a deployment,
there is nothing to read" — is the one scenario still logs nothing useful. Verified
directly against the installed `uvicorn`/`starlette` source and by feeding a real
traceback through `_JsonFormatter().format()`.

## Critical Issues

### CR-01: `_JsonFormatter` silently drops every exception traceback, including uvicorn's own unhandled-error log line

**File:** `src/spur/records.py:50-87`
**Issue:** `_STANDARD_LOGRECORD_ATTRS` (lines 50-55) includes `exc_info`, `exc_text` and
`stack_info` — real, always-present `LogRecord` attributes — and `_JsonFormatter.format()`
(lines 64-87) excludes every key in that set from the JSON payload with no replacement.
Nothing in the formatter calls `self.formatException()` or otherwise renders
`record.exc_info`/`record.exc_text` into the output the way the stdlib `Formatter.format()`
would. Confirmed empirically:

```
$ .venv/bin/python3 - <<'EOF'
import logging
from spur.records import _JsonFormatter
logger = logging.getLogger("uvicorn.error")
try:
    raise ValueError("boom, unexpected model.py bug")
except ValueError as exc:
    rec = logger.makeRecord("uvicorn.error", logging.ERROR, __file__, 1,
                             "Exception in ASGI application\n", (), (type(exc), exc, exc.__traceback__))
print(_JsonFormatter().format(rec))
EOF
{"ts": "...", "level": "ERROR", "logger": "uvicorn.error", "event": "Exception in ASGI application\n", "version": "0.1.0"}
```

No trace of `ValueError`, no file/line, nothing beyond the bare message. This is not a
contrived record: it is the literal record uvicorn's own `h11_impl.py`
(`run_asgi`, `.venv/lib/python3.12/site-packages/uvicorn/protocols/http/h11_impl.py:414-416`)
emits for *any* exception that escapes the ASGI app — `msg = "Exception in ASGI
application\n"; self.logger.error(msg, exc_info=exc)`. Since `cli.cmd_serve` passes
`log_config=None` (D-02), that `uvicorn.error` record rides the exact same root handler
and `_JsonFormatter` this phase installs (`http-api.md`'s own claim: "uvicorn's own access
and error records … ride the same stream and the same JSON format"). The claim is true of
the envelope, not of the content that matters most in this one record.

`build_failed()`'s own docstring (`records.py:210-227`) explains why *its* three known
classes (`BuildError`/`BuildTimeout`/`BrokenProcessPool`) deliberately carry no traceback —
that reasoning does not extend to an exception `build_failed()` never sees, because
`model()` never catches it (see WR-01 below). For that case, this is the *only* place a
traceback could still surface, and it is thrown away unconditionally, for every logger,
not just `spur`'s own. This directly contradicts the resolved tech-debt item this phase
closes (`docs/tech_debt/resolved/2026-09-21-no-structured-logging.md`): "The first time
something goes wrong in a deployment, there is nothing to read" — for exactly the failure
class no `except` clause names, there is still nothing to read after this phase.

No test in `tests/test_records.py` constructs a record with real `exc_info` set, so this
gap shipped untested.

**Fix:**
```python
def format(self, record: logging.LogRecord) -> str:
    payload: dict[str, object] = {
        "ts": ...,
        "level": record.levelname,
        "logger": record.name,
        "event": record.__dict__.get("event", record.getMessage()),
        "version": __version__,
    }
    if record.exc_info:
        payload["exc_info"] = self.formatException(record.exc_info)
    elif record.exc_text:
        payload["exc_info"] = record.exc_text
    for key, value in record.__dict__.items():
        if key in _STANDARD_LOGRECORD_ATTRS or key == "event":
            continue
        payload[key] = value
    return json.dumps(payload, default=str)
```
Add a round-trip test that builds a record via `logger.makeRecord(..., exc_info=(ExcType,
exc, tb))` (the same pattern `_make_record` already uses for `extra`) and asserts the
formatted JSON contains the exception's message/type.

## Warnings

### WR-01: `model()`'s exception handling only covers three known classes — anything else vanishes from spur's own log vocabulary

**File:** `src/spur/app.py:377-413`
**Issue:** The `try`/`except` around `_build_slot(...)` in `model()` catches exactly
`BuildError`, `BuildTimeout` and `BrokenProcessPool`. Anything else raised inside that
block — most concretely `_gzip()` running under `run_in_threadpool` (line 373), which
calls `gzip.compress()` and can raise under memory pressure, or any future violation of
`model.py`'s own "`BuildError` is the only exception the module lets out" contract
(`docs/architecture/solid-model/errors_and_logging.md`) — propagates uncaught out of the
endpoint. `_build_slot`'s `finally` still releases the admission slot correctly (no
capacity leak), but `build_failed()` is never called: no `build.failed`, no
`export.served`, nothing from `spur`'s own vocabulary for a request that actually failed.
The only remaining evidence is uvicorn's `"Exception in ASGI application"` fallback — which
CR-01 shows loses its traceback too. Together the two gaps mean this exact failure mode
produces a log line with no exception class, no traceback, and no `spur`-owned fields at
all — the "first incident, nothing to read" scenario this phase exists to close.

**Fix:** Add a catch-all around the same block that logs and re-raises, rather than
silently falling through to the ASGI-level fallback:
```python
except (BuildError, BuildTimeout, BrokenProcessPool):
    ...  # unchanged, three branches above
except Exception as exc:
    build_failed(request_id, params, fmt, q.quality, exc=exc,
                duration_s=time.monotonic() - start)
    raise
```
`build_failed()` already treats an unrecognised class as ERROR by default (its own
docstring says as much), so no change to `records.py` is required for this half of the fix
— only CR-01's fix is needed to make the resulting record actually carry a traceback.

### WR-02: `test_calc_module_stays_log_free` only catches a literal `import logging`, not `from .records import ...`

**File:** `tests/test_records.py:182-187`
**Issue:** The regex `r"^\s*(import|from)\s+logging\b"` guards against `calc.py` importing
the stdlib `logging` module directly, but `docs/architecture/gear-maths/errors_and_logging.md`
states a stronger invariant: *"calc.py never imports it \[`records.py`\], the way it never
imports the CAD kernel."* Nothing enforces that stronger claim. A future edit adding
`from .records import build_started` (or `import spur.records`) to `calc.py` would not
match this regex at all and would pass `make verify` silently — unlike the CAD-kernel
boundary, which has both a regex-adjacent doc claim *and* an import-linter contract
(`pyproject.toml`'s "The gear maths stays free of the CAD kernel", `source_modules =
["spur.calc", "spur.params", "spur.cli"]`, `forbidden_modules = ["cadquery", "OCP"]`).
There is no equivalent import-linter contract naming `spur.records` as forbidden from
`spur.calc`; this test is the *only* stated guard, and it doesn't cover the case its own
docstring says it protects against ("cheap insurance against drift into the module that
matters most to keep pure").
**Fix:** Either broaden the regex to also flag `from .records`, `from spur.records`,
`import spur.records`, and `import records`, or — more robustly, matching the existing
CAD-kernel pattern — add an import-linter contract:
```toml
[[tool.importlinter.contracts]]
name = "The gear maths stays free of the logger"
type = "forbidden"
source_modules = ["spur.calc"]
forbidden_modules = ["spur.records", "logging"]
```

## Info

### IN-01: Two tests in `tests/test_records.py` duplicate the same idempotency setup

**File:** `tests/test_records.py:65-74` and `tests/test_records.py:165-179`
**Issue:** `test_configure_called_twice_installs_exactly_one_handler` and
`test_configure_twice_still_emits_exactly_one_line_per_record` both open with the identical
four lines (`records.configure()` twice, then filter `logging.getLogger().handlers` for
`_JsonHandler` and assert `len(...) == 1`) before the second test goes on to prove the
stronger, distinct claim (one line printed, not two). Not wrong, and each test name reads
as a distinct requirement, but the first test's assertion is a strict subset of the
second's — worth folding into one test if this file is touched again.
**Fix:** Optional. Either drop the handler-count assertion from the first test (letting
the second test's superset assertion stand alone) or merge the two into one test named for
the stronger property.

---

_Reviewed: 2026-09-24_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
