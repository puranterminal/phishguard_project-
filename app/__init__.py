import os
from flask import Flask, render_template, session, request, abort, g
import config
from app.database import create_tables
from app.repository.user_repo import get_user_by_id


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    with app.app_context():
        create_tables()

    @app.before_request
    def load_current_user():
        g.current_user = None
        if session.get("user_id"):
            g.current_user = get_user_by_id(session["user_id"])

    @app.context_processor
    def inject_current_user():
        return {"current_user": g.get("current_user")}

    @app.before_request
    def generate_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = os.urandom(16).hex()

    from app.routes import (
        authRoutes, lessonRoutes, quizRoutes,
        scanRoutes, reportRoutes, adminRoutes, mainRoutes
    )
    app.register_blueprint(mainRoutes.register())
    app.register_blueprint(authRoutes.register(),   url_prefix="/auth")
    app.register_blueprint(lessonRoutes.register(), url_prefix="/lessons")
    app.register_blueprint(quizRoutes.register(),   url_prefix="/quiz")
    app.register_blueprint(scanRoutes.register(),   url_prefix="/scan")
    app.register_blueprint(reportRoutes.register(), url_prefix="/report")
    app.register_blueprint(adminRoutes.register(),  url_prefix="/admin")

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    return app
