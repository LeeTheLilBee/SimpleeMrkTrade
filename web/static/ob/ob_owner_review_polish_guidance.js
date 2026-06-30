// OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE";
  const ENDPOINT = "/ob/owner-review-polish-guidance.json";

  // SMOKE MARKERS
  // Owner Review Polish Guidance
  // owner review polish guidance
  // calm owner-facing explanations
  // why repeat guidance
  // what improved guidance
  // what still needs practice guidance
  // practice-only reminder
  // not real Manual Live reminder
  // confidence without failure language
  // blocker explanation copy
  // clean moment explanation copy
  // unsafe moment explanation copy
  // next focus explanation copy
  // owner-readable metrics copy
  // review polish copy bank
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

  let guidanceState = {
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
      source: "ob_giant_pack_027_safe_fallback",
      guidance_state: {
        guidance_id: "ob_owner_review_polish_guidance_001",
        label: "Owner Review Polish Guidance",
        status: "owner_review_polish_ready",
        section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        purpose: "Translate practice metrics into calm owner-readable guidance without saving records.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        metrics_source: "/ob/practice-repetition-metrics-board.json",
        lesson_queue_source: "/ob/practice-lesson-review-queue.json",
        readiness_source: "/ob/owner-practice-loop-readiness-checkpoint.json"
      },
      guidance_groups: [
        {
          group_id: "why_repeat_guidance",
          label: "Why repeat guidance",
          purpose: "Explain why repetition is useful without framing it as failure.",
          owner_copy: "Repeat this because the system found a step worth making automatic, not because you failed.",
          tone: "calm_direct",
          status: "ready"
        },
        {
          group_id: "what_improved_guidance",
          label: "What improved guidance",
          purpose: "Show progress in completion, fewer blockers, and cleaner moments.",
          owner_copy: "The practice loop is getting cleaner: completion is up, blockers are down, and clean moments are increasing.",
          tone: "encouraging_grounded",
          status: "ready"
        },
        {
          group_id: "what_needs_practice_guidance",
          label: "What still needs practice guidance",
          purpose: "Name the next weak point without shame.",
          owner_copy: "The checklist/fill path still needs reps. Keep it in Proof/Demo until it feels boring and clean.",
          tone: "firm_calm",
          status: "ready"
        },
        {
          group_id: "practice_only_reminder",
          label: "Practice-only reminder",
          purpose: "Separate owner practice from real Manual Live.",
          owner_copy: "This is practice-only. Real Manual Live is still locked.",
          tone: "boundary_clear",
          status: "locked"
        },
        {
          group_id: "live_lock_reminder",
          label: "Live lock reminder",
          purpose: "Keep Hybrid, Automated, broker, bank, database, and Vault actions blocked.",
          owner_copy: "No broker, bank, database, save endpoint, or direct Vault action is enabled here.",
          tone: "boundary_clear",
          status: "locked"
        }
      ],
      copy_bank: [
        {
          copy_id: "repeat_not_failure",
          label: "Repeat is not failure",
          copy_type: "why_repeat",
          owner_copy: "A repeat recommendation means the step is important enough to drill, not that you did something wrong.",
          use_when: "repeat_recommended_count_above_zero",
          status: "ready"
        },
        {
          copy_id: "checklist_fill_focus",
          label: "Checklist/fill focus",
          copy_type: "next_focus",
          owner_copy: "Your next rep should focus on checklist and fake fill/not-placed decisions.",
          use_when: "checklist_lesson_pending",
          status: "ready"
        },
        {
          copy_id: "capital_boundary_clear",
          label: "Capital boundary clear",
          copy_type: "safety",
          owner_copy: "Apartment and protected reserve accounts stay protected. Use Proof/Demo for trade practice.",
          use_when: "protected_account_blocked",
          status: "locked"
        },
        {
          copy_id: "clean_moment_growth",
          label: "Clean moment growth",
          copy_type: "what_improved",
          owner_copy: "Clean moments are increasing. Keep repeating until the process feels slow, boring, and controlled.",
          use_when: "clean_moment_trend_improving",
          status: "ready"
        },
        {
          copy_id: "unsafe_moment_down",
          label: "Unsafe moment down",
          copy_type: "what_improved",
          owner_copy: "Unsafe moments are dropping. Keep the lock wall visible while you practice.",
          use_when: "unsafe_moment_trend_declining",
          status: "ready"
        },
        {
          copy_id: "practice_only_wall",
          label: "Practice-only wall",
          copy_type: "boundary",
          owner_copy: "This readiness is owner practice readiness, not real Manual Live readiness.",
          use_when: "any_practice_metrics_screen",
          status: "locked"
        }
      ],
      metric_translation_rules: [
        {
          rule_id: "completion_up",
          label: "Completion up",
          metric_signal: "completion_trend_improving",
          plain_language: "You are finishing more practice loops.",
          owner_guidance: "Keep repeating the same structure until completion becomes automatic.",
          status: "ready"
        },
        {
          rule_id: "blockers_down",
          label: "Blockers down",
          metric_signal: "blocker_trend_declining",
          plain_language: "Fewer things are stopping the practice loop.",
          owner_guidance: "Keep the same candidate type and focus on clean execution of steps.",
          status: "ready"
        },
        {
          rule_id: "confusion_watch",
          label: "Confusion watch",
          metric_signal: "confusion_reduction_watch",
          plain_language: "Some confusion is still showing up.",
          owner_guidance: "Do another repetition focused only on the confusing step.",
          status: "watch"
        },
        {
          rule_id: "clean_moments_up",
          label: "Clean moments up",
          metric_signal: "clean_moment_trend_improving",
          plain_language: "More steps are feeling clean and repeatable.",
          owner_guidance: "Do not rush to live; repeat until clean feels normal.",
          status: "ready"
        },
        {
          rule_id: "unsafe_moments_down",
          label: "Unsafe moments down",
          metric_signal: "unsafe_moment_trend_declining",
          plain_language: "Risky moments are reducing.",
          owner_guidance: "Keep practicing with locks visible and capital boundaries protected.",
          status: "ready"
        }
      ],
      owner_review_cards: [
        {
          card_id: "owner_review_now",
          label: "What matters now",
          headline: "Repeat the checklist/fill path.",
          body: "That is where the most useful practice is still showing up.",
          action_label: "Practice again in Proof/Demo",
          status: "ready"
        },
        {
          card_id: "owner_review_improved",
          label: "What improved",
          headline: "Completion is up and blockers are down.",
          body: "The rehearsal flow is getting cleaner without unlocking real live actions.",
          action_label: "Keep the same structure",
          status: "ready"
        },
        {
          card_id: "owner_review_locked",
          label: "What stays locked",
          headline: "Real Manual Live is still locked.",
          body: "No broker, bank, database, save endpoint, or direct Vault action is active.",
          action_label: "Respect the lock wall",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_guidance_database_now",
        "write_guidance_file_now",
        "create_guidance_save_endpoint_now",
        "persist_owner_review_copy_now",
        "create_real_guidance_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_guidance",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_guidance_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_review_polish_guidance_only: true,
        dry_run_only: true,
        guidance_preview_only: true,
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
      guidance_state: { ...(fallback.guidance_state || {}), ...(safe.guidance_state || {}) },
      guidance_groups: Array.isArray(safe.guidance_groups) ? safe.guidance_groups : fallback.guidance_groups,
      copy_bank: Array.isArray(safe.copy_bank) ? safe.copy_bank : fallback.copy_bank,
      metric_translation_rules: Array.isArray(safe.metric_translation_rules) ? safe.metric_translation_rules : fallback.metric_translation_rules,
      owner_review_cards: Array.isArray(safe.owner_review_cards) ? safe.owner_review_cards : fallback.owner_review_cards,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_review_polish_guidance_only: true,
        dry_run_only: true,
        guidance_preview_only: true,
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
    window.OB_OWNER_REVIEW_POLISH_GUIDANCE_GP027 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_review_polish_guidance_gp027: normalized,
      ownerReviewPolishGuidanceOnly: true,
      dryRunOnly: true,
      guidancePreviewOnly: true,
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
    window.dispatchEvent(new CustomEvent("obOwnerReviewPolishGuidanceUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchGuidance() {
    guidanceState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      guidanceState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        guidanceState.status = "ready";
        guidanceState.source = normalized.source || "server";
        guidanceState.payload = normalized;
        guidanceState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        guidanceState.status = "guarded_fallback";
        guidanceState.source = "guarded_fallback";
        guidanceState.payload = fallback;
        guidanceState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      guidanceState.status = "error_fallback";
      guidanceState.source = "error_fallback";
      guidanceState.payload = fallback;
      guidanceState.fallbackActive = true;
      guidanceState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return guidanceState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("boundary")) return "red";
    if (text.includes("ready") || text.includes("encouraging") || text.includes("calm")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-review-polish-guidance-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-review-polish-guidance-row">
        <div class="ob-owner-review-polish-guidance-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.group_id || item.copy_id || item.rule_id || item.card_id, "Item")}</strong>
          <span>${safeText(item.status || item.tone || item.copy_type || "guidance", "guidance")}</span>
        </div>
        <span>${safeText(item.owner_copy || item.plain_language || item.body || item.purpose || "detail", "detail")}</span>
        <div class="ob-owner-review-polish-guidance-status ${tone(item.status || item.tone || item.copy_type)}">${safeText(item.status || item.tone || item.copy_type || "ready", "ready")}</div>
      </div>
    `;
  }

  function reviewCard(item) {
    return `
      <div class="ob-owner-review-polish-guidance-row">
        <div class="ob-owner-review-polish-guidance-dot">R</div>
        <div>
          <strong>${safeText(item.label, "Review card")}</strong>
          <span>${safeText(item.status, "ready")}</span>
        </div>
        <span>
          ${safeText(item.headline, "Headline")}<br>
          ${safeText(item.body, "Body")}<br>
          Action: ${safeText(item.action_label, "Review")}
        </span>
        <div class="ob-owner-review-polish-guidance-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-review-polish-guidance-row">
        <div class="ob-owner-review-polish-guidance-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP027 owner review polish boundaries.</span>
        <div class="ob-owner-review-polish-guidance-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = guidanceState.payload || buildFallbackPayload();
    const state = payload.guidance_state || {};
    const groups = Array.isArray(payload.guidance_groups) ? payload.guidance_groups : [];
    const copyBank = Array.isArray(payload.copy_bank) ? payload.copy_bank : [];
    const rules = Array.isArray(payload.metric_translation_rules) ? payload.metric_translation_rules : [];
    const cards = Array.isArray(payload.owner_review_cards) ? payload.owner_review_cards : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-review-polish-guidance-panel" id="obOwnerReviewPolishGuidancePanel" data-ob-giant-pack-027="true">
        <div class="ob-owner-review-polish-guidance-head">
          <div>
            <div class="ob-label">OB Giant Pack 027 · Owner Review Polish</div>
            <div class="ob-owner-review-polish-guidance-title">Owner Review Polish Guidance</div>
            <div class="ob-owner-review-polish-guidance-subtitle">
              ${safeText(guidanceState.status, "booting")} · ${safeText(state.status, "owner_review_polish_ready")} · calm owner-readable guidance.
            </div>
          </div>
          <div class="ob-owner-review-polish-guidance-chip-row">
            <span class="ob-owner-review-polish-guidance-chip green">Owner-readable</span>
            <span class="ob-owner-review-polish-guidance-chip gold">Why repeat</span>
            <span class="ob-owner-review-polish-guidance-chip red">Practice-only</span>
            <span class="ob-owner-review-polish-guidance-chip red">Live locked</span>
          </div>
        </div>

        <div class="ob-owner-review-polish-guidance-stat-grid">
          ${card("Groups", safeText(groups.length, "0"))}
          ${card("Copy", safeText(copyBank.length, "0"))}
          ${card("Rules", safeText(rules.length, "0"))}
          ${card("Cards", safeText(cards.length, "0"))}
          ${card("Mode", "practice-only")}
        </div>

        <div class="ob-owner-review-polish-guidance-grid">
          <div>
            <div class="ob-owner-review-polish-guidance-card">
              <span>Purpose</span>
              <strong>Turn metrics into calm, direct owner guidance without saving copy or implying real Manual Live readiness.</strong>
              <div class="ob-owner-review-polish-guidance-callout">
                <strong>Owner language:</strong><br>
                Repeat means drill the step until it becomes automatic. It is not a failure signal.
              </div>
              <div class="ob-owner-review-polish-guidance-boundary">
                <strong>Boundary:</strong><br>
                This guidance is preview-only. No database, save endpoint, broker, bank, or direct Vault action is enabled.
              </div>
            </div>

            <div class="ob-owner-review-polish-guidance-card" style="margin-top: 11px;">
              <span>Practice-only reminder</span>
              <strong>This readiness is practice readiness, not real Manual Live readiness.</strong>
              <div class="ob-owner-review-polish-guidance-boundary">
                Real Manual Live, Hybrid, Automated, broker/bank/database/Vault actions remain locked.
              </div>
            </div>
          </div>

          <div>
            <div class="ob-owner-review-polish-guidance-section">
              <div class="ob-owner-review-polish-guidance-section-title">Owner review cards</div>
              <div class="ob-owner-review-polish-guidance-list">${cards.map(reviewCard).join("")}</div>
            </div>

            <div class="ob-owner-review-polish-guidance-section">
              <div class="ob-owner-review-polish-guidance-section-title">Guidance groups</div>
              <div class="ob-owner-review-polish-guidance-list">${groups.map((item, index) => row(item, index, "G")).join("")}</div>
            </div>

            <div class="ob-owner-review-polish-guidance-section">
              <div class="ob-owner-review-polish-guidance-section-title">Review polish copy bank</div>
              <div class="ob-owner-review-polish-guidance-list">${copyBank.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-owner-review-polish-guidance-section">
              <div class="ob-owner-review-polish-guidance-section-title">Metric translation rules</div>
              <div class="ob-owner-review-polish-guidance-list">${rules.map((item, index) => row(item, index, "T")).join("")}</div>
            </div>

            <div class="ob-owner-review-polish-guidance-section">
              <div class="ob-owner-review-polish-guidance-section-title">Blocked actions</div>
              <div class="ob-owner-review-polish-guidance-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-review-polish-guidance-callout">
          <strong>Next handoff:</strong><br>
          GP028 can add Owner Practice Focus Queue so recommendations become ordered next-practice tasks.
        </div>

        <div class="ob-owner-review-polish-guidance-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerReviewPolishGuidancePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const metricsBoard = document.getElementById("obPracticeRepetitionMetricsBoardPanel");
    const checkpoint = document.getElementById("obOwnerPracticeLoopReadinessCheckpointPanel");
    const lessonQueue = document.getElementById("obPracticeLessonReviewQueuePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (metricsBoard && metricsBoard.parentNode) metricsBoard.insertAdjacentElement("afterend", panel);
    else if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else if (lessonQueue && lessonQueue.parentNode) lessonQueue.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = guidanceState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-027-owner-review-polish-guidance", "ready");
    document.body.setAttribute("data-ob-owner-review-polish-guidance-only", "true");
    document.body.setAttribute("data-ob-guidance-preview-only", "true");
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

    window.OB_GIANT_PACK_027_OWNER_REVIEW_POLISH_GUIDANCE_STATE = {
      version: VERSION,
      status: guidanceState.status,
      fallbackActive: guidanceState.fallbackActive,
      guidanceGroupCount: payload.guidance_groups.length,
      copyBankCount: payload.copy_bank.length,
      reviewCardCount: payload.owner_review_cards.length,
      ownerReviewPolishGuidanceOnly: true,
      guidancePreviewOnly: true,
      dryRunOnly: true,
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
      fetchGuidance();
    }, 6460);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_REVIEW_POLISH_GUIDANCE_GP027_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return guidanceState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchGuidance,
    renderPanel,
    setFlags
  };
})();
