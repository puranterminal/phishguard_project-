from flask import Blueprint
from app.controllers import lessonController
from app.auth import login_required, admin_required

bp = Blueprint("lessons", __name__)


def register():
    bp.route("/", methods=["GET"])(
        lessonController.index
    )
    bp.route("/<int:lesson_id>", methods=["GET"])(
        lessonController.detail
    )
    bp.route("/<int:lesson_id>/vote", methods=["POST"])(
        login_required(lessonController.vote)
    )
    bp.route("/<int:lesson_id>/comment", methods=["POST"])(
        login_required(lessonController.add_comment)
    )
    bp.route("/comment/<int:comment_id>/delete", methods=["POST"])(
        login_required(lessonController.delete_comment)
    )
    bp.route("/admin", methods=["GET"])(
        admin_required(lessonController.admin_index)
    )
    bp.route("/admin/new", methods=["GET", "POST"])(
        admin_required(lessonController.admin_new)
    )
    bp.route("/admin/<int:lesson_id>/edit", methods=["GET", "POST"])(
        admin_required(lessonController.admin_edit)
    )
    bp.route("/admin/<int:lesson_id>/delete", methods=["POST"])(
        admin_required(lessonController.admin_delete)
    )
    return bp