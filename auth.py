from functools import wraps
from flask import request, jsonify
from models import User
import bcrypt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify({'message': 'Authentication required!'}), 401
        user = User.query.filter_by(email=auth.username).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        if not bcrypt.checkpw(auth.password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(email, password):
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return True
    return False
