from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.community import *
from app.models.article import Article
from app.models.user import User
from app import db, sbert_model
import numpy as np
import random

community_bp = Blueprint('community', __name__)


@community_bp.route("/communities", methods=["GET"])
@jwt_required(optional=True)  # allow browsing without login
def get_communities():
    communities = Community.query.all()
    return jsonify([c.to_dict() for c in communities]), 200


@community_bp.route("/random", methods=["GET"])
def get_random_communities():
    communities = Community.query.order_by(db.func.random()).limit(3).all()
    return jsonify([c.to_dict() for c in communities]), 200


@community_bp.route("/communities/<int:community_id>/join", methods=["POST"])
@jwt_required()
def join_community(community_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if community exists
    community = Community.query.get(community_id)
    if not community:
        return jsonify({"error": "Community not found"}), 404

    # Already joined?
    existing = CommunityMember.query.filter_by(
        user_id=user.user_id, community_id=community_id
    ).first()
    if existing:
        return jsonify({"message": "Already a member"}), 200

    membership = CommunityMember(user_id=user.user_id, community_id=community_id)
    db.session.add(membership)
    db.session.commit()

    return jsonify({"message": f"Joined community {community.name}"}), 201


@community_bp.route("/communities/<int:community_id>/leave", methods=["DELETE"])
@jwt_required()
def leave_community(community_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    membership = CommunityMember.query.filter_by(
        user_id=user.user_id, community_id=community_id
    ).first()

    if not membership:
        return jsonify({"error": "Not a member of this community"}), 400

    db.session.delete(membership)
    db.session.commit()

    return jsonify({"message": "Left the community"}), 200


@community_bp.route("/communities/<int:community_id>/posts", methods=["GET"])
def get_community_posts(community_id):
    posts = CommunityPost.query.filter_by(community_id=community_id, status="approved").all()
    result = []
    for p in posts:
        result.append({
            "post_id": p.post_id,
            "content": p.content,
            "post_type": p.post_type,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "author": p.author.user_name
        })
    return jsonify(result), 200


@community_bp.route("/communities/<int:community_id>/posts", methods=["POST"])
@jwt_required()
def add_post(community_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.json
    content = data.get("content")
    post_type = data.get("post_type", "text")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    new_post = CommunityPost(
        user_id=user.user_id,
        community_id=community_id,
        content=content,
        post_type=post_type,
        status="pending"
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post submitted for review"}), 201


@community_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    post = CommunityPost.query.get_or_404(post_id)

    if post.author.user_name != user.user_name:
        return jsonify({"error": "You are not authorized to delete this post"}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"}), 200


@community_bp.route("/communities/<int:community_id>/articles", methods=["POST"])
@jwt_required()
def add_article(community_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    title = data.get("title")
    content = data.get("content")
    tags = data.get("tags")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    # Create article
    new_article = Article(
        title=title,
        content=content,
        community_id=community_id,
        author_id=user.user_id,
        status="pending",
        tags=tags
    )

    # Encode and save embedding
    article_text = f"{title} {content} {tags or ''}"
    vector = sbert_model.encode(article_text, convert_to_numpy=True, normalize_embeddings=True)
    new_article.set_embedding(vector)

    db.session.add(new_article)
    db.session.commit()

    return jsonify({
        "message": "Article submitted for review",
        "article": new_article.to_dict()
    }), 201


@community_bp.route("/communities/<int:community_id>/articles", methods=["GET"])
def get_community_articles(community_id):
    articles = Article.query.filter_by(community_id=community_id, status="approved").all()
    result = []
    for a in articles:
        result.append({
            "article_id": a.article_id,
            "title": a.title,
            "content": a.content,
            "tags": a.tags,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
            "author": a.author.user_name
        })
    return jsonify(result), 200


@community_bp.route("/articles/<int:article_id>", methods=["GET"])
@jwt_required()
def get_article(article_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    article = Article.query.get_or_404(article_id)

    return jsonify(article.to_dict()), 200

@community_bp.route("/articles/random", methods=["GET"])
def get_random_article():
    try:
        # Fetch only approved articles
        articles = Article.query.filter_by(status="approved").all()

        if not articles:
            return jsonify({"message": "No approved articles found"}), 404

        # Pick a random one
        article = random.choice(articles)

        result = {
            "article_id": article.article_id,
            "title": article.title,
            "content": article.content,
            "tags": article.tags,
            "status": article.status,
            "created_at": article.created_at.isoformat(),
            "author": article.author.user_name if article.author else None,
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@community_bp.route("/articles/feed", methods=["GET"])
@jwt_required()
def get_feed_articles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    memberships = CommunityMember.query.filter_by(user_id=user.user_id).all()
    community_ids = [m.community_id for m in memberships]

    articles = Article.query.filter(Article.community_id.in_(community_ids)).all()

    return jsonify([a.to_dict() for a in articles]), 200


@community_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
def delete_article(article_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    article = Article.query.get_or_404(article_id)

    if article.author.user_name != user.user_name:
        return jsonify({"error": "You are not authorized to delete this article"}), 403

    db.session.delete(article)
    db.session.commit()
    return jsonify({"message": "Article deleted"}), 200