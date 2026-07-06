from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from services.openweather_service import get_current_weather

from models.weather_log import WeatherLog
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/predictions')
@login_required
def predictions():
    return render_template('predictions.html')

@predictions_bp.route('/api/predictions/<city_name>', methods=['GET'])
@login_required
def get_prediction(city_name):
    weather = get_current_weather(city_name)
    if not weather:
        return jsonify({'success': False, 'message': 'City not found'}), 404
        
    current_temp = weather['main']['temp']
    current_humidity = weather['main']['humidity']
    
    # Historical Trend Prediction (AI Replacement)
    # Fetch average temp and humidity from last 7 days for this city
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    stats = db.session.query(
        func.avg(WeatherLog.temperature).label('avg_temp'),
        func.avg(WeatherLog.humidity).label('avg_hum')
    ).filter(
        WeatherLog.city.ilike(city_name),
        WeatherLog.recorded_at >= seven_days_ago
    ).first()
    
    if stats and stats.avg_temp is not None:
        # Use historical averages to adjust tomorrow's prediction slightly
        predicted_temp = round((current_temp + stats.avg_temp) / 2, 1)
        predicted_hum = round((current_humidity + stats.avg_hum) / 2)
        insight = f"Based on historical trends over the last 7 days, {city_name} is tracking towards {predicted_temp}°C."
    else:
        # Fallback if no history exists yet
        predicted_temp = current_temp
        predicted_hum = current_humidity
        insight = f"Insufficient historical data for {city_name}. Tracking has started, check back tomorrow for trend predictions."
        
    ai_prediction = {
        'today': {
            'temp': current_temp,
            'humidity': current_humidity,
            'description': weather['weather'][0]['description']
        },
        'tomorrow': {
            'temp': predicted_temp, 
            'humidity': predicted_hum,
            'description': 'forecast based on trends'
        },
        'ai_insight': insight
    }
    
    return jsonify({'success': True, 'prediction': ai_prediction, 'city': city_name})
