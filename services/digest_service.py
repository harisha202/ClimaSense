from extensions import mail
from flask_mail import Message
from flask import current_app
from services.openweather_service import get_current_weather
from models.saved_city import SavedCity

def build_digest_for_user(user):
    """Fetches current weather for all of a user's saved cities, formats a summary"""
    cities = SavedCity.query.filter_by(user_id=user.id).all()
    if not cities:
        return None
        
    digest_lines = [f"Daily Weather Digest for {user.username}\n"]
    for saved_city in cities:
        weather = get_current_weather(saved_city.city)
        if weather:
            temp = weather['main']['temp']
            desc = weather['weather'][0]['description']
            digest_lines.append(f"- {saved_city.city}: {temp}°C, {desc}")
            
    return "\n".join(digest_lines)

def send_digest_email(user, digest_content):
    """Uses Flask-Mail to send the daily summary to the user's email address"""
    if not digest_content:
        return False
        
    try:
        msg = Message(
            subject="ClimaSense: Your Daily Weather Digest",
            recipients=[user.email],
            body=digest_content
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send digest email to {user.email}: {e}")
        return False
