<script lang="ts">
    import { apiFetch } from '$lib/api';
    import { token, currentUser } from '$lib/stores';
    import { goto } from '$app/navigation';
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import { fade } from 'svelte/transition';

    let isLogin = $state(true);
    let email = $state('');
    let name = $state('');
    let password = $state('');
    let errorMessage = $state('');
    let isLoading = $state(false); 

    function toggleMode() {
        isLogin = !isLogin;
        errorMessage = ''; 
        password = '';
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

<main class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4 sm:p-8 transition-colors duration-200">
    <Card class="p-6 sm:p-8 w-full max-w-md">
        
        <div class="text-center mb-8">
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                {isLogin ? 'Willkommen zurück' : 'Account erstellen'}
            </h1>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {isLogin ? 'Logge dich in deine WG-Kasse ein' : 'Registriere dich für deine WG-Kasse'}
            </p>
        </div>
        
        {#if errorMessage}
            <div transition:fade={{ duration: 150 }} class="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6 text-sm border border-red-200 dark:border-red-800 flex items-start gap-3">
                <span class="text-lg leading-none">⚠️</span>
                <span>{errorMessage}</span>
            </div>
        {/if}

        <form onsubmit={handleSubmit} class="space-y-5">
            {#if !isLogin}
                <div transition:fade={{ duration: 150 }}>
                    <Input 
                        id="name" 
                        label="Dein Name" 
                        bind:value={name} 
                        required 
                        disabled={isLoading} 
                        placeholder="z.B. Alex" 
                    />
                </div>
            {/if}

            <Input 
                id="email" 
                type="email" 
                label="E-Mail" 
                bind:value={email} 
                required 
                disabled={isLoading} 
                placeholder="name@beispiel.de" 
                autocomplete="email"
            />

            <Input 
                id="password" 
                type="password" 
                label="Passwort" 
                bind:value={password} 
                required 
                disabled={isLoading} 
                placeholder="••••••••" 
                autocomplete={isLogin ? "current-password" : "new-password"}
            />

            <div class="pt-2">
                <Button type="submit" {isLoading} class="w-full py-3">
                    {isLogin ? 'Sicher einloggen' : 'Account erstellen'}
                </Button>
            </div>
        </form>

        <div class="mt-6 pt-6 border-t border-gray-100 dark:border-gray-700 text-center">
            <Button variant="ghost" type="button" disabled={isLoading} onclick={toggleMode}>
                {isLogin ? 'Noch keinen Account? Hier registrieren' : 'Schon einen Account? Hier einloggen'}
            </Button>
        </div>

    </Card>
</main>