import os
from flask import Flask, request, jsonify, Response
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DBAPIError
from src.models import db, User
from src.auth import token_required
import bcrypt
import re
from datetime import datetime
from src.config import Config, TestConfig

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'testing' or os.getenv('PYTEST_CURRENT_TEST') == 'True':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(Config)

db.init_app(app)

# bootstrap database
with app.app_context():
    db.create_all()

# health check
@app.route('/healthz', methods=['GET'])
def health_check():
    # 400 Bad Request
    if request.args or request.get_data(as_text=True):
        return Response(status=400, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    try:
        # 200 OK
        db.session.execute(text('SELECT 1'))
        return Response(status=200, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    except (OperationalError, DBAPIError) as e:
        # 503 Service Unavailable
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })

@app.errorhandler(405)
def method_not_allowed(e):
    # 405 Method Not Allowed
        return Response(status=405, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Creat user
@app.route('/v1/user', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # no email
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    # no password
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        email=email,
        password=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# get user info
@app.route('/v1/user/self', methods=['GET'])
@token_required
def get_user_info():
    auth = request.authorization
    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'account_created': user.account_created,
        'account_updated': user.account_updated
    }), 200

# update user info
@app.route('/v1/user/self', methods=['PUT'])
@token_required
def update_user():
    data = request.get_json()
    auth = request.authorization

    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # allowed fields
    allowed_updates = {'first_name', 'last_name', 'password'}
    for key in data:
        if key not in allowed_updates:
            return jsonify({'error': f'Field {key} cannot be updated'}), 400

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'password' in data:
        password = data['password']
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password

    # update account_updated time
    user.account_updated = datetime.now()
    db.session.commit()

    return jsonify({}), 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
