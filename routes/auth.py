import re
import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from models.user import User
from extensions import db, get_redis_client

auth_bp = Blueprint('auth', __name__)

# Fallback in-memory rate limiting dictionary
_memory_limits = {}

def is_rate_limited(key_identifier, limit=5, window=60):
    if current_app.config.get('TESTING'):
        return False
        
    key = f"rl:auth:{key_identifier}"
    client = get_redis_client()
    if client:
        try:
            current = client.get(key)
            if current and int(current) >= limit:
                return True
            
            pipe = client.pipeline()
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

def validate_signup_input(username, email, password, confirm_password=None):
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
        
    if confirm_password is not None and password != confirm_password:
        return False, "Passwords do not match."

    return True, ""

def process_login():
    """Consolidated authentication logic for both /login and /auth/login endpoints."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if not username or not password:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please enter both your username and password.'}), 400
        return render_template('show_login.html', error='Please enter both your username and password.'), 400

    if is_rate_limited(request.remote_addr, limit=5, window=60) or (username and is_rate_limited(f"user:{username.lower()}", limit=5, window=60)):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Too many login attempts. Please wait a minute.'}), 429
        return render_template('show_login.html', error='Too many login attempts. Please wait a minute.'), 429

    user = User.query.filter(func.lower(User.username) == username.lower()).first()
    
    if user and user.check_password(password):
        login_user(user)
        next_url = request.args.get('next')
        if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
            next_url = url_for('weather.home')
        if request.is_json:
            return jsonify({'success': True, 'redirect': next_url})
        return redirect(next_url)
    else:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        return render_template('show_login.html', error='Invalid username or password'), 401

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='show_login')
def show_login():
    """Show login page on GET, handle authentication on POST"""
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('weather.home'))
        return render_template('show_login.html')
    return process_login()

@auth_bp.route('/auth/login', methods=['POST'])
def handle_login():
    """Handle login POST request with IP and per-username rate limiting"""
    return process_login()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle signup with input validation, password confirmation, and case-insensitive uniqueness"""
    if current_user.is_authenticated:
        return redirect(url_for('weather.home'))
        
    if request.method == 'POST':
        if is_rate_limited(request.remote_addr, limit=5, window=60):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Too many signup attempts. Please wait a minute.'}), 429
            return render_template('signup.html', error='Too many signup attempts. Please wait a minute.'), 429
            
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict() or {}
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        password = str(data.get('password', ''))
        confirm_password = str(data.get('confirm_password') or data.get('password_confirm') or '')
        
        valid, err_msg = validate_signup_input(username, email, password, confirm_password=confirm_password)
        if not valid:
            if request.is_json:
                return jsonify({'success': False, 'message': err_msg}), 400
            return render_template('signup.html', error=err_msg), 400
        
        if User.query.filter(func.lower(User.username) == username.lower()).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username is already taken.'}), 400
            return render_template('signup.html', error='Username is already taken.'), 400
        if User.query.filter(func.lower(User.email) == email.lower()).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
            return render_template('signup.html', error='Email address is already registered.'), 400
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('auth.show_login'), 'message': 'Account created successfully! Please sign in.'})
        return redirect(url_for('auth.show_login'))
        
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle logout"""
    logout_user()
    return redirect(url_for('auth.show_login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User account profile & security management"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        curr_pass = str(data.get('current_password', ''))
        new_pass = str(data.get('new_password', ''))
        confirm_pass = str(data.get('confirm_new_password') or data.get('confirm_password') or '')
        
        if not current_user.check_password(curr_pass):
            return jsonify({'success': False, 'message': 'Current password is incorrect.'}), 400
        if not new_pass or len(new_pass) < 8:
            return jsonify({'success': False, 'message': 'New password must be at least 8 characters long.'}), 400
        has_letter = any(c.isalpha() for c in new_pass)
        has_digit_or_special = any(c.isdigit() or not c.isalnum() for c in new_pass)
        if not (has_letter and has_digit_or_special):
            return jsonify({'success': False, 'message': 'New password must contain both letters and at least one number or special character.'}), 400
        if confirm_pass and new_pass != confirm_pass:
            return jsonify({'success': False, 'message': 'New passwords do not match.'}), 400
            
        current_user.set_password(new_pass)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password updated successfully!'})
    saved_count = len(current_user.saved_cities) if current_user.saved_cities else 0
    return render_template('profile.html', user=current_user, saved_count=saved_count)
