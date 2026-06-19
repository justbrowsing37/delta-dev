import re
import uuid as uuid_lib
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.bot_event import BotEvent
from app.models.ai_interaction import AiInteraction
from app.models.waitlist_entry import WaitlistEntry
from app.utils.market import TIMEZONE, SYMBOLS, now_et, market_open_state, compute_health

log = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


def _admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "sweep_bot.log"


def _parse_equity_from_log():
    if not LOG_PATH.exists():
        return None
    try:
        lines = LOG_PATH.read_text().splitlines()
        for line in reversed(lines):
            m = re.search(r"Equity:\s*\$([0-9,]+\.?\d*)", line)
            if m:
                return float(m.group(1).replace(",", ""))
    except Exception as e:
        log.warning("Failed to parse equity from log: %s", e)
    return None


def _read_log_tail(n=50):
    if not LOG_PATH.exists():
        return []
    try:
        lines = LOG_PATH.read_text().splitlines()
        return lines[-n:]
    except Exception as e:
        log.warning("Failed to read log tail: %s", e)
        return []


@admin_bp.route("/")
@login_required
@_admin_required
def shell():
    return render_template("admin/shell.html")


@admin_bp.route("/api/usage")
@login_required
@_admin_required
def api_usage():
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    ai_today = AiInteraction.query.filter(AiInteraction.created_at >= today_start)
    total_queries = ai_today.count()
    total_tokens = ai_today.with_entities(func.sum(AiInteraction.tokens_used)).scalar() or 0

    top_users = (
        db.session.query(
            User.email,
            User.tier,
            func.count(AiInteraction.id).label("queries"),
            func.coalesce(func.sum(AiInteraction.tokens_used), 0).label("tokens"),
        )
        .outerjoin(
            AiInteraction,
            db.and_(
                AiInteraction.user_id == User.id,
                AiInteraction.created_at >= today_start,
            ),
        )
        .group_by(User.id, User.email, User.tier)
        .order_by(func.count(AiInteraction.id).desc())
        .limit(10)
        .all()
    )

    daily_counts = (
        db.session.query(
            func.date(AiInteraction.created_at).label("day"),
            func.count(AiInteraction.id).label("count"),
        )
        .filter(AiInteraction.created_at >= today_start - timedelta(days=6))
        .group_by(func.date(AiInteraction.created_at))
        .order_by(func.date(AiInteraction.created_at).asc())
        .all()
    )

    return jsonify({
        "total_queries": total_queries,
        "total_tokens": total_tokens,
        "top_users": [
            {"email": u.email, "tier": u.tier, "queries": u.queries, "tokens": u.tokens}
            for u in top_users
        ],
        "daily_trend": [
            {"day": d.day.isoformat(), "count": d.count}
            for d in daily_counts
        ],
    })


@admin_bp.route("/api/users")
@login_required
@_admin_required
def api_users():
    q = request.args.get("q", "").strip()
    query = User.query.order_by(User.created_at.desc())
    if q:
        query = query.filter(User.email.ilike(f"%{q}%"))
    users = query.all()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ai_counts = dict(
        db.session.query(
            AiInteraction.user_id,
            func.count(AiInteraction.id),
        )
        .filter(AiInteraction.created_at >= today_start)
        .group_by(AiInteraction.user_id)
        .all()
    )

    rows = []
    for u in users:
        rows.append({
            "id": str(u.id),
            "email": u.email,
            "tier": u.tier,
            "display_name": u.display_name,
            "last_login": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "ai_queries_today": ai_counts.get(u.id, 0),
        })

    return jsonify({"users": rows})


@admin_bp.route("/api/users/<user_id>")
@login_required
@_admin_required
def api_user_detail(user_id):
    try:
        uuid_lib.UUID(str(user_id))
    except ValueError:
        abort(404)
    u = User.query.get(user_id)
    if not u:
        abort(404)

    interactions = AiInteraction.query.filter(
        AiInteraction.user_id == u.id
    ).order_by(AiInteraction.created_at.desc()).limit(50).all()

    return jsonify({
        "user": {
            "id": str(u.id),
            "email": u.email,
            "tier": u.tier,
            "display_name": u.display_name,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "is_pro": u.is_pro,
            "last_login": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        },
        "ai_interactions": [
            {
                "message": i.message[:200],
                "response": i.response[:200],
                "tokens_used": i.tokens_used,
                "model_name": i.model_name,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in interactions
        ],
    })


@admin_bp.route("/api/users/<user_id>/tier", methods=["POST"])
@login_required
@_admin_required
def api_user_tier(user_id):
    try:
        uuid_lib.UUID(str(user_id))
    except ValueError:
        abort(404)
    u = User.query.get(user_id)
    if not u:
        abort(404)

    data = request.get_json(force=True)
    new_tier = (data.get("tier") or "").strip()
    if new_tier not in ("core", "pro", "admin"):
        return jsonify({"ok": False, "error": "Invalid tier. Must be core, pro, or admin."}), 400

    u.tier = new_tier
    db.session.commit()
    return jsonify({"ok": True, "tier": new_tier})


@admin_bp.route("/api/system")
@login_required
@_admin_required
def api_system():
    total_users = User.query.count()
    total_ai = AiInteraction.query.count()
    total_events = BotEvent.query.count()
    total_waitlist = WaitlistEntry.query.count()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    users_today = User.query.filter(User.created_at >= today_start).count()
    ai_today = AiInteraction.query.filter(AiInteraction.created_at >= today_start).count()
    events_today = BotEvent.query.filter(BotEvent.timestamp >= today_start).count()

    return jsonify({
        "total_users": total_users,
        "users_today": users_today,
        "total_ai_interactions": total_ai,
        "ai_today": ai_today,
        "total_bot_events": total_events,
        "events_today": events_today,
        "total_waitlist": total_waitlist,
    })


@admin_bp.route("/api/bot/health")
@login_required
@_admin_required
def api_bot_health():
    now = now_et()
    today = now.date()
    today_start_utc = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    events = (
        BotEvent.query
        .filter(BotEvent.timestamp >= today_start_utc)
        .order_by(BotEvent.timestamp.desc())
        .all()
    )

    health, health_note = compute_health(events)
    equity = _parse_equity_from_log()
    log_tail = _read_log_tail(50)

    last_event = events[0] if events else None
    last_scan = None
    for e in events:
        if e.event == "scan":
            last_scan = e
            break

    events_today = len(events)
    errors_today = sum(1 for e in events if e.event == "error")

    positions = {}
    for e in reversed(events):
        sym = e.symbol
        if sym not in SYMBOLS:
            continue
        if e.event in ("position_opened", "position") and e.status in ("filled", "active"):
            positions[sym] = {
                "side": e.side or "unknown",
                "price": e.price,
                "qty": e.qty,
                "status": e.status,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
        elif e.event == "exit" and sym in positions:
            del positions[sym]

    symbols = {}
    for sym in SYMBOLS:
        sym_events = [e for e in events if e.symbol == sym]
        last_sym_event = sym_events[0] if sym_events else None
        pos = positions.get(sym)

        if pos:
            status = f"{pos['side']}_active"
        elif last_sym_event and last_sym_event.event == "error":
            status = "error"
        elif last_sym_event and last_sym_event.event == "skip":
            status = "skipped"
        elif last_sym_event and last_sym_event.event == "scan":
            status = "scanning"
        else:
            status = "flat"

        symbols[sym] = {
            "status": status,
            "last_event": last_sym_event.event if last_sym_event else None,
            "last_time": last_sym_event.timestamp.isoformat() if last_sym_event and last_sym_event.timestamp else None,
            "position": pos,
        }

    return jsonify({
        "status": health,
        "status_note": health_note,
        "market_state": "open" if market_open_state(now) else "closed",
        "equity": equity,
        "events_today": events_today,
        "errors_today": errors_today,
        "active_positions": len(positions),
        "last_event_time": last_event.timestamp.isoformat() if last_event else None,
        "last_scan_time": last_scan.timestamp.isoformat() if last_scan else None,
        "recent_events": [
            {
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "event": e.event,
                "symbol": e.symbol,
                "side": e.side,
                "price": e.price,
                "qty": e.qty,
                "status": e.status,
                "message": e.message,
            }
            for e in events[:20]
        ],
        "symbols": symbols,
        "log_tail": log_tail,
    })
