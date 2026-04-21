/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;

const CACHE = `cache-${version}`;
const ASSETS = [
    ...build, // Der gebaute SvelteKit Code
    ...files  // Alles aus dem static Ordner
];

// 1. Install-Event: Cacht alle Assets beim Installieren
sw.addEventListener('install', (event) => {
    async function addFilesToCache() {
        const cache = await caches.open(CACHE);
        await cache.addAll(ASSETS);
    }
    event.waitUntil(addFilesToCache());
    sw.skipWaiting();
});

// 2. Activate-Event: Löscht alte Caches, wenn eine neue Version kommt
sw.addEventListener('activate', (event) => {
    async function deleteOldCaches() {
        for (const key of await caches.keys()) {
            if (key !== CACHE) await caches.delete(key);
        }
    }
    event.waitUntil(deleteOldCaches());
    sw.clients.claim();
});

// 3. Fetch-Event: WICHTIG! Macht die App "offline ready" und triggert den Install Prompt
sw.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;

    async function respond() {
        const url = new URL(event.request.url);
        const cache = await caches.open(CACHE);

        // Serviere gecachte Dateien (HTML, CSS, JS, Bilder)
        if (ASSETS.includes(url.pathname)) {
            const cachedResponse = await cache.match(event.request);
            if (cachedResponse) return cachedResponse;
        }

        // Für API Requests (FastAPI): Versuche Netzwerk, bei Fehler zeige Cache (oder nichts)
        try {
            const response = await fetch(event.request);
            if (response.status === 200) {
                cache.put(event.request, response.clone());
            }
            return response;
        } catch {
            const cachedResponse = await cache.match(event.request);
            if (cachedResponse) return cachedResponse;
            return new Response('Offline', { status: 503 });
        }
    }
    event.respondWith(respond());
});