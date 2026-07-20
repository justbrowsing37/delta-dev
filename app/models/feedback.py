import uuid
from datetime import datetime, timezone
from app.extensions import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id            = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id       = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id    = db.Column(db.String(100), nullable=False, index=True)  # e.g. "0.1", "0.1A", "0-check"
    understood    = db.Column(db.Boolean, nullable=False)                   # True = Yes, False = No
    comment       = db.Column(db.Text)
    want_module_1 = db.Column(db.Boolean)                                   # only set on the check screen
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "content_id", name="uq_feedback_user_content"),
    )

    def __repr__(self):
        return f"<Feedback user={self.user_id} content={self.content_id} understood={self.understood}>"
