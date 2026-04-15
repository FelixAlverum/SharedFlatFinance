<script lang="ts">
    import type { Snippet } from 'svelte';
    interface Props {
        children: Snippet;
        class?: string;
    }
    let { children, class: className = 'p-6 sm:p-8' }: Props = $props();
</script>

<div class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl shadow-xl {className}">
    {@render children()}
</div>