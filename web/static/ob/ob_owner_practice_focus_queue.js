// OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE";
  const ENDPOINT = "/ob/owner-practice-focus-queue.json";

  // SMOKE MARKERS
  // Owner Practice Focus Queue
  // owner practice focus queue
  // ordered practice focus list
  // priority practice queue
  // practice task reason
  // suggested practice account
  // suggested candidate type
  // done criteria
  // next practice task
  // locked review task
  // practice-only task
  // repeat checklist fill path task
  // compare option stock fallback task
  // capital boundary review task
  // owner practice task queue
  // focus queue readiness
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

  let focusState = {
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
      source: "ob_giant_pack_028_safe_fallback",
      queue_state: {
        queue_id: "ob_owner_practice_focus_queue_001",
        label: "Owner Practice Focus Queue",
        status: "owner_practice_focus_queue_ready",
        section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        purpose: "Turn practice metrics and guidance into an ordered next-practice queue without saving records.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        metrics_source: "/ob/practice-repetition-metrics-board.json",
        guidance_source: "/ob/owner-review-polish-guidance.json",
        practice_loop_source: "/ob/owner-practice-loop-board.json"
      },
      focus_queue_summary: {
        total_focus_tasks: 5,
        ready_focus_tasks: 3,
        locked_review_tasks: 2,
        high_priority_tasks: 2,
        first_focus_task: "repeat_checklist_fill_path",
        readiness_label: "focus_queue_ready",
        status: "ready"
      },
      focus_tasks: [
        {
          focus_id: "repeat_checklist_fill_path",
          rank: 1,
          label: "Repeat checklist/fill path",
          priority: "high",
          reason: "Most confusion and missed-step flags are tied to checklist and fake fill/not-placed decisions.",
          suggested_account: "Proof/Demo OB Account",
          suggested_candidate_type: "option_style_fake_candidate",
          done_criteria: [
            "Owner completes checklist without missing fields",
            "Owner chooses fake fill or not-placed outcome",
            "Owner writes one clear lesson note",
            "Dry-run save preview can explain why write is still blocked"
          ],
          owner_copy: "Start here. This is the practice rep that makes the next live-manual layer safer later.",
          status: "ready"
        },
        {
          focus_id: "compare_option_vs_stock_fallback",
          rank: 2,
          label: "Compare option-style candidate vs stock fallback",
          priority: "medium",
          reason: "Stock fallback path is clean; option-style path still needs confidence.",
          suggested_account: "Proof/Demo OB Account",
          suggested_candidate_type: "option_style_fake_candidate",
          done_criteria: [
            "Owner names the difference between option-style and stock fallback paths",
            "Owner identifies which path felt cleaner",
            "Owner records one confidence lesson"
          ],
          owner_copy: "Use the cleaner fallback path as a contrast, not as a shortcut.",
          status: "ready"
        },
        {
          focus_id: "practice_dry_run_save_explanation",
          rank: 3,
          label: "Practice dry-run save explanation",
          priority: "medium",
          reason: "Owner should be able to explain why the dry-run save preview is not a real save.",
          suggested_account: "Proof/Demo OB Account",
          suggested_candidate_type: "completed_practice_session",
          done_criteria: [
            "Owner can explain no database write",
            "Owner can explain no save endpoint",
            "Owner can explain no direct Vault upload",
            "Owner can explain why real Manual Live stays locked"
          ],
          owner_copy: "This protects the boundary between practice records and real persistence.",
          status: "ready"
        },
        {
          focus_id: "capital_boundary_review",
          rank: 4,
          label: "Capital boundary review",
          priority: "high",
          reason: "Apartment/trust/protected reserves must stay protected even when a practice path is tempting.",
          suggested_account: "SimpleeProperty / Apartment OB Account",
          suggested_candidate_type: "capital_block_rehearsal",
          done_criteria: [
            "Owner confirms apartment reserve block",
            "Owner redirects trade practice to Proof/Demo",
            "Owner records why protected accounts are not casual trading capital"
          ],
          owner_copy: "This is a locked review task. It teaches the boundary; it does not unlock the account.",
          status: "locked_review"
        },
        {
          focus_id: "live_lock_respect_review",
          rank: 5,
          label: "Live lock respect review",
          priority: "high",
          reason: "Practice readiness must not be confused with real Manual Live readiness.",
          suggested_account: "None",
          suggested_candidate_type: "lock_wall_review",
          done_criteria: [
            "Owner confirms Real Manual Live locked",
            "Owner confirms Hybrid locked",
            "Owner confirms Automated locked",
            "Owner confirms broker/bank/database/Vault actions blocked"
          ],
          owner_copy: "The lock wall is part of the system, not an obstacle to skip.",
          status: "locked_review"
        }
      ],
      focus_sources: [
        {
          source_id: "metrics_board",
          label: "Practice Repetition Metrics Board",
          route: "/ob/practice-repetition-metrics-board.json",
          contribution: "Supplies repetition, blocker, confusion, clean moment, unsafe moment, account, and candidate distribution signals.",
          status: "ready"
        },
        {
          source_id: "owner_review_polish_guidance",
          label: "Owner Review Polish Guidance",
          route: "/ob/owner-review-polish-guidance.json",
          contribution: "Supplies owner-readable language and practice-only reminders.",
          status: "ready"
        },
        {
          source_id: "lesson_review_queue",
          label: "Practice Lesson Review Queue",
          route: "/ob/practice-lesson-review-queue.json",
          contribution: "Supplies lesson category and repeat recommendation signals.",
          status: "ready"
        },
        {
          source_id: "pre_live_lock_wall",
          label: "Manual Live Pre-Live Lock Wall",
          route: "/ob/manual-live-pre-live-lock-wall.json",
          contribution: "Supplies the lock wall that keeps practice separate from real Manual Live.",
          status: "locked"
        }
      ],
      focus_order_rules: [
        {
          rule_id: "rank_high_confusion_first",
          label: "Rank high confusion first",
          purpose: "Practice tasks with confusion and missed-step flags rank first.",
          applies_to: "repeat_checklist_fill_path",
          status: "ready"
        },
        {
          rule_id: "rank_boundary_locks_as_review",
          label: "Rank boundary locks as review",
          purpose: "Protected account and live-lock tasks stay visible but locked.",
          applies_to: "capital_boundary_review",
          status: "locked"
        },
        {
          rule_id: "rank_clean_path_comparison_second",
          label: "Rank clean path comparison second",
          purpose: "Clean fallback path becomes a comparison tool after the primary confusion path.",
          applies_to: "compare_option_vs_stock_fallback",
          status: "ready"
        },
        {
          rule_id: "rank_persistence_explanation_before_save",
          label: "Rank persistence explanation before save",
          purpose: "Owner should understand dry-run save before future persistence work.",
          applies_to: "practice_dry_run_save_explanation",
          status: "ready"
        }
      ],
      focus_completion_contract: {
        contract_id: "owner_practice_focus_completion_contract_001",
        label: "Focus completion contract",
        purpose: "Defines what a future completed focus task would require, without persisting.",
        required_fields: [
          "focus_id",
          "rank",
          "priority",
          "suggested_account",
          "suggested_candidate_type",
          "done_criteria",
          "owner_confirmation_placeholder",
          "lesson_link_placeholder",
          "dry_run_only",
          "write_blocked_reason",
          "created_at_preview"
        ],
        status: "ready"
      },
      blocked_actions: [
        "write_focus_queue_database_now",
        "write_focus_queue_file_now",
        "create_focus_queue_save_endpoint_now",
        "persist_focus_task_completion_now",
        "create_real_focus_task_record_now",
        "claim_real_manual_live_ready",
        "submit_order_from_focus_queue",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_focus_queue_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_focus_queue_only: true,
        dry_run_only: true,
        focus_queue_preview_only: true,
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
      queue_state: { ...(fallback.queue_state || {}), ...(safe.queue_state || {}) },
      focus_queue_summary: { ...(fallback.focus_queue_summary || {}), ...(safe.focus_queue_summary || {}) },
      focus_tasks: Array.isArray(safe.focus_tasks) ? safe.focus_tasks : fallback.focus_tasks,
      focus_sources: Array.isArray(safe.focus_sources) ? safe.focus_sources : fallback.focus_sources,
      focus_order_rules: Array.isArray(safe.focus_order_rules) ? safe.focus_order_rules : fallback.focus_order_rules,
      focus_completion_contract: { ...(fallback.focus_completion_contract || {}), ...(safe.focus_completion_contract || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_focus_queue_only: true,
        dry_run_only: true,
        focus_queue_preview_only: true,
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
    window.OB_OWNER_PRACTICE_FOCUS_QUEUE_GP028 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_practice_focus_queue_gp028: normalized,
      ownerPracticeFocusQueueOnly: true,
      dryRunOnly: true,
      focusQueuePreviewOnly: true,
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
    window.dispatchEvent(new CustomEvent("obOwnerPracticeFocusQueueUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchFocusQueue() {
    focusState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      focusState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        focusState.status = "ready";
        focusState.source = normalized.source || "server";
        focusState.payload = normalized;
        focusState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        focusState.status = "guarded_fallback";
        focusState.source = "guarded_fallback";
        focusState.payload = fallback;
        focusState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      focusState.status = "error_fallback";
      focusState.source = "error_fallback";
      focusState.payload = fallback;
      focusState.fallbackActive = true;
      focusState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return focusState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("high")) return "red";
    if (text.includes("ready") || text.includes("recommended")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-practice-focus-queue-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-practice-focus-queue-row">
        <div class="ob-owner-practice-focus-queue-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.source_id || item.rule_id, "Item")}</strong>
          <span>${safeText(item.status || item.priority || "queue", "queue")}</span>
        </div>
        <span>${safeText(item.purpose || item.contribution || item.reason || item.owner_copy || "detail", "detail")}</span>
        <div class="ob-owner-practice-focus-queue-status ${tone(item.status || item.priority)}">${safeText(item.status || item.priority || "ready", "ready")}</div>
      </div>
    `;
  }

  function focusTaskRow(item) {
    const criteria = Array.isArray(item.done_criteria) ? item.done_criteria.join(" · ") : "none";
    return `
      <div class="ob-owner-practice-focus-queue-row">
        <div class="ob-owner-practice-focus-queue-dot">${safeText(item.rank, "?")}</div>
        <div>
          <strong>${safeText(item.label, "Focus task")}</strong>
          <span>${safeText(item.priority, "priority")} · ${safeText(item.status, "ready")}</span>
        </div>
        <span>
          Reason: ${safeText(item.reason, "reason")}<br>
          Account: ${safeText(item.suggested_account, "account")}<br>
          Candidate type: ${safeText(item.suggested_candidate_type, "candidate")}<br>
          Done: ${criteria}<br>
          ${safeText(item.owner_copy, "copy")}
        </span>
        <div class="ob-owner-practice-focus-queue-status ${tone(item.status || item.priority)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function fieldRows(fields) {
    return (fields || []).map((field) => `
      <div class="ob-owner-practice-focus-queue-row">
        <div class="ob-owner-practice-focus-queue-dot">F</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>contract field</span>
        </div>
        <span>Required in future focus completion record preview.</span>
        <div class="ob-owner-practice-focus-queue-status gold">required</div>
      </div>
    `).join("");
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-practice-focus-queue-row">
        <div class="ob-owner-practice-focus-queue-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP028 owner practice focus queue boundaries.</span>
        <div class="ob-owner-practice-focus-queue-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = focusState.payload || buildFallbackPayload();
    const state = payload.queue_state || {};
    const summary = payload.focus_queue_summary || {};
    const tasks = Array.isArray(payload.focus_tasks) ? payload.focus_tasks : [];
    const sources = Array.isArray(payload.focus_sources) ? payload.focus_sources : [];
    const rules = Array.isArray(payload.focus_order_rules) ? payload.focus_order_rules : [];
    const contract = payload.focus_completion_contract || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-practice-focus-queue-panel" id="obOwnerPracticeFocusQueuePanel" data-ob-giant-pack-028="true">
        <div class="ob-owner-practice-focus-queue-head">
          <div>
            <div class="ob-label">OB Giant Pack 028 · Practice Focus Queue</div>
            <div class="ob-owner-practice-focus-queue-title">Owner Practice Focus Queue</div>
            <div class="ob-owner-practice-focus-queue-subtitle">
              ${safeText(focusState.status, "booting")} · ${safeText(state.status, "owner_practice_focus_queue_ready")} · ordered next-practice work.
            </div>
          </div>
          <div class="ob-owner-practice-focus-queue-chip-row">
            <span class="ob-owner-practice-focus-queue-chip green">Ordered queue</span>
            <span class="ob-owner-practice-focus-queue-chip gold">Done criteria</span>
            <span class="ob-owner-practice-focus-queue-chip red">Practice-only</span>
            <span class="ob-owner-practice-focus-queue-chip red">No save endpoint</span>
          </div>
        </div>

        <div class="ob-owner-practice-focus-queue-stat-grid">
          ${card("Tasks", safeText(summary.total_focus_tasks, "0"))}
          ${card("Ready", safeText(summary.ready_focus_tasks, "0"))}
          ${card("Locked", safeText(summary.locked_review_tasks, "0"))}
          ${card("High", safeText(summary.high_priority_tasks, "0"))}
          ${card("First", safeText(summary.first_focus_task, "none"))}
        </div>

        <div class="ob-owner-practice-focus-queue-grid">
          <div>
            <div class="ob-owner-practice-focus-queue-card">
              <span>Purpose</span>
              <strong>Order the next practice work so the owner knows exactly what to repeat, why, and what “done” means.</strong>
              <div class="ob-owner-practice-focus-queue-callout">
                <strong>First focus:</strong><br>
                Repeat checklist/fill path in Proof/Demo with option-style fake candidate.
              </div>
              <div class="ob-owner-practice-focus-queue-boundary">
                <strong>Boundary:</strong><br>
                Focus queue is preview-only. It does not save tasks, persist completion, read broker/bank data, or enable real Manual Live.
              </div>
            </div>

            <div class="ob-owner-practice-focus-queue-card" style="margin-top: 11px;">
              <span>Focus completion contract</span>
              <strong>${safeText(contract.label, "Focus completion contract")}</strong>
              <div class="ob-owner-practice-focus-queue-list">${fieldRows(contract.required_fields || [])}</div>
            </div>
          </div>

          <div>
            <div class="ob-owner-practice-focus-queue-section">
              <div class="ob-owner-practice-focus-queue-section-title">Ordered practice focus tasks</div>
              <div class="ob-owner-practice-focus-queue-list">${tasks.map(focusTaskRow).join("")}</div>
            </div>

            <div class="ob-owner-practice-focus-queue-section">
              <div class="ob-owner-practice-focus-queue-section-title">Focus sources</div>
              <div class="ob-owner-practice-focus-queue-list">${sources.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-owner-practice-focus-queue-section">
              <div class="ob-owner-practice-focus-queue-section-title">Focus order rules</div>
              <div class="ob-owner-practice-focus-queue-list">${rules.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-owner-practice-focus-queue-section">
              <div class="ob-owner-practice-focus-queue-section-title">Blocked actions</div>
              <div class="ob-owner-practice-focus-queue-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-practice-focus-queue-callout">
          <strong>Next handoff:</strong><br>
          GP029 can add Practice Review Compact Snapshot so the owner sees metrics, guidance, and focus in one compressed view.
        </div>

        <div class="ob-owner-practice-focus-queue-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerPracticeFocusQueuePanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const guidance = document.getElementById("obOwnerReviewPolishGuidancePanel");
    const metrics = document.getElementById("obPracticeRepetitionMetricsBoardPanel");
    const checkpoint = document.getElementById("obOwnerPracticeLoopReadinessCheckpointPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (guidance && guidance.parentNode) guidance.insertAdjacentElement("afterend", panel);
    else if (metrics && metrics.parentNode) metrics.insertAdjacentElement("afterend", panel);
    else if (checkpoint && checkpoint.parentNode) checkpoint.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = focusState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-028-owner-practice-focus-queue", "ready");
    document.body.setAttribute("data-ob-owner-practice-focus-queue-only", "true");
    document.body.setAttribute("data-ob-focus-queue-preview-only", "true");
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

    window.OB_GIANT_PACK_028_OWNER_PRACTICE_FOCUS_QUEUE_STATE = {
      version: VERSION,
      status: focusState.status,
      fallbackActive: focusState.fallbackActive,
      focusTaskCount: payload.focus_tasks.length,
      readyFocusTasks: payload.focus_queue_summary.ready_focus_tasks,
      lockedReviewTasks: payload.focus_queue_summary.locked_review_tasks,
      ownerPracticeFocusQueueOnly: true,
      focusQueuePreviewOnly: true,
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
      fetchFocusQueue();
    }, 6620);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_PRACTICE_FOCUS_QUEUE_GP028_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return focusState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchFocusQueue,
    renderPanel,
    setFlags
  };
})();
