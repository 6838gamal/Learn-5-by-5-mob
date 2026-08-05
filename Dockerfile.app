# ══════════════════════════════════════════════════════════════════════════════
# Learn 5 by 5 — Web Frontend (app/)
# Entry point: uvicorn app.main:app
# Port: 5000
# ══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Build wheels ─────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build tools needed for any C-extension packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency manifest — layer-cached until pyproject.toml changes
COPY pyproject.toml .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels \
        "fastapi>=0.111.0" \
        "uvicorn[standard]>=0.29.0" \
        "jinja2>=3.1.0" \
        "httpx>=0.27.0" \
        "pydantic-settings>=2.2.0" \
        "python-multipart>=0.0.9" \
        "itsdangerous>=2.1.0" \
        "starlette>=1.0.0"


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Defaults — override at runtime via env vars or docker-compose
    PORT=5000 \
    DEBUG=false \
    ENVIRONMENT=production

# Install pre-built wheels (no compiler needed in runtime image)
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/* && rm -rf /tmp/wheels

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p app/static && \
    chown -R appuser:appuser /app

# Copy application source
COPY --chown=appuser:appuser app/       ./app/
COPY --chown=appuser:appuser pyproject.toml .

USER appuser

EXPOSE 5000

# Healthcheck — hits the splash redirect
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/splash')" || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--workers", "2", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
