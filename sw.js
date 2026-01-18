
const CACHE_NAME = 'cancionero-v1';

// Pega aquí los enlaces raw=1 de tus archivos
const ASSETS = [
  'https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/index.htm',
  'https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/manifest.json'
];
// Instalar y cachear archivos
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

// Responder desde cache si no hay red
self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then((res) => res || fetch(e.request)));
});

