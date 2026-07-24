# Learn 5 by 5

A language-learning app where users master 5 new words per day through AI-powered voice conversation, spaced repetition, and structured daily lessons.

---

## Project Structure

```
learn-5-by-5/
├── lib/                     # Flutter mobile app (iOS + Android + Web)
├── backend/                 # FastAPI REST API + Admin Dashboard
│   ├── app/                 # API source code (Clean Architecture)
│   │   ├── core/            # Config, DB, security, dependencies
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # DB access layer
│   │   ├── services/        # Business logic
│   │   └── api/v1/          # REST route handlers
│   ├── admin/               # Jinja2 + HTMX admin dashboard
│   ├── migrations/          # Alembic DB migrations
│   ├── scripts/             # seed.py and utilities
│   └── tests/               # pytest tests
├── docs/                    # Architecture documentation
│   ├── ARCHITECTURE.md      # System overview + tech stack + folder structure
│   ├── DATABASE_SCHEMA.md   # All tables, columns, relationships, indexes
│   ├── FLOWS.md             # Auth, lesson, AI, subscription, support flows
│   ├── API_SPEC.md          # All REST endpoints with request/response examples
│   └── IMPLEMENTATION_PLAN.md  # 9-phase plan with tasks per phase
├── assets/                  # Flutter app assets
└── docker-compose.yml       # Full-stack local dev setup
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Mobile | Flutter 3 + Riverpod + GoRouter + Dio |
| Backend | Python 3.13 + FastAPI + SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 16 |
| Admin UI | FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind CSS |
| AI | OpenAI (GPT-4o + Whisper + TTS) |
| Payments | Stripe |
| Notifications | Firebase FCM + Celery + Redis |
| Containerization | Docker + Docker Compose |

---

## How to Run (Backend)

```bash
cd backend
cp .env.example .env
# Edit .env with your actual values (DB, OpenAI, Stripe keys)

# With Docker (recommended):
docker-compose up

# Or locally:
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs` (debug mode only)  
Admin dashboard: `http://localhost:8000/admin`  
Default admin: `admin@learn5by5.com` / `changeme123` ← **change immediately**

---

## Required Secrets

| Secret | Where to get it |
|--------|----------------|
| `OPENAI_API_KEY` | platform.openai.com |
| `STRIPE_SECRET_KEY` | dashboard.stripe.com |
| `STRIPE_WEBHOOK_SECRET` | Stripe CLI or dashboard |
| `FIREBASE_CREDENTIALS_JSON` | Firebase Console |
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `ADMIN_SESSION_SECRET` | Generate: `openssl rand -hex 32` |

---

## Implementation Phases

See `docs/IMPLEMENTATION_PLAN.md` for full details.

1. **Foundation** — Backend scaffold, DB, Auth ✅ Scaffolded
2. **Core Lesson** — Daily lesson, words, SRS ✅ Scaffolded
3. **AI Layer** — Voice conversation, feedback ✅ Scaffolded
4. **Flutter App** — All screens + navigation ✅ Scaffolded
5. **Subscriptions** — Stripe integration
6. **Admin Dashboard** — Full content management ✅ Scaffolded
7. **Notifications** — Push + scheduling
8. **Support System** — Ticket + FAQ
9. **Production** — Docker, tests, hardening

---

## User Preferences
- Clean Architecture with Repository + Service + API layers
- No React/Vue/Angular in the admin dashboard — Jinja2 + HTMX + Alpine.js only
- Single admin user, no multi-role admin system
- Max 5 new words per day (core product constraint)
- Spaced repetition uses SM-2 algorithm
