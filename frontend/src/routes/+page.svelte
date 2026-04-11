<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { token, currentUser } from '$lib/stores';
    import { goto } from '$app/navigation';

    let isLogin = $state(true);
    let email = $state('');
    let name = $state('');
    let password = $state('');
    let errorMessage = $state('');
    let isLoading = $state(false); // NEU: Ladezustand

    // NEU: Sauberes Umschalten zwischen Login und Register
    function toggleMode() {
        isLogin = !isLogin;
        errorMessage = ''; // Fehler beim Wechseln verstecken
        password = ''; // Aus Sicherheitsgründen Passwort-Feld leeren
    }

    async function handleSubmit(event: Event) {
        event.preventDefault(); 
        
        errorMessage = '';
        isLoading = true;

        try {
            if (!isLogin) {
                await apiFetch('/users/', {
                    method: 'POST',
                    body: JSON.stringify({ email, name, password })
                });
                isLogin = true; 
            }

            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const tokenResponse = await apiFetch('/users/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            // 3. Token setzen
            $token = tokenResponse.access_token;

            // 4. User-Daten laden
            const userData = await apiFetch('/users/me');
            $currentUser = userData;

            // 5. Erfolgreich -> Weiterleitung
            goto('/add-receipt'); 

        } catch (error: any) {
            errorMessage = error.message;
        } finally {
            isLoading = false; // Wird auch ausgeführt, wenn ein Fehler auftritt
        }
    }
</script>

<main class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        
        <h1 class="text-2xl font-bold text-center mb-6">
            {isLogin ? 'Login' : 'Registrieren'}
        </h1>
        
        {#if errorMessage}
            <div class="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
                {errorMessage}
            </div>
        {/if}

        <form onsubmit={handleSubmit} class="space-y-4">
            
            {#if !isLogin}
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Dein Name</label>
                    <input id="name" type="text" bind:value={name} required disabled={isLoading} class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border disabled:bg-gray-100 disabled:text-gray-500" />
                </div>
            {/if}

            <div>
                <label for="email" class="block text-sm font-medium text-gray-700">E-Mail</label>
                <input id="email" type="email" bind:value={email} required disabled={isLoading} class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border disabled:bg-gray-100 disabled:text-gray-500" />
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                <input id="password" type="password" bind:value={password} required disabled={isLoading} class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border disabled:bg-gray-100 disabled:text-gray-500" />
            </div>

            <button 
                type="submit" 
                disabled={isLoading}
                class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-bold py-2 px-4 rounded transition flex justify-center items-center gap-2"
            >
                {#if isLoading}
                    <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Lädt...
                {:else}
                    {isLogin ? 'Einloggen' : 'Registrieren'}
                {/if}
            </button>
        </form>

        <div class="mt-4 text-center">
            <button 
                type="button" 
                class="text-sm text-blue-500 hover:underline disabled:text-gray-400 disabled:no-underline" 
                onclick={toggleMode}
                disabled={isLoading}
            >
                {isLogin ? 'Noch keinen Account? Registrieren' : 'Schon einen Account? Einloggen'}
            </button>
        </div>

    </div>
</main>