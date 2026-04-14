<script lang="ts">
    import type { Snippet } from 'svelte';
    import type { HTMLButtonAttributes } from 'svelte/elements'; // <-- NEU: Importiert alle Standard-Attribute

    interface Props extends HTMLButtonAttributes {
        children: Snippet;
        variant?: 'primary' | 'secondary' | 'destructive' | 'outline';
    }
    
    let { 
        children, 
        variant = 'primary', 
        class: className = '', 
        ...rest
    }: Props = $props();

    const baseClasses = "flex items-center justify-center gap-2 px-4 py-2 text-sm font-bold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed";
    
    const variants = {
        primary: "bg-blue-600 hover:bg-blue-700 text-white shadow",
        secondary: "bg-gray-100 hover:bg-gray-200 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
        destructive: "bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 dark:bg-red-900/20 dark:border-red-800",
        outline: "bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300"
    };
</script>

<button class="{baseClasses} {variants[variant]} {className}" {...rest}>
    {@render children()}
</button>