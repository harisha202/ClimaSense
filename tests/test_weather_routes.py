import pytest
from unittest.mock import patch

MOCK_WEATHER_BENGALURU = {
    'coord': {'lon': 77.5946, 'lat': 12.9716},
    'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
    'main': {
        'temp': 24.5,
        'feels_like': 24.2,
        'temp_min': 22.0,
        'temp_max': 27.0,
        'pressure': 1014,
        'humidity': 52
    },
    'visibility': 10000,
    'wind': {'speed': 3.1, 'deg': 120},
    'clouds': {'all': 10},
    'dt': 1792950000,
    'sys': {'country': 'IN', 'sunrise': 1792920000, 'sunset': 1792960000},
    'name': 'Bengaluru'
}

MOCK_FORECAST_BENGALURU = {
    'city': {'name': 'Bengaluru', 'country': 'IN', 'timezone': 19800},
    'list': [
        {
            'dt': 1792950000,
            'dt_txt': '2026-10-26 12:00:00',
            'main': {'temp': 25.0, 'temp_min': 21.0, 'temp_max': 27.0, 'humidity': 50, 'pressure': 1014},
            'weather': [{'description': 'clear sky', 'icon': '01d'}],
            'pop': 0.1
        },
        {
            'dt': 1792960800,
            'dt_txt': '2026-10-26 15:00:00',
            'main': {'temp': 23.0, 'temp_min': 20.0, 'temp_max': 25.0, 'humidity': 60, 'pressure': 1013},
            'weather': [{'description': 'few clouds', 'icon': '02d'}],
            'pop': 0.15
        }
    ]
}

def test_api_weather_success(client):
    """Verify /api/weather/<city> returns grounded telemetry and comfort score."""
    with patch('services.openweather_service.get_current_weather', return_value=MOCK_WEATHER_BENGALURU), \
         patch('services.openweather_service.get_forecast', return_value=MOCK_FORECAST_BENGALURU), \
         patch('services.openweather_service.get_aqi', return_value={'list': [{'main': {'aqi': 2}}]}):
        
        res = client.get('/api/weather/Bengaluru')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Bengaluru'
        assert data['data']['main']['temp'] == 24.5
        assert 'comfort_score' in data
        assert 'comfort_label' in data
        assert data['comfort_score'] > 0

def test_api_weather_not_found(client):
    """Verify /api/weather/<city> returns 404 on invalid city."""
    with patch('services.openweather_service.get_current_weather', return_value=None):
        res = client.get('/api/weather/NonExistentCityXYZ')
        assert res.status_code == 404
        data = res.get_json()
        assert data['success'] is False

def test_api_weather_geo(auth_client):
    """Verify /api/weather/geo with coordinates."""
    with patch('services.openweather_service.get_weather_by_coords', return_value=MOCK_WEATHER_BENGALURU):
        res = auth_client.get('/api/weather/geo?lat=12.97&lon=77.59')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Bengaluru'

def test_export_weather_csv(client):
    """Verify /api/weather/<city>/export/csv exports sanitized CSV."""
    with patch('services.openweather_service.get_current_weather', return_value=MOCK_WEATHER_BENGALURU):
        res = client.get('/api/weather/Bengaluru/export/csv')
        assert res.status_code == 200
        assert res.mimetype == 'text/csv'
        csv_text = res.get_data(as_text=True)
        assert 'City,Country,Observation Timestamp' in csv_text
        assert 'Bengaluru' in csv_text
        assert '24.5' in csv_text

def test_saved_cities_crud(auth_client):
    """Verify saving and retrieving cities for authenticated user."""
    # Save city
    res = auth_client.post('/api/cities/save', json={'city': 'Tokyo'})
    assert res.status_code == 200
    assert res.get_json()['success'] is True
    
    # Duplicate save rejected
    res_dup = auth_client.post('/api/cities/save', json={'city': 'Tokyo'})
    assert res_dup.status_code == 400
    
    # Get saved cities
    with patch('services.openweather_service.get_current_weather', return_value=MOCK_WEATHER_BENGALURU):
        res_list = auth_client.get('/api/cities/saved')
        assert res_list.status_code == 200
        assert len(res_list.get_json()['cities']) >= 1
