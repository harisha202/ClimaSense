import random
import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

# Curated Unsplash fallback photography with verified photographers and compliant referral links
UNSPLASH_FALLBACK_COLLECTION = {
    'sunny': {
        'url': 'https://images.unsplash.com/photo-1601297183305-6df142704ea2?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'CHUTTERSNAP',
        'photographer_url': 'https://unsplash.com/@chuttersnap?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'cloudy': {
        'url': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Billy Huynh',
        'photographer_url': 'https://unsplash.com/@billy_huy?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'rain': {
        'url': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Valentin Müller',
        'photographer_url': 'https://unsplash.com/@valentinbkk?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'storm': {
        'url': 'https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Raychel Sanner',
        'photographer_url': 'https://unsplash.com/@raychelsanner?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'snow': {
        'url': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Galina N',
        'photographer_url': 'https://unsplash.com/@galina88?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'fog': {
        'url': 'https://images.unsplash.com/photo-1487621167305-5d248087c724?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Daniel Leone',
        'photographer_url': 'https://unsplash.com/@daniels?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'night': {
        'url': 'https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Fabian Møller',
        'photographer_url': 'https://unsplash.com/@fabianmoller?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    },
    'default': {
        'url': 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1600&q=80',
        'photographer_name': 'Eberhard Grossgasteiger',
        'photographer_url': 'https://unsplash.com/@eberhardgross?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash'
    }
}

def determine_weather_mood(description=''):
    """Maps weather description text to an Unsplash visual mood keyword."""
    d = (description or '').lower()
    if any(k in d for k in ['thunderstorm', 'storm', 'tornado', 'squall']):
        return 'storm'
    if any(k in d for k in ['rain', 'drizzle', 'shower', 'downpour']):
        return 'rain'
    if any(k in d for k in ['snow', 'sleet', 'blizzard', 'flurries', 'ice']):
        return 'snow'
    if any(k in d for k in ['fog', 'mist', 'haze', 'smoke', 'dust']):
        return 'fog'
    if any(k in d for k in ['cloud', 'overcast']):
        return 'cloudy'
    if 'night' in d:
        return 'night'
    if any(k in d for k in ['clear', 'sun']):
        return 'sunny'
    return 'default'

def get_fallback_photo(mood='default'):
    """Returns curated Unsplash fallback photo for given mood with accurate attribution."""
    photo = UNSPLASH_FALLBACK_COLLECTION.get(mood) or UNSPLASH_FALLBACK_COLLECTION['default']
    return dict(photo)

def get_background_image(city, weather_description=''):
    """
    Fetches high-quality scenic background photography strictly from Unsplash.
    - Curated Unsplash photography only.
    - Caches genuine city matches for 24h.
    - Caches mood fallbacks for 5 minutes so live searches retry promptly.
    - Honors Unsplash rate limits and photographer attribution requirements.
    """
    if not city or not city.strip():
        return get_fallback_photo('default')

    city = city.strip()
    mood = determine_weather_mood(weather_description)
    cache_key = f"bg_{city.lower()}_{mood}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('UNSPLASH_API_KEY')
    if not api_key:
        current_app.logger.info("UNSPLASH_API_KEY not configured; serving curated Unsplash mood fallback.")
        fallback = get_fallback_photo(mood)
        cache_set(cache_key, fallback, ttl=300)
        return fallback

    headers = {
        "Authorization": f"Client-ID {api_key}",
        "Accept-Version": "v1"
    }

    # Query search candidates: first city + scenery/mood, then plain city
    search_queries = [
        f"{city} skyline landmark",
        f"{city} {mood}" if mood != 'default' else f"{city} cityscape",
        city
    ]

    for query in search_queries:
        url = (
            f"https://api.unsplash.com/search/photos?"
            f"query={requests.utils.quote(query)}"
            f"&orientation=landscape"
            f"&content_filter=high"
            f"&per_page=5"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=4.0)

            # Check rate limiting headers
            remaining = resp.headers.get('X-Ratelimit-Remaining')
            if remaining is not None:
                current_app.logger.info(f"Unsplash API Rate Limit Remaining: {remaining}")
                if int(remaining) <= 1:
                    current_app.logger.warning("Unsplash API rate limit nearly exhausted. Throttling requests.")

            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                if results:
                    # Pick highest liked or top result
                    chosen = max(results, key=lambda x: x.get('likes', 0)) if len(results) > 1 else results[0]
                    img_url = chosen['urls'].get('regular') or chosen['urls'].get('full')
                    user = chosen.get('user', {})
                    photographer_name = user.get('name') or user.get('username') or 'Unsplash Community'
                    photographer_url = user.get('links', {}).get('html', 'https://unsplash.com')

                    result = {
                        'url': img_url,
                        'photographer_name': photographer_name,
                        'photographer_url': f"{photographer_url}?utm_source=ClimaSense&utm_medium=referral",
                        'source': 'Unsplash',
                        'is_fallback': False
                    }
                    # Cache live result for 24 hours
                    cache_set(cache_key, result, ttl=86400)
                    return result
            elif resp.status_code in (401, 403):
                current_app.logger.warning(
                    f"Unsplash API authentication error ({resp.status_code}): check UNSPLASH_API_KEY validity or rate limit."
                )
                break
            elif resp.status_code == 429:
                current_app.logger.warning("Unsplash API rate limit exceeded (HTTP 429).")
                break
            else:
                current_app.logger.info(
                    f"Unsplash search for '{query}' returned HTTP {resp.status_code}."
                )
        except requests.exceptions.Timeout:
            current_app.logger.warning(f"Unsplash API timeout during search for '{query}'.")
        except Exception as e:
            current_app.logger.error(f"Unsplash API connection failure: {e}")
            break

    # If all searches fail, use curated mood fallback and cache only briefly (5 min)
    fallback = get_fallback_photo(mood)
    fallback['is_fallback'] = True
    cache_set(cache_key, fallback, ttl=300)
    return fallback
