import pytest
from models.user import User

def test_signup_successful(client, db_session):
    """Verify signup flow creates user and redirects to login."""
    res = client.post('/signup', json={
        'username': 'new_climate_user',
        'email': 'newuser@climasense.local',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    
    user = User.query.filter_by(username='new_climate_user').first()
    assert user is not None
    assert user.email == 'newuser@climasense.local'

def test_signup_password_mismatch(client):
    """Verify signup rejects mismatched passwords."""
    res = client.post('/signup', json={
        'username': 'mismatch_user',
        'email': 'mismatch@climasense.local',
        'password': 'StrongPassword123!',
        'confirm_password': 'DifferentPassword123!'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert "Passwords do not match" in data['message']

def test_signup_duplicate_case_insensitive(client, test_user):
    """Verify duplicate username or email is rejected case-insensitively."""
    # Test duplicate username in uppercase
    res = client.post('/signup', json={
        'username': test_user.username.upper(),
        'email': 'different_email@climasense.local',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    })
    assert res.status_code == 400
    assert "already taken" in res.get_json()['message']

    # Test duplicate email in uppercase
    res2 = client.post('/signup', json={
        'username': 'unique_user_name',
        'email': test_user.email.upper(),
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    })
    assert res2.status_code == 400
    assert "already registered" in res2.get_json()['message']

def test_login_and_logout_flow(client, test_user):
    """Verify login and logout session state."""
    # Test /login endpoint
    res = client.post('/login', json={
        'username': test_user.username,
        'password': 'CorrectHorseBattery99!'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Test /auth/login endpoint (consolidated logic)
    res2 = client.post('/auth/login', json={
        'username': test_user.username,
        'password': 'CorrectHorseBattery99!'
    })
    assert res2.status_code == 200
    assert res2.get_json()['success'] is True

    # Test invalid password
    res3 = client.post('/login', json={
        'username': test_user.username,
        'password': 'IncorrectPassword!'
    })
    assert res3.status_code == 401
    assert res3.get_json()['success'] is False

    # Test logout
    res_logout = client.get('/logout', follow_redirects=False)
    assert res_logout.status_code == 302

def test_profile_password_update(auth_client, test_user):
    """Verify authenticated profile password update with verification."""
    res = auth_client.post('/profile', json={
        'current_password': 'CorrectHorseBattery99!',
        'new_password': 'BrandNewPassword2026!',
        'confirm_new_password': 'BrandNewPassword2026!'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    
    # Verify new password works
    assert test_user.check_password('BrandNewPassword2026!') is True

def test_profile_wrong_current_password(auth_client):
    """Verify profile rejects incorrect current password."""
    res = auth_client.post('/profile', json={
        'current_password': 'WrongPassword123!',
        'new_password': 'BrandNewPassword2026!',
        'confirm_new_password': 'BrandNewPassword2026!'
    })
    assert res.status_code == 400
    assert "Current password is incorrect" in res.get_json()['message']
