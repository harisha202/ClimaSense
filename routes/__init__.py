from .auth import auth_bp
from .weather import weather_bp
from .forecast import forecast_bp
from .aqi import aqi_bp
from .predictions import predictions_bp
from .history import history_bp
from .alerts import alerts_bp
from .trends import trends_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(aqi_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(trends_bp)
