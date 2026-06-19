from datetime import datetime, timezone

from app.extensions import db
from app.models.bot_event import BotEvent

EXPLANATIONS = {
    "scan": {
        "title": "Liquidity Sweep Detected",
        "summary": "A sweep setup was identified on the 4-hour range.",
        "educational": (
            "Delta One's scanner detected a 5-minute candle that swept beyond "
            "the 4-hour range edge and closed back inside. This is the core "
            "setup: price broke a key level (triggering stop-losses clustered "
            "there), then failed to hold the breakout — a telltale fakeout. "
            "The engine now checks trend alignment and ATR-based risk before "
            "deciding whether to enter."
        ),
        "related_module_slug": "the-sweep-strategy",
        "related_lesson_slug": "what-delta-one-looks-for",
    },
    "position_opened": {
        "title": "Position Opened",
        "summary": "A trade was entered on a confirmed sweep reversal.",
        "educational": (
            "All three entry confluences aligned: the sweep was detected, the "
            "50 EMA trend filter confirmed the direction, and the risk-reward "
            "ratio met the minimum threshold. A market order was placed with an "
            "ATR-based stop-loss and a take-profit at the opposite range edge. "
            "Position size was calculated as 2% of equity divided by the "
            "stop distance."
        ),
        "related_module_slug": "the-sweep-strategy",
        "related_lesson_slug": "entry-conditions",
    },
    "exit": {
        "title": "Position Closed",
        "summary": "A trade was closed at take-profit or stop-loss.",
        "educational": (
            "The position was closed either because price hit the take-profit "
            "target (the opposite range edge) or the stop-loss was triggered. "
            "Every trade has a defined exit — there are no open-ended holds. "
            "If the take-profit was reached, the sweep thesis played out. If "
            "the stop was hit, the setup failed and risk was contained."
        ),
        "related_module_slug": "understanding-the-signals",
        "related_lesson_slug": "paper-trading-a-signal",
    },
    "order_submitted": {
        "title": "Order Submitted",
        "summary": "An entry or exit order was sent to the broker.",
        "educational": (
            "An order was submitted to the broker for execution. For entries, "
            "this happens when the sweep + confluence criteria are satisfied. "
            "For exits, this happens at take-profit or stop-loss levels. The "
            "engine uses market orders to ensure execution, accepting a small "
            "amount of slippage in exchange for certainty."
        ),
        "related_module_slug": "the-sweep-strategy",
        "related_lesson_slug": "entry-conditions",
    },
    "skip": {
        "title": "Sweep Skipped",
        "summary": "A sweep was detected but did not meet entry criteria.",
        "educational": (
            "Price swept the range edge, but one or more confluences failed: "
            "the 50 EMA trend did not align with the reversal direction, or "
            "the risk-reward ratio was below the 1.5R minimum, or swing "
            "structure did not confirm. Skipping marginal setups is a core "
            "part of the strategy — not every sweep is worth trading."
        ),
        "related_module_slug": "the-sweep-strategy",
        "related_lesson_slug": "entry-conditions",
    },
    "error": {
        "title": "Error Event",
        "summary": "The engine encountered an issue.",
        "educational": (
            "An unexpected error occurred during engine operation. This could "
            "be a connection issue with the broker, a data feed interruption, "
            "or a configuration problem. Errors are logged and the engine's "
            "circuit breaker may pause trading if errors exceed thresholds."
        ),
        "related_module_slug": None,
        "related_lesson_slug": None,
    },
    "position": {
        "title": "Position Update",
        "summary": "An existing position was updated or adjusted.",
        "educational": (
            "A previously opened position was modified — the stop-loss may "
            "have been adjusted to breakeven, the take-profit may have been "
            "scaled, or a partial exit was executed. Delta One manages "
            "positions actively, not just at entry and exit."
        ),
        "related_module_slug": "the-sweep-strategy",
        "related_lesson_slug": "risk-management",
    },
}


class SignalExplainerService:

    @classmethod
    def get_explanation(cls, event_type):
        return EXPLANATIONS.get(
            event_type,
            {
                "title": "Unknown Event",
                "summary": "An unrecognized event type was logged.",
                "educational": (
                    "This event type is not part of the standard sweep "
                    "strategy workflow. Check the raw message field for "
                    "more details."
                ),
                "related_module_slug": None,
                "related_lesson_slug": None,
            },
        )

    @classmethod
    def get_recent_signals(cls, limit=20):
        events = (
            BotEvent.query
            .order_by(BotEvent.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [cls._enrich(e) for e in events]

    @classmethod
    def get_signal_by_id(cls, signal_id):
        event = db.session.get(BotEvent, signal_id)
        if not event:
            return None
        return cls._enrich(event)

    @classmethod
    def _enrich(cls, event):
        explanation = cls.get_explanation(event.event)
        return {
            "id": event.id,
            "timestamp": event.timestamp,
            "event": event.event,
            "symbol": event.symbol,
            "side": event.side,
            "price": event.price,
            "qty": event.qty,
            "status": event.status,
            "message": event.message,
            "title": explanation["title"],
            "summary": explanation["summary"],
            "educational": explanation["educational"],
            "related_module_slug": explanation["related_module_slug"],
            "related_lesson_slug": explanation["related_lesson_slug"],
        }
