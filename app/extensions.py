import uuid

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    # Flask-Login always hands back the id as a string (from the session
    # cookie), but User.id is a UUID column. Passing the raw string breaks on
    # SQLite ('str' has no attribute 'hex'), so coerce to UUID first.
    try:
        uid = uuid.UUID(str(user_id))
    except (ValueError, TypeError, AttributeError):
        return None
    return db.session.get(User, uid)
