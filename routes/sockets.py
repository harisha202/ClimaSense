from flask_socketio import join_room, leave_room, emit
from extensions import socketio
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

from flask_socketio import disconnect

@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        disconnect()
        return False

@socketio.on('join_city')
def on_join_city(data):
    """Client wants to listen to alerts for a specific city"""
    city = data.get('city')
    if city:
        join_room(city)
        logger.info(f"Client joined room: {city}")

@socketio.on('leave_city')
def on_leave_city(data):
    city = data.get('city')
    if city:
        leave_room(city)
        logger.info(f"Client left room: {city}")
