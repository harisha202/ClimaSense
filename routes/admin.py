from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from services.cache_service import get_cache_stats
from models.user import User
from models.weather_log import WeatherLog
from models.forecast_snapshot import ForecastSnapshot
from models.saved_city import SavedCity
from extensions import db, redis_client
import time

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_bp.route('/test')
@login_required
def admin_dashboard():
    """Renders the comprehensive administrative diagnostics and automated test bench page."""
    return render_template('admin.html')

@admin_bp.route('/api/admin/metrics')
@login_required
def api_admin_metrics():
    """Returns live diagnostic metrics, user counts, and service states."""
    user_count = User.query.count()
    log_count = WeatherLog.query.count()
    saved_count = SavedCity.query.count()
    snapshot_count = ForecastSnapshot.query.count()
    cache_stats = get_cache_stats()

    db_latency_ms = 0
    t0 = time.time()
    try:
        db.session.execute(db.text('SELECT 1'))
        db_latency_ms = round((time.time() - t0) * 1000, 2)
        db_state = 'Optimal'
    except Exception as e:
        db_state = f'Error: {e}'

    return jsonify({
        'success': True,
        'metrics': {
            'users': user_count,
            'logs': log_count,
            'saved_cities': saved_count,
            'forecast_snapshots': snapshot_count,
            'db_latency_ms': db_latency_ms,
            'db_state': db_state,
            'cache': cache_stats,
            'ai_model': current_app.config.get('AI_MODEL', 'gemini-2.0-flash'),
            'ai_provider': current_app.config.get('AI_PROVIDER', 'gemini'),
            'environment': current_app.config.get('ENV', 'development')
        }
    })

@admin_bp.route('/api/admin/run-smoke-tests', methods=['POST'])
@login_required
def run_smoke_tests():
    """
    Executes in-process smoke tests verifying critical system components
    and returns a test report for the UI.
    """
    results = []

    # Test 1: Database read
    t0 = time.time()
    try:
        db.session.execute(db.text('SELECT 1'))
        results.append({'test': 'Database Connectivity', 'status': 'PASSED', 'duration_ms': round((time.time() - t0) * 1000, 1)})
    except Exception as e:
        results.append({'test': 'Database Connectivity', 'status': 'FAILED', 'error': str(e)})

    # Test 2: In-Memory / Redis Cache set & get
    from services.cache_service import cache_set, cache_get
    t0 = time.time()
    try:
        cache_set('smoke_test_key', {'val': 42}, ttl=60)
        ret = cache_get('smoke_test_key')
        assert ret and ret.get('val') == 42
        results.append({'test': 'Cache Operations (Set/Get)', 'status': 'PASSED', 'duration_ms': round((time.time() - t0) * 1000, 1)})
    except Exception as e:
        results.append({'test': 'Cache Operations', 'status': 'FAILED', 'error': str(e)})

    # Test 3: Comfort score calculation
    from services.ai_service import calculate_comfort_score
    t0 = time.time()
    try:
        score = calculate_comfort_score(22, 50, 3.0, 1)
        assert score['score'] >= 85
        results.append({'test': 'Comfort Score Engine', 'status': 'PASSED', 'duration_ms': round((time.time() - t0) * 1000, 1)})
    except Exception as e:
        results.append({'test': 'Comfort Score Engine', 'status': 'FAILED', 'error': str(e)})

    # Test 4: City extraction safety
    from services.ai_service import extract_cities_from_text
    t0 = time.time()
    try:
        res = extract_cities_from_text("What should I wear for work?", default_city="Bengaluru")
        assert res == ["Bengaluru"]
        results.append({'test': 'City Extraction Stop-Word Filter', 'status': 'PASSED', 'duration_ms': round((time.time() - t0) * 1000, 1)})
    except Exception as e:
        results.append({'test': 'City Extraction', 'status': 'FAILED', 'error': str(e)})

    # Test 5: Unsplash Curated Fallbacks
    from services.unsplash_service import get_fallback_photo
    t0 = time.time()
    try:
        photo = get_fallback_photo('rain')
        assert photo['source'] == 'Unsplash' and 'images.unsplash.com' in photo['url']
        results.append({'test': 'Unsplash Curated Mood Fallback', 'status': 'PASSED', 'duration_ms': round((time.time() - t0) * 1000, 1)})
    except Exception as e:
        results.append({'test': 'Unsplash Fallback', 'status': 'FAILED', 'error': str(e)})

    total_passed = sum(1 for r in results if r['status'] == 'PASSED')
    return jsonify({
        'success': True,
        'summary': f"{total_passed}/{len(results)} tests passed",
        'all_passed': total_passed == len(results),
        'results': results
    })
