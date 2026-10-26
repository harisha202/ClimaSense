# 🌤️ ClimaSense — AI-Powered Weather Intelligence Platform

ClimaSense is a modern, production-grade weather intelligence platform built with **Python 3 (Flask)**. It seamlessly combines real-time meteorological observations, dynamic full-screen city photography, grounded generative artificial intelligence, condition-aware 3D weather visuals, an interactive radar map, and an ultra-light frosted glass design system.

---

## 🌟 Overview & Key Capabilities

The interface adheres to an accessible **Ultra-Light Frosted Glass Design System** with translucent surfaces, delicate borders, and soft slate typography. Dark themes, dark panels, and heavy opaque overlays are eliminated to keep the scenic backgrounds bright, vivid, and visible through the dashboard cards.

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
   - Searching for any city (e.g. **Delhi**, **Bengaluru**, **Mumbai**, **Mysuru**, **London**, **Tokyo**) automatically displays authentic high-resolution city photography.
   - **Priority Rule:** The searched city photograph immediately takes precedence over the default page background on Home and Weather pages.
   - **Persistent Viewport Layer:** The background photograph remains fixed to the browser viewport, staying visible across the entire page during scrolling.
   - **Race Condition Guard:** Request tracking prevents slower previous searches from overwriting the latest search result.

3. **Condition-Aware 3D Weather Animations & Visual Accents**
   - **3D Weather Stage:** Live condition-driven dimensional sun with pulsing aura, floating cloud clusters, rain droplets, snow flurries, lightning flashes, wind streams, and mist bars.
   - **Separate Visual Layers:** Page background photograph (Layer A), 3D weather stage inside the hero section (Layer B), and metric emojis (Layer C) are strictly separated.
   - **Subtle Page-Specific 3D Accents:**
     - *Home:* Floating ambient sun aura.
     - *Explore:* 3D gyroscopic compass tilt.
     - *Compare:* 3D dual-scale balance indicator.
     - *Air Quality:* 3D environmental purity leaf.
     - *Climate:* 3D planetary orbit trend.
   - Fully compliant with `prefers-reduced-motion` accessibility standards.

4. **Dedicated Full-Width Interactive Map Section**
   - Embedded directly in the main dashboard flow matching the exact width of the 5-Day Forecast section.
   - Dynamic map centered on the searched city's exact coordinates with interactive marker and coordinate badge.
   - Includes real-time meteorological overlays: clouds, precipitation, temperature, and wind.
   - Clicking **"View on map"** in Quick Info smoothly scrolls to the dedicated map and recalculates dimensions without modal popups.

5. **Authentication-Based Navigation & Route Protection**
   - **When Unauthenticated (`/login`, `/signup`):** The 6 main dashboard navigation links (**Home**, **Weather**, **Explore Cities**, **Compare**, **Air Quality**, **Climate**), the temperature-unit toggle, and user controls (**Search History**, **Settings**, **Profile**, **Sign Out**) are hidden. The header displays only the ClimaSense branding and Sign In / Sign Up toggle options.
   - **Protected Routes:** Accessing `/`, `/home`, `/weather`, `/explore`, `/compare`, `/air-quality`, or `/predictions` while logged out immediately redirects to `/login`.
   - **After Login:** Users land on `/home` (`home.html`), where all introductory features, city search, global destinations, and AI teasers are available.
   - **After Logout:** Sessions are cleanly terminated and returned to `/login`.

6. **Live Meteorological Telemetry & Extended Forecasts**
   - Live temperature, feels-like, humidity, atmospheric pressure, wind speed/direction, cloudiness, UV index, and visibility.
   - Grounded **Comfort Score (0–100)** computed from thermal neutrality bands, relative humidity, and air quality.
   - **Wider 5-Day Extended Forecast:** 5 desktop columns with consistent heights, daily highs/lows, condition icons, and CSV export.
   - **Hourly Forecast & 24-Hour Timeline:** Temperature curve with interactive tooltips and CSV export.
   - **Quick Info Card:** City classification, coordinates, country code, and time zone.
   - **City Discovery Card:** Municipal highlights, geographical topography, and urban background insights.

7. **Generative AI Weather Briefing & Assistant**
   - Real-time weather briefing card generated using generative artificial intelligence.
   - Provides plain-language advice: clothing suggestions, umbrella recommendations, outdoor exercise suitability, and health guidance.
   - **Grounded Smart Rules Engine:** Automatic fallback ensuring continuous briefing availability.
   - Interactive docked chat assistant with quick suggestion chips.

8. **Security & Data Integrity**
   - Credential security enforced server-side. Zero sensitive parameters exposed to frontend code or browser logs.
   - Formula-injection sanitized CSV exports escaping sensitive spreadsheet prefixes.
   - Clean UI without obstructive visible attribution overlays on the dashboard.
   - Per-IP and per-username rate limiting against brute-force attempts.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- **Python 3.8+** (tested on 3.8, 3.9, 3.10)
- `pip` package manager

### 2. Install Dependencies
```bash
# Navigate to project directory
cd ClimaSense

# Install required packages
pip install -r requirements.txt
```

### 3. Initialize Database
Database tables initialize automatically on first startup. To verify or initialize schema manually:
```bash
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database tables verified.')"
```

### 4. Run the Application
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

ClimaSense includes a comprehensive automated test suite (58 tests) covering route protection, authentication state, background priority, 3D visual elements, dedicated map placement, and meteorological integrations:

```bash
python -m pytest -q -W default
```

---

## 📦 Clean Distribution Packaging

To generate a sanitized production archive (`ClimaSense_clean.zip`) excluding private credentials, runtime databases, repository history, cache directories, and temporary files:

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
| `/api/background/<city>` | `GET` | Authentic city photography retrieval |
| `/api/aqi?lat=<lat>&lon=<lon>` | `GET` | Air Quality Index and pollutant concentrations |
| `/api/uv?lat=<lat>&lon=<lon>` | `GET` | Real-time Ultraviolet radiation risk level |
| `/api/alerts?lat=<lat>&lon=<lon>` | `GET` | Severe meteorological alerts |
| `/api/weather/<city>/briefing` | `GET` | Grounded AI Weather Briefing |
| `/api/weather/chat` | `POST` | Conversational Weather Assistant |
| `/api/forecast/<city>/export/hourly/csv` | `GET` | 24-Hour Hourly Timeline CSV export |
| `/api/forecast/<city>/export/weekly/csv` | `GET` | 5-Day Extended Forecast CSV export |
| `/api/compare/export/csv` | `GET` | Direct City Comparison CSV export |
| `/api/history/export/csv` | `GET` | User Search History CSV export |
