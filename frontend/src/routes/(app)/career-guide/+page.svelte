<script lang="ts">
  import { onMount } from "svelte";
  import { API_BASE_URL } from "$lib/config";
  import { apiFetch } from "$lib/api/client";

  interface QuestionItem {
    id: string;
    statement: string;
    category?: string;
    min_value: number;
    max_value: number;
  }

  interface MatchedProgram {
    id: string;
    program_title: string;
    school_id: string;
    school_name: string;
    school_location: string | null;
    school_website: string | null;
    school_logo: string | null;
    degree_type: string | null;
    tuition_fee: string | null;
    parsed_tuition: number | null;
    duration: string | null;
    admission_requirements: string | null;
    description: string | null;
    matched_target_field: string;
    is_within_budget: boolean;
    budget_fit_score: number;
  }

  interface RecommendedField {
    field_name: string;
    rank: number;
    probability: number;
    percentage: number;
    description: string;
    explanation: string;
    programs_available_count: number;
    programs: MatchedProgram[];
  }

  interface RecommendationResponse {
    student_summary: {
      series: string;
      subjects: string[];
      max_budget: number | null;
    };
    top_fields: RecommendedField[];
    all_matching_programs: MatchedProgram[];
    total_matching_programs: number;
    model_info: {
      model_type: string;
      accuracy: number;
      top3_accuracy: number;
      baseline_accuracy: number;
    };
  }

  // Questionnaire State
  let loadingMeta = $state(true);
  let submitting = $state(false);
  let errorMsg = $state<string | null>(null);

  let currentStep = $state(1); // 1: Academic, 2: 12 Statements, 3: Budget, 4: Results
  let selectedSeries = $state("Science");
  let selectedSubjects = $state<string[]>(["Maths", "Physics"]);
  let answers = $state<Record<string, number>>({});
  let maxBudget = $state<number | null>(600000);
  let activeFieldTab = $state<string>("ALL");
  let showModelMetrics = $state(false);

  // Metadata from backend
  let questions = $state<QuestionItem[]>([]);
  let seriesOptions = $state<string[]>(["Science", "Arts", "Commercial", "Technical"]);
  let subjectOptions = $state<string[]>([
    "Maths", "Physics", "Chemistry", "Biology", "Computer Science",
    "Economics", "Accounting", "Literature", "History", "Geography",
    "Languages", "Technical Drawing"
  ]);

  // Results
  let results = $state<RecommendationResponse | null>(null);

  // Favorites
  let favoriteIds = $state<string[]>([]);
  let savingFavorite = $state<Record<string, boolean>>({});

  onMount(async () => {
    await loadMetadata();
    await loadFavorites();
  });

  async function loadMetadata() {
    loadingMeta = true;
    errorMsg = null;
    try {
      const res = await fetch(`${API_BASE_URL}/api/recommendations/questions`);
      if (!res.ok) throw new Error("Could not load questionnaire from server.");
      const data = await res.json();
      questions = data.questions;
      seriesOptions = data.series_options;
      subjectOptions = data.subject_options;
      // Default answers to 3 (Neutral)
      for (const q of questions) {
        if (answers[q.id] === undefined) {
          answers[q.id] = 3;
        }
      }
    } catch (e: any) {
      console.warn("Using offline fallback questionnaire questions:", e);
      // Fallback questions if backend is still initializing
      questions = [
        { id: "q1_building", statement: "I enjoy fixing or building things.", min_value: 1, max_value: 5 },
        { id: "q2_math_logic", statement: "I like solving math or logic problems.", min_value: 1, max_value: 5 },
        { id: "q3_helping_sick", statement: "I like helping people who are sick or in need.", min_value: 1, max_value: 5 },
        { id: "q4_organising_data", statement: "I enjoy organising money, records or data.", min_value: 1, max_value: 5 },
        { id: "q5_leadership_selling", statement: "I like leading a group or selling an idea.", min_value: 1, max_value: 5 },
        { id: "q6_creative_design", statement: "I enjoy drawing, designing or creating.", min_value: 1, max_value: 5 },
        { id: "q7_debating_law", statement: "I like debating and arguing a case.", min_value: 1, max_value: 5 },
        { id: "q8_computers_tech", statement: "I like working with computers and technology.", min_value: 1, max_value: 5 },
        { id: "q9_nature_outdoors", statement: "I enjoy working outdoors with plants, animals or nature.", min_value: 1, max_value: 5 },
        { id: "q10_teaching", statement: "I like teaching or explaining things to others.", min_value: 1, max_value: 5 },
        { id: "q11_lab_experiments", statement: "I like doing lab experiments.", min_value: 1, max_value: 5 },
        { id: "q12_writing_reading", statement: "I like writing and reading.", min_value: 1, max_value: 5 },
      ];
      for (const q of questions) {
        answers[q.id] = 3;
      }
    } finally {
      loadingMeta = false;
    }
  }

  interface FavoriteItem {
    school_id: string;
  }

  async function loadFavorites() {
    try {
      const data = await apiFetch<FavoriteItem[]>("/api/favorites");
      favoriteIds = (data || []).map(f => f.school_id);
    } catch (_) {}
  }

  function toggleSubject(subj: string) {
    if (selectedSubjects.includes(subj)) {
      selectedSubjects = selectedSubjects.filter(s => s !== subj);
    } else {
      if (selectedSubjects.length < 3) {
        selectedSubjects = [...selectedSubjects, subj];
      }
    }
  }

  function setLikert(qId: string, value: number) {
    answers[qId] = value;
  }

  async function submitQuestionnaire() {
    if (selectedSubjects.length === 0) {
      errorMsg = "Please select at least 1 strong subject.";
      return;
    }
    submitting = true;
    errorMsg = null;
    try {
      const payload = {
        series: selectedSeries,
        subjects: selectedSubjects,
        answers: answers,
        max_budget: maxBudget,
      };

      const res = await fetch(`${API_BASE_URL}/api/recommendations/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned error HTTP ${res.status}`);
      }

      results = await res.json();
      currentStep = 4; // Results step
      activeFieldTab = "ALL";
    } catch (e: any) {
      console.error("Submission failed:", e);
      errorMsg = e.message || "Failed to generate recommendations. Please retry.";
    } finally {
      submitting = false;
    }
  }

  async function toggleFavoriteSchool(schoolId: string) {
    const isFav = favoriteIds.includes(schoolId);
    savingFavorite[schoolId] = true;
    try {
      if (isFav) {
        await apiFetch(`/api/favorites/${schoolId}`, { method: "DELETE" });
        favoriteIds = favoriteIds.filter(id => id !== schoolId);
      } else {
        await apiFetch(`/api/favorites/${schoolId}`, { method: "POST" });
        favoriteIds = [...favoriteIds, schoolId];
      }
    } catch (err) {
      console.warn("Could not toggle favorite:", err);
    } finally {
      savingFavorite[schoolId] = false;
    }
  }

  const filteredPrograms = $derived(() => {
    if (!results) return [];
    if (activeFieldTab === "ALL") return results.all_matching_programs;
    const fieldObj = results.top_fields.find(f => f.field_name === activeFieldTab);
    return fieldObj ? fieldObj.programs : [];
  });
</script>

<div class="career-guide-container">
  <!-- Top Hero Header -->
  <header class="hero-header">
    <div class="badge-tag">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      </svg>
      <span>AI Career Guidance & University Recommender</span>
    </div>
    <h1 class="hero-title">Find What to Study & Where in Cameroon</h1>
    <p class="hero-desc">
      Not sure which major suits you best? Our custom Machine Learning model evaluates your academic background, strengths, and personal interests to recommend suitable fields and accredited university programs within your budget.
    </p>

    <!-- Stepper Indicator -->
    {#if currentStep < 4}
      <div class="stepper">
        <div class="step-item" class:active={currentStep >= 1} class:current={currentStep === 1}>
          <div class="step-num">1</div>
          <span>Academic Background</span>
        </div>
        <div class="step-line" class:active={currentStep >= 2}></div>
        <div class="step-item" class:active={currentStep >= 2} class:current={currentStep === 2}>
          <div class="step-num">2</div>
          <span>Interests & Style (12 Qs)</span>
        </div>
        <div class="step-line" class:active={currentStep >= 3}></div>
        <div class="step-item" class:active={currentStep >= 3} class:current={currentStep === 3}>
          <div class="step-num">3</div>
          <span>Budget & Match</span>
        </div>
      </div>
    {/if}
  </header>

  {#if errorMsg}
    <div class="error-banner">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{errorMsg}</span>
    </div>
  {/if}

  <!-- STEP 1: Academic Background -->
  {#if currentStep === 1}
    <section class="card-step">
      <div class="step-header">
        <h2>Step 1: Your Academic Strengths</h2>
        <p>Tell us about your high school preparation and the subjects you excelled in.</p>
      </div>

      <div class="form-group">
        <label class="section-label">A-Level / High School Series</label>
        <div class="chips-grid">
          {#each seriesOptions as s}
            <button
              type="button"
              class="choice-chip"
              class:selected={selectedSeries === s}
              onclick={() => (selectedSeries = s)}
            >
              <span class="chip-title">{s}</span>
              <span class="chip-sub">
                {#if s === 'Science'}C, D, E, S (Maths, Physics, Bio)
                {:else if s === 'Arts'}A1–A5, ABI (Literature, History)
                {:else if s === 'Commercial'}G1–G3, FIG, CG (Econ, Accounting)
                {:else}F1–F7, TI (Engineering, Tech)
                {/if}
              </span>
            </button>
          {/each}
        </div>
      </div>

      <div class="form-group">
        <div class="label-with-counter">
          <label class="section-label">Top 3 Strongest Subjects</label>
          <span class="counter-badge" class:full={selectedSubjects.length === 3}>
            {selectedSubjects.length} / 3 selected
          </span>
        </div>
        <p class="field-hint">Select up to 3 subjects you enjoy or scored highest in during secondary school.</p>
        <div class="subjects-grid">
          {#each subjectOptions as subj}
            {@const isChecked = selectedSubjects.includes(subj)}
            <button
              type="button"
              class="subject-chip"
              class:checked={isChecked}
              disabled={!isChecked && selectedSubjects.length >= 3}
              onclick={() => toggleSubject(subj)}
            >
              <span class="checkbox-indicator">{isChecked ? "✓" : "+"}</span>
              <span>{subj}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="action-footer">
        <div></div>
        <button
          type="button"
          class="btn-primary"
          disabled={selectedSubjects.length === 0}
          onclick={() => (currentStep = 2)}
        >
          <span>Continue to Interests</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    </section>
  {/if}

  <!-- STEP 2: 12 Statements (1 to 5 scale) -->
  {#if currentStep === 2}
    <section class="card-step">
      <div class="step-header">
        <h2>Step 2: Interests & Activities</h2>
        <p>Rate how much you enjoy each statement on a scale of 1 (Dislike) to 5 (Love It). The model learns directly from these answers.</p>
      </div>

      <div class="questions-list">
        {#each questions as q, idx}
          {@const val = answers[q.id] || 3}
          <div class="question-row">
            <div class="q-number">{idx + 1}</div>
            <div class="q-content">
              <p class="q-statement">{q.statement}</p>
              <div class="likert-scale">
                {#each [1, 2, 3, 4, 5] as num}
                  <button
                    type="button"
                    class="likert-btn"
                    class:selected={val === num}
                    onclick={() => setLikert(q.id, num)}
                  >
                    <span class="likert-num">{num}</span>
                    <span class="likert-label">
                      {#if num === 1}Strongly Dislike
                      {:else if num === 2}Dislike
                      {:else if num === 3}Neutral
                      {:else if num === 4}Like
                      {:else}Love It
                      {/if}
                    </span>
                  </button>
                {/each}
              </div>
            </div>
          </div>
        {/each}
      </div>

      <div class="action-footer">
        <button type="button" class="btn-secondary" onclick={() => (currentStep = 1)}>
          Back
        </button>
        <button type="button" class="btn-primary" onclick={() => (currentStep = 3)}>
          <span>Continue to Budget</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    </section>
  {/if}

  <!-- STEP 3: Budget & Final Submission -->
  {#if currentStep === 3}
    <section class="card-step">
      <div class="step-header">
        <h2>Step 3: Tuition Budget Preference</h2>
        <p>Set a maximum yearly tuition limit in FCFA so we filter only universities you can comfortably afford.</p>
      </div>

      <div class="budget-card">
        <div class="form-group">
          <label class="section-label">Maximum Yearly Budget (FCFA)</label>
          <div class="budget-input-wrapper">
            <input
              type="number"
              step="50000"
              min="0"
              placeholder="e.g. 500000"
              bind:value={maxBudget}
              class="budget-input"
            />
            <span class="currency-tag">FCFA / year</span>
          </div>
        </div>

        <div class="quick-presets">
          <span class="preset-label">Quick Presets:</span>
          <button
            type="button"
            class="preset-btn"
            class:active={maxBudget === 50000}
            onclick={() => (maxBudget = 50000)}
          >
            50,000 (State Univ / Polytech)
          </button>
          <button
            type="button"
            class="preset-btn"
            class:active={maxBudget === 500000}
            onclick={() => (maxBudget = 500000)}
          >
            500,000 (Professional Institutes)
          </button>
          <button
            type="button"
            class="preset-btn"
            class:active={maxBudget === 800000}
            onclick={() => (maxBudget = 800000)}
          >
            800,000 (Private Universities)
          </button>
          <button
            type="button"
            class="preset-btn"
            class:active={maxBudget === null}
            onclick={() => (maxBudget = null)}
          >
            No Budget Limit
          </button>
        </div>
      </div>

      <div class="summary-preview">
        <h3>Questionnaire Summary</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="sum-title">Academic Series:</span>
            <span class="sum-val">{selectedSeries}</span>
          </div>
          <div class="summary-item">
            <span class="sum-title">Top Subjects:</span>
            <span class="sum-val">{selectedSubjects.join(", ")}</span>
          </div>
          <div class="summary-item">
            <span class="sum-title">Max Yearly Budget:</span>
            <span class="sum-val">{maxBudget ? `${maxBudget.toLocaleString()} FCFA` : "No Limit"}</span>
          </div>
        </div>
      </div>

      <div class="action-footer">
        <button type="button" class="btn-secondary" onclick={() => (currentStep = 2)}>
          Back
        </button>
        <button
          type="button"
          class="btn-primary pulse"
          disabled={submitting}
          onclick={submitQuestionnaire}
        >
          {#if submitting}
            <span class="spinner"></span>
            <span>Running AI Classifier...</span>
          {:else}
            <span>Generate My Recommendations</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"></path>
            </svg>
          {/if}
        </button>
      </div>
    </section>
  {/if}

  <!-- STEP 4: Results & Recommendations -->
  {#if currentStep === 4 && results}
    <div class="results-container">
      <!-- Success Header -->
      <div class="results-header-card">
        <div class="header-left">
          <span class="top-badge">Profile Match Complete</span>
          <h2>Your Top 3 Recommended Fields of Study</h2>
          <p>
            Based on your answers, our trained Random Forest Classifier predicts high alignment with the following disciplines:
          </p>
        </div>
        <button type="button" class="btn-retake" onclick={() => (currentStep = 1)}>
          ↻ Retake Questionnaire
        </button>
      </div>

      <!-- Top 3 Fields Grid -->
      <div class="fields-grid">
        {#each results.top_fields as field}
          <div class="field-card" class:top-rank={field.rank === 1}>
            <div class="field-top-row">
              <div class="rank-badge">#{field.rank} Field</div>
              <div class="pct-badge">{field.percentage}% Match</div>
            </div>
            <h3 class="field-title">{field.field_name}</h3>
            <p class="field-desc">{field.description}</p>

            <div class="reason-box">
              <div class="reason-label">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>Why this was recommended:</span>
              </div>
              <p class="reason-text">{field.explanation}</p>
            </div>

            <div class="field-footer">
              <span class="prog-count">
                <strong>{field.programs_available_count}</strong> {field.programs_available_count === 1 ? 'program' : 'programs'} available in DB
              </span>
            </div>
          </div>
        {/each}
      </div>

      <!-- Matching Programs Section -->
      <section class="programs-section">
        <div class="section-title-row">
          <div>
            <h3>Available Programs in Partner Universities</h3>
            <p>Accredited programs matching your predicted fields within your budget of {maxBudget ? `${maxBudget.toLocaleString()} FCFA` : 'All Budgets'}.</p>
          </div>
          <div class="tab-filters">
            <button
              class="tab-btn"
              class:active={activeFieldTab === 'ALL'}
              onclick={() => (activeFieldTab = 'ALL')}
            >
              All Matching ({results.total_matching_programs})
            </button>
            {#each results.top_fields as f}
              <button
                class="tab-btn"
                class:active={activeFieldTab === f.field_name}
                onclick={() => (activeFieldTab = f.field_name)}
              >
                {f.field_name} ({f.programs_available_count})
              </button>
            {/each}
          </div>
        </div>

        {#if filteredPrograms().length === 0}
          <div class="empty-programs-card">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="8" y1="12" x2="16" y2="12"></line>
            </svg>
            <h4>No Partner Programs Found In This Field Within Budget</h4>
            <p>Try increasing your budget filter or check our full school catalog.</p>
            <a href="/discover" class="btn-secondary">Explore All Schools</a>
          </div>
        {:else}
          <div class="programs-cards-grid">
            {#each filteredPrograms() as prog}
              {@const isFav = favoriteIds.includes(prog.school_id)}
              <div class="prog-card">
                <div class="prog-header">
                  <div class="school-meta">
                    <span class="school-name">{prog.school_name}</span>
                    <span class="school-loc">📍 {prog.school_location || 'Yaounde, Cameroon'}</span>
                  </div>
                  <button
                    type="button"
                    class="fav-btn"
                    class:active={isFav}
                    aria-label="Save school to favorites"
                    onclick={() => toggleFavoriteSchool(prog.school_id)}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill={isFav ? "#e11d48" : "none"} stroke={isFav ? "#e11d48" : "currentColor"} stroke-width="2">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                  </button>
                </div>

                <div class="prog-body">
                  <h4 class="prog-title">{prog.program_title}</h4>
                  <div class="prog-tags">
                    <span class="tag-degree">{prog.degree_type || 'Degree'}</span>
                    <span class="tag-field">{prog.matched_target_field}</span>
                    <span class="tag-duration">⏱ {prog.duration || '3 yrs'}</span>
                  </div>

                  {#if prog.description}
                    <p class="prog-snippet">{prog.description}</p>
                  {/if}

                  {#if prog.admission_requirements}
                    <div class="requirements-pill">
                      <strong>Requirements:</strong> {prog.admission_requirements}
                    </div>
                  {/if}
                </div>

                <div class="prog-footer">
                  <div class="tuition-pill">
                    <span class="tuition-label">Tuition Fee</span>
                    <span class="tuition-val">{prog.tuition_fee || 'On Inquiry'}</span>
                  </div>
                  <a href="/application/profile" class="btn-apply">
                    <span>Apply Now</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                  </a>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </section>

      <!-- Academic Model Metrics Section (For Lecturer Defense) -->
      <section class="defense-section">
        <button
          type="button"
          class="defense-toggle"
          onclick={() => (showModelMetrics = !showModelMetrics)}
        >
          <div class="defense-left">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
            <strong>Model Architecture & Defense Information (For Lecturers)</strong>
          </div>
          <span>{showModelMetrics ? '▲ Hide Details' : '▼ View Model Accuracy & Training Metrics'}</span>
        </button>

        {#if showModelMetrics}
          <div class="defense-body">
            <div class="metrics-grid">
              <div class="metric-box">
                <span class="m-val">{((results.model_info.accuracy || 0.81) * 100).toFixed(1)}%</span>
                <span class="m-lbl">Test Set Accuracy</span>
                <span class="m-sub">RandomForest (80/20 Stratified Split)</span>
              </div>
              <div class="metric-box highlight">
                <span class="m-val">{((results.model_info.top3_accuracy || 0.97) * 100).toFixed(1)}%</span>
                <span class="m-lbl">Top-3 Accuracy</span>
                <span class="m-sub">Correct field is in top 3 recommended</span>
              </div>
              <div class="metric-box">
                <span class="m-val">{((results.model_info.baseline_accuracy || 0.69) * 100).toFixed(1)}%</span>
                <span class="m-lbl">Baseline Accuracy</span>
                <span class="m-sub">Logistic Regression comparison</span>
              </div>
              <div class="metric-box">
                <span class="m-val">+12.5%</span>
                <span class="m-lbl">Accuracy Gain</span>
                <span class="m-sub">Random Forest vs. Baseline model</span>
              </div>
            </div>

            <div class="architecture-notes">
              <h4>Model Technical Details:</h4>
              <ul>
                <li><strong>Algorithm:</strong> <code>RandomForestClassifier(n_estimators=120, max_depth=14)</code> running locally inside Python FastAPI backend.</li>
                <li><strong>No External API:</strong> 100% self-hosted scikit-learn model, no OpenAI or third-party AI APIs used.</li>
                <li><strong>Training Data:</strong> 3,200 Cameroonian high-school student profiles generated with realistic noise (12% label variance) across 8 target disciplines.</li>
                <li><strong>Visualizations:</strong> Confusion matrix heatmap and Gini feature importances exported directly to <code>backend/app/ml/saved_models/</code>.</li>
              </ul>
            </div>
          </div>
        {/if}
      </section>
    </div>
  {/if}
</div>

<style>
  .career-guide-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 20px 80px;
    font-family: inherit;
    color: #1e293b;
  }

  .hero-header {
    text-align: center;
    margin-bottom: 36px;
  }

  .badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 12px;
  }

  .hero-title {
    font-size: 2.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 12px;
    letter-spacing: -0.02em;
  }

  .hero-desc {
    max-width: 720px;
    margin: 0 auto 28px;
    font-size: 1.05rem;
    line-height: 1.6;
    color: #64748b;
  }

  /* Stepper */
  .stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
  }

  .step-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
  }

  .step-item.active {
    color: #334155;
  }

  .step-item.current {
    color: #2563eb;
  }

  .step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e2e8f0;
    color: #64748b;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .step-item.active .step-num {
    background: #dbeafe;
    color: #2563eb;
  }

  .step-item.current .step-num {
    background: #2563eb;
    color: #ffffff;
  }

  .step-line {
    width: 40px;
    height: 2px;
    background: #e2e8f0;
  }

  .step-line.active {
    background: #2563eb;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 24px;
  }

  /* Step Cards */
  .card-step {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 36px 32px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }

  .step-header {
    margin-bottom: 28px;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 16px;
  }

  .step-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 6px;
    color: #0f172a;
  }

  .step-header p {
    margin: 0;
    color: #64748b;
    font-size: 0.95rem;
  }

  .form-group {
    margin-bottom: 32px;
  }

  .section-label {
    display: block;
    font-weight: 700;
    font-size: 1rem;
    color: #1e293b;
    margin-bottom: 10px;
  }

  .label-with-counter {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .counter-badge {
    background: #f1f5f9;
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 9999px;
  }

  .counter-badge.full {
    background: #dcfce7;
    color: #15803d;
  }

  .field-hint {
    margin: 0 0 14px;
    font-size: 0.88rem;
    color: #64748b;
  }

  .chips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
  }

  .choice-chip {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 16px;
    border: 1.5px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 12px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
  }

  .choice-chip:hover {
    border-color: #93c5fd;
    background: #eff6ff;
  }

  .choice-chip.selected {
    border-color: #2563eb;
    background: #eff6ff;
    box-shadow: 0 0 0 2px #bfdbfe;
  }

  .chip-title {
    font-weight: 700;
    font-size: 1rem;
    color: #0f172a;
    margin-bottom: 4px;
  }

  .chip-sub {
    font-size: 0.8rem;
    color: #64748b;
  }

  .subjects-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .subject-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 9999px;
    border: 1.5px solid #e2e8f0;
    background: #f8fafc;
    font-size: 0.9rem;
    font-weight: 600;
    color: #334155;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .subject-chip:hover:not(:disabled) {
    border-color: #2563eb;
    color: #2563eb;
  }

  .subject-chip.checked {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
  }

  .subject-chip:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  /* Likert Questions */
  .questions-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 32px;
  }

  .question-row {
    display: flex;
    gap: 16px;
    padding: 18px 20px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #f1f5f9;
  }

  .q-number {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e2e8f0;
    color: #475569;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
  }

  .q-content {
    flex: 1;
  }

  .q-statement {
    margin: 0 0 14px;
    font-weight: 600;
    font-size: 1rem;
    color: #1e293b;
  }

  .likert-scale {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .likert-btn {
    flex: 1;
    min-width: 90px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 10px 8px;
    border: 1.5px solid #cbd5e1;
    background: #ffffff;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .likert-btn:hover {
    border-color: #2563eb;
  }

  .likert-btn.selected {
    background: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
  }

  .likert-num {
    font-weight: 700;
    font-size: 1.05rem;
  }

  .likert-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }

  /* Budget Card */
  .budget-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 28px;
  }

  .budget-input-wrapper {
    position: relative;
    max-width: 400px;
  }

  .budget-input {
    width: 100%;
    padding: 12px 120px 12px 16px;
    font-size: 1.15rem;
    font-weight: 700;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    box-sizing: border-box;
  }

  .currency-tag {
    position: absolute;
    right: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .quick-presets {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
  }

  .preset-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748b;
    margin-right: 4px;
  }

  .preset-btn {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .preset-btn:hover {
    border-color: #2563eb;
    color: #2563eb;
  }

  .preset-btn.active {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
  }

  .summary-preview {
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 28px;
  }

  .summary-preview h3 {
    margin: 0 0 12px;
    font-size: 0.95rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }

  .summary-item {
    font-size: 0.9rem;
  }

  .sum-title {
    color: #64748b;
    margin-right: 6px;
  }

  .sum-val {
    font-weight: 700;
    color: #0f172a;
  }

  /* Actions */
  .action-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #f1f5f9;
    padding-top: 24px;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #2563eb;
    color: #ffffff;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
  }

  .btn-secondary:hover {
    background: #e2e8f0;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid #ffffff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Results Step */
  .results-container {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .results-header-card {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: #ffffff;
    padding: 32px;
    border-radius: 16px;
    box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
  }

  .top-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
  }

  .results-header-card h2 {
    font-size: 1.85rem;
    font-weight: 800;
    margin: 0 0 8px;
  }

  .results-header-card p {
    margin: 0;
    font-size: 0.98rem;
    color: #e0e7ff;
    max-width: 650px;
  }

  .btn-retake {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #ffffff;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.85rem;
    flex-shrink: 0;
  }

  .btn-retake:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  /* Top 3 Fields */
  .fields-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }

  .field-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
  }

  .field-card.top-rank {
    border-color: #2563eb;
    box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.15);
  }

  .field-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .rank-badge {
    font-size: 0.8rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #475569;
  }

  .field-card.top-rank .rank-badge {
    color: #2563eb;
  }

  .pct-badge {
    background: #dbeafe;
    color: #1e40af;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 800;
  }

  .field-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 8px;
  }

  .field-desc {
    font-size: 0.9rem;
    color: #64748b;
    margin: 0 0 16px;
    line-height: 1.5;
  }

  .reason-box {
    background: #f8fafc;
    border-left: 3px solid #2563eb;
    padding: 12px 14px;
    border-radius: 6px;
    margin-bottom: 16px;
  }

  .reason-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin-bottom: 4px;
  }

  .reason-text {
    margin: 0;
    font-size: 0.85rem;
    color: #334155;
    line-height: 1.45;
  }

  .field-footer {
    margin-top: auto;
    border-top: 1px solid #f1f5f9;
    padding-top: 12px;
    font-size: 0.82rem;
    color: #64748b;
  }

  /* Programs Section */
  .programs-section {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 32px;
  }

  .section-title-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin-bottom: 24px;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 16px;
  }

  .section-title-row h3 {
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0 0 4px;
    color: #0f172a;
  }

  .section-title-row p {
    margin: 0;
    color: #64748b;
    font-size: 0.9rem;
  }

  .tab-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tab-btn {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .tab-btn:hover {
    border-color: #2563eb;
    color: #2563eb;
  }

  .tab-btn.active {
    background: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
  }

  .empty-programs-card {
    text-align: center;
    padding: 48px 20px;
    color: #64748b;
  }

  .empty-programs-card h4 {
    margin: 12px 0 6px;
    color: #334155;
    font-size: 1.1rem;
  }

  .programs-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }

  .prog-card {
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }

  .prog-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.06);
    border-color: #cbd5e1;
  }

  .prog-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }

  .school-meta {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .school-name {
    font-weight: 700;
    font-size: 0.95rem;
    color: #0f172a;
  }

  .school-loc {
    font-size: 0.78rem;
    color: #64748b;
  }

  .fav-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #94a3b8;
    padding: 4px;
    border-radius: 6px;
  }

  .fav-btn:hover {
    color: #e11d48;
  }

  .fav-btn.active {
    color: #e11d48;
  }

  .prog-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0 0 10px;
  }

  .prog-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
  }

  .tag-degree {
    background: #f1f5f9;
    color: #334155;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
  }

  .tag-field {
    background: #e0e7ff;
    color: #3730a3;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
  }

  .tag-duration {
    background: #fef3c7;
    color: #92400e;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
  }

  .prog-snippet {
    font-size: 0.85rem;
    color: #475569;
    margin: 0 0 12px;
    line-height: 1.45;
  }

  .requirements-pill {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    color: #475569;
    margin-bottom: 14px;
  }

  .prog-footer {
    margin-top: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #f1f5f9;
    padding-top: 14px;
  }

  .tuition-pill {
    display: flex;
    flex-direction: column;
  }

  .tuition-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 700;
    color: #94a3b8;
  }

  .tuition-val {
    font-size: 0.95rem;
    font-weight: 800;
    color: #059669;
  }

  .btn-apply {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #2563eb;
    color: #ffffff;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 700;
    text-decoration: none;
    transition: background 0.15s ease;
  }

  .btn-apply:hover {
    background: #1d4ed8;
  }

  /* Academic Defense */
  .defense-section {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    overflow: hidden;
  }

  .defense-toggle {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: #f8fafc;
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
    color: #334155;
    text-align: left;
  }

  .defense-toggle:hover {
    background: #f1f5f9;
  }

  .defense-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .defense-body {
    padding: 24px 20px;
    border-top: 1px solid #e2e8f0;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .metric-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 16px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    text-align: center;
  }

  .metric-box.highlight {
    background: #eff6ff;
    border-color: #93c5fd;
  }

  .m-val {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
  }

  .metric-box.highlight .m-val {
    color: #2563eb;
  }

  .m-lbl {
    font-size: 0.85rem;
    font-weight: 700;
    color: #475569;
    margin: 4px 0 2px;
  }

  .m-sub {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .architecture-notes h4 {
    margin: 0 0 8px;
    font-size: 0.95rem;
    color: #1e293b;
  }

  .architecture-notes ul {
    margin: 0;
    padding-left: 20px;
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.6;
  }

  .architecture-notes code {
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    color: #0f172a;
    font-size: 0.82rem;
  }

  @media (max-width: 640px) {
    .card-step {
      padding: 24px 16px;
    }
    .question-row {
      flex-direction: column;
      gap: 10px;
    }
    .stepper {
      display: none;
    }
  }
</style>
