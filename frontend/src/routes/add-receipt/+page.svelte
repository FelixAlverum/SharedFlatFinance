<script lang="ts">
    import { apiFetch } from '$lib/api';

    // State for the file upload
    let files: FileList | null = $state(null);
    let isLoading = $state(false);
    let errorMessage = $state('');

    // State for the parsed data returned from the backend
    let parsedData: any = $state(null);

    // --- 1. UPLOAD & PARSE ---
    async function handleUpload(event: Event) {
        event.preventDefault();
        if (!files || files.length === 0) return;

        isLoading = true;
        errorMessage = '';
        parsedData = null;

        try {
            const formData = new FormData();
            formData.append('file', files[0]);

            // Calls your FastAPI /api/upload-receipt endpoint
            const response = await apiFetch('/upload-receipt', {
                method: 'POST',
                body: formData
            });

            parsedData = response;
        } catch (error: any) {
            errorMessage = error.message || 'Failed to upload receipt.';
        } finally {
            isLoading = false;
        }
    }

    // --- 2. DELETE AN ITEM ROW ---
    function removeItem(index: number) {
        parsedData.items.splice(index, 1);
    }
</script>

<main class="max-w-4xl mx-auto p-4 md:p-8">
    <h1 class="text-3xl font-bold mb-6">🧾 Add Receipt</h1>

    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
        <form onsubmit={handleUpload} class="flex flex-col md:flex-row gap-4 items-end">
            <div class="flex-1 w-full">
                <label for="receipt" class="block text-sm font-medium text-gray-700 mb-2">Upload REWE PDF</label>
                <input 
                    id="receipt" 
                    type="file" 
                    accept=".pdf" 
                    bind:files={files}
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" 
                    required 
                />
            </div>
            <button 
                type="submit" 
                disabled={isLoading || !files}
                class="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-md transition disabled:bg-gray-400"
            >
                {isLoading ? 'Parsing...' : 'Upload & Parse'}
            </button>
        </form>

        {#if errorMessage}
            <div class="mt-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
                {errorMessage}
            </div>
        {/if}
    </div>

    {#if parsedData}
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="p-6 border-b border-gray-200 bg-gray-50">
                <h2 class="text-xl font-bold text-gray-800">Review Items</h2>
                <p class="text-sm text-gray-500">Correct any scanning errors before saving.</p>
                
                <div class="mt-4">
                    <label for="title" class="block text-sm font-medium text-gray-700">Receipt Title</label>
                    <input id="title" type="text" bind:value={parsedData.title} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border" />
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-100 text-gray-600 text-sm uppercase tracking-wider">
                            <th class="p-4 font-semibold">Item Name</th>
                            <th class="p-4 font-semibold w-24">Qty</th>
                            <th class="p-4 font-semibold w-32">Unit Price (€)</th>
                            <th class="p-4 font-semibold w-32">Total (€)</th>
                            <th class="p-4 font-semibold w-16 text-center">Action</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        {#each parsedData.items as item, index}
                            <tr class="hover:bg-gray-50 transition">
                                <td class="p-2">
                                    <input type="text" bind:value={item.name} class="w-full border-transparent focus:border-blue-500 focus:ring-0 rounded p-2" />
                                </td>
                                <td class="p-2">
                                    <input type="number" step="0.1" bind:value={item.quantity} class="w-full border-transparent focus:border-blue-500 focus:ring-0 rounded p-2" />
                                </td>
                                <td class="p-2">
                                    <input type="number" step="0.01" bind:value={item.unit_price} class="w-full border-transparent focus:border-blue-500 focus:ring-0 rounded p-2" />
                                </td>
                                <td class="p-2">
                                    <input type="number" step="0.01" bind:value={item.total_price} class="w-full border-transparent focus:border-blue-500 focus:ring-0 rounded p-2 font-semibold" />
                                </td>
                                <td class="p-2 text-center">
                                    <button onclick={() => removeItem(index)} class="text-red-500 hover:text-red-700 p-2 rounded hover:bg-red-50" title="Remove item">
                                        🗑️
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>

            <div class="p-6 bg-gray-50 border-t border-gray-200 flex justify-end">
                <button class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-md transition shadow-sm">
                    💾 Save to Database
                </button>
            </div>
        </div>
    {/if}
</main>