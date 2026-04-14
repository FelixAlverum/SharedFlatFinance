<script lang="ts">
    import '../app.css';
    import Header from '$lib/components/Header.svelte';
    import { onMount } from 'svelte';
    import { token, currentUser } from '$lib/stores';
    import { apiFetch } from '$lib/api';
    import { fade } from 'svelte/transition';

    let { children } = $props();

    onMount(async () => {
        // Wenn ein Token da ist, aber noch keine User-Daten (oder um sie zu aktualisieren)
        if ($token && !$currentUser) {
            try {
                $currentUser = await apiFetch('/users/me');
            } catch (e) {
                console.warn("Sitzung abgelaufen");
            }
        }
    });
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200 flex flex-col">
    
    <Header />

    <main class="grow" transition:fade={{ duration: 150 }}>
        {@render children()}
    </main>

</div>