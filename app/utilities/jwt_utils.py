# /utilities/jwt_utils.py
from datetime import datetime, timedelta
import jwt
from flask import current_app

def encode_jwt(payload):
    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def decode_jwt(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
