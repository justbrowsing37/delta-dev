import uuid
from datetime import datetime, timezone
from app.extensions import db


class UserProgress(db.Model):
    __tablename__ = "user_progress"

    id           = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id      = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id    = db.Column(db.Uuid, db.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    status       = db.Column(db.String(20), default="not_started")
    score        = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime(timezone=True))
    created_at   = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user   = db.relationship("User", back_populates="progress")
    lesson = db.relationship("Lesson", back_populates="user_progress")

    __table_args__ = (
        db.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )
