let mapInstance = null;

window.initMap = (lat, lon, cityName) => {
    const mapDiv = document.getElementById('map');
    if(!mapDiv) return;
    
    mapDiv.classList.remove('hidden');
    
    if (mapInstance) {
        mapInstance.remove(); // Leaflet throws error if initializing on already initialized container
    }
    
    mapInstance = L.map('map', { attributionControl: false }).setView([lat, lon], 10);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: ''
    }).addTo(mapInstance);
    
    L.marker([lat, lon]).addTo(mapInstance)
        .bindPopup(`<b>${cityName}</b>`)
        .openPopup();
        
    // Invalidate size after a short delay because container might be animating/resizing
    setTimeout(() => {
        mapInstance.invalidateSize();
    }, 200);
};
