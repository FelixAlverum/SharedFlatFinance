<script lang="ts">
    import type { HTMLInputAttributes } from 'svelte/elements';

    interface Props extends HTMLInputAttributes {
        id: string;
        label: string;
        value: string | number; // Bindable
    }

    let { 
        id, 
        label, 
        value = $bindable(), 
        class: className = '',
        ...rest // Fängt placeholder, required, disabled, type etc. ab
    }: Props = $props();
</script>

<div class={className}>
    <label for={id} class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        {label}
    </label>
    <input 
        {id} 
        bind:value 
        class="block w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 p-2.5 transition-colors disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:text-gray-500 dark:disabled:text-gray-400" 
        {...rest} 
    />
</div>