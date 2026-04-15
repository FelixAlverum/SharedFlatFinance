<script lang="ts">
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import { fade } from 'svelte/transition';

    type TotalSpend = { name: string; total_spend: number };
    type TimeSeries = { period: string; amount: number };
    // Die PopularItem Struktur wurde um user_email und user_name erweitert
    type PopularItem = { user_email: string; user_name: string; name: string; buy_count: number; total_spend: number };

    // --- State ---
    let totalSpend: TotalSpend[] = $state([]);
    let popularItems: PopularItem[] = $state([]);
    let spendingOverTime: TimeSeries[] = $state([]);
    
    let isLoading = $state(true);
    let errorMessage = $state('');
    let selectedYear = $state(new Date().getFullYear());
    
    // --- State für die Tabs ---
    let activeTab = $state('');

    async function loadStats() {
        isLoading = true;
        errorMessage = '';
        try {
            // Kategorie-Fetch wurde entfernt
            const [ts, pi, sot] = await Promise.all([
                apiFetch('/stats/total-spend'),
                apiFetch('/stats/popular-items'), 
                apiFetch(`/stats/spending-over-time?year=${selectedYear}`)
            ]);
            
            totalSpend = ts.sort((a: TotalSpend, b: TotalSpend) => b.total_spend - a.total_spend);
            popularItems = pi;
            spendingOverTime = sot;

            // Setze den ersten User als aktiven Tab, falls noch keiner gewählt ist
            if (pi.length > 0 && !activeTab) {
                activeTab = pi[0].user_email;
            }

        } catch (e: any) {
            errorMessage = e.message || 'Fehler beim Laden der Statistiken.';
        } finally {
            isLoading = false;
        }
    }

    onMount(loadStats);

    // --- Derived Data ---
    let maxTotalSpend = $derived(Math.max(...totalSpend.map(s => s.total_spend), 1));
    let maxMonthlySpend = $derived(Math.max(...spendingOverTime.map(s => s.amount), 1));

    // Extrahiere alle einzigartigen User aus den PopularItems für die Tab-Leiste
    let uniqueUsers = $derived.by(() => {
        const map = new Map<string, { email: string, name: string }>();
        popularItems.forEach(item => {
            if (!map.has(item.user_email)) {
                map.set(item.user_email, { email: item.user_email, name: item.user_name });
            }
        });
        return Array.from(map.values());
    });

    // Filtere die Items für den aktuell ausgewählten Tab und nimm nur die Top 5
    let currentTabItems = $derived(
        popularItems
            .filter(i => i.user_email === activeTab)
            .sort((a, b) => b.buy_count - a.buy_count)
            .slice(0, 5)
    );

    function formatMonth(period: string) {
        const [year, month] = period.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1, 1);
        return date.toLocaleDateString('de-DE', { month: 'short' });
    }
</script>

<main class="max-w-7xl mx-auto p-4 md:p-8" in:fade={{ duration: 150 }}>
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">📈 WG Statistiken</h1>
        
        <select 
            bind:value={selectedYear} 
            onchange={loadStats}
            class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 shadow-sm transition-colors"
        >
            <option value={new Date().getFullYear()}>Jahr {new Date().getFullYear()}</option>
            <option value={new Date().getFullYear() - 1}>Jahr {new Date().getFullYear() - 1}</option>
            <option value={new Date().getFullYear() - 2}>Jahr {new Date().getFullYear() - 2}</option>
        </select>
    </div>

    {#if isLoading}
        <div class="flex justify-center items-center h-64">
            <svg class="animate-spin h-10 w-10 text-blue-600 dark:text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>
    {:else if errorMessage}
        <div class="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6 border border-red-200 dark:border-red-800">
            {errorMessage}
        </div>
    {:else}
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <div class="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col transition-colors">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">Deine Ausgaben in {selectedYear}</h2>
                {#if spendingOverTime.length > 0}
                    <div class="flex-1 min-h-62.5 flex items-end gap-2 sm:gap-4 pt-8">
                        {#each spendingOverTime as data}
                            <div class="relative flex-1 flex flex-col items-center group h-full justify-end">
                                <div class="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-10 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs font-bold py-1.5 px-2.5 rounded whitespace-nowrap pointer-events-none z-10 shadow-lg">
                                    {data.amount.toFixed(2)} €
                                </div>
                                <div 
                                    class="w-full bg-blue-600 hover:bg-blue-500 dark:bg-blue-500 dark:hover:bg-blue-400 rounded-t-md transition-all duration-700 ease-out"
                                    style="height: {(data.amount / maxMonthlySpend) * 100}%"
                                ></div>
                                <span class="mt-3 text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400">
                                    {formatMonth(data.period)}
                                </span>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400 italic">
                        Keine Ausgaben in diesem Jahr.
                    </div>
                {/if}
            </div>

            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">WG Leaderboard</h2>
                <div class="space-y-5">
                    {#each totalSpend as user, index}
                        <div>
                            <div class="flex justify-between text-sm font-bold mb-1.5">
                                <span class="text-gray-700 dark:text-gray-200 flex items-center gap-2">
                                    {#if index === 0} 👑 {/if}
                                    {user.name}
                                </span>
                                <span class="text-gray-900 dark:text-white">{user.total_spend.toFixed(2)} €</span>
                            </div>
                            <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                                <div 
                                    class="h-full rounded-full transition-all duration-1000 {index === 0 ? 'bg-yellow-400 dark:bg-yellow-500' : 'bg-blue-600 dark:bg-blue-500'}" 
                                    style="width: {(user.total_spend / maxTotalSpend) * 100}%"
                                ></div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="lg:col-span-3 bg-white dark:bg-gray-800 p-0 sm:p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 transition-colors overflow-hidden">
                <div class="p-6 sm:p-0">
                    <h2 class="text-xl font-bold mb-2 text-gray-800 dark:text-gray-100">Favoriten der WG</h2>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">Die Top 5 Artikel für jeden Mitbewohner.</p>
                </div>

                {#if uniqueUsers.length > 0}
                    <div class="flex overflow-x-auto border-b border-gray-200 dark:border-gray-700 no-scrollbar px-6 sm:px-0">
                        {#each uniqueUsers as user}
                            <button
                                class="px-5 py-3 text-sm font-bold whitespace-nowrap border-b-2 transition-colors {activeTab === user.email ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'}"
                                onclick={() => activeTab = user.email}
                            >
                                {user.name}
                            </button>
                        {/each}
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse min-w-125">
                            <thead>
                                <tr class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
                                    <th class="p-4 font-bold w-12 text-center">#</th>
                                    <th class="p-4 font-bold">Artikel</th>
                                    <th class="p-4 font-bold text-center w-32">Menge</th>
                                    <th class="p-4 font-bold text-right w-40">Gesamtkosten</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100 dark:divide-gray-800/50">
                                {#each currentTabItems as item, index}
                                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors group">
                                        <td class="p-4 text-center font-mono text-sm text-gray-400 dark:text-gray-500">
                                            {index + 1}
                                        </td>
                                        <td class="p-4 font-medium text-gray-900 dark:text-gray-100">
                                            {item.name}
                                        </td>
                                        <td class="p-4 text-center">
                                            <span class="inline-block bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 py-1 px-3 rounded-full text-xs font-bold border border-blue-200 dark:border-blue-800/50">
                                                {item.buy_count}x
                                            </span>
                                        </td>
                                        <td class="p-4 text-right font-bold text-gray-900 dark:text-gray-100">
                                            {item.total_spend.toFixed(2)} €
                                        </td>
                                    </tr>
                                {/each}
                                {#if currentTabItems.length === 0}
                                    <tr>
                                        <td colspan="4" class="p-8 text-center text-gray-500 dark:text-gray-400 italic">
                                            Keine Artikel für diesen Nutzer gefunden.
                                        </td>
                                    </tr>
                                {/if}
                            </tbody>
                        </table>
                    </div>
                {:else}
                    <p class="text-sm text-gray-500 italic p-6 sm:p-0">Noch keine Favoriten vorhanden.</p>
                {/if}
            </div>

        </div>
    {/if}
</main>