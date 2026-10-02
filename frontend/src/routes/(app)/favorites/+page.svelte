<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/api/client";
  import SchoolDetail, { type School, type Program } from "$lib/components/SchoolDetail.svelte";
  import SubmitApplicationPanel from "$lib/components/SubmitApplicationPanel.svelte";

  interface FavoriteItem {
    id: string;
    name: string;
    location: string | null;
    logo_url: string | null;
    description: string | null;
    website_url: string | null;
    contact_email: string | null;
    application_deadline: string | null;
    rolling_admission: boolean;
    created_at?: string;
  }

  let favoriteSchools = $state<FavoriteItem[]>([]);
  let selectedSchoolId = $state<string | null>(null);
  let expandedSchoolIds = $state<Record<string, boolean>>({});
  let schoolDetailsMap = $state<Record<string, School>>({});

  let loading = $state(true);
  let loadingDetails = $state<Record<string, boolean>>({});
  let loadError = $state<string | null>(null);
  let removeMessage = $state<string | null>(null);

  // Derived selected school
  const currentSchool = $derived<School | null>(
    selectedSchoolId
      ? schoolDetailsMap[selectedSchoolId] ||
          (favoriteSchools.find((s) => s.id === selectedSchoolId) as School | null)
      : null
  );

  async function loadFavorites() {
    loading = true;
    loadError = null;
    try {
      const data = await apiFetch<FavoriteItem[]>("/api/favorites");
      favoriteSchools = data;

      // Seed the details map with basic info so UI renders instantly
      for (const item of data) {
        if (!schoolDetailsMap[item.id]) {
          schoolDetailsMap[item.id] = {
            ...item,
            programs: undefined,
          };
        }
      }

      // First favorited school selected by default
      if (favoriteSchools.length > 0) {
        const firstId = favoriteSchools[0].id;
        selectSchool(firstId);
      } else {
        selectedSchoolId = null;
      }
    } catch (err: any) {
      console.error("Failed to fetch favorites:", err);
      loadError = err.message || "Failed to load your favorite universities.";
    } finally {
      loading = false;
    }
  }

  async function fetchFullSchoolData(schoolId: string) {
    if (loadingDetails[schoolId]) return;
    loadingDetails[schoolId] = true;

    try {
      const [schoolRes, programsRes] = await Promise.all([
        apiFetch<School>(`/api/schools/${schoolId}`).catch(() => null),
        apiFetch<Program[]>(`/api/schools/${schoolId}/programs`).catch(() => []),
      ]);

      const existing = schoolDetailsMap[schoolId] || favoriteSchools.find((s) => s.id === schoolId);
      schoolDetailsMap[schoolId] = {
        ...(existing || {}),
        ...(schoolRes || {}),
        programs: programsRes,
      } as School;
    } catch (err) {
      console.warn(`Could not load full details for school ${schoolId}:`, err);
    } finally {
      loadingDetails[schoolId] = false;
    }
  }

  function selectSchool(schoolId: string) {
    selectedSchoolId = schoolId;
    expandedSchoolIds[schoolId] = true;

    // Load full details + programs if not already fetched
    if (!schoolDetailsMap[schoolId]?.programs) {
      fetchFullSchoolData(schoolId);
    }
  }

  function toggleAccordion(schoolId: string, event: MouseEvent) {
    event.stopPropagation();
    expandedSchoolIds[schoolId] = !expandedSchoolIds[schoolId];
    if (expandedSchoolIds[schoolId] && selectedSchoolId !== schoolId) {
      selectSchool(schoolId);
    }
  }

  async function handleRemoveFavorite(schoolId: string) {
    const schoolToRemove = favoriteSchools.find((s) => s.id === schoolId);
    const removedName = schoolToRemove?.name || "School";

    // Optimistically remove from list
    const remaining = favoriteSchools.filter((s) => s.id !== schoolId);
    favoriteSchools = remaining;
    delete expandedSchoolIds[schoolId];
    delete schoolDetailsMap[schoolId];

    // If currently selected school was removed, select next available school
    if (selectedSchoolId === schoolId) {
      if (remaining.length > 0) {
        selectSchool(remaining[0].id);
      } else {
        selectedSchoolId = null;
      }
    }

    removeMessage = `Removed ${removedName} from your universities list.`;
    setTimeout(() => {
      removeMessage = null;
    }, 4000);

    try {
      await apiFetch(`/api/favorites/${schoolId}`, { method: "DELETE" });
    } catch (err) {
      console.error("Failed to remove favorite from server:", err);
      // Reload on failure
      loadFavorites();
    }
  }

  onMount(loadFavorites);
</script>

<div class="my-colleges-page">
  <header class="page-header">
    <div class="header-titles">
      <h2>My Universities</h2>
      <p class="subtitle">
        Manage your saved institutions and prepare your applications.
      </p>
    </div>
    {#if !loading && favoriteSchools.length > 0}
      <span class="count-badge">{favoriteSchools.length} {favoriteSchools.length === 1 ? 'University' : 'Universities'}</span>
    {/if}
  </header>

  {#if removeMessage}
    <div class="alert-info" role="status">
      ℹ️ {removeMessage}
    </div>
  {/if}

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading your saved universities from database...</p>
    </div>
  {:else if loadError}
    <div class="error-state">
      <p class="error-text">⚠️ {loadError}</p>
      <button class="btn-retry" onclick={loadFavorites}>Retry</button>
    </div>
  {:else if favoriteSchools.length === 0}
    <!-- Empty State -->
    <div class="empty-state">
      <div class="empty-icon-box">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#94a3b8" stroke-width="1.5">
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      </div>
      <h3>No Universities in Your List Yet</h3>
      <p class="empty-text">
        You haven't added any universities to your list. Browse higher education institutions in Cameroon to explore programs, tuition fees, and admission criteria.
      </p>
      <a href="/discover" class="btn-discover">
        <span>Discover Universities</span>
        <span>↗</span>
      </a>
    </div>
  {:else}
    <SubmitApplicationPanel schools={favoriteSchools} />

    <!-- Two-column Common App "My Colleges" layout -->
    <div class="two-column-layout">
      <!-- Left Panel (fixed width, ~280px): "My Universities" -->
      <aside class="left-panel" aria-label="My Universities navigation">
        <div class="panel-header">
          <h3 class="panel-title">My Universities</h3>
          <span class="panel-count">{favoriteSchools.length}</span>
        </div>

        <nav class="schools-accordion" aria-label="Favorited colleges list">
          {#each favoriteSchools as school (school.id)}
            {@const isExpanded = !!expandedSchoolIds[school.id]}
            {@const isSelected = selectedSchoolId === school.id}
            <div class="accordion-item" class:item-selected={isSelected}>
              <!-- School header / toggle -->
              <button
                type="button"
                class="accordion-trigger"
                class:active-trigger={isSelected}
                onclick={(e) => toggleAccordion(school.id, e)}
                aria-expanded={isExpanded}
                aria-controls={`sub-items-${school.id}`}
              >
                <span class="chevron" class:expanded={isExpanded} aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </span>
                <span class="school-label">{school.name}</span>
              </button>

              <!-- Collapsible Content -->
              {#if isExpanded}
                <div id={`sub-items-${school.id}`} class="accordion-body">
                  <!-- Sub-item: College information -->
                  <button
                    type="button"
                    class="sub-item-link"
                    class:sub-item-active={isSelected}
                    onclick={() => selectSchool(school.id)}
                  >
                    <span class="sub-item-dot" aria-hidden="true"></span>
                    <span class="sub-item-text">College information</span>
                  </button>

                  <!-- Clear reserved spot for future school-specific application sections -->
                  <div class="school-specific-sections-slot" aria-hidden="true">
                    <!-- Reserved: school-specific questions and writing supplement will be added here -->
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </nav>
      </aside>

      <!-- Main Area (Right of Panel): Selected School Details -->
      <main class="main-area" aria-label="Selected university details">
        {#if currentSchool}
          <SchoolDetail
            school={currentSchool}
            showBackButton={false}
            showRemoveFavorite={true}
            onremovefavorite={handleRemoveFavorite}
          />
        {/if}
      </main>
    </div>
  {/if}
</div>

<style>
  .my-colleges-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1a2b4a;
    text-align: left;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 1.25rem;
  }

  .header-titles h2 {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
    letter-spacing: -0.02em;
  }

  .subtitle {
    margin: 0.4rem 0 0;
    color: #64748b;
    font-size: 1rem;
  }

  .count-badge {
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 700;
    white-space: nowrap;
  }

  .alert-info {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    padding: 0.75rem 1.25rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    font-weight: 500;
    font-size: 0.92rem;
  }

  /* Two-column Common App Layout */
  .two-column-layout {
    display: flex;
    align-items: flex-start;
    gap: 2rem;
  }

  /* Left Panel: ~280px */
  .left-panel {
    width: 280px;
    min-width: 280px;
    flex-shrink: 0;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }

  .panel-title {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
  }

  .panel-count {
    background: #e2e8f0;
    color: #475569;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    border-radius: 9999px;
  }

  .schools-accordion {
    display: flex;
    flex-direction: column;
    padding: 0.5rem 0;
  }

  .accordion-item {
    border-bottom: 1px solid #f1f5f9;
  }

  .accordion-item:last-child {
    border-bottom: none;
  }

  .accordion-trigger {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.85rem 1.15rem;
    background: none;
    border: none;
    color: #1e293b;
    font-size: 0.92rem;
    font-weight: 600;
    text-align: left;
    cursor: pointer;
    line-height: 1.35;
    transition: background-color 0.15s, color 0.15s;
  }

  .accordion-trigger:hover {
    background-color: #f8fafc;
    color: #2563eb;
  }

  .accordion-trigger.active-trigger {
    color: #2563eb;
  }

  .chevron {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    transition: transform 0.2s ease, color 0.15s;
    flex-shrink: 0;
  }

  .chevron.expanded {
    transform: rotate(90deg);
    color: #2563eb;
  }

  .school-label {
    flex: 1;
    overflow-wrap: break-word;
    word-break: break-word;
  }

  .accordion-body {
    padding: 0.25rem 0 0.6rem 2rem;
    background: #fcfdfe;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .sub-item-link {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.55rem 0.85rem;
    background: none;
    border: none;
    color: #475569;
    font-size: 0.88rem;
    font-weight: 500;
    text-align: left;
    cursor: pointer;
    border-radius: 6px;
    margin-right: 0.5rem;
    transition: all 0.15s ease;
  }

  .sub-item-link:hover {
    background-color: #f1f5f9;
    color: #0f172a;
  }

  .sub-item-link.sub-item-active {
    background-color: #eff6ff;
    color: #1d4ed8;
    font-weight: 700;
  }

  .sub-item-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #cbd5e1;
    flex-shrink: 0;
  }

  .sub-item-active .sub-item-dot {
    background-color: #2563eb;
    box-shadow: 0 0 0 2px #bfdbfe;
  }

  .school-specific-sections-slot {
    /* Reserved container for future school-specific sections */
    min-height: 2px;
  }

  /* Main Area: Right of Panel */
  .main-area {
    flex: 1;
    min-width: 0;
  }

  /* States */
  .loading-state,
  .error-state {
    text-align: center;
    padding: 4rem 1rem;
    background: #ffffff;
    border-radius: 16px;
    border: 1px dashed #cbd5e1;
  }

  .spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #e2e8f0;
    border-top-color: #2563eb;
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .btn-retry {
    margin-top: 1rem;
    background: #2563eb;
    color: #ffffff;
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }

  /* Empty state */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4.5rem 1.5rem;
    background: #ffffff;
    border-radius: 16px;
    border: 1px dashed #cbd5e1;
    text-align: center;
    max-width: 600px;
    margin: 2rem auto;
  }

  .empty-icon-box {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.25rem;
  }

  .empty-state h3 {
    margin: 0 0 0.5rem;
    font-size: 1.35rem;
    font-weight: 700;
    color: #0f172a;
  }

  .empty-text {
    margin: 0 0 1.75rem;
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.6;
    max-width: 440px;
  }

  .btn-discover {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.7rem 1.5rem;
    background: #2563eb;
    color: #ffffff;
    text-decoration: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.95rem;
    transition: background-color 0.15s, transform 0.15s;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2);
  }

  .btn-discover:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
  }

  /* Responsive */
  @media (max-width: 860px) {
    .two-column-layout {
      flex-direction: column;
      gap: 1.5rem;
    }

    .left-panel {
      width: 100%;
      min-width: 100%;
    }
  }
</style>
