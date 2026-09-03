<script lang="ts">
  import { onMount } from "svelte";
  import { API_BASE_URL } from "$lib/config";

  interface ApplicationSectionStatus {
    key: string;
    label: string;
    href: string;
    complete: boolean;
  }

  interface DashboardSummary {
    firstName: string;
    applicationSections: ApplicationSectionStatus[];
    universitiesOnList: number;
    universitiesInProgress: number;
    favoritedUniversities: number;
    requiredDocumentsOutstanding: number;
  }

  // Sensible fallback so the UI has something to render before/if the fetch fails.
  const DEFAULT_SECTIONS: ApplicationSectionStatus[] = [
    {
      key: "profile",
      label: "Profile",
      href: "/application/profile",
      complete: false,
    },
    {
      key: "contact",
      label: "Contact",
      href: "/application/contact",
      complete: false,
    },
    {
      key: "education",
      label: "Education",
      href: "/application/education",
      complete: false,
    },
    {
      key: "activities",
      label: "Activities and experiences",
      href: "/application/activities",
      complete: false,
    },
    {
      key: "writing",
      label: "Writing",
      href: "/application/writing",
      complete: false,
    },
  ];

  let summary = $state<DashboardSummary>({
    firstName: "",
    applicationSections: DEFAULT_SECTIONS,
    universitiesOnList: 0,
    universitiesInProgress: 0,
    favoritedUniversities: 0,
    requiredDocumentsOutstanding: 0,
  });

  let loading = $state(true);
  let loadError = $state<string | null>(null);

  let applicationExpanded = $state(true);
  let universitiesExpanded = $state(false);
  let greeting = $derived(
    new Date().getHours() < 12
      ? "Good morning"
      : new Date().getHours() < 16
        ? "Good afternoon"
        : "Good evening",
  );

  async function loadDashboard() {
    loading = true;
    loadError = null;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/dashboard/summary`, {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      summary = await res.json();
    } catch (err) {
      loadError =
        err instanceof Error ? err.message : "Could not load your dashboard.";
    } finally {
      loading = false;
    }
  }

  function getCompletedSections(sections: ApplicationSectionStatus[]): ApplicationSectionStatus[] {
    if (typeof window === "undefined") return sections;
    return sections.map((sec) => {
      const isCompleteStored = localStorage.getItem(`section_${sec.key}_complete`);
      return {
        ...sec,
        complete: isCompleteStored === "true" || sec.complete
      };
    });
  }

  onMount(loadDashboard);

  const visibleSections = $derived(
    getCompletedSections(
      summary.applicationSections.length
        ? summary.applicationSections
        : DEFAULT_SECTIONS,
    )
  );
  const totalSections = $derived(visibleSections.length);
  const completedSections = $derived(
    visibleSections.filter((s) => s.complete).length,
  );
  const percentComplete = $derived(
    totalSections === 0
      ? 0
      : Math.round((completedSections / totalSections) * 100),
  );

  // --- circular progress ring math ---
  const ringSize = 96;
  const strokeWidth = 9;
  const radius = (ringSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = $derived(
    circumference - (percentComplete / 100) * circumference,
  );
</script>

<div class="dashboard-page">
  {#if loadError}
    <div class="banner-error" role="alert">
      We couldn't refresh your latest progress. Showing what we have —
      <button class="retry" onclick={loadDashboard}>try again</button>.
    </div>
  {/if}

  <section class="hero">
    <svg
      class="hero-illustration"
      width="140"
      height="90"
      viewBox="0 0 140 90"
      aria-hidden="true"
    >
      <circle cx="112" cy="20" r="14" fill="#ffd76a" />
      <path
        d="M20 78c0-22 18-38 38-38s38 16 38 38"
        fill="none"
        stroke="#1a56db"
        stroke-width="3"
      />
      <rect x="10" y="78" width="120" height="4" rx="2" fill="#1a56db" />
      <circle cx="58" cy="58" r="10" fill="#1a56db" />
      <rect x="52" y="66" width="12" height="14" fill="#1a56db" />
    </svg>
    <h1>{greeting}{summary.firstName ? `, ${summary.firstName}` : ""}!</h1>
  </section>

  <h2 class="page-title">Dashboard</h2>

  <!-- My ApplyCM Application -->
  <section class="card">
    <button
      class="card-header"
      onclick={() => (applicationExpanded = !applicationExpanded)}
      aria-expanded={applicationExpanded}
    >
      <span class="chevron" class:collapsed={!applicationExpanded}>▾</span>
      <h3>My ApplyCM Application</h3>
    </button>

    {#if applicationExpanded}
      <div class="card-body application-body">
        <div class="circular-progress" style="width:{ringSize}px">
          <svg
            width={ringSize}
            height={ringSize}
            viewBox="0 0 {ringSize} {ringSize}"
            role="img"
            aria-label="{percentComplete}% complete"
          >
            <circle
              cx={ringSize / 2}
              cy={ringSize / 2}
              r={radius}
              fill="none"
              stroke="#e2e8f0"
              stroke-width={strokeWidth}
            />
            <circle
              cx={ringSize / 2}
              cy={ringSize / 2}
              r={radius}
              fill="none"
              stroke="#1e824c"
              stroke-width={strokeWidth}
              stroke-linecap="round"
              stroke-dasharray={circumference}
              stroke-dashoffset={dashOffset}
              transform="rotate(-90 {ringSize / 2} {ringSize / 2})"
              class="progress-arc"
            />
            <text
              x="50%"
              y="50%"
              text-anchor="middle"
              dominant-baseline="central"
              class="center-text"
            >
              {percentComplete}%
            </text>
          </svg>
          <p class="progress-label">
            {completedSections}/{totalSections} sections complete
          </p>
        </div>

        <div class="section-grid">
          {#each visibleSections as section (section.key)}
            <a href={section.href} class="section-nav-item">
              <span class="icon" class:complete={section.complete}>
                {#if section.complete}
                  <svg
                    viewBox="0 0 24 24"
                    width="18"
                    height="18"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M5 12.5l4.5 4.5L19 7"
                      stroke="white"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                {/if}
              </span>
              <span class="label">{section.label}</span>
            </a>
          {/each}
        </div>
      </div>
    {/if}
  </section>

  <!-- My Universities -->
  <section class="card">
    <button
      class="card-header"
      onclick={() => (universitiesExpanded = !universitiesExpanded)}
      aria-expanded={universitiesExpanded}
    >
      <span class="chevron" class:collapsed={!universitiesExpanded}>▾</span>
      <h3>My Universities</h3>
    </button>

    <div class="card-body">
      <p class="muted">
        {loading ? "—" : summary.universitiesOnList} universities on my list
      </p>

      <div class="stat-row">
        <div class="stat-pill">
          <span class="dot" aria-hidden="true"></span>
          {loading ? "—" : summary.universitiesInProgress} in progress
        </div>
        <div class="stat-pill">
          <span class="dot favorited" aria-hidden="true"></span>
          {loading ? "—" : summary.favoritedUniversities} favorited
        </div>
        {#if summary.requiredDocumentsOutstanding > 0}
          <div class="stat-pill">
            <span class="dot pending" aria-hidden="true"></span>
            {summary.requiredDocumentsOutstanding} documents needed
          </div>
        {/if}
      </div>

      <button
        class="link-button"
        onclick={() => (universitiesExpanded = !universitiesExpanded)}
      >
        {universitiesExpanded ? "▴ Hide universities" : "▾ Show universities"}
      </button>

      {#if universitiesExpanded}
        <a class="link-button" href="/favorites">Go to My Universities →</a>
      {/if}
    </div>
  </section>
</div>

<style>
  .dashboard-page {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1a2b4a;
    font-family:
      "Inter",
      system-ui,
      -apple-system,
      sans-serif;
  }

  .banner-error {
    background: #fff4e5;
    border: 1px solid #f3c78a;
    color: #7a4a00;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
  }
  .retry {
    background: none;
    border: none;
    padding: 0;
    color: #1a56db;
    text-decoration: underline;
    cursor: pointer;
    font: inherit;
  }

  .hero {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: linear-gradient(135deg, #dceeff 0%, #eaf6ff 100%);
    border-radius: 12px;
    padding: 1.5rem 2rem;
  }
  .hero h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a2b4a;
  }
  .hero-illustration {
    flex-shrink: 0;
  }

  .page-title {
    margin: 2rem 0 1rem;
    font-size: 2rem;
    font-weight: 700;
  }

  .card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    overflow: hidden;
  }

  .card-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #f3f6fa;
    border: none;
    padding: 1rem 1.5rem;
    cursor: pointer;
    text-align: left;
    font: inherit;
  }
  .card-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a2b4a;
  }
  .chevron {
    font-size: 1rem;
    color: #5f6b7a;
    transition: transform 0.15s ease;
  }
  .chevron.collapsed {
    transform: rotate(-90deg);
  }

  .card-body {
    padding: 1.5rem;
  }

  .application-body {
    display: flex;
    align-items: flex-start;
    gap: 2.5rem;
    flex-wrap: wrap;
  }

  .circular-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .progress-arc {
    transition: stroke-dashoffset 0.5s ease;
  }
  .center-text {
    font-size: 0.85rem;
    font-weight: 700;
    fill: #1a2b4a;
  }
  .progress-label {
    margin: 0;
    font-size: 0.85rem;
    color: #5f6b7a;
    text-align: center;
  }

  .section-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1.25rem;
    flex: 1;
  }

  .section-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    width: 84px;
    text-decoration: none;
  }
  .icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px dashed #a9b6c8;
    display: flex;
    align-items: center;
    justify-content: center;
    transition:
      border-color 0.15s ease,
      background-color 0.15s ease;
  }
  .icon.complete {
    border: none;
    background-color: #1a56db;
  }
  .section-nav-item:hover .icon {
    border-color: #2483f0;
  }
  .section-nav-item:hover .icon.complete {
    background-color: #1a56db;
  }
  .label {
    font-size: 0.85rem;
    color: #1a56db;
    text-align: center;
    line-height: 1.25;
  }
  .section-nav-item:hover .label {
    text-decoration: underline;
  }

  .muted {
    color: #5f6b7a;
    margin: 0 0 1rem;
  }

  .stat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  .stat-pill {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    background: #f3f6fa;
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-size: 0.85rem;
    color: #1a2b4a;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #a9b6c8;
  }
  .dot.favorited {
    background: #e0574f;
  }
  .dot.pending {
    background: #e2a53a;
  }

  .link-button {
    background: none;
    border: none;
    color: #1a56db;
    font-size: 0.9rem;
    cursor: pointer;
    padding: 0;
    display: block;
    text-decoration: none;
    margin-top: 0.5rem;
  }
  .link-button:hover {
    text-decoration: underline;
  }
</style>
