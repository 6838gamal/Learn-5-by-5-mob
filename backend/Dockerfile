# ── Stage 1: Build Stage ──────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# تثبيت أدوات التجميع الخاصة بالحزم التي تحتاج C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المطلب من داخل مجلد backend
COPY backend/requirements.txt .

# تجهيز الـ Wheels لتفادي مشاكل المسارات والربط بين الـ Stages
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ── Stage 2: Runtime Stage ────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. تثبيت الحزم الجاهزة (Wheels) من مرحلة البناء
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# 2. إنشاء مستخدم غير جذر (Non-root user) للأمان وتجهيز مجلد المرفقات
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p static/uploads && \
    chown -R appuser:appuser /app

# 3. نسخ كود التطبيق المكتوب داخل مجلد backend وتحديد ملكية الملفات
COPY --chown=appuser:appuser backend/ .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
