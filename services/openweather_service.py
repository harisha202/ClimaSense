import requests
from flask import current_app
from services.cache_service import cache_get, cache_set

def get_current_weather(city):
    """Current weather by city name"""
    cache_key = f"weather_city_{city.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config['OPENWEATHER_API_KEY']
    if not api_key:
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
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

    api_key = current_app.config['OPENWEATHER_API_KEY']
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
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

    api_key = current_app.config['OPENWEATHER_API_KEY']
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
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

    api_key = current_app.config['OPENWEATHER_API_KEY']
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching AQI for {lat}, {lon}: {e}")
    return None

def get_alerts(lat, lon):
    """Severe weather alerts using One Call API"""
    cache_key = f"alerts_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    api_key = current_app.config['OPENWEATHER_API_KEY']
    # Free tier note: One Call API 3.0 requires separate subscription, using generic alerts logic or mock if needed
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,daily&appid={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            cache_set(cache_key, data)
            return data
    except Exception as e:
        current_app.logger.error(f"Error fetching alerts for {lat}, {lon}: {e}")
    return None
