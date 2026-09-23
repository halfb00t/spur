# packaging

`Dockerfile`, `compose.yaml`, `requirements.txt`, `docker/`, `.github/workflows/ci.yml`,
`Makefile`.

## Responsibility

Produce a reproducible image that can still do the job after being trimmed, and prove
both halves of that sentence automatically.

## Shape

- **`requirements.txt` is generated, not written** (L12): the full resolved closure, 31
  of 31 packages, installed with `--no-deps`. Regenerate with `make lock`
  (`docker/refresh-requirements.sh`); never hand-edit a line, because with `--no-deps`
  pip will not tell you when a bumped version breaks the closure. `pyproject.toml` keeps
  loose ranges for developer environments.
- **The image drops what it does not import.** ~440 MB of `trame*`, `matplotlib`,
  `scipy`, `numba`, `llvmlite`, `pillow` and friends are uninstalled in the same layer.
  `vtk` is *not* removable — `OCP` links `libvtkWrappingPythonCore` — and `casadi`,
  `nlopt`, `ezdxf` and `pyparsing` are imported eagerly by cadquery. That list came from
  uninstalling and re-adding until `export()` worked again, not from guessing.
- **`docker/smoke.py` runs during the build** and exercises the kernel, both exporters
  and the ASGI app, so a wrong closure fails the build instead of production. It drives
  `app.py`'s ASGI callable directly, so it also drives `app.router.lifespan_context(app)`
  itself, explicitly, before making requests — the build pool (Phase 2) only starts
  inside that lifespan, and a bare ASGI call never triggers it on its own. Its own
  `anyio.run(main)` is guarded by `if __name__ == "__main__":`, required once a build
  actually spawns a worker process: `spawn` re-imports this module as `__main__` in the
  child, and an unguarded call would relaunch the whole script inside it.
- **`compose.yaml` is hardened and measured**: `127.0.0.1` binding, `read_only`,
  `tmpfs /tmp` capped at 256 MB, `cap_drop: ALL`, `no-new-privileges`, one server process
  (`SPUR_WORKERS: "1"`) plus a build-worker pool (`SPUR_BUILD_WORKERS: "2"`, D-01), and a
  `mem_limit: 4g` set from a real sweep of that N-worker topology over the same 40-gear
  corpus L07's `2g` was earned against — see `bench/RESULTS.md`'s Memory section for the
  per-N peaks and the confirm run.

## The gate (L13)

```
make verify   ruff + mypy --strict + import-linter + unfinished-work scan + pytest   (~11 s warm, no Docker)
make check    verify + the in-image smoke test + the vendored-bundle byte check      (needs Docker)
make bench    bench.latency (host) + bench.memory (Docker) -- NOT part of the gate
```

The same `make verify` runs in three places: the pre-commit hook
(`.pre-commit-config.yaml`), CI (`.github/workflows/ci.yml`, on Python 3.10 and 3.12),
and `make worktree.land` before a merge. One definition of "passing".

`make bench` is a sibling of the gate, not a member of it (D-16): it needs a running
service and minutes (a full N=1,2,4 memory sweep alone is ~15 minutes), and a latency
assertion on shared hardware would flap until people stopped trusting it. It exists so
the numbers in `bench/RESULTS.md` stay falsifiable by whoever doubts them later, not
quoted from a session that has since ended — see `bench/README.md`.

CI additionally builds the image and curls `/api/health`, `/api/model.stl` and
`/api/model.step` against the running container, and rebuilds the three.js bundle to
prove it still matches `web/` (L11).

## Platform notes

`make venv` picks `python3.12`/`3.11`/`3.10` itself and says so if it cannot find one,
because a newer default `python3` sends pip off building OpenCascade from source. On
Apple silicon, `PLATFORM=linux/arm64 make image` avoids inheriting an emulated
`DOCKER_DEFAULT_PLATFORM=linux/amd64` from the shell.

## Worktrees

`make worktree.new SLUG=<s>` branches into `.claude/worktrees/<s>`; `make worktree.land
SLUG=<s> MSG="..."` squash-merges it after re-running the gate on the merged result, and
refuses if either checkout is dirty or the base branch is wrong.

One trap, verified rather than assumed: **do not share the main checkout's `.venv` with a
worktree.** Its editable install points at the main checkout's `src/`, so `import spur`
from inside a worktree resolves back to the main tree and the suite silently tests
unmodified code. Run `make venv` inside the worktree (~1.4 GB) or use `make test-image`.

## Known gap

`malloc_trim(0)` is glibc-only, so the memory behaviour L07 exists for is inactive on a
macOS development machine and untested there. It now runs per build worker
(`SPUR_BUILD_WORKERS` processes, Phase 2) rather than in the single server process L07
originally measured, but the gap itself is unchanged: it is exercised in the container,
not by an automated test.
