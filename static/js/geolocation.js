document.addEventListener('DOMContentLoaded', () => {
    const geoBtn = document.getElementById('geo-btn');
    if (!geoBtn) return;
    
    geoBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            return;
        }
        
        // Show loading state
        document.getElementById('loading-spinner').classList.remove('hidden');
        document.getElementById('weather-card').classList.add('hidden');
        document.getElementById('forecast-container').classList.add('hidden');
        document.getElementById('map').classList.add('hidden');
        
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                try {
                    const res = await fetch(`/api/weather/geo?lat=${lat}&lon=${lon}`);
                    const data = await res.json();
                    
                    if (data.success && window.renderWeather) {
                        // Pass to script.js to render
                        window.renderWeather(data.data);
                        
                        // Also trigger forecast and AQI using the resolved city name or coords
                        if (window.fetchForecast) window.fetchForecast(data.data.name);
                        if (window.fetchAQI) window.fetchAQI(lat, lon);
                        if (window.fetchAlerts) window.fetchAlerts(lat, lon);
                    } else {
                        alert(data.message || 'Error fetching weather for location');
                        document.getElementById('loading-spinner').classList.add('hidden');
                    }
                } catch(e) {
                    console.error('Geo weather error', e);
                    document.getElementById('loading-spinner').classList.add('hidden');
                }
            },
            (error) => {
                console.error('Geolocation error', error);
                alert('Unable to retrieve your location');
                document.getElementById('loading-spinner').classList.add('hidden');
            }
        );
    });
});
