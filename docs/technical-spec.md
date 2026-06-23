# Delta One — Technical Specification

> Version 2.0 · June 2026  
> Consolidates architecture_plan.txt, program-architecture.txt, and implementation.txt

---

## 1. Overview

Delta One is a two-tier trading intelligence platform. It combines a live 4-hour liquidity sweep trading bot with an educational web application that teaches users why markets move.

**Core components:**
- A **standalone trading bot** (`sweep_main.py`) running on Alpaca (paper)
- A **Flask web app** with a 3-column terminal-multiplexer workspace
- A **curriculum** of 5 modules / 22 lessons (~76 min total)
- A **signal explainer** that turns bot events into educational text
- An **AI teaching assistant** powered by Groq (llama3-70b)
- An **admin panel** for monitoring usage, users, system, and bot health

**Target users:** Retail traders who want to understand institutional market mechanics.

---

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Backend | Flask 3.x (create_app factory pattern) |
| Database | PostgreSQL 16 (local), SQLAlchemy ORM |
| Migrations | Flask-Migrate / Alembic |
| Auth | Flask-Login + Werkzeug password hashing |
| Templates | Jinja2 (workspace, admin, landing, auth, errors) |
| Frontend JS | Vanilla JS — no framework |
| AI | Groq API (llama3-70b-8192) via `groq` SDK |
| CSS | Custom per-module (base.css, workspace.css, admin.css, landing.css) |
| Trading | Alpaca Trade API (`alpaca-py`) |
| Backtesting | yfinance data + local engine |
| Payments | Stripe — **not yet integrated** |
| Hosting | Local dev; TBD for production |

---

## 3. System Architecture

Two independent processes share a single PostgreSQL database:

```
┌──────────────────────────┐     ┌──────────────────────────┐
│   sweep_main.py          │     │   Flask Web App          │
│   (standalone bot)       │     │   (flask run)            │
│                          │     │                          │
│   4H loop ───► Alpaca    │     │   Landing / Auth         │
│   Strategy engine        │     │   Workspace (3-col UX)   │
│   Risk management        │     │   Curriculum viewer      │
│   Logging (CSV + DB)     │     │   AI assistant           │
│                          │     │   Admin panel            │
└──────────┬───────────────┘     └──────────┬───────────────┘
           │                                │
           └─────────── PostgreSQL ─────────┘
                       delta_one
                   ┌──────────────┐
                   │  bot_events  │ ←──── Bot writes, web app reads
                   │  users       │ ←──── Web app manages
                   │  modules     │
                   │  lessons     │
                   │  progress    │
                   │  waitlist    │
                   │  sessions    │
                   │  ai_interact │
                   └──────────────┘
```

**Bot → App bridge:** `sweep_csv.py` writes each event to both `data/bot_events.csv` (legacy) and the `bot_events` DB table (conditional, graceful fallback). The Flask app reads exclusively from the DB.

---

## 4. Data Model

### 4a. `users`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| email | VARCHAR(255) UNIQUE NOT NULL | Lowercased on write |
| password_hash | VARCHAR(255) NOT NULL | Werkzeug |
| display_name | VARCHAR(100) | |
| tier | VARCHAR(20) DEFAULT `core` | `core` \| `pro` \| `admin` |
| is_active | BOOLEAN DEFAULT TRUE | |
| onboarding_complete | BOOLEAN DEFAULT FALSE | |
| avatar_url | VARCHAR(500) | Future |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | Auto-update |
| last_login_at | TIMESTAMPTZ | |

Relationships: `progress` (→ UserProgress), `ai_interactions` (→ AiInteraction)

### 4b. `sessions`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users) | ON DELETE CASCADE |
| token | VARCHAR(255) UNIQUE | |
| ip_address | VARCHAR(45) | |
| user_agent | TEXT | |
| expires_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |

### 4c. `modules`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| title | VARCHAR(200) NOT NULL | |
| slug | VARCHAR(200) UNIQUE NOT NULL | e.g. `what-is-the-market` |
| description | TEXT | |
| icon | VARCHAR(50) | SVG icon name |
| sort_order | INTEGER DEFAULT 0 | Display order |
| is_published | BOOLEAN DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

Relationships: `lessons` (→ Lesson, cascade delete)

### 4d. `lessons`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| module_id | UUID (FK → modules) | ON DELETE CASCADE |
| title | VARCHAR(200) NOT NULL | |
| slug | VARCHAR(200) NOT NULL | Unique per module |
| content | TEXT | HTML content |
| content_type | VARCHAR(20) DEFAULT `html` | `html` \| `markdown` |
| sort_order | INTEGER DEFAULT 0 | |
| estimated_minutes | INTEGER DEFAULT 5 | |
| is_published | BOOLEAN DEFAULT FALSE | |
| concept_tags | TEXT[] | e.g. `{liquidity}` |
| related_signal_type | VARCHAR(50) | Links to bot signal type |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

UNIQUE(module_id, slug)

### 4e. `user_progress`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users) | ON DELETE CASCADE |
| lesson_id | UUID (FK → lessons) | ON DELETE CASCADE |
| status | VARCHAR(20) DEFAULT `not_started` | `not_started` \| `in_progress` \| `completed` |
| score | INTEGER | Future: quiz score |
| completed_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

UNIQUE(user_id, lesson_id)

### 4f. `bot_events`

| Column | Type | Notes |
|---|---|---|
| id | BIGSERIAL (PK) | Auto-increment |
| timestamp | TIMESTAMPTZ | ET timezone stored |
| event | VARCHAR(50) NOT NULL | `scan` \| `entry` \| `exit` |
| symbol | VARCHAR(10) | |
| side | VARCHAR(10) | `long` \| `short` \| `none` |
| price | DOUBLE PRECISION | |
| qty | INTEGER | |
| status | VARCHAR(30) | `filled` \| `closed` |
| message | TEXT | Free-form context |
| created_at | TIMESTAMPTZ | |

INDEX(event, timestamp)

### 4g. `waitlist_entries`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| email | VARCHAR(255) UNIQUE NOT NULL | |
| source | VARCHAR(50) DEFAULT `landing` | |
| converted | BOOLEAN DEFAULT FALSE | Later became a user? |
| created_at | TIMESTAMPTZ | |

### 4h. `ai_interactions`

| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users) | Nullable |
| message | TEXT NOT NULL | User prompt |
| response | TEXT NOT NULL | AI reply |
| tokens_used | INTEGER DEFAULT 0 | |
| model_name | VARCHAR(100) | e.g. `llama3-70b-8192` |
| tier | VARCHAR(20) | `core` \| `pro` |
| created_at | TIMESTAMPTZ | |

---

## 5. Route Map

### 5a. Public Blueprint (`public_bp` — no auth)

| Method | Path | Handler | Notes |
|---|---|---|---|
| GET | `/` | `landing` | Full landing page |
| GET | `/pricing` | `pricing` | Pricing tiers (static) |
| POST | `/waitlist` | `waitlist` | JSON: `{email}` |

### 5b. Auth Blueprint (`auth_bp`)

| Method | Path | Handler | Notes |
|---|---|---|---|
| GET | `/auth/login` | `login_page` | Login form |
| POST | `/auth/login` | `login_action` | Rate limited |
| GET | `/auth/signup` | `signup_page` | Signup form |
| POST | `/auth/signup` | `signup_action` | Rate limited |
| GET | `/auth/logout` | `logout_action` | Clears session |

### 5c. API Blueprint (`api_bp` — CSRF exempt, `@login_required`)

| Method | Path | Handler | Notes |
|---|---|---|---|
| GET | `/api/summary` | `api_summary` | Bot status, events, positions |
| GET | `/api/activity` | `api_activity` | Last 60 min event counts |
| GET | `/api/symbol/<symbol>` | `api_symbol` | Per-symbol detail |
| GET | `/api/footer` | `api_footer` | Recent errors, skips, counts |
| GET | `/api/concepts` | `api_concepts` | Concept graph (16 nodes, 19 edges) |
| GET | `/api/concepts/<id>` | `api_concept_detail` | Concept detail |
| GET | `/api/signals/live` | `api_live_signals` | Recent signals with explanations |
| GET | `/api/signals/history` | `api_signal_history` | Paginated signal history |
| POST | `/api/ai/ask` | `api_ai_ask` | Groq AI query (rate limited) |
| GET | `/api/admin/ai/usage/today` | `admin_ai_usage` | Admin-only AI usage |

### 5d. Workspace Blueprint (`workspace_bp` — CSRF exempt, `@login_required`)

| Method | Path | Handler | Notes |
|---|---|---|---|
| GET | `/workspace/` | `shell` | 3-column terminal multiplexer |
| GET | `/workspace/api/modules` | `api_modules` | Module list with progress |
| GET | `/workspace/api/modules/<slug>` | `api_module_detail` | Module with lesson list |
| GET | `/workspace/api/lessons/<ms>/<ls>` | `api_lesson_detail` | Lesson content + prev/next |
| POST | `/workspace/api/lessons/<ms>/<ls>/complete` | `api_mark_complete` | Mark lesson done |

### 5e. Admin Blueprint (`admin_bp` — `@login_required` + `@_admin_required`)

| Method | Path | Handler | Notes |
|---|---|---|---|
| GET | `/admin/` | `shell` | Admin panel |
| GET | `/admin/api/usage` | `api_usage` | AI query stats (today, top users, 7d) |
| GET | `/admin/api/users` | `api_users` | All users (`?q=` filter) |
| GET | `/admin/api/users/<id>` | `api_user_detail` | User + AI interactions |
| POST | `/admin/api/users/<id>/tier` | `api_user_tier` | Change tier |
| GET | `/admin/api/system` | `api_system` | DB row counts |
| GET | `/admin/api/bot/health` | `api_bot_health` | Bot status + events + log tail |

---

## 6. Frontend Architecture

### 6a. Workspace: 3-Column Terminal Multiplexer

The primary authenticated UX is a fixed 3-column CSS grid layout with a Linux terminal aesthetic.

```
┌─ Status bar (28px) ─────────────────────────────────────────────────────┐
│ delta-one | workspace | username               admin | logout           │
├──── 220px ────┬─────────── 1fr ──────────┬────── 280px ────────────────┤
│ NAV           │ CONTENT PANEL            │ RIGHT COLUMN                 │
│               │                          │                              │
│ [Dash]        │ Renders inline:          │ Signals feed (15s auto-poll) │
│ [Less]        │  • Dashboard summary     │ ┌─ signal ───────────────┐  │
│ [Maps]        │  • Module/lesson list    │ │ event sym desc         │  │
│               │  • Lesson content        │ └────────────────────────┘  │
│ Concept Tree  │  • Concept detail        │                              │
│ (collapsible) │  • Signal detail         │ Notes textarea              │
│               │                          │ (localStorage)              │
│ Module 0      │ AI TERMINAL (160-200px)  │                              │
│ Module 1      │ ┌──────────────────────┐ │                              │
│ Module 2      │ │ > explain gamma      │ │                              │
│ Module 3      │ │ Γ measures rate of   │ │                              │
│ Module 4      │ │ change of delta...   │ │                              │
│               │ └──────────────────────┘ │                              │
└───────────────┴──────────────────────────┴──────────────────────────────┘
```

**Key design choices:**
- Near-black background (`#0a0b0c`), dark surfaces (`#0f1114`), 1px borders (`#1a1d21`)
- JetBrains Mono font, zero border-radius
- Color only for active state, accent, and signal severity
- No gradients, no glow, no SaaS styling
- Responsive breakpoint at 900px (stacks to single column)

**JavaScript (`static/workspace.js`):**
- `showView()` — nav-driven content panel switching
- Concept tree collapse/expand (5 module groups, 16 concept nodes)
- Inline lesson/module rendering via internal API calls
- 15s signal polling from `/api/signals/live`
- Notes localStorage save/restore
- AI terminal: Enter → POST `/api/ai/ask` → append response
- `handleFocusParam()` — reads `?focus=` query param on boot

### 6b. Admin Panel

Same 3-column terminal layout:
- **Left:** Admin nav (Usage / Users / System / Bot Health)
- **Center:** Content pane + AI terminal at bottom
- **Right:** Quick stats (total users, AI today, events, bot status dot) — 15s polling

### 6c. Unauthenticated Pages

- **Landing (`/`)** — Hero, ticker, stats counters, pricing table, waitlist form
- **Pricing (`/pricing`)** — Static Core vs Pro tiers (pre-Stripe)
- **Login/Signup** — Flask-WTF forms with validation and rate limiting
- **Errors** — Custom 404 and 500 pages

All extend `base.html` which pulls in `components/nav.html` (Pricing, Login, Sign Up — anonymous only).

---

## 7. Bot Engine

### 7a. Strategy: 4H Liquidity Sweep

The core thesis: when price sweeps beyond a key level and fails to hold, the breakout was a trap — a reversal trade is available in the opposite direction.

**Entry confluences (3 layers):**
1. **4H range structure** — built from 1H data
2. **Breakout and reentry detection** — on the 5M execution layer
3. **50 EMA trend filter** — blocks counter-trend entries

**Risk management:**
- ATR-based stops with swing structure confirmation
- Minimum 1.5R reward-to-risk
- 2% equity risk per trade
- Circuit breakers: max daily loss, max consecutive losses

### 7b. Bot Files

| File | Role |
|---|---|
| `sweep_main.py` | Live trading loop (standalone) |
| `sweep_strategy.py` | Pure strategy logic (Position, signals, risk calcs) |
| `sweep_data.py` | Data fetcher (Alpaca, 5min + 1H bars) |
| `sweep_backtest.py` | Backtest engine (yfinance) |
| `sweep_config.py` | All tunable parameters |
| `sweep_state.py` | Position state (positions.json) |
| `sweep_runner.py` | TradeTracker helper |
| `sweep_csv.py` | Dual-write logger (CSV + DB) |
| `bot_logger.py` | Logging setup (stdout + file) |

### 7c. Signal Types

The SignalExplainerService maps 7 event types to educational explanations:

| Event | Explanation |
|---|---|
| `sweep_reentry` | Price swept beyond a key level, then reversed |
| `trend_rebuild` | Trend structure reforming after a pullback |
| `retest` | Price returning to a previously broken level |
| `stop` | Stop loss triggered — acceptable loss |
| `target` | Profit target reached |
| `scan` | Bot scanning for setups |
| `entry` | Bot entered a position |

---

## 8. Services Layer

### 8a. `AuthService`
- `create_user(email, password, display_name)` — validates uniqueness, hashes password, creates user
- `authenticate(email, password)` — returns User or None

### 8b. `CurriculumService`
- `get_published_modules(user_id)` — modules with per-user progress
- `get_module_by_slug(slug, user_id)` — module detail with lesson progress
- `get_lesson(module_slug, lesson_slug, user_id)` — lesson with prev/next navigation
- `mark_complete(user_id, lesson_id)` — upserts UserProgress
- `get_progress(user_id)` — aggregate stats
- `get_module_progress(user_id, module_id)` — per-module stats

### 8c. `SignalExplainerService`
- `get_explanation(event)` → `{short, long}` text
- `get_recent_signals(limit=20)` → list of annotated events

### 8d. `AiService` (Groq)
- `ask(user, message)` → calls Groq API, writes AiInteraction record, returns response
- `get_usage_today(user)` → query count since midnight UTC
- Rate limits: free = 20/day, pro = unlimited (`-1`)
- System prompt: "You are Delta, an expert trading educator... Never give trading advice."
- Model: `llama3-70b-8192`, max_tokens=350, temperature=0.7
- Graceful fallback on API failure

---

## 9. Curriculum Content

5 modules, 22 lessons, ~76 minutes total.

| Module | Lessons | Est. Time |
|---|---|---|
| 0 — What is the Market? | 0.1-0.5 (5 lessons) | 17 min |
| 1 — Reading the Market | 1.1-1.4 (4 lessons) | 13 min |
| 2 — How Big Money Moves | 2.1-2.5 (5 lessons) | 17 min |
| 3 — The Sweep Strategy | 3.1-3.4 (4 lessons) | 15 min |
| 4 — Understanding the Signals | 4.1-4.4 (4 lessons) | 15 min |

---

## 10. Design Backlog (Aspirational / Not Implemented)

The following detailed lesson UX designs exist in `docs/` but are **not yet implemented** in code:

### Interactive Lesson Types (from `lesson-plans-module-0.txt`)

| Type | Description | Used In |
|---|---|---|
| `reveal` | Animated candlestick chart with progressive narration cards | 0.1, 0.2, 0.4 |
| `simulation` | Step-by-step animated flow diagram (order routing simulation) | 0.3 |
| `classify` | Scenario-based classification game (bullish vs bearish) | 0.5 |

Each lesson plan defines:
- Learning objective
- Hook text (opening line on entry)
- Interaction type + `interaction_data` (chart data, narration, events)
- Key takeaway (shown after interaction completes)
- Reflect questions (2 per lesson, sequential gating with acceptable answers)
- Notes content (populated in right panel)

### Lesson UX Mockup (from `Lesson-Draft.txt`)
- 3-panel layout: lesson content (center), notes (right), chart (top)
- Candlestick chart with narrated reveal
- Reflection question inputs with submit
- Mark Complete button

---

## 11. Future Architecture Hooks

The following paths are reserved in the architecture but not built:

| Path | Purpose | Phase |
|---|---|---|
| `app/routes/webhooks.py` | Stripe webhook listener | P7 |
| `app/models/subscription.py` | Subscription tracking (Stripe customer/sub IDs) | P7 |
| `app/models/user_preference.py` | Theme, notification prefs | P10 |
| `app/models/concept_tag.py` | Tag taxonomy | Future |
| `app/models/quiz.py` | Quiz/question models | Future |
| `app/models/note.py` | Per-lesson user notes | P9 |
| `tests/` | Test suite (pytest) | P8 |

**Design implications already in place:**
- User model has `tier` and `onboarding_complete` → ready for gating
- AiInteraction model has `tier` column → ready for Pro/Free AI gating
- Blueprint registration has commented webhooks import → ready
- `base.html` has blocks for head extensions → ready
- `AiService` is designed to be provider-swappable (Groq → other)

---

## 12. Configuration & Deployment

### Environment (`.env`)
```
SECRET_KEY=<generate-random>
DATABASE_URL=postgresql://localhost/delta_one
ALPACA_API_KEY=<key>
ALPACA_SECRET_KEY=<secret>
GROQ_API_KEY=<key>
GROQ_MODEL=llama3-70b-8192
AI_DAILY_LIMIT_FREE=20
AI_DAILY_LIMIT_PRO=-1
FLASK_APP=app
FLASK_ENV=development
```

### Dependencies (`requirements.txt`)
`alpaca-py`, `flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Login`, `Flask-WTF`, `pandas`, `numpy`, `yfinance`, `python-dateutil`, `python-dotenv`, `psycopg2-binary`, `WTForms`, `email-validator`, `groq`

### Running
```bash
# Web app
export FLASK_APP=app && export FLASK_ENV=development && flask run

# Bot (separate process)
python sweep_main.py

# Database
flask db upgrade
python seeds/curriculum_seed.py
```

---

## 13. Build Status Summary

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation | Complete |
| 1 | Auth + Landing | Complete |
| 2 | Dashboard + API Migration | Complete |
| 3 | Curriculum Framework | Complete |
| 4 | Signal Explorer | Complete |
| 5a-5d | Workspace Iterations | Complete (5d = current) |
| 6 | AI Assistant + Admin Panel | Complete |
| **7** | **Monetization** | **Not started** |
| **8** | **Launch Polish** | **Not started** |
| 9-13 | Post-Launch Features | Not started |
