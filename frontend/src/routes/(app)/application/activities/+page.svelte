<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let activityName = $state("");
  let rolePosition = $state("");
  let description = $state("");
  let honorsAwards = $state("");
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let saveError = $state<string | null>(null);

  onMount(async () => {
    const profile = await loadProfile();
    if (!profile) return;
    activityName = profile.activity_name ?? activityName;
    rolePosition = profile.activity_role ?? rolePosition;
    description = profile.activity_description ?? description;
    honorsAwards = profile.honors_awards ?? honorsAwards;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("activities", {
        activity_name: activityName,
        activity_role: rolePosition,
        activity_description: description,
        honors_awards: honorsAwards
      });
      saveSuccess = true;
      setTimeout(() => goto("/application/writing"), 1200);
    } catch (err) {
      saveError = err instanceof Error ? err.message : "Could not save your details. Please try again.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="step-page">
  <h3 class="step-title">Activities & Experiences</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Activities saved! Redirecting to Writing & Statement...
    </div>
  {/if}

  {#if saveError}
    <div class="alert-error" role="alert">
      {saveError}
    </div>
  {/if}

  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
    <div class="form-grid">
      <div class="form-group">
        <label for="activityName">Activity / Organization Name</label>
        <span class="field-desc">Name of club, organization, volunteer group, or sports team.</span>
        <input
          id="activityName"
          type="text"
          placeholder="Activity / Organization Name"
          required
          bind:value={activityName}
        />
      </div>

      <div class="form-group">
        <label for="rolePosition">Role / Leadership Position</label>
        <span class="field-desc">Your official position or role within the activity.</span>
        <input
          id="rolePosition"
          type="text"
          placeholder="Role / Leadership Position"
          required
          bind:value={rolePosition}
        />
      </div>
    </div>

    <div class="form-group">
      <label for="description">Activity Description & Impact</label>
      <span class="field-desc">Describe your responsibilities, key achievements, and time dedicated.</span>
      <textarea
        id="description"
        rows="4"
        placeholder="Activity Description & Impact"
        required
        bind:value={description}
      ></textarea>
    </div>

    <div class="form-group">
      <label for="honorsAwards">Honors & Awards (Optional)</label>
      <span class="field-desc">Any awards, recognitions, or prizes received for this activity.</span>
      <input
        id="honorsAwards"
        type="text"
        placeholder="Honors & Awards"
        bind:value={honorsAwards}
      />
    </div>

    <button type="submit" class="btn-save" disabled={isSaving}>
      {isSaving ? "Saving..." : "Save & Continue"}
    </button>
  </form>
</div>

<style>
  .step-page {
    text-align: left;
    max-width: 640px;
  }
  .step-title {
    margin-bottom: 1.75rem;
    font-size: 1.85rem;
    font-weight: 700;
    color: #1a2b4a;
  }

  .alert-success {
    background-color: #e6fffa;
    border: 1px solid #319795;
    color: #234e52;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }

  .alert-error {
    background-color: #fff5f5;
    border: 1px solid #feb2b2;
    color: #9b2c2c;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }

  .step-page form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }

  @media (max-width: 580px) {
    .form-grid {
      grid-template-columns: 1fr;
    }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .form-group label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a2b4a;
  }

  .field-desc {
    font-size: 0.825rem;
    color: #64748b;
    margin-bottom: 0.25rem;
    line-height: 1.35;
  }

  .step-page form input,
  .step-page form textarea {
    padding: 0.75rem 1rem;
    border: 1px solid #cbd5e0;
    border-radius: 8px;
    font-size: 1rem;
    color: #2d3748;
    background-color: #ffffff;
    font-family: inherit;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  /* Placeholder styling */
  .step-page form input::placeholder,
  .step-page form textarea::placeholder {
    color: #94a3b8;
    font-style: italic;
    opacity: 0.9;
  }

  /* Explicit Blue focus border */
  .step-page form input:focus,
  .step-page form textarea:focus {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
  }

  .btn-save {
    margin-top: 1.5rem;
    padding: 0.75rem 2rem;
    background-color: #2563eb;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    width: fit-content;
    border-radius: 50px;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  }

  .btn-save:hover:not(:disabled) {
    background-color: #1d4ed8;
    transform: translateY(-1px);
  }

  .btn-save:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
</style>
