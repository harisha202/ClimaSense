import pytest
from app import create_app
from extensions import db
from models.user import User

@pytest.fixture
def app():
    # Use testing config
    app = create_app('development')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "REDIS_URL": "redis://localhost:6379/1" # different db for testing, or we mock
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(app, client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    
    client.post('/login', json={'username': 'testuser', 'password': 'password123'})
    return client
