# 🌤️ ClimaSense - AI-Powered Weather Intelligence Dashboard

A modern, production-grade weather intelligence platform built with **Python 3 (Flask)**, integrating real-time meteorological networks (**OpenWeatherMap**), dynamic high-resolution urban photography strictly from **Unsplash**, and grounded generative intelligence (**Google Gemini API**).

---

## 🌟 Overview & Key Capabilities

ClimaSense provides an immersive, data-grounded weather experience. Rather than displaying isolated numbers, ClimaSense synthesizes live measurements into human-actionable insights, automated daily morning digests, and interactive conversational analytics.

### 🚀 Core Features

1. **Live Grounded Weather Intelligence**
   - Live temperature, feels-like temperature, humidity, atmospheric pressure, wind speed/direction, and visibility for any global city.
   - Grounded **Comfort Score (0–100)** objectively computed from thermal comfort bands, humidity deviation, wind chill, and air quality index.
   - 24-Hour hourly progression timeline and 5-day meteorological forecasts with real probability of precipitation.
   - Comprehensive **Air Quality Index (AQI 1–5)** with individual pollutant concentrations ($\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{O}_3$, $\text{CO}$, $\text{SO}_2$) and true dominant pollutant identification via WHO ratio modeling.
   - Real-time UV Index with risk category levels (Low, Moderate, High, Very High).
   - Severe weather alerts mapped from provider condition thresholds (Flood warnings, high winds, severe thunderstorms, extreme heat).

2. **Google Gemini AI Weather Briefing**
   - High-visibility **AI Weather Briefing Card** directly on the dashboard.
   - Uses server-side Google Gemini (`gemini-2.0-flash` or configured model) fed with a structured JSON context of measured values.
   - Passes API keys strictly via `x-goog-api-key` headers (never in URL parameters) to prevent credential leakage in access logs.
   - Delivers concise, human advice: temperature summary, 24-hour forecast changes, umbrella and rain recommendations, outdoor workout guidance, clothing advice, and UV/AQI health precautions.
   - Transparent **Smart Rules Fallback** with visible provider badge when Gemini is unconfigured, rate-limited, or offline.

3. **Grounded AI Weather Chat Assistant**
   - Dedicated floating/docked interactive AI chat widget (`Ask AI`).
   - One-click suggestion chips:
     - *"Should I carry an umbrella today?"*
     - *"What is the best time to dry clothes?"*
     - *"Is this a good time for outdoor exercise?"*
     - *"What should I wear today?"*
     - *"Compare Bengaluru and London weather"*
   - Intelligent city extraction supporting multi-word cities (*New York*, *Los Angeles*), accented names (*São Paulo*), and stop-word protection (*"for work"* correctly defaults to the current city).
   - Strict whole-word regex matching prevents substring false positives (e.g., *"train"* will not trigger umbrella rain advice; *"brunch"* will not trigger workout advice).
   - Strict 5-day forecast horizon enforcement (transparently explains that real provider forecasts are verifiable up to 5 days ahead, avoiding model hallucination).

4. **Unsplash-Only Dynamic Imagery**
   - **Strictly Unsplash:** Every background and attribution is sourced directly from Unsplash. Wikipedia fallback has been completely removed to avoid flags, logos, or non-scenery images.
   - **Curated Mood Fallbacks:** Curated Unsplash photography per weather mood (sunny, cloudy, rain, storm, snow, fog, night) with verified photographer credits and compliant referral links.
   - **Smart Rate-Limit Awareness:** Respects Unsplash demo tier hourly rate limits with `X-Ratelimit-Remaining` inspection. Real city photos cache for 24 hours, while fallbacks cache for only 5 minutes to retry promptly.

5. **Climate Analytics & Forecast Accuracy Tracker**
   - **Forecast Accuracy Tracking:** Stores forecast projections in `forecast_snapshots` and compares them against next-day station observations to compute grounded accuracy percentages.
   - Interactive Chart.js comparative visualizations supporting 7-day and 30-day horizons with dual-city overlay.
   - Transparent disclaimer: AI provides analytical insights and does not pretend to simulate numerical weather prediction (NWP) atmospheric physics.

6. **Best-Time Planner & City Comparison**
   - **Activity Planner:** Identifies optimal windows today for outdoor running, laundry drying, and commutes based on temperature, wind, humidity, and precipitation probability.
   - **Direct City Comparison:** Dedicated side-by-side comparison screen (`/compare`) evaluating meteorological metrics and comfort ratings.

7. **System Diagnostics & In-Browser Test Bench**
   - Dedicated diagnostic center at `/test` and `/admin` displaying real-time database latency, cache hit rates, model configuration, and live simulator controls.
   - One-click in-browser smoke test suite running real backend assertions.

8. **Production Robustness & Security**
   - **XSS-Safe PDF Exports:** Environmental PDF reports rendered through secure Jinja2 templates.
   - **Authentication Protection:** Rigorous server-side signup validation, brute-force rate limits per IP and username, and instant demo login mode.
   - **PWA & Offline Resilience:** Service worker registered at root `/sw.js` with offline fallback screen (`/offline.html`) and responsive manifest icons.

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
 ┌──────▼──────┐┌──────▼──────┐┌──────▼──────┐┌───▼──────────┐
 │ OpenWeather ││   Unsplash  ││Google Gemini││  PostgreSQL/ │
 │ Meteorological││ Scenery API ││ Generative ││    SQLite    │
 │   Network   ││ (No Wiki)   ││ Intelligence││  + Redis     │
 └─────────────┘└─────────────┘└─────────────┘└──────────────┘
```

---

## ⚙️ Configuration Reference

Create an `api.env` file in the root directory:

```ini
# Flask Core
SECRET_KEY=your_strong_random_secret_key_here
FLASK_ENV=development

# External APIs
OPENWEATHER_API_KEY=your_openweather_api_key
UNSPLASH_API_KEY=your_unsplash_api_key

# Google Gemini AI Configuration
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key
AI_MODEL=gemini-2.0-flash

# Cache & Message Broker
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

> **Unsplash API Note:** The free demo tier has an hourly request limit, which is why successful images are cached for 24 hours. The app never falls back to Wikipedia; if an API call fails or quota is exhausted, curated Unsplash photos per weather mood are displayed with full photographer attribution and retried after 5 minutes.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.9+ or Python 3.10+
- *(Optional)* Redis server (ClimaSense automatically falls back to an in-memory dictionary cache if Redis is not running).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Flask Web Server
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```
Click **"Instant Demo Login"** on the login page for immediate access.

### 4. Run Automated Tests
```bash
python -m pytest
```

### Test Suite Summary:
```text
tests/test_ai.py ..........                                              [ 27%]
tests/test_auth.py ....                                                  [ 37%]
tests/test_full_phases.py .......                                        [ 56%]
tests/test_history.py .                                                  [ 59%]
tests/test_phase0.py ......                                              [ 75%]
tests/test_weather.py .........                                          [100%]

============================= 42 passed in 23.79s =============================
```

---

## 📡 API Endpoints Reference

### Web Pages
- `GET /` - Login Page (with one-click instant demo)
- `GET /signup` - User Registration Page
- `GET /index` - Main Weather Dashboard
- `GET /compare` - Side-by-Side City Comparison Page
- `GET /test` or `/admin` - System Diagnostics & Test Bench Page
- `GET /predictions` - Climate Analytics & Forecast Accuracy Tracker
- `GET /trends` - Historical Trends & City Comparison
- `GET /history` - User Search History (with empty state)
- `GET /about` - Architecture & System Specifications
- `GET /logout` - User Logout

### Operational & Diagnostic APIs
- `GET /health` - Standardized health check for Docker and platforms
- `GET /api/admin/metrics` - Live DB latency, cache hit rate, and AI provider status
- `POST /api/admin/run-smoke-tests` - In-browser automated smoke test execution
- `GET /api/dashboard/<city>` - Combined single-roundtrip dashboard payload
- `GET /api/weather/<city>` - Current conditions, true rain probability, and comfort score
- `GET /api/weather/<city>/briefing` - Grounded Gemini AI Weather Briefing
- `POST /api/weather/chat` - Conversational Weather Assistant
- `GET /api/forecast/<city>` - 5-Day and 24-Hour hourly forecast with timezone alignment
- `GET /api/aqi` - Air Quality Index & true dominant pollutant ratio calculation
- `GET /api/uv` - Real-time UV exposure and risk category
- `GET /api/alerts` - Severe weather alerts (clearly distinguishing inferred vs official)
- `GET /api/background/<city>` - Unsplash scenic photography
- `GET /api/weather/<city>/export/pdf` - XSS-safe printable PDF environmental report
- `GET /api/weather/<city>/export/csv` - Download CSV environmental report


---

## 📑 Project Engineering Reports & Documentation

- 📄 **Complete Markdown Project Report (32 Sections):** [`CLIMASENSE_PROJECT_REPORT.md`](CLIMASENSE_PROJECT_REPORT.md)
- 📑 **Official PDF Project Engineering Report:** [`CLIMASENSE_PROJECT_REPORT.pdf`](CLIMASENSE_PROJECT_REPORT.pdf)
- 🎨 **Visual Design Mockup References:** [`docs/design_references/`](docs/design_references/)

### 📊 Real Meteorological CSV Export Endpoints (Formula-Safe)
- `GET /api/weather/<city>/export/csv` — Current Observed Weather CSV (`climasense_current_weather_{city}.csv`)
- `GET /api/forecast/<city>/export/hourly/csv` — 24-Hour Hourly Timeline CSV (`climasense_hourly_forecast_{city}.csv`)
- `GET /api/forecast/<city>/export/weekly/csv` — 7-Day Extended Outlook CSV (`climasense_weekly_forecast_{city}.csv`)
- `GET /api/compare/export/csv?city1=<c1>&city2=<c2>` — Direct City Comparison CSV (`climasense_comparison.csv`)
- `GET /api/history/export/csv` — Authenticated User Search Telemetry CSV (`climasense_search_history.csv`)
