from flask import Blueprint
from app.controllers import mainController

bp = Blueprint("main", __name__)


def register():
    bp.route("/", methods=["GET"])(
        mainController.home
    )
    return bp
