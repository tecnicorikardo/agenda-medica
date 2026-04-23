/* Service Worker — Agenda Médica */
const CACHE = "agenda-v2";
const PRECACHE = ["/", "/app.js", "/app.css", "/manifest.json", "/assets/logo.png"];

// ── Install: pré-cache dos assets principais ──────────────────────────────────
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

// ── Activate: limpa caches antigos ───────────────────────────────────────────
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: network-first para /api, cache-first para assets ──────────────────
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // API: sempre vai para a rede, sem cache
  if (url.pathname.startsWith("/api")) return;

  // Navegação: serve index.html do cache se offline
  if (e.request.mode === "navigate") {
    e.respondWith(
      fetch(e.request).catch(() => caches.match("/"))
    );
    return;
  }

  // Assets: cache-first
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((res) => {
        if (res && res.status === 200 && res.type === "basic") {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, clone));
        }
        return res;
      });
    })
  );
});

// ── Push: recebe notificação do servidor ─────────────────────────────────────
self.addEventListener("push", (e) => {
  let data = { title: "Agenda Médica", body: "Nova notificação", url: "/", icon: "/icons/icon-192.png", badge: "/icons/badge-72.png", tag: "agenda" };
  try { if (e.data) data = { ...data, ...JSON.parse(e.data.text()) }; } catch {}

  e.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: data.badge,
      tag: data.tag,
      renotify: true,
      vibrate: [200, 100, 200],
      data: { url: data.url },
    })
  );
});

// ── Notification click: abre/foca o app ──────────────────────────────────────
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const target = e.notification.data?.url || "/";
  e.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const client of list) {
        if (client.url.includes(self.location.origin) && "focus" in client) {
          client.navigate(target);
          return client.focus();
        }
      }
      return clients.openWindow(target);
    })
  );
});
