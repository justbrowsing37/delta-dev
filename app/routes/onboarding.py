from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_required, current_user
from app.extensions import db
from app.services.onboarding_service import get_quiz_questions, score_quiz

onboarding_bp = Blueprint("onboarding", __name__)


@onboarding_bp.route("/onboarding")
@login_required
def index():
    if current_user.onboarding_complete:
        return redirect(url_for("workspace.shell"))
    return redirect(url_for("onboarding.quiz"))


@onboarding_bp.route("/onboarding/quiz", methods=["GET"])
@login_required
def quiz():
    if current_user.onboarding_complete:
        return redirect(url_for("workspace.shell"))
    questions = get_quiz_questions()
    return render_template("onboarding/quiz.html", questions=questions)


@onboarding_bp.route("/onboarding/quiz", methods=["POST"])
@login_required
def quiz_submit():
    answers = {}
    for key, value in request.form.items():
        if key.startswith("q"):
            question_id = key[1:]
            answers[question_id] = int(value)

    result = score_quiz(answers)
    session["onboarding_result"] = result
    return redirect(url_for("onboarding.result"))


@onboarding_bp.route("/onboarding/result")
@login_required
def result():
    if current_user.onboarding_complete:
        return redirect(url_for("workspace.shell"))
    result = session.get("onboarding_result")
    if not result:
        return redirect(url_for("onboarding.quiz"))
    return render_template("onboarding/result.html", result=result)


@onboarding_bp.route("/onboarding/complete", methods=["POST"])
@login_required
def complete():
    result = session.get("onboarding_result")
    if result:
        current_user.skill_level = result["skill_level"]
    current_user.onboarding_complete = True
    db.session.commit()
    session.pop("onboarding_result", None)
    return redirect(url_for("workspace.shell"))
