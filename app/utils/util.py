from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import jose
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'a super secret, secret key'

def token_required(f):  # checks token on protected routes
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        print("🔍 Incoming Headers:", dict(request.headers))

        if not auth_header or not auth_header.startswith("Bearer "):
            print("🚫 Missing or malformed Authorization header")
            return jsonify({'message': 'Token is missing!'}), 401

        token = auth_header.split(" ")[1]
        print("🔑 Extracted Token:", token)

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print("🧠 Decoded Token Payload:", data)
            kwargs['token_customer_id'] = data['sub']
        except ExpiredSignatureError:
            print("⏰ Token expired")
            return jsonify({'message': 'Token has expired!'}), 401
        except JWTError as e:
            print("❌ Token decode error:", str(e))
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated

def encode_token(customer_id):  # creates the toke when a user logs in
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # setting the expiration time set to an hour past now
        'iat': datetime.now(timezone.utc),  # issued at time
        'sub': str(customer_id)  # subject of the token
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token