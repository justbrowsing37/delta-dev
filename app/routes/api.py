import logging
from datetime import datetime, timedelta, timezone
from collections import Counter
from sqlalchemy import func
from flask import Blueprint, jsonify, abort, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.bot_event import BotEvent
from app.services.signal_explainer import SignalExplainerService
from app.services.ai_service import AiService, RateLimitExceeded
from app.utils.market import TIMEZONE, SYMBOLS, PAPER, now_et, market_open_state, compute_health

log = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


def _today_start():
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _latest_event(event_type=None, symbol=None):
    q = BotEvent.query.order_by(BotEvent.timestamp.desc())
    if event_type:
        q = q.filter(BotEvent.event == event_type)
    if symbol:
        q = q.filter(BotEvent.symbol == symbol.upper())
    return q.first()


def _active_positions():
    events = (
        BotEvent.query.filter(BotEvent.symbol.in_(SYMBOLS))
        .order_by(BotEvent.timestamp.asc())
        .all()
    )
    positions = {}
    for e in events:
        sym = e.symbol
        if e.event in ("position_opened", "position") and e.status in ("filled", "active"):
            positions[sym] = {
                "symbol": sym,
                "side": e.side or "unknown",
                "price": e.price,
                "qty": e.qty,
                "status": e.status,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "value": (e.price or 0) * (e.qty or 0),
            }
        elif e.event == "exit":
            positions.pop(sym, None)
    return positions


@api_bp.route("/summary")
@login_required
def summary():
    try:
        now = now_et()
        today = _today_start()

        total = BotEvent.query.count()
        if total == 0:
            return jsonify({
                "bot_status": "critical",
                "health_note": "No events yet",
                "market_state": "open" if market_open_state(now) else "closed",
                "mode": "paper" if PAPER else "live",
                "last_event_time": None,
                "last_scan_time": None,
                "events_today": 0,
                "errors_today": 0,
                "active_positions": 0,
                "last_refresh_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            })

        last = _latest_event()
        last_scan = _latest_event(event_type="scan")
        positions = _active_positions()
        health, health_note = compute_health([last] if last else [])

        events_today = BotEvent.query.filter(BotEvent.timestamp >= today).count()
        errors_today = BotEvent.query.filter(
            BotEvent.timestamp >= today, BotEvent.event == "error"
        ).count()

        return jsonify({
            "bot_status": health,
            "health_note": health_note,
            "market_state": "open" if market_open_state(now) else "closed",
            "mode": "paper" if PAPER else "live",
            "last_event_time": last.timestamp.isoformat() if last and last.timestamp else None,
            "last_scan_time": last_scan.timestamp.isoformat() if last_scan and last_scan.timestamp else None,
            "events_today": events_today,
            "errors_today": errors_today,
            "active_positions": len(positions),
            "last_refresh_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        })
    except Exception as e:
        log.error("Summary endpoint failed: %s", e)
        return jsonify({"bot_status": "error", "health_note": "Data unavailable"}), 500


@api_bp.route("/activity")
@login_required
def activity():
    try:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=60)

        recent = (
            BotEvent.query.filter(BotEvent.timestamp >= cutoff)
            .order_by(BotEvent.timestamp.asc())
            .all()
        )

        if not recent:
            return jsonify({"labels": [], "datasets": {}})

        buckets = {}
        for e in recent:
            if not e.timestamp:
                continue
            key = e.timestamp.astimezone(TIMEZONE).strftime("%H:%M")
            if key not in buckets:
                buckets[key] = Counter()
            buckets[key][e.event] += 1

        labels = sorted(buckets.keys())
        event_types = ["scan", "order_submitted", "position_opened", "exit", "skip", "error", "position"]
        datasets = {et: [buckets[label].get(et, 0) for label in labels] for et in event_types}

        return jsonify({"labels": labels, "datasets": datasets})
    except Exception as e:
        log.error("Activity endpoint failed: %s", e)
        return jsonify({"labels": [], "datasets": {}}), 500


@api_bp.route("/symbol/<symbol>")
@login_required
def symbol(symbol):
    try:
        symbol = symbol.upper()
        sym_events = (
            BotEvent.query.filter(BotEvent.symbol == symbol)
            .order_by(BotEvent.timestamp.desc())
            .all()
        )

        if not sym_events:
            return jsonify({
                "symbol": symbol,
                "status": "flat",
                "latest_action": None,
                "latest_time": None,
                "position": None,
                "recent_events": [],
            })

        last = sym_events[0]
        positions = _active_positions()
        current_pos = positions.get(symbol)
        recent = [e.to_dict() for e in reversed(sym_events[:12])]

        if current_pos:
            status = f"{current_pos.get('side', 'unknown')}_active"
        elif last.event == "error":
            status = "error"
        elif last.event == "skip":
            status = "skipped"
        elif last.event == "scan":
            status = "scanning"
        else:
            status = "flat"

        return jsonify({
            "symbol": symbol,
            "status": status,
            "latest_action": last.event,
            "latest_time": last.timestamp.isoformat() if last.timestamp else None,
            "position": current_pos,
            "recent_events": recent,
        })
    except Exception as e:
        log.error("Symbol endpoint failed for %s: %s", symbol, e)
        return jsonify({"symbol": symbol, "status": "error"}), 500


@api_bp.route("/footer")
@login_required
def footer():
    try:
        today = _today_start()

        today_error_rows = (
            BotEvent.query.filter(
                BotEvent.timestamp >= today, BotEvent.event == "error"
            )
            .order_by(BotEvent.timestamp.desc())
            .limit(8)
            .all()
        )

        today_skip_rows = (
            BotEvent.query.filter(
                BotEvent.timestamp >= today, BotEvent.event == "skip"
            )
            .order_by(BotEvent.timestamp.desc())
            .limit(8)
            .all()
        )

        count_rows = (
            db.session.query(BotEvent.event, func.count())
            .filter(BotEvent.timestamp >= today)
            .group_by(BotEvent.event)
            .all()
        )

        errors = [
            {
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "symbol": r.symbol,
                "message": r.message,
            }
            for r in today_error_rows
        ]

        skips = [
            {
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "symbol": r.symbol,
                "message": r.message,
                "status": r.status,
            }
            for r in today_skip_rows
        ]

        event_counts = {event: count for event, count in count_rows}

        return jsonify({
            "errors": errors,
            "skips": skips,
            "event_counts": event_counts,
        })
    except Exception as e:
        log.error("Footer endpoint failed: %s", e)
        return jsonify({"errors": [], "skips": [], "event_counts": {}}), 500


@api_bp.route("/signals/live")
@login_required
def signals_live():
    try:
        signals = SignalExplainerService.get_recent_signals(limit=20)
        results = []
        for s in signals:
            row = {
                "id": s["id"],
                "timestamp": s["timestamp"].isoformat() if s["timestamp"] else None,
                "event": s["event"],
                "symbol": s["symbol"],
                "side": s["side"],
                "price": s["price"],
                "qty": s["qty"],
                "status": s["status"],
                "message": s["message"],
                "title": s["title"],
                "summary": s["summary"],
                "educational": s["educational"],
            }
            if s["related_module_slug"] and s["related_lesson_slug"]:
                row["related_lesson_url"] = f"/lessons/{s['related_module_slug']}/{s['related_lesson_slug']}"
            results.append(row)
        return jsonify({"signals": results})
    except Exception as e:
        log.error("Signals/live endpoint failed: %s", e)
        return jsonify({"signals": []}), 500


@api_bp.route("/ai/ask", methods=["POST"])
@login_required
def ai_ask():
    body = request.get_json(force=True)
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        response = AiService.ask(current_user, message)
        usage = AiService.get_usage_today(current_user)
        return jsonify({"response": response, "usage": usage})
    except RateLimitExceeded as e:
        return jsonify({
            "error": f"Daily limit reached. You can make {e.limit} queries per day.",
            "limit": e.limit,
        }), 429
    except Exception as e:
        log.error("AI ask failed: %s", e)
        return jsonify({"error": "AI service unavailable"}), 500


@api_bp.route("/admin/ai/usage/today")
@login_required
def admin_ai_usage_today():
    if not current_user.is_admin:
        return jsonify({"error": "Forbidden"}), 403
    try:
        from app.models.ai_interaction import AiInteraction

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        count = AiInteraction.query.filter(AiInteraction.created_at >= today_start).count()
        return jsonify({"today": count})
    except Exception as e:
        log.error("Admin AI usage endpoint failed: %s", e)
        return jsonify({"today": 0}), 500


CONCEPT_NODES = [
    {"id": "stock",             "label": "Stock",              "group": "module0", "moduleSlug": "what-is-the-market",      "lessonSlug": "what-is-a-stock",              "description": "A stock is a fractional ownership stake in a company. When you buy a share, you own a tiny slice of that business."},
    {"id": "exchange",          "label": "Stock Exchange",     "group": "module0", "moduleSlug": "what-is-the-market",      "lessonSlug": "how-does-a-stock-exchange-work", "description": "A central marketplace where buyers and sellers meet to trade shares electronically."},
    {"id": "price",             "label": "Price Movement",     "group": "module0", "moduleSlug": "what-is-the-market",      "lessonSlug": "what-moves-a-stock-price",       "description": "Stock prices move based on supply and demand — more buyers than sellers drives price up, and vice versa."},
    {"id": "support_resistance","label": "Support & Resistance","group": "module1","moduleSlug": "reading-the-market",     "lessonSlug": "support-and-resistance",          "description": "Price levels where buying or selling pressure consistently stops a move — the floor and ceiling of price action."},
    {"id": "trading_range",     "label": "Trading Range",      "group": "module1", "moduleSlug": "reading-the-market",     "lessonSlug": "what-is-a-trading-range",        "description": "A sideways price zone between support and resistance where buyers and sellers are balanced."},
    {"id": "breakout",          "label": "Breakouts & Fakeouts","group": "module1","moduleSlug": "reading-the-market",     "lessonSlug": "breakouts-vs-fakeouts",           "description": "A breakout pushes beyond a range edge; a fakeout reverses back inside, trapping traders who chased the move."},
    {"id": "institutional",     "label": "Retail vs Institutions","group": "module2","moduleSlug": "how-big-money-moves",  "lessonSlug": "retail-vs-institutional-traders", "description": "Retail traders trade with emotion and small capital; institutions use algorithms and seek large positions."},
    {"id": "liquidity",         "label": "Liquidity",          "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "what-is-liquidity",              "description": "The pool of resting orders waiting to be filled. Institutions need liquidity to enter and exit large positions."},
    {"id": "stop_hunt",         "label": "Stop Hunts",         "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "why-stop-hunts-happen",          "description": "Price deliberately pushed beyond a key level to trigger clustered stop-loss orders, providing liquidity for institutions."},
    {"id": "sweep",             "label": "Liquidity Sweep",    "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "liquidity-sweeps-explained",     "description": "The core pattern: price sweeps beyond a range edge (triggering stops), then reverses — the fakeout is the signal."},
    {"id": "delta_scan",        "label": "Delta One Scan",     "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "what-delta-one-looks-for",       "description": "Delta One scans for 4H range structure + 5-minute sweep + 50 EMA trend alignment — all three must align before acting."},
    {"id": "entry",             "label": "Entry Conditions",   "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "entry-conditions",               "description": "Entry requires sweep confirmation + ATR-based stop placement + minimum 1.5R reward-to-risk + position sizing at 2% equity risk."},
    {"id": "risk",              "label": "Risk Management",    "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "risk-management",                "description": "Multiple layers: per-trade 2% risk, ATR-based stops, daily circuit breaker, consecutive loss breaker."},
    {"id": "flip",              "label": "Flip Direction",     "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "when-to-flip-direction",         "description": "If the market reverses, the engine can flip position direction — but only after fresh sweep confirmation on the opposite side."},
    {"id": "read_signal",       "label": "Reading Signals",    "group": "module4", "moduleSlug": "understanding-the-signals","lessonSlug": "how-to-read-a-delta-one-signal", "description": "A signal card shows symbol, side, price, timestamp, and event type — each linked to an educational explanation."},
    {"id": "paper_trade",       "label": "Paper Trading",      "group": "module4", "moduleSlug": "understanding-the-signals","lessonSlug": "paper-trading-a-signal",          "description": "Simulated trading to practice reading signals and managing trades without real financial risk."},
]

CONCEPT_EDGES = [
    {"from": "stock",              "to": "exchange",           "arrows": "to"},
    {"from": "stock",              "to": "price",              "arrows": "to"},
    {"from": "exchange",           "to": "support_resistance", "arrows": "to"},
    {"from": "exchange",           "to": "trading_range",      "arrows": "to"},
    {"from": "price",              "to": "support_resistance", "arrows": "to"},
    {"from": "price",              "to": "trading_range",      "arrows": "to"},
    {"from": "support_resistance", "to": "trading_range",      "arrows": "to"},
    {"from": "trading_range",      "to": "breakout",           "arrows": "to"},
    {"from": "breakout",           "to": "sweep",              "arrows": "to"},
    {"from": "institutional",      "to": "liquidity",          "arrows": "to"},
    {"from": "liquidity",          "to": "stop_hunt",          "arrows": "to"},
    {"from": "stop_hunt",          "to": "sweep",              "arrows": "to"},
    {"from": "sweep",              "to": "delta_scan",         "arrows": "to"},
    {"from": "delta_scan",         "to": "entry",              "arrows": "to"},
    {"from": "entry",              "to": "risk",               "arrows": "to"},
    {"from": "entry",              "to": "flip",               "arrows": "to"},
    {"from": "risk",               "to": "flip",               "arrows": "to"},
    {"from": "sweep",              "to": "read_signal",        "arrows": "to"},
    {"from": "read_signal",        "to": "paper_trade",        "arrows": "to"},
]

CONCEPT_DESCRIPTIONS = {n["id"]: {
    "title": n["label"],
    "description": n["description"],
    "module_slug": n["moduleSlug"],
    "lesson_slug": n["lessonSlug"],
} for n in CONCEPT_NODES}


@api_bp.route("/concepts")
@login_required
def concepts():
    return jsonify({"nodes": CONCEPT_NODES, "edges": CONCEPT_EDGES})


@api_bp.route("/concepts/<node_id>")
@login_required
def concept_detail(node_id):
    info = CONCEPT_DESCRIPTIONS.get(node_id)
    if not info:
        abort(404)
    from app.models.lesson import Lesson
    from app.models.module import Module
    lesson = (
        Lesson.query
        .join(Module, Lesson.module_id == Module.id)
        .filter(Module.slug == info["module_slug"], Lesson.slug == info["lesson_slug"])
        .first()
    )
    return jsonify({
        "id": node_id,
        "title": info["title"],
        "description": info["description"],
        "module_slug": info["module_slug"],
        "lesson_slug": info["lesson_slug"],
        "lesson_title": lesson.title if lesson else None,
        "lesson_content": lesson.content if lesson else None,
    })
