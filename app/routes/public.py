import logging
from flask import Blueprint, render_template, request, jsonify
from app.extensions import db, csrf
from app.models.waitlist_entry import WaitlistEntry

log = logging.getLogger(__name__)
public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def landing():
    return render_template("public/landing.html")


@public_bp.route("/pricing")
def pricing():
    return render_template("public/pricing.html")


@public_bp.route("/waitlist", methods=["POST"])
@csrf.exempt
def waitlist():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Valid email required."}), 400
    existing = WaitlistEntry.query.filter(WaitlistEntry.email == email).first()
    if existing:
        return jsonify({"ok": True})
    entry = WaitlistEntry(email=email, source="landing")
    db.session.add(entry)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error("Waitlist save failed: %s", e)
        return jsonify({"ok": False, "error": "Could not save. Try again."}), 500
    return jsonify({"ok": True})
