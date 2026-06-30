// OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_JS

(function () {
  const VERSION = "OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER";
  const ENDPOINT = "/ob/practice-session-detail-drawer.json";

  // SMOKE MARKERS
  // Practice Session Detail Drawer
  // practice session detail drawer
  // selected practice session
  // session step timeline
  // current practice step
  // practice blockers detail
  // dry-run payload preview detail
  // lesson status detail
  // next practice action detail
  // session lifecycle detail
  // owner-only detail drawer
  // Review Center detail handoff
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

  let drawerState = {
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
      source: "ob_giant_pack_023_safe_fallback",
      drawer_state: {
        drawer_id: "ob_practice_session_detail_drawer_001",
        label: "Practice Session Detail Drawer",
        status: "detail_drawer_ready",
        section: "OB — Rehearsal Persistence Adapter + Owner Practice Loop Layer",
        purpose: "Inspect each owner practice loop session step-by-step without saving records.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        practice_loop_source: "/ob/owner-practice-loop-board.json",
        dry_run_adapter_source: "/ob/rehearsal-persistence-adapter-dry-run.json",
        review_center_target: "/ob/review-center-rehearsal-command-board.json"
      },
      selected_session: {
        session_id: "practice_loop_demo_001",
        label: "MU option-style full practice loop",
        candidate_source: "fake_demo_candidate",
        mission_account: "Proof/Demo OB Account",
        status: "active",
        current_step: "complete_checklist_and_fill_path",
        completion_percent: 62,
        dry_run_save_preview: "pending",
        lesson_review_state: "not_ready",
        selected_reason: "Active owner practice session",
        next_practice_action: "Complete fake checklist and fill/not-placed path.",
        owner_visibility: "owner_only"
      },
      session_step_timeline: [
        {"step_id": "start_practice_session", "label": "Start practice session", "result": "complete", "detail": "Demo session started with fake candidate.", "status": "complete"},
        {"step_id": "review_candidate_context", "label": "Review candidate context", "result": "complete", "detail": "Symbol, strategy, score, confidence, and freshness reviewed.", "status": "complete"},
        {"step_id": "run_capital_and_tower_gates", "label": "Run capital and Tower gates", "result": "complete", "detail": "Proof/Demo account passed rehearsal-only capital gate.", "status": "complete"},
        {"step_id": "complete_manual_decision", "label": "Complete manual decision", "result": "complete", "detail": "Owner selected rehearsal decision and reason.", "status": "complete"},
        {"step_id": "complete_checklist_and_fill_path", "label": "Complete checklist and fill path", "result": "active", "detail": "Owner must finish checklist and fake fill/not-placed state.", "status": "active"},
        {"step_id": "complete_monitor_close_review", "label": "Complete monitor, close, review", "result": "not_started", "detail": "Monitor/close/final review not reached yet.", "status": "not_started"},
        {"step_id": "preview_dry_run_save", "label": "Preview dry-run save", "result": "blocked_until_steps_complete", "detail": "Dry-run save preview waits for required steps.", "status": "blocked"},
        {"step_id": "repeat_practice_loop", "label": "Repeat practice loop", "result": "not_ready", "detail": "Repeat is available after lesson review.", "status": "not_started"}
      ],
      blocker_detail: [
        {
          blocker_id: "missing_fake_fill_or_not_placed_choice",
          label: "Missing fake fill / not-placed choice",
          blocking_step: "complete_checklist_and_fill_path",
          severity: "needs_review",
          required_action: "Choose fake fill or not-placed outcome.",
          owner_can_continue_after: "required field completed",
          status: "active"
        },
        {
          blocker_id: "lesson_review_not_ready",
          label: "Lesson review not ready",
          blocking_step: "complete_monitor_close_review",
          severity: "watch",
          required_action: "Complete close/review before lesson record.",
          owner_can_continue_after: "close review completed",
          status: "pending"
        }
      ],
      dry_run_payload_preview_detail: {
        preview_id: "dry_run_preview_detail_demo_001",
        linked_session: "practice_loop_demo_001",
        preview_status: "pending_required_steps",
        would_emit_record_types: [
          "rehearsal_decision_record",
          "rehearsal_preflight_record",
          "rehearsal_checklist_record",
          "rehearsal_fill_or_not_placed_record",
          "rehearsal_close_record",
          "rehearsal_final_review_record",
          "rehearsal_receipt_record"
        ],
        write_blocked_reason: "practice_session_not_complete",
        review_center_target: "/ob/review-center-rehearsal-command-board.json",
        vault_ready: false,
        no_direct_vault_upload: true,
        no_database_write: true,
        no_file_write: true,
        status: "blocked"
      },
      lesson_status_detail: [
        {
          lesson_id: "lesson_detail_demo_001",
          label: "Checklist confidence lesson",
          linked_step: "complete_checklist_and_fill_path",
          lesson_prompt: "What part of the checklist felt unclear, risky, or clean?",
          lesson_status: "pending",
          required_before_complete: true,
          status: "pending"
        },
        {
          lesson_id: "lesson_detail_demo_002",
          label: "Capital rule lesson",
          linked_step: "run_capital_and_tower_gates",
          lesson_prompt: "Why is Proof/Demo allowed while ATM/apartment reserves stay protected?",
          lesson_status: "complete",
          required_before_complete: false,
          status: "complete"
        }
      ],
      drawer_actions: [
        {"action_id": "resume_selected_session", "label": "Resume selected session", "purpose": "Return owner to current practice step.", "enabled_now": false, "reason": "UI action placeholder only.", "status": "placeholder"},
        {"action_id": "preview_dry_run_payload", "label": "Preview dry-run payload", "purpose": "Inspect dry-run payload when required steps are complete.", "enabled_now": false, "reason": "Preview only; no persistence.", "status": "placeholder"},
        {"action_id": "send_to_review_center", "label": "Send to Review Center", "purpose": "Future handoff target only; no write or save.", "enabled_now": false, "reason": "No save endpoint yet.", "status": "placeholder"},
        {"action_id": "mark_lesson_reviewed", "label": "Mark lesson reviewed", "purpose": "Future owner input action placeholder.", "enabled_now": false, "reason": "No database write.", "status": "placeholder"}
      ],
      blocked_actions: [
        "write_session_detail_database_now",
        "write_session_detail_file_now",
        "create_session_detail_save_endpoint_now",
        "persist_drawer_action_now",
        "create_real_session_detail_record_now",
        "read_broker_account",
        "submit_order_from_detail_drawer",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_session_detail_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_session_detail_drawer_only: true,
        dry_run_only: true,
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
      drawer_state: { ...(fallback.drawer_state || {}), ...(safe.drawer_state || {}) },
      selected_session: { ...(fallback.selected_session || {}), ...(safe.selected_session || {}) },
      session_step_timeline: Array.isArray(safe.session_step_timeline) ? safe.session_step_timeline : fallback.session_step_timeline,
      blocker_detail: Array.isArray(safe.blocker_detail) ? safe.blocker_detail : fallback.blocker_detail,
      dry_run_payload_preview_detail: { ...(fallback.dry_run_payload_preview_detail || {}), ...(safe.dry_run_payload_preview_detail || {}) },
      lesson_status_detail: Array.isArray(safe.lesson_status_detail) ? safe.lesson_status_detail : fallback.lesson_status_detail,
      drawer_actions: Array.isArray(safe.drawer_actions) ? safe.drawer_actions : fallback.drawer_actions,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_session_detail_drawer_only: true,
        dry_run_only: true,
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
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_PRACTICE_SESSION_DETAIL_DRAWER_GP023 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      practice_session_detail_drawer_gp023: normalized,
      practiceSessionDetailDrawerOnly: true,
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
    window.dispatchEvent(new CustomEvent("obPracticeSessionDetailDrawerUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchDrawer() {
    drawerState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      drawerState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        drawerState.status = "ready";
        drawerState.source = normalized.source || "server";
        drawerState.payload = normalized;
        drawerState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        drawerState.status = "guarded_fallback";
        drawerState.source = "guarded_fallback";
        drawerState.payload = fallback;
        drawerState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      drawerState.status = "error_fallback";
      drawerState.source = "error_fallback";
      drawerState.payload = fallback;
      drawerState.fallbackActive = true;
      drawerState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return drawerState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("failed") || text.includes("not_started")) return "red";
    if (text.includes("ready") || text.includes("complete") || text.includes("active")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-practice-session-detail-drawer-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-practice-session-detail-drawer-row">
        <div class="ob-practice-session-detail-drawer-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.step_id || item.blocker_id || item.lesson_id || item.action_id, "Item")}</strong>
          <span>${safeText(item.status || item.result || item.severity || "detail", "detail")}</span>
        </div>
        <span>${safeText(item.detail || item.required_action || item.lesson_prompt || item.purpose || item.reason || "detail", "detail")}</span>
        <div class="ob-practice-session-detail-drawer-status ${tone(item.status || item.result || item.severity)}">${safeText(item.status || item.result || item.severity || "ready", "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-practice-session-detail-drawer-row">
        <div class="ob-practice-session-detail-drawer-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP023 detail drawer boundaries.</span>
        <div class="ob-practice-session-detail-drawer-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = drawerState.payload || buildFallbackPayload();
    const state = payload.drawer_state || {};
    const selected = payload.selected_session || {};
    const timeline = Array.isArray(payload.session_step_timeline) ? payload.session_step_timeline : [];
    const blockers = Array.isArray(payload.blocker_detail) ? payload.blocker_detail : [];
    const preview = payload.dry_run_payload_preview_detail || {};
    const lessons = Array.isArray(payload.lesson_status_detail) ? payload.lesson_status_detail : [];
    const actions = Array.isArray(payload.drawer_actions) ? payload.drawer_actions : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-practice-session-detail-drawer-panel" id="obPracticeSessionDetailDrawerPanel" data-ob-giant-pack-023="true">
        <div class="ob-practice-session-detail-drawer-head">
          <div>
            <div class="ob-label">OB Giant Pack 023 · Practice Session Detail</div>
            <div class="ob-practice-session-detail-drawer-title">Practice Session Detail Drawer</div>
            <div class="ob-practice-session-detail-drawer-subtitle">
              ${safeText(drawerState.status, "booting")} · ${safeText(state.status, "detail_drawer_ready")} · inspect one practice loop without saving.
            </div>
          </div>
          <div class="ob-practice-session-detail-drawer-chip-row">
            <span class="ob-practice-session-detail-drawer-chip green">Session detail</span>
            <span class="ob-practice-session-detail-drawer-chip gold">Dry-run preview</span>
            <span class="ob-practice-session-detail-drawer-chip red">No DB write</span>
            <span class="ob-practice-session-detail-drawer-chip red">No broker/order</span>
          </div>
        </div>

        <div class="ob-practice-session-detail-drawer-stat-grid">
          ${card("Selected", safeText(selected.session_id, "none"))}
          ${card("Status", safeText(selected.status, "unknown"))}
          ${card("Step", safeText(selected.current_step, "none"))}
          ${card("Progress", safeText(selected.completion_percent, "0") + "%")}
          ${card("Preview", safeText(preview.preview_status, "pending"))}
        </div>

        <div class="ob-practice-session-detail-drawer-grid">
          <div>
            <div class="ob-practice-session-detail-drawer-card">
              <span>Selected session</span>
              <strong>${safeText(selected.label, "Practice session")}</strong>
              <div class="ob-practice-session-detail-drawer-callout">
                <strong>Next action:</strong><br>
                ${safeText(selected.next_practice_action, "Continue practice.")}
              </div>
              <div class="ob-practice-session-detail-drawer-boundary">
                <strong>Boundary:</strong><br>
                Detail drawer is read-only/dry-run. It does not save, persist, submit, upload, or execute anything.
              </div>
            </div>

            <div class="ob-practice-session-detail-drawer-card" style="margin-top: 11px;">
              <span>Dry-run payload preview detail</span>
              <strong>${safeText(preview.preview_id, "preview")}</strong>
              <div class="ob-practice-session-detail-drawer-callout">
                Status: ${safeText(preview.preview_status, "pending")}<br>
                Write blocked reason: ${safeText(preview.write_blocked_reason, "none")}<br>
                Review target: ${safeText(preview.review_center_target, "Review Center")}<br>
                Vault-ready: ${safeText(preview.vault_ready, "false")} · Direct Vault upload: blocked
              </div>
            </div>
          </div>

          <div>
            <div class="ob-practice-session-detail-drawer-section">
              <div class="ob-practice-session-detail-drawer-section-title">Session step timeline</div>
              <div class="ob-practice-session-detail-drawer-list">${timeline.map((item, index) => row(item, index, "T")).join("")}</div>
            </div>

            <div class="ob-practice-session-detail-drawer-section">
              <div class="ob-practice-session-detail-drawer-section-title">Practice blockers detail</div>
              <div class="ob-practice-session-detail-drawer-list">${blockers.map((item, index) => row(item, index, "B")).join("")}</div>
            </div>

            <div class="ob-practice-session-detail-drawer-section">
              <div class="ob-practice-session-detail-drawer-section-title">Lesson status detail</div>
              <div class="ob-practice-session-detail-drawer-list">${lessons.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-practice-session-detail-drawer-section">
              <div class="ob-practice-session-detail-drawer-section-title">Drawer actions</div>
              <div class="ob-practice-session-detail-drawer-list">${actions.map((item, index) => row(item, index, "A")).join("")}</div>
            </div>

            <div class="ob-practice-session-detail-drawer-section">
              <div class="ob-practice-session-detail-drawer-section-title">Blocked actions</div>
              <div class="ob-practice-session-detail-drawer-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-practice-session-detail-drawer-callout">
          <strong>Next handoff:</strong><br>
          GP024 can add Practice Lesson Review Queue depth so lessons become structured owner learning records.
        </div>

        <div class="ob-practice-session-detail-drawer-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPracticeSessionDetailDrawerPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const practiceBoard = document.getElementById("obOwnerPracticeLoopBoardPanel");
    const dryRunPanel = document.getElementById("obRehearsalPersistenceAdapterDryRunPanel");
    const preLiveLockPanel = document.getElementById("obManualLivePreLiveLockWallPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (practiceBoard && practiceBoard.parentNode) practiceBoard.insertAdjacentElement("afterend", panel);
    else if (dryRunPanel && dryRunPanel.parentNode) dryRunPanel.insertAdjacentElement("afterend", panel);
    else if (preLiveLockPanel && preLiveLockPanel.parentNode) preLiveLockPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = drawerState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-023-practice-session-detail-drawer", "ready");
    document.body.setAttribute("data-ob-practice-session-detail-drawer-only", "true");
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
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_023_PRACTICE_SESSION_DETAIL_DRAWER_STATE = {
      version: VERSION,
      status: drawerState.status,
      fallbackActive: drawerState.fallbackActive,
      timelineCount: payload.session_step_timeline.length,
      blockerCount: payload.blocker_detail.length,
      lessonCount: payload.lesson_status_detail.length,
      practiceSessionDetailDrawerOnly: true,
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
      fetchDrawer();
    }, 5820);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_PRACTICE_SESSION_DETAIL_DRAWER_GP023_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return drawerState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchDrawer,
    renderPanel,
    setFlags
  };
})();
