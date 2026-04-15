<script lang="ts">
    import type { Snippet } from 'svelte';
    import type { HTMLButtonAttributes } from 'svelte/elements';
    import Spinner from './Spinner.svelte'; // Pfad ggf. anpassen

    interface Props extends HTMLButtonAttributes {
        children: Snippet;
        variant?: 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost';
        isLoading?: boolean; // <-- NEU
    }
    
    let { 
        children, 
        variant = 'primary', 
        isLoading = false,
        class: className = '', 
        disabled, // Fangen wir extra ab, um es mit isLoading zu kombinieren
        ...rest
    }: Props = $props();

    const baseClasses = "flex items-center justify-center gap-2 px-4 py-2 text-sm font-bold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-900";
    
    const variants = {
        primary: "bg-blue-600 hover:bg-blue-700 text-white shadow-sm",
        secondary: "bg-gray-100 hover:bg-gray-200 text-gray-800 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700",
        destructive: "bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 dark:bg-red-900/20 dark:border-red-800/50 dark:text-red-400 dark:hover:bg-red-900/40",
        outline: "bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800",
        ghost: "bg-transparent text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/30 shadow-none" // Gut für den Toggle-Button
    };
</script>

<button 
    class="{baseClasses} {variants[variant]} {className}" 
    disabled={isLoading || disabled} 
    {...rest}
>
    {#if isLoading}
        <Spinner class="h-4 w-4" />
    {/if}
    {@render children()}
</button>