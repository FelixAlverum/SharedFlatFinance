<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { User, Transaction, Balance } from '$lib/types';
    
    import ConfirmModal from '$lib/components/ConfirmModal.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import { appState } from '$lib/state.svelte';

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

    let isDeleteModalOpen = $state(false);
    let transactionToDelete = $state<string | null>(null);

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
            // Fehler bereits von apiFetch gelöst!
        }
    }

    onMount(() => {
        // Interne async Funktion für den Initial-Load
        const init = async () => {
            try {
                const [usersRes, balancesRes] = await Promise.all([
                    apiFetch('/users/'),
                    apiFetch('/balances/')
                ]);
                users = usersRes;
                balances = (balancesRes as Balance[]).sort((a: Balance, b: Balance) => b.amount - a.amount);
                await fetchTransactions(true);
            } catch (error: any) {
                // Fehler bereits von apiFetch gelöst!
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
        return () => observer.disconnect();
    });

function requestDelete(id: string) {
        transactionToDelete = id;
        isDeleteModalOpen = true;
    }

    function cancelDelete() {
        isDeleteModalOpen = false;
        transactionToDelete = null;
    }

    async function executeDelete() {
        if (!transactionToDelete) return;
        
        const id = transactionToDelete;
        
        // Modal sofort schließen für bessere UI Responsiveness
        isDeleteModalOpen = false;
        transactionToDelete = null;

        try {
            await apiFetch(`/transactions/${id}`, { method: 'DELETE' });

            transactions = transactions.filter(t => t.id !== id);

            const newBalancesRes = await apiFetch('/balances/');
            balances = (newBalancesRes as Balance[]).sort((a, b) => b.amount - a.amount);
            
            if (transactions.length < 5 && hasMore) {
                await fetchTransactions();
            }

        } catch (error: any) {
            // errorMessage = `Fehler beim Löschen: ${error.message}`;
            // Fehler bereits von apiFetch gelöst
            appState.addToast('Fehler beim Löschen des Kassenbons', 'error');
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
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">📊 WG Übersicht</h1>
        
        <Button onclick={() => goto('/add-receipt')}>
            + Neuer Bon
        </Button>
    </div>

    {#if isLoading}
        <div class="flex flex-col items-center justify-center py-20 gap-4">
            <Spinner class="h-10 w-10 border-blue-600 dark:border-blue-400" />
            <span class="italic text-gray-500 dark:text-gray-400">Lade Dashboard...</span>
        </div>
    {:else if errorMessage}
        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg text-red-700 dark:text-red-400 mb-8">❌ {errorMessage}</div>
    {:else}

        <section class="mb-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each balances as balance}
                <Card class="p-6">
                    <div class="text-xs font-bold text-gray-400 uppercase mb-1">{balance.name}</div>
                    <div class="text-2xl font-black {balance.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-500'}">
                        {balance.amount.toFixed(2)} €
                    </div>
                </Card>
            {/each}
        </section>

        <section>
            <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4 border-b dark:border-gray-800 pb-2">Historie</h2>
            
            <Card class="overflow-hidden">
                <ul class="divide-y divide-gray-200 dark:divide-gray-800">
                    {#each transactions as tx (tx.id)}
                        <li class="p-4 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                            <div>
                                <div class="font-bold text-gray-900 dark:text-gray-100">{tx.title}</div>
                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                    {getUserName(tx.payer_email)} · {new Date(tx.date).toLocaleDateString()}
                                </div>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="font-bold text-gray-900 dark:text-gray-100">{getTransactionTotal(tx).toFixed(2)} €</span>
                                
                                <div class="flex items-center gap-2">
                                    <Button variant="secondary" onclick={() => goto(`/edit-receipt/${tx.id}`)}>
                                        ✏️ Edit
                                    </Button>
                                    
                                    <Button variant="destructive" onclick={() => requestDelete(tx.id)}>
                                        🗑️
                                    </Button>
                                </div>
                            </div>
                        </li>
                    {/each}
                </ul>

                <div bind:this={observerNode} class="p-8 flex justify-center border-t border-gray-50 dark:border-gray-800">
                    {#if isFetchingMore}
                        <Spinner />
                    {:else if !hasMore}
                        <span class="text-gray-400 dark:text-gray-500 text-sm italic">Alle Transaktionen geladen</span>
                    {/if}
                </div>
            </Card>
        </section>
    {/if}
</main>

<ConfirmModal 
    isOpen={isDeleteModalOpen}
    title="Kassenbon löschen"
    message="Möchtest du diesen Kassenbon wirklich dauerhaft löschen? Die Bilanzen aller Mitbewohner werden automatisch neu berechnet."
    confirmText="Ja, löschen"
    cancelText="Abbrechen"
    isDestructive={true}
    onConfirm={executeDelete}
    onCancel={cancelDelete}
/>