from flask import Blueprint, jsonify, request
from flask_login import login_required
from services.openweather_service import get_aqi

aqi_bp = Blueprint('aqi', __name__)

# Standard threshold reference values (µg/m³) for determining dominant pollutant
POLLUTANT_THRESHOLDS = {
    'pm2_5': 25.0,
    'pm10': 50.0,
    'o3': 100.0,
    'no2': 40.0,
    'so2': 20.0,
    'co': 4000.0
}

POLLUTANT_LABELS = {
    'pm2_5': 'PM2.5',
    'pm10': 'PM10',
    'o3': 'Ozone (O₃)',
    'no2': 'Nitrogen Dioxide (NO₂)',
    'so2': 'Sulfur Dioxide (SO₂)',
    'co': 'Carbon Monoxide (CO)'
}

def determine_dominant_pollutant(components):
    """
    Computes the true dominant air pollutant based on normalized
    health threshold ratios rather than assuming PM2.5.
    """
    if not components:
        return "PM2.5", 0
        
    highest_ratio = -1.0
    dominant_key = 'pm2_5'
    dominant_val = 0
    
    for key, threshold in POLLUTANT_THRESHOLDS.items():
        val = components.get(key, 0)
        ratio = val / threshold
        if ratio > highest_ratio:
            highest_ratio = ratio
            dominant_key = key
            dominant_val = val
            
    display_name = POLLUTANT_LABELS.get(dominant_key, dominant_key.upper())
    return f"{display_name} ({round(dominant_val, 1)} µg/m³)", dominant_key

@aqi_bp.route('/api/aqi')
@login_required
def api_aqi():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coordinates'}), 400
        
    data = get_aqi(lat, lon)
    if data and 'list' in data and len(data['list']) > 0:
        item = data['list'][0]
        aqi_value = item['main']['aqi']
        # Map 1-5 to standard label
        labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
        label = labels.get(aqi_value, 'Unknown')
        
        components = item.get('components', {})
        main_pollutant, main_key = determine_dominant_pollutant(components)
        
        return jsonify({
            'success': True, 
            'aqi': aqi_value, 
            'label': label,
            'main_pollutant': main_pollutant,
            'dominant_key': main_key,
            'components': components
        })
    return jsonify({'success': False, 'message': 'AQI data not found'}), 404
