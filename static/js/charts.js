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

    loadBtn.addEventListener('click', async () => {
        primaryCityName = document.getElementById('trend-city').value;
        secondaryCityName = document.getElementById('compare-city').value;
        const range = document.getElementById('trend-range').value;
        
        if(!primaryCityName) return;
        
        try {
            // Fetch Primary City
            const res1 = await fetch(`/api/trends/${encodeURIComponent(primaryCityName)}?range=${range}`);
            const data1 = await res1.json();
            if(data1.success) currentDataPrimary = data1.data;
            
            // Fetch Secondary City if provided
            if (secondaryCityName) {
                const res2 = await fetch(`/api/trends/${encodeURIComponent(secondaryCityName)}?range=${range}`);
                const data2 = await res2.json();
                if(data2.success) currentDataSecondary = data2.data;
            } else {
                currentDataSecondary = [];
            }
            
            renderChart();
        } catch(e) {
            console.error('Error loading trends', e);
        }
    });

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

        const ctx = document.getElementById('trend-canvas').getContext('2d');
        
        const primaryGrouped = processData(currentDataPrimary);
        const secondaryGrouped = processData(currentDataSecondary);
        
        // Merge labels from both datasets to ensure x-axis alignment
        const labelSet = new Set([...Object.keys(primaryGrouped), ...Object.keys(secondaryGrouped)]);
        // Sort dates chronologically (assuming DD MMM format, we might just sort as strings for simplicity if they are within a month, but better to just use the order from the array or sort by actual date)
        const labels = Array.from(labelSet).sort((a,b) => new Date(a + " " + new Date().getFullYear()) - new Date(b + " " + new Date().getFullYear()));
        
        const emptyState = document.getElementById('trend-empty-state');
        const canvas = document.getElementById('trend-canvas');
        
        if (labels.length < 2) {
            if (emptyState) emptyState.classList.remove('hidden');
            if (canvas) canvas.classList.add('hidden');
            return;
        } else {
            if (emptyState) emptyState.classList.add('hidden');
            if (canvas) canvas.classList.remove('hidden');
        }

        const primaryDataPoints = labels.map(label => primaryGrouped[label] !== undefined ? primaryGrouped[label] : null);
        
        const datasets = [{
            label: `${primaryCityName} - ${currentMetric.replace('_', ' ').toUpperCase()}`,
            data: primaryDataPoints,
            borderColor: '#ffcc00',
            backgroundColor: 'rgba(255, 204, 0, 0.2)',
            tension: 0.3,
            fill: true
        }];

        if (secondaryCityName && currentDataSecondary.length > 0) {
            const secondaryDataPoints = labels.map(label => secondaryGrouped[label] !== undefined ? secondaryGrouped[label] : null);
            datasets.push({
                label: `${secondaryCityName} - ${currentMetric.replace('_', ' ').toUpperCase()}`,
                data: secondaryDataPoints,
                borderColor: '#00ccff',
                backgroundColor: 'rgba(0, 204, 255, 0.2)',
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
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#adb5bd' }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#adb5bd' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8f9fa' } }
                }
            }
        });
    }
});
