<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let secondarySchool = $state("");
  let ordinaryLevelSlipImage = $state("");
  let advancedLevelSlipImage = $state("");
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let saveError = $state<string | null>(null);

  onMount(async () => {
    const profile = await loadProfile();
    if (!profile) return;
    secondarySchool = profile.secondary_school ?? secondarySchool;
    ordinaryLevelSlipImage = profile.o_level_slip_url ?? ordinaryLevelSlipImage;
    advancedLevelSlipImage = profile.a_level_slip_url ?? advancedLevelSlipImage;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("education", {
        secondary_school: secondarySchool,
        o_level_slip_url: ordinaryLevelSlipImage,
        a_level_slip_url: advancedLevelSlipImage
      });
      saveSuccess = true;
      setTimeout(() => goto("/application/activities"), 1200);
    } catch (err) {
      saveError = err instanceof Error ? err.message : "Could not save your details. Please try again.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="step-page">
  <h3 class="step-title">Education History</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Education details saved! Redirecting to Activities & Experiences...
    </div>
  {/if}

  {#if saveError}
    <div class="alert-error" role="alert">
      {saveError}
    </div>
  {/if}

  <form onsubmit={(event) => { event.preventDefault(); handleSubmit(); }}>
    <div class="form-group">
      <label for="secondarySchool">Secondary School Name</label>
      <span class="field-desc">Full official name of your secondary or high school institution.</span>
      <input
        id="secondarySchool"
        type="text"
        placeholder="Secondary School Name"
        required
        bind:value={secondarySchool}
      />
    </div>

    <div class="form-group">
      <label for="ordinaryLevelSlipImage">Ordinary Level Result Slip (Image URL / Path)</label>
      <span class="field-desc">Uploaded image link or document reference for GCE Ordinary Level results.</span>
      <input
        id="ordinaryLevelSlipImage"
        type="text"
        placeholder="Ordinary Level Result Slip URL"
        required
        bind:value={ordinaryLevelSlipImage}
      />
    </div>

    <div class="form-group">
      <label for="advancedLevelSlipImage">Advanced Level Result Slip (Image URL / Path)</label>
      <span class="field-desc">Uploaded image link or document reference for GCE Advanced Level results.</span>
      <input
        id="advancedLevelSlipImage"
        type="text"
        placeholder="Advanced Level Result Slip URL"
        required
        bind:value={advancedLevelSlipImage}
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

  .step-page form input {
    padding: 0.75rem 1rem;
    border: 1px solid #cbd5e0;
    border-radius: 8px;
    font-size: 1rem;
    color: #2d3748;
    background-color: #ffffff;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  /* Placeholder styling */
  .step-page form input::placeholder {
    color: #94a3b8;
    font-style: italic;
    opacity: 0.9;
  }

  /* Focus styling: Explicit Blue border instead of black */
  .step-page form input:focus {
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
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
  }

  .btn-save:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
</style>
