from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from models.search_history import SearchHistory
from extensions import db
import io
import csv
from flask import Response

history_bp = Blueprint('history', __name__)

def sanitize_csv_cell(val):
    if val is None:
        return 'N/A'
    s = str(val).strip()
    forbidden = ('=', '+', '-', '@', chr(9), chr(10), chr(13))
    if s and s[0] in forbidden:
        return "'" + s
    return s

@history_bp.route('/history')
@login_required
def history():
    return render_template('history.html')

@history_bp.route('/api/search-history')
@login_required
def get_search_history():
    histories = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.searched_at.desc()).limit(20).all()
    return jsonify({'success': True, 'history': [h.to_dict() for h in histories]})

@history_bp.route('/api/clear-history', methods=['GET', 'POST', 'DELETE'])
@history_bp.route('/api/search-history/clear', methods=['GET', 'POST', 'DELETE'])
@login_required
def clear_history():
    SearchHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Search history cleared successfully'})

@history_bp.route('/api/history/export/csv')
@login_required
def export_history_csv():
    """
    Exports verified search history records to CSV.
    """
    records = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.searched_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Record ID', 'City Queried', 'Search Timestamp (UTC)'])
    
    for r in records:
        writer.writerow([
            sanitize_csv_cell(r.id),
            sanitize_csv_cell(r.city),
            sanitize_csv_cell(r.searched_at.strftime('%Y-%m-%d %H:%M:%S UTC'))
        ])
        
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=climasense_search_history.csv'
    return response
