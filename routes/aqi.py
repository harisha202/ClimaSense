from flask import Blueprint, jsonify
from flask_login import login_required
from services.openweather_service import get_aqi

aqi_bp = Blueprint('aqi', __name__)

@aqi_bp.route('/api/aqi')
@login_required
def api_aqi():
    from flask import request
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coordinates'}), 400
        
    data = get_aqi(lat, lon)
    if data and 'list' in data and len(data['list']) > 0:
        aqi_value = data['list'][0]['main']['aqi']
        # Map 1-5 to label
        labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
        label = labels.get(aqi_value, 'Unknown')
        return jsonify({'success': True, 'aqi': aqi_value, 'label': label})
    return jsonify({'success': False, 'message': 'AQI data not found'}), 404
