# Delta One — Build Log

## 2025-07 — Module 0 MVP

### What was built
- `content/module-0/` — all lesson and activity markdown files
- `app/models/feedback.py` — user feedback / completion tracking
- `app/services/content_parser.py` — reads markdown, parses into structured sections
- `app/routes/module.py` — full Module 0 route set with gating logic
- `app/templates/module/` — index, lesson, check templates
- `static/module.css` — lesson experience styles
- `dev/` folder scaffolded for waitlist site migration
- `mvp/` folder scaffolded for build notes and seeds

### DB changes
- New `feedback` table via `app/models/feedback.py`
- Run `flask db migrate -m "add feedback table"` then `flask db upgrade`

### Architecture decision: content-from-files
Module 0 content is parsed from markdown files at request time (lru_cache in-process).
This avoids a DB seeding step for the MVP and lets content be edited by committing `.md` files.
Module 1+ will likely seed content into the DB via the existing `Module`/`Lesson` models.

### Two-planet structure
- `mvp/` = product app planet
- `dev/` = waitlist/marketing site planet
- Both live in this repo. Waitlist repo will be pointed here and decommissioned.
