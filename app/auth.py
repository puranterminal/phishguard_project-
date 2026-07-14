from functools import wraps
from flask import session, redirect, url_for, flash
from app.repository.user_repo import get_user_by_id


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        user = get_user_by_id(session["user_id"])
        if not user:
            session.clear()
            flash("Account not found. Please login again.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        user = get_user_by_id(session["user_id"])
        if not user or user.role != "admin":    # ← changed user["role"] to user.role
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated