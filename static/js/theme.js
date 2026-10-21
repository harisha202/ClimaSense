// ClimaSense - Light Theme & Unit Preferences
// Strict Light Mode Policy: Pure light theme across entire application
document.addEventListener('DOMContentLoaded', () => {
    // Enforce light theme globally
    localStorage.setItem('theme', 'light');
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
    
    // Hide theme toggle button if present since app is permanently light-themed
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.style.display = 'none';
    }

    // Unit toggle logic (°C / °F)
    const unitBtn = document.getElementById('unit-toggle');
    let isMetric = localStorage.getItem('unit') !== 'imperial';
    
    const updateUnitBtnText = () => {
        if (unitBtn) unitBtn.textContent = isMetric ? '°C' : '°F';
    };
    updateUnitBtnText();
    
    if (unitBtn) {
        unitBtn.addEventListener('click', () => {
            isMetric = !isMetric;
            localStorage.setItem('unit', isMetric ? 'metric' : 'imperial');
            updateUnitBtnText();
            // Dispatch event for other scripts
            window.dispatchEvent(new Event('unitChanged'));
        });
    }
    
    // Global helper function for converting temp based on preference
    window.getTempString = (tempCelsius) => {
        const metric = localStorage.getItem('unit') !== 'imperial';
        if (metric) {
            return `${Math.round(tempCelsius)}°C`;
        } else {
            const fahrenheit = (tempCelsius * 9/5) + 32;
            return `${Math.round(fahrenheit)}°F`;
        }
    };
});
