import uuid
from datetime import datetime, timezone
from app.extensions import db


class Lesson(db.Model):
    __tablename__ = "lessons"

    id                  = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    module_id           = db.Column(db.Uuid, db.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    title               = db.Column(db.String(200), nullable=False)
    slug                = db.Column(db.String(200), nullable=False)
    content             = db.Column(db.Text)
    content_type        = db.Column(db.String(20), default="html")
    item_type           = db.Column(db.String(20), default="lesson")
    connects_to         = db.Column(db.JSON, default=list)
    sort_order          = db.Column(db.Integer, default=0)
    estimated_minutes   = db.Column(db.Integer, default=5)
    is_published        = db.Column(db.Boolean, default=False)
    concept_tags        = db.Column(db.JSON, default=list)
    related_signal_type = db.Column(db.String(50))
    created_at          = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at          = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    module       = db.relationship("Module", back_populates="lessons")
    user_progress = db.relationship("UserProgress", back_populates="lesson", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("module_id", "slug", name="uq_lesson_module_slug"),
    )

    def __repr__(self):
        return f"<Lesson {self.slug}>"
