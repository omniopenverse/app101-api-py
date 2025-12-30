import os
import pytest

# Ensure a writable log file path before importing the app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("APP101_LOG_FILE", os.path.join(BASE_DIR, "local", "test-app.log"))

from app import app as flask_app, db
from models import Users

@pytest.fixture
def client():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with flask_app.test_client() as client:
        with flask_app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}

def test_get_all_users_empty(client):
    response = client.get('/users')
    assert response.status_code == 201
    assert response.json == {'info': 'No users found'}

def test_add_user(client):
    response = client.post('/user', json={'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
    assert response.status_code == 201
    assert response.json['message'] == 'User added'

def test_get_user_found(client):
    client.post('/user', json={'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
    response = client.get('/user/Alice')
    assert response.status_code == 200
    assert response.json['name'] == 'Alice'

def test_get_user_not_found(client):
    response = client.get('/user/Unknown')
    assert response.status_code == 404
    assert response.json['error'] == 'User not found'

def test_get_all_users_after_insert(client):
    client.post('/user', json={'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]['name'] == 'Alice'

def test_content_type_required(client):
    response = client.post('/user', data="not json", content_type='text/plain')
    assert response.status_code in [400, 415]
