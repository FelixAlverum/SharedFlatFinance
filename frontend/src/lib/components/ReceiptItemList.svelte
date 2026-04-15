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
</script>

<div class="hidden lg:block overflow-x-auto">
    <table class="w-full text-left border-collapse min-w-200">
        <thead>
            <tr class="bg-gray-100 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400 text-xs uppercase tracking-wider border-b border-gray-200 dark:border-gray-800">
                <th class="p-3 font-semibold w-1/4">Produkt</th>
                <th class="p-3 font-semibold w-12 text-right">Gesamt</th>
                {#each users as user}
                    <th class="p-3 font-semibold w-20 text-center" title={user.name}>
                        {user.name.substring(0, 6)}
                    </th>
                {/each}
                <th class="p-3 font-semibold w-20 text-center">Alle</th>
                <th class="p-3 font-semibold w-12 text-center">Edit</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
            {#each items as item, index}
                <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition {getRowClass(item)}">
                    
                    <td class="p-2">
                        <input 
                            type="text" 
                            bind:value={item.name} 
                            class="w-full text-sm border-transparent focus:ring-1 focus:ring-blue-500 rounded p-1.5 text-gray-900 dark:text-white {logic.checkIsComplete(item) ? 'bg-transparent' : 'bg-black/5 dark:bg-white/5'}" 
                        />
                    </td>
                    
                    <td class="p-2 text-right align-middle">
                        <div class="font-bold text-gray-800 dark:text-gray-200 text-sm whitespace-nowrap">
                            {item.total_price.toFixed(2)}€
                        </div>
                    </td>
                    
                    {#each users as user}
                        <td class="p-2 text-center">
                            <Button 
                                variant={logic.isUserActive(item, user.email) ? 'primary' : 'outline'}
                                class="w-full px-2! py-1! text-xs"
                                onclick={() => handleToggleUser(item, user.email)} 
                            >
                                {user.name.substring(0, 6)}
                            </Button>
                        </td>
                    {/each}
                    
                    <td class="p-2 text-center">
                        <Button 
                            variant="secondary" 
                            class="w-full px-2! py-1! text-xs" 
                            onclick={() => handleToggleAll(item)}
                        >
                            Alle
                        </Button>
                    </td>
                    
                    <td class="p-2 text-center">
                        <Button 
                            variant="secondary" 
                            class="px-2! py-1! text-xs" 
                            onclick={() => openSplitModal(index)}
                        >
                            ✎
                        </Button>
                    </td>
                    
                </tr>
            {/each}
        </tbody>
    </table>
</div>

<div class="block lg:hidden divide-y divide-gray-200 dark:divide-gray-800 border-t border-gray-200 dark:border-gray-800">
    {#each items as item, index}
        <div class="p-4 transition {getRowClass(item)}">
            
            <div class="flex gap-2 items-center justify-between mb-3 w-full">
                <input 
                    type="text" 
                    bind:value={item.name} 
                    class="font-semibold text-sm border-transparent focus:ring-1 focus:ring-blue-500 rounded p-1.5 -ml-1 flex-1 text-gray-900 dark:text-white {logic.checkIsComplete(item) ? 'bg-transparent' : 'bg-black/5 dark:bg-white/5'}" 
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
                    ✎ Edit
                </Button>
            </div>
            
        </div>
    {/each}
</div>