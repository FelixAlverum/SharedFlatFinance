<script lang="ts">
    import { apiFetch } from '$lib/api';
    import type { User, Item, ParsedData } from '$lib/types';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import * as receiptLogic from '$lib/receipt-logic.svelte';
    
    // --- UI Komponenten ---
    import SplitModal from '$lib/components/SplitModal.svelte';
    import ReceiptItemList from '$lib/components/ReceiptItemList.svelte';
    import Card from '$lib/components/Card.svelte';
    import Button from '$lib/components/Button.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import Input from '$lib/components/Input.svelte';

    // --- State ---
    let files: FileList | null = $state(null);
    let isLoading = $state(false);
    let errorMessage = $state('');
    let parsedData: ParsedData | null = $state(null);
    let users: User[] = $state([]);
    let isModalOpen = $state(false);
    let activeItemIndex = $state(0);
    let showSummary = $state(false);

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
            goto('/dashboard');
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
    let summaryTotals = $derived.by(() => {
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
    <SplitModal bind:isOpen={isModalOpen} bind:item={parsedData.items[activeItemIndex]} {users} />
{/if}

<main class="max-w-7xl mx-auto p-4 md:p-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-900 dark:text-white">🧾 Kassenbon eintragen</h1>

    {#if !showSummary}
        <Card class="mb-8 p-6">
            <div class="flex flex-col md:flex-row gap-4 items-center">
                <div class="flex-1 w-full relative">
                    <label for="receipt" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        REWE Kassenbon hochladen (PDF)
                    </label>
                    <input 
                        id="receipt" 
                        type="file" 
                        accept=".pdf" 
                        bind:files={files} 
                        onchange={handleUpload}
                        disabled={isLoading}
                        class="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900/30 dark:file:text-blue-400 dark:hover:file:bg-blue-900/50 disabled:opacity-50 cursor-pointer" 
                    />
                </div>
                {#if isLoading}
                    <div class="text-blue-600 dark:text-blue-400 font-bold flex items-center gap-2 px-4">
                        <Spinner class="h-5 w-5 border-blue-600 dark:border-blue-400" />
                        <span class="animate-pulse">Lese Bon aus...</span>
                    </div>
                {/if}
            </div>
            {#if errorMessage}
                <div class="mt-4 text-red-600 dark:text-red-400 text-sm font-semibold">{errorMessage}</div>
            {/if}
        </Card>

        {#if parsedData}
            <Card class="overflow-hidden">
                <div class="p-6 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                    <div class="flex justify-between items-end mb-2">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Fortschritt der Aufteilung</span>
                        <span class="text-sm font-bold {completeItemsCount === totalItemsCount ? 'text-green-600 dark:text-green-400' : 'text-blue-600 dark:text-blue-400'}">
                            {completeItemsCount} von {totalItemsCount} Artikeln aufgeteilt
                        </span>
                    </div>
                    <div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden">
                        <div 
                            class="h-3 transition-all duration-500 ease-out {completeItemsCount === totalItemsCount ? 'bg-green-500' : 'bg-blue-500'}" 
                            style="width: {globalProgress}%">
                        </div>
                    </div>
                </div>

                <div class="p-6 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <Input id="title" label="Titel des Einkaufs" bind:value={parsedData.title} />
                    </div>
                    <div>
                        <label for="payer" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Wer hat bezahlt?</label>
                        <select id="payer" bind:value={parsedData.payer_email} class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 p-2 border bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 shadow-sm">
                            {#each users as user}
                                <option value={user.email}>{user.name}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <div class="bg-white dark:bg-gray-900 overflow-hidden">
                    <ReceiptItemList bind:items={parsedData.items} {users} {openSplitModal} />
                </div>

                <div class="p-6 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-800 flex justify-end">
                    <Button class="w-full md:w-auto" onclick={() => showSummary = true}>
                        Übersicht prüfen ➔
                    </Button>
                </div>
            </Card>
        {/if}

    {:else}
        <Card class="p-6 md:p-8 max-w-2xl mx-auto">
            <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Zusammenfassung</h2>
            
            <div class="mb-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
                <p class="text-sm text-blue-800 dark:text-blue-300 mb-2">Bezahlt von:</p>
                <p class="font-bold text-lg text-gray-900 dark:text-white">{users.find(u => u.email === parsedData?.payer_email)?.name}</p>
            </div>

            <h3 class="font-bold text-gray-700 dark:text-gray-300 mb-4 border-b dark:border-gray-700 pb-2">Wer zahlt wie viel?</h3>
            <ul class="space-y-3 mb-8">
                {#each summaryTotals as total}
                    <li class="flex justify-between items-center text-lg">
                        <span class="text-gray-800 dark:text-gray-200">{total.name}</span>
                        <span class="font-bold {total.amount > 0 ? 'text-gray-800 dark:text-gray-200' : 'text-gray-400 dark:text-gray-600'}">
                            {total.amount.toFixed(2)} €
                        </span>
                    </li>
                {/each}
            </ul>

            {#if incompleteItems.length > 0}
                <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg mb-8">
                    <h3 class="font-bold text-red-800 dark:text-red-300 mb-2 flex items-center gap-2">⚠️ Aktion erforderlich</h3>
                    <p class="text-sm text-red-700 dark:text-red-400 mb-3">Bitte teile zuerst folgende Produkte zu 100% auf, bevor du speichern kannst:</p>
                    <ul class="list-disc list-inside text-sm text-red-800 dark:text-red-400 space-y-1">
                        {#each incompleteItems as item}
                            <li>{item.name} <span class="font-semibold">({item.total_price.toFixed(2)}€)</span></li>
                        {/each}
                    </ul>
                </div>
            {/if}

            {#if errorMessage}
                <div class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm font-bold flex items-center gap-2 shadow-sm">
                    <span>❌</span>
                    <span>{errorMessage}</span>
                </div>
            {/if}

            <div class="flex flex-col md:flex-row gap-4 justify-between border-t dark:border-gray-800 pt-6">
                <Button variant="secondary" class="w-full md:w-auto" onclick={navigateBackToEdit}>
                    ⬅ Zurück
                </Button>
                
                <Button 
                    onclick={saveTransaction} 
                    disabled={isLoading || incompleteItems.length > 0}
                    class="w-full md:w-auto {incompleteItems.length === 0 ? 'bg-green-600 hover:bg-green-700' : ''}"
                >
                    {#if isLoading}
                        <Spinner class="h-5 w-5 border-white dark:border-white" />
                        Speichert...
                    {:else if incompleteItems.length > 0}
                        🔒 Speichern gesperrt
                    {:else}
                        ✅ Speichern
                    {/if}
                </Button>
            </div>
        </Card>
    {/if}
</main>