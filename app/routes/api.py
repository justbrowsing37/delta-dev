import logging
from flask import Blueprint, jsonify, abort, request
from flask_login import login_required, current_user

from app.services.ai_service import AiService, RateLimitExceeded

log = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


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


CONCEPT_NODES = [
    {"id": "stock",              "label": "Stock",                 "group": "module0", "moduleSlug": "what-is-the-market",       "lessonSlug": "what-is-a-stock",               "description": "A stock is a fractional ownership stake in a company. When you buy a share, you own a tiny slice of that business."},
    {"id": "exchange",           "label": "Stock Exchange",        "group": "module0", "moduleSlug": "what-is-the-market",       "lessonSlug": "how-does-a-stock-exchange-work",  "description": "A central marketplace where buyers and sellers meet to trade shares electronically."},
    {"id": "price",              "label": "Price Movement",        "group": "module0", "moduleSlug": "what-is-the-market",       "lessonSlug": "what-moves-a-stock-price",        "description": "Stock prices move based on supply and demand — more buyers than sellers drives price up, and vice versa."},
    {"id": "support_resistance", "label": "Support & Resistance",  "group": "module1", "moduleSlug": "reading-the-market",      "lessonSlug": "support-and-resistance",           "description": "Price levels where buying or selling pressure consistently stops a move — the floor and ceiling of price action."},
    {"id": "trading_range",      "label": "Trading Range",         "group": "module1", "moduleSlug": "reading-the-market",      "lessonSlug": "what-is-a-trading-range",         "description": "A sideways price zone between support and resistance where buyers and sellers are balanced."},
    {"id": "breakout",           "label": "Breakouts & Fakeouts",  "group": "module1", "moduleSlug": "reading-the-market",      "lessonSlug": "breakouts-vs-fakeouts",            "description": "A breakout pushes beyond a range edge; a fakeout reverses back inside, trapping traders who chased the move."},
    {"id": "institutional",      "label": "Retail vs Institutions","group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "retail-vs-institutional-traders",  "description": "Retail traders trade with emotion and small capital; institutions use algorithms and seek large positions."},
    {"id": "liquidity",          "label": "Liquidity",             "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "what-is-liquidity",               "description": "The pool of resting orders waiting to be filled. Institutions need liquidity to enter and exit large positions."},
    {"id": "stop_hunt",          "label": "Stop Hunts",            "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "why-stop-hunts-happen",           "description": "Price deliberately pushed beyond a key level to trigger clustered stop-loss orders, providing liquidity for institutions."},
    {"id": "sweep",              "label": "Liquidity Sweep",       "group": "module2", "moduleSlug": "how-big-money-moves",     "lessonSlug": "liquidity-sweeps-explained",      "description": "The core pattern: price sweeps beyond a range edge (triggering stops), then reverses — the fakeout is the signal."},
    {"id": "delta_scan",         "label": "Delta One Scan",        "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "what-delta-one-looks-for",        "description": "Delta One scans for 4H range structure + 5-minute sweep + 50 EMA trend alignment — all three must align before acting."},
    {"id": "entry",              "label": "Entry Conditions",      "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "entry-conditions",                "description": "Entry requires sweep confirmation + ATR-based stop placement + minimum 1.5R reward-to-risk + position sizing at 2% equity risk."},
    {"id": "risk",               "label": "Risk Management",       "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "risk-management",                 "description": "Multiple layers: per-trade 2% risk, ATR-based stops, daily circuit breaker, consecutive loss breaker."},
    {"id": "flip",               "label": "Flip Direction",        "group": "module3", "moduleSlug": "the-sweep-strategy",     "lessonSlug": "when-to-flip-direction",          "description": "If the market reverses, the engine can flip position direction — but only after fresh sweep confirmation on the opposite side."},
    {"id": "read_signal",        "label": "Reading Signals",       "group": "module4", "moduleSlug": "understanding-the-signals", "lessonSlug": "how-to-read-a-delta-one-signal",  "description": "A signal card shows symbol, side, price, timestamp, and event type — each linked to an educational explanation."},
    {"id": "paper_trade",        "label": "Paper Trading",         "group": "module4", "moduleSlug": "understanding-the-signals", "lessonSlug": "paper-trading-a-signal",           "description": "Simulated trading to practice reading signals and managing trades without real financial risk."},
]

CONCEPT_EDGES = [
    {"from": "stock",              "to": "exchange",            "arrows": "to"},
    {"from": "stock",              "to": "price",               "arrows": "to"},
    {"from": "exchange",           "to": "support_resistance",  "arrows": "to"},
    {"from": "exchange",           "to": "trading_range",       "arrows": "to"},
    {"from": "price",              "to": "support_resistance",  "arrows": "to"},
    {"from": "price",              "to": "trading_range",       "arrows": "to"},
    {"from": "support_resistance", "to": "trading_range",       "arrows": "to"},
    {"from": "trading_range",      "to": "breakout",            "arrows": "to"},
    {"from": "breakout",           "to": "sweep",               "arrows": "to"},
    {"from": "institutional",      "to": "liquidity",           "arrows": "to"},
    {"from": "liquidity",          "to": "stop_hunt",           "arrows": "to"},
    {"from": "stop_hunt",          "to": "sweep",               "arrows": "to"},
    {"from": "sweep",              "to": "delta_scan",          "arrows": "to"},
    {"from": "delta_scan",         "to": "entry",               "arrows": "to"},
    {"from": "entry",              "to": "risk",                "arrows": "to"},
    {"from": "entry",              "to": "flip",                "arrows": "to"},
    {"from": "risk",               "to": "flip",                "arrows": "to"},
    {"from": "sweep",              "to": "read_signal",         "arrows": "to"},
    {"from": "read_signal",        "to": "paper_trade",         "arrows": "to"},
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
