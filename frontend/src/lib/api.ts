import { get } from 'svelte/store';
import { token } from './stores';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Zentraler API-Wrapper für Fetch-Calls.
 * Behandelt automatisch JSON-Parsing, Pydantic-Error-Formatting und Auth-Tokens.
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    // 1. Hole den aktuellen Token aus dem Store
    const currentToken = get(token);
    
    // 2. Bereite die Header vor
    const headers = new Headers(options.headers || {});
    
    if (currentToken) {
        headers.set('Authorization', `Bearer ${currentToken}`);
    }
    
    // Wenn kein spezieller Content-Type gesetzt ist, gehen wir von JSON aus.
    // Verhindert, dass FormData (wie beim File-Upload) überschrieben wird.
    if (!headers.has('Content-Type') && 
        !(options.body instanceof URLSearchParams) && 
        !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    // 3. URL sicher zusammenbauen
    const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // 4. Erfolgreiche Response: Direkt parsen und zurückgeben
        if (response.ok) {
            // 204 No Content liefert keinen Body
            if (response.status === 204) return null;
            return await response.json();
        }

        // 5. Fehlerbehandlung: Backend-Response lesen
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            // Wenn das Backend hart crasht und kein JSON schickt (z.B. 502 Bad Gateway)
            throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }

        // 6. FastAPI / Pydantic Error-Parsing
        let parsedErrorMessage = 'Ein unbekannter Fehler ist aufgetreten.';

        // Typischer 422 Unprocessable Entity (Validierungsfehler) von FastAPI
        if (response.status === 422 && errorData.detail && Array.isArray(errorData.detail)) {
            parsedErrorMessage = errorData.detail
                .map((e: any) => {
                    const fieldLocation = e.loc ? e.loc[e.loc.length - 1] : 'unbekanntes Feld';
                    return `Fehler bei '${fieldLocation}': ${e.msg}`;
                })
                .join(' | ');
        } 
        // Normale HTTPException (z.B. 400 Bad Request mit String-Detail)
        else if (errorData.detail && typeof errorData.detail === 'string') {
            parsedErrorMessage = errorData.detail;
        } 
        // Fallback für andere Backend-Muster
        else if (errorData.message) {
            parsedErrorMessage = Array.isArray(errorData.message) 
                ? errorData.message.map((e: any) => JSON.stringify(e)).join(' | ') 
                : errorData.message;
        } 
        // Absoluter Notnagel
        else {
            parsedErrorMessage = typeof errorData === 'object' ? JSON.stringify(errorData) : String(errorData);
        }

        // Wir werfen einen Error, der nur den sauberen, lesbaren String enthält
        throw new Error(parsedErrorMessage);

    } catch (error: any) {
        // Netzwerkfehler (Server offline, CORS-Probleme, etc.) abfangen
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            throw new Error('Netzwerkfehler: Das Backend ist nicht erreichbar.');
        }
        // Bereits von uns formatierte Fehler weitergeben
        throw error;
    }
}