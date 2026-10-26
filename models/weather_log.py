from extensions import db
from datetime import datetime

class WeatherLog(db.Model):
    __tablename__ = 'weather_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    humidity = db.Column(db.Integer)
    pressure = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    aqi = db.Column(db.Integer)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_city_recorded_at', 'city', 'recorded_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'aqi': self.aqi,
            'description': self.description,
            'icon': self.icon,
            'recorded_at': self.recorded_at.isoformat()
        }
