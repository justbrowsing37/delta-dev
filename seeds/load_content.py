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


# ─────────────────────────────────────────────────────────────────────
# Lesson blocks — a small shortcode syntax so a lesson can mix plain
# prose with interactive elements (an animated stat, a tap-to-reveal
# question, an inline check, a calculator) without leaving markdown.
# Expanded to raw HTML *before* the markdown pass, since python-markdown
# passes block-level raw HTML through untouched — workspace.js then
# hydrates each `data-block` element into a live widget on render.
#
# Syntax:
#   [[stat from="150" to="1000" prefix="$" label="NVDA share price"]]
#
#   [[reveal prompt="What do you think happens next?"]]
#   Markdown answer text goes here.
#   [[/reveal]]
#
#   [[quiz]]
#   Q: What actually moves a stock's price?
#   - Its ticker symbol length
#   - What investors believe about its future *(correct)*
#   - The company's logo
#   [[/quiz]]
#
#   [[calc type="ownership" symbol="NVDA" price="135" shares_outstanding="24500000000"]]
# ─────────────────────────────────────────────────────────────────────

ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
BLOCK_PAIR_RE = re.compile(r'\[\[(reveal|quiz)([^\]]*)\]\](.*?)\[\[/\1\]\]', re.DOTALL)
BLOCK_SELF_RE = re.compile(r'\[\[(stat|calc)([^\]]*)\]\]')


def parse_attrs(attr_str):
    return dict(ATTR_RE.findall(attr_str or ""))


def render_fragment(text):
    """Render a small chunk of markdown (used inside block bodies)."""
    return md.markdown(text.strip(), extensions=["extra", "sane_lists"])


def build_stat_block(attrs):
    frm = attrs.get("from", "0")
    to = attrs.get("to", "0")
    prefix = attrs.get("prefix", "")
    suffix = attrs.get("suffix", "")
    label = attrs.get("label", "")
    return (
        '<div class="ws-block ws-stat-block" data-block="stat" '
        f'data-from="{frm}" data-to="{to}" data-prefix="{prefix}" data-suffix="{suffix}">'
        f'<div class="ws-stat-value" aria-hidden="true">{prefix}{frm}{suffix}</div>'
        f'<div class="ws-stat-label">{label}</div>'
        '</div>'
    )


def build_calc_block(attrs):
    calc_type = attrs.get("type", "ownership")
    symbol = attrs.get("symbol", "")
    price = attrs.get("price", "0")
    shares_out = attrs.get("shares_outstanding", "0")
    return (
        '<div class="ws-block ws-calc-block" data-block="calc" '
        f'data-type="{calc_type}" data-symbol="{symbol}" data-price="{price}" '
        f'data-shares-outstanding="{shares_out}"></div>'
    )


def build_reveal_block(attrs, inner_md):
    prompt = attrs.get("prompt", "What do you think?")
    answer_html = render_fragment(inner_md)
    return (
        '<div class="ws-block ws-reveal-block" data-block="reveal">'
        f'<button type="button" class="ws-reveal-prompt">{prompt}</button>'
        f'<div class="ws-reveal-answer">{answer_html}</div>'
        '</div>'
    )


def build_quiz_block(inner_text):
    lines = [ln.rstrip() for ln in inner_text.strip("\n").splitlines() if ln.strip()]
    question = ""
    options = []
    for ln in lines:
        s = ln.strip()
        if s.lower().startswith("q:"):
            question = s[2:].strip()
        elif s.startswith("-"):
            opt = s[1:].strip()
            correct = "(correct)" in opt
            opt = opt.replace("*(correct)*", "").replace("(correct)", "").strip()
            options.append((opt, correct))

    opts_html = ""
    for opt, correct in options:
        opts_html += (
            '<button type="button" class="ws-quiz-option" '
            f'data-correct="{"true" if correct else "false"}">{opt}</button>'
        )

    return (
        '<div class="ws-block ws-quiz-block" data-block="quiz">'
        f'<div class="ws-quiz-question">{question}</div>'
        f'<div class="ws-quiz-options">{opts_html}</div>'
        '<div class="ws-quiz-feedback" hidden></div>'
        '</div>'
    )


def expand_blocks(text):
    def replace_pair(m):
        kind, attr_str, inner = m.group(1), m.group(2), m.group(3)
        attrs = parse_attrs(attr_str)
        if kind == "reveal":
            return "\n\n" + build_reveal_block(attrs, inner) + "\n\n"
        if kind == "quiz":
            return "\n\n" + build_quiz_block(inner) + "\n\n"
        return ""

    def replace_self(m):
        kind, attr_str = m.group(1), m.group(2)
        attrs = parse_attrs(attr_str)
        if kind == "stat":
            return "\n\n" + build_stat_block(attrs) + "\n\n"
        if kind == "calc":
            return "\n\n" + build_calc_block(attrs) + "\n\n"
        return ""

    text = BLOCK_PAIR_RE.sub(replace_pair, text)
    text = BLOCK_SELF_RE.sub(replace_self, text)
    return text


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
            content=to_html(expand_blocks(body)),
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
