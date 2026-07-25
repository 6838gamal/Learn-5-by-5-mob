# ── Stage 1: Build Stage ──────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# تثبيت أدوات التجميع الخاصة بالحزم التي تحتاج C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف متطلبات backend من المجلد الرئيسي
COPY backend/requirements.txt .

# تجهيز الـ Wheels لتفادي مشاكل المسارات والربط بين الـ Stages
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ── Stage 2: Runtime Stage ────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. تثبيت الحزم الجاهزة (Wheels) من مرحلة البناء
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# 2. إنشاء مستخدم غير جذر (Non-root user) وتجهيز مجلد الاستاتيك للـ Admin
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p admin/static && \
    chown -R appuser:appuser /app

# 3. نسخ كود الـ backend المشرك وكود الـ admin وتحديد الملكية
COPY --chown=appuser:appuser backend/ .
COPY --chown=appuser:appuser admin/ ./admin/

USER appuser

EXPOSE 8001

CMD ["uvicorn", "admin.main:app", "--host", "0.0.0.0", "--port", "8001"]
