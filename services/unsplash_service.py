import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

def get_background_image(city, weather_description):
    """Calls Unsplash search API, returns the best-matching photo URL"""
    cache_key = f"bg_{city.lower()}_{weather_description.replace(' ', '_')}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config['UNSPLASH_API_KEY']
    if not api_key:
        return _fallback_image()

    query = f"{city} city landmark {weather_description}"
    url = f"https://api.unsplash.com/search/photos?query={query}&orientation=landscape&order_by=relevant&per_page=1"
    headers = {"Authorization": f"Client-ID {api_key}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('results'):
                img_url = data['results'][0]['urls']['regular']
                cache_set(cache_key, img_url, ttl=3600)  # cache images longer
                return img_url
    except Exception as e:
        current_app.logger.error(f"Error fetching unsplash image for {query}: {e}")
        
    return _fallback_image()

def _fallback_image():
    return "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=1000&auto=format&fit=crop"
