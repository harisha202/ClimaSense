from flask import Blueprint, jsonify, current_app
from extensions import db, get_redis_client
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
@health_bp.route('/api/health')
def health_check():
    """
    Standardized operational health check for Docker, load balancers, and monitoring.
    Returns HTTP 200 if critical backend dependencies are operational.
    """
    status = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'version': '2.0.0',
        'checks': {}
    }
    healthy = True

    # 1. Database check
    try:
        db.session.execute(db.text('SELECT 1'))
        status['checks']['database'] = {'status': 'up', 'type': 'SQLAlchemy'}
    except Exception as e:
        status['checks']['database'] = {'status': 'down', 'error': str(e)}
        healthy = False

    # 2. Redis / Cache check
    client = get_redis_client()
    if client:
        try:
            client.ping()
            status['checks']['cache'] = {'status': 'up', 'provider': 'Redis'}
        except Exception as e:
            status['checks']['cache'] = {'status': 'degraded', 'error': 'Redis unreachable; using in-memory fallback'}
    else:
        status['checks']['cache'] = {'status': 'up', 'provider': 'InMemoryCache (Fallback)'}

    # 3. Weather API Configuration
    ow_key = bool(current_app.config.get('OPENWEATHER_API_KEY'))
    status['checks']['openweather_api'] = {'configured': ow_key}

    # 4. Unsplash API Configuration
    un_key = bool(current_app.config.get('UNSPLASH_API_KEY'))
    status['checks']['unsplash_api'] = {'configured': un_key}

    # 5. AI Service Configuration
    ai_key = bool(current_app.config.get('AI_API_KEY'))
    status['checks']['ai_service'] = {
        'configured': ai_key,
        'model': current_app.config.get('AI_MODEL', 'gemini-2.0-flash')
    }

    http_status = 200 if healthy else 503
    status['status'] = 'healthy' if healthy else 'unhealthy'
    return jsonify(status), http_status
