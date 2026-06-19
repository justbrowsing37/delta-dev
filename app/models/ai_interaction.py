import uuid
from datetime import datetime, timezone
from app.extensions import db


class AiInteraction(db.Model):
    __tablename__ = "ai_interactions"

    id          = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id     = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    message     = db.Column(db.Text, nullable=False)
    response    = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    model_name  = db.Column(db.String(100))
    tier        = db.Column(db.String(20))
    created_at  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="ai_interactions")

    def __repr__(self):
        return f"<AiInteraction {self.id} user={self.user_id} model={self.model_name}>"
