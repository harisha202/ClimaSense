from celery import Celery
from flask import current_app
from extensions import db
from models.user import User
from services.digest_service import build_digest_for_user, send_digest_email
from services.openweather_service import get_current_weather
from models.saved_city import SavedCity

celery = Celery(__name__)

@celery.task
def send_daily_digests():
    """Loops through all users with saved cities, emails each one."""
    users = User.query.all()
    for user in users:
        if user.saved_cities:
            digest = build_digest_for_user(user)
            if digest:
                send_digest_email(user, digest)
    return True

@celery.task
def warm_cache():
    """Pre-fetches weather for popular/saved cities."""
    # Getting distinct saved cities
    cities = db.session.query(SavedCity.city).distinct().all()
    for (city,) in cities:
        # get_current_weather already stores in cache via openweather_service
        get_current_weather(city)
    return True

@celery.task
def check_live_alerts():
    """Checks for active alerts for all distinct saved cities and pushes to WebSockets"""
    # For a real project we need to push within app context
    from app import create_app
    app = create_app()
    with app.app_context():
        from extensions import socketio, db
        from models.saved_city import SavedCity
        from services.openweather_service import get_current_weather, get_alerts
        
        cities = db.session.query(SavedCity.city).distinct().all()
        for (city,) in cities:
            weather = get_current_weather(city)
            if weather and 'coord' in weather:
                lat = weather['coord']['lat']
                lon = weather['coord']['lon']
                
                alerts_data = get_alerts(lat, lon)
                
                if alerts_data and 'alerts' in alerts_data and len(alerts_data['alerts']) > 0:
                    alert = alerts_data['alerts'][0]
                    alert_payload = {
                        'title': alert.get('event', 'Severe Weather Alert'),
                        'description': alert.get('description', ''),
                        'city': city
                    }
                    socketio.emit('weather_alert', alert_payload, room=city)
        return True

from celery.schedules import crontab

celery.conf.beat_schedule = {
    'warm-cache-every-6-hours': {
        'task': 'tasks.celery_tasks.warm_cache',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'check-alerts-every-minute': {
        'task': 'tasks.celery_tasks.check_live_alerts',
        'schedule': crontab(minute='*'),
    },
}
