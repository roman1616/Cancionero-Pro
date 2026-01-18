
const CACHE_NAME = 'cancionero-v1';

  'https://www.dropbox.com/scl/fi/r3thafjal4m6zvwllz9vl/Cancionero-Pro-v1.0.html?rlkey=qvfi10gk0bnymtrzyya06s92f&st=9n2j0ink&raw=1', 
  'https://www.dropbox.com/scl/fi/el9tkusu6sszh0epml6fh/manifest.json?rlkey=cm7gwf0x3g8b3ryserxcw0deu&st=peya6pog&raw=1'

// Pega aquí los enlaces raw=1 de tus archivos
const ASSETS = [
  'https://www.dropbox.com',
  'https://www.dropbox.com'
];
// Instalar y cachear archivos
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

// Responder desde cache si no hay red
self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then((res) => res || fetch(e.request)));
});
