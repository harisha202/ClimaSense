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
    """Severe weather alerts using fallback logic (since OneCall is paid)"""
    cache_key = f"alerts_{lat}_{lon}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    # Instead of hitting the paid onecall API, we check current weather for severe conditions
    weather = get_weather_by_coords(lat, lon)
    if weather and 'weather' in weather and len(weather['weather']) > 0:
        desc = weather['weather'][0]['description'].lower()
        temp = weather['main']['temp']
        wind = weather['wind']['speed']
        
        alerts = []
        if 'storm' in desc or 'thunder' in desc:
            alerts.append({'event': 'Severe Thunderstorm', 'description': 'Thunderstorms detected in the area. Take caution.'})
        elif 'hurricane' in desc or 'tornado' in desc:
            alerts.append({'event': 'Extreme Weather Warning', 'description': 'Extreme weather conditions detected. Seek shelter immediately.'})
        elif 'heavy rain' in desc or 'extreme rain' in desc:
            alerts.append({'event': 'Heavy Rainfall', 'description': 'Heavy rain detected. Risk of localized flooding.'})
        elif temp > 40:
            alerts.append({'event': 'Extreme Heat Advisory', 'description': 'Temperatures exceed 40°C. Stay hydrated and avoid outdoor activities.'})
        elif wind > 20: # m/s (approx 72 km/h)
            alerts.append({'event': 'High Wind Warning', 'description': 'Dangerous high winds detected. Secure loose objects.'})
            
        data = {'alerts': alerts}
        cache_set(cache_key, data)
        return data
        
    return None
