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
    created_at?: string;
  }

  const DEFAULT_CAMEROON_SCHOOLS: School[] = [
    {
      id: "s1-yaounde1",
      name: "University of Yaoundé I",
      city: "Yaoundé",
      arrondissement: "Yaounde I (Ngoa-Ekellé)",
      description:
        "Cameroon's first public state university established in 1962, hosting faculties of Science, Arts, Medicine (FMSB), and Higher Teacher Training College (ENS).",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Medicine (FMSB), Computer Science, Mathematics, Physics, Biochemistry, Bilingual Letters, Higher Teacher Education (ENS).",
    },
    {
      id: "s2-yaounde2",
      name: "University of Yaoundé II (Soa)",
      city: "Yaoundé",
      arrondissement: "Soa (Yaoundé Suburbs)",
      description:
        "First public state university for Law, Economics, Political Science, International Relations (IRIC), and Information & Communication (ESSTIC).",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Law & Political Science, Economics & Management, International Relations (IRIC), Journalism & Mass Communication (ESSTIC).",
    },
    {
      id: "s3-douala",
      name: "University of Douala",
      city: "Douala",
      arrondissement: "Douala V (Ange Raphaël / Ndogbong)",
      description:
        "Major public state university situated in Cameroon's economic capital, renowned for ENSET technical education, ESSEC business school, and FGI industrial engineering.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Industrial Engineering (FGI), Business & Management (ESSEC), Technical Teacher Education (ENSET), Applied Physics & Chemistry.",
    },
    {
      id: "s4-buea",
      name: "University of Buea",
      city: "Buea",
      arrondissement: "Buea Central (Molyko)",
      description:
        "First Anglo-Saxon public state university in Cameroon, famous for ASTI translation school, College of Technology (COT), and Health Sciences.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "September 30, 2026",
      programs:
        "Software Engineering, Medicine & Nursing, Computer Science, Journalism & Mass Communication, Translation & Interpretation (ASTI).",
    },
    {
      id: "s5-bamenda",
      name: "University of Bamenda",
      city: "Bamenda",
      arrondissement: "Bambili",
      description:
        "Premier Anglo-Saxon public state university in the North West Region featuring Higher Teacher Training (HTTC/HTTTC), National Polytechnic (ENSPB), and Health Sciences.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "September 30, 2026",
      programs:
        "Transport & Logistics (ENSPB), Mechanical & Computer Engineering, Teacher Education (HTTC/HTTTC), Medical Laboratory Science.",
    },
    {
      id: "s6-dschang",
      name: "University of Dschang",
      city: "Dschang",
      arrondissement: "Dschang Central",
      description:
        "Renowned national agricultural research state university featuring FASA (Agronomy) and Bandjoun Technology Institute (IUT) with multi-campus presence.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Agronomy & Forestry (FASA), Electrical & Telecom Engineering (IUT Bandjoun), Environmental Science, Fine Arts (Foumban).",
    },
    {
      id: "s7-ngaoundere",
      name: "University of Ngaoundere",
      city: "Ngaoundéré",
      arrondissement: "Ngaoundere III (Dang)",
      description:
        "Major public state university in the Adamawa Region, world-renowned for ENSAI (Agro-Industrial Food Sciences) and IUT Ngaoundéré technology institute.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Agro-Industrial Food Engineering (ENSAI), Chemical Engineering, Veterinary Medicine, Economics & Management, Law.",
    },
    {
      id: "s8-maroua",
      name: "University of Maroua",
      city: "Maroua",
      arrondissement: "Maroua I (Kongola)",
      description:
        "Public state university in the Far North Region specializing in Sahelian agriculture, renewable energy engineering, and Higher Teacher Training (ENS Maroua).",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Renewable Energy Engineering, Sahelian Agriculture, Teacher Education (ENS Maroua), Environmental Science & Heritage.",
    },
    {
      id: "s9-ebolowa",
      name: "University of Ebolowa",
      city: "Ebolowa",
      arrondissement: "Ebolowa I (Mvila)",
      description:
        "Public state university in the South Region specializing in Agriculture, Wood & Forestry Technology, Autonomous Engineering, and Social Sciences.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Agricultural Technology, Wood & Forestry Engineering, Environmental Studies, Economic & Social Sciences.",
    },
    {
      id: "s10-bertoua",
      name: "University of Bertoua",
      city: "Bertoua",
      arrondissement: "Bertoua I (Lom-et-Djérem)",
      description:
        "Public state university in the East Region focusing on Mining Engineering, Natural Resources Management, Agriculture, and Teacher Training (ENS Bertoua).",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Mining & Geology Engineering, Natural Resources Management, Agricultural Sciences, Teacher Education (ENS Bertoua).",
    },
    {
      id: "s11-garoua",
      name: "University of Garoua",
      city: "Garoua",
      arrondissement: "Garoua I (Bénoué)",
      description:
        "Public state university in the North Region specializing in Medicine & Biomedical Sciences, Veterinary Medicine, Cotton & Textile Technology, and Law.",
      tuition: "50,000 FCFA / year (State registration fee)",
      deadline: "October 15, 2026",
      programs:
        "Medicine & Biomedical Sciences, Veterinary Medicine, Textile & Cotton Engineering, Law & Political Science.",
    },
    {
      id: "s12-ictu",
      name: "The ICT University",
      city: "Yaoundé",
      arrondissement: "Yaoundé IV (Dispensaire Messassi)",
      description:
        "Top US-accredited private university in Central Africa delivering ICT-driven education, research, and innovation.",
      tuition: "365,000 FCFA / semester (~730,000 FCFA / year)",
      deadline: "September 30, 2026 (October Intake)",
      programs:
        "B.Sc. Computer Science, Software Engineering, Information Systems & Networking, Business Management, Banking & Finance.",
    },
    {
      id: "s13-ucac",
      name: "Catholic University of Central Africa (UCAC)",
      city: "Yaoundé",
      arrondissement: "Yaoundé VI (Nkolbisson)",
      description:
        "Prestigious private Catholic university offering recognized programs in Social Sciences, Nursing, Management, and Ethics.",
      tuition: "750,000 - 1,200,000 FCFA / year",
      deadline: "July 31, 2026",
      programs:
        "Business Administration, Nursing & Health Care Management, Human Resource Management, Law & Political Science.",
    },
  ];

  let schools = $state<School[]>([]);
  let loading = $state(true);
  let loadError = $state<string | null>(null);
  let searchQuery = $state("");
  let selectedCity = $state("All");
  let expandedSchoolId = $state<string | null>(null);
  let favoriteIds = $state<string[]>([]);

  const CITIES = [
    "All",
    "Yaoundé",
    "Douala",
    "Buea",
    "Bamenda",
    "Dschang",
    "Ngaoundéré",
    "Maroua",
    "Ebolowa",
    "Bertoua",
    "Garoua",
  ];

  async function fetchSchools() {
    loading = true;
    loadError = null;
    try {
      const res = await fetch("http://localhost:8000/api/schools");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          schools = data.map((item: School) => {
            const match = DEFAULT_CAMEROON_SCHOOLS.find(
              (d) => d.name.toLowerCase() === item.name.toLowerCase(),
            );
            return {
              ...item,
              tuition: item.tuition || match?.tuition || null,
              deadline: item.deadline || match?.deadline || null,
              programs: item.programs || match?.programs || null,
              arrondissement:
                item.arrondissement || match?.arrondissement || null,
              description: item.description || match?.description || null,
            };
          });
        } else {
          schools = DEFAULT_CAMEROON_SCHOOLS;
        }
      } else {
        schools = DEFAULT_CAMEROON_SCHOOLS;
      }
    } catch (err) {
      console.warn(
        "Backend GET /api/schools request failed, using default schools data:",
        err,
      );
      schools = DEFAULT_CAMEROON_SCHOOLS;
    } finally {
      loading = false;
    }
  }

  function loadFavorites() {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem("favorite_school_ids");
        if (stored) {
          favoriteIds = JSON.parse(stored);
        }
      } catch (err) {
        favoriteIds = [];
      }
    }
  }

  function toggleFavorite(schoolId: string, event: MouseEvent) {
    event.stopPropagation();
    if (favoriteIds.includes(schoolId)) {
      favoriteIds = favoriteIds.filter((id) => id !== schoolId);
    } else {
      favoriteIds = [...favoriteIds, schoolId];
    }

    if (typeof window !== "undefined") {
      localStorage.setItem("favorite_school_ids", JSON.stringify(favoriteIds));
      const favObjects = schools.filter((s) => favoriteIds.includes(s.id));
      localStorage.setItem("favorite_schools_list", JSON.stringify(favObjects));
    }

    fetch("http://localhost:8000/api/favorites", {
      method: favoriteIds.includes(schoolId) ? "POST" : "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ school_id: schoolId }),
    }).catch(() => {});
  }

  function toggleExpand(schoolId: string) {
    if (expandedSchoolId === schoolId) {
      expandedSchoolId = null;
    } else {
      expandedSchoolId = schoolId;
    }
  }

  onMount(() => {
    loadFavorites();
    fetchSchools();
  });

  const filteredSchools = $derived(
    schools.filter((s) => {
      const query = searchQuery.toLowerCase();
      const matchesSearch =
        s.name.toLowerCase().includes(query) ||
        (s.city && s.city.toLowerCase().includes(query)) ||
        (s.arrondissement && s.arrondissement.toLowerCase().includes(query)) ||
        (s.programs && s.programs.toLowerCase().includes(query));
      const matchesCity = selectedCity === "All" || s.city === selectedCity;
      return matchesSearch && matchesCity;
    }),
  );
</script>

<div class="discover-page">
  <header class="header">
    <h2>Discover Universities</h2>
    <p class="subtitle">
      Explore all 11 public state universities and top higher education
      institutions across Cameroon
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
        placeholder="Search by university name, city, program, or arrondissement..."
        bind:value={searchQuery}
      />
      {#if searchQuery}
        <button class="btn-clear" onclick={() => (searchQuery = "")}>✕</button>
      {/if}
    </div>

    <div class="city-chips">
      {#each CITIES as city}
        <button
          class="chip"
          class:active={selectedCity === city}
          onclick={() => (selectedCity = city)}
        >
          {city}
        </button>
      {/each}
    </div>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading universities from backend...</p>
    </div>
  {:else if filteredSchools.length === 0}
    <div class="empty-state">
      <p>No universities found matching "{searchQuery}".</p>
      <button
        class="btn-reset"
        onclick={() => {
          searchQuery = "";
          selectedCity = "All";
        }}>Reset Filters</button
      >
    </div>
  {:else}
    <!-- 1 School Per Row Layout -->
    <div class="schools-grid">
      {#each filteredSchools as school (school.id)}
        {@const isFav = favoriteIds.includes(school.id)}
        {@const isExpanded = expandedSchoolId === school.id}
        <div
          class="university-card"
          class:expanded={isExpanded}
          onclick={() => toggleExpand(school.id)}
          role="button"
          tabindex="0"
          onkeydown={(e) => {
            if (e.key === "Enter" || e.key === " ") toggleExpand(school.id);
          }}
        >
          <!-- Simple Default Card Header -->
          <div class="card-main">
            <div class="info-primary">
              <h3 class="school-name">{school.name}</h3>
              {#if school.city}
                <div class="city-badge">
                  <svg
                    viewBox="0 0 24 24"
                    width="14"
                    height="14"
                    fill="currentColor"
                  >
                    <path
                      d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"
                    />
                  </svg>
                  <span>{school.city}</span>
                </div>
              {/if}
            </div>

            <!-- Favorite Icon Button -->
            <button
              class="btn-favorite"
              class:favorited={isFav}
              onclick={(e) => toggleFavorite(school.id, e)}
              title={isFav ? "Remove from favorites" : "Add to favorites"}
              aria-label={isFav ? "Remove from favorites" : "Add to favorites"}
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
                  stroke="#64748b"
                  stroke-width="2"
                >
                  <path
                    d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                  />
                </svg>
              {/if}
            </button>
          </div>

          <!-- Reveal Indicator -->
          <div class="reveal-hint">
            <span
              >{isExpanded
                ? "Hide information ▲"
                : "Tap to view details ▾"}</span
            >
          </div>

          <!-- Expanded Details Section (On Tap / Click) -->
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
                  <span class="detail-val highlight-val"
                    >💰 {school.tuition}</span
                  >
                </div>
              {/if}

              {#if school.deadline}
                <div class="detail-row">
                  <span class="detail-label">Admission Deadline:</span>
                  <span class="detail-val highlight-val"
                    >📅 {school.deadline}</span
                  >
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
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .discover-page {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1a2b4a;
    text-align: left;
  }

  .header h2 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem;
    color: #1a2b4a;
  }
  .subtitle {
    margin: 0 0 2rem;
    color: #64748b;
    font-size: 1rem;
  }

  .filter-section {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    margin-bottom: 2rem;
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
    padding: 0.85rem 2.5rem 0.85rem 2.8rem;
    border: 1px solid #cbd5e0;
    border-radius: 50px;
    font-size: 1rem;
    background-color: #ffffff;
    transition:
      border-color 0.2s ease,
      box-shadow 0.2s ease;
  }

  .search-box input::placeholder {
    color: #94a3b8;
    font-style: italic;
  }

  .search-box input:focus {
    border-color: #2563eb !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
  }

  .btn-clear {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    font-size: 1rem;
  }

  .city-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chip {
    padding: 0.4rem 1rem;
    border-radius: 50px;
    border: 1px solid #cbd5e0;
    background: #ffffff;
    color: #4a5568;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .chip:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
  }

  .chip.active {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
  }

  .loading-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 1rem;
    color: #64748b;
  }

  .spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #e2e8f0;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .btn-reset {
    margin-top: 1rem;
    padding: 0.5rem 1.25rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 50px;
    cursor: pointer;
  }

  /* 1 School Per Row Layout */
  .schools-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* Simple Basic Card Styling */
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
    transform: translateY(-2px);
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

  .info-primary {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .school-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a2b4a;
    margin: 0;
    line-height: 1.3;
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
    background: #f8fafc;
    border: 1px solid #e2e8f0;
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
    background: #fee2e2;
    border-color: #fca5a5;
    transform: scale(1.1);
  }

  .btn-favorite.favorited {
    background: #fef2f2;
    border-color: #fca5a5;
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

  /* Expanded Information Revealed On Tap */
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
    letter-spacing: 0.05em;
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
</style>
