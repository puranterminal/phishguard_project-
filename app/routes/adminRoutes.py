from flask import Blueprint
from app.controllers import adminController
from app.auth import admin_required

bp = Blueprint("admin", __name__)


def register():
    bp.route("/", methods=["GET"])(
        admin_required(adminController.dashboard)
    )
    bp.route("/reports/<int:rid>/resolve", methods=["POST"])(
        admin_required(adminController.resolve_report)
    )
    return bp
