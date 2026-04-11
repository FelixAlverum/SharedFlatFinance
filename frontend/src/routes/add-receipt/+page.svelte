<script lang="ts">
    import { apiFetch } from '$lib/api';
    import type { User, Item, ParsedData } from '$lib/types';
    import SplitModal from '$lib/components/SplitModal.svelte';
    import ReceiptItemList from '$lib/components/ReceiptItemList.svelte';
    
    // Logik-Importe
    import * as receiptLogic from '$lib/receipt-logic';

    // --- State ---
    let files: FileList | null = $state(null);
    let isLoading = $state(false);
    let errorMessage = $state('');
    let parsedData: ParsedData | null = $state(null);
    let users: User[] = $state([]);
    let isModalOpen = $state(false);
    let activeItemIndex = $state(0);
    let showSummary = $state(false);

    // --- Initialisierung ---
    import { onMount } from 'svelte';
    onMount(async () => {
        users = await apiFetch('/users/');
    });

    async function handleUpload() {
        if (!files) return;
        isLoading = true;
        errorMessage = '';
        try {
            const formData = new FormData();
            formData.append('file', files[0]);
            const response = await apiFetch('/upload-receipt', { method: 'POST', body: formData });
            
            // Initialisierung der Pfand-Automatik
            const allEmails = users.map(u => u.email);
            response.items.forEach((item: Item) => {
                if (item.name.toUpperCase().includes('PFAND')) {
                    item.splits = users.map(u => ({ user_email: u.email, amount: 0 }));
                } else {
                    item.splits = [];
                }
            });
            receiptLogic.applyGlobalFairSplits(response.items);
            parsedData = response;
        } catch (e: any) {
            errorMessage = e.message;
        } finally { isLoading = false; }
    }

    async function saveTransaction() {
        if (!parsedData || incompleteItems.length > 0) return;
        isLoading = true;
        try {
            await apiFetch('/transactions/', {
                method: 'POST',
                body: JSON.stringify({
                    ...parsedData,
                    date: new Date().toISOString()
                })
            });
            window.location.href = '/dashboard';
        } catch (e: any) {
            errorMessage = e.message;
        } finally { isLoading = false; }
    }
    
    function navigateBackToEdit() {
        errorMessage = '';
        showSummary = false;
    }

    function openSplitModal(index: number) {
        activeItemIndex = index;
        isModalOpen = true;
    }

    // --- Derived ---
    let summaryTotals: { name: string, amount: number }[] = $derived.by(() => {
        if (!parsedData) return [];
        const totals: Record<string, { name: string, amount: number }> = {};
        users.forEach(u => totals[u.email] = { name: u.name, amount: 0 });
        
        parsedData.items.forEach(item => {
            if (item.splits) {
                item.splits.forEach(s => {
                    if (totals[s.user_email]) totals[s.user_email].amount += s.amount;
                });
            }
        });
        return Object.values(totals);
    });

    // In src/routes/add-receipt/+page.svelte (oder edit-receipt)
let incompleteItems: Item[] = $derived(
    parsedData!.items.filter((i: Item) => {
        const _dependency = i.splits; 
        return !receiptLogic.checkIsComplete(i);
    }) || []
);

    let totalItemsCount = $derived(parsedData!.items?.length || 0);
    let completeItemsCount = $derived(totalItemsCount - incompleteItems.length);
    let globalProgress = $derived(totalItemsCount === 0 ? 0 : (completeItemsCount / totalItemsCount) * 100);

</script>

{#if parsedData}
    <SplitModal bind:isOpen={isModalOpen} bind:item={parsedData.items[activeItemIndex]} users={users} />
{/if}

<main class="max-w-7xl mx-auto p-4 md:p-8">
    <h1 class="text-3xl font-bold mb-6">🧾 Kassenbon eintragen</h1>

    {#if !showSummary}
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <div class="flex flex-col md:flex-row gap-4 items-center">
                <div class="flex-1 w-full relative">
                    <label for="receipt" class="block text-sm font-medium text-gray-700 mb-2">REWE Kassenbon hochladen (PDF)</label>
                    <input 
                        id="receipt" 
                        type="file" 
                        accept=".pdf" 
                        bind:files={files} 
                        onchange={handleUpload}
                        disabled={isLoading}
                        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50 cursor-pointer" 
                    />
                </div>
                {#if isLoading}
                    <div class="text-blue-600 font-bold flex items-center gap-2 px-4">
                        <span class="animate-pulse">⏳ Lese Bon aus...</span>
                    </div>
                {/if}
            </div>
            {#if errorMessage}
                <div class="mt-4 text-red-600 text-sm font-semibold">{errorMessage}</div>
            {/if}
        </div>

        {#if parsedData}
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                
                <div class="p-6 border-b border-gray-200 bg-white">
                    <div class="flex justify-between items-end mb-2">
                        <span class="text-sm font-medium text-gray-600">Fortschritt der Aufteilung</span>
                        <span class="text-sm font-bold {completeItemsCount === totalItemsCount ? 'text-green-600' : 'text-blue-600'}">
                            {completeItemsCount} von {totalItemsCount} Artikeln aufgeteilt
                        </span>
                    </div>
                    <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                        <div 
                            class="h-3 transition-all duration-500 ease-out {completeItemsCount === totalItemsCount ? 'bg-green-500' : 'bg-blue-500'}" 
                            style="width: {globalProgress}%">
                        </div>
                    </div>
                </div>

                <div class="p-6 border-b border-gray-200 bg-gray-50 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label for="title" class="block text-sm font-medium text-gray-700">Titel des Einkaufs</label>
                        <input id="title" type="text" bind:value={parsedData.title} class="mt-1 block w-full rounded-md border-gray-300 p-2 border" />
                    </div>
                    <div>
                        <label for="payer" class="block text-sm font-medium text-gray-700">Wer hat bezahlt?</label>
                        <select id="payer" bind:value={parsedData.payer_email} class="mt-1 block w-full rounded-md border-gray-300 p-2 border bg-white">
                            {#each users as user}
                                <option value={user.email}>{user.name}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <ReceiptItemList 
            bind:items={parsedData.items} 
            {users} 
            {openSplitModal}  
        />

        </div>

                <div class="p-6 bg-gray-50 border-t border-gray-200 flex justify-end">
                    <button onclick={() => showSummary = true} class="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-md">
                        Übersicht prüfen ➔
                    </button>
                </div>
            </div>
        {/if}

    {:else}
        <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg max-w-2xl mx-auto border border-gray-200">
            <h2 class="text-2xl font-bold mb-6 text-gray-800">Zusammenfassung</h2>
            
            <div class="mb-6 bg-blue-50 p-4 rounded-lg border border-blue-100">
                <p class="text-sm text-blue-800 mb-2">Bezahlt von:</p>
                <p class="font-bold text-lg">{users.find(u => u.email === parsedData?.payer_email)?.name}</p>
            </div>

            <h3 class="font-bold text-gray-700 mb-4 border-b pb-2">Wer zahlt wie viel?</h3>
            <ul class="space-y-3 mb-8">
                {#each summaryTotals as total}
                    <li class="flex justify-between items-center text-lg">
                        <span>{total.name}</span>
                        <span class="font-bold {total.amount > 0 ? 'text-gray-800' : 'text-gray-400'}">{total.amount.toFixed(2)} €</span>
                    </li>
                {/each}
            </ul>

            {#if incompleteItems.length > 0}
                <div class="bg-red-50 border border-red-200 p-4 rounded-lg mb-8">
                    <h3 class="font-bold text-red-800 mb-2 flex items-center gap-2">⚠️ Aktion erforderlich</h3>
                    <p class="text-sm text-red-700 mb-3">Bitte teile zuerst folgende Produkte zu 100% auf, bevor du speichern kannst:</p>
                    <ul class="list-disc list-inside text-sm text-red-800 space-y-1">
                        {#each incompleteItems as item}
                            <li>{item.name} <span class="font-semibold">({item.total_price.toFixed(2)}€)</span></li>
                        {/each}
                    </ul>
                </div>
            {/if}

            {#if errorMessage}
                <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm font-bold flex items-center gap-2 shadow-sm">
                    <span>❌</span>
                    <span>{errorMessage}</span>
                </div>
            {/if}

            <div class="flex flex-col md:flex-row gap-4 justify-between border-t pt-6">
                <button onclick={navigateBackToEdit} class="w-full md:w-auto px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg transition">
                    ⬅ Zurück
                </button>
                
                <button 
                    onclick={saveTransaction} 
                    disabled={isLoading || incompleteItems.length > 0}
                    class="w-full md:w-auto px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold rounded-lg transition shadow-md flex justify-center items-center gap-2"
                >
                    {#if isLoading}
                        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Speichert...
                    {:else if incompleteItems.length > 0}
                        🔒 Speichern gesperrt
                    {:else}
                        ✅ Speichern
                    {/if}
                </button>
            </div>
        </div>
    {/if}
</main>