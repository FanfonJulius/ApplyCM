<script lang="ts">
  import { onMount } from "svelte";
  import { loadProfile, profileState, isSectionComplete } from "$lib/stores/profile.svelte";
  import {
    REQUIRED_SECTIONS,
    fetchApplicationPdf,
    fetchSubmissions,
    submitApplication,
    type Submission,
    type SubmitResponse,
  } from "$lib/api/submissions";

  interface SubmittableSchool {
    id: string;
    name: string;
    contact_email: string | null;
  }

  let { schools }: { schools: SubmittableSchool[] } = $props();

  let submissions = $state<Record<string, Submission>>({});
  let selected = $state<Record<string, boolean>>({});
  let loadingStatus = $state(true);
  let confirming = $state(false);
  let submitting = $state(false);
  let downloading = $state(false);
  let errorMessage = $state<string | null>(null);
  let lastResult = $state<SubmitResponse | null>(null);

  const missingSections = $derived(
    profileState.loaded ? REQUIRED_SECTIONS.filter((s) => !isSectionComplete(s.id)) : []
  );
  const profileReady = $derived(profileState.loaded && !!profileState.profile && missingSections.length === 0);

  function isSent(schoolId: string) {
    return submissions[schoolId]?.status === "sent";
  }

  function canSelect(school: SubmittableSchool) {
    return !!school.contact_email && !isSent(school.id);
  }

  const selectable = $derived(schools.filter(canSelect));
  const selectedSchools = $derived(selectable.filter((s) => selected[s.id]));
  const allSelected = $derived(selectable.length > 0 && selectedSchools.length === selectable.length);
  const sentCount = $derived(schools.filter((s) => isSent(s.id)).length);
  const studentEmail = $derived(profileState.profile?.email ?? null);

  async function refreshSubmissions() {
    try {
      const list = await fetchSubmissions();
      submissions = Object.fromEntries(list.map((s) => [s.school_id, s]));
    } catch (err) {
      errorMessage = err instanceof Error ? err.message : "Could not load your submission status.";
    } finally {
      loadingStatus = false;
    }
  }

  function toggleAll() {
    const next = !allSelected;
    selected = Object.fromEntries(selectable.map((s) => [s.id, next]));
  }

  async function downloadPdf() {
    downloading = true;
    errorMessage = null;
    try {
      const blob = await fetchApplicationPdf();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ApplyCM_Application.pdf";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 10_000);
    } catch (err) {
      errorMessage = err instanceof Error ? err.message : "Could not generate your PDF.";
    } finally {
      downloading = false;
    }
  }

  async function confirmSubmit() {
    submitting = true;
    errorMessage = null;
    try {
      lastResult = await submitApplication(selectedSchools.map((s) => s.id));
      selected = {};
      confirming = false;
      await refreshSubmissions();
    } catch (err) {
      errorMessage = err instanceof Error ? err.message : "Could not submit your application.";
      confirming = false;
    } finally {
      submitting = false;
    }
  }

  function formatDate(iso: string | null) {
    if (!iso) return "";
    return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
  }

  const outcomeLabel: Record<string, string> = {
    sent: "Sent",
    failed: "Failed",
    already_sent: "Already sent earlier",
    in_progress: "Still sending — check back shortly",
  };

  onMount(() => {
    loadProfile();
    refreshSubmissions();
  });
</script>

<section class="submit-panel" aria-labelledby="submit-panel-title">
  <div class="submit-header">
    <div>
      <h3 id="submit-panel-title">Submit your application</h3>
      <p class="submit-hint">
        Tick the universities to apply to. Each one receives your application profile as a PDF by email, and you get a copy.
      </p>
    </div>
    <button type="button" class="btn-secondary" onclick={downloadPdf} disabled={downloading || !profileState.profile}>
      {downloading ? "Preparing PDF…" : "Download my PDF"}
    </button>
  </div>

  {#if profileState.loaded && !profileReady}
    <div class="notice-warning" role="status">
      {#if !profileState.profile}
        Start your application profile before submitting.
        <a href="/application/profile">Go to Profile</a>
      {:else}
        Finish these sections before submitting:
        {#each missingSections as section, i (section.id)}
          <a href={`/application/${section.id}`}>{section.label}</a>{i < missingSections.length - 1 ? ", " : ""}
        {/each}
      {/if}
    </div>
  {/if}

  {#if errorMessage}
    <div class="notice-error" role="alert">{errorMessage}</div>
  {/if}

  {#if lastResult}
    <div class="notice-result" role="status">
      <p class="result-title">
        {#if lastResult.sent_count > 0}
          Application sent to {lastResult.sent_count} {lastResult.sent_count === 1 ? "university" : "universities"}.
          {#if lastResult.student_copy_sent}A copy was emailed to you.{/if}
        {:else}
          No new applications were sent.
        {/if}
      </p>
      <ul>
        {#each lastResult.results as result (result.school_id)}
          <li class={`outcome-${result.status}`}>
            <strong>{result.school_name}</strong>: {outcomeLabel[result.status]}{result.error ? ` — ${result.error}` : ""}
          </li>
        {/each}
      </ul>
      <button type="button" class="btn-link" onclick={() => (lastResult = null)}>Dismiss</button>
    </div>
  {/if}

  <fieldset class="school-choices" disabled={submitting || loadingStatus}>
    <legend class="visually-hidden">Universities to apply to</legend>
    {#if selectable.length > 1}
      <label class="choice select-all">
        <input type="checkbox" checked={allSelected} onchange={toggleAll} />
        <span>Select all ({selectable.length})</span>
      </label>
    {/if}
    {#each schools as school (school.id)}
      {@const submission = submissions[school.id]}
      <label class="choice" class:choice-disabled={!canSelect(school)}>
        <input
          type="checkbox"
          bind:checked={selected[school.id]}
          disabled={!canSelect(school)}
        />
        <span class="choice-name">{school.name}</span>
        {#if submission?.status === "sent"}
          <span class="badge badge-sent">Sent {formatDate(submission.sent_at)}</span>
        {:else if submission?.status === "failed"}
          <span class="badge badge-failed" title={submission.error ?? ""}>Failed — tick to retry</span>
        {:else if submission?.status === "sending"}
          <span class="badge badge-sending">Sending…</span>
        {:else if !school.contact_email}
          <span class="badge badge-muted">No admissions email yet</span>
        {/if}
      </label>
    {/each}
  </fieldset>

  {#if confirming}
    <div class="confirm-box" role="group" aria-label="Confirm submission">
      <p>
        Your application PDF will be emailed to
        <strong>{selectedSchools.map((s) => s.name).join(", ")}</strong>.
        {#if studentEmail}A copy will be sent to <strong>{studentEmail}</strong>.{/if}
        Universities reply to you directly. This can't be undone.
      </p>
      <div class="confirm-actions">
        <button type="button" class="btn-primary" onclick={confirmSubmit} disabled={submitting}>
          {submitting ? "Sending…" : "Yes, send my application"}
        </button>
        <button type="button" class="btn-secondary" onclick={() => (confirming = false)} disabled={submitting}>
          Cancel
        </button>
      </div>
    </div>
  {:else}
    <div class="submit-footer">
      <span class="sent-summary">
        {#if sentCount > 0}Submitted to {sentCount} of {schools.length}{/if}
      </span>
      <button
        type="button"
        class="btn-primary"
        onclick={() => (confirming = true)}
        disabled={!profileReady || selectedSchools.length === 0}
      >
        Submit to {selectedSchools.length} {selectedSchools.length === 1 ? "university" : "universities"}
      </button>
    </div>
  {/if}
</section>

<style>
  .submit-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  }

  .submit-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .submit-header h3 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
  }

  .submit-hint {
    margin: 0.3rem 0 0;
    color: #64748b;
    font-size: 0.9rem;
  }

  .notice-warning,
  .notice-error,
  .notice-result {
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .notice-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
  }

  .notice-warning a {
    color: #92400e;
    font-weight: 700;
  }

  .notice-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
  }

  .notice-result {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #14532d;
  }

  .notice-result ul {
    margin: 0.4rem 0;
    padding-left: 1.2rem;
  }

  .result-title {
    margin: 0;
    font-weight: 600;
  }

  .outcome-failed {
    color: #b91c1c;
  }

  .school-choices {
    border: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .choice {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 0.75rem;
    border: 1px solid #f1f5f9;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.92rem;
  }

  .choice:hover {
    background: #f8fafc;
  }

  .choice input {
    width: 1.05rem;
    height: 1.05rem;
    accent-color: #2563eb;
  }

  .choice-disabled {
    cursor: default;
    color: #64748b;
  }

  .select-all {
    border-style: dashed;
    font-weight: 600;
  }

  .choice-name {
    flex: 1;
  }

  .badge {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    border-radius: 9999px;
    white-space: nowrap;
  }

  .badge-sent {
    background: #dcfce7;
    color: #166534;
  }

  .badge-failed {
    background: #fee2e2;
    color: #b91c1c;
  }

  .badge-sending {
    background: #e0f2fe;
    color: #075985;
  }

  .badge-muted {
    background: #f1f5f9;
    color: #64748b;
  }

  .submit-footer,
  .confirm-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .submit-footer {
    justify-content: space-between;
  }

  .sent-summary {
    color: #166534;
    font-size: 0.88rem;
    font-weight: 600;
  }

  .confirm-box {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid #bfdbfe;
    background: #eff6ff;
    border-radius: 10px;
    font-size: 0.92rem;
    color: #1e3a8a;
  }

  .confirm-box p {
    margin: 0;
  }

  .btn-primary,
  .btn-secondary {
    border-radius: 8px;
    padding: 0.55rem 1.1rem;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    white-space: nowrap;
  }

  .btn-primary {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
  }

  .btn-secondary {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #f8fafc;
  }

  .btn-primary:disabled,
  .btn-secondary:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .btn-link {
    background: none;
    border: none;
    padding: 0;
    color: inherit;
    text-decoration: underline;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }

  @media (max-width: 640px) {
    .submit-header,
    .submit-footer {
      flex-direction: column;
      align-items: stretch;
    }
  }
</style>
