from flask import Blueprint
from app.controllers import reportController

bp = Blueprint("report", __name__)


def register():
    bp.route("/", methods=["GET", "POST"])(
        reportController.index
    )
    return bp
