document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('theme-toggle');
    const unitBtn = document.getElementById('unit-toggle');
    
    // Theme logic
    const currentTheme = localStorage.getItem('theme') || 'dark';
    if (currentTheme === 'light') {
        document.body.classList.replace('dark-theme', 'light-theme');
        if(themeBtn) themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    } else {
        document.body.classList.replace('light-theme', 'dark-theme');
        if(themeBtn) themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }
    
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            if (document.body.classList.contains('dark-theme')) {
                document.body.classList.replace('dark-theme', 'light-theme');
                localStorage.setItem('theme', 'light');
                themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
            } else {
                document.body.classList.replace('light-theme', 'dark-theme');
                localStorage.setItem('theme', 'dark');
                themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
            }
        });
    }

    // Unit toggle logic
    let isMetric = localStorage.getItem('unit') !== 'imperial';
    
    const updateUnitBtnText = () => {
        if(unitBtn) unitBtn.textContent = isMetric ? '°C' : '°F';
    }
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
    
    // Helper function for converting temp based on preference
    window.getTempString = (tempCelsius) => {
        const metric = localStorage.getItem('unit') !== 'imperial';
        if (metric) {
            return Math.round(tempCelsius) + '°C';
        } else {
            const fahrenheit = (tempCelsius * 9/5) + 32;
            return Math.round(fahrenheit) + '°F';
        }
    };
});
