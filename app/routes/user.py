from flask import Blueprint, request, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
from datetime import datetime, timedelta
from app.utilities.jwt_utils import encode_jwt, decode_jwt
from app import app, db
from app.models import User

user_bp = Blueprint('user', __name__)

# 現有的路由，僅添加了 user_bp
@user_bp.route("/api/user", methods=["POST"])
def register():
    try:
        data = request.json
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"error": True, "message": "Email 已被使用"}), 400

        existing_name = User.query.filter_by(name=data['name']).first()
        if existing_name:
            return jsonify({"error": True, "message": "名稱已被使用"}), 400

        hashed_password = generate_password_hash(data["password"], method="scrypt")
        new_user = User(name=data['name'], email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

@app.route("/api/user/auth", methods=["PUT"])
def login():
    try:
        data = request.json
        user = User.query.filter_by(email=data['email']).first()

        if not user or not check_password_hash(user.password, data["password"]):
            return jsonify({"error": True, "message": "帳密錯誤"}), 404

        payload = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7),
        }
        token = encode_jwt(payload)

        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

@app.route("/api/user/auth", methods=["GET"])
def get_user():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"data": None}), 200

    try:
        data = decode_jwt(token)
        return jsonify({
            "data": {
                "id": data["id"],
                "name": data["name"],
                "email": data["email"]
            }
        }), 200
    except Exception as e:
        return jsonify({"data": None}), 200