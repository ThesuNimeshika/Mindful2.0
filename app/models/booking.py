from app import db
from datetime import datetime


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'professional_id': self.professional_id,
            'appointment_date': self.appointment_date.isoformat(),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }