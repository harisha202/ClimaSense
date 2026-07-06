from unittest.mock import patch

@patch('services.openweather_service.get_current_weather')
def test_history_recording(mock_get_weather, logged_in_client, app):
    mock_get_weather.return_value = {
        'name': 'Paris',
        'main': {'temp': 20, 'feels_like': 20, 'humidity': 50, 'pressure': 1012},
        'weather': [{'description': 'clear sky', 'icon': '01d'}],
        'wind': {'speed': 2},
        'coord': {'lat': 48.85, 'lon': 2.35}
    }
    
    # Trigger a search
    logged_in_client.get('/api/weather/Paris')
    
    # Check history endpoint
    res = logged_in_client.get('/api/search-history')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] == True
    assert len(data['history']) == 1
    assert data['history'][0]['city'] == 'Paris'
    
    # Test clearing history
    res_clear = logged_in_client.post('/api/clear-history')
    assert res_clear.status_code == 200
    
    res2 = logged_in_client.get('/api/search-history')
    data2 = res2.get_json()
    assert len(data2['history']) == 0
