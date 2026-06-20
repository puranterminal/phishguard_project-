from flask import Blueprint
from app.controllers import authController
from app.auth import login_required, admin_required

bp = Blueprint("auth", __name__)


def register():
    bp.route("/login", methods=["GET", "POST"])(
        authController.login
    )
    bp.route("/register", methods=["GET", "POST"])(
        authController.register
    )
    bp.route("/logout", methods=["GET", "POST"])(
        authController.logout
    )
    bp.route("/dashboard", methods=["GET", "POST"])(
        admin_required(authController.dashboard)
    )
    bp.route("/profile", methods=["GET", "POST"])(
        login_required(authController.profile)
    )
    bp.route("/edit/<int:id>", methods=["GET", "POST"])(
        admin_required(authController.editUsers)
    )
    bp.route("/delete/<int:id>", methods=["GET", "POST"])(
        admin_required(authController.deleteUser)
    )
    return bp
