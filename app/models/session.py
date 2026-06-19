import uuid
from datetime import datetime, timezone
from app.extensions import db


class Session(db.Model):
    __tablename__ = "sessions"

    id         = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id    = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token      = db.Column(db.String(255), unique=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    expires_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref=db.backref("sessions", lazy="dynamic"))
