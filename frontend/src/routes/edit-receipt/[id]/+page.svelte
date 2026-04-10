<script lang="ts">
    import { page } from '$app/state'; // Svelte 5 Way
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import type { User, Transaction, Item } from '$lib/types';
    import SplitModal from '$lib/components/SplitModal.svelte';

    // --- State ---
    const txId = page.params.id;
    let isLoading = $state(true);
    let isSaving = $state(false);
    let errorMessage = $state('');
    
    let users: User[] = $state([]);
    let transactionData: Transaction | null = $state(null);
    
    let isModalOpen = $state(false);
    let activeItemIndex = $state(0);
    let showSummary = $state(false);

    onMount(async () => {
        try {
            // Lade User und die spezifische Transaktion parallel
            const [usersRes, txRes] = await Promise.all([
                apiFetch('/users/'),
                apiFetch(`/transactions/${txId}`)
            ]);
            users = usersRes;
            transactionData = txRes;
        } catch (error: any) {
            errorMessage = error.message;
        } finally {
            isLoading = false;
        }
    });

    // --- Logic (Wiederverwendung deiner Logik) ---
    function getSplitSum(item: Item) {
        return item.splits.reduce((sum, split) => sum + split.amount, 0);
    }

    function checkIsComplete(item: Item) {
        return Math.abs(item.total_price - getSplitSum(item)) < 0.01;
    }

    let incompleteItems: Item[] = $derived(
    transactionData?.items.filter((item: Item) => !checkIsComplete(item)) || []
);

    async function updateTransaction() {
        if (!transactionData) return;
        if (incompleteItems.length > 0) {
            errorMessage = "Bitte teile alle Posten vollständig auf.";
            return;
        }

        isSaving = true;
        try {
            await apiFetch(`/transactions/${txId}`, {
                method: 'PUT',
                body: JSON.stringify(transactionData)
            });
            alert('Änderungen gespeichert!');
            window.location.href = '/dashboard';
        } catch (error: any) {
            errorMessage = error.message;
        } finally {
            isSaving = false;
        }
    }

    // Modal & Toggle Funktionen (analog zu add-receipt Seite)
    function openSplitModal(index: number) {
        activeItemIndex = index;
        isModalOpen = true;
    }
</script>

<main class="max-w-7xl mx-auto p-4 md:p-8">
    <div class="flex items-center gap-4 mb-6">
        <a href="/dashboard" class="text-gray-500 hover:text-gray-800">← Zurück</a>
        <h1 class="text-3xl font-bold">✏️ Transaktion bearbeiten</h1>
    </div>

    {#if isLoading}
        <div class="py-20 text-center italic text-gray-500">Lade Transaktionsdaten...</div>
    {:else if errorMessage && !transactionData}
        <div class="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{errorMessage}</div>
    {:else if transactionData}
        
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="p-6 border-b border-gray-200 bg-gray-50 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700">Titel</label>
                    <input id="title" type="text" bind:value={transactionData.title} class="mt-1 block w-full rounded-md border-gray-300 p-2 border" />
                </div>
                <div>
                    <label for="payer" class="block text-sm font-medium text-gray-700">Bezahlt von</label>
                    <select id="payer" bind:value={transactionData.payer_email} class="mt-1 block w-full rounded-md border-gray-300 p-2 border bg-white">
                        {#each users as user}
                            <option value={user.email}>{user.name}</option>
                        {/each}
                    </select>
                </div>
            </div>

            <table class="w-full text-left border-collapse">
                <tbody class="divide-y divide-gray-200">
                    {#each transactionData.items as item, index}
                        <tr class="hover:bg-gray-50 {checkIsComplete(item) ? '' : 'bg-yellow-50'}">
                            <td class="p-4 font-medium text-sm">{item.name}</td>
                            <td class="p-4 text-sm font-bold">{item.total_price.toFixed(2)}€</td>
                            <td class="p-4 text-right">
                                <button onclick={() => openSplitModal(index)} class="text-blue-600 hover:underline">Aufteilung ändern</button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>

            <div class="p-6 bg-gray-50 border-t flex justify-between items-center">
                <p class="text-sm text-gray-600">
                    {#if incompleteItems.length > 0}
                        <span class="text-red-600 font-bold">⚠️ {incompleteItems.length} Posten unvollständig</span>
                    {:else}
                        <span class="text-green-600 font-bold">✅ Alles bereit</span>
                    {/if}
                </p>
                <button 
                    onclick={updateTransaction}
                    disabled={isSaving || incompleteItems.length > 0}
                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg disabled:bg-gray-400"
                >
                    {isSaving ? 'Speichert...' : 'Änderungen übernehmen'}
                </button>
            </div>
        </div>

        {#if transactionData}
            <SplitModal bind:isOpen={isModalOpen} bind:item={transactionData.items[activeItemIndex]} {users} />
        {/if}
    {/if}
</main>