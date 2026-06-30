// OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_JS

(function () {
  const VERSION = "OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY";
  const ENDPOINT = "/ob/mission-account-capital-rule-rehearsal-overlay.json";

  // SMOKE MARKERS
  // Mission Account Capital Rule Rehearsal Overlay
  // mission account fit
  // protected floor
  // deployment limit
  // ATM reserve boundary
  // apartment reserve boundary
  // trust capital boundary
  // proof demo boundary
  // owner override placeholder
  // Tower block reason
  // capital rule rehearsal
  // capital deployment lock
  // account purpose enforcement
  // mission account allowed modes
  // manual live capital check
  // rehearsal-only capital check
  // no real capital movement
  // no bank integration
  // no broker API
  // no broker read
  // no order submit
  // no auto execution
  // no database write
  // no direct Vault upload
  // Live Auto Locked

  let overlayState = {
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
      source: "ob_giant_pack_015_safe_fallback",
      overlay_state: {
        overlay_id: "ob_mission_account_capital_rule_rehearsal_overlay_001",
        label: "Mission Account Capital Rule Rehearsal Overlay",
        status: "capital_rehearsal_overlay_ready",
        purpose: "Apply owner-side mission account capital rules to rehearsal mode before real Manual Live.",
        owner_only: true,
        rehearsal_only: true,
        no_real_capital_movement: true,
        no_database_write: true,
        no_broker_data: true,
        account_source: "/ob/account-experience.json",
        input_prep_source: "/ob/owner-input-persistence-prep.json",
        tower_capital_safety_source: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      mission_account_capital_profiles: [
        {
          account_id: "trust_ob_account",
          label: "Trust OB Account",
          purpose: "Protect trust capital and long-term mission foundation.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "trust_protected_floor_placeholder",
          deployment_limit_rule: "trust_deployment_limit_placeholder",
          reserve_boundary: "trust_capital_boundary",
          default_decision: "review_required",
          status: "guarded"
        },
        {
          account_id: "personal_ob_account",
          label: "Personal OB Account",
          purpose: "Owner personal capital testing lane with strict Manual Live rehearsal checks.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "personal_protected_floor_placeholder",
          deployment_limit_rule: "personal_deployment_limit_placeholder",
          reserve_boundary: "personal_capital_boundary",
          default_decision: "review_required",
          status: "guarded"
        },
        {
          account_id: "simplee_world_ob_account",
          label: "Simplee World OB Account",
          purpose: "Business parent capital lane; protected from casual trade deployment.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "business_parent_protected_floor_placeholder",
          deployment_limit_rule: "business_parent_deployment_limit_placeholder",
          reserve_boundary: "business_parent_boundary",
          default_decision: "tower_review_required",
          status: "guarded"
        },
        {
          account_id: "atm_ob_account",
          label: "SimpleeOnTheGo / ATM OB Account",
          purpose: "ATM route acquisition capital lane; reserve boundary protects ATM deployment funds.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "atm_route_capital_floor_placeholder",
          deployment_limit_rule: "atm_trade_deployment_limit_placeholder",
          reserve_boundary: "ATM reserve boundary",
          default_decision: "block_if_reserve_at_risk",
          status: "guarded"
        },
        {
          account_id: "apartment_ob_account",
          label: "SimpleeProperty / Apartment OB Account",
          purpose: "Apartment/lender packet capital lane; reserve boundary protects apartment acquisition funds.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "apartment_capital_floor_placeholder",
          deployment_limit_rule: "apartment_trade_deployment_limit_placeholder",
          reserve_boundary: "apartment reserve boundary",
          default_decision: "block_if_reserve_at_risk",
          status: "guarded"
        },
        {
          account_id: "proof_demo_ob_account",
          label: "Proof/Demo OB Account",
          purpose: "Safe rehearsal and proof lane using fake/demo capital assumptions only.",
          allowed_modes: ["survey", "paper", "owner_rehearsal"],
          manual_live_rehearsal_allowed: true,
          real_manual_live_allowed_now: false,
          protected_floor_rule: "demo_floor_placeholder",
          deployment_limit_rule: "demo_limit_placeholder",
          reserve_boundary: "proof_demo_boundary",
          default_decision: "safe_for_rehearsal",
          status: "ready"
        }
      ],
      capital_rule_checks: [
        {
          rule_id: "mission_account_fit",
          label: "Mission account fit",
          purpose: "Candidate must fit the selected mission account purpose before checklist rehearsal.",
          block_reason: "candidate_does_not_fit_mission_account",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "protected_floor",
          label: "Protected floor",
          purpose: "Rehearsal must show whether hypothetical trade would break protected floor.",
          block_reason: "protected_floor_would_be_breached",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "deployment_limit",
          label: "Deployment limit",
          purpose: "Rehearsal must show whether hypothetical trade exceeds allowed deployment amount.",
          block_reason: "deployment_limit_exceeded",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "atm_reserve_boundary",
          label: "ATM reserve boundary",
          purpose: "ATM route capital cannot be rehearsed as casually deployable trade capital.",
          block_reason: "atm_reserve_boundary_at_risk",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "apartment_reserve_boundary",
          label: "Apartment reserve boundary",
          purpose: "Apartment acquisition capital cannot be rehearsed as casually deployable trade capital.",
          block_reason: "apartment_reserve_boundary_at_risk",
          severity: "blocking",
          status: "ready"
        },
        {
          rule_id: "trust_capital_boundary",
          label: "Trust capital boundary",
          purpose: "Trust capital requires guarded review and owner/Tower approval placeholder.",
          block_reason: "trust_capital_requires_review",
          severity: "review_required",
          status: "ready"
        },
        {
          rule_id: "proof_demo_boundary",
          label: "Proof/Demo boundary",
          purpose: "Proof/Demo account is safe for rehearsal and should not imply real money movement.",
          block_reason: "demo_only_not_real_money",
          severity: "info",
          status: "ready"
        },
        {
          rule_id: "owner_override_placeholder",
          label: "Owner override placeholder",
          purpose: "Future override requires owner step-up, Tower receipt, and blocked reason acknowledgement.",
          block_reason: "owner_override_not_wired_yet",
          severity: "locked",
          status: "placeholder"
        },
        {
          rule_id: "tower_block_reason_required",
          label: "Tower block reason required",
          purpose: "Every capital block must expose a clear Tower-style blocked reason.",
          block_reason: "missing_tower_block_reason",
          severity: "blocking",
          status: "ready"
        }
      ],
      rehearsal_capital_scenarios: [
        {
          scenario_id: "demo_safe_proof_account",
          label: "Proof/Demo safe rehearsal",
          account_id: "proof_demo_ob_account",
          candidate_id: "demo_mu_call_rehearsal_001",
          hypothetical_trade_risk: "demo_only",
          capital_fit: "fits_rehearsal",
          protected_floor_result: "not_applicable_demo",
          deployment_limit_result: "within_demo_limit",
          tower_block_reason: "none",
          owner_next_action: "Continue rehearsal.",
          status: "allowed_for_rehearsal"
        },
        {
          scenario_id: "atm_reserve_at_risk",
          label: "ATM reserve at risk",
          account_id: "atm_ob_account",
          candidate_id: "demo_mu_call_rehearsal_001",
          hypothetical_trade_risk: "would_touch_reserved_atm_capital",
          capital_fit: "does_not_fit_account_purpose",
          protected_floor_result: "reserve_floor_at_risk",
          deployment_limit_result: "blocked",
          tower_block_reason: "atm_reserve_boundary_at_risk",
          owner_next_action: "Use Proof/Demo or different owner lane; do not rehearse ATM deployment as casual trade capital.",
          status: "blocked"
        },
        {
          scenario_id: "apartment_reserve_at_risk",
          label: "Apartment reserve at risk",
          account_id: "apartment_ob_account",
          candidate_id: "demo_amd_stock_rehearsal_002",
          hypothetical_trade_risk: "would_touch_apartment_acquisition_reserve",
          capital_fit: "does_not_fit_account_purpose",
          protected_floor_result: "acquisition_floor_at_risk",
          deployment_limit_result: "blocked",
          tower_block_reason: "apartment_reserve_boundary_at_risk",
          owner_next_action: "Keep apartment acquisition capital protected.",
          status: "blocked"
        },
        {
          scenario_id: "trust_review_required",
          label: "Trust capital review required",
          account_id: "trust_ob_account",
          candidate_id: "demo_reject_bad_spread_003",
          hypothetical_trade_risk: "trust_capital_needs_review",
          capital_fit: "review_required",
          protected_floor_result: "unknown_until_owner_review",
          deployment_limit_result: "requires_tower_review",
          tower_block_reason: "trust_capital_requires_review",
          owner_next_action: "Do not proceed without future owner step-up and Tower receipt.",
          status: "review_required"
        }
      ],
      capital_block_reason_contract: {
        blocked_reason_id: "capital_rule_block_reason_contract_001",
        required_fields: [
          "blocked_reason",
          "blocking_app",
          "severity",
          "required_action",
          "linked_policy",
          "owner_can_override",
          "tower_clearance_required",
          "linked_account",
          "linked_rehearsal_session"
        ],
        allowed_severity: ["info", "watch", "needs_review", "blocking", "critical", "locked"],
        owner_override_allowed_now: false,
        tower_clearance_required: true,
        status: "ready"
      },
      owner_override_contract: {
        override_id: "capital_rule_owner_override_placeholder_001",
        enabled_now: false,
        future_requirements: [
          "owner_step_up",
          "Tower approval receipt",
          "blocked reason acknowledgement",
          "capital rule linked policy",
          "Review Center note",
          "Vault-ready receipt placeholder"
        ],
        status: "placeholder"
      },
      blocked_actions: [
        "move_real_capital",
        "change_real_account_balance",
        "read_bank_account",
        "read_broker_account",
        "submit_order_from_ob",
        "auto_execute",
        "override_capital_rule_now",
        "use_atm_reserve_as_trade_capital",
        "use_apartment_reserve_as_trade_capital",
        "upload_direct_to_vault",
        "write_database_now",
        "show_owner_capital_rules_to_beta_user"
      ],
      boundaries: {
        private_beta_only: true,
        owner_rehearsal_only: true,
        capital_rehearsal_overlay_only: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
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
        owner_override_placeholder_only: true,
        tower_block_reason_required: true,
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
      overlay_state: { ...(fallback.overlay_state || {}), ...(safe.overlay_state || {}) },
      mission_account_capital_profiles: Array.isArray(safe.mission_account_capital_profiles) ? safe.mission_account_capital_profiles : fallback.mission_account_capital_profiles,
      capital_rule_checks: Array.isArray(safe.capital_rule_checks) ? safe.capital_rule_checks : fallback.capital_rule_checks,
      rehearsal_capital_scenarios: Array.isArray(safe.rehearsal_capital_scenarios) ? safe.rehearsal_capital_scenarios : fallback.rehearsal_capital_scenarios,
      capital_block_reason_contract: { ...(fallback.capital_block_reason_contract || {}), ...(safe.capital_block_reason_contract || {}) },
      owner_override_contract: { ...(fallback.owner_override_contract || {}), ...(safe.owner_override_contract || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        owner_rehearsal_only: true,
        capital_rehearsal_overlay_only: true,
        no_real_capital_movement: true,
        no_bank_integration: true,
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
        owner_override_placeholder_only: true,
        tower_block_reason_required: true,
        hybrid_locked: true,
        automated_locked: true,
        live_auto_locked: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);
    window.OB_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_GP015 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      mission_account_capital_rule_rehearsal_overlay_gp015: normalized,
      capitalRehearsalOverlayOnly: true,
      noRealCapitalMovement: true,
      noBankIntegration: true,
      noBrokerApi: true,
      noBrokerRead: true,
      noOrderSubmit: true,
      noAutoExecution: true,
      ownerOverridePlaceholderOnly: true,
      towerBlockReasonRequired: true,
      liveAutoLocked: true
    };
    window.dispatchEvent(new CustomEvent("obMissionAccountCapitalRuleRehearsalOverlayUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchOverlay() {
    overlayState.status = "loading";
    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });
      overlayState.httpStatus = response.status;
      if (response.ok) {
        const normalized = expose(await response.json());
        overlayState.status = "ready";
        overlayState.source = normalized.source || "server";
        overlayState.payload = normalized;
        overlayState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        overlayState.status = "guarded_fallback";
        overlayState.source = "guarded_fallback";
        overlayState.payload = fallback;
        overlayState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      overlayState.status = "error_fallback";
      overlayState.source = "error_fallback";
      overlayState.payload = fallback;
      overlayState.fallbackActive = true;
      overlayState.error = error && error.message ? error.message : "Unknown fetch error";
    }
    renderPanel();
    setFlags();
    return overlayState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("locked") || text.includes("risk") || text.includes("placeholder")) return "red";
    if (text.includes("ready") || text.includes("allowed") || text.includes("safe")) return "green";
    return "gold";
  }

  function card(label, value) {
    return `<div class="ob-capital-rule-rehearsal-overlay-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function row(item, index, kind) {
    return `
      <div class="ob-capital-rule-rehearsal-overlay-row">
        <div class="ob-capital-rule-rehearsal-overlay-dot">${kind || index + 1}</div>
        <div>
          <strong>${safeText(item.label || item.rule_id || item.scenario_id || item.account_id, "Item")}</strong>
          <span>${safeText(item.status || item.severity || item.account_id || "capital", "capital")}</span>
        </div>
        <span>${safeText(item.purpose || item.owner_next_action || item.block_reason || item.reserve_boundary || "detail", "detail")}</span>
        <div class="ob-capital-rule-rehearsal-overlay-status ${tone(item.status || item.severity)}">${safeText(item.status || item.severity || "ready", "ready")}</div>
      </div>
    `;
  }

  function profileRow(item) {
    return `
      <div class="ob-capital-rule-rehearsal-overlay-row">
        <div class="ob-capital-rule-rehearsal-overlay-dot">A</div>
        <div>
          <strong>${safeText(item.label, "Account")}</strong>
          <span>${safeText(item.account_id, "account")}</span>
        </div>
        <span>
          Purpose: ${safeText(item.purpose, "purpose")}<br>
          Allowed modes: ${(item.allowed_modes || []).join(" · ")}<br>
          Protected floor: ${safeText(item.protected_floor_rule, "placeholder")}<br>
          Deployment limit: ${safeText(item.deployment_limit_rule, "placeholder")}<br>
          Reserve: ${safeText(item.reserve_boundary, "boundary")}
        </span>
        <div class="ob-capital-rule-rehearsal-overlay-status ${tone(item.status)}">${safeText(item.status, "guarded")}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-capital-rule-rehearsal-overlay-row">
        <div class="ob-capital-rule-rehearsal-overlay-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is blocked by GP015 capital rehearsal boundaries.</span>
        <div class="ob-capital-rule-rehearsal-overlay-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = overlayState.payload || buildFallbackPayload();
    const state = payload.overlay_state || {};
    const profiles = Array.isArray(payload.mission_account_capital_profiles) ? payload.mission_account_capital_profiles : [];
    const checks = Array.isArray(payload.capital_rule_checks) ? payload.capital_rule_checks : [];
    const scenarios = Array.isArray(payload.rehearsal_capital_scenarios) ? payload.rehearsal_capital_scenarios : [];
    const blockContract = payload.capital_block_reason_contract || {};
    const overrideContract = payload.owner_override_contract || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];

    return `
      <div class="ob-capital-rule-rehearsal-overlay-panel" id="obMissionAccountCapitalRuleRehearsalOverlayPanel" data-ob-giant-pack-015="true">
        <div class="ob-capital-rule-rehearsal-overlay-head">
          <div>
            <div class="ob-label">OB Giant Pack 015 · Mission Account Capital Rules</div>
            <div class="ob-capital-rule-rehearsal-overlay-title">Capital Rule Rehearsal Overlay</div>
            <div class="ob-capital-rule-rehearsal-overlay-subtitle">
              ${safeText(overlayState.status, "booting")} · ${safeText(state.status, "capital_rehearsal_overlay_ready")} · rehearsal-only, no real capital movement.
            </div>
          </div>
          <div class="ob-capital-rule-rehearsal-overlay-chip-row">
            <span class="ob-capital-rule-rehearsal-overlay-chip green">Mission account fit</span>
            <span class="ob-capital-rule-rehearsal-overlay-chip gold">Protected floors</span>
            <span class="ob-capital-rule-rehearsal-overlay-chip red">No capital movement</span>
            <span class="ob-capital-rule-rehearsal-overlay-chip red">No broker/bank</span>
          </div>
        </div>

        <div class="ob-capital-rule-rehearsal-overlay-stat-grid">
          ${card("Accounts", String(profiles.length))}
          ${card("Rules", String(checks.length))}
          ${card("Scenarios", String(scenarios.length))}
          ${card("Override", overrideContract.enabled_now ? "on" : "placeholder")}
          ${card("Movement", "disabled")}
        </div>

        <div class="ob-capital-rule-rehearsal-overlay-grid">
          <div>
            <div class="ob-capital-rule-rehearsal-overlay-card">
              <span>Purpose</span>
              <strong>Rehearse capital rules before real Manual Live so mission accounts cannot be treated like casual trade capital.</strong>
              <div class="ob-capital-rule-rehearsal-overlay-callout">
                <strong>Checks:</strong><br>
                Mission account fit, protected floor, deployment limits, ATM reserve, apartment reserve, trust review, and Tower block reasons.
              </div>
              <div class="ob-capital-rule-rehearsal-overlay-boundary">
                <strong>Boundary:</strong><br>
                No real capital movement. No bank integration. No broker API. No order submit. No database write. No Vault upload.
              </div>
            </div>

            <div class="ob-capital-rule-rehearsal-overlay-card" style="margin-top: 11px;">
              <span>Capital block reason contract</span>
              <strong>${safeText(blockContract.blocked_reason_id, "block reason contract")}</strong>
              <div class="ob-capital-rule-rehearsal-overlay-callout">
                Required fields: ${(blockContract.required_fields || []).join(" · ")}
              </div>
            </div>

            <div class="ob-capital-rule-rehearsal-overlay-card" style="margin-top: 11px;">
              <span>Owner override placeholder</span>
              <strong>${safeText(overrideContract.override_id, "override placeholder")}</strong>
              <div class="ob-capital-rule-rehearsal-overlay-callout">
                Enabled now: ${overrideContract.enabled_now ? "yes" : "no"} · Future requirements: ${(overrideContract.future_requirements || []).join(" · ")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-capital-rule-rehearsal-overlay-section">
              <div class="ob-capital-rule-rehearsal-overlay-section-title">Mission account capital profiles</div>
              <div class="ob-capital-rule-rehearsal-overlay-list">${profiles.map(profileRow).join("")}</div>
            </div>

            <div class="ob-capital-rule-rehearsal-overlay-section">
              <div class="ob-capital-rule-rehearsal-overlay-section-title">Capital rule checks</div>
              <div class="ob-capital-rule-rehearsal-overlay-list">${checks.map((item, index) => row(item, index, "R")).join("")}</div>
            </div>

            <div class="ob-capital-rule-rehearsal-overlay-section">
              <div class="ob-capital-rule-rehearsal-overlay-section-title">Rehearsal capital scenarios</div>
              <div class="ob-capital-rule-rehearsal-overlay-list">${scenarios.map((item, index) => row(item, index, "S")).join("")}</div>
            </div>

            <div class="ob-capital-rule-rehearsal-overlay-section">
              <div class="ob-capital-rule-rehearsal-overlay-section-title">Blocked actions</div>
              <div class="ob-capital-rule-rehearsal-overlay-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-capital-rule-rehearsal-overlay-callout">
          <strong>Next handoff:</strong><br>
          GP016 can prepare Tower step-up enforcement wiring using these capital block reasons and override placeholders.
        </div>

        <div class="ob-capital-rule-rehearsal-overlay-boundary">
          <strong>Still locked:</strong><br>
          Rehearsal-only. No real capital movement. No bank integration. No broker API. No order submit. No auto execution. No database write. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obMissionAccountCapitalRuleRehearsalOverlayPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const ownerInputPanel = document.getElementById("obOwnerInputPersistencePrepPanel");
    const commandBoardPanel = document.getElementById("obReviewCenterRehearsalCommandBoardPanel");
    const contractsPanel = document.getElementById("obRehearsalRecordContractsPanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (ownerInputPanel && ownerInputPanel.parentNode) ownerInputPanel.insertAdjacentElement("afterend", panel);
    else if (commandBoardPanel && commandBoardPanel.parentNode) commandBoardPanel.insertAdjacentElement("afterend", panel);
    else if (contractsPanel && contractsPanel.parentNode) contractsPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = overlayState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-015-capital-rule-rehearsal-overlay", "ready");
    document.body.setAttribute("data-ob-capital-rehearsal-overlay-only", "true");
    document.body.setAttribute("data-ob-no-real-capital-movement", "true");
    document.body.setAttribute("data-ob-no-bank-integration", "true");
    document.body.setAttribute("data-ob-owner-override-placeholder-only", "true");
    document.body.setAttribute("data-ob-tower-block-reason-required", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-broker-read", "true");
    document.body.setAttribute("data-ob-no-order-submit", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-no-direct-vault-upload", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_015_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_STATE = {
      version: VERSION,
      status: overlayState.status,
      fallbackActive: overlayState.fallbackActive,
      accountProfileCount: payload.mission_account_capital_profiles.length,
      capitalRuleCount: payload.capital_rule_checks.length,
      scenarioCount: payload.rehearsal_capital_scenarios.length,
      capitalRehearsalOverlayOnly: true,
      noRealCapitalMovement: true,
      noBankIntegration: true,
      ownerOverridePlaceholderOnly: true,
      towerBlockReasonRequired: true,
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
      fetchOverlay();
    }, 5100);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MISSION_ACCOUNT_CAPITAL_RULE_REHEARSAL_OVERLAY_GP015_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return overlayState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchOverlay,
    renderPanel,
    setFlags
  };
})();
