<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { onMount } from 'svelte';
    import type { User, Transaction, Balance } from '$lib/types';

    // --- State ---
    let users: User[] = $state([]);
    let transactions: Transaction[] = $state([]);
    let balances: Balance[] = $state([]);
    
    let isLoading = $state(true);
    let isFetchingMore = $state(false);
    let errorMessage = $state('');

    const limit = 15;
    let offset = $state(0);
    let hasMore = $state(true);
    let observerNode: HTMLElement | undefined = $state();

    async function fetchTransactions(reset = false) {
        if (reset) {
            offset = 0;
            hasMore = true;
        }
        try {
            const txRes = await apiFetch(`/transactions/?limit=${limit}&offset=${offset}`);
            if (reset) {
                transactions = txRes;
            } else {
                transactions = [...transactions, ...txRes];
            }
            if (txRes.length < limit) {
                hasMore = false;
            }
        } catch (error: any) {
            errorMessage = error.message;
        }
    }

    // FIX: onMount selbst darf nicht async sein, wenn ein Cleanup-Return genutzt wird
    onMount(() => {
        // Interne async Funktion für den Initial-Load
        const init = async () => {
            try {
                const [usersRes, balancesRes] = await Promise.all([
                    apiFetch('/users/'),
                    apiFetch('/balances/')
                ]);
                users = usersRes;
                // FIX: Typen für a und b hinzugefügt
                balances = (balancesRes as Balance[]).sort((a: Balance, b: Balance) => b.amount - a.amount);
                await fetchTransactions(true);
            } catch (error: any) {
                errorMessage = error.message;
            } finally {
                isLoading = false;
            }
        };

        init();

        const observer = new IntersectionObserver(async (entries) => {
            if (entries[0].isIntersecting && hasMore && !isFetchingMore && !isLoading) {
                isFetchingMore = true;
                offset += limit;
                await fetchTransactions();
                isFetchingMore = false;
            }
        }, { rootMargin: '200px' });

        if (observerNode) observer.observe(observerNode);
        
        // Jetzt ist der Return korrekt, da die umschließende Funktion nicht async ist
        return () => observer.disconnect();
    });

    async function deleteTransaction(id: string) {
        if (!confirm('Wirklich löschen?')) return;
        try {
            await apiFetch(`/transactions/${id}`, { method: 'DELETE' });
            const [newBalancesRes] = await Promise.all([
                apiFetch('/balances/'),
                fetchTransactions(true) 
            ]);
            // FIX: Typen für a und b hinzugefügt
            balances = (newBalancesRes as Balance[]).sort((a: Balance, b: Balance) => b.amount - a.amount);
        } catch (error: any) {
            alert(error.message);
        }
    }

    function getTransactionTotal(tx: Transaction): number {
        return tx.items.reduce((sum, item) => sum + item.total_price, 0);
    }

    function getUserName(email: string): string {
        return users.find(u => u.email === email)?.name || email;
    }
</script>

<main class="max-w-7xl mx-auto p-4 md:p-8">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">📊 WG Übersicht</h1>
        <a href="/add-receipt" class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-2 px-4 rounded-lg shadow transition">
            + Neuer Bon
        </a>
    </div>

    {#if isLoading}
        <div class="flex justify-center py-20 italic text-gray-500">Lade Dashboard...</div>
    {:else if errorMessage}
        <div class="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 mb-8">❌ {errorMessage}</div>
    {:else}

        <section class="mb-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each balances as balance}
                <div class="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div class="text-xs font-bold text-gray-400 uppercase mb-1">{balance.name}</div>
                    <div class="text-2xl font-black {balance.amount >= 0 ? 'text-green-600' : 'text-red-600'}">
                        {balance.amount.toFixed(2)} €
                    </div>
                </div>
            {/each}
        </section>

        <section>
            <h2 class="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Historie</h2>
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <ul class="divide-y divide-gray-200">
                    {#each transactions as tx (tx.id)}
                        <li class="p-4 flex justify-between items-center hover:bg-gray-50 transition">
                            <div>
                                <div class="font-bold text-gray-900">{tx.title}</div>
                                <div class="text-xs text-gray-500">
                                    {getUserName(tx.payer_email)} · {new Date(tx.date).toLocaleDateString()}
                                </div>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="font-bold text-gray-900">{getTransactionTotal(tx).toFixed(2)} €</span>
                                <div class="flex items-center gap-2">
    <a 
        href="/edit-receipt/{tx.id}"
        class="px-4 py-2 bg-gray-100 hover:bg-blue-50 text-gray-700 hover:text-blue-600 text-sm font-semibold rounded-lg border border-gray-200 transition"
    >
        ✏️ Edit
    </a>
    <button 
        onclick={() => deleteTransaction(tx.id)}
        class="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-semibold rounded-lg border border-red-200 transition"
    >
        🗑️
    </button>
</div>
                            </div>
                        </li>
                    {/each}
                </ul>

                <div bind:this={observerNode} class="p-8 flex justify-center border-t border-gray-50">
                    {#if isFetchingMore}
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    {:else if !hasMore}
                        <span class="text-gray-400 text-sm italic">Alle Transaktionen geladen</span>
                    {/if}
                </div>
            </div>
        </section>
    {/if}
</main>