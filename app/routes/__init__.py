def register_blueprints(app):
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.workspace import workspace_bp
    from app.routes.admin import admin_bp
    from app.routes.onboarding import onboarding_bp
    from app.routes.module import module_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(workspace_bp, url_prefix="/workspace")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(module_bp)
