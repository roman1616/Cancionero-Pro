const CACHE_NAME = 'cancionero-v2'; // Cambiamos a v2 para forzar actualización
const ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/script.js',
  '/logo.png' // Añade aquí todos tus archivos estáticos
];

// Paso 1: Instalación - Guardar archivos en caché
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// Paso 2: Interceptar peticiones
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Si el archivo está en caché, lo devuelve. Si no, va a internet.
      return response || fetch(event.request);
    })
  );
});



