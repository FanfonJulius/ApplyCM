<script lang="ts">
  import { onMount } from "svelte";
  import { API_BASE_URL } from "$lib/config";
  import { apiFetch } from "$lib/api/client";
  import SchoolDetail from "$lib/components/SchoolDetail.svelte";

  interface Program {
    id: string;
    school_id: string;
    field_of_study: string;
    degree_type: string | null;
    tuition_fee: string | null;
    duration: string | null;
    language_of_instruction: string | null;
    delivery_mode: string | null;
    admission_requirements: string | null;
    required_documents: string | null;
    application_deadline: string | null;
    class_size: number | null;
    description: string | null;
  }

  interface School {
    id: string;
    name: string;
    location: string | null;
    description: string | null;
    website_url: string | null;
    logo_url: string | null;
    contact_email: string | null;
    application_deadline: string | null;
    rolling_admission: boolean;
    created_at?: string;
    programs?: Program[];
  }

  let schools = $state<School[]>([]);
  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let searchQuery = $state("");
  let selectedFilter = $state("All");
  let selectedSchoolId = $state<string | null>(null);
  let favoriteIds = $state<string[]>([]);
  let logoErrors = $state<Record<string, boolean>>({});

  const selectedSchool = $derived(
    schools.find((s) => s.id === selectedSchoolId) || null
  );

  const DEGREE_FILTERS = ["All", "Bachelor", "Engineering", "Master", "Licence Pro", "HND"];

  function getInitials(name: string): string {
    if (!name) return "SCH";
    const clean = name.replace(/[^a-zA-Z0-9\s]/g, "");
    const words = clean
      .split(/\s+/)
      .filter((w) => !["of", "the", "and", "de", "la", "et", "l", "du"].includes(w.toLowerCase()));
    if (words.length === 0) return name.slice(0, 3).toUpperCase();
    if (words.length === 1) return words[0].slice(0, 3).toUpperCase();
    return words.slice(0, 3).map((w) => w[0]?.toUpperCase() || "").join("");
  }

  async function fetchSchools() {
    loading = true;
    loadError = null;
    try {
      const res = await fetch(`${API_BASE_URL}/api/schools`);
      if (!res.ok) {
        throw new Error(`Failed to load schools: HTTP ${res.status}`);
      }
      const data: School[] = await res.json();
      schools = data;

      // Pre-load programs in background so search filter works across degree types
      for (const school of schools) {
        fetchProgramsForSchool(school.id);
      }
    } catch (err: any) {
      console.error("Failed to fetch schools from backend API:", err);
      loadError = err.message || "Failed to load universities from server.";
    } finally {
      loading = false;
    }
  }

  async function fetchProgramsForSchool(schoolId: string) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/schools/${schoolId}/programs`);
      if (res.ok) {
        const progs: Program[] = await res.json();
        const index = schools.findIndex((s) => s.id === schoolId);
        if (index !== -1) {
          schools[index] = { ...schools[index], programs: progs };
        }
      }
    } catch (err) {
      console.warn(`Could not load programs for school ${schoolId}:`, err);
    }
  }

  async function loadFavorites() {
    try {
      const favSchools = await apiFetch<Array<{ id: string }>>("/api/favorites");
      favoriteIds = favSchools.map((s) => s.id);
    } catch (err) {
      console.warn("Could not load favorites from API:", err);
      favoriteIds = [];
    }
  }

  async function toggleFavorite(schoolId: string, event: MouseEvent) {
    event.stopPropagation();
    const isCurrentlyFav = favoriteIds.includes(schoolId);

    // Optimistic UI update
    if (isCurrentlyFav) {
      favoriteIds = favoriteIds.filter((id) => id !== schoolId);
    } else {
      favoriteIds = [...favoriteIds, schoolId];
    }

    try {
      if (isCurrentlyFav) {
        await apiFetch(`/api/favorites/${schoolId}`, { method: "DELETE" });
      } else {
        await apiFetch("/api/favorites", {
          method: "POST",
          body: JSON.stringify({ school_id: schoolId }),
        });
      }
    } catch (err) {
      console.error("Failed to update favorite on server:", err);
      // Revert optimistic update on failure
      if (isCurrentlyFav) {
        favoriteIds = [...favoriteIds, schoolId];
      } else {
        favoriteIds = favoriteIds.filter((id) => id !== schoolId);
      }
    }
  }

  function openSchoolDetail(schoolId: string) {
    selectedSchoolId = schoolId;
    const school = schools.find((s) => s.id === schoolId);
    if (school && !school.programs) {
      fetchProgramsForSchool(schoolId);
    }
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function closeSchoolDetail() {
    selectedSchoolId = null;
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  onMount(() => {
    loadFavorites();
    fetchSchools();
  });

  const filteredSchools = $derived(
    schools.filter((s) => {
      const query = searchQuery.toLowerCase().trim();
      const hasProgramsMatch = s.programs?.some((p) =>
        p.field_of_study.toLowerCase().includes(query) ||
        (p.degree_type && p.degree_type.toLowerCase().includes(query)) ||
        (p.description && p.description.toLowerCase().includes(query))
      );

      const matchesSearch =
        !query ||
        s.name.toLowerCase().includes(query) ||
        (s.location && s.location.toLowerCase().includes(query)) ||
        (s.description && s.description.toLowerCase().includes(query)) ||
        hasProgramsMatch;

      const matchesDegree =
        selectedFilter === "All" ||
        s.programs?.some((p) => p.degree_type === selectedFilter);

      return matchesSearch && matchesDegree;
    })
  );
</script>

<svelte:window
  onkeydown={(e) => {
    if (e.key === "Escape" && selectedSchoolId) {
      closeSchoolDetail();
    }
  }}
/>

<div class="discover-page">
  {#if selectedSchool}
    <!-- ======================================================== -->
    <!-- 2. DETAIL VIEW (Replaces full list, same page, client swap) -->
    <!-- ======================================================== -->
    <SchoolDetail
      school={selectedSchool}
      showBackButton={true}
      onclose={closeSchoolDetail}
      showFavoriteHeart={true}
      isFavorited={favoriteIds.includes(selectedSchool.id)}
      ontogglefavorite={toggleFavorite}
    />
  {:else}
    <!-- ======================================================== -->
    <!-- 1. LIST VIEW (Default State: Common App style search)    -->
    <!-- ======================================================== -->
    <header class="header">
      <h2>Discover Universities & Higher Institutes</h2>
      <p class="subtitle">
        Browse higher education institutions in Cameroon. Click any institution to view its full profile, accredited degree programs, tuition fees, and admission criteria.
      </p>
    </header>

    <div class="filter-section">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20">
          <path
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            stroke="#64748b"
            stroke-width="2"
            stroke-linecap="round"
            fill="none"
          />
        </svg>
        <input
          type="text"
          placeholder="Search by school name, location, degree type, or field of study..."
          bind:value={searchQuery}
        />
        {#if searchQuery}
          <button class="btn-clear" onclick={() => (searchQuery = "")} aria-label="Clear search">✕</button>
        {/if}
      </div>

      <div class="degree-chips">
        <span class="chips-label">Filter by Degree:</span>
        {#each DEGREE_FILTERS as filter}
          <button
            type="button"
            class="chip"
            class:active={selectedFilter === filter}
            onclick={() => (selectedFilter = filter)}
          >
            {filter}
          </button>
        {/each}
      </div>
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading schools and programs from database...</p>
      </div>
    {:else if loadError}
      <div class="error-state">
        <p class="error-text">⚠️ {loadError}</p>
        <button class="btn-reset" onclick={fetchSchools}>Retry</button>
      </div>
    {:else if filteredSchools.length === 0}
      <div class="empty-state">
        <p>No universities found matching your filter.</p>
        <button
          class="btn-reset"
          onclick={() => {
            searchQuery = "";
            selectedFilter = "All";
          }}>Reset Filters</button
        >
      </div>
    {:else}
      <!-- Common App Style List View Rows (Left: Logo Box, Right: Name, Location, Heart) -->
      <div class="schools-list">
        {#each filteredSchools as school (school.id)}
          {@const isFav = favoriteIds.includes(school.id)}
          <div class="school-row">
            <!-- Left section: Fixed-size boxed container holding logo / initials fallback -->
            <div class="logo-box">
              {#if school.logo_url && !logoErrors[school.id]}
                <img
                  src={school.logo_url}
                  alt="{school.name} logo"
                  class="school-logo-img"
                  onerror={() => (logoErrors[school.id] = true)}
                />
              {:else}
                <div class="logo-fallback">
                  {getInitials(school.name)}
                </div>
              {/if}
            </div>

            <!-- Right section: School Name + Location -->
            <div class="school-info-col">
              <button
                type="button"
                class="school-name-btn"
                onclick={() => openSchoolDetail(school.id)}
              >
                {school.name}
              </button>

              {#if school.location}
                <div class="school-location-line">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                    <path
                      d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"
                    />
                  </svg>
                  <span>{school.location}</span>
                </div>
              {/if}
            </div>

            <!-- Far-right: Favorite heart button -->
            <button
              type="button"
              class="btn-favorite"
              class:favorited={isFav}
              onclick={(e) => toggleFavorite(school.id, e)}
              title={isFav ? "Remove from favorites" : "Add to favorites"}
              aria-label={isFav ? `Remove ${school.name} from favorites` : `Add ${school.name} to favorites`}
            >
              {#if isFav}
                <svg viewBox="0 0 24 24" width="22" height="22" fill="#ef4444">
                  <path
                    d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                  />
                </svg>
              {:else}
                <svg
                  viewBox="0 0 24 24"
                  width="22"
                  height="22"
                  fill="none"
                  stroke="#94a3b8"
                  stroke-width="2"
                >
                  <path
                    d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                  />
                </svg>
              {/if}
            </button>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .discover-page {
    max-width: 980px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1a2b4a;
    text-align: left;
  }

  /* List Header */
  .header h2 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem;
    color: #0f172a;
    letter-spacing: -0.02em;
  }

  .subtitle {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2rem;
    line-height: 1.5;
  }

  /* Filters */
  .filter-section {
    margin-bottom: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .search-box {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    pointer-events: none;
  }

  .search-box input {
    width: 100%;
    padding: 0.85rem 2.8rem 0.85rem 3rem;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    font-size: 0.95rem;
    background: #ffffff;
    color: #1e293b;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .search-box input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
  }

  .btn-clear {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
    line-height: 1;
  }

  .degree-chips {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
  }

  .chips-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748b;
    margin-right: 0.25rem;
  }

  .chip {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #475569;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .chip:hover {
    background: #e2e8f0;
  }

  .chip.active {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
  }

  /* ======================================================== */
  /* Common App Style School Rows (Clean horizontal list item) */
  /* ======================================================== */
  .schools-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .school-row {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  }

  .school-row:hover {
    border-color: #cbd5e1;
    background-color: #fafbfc;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  /* Left Section: Fixed-size boxed container for school logo / fallback */
  .logo-box {
    width: 60px;
    height: 60px;
    min-width: 60px;
    border-radius: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
  }

  .school-logo-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 6px;
  }

  .logo-fallback {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    color: #1d4ed8;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Right Section: School Name + Location */
  .school-info-col {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex: 1;
    min-width: 0;
  }

  .school-name-btn {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    font-size: 1.12rem;
    font-weight: 700;
    color: #0f172a;
    text-align: left;
    cursor: pointer;
    line-height: 1.35;
    transition: color 0.15s;
  }

  .school-name-btn:hover {
    color: #2563eb;
    text-decoration: underline;
    text-underline-offset: 3px;
  }

  .school-location-line {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.88rem;
    color: #64748b;
  }

  /* Far-right Favorite Heart Button */
  .btn-favorite {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.15s, background-color 0.15s;
    flex-shrink: 0;
    margin-left: auto;
  }

  .btn-favorite:hover {
    transform: scale(1.15);
    background-color: #fee2e2;
  }

  /* List View States (Loading, Error, Empty) */
  .loading-state,
  .empty-state,
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

  .btn-reset {
    margin-top: 1rem;
    background: #2563eb;
    color: #ffffff;
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }

  /* Responsive layout adjustments */
  @media (max-width: 640px) {
    .school-row {
      gap: 0.85rem;
      padding: 0.85rem 1rem;
    }

    .logo-box {
      width: 50px;
      height: 50px;
      min-width: 50px;
    }

    .school-name-btn {
      font-size: 1rem;
    }
  }
</style>
