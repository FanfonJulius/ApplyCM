<script lang="ts">
    import { API_BASE_URL } from "$lib/config";
    let email = $state("");
    let password = $state("");
    let isLoading = $state(false);
    let success = $state(false);
    let errorMessage = $state("");

    async function login() {
        errorMessage = "";
        isLoading = true;
        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || "Invalid email or password");
            }

            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            success = true;
            setTimeout(() => {
                window.location.href = "/dashboard";
            }, 900);
        } catch (error: any) {
            console.error(error);
            errorMessage =
                error.message || "Invalid email or password. Please try again.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="page-background">
    <div class="auth-card">
        <h2 class="auth-card-title">Login to ApplyCM</h2>
        <form
            onsubmit={(event) => {
                event.preventDefault();
                login();
            }}
        >
            <div class="form-group">
                <label for="email">Email Address</label>
                <input
                    type="email"
                    id="email"
                    required
                    bind:value={email}
                    disabled={isLoading}
                />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <div class="password-container">
                    <input
                        id="password"
                        type="password"
                        required
                        bind:value={password}
                        disabled={isLoading}
                    />
                </div>
            </div>
            {#if errorMessage}
                <p class="error-message">{errorMessage}</p>
            {/if}
            <button type="submit" class="btn-submit" disabled={isLoading}
                >{#if isLoading}Logging in...{:else}Login{/if}</button
            >
        </form>
        <p>Don't have an account? <a href="/signup">Sign up</a></p>
    </div>
    {#if success}
        <div class="alert-success" role="status">✓ Logged in successfully</div>
    {/if}
</div>

<style>
    .page-background {
        min-height: 100vh;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(
            circle at 50% 20%,
            #234c8e 0%,
            #142a51 45%,
            #050a14 100%
        );
        padding: 2rem 1rem;
    }

    .auth-card {
        max-width: 400px;
        width: 100%;
        margin: 0 auto;
        padding: 2rem;
        background: #ffffff;
        border: 1px solid #96bef3;
        border-radius: 40px;
        border-width: 0.5px;
        box-shadow:
            0 8px 24px rgba(51, 132, 238, 0.35),
            0 2px 6px rgba(0, 0, 0, 0.3);
        transition:
            box-shadow 0.5s ease-in-out,
            transform 0.5s ease-in-out;
    }
    .auth-card:hover {
        box-shadow:
            0 20px 40px rgba(0, 0, 0, 0.45),
            0 8px 16px rgba(51, 132, 238, 0.4);
        transform: translateY(-6px);
    }
    .auth-card-title {
        text-align: center;
        margin-bottom: 1.5rem;
        color: #2b6cb0;
    }
    .form-group {
        margin-bottom: 1.5rem;
        text-align: left;
    }
    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
    }
    .form-group input {
        width: 95%;
        padding: 0.5rem;
        border: 1px solid #cbd5e0;
        border-radius: 50px;
    }
    .btn-submit {
        width: 100%;
        padding: 0.75rem;
        background-color: #38a169;
        color: white;
        border: none;
        border-radius: 50px;
        cursor: pointer;
    }
    .password-container {
        position: relative;
    }
    .password-container input {
        padding-right: 0.5rem;
    }
    .error-message {
        color: #e53e3e;
        font-size: 0.875rem;
        margin: -0.5rem 0 1rem;
        text-align: left;
    }
</style>
