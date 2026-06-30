// OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_WIRING_PREP_JS

(function () {
  const VERSION = "OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_WIRING_PREP";
  const ENDPOINT = "/ob/tower-step-up-enforcement-prep.json";

  // SMOKE MARKERS
  // Tower Step-Up Enforcement Wiring Prep
  // Tower owns step-up approval
  // OB requests step-up only
  // owner step-up request contract
  // step-up session placeholder
  // Tower approval receipt placeholder
  // capital override gate placeholder
  // blocked reason acknowledgement
  // Tower clearance state
  // owner re-auth placeholder
  // step-up expiration placeholder
  // step-up revocation placeholder
  // approval scope contract
  // override remains disabled
  // submit gate remains disabled
  // no active auth change
  // no Tower file modification
  // no database write
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no direct Vault upload
  // Live Auto Locked

  let stepUpState = {
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
      source: "ob_giant_pack_016_safe_fallback",
      prep_state: {
        prep_id: "ob_tower_step_up_enforcement_prep_001",
        label: "Tower Step-Up Enforcement Wiring Prep",
        status: "step_up_wiring_prep_ready",
        purpose: "Prepare OB to request future Tower step-up for owner overrides, capital blocks, and Manual Live rehearsal submits.",
        owner_only: true,
        tower_owns_approval: true,
        ob_requests_only: true,
        no_active_auth_change: true,
        no_tower_file_modification: true,
        no_database_write: true,
        no_broker_data: true,
        capital_overlay_source: "/ob/mission-account-capital-rule-rehearsal-overlay.json",
        owner_input_prep_source: "/ob/owner-input-persistence-prep.json",
        tower_source_of_truth: "Tower"
      },
      step_up_request_contract: {
        contract_id: "tower_step_up_request_contract_001",
        label: "Owner Step-Up Request Contract",
        purpose: "Shape future OB requests to Tower when owner wants to proceed through a guarded action.",
        required_fields: [
          "step_up_request_id",
          "source_app",
          "requesting_room",
          "actor",
          "actor_role",
          "business_lane",
          "mission_account",
          "requested_action",
          "blocked_reason",
          "severity",
          "linked_policy",
          "linked_rehearsal_session",
          "linked_receipts",
          "linked_packet",
          "owner_acknowledgement_required",
          "tower_clearance_required",
          "expires_at",
          "revocation_status"
        ],
        status: "ready"
      },
      step_up_session_placeholder: {
        session_id: "tower_step_up_session_placeholder_001",
        label: "Step-Up Session Placeholder",
        enabled_now: false,
        future_behavior: "Tower creates/verifies step-up session and returns clearance state to OB.",
        status_values: ["not_requested", "requested", "pending_owner_step_up", "approved", "denied", "expired", "revoked"],
        timeout_policy: "future_tower_policy",
        owner_reauth_required: true,
        status: "placeholder"
      },
      tower_approval_receipt_placeholder: {
        receipt_id: "tower_approval_receipt_placeholder_001",
        label: "Tower Approval Receipt Placeholder",
        enabled_now: false,
        future_receipt_fields: [
          "receipt_id",
          "timestamp",
          "source_app",
          "actor",
          "approved_action",
          "scope",
          "expiration",
          "linked_policy",
          "linked_block_reason",
          "linked_rehearsal_session",
          "revocation_status",
          "vault_ready"
        ],
        no_direct_vault_upload: true,
        status: "placeholder"
      },
      enforcement_gates: [
        {
          gate_id: "capital_override_step_up_gate",
          label: "Capital override step-up gate",
          purpose: "Future owner override of capital block requires Tower step-up approval receipt.",
          source_block_reasons: ["atm_reserve_boundary_at_risk", "apartment_reserve_boundary_at_risk", "trust_capital_requires_review", "protected_floor_would_be_breached", "deployment_limit_exceeded"],
          required_clearance: "owner_step_up_plus_tower_approval_receipt",
          enabled_now: false,
          status: "locked"
        },
        {
          gate_id: "owner_input_submit_step_up_gate",
          label: "Owner input submit step-up gate",
          purpose: "Future write submit requires Tower step-up and valid owner input draft.",
          source_block_reasons: ["owner_step_up_required", "required_field_gate", "sensitive_field_lock"],
          required_clearance: "owner_step_up_before_persistence_write",
          enabled_now: false,
          status: "locked"
        },
        {
          gate_id: "manual_live_real_activation_gate",
          label: "Manual Live real activation gate",
          purpose: "Real Manual Live remains locked until Tower clearance and readiness conditions are satisfied.",
          source_block_reasons: ["manual_live_real_not_active", "rehearsal_only_mode", "capital_rules_not_live"],
          required_clearance: "future_manual_live_owner_clearance",
          enabled_now: false,
          status: "locked"
        },
        {
          gate_id: "hybrid_automated_gate",
          label: "Hybrid / Automated gate",
          purpose: "Hybrid and Automated remain locked behind future Tower policy.",
          source_block_reasons: ["hybrid_locked", "automated_locked", "live_auto_locked"],
          required_clearance: "future_high_risk_tower_clearance",
          enabled_now: false,
          status: "locked"
        }
      ],
      blocked_reason_acknowledgement_contract: {
        acknowledgement_id: "blocked_reason_acknowledgement_contract_001",
        label: "Blocked Reason Acknowledgement Contract",
        purpose: "Owner must acknowledge why a request is blocked before future step-up can proceed.",
        required_fields: [
          "acknowledgement_id",
          "blocked_reason",
          "blocking_app",
          "severity",
          "owner_acknowledged",
          "acknowledged_at",
          "linked_policy",
          "linked_account",
          "linked_rehearsal_session",
          "next_allowed_action"
        ],
        enabled_now: false,
        status: "placeholder"
      },
      approval_scope_contract: {
        scope_id: "tower_approval_scope_contract_001",
        label: "Approval Scope Contract",
        purpose: "Future Tower approval must be scoped and expiring, not a permanent blank check.",
        scopes: [
          "single_rehearsal_submit",
          "single_capital_override_review",
          "single_manual_live_owner_action",
          "single_receipt_confirmation",
          "readiness_checkpoint_only"
        ],
        required_limits: [
          "scope",
          "expiration",
          "linked_action",
          "linked_policy",
          "linked_receipt",
          "revocation_status"
        ],
        status: "ready"
      },
      tower_clearance_states: [
        {
          state_id: "not_requested",
          label: "Not requested",
          meaning: "OB has not requested Tower step-up.",
          owner_next_action: "Resolve normal requirements first.",
          status: "ready"
        },
        {
          state_id: "requested",
          label: "Requested",
          meaning: "OB has shaped a future step-up request.",
          owner_next_action: "Tower must own approval.",
          status: "placeholder"
        },
        {
          state_id: "pending_owner_step_up",
          label: "Pending owner step-up",
          meaning: "Owner must complete future Tower verification.",
          owner_next_action: "Complete Tower step-up when wired.",
          status: "placeholder"
        },
        {
          state_id: "approved",
          label: "Approved",
          meaning: "Tower approves a scoped action with expiration.",
          owner_next_action: "Proceed only within scope.",
          status: "placeholder"
        },
        {
          state_id: "denied",
          label: "Denied",
          meaning: "Tower denies requested action.",
          owner_next_action: "Do not proceed.",
          status: "placeholder"
        },
        {
          state_id: "expired",
          label: "Expired",
          meaning: "Approval expired.",
          owner_next_action: "Request new step-up if still needed.",
          status: "placeholder"
        },
        {
          state_id: "revoked",
          label: "Revoked",
          meaning: "Tower revoked approval.",
          owner_next_action: "Stop action and create review receipt.",
          status: "placeholder"
        }
      ],
      step_up_flow_prep: [
        {
          step_id: "detect_blocked_action",
          label: "Detect blocked action",
          purpose: "OB sees capital rule, owner input, or Manual Live gate block.",
          status: "ready"
        },
        {
          step_id: "shape_step_up_request",
          label: "Shape step-up request",
          purpose: "OB builds future Tower request payload without submitting it.",
          status: "ready"
        },
        {
          step_id: "require_block_reason_acknowledgement",
          label: "Require blocked reason acknowledgement",
          purpose: "Owner must understand why the request is blocked.",
          status: "ready"
        },
        {
          step_id: "handoff_to_tower",
          label: "Handoff to Tower",
          purpose: "Future Tower route/session handles actual verification.",
          status: "placeholder"
        },
        {
          step_id: "receive_clearance_state",
          label: "Receive clearance state",
          purpose: "OB will later receive approved/denied/expired/revoked status.",
          status: "placeholder"
        },
        {
          step_id: "enforce_scope_expiration",
          label: "Enforce scope and expiration",
          purpose: "Future approval applies only to exact scoped action.",
          status: "placeholder"
        },
        {
          step_id: "write_approval_receipt_placeholder",
          label: "Write approval receipt placeholder",
          purpose: "Future Tower receipt becomes Vault-ready without OB direct upload.",
          status: "placeholder"
        }
      ],
      blocked_actions: [
        "approve_step_up_inside_ob",
        "change_tower_permission_inside_ob",
        "create_active_auth_session_now",
        "write_tower_receipt_now",
        "write_rehearsal_database_now",
        "override_capital_rule_now",
        "submit_owner_input_now",
        "submit_order_from_ob",
        "read_broker_account",
        "auto_execute",
        "upload_direct_to_vault",
        "show_step_up_controls_to_beta_user",
        "make_approval_permanent"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        tower_step_up_wiring_prep_only: true,
        tower_owns_approval: true,
        ob_requests_only: true,
        no_active_auth_change: true,
        no_tower_file_modification: true,
        no_permission_mutation: true,
        no_database_write: true,
        no_file_write: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        owner_override_placeholder_only: true,
        submit_gate_placeholder_only: true,
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
      prep_state: { ...(fallback.prep_state || {}), ...(safe.prep_state || {}) },
      step_up_request_contract: { ...(fallback.step_up_request_contract || {}), ...(safe.step_up_request_contract || {}) },
      step_up_session_placeholder: { ...(fallback.step_up_session_placeholder || {}), ...(safe.step_up_session_placeholder || {}) },
      tower_approval_receipt_placeholder: { ...(fallback.tower_approval_receipt_placeholder || {}), ...(safe.tower_approval_receipt_placeholder || {}) },
      enforcement_gates: Array.isArray(safe.enforcement_gates) ? safe.enforcement_gates : fallback.enforcement_gates,
      blocked_reason_acknowledgement_contract: { ...(fallback.blocked_reason_acknowledgement_contract || {}), ...(safe.blocked_reason_acknowledgement_contract || {}) },
      approval_scope_contract: { ...(fallback.approval_scope_contract || {}), ...(safe.approval_scope_contract || {}) },
      tower_clearance_states: Array.isArray(safe.tower_clearance_states) ? safe.tower_clearance_states : fallback.tower_clearance_states,
      step_up_flow_prep: Array.isArray(safe.step_up_flow_prep) ? safe.step_up_flow_prep : fallback.step_up_flow_prep,
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        tower_step_up_wiring_prep_only: true,
        tower_owns_approval: true,
        ob_requests_only: true,
        no_active_auth_change: true,
        no_tower_file_modification: true,
        no_permission_mutation: true,
        no_database_write: true,
        no_file_write: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
        no_broker_api: true,
        no_broker_read: true,
        no_order_submit: true,
        no_auto_close: true,
        no_auto_execution: true,
        no_direct_vault_upload: true,
        owner_override_placeholder_only: true,
        submit_gate_placeholder_only: true,
        manual_live_real_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_TOWER_STEP_UP_ENFORCEMENT_PREP_GP016 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      tower_step_up_enforcement_prep_gp016: normalized,
      towerStepUpWiringPrepOnly: true,
      towerOwnsApproval: true,
      obRequestsOnly: true,
      noActiveAuthChange: true,
      noTowerFileModification: true,
      noPermissionMutation: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obTowerStepUpEnforcementPrepUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchStepUp() {
    stepUpState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      stepUpState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        stepUpState.status = "ready";
        stepUpState.source = normalized.source || "server";
        stepUpState.payload = normalized;
        stepUpState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        stepUpState.status = "guarded_fallback";
        stepUpState.source = "guarded_fallback";
        stepUpState.payload = fallback;
        stepUpState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      stepUpState.status = "error_fallback";
      stepUpState.source = "error_fallback";
      stepUpState.payload = fallback;
      stepUpState.fallbackActive = true;
      stepUpState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return stepUpState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("placeholder") || text.includes("denied") || text.includes("expired") || text.includes("revoked")) return "red";
    if (text.includes("ready") || text.includes("approved")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-tower-step-up-prep-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-tower-step-up-prep-row">
        <div class="ob-tower-step-up-prep-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.gate_id || item.state_id || item.step_id, "Item")}</strong>
          <span>${safeText(item.status || item.required_clearance || item.state_id || "step-up", "step-up")}</span>
        </div>
        <span>${safeText(item.purpose || item.meaning || item.owner_next_action || "detail", "detail")}</span>
        <div class="ob-tower-step-up-prep-status ${tone(item.status)}">${safeText(item.status, "ready")}</div>
      </div>
    `;
  }

  function fieldRows(fields, label) {
    return (fields || []).map((field) => `
      <div class="ob-tower-step-up-prep-row">
        <div class="ob-tower-step-up-prep-dot">F</div>
        <div>
          <strong>${safeText(field, "field")}</strong>
          <span>${label || "required field"}</span>
        </div>
        <span>Required for future Tower step-up enforcement wiring.</span>
        <div class="ob-tower-step-up-prep-status gold">required</div>
      </div>
    `).join("");
  }

  function blockedRow(item) {
    return `
      <div class="ob-tower-step-up-prep-row">
        <div class="ob-tower-step-up-prep-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP016 Tower step-up wiring-prep boundaries.</span>
        <div class="ob-tower-step-up-prep-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = stepUpState.payload || buildFallbackPayload();
    const state = payload.prep_state || {};
    const request = payload.step_up_request_contract || {};
    const session = payload.step_up_session_placeholder || {};
    const receipt = payload.tower_approval_receipt_placeholder || {};
    const gates = Array.isArray(payload.enforcement_gates) ? payload.enforcement_gates : [];
    const acknowledgement = payload.blocked_reason_acknowledgement_contract || {};
    const scope = payload.approval_scope_contract || {};
    const states = Array.isArray(payload.tower_clearance_states) ? payload.tower_clearance_states : [];
    const flow = Array.isArray(payload.step_up_flow_prep) ? payload.step_up_flow_prep : [];
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-tower-step-up-prep-panel" id="obTowerStepUpEnforcementPrepPanel" data-ob-giant-pack-016="true">
        <div class="ob-tower-step-up-prep-head">
          <div>
            <div class="ob-label">OB Giant Pack 016 · Tower Step-Up Enforcement Prep</div>
            <div class="ob-tower-step-up-prep-title">Tower Step-Up Wiring Prep</div>
            <div class="ob-tower-step-up-prep-subtitle">
              ${safeText(stepUpState.status, "booting")} · ${safeText(state.status, "step_up_wiring_prep_ready")} · OB requests only, Tower approves.
            </div>
          </div>
          <div class="ob-tower-step-up-prep-chip-row">
            <span class="ob-tower-step-up-prep-chip green">Request contract</span>
            <span class="ob-tower-step-up-prep-chip gold">Tower owns approval</span>
            <span class="ob-tower-step-up-prep-chip red">No auth change</span>
            <span class="ob-tower-step-up-prep-chip red">No permission mutation</span>
          </div>
        </div>

        <div class="ob-tower-step-up-prep-stat-grid">
          ${card("Gates", String(gates.length))}
          ${card("States", String(states.length))}
          ${card("Flow", String(flow.length))}
          ${card("Session", session.enabled_now ? "on" : "placeholder")}
          ${card("Override", "disabled")}
        </div>

        <div class="ob-tower-step-up-prep-grid">
          <div>
            <div class="ob-tower-step-up-prep-card">
              <span>Purpose</span>
              <strong>Prepare OB to ask Tower for future owner step-up without allowing OB to approve, mutate permissions, or bypass gates.</strong>
              <div class="ob-tower-step-up-prep-callout">
                <strong>Core rule:</strong><br>
                The Tower approves. OB only requests, displays blocked reasons, and enforces returned clearance state.
              </div>
              <div class="ob-tower-step-up-prep-boundary">
                <strong>Boundary:</strong><br>
                No active auth change. No Tower file modification. No permission mutation. No database write. No broker action.
              </div>
            </div>

            <div class="ob-tower-step-up-prep-card" style="margin-top: 11px;">
              <span>Step-up request contract</span>
              <strong>${safeText(request.label, "Owner Step-Up Request Contract")}</strong>
              <div class="ob-tower-step-up-prep-list">${fieldRows(request.required_fields || [], "request field")}</div>
            </div>

            <div class="ob-tower-step-up-prep-card" style="margin-top: 11px;">
              <span>Approval receipt placeholder</span>
              <strong>${safeText(receipt.label, "Tower Approval Receipt Placeholder")}</strong>
              <div class="ob-tower-step-up-prep-callout">
                Enabled now: ${receipt.enabled_now ? "yes" : "no"} · No direct Vault upload: ${receipt.no_direct_vault_upload ? "true" : "false"}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Enforcement gates</div>
              <div class="ob-tower-step-up-prep-list">${gates.map((item, index) => row(item, index, "G")).join("")}</div>
            </div>

            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Tower clearance states</div>
              <div class="ob-tower-step-up-prep-list">${states.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Step-up flow prep</div>
              <div class="ob-tower-step-up-prep-list">${flow.map((item, index) => row(item, index, "F")).join("")}</div>
            </div>

            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Blocked reason acknowledgement fields</div>
              <div class="ob-tower-step-up-prep-list">${fieldRows(acknowledgement.required_fields || [], "ack field")}</div>
            </div>

            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Approval scopes</div>
              <div class="ob-tower-step-up-prep-list">${fieldRows(scope.scopes || [], "approval scope")}</div>
            </div>

            <div class="ob-tower-step-up-prep-section">
              <div class="ob-tower-step-up-prep-section-title">Blocked actions</div>
              <div class="ob-tower-step-up-prep-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-tower-step-up-prep-callout">
          <strong>Next handoff:</strong><br>
          GP017 can connect real candidate adapter data into the rehearsal path while these Tower step-up gates stay locked.
        </div>

        <div class="ob-tower-step-up-prep-boundary">
          <strong>Still locked:</strong><br>
          No active auth change. No Tower permission mutation. No database write. No broker API. No order submit. No direct Vault upload. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obTowerStepUpEnforcementPrepPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const capitalPanel = document.getElementById("obMissionAccountCapitalRuleRehearsalOverlayPanel");
    const ownerInputPanel = document.getElementById("obOwnerInputPersistencePrepPanel");
    const commandBoardPanel = document.getElementById("obReviewCenterRehearsalCommandBoardPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (capitalPanel && capitalPanel.parentNode) capitalPanel.insertAdjacentElement("afterend", panel);
    else if (ownerInputPanel && ownerInputPanel.parentNode) ownerInputPanel.insertAdjacentElement("afterend", panel);
    else if (commandBoardPanel && commandBoardPanel.parentNode) commandBoardPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = stepUpState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-016-tower-step-up-prep", "ready");
    document.body.setAttribute("data-ob-tower-step-up-wiring-prep-only", "true");
    document.body.setAttribute("data-ob-tower-owns-approval", "true");
    document.body.setAttribute("data-ob-requests-only", "true");
    document.body.setAttribute("data-ob-no-active-auth-change", "true");
    document.body.setAttribute("data-ob-no-tower-file-modification", "true");
    document.body.setAttribute("data-ob-no-permission-mutation", "true");
    document.body.setAttribute("data-ob-no-database-write", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_016_TOWER_STEP_UP_ENFORCEMENT_PREP_STATE = {
      version: VERSION,
      status: stepUpState.status,
      fallbackActive: stepUpState.fallbackActive,
      gateCount: payload.enforcement_gates.length,
      clearanceStateCount: payload.tower_clearance_states.length,
      flowStepCount: payload.step_up_flow_prep.length,
      towerStepUpWiringPrepOnly: true,
      towerOwnsApproval: true,
      obRequestsOnly: true,
      noActiveAuthChange: true,
      noTowerFileModification: true,
      noPermissionMutation: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchStepUp();
    }, 5260);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_TOWER_STEP_UP_ENFORCEMENT_PREP_GP016_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return stepUpState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchStepUp,
    renderPanel,
    setFlags
  };
})();
