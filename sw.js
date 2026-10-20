const CACHE_NAME = 'dart-dashboard-v1';

// 설치 시 즉시 활성화
self.addEventListener('install', event => {
  self.skipWaiting();
});

// 활성화 시 이전 캐시 정리
self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

// 네트워크 요청 가로채기 (실시간 데이터 갱신을 위해 캐시보다 네트워크 우선)
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
