# Delta One — Roadmap

> Current build status · What's accomplished · What's remaining  
> Updated: June 2026

---

## Quick Status

```
████████████████████████░░░░░░░░░░  60%  (Phases 0-6 complete)
███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10%  (Phase 7 — in design)
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%  (Phase 8 — not started)
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%  (Post-launch — not started)
```

| Milestone | Status | Target |
|---|---|---|
| Foundation (P0) | ✅ Complete | Done |
| Auth + Landing (P1) | ✅ Complete | Done |
| Dashboard + API (P2) | ✅ Complete | Done |
| Curriculum (P3) | ✅ Complete | Done |
| Signal Explorer (P4) | ✅ Complete | Done |
| Workspace UX (P5a-d) | ✅ Complete | Done |
| AI + Admin (P6) | ✅ Complete | Done |
| **Monetization (P7)** | ❌ Not started | TBD |
| **Launch Polish (P8)** | ❌ Not started | TBD |
| Post-Launch (P9-P13) | ❌ Not started | After launch |

---

## What's Accomplished (Phases 0-6)

### Phase 0 — Foundation

**Goal:** Project structure exists, database is running, app boots.

- [x] PostgreSQL database `delta_one` created locally
- [x] Flask app factory (`create_app()`) with extension initialization
- [x] 8 SQLAlchemy models: User, Session, Module, Lesson, UserProgress, BotEvent, WaitlistEntry, AiInteraction
- [x] Alembic migrations (2 versions: initial + ai_interactions)
- [x] 5 blueprint registration system (public, auth, api, workspace, admin)
- [x] Base template with error pages (404, 500)
- [x] `sweep_csv.py` dual-writes bot events to CSV + PostgreSQL

### Phase 1 — Auth + Landing

**Goal:** Users can sign up, log in, and see a living landing page.

- [x] AuthService (create_user, authenticate) with password hashing
- [x] Flask-WTF forms: LoginForm, SignupForm
- [x] Rate limited login/signup routes
- [x] Landing page migrated from static HTML → Flask template
- [x] Pricing page (Core free / Pro $20/mo)
- [x] Dark/light mode toggle on landing
- [x] Waitlist signup form on landing page

### Phase 2 — Dashboard + API Migration

**Goal:** Bot monitoring data comes from PostgreSQL instead of CSV.

- [x] 4 API endpoints ported: `/api/summary`, `/api/activity`, `/api/symbol/<s>`, `/api/footer`
- [x] Old `dashboard_app.py` and its template deleted

### Phase 3 — Curriculum Framework

**Goal:** Lesson viewer works. Users can browse modules and mark lessons done.

- [x] Seed script creates 5 modules, 22 lessons (~76 min)
- [x] CurriculumService with module/lesson queries and progress tracking
- [x] Inline lesson viewing in workspace (via internal API)
- [x] Mark-complete with progress tracking per user
- [x] Concept tree in workspace: 5 collapsible groups, 16 nodes

### Phase 4 — Signal Explorer

**Goal:** Bot signals displayed as educational case studies.

- [x] SignalExplainerService with 7 event type explanations
- [x] Live signal feed endpoint (`/api/signals/live`)
- [x] Signals linked to related lessons via `concept_tags`
- [x] 15-second auto-poll in workspace right column

### Phase 5 — Workspace (3 iterations → current)

**Goal:** Single unified terminal-themed interface for all authenticated features.

- [x] **5a:** vis-network concept map terminal (superseded — `/api/concepts` survived)
- [x] **5b:** 5-pane draggable OS shell (superseded)
- [x] **5c:** Workspace promoted to primary UX, legacy routes redirect with `?focus=`
- [x] **5d:** 3-column fixed CSS grid terminal multiplexer (current)
- [x] All legacy route files and templates deleted

### Phase 6 — AI Assistant + Admin Panel

**Goal:** Real LLM replaces keyword copilot. Admin panel for monitoring.

- [x] AiService with Groq API (llama3-70b-8192)
- [x] Rate limiting: free=20/day, pro=unlimited
- [x] AI interactions logged to database for audit
- [x] Graceful fallback on API failure
- [x] Admin panel: Usage, Users, System, Bot Health tools
- [x] Bot Health shows live equity, positions, event feed, log tail
- [x] Old `dashboard_app.py` fully replaced

### Security Hardening (cross-cutting)

- [x] All API endpoints require logged-in user
- [x] Production mode refuses to start without SECRET_KEY env var
- [x] Email normalization (lowercased on signup/login)
- [x] UUID validation on admin user routes
- [x] Login redirect validation (prevents open redirect attacks)
- [x] Login timestamps recorded
- [x] UTC standardization internally
- [x] Market helpers centralized in `app/utils/market.py`
- [x] AI service failures logged with full error details

---

## What's Remaining

### Phase 7 — Monetization (NOT STARTED)

**Goal:** Stripe payments work. Pro tier gates premium features.

| Step | Description | Dependencies | Est. Effort |
|---|---|---|---|
| 7.1 | Subscription model + Stripe integration | P3+ (features to gate) | 3-4 days |

**Sub-tasks:**
- [ ] Create `app/models/subscription.py` (Stripe customer/subscription IDs)
- [ ] Create `app/services/tier_service.py` (`user_has_access`, `upgrade`)
- [ ] Create `app/routes/webhooks.py` (Stripe webhook endpoint)
- [ ] Wire pricing page "Subscribe" buttons to Stripe Checkout
- [ ] Add `stripe` to `requirements.txt`
- [ ] Register webhooks blueprint
- [ ] Implement `@tier_required('pro')` route decorator
- [ ] Add template-level gating (`{% if current_user.is_pro %}`)

**Features to gate (decide which):**
- [ ] AI Assistant access (beyond free daily limit)
- [ ] Advanced signal explanations
- [ ] Extended signal history
- [ ] Custom concept maps
- [ ] Notes export

### Phase 8 — Launch Polish (NOT STARTED)

**Goal:** Onboarding flow, automated tests, production readiness.

| Step | Description | Dependencies | Est. Effort |
|---|---|---|---|
| 8.1 | Onboarding flow for new users | P1 (auth), P3 (lessons), P4 (signals), P5 (workspace) | 2-3 days |
| 8.2 | Automated test suite | All phases | 2-3 days |
| 8.3 | Uptime & stress testing | P8.2 | 1-2 days |

**8.1 — Onboarding Flow:**
- [ ] Create `app/services/onboarding_service.py`
- [ ] 5-step guided tour: welcome → tour terminal → complete first lesson → see live signal → done
- [ ] Use existing `user.onboarding_complete` boolean
- [ ] Wire post-signup redirect to onboarding

**8.2 — Automated Tests:**
- [ ] Create `tests/conftest.py` with fixtures (app, client, db)
- [ ] `test_auth.py` — signup, login, logout, rate limiting
- [ ] `test_models.py` — model validation, constraints, relationships
- [ ] `test_routes.py` — status codes, redirects, auth gating
- [ ] `test_strategy.py` — backtest regression tests
- [ ] `test_services.py` — CurriculumService, AiService, SignalExplainerService
- [ ] Add `pytest`, `pytest-flask` to requirements
- [ ] TestingConfig (SQLite in-memory) already exists in `app/config.py`

**8.3 — Production Deployment:**
- [ ] Gunicorn/WSGI server (not Flask dev server)
- [ ] Production environment variables (no `.env` fallback in prod)
- [ ] PostgreSQL connection pooling (SQLAlchemy pool settings)
- [ ] Static file caching headers
- [ ] Session configuration for production
- [ ] 24-hour stress test (bot + web app running together)

---

## Post-Launch Backlog (Phases 9-13)

These are documented to keep the architecture compatible. Not scheduled.

### Phase 9 — Notes System
- [ ] `app/models/note.py` (reserved)
- [ ] Per-lesson notes with markdown support
- [ ] Server-side CRUD (currently localStorage only)
- [ ] Notes export feature
- [ ] Public note sharing (community)

### Phase 10 — Theme Customization
- [ ] `app/models/user_preference.py` (reserved)
- [ ] Multiple VS Code-like themes (Monokai, Solarized, etc.)
- [ ] User-selectable in workspace settings

### Phase 11 — Max Tier
- [ ] Broader market coverage
- [ ] Intraday signals
- [ ] Extended signal history

### Phase 12 — Community Features
- [ ] Lesson comments/discussion
- [ ] Concept map sharing
- [ ] Public profiles

### Phase 13 — Mobile App
- [ ] REST API already exists
- [ ] Mobile-specific endpoints as needed
- [ ] Potential native app

---

## Design Backlog (Aspirational)

The following detailed lesson UX designs exist in `docs/` but are **not implemented** in code:

| Document | Content | Priority |
|---|---|---|
| `lesson-plans-module-0.txt` | 5 detailed lesson plans with interactive types (reveal, simulation, classify), narration, reflection questions | Medium — would enhance curriculum |
| `Lesson-Draft.txt` | Lesson viewer mockup with candlestick chart, narrated reveal, reflection inputs | Medium — aspirational UX |

These can be referenced when enhancing the curriculum viewer. The current implementation renders lessons as HTML content with mark-complete functionality, without the interactive chart simulations or reflection question gating described in these docs.

---

## Dependency Graph

```
P0  Foundation
│
├──► P1  Auth + Landing
│     │
│     ├──► P2  Dashboard Migration
│     │
│     └──► P3  Curriculum Framework
│            │
│            ├──► P4  Signal Explorer
│            │
│            └──► P5a-d  Workspace (current: 3-column multiplexer)
│                  │
│                  └──► P6  AI Assistant + Admin Panel
│
├──► P7  Monetization (depends on P3+ for gatable features)
│
└──► P8  Launch Polish (depends on everything above)
       │
       └──► P9-P13  Post-Launch
```

**Key insight:** P7 and P8 are independent of each other and could be worked on in parallel, though P8's onboarding depends on features from P3/P4/P5.

---

## Risk & Cut Decisions

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Stripe integration complexity | Medium | Delays launch | Can defer P7 until post-launch; Core tier is already functional |
| No tests in production | High | Regression bugs | Write smoke tests before any P7/P8 work begins |
| Groq API free tier limits | Medium | User frustration | Rate limits already enforced; Pro tier unlocks more |
| Bot strategy not validated | Low | Trust issue | Paper trading on Alpaca; users see educational value regardless |
| Production deployment unknowns | Medium | Launch delay | Deploy on basic VPS first; optimize after launch |

**Safest items to cut if behind schedule:**
1. Phase 7 (Monetization) — Core is free indefinitely
2. Interactive lesson designs — current HTML lessons work
3. Theme customization — cosmetic only
4. Notes system — localStorage works for now
