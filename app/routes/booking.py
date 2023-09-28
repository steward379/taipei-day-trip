# /routes/booking.py
from flask import Blueprint, request, jsonify
from utilities.jwt_utils import decode_jwt

booking_bp = Blueprint('booking', __name__)

@booking_bp.before_request
def require_login():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": True, "message": "請先登入"}), 401

    try:
        decode_jwt(token)
    except:
        return jsonify({"error": True, "message": "無效的 token"}), 401

@booking_bp.route('/api/booking', methods=['GET'])
def get_booking():
    # Implement your logic here
    return jsonify({"message": "GET booking"})

@booking_bp.route('/api/booking', methods=['POST'])
def create_booking():
    # Implement your logic here
    return jsonify({"message": "POST booking"})

@booking_bp.route('/api/booking', methods=['DELETE'])
def delete_booking():
    # Implement your logic here
    return jsonify({"message": "DELETE booking"})
