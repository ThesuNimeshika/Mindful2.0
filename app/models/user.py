from app import db
from app.models.booking import Booking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), default='regular')
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    diary_entries = db.relationship('UserDiary', backref='user', lazy=True, cascade='all, delete-orphan')
    user_responses = db.relationship('UserResponse', backref='user', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', foreign_keys='Booking.user_id', backref='client', lazy=True)
    professional_bookings = db.relationship('Booking', foreign_keys='Booking.professional_id', backref='professional', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'email': self.email,
            'user_type': self.user_type,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat()
        }
