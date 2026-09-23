# syntax=docker/dockerfile:1
# spur: parametric spur gear web service. Builds for linux/amd64 and linux/arm64.
FROM python:3.12-slim-bookworm

# Shared libraries the OpenCascade (cadquery-ocp) and VTK wheels link against.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libx11-6 libexpat1 \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XDG_CACHE_HOME=/tmp/.cache

WORKDIR /app

# Heavy CAD dependencies first so code changes don't invalidate this layer.
# --no-deps because requirements.txt is the entire pinned closure: that is what lets it
# leave out the ~550 MB of packages cadquery declares but spur never imports (VTK
# viewers, DXF export, the assembly solver, matplotlib). docker/smoke.py below is what
# makes that safe -- it fails the build if the closure is incomplete.
COPY requirements.txt .
RUN pip install --no-deps -r requirements.txt

COPY pyproject.toml README.md ./
COPY src ./src
COPY docker ./docker
RUN pip install --no-deps . \
 && python docker/smoke.py \
 && rm -rf /tmp/.cache

RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin spur
USER 10001

ENV SPUR_HOST=0.0.0.0 \
    SPUR_PORT=8000 \
    SPUR_WORKERS=1
EXPOSE 8000

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

CMD ["spur", "serve"]
