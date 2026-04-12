<script lang="ts">
    import { fade, scale } from 'svelte/transition';

    interface Props {
        isOpen: boolean;
        title?: string;
        message?: string;
        confirmText?: string;
        cancelText?: string;
        isDestructive?: boolean;
        onConfirm: () => void;
        onCancel: () => void;
    }

    let {
        isOpen,
        title = 'Bitte bestätigen',
        message = 'Bist du sicher, dass du diese Aktion ausführen möchtest?',
        confirmText = 'Ja, weiter',
        cancelText = 'Abbrechen',
        isDestructive = true,
        onConfirm,
        onCancel
    }: Props = $props();

    function handleKeydown(event: KeyboardEvent) {
        if (isOpen && event.key === 'Escape') {
            onCancel();
        }
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if isOpen}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 backdrop-blur-sm p-4" 
        transition:fade={{ duration: 150 }}
        onclick={onCancel} 
        role="presentation"
    >
        <div 
            class="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden" 
            transition:scale={{ duration: 150, start: 0.95 }}
            onclick={(e) => e.stopPropagation()} 
            role="dialog"
            aria-modal="true"
            tabindex="-1"
        >
            <div class="p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{title}</h3>
                <p class="text-gray-600 text-sm mb-6 leading-relaxed">{message}</p>
                
                <div class="flex gap-3 justify-end">
                    <button 
                        onclick={onCancel}
                        class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-lg transition"
                    >
                        {cancelText}
                    </button>
                    <button 
                        onclick={onConfirm}
                        class="px-4 py-2 font-semibold rounded-lg transition text-white
                        {isDestructive ? 'bg-red-500 hover:bg-red-600 shadow-sm shadow-red-500/20' : 'bg-blue-600 hover:bg-blue-700 shadow-sm shadow-blue-600/20'}"
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}