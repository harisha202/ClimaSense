import pytest
import os
from config import Config, ProductionConfig, TestingConfig, DevelopmentConfig
from extensions import get_redis_client
from services.cache_service import cache_set, cache_get, cache_delete, get_cache_stats

def test_testing_config():
    """Verify testing configuration properties."""
    assert TestingConfig.TESTING is True
    assert TestingConfig.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    assert TestingConfig.WTF_CSRF_ENABLED is False

def test_production_config_rejects_weak_secret():
    """Verify production rejects default or short secret key."""
    os.environ['SECRET_KEY'] = 'dev_secret_key'
    with pytest.raises(ValueError) as excinfo:
        ProductionConfig.init_app(None)
    assert "CRITICAL SECURITY ERROR" in str(excinfo.value)

def test_redis_dynamic_access_and_fallback(app):
    """Verify Redis fallback to in-memory cache when Redis server is unreachable."""
    with app.app_context():
        client = get_redis_client()
        # In testing without redis running locally, client is None or gracefully handled
        cache_set('test_key_123', {'weather': 'sunny', 'temp': 22.5}, ttl=60)
        retrieved = cache_get('test_key_123')
        assert retrieved is not None
        assert retrieved['weather'] == 'sunny'
        assert retrieved['temp'] == 22.5
        
        cache_delete('test_key_123')
        assert cache_get('test_key_123') is None
        
        stats = get_cache_stats()
        assert stats['hits'] >= 1
        assert 'hit_rate_pct' in stats

def test_health_endpoint(client):
    """Verify /health returns 200 with complete diagnostics."""
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert 'checks' in data
    assert data['checks']['database']['status'] == 'up'
    assert 'cache' in data['checks']
    assert 'openweather_api' in data['checks']
    assert 'unsplash_api' in data['checks']
    assert 'ai_service' in data['checks']
