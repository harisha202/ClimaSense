import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

def get_background_image(city, weather_description=''):
    """
    Calls Unsplash search API for place-specific image with full photographer attribution,
    falling back gracefully to the Wikipedia REST API or default curated photography.
    """
    cache_key = f"bg_{city.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('UNSPLASH_API_KEY')
    if api_key:
        url = f"https://api.unsplash.com/search/photos?query={requests.utils.quote(city)}&orientation=landscape&order_by=relevant&per_page=1"
        headers = {"Authorization": f"Client-ID {api_key}"}
        try:
            resp = requests.get(url, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('results') and len(data['results']) > 0:
                    photo = data['results'][0]
                    img_url = photo['urls']['regular']
                    user = photo.get('user', {})
                    photographer_name = user.get('name', 'Unsplash Community')
                    photographer_url = user.get('links', {}).get('html', 'https://unsplash.com')
                    
                    result = {
                        'url': img_url,
                        'photographer_name': photographer_name,
                        'photographer_url': f"{photographer_url}?utm_source=ClimaSense&utm_medium=referral",
                        'source': 'Unsplash'
                    }
                    cache_set(cache_key, result, ttl=86400) # cache for 24 hours
                    return result
        except Exception as e:
            current_app.logger.error(f"Error fetching Unsplash image for {city}: {e}")

    # Fallback: Free Wikipedia REST API for the searched place
    try:
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(city)}"
        wiki_resp = requests.get(wiki_url, headers={"User-Agent": "ClimaSense/1.0"}, timeout=2.0)
        if wiki_resp.status_code == 200:
            wiki_data = wiki_resp.json()
            img_url = (wiki_data.get('originalimage') or wiki_data.get('thumbnail') or {}).get('source')
            if img_url:
                result = {
                    'url': img_url,
                    'photographer_name': 'Wikimedia Commons',
                    'photographer_url': f"https://en.wikipedia.org/wiki/{requests.utils.quote(city)}",
                    'source': 'Wikipedia'
                }
                cache_set(cache_key, result, ttl=86400)
                return result
    except Exception as e:
        current_app.logger.error(f"Error fetching Wikipedia image for {city}: {e}")

    default_result = {
        'url': _fallback_image(),
        'photographer_name': 'Unsplash',
        'photographer_url': 'https://unsplash.com/?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    }
    return default_result

def _fallback_image():
    return "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?q=80&w=1000&auto=format&fit=crop"
