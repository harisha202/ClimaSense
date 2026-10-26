import pytest
from unittest.mock import patch, MagicMock
from services.encyclopedia_service import (
    fetch_wikipedia_summary,
    clean_extract_to_concise_summary,
    get_city_encyclopedia
)

SAMPLE_WIKI_EXTRACT = (
    "Mysore, officially Mysuru, is a metropolitan city in the southern Indian state of Karnataka. "
    "It is the headquarters of the Mysore district and the Mysore division. "
    "Mysore was the capital of the Kingdom of Mysore for nearly six centuries from 1399 until 1947. "
    "The city is located at the foothills of the Chamundi Hills about 145 km southwest of Bangalore. "
    "Mysore is known for its heritage structures and palaces, including the Mysore Palace, and for the festivities that take place during the Dasara festival."
)

def test_clean_extract_to_concise_summary():
    """Verify summary is approximately 250-400 characters and ends on a sentence boundary."""
    summary = clean_extract_to_concise_summary(SAMPLE_WIKI_EXTRACT, min_chars=220, max_chars=380)
    assert len(summary) >= 220
    assert len(summary) <= 400
    assert summary.endswith('.')

def test_fetch_wikipedia_summary_success(app):
    """Verify grounded Wikipedia REST summary parsing."""
    with app.app_context():
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                'title': 'Mysore',
                'type': 'standard',
                'extract': SAMPLE_WIKI_EXTRACT,
                'content_urls': {'desktop': {'page': 'https://en.wikipedia.org/wiki/Mysore'}},
                'thumbnail': {'source': 'https://upload.wikimedia.org/mysore.jpg'}
            }
            mock_get.return_value = mock_resp

            res = fetch_wikipedia_summary('Mysuru', country='IN')
            assert res['success'] is True
            assert res['city'] == 'Mysuru'
            assert res['source'] == 'Wikipedia'
            assert 'https://en.wikipedia.org/wiki/Mysore' in res['article_url']
            assert len(res['summary']) >= 200
            assert len(res['summary']) <= 400

def test_fetch_wikipedia_unavailable_state(app):
    """Verify honest unavailable state when article is not found."""
    with app.app_context():
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp

            res = fetch_wikipedia_summary('NonExistentCity12345')
            assert res['success'] is False
            assert res['is_available'] is False
            assert 'unavailable' in res['summary'].lower()
            assert 'https://en.wikipedia.org' in res['article_url']

def test_api_encyclopedia_endpoint(client, app):
    """Verify /api/encyclopedia/<city> returns concise info."""
    with app.app_context():
        with patch('services.encyclopedia_service.fetch_wikipedia_summary') as mock_fetch:
            mock_fetch.return_value = {
                'success': True,
                'city': 'Tokyo',
                'title': 'Tokyo',
                'summary': 'Tokyo is the capital and largest city of Japan. Formerly Edo, it is the center of the Greater Tokyo Area.',
                'article_url': 'https://en.wikipedia.org/wiki/Tokyo',
                'source': 'Wikipedia',
                'is_available': True
            }
            res = client.get('/api/encyclopedia/Tokyo')
            assert res.status_code == 200
            data = res.get_json()
            assert data['success'] is True
            assert data['info']['title'] == 'Tokyo'
            assert data['info']['source'] == 'Wikipedia'
