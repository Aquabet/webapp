import os
os.environ['FLASK_ENV'] = 'testing'
os.environ['PYTEST_CURRENT_TEST'] = 'True'

import sys
import pytest
import json
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

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

def test_create_user(client):
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    assert b"User created successfully" in response.data

def test_duplicate_user(client):
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    response = client.post('/v1/user', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    assert b"User already exists" in response.data

def test_get_user_info(client):
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
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['email'] == "test@example.com"
    assert data['first_name'] == "Test"
    assert data['last_name'] == "User"

def test_unauthorized_access(client):
    response = client.get('/v1/user/self')
    assert response.status_code == 401
    assert b"Authentication required!" in response.data
