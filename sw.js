const CACHE_NAME = 'cancionero-v2'; // Cambiamos a v2 para forzar actualización
const ASSETS = [
  'https://roman1616.github.io',
  'https://roman1616.github.io'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting(); // Fuerza al Service Worker a activarse de inmediato
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim()); // Toma el control de la página de inmediato
});

// Este bloque es OBLIGATORIO para que aparezca el botón de instalar
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});


