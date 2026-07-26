from unittest.mock import patch

@patch('services.openweather_service.get_current_weather')
def test_get_weather(mock_get_weather, logged_in_client):
    mock_get_weather.return_value = {
        'name': 'London',
        'main': {'temp': 15, 'feels_like': 14, 'humidity': 80, 'pressure': 1012},
        'weather': [{'description': 'broken clouds', 'icon': '04d'}],
        'wind': {'speed': 4.1},
        'coord': {'lat': 51.51, 'lon': -0.13}
    }
    
    res = logged_in_client.get('/api/weather/London')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] == True
    assert data['data']['name'] == 'London'

def test_get_weather_unauthorized(client):
    res = client.get('/api/weather/London')
    assert res.status_code == 401

def test_system_status(logged_in_client):
    res = logged_in_client.get('/api/system-status')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] == True
    # Ensure API Key is never shown in raw text
    assert '••••••••' in data['status']['weather_api']['api_key_status']

@patch('services.openweather_service.get_uv_index')
def test_uv_endpoint(mock_uv, logged_in_client):
    mock_uv.return_value = {'value': 4.5}
    res = logged_in_client.get('/api/uv?lat=51.51&lon=-0.13')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] == True
    assert data['uvi'] == 4.5
    assert data['category'] == 'Moderate'

@patch('services.openweather_service.get_current_weather')
def test_export_pdf(mock_weather, logged_in_client):
    mock_weather.return_value = {
        'name': 'London',
        'sys': {'country': 'GB'},
        'main': {'temp': 15, 'feels_like': 14, 'humidity': 80, 'pressure': 1012},
        'weather': [{'description': 'broken clouds', 'icon': '04d'}],
        'wind': {'speed': 4.1},
        'coord': {'lat': 51.51, 'lon': -0.13}
    }
    res = logged_in_client.get('/api/weather/London/export/pdf')
    assert res.status_code == 200
    assert 'text/html' in res.content_type
    assert b'ClimaSense Environmental Report' in res.data
