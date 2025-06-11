import pytest
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

# def test_add_user_missing_field(client):
#     response = client.post('/user', json={'name': 'Bob', 'age': 25})  # Missing email
#     assert response.status_code == 400 or response.status_code == 500  # Flask might raise 500 without validation

# def test_add_user_invalid_age_type(client):
#     response = client.post('/user', json={'name': 'Bob', 'age': 'twenty', 'email': 'bob@example.com'})
#     assert response.status_code == 400 or response.status_code == 500

# def test_add_duplicate_user_email(client):
#     client.post('/user', json={'name': 'Bob', 'age': 25, 'email': 'bob@example.com'})
#     response = client.post('/user', json={'name': 'Bob2', 'age': 26, 'email': 'bob@example.com'})  # same email
#     assert response.status_code == 400 or response.status_code == 500

def test_content_type_required(client):
    response = client.post('/user', data="not json", content_type='text/plain')
    assert response.status_code in [400, 415]
