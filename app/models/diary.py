from app import db
from datetime import datetime
import pickle
import numpy as np

class UserDiary(db.Model):
    __tablename__ = 'user_diary'

    diary_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood_rating = db.Column(db.Integer)
    tags = db.Column(db.String(255))
    sentiment_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # New column for SBERT embeddings
    embedding = db.Column(db.LargeBinary)

    def set_embedding(self, vector: np.ndarray):
        self.embedding = pickle.dumps(vector)

    def get_embedding(self) -> np.ndarray:
        return pickle.loads(self.embedding) if self.embedding else None

    def to_dict(self):
        return {
            'diary_id': self.diary_id,
            'user_id': self.user_id,
            'content': self.content,
            'mood_rating': self.mood_rating,
            'tags': self.tags.split(',') if self.tags else [],
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }