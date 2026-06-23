from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def tier_required(tier: str):
    """
    Route decorator that restricts access to users of a given tier.
    Usage: @tier_required('pro')
    Redirects Core users to the upgrade page with a flash message.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if tier == 'pro' and not current_user.is_pro and not current_user.is_admin:
                flash("This feature is available on the Pro plan.", "upgrade")
                return redirect(url_for('public.pricing'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
