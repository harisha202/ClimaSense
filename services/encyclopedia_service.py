import re
import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

WIKIPEDIA_CACHE_TTL = 604800  # 7 days cache for static municipal summaries

def clean_extract_to_concise_summary(text, min_chars=250, max_chars=400):
    """
    Trims a full extract to approximately 250-400 characters,
    stopping neatly at a sentence end if possible.
    """
    if not text:
        return ""
        
    cleaned = re.sub(r'\s+', ' ', text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
        
    # Attempt to cut at a sentence boundary between min_chars and max_chars
    sub = cleaned[:max_chars + 1]
    last_period = sub.rfind('.')
    if last_period >= min_chars:
        return sub[:last_period + 1].strip()
        
    # Otherwise cut at the last word within limit and append ellipsis
    last_space = sub[:max_chars].rfind(' ')
    if last_space > 0:
        return sub[:last_space].rstrip(',;:') + '...'
    return sub[:max_chars] + '...'

def fetch_wikipedia_summary(city, country=''):
    """
    Retrieves authentic, concise encyclopedic summary from the official Wikipedia REST API.
    Disambiguates with country when available.
    Returns structured dict with city name, short summary, source attribution, and article link.
    """
    clean_city = (city or '').strip()
    if not clean_city:
        return {
            'success': False,
            'city': '',
            'title': 'Unknown City',
            'summary': 'City name was not provided.',
            'article_url': 'https://en.wikipedia.org',
            'thumbnail': None,
            'source': 'Wikipedia',
            'is_available': False
        }

    cache_key = f"wiki_summary_{clean_city.lower()}_{country.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    headers = {"User-Agent": "ClimaSense/2.0 (educational/weather dashboard; contact@climasense.local)"}
    
    # Titles to attempt in order of specificity
    candidates = []
    if country:
        candidates.append(f"{clean_city},_{country}")
    candidates.append(clean_city)
    
    summary_data = None
    selected_title = clean_city

    for cand in candidates:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(cand)}"
            resp = requests.get(url, headers=headers, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                # Ensure it is a standard page, not an empty or generic disambiguation
                if data.get('type') != 'disambiguation' and data.get('extract'):
                    summary_data = data
                    selected_title = data.get('title', cand)
                    break
        except Exception as e:
            current_app.logger.warning(f"Wikipedia REST API lookup error for {cand}: {e}")

    # Fallback to MediaWiki search API if direct summary failed
    if not summary_data:
        try:
            search_query = f"{clean_city} {country} city".strip()
            search_url = (
                f"https://en.wikipedia.org/w/api.php?action=query&list=search"
                f"&srsearch={requests.utils.quote(search_query)}&format=json&utf8=1&srlimit=1"
            )
            s_resp = requests.get(search_url, headers=headers, timeout=4.0)
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                search_results = s_data.get('query', {}).get('search', [])
                if search_results:
                    first_title = search_results[0].get('title')
                    if first_title:
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(first_title)}"
                        sum_resp = requests.get(sum_url, headers=headers, timeout=4.0)
                        if sum_resp.status_code == 200:
                            summary_data = sum_resp.json()
                            selected_title = first_title
        except Exception as e:
            current_app.logger.warning(f"Wikipedia Search API error for {clean_city}: {e}")

    if summary_data and summary_data.get('extract'):
        raw_extract = summary_data.get('extract', '')
        concise = clean_extract_to_concise_summary(raw_extract, min_chars=220, max_chars=400)
        article_url = summary_data.get('content_urls', {}).get('desktop', {}).get('page') or f"https://en.wikipedia.org/wiki/{requests.utils.quote(selected_title)}"
        thumb = summary_data.get('thumbnail', {}).get('source')
        
        result = {
            'success': True,
            'city': clean_city,
            'title': selected_title,
            'summary': concise,
            'full_extract': raw_extract,
            'article_url': article_url,
            'thumbnail': thumb,
            'source': 'Wikipedia',
            'is_available': True
        }
        cache_set(cache_key, result, ttl=WIKIPEDIA_CACHE_TTL)
        return result

    # Honest unavailable state if no authentic Wikipedia article could be sourced
    unavailable_result = {
        'success': False,
        'city': clean_city,
        'title': clean_city,
        'summary': f"City information for {clean_city} is currently unavailable on Wikipedia.",
        'article_url': f"https://en.wikipedia.org/wiki/Special:Search?search={requests.utils.quote(clean_city)}",
        'thumbnail': None,
        'source': 'Wikipedia',
        'is_available': False
    }
    cache_set(cache_key, unavailable_result, ttl=3600)
    return unavailable_result

def get_city_encyclopedia(city, country=''):
    """
    Backwards compatibility wrapper returning structured concise Wikipedia city information.
    """
    info = fetch_wikipedia_summary(city, country=country)
    return {
        'city': info.get('city', city),
        'title': info.get('title', city),
        'summary': info.get('summary', ''),
        'lead_paragraph': info.get('summary', ''),
        'article_url': info.get('article_url', 'https://en.wikipedia.org'),
        'source': 'Wikipedia',
        'is_available': info.get('is_available', False),
        'sections': [],
        'word_count': len(info.get('summary', '').split()),
        'reading_time_minutes': 1
    }
