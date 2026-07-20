import os
import re
import click
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf

try:
    import markdown as md_lib
    def _md_filter(text):
        return md_lib.markdown(text or "", extensions=["nl2br", "tables"])
except ImportError:
    def _md_filter(text):
        # Fallback: minimal HTML escape + newline-to-br
        import html
        return html.escape(text or "").replace("\n", "<br>")


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
    from app.routes.onboarding import onboarding_bp
    from app.routes.module import module_bp
    csrf.exempt(api_bp)
    csrf.exempt(workspace_bp)
    csrf.exempt(onboarding_bp)
    csrf.exempt(module_bp)  # module feedback API uses JSON, not WTF forms

    # Jinja2 globals and filters
    app.jinja_env.globals['enumerate'] = enumerate
    app.jinja_env.filters['markdown'] = _md_filter

    @app.cli.command("seed-users")
    def seed_users():
        """Wipe all users and create 3 test users (admin, core, pro)."""
        from app.models.user import User
        click.echo("Wiping all users...")
        User.query.delete()
        db.session.commit()

        users = [
            {"email": "admin@admin.com", "password": "admin123", "tier": "admin",
             "display_name": "Admin", "onboarding_complete": True, "skill_level": "advanced"},
            {"email": "test@core.com", "password": "testing123", "tier": "core",
             "display_name": "Core User", "onboarding_complete": True, "skill_level": "beginner"},
            {"email": "test@pro.com", "password": "testing1234", "tier": "pro",
             "display_name": "Pro User", "onboarding_complete": True, "skill_level": "intermediate"},
        ]

        for u in users:
            user = User(
                email=u["email"],
                display_name=u["display_name"],
                tier=u["tier"],
                onboarding_complete=u["onboarding_complete"],
                skill_level=u["skill_level"]
            )
            user.set_password(u["password"])
            db.session.add(user)

        db.session.commit()
        click.echo("Done. Created: admin@admin.com, test@core.com, test@pro.com")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.shell_context_processor
    def shell_context():
        from app.models import User, Module, Lesson, UserProgress, WaitlistEntry, AiInteraction, Feedback
        return {"db": db, "User": User, "Module": Module, "Lesson": Lesson,
                "UserProgress": UserProgress, "WaitlistEntry": WaitlistEntry,
                "AiInteraction": AiInteraction, "Feedback": Feedback}

    return app
