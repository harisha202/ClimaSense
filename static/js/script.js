document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('Service Worker registered', reg))
            .catch(err => console.error('Service Worker registration failed', err));
    }

    const searchBtn = document.getElementById('search-btn');
    const cityInput = document.getElementById('city-input');
    
    // Check if city was passed in URL (from history)
    const urlParams = new URLSearchParams(window.location.search);
    const initialCity = urlParams.get('city');
    
    if (initialCity) {
        cityInput.value = initialCity;
        fetchWeather(initialCity);
    }
    
    if(searchBtn) {
        searchBtn.addEventListener('click', () => {
            const city = cityInput.value.trim();
            if (city) {
                fetchWeather(city);
            }
        });
    }

    if(cityInput) {
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const city = cityInput.value.trim();
                if (city) fetchWeather(city);
            }
        });
    }

    window.addEventListener('unitChanged', () => {
        // re-render if we have data
        if(window.currentWeatherData) {
            window.renderWeather(window.currentWeatherData);
        }
        if(window.currentForecastData) {
            window.renderForecast(window.currentForecastData);
        }
    });


});

async function fetchWeather(city) {
    const spinner = document.getElementById('loading-spinner');
    const wrapper = document.getElementById('dashboard-wrapper');
    const card = document.getElementById('weather-card');
    const forecast = document.getElementById('forecast-container');
    const map = document.getElementById('map');
    const aqi = document.getElementById('aqi-badge');
    const banner = document.getElementById('alert-banner');
    
    if(spinner) spinner.classList.remove('hidden');
    if(wrapper) wrapper.classList.add('hidden');
    if(card) card.classList.add('hidden');
    if(forecast) forecast.classList.add('hidden');
    if(map) map.classList.add('hidden');
    if(aqi) aqi.classList.add('hidden');
    if(banner) banner.classList.add('hidden');
    
    try {
        const res = await fetch(`/api/weather/${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('lastCity', data.data.name);
            window.currentWeatherData = data.data; // save for unit toggle
            window.renderWeather(data.data);
            
            // Trigger parallel fetches
            const lat = data.data.coord.lat;
            const lon = data.data.coord.lon;
            const desc = data.data.weather[0].description;
            
            window.fetchForecast(data.data.name);
            window.fetchAQI(lat, lon);
            window.fetchAlerts(lat, lon);
            window.fetchBackground(data.data.name, desc);
            
            if(window.joinCityRoom) {
                window.joinCityRoom(data.data.name);
            }
            
            if(window.initMap) {
                window.initMap(lat, lon, data.data.name);
            }
        } else {
            alert(data.message || 'City not found');
            if(spinner) spinner.classList.add('hidden');
        }
    } catch(e) {
        console.error(e);
        if(spinner) spinner.classList.add('hidden');
    }
}

window.renderWeather = (data) => {
    document.getElementById('loading-spinner').classList.add('hidden');
    const wrapper = document.getElementById('dashboard-wrapper');
    if (wrapper) wrapper.classList.remove('hidden');
    const card = document.getElementById('weather-card');
    card.classList.remove('hidden');
    
    document.getElementById('city-name').textContent = `${data.name}, ${data.sys.country}`;
    
    // Calculate and display local time of the searched city
    const utcTime = new Date().getTime() + (new Date().getTimezoneOffset() * 60000);
    const cityTime = new Date(utcTime + (data.timezone * 1000));
    const dtOpts = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
    const localTimeStr = cityTime.toLocaleTimeString('en-US', dtOpts);
    
    const timeEl = document.getElementById('city-local-time');
    if (timeEl) {
        timeEl.innerHTML = `<i class="fa-regular fa-clock" style="margin-right: 5px;"></i> ${localTimeStr} (Local Time)`;
    }
    
    document.getElementById('temperature').textContent = window.getTempString(data.main.temp);
    document.getElementById('weather-desc').textContent = data.weather[0].description;
    document.getElementById('feels-like').textContent = window.getTempString(data.main.feels_like);
    document.getElementById('humidity').textContent = data.main.humidity + '%';
    document.getElementById('wind-speed').textContent = data.wind.speed + ' m/s';
    document.getElementById('pressure').textContent = data.main.pressure + ' hPa';
    document.getElementById('weather-icon').src = `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`;
    
    // update suggestions
    renderSuggestions(data);
    
    // reset save button
    const saveBtn = document.getElementById('save-city-btn');
    if (saveBtn) {
        saveBtn.innerHTML = '<i class="fa-regular fa-star"></i>';
        saveBtn.onclick = async () => {
            try {
                const res = await fetch('/api/cities/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({city: data.name})
                });
                const result = await res.json();
                if (result.success) {
                    saveBtn.innerHTML = '<i class="fa-solid fa-star" style="color: var(--accent);"></i>';
                } else {
                    alert(result.message);
                }
            } catch(e) { console.error(e); }
        };
    }
};

window.fetchForecast = async (city) => {
    try {
        const res = await fetch(`/api/forecast/${encodeURIComponent(city)}`);
        const data = await res.json();
        if(data.success) {
            window.currentForecastData = data.forecast;
            window.renderForecast(data.forecast);
        }
    } catch(e) { console.error(e); }
};

window.renderForecast = (forecast) => {
    const container = document.getElementById('forecast-container');
    container.innerHTML = '';
    container.classList.remove('hidden');
    
    forecast.forEach(day => {
        const date = new Date(day.date).toLocaleDateString('en-GB', {weekday: 'short', day: 'numeric'});
        const card = document.createElement('div');
        card.className = 'forecast-card glass';
        card.innerHTML = `
            <div class="forecast-day">${date}</div>
            <img src="https://openweathermap.org/img/wn/${day.icon}.png" alt="icon">
            <div class="forecast-temp">${window.getTempString(day.temp)}</div>
        `;
        container.appendChild(card);
    });
};

window.fetchAQI = async (lat, lon) => {
    try {
        const res = await fetch(`/api/aqi?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if(data.success) {
            const aqi = document.getElementById('aqi-badge');
            aqi.textContent = `AQI: ${data.label}`;
            aqi.className = 'aqi-badge'; // reset
            aqi.classList.add('aqi-' + data.label.toLowerCase().replace(' ', '-'));
            aqi.classList.remove('hidden');
            
            // Calculate Comfort Index
            if (window.currentWeatherData) {
                const temp = window.currentWeatherData.main.temp;
                const humidity = window.currentWeatherData.main.humidity;
                const aqiVal = data.aqi || 3; // 1-5 scale
                
                // Ideal temp: 22C. Penalty for deviation.
                const tempScore = Math.max(0, 100 - (Math.abs(temp - 22) * 3));
                // Ideal humidity: 45%. Penalty for deviation.
                const humScore = Math.max(0, 100 - (Math.abs(humidity - 45) * 1.5));
                // AQI Penalty (1 is good, 5 is bad)
                const aqiScore = Math.max(0, 100 - ((aqiVal - 1) * 20));
                
                const comfort = Math.round((tempScore * 0.5) + (humScore * 0.3) + (aqiScore * 0.2));
                
                const comfortBadge = document.getElementById('comfort-badge');
                if (comfortBadge) {
                    comfortBadge.textContent = `Comfort: ${comfort}/100`;
                    comfortBadge.className = 'aqi-badge';
                    if (comfort >= 80) comfortBadge.classList.add('aqi-good');
                    else if (comfort >= 60) comfortBadge.classList.add('aqi-moderate');
                    else if (comfort >= 40) comfortBadge.classList.add('aqi-unhealthy-sensitive');
                    else comfortBadge.classList.add('aqi-unhealthy');
                    comfortBadge.classList.remove('hidden');
                }
            }
        }
    } catch(e) { console.error(e); }
};

window.fetchAlerts = async (lat, lon) => {
    try {
        const res = await fetch(`/api/alerts?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if(data.success && data.alert) {
            const banner = document.getElementById('alert-banner');
            banner.textContent = `⚠️ ${data.alert.title}: ${data.alert.description}`;
            banner.className = 'alert-banner severe';
            banner.classList.remove('hidden');
        }
    } catch(e) { console.error(e); }
};


window.fetchBackground = async (city, desc) => {
    try {
        const res = await fetch(`/api/background/${encodeURIComponent(city)}/${encodeURIComponent(desc)}`);
        const data = await res.json();
        if(data.success) {
            document.getElementById('bg-image').style.backgroundImage = `url('${data.url}')`;
        }
    } catch(e) { console.error(e); }
};

function renderSuggestions(data) {
    const row = document.getElementById('suggestions-row');
    row.innerHTML = '';
    row.classList.remove('hidden');
    
    const desc = data.weather[0].description.toLowerCase();
    const temp = data.main.temp;
    
    let tip = '';
    if(desc.includes('rain') || desc.includes('drizzle')) tip = '☂️ Carry an umbrella';
    else if(temp > 30) tip = '🥤 Stay hydrated, it is hot!';
    else if(temp < 5) tip = '🧥 Wear a heavy coat';
    else if(desc.includes('clear')) tip = '😎 Great day for an outdoor run';
    else tip = '⛅ Moderate weather expected';
    
    const pill = document.createElement('div');
    pill.style.cssText = 'padding: 0.5rem 1rem; border-radius: 20px; background: var(--accent); color: white; font-weight: bold; font-size: 0.9rem;';
    pill.textContent = tip;
    row.appendChild(pill);
}