import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_forms import LoginForm, SignupForm
from app.services.auth_service import AuthService
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

_login_attempts = defaultdict(list)
_RATE_LIMIT = 10
_RATE_WINDOW = 300


def _check_rate_limit(ip):
    now = time.time()
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < _RATE_WINDOW]
    if len(_login_attempts[ip]) >= _RATE_LIMIT:
        return False
    _login_attempts[ip].append(now)
    return True


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.shell")) if current_user.is_admin else redirect(url_for("workspace.shell"))
    if request.method == "POST" and not _check_rate_limit(request.remote_addr or "unknown"):
        flash("Too many login attempts. Try again in 5 minutes.", "error")
        return render_template("auth/login.html", form=LoginForm())
    form = LoginForm()
    if form.validate_on_submit():
        user, error = AuthService.authenticate(form.email.data, form.password.data)
        if error:
            flash(error, "error")
        else:
            login_user(user)
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            next_url = request.args.get("next")
            if next_url:
                parsed = urlparse(next_url)
                if not parsed.scheme and not parsed.netloc:
                    return redirect(next_url)
            return redirect(url_for("admin.shell")) if user.is_admin else redirect(url_for("workspace.shell"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("admin.shell")) if current_user.is_admin else redirect(url_for("workspace.shell"))
    if request.method == "POST" and not _check_rate_limit(request.remote_addr or "unknown"):
        flash("Too many signup attempts. Try again in 5 minutes.", "error")
        return render_template("auth/signup.html", form=SignupForm())
    form = SignupForm()
    if form.validate_on_submit():
        user, error = AuthService.create_user(form.email.data, form.password.data)
        if error:
            flash(error, "error")
        else:
            login_user(user)
            return redirect(url_for("admin.shell")) if user.is_admin else redirect(url_for("workspace.shell"))
    return render_template("auth/signup.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.landing"))
