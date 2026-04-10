<script lang="ts">
    import { page } from '$app/stores';
    import { goto, beforeNavigate } from '$app/navigation';
    import { token } from '$lib/stores';
    import { onMount } from 'svelte';
    
    import '../app.css';
    import Header from '$lib/components/Header.svelte';
    import { fade } from 'svelte/transition';

    let { children } = $props();

    onMount(() => {
        checkAuth($page.url.pathname);
    });

    beforeNavigate((navigation) => {
        const targetPath = navigation.to?.url.pathname;
        if (targetPath) {
            checkAuth(targetPath);
        }
    });

    function checkAuth(path: string) {
        const isPublicPath = path === '/' || path === '/login'; 
        if (!isPublicPath && !$token) {
            goto('/');
        }
    }
</script>

<svelte:head>
    <title>WGSplit</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 font-sans text-gray-900">
    <Header />

    <main transition:fade={{ duration: 150 }}>
        {@render children()}
    </main>
</div>