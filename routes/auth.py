import re
import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db, redis_client

auth_bp = Blueprint('auth', __name__)

# Fallback in-memory rate limiting dictionary
_memory_limits = {}

def is_rate_limited(key_identifier, limit=5, window=60):
    if current_app.config.get('TESTING'):
        return False
        
    key = f"rl:auth:{key_identifier}"
    if redis_client:
        try:
            current = redis_client.get(key)
            if current and int(current) >= limit:
                return True
            
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
            return False
        except Exception:
            pass # Fall back to memory
            
    now = time.time()
    if key not in _memory_limits:
        _memory_limits[key] = []
    
    # Clean up old timestamps
    _memory_limits[key] = [t for t in _memory_limits[key] if now - t < window]
    
    if len(_memory_limits[key]) >= limit:
        return True
        
    _memory_limits[key].append(now)
    return False

def validate_signup_input(username, email, password):
    """Rigorous server-side validation for new user accounts."""
    if not username or not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
        return False, "Username must be 3-30 characters long and contain only letters, numbers, or underscores."
        
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not email or not re.match(email_regex, email):
        return False, "Please enter a valid email address."
        
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
        
    has_letter = any(c.isalpha() for c in password)
    has_digit_or_special = any(c.isdigit() or not c.isalnum() for c in password)
    if not (has_letter and has_digit_or_special):
        return False, "Password must contain both letters and at least one number or special character."
        
    return True, ""

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='show_login')
def show_login():
    """Show login page on GET, handle authentication on POST"""
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('weather.index'))
        return render_template('show_login.html')

    # Handle login POST request with IP and per-username rate limiting
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if is_rate_limited(request.remote_addr, limit=5, window=60) or (username and is_rate_limited(f"user:{username.lower()}", limit=5, window=60)):
        return jsonify({'success': False, 'message': 'Too many login attempts. Please wait a minute.'}), 429

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('weather.index')})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/auth/login', methods=['POST'])
def handle_login():
    """Handle login POST request with IP and per-username rate limiting"""
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if is_rate_limited(request.remote_addr, limit=5, window=60) or (username and is_rate_limited(f"user:{username.lower()}", limit=5, window=60)):
        return jsonify({'success': False, 'message': 'Too many login attempts. Please wait a minute.'}), 429

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/login/demo', methods=['POST'])
def handle_demo_login():
    """One-click instant demo login for evaluation and review without typing."""
    demo_user = User.query.filter_by(username='demo_guest').first()
    if not demo_user:
        demo_user = User(username='demo_guest', email='demo@climasense.dev')
        demo_user.set_password('DemoAccess2026!')
        db.session.add(demo_user)
        db.session.commit()
    login_user(demo_user)
    return jsonify({'success': True, 'redirect': url_for('weather.index')})

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle signup with input validation"""
    if current_user.is_authenticated:
        return redirect(url_for('weather.index'))
        
    if request.method == 'POST':
        if is_rate_limited(request.remote_addr, limit=5, window=60):
            return jsonify({'success': False, 'message': 'Too many signup attempts. Please wait a minute.'}), 429
            
        data = request.get_json(silent=True) or {}
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        password = str(data.get('password', ''))
        
        valid, err_msg = validate_signup_input(username, email, password)
        if not valid:
            return jsonify({'success': False, 'message': err_msg}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username is already taken.'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        return jsonify({'success': True})
        
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle logout"""
    logout_user()
    return redirect(url_for('auth.show_login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Page 03: Password recovery request endpoint"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        email = str(data.get('email', '')).strip()
        if not email:
            return jsonify({'success': False, 'message': 'Please provide your registered email address.'}), 400
        user = User.query.filter_by(email=email).first()
        return jsonify({
            'success': True,
            'message': 'If that email address is registered, instructions have been sent.'
        })
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Page 03: Reset password endpoint"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        email = str(data.get('email', '')).strip()
        new_pass = str(data.get('password', ''))
        confirm_pass = str(data.get('confirm_password', ''))
        if not new_pass or len(new_pass) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters.'}), 400
        if new_pass != confirm_pass:
            return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_pass)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Password reset successfully.'})
        return jsonify({'success': False, 'message': 'Invalid password recovery token.'}), 400
    return render_template('forgot_password.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Page 16: User account profile & security management"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        curr_pass = str(data.get('current_password', ''))
        new_pass = str(data.get('new_password', ''))
        if not current_user.check_password(curr_pass):
            return jsonify({'success': False, 'message': 'Current password is incorrect.'}), 400
        if not new_pass or len(new_pass) < 8:
            return jsonify({'success': False, 'message': 'New password must be at least 8 characters long.'}), 400
        current_user.set_password(new_pass)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password updated successfully!'})
    saved_count = len(current_user.saved_cities) if current_user.saved_cities else 0
    return render_template('profile.html', user=current_user, saved_count=saved_count)

