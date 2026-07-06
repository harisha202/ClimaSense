import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, redirect, url_for
from config import config_dict
from extensions import db, login_manager, mail, init_redis, socketio
from routes import register_blueprints
from models.user import User

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    env_config = os.getenv('FLASK_ENV', config_name)
    app.config.from_object(config_dict.get(env_config, config_dict['default']))
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.show_login'
    login_manager.login_message = "Please log in to access this page."
    mail.init_app(app)
    init_redis(app)
    from extensions import redis_client
    socketio.init_app(app, cors_allowed_origins="*", message_queue=app.config.get('REDIS_URL') if redis_client else None)
    
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