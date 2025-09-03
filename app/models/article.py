from app import db
from datetime import datetime
import pickle
import numpy as np

class Article(db.Model):
    __tablename__ = 'articles'

    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.community_id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    status = db.Column(db.String(20), default="pending")
    tags = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # SBERT embeddings
    embedding = db.Column(db.LargeBinary)

    # Relationships
    author = db.relationship('User', backref='articles')
    community = db.relationship('Community', backref='articles_list')

    def set_embedding(self, vector: np.ndarray):
        self.embedding = pickle.dumps(vector)

    def get_embedding(self) -> np.ndarray:
        return pickle.loads(self.embedding) if self.embedding else None

    def to_dict(self):
        return {
            "article_id": self.article_id,
            "title": self.title,
            "content": self.content,
            "community_id": self.community_id,
            "community_name": self.community.name if self.community else None,
            "author_id": self.author_id,
            "author_name": self.author.user_name if self.author else None,
            "status": self.status,
            "tags": self.tags.split(",") if self.tags else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }