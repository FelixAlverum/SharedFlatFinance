<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { token, currentUser } from '$lib/stores';

    // NEU in Svelte 5: $state() macht die Variablen reaktiv!
    let isLogin = $state(true);
    let email = $state('');
    let name = $state('');
    let password = $state('');
    let errorMessage = $state('');

    // Wir übergeben das Event jetzt direkt in die Funktion
    async function handleSubmit(event: Event) {
        event.preventDefault(); // Verhindert, dass die Seite beim Klicken auf Submit neu lädt
        
        errorMessage = '';
        try {
            if (isLogin) {
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const response = await apiFetch('/users/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                $token = response.access_token;

            } else {
                await apiFetch('/users/', {
                    method: 'POST',
                    body: JSON.stringify({ email, name, password })
                });
                
                isLogin = true;
                await handleSubmit(event);
                return;
            }

            const userData = await apiFetch('/users/me');
            $currentUser = userData;

        } catch (error: any) {
            errorMessage = error.message;
        }
    }

    function logout() {
        $token = null;
        $currentUser = null;
    }
</script>

<main class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        
        {#if $currentUser}
            <div class="text-center">
                <h1 class="text-3xl font-bold mb-2">💸 WG Kasse</h1>
                <p class="text-green-600 font-semibold mb-6">Erfolgreich eingeloggt als {$currentUser.name}!</p>
                
                <button onclick={logout} class="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition">
                    Logout
                </button>
            </div>

        {:else}
            <h1 class="text-2xl font-bold text-center mb-6">{isLogin ? 'Login' : 'Registrieren'}</h1>
            
            {#if errorMessage}
                <div class="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
                    {errorMessage}
                </div>
            {/if}

            <form onsubmit={handleSubmit} class="space-y-4">
                
                {#if !isLogin}
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700">Dein Name</label>
                        <input id="name" type="text" bind:value={name} required class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border" />
                    </div>
                {/if}

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">E-Mail</label>
                    <input id="email" type="email" bind:value={email} required class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border" />
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                    <input id="password" type="password" bind:value={password} required class="mt-1 block w-full rounded border-gray-300 shadow-sm p-2 border" />
                </div>

                <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition">
                    {isLogin ? 'Einloggen' : 'Registrieren'}
                </button>
            </form>

            <div class="mt-4 text-center">
                <button class="text-sm text-blue-500 hover:underline" onclick={() => isLogin = !isLogin}>
                    {isLogin ? 'Noch keinen Account? Registrieren' : 'Schon einen Account? Einloggen'}
                </button>
            </div>
        {/if}
    </div>
</main>