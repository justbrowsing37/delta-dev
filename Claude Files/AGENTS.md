# Delta One — AI Handoff Guide

This file is the canonical repo handoff for any future AI assistant continuing development on Delta One.

## 1. Project summary

Delta One is a curriculum-first market education product.

The current product promise is:
- teach beginners how markets work,
- deliver structured lessons and activities,
- track learner progress,
- and provide a clean learning workspace.

The product is not currently positioned as a public trading bot, signal platform, or AI-first assistant.

### Current product direction

At launch, the public-facing product is Delta Core:
- structured lessons,
- progressive activities that build on one another,
- progress tracking,
- and a simple learning workspace.

The bot and AI remain secondary infrastructure. They should not drive product priorities.

### Launch target

- Target launch: January 1, 2027.
- Priority is curriculum quality and lesson delivery, not bot sophistication.

---

## 2. Repository purpose and priorities

If you are continuing this project, the highest-value work is usually one of these:

1. Curriculum content work
   - write or refine lessons and activities
   - maintain tone and structure consistency
   - keep examples beginner-friendly

2. Lesson delivery system work
   - improve module/lesson navigation
   - fix progress tracking issues
   - make the workspace experience cleaner

3. Contributor experience
   - improve onboarding docs
   - reduce confusion around content structure and app flow

4. App stability and setup
   - make local development easier
   - resolve environment/setup issues
   - keep the app deployable

### What not to prioritize first

Do not make the bot or AI the center of the product. Do not design around live signal intelligence as the core experience.

---

## 3. Core stack

- Backend: Flask
- Database: PostgreSQL (Supabase-style hosting expectation)
- ORM: SQLAlchemy / Flask-SQLAlchemy
- Auth: Flask-Login
- Forms: Flask-WTF / WTForms
- Templates: Jinja2
- Frontend: Vanilla JS + CSS
- Migrations: Flask-Migrate / Alembic
- Hosting: Cloudflare Pages for static waitlist site, Render for app/staging
- AI: optional Groq integration for assistant features

### Main runtime entry point

- Application factory: app/__init__.py
- Entry command used by Procfile: gunicorn "app:create_app()"

---

## 4. Repository structure

```text
app/                 # Flask app package
  __init__.py        # app factory and CLI commands
  config.py         # environment-driven config
  extensions.py     # db / migrate / login / csrf setup
  forms/            # WTForms forms
  models/           # SQLAlchemy models
  routes/           # Flask blueprints
  services/         # business logic and integrations
  templates/        # Jinja templates
content/            # curriculum markdown content files
docs/               # canonical product and technical docs
migrations/         # Alembic migrations
seeds/              # seed scripts for database content
static/             # frontend CSS/JS assets
tests/              # regression and smoke tests
```

### Important note

The repo contains both:
- product documentation for a curriculum-first product, and
- older bot/signal infrastructure files.

The docs in docs/ should be treated as the source of truth for current product direction.

---

## 5. App architecture

### Flask app factory

The app is created through the factory function in app/__init__.py.

That factory:
- creates the Flask app,
- loads config,
- initializes SQLAlchemy, migrations, login, and CSRF,
- registers blueprints,
- registers CLI commands,
- and sets up error handlers.

### Blueprint structure

Key blueprints:
- public: landing page, pricing page, waitlist signup
- auth: login, signup, logout
- workspace: authenticated lesson/workspace shell and curriculum APIs
- api: AI endpoint and concept graph API
- admin: admin dashboard and usage/curriculum stats

### Main app flow

1. User lands on public pages.
2. User signs up / logs in.
3. Authenticated users enter workspace.
4. Curriculum service loads modules and lessons from the database.
5. User can mark lessons complete.
6. Progress is stored in user_progress.

---

## 6. Data model overview

The core database models live in app/models/.

### User

- app/models/user.py
- Stores auth fields, tier, onboarding state, skill level, and profile info.

### Module

- app/models/module.py
- Represents a top-level curriculum section such as “What is the Market?”

### Lesson

- app/models/lesson.py
- Represents a lesson or activity item inside a module.
- Important fields include:
  - title
  - slug
  - content
  - content_type
  - item_type (lesson vs activity)
  - connects_to
  - sort_order
  - estimated_minutes
  - is_published
  - concept_tags

### UserProgress

- app/models/progress.py
- Tracks completion state for each learner and lesson.

### WaitlistEntry

- app/models/waitlist_entry.py
- Stores waitlist signups from the landing page.

### AiInteraction

- app/models/ai_interaction.py
- Stores AI assistant interactions and usage metadata.

### Important modeling note

The curriculum system is modeled as database-backed content, not as direct markdown file loading. The current code uses SQLAlchemy models and services.

---

## 7. Key services

### CurriculumService

- app/services/curriculum.py
- The main service for loading modules, lessons, completion state, and progress.
- Important methods:
  - get_published_modules(user_id=None)
  - get_module_by_slug(slug, user_id=None)
  - get_lesson(module_slug, lesson_slug, user_id=None)
  - mark_complete(user_id, lesson_id)
  - get_progress(user_id, module_id=None)

### AuthService

- app/services/auth_service.py
- Handles user creation and login authentication.

### AiService

- app/services/ai_service.py
- Optional AI assistant integration via Groq.
- It uses daily rate limits based on tier.
- If no API key is configured, it returns a fallback response.

---

## 8. Main routes and endpoints

### Public routes

- / : landing page
- /pricing : pricing page
- /waitlist : waitlist signup POST endpoint

### Auth routes

- /auth/login
- /auth/signup
- /auth/logout

### Workspace routes

- /workspace/ : workspace shell
- /workspace/api/modules
- /workspace/api/modules/<slug>
- /workspace/api/lessons/<module_slug>/<lesson_slug>
- /workspace/api/lessons/<module_slug>/<lesson_slug>/complete (POST)

### API routes

- /api/ai/ask (POST)
- /api/concepts
- /api/concepts/<node_id>

### Admin routes

- /admin/
- /admin/api/usage
- /admin/api/users
- /admin/api/users/<user_id>
- /admin/api/users/<user_id>/tier (POST)
- /admin/api/system
- /admin/api/curriculum

---

## 9. Curriculum and content system

### Canonical docs

The repo’s documentation is the main source of truth for product direction:

- docs/product-vision.md
- docs/roadmap.md
- docs/technical-spec.md
- docs/curriculum.txt
- docs/contributor-guide.md

### Content format expectations

The curriculum is intended to follow a lesson → activity → lesson → activity pattern.

The content authoring rules in docs/contributor-guide.md should be followed for any new curriculum work.

### File naming conventions

- Lessons: X.Y-short-title.md
- Activities: X.YA-short-title.md
- Checks: X-check.md

### Content location

- Curriculum content files live under content/
- The app currently uses database-backed lesson records rather than directly serving those markdown files from disk.

### Important mismatch to be aware of

There is a meaningful mismatch between documentation and implementation:
- docs and content/ suggest a markdown-first curriculum system,
- but the current Flask app uses SQLAlchemy models and seed scripts to populate lesson content into the database.

If you want to make the app fully content-file-driven, that will likely require new work around content ingestion or a migration strategy.

---

## 10. Local development setup

### Prerequisites

- Python 3.11+ (project targets modern Flask)
- PostgreSQL running locally or a reachable database URL
- Environment variables configured in a .env file

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

Create a .env file at the repo root with at least:

```env
SECRET_KEY=change-this-in-development
DATABASE_URL=postgresql://localhost/delta_one
GROQ_API_KEY=
```

Optional AI settings:

```env
GROQ_MODEL=llama3-70b-8192
AI_DAILY_LIMIT_FREE=50
AI_DAILY_LIMIT_PRO=-1
```

### Run the app

```bash
gunicorn "app:create_app()" --bind 0.0.0.0:8000
```

Or use the Procfile-style command in development if desired.

### Run tests

```bash
pytest
```

### Seed the database

The repo has seed scripts in seeds/.

Example:

```bash
python -m seeds.curriculum_seed
```

The seed script expects a running PostgreSQL instance and the DATABASE_URL env var to be configured.

### Flask CLI commands

The app factory defines a CLI command:

```bash
flask --app app seed-users
```

That command creates demo users for admin/core/pro tiers.

---

## 11. Current implementation status

### What appears to work

- Flask app factory and blueprint registration
- auth and login/signup flows
- workspace shell and curriculum API endpoints
- basic progress completion tracking
- admin dashboard APIs
- AI endpoint with fallback behavior and rate limits
- smoke tests for app factory, routes, and basic model behavior

### What is likely incomplete or aspirational

- the curriculum is not fully implemented as markdown-driven content
- some content/docs suggest a richer learning path than the current app exposes
- bot/signal infrastructure exists but is not the primary product focus
- AI features are present but optional and not core to launch

---

## 12. Important implementation caveats

### 1. Product direction matters

Treat the curriculum as the product. Do not turn the app into a bot dashboard or trading signal platform.

### 2. Docs are more authoritative than code comments

The docs in docs/ describe the intended product direction more clearly than many of the older bot-related files.

### 3. AI is optional

The AI service exists, but it should remain a support feature rather than a launch-critical one.

### 4. The content system is partially disconnected

The content files in content/ are not obviously wired into the Flask runtime in the current implementation. If you need content-driven delivery, expect to build that path intentionally.

### 5. The app is still evolving

The repo appears to be transitioning from a bot-first or signal-first prototype toward a curriculum-first learning platform. Keep that transition in mind whenever you touch routing, templates, or feature scope.

---

## 13. Suggested next tasks for a future agent

If you need to decide where to work next, a good order is:

1. Make the curriculum content delivery experience feel complete
   - module/lesson rendering polish
   - better navigation and state handling
   - progress UI improvements

2. Tighten content ingestion and publishing workflow
   - connect content files to runtime more directly
   - support lesson/activity/check publishing in a contributor-friendly way

3. Improve contributor onboarding
   - make it easier to add new curriculum content without understanding the whole app

4. Refine the app shell and learning UX
   - make workspace transitions smoother
   - improve visual clarity for modules and lessons

5. Keep bot/AI work secondary
   - only add complexity if it clearly strengthens the learning experience

---

## 14. Working rules for future AI assistants

When editing this repo:
- preserve the curriculum-first product direction,
- avoid over-indexing on bot or signal logic,
- keep changes aligned with the docs and current architecture,
- prefer small, targeted changes over broad rewrites,
- and verify behavior with tests or at least app import checks when possible.

If you are unsure whether a change belongs in the app, curriculum layer, or bot layer, default to the docs and the current product direction in docs/product-vision.md and docs/technical-spec.md.
