from datetime import datetime
import json
from extensions import mail
from flask_mail import Message
from flask import current_app
from services.openweather_service import get_current_weather, get_forecast
from services.ai_service import _call_gemini_api
from models.saved_city import SavedCity

def build_digest_for_user(user):
    """
    Fetches real weather for all of a user's saved cities and generates
    an AI-enhanced or rule-based morning digest with personalized tips.
    """
    cities = SavedCity.query.filter_by(user_id=user.id).all()
    if not cities:
        return None
        
    cities_data = []
    for sc in cities:
        weather = get_current_weather(sc.city)
        if weather:
            desc = weather['weather'][0]['description'] if weather.get('weather') else 'N/A'
            temp = weather.get('main', {}).get('temp', 0)
            feels_like = weather.get('main', {}).get('feels_like', temp)
            humidity = weather.get('main', {}).get('humidity', 0)
            wind = weather.get('wind', {}).get('speed', 0)
            
            # Check 24h rain forecast
            fc = get_forecast(sc.city)
            rain_likely = False
            if fc and 'list' in fc:
                rain_likely = any('rain' in item['weather'][0]['description'].lower() or item.get('pop', 0) > 0.4 for item in fc['list'][:8])
                
            cities_data.append({
                'city': weather.get('name', sc.city),
                'temp_c': temp,
                'feels_like_c': feels_like,
                'humidity': humidity,
                'wind_ms': wind,
                'description': desc,
                'rain_likely': rain_likely
            })
            
    if not cities_data:
        return None

    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    
    # Try Gemini smart digest if configured
    api_key = current_app.config.get('AI_API_KEY')
    if api_key:
        prompt = f"""You are ClimaSense AI. Write a concise, personalized daily weather digest email for user '{user.username}'.
Include:
1. A warm morning greeting.
2. For each saved city, a 1-sentence weather summary plus EXACTLY ONE actionable weather tip (e.g. umbrella, clothing, commute, outdoor activity).
3. A brief closing note mentioning data timestamp and 5-day provider limits.

SAVED CITIES WEATHER DATA:
{json.dumps(cities_data, indent=2)}
"""
        ai_summary, success = _call_gemini_api(prompt, max_tokens=450)
        if success and ai_summary:
            return {
                'subject': f"🌤️ ClimaSense Daily Digest: {now_str[:10]}",
                'body_text': ai_summary,
                'is_ai_generated': True,
                'timestamp': now_str
            }
            
    # Grounded rule-based fallback digest
    lines = [
        f"Good day, {user.username}!",
        f"Here is your ClimaSense Daily Weather Digest ({now_str}):\n"
    ]
    for c in cities_data:
        tip = "Great day for regular outdoor commutes."
        if c['rain_likely'] or 'rain' in c['description'].lower():
            tip = "Carry an umbrella—rain is detected or forecast today."
        elif c['temp_c'] > 30:
            tip = "Stay hydrated and wear breathable light clothing."
        elif c['temp_c'] < 12:
            tip = "Bundle up with warm outerwear."
            
        lines.append(f"• {c['city']}: {round(c['temp_c'], 1)}°C ({c['description']}), Humidity: {c['humidity']}%")
        lines.append(f"  Tip: {tip}\n")
        
    lines.append("Note: Provider forecasts are verified up to 5 days ahead. Have a wonderful day!")
    
    return {
        'subject': f"🌤️ ClimaSense Daily Digest: {now_str[:10]}",
        'body_text': "\n".join(lines),
        'is_ai_generated': False,
        'timestamp': now_str
    }

def send_digest_email(user, digest_result):
    """
    Sends the digest email to the user using Flask-Mail.
    """
    if not digest_result or not user or not user.email:
        return False
        
    body_content = digest_result['body_text'] if isinstance(digest_result, dict) else str(digest_result)
    subject = digest_result.get('subject', "ClimaSense: Your Daily Weather Digest") if isinstance(digest_result, dict) else "ClimaSense: Your Daily Weather Digest"
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body_content
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send digest email to {user.email}: {e}")
        return False
