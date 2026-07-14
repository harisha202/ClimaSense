🌤️ ClimaSense - AI-Powered Weather Dashboard
A modern, production-ready weather application built with Flask that provides real-time weather data, 5-day forecasts, severe weather alerts, and gorgeous dynamic backgrounds based on the city you search for.

🌍 Real-World Application & Use Case
What it does: ClimaSense is a comprehensive weather dashboard that doesn't just display static numbers. It fetches live, real-time data from global weather networks (OpenWeatherMap) and combines it with dynamic, high-resolution photography (Unsplash) to give users an immersive view of a city's current conditions. It calculates comfort indices, tracks air quality, and pushes severe weather alerts directly to the user's screen in real-time.

Why this architecture is used in the real world: While a simple weather app can be built with basic HTML and a single API call, ClimaSense is engineered using the same architecture found in enterprise-level production systems:

Asynchronous Task Queues (Celery + Redis): Real-world applications cannot afford to freeze or crash when an external API is slow. By offloading caching and background polling to Celery, the main application remains lightning fast for the end-user.
Real-Time WebSockets (Socket.IO): Instead of forcing the user's browser to constantly refresh the page to check for new alerts (which drains battery and destroys server bandwidth), ClimaSense maintains a persistent connection to push emergency alerts instantly—a critical requirement for modern live dashboards.
Intelligent Caching: Hitting third-party APIs for every user request quickly leads to rate-limiting and massive server bills. ClimaSense uses multi-layered caching to serve thousands of users efficiently while making only a fraction of the API calls.

✨ Features
Core Functionality
Real-Time Weather Data: Fetches live, up-to-the-minute current weather conditions and detailed 5-day forecasts for any global city.
Dynamic City Backgrounds: Seamlessly integrates with the Unsplash API to fetch and display high-resolution, contextual photography of the searched city.
Air Quality & Comfort Index: Actively tracks real-time AQI and computes a custom "Comfort Score" based on temperature, humidity, and pollution levels.
Live Severe Alerts: Broadcasts severe weather warnings to active users instantly via persistent WebSocket connections.
Progressive Web App (PWA): Fully installable on mobile and desktop platforms, featuring offline shell caching via Service Workers for a native app experience.
Technical & UI Excellence
Distributed Background Jobs: Leverages Celery and Redis to handle caching and background polling asynchronously, drastically improving UI rendering speeds.
Glassmorphism UI & 3D Engine: Features a stunning, highly polished frontend built entirely with vanilla CSS (no heavy frameworks), utilizing frosted glass containers and a hardware-accelerated 3D animated scene engine.
Advanced API Caching: Implements multi-layered caching strategies to heavily reduce external API calls, ensuring high availability and bypassing rate limits.

 Security Features
Password Hashing: User credentials are cryptographically secured and never stored in plaintext (powered by Flask-Bcrypt).
Session-Based Authentication: Critical application routes and features are heavily protected using strict @login_required decorators.
API Key Protection: Sensitive API keys are isolated via environment variables and strictly ignored by version control to prevent leaks.
WebSocket Security: Socket connections validate the active user's session before allowing access to private weather alert broadcast rooms.

🙏 Acknowledgments
Weather data and forecasting provided by OpenWeatherMap.
Dynamic contextual photography provided by Unsplash.
Engineered using Flask, Celery, Redis, and Socket.IO.
