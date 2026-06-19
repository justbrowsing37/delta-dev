import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config) -> Flask:
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(__name__,
                template_folder=os.path.join(_root, "app", "templates"),
                static_folder=os.path.join(_root, "static"))
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    from app import models  # noqa: ensure models are registered with SQLAlchemy metadata

    from app.routes import register_blueprints
    register_blueprints(app)

    from app.routes.api import api_bp
    from app.routes.workspace import workspace_bp
    csrf.exempt(api_bp)
    csrf.exempt(workspace_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.shell_context_processor
    def shell_context():
        from app.models import User, Module, Lesson, UserProgress, BotEvent, WaitlistEntry
        return {"db": db, "User": User, "Module": Module, "Lesson": Lesson,
                "UserProgress": UserProgress, "BotEvent": BotEvent,
                "WaitlistEntry": WaitlistEntry}

    return app
