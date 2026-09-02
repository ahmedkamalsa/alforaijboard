// Service Worker - alforaijboard - يسرّع التحميل من ~5ث إلى ~1ث عبر الكاش الأوفلاين
// يكاش: app.js + styles.css + static-data/*.json (وأصول أساسية)

const CACHE_NAME = 'alforaijboard-v20260809-1';
const PRECACHE_URLS = [
  './',
  './index.html',
  './app.js',
  './styles.css',
  './config.js',
  './last-updated.json',
  './static-data/clients.json',
  './static-data/daily-agent-status.json',
  './static-data/dashboard-summary.json',
  './static-data/health.json',
  './static-data/live-db.json',
  './static-data/market-matching.json',
  './static-data/official-reference-sources.json',
  './static-data/opportunities.json',
  './static-data/opportunities-history.json',
  './static-data/opportunity-delta.json',
  './static-data/outreach-stats.json',
  './static-data/sources.json',
  './static-data/update-notifications.json',
  './static-data/weekly-digest.json',
  './static-data/whatsapp-alerts.json'
];

// Install: precache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: Cache-First for static assets & static-data, network fallback, then cache update
// يسرّع التحميل عبر إرجاع الكاش فوراً بدل انتظار شبكة 404KB مع 30 تبويب
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // فقط نفس المنشأ - تجاهل طلبات خارجية
  if (url.origin !== location.origin) return;

  const isStaticData = url.pathname.includes('/static-data/');
  const isCoreAsset =
    url.pathname.endsWith('/app.js') || url.pathname.endsWith('/styles.css') ||
    url.pathname.endsWith('/config.js') || url.pathname.endsWith('/index.html') ||
    url.pathname.endsWith('/') || url.pathname.endsWith('/last-updated.json');

  // تجاهل query مثل ?v=20260809 - نطابق عبر pathname
  // استراتيجية Cache-First: يرجع من الكاش فوراً (~1ث)، ويحدّث الكاش في الخلفية
  if (isStaticData || isCoreAsset) {
    event.respondWith(
      caches.match(req, { ignoreSearch: true }).then((cached) => {
        if (cached) {
          // تحديث في الخلفية (stale-while-revalidate سريع)
          event.waitUntil(
            fetch(req).then((res) => {
              if (res && res.ok) {
                const clone = res.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
              }
            }).catch(() => {})
          );
          return cached;
        }
        // غير موجود في الكاش -> شبكة ثم حفظ
        return fetch(req).then((res) => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        }).catch(() => {
          // أوفلاين تماماً ولا كاش
          return cached || Response.error();
        });
      })
    );
    return;
  }

  // باقي الملفات: network-first مع fallback للكاش (صور listings وغيرها)
  event.respondWith(
    fetch(req).then((res) => {
      if (res && res.ok) {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
      }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }))
  );
});
