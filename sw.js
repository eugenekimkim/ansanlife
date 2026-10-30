/* 안산살이 service worker
   - 화면(index.html): 네트워크 우선, 오프라인이면 마지막으로 받은 화면
   - 이미지·글꼴·공지 원문: 캐시 우선(백그라운드로 갱신)
   - API 서버, 네이버 지도, 카메라 사진: 캐시하지 않음 */
const CACHE = 'ansanlife-v4';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'assets/intro-orange.jpg', 'assets/intro-sky.jpg', 'assets/icon-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

const sameOrigin = url => url.origin === self.location.origin;
const fonts = url => url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (!sameOrigin(url) && !fonts(url)) return; // API·지도는 그대로 네트워크로

  if (url.pathname.endsWith('/admin.html')) return; // 관리 페이지는 항상 네트워크로
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { if (r.ok && !r.redirected) { const c = r.clone(); caches.open(CACHE).then(x => x.put('index.html', c)); } return r; })
      .catch(() => caches.match('index.html').then(r => r || caches.match('./'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(r => { if (r.ok && r.type !== 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); } return r; }).catch(() => hit);
    return hit || net;
  }));
});
