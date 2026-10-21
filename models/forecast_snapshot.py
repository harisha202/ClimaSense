from extensions import db
from datetime import datetime

class ForecastSnapshot(db.Model):
    """
    Stores forecast predictions alongside observed actuals to compute
    transparent 24-48 hour meteorological accuracy scores.
    """
    __tablename__ = 'forecast_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    target_date = db.Column(db.String(20), nullable=False, index=True) # YYYY-MM-DD
    
    # Forecasted values
    predicted_max_temp = db.Column(db.Float, nullable=False)
    predicted_min_temp = db.Column(db.Float, nullable=False)
    predicted_condition = db.Column(db.String(100), nullable=True)
    predicted_pop = db.Column(db.Integer, default=0) # Probability of precipitation %

    # Actual observed values (recorded post-event)
    actual_max_temp = db.Column(db.Float, nullable=True)
    actual_min_temp = db.Column(db.Float, nullable=True)
    actual_condition = db.Column(db.String(100), nullable=True)
    actual_rain_observed = db.Column(db.Boolean, default=False)

    # Computed accuracy score (0 - 100)
    accuracy_percentage = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_accuracy(self):
        """Calculates grounded prediction accuracy percentage based on delta."""
        if self.actual_max_temp is None or self.actual_min_temp is None:
            return None
            
        temp_delta = abs(self.predicted_max_temp - self.actual_max_temp) + abs(self.predicted_min_temp - self.actual_min_temp)
        # 1°C difference penalizes ~ 5%
        temp_score = max(0.0, 100.0 - (temp_delta * 6.0))

        # Rain prediction alignment
        rain_predicted = self.predicted_pop >= 40
        rain_match = (rain_predicted == self.actual_rain_observed)
        rain_score = 100.0 if rain_match else 60.0

        score = round((temp_score * 0.7) + (rain_score * 0.3), 1)
        self.accuracy_percentage = min(100.0, max(10.0, score))
        self.is_verified = True
        return self.accuracy_percentage

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'target_date': self.target_date,
            'predicted': {
                'max_temp': self.predicted_max_temp,
                'min_temp': self.predicted_min_temp,
                'condition': self.predicted_condition,
                'pop': self.predicted_pop
            },
            'actual': {
                'max_temp': self.actual_max_temp,
                'min_temp': self.actual_min_temp,
                'condition': self.actual_condition,
                'rain_observed': self.actual_rain_observed
            } if self.is_verified else None,
            'accuracy_percentage': self.accuracy_percentage,
            'is_verified': self.is_verified
        }
