from flask import Blueprint, jsonify, render_template, request
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
        
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'City not found or API error'}), 404

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
