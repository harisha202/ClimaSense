import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

def get_background_image(city, weather_description):
    """Calls Unsplash search API for place-specific image, with Wikipedia REST API fallback"""
    # Cache by city name for instant repeat lookups
    cache_key = f"bg_{city.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('UNSPLASH_API_KEY')
    if api_key:
        # Single direct query for the searched city for maximum speed and landmark relevance
        url = f"https://api.unsplash.com/search/photos?query={city}&orientation=landscape&order_by=relevant&per_page=1"
        headers = {"Authorization": f"Client-ID {api_key}"}
        try:
            resp = requests.get(url, headers=headers, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('results') and len(data['results']) > 0:
                    img_url = data['results'][0]['urls']['regular']
                    cache_set(cache_key, img_url, ttl=86400) # cache for 24 hours
                    return img_url
        except Exception as e:
            current_app.logger.error(f"Error fetching unsplash image for {city}: {e}")

    # Fallback: Free Wikipedia REST API for the searched place
    try:
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(city)}"
        wiki_resp = requests.get(wiki_url, headers={"User-Agent": "ClimaSense/1.0"}, timeout=1.8)
        if wiki_resp.status_code == 200:
            wiki_data = wiki_resp.json()
            img_url = (wiki_data.get('originalimage') or wiki_data.get('thumbnail') or {}).get('source')
            if img_url:
                cache_set(cache_key, img_url, ttl=86400) # cache for 24 hours
                return img_url
    except Exception as e:
        current_app.logger.error(f"Error fetching Wikipedia image for {city}: {e}")

    return _fallback_image()

def _fallback_image():
    return "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=1000&auto=format&fit=crop"
