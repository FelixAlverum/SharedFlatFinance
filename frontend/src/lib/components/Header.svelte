<script lang="ts">
    import { page } from '$app/stores';
    import { slide } from 'svelte/transition';
    import { token, currentUser } from '$lib/stores';
    import { goto } from '$app/navigation';

    let isMenuOpen = $state(false);

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

    function logout() {
        $token = null;
        $currentUser = null;
        closeMenu();
        goto('/');
    }
</script>

<nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <div class="flex items-center">
                <a href="/dashboard" class="text-xl font-bold text-blue-600 tracking-tight">
                    WG<span class="text-gray-800">Split</span>
                </a>
            </div>

            <div class="hidden md:flex items-center space-x-8">
                {#if $currentUser}
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
                    
                    <button 
                        onclick={logout}
                        class="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
                    >
                        Logout
                    </button>
                {:else}
                    <a href="/" class="text-sm font-medium text-gray-500 hover:text-blue-600">Login</a>
                {/if}
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
                {#if $currentUser}
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
                    <button 
                        onclick={logout}
                        class="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50"
                    >
                        Logout
                    </button>
                {:else}
                    <a href="/" onclick={closeMenu} class="block px-3 py-2 text-gray-700 font-medium">Login</a>
                {/if}
            </div>
        </div>
    {/if}
</nav>