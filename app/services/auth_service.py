from app.models.user import User
from app.extensions import db


class AuthService:
    @staticmethod
    def create_user(email, password, display_name=None):
        email = email.strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            return None, "Email already registered"
        user = User(email=email, display_name=display_name or email.split("@")[0])
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def authenticate(email, password):
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        return user, None
