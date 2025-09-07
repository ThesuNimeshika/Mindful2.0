from app import db
from datetime import datetime


class Community(db.Model):
    __tablename__ = 'communities'

    community_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # stress, depression, cancer, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship('CommunityMember', backref='community', lazy=True, cascade="all, delete-orphan")
    posts = db.relationship('CommunityPost', backref='community', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'community_id': self.community_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat()
        }


class CommunityMember(db.Model):
    __tablename__ = 'community_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.community_id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.community_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), default='text')  # text, image, link
    status = db.Column(db.String(20), default='pending')  # admin approval
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    author = db.relationship('User', foreign_keys=[user_id], backref='community_posts')

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "community_id": self.community_id,
            "content": self.content,
            "post_type": self.post_type,
            "status": self.status,
            "created_at": self.created_at.date().isoformat() if self.created_at else None,
            "author": {
                "user_id": self.author.user_id,
                "username": self.author.user_name
            } if self.author else None
        }