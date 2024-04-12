// This is the service worker with the combined offline experience (Offline page + Offline copy of pages)

const CACHE = "engage-cache";

importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

// Add whichever assets you want to pre-cache here:
const PRECACHE_ASSETS = [
  '/static/',
  '/offline/',
]

// Listener for the install event - pre-caches our assets list on service worker install.
self.addEventListener('install', event => {
  event.waitUntil((async () => {
      const cache = await caches.open(CACHE);
      cache.addAll(PRECACHE_ASSETS);
  })());
});


self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

if (workbox.navigationPreload.isSupported()) {
  workbox.navigationPreload.enable();
}

workbox.routing.registerRoute(
  new RegExp('/*'),
  new workbox.strategies.StaleWhileRevalidate({
    cacheName: CACHE
  })
);

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preloadResp = await event.preloadResponse;

        if (preloadResp) {
          return preloadResp;
        }

        const networkResp = await fetch(event.request);
        return networkResp;
      } catch (error) {

        const cache = await caches.open(CACHE);
        const cachedResp = await cache.match('/offline/');
        return cachedResp;
      }
    })());
  }
});
