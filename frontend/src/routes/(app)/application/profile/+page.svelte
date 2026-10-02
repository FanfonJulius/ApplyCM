<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { loadProfile, saveSection } from "$lib/stores/profile.svelte";

  let firstName = $state("");
  let lastName = $state("");
  let email = $state("");
  let phone = $state("");
  let declaredState = $state("");
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
    firstName = profile.first_name ?? firstName;
    lastName = profile.last_name ?? lastName;
    email = profile.email ?? email;
    phone = profile.phone ?? phone;
    declaredState = profile.declared_state ?? declaredState;
  });

  async function handleSubmit() {
    isSaving = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveSection("profile", {
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone,
        declared_state: declaredState
      });
      saveSuccess = true;
      setTimeout(() => goto("/application/contact"), 1200);
    } catch (err) {
      saveError = err instanceof Error ? err.message : "Could not save your details. Please try again.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="step-page">
  <h3 class="step-title">Personal Details</h3>

  {#if saveSuccess}
    <div class="alert-success" role="status">
      ✓ Personal details saved! Section completed. Redirecting to Contact Details...
    </div>
  {/if}

  {#if saveError}
    <div class="alert-error" role="alert">
      {saveError}
    </div>
  {/if}

  <form onsubmit={(event) => { event.preventDefault(); handleSubmit(); }}>
    <div class="form-grid">
      <div class="form-group">
        <label for="firstName">First Name</label>
        <span class="field-desc">Enter your official given name as shown on legal identity documents.</span>
        <input
          id="firstName"
          type="text"
          placeholder="First Name"
          required
          bind:value={firstName}
        />
      </div>

      <div class="form-group">
        <label for="lastName">Last Name</label>
        <span class="field-desc">Enter your official family name or surname.</span>
        <input
          id="lastName"
          type="text"
          placeholder="Last Name"
          required
          bind:value={lastName}
        />
      </div>
    </div>

    <div class="form-group">
      <label for="email">Email Address</label>
      <span class="field-desc">Primary email address for application updates and university correspondence.</span>
      <input
        id="email"
        type="email"
        placeholder="Email Address"
        required
        bind:value={email}
      />
    </div>

    <div class="form-group">
      <label for="phone">Phone Number</label>
      <span class="field-desc">Mobile telephone number including country code (+237).</span>
      <input
        id="phone"
        type="tel"
        placeholder="Phone Number"
        required
        bind:value={phone}
      />
    </div>

    <div class="form-group">
      <label for="declaredState">Declared State / Region</label>
      <span class="field-desc">Select your official region of origin or state of residence.</span>
      <select
        id="declaredState"
        required
        bind:value={declaredState}
      >
        <option value="" disabled selected>Select Declared State / Region</option>
        {#each CAMEROON_REGIONS as region}
          <option value={region}>{region}</option>
        {/each}
      </select>
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
  .step-page form select {
    padding: 0.75rem 1rem;
    border: 1px solid #cbd5e0;
    border-radius: 8px;
    font-size: 1rem;
    color: #2d3748;
    background-color: #ffffff;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  /* Input placeholder styling */
  .step-page form input::placeholder {
    color: #94a3b8;
    font-style: italic;
    opacity: 0.9;
  }

  .step-page form select:invalid {
    color: #94a3b8;
    font-style: italic;
  }

  /* Input focus styling: Explicit Blue border instead of black */
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
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
  }

  .btn-save:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
</style>
