<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let address = $state("");
  let city = $state("");
  let region = $state("");
  let emergencyName = $state("");
  let emergencyPhone = $state("");
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let saveError = $state<string | null>(null);

  const CAMEROON_REGIONS = [
    "Adamawa",
    "Centre",
    "East",
    "Far North",
    "Littoral",
    "North",
    "Northwest",
    "South",
    "Southwest",
    "West"
  ];

  onMount(async () => {
    const profile = await loadProfile();
    if (!profile) return;
    address = profile.address ?? address;
    city = profile.city ?? city;
    region = profile.region ?? region;
    emergencyName = profile.emergency_contact_name ?? emergencyName;
    emergencyPhone = profile.emergency_contact_phone ?? emergencyPhone;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("contact", {
        address: address,
        city: city,
        region: region,
        emergency_contact_name: emergencyName,
        emergency_contact_phone: emergencyPhone
      });
      saveSuccess = true;
      setTimeout(() => goto("/application/education"), 1200);
    } catch (err) {
      saveError = err instanceof Error ? err.message : "Could not save your details. Please try again.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="step-page">
  <h3 class="step-title">Contact & Address Information</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Contact information saved! Redirecting to Education History...
    </div>
  {/if}

  {#if saveError}
    <div class="alert-error" role="alert">
      {saveError}
    </div>
  {/if}

  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
    <div class="form-group">
      <label for="address">Permanent Street Address</label>
      <span class="field-desc">Provide your residential street address or quarter location.</span>
      <input
        id="address"
        type="text"
        placeholder="Permanent Street Address"
        required
        bind:value={address}
      />
    </div>

    <div class="form-grid">
      <div class="form-group">
        <label for="city">City / Town</label>
        <span class="field-desc">City or municipality where you currently reside.</span>
        <input
          id="city"
          type="text"
          placeholder="City / Town"
          required
          bind:value={city}
        />
      </div>

      <div class="form-group">
        <label for="region">Region / Province</label>
        <span class="field-desc">Administrative region of your address.</span>
        <select id="region" required bind:value={region}>
          <option value="" disabled selected>Select Region</option>
          {#each CAMEROON_REGIONS as reg}
            <option value={reg}>{reg}</option>
          {/each}
        </select>
      </div>
    </div>

    <h4 class="section-subtitle">Emergency Contact</h4>

    <div class="form-grid">
      <div class="form-group">
        <label for="emergencyName">Emergency Contact Name</label>
        <span class="field-desc">Full name of a parent, guardian, or trusted emergency contact.</span>
        <input
          id="emergencyName"
          type="text"
          placeholder="Emergency Contact Name"
          required
          bind:value={emergencyName}
        />
      </div>

      <div class="form-group">
        <label for="emergencyPhone">Emergency Contact Phone</label>
        <span class="field-desc">Telephone number for your emergency contact.</span>
        <input
          id="emergencyPhone"
          type="tel"
          placeholder="Emergency Contact Phone"
          required
          bind:value={emergencyPhone}
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
  .section-subtitle {
    margin-top: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2d3748;
    border-bottom: 1px solid #edf2f7;
    padding-bottom: 0.5rem;
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

  .step-page form select:invalid {
    color: #94a3b8;
    font-style: italic;
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
