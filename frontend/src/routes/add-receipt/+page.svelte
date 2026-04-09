<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { onMount } from 'svelte';
    import SplitModal from '$lib/components/SplitModal.svelte';

    let files: FileList | null = $state(null);
    let isLoading = $state(false);
    let errorMessage = $state('');
    let parsedData: any = $state(null);

    let users: any[] = $state([]);
    let isModalOpen = $state(false);
    let activeItemIndex = $state(0);
    
    let showSummary = $state(false); 

    onMount(async () => {
        try {
            users = await apiFetch('/users/');
        } catch (e) {
            console.error("Fehler beim Laden der User", e);
        }
    });

    function recalculateEqualSplits(item: any, activeEmails: string[]) {
        if (activeEmails.length === 0) {
            item.splits = [];
            return;
        }
        const amount = Math.round((item.total_price / activeEmails.length) * 100) / 100;
        item.splits = activeEmails.map(email => ({ user_email: email, amount }));
        
        const sum = amount * activeEmails.length;
        const diff = Math.round((item.total_price - sum) * 100) / 100;
        if (diff !== 0) {
            item.splits[0].amount = Math.round((item.splits[0].amount + diff) * 100) / 100;
        }
    }

    function toggleUser(item: any, email: string) {
        let activeEmails = item.splits.filter((s: any) => s.amount > 0).map((s: any) => s.user_email);
        
        if (activeEmails.includes(email)) {
            activeEmails = activeEmails.filter((e: string) => e !== email); 
        } else {
            activeEmails.push(email); 
        }
        recalculateEqualSplits(item, activeEmails);
    }

    function toggleAll(item: any) {
        const activeEmails = item.splits.filter((s: any) => s.amount > 0).map((s: any) => s.user_email);
        
        if (activeEmails.length === users.length) {
            recalculateEqualSplits(item, []);
        } else {
            const allEmails = users.map(u => u.email);
            recalculateEqualSplits(item, allEmails);
        }
    }

    function isUserActive(item: any, email: string): boolean {
        return item.splits.some((s: any) => s.user_email === email && s.amount > 0);
    }

    // ANGEPASST: Braucht kein Event mehr, triggert direkt beim Auswählen der Datei
    async function handleUpload() {
        if (!files || files.length === 0) return;

        isLoading = true;
        errorMessage = '';
        parsedData = null;
        showSummary = false;

        try {
            const formData = new FormData();
            formData.append('file', files[0]);

            const response = await apiFetch('/upload-receipt', {
                method: 'POST',
                body: formData
            });

            const allEmails = users.map(u => u.email);
            response.items = response.items.map((item: any) => {
                item.splits = [];
                if (item.name.toUpperCase().includes('PFAND') || item.name.toUpperCase().includes('LEERGUT')) {
                    recalculateEqualSplits(item, allEmails);
                }
                return item;
            });
            parsedData = response;
        } catch (error: any) {
            errorMessage = error.message || 'Fehler beim Auslesen des Bons.';
        } finally {
            isLoading = false;
        }
    }

    function openSplitModal(index: number) {
        activeItemIndex = index;
        isModalOpen = true;
    }

    async function saveTransaction() {
        try {
            await apiFetch('/transactions/', {
                method: 'POST',
                body: JSON.stringify(parsedData)
            });
            alert('🎉 Kassenbon erfolgreich in der Datenbank gespeichert!');
            parsedData = null; 
            files = null;
            showSummary = false;
        } catch (error: any) {
            errorMessage = error.message;
        }
    }

    function getSplitSum(item: any): number {
        if (!item.splits) return 0;
        return item.splits.reduce((sum: number, split: any) => sum + split.amount, 0);
    }

    function checkIsComplete(item: any): boolean {
        return Math.abs(item.total_price - getSplitSum(item)) < 0.01; 
    }

    let incompleteItems = $derived(() => {
        if (!parsedData) return [];
        return parsedData.items.filter((item: any) => !checkIsComplete(item));
    });

    let summaryTotals = $derived(() => {
        if (!parsedData) return [];
        const totals: Record<string, { name: string, amount: number }> = {};
        users.forEach(u => totals[u.email] = { name: u.name, amount: 0 });
        
        parsedData.items.forEach((item: any) => {
            if (item.splits) {
                item.splits.forEach((s: any) => {
                    if (totals[s.user_email]) totals[s.user_email].amount += s.amount;
                });
            }
        });
        return Object.values(totals);
    });

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

                <div class="hidden md:block overflow-x-auto">
                    <table class="w-full text-left border-collapse min-w-[800px]">
                        <thead>
                            <tr class="bg-gray-100 text-gray-600 text-xs uppercase tracking-wider">
                                <th class="p-3 font-semibold w-1/4">Produkt</th>
                                <th class="p-3 font-semibold w-12">Gesamt</th>
                                
                                {#each users as user}
                                    <th class="p-3 font-semibold w-20 text-center" title={user.name}>{user.name.substring(0, 6)}</th>
                                {/each}
                                
                                <th class="p-3 font-semibold w-20 text-center">Alle</th>
                                <th class="p-3 font-semibold w-12 text-center">Edit</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            {#each parsedData.items as item, index}
                                <tr class="hover:bg-gray-50 transition">
                                    <td class="p-2"><input type="text" bind:value={item.name} class="w-full text-sm border-transparent focus:border-blue-500 rounded p-1" /></td>
                                    
                                    <td class="p-2 relative">
                                        <div class="font-semibold text-gray-800 text-sm mb-1">{item.total_price.toFixed(2)}€</div>
                                    </td>

                                    {#each users as user}
                                        <td class="p-2 text-center">
                                            <button 
                                                onclick={() => toggleUser(item, user.email)} 
                                                class="w-full px-2 py-1.5 text-xs font-bold rounded transition border {isUserActive(item, user.email) ? 'bg-blue-500 text-white border-blue-500' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-300 hover:bg-blue-50'}"
                                                title="{user.name} zahlt mit"
                                            >
                                                {user.name.substring(0, 6)}
                                            </button>
                                        </td>
                                    {/each}

                                    <td class="p-2 text-center">
                                        <button onclick={() => toggleAll(item)} class="w-full px-2 py-1.5 text-xs font-bold rounded transition border bg-white text-gray-600 border-gray-300 hover:border-blue-300 hover:bg-blue-50">Alle</button>
                                    </td>

                                    <td class="p-2 text-center">
                                        <button onclick={() => openSplitModal(index)} class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded">✎</button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                <div class="block md:hidden divide-y divide-gray-200">
                    {#each parsedData.items as item, index}
                        <div class="p-4 bg-white">
                            <div class="flex gap-2 items-center mb-2">
                                <input type="text" bind:value={item.name} class="flex-1 text-sm font-semibold border-transparent focus:border-blue-500 rounded p-1 -ml-1" />
                                <span class="font-bold text-gray-800 whitespace-nowrap">{item.total_price.toFixed(2)}€</span>
                            </div>

                            <div class="flex flex-wrap items-center gap-2">
                                {#each users as user}
                                    <button 
                                        onclick={() => toggleUser(item, user.email)} 
                                        class="px-3 py-1.5 text-xs font-bold rounded transition border {isUserActive(item, user.email) ? 'bg-blue-500 text-white border-blue-500 shadow-sm' : 'bg-white text-gray-600 border-gray-300 active:bg-gray-100'}"
                                    >
                                        {user.name.substring(0, 6)}
                                    </button>
                                {/each}
                                <button onclick={() => toggleAll(item)} class="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-bold rounded border border-gray-300">Alle</button>
                                <button onclick={() => openSplitModal(index)} class="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-bold rounded border border-gray-300">✎ Edit</button>
                            </div>
                        </div>
                    {/each}
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
                <p class="font-bold text-lg">{users.find(u => u.email === parsedData.payer_email)?.name}</p>
            </div>

            <h3 class="font-bold text-gray-700 mb-4 border-b pb-2">Wer zahlt wie viel?</h3>
            <ul class="space-y-3 mb-8">
                {#each summaryTotals() as total}
                    <li class="flex justify-between items-center text-lg">
                        <span>{total.name}</span>
                        <span class="font-bold {total.amount > 0 ? 'text-gray-800' : 'text-gray-400'}">{total.amount.toFixed(2)} €</span>
                    </li>
                {/each}
            </ul>

            {#if incompleteItems().length > 0}
                <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-8">
                    <h3 class="font-bold text-yellow-800 mb-2 flex items-center gap-2">⚠️ Hinweis: Unvollständige Aufteilung</h3>
                    <p class="text-sm text-yellow-700 mb-3">Folgende Produkte sind noch nicht zu 100% aufgeteilt. Du kannst trotzdem speichern und sie später anpassen:</p>
                    <ul class="list-disc list-inside text-sm text-yellow-800 space-y-1">
                        {#each incompleteItems() as item}
                            <li>{item.name} <span class="font-semibold">({item.total_price.toFixed(2)}€)</span></li>
                        {/each}
                    </ul>
                </div>
            {/if}

            <div class="flex flex-col md:flex-row gap-4 justify-between border-t pt-6">
                <button onclick={() => showSummary = false} class="w-full md:w-auto px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg transition">
                    ⬅ Zurück
                </button>
                <button 
                    onclick={saveTransaction} 
                    class="w-full md:w-auto px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition shadow-md"
                >
                    ✅ Speichern
                </button>
            </div>
        </div>
    {/if}
</main>