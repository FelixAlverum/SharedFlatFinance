import { appState } from './state.svelte';
import { env } from '$env/dynamic/public';

const BASE_URL = env.PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Zentraler API-Wrapper für Fetch-Calls.
 * Behandelt automatisch JSON-Parsing, Pydantic-Error-Formatting, Auth-Tokens und Toasts.
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const currentToken = appState.token;
    const headers = new Headers(options.headers || {});
    
    // 1. Token anhängen, falls vorhanden
    if (currentToken) {
        headers.set('Authorization', `Bearer ${currentToken}`);
    }
    
    // 2. Content-Type automatisch setzen (außer bei FormData für Bild-Uploads)
    if (!headers.has('Content-Type') && 
        !(options.body instanceof URLSearchParams) && 
        !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // --- ERFOLGSFALL ---
        if (response.ok) {
            if (response.status === 204) return null;
            return await response.json();
        } 
        
        // --- FEHLERFALL ---
        else {
            const errorData = await response.json().catch(() => ({ detail: 'Unbekannter Fehler' }));
            let errorMessage = 'Etwas ist schiefgelaufen';

            // Spezifische Behandlung für FastAPI / Pydantic Validierungsfehler (422)
            // FastAPI sendet Fehler als Array zurück
            if (response.status === 422 && Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail.map((err: any) => {
                    // Holt das fehlerhafte Feld (z.B. "email" oder "password")
                    const field = err.loc[err.loc.length - 1];
                    return `${field}: ${err.msg}`;
                }).join(' | ');
            } 
            // Normale FastAPI HTTPException (z.B. 400 oder 404)
            else if (typeof errorData.detail === 'string') {
                errorMessage = errorData.detail;
            } 
            // Fallback für andere Formate
            else if (errorData.message) {
                errorMessage = errorData.message;
            }

            // NEU: Wenn der Token abgelaufen oder ungültig ist (401), direkt ausloggen
            if (response.status === 401) {
                appState.token = null;
                appState.currentUser = null;
                errorMessage = 'Sitzung abgelaufen. Bitte logge dich neu ein.';
            }

            // Automatischen Toast anzeigen
            appState.addToast(errorMessage, 'error');
            
            throw new Error(errorMessage);
        }
    } catch (err: any) {
        // --- NETZWERKFEHLER (Backend offline) ---
        if (err.message === 'Failed to fetch') {
            const networkError = 'Server nicht erreichbar. Überprüfe deine Verbindung.';
            appState.addToast(networkError, 'error');
            throw new Error(networkError);
        }
        
        // Alle anderen Fehler einfach weiterreichen
        throw err;
    }
}