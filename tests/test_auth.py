def test_signup(client, app):
    response = client.post('/signup', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    
    from models.user import User
    with app.app_context():
        u = User.query.filter_by(username='newuser').first()
        assert u is not None

def test_login(client, app):
    # create user
    with app.app_context():
        from models.user import User
        from extensions import db
        user = User(username='test', email='test@test.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        
    response = client.post('/login', json={'username': 'test', 'password': 'pass'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True

def test_login_invalid(client):
    response = client.post('/login', json={'username': 'wrong', 'password': 'pass'})
    assert response.status_code == 401
    
def test_protected_route(client):
    response = client.get('/index')
    assert response.status_code == 302 # redirect to login
