# Technical Spec

## Current product architecture

Delta One is a Flask application. Curriculum content is stored as markdown files in the `content/` directory. The public-facing system should prioritize lesson delivery over trading infrastructure.

## Core stack

| Layer | Choice |
|---|---|
| Backend | Flask |
| Database | PostgreSQL (Supabase-managed) |
| ORM | SQLAlchemy / Flask-SQLAlchemy |
| Auth | Flask-Login |
| Templates | Jinja2 |
| Frontend | Vanilla JS + CSS |
| Hosting (production) | Cloudflare Pages (static/waitlist) |
| Hosting (app/staging) | Render |
| Migrations | Flask-Migrate (Alembic) |

## Content architecture

Curriculum content lives in `content/`.

```text
content/
├── module-0/
├── module-1/
├── module-2/
├── module-3/
└── module-4/
```

Naming pattern:
- Lessons: `X.Y-title.md`
- Activities: `X.YA-title.md`

## Curriculum model

The learning system follows a paired pattern: lesson → activity → lesson → activity, with each activity building on the previous one. The full 42-item structure is in `docs/curriculum.txt`.

## Database schema (core tables)

- `users` — auth, tier, profile
- `modules` — top-level curriculum grouping
- `lessons` — individual content units within modules
- `user_progress` — completion state per user per lesson
- `waitlist_entries` — pre-launch signups

Bot-related tables (`bot_events`) exist but are internal only. They are not surfaced to users at launch.

## Application priorities

The application should optimize for:
- rendering lesson content cleanly,
- moving users through modules,
- storing completion/progress,
- and supporting contributor-friendly content updates.

## Bot status

The private bot code remains in the repository (`sweep_*.py`). It is not the center of the public product architecture at launch. It may continue running privately for research, validation, or future case-study generation. It should not drive documentation or build prioritization.

## AI status

AI is not a current core system requirement. Do not design the product around AI before the lesson system is complete. AI can be added later as a support layer if it improves clarity without increasing launch risk.

## Hosting notes

- Cloudflare Pages handles the static waitlist site (`deltaone-waitlist` repo).
- Render handles the Flask app in development and staging.
- Production app hosting will move to a dedicated server (DigitalOcean or equivalent) before launch.
- Supabase CORS/allowed origins must include the live Cloudflare Pages URL.

## Documentation policy

Canonical docs describe the current product direction only. If a document reflects a superseded bot-first or signal-first direction, it should be replaced or removed, not left in place.
