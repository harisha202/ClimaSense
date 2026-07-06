from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv('api.env')

# Initialize Flask
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')

# Secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# API Keys from .env file
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')

# Validate keys on startup
if not OPENWEATHER_API_KEY:
    print("❌ ERROR: OPENWEATHER_API_KEY not set in api.env")
if not UNSPLASH_API_KEY:
    print("❌ ERROR: UNSPLASH_API_KEY not set in api.env")

# Login credentials
VALID_USERNAME = "harish"
VALID_PASSWORD_HASH = generate_password_hash("56789")

# Cache for reducing API calls (optional but recommended)
weather_cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

@app.route('/')
def show_login():
    """Show login page"""
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('show_login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    """Handle login POST request"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username == VALID_USERNAME and check_password_hash(VALID_PASSWORD_HASH, password):
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect(url_for('show_login'))

@app.route('/index')
def index():
    """Weather page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('show_login'))
    return render_template('index.html')

@app.route('/history')
def history():
    """History page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('show_login'))
    return render_template('history.html')

@app.route('/api/weather/<city>')
def get_weather(city):
    """Fetch weather data for a city with caching"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    # Check cache first
    cache_key = f"weather_{city.lower()}"
    if cache_key in weather_cache:
        cached_data, cached_time = weather_cache[cache_key]
        if (datetime.now() - cached_time).seconds < CACHE_DURATION:
            print(f"Returning cached weather data for {city}")
            return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=10)
        print(f"OpenWeather response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            now = datetime.now()
            
            weather_data = {
                'city': data.get('name', 'Unknown'),
                'country': data.get('sys', {}).get('country', 'Unknown'),
                'temperature': round(data.get('main', {}).get('temp', 0), 1),
                'feels_like': round(data.get('main', {}).get('feels_like', 0), 1),
                'humidity': data.get('main', {}).get('humidity', 0),
                'pressure': data.get('main', {}).get('pressure', 0),
                'wind_speed': round((data.get('wind', {}).get('speed', 0) * 3.6), 1),
                'description': data.get('weather', [{}])[0].get('description', 'Unknown').capitalize(),
                'icon': data.get('weather', [{}])[0].get('icon', '01d'),
                'date': now.strftime('%A, %B %d, %Y'),
                'time': now.strftime('%I:%M:%S %p'),
                'timestamp': now.isoformat()
            }
            
            # Cache the data
            weather_cache[cache_key] = (weather_data, now)
            
            return jsonify({'success': True, 'data': weather_data})
            
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': 'City not found'})
        elif response.status_code == 401:
            return jsonify({'success': False, 'message': 'Invalid API key. Please check your api.env file'})
        else:
            return jsonify({'success': False, 'message': f'API Error: {response.status_code}'})
            
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/forecast/<city>')
def get_forecast(city):
    """Fetch 5-day forecast for a city using FREE API endpoint with caching"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    # Check cache first
    cache_key = f"forecast_{city.lower()}"
    if cache_key in weather_cache:
        cached_data, cached_time = weather_cache[cache_key]
        if (datetime.now() - cached_time).seconds < CACHE_DURATION:
            print(f"Returning cached forecast data for {city}")
            return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    try:
        # Use FREE 5-day forecast endpoint (3-hour intervals)
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
        print(f"Fetching forecast for: {city}")
        response = requests.get(url, timeout=10)
        print(f"Forecast response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            forecast_list = []
            
            # Process forecast data - get one forecast per day (around noon - 12:00)
            processed_dates = set()
            
            for item in data.get('list', []):
                # Get date from timestamp
                dt = datetime.fromtimestamp(item.get('dt', 0))
                date_str = dt.strftime('%Y-%m-%d')
                
                # Only process if we haven't seen this date yet and it's around noon (12:00)
                if date_str not in processed_dates and '12:00:00' in item.get('dt_txt', ''):
                    processed_dates.add(date_str)
                    
                    forecast_item = {
                        'day': dt.strftime('%A'),
                        'date': dt.strftime('%b %d'),
                        'temp_max': round(item.get('main', {}).get('temp_max', 0), 1),
                        'temp_min': round(item.get('main', {}).get('temp_min', 0), 1),
                        'humidity': item.get('main', {}).get('humidity', 0),
                        'wind_speed': round((item.get('wind', {}).get('speed', 0) * 3.6), 1),
                        'description': item.get('weather', [{}])[0].get('description', 'Unknown').capitalize(),
                        'icon': item.get('weather', [{}])[0].get('icon', '01d')
                    }
                    
                    forecast_list.append(forecast_item)
                    
                    if len(forecast_list) >= 5:
                        break
            
            # If we didn't get 5 days with noon data, get the first entry for each remaining day
            if len(forecast_list) < 5:
                for item in data.get('list', []):
                    dt = datetime.fromtimestamp(item.get('dt', 0))
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    if date_str not in processed_dates:
                        processed_dates.add(date_str)
                        
                        forecast_item = {
                            'day': dt.strftime('%A'),
                            'date': dt.strftime('%b %d'),
                            'temp_max': round(item.get('main', {}).get('temp_max', 0), 1),
                            'temp_min': round(item.get('main', {}).get('temp_min', 0), 1),
                            'humidity': item.get('main', {}).get('humidity', 0),
                            'wind_speed': round((item.get('wind', {}).get('speed', 0) * 3.6), 1),
                            'description': item.get('weather', [{}])[0].get('description', 'Unknown').capitalize(),
                            'icon': item.get('weather', [{}])[0].get('icon', '01d')
                        }
                        
                        forecast_list.append(forecast_item)
                        
                        if len(forecast_list) >= 5:
                            break
            
            # Cache the forecast data
            weather_cache[cache_key] = (forecast_list, datetime.now())
            
            print(f"Total forecast days: {len(forecast_list)}")
            return jsonify({'success': True, 'data': forecast_list})
            
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': 'City not found'})
        elif response.status_code == 401:
            return jsonify({'success': False, 'message': 'Invalid API key. Please check your api.env file'})
        else:
            return jsonify({'success': False, 'message': f'API Error: {response.status_code}'})
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Request timeout. Please try again.'})
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({'success': False, 'message': 'Network error. Please check your connection.'})
    except Exception as e:
        print(f"Forecast API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/background/<city>/<description>')
def get_background(city, description):
    """Fetch city background image based on city and weather description"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        query = f"{city} {description}".replace(' ', '+')
        url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_API_KEY}&per_page=1&orientation=landscape"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                image_url = data['results'][0]['urls']['regular']
                photographer = data['results'][0]['user']['name']
                return jsonify({
                    'success': True, 
                    'image_url': image_url,
                    'photographer': photographer
                })
            return jsonify({'success': False, 'message': 'No images found'})
        else:
            return jsonify({'success': False, 'message': f'Image API Error: {response.status_code}'})
            
    except Exception as e:
        print(f"Background API Error: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading background'})

@app.route('/api/search-history', methods=['GET'])
def get_search_history():
    """Get search history"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    history = session.get('search_history', [])
    return jsonify({'success': True, 'history': history})

@app.route('/api/search-history', methods=['POST'])
def save_search_history():
    """Save search to history"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    city = data.get('city')
    
    if city:
        history = session.get('search_history', [])
        now = datetime.now()
        
        entry = {
            'city': city,
            'timestamp': now.strftime('%Y-%m-%d %I:%M:%S %p'),
            'date': now.strftime('%B %d, %Y'),
            'time': now.strftime('%I:%M %p')
        }
        
        # Remove duplicate city entries
        history = [h for h in history if h.get('city', '').lower() != city.lower()]
        history.insert(0, entry)
        history = history[:15]  # Keep last 15 searches
        
        session['search_history'] = history
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Search saved'})
    
    return jsonify({'success': False, 'message': 'Invalid data'})

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear search history"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    session['search_history'] = []
    session.modified = True
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear weather cache (admin feature)"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    weather_cache.clear()
    return jsonify({'success': True, 'message': 'Cache cleared successfully'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get app statistics"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    history = session.get('search_history', [])
    
    stats = {
        'total_searches': len(history),
        'unique_cities': len(set([h.get('city', '').lower() for h in history])),
        'cache_size': len(weather_cache),
        'session_active': session.get('logged_in', False),
        'username': session.get('username', 'Unknown')
    }
    
    return jsonify({'success': True, 'stats': stats})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("=" * 60)
    print("🌤️  WEATHER APP STARTING...")
    print("=" * 60)
    print("✅ Features Enabled:")
    print("   • User Authentication")
    print("   • Weather API with Caching")
    print("   • 5-Day Forecast")
    print("   • Dynamic Backgrounds")
    print("   • Search History")
    print("   • User Settings Support")
    print("=" * 60)
    print("🌐 App running at: http://localhost:5000")
    print("👤 Login: harish / 56789")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)