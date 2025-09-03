from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.questionnaire import Questionnaire, Question, UserResponse, AnswerOption, Submission

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route("/questionnaires/<int:id>", methods=["GET"])
@jwt_required()
def get_questionnaire(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    return jsonify({
        "id": questionnaire.id,
        "title": questionnaire.title,
        "description": questionnaire.description,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "answers": [{"id": a.id, "text": a.text, "value": a.value} for a in q.answers]
            }
            for q in sorted(questionnaire.questions, key=lambda x: x.order)
        ]
    })



@quiz_bp.route("/questionnaires/<int:id>/submit", methods=["POST"])
@jwt_required()
def submit_questionnaire(id):
    user_id = get_jwt_identity()
    questionnaire = Questionnaire.query.get_or_404(id)
    data = request.json.get("answers", [])

    if not data:
        return jsonify({"error": "No responses submitted"}), 400

    # Calculate score
    total_score = 0
    responses = []
    for r in data:
        answer = AnswerOption.query.get(r["answer_id"])
        if not answer:
            return jsonify({"error": f"Invalid answer_id {r['answer_id']}"}), 400
        total_score += answer.value
        responses.append((r["question_id"], answer.id))

    # Simple scoring thresholds (customize per questionnaire)
    if total_score < 5:
        mood = "Calm"
    elif total_score < 10:
        mood = "Stressed"
    else:
        mood = "Highly Stressed"

    submission = Submission(
        user_id=user_id,
        questionnaire_id=id,
        score=total_score,
        mood=mood
    )
    db.session.add(submission)
    db.session.flush()  # get submission.id

    for q_id, a_id in responses:
        db.session.add(UserResponse(submission_id=submission.id, question_id=q_id, answer_id=a_id, user_id=user_id))

    db.session.commit()

    return jsonify({
        "message": "Submission recorded",
        "score": total_score,
        "mood": mood,
        "submission_id": submission.id
    }), 201


@quiz_bp.route("/questionnaires/<int:id>/history", methods=["GET"])
@jwt_required()
def get_history(id):
    user_id = get_jwt_identity()
    submissions = Submission.query.filter_by(user_id=user_id, questionnaire_id=id).order_by(Submission.created_at.asc()).all()

    return jsonify([
        {
            "id": s.id,
            "score": s.score,
            "mood": s.mood,
            "created_at": s.created_at.isoformat()
        }
        for s in submissions
    ])
