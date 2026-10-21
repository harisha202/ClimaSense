const CACHE_NAME = 'climasense-v2.1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/manifest.json',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Cache assets gracefully so single network misses don't abort installation
      for (const asset of ASSETS_TO_CACHE) {
        try {
          await cache.add(asset);
        } catch (e) {
          console.warn('Failed to cache asset during SW install:', asset, e);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  // Bypass websockets, socket.io polling, and dynamic API endpoints
  if (event.request.url.includes('/socket.io/') || event.request.url.includes('/api/')) return;
  
  // Network first with cache fallback
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(async () => {
        // Fallback to cache
        const match = await caches.match(event.request);
        if (match) return match;
        
        
        
        return new Response('You are offline. Please reconnect to access live meteorological data.', {
          status: 503,
          headers: { 'Content-Type': 'text/plain' }
        });
      })
  );
});
