from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.questionnaire import Questionnaire, Question, AnswerOption
from app.models.user import User
from app.models.community import Community, CommunityPost
from app.models.article import Article
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Communities
@admin_bp.route("/communities", methods=["GET"])
@jwt_required()
@admin_required
def get_communities():
    communities = Community.query.all()
    return jsonify([c.to_dict() for c in communities]), 200


@admin_bp.route("/communities", methods=["POST"])
@jwt_required()
@admin_required
def add_community():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")
    category = data.get("category", "general")

    if not name:
        return jsonify({"error": "Community name required"}), 400

    community = Community(name=name, description=description, category=category)
    db.session.add(community)
    db.session.commit()

    return jsonify({"message": "Community created", "community": community.to_dict()}), 201


@admin_bp.route("/communities/<int:community_id>", methods=["PATCH"])
@jwt_required()
@admin_required
def edit_community(community_id):
    community = Community.query.get_or_404(community_id)
    data = request.get_json()

    community.name = data.get("name", community.name)
    community.description = data.get("description", community.description)
    community.category = data.get("category", community.category)

    db.session.commit()
    return jsonify({"message": "Community updated", "community": community.to_dict()}), 200


@admin_bp.route("/communities/<int:community_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_community(community_id):
    community = Community.query.get_or_404(community_id)
    db.session.delete(community)
    db.session.commit()
    return jsonify({"message": "Community deleted"}), 200


# Articles
@admin_bp.route("/articles", methods=["GET"])
@jwt_required()
@admin_required
def list_articles():
    status = request.args.get("status", "approved")  # default to "approved"
    query = Article.query.filter_by(status=status)
    articles = query.all()
    return jsonify([a.to_dict() for a in articles]), 200


@admin_bp.route("/articles/<int:article_id>", methods=["GET"])
@jwt_required()
@admin_required
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    return jsonify(article.to_dict()), 200


@admin_bp.route("/articles/<int:article_id>/approve", methods=["PATCH"])
@jwt_required()
@admin_required
def approve_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.status = "approved"
    db.session.commit()
    return jsonify({"message": "Article approved"}), 200


@admin_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({"message": "Article deleted"}), 200


# Posts
@admin_bp.route("/posts", methods=["GET"])
@jwt_required()
@admin_required
def list_posts():
    status = request.args.get("status", "approved")  # default to "approved"
    query = CommunityPost.query.filter_by(status=status)
    posts = query.all()
    return jsonify([p.to_dict() for p in posts]), 200


@admin_bp.route("/posts/<int:post_id>", methods=["GET"])
@jwt_required()
@admin_required
def view_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    return jsonify(post.to_dict()), 200


@admin_bp.route("/posts/<int:post_id>/approve", methods=["PATCH"])
@jwt_required()
@admin_required
def approve_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    post.status = "approved"
    db.session.commit()
    return jsonify({"message": "Post approved"}), 200


@admin_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"}), 200


# Users
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route("/users/search", methods=["GET"])
@jwt_required()
@admin_required
def search_users():
    q = request.args.get("q", "")
    users = User.query.filter(
        (User.user_name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
    ).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route("/users/<int:user_id>/type", methods=["PATCH"])
@jwt_required()
@admin_required
def update_user_type(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    new_type = data.get("user_type")

    if not new_type:
        return jsonify({"error": "Missing user_type"}), 400

    # validate allowed types
    allowed_types = ["admin", "regular", "professional"]
    if new_type not in allowed_types:
        return jsonify({"error": f"Invalid user_type. Allowed: {allowed_types}"}), 400

    user.user_type = new_type
    db.session.commit()

    return jsonify({"message": f"user_type updated to '{new_type}'"}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


#Questionnaires
# Get all questionnaires
@admin_bp.route("/questionnaires", methods=["GET"])
@jwt_required()
@admin_required
def get_questionnaires():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.user_type != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    questionnaires = Questionnaire.query.all()
    result = []
    for q in questionnaires:
        result.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "questions": [
                {
                    "id": ques.id,
                    "text": ques.text,
                    "order": ques.order,
                    "answers": [
                        {"id": a.id, "text": a.text, "value": a.value}
                        for a in ques.answers
                    ],
                }
                for ques in q.questions
            ],
        })

    return jsonify(result), 200


# Get single questionnaire
@admin_bp.route("/questionnaires/<int:id>", methods=["GET"])
@jwt_required()
@admin_required
def get_questionnaire(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.user_type != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    q = Questionnaire.query.get_or_404(id)
    result = {
        "id": q.id,
        "title": q.title,
        "description": q.description,
        "questions": [
            {
                "id": ques.id,
                "text": ques.text,
                "order": ques.order,
                "answers": [
                    {"id": a.id, "text": a.text, "value": a.value}
                    for a in ques.answers
                ],
            }
            for ques in q.questions
        ],
    }

    return jsonify(result), 200


@admin_bp.route("/questionnaires", methods=["POST"])
@jwt_required()
@admin_required
def create_questionnaire():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Ensure only admins can do this
    if not user or user.user_type != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    title = data.get("title")
    description = data.get("description")
    questions_data = data.get("questions", [])

    if not title or not questions_data:
        return jsonify({"error": "Title and questions are required"}), 400

    questionnaire = Questionnaire(title=title, description=description)
    db.session.add(questionnaire)
    db.session.flush()  # get questionnaire.id

    # Create questions & answers
    for idx, q in enumerate(questions_data, start=1):
        question = Question(
            questionnaire_id=questionnaire.id,
            text=q["text"],
            order=idx
        )
        db.session.add(question)
        db.session.flush()

        for ans in q.get("answers", []):
            db.session.add(AnswerOption(
                question_id=question.id,
                text=ans["text"],
                value=ans["value"]
            ))

    db.session.commit()

    return jsonify({"message": "Questionnaire created", "id": questionnaire.id}), 201


@admin_bp.route("/questionnaires/<int:id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_questionnaire(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.user_type != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    questionnaire = Questionnaire.query.get_or_404(id)
    data = request.json

    questionnaire.title = data.get("title", questionnaire.title)
    questionnaire.description = data.get("description", questionnaire.description)


    if "questions" in data:
        # delete old ones
        Question.query.filter_by(questionnaire_id=questionnaire.id).delete()
        db.session.flush()

        for idx, q in enumerate(data["questions"], start=1):
            question = Question(
                questionnaire_id=questionnaire.id,
                text=q["text"],
                order=idx
            )
            db.session.add(question)
            db.session.flush()

            for ans in q.get("answers", []):
                db.session.add(AnswerOption(
                    question_id=question.id,
                    text=ans["text"],
                    value=ans["value"]
                ))

    db.session.commit()
    return jsonify({"message": "Questionnaire updated"})


@admin_bp.route("/questionnaires/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_questionnaire(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.user_type != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    questionnaire = Questionnaire.query.get_or_404(id)
    db.session.delete(questionnaire)
    db.session.commit()

    return jsonify({"message": "Questionnaire deleted"})


#user type update
# List all professionals
@admin_bp.route('/professionals', methods=['GET'])
@jwt_required()
@admin_required
def list_professionals():
    professionals = User.query.filter(User.user_type == "professional").all()
    return jsonify([p.to_dict() for p in professionals])


# List all pending upgrade requests
@admin_bp.route('/professionals/pending', methods=['GET'])
@jwt_required()
@admin_required
def list_pending_professionals():
    pending = User.query.filter(User.user_type == "pending_professional").all()
    return jsonify([p.to_dict() for p in pending])


# Approve professional request
@admin_bp.route('/professionals/<int:user_id>/approve', methods=['PUT'])
@jwt_required()
@admin_required
def approve_professional(user_id):
    user = User.query.get_or_404(user_id)

    if user.user_type != "pending_professional":
        return jsonify({"error": "User is not pending approval"}), 400

    user.user_type = "professional"
    db.session.commit()

    return jsonify({"message": "Professional approved", "user": user.to_dict()})


# Reject professional request
@admin_bp.route('/professionals/<int:user_id>/reject', methods=['PUT'])
@jwt_required()
@admin_required
def reject_professional(user_id):
    user = User.query.get_or_404(user_id)

    if user.user_type != "pending_professional":
        return jsonify({"error": "User is not pending approval"}), 400

    user.user_type = "regular"
    db.session.commit()

    return jsonify({"message": "Professional request rejected", "user": user.to_dict()})


# Delete a professional
@admin_bp.route('/professionals/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_professional(user_id):
    user = User.query.get_or_404(user_id)

    if user.user_type != "professional":
        return jsonify({"error": "User is not a professional"}), 400

    user.user_type = "regular"
    db.session.commit()

    return jsonify({"message": "Professional deleted"})