import { browser } from '$app/environment';
import type { User } from '$lib/types';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
    id: string;
    message: string;
    type: ToastType;
    duration: number;
}

class AppState {
    #token = $state<string | null>(null);
    #currentUser = $state<User | null>(null);
    #theme = $state<'light' | 'dark'>('dark');
    #toasts = $state<Toast[]>([]);

    constructor() {
        if (browser) {
            this.#token = localStorage.getItem('token');
            this.#theme = (localStorage.getItem('theme') as 'light' | 'dark') || 'light';
            
            const storedUser = localStorage.getItem('currentUser');
            if (storedUser) {
                try {
                    this.#currentUser = JSON.parse(storedUser);
                } catch {
                    localStorage.removeItem('currentUser');
                }
            }
        }
    }

    get token() { return this.#token; }
    set token(value: string | null) {
        this.#token = value;
        if (browser) {
            if (value) localStorage.setItem('token', value);
            else localStorage.removeItem('token');
        }
    }

    get currentUser() { return this.#currentUser; }
    set currentUser(value: User | null) {
        this.#currentUser = value;
        if (browser) {
            if (value) localStorage.setItem('currentUser', JSON.stringify(value));
            else localStorage.removeItem('currentUser');
        }
    }

    get theme() { return this.#theme; }
    set theme(value: 'light' | 'dark') {
        this.#theme = value;
        if (browser) {
            localStorage.setItem('theme', value);
            // Direktes DOM-Update für Tailwind Darkmode
            if (value === 'dark') document.documentElement.classList.add('dark');
            else document.documentElement.classList.remove('dark');
        }
    }

    get toasts() { return this.#toasts; }

    addToast(message: string, type: ToastType = 'info', duration = 7000) {
        const id = Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
        this.#toasts = [...this.#toasts, { id, message, type, duration }];
        setTimeout(() => {
            this.removeToast(id);
        }, duration);
    }

    removeToast(id: string) {
        this.#toasts = this.#toasts.filter(t => t.id !== id);
    }
}

export const appState = new AppState();