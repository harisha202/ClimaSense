import pytest

def test_public_pages_render_status_200(client):
    """Verify all public informational pages render successfully without error."""
    public_urls = [
        '/about',
        '/help',
        '/privacy',
        '/terms',
        '/login',
        '/signup'
    ]
    for url in public_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Page {url} failed to render (status {res.status_code})"

def test_protected_pages_redirect_when_unauthenticated(client):
    """Verify protected dashboard pages redirect unauthorized users to login."""
    protected_urls = [
        '/',
        '/home',
        '/weather',
        '/index',
        '/compare',
        '/explore',
        '/predictions',
        '/trends',
        '/history',
        '/settings',
        '/profile',
        '/air-quality',
        '/alerts',
        '/forecast/hourly',
        '/forecast/weekly'
    ]
    for url in protected_urls:
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 302, f"Protected page {url} did not redirect (status {res.status_code})"
        assert '/login' in res.headers['Location']

def test_protected_pages_render_for_authenticated_user(auth_client):
    """Verify protected pages render HTTP 200 for authenticated user."""
    auth_urls = [
        '/',
        '/home',
        '/weather',
        '/compare',
        '/explore',
        '/predictions',
        '/trends',
        '/history',
        '/settings',
        '/profile',
        '/air-quality',
        '/alerts',
        '/forecast/hourly',
        '/forecast/weekly'
    ]
    for url in auth_urls:
        res = auth_client.get(url)
        assert res.status_code == 200, f"Page {url} failed for authenticated user (status {res.status_code})"

def test_unauthenticated_navigation_hidden_on_login_and_signup(client):
    """Verify that main navigation and user controls are completely hidden on login and signup pages."""
    from bs4 import BeautifulSoup
    for auth_path in ['/login', '/signup']:
        res = client.get(auth_path)
        assert res.status_code == 200
        soup = BeautifulSoup(res.data, 'html.parser')
        
        # Main nav menu must not exist
        assert soup.find('ul', class_='nav-menu') is None, f"nav-menu must not be present on {auth_path}"
        
        # Unit toggle button must not exist
        assert soup.find(id='unit-toggle') is None, f"unit-toggle must not be present on {auth_path}"
        
        # Main navigation link texts must not appear in links
        links = [a.get_text(strip=True) for a in soup.find_all('a')]
        for forbidden in ['Home', 'Weather', 'Explore Cities', 'Compare', 'Air Quality', 'Climate', 'Search History', 'Sign Out']:
            assert forbidden not in links, f"{forbidden} link must not appear on {auth_path}"

def test_authenticated_navigation_displayed_on_dashboard(auth_client):
    """Verify that all 6 main navigation links and user controls appear for authenticated users."""
    from bs4 import BeautifulSoup
    res = auth_client.get('/weather')
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    
    # Main nav menu and unit toggle must exist
    assert soup.find('ul', class_='nav-menu') is not None
    assert soup.find(id='unit-toggle') is not None
    
    # All 6 main navigation links must appear
    nav_links = [a.get_text(strip=True) for a in soup.select('ul.nav-menu a.nav-link')]
    expected = ['Home', 'Weather', 'Explore Cities', 'Compare', 'Air Quality', 'Climate']
    assert nav_links == expected

def test_logout_redirects_to_login_and_hides_navigation(auth_client):
    """Verify that logging out redirects to login page where main navigation is hidden."""
    from bs4 import BeautifulSoup
    res = auth_client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    soup = BeautifulSoup(res.data, 'html.parser')
    
    # After logout, on login page, nav-menu must be hidden
    assert soup.find('ul', class_='nav-menu') is None
    assert soup.find(id='unit-toggle') is None

