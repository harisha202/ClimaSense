let trendChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const loadBtn = document.getElementById('load-trend-btn');
    const tabs = document.querySelectorAll('.chart-tabs .theme-toggle-btn');
    let currentMetric = 'temperature';
    let currentDataPrimary = [];
    let currentDataSecondary = [];
    let primaryCityName = '';
    let secondaryCityName = '';

    if(!loadBtn) return;

    const executeLoad = async () => {
        primaryCityName = (document.getElementById('trend-city').value || 'London').trim();
        secondaryCityName = (document.getElementById('compare-city').value || '').trim();
        const range = document.getElementById('trend-range').value;
        
        if(!primaryCityName) return;
        
        try {
            // Fetch Primary City
            const res1 = await fetch(`/api/trends/${encodeURIComponent(primaryCityName)}?range=${range}`);
            const data1 = await res1.json();
            currentDataPrimary = data1.success ? data1.data : [];
            
            // Fetch Secondary City if provided
            if (secondaryCityName) {
                const res2 = await fetch(`/api/trends/${encodeURIComponent(secondaryCityName)}?range=${range}`);
                const data2 = await res2.json();
                currentDataSecondary = data2.success ? data2.data : [];
            } else {
                currentDataSecondary = [];
            }
            
            renderChart();
        } catch(e) {
            console.error('Error loading trends', e);
            currentDataPrimary = [];
            currentDataSecondary = [];
            renderChart();
        }
    };

    loadBtn.addEventListener('click', executeLoad);
    
    // Auto load default city
    executeLoad();

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            tabs.forEach(t => {
                t.classList.remove('active');
                t.style.borderBottom = 'none';
            });
            e.target.classList.add('active');
            e.target.style.borderBottom = '2px solid var(--accent)';
            currentMetric = e.target.getAttribute('data-metric');
            if(currentDataPrimary.length > 0) renderChart();
        });
    });

    function processData(dataArray) {
        const grouped = {};
        dataArray.forEach(log => {
            const date = new Date(log.recorded_at).toLocaleDateString('en-GB', {day: 'numeric', month: 'short'});
            if(!grouped[date]) grouped[date] = [];
            grouped[date].push(log[currentMetric]);
        });
        
        const result = {};
        for (const [date, vals] of Object.entries(grouped)) {
            result[date] = vals.reduce((a,b)=>a+b, 0) / vals.length;
        }
        return result;
    }

    function renderChart() {
        if (trendChart) {
            trendChart.destroy();
        }

        const primaryGrouped = processData(currentDataPrimary);
        const secondaryGrouped = processData(currentDataSecondary);
        
        const labelSet = new Set([...Object.keys(primaryGrouped), ...Object.keys(secondaryGrouped)]);
        const labels = Array.from(labelSet).sort((a,b) => new Date(a + " " + new Date().getFullYear()) - new Date(b + " " + new Date().getFullYear()));
        
        const emptyState = document.getElementById('trend-empty-state');
        const canvas = document.getElementById('trend-canvas');
        
        if (labels.length < 1) {
            if (emptyState) emptyState.classList.remove('hidden');
            if (canvas) canvas.classList.add('hidden');
            return;
        } else {
            if (emptyState) emptyState.classList.add('hidden');
            if (canvas) canvas.classList.remove('hidden');
        }

        const ctx = canvas.getContext('2d');
        const isDark = document.body.classList.contains('dark-theme');
        const textColor = isDark ? '#adb5bd' : '#475569';
        const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';

        // Unit adjustment
        const isImperial = localStorage.getItem('tempUnit') === 'F';
        const adjustValue = (val) => {
            if (val === null || val === undefined) return null;
            if (currentMetric === 'temperature' && isImperial) {
                return (val * 9/5) + 32;
            }
            return val;
        };

        const primaryDataPoints = labels.map(label => {
            const v = primaryGrouped[label];
            return v !== undefined ? adjustValue(v) : null;
        });
        
        let unitLabel = '°C';
        if (currentMetric === 'temperature' && isImperial) unitLabel = '°F';
        else if (currentMetric === 'humidity') unitLabel = '%';
        else if (currentMetric === 'wind_speed') unitLabel = ' m/s';
        else if (currentMetric === 'pressure') unitLabel = ' hPa';

        const datasets = [{
            label: `${primaryCityName} - ${currentMetric.replace('_', ' ').toUpperCase()} (${unitLabel})`,
            data: primaryDataPoints,
            borderColor: '#ffb703',
            backgroundColor: 'rgba(255, 183, 3, 0.18)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
        }];

        if (secondaryCityName && currentDataSecondary.length > 0) {
            const secondaryDataPoints = labels.map(label => {
                const v = secondaryGrouped[label];
                return v !== undefined ? adjustValue(v) : null;
            });
            datasets.push({
                label: `${secondaryCityName} - ${currentMetric.replace('_', ' ').toUpperCase()} (${unitLabel})`,
                data: secondaryDataPoints,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.18)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            });
        }

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    }
                },
                plugins: {
                    legend: { labels: { color: textColor, font: { weight: '600' } } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(1) + unitLabel;
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
});
