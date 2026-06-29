import uuid as uuid_lib
import logging
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.ai_interaction import AiInteraction
from app.models.waitlist_entry import WaitlistEntry

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
            "skill_level": u.skill_level,
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
            "skill_level": u.skill_level,
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
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = User.query.count()
    core_users = User.query.filter_by(tier="core").count()
    pro_users = User.query.filter_by(tier="pro").count()
    admin_users = User.query.filter_by(tier="admin").count()
    users_today = User.query.filter(User.created_at >= today_start).count()

    total_ai = AiInteraction.query.count()
    ai_today = AiInteraction.query.filter(AiInteraction.created_at >= today_start).count()
    total_waitlist = WaitlistEntry.query.count()

    from app.models.lesson import Lesson
    from app.models.progress import UserProgress
    lessons_completed_today = UserProgress.query.filter(
        UserProgress.completed_at >= today_start,
        UserProgress.status == "completed"
    ).count()
    total_completions = UserProgress.query.filter_by(status="completed").count()

    return jsonify({
        "total_users": total_users,
        "core_users": core_users,
        "pro_users": pro_users,
        "admin_users": admin_users,
        "users_today": users_today,
        "total_ai_interactions": total_ai,
        "ai_today": ai_today,
        "total_waitlist": total_waitlist,
        "lessons_completed_today": lessons_completed_today,
        "total_lesson_completions": total_completions,
    })


@admin_bp.route("/api/curriculum")
@login_required
@_admin_required
def api_curriculum():
    from app.models.lesson import Lesson
    from app.models.module import Module
    from app.models.progress import UserProgress

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    modules = (
        db.session.query(
            Module.id,
            Module.title,
            Module.slug,
            Module.sort_order,
            func.count(Lesson.id).label("total_lessons"),
        )
        .outerjoin(Lesson, db.and_(Lesson.module_id == Module.id, Lesson.is_published.is_(True)))
        .filter(Module.is_published.is_(True))
        .group_by(Module.id, Module.title, Module.slug, Module.sort_order)
        .order_by(Module.sort_order)
        .all()
    )

    module_stats = []
    for m in modules:
        completions = (
            db.session.query(func.count(UserProgress.id))
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .filter(
                Lesson.module_id == m.id,
                UserProgress.status == "completed",
            )
            .scalar() or 0
        )
        completions_today = (
            db.session.query(func.count(UserProgress.id))
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .filter(
                Lesson.module_id == m.id,
                UserProgress.status == "completed",
                UserProgress.completed_at >= today_start,
            )
            .scalar() or 0
        )
        module_stats.append({
            "title": m.title,
            "slug": m.slug,
            "total_lessons": m.total_lessons,
            "total_completions": completions,
            "completions_today": completions_today,
        })

    return jsonify({"modules": module_stats})
