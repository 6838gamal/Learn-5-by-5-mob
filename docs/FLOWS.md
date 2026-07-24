# Learn 5 by 5 — User & System Flows

---

## 1. Authentication Flow

```
┌──────────────┐
│  App Launch  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐     YES   ┌────────────────┐
│  Valid JWT in storage?├──────────►  Home Screen    │
└──────┬───────────────┘           └────────────────┘
       │ NO
       ▼
┌──────────────┐
│  Auth Screen │
├──────────────┤
│  Login       │
│  Register    │
│  Forgot PW   │
└──────┬───────┘
       │
       ▼ Register
┌──────────────────────┐
│  POST /auth/register │
│  → email + password  │
│  → verification email│
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────┐
│  Onboarding Flow        │
│  1. Select target lang  │
│  2. Select UI language  │
│  3. Select level        │
│  4. Set daily goal      │
└──────┬──────────────────┘
       │
       ▼
┌──────────────┐
│  Home Screen │
└──────────────┘

       │ Login
       ▼
┌──────────────────────┐
│  POST /auth/login    │
│  → access_token (15m)│
│  → refresh_token(30d)│
└──────┬───────────────┘
       │
       ▼ (token expired)
┌──────────────────────┐
│ POST /auth/refresh   │
│  → new access_token  │
└──────────────────────┘
```

---

## 2. Daily Lesson Flow (Core User Journey)

Each day the user follows these 11 steps:

```
Step 1: Word Introduction
  ┌──────────────────────────────┐
  │  Show word (large)           │
  │  Phonetic + part of speech   │
  │  [Listen to pronunciation]   │
  │  Translation / meaning       │
  └──────────┬───────────────────┘
             │ (repeat for all 5 words)
             ▼

Step 2: Examples
  ┌──────────────────────────────┐
  │  3 example sentences per word│
  │  With audio playback         │
  └──────────┬───────────────────┘
             ▼

Step 3: 5 Daily Sentences
  ┌──────────────────────────────┐
  │  5 sentences using today's   │
  │  words in real context       │
  └──────────┬───────────────────┘
             ▼

Step 4: Scenario Introduction
  ┌──────────────────────────────┐
  │  Show today's scenario       │
  │  e.g. "Ordering at a café"   │
  │  Preview key phrases         │
  └──────────┬───────────────────┘
             ▼

Step 5: AI Voice Conversation
  ┌──────────────────────────────┐
  │  User speaks via microphone  │
  │  AI responds using scenario  │
  │  Real-time corrections shown │
  └──────────┬───────────────────┘
             ▼

Step 6: AI Feedback
  ┌──────────────────────────────┐
  │  Summary of conversation     │
  │  Errors + corrections        │
  │  Score + encouragement       │
  │  Suggested words             │
  └──────────┬───────────────────┘
             ▼

Step 7: Quiz
  ┌──────────────────────────────┐
  │  7 questions mixing types:   │
  │  - Multiple choice           │
  │  - Fill in the blank         │
  │  - Arrange words             │
  │  - Listening                 │
  │  - Pronunciation             │
  └──────────┬───────────────────┘
             ▼

Step 8: Results + XP
  ┌──────────────────────────────┐
  │  Score, XP earned, streak    │
  │  Words added to SRS queue    │
  └──────────┬───────────────────┘
             ▼

Step 9: SRS Scheduling
  ┌──────────────────────────────┐
  │  SM-2 algorithm calculates   │
  │  next review date per word   │
  │  Based on quiz performance   │
  └──────────────────────────────┘
```

---

## 3. Review Flow (Spaced Repetition)

```
┌────────────────────────────────┐
│  Home Screen shows:            │
│  "X words due for review today"│
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│  Load words where              │
│  next_review_at <= NOW()       │
│  for this user                 │
└──────────┬─────────────────────┘
           │
           ▼ (per word)
┌────────────────────────────────┐
│  Show word                     │
│  Ask: "Do you remember it?"    │
│  [Show Answer] → rate 0-5      │
└──────────┬─────────────────────┘
           │
           ▼ SM-2 Algorithm
┌────────────────────────────────┐
│  quality >= 3 → increase       │
│              interval/ease     │
│  quality < 3  → reset interval │
│  Update user_word_progress     │
│  Create new SRS entry          │
└────────────────────────────────┘
```

**SM-2 Formula:**
```
EF(next) = EF(prev) + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
interval: if reps == 0 → 1 day
           if reps == 1 → 6 days
           else → prev_interval * EF
```

---

## 4. AI Conversation Flow

```
Flutter App                    FastAPI Backend              OpenAI
    │                               │                          │
    │── POST /ai/conversation/start ►│                          │
    │   {lesson_date, scenario_id}   │                          │
    │◄── {conversation_id, prompt} ──│                          │
    │                               │                          │
    │ [User speaks]                  │                          │
    │── POST /ai/conversation/message►│                          │
    │   {audio_blob, conversation_id}│                          │
    │                               │── Whisper STT ──────────►│
    │                               │◄── transcript ───────────│
    │                               │── GPT-4o (chat) ────────►│
    │                               │   (with today's words)   │
    │                               │◄── AI reply text ────────│
    │                               │── TTS (ElevenLabs/OpenAI)►│
    │                               │◄── audio bytes ──────────│
    │◄── {transcript, reply, audio,──│                          │
    │     corrections, ai_text}      │                          │
    │                               │                          │
    │ [User ends session]            │                          │
    │── POST /ai/conversation/end ──►│                          │
    │   {conversation_id}            │                          │
    │                               │── GPT-4o (feedback) ────►│
    │                               │◄── feedback JSON ────────│
    │◄── {score, feedback, errors} ──│                          │
```

---

## 5. Subscription Flow

```
┌─────────────────────────────────┐
│  User hits Premium feature      │
│  (or opens Subscription screen) │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Show plan comparison:          │
│  Free vs Premium vs Lifetime    │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Select plan → Stripe Checkout  │
│  POST /subscriptions/create     │
│  → Stripe payment intent        │
└──────────┬──────────────────────┘
           │ Payment success
           ▼
┌─────────────────────────────────┐
│  Stripe webhook →               │
│  POST /webhooks/stripe          │
│  → Update subscription record   │
│  → Unlock premium features      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  User notified + features active│
└─────────────────────────────────┘
```

---

## 6. Support Flow

```
User                        App                        Admin Dashboard
 │                           │                               │
 │── Create ticket ─────────►│                               │
 │   {subject, category,     │── POST /support/tickets ─────►│
 │    description}           │                               │
 │◄── ticket created ────────│                               │
 │                           │                          New ticket notification
 │                           │                               │
 │── Send message ──────────►│                               │
 │   + optional attachment   │── POST /support/messages ────►│
 │◄── message saved ─────────│                               │
 │                           │                               │
 │                           │                        Admin replies
 │                           │◄── POST /support/messages ────│
 │◄── push notification ─────│                               │
 │                           │                               │
 │── View ticket history ───►│                               │
 │◄── messages list ─────────│                               │
```

---

## 7. Admin Flow

```
Admin Dashboard (Jinja2 + HTMX)
│
├── /admin/login              → session auth
│
├── /admin/dashboard          → metrics overview
│   ├── Active users today
│   ├── Revenue
│   ├── AI conversations
│   └── System health
│
├── /admin/users              → list, search, filter
│   ├── /admin/users/{id}     → detail + edit
│   └── /admin/users/{id}/activity
│
├── /admin/content
│   ├── /admin/content/words  → CRUD words
│   ├── /admin/content/categories
│   ├── /admin/content/examples
│   ├── /admin/content/scenarios
│   └── /admin/content/daily-lessons → assign words to days
│
├── /admin/languages          → manage languages + translations
│
├── /admin/ai
│   ├── /admin/ai/prompts     → edit system prompts
│   ├── /admin/ai/usage       → token usage stats
│   └── /admin/ai/settings    → model config
│
├── /admin/subscriptions
│   ├── /admin/subscriptions/plans → CRUD plans
│   └── /admin/subscriptions/list  → all subscriptions
│
├── /admin/support
│   ├── /admin/support/tickets     → list + filter
│   └── /admin/support/tickets/{id} → reply
│
├── /admin/notifications      → send push notifications
│
└── /admin/settings           → app config, backups, logs
```
