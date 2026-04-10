<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import '../app.css';
    
    // Neue Imports für Routing und Animationen
    import { page } from '$app/stores';
    import { fade, slide } from 'svelte/transition';

    let { children } = $props();

    // State für das Hamburger-Menü
    let isMenuOpen = $state(false);

    // Navigations-Pfade
    const navItems = [
        { path: '/add-receipt', label: '🧾 Bon hochladen' },
        { path: '/dashboard', label: '📊 Übersicht' },
        { path: '/settings', label: '⚙️ Einstellungen' }
    ];

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
    }

    function closeMenu() {
        isMenuOpen = false;
    }
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-gray-50 font-sans text-gray-900">
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/add-receipt" class="text-xl font-bold text-blue-600 tracking-tight">
                        WG<span class="text-gray-800">Split</span>
                    </a>
                </div>

                <div class="hidden md:flex items-center space-x-8">
                    {#each navItems as item}
                        <a 
                            href={item.path} 
                            class="text-sm font-medium transition-colors border-b-2 px-1 py-5 { 
                                $page.url.pathname === item.path 
                                ? 'border-blue-600 text-blue-600' 
                                : 'border-transparent text-gray-500 hover:text-gray-900 hover:border-gray-300' 
                            }"
                        >
                            {item.label}
                        </a>
                    {/each}
                </div>

                <div class="flex items-center md:hidden">
                    <button 
                        onclick={toggleMenu} 
                        class="text-gray-500 hover:text-gray-900 focus:outline-none p-2"
                        aria-label="Menü öffnen"
                    >
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            {#if isMenuOpen}
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            {:else}
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            {/if}
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        {#if isMenuOpen}
            <div transition:slide={{ duration: 200 }} class="md:hidden bg-white border-b border-gray-200 shadow-lg absolute w-full">
                <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                    {#each navItems as item}
                        <a 
                            href={item.path}
                            onclick={closeMenu}
                            class="block px-3 py-2 rounded-md text-base font-medium {
                                $page.url.pathname === item.path 
                                ? 'bg-blue-50 text-blue-700' 
                                : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                            }"
                        >
                            {item.label}
                        </a>
                    {/each}
                </div>
            </div>
        {/if}
    </nav>

    <main transition:fade={{ duration: 150 }}>
        {@render children()}
    </main>
</div>