document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('Service Worker registered', reg))
            .catch(err => console.error('Service Worker registration failed', err));
    }

    // Load saved cities & recent searches
    window.fetchSavedCities();
    window.fetchRecentSearches();

    const searchBtn = document.getElementById('search-btn');
    const cityInput = document.getElementById('city-input');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeBtn = document.querySelector('.close-btn');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    
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
            if (city) fetchWeather(city);
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
    
    // Autocomplete simulation
    cityInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        const suggestionsRow = document.getElementById('suggestions-row');
        const popularCities = ['Bengaluru', 'London', 'Tokyo', 'Paris', 'New York', 'Dubai', 'Sydney'];
        
        if (val.length > 1) {
            const matches = popularCities.filter(c => c.toLowerCase().startsWith(val));
            if (matches.length > 0) {
                suggestionsRow.innerHTML = '';
                matches.forEach(m => {
                    const pill = document.createElement('div');
                    pill.style.cssText = 'padding: 0.5rem 1rem; border-radius: 20px; background: var(--accent); color: #000; font-weight: bold; font-size: 0.9rem; cursor: pointer;';
                    pill.textContent = m;
                    pill.onclick = () => {
                        cityInput.value = m;
                        suggestionsRow.classList.add('hidden');
                        fetchWeather(m);
                    };
                    suggestionsRow.appendChild(pill);
                });
                suggestionsRow.classList.remove('hidden');
            } else {
                suggestionsRow.classList.add('hidden');
            }
        } else {
            suggestionsRow.classList.add('hidden');
        }
    });

    if(exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            if(window.currentWeatherData) {
                window.location.href = `/api/weather/${encodeURIComponent(window.currentWeatherData.name)}/export/csv`;
            } else {
                window.showToast("Please search for a city first.");
            }
        });
    }
    
    if(settingsBtn) {
        settingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
    }
    if(closeBtn) {
        closeBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    }
    if(saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            const tempUnit = document.getElementById('setting-temp-unit').value;
            const windUnit = document.getElementById('setting-wind-unit').value;
            localStorage.setItem('tempUnit', tempUnit);
            localStorage.setItem('windUnit', windUnit);
            settingsModal.classList.add('hidden');
            window.showToast("Settings saved.");
            
            // Re-render
            if(window.currentWeatherData) window.renderWeather(window.currentWeatherData);
            if(window.currentForecastData) window.renderForecast(window.currentForecastData);
            if(window.currentHourlyData) window.renderTimeline(window.currentHourlyData);
        });
    }
});

async function fetchWeather(city) {
    const spinner = document.getElementById('loading-spinner');
    const wrapper = document.getElementById('dashboard-wrapper');
    const banner = document.getElementById('alert-banner');
    
    if(spinner) spinner.classList.remove('hidden');
    if(wrapper) wrapper.classList.add('hidden');
    if(banner) banner.classList.add('hidden');
    
    try {
        const res = await fetch(`/api/weather/${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('lastCity', data.data.name);
            window.currentWeatherData = data.data; // save for unit toggle
            window.renderWeather(data.data);
            
            if(data.ai_summary) {
                document.getElementById('ai-summary-text').textContent = data.ai_summary;
            }
            
            // Trigger parallel fetches
            const lat = data.data.coord.lat;
            const lon = data.data.coord.lon;
            const desc = data.data.weather[0].description;
            
            window.fetchForecast(data.data.name);
            window.fetchAQI(lat, lon);
            window.fetchAlerts(lat, lon);
            window.fetchBackground(data.data.name, desc);
            window.updateTheme(desc);
            window.fetchRecentSearches(); // refresh recent
            
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

window.getTempString = (tempC) => {
    const unit = localStorage.getItem('tempUnit') || 'C';
    if(unit === 'F') return Math.round((tempC * 9/5) + 32) + '°F';
    return Math.round(tempC) + '°C';
};
window.getWindString = (speedMS) => {
    const unit = localStorage.getItem('windUnit') || 'kmh';
    if(unit === 'mph') return Math.round(speedMS * 2.23694) + ' mph';
    if(unit === 'ms') return Math.round(speedMS) + ' m/s';
    return Math.round(speedMS * 3.6) + ' km/h'; // default kmh
};

window.getWeatherEmoji = (desc) => {
    if(desc.includes('thunderstorm') || desc.includes('storm')) return '⛈️';
    if(desc.includes('snow')) return '❄️';
    if(desc.includes('rain') || desc.includes('drizzle')) return '🌧️';
    if(desc.includes('fog') || desc.includes('mist')) return '🌫️';
    if(desc.includes('cloud')) return '☁️';
    if(desc.includes('clear')) return '☀️';
    return '☀️'; // default
};

window.renderWeather = (data) => {
    document.getElementById('loading-spinner').classList.add('hidden');
    const wrapper = document.getElementById('dashboard-wrapper');
    if (wrapper) wrapper.classList.remove('hidden');
    
    document.getElementById('city-name').textContent = `📍 ${data.name}`;
    
    const descStr = data.weather[0].description;
    const tempStr = window.getTempString(data.main.temp);
    const emoji = window.getWeatherEmoji(descStr);
    
    // Capitalize description
    const capDesc = descStr.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    
    document.getElementById('city-subtitle').textContent = `${emoji} ${capDesc} • ${tempStr}`;
    
    // Calculate and display local time
    const utcTime = new Date().getTime() + (new Date().getTimezoneOffset() * 60000);
    const cityTime = new Date(utcTime + (data.timezone * 1000));
    const dtOpts = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
    const localTimeStr = cityTime.toLocaleTimeString('en-US', dtOpts);
    
    document.getElementById('city-local-time').innerHTML = `<i class="fa-regular fa-clock"></i> ${localTimeStr} (Local)`;
    
    // Main (hidden but kept for any logic that might check it)
    document.getElementById('temperature').textContent = tempStr;
    document.getElementById('weather-desc').textContent = descStr;
    document.getElementById('weather-icon').src = `https://openweathermap.org/img/wn/${data.weather[0].icon}@4x.png`;
    
    // KPIs
    document.getElementById('kpi-temperature').textContent = window.getTempString(data.main.temp);
    document.getElementById('feels-like-label').textContent = 'Feels Like ' + window.getTempString(data.main.feels_like);
    document.getElementById('humidity').textContent = data.main.humidity + '%';
    document.getElementById('wind-speed').textContent = window.getWindString(data.wind.speed);
    document.getElementById('visibility').textContent = (data.visibility / 1000).toFixed(1) + ' km';
    document.getElementById('pressure').textContent = data.main.pressure + ' hPa';
    
    const rain = data.rain ? (data.rain['1h'] || 0) : 0;
    document.getElementById('rain').textContent = rain + ' mm';
    
    // Sun & Moon
    const sr = new Date((data.sys.sunrise + data.timezone + new Date().getTimezoneOffset()*60) * 1000);
    const ss = new Date((data.sys.sunset + data.timezone + new Date().getTimezoneOffset()*60) * 1000);
    document.getElementById('sunrise-time').textContent = sr.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    document.getElementById('sunset-time').textContent = ss.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    
    // Info
    document.getElementById('info-country').textContent = data.sys.country;
    let tzH = data.timezone / 3600;
    document.getElementById('info-tz').textContent = `UTC ${tzH >= 0 ? '+' : ''}${tzH}`;
    document.getElementById('info-coords').textContent = `${data.coord.lat.toFixed(2)}, ${data.coord.lon.toFixed(2)}`;
    
    // reset save button
    const saveBtn = document.getElementById('save-city-btn');
    if (saveBtn) {
        saveBtn.onclick = async () => {
            try {
                const res = await fetch('/api/cities/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({city: data.name})
                });
                const result = await res.json();
                if (result.success) {
                    window.showToast(`${data.name} saved!`);
                    window.fetchSavedCities();
                } else {
                    window.showToast(result.message);
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
            window.currentHourlyData = data.hourly;
            window.renderForecast(data.forecast);
            if(data.hourly) window.renderTimeline(data.hourly);
        }
    } catch(e) { console.error(e); }
};

window.renderForecast = (forecast) => {
    const container = document.getElementById('forecast-container');
    container.innerHTML = '';
    
    forecast.forEach(day => {
        const date = new Date(day.date).toLocaleDateString('en-GB', {weekday: 'short', day: 'numeric'});
        const row = document.createElement('div');
        row.className = 'forecast-row';
        row.innerHTML = `
            <div class="forecast-row-day">${date}</div>
            <img src="https://openweathermap.org/img/wn/${day.icon}.png" alt="icon">
            <div class="forecast-row-desc">${day.description}</div>
            <div style="font-weight: bold;">${window.getTempString(day.temp)}</div>
        `;
        container.appendChild(row);
    });
};

window.renderTimeline = (hourly) => {
    const container = document.getElementById('timeline-container');
    container.innerHTML = '';
    
    hourly.forEach(item => {
        const block = document.createElement('div');
        block.className = 'timeline-item';
        block.innerHTML = `
            <div class="timeline-time">${item.time}</div>
            <img src="https://openweathermap.org/img/wn/${item.icon}.png" alt="icon">
            <div class="timeline-temp">${window.getTempString(item.temp)}</div>
        `;
        container.appendChild(block);
    });
};

window.fetchAQI = async (lat, lon) => {
    try {
        const res = await fetch(`/api/aqi?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if(data.success) {
            document.getElementById('aqi-value').textContent = data.aqi || '--';
            const label = document.getElementById('aqi-label');
            label.textContent = data.label;
            
            label.className = 'aqi-badge';
            label.classList.add('aqi-' + data.label.toLowerCase().replace(' ', '-'));
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

window.updateTheme = (desc) => {
    const body = document.body;
    body.className = body.className.replace(/\btheme-[a-z]+\b/g, ''); // remove old
    if(desc.includes('thunderstorm') || desc.includes('storm')) body.classList.add('theme-thunderstorm');
    else if(desc.includes('rain') || desc.includes('drizzle')) body.classList.add('theme-rain');
    else if(desc.includes('snow')) body.classList.add('theme-snow');
    else if(desc.includes('fog') || desc.includes('mist')) body.classList.add('theme-fog');
    else if(desc.includes('cloud')) body.classList.add('theme-cloudy');
    else if(desc.includes('clear')) {
        const h = new Date().getHours();
        if(h > 18 || h < 6) body.classList.add('theme-night');
        else body.classList.add('theme-sunny');
    } else {
        body.classList.add('theme-sunny');
    }
};

window.showToast = (message) => {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<i class="fa-solid fa-circle-info" style="color: var(--accent); margin-right: 8px;"></i> ${message}`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

window.fetchSavedCities = async () => {
    const shelf = document.getElementById('saved-cities-shelf');
    const container = document.getElementById('saved-cities-container');
    if (!shelf) return;
    
    try {
        const res = await fetch('/api/cities/saved');
        const data = await res.json();
        if (data.success && data.cities.length > 0) {
            container.classList.remove('hidden');
            shelf.innerHTML = '';
            data.cities.forEach(c => {
                const card = document.createElement('div');
                card.className = 'saved-city-card';
                card.innerHTML = `
                    <button class="remove-btn" title="Remove city" onclick="window.unsaveCity(event, '${c.city}')"><i class="fa-solid fa-xmark"></i></button>
                    <strong>${c.city}</strong>
                `;
                card.onclick = () => {
                    document.getElementById('city-input').value = c.city;
                    fetchWeather(c.city);
                };
                shelf.appendChild(card);
            });
        } else {
            container.classList.add('hidden');
        }
    } catch(e) { console.error(e); }
};

window.fetchRecentSearches = async () => {
    const shelf = document.getElementById('recent-cities-shelf');
    const container = document.getElementById('recent-cities-container');
    if (!shelf) return;
    
    try {
        const res = await fetch('/api/weather/recent');
        const data = await res.json();
        if (data.success && data.recent.length > 0) {
            container.classList.remove('hidden');
            shelf.innerHTML = '';
            data.recent.forEach(c => {
                const card = document.createElement('div');
                card.className = 'saved-city-card';
                card.innerHTML = `<strong>${c}</strong>`;
                card.onclick = () => {
                    document.getElementById('city-input').value = c;
                    fetchWeather(c);
                };
                shelf.appendChild(card);
            });
        } else {
            container.classList.add('hidden');
        }
    } catch(e) { console.error(e); }
};

window.unsaveCity = async (e, city) => {
    e.stopPropagation();
    try {
        const res = await fetch('/api/cities/unsave', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city: city})
        });
        const result = await res.json();
        if(result.success) {
            window.showToast(`${city} removed.`);
            window.fetchSavedCities();
        }
    } catch(err) { console.error(err); }
};