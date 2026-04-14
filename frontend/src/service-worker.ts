/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;

// Erstelle einen eindeutigen Cache-Namen für diesen Build
const CACHE = `wg-kasse-cache-${version}`;

// Alle Dateien, die SvelteKit generiert hat + alles aus dem static/ Ordner
const ASSETS = [
    ...build,
    ...files
];

// 1. INSTALLATION: Assets in den Cache laden
sw.addEventListener('install', (event) => {
    async function addFilesToCache() {
        const cache = await caches.open(CACHE);
        await cache.addAll(ASSETS);
    }
    event.waitUntil(addFilesToCache());
    sw.skipWaiting();
});

// 2. AKTIVIERUNG: Alte Caches löschen, wenn es ein Update gibt
sw.addEventListener('activate', (event) => {
    async function deleteOldCaches() {
        for (const key of await caches.keys()) {
            if (key !== CACHE) await caches.delete(key);
        }
    }
    event.waitUntil(deleteOldCaches());
    sw.clients.claim();
});

// 3. FETCH: Anfragen abfangen
sw.addEventListener('fetch', (event) => {
    // Ignoriere alles, was kein GET-Request ist (z.B. API POSTs)
    if (event.request.method !== 'GET') return;
    
    // Ignoriere Anfragen an deine externe FastAPI
    if (event.request.url.includes('/api/')) return;

    async function respond() {
        const url = new URL(event.request.url);
        const cache = await caches.open(CACHE);

        // Wenn die angefragte Datei zu unseren statischen Assets gehört, 
        // lade sie SOFORT aus dem Cache (macht die App rasend schnell)
        if (ASSETS.includes(url.pathname)) {
            const cachedResponse = await cache.match(event.request);
            if (cachedResponse) return cachedResponse;
        }

        // Ansonsten versuche es über das Netzwerk
        try {
            const response = await fetch(event.request);
            
            // Wenn erfolgreich, direkt in den Cache legen für später
            if (response.status === 200) {
                cache.put(event.request, response.clone());
            }
            return response;
        } catch {
            // Wenn das Netzwerk fehlschlägt (Offline) und wir es im Cache haben
            const cachedResponse = await cache.match(event.request);
            if (cachedResponse) return cachedResponse;
            
            // Im absoluten Notfall (offline und nicht gecacht)
            return new Response('Du bist offline', { status: 408 });
        }
    }

    event.respondWith(respond());
});