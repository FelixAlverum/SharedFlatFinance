import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createPersistedStore<T>(key: string, startValue: T) {
    const storedValue = browser ? localStorage.getItem(key) : null;
    const initial = storedValue ? JSON.parse(storedValue) : startValue;
    const store = writable<T>(initial);

    if (browser) {
        store.subscribe(value => {
            if (value === null || value === undefined) {
                localStorage.removeItem(key);
            } else {
                localStorage.setItem(key, JSON.stringify(value));
            }
        });
    }

    return store;
}

export const token = createPersistedStore<string | null>('auth_token', null);
export const currentUser = createPersistedStore<any | null>('current_user', null);