// OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_CONTRACT_JS

(function () {
  const VERSION = "OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_CONTRACT";
  const ENDPOINT = "/ob/rehearsal-persistence-adapter-dry-run.json";

  // SMOKE MARKERS
  // Rehearsal Persistence Adapter Dry-Run Contract
  // persistence adapter dry run
  // dry run write payload
  // no database write
  // no file write
  // no save endpoint
  // owner practice loop source
  // rehearsal session write shape
  // rehearsal decision write shape
  // rehearsal preflight write shape
  // rehearsal checklist write shape
  // rehearsal fill write shape
  // rehearsal not placed write shape
  // rehearsal close write shape
  // rehearsal final review write shape
  // rehearsal receipt write shape
  // validation before write
  // Tower step-up required later
  // Review Center read model target
  // adapter input contract
  // adapter output contract
  // rollback placeholder
  // idempotency key placeholder
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let adapterState = {
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
      source: "ob_giant_pack_021_safe_fallback",
      adapter_state: {
        adapter_id: "ob_rehearsal_persistence_adapter_dry_run_001",
        label: "Rehearsal Persistence Adapter Dry-Run Contract",
        status: "dry_run_adapter_ready",
        purpose: "Shape future rehearsal persistence write payloads without writing anything yet.",
        section: "OB — Rehearsal Persistence Adapter + Owner Practice Loop Layer",
        owner_only: true,
        dry_run_only: true,
        no_database_write: true,
        no_file_write: true,
        no_save_endpoint: true,
        no_broker_data: true,
        no_direct_vault_upload: true,
        record_contract_source: "/ob/rehearsal-record-contracts.json",
        owner_input_source: "/ob/owner-input-persistence-prep.json",
        command_board_target: "/ob/review-center-rehearsal-command-board.json"
      },
      adapter_input_contracts: [
        {
          input_id: "owner_decision_draft_input",
          label: "Owner decision draft input",
          accepts: "decision_input_draft",
          target_record: "rehearsal_decision_record",
          required_before_dry_run: ["session_id", "candidate_id", "decision", "decision_reason", "owner_action", "timestamp"],
          status: "ready"
        },
        {
          input_id: "owner_preflight_draft_input",
          label: "Owner preflight draft input",
          accepts: "preflight_input_draft",
          target_record: "rehearsal_preflight_record",
          required_before_dry_run: ["session_id", "account_policy_state", "mode_permission_state", "kill_switch_state", "data_freshness_state", "owner_action", "timestamp"],
          status: "ready"
        },
        {
          input_id: "owner_checklist_draft_input",
          label: "Owner checklist draft input",
          accepts: "checklist_input_draft",
          target_record: "rehearsal_checklist_record",
          required_before_dry_run: ["session_id", "broker_account_confirmed", "symbol_contract_confirmed", "action_side_confirmed", "limit_order_confirmed", "entry_limit", "stop_plan", "target_plan"],
          status: "ready"
        },
        {
          input_id: "owner_fill_draft_input",
          label: "Owner fill draft input",
          accepts: "fill_or_not_placed_input_draft",
          target_record: "rehearsal_fill_record",
          required_before_dry_run: ["session_id", "fill_or_not_placed_choice", "symbol_or_contract", "owner_action", "timestamp"],
          status: "ready"
        },
        {
          input_id: "owner_not_placed_draft_input",
          label: "Owner not-placed draft input",
          accepts: "fill_or_not_placed_input_draft",
          target_record: "rehearsal_not_placed_record",
          required_before_dry_run: ["session_id", "fill_or_not_placed_choice", "not_placed_reason", "owner_action", "timestamp"],
          status: "ready"
        },
        {
          input_id: "owner_close_draft_input",
          label: "Owner close draft input",
          accepts: "close_input_draft",
          target_record: "rehearsal_close_record",
          required_before_dry_run: ["session_id", "close_decision", "close_reason", "close_time", "close_price", "close_quantity", "realized_result"],
          status: "ready"
        },
        {
          input_id: "owner_final_review_draft_input",
          label: "Owner final review draft input",
          accepts: "final_review_input_draft",
          target_record: "rehearsal_final_review_record",
          required_before_dry_run: ["session_id", "realized_result_summary", "setup_quality_review", "entry_quality_review", "exit_quality_review", "risk_management_review", "lesson_record"],
          status: "ready"
        }
      ],
      adapter_output_contracts: [
        {
          output_id: "dry_run_write_payload",
          label: "Dry-run write payload",
          purpose: "Shows exactly what would be written later without writing it.",
          emits: ["record_type", "record_id_preview", "session_id", "source_app", "owner_action", "validation_state", "write_blocked_reason", "review_center_target"],
          status: "ready"
        },
        {
          output_id: "review_center_read_model_target",
          label: "Review Center read model target",
          purpose: "Shapes future records so Review Center can read them cleanly.",
          emits: ["session_rollup", "missing_steps", "quality_flags", "freshness_flags", "owner_readiness_label", "next_action"],
          status: "ready"
        },
        {
          output_id: "vault_ready_receipt_preview",
          label: "Vault-ready receipt preview",
          purpose: "Shows Vault-ready receipt preview with no direct Vault upload.",
          emits: ["receipt_id_preview", "vault_ready", "vault_destination_placeholder", "no_direct_vault_upload"],
          status: "ready"
        }
      ],
      dry_run_validation_gates: [
        {
          gate_id: "required_fields_present",
          label: "Required fields present",
          purpose: "Dry-run payload cannot be shaped if required fields are missing.",
          block_reason: "missing_required_fields",
          severity: "blocking",
          status: "ready"
        },
        {
          gate_id: "record_contract_match",
          label: "Record contract match",
          purpose: "Input must match GP012 target record contract.",
          block_reason: "record_contract_mismatch",
          severity: "blocking",
          status: "ready"
        },
        {
          gate_id: "quality_freshness_pass",
          label: "Quality/freshness pass",
          purpose: "Input must preserve source confidence and freshness labels.",
          block_reason: "quality_or_freshness_failed",
          severity: "blocking",
          status: "ready"
        },
        {
          gate_id: "tower_step_up_required_later",
          label: "Tower step-up required later",
          purpose: "Actual write later requires Tower step-up; GP021 only shapes the request.",
          block_reason: "tower_step_up_not_active_yet",
          severity: "locked",
          status: "placeholder"
        },
        {
          gate_id: "idempotency_key_placeholder",
          label: "Idempotency key placeholder",
          purpose: "Future writes must prevent duplicate rehearsal records.",
          block_reason: "idempotency_not_wired_yet",
          severity: "placeholder",
          status: "placeholder"
        },
        {
          gate_id: "rollback_placeholder",
          label: "Rollback placeholder",
          purpose: "Future writes must have a rollback/revoke strategy.",
          block_reason: "rollback_not_wired_yet",
          severity: "placeholder",
          status: "placeholder"
        }
      ],
      dry_run_payload_shape: {
        payload_id: "rehearsal_dry_run_payload_shape_001",
        required_fields: [
          "dry_run_id",
          "idempotency_key_preview",
          "record_type",
          "record_id_preview",
          "session_id",
          "source_app",
          "owner_action",
          "mission_account",
          "business_lane",
          "sensitivity",
          "freshness_label",
          "confidence_label",
          "validation_state",
          "blocked_reason",
          "tower_step_up_required",
          "review_center_target",
          "vault_ready",
          "no_direct_vault_upload",
          "created_at_preview"
        ],
        status: "ready"
      },
      owner_practice_loop_handoff: [
        {
          step_id: "select_rehearsal_session",
          label: "Select rehearsal session",
          purpose: "Owner selects active or completed rehearsal session.",
          status: "ready"
        },
        {
          step_id: "collect_owner_draft",
          label: "Collect owner draft",
          purpose: "Owner input draft is collected from GP014 shape.",
          status: "ready"
        },
        {
          step_id: "run_dry_validation",
          label: "Run dry validation",
          purpose: "Required fields, quality, freshness, and contract match are checked.",
          status: "ready"
        },
        {
          step_id: "shape_dry_run_payload",
          label: "Shape dry-run payload",
          purpose: "Adapter shapes what future persistence would write.",
          status: "ready"
        },
        {
          step_id: "show_review_center_preview",
          label: "Show Review Center preview",
          purpose: "Review Center can preview the dry-run result.",
          status: "ready"
        },
        {
          step_id: "block_actual_write",
          label: "Block actual write",
          purpose: "Actual write remains disabled until future persistence pack.",
          status: "locked"
        }
      ],
      blocked_actions: [
        "write_rehearsal_database_now",
        "write_file_now",
        "create_save_endpoint_now",
        "persist_owner_input_now",
        "create_real_record_id_now",
        "claim_tower_step_up_approved",
        "read_broker_account",
        "submit_order_from_ob",
        "auto_execute",
        "read_bank_account",
        "move_real_capital",
        "upload_direct_to_vault",
        "show_owner_practice_records_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        persistence_adapter_dry_run_only: true,
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
        tower_step_up_required_later: true,
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
      adapter_state: { ...(fallback.adapter_state || {}), ...(safe.adapter_state || {}) },
      adapter_input_contracts: Array.isArray(safe.adapter_input_contracts) ? safe.adapter_input_contracts : fallback.adapter_input_contracts,
      adapter_output_contracts: Array.isArray(safe.adapter_output_contracts) ? safe.adapter_output_contracts : fallback.adapter_output_contracts,
      dry_run_validation_gates: Array.isArray(safe.dry_run_validation_gates) ? safe.dry_run_validation_gates : fallback.dry_run_validation_gates,
      dry_run_payload_shape: { ...(fallback.dry_run_payload_shape || {}), ...(safe.dry_run_payload_shape || {}) },
      owner_practice_loop_handoff: Array.isArray(safe.owner_practice_loop_handoff) ? safe.owner_practice_loop_handoff : fallback.owner_practice_loop_handoff,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        persistence_adapter_dry_run_only: true,
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
        tower_step_up_required_later: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_GP021 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      rehearsal_persistence_adapter_dry_run_gp021: normalized,
      persistenceAdapterDryRunOnly: true,
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
    window.dispatchEvent(new CustomEvent("obRehearsalPersistenceAdapterDryRunUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchAdapter() {
    adapterState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      adapterState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        adapterState.status = "ready";
        adapterState.source = normalized.source || "server";
        adapterState.payload = normalized;
        adapterState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        adapterState.status = "guarded_fallback";
        adapterState.source = "guarded_fallback";
        adapterState.payload = fallback;
        adapterState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      adapterState.status = "error_fallback";
      adapterState.source = "error_fallback";
      adapterState.payload = fallback;
      adapterState.fallbackActive = true;
      adapterState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return adapterState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("placeholder") || text.includes("disabled")) return "red";
    if (text.includes("ready") || text.includes("pass")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-rehearsal-persistence-dry-run-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-rehearsal-persistence-dry-run-row">
        <div class="ob-rehearsal-persistence-dry-run-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.input_id || item.output_id || item.gate_id || item.step_id, "Item")}</strong>
          <span>${safeText(item.status || item.target_record || item.severity || "dry-run", "dry-run")}</span>
        </div>
        <span>${safeText(item.purpose || item.accepts || item.block_reason || "detail", "detail")}</span>
        <div class="ob-rehearsal-persistence-dry-run-status ${tone(item.status || item.severity)}">${safeText(item.status || item.severity || "ready", "ready")}</div>
      </div>
    `;
  }

  function inputRow(item) {
    const required = Array.isArray(item.required_before_dry_run) ? item.required_before_dry_run.join(" · ") : "none";
    return `
      <div class="ob-rehearsal-persistence-dry-run-row">
        <div class="ob-rehearsal-persistence-dry-run-dot">I</div>
        <div>
          <strong>${safeText(item.label, "Input contract")}</strong>
          <span>${safeText(item.target_record, "target")}</span>
        </div>
        <span>
          Accepts: ${safeText(item.accepts, "draft")}<br>
          Required before dry-run: ${required}
        </span>
        <div class="ob-rehearsal-persistence-dry-run-status green">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function fieldRows(fields) {
    return (fields || []).map((field) => `
      <div class="ob-rehearsal-persistence-dry-run-row">
        <div class="ob-rehearsal-persistence-dry-run-dot">F</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>payload field</span>
        </div>
        <span>Required in dry-run payload shape.</span>
        <div class="ob-rehearsal-persistence-dry-run-status gold">required</div>
      </div>
    `).join("");
  }

  function blockedRow(item) {
    return `
      <div class="ob-rehearsal-persistence-dry-run-row">
        <div class="ob-rehearsal-persistence-dry-run-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP021 dry-run persistence boundaries.</span>
        <div class="ob-rehearsal-persistence-dry-run-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = adapterState.payload || buildFallbackPayload();
    const state = payload.adapter_state || {};
    const inputs = Array.isArray(payload.adapter_input_contracts) ? payload.adapter_input_contracts : [];
    const outputs = Array.isArray(payload.adapter_output_contracts) ? payload.adapter_output_contracts : [];
    const gates = Array.isArray(payload.dry_run_validation_gates) ? payload.dry_run_validation_gates : [];
    const shape = payload.dry_run_payload_shape || {};
    const flow = Array.isArray(payload.owner_practice_loop_handoff) ? payload.owner_practice_loop_handoff : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-rehearsal-persistence-dry-run-panel" id="obRehearsalPersistenceAdapterDryRunPanel" data-ob-giant-pack-021="true">
        <div class="ob-rehearsal-persistence-dry-run-head">
          <div>
            <div class="ob-label">OB Giant Pack 021 · Rehearsal Persistence Adapter</div>
            <div class="ob-rehearsal-persistence-dry-run-title">Dry-Run Persistence Adapter Contract</div>
            <div class="ob-rehearsal-persistence-dry-run-subtitle">
              ${safeText(adapterState.status, "booting")} · ${safeText(state.status, "dry_run_adapter_ready")} · shapes future writes without writing.
            </div>
          </div>
          <div class="ob-rehearsal-persistence-dry-run-chip-row">
            <span class="ob-rehearsal-persistence-dry-run-chip green">Dry-run payload</span>
            <span class="ob-rehearsal-persistence-dry-run-chip gold">Review Center target</span>
            <span class="ob-rehearsal-persistence-dry-run-chip red">No DB write</span>
            <span class="ob-rehearsal-persistence-dry-run-chip red">No save endpoint</span>
          </div>
        </div>

        <div class="ob-rehearsal-persistence-dry-run-stat-grid">
          ${card("Inputs", String(inputs.length))}
          ${card("Outputs", String(outputs.length))}
          ${card("Gates", String(gates.length))}
          ${card("Loop steps", String(flow.length))}
          ${card("Write", "disabled")}
        </div>

        <div class="ob-rehearsal-persistence-dry-run-grid">
          <div>
            <div class="ob-rehearsal-persistence-dry-run-card">
              <span>Purpose</span>
              <strong>Prepare future rehearsal record persistence by shaping dry-run write payloads only.</strong>
              <div class="ob-rehearsal-persistence-dry-run-callout">
                <strong>Dry-run means:</strong><br>
                OB can preview what would be saved later, but it does not create records, write files, open a save endpoint, touch broker/bank data, or upload to Vault.
              </div>
              <div class="ob-rehearsal-persistence-dry-run-boundary">
                <strong>Boundary:</strong><br>
                No database write. No file write. No real record IDs. No broker API. No order submit. No direct Vault upload.
              </div>
            </div>

            <div class="ob-rehearsal-persistence-dry-run-card" style="margin-top: 11px;">
              <span>Dry-run payload shape</span>
              <strong>${safeText(shape.payload_id, "payload shape")}</strong>
              <div class="ob-rehearsal-persistence-dry-run-list">${fieldRows(shape.required_fields || [])}</div>
            </div>
          </div>

          <div>
            <div class="ob-rehearsal-persistence-dry-run-section">
              <div class="ob-rehearsal-persistence-dry-run-section-title">Adapter input contracts</div>
              <div class="ob-rehearsal-persistence-dry-run-list">${inputs.map(inputRow).join("")}</div>
            </div>

            <div class="ob-rehearsal-persistence-dry-run-section">
              <div class="ob-rehearsal-persistence-dry-run-section-title">Adapter output contracts</div>
              <div class="ob-rehearsal-persistence-dry-run-list">${outputs.map((item, index) => row(item, index, "O")).join("")}</div>
            </div>

            <div class="ob-rehearsal-persistence-dry-run-section">
              <div class="ob-rehearsal-persistence-dry-run-section-title">Dry-run validation gates</div>
              <div class="ob-rehearsal-persistence-dry-run-list">${gates.map((item, index) => row(item, index, "G")).join("")}</div>
            </div>

            <div class="ob-rehearsal-persistence-dry-run-section">
              <div class="ob-rehearsal-persistence-dry-run-section-title">Owner practice loop handoff</div>
              <div class="ob-rehearsal-persistence-dry-run-list">${flow.map((item, index) => row(item, index, "L")).join("")}</div>
            </div>

            <div class="ob-rehearsal-persistence-dry-run-section">
              <div class="ob-rehearsal-persistence-dry-run-section-title">Blocked actions</div>
              <div class="ob-rehearsal-persistence-dry-run-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-rehearsal-persistence-dry-run-callout">
          <strong>Next handoff:</strong><br>
          GP022 can create the Owner Practice Loop Board that uses this dry-run adapter to show repeatable practice sessions.
        </div>

        <div class="ob-rehearsal-persistence-dry-run-boundary">
          <strong>Still locked:</strong><br>
          No DB write. No file write. No save endpoint. No real record creation. No broker/bank action. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obRehearsalPersistenceAdapterDryRunPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const preLiveLockPanel = document.getElementById("obManualLivePreLiveLockWallPanel");
    const qualityPanel = document.getElementById("obRehearsalQualityFreshnessGatePanel");
    const finalReadinessPanel = document.getElementById("obManualLiveOwnerRehearsalFinalReadinessPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (preLiveLockPanel && preLiveLockPanel.parentNode) preLiveLockPanel.insertAdjacentElement("afterend", panel);
    else if (qualityPanel && qualityPanel.parentNode) qualityPanel.insertAdjacentElement("afterend", panel);
    else if (finalReadinessPanel && finalReadinessPanel.parentNode) finalReadinessPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = adapterState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-021-rehearsal-persistence-adapter-dry-run", "ready");
    document.body.setAttribute("data-ob-persistence-adapter-dry-run-only", "true");
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

    window.OB_GIANT_PACK_021_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_STATE = {
      version: VERSION,
      status: adapterState.status,
      fallbackActive: adapterState.fallbackActive,
      inputContractCount: payload.adapter_input_contracts.length,
      outputContractCount: payload.adapter_output_contracts.length,
      dryRunGateCount: payload.dry_run_validation_gates.length,
      persistenceAdapterDryRunOnly: true,
      dryRunOnly: true,
      noDatabaseWrite: true,
      noFileWrite: true,
      noSaveEndpoint: true,
      noRealRecordCreation: true,
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
      fetchAdapter();
    }, 5500);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_REHEARSAL_PERSISTENCE_ADAPTER_DRY_RUN_GP021_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return adapterState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchAdapter,
    renderPanel,
    setFlags
  };
})();
