document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('Service Worker registered', reg))
            .catch(err => console.error('Service Worker registration failed', err));
    }

    // Load saved cities
    window.fetchSavedCities();

    const searchBtn = document.getElementById('search-btn');
    const cityInput = document.getElementById('city-input');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeBtn = document.querySelector('.close-btn');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    
    // Check if city was passed in URL or saved last city
    const urlParams = new URLSearchParams(window.location.search);
    const initialCity = urlParams.get('city') || localStorage.getItem('lastCity') || 'Bengaluru';
    
    if (initialCity && cityInput) {
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
    if (cityInput) {
        cityInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            const suggestionsRow = document.getElementById('suggestions-row');
            if (!suggestionsRow) return;
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
    }

    if(exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            if(window.currentWeatherData) {
                window.location.href = `/api/weather/${encodeURIComponent(window.currentWeatherData.name)}/export/csv`;
            } else {
                window.showToast("Please search for a city first.");
            }
        });
    }
    const exportPdfBtn = document.getElementById('export-pdf-btn');
    if(exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            if(window.currentWeatherData) {
                window.open(`/api/weather/${encodeURIComponent(window.currentWeatherData.name)}/export/pdf`, '_blank');
            } else {
                window.showToast("Please search for a city first.");
            }
        });
    }
    const statusToggleBtn = document.getElementById('status-toggle');
    const statusModal = document.getElementById('status-modal');
    const closeStatusModal = document.getElementById('close-status-modal');
    if(statusToggleBtn && statusModal) {
        statusToggleBtn.addEventListener('click', () => {
            statusModal.classList.remove('hidden');
            window.fetchSystemStatus();
        });
    }
    if(closeStatusModal && statusModal) {
        closeStatusModal.addEventListener('click', () => statusModal.classList.add('hidden'));
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
            localStorage.setItem('unit', tempUnit === 'F' ? 'imperial' : 'metric');
            localStorage.setItem('windUnit', windUnit);
            const unitBtn = document.getElementById('unit-toggle');
            if (unitBtn) unitBtn.textContent = tempUnit === 'F' ? '°F' : '°C';
            settingsModal.classList.add('hidden');
            window.showToast("Settings saved.");
            
            // Re-render
            if(window.currentWeatherData) window.renderWeather(window.currentWeatherData);
            if(window.currentForecastData) window.renderForecast(window.currentForecastData);
            if(window.currentHourlyData) window.renderTimeline(window.currentHourlyData);
        });
    }

    window.addEventListener('unitChanged', () => {
        if(window.currentWeatherData) window.renderWeather(window.currentWeatherData);
        if(window.currentForecastData) window.renderForecast(window.currentForecastData);
        if(window.currentHourlyData) window.renderTimeline(window.currentHourlyData);
    });
});

async function fetchWeather(city) {
    const spinner = document.getElementById('loading-spinner');
    const wrapper = document.getElementById('dashboard-wrapper');
    const banner = document.getElementById('alert-banner');
    
    if(spinner) spinner.classList.remove('hidden');
    if(wrapper) wrapper.classList.add('hidden');
    if(banner) banner.classList.add('hidden');
    
    // Fetch Unsplash city background immediately
    window.fetchBackground(city);
    
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
            
            window.currentRainProb = data.rain_probability || 10;
            const rainProbEl = document.getElementById('rain-prob');
            if(rainProbEl) rainProbEl.textContent = window.currentRainProb + '%';
            
            // Highlights Banner
            const hbBanner = document.getElementById('highlights-banner');
            const hbWeather = document.getElementById('hb-weather');
            const hbRain = document.getElementById('hb-rain');
            if(hbBanner) hbBanner.classList.remove('hidden');
            if(hbWeather) hbWeather.textContent = `${data.data.weather[0].description.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} • ${window.getTempString(data.data.main.temp)}`;
            if(hbRain) hbRain.textContent = `${window.currentRainProb}% Chance of Rain`;
            
            // Trigger parallel fetches
            const lat = data.data.coord.lat;
            const lon = data.data.coord.lon;
            const desc = data.data.weather[0].description;
            
            window.fetchForecast(data.data.name);
            window.fetchAQI(lat, lon);
            window.fetchUV(lat, lon);
            window.fetchAlerts(lat, lon);
            window.updateTheme(desc);
            window.renderInsights(data.data, window.currentRainProb);
            
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
    const isImperial = localStorage.getItem('tempUnit') === 'F' || localStorage.getItem('unit') === 'imperial';
    if(isImperial) return Math.round((tempC * 9/5) + 32) + '°F';
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
        const highStr = window.getTempString(day.max_temp !== undefined ? day.max_temp : day.temp);
        const lowStr = window.getTempString(day.min_temp !== undefined ? day.min_temp : day.temp);
        row.innerHTML = `
            <div class="forecast-row-day">${date}</div>
            <img src="https://openweathermap.org/img/wn/${day.icon}.png" alt="icon">
            <div class="forecast-row-desc">${day.description}</div>
            <div class="forecast-temp-range">
                <span class="temp-high">${highStr}</span> / <span class="temp-low">${lowStr}</span>
            </div>
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
            
            const mainPollutantEl = document.getElementById('aqi-main-pollutant');
            if(mainPollutantEl && data.main_pollutant) {
                mainPollutantEl.textContent = `Main Pollutant: ${data.main_pollutant}`;
            }
            const hbAqi = document.getElementById('hb-aqi');
            if(hbAqi) {
                hbAqi.textContent = `AQI: ${data.label}`;
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

window.fetchBackground = async (city) => {
    if (!city) return;
    try {
        const res = await fetch(`/api/background/${encodeURIComponent(city)}`);
        const data = await res.json();
        if(data.success && data.url) {
            const bgEl = document.getElementById('bg-image');
            if (bgEl) {
                const img = new Image();
                img.onload = () => {
                    bgEl.style.backgroundImage = `url('${data.url}')`;
                };
                img.src = data.url;
            }
        }
    } catch(e) { console.error('Error fetching background image:', e); }
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

window.fetchUV = async (lat, lon) => {
    try {
        const res = await fetch(`/api/uv?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if(data.success) {
            const uvEl = document.getElementById('uv-index');
            const uvLbl = document.getElementById('uv-label');
            if(uvEl) uvEl.textContent = data.uvi;
            if(uvLbl) uvLbl.textContent = `UV Index (${data.category})`;
        }
    } catch(e) { console.error(e); }
};

window.renderInsights = (weather, rainProb) => {
    const list = document.getElementById('weather-insights-list');
    if(!list) return;
    list.innerHTML = '';
    
    const temp = weather.main.temp;
    const wind = weather.wind.speed;
    const desc = weather.weather[0].description.toLowerCase();
    
    const items = [];
    // Bullet 1: Activity
    if(temp >= 18 && temp <= 28 && !desc.includes('rain') && !desc.includes('storm')) {
        items.push('🏃 Pleasant temperature and clear skies make outdoor sports and exercise ideal today.');
    } else if(temp > 32) {
        items.push('🔥 Extreme heat detected. Keep strenuous outdoor activity to early morning or evening.');
    } else if(temp < 10) {
        items.push('🧥 Cold temperatures outside. Wear warm layered clothing if heading outdoors.');
    } else {
        items.push('🚶 Moderate outdoor conditions. Stay prepared for shifting weather.');
    }
    
    // Bullet 2: Rain
    if(rainProb >= 60 || desc.includes('rain') || desc.includes('storm')) {
        items.push('☔ High chance of precipitation. Carry an umbrella and allow extra travel time.');
    } else {
        items.push('🌤️ Low chance of rain expected today. Favorable for commuting and travel.');
    }
    
    // Bullet 3: Wind & Comfort
    if(wind > 10) {
        items.push('💨 Strong winds reported. Secure light patio items and be cautious on elevated roads.');
    } else {
        items.push('🍃 Light breezes contribute to comfortable ambient air circulation.');
    }
    
    // Bullet 4: Air Quality & Health
    items.push('🌿 Monitor local air quality levels if you have sensitive respiratory conditions.');

    items.forEach(text => {
        const li = document.createElement('li');
        li.style.cssText = 'background: rgba(255,255,255,0.05); padding: 0.8rem 1rem; border-radius: 8px; border-left: 3px solid var(--accent); font-size: 0.9rem;';
        li.textContent = text;
        list.appendChild(li);
    });
};

window.fetchSystemStatus = async () => {
    const grid = document.getElementById('status-cards-grid');
    if(!grid) return;
    grid.innerHTML = '<div style="grid-column: span 2; text-align: center; padding: 2rem;">Loading System Diagnostics...</div>';
    try {
        const res = await fetch('/api/system-status');
        const data = await res.json();
        if(data.success && data.status) {
            grid.innerHTML = '';
            Object.values(data.status).forEach(srv => {
                const card = document.createElement('div');
                card.className = 'status-card';
                card.innerHTML = `
                    <div class="status-card-header">
                        <span>${srv.name}</span>
                        <span class="status-badge ${srv.status === 'Online' ? 'status-online' : 'status-degraded'}">${srv.status}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #adb5bd;">${srv.database || srv.ttl || 'Operational'}</div>
                    ${srv.api_key_status ? `<div class="status-key-secure"><i class="fa-solid fa-lock"></i> API Key: ${srv.api_key_status}</div>` : ''}
                `;
                grid.appendChild(card);
            });
        }
    } catch(e) {
        console.error(e);
        grid.innerHTML = '<div style="grid-column: span 2; color: #ef4444;">Failed to load system status.</div>';
    }
};