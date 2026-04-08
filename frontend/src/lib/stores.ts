import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// 1. Schau nach, ob wir schon einen Token im Browser gespeichert haben
const initialToken = browser ? window.localStorage.getItem('token') : null;

// 2. Erstelle reaktive Variablen
export const token = writable<string | null>(initialToken);
export const currentUser = writable<{ email: string; name: string } | null>(null);

// 3. Jedes Mal, wenn sich der Token ändert, speichern wir ihn im Browser
token.subscribe((value) => {
    if (browser) {
        if (value) {
            window.localStorage.setItem('token', value);
        } else {
            window.localStorage.removeItem('token');
        }
    }
});