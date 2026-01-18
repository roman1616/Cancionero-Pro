const CACHE_NAME = 'cancionero-v1';
const ASSETS = [
  'https://roman1616.github.io',
  'https://roman1616.github.io'
];

// Al instalar, guarda los archivos en la memoria del teléfono
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

// Permite que la app funcione aunque no tengas internet
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});

