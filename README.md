# 🌤️ Weather Dashboard Application

A modern, feature-rich weather application built with Flask that provides real-time weather data, 5-day forecasts, and dynamic backgrounds based on weather conditions.

## ✨ Features

### Core Functionality
- **Real-time Weather Data** - Current weather conditions for any city worldwide
- **5-Day Forecast** - Detailed weather predictions with temperature, humidity, and wind speed
- **Dynamic Backgrounds** - Beautiful city images that match current weather conditions
- **Intelligent Caching** - Reduces API calls with 5-minute cache duration
- **Search History** - Tracks your last 15 weather searches with timestamps

### User Experience
- **Secure Authentication** - Login system to protect your data
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- **Session Management** - Persistent login sessions across page refreshes
- **User Statistics** - Track total searches, unique cities, and cache performance

### Technical Features
- **API Integration** - OpenWeatherMap for weather data, Unsplash for images
- **Error Handling** - Graceful handling of network errors and invalid inputs
- **Cache Management** - Optional cache clearing for fresh data
- **RESTful API** - Clean API endpoints for all operations

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- OpenWeatherMap API key (free tier)
- Unsplash API key (free tier)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd weather-app
```

2. **Install dependencies**
```bash
pip install flask requests python-dotenv werkzeug
```

3. **Set up API keys**

Create an `api.env` file in the project root:
```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

To get API keys:
- **OpenWeatherMap**: Sign up at https://openweathermap.org/api
- **Unsplash**: Create an app at https://unsplash.com/developers

4. **Run the application**
```bash
python app.py
```

5. **Access the app**
Open your browser and navigate to: `http://localhost:5000`

## 🔐 Default Login Credentials

```
Username: harish
Password: 56789
```

**Security Note**: Change these credentials in `app.py` before deploying to production!

## 📁 Project Structure

```
weather-app/
│
├── app.py                  # Main Flask application
├── api.env                 # API keys (not in git)
├── requirements.txt        # Python dependencies
│
├── templates/
│   ├── show_login.html    # Login page
│   ├── index.html         # Main weather dashboard
│   └── history.html       # Search history page
│
└── static/
    ├── css/
    │   └── styles.css     # Application styles
    └── js/
        └── main.js        # Frontend JavaScript
```

## 🌐 API Endpoints

### Authentication
- `GET /` - Login page
- `POST /login` - Handle login
- `GET /logout` - Logout user

### Weather Data
- `GET /api/weather/<city>` - Get current weather for a city
- `GET /api/forecast/<city>` - Get 5-day forecast
- `GET /api/background/<city>/<description>` - Get background image

### History & Stats
- `GET /api/search-history` - Retrieve search history
- `POST /api/search-history` - Save new search
- `POST /api/clear-history` - Clear all history
- `GET /api/stats` - Get user statistics

### Utilities
- `POST /api/clear-cache` - Clear weather cache

## 🎨 Features in Detail

### Weather Information Displayed
- City name and country
- Current temperature (°C)
- "Feels like" temperature
- Weather description (e.g., "Clear sky", "Light rain")
- Humidity percentage
- Atmospheric pressure
- Wind speed (km/h)
- Weather icon
- Current date and time

### Forecast Information
- Day of week
- Date
- Maximum temperature
- Minimum temperature
- Humidity
- Wind speed
- Weather description
- Weather icon

### Caching System
The app implements intelligent caching to reduce API calls:
- Weather data cached for 5 minutes
- Forecast data cached for 5 minutes
- Manual cache clearing available
- Cache statistics in user dashboard

## 🛠️ Configuration

### Changing Login Credentials
Edit `app.py`:
```python
VALID_USERNAME = "your_username"
VALID_PASSWORD_HASH = generate_password_hash("your_password")
```

### Adjusting Cache Duration
Edit `app.py`:
```python
CACHE_DURATION = 300  # Change to desired seconds
```

### Search History Limit
Edit `app.py`:
```python
history = history[:15]  # Change 15 to desired limit
```

## 🔒 Security Features

- Password hashing using Werkzeug's security module
- Session-based authentication
- Unauthorized access prevention
- API key protection via environment variables
- CSRF protection through session tokens

## 🐛 Troubleshooting

### "City not found" error
- Verify the city name spelling
- Try using the full city name or add country code
- Example: "London,UK" instead of just "London"

### API key errors
- Ensure your API keys are correctly set in `api.env`
- Verify your API keys are active on respective platforms
- Check you haven't exceeded API rate limits

### Application won't start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.7 or higher
- Ensure port 5000 is not already in use

## 📊 API Rate Limits

**OpenWeatherMap Free Tier:**
- 60 calls/minute
- 1,000,000 calls/month

**Unsplash Free Tier:**
- 50 requests/hour

The app's caching system helps stay within these limits.

## 🚀 Deployment

For production deployment:

1. Set a strong secret key:
```python
app.secret_key = 'your-strong-random-secret-key'
```

2. Disable debug mode:
```python
app.run(debug=False)
```

3. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn app:app
```

4. Consider using environment variables for all sensitive data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created by Harish

## 🙏 Acknowledgments

- Weather data provided by [OpenWeatherMap](https://openweathermap.org/)
- Images provided by [Unsplash](https://unsplash.com/)
- Built with [Flask](https://flask.palletsprojects.com/)

---

**Note**: This application is for educational purposes. Always ensure you comply with API terms of service when using in production.
