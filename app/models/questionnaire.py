from app import db
from datetime import datetime


class Questionnaire(db.Model):
    __tablename__ = "questionnaires"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship("Question", backref="questionnaire", cascade="all, delete-orphan")


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaires.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)

    answers = db.relationship("AnswerOption", backref="question", cascade="all, delete-orphan")


class AnswerOption(db.Model):
    __tablename__ = "answer_options"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # numeric weight


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaires.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    mood = db.Column(db.String(50), nullable=False)  # e.g. "Calm", "Stressed"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship("UserResponse", backref="submission", cascade="all, delete-orphan")


class UserResponse(db.Model):
    __tablename__ = "user_responses"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer_options.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
