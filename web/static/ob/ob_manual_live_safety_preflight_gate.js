// OB_GIANT_PACK_005_MANUAL_LIVE_SAFETY_PREFLIGHT_GATE_JS

(function () {
  const VERSION = "OB_GIANT_PACK_005_MANUAL_LIVE_SAFETY_PREFLIGHT_GATE";
  const ENDPOINT = "/ob/manual-live-safety-preflight-gate.json";

  // SMOKE MARKERS
  // Manual Live Safety Preflight Gate
  // safety preflight before broker checklist
  // account policy check
  // mode permission check
  // kill switch check
  // data freshness check
  // source confidence check
  // broker restriction manual check
  // options approval manual check
  // liquidity spread check
  // duplicate order protection
  // same symbol exposure check
  // same sector exposure check
  // protected floor check
  // deployment capital lock check
  // PDT margin cash account warning
  // Tower clearance required
  // owner step-up required
  // approve reject watch gate
  // checklist only no order
  // no broker API
  // no auto execution
  // Manual Live owner-only
  // beta Survey Paper only
  // Hybrid locked
  // Automated locked
  // Live Auto Locked

  let preflightState = {
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
      source: "ob_giant_pack_005_safe_fallback",
      tower_sources: {
        account_experience: "/ob/account-experience.json",
        manual_live_level_1: "/ob/manual-live-level-1.json",
        receipts_review_foundation: "/ob/receipts-review-foundation.json",
        private_beta_tower_lock_polish: "/ob/private-beta-tower-lock-polish.json",
        mission_account_policy_registry: "/tower/tower-mission-account-policy-registry-index-v451.json",
        mode_permission_controller: "/tower/tower-mode-permission-controller-index-v461.json",
        kill_switch_board: "/tower/tower-kill-switch-board-index-v471.json",
        safety_notification_snapshot: "/tower/tower-safety-notification-snapshot-index-v481.json",
        capital_safety_enforcement_readiness: "/tower/tower-capital-safety-command-enforcement-readiness-v500.json"
      },
      gate_state: {
        gate_id: "ob_manual_live_safety_preflight_gate",
        label: "Manual Live Safety Preflight Gate",
        current_state: "checklist_only",
        owner_only: true,
        beta_locked: true,
        blocks_broker_submit: true,
        creates_order: false,
        requires_tower_clearance: true,
        requires_owner_step_up: true
      },
      preflight_checks: [
        {
          check_id: "account_policy_check",
          label: "Account policy check",
          category: "account",
          required_state: "active policy",
          current_state: "required",
          gate_effect: "No broker checklist if selected account has no active policy.",
          receipt_event: "preflight_account_policy_checked"
        },
        {
          check_id: "mode_permission_check",
          label: "Mode permission check",
          category: "mode",
          required_state: "Manual Live Level 1 owner-only",
          current_state: "required",
          gate_effect: "Beta users stay Survey/Paper; owner-only Manual Live only.",
          receipt_event: "preflight_mode_permission_checked"
        },
        {
          check_id: "kill_switch_check",
          label: "Kill switch check",
          category: "Tower safety",
          required_state: "no global/account/mode/strategy/symbol halt",
          current_state: "required",
          gate_effect: "Any active Tower halt blocks manual broker checklist.",
          receipt_event: "preflight_kill_switch_checked"
        },
        {
          check_id: "data_freshness_check",
          label: "Data freshness check",
          category: "data",
          required_state: "fresh or manually reviewed",
          current_state: "required",
          gate_effect: "Stale or unknown data blocks action until owner refreshes/reviews.",
          receipt_event: "preflight_data_freshness_checked"
        },
        {
          check_id: "source_confidence_check",
          label: "Source confidence check",
          category: "data",
          required_state: "system generated + owner reviewed",
          current_state: "required",
          gate_effect: "Unverified or stale signal confidence blocks broker checklist.",
          receipt_event: "preflight_source_confidence_checked"
        },
        {
          check_id: "broker_restriction_manual_check",
          label: "Broker restriction manual check",
          category: "broker manual",
          required_state: "owner confirms broker/account status manually",
          current_state: "manual_required",
          gate_effect: "OB cannot know final broker restrictions without owner manual confirmation.",
          receipt_event: "preflight_broker_restriction_checked"
        },
        {
          check_id: "options_approval_manual_check",
          label: "Options approval manual check",
          category: "broker manual",
          required_state: "owner confirms options permission manually if option contract",
          current_state: "manual_required",
          gate_effect: "Options candidate cannot proceed to checklist without manual broker confirmation.",
          receipt_event: "preflight_options_approval_checked"
        },
        {
          check_id: "liquidity_spread_check",
          label: "Liquidity / spread check",
          category: "market safety",
          required_state: "spread/liquidity acceptable",
          current_state: "required",
          gate_effect: "Wide spread or low liquidity blocks manual placement checklist.",
          receipt_event: "preflight_liquidity_spread_checked"
        },
        {
          check_id: "duplicate_order_protection",
          label: "Duplicate order protection",
          category: "order safety",
          required_state: "no duplicate open/pending intent",
          current_state: "required",
          gate_effect: "Blocks repeat trade intent for same candidate/account.",
          receipt_event: "preflight_duplicate_order_checked"
        },
        {
          check_id: "same_symbol_exposure_check",
          label: "Same symbol exposure check",
          category: "exposure",
          required_state: "within symbol exposure cap",
          current_state: "required",
          gate_effect: "Blocks stacking same symbol beyond account policy.",
          receipt_event: "preflight_symbol_exposure_checked"
        },
        {
          check_id: "same_sector_exposure_check",
          label: "Same sector exposure check",
          category: "exposure",
          required_state: "within sector/theme exposure cap",
          current_state: "required",
          gate_effect: "Blocks sector crowding before manual checklist.",
          receipt_event: "preflight_sector_exposure_checked"
        },
        {
          check_id: "protected_floor_check",
          label: "Protected floor check",
          category: "capital safety",
          required_state: "account remains above protected floor",
          current_state: "required",
          gate_effect: "Trust/apartment/deployment accounts cannot risk protected floor.",
          receipt_event: "preflight_protected_floor_checked"
        },
        {
          check_id: "deployment_capital_lock_check",
          label: "Deployment capital lock check",
          category: "capital safety",
          required_state: "deployment capital not used for trade risk",
          current_state: "required",
          gate_effect: "ATM/apartment deployment capital is locked before trade review.",
          receipt_event: "preflight_deployment_capital_lock_checked"
        },
        {
          check_id: "pdt_margin_cash_account_warning",
          label: "PDT / margin / cash account warning",
          category: "broker manual",
          required_state: "owner reviews broker account rule implications",
          current_state: "manual_warning",
          gate_effect: "Warning must be acknowledged; OB does not determine broker compliance.",
          receipt_event: "preflight_pdt_margin_cash_warning_acknowledged"
        },
        {
          check_id: "tower_clearance_required",
          label: "Tower clearance required",
          category: "Tower safety",
          required_state: "Tower cleared or owner step-up requested",
          current_state: "required",
          gate_effect: "No owner action can proceed without Tower clearance state.",
          receipt_event: "preflight_tower_clearance_checked"
        }
      ],
      action_gate: {
        approve: {
          label: "Approve",
          allowed_result: "manual broker checklist only",
          blocked_result: "no OB order submit",
          requires_all_checks: true,
          receipt_event: "preflight_owner_approved_checklist"
        },
        reject: {
          label: "Reject",
          allowed_result: "reject receipt only",
          blocked_result: "no trade",
          requires_all_checks: false,
          receipt_event: "preflight_owner_rejected"
        },
        watch: {
          label: "Watch",
          allowed_result: "watch receipt only",
          blocked_result: "no trade",
          requires_all_checks: false,
          receipt_event: "preflight_owner_watched"
        }
      },
      blocked_actions: [
        "submit_order_from_ob",
        "broker_api_order",
        "auto_execute",
        "hybrid_submit",
        "automated_live",
        "skip_tower_clearance",
        "skip_broker_manual_confirmation",
        "use_deployment_capital_without_gate"
      ],
      receipt_output: {
        receipt_type: "manual_live_safety_preflight_receipt",
        destination: "Review Center / Manual Live preflight",
        vault_ready: true,
        no_direct_vault_upload: true,
        sensitivity: "owner_only"
      },
      boundaries: {
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        safety_preflight_required: true,
        checklist_only_no_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
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
      tower_sources: { ...(fallback.tower_sources || {}), ...(safe.tower_sources || {}) },
      gate_state: { ...(fallback.gate_state || {}), ...(safe.gate_state || {}) },
      preflight_checks: Array.isArray(safe.preflight_checks) ? safe.preflight_checks : fallback.preflight_checks,
      action_gate: { ...(fallback.action_gate || {}), ...(safe.action_gate || {}) },
      blocked_actions: Array.isArray(safe.blocked_actions) ? safe.blocked_actions : fallback.blocked_actions,
      receipt_output: { ...(fallback.receipt_output || {}), ...(safe.receipt_output || {}) },
      boundaries: {
        ...(fallback.boundaries || {}),
        ...(safe.boundaries || {}),
        private_beta_only: true,
        manual_live_owner_only: true,
        beta_survey_paper_only: true,
        safety_preflight_required: true,
        checklist_only_no_order: true,
        no_public_proof: true,
        no_public_receipts: true,
        no_broker_api: true,
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

    window.OB_MANUAL_LIVE_SAFETY_PREFLIGHT_GP005 = normalized;
    window.OB_SERVER_DATA = {
      ...(window.OB_SERVER_DATA || {}),
      manual_live_safety_preflight_gp005: normalized,
      safety_preflight_required: true,
      checklist_only_no_order: true,
      no_broker_api: true,
      no_auto_execution: true,
      hybrid_locked: true,
      automated_locked: true,
      live_auto_locked: true
    };

    window.dispatchEvent(new CustomEvent("obManualLiveSafetyPreflightUpdated", { detail: normalized }));
    return normalized;
  }

  async function fetchPreflight() {
    preflightState.status = "loading";

    try {
      const response = await fetch(ENDPOINT, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
      });

      preflightState.httpStatus = response.status;

      if (response.ok) {
        const normalized = expose(await response.json());
        preflightState.status = "ready";
        preflightState.source = normalized.source || "server";
        preflightState.payload = normalized;
        preflightState.fallbackActive = false;
      } else {
        const fallback = expose(buildFallbackPayload());
        preflightState.status = "guarded_fallback";
        preflightState.source = "guarded_fallback";
        preflightState.payload = fallback;
        preflightState.fallbackActive = true;
      }
    } catch (error) {
      const fallback = expose(buildFallbackPayload());
      preflightState.status = "error_fallback";
      preflightState.source = "error_fallback";
      preflightState.payload = fallback;
      preflightState.fallbackActive = true;
      preflightState.error = error && error.message ? error.message : "Unknown fetch error";
    }

    renderPanel();
    setFlags();
    return preflightState;
  }

  function tone(value) {
    const text = safeText(value, "").toLowerCase();
    if (text.includes("blocked") || text.includes("required") || text.includes("manual") || text.includes("warning")) return "gold";
    if (text.includes("disabled") || text.includes("locked") || text.includes("halt")) return "red";
    return "green";
  }

  function card(label, value) {
    return `<div class="ob-manual-live-preflight-stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function checkRow(item, index) {
    return `
      <div class="ob-manual-live-preflight-row">
        <div class="ob-manual-live-preflight-dot">${index + 1}</div>
        <div>
          <strong>${safeText(item.label, "Preflight check")}</strong>
          <span>${safeText(item.category, "category")}</span>
        </div>
        <span>${safeText(item.required_state, "required")}<br>${safeText(item.gate_effect, "gate effect")}</span>
        <div class="ob-manual-live-preflight-status ${tone(item.current_state)}">${safeText(item.current_state, "required")}</div>
      </div>
    `;
  }

  function actionRow(key, item) {
    return `
      <div class="ob-manual-live-preflight-row">
        <div class="ob-manual-live-preflight-dot">A</div>
        <div>
          <strong>${safeText(item.label, key)}</strong>
          <span>${key}</span>
        </div>
        <span>${safeText(item.allowed_result, "allowed")}<br>Blocked: ${safeText(item.blocked_result, "none")}</span>
        <div class="ob-manual-live-preflight-status ${item.requires_all_checks ? "gold" : "green"}">${item.requires_all_checks ? "all checks" : "receipt only"}</div>
      </div>
    `;
  }

  function blockedRow(item) {
    return `
      <div class="ob-manual-live-preflight-row">
        <div class="ob-manual-live-preflight-dot">×</div>
        <div>
          <strong>${safeText(item, "blocked")}</strong>
          <span>blocked action</span>
        </div>
        <span>This action is not allowed by OB Giant Pack 005.</span>
        <div class="ob-manual-live-preflight-status red">blocked</div>
      </div>
    `;
  }

  function panelHtml() {
    const payload = preflightState.payload || buildFallbackPayload();
    const checks = Array.isArray(payload.preflight_checks) ? payload.preflight_checks : [];
    const actions = payload.action_gate || {};
    const blocked = Array.isArray(payload.blocked_actions) ? payload.blocked_actions : [];
    const gate = payload.gate_state || {};
    const receipt = payload.receipt_output || {};

    return `
      <div class="ob-manual-live-preflight-panel" id="obManualLiveSafetyPreflightPanel" data-ob-giant-pack-005="true">
        <div class="ob-manual-live-preflight-head">
          <div>
            <div class="ob-label">OB Giant Pack 005 · Manual Live Safety Preflight</div>
            <div class="ob-manual-live-preflight-title">Safety Gate Before Broker Checklist</div>
            <div class="ob-manual-live-preflight-subtitle">
              ${safeText(preflightState.status, "booting")} · ${safeText(gate.current_state, "checklist_only")} · OB still creates no order.
            </div>
          </div>
          <div class="ob-manual-live-preflight-chip-row">
            <span class="ob-manual-live-preflight-chip gold">Tower clearance required</span>
            <span class="ob-manual-live-preflight-chip gold">Owner step-up required</span>
            <span class="ob-manual-live-preflight-chip red">No broker API</span>
            <span class="ob-manual-live-preflight-chip red">No auto execution</span>
          </div>
        </div>

        <div class="ob-manual-live-preflight-stat-grid">
          ${card("Preflight checks", String(checks.length))}
          ${card("Gate", safeText(gate.current_state, "checklist"))}
          ${card("Owner-only", gate.owner_only ? "yes" : "no")}
          ${card("Order submit", "blocked")}
          ${card("Receipt", safeText(receipt.receipt_type, "preflight"))}
        </div>

        <div class="ob-manual-live-preflight-grid">
          <div>
            <div class="ob-manual-live-preflight-card">
              <span>Gate purpose</span>
              <strong>Nothing moves from command card to broker checklist without safety review.</strong>
              <div class="ob-manual-live-preflight-callout">
                <strong>Allowed:</strong><br>
                Owner can approve a manual broker checklist, reject, or watch. Approval creates checklist/receipt only.
              </div>
              <div class="ob-manual-live-preflight-boundary">
                <strong>Blocked:</strong><br>
                OB cannot submit orders, call broker API, auto-execute, hybrid-submit, or use deployment capital without Tower gate.
              </div>
            </div>

            <div class="ob-manual-live-preflight-card" style="margin-top: 11px;">
              <span>Action gate</span>
              <div class="ob-manual-live-preflight-list">
                ${Object.keys(actions).map((key) => actionRow(key, actions[key])).join("")}
              </div>
            </div>

            <div class="ob-manual-live-preflight-card" style="margin-top: 11px;">
              <span>Blocked actions</span>
              <div class="ob-manual-live-preflight-list">${blocked.map(blockedRow).join("")}</div>
            </div>
          </div>

          <div>
            <div class="ob-manual-live-preflight-section">
              <div class="ob-manual-live-preflight-section-title">Required preflight checks</div>
              <div class="ob-manual-live-preflight-list">${checks.map(checkRow).join("")}</div>
            </div>
          </div>
        </div>

        <div class="ob-manual-live-preflight-callout">
          <strong>Receipt output:</strong><br>
          ${safeText(receipt.receipt_type, "preflight receipt")} · ${safeText(receipt.destination, "Review Center")} · Vault-ready placeholder only.
        </div>

        <div class="ob-manual-live-preflight-boundary">
          <strong>Boundary:</strong><br>
          Manual Live owner-only. Beta Survey/Paper only. No broker API. No auto execution. Hybrid locked. Automated locked. Live Auto Locked.
        </div>
      </div>
    `;
  }

  function renderPanel() {
    const existing = document.getElementById("obManualLiveSafetyPreflightPanel");
    if (existing) existing.remove();

    const layer = document.querySelector(".ob-layer");
    if (!layer) return;

    const polishPanel = document.getElementById("obPrivateBetaTowerLockPolishPanel");
    const receiptsPanel = document.getElementById("obReceiptsReviewFoundationPanel");
    const manualPanel = document.getElementById("obManualLiveLevel1Panel");
    const accountPanel = document.getElementById("obAccountExperiencePanel");

    const wrapper = document.createElement("div");
    wrapper.innerHTML = panelHtml();
    const panel = wrapper.firstElementChild;

    if (polishPanel && polishPanel.parentNode) polishPanel.insertAdjacentElement("afterend", panel);
    else if (receiptsPanel && receiptsPanel.parentNode) receiptsPanel.insertAdjacentElement("afterend", panel);
    else if (manualPanel && manualPanel.parentNode) manualPanel.insertAdjacentElement("afterend", panel);
    else if (accountPanel && accountPanel.parentNode) accountPanel.insertAdjacentElement("afterend", panel);
    else layer.prepend(panel);
  }

  function setFlags() {
    const payload = preflightState.payload || buildFallbackPayload();

    document.body.setAttribute("data-ob-giant-pack-005-manual-live-safety-preflight", "ready");
    document.body.setAttribute("data-ob-safety-preflight-required", "true");
    document.body.setAttribute("data-ob-checklist-only-no-order", "true");
    document.body.setAttribute("data-ob-no-broker-api", "true");
    document.body.setAttribute("data-ob-no-auto-execution", "true");
    document.body.setAttribute("data-ob-hybrid-locked", "true");
    document.body.setAttribute("data-ob-automated-locked", "true");
    document.body.setAttribute("data-ob-live-auto-locked", "true");

    window.OB_GIANT_PACK_005_MANUAL_LIVE_PREFLIGHT_STATE = {
      version: VERSION,
      status: preflightState.status,
      fallbackActive: preflightState.fallbackActive,
      preflightCheckCount: payload.preflight_checks.length,
      checklistOnlyNoOrder: true,
      noBrokerApi: true,
      noAutoExecution: true,
      hybridLocked: true,
      automatedLocked: true,
      liveAutoLocked: true
    };
  }

  function boot() {
    expose(buildFallbackPayload());
    setTimeout(function () {
      renderPanel();
      setFlags();
      fetchPreflight();
    }, 3500);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_MANUAL_LIVE_SAFETY_PREFLIGHT_GP005_API = {
    version: VERSION,
    endpoint: ENDPOINT,
    getState: function () { return preflightState; },
    buildFallbackPayload,
    normalizePayload,
    expose,
    fetchPreflight,
    renderPanel,
    setFlags
  };
})();
