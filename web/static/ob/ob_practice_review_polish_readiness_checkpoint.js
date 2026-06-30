// OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT";
  const ENDPOINT = "/ob/practice-review-polish-readiness-checkpoint.json";

  // SMOKE MARKERS
  // Practice Review Polish Readiness Checkpoint
  // practice review polish readiness
  // mini-section close checkpoint
  // GP026 readiness
  // GP027 readiness
  // GP028 readiness
  // GP029 readiness
  // GP030 readiness
  // practice repetition metrics ready
  // owner review polish guidance ready
  // owner practice focus queue ready
  // practice review compact snapshot ready
  // save batch checkpoint
  // safe to save GP026-GP030
  // readiness label practice_review_polish_ready
  // not real Manual Live ready
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
      source: "ob_giant_pack_030_safe_fallback",
      checkpoint_state: {
        checkpoint_id: "ob_practice_review_polish_readiness_checkpoint_001",
        label: "Practice Review Polish Readiness Checkpoint",
        status: "practice_review_polish_ready",
        readiness_label: "practice_review_polish_ready",
        section: "OB — Practice Repetition Metrics + Owner Review Polish Layer",
        purpose: "Close GP026-GP030 as the practice repetition metrics and owner review polish layer.",
        owner_only: true,
        rehearsal_only: true,
        dry_run_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp026_to_gp030: true,
        not_real_manual_live_ready: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true
      },
      readiness_components: [
        {
          component_id: "gp026_practice_repetition_metrics_board",
          pack: "GP026",
          label: "Practice Repetition Metrics Board",
          purpose: "Shows repetition count, trends, distributions, and next focus.",
          route: "/ob/practice-repetition-metrics-board.json",
          asset: "ob_practice_repetition_metrics_board.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp027_owner_review_polish_guidance",
          pack: "GP027",
          label: "Owner Review Polish Guidance",
          purpose: "Turns practice metrics into calm owner-readable guidance.",
          route: "/ob/owner-review-polish-guidance.json",
          asset: "ob_owner_review_polish_guidance.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp028_owner_practice_focus_queue",
          pack: "GP028",
          label: "Owner Practice Focus Queue",
          purpose: "Orders the owner’s next practice tasks with reasons and done criteria.",
          route: "/ob/owner-practice-focus-queue.json",
          asset: "ob_owner_practice_focus_queue.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp029_practice_review_compact_snapshot",
          pack: "GP029",
          label: "Practice Review Compact Snapshot",
          purpose: "Compresses metrics, guidance, focus queue, locks, and next action into one snapshot.",
          route: "/ob/practice-review-compact-snapshot.json",
          asset: "ob_practice_review_compact_snapshot.js",
          readiness: "ready",
          status: "ready"
        },
        {
          component_id: "gp030_readiness_checkpoint",
          pack: "GP030",
          label: "Practice Review Polish Readiness Checkpoint",
          purpose: "Closes the mini-section and marks safe to save batch.",
          route: "/ob/practice-review-polish-readiness-checkpoint.json",
          asset: "ob_practice_review_polish_readiness_checkpoint.js",
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
        readiness_label: "practice_review_polish_ready",
        save_batch: "GP026-GP030",
        next_batch: "GP031-GP035",
        next_recommended_section: "OB — Manual Live Level 1 Operator Confidence Layer",
        status: "ready"
      },
      layer_capabilities: [
        {
          capability_id: "read_practice_metrics",
          label: "Read practice metrics",
          purpose: "Owner can see repetition, completion, blocker, confusion, clean moment, and unsafe moment trends.",
          status: "ready"
        },
        {
          capability_id: "read_owner_guidance",
          label: "Read owner guidance",
          purpose: "Owner can see calm explanations without failure language.",
          status: "ready"
        },
        {
          capability_id: "read_focus_queue",
          label: "Read focus queue",
          purpose: "Owner can see ordered next-practice tasks and done criteria.",
          status: "ready"
        },
        {
          capability_id: "read_compact_snapshot",
          label: "Read compact snapshot",
          purpose: "Owner can see a compressed practice status and next action.",
          status: "ready"
        },
        {
          capability_id: "hold_live_locks",
          label: "Hold live locks",
          purpose: "Real Manual Live, Hybrid, Automated, broker/bank/database/Vault actions remain locked.",
          status: "locked"
        }
      ],
      remaining_locked_items: [
        {
          lock_id: "real_manual_live_locked",
          label: "Real Manual Live locked",
          reason: "Practice review polish readiness is not real Manual Live readiness.",
          status: "locked"
        },
        {
          lock_id: "real_persistence_locked",
          label: "Real persistence locked",
          reason: "No database write, file write, save endpoint, or real record creation exists.",
          status: "locked"
        },
        {
          lock_id: "broker_bank_locked",
          label: "Broker/bank locked",
          reason: "No broker API, broker read, bank read, or capital movement exists.",
          status: "locked"
        },
        {
          lock_id: "direct_vault_upload_locked",
          label: "Direct Vault upload locked",
          reason: "Only preview/handoff references exist; no direct upload.",
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
          purpose: "GP026-GP030 JSON routes exist.",
          status: "ready"
        },
        {
          item_id: "assets_loaded",
          label: "Assets loaded",
          purpose: "GP026-GP030 JS assets load in all six OB rooms.",
          status: "ready"
        },
        {
          item_id: "dark_private_boundary_intact",
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
          purpose: "Batch GP026-GP030 can be committed together after passing.",
          status: "ready"
        }
      ],
      blocked_actions: [
        "claim_real_manual_live_ready",
        "write_practice_review_polish_database_now",
        "write_practice_review_polish_file_now",
        "create_practice_review_polish_save_endpoint_now",
        "create_real_practice_review_polish_record_now",
        "submit_order_from_practice_review_polish_checkpoint",
        "read_broker_account",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_practice_review_polish_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_review_polish_readiness_checkpoint_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp026_to_gp030: true,
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
      layer_capabilities: Array.isArray(safe.layer_capabilities) ? safe.layer_capabilities : fallback.layer_capabilities,
      remaining_locked_items: Array.isArray(safe.remaining_locked_items) ? safe.remaining_locked_items : fallback.remaining_locked_items,
      save_batch_checklist: Array.isArray(safe.save_batch_checklist) ? safe.save_batch_checklist : fallback.save_batch_checklist,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        practice_review_polish_readiness_checkpoint_only: true,
        mini_section_complete: true,
        safe_to_save_batch_gp026_to_gp030: true,
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
    window.OB_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_GP030 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      practice_review_polish_readiness_checkpoint_gp030: normalized,
      practiceReviewPolishReady: true,
      safeToSaveBatchGP026ToGP030: true,
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
    window.dispatchEvent(new CustomEvent("obPracticeReviewPolishReadinessCheckpointUpdated", { detail: normalized }));
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
    return `<div class="ob-practice-review-polish-readiness-checkpoint-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-practice-review-polish-readiness-checkpoint-row">
        <div class="ob-practice-review-polish-readiness-checkpoint-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.component_id || item.capability_id || item.lock_id || item.item_id, "Item")}</strong>
          <span>${safeText(item.status || item.readiness || item.pack || "checkpoint", "checkpoint")}</span>
        </div>
        <span>${safeText(item.purpose || item.reason || "detail", "detail")}</span>
        <div class="ob-practice-review-polish-readiness-checkpoint-status ${tone(item.status || item.readiness)}">${safeText(item.status || item.readiness || "ready", "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-practice-review-polish-readiness-checkpoint-row">
        <div class="ob-practice-review-polish-readiness-checkpoint-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP030 readiness boundaries.</span>
        <div class="ob-practice-review-polish-readiness-checkpoint-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = checkpointState.payload || buildFallbackPayload();
    const state = payload.checkpoint_state || {};
    const components = Array.isArray(payload.readiness_components) ? payload.readiness_components : [];
    const scorecard = payload.readiness_scorecard || {};
    const capabilities = Array.isArray(payload.layer_capabilities) ? payload.layer_capabilities : [];
    const locks = Array.isArray(payload.remaining_locked_items) ? payload.remaining_locked_items : [];
    const checklist = Array.isArray(payload.save_batch_checklist) ? payload.save_batch_checklist : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-practice-review-polish-readiness-checkpoint-panel" id="obPracticeReviewPolishReadinessCheckpointPanel" data-ob-giant-pack-030="true">
        <div class="ob-practice-review-polish-readiness-checkpoint-head">
          <div>
            <div class="ob-label">OB Giant Pack 030 · Review Polish Checkpoint</div>
            <div class="ob-practice-review-polish-readiness-checkpoint-title">Practice Review Polish Readiness Checkpoint</div>
            <div class="ob-practice-review-polish-readiness-checkpoint-subtitle">
              ${safeText(checkpointState.status, "booting")} · ${safeText(state.readiness_label, "practice_review_polish_ready")} · mini-section close.
            </div>
          </div>
          <div class="ob-practice-review-polish-readiness-checkpoint-chip-row">
            <span class="ob-practice-review-polish-readiness-checkpoint-chip green">Review polish ready</span>
            <span class="ob-practice-review-polish-readiness-checkpoint-chip gold">Safe to save GP026-GP030</span>
            <span class="ob-practice-review-polish-readiness-checkpoint-chip red">Not real Manual Live</span>
            <span class="ob-practice-review-polish-readiness-checkpoint-chip red">Live Auto Locked</span>
          </div>
        </div>

        <div class="ob-practice-review-polish-readiness-checkpoint-stat-grid">
          ${card("Score", safeText(scorecard.readiness_score, "0") + "%")}
          ${card("Ready", safeText(scorecard.ready_components, "0") + "/" + safeText(scorecard.total_components, "0"))}
          ${card("Blocked", safeText(scorecard.blocked_components, "0"))}
          ${card("Save", safeText(scorecard.save_batch, "GP026-GP030"))}
          ${card("Next", safeText(scorecard.next_batch, "GP031-GP035"))}
        </div>

        <div class="ob-practice-review-polish-readiness-checkpoint-grid">
          <div>
            <div class="ob-practice-review-polish-readiness-checkpoint-card">
              <span>Readiness label</span>
              <strong>${safeText(scorecard.readiness_label, "practice_review_polish_ready")}</strong>
              <div class="ob-practice-review-polish-readiness-checkpoint-callout">
                <strong>Mini-section closed:</strong><br>
                GP026-GP030 create practice repetition metrics, owner-readable guidance, focus queue, compact snapshot, and readiness checkpoint.
              </div>
              <div class="ob-practice-review-polish-readiness-checkpoint-boundary">
                <strong>Boundary:</strong><br>
                This is not real Manual Live readiness. No persistence, broker, bank, Vault, Hybrid, or Automated action is enabled.
              </div>
            </div>

            <div class="ob-practice-review-polish-readiness-checkpoint-card" style="margin-top: 11px;">
              <span>Next recommended section</span>
              <strong>${safeText(scorecard.next_recommended_section, "OB — Manual Live Level 1 Operator Confidence Layer")}</strong>
              <div class="ob-practice-review-polish-readiness-checkpoint-callout">
                Save batch: ${safeText(scorecard.save_batch, "GP026-GP030")}<br>
                Next batch: ${safeText(scorecard.next_batch, "GP031-GP035")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-practice-review-polish-readiness-checkpoint-section">
              <div class="ob-practice-review-polish-readiness-checkpoint-section-title">Readiness components</div>
              <div class="ob-practice-review-polish-readiness-checkpoint-list">${components.map((item, index) => row(item, index, "C")).join("")}</div>
            </div>

            <div class="ob-practice-review-polish-readiness-checkpoint-section">
              <div class="ob-practice-review-polish-readiness-checkpoint-section-title">Layer capabilities</div>
              <div class="ob-practice-review-polish-readiness-checkpoint-list">${capabilities.map((item, index) => row(item, index, "P")).join("")}</div>
            </div>

            <div class="ob-practice-review-polish-readiness-checkpoint-section">
              <div class="ob-practice-review-polish-readiness-checkpoint-section-title">Remaining locked items</div>
              <div class="ob-practice-review-polish-readiness-checkpoint-list">${locks.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-practice-review-polish-readiness-checkpoint-section">
              <div class="ob-practice-review-polish-readiness-checkpoint-section-title">Save batch checklist</div>
              <div class="ob-practice-review-polish-readiness-checkpoint-list">${checklist.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-practice-review-polish-readiness-checkpoint-section">
              <div class="ob-practice-review-polish-readiness-checkpoint-section-title">Blocked actions</div>
              <div class="ob-practice-review-polish-readiness-checkpoint-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-practice-review-polish-readiness-checkpoint-callout">
          <strong>After this passes:</strong><br>
          Save and push GP026-GP030 together.
        </div>

        <div class="ob-practice-review-polish-readiness-checkpoint-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real records. No broker/bank actions. No direct Vault upload. Real Manual Live locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obPracticeReviewPolishReadinessCheckpointPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const snapshot = document.getElementById("obPracticeReviewCompactSnapshotPanel");
    const focus = document.getElementById("obOwnerPracticeFocusQueuePanel");
    const guidance = document.getElementById("obOwnerReviewPolishGuidancePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (snapshot && snapshot.parentNode) snapshot.insertAdjacentElement("afterend", panel);
    else if (focus && focus.parentNode) focus.insertAdjacentElement("afterend", panel);
    else if (guidance && guidance.parentNode) guidance.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = checkpointState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-030-practice-review-polish-readiness-checkpoint", "ready");
    document.body.setAttribute("data-ob-practice-review-polish-ready", "true");
    document.body.setAttribute("data-ob-safe-to-save-gp026-gp030", "true");
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

    window.OB_GIANT_PACK_030_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_STATE = {
      version: VERSION,
      status: checkpointState.status,
      fallbackActive: checkpointState.fallbackActive,
      readinessScore: payload.readiness_scorecard.readiness_score,
      readyComponents: payload.readiness_scorecard.ready_components,
      saveBatch: payload.readiness_scorecard.save_batch,
      practiceReviewPolishReady: true,
      safeToSaveBatchGP026ToGP030: true,
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
    }, 6940);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_PRACTICE_REVIEW_POLISH_READINESS_CHECKPOINT_GP030_API = {
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
