<script lang="ts">
    import { appState } from '$lib/state.svelte';
    import { flip } from 'svelte/animate';
    import { fly } from 'svelte/transition';

    const styles = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-black',
        info: 'bg-blue-500 text-white'
    };
</script>

<div class="fixed bottom-4 right-4 z-100 flex flex-col gap-2 w-full max-w-xs pointer-events-none">
    {#each appState.toasts as toast (toast.id)}
        <div
            animate:flip={{ duration: 300 }}
            in:fly={{ y: 20, duration: 300 }}
            out:fly={{ x: 100, duration: 300 }}
            class="pointer-events-auto p-4 rounded-lg shadow-lg flex justify-between items-start gap-3 {styles[toast.type]}"
        >
            <p class="text-sm font-medium">{toast.message}</p>
            <button 
                onclick={() => appState.removeToast(toast.id)}
                class="hover:opacity-75 transition-opacity"
            >
                ✕
            </button>
        </div>
    {/each}
</div>