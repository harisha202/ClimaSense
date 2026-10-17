# 🌤️ ClimaSense - AI-Powered Weather Intelligence Dashboard

A modern, production-grade weather intelligence platform built with **Python 3 (Flask)**, integrating real-time meteorological networks (**OpenWeatherMap**), dynamic high-resolution urban photography (**Unsplash**), and grounded generative intelligence (**Google Gemini API**).

---

## 🌟 Overview & Key Capabilities

ClimaSense provides an immersive, data-grounded weather experience. Rather than displaying isolated numbers, ClimaSense synthesizes live measurements into human-actionable insights, automated daily morning digests, and interactive conversational analytics.

### 🚀 Core Features

1. **Live Grounded Weather Intelligence**
   - Live temperature, feels-like temperature, humidity, atmospheric pressure, wind speed/direction, and visibility for any global city.
   - Grounded **Comfort Score (0–100)** objectively computed from thermal comfort bands, humidity deviation, wind chill, and air quality index.
   - 24-Hour hourly progression timeline and 5-day meteorological forecasts.
   - Comprehensive **Air Quality Index (AQI 1–5)** with individual pollutant concentrations ($\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{O}_3$, $\text{CO}$, $\text{SO}_2$) and dominant pollutant identification.
   - Real-time UV Index with risk category levels (Low, Moderate, High, Very High).
   - Severe weather alerts mapped from provider condition thresholds (Flood warnings, high winds, severe thunderstorms, extreme heat).

2. **Google Gemini AI Weather Briefing**
   - High-visibility **AI Weather Briefing Card** directly on the dashboard.
   - Uses server-side Google Gemini (`gemini-1.5-flash` or configured model) fed with a structured JSON context of measured values.
   - Delivers concise, human advice: temperature summary, 24-hour forecast changes, umbrella and rain recommendations, outdoor workout guidance, clothing advice, and UV/AQI health precautions.
   - Includes real-time freshness timestamp, skeleton loading state, instant cache refresh control, and a transparent **Grounded Rule Engine fallback** if Gemini is offline or unconfigured.

3. **Grounded AI Weather Chat Assistant**
   - Dedicated floating/docked interactive AI chat widget (`Ask AI`).
   - One-click suggestion chips:
     - *"Should I carry an umbrella today?"*
     - *"What is the best time to dry clothes?"*
     - *"Is this a good time for outdoor exercise?"*
     - *"What should I wear today?"*
     - *"Compare Bengaluru and London weather"*
   - Automatic multi-city extraction and parallel data gathering before prompt assembly.
   - Built-in prompt injection defense, message length boundaries (300 chars), and per-user rate limiting (10 queries/min).
   - Strict 5-day forecast horizon enforcement (transparently explains that real provider forecasts are verifiable up to 5 days ahead, avoiding model hallucination).

4. **Dynamic Visuals, Emojis & Translucent Glassmorphism**
   - **Preserved Unsplash Integration:** High-resolution dynamic city photographs fetched based on the searched city with Wikipedia REST API fallback and photographer attribution.
   - **Translucent Glass Cards:** Softly blurred, pale-blue/white glassmorphism cards with adjustable opacity, subtle borders, and soft shadows—ensuring the background photograph remains visible.
   - **Dynamic Weather Emojis:** Accurately mapped from OpenWeather condition codes and day/night icons (`☀️ 🌤️ ⛅ ☁️ 🌧️ 🌦️ ⛈️ ❄️ 🌫️ 🌙 🌬️ 🌈`).
   - **Lightweight CSS Atmospheric Effects:** Radiant sunshine glow, animated falling rain, thunderstorm lightning flashes, drifting clouds, and snow particles.
   - Accessible contrast, interactive 3D card depth on hover, and full `@media (prefers-reduced-motion: reduce)` compliance.

5. **Climate Analytics & Projections**
   - Honest, transparent analytics distinguishing **Observed Historical Logs** (`weather_logs` table), **OpenWeather 24-Hour Forecasts**, and **Gemini Trend Interpretations**.
   - Interactive Chart.js comparative visualizations supporting 7-day and 30-day horizons with dual-city overlay.
   - Transparent disclaimer: AI provides analytical insights and does not pretend to simulate numerical weather prediction (NWP) atmospheric physics.

6. **Smart Daily Email Digest (Celery + Redis)**
   - Celery background worker periodically checks saved cities for each registered user.
   - Generates a personalized daily digest with exactly one tailored weather tip per city.
   - Grounded rule-based fallback if Gemini is offline.
   - Mobile-responsive layout sent via Flask-Mail.

7. **Production Robustness & Security**
   - **Search Race-Condition Protection:** Search sequence ID tracking prevents stale, out-of-order responses from overwriting newer user searches.
   - **Server-Side Key Isolation:** Gemini, OpenWeather, and Unsplash keys are strictly maintained on the server and masked in system status diagnostics.
   - **Multi-Layered Caching:** Redis cache with transparent in-memory dictionary fallback when Redis is absent.
   - **Session Security:** Passwords cryptographically hashed via Bcrypt; routes protected with Flask-Login.
   - **PWA Ready:** Service worker shell caching and web app manifest.
   - **Data Exports:** Instant CSV export and printable environmental PDF reports.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│  Glassmorphic UI • 3D Tilt • Leaflet Map • Chart.js    │
│  Dynamic Visual Effects • AI Chat • Socket.IO Client   │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP / WebSockets
┌───────────────────────────▼────────────────────────────┐
│                  Flask Application                     │
│  Application Factory • Blueprints • Auth & Rate Limits │
└───────┬──────────────┬──────────────┬───────────┬──────┘
        │              │              │           │
┌───────▼──────┐┌──────▼──────┐┌──────▼─────┐┌───▼───────────┐
│ Google Gemini││ OpenWeather ││  Unsplash  ││ Redis / Celery│
│ REST API     ││ Live/Forecast││  Dynamic   ││ Caching &     │
│ Briefing/Chat││ AQI/UV/Alert││ Background ││ Daily Digests │
└──────────────┘└─────────────┘└────────────┘└───────────────┘
        │              │              │           │
┌───────▼──────────────▼──────────────▼───────────▼──────────┐
│              SQLite / SQLAlchemy Database                  │
│       Users • Saved Cities • Search History • Logs         │
└────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Environment Configuration

Configuration is loaded from `api.env` (or `.env`). Placeholders can be found in `.env.example`:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Flask session encryption key | `dev_secret_key` |
| `FLASK_ENV` | Environment mode | `development` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///app.db` |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API Key | *(Provided in api.env)* |
| `UNSPLASH_API_KEY` | Unsplash Developer Access Key | *(Provided in api.env)* |
| `AI_PROVIDER` | AI provider identifier | `gemini` |
| `AI_API_KEY` | Google Gemini API Key | *(Set your key or leave blank for rule fallback)* |
| `AI_MODEL` | Google Gemini model identifier | `gemini-1.5-flash` |
| `AI_BRIEFING_CACHE_TTL`| AI briefing cache lifetime (seconds) | `1800` (30 minutes) |
| `AI_CHAT_RATE_LIMIT` | Max chat queries per minute per user | `10` |
| `AI_MAX_OUTPUT_TOKENS` | Max tokens generated by Gemini | `800` |
| `AI_REQUEST_TIMEOUT` | Gemini HTTP timeout (seconds) | `10` |
| `REDIS_URL` | Redis cache & Celery broker | `redis://localhost:6379/0` |
| `CACHE_TTL_SECONDS` | Weather data cache TTL | `300` (5 minutes) |
| `MAIL_SERVER` | SMTP Mail Server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP Port | `587` |
| `MAIL_USE_TLS` | SMTP TLS flag | `True` |
| `MAIL_USERNAME` | SMTP Email Account | `your_email@gmail.com` |
| `MAIL_PASSWORD` | SMTP App Password | `your_app_password` |

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.8+
- *(Optional)* Redis server (ClimaSense automatically falls back to an in-memory dictionary cache if Redis is not running).

### 2. Install Dependencies
```powershell
cd c:\Users\91797\OneDrive\Desktop\ClimaSense
pip install -r requirements.txt
```

### 3. Run the Flask Web Server
```powershell
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

### 4. (Optional) Run Celery Worker & Scheduler
For asynchronous background cache warming and daily email digests:
```powershell
# Celery Worker
celery -A tasks.celery_tasks.celery worker --loglevel=info

# Celery Beat Scheduler
celery -A tasks.celery_tasks.celery beat --loglevel=info
```

---

## 🧪 Automated Testing

The project includes an automated test suite verifying authentication, search history, OpenWeather endpoints, UV, exports, Gemini briefings, chat groundings, rate limits, and fallback resilience:

```powershell
python -m pytest
```

### Test Suite Summary:
```text
tests\test_ai.py ..........                                              [ 50%]
tests\test_auth.py ....                                                  [ 70%]
tests\test_history.py .                                                  [ 75%]
tests\test_weather.py .....                                              [100%]

============================= 20 passed in 9.40s ==============================
```

---

## 📡 API Endpoints Reference

### Web Pages
- `GET /` - Login Page
- `GET /signup` - User Registration Page
- `GET /index` - Main Weather Dashboard
- `GET /predictions` - Climate Analytics & Projections
- `GET /trends` - Historical Trends & City Comparison
- `GET /history` - User Search History
- `GET /about` - Architecture & System Specifications
- `GET /logout` - User Logout

### Weather & AI APIs
- `GET /api/weather/<city>` - Current conditions, rain probability, and grounded comfort score
- `GET /api/weather/<city>/briefing` - Grounded Gemini AI Weather Briefing (`?refresh=true` for cache bypass)
- `POST /api/weather/chat` - Conversational Weather Assistant (body: `{"message": "...", "city": "..."}`)
- `GET /api/forecast/<city>` - 5-Day and 24-Hour hourly forecast
- `GET /api/weather/geo` - Coordinates geolocation lookup (`?lat=...&lon=...`)
- `GET /api/aqi` - Air Quality Index & pollutant components (`?lat=...&lon=...`)
- `GET /api/uv` - Real-time UV exposure and risk category
- `GET /api/alerts` - Severe weather alerts
- `GET /api/background/<city>` - Place-specific Unsplash photograph with fallback
- `GET /api/tiles/<layer>/<z>/<x>/<y>.png` - OpenWeather radar map tile proxy
- `GET /api/predictions/<city>` - Observed history vs 24h projection vs Gemini trend insight
- `GET /api/trends/<city>` - Stored historical logs (`?range=7d` or `30d`)
- `GET /api/system-status` - Operational status with masked server credentials
- `GET /api/weather/<city>/export/csv` - Download CSV environmental report
- `GET /api/weather/<city>/export/pdf` - Printable PDF environmental report

### Saved Cities & History
- `GET /api/cities/saved` - Fetch bookmarked cities
- `POST /api/cities/save` - Bookmark a city
- `POST /api/cities/unsave` - Remove a bookmarked city
- `GET /api/search-history` - Fetch recent search history
- `POST /api/clear-history` - Clear search history

---

## 🔒 Security & Privacy

1. **API Key Protection:** All provider credentials (OpenWeatherMap, Unsplash, Google Gemini) are isolated server-side. Public APIs never output raw keys.
2. **Rate Limiting:** Dedicated in-memory/Redis rate limiting prevents API abuse on authentication routes and AI chat endpoints.
3. **Prompt Injection Hardening:** User chat questions are stripped of instruction-override prefixes and bounded to 300 characters before being framed as queries against real weather data.
4. **Data Isolation:** User search history, bookmarked cities, and email digests are scoped strictly to the authenticated `user_id`.
