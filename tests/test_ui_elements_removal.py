import pytest
from bs4 import BeautifulSoup
from services.unsplash_service import get_background_image

def test_current_weather_csv_button_removed(auth_client):
    """Verify that #export-current-weather-csv button is completely removed from the hero card."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    assert soup.find('a', id='export-current-weather-csv') is None, "export-current-weather-csv button must be removed"

def test_forecast_csv_exports_preserved(auth_client):
    """Verify that hourly and weekly forecast export buttons are preserved."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    assert soup.find('a', id='export-hourly-forecast-csv') is not None, "Hourly CSV export must be preserved"
    assert soup.find('a', id='export-weekly-forecast-csv') is not None, "Weekly CSV export must be preserved"

def test_sunrise_sunset_row_removed(auth_client):
    """Verify that sunrise and sunset display row is completely removed from dashboard."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    assert soup.find(class_='sun-times-row') is None, "sun-times-row must be removed"
    assert soup.find(id='sunrise-time') is None, "sunrise-time element must be removed"
    assert soup.find(id='sunset-time') is None, "sunset-time element must be removed"

def test_floating_ask_ai_button_removed(auth_client):
    """Verify that the floating #chat-widget-toggle Ask AI button is removed."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    assert soup.find(id='chat-widget-toggle') is None, "chat-widget-toggle floating button must be removed"

def test_ai_assistant_panel_and_briefing_preserved(auth_client):
    """Verify that AI weather briefing and AI assistant panel are preserved."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    assert soup.find(id='chat-panel') is not None, "chat-panel must be preserved"
    assert soup.find(id='open-assistant-btn') is not None, "open-assistant-btn shortcut must be present"
    assert soup.find(id='briefing-text') is not None, "briefing-text must be preserved"

def test_about_nav_link_removed_from_base_nav(client):
    """Verify that About link is removed from top navigation bar."""
    res = client.get('/')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    nav_links = [a.get_text(strip=True) for a in soup.select('ul.nav-menu a.nav-link')]
    assert 'About' not in nav_links, "About link must not be in top navigation bar"

def test_wikipedia_elements_and_city_overview_removed_from_dashboard(auth_client):
    """Verify Wikipedia text, Wikipedia Source, and Read city overview link are removed from dashboard."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Source: Wikipedia' not in html, "Source: Wikipedia must be removed from dashboard"
    assert 'Read full article on Wikipedia' not in html, "Read full article on Wikipedia must be removed"
    assert 'Wikipedia Source' not in html, "Wikipedia Source must be removed"
    assert 'Read city overview' not in html, "Read city overview link must be removed"
    assert '#city-info-section' not in html, "city-info-section anchor link must be removed"
    assert 'Cached (' not in html, "Cached timestamp label must not be displayed"

def test_main_weather_container_structure(auth_client):
    """Verify all current weather information is grouped inside one main DIV with separate inner DIV cards."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    main_container = soup.find('div', id='main-weather-container')
    assert main_container is not None, "Main weather container (#main-weather-container) must exist"
    
    # Check inner metric cards
    cards = main_container.find_all(class_='weather-metric-card')
    assert len(cards) >= 7, f"Expected at least 7 inner metric cards, found {len(cards)}"
    
    # Verify core metric elements exist inside the container
    assert main_container.find(id='temperature') is not None
    assert main_container.find(id='weather-desc') is not None
    assert main_container.find(id='humidity') is not None
    assert main_container.find(id='wind-speed') is not None
    assert main_container.find(id='pressure') is not None
    assert main_container.find(id='visibility') is not None
    assert main_container.find(id='cloud-coverage') is not None
    assert main_container.find(id='uv-index') is not None
    assert main_container.find(id='rain') is not None
    assert main_container.find(id='comfort-score-val') is not None

def test_city_matched_background_delhi_and_tokyo(app):
    """Verify Delhi and Tokyo background searches return authentic city-specific photography."""
    with app.app_context():
        delhi_bg = get_background_image('Delhi', '', 'IN')
        assert 'Delhi' in delhi_bg.get('title', '') or delhi_bg.get('city') == 'Delhi'
        assert delhi_bg.get('photographer_name') in ['Sylwia Bartyzel', 'Rishabh Sharma']
        
        tokyo_bg = get_background_image('Tokyo', '', 'JP')
        assert 'Tokyo' in tokyo_bg.get('title', '') or tokyo_bg.get('city') == 'Tokyo'
        assert tokyo_bg.get('photographer_name') in ['Jezael Melgoza', 'Yu Kato']

def test_visible_unsplash_photographer_credit_sentence_removed(client, auth_client):
    """Verify that visible photographer attribution sentences are completely removed from Home and Weather."""
    # Check Home page
    res_home = client.get('/')
    assert res_home.status_code == 200
    soup_home = BeautifulSoup(res_home.data, 'html.parser')
    assert soup_home.find(id='hero-photographer-attribution') is None
    assert 'Photo by' not in soup_home.find('section', class_='home-hero-section').get_text()

    # Check Weather page
    res_weather = auth_client.get('/weather')
    assert res_weather.status_code == 200
    soup_weather = BeautifulSoup(res_weather.data, 'html.parser')
    assert soup_weather.find(id='hero-photographer-attribution') is None
    hero = soup_weather.find('section', class_='weather-hero-panorama')
    assert hero is not None
    assert 'Photo by' not in hero.get_text()

def test_dedicated_map_section_in_dashboard(auth_client):
    """Verify dedicated full-width interactive map section exists in dashboard and modal is removed."""
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    
    # Map section must exist in dashboard flow
    map_section = soup.find(id='weather-map-section')
    assert map_section is not None, "#weather-map-section must exist"
    assert 'map-wide-card' in map_section.get('class', [])
    
    # Inner map container must exist inside map_section
    inner_map = map_section.find(id='map')
    assert inner_map is not None, "#map element must be inside #weather-map-section"
    
    # Map modal must be removed
    assert soup.find(id='map-modal') is None, "#map-modal must be removed"

def test_page_specific_background_classes_and_3d_accents(client, auth_client):
    """Verify distinct background identity class and 3D accents for each page."""
    # Home
    res = client.get('/')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-weather-home' in soup.find('body').get('class', [])
    assert soup.find(class_='accent-home') is not None
    
    # Explore
    res = client.get('/explore')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-weather-explore' in soup.find('body').get('class', [])
    assert soup.find(class_='accent-explore') is not None
    
    # Compare
    res = client.get('/compare')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-weather-compare' in soup.find('body').get('class', [])
    assert soup.find(class_='accent-compare') is not None
    
    # Weather (auth)
    res = auth_client.get('/weather')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-weather-index' in soup.find('body').get('class', [])
    assert soup.find(id='weather-3d-stage') is not None
    
    # Air Quality (auth)
    res = auth_client.get('/air-quality')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-weather-air_quality_page' in soup.find('body').get('class', [])
    assert soup.find(class_='accent-aqi') is not None
    
    # Predictions (auth)
    res = auth_client.get('/predictions')
    soup = BeautifulSoup(res.data, 'html.parser')
    assert 'page-predictions-predictions' in soup.find('body').get('class', [])
    assert soup.find(class_='accent-climate') is not None

