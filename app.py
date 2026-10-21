import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, redirect, url_for, render_template
from config import config_dict
from extensions import db, login_manager, mail, init_redis, socketio
from routes import register_blueprints
from models import User, SavedCity, SearchHistory, WeatherLog, ForecastSnapshot

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    env_config = os.getenv('FLASK_ENV', config_name)
    cfg_class = config_dict.get(env_config, config_dict['default'])
    app.config.from_object(cfg_class)
    if hasattr(cfg_class, 'init_app'):
        cfg_class.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.show_login'
    login_manager.login_message = "Please log in to access this page."
    mail.init_app(app)
    init_redis(app)
    from extensions import redis_client

    # Socket.IO Origin restriction
    allowed_origins = "*" if app.config.get('DEBUG') else os.getenv('ALLOWED_ORIGINS', '*')
    socketio.init_app(app, cors_allowed_origins=allowed_origins, message_queue=app.config.get('REDIS_URL') if redis_client else None)
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify, redirect, url_for
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return redirect(url_for('auth.show_login'))
        
    # Service Worker root endpoints for full PWA caching scope
    @app.route('/sw.js')
    def service_worker():
        response = app.send_static_file('sw.js')
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Service-Worker-Allowed'] = '/'
        return response

    
    # Register blueprints
    register_blueprints(app)
    
    # Import socket handlers
    import routes.sockets
        
    # Create tables
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=app.config['DEBUG'])
