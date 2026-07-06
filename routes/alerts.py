from flask import Blueprint, jsonify, request
from flask_login import login_required
from services.openweather_service import get_alerts

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/api/alerts')
@login_required
def api_alerts():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'success': False, 'message': 'Missing coordinates'}), 400
        
    data = get_alerts(lat, lon)
    if data and 'alerts' in data and len(data['alerts']) > 0:
        alert = data['alerts'][0]
        return jsonify({
            'success': True, 
            'alert': {
                'title': alert.get('event', 'Weather Alert'),
                'description': alert.get('description', ''),
                'start': alert.get('start'),
                'end': alert.get('end')
            }
        })
    return jsonify({'success': True, 'alert': None})
