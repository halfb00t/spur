# spur -- every command you need to work on this project. `make` lists them.

VENV        ?= .venv
IMAGE       ?= spur:latest
PLATFORM    ?=
PYTEST_ARGS ?=
SWEEP       ?=
SET         ?=

# cadquery-ocp publishes wheels up to CPython 3.12, and spur supports 3.12 only (L23).
# Choosing the interpreter here instead of using a bare `python3` is what stops pip
# trying to build OpenCascade from source against a newer one and failing minutes in.
PYTHON ?= $(shell for p in python3.12; do \
            command -v $$p >/dev/null 2>&1 && { echo $$p; break; }; done)

PY    := $(VENV)/bin/python
STAMP := $(VENV)/.installed
HOOKS := $(VENV)/.hooks-installed
# A DOCKER_DEFAULT_PLATFORM in your environment wins unless you set PLATFORM here;
# PLATFORM=linux/arm64 gives a native, much faster image on Apple silicon.
PLATFORM_ARG := $(if $(PLATFORM),--platform $(PLATFORM),)

.DEFAULT_GOAL := help
.PHONY: help venv verify verify.static verify.fast lint typecheck lint-imports \
        no-fake-done test test.fast serve \
        check image test-image smoke up down logs lock vendor vendor-check fixture.regen \
        bench bench.latency bench.memory bench.build bench.export \
        worktree.bootstrap worktree.new worktree.land pr.land clean clean-docker

help:  ## list the targets
	@grep -hE '^[a-z][a-z.-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*##/\t/' | expand -t18

# --- local python ------------------------------------------------------------------

$(STAMP): pyproject.toml
	@test -n "$(PYTHON)" || { \
	  echo "make: no python3.12 on PATH."; \
	  echo "      cadquery-ocp has no wheels past 3.12 and spur supports 3.12 only (L23)."; \
	  echo "      Install one (brew install python@3.12), or use 'make test-image'."; \
	  exit 1; }
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --quiet --upgrade pip
	$(PY) -m pip install -e '.[dev]'
	@touch $@

# D-06: a clone that forgot `pre-commit install` pushed unverified until CI, silently, so
# the gate installs the hooks itself. The stamp depends on .pre-commit-config.yaml, so a
# config change re-installs on the next gate run; $(STAMP) alone (pyproject.toml only)
# never would.
#
# Main checkout only. pre-commit 4.6.2 writes into `git rev-parse --git-common-dir`, which
# every linked worktree shares, and bakes the installing venv's python into the shim
# (pre_commit/commands/install_uninstall.py `_hook_paths`, pre_commit/resources/hook-tmpl;
# read 2026-10-06). An install from a worktree would point every checkout's hooks at a
# venv `make worktree.land` deletes, and every later commit would fail. tests/test_hooks.py
# runs both branches. Re-running the install from inside a running hook leaves that hook
# intact (17-RESEARCH Pitfall 6, scratch repo, 2026-10-06), so the stamp may go stale in
# the middle of a commit. No `|| true`: a failing install fails the gate -- except where
# the install cannot succeed whatever the code does: pre-commit 4.6.2 refuses with
# "Cowardly refusing to install hooks with `core.hooksPath` set" (read 2026-10-06,
# install_uninstall.py), so with that key set the recipe says so loudly and installs nothing.
# It does not touch the stamp then, so the message repeats on every run until the key is
# unset and the hooks get installed.
$(HOOKS): .pre-commit-config.yaml $(STAMP)
	@if [ -n "$$(git config --get core.hooksPath)" ]; then \
	  echo "make: core.hooksPath is set, so pre-commit cannot install: no git hooks installed. Unset it or wire the hooks yourself (L36)."; \
	elif [ "$$(git rev-parse --absolute-git-dir)" \
	     = "$$(git rev-parse --path-format=absolute --git-common-dir)" ]; then \
	  $(VENV)/bin/pre-commit install && touch $@; \
	else \
	  echo "make: a linked worktree -- the hooks live in the main checkout's .git/hooks; run make venv there (L36)."; \
	  touch $@; \
	fi

venv: $(STAMP) $(HOOKS)  ## create .venv with the dev extras, ~1.4 GB (override with VENV=)

# --- the gate ----------------------------------------------------------------------

# Nothing is done until this passes. Needs no Docker, so it is the one an agent runs
# after every change; `make check` adds the container checks CI also runs.
#
# The commit stage is a named prefix of the gate, never a second list of checks (L13, L36):
# `verify` and `verify.fast` both start at `verify.static` and each ends in one pytest
# recipe, `test` and `test.fast`. `verify: verify.fast test` was rejected: it runs the
# slice twice, taking the gate from about 64 s to about 75 s, over L34's 66 s bar.
verify.static: $(HOOKS) lint typecheck lint-imports no-fake-done  ## the gate's static steps: ruff, mypy, import boundaries, unfinished-work scan
verify: verify.static test  ## the gate: lint, types, import boundaries, tests
verify.fast: verify.static test.fast  ## the commit-time subset: the static steps + every test file but the four heavy ones, under 30 s (L36)

lint: $(STAMP)  ## ruff: correctness rules only, no reformatting (L16)
	$(PY) -m ruff check .

typecheck: $(STAMP)  ## mypy --strict over the package and its tests
	$(PY) -m mypy src tests docker bench scripts

lint-imports: $(STAMP)  ## the module boundaries declared in pyproject.toml
	$(VENV)/bin/lint-imports

# ':!.../vendor' keeps a future three.js release's own comments from failing our gate:
# the bundle is a build artefact (L11), not code we wrote.
#
# -w, not \b: git grep -E hands the pattern to the system regex library, and macOS's does
# not implement \b -- a staged file holding both TODO and NotImplementedError passed the
# \b-anchored scan with exit 1 and no output (homebrew git 2.54.0, 2026-10-05). So on the
# dev host, where the pre-commit hook runs, this check passed vacuously and only CI's
# Linux git enforced it. -w is git's own whole-word match, the same on both;
# tests/test_no_fake_done.py stages that probe against a copy of this file.
#
# The second block: mypy's warn_unused_ignores refuses a stale suppression, but nothing
# refused a new one -- the fifth arrived unnoticed in 10-02. Scoped to src/spur/ because
# tests/test_calc.py and tests/test_cli.py each carry one on purpose, on a deliberate
# GearParams.model_construct(**kw) (Phase 16, D-05). The spellings mypy also accepts --
# no space, any case, and the whole-file `mypy: ignore-errors` -- are matched, and
# --untracked reaches a module not yet `git add`ed (16-REVIEW WR-02); `pyright: ignore`
# is not refused. tests/test_no_fake_done.py stages or drops each probe.
no-fake-done: ## refuse unfinished work dressed up as finished
	@if git grep -nwE '(TODO|FIXME|XXX|HACK|NotImplementedError)' \
	     -- '*.py' '*.js' '*.sh' ':!src/spur/static/vendor'; then \
	  echo "make: unfinished-work markers above. Finish it, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi
	@if git grep -nEi --untracked 'type:[[:space:]]*ignore|mypy:[[:space:]]*ignore-errors' \
	     -- 'src/spur/*.py'; then \
	  echo "make: a mypy suppression in src/spur above. Narrow the type, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi

# --cov gates every run on [tool.coverage.report] fail_under (bench/RESULTS.md, Phase 15,
# Coverage floor). A run over part of the suite reads a low total and fails it: pass
# --no-cov, e.g. make test PYTEST_ARGS="tests/regression -q -n0 --no-cov" (-n0 also runs
# it serially, which -x and --pdb need). PYTEST_ARGS comes last so the caller's flags
# win. --cov-report=term is the default report, spelt out because --cov takes an
# optional value: a bare --cov followed by a path in PYTEST_ARGS swallows it as the
# coverage source and runs the whole suite instead (measured: 927 tests, not
# test_calc.py's 404, with --no-cov no help).
#
# PYTEST_WORKERS is 8, the apparent knee of the pytest-xdist sweep the human picked at the
# profile checkpoint (bench/RESULTS.md, "The gate, measured and pinned (Phase 15)", xdist
# sweep and Gate decision; 12-CPU M2 Max, 2026-10-03/04). It is a measured choice, not
# the host's CPU count: the sweep's N = 12 ran slower than N = 8. The clamp keeps it
# from oversubscribing a smaller host: CI's runner has 4 vCPUs, and tests/test_pool.py's
# injected 0.2 s and 1.0 s timeouts are what a starved runner would trip. A missing or
# non-numeric answer from getconf falls back to one worker: left alone, an empty n reads
# as 0 in the arithmetic and the suite would run -n 0 (serial, 4x the cost) with no
# message (15-REVIEW IN-02). The count is the host's online CPUs, not a cgroup quota.
PYTEST_WORKERS ?= $(shell w=8; n=$$(getconf _NPROCESSORS_ONLN 2>/dev/null); \
                    [ "$$n" -ge 1 ] 2>/dev/null || n=1; echo $$(( n < w ? n : w )))

test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)

# The commit-time slice (D-02, D-04): gsd's SDK kills `git commit` at 30 000 ms, and the
# whole gate is 63.555 s (L34). Every test file but the four heavy ones, named by
# exclusion -- never inclusion, never a marker -- so a new test file runs at commit until
# someone names it heavy (`--strict-markers` is on and no marker is registered). The four,
# by share of pytest's seconds (L34, bench/RESULTS.md "Per-file share"): tests/test_model.py
# 74.1 %, tests/test_pool.py 8.5 %, tests/test_api.py 4.8 %; tests/test_cli.py is the
# fourth (D-02). --no-cov is mandatory: `fail_under = 96` reads a partial run as a failure.
# Re-priced 2026-10-06 on the 12-core M2 Max dev host (1-min load 3.0-5.5): `make
# verify.fast` read 11.28, 11.30 and 11.28 s wall warm (620 passed in 10.75 s) and 19.94 s
# with an empty mypy cache -- all under the 30.0 s kill, with 10 s or more of headroom.
# The OS-cold page cache is not priced: the slice imports the kernel (tests/test_bench.py
# through bench.build_time, the regression replay's solids), so D-07 is the recovery if a
# commit ever runs over.
test.fast: $(STAMP)  ## run every test file but the four heavy ones, no coverage (the commit-time slice)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --no-cov \
	  --ignore=tests/test_model.py --ignore=tests/test_pool.py \
	  --ignore=tests/test_api.py --ignore=tests/test_cli.py $(PYTEST_ARGS)

serve: $(STAMP)  ## run the dev server on http://127.0.0.1:8000
	$(VENV)/bin/spur serve

check: verify smoke vendor-check  ## everything CI runs, locally (needs Docker)

# --- container ---------------------------------------------------------------------

image:  ## build the container image
	docker build $(PLATFORM_ARG) -t $(IMAGE) .

test-image: image  ## run the test suite inside the image (needs no local python)
	docker run --rm $(PLATFORM_ARG) --user root -e PYTHONPATH=/app/src \
	  -v "$(CURDIR)/src:/app/src:ro" -v "$(CURDIR)/tests:/app/tests:ro" \
	  -v "$(CURDIR)/pyproject.toml:/app/pyproject.toml:ro" \
	  -w /app --entrypoint sh $(IMAGE) \
	  -c "pip install -q --root-user-action=ignore pytest httpx \
	      && python -m pytest -q -p no:cacheprovider $(PYTEST_ARGS)"

smoke: image  ## exercise the kernel, both exporters and the ASGI app inside the image
	docker run --rm $(PLATFORM_ARG) --entrypoint python $(IMAGE) docker/smoke.py

up:  ## build, start and wait for the service on http://localhost:8000
	docker compose up -d --build
	@printf 'waiting for the container to report healthy'
	@n=0; until [ "$$(docker compose ps --format '{{.Health}}')" = healthy ]; do \
	   n=$$((n+1)); \
	   if [ $$n -gt 60 ]; then echo ' gave up'; docker compose logs --tail=20; exit 1; fi; \
	   printf '.'; sleep 2; \
	 done
	@echo ' -> http://localhost:8000'

down:  ## stop and remove the service
	docker compose down

logs:  ## follow the service log
	docker compose logs -f

# --- measurement: not part of the gate (D-16) ---------------------------------------
# Both need a running service and minutes; a latency assertion on shared hardware would
# flap until someone stopped believing it. Rerun deliberately, not on every commit.

bench: bench.latency bench.memory  ## everything this phase's success criteria need

bench.latency: $(STAMP)  ## /api/health under load, on the host -- run `make serve` first (D-17)
	$(PY) -m bench.latency

bench.memory: $(STAMP)  ## container memory sweep over the 40-gear corpus; manages its own containers
	$(PY) -m bench.memory sweep

# bench.build needs no service: it times spur.model in-process, the code a worker runs
# (D-12), so it never depends on `make serve` or Docker the way the two targets above do.
bench.build: $(STAMP)  ## build, fine STL and STEP time per set vs SPUR_BUILD_TIMEOUT; SWEEP=<json> (default: the Phase 8 hex-bore sweep)
	$(PY) -m bench.build_time $(SWEEP)

# Re-measures L19's gzip table and L24's mesh-copy cost for one set (D-17); needs no
# service, same reason bench.build needs none -- it is spur.model in-process plus a few
# short-lived child processes of its own.
bench.export: $(STAMP)  ## gzip level table (L19) and mesh-copy cost (L24) for one set; SWEEP=<json> SET="<label>"
	$(PY) -m bench.export_cost $(SWEEP) --set "$(SET)"

# --- generated artefacts -----------------------------------------------------------

lock:  ## regenerate requirements.txt, the pinned closure the image installs
	docker/refresh-requirements.sh

vendor:  ## rebuild the vendored three.js bundle (needs node)
	cd web && npm ci && npm run build

vendor-check:  ## fail if the committed bundle no longer matches web/
	cd web && npm ci --silent && npm run build
	git diff --exit-code -- src/spur/static/vendor

fixture.regen: $(STAMP)  ## rewrite tests/regression/pre_v0_2.json (the L05 fixture); commit it alone, saying what moved and why
	$(PY) tests/regression/capture.py

# --- worktrees: isolated, parallel agent work ---------------------------------------

worktree.bootstrap:  ## once per clone: let each worktree keep its own config
	git config extensions.worktreeConfig true

worktree.new:  ## SLUG=<slug> : branch agent/<slug> off HEAD into .claude/worktrees/<slug>
	@test -n "$(SLUG)" || { echo "SLUG= required"; exit 1; }
	@echo "$(SLUG)" | grep -qE '^[a-zA-Z0-9_-]+$$' || { echo "Bad SLUG (alnum/_/- only)"; exit 1; }
	@BASE=$$(git symbolic-ref --short HEAD); \
	git worktree add .claude/worktrees/$(SLUG) -b agent/$(SLUG) $$BASE; \
	git -C .claude/worktrees/$(SLUG) config --worktree worktree.base $$BASE; \
	echo "worktree .claude/worktrees/$(SLUG) on agent/$(SLUG) (base $$BASE)"; \
	echo "run 'make venv' inside it, or 'make test-image' -- do NOT share the main"; \
	echo ".venv: its editable install resolves 'import spur' back to the main checkout,"; \
	echo "so the suite would silently test unmodified code."

worktree.land:  ## SLUG=<slug> MSG="<commit>" : verify, squash-merge, remove the worktree
	@test -n "$(SLUG)" || { echo "SLUG= required"; exit 1; }
	@test -n "$(MSG)" || { echo 'MSG= required'; exit 1; }
	@WT=$$(git rev-parse --show-toplevel)/.claude/worktrees/$(SLUG); \
	test -d "$$WT" || { echo "No worktree at $$WT"; exit 1; }; \
	BASE=$$(git -C $$WT config worktree.base); \
	test -n "$$BASE" || { echo "worktree.base unset; run worktree.bootstrap, then recreate"; exit 1; }; \
	git -C $$WT diff --quiet && git -C $$WT diff --cached --quiet || { echo "Dirty worktree; commit or reset first"; exit 1; }; \
	test "$$(git symbolic-ref --short HEAD)" = "$$BASE" || { echo "Switch the main checkout to $$BASE first"; exit 1; }; \
	LOCK=$$(git rev-parse --git-dir)/worktree-land.lock; \
	until mkdir "$$LOCK" 2>/dev/null; do echo "another land in progress on $$BASE; waiting..."; sleep 1; done; \
	trap 'rmdir "$$LOCK" 2>/dev/null' EXIT; \
	git diff --quiet && git diff --cached --quiet || { echo "Dirty $$BASE; commit or reset first"; exit 1; }; \
	: "reset --hard HEAD is safe here: the base was just verified clean under the lock, so it only discards the failed squash (which leaves no MERGE_HEAD to abort)"; \
	git merge --squash agent/$(SLUG) || { git reset --hard HEAD; echo "CONFLICT - resolve in the worktree, then retry"; exit 1; }; \
	$(MAKE) verify || { git reset --hard HEAD; echo "verify failed on the merged result; not landing"; exit 1; }; \
	git commit -m "$(MSG)"; \
	git worktree remove --force $$WT; \
	git branch -D agent/$(SLUG); \
	echo "landed agent/$(SLUG) on $$BASE"

# --- landing on main: the merge gate (L22) ------------------------------------------

pr.land: $(STAMP)  ## PR=<n> : squash-merge a PR only if its head is green and current with main
	@test -n "$(PR)" || { echo "PR= required"; exit 1; }
	$(PY) -m scripts.pr_land $(PR)

# --- cleanup -----------------------------------------------------------------------

# parallel = true leaves one .coverage.<host>.<pid>.* per process; a killed run's files
# would otherwise outlive a clean and be combined into the next total (15-REVIEW IN-04).
clean:  ## remove the venv, caches and exported models
	rm -rf $(VENV) .pytest_cache .ruff_cache build dist
	rm -f .coverage .coverage.*
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	rm -f *.stl *.step *.stp

clean-docker:  ## remove this project's container and image
	-docker compose down --remove-orphans
	-docker image rm $(IMAGE)
