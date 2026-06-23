import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    tier = db.Column(db.String(20), default="core")
    is_active = db.Column(db.Boolean, default=True)
    onboarding_complete = db.Column(db.Boolean, default=False)
    skill_level = db.Column(db.String(20), default="beginner")
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login_at = db.Column(db.DateTime(timezone=True))

    progress = db.relationship("UserProgress", back_populates="user", lazy="dynamic")
    ai_interactions = db.relationship(
        "AiInteraction", back_populates="user", lazy="dynamic"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_pro(self) -> bool:
        return self.tier == "pro"

    @property
    def is_admin(self) -> bool:
        return self.tier == "admin"

    def __repr__(self):
        return f"<User {self.email} tier={self.tier}>"
