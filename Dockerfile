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
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps . && python -c "import spur.model" && rm -rf /tmp/.cache

RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin spur
USER 10001

ENV SPUR_HOST=0.0.0.0 \
    SPUR_PORT=8000 \
    SPUR_WORKERS=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request as u; u.urlopen('http://127.0.0.1:' + os.environ.get('SPUR_PORT', '8000') + '/api/health', timeout=4)"]

CMD ["spur", "serve"]
