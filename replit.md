# Learn 5 by 5

تطبيق Flutter لتعلم 5 كلمات جديدة يومياً باستخدام الذكاء الاصطناعي والتكرار المتباعد.

## Architecture

| Layer | Stack | Notes |
|-------|-------|-------|
| Mobile / Web frontend | Flutter (Dart) | runs on port 5000 (debug server) |
| REST API backend | FastAPI (Python) | hosted externally on Render.com |
| Database | PostgreSQL | hosted on Render.com (Virginia) |

## How to run

Single workflow: **Start application** — starts the Flutter debug web server on port 5000.

The backend API is external: `https://learn-5-by-5-api-backend.onrender.com`

> **Note:** Render.com free tier has ~20-25 s cold starts. The first login after a period of inactivity may be slow — this is expected and the timeout is set to 60 s to accommodate it.

## Environment variables

| Variable | Value / Purpose |
|----------|----------------|
| `API_BASE_URL` | `https://learn-5-by-5-api-backend.onrender.com/api/v1` — backend base URL passed to Flutter via dart-define |
| `GOOGLE_WEB_CLIENT_ID` | Google OAuth Web Client ID for Google Sign-In |

## Key files

- `lib/core/config/app_config.dart` — API URL, timeouts (connect: 30 s, receive: 60 s)
- `lib/core/network/dio_client.dart` — Dio HTTP client + AuthInterceptor (token refresh)
- `lib/presentation/providers/auth_provider.dart` — Google login flow, token storage, user state
- `lib/core/router/app_router.dart` — GoRouter with auth redirect guard
- `backend/` — FastAPI source (runs on Render.com, not locally)

## Known issues / follow-ups

- Google Sign-In requires `GOOGLE_WEB_CLIENT_ID` secret to be set
- OpenAI, Stripe, Firebase keys needed for AI/payment/notification features
- Render.com backend cold starts can take ~22 s; timeout is set to 60 s

## User preferences
