from datetime import datetime, timezone
from app.extensions import db


class BotEvent(db.Model):
    __tablename__ = "bot_events"

    id        = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    event     = db.Column(db.String(50), nullable=False, index=True)
    symbol    = db.Column(db.String(10), index=True)
    side      = db.Column(db.String(10))
    price     = db.Column(db.Float)
    qty       = db.Column(db.Integer)
    status    = db.Column(db.String(30))
    message   = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.Index("idx_bot_events_event_ts", "event", "timestamp"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event": self.event,
            "symbol": self.symbol,
            "side": self.side,
            "price": self.price,
            "qty": self.qty,
            "status": self.status,
            "message": self.message,
        }

    def __repr__(self):
        return f"<BotEvent {self.event} {self.symbol} @ {self.timestamp}>"
