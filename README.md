# 🌤️ ClimaSense — AI-Powered Weather Intelligence Platform

ClimaSense is a modern, production-grade weather intelligence platform built with **Python 3 (Flask)**. It integrates real-time meteorological observations (**OpenWeatherMap**), dynamic full-screen city photography (**Unsplash**), grounded generative artificial intelligence (**Google Gemini API**), condition-aware 3D weather visuals, an interactive Leaflet radar map, and an ultra-light frosted glass design system.

---

## 🌟 Overview & Key Capabilities

The interface adheres to an accessible **Ultra-Light Frosted Glass Design System** (`rgba(255, 255, 255, 0.72–0.78)` containers, `backdrop-filter: blur(14px)`, `#DCEAF7` light-blue borders, and soft slate typography `#334155` / `#475569`). Dark modes, dark cards, and heavy opaque overlays are eliminated to keep the scenic backgrounds bright, vivid, and visible through the dashboard cards.

### 🚀 Core Features

1. **Distinct Background Identities for Every Main Page**
   - **Home (`/home`, `/`):** Welcoming Golden Alpine Dawn Horizon.
   - **Weather (`/weather`):** Vibrant Azure Daytime Sky Panorama before search.
   - **Explore Cities (`/explore`):** Scenic Mediterranean Coastal Travel Horizon.
   - **Compare Cities (`/compare`):** High-Altitude Alpine Mountain Peak Panorama.
   - **Air Quality (`/air-quality`):** Pristine Sunlit Evergreen Forest Canopy.
   - **Climate / Predictions (`/predictions`, `/trends`):** Vast Dynamic Cloudscapes & Atmospheric Horizon.
   - **Sign In & Sign Up (`/login`, `/signup`):** Strict plain white background for distraction-free authentication.

2. **Dynamic City Backgrounds with Search Priority**
   - Searching for any city (e.g. **Delhi**, **Bengaluru**, **Mumbai**, **Mysuru**, **London**, **Tokyo**) fetches authentic high-resolution (`2400px`, `q=90`) Unsplash photographs.
   - **Priority Rule:** The searched city photograph immediately takes precedence over the default page background on Home and Weather pages.
   - **Persistent Viewport Layer:** Background remains fixed to the browser viewport (`position: fixed; inset: 0`), staying visible seamlessly across the entire page during scrolling.
   - **Race Condition Guard:** Request-ID tracking prevents slower previous searches from overwriting the latest search result.

3. **Condition-Aware 3D Weather Animations & Visual Accents**
   - **3D Weather Stage (`#weather-3d-stage`):** Live 3D sun with pulsing aura, floating cloud clusters, rain droplets, snow flurries, lightning flashes, wind streams, and mist bars.
   - **Separate Visual Layers:** Page background photograph (Layer A), 3D weather stage inside the hero section (Layer B), and metric emojis (Layer C) are strictly separated.
   - **Subtle Page-Specific 3D Accents:**
     - *Home:* Floating ambient sun aura (`.accent-home`).
     - *Explore:* 3D gyroscopic compass tilt (`.accent-explore`).
     - *Compare:* 3D dual-scale balance indicator (`.accent-compare`).
     - *Air Quality:* 3D environmental purity leaf (`.accent-aqi`).
     - *Climate:* 3D planetary orbit trend (`.accent-climate`).
   - Fully compliant with `prefers-reduced-motion: reduce`.

4. **Dedicated Full-Width Interactive Map Section**
   - Embedded directly in the main dashboard flow matching the exact width of the 5-Day Forecast section.
   - Powered by **Leaflet.js** with OpenStreetMap base layer and weather radar overlays (clouds, precipitation, temperature, wind).
   - Dynamically centers on the searched city's exact latitude and longitude with an interactive marker and coordinate badge.
   - Clicking **"View on map"** in Quick Info smoothly scrolls to the dedicated map and recalculates dimensions without modal popups.

5. **Authentication-Based Navigation & Route Protection**
   - **When Unauthenticated (`/login`, `/signup`):** The 6 main dashboard navigation links (**Home**, **Weather**, **Explore Cities**, **Compare**, **Air Quality**, **Climate**), the temperature-unit toggle, and authenticated user controls (**Search History**, **Settings**, **Profile**, **Sign Out**) are hidden. The header displays only the ClimaSense branding and Sign In / Sign Up toggle pills.
   - **Protected Routes:** Accessing `/`, `/home`, `/weather`, `/explore`, `/compare`, `/air-quality`, or `/predictions` while logged out immediately redirects to `/login`.
   - **After Login:** Users land on `/home` (`home.html`), where all introductory features, city search, global destinations, and AI teasers are available.
   - **After Logout:** Sessions are cleanly terminated via `logout_user()` and redirected to `/login`.

6. **Live Meteorological Telemetry & Extended Forecasts**
   - Live temperature, feels-like, humidity, atmospheric pressure, wind speed/direction, cloudiness, UV index, and visibility.
   - Grounded **Comfort Score (0–100)** computed from thermal neutrality bands, relative humidity, and air quality.
   - **Wider 5-Day Extended Forecast:** 5 desktop columns with consistent heights, daily highs/lows, condition icons, and CSV export.
   - **Hourly Forecast & 24-Hour Timeline:** Chart.js temperature curve with interactive tooltips and CSV export.
   - **Quick Info Card:** City classification, coordinates, country code, and time zone.
   - **City Discovery Card:** Municipal highlights, geographical topography, and urban background insights.

7. **Google Gemini AI Weather Briefing & Assistant**
   - Real-time weather briefing card generated using Google Gemini (`gemini-2.0-flash`).
   - Provides plain-language advice: clothing suggestions, umbrella recommendations, outdoor exercise suitability, and health guidance.
   - **Grounded Smart Rules Engine:** Automatic fallback ensuring continuous briefing availability if Gemini is unconfigured or rate-limited.
   - Interactive docked chat assistant (`#chat-panel`) with quick suggestion chips.

8. **Security & Data Integrity**
   - Sensitive credentials (`OPENWEATHER_API_KEY`, `UNSPLASH_API_KEY`, `AI_API_KEY`, `SECRET_KEY`) are processed server-side only. Zero client-side exposure.
   - Formula-injection sanitized CSV exports escaping `=`, `+`, `-`, and `@`.
   - Visible photographer credit sentence removed from visible dashboard UI while maintaining compliant backend referral integration.
   - Per-IP and per-username rate limiting against brute-force attempts.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│  Ultra-Light Frosted Glass UI • Fixed HD Background   │
│  3D Weather Stage • Leaflet Radar Map • Chart.js       │
│  Gemini AI Chat Assistant • Sockets • Responsive Grid  │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP / WebSockets
┌───────────────────────────▼────────────────────────────┐
│                  Flask Application                     │
│  Application Factory • Blueprints • Auth & Rate Limits │
│  Services: OpenWeather • Unsplash • Gemini • Wiki      │
└───────┬──────────────┬──────────────┬───────────┬──────┘
        │              │              │           │
 ┌──────▼──────┐┌──────▼──────┐┌──────▼──────┐┌───▼──────────┐
 │ OpenWeather ││   Unsplash  ││Google Gemini││    SQLite    │
 │ Meteorological││ City Scenery││ Generative ││  + In-Memory │
 │   Network   ││     API     ││ Intelligence││    Cache     │
 └─────────────┘└─────────────┘└─────────────┘└──────────────┘
```

---

## ⚙️ Configuration Reference

Create an environment configuration file named `.env` in the project root:

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
AI_BRIEFING_CACHE_TTL=1800
AI_CHAT_RATE_LIMIT=10
AI_MAX_OUTPUT_TOKENS=800
AI_REQUEST_TIMEOUT=10

# Cache Configuration (Falls back to in-memory cache if Redis is absent)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

> **Security Note:** `.env` and `api.env` are ignored by Git. API keys are never exposed in HTML templates, JavaScript files, or client-side responses.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- **Python 3.8+** (tested on 3.8, 3.9, 3.10)
- `pip` package manager

### 2. Clone and Setup Environment
```bash
# Navigate to project directory
cd ClimaSense

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials
```bash
# Copy sample configuration
cp .env.example .env
```
*(On Windows PowerShell, use `Copy-Item .env.example .env`)*

Edit `.env` to provide your API keys from:
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Unsplash Developer Portal](https://unsplash.com/developers)
- [Google AI Studio (Gemini)](https://aistudio.google.com/)

### 4. Initialize Database
Database tables initialize automatically on first startup. To verify or initialize schema manually:
```bash
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database tables verified.')"
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```
*(Unauthenticated visitors are automatically directed to `/login`)*

---

## 🧪 Testing & Quality Assurance

ClimaSense includes a comprehensive automated test suite (58 tests) covering route protection, authentication state, background priority, 3D visual elements, dedicated map placement, and API integrations:

```bash
python -m pytest -q -W default
```

**Expected output:**
```text
..........................................................               [100%]
58 passed in 31.28s
```

---

## 📦 Clean Distribution Packaging

To generate a sanitized production archive (`ClimaSense_clean.zip`) excluding credentials (`.env`, `api.env`), runtime databases (`*.db`), git history (`.git/`), cache directories (`__pycache__`, `.pytest_cache`), and temporary scratch files:

```bash
python package_dist.py
```

---

## 📡 Complete Page & Route Reference

### Web Pages
| Route | Method | Access | Description |
|---|---|---|---|
| `/` or `/home` | `GET` | Authenticated | Welcoming Home & Discovery Page |
| `/login` | `GET`, `POST` | Public | Minimal Sign In Page |
| `/signup` | `GET`, `POST` | Public | User Registration Page |
| `/weather` or `/index` | `GET` | Authenticated | Main Weather Dashboard with 3D visuals & Map |
| `/explore` | `GET` | Authenticated | Global Destinations Travel Discovery |
| `/compare` | `GET` | Authenticated | Side-by-Side City Comparison Page |
| `/air-quality` | `GET` | Authenticated | Environmental Health & UV Index Page |
| `/predictions` | `GET` | Authenticated | Climate Analytics & Historical Accuracy |
| `/trends` | `GET` | Authenticated | Meteorological Trends & Historical Data |
| `/history` | `GET` | Authenticated | User Search Telemetry History |
| `/profile` | `GET`, `POST` | Authenticated | User Account & Password Management |
| `/settings` | `GET` | Authenticated | Display Units & User Preferences |
| `/about` | `GET` | Public | System Architecture & Documentation |
| `/help` | `GET` | Public | Help Center & FAQ |
| `/privacy` | `GET` | Public | Privacy Policy |
| `/terms` | `GET` | Public | Terms of Service |
| `/logout` | `GET` | Authenticated | Session Sign Out |

### APIs & Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | Operational health check (Database, APIs, Cache) |
| `/api/weather/<city>` | `GET` | Current weather, comfort score, rain probability |
| `/api/forecast/<city>` | `GET` | 5-Day and 24-Hour hourly forecast breakdown |
| `/api/background/<city>` | `GET` | Authentic city photography with Unsplash resolution |
| `/api/aqi?lat=<lat>&lon=<lon>` | `GET` | Air Quality Index and pollutant concentrations |
| `/api/uv?lat=<lat>&lon=<lon>` | `GET` | Real-time Ultraviolet radiation risk level |
| `/api/alerts?lat=<lat>&lon=<lon>` | `GET` | Severe meteorological alerts |
| `/api/weather/<city>/briefing` | `GET` | Grounded Gemini AI Weather Briefing |
| `/api/weather/chat` | `POST` | Conversational Weather Assistant |
| `/api/forecast/<city>/export/hourly/csv` | `GET` | 24-Hour Hourly Timeline CSV export |
| `/api/forecast/<city>/export/weekly/csv` | `GET` | 5-Day Extended Forecast CSV export |
| `/api/compare/export/csv` | `GET` | Direct City Comparison CSV export |
| `/api/history/export/csv` | `GET` | User Search History CSV export |

---

## 📄 License & Attribution

- **Weather Data:** Powered by [OpenWeatherMap](https://openweathermap.org/).
- **Scenic Photography:** Provided by [Unsplash](https://unsplash.com/).
- **Generative Intelligence:** Powered by [Google Gemini](https://ai.google.dev/).
- **Mapping:** [Leaflet](https://leafletjs.com/) and [OpenStreetMap](https://www.openstreetmap.org/).
- **Icons:** [Font Awesome](https://fontawesome.com/).
