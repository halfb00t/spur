"""Repository tooling that is not part of the shipped `spur` wheel.

Hatch packages only `src/spur` (`[tool.hatch.build.targets.wheel] packages`), so nothing
under `scripts/` is installed or distributed -- it exists to be run from a clone, the way
`bench/` already is. Importable from the repository root via `.venv/bin/python -m
scripts.<module>` (there is no `scripts` entry in the wheel's package list, so a bare
`import scripts` only resolves when the repo root is on `sys.path`). Type-checked by
`make typecheck`'s `src tests docker bench scripts` list, same as `bench` and
`docker/smoke.py`.
"""

from __future__ import annotations
