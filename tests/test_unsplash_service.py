import pytest
from unittest.mock import patch, MagicMock
from services.unsplash_service import (
    get_background_image,
    fetch_city_photos_from_unsplash,
    determine_weather_mood,
    get_fallback_photo,
    get_rotating_fallback_photo
)

MOCK_UNSPLASH_RESULTS = [
    {
        'urls': {'regular': 'https://images.unsplash.com/photo-mysuru-palace', 'full': 'https://images.unsplash.com/photo-mysuru-full'},
        'user': {'name': 'Karnataka Tourism Photographer', 'username': 'karnatakatour', 'links': {'html': 'https://unsplash.com/@karnatakatour'}},
        'alt_description': 'Mysuru Palace illuminated at dusk',
        'description': 'Historic Mysuru Palace'
    },
    {
        'urls': {'regular': 'https://images.unsplash.com/photo-mysuru-chamundi', 'full': 'https://images.unsplash.com/photo-mysuru-chamundi-full'},
        'user': {'name': 'Heritage Photo Guy', 'username': 'heritagephoto', 'links': {'html': 'https://unsplash.com/@heritagephoto'}},
        'alt_description': 'Chamundi Hills Temple View Mysuru',
        'description': 'Chamundi Hills'
    }
]

def test_determine_weather_mood():
    """Verify weather mood mapping."""
    assert determine_weather_mood('thunderstorm with heavy rain') == 'storm'
    assert determine_weather_mood('light drizzle') == 'rain'
    assert determine_weather_mood('snow flurries') == 'snow'
    assert determine_weather_mood('dense mist and fog') == 'fog'
    assert determine_weather_mood('overcast clouds') == 'cloudy'
    assert determine_weather_mood('clear sky') == 'sunny'

def test_unsplash_city_matched_query(app):
    """Verify city-matched photo fetching and attribution."""
    with app.app_context():
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {'X-Ratelimit-Remaining': '45'}
            mock_resp.json.return_value = {'results': MOCK_UNSPLASH_RESULTS}
            mock_get.return_value = mock_resp

            photos = fetch_city_photos_from_unsplash('Mysuru', country='IN', api_key='test_key_123')
            assert photos is not None
            assert len(photos) == 2
            assert photos[0]['photographer_name'] == 'Karnataka Tourism Photographer'
            assert 'utm_source=ClimaSense' in photos[0]['photographer_url']
            assert photos[0]['is_fallback'] is False

def test_unsplash_city_repeated_search_rotation(app):
    """Verify repeated search for the same city selects the next photo from the pool."""
    with app.app_context():
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {'X-Ratelimit-Remaining': '45'}
            mock_resp.json.return_value = {'results': MOCK_UNSPLASH_RESULTS}
            mock_get.return_value = mock_resp

            app.config['UNSPLASH_API_KEY'] = 'test_key_123'
            
            photo1 = get_background_image('Mysuru')
            assert photo1['is_fallback'] is False
            assert photo1['city'] == 'Mysuru'
            
            # Repeated search selects next image in rotation
            photo2 = get_background_image('Mysuru')
            assert photo2['is_fallback'] is False
            assert photo2['city'] == 'Mysuru'
            assert photo2['photographer_name'] != photo1['photographer_name']

def test_unsplash_fallback_when_no_key_or_error(app):
    """Verify fallback photograph is returned with is_fallback: True."""
    with app.app_context():
        app.config['UNSPLASH_API_KEY'] = None
        photo = get_background_image('Mysuru')
        assert photo['is_fallback'] is True
        assert 'url' in photo
        assert 'photographer_name' in photo
        assert 'photographer_url' in photo
        assert 'utm_source=ClimaSense' in photo['photographer_url']

def test_api_background_endpoint(client, app):
    """Verify /api/background/<city> endpoint."""
    with app.app_context():
        app.config['UNSPLASH_API_KEY'] = None
        res = client.get('/api/background/London')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'url' in data
        assert data['is_fallback'] is True
