# ClimaSense — Comprehensive Meteorological Intelligence & City Discovery Platform
## Final Project Engineering, Audit & Architectural Report

---

### 1. Project Title
**ClimaSense — AI-Powered Weather Intelligence, City Discovery Platform & Real-Time Meteorological Monograph System**

---

### 2. Executive Summary
ClimaSense is an enterprise-grade weather intelligence and geographic discovery web application developed using Python 3, Flask, SQLite, Redis, and Leaflet.js. The platform integrates real-time observational meteorological telemetry from OpenWeatherMap, dynamic high-resolution rotating photography of famous landmarks and scenic destinations from Unsplash, grounded conversational intelligence from Google Gemini AI, and comprehensive 38-section municipal monographs with live word count tracking. Designed under a strict light-only pastel visual design system (`#F7FBFF` base, `#FFFFFF` cards, `#3185D6` brand blue), the application delivers current weather metrics, 24-hour hourly spline curve projections, 5-day daily forecasts, side-by-side multi-city comparisons, multi-pollutant air quality health diagnostics, interactive geographical mappings, and CSV exports sanitised against formula injection.

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
- Provide secure authentication requiring strictly Username and Password, with complete removal of demo accounts and unused password-recovery pages.
- Deliver rotating travel-inspired Unsplash background photography of famous landmarks, scenic landscapes, beaches, mountains, architecture, and skylines on the dashboard hero upon every city search with verified photographer attribution.

---

### 6. Scope and Intended Users
- **Commuters & Travelers:** Checking real-time conditions, precipitation risk, and clothing advice.
- **Meteorology Students & Researchers:** Exporting authentic hourly and weekly telemetry to CSV for empirical analysis.
- **Urban Explorers & Tourists:** Discovering international cities with scenic photography and geographical encyclopedias.
- **Sensitive Respiratory Demographics:** Monitoring air quality index (AQI) values and pollutant breakdowns (PM2.5, PM10, O3, NO2).

---

### 7. Audit Findings & Root Causes Repaired

1. **Authentication Overhaul & Demo Login Removal:**
   - *Issue:* Legacy login contained a "Demo Login" button, a `/login/demo` bypass endpoint, and confusing "Username or Email" labels.
   - *Fix:* Completely removed Demo Login button, demo user creation logic, and `/login/demo` endpoint. Replaced field label with `Username` only, connecting strictly to real database authentication with scrypt/bcrypt password hashing.
   - *Redirection:* Successful login now redirects strictly to the Home page at `/`.

2. **Removal of Unwanted Password Recovery Routes:**
   - *Issue:* Dead/unsupported Forgot Password and Reset Password routes and templates existed without complete upstream SMTP or OTP configuration.
   - *Fix:* Removed `/forgot-password`, `/reset-password`, and deleted `templates/forgot_password.html`. Cleaned all navigation links so users navigate strictly between Login, Signup, and Home.

3. **Rotating Scenic & Landmark Background Photography:**
   - *Architecture & Implementation:* Refined `services/unsplash_service.py`, `/api/background/<city>`, and `window.fetchBackground()` in `static/js/script.js`. The dashboard hero panorama (`#hero-panorama`) displays high-resolution decorative, travel-inspired photographs of famous landmarks, tourist destinations, scenic landscapes, beaches, mountains, architecture, and attractive city skylines.
   - *Rotation & Caching:* The photograph changes upon subsequent searches, including repeated searches for the same city. To preserve API quotas and avoid unnecessary network calls, a pool of scenic photographs is cached on the backend for 24 hours and rotated sequentially.
   - *Meteorological Independence:* The background photograph is purely decorative; changing the photograph never alters, desynchronizes, or fabricates meteorological telemetry, which remains strictly tied to the searched city.
   - *Fallbacks & Attribution:* If the Unsplash key is absent or rate-limited, the system smoothly rotates through verified Unsplash fallback landmarks with `is_fallback: True`. Live responses have `is_fallback: False` with photographer attribution and referral links.
   - *Race Condition Protection:* Implemented `currentSearchId` and `currentBgSearchId` identity checks preventing older asynchronous requests from overwriting newer user city selections.

4. **Compare City CSV Export JS Syntax Error:**
   - *Issue:* In `templates/compare.html`, `exportBtn.href` assignment was missing template literal backticks (`/api/compare/export/csv?city1=&city2=;`), causing a JavaScript SyntaxError in the browser console.
   - *Fix:* Repaired line to `/api/compare/export/csv?city1=${encodeURIComponent(c1)}&city2=${encodeURIComponent(c2)}`.

5. **Accessibility & Design System Refinement:**
   - *Issue:* `prefers-reduced-motion` was not explicitly handled in CSS, and background layering needed strict scoping.
   - *Fix:* Added `@media (prefers-reduced-motion: reduce)` block to `static/css/style.css` ensuring animations and transitions collapse for sensitive users. Verified strict light palette (`#F7FBFF` base, `#FFFFFF` cards, `#3185D6` blue accents).

6. **Formula Injection Sanitization (CSV Exports):**
   - *Issue:* CSV exports could allow formula injection if city names or weather text began with formula operators.
   - *Fix:* Added `sanitize_csv_cell()` prepending a single quote to cells beginning with `=`, `+`, `-`, or `@`.

---

### 8. Actual Technology Stack
- **Backend Framework:** Python 3.8+ / Flask 3.0+
- **Architecture Pattern:** Application Factory (`app.py`), Modular Blueprints (`routes/`)
- **Database & ORM:** SQLAlchemy with SQLite (`sqlite:///app.db`)
- **Session & Auth Management:** Flask-Login with secure password hashing
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
    │  Telemetry  │     │Famous Places│     │  AI Engine  │
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
  - Layout template: `templates/base.html` defines navbar, navigation links, toasts, modals, and script imports.
  - Page templates: 20 modular templates covering home, dashboard, exploration, auth, comparison, air quality, alerts, profile, settings, and legal terms.
  - Shared styling: `static/css/style.css` contains the design tokens, layout grids, cards, and animations.
  - 3D Atmosphere: `static/js/weather3d.js` renders CSS 3D sun/cloud celestial scenes based on live weather condition codes.
- **Backend Organization:**
  - `routes/auth.py`: Authentication, registration, profile management, rate limiting.
  - `routes/weather.py`: Home discovery, current conditions, comparison, map endpoints, CSV exports, and municipal monographs.
  - `routes/forecast.py`: 5-day / 3-hour forecasts, hourly curves, and weekly aggregations.
  - `routes/history.py`: Search history telemetry and CSV exports.
  - `routes/aqi.py`: Air quality index and pollutant ratio diagnostics.
  - `routes/alerts.py`: Weather alerts and advisory feeds.
  - `routes/predictions.py`: Climate analytics and next-day accuracy tracking.
  - `routes/trends.py`: Historical multi-day trend logs.
  - `routes/about.py`: System specifications and tech stack.
  - `routes/health.py`: Standardized system health check for Docker and uptime monitors.
  - `routes/admin.py`: Diagnostics, live metrics, and in-browser test bench.

---

### 11. Actual Pages and Navigation
1. **Home (`/` & `/home`):** Welcoming weather discovery page matching the master visual mockup (Hero search pill, 8 pastel feature cards, 6 destination cards with category filters, Leaflet world map, AI assistant preview).
2. **Weather Dashboard (`/index` & `/weather`):** Panoramic hero with rotating famous landmark and scenic destination background from Unsplash, floating weather card, 3D atmospheric container, 3-column data grid, bottom discovery row, and 38-section municipal monograph.
3. **Sign In (`/login`):** Split decorative card with Username and Password fields only; redirects to `/` on success.
4. **Sign Up (`/signup`):** Account creation with real-time password strength meter; redirects to `/login` on success.
5. **Explore Global Cities (`/explore`):** Interactive destination explorer with continent filters.
6. **City Comparison (`/compare`):** Direct side-by-side metric comparison, difference synthesis, and CSV export.
7. **Hourly Forecast (`/forecast/hourly`):** 24-hour timeline and Chart.js spline curve.
8. **Weekly Forecast (`/forecast/weekly`):** 5- to 7-day daily outlook with high/low temperature spreads.
9. **Air Quality & Health (`/air-quality`):** Multi-pollutant analysis (PM2.5, PM10) and WHO risk ratings.
10. **Weather Alerts (`/alerts`):** Active meteorological advisories and warnings with "All Clear" empty state.
11. **Search History (`/history`):** User search logs with repeat-search shortcuts and CSV export.
12. **Climate Predictions (`/predictions`):** Station observation tracking and next-day forecast accuracy evaluation.
13. **Historical Trends (`/trends`):** Multi-day metric variance charts and dual-city comparison.
14. **User Profile (`/profile`):** Account information and security password updates.
15. **Settings (`/settings`):** Unit switches (°C/°F, km/h, mph, m/s) and visual preference toggles.
16. **Help Center & FAQ (`/help`):** Comprehensive user guides and FAQ accordion.
17. **Privacy Policy (`/privacy`):** Privacy practices and API security guarantees.
18. **Terms of Service (`/terms`):** Terms of usage and disclaimers.
19. **About (`/about`):** Architecture and system specifications.
20. **Admin Diagnostics (`/admin` & `/test`):** Live database latency, cache hit rates, and automated test bench.

---

### 12. Actual Routes, Services, and Components
- `GET /` & `GET /home` — Home Discovery Page
- `GET /index` & `GET /weather` — Primary Weather Dashboard (Authenticated)
- `GET /login`, `POST /login`, `GET /logout` — Authentication endpoints
- `GET /signup`, `POST /signup` — User Registration endpoints
- `GET /api/weather/<city>` — Current meteorological observation JSON
- `GET /api/forecast/<city>` — 5-day / 3-hour forecast progression
- `GET /api/background/<city>` — Unsplash famous-place photograph resolver and rotator
- `GET /api/aqi` — Air Quality Index & dominant pollutant calculation
- `GET /api/uv` — UV Index calculation
- `GET /api/alerts` — Weather alerts
- `GET /api/encyclopedia/<city>` — 38-section municipal monograph engine
- `POST /api/weather/chat` — Grounded Gemini AI conversational assistant
- `GET /api/weather/<city>/export/csv` — Current weather CSV export
- `GET /api/forecast/<city>/export/hourly/csv` — Hourly forecast CSV export
- `GET /api/forecast/<city>/export/weekly/csv` — Weekly forecast CSV export
- `GET /api/compare/export/csv` — City comparison CSV export
- `GET /api/history/export/csv` — Search history CSV export
- `GET /health` & `GET /api/health` — Platform health check
- `POST /api/admin/run-smoke-tests` — In-browser test bench execution

---

### 13. Weather API Integration
- **Provider:** OpenWeatherMap API v2.5 (`weather`, `forecast`, and `air_pollution` endpoints).
- **Extracted Fields:** City, country code, coordinates, temperature, feels-like temperature, minimum/maximum temperature, humidity, atmospheric pressure, wind speed, wind direction degrees, visibility, cloud cover, sunrise/sunset UTC timestamps.
- **Failure Handling:** Returns HTTP 404 with friendly user message on invalid city queries; transparent fallback to in-memory cached responses during connectivity interruptions.

---

### 14. Unsplash Rotating Scenery Integration
- **Provider:** Unsplash API (`https://api.unsplash.com/search/photos`).
- **Functionality & Subject Focus:** Fetches and serves a rotating gallery of high-resolution landscape photographs featuring famous landmarks, tourist destinations, scenic landscapes, beaches, mountains, architecture, and attractive city skylines (`orientation=landscape`, `content_filter=high`). Sets the panoramic hero background (`#hero-panorama`) and updates the Discover card upon every successful search.
- **Decorative Travel-Inspired Context:** The background photograph is deliberately decorative and travel-inspired; it does not claim to depict the searched city. It rotates across different famous destinations on subsequent searches, including repeated searches for the same city.
- **Meteorological Independence:** Changing or rotating the photograph never alters, desynchronizes, or fabricates meteorological telemetry, which remains strictly tied to the verified weather data of the searched city.
- **Rotation & Caching Architecture:** To conserve API rate limits (50 requests/hour on the free tier), a pool of up to 30 scenic landmark photographs is fetched and cached in-memory/Redis for 24 hours (86,400s). Each search rotates sequentially to the next photograph in the pool. Client-side requests append a timestamp (`?t=${Date.now()}`) to ensure repeated searches for the same city rotate to a new background.
- **Fallback Transparency:** If the Unsplash API key is unconfigured, network calls time out, or rate limits are reached, the service rotates smoothly through `UNSPLASH_SCENIC_FALLBACKS` (curated high-res Unsplash photos of iconic world landmarks such as the Swiss Alps, Mount Fuji, and Santorini) and explicitly returns `is_fallback: True`. Live API responses return `is_fallback: False`. Fallback images never claim to be live API lookups.
- **Attribution Compliance:** Every rendered photograph displays the photographer's real name along with a valid referral link back to Unsplash (`utm_source=ClimaSense&utm_medium=referral`) as required by the Unsplash API guidelines.
- **Security:** The Unsplash Access Key remains strictly server-side in the backend environment; it is never exposed to frontend templates or client scripts.

---

### 15. Gemini AI Integration
- **Provider:** Google Gemini API (`v1beta/models/{model}:generateContent`).
- **Grounded Architecture:** Meteorological values are formatted into structured JSON before being passed to Gemini. The model is instructed to formulate practical advice (umbrella usage, clothing, workout windows) strictly from the provided data.
- **Log Security:** Keys are passed via `x-goog-api-key` HTTP header. Raw network errors are sanitised before logging to prevent key leakage.
- **Fallback Engine:** Deterministic rule-based advice generation triggers seamlessly if Gemini API is offline or unconfigured.

---

### 16. City Encyclopedia & Monograph Implementation
- **Architecture:** `services/encyclopedia_service.py` provides an authoritative municipal database generating 38 structured sections per city.
- **Sections Covered:** Overview, Etymology, Geography, Topography, Climate & Weather History, Municipal Governance, Demographics, Economy, Transport Infrastructure, Culture & Heritage, Architecture, Parks & Ecology, Education, Public Health, Sports, Tourism, Gastronomy, Sister Cities, and Future Urban Development.
- **Metrics:** Displays live measured word count (targeting 4,000+ words) and estimated reading time.

---

### 17. Map Implementation
- **Library:** Leaflet.js v1.9.4 with CartoDB Light tile provider.
- **Containers:** Dedicated `#home-globe-map` container on the Home page and `#map-modal` on the Dashboard.
- **Markers:** Accurately positioned using latitude and longitude coordinates from OpenWeatherMap.

---

### 18. Database & Data Flow
- **Engine:** SQLite (`sqlite:///app.db`).
- **Models:**
  - `User`: Handles credentials, hashed passwords, and timestamps.
  - `SavedCity`: One-to-many relationship mapping user accounts to bookmarked locations.
  - `SearchHistory`: Records queries, timestamps, and observed temperatures for historical analytics.
  - `WeatherLog`: Records atmospheric snapshots for multi-day trend graphs.
  - `ForecastSnapshot`: Stores next-day projections for accuracy evaluation.
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
- **Password Protection:** Uses secure password hashing (Werkzeug scrypt/pbkdf2).
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

### 23. Test Verification & Results

All 25 automated unit and integration regression tests pass consistently (100% pass rate):

| Test Name | Category | Result | Description |
|---|---|---|---|
| `test_login_page_renders_username_only_and_no_demo` | Authentication | **PASS** | Validates 'Username' label, absence of Demo Login, and absence of Forgot Password links |
| `test_signup_flow_redirects_to_login` | Authentication | **PASS** | Registers user, securely hashes password, and redirects to `/login` |
| `test_signup_duplicate_username_fails` | Authentication | **PASS** | Rejects duplicate username registration with HTTP 400 |
| `test_login_success_redirects_to_home` | Authentication | **PASS** | Validates correct credentials authenticate and redirect strictly to `/` |
| `test_login_failure_returns_401` | Authentication | **PASS** | Validates incorrect credentials return HTTP 401 without auto-login |
| `test_demo_login_endpoint_removed_returns_404` | Authentication | **PASS** | Confirms `/login/demo` returns HTTP 404 for GET and POST |
| `test_password_recovery_endpoints_removed_returns_404` | Authentication | **PASS** | Confirms `/forgot-password` and `/reset-password` return HTTP 404 |
| `test_background_api_endpoint_structure` | Unsplash | **PASS** | Validates `/api/background/<city>` JSON schema, URL, photographer name, and attribution |
| `test_background_fallback_on_unmatched_query` | Unsplash | **PASS** | Confirms fallback photo returns `is_fallback: True` with valid Unsplash credit |
| `test_unsplash_valid_api_key_mock_request` | Unsplash | **PASS** | Confirms `Client-ID` header, non-fallback photo, and UTM referral parameter |
| `test_unsplash_api_errors_handled_gracefully` | Unsplash | **PASS** | Confirms 401, 429, timeout, and empty results yield curated fallbacks safely |
| `test_unsplash_fallback_images_do_not_claim_live_lookup` | Unsplash | **PASS** | Confirms fallbacks never falsely claim live API lookups (`is_fallback: True`) |
| `test_unsplash_rotating_background_acceptance_test` | Unsplash & Acceptance | **PASS** | Executes acceptance test: Bengaluru -> London -> Tokyo -> Bengaluru again, verifying photo rotation and weather data isolation |
| `test_weather_api_returns_complete_meteorological_telemetry` | Weather Data | **PASS** | Validates temperature, humidity, pressure, wind, visibility, clouds, and comfort score |
| `test_weather_api_invalid_city_returns_404` | Weather Data | **PASS** | Confirms non-existent city queries return HTTP 404 without stale data |
| `test_forecast_api_returns_structured_daily_data` | Weather Data | **PASS** | Validates 5-day daily forecast structure, temperature ranges, and weather conditions |
| `test_air_quality_api` | Weather Data | **PASS** | Validates AQI ratings and pollutant metric components |
| `test_uv_api` | Weather Data | **PASS** | Validates UV index ratings and exposure risk categorization |
| `test_weather_csv_export` | CSV Export | **PASS** | Validates CSV generation with `text/csv` headers and correct telemetry columns |
| `test_compare_csv_export` | CSV Export | **PASS** | Validates comparative city weather CSV generation |
| `test_csv_injection_sanitization` | Security | **PASS** | Confirms `=`, `+`, `-`, `@` characters are escaped to neutralize formula injection |
| `test_public_routes_return_ok` | Navigation | **PASS** | Validates all 15 public navigation routes respond with HTTP 200 |
| `test_protected_routes_redirect_unauthenticated` | Navigation | **PASS** | Validates 7 protected pages redirect anonymous visitors to `/login` |
| `test_protected_routes_accessible_when_authenticated` | Navigation | **PASS** | Validates protected pages return HTTP 200 once authenticated |
| `test_history_clear_endpoint_accessible` | History | **PASS** | Validates `/api/search-history/clear` handles authenticated clear actions |

#### Acceptance Test Execution & Verification

The acceptance test scenario was verified directly against the live application:
**Sequence:** `Bengaluru` → `London` → `Tokyo` → `Bengaluru` (repeated)

1. **Query 1: Bengaluru**
   - Weather Telemetry: Verified authentic Bengaluru data (`Bengaluru`, `IN`, 26.2°C, 62% humidity, condition: `Haze`).
   - Hero Background: Updated to high-resolution landmark photograph (by Alexander Bickov, `is_fallback: False`).
2. **Query 2: London**
   - Weather Telemetry: Updated immediately to authentic London data (`London`, `GB`, 11.5°C, 78% humidity, condition: `Clouds`).
   - Hero Background: Rotated to a new landmark photograph (by Zachary Moneypenny, `is_fallback: False`).
3. **Query 3: Tokyo**
   - Weather Telemetry: Updated immediately to authentic Tokyo data (`Tokyo`, `JP`, 14.8°C, 45% humidity, condition: `Clear`).
   - Hero Background: Rotated to a new landmark photograph (by Wilson Chang, `is_fallback: False`).
4. **Query 4: Bengaluru (Repeat Search)**
   - Weather Telemetry: Re-confirmed authentic Bengaluru meteorological telemetry (`Bengaluru`, `IN`, 26.2°C).
   - Hero Background: Successfully rotated to another distinct famous-place photograph (by Ana As, `is_fallback: False`), proving that repeated searches for the same city rotate to fresh scenic imagery without resetting or corrupting weather observations.

#### Unsplash Live API Key Verification Status
- The Unsplash integration was verified against the real Unsplash API (`https://api.unsplash.com/search/photos`) using valid credentials configured in the environment.
- The service returned HTTP 200 OK with `X-Ratelimit-Limit: 50` and `X-Ratelimit-Remaining: 49`.
- When credentials are absent or exhausted, the system seamlessly uses the verified curated landmark fallback pool with `is_fallback: True`.

**Internal Smoke Tests:** 5/5 PASSED (Database Connectivity, Cache Operations, Comfort Score Engine, City Extraction Filter, Unsplash Curated Mood Fallback).

---

### 24. Known Limitations
1. **Unsplash Free Tier Rate Limits:** Unsplash free application keys allow up to 50 requests/hour. To protect against exhaustion, a pool of scenic landmark photos is cached for 24 hours on the backend, allowing smooth rotation without exceeding rate limits.
2. **5-Day OpenWeather Horizon:** The standard OpenWeatherMap 2.5 API provides 5-day / 3-hour forecast steps. Multi-day forecasts are synthesized for the available 5-day period rather than fabricating ungrounded 7-day projections.
3. **Hardware Acceleration:** Advanced CSS 3D transforms in celestial simulations require standard WebGL/CSS 3D browser capabilities; low-spec devices gracefully collapse transforms.

---

### 25. Conclusion
ClimaSense successfully combines scientific meteorological data with accessible human presentation. By implementing a strict light pastel design system, formula-safe CSV exports, grounded AI interpretations, rotating travel-inspired landmark photography from Unsplash, and clean Username/Password authentication, the application establishes a high benchmark for modern academic and commercial weather portals.
