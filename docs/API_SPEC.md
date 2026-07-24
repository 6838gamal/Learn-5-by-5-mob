# Learn 5 by 5 — REST API Specification

**Base URL:** `/api/v1`  
**Auth:** Bearer JWT token in `Authorization` header (except public routes)

---

## Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | Public | Create account |
| POST | `/auth/login` | Public | Login, returns tokens |
| POST | `/auth/refresh` | Public | Refresh access token |
| POST | `/auth/logout` | User | Revoke refresh token |
| POST | `/auth/forgot-password` | Public | Send reset email |
| POST | `/auth/reset-password` | Public | Reset with token |
| POST | `/auth/verify-email` | Public | Verify email token |
| GET  | `/auth/me` | User | Current user info |

---

## Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/users/profile` | User | Get own profile |
| PATCH | `/users/profile` | User | Update profile |
| POST | `/users/avatar` | User | Upload avatar |
| PATCH | `/users/password` | User | Change password |
| DELETE | `/users/account` | User | Delete account |
| GET  | `/users/stats` | User | Learning statistics |

---

## Languages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/languages` | Public | List supported languages |
| GET  | `/languages/{code}` | Public | Language detail |

---

## Lessons

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/lessons/today` | User | Today's 5 words + lesson data |
| GET  | `/lessons/{date}` | User | Lesson for specific date |
| POST | `/lessons/progress` | User | Update step completion |
| GET  | `/lessons/history` | User | Past lesson history |
| GET  | `/lessons/streak` | User | Current streak info |

---

## Words

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/words/{id}` | User | Word detail with translations |
| GET  | `/words/{id}/audio` | User | Word pronunciation audio |
| GET  | `/words/search` | User | Search words |

---

## Review (Spaced Repetition)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/review/due` | User | Words due for review today |
| GET  | `/review/count` | User | Count of due words |
| POST | `/review/submit` | User | Submit review quality rating |
| GET  | `/review/schedule` | User | Upcoming review schedule |

---

## AI Conversation

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/ai/conversation/start` | User | Start a new conversation |
| POST | `/ai/conversation/{id}/message` | User | Send voice message, get reply |
| POST | `/ai/conversation/{id}/end` | User | End session, get feedback |
| GET  | `/ai/conversation/{id}` | User | Get conversation history |
| GET  | `/ai/conversations` | User | List past conversations |
| GET  | `/ai/usage` | User | AI usage stats (for limits) |

---

## Quiz

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/quiz/start` | User | Start a quiz session |
| GET  | `/quiz/{id}/next` | User | Get next question |
| POST | `/quiz/{id}/answer` | User | Submit an answer |
| POST | `/quiz/{id}/complete` | User | Complete quiz, get results |
| GET  | `/quiz/history` | User | Past quiz attempts |

---

## Subscriptions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/subscriptions/plans` | Public | List all plans |
| GET  | `/subscriptions/current` | User | Current subscription |
| POST | `/subscriptions/checkout` | User | Create Stripe checkout session |
| POST | `/subscriptions/cancel` | User | Cancel subscription |
| GET  | `/subscriptions/invoices` | User | Invoice history |
| POST | `/webhooks/stripe` | Public | Stripe webhook receiver |

---

## Support

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/support/tickets` | User | Create ticket |
| GET  | `/support/tickets` | User | List own tickets |
| GET  | `/support/tickets/{id}` | User | Ticket detail + messages |
| POST | `/support/tickets/{id}/messages` | User | Send message |
| POST | `/support/tickets/{id}/attachments` | User | Upload attachment |
| GET  | `/support/faq` | Public | FAQ list |

---

## Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/notifications` | User | List notifications |
| PATCH | `/notifications/{id}/read` | User | Mark as read |
| PATCH | `/notifications/read-all` | User | Mark all as read |
| POST | `/notifications/fcm-token` | User | Register device FCM token |

---

## Standard Response Format

```json
// Success
{
  "success": true,
  "data": { ... },
  "message": null
}

// Error
{
  "success": false,
  "data": null,
  "message": "Human-readable error",
  "code": "ERROR_CODE",
  "details": { ... }
}

// Paginated
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

---

## Key Request/Response Examples

### POST `/auth/login`
```json
// Request
{ "email": "user@example.com", "password": "secret" }

// Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### GET `/lessons/today`
```json
{
  "lesson_date": "2026-07-24",
  "language": { "code": "en", "name_en": "English" },
  "words": [
    {
      "id": 42,
      "word": "serene",
      "phonetic": "/səˈriːn/",
      "audio_url": "https://...",
      "part_of_speech": "adjective",
      "translation": "هادئ",
      "examples": [
        { "sentence": "The lake was serene at dawn.", "audio_url": "..." }
      ]
    }
  ],
  "scenario": { "id": 5, "title": "Morning walk" },
  "progress": { "step_completed": 3, "is_complete": false }
}
```

### POST `/ai/conversation/{id}/message`
```json
// Request (multipart/form-data)
{ "audio": <binary>, "conversation_id": "uuid" }

// Response
{
  "user_transcript": "I want to order a coffee please",
  "ai_text": "Of course! What size would you like?",
  "ai_audio_url": "https://...",
  "corrections": [
    {
      "original": "I want to order",
      "corrected": "I would like to order",
      "explanation": "More polite phrasing"
    }
  ]
}
```

### POST `/review/submit`
```json
// Request
{ "word_id": 42, "quality": 4 }  // quality 0-5 (SM-2)

// Response
{
  "next_review_date": "2026-07-31",
  "interval_days": 7,
  "mastery_level": 3
}
```
