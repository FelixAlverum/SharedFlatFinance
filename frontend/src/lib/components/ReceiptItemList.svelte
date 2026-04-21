<script lang="ts">
    import type { Item, User } from '$lib/types';
    import * as logic from '$lib/receipt-logic.svelte';
    import Button from '$lib/components/ui/Button.svelte';

    interface Props {
        items: Item[];
        users: User[];
        openSplitModal: (index: number) => void;
    }

    let { 
        items = $bindable(), 
        users,
        openSplitModal,
    }: Props = $props();

    // Dark Mode optimierte Hintergrundfarben für die Zustände
    function getRowClass(item: Item) {
        if (logic.checkIsComplete(item)) return 'bg-white dark:bg-gray-900';
        const sum = logic.getSplitSum(item);
        if (sum > 0.01) return 'bg-red-50 dark:bg-red-900/20'; 
        return 'bg-yellow-50/30 dark:bg-yellow-900/10';
    }

    function handleToggleUser(item: Item, email: string) {
        logic.toggleUser(item, email, items);
    }

    function handleToggleAll(item: Item) {
        logic.toggleAll(item, users, items);
    }

    // --- NEU: Funktion zum Löschen einer Zeile ---
    function deleteItem(index: number) {
        items = items.filter((_, i) => i !== index);
    }
</script>

<div class="hidden lg:block overflow-x-auto">
    <table class="w-full text-left border-collapse min-w-150">
        <thead>
            <tr class="bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                <th class="p-3 font-bold w-1/2">Artikel & Preis</th>
                <th class="p-3 font-bold text-right">Wer zahlt?</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
            {#each items as item, index}
                <tr class="{getRowClass(item)} transition-colors">
                    
                    <td class="p-3">
                        <div class="flex items-center gap-3">
                            <input 
                                type="text" 
                                bind:value={item.name} 
                                class="font-medium bg-transparent border-none focus:ring-2 focus:ring-blue-500 rounded p-1 -ml-1 flex-1 text-gray-900 dark:text-white" 
                            />
                            <span class="font-bold text-gray-800 dark:text-gray-200 whitespace-nowrap">
                                {item.total_price.toFixed(2)}€
                            </span>
                        </div>
                    </td>

                    <td class="p-3">
                        <div class="flex flex-wrap items-center justify-end gap-2">
                            {#each users as user}
                                <Button 
                                    variant={logic.isUserActive(item, user.email) ? 'primary' : 'outline'}
                                    class="px-3! py-1.5! text-xs"
                                    onclick={() => handleToggleUser(item, user.email)} 
                                >
                                    {user.name.substring(0, 6)}
                                </Button>
                            {/each}
                            
                            <Button 
                                variant="secondary" 
                                class="px-3! py-1.5! text-xs" 
                                onclick={() => handleToggleAll(item)}
                            >
                                Alle
                            </Button>
                            
                            <Button 
                                variant="secondary" 
                                class="px-3! py-1.5! text-xs flex items-center gap-1" 
                                onclick={() => openSplitModal(index)}
                                title="Detail Aufteilung"
                            >
                                ✏️
                            </Button>

                            <Button 
                                variant="destructive" 
                                class="px-2! py-1.5! text-xs flex items-center justify-center" 
                                onclick={() => deleteItem(index)}
                                title="Artikel löschen"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </Button>
                        </div>
                    </td>

                </tr>
            {/each}
        </tbody>
    </table>
</div>

<div class="lg:hidden space-y-3 p-3">
    {#each items as item, index}
        <div class="{getRowClass(item)} p-3 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm transition-colors">
            
            <div class="flex justify-between items-center mb-3">
                <input 
                    type="text" 
                    bind:value={item.name} 
                    class="font-medium bg-transparent border-none focus:ring-2 focus:ring-blue-500 rounded p-1.5 -ml-1 flex-1 text-gray-900 dark:text-white {logic.checkIsComplete(item) ? 'bg-transparent' : 'bg-black/5 dark:bg-white/5'}" 
                />
                <span class="font-bold text-gray-800 dark:text-gray-200 whitespace-nowrap ml-2">
                    {item.total_price.toFixed(2)}€
                </span>
            </div>

            <div class="flex flex-wrap items-center gap-2">
                {#each users as user}
                    <Button 
                        variant={logic.isUserActive(item, user.email) ? 'primary' : 'outline'}
                        class="px-3! py-1.5! text-xs"
                        onclick={() => handleToggleUser(item, user.email)} 
                    >
                        {user.name.substring(0, 6)}
                    </Button>
                {/each}
                
                <Button 
                    variant="secondary" 
                    class="px-3! py-1.5! text-xs" 
                    onclick={() => handleToggleAll(item)}
                >
                    Alle
                </Button>
                
                <Button 
                    variant="secondary" 
                    class="px-3! py-1.5! text-xs flex items-center gap-1" 
                    onclick={() => openSplitModal(index)}
                >
                    ✏️
                </Button>

                <Button 
                    variant="destructive" 
                    class="px-2! py-1.5! text-xs ml-auto flex items-center justify-center" 
                    onclick={() => deleteItem(index)}
                    title="Artikel löschen"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </Button>
            </div>
            
        </div>
    {/each}
</div>