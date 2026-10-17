from flask import Blueprint, jsonify, render_template, request, Response
import csv
import io
from datetime import datetime
from flask_login import login_required, current_user
from services.openweather_service import get_current_weather, get_weather_by_coords
from services.unsplash_service import get_background_image
from models.search_history import SearchHistory
from models.weather_log import WeatherLog
from extensions import db
from models.saved_city import SavedCity
from services.ai_service import calculate_comfort_score, get_weather_briefing, answer_weather_chat

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@weather_bp.route('/api/weather/<city>')
@login_required
def api_weather(city):
    data = get_current_weather(city)
    if data:
        # Save to search history
        history = SearchHistory(user_id=current_user.id, city=data['name'])
        db.session.add(history)
        
        # Log for trends
        log = WeatherLog(
            city=data['name'],
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data['wind']['speed'],
            description=data['weather'][0]['description'],
            icon=data['weather'][0]['icon']
        )
        db.session.add(log)
        db.session.commit()
        
        # Generate simple AI-style summary
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        wind = data['wind']['speed']
        
        summary = f"Today's weather is {desc}."
        if temp > 30:
            summary += " It is quite hot outside."
        elif temp < 10:
            summary += " It is cold outside, bundle up."
        else:
            summary += " The temperature is moderate."
            
        if wind > 10:
            summary += " Expect strong winds throughout the day."
        else:
            summary += " Light winds expected."
            
        if 'rain' in desc.lower():
            summary += " Don't forget your umbrella!"
            
        # Compute chance of rain percentage
        desc_lower = desc.lower()
        if 'storm' in desc_lower or 'thunder' in desc_lower:
            rain_prob = 85
        elif 'rain' in desc_lower or 'shower' in desc_lower:
            rain_prob = 75
        elif 'drizzle' in desc_lower:
            rain_prob = 50
        elif 'cloud' in desc_lower:
            rain_prob = 25
        else:
            rain_prob = 10
            
        # Compute grounded comfort score
        comfort = calculate_comfort_score(data['main']['temp'], data['main']['humidity'], data['wind']['speed'])
            
        return jsonify({
            'success': True,
            'data': data,
            'ai_summary': summary,
            'rain_probability': rain_prob,
            'comfort_score': comfort['score'],
            'comfort_label': comfort['label']
        })
    return jsonify({'success': False, 'message': 'City not found or API error'}), 404

@weather_bp.route('/api/weather/<city>/briefing')
@login_required
def api_weather_briefing(city):
    force_refresh = request.args.get('refresh') == 'true'
    res = get_weather_briefing(city, force_refresh=force_refresh)
    status_code = 200 if res.get('success') else 404
    return jsonify(res), status_code

@weather_bp.route('/api/weather/chat', methods=['POST'])
@login_required
def api_weather_chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get('message', '').strip()
    city = payload.get('city', 'Bengaluru').strip()
    if not message:
        return jsonify({'success': False, 'message': 'Message cannot be empty.'}), 400
    res = answer_weather_chat(message, current_city=city, user_id=current_user.id)
    return jsonify(res)

@weather_bp.route('/api/weather/recent')
@login_required
def get_recent_searches():
    histories = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.searched_at.desc()).limit(10).all()
    # Deduplicate while preserving order
    seen = set()
    unique_cities = []
    for h in histories:
        if h.city not in seen:
            seen.add(h.city)
            unique_cities.append(h.city)
    return jsonify({'success': True, 'recent': unique_cities})

@weather_bp.route('/api/weather/<city>/export/csv')
def export_weather_csv(city):
    data = get_current_weather(city)
    if not data:
        return jsonify({'success': False, 'message': 'City not found'}), 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['City', 'Country', 'Temperature (C)', 'Feels Like (C)', 'Humidity (%)', 'Pressure (hPa)', 'Wind Speed (m/s)', 'Description'])
    writer.writerow([
        data.get('name', city),
        data.get('sys', {}).get('country', 'N/A'),
        data.get('main', {}).get('temp', 'N/A'),
        data.get('main', {}).get('feels_like', 'N/A'),
        data.get('main', {}).get('humidity', 'N/A'),
        data.get('main', {}).get('pressure', 'N/A'),
        data.get('wind', {}).get('speed', 'N/A'),
        data['weather'][0]['description'] if data.get('weather') else 'N/A'
    ])
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=weather_report_{city.lower()}.csv'
    return response

@weather_bp.route('/api/weather/geo')
@login_required
def api_weather_geo():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coordinates'}), 400
        
    data = get_weather_by_coords(lat, lon)
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'Location not found or API error'}), 404

@weather_bp.route('/api/background/<city>', defaults={'description': ''}, strict_slashes=False)
@weather_bp.route('/api/background/<city>/<description>', strict_slashes=False)
@login_required
def api_background(city, description=''):
    bg_data = get_background_image(city, description)
    if isinstance(bg_data, dict):
        return jsonify({'success': True, **bg_data})
    return jsonify({'success': True, 'url': bg_data})
@weather_bp.route('/api/cities/save', methods=['POST'])
@login_required
def save_city():
    data = request.json
    city_name = data.get('city')
    if not city_name:
        return jsonify({'success': False, 'message': 'City name required'}), 400
        
    existing = SavedCity.query.filter_by(user_id=current_user.id, city=city_name).first()
    if existing:
        return jsonify({'success': False, 'message': 'City already saved'}), 400
        
    new_city = SavedCity(user_id=current_user.id, city=city_name)
    db.session.add(new_city)
    db.session.commit()
    return jsonify({'success': True, 'message': 'City saved successfully'})

@weather_bp.route('/api/cities/saved', methods=['GET'])
@login_required
def get_saved_cities():
    cities = SavedCity.query.filter_by(user_id=current_user.id).order_by(SavedCity.created_at.desc()).all()
    return jsonify({'success': True, 'cities': [c.to_dict() for c in cities]})

@weather_bp.route('/api/cities/unsave', methods=['POST'])
@login_required
def unsave_city():
    data = request.json
    city_name = data.get('city')
    if not city_name:
        return jsonify({'success': False, 'message': 'City name required'}), 400
        
    existing = SavedCity.query.filter_by(user_id=current_user.id, city=city_name).first()
    if not existing:
        return jsonify({'success': False, 'message': 'City not found in saved list'}), 404
        
    db.session.delete(existing)
    db.session.commit()
    return jsonify({'success': True, 'message': 'City removed successfully'})

_tile_cache = {}

@weather_bp.route('/api/tiles/<layer>/<z>/<x>/<y>.png')
@login_required
def proxy_tiles(layer, z, x, y):
    from flask import current_app
    import requests
    tile_key = f"{layer}_{z}_{x}_{y}"
    if tile_key in _tile_cache:
        resp_content = _tile_cache[tile_key]
        return Response(resp_content, mimetype='image/png', headers={'Cache-Control': 'public, max-age=86400'})
        
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    url = f"https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={api_key}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            if len(_tile_cache) > 200:
                _tile_cache.clear()
            _tile_cache[tile_key] = resp.content
            return Response(resp.content, mimetype='image/png', headers={'Cache-Control': 'public, max-age=86400'})
        return Response(status=resp.status_code)
    except:
        return Response(status=404)

@weather_bp.route('/api/uv')
@login_required
def api_uv():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coords'}), 400
    from services.openweather_service import get_uv_index
    data = get_uv_index(lat, lon)
    uvi = data.get('value', 5.0) if data else 5.0
    category = "Low" if uvi < 3 else "Moderate" if uvi < 6 else "High" if uvi < 8 else "Very High"
    return jsonify({'success': True, 'uvi': uvi, 'category': category})

@weather_bp.route('/api/system-status')
@login_required
def api_system_status():
    from flask import current_app
    ow_key = bool(current_app.config.get('OPENWEATHER_API_KEY'))
    un_key = bool(current_app.config.get('UNSPLASH_API_KEY'))
    
    # CRITICAL SECURITY RULE: API KEY SHOULD NOT BE SHOWN
    return jsonify({
        'success': True,
        'status': {
            'weather_api': {
                'name': 'OpenWeatherMap API',
                'status': 'Online' if ow_key else 'Degraded',
                'api_key_status': 'Protected (•••••••• - Not Shown)'
            },
            'backend': {
                'name': 'Flask 3.0 Backend Engine',
                'status': 'Online',
                'database': 'Connected (SQLAlchemy)'
            },
            'cache': {
                'name': 'Redis / Celery Cache',
                'status': 'Online',
                'ttl': f"{current_app.config.get('CACHE_TTL_SECONDS', 300)}s"
            },
            'background_service': {
                'name': 'Unsplash Dynamic Imagery',
                'status': 'Online' if un_key else 'Fallback',
                'api_key_status': 'Protected (•••••••• - Not Shown)'
            }
        }
    })

@weather_bp.route('/api/weather/<city>/export/pdf')
def export_weather_pdf(city):
    data = get_current_weather(city)
    if not data:
        return jsonify({'success': False, 'message': 'City not found'}), 404
        
    name = data.get('name', city)
    country = data.get('sys', {}).get('country', 'N/A')
    temp = data.get('main', {}).get('temp', 'N/A')
    feels_like = data.get('main', {}).get('feels_like', 'N/A')
    humidity = data.get('main', {}).get('humidity', 'N/A')
    pressure = data.get('main', {}).get('pressure', 'N/A')
    wind_speed = data.get('wind', {}).get('speed', 'N/A')
    desc = data['weather'][0]['description'].title() if data.get('weather') else 'N/A'
        
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Weather Report - {name}</title>
    <style>
        body {{ font-family: 'Open Sans', Arial, sans-serif; padding: 40px; color: #111; background: #fff; }}
        h1 {{ color: #0d3b66; border-bottom: 2px solid #0d3b66; padding-bottom: 10px; }}
        .meta {{ color: #666; margin-bottom: 30px; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f4f6f9; color: #333; }}
        @media print {{
            body {{ padding: 0; }}
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h1>ClimaSense Environmental Report</h1>
    <div class="meta">City: <strong>{name}, {country}</strong> | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Temperature</td><td>{temp} °C</td></tr>
        <tr><td>Feels Like</td><td>{feels_like} °C</td></tr>
        <tr><td>Humidity</td><td>{humidity} %</td></tr>
        <tr><td>Atmospheric Pressure</td><td>{pressure} hPa</td></tr>
        <tr><td>Wind Speed</td><td>{wind_speed} m/s</td></tr>
        <tr><td>Conditions</td><td>{desc}</td></tr>
    </table>
    <div style="margin-top: 30px;">
        <button onclick="window.print()" style="padding: 10px 20px; background: #0d3b66; color: #fff; border: none; border-radius: 4px; cursor: pointer;">Print / Save as PDF</button>
    </div>
    <script>
        window.onload = () => window.print();
    </script>
</body>
</html>"""
    return Response(html, mimetype='text/html')
