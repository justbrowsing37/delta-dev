"""
Load curriculum content from markdown into the database.

Authoring happens in markdown under content/module-N/, and the app serves
lessons from the database. This loader is the bridge: it reads the markdown,
converts it to HTML, and syncs it into the DB the app reads from. Re-running
replaces each module's lessons, so it's safe to run repeatedly as content
changes — it's a content *sync* tool, not a migration.

File naming convention (drives ordering + lesson/activity type):
    content/module-0/0.1-what-is-a-stock.md        -> Module 0, lesson 1
    content/module-0/0.1A-calculate-ownership.md   -> activity of lesson 1
The first "# Heading" line becomes the title; everything after is the body.

Local usage (SQLite — no Postgres needed):
    DATABASE_URL="sqlite:///delta_local.db" .venv/bin/python -m seeds.load_content

WARNING: this deletes and recreates a module (and its lessons) by slug, which
in a real database would also drop user progress for that module. It is meant
for local development and pre-launch seeding, not for mutating a live prod DB
with real users — use Alembic migrations + an upsert path for that.
"""

import os
import re
import sys

import markdown as md

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.module import Module  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

CONTENT_ROOT = os.path.join(os.path.dirname(__file__), "..", "content")

# Only module framing lives here — all lesson content lives in the markdown.
# Add a new entry when a module's content is ready to publish.
MODULES = {
    "module-0": {
        "title": "What is the Market?",
        "slug": "what-is-the-market",
        "description": "No assumed knowledge. Start here if you've never traded before.",
        "icon": "bank",
        "sort_order": 0,
    },
}

# e.g. "0.1-what-is-a-stock.md" or "0.1A-calculate-ownership-percentage.md"
FILENAME_RE = re.compile(r"^(\d+)\.(\d+)([A-Za-z]?)-(.+)\.md$")


def parse_filename(fname):
    m = FILENAME_RE.match(fname)
    if not m:
        return None
    return {
        "module_num": int(m.group(1)),
        "lesson_num": int(m.group(2)),
        "suffix": m.group(3),          # "" = lesson, "A"/"B"/... = activity
        "slug": m.group(4),
        "is_activity": bool(m.group(3)),
        "file": fname,
    }


def split_title_body(text):
    """First '# Heading' -> title; the rest -> body markdown."""
    title, body_start = None, 0
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            title = line.strip()[2:].strip()
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip()
    return title, body


def to_html(body):
    return md.markdown(body, extensions=["extra", "sane_lists"])


def load_module(dir_name, meta):
    module_dir = os.path.join(CONTENT_ROOT, dir_name)
    items = []
    for fname in os.listdir(module_dir):
        if not fname.endswith(".md"):
            continue
        info = parse_filename(fname)
        if not info:
            print(f"  skip (name doesn't match X.Y[-A]-slug.md): {fname}")
            continue
        items.append(info)

    # Order: by lesson number, then lesson before its activity(ies).
    items.sort(key=lambda x: (x["lesson_num"], x["is_activity"], x["suffix"]))

    # Map each lesson number to its slug so activities can link back to it.
    lesson_slug_by_num = {
        it["lesson_num"]: it["slug"] for it in items if not it["is_activity"]
    }

    # Replace the module for an idempotent re-sync (dev-only; see module docstring).
    existing = Module.query.filter_by(slug=meta["slug"]).first()
    if existing:
        db.session.delete(existing)
        db.session.flush()

    module = Module(
        title=meta["title"],
        slug=meta["slug"],
        description=meta.get("description"),
        icon=meta.get("icon"),
        sort_order=meta.get("sort_order", 0),
        is_published=True,
    )
    db.session.add(module)
    db.session.flush()

    for order, info in enumerate(items):
        with open(os.path.join(module_dir, info["file"]), encoding="utf-8") as fh:
            title, body = split_title_body(fh.read())
        connects = []
        if info["is_activity"] and info["lesson_num"] in lesson_slug_by_num:
            connects = [lesson_slug_by_num[info["lesson_num"]]]
        db.session.add(Lesson(
            module_id=module.id,
            title=title or info["slug"],
            slug=info["slug"],
            content=to_html(body),
            content_type="html",
            item_type="activity" if info["is_activity"] else "lesson",
            connects_to=connects,
            sort_order=order,
            is_published=True,
        ))
        kind = "activity" if info["is_activity"] else "lesson"
        print(f"  + [{kind:8}] {info['file']}  ->  {title}")

    return len(items)


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        total = 0
        for dir_name, meta in MODULES.items():
            print(f"Loading {dir_name} ({meta['slug']}) ...")
            total += load_module(dir_name, meta)
        db.session.commit()
        print(f"\nDone. Loaded {total} item(s) across {len(MODULES)} module(s).")


if __name__ == "__main__":
    main()
