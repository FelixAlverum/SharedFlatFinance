<script lang="ts">
    import { fade, scale } from 'svelte/transition';

    let { 
        isOpen = $bindable(false), 
        item = $bindable(), 
        users = [] 
    } = $props();

    let localSplits: Record<string, number> = $state({});

    $effect(() => {
        if (isOpen && item && users.length > 0) {
            const init: Record<string, number> = {};
            users.forEach((u: any) => init[u.email] = 0);
            
            if (item.splits) {
                item.splits.forEach((s: any) => {
                    init[s.user_email] = s.amount;
                });
            }
            localSplits = init;
        }
    });

    let totalAssigned = $derived(
        Object.values(localSplits).reduce((sum, val) => sum + (Number(val) || 0), 0)
    );
    let remaining = $derived(
        Math.round((item?.total_price - totalAssigned) * 100) / 100
    );

    function addQuantity(email: string) {
        if (!item) return;
        const current = localSplits[email] || 0;
        localSplits[email] = Math.round((current + item.unit_price) * 100) / 100;
    }

    function save() {
        item.splits = Object.entries(localSplits)
            .filter(([_, amount]) => amount > 0)
            .map(([email, amount]) => ({ user_email: email, amount: amount }));
        isOpen = false;
    }
</script>

{#if isOpen && item}
    <div 
        class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4 sm:p-6 backdrop-blur-sm"
        transition:fade={{ duration: 150 }}
    >
        <div 
            class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md flex flex-col max-h-[90vh] overflow-hidden"
            transition:scale={{ duration: 150, start: 0.95 }}
        >
            <div class="bg-gray-50 dark:bg-gray-900/50 p-4 sm:p-5 border-b border-gray-200 dark:border-gray-700 flex justify-between shrink-0">
                <div>
                    <h3 class="text-lg font-bold text-gray-800 dark:text-white">Manuelle Aufteilung</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">{item.name} <span class="opacity-75">({item.quantity} Stk. à {item.unit_price}€)</span></p>
                </div>
            </div>

            <div class="p-4 sm:p-6 space-y-5 overflow-y-auto">
                
                <div class="bg-blue-50 dark:bg-blue-900/20 p-3.5 rounded-lg flex flex-col sm:flex-row justify-between sm:items-center gap-1 sm:gap-2 border border-blue-100 dark:border-blue-800/50">
                    <span class="text-sm font-medium text-blue-800 dark:text-blue-300">
                        Gesamt: <span class="font-bold">{item.total_price}€</span>
                    </span>
                    <span class="text-sm font-bold {remaining === 0 ? 'text-green-600 dark:text-green-400' : remaining < 0 ? 'text-red-600 dark:text-red-400' : 'text-orange-600 dark:text-orange-400'}">
                        {remaining === 0 ? 'Perfekt ✓' : `Rest: ${remaining}€`}
                    </span>
                </div>

                <div class="space-y-3">
                    {#each users as user}
                        <div class="flex items-center gap-2 sm:gap-3">
                            <span class="w-1/3 text-sm font-medium text-gray-700 dark:text-gray-200 truncate" title={user.name}>
                                {user.name}
                            </span>
                            
                            <button 
                                type="button" 
                                onclick={() => addQuantity(user.email)} 
                                class="px-2 sm:px-3 py-1.5 bg-gray-100 hover:bg-blue-100 text-blue-700 dark:bg-gray-700 dark:hover:bg-blue-900/50 dark:text-blue-400 dark:border-gray-600 border text-xs font-bold rounded-lg transition-colors shrink-0"
                            >
                                +1 Stk.
                            </button>
                            
                            <div class="flex-1 relative">
                                <input 
                                    type="number" 
                                    step="0.01" 
                                    bind:value={localSplits[user.email]} 
                                    class="w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 rounded-lg p-2 text-right pr-8 transition-colors" 
                                />
                                <span class="absolute right-3 top-2.5 text-sm text-gray-400 dark:text-gray-500 pointer-events-none">€</span>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="bg-gray-50 dark:bg-gray-900/50 p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3 shrink-0">
                <button 
                    type="button" 
                    onclick={() => isOpen = false} 
                    class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg font-medium transition-colors"
                >
                    Abbrechen
                </button>
                <button 
                    type="button" 
                    onclick={save} 
                    disabled={remaining !== 0} 
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:disabled:bg-blue-800/50 text-white rounded-lg font-bold transition-colors"
                >
                    Speichern
                </button>
            </div>
        </div>
    </div>
{/if}