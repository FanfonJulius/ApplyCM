<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/state";
    import type { ProfileSection } from "$lib/api/profile";
    import { isSectionComplete, loadProfile, profileState } from "$lib/stores/profile.svelte";

    let { children } = $props();

    const SECTIONS: { key: ProfileSection; label: string; href: string }[] = [
        { key: "profile", label: "1. Personal Details", href: "/application/profile" },
        { key: "contact", label: "2. Contact Details", href: "/application/contact" },
        { key: "education", label: "3. Education History", href: "/application/education" },
        { key: "activities", label: "4. Activities & Experiences", href: "/application/activities" },
        { key: "writing", label: "5. Writing & Statement", href: "/application/writing" },
    ];

    onMount(() => {
        loadProfile();
    });
</script>

<div class="application-layout">
    <aside class="sub-nav">
        <h3>Shared Profile</h3>
        <ul>
            {#each SECTIONS as item}
                {@const active = page.url.pathname === item.href}
                {@const complete = isSectionComplete(item.key)}
                <li>
                    <a href={item.href} class:active>
                        <span>{item.label}</span>
                        {#if complete}
                            <span class="badge-complete" title="Completed">✓</span>
                        {/if}
                    </a>
                </li>
            {/each}
        </ul>
    </aside>
    <section class="step-content">
        {#if profileState.error}
            <div class="load-error" role="alert">
                We couldn't load your saved profile: {profileState.error}
            </div>
        {/if}
        {@render children()}
    </section>
</div>

<style>
    .load-error {
        background-color: #fff5f5;
        border: 1px solid #feb2b2;
        color: #9b2c2c;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    .application-layout {
        display: flex;
        gap: 2rem;
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        max-width: 1080px;
        margin: 0 auto;
    }
    .sub-nav {
        width: 240px;
        flex-shrink: 0;
        border-right: 1px solid #e2e8f0;
        padding-right: 1.5rem;
    }
    .sub-nav h3 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a2b4a;
        margin-bottom: 1.25rem;
    }
    .sub-nav ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }
    .sub-nav ul li a {
        text-decoration: none;
        color: #4a5568;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.65rem 0.85rem;
        border-radius: 8px;
        font-size: 0.925rem;
        font-weight: 500;
        transition: background-color 0.15s ease, color 0.15s ease;
    }
    .sub-nav ul li a:hover {
        background-color: #f1f5f9;
        color: #2563eb;
    }
    .sub-nav ul li a.active {
        background-color: #eff6ff;
        color: #2563eb;
        font-weight: 600;
    }
    .badge-complete {
        background-color: #2563eb;
        color: white;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .step-content {
        flex: 1;
        min-width: 0;
    }

    @media (max-width: 768px) {
        .application-layout {
            flex-direction: column;
            gap: 1.5rem;
        }
        .sub-nav {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid #e2e8f0;
            padding-right: 0;
            padding-bottom: 1rem;
        }
    }
</style>
