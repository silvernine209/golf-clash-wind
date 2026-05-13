// Golf Clash Wind — service worker.
// Strategy:
//   - Navigations (HTML): network-first with cache fallback → always fresh online,
//     but works offline. Avoids stale UI after deploys.
//   - Static assets (clubs.js, icons, manifest): cache-first.
const CACHE = "gc-wind-v2";
const SHELL = [
  "./",
  "./index.html",
  "./clubs.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const isHTML = req.mode === "navigate" ||
                 (req.headers.get("accept") || "").includes("text/html");

  if (isHTML) {
    // Network-first for HTML so we don't get stuck on a stale shell.
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(req).then((hit) => hit || caches.match("./index.html")))
    );
  } else {
    // Cache-first for everything else.
    e.respondWith(
      caches.match(req).then((hit) => hit ||
        fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        }).catch(() => caches.match("./index.html"))
      )
    );
  }
});
