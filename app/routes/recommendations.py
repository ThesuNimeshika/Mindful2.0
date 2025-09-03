from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.article import Article
from app.models.diary import UserDiary
import numpy as np

recommendations_bp = Blueprint("recommendations_bp", __name__)

@recommendations_bp.route("/recommendations/home", methods=["GET"])
@jwt_required()
def recommend_home():
    user_id = get_jwt_identity()

    # Fetch all diary entries of the user that have embeddings
    diaries = UserDiary.query.filter(
        UserDiary.user_id == user_id,
        UserDiary.embedding.isnot(None)
    ).all()

    if not diaries:
        return jsonify({"message": "No diary entries found for this user", "recommendations": []}), 200

    # Aggregate diary embeddings: we can take the mean vector for simplicity
    diary_embeddings = np.array([d.get_embedding() for d in diaries])
    user_vector = np.mean(diary_embeddings, axis=0)  # shape = (embedding_dim,)

    # Fetch all articles with embeddings
    articles = Article.query.filter(Article.embedding.isnot(None)).all()
    if not articles:
        return jsonify({"message": "No articles found", "recommendations": []}), 200

    results = []
    for article in articles:
        article_emb = article.get_embedding()
        score = float(np.dot(user_vector, article_emb))  # cosine similarity
        results.append({
            "article_id": article.article_id,
            "title": article.title,
            "tags": article.tags,
            "similarity_score": round(score, 4)
        })

    # Rank top K articles
    top_k = 5
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]

    return jsonify({"recommendations": results}), 200
