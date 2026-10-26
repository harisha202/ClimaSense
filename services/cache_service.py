import json
import time
from flask import current_app
from extensions import get_redis_client

# In-memory dictionary for fallback when Redis isn't running
_fallback_cache = {}
MAX_IN_MEMORY_ENTRIES = 1000

# Cache diagnostic counters
_cache_stats = {
    'hits': 0,
    'misses': 0,
    'sets': 0
}

def get_cache_stats():
    """Returns runtime cache hit/miss diagnostic metrics."""
    total = _cache_stats['hits'] + _cache_stats['misses']
    hit_rate = round((_cache_stats['hits'] / total * 100), 1) if total > 0 else 100.0
    client = get_redis_client()
    return {
        'hits': _cache_stats['hits'],
        'misses': _cache_stats['misses'],
        'sets': _cache_stats['sets'],
        'hit_rate_pct': hit_rate,
        'entries_count': len(_fallback_cache) if not client else 'Managed by Redis'
    }

def _clean_fallback_cache():
    """Removes expired entries and enforces max size limit."""
    global _fallback_cache
    now = time.time()
    # Remove expired
    _fallback_cache = {k: v for k, v in _fallback_cache.items() if v['expires_at'] > now}
    # Enforce capacity if still over limit
    if len(_fallback_cache) > MAX_IN_MEMORY_ENTRIES:
        # Sort by expiration time and keep the newest half
        sorted_keys = sorted(_fallback_cache.keys(), key=lambda k: _fallback_cache[k]['expires_at'])
        for k in sorted_keys[:len(_fallback_cache) - MAX_IN_MEMORY_ENTRIES]:
            del _fallback_cache[k]

def cache_get(key):
    """Checks cache for a value. Returns dict, list, primitive, or None."""
    global _fallback_cache
    client = get_redis_client()
    if not client:
        if key in _fallback_cache:
            entry = _fallback_cache[key]
            if time.time() < entry['expires_at']:
                _cache_stats['hits'] += 1
                return entry['data']
            else:
                del _fallback_cache[key]
        _cache_stats['misses'] += 1
        return None
        
    try:
        val = client.get(key)
        if val:
            _cache_stats['hits'] += 1
            return json.loads(val)
        _cache_stats['misses'] += 1
    except Exception as e:
        current_app.logger.warning(f"Redis get error for {key}: {e}")
        _cache_stats['misses'] += 1
    return None

def cache_set(key, value, ttl=None):
    """Stores a value in Redis with a TTL (time-to-live in seconds)."""
    if ttl is None:
        ttl = current_app.config.get('CACHE_TTL_SECONDS', 300)
        
    _cache_stats['sets'] += 1
    client = get_redis_client()

    if not client:
        _clean_fallback_cache()
        _fallback_cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl
        }
        return True
        
    try:
        client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        current_app.logger.warning(f"Redis set error for {key}: {e}")
        # Fall back to in-memory
        _fallback_cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl
        }
        return False

def cache_delete(key):
    """Removes a cached value."""
    client = get_redis_client()
    if not client:
        if key in _fallback_cache:
            del _fallback_cache[key]
        return True
        
    try:
        client.delete(key)
        return True
    except Exception as e:
        current_app.logger.warning(f"Redis delete error for {key}: {e}")
        return False
