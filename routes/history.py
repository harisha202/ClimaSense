from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from models.search_history import SearchHistory
from extensions import db

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def history():
    return render_template('history.html')

@history_bp.route('/api/search-history')
@login_required
def get_search_history():
    histories = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.searched_at.desc()).limit(20).all()
    return jsonify({'success': True, 'history': [h.to_dict() for h in histories]})

@history_bp.route('/api/clear-history', methods=['POST'])
@login_required
def clear_history():
    SearchHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True})
