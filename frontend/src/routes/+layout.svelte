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
                // apiFetch wirft dank unseres vorherigen Updates automatisch einen 
                // Error und loggt den User aus, falls der Token abgelaufen ist!
                $currentUser = await apiFetch('/users/me');
            } catch (e) {
                console.warn("Sitzung abgelaufen");
            }
        }
    });
</script>

<Header />

<main transition:fade={{ duration: 150 }}>
    {@render children()}
</main>