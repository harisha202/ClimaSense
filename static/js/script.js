// ClimaSense - Complete Weather & City Discovery Controller
document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .catch(err => console.warn('Service Worker registration skipped:', err));
    }

    // Load saved cities on startup
    if (window.fetchSavedCities) window.fetchSavedCities();

    const searchBtn = document.getElementById('search-btn');
    const cityInput = document.getElementById('city-input');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeBtn = document.querySelector('.close-btn');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const saveCityBtn = document.getElementById('save-city-btn');
    
    // Check if city was passed in URL or saved in current active session
    const urlParams = new URLSearchParams(window.location.search);
    const initialCity = urlParams.get('city') || sessionStorage.getItem('currentSearchCity');
    
    // Initialize AI Chat Widget
    if (window.initChatWidget) window.initChatWidget();
    
    const refreshBriefingBtn = document.getElementById('refresh-briefing-btn');
    if (refreshBriefingBtn) {
        refreshBriefingBtn.addEventListener('click', () => {
            const currentCity = window.currentWeatherData ? window.currentWeatherData.name : sessionStorage.getItem('currentSearchCity');
            if (currentCity) {
                window.fetchBriefing(currentCity, true);
            }
        });
    }

    // Initial weather load: ONLY if there is an explicit city query parameter or restored session
    if (initialCity && initialCity.trim()) {
        if (cityInput) {
            cityInput.value = initialCity;
            fetchWeather(initialCity);
        }
    } else {
        // Plain white default background across the entire website before city search
        if (window.resetToPlainWhiteBackground) window.resetToPlainWhiteBackground();
    }
    
    // Bind search button
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const city = cityInput ? cityInput.value.trim() : '';
            if (city) fetchWeather(city);
        });
    }

    // Bind Enter key in search input
    if (cityInput) {
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const city = cityInput.value.trim();
                if (city) fetchWeather(city);
            }
        });
    }

    // Save city button
    if (saveCityBtn) {
        saveCityBtn.addEventListener('click', async () => {
            const cityToSave = window.currentWeatherData ? window.currentWeatherData.name : (cityInput ? cityInput.value.trim() : '');
            if (!cityToSave) {
                window.showToast("Please search for a city first.");
                return;
            }
            try {
                const res = await fetch('/api/cities/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({city: cityToSave})
                });
                const result = await res.json();
                if (result.success) {
                    window.showToast(`Saved ${cityToSave} to your bookmarks!`);
                    if (window.fetchSavedCities) window.fetchSavedCities();
                } else {
                    window.showToast(result.message || 'City could not be saved.');
                }
            } catch(e) {
                console.error(e);
                window.showToast("Could not save city.");
            }
        });
    }
    
    // Autocomplete simulation with 250ms debounce
    let debounceTimer = null;
    if (cityInput) {
        cityInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const val = e.target.value.toLowerCase().trim();
                const suggestionsRow = document.getElementById('suggestions-row');
                if (!suggestionsRow) return;
                const popularCities = ['London', 'Tokyo', 'Paris', 'New York', 'Dubai', 'Sydney', 'Bengaluru', 'Singapore', 'Berlin', 'Rome', 'San Francisco', 'Toronto'];
                
                if (val.length > 0) {
                    const matches = popularCities.filter(c => c.toLowerCase().startsWith(val));
                    if (matches.length > 0) {
                        suggestionsRow.innerHTML = '';
                        matches.slice(0, 6).forEach(m => {
                            const pill = document.createElement('div');
                            pill.style.cssText = 'padding: 0.35rem 0.85rem; border-radius: 9999px; background: var(--blue-pale); color: var(--blue-deep); font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s;';
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
            }, 250);
        });

        // Hide suggestions on outside click
        document.addEventListener('click', (e) => {
            const suggestionsRow = document.getElementById('suggestions-row');
            if (suggestionsRow && !cityInput.contains(e.target) && !suggestionsRow.contains(e.target)) {
                suggestionsRow.classList.add('hidden');
            }
        });
    }

    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            if (window.currentWeatherData) {
                window.location.href = `/api/weather/${encodeURIComponent(window.currentWeatherData.name)}/export/csv`;
            } else {
                window.showToast("Please search for a city first.");
            }
        });
    }

    const exportPdfBtn = document.getElementById('export-pdf-btn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            if (window.currentWeatherData) {
                window.open(`/api/weather/${encodeURIComponent(window.currentWeatherData.name)}/export/pdf`, '_blank');
            } else {
                window.showToast("Please search for a city first.");
            }
        });
    }

    const statusToggleBtn = document.getElementById('status-toggle');
    const statusModal = document.getElementById('status-modal');
    const closeStatusModal = document.getElementById('close-status-modal');
    if (statusToggleBtn && statusModal) {
        statusToggleBtn.addEventListener('click', () => {
            statusModal.classList.remove('hidden');
            window.fetchSystemStatus();
        });
    }
    if (closeStatusModal && statusModal) {
        closeStatusModal.addEventListener('click', () => statusModal.classList.add('hidden'));
    }
    
    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
    }
    if (closeBtn && settingsModal) {
        closeBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    }

    window.addEventListener('unitChanged', () => {
        if (window.currentWeatherData) window.renderWeather(window.currentWeatherData);
        if (window.currentForecastData) window.renderForecast(window.currentForecastData);
        if (window.currentHourlyData) window.renderTimeline(window.currentHourlyData);
    });
});

let currentSearchId = 0;
let currentBgSearchId = 0;

async function fetchWeather(city) {
    if (!city || !city.trim()) return;
    const searchId = ++currentSearchId;
    const spinner = document.getElementById('loading-spinner');
    const wrapper = document.getElementById('dashboard-wrapper');
    const banner = document.getElementById('alert-banner');
    
    if (spinner) spinner.classList.remove('hidden');
    if (banner) banner.classList.add('hidden');
    
    try {
        const res = await fetch(`/api/weather/${encodeURIComponent(city.trim())}`);
        const data = await res.json();
        
        // Prevent stale responses from overwriting newer search
        if (searchId !== currentSearchId) return;
        
        if (data.success && data.data) {
            const canonicalCity = data.data.name;
            const desc = (data.data.weather && data.data.weather[0]) ? data.data.weather[0].description : '';
            const icon = (data.data.weather && data.data.weather[0]) ? data.data.weather[0].icon : '01d';
            const lat = data.data.coord ? data.data.coord.lat : null;
            const lon = data.data.coord ? data.data.coord.lon : null;

            sessionStorage.setItem('currentSearchCity', canonicalCity);
            localStorage.setItem('lastCity', canonicalCity);
            const cityInput = document.getElementById('city-input');
            if (cityInput) cityInput.value = canonicalCity;

            window.currentWeatherData = data.data;
            window.renderWeather(data.data, data.comfort_score, data.comfort_label);
            
            const country = (data.data.sys && data.data.sys.country) ? data.data.sys.country : '';
            // Step 4 & 6: Fetch Unsplash city background with canonical name, mood, and country
            window.fetchBackground(canonicalCity, desc, searchId, country);
            
            // Highlights Banner
            const hbBanner = document.getElementById('highlights-banner');
            const hbWeather = document.getElementById('hb-weather');
            const hbRain = document.getElementById('hb-rain');
            const hbRainBox = document.getElementById('hb-rain-box');
            const hbRainDivider = document.getElementById('hb-rain-divider');
            if (hbBanner) hbBanner.classList.remove('hidden');
            if (hbWeather) hbWeather.textContent = `${desc ? desc.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : 'Current Conditions'} • ${window.getTempString(data.data.main.temp)}`;
            if (data.rain_probability !== undefined && data.rain_probability !== null) {
                window.currentRainProb = data.rain_probability;
                if (hbRain) hbRain.textContent = `${data.rain_probability}% Chance of Rain`;
                if (hbRainBox) hbRainBox.style.display = 'inline-flex';
                if (hbRainDivider) hbRainDivider.style.display = 'inline-block';
            } else {
                window.currentRainProb = null;
                if (hbRainBox) hbRainBox.style.display = 'none';
                if (hbRainDivider) hbRainDivider.style.display = 'none';
            }
            
            // Trigger parallel fetches for the selected city
            if (window.fetchForecast) window.fetchForecast(canonicalCity);
            if (lat !== null && lon !== null) {
                if (window.fetchAQI) window.fetchAQI(lat, lon);
                if (window.fetchUV) window.fetchUV(lat, lon);
                if (window.fetchAlerts) window.fetchAlerts(lat, lon);
                if (window.initMap) window.initMap(lat, lon, canonicalCity);
            }
            if (window.Weather3D) {
                window.Weather3D.updateScene(icon, data.data.weather[0].main, desc);
            }
            if (window.fetchBriefing) window.fetchBriefing(canonicalCity);
            if (window.fetchCityEncyclopedia) window.fetchCityEncyclopedia(canonicalCity, country);
            if (window.joinCityRoom) window.joinCityRoom(canonicalCity);
        } else {
            if (searchId === currentSearchId) {
                if (spinner) spinner.classList.add('hidden');
                if (wrapper) wrapper.classList.remove('hidden');
                window.showToast(data.message || `City "${city}" could not be found.`);
            }
        }
    } catch(e) {
        console.error('Fetch weather error:', e);
        if (searchId === currentSearchId) {
            if (spinner) spinner.classList.add('hidden');
            if (wrapper) wrapper.classList.remove('hidden');
            window.showToast("Network error retrieving weather data. Please try again.");
        }
    }
}

window.getTempString = (tempC) => {
    if (tempC === undefined || tempC === null) return '--°C';
    const isImperial = localStorage.getItem('tempUnit') === 'F' || localStorage.getItem('unit') === 'imperial';
    if (isImperial) return Math.round((tempC * 9/5) + 32) + '°F';
    return Math.round(tempC) + '°C';
};

window.getWindString = (speedMS) => {
    if (speedMS === undefined || speedMS === null) return '-- km/h';
    const unit = localStorage.getItem('windUnit') || 'kmh';
    if (unit === 'mph') return Math.round(speedMS * 2.23694) + ' mph';
    if (unit === 'ms') return Math.round(speedMS) + ' m/s';
    return Math.round(speedMS * 3.6) + ' km/h';
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

window.resetToPlainWhiteBackground = () => {
    const pageBg = document.getElementById('page-background-layer');
    if (pageBg) {
        pageBg.style.backgroundImage = 'none';
        pageBg.classList.remove('has-image');
    }
    const pageOverlay = document.getElementById('page-background-overlay');
    if (pageOverlay) {
        pageOverlay.classList.remove('has-image');
    }
    const heroBg = document.getElementById('hero-panorama');
    if (heroBg) {
        heroBg.style.backgroundImage = 'none';
    }
    const attrBox = document.getElementById('hero-photographer-attribution');
    if (attrBox) {
        attrBox.classList.add('hidden');
    }
};

window.fetchBackground = async (city, weatherDesc = '', searchId = 0, country = '') => {
    if (!city) return;
    const bgSearchId = ++currentBgSearchId;
    try {
        let baseEndpoint = weatherDesc
            ? `/api/background/${encodeURIComponent(city)}/${encodeURIComponent(weatherDesc)}`
            : `/api/background/${encodeURIComponent(city)}`;
        let url = `${baseEndpoint}?t=${Date.now()}`;
        if (country) {
            url += `&country=${encodeURIComponent(country)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        
        // Race condition prevention: check if newer search began
        if (searchId && searchId !== currentSearchId) return;
        if (bgSearchId !== currentBgSearchId) return;
        
        if (data.success && data.url) {
            const pageBg = document.getElementById('page-background-layer');
            const pageOverlay = document.getElementById('page-background-overlay');
            const discoverThumb = document.getElementById('discover-city-thumb');
            const attrBox = document.getElementById('hero-photographer-attribution');
            const attrLink = document.getElementById('hero-photographer-link');
            
            const img = new Image();
            img.onload = () => {
                if (searchId && searchId !== currentSearchId) return;
                if (bgSearchId !== currentBgSearchId) return;
                
                if (pageBg) {
                    pageBg.style.backgroundImage = `url('${data.url}')`;
                    pageBg.classList.add('has-image');
                }
                if (pageOverlay) {
                    pageOverlay.classList.add('has-image');
                }
                if (discoverThumb) {
                    discoverThumb.src = data.url;
                }
                if (attrBox && attrLink) {
                    attrLink.textContent = data.photographer_name || 'Unsplash Community';
                    attrLink.href = data.photographer_url || 'https://unsplash.com?utm_source=ClimaSense&utm_medium=referral';
                    attrBox.classList.remove('hidden');
                }
            };
            img.onerror = () => {
                if (searchId && searchId !== currentSearchId) return;
                if (bgSearchId !== currentBgSearchId) return;
                console.warn('City background failed to load, maintaining clean light surface');
            };
            img.src = data.url;
        }
    } catch(e) {
        console.error('Error fetching background image:', e);
    }
};

// ============================================================
// 3D Weather Dimensional Visual Generator
// ============================================================
window.update3DWeatherVisual = (condition, desc = '') => {
    const stage = document.getElementById('weather-3d-visual');
    if (!stage) return;

    const cond = (condition || '').toLowerCase();
    const d = (desc || '').toLowerCase();

    let html = '';
    let emoji = '☀️';

    if (cond.includes('thunder') || d.includes('thunder') || d.includes('lightning') || d.includes('storm')) {
        emoji = '⛈️';
        html = `
            <div class="visual-3d-container storm-3d">
                <div class="cloud-cluster-3d">
                    <div class="cloud-puff-3d puff-base storm-dark"></div>
                    <div class="cloud-puff-3d puff-top storm-mid"></div>
                </div>
                <div class="lightning-flash-3d">⚡</div>
                <div class="rain-particle-3d r1"></div>
                <div class="rain-particle-3d r2"></div>
            </div>`;
    } else if (cond.includes('snow') || d.includes('snow') || d.includes('flurr') || d.includes('sleet') || d.includes('ice') || d.includes('blizzard')) {
        emoji = '❄️';
        html = `
            <div class="visual-3d-container snow-3d">
                <div class="cloud-cluster-3d">
                    <div class="cloud-puff-3d puff-base snow-cloud"></div>
                    <div class="cloud-puff-3d puff-top"></div>
                </div>
                <div class="snowflake-particle-3d s1">❄</div>
                <div class="snowflake-particle-3d s2">❅</div>
                <div class="snowflake-particle-3d s3">❆</div>
            </div>`;
    } else if (cond.includes('rain') || cond.includes('drizzle') || d.includes('rain') || d.includes('shower')) {
        emoji = '🌧️';
        html = `
            <div class="visual-3d-container rain-3d">
                <div class="cloud-cluster-3d">
                    <div class="cloud-puff-3d puff-base rain-cloud"></div>
                    <div class="cloud-puff-3d puff-top"></div>
                </div>
                <div class="raindrop-particle-3d d1"></div>
                <div class="raindrop-particle-3d d2"></div>
                <div class="raindrop-particle-3d d3"></div>
            </div>`;
    } else if (cond.includes('cloud') || d.includes('cloud') || d.includes('overcast')) {
        if (d.includes('few') || d.includes('scattered') || d.includes('partly') || d.includes('broken')) {
            emoji = '⛅';
            html = `
                <div class="visual-3d-container partly-cloudy-3d">
                    <div class="sun-orb-3d sun-peeking"></div>
                    <div class="cloud-cluster-3d">
                        <div class="cloud-puff-3d puff-base"></div>
                        <div class="cloud-puff-3d puff-top"></div>
                    </div>
                </div>`;
        } else {
            emoji = '☁️';
            html = `
                <div class="visual-3d-container overcast-3d">
                    <div class="cloud-cluster-3d">
                        <div class="cloud-puff-3d puff-deep"></div>
                        <div class="cloud-puff-3d puff-base"></div>
                        <div class="cloud-puff-3d puff-top"></div>
                    </div>
                </div>`;
        }
    } else if (cond.includes('wind') || d.includes('wind') || d.includes('breeze') || d.includes('gale') || d.includes('squall')) {
        emoji = '💨';
        html = `
            <div class="visual-3d-container wind-3d">
                <div class="wind-stream-3d w1"></div>
                <div class="wind-stream-3d w2"></div>
                <div class="wind-stream-3d w3"></div>
            </div>`;
    } else if (cond.includes('mist') || cond.includes('fog') || cond.includes('haze') || cond.includes('smoke') || cond.includes('dust') || cond.includes('sand')) {
        emoji = '🌫️';
        html = `
            <div class="visual-3d-container fog-3d">
                <div class="mist-bar-3d m1"></div>
                <div class="mist-bar-3d m2"></div>
                <div class="mist-bar-3d m3"></div>
            </div>`;
    } else {
        // Clear sky / sunny default
        emoji = '☀️';
        html = `
            <div class="visual-3d-container sunny-3d">
                <div class="sun-orb-3d sunny-hero"></div>
                <div class="sun-aura-3d"></div>
            </div>`;
    }

    stage.innerHTML = html;

    const condEmojiEl = document.getElementById('weather-condition-emoji');
    if (condEmojiEl) {
        condEmojiEl.textContent = emoji;
    }
};

window.renderWeather = (data, comfortScore, comfortLabel) => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.classList.add('hidden');
    const wrapper = document.getElementById('dashboard-wrapper');
    if (wrapper) wrapper.classList.remove('hidden');
    
    const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = (val !== undefined && val !== null) ? val : '--';
    };
    const setHtml = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = (val !== undefined && val !== null) ? val : '';
    };

    setTxt('city-name', `${data.name}, ${data.sys ? data.sys.country : ''}`);
    
    const descStr = (data.weather && data.weather[0]) ? data.weather[0].description : '';
    const iconCode = (data.weather && data.weather[0]) ? data.weather[0].icon : '01d';
    const tempStr = window.getTempString(data.main ? data.main.temp : null);
    const emoji = window.getWeatherEmoji(descStr, iconCode, data.wind ? data.wind.speed : 0);
    const capDesc = descStr ? descStr.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : '--';
    
    setTxt('city-subtitle', `${emoji} ${capDesc} • ${tempStr}`);
    
    // Calculate and display local time
    const tzSec = data.timezone || 0;
    const utcTime = new Date().getTime() + (new Date().getTimezoneOffset() * 60000);
    const cityTime = new Date(utcTime + (tzSec * 1000));
    const dtOpts = { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    const localTimeStr = cityTime.toLocaleDateString('en-US', dtOpts);
    
    setHtml('city-local-time', `<i class="fa-regular fa-clock"></i> ${localTimeStr} (Local)`);
    
    // Main Temp & Description
    // Trigger 3D Weather Dimensional Visual & Condition Emoji
    const mainCond = (data.weather && data.weather[0]) ? data.weather[0].main : '';
    window.update3DWeatherVisual(mainCond, descStr);
    
    setTxt('temperature', tempStr);
    setTxt('weather-desc', capDesc);
    const iconImg = document.getElementById('weather-icon');
    if (iconImg) iconImg.src = `https://openweathermap.org/img/wn/${iconCode}@4x.png`;
    
    // Feels Like & Min/Max
    if (data.main) {
        setTxt('feels-like-label', 'Feels like ' + window.getTempString(data.main.feels_like));
        setTxt('card-feels-like', window.getTempString(data.main.feels_like));
        if (data.main.temp_min !== undefined && data.main.temp_max !== undefined) {
            setTxt('temp-min-max', `Low: ${window.getTempString(data.main.temp_min)} • High: ${window.getTempString(data.main.temp_max)}`);
        }
        setTxt('humidity', data.main.humidity !== undefined ? data.main.humidity + '%' : '--%');
        setTxt('pressure', data.main.pressure !== undefined ? data.main.pressure + ' hPa' : '-- hPa');
    }
    
    if (data.wind) {
        setTxt('wind-speed', window.getWindString(data.wind.speed));
        if (data.wind.deg !== undefined) {
            const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
            const dirIdx = Math.round(data.wind.deg / 45) % 8;
            setTxt('wind-direction', `(${dirs[dirIdx]} ${data.wind.deg}°)`);
        }
    }
    
    setTxt('visibility', data.visibility !== undefined ? (data.visibility / 1000).toFixed(1) + ' km' : 'Unavailable');
    setTxt('cloud-coverage', (data.clouds && data.clouds.all !== undefined) ? data.clouds.all + '%' : '--%');
    
    // Rain
    const rainVal = data.rain ? (data.rain['1h'] || data.rain['3h'] || 0) : 0;
    setTxt('rain', `${rainVal} mm`);
    
    // Comfort Score KPI
    if (comfortScore !== undefined && comfortScore !== null) {
        setTxt('comfort-score-val', `${comfortScore}/100`);
        setTxt('comfort-score-label', comfortLabel ? `(${comfortLabel})` : '');
    }
    

    
    // Dynamic Hero Greeting
    const hour = cityTime.getHours();
    let greetingPrefix = "Good morning";
    if (hour >= 12 && hour < 17) greetingPrefix = "Good afternoon";
    else if (hour >= 17 && hour < 21) greetingPrefix = "Good evening";
    else if (hour >= 21 || hour < 5) greetingPrefix = "Good night";
    setTxt('hero-greeting', `${greetingPrefix}, ${data.name} ${emoji}`);

    // Update CSV export URLs
    const expHourly = document.getElementById('export-hourly-forecast-csv');
    if (expHourly) expHourly.href = `/api/forecast/${encodeURIComponent(data.name)}/export/hourly/csv`;
    const expWeekly = document.getElementById('export-weekly-forecast-csv');
    if (expWeekly) expWeekly.href = `/api/forecast/${encodeURIComponent(data.name)}/export/weekly/csv`;

    setTxt('fc-city-badge', `📍 ${data.name}, ${data.sys ? data.sys.country : ''}`);

    // Quick Info Card
    setTxt('qi-capital', data.name);
    setTxt('qi-country', data.sys ? data.sys.country : '--');
    if (data.coord) {
        setTxt('info-coords', `${data.coord.lat.toFixed(2)}°, ${data.coord.lon.toFixed(2)}°`);
    }
    const tzH = tzSec / 3600;
    setTxt('qi-timezone', `UTC ${tzH >= 0 ? '+' : ''}${tzH}`);

    // Discover Card Title
    setHtml('discover-city-title', `<i class="fa-solid fa-book-open" style="color: var(--blue-primary);"></i> Discover ${data.name}`);

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
};

window.fetchForecast = async (city) => {
    try {
        const res = await fetch(`/api/forecast/${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data.success) {
            window.currentForecastData = data.forecast;
            window.currentHourlyData = data.hourly;
            window.renderForecast(data.forecast);
            if (data.hourly) window.renderTimeline(data.hourly);
        }
    } catch(e) { console.error('Forecast fetch error:', e); }
};

window.renderForecast = (forecast) => {
    const container = document.getElementById('forecast-container');
    if (!container) return;
    container.innerHTML = '';
    
    const days = (forecast || []).slice(0, 5);
    days.forEach((day, idx) => {
        const dObj = new Date(day.date);
        const dayName = idx === 0 ? 'Today' : dObj.toLocaleDateString('en-US', {weekday: 'short'});
        const dateStr = dObj.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
        const highStr = window.getTempString(day.max_temp !== undefined ? day.max_temp : day.temp);
        const lowStr = window.getTempString(day.min_temp !== undefined ? day.min_temp : day.temp);
        const cond = day.condition || day.description || '';
        const dayEmoji = window.getWeatherEmoji(cond, day.icon, 0);
        
        const tile = document.createElement('div');
        tile.className = 'forecast-day-tile';
        tile.innerHTML = `
            <div class="forecast-tile-header">
                <span class="forecast-tile-day">${dayName}</span>
                <span class="forecast-tile-date">${dateStr}</span>
            </div>
            <div class="forecast-tile-icon-box">
                <img src="https://openweathermap.org/img/wn/${day.icon}@2x.png" alt="${cond}" class="forecast-tile-img" onerror="this.src='https://openweathermap.org/img/wn/${day.icon}.png'">
            </div>
            <div class="forecast-tile-temps">
                <span class="forecast-tile-high">${highStr}</span>
                <span class="forecast-tile-low">${lowStr}</span>
            </div>
            <div class="forecast-tile-cond-badge">
                <span class="forecast-tile-emoji">${dayEmoji}</span>
                <span class="forecast-tile-cond-text">${cond}</span>
            </div>
        `;
        container.appendChild(tile);
    });
};

window.renderTimeline = (hourly) => {
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
    const hbAqi = document.getElementById('hb-aqi');
    if (hbAqi) hbAqi.textContent = 'AQI: Loading...';
    try {
        const res = await fetch(`/api/aqi?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (data.success && data.label) {
            if (hbAqi) {
                hbAqi.textContent = `AQI: ${data.label}`;
            }
        } else {
            if (hbAqi) hbAqi.textContent = 'AQI: Unavailable';
        }
    } catch(e) {
        console.error('AQI fetch error:', e);
        if (hbAqi) hbAqi.textContent = 'AQI: Unavailable';
    }
};

window.fetchUV = async (lat, lon) => {
    try {
        const res = await fetch(`/api/uv?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (data.success) {
            const uvEl = document.getElementById('uv-index');
            if (uvEl) uvEl.textContent = `${data.uvi} (${data.category})`;
        }
    } catch(e) { console.error('UV fetch error:', e); }
};

window.fetchAlerts = async (lat, lon) => {
    try {
        const res = await fetch(`/api/alerts?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        const banner = document.getElementById('alert-banner');
        if (banner) {
            if (data.success && data.alert) {
                banner.textContent = `⚠️ ${data.alert.title}: ${data.alert.description}`;
                banner.className = 'alert-banner severe';
                banner.classList.remove('hidden');
            } else {
                banner.classList.add('hidden');
            }
        }
    } catch(e) { console.error('Alerts fetch error:', e); }
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
            timeEl.textContent = 'Grounded Observation';
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
    const openAssistantBtn = document.getElementById('open-assistant-btn');
    const chatPanel = document.getElementById('chat-panel');
    const closeBtn = document.getElementById('close-chat-btn');
    const sendBtn = document.getElementById('chat-send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const chips = document.querySelectorAll('.chat-chip');
    
    if (!chatPanel) return;
    
    let chatHistory = [];
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            chatPanel.classList.toggle('hidden');
            if (!chatPanel.classList.contains('hidden') && chatInput) {
                chatInput.focus();
            }
        });
    }

    if (openAssistantBtn) {
        openAssistantBtn.addEventListener('click', (e) => {
            e.preventDefault();
            chatPanel.classList.remove('hidden');
            if (chatInput) chatInput.focus();
        });
    }

    if (window.location.hash === '#chat-panel') {
        chatPanel.classList.remove('hidden');
        if (chatInput) chatInput.focus();
    }
    window.addEventListener('hashchange', () => {
        if (window.location.hash === '#chat-panel') {
            chatPanel.classList.remove('hidden');
            if (chatInput) chatInput.focus();
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
        
        const userBubble = document.createElement('div');
        userBubble.className = 'chat-bubble user';
        userBubble.textContent = text;
        chatBody.appendChild(userBubble);
        chatInput.value = '';
        
        // Record in conversation history (max 6 turns)
        chatHistory.push({ role: 'user', content: text });
        if (chatHistory.length > 6) chatHistory = chatHistory.slice(-6);
        
        const aiBubble = document.createElement('div');
        aiBubble.className = 'chat-bubble ai';
        aiBubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consulting weather context...';
        chatBody.appendChild(aiBubble);
        chatBody.scrollTop = chatBody.scrollHeight;
        
        const activeCity = window.currentWeatherData ? window.currentWeatherData.name : (localStorage.getItem('lastCity') || 'London');
        
        try {
            const res = await fetch('/api/weather/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: text, city: activeCity, history: chatHistory })
            });
            const data = await res.json();
            if (data.success && data.answer) {
                const isGemini = data.is_ai_generated && data.provider === 'Google Gemini';
                const tagIcon = isGemini ? 'fa-brain' : 'fa-shield-halved';
                const tagText = isGemini ? 'Google Gemini' : 'Smart Rules Fallback';
                const tagBg = isGemini ? 'var(--lavender-pale)' : 'var(--blue-pale)';
                const tagColor = isGemini ? 'var(--lavender-accent)' : 'var(--blue-primary)';
                
                aiBubble.innerHTML = `
                    <div style="margin-bottom: 6px;">
                        <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; background: ${tagBg}; color: ${tagColor}; font-weight: 700; border: 1px solid var(--border-subtle); display: inline-flex; align-items: center; gap: 4px;">
                            <i class="fa-solid ${tagIcon}"></i> ${tagText}
                        </span>
                    </div>
                    <div style="line-height: 1.6;">${data.answer.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                `;
                chatHistory.push({ role: 'assistant', content: data.answer });
                if (chatHistory.length > 6) chatHistory = chatHistory.slice(-6);
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
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleChatSend();
            }
        });
    }
};

window.fetchCityEncyclopedia = async (city, country = '') => {
    const infoName = document.getElementById('city-info-name') || document.getElementById('city-info-title');
    const infoSummary = document.getElementById('city-info-summary');
    const infoReadMore = document.getElementById('city-info-read-more');
    const discoverNarrative = document.getElementById('discover-city-narrative');
    const discoverTitle = document.getElementById('discover-city-title');

    if (infoName) infoName.textContent = `About ${city}`;
    if (infoSummary) infoSummary.textContent = `Loading Wikipedia overview for ${city}...`;

    try {
        let url = `/api/encyclopedia/${encodeURIComponent(city)}`;
        if (country) {
            url += `?country=${encodeURIComponent(country)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        
        const info = data.info || (data.article ? {
            title: data.article.title || city,
            summary: data.article.summary || data.article.lead_paragraph || '',
            article_url: data.article.article_url || `https://en.wikipedia.org/wiki/${encodeURIComponent(city)}`,
            is_available: data.article.is_available !== false
        } : null);

        if (info && info.summary) {
            if (infoName) infoName.textContent = info.title || city;
            if (infoSummary) infoSummary.textContent = info.summary;
            if (infoReadMore && info.article_url) {
                infoReadMore.href = info.article_url;
            }
            if (discoverNarrative) {
                discoverNarrative.textContent = info.summary;
            }
            if (discoverTitle) {
                discoverTitle.innerHTML = `<i class="fa-solid fa-book-open" style="color: var(--blue-primary);"></i> ${info.title || city}`;
            }
        } else {
            if (infoSummary) {
                infoSummary.textContent = `Detailed Wikipedia summary for ${city} is currently unavailable.`;
            }
            if (infoReadMore) {
                infoReadMore.href = `https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(city)}`;
            }
        }
    } catch (e) {
        console.error('Error fetching city info:', e);
        if (infoSummary) {
            infoSummary.textContent = `Could not retrieve Wikipedia overview for ${city} at this time.`;
        }
    }
};

window.fetchSavedCities = async () => {
    const shelf = document.getElementById('saved-cities-shelf');
    const container = document.getElementById('saved-cities-container');
    if (!shelf) return;
    
    try {
        const res = await fetch('/api/cities/saved');
        const data = await res.json();
        if (data.success && data.cities && data.cities.length > 0) {
            if (container) container.classList.remove('hidden');
            shelf.innerHTML = '';
            data.cities.forEach(c => {
                const card = document.createElement('div');
                card.className = 'saved-city-card';
                card.innerHTML = `
                    <button class="remove-btn" title="Remove city" onclick="window.unsaveCity(event, '${c.city}')"><i class="fa-solid fa-xmark"></i></button>
                    <strong>${c.city}</strong>
                `;
                card.onclick = () => {
                    const cityInput = document.getElementById('city-input');
                    if (cityInput) cityInput.value = c.city;
                    fetchWeather(c.city);
                };
                shelf.appendChild(card);
            });
        } else {
            if (container) container.classList.add('hidden');
        }
    } catch(e) { console.error('Saved cities error:', e); }
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
        if (result.success) {
            window.showToast(`${city} removed.`);
            window.fetchSavedCities();
        }
    } catch(err) { console.error(err); }
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
    toast.innerHTML = `<i class="fa-solid fa-circle-info" style="color: var(--blue-primary); margin-right: 8px;"></i> ${message}`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

window.fetchSystemStatus = async () => {
    const grid = document.getElementById('status-cards-grid');
    if (!grid) return;
    grid.innerHTML = '<div style="grid-column: span 2; text-align: center; padding: 2rem;">Loading System Diagnostics...</div>';
    try {
        const res = await fetch('/api/system-status');
        const data = await res.json();
        if (data.success && data.status) {
            grid.innerHTML = '';
            Object.values(data.status).forEach(srv => {
                const card = document.createElement('div');
                card.className = 'status-card';
                card.innerHTML = `
                    <div class="status-card-header">
                        <span>${srv.name}</span>
                        <span class="status-badge ${srv.status === 'Online' ? 'status-online' : 'status-degraded'}">${srv.status}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #64788b;">${srv.database || srv.ttl || 'Operational'}</div>
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
