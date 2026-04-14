<script lang="ts">
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import { fade } from 'svelte/transition';

    // --- Typen passend zu deinen Pydantic Schemas ---
    type TotalSpend = { name: string; total_spend: number };
    type PopularItem = { name: string; buy_count: number; total_spend: number };
    type TimeSeries = { period: string; amount: number };
    type CategorySpend = { category: string; amount: number };

    // --- State ---
    let totalSpend: TotalSpend[] = $state([]);
    let popularItems: PopularItem[] = $state([]);
    let spendingOverTime: TimeSeries[] = $state([]);
    let categorySpend: CategorySpend[] = $state([]);
    
    let isLoading = $state(true);
    let errorMessage = $state('');
    let selectedYear = $state(new Date().getFullYear());

    // --- Ladefunktion ---
    async function loadStats() {
        isLoading = true;
        errorMessage = '';
        try {
            // Alle 4 Endpunkte parallel abrufen für maximale Geschwindigkeit
            const [ts, pi, sot, cs] = await Promise.all([
                apiFetch('/stats/total-spend'),
                apiFetch('/stats/popular-items?limit=5'),
                apiFetch(`/stats/spending-over-time?year=${selectedYear}`),
                apiFetch('/stats/category-spend')
            ]);
            
            // Sortieren: Wer am meisten ausgegeben hat, steht oben
            totalSpend = ts.sort((a: TotalSpend, b: TotalSpend) => b.total_spend - a.total_spend);
            popularItems = pi;
            spendingOverTime = sot;
            categorySpend = cs;
        } catch (e: any) {
            errorMessage = e.message || 'Fehler beim Laden der Statistiken.';
        } finally {
            isLoading = false;
        }
    }

    onMount(loadStats);

    // --- Hilfsdaten für Diagramme ($derived) ---
    // Maximaler Balken-Wert für das WG Leaderboard
    let maxTotalSpend = $derived(Math.max(...totalSpend.map(s => s.total_spend), 1));
    
    // Maximaler Balken-Wert für den Monatsverlauf
    let maxMonthlySpend = $derived(Math.max(...spendingOverTime.map(s => s.amount), 1));
    
    // Gesamtsumme für Prozentberechnung bei Kategorien
    let sumCategorySpend = $derived(categorySpend.reduce((sum, c) => sum + c.amount, 0) || 1);

    // Formatiert "YYYY-MM" zu "Jan", "Feb" etc.
    function formatMonth(period: string) {
        const [year, month] = period.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1, 1);
        return date.toLocaleDateString('de-DE', { month: 'short' });
    }
</script>

<main class="max-w-7xl mx-auto p-4 md:p-8" in:fade={{ duration: 150 }}>
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">📈 WG Statistiken</h1>
        
        <select 
            bind:value={selectedYear} 
            onchange={loadStats}
            class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 shadow-sm"
        >
            <option value={new Date().getFullYear()}>Jahr {new Date().getFullYear()}</option>
            <option value={new Date().getFullYear() - 1}>Jahr {new Date().getFullYear() - 1}</option>
            <option value={new Date().getFullYear() - 2}>Jahr {new Date().getFullYear() - 2}</option>
        </select>
    </div>

    {#if isLoading}
        <div class="flex justify-center items-center h-64">
            <svg class="animate-spin h-10 w-10 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>
    {:else if errorMessage}
        <div class="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6 border border-red-200 dark:border-red-800">
            {errorMessage}
        </div>
    {:else}
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <div class="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">Deine Ausgaben in {selectedYear}</h2>
                
                {#if spendingOverTime.length > 0}
                    <div class="flex-1 min-h-62.5 flex items-end gap-2 sm:gap-4 pt-8">
                        {#each spendingOverTime as data}
                            <div class="relative flex-1 flex flex-col items-center group h-full justify-end">
                                <div class="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-10 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs font-bold py-1.5 px-2.5 rounded whitespace-nowrap pointer-events-none z-10 shadow-lg">
                                    {data.amount.toFixed(2)} €
                                </div>
                                <div 
                                    class="w-full bg-blue-500 hover:bg-blue-400 dark:bg-blue-600 dark:hover:bg-blue-500 rounded-t-md transition-all duration-700 ease-out"
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
                        Keine Ausgaben in diesem Jahr gefunden.
                    </div>
                {/if}
            </div>

            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">WG Leaderboard</h2>
                <div class="space-y-5">
                    {#each totalSpend as user, index}
                        <div>
                            <div class="flex justify-between text-sm font-bold mb-1">
                                <span class="text-gray-700 dark:text-gray-200 flex items-center gap-2">
                                    {#if index === 0} 👑 {/if}
                                    {user.name}
                                </span>
                                <span class="text-gray-900 dark:text-white">{user.total_spend.toFixed(2)} €</span>
                            </div>
                            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                                <div 
                                    class="h-2.5 rounded-full {index === 0 ? 'bg-yellow-400' : 'bg-blue-500 dark:bg-blue-600'}" 
                                    style="width: {(user.total_spend / maxTotalSpend) * 100}%"
                                ></div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">Nach Kategorie</h2>
                {#if categorySpend.length > 0}
                    <div class="space-y-4">
                        {#each categorySpend as cat}
                            <div>
                                <div class="flex justify-between text-sm mb-1">
                                    <span class="font-medium text-gray-600 dark:text-gray-300">{cat.category}</span>
                                    <span class="font-bold text-gray-900 dark:text-white">{cat.amount.toFixed(2)} €</span>
                                </div>
                                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                    <div class="bg-purple-500 h-2 rounded-full" style="width: {(cat.amount / sumCategorySpend) * 100}%"></div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p class="text-sm text-gray-500 italic">Noch keine Kategorien erfasst.</p>
                {/if}
            </div>

            <div class="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <h2 class="text-xl font-bold mb-6 text-gray-800 dark:text-gray-100">Deine Favoriten (Oft gekauft)</h2>
                
                {#if popularItems.length > 0}
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                        {#each popularItems as item, index}
                            <div class="p-4 rounded-lg border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex flex-col relative overflow-hidden">
                                <span class="absolute -right-4 -bottom-6 text-6xl font-black text-gray-200/50 dark:text-gray-700/30 select-none pointer-events-none">
                                    #{index + 1}
                                </span>
                                
                                <span class="font-bold text-gray-800 dark:text-gray-100 text-lg truncate mb-1 z-10" title={item.name}>{item.name}</span>
                                <div class="flex justify-between items-end mt-auto z-10">
                                    <span class="text-xs font-bold bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 px-2 py-1 rounded">
                                        {item.buy_count}x gekauft
                                    </span>
                                    <span class="text-sm font-bold text-gray-600 dark:text-gray-400">
                                        {item.total_spend.toFixed(2)} €
                                    </span>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p class="text-sm text-gray-500 italic">Noch keine Favoriten vorhanden.</p>
                {/if}
            </div>

        </div>
    {/if}
</main>