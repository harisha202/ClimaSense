import os
import re
import json
import time
from datetime import datetime
import requests
from flask import current_app
from services.cache_service import cache_get, cache_set
from services.openweather_service import get_current_weather, get_forecast, get_aqi, get_uv_index

# In-memory rate limiting dictionary for AI chat
_chat_rate_limits = {}

def calculate_comfort_score(temp, humidity, wind_speed, aqi_val=1):
    """
    Computes a transparent, grounded Comfort Score (0 to 100)
    based on temperature, humidity, wind speed, and air quality.
    """
    score = 100.0
    
    # Temperature penalty (ideal 20°C - 24°C)
    if temp < 18.0:
        score -= min(35.0, (18.0 - temp) * 2.5)
    elif temp > 26.0:
        score -= min(40.0, (temp - 26.0) * 3.0)
        
    # Humidity penalty (ideal 40% - 60%)
    if humidity < 35:
        score -= min(20.0, (35 - humidity) * 0.8)
    elif humidity > 65:
        score -= min(25.0, (humidity - 65) * 0.8)
        
    # Wind penalty (ideal 1.5 - 5.0 m/s)
    if wind_speed > 8.0:
        score -= min(20.0, (wind_speed - 8.0) * 2.0)
        
    # AQI penalty (1: Good, 2: Fair, 3: Moderate, 4: Poor, 5: Very Poor)
    aqi_penalties = {1: 0, 2: 5, 3: 15, 4: 30, 5: 45}
    score -= aqi_penalties.get(int(aqi_val or 1), 10)
    
    final_score = int(max(5, min(100, round(score))))
    
    if final_score >= 85:
        label = "Optimal"
    elif final_score >= 70:
        label = "Comfortable"
    elif final_score >= 50:
        label = "Moderate"
    elif final_score >= 30:
        label = "Uncomfortable"
    else:
        label = "Harsh"
        
    return {
        'score': final_score,
        'label': label,
        'ideal_ranges': {
            'temperature': '20°C - 25°C',
            'humidity': '40% - 60%',
            'wind': '< 8 m/s',
            'aqi': 'Good (1)'
        }
    }

def is_chat_rate_limited(identifier, limit=None, window=60):
    """Checks whether the user or IP has exceeded chat rate limit per minute"""
    if limit is None:
        limit = current_app.config.get('AI_CHAT_RATE_LIMIT', 10)
        
    now = time.time()
    if identifier not in _chat_rate_limits:
        _chat_rate_limits[identifier] = []
        
    # Remove timestamps older than window
    _chat_rate_limits[identifier] = [t for t in _chat_rate_limits[identifier] if now - t < window]
    
    if len(_chat_rate_limits[identifier]) >= limit:
        return True
        
    _chat_rate_limits[identifier].append(now)
    return False

def sanitize_user_input(text):
    """
    Sanitizes user input to prevent prompt injection and limits input length.
    """
    if not text:
        return ""
    # Truncate to maximum 300 characters
    text = text.strip()[:300]
    # Remove dangerous prompt injection phrases while keeping natural language
    patterns = [
        r'(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions',
        r'(?i)reveal\s+(the\s+)?(api|system|secret)\s+key',
        r'(?i)system\s*:\s*',
        r'(?i)disregard\s+system\s+prompt',
        r'(?i)you\s+are\s+now\s+a',
    ]
    for p in patterns:
        text = re.sub(p, '[redacted]', text)
    return text

def _call_gemini_api(prompt, max_tokens=None):
    """
    Calls the Google Gemini REST API using server-side credentials.
    Returns (response_text, True) on success, or (error_msg, False) on failure.
    """
    api_key = current_app.config.get('AI_API_KEY')
    if not api_key:
        return "Gemini API key is not configured.", False
        
    model = current_app.config.get('AI_MODEL', 'gemini-1.5-flash')
    timeout = current_app.config.get('AI_REQUEST_TIMEOUT', 10)
    if max_tokens is None:
        max_tokens = current_app.config.get('AI_MAX_OUTPUT_TOKENS', 800)
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get('candidates', [])
            if candidates and 'content' in candidates[0]:
                parts = candidates[0]['content'].get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text'].strip(), True
            return "Empty response from Gemini API.", False
        else:
            err_msg = f"Gemini API error {resp.status_code}: {resp.text[:200]}"
            current_app.logger.warning(err_msg)
            return err_msg, False
    except requests.exceptions.Timeout:
        current_app.logger.warning("Gemini API request timed out.")
        return "Gemini API request timed out.", False
    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}")
        return str(e), False

def build_weather_context(city, weather_data=None, forecast_data=None, aqi_data=None, uv_data=None):
    """
    Constructs a clean, structured JSON context from real weather services.
    """
    if not weather_data:
        weather_data = get_current_weather(city)
    if not weather_data:
        return None
        
    coord = weather_data.get('coord', {})
    lat = coord.get('lat')
    lon = coord.get('lon')
    
    if forecast_data is None:
        forecast_data = get_forecast(city)
    if aqi_data is None and lat and lon:
        aqi_data = get_aqi(lat, lon)
    if uv_data is None and lat and lon:
        uv_data = get_uv_index(lat, lon)
        
    main = weather_data.get('main', {})
    wind = weather_data.get('wind', {})
    weather_desc = weather_data['weather'][0]['description'] if weather_data.get('weather') else 'N/A'
    
    # AQI details
    aqi_val = None
    aqi_label = "Unavailable"
    main_pollutant = "Unavailable"
    if aqi_data and 'list' in aqi_data and len(aqi_data['list']) > 0:
        first_aqi = aqi_data['list'][0]
        aqi_val = first_aqi.get('main', {}).get('aqi')
        labels = {1: 'Good', 2: 'Fair', 3: 'Moderate', 4: 'Poor', 5: 'Very Poor'}
        aqi_label = labels.get(aqi_val, 'Unknown')
        pm25 = first_aqi.get('components', {}).get('pm2_5', 0)
        main_pollutant = f"PM2.5 ({pm25} µg/m³)" if pm25 else "PM2.5 (Normal)"
        
    # UV details
    uv_val = uv_data.get('value', 5.0) if uv_data else None
    if uv_val is not None:
        uv_category = "Low" if uv_val < 3 else "Moderate" if uv_val < 6 else "High" if uv_val < 8 else "Very High"
    else:
        uv_category = "Unavailable"
        
    temp_c = main.get('temp', 0)
    humidity = main.get('humidity', 50)
    wind_speed = wind.get('speed', 0)
    
    comfort = calculate_comfort_score(temp_c, humidity, wind_speed, aqi_val)
    
    # Next 24 hours summary from forecast
    hourly_summary = []
    if forecast_data and 'list' in forecast_data:
        for item in forecast_data['list'][:8]:
            dt = datetime.fromtimestamp(item['dt']).strftime('%I %p')
            hourly_summary.append({
                'time': dt,
                'temp_c': item['main']['temp'],
                'condition': item['weather'][0]['description'] if item.get('weather') else '',
                'pop_percent': int(item.get('pop', 0) * 100)
            })
            
    # Next 5 days summary
    daily_summary = []
    if forecast_data and 'list' in forecast_data:
        from collections import defaultdict
        grouped = defaultdict(list)
        for item in forecast_data['list']:
            date_key = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            grouped[date_key].append(item)
        for d_str, items in list(grouped.items())[:5]:
            temps = [i['main']['temp'] for i in items]
            mid = next((i for i in items if '12:00:00' in i.get('dt_txt', '')), items[0])
            daily_summary.append({
                'date': d_str,
                'max_temp_c': max(temps),
                'min_temp_c': min(temps),
                'condition': mid['weather'][0]['description'] if mid.get('weather') else ''
            })

    return {
        'city': weather_data.get('name', city),
        'country': weather_data.get('sys', {}).get('country', 'N/A'),
        'coordinates': {'lat': lat, 'lon': lon},
        'current_temperature_c': temp_c,
        'feels_like_c': main.get('feels_like', temp_c),
        'humidity_percent': humidity,
        'pressure_hpa': main.get('pressure', 1013),
        'wind_speed_ms': wind_speed,
        'condition_description': weather_desc,
        'comfort_score': comfort['score'],
        'comfort_label': comfort['label'],
        'aqi_index': aqi_val,
        'aqi_label': aqi_label,
        'main_pollutant': main_pollutant,
        'uv_index': uv_val,
        'uv_category': uv_category,
        'hourly_forecast_24h': hourly_summary,
        'daily_forecast_5d': daily_summary,
        'data_timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    }

def generate_rule_based_briefing(context):
    """
    Transparent, grounded rule-based fallback based on real weather measurements.
    """
    city = context['city']
    temp = context['current_temperature_c']
    feels_like = context['feels_like_c']
    desc = context['condition_description']
    wind = context['wind_speed_ms']
    humidity = context['humidity_percent']
    uv = context['uv_index']
    aqi_label = context['aqi_label']
    comfort = context['comfort_label']
    
    # Check forecast for rain in next 24h
    rain_expected = any('rain' in h.get('condition', '').lower() or h.get('pop_percent', 0) > 40 for h in context.get('hourly_forecast_24h', []))
    
    parts = []
    # Current condition overview
    parts.append(f"{city}: Currently experiencing {desc} at {round(temp, 1)}°C (feels like {round(feels_like, 1)}°C) with {humidity}% humidity and {round(wind, 1)} m/s wind.")
    
    # Umbrella & rain advice
    if rain_expected or 'rain' in desc.lower() or 'drizzle' in desc.lower() or 'storm' in desc.lower():
        parts.append("Precipitation is detected or expected in the coming hours—carrying an umbrella and wearing waterproof gear is strongly recommended.")
    else:
        parts.append("No immediate rainfall is indicated in the short-term forecast, so outdoor travel should remain clear.")
        
    # Activity & Clothing
    if temp > 30:
        parts.append("Hot conditions require light breathable clothing, sun protection, and proper hydration.")
    elif temp < 12:
        parts.append("Cool conditions indicate warm layered outerwear is appropriate.")
    else:
        parts.append("Comfortable ambient temperatures are well-suited for regular daily commutes and outdoor exercise.")
        
    # Health, AQI & UV
    if uv and uv >= 6:
        parts.append(f"UV exposure is high ({uv}); apply SPF sunscreen and limit direct midday sun.")
    if aqi_label in ['Poor', 'Very Poor']:
        parts.append(f"Air quality is currently {aqi_label}; sensitive individuals should minimize prolonged strenuous outdoor activities.")
    else:
        parts.append(f"Air quality is rated {aqi_label} with an overall '{comfort}' comfort index.")
        
    return " ".join(parts)

def get_weather_briefing(city, force_refresh=False):
    """
    Generates or retrieves a cached AI Weather Briefing for a city.
    Uses Google Gemini when configured; otherwise falls back gracefully to
    a grounded rule-based briefing based on real data.
    """
    context = build_weather_context(city)
    if not context:
        return {'success': False, 'message': f"Could not retrieve weather data for '{city}'."}
        
    cache_ttl = current_app.config.get('AI_BRIEFING_CACHE_TTL', 1800)
    cache_key = f"ai_briefing_{city.lower()}_{context['data_timestamp'].replace(' ', '_')}"
    
    if not force_refresh:
        cached = cache_get(cache_key)
        if cached:
            cached['cached'] = True
            return cached
            
    api_key = current_app.config.get('AI_API_KEY')
    model_name = current_app.config.get('AI_MODEL', 'gemini-1.5-flash')
    
    if api_key:
        prompt = f"""You are ClimaSense AI, an intelligent, grounded meteorological assistant.
Generate a concise, human-friendly Weather Briefing (3 to 4 sentences) for {context['city']}.
Use ONLY the real measurements provided below. Do NOT invent or hallucinate unmeasured data.

REAL WEATHER DATA (JSON):
{json.dumps(context, indent=2)}

INSTRUCTIONS:
1. Summarize current temperature, feels-like, and condition.
2. State forecast changes over the next 24 hours (including whether rain is expected and if an umbrella is needed).
3. Offer practical advice on clothing and outdoor exercise/activities.
4. Mention UV precaution or Air Quality if notable.
5. Keep tone professional, encouraging, and clear.
"""
        response_text, success = _call_gemini_api(prompt, max_tokens=300)
        if success:
            result = {
                'success': True,
                'city': context['city'],
                'briefing': response_text,
                'is_ai_generated': True,
                'provider': 'Google Gemini',
                'model': model_name,
                'cached': False,
                'comfort_score': context['comfort_score'],
                'comfort_label': context['comfort_label'],
                'timestamp': context['data_timestamp']
            }
            cache_set(cache_key, result, ttl=cache_ttl)
            return result

    # Rule-based fallback if API is not configured or failed
    fallback_text = generate_rule_based_briefing(context)
    result = {
        'success': True,
        'city': context['city'],
        'briefing': fallback_text,
        'is_ai_generated': False,
        'provider': 'Grounded Rule Engine (Gemini Key Not Set / Offline)',
        'model': 'Rule-Based Fallback',
        'cached': False,
        'comfort_score': context['comfort_score'],
        'comfort_label': context['comfort_label'],
        'timestamp': context['data_timestamp']
    }
    # Do not cache fallback for long if Gemini might be transiently offline
    cache_set(cache_key, result, ttl=300)
    return result

def extract_cities_from_text(text, default_city='Bengaluru'):
    """
    Extracts potential city names from a user chat message.
    Supports single cities and multi-city comparisons.
    """
    # Common known world/regional cities regex or split
    # Check for patterns like "Compare X and Y", "trip to X", "weather in X"
    cities = []
    compare_match = re.search(r'(?i)compare\s+([A-Za-z\s]+?)\s+(?:and|with|to)\s+([A-Za-z\s]+?)(?:\s+weather|\?|\.|$)', text)
    if compare_match:
        c1 = compare_match.group(1).strip()
        c2 = compare_match.group(2).strip()
        return [c1, c2]
        
    in_match = re.search(r'(?i)(?:in|to|for|at)\s+([A-Za-z]{3,20})(?:\s+this|\s+tomorrow|\s+today|\?|\.|$)', text)
    if in_match:
        c = in_match.group(1).strip()
        # Avoid common non-city words
        if c.lower() not in ['today', 'tomorrow', 'weekend', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'umbrella', 'drying', 'clothes', 'exercise']:
            return [c]
            
    # Default to current viewed city if no explicit city found
    return [default_city]

def answer_weather_chat(user_question, current_city='Bengaluru', user_id=None):
    """
    Handles conversational questions grounded in real weather data.
    """
    cleaned_question = sanitize_user_input(user_question)
    if not cleaned_question:
        return {'success': False, 'message': 'Please enter a valid weather question.'}
        
    # Rate limiting
    rate_id = str(user_id) if user_id else 'anon'
    if is_chat_rate_limited(rate_id):
        return {'success': False, 'message': 'Rate limit reached (max 10 questions/min). Please pause for a moment.'}
        
    # Extract cities
    target_cities = extract_cities_from_text(cleaned_question, default_city=current_city)
    
    # Check for long-range future date questions beyond 5-day provider horizon
    is_far_future = bool(re.search(r'(?i)(next\s+month|next\s+year|in\s+2\s+weeks|in\s+3\s+weeks|next\s+season)', cleaned_question))
    
    # Gather real weather context for all target cities
    city_contexts = {}
    for c in target_cities:
        ctx = build_weather_context(c)
        if ctx:
            city_contexts[ctx['city']] = ctx
            
    if not city_contexts:
        return {
            'success': False,
            'message': f"Could not locate live weather data for '{', '.join(target_cities)}'. Please verify the city name."
        }
        
    api_key = current_app.config.get('AI_API_KEY')
    model_name = current_app.config.get('AI_MODEL', 'gemini-1.5-flash')
    
    if api_key:
        prompt = f"""You are ClimaSense Weather AI Assistant. Answer the user's weather question accurately, concisely, and supportively.
CRITICAL SAFETY & GROUNDING RULES:
1. Rely ONLY on the provided REAL WEATHER DATA below.
2. Never invent, hallucinate, or fabricate unmeasured temperatures, rain, or forecasts.
3. If the user asks about dates beyond the available 5-day forecast horizon, explicitly explain that live weather forecasts are limited to 5 days ahead, and provide what is known.
4. If comparing multiple cities, compare their temperature, conditions, and rain probabilities directly based on the data.
5. If user asks about drying clothes or outdoor exercise, recommend specific times based on the hourly forecast.

USER QUESTION:
"{cleaned_question}"

REAL WEATHER DATA:
{json.dumps(city_contexts, indent=2)}
"""
        response_text, success = _call_gemini_api(prompt, max_tokens=400)
        if success:
            return {
                'success': True,
                'answer': response_text,
                'is_ai_generated': True,
                'provider': 'Google Gemini',
                'model': model_name,
                'cities': list(city_contexts.keys())
            }
            
    # Grounded rule-based fallback response
    fallback_answer = _build_rule_based_chat_answer(cleaned_question, city_contexts, is_far_future)
    return {
        'success': True,
        'answer': fallback_answer,
        'is_ai_generated': False,
        'provider': 'Grounded Rule Engine (Gemini Key Not Set / Offline)',
        'cities': list(city_contexts.keys())
    }

def _build_rule_based_chat_answer(question, contexts, is_far_future):
    q_lower = question.lower()
    
    if is_far_future:
        return "Live meteorological provider forecasts are limited to a 5-day horizon. Long-range multi-week or monthly forecasts cannot be verified accurately with real-time station data."
        
    # Multi-city comparison
    if len(contexts) > 1:
        parts = ["City Comparison:"]
        for cname, c in contexts.items():
            parts.append(f"• {cname}: {round(c['current_temperature_c'], 1)}°C, {c['condition_description']}, Humidity: {c['humidity_percent']}%, Wind: {round(c['wind_speed_ms'], 1)} m/s.")
        return " ".join(parts)
        
    ctx = list(contexts.values())[0]
    cname = ctx['city']
    temp = ctx['current_temperature_c']
    desc = ctx['condition_description']
    hourly = ctx.get('hourly_forecast_24h', [])
    rain_expected = any('rain' in h.get('condition', '').lower() or h.get('pop_percent', 0) > 40 for h in hourly)
    
    # Umbrella question
    if 'umbrella' in q_lower or 'rain' in q_lower:
        if rain_expected or 'rain' in desc.lower():
            return f"Yes, you should carry an umbrella in {cname}. Precipitation is detected or forecast within the next 24 hours."
        return f"An umbrella is likely not needed right now in {cname}. Current conditions are {desc} with a low chance of rain."
        
    # Clothes drying question
    if 'dry' in q_lower or 'clothes' in q_lower or 'laundry' in q_lower:
        if rain_expected or ctx['humidity_percent'] > 75:
            return f"Outdoor clothes drying is not ideal today in {cname} due to elevated humidity ({ctx['humidity_percent']}%) and potential rain. Indoor drying is recommended."
        return f"Good conditions for drying clothes in {cname}! Clear skies and moderate humidity ({ctx['humidity_percent']}%) support fast outdoor drying."
        
    # Exercise question
    if 'exercise' in q_lower or 'outdoor' in q_lower or 'run' in q_lower or 'jog' in q_lower:
        if temp > 32 or ctx['aqi_label'] in ['Poor', 'Very Poor']:
            return f"Limit intense outdoor exercise in {cname} right now. Conditions are hot ({round(temp, 1)}°C) and air quality is rated {ctx['aqi_label']}."
        return f"Great time for outdoor workouts in {cname}! Temperatures are {round(temp, 1)}°C with {ctx['condition_description']} and {ctx['aqi_label']} air quality."
        
    # What to wear
    if 'wear' in q_lower or 'clothing' in q_lower or 'jacket' in q_lower:
        if temp < 12:
            return f"In {cname} ({round(temp, 1)}°C), wear warm layered clothing, a heavy jacket, and thermal wear if heading out late."
        elif temp > 28:
            return f"In {cname} ({round(temp, 1)}°C), light, loose cotton fabrics, sunglasses, and sun protection are best."
        return f"In {cname} ({round(temp, 1)}°C), comfortable casual wear with a light jacket or sweater will be ideal."
        
    # General overview
    return f"In {cname}, current weather is {desc} at {round(temp, 1)}°C (feels like {round(ctx['feels_like_c'], 1)}°C), with {ctx['humidity_percent']}% humidity and a '{ctx['comfort_label']}' comfort rating."
