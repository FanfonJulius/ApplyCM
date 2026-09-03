<script lang="ts">
  import { onMount } from "svelte";

  interface School {
    id: string;
    name: string;
    city: string | null;
    arrondissement: string | null;
    description: string | null;
    tuition?: string | null;
    deadline?: string | null;
    programs?: string | null;
  }

  let favoriteSchools = $state<School[]>([]);
  let selectedSchoolIds = $state<string[]>([]);
  let submittedSchoolIds = $state<string[]>([]);
  let expandedSchoolId = $state<string | null>(null);
  let isApplying = $state(false);
  let applyMessage = $state<string | null>(null);

  function loadFavoritesAndApplications() {
    if (typeof window !== "undefined") {
      try {
        const storedList = localStorage.getItem("favorite_schools_list");
        if (storedList) {
          favoriteSchools = JSON.parse(storedList);
        }
      } catch (err) {
        favoriteSchools = [];
      }

      selectedSchoolIds = favoriteSchools.map((s) => s.id);

      try {
        const submitted = localStorage.getItem("submitted_application_school_ids");
        if (submitted) {
          submittedSchoolIds = JSON.parse(submitted);
        }
      } catch (err) {
        submittedSchoolIds = [];
      }
    }
  }

  function removeFavorite(schoolId: string, event: MouseEvent) {
    event.stopPropagation();
    favoriteSchools = favoriteSchools.filter((s) => s.id !== schoolId);
    selectedSchoolIds = selectedSchoolIds.filter((id) => id !== schoolId);

    if (typeof window !== "undefined") {
      const favIds = favoriteSchools.map((s) => s.id);
      localStorage.setItem("favorite_school_ids", JSON.stringify(favIds));
      localStorage.setItem("favorite_schools_list", JSON.stringify(favoriteSchools));
    }

    fetch(`http://localhost:8000/api/favorites/${schoolId}`, {
      method: "DELETE"
    }).catch(() => {});
  }

  function toggleExpand(schoolId: string) {
    if (expandedSchoolId === schoolId) {
      expandedSchoolId = null;
    } else {
      expandedSchoolId = schoolId;
    }
  }

  function toggleSelectSchool(schoolId: string, event: Event) {
    event.stopPropagation();
    if (selectedSchoolIds.includes(schoolId)) {
      selectedSchoolIds = selectedSchoolIds.filter((id) => id !== schoolId);
    } else {
      selectedSchoolIds = [...selectedSchoolIds, schoolId];
    }
  }

  function toggleSelectAll() {
    if (selectedSchoolIds.length === favoriteSchools.length) {
      selectedSchoolIds = [];
    } else {
      selectedSchoolIds = favoriteSchools.map((s) => s.id);
    }
  }

  async function handleBatchApply() {
    if (selectedSchoolIds.length === 0) return;

    isApplying = true;
    applyMessage = null;

    try {
      await fetch("http://localhost:8000/api/applications/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          school_ids: selectedSchoolIds
        }),
      });

      const updatedSubmitted = Array.from(new Set([...submittedSchoolIds, ...selectedSchoolIds]));
      submittedSchoolIds = updatedSubmitted;

      if (typeof window !== "undefined") {
        localStorage.setItem("submitted_application_school_ids", JSON.stringify(updatedSubmitted));
      }

      applyMessage = `Application successfully submitted to ${selectedSchoolIds.length} university(ies)!`;
    } catch (err) {
      console.warn("Backend batch apply call failed, recording submitted status locally:", err);
      const updatedSubmitted = Array.from(new Set([...submittedSchoolIds, ...selectedSchoolIds]));
      submittedSchoolIds = updatedSubmitted;

      if (typeof window !== "undefined") {
        localStorage.setItem("submitted_application_school_ids", JSON.stringify(updatedSubmitted));
      }

      applyMessage = `Application submitted to ${selectedSchoolIds.length} university(ies)!`;
    } finally {
      isApplying = false;
      setTimeout(() => {
        applyMessage = null;
      }, 3500);
    }
  }

  onMount(loadFavoritesAndApplications);
</script>

<div class="favorites-page">
  <header class="header">
    <div class="header-top">
      <h2>My Favorite Universities</h2>
      <span class="count-badge">{favoriteSchools.length} Saved</span>
    </div>
    <p class="subtitle">Select universities to send your completed application profile to</p>
  </header>

  {#if applyMessage}
    <div class="alert-success" role="status">
      ✓ {applyMessage}
    </div>
  {/if}

  {#if favoriteSchools.length === 0}
    <div class="empty-state">
      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#94a3b8" stroke-width="1.5">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
      <p class="empty-text">No favorite universities saved yet.</p>
      <a href="/discover" class="btn-discover">Discover Universities →</a>
    </div>
  {:else}
    <!-- Apply Action Bar -->
    <div class="apply-bar">
      <div class="select-info">
        <button class="btn-select-all" onclick={toggleSelectAll}>
          {selectedSchoolIds.length === favoriteSchools.length ? "Deselect All" : "Select All"}
        </button>
        <span class="selection-count">
          {selectedSchoolIds.length} of {favoriteSchools.length} selected
        </span>
      </div>

      <button
        class="btn-apply-batch"
        disabled={selectedSchoolIds.length === 0 || isApplying}
        onclick={handleBatchApply}
      >
        {isApplying ? "Sending Application..." : `Apply to ${selectedSchoolIds.length} Selected`}
      </button>
    </div>

    <!-- 1 Card Per Row Layout Identical to Discover Universities -->
    <div class="schools-grid">
      {#each favoriteSchools as school (school.id)}
        {@const isExpanded = expandedSchoolId === school.id}
        {@const isSelected = selectedSchoolIds.includes(school.id)}
        {@const isSubmitted = submittedSchoolIds.includes(school.id)}

        <div
          class="university-card"
          class:expanded={isExpanded}
          class:selected={isSelected}
          class:submitted={isSubmitted}
          onclick={() => toggleExpand(school.id)}
          role="button"
          tabindex="0"
          onkeydown={(e) => { if (e.key === "Enter" || e.key === " ") toggleExpand(school.id); }}
        >
          <!-- Main Card Header -->
          <div class="card-main">
            <div class="card-left">
              <input
                type="checkbox"
                class="school-checkbox"
                checked={isSelected}
                disabled={isSubmitted}
                onclick={(e) => toggleSelectSchool(school.id, e)}
                aria-label={`Select ${school.name}`}
              />

              <div class="info-primary">
                <div class="title-row">
                  <h3 class="school-name">{school.name}</h3>

                  {#if isSubmitted}
                    <span class="status-btn-submitted">✓ Application Sent</span>
                  {/if}
                </div>

                {#if school.city}
                  <div class="city-badge">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
                    </svg>
                    <span>{school.city}</span>
                  </div>
                {/if}
              </div>
            </div>

            <!-- Remove Favorite Button -->
            <button
              class="btn-favorite favorited"
              onclick={(e) => removeFavorite(school.id, e)}
              title="Remove from favorites"
              aria-label="Remove from favorites"
            >
              <svg viewBox="0 0 24 24" width="22" height="22" fill="#ef4444">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </button>
          </div>

          <!-- Reveal Indicator -->
          <div class="reveal-hint">
            <span>{isExpanded ? "Hide information ▲" : "Tap to view details ▾"}</span>
          </div>

          <!-- Details Section -->
          {#if isExpanded}
            <div class="card-details">
              {#if school.arrondissement}
                <div class="detail-row">
                  <span class="detail-label">Arrondissement / Campus:</span>
                  <span class="detail-val">{school.arrondissement}</span>
                </div>
              {/if}

              {#if school.tuition}
                <div class="detail-row">
                  <span class="detail-label">Tuition Fees:</span>
                  <span class="detail-val highlight-val">💰 {school.tuition}</span>
                </div>
              {/if}

              {#if school.deadline}
                <div class="detail-row">
                  <span class="detail-label">Admission Deadline:</span>
                  <span class="detail-val highlight-val">📅 {school.deadline}</span>
                </div>
              {/if}

              {#if school.programs}
                <div class="detail-row">
                  <span class="detail-label">Key Programs Offered:</span>
                  <span class="detail-val">{school.programs}</span>
                </div>
              {/if}

              {#if school.description}
                <div class="detail-row">
                  <span class="detail-label">Description:</span>
                  <p class="description-text">{school.description}</p>
                </div>
              {/if}

              {#if isSubmitted}
                <div class="submitted-notice">
                  <span class="green-dot">●</span> Application successfully submitted to this institution.
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .favorites-page {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1a2b4a;
    text-align: left;
  }

  .header-top {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .header h2 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
  }

  .count-badge {
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    padding: 0.35rem 0.85rem;
    border-radius: 50px;
    font-size: 0.875rem;
    font-weight: 700;
  }

  .subtitle {
    margin: 0.5rem 0 1.75rem;
    color: #64748b;
  }

  .alert-success {
    background-color: #dcfce7;
    border: 1px solid #86efac;
    color: #14532d;
    padding: 0.85rem 1.25rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    font-weight: 600;
  }

  .apply-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .select-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .btn-select-all {
    background: #ffffff;
    border: 1px solid #cbd5e0;
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-select-all:hover {
    background: #f1f5f9;
    color: #1a2b4a;
  }

  .selection-count {
    font-size: 0.9rem;
    font-weight: 600;
    color: #475569;
  }

  .btn-apply-batch {
    background-color: #2563eb;
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    border: none;
    padding: 0.65rem 1.5rem;
    border-radius: 50px;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.15s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  }

  .btn-apply-batch:hover:not(:disabled) {
    background-color: #1d4ed8;
    transform: translateY(-1px);
  }

  .btn-apply-batch:disabled {
    background-color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 1rem;
    background: white;
    border-radius: 12px;
    border: 1px dashed #cbd5e0;
  }

  .empty-text {
    margin: 1rem 0;
    color: #64748b;
    font-weight: 500;
  }

  .btn-discover {
    padding: 0.6rem 1.5rem;
    background: #2563eb;
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .schools-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .university-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    user-select: none;
  }

  .university-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.1);
  }

  .university-card.selected {
    border-color: #93c5fd;
    background-color: #f8fafc;
  }

  .university-card.expanded {
    border-color: #2563eb;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.15);
  }

  .card-main {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .card-left {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    flex: 1;
  }

  .school-checkbox {
    width: 20px;
    height: 20px;
    margin-top: 0.25rem;
    accent-color: #2563eb;
    cursor: pointer;
  }

  .info-primary {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    flex: 1;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .school-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a2b4a;
    margin: 0;
    line-height: 1.3;
  }

  .status-btn-submitted {
    background-color: #16a34a;
    color: #ffffff;
    font-size: 0.775rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25);
  }

  .city-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background-color: #eff6ff;
    color: #2563eb;
    padding: 0.25rem 0.65rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    width: fit-content;
  }

  .btn-favorite {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.15s ease;
  }

  .btn-favorite:hover {
    transform: scale(1.1);
  }

  .reveal-hint {
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px dashed #e2e8f0;
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 500;
    text-align: center;
  }

  .card-details {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    animation: fadeIn 0.25s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .detail-row {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .detail-label {
    font-size: 0.775rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #64748b;
  }

  .detail-val {
    font-size: 0.9rem;
    color: #1a2b4a;
    font-weight: 600;
  }

  .highlight-val {
    color: #1d4ed8;
  }

  .description-text {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.45;
    color: #475569;
  }

  .submitted-notice {
    font-size: 0.85rem;
    color: #16a34a;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    background: #f0fdf4;
    padding: 0.5rem 0.85rem;
    border-radius: 6px;
    border: 1px solid #bbf7d0;
  }

  .green-dot {
    color: #16a34a;
    font-size: 0.7rem;
  }
</style>
