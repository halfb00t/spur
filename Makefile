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
.PHONY: help venv test serve check image test-image smoke up down logs \
        lock vendor vendor-check clean clean-docker

help:  ## list the targets
	@grep -hE '^[a-z][a-z-]*:.*##' $(MAKEFILE_LIST) | sed 's/:[^#]*##/\t/' | expand -t18

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

test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest $(PYTEST_ARGS)

serve: $(STAMP)  ## run the dev server on http://127.0.0.1:8000
	$(VENV)/bin/spur serve

check: test smoke vendor-check  ## everything CI runs, locally

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

# --- generated artefacts -----------------------------------------------------------

lock:  ## regenerate requirements.txt, the pinned closure the image installs
	docker/refresh-requirements.sh

vendor:  ## rebuild the vendored three.js bundle (needs node)
	cd web && npm ci && npm run build

vendor-check:  ## fail if the committed bundle no longer matches web/
	cd web && npm ci --silent && npm run build
	git diff --exit-code -- src/spur/static/vendor

# --- cleanup -----------------------------------------------------------------------

clean:  ## remove the venv, caches and exported models
	rm -rf $(VENV) .pytest_cache .ruff_cache build dist
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	rm -f *.stl *.step *.stp

clean-docker:  ## remove this project's container and image
	-docker compose down --remove-orphans
	-docker image rm $(IMAGE)
