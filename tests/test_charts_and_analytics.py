import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from models.weather_log import WeatherLog
from models.forecast_snapshot import ForecastSnapshot

def test_trends_endpoint_empty_state(client, db_session):
    """Verify trends returns empty dataset honestly when no logs exist."""
    res = client.get('/api/trends/NewCityNoHistory')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['city'] == 'NewCityNoHistory'
    assert len(data['data']) == 0

def test_trends_endpoint_with_records(client, db_session):
    """Verify trends returns real historical logs for requested range."""
    now = datetime.utcnow()
    for i in range(5):
        log = WeatherLog(
            city='London',
            temperature=15.0 + i,
            feels_like=14.5 + i,
            humidity=60,
            pressure=1013,
            wind_speed=3.0,
            aqi=1,
            description='cloudy',
            icon='04d',
            recorded_at=now - timedelta(days=i)
        )
        db_session.add(log)
    db_session.commit()

    res = client.get('/api/trends/London?range=7d')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['data']) == 5
    assert data['data'][0]['city'] == 'London'

def test_predictions_accuracy_honest_state_no_verified_data(client):
    """Verify forecast accuracy does NOT show fake 91.5% when no verified records exist."""
    mock_weather = {
        'name': 'Dublin',
        'main': {'temp': 14.0, 'humidity': 70},
        'weather': [{'description': 'light rain'}]
    }
    with patch('services.openweather_service.get_current_weather', return_value=mock_weather), \
         patch('services.openweather_service.get_forecast', return_value={'list': []}), \
         patch('routes.predictions._call_gemini_api', return_value=("Mock insight", True)):
        
        res = client.get('/api/predictions/Dublin')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        pred = data['prediction']
        assert pred['accuracy_percentage'] is None
        assert "Not enough verified data" in pred['accuracy_headline']

def test_predictions_accuracy_with_verified_data(client, db_session):
    """Verify forecast accuracy calculates truthfully from verified snapshots."""
    snap1 = ForecastSnapshot(
        city='Edinburgh',
        target_date='2026-10-24',
        predicted_max_temp=15.0,
        predicted_min_temp=8.0,
        actual_max_temp=14.5,
        actual_min_temp=8.5,
        accuracy_percentage=94.0,
        is_verified=True
    )
    snap2 = ForecastSnapshot(
        city='Edinburgh',
        target_date='2026-10-25',
        predicted_max_temp=16.0,
        predicted_min_temp=9.0,
        actual_max_temp=15.0,
        actual_min_temp=8.0,
        accuracy_percentage=88.0,
        is_verified=True
    )
    db_session.add_all([snap1, snap2])
    db_session.commit()

    mock_weather = {
        'name': 'Edinburgh',
        'main': {'temp': 13.0, 'humidity': 65},
        'weather': [{'description': 'few clouds'}]
    }
    with patch('services.openweather_service.get_current_weather', return_value=mock_weather), \
         patch('services.openweather_service.get_forecast', return_value={'list': []}), \
         patch('routes.predictions._call_gemini_api', return_value=("Mock insight", True)):
        
        res = client.get('/api/predictions/Edinburgh')
        assert res.status_code == 200
        data = res.get_json()
        pred = data['prediction']
        assert pred['accuracy_percentage'] == 91.0
        assert "91.0% Verified Accuracy" in pred['accuracy_headline']

def test_compare_export_csv(client):
    """Verify side-by-side comparison CSV export reflects selected cities."""
    mock_c1 = {
        'name': 'London',
        'sys': {'country': 'GB'},
        'main': {'temp': 16.0, 'feels_like': 15.5, 'humidity': 65, 'pressure': 1015},
        'wind': {'speed': 4.0},
        'weather': [{'description': 'scattered clouds'}]
    }
    mock_c2 = {
        'name': 'Paris',
        'sys': {'country': 'FR'},
        'main': {'temp': 19.5, 'feels_like': 19.0, 'humidity': 55, 'pressure': 1018},
        'wind': {'speed': 3.2},
        'weather': [{'description': 'clear sky'}]
    }
    with patch('services.openweather_service.get_current_weather', side_effect=lambda c: mock_c1 if c == 'London' else mock_c2):
        res = client.get('/api/compare/export/csv?city1=London&city2=Paris')
        assert res.status_code == 200
        assert res.mimetype == 'text/csv'
        csv_text = res.get_data(as_text=True)
        assert 'London, GB' in csv_text
        assert 'Paris, FR' in csv_text
        assert 'Temperature' in csv_text
