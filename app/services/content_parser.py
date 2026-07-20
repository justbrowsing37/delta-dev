"""Reads Module 0 markdown files from disk, parses them into structured section dicts.

This service never stores content in the DB — it reads from content/module-0/ at
request time and caches the parse result in-process. All lesson/activity/check
rendering goes through here.
"""
import os
import re
from functools import lru_cache
from typing import Optional

# Canonical sequence of Module 0 items in display order
MODULE_0_SEQUENCE = [
    {"id": "0.1",  "type": "lesson",   "filename": "0.1-what-is-a-stock.md",                     "title": "What is a Stock?"},
    {"id": "0.1A", "type": "activity", "filename": "0.1A-calculate-ownership-percentage.md",     "title": "Calculate Ownership Percentage"},
    {"id": "0.2",  "type": "lesson",   "filename": "0.2-what-does-it-mean-to-own-a-share.md",   "title": "What Does It Mean to Own a Share?"},
    {"id": "0.2A", "type": "activity", "filename": "0.2A-analyse-meta-buyback.md",               "title": "Analyse the Meta Buyback"},
    {"id": "0.3",  "type": "lesson",   "filename": "0.3-how-does-a-stock-exchange-work.md",      "title": "How Does a Stock Exchange Work?"},
    {"id": "0.3A", "type": "activity", "filename": "0.3A-read-nvda-level-2.md",                  "title": "Read NVDA Level 2"},
    {"id": "0.4",  "type": "lesson",   "filename": "0.4-what-moves-a-stock-price.md",            "title": "What Moves a Stock Price?"},
    {"id": "0.4A", "type": "activity", "filename": "0.4A-find-unexplained-price-move.md",        "title": "Find an Unexplained Price Move"},
    {"id": "0.5",  "type": "lesson",   "filename": "0.5-bulls-bears-and-market-sentiment.md",   "title": "Bulls, Bears & Market Sentiment"},
    {"id": "0.C",  "type": "check",    "filename": "0-check.md",                                  "title": "Module 0 Check"},
]

_CONTENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # app/services/
    "..", "..", "content", "module-0"
)


def _content_dir() -> str:
    return os.path.normpath(_CONTENT_DIR)


@lru_cache(maxsize=32)
def _load_file(filename: str) -> str:
    path = os.path.join(_content_dir(), filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_lesson(raw: str) -> dict:
    """Parse a lesson markdown file into labelled sections."""
    sections = {}
    current_key = None
    current_lines = []
    title = ""

    for line in raw.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        else:
            if current_key is not None:
                current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    # Extract inline key concept blockquote
    key_concept = None
    for key, val in sections.items():
        match = re.search(r'^>\s*Key concept:\s*(.+)$', val, re.MULTILINE)
        if match:
            key_concept = match.group(1).strip()
            # Remove blockquote from the section body
            cleaned = re.sub(r'^>\s*Key concept:.*$\n?', '', val, flags=re.MULTILINE).strip()
            sections[key] = cleaned
            break

    return {
        "title": title,
        "type": "lesson",
        "key_concept": key_concept,
        "sections": sections,
    }


def _parse_activity(raw: str) -> dict:
    """Parse an activity markdown file."""
    sections = {}
    current_key = None
    current_lines = []
    title = ""

    for line in raw.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        else:
            if current_key is not None:
                current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return {
        "title": title,
        "type": "activity",
        "sections": sections,
    }


def _parse_check(raw: str) -> dict:
    """Parse the module check markdown file."""
    sections = {}
    current_key = None
    current_lines = []
    title = ""

    for line in raw.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        else:
            if current_key is not None:
                current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return {
        "title": title,
        "type": "check",
        "sections": sections,
    }


def get_item(item_id: str) -> Optional[dict]:
    """Return a fully parsed content item by its ID (e.g. '0.1', '0.2A', '0.C')."""
    meta = next((x for x in MODULE_0_SEQUENCE if x["id"] == item_id), None)
    if not meta:
        return None
    raw = _load_file(meta["filename"])
    if meta["type"] == "lesson":
        parsed = _parse_lesson(raw)
    elif meta["type"] == "activity":
        parsed = _parse_activity(raw)
    else:
        parsed = _parse_check(raw)
    parsed["id"] = item_id
    parsed["type"] = meta["type"]
    return parsed


def get_sequence() -> list:
    """Return the full sequence metadata list (no file I/O)."""
    return MODULE_0_SEQUENCE


def get_nav(item_id: str) -> dict:
    """Return prev/next item metadata for a given item_id."""
    seq = MODULE_0_SEQUENCE
    idx = next((i for i, x in enumerate(seq) if x["id"] == item_id), None)
    prev_item = seq[idx - 1] if idx and idx > 0 else None
    next_item = seq[idx + 1] if idx is not None and idx < len(seq) - 1 else None
    return {
        "position": (idx + 1) if idx is not None else None,
        "total": len(seq),
        "prev": prev_item,
        "next": next_item,
    }
