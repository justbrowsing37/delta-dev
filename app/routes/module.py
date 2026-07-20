"""Module 0 routes: index, item viewer, mark-complete, feedback.

Gating: a user cannot access item N+1 until item N is marked complete.
Progress is stored in the Feedback table (understood col) + UserProgress
tied to synthetic lesson records loaded from content/.

Since we read content from files (not DB lessons), progress is tracked
via the Feedback table keyed on content_id strings like '0.1', '0.2A'.
"""
import logging
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.feedback import Feedback
from app.services.content_parser import get_item, get_sequence, get_nav

log = logging.getLogger(__name__)
module_bp = Blueprint("module", __name__, url_prefix="/module")


# ------------------------------------------------------------------ helpers

def _completed_ids(user_id) -> set:
    """Return set of content_ids the user has submitted feedback for."""
    rows = Feedback.query.filter_by(user_id=user_id).all()
    return {r.content_id for r in rows}


def _is_unlocked(item_id: str, completed: set) -> bool:
    """An item is unlocked if all items before it are completed."""
    seq = get_sequence()
    for meta in seq:
        if meta["id"] == item_id:
            return True  # reached item before finding an incomplete predecessor
        if meta["id"] not in completed:
            return False
    return False


def _resume_item(completed: set) -> str:
    """Return the item_id the user should resume at."""
    for meta in get_sequence():
        if meta["id"] not in completed:
            return meta["id"]
    return get_sequence()[-1]["id"]  # all done — land on check


# ------------------------------------------------------------------ views

@module_bp.route("/")
@login_required
def index():
    completed = _completed_ids(current_user.id)
    seq = get_sequence()
    items = []
    for meta in seq:
        items.append({
            **meta,
            "is_completed": meta["id"] in completed,
            "is_unlocked": _is_unlocked(meta["id"], completed),
        })
    resume_id = _resume_item(completed)
    return render_template(
        "module/index.html",
        items=items,
        completed_count=len(completed),
        total=len(seq),
        resume_id=resume_id,
    )


@module_bp.route("/<item_id>")
@login_required
def item(item_id):
    completed = _completed_ids(current_user.id)
    if not _is_unlocked(item_id, completed):
        # redirect to the first locked item the user should actually be on
        return redirect(url_for("module.item", item_id=_resume_item(completed)))

    content = get_item(item_id)
    if not content:
        abort(404)

    nav = get_nav(item_id)
    already_completed = item_id in completed

    # Existing feedback for pre-fill
    existing_feedback = Feedback.query.filter_by(
        user_id=current_user.id, content_id=item_id
    ).first()

    if content["type"] == "check":
        return render_template(
            "module/check.html",
            content=content,
            nav=nav,
            already_completed=already_completed,
            existing_feedback=existing_feedback,
        )

    return render_template(
        "module/lesson.html",
        content=content,
        nav=nav,
        already_completed=already_completed,
        existing_feedback=existing_feedback,
    )


# ------------------------------------------------------------------ API: submit feedback + mark complete

@module_bp.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    data = request.get_json(force=True)
    content_id    = (data.get("content_id") or "").strip()
    understood    = data.get("understood")
    comment       = (data.get("comment") or "").strip() or None
    want_module_1 = data.get("want_module_1")  # only present on check

    if not content_id or understood is None:
        return jsonify({"ok": False, "error": "content_id and understood are required"}), 400

    # Validate the item exists and is unlocked
    seq_ids = {x["id"] for x in get_sequence()}
    if content_id not in seq_ids:
        return jsonify({"ok": False, "error": "Unknown content_id"}), 400

    completed = _completed_ids(current_user.id)
    if not _is_unlocked(content_id, completed):
        return jsonify({"ok": False, "error": "Item not yet unlocked"}), 403

    # Upsert feedback
    existing = Feedback.query.filter_by(
        user_id=current_user.id, content_id=content_id
    ).first()

    if existing:
        existing.understood    = bool(understood)
        existing.comment       = comment
        if want_module_1 is not None:
            existing.want_module_1 = bool(want_module_1)
    else:
        fb = Feedback(
            user_id=current_user.id,
            content_id=content_id,
            understood=bool(understood),
            comment=comment,
            want_module_1=bool(want_module_1) if want_module_1 is not None else None,
        )
        db.session.add(fb)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error("Feedback save failed: %s", e)
        return jsonify({"ok": False, "error": "Could not save feedback"}), 500

    # Determine next item
    nav = get_nav(content_id)
    next_item = nav.get("next")
    next_url = url_for("module.item", item_id=next_item["id"]) if next_item else None

    return jsonify({"ok": True, "next_url": next_url})
