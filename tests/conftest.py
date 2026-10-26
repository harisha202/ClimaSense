import pytest
import os
import warnings

# Suppress eventlet / dnspython resolver query deprecation
try:
    import dns.resolver
    def _silent_query(self, qname, rdtype=dns.rdatatype.A, rdclass=dns.rdataclass.IN,
                      tcp=False, source=None, raise_on_no_answer=True,
                      source_port=0, lifetime=None):
        return self.resolve(
            qname, rdtype, rdclass, tcp, source, raise_on_no_answer,
            source_port, lifetime, True
        )
    dns.resolver.Resolver.query = _silent_query
except Exception:
    pass

from app import create_app
from extensions import db as _db
from models.user import User

@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application instance."""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    app = create_app('testing')
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Provides a clean database session for each test function."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()
        # Clean up tables between test runs
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture(scope='function')
def test_user(app, db_session):
    """Creates a default verified user for authenticated route tests."""
    user = User(username='testmeteorologist', email='test@climasense.local')
    user.set_password('CorrectHorseBattery99!')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    """A test client pre-authenticated with test_user."""
    client.post('/login', json={
        'username': 'testmeteorologist',
        'password': 'CorrectHorseBattery99!'
    })
    return client
