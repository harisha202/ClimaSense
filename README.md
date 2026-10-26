# 🌤️ ClimaSense - AI-Powered Weather Intelligence Dashboard

A modern, production-grade weather intelligence platform built with **Python 3 (Flask)**, integrating real-time meteorological networks (**OpenWeatherMap**), rotating travel-inspired photography of famous landmarks and scenic landscapes strictly from **Unsplash**, and grounded generative intelligence (**Google Gemini API**).

---

## 🌟 Overview & Key Capabilities

ClimaSense provides an immersive, data-grounded weather experience. The interface adheres to a strict, accessible **Light-Only Design System** (`#F7FBFF` background, `#FFFFFF` cards, `#3185D6` primary blue accents) with zero dark panels, zero jarring dark overlays, and full `prefers-reduced-motion` compliance.

### 🚀 Core Features

1. **Live Grounded Weather Intelligence**
   - Live temperature, feels-like temperature, humidity, atmospheric pressure, wind speed/direction, cloud coverage, sunrise/sunset, and visibility for any global city.
   - Grounded **Comfort Score (0–100)** objectively computed from thermal neutrality bands, relative humidity, wind speed, and air quality index.
   - 24-Hour hourly progression timeline and 5-day meteorological forecasts with real probability of precipitation.
   - Comprehensive **Air Quality Index (AQI 1–5)** with individual pollutant concentrations ($\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{O}_3$, $\text{CO}$, $\text{SO}_2$) and dominant pollutant identification via normalized WHO ratio modeling.
   - Real-time UV Index with risk category levels (Low, Moderate, High, Very High).
   - Severe weather alerts mapped from authoritative meteorological bulletins.

2. **Rotating Scenic & Landmark Background Photography**
   - **Hero Section Background:** Whenever a user searches for a city, the main Weather Dashboard hero background displays rotating high-resolution photography of famous landmarks, tourist destinations, scenic landscapes, beaches, mountains, architecture, and attractive city skylines.
   - **Decorative & Travel-Inspired:** The photograph serves as a travel-inspired scenic backdrop that rotates on subsequent searches, including repeated searches for the same city.
   - **Data Independence:** Changing the photograph never modifies or fabricates weather data; all meteorological values, forecasts, charts, and maps remain strictly tied to the searched city.
   - **Photographer Attribution:** Compliant Unsplash attribution badge displaying the photographer name and UTM referral link.
   - **Smart Caching & Rate-Limit Protection:** A pool of scenic photographs is cached for 24 hours to honor API quotas, rotating sequentially. If the API key is absent, throttled (429), or unauthorized (401/403), curated fallback landmark photography is displayed with explicit `is_fallback: True` metadata.

3. **Google Gemini AI Weather Briefing**
   - High-visibility **AI Weather Briefing Card** directly on the dashboard.
   - Uses server-side Google Gemini (`gemini-2.0-flash` or configured model) fed with a structured JSON context of measured values.
   - Passes API keys strictly via `x-goog-api-key` headers (never in URL parameters) to prevent credential leakage in access logs.
   - Delivers concise, human advice: temperature summary, 24-hour forecast changes, umbrella and rain recommendations, outdoor workout guidance, clothing advice, and UV/AQI health precautions.
   - Transparent **Smart Rules Fallback** with visible provider badge when Gemini is unconfigured, rate-limited, or offline.

4. **Wikipedia City Information**
   - Clean, concise Wikipedia summary extraction (250–400 characters, sentence-boundary aligned).
   - Direct link to authoritative Wikipedia page and source attribution.
   - Clean unavailable state when Wikipedia has no entry for a query.

5. **Grounded AI Weather Chat Assistant**
   - Dedicated floating/docked interactive AI chat widget (`Ask AI`).
   - Bounded 6-turn conversation history with strict system prompt grounding.
   - Transparent provider tagging (`Google Gemini` vs `Smart Rules Engine`).
   - Suggestion chips for umbrellas, clothing recommendations, drying clothes, and workouts.
   - Strict 5-day forecast horizon enforcement to prevent hallucination.

6. **Climate Analytics & Forecast Accuracy Tracker**
   - **Forecast Accuracy Tracking:** Stores forecast projections in `forecast_snapshots` and compares them against next-day station observations to compute grounded accuracy percentages. Honest "pending verification" state when prior snapshots are not yet recorded.
   - Interactive Chart.js comparative visualizations supporting 7-day and 30-day horizons with dual-city overlay.

7. **Authentication & Security**
   - Dedicated **Login** page requiring only `Username` and `Password` (no demo accounts, no fake credentials).
   - Unified login handlers eliminating duplicate route logic.
   - Password confirmation validation and case-insensitive username/email uniqueness.
   - Secure password hashing using Werkzeug scrypt/pbkdf2, session protection, and per-IP/username rate limiting.
   - Post-login navigation redirects directly to the **Home page at `/`**.
   - Formula-injection sanitized CSV exports escaping `=`, `+`, `-`, and `@`.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│  Pure Light UI • 3D Celestial • Leaflet Map • Chart.js │
│  Dynamic Unsplash Hero • AI Chat • Socket.IO Client    │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP / WebSockets
┌───────────────────────────▼────────────────────────────┐
│                  Flask Application                     │
│  Application Factory • Blueprints • Auth & Rate Limits │
└───────┬──────────────┬──────────────┬───────────┬──────┘
        │              │              │           │
 ┌──────▼──────┐┌──────▼──────┐┌──────▼──────┐┌───▼──────────┐
 │ OpenWeather ││   Unsplash  ││Google Gemini││    SQLite    │
 │ Meteorological││ Scenery API ││ Generative ││  + Redis     │
 │   Network   ││ Attributions││ Intelligence││  (Fallback)  │
 └─────────────┘└─────────────┘└─────────────┘└──────────────┘
```

---

## ⚙️ Configuration Reference

Copy `.env.example` to `.env` or `api.env`:

```ini
# Flask Core
SECRET_KEY=your_strong_random_secret_key_here
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db

# External APIs (Stored securely on backend)
OPENWEATHER_API_KEY=your_openweather_api_key
UNSPLASH_API_KEY=your_unsplash_api_key

# Google Gemini AI Configuration
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key
AI_MODEL=gemini-2.0-flash

# Cache & Message Broker (Falls back to in-memory cache if Redis is absent)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

> **Security Note:** API keys are processed server-side only. Secrets are never exposed to browser JavaScript, HTML attributes, URLs, public API responses, or client-side diagnostics.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.8+ (tested on Python 3.8, 3.9, 3.10)
- *(Optional)* Redis server (ClimaSense automatically falls back to an in-memory dictionary cache if Redis is not running).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create your local environment file by copying the template:
```bash
cp .env.example .env
```
*(On Windows PowerShell, use `Copy-Item .env.example .env`)*

Configure your API keys in `.env`:
- `OPENWEATHER_API_KEY`: Real-time weather, forecasts, AQI, and UV data from [OpenWeatherMap](https://openweathermap.org/api).
- `UNSPLASH_API_KEY`: Dynamic landmark and city photography from [Unsplash](https://unsplash.com/developers).
- `AI_API_KEY`: Generative AI weather briefings and interactive assistant from [Google AI Studio](https://aistudio.google.com/).

### 4. Database Initialization
Database tables are created automatically when the application starts for the first time. To initialize or verify the SQLite database schema manually at any time:
```bash
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database tables initialized successfully.')"
```

### 5. Run the Flask Web Server
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

### 6. Run Automated Regression Tests
To run the full test suite with default warning investigation (zero uninvestigated warnings):
```bash
python -m pytest -q -W default
```

### 7. Build Clean Distribution Archive
To package a clean, production-ready distribution archive (`ClimaSense_clean.zip`) excluding all credentials, git history, runtime database, cache files, and nested archives:
```bash
python package_dist.py
```

---

## 📡 Complete Page & Route Reference

### Web Pages
- `GET /` or `/home` — Public Welcoming Home & Discovery Page
- `GET /login` — Clean Login Page (Username & Password only)
- `GET /signup` — User Registration Page
- `GET /weather` or `/index` — Main Weather Dashboard (Authenticated)
- `GET /explore` — Cities Explorer Destination Discovery
- `GET /compare` — Side-by-Side City Comparison Page
- `GET /forecast/hourly` — Dedicated 24-Hour Hourly Forecast Page
- `GET /forecast/weekly` — Dedicated 5- to 7-Day Extended Forecast Page
- `GET /air-quality` — Dedicated Air Quality & UV Health Page
- `GET /alerts` — Severe Weather Alerts & Advisories Page
- `GET /history` — User Search History (Authenticated)
- `GET /predictions` — Climate Analytics & Forecast Accuracy Tracker
- `GET /trends` — Historical Meteorological Trends & City Variance
- `GET /profile` — User Account Profile & Password Management (Authenticated)
- `GET /settings` — User Preferences & Display Units (Authenticated)
- `GET /about` — Architecture & System Specifications
- `GET /help` — Help Center & FAQ
- `GET /privacy` — Privacy Policy
- `GET /terms` — Terms of Service
- `GET /admin` or `/test` — Diagnostics & Interactive Test Bench (Authenticated)
- `GET /logout` — User Sign Out

### Operational & Meteorological APIs
- `GET /health` or `/api/health` — Standardized health check for Docker and platforms
- `GET /api/background/<city>` — Dynamic rotating Unsplash background photograph of famous landmarks and scenic destinations with verified photographer attribution
- `GET /api/weather/<city>` — Current conditions, feels-like, rain probability, and comfort score
- `GET /api/forecast/<city>` — 5-Day and 24-Hour hourly forecast with timezone alignment
- `GET /api/aqi?lat=<lat>&lon=<lon>` — Air Quality Index & dominant pollutant calculation
- `GET /api/uv?lat=<lat>&lon=<lon>` — Real-time UV exposure and risk category
- `GET /api/alerts?lat=<lat>&lon=<lon>` — Severe weather alerts
- `GET /api/weather/<city>/briefing` — Grounded Gemini AI Weather Briefing
- `POST /api/weather/chat` — Conversational Weather Assistant
- `GET /api/dashboard/<city>` — Combined single-roundtrip dashboard payload
- `POST /api/admin/run-smoke-tests` — In-browser automated smoke test execution

### Real Meteorological CSV Export Endpoints (Formula-Injection Protected)
- `GET /api/weather/<city>/export/csv` — Current Observed Weather CSV (`climasense_current_weather_{city}.csv`)
- `GET /api/forecast/<city>/export/hourly/csv` — 24-Hour Hourly Timeline CSV (`climasense_hourly_forecast_{city}.csv`)
- `GET /api/forecast/<city>/export/weekly/csv` — 5-Day Extended Outlook CSV (`climasense_weekly_forecast_{city}.csv`)
- `GET /api/compare/export/csv?city1=<c1>&city2=<c2>` — Direct City Comparison CSV (`climasense_comparison.csv`)
- `GET /api/history/export/csv` — Authenticated User Search Telemetry CSV (`climasense_search_history.csv`)
