---
name: Learn 5 by 5 project spec
description: Key architectural decisions and conventions for the Learn 5 by 5 language learning app
---

# Learn 5 by 5 — Key Decisions

## Architecture
- Clean Architecture: API → Service → Repository → ORM model
- Flutter: Riverpod + GoRouter + Dio (not Bloc, not Provider)
- Backend: FastAPI async with SQLAlchemy 2.0 (async engine + asyncpg)
- Admin dashboard: FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind — NO React/Vue/Angular

## Core Product Constraint
- Max 5 new words per day (enforced at service layer)
- SRS uses SM-2 algorithm (implemented in backend/app/services/srs_service.py)

## Naming / Structure
- All models in backend/app/models/ (one file per domain)
- All repositories inherit BaseRepository (generic CRUD)
- All services take AsyncSession in __init__
- Admin auth is session-based (separate from JWT API auth)
- Stripe webhook at POST /webhooks/stripe (not under /subscriptions/)

## Languages supported (seeded)
- en (English), ar (Arabic, RTL), fr (French), es (Spanish), de (German)
- All five are both UI languages and learnable target languages

## Subscription plan slugs
- free / premium / lifetime (used in feature-gating checks)

**Why:** The spec explicitly forbids mixing admin auth with the API JWT system, and explicitly forbids React/Vue in admin.

**How to apply:** When adding new features, keep admin routes in backend/admin/app.py (session auth), API routes in backend/app/api/v1/endpoints/ (JWT auth).
