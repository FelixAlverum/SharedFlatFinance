<script lang="ts">
    import { page } from '$app/state'; // Svelte 5 Way
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import type { User, Transaction, Item } from '$lib/types';
    import SplitModal from '$lib/components/SplitModal.svelte';
    import ReceiptItemList from '$lib/components/ReceiptItemList.svelte';
    import {checkIsComplete} from '$lib/receipt-logic.svelte';
    import { goto } from '$app/navigation';
    
    // --- State ---
    const txId = page.params.id;
    let isLoading = $state(true);
    let isSaving = $state(false);
    let errorMessage = $state('');
    
    let users: User[] = $state([]);
    let transactionData: Transaction | null = $state(null);
    
    let isModalOpen = $state(false);
    let activeItemIndex = $state(0);

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

    let incompleteItems: Item[] = $derived(
    transactionData!.items.filter((item: Item) => !checkIsComplete(item)) || []
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
            goto('/dashboard');
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

    function handleBack() {
        errorMessage = '';
        goto('/dashboard');
    }
</script>

<main class="max-w-7xl mx-auto p-4 md:p-8">
    <div class="flex items-center gap-4 mb-6">
        <button onclick={handleBack} class="text-gray-500 hover:text-gray-800 transition">← Zurück</button>
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

            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <ReceiptItemList 
                bind:items={transactionData.items} 
                {users} 
                {openSplitModal} 
            />
            </div>

            <div class="p-6 bg-gray-50 border-t flex flex-col md:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-2">
                    {#if incompleteItems.length > 0}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800">
                            ⚠️ {incompleteItems.length} Posten unvollständig
                        </span>
                    {:else}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                            ✅ Alles vollständig aufgeteilt
                        </span>
                    {/if}
                    
                    {#if errorMessage}
                        <span class="text-red-600 text-xs font-bold animate-pulse">! {errorMessage}</span>
                    {/if}
                </div>

                <div class="flex gap-3 w-full md:w-auto">
                    <button 
                        onclick={handleBack}
                        class="flex-1 md:flex-none px-6 py-2 bg-white border border-gray-300 text-gray-700 font-bold rounded-lg hover:bg-gray-50 transition"
                    >
                        Abbrechen
                    </button>
                    <button 
                        onclick={updateTransaction}
                        disabled={isSaving || incompleteItems.length > 0}
                        class="flex-1 md:flex-none bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-8 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md"
                    >
                        {isSaving ? 'Speichert...' : 'Änderungen speichern'}
                    </button>
                </div>
            </div>
        </div>

        <SplitModal bind:isOpen={isModalOpen} bind:item={transactionData.items[activeItemIndex]} {users} />
        
    {/if}
</main>