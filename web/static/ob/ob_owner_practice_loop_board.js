// OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_JS

(function () {
  const VERSION = "OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD";
  const ENDPOINT = "/ob/owner-practice-loop-board.json";

  // SMOKE MARKERS
  // Owner Practice Loop Board
  // repeatable owner practice loop
  // start practice session
  // resume practice session
  // complete practice session
  // dry-run save preview
  // practice streak placeholder
  // practice repetition counter
  // next practice action
  // lesson review queue
  // rehearsal session lifecycle
  // practice session status
  // active practice session
  // completed practice session
  // incomplete practice session
  // blocked practice session
  // owner-only practice board
  // Review Center practice handoff
  // no database write
  // no file write
  // no save endpoint
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let boardState = {
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
      source: "ob_giant_pack_022_safe_fallback",
      board_state: {
        board_id: "ob_owner_practice_loop_board_001",
        label: "Owner Practice Loop Board",
        status: "practice_loop_board_ready",
        section: "OB — Rehearsal Persistence Adapter + Owner Practice Loop Layer",
        purpose: "Let owner repeat safe Manual Live rehearsal loops using dry-run persistence previews.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        dry_run_adapter_source: "/ob/rehearsal-persistence-adapter-dry-run.json",
        review_center_target: "/ob/review-center-rehearsal-command-board.json"
      },
      practice_status_labels: [
        {
          status_id: "not_started",
          label: "Not started",
          purpose: "Practice loop has not started.",
          next_action: "Start a fake/demo candidate practice session.",
          status: "ready"
        },
        {
          status_id: "active",
          label: "Active",
          purpose: "Practice session is currently in progress.",
          next_action: "Continue from the current rehearsal step.",
          status: "ready"
        },
        {
          status_id: "incomplete",
          label: "Incomplete",
          purpose: "Practice session stopped before final review.",
          next_action: "Resume or mark as abandoned with lesson note.",
          status: "ready"
        },
        {
          status_id: "needs_lesson_review",
          label: "Needs lesson review",
          purpose: "Final action exists, but lesson review is not complete.",
          next_action: "Complete lesson review.",
          status: "ready"
        },
        {
          status_id: "complete",
          label: "Complete",
          purpose: "Practice session completed all required steps.",
          next_action: "Review dry-run save preview and repeat.",
          status: "ready"
        },
        {
          status_id: "blocked",
          label: "Blocked",
          purpose: "Practice session cannot proceed due to missing fields, stale data, or safety block.",
          next_action: "Resolve blocker before continuing.",
          status: "locked"
        }
      ],
      practice_loop_steps: [
        {
          step_id: "start_practice_session",
          label: "Start practice session",
          purpose: "Owner starts a fake/demo or read-only adapted candidate practice loop.",
          required_inputs: ["session_id_preview", "candidate_source", "mission_account", "practice_mode"],
          status: "ready"
        },
        {
          step_id: "review_candidate_context",
          label: "Review candidate context",
          purpose: "Owner reviews symbol, strategy, score, confidence, freshness, and mission-account fit.",
          required_inputs: ["candidate_id", "strategy", "source_confidence", "freshness_label"],
          status: "ready"
        },
        {
          step_id: "run_capital_and_tower_gates",
          label: "Run capital and Tower gates",
          purpose: "Owner sees capital rule blocks and Tower step-up placeholders before decision.",
          required_inputs: ["mission_account", "capital_rule_state", "tower_step_up_state"],
          status: "ready"
        },
        {
          step_id: "complete_manual_decision",
          label: "Complete manual decision",
          purpose: "Owner chooses approve/reject/watch in rehearsal only.",
          required_inputs: ["decision", "decision_reason", "owner_action"],
          status: "ready"
        },
        {
          step_id: "complete_checklist_and_fill_path",
          label: "Complete checklist and fill path",
          purpose: "Owner rehearses broker checklist and fake fill/not-placed state.",
          required_inputs: ["checklist_state", "fill_or_not_placed_choice"],
          status: "ready"
        },
        {
          step_id: "complete_monitor_close_review",
          label: "Complete monitor, close, review",
          purpose: "Owner rehearses monitoring, close capture, and final review.",
          required_inputs: ["monitor_state", "close_state", "lesson_record"],
          status: "ready"
        },
        {
          step_id: "preview_dry_run_save",
          label: "Preview dry-run save",
          purpose: "GP021 adapter shapes what would be saved later without writing.",
          required_inputs: ["dry_run_payload_preview", "blocked_write_reason"],
          status: "ready"
        },
        {
          step_id: "repeat_practice_loop",
          label: "Repeat practice loop",
          purpose: "Owner can run another practice session after reviewing lesson.",
          required_inputs: ["next_practice_action"],
          status: "ready"
        }
      ],
      practice_sessions: [
        {
          session_id: "practice_loop_demo_001",
          label: "MU option-style full practice loop",
          candidate_source: "fake_demo_candidate",
          mission_account: "Proof/Demo OB Account",
          status: "active",
          current_step: "complete_checklist_and_fill_path",
          completion_percent: 62,
          dry_run_save_preview: "pending",
          lesson_review_state: "not_ready",
          next_practice_action: "Complete fake checklist and fill/not-placed path.",
          blockers: [],
          status_label: "active"
        },
        {
          session_id: "practice_loop_demo_002",
          label: "AMD stock fallback completed practice loop",
          candidate_source: "read_only_candidate_adapter",
          mission_account: "Proof/Demo OB Account",
          status: "complete",
          current_step: "repeat_practice_loop",
          completion_percent: 100,
          dry_run_save_preview: "ready",
          lesson_review_state: "complete",
          next_practice_action: "Repeat with option-style candidate or review lesson record.",
          blockers: [],
          status_label: "complete"
        },
        {
          session_id: "practice_loop_demo_003",
          label: "Apartment reserve block practice loop",
          candidate_source: "fake_demo_candidate",
          mission_account: "SimpleeProperty / Apartment OB Account",
          status: "blocked",
          current_step: "run_capital_and_tower_gates",
          completion_percent: 34,
          dry_run_save_preview: "blocked",
          lesson_review_state: "not_started",
          next_practice_action: "Use Proof/Demo account or acknowledge apartment reserve block.",
          blockers: ["apartment_reserve_boundary_at_risk", "tower_step_up_required_later"],
          status_label: "blocked"
        }
      ],
      dry_run_save_preview_contract: {
        preview_id: "owner_practice_dry_run_save_preview_001",
        label: "Dry-run save preview",
        purpose: "Shows what future persistence would save at the end of a practice loop.",
        required_fields: [
          "practice_session_id",
          "rehearsal_session_id",
          "candidate_id",
          "mission_account",
          "current_step",
          "completion_percent",
          "lesson_review_state",
          "dry_run_payload_preview",
          "write_blocked_reason",
          "review_center_target",
          "vault_ready",
          "no_direct_vault_upload",
          "created_at_preview"
        ],
        status: "ready"
      },
      practice_metrics: {
        total_practice_sessions: 3,
        active_practice_sessions: 1,
        completed_practice_sessions: 1,
        incomplete_practice_sessions: 1,
        blocked_practice_sessions: 1,
        average_completion_percent: 65,
        practice_streak_placeholder: "not_enabled",
        repetition_counter_placeholder: "not_enabled"
      },
      lesson_review_queue: [
        {
          lesson_id: "lesson_review_demo_001",
          linked_session: "practice_loop_demo_001",
          label: "Checklist/fill lesson pending",
          purpose: "Owner must record what was confusing or clean about checklist/fill path.",
          status: "pending"
        },
        {
          lesson_id: "lesson_review_demo_002",
          linked_session: "practice_loop_demo_002",
          label: "Completed fallback lesson",
          purpose: "Owner completed lesson review after stock fallback practice.",
          status: "complete"
        },
        {
          lesson_id: "lesson_review_demo_003",
          linked_session: "practice_loop_demo_003",
          label: "Capital block lesson",
          purpose: "Owner records why apartment reserves stay protected.",
          status: "blocked"
        }
      ],
      blocked_actions: [
        "write_practice_session_database_now",
        "write_practice_session_file_now",
        "create_practice_save_endpoint_now",
        "persist_dry_run_preview_now",
        "create_real_session_record_now",
        "read_broker_account",
        "submit_order_from_practice_loop",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_practice_loop_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_loop_only: true,
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
      board_state: { ...(fallback.board_state || {}), ...(safe.board_state || {}) },
      practice_status_labels: Array.isArray(safe.practice_status_labels) ? safe.practice_status_labels : fallback.practice_status_labels,
      practice_loop_steps: Array.isArray(safe.practice_loop_steps) ? safe.practice_loop_steps : fallback.practice_loop_steps,
      practice_sessions: Array.isArray(safe.practice_sessions) ? safe.practice_sessions : fallback.practice_sessions,
      dry_run_save_preview_contract: { ...(fallback.dry_run_save_preview_contract || {}), ...(safe.dry_run_save_preview_contract || {}) },
      practice_metrics: { ...(fallback.practice_metrics || {}), ...(safe.practice_metrics || {}) },
      lesson_review_queue: Array.isArray(safe.lesson_review_queue) ? safe.lesson_review_queue : fallback.lesson_review_queue,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_loop_only: true,
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
    window.OB_OWNER_PRACTICE_LOOP_BOARD_GP022 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_practice_loop_board_gp022: normalized,
      ownerPracticeLoopOnly: true,
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
    window.dispatchEvent(new CustomEvent("obOwnerPracticeLoopBoardUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchBoard() {
    boardState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      boardState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        boardState.status = "ready";
        boardState.source = normalized.source || "server";
        boardState.payload = normalized;
        boardState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        boardState.status = "guarded_fallback";
        boardState.source = "guarded_fallback";
        boardState.payload = fallback;
        boardState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      boardState.status = "error_fallback";
      boardState.source = "error_fallback";
      boardState.payload = fallback;
      boardState.fallbackActive = true;
      boardState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return boardState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("failed") || text.includes("stale")) return "red";
    if (text.includes("ready") || text.includes("complete") || text.includes("active")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-practice-loop-board-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-practice-loop-board-row">
        <div class="ob-owner-practice-loop-board-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.status_id || item.step_id || item.session_id || item.lesson_id, "Item")}</strong>
          <span>${safeText(item.status || item.current_step || item.status_label || "practice", "practice")}</span>
        </div>
        <span>${safeText(item.purpose || item.next_action || item.next_practice_action || "detail", "detail")}</span>
        <div class="ob-owner-practice-loop-board-status ${tone(item.status || item.status_label)}">${safeText(item.status || item.status_label || "ready", "ready")}</div>
      </div>
    `;
  }

  function sessionRow(item) {
    const blockers = Array.isArray(item.blockers) && item.blockers.length ? item.blockers.join(" · ") : "none";
    return `
      <div class="ob-owner-practice-loop-board-row">
        <div class="ob-owner-practice-loop-board-dot">S</div>
        <div>
          <strong>${safeText(item.label, "Practice session")}</strong>
          <span>${safeText(item.session_id, "session")}</span>
        </div>
        <span>
          Candidate source: ${safeText(item.candidate_source, "source")}<br>
          Account: ${safeText(item.mission_account, "account")}<br>
          Current step: ${safeText(item.current_step, "step")}<br>
          Completion: ${safeText(item.completion_percent, "0")}%<br>
          Dry-run save preview: ${safeText(item.dry_run_save_preview, "pending")}<br>
          Blockers: ${blockers}<br>
          Next: ${safeText(item.next_practice_action, "continue")}
        </span>
        <div class="ob-owner-practice-loop-board-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function fieldRows(fields) {
    return (fields || []).map((field) => `
      <div class="ob-owner-practice-loop-board-row">
        <div class="ob-owner-practice-loop-board-dot">F</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>preview field</span>
        </div>
        <span>Required in dry-run save preview contract.</span>
        <div class="ob-owner-practice-loop-board-status gold">required</div>
      </div>
    `).join("");
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-practice-loop-board-row">
        <div class="ob-owner-practice-loop-board-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP022 owner practice loop boundaries.</span>
        <div class="ob-owner-practice-loop-board-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = boardState.payload || buildFallbackPayload();
    const state = payload.board_state || {};
    const labels = Array.isArray(payload.practice_status_labels) ? payload.practice_status_labels : [];
    const steps = Array.isArray(payload.practice_loop_steps) ? payload.practice_loop_steps : [];
    const sessions = Array.isArray(payload.practice_sessions) ? payload.practice_sessions : [];
    const preview = payload.dry_run_save_preview_contract || {};
    const metrics = payload.practice_metrics || {};
    const lessons = Array.isArray(payload.lesson_review_queue) ? payload.lesson_review_queue : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-practice-loop-board-panel" id="obOwnerPracticeLoopBoardPanel" data-ob-giant-pack-022="true">
        <div class="ob-owner-practice-loop-board-head">
          <div>
            <div class="ob-label">OB Giant Pack 022 · Owner Practice Loop</div>
            <div class="ob-owner-practice-loop-board-title">Owner Practice Loop Board</div>
            <div class="ob-owner-practice-loop-board-subtitle">
              ${safeText(boardState.status, "booting")} · ${safeText(state.status, "practice_loop_board_ready")} · repeat safe rehearsal without writing.
            </div>
          </div>
          <div class="ob-owner-practice-loop-board-chip-row">
            <span class="ob-owner-practice-loop-board-chip green">Practice loop</span>
            <span class="ob-owner-practice-loop-board-chip gold">Dry-run preview</span>
            <span class="ob-owner-practice-loop-board-chip red">No DB write</span>
            <span class="ob-owner-practice-loop-board-chip red">No broker/order</span>
          </div>
        </div>

        <div class="ob-owner-practice-loop-board-stat-grid">
          ${card("Total", safeText(metrics.total_practice_sessions, "0"))}
          ${card("Active", safeText(metrics.active_practice_sessions, "0"))}
          ${card("Complete", safeText(metrics.completed_practice_sessions, "0"))}
          ${card("Blocked", safeText(metrics.blocked_practice_sessions, "0"))}
          ${card("Avg", safeText(metrics.average_completion_percent, "0") + "%")}
        </div>

        <div class="ob-owner-practice-loop-board-grid">
          <div>
            <div class="ob-owner-practice-loop-board-card">
              <span>Purpose</span>
              <strong>Make owner rehearsal repeatable: start, resume, complete, preview dry-run save, review lessons, and repeat.</strong>
              <div class="ob-owner-practice-loop-board-callout">
                <strong>Practice loop means:</strong><br>
                Safe owner-only rehearsal cycle with fake/demo or read-only adapted candidates.
              </div>
              <div class="ob-owner-practice-loop-board-boundary">
                <strong>Boundary:</strong><br>
                No database write. No save endpoint. No broker/bank action. No real capital movement. No direct Vault upload.
              </div>
            </div>

            <div class="ob-owner-practice-loop-board-card" style="margin-top: 11px;">
              <span>Dry-run save preview contract</span>
              <strong>${safeText(preview.label, "Dry-run save preview")}</strong>
              <div class="ob-owner-practice-loop-board-list">${fieldRows(preview.required_fields || [])}</div>
            </div>
          </div>

          <div>
            <div class="ob-owner-practice-loop-board-section">
              <div class="ob-owner-practice-loop-board-section-title">Practice status labels</div>
              <div class="ob-owner-practice-loop-board-list">${labels.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-board-section">
              <div class="ob-owner-practice-loop-board-section-title">Practice loop steps</div>
              <div class="ob-owner-practice-loop-board-list">${steps.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-board-section">
              <div class="ob-owner-practice-loop-board-section-title">Practice sessions</div>
              <div class="ob-owner-practice-loop-board-list">${sessions.map(sessionRow).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-board-section">
              <div class="ob-owner-practice-loop-board-section-title">Lesson review queue</div>
              <div class="ob-owner-practice-loop-board-list">${lessons.map((item, index) => row(item, index, "Q")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-board-section">
              <div class="ob-owner-practice-loop-board-section-title">Blocked actions</div>
              <div class="ob-owner-practice-loop-board-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-practice-loop-board-callout">
          <strong>Next handoff:</strong><br>
          GP023 can add Practice Session Detail Drawer so each loop can be inspected step-by-step.
        </div>

        <div class="ob-owner-practice-loop-board-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerPracticeLoopBoardPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const dryRunPanel = document.getElementById("obRehearsalPersistenceAdapterDryRunPanel");
    const preLiveLockPanel = document.getElementById("obManualLivePreLiveLockWallPanel");
    const qualityPanel = document.getElementById("obRehearsalQualityFreshnessGatePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (dryRunPanel && dryRunPanel.parentNode) dryRunPanel.insertAdjacentElement("afterend", panel);
    else if (preLiveLockPanel && preLiveLockPanel.parentNode) preLiveLockPanel.insertAdjacentElement("afterend", panel);
    else if (qualityPanel && qualityPanel.parentNode) qualityPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = boardState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-022-owner-practice-loop-board", "ready");
    document.body.setAttribute("data-ob-owner-practice-loop-only", "true");
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

    window.OB_GIANT_PACK_022_OWNER_PRACTICE_LOOP_BOARD_STATE = {
      version: VERSION,
      status: boardState.status,
      fallbackActive: boardState.fallbackActive,
      practiceSessionCount: payload.practice_sessions.length,
      practiceStepCount: payload.practice_loop_steps.length,
      lessonQueueCount: payload.lesson_review_queue.length,
      ownerPracticeLoopOnly: true,
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
      fetchBoard();
    }, 5660);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_PRACTICE_LOOP_BOARD_GP022_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return boardState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchBoard,
    renderPanel,
    setFlags
  };
})();
