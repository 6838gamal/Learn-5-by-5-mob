# Learn 5 by 5 — Implementation Plan

## Phase Overview

| Phase | Name | Focus | Deliverable |
|-------|------|-------|-------------|
| 1 | Foundation | Backend scaffold, DB, Auth | Working API with auth |
| 2 | Core Lesson | Daily lesson, words, SRS | Full lesson flow |
| 3 | AI Layer | Voice conversation, feedback | AI chat works end-to-end |
| 4 | Flutter App | All screens, navigation | Mobile app complete |
| 5 | Subscriptions | Stripe integration, plan gates | Monetization live |
| 6 | Admin Dashboard | Jinja2 admin UI | Admin can manage everything |
| 7 | Notifications | Push, scheduling, reminders | Engagement loop |
| 8 | Support | Ticket system, FAQ | Customer support live |
| 9 | Production | Docker, CI/CD, hardening | Production-ready |

---

## Phase 1 — Foundation

**Goal:** Working backend with database, auth, and project structure.

### Tasks
- [ ] Set up FastAPI project with clean architecture layout
- [ ] Configure PostgreSQL with SQLAlchemy 2.0 (async)
- [ ] Create all database models (SQLAlchemy ORM)
- [ ] Run Alembic initial migration
- [ ] Implement JWT auth (register, login, refresh, logout)
- [ ] Email verification flow
- [ ] Forgot/reset password flow
- [ ] User profile CRUD
- [ ] Global error handling middleware
- [ ] Request logging middleware
- [ ] Rate limiting (slowapi)
- [ ] CORS configuration
- [ ] Seed script: languages, subscription plans

**Done when:** `POST /auth/login` returns tokens, `GET /auth/me` returns user profile.

---

## Phase 2 — Core Lesson Flow

**Goal:** A user can complete a full daily lesson (steps 1–9).

### Tasks
- [ ] Word model + CRUD API
- [ ] Word categories API
- [ ] Word translations (per UI language)
- [ ] Word example sentences
- [ ] Daily lesson words assignment (admin or auto)
- [ ] `GET /lessons/today` endpoint
- [ ] Lesson progress tracking (step-by-step)
- [ ] Streak calculation
- [ ] Quiz engine: question generation for all 7 types
- [ ] Quiz attempt + answer API
- [ ] SM-2 spaced repetition algorithm
- [ ] SRS scheduling service
- [ ] Review due words API
- [ ] Review submission + recalculation
- [ ] XP / scoring system

**Done when:** User can complete lesson steps 1–9 and words are scheduled for review.

---

## Phase 3 — AI Conversation Layer

**Goal:** Voice conversation with AI using today's words.

### Tasks
- [ ] OpenAI client setup (async, with retry)
- [ ] Whisper STT: transcribe user audio
- [ ] GPT-4o chat: AI conversation with scenario context
- [ ] TTS: generate AI voice response (OpenAI TTS or ElevenLabs)
- [ ] AI conversation session management
- [ ] Real-time error/correction detection in responses
- [ ] End-of-session feedback generation
- [ ] AI usage tracking (for subscription limits)
- [ ] Scenario management (DB + API)
- [ ] Scenario assignment to daily lessons

**Done when:** User can have a voice conversation with AI and receive a scored feedback report.

---

## Phase 4 — Flutter App

**Goal:** Complete mobile app covering all screens.

### Tasks
- [ ] Project structure: Riverpod + GoRouter + Dio
- [ ] Localization: AR, EN, FR, ES, DE (ARB files)
- [ ] Theme: light/dark/system
- [ ] Auth screens: login, register, forgot password
- [ ] Onboarding: language selection, level, goal
- [ ] Home screen: streak, today's lesson card, review card
- [ ] Lesson flow screens (steps 1–9)
- [ ] Word card widget (with audio)
- [ ] AI chat screen: microphone, waveform, corrections
- [ ] Quiz screens: all 7 question types
- [ ] Review screen (SRS flashcard style)
- [ ] Profile screen
- [ ] Settings screen (theme, language, notifications)
- [ ] Subscription screen + Stripe checkout (WebView)
- [ ] Support: ticket list, ticket detail, message thread
- [ ] Notification center
- [ ] Offline handling + error states

**Done when:** User can complete full learning journey on device.

---

## Phase 5 — Subscriptions

**Goal:** Monetization layer with feature gating.

### Tasks
- [ ] Stripe SDK integration (backend)
- [ ] Plan management API
- [ ] Checkout session creation
- [ ] Stripe webhook handler
- [ ] Subscription status middleware (feature gating)
- [ ] AI usage limit enforcement (Free plan)
- [ ] Lesson limit enforcement (Free plan)
- [ ] Subscription management screen (cancel, upgrade)
- [ ] Invoice history

**Done when:** Free users are gated, Premium users have full access, Stripe payments flow end-to-end.

---

## Phase 6 — Admin Dashboard

**Goal:** Full admin UI for content and operations.

### Tasks
- [ ] Admin auth (session-based, separate from API)
- [ ] Dashboard home: metrics, charts (Chart.js)
- [ ] Users: list, search, filter, detail, edit, suspend
- [ ] Content: words CRUD (with translations, examples)
- [ ] Content: categories, scenarios, daily lesson assignment
- [ ] Languages: manage, add translations
- [ ] AI settings: prompts, model config, usage limits
- [ ] Subscriptions: plans CRUD, pricing, coupons
- [ ] Support: ticket queue, reply, close
- [ ] Notifications: send broadcast / targeted
- [ ] Settings: app config, email, AI keys
- [ ] Logs viewer

**Done when:** Admin can manage all content and operations without touching the database directly.

---

## Phase 7 — Notifications

**Goal:** Engagement loop via push notifications.

### Tasks
- [ ] FCM token registration API
- [ ] Celery + Redis task queue
- [ ] Daily reminder scheduler (per user timezone)
- [ ] Review due reminder
- [ ] Subscription expiry warning
- [ ] Admin broadcast notifications
- [ ] Notification center in app

**Done when:** Users receive daily lesson reminders and review nudges.

---

## Phase 8 — Support System

**Goal:** In-app support ticketing.

### Tasks
- [ ] Ticket creation + status tracking
- [ ] Messaging thread per ticket
- [ ] File attachment upload (S3/Cloudflare R2)
- [ ] Admin reply flow
- [ ] Push notification on admin reply
- [ ] FAQ page (admin-managed content)

**Done when:** Users can raise and resolve support issues without email.

---

## Phase 9 — Production Readiness

**Goal:** Deploy-ready, hardened, observable.

### Tasks
- [ ] Docker Compose: app + db + redis + celery
- [ ] Dockerfile for backend (multi-stage)
- [ ] Health check endpoints
- [ ] Structured logging (JSON, log levels)
- [ ] Sentry error tracking integration
- [ ] Database connection pooling (pgBouncer or asyncpg pool)
- [ ] Alembic migration CI check
- [ ] pytest test suite (>70% coverage on services)
- [ ] API integration tests
- [ ] `.env.example` with all required vars documented
- [ ] Security audit: rate limits, input validation, OWASP basics
- [ ] Performance: DB query analysis, N+1 detection
- [ ] README with full setup instructions

**Done when:** App deploys from `docker-compose up` in a clean environment with zero manual steps.

---

## Module Breakdown

```
Module                Owner           Depends On
──────────────────────────────────────────────────
Auth                  Backend         Database
User Profile          Backend         Auth
Languages             Backend         Database
Words & Content       Backend         Languages
Lesson Engine         Backend         Words, Auth
SRS / Review          Backend         Lesson Engine
AI Conversation       Backend         OpenAI, Lesson Engine
Quiz Engine           Backend         Words, Lesson Engine
Subscriptions         Backend         Stripe, Auth
Support System        Backend         Auth, Storage
Notifications         Backend         FCM, Celery
Admin Dashboard       Backend         All modules
Flutter App           Mobile          Backend API
```
