const socket = io();

let currentRoom = null;
let notifCount = 0;

document.addEventListener('DOMContentLoaded', () => {
    socket.on('connect', () => {
        console.log('Connected to real-time alerts server');
    });

    socket.on('weather_alert', (data) => {
        console.log('Received live alert:', data);
        showToast(data.title, data.description, data.city);
        addNotification(data.title, data.description, data.city);
    });
});

window.joinCityRoom = (city) => {
    if (currentRoom) {
        socket.emit('leave_city', {city: currentRoom});
    }
    currentRoom = city;
    socket.emit('join_city', {city: currentRoom});
    console.log(`Joined real-time alerts room for ${city}`);
};

function showToast(title, desc, city) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast glass';
    toast.innerHTML = `
        <strong>⚠️ ${title} (${city})</strong>
        <p style="margin-top: 5px; font-size: 0.9rem;">${desc}</p>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 6 seconds
    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s ease-in reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 6000);
}

function addNotification(title, desc, city) {
    const list = document.getElementById('notif-list');
    const badge = document.getElementById('notif-badge');
    
    // Remove empty state
    const emptyMsg = document.querySelector('.notif-empty');
    if (emptyMsg) emptyMsg.remove();
    
    // Add to list
    const li = document.createElement('li');
    li.innerHTML = `
        <div style="font-weight:bold; color:var(--danger)">⚠️ ${title}</div>
        <div style="font-size:0.85rem; color:var(--text-secondary)">${city} - ${desc}</div>
    `;
    list.insertBefore(li, list.firstChild);
    
    // Update badge
    notifCount++;
    badge.textContent = notifCount;
    badge.classList.remove('hidden');
}
