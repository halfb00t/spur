# bench

The measuring instrument for Phase 2's two success criteria (D-16): a committed,
rerunnable harness so the numbers stay falsifiable by whoever doubts them later, not a
figure quoted from a session that has since ended.

## What each half measures

- **`bench.latency`** (`bench/latency.py`) -- does `/api/health` stay responsive while a
  build is in flight? Reproduces the debt file's own two scenarios (one 200-tooth fine
  build; ten concurrent builds) and reports idle p95, under-load p95, their ratio, and
  the slowest build observed.
- **`bench.memory`** (`bench/memory.py`) -- the container memory ceiling. `sweep` drives
  the 40-gear corpus (`bench/corpus.py`) through the service at each of N = 1, 2, 4 build
  workers and records the peak per N; `confirm` re-runs the same corpus at a candidate
  `mem_limit` and reports the failure count. `sweep` runs under a ceiling of its own
  (CR-02 review) so `compose.yaml`'s `mem_limit` can never cap the measurement it
  exists to determine, and a row whose peak reaches that ceiling is reported capped,
  with no peak number.

## Where each half must run, and why

- **Latency runs on the host** (`make serve`), the same way the debt file's own
  0.22s -> 0.76s -> 2.00s baseline was produced. A container adds overhead the recorded
  baseline never paid; measuring latency there would make old and new numbers
  incomparable (D-17).
- **Memory runs in the container** (`docker compose`), because `mem_limit` is a
  container setting and must be measured under the container's own accounting.
  `malloc_trim(0)` -- the per-worker arena release `_release_arenas()` depends on -- is
  glibc-only and does nothing on a macOS development machine; the container is Linux,
  where it actually runs (`docs/architecture/packaging.md` "Known gap").

Every number either half prints carries the machine that produced it (CPU count,
architecture, RAM) -- a measurement's meaning changes with the hardware behind it.

## How to run them

```
make serve            # in one terminal
make bench.latency     # in another -- both load scenarios against /api/health

make bench.memory      # manages its own containers: the N=1,2,4 sweep
.venv/bin/python -m bench.memory confirm 2g   # confirm a candidate mem_limit
```

`make bench` runs both halves in sequence. None of the three targets are part of
`make verify` or `make check` (D-16): they need a running service and minutes, and a
latency assertion on shared hardware would flap until someone stopped believing it.

## The one rule that outranks convenience

The corpus does not change. `bench/corpus.py`'s 40 distinct 160-199 tooth gears are
L07's own -- the exact workload that earned `compose.yaml`'s `mem_limit: 2g`. Narrowing,
shortening or re-picking it to make a ceiling look better produces a number that cannot
be compared with the one already on record, which defeats the entire point of measuring.
