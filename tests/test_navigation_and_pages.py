import pytest

def test_public_pages_render_status_200(client):
    """Verify all public informational pages render successfully without error."""
    public_urls = [
        '/',
        '/home',
        '/compare',
        '/explore',
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
        '/weather',
        '/index',
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
        '/weather',
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
