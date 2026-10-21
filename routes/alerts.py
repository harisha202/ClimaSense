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
        formatted_alerts = []
        for a in data['alerts']:
            formatted_alerts.append({
                'title': a.get('event', 'Weather Alert'),
                'description': a.get('description', ''),
                'start': a.get('start'),
                'end': a.get('end'),
                'sender': a.get('sender_name', 'Meteorological Authority'),
                'is_inferred': a.get('inferred', False)
            })

        return jsonify({
            'success': True,
            'alert': formatted_alerts[0], # Backwards compatibility
            'alerts': formatted_alerts,
            'count': len(formatted_alerts)
        })
    return jsonify({'success': True, 'alert': None, 'alerts': [], 'count': 0})
