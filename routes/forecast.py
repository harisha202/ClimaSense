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
            
        simplified = []
        for date, items in list(daily.items())[:5]: # next 5 days
            # pick midday if possible, else first
            midday = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
            simplified.append({
                'date': date.isoformat(),
                'temp': midday['main']['temp'],
                'icon': midday['weather'][0]['icon'],
                'description': midday['weather'][0]['description']
            })
        return jsonify({'success': True, 'forecast': simplified})
    return jsonify({'success': False, 'message': 'Forecast not found'}), 404
