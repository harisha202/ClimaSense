import pytest
from datetime import datetime
from models.user import User
from models.weather_log import WeatherLog
from models.forecast_snapshot import ForecastSnapshot
from models.saved_city import SavedCity
from models.search_history import SearchHistory

def test_user_password_hashing(db_session):
    """Verify password hashing and verification."""
    user = User(username='climate_researcher', email='climate@research.org')
    user.set_password('Atmosphere2026!Sec')
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.password_hash != 'Atmosphere2026!Sec'
    assert user.check_password('Atmosphere2026!Sec') is True
    assert user.check_password('WrongPassword!') is False

def test_weather_log_model(db_session):
    """Verify WeatherLog creation and dictionary conversion."""
    log = WeatherLog(
        city='Tokyo',
        temperature=18.4,
        feels_like=17.9,
        humidity=65,
        pressure=1015,
        wind_speed=4.2,
        aqi=2,
        description='scattered clouds',
        icon='03d'
    )
    db_session.add(log)
    db_session.commit()
    
    d = log.to_dict()
    assert d['city'] == 'Tokyo'
    assert d['temperature'] == 18.4
    assert d['humidity'] == 65
    assert d['aqi'] == 2
    assert d['description'] == 'scattered clouds'

def test_forecast_snapshot_accuracy_calculation(db_session):
    """Verify ForecastSnapshot accuracy calculation metrics."""
    snap = ForecastSnapshot(
        city='Paris',
        target_date='2026-10-26',
        predicted_max_temp=22.0,
        predicted_min_temp=14.0,
        predicted_condition='clear sky',
        predicted_pop=10
    )
    db_session.add(snap)
    db_session.commit()
    
    assert snap.is_verified is False
    assert snap.accuracy_percentage is None
    
    # Simulate post-event verification
    snap.actual_max_temp = 21.5
    snap.actual_min_temp = 14.5
    snap.actual_condition = 'few clouds'
    snap.actual_rain_observed = False
    
    acc = snap.calculate_accuracy()
    db_session.commit()
    
    assert snap.is_verified is True
    assert acc is not None
    assert acc >= 90.0

def test_user_cascade_relationships(db_session):
    """Verify saved cities and search history cascade on user deletion."""
    user = User(username='cascadetest', email='cascade@test.local')
    user.set_password('SecurePass123!')
    db_session.add(user)
    db_session.commit()
    
    city = SavedCity(user_id=user.id, city='London')
    hist = SearchHistory(user_id=user.id, city='London')
    db_session.add_all([city, hist])
    db_session.commit()
    
    assert len(user.saved_cities) == 1
    assert len(user.search_history) == 1
    
    db_session.delete(user)
    db_session.commit()
    
    assert SavedCity.query.filter_by(city='London').count() == 0
    assert SearchHistory.query.filter_by(city='London').count() == 0
