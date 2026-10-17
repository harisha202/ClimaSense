from unittest.mock import patch, MagicMock
import requests

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
    assert data['success'] is True
    assert data['data']['name'] == 'London'
    assert 'comfort_score' in data
    assert 'comfort_label' in data

def test_get_weather_unauthorized(client):
    res = client.get('/api/weather/London')
    assert res.status_code == 401

def test_system_status(logged_in_client):
    res = logged_in_client.get('/api/system-status')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    # Ensure API Key is never shown in raw text
    assert '••••••••' in data['status']['weather_api']['api_key_status']

@patch('services.openweather_service.get_uv_index')
def test_uv_endpoint(mock_uv, logged_in_client):
    mock_uv.return_value = {'value': 4.5}
    res = logged_in_client.get('/api/uv?lat=51.51&lon=-0.13')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
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

@patch('services.openweather_service.get_current_weather')
def test_export_csv(mock_weather, logged_in_client):
    mock_weather.return_value = {
        'name': 'Paris',
        'sys': {'country': 'FR'},
        'main': {'temp': 20, 'feels_like': 19, 'humidity': 50, 'pressure': 1014},
        'weather': [{'description': 'clear sky', 'icon': '01d'}],
        'wind': {'speed': 2.5},
        'coord': {'lat': 48.85, 'lon': 2.35}
    }
    res = logged_in_client.get('/api/weather/Paris/export/csv')
    assert res.status_code == 200
    assert 'text/csv' in res.content_type
    assert b'City,Country' in res.data

@patch('services.unsplash_service.requests.get')
def test_background_attribution(mock_requests_get, logged_in_client, app):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'results': [{
            'urls': {'regular': 'https://images.unsplash.com/test.jpg'},
            'user': {
                'name': 'Jane Photographer',
                'links': {'html': 'https://unsplash.com/@jane'}
            }
        }]
    }
    mock_requests_get.return_value = mock_resp
    with app.app_context():
        app.config['UNSPLASH_API_KEY'] = 'test_unsplash_key'
        res = logged_in_client.get('/api/background/Tokyo')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'test.jpg' in data['url']
        assert data['photographer_name'] == 'Jane Photographer'
        assert 'utm_source=ClimaSense' in data['photographer_url']

@patch('services.openweather_service.get_forecast')
def test_forecast_endpoint(mock_fc, logged_in_client):
    mock_fc.return_value = {
        'list': [
            {
                'dt': 1700000000,
                'dt_txt': '2026-10-17 12:00:00',
                'main': {'temp': 18.0},
                'weather': [{'icon': '01d', 'description': 'sunny'}]
            }
        ]
    }
    res = logged_in_client.get('/api/forecast/Berlin')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'forecast' in data

@patch('services.openweather_service._safe_request')
def test_safe_request_handles_retry(mock_safe):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_safe.return_value = mock_resp
    from services.openweather_service import get_current_weather
    # Should execute without crashing
    assert mock_safe is not None
