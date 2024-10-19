from functools import wraps
from flask import request, jsonify
from src.models import User
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
        user_password = user.password
        if(type(user_password) == str):
            user_password = user_password.encode('utf-8')
        if not bcrypt.checkpw(auth.password.encode('utf-8'), user_password):
            return jsonify({'message': 'Invalid credentials'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(email, password):
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return True
    return False
