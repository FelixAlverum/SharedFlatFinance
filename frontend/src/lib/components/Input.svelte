<script lang="ts">
    interface Props {
        id: string;
        label: string;
        value: string;
        type?: 'text' | 'email' | 'password' | 'number';
        required?: boolean;
        disabled?: boolean;
    }
    let { id, label, value = $bindable(), type = 'text', required = false, disabled = false }: Props = $props();
</script>

<div>
    <label for={id} class="block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
    <input 
        {id} 
        {type} 
        bind:value 
        {required} 
        {disabled} 
        class="mt-1 block w-full rounded border-gray-300 dark:border-gray-700 shadow-sm p-2 border bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50" 
    />
</div>