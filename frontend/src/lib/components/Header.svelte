<script lang="ts">
    import { page } from '$app/stores';
    import { slide } from 'svelte/transition';
    import { token, currentUser, theme } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import Button from '$lib/components/Button.svelte';

    let isMenuOpen = $state(false);

    const navItems = [
        { path: '/add-receipt', label: '🧾 Bon hochladen' },
        { path: '/add-transaction', label: '✍️ Manuelle Eingabe' },
        { path: '/dashboard', label: '📊 Übersicht' },
        { path: '/settings', label: '⚙️ Einstellungen' }
    ];

    function toggleMenu() { isMenuOpen = !isMenuOpen; }
    function closeMenu() { isMenuOpen = false; }

    function logout() {
        $token = null;
        $currentUser = null;
        closeMenu();
        goto('/');
    }

    function toggleTheme() {
        if ($theme === 'light') {
            $theme = 'dark';
            document.documentElement.classList.add('dark');
        } else {
            $theme = 'light';
            document.documentElement.classList.remove('dark');
        }
    }

    $effect(() => {
        if (browser) {
            if ($theme === 'dark') document.documentElement.classList.add('dark');
            else document.documentElement.classList.remove('dark');
        }
    });
</script>

<nav class="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 transition-colors">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            
            <div class="flex items-center">
                <a href="/dashboard" class="text-xl font-bold text-blue-600 dark:text-blue-400 tracking-tight">
                    WG<span class="text-gray-800 dark:text-white">Split</span>
                </a>
            </div>

            <div class="hidden md:flex items-center space-x-8">
                <button 
                    onclick={toggleTheme} 
                    class="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                    aria-label="Dark Mode umschalten"
                >
                    {#if $theme === 'light'}
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
                    {:else}
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                    {/if}
                </button>

                {#if $currentUser}
                    {#each navItems as item}
                        <a 
                            href={item.path} 
                            class="text-sm font-medium transition-colors border-b-2 px-1 py-5 { 
                                $page.url.pathname === item.path 
                                ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' 
                                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700' 
                            }"
                        >
                            {item.label}
                        </a>
                    {/each}
                    
                    <Button variant="outline" onclick={logout} aria-label="Ausloggen">
                        Logout
                    </Button>
                {/if}
            </div>

            <div class="flex items-center md:hidden gap-2">
                <button onclick={toggleTheme} class="p-2 text-gray-500 dark:text-gray-400">
                    {#if $theme === 'light'}
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
                    {:else}
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                    {/if}
                </button>

                <button 
                    onclick={toggleMenu} 
                    class="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none p-2"
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
        <div transition:slide={{ duration: 200 }} class="md:hidden bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-lg absolute w-full">
            <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                {#if $currentUser}
                    {#each navItems as item}
                        <a 
                            href={item.path}
                            onclick={closeMenu}
                            class="block px-3 py-2 rounded-md text-base font-medium {
                                $page.url.pathname === item.path 
                                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400' 
                                : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800'
                            }"
                        >
                            {item.label}
                        </a>
                    {/each}
                    <div class="px-3 py-2">
                        <Button variant="destructive" class="w-full justify-start" onclick={logout}>
                            Logout
                        </Button>
                    </div>
                {:else}
                    <a href="/" onclick={closeMenu} class="block px-3 py-2 text-gray-700 dark:text-gray-300 font-medium">Login</a>
                {/if}
            </div>
        </div>
    {/if}
</nav>