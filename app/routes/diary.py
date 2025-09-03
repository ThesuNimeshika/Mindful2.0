from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, sbert_model
from app.models.diary import UserDiary
from app.models.article import Article
from app.ml.nlp_recommender import NLPRecommender
from datetime import datetime

diary_bp = Blueprint('diary', __name__)


@diary_bp.route('/create_entry', methods=['POST'])
@jwt_required()
def create_entry():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        entry = UserDiary(
            user_id=user_id,
            content=data['content'],
            mood_rating=data.get('mood_rating'),
            tags=','.join(data.get('tags', []))
        )

        # Encode diary content
        vector = sbert_model.encode(entry.content, convert_to_numpy=True, normalize_embeddings=True)
        entry.set_embedding(vector)

        db.session.add(entry)
        db.session.commit()

        return jsonify({
            'message': 'Diary entry created successfully',
            'entry': entry.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@diary_bp.route('/entries', methods=['GET'])
@jwt_required()
def get_entries():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        entries = UserDiary.query.filter_by(user_id=user_id) \
            .order_by(UserDiary.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'entries': [entry.to_dict() for entry in entries.items],
            'total': entries.total,
            'pages': entries.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@diary_bp.route('/update_entry/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    try:
        user_id = get_jwt_identity()
        entry = UserDiary.query.filter_by(diary_id=entry_id, user_id=user_id).first()

        if not entry:
            return jsonify({'error': 'Entry not found'}), 404

        data = request.get_json()
        entry.content = data.get('content', entry.content)
        entry.mood_rating = data.get('mood_rating', entry.mood_rating)
        entry.tags = ','.join(data.get('tags', entry.tags.split(',') if entry.tags else []))
        entry.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Entry updated successfully',
            'entry': entry.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@diary_bp.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    try:
        user_id = get_jwt_identity()
        entry = UserDiary.query.filter_by(diary_id=entry_id, user_id=user_id).first()

        if not entry:
            return jsonify({'error': 'Entry not found'}), 404

        db.session.delete(entry)
        db.session.commit()

        return jsonify({'message': 'Entry deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500