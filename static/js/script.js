document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
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
    
    // Initialize AI Chat Widget
    if (window.initChatWidget) window.initChatWidget();
    
    const refreshBriefingBtn = document.getElementById('refresh-briefing-btn');
    if (refreshBriefingBtn) {
        refreshBriefingBtn.addEventListener('click', () => {
            const currentCity = window.currentWeatherData ? window.currentWeatherData.name : (localStorage.getItem('lastCity') || 'Bengaluru');
            window.fetchBriefing(currentCity, true);
        });
    }

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
    
    // Autocomplete simulation with 300ms debounce
    let debounceTimer = null;
    if (cityInput) {
        cityInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const val = e.target.value.toLowerCase().trim();
                const suggestionsRow = document.getElementById('suggestions-row');
                if (!suggestionsRow) return;
                const popularCities = ['Bengaluru', 'London', 'Tokyo', 'Paris', 'New York', 'Dubai', 'Sydney', 'Mumbai', 'Singapore', 'Berlin'];
                
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
            }, 300);
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

let currentSearchId = 0;

async function fetchWeather(city) {
    const searchId = ++currentSearchId;
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
        
        // Prevent stale responses from overwriting newer search
        if (searchId !== currentSearchId) return;
        
        if (data.success) {
            localStorage.setItem('lastCity', data.data.name);
            window.currentWeatherData = data.data; // save for unit toggle
            window.renderWeather(data.data, data.comfort_score, data.comfort_label);
            
            if(data.ai_summary) {
                const aiSumEl = document.getElementById('ai-summary-text');
                if (aiSumEl) aiSumEl.textContent = data.ai_summary;
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
            const icon = data.data.weather[0].icon;
            
            window.fetchForecast(data.data.name);
            window.fetchAQI(lat, lon);
            window.fetchUV(lat, lon);
            window.fetchAlerts(lat, lon);
            window.updateTheme(desc);
            window.updateWeatherEffects(desc, icon);
            if (window.Weather3D) {
                window.Weather3D.updateScene(icon, data.data.weather[0].main, desc);
            }
            window.renderInsights(data.data, window.currentRainProb);
            window.fetchBriefing(data.data.name);
            window.fetchCityEncyclopedia(data.data.name);
            
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
        if (searchId === currentSearchId && spinner) spinner.classList.add('hidden');
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

window.getWeatherEmoji = (desc, icon, windSpeed) => {
    desc = (desc || '').toLowerCase();
    icon = icon || '';
    const isNight = icon.endsWith('n');
    
    if (desc.includes('thunderstorm') || desc.includes('storm')) return '⛈️';
    if (desc.includes('snow') || desc.includes('sleet') || desc.includes('blizzard')) return '❄️';
    if (desc.includes('drizzle')) return '🌦️';
    if (desc.includes('heavy rain') || desc.includes('shower rain')) return '🌧️';
    if (desc.includes('rain')) return isNight ? '🌧️' : '🌦️';
    if (desc.includes('fog') || desc.includes('mist') || desc.includes('haze') || desc.includes('smoke')) return '🌫️';
    if (windSpeed && windSpeed > 10) return '🌬️';
    if (desc.includes('few clouds') || desc.includes('scattered clouds')) return isNight ? '☁️' : '🌤️';
    if (desc.includes('broken clouds') || desc.includes('partly cloudy')) return isNight ? '☁️' : '⛅';
    if (desc.includes('cloud') || desc.includes('overcast')) return '☁️';
    if (desc.includes('clear')) return isNight ? '🌙' : '☀️';
    return isNight ? '🌙' : '☀️';
};

window.updateWeatherEffects = (desc, icon) => {
    const layer = document.getElementById('weather-effects-layer');
    if (!layer) return;
    layer.className = 'weather-effects-layer';
    desc = (desc || '').toLowerCase();
    icon = icon || '';
    
    if (desc.includes('thunderstorm') || desc.includes('storm')) {
        layer.classList.add('thunderstorm', 'rain');
    } else if (desc.includes('rain') || desc.includes('drizzle')) {
        layer.classList.add('rain');
    } else if (desc.includes('snow')) {
        layer.classList.add('snow');
    } else if (desc.includes('cloud') || desc.includes('overcast')) {
        layer.classList.add('clouds');
    } else if (desc.includes('clear')) {
        if (!icon.endsWith('n')) {
            layer.classList.add('sunshine');
        }
    }
};

window.fetchBriefing = async (city, forceRefresh = false) => {
    const skeleton = document.getElementById('briefing-skeleton');
    const textEl = document.getElementById('briefing-text');
    const badgeEl = document.getElementById('briefing-badge');
    const timeEl = document.getElementById('briefing-timestamp');
    const mySearchId = currentSearchId;
    
    if (skeleton) skeleton.classList.remove('hidden');
    if (textEl) textEl.style.display = 'none';
    
    try {
        const res = await fetch(`/api/weather/${encodeURIComponent(city)}/briefing?refresh=${forceRefresh ? 'true' : 'false'}`);
        const data = await res.json();
        if (mySearchId !== currentSearchId) return;
        
        if (skeleton) skeleton.classList.add('hidden');
        if (textEl) {
            textEl.style.display = 'block';
            textEl.textContent = data.briefing || "Weather briefing is currently unavailable.";
        }
        if (badgeEl) {
            if (data.is_ai_generated) {
                badgeEl.className = 'ai-badge';
                badgeEl.innerHTML = `<i class="fa-solid fa-sparkles"></i> ${data.model || 'Gemini AI'}`;
            } else {
                badgeEl.className = 'ai-badge';
                badgeEl.style.background = 'rgba(16, 185, 129, 0.15)';
                badgeEl.style.color = '#10b981';
                badgeEl.innerHTML = `<i class="fa-solid fa-calculator"></i> Grounded Engine`;
            }
        }
        if (timeEl) {
            timeEl.textContent = data.cached ? `Cached (${data.timestamp})` : `Updated (${data.timestamp})`;
        }
    } catch(e) {
        console.error('Error fetching briefing:', e);
        if (mySearchId !== currentSearchId) return;
        if (skeleton) skeleton.classList.add('hidden');
        if (textEl) {
            textEl.style.display = 'block';
            textEl.textContent = "AI briefing could not be loaded at this time.";
        }
    }
};

window.initChatWidget = () => {
    const toggleBtn = document.getElementById('chat-widget-toggle');
    const chatPanel = document.getElementById('chat-panel');
    const closeBtn = document.getElementById('close-chat-btn');
    const sendBtn = document.getElementById('chat-send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const chips = document.querySelectorAll('.chat-chip');
    
    if (!toggleBtn || !chatPanel) return;
    
    toggleBtn.addEventListener('click', () => {
        chatPanel.classList.toggle('hidden');
        if (!chatPanel.classList.contains('hidden') && chatInput) {
            chatInput.focus();
        }
    });
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => chatPanel.classList.add('hidden'));
    }
    
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.getAttribute('data-question');
            if (q && chatInput) {
                chatInput.value = q;
                handleChatSend();
            }
        });
    });
    
    const handleChatSend = async () => {
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Append user message
        const userBubble = document.createElement('div');
        userBubble.className = 'chat-bubble user';
        userBubble.textContent = text;
        chatBody.appendChild(userBubble);
        chatInput.value = '';
        
        // Typing indicator
        const aiBubble = document.createElement('div');
        aiBubble.className = 'chat-bubble ai';
        aiBubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consulting weather data...';
        chatBody.appendChild(aiBubble);
        chatBody.scrollTop = chatBody.scrollHeight;
        
        const activeCity = window.currentWeatherData ? window.currentWeatherData.name : (localStorage.getItem('lastCity') || 'Bengaluru');
        
        try {
            const res = await fetch('/api/weather/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: text, city: activeCity })
            });
            const data = await res.json();
            if (data.success && data.answer) {
                aiBubble.textContent = data.answer;
            } else {
                aiBubble.textContent = data.message || "I could not retrieve an answer right now. Please try again.";
            }
        } catch(e) {
            console.error('Chat error:', e);
            aiBubble.textContent = "Network error. Please check your connection.";
        }
        chatBody.scrollTop = chatBody.scrollHeight;
    };
    
    if (sendBtn) sendBtn.addEventListener('click', handleChatSend);
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleChatSend();
        });
    }
};

window.renderWeather = (data, comfortScore, comfortLabel) => {
    document.getElementById('loading-spinner').classList.add('hidden');
    const wrapper = document.getElementById('dashboard-wrapper');
    if (wrapper) wrapper.classList.remove('hidden');
    
    document.getElementById('city-name').textContent = `📍 ${data.name}`;
    
    const descStr = data.weather[0].description;
    const iconCode = data.weather[0].icon;
    const tempStr = window.getTempString(data.main.temp);
    const emoji = window.getWeatherEmoji(descStr, iconCode, data.wind ? data.wind.speed : 0);
    
    // Capitalize description
    const capDesc = descStr.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    
    document.getElementById('city-subtitle').textContent = `${emoji} ${capDesc} • ${tempStr}`;
    
    // Calculate and display local time
    const utcTime = new Date().getTime() + (new Date().getTimezoneOffset() * 60000);
    const cityTime = new Date(utcTime + (data.timezone * 1000));
    const dtOpts = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
    const localTimeStr = cityTime.toLocaleTimeString('en-US', dtOpts);
    
    document.getElementById('city-local-time').innerHTML = `<i class="fa-regular fa-clock"></i> ${localTimeStr} (Local)`;
    
    // Main
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
    
    // Comfort Score KPI
    const csVal = document.getElementById('comfort-score-val');
    const csLabel = document.getElementById('comfort-score-label');
    if (csVal) csVal.textContent = (comfortScore !== undefined && comfortScore !== null) ? `${comfortScore}/100` : '--';
    if (csLabel) csLabel.textContent = comfortLabel ? `Comfort: ${comfortLabel}` : 'Comfort Score';
    
    // Unsplash attribution update
    const attrCity = document.getElementById('attr-city');
    if (attrCity) attrCity.textContent = data.name;
    
    const rain = data.rain ? (data.rain['1h'] || 0) : 0;
    document.getElementById('rain').textContent = rain + ' mm';
    
    // Sun & Moon
    const sr = new Date((data.sys.sunrise + data.timezone + new Date().getTimezoneOffset()*60) * 1000);
    const ss = new Date((data.sys.sunset + data.timezone + new Date().getTimezoneOffset()*60) * 1000);
    document.getElementById('sunrise-time').textContent = sr.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    document.getElementById('sunset-time').textContent = ss.toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'});
    
    // Info
    const infoCountry = document.getElementById('info-country');
    if (infoCountry) infoCountry.textContent = data.sys.country;
    let tzH = data.timezone / 3600;
    const infoTz = document.getElementById('info-tz');
    if (infoTz) infoTz.textContent = `UTC ${tzH >= 0 ? '+' : ''}${tzH}`;
    const infoCoords = document.getElementById('info-coords');
    if (infoCoords) infoCoords.textContent = `${data.coord.lat.toFixed(2)}, ${data.coord.lon.toFixed(2)}`;

    // Dynamic Hero Greeting & Badges matching Mockup
    const hour = cityTime.getHours();
    let greetingPrefix = "Good morning";
    if (hour >= 12 && hour < 17) greetingPrefix = "Good afternoon";
    else if (hour >= 17 && hour < 21) greetingPrefix = "Good evening";
    else if (hour >= 21 || hour < 5) greetingPrefix = "Good night";
    const heroGreeting = document.getElementById('hero-greeting');
    if (heroGreeting) heroGreeting.textContent = `${greetingPrefix}, ${data.name} ${emoji}`;

    const dateStr = cityTime.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = cityTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const cityLocalTimeEl = document.getElementById('city-local-time');
    if (cityLocalTimeEl) cityLocalTimeEl.textContent = `${dateStr} | ${timeStr}`;

        // Dynamically update CSV export URLs for active city
    const expCurrent = document.getElementById('export-current-weather-csv');
    if (expCurrent) expCurrent.href = `/api/weather/${encodeURIComponent(data.name)}/export/csv`;
    const expHourly = document.getElementById('export-hourly-forecast-csv');
    if (expHourly) expHourly.href = `/api/forecast/${encodeURIComponent(data.name)}/export/hourly/csv`;
    const expWeekly = document.getElementById('export-weekly-forecast-csv');
    if (expWeekly) expWeekly.href = `/api/forecast/${encodeURIComponent(data.name)}/export/weekly/csv`;

    const fcBadge = document.getElementById('fc-city-badge');
    if (fcBadge) fcBadge.textContent = `📍 ${data.name}, ${data.sys.country}`;

    // Quick Info Card
    const qiCapital = document.getElementById('qi-capital');
    if (qiCapital) qiCapital.textContent = data.name;
    const qiCountry = document.getElementById('qi-country');
    if (qiCountry) qiCountry.textContent = data.sys.country;
    const qiTz = document.getElementById('qi-timezone');
    if (qiTz) qiTz.textContent = `UTC ${tzH >= 0 ? '+' : ''}${tzH}`;

    // Discover Card
    const discoverTitle = document.getElementById('discover-city-title');
    if (discoverTitle) discoverTitle.innerHTML = `<i class="fa-solid fa-book-open" style="color: var(--blue-primary);"></i> Discover ${data.name}`;

    // Map Button binding
    const mapBtn = document.getElementById('qi-view-map-btn');
    if (mapBtn) {
        mapBtn.onclick = () => {
            const mapModal = document.getElementById('map-modal');
            if (mapModal) {
                mapModal.classList.remove('hidden');
                if (window.leafletMap) {
                    setTimeout(() => window.leafletMap.invalidateSize(), 200);
                }
            }
        };
    }
    const closeMapModal = document.getElementById('close-map-modal');
    if (closeMapModal) {
        closeMapModal.onclick = () => {
            const mapModal = document.getElementById('map-modal');
            if (mapModal) mapModal.classList.add('hidden');
        };
    }
    
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
    if (!container) return;
    container.innerHTML = '';
    
    // Support either 5-column tile grid or row fallback
    const days = (forecast || []).slice(0, 5);
    days.forEach((day, idx) => {
        const dObj = new Date(day.date);
        const dayName = idx === 0 ? 'Today' : dObj.toLocaleDateString('en-US', {weekday: 'short'});
        const dateStr = dObj.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
        const highStr = window.getTempString(day.max_temp !== undefined ? day.max_temp : day.temp);
        const lowStr = window.getTempString(day.min_temp !== undefined ? day.min_temp : day.temp);
        
        const tile = document.createElement('div');
        tile.className = 'forecast-day-tile';
        tile.innerHTML = `
            <div class="forecast-tile-day">${dayName}</div>
            <div class="forecast-tile-date">${dateStr}</div>
            <img src="https://openweathermap.org/img/wn/${day.icon}.png" alt="Weather icon" style="width: 38px; height: 38px;">
            <div class="forecast-tile-temp">${highStr}</div>
            <div class="forecast-tile-cond">${day.description}</div>
        `;
        container.appendChild(tile);
    });
};

window.renderTimeline = (hourly) => {
    const container = document.getElementById('timeline-container');
    if (container) {
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
    }

    const canvas = document.getElementById('hourly-curve-canvas');
    if (canvas && typeof Chart !== 'undefined') {
        const isImperial = localStorage.getItem('tempUnit') === 'F' || localStorage.getItem('unit') === 'imperial';
        const points = (hourly || []).slice(0, 8);
        const labels = points.map(p => p.time || '');
        const temps = points.map(p => {
            let t = p.temp;
            if (isImperial) {
                t = Math.round((t * 9/5) + 32);
            } else {
                t = Math.round(t);
            }
            return t;
        });

        if (window.hourlyChartInstance) {
            window.hourlyChartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 160);
        gradient.addColorStop(0, 'rgba(49, 133, 214, 0.28)');
        gradient.addColorStop(1, 'rgba(49, 133, 214, 0.01)');

        window.hourlyChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Temperature',
                    data: temps,
                    borderColor: '#3185D6',
                    borderWidth: 2.5,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#FFFFFF',
                    pointBorderColor: '#3185D6',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.parsed.y}${isImperial ? '°F' : '°C'}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 10, family: 'Inter' }, color: '#64788B' }
                    },
                    y: {
                        display: false,
                        suggestedMin: Math.min(...temps) - 2,
                        suggestedMax: Math.max(...temps) + 2
                    }
                }
            }
        });
    }
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

window.fetchBackground = async (city, weatherDesc = '') => {
    if (!city) return;
    try {
        const url = weatherDesc
            ? `/api/background/${encodeURIComponent(city)}/${encodeURIComponent(weatherDesc)}`
            : `/api/background/${encodeURIComponent(city)}`;
        const res = await fetch(url);
        const data = await res.json();
        if(data.success && data.url) {
            const bgEl = document.getElementById('bg-image');
            const heroPanorama = document.getElementById('hero-panorama');
            const discoverThumb = document.getElementById('discover-city-thumb');
            
            const img = new Image();
            img.onload = () => {
                if (bgEl) bgEl.style.backgroundImage = `url('${data.url}')`;
                if (heroPanorama) heroPanorama.style.backgroundImage = `url('${data.url}')`;
                if (discoverThumb) discoverThumb.src = data.url;
            };
            img.onerror = () => {
                const fallbackUrl = "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1600&q=80";
                if (bgEl) bgEl.style.backgroundImage = `url('${fallbackUrl}')`;
                if (heroPanorama) heroPanorama.style.backgroundImage = `url('${fallbackUrl}')`;
            };
            img.src = data.url;
            
            // Photographer and Unsplash attribution compliance using safe DOM nodes
            const attrEl = document.getElementById('photo-attribution');
            if (attrEl) {
                attrEl.textContent = '';
                const icon = document.createElement('i');
                icon.className = 'fa-solid fa-camera';
                icon.style.marginRight = '6px';

                const spanBefore = document.createElement('span');
                spanBefore.textContent = ' Photo by ';

                const photoLink = document.createElement('a');
                photoLink.href = data.photographer_url || 'https://unsplash.com/?utm_source=ClimaSense&utm_medium=referral';
                photoLink.target = '_blank';
                photoLink.rel = 'noopener noreferrer';
                photoLink.textContent = data.photographer_name || 'Unsplash Community';

                const spanMid = document.createElement('span');
                spanMid.textContent = ' on ';

                const unsplashLink = document.createElement('a');
                unsplashLink.href = 'https://unsplash.com/?utm_source=ClimaSense&utm_medium=referral';
                unsplashLink.target = '_blank';
                unsplashLink.rel = 'noopener noreferrer';
                unsplashLink.textContent = 'Unsplash';

                attrEl.appendChild(icon);
                attrEl.appendChild(spanBefore);
                attrEl.appendChild(photoLink);
                attrEl.appendChild(spanMid);
                attrEl.appendChild(unsplashLink);
            }
        }
    } catch(e) { console.error('Error fetching background image:', e); }
};

window.updateTheme = (desc) => {
    // Strict Light Theme enforcement: zero dark mode classes
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
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

window.fetchCityEncyclopedia = async (city) => {
    const encWrapper = document.getElementById('encyclopedia-wrapper');
    const encTitle = document.getElementById('encyclopedia-city-title');
    const encLead = document.getElementById('encyclopedia-lead-paragraph');
    const tocList = document.getElementById('toc-list');
    const articleBody = document.getElementById('encyclopedia-article-body');
    const badgeWordCount = document.getElementById('badge-word-count');
    const badgeReadingTime = document.getElementById('badge-reading-time');

    if (!encWrapper || !encTitle || !articleBody) return;

    try {
        const res = await fetch(`/api/encyclopedia/${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data.success && data.article) {
            const article = data.article;
            encTitle.textContent = `${article.city} — Municipal & Meteorological Monograph`;
            if (badgeWordCount) {
                badgeWordCount.innerHTML = `<i class="fa-solid fa-file-lines"></i> <strong>${article.total_word_count.toLocaleString()} Words</strong>`;
            }
            if (badgeReadingTime) {
                badgeReadingTime.innerHTML = `<i class="fa-solid fa-clock"></i> <strong>${article.reading_time_minutes} min read</strong>`;
            }
            if (encLead) {
                encLead.textContent = article.summary || '';
            }

            // Table of Contents
            if (tocList) {
                tocList.innerHTML = '';
                article.sections.forEach((sec, idx) => {
                    const li = document.createElement('li');
                    const link = document.createElement('a');
                    link.className = 'toc-link';
                    link.href = `#encyclopedia-sec-${idx}`;
                    link.innerHTML = `<i class="fa-solid fa-angle-right" style="font-size:0.75rem; margin-right:4px;"></i> ${sec.title}`;
                    link.onclick = (e) => {
                        e.preventDefault();
                        const target = document.getElementById(`encyclopedia-sec-${idx}`);
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            document.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
                            link.classList.add('active');
                        }
                    };
                    li.appendChild(link);
                    tocList.appendChild(li);
                });
            }

            // Monograph Sections
            articleBody.innerHTML = '';
            article.sections.forEach((sec, idx) => {
                const secEl = document.createElement('section');
                secEl.id = `encyclopedia-sec-${idx}`;
                secEl.className = 'encyclopedia-section';

                const h2 = document.createElement('h2');
                h2.innerHTML = `${sec.title} <span class="encyclopedia-citation">[Ref: City Archive ${idx + 1}]</span>`;
                secEl.appendChild(h2);

                if (sec.content) {
                    const paragraphs = sec.content.split('\n\n');
                    paragraphs.forEach(pText => {
                        if (pText.trim()) {
                            const p = document.createElement('p');
                            p.textContent = pText.trim();
                            secEl.appendChild(p);
                        }
                    });
                }

                articleBody.appendChild(secEl);
            });

            encWrapper.classList.remove('hidden');
        }
    } catch (e) {
        console.error('Error fetching city encyclopedia:', e);
    }
};
