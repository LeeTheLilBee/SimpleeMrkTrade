// OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_JS

(function () {
  const VERSION = "OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD";
  const ENDPOINT = "/ob/review-center-rehearsal-command-board.json";

  // SMOKE MARKERS
  // Review Center Rehearsal Command Board
  // active rehearsal session
  // completed rehearsal sessions
  // incomplete rehearsal sessions
  // where rehearsal stopped
  // missing rehearsal steps
  // rule violations
  // lesson records
  // performance receipt previews
  // owner readiness label
  // next rehearsal action
  // not started status
  // in progress status
  // needs final review status
  // complete status
  // blocked status
  // owner ready status
  // Review Center rollup
  // rehearsal command board
  // record contract handoff
  // no database write
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no public proof
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
      source: "ob_giant_pack_013_safe_fallback",
      board_state: {
        board_id: "ob_review_center_rehearsal_command_board_001",
        label: "Review Center Rehearsal Command Board",
        status: "command_board_ready",
        destination_room: "Review Center",
        owner_only: true,
        contract_source: "/ob/rehearsal-record-contracts.json",
        rehearsal_engine_source: "/ob/owner-rehearsal-engine.json",
        no_database_write: true,
        no_broker_data: true
      },
      status_labels: [
        { status_id: "not_started", label: "Not started", meaning: "No rehearsal session has begun.", owner_next_action: "Start fake candidate rehearsal.", tone: "gold" },
        { status_id: "in_progress", label: "In progress", meaning: "Rehearsal session started but not completed.", owner_next_action: "Resume at current step.", tone: "gold" },
        { status_id: "needs_final_review", label: "Needs final review", meaning: "Flow reached close/review but final lesson/performance receipt is incomplete.", owner_next_action: "Complete final review.", tone: "gold" },
        { status_id: "complete", label: "Complete", meaning: "All required rehearsal records are represented.", owner_next_action: "Review lessons or run another rehearsal.", tone: "green" },
        { status_id: "blocked", label: "Blocked", meaning: "A required rehearsal step is missing or boundary is violated.", owner_next_action: "Resolve missing step/blocker.", tone: "red" },
        { status_id: "owner_ready", label: "Owner ready", meaning: "Rehearsal flow and review are complete enough for owner readiness review.", owner_next_action: "Move to next readiness pack.", tone: "green" }
      ],
      rehearsal_sessions: [
        {
          session_id: "ob_rehearsal_session_demo_001",
          title: "MU option-style full rehearsal",
          candidate_id: "demo_mu_call_rehearsal_001",
          mission_account: "Proof/Demo OB Account",
          status: "in_progress",
          current_step: "capture_fake_fill_or_not_placed",
          stopped_at: "fake fill capture",
          completion_percent: 58,
          missing_steps: ["monitor_fake_position", "capture_fake_close", "complete_final_review", "readiness_confirmed"],
          rule_violations: [],
          lesson_records: [],
          performance_receipt_preview: "pending",
          owner_readiness_label: "not_ready_until_final_review",
          next_rehearsal_action: "Capture fake fill or not-placed result, then continue to monitor placeholder."
        },
        {
          session_id: "ob_rehearsal_session_demo_002",
          title: "AMD stock fallback completed rehearsal",
          candidate_id: "demo_amd_stock_rehearsal_002",
          mission_account: "Proof/Demo OB Account",
          status: "complete",
          current_step: "readiness_confirmed",
          stopped_at: "complete",
          completion_percent: 100,
          missing_steps: [],
          rule_violations: [],
          lesson_records: ["entered only after checklist", "close reason captured", "final review completed"],
          performance_receipt_preview: "owner_manual_live_l1_rehearsal_receipt_preview",
          owner_readiness_label: "owner_ready",
          next_rehearsal_action: "Review lesson and run one more option-style rehearsal."
        },
        {
          session_id: "ob_rehearsal_session_demo_003",
          title: "Bad spread rejection rehearsal",
          candidate_id: "demo_reject_bad_spread_003",
          mission_account: "Proof/Demo OB Account",
          status: "needs_final_review",
          current_step: "complete_final_review",
          stopped_at: "rule review",
          completion_percent: 84,
          missing_steps: ["complete_final_review"],
          rule_violations: ["spread_liquidity_failed_demo"],
          lesson_records: ["reject instead of forcing entry"],
          performance_receipt_preview: "pending_final_review",
          owner_readiness_label: "needs_final_review",
          next_rehearsal_action: "Complete final review and record lesson."
        }
      ],
      board_sections: [
        {
          section_id: "active_rehearsal_session",
          label: "Active rehearsal session",
          purpose: "Show the owner where the current rehearsal is and what to do next.",
          source_records: ["rehearsal_session_record", "rehearsal_candidate_record"],
          status: "ready"
        },
        {
          section_id: "completed_rehearsal_sessions",
          label: "Completed rehearsal sessions",
          purpose: "Show completed rehearsal sessions with lessons and receipt previews.",
          source_records: ["rehearsal_final_review_record", "rehearsal_receipt_record"],
          status: "ready"
        },
        {
          section_id: "incomplete_rehearsal_sessions",
          label: "Incomplete rehearsal sessions",
          purpose: "Show where rehearsal stopped and what is missing.",
          source_records: ["rehearsal_session_record", "rehearsal_monitor_record", "rehearsal_close_record"],
          status: "ready"
        },
        {
          section_id: "rule_violations",
          label: "Rule violations",
          purpose: "Surface demo rule violations from review or rejected sessions.",
          source_records: ["rehearsal_final_review_record"],
          status: "ready"
        },
        {
          section_id: "lesson_records",
          label: "Lesson records",
          purpose: "Surface what worked, what failed, what to repeat, and what to avoid.",
          source_records: ["rehearsal_final_review_record"],
          status: "ready"
        },
        {
          section_id: "performance_receipts",
          label: "Performance receipt previews",
          purpose: "Show Vault-ready rehearsal receipt previews without uploading to Vault.",
          source_records: ["rehearsal_receipt_record"],
          status: "ready"
        },
        {
          section_id: "owner_readiness",
          label: "Owner readiness label",
          purpose: "Show whether owner is not started, in progress, needs review, complete, blocked, or owner-ready.",
          source_records: ["rehearsal_session_record", "rehearsal_receipt_record"],
          status: "ready"
        }
      ],
      board_metrics: {
        total_sessions: 3,
        active_sessions: 1,
        completed_sessions: 1,
        incomplete_sessions: 2,
        blocked_sessions: 0,
        needs_final_review: 1,
        owner_ready_sessions: 1,
        average_completion_percent: 80
      },
      next_actions: [
        {
          action_id: "resume_active_session",
          label: "Resume active rehearsal",
          priority: "high",
          action: "Continue MU demo rehearsal from fake fill/not-placed capture.",
          linked_session: "ob_rehearsal_session_demo_001",
          status: "ready"
        },
        {
          action_id: "complete_final_review",
          label: "Complete final review",
          priority: "high",
          action: "Finish bad spread rejection final review and lesson record.",
          linked_session: "ob_rehearsal_session_demo_003",
          status: "ready"
        },
        {
          action_id: "review_completed_lesson",
          label: "Review completed lesson",
          priority: "medium",
          action: "Review AMD completed rehearsal receipt and lesson record.",
          linked_session: "ob_rehearsal_session_demo_002",
          status: "ready"
        },
        {
          action_id: "prepare_persistence_pack",
          label: "Prepare persistence pack",
          priority: "later",
          action: "After command board review, prepare owner input persistence prep.",
          linked_session: "all",
          status: "later"
        }
      ],
      blocked_actions: [
        "write_rehearsal_database_now",
        "read_broker_account",
        "store_real_broker_data",
        "submit_order_from_ob",
        "auto_execute",
        "publish_rehearsal",
        "create_public_proof",
        "upload_direct_to_vault",
        "show_rehearsal_records_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        review_center_only: true,
        contract_only_no_database_write: true,
        fake_candidate_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        no_real_market_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
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
      status_labels: Array.isArray(safe.status_labels) ? safe.status_labels : fallback.status_labels,
      rehearsal_sessions: Array.isArray(safe.rehearsal_sessions) ? safe.rehearsal_sessions : fallback.rehearsal_sessions,
      board_sections: Array.isArray(safe.board_sections) ? safe.board_sections : fallback.board_sections,
      board_metrics: { ...(fallback.board_metrics || {}), ...(safe.board_metrics || {}) },
      next_actions: Array.isArray(safe.next_actions) ? safe.next_actions : fallback.next_actions,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        review_center_only: true,
        contract_only_no_database_write: true,
        fake_candidate_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        no_real_market_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        no_direct_vault_upload: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_GP013 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      review_center_rehearsal_command_board_gp013: normalized,
      owner_rehearsal_only: true,
      review_center_only: true,
      contract_only_no_database_write: true,
      fake_candidate_only: true,
      no_broker_api: true,
      no_broker_read: true,
      no_order_submit: true,
      no_auto_execution: true,
      no_direct_vault_upload: true,
      live_auto_locked: true
    };
    window.dispatchEvent(new CustomEvent("obReviewCenterRehearsalCommandBoardUpdated", { detail: normalized }));
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
    if (text.includes("blocked") || text.includes("red") || text.includes("no ")) return "red";
    if (text.includes("complete") || text.includes("ready") || text.includes("green")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-rehearsal-command-board-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-rehearsal-command-board-row">
        <div class="ob-rehearsal-command-board-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.title || item.section_id || item.action_id || item.status_id, "Item")}</strong>
          <span>${safeText(item.status || item.priority || item.status_id || item.session_id || "board", "board")}</span>
        </div>
        <span>${safeText(item.purpose || item.meaning || item.next_rehearsal_action || item.action || "detail", "detail")}</span>
        <div class="ob-rehearsal-command-board-status ${tone(item.status || item.tone || item.priority)}">${safeText(item.status || item.tone || item.priority || "ready", "ready")}</div>
      </div>
    `;
  }

  function sessionRow(item, index) {
    const missing = Array.isArray(item.missing_steps) && item.missing_steps.length ? item.missing_steps.join(" · ") : "none";
    const violations = Array.isArray(item.rule_violations) && item.rule_violations.length ? item.rule_violations.join(" · ") : "none";
    return `
      <div class="ob-rehearsal-command-board-row">
        <div class="ob-rehearsal-command-board-dot">S</div>
        <div>
          <strong>${safeText(item.title, "Session")}</strong>
          <span>${safeText(item.session_id, "session")}</span>
        </div>
        <span>
          Current step: ${safeText(item.current_step, "unknown")}<br>
          Stopped at: ${safeText(item.stopped_at, "unknown")}<br>
          Missing: ${missing}<br>
          Rule violations: ${violations}<br>
          Next: ${safeText(item.next_rehearsal_action, "review")}
        </span>
        <div class="ob-rehearsal-command-board-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-rehearsal-command-board-row">
        <div class="ob-rehearsal-command-board-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP013 Review Center rehearsal boundaries.</span>
        <div class="ob-rehearsal-command-board-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = boardState.payload || buildFallbackPayload();
    const state = payload.board_state || {};
    const labels = Array.isArray(payload.status_labels) ? payload.status_labels : [];
    const sessions = Array.isArray(payload.rehearsal_sessions) ? payload.rehearsal_sessions : [];
    const sections = Array.isArray(payload.board_sections) ? payload.board_sections : [];
    const metrics = payload.board_metrics || {};
    const next = Array.isArray(payload.next_actions) ? payload.next_actions : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-rehearsal-command-board-panel" id="obReviewCenterRehearsalCommandBoardPanel" data-ob-giant-pack-013="true">
        <div class="ob-rehearsal-command-board-head">
          <div>
            <div class="ob-label">OB Giant Pack 013 · Review Center Rehearsal Command Board</div>
            <div class="ob-rehearsal-command-board-title">Rehearsal Command Board</div>
            <div class="ob-rehearsal-command-board-subtitle">
              ${safeText(boardState.status, "booting")} · ${safeText(state.status, "command_board_ready")} · Review Center owner-only rollup.
            </div>
          </div>
          <div class="ob-rehearsal-command-board-chip-row">
            <span class="ob-rehearsal-command-board-chip green">Review Center rollup</span>
            <span class="ob-rehearsal-command-board-chip gold">Owner-only</span>
            <span class="ob-rehearsal-command-board-chip red">No DB write</span>
            <span class="ob-rehearsal-command-board-chip red">No broker data</span>
          </div>
        </div>

        <div class="ob-rehearsal-command-board-stat-grid">
          ${card("Total", safeText(metrics.total_sessions, "0"))}
          ${card("Active", safeText(metrics.active_sessions, "0"))}
          ${card("Complete", safeText(metrics.completed_sessions, "0"))}
          ${card("Needs review", safeText(metrics.needs_final_review, "0"))}
          ${card("Avg complete", safeText(metrics.average_completion_percent, "0") + "%")}
        </div>

        <div class="ob-rehearsal-command-board-grid">
          <div>
            <div class="ob-rehearsal-command-board-card">
              <span>Purpose</span>
              <strong>Show active, incomplete, completed, blocked, lesson, receipt, and next-action rehearsal status in Review Center.</strong>
              <div class="ob-rehearsal-command-board-callout">
                <strong>Board reads from:</strong><br>
                GP011 owner rehearsal engine + GP012 rehearsal record contracts.
              </div>
              <div class="ob-rehearsal-command-board-boundary">
                <strong>Boundary:</strong><br>
                This is a Review Center rollup only. No database write, broker read, order submit, public proof, or Vault upload.
              </div>
            </div>

            <div class="ob-rehearsal-command-board-card" style="margin-top: 11px;">
              <span>Status labels</span>
              <div class="ob-rehearsal-command-board-list">${labels.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-rehearsal-command-board-card" style="margin-top: 11px;">
              <span>Next rehearsal actions</span>
              <div class="ob-rehearsal-command-board-list">${next.map((item, index) => row(item, index, "A")).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-rehearsal-command-board-section">
              <div class="ob-rehearsal-command-board-section-title">Rehearsal sessions</div>
              <div class="ob-rehearsal-command-board-list">${sessions.map(sessionRow).join("")}</div>
            </div>

            <div class="ob-rehearsal-command-board-section">
              <div class="ob-rehearsal-command-board-section-title">Board sections</div>
              <div class="ob-rehearsal-command-board-list">${sections.map((item, index) => row(item, index, "B")).join("")}</div>
            </div>

            <div class="ob-rehearsal-command-board-section">
              <div class="ob-rehearsal-command-board-section-title">Blocked actions</div>
              <div class="ob-rehearsal-command-board-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-rehearsal-command-board-callout">
          <strong>Review Center handoff:</strong><br>
          GP013 makes rehearsal progress readable before persistence wiring. GP014 can add owner input persistence prep next.
        </div>

        <div class="ob-rehearsal-command-board-boundary">
          <strong>Still locked:</strong><br>
          No database write. No real broker data. No broker API. No order submit. No public proof. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obReviewCenterRehearsalCommandBoardPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const contractsPanel = document.getElementById("obRehearsalRecordContractsPanel");
    const rehearsalPanel = document.getElementById("obOwnerRehearsalEnginePanel");
    const reviewCenterAnchor = document.querySelector("[data-ob-room='review-center'], .ob-review-center, #reviewCenter");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (contractsPanel && contractsPanel.parentNode) contractsPanel.insertAdjacentElement("afterend", panel);
    else if (rehearsalPanel && rehearsalPanel.parentNode) rehearsalPanel.insertAdjacentElement("afterend", panel);
    else if (reviewCenterAnchor && reviewCenterAnchor.parentNode) reviewCenterAnchor.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = boardState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-013-review-center-rehearsal-command-board", "ready");
    document.body.setAttribute("data-ob-review-center-rehearsal-rollup", "true");
    document.body.setAttribute("data-ob-owner-rehearsal-only", "true");
    document.body.setAttribute("data-ob-contract-only-no-database-write", "true");
    document.body.setAttribute("data-ob-fake-candidate-only", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_013_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_STATE = {
      version: VERSION,
      status: boardState.status,
      fallbackActive: boardState.fallbackActive,
      sessionCount: payload.rehearsal_sessions.length,
      boardSectionCount: payload.board_sections.length,
      nextActionCount: payload.next_actions.length,
      reviewCenterRehearsalRollup: true,
      ownerRehearsalOnly: true,
      contractOnlyNoDatabaseWrite: true,
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
    }, 4780);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_REVIEW_CENTER_REHEARSAL_COMMAND_BOARD_GP013_API = {
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
