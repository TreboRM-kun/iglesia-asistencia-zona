const CACHE_NAME = "iglesia-redencion-v10";
const APP_FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./src/img/bg2.png",
  "./src/img/lg1.png",
  "./src/img/app-icon-192.png",
  "./src/img/app-icon-512.png"
];

self.addEventListener("install", evento => {
  evento.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", evento => {
  evento.waitUntil(
    caches.keys()
      .then(claves => Promise.all(
        claves
          .filter(clave => clave !== CACHE_NAME)
          .map(clave => caches.delete(clave))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", evento => {
  const solicitud = evento.request;
  const url = new URL(solicitud.url);
  if (solicitud.method !== "GET" || url.origin !== self.location.origin) return;

  if (solicitud.mode === "navigate") {
    evento.respondWith(
      fetch(solicitud)
        .then(respuesta => {
          if (respuesta.ok) {
            const copia = respuesta.clone();
            evento.waitUntil(
              caches.open(CACHE_NAME).then(cache => cache.put(solicitud, copia))
            );
          }
          return respuesta;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  evento.respondWith(
    caches.match(solicitud).then(guardada =>
      guardada || fetch(solicitud).then(respuesta => {
        if (respuesta.ok) {
          const copia = respuesta.clone();
          evento.waitUntil(
            caches.open(CACHE_NAME).then(cache => cache.put(solicitud, copia))
          );
        }
        return respuesta;
      })
    )
  );
});
