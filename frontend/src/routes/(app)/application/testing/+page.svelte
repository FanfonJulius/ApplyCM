<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let oLevelPasses = $state("");
  let aLevelPoints = $state("");
  let englishTestType = $state("");
  let testScore = $state("");
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let saveError = $state<string | null>(null);

  onMount(async () => {
    const profile = await loadProfile();
    if (!profile) return;
    oLevelPasses = profile.o_level_passes ?? oLevelPasses;
    aLevelPoints = profile.a_level_points ?? aLevelPoints;
    englishTestType = profile.english_test_type ?? englishTestType;
    testScore = profile.english_test_score ?? testScore;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("testing", {
        o_level_passes: oLevelPasses,
        a_level_points: aLevelPoints,
        english_test_type: englishTestType,
        english_test_score: testScore
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
  <h3 class="step-title">Standardized Testing & GCE Grades</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Testing details saved! Redirecting to Activities...
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
        <label for="oLevelPasses">GCE Ordinary Level Passes</label>
        <input
          id="oLevelPasses"
          type="text"
          placeholder="e.g. 9 Passes (5 A Grades, 4 B Grades)"
          required
          bind:value={oLevelPasses}
        />
      </div>

      <div class="form-group">
        <label for="aLevelPoints">GCE Advanced Level Points / Grades</label>
        <input
          id="aLevelPoints"
          type="text"
          placeholder="e.g. 15 Points (A, A, B)"
          required
          bind:value={aLevelPoints}
        />
      </div>
    </div>

    <div class="form-grid">
      <div class="form-group">
        <label for="englishTestType">English Proficiency Test (Optional)</label>
        <select id="englishTestType" bind:value={englishTestType}>
          <option value="" selected>-- None / Not Applicable --</option>
          <option value="IELTS">IELTS Academic</option>
          <option value="TOEFL">TOEFL iBT</option>
          <option value="Duolingo">Duolingo English Test</option>
          <option value="GCE_English">GCE O-Level English Grade A/B</option>
        </select>
      </div>

      <div class="form-group">
        <label for="testScore">Score / Certificate Link</label>
        <input
          id="testScore"
          type="text"
          placeholder="e.g. Band 7.5 / 105 TOEFL / Grade A"
          bind:value={testScore}
        />
      </div>
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
    gap: 0.4rem;
  }

  .form-group label {
    font-size: 0.9rem;
    font-weight: 600;
    color: #4a5568;
  }

  .step-page form input,
  .step-page form select {
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

  /* Explicit Blue focus border */
  .step-page form input:focus,
  .step-page form select:focus {
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
