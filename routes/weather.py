from flask import Blueprint, jsonify, render_template, request, Response
import csv
import io
from flask_login import login_required, current_user
from services.openweather_service import get_current_weather, get_weather_by_coords
from services.unsplash_service import get_background_image
from models.search_history import SearchHistory
from models.weather_log import WeatherLog
from extensions import db
from models.saved_city import SavedCity

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
            
        return jsonify({'success': True, 'data': data, 'ai_summary': summary})
    return jsonify({'success': False, 'message': 'City not found or API error'}), 404

@weather_bp.route('/api/weather/recent')
@login_required
def get_recent_searches():
    histories = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).limit(10).all()
    # Deduplicate while preserving order
    seen = set()
    unique_cities = []
    for h in histories:
        if h.city not in seen:
            seen.add(h.city)
            unique_cities.append(h.city)
    return jsonify({'success': True, 'recent': unique_cities})

@weather_bp.route('/api/weather/<city>/export/csv')
@login_required
def export_weather_csv(city):
    data = get_current_weather(city)
    if not data:
        return jsonify({'success': False, 'message': 'City not found'}), 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['City', 'Country', 'Temperature (C)', 'Feels Like (C)', 'Humidity (%)', 'Pressure (hPa)', 'Wind Speed (m/s)', 'Description'])
    writer.writerow([
        data['name'],
        data['sys']['country'],
        data['main']['temp'],
        data['main']['feels_like'],
        data['main']['humidity'],
        data['main']['pressure'],
        data['wind']['speed'],
        data['weather'][0]['description']
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

@weather_bp.route('/api/background/<city>/<description>')
@login_required
def api_background(city, description):
    img_url = get_background_image(city, description)
    return jsonify({'success': True, 'url': img_url})
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

@weather_bp.route('/api/tiles/<layer>/<z>/<x>/<y>.png')
@login_required
def proxy_tiles(layer, z, x, y):
    from flask import current_app
    import requests
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    url = f"https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={api_key}"
    try:
        resp = requests.get(url, timeout=5)
        return Response(resp.content, mimetype='image/png')
    except:
        return Response(status=404)
