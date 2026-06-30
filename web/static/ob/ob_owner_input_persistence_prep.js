// OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_JS

(function () {
  const VERSION = "OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP";
  const ENDPOINT = "/ob/owner-input-persistence-prep.json";

  // SMOKE MARKERS
  // Owner Input Persistence Prep
  // owner input draft contract
  // owner input validation plan
  // autosave contract placeholder
  // submit gate placeholder
  // draft session buffer
  // field validation map
  // required field gate
  // sensitive field lock
  // owner step up required
  // Tower step up handoff
  // Review Center write prep
  // rehearsal record write prep
  // persistence adapter placeholder
  // no database write
  // no file write
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let prepState = {
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
      source: "ob_giant_pack_014_safe_fallback",
      prep_state: {
        prep_id: "ob_owner_input_persistence_prep_001",
        label: "Owner Input Persistence Prep",
        status: "write_prep_ready",
        purpose: "Prepare safe owner input drafts for future persistence without writing to database yet.",
        owner_only: true,
        requires_tower_step_up: true,
        contract_source: "/ob/rehearsal-record-contracts.json",
        command_board_source: "/ob/review-center-rehearsal-command-board.json",
        no_database_write: true,
        no_file_write: true,
        no_broker_data: true
      },
      input_draft_contracts: [
        {
          draft_id: "decision_input_draft",
          label: "Decision input draft",
          target_record: "rehearsal_decision_record",
          required_fields: ["session_id", "candidate_id", "decision", "decision_reason", "owner_action", "timestamp"],
          optional_fields: ["blocked_reason", "confidence_label", "freshness_label", "owner_note"],
          status: "ready"
        },
        {
          draft_id: "preflight_input_draft",
          label: "Preflight input draft",
          target_record: "rehearsal_preflight_record",
          required_fields: ["session_id", "account_policy_state", "mode_permission_state", "kill_switch_state", "data_freshness_state", "owner_action", "timestamp"],
          optional_fields: ["source_confidence_state", "exposure_state", "protected_floor_state", "owner_step_up_state", "owner_note"],
          status: "ready"
        },
        {
          draft_id: "checklist_input_draft",
          label: "Checklist input draft",
          target_record: "rehearsal_checklist_record",
          required_fields: ["session_id", "broker_account_confirmed", "symbol_contract_confirmed", "action_side_confirmed", "limit_order_confirmed", "entry_limit", "stop_plan", "target_plan", "owner_action", "timestamp"],
          optional_fields: ["do_not_enter_above", "spread_liquidity_confirmed", "options_approval_confirmed", "pdt_margin_cash_acknowledged", "owner_note"],
          status: "ready"
        },
        {
          draft_id: "fill_or_not_placed_input_draft",
          label: "Fill / not-placed input draft",
          target_record: "rehearsal_fill_record_or_rehearsal_not_placed_record",
          required_fields: ["session_id", "fill_or_not_placed_choice", "symbol_or_contract", "owner_action", "timestamp"],
          optional_fields: ["fill_time", "fill_price", "quantity", "not_placed_reason", "manual_broker_confirmation", "owner_note"],
          status: "ready"
        },
        {
          draft_id: "close_input_draft",
          label: "Close input draft",
          target_record: "rehearsal_close_record",
          required_fields: ["session_id", "close_decision", "close_reason", "close_time", "close_price", "close_quantity", "realized_result", "owner_action", "timestamp"],
          optional_fields: ["symbol_or_contract", "manual_broker_confirmation", "commission_or_fee_optional", "owner_note"],
          status: "ready"
        },
        {
          draft_id: "final_review_input_draft",
          label: "Final review input draft",
          target_record: "rehearsal_final_review_record",
          required_fields: ["session_id", "realized_result_summary", "setup_quality_review", "entry_quality_review", "exit_quality_review", "risk_management_review", "rule_violation_review", "lesson_record", "owner_final_notes", "owner_action", "timestamp"],
          optional_fields: ["discipline_score_placeholder", "confidence_label", "freshness_label", "owner_note"],
          status: "ready"
        }
      ],
      validation_rules: [
        {
          rule_id: "required_field_gate",
          label: "Required field gate",
          purpose: "Submit remains blocked until all required fields for the target record are present.",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "owner_step_up_required",
          label: "Owner step-up required",
          purpose: "Future persistence submit requires Tower owner step-up confirmation.",
          severity: "blocking",
          status: "placeholder"
        },
        {
          rule_id: "sensitive_field_lock",
          label: "Sensitive field lock",
          purpose: "Owner-only and restricted fields remain hidden from beta users.",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "session_id_required",
          label: "Session ID required",
          purpose: "Every draft must link back to a rehearsal session.",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "no_real_broker_data",
          label: "No real broker data",
          purpose: "Input drafts must not claim broker API data or broker-read confirmation.",
          severity: "blocking",
          status: "locked"
        },
        {
          rule_id: "review_center_destination_required",
          label: "Review Center destination required",
          purpose: "Prepared records must point to Review Center rehearsal rollup destination.",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "vault_ready_no_upload",
          label: "Vault-ready, no upload",
          purpose: "Records may be Vault-ready but OB must not upload directly to Vault.",
          severity: "blocking",
          status: "locked"
        }
      ],
      autosave_contract: {
        autosave_id: "owner_rehearsal_input_autosave_placeholder",
        label: "Autosave Contract Placeholder",
        enabled_now: false,
        future_behavior: "Save owner draft locally/server-side only after persistence adapter is built.",
        draft_buffer: "owner_input_draft_session_buffer",
        save_frequency: "future_configurable",
        owner_visibility: "owner_only",
        beta_visibility: "none",
        no_database_write_now: true,
        no_file_write_now: true,
        status: "placeholder"
      },
      submit_gate_contract: {
        submit_gate_id: "owner_rehearsal_submit_gate_placeholder",
        label: "Submit Gate Placeholder",
        enabled_now: false,
        future_behavior: "Validate fields, require Tower step-up, then write to future rehearsal record persistence adapter.",
        required_gate_states: [
          "all_required_fields_present",
          "owner_step_up_confirmed",
          "session_id_valid",
          "target_record_contract_valid",
          "sensitivity_allowed",
          "review_center_destination_present",
          "no_broker_api_claim",
          "no_direct_vault_upload"
        ],
        blocked_until: [
          "persistence_adapter_built",
          "Tower_step_up_wired",
          "owner_input_save_endpoint_created",
          "Review_Center_read_model_ready"
        ],
        status: "placeholder"
      },
      persistence_adapter_placeholder: {
        adapter_id: "ob_rehearsal_record_persistence_adapter_placeholder",
        label: "Persistence Adapter Placeholder",
        target: "future owner rehearsal record store",
        accepts: [
          "decision_input_draft",
          "preflight_input_draft",
          "checklist_input_draft",
          "fill_or_not_placed_input_draft",
          "close_input_draft",
          "final_review_input_draft"
        ],
        emits: [
          "rehearsal_session_record",
          "rehearsal_decision_record",
          "rehearsal_preflight_record",
          "rehearsal_checklist_record",
          "rehearsal_fill_record",
          "rehearsal_not_placed_record",
          "rehearsal_close_record",
          "rehearsal_final_review_record",
          "rehearsal_receipt_record"
        ],
        enabled_now: false,
        status: "placeholder"
      },
      owner_input_flow: [
        {
          step_id: "open_rehearsal_session",
          label: "Open rehearsal session",
          purpose: "Owner starts or resumes a fake/demo rehearsal.",
          status: "ready"
        },
        {
          step_id: "draft_owner_input",
          label: "Draft owner input",
          purpose: "Owner enters decision/preflight/checklist/fill/close/final review fields.",
          status: "ready"
        },
        {
          step_id: "validate_required_fields",
          label: "Validate required fields",
          purpose: "System validates the draft against GP012 record contract.",
          status: "ready"
        },
        {
          step_id: "block_sensitive_or_invalid",
          label: "Block sensitive/invalid drafts",
          purpose: "System blocks missing fields, sensitive visibility failures, broker claims, and direct Vault upload claims.",
          status: "ready"
        },
        {
          step_id: "request_tower_step_up",
          label: "Request Tower step-up",
          purpose: "Future submit requires Tower owner step-up.",
          status: "placeholder"
        },
        {
          step_id: "prepare_write_payload",
          label: "Prepare write payload",
          purpose: "System shapes future persistence payload without writing yet.",
          status: "ready"
        },
        {
          step_id: "handoff_to_review_center",
          label: "Handoff to Review Center",
          purpose: "Prepared payload maps back into Review Center command board.",
          status: "ready"
        }
      ],
      blocked_actions: [
        "write_rehearsal_database_now",
        "write_file_now",
        "create_save_endpoint_now",
        "store_real_broker_data",
        "read_broker_account",
        "submit_order_from_ob",
        "auto_execute",
        "upload_direct_to_vault",
        "show_owner_input_to_beta_user",
        "skip_required_field_gate",
        "skip_tower_step_up_later"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_input_prep_only: true,
        contract_only_no_database_write: true,
        no_file_write: true,
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
        tower_step_up_placeholder_only: true,
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
      prep_state: { ...(fallback.prep_state || {}), ...(safe.prep_state || {}) },
      input_draft_contracts: Array.isArray(safe.input_draft_contracts) ? safe.input_draft_contracts : fallback.input_draft_contracts,
      validation_rules: Array.isArray(safe.validation_rules) ? safe.validation_rules : fallback.validation_rules,
      autosave_contract: { ...(fallback.autosave_contract || {}), ...(safe.autosave_contract || {}) },
      submit_gate_contract: { ...(fallback.submit_gate_contract || {}), ...(safe.submit_gate_contract || {}) },
      persistence_adapter_placeholder: { ...(fallback.persistence_adapter_placeholder || {}), ...(safe.persistence_adapter_placeholder || {}) },
      owner_input_flow: Array.isArray(safe.owner_input_flow) ? safe.owner_input_flow : fallback.owner_input_flow,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        owner_input_prep_only: true,
        contract_only_no_database_write: true,
        no_file_write: true,
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
        tower_step_up_placeholder_only: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_OWNER_INPUT_PERSISTENCE_PREP_GP014 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      owner_input_persistence_prep_gp014: normalized,
      owner_input_prep_only: true,
      contract_only_no_database_write: true,
      no_file_write: true,
      no_broker_api: true,
      no_broker_read: true,
      no_order_submit: true,
      no_auto_execution: true,
      no_direct_vault_upload: true,
      tower_step_up_placeholder_only: true,
      live_auto_locked: true
    };
    window.dispatchEvent(new CustomEvent("obOwnerInputPersistencePrepUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchPrep() {
    prepState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      prepState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        prepState.status = "ready";
        prepState.source = normalized.source || "server";
        prepState.payload = normalized;
        prepState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        prepState.status = "guarded_fallback";
        prepState.source = "guarded_fallback";
        prepState.payload = fallback;
        prepState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      prepState.status = "error_fallback";
      prepState.source = "error_fallback";
      prepState.payload = fallback;
      prepState.fallbackActive = true;
      prepState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return prepState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("disabled") || text.includes("no ") || text.includes("placeholder")) return "red";
    if (text.includes("ready")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-owner-input-persistence-prep-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-owner-input-persistence-prep-row">
        <div class="ob-owner-input-persistence-prep-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.draft_id || item.rule_id || item.step_id, "Item")}</strong>
          <span>${safeText(item.status || item.target_record || item.severity || "prep", "prep")}</span>
        </div>
        <span>${safeText(item.purpose || item.future_behavior || item.action || "detail", "detail")}</span>
        <div class="ob-owner-input-persistence-prep-status ${tone(item.status || item.severity)}">${safeText(item.status || item.severity || "ready", "ready")}</div>
      </div>
    `;
  }

  function draftRow(item, index) {
    const required = Array.isArray(item.required_fields) ? item.required_fields.join(" · ") : "none";
    const optional = Array.isArray(item.optional_fields) ? item.optional_fields.join(" · ") : "none";
    return `
      <div class="ob-owner-input-persistence-prep-row">
        <div class="ob-owner-input-persistence-prep-dot">D</div>
        <div>
          <strong>${safeText(item.label, "Draft")}</strong>
          <span>${safeText(item.target_record, "record")}</span>
        </div>
        <span>
          Required: ${required}<br>
          Optional: ${optional}
        </span>
        <div class="ob-owner-input-persistence-prep-status green">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-owner-input-persistence-prep-row">
        <div class="ob-owner-input-persistence-prep-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP014 owner input persistence-prep boundaries.</span>
        <div class="ob-owner-input-persistence-prep-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = prepState.payload || buildFallbackPayload();
    const state = payload.prep_state || {};
    const drafts = Array.isArray(payload.input_draft_contracts) ? payload.input_draft_contracts : [];
    const validations = Array.isArray(payload.validation_rules) ? payload.validation_rules : [];
    const flow = Array.isArray(payload.owner_input_flow) ? payload.owner_input_flow : [];
    const autosave = payload.autosave_contract || {};
    const submit = payload.submit_gate_contract || {};
    const adapter = payload.persistence_adapter_placeholder || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-owner-input-persistence-prep-panel" id="obOwnerInputPersistencePrepPanel" data-ob-giant-pack-014="true">
        <div class="ob-owner-input-persistence-prep-head">
          <div>
            <div class="ob-label">OB Giant Pack 014 · Owner Input Persistence Prep</div>
            <div class="ob-owner-input-persistence-prep-title">Owner Input Write-Prep Layer</div>
            <div class="ob-owner-input-persistence-prep-subtitle">
              ${safeText(prepState.status, "booting")} · ${safeText(state.status, "write_prep_ready")} · no database write.
            </div>
          </div>
          <div class="ob-owner-input-persistence-prep-chip-row">
            <span class="ob-owner-input-persistence-prep-chip green">Input drafts</span>
            <span class="ob-owner-input-persistence-prep-chip gold">Validation gates</span>
            <span class="ob-owner-input-persistence-prep-chip red">No DB write</span>
            <span class="ob-owner-input-persistence-prep-chip red">No broker data</span>
          </div>
        </div>

        <div class="ob-owner-input-persistence-prep-stat-grid">
          ${card("Drafts", String(drafts.length))}
          ${card("Validation", String(validations.length))}
          ${card("Flow steps", String(flow.length))}
          ${card("Autosave", autosave.enabled_now ? "on" : "placeholder")}
          ${card("Submit", submit.enabled_now ? "on" : "blocked")}
        </div>

        <div class="ob-owner-input-persistence-prep-grid">
          <div>
            <div class="ob-owner-input-persistence-prep-card">
              <span>Purpose</span>
              <strong>Prepare owner-entered rehearsal inputs for future safe persistence, without writing yet.</strong>
              <div class="ob-owner-input-persistence-prep-callout">
                <strong>Prepares:</strong><br>
                Draft contracts, validation gates, autosave placeholder, submit gate placeholder, and persistence adapter placeholder.
              </div>
              <div class="ob-owner-input-persistence-prep-boundary">
                <strong>Boundary:</strong><br>
                No database write. No file write. No save endpoint. No broker data. No order submit. No Vault upload.
              </div>
            </div>

            <div class="ob-owner-input-persistence-prep-card" style="margin-top: 11px;">
              <span>Autosave contract</span>
              <strong>${safeText(autosave.label, "Autosave Contract Placeholder")}</strong>
              <div class="ob-owner-input-persistence-prep-callout">
                Enabled now: ${autosave.enabled_now ? "yes" : "no"} · Buffer: ${safeText(autosave.draft_buffer, "placeholder")}
              </div>
            </div>

            <div class="ob-owner-input-persistence-prep-card" style="margin-top: 11px;">
              <span>Submit gate</span>
              <strong>${safeText(submit.label, "Submit Gate Placeholder")}</strong>
              <div class="ob-owner-input-persistence-prep-callout">
                Required gates: ${(submit.required_gate_states || []).join(" · ")}
              </div>
            </div>

            <div class="ob-owner-input-persistence-prep-card" style="margin-top: 11px;">
              <span>Persistence adapter</span>
              <strong>${safeText(adapter.label, "Persistence Adapter Placeholder")}</strong>
              <div class="ob-owner-input-persistence-prep-callout">
                Enabled now: ${adapter.enabled_now ? "yes" : "no"} · Target: ${safeText(adapter.target, "future store")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-owner-input-persistence-prep-section">
              <div class="ob-owner-input-persistence-prep-section-title">Owner input draft contracts</div>
              <div class="ob-owner-input-persistence-prep-list">${drafts.map(draftRow).join("")}</div>
            </div>

            <div class="ob-owner-input-persistence-prep-section">
              <div class="ob-owner-input-persistence-prep-section-title">Validation rules</div>
              <div class="ob-owner-input-persistence-prep-list">${validations.map((item, index) => row(item, index, "V")).join("")}</div>
            </div>

            <div class="ob-owner-input-persistence-prep-section">
              <div class="ob-owner-input-persistence-prep-section-title">Owner input flow</div>
              <div class="ob-owner-input-persistence-prep-list">${flow.map((item, index) => row(item, index, "F")).join("")}</div>
            </div>

            <div class="ob-owner-input-persistence-prep-section">
              <div class="ob-owner-input-persistence-prep-section-title">Blocked actions</div>
              <div class="ob-owner-input-persistence-prep-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-owner-input-persistence-prep-callout">
          <strong>Next handoff:</strong><br>
          GP015 can add Mission Account Capital Rule Rehearsal Overlay using these owner input gates.
        </div>

        <div class="ob-owner-input-persistence-prep-boundary">
          <strong>Still locked:</strong><br>
          No database write. No file write. No real broker data. No broker API. No order submit. No public proof. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obOwnerInputPersistencePrepPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const commandBoardPanel = document.getElementById("obReviewCenterRehearsalCommandBoardPanel");
    const contractsPanel = document.getElementById("obRehearsalRecordContractsPanel");
    const rehearsalPanel = document.getElementById("obOwnerRehearsalEnginePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (commandBoardPanel && commandBoardPanel.parentNode) commandBoardPanel.insertAdjacentElement("afterend", panel);
    else if (contractsPanel && contractsPanel.parentNode) contractsPanel.insertAdjacentElement("afterend", panel);
    else if (rehearsalPanel && rehearsalPanel.parentNode) rehearsalPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = prepState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-014-owner-input-persistence-prep", "ready");
    document.body.setAttribute("data-ob-owner-input-prep-only", "true");
    document.body.setAttribute("data-ob-contract-only-no-database-write", "true");
    document.body.setAttribute("data-ob-no-file-write", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-tower-step-up-placeholder-only", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_014_OWNER_INPUT_PERSISTENCE_PREP_STATE = {
      version: VERSION,
      status: prepState.status,
      fallbackActive: prepState.fallbackActive,
      draftContractCount: payload.input_draft_contracts.length,
      validationRuleCount: payload.validation_rules.length,
      ownerInputPrepOnly: true,
      contractOnlyNoDatabaseWrite: true,
      noFileWrite: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      noDirectVaultUpload: true,
      towerStepUpPlaceholderOnly: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchPrep();
    }, 4940);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_OWNER_INPUT_PERSISTENCE_PREP_GP014_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return prepState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchPrep,
    renderPanel,
    setFlags
  };
})();
