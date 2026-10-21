# ClimaSense — Comprehensive Meteorological Intelligence & City Discovery Platform
## Final Project Engineering & Architectural Report

---

### 1. Project Title
**ClimaSense — AI-Powered Weather Intelligence, City Discovery Platform & Real-Time Meteorological Monograph System**

---

### 2. Executive Summary
ClimaSense is an enterprise-grade weather intelligence and geographic discovery web application developed using Python 3, Flask, SQLite, Redis, and Leaflet.js. The platform integrates real-time observational meteorological telemetry from OpenWeatherMap, dynamic high-resolution urban photography from Unsplash, grounded conversational intelligence from Google Gemini AI, and comprehensive 38-section municipal monographs with live word count tracking. Designed under a strict light-only pastel visual design system, the application delivers current weather metrics, 24-hour hourly spline curve projections, 7-day daily forecasts, side-by-side multi-city comparisons, multi-pollutant air quality health diagnostics, interactive geographical mappings, and CSV exports sanitised against formula injection.

---

### 3. Introduction
Standard weather portals often present isolated numeric values (temperatures, pressure figures, humidity percentages) without providing actionable human context or environmental narrative. ClimaSense bridges meteorological science and end-user decision making by combining real-time observations with grounded AI briefings, dynamic scenic context, and structured municipal encyclopedias.

---

### 4. Problem Statement
1. **Raw Numerical Overload:** Typical meteorological dashboards present disconnected metrics without actionable guidance on clothing, travel, or outdoor activities.
2. **Visual Clutter & Dark Themes:** Many weather dashboards use high-contrast dark modes or generic stock graphics that detract from readability and municipal identity.
3. **Data Hallucination Risks:** Generative AI tools often fabricate weather values if disconnected from real-time meteorological sensor feeds.
4. **Data Portability Gaps:** Users frequently lack simple, secure mechanisms to export genuine observed readings and forecasts to standard spreadsheet formats without risk of formula injection.
5. **Incomplete Municipal Context:** Weather is intrinsically tied to geographic, demographic, and climate-historical contexts that are absent from conventional forecast widgets.

---

### 5. Objectives
- Engineer a unified, responsive light-only web application adhering strictly to low-saturation pastel aesthetics (`#F7FBFF` base, `#FFFFFF` cards, `#3185D6` brand blue).
- Provide real-time meteorological data feeds for global cities with sub-second response times and Redis/in-memory caching.
- Ground Google Gemini AI assistance in verified meteorological readings to eliminate hallucinations.
- Supply genuine CSV data exports for current conditions, hourly timelines, weekly forecasts, city comparisons, and user search history.
- Implement municipal monographs targeting 4,000+ words across 38 distinct urban and meteorological topics.
- Enforce SQLite as the primary database for local and deployment storage.

---

### 6. Scope and Intended Users
- **Commuters & Travelers:** Checking real-time conditions, precipitation risk, and clothing advice.
- **Meteorology Students & Researchers:** Exporting authentic hourly and weekly telemetry to CSV for empirical analysis.
- **Urban Explorers & Tourists:** Discovering international cities with scenic photography and geographical encyclopedias.
- **Sensitive Respiratory Demographics:** Monitoring air quality index (AQI) values and pollutant breakdowns (PM2.5, PM10, O3, NO2).

---

### 7. Existing System Limitations (Resolved)
- **Syntax Error in script.js:** A duplicated closing bracket previously prevented JavaScript execution, causing search, autocomplete, and briefings to fail. (*Fixed*)
- **Deprecated Gemini Model Identifier:** Legacy code referenced `gemini-1.5-flash`, which has been superseded. (*Fixed & upgraded to configurable model*)
- **API Key Leakage in Error Logs:** Exceptions previously logged full URLs with embedded keys. (*Fixed; keys now pass via `x-goog-api-key` headers*)
- **City Extraction Ambiguity in Chat:** City parsing previously mistook query stop-words for city names. (*Fixed with regex whole-word boundaries*)
- **Dark Theme Contamination:** Dark panels previously disrupted visual consistency. (*Fixed; 100% light pastel theme enforced*)
- **Pytest Dependencies Cleaned:** Pytest testing harnesses and dependencies removed from production runtime per specification. (*Fixed*)

---

### 8. Actual Technology Stack
- **Backend Framework:** Python 3.8+ / Flask 3.0+
- **Architecture Pattern:** Application Factory (`app.py`), Modular Blueprints (`routes/`)
- **Database & ORM:** SQLAlchemy with SQLite (`sqlite:///app.db`)
- **Session & Auth Management:** Flask-Login with bcrypt password hashing
- **Cache & Message Broker:** Redis with transparent in-memory dictionary fallback
- **Real-Time WebSockets:** Flask-SocketIO (for live city discussion rooms)
- **Frontend Stack:** Semantic HTML5, CSS3 Custom Properties (CSS variables), Vanilla JavaScript (ES6+)
- **Visualizations:** Chart.js (spline curves and historical charts), Leaflet.js (interactive maps)
- **External APIs:** OpenWeatherMap API, Unsplash Scenery API, Google Gemini AI API

---

### 9. System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                       Client Browser                        │
│  Light Pastel UI • CSS 3D Transforms • Leaflet • Chart.js   │
└──────────────────────────────▲──────────────────────────────┘
                               │ HTTP / JSON / SSE / WS
┌──────────────────────────────▼──────────────────────────────┐
│                    Flask Application Core                   │
│   Auth • CSRF • Rate Limiter • Blueprints • Error Handlers  │
└──────────┬───────────────────┬───────────────────┬──────────┘
           │                   │                   │
    ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
    │ OpenWeather │     │   Unsplash  │     │Google Gemini│
    │  Telemetry  │     │ City Photos │     │  AI Engine  │
    └─────────────┘     └─────────────┘     └─────────────┘
           │                   │                   │
    ┌──────▼───────────────────▼───────────────────▼──────────┐
    │          Caching Layer (Redis / Memory Cache)           │
    └──────────────────────────┬──────────────────────────────┘
                               │
    ┌──────────────────────────▼──────────────────────────────┐
    │                SQLite Relational Database               │
    │         Users • SavedCities • SearchHistory             │
    └─────────────────────────────────────────────────────────┘
```

---

### 10. Frontend and Backend Architecture
- **Frontend Organization:**
  - Layout template: `templates/base.html` defines navbar, navigation links, toasts, and script imports.
  - Page templates: 21 modular templates covering home, dashboard, exploration, auth, comparison, air quality, alerts, profile, settings, and legal terms.
  - Shared styling: `static/css/style.css` contains the design tokens, layout grids, cards, and animations.
  - 3D Atmosphere: `static/js/weather3d.js` renders CSS 3D sun/cloud celestial scenes based on live weather condition codes.
- **Backend Organization:**
  - `routes/auth.py`: Authentication, registration, password recovery, profile management.
  - `routes/weather.py`: Home discovery, current conditions, comparison, map endpoints, and municipal monographs.
  - `routes/forecast.py`: 5-day / 3-hour forecasts, hourly curves, and weekly aggregations.
  - `routes/history.py`: Search history telemetry and CSV exports.

---

### 11. Actual Pages and Navigation
1. **Home (`/` & `/home`):** Welcoming weather discovery page matching the master visual mockup (Hero search pill, 8 pastel feature cards, 6 destination cards with category filters, Leaflet world map, AI assistant preview).
2. **Weather Dashboard (`/index` & `/weather`):** Panoramic city hero, floating card, 3D atmospheric container, 3-column data grid, bottom discovery row, and 38-section municipal monograph.
3. **Sign In (`/login`):** Split decorative card explaining core features with instant demo login.
4. **Sign Up (`/signup`):** Account creation with real-time password strength meter.
5. **Password Recovery (`/forgot-password`):** Verified password reset flow.
6. **Explore Global Cities (`/explore`):** Interactive destination explorer with continent filters.
7. **City Comparison (`/compare`):** Direct side-by-side metric comparison and comfort scores.
8. **Hourly Forecast (`/forecast/hourly`):** 24-hour timeline and Chart.js spline curve.
9. **Weekly Forecast (`/forecast/weekly`):** 7-day daily outlook with high/low temperature spreads.
10. **Air Quality & Health (`/air-quality`):** Multi-pollutant analysis (PM2.5, PM10) and WHO risk ratings.
11. **Weather Alerts (`/alerts`):** Active meteorological advisories and warnings.
12. **Search History (`/history`):** User search logs with repeat-search shortcuts and CSV export.
13. **User Profile (`/profile`):** Account information and security password updates.
14. **Settings (`/settings`):** Unit switches (°C/°F, km/h, mph, m/s) and visual preference toggles.
15. **Help Center & FAQ (`/help`):** Comprehensive user guides and PWA installation tips.
16. **Privacy Policy (`/privacy`):** Privacy practices and API security guarantees.
17. **Terms of Service (`/terms`):** Terms of usage and disclaimers.
18. **About (`/about`):** Architecture and system specifications.

---

### 12. Actual Routes, Services, and Components
- `GET /` & `GET /home` — Home Discovery Page
- `GET /index` & `GET /weather` — Primary Weather Dashboard
- `GET /login`, `POST /login`, `POST /login/demo`, `GET /logout` — Authentication endpoints
- `GET /api/weather/<city>` — Current meteorological observation JSON
- `GET /api/forecast/<city>` — 5-day / 3-hour forecast progression
- `GET /api/background/<city>` — Unsplash city photograph resolver
- `GET /api/encyclopedia/<city>` — 38-section municipal monograph engine
- `POST /api/weather/chat` — Grounded Gemini AI conversational assistant
- `GET /api/weather/<city>/export/csv` — Current weather CSV export
- `GET /api/forecast/<city>/export/hourly/csv` — Hourly forecast CSV export
- `GET /api/forecast/<city>/export/weekly/csv` — Weekly forecast CSV export
- `GET /api/compare/export/csv` — City comparison CSV export
- `GET /api/history/export/csv` — Search history CSV export

---

### 13. Weather API Integration
- **Provider:** OpenWeatherMap API v2.5 (`weather` and `forecast` endpoints).
- **Extracted Fields:** City, country code, coordinates, temperature, feels-like temperature, humidity, atmospheric pressure, wind speed, wind direction degrees, visibility, cloud cover, sunrise/sunset UTC timestamps.
- **Failure Handling:** Returns HTTP 404 with friendly user message on invalid city queries; transparent fallback to in-memory cached responses during connectivity interruptions.

---

### 14. Unsplash Scenery Integration
- **Provider:** Unsplash API (`https://api.unsplash.com/search/photos`).
- **Functionality:** Queries city-specific landscape photography. Sets panoramic background image on the hero section and thumbnail on the Discover card.
- **Attribution Compliance:** Renders photographer name with verified referral link to Unsplash (`utm_source=ClimaSense`).
- **Security:** Access key remains entirely on the server; never exposed to frontend bundles.

---

### 15. Gemini AI Integration
- **Provider:** Google Gemini API (`v1beta/models/{model}:generateContent`).
- **Grounded Architecture:** Meteorological values are formatted into structured JSON before being passed to Gemini. The model is instructed to formulate practical advice (umbrella usage, clothing, workout windows) strictly from the provided data.
- **Log Security:** Keys are passed via `x-goog-api-key` HTTP header. Raw network errors are sanitised before logging to prevent key leakage.

---

### 16. City Encyclopedia & Monograph Implementation
- **Architecture:** `services/encyclopedia_service.py` provides an authoritative municipal database generating 38 structured sections per city.
- **Sections Covered:** Overview, Etymology, Geography, Topography, Climate & Weather History, Municipal Governance, Demographics, Economy, Transport Infrastructure, Culture & Heritage, Architecture, Parks & Ecology, Education, Public Health, Sports, Tourism, Gastronomy, Sister Cities, and Future Urban Development.
- **Metrics:** Displays live measured word count (targeting 4,000+ words) and estimated reading time.

---

### 17. Map Implementation
- **Library:** Leaflet.js v1.9.4 with OpenStreetMap tile provider.
- **Containers:** Dedicated `#home-globe-map` container on the Home page and `#map-modal` on the Dashboard.
- **Markers:** Accurately positioned using latitude and longitude coordinates from OpenWeatherMap.

---

### 18. Database & Data Flow
- **Engine:** SQLite (`sqlite:///app.db`).
- **Models:**
  - `User`: Handles credentials, hashed passwords, demo flags, and timestamps.
  - `SavedCity`: One-to-many relationship mapping user accounts to bookmarked locations.
  - `SearchHistory`: Records queries, timestamps, and observed temperatures for historical analytics.
- **Isolation:** Saved cities and search histories are strictly scoped to the authenticated user's ID.

---

### 19. Redis and Celery Infrastructure
- **Redis:** Configured via `REDIS_URL` in `config.py`. Automatically falls back to an in-memory dictionary if Redis is unavailable locally.
- **Celery:** Configured for background tasks and daily digest emails (`tasks/celery_tasks.py`).

---

### 20. CSV Export Implementation
- **Current Weather CSV (`climasense_current_weather_{city}.csv`):** City, Country, Timestamp (UTC), Temperature (°C), Feels Like (°C), Condition, Humidity (%), Wind Speed (m/s), Wind Direction, Pressure (hPa), Visibility (km).
- **Hourly Forecast CSV (`climasense_hourly_forecast_{city}.csv`):** City, Country, Local Time, UTC Time, Temperature (°C), Condition, Rain Probability (%), Humidity (%), Wind Speed (m/s).
- **Weekly Forecast CSV (`climasense_weekly_forecast_{city}.csv`):** City, Country, Date, Day of Week, Min Temp (°C), Max Temp (°C), Midday Condition, Rain Probability (%),
- **City Comparison CSV (`climasense_comparison.csv`):** Side-by-side metric matrix comparing temperatures, humidity, wind, and pressure with calculated differences.
- **Search History CSV (`climasense_search_history.csv`):** Query ID, City, and Search Timestamp.
- **Security Policy:** All CSV cells are sanitized against spreadsheet formula injection by prepending a single quote (`'`) if the text begins with `=`, `+`, `-`, `@`, tab, or newline characters.

---

### 21. Security and Authentication
- **Password Protection:** Uses `bcrypt` with salt hashing.
- **Session Security:** HTTP-only cookies with configurable `SESSION_COOKIE_SECURE`.
- **API Protection:** Server-side proxying ensures OpenWeather, Unsplash, and Gemini API keys are never delivered to the client.
- **Reflected XSS Prevention:** PDF and export templates strictly escape user-supplied strings through Jinja2 auto-escaping.
- **Secret Validation:** Application startup enforces a non-default `SECRET_KEY` in production environments.

---

### 22. Error Handling and Caching
- **Network Resilience:** Graceful error messages and retry prompts on network dropouts.
- **Cache TTL Hierarchy:** Weather observations cache for 5 minutes (300s); Unsplash scenery caches for 24 hours (86400s); AI briefings cache for 30 minutes (1800s).
- **No Stale AI:** Stale weather data is purged before generating new AI briefings.

---

### 23. Installation and Configuration
```bash
# 1. Clone repository & enter directory
cd ClimaSense

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OpenWeather, Unsplash, and Gemini API keys

# 5. Run database initialization & startup
python app.py
```

---

### 24. Known Limitations
1. **Demo Tier Rate Limits:** Unsplash demo access keys allow up to 50 requests/hour; OpenWeather free tier permits 60 calls/minute. Caching layers are tuned to prevent exceeding these ceilings.
2. **5-Day Numerical Horizon:** Numerical meteorological forecasts are scientifically verifiable up to 5 days ahead via the standard OpenWeather API; requests beyond 5 days transparently communicate forecast limitations.
3. **Hardware Acceleration:** Advanced CSS 3D transforms require standard WebGL/CSS 3D browser support; low-spec devices gracefully receive static layered fallback visuals.

---

### 25. Conclusion
ClimaSense successfully combines scientific meteorological data with accessible human presentation. By implementing a strict light pastel design system, formula-safe CSV exports, grounded AI interpretations, and authoritative municipal monographs, the application establishes a high benchmark for modern academic and commercial weather portals.
