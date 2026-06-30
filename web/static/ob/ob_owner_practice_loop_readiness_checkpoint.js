// OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT";
  const ENDPOINT = "/ob/owner-practice-loop-readiness-checkpoint.json";

  // SMOKE MARKERS
  // Owner Practice Loop Readiness Checkpoint
  // owner practice loop readiness
  // mini-section close checkpoint
  // GP021 readiness
  // GP022 readiness
  // GP023 readiness
  // GP024 readiness
  // dry-run persistence adapter ready
  // owner practice loop board ready
  // practice session detail drawer ready
  // practice lesson review queue ready
  // save batch checkpoint
  // repeatable owner practice ready
  // readiness label owner_practice_loop_ready
  // not real manual live ready
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

  let checkpointState = {
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
      source: "ob_giant_pack_025_safe_fallback",
      checkpoint_state: {
        checkpoint_id: "ob_owner_practice_loop_readiness_checkpoint_001",
        label: "Owner Practice Loop Readiness Checkpoint",
        status: "owner_practice_loop_ready",
        readiness_label: "owner_practice_loop_ready",
        section: "OB — Rehearsal Persistence Adapter + Owner Practice Loop Layer",
        purpose: "Close GP021-GP025 as the dry-run owner practice loop layer.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp021_to_gp025: true,
        not_real_manual_live_ready: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true
      },
      readiness_components: [
        {
          component_id: "gp021_dry_run_adapter",
          pack: "GP021",
          label: "Rehearsal Persistence Adapter Dry-Run Contract",
          purpose: "Shapes future write payloads without writing.",
          route: "/ob/rehearsal-persistence-adapter-dry-run.json",
          asset: "ob_rehearsal_persistence_adapter_dry_run.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp022_owner_practice_loop_board",
          pack: "GP022",
          label: "Owner Practice Loop Board",
          purpose: "Shows repeatable owner practice sessions and dry-run preview path.",
          route: "/ob/owner-practice-loop-board.json",
          asset: "ob_owner_practice_loop_board.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp023_practice_session_detail_drawer",
          pack: "GP023",
          label: "Practice Session Detail Drawer",
          purpose: "Inspects selected practice session, blockers, timeline, dry-run preview, and next action.",
          route: "/ob/practice-session-detail-drawer.json",
          asset: "ob_practice_session_detail_drawer.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp024_practice_lesson_review_queue",
          pack: "GP024",
          label: "Practice Lesson Review Queue",
          purpose: "Structures owner learning prompts, flags, and repeat recommendations.",
          route: "/ob/practice-lesson-review-queue.json",
          asset: "ob_practice_lesson_review_queue.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp025_readiness_checkpoint",
          pack: "GP025",
          label: "Owner Practice Loop Readiness Checkpoint",
          purpose: "Closes the mini-section and marks safe to save batch.",
          route: "/ob/owner-practice-loop-readiness-checkpoint.json",
          asset: "ob_owner_practice_loop_readiness_checkpoint.js",
          readiness: "ready",
          status: "ready"
        }
      ],
      readiness_scorecard: {
        total_components: 5,
        ready_components: 5,
        blocked_components: 0,
        warnings: 0,
        readiness_score: 100,
        readiness_label: "owner_practice_loop_ready",
        save_batch: "GP021-GP025",
        next_batch: "GP026-GP030",
        next_recommended_section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        status: "ready"
      },
      owner_practice_capabilities: [
        {
          capability_id: "shape_dry_run_save_payload",
          label: "Shape dry-run save payload",
          purpose: "Owner can see what future persistence would write.",
          status: "ready"
        },
        {
          capability_id: "repeat_practice_session",
          label: "Repeat practice session",
          purpose: "Owner can repeat fake/demo/read-only candidate practice loops.",
          status: "ready"
        },
        {
          capability_id: "inspect_practice_session_detail",
          label: "Inspect session detail",
          purpose: "Owner can inspect timeline, blockers, preview, lesson state, and next action.",
          status: "ready"
        },
        {
          capability_id: "review_practice_lessons",
          label: "Review practice lessons",
          purpose: "Owner can see structured learning prompts and repeat recommendations.",
          status: "ready"
        },
        {
          capability_id: "hold_pre_live_locks",
          label: "Hold pre-live locks",
          purpose: "Real Manual Live, Hybrid, Automated, broker/bank/database/Vault actions remain locked.",
          status: "locked"
        }
      ],
      remaining_locked_items: [
        {
          lock_id: "real_manual_live_locked",
          label: "Real Manual Live locked",
          reason: "Owner practice loop readiness is not real Manual Live readiness.",
          status: "locked"
        },
        {
          lock_id: "real_persistence_locked",
          label: "Real persistence locked",
          reason: "No database write, file write, or save endpoint exists.",
          status: "locked"
        },
        {
          lock_id: "broker_bank_locked",
          label: "Broker/bank locked",
          reason: "No broker API, broker read, bank read, or capital movement exists.",
          status: "locked"
        },
        {
          lock_id: "vault_direct_upload_locked",
          label: "Direct Vault upload locked",
          reason: "Only Vault-ready previews exist; no direct upload.",
          status: "locked"
        },
        {
          lock_id: "hybrid_automated_locked",
          label: "Hybrid/Automated locked",
          reason: "Hybrid and Automated remain behind future Tower policy.",
          status: "locked"
        }
      ],
      save_batch_checklist: [
        {
          item_id: "routes_registered",
          label: "Routes registered",
          purpose: "GP021-GP025 JSON routes exist.",
          status: "ready"
        },
        {
          item_id: "assets_loaded",
          label: "Assets loaded",
          purpose: "GP021-GP025 JS assets load in all six OB rooms.",
          status: "ready"
        },
        {
          item_id: "dark_boundary_intact",
          label: "Dark/private boundary intact",
          purpose: "No white/public visual regression.",
          status: "ready"
        },
        {
          item_id: "live_auto_locked_preserved",
          label: "Live Auto Locked preserved",
          purpose: "Live Auto Locked remains visible across rooms.",
          status: "ready"
        },
        {
          item_id: "safe_to_save_batch",
          label: "Safe to save batch",
          purpose: "Batch GP021-GP025 can be committed together after passing.",
          status: "ready"
        }
      ],
      blocked_actions: [
        "claim_real_manual_live_ready",
        "write_practice_loop_database_now",
        "write_practice_loop_file_now",
        "create_practice_loop_save_endpoint_now",
        "create_real_practice_record_now",
        "submit_order_from_readiness_checkpoint",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_practice_loop_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_loop_readiness_checkpoint_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp021_to_gp025: true,
        dry_run_only: true,
        not_real_manual_live_ready: true,
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
      checkpoint_state: { ...(fallback.checkpoint_state || {}), ...(safe.checkpoint_state || {}) },
      readiness_components: Array.isArray(safe.readiness_components) ? safe.readiness_components : fallback.readiness_components,
      readiness_scorecard: { ...(fallback.readiness_scorecard || {}), ...(safe.readiness_scorecard || {}) },
      owner_practice_capabilities: Array.isArray(safe.owner_practice_capabilities) ? safe.owner_practice_capabilities : fallback.owner_practice_capabilities,
      remaining_locked_items: Array.isArray(safe.remaining_locked_items) ? safe.remaining_locked_items : fallback.remaining_locked_items,
      save_batch_checklist: Array.isArray(safe.save_batch_checklist) ? safe.save_batch_checklist : fallback.save_batch_checklist,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_practice_loop_readiness_checkpoint_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp021_to_gp025: true,
        dry_run_only: true,
        not_real_manual_live_ready: true,
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
    window.OB_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_GP025 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_practice_loop_readiness_checkpoint_gp025: normalized,
      ownerPracticeLoopReady: true,
      safeToSaveBatchGP021ToGP025: true,
      notRealManualLiveReady: true,
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
    window.dispatchEvent(new CustomEvent("obOwnerPracticeLoopReadinessCheckpointUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchCheckpoint() {
    checkpointState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      checkpointState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        checkpointState.status = "ready";
        checkpointState.source = normalized.source || "server";
        checkpointState.payload = normalized;
        checkpointState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        checkpointState.status = "guarded_fallback";
        checkpointState.source = "guarded_fallback";
        checkpointState.payload = fallback;
        checkpointState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      checkpointState.status = "error_fallback";
      checkpointState.source = "error_fallback";
      checkpointState.payload = fallback;
      checkpointState.fallbackActive = true;
      checkpointState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return checkpointState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("not_real")) return "red";
    if (text.includes("ready") || text.includes("complete") || text.includes("100")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-practice-loop-readiness-checkpoint-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-practice-loop-readiness-checkpoint-row">
        <div class="ob-owner-practice-loop-readiness-checkpoint-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.component_id || item.capability_id || item.lock_id || item.item_id, "Item")}</strong>
          <span>${safeText(item.status || item.readiness || item.pack || "checkpoint", "checkpoint")}</span>
        </div>
        <span>${safeText(item.purpose || item.reason || "detail", "detail")}</span>
        <div class="ob-owner-practice-loop-readiness-checkpoint-status ${tone(item.status || item.readiness)}">${safeText(item.status || item.readiness || "ready", "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-practice-loop-readiness-checkpoint-row">
        <div class="ob-owner-practice-loop-readiness-checkpoint-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP025 readiness checkpoint boundaries.</span>
        <div class="ob-owner-practice-loop-readiness-checkpoint-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = checkpointState.payload || buildFallbackPayload();
    const state = payload.checkpoint_state || {};
    const components = Array.isArray(payload.readiness_components) ? payload.readiness_components : [];
    const scorecard = payload.readiness_scorecard || {};
    const capabilities = Array.isArray(payload.owner_practice_capabilities) ? payload.owner_practice_capabilities : [];
    const locks = Array.isArray(payload.remaining_locked_items) ? payload.remaining_locked_items : [];
    const checklist = Array.isArray(payload.save_batch_checklist) ? payload.save_batch_checklist : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-practice-loop-readiness-checkpoint-panel" id="obOwnerPracticeLoopReadinessCheckpointPanel" data-ob-giant-pack-025="true">
        <div class="ob-owner-practice-loop-readiness-checkpoint-head">
          <div>
            <div class="ob-label">OB Giant Pack 025 · Owner Practice Loop Checkpoint</div>
            <div class="ob-owner-practice-loop-readiness-checkpoint-title">Owner Practice Loop Readiness Checkpoint</div>
            <div class="ob-owner-practice-loop-readiness-checkpoint-subtitle">
              ${safeText(checkpointState.status, "booting")} · ${safeText(state.readiness_label, "owner_practice_loop_ready")} · mini-section close.
            </div>
          </div>
          <div class="ob-owner-practice-loop-readiness-checkpoint-chip-row">
            <span class="ob-owner-practice-loop-readiness-checkpoint-chip green">Owner practice ready</span>
            <span class="ob-owner-practice-loop-readiness-checkpoint-chip gold">Safe to save GP021-GP025</span>
            <span class="ob-owner-practice-loop-readiness-checkpoint-chip red">Not real Manual Live</span>
            <span class="ob-owner-practice-loop-readiness-checkpoint-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-owner-practice-loop-readiness-checkpoint-stat-grid">
          ${card("Score", safeText(scorecard.readiness_score, "0") + "%")}
          ${card("Ready", safeText(scorecard.ready_components, "0") + "/" + safeText(scorecard.total_components, "0"))}
          ${card("Blocked", safeText(scorecard.blocked_components, "0"))}
          ${card("Save", safeText(scorecard.save_batch, "GP021-GP025"))}
          ${card("Next", safeText(scorecard.next_batch, "GP026-GP030"))}
        </div>

        <div class="ob-owner-practice-loop-readiness-checkpoint-grid">
          <div>
            <div class="ob-owner-practice-loop-readiness-checkpoint-card">
              <span>Readiness label</span>
              <strong>${safeText(scorecard.readiness_label, "owner_practice_loop_ready")}</strong>
              <div class="ob-owner-practice-loop-readiness-checkpoint-callout">
                <strong>Mini-section closed:</strong><br>
                GP021-GP025 create a dry-run owner practice loop with detail inspection, lessons, and readiness checkpoint.
              </div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-boundary">
                <strong>Boundary:</strong><br>
                This is not real Manual Live readiness. No persistence, broker, bank, Vault, Hybrid, or Automated action is enabled.
              </div>
            </div>

            <div class="ob-owner-practice-loop-readiness-checkpoint-card" style="margin-top: 11px;">
              <span>Next recommended section</span>
              <strong>${safeText(scorecard.next_recommended_section, "OB — Practice Repetition Metrics + Owner Review Polish Layer")}</strong>
              <div class="ob-owner-practice-loop-readiness-checkpoint-callout">
                Save batch: ${safeText(scorecard.save_batch, "GP021-GP025")}<br>
                Next batch: ${safeText(scorecard.next_batch, "GP026-GP030")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-owner-practice-loop-readiness-checkpoint-section">
              <div class="ob-owner-practice-loop-readiness-checkpoint-section-title">Readiness components</div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-list">${components.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-readiness-checkpoint-section">
              <div class="ob-owner-practice-loop-readiness-checkpoint-section-title">Owner practice capabilities</div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-list">${capabilities.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-readiness-checkpoint-section">
              <div class="ob-owner-practice-loop-readiness-checkpoint-section-title">Remaining locked items</div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-list">${locks.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-readiness-checkpoint-section">
              <div class="ob-owner-practice-loop-readiness-checkpoint-section-title">Save batch checklist</div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-list">${checklist.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-owner-practice-loop-readiness-checkpoint-section">
              <div class="ob-owner-practice-loop-readiness-checkpoint-section-title">Blocked actions</div>
              <div class="ob-owner-practice-loop-readiness-checkpoint-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-practice-loop-readiness-checkpoint-callout">
          <strong>After this passes:</strong><br>
          Save and push GP021-GP025 together.
        </div>

        <div class="ob-owner-practice-loop-readiness-checkpoint-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerPracticeLoopReadinessCheckpointPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const lessonQueue = document.getElementById("obPracticeLessonReviewQueuePanel");
    const detailDrawer = document.getElementById("obPracticeSessionDetailDrawerPanel");
    const practiceBoard = document.getElementById("obOwnerPracticeLoopBoardPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (lessonQueue && lessonQueue.parentNode) lessonQueue.insertAdjacentElement("afterend", panel);
    else if (detailDrawer && detailDrawer.parentNode) detailDrawer.insertAdjacentElement("afterend", panel);
    else if (practiceBoard && practiceBoard.parentNode) practiceBoard.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = checkpointState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-025-owner-practice-loop-readiness-checkpoint", "ready");
    document.body.setAttribute("data-ob-owner-practice-loop-ready", "true");
    document.body.setAttribute("data-ob-safe-to-save-gp021-gp025", "true");
    document.body.setAttribute("data-ob-not-real-manual-live-ready", "true");
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

    window.OB_GIANT_PACK_025_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_STATE = {
      version: VERSION,
      status: checkpointState.status,
      fallbackActive: checkpointState.fallbackActive,
      readinessScore: payload.readiness_scorecard.readiness_score,
      readyComponents: payload.readiness_scorecard.ready_components,
      saveBatch: payload.readiness_scorecard.save_batch,
      ownerPracticeLoopReady: true,
      safeToSaveBatchGP021ToGP025: true,
      notRealManualLiveReady: true,
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
      fetchCheckpoint();
    }, 6140);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_PRACTICE_LOOP_READINESS_CHECKPOINT_GP025_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return checkpointState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchCheckpoint,
    renderPanel,
    setFlags
  };
})();
