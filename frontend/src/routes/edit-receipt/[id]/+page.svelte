<script lang="ts">
    import { page } from '$app/state'; // Svelte 5 Way
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import type { User, Transaction, Item } from '$lib/types';
    import { checkIsComplete } from '$lib/receipt-logic.svelte';
    import { goto } from '$app/navigation';
    
    // --- UI Komponenten ---
    import SplitModal from '$lib/components/SplitModal.svelte';
    import ReceiptItemList from '$lib/components/ReceiptItemList.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    
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

    // Modal & Toggle Funktionen
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
        <button onclick={handleBack} class="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition">
            ← Zurück
        </button>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">✏️ Transaktion bearbeiten</h1>
    </div>

    {#if isLoading}
        <div class="flex flex-col items-center justify-center py-20 gap-4">
            <Spinner class="h-10 w-10 border-blue-600 dark:border-blue-400" />
            <span class="italic text-gray-500 dark:text-gray-400">Lade Transaktionsdaten...</span>
        </div>
    {:else if errorMessage && !transactionData}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 p-4 rounded-lg border border-red-200 dark:border-red-800">
            {errorMessage}
        </div>
    {:else if transactionData}
        
        <Card class="overflow-hidden">
            <div class="p-6 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <Input id="title" label="Titel" bind:value={transactionData.title} />
                </div>
                <div>
                    <label for="payer" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Bezahlt von</label>
                    <select id="payer" bind:value={transactionData.payer_email} class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 p-2 border bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 shadow-sm">
                        {#each users as user}
                            <option value={user.email}>{user.name}</option>
                        {/each}
                    </select>
                </div>
            </div>

            <div class="bg-white dark:bg-gray-900 overflow-hidden">
                <ReceiptItemList 
                    bind:items={transactionData.items} 
                    {users} 
                    {openSplitModal} 
                />
            </div>

            <div class="p-6 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4">
                
                <div class="flex items-center gap-2">
                    {#if incompleteItems.length > 0}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400">
                            ⚠️ {incompleteItems.length} Posten unvollständig
                        </span>
                    {:else}
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                            ✅ Alles vollständig aufgeteilt
                        </span>
                    {/if}
                    
                    {#if errorMessage}
                        <span class="text-red-600 dark:text-red-400 text-xs font-bold animate-pulse">! {errorMessage}</span>
                    {/if}
                </div>

                <div class="flex gap-3 w-full md:w-auto">
                    <Button 
                        variant="secondary" 
                        onclick={handleBack} 
                        class="flex-1 md:flex-none"
                    >
                        Abbrechen
                    </Button>
                    
                    <Button 
                        onclick={updateTransaction}
                        disabled={isSaving || incompleteItems.length > 0}
                        class="flex-1 md:flex-none"
                    >
                        {#if isSaving}
                            <Spinner class="h-5 w-5 border-white dark:border-white" />
                            Speichert...
                        {:else}
                            Änderungen speichern
                        {/if}
                    </Button>
                </div>
            </div>
        </Card>

        <SplitModal bind:isOpen={isModalOpen} bind:item={transactionData.items[activeItemIndex]} {users} />
        
    {/if}
</main>