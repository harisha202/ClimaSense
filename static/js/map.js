let mapInstance = null;

window.initMap = (lat, lon, cityName) => {
    const mapDiv = document.getElementById('map');
    if(!mapDiv) return;
    
    mapDiv.classList.remove('hidden');
    
    if (mapInstance) {
        mapInstance.remove(); // Leaflet throws error if initializing on already initialized container
    }
    
    mapInstance = L.map('map', { attributionControl: false }).setView([lat, lon], 10);
    
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
        .bindPopup(`<b>${cityName}</b>`)
        .openPopup();
        
    // Invalidate size after a short delay because container might be animating/resizing
    setTimeout(() => {
        mapInstance.invalidateSize();
    }, 200);
};
