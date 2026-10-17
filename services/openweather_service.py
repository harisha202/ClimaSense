import time
import random
import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

def _safe_request(url, timeout=8, max_retries=2):
    """
    Executes an HTTP GET with bounded retries, exponential backoff,
    and jitter for transient server/network failures. Permanent client
    errors (401, 403, 404) are returned immediately without retrying.
    """
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp
            # Permanent client errors: don't retry
            if resp.status_code in (401, 403, 404):
                return resp
            # Transient 5xx server errors: retry with backoff
            if resp.status_code >= 500 and attempt < max_retries:
                time.sleep(0.2 * (2 ** attempt) + random.uniform(0.05, 0.15))
                continue
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < max_retries:
                time.sleep(0.2 * (2 ** attempt) + random.uniform(0.05, 0.15))
                continue
            return None
        except Exception:
            return None
    return None

def get_current_weather(city):
    """Current weather by city name"""
    cache_key = f"weather_city_{city.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        resp = _safe_request(url, timeout=8)
        if resp and resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching weather for {city}: {e}")
    return None

def get_weather_by_coords(lat, lon):
    """Current weather by coordinates"""
    cache_key = f"weather_coords_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    try:
        resp = _safe_request(url, timeout=8)
        if resp and resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching weather for coords {lat}, {lon}: {e}")
    return None

def get_forecast(city):
    """5-day/3-hour forecast"""
    cache_key = f"forecast_city_{city.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}"
    try:
        resp = _safe_request(url, timeout=8)
        if resp and resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching forecast for {city}: {e}")
    return None

def get_aqi(lat, lon):
    """Air quality index"""
    cache_key = f"aqi_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        resp = _safe_request(url, timeout=8)
        if resp and resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching AQI for {lat}, {lon}: {e}")
    return None

def get_uv_index(lat, lon):
    """UV index retrieval with fallback estimation"""
    cache_key = f"uvi_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
        return {'value': 5.0}

    url = f"https://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={api_key}"
    try:
        resp = _safe_request(url, timeout=5)
        if resp and resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching UVI for {lat}, {lon}: {e}")
    
    # Fallback estimation based on cloud cover
    weather = get_weather_by_coords(lat, lon)
    uvi_val = 5.0
    if weather and 'clouds' in weather:
        clouds = weather.get('clouds', {}).get('all', 50)
        uvi_val = round(max(1.0, 9.0 * (1.0 - clouds / 150.0)), 1)
    data = {'value': uvi_val}
    cache_set(cache_key, data)
    return data

def get_alerts(lat, lon):
    """Severe weather alerts using condition threshold detection"""
    cache_key = f"alerts_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    weather = get_weather_by_coords(lat, lon)
    if weather and 'weather' in weather and len(weather['weather']) > 0:
        desc = weather['weather'][0]['description'].lower()
        temp = weather['main']['temp']
        wind = weather['wind']['speed']
        rain_1h = weather.get('rain', {}).get('1h', 0)
        
        alerts = []
        if 'flood' in desc or rain_1h >= 15 or 'extreme rain' in desc:
            alerts.append({'event': 'Flood Warning', 'description': 'High rainfall intensity detected. Risk of flash flooding in low-lying areas.'})
        elif 'storm' in desc or 'thunder' in desc:
            alerts.append({'event': 'Severe Thunderstorm', 'description': 'Thunderstorms detected in the area. Take caution.'})
        elif 'hurricane' in desc or 'tornado' in desc:
            alerts.append({'event': 'Extreme Weather Warning', 'description': 'Extreme weather conditions detected. Seek shelter immediately.'})
        elif 'heavy rain' in desc:
            alerts.append({'event': 'Heavy Rainfall', 'description': 'Heavy rain detected. Risk of localized flooding.'})
        elif temp > 40:
            alerts.append({'event': 'Extreme Heat Advisory', 'description': 'Temperatures exceed 40°C. Stay hydrated and avoid outdoor activities.'})
        elif wind > 20: # m/s (approx 72 km/h)
            alerts.append({'event': 'High Wind Warning', 'description': 'Dangerous high winds detected. Secure loose objects.'})
            
        data = {'alerts': alerts}
        cache_set(cache_key, data)
        return data
        
    return None
