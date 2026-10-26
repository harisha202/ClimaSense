let mapInstance = null;
window.mapInstance = null;

window.initMap = (lat, lon, cityName) => {
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return;
    
    mapDiv.classList.remove('hidden');
    
    // Update map section title & coordinates badge
    const titleEl = document.getElementById('map-section-title');
    if (titleEl && cityName) {
        titleEl.textContent = `${cityName} Radar & Geographical Map`;
    }
    const coordsBadge = document.getElementById('map-coords-badge');
    if (coordsBadge && typeof lat === 'number' && typeof lon === 'number') {
        coordsBadge.textContent = `📍 ${lat.toFixed(2)}°, ${lon.toFixed(2)}°`;
    }
    
    if (mapInstance) {
        mapInstance.remove(); // Leaflet throws error if initializing on already initialized container
        mapInstance = null;
    }
    
    mapInstance = L.map('map', { attributionControl: false, scrollWheelZoom: false }).setView([lat, lon], 11);
    window.mapInstance = mapInstance;
    
    // Base layer
    const baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: ''
    });
    
    // Weather layers (using backend proxy to hide API key)
    const clouds = L.tileLayer('/api/tiles/clouds_new/{z}/{x}/{y}.png', { opacity: 0.8 });
    const precipitation = L.tileLayer('/api/tiles/precipitation_new/{z}/{x}/{y}.png', { opacity: 0.8 });
    const temp = L.tileLayer('/api/tiles/temp_new/{z}/{x}/{y}.png', { opacity: 0.6 });
    const wind = L.tileLayer('/api/tiles/wind_new/{z}/{x}/{y}.png', { opacity: 0.6 });
    
    baseLayer.addTo(mapInstance);
    
    const overlayMaps = {
        "Clouds": clouds,
        "Precipitation (Rain)": precipitation,
        "Temperature": temp,
        "Wind Speed": wind
    };
    
    L.control.layers({"Base Map": baseLayer}, overlayMaps).addTo(mapInstance);
    
    // Default add precipitation
    precipitation.addTo(mapInstance);
    
    L.marker([lat, lon]).addTo(mapInstance)
        .bindPopup(`<b>${cityName}</b><br><span style="font-size:0.8rem; color:#64748B;">Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}</span>`)
        .openPopup();
        
    // Invalidate size after delay to ensure crisp canvas rendering
    setTimeout(() => {
        if (mapInstance) mapInstance.invalidateSize();
    }, 250);
};
