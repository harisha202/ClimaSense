/**
 * ClimaSense - 3D Weather Visualization Engine & Centralized Emoji System
 * Layered CSS 3D cloud rendering, particle physics, and weather-responsive ambiance.
 * Strict boundary: All 3D atmospheric effects are contained within #weather-3d-scene.
 */

// Centralized Weather Emoji & Condition System
window.WEATHER_EMOJI_MAP = {
    // Standard condition codes / icon IDs
    '01d': { emoji: '☀️', name: 'Sunny / Clear Day', mood: 'sunny' },
    '01n': { emoji: '🌙', name: 'Clear Night', mood: 'night-clear' },
    '02d': { emoji: '⛅', name: 'Partly Cloudy Day', mood: 'partly-cloudy' },
    '02n': { emoji: '☁️', name: 'Partly Cloudy Night', mood: 'night-cloudy' },
    '03d': { emoji: '☁️', name: 'Scattered Clouds', mood: 'cloudy' },
    '03n': { emoji: '☁️', name: 'Scattered Clouds', mood: 'night-cloudy' },
    '04d': { emoji: '☁️', name: 'Overcast Clouds', mood: 'overcast' },
    '04n': { emoji: '☁️', name: 'Overcast Clouds', mood: 'overcast' },
    '09d': { emoji: '🌧️', name: 'Showers / Heavy Rain', mood: 'rain' },
    '09n': { emoji: '🌧️', name: 'Night Showers', mood: 'rain-night' },
    '10d': { emoji: '🌦️', name: 'Light Rain / Sun Showers', mood: 'light-rain' },
    '10n': { emoji: '🌧️', name: 'Night Rain', mood: 'rain-night' },
    '11d': { emoji: '⛈️', name: 'Thunderstorm', mood: 'thunderstorm' },
    '11n': { emoji: '⛈️', name: 'Night Thunderstorm', mood: 'thunderstorm' },
    '13d': { emoji: '❄️', name: 'Snow', mood: 'snow' },
    '13n': { emoji: '❄️', name: 'Night Snow', mood: 'snow' },
    '50d': { emoji: '🌫️', name: 'Mist / Fog / Haze', mood: 'fog' },
    '50n': { emoji: '🌫️', name: 'Night Fog', mood: 'fog' },
    // Fallback names
    'Clear': { emoji: '☀️', name: 'Clear', mood: 'sunny' },
    'Clouds': { emoji: '⛅', name: 'Clouds', mood: 'cloudy' },
    'Rain': { emoji: '🌧️', name: 'Rain', mood: 'rain' },
    'Drizzle': { emoji: '🌦️', name: 'Drizzle', mood: 'light-rain' },
    'Thunderstorm': { emoji: '⛈️', name: 'Thunderstorm', mood: 'thunderstorm' },
    'Snow': { emoji: '❄️', name: 'Snow', mood: 'snow' },
    'Mist': { emoji: '🌫️', name: 'Mist', mood: 'fog' },
    'Fog': { emoji: '🌫️', name: 'Fog', mood: 'fog' },
    'Haze': { emoji: '🌫️', name: 'Haze', mood: 'fog' },
    'Smoke': { emoji: '🌫️', name: 'Smoke', mood: 'fog' },
    'Dust': { emoji: '🌪️', name: 'Dust', mood: 'fog' },
    'Tornado': { emoji: '🌪️', name: 'Tornado', mood: 'thunderstorm' }
};

window.getWeatherEmoji = function(codeOrMain, isNight) {
    if (!codeOrMain) return '🌤️';
    if (window.WEATHER_EMOJI_MAP[codeOrMain]) {
        return window.WEATHER_EMOJI_MAP[codeOrMain].emoji;
    }
    const key = isNight ? `${codeOrMain}n` : `${codeOrMain}d`;
    if (window.WEATHER_EMOJI_MAP[key]) {
        return window.WEATHER_EMOJI_MAP[key].emoji;
    }
    return window.WEATHER_EMOJI_MAP[codeOrMain]?.emoji || '🌤️';
};

class Weather3DScene {
    constructor(containerId = 'weather-3d-scene') {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.tiltContainer = this.container.querySelector('.scene-3d-viewport');
        this.currentMood = 'sunny';
        this.isNight = false;
        this.particles = [];
        this.init();
    }

    init() {
        if (!this.container) return;
        
        // Mouse tilt listener for 3D parallax
        this.container.addEventListener('mousemove', (e) => {
            const rect = this.container.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            if (this.tiltContainer) {
                this.tiltContainer.style.transform = `rotateX(${-y * 14}deg) rotateY(${x * 18}deg)`;
            }
        });

        this.container.addEventListener('mouseleave', () => {
            if (this.tiltContainer) {
                this.tiltContainer.style.transform = 'rotateX(0deg) rotateY(0deg)';
                this.tiltContainer.style.transition = 'transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
            }
        });

        this.container.addEventListener('mouseenter', () => {
            if (this.tiltContainer) {
                this.tiltContainer.style.transition = 'transform 0.1s ease-out';
            }
        });

        // Initialize with default clear sky
        this.updateScene('01d', 'Clear', 'clear sky');
    }

    updateScene(iconCode, mainWeather, description) {
        if (!this.container) return;
        
        const isNight = iconCode ? iconCode.endsWith('n') : false;
        this.isNight = isNight;
        
        let mood = 'sunny';
        if (window.WEATHER_EMOJI_MAP[iconCode]) {
            mood = window.WEATHER_EMOJI_MAP[iconCode].mood;
        } else if (window.WEATHER_EMOJI_MAP[mainWeather]) {
            mood = window.WEATHER_EMOJI_MAP[mainWeather].mood;
        }

        this.currentMood = mood;
        this.renderAtmosphere(mood, isNight, description);
    }

    renderAtmosphere(mood, isNight, description) {
        if (!this.container) return;
        
        // Build interior 3D DOM structure
        const skyClass = isNight ? 'sky-night' : 'sky-day';
        const moodClass = `mood-${mood}`;
        
        this.container.className = `weather-3d-container ${skyClass} ${moodClass}`;
        
        let celestialHtml = '';
        if (isNight) {
            celestialHtml = `
                <div class="celestial-body moon-3d">
                    <div class="moon-crescent"></div>
                    <div class="moon-glow"></div>
                </div>
                <div class="star-field">
                    ${this.generateStars(28)}
                </div>
            `;
        } else {
            celestialHtml = `
                <div class="celestial-body sun-3d">
                    <div class="sun-core"></div>
                    <div class="sun-flare flare-1"></div>
                    <div class="sun-flare flare-2"></div>
                    <div class="sun-rays"></div>
                </div>
            `;
        }

        // Layered 3D Clouds (Background, Midground, Foreground with parallax z-indices)
        const cloudDensity = (mood.includes('overcast') || mood.includes('thunder')) ? 3 :
                             (mood.includes('cloud') || mood.includes('rain')) ? 2 : 1;
        
        const cloudsHtml = this.generateLayeredClouds(cloudDensity, isNight, mood);
        const particlesHtml = this.generateParticles(mood);

        this.container.innerHTML = `
            <div class="scene-3d-viewport">
                <div class="atmosphere-gradient"></div>
                ${celestialHtml}
                ${cloudsHtml}
                ${particlesHtml}
                <div class="scene-overlay-readout">
                    <span class="scene-pill scene-badge">
                        <i class="fa-solid fa-cube"></i> 3D Atmospheric Simulation
                    </span>
                    <span class="scene-pill scene-condition">
                        ${this.isNight ? '🌙' : '☀️'} ${description ? description.toUpperCase() : 'CLEAR SKY'}
                    </span>
                </div>
            </div>
        `;

        this.tiltContainer = this.container.querySelector('.scene-3d-viewport');
    }

    generateStars(count) {
        let stars = '';
        for (let i = 0; i < count; i++) {
            const top = (Math.random() * 85).toFixed(1);
            const left = (Math.random() * 95).toFixed(1);
            const size = (Math.random() * 2.5 + 1.2).toFixed(1);
            const delay = (Math.random() * 3).toFixed(1);
            const duration = (Math.random() * 2 + 1.5).toFixed(1);
            stars += `<div class="star-particle" style="top:${top}%; left:${left}%; width:${size}px; height:${size}px; animation-delay:${delay}s; animation-duration:${duration}s;"></div>`;
        }
        return stars;
    }

    generateLayeredClouds(density, isNight, mood) {
        if (density === 0 && !mood.includes('cloud')) {
            // Subtle wisps for clear sky
            return `
                <div class="clouds-3d-stage">
                    <div class="cloud-layer layer-back wisp-drift">
                        <div class="cloud-shape wisp-1"></div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="clouds-3d-stage">
                <!-- Layer 1: Background distant slow drift -->
                <div class="cloud-layer layer-deep">
                    <div class="cloud-cluster cluster-back-1">
                        <div class="cloud-puff puff-lg"></div>
                        <div class="cloud-puff puff-md"></div>
                        <div class="cloud-puff puff-sm"></div>
                    </div>
                    <div class="cloud-cluster cluster-back-2">
                        <div class="cloud-puff puff-md"></div>
                        <div class="cloud-puff puff-lg"></div>
                    </div>
                </div>

                <!-- Layer 2: Midground floating cumulus -->
                <div class="cloud-layer layer-mid">
                    <div class="cloud-cluster cluster-mid-1">
                        <div class="cloud-puff puff-xl"></div>
                        <div class="cloud-puff puff-lg"></div>
                        <div class="cloud-puff puff-md"></div>
                    </div>
                    ${density >= 2 ? `
                    <div class="cloud-cluster cluster-mid-2">
                        <div class="cloud-puff puff-lg"></div>
                        <div class="cloud-puff puff-md"></div>
                    </div>` : ''}
                </div>

                <!-- Layer 3: Foreground close fast drift -->
                <div class="cloud-layer layer-front">
                    <div class="cloud-cluster cluster-front-1">
                        <div class="cloud-puff puff-hero"></div>
                        <div class="cloud-puff puff-lg"></div>
                    </div>
                    ${density >= 3 ? `
                    <div class="cloud-cluster cluster-front-2 storm-tint">
                        <div class="cloud-puff puff-xl"></div>
                        <div class="cloud-puff puff-lg"></div>
                    </div>` : ''}
                </div>
            </div>
        `;
    }

    generateParticles(mood) {
        if (mood.includes('rain')) {
            let drops = '';
            const dropCount = mood.includes('light') ? 24 : 50;
            for (let i = 0; i < dropCount; i++) {
                const left = (Math.random() * 100).toFixed(1);
                const delay = (Math.random() * 1.5).toFixed(2);
                const duration = (Math.random() * 0.4 + 0.45).toFixed(2);
                drops += `<div class="rain-drop" style="left:${left}%; animation-delay:${delay}s; animation-duration:${duration}s;"></div>`;
            }
            return `<div class="particle-container rain-container">${drops}</div>`;
        }

        if (mood.includes('snow')) {
            let flakes = '';
            for (let i = 0; i < 35; i++) {
                const left = (Math.random() * 100).toFixed(1);
                const delay = (Math.random() * 3).toFixed(2);
                const duration = (Math.random() * 2.5 + 2.5).toFixed(2);
                const size = (Math.random() * 5 + 3).toFixed(1);
                flakes += `<div class="snow-flake" style="left:${left}%; width:${size}px; height:${size}px; animation-delay:${delay}s; animation-duration:${duration}s;">❄</div>`;
            }
            return `<div class="particle-container snow-container">${flakes}</div>`;
        }

        if (mood.includes('fog')) {
            return `
                <div class="particle-container fog-container">
                    <div class="fog-sheet fog-1"></div>
                    <div class="fog-sheet fog-2"></div>
                </div>
            `;
        }

        if (mood.includes('thunder')) {
            let drops = '';
            for (let i = 0; i < 60; i++) {
                const left = (Math.random() * 100).toFixed(1);
                const delay = (Math.random() * 1.2).toFixed(2);
                const duration = (Math.random() * 0.35 + 0.35).toFixed(2);
                drops += `<div class="rain-drop heavy-rain" style="left:${left}%; animation-delay:${delay}s; animation-duration:${duration}s;"></div>`;
            }
            return `
                <div class="particle-container thunder-container">
                    <div class="lightning-flash"></div>
                    ${drops}
                </div>
            `;
        }

        return '';
    }
}

// Global initialization
window.Weather3D = null;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('weather-3d-scene')) {
        window.Weather3D = new Weather3DScene('weather-3d-scene');
    }
});
