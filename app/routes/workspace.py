import logging
from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required, current_user

from app.services.curriculum import CurriculumService

log = logging.getLogger(__name__)
workspace_bp = Blueprint("workspace", __name__)


@workspace_bp.route("/")
@login_required
def shell():
    try:
        modules = CurriculumService.get_published_modules(user_id=current_user.id)
        progress = CurriculumService.get_progress(current_user.id)
    except Exception as e:
        log.error("Workspace shell data failed: %s", e)
        modules, progress = [], {"completed": 0, "total": 0, "percentage": 0}
    return render_template(
        "workspace/shell.html",
        modules=modules,
        progress=progress,
    )


@workspace_bp.route("/api/modules")
@login_required
def api_modules():
    try:
        modules = CurriculumService.get_published_modules(user_id=current_user.id)
        return jsonify({"modules": modules})
    except Exception as e:
        log.error("Failed to fetch modules: %s", e)
        return jsonify({"modules": []})


@workspace_bp.route("/api/modules/<slug>")
@login_required
def api_module_detail(slug):
    try:
        module = CurriculumService.get_module_by_slug(slug, user_id=current_user.id)
        if not module:
            abort(404)
        return jsonify(module)
    except Exception as e:
        log.error("Failed to fetch module %s: %s", slug, e)
        abort(500)


@workspace_bp.route("/api/lessons/<module_slug>/<lesson_slug>")
@login_required
def api_lesson_detail(module_slug, lesson_slug):
    try:
        lesson = CurriculumService.get_lesson(module_slug, lesson_slug, user_id=current_user.id)
        if not lesson:
            abort(404)
        return jsonify(lesson)
    except Exception as e:
        log.error("Failed to fetch lesson %s/%s: %s", module_slug, lesson_slug, e)
        abort(500)


@workspace_bp.route("/api/lessons/<module_slug>/<lesson_slug>/complete", methods=["POST"])
@login_required
def api_mark_complete(module_slug, lesson_slug):
    try:
        lesson = CurriculumService.get_lesson(module_slug, lesson_slug)
        if not lesson:
            return jsonify({"ok": False, "error": "Lesson not found"}), 404
        CurriculumService.mark_complete(user_id=current_user.id, lesson_id=lesson["id"])
        return jsonify({"ok": True})
    except Exception as e:
        log.error("Failed to mark lesson complete %s/%s: %s", module_slug, lesson_slug, e)
        return jsonify({"ok": False, "error": "Internal error"}), 500
