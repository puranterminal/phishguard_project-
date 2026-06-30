from flask import Blueprint
from app.controllers import quizController
from app.auth import login_required, admin_required

bp = Blueprint("quiz", __name__)


def register():
    bp.route("/", methods=["GET"])(
        login_required(quizController.index)
    )
    bp.route("/submit", methods=["POST"])(
        login_required(quizController.submit)
    )
    bp.route("/admin", methods=["GET"])(
        admin_required(quizController.admin_index)
    )
    bp.route("/admin/new", methods=["GET", "POST"])(
        admin_required(quizController.admin_new)
    )
    bp.route("/admin/<int:qid>/edit", methods=["GET", "POST"])(
        admin_required(quizController.admin_edit)
    )
    bp.route("/admin/<int:qid>/delete", methods=["POST"])(
        admin_required(quizController.admin_delete)
    )
    return bp
