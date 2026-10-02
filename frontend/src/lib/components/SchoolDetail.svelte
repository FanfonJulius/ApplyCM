<script lang="ts">
  export interface Program {
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

  export interface School {
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

  let {
    school,
    showBackButton = false,
    onclose,
    showRemoveFavorite = false,
    onremovefavorite,
    showFavoriteHeart = false,
    isFavorited = false,
    ontogglefavorite,
  }: {
    school: School;
    showBackButton?: boolean;
    onclose?: () => void;
    showRemoveFavorite?: boolean;
    onremovefavorite?: (schoolId: string) => void;
    showFavoriteHeart?: boolean;
    isFavorited?: boolean;
    ontogglefavorite?: (schoolId: string, event: MouseEvent) => void;
  } = $props();

  let logoError = $state(false);

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
</script>

<div class="school-detail-container">
  {#if showBackButton}
    <!-- Back button -->
    <button type="button" class="btn-back" onclick={() => onclose?.()}>
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      <span>Back to schools</span>
    </button>
  {/if}

  <!-- School Hero / Identity Card -->
  <section class="detail-hero-card">
    <div class="hero-main-row">
      <div class="hero-logo-box">
        {#if school.logo_url && !logoError}
          <img
            src={school.logo_url}
            alt="{school.name} logo"
            class="hero-logo-img"
            onerror={() => (logoError = true)}
          />
        {:else}
          <div class="hero-logo-fallback">
            {getInitials(school.name)}
          </div>
        {/if}
      </div>

      <div class="hero-title-group">
        <div class="hero-title-top">
          <span class="institution-type-label">Higher Education Institution</span>
          {#if showFavoriteHeart}
            <button
              type="button"
              class="btn-favorite-heart"
              class:favorited={isFavorited}
              onclick={(e) => ontogglefavorite?.(school.id, e)}
              title={isFavorited ? "Remove from favorites" : "Add to favorites"}
              aria-label={isFavorited ? `Remove ${school.name} from favorites` : `Add ${school.name} to favorites`}
            >
              {#if isFavorited}
                <svg viewBox="0 0 24 24" width="22" height="22" fill="#ef4444">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
              {:else}
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#94a3b8" stroke-width="2">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
              {/if}
            </button>
          {/if}
        </div>
        <h1 class="detail-school-name">{school.name}</h1>

        {#if school.location}
          <div class="detail-location-row">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
            </svg>
            <span>{school.location}</span>
          </div>
        {/if}
      </div>
    </div>

    <!-- Badges & Action Links -->
    <div class="hero-footer-row">
      <div class="hero-badges">
        {#if school.rolling_admission}
          <span class="badge-rolling">✓ Rolling Admission</span>
        {/if}
        {#if school.application_deadline}
          <span class="badge-deadline">📅 Deadline: {school.application_deadline}</span>
        {/if}
      </div>

      <div class="hero-actions">
        {#if school.website_url}
          <a
            href={school.website_url}
            target="_blank"
            rel="noreferrer"
            class="btn-action-pill"
          >
            🌐 Visit Website ↗
          </a>
        {/if}
        {#if school.contact_email}
          <a
            href="mailto:{school.contact_email}"
            class="btn-action-pill"
          >
            ✉️ {school.contact_email}
          </a>
        {/if}

        {#if showRemoveFavorite}
          <button
            type="button"
            class="btn-remove-favorite"
            onclick={() => onremovefavorite?.(school.id)}
            title="Remove from favorites"
          >
            <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
            <span>Remove from favorites</span>
          </button>
        {/if}
      </div>
    </div>
  </section>

  <!-- Overview / Description -->
  {#if school.description}
    <section class="detail-section-card">
      <h2 class="section-heading">About the Institution</h2>
      <p class="section-description-text">{school.description}</p>
    </section>
  {/if}

  <!-- Academic Programs Section -->
  <section class="detail-section-card">
    <div class="section-heading-row">
      <h2 class="section-heading">Offered Academic Programs</h2>
      {#if school.programs}
        <span class="program-count-pill">{school.programs.length} Programs Available</span>
      {/if}
    </div>

    {#if !school.programs}
      <div class="loading-progs-box">
        <div class="spinner-small"></div>
        <span>Loading academic programs from database...</span>
      </div>
    {:else if school.programs.length === 0}
      <p class="empty-progs-text">No academic programs currently registered for this institution.</p>
    {:else}
      <div class="programs-grid">
        {#each school.programs as prog (prog.id)}
          <div class="detail-program-card">
            <div class="prog-top-row">
              <h3 class="prog-name">{prog.field_of_study}</h3>
              {#if prog.degree_type}
                <span class="degree-tag">{prog.degree_type}</span>
              {/if}
            </div>

            <div class="prog-specs-row">
              {#if prog.tuition_fee}
                <span class="spec-pill tuition-pill">💰 {prog.tuition_fee}</span>
              {/if}
              {#if prog.duration}
                <span class="spec-pill">⏱️ {prog.duration}</span>
              {/if}
              {#if prog.language_of_instruction}
                <span class="spec-pill">🗣️ {prog.language_of_instruction}</span>
              {/if}
              {#if prog.delivery_mode}
                <span class="spec-pill">🏫 {prog.delivery_mode}</span>
              {/if}
              {#if prog.class_size}
                <span class="spec-pill">👥 Class Size: {prog.class_size}</span>
              {/if}
              {#if prog.application_deadline}
                <span class="spec-pill">📅 Deadline: {prog.application_deadline}</span>
              {/if}
            </div>

            {#if prog.description}
              <p class="prog-desc">{prog.description}</p>
            {/if}

            {#if prog.admission_requirements}
              <div class="prog-meta-box">
                <span class="meta-box-label">Admission Requirements:</span>
                <span class="meta-box-text">{prog.admission_requirements}</span>
              </div>
            {/if}

            {#if prog.required_documents}
              <div class="prog-meta-box">
                <span class="meta-box-label">Required Documents:</span>
                <span class="meta-box-text">{prog.required_documents}</span>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </section>

  {#if showBackButton}
    <!-- Bottom return button -->
    <div class="detail-footer-nav">
      <button type="button" class="btn-back" onclick={() => onclose?.()}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        <span>Back to all schools</span>
      </button>
    </div>
  {/if}
</div>

<style>
  .school-detail-container {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
    animation: fadeInView 0.2s ease-out;
    width: 100%;
  }

  @keyframes fadeInView {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .btn-back {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    color: #2563eb;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0.4rem 0;
    width: fit-content;
    transition: color 0.15s, transform 0.15s;
  }

  .btn-back:hover {
    color: #1d4ed8;
    transform: translateX(-3px);
  }

  /* Detail Hero Card */
  .detail-hero-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .hero-main-row {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .hero-logo-box {
    width: 80px;
    height: 80px;
    min-width: 80px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .hero-logo-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 8px;
  }

  .hero-logo-fallback {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    color: #1d4ed8;
    font-size: 1.3rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .hero-title-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    flex: 1;
  }

  .hero-title-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .institution-type-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #2563eb;
  }

  .btn-favorite-heart {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.15s, background 0.15s;
  }

  .btn-favorite-heart:hover {
    transform: scale(1.15);
    background-color: #fee2e2;
  }

  .detail-school-name {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
    line-height: 1.25;
  }

  .detail-location-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.95rem;
    color: #64748b;
  }

  .hero-footer-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding-top: 1.25rem;
    border-top: 1px solid #f1f5f9;
  }

  .hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
  }

  .badge-rolling {
    background: #ecfdf5;
    color: #059669;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid #a7f3d0;
  }

  .badge-deadline {
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid #bfdbfe;
  }

  .hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .btn-action-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.88rem;
    color: #1d4ed8;
    background: #ffffff;
    border: 1px solid #bfdbfe;
    padding: 0.45rem 1rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: background 0.15s, border-color 0.15s;
  }

  .btn-action-pill:hover {
    background: #eff6ff;
    border-color: #93c5fd;
  }

  .btn-remove-favorite {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.88rem;
    color: #dc2626;
    background: #fff5f5;
    border: 1px solid #fecaca;
    padding: 0.45rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
  }

  .btn-remove-favorite:hover {
    background: #fee2e2;
    border-color: #fca5a5;
    transform: translateY(-1px);
  }

  /* Section Cards in Detail View */
  .detail-section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .section-heading-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .section-heading {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
  }

  .program-count-pill {
    font-size: 0.8rem;
    font-weight: 600;
    background: #f1f5f9;
    color: #475569;
    padding: 0.25rem 0.7rem;
    border-radius: 6px;
  }

  .section-description-text {
    color: #334155;
    font-size: 0.98rem;
    line-height: 1.7;
    margin: 0;
  }

  /* Programs inside Detail View */
  .programs-grid {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .detail-program-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.35rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .prog-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .prog-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    line-height: 1.35;
  }

  .degree-tag {
    background: #e0e7ff;
    color: #3730a3;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    white-space: nowrap;
  }

  .prog-specs-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .spec-pill {
    font-size: 0.82rem;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-weight: 500;
  }

  .spec-pill.tuition-pill {
    background: #fef3c7;
    border-color: #fde68a;
    color: #92400e;
    font-weight: 600;
  }

  .prog-desc {
    font-size: 0.92rem;
    color: #475569;
    line-height: 1.55;
    margin: 0.15rem 0;
  }

  .prog-meta-box {
    font-size: 0.86rem;
    line-height: 1.5;
    background: #ffffff;
    border: 1px solid #f1f5f9;
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
  }

  .meta-box-label {
    font-weight: 700;
    color: #0f172a;
    display: block;
    margin-bottom: 0.25rem;
  }

  .meta-box-text {
    color: #475569;
  }

  .loading-progs-box {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.92rem;
    color: #64748b;
    padding: 1.5rem 0;
  }

  .empty-progs-text {
    font-size: 0.92rem;
    color: #64748b;
    font-style: italic;
    margin: 0;
  }

  .detail-footer-nav {
    padding-top: 0.5rem;
  }

  .spinner-small {
    width: 18px;
    height: 18px;
    border: 2px solid #e2e8f0;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 640px) {
    .hero-main-row {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .hero-footer-row {
      flex-direction: column;
      align-items: flex-start;
    }

    .hero-logo-box {
      width: 60px;
      height: 60px;
      min-width: 60px;
    }

    .detail-school-name {
      font-size: 1.4rem;
    }
  }
</style>
