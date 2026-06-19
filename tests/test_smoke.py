"""Smoke tests — verify the app factory, config, blueprints, and models load."""

import pytest
from app import create_app
from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_creates(app):
    assert app is not None
    assert app.name == "app"


def test_config_defaults():
    assert hasattr(Config, "SECRET_KEY")
    assert hasattr(Config, "SQLALCHEMY_DATABASE_URI")


def test_development_config():
    assert DevelopmentConfig.DEBUG is True


def test_production_config():
    assert ProductionConfig.DEBUG is False


def test_testing_config():
    assert TestingConfig.TESTING is True


def test_blueprints_registered(app):
    for name in ("public", "auth", "api", "workspace", "admin"):
        assert name in app.blueprints, f"Blueprint '{name}' not registered"


def test_models_import():
    from app.models import User, Session, Module, Lesson, UserProgress, BotEvent, WaitlistEntry, AiInteraction
    assert all([User, Session, Module, Lesson, UserProgress, BotEvent, WaitlistEntry, AiInteraction])


def test_services_import():
    from app.services.auth_service import AuthService
    from app.services.curriculum import CurriculumService
    from app.services.signal_explainer import SignalExplainerService
    from app.services.ai_service import AiService
    assert all([AuthService, CurriculumService, SignalExplainerService, AiService])


def test_routes_import():
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.workspace import workspace_bp
    from app.routes.admin import admin_bp
    assert all([public_bp, auth_bp, api_bp, workspace_bp, admin_bp])


def test_login_page_loads(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200


def test_signup_page_loads(client):
    resp = client.get("/auth/signup")
    assert resp.status_code == 200


def test_landing_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_pricing_page_loads(client):
    resp = client.get("/pricing")
    assert resp.status_code == 200


def test_404_returns_not_found(client):
    resp = client.get("/nonexistent-route")
    assert resp.status_code == 404


def test_workspace_redirects_when_not_logged_in(client):
    resp = client.get("/workspace/")
    assert resp.status_code == 302


def test_api_redirects_when_not_logged_in(client):
    resp = client.get("/api/summary")
    assert resp.status_code == 302


def test_user_model_creation(app):
    with app.app_context():
        from app.models.user import User
        from datetime import datetime, timezone
        u = User(email="test@example.com", tier="core")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        assert u.id is not None
        assert u.check_password("password123") is True
        assert u.is_pro is False
        assert u.is_admin is False
        assert u.tier == "core"
        db.session.rollback()


def test_sweep_modules_import():
    from sweep_config import UNIVERSE, PAPER, MIN_RR, STOP_ATR_MULT, LOOP_INTERVAL_SEC
    assert len(UNIVERSE) > 0
    assert PAPER is True
    assert MIN_RR >= 1.0
    assert STOP_ATR_MULT > 0
    assert LOOP_INTERVAL_SEC > 0


def test_bot_logger_import():
    import bot_logger
    assert bot_logger is not None
