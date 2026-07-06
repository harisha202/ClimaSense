from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from models.weather_log import WeatherLog
from datetime import datetime, timedelta

trends_bp = Blueprint('trends', __name__)

@trends_bp.route('/trends')
@login_required
def trends():
    return render_template('trends.html')

@trends_bp.route('/api/trends/<city>')
@login_required
def api_trends(city):
    range_str = request.args.get('range', '7d')
    days = 7
    if range_str == '30d':
        days = 30
        
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    logs = WeatherLog.query.filter(WeatherLog.city == city, WeatherLog.recorded_at >= cutoff).order_by(WeatherLog.recorded_at.asc()).all()
    
    return jsonify({
        'success': True,
        'city': city,
        'range': range_str,
        'data': [log.to_dict() for log in logs]
    })
