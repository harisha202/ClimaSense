import random
import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

# Curated Unsplash fallback photography with verified photographers and compliant referral links
UNSPLASH_FALLBACK_COLLECTION = {
    'sunny': {
        'url': 'https://images.unsplash.com/photo-1601297183305-6df142704ea2?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'CHUTTERSNAP',
        'photographer_url': 'https://unsplash.com/@chuttersnap?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'cloudy': {
        'url': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Billy Huynh',
        'photographer_url': 'https://unsplash.com/@billy_huy?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'rain': {
        'url': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Valentin Müller',
        'photographer_url': 'https://unsplash.com/@valentinbkk?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'storm': {
        'url': 'https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Raychel Sanner',
        'photographer_url': 'https://unsplash.com/@raychelsanner?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'snow': {
        'url': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Galina N',
        'photographer_url': 'https://unsplash.com/@galina88?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'fog': {
        'url': 'https://images.unsplash.com/photo-1487621167305-5d248087c724?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Daniel Leone',
        'photographer_url': 'https://unsplash.com/@daniels?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'night': {
        'url': 'https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Fabian Møller',
        'photographer_url': 'https://unsplash.com/@fabianmoller?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    },
    'default': {
        'url': 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Eberhard Grossgasteiger',
        'photographer_url': 'https://unsplash.com/@eberhardgross?utm_source=ClimaSense&utm_medium=referral',
        'source': 'Unsplash',
        'is_fallback': True
    }
}

# Curated rotating scenic landmarks, destinations, beaches & architecture fallbacks
UNSPLASH_SCENIC_FALLBACKS = [
    {
        'url': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Bailey Zindel',
        'photographer_url': 'https://unsplash.com/@baileyzindel?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Yosemite National Park Valley Landscape',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Jezael Melgoza',
        'photographer_url': 'https://unsplash.com/@jezael?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Tokyo Tower & Urban Skyline',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Chris Karidis',
        'photographer_url': 'https://unsplash.com/@chriskaridis?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Parisian Classical Architecture & Eiffel Tower',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Sean Oulashin',
        'photographer_url': 'https://unsplash.com/@oulashin?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Tropical Coastal Beach & Turquoise Ocean',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Kalon Egodage',
        'photographer_url': 'https://unsplash.com/@kalon_egodage?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Majestic Alpine Mountain Peaks',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Oliver Niblett',
        'photographer_url': 'https://unsplash.com/@oliver_niblett?utm_source=ClimaSense&utm_medium=referral',
        'title': 'New York Manhattan Skyline at Twilight',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Constantinos Kollias',
        'photographer_url': 'https://unsplash.com/@ckollias?utm_source=ClimaSense&utm_medium=referral',
        'title': 'Santorini Mediterranean Cliffside Architecture',
        'source': 'Unsplash',
        'is_fallback': True
    },
    {
        'url': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=2400&q=90',
        'photographer_name': 'Luke Stackpoole',
        'photographer_url': 'https://unsplash.com/@withluke?utm_source=ClimaSense&utm_medium=referral',
        'title': 'London Historic River Thames & Tower Bridge',
        'source': 'Unsplash',
        'is_fallback': True
    }
]


# Curated city-specific fallback photography for prominent destinations
CITY_FALLBACK_COLLECTION = {
    'delhi': [
        {
            'url': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Sylwia Bartyzel',
            'photographer_url': 'https://unsplash.com/@sylviagb?utm_source=ClimaSense&utm_medium=referral',
            'title': 'India Gate Landmark Delhi',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Delhi'
        },
        {
            'url': 'https://images.unsplash.com/photo-1598324789736-4861f89564a0?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Rishabh Sharma',
            'photographer_url': 'https://unsplash.com/@rishidk?utm_source=ClimaSense&utm_medium=referral',
            'title': 'Humayuns Tomb Delhi Heritage Architecture',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Delhi'
        }
    ],
    'new delhi': [
        {
            'url': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Sylwia Bartyzel',
            'photographer_url': 'https://unsplash.com/@sylviagb?utm_source=ClimaSense&utm_medium=referral',
            'title': 'India Gate Landmark Delhi',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Delhi'
        }
    ],
    'tokyo': [
        {
            'url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Jezael Melgoza',
            'photographer_url': 'https://unsplash.com/@jezael?utm_source=ClimaSense&utm_medium=referral',
            'title': 'Tokyo Tower & Urban Skyline',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Tokyo'
        },
        {
            'url': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Yu Kato',
            'photographer_url': 'https://unsplash.com/@yukato?utm_source=ClimaSense&utm_medium=referral',
            'title': 'Shinjuku Tokyo City Neon & Skyline',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Tokyo'
        }
    ],
    'london': [
        {
            'url': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Luke Stackpoole',
            'photographer_url': 'https://unsplash.com/@withluke?utm_source=ClimaSense&utm_medium=referral',
            'title': 'London Historic River Thames & Tower Bridge',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'London'
        }
    ],
    'paris': [
        {
            'url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Chris Karidis',
            'photographer_url': 'https://unsplash.com/@chriskaridis?utm_source=ClimaSense&utm_medium=referral',
            'title': 'Parisian Classical Architecture & Eiffel Tower',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Paris'
        }
    ],
    'new york': [
        {
            'url': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Oliver Niblett',
            'photographer_url': 'https://unsplash.com/@oliver_niblett?utm_source=ClimaSense&utm_medium=referral',
            'title': 'New York Manhattan Skyline at Twilight',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'New York'
        }
    ],
    'bengaluru': [
        {
            'url': 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=2400&q=90',
            'photographer_name': 'Naveen Kumar',
            'photographer_url': 'https://unsplash.com/@naveenk?utm_source=ClimaSense&utm_medium=referral',
            'title': 'Vidhana Soudha Bengaluru Architecture',
            'source': 'Unsplash',
            'is_fallback': True,
            'city': 'Bengaluru'
        }
    ]
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
    res = dict(photo)
    res['is_fallback'] = True
    return res

def get_rotating_fallback_photo():
    """Rotates through curated famous landmarks, destinations, beaches and mountains."""
    idx = cache_get('scenic_fallback_index') or 0
    photo = dict(UNSPLASH_SCENIC_FALLBACKS[idx % len(UNSPLASH_SCENIC_FALLBACKS)])
    cache_set('scenic_fallback_index', idx + 1, ttl=86400)
    photo['is_fallback'] = True
    return photo

def _fetch_unsplash_search(query, api_key, per_page=15):
    """
    Executes an authenticated Unsplash search query.
    Returns a list of parsed photo objects or None if failed/empty.
    """
    headers = {
        "Authorization": f"Client-ID {api_key}",
        "Accept-Version": "v1"
    }
    url = (
        f"https://api.unsplash.com/search/photos?"
        f"query={requests.utils.quote(query)}"
        f"&orientation=landscape"
        f"&content_filter=high"
        f"&per_page={per_page}"
    )

    try:
        resp = requests.get(url, headers=headers, timeout=5.0)
        remaining = resp.headers.get('X-Ratelimit-Remaining')
        if remaining is not None:
            try:
                rem_val = int(remaining)
                current_app.logger.info(f"Unsplash API Rate Limit Remaining: {rem_val}")
                if rem_val <= 1:
                    current_app.logger.warning("Unsplash API rate limit nearly exhausted.")
            except (ValueError, TypeError):
                pass

        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            if results:
                photos = []
                for item in results:
                    raw_url = item['urls'].get('raw')
                    if raw_url:
                        img_url = f"{raw_url}&auto=format&fit=crop&w=2400&q=90"
                    else:
                        img_url = item['urls'].get('full') or item['urls'].get('regular')
                    user = item.get('user', {})
                    photographer_name = user.get('name') or user.get('username') or 'Unsplash Community'
                    photographer_url = user.get('links', {}).get('html', 'https://unsplash.com')
                    title = item.get('alt_description') or item.get('description') or query
                    photos.append({
                        'url': img_url,
                        'photographer_name': photographer_name,
                        'photographer_url': f"{photographer_url}?utm_source=ClimaSense&utm_medium=referral",
                        'title': title,
                        'source': 'Unsplash',
                        'is_fallback': False
                    })
                return photos
        elif resp.status_code in (401, 403):
            current_app.logger.warning(f"Unsplash API auth error ({resp.status_code}): check key validity.")
        elif resp.status_code == 429:
            current_app.logger.warning("Unsplash API rate limit exceeded (HTTP 429).")
    except requests.exceptions.Timeout:
        current_app.logger.warning(f"Unsplash API timeout while requesting query '{query}'.")
    except Exception as e:
        current_app.logger.error(f"Unsplash API connection failure: {e}")
        
    return None

def fetch_city_photos_from_unsplash(city, country='', api_key=None):
    """
    Fetches high-resolution photographs specifically matching the searched city,
    incorporating city landmarks, skyline, and regional architecture.
    """
    if not api_key:
        return None
        
    clean_city = city.strip()
    if not clean_city:
        return None
        
    # Primary targeted query: city name with location context and landscape/skyline
    query = f"{clean_city} {country} city skyline landmarks architecture".strip()
    photos = _fetch_unsplash_search(query, api_key, per_page=15)
    
    # Secondary broader query if targeted query had 0 results
    if not photos:
        broader_query = f"{clean_city} city"
        photos = _fetch_unsplash_search(broader_query, api_key, per_page=10)
        
    return photos

def get_background_image(city='', weather_description='', country=''):
    """
    City-matched dynamic background service.
    - Searches Unsplash specifically for the city requested by current weather search.
    - Uses country/region context when available to reduce ambiguous results.
    - Caches a pool of relevant photographs per city to optimize API quota.
    - Rotates to another relevant photograph for the same city on repeated searches.
    - Falls back gracefully to curated Unsplash photography with is_fallback: True
      if the API key is missing, rate-limited, or no city-specific photo is found.
    """
    api_key = current_app.config.get('UNSPLASH_API_KEY')
    clean_city = (city or '').strip()

    if api_key and clean_city:
        # Cache key unique to the searched city
        cache_key_city = f"unsplash_city_pool_{clean_city.lower()}"
        pool = cache_get(cache_key_city)
        
        if not pool:
            pool = fetch_city_photos_from_unsplash(clean_city, country=country, api_key=api_key)
            if pool:
                # Cache results for this city for 2 hours
                cache_set(cache_key_city, pool, ttl=7200)
                
        if pool and len(pool) > 0:
            # Rotate through the city's matching photos on repeated searches
            idx_key = f"unsplash_city_idx_{clean_city.lower()}"
            idx = cache_get(idx_key) or 0
            photo = dict(pool[idx % len(pool)])
            cache_set(idx_key, idx + 1, ttl=7200)
            photo['is_fallback'] = False
            photo['city'] = clean_city
            return photo

    # If no city provided (e.g. general default on home page) but API key present:
    if api_key and not clean_city:
        cache_key_general = 'unsplash_general_scenic_pool'
        pool = cache_get(cache_key_general)
        if not pool:
            pool = _fetch_unsplash_search("famous landmarks scenic destinations architecture", api_key, per_page=20)
            if pool:
                cache_set(cache_key_general, pool, ttl=86400)
        if pool and len(pool) > 0:
            idx = cache_get('unsplash_general_idx') or 0
            photo = dict(pool[idx % len(pool)])
            cache_set('unsplash_general_idx', idx + 1, ttl=86400)
            photo['is_fallback'] = False
            return photo

    # Graceful curated fallback: check if city has dedicated curated photography
    if clean_city:
        city_lower = clean_city.lower()
        for k, photos in CITY_FALLBACK_COLLECTION.items():
            if k in city_lower or city_lower in k:
                idx_key = f"curated_city_idx_{k}"
                idx = cache_get(idx_key) or 0
                photo = dict(photos[idx % len(photos)])
                cache_set(idx_key, idx + 1, ttl=7200)
                photo['is_fallback'] = True
                photo['city'] = clean_city
                return photo

    # Graceful curated fallback when no city match, network error, or no matching results
    if weather_description:
        mood = determine_weather_mood(weather_description)
        photo = get_fallback_photo(mood)
    else:
        photo = get_rotating_fallback_photo()
        
    photo['is_fallback'] = True
    return photo
