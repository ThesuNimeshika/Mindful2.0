from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validation
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            user_name=data['user_name'],
            email=data['email'],
            user_type=data.get('user_type', 'regular')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.user_id))

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=str(user.user_id))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            })

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update fields
        if 'user_name' in data:
            user.user_name = data['user_name']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Request upgrade to professional (user → professional)
@auth_bp.route('/upgrade', methods=['PUT'])
@jwt_required()
def upgrade_to_professional():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.user_type == "professional":
            return jsonify({'error': 'Already a professional'}), 400

        # Mark as pending professional (admin approval needed)
        user.user_type = "pending_professional"
        db.session.commit()

        return jsonify({
            'message': 'Upgrade request submitted. Awaiting admin approval.',
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500