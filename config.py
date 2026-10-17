import os
from dotenv import load_dotenv

load_dotenv('api.env')
load_dotenv('.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenWeather & Unsplash APIs
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')
    
    # Redis Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', 300))
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Google Gemini AI Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini')
    AI_API_KEY = os.environ.get('AI_API_KEY') or os.environ.get('GEMINI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-1.5-flash')
    AI_BRIEFING_CACHE_TTL = int(os.environ.get('AI_BRIEFING_CACHE_TTL', 1800))
    AI_CHAT_RATE_LIMIT = int(os.environ.get('AI_CHAT_RATE_LIMIT', 10))
    AI_MAX_OUTPUT_TOKENS = int(os.environ.get('AI_MAX_OUTPUT_TOKENS', 800))
    AI_REQUEST_TIMEOUT = int(os.environ.get('AI_REQUEST_TIMEOUT', 10))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
