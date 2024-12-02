import os
os.environ['FLASK_ENV'] = 'testing'
os.environ['PYTEST_CURRENT_TEST'] = 'True'
os.environ['AWS_REGION'] = 'us-west-2'

import sys
import pytest
import json
import base64
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from src.models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def mock_sns():
    """Mock AWS SNS client."""
    with patch('boto3.client') as mock_boto_client:
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        yield mock_client

def test_create_user(client):
    """Test user creation and verification email."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    assert b"User created successfully. Please verify your email." in response.data

def test_create_existing_user_not_verified(client):
    """Test re-creating an unverified user."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    client.post('/v1/user', data=json.dumps(payload), content_type='application/json')

    response = client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    assert b"Verification email resent. Please check your email." in response.data

def test_get_user_info_before_verification(client):
    """Test accessing user info before email verification."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    client.post('/v1/user', data=json.dumps(payload), content_type='application/json')

    auth_string = 'test@example.com:password123'
    auth_headers = {
        'Authorization': 'Basic ' + base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    }

    response = client.get('/v1/user/self', headers=auth_headers)
    assert response.status_code == 403
    assert b"User not verified" in response.data

def test_user_verification(client):
    """Test user email verification."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    assert b"User created successfully" in response.data

    with app.app_context():
        user = db.session.query(User).filter_by(email="test@example.com").first()
        assert user is not None, "User was not saved to the database."
        assert user.verification_token is not None, "Verification token was not generated."

    verify_url = f"/v1/user/verify?token={user.verification_token}"
    response = client.get(verify_url)
    assert response.status_code == 200
    assert b"Email successfully verified." in response.data

    auth_string = 'test@example.com:password123'
    auth_headers = {
        'Authorization': 'Basic ' + base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    }
    response = client.get('/v1/user/self', headers=auth_headers)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"


def test_unauthorized_access(client):
    """Test unauthorized access to user info."""
    response = client.get('/v1/user/self')
    assert response.status_code == 401
    assert b"Authentication required!" in response.data
