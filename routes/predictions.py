from flask import Blueprint, jsonify, render_template, current_app
from flask_login import login_required
from services.openweather_service import get_current_weather, get_forecast
from services.ai_service import _call_gemini_api
from models.weather_log import WeatherLog
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
import json

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
        return jsonify({'success': False, 'message': f"City '{city_name}' not found or weather service unavailable."}), 404
        
    current_temp = weather['main']['temp']
    current_humidity = weather['main']['humidity']
    current_desc = weather['weather'][0]['description'] if weather.get('weather') else 'N/A'
    
    # 1. Fetch real OpenWeather forecast for tomorrow (midday)
    forecast_data = get_forecast(city_name)
    tomorrow_forecast_temp = None
    tomorrow_forecast_desc = "Forecast projection"
    if forecast_data and 'list' in forecast_data:
        # Find item closest to 24 hours ahead
        now_ts = datetime.utcnow().timestamp()
        target_ts = now_ts + 86400
        best_item = min(forecast_data['list'], key=lambda x: abs(x['dt'] - target_ts))
        tomorrow_forecast_temp = best_item['main']['temp']
        tomorrow_forecast_desc = best_item['weather'][0]['description']
        
    # 2. Query historical WeatherLog records for this city over past 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    stats = db.session.query(
        func.count(WeatherLog.id).label('log_count'),
        func.avg(WeatherLog.temperature).label('avg_temp'),
        func.avg(WeatherLog.humidity).label('avg_hum')
    ).filter(
        WeatherLog.city.ilike(city_name),
        WeatherLog.recorded_at >= seven_days_ago
    ).first()
    
    has_history = stats and stats.log_count and stats.log_count > 0 and stats.avg_temp is not None
    avg_hist_temp = round(stats.avg_temp, 1) if has_history else None
    avg_hist_hum = round(stats.avg_hum, 1) if has_history else None
    log_count = stats.log_count if stats else 0
    
    # Projected tomorrow value (uses OpenWeather forecast if available, else historical trend)
    if tomorrow_forecast_temp is not None:
        proj_temp = round(tomorrow_forecast_temp, 1)
        proj_desc = tomorrow_forecast_desc
    elif has_history:
        proj_temp = round((current_temp + avg_hist_temp) / 2, 1)
        proj_desc = "Derived from historical moving average"
    else:
        proj_temp = current_temp
        proj_desc = current_desc
        
    # 3. Generate honest trend analysis (Gemini or grounded fallback)
    api_key = current_app.config.get('AI_API_KEY')
    insight_text = ""
    is_ai = False
    
    if api_key:
        prompt = f"""You are a meteorological data analyst for ClimaSense.
Provide a clear, honest 2-3 sentence analysis comparing historical observations with provider forecasts for {city_name}.
IMPORTANT HONESTY RULES:
- Do NOT claim to be a physical atmospheric forecasting model.
- Clearly distinguish between observed database history and OpenWeather forecasts.
- If historical data count is low, explicitly mention that tracking is preliminary.

DATA CONTEXT:
- City: {city_name}
- Current Weather: {current_temp}°C, {current_desc}, Humidity: {current_humidity}%
- 7-Day Database History: {log_count} observations recorded. Observed Average Temp: {avg_hist_temp}°C, Avg Humidity: {avg_hist_hum}%
- OpenWeather Tomorrow Forecast: {tomorrow_forecast_temp}°C, {tomorrow_forecast_desc}
"""
        res_text, success = _call_gemini_api(prompt, max_tokens=250)
        if success:
            insight_text = res_text
            is_ai = True

    if not insight_text:
        # Grounded rule-based explanation
        if has_history:
            diff = round(current_temp - avg_hist_temp, 1)
            diff_str = f"{abs(diff)}°C warmer" if diff > 0 else f"{abs(diff)}°C cooler" if diff < 0 else "consistent with"
            insight_text = (
                f"Historical Analysis: Across {log_count} logged records over the last 7 days, {city_name} averaged {avg_hist_temp}°C. "
                f"Current conditions ({current_temp}°C) are {diff_str} recent observations. "
                f"OpenWeather projects {proj_temp}°C tomorrow with {proj_desc}."
            )
        else:
            insight_text = (
                f"Current observations indicate {current_temp}°C with {current_desc}. "
                f"Logged historical records for {city_name} are currently accumulating. "
                f"OpenWeather provider forecast projects {proj_temp}°C tomorrow."
            )

    payload = {
        'today': {
            'temp': current_temp,
            'humidity': current_humidity,
            'description': current_desc
        },
        'tomorrow': {
            'temp': proj_temp,
            'humidity': avg_hist_hum if avg_hist_hum else current_humidity,
            'description': proj_desc,
            'source': 'OpenWeather 24h Projection' if tomorrow_forecast_temp is not None else 'Historical Moving Average'
        },
        'history_summary': {
            'has_history': has_history,
            'observations_count': log_count,
            'seven_day_avg_temp': avg_hist_temp,
            'seven_day_avg_humidity': avg_hist_hum
        },
        'ai_insight': insight_text,
        'is_ai_generated': is_ai,
        'provider': 'Google Gemini' if is_ai else 'Grounded Analytical Engine'
    }
    
    return jsonify({
        'success': True,
        'city': city_name,
        'prediction': payload
    })
