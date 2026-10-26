from flask import Blueprint, jsonify, Response
from flask_login import login_required
import services.openweather_service as openweather_service
from collections import defaultdict
from datetime import datetime
import io
import csv
import re

forecast_bp = Blueprint('forecast', __name__)

def get_forecast(city):
    return openweather_service.get_forecast(city)

def sanitize_csv_cell(val):
    if val is None:
        return 'N/A'
    s = str(val).strip()
    forbidden = ('=', '+', '-', '@', chr(9), chr(10), chr(13))
    if s and s[0] in forbidden:
        return "'" + s
    return s

@forecast_bp.route('/api/forecast/<city>')
def api_forecast(city):
    data = get_forecast(city)
    if data and 'list' in data:
        # Timezone offset provided by OpenWeather in seconds from UTC
        tz_offset = data.get('city', {}).get('timezone', 0)
        
        daily = defaultdict(list)
        hourly_forecast = []
        
        for item in data['list']:
            # Adjust timestamp to city's true local time
            local_dt = datetime.utcfromtimestamp(item['dt'] + tz_offset)
            daily[local_dt.date()].append(item)
            
            if len(hourly_forecast) < 12:
                hourly_forecast.append({
                    'time': local_dt.strftime('%I %p'),
                    'dt': item['dt'],
                    'temp': round(item['main']['temp'], 1),
                    'pop': int(round(item.get('pop', 0) * 100)),
                    'condition': item['weather'][0]['description'] if item.get('weather') else '',
                    'description': item['weather'][0]['description'] if item.get('weather') else '',
                    'icon': item['weather'][0]['icon'] if item.get('weather') else '01d'
                })
            
        simplified_daily = []
        for date, items in list(daily.items())[:5]: # Next 5 days
            midday = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
            temps = [i['main']['temp'] for i in items]
            max_temp = max(temps)
            min_temp = min(temps)
            max_pop = max((int(round(i.get('pop', 0) * 100)) for i in items), default=0)
            cond = midday['weather'][0]['description'] if midday.get('weather') else ''
            
            simplified_daily.append({
                'date': date.strftime('%a, %b %d'),
                'max_temp': round(max_temp, 1),
                'min_temp': round(min_temp, 1),
                'temp': round(max_temp, 1),
                'pop': max_pop,
                'condition': cond,
                'description': cond,
                'icon': midday['weather'][0]['icon'] if midday.get('weather') else '01d'
            })
            
        return jsonify({
            'success': True,
            'city': data.get('city', {}).get('name', city),
            'timezone_offset': tz_offset,
            'forecast': simplified_daily,
            'daily': simplified_daily,
            'simplified_daily': simplified_daily,
            'hourly': hourly_forecast
        })
        
    return jsonify({'success': False, 'message': 'Forecast unavailable'}), 404

@forecast_bp.route('/api/forecast/<city>/export/hourly/csv')
@login_required
def export_hourly_csv(city):
    """
    Exports 24-hour meteorological timeline to CSV.
    """
    data = get_forecast(city)
    if not data or 'list' not in data:
        return jsonify({'success': False, 'message': 'Forecast data unavailable'}), 404
        
    tz_offset = data.get('city', {}).get('timezone', 0)
    c_name = data.get('city', {}).get('name', city)
    country = data.get('city', {}).get('country', '')
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'City', 'Country', 'Forecast Timestamp (Local)', 'Forecast Timestamp (UTC)',
        'Temperature (C)', 'Weather Condition', 'Precipitation Probability (%)',
        'Humidity (%)', 'Wind Speed (m/s)'
    ])
    
    for item in data['list'][:16]:  # Up to 48 hours / 16 3-hr steps
        local_dt = datetime.utcfromtimestamp(item['dt'] + tz_offset).strftime('%Y-%m-%d %H:%M')
        utc_dt = datetime.utcfromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M UTC')
        temp = round(item['main']['temp'], 1)
        cond = item['weather'][0]['description'].title() if item.get('weather') else 'N/A'
        pop = int(round(item.get('pop', 0) * 100))
        hum = item['main'].get('humidity', 'N/A')
        wind = item.get('wind', {}).get('speed', 'N/A')
        
        writer.writerow([
            sanitize_csv_cell(c_name),
            sanitize_csv_cell(country),
            sanitize_csv_cell(local_dt),
            sanitize_csv_cell(utc_dt),
            sanitize_csv_cell(temp),
            sanitize_csv_cell(cond),
            sanitize_csv_cell(pop),
            sanitize_csv_cell(hum),
            sanitize_csv_cell(wind)
        ])
        
    clean_city = re.sub(r'[^a-zA-Z0-9_-]', '_', city.lower())
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=climasense_hourly_forecast_{clean_city}.csv'
    return response

@forecast_bp.route('/api/forecast/<city>/export/weekly/csv')
@login_required
def export_weekly_csv(city):
    """
    Exports multi-day daily weather outlook to CSV.
    """
    data = get_forecast(city)
    if not data or 'list' not in data:
        return jsonify({'success': False, 'message': 'Forecast data unavailable'}), 404
        
    tz_offset = data.get('city', {}).get('timezone', 0)
    c_name = data.get('city', {}).get('name', city)
    country = data.get('city', {}).get('country', '')
    
    daily = defaultdict(list)
    for item in data['list']:
        local_dt = datetime.utcfromtimestamp(item['dt'] + tz_offset)
        daily[local_dt.date()].append(item)
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'City', 'Country', 'Forecast Date', 'Day of Week',
        'Min Temperature (C)', 'Max Temperature (C)', 'Midday Weather Condition',
        'Max Rain Probability (%)'
    ])
    
    for date, items in list(daily.items())[:7]:
        midday = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
        temps = [i['main']['temp'] for i in items]
        max_t = round(max(temps), 1)
        min_t = round(min(temps), 1)
        max_pop = max((int(round(i.get('pop', 0) * 100)) for i in items), default=0)
        cond = midday['weather'][0]['description'].title() if midday.get('weather') else 'N/A'
        
        writer.writerow([
            sanitize_csv_cell(c_name),
            sanitize_csv_cell(country),
            sanitize_csv_cell(date.strftime('%Y-%m-%d')),
            sanitize_csv_cell(date.strftime('%A')),
            sanitize_csv_cell(min_t),
            sanitize_csv_cell(max_t),
            sanitize_csv_cell(cond),
            sanitize_csv_cell(max_pop)
        ])
        
    clean_city = re.sub(r'[^a-zA-Z0-9_-]', '_', city.lower())
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=climasense_weekly_forecast_{clean_city}.csv'
    return response
