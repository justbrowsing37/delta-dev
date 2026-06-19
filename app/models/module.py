import uuid
from datetime import datetime, timezone
from app.extensions import db


class Module(db.Model):
    __tablename__ = "modules"

    id           = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    title        = db.Column(db.String(200), nullable=False)
    slug         = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description  = db.Column(db.Text)
    icon         = db.Column(db.String(50))
    sort_order   = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    lessons = db.relationship(
        "Lesson", back_populates="module",
        order_by="Lesson.sort_order",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Module {self.slug}>"
