from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from sentence_transformers import SentenceTransformer

from app.config import Config

load_dotenv()

db = SQLAlchemy()

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

jwt = JWTManager()
migrate = Migrate()


def create_app():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.diary import diary_bp
    from app.routes.community import community_bp
    from app.routes.questionnaire import quiz_bp
    from app.routes.admin import admin_bp
    # from app.routes.mood import mood_bp
    # from app.routes.ml import ml_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.booking import booking_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(diary_bp, url_prefix='/api/diary')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # app.register_blueprint(mood_bp, url_prefix='/api/mood')
    # app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(booking_bp, url_prefix='/api/booking')

    for rule in app.url_map.iter_rules():
        print(rule)

    return app