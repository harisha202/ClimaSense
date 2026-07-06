from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
import redis
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()

# We will initialize redis later in the app factory or gracefully handle missing redis
redis_client = None

def init_redis(app):
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()
    except Exception:
        # Silently fail and log a friendly info message rather than a scary socket error
        app.logger.info("ℹ️ Redis not detected locally. Falling back to in-memory dictionary cache.")
        redis_client = None
