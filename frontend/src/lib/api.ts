import { get } from 'svelte/store';
import { token } from './stores';

const BASE_URL = 'http://localhost:8000/api';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    // Hole den aktuellen Token aus dem Store
    const currentToken = get(token);
    
    // Bereite die Header vor
    const headers = new Headers(options.headers || {});
    
    if (currentToken) {
        headers.set('Authorization', `Bearer ${currentToken}`);
    }
    
    // Wenn kein spezieller Content-Type gesetzt ist, gehen wir von JSON aus
    if (!headers.has('Content-Type') && 
        !(options.body instanceof URLSearchParams) && 
        !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    // Führe die Anfrage an FastAPI aus
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'API Error');
    }

    return response.json();
}