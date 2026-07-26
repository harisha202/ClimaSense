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
        daily = defaultdict(list)
        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            daily[dt.date()].append(item)
            
        simplified_daily = []
        for date, items in list(daily.items())[:5]: # next 5 days
            midday = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
            temps = [i['main']['temp'] for i in items]
            max_temp = max(temps)
            min_temp = min(temps)
            simplified_daily.append({
                'date': date.isoformat(),
                'temp': midday['main']['temp'],
                'max_temp': max_temp,
                'min_temp': min_temp,
                'icon': midday['weather'][0]['icon'],
                'description': midday['weather'][0]['description']
            })
            
        # Hourly forecast for next 24 hours (8 entries of 3 hours)
        hourly = []
        for item in data['list'][:8]:
            dt = datetime.fromtimestamp(item['dt'])
            pop_pct = int(item.get('pop', 0.15) * 100)
            hourly.append({
                'time': dt.strftime('%I %p'),  # e.g., '02 PM'
                'temp': item['main']['temp'],
                'icon': item['weather'][0]['icon'],
                'pop': pop_pct
            })
            
        return jsonify({'success': True, 'forecast': simplified_daily, 'hourly': hourly})
    return jsonify({'success': False, 'message': 'Forecast not found'}), 404
