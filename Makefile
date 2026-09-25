# spur -- every command you need to work on this project. `make` lists them.

VENV        ?= .venv
IMAGE       ?= spur:latest
PLATFORM    ?=
PYTEST_ARGS ?=

# cadquery-ocp publishes wheels for CPython 3.10-3.12 only. Choosing the interpreter
# here instead of using a bare `python3` is what stops pip trying to build OpenCascade
# from source against a newer one and failing several minutes in.
PYTHON ?= $(shell for p in python3.12 python3.11 python3.10; do \
            command -v $$p >/dev/null 2>&1 && { echo $$p; break; }; done)

PY    := $(VENV)/bin/python
STAMP := $(VENV)/.installed
# A DOCKER_DEFAULT_PLATFORM in your environment wins unless you set PLATFORM here;
# PLATFORM=linux/arm64 gives a native, much faster image on Apple silicon.
PLATFORM_ARG := $(if $(PLATFORM),--platform $(PLATFORM),)

.DEFAULT_GOAL := help
.PHONY: help venv verify lint typecheck lint-imports no-fake-done test serve \
        check image test-image smoke up down logs lock vendor vendor-check \
        bench bench.latency bench.memory \
        worktree.bootstrap worktree.new worktree.land clean clean-docker

help:  ## list the targets
	@grep -hE '^[a-z][a-z.-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*##/\t/' | expand -t18

# --- local python ------------------------------------------------------------------

$(STAMP): pyproject.toml
	@test -n "$(PYTHON)" || { \
	  echo "make: no python3.10-3.12 on PATH."; \
	  echo "      cadquery-ocp has no wheels for anything newer and pip cannot build it."; \
	  echo "      Install one (brew install python@3.12), or use 'make test-image'."; \
	  exit 1; }
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --quiet --upgrade pip
	$(PY) -m pip install -e '.[dev]'
	@touch $@

venv: $(STAMP)  ## create .venv with the dev extras, ~1.4 GB (override with VENV=)

# --- the gate ----------------------------------------------------------------------

# Nothing is done until this passes. Needs no Docker, so it is the one an agent runs
# after every change; `make check` adds the container checks CI also runs.
verify: lint typecheck lint-imports no-fake-done test  ## the gate: lint, types, import boundaries, tests

lint: $(STAMP)  ## ruff: correctness rules only, no reformatting (L16)
	$(PY) -m ruff check .

typecheck: $(STAMP)  ## mypy --strict over the package and its tests
	$(PY) -m mypy src tests docker bench scripts

lint-imports: $(STAMP)  ## the module boundaries declared in pyproject.toml
	$(VENV)/bin/lint-imports

# ':!.../vendor' keeps a future three.js release's own comments from failing our gate:
# the bundle is a build artefact (L11), not code we wrote.
no-fake-done: ## refuse unfinished work dressed up as finished
	@if git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b' \
	     -- '*.py' '*.js' '*.sh' ':!src/spur/static/vendor'; then \
	  echo "make: unfinished-work markers above. Finish it, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi

test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest $(PYTEST_ARGS)

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

# --- generated artefacts -----------------------------------------------------------

lock:  ## regenerate requirements.txt, the pinned closure the image installs
	docker/refresh-requirements.sh

vendor:  ## rebuild the vendored three.js bundle (needs node)
	cd web && npm ci && npm run build

vendor-check:  ## fail if the committed bundle no longer matches web/
	cd web && npm ci --silent && npm run build
	git diff --exit-code -- src/spur/static/vendor

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

# --- cleanup -----------------------------------------------------------------------

clean:  ## remove the venv, caches and exported models
	rm -rf $(VENV) .pytest_cache .ruff_cache build dist
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	rm -f *.stl *.step *.stp

clean-docker:  ## remove this project's container and image
	-docker compose down --remove-orphans
	-docker image rm $(IMAGE)
