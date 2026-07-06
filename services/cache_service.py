import json
from extensions import redis_client
from flask import current_app
import time

# In-memory dictionary for fallback when Redis isn't running
_fallback_cache = {}

def cache_get(key):
    """Checks Redis for a cached value. Returns dict or None."""
    if not redis_client:
        # Fallback cache logic
        if key in _fallback_cache:
            entry = _fallback_cache[key]
            if time.time() < entry['expires_at']:
                return entry['data']
            else:
                del _fallback_cache[key]
        return None
        
    try:
        val = redis_client.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        current_app.logger.warning(f"Redis get error for {key}: {e}")
    return None

def cache_set(key, value, ttl=None):
    """Stores a value in Redis with a TTL (time-to-live in seconds)."""
    if ttl is None:
        ttl = current_app.config.get('CACHE_TTL_SECONDS', 300)
        
    if not redis_client:
        # Fallback cache logic
        _fallback_cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl
        }
        return True
        
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        current_app.logger.warning(f"Redis set error for {key}: {e}")
        return False

def cache_delete(key):
    """Removes a cached value."""
    if not redis_client:
        if key in _fallback_cache:
            del _fallback_cache[key]
        return True
        
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        current_app.logger.warning(f"Redis delete error for {key}: {e}")
        return False
