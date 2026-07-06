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
