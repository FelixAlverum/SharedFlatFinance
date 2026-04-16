<script lang="ts">
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/api';
    import { currentUser } from '$lib/stores';
    import { goto } from '$app/navigation';
    import type { User } from '$lib/types';
    import { fade } from 'svelte/transition';

    // --- State ---
    let users: User[] = $state([]);
    let title = $state('');
    let amountStr = $state('');
    let payerEmail = $state('');
    let involvedEmails: string[] = $state([]);
    
    let isLoading = $state(false);
    let errorMessage = $state('');

    // --- Initialisierung ---
    onMount(async () => {
        try {
            users = await apiFetch('/users/');
            // Vorauswahl: Der aktuell eingeloggte User hat meistens auch bezahlt
            if ($currentUser) {
                payerEmail = $currentUser.email;
                involvedEmails = [$currentUser.email];
            }
        } catch (e: any) {
            errorMessage = 'Fehler beim Laden der Benutzer.';
        }
    });

    // --- UI Actions ---
    function toggleUser(email: string) {
        if (involvedEmails.includes(email)) {
            involvedEmails = involvedEmails.filter(e => e !== email);
        } else {
            involvedEmails = [...involvedEmails, email];
        }
    }

    function toggleAll() {
        if (involvedEmails.length === users.length) {
            involvedEmails = [];
        } else {
            involvedEmails = users.map(u => u.email);
        }
    }

    // --- Submit Logik ---
    async function saveTransaction() {
        // Komma durch Punkt ersetzen für sicheres Parsing
        const amount = parseFloat(amountStr.replace(',', '.'));

        if (!title.trim() || !payerEmail || isNaN(amount) || amount <= 0 || involvedEmails.length === 0) {
            errorMessage = 'Bitte fülle alle Felder korrekt aus (Betrag > 0) und wähle mindestens eine beteiligte Person.';
            return;
        }

        isLoading = true;
        errorMessage = '';

        // 1. Faire Aufteilung für diesen einen Artikel berechnen
        const totalCents = Math.round(amount * 100);
        const numParticipants = involvedEmails.length;
        const shareCents = Math.trunc(totalCents / numParticipants);
        const remainderCents = totalCents % numParticipants;
        const absRemainder = Math.abs(remainderCents);
        const centSign = Math.sign(totalCents);

        // Mischen für Zufalls-Cent
        const shuffledEmails = [...involvedEmails].sort(() => Math.random() - 0.5);

        const splits = involvedEmails.map(email => {
            let extraCent = 0;
            if (shuffledEmails.indexOf(email) < absRemainder) {
                extraCent = centSign;
            }
            return {
                user_email: email,
                amount: (shareCents + extraCent) / 100
            };
        });

        // 2. Payload für das Backend zusammenbauen
        const payload = {
            title: title.trim(),
            date: new Date().toISOString(),
            payer_email: payerEmail,
            items: [
                {
                    name: title.trim(),
                    quantity: 1.0,
                    unit_price: amount,
                    total_price: amount,
                    category: 'Manuell',
                    splits: splits
                }
            ]
        };

        // 3. API Request
        try {
            await apiFetch('/transactions/', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            goto('/dashboard');
        } catch (e: any) {
            errorMessage = e.message;
            isLoading = false;
        }
    }
</script>

<main class="max-w-2xl mx-auto p-4 md:p-8" in:fade={{ duration: 150 }}>
    <h1 class="text-3xl font-bold mb-6 text-gray-900 dark:text-white">✍️ Manuelle Transaktion</h1>

    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        
        {#if errorMessage}
            <div class="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6 text-sm border border-red-200 dark:border-red-800">
                {errorMessage}
            </div>
        {/if}

        <form class="space-y-6" onsubmit={(e) => { e.preventDefault(); saveTransaction(); }}>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Titel der Ausgabe</label>
                    <input 
                        id="title" 
                        type="text" 
                        bind:value={title} 
                        placeholder="z.B. Stromrechnung, Kino..."
                        required 
                        class="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 p-2.5 border transition-colors" 
                    />
                </div>

                <div>
                    <label for="amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Betrag (€)</label>
                    <input 
                        id="amount" 
                        type="text" 
                        inputmode="decimal"
                        bind:value={amountStr} 
                        placeholder="0.00"
                        required 
                        class="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 p-2.5 border transition-colors" 
                    />
                </div>
            </div>

            <div class="pt-2 border-t border-gray-100 dark:border-gray-700">
                <label for="payer" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Wer hat bezahlt?</label>
                <select 
                    id="payer" 
                    bind:value={payerEmail} 
                    required
                    class="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 p-2.5 border transition-colors"
                >
                    <option value="" disabled>Bitte wählen...</option>
                    {#each users as user}
                        <option value={user.email}>{user.name}</option>
                    {/each}
                </select>
            </div>

            <div class="pt-2 border-t border-gray-100 dark:border-gray-700">
                <div class="flex justify-between items-end mb-3">
                    <span class="block text-sm font-medium text-gray-700 dark:text-gray-300">Wer ist daran beteiligt?</span>
                    <button 
                        type="button" 
                        onclick={toggleAll} 
                        class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline"
                    >
                        {involvedEmails.length === users.length ? 'Auswahl aufheben' : 'Alle auswählen'}
                    </button>
                </div>

                <div class="flex flex-wrap gap-3">
                    {#each users as user}
                        <button 
                            type="button"
                            onclick={() => toggleUser(user.email)} 
                            class="px-4 py-2 text-sm font-bold rounded-lg transition-all border 
                                {involvedEmails.includes(user.email) 
                                    ? 'bg-blue-600 border-blue-600 text-white dark:bg-blue-500 dark:border-blue-500 shadow-md transform scale-105' 
                                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700'}"
                        >
                            {user.name}
                        </button>
                    {/each}
                </div>
            </div>

            <div class="pt-6">
                <button 
                    type="submit" 
                    disabled={isLoading}
                    class="w-full flex justify-center items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 dark:bg-green-500 dark:hover:bg-green-600 dark:disabled:bg-green-800 text-white font-bold py-3 px-4 rounded-lg transition-colors shadow-sm"
                >
                    {#if isLoading}
                        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Speichert...
                    {:else}
                        ✅ Transaktion eintragen
                    {/if}
                </button>
            </div>

        </form>
    </div>
</main>