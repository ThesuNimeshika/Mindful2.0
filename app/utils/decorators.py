from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from functools import wraps
from flask import jsonify

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404
        if user.user_type != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return fn(*args, **kwargs)
    return wrapper