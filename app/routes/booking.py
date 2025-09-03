from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.booking import Booking
from app.models.user import User
from app.models.availability import Availability
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

# USER ENDPOINTS
# Get all professionals (psychologists)
@booking_bp.route("/professionals", methods=["GET"])
@jwt_required()
def get_professionals():
    professionals = User.query.filter_by(user_type="professional").all()
    return jsonify([p.to_dict() for p in professionals])


# Get available slots for a professional
@booking_bp.route("/availability/<int:professional_id>", methods=["GET"])
@jwt_required()
def get_professional_availability(professional_id):
    slots = Availability.query.filter_by(
        professional_id=professional_id, is_booked=False
    ).all()
    return jsonify([s.to_dict() for s in slots])


# Book a slot
@booking_bp.route("/book", methods=["POST"])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.json

    slot = Availability.query.get_or_404(data["slot_id"])
    if slot.is_booked:
        return jsonify({"error": "Slot already booked"}), 400

    booking = Booking(
        user_id=user_id,
        professional_id=slot.professional_id,
        appointment_date=datetime.combine(slot.date, slot.start_time),
        notes=data.get("notes")
    )
    db.session.add(booking)

    # mark slot as booked
    slot.is_booked = True
    db.session.commit()

    return jsonify(booking.to_dict()), 201


# View my bookings (as user)
@booking_bp.route("/bookings/me", methods=["GET"])
@jwt_required()
def get_my_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in bookings])


# Cancel my booking
@booking_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    # Free up the slot if booking was still active
    if booking.status in ["pending", "confirmed"]:
        slot = Availability.query.filter_by(
            professional_id=booking.professional_id,
            date=booking.appointment_date.date(),
            start_time=booking.appointment_date.time()
        ).first()
        if slot:
            slot.is_booked = False

    booking.status = "cancelled"
    db.session.commit()
    return jsonify(booking.to_dict())


# PROFESSIONAL ENDPOINTS

# View pending booking requests
@booking_bp.route("/bookings/pending", methods=["GET"])
@jwt_required()
def get_pending_bookings():
    professional_id = get_jwt_identity()
    bookings = Booking.query.filter_by(
        professional_id=professional_id, status="pending"
    ).all()
    return jsonify([b.to_dict() for b in bookings])


# Accept booking
@booking_bp.route("/bookings/<int:booking_id>/accept", methods=["PUT"])
@jwt_required()
def accept_booking(booking_id):
    professional_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    if booking.professional_id != professional_id:
        return jsonify({"error": "Unauthorized"}), 403

    if booking.status != "pending":
        return jsonify({"error": "Booking already processed"}), 400

    booking.status = "confirmed"
    db.session.commit()
    return jsonify(booking.to_dict())



# Reject booking
@booking_bp.route("/bookings/<int:booking_id>/reject", methods=["PUT"])
@jwt_required()
def reject_booking(booking_id):
    professional_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)

    if booking.professional_id != professional_id:
        return jsonify({"error": "Unauthorized"}), 403

    if booking.status != "pending":
        return jsonify({"error": "Booking already processed"}), 400

    booking.status = "cancelled"

    # free up the slot again
    slot = Availability.query.filter_by(
        professional_id=booking.professional_id,
        date=booking.appointment_date.date(),
        start_time=booking.appointment_date.time()
    ).first()
    if slot:
        slot.is_booked = False

    db.session.commit()
    return jsonify(booking.to_dict())


# View all my bookings as a professional
@booking_bp.route("/bookings/professional/me", methods=["GET"])
@jwt_required()
def get_professional_bookings():
    professional_id = get_jwt_identity()
    bookings = Booking.query.filter_by(professional_id=professional_id).all()
    return jsonify([b.to_dict() for b in bookings])


# AVAILABILITY MANAGEMENT

# Add availability slot
@booking_bp.route("/availability", methods=["POST"])
@jwt_required()
def add_availability():
    professional_id = get_jwt_identity()
    data = request.json

    availability = Availability(
        professional_id=professional_id,
        date=datetime.fromisoformat(data["date"]).date(),
        start_time=datetime.strptime(data["start_time"], "%H:%M").time(),
        end_time=datetime.strptime(data["end_time"], "%H:%M").time()
    )
    db.session.add(availability)
    db.session.commit()

    return jsonify(availability.to_dict()), 201


# View my available (not booked) slots
@booking_bp.route("/availability/me", methods=["GET"])
@jwt_required()
def get_my_availability():
    professional_id = get_jwt_identity()
    slots = Availability.query.filter_by(
        professional_id=professional_id,
        is_booked=False
    ).all()
    return jsonify([s.to_dict() for s in slots])


# Delete availability slot
@booking_bp.route("/availability/<int:slot_id>", methods=["DELETE"])
@jwt_required()
def delete_availability(slot_id):
    professional_id = get_jwt_identity()
    slot = Availability.query.get_or_404(slot_id)

    if slot.professional_id != professional_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(slot)
    db.session.commit()
    return jsonify({"message": "Slot deleted"})
