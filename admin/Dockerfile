# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# requirements live in backend/
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

# Copy shared backend package (app.*) and the admin package
COPY backend/ .
COPY admin/ ./admin/

RUN mkdir -p admin/static

EXPOSE 8001

CMD ["uvicorn", "admin.main:app", "--host", "0.0.0.0", "--port", "8001"]
