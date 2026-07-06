# ClimaSense - AI-Powered Weather Dashboard

ClimaSense is a modern, responsive, and real-time weather dashboard built with Flask. It uses a stunning 3D glassmorphism UI, real-time WebSocket alerts, and Celery for background tasks, along with gorgeous dynamic background images fetched from Unsplash to match the city you're searching for.

## Features
- **Real-time Weather Data**: Integrated with OpenWeatherMap API for live current weather, 5-day forecast, and Air Quality Index (AQI).
- **Dynamic Backgrounds**: Integrates with the Unsplash API to fetch beautiful, high-quality images of the searched city in real-time.
- **Glassmorphism UI & 3D CSS Engine**: A highly polished, modern front-end built without heavy frameworks. 
- **Real-Time Alerts**: Uses Flask-SocketIO to push severe weather alerts to connected clients instantly.
- **Background Jobs**: Powered by Celery and Redis to handle email digests, caching, and polling weather alerts.
- **Progressive Web App (PWA)**: Includes a service worker and manifest for offline shell support and mobile installation.
- **User Authentication**: Secure signup and login powered by Flask-Login and bcrypt.

## Tech Stack
- **Backend**: Python 3.8+, Flask, Flask-SQLAlchemy (SQLite), Flask-SocketIO, Eventlet
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript, Leaflet.js, Chart.js
- **Task Queue**: Celery, Redis
- **APIs**: OpenWeatherMap, Unsplash

## Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/climasense.git
cd climasense
```

### 2. Set up a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to a new file named `api.env` (or `.env`).
```bash
cp .env.example api.env
```
Open `api.env` and fill in your keys:
- `OPENWEATHER_API_KEY`: Get this from [OpenWeatherMap](https://openweathermap.org/)
- `UNSPLASH_API_KEY`: Get this from [Unsplash Developer](https://unsplash.com/developers)
- `SECRET_KEY`: Set a secure random string

### 5. Run the Application
Start the Flask application using eventlet (which supports WebSockets):
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`

### 6. (Optional) Run Celery Background Tasks
If you have Redis installed and want to run background caching and alerts:
1. Ensure Redis is running on `localhost:6379`
2. Start the Celery worker:
```bash
celery -A tasks.celery_tasks.celery worker --loglevel=info
```
3. Start the Celery beat scheduler:
```bash
celery -A tasks.celery_tasks.celery beat --loglevel=info
```

## Security Note
This project uses a `.gitignore` file that prevents `api.env` and `.env` from being committed to the repository. **Never** commit your API keys or database files (`instance/*.db`) to version control.

## License
MIT License
