from flask import Blueprint
from app.controllers import scanController

bp = Blueprint("scan", __name__)


def register():
    bp.route("/", methods=["GET", "POST"])(
        scanController.index
    )
    bp.route("/delete/<int:scan_id>", methods=["POST"])(
        scanController.delete_scan
    )
    bp.route("/email", methods=["GET", "POST"])(
        scanController.email_analyzer
    )
    return bp
