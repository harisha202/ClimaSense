from flask import Blueprint, jsonify
from flask_login import login_required
from services.openweather_service import get_forecast
from collections import defaultdict
from datetime import datetime

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/api/forecast/<city>')
@login_required
def api_forecast(city):
    data = get_forecast(city)
    if data and 'list' in data:
        # Simplify forecast logic: Group by day, take one reading per day (e.g. 12:00)
        daily = defaultdict(list)
        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            daily[dt.date()].append(item)
            
        simplified_daily = []
        for date, items in list(daily.items())[:5]: # next 5 days
            # pick midday if possible, else first
            midday = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
            simplified_daily.append({
                'date': date.isoformat(),
                'temp': midday['main']['temp'],
                'icon': midday['weather'][0]['icon'],
                'description': midday['weather'][0]['description']
            })
            
        # Hourly forecast for next 24 hours (8 entries of 3 hours)
        hourly = []
        for item in data['list'][:8]:
            dt = datetime.fromtimestamp(item['dt'])
            hourly.append({
                'time': dt.strftime('%I %p'),  # e.g., '02 PM'
                'temp': item['main']['temp'],
                'icon': item['weather'][0]['icon'],
            })
            
        return jsonify({'success': True, 'forecast': simplified_daily, 'hourly': hourly})
    return jsonify({'success': False, 'message': 'Forecast not found'}), 404
