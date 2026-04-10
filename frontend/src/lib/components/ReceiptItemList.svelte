<script lang="ts">
    import type { Item, User } from '$lib/types';
    import {toggleUser, toggleAll, isUserActive, checkIsComplete} from '$lib/receipt-logic';

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
</script>

<div class="hidden lg:block overflow-x-auto">
    <table class="w-full text-left border-collapse min-w-[800px]">
        <thead>
            <tr class="bg-gray-100 text-gray-600 text-xs uppercase tracking-wider">
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
        <tbody class="divide-y divide-gray-200">
            {#each items as item, index}
                <tr class="hover:bg-gray-50 transition {checkIsComplete(item) ? '' : 'bg-yellow-50/30'}">
                    <td class="p-2">
                        <input 
                            type="text" 
                            bind:value={item.name} 
                            class="w-full text-sm border-transparent focus:border-blue-500 rounded p-1 {checkIsComplete(item) ? 'bg-transparent' : 'bg-yellow-50/50'}" 
                        />
                    </td>
                    <td class="p-2 text-right align-middle">
                        <div class="font-bold text-gray-800 text-sm whitespace-nowrap">{item.total_price.toFixed(2)}€</div>
                    </td>
                    {#each users as user}
                        <td class="p-2 text-center">
                            <button 
                                onclick={() => toggleUser(item, user.email)} 
                                class="w-full px-2 py-1.5 text-xs font-bold rounded transition border {isUserActive(item, user.email) ? 'bg-blue-500 text-white border-blue-500' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-300 hover:bg-blue-50'}"
                            >
                                {user.name.substring(0, 6)}
                            </button>
                        </td>
                    {/each}
                    <td class="p-2 text-center">
                        <button onclick={() => toggleAll(item, users)} class="w-full px-2 py-1.5 text-xs font-bold rounded transition border bg-white text-gray-600 border-gray-300 hover:border-blue-300 hover:bg-blue-50">Alle</button>
                    </td>
                    <td class="p-2 text-center">
                        <button onclick={() => openSplitModal(index)} class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded">✎</button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

<div class="block lg:hidden divide-y divide-gray-200">
    {#each items as item, index}
        <div class="p-4 bg-white {checkIsComplete(item) ? '' : 'bg-yellow-50/30'}">
            <div class="flex gap-2 items-center justify-between mb-3 w-full">
                <input 
                    type="text" 
                    bind:value={item.name} 
                    class="font-semibold text-sm border-transparent focus:border-blue-500 rounded p-1 -ml-1 flex-1 {checkIsComplete(item) ? 'bg-transparent' : 'bg-yellow-50/50'}" 
                />
                <span class="font-bold text-gray-800 whitespace-nowrap ml-2">{item.total_price.toFixed(2)}€</span>
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
                <button onclick={() => toggleAll(item, users)} class="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-bold rounded border border-gray-300">Alle</button>
                <button onclick={() => openSplitModal(index)} class="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-bold rounded border border-gray-300">✎ Edit</button>
            </div>
        </div>
    {/each}
</div>