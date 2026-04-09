<script lang="ts">
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
    <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
            <div class="bg-gray-50 p-4 border-b border-gray-200 flex justify-between">
                <div>
                    <h3 class="text-lg font-bold text-gray-800">Manuelle Aufteilung</h3>
                    <p class="text-sm text-gray-600">{item.name} ({item.quantity} Stk. à {item.unit_price}€)</p>
                </div>
            </div>

            <div class="p-6 space-y-4">
                <div class="bg-blue-50 p-3 rounded-lg flex justify-between items-center border border-blue-100">
                    <span class="text-sm font-medium text-blue-800">Gesamt: {item.total_price}€</span>
                    <span class="text-sm font-bold {remaining === 0 ? 'text-green-600' : remaining < 0 ? 'text-red-600' : 'text-orange-600'}">
                        {remaining === 0 ? 'Perfekt ✓' : `Rest: ${remaining}€`}
                    </span>
                </div>

                <div class="space-y-3 mt-4">
                    {#each users as user}
                        <div class="flex items-center gap-2">
                            <span class="w-1/3 text-sm font-medium truncate">{user.name}</span>
                            <button onclick={() => addQuantity(user.email)} class="px-2 py-1 bg-gray-100 hover:bg-blue-100 text-blue-700 text-xs rounded border transition">
                                +1 Stk.
                            </button>
                            <div class="flex-1 relative">
                                <input type="number" step="0.01" bind:value={localSplits[user.email]} class="w-full border-gray-300 focus:border-blue-500 rounded-md p-2 text-right pr-8" />
                                <span class="absolute right-3 top-2 text-gray-400">€</span>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="bg-gray-50 p-4 border-t border-gray-200 flex justify-end gap-3">
                <button onclick={() => isOpen = false} class="px-4 py-2 text-gray-600 hover:bg-gray-200 rounded font-medium">Abbrechen</button>
                <button onclick={save} disabled={remaining !== 0} class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded font-bold">Speichern</button>
            </div>
        </div>
    </div>
{/if}