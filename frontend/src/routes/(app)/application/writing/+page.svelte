<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let essayPrompt = $state("Personal Statement");
  let personalStatement = $state("");
  let additionalInfo = $state("");
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let saveError = $state<string | null>(null);

  onMount(async () => {
    const profile = await loadProfile();
    if (!profile) return;
    essayPrompt = profile.essay_prompt ?? essayPrompt;
    personalStatement = profile.writing_sample ?? personalStatement;
    additionalInfo = profile.additional_info ?? additionalInfo;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("writing", {
        essay_prompt: essayPrompt,
        writing_sample: personalStatement,
        additional_info: additionalInfo
      });
      saveSuccess = true;
      setTimeout(() => goto("/dashboard"), 1200);
    } catch (err) {
      saveError = err instanceof Error ? err.message : "Could not save your details. Please try again.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="step-page">
  <h3 class="step-title">Writing & Personal Statement</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Writing section saved! Application sections complete. Redirecting to Dashboard...
    </div>
  {/if}

  {#if saveError}
    <div class="alert-error" role="alert">
      {saveError}
    </div>
  {/if}

  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
    <div class="form-group">
      <label for="essayPrompt">Select Essay Topic</label>
      <span class="field-desc">Choose the primary prompt or topic for your personal statement essay.</span>
      <select id="essayPrompt" required bind:value={essayPrompt}>
        <option value="Personal Statement">Personal Statement / Career Goals</option>
        <option value="Challenge Overcome">Share a time you faced a significant challenge and how you overcame it</option>
        <option value="Community Impact">How do you plan to impact your community through your studies?</option>
        <option value="Open Prompt">Topic of your choice</option>
      </select>
    </div>

    <div class="form-group">
      <label for="personalStatement">Personal Statement Essay</label>
      <span class="field-desc">Compose your personal essay (recommended length: 250 - 650 words).</span>
      <textarea
        id="personalStatement"
        rows="8"
        placeholder="Write your essay here..."
        required
        bind:value={personalStatement}
      ></textarea>
    </div>

    <div class="form-group">
      <label for="additionalInfo">Additional Information / Special Circumstances (Optional)</label>
      <span class="field-desc">Provide any additional context regarding your education journey or special circumstances.</span>
      <textarea
        id="additionalInfo"
        rows="3"
        placeholder="Additional information or details for admissions..."
        bind:value={additionalInfo}
      ></textarea>
    </div>

    <button type="submit" class="btn-save" disabled={isSaving}>
      {isSaving ? "Saving..." : "Save & Finish Profile"}
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

  .step-page form select,
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
  .step-page form textarea::placeholder {
    color: #94a3b8;
    font-style: italic;
    opacity: 0.9;
  }

  /* Explicit Blue focus border */
  .step-page form select:focus,
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
