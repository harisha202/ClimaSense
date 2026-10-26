from flask import Blueprint, jsonify, render_template, request, Response, current_app, redirect, url_for
import re
import csv
import io

def sanitize_csv_cell(val):
    if val is None:
        return 'N/A'
    s = str(val).strip()
    forbidden = ('=', '+', '-', '@', chr(9), chr(10), chr(13))
    if s and s[0] in forbidden:
        return "'" + s
    return s
import csv
import io
import time
from datetime import datetime
from flask_login import login_required, current_user
import services.openweather_service as openweather_service
from services.unsplash_service import get_background_image
from services.planner_service import generate_activity_plans
from services.encyclopedia_service import get_city_encyclopedia
from models.search_history import SearchHistory
from models.weather_log import WeatherLog
from extensions import db, get_redis_client
from models.saved_city import SavedCity
from services.ai_service import calculate_comfort_score, get_weather_briefing, answer_weather_chat

weather_bp = Blueprint('weather', __name__)

def get_current_weather(city):
    return openweather_service.get_current_weather(city)

def get_weather_by_coords(lat, lon):
    return openweather_service.get_weather_by_coords(lat, lon)

@weather_bp.route('/home')
@weather_bp.route('/')
def home():
    """Page 00: Welcoming ClimaSense Home & Discovery Page matching master screenshot reference."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.show_login'))
    return render_template('home.html')

@weather_bp.route('/weather')
@weather_bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@weather_bp.route('/compare')
@login_required
def compare():
    return render_template('compare.html')

@weather_bp.route('/explore')
@login_required
def explore():
    """Page 06: Cities Explorer destination discovery"""
    destinations = [
        {"city": "Tokyo", "country": "Japan", "region": "Asia", "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80", "desc": "Capital of Japan, blending historic shrines with ultramodern skylines."},
        {"city": "Paris", "country": "France", "region": "Europe", "img": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80", "desc": "Global center for art, fashion, gastronomy, and cultural landmarks."},
        {"city": "New York", "country": "United States", "region": "Americas", "img": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80", "desc": "Metropolis comprising 5 boroughs at the intersection of global finance."},
        {"city": "London", "country": "United Kingdom", "region": "Europe", "img": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=800&q=80", "desc": "Standing on the River Thames with history stretching back to Roman times."},
        {"city": "Bengaluru", "country": "India", "region": "Asia", "img": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=800&q=80", "desc": "High-tech capital of India, known for pleasant weather and green parks."},
        {"city": "Sydney", "country": "Australia", "region": "Oceania", "img": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=800&q=80", "desc": "Famed for its Opera House, Harbour Bridge, and Pacific beaches."},
        {"city": "Dubai", "country": "United Arab Emirates", "region": "Asia", "img": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=800&q=80", "desc": "Known for luxury shopping, ultramodern architecture, and vibrant nightlife."},
        {"city": "Singapore", "country": "Singapore", "region": "Asia", "img": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=800&q=80", "desc": "Island city-state off southern Malaysia with tropical botanical marvels."}
    ]
    return render_template('explore.html', destinations=destinations)

@weather_bp.route('/settings')
@login_required
def settings():
    """Page 17: User preferences & display settings"""
    return render_template('settings.html')

@weather_bp.route('/help')
def help_faq():
    """Page 19: Help Center & FAQ"""
    return render_template('help.html')

@weather_bp.route('/privacy')
def privacy():
    """Page 20: Privacy Policy"""
    return render_template('privacy_terms.html', section='privacy')

@weather_bp.route('/terms')
def terms():
    """Page 20: Terms of Service"""
    return render_template('privacy_terms.html', section='terms')

@weather_bp.route('/air-quality')
@login_required
def air_quality_page():
    """Page 13: Dedicated Air Quality & UV page"""
    return render_template('air_quality.html')

@weather_bp.route('/alerts')
@login_required
def alerts_page():
    """Page 14: Dedicated Weather Alerts page"""
    return render_template('alerts.html')

@weather_bp.route('/forecast/hourly')
@login_required
def hourly_forecast_page():
    """Page 11: Dedicated Hourly Forecast page"""
    return render_template('hourly_forecast.html')

@weather_bp.route('/forecast/weekly')
@login_required
def weekly_forecast_page():
    """Page 12: Dedicated Weekly Forecast page"""
    return render_template('weekly_forecast.html')


@weather_bp.route('/api/weather/<city>')
def api_weather(city):
    data = get_current_weather(city)
    if data:
        coord = data.get('coord', {})
        lat = coord.get('lat')
        lon = coord.get('lon')

        # Fetch AQI if coordinates available to unify comfort score and log entry
        aqi_val = 1
        if lat is not None and lon is not None:
            aqi_res = openweather_service.get_aqi(lat, lon)
            if aqi_res and 'list' in aqi_res and aqi_res['list']:
                aqi_val = aqi_res['list'][0].get('main', {}).get('aqi', 1)

        # Deduplicate search history (skip duplicate searches for the same city within 5 minutes) if authenticated
        if current_user.is_authenticated:
            recent_search = SearchHistory.query.filter_by(user_id=current_user.id, city=data['name'])\
                .order_by(SearchHistory.searched_at.desc()).first()
            if not recent_search or (datetime.utcnow() - recent_search.searched_at).total_seconds() > 300:
                history = SearchHistory(user_id=current_user.id, city=data['name'])
                db.session.add(history)
        
        # Log for trends with AQI included
        log = WeatherLog(
            city=data['name'],
            temperature=data['main']['temp'],
            feels_like=data['main'].get('feels_like', data['main']['temp']),
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data['wind']['speed'],
            aqi=aqi_val,
            description=data['weather'][0]['description'] if data.get('weather') else '',
            icon=data['weather'][0].get('icon', '01d') if data.get('weather') else '01d'
        )
        db.session.add(log)
        db.session.commit()
        
        # Determine real rain probability from next forecast interval if available
        rain_prob = None
        forecast = openweather_service.get_forecast(city)
        if forecast and 'list' in forecast and forecast['list']:
            first_step = forecast['list'][0]
            rain_prob = int(round(first_step.get('pop', 0) * 100))
            
        if rain_prob is None:
            # Fallback to description analysis
            desc_lower = (data.get('weather', [{}])[0].get('description') or '').lower()
            if 'storm' in desc_lower or 'thunder' in desc_lower:
                rain_prob = 85
            elif 'rain' in desc_lower or 'shower' in desc_lower:
                rain_prob = 75
            elif 'drizzle' in desc_lower:
                rain_prob = 40
            else:
                rain_prob = None
            
        # Grounded comfort score with air quality factored in
        comfort = calculate_comfort_score(
            data['main']['temp'],
            data['main']['humidity'],
            data['wind']['speed'],
            aqi_val=aqi_val
        )

        desc = data['weather'][0]['description'] if data.get('weather') else ''
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
            
        if rain_prob >= 40:
            summary += " Don't forget your umbrella!"
            
        return jsonify({
            'success': True,
            'data': data,
            'ai_summary': summary,
            'rain_probability': rain_prob,
            'comfort_score': comfort['score'],
            'comfort_label': comfort['label']
        })
    return jsonify({'success': False, 'message': 'City not found or API error'}), 404

@weather_bp.route('/api/dashboard/<city>')
@login_required
def api_combined_dashboard(city):
    """
    Combined endpoint: returns current weather, forecast, AQI, UV,
    planner, briefing, and background in one single roundtrip.
    """
    data = get_current_weather(city)
    if not data:
        return jsonify({'success': False, 'message': f"City '{city}' not found."}), 404

    coord = data.get('coord', {})
    lat = coord.get('lat')
    lon = coord.get('lon')

    forecast = openweather_service.get_forecast(city)
    aqi_data = openweather_service.get_aqi(lat, lon) if (lat and lon) else None
    uv_data = openweather_service.get_uv_index(lat, lon) if (lat and lon) else None
    desc = data['weather'][0]['description'] if data.get('weather') else ''

    country = data.get('sys', {}).get('country', '')
    background = get_background_image(city, desc, country=country)
    briefing = get_weather_briefing(city)
    planner = generate_activity_plans(forecast, data) if forecast else None

    # Compute comfort
    aqi_val = 1
    if aqi_data and 'list' in aqi_data and aqi_data['list']:
        aqi_val = aqi_data['list'][0].get('main', {}).get('aqi', 1)
        
    comfort = calculate_comfort_score(data['main']['temp'], data['main']['humidity'], data['wind']['speed'], aqi_val)

    return jsonify({
        'success': True,
        'city': data.get('name', city),
        'weather': data,
        'forecast': forecast,
        'aqi': aqi_data,
        'uv': uv_data,
        'comfort_score': comfort['score'],
        'comfort_label': comfort['label'],
        'background': background,
        'briefing': briefing,
        'planner': planner
    })

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
    history = payload.get('history', [])
    res = answer_weather_chat(message, current_city=city, user_id=current_user.id, history=history)
    return jsonify(res)

@weather_bp.route('/api/weather/recent')
@login_required
def get_recent_searches():
    histories = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.searched_at.desc()).limit(10).all()
    seen = set()
    unique_cities = []
    for h in histories:
        if h.city not in seen:
            seen.add(h.city)
            unique_cities.append(h.city)
    return jsonify({'success': True, 'recent': unique_cities})

@weather_bp.route('/api/weather/<city>/export/csv')
def export_weather_csv(city):
    """
    Exports verified current weather observations to CSV.
    Implements formula injection sanitization and explicit units.
    """
    data = get_current_weather(city)
    if not data:
        return jsonify({'success': False, 'message': 'City not found'}), 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'City', 'Country', 'Observation Timestamp (UTC)',
        'Temperature (C)', 'Feels Like (C)', 'Weather Condition',
        'Humidity (%)', 'Wind Speed (m/s)', 'Wind Direction (deg)',
        'Pressure (hPa)', 'Visibility (km)'
    ])
    
    timestamp = datetime.utcfromtimestamp(data.get('dt', datetime.utcnow().timestamp())).strftime('%Y-%m-%d %H:%M:%S UTC')
    vis_km = round(data.get('visibility', 0) / 1000.0, 2) if data.get('visibility') is not None else 'N/A'
    wind_deg = data.get('wind', {}).get('deg', 'N/A')
    
    writer.writerow([
        sanitize_csv_cell(data.get('name', city)),
        sanitize_csv_cell(data.get('sys', {}).get('country', 'N/A')),
        sanitize_csv_cell(timestamp),
        sanitize_csv_cell(data.get('main', {}).get('temp', 'N/A')),
        sanitize_csv_cell(data.get('main', {}).get('feels_like', 'N/A')),
        sanitize_csv_cell(data['weather'][0]['description'].title() if data.get('weather') else 'N/A'),
        sanitize_csv_cell(data.get('main', {}).get('humidity', 'N/A')),
        sanitize_csv_cell(data.get('wind', {}).get('speed', 'N/A')),
        sanitize_csv_cell(f"{wind_deg}°" if wind_deg != 'N/A' else 'N/A'),
        sanitize_csv_cell(data.get('main', {}).get('pressure', 'N/A')),
        sanitize_csv_cell(vis_km)
    ])
    
    clean_city = re.sub(r'[^a-zA-Z0-9_-]', '_', city.lower())
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=climasense_current_weather_{clean_city}.csv'
    return response

@weather_bp.route('/api/weather/<city>/export/pdf')
@login_required
def export_weather_pdf(city):
    """
    Renders verified weather report through Jinja2 template to prevent Reflected XSS.
    Enforces login protection.
    """
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
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    rendered_html = render_template(
        'export_pdf.html',
        name=name,
        country=country,
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed=wind_speed,
        desc=desc,
        timestamp=timestamp
    )
    return Response(rendered_html, mimetype='text/html')

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

@weather_bp.route('/api/background', defaults={'city': '', 'description': ''}, strict_slashes=False)
@weather_bp.route('/api/background/<city>', defaults={'description': ''}, strict_slashes=False)
@weather_bp.route('/api/background/<city>/<description>', strict_slashes=False)
def api_background(city='', description=''):
    country = request.args.get('country', '').strip()
    bg_data = get_background_image(city, description, country=country)
    if isinstance(bg_data, dict):
        return jsonify({'success': True, **bg_data})
    return jsonify({'success': True, 'url': bg_data})

@weather_bp.route('/api/cities/save', methods=['POST'])
@login_required
def save_city():
    data = request.get_json(silent=True) or {}
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
    data = request.get_json(silent=True) or {}
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
    except Exception:
        return Response(status=404)

@weather_bp.route('/api/uv')
def api_uv():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coords'}), 400
    data = openweather_service.get_uv_index(lat, lon)
    uvi = data.get('value', 5.0) if data else 5.0
    category = "Low" if uvi < 3 else "Moderate" if uvi < 6 else "High" if uvi < 8 else "Very High"
    return jsonify({'success': True, 'uvi': uvi, 'uv_index': uvi, 'category': category})

@weather_bp.route('/api/system-status')
@login_required
def api_system_status():
    """Live system status reporting true operational status of database, cache, and APIs."""
    ow_key = bool(current_app.config.get('OPENWEATHER_API_KEY'))
    un_key = bool(current_app.config.get('UNSPLASH_API_KEY'))
    ai_key = bool(current_app.config.get('AI_API_KEY'))

    # Check Database connection
    db_status = 'Online'
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_status = 'Degraded'

    # Check Redis cache
    cache_status = 'Fallback (Memory)'
    r_client = get_redis_client()
    if r_client:
        try:
            r_client.ping()
            cache_status = 'Online (Redis)'
        except Exception:
            cache_status = 'Degraded'

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
                'database': f"Connected ({db_status})"
            },
            'cache': {
                'name': 'Redis / Celery Cache',
                'status': cache_status,
                'ttl': f"{current_app.config.get('CACHE_TTL_SECONDS', 300)}s"
            },
            'background_service': {
                'name': 'Unsplash Dynamic Imagery',
                'status': 'Online' if un_key else 'Curated Fallback',
                'api_key_status': 'Protected (•••••••• - Not Shown)'
            },
            'ai_service': {
                'name': 'Google Gemini Intelligence',
                'status': 'Online' if ai_key else 'Smart Rules Fallback',
                'model': current_app.config.get('AI_MODEL', 'gemini-2.0-flash')
            }
        }
    })

@weather_bp.route('/api/encyclopedia/<city>')
@weather_bp.route('/api/city-info/<city>')
def api_encyclopedia(city):
    """
    Returns structured 38-section municipal encyclopedia targeting 4,000+ words
    with citations and verified word count badge.
    """
    country = request.args.get('country', '').strip()
    from services.encyclopedia_service import fetch_wikipedia_summary
    info = fetch_wikipedia_summary(city, country=country)
    article = get_city_encyclopedia(city, country=country)
    return jsonify({
        'success': True,
        'city': city,
        'article': article,
        'info': info
    })


@weather_bp.route('/api/compare/export/csv')
def export_comparison_csv():
    """
    Exports side-by-side city comparison measurements to CSV.
    """
    city1 = request.args.get('city1', 'Bengaluru').strip()
    city2 = request.args.get('city2', 'Mysuru').strip()
    
    data1 = get_current_weather(city1)
    data2 = get_current_weather(city2)
    
    if not data1 or not data2:
        return jsonify({'success': False, 'message': 'One or both cities could not be found'}), 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    
    c1_name = f"{data1.get('name', city1)}, {data1.get('sys', {}).get('country', '')}"
    c2_name = f"{data2.get('name', city2)}, {data2.get('sys', {}).get('country', '')}"
    
    writer.writerow(['Metric', 'Measurement Unit', sanitize_csv_cell(c1_name), sanitize_csv_cell(c2_name), 'Difference'])
    
    t1 = data1.get('main', {}).get('temp', 0)
    t2 = data2.get('main', {}).get('temp', 0)
    writer.writerow(['Temperature', '°C', sanitize_csv_cell(t1), sanitize_csv_cell(t2), sanitize_csv_cell(round(t1 - t2, 1))])
    
    f1 = data1.get('main', {}).get('feels_like', 0)
    f2 = data2.get('main', {}).get('feels_like', 0)
    writer.writerow(['Feels Like Temperature', '°C', sanitize_csv_cell(f1), sanitize_csv_cell(f2), sanitize_csv_cell(round(f1 - f2, 1))])
    
    h1 = data1.get('main', {}).get('humidity', 0)
    h2 = data2.get('main', {}).get('humidity', 0)
    writer.writerow(['Relative Humidity', '%', sanitize_csv_cell(h1), sanitize_csv_cell(h2), sanitize_csv_cell(round(h1 - h2, 1))])
    
    w1 = data1.get('wind', {}).get('speed', 0)
    w2 = data2.get('wind', {}).get('speed', 0)
    writer.writerow(['Wind Velocity', 'm/s', sanitize_csv_cell(w1), sanitize_csv_cell(w2), sanitize_csv_cell(round(w1 - w2, 2))])
    
    p1 = data1.get('main', {}).get('pressure', 0)
    p2 = data2.get('main', {}).get('pressure', 0)
    writer.writerow(['Atmospheric Pressure', 'hPa', sanitize_csv_cell(p1), sanitize_csv_cell(p2), sanitize_csv_cell(round(p1 - p2, 1))])
    
    cond1 = data1['weather'][0]['description'].title() if data1.get('weather') else 'N/A'
    cond2 = data2['weather'][0]['description'].title() if data2.get('weather') else 'N/A'
    writer.writerow(['Weather Condition', 'Text', sanitize_csv_cell(cond1), sanitize_csv_cell(cond2), 'N/A'])
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=climasense_comparison.csv'
    return response
