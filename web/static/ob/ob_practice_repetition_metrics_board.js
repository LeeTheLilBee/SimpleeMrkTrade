// OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_JS

(function () {
  const VERSION = "OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD";
  const ENDPOINT = "/ob/practice-repetition-metrics-board.json";

  // SMOKE MARKERS
  // Practice Repetition Metrics Board
  // practice repetition metrics
  // repetition count
  // practice streak placeholder
  // completion trend
  // blocker trend
  // confusion reduction trend
  // clean moment trend
  // unsafe moment trend
  // lesson category metrics
  // account practice distribution
  // candidate type practice distribution
  // next practice focus
  // owner review polish layer
  // readiness trend dry run
  // no database write
  // no file write
  // no save endpoint
  // no real record creation
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let metricsState = {
    status: "booting",
    httpStatus: null,
    source: "fallback",
    payload: null,
    fallbackActive: true,
    error: null
  };

  function safeText(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return String(value);
  }

  function buildFallbackPayload() {
    return {
      version: VERSION,
      source: "ob_giant_pack_026_safe_fallback",
      board_state: {
        board_id: "ob_practice_repetition_metrics_board_001",
        label: "Practice Repetition Metrics Board",
        status: "practice_repetition_metrics_ready",
        section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        purpose: "Show dry-run repetition metrics, trend placeholders, and next-practice focus without saving records.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        practice_loop_source: "/ob/owner-practice-loop-board.json",
        lesson_queue_source: "/ob/practice-lesson-review-queue.json",
        readiness_source: "/ob/owner-practice-loop-readiness-checkpoint.json"
      },
      repetition_summary: {
        total_practice_runs: 12,
        completed_runs: 7,
        active_runs: 1,
        blocked_runs: 2,
        incomplete_runs: 2,
        average_completion_percent: 74,
        repeat_recommended_count: 5,
        current_streak_placeholder: "not_enabled",
        best_streak_placeholder: "not_enabled",
        status: "ready"
      },
      repetition_trends: [
        {
          trend_id: "completion_trend",
          label: "Completion trend",
          purpose: "Tracks whether practice sessions are reaching final review more often.",
          direction: "improving",
          current_value: "74%",
          prior_value: "62%",
          status: "ready"
        },
        {
          trend_id: "blocker_trend",
          label: "Blocker trend",
          purpose: "Tracks blocker frequency across repeated practice.",
          direction: "declining",
          current_value: "2 active blockers",
          prior_value: "4 active blockers",
          status: "ready"
        },
        {
          trend_id: "confusion_reduction_trend",
          label: "Confusion reduction trend",
          purpose: "Tracks whether confusion flags are reducing.",
          direction: "watch",
          current_value: "3 confusion flags",
          prior_value: "4 confusion flags",
          status: "watch"
        },
        {
          trend_id: "clean_moment_trend",
          label: "Clean moment trend",
          purpose: "Tracks repeatable clean moments.",
          direction: "improving",
          current_value: "5 clean moments",
          prior_value: "2 clean moments",
          status: "ready"
        },
        {
          trend_id: "unsafe_moment_trend",
          label: "Unsafe moment trend",
          purpose: "Tracks unsafe moments that need owner review.",
          direction: "declining",
          current_value: "1 unsafe moment",
          prior_value: "3 unsafe moments",
          status: "ready"
        }
      ],
      lesson_category_metrics: [
        {
          category_id: "checklist_lesson",
          label: "Checklist lessons",
          total_lessons: 4,
          pending_lessons: 2,
          completed_lessons: 1,
          repeat_recommended: 2,
          next_focus: "Repeat checklist/fill path.",
          status: "needs_review"
        },
        {
          category_id: "capital_rule_lesson",
          label: "Capital rule lessons",
          total_lessons: 2,
          pending_lessons: 0,
          completed_lessons: 1,
          repeat_recommended: 1,
          next_focus: "Compare Proof/Demo vs protected reserve account.",
          status: "ready"
        },
        {
          category_id: "confidence_lesson",
          label: "Confidence lessons",
          total_lessons: 3,
          pending_lessons: 1,
          completed_lessons: 2,
          repeat_recommended: 1,
          next_focus: "Run option-style candidate and compare confidence.",
          status: "ready"
        },
        {
          category_id: "safety_lesson",
          label: "Safety lessons",
          total_lessons: 3,
          pending_lessons: 1,
          completed_lessons: 0,
          repeat_recommended: 1,
          next_focus: "Review dry-run save and Tower locks.",
          status: "watch"
        }
      ],
      account_practice_distribution: [
        {
          account_id: "proof_demo",
          label: "Proof/Demo OB Account",
          practice_runs: 8,
          completion_rate: "88%",
          purpose: "Primary safe owner rehearsal account.",
          status: "ready"
        },
        {
          account_id: "trust",
          label: "Trust OB Account",
          practice_runs: 2,
          completion_rate: "50%",
          purpose: "Trust account boundary learning only.",
          status: "watch"
        },
        {
          account_id: "apartment",
          label: "SimpleeProperty / Apartment OB Account",
          practice_runs: 2,
          completion_rate: "0%",
          purpose: "Protected reserve block rehearsal only.",
          status: "locked"
        }
      ],
      candidate_type_distribution: [
        {
          candidate_type: "option_style_fake_candidate",
          label: "Option-style fake candidate",
          practice_runs: 6,
          completion_rate: "67%",
          next_focus: "Checklist/fill path confidence.",
          status: "watch"
        },
        {
          candidate_type: "stock_fallback_rehearsal",
          label: "Stock fallback rehearsal",
          practice_runs: 4,
          completion_rate: "100%",
          next_focus: "Compare against option-style path.",
          status: "ready"
        },
        {
          candidate_type: "capital_block_rehearsal",
          label: "Capital block rehearsal",
          practice_runs: 2,
          completion_rate: "0%",
          next_focus: "Keep reserves protected and use Proof/Demo for practice.",
          status: "locked"
        }
      ],
      next_practice_focus: [
        {
          focus_id: "repeat_checklist_fill_path",
          label: "Repeat checklist/fill path",
          reason: "Highest confusion and missed-step flags are tied to checklist/fill.",
          suggested_account: "Proof/Demo OB Account",
          suggested_candidate_type: "option_style_fake_candidate",
          status: "recommended"
        },
        {
          focus_id: "compare_option_vs_stock_fallback",
          label: "Compare option vs stock fallback",
          reason: "Stock fallback is clean; option-style path still needs confidence.",
          suggested_account: "Proof/Demo OB Account",
          suggested_candidate_type: "option_style_fake_candidate",
          status: "recommended"
        },
        {
          focus_id: "review_capital_boundary",
          label: "Review capital boundary",
          reason: "Apartment reserve block should stay locked and understood.",
          suggested_account: "SimpleeProperty / Apartment OB Account",
          suggested_candidate_type: "capital_block_rehearsal",
          status: "locked_review"
        }
      ],
      review_polish_targets: [
        {
          target_id: "make_metrics_owner_readable",
          label: "Make metrics owner-readable",
          purpose: "Summarize metrics in plain owner language.",
          status: "ready"
        },
        {
          target_id: "show_why_repeat_needed",
          label: "Show why repeat is needed",
          purpose: "Explain the reason for repetition without implying failure.",
          status: "ready"
        },
        {
          target_id: "keep_real_live_separate",
          label: "Keep real live separate",
          purpose: "Make it obvious metrics are practice-only, not real Manual Live.",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_repetition_metrics_database_now",
        "write_repetition_metrics_file_now",
        "create_metrics_save_endpoint_now",
        "persist_streak_now",
        "persist_repetition_counter_now",
        "create_real_metrics_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_metrics_board",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_metrics_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_repetition_metrics_board_only: true,
        dry_run_only: true,
        metrics_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};
    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      board_state: { ...(fallback.board_state || {}), ...(safe.board_state || {}) },
      repetition_summary: { ...(fallback.repetition_summary || {}), ...(safe.repetition_summary || {}) },
      repetition_trends: Array.isArray(safe.repetition_trends) ? safe.repetition_trends : fallback.repetition_trends,
      lesson_category_metrics: Array.isArray(safe.lesson_category_metrics) ? safe.lesson_category_metrics : fallback.lesson_category_metrics,
      account_practice_distribution: Array.isArray(safe.account_practice_distribution) ? safe.account_practice_distribution : fallback.account_practice_distribution,
      candidate_type_distribution: Array.isArray(safe.candidate_type_distribution) ? safe.candidate_type_distribution : fallback.candidate_type_distribution,
      next_practice_focus: Array.isArray(safe.next_practice_focus) ? safe.next_practice_focus : fallback.next_practice_focus,
      review_polish_targets: Array.isArray(safe.review_polish_targets) ? safe.review_polish_targets : fallback.review_polish_targets,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_repetition_metrics_board_only: true,
        dry_run_only: true,
        metrics_preview_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_real_record_creation: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        not_real_manual_live_ready: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRACTICE_REPETITION_METRICS_BOARD_GP026 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      practice_repetition_metrics_board_gp026: normalized,
      practiceRepetitionMetricsBoardOnly: true,
      dryRunOnly: true,
      metricsPreviewOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obPracticeRepetitionMetricsBoardUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchMetrics() {
    metricsState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      metricsState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        metricsState.status = "ready";
        metricsState.source = normalized.source || "server";
        metricsState.payload = normalized;
        metricsState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        metricsState.status = "guarded_fallback";
        metricsState.source = "guarded_fallback";
        metricsState.payload = fallback;
        metricsState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      metricsState.status = "error_fallback";
      metricsState.source = "error_fallback";
      metricsState.payload = fallback;
      metricsState.fallbackActive = true;
      metricsState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return metricsState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("declining") || text.includes("unsafe")) return "red";
    if (text.includes("ready") || text.includes("improving") || text.includes("recommended")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-practice-repetition-metrics-board-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-practice-repetition-metrics-board-row">
        <div class="ob-practice-repetition-metrics-board-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.trend_id || item.category_id || item.account_id || item.candidate_type || item.focus_id || item.target_id, "Item")}</strong>
          <span>${safeText(item.status || item.direction || item.completion_rate || "metric", "metric")}</span>
        </div>
        <span>${safeText(item.purpose || item.reason || item.next_focus || item.recommendation || "detail", "detail")}</span>
        <div class="ob-practice-repetition-metrics-board-status ${tone(item.status || item.direction)}">${safeText(item.status || item.direction || "ready", "ready")}</div>
      </div>
    `;
  }

  function focusRow(item) {
    return `
      <div class="ob-practice-repetition-metrics-board-row">
        <div class="ob-practice-repetition-metrics-board-dot">F</div>
        <div>
          <strong>${safeText(item.label, "Focus")}</strong>
          <span>${safeText(item.status, "recommended")}</span>
        </div>
        <span>
          Reason: ${safeText(item.reason, "reason")}<br>
          Account: ${safeText(item.suggested_account, "account")}<br>
          Candidate type: ${safeText(item.suggested_candidate_type, "candidate")}
        </span>
        <div class="ob-practice-repetition-metrics-board-status ${tone(item.status)}">${safeText(item.status, "recommended")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-practice-repetition-metrics-board-row">
        <div class="ob-practice-repetition-metrics-board-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP026 repetition metrics boundaries.</span>
        <div class="ob-practice-repetition-metrics-board-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = metricsState.payload || buildFallbackPayload();
    const state = payload.board_state || {};
    const summary = payload.repetition_summary || {};
    const trends = Array.isArray(payload.repetition_trends) ? payload.repetition_trends : [];
    const lessonMetrics = Array.isArray(payload.lesson_category_metrics) ? payload.lesson_category_metrics : [];
    const accounts = Array.isArray(payload.account_practice_distribution) ? payload.account_practice_distribution : [];
    const candidates = Array.isArray(payload.candidate_type_distribution) ? payload.candidate_type_distribution : [];
    const focus = Array.isArray(payload.next_practice_focus) ? payload.next_practice_focus : [];
    const polish = Array.isArray(payload.review_polish_targets) ? payload.review_polish_targets : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-practice-repetition-metrics-board-panel" id="obPracticeRepetitionMetricsBoardPanel" data-ob-giant-pack-026="true">
        <div class="ob-practice-repetition-metrics-board-head">
          <div>
            <div class="ob-label">OB Giant Pack 026 · Practice Metrics</div>
            <div class="ob-practice-repetition-metrics-board-title">Practice Repetition Metrics Board</div>
            <div class="ob-practice-repetition-metrics-board-subtitle">
              ${safeText(metricsState.status, "booting")} · ${safeText(state.status, "practice_repetition_metrics_ready")} · dry-run metrics preview.
            </div>
          </div>
          <div class="ob-practice-repetition-metrics-board-chip-row">
            <span class="ob-practice-repetition-metrics-board-chip green">Repetition metrics</span>
            <span class="ob-practice-repetition-metrics-board-chip gold">Next focus</span>
            <span class="ob-practice-repetition-metrics-board-chip red">No DB write</span>
            <span class="ob-practice-repetition-metrics-board-chip red">Not real Manual Live</span>
          </div>
        </div>

        <div class="ob-practice-repetition-metrics-board-stat-grid">
          ${card("Runs", safeText(summary.total_practice_runs, "0"))}
          ${card("Complete", safeText(summary.completed_runs, "0"))}
          ${card("Blocked", safeText(summary.blocked_runs, "0"))}
          ${card("Avg", safeText(summary.average_completion_percent, "0") + "%")}
          ${card("Repeat", safeText(summary.repeat_recommended_count, "0"))}
        </div>

        <div class="ob-practice-repetition-metrics-board-grid">
          <div>
            <div class="ob-practice-repetition-metrics-board-card">
              <span>Purpose</span>
              <strong>Show owner practice repetition metrics, trends, and next-focus recommendations without saving metrics.</strong>
              <div class="ob-practice-repetition-metrics-board-callout">
                <strong>Metrics preview:</strong><br>
                This board is dry-run only. It helps you see practice progress without creating records or enabling live trading.
              </div>
              <div class="ob-practice-repetition-metrics-board-boundary">
                <strong>Boundary:</strong><br>
                No database write. No save endpoint. No real record. No broker/bank action. No direct Vault upload.
              </div>
            </div>

            <div class="ob-practice-repetition-metrics-board-card" style="margin-top: 11px;">
              <span>Streak placeholders</span>
              <strong>Current: ${safeText(summary.current_streak_placeholder, "not_enabled")} · Best: ${safeText(summary.best_streak_placeholder, "not_enabled")}</strong>
              <div class="ob-practice-repetition-metrics-board-callout">
                Streaks are placeholders only until real persistence exists.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Repetition trends</div>
              <div class="ob-practice-repetition-metrics-board-list">${trends.map((item, index) => row(item, index, "T")).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Lesson category metrics</div>
              <div class="ob-practice-repetition-metrics-board-list">${lessonMetrics.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Account practice distribution</div>
              <div class="ob-practice-repetition-metrics-board-list">${accounts.map((item, index) => row(item, index, "A")).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Candidate type distribution</div>
              <div class="ob-practice-repetition-metrics-board-list">${candidates.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Next practice focus</div>
              <div class="ob-practice-repetition-metrics-board-list">${focus.map(focusRow).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Owner review polish targets</div>
              <div class="ob-practice-repetition-metrics-board-list">${polish.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-practice-repetition-metrics-board-section">
              <div class="ob-practice-repetition-metrics-board-section-title">Blocked actions</div>
              <div class="ob-practice-repetition-metrics-board-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-practice-repetition-metrics-board-callout">
          <strong>Next handoff:</strong><br>
          GP027 can add Owner Review Polish Copy + Guidance so metrics read cleanly and calmly.
        </div>

        <div class="ob-practice-repetition-metrics-board-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPracticeRepetitionMetricsBoardPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const checkpoint = document.getElementById("obOwnerPracticeLoopReadinessCheckpointPanel");
    const lessonQueue = document.getElementById("obPracticeLessonReviewQueuePanel");
    const detailDrawer = document.getElementById("obPracticeSessionDetailDrawerPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else if (lessonQueue && lessonQueue.parentNode) lessonQueue.insertAdjacentElement("afterend", panel);
    else if (detailDrawer && detailDrawer.parentNode) detailDrawer.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = metricsState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-026-practice-repetition-metrics-board", "ready");
    document.body.setAttribute("data-ob-practice-repetition-metrics-preview-only", "true");
    document.body.setAttribute("data-ob-dry-run-only", "true");
    document.body.setAttribute("data-ob-no-database-write", "true");
    document.body.setAttribute("data-ob-no-file-write", "true");
    document.body.setAttribute("data-ob-no-save-endpoint", "true");
    document.body.setAttribute("data-ob-no-real-record-creation", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_026_PRACTICE_REPETITION_METRICS_BOARD_STATE = {
      version: VERSION,
      status: metricsState.status,
      fallbackActive: metricsState.fallbackActive,
      totalPracticeRuns: payload.repetition_summary.total_practice_runs,
      completedRuns: payload.repetition_summary.completed_runs,
      repeatRecommendedCount: payload.repetition_summary.repeat_recommended_count,
      practiceRepetitionMetricsBoardOnly: true,
      dryRunOnly: true,
      metricsPreviewOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchMetrics();
    }, 6300);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_PRACTICE_REPETITION_METRICS_BOARD_GP026_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return metricsState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchMetrics,
    renderPanel,
    setFlags
  };
})();
