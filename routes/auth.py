from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db, redis_client
import time

auth_bp = Blueprint('auth', __name__)

# Fallback in-memory rate limiting dictionary
_memory_limits = {}

def is_rate_limited(ip, limit=5, window=60):
    key = f"rl:auth:{ip}"
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

@auth_bp.route('/')
def show_login():
    """Show login page"""
    if current_user.is_authenticated:
        return redirect(url_for('weather.index'))
    return render_template('show_login.html')

@auth_bp.route('/login', methods=['POST'])
def handle_login():
    """Handle login POST request"""
    if is_rate_limited(request.remote_addr, limit=5, window=60):
        return jsonify({'success': False, 'message': 'Too many login attempts. Please wait a minute.'}), 429
        
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle signup"""
    if current_user.is_authenticated:
        return redirect(url_for('weather.index'))
        
    if request.method == 'POST':
        if is_rate_limited(request.remote_addr, limit=5, window=60):
            return jsonify({'success': False, 'message': 'Too many signup attempts. Please wait a minute.'}), 429
            
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True})
        
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle logout"""
    logout_user()
    return redirect(url_for('auth.show_login'))
