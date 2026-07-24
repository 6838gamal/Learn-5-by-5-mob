# Learn 5 by 5 — System Architecture

## Overview

Learn 5 by 5 is a language-learning mobile app where users learn 5 new words per day and master them through real-life practice, AI conversation, and spaced-repetition review.

---

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTS                                 │
│                                                             │
│   ┌──────────────────┐       ┌──────────────────────┐      │
│   │  Flutter App     │       │  Admin Dashboard     │      │
│   │  (iOS / Android) │       │  (FastAPI + Jinja2)  │      │
│   └────────┬─────────┘       └──────────┬───────────┘      │
└────────────┼──────────────────────────── ┼ ────────────────┘
             │ HTTPS / REST                │ HTTPS
             ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │   Auth   │  │ Lessons  │  │   AI     │  │  Support  │  │
│  │  Router  │  │  Router  │  │  Router  │  │   Router  │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Words   │  │ Reviews  │  │  Quizzes │  │   Subs    │  │
│  │  Router  │  │  Router  │  │  Router  │  │   Router  │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Service Layer                           │   │
│  │  AuthService │ LessonService │ AIService            │   │
│  │  ReviewService │ QuizService │ SubscriptionService  │   │
│  │  SupportService │ NotificationService               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Repository Layer                        │   │
│  │  UserRepo │ WordRepo │ LessonRepo │ ProgressRepo    │   │
│  │  ReviewRepo │ SubscriptionRepo │ SupportRepo        │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy 2.0
                             ▼
              ┌──────────────────────────┐
              │      PostgreSQL          │
              │   (Primary Database)     │
              └──────────────────────────┘

              ┌──────────────────────────┐
              │   External Services      │
              │  OpenAI / ElevenLabs     │
              │  FCM (Push Notifications)│
              │  Stripe (Payments)       │
              └──────────────────────────┘
```

---

## Technology Stack

### Mobile (Flutter)
| Layer | Technology |
|-------|-----------|
| Framework | Flutter 3.x (Dart 3.x) |
| State Management | Riverpod |
| Navigation | GoRouter |
| Networking | Dio + Retrofit |
| Local Storage | Hive / SharedPreferences |
| Audio | just_audio + record |
| Localization | flutter_localizations + intl |
| DI | Riverpod providers |

### Backend (FastAPI)
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Language | Python 3.13 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Task Queue | Celery + Redis (notifications) |
| AI | OpenAI API (GPT-4o + Whisper + TTS) |
| Containerization | Docker + Docker Compose |

### Admin Dashboard
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Templates | Jinja2 |
| Interactivity | HTMX + Alpine.js |
| Styling | Tailwind CSS |
| Auth | Session-based (admin only) |

---

## Design Patterns

- **Clean Architecture** — separation of presentation, domain, and data layers
- **Repository Pattern** — abstract database access behind interfaces
- **Service Layer** — business logic lives in services, not routes
- **Dependency Injection** — FastAPI `Depends()` + Riverpod in Flutter
- **SOLID Principles** — throughout

---

## Security

- JWT access tokens (15 min) + refresh tokens (30 days)
- bcrypt password hashing
- Rate limiting on all public endpoints
- CORS restricted to known origins
- Input validation via Pydantic v2
- SQL injection prevention via SQLAlchemy ORM
- HTTPS enforced in production
- Admin dashboard: separate session-based auth, not exposed via public API

---

## Folder Structure

```
learn-5-by-5/
├── lib/                          # Flutter app
│   ├── core/
│   │   ├── config/               # App config, constants
│   │   ├── theme/                # Light/dark theme
│   │   ├── localization/         # ARB files + generated
│   │   ├── router/               # GoRouter config
│   │   ├── network/              # Dio client, interceptors
│   │   └── utils/                # Helpers, extensions
│   ├── data/
│   │   ├── models/               # JSON-serializable DTOs
│   │   ├── datasources/          # Remote + local datasources
│   │   └── repositories/         # Repository implementations
│   ├── domain/
│   │   ├── entities/             # Pure Dart entities
│   │   ├── repositories/         # Abstract repository interfaces
│   │   └── usecases/             # Business use cases
│   ├── presentation/
│   │   ├── providers/            # Riverpod providers
│   │   ├── screens/
│   │   │   ├── auth/             # Login, register, forgot password
│   │   │   ├── onboarding/       # Language selection, goal setup
│   │   │   ├── home/             # Dashboard, streak, today's lesson
│   │   │   ├── lesson/           # Daily lesson flow (5 words)
│   │   │   ├── review/           # Spaced repetition review
│   │   │   ├── quiz/             # All quiz types
│   │   │   ├── ai_chat/          # AI voice conversation
│   │   │   ├── profile/          # Profile, settings, subscription
│   │   │   └── support/          # Support tickets, FAQ
│   │   └── widgets/              # Shared UI components
│   └── main.dart
│
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Settings (pydantic-settings)
│   │   │   ├── database.py       # Async engine + session
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   ├── dependencies.py   # FastAPI Depends()
│   │   │   └── exceptions.py     # Custom exception handlers
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic v2 schemas
│   │   ├── repositories/         # DB access layer
│   │   ├── services/             # Business logic
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py     # Main v1 router
│   │   │       └── endpoints/    # Route handlers
│   │   └── main.py               # FastAPI app factory
│   ├── admin/
│   │   ├── routers/              # Admin route handlers
│   │   ├── templates/            # Jinja2 HTML templates
│   │   └── static/               # CSS, JS assets
│   ├── migrations/               # Alembic migrations
│   ├── tests/                    # pytest test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
│
├── docker-compose.yml
├── docs/                         # Architecture docs (this folder)
└── replit.md
```
