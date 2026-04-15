import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    // Wichtig für TailwindCSS und andere Pre-Prozessoren
    preprocess: vitePreprocess(),

    compilerOptions: {
        // Force runes mode for the project, except for libraries. Can be removed in svelte 6.
        runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
    },

    kit: {
        // Hier konfigurieren wir den Node-Adapter für Docker
        adapter: adapter({
            out: 'build' // Gibt an, dass der kompilierte Code im Ordner "build" landen soll
        })
    }
};

export default config;