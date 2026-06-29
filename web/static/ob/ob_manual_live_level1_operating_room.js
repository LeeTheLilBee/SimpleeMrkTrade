// OB_GIANT_PACK_002_MANUAL_LIVE_LEVEL_1_OPERATING_ROOM_JS

(function () {
  const VERSION = "OB_GIANT_PACK_002_MANUAL_LIVE_LEVEL_1_OPERATING_ROOM";
  const ENDPOINT = "/ob/manual-live-level-1.json";

  // SMOKE MARKERS
  // Manual Live Level 1 Operating Room
  // candidate command card
  // mission account fit
  // Tower permission state
  // strategy reason
  // risk summary
  // contract order details
  // entry zone
  // stop target
  // do not enter above
  // Approve Reject Watch
  // broker checklist
  // fill confirmation
  // order not placed state
  // exit alert
  // close confirmation
  // Manual Live owner-only
  // beta user locked
  // Hybrid locked
  // Automated locked
  // no broker API
  // no auto execution
  // Live Auto Locked

  let manualState = {
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
      source: "ob_giant_pack_002_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        mode_permission_controller: "/tower/tower-mode-permission-controller-index-v461.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      mode_state: {
        current_mode: "manual_live_owner_level_1_preview",
        owner_only: true,
        beta_user_locked: true,
        hybrid_locked: true,
        automated_locked: true,
        broker_api_enabled: false,
        auto_execution_enabled: false,
        live_auto_locked: true
      },
      active_command_card: {
        command_id: "ML1-CMD-001",
        symbol: "MU",
        instrument: "OPTION_PREMIUM / stock fallback label only",
        strategy: "options-first candidate review",
        status: "owner_review_required",
        mission_account_fit: "Personal / ATM may review; Trust and Apartment require stricter policy check.",
        tower_permission_state: "needs_owner_review_and_tower_clearance",
        strategy_reason: "Candidate passes review-interest threshold but remains manual-only until owner confirms checklist.",
        risk_summary: "Position size, spread, liquidity, same-sector exposure, account floor, and deployment locks must be checked before action.",
        contract_order_details: {
          action: "review_only",
          order_type: "limit_order_recommended_for_manual_broker_entry",
          quantity: "owner enters manually at broker after checklist",
          expiration: "example-only",
          strike: "example-only",
          option_type: "call/put review only",
          broker_api: "disabled"
        },
        trade_levels: {
          entry_zone: "manual review only",
          do_not_enter_above: "owner-defined before broker action",
          stop: "owner-defined before broker action",
          target: "owner-defined before broker action"
        },
        allowed_owner_actions: ["approve_for_manual_broker_checklist", "reject", "watch"],
        blocked_actions: ["submit_order_from_ob", "auto_execute", "hybrid_submit", "broker_api_order"],
        receipt_preview: "Manual Live decision receipt will be created in Review Center later."
      },
      workflow_steps: [
        {
          step_id: "ml1_detect",
          label: "OB detects candidate",
          owner_action: "Open Trade Center",
          tower_state: "read-only candidate",
          status: "ready"
        },
        {
          step_id: "ml1_permission",
          label: "Tower checks permission",
          owner_action: "Review account/mode safety chips",
          tower_state: "Manual Live owner-only",
          status: "required"
        },
        {
          step_id: "ml1_review",
          label: "Owner reviews command card",
          owner_action: "Approve / Reject / Watch",
          tower_state: "no execution permission created",
          status: "required"
        },
        {
          step_id: "ml1_checklist",
          label: "Broker checklist created",
          owner_action: "Manually check broker account, order type, spread, and buying power",
          tower_state: "broker API disabled",
          status: "checklist_only"
        },
        {
          step_id: "ml1_fill",
          label: "Owner confirms fill",
          owner_action: "Enter fill details after manual brokerage action",
          tower_state: "receipt required",
          status: "placeholder"
        },
        {
          step_id: "ml1_monitor",
          label: "OB monitors position",
          owner_action: "Wait for exit alert / review risk",
          tower_state: "manual close only",
          status: "placeholder"
        },
        {
          step_id: "ml1_exit",
          label: "Exit alert issued",
          owner_action: "Close manually at broker if owner accepts",
          tower_state: "no auto close",
          status: "placeholder"
        },
        {
          step_id: "ml1_close",
          label: "Close confirmation",
          owner_action: "Confirm close details in OB",
          tower_state: "Review Center receipt",
          status: "placeholder"
        }
      ],
      broker_checklist: [
        "Confirm correct mission account before acting.",
        "Confirm Manual Live owner-only clearance is active.",
        "Confirm no global/account/mode/strategy kill switch is active.",
        "Confirm data freshness and source confidence.",
        "Confirm cash/margin/PDT/account restrictions manually at broker.",
        "Confirm options approval manually at broker if reviewing option contract.",
        "Confirm spread/liquidity is acceptable before entering.",
        "Use limit-order discipline; OB does not submit the order.",
        "Confirm fill details after manual broker action.",
        "If order is not placed, record order-not-placed state."
      ],
      states: {
        approve: {
          label: "Approve",
          effect: "Creates manual broker checklist only.",
          real_order: false,
          receipt_required: true
        },
        reject: {
          label: "Reject",
          effect: "Records rejected candidate reason later in Review Center.",
          real_order: false,
          receipt_required: true
        },
        watch: {
          label: "Watch",
          effect: "Keeps candidate under observation without trade action.",
          real_order: false,
          receipt_required: true
        },
        order_not_placed: {
          label: "Order not placed",
          effect: "Records missed/not-placed reason.",
          real_order: false,
          receipt_required: true
        },
        fill_confirmation: {
          label: "Fill confirmation",
          effect: "Owner-entered confirmation only after manual brokerage action.",
          real_order: false,
          receipt_required: true
        },
        exit_alert: {
          label: "Exit alert",
          effect: "Owner receives close-review prompt; OB does not auto-close.",
          real_order: false,
          receipt_required: true
        },
        close_confirmation: {
          label: "Close confirmation",
          effect: "Owner confirms close details after manual broker close.",
          real_order: false,
          receipt_required: true
        }
      },
      beta_user_locked_state: {
        label: "Manual Live locked",
        message: "Standard beta users remain Survey/Paper only.",
        allowed_modes: ["survey", "paper"],
        hidden_features: ["manual_live", "mission_accounts", "capital_deployment", "broker_checklist"]
      },
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_broker_api: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        live_auto_locked: true,
        tower_controls_permission: true,
        ob_creates_no_order: true
      }
    };
  }

  function normalizePayload(raw) {
    const fallback = buildFallbackPayload();
    const safe = raw && typeof raw === "object" ? raw : {};

    return {
      version: safe.version || VERSION,
      source: safe.source || fallback.source,
      tower_sources: { ...(fallback.tower_sources || {}), ...(safe.tower_sources || {}) },
      mode_state: { ...(fallback.mode_state || {}), ...(safe.mode_state || {}) },
      active_command_card: { ...(fallback.active_command_card || {}), ...(safe.active_command_card || {}) },
      workflow_steps: Array.isArray(safe.workflow_steps) ? safe.workflow_steps : fallback.workflow_steps,
      broker_checklist: Array.isArray(safe.broker_checklist) ? safe.broker_checklist : fallback.broker_checklist,
      states: { ...(fallback.states || {}), ...(safe.states || {}) },
      beta_user_locked_state: { ...(fallback.beta_user_locked_state || {}), ...(safe.beta_user_locked_state || {}) },
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        no_public_signup: true,
        no_public_proof: true,
        no_broker_api: true,
        no_auto_execution: true,
        no_hybrid_submit: true,
        no_automated_live: true,
        live_auto_locked: true,
        tower_controls_permission: true,
        ob_creates_no_order: true
      }
    };
  }

  function expose(payload) {
    const normalized = normalizePayload(payload);

    window.OB_MANUAL_LIVE_LEVEL_1_GP002 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_level_1_gp002: normalized,
      manual_live_owner_only: normalized.boundaries.manual_live_owner_only,
      broker_api_enabled: false,
      auto_execution_enabled: false,
      hybrid_locked: true,
      automated_locked: true
    };

    window.dispatchEvent(new CustomEvent("obManualLiveLevel1Updated", { detail: normalized }));
    return normalized;
  }

  async function fetchManualLiveLevel1() {
    manualState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      manualState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        manualState.status = "ready";
        manualState.source = normalized.source || "server";
        manualState.payload = normalized;
        manualState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        manualState.status = "guarded_fallback";
        manualState.source = "guarded_fallback";
        manualState.payload = fallback;
        manualState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      manualState.status = "error_fallback";
      manualState.source = "error_fallback";
      manualState.payload = fallback;
      manualState.fallbackActive = true;
      manualState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return manualState;
  }

  function statusClass(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("locked") || text.includes("blocked") || text.includes("required") || text.includes("disabled")) return "red";
    if (text.includes("owner") || text.includes("manual") || text.includes("checklist") || text.includes("review")) return "gold";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-l1-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function stepRow(item, index) {
    return `
      <div class="ob-manual-live-l1-row">
        <div class="ob-manual-live-l1-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Step")}</strong>
          <span>${safeText(item.step_id, "step")}</span>
        </div>
        <span>${safeText(item.owner_action, "Owner action required.")}<br>${safeText(item.tower_state, "")}</span>
        <div class="ob-manual-live-l1-status ${statusClass(item.status)}">${safeText(item.status, "review")}</div>
      </div>
    `;
  }

  function checklistRow(item, index) {
    return `
      <div class="ob-manual-live-l1-row">
        <div class="ob-manual-live-l1-dot">✓</div>
        <div>
          <strong>Checklist ${index + 1}</strong>
          <span>before broker action</span>
        </div>
        <span>${safeText(item, "Checklist item.")}</span>
        <div class="ob-manual-live-l1-status gold">required</div>
      </div>
    `;
  }

  function stateRow(key, item, index) {
    return `
      <div class="ob-manual-live-l1-row">
        <div class="ob-manual-live-l1-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, key)}</strong>
          <span>${key}</span>
        </div>
        <span>${safeText(item.effect, "State effect.")}</span>
        <div class="ob-manual-live-l1-status ${item.real_order ? "red" : "green"}">${item.real_order ? "real order" : "no order"}</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = manualState.payload || buildFallbackPayload();
    const mode = payload.mode_state || {};
    const cardData = payload.active_command_card || {};
    const levels = cardData.trade_levels || {};
    const order = cardData.contract_order_details || {};
    const steps = Array.isArray(payload.workflow_steps) ? payload.workflow_steps : [];
    const checklist = Array.isArray(payload.broker_checklist) ? payload.broker_checklist : [];
    const states = payload.states || {};

    return `
      <div class="ob-manual-live-l1-panel" id="obManualLiveLevel1Panel" data-ob-giant-pack-002="true">
        <div class="ob-manual-live-l1-head">
          <div>
            <div class="ob-label">OB Giant Pack 002 · Manual Live Level 1</div>
            <div class="ob-manual-live-l1-title">Trade Center Operating Room</div>
            <div class="ob-manual-live-l1-subtitle">
              ${safeText(mode.current_mode, "manual_live_owner_level_1_preview")} · ${safeText(manualState.status, "booting")} · Owner reviews, broker action stays manual.
            </div>
          </div>
          <div class="ob-manual-live-l1-chip-row">
            <span class="ob-manual-live-l1-chip gold">Manual Live owner-only</span>
            <span class="ob-manual-live-l1-chip red">Beta locked</span>
            <span class="ob-manual-live-l1-chip red">No broker API</span>
            <span class="ob-manual-live-l1-chip red">No auto execution</span>
          </div>
        </div>

        <div class="ob-manual-live-l1-stat-grid">
          ${card("Symbol", safeText(cardData.symbol, "—"))}
          ${card("Status", safeText(cardData.status, "review"))}
          ${card("Tower", safeText(cardData.tower_permission_state, "required"))}
          ${card("Hybrid", mode.hybrid_locked ? "locked" : "open")}
          ${card("Auto", mode.automated_locked ? "locked" : "open")}
        </div>

        <div class="ob-manual-live-l1-grid">
          <div>
            <div class="ob-manual-live-l1-card">
              <span>Candidate command card</span>
              <strong>${safeText(cardData.symbol, "Symbol")} · ${safeText(cardData.strategy, "strategy")}</strong>
              <div class="ob-manual-live-l1-callout">
                <strong>Mission account fit</strong><br>
                ${safeText(cardData.mission_account_fit, "Mission fit pending.")}
              </div>
              <div class="ob-manual-live-l1-callout">
                <strong>Strategy reason</strong><br>
                ${safeText(cardData.strategy_reason, "Strategy reason pending.")}
              </div>
              <div class="ob-manual-live-l1-boundary">
                <strong>Risk summary</strong><br>
                ${safeText(cardData.risk_summary, "Risk summary pending.")}
              </div>
              <div class="ob-manual-live-l1-action-row">
                <span class="ob-manual-live-l1-action gold">Approve</span>
                <span class="ob-manual-live-l1-action red">Reject</span>
                <span class="ob-manual-live-l1-action green">Watch</span>
                <span class="ob-manual-live-l1-action disabled red">Submit disabled</span>
              </div>
            </div>

            <div class="ob-manual-live-l1-card" style="margin-top: 11px;">
              <span>Contract / order details</span>
              <strong>${safeText(order.order_type, "limit order checklist only")}</strong>
              <div class="ob-manual-live-l1-callout">
                <strong>Entry zone:</strong> ${safeText(levels.entry_zone, "manual review only")}<br>
                <strong>Do not enter above:</strong> ${safeText(levels.do_not_enter_above, "owner-defined")}<br>
                <strong>Stop:</strong> ${safeText(levels.stop, "owner-defined")}<br>
                <strong>Target:</strong> ${safeText(levels.target, "owner-defined")}
              </div>
              <div class="ob-manual-live-l1-boundary">
                <strong>Order boundary:</strong><br>
                OB does not submit orders. Owner places manually at broker only after checklist.
              </div>
            </div>

            <div class="ob-manual-live-l1-card" style="margin-top: 11px;">
              <span>Beta user state</span>
              <strong>${safeText(payload.beta_user_locked_state && payload.beta_user_locked_state.label, "Manual Live locked")}</strong>
              <div class="ob-manual-live-l1-boundary">
                ${safeText(payload.beta_user_locked_state && payload.beta_user_locked_state.message, "Standard beta users remain Survey/Paper only.")}
              </div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-l1-section">
              <div class="ob-manual-live-l1-section-title">Manual Live Level 1 workflow</div>
              <div class="ob-manual-live-l1-list">${steps.map(stepRow).join("")}</div>
            </div>

            <div class="ob-manual-live-l1-section">
              <div class="ob-manual-live-l1-section-title">Broker checklist</div>
              <div class="ob-manual-live-l1-list">${checklist.map(checklistRow).join("")}</div>
            </div>

            <div class="ob-manual-live-l1-section">
              <div class="ob-manual-live-l1-section-title">Action states</div>
              <div class="ob-manual-live-l1-list">${Object.keys(states).map((key, index) => stateRow(key, states[key], index)).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-l1-callout">
          <strong>Source:</strong><br>
          Manual Live Level 1 uses the OB account experience and Tower capital safety contracts as the control layer.
        </div>

        <div class="ob-manual-live-l1-boundary">
          <strong>Boundary:</strong><br>
          This is an operating-room framework only. No broker API. No auto execution. No hybrid submit. No automated live. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveLevel1Panel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const accountPanel = document.getElementById("obAccountExperiencePanel");
    const tradeCenterAnchor = document.querySelector("[data-ob-trade-center]");
    const dashboardFocus = document.querySelector("[data-ob-dashboard-focus]");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (accountPanel && accountPanel.parentNode) accountPanel.insertAdjacentElement("afterend", panel);
    else if (tradeCenterAnchor && tradeCenterAnchor.parentNode) tradeCenterAnchor.insertAdjacentElement("afterend", panel);
    else if (dashboardFocus && dashboardFocus.parentNode) dashboardFocus.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = manualState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-002-manual-live-level-1", "ready");
    document.body.setAttribute("data-ob-manual-live-owner-only", "true");
    document.body.setAttribute("data-ob-beta-manual-live-locked", "true");
    document.body.setAttribute("data-ob-broker-api-enabled", "false");
    document.body.setAttribute("data-ob-auto-execution-enabled", "false");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");

    window.OB_GIANT_PACK_002_MANUAL_LIVE_L1_STATE = {
      version: VERSION,
      status: manualState.status,
      fallbackActive: manualState.fallbackActive,
      currentMode: payload.mode_state.current_mode,
      manualLiveOwnerOnly: true,
      betaUserLocked: true,
      brokerApiEnabled: false,
      autoExecutionEnabled: false,
      hybridLocked: true,
      automatedLocked: true,
      liveAutoLocked: true,
      obCreatesNoOrder: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchManualLiveLevel1();
    }, 3020);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_LEVEL_1_GP002_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return manualState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchManualLiveLevel1,
    renderPanel,
    setFlags
  };
})();
