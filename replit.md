# Learn 5 by 5

تطبيق لتعلم 5 كلمات جديدة يومياً باستخدام الذكاء الاصطناعي والتكرار المتباعد.

## Architecture

| Layer | Stack | Notes |
|-------|-------|-------|
| Web frontend | FastAPI + Jinja2 + Tailwind + Alpine.js + HTMX | runs on port 5000 |
| Flutter mobile app | Flutter (Dart) | in `lib/` — separate build target |
| REST API backend | FastAPI (Python) | hosted externally on Render.com |
| Database | PostgreSQL | hosted on Render.com (Virginia) |

## How to run

Single workflow: **Start application** — starts the FastAPI web server on port 5000.

```
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

The backend API is external: `https://learn-5-by-5-api-backend.onrender.com`

> **Note:** Render.com free tier has ~20-25 s cold starts. The first login after a period of inactivity may be slow — this is expected and the timeout is set to 60 s to accommodate it.

## App screens (web — `app/`)

| Route | Template | Status |
|-------|----------|--------|
| `/` → `/splash` | `app/templates/splash.html` | ✅ Animated splash screen |
| `/auth/login` | `app/templates/auth/login.html` | ✅ Google Sign-In only |
| `/onboarding` | `app/templates/onboarding.html` | ✅ 3-step language setup |
| `/home` | `app/templates/home.html` | ✅ Dashboard |
| `/lesson` | `app/templates/lesson.html` | ✅ 5-word lesson flow |
| `/review` | `app/templates/review.html` | ✅ SRS flashcard review |
| `/quiz` | `app/templates/quiz.html` | ✅ Multiple-choice quiz |
| `/ai-chat` | `app/templates/ai_chat.html` | ✅ AI tutor chat |
| `/profile` | `app/templates/profile/index.html` | ✅ Profile & stats |
| `/profile/settings` | `app/templates/profile/settings.html` | ✅ Theme & language |
| `/subscription` | `app/templates/profile/subscription.html` | ✅ Plans & upgrade |
| `/notifications` | `app/templates/notifications.html` | ✅ Notification list |
| `/support` | `app/templates/support/tickets.html` | ✅ Support tickets |
| `/support/{id}` | `app/templates/support/ticket_detail.html` | ✅ Ticket thread |

## Environment variables

| Variable | Value / Purpose |
|----------|----------------|
| `API_BASE_URL` | `https://learn-5-by-5-api-backend.onrender.com/api/v1` — backend base URL |
| `GOOGLE_WEB_CLIENT_ID` | Google OAuth Web Client ID for Google Sign-In |
| `SESSION_SECRET` | Secret key for Starlette session middleware (set as Replit Secret) |

## Key files

- `app/main.py` — FastAPI app entry point, splash route, router mounts
- `app/config.py` — Settings via pydantic-settings (reads env vars + SESSION_SECRET)
- `app/routers/auth.py` — Google Sign-In only auth flow
- `app/services/api_client.py` — httpx wrapper proxying requests to backend API
- `app/dependencies.py` — `require_auth` guard + `get_api_client` factory
- `app/templates/base.html` — Shell layout with sidebar nav (Tailwind + Alpine + HTMX)
- `backend/` — FastAPI source (runs on Render.com, not locally)

## Framework notes

- **Starlette 1.x**: `TemplateResponse` signature is `(request, name, context)` — `request` is the first arg, NOT inside the context dict.
- **Auth**: Google Sign-In only. No email/password. No register page.
- **Session**: Starlette `SessionMiddleware`; token stored in `request.session["access_token"]`.

## User preferences
