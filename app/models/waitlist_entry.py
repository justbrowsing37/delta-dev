import uuid
from datetime import datetime, timezone
from app.extensions import db


class WaitlistEntry(db.Model):
    __tablename__ = "waitlist_entries"

    id         = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    email      = db.Column(db.String(255), unique=True, nullable=False, index=True)
    source     = db.Column(db.String(50), default="landing")
    converted  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<WaitlistEntry {self.email}>"
