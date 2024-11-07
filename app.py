import os
import uuid
from flask import Flask, request, jsonify, Response
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DBAPIError
from src.metrics import log_api_call_count, log_api_call_duration
from src.models import db, User, Image
from src.auth import token_required
import bcrypt
import re
from datetime import datetime
from src.config import Config, TestConfig
import time
import boto3
import logging

logging.basicConfig(
    filename='/var/log/webapp.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'testing' or os.getenv('PYTEST_CURRENT_TEST') == 'True':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(Config)

db.init_app(app)

initialized = False

# bootstrap database
def initialize_database():
    global initialized
    if not initialized:
        with app.app_context():
            try:
                db.create_all()
                initialized = True
            except (OperationalError, DBAPIError):
                initialized = False

initialize_database()

@app.teardown_appcontext
def shutdown_session(exception=None):
    try:
        db.session.remove()
    except OperationalError:
        pass

@app.before_request
def before_request():
    if not check_db_connection():
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })

def check_db_connection():
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except (OperationalError, DBAPIError):
        return False

# health check
@app.route('/healthz', methods=['GET'])
def health_check():
    start_time = time.time()
    # 503 Service Unavailable
    if not check_db_connection():
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    # 400 Bad Request
    if request.args or request.get_data(as_text=True):
        return Response(status=400, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    try:
        # 200 OK
        db.session.execute(text('SELECT 1'))
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("HealthCheck", time_elapsed)
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

# Create user
@app.route('/v1/user', methods=['POST'])
def create_user():
    log_api_call_count("CreateUser")
    start_time = time.time()
    if not check_db_connection():
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    if not initialized:
        initialize_database()

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
        id=str(uuid.uuid4()),
        email=email,
        password=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    db.session.add(new_user)

    db_start_time = time.time()
    db.session.commit()
    db_time_elapsed = (time.time() - db_start_time) * 1000
    log_api_call_duration("CreateUserDB", db_time_elapsed)

    time_elapsed = (time.time() - start_time) * 1000
    log_api_call_duration("CreateUser", time_elapsed)
    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201


# get user info
@app.route('/v1/user/self', methods=['GET'])
@token_required
def get_user_info():
    log_api_call_count("GetUserInfo")
    start_time = time.time()
    if not check_db_connection():
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    if not initialized:
        initialize_database()

    auth = request.authorization
    db_start_time = time.time()
    user = User.query.filter_by(email=auth.username).first()
    db_time_elapsed = (time.time() - db_start_time) * 1000
    log_api_call_duration("GetUserInfoDB", db_time_elapsed)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    time_elapsed = (time.time() - start_time) * 1000
    log_api_call_duration("GetUserInfo", time_elapsed)
    return jsonify({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'account_created': user.account_created,
        'account_updated': user.account_updated,
        'user_id': user.id
    }), 200


# update user info
@app.route('/v1/user/self', methods=['PUT'])
@token_required
def update_user():
    log_api_call_count("UpdateUser")
    start_time = time.time()
    if not check_db_connection():
        return Response(status=503, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        })
    if not initialized:
        initialize_database()

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

    # Update fields
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

    # Update account_updated time
    user.account_updated = datetime.now()
    db_start_time = time.time()
    db.session.commit()
    db_time_elapsed = (time.time() - db_start_time) * 1000
    log_api_call_duration("UpdateUserDB", db_time_elapsed)

    time_elapsed = (time.time() - start_time) * 1000
    log_api_call_duration("UpdateUser", time_elapsed)
    return jsonify({}), 204


s3_client = boto3.client("s3", region_name="us-west-2")

def upload_file_to_s3(file, bucket_name, object_name):
    start_time = time.time()
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("S3Upload", time_elapsed)
        return True
    except Exception as e:
        print(e)
        return False
    
def delete_file_from_s3(bucket_name, object_name):
    start_time = time.time()
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("S3Delete", time_elapsed)
        return True
    except Exception as e:
        print(e)
        return False
    
@app.route('/v1/user/self/pic', methods=['POST'])
@token_required
def upload_profile_pic():
    log_api_call_count("UploadProfilePic")
    start_time = time.time()
    auth = request.authorization
    user = User.query.filter_by(email=auth.username).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'profilePic' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['profilePic']
    file_name = f"{user.id}/{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    bucket_name = app.config['S3_BUCKET_NAME']

    existing_image = Image.query.filter_by(user_id=user.id).first()
    if existing_image:
        if not delete_file_from_s3(bucket_name, existing_image.url.split('/')[-1]):
            return jsonify({'error': 'Failed to delete existing profile picture'}), 500
        db.session.delete(existing_image)

    if upload_file_to_s3(file, bucket_name, file_name):
        new_image = Image(
            file_name=file.filename,
            url=f"{bucket_name}/{file_name}",
            user_id=user.id,
            upload_date=datetime.now()
        )
        db.session.add(new_image)
        
        db_start_time = time.time()
        db.session.commit()
        db_time_elapsed = (time.time() - db_start_time) * 1000
        log_api_call_duration("UploadProfilePicDB", db_time_elapsed)
        
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("UploadProfilePic", time_elapsed)

        return jsonify({
            "file_name": new_image.file_name,
            "id": new_image.id,
            "url": new_image.url,
            "upload_date": new_image.upload_date.strftime("%Y-%m-%d"),
            "user_id": new_image.user_id
        }), 201
    else:
        return jsonify({'error': 'File upload failed'}), 500
    
@app.route('/v1/user/self/pic', methods=['GET'])
@token_required
def get_profile_pic():
    log_api_call_count("GetProfilePic")
    start_time = time.time()
    auth = request.authorization
    user = User.query.filter_by(email=auth.username).first()
    
    if not user:
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("GetProfilePic", time_elapsed)
        return jsonify({'error': 'User not found'}), 404

    image = Image.query.filter_by(user_id=user.id).first()
    if not image:
        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("GetProfilePic", time_elapsed)
        return jsonify({'error': 'Profile picture not found'}), 404

    time_elapsed = (time.time() - start_time) * 1000
    log_api_call_duration("GetProfilePic", time_elapsed)
    return jsonify({
        "file_name": image.file_name,
        "id": image.id,
        "url": image.url,
        "upload_date": image.upload_date.strftime("%Y-%m-%d"),
        "user_id": image.user_id
    }), 200

@app.route('/v1/user/self/pic', methods=['DELETE'])
@token_required
def delete_profile_pic():
    log_api_call_count("DeleteProfilePic")
    start_time = time.time()
    auth = request.authorization
    user = User.query.filter_by(email=auth.username).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    image = Image.query.filter_by(user_id=user.id).first()
    if not image:
        return jsonify({'error': 'Profile picture not found'}), 404

    bucket_name = app.config['S3_BUCKET_NAME']
    if delete_file_from_s3(bucket_name, image.url.split('/')[-1]):
        db.session.delete(image)
        
        db_start_time = time.time()
        db.session.commit()
        db_time_elapsed = (time.time() - db_start_time) * 1000
        log_api_call_duration("DeleteProfilePicDB", db_time_elapsed)

        time_elapsed = (time.time() - start_time) * 1000
        log_api_call_duration("DeleteProfilePic", time_elapsed)

        return Response(status=204)
    else:
        return jsonify({'error': 'File deletion failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
