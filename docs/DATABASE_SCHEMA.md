# Learn 5 by 5 — Database Schema

## Tables Overview

| Table | Purpose |
|-------|---------|
| `users` | App users (Learners) |
| `languages` | Supported languages (EN, AR, FR, ES, DE) |
| `word_categories` | Thematic groupings (Travel, Food, etc.) |
| `words` | Master word list per language |
| `word_translations` | Word meaning in each UI language |
| `word_examples` | Example sentences for each word |
| `daily_lesson_words` | Which 5 words are assigned each day |
| `user_lesson_progress` | Per-user daily lesson completion state |
| `user_word_progress` | Per-user mastery level for each word |
| `spaced_repetition_schedule` | SRS scheduling records |
| `scenarios` | Conversation scenarios for the AI chat |
| `ai_conversations` | AI chat session records |
| `ai_messages` | Individual messages within a session |
| `quiz_attempts` | A single quiz session |
| `quiz_answers` | Individual answers within a quiz attempt |
| `subscription_plans` | Free / Premium / Lifetime plan definitions |
| `subscriptions` | User ↔ plan relationships |
| `support_tickets` | User support requests |
| `support_messages` | Messages within a ticket |
| `notifications` | Notification records |
| `app_settings` | Global app configuration (admin-controlled) |
| `admin_users` | Admin dashboard users |

---

## Table Definitions

### `languages`
```sql
CREATE TABLE languages (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(5)  NOT NULL UNIQUE,   -- 'en', 'ar', 'fr', 'es', 'de'
    name_en     VARCHAR(50) NOT NULL,
    name_native VARCHAR(50) NOT NULL,
    is_ui_lang  BOOLEAN     NOT NULL DEFAULT TRUE,  -- can be used as UI language
    is_target   BOOLEAN     NOT NULL DEFAULT TRUE,  -- can be learned
    rtl         BOOLEAN     NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `users`
```sql
CREATE TABLE users (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR(255) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    full_name           VARCHAR(100),
    avatar_url          VARCHAR(500),
    ui_language_id      INT         REFERENCES languages(id),   -- interface language
    target_language_id  INT         REFERENCES languages(id),   -- language being learned
    native_language_id  INT         REFERENCES languages(id),
    level               VARCHAR(20) NOT NULL DEFAULT 'beginner', -- beginner/intermediate/advanced
    timezone            VARCHAR(50),
    daily_goal_time     INT         NOT NULL DEFAULT 10,        -- minutes
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    is_verified         BOOLEAN     NOT NULL DEFAULT FALSE,
    verification_token  VARCHAR(255),
    last_login_at       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `refresh_tokens`
```sql
CREATE TABLE refresh_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,
    device_info VARCHAR(255),
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `word_categories`
```sql
CREATE TABLE word_categories (
    id          SERIAL      PRIMARY KEY,
    name_en     VARCHAR(100) NOT NULL,
    icon        VARCHAR(50),
    sort_order  INT         NOT NULL DEFAULT 0,
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE
);
```

### `words`
```sql
CREATE TABLE words (
    id              SERIAL      PRIMARY KEY,
    language_id     INT         NOT NULL REFERENCES languages(id),
    category_id     INT         REFERENCES word_categories(id),
    word            VARCHAR(100) NOT NULL,
    phonetic        VARCHAR(100),          -- IPA pronunciation
    audio_url       VARCHAR(500),          -- TTS audio file
    difficulty      SMALLINT    NOT NULL DEFAULT 1,  -- 1=easy, 5=hard
    part_of_speech  VARCHAR(30),           -- noun, verb, adj, etc.
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (language_id, word)
);
```

### `word_translations`
```sql
CREATE TABLE word_translations (
    id          SERIAL      PRIMARY KEY,
    word_id     INT         NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    language_id INT         NOT NULL REFERENCES languages(id),  -- translation language
    meaning     TEXT        NOT NULL,
    notes       TEXT,
    UNIQUE (word_id, language_id)
);
```

### `word_examples`
```sql
CREATE TABLE word_examples (
    id          SERIAL      PRIMARY KEY,
    word_id     INT         NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    sentence    TEXT        NOT NULL,
    translation TEXT,                      -- in the user's native language
    audio_url   VARCHAR(500),
    sort_order  INT         NOT NULL DEFAULT 0
);
```

### `daily_lesson_words`
```sql
CREATE TABLE daily_lesson_words (
    id              SERIAL      PRIMARY KEY,
    language_id     INT         NOT NULL REFERENCES languages(id),
    lesson_date     DATE        NOT NULL,
    word_id         INT         NOT NULL REFERENCES words(id),
    sort_order      SMALLINT    NOT NULL DEFAULT 0,   -- 1-5
    UNIQUE (language_id, lesson_date, word_id)
);
```

### `scenarios`
```sql
CREATE TABLE scenarios (
    id              SERIAL      PRIMARY KEY,
    language_id     INT         NOT NULL REFERENCES languages(id),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    context_prompt  TEXT        NOT NULL,   -- system prompt for AI
    difficulty      SMALLINT    NOT NULL DEFAULT 1,
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `user_lesson_progress`
```sql
CREATE TABLE user_lesson_progress (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_date     DATE        NOT NULL,
    language_id     INT         NOT NULL REFERENCES languages(id),
    step_completed  SMALLINT    NOT NULL DEFAULT 0,  -- 0-11 (steps in daily flow)
    is_complete     BOOLEAN     NOT NULL DEFAULT FALSE,
    completed_at    TIMESTAMPTZ,
    score           SMALLINT,                         -- quiz score %
    xp_earned       INT         NOT NULL DEFAULT 0,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, lesson_date, language_id)
);
```

### `user_word_progress`
```sql
CREATE TABLE user_word_progress (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_id         INT         NOT NULL REFERENCES words(id),
    mastery_level   SMALLINT    NOT NULL DEFAULT 0,  -- 0=new, 5=mastered
    ease_factor     FLOAT       NOT NULL DEFAULT 2.5, -- SRS ease factor
    interval_days   INT         NOT NULL DEFAULT 1,
    repetitions     INT         NOT NULL DEFAULT 0,
    correct_count   INT         NOT NULL DEFAULT 0,
    incorrect_count INT         NOT NULL DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ,
    next_review_at  TIMESTAMPTZ,
    first_learned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, word_id)
);
```

### `spaced_repetition_schedule`
```sql
CREATE TABLE spaced_repetition_schedule (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_id         INT         NOT NULL REFERENCES words(id),
    scheduled_date  DATE        NOT NULL,
    is_done         BOOLEAN     NOT NULL DEFAULT FALSE,
    quality_rating  SMALLINT,               -- 0-5 SM-2 quality
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_srs_user_date ON spaced_repetition_schedule (user_id, scheduled_date, is_done);
```

### `ai_conversations`
```sql
CREATE TABLE ai_conversations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scenario_id     INT         REFERENCES scenarios(id),
    lesson_date     DATE,
    language_id     INT         NOT NULL REFERENCES languages(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'active',  -- active/completed/abandoned
    ai_feedback     TEXT,                   -- end-of-session feedback
    score           SMALLINT,               -- 0-100
    duration_secs   INT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ
);
```

### `ai_messages`
```sql
CREATE TABLE ai_messages (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID        NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role            VARCHAR(10) NOT NULL,   -- 'user' or 'assistant'
    content         TEXT        NOT NULL,
    audio_url       VARCHAR(500),
    corrections     JSONB,                  -- [{original, corrected, explanation}]
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `quiz_attempts`
```sql
CREATE TABLE quiz_attempts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_date     DATE,
    language_id     INT         NOT NULL REFERENCES languages(id),
    quiz_type       VARCHAR(30) NOT NULL,   -- daily/review/placement
    total_questions INT         NOT NULL,
    correct_answers INT         NOT NULL DEFAULT 0,
    score           SMALLINT    NOT NULL DEFAULT 0,  -- %
    duration_secs   INT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

### `quiz_answers`
```sql
CREATE TABLE quiz_answers (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id      UUID        NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    word_id         INT         REFERENCES words(id),
    question_type   VARCHAR(30) NOT NULL,   -- multiple_choice/fill_blank/arrange/listening/speaking/build_sentence
    question_data   JSONB       NOT NULL,
    user_answer     JSONB,
    is_correct      BOOLEAN     NOT NULL DEFAULT FALSE,
    time_taken_ms   INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `subscription_plans`
```sql
CREATE TABLE subscription_plans (
    id              SERIAL      PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,   -- Free / Premium / Lifetime
    slug            VARCHAR(30) NOT NULL UNIQUE,
    price_usd       DECIMAL(10,2) NOT NULL DEFAULT 0,
    billing_period  VARCHAR(20),            -- monthly / yearly / once
    features        JSONB       NOT NULL DEFAULT '{}',
    ai_chat_limit   INT,                    -- NULL = unlimited
    lesson_limit    INT,                    -- NULL = unlimited
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `subscriptions`
```sql
CREATE TABLE subscriptions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id             INT         NOT NULL REFERENCES subscription_plans(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'active',  -- active/expired/cancelled/trial
    external_id         VARCHAR(255),       -- Stripe subscription ID
    starts_at           TIMESTAMPTZ NOT NULL,
    ends_at             TIMESTAMPTZ,        -- NULL for Lifetime
    cancelled_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sub_user ON subscriptions (user_id, status);
```

### `support_tickets`
```sql
CREATE TABLE support_tickets (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject         VARCHAR(255) NOT NULL,
    category        VARCHAR(50),            -- billing/technical/content/other
    status          VARCHAR(20) NOT NULL DEFAULT 'open',  -- open/in_progress/closed
    priority        VARCHAR(20) NOT NULL DEFAULT 'normal',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);
```

### `support_messages`
```sql
CREATE TABLE support_messages (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id       UUID        NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_type     VARCHAR(10) NOT NULL,   -- 'user' or 'admin'
    sender_id       VARCHAR(255),           -- user UUID or admin ID
    content         TEXT        NOT NULL,
    attachments     JSONB,                  -- [{url, filename, type}]
    is_read         BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `notifications`
```sql
CREATE TABLE notifications (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        REFERENCES users(id) ON DELETE CASCADE,  -- NULL = broadcast
    type            VARCHAR(50) NOT NULL,   -- daily_reminder/review/subscription/system
    title           VARCHAR(255) NOT NULL,
    body            TEXT        NOT NULL,
    data            JSONB,
    is_sent         BOOLEAN     NOT NULL DEFAULT FALSE,
    is_read         BOOLEAN     NOT NULL DEFAULT FALSE,
    scheduled_at    TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `app_settings`
```sql
CREATE TABLE app_settings (
    key         VARCHAR(100) PRIMARY KEY,
    value       JSONB        NOT NULL,
    description VARCHAR(255),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

### `admin_users`
```sql
CREATE TABLE admin_users (
    id              SERIAL      PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Key Relationships

```
users ──────────────────────── user_lesson_progress (1:N)
users ──────────────────────── user_word_progress (1:N)
users ──────────────────────── spaced_repetition_schedule (1:N)
users ──────────────────────── ai_conversations (1:N)
users ──────────────────────── quiz_attempts (1:N)
users ──────────────────────── subscriptions (1:N)
users ──────────────────────── support_tickets (1:N)
users ──────────────────────── notifications (1:N)

words ──────────────────────── word_translations (1:N)
words ──────────────────────── word_examples (1:N)
words ──────────────────────── user_word_progress (1:N)
words ──────────────────────── daily_lesson_words (1:N)

languages ──────────────────── words (1:N)
languages ──────────────────── daily_lesson_words (1:N)
languages ──────────────────── scenarios (1:N)

ai_conversations ───────────── ai_messages (1:N)
quiz_attempts ──────────────── quiz_answers (1:N)
support_tickets ────────────── support_messages (1:N)
subscription_plans ─────────── subscriptions (1:N)
```

---

## Indexes

```sql
-- Performance-critical indexes
CREATE INDEX idx_words_language ON words (language_id, is_active);
CREATE INDEX idx_daily_lesson_date ON daily_lesson_words (language_id, lesson_date);
CREATE INDEX idx_user_word_progress_next ON user_word_progress (user_id, next_review_at);
CREATE INDEX idx_srs_schedule ON spaced_repetition_schedule (user_id, scheduled_date, is_done);
CREATE INDEX idx_ai_conv_user ON ai_conversations (user_id, started_at DESC);
CREATE INDEX idx_tickets_status ON support_tickets (status, created_at DESC);
CREATE INDEX idx_notifications_user ON notifications (user_id, is_read, created_at DESC);
CREATE INDEX idx_subscriptions_user ON subscriptions (user_id, status);
```
